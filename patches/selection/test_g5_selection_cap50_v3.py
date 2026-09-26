import hashlib
import importlib.util
import sys
from pathlib import Path

import capstone
import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v3.py")
spec = importlib.util.spec_from_file_location(MODULE.stem, MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"
EXPECTED_CANDIDATE_SHA256 = "e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977"


@pytest.fixture
def original() -> bytes:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    return SOURCE.read_bytes()


def test_build_is_deterministic_and_matches_pinned_sha(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    assert len(candidate) == len(original)
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] == EXPECTED_CANDIDATE_SHA256


def test_wrapper_reserves_backup_buffer_below_call_frame(original: bytes) -> None:
    """lap680 regression guard: the wrapper's 80-byte backup buffer at
    ``[ebp-0x50, ebp)`` must sit strictly below every later push/call in the
    same chunk-dispatch sequence. Without an explicit ``sub esp, 0x50`` right
    after ``mov ebp, esp``, the subsequent 5-arg push + ``call original_body``
    (args at ``[ebp-0x14 .. ebp-0x4]``, return address at ``[ebp-0x18]``)
    aliases that same buffer, so the final restore copies chunk 2's leftover
    return address and argument words into live selection entries 14-19
    instead of the true backed-up unit handles -- exactly the corruption
    that produced the live page fault at read address 0x02A45AAA (entry 14's
    low word, 0x004E4E1C & 0xFFFF == 19996, fed an unrelated unbounded
    selection-panel accessor at 0x0040FED0).
    """
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        off = mod._va_to_file_offset(pe, mod.CAVE_BASE)
        body_addr = int(report["hook"]["body_addr"], 16)
        data = candidate[off : off + (body_addr - mod.CAVE_BASE)]
    finally:
        pe.close()

    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insns = [insn for insn in md.disasm(data, mod.CAVE_BASE) if insn.address < body_addr]

    mov_ebp_idx = next(
        i for i, insn in enumerate(insns) if insn.mnemonic == "mov" and insn.op_str == "ebp, esp"
    )
    reserve = insns[mov_ebp_idx + 1]
    assert reserve.mnemonic == "sub" and reserve.op_str == "esp, 0x50", (
        f"expected 'sub esp, 0x50' immediately after 'mov ebp, esp', got "
        f"'{reserve.mnemonic} {reserve.op_str}' -- the backup buffer is unreserved again"
    )

    # Every `call original_body` site must be preceded by exactly five
    # `push dword ptr [ebp+N]` argument pushes with N in [0x14, 0x24] --
    # confirm none of their store addresses (esp at push time) land inside
    # [ebp-0x50, ebp).
    call_sites = [i for i, insn in enumerate(insns) if insn.mnemonic == "call" and insn.op_str == hex(body_addr)]
    assert len(call_sites) == 3, f"expected 3 chunk dispatch calls, found {len(call_sites)}"
    for call_idx in call_sites:
        pushes = insns[call_idx - 5 : call_idx]
        assert all(insn.mnemonic == "push" and insn.op_str.startswith("dword ptr [ebp") for insn in pushes)
        # The reservation guarantees esp <= ebp-0x50 before any of these
        # pushes; each push only decreases esp further, so none can land in
        # [ebp-0x50, ebp) as long as the reservation instruction above holds.
