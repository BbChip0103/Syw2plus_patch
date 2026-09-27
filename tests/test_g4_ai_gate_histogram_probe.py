"""Regression contract for the G4 AI production gate rejection classifier
(``tools/g4_ai_gate_histogram_probe.py``), STATUS 2026-09-27 13:45 방향
("owner별 거부 사유 히스토그램"). ``classify_candidate`` is pure -- it takes
already-read table values and returns the reject reason (or
``WOULD_ACCEPT``) -- so every gate in the ``FUN_00406C70`` ->
``FUN_0043E7F0`` -> ``FUN_00406B00`` crowd-check chain is pinned here
without needing a live game process.
"""

from __future__ import annotations

from tools import g4_ai_gate_histogram_probe as gh

BASE_RECORD = {
    "nation_mask": 0x000F, "building_type": 58, "produce_kind": 5,
    "research_kind": -1, "prereq_count_kind": -1, "prereq_count_min": -1,
    "prereq_own_kind_a": -1, "prereq_own_kind_b": -1, "tech_kind": -1,
}
BASE_TYPE_SPEC = {"flags": 0, "ratio_cap": 100, "typemax": 999}
BASE_SCENARIO = {"avail_flag": 1, "scenario_typemax": None}


def _dynamic(*, total_units=100, count=0, prereq_count_current=0,
             prereq_owned=0, tech_researched=0, hero_cooldown=0, hero_count=0):
    per_kind = {
        "count": count, "prereq_count_current": prereq_count_current,
        "prereq_owned": prereq_owned, "tech_researched": tech_researched,
        "hero_cooldown": hero_cooldown,
    }
    return {"total_units": total_units, "hero_count": hero_count, "per_kind": {5: per_kind}}


def _classify(**overrides):
    record = {**BASE_RECORD, **overrides.pop("record", {})}
    type_spec = {**BASE_TYPE_SPEC, **overrides.pop("type_spec", {})}
    scenario = {**BASE_SCENARIO, **overrides.pop("scenario", {})}
    dynamic = overrides.pop("dynamic", _dynamic())
    return gh.classify_candidate(
        record=record, owner_nation=overrides.pop("owner_nation", 1),
        dynamic=dynamic, scenario=scenario, type_spec=type_spec,
        tech_def_exists=overrides.pop("tech_def_exists", False),
        crowd_count=overrides.pop("crowd_count", None),
    )


def test_accepts_when_every_gate_passes() -> None:
    assert _classify() == "WOULD_ACCEPT"


def test_nation_mismatch_when_mask_excludes_owner_nation() -> None:
    assert _classify(record={"nation_mask": 0x0002}, owner_nation=1) == "NATION_MISMATCH"


def test_out_of_range_nation_defaults_to_bit0_per_fun_00406c70() -> None:
    # 0x00406d5a's `ja` sends any bl-1 > 3 to the edx=1 default case.
    assert _classify(record={"nation_mask": 0x0001}, owner_nation=9) == "WOULD_ACCEPT"
    assert _classify(record={"nation_mask": 0x0002}, owner_nation=9) == "NATION_MISMATCH"


def test_prereq_count_gate_rejects_below_minimum() -> None:
    record = {**BASE_RECORD, "prereq_count_kind": 5, "prereq_count_min": 3}
    dynamic = _dynamic(prereq_count_current=2)
    assert _classify(record=record, dynamic=dynamic) == "PREREQ_COUNT"


def test_prereq_own_gate_rejects_when_not_owned() -> None:
    record = {**BASE_RECORD, "prereq_own_kind_a": 5}
    dynamic = _dynamic(prereq_owned=0)
    assert _classify(record=record, dynamic=dynamic) == "PREREQ_OWN"

    record_b = {**BASE_RECORD, "prereq_own_kind_b": 5}
    assert _classify(record=record_b, dynamic=dynamic) == "PREREQ_OWN"


def test_tech_gate_only_applies_when_definition_exists() -> None:
    record = {**BASE_RECORD, "tech_kind": 5}
    dynamic = _dynamic(tech_researched=0)
    assert _classify(record=record, dynamic=dynamic, tech_def_exists=True) == "TECH_NOT_RESEARCHED"
    # Same unresearched state, but no tech-definition row: treated as satisfied.
    assert _classify(record=record, dynamic=dynamic, tech_def_exists=False) == "WOULD_ACCEPT"


