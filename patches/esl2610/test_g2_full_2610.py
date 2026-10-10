from __future__ import annotations

from pathlib import Path

import pytest

from patches.esl2610 import g2_bounds_2610, g2_full_2610, g2_newcode_2610, g2_scan
from patches.esl2610 import g2_state_2610 as st
from patches.esl2610 import pe_extend

STOCK = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists():
        pytest.fail("pinned official 2613 EXE missing: the G2 build cannot be verified here")
    return pe_extend.BASE_PATH.read_bytes()


@pytest.fixture(scope="module")
def built(base):
    if not STOCK.exists():
        pytest.fail("stock oracle EXE missing: the G2 build cannot be verified here")
    return g2_full_2610.build_candidate(base, STOCK.read_bytes())


def test_state_map_expands_arrays_in_place():
    sec = next(s for s in st.STATE_SECTIONS if s.name == ".hrstate")
    new = 0x02000000
    # header unchanged, list grows, hr_unit follows the grown list
    assert sec.map(0x01193000, new) == new
    assert sec.map(0x01193020, new) == new + 0x20
    hr_unit = sec.map(0x011942E0, new)
    assert hr_unit == new + 0x20 + 4 * 4093
    # the list end and the next array's base map to the same address
    assert sec.map(0x01193020 + 4 * 1200, new) == hr_unit
    assert sec.map(sec.end, new) == hr_unit + 0x40 * 4093


def test_stream_wrapper_rejects_missing_size_when_buffer_is_supplied():
    from patches.esl2610.g2_persist_2610 import _Asm

    with pytest.raises(ValueError, match="size"):
        _Asm(0x00401000).stream(0x00402000, 0x02200000, None)


def test_layout_honours_encoded_base_alignment():
    starts = st.layout(0x02282000)
    for name, m, _ in st.ENCODED_BASES:
        sec, arr = st._array(name)  # noqa: SLF001
        assert sec.map(arr.base, starts[sec.name]) % m == 0
    names = [s.name for s in st.STATE_SECTIONS]
    for a, b in zip(names, names[1:]):
        sec_a = next(s for s in st.STATE_SECTIONS if s.name == a)
        assert starts[a] + sec_a.new_size <= starts[b]


def test_div_magic_is_exact_for_4093():
    for n in range(0, 1 << 16):
        assert (n * st.DIV_MAGIC_NEW) >> (32 + st.DIV_SHIFT_NEW) == n // 4093
    assert st.DIV_MAGIC_NEW < 1 << 31  # also valid as the signed imul form


def test_family_values():
    assert g2_bounds_2610.new_value(0x4B0) == 0xFFD
    assert g2_bounds_2610.new_value(0x4AF) == 0xFFC
    assert g2_bounds_2610.new_value(0xFFFFFB51) == (-0xFFC) & 0xFFFFFFFF
    assert g2_bounds_2610.new_value(0xFB51) == (-0xFFC) & 0xFFFF
    assert g2_bounds_2610.new_value(0x226C80) == 0x758 * 4093
    assert g2_bounds_2610.new_value(0x226528) == 0x758 * 4092
    assert g2_bounds_2610.new_value(0x12C4) == 4 * 4093 + 4
    assert g2_bounds_2610.new_value(0xFFFEF970) == (-(0x10 + 0x38 * 4093)) & 0xFFFFFFFF


FULL_SHA256 = "9d2179c4b4b91e8d3fe4d7aebfc152723f6c2025323ee784aaefd08008c18d90"


def test_full_candidate_counts_are_pinned(built):
    candidate, report = built
    assert report["candidate_sha256"] == FULL_SHA256
    assert report["layer2"]["counts"] == {
        "relocated": 856, "neg_pool_base": 65, "kept": 7, "pool_end_cmp": 21,
        "pool_end_neg": 15, "exist_end": 12, "div_test": 3, "text_extra": 1,
        "text_bulk_by_oracle": 12, "text_bulk": 6}
    assert report["layer1"]["rebased_bulk_relative_disps"] == 13
    assert report["layer2"]["clamp"] == 4093
    assert report["layer3"]["counts"] == {
        "absolute": 2773, "regbase": 89, "encoded": 6, "raise": 390, "div": 8,
        "absolute_skipped_relative": 1, "text_raise": 5, "blob_length": 14,
        "data_ptr": 1, "stack_bitset": 3}
    assert report["layer3"]["table"] == {"raise": 390, "keep": 40, "regbase": 18}
    assert report["layer3"]["text_table"] == {"oracle": 5, "raise": 5, "keep": 54, "layer2": 0}


def test_2613_kills_pool_reference_follows_relocated_array(built):
    from patches.esl2610.g2_newcode_2610 import _insn

    candidate, report = built
    assert _insn(candidate, 0x0115BFAB).disp == int(report["layer2"]["new_pool"], 16) + 0x8D


def _starts(report):
    return {k: int(v, 16) for k, v in report["layer3"]["starts"].items()}


