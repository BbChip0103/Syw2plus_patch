import hashlib
import importlib.util
import sys
from pathlib import Path

import capstone
import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v7.py")
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


def test_build_is_v6_plus_two_pinned_call_sites_and_private_cave(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    v6_candidate, v6_report = mod.v6.build_candidate(original)
    assert len(candidate) == len(original)
    assert report["v6_candidate_sha256"] == hashlib.sha256(v6_candidate).hexdigest()
    assert report["v6_candidate_sha256"] == v6_report["candidate_sha256"]
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] != report["v6_candidate_sha256"]


def test_only_the_two_call_sites_and_rsrc_cave_differ_from_v6(original: bytes) -> None:
    """v7 must not touch anything v6 already established -- drag/move/attack/
    group-assign/recall/death-recall-cleanup behavior must be byte-identical;
    only the save/load call sites and the .rsrc section header + its own
    zero-filled raw padding may change."""
    candidate, report = mod.build_candidate(original)
    v6_candidate, _v6_report = mod.v6.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        save_site_off = _offset(pe, mod.SAVE_CALL_VA)
        load_site_off = _offset(pe, mod.LOAD_CALL_VA)
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        section_header_off = rsrc.get_file_offset()
        cave_off = rsrc.PointerToRawData + mod.RSRC_CAVE_OFFSET
        cave_len = mod.RSRC_CODE_END_OFFSET - mod.RSRC_CAVE_OFFSET
    finally:
        pe.close()
    diffs = [i for i in range(len(candidate)) if candidate[i] != v6_candidate[i]]
    assert diffs, "expected at least the two call sites and the cave to differ"
    allowed = (
        set(range(save_site_off, save_site_off + 5))
        | set(range(load_site_off, load_site_off + 5))
        | set(range(section_header_off, section_header_off + 40))
        | set(range(cave_off, cave_off + cave_len))
    )
    assert set(diffs) <= allowed, f"unexpected byte differences outside pinned scope: {sorted(set(diffs) - allowed)}"


def test_call_site_old_bytes_are_the_pinned_stock_stream_calls(original: bytes) -> None:
    v6_candidate, _v6_report = mod.v6.build_candidate(original)
    pe = pefile.PE(data=v6_candidate, fast_load=True)
    try:
        save_off = _offset(pe, mod.SAVE_CALL_VA)
        load_off = _offset(pe, mod.LOAD_CALL_VA)
    finally:
        pe.close()
    assert v6_candidate[save_off : save_off + 5] == mod.SAVE_CALL_OLD
    assert v6_candidate[load_off : load_off + 5] == mod.LOAD_CALL_OLD
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    save_insn = next(md.disasm(mod.SAVE_CALL_OLD, mod.SAVE_CALL_VA))
    load_insn = next(md.disasm(mod.LOAD_CALL_OLD, mod.LOAD_CALL_VA))
    assert save_insn.mnemonic == "call" and save_insn.op_str == hex(mod.STREAM_SAVE_FN)
    assert load_insn.mnemonic == "call" and load_insn.op_str == hex(mod.STREAM_LOAD_FN)


def test_rsrc_cave_fits_and_is_marked_executable(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        assert int(rsrc.Misc_VirtualSize) >= mod.RSRC_CODE_END_OFFSET
        assert int(rsrc.Characteristics) & mod.RSRC_EXECUTE_CODE_FLAGS == mod.RSRC_EXECUTE_CODE_FLAGS
        save_off = _offset(pe, int(report["hooks"]["save"]["wrapper_va"], 16))
        load_off = _offset(pe, int(report["hooks"]["load"]["wrapper_va"], 16))
    finally:
        pe.close()
    assert report["hooks"]["save"]["bytes"] <= mod.LOAD_WRAPPER_OFFSET - mod.SAVE_WRAPPER_OFFSET
    assert report["hooks"]["load"]["bytes"] <= mod.RSRC_CODE_END_OFFSET - mod.LOAD_WRAPPER_OFFSET
    save_bytes = candidate[save_off : save_off + report["hooks"]["save"]["bytes"]]
    load_bytes = candidate[load_off : load_off + report["hooks"]["load"]["bytes"]]

    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    save_insns = list(md.disasm(save_bytes, int(report["hooks"]["save"]["wrapper_va"], 16)))
    assert save_insns[0].mnemonic == "pushal"
    assert save_insns[-1].mnemonic == "jmp" and save_insns[-1].op_str == hex(mod.STREAM_SAVE_FN)
    assert save_insns[-2].mnemonic == "popal"

    load_insns = list(md.disasm(load_bytes, int(report["hooks"]["load"]["wrapper_va"], 16)))
    assert load_insns[0].mnemonic == "push" and load_insns[0].op_str == "ebp"
    assert any(i.mnemonic == "call" and i.op_str == hex(mod.STREAM_LOAD_FN) for i in load_insns)
    assert load_insns[-1].mnemonic == "ret"
    assert load_insns[-2].mnemonic == "pop" and load_insns[-2].op_str == "ebp"


def test_shadow_addresses_match_the_pinned_legacy_selection_window() -> None:
    # 0x00899028 + 20 * 4 == 0x00899078, the exact legacy end-bound v1's
    # END_SITES already pin; the shadow must stay inside that stock window.
    assert mod.LEGACY_ENTRIES_ADDR == 0x00899028
    assert mod.LEGACY_ENTRIES_ADDR + mod.STOCK_CAPACITY * 4 == 0x00899078
    assert mod.LEGACY_COUNT_ADDR == 0x00899024
