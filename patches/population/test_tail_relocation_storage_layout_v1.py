import importlib.util
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "tail_relocation_storage_layout_v1", Path(__file__).with_name("tail_relocation_storage_layout_v1.py")
)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original():
    if not SOURCE.exists():
        pytest.skip("Local original game required")
    return SOURCE.read_bytes()


# ---------------------------------------------------------------------------
# N=1200 identity -- the work card W4 §4 required regression anchor: this
# module must be a pure no-op at the stock capacity.
# ---------------------------------------------------------------------------


def test_n1200_is_not_relocated():
    result = mod.layout(1200)
    assert result.relocated is False
    for region in result.regions:
        assert region.new_start == region.old_start
        assert region.delta == 0
    assert result.rsrc.new_start == result.rsrc.old_start
    assert result.rsrc.delta == 0


def test_n1200_size_of_image_matches_pinned_original():
    assert mod.layout(1200).size_of_image == 0xC8F000


def test_n1200_build_layout_artifact_is_byte_identical_to_original(original):
    artifact = mod.build_layout_artifact(original, 1200)
    assert artifact == original


# ---------------------------------------------------------------------------
# N=1210 relocation geometry -- work card W4 §1 requirements.
# ---------------------------------------------------------------------------


def test_n1210_regions_are_packed_at_the_tail_in_pool_existence_age_order():
    result = mod.layout(1210)
    assert result.relocated is True
    pool, existence, age = result.regions
    assert pool.name == "unit_pool"
    assert existence.name == "unit_existence"
    assert age.name == "unit_age"
    assert pool.new_start == mod.RSRC_BASE_VA
    assert existence.new_start == pool.new_end
    # The allocator's `[ecx-0x960]`-style scan requires existence and age to
    # be exactly adjacent (work card W4 §1) -- not just non-overlapping.
    assert age.new_start == existence.new_end


def test_n1210_relocated_regions_do_not_overlap_the_bulk_save_load_blob():
    result = mod.layout(1210)
    for region in result.regions:
        assert region.new_end <= mod.BULK_BLOB_START or region.new_start >= mod.BULK_BLOB_END


def test_n1210_rsrc_shifts_up_by_the_combined_relocated_span():
    result = mod.layout(1210)
    combined_span = sum(r.array_new_span for r in result.regions)
    raw_shift = result.regions[-1].new_end - result.rsrc.old_start
    assert raw_shift == combined_span
    # .rsrc's actual new base is the raw insertion point rounded *up* to
    # SectionAlignment (it is a real PE section start, not just an address
    # inside one) -- so the shift may exceed combined_span by at most one
    # alignment unit's worth of padding, never less.
    actual_shift = result.rsrc.new_start - result.rsrc.old_start
    assert combined_span <= actual_shift < combined_span + mod.SECTION_ALIGNMENT
    assert result.rsrc.new_start % mod.SECTION_ALIGNMENT == 0


def test_rejects_capacity_below_stock():
    with pytest.raises(ValueError):
        mod.layout(mod.STOCK_CAPACITY - 1)


def test_n1210_build_layout_artifact_changes_only_header_fields(original):
    artifact = mod.build_layout_artifact(original, 1210)
    assert len(artifact) == len(original)
    assert artifact != original
    # .text's raw bytes (this module never touches code) must be untouched;
    # only header/section-table/resource-offset fields differ.
    import pefile

    pe = pefile.PE(data=original, fast_load=True)
    text_sections = [s for s in pe.sections if s.Name.rstrip(b"\0") == b".text"]
    assert len(text_sections) == 1
    raw_start = int(text_sections[0].PointerToRawData)
    raw_end = raw_start + int(text_sections[0].SizeOfRawData)
    pe.close()
    assert artifact[raw_start:raw_end] == original[raw_start:raw_end]


# ---------------------------------------------------------------------------
# G-a / G-b -- the two mandatory pre-execution gates from work card W4 §4.
# Reusable regression anchors, not one-off probes.
# ---------------------------------------------------------------------------