def test_displacements_off_a_non_moved_base_follow_their_target(built):
    """H1: ecx=0x893130 (bulk record) + disp into .f2data / .r17data."""
    from patches.esl2610.g2_newcode_2610 import _insn

    candidate, report = built
    starts = _starts(report)
    for va, old_target in ((0x019A75D6, 0x0160530C), (0x019A75F5, 0x01A44000),
                           (0x019A75FF, 0x016052F0)):
        disp = _insn(candidate, va).disp & 0xFFFFFFFF
        assert (0x00893130 + disp) & 0xFFFFFFFF == st.map_value(old_target, starts)


def test_end_plus_field_sentinels_are_mapped(built):
    """H2: end+4 loop ends / end-relative fields of a section's last array."""
    from patches.esl2610.g2_newcode_2610 import _insn

    candidate, report = built
    starts = _starts(report)
    for va, old in ((0x011A79DC, 0x011B2094), (0x012568D0, 0x012728D4)):
        assert _insn(candidate, va).operands[1].imm == st.map_value(old, starts)
    assert _insn(candidate, 0x0160176A).disp == st.map_value(0x0160CFC0, starts)


def test_no_unmapped_operand_next_to_a_moved_range(base, built):
    """Operands within 0x40 past a whole-section range must have been moved."""
    candidate, _ = built
    from capstone import x86

    whole = [sec for sec in st.STATE_SECTIONS if sec.whole]
    for name, va, vsize, rs, rp in g2_scan._executable_sections(base):  # noqa: SLF001
        size = min(rs, max(vsize, 1)) if vsize else rs
        for insn in g2_scan._sweep(base[rp : rp + size], va):  # noqa: SLF001
            if insn.mnemonic == "call" or insn.mnemonic.startswith("j"):
                continue
            for op in insn.operands:
                v = (op.imm if op.type == x86.X86_OP_IMM else op.mem.disp
                     if op.type == x86.X86_OP_MEM else None)
                if v is None:
                    continue
                v &= 0xFFFFFFFF
                for sec in whole:
                    if sec.end < v <= sec.end + 0x40:
                        assert sec.contains(v), (hex(insn.address), sec.name)


def test_blob_and_clear_lengths_cover_the_grown_arrays(built):
    """H3/H4: KIL1 and PSN2 blobs and their clears span the grown layout."""
    from patches.esl2610.g2_newcode_2610 import _insn

    candidate, report = built
    starts = _starts(report)
    kill = st.blob_length((st.KILL_FROM, st.KILL_TO), starts)
    psn = st.blob_length((st.PSN_FROM, st.PSN_TO), starts)
    assert kill == 0x20 * 4093 + 0x1000 and psn == 0x16000 + 0x10 * 2893
    for va in (0x0115B28A, 0x0115B4C7):
        assert _insn(candidate, va).operands[1].imm == kill // 4
    for va in (0x01091043,):
        assert _insn(candidate, va).operands[1].imm == psn
    for va in (0x01090DB8, 0x0109114B):
        assert _insn(candidate, va).operands[1].imm == psn // 4
    # the KIL1 size check goes to the converter in .g2code (grown + official sizes)
    kil1 = report["layer4"]["kil1"]
    assert int(kil1["grown_size"], 16) == kill and kil1["legacy_size"] == "0xa600"
    assert _insn(candidate, 0x0115B485).mnemonic == "jmp"


def test_text_unit_bounds_are_raised(built):
    from patches.esl2610.g2_newcode_2610 import _insn

    candidate, _ = built
    for va in (0x004183A8, 0x004183BE, 0x00422DC7):
        assert _insn(candidate, va).operands[1].imm == 4093
    assert _insn(candidate, 0x00418425).op_str == "bx, 0xffd"
    assert _insn(candidate, 0x00444F8A).op_str == "esi, 0xffd"
    # per-player roster capacity stays (official per-player cap 1008 < 1200)
    assert _insn(candidate, 0x0043EE37).op_str == "ax, 0x4b0"


def test_save_format_marker_and_manifest(built):
    candidate, report = built
    l4 = report["layer4"]
    assert l4["marker"] == "S2P2"
    code = int(l4["g2code_va"], 16)
    off = pe_extend.va_to_offset(candidate, code + 0x600)
    import struct as _s
    magic, version, layout, *sizes = _s.unpack_from("<8I", candidate, off)
    assert magic == int.from_bytes(b"G2MF", "little") and version == 1
    assert layout == int(l4["layout_hash"], 16)
    assert sizes == [int(x["size"], 16) for x in l4["sidecars"]]


