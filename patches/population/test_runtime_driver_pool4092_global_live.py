"""lap697 work -- global unit enumeration for the G2 pool4092 6-region candidate.

STATUS/INBOX 2026-09-27 01:05 지시: `runtime_driver.state(..., detailed=True)`
defaulted to `profile="original"` (STOCK_POOL, capacity 1200 @ the stock
addresses) even when reading the relocated `g2_supply10000_pool4092_owner500`
candidate, so the unit_existence bitmap read stale/zeroed memory at the old
stock addresses and `global_live_count` always returned 0. This pins:

1. The registered `POOL_PROFILE_LAYOUTS`/`FULL_REGION_PROFILES` addresses for
   that profile against the pure-geometry `full_tail_relocation_storage_layout_v1.
   layout(4093)` computation (no live process required).
2. `state(pid, detailed=True, profile=...)` decodes the active_slot_list
   region (count + entries) and flags duplicates / bitmap mismatches, using a
   fake `read()` (no Wine/game process required).
"""

from __future__ import annotations

import struct

import pytest

from patches.population import runtime_driver as mod
from patches.population.full_tail_relocation_storage_layout_v1 import layout

PROFILE = "g2_supply10000_pool4092_owner500"
CAPACITY = 4093


def test_pool_profile_layout_matches_pure_geometry() -> None:
    capacity, unit_base, exists_base = mod.POOL_PROFILE_LAYOUTS[PROFILE]
    regions = {r.name: r for r in layout(CAPACITY).regions}
    assert capacity == CAPACITY
    assert unit_base == regions["unit_pool"].new_start
    assert exists_base == regions["unit_existence"].new_start


def test_full_region_profile_registered_for_all_six_regions() -> None:
    assert mod.FULL_REGION_PROFILES[PROFILE] == CAPACITY
    regions = {r.name: r for r in layout(CAPACITY).regions}
    assert set(regions) == {
        "unit_pool",
        "unit_existence",
        "unit_age",
        "category_slot_list_a",
        "category_slot_list_b",
        "active_slot_list",
    }


class _FakeMemory:
    """Sparse process memory: exact (address, size) overrides, zero elsewhere."""

    def __init__(self) -> None:
        self.overrides: dict[tuple[int, int], bytes] = {}

    def set(self, address: int, data: bytes) -> None:
        self.overrides[(address, len(data))] = data

    def read(self, pid: int, address: int, size: int) -> bytes:
        found = self.overrides.get((address, size))
        return found if found is not None else b"\x00" * size


def _build_memory(*, active_slots: list[int], exists_slots: set[int]) -> _FakeMemory:
    mem = _FakeMemory()
    mem.set(0x4ED818, struct.pack("<i", 9))  # ps
    mem.set(0x8924B8, struct.pack("<i", 1))  # tick
    capacity, unit_base, exists_base = mod.POOL_PROFILE_LAYOUTS[PROFILE]
    exists = [1 if slot in exists_slots else 0 for slot in range(capacity)]
    mem.set(exists_base, struct.pack(f"<{capacity}h", *exists))
    regions = {r.name: r for r in layout(CAPACITY).regions}
    active_region = regions["active_slot_list"]
    count_addr = active_region.new_start + active_region.array_new_span
    mem.set(count_addr, struct.pack("<H", len(active_slots)))
    mem.set(active_region.new_start, struct.pack(f"<{len(active_slots)}H", *active_slots))
    return mem


def test_state_detailed_reports_no_duplicates_when_lists_agree(monkeypatch: pytest.MonkeyPatch) -> None:
    mem = _build_memory(active_slots=[5, 10, 4091], exists_slots={5, 10, 4091})
    monkeypatch.setattr(mod, "read", mem.read)
    result = mod.state(pid=1234, detailed=True, profile=PROFILE)
    active = result["active_slot_list"]
    assert active["count"] == 3
    assert sorted(active["slots"]) == [5, 10, 4091]
    assert active["duplicate_count"] == 0
    assert active["matches_existence_bitmap"] is True
    assert sorted(u["slot"] for u in result["units"]) == [5, 10, 4091]


def test_state_detailed_flags_duplicate_slots(monkeypatch: pytest.MonkeyPatch) -> None:
    # A duplicate entry within an otherwise-correct set is exactly the kind of
    # pool corruption `duplicate_count` exists to catch: the set-based
    # `matches_existence_bitmap` check alone would miss it (sets collapse the
    # duplicate), which is why the probe must gate on both signals together.
    mem = _build_memory(active_slots=[5, 5, 10], exists_slots={5, 10})
    monkeypatch.setattr(mod, "read", mem.read)
    result = mod.state(pid=1234, detailed=True, profile=PROFILE)
    active = result["active_slot_list"]
    assert active["count"] == 3
    assert active["duplicate_count"] == 1
    assert active["matches_existence_bitmap"] is True


def test_state_detailed_flags_bitmap_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    mem = _build_memory(active_slots=[5, 10], exists_slots={5, 10, 4091})
    monkeypatch.setattr(mod, "read", mem.read)
    result = mod.state(pid=1234, detailed=True, profile=PROFILE)
    active = result["active_slot_list"]
    assert active["duplicate_count"] == 0
    assert active["matches_existence_bitmap"] is False


def test_state_detailed_without_full_region_profile_omits_active_slot_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mem = _build_memory(active_slots=[], exists_slots=set())
    monkeypatch.setattr(mod, "read", mem.read)
    result = mod.state(pid=1234, detailed=True, profile="original")
    assert "active_slot_list" not in result
