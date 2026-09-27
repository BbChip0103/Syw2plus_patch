"""Regression contract for the AI building-construction prerequisite table
decode (``tools/g4_ai_construction_table.py``), which extends
``analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md``
(lap515) with the ``FUN_00422EB0`` record layout that document's
``FUN_0043DB00`` prerequisite reads left undecoded.
"""

from __future__ import annotations

import struct

from tools import g4_ai_construction_table as ct
from tools import runtime_env


def test_decodes_the_real_table() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    records = ct.load_construction_table(executable)
    assert len(records) == 39
    assert all(r["building_type"] != 0 for r in records)
    # Most records' nation_kind is one of the four faction-detection kinds
    # FUN_0043DBB0's jump table recognizes (see the histogram probe module).
    # One outlier (building_type 23, index 13) decodes to nation_kind=49 --
    # not one of the four; left unexplained here (not needed for the G4
    # owner0/owner1 HQ/production-building hypothesis this lap tests).
    known = {7, 21, 70, 75}
    unexplained = {r["nation_kind"] for r in records} - known
    assert unexplained == {49}, unexplained


def test_hq_records_match_this_laps_fresh_disassembly() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    records = ct.load_construction_table(executable)
    hq58 = ct.record_for_building_type(records, 58)
    assert hq58 == {
        "index": 25, "building_type": 58, "prereq_building_type": 0,
        "nation_kind": 75, "prereq_own_kind": 0, "cost": 20,
    }
    type60 = ct.record_for_building_type(records, 60)
    assert type60 == {
        "index": 27, "building_type": 60, "prereq_building_type": 58,
        "nation_kind": 75, "prereq_own_kind": 0, "cost": 30,
    }


def test_record_for_building_type_returns_none_when_absent() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    records = ct.load_construction_table(executable)
    assert ct.record_for_building_type(records, 999) is None


def test_nation_kind_to_flag_off_matches_lap515_faction_flags() -> None:
    assert ct.NATION_KIND_TO_FLAG_OFF == {7: 0x314C, 21: 0x3154, 70: 0x3158, 75: 0x3150}


def _make_record(building_type: int, prereq_building_type: int, nation_kind: int,
                  prereq_own_kind: int, cost: int) -> bytes:
    return struct.pack("<iiiii", building_type, prereq_building_type, nation_kind, prereq_own_kind, cost)


def test_decode_record_reads_every_field_in_declared_order() -> None:
    blob = _make_record(60, 58, 75, 0, 30)
    record = ct._decode_record(blob, 0, index=0)
    assert record == {
        "index": 0, "building_type": 60, "prereq_building_type": 58,
        "nation_kind": 75, "prereq_own_kind": 0, "cost": 30,
    }


def test_decode_record_returns_none_at_zero_terminator() -> None:
    blob = _make_record(0, 0, 0, 0, 0)
    assert ct._decode_record(blob, 0, index=0) is None