def test_full_candidate_leaves_no_old_reference(base, built):
    candidate, report = built
    # no operand into a moved module range is left (one data misdecode is a call)
    # (bulk-object-relative displacements in 0x4A3xxx and the three displacements
    # off ecx=0x893130 are numerically in range but are relative, not addresses)
    left = [(n, i.address) for n, i, k, v in st.absolute_refs(candidate)
            if v < 0x01AB5000 and i.mnemonic != "call"
            and not 0x004A3000 <= i.address < 0x004A3A40
            and i.address not in (0x019A75D6, 0x019A75F5, 0x019A75FF)]
    assert left == []
    # the only six-array operands left in 2610 code are the reviewed keeps
    inv = g2_scan.build_inventory(candidate, require_pinned_base=False)
    kept = {s.va for s in inv.sites if s.op_kind in ("disp", "imm", "neg_pool_base")
            and s.section not in (".text", ".rsrc") and s.value < 0x00892410
            and s.va in g2_newcode_2610.KEEP_SITES}
    assert kept == set(g2_newcode_2610.KEEP_SITES)
    # every raised capacity operand is gone
    rows = g2_bounds_2610.build_table(
        base, {u.address for _, _, u, _, _ in st.register_base_uses(base)})
    raised = {r["va"] for r in rows if r["decision"] == "raise"}
    assert not [i.address for _, i, _, _, _ in g2_bounds_2610.family_operands(candidate)
                if i.address in raised]


def test_full_candidate_keeps_product_caps(base, built):
    candidate, _ = built
    # official per-player cap 1008 (0x3F0) at the allocation gate and the
    # official supply formula (1500 + 200 per hero) are untouched
    for va, raw in ((0x0043EDB0, bytes.fromhex("663df003")),
                    (0x0043FE9E, bytes.fromhex("81c1c8000000")),
                    (0x0043FFD4, bytes.fromhex("05dc050000"))):
        off = pe_extend.va_to_offset(candidate, va)
        assert candidate[off : off + len(raw)] == raw


def test_active_list_walk_and_reset_follow_the_relocation(built):
    """The vision rebuild walks the active list relative to the bulk object."""
    candidate, _ = built
    from patches.esl2610.g2_newcode_2610 import _insn

    walk = _insn(candidate, 0x004A39E6)
    count = _insn(candidate, 0x004A39DA)
    assert (0x00892410 + walk.disp) & 0xFFFFFFFF == 0x022179D8  # == [0x41CD56] list base
    assert (0x00892410 + count.disp) & 0xFFFFFFFF == 0x022199D2  # == [0x41CD2A] count
    assert _insn(candidate, 0x004A3222).op_str == "ecx, 0xffd"


def test_no_kept_capacity_gate_is_a_unit_limit(base):
    """Every kept 1200-family constant has a recorded non-unit reason."""
    rows = g2_bounds_2610.build_table(
        base, {u.address for _, _, u, _, _ in st.register_base_uses(base)})
    kept = [r for r in rows if r["decision"] == "keep"]
    assert len(kept) == 40
    assert not [r for r in kept if "frozen" in r["why"] or "selection" in r["why"]]
    assert all(r["section"] != ".navcode" or "6000" in r["why"] for r in kept)


def test_selection_buffer_grows_with_the_pool(built):
    from patches.esl2610.g2_newcode_2610 import _insn

    candidate, report = built
    starts = _starts(report)
    base_va = st.map_value(0x01604004, starts)
    assert _insn(candidate, 0x00412E3C).operands[1].imm == base_va
    assert _insn(candidate, 0x00412E52).operands[1].imm == base_va + 4 * 4096
    assert _insn(candidate, 0x0113420A).operands[1].imm == 4096


def test_official_psn2_blob_is_converted_so_kil1_still_loads(built):
    """Official saves: the PSN2 success path is the only way to the KIL1 load."""
    import capstone

    from patches.esl2610 import g2_persist_2610 as gp
    from patches.esl2610.g2_newcode_2610 import _insn

    candidate, report = built
    psn = report["layer4"]["psn2"]
    code = int(report["layer4"]["g2code_va"], 16)
    assert _insn(candidate, gp.PSN2_SIZE_CHECK_VA).op_str == hex(code + gp.PSN_OFF)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    off = pe_extend.va_to_offset(candidate, code + gp.PSN_OFF)
    text = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(candidate[off : off + 0xA0], code + gp.PSN_OFF)]
    assert f"cmp dword ptr [{hex(int(psn['header'], 16) + 8)}], {psn['grown_size']}" in text
    assert f"cmp dword ptr [{hex(int(psn['header'], 16) + 8)}], 0x16000" in text
    # prefix + 1200 cache entries copied, the 2893 new entries zeroed, the tail moved
    assert "mov ecx, 0x42c0" in text and "mov ecx, 0x2d34" in text and "mov ecx, 0x1540" in text
    assert f"jmp {hex(gp.PSN2_SUCCESS_VA)}" in text


def test_loads_clear_the_stock_arrays_the_bulk_block_restores(built):
    import capstone

    from patches.esl2610 import g2_persist_2610 as gp

    candidate, report = built
    code = int(report["layer4"]["g2code_va"], 16)
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    off = pe_extend.va_to_offset(candidate, code + gp.ZERO_OFF)
    text = [f"{i.mnemonic} {i.op_str}" for i in md.disasm(candidate[off : off + 0x60], code + gp.ZERO_OFF)]
    for old in ("0x8990c8", "0x899a28", "0x89b008", "0x89c2ca", "0x974fa8"):
        assert f"mov edi, {old}" in text
