import hashlib
import importlib.util
import sys
from pathlib import Path

import capstone
import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v9.py")
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


def test_build_is_deterministic_and_v8_plus_one_hook(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    candidate2, report2 = mod.build_candidate(original)
    v8_candidate, v8_report = mod.v8.build_candidate(original)
    assert len(candidate) == len(original)
    assert candidate == candidate2
    assert report["candidate_sha256"] == report2["candidate_sha256"]
    assert report["v8_candidate_sha256"] == hashlib.sha256(v8_candidate).hexdigest()
    assert report["v8_candidate_sha256"] == v8_report["candidate_sha256"]
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] != report["v8_candidate_sha256"]


def test_hook_old_bytes_are_the_pinned_stock_encoding(original: bytes) -> None:
    v8_candidate, _v8_report = mod.v8.build_candidate(original)
    pe = pefile.PE(data=v8_candidate, fast_load=True)
    try:
        hook_off = _offset(pe, mod.NEWGAME_HOOK_VA)
    finally:
        pe.close()
    actual = v8_candidate[hook_off : hook_off + len(mod.NEWGAME_HOOK_OLD)]
    assert actual == mod.NEWGAME_HOOK_OLD
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insn = next(md.disasm(mod.NEWGAME_HOOK_OLD, mod.NEWGAME_HOOK_VA))
    assert insn.mnemonic == "mov"
    assert insn.op_str == "dword ptr [esi + 0x6c14], ebx"
    assert insn.size == len(mod.NEWGAME_HOOK_OLD)


def test_only_the_hook_site_cave_and_section_header_differ_from_v8(original: bytes) -> None:
    """v9 must not touch anything v8 already established -- the save/load
    wrappers, every prior selection-cap50 site, and the rest of the binary
    must be byte-identical; only the new-game-init hook, its cave, and the
    .rsrc section header's VirtualSize field may change."""
    candidate, report = mod.build_candidate(original)
    v8_candidate, _v8_report = mod.v8.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        hook_off = _offset(pe, mod.NEWGAME_HOOK_VA)
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        section_header_off = rsrc.get_file_offset()
        cave_off = rsrc.PointerToRawData + mod.NEWGAME_CAVE_OFFSET
        cave_len = mod.NEWGAME_CAVE_END_OFFSET - mod.NEWGAME_CAVE_OFFSET
    finally:
        pe.close()
    diffs = [i for i in range(len(candidate)) if candidate[i] != v8_candidate[i]]
    assert diffs, "expected at least the hook site and cave to differ"
    allowed = (
        set(range(hook_off, hook_off + len(mod.NEWGAME_HOOK_OLD)))
        | set(range(section_header_off, section_header_off + 40))
        | set(range(cave_off, cave_off + cave_len))
    )
    assert set(diffs) <= allowed, (
        f"unexpected byte differences outside pinned scope: {sorted(set(diffs) - allowed)}"
    )


def test_cave_reproduces_original_write_then_zeroes_the_relocated_array(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        cave_va = int(report["hooks"]["newgame_init"]["cave_va"], 16)
        cave_off = _offset(pe, cave_va)
    finally:
        pe.close()
    cave_bytes = candidate[cave_off : cave_off + report["hooks"]["newgame_init"]["bytes"]]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insns = list(md.disasm(cave_bytes, cave_va))

    assert insns[0].mnemonic == "mov"
    assert insns[0].op_str == "dword ptr [esi + 0x6c14], ebx", (
        "the cave must reproduce the original instruction it replaced before doing anything else"
    )
    assert insns[1].mnemonic == "pushal"
    assert insns[-1].mnemonic == "jmp" and insns[-1].op_str == hex(mod.NEWGAME_RESUME_VA)
    assert insns[-2].mnemonic == "popal"

    stosd = [i for i in insns if i.mnemonic.endswith("stosd")]
    assert len(stosd) == 1
    mov_edi = next(i for i in insns if i.mnemonic == "mov" and i.op_str.startswith("edi, 0x"))
    assert int(mov_edi.op_str.split(",")[1].strip(), 16) == mod.SELECTION_BASE
    mov_ecx = next(
        i for i in insns[2:] if i.mnemonic == "mov" and i.op_str.startswith("ecx, ")
    )
    assert int(mov_ecx.op_str.split(",")[1].strip(), 0) == mod.SELECTION_DWORDS
    assert mod.SELECTION_DWORDS == 1 + mod.TARGET_CAPACITY


def test_hook_replacement_is_a_same_length_jmp_plus_nop(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        hook_off = _offset(pe, mod.NEWGAME_HOOK_VA)
    finally:
        pe.close()
    hook_bytes = candidate[hook_off : hook_off + len(mod.NEWGAME_HOOK_OLD)]
    assert len(hook_bytes) == len(mod.NEWGAME_HOOK_OLD)
    assert hook_bytes[0] == 0xE9
    assert hook_bytes[-1] == 0x90
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insn = next(md.disasm(hook_bytes[:5], mod.NEWGAME_HOOK_VA))
    assert insn.mnemonic == "jmp"
    assert insn.op_str == report["hooks"]["newgame_init"]["cave_va"]


def test_new_game_init_callers_are_the_three_pinned_sites() -> None:
    assert mod.NEWGAME_INIT_CALLERS == (0x0041B9C0, 0x0041BC4F, 0x004C3E59)


def test_cave_region_does_not_overlap_v7_v8_own_cave() -> None:
    assert mod.NEWGAME_CAVE_OFFSET >= mod.v8.v7.RSRC_CODE_END_OFFSET
    assert mod.NEWGAME_CAVE_OFFSET == mod.RSRC_CODE_END_OFFSET
