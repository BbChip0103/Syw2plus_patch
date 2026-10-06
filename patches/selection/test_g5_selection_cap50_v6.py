import hashlib
import importlib.util
import sys
from pathlib import Path

import capstone
import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v6.py")
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


def test_build_is_v5_plus_one_pinned_hook_and_private_cave(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    v5_candidate, v5_report = mod.v5.build_candidate(original)
    assert len(candidate) == len(original)
    assert report["v5_candidate_sha256"] == hashlib.sha256(v5_candidate).hexdigest()
    assert report["v5_candidate_sha256"] == v5_report["candidate_sha256"]
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] != report["v5_candidate_sha256"]


def test_only_the_h4_site_and_cave_differ_from_v5(original: bytes) -> None:
    """v6 must not touch anything v5 already established -- drag/move/attack/
    group-assign/recall behavior for live members must be byte-identical."""
    candidate, _report = mod.build_candidate(original)
    v5_candidate, _v5_report = mod.v5.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        site_off = _offset(pe, mod.H4_SITE)
        cave_off = _offset(pe, mod.H4_CAVE)
    finally:
        pe.close()
    diffs = [i for i in range(len(candidate)) if candidate[i] != v5_candidate[i]]
    assert diffs, "expected at least the hook site and cave to differ"
    allowed = set(range(site_off, site_off + len(mod.H4_OLD))) | set(
        range(cave_off, cave_off + len(mod._assemble_h4()))
    )
    assert set(diffs) <= allowed, f"unexpected byte differences outside H4 site/cave: {sorted(set(diffs) - allowed)}"


def test_hook_site_old_bytes_are_the_stock_call_to_group_removal(original: bytes) -> None:
    v5_candidate, _v5_report = mod.v5.build_candidate(original)
    pe = pefile.PE(data=v5_candidate, fast_load=True)
    try:
        off = _offset(pe, mod.H4_SITE)
    finally:
        pe.close()
    assert v5_candidate[off : off + len(mod.H4_OLD)] == mod.H4_OLD
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insn = next(md.disasm(mod.H4_OLD, mod.H4_SITE))
    assert insn.mnemonic == "call"
    assert insn.op_str == hex(mod.H4_TARGET)


def test_h4_cave_fits_within_limit_and_decodes(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    cave_end = int(report["hook"]["cave_end_exclusive"], 16)
    assert cave_end <= mod.CAVE_LIMIT
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        cave_off = _offset(pe, mod.H4_CAVE)
        site_off = _offset(pe, mod.H4_SITE)
    finally:
        pe.close()
    h4_bytes = mod._assemble_h4()
    assert candidate[cave_off : cave_off + len(h4_bytes)] == h4_bytes

    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    site_insns = list(md.disasm(candidate[site_off : site_off + 5], mod.H4_SITE))
    assert len(site_insns) == 1
    assert site_insns[0].mnemonic == "jmp"
    assert site_insns[0].op_str == hex(mod.H4_CAVE)

    cave_insns = list(md.disasm(h4_bytes, mod.H4_CAVE))
    # the original removal call must still run first, unmodified target
    assert cave_insns[0].mnemonic == "call" and cave_insns[0].op_str == hex(mod.H4_TARGET)
    # every control-transfer instruction must land inside the cave itself or
    # exactly at the resume address / the original call target -- no stray
    # jumps into unrelated code.
    valid_targets = {mod.H4_TARGET, mod.H4_RETURN, 0x0040F750} | {insn.address for insn in cave_insns}
    for insn in cave_insns:
        if insn.mnemonic in ("jmp", "je", "jne", "call"):
            target = int(insn.op_str, 16)
            assert target in valid_targets, f"{insn.mnemonic} {insn.op_str} leaves the expected target set"
    # the cave must end by returning control to the instruction right after
    # the original 5-byte call site, not by falling off the end or ret-ing.
    assert cave_insns[-1].mnemonic == "jmp"
    assert cave_insns[-1].op_str == hex(mod.H4_RETURN)
    assert cave_insns[-2].mnemonic == "popal"


def test_h4_cave_matches_only_low_word_within_the_units_own_group(original: bytes) -> None:
    """Structural regression for the fix itself: the scan must be bounded to
    exactly one group's 20 entries (``GROUP_STRIDE`` * the unit's own
    ``+0x344`` value, not all 10 groups), compare only the entry's low word
    (slot) against the dying unit's own slot, and unconditionally force
    ``unit+0x344 = -1`` afterwards via the existing setter."""
    h4_bytes = mod._assemble_h4()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insns = list(md.disasm(h4_bytes, mod.H4_CAVE))
    mnems = [(i.mnemonic, i.op_str) for i in insns]

    assert ("cmp", "eax, -1") in mnems  # skip immediately if not a member of anything
    assert any(m == "imul" and "0x50" in op for m, op in mnems)  # one group's stride only
    assert any(m == "cmp" and op == "ax, cx" for m, op in mnems)  # low-word-only match
    # no high-word ([edi+2]) comparison anywhere in the scan -- confirms this
    # intentionally does not require the aux/high-word match FUN_00445A90 uses.
    assert not any("edi + 2]" in op and m == "cmp" for m, op in mnems)
    assert ("call", hex(0x0040F750)) in mnems  # force-clear via the stock setter
    assert ("push", "-1") in mnems