def test_hero_gates_only_apply_when_flag_bit_set() -> None:
    dynamic = _dynamic(hero_cooldown=5, hero_count=5)
    assert _classify(dynamic=dynamic) == "WOULD_ACCEPT"  # no FLAG_HERO -> hero fields ignored
    assert _classify(type_spec={"flags": gh.FLAG_HERO}, dynamic=dynamic) == "HERO_COOLDOWN"
    assert _classify(
        type_spec={"flags": gh.FLAG_HERO}, dynamic=_dynamic(hero_cooldown=0, hero_count=5),
    ) == "HERO_CAP"


def test_avail_flag_zero_rejects_before_typemax_or_ratio() -> None:
    assert _classify(scenario={"avail_flag": 0}) == "H_AVAIL"


def test_typemax_gate_uses_scenario_override_when_present() -> None:
    dynamic = _dynamic(count=10)
    assert _classify(type_spec={"typemax": 20}, dynamic=dynamic) == "WOULD_ACCEPT"
    assert _classify(type_spec={"typemax": 5}, dynamic=dynamic) == "H_TYPEMAX"
    # Scenario override (0x00B3DE70) wins over the static type-spec typemax when the
    # 0x009E1DD8 switch selected it (scenario_typemax is not None).
    assert _classify(
        type_spec={"typemax": 20}, scenario={"avail_flag": 1, "scenario_typemax": 5}, dynamic=dynamic,
    ) == "H_TYPEMAX"


def test_ratio_gate_rejects_over_cap_percentage() -> None:
    dynamic = _dynamic(total_units=100, count=31)
    assert _classify(type_spec={"ratio_cap": 30}, dynamic=dynamic) == "H_RATIO"
    assert _classify(type_spec={"ratio_cap": 31}, dynamic=dynamic) == "WOULD_ACCEPT"


def test_ratio_gate_skipped_when_owner_has_zero_total_units() -> None:
    dynamic = _dynamic(total_units=0, count=0)
    assert _classify(type_spec={"ratio_cap": 0}, dynamic=dynamic) == "WOULD_ACCEPT"


def test_crowd_gate_only_applies_with_crowd_flag_and_known_count() -> None:
    assert _classify(type_spec={"flags": gh.FLAG_CROWD_A}, crowd_count=7) == "H_CROWD"
    assert _classify(type_spec={"flags": gh.FLAG_CROWD_A}, crowd_count=6) == "WOULD_ACCEPT"
    # Flag bit unset: crowding never checked even if the count would exceed the threshold.
    assert _classify(type_spec={"flags": 0}, crowd_count=99) == "WOULD_ACCEPT"


def test_address_constants_match_the_lap501_memory_map() -> None:
    assert gh.PLAYER_BASE == 0x00956770
    assert gh.PLAYER_STRIDE == 0x3ABC
    assert gh.PLAYER_TOTAL_UNITS_OFF == 0x200A
    assert gh.TYPE_SPEC_BASE == 0x009B5228
    assert gh.TYPE_SPEC_STRIDE == 0x394
    assert gh.COUNT_TABLE == 0x0089A388
    assert gh.OVERRIDE_SWITCH == 0x009E1DD8
    assert gh.SCENARIO_TYPEMAX_TABLE == 0x00B3DE70
    assert gh.AVAIL_FLAG_TABLE == 0x00B3E000
    assert (gh.PLAYER_BASE + gh.PLAYER_PREREQ_COUNT_TABLE_OFF) == 0x00956F60
    assert (gh.PLAYER_BASE + gh.PLAYER_PREREQ_OWN_TABLE_OFF) == 0x009598CC
    assert (gh.PLAYER_BASE + gh.PLAYER_TECH_RESEARCHED_TABLE_OFF) == 0x00959A8C
    assert gh.TECH_DEF_TABLE == 0x009E2F38
    assert (gh.UNIT_POOL_CAPACITY, gh.UNIT_POOL_BASE, gh.UNIT_EXISTS_BASE) == (1200, 0x0066B790, 0x008990C8)
