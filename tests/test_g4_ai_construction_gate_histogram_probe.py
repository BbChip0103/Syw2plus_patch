"""Regression contract for the G4 AI construction gate rejection classifier
(``tools/g4_ai_construction_gate_histogram_probe.py``), STATUS 2026-09-27
14:45 운영자 방향 v2 step ①: "AI 건설 결정 루틴... 건설 거부 사유
히스토그램을 owner별 raw 수집". ``classify_candidate``/``type_cap``/
``owner_building_counts`` are pure -- they take already-read table/roster
values and return the reject reason (or counts) -- so every gate in the
fresh ``FUN_0043DBB0`` -> ``FUN_0043DB00`` chain this lap disassembled is
pinned here without needing a live game process.
"""

from __future__ import annotations

from tools import g4_ai_construction_gate_histogram_probe as ch

BASE_RECORD = {
    "building_type": 60, "prereq_building_type": 58, "nation_kind": 75,
    "prereq_own_kind": 0, "cost": 30,
}
ALL_FACTIONS_ON = {7: True, 21: True, 70: True, 75: True}
ALL_FACTIONS_OFF = {7: False, 21: False, 70: False, 75: False}
BASE_STATIC = {"ai_flag": 0, "total_buildings": 0, "build_cap_denom": 0}
BASE_TYPE_SPEC = {"avail": True, "typemax": 999}


def _classify(**overrides):
    record = {**BASE_RECORD, **overrides.pop("record", {})}
    faction_flags = overrides.pop("faction_flags", ALL_FACTIONS_ON)
    static = {**BASE_STATIC, **overrides.pop("static", {})}
    type_spec = {**BASE_TYPE_SPEC, **overrides.pop("type_spec", {})}
    return ch.classify_candidate(
        record=record, faction_flags=faction_flags, static=static,
        override_switch=overrides.pop("override_switch", 0), type_spec=type_spec,
        prereq_building_owned=overrides.pop("prereq_building_owned", True),
        prereq_own_owned=overrides.pop("prereq_own_owned", True),
        current_count=overrides.pop("current_count", 0),
        total_n=overrides.pop("total_n", 0),
    )


def test_accepts_when_every_gate_passes() -> None:
    assert _classify() == "WOULD_BUILD"


def test_faction_block_when_nation_flag_is_false() -> None:
    assert _classify(faction_flags=ALL_FACTIONS_OFF) == "FACTION_BLOCK"
    # a nation_kind the live faction-flag dict has no entry for at all
    # (e.g. this lap's finding: a modded worker kind the jump table's
    # default/no-op case never sets any flag for) is also blocked.
    assert _classify(faction_flags={}) == "FACTION_BLOCK"


def test_scenario_unavail_rejects_before_prereqs() -> None:
    assert _classify(type_spec={"avail": False, "typemax": 999}, prereq_building_owned=False) == "SCENARIO_UNAVAIL"


def test_build_count_cap_only_applies_when_ai_and_no_override() -> None:
    static = {"ai_flag": 1, "total_buildings": 10, "build_cap_denom": 50}  # cap = 50//5 = 10
    assert _classify(static=static) == "BUILD_COUNT_CAP"
    # not ai: cap not enforced
    assert _classify(static={**static, "ai_flag": 0}) == "WOULD_BUILD"
    # override switch set: cap not enforced
    assert _classify(static=static, override_switch=1) == "WOULD_BUILD"


def test_prereq_building_gate_rejects_when_not_owned() -> None:
    assert _classify(prereq_building_owned=False) == "PREREQ_BUILDING"
    # prereq_building_type == 0 means "no prerequisite" regardless of the flag
    assert _classify(record={"prereq_building_type": 0}, prereq_building_owned=False) == "WOULD_BUILD"


def test_prereq_own_gate_rejects_when_not_owned() -> None:
    record = {**BASE_RECORD, "prereq_own_kind": 45}
    assert _classify(record=record, prereq_own_owned=False) == "PREREQ_OWN"
    assert _classify(record=record, prereq_own_owned=True) == "WOULD_BUILD"


def test_type_cap_gate_rejects_at_or_above_cap() -> None:
    # type_cap(typemax=12, total_n=6) = floor(12*6/6)=12; 12%12==0 -> no add -> cap=12
    assert ch.type_cap(typemax=12, total_n=6) == 12
    assert _classify(type_spec={"avail": True, "typemax": 12}, total_n=6, current_count=12) == "TYPE_CAP"
    assert _classify(type_spec={"avail": True, "typemax": 12}, total_n=6, current_count=11) == "WOULD_BUILD"


def test_type_cap_adds_typemax_when_quotient_not_divisible_by_12() -> None:
    # typemax=10, N=1 -> quotient = floor(10/6) = 1; 1%12 != 0 -> cap = 1+10 = 11
    assert ch.type_cap(typemax=10, total_n=1) == 11


def test_type_cap_falls_back_to_typemax_when_total_n_is_zero() -> None:
    assert ch.type_cap(typemax=7, total_n=0) == 7


def test_owner_building_counts_counts_completed_and_under_construction() -> None:
    units = [
        {"owner": 0, "type": 58, "complete": True, "order_state": 0, "under_construction_kind": -1},
        {"owner": 0, "type": 60, "complete": False, "order_state": 0xC, "under_construction_kind": 60},
        {"owner": 0, "type": 5, "complete": False, "order_state": 1, "under_construction_kind": -1},
        {"owner": 1, "type": 58, "complete": True, "order_state": 0, "under_construction_kind": -1},
    ]
    counts, total = ch.owner_building_counts(units, owner=0)
    assert counts == {58: 1, 60: 1}
    assert total == 2


def test_nation_kind_flag_offsets_match_this_laps_jump_table_extraction() -> None:
    assert ch.PLAYER_FACTION_FLAG_OFF == {7: 0x314C, 21: 0x3154, 70: 0x3158, 75: 0x3150}


def test_address_constants_match_lap515_and_this_laps_fresh_disassembly() -> None:
    assert ch.PLAYER_BASE == 0x00956770
    assert ch.PLAYER_STRIDE == 0x3ABC
    assert ch.PLAYER_AI_OFF == 0x002
    assert ch.PLAYER_TOTAL_BUILDINGS_OFF == 0x200E
    assert ch.PLAYER_BUILD_CAP_DENOM_OFF == 0x2010
    assert ch.PLAYER_PREREQ_BUILDING_TABLE_OFF == 0x2FB8
    assert ch.PLAYER_PREREQ_OWN_TABLE_OFF == 0x315C
    assert ch.TYPE_SPEC_BASE == 0x009B5228
    assert ch.TYPE_SPEC_STRIDE == 0x394
    assert ch.TYPE_SPEC_BUILD_AVAIL_OFF == 0x4C
    assert ch.OVERRIDE_SWITCH == 0x009E1DD8
    assert (ch.UNIT_POOL_CAPACITY, ch.UNIT_POOL_BASE, ch.UNIT_EXISTS_BASE) == (1200, 0x0066B790, 0x008990C8)
