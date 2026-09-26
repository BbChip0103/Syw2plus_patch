from pathlib import Path

import pefile
import pytest

from patches.population import full_tail_relocation_storage_layout_v1 as full_layout
from patches.population import g2_full_unit_capacity_v1 as mod
from patches.population import g2_full_unit_capacity_supply5000_v1 as combined_mod
from patches.population import g2_full_capacity_supply5000_owner1200_v1 as product_mod
from patches.population import g2_full_capacity_persistence_v1 as persistence_mod
from patches.population import g2_full_capacity_persistence_compat_v1 as persistence_compat_mod
from patches.population.fixed_owner_count_1200 import OWNER_COUNT_AFTER, OWNER_COUNT_FILE_OFFSET


ORIGINAL = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not ORIGINAL.exists():
        pytest.skip("Local original game required")
    return ORIGINAL.read_bytes()


def test_n1200_is_byte_identical(original: bytes) -> None:
    candidate, report = mod.build_candidate(original, 1200)
    assert candidate == original
    assert report["candidate_sha256"] == report["original_sha256"]


def test_n1250_relocates_all_six_regions_contiguously() -> None:
    result = full_layout.layout(1250)
    assert len(result.regions) == 6
    assert result.regions[0].new_start == full_layout.RSRC_BASE_VA
    for left, right in zip(result.regions, result.regions[1:]):
        assert left.new_end == right.new_start
    assert result.regions[-1].new_end <= result.rsrc.new_start


def test_list_counts_follow_expanded_arrays_not_stock_offsets() -> None:
    result = full_layout.layout(1250)
    for index in range(3, 6):
        spec = full_layout.REGIONS[index]
        region = result.regions[index]
        old_count = spec.base + spec.elem_size * 1200
        sites = mod._list_region_sites([], index, 1250)
        assert sites == []
        new_count = region.new_start + spec.elem_size * 1250
        assert new_count == region.new_end - spec.count_bytes
        assert new_count != old_count + (region.new_start - spec.base)


def test_fixup_inventory_matches_decoded_original(original: bytes) -> None:
    # W19 (lap439/440): unit_pool was 1014 (986 disp + 28 imm) before the
    # imm-scanner repair. 25 of those 28 imm "sites" were never pool
    # addresses at all (root cause of the P2 tick-11,928 fault) -- only 3
    # (the genuine `mov reg, pool_base` loads) survive
    # IMM_SITE_CLASSIFICATION, so the true count is 986 + 3 = 989.
    sites = mod.collect_fixup_sites(original, 1250)
    assert {name: len(items) for name, items in sites.items()} == {
        "unit_pool": 989,
        "unit_existence": 34,
        "unit_age": 4,
        "category_slot_list_a": 24,
        "category_slot_list_b": 10,
        "active_slot_list": 262,
    }


def test_bulk_relative_category_removal_aliases_are_explicit(original: bytes) -> None:
    sites = mod.collect_fixup_sites(original, 1250)
    result = full_layout.layout(1250)
    for index, inventory in (
        (3, mod.CATEGORY_A_BULK_SITES),
        (4, mod.CATEGORY_B_BULK_SITES),
    ):
        aliases = [site for site in sites[full_layout.REGIONS[index].name]
                   if site.va in inventory]
        assert {site.va for site in aliases} == set(inventory)
        region = result.regions[index]
        expected = {
            "base": region.new_start - mod.CATEGORY_BULK_BASE,
            "last": region.new_start - 4 - mod.CATEGORY_BULK_BASE,
            "count": region.new_start + region.array_new_span - mod.CATEGORY_BULK_BASE,
            "self_count": region.new_start + region.array_new_span - mod.CATEGORY_BULK_BASE,
        }
        assert all(site.new_value == expected[inventory[site.va]] for site in aliases)


def test_category_b_removal_uses_its_own_count_for_guard_and_last_index(
    original: bytes,
) -> None:
    sites = mod.collect_fixup_sites(original, 1250)["category_slot_list_b"]
    guard = next(site for site in sites if site.va == 0x004A3692)
    category_b = full_layout.layout(1250).regions[4]
    assert guard.old_value == 0x0089C2C8 - mod.CATEGORY_BULK_BASE
    assert guard.new_value == (
        category_b.new_start + category_b.array_new_span - mod.CATEGORY_BULK_BASE
    )


def test_active_last_element_aliases_are_explicit_and_scalar_predecessor_is_untouched(
    original: bytes,
) -> None:
    sites = mod.collect_fixup_sites(original, 1250)["active_slot_list"]
    aliases = [site for site in sites if site.va in mod.ACTIVE_LAST_ELEMENT_ALIAS_SITES]
    active = full_layout.layout(1250).regions[5]
    assert {site.va for site in aliases} == set(mod.ACTIVE_LAST_ELEMENT_ALIAS_SITES)
    assert all(site.old_value == 0x00974FA6 for site in aliases)
    assert all(site.new_value == active.new_start - 2 for site in aliases)

    candidate, _report = mod.build_candidate(original, 1250)
    for va in (0x0043F7E8, 0x0043F802):
        offset = va - mod.IMAGE_BASE
        assert candidate[offset : offset + 10] == original[offset : offset + 10]


