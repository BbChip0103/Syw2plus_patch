from __future__ import annotations

import struct

import pytest

from patches.esl2610 import g2_reloc_2610 as mod
from patches.esl2610 import pe_extend


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists():
        pytest.skip("local pinned ESL2610 executable required")
    return pe_extend.BASE_PATH.read_bytes()


@pytest.fixture(scope="module")
def plan(base):
    return mod.plan_spike(base)


def test_relocate_value_maps_each_region_into_the_packed_block():
    pb = mod._PACK_BASE  # map onto the geometry's own base (offset 0)
    # pool base maps to pool base; existence base maps just past the grown pool.
    assert mod.relocate_value(mod.g2_scan.POOL[0], pb) == pb
    grown_pool_end = pb + mod.UNIT_STRIDE * mod.CAPACITY
    assert mod.relocate_value(mod.g2_scan.EXIST[0], pb) == grown_pool_end
    with pytest.raises(ValueError):
        mod.relocate_value(0x00500000, pb)  # outside every region


def test_active_list_one_based_base_and_count_word_map_correctly():
    pb = mod._PACK_BASE
    active = mod._GEO_BY_NAME["active_slot_list"]
    new_start = pb + (active.new_start - mod._PACK_BASE)
    # 1-based base (two bytes below the array start) maps two bytes below.
    assert mod.relocate_value(0x00974FA6, pb) == new_start - 2
    assert mod.relocate_value(0x00974FA8, pb) == new_start  # array start
    # trailing count word (array_old_span past the array start) lands past the
    # grown 4093-sized array.
    count_word = active.old_start + active.array_old_span
    assert mod.relocate_value(count_word, pb) == new_start + active.array_new_span


def test_g2bss_base_is_first_free_rva(plan, base):
    import pefile

    pe = pefile.PE(data=base, fast_load=True)
    try:
        assert plan.g2bss_va == mod.IMAGE_BASE + int(pe.OPTIONAL_HEADER.SizeOfImage)
    finally:
        pe.close()


def test_four_direct_arrays_packed_without_overlap(plan):
    assert len(plan.direct_arrays) == 4
    names = {a["name"] for a in plan.direct_arrays}
    assert names == {".wecache", ".rsidle", ".killdat_sub", ".mvstate_body"}
    blocks = [(plan.six_array_base, plan.six_array_base + plan.six_array_span)]
    for a in plan.direct_arrays:
        lo = int(a["new_base"], 16)
        hi = lo + int(a["span_4093"], 16)
        for blo, bhi in blocks:
            assert not (lo < bhi and blo < hi), f"{a['name']} overlaps"
        blocks.append((lo, hi))


def test_direct_array_spans_are_stride_times_capacity(plan):
    for a in plan.direct_arrays:
        assert int(a["span_1200"], 16) == int(a["stride"], 16) * mod.STOCK_CAPACITY
        assert int(a["span_4093"], 16) == int(a["stride"], 16) * mod.CAPACITY


def test_every_gate_and_memset_site_matches_pinned_old_bytes(base):
    # The 1200/0x758*1200 immediates and memset dword counts the plan will edit
    # must actually be present at the recorded VAs, or the plan is stale.
    def imm32_at(va: int, expected: int) -> bool:
        off = pe_extend.va_to_offset(base, va)
        window = base[off : off + 16]
        needle = struct.pack("<I", expected)
        return needle in window

    for arr in mod.SPIKE_ARRAYS:
        for va in arr.gate_sites:
            assert imm32_at(va, mod.STOCK_CAPACITY), f"{arr.name} gate 0x{va:08x}"
        for va in arr.byte_span_gate_sites:
            span = mod.UNIT_STRIDE * mod.STOCK_CAPACITY
            # the planner records the inclusive (0x226c80) or exclusive (0x226c7f) form
            assert imm32_at(va, span) or imm32_at(va, span - 1), f"{arr.name} span 0x{va:08x}"
        for va, count in arr.memset_sites:
            assert imm32_at(va, count), f"{arr.name} memset 0x{va:08x}"
        # every recorded site must resolve to a real file offset
        first = arr.gate_sites[0] if arr.gate_sites else arr.byte_span_gate_sites[0]
        assert pe_extend.va_to_offset(base, first) > 0


def test_plan_still_reports_blockers_fail_closed(plan):
    # Settling the spike pattern does not unblock the build: the remaining
    # modules/bounds/arrays stay blockers.
    assert plan.blocked
    kinds = {b["kind"] for b in plan.blocked}
    assert "new_code_unit_capacity_refs" in kinds
    assert "capacity_bound_checks" in kinds


def test_build_stays_fail_closed_without_the_stock_oracle(base, monkeypatch, tmp_path):
    from patches.esl2610 import g2_pool4093_2610 as builder

    monkeypatch.setattr(builder, "STOCK_ORACLE", tmp_path / "missing.exe")
    with pytest.raises(builder.G2BuildBlocked):
        builder.build_candidate(base)
