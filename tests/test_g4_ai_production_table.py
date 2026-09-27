"""Regression contract for the AI production/research table decode
(``tools/g4_ai_production_table.py``), which extends
``analysis/memory_maps/ai_production_decision_path_00406770_20260923.md``
(lap501) with the ``FUN_00406C70`` per-record field layout that document
left undecoded. Pins the counts lap501 already established independently
(143 total / 65 production / 78 research / 27 building types) against a
fresh decode of the same protected original bytes, plus the new field
layout this lap derived from ``FUN_00406C70``'s disassembly.
"""

from __future__ import annotations

import struct

from tools import g4_ai_production_table as prod_table
from tools import runtime_env


def test_decodes_the_real_table_with_lap501s_known_counts() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    records = prod_table.load_production_table(executable)
    assert len(records) == 143

    production = [r for r in records if r["produce_kind"] != -1]
    research = [r for r in records if r["research_kind"] != -1]
    assert len(production) == 65
    assert len(research) == 78
    assert len(production) + len(research) == len(records)

    building_types = prod_table.building_types(production)
    assert len(building_types) == 27
    assert all(r["nation_mask"] == 0x000F for r in records)


def test_production_records_helper_matches_manual_filter() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    assert prod_table.production_records(executable) == [
        r for r in prod_table.load_production_table(executable) if r["produce_kind"] != -1
    ]


def test_records_for_building_type_is_exact() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    records = prod_table.production_records(executable)
    building_type = records[0]["building_type"]
    matched = prod_table.records_for_building_type(records, building_type)
    assert matched
    assert all(r["building_type"] == building_type for r in matched)
    assert len(matched) == sum(1 for r in records if r["building_type"] == building_type)


def _make_record(*, nation_mask=0x000F, building_type=1, produce_kind=5, research_kind=-1,
                  prereq_count_kind=-1, prereq_count_min=-1, prereq_own_kind_a=-1,
                  prereq_own_kind_b=-1, tech_kind=-1) -> bytes:
    return struct.pack(
        "<hhhhhhhhh", nation_mask, building_type, produce_kind, research_kind,
        prereq_count_kind, prereq_count_min, prereq_own_kind_a, prereq_own_kind_b, tech_kind,
    )


def test_decode_record_reads_every_field_in_declared_order() -> None:
    blob = _make_record(
        nation_mask=0x0003, building_type=41, produce_kind=7, research_kind=-1,
        prereq_count_kind=2, prereq_count_min=3, prereq_own_kind_a=9,
        prereq_own_kind_b=10, tech_kind=11,
    )
    record = prod_table._decode_record(blob, 0, index=0)
    assert record == {
        "index": 0, "nation_mask": 0x0003, "building_type": 41, "produce_kind": 7,
        "research_kind": -1, "prereq_count_kind": 2, "prereq_count_min": 3,
        "prereq_own_kind_a": 9, "prereq_own_kind_b": 10, "tech_kind": 11,
    }


def test_decode_record_returns_none_at_terminator_sentinel() -> None:
    blob = _make_record(nation_mask=prod_table.TERMINATOR_NATION_MASK)
    assert prod_table._decode_record(blob, 0, index=0) is None