def test_n1250_candidate_patches_every_inventory_site(original: bytes) -> None:
    _candidate, report = mod.build_candidate(original, 1250)
    assert report["applied_fixup_counts"] == report["fixup_site_counts"]


def test_n1250_data_section_covers_every_relocated_region(original: bytes) -> None:
    candidate, _report = mod.build_candidate(original, 1250)
    result = full_layout.layout(1250)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        data = next(section for section in pe.sections if section.Name.rstrip(b"\0") == b".data")
        start = mod.IMAGE_BASE + int(data.VirtualAddress)
        end = start + int(data.Misc_VirtualSize)
        for region in result.regions:
            assert start <= region.new_start < region.new_end <= end
    finally:
        pe.close()


def _section_intervals(data: bytes) -> list[tuple[str, int, int]]:
    pe = pefile.PE(data=data, fast_load=True)
    try:
        return [
            (
                section.Name.rstrip(b"\0").decode("ascii", "replace"),
                mod.IMAGE_BASE + int(section.VirtualAddress),
                mod.IMAGE_BASE + int(section.VirtualAddress) + int(section.Misc_VirtualSize),
            )
            for section in pe.sections
        ]
    finally:
        pe.close()


def _uncovered_bytes(intervals: list[tuple[str, int, int]], start: int, end: int) -> int:
    covered = 0
    cursor = start
    for _name, low, high in sorted(intervals, key=lambda item: item[1]):
        low = max(low, cursor)
        high = min(high, end)
        if high > low:
            covered += high - low
            cursor = high
    return (end - start) - covered


def _assert_relocated_block_covered_by_sections(candidate: bytes, capacity: int) -> None:
    result = full_layout.layout(capacity)
    intervals = _section_intervals(candidate)
    block_start = result.regions[0].new_start
    block_end = result.regions[-1].new_end
    uncovered = _uncovered_bytes(intervals, block_start, block_end)
    assert uncovered == 0, (
        f"{uncovered} relocated bytes in [0x{block_start:08x}, 0x{block_end:08x}) "
        "are outside every section"
    )


def test_n4001_data_section_covers_every_relocated_region(original: bytes) -> None:
    candidate, _report = product_mod.build_candidate(original, 4001)
    _assert_relocated_block_covered_by_sections(candidate, 4001)


def test_n4001_persistence_candidate_data_section_covers_every_relocated_region(
    original: bytes,
) -> None:
    candidate, _report = persistence_mod.build_candidate(original, 4001)
    _assert_relocated_block_covered_by_sections(candidate, 4001)


def test_n4001_persistence_compat_candidate_data_section_covers_every_relocated_region(
    original: bytes,
) -> None:
    candidate, _report = persistence_compat_mod.build_candidate(original, 4001)
    _assert_relocated_block_covered_by_sections(candidate, 4001)


def test_rejects_wrong_source() -> None:
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        mod.build_candidate(b"not the original", 1250)


def test_n1250_supply5000_combined_hash_is_pinned(original: bytes) -> None:
    # SHA changed under W19 (lap439/440): 25 fewer (bogus) imm relocations
    # are applied to unit_pool now that the false-positive imm sites are
    # rejected -- see test_fixup_inventory_matches_decoded_original.
    candidate, report = combined_mod.build_candidate(original, 1250)
    assert report["sha256"] == "3cc91ef82fb660a6113a6307779ae98bfd7284e3eae804f19e841c1819453977"
    assert len(candidate) == len(original)


def test_n4001_product_capacity_candidate_is_structurally_pinned(original: bytes) -> None:
    # SHA and unit_pool count changed under W19 (lap439/440): see
    # test_fixup_inventory_matches_decoded_original.
    candidate, report = product_mod.build_candidate(original, 4001)
    assert report["sha256"] == "d13189bb9839b6cc9818624df792e1f465b820448c3f09b7ebc1e5b81f3c26c5"
    assert candidate[
        OWNER_COUNT_FILE_OFFSET : OWNER_COUNT_FILE_OFFSET + len(OWNER_COUNT_AFTER)
    ] == OWNER_COUNT_AFTER
    assert report["capacity_supply_report"]["capacity_report"]["applied_fixup_counts"] == {
        "unit_pool": 989,
        "unit_existence": 34,
        "unit_age": 4,
        "category_slot_list_a": 24,
        "category_slot_list_b": 10,
        "active_slot_list": 262,
    }
