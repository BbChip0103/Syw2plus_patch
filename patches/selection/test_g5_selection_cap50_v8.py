import hashlib
import importlib.util
import sys
from pathlib import Path

import capstone
import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v8.py")
spec = importlib.util.spec_from_file_location(MODULE.stem, MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    return SOURCE.read_bytes()


def _offset(pe: pefile.PE, va: int) -> int:
    return mod._va_to_file_offset(pe, va)


def test_build_is_v7_plus_exactly_one_changed_byte(original: bytes) -> None:
    """lap746 runtime evidence: v7's load-wrapper zero-fill only cleared
    entries[count:20], leaving entries[20:50] stale after a load performed
    with a >20 selection still live. The fix widens a single immediate
    operand (STOCK_CAPACITY=20 -> TARGET_CAPACITY=50) inside the existing
    load-wrapper cave; nothing else about v7 may change."""
    candidate, report = mod.build_candidate(original)
    v7_candidate, v7_report = mod.v7.build_candidate(original)
    assert len(candidate) == len(original)
    assert report["v7_candidate_sha256"] == hashlib.sha256(v7_candidate).hexdigest()
    assert report["v7_candidate_sha256"] == v7_report["candidate_sha256"]
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] != report["v7_candidate_sha256"]

    diffs = [i for i in range(len(candidate)) if candidate[i] != v7_candidate[i]]
    assert len(diffs) == 1, f"expected exactly one changed byte, got {diffs}"
    changed_offset = diffs[0]
    assert v7_candidate[changed_offset] == mod.STOCK_CAPACITY
    assert candidate[changed_offset] == mod.TARGET_CAPACITY

    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        load_wrapper_start = rsrc.PointerToRawData + mod.LOAD_WRAPPER_OFFSET
        load_wrapper_end = rsrc.PointerToRawData + mod.RSRC_CODE_END_OFFSET
    finally:
        pe.close()
    assert load_wrapper_start <= changed_offset < load_wrapper_end


def test_load_wrapper_old_bytes_are_the_pinned_v7_encoding(original: bytes) -> None:
    v7_candidate, _v7_report = mod.v7.build_candidate(original)
    pe = pefile.PE(data=v7_candidate, fast_load=True)
    try:
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        rsrc_va = mod.IMAGE_BASE + int(rsrc.VirtualAddress)
        load_va = rsrc_va + mod.LOAD_WRAPPER_OFFSET
        raw = rsrc.PointerToRawData
    finally:
        pe.close()
    old_code = mod._assemble(mod.v7._LOAD_WRAPPER_ASM, load_va)
    actual = v7_candidate[raw + mod.LOAD_WRAPPER_OFFSET: raw + mod.LOAD_WRAPPER_OFFSET + len(old_code)]
    assert actual == old_code


def test_load_wrapper_zero_fill_now_spans_the_full_fifty_slots(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        load_off = _offset(pe, int(report["hooks"]["load"]["wrapper_va"], 16))
    finally:
        pe.close()
    load_bytes = candidate[load_off: load_off + report["hooks"]["load"]["bytes"]]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insns = list(md.disasm(load_bytes, int(report["hooks"]["load"]["wrapper_va"], 16)))
    mov_ecx_imms = [
        int(insn.op_str.split(",")[1].strip(), 16)
        for insn in insns
        if insn.mnemonic == "mov" and insn.op_str.startswith("ecx, 0x")
    ]
    assert mod.STOCK_CAPACITY in mov_ecx_imms, "the count-cap compare must still clamp to 20"
    assert mod.TARGET_CAPACITY in mov_ecx_imms, "the zero-fill length must now be 50, not 20"
    assert insns[0].mnemonic == "push" and insns[0].op_str == "ebp"
    assert any(i.mnemonic == "call" and i.op_str == hex(mod.STREAM_LOAD_FN) for i in insns)
    assert insns[-1].mnemonic == "ret"
    assert insns[-2].mnemonic == "pop" and insns[-2].op_str == "ebp"


def test_v8_rejects_if_v7_already_covers_the_full_tail() -> None:
    # Guard against silent bit-rot: if v7's mirror text is ever widened to
    # already cover entries[20:50], this module must fail loudly instead of
    # producing a candidate that is byte-identical to v7.
    assert mod.v7._MIRROR_FROM_LEGACY.strip() != mod._MIRROR_FROM_LEGACY_FULL_TAIL.strip()