def _text_insns(data: bytes):
    import capstone
    import pefile

    pe = pefile.PE(data=data, fast_load=True)
    try:
        matches = [s for s in pe.sections if s.Name.rstrip(b"\0") == b".text"]
        assert len(matches) == 1
        section = matches[0]
        va_start = mod.IMAGE_BASE + int(section.VirtualAddress)
        raw_start = int(section.PointerToRawData)
        raw_end = raw_start + int(section.SizeOfRawData)
        text_bytes = bytes(pe.__data__[raw_start:raw_end])
    finally:
        pe.close()
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    engine.detail = True
    engine.skipdata = True
    return [i for i in engine.disasm(text_bytes, va_start) if i.mnemonic != ".byte"]


def _literal_operands_in_range(insns, lo: int, hi: int) -> dict[int, tuple[str, int]]:
    import capstone

    hits: dict[int, tuple[str, int]] = {}
    for insn in insns:
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_MEM:
                value = int(op.mem.disp) & 0xFFFFFFFF
                kind = "disp"
            elif op.type == capstone.x86.X86_OP_IMM:
                value = int(op.imm) & 0xFFFFFFFF
                kind = "imm"
            else:
                continue
            if lo <= value < hi:
                hits[insn.address] = (kind, value)
    return hits


# G-a: the original binary must not already use the destination span for
# something else. lap400 D4 found exactly one non-address false positive.
G_A_KNOWN_NON_ADDRESS_SITES = frozenset({0x00401402})


def test_ga_original_has_no_live_references_into_the_n1210_tail_destination(original):
    result = mod.layout(1210)
    lo, hi = result.regions[0].new_start, result.regions[-1].new_end
    hits = _literal_operands_in_range(_text_insns(original), lo, hi)
    assert set(hits) <= G_A_KNOWN_NON_ADDRESS_SITES, (
        f"unclassified literal reference(s) into the tail destination: {hits}"
    )


def test_gb_bulk_blob_references_are_unaffected_except_the_relocated_sites(original):
    from patches.population.g2_unit_pool_expansion_v1 import build_candidate

    patched, _ = build_candidate(original, 1210)
    lo, hi = mod.BULK_BLOB_START, mod.BULK_BLOB_END
    before = _literal_operands_in_range(_text_insns(original), lo, hi)
    after = _literal_operands_in_range(_text_insns(patched), lo, hi)
    # Relocating existence/age out of the blob may only *remove* sites from
    # this range (their va now encodes the new tail address, outside [lo,
    # hi)) -- it must never introduce a new reference into the blob, and it
    # must never change the value of a site that is still inside the blob
    # (that would mean category_slot_list_a/b/active_slot_list -- none of
    # which this module ever touches -- silently moved).
    assert set(after) <= set(before)
    for va in after:
        assert after[va] == before[va]


# ---------------------------------------------------------------------------
# G-c -- work card W5 §2: every byte of the relocated pool/existence/age
# block must lie inside some section's declared [VA, VA+VirtualSize) in the
# candidate's *own* section table. lap402 D1 found a candidate that passed
# G-a/G-b/N=1200-identity yet left 99.24% of this block outside every
# section (a `.data` VirtualSize computed from growth-delta instead of the
# relocated block's absolute extent). This is the regression anchor that
# would have caught it.
# ---------------------------------------------------------------------------


def _sections(data: bytes) -> list[dict[str, int]]:
    import struct

    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    num = struct.unpack_from("<H", data, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe_off + 20)[0]
    table = pe_off + 24 + opt_size
    out = []
    for i in range(num):
        off = table + i * 40
        vsz, va, _rsz, _rp = struct.unpack_from("<IIII", data, off + 8)
        out.append({"va": mod.IMAGE_BASE + va, "virtual_end": mod.IMAGE_BASE + va + vsz})
    return out


def test_gc_n1210_relocated_block_is_fully_covered_by_declared_sections(original):
    result = mod.layout(1210)
    artifact = mod.build_layout_artifact(original, 1210)
    cand_sections = _sections(artifact)
    for region in result.regions:
        covered = sum(
            max(0, min(region.new_end, sec["virtual_end"]) - max(region.new_start, sec["va"]))
            for sec in cand_sections
        )
        assert covered == region.new_end - region.new_start, (
            f"{region.name} [{hex(region.new_start)}, {hex(region.new_end)}) is only "
            f"{covered}/{region.new_end - region.new_start} bytes inside a declared section"
        )
