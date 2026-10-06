import hashlib
import importlib.util
import sys
from pathlib import Path

import capstone
import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v4.py")
spec = importlib.util.spec_from_file_location(MODULE.stem, MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"
EXPECTED_CANDIDATE_SHA256 = "0e472792410ddc87eb5eee9809c99761da61d8afa23e73638db0fae5e10f9cbb"


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


def test_cave_fits_within_limit(original: bytes) -> None:
    _candidate, report = mod.build_candidate(original)
    cave_end = int(report["hook"]["cave_end_exclusive"], 16)
    assert cave_end <= mod.CAVE_LIMIT


def test_gate_reproduces_v3_body_modulo_call_site_relocation(original: bytes) -> None:
    """v4 must only change the leading gate; the count-check, 80-byte backup
    buffer, three chunked dispatch calls, restore, and (unrelocated) original
    body bytes must stay the same as v3's. The relocated body differs only in
    the two external ``call`` rel32 fields, since v4's gate is a different
    length so ``body_addr`` (and hence the encoded displacement) differs --
    mask those 4-byte fields out before comparing.
    """
    from patches.selection import g5_selection_cap50_v3 as v3

    v4_candidate, v4_report = mod.build_candidate(original)
    v3_candidate, v3_report = v3.build_candidate(original)

    v4_pe = pefile.PE(data=v4_candidate, fast_load=True)
    v3_pe = pefile.PE(data=v3_candidate, fast_load=True)
    try:
        v4_body_addr = int(v4_report["hook"]["body_addr"], 16)
        v3_body_addr = int(v3_report["hook"]["body_addr"], 16)
        v4_off = mod._va_to_file_offset(v4_pe, v4_body_addr)
        v3_off = v3._va_to_file_offset(v3_pe, v3_body_addr)
        v4_tail = bytearray(v4_candidate[v4_off : v4_off + mod.BODY_LEN])
        v3_tail = bytearray(v3_candidate[v3_off : v3_off + v3.BODY_LEN])
    finally:
        v4_pe.close()
        v3_pe.close()
    for call_site, _target in mod.EXTERNAL_CALLS:
        rel32_off = call_site - mod.HOOK_SITE + 1  # skip the 0xE8 opcode byte
        v4_tail[rel32_off : rel32_off + 4] = b"\x00\x00\x00\x00"
        v3_tail[rel32_off : rel32_off + 4] = b"\x00\x00\x00\x00"
    assert bytes(v4_tail) == bytes(v3_tail), "original body bytes (modulo call relocation) must be unchanged from v3"


def _decode_gate(candidate: bytes, report: dict) -> list[capstone.CsInsn]:
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        gate_off = mod._va_to_file_offset(pe, mod.CAVE_BASE)
        body_addr = int(report["hook"]["body_addr"], 16)
        data = candidate[gate_off : gate_off + (body_addr - mod.CAVE_BASE)]
    finally:
        pe.close()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    return list(md.disasm(data, mod.CAVE_BASE))


def test_gate_immediate_and_range_values_match_known_non_order_set(original: bytes) -> None:
    """Structural regression: every ``cmp eax, imm`` immediately followed by
    a conditional jump in the gate must be one of the pinned lap676
    known-non-order singles/range endpoints -- catches an accidental typo'd
    constant or a dropped/added comparison without needing an x86 emulator.
    """
    candidate, report = mod.build_candidate(original)
    insns = _decode_gate(candidate, report)
    # check_count's first instruction re-reads the live selection count
    # (``movzx eax, word ptr [SELECTION_BASE]``); everything strictly before
    # it is the gate this test is checking.
    check_count_idx = next(
        i for i, insn in enumerate(insns)
        if insn.mnemonic == "movzx" and hex(mod.SELECTION_BASE) in insn.op_str
    )
    gate_insns = insns[:check_count_idx]

    cmp_imms: list[int] = []
    for insn in gate_insns:
        if insn.mnemonic == "cmp" and "," in insn.op_str:
            _reg, imm = insn.op_str.split(",", 1)
            cmp_imms.append(int(imm.strip(), 16))

    expected = sorted(
        set(mod.KNOWN_NON_ORDER_SINGLES) | {v for lo, hi in mod.KNOWN_NON_ORDER_RANGES for v in (lo, hi)}
    )
    assert sorted(cmp_imms) == expected

    mnemonics = [insn.mnemonic for insn in gate_insns if insn.mnemonic in ("je", "jb", "jbe", "jmp")]
    # 3 singles (je), 2 ranges (jb, jbe each), trailing unconditional jmp to check_count
    assert mnemonics == ["je", "je", "je", "jb", "jbe", "jb", "jbe", "jmp"]
