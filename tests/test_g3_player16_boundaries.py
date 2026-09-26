"""Focused static checks for the G3 16-player feasibility boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.g3_player16_boundaries import ORIGINAL_SHA256, inventory


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "Syw2plus" / "syw2plus_original.exe"


def _report() -> dict:
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")
    return inventory(ORIGINAL)


def test_player_geometry_bulk_excess_and_no_go():
    report = _report()
    player = report["player_struct"]
    assert report["source"]["sha256"] == ORIGINAL_SHA256
    assert player["base"] == "0x00956770"
    assert int(player["target_end"], 16) - int(player["original_end"], 16) == 0x3ABC * 8
    assert player["original_count"] == 8
    assert player["target_count"] == 16
    assert player["target_geometry_check"] is True
    bulk = report["bulk_save"]
    assert bulk["start"] == "0x00892410"
    assert bulk["end"] == "0x00975d8c"
    assert bulk["target_excess_bytes"] == 112036
    assert bulk["target_excess_hex"] == "0x0001b5a4"
    assert bulk["arithmetic_check"] is True
    assert report["activation"]["status"] == "NO-GO"
    assert "not declared impossible" in report["activation"]["reason"]


def test_mask_function_bytes_and_static_field_policy():
    report = _report()
    instructions = {item["instruction"]: item for item in report["mask_evidence"]["instructions"]}
    assert instructions["0x0043ebc2"]["bytes"] == "b2 01"
    assert instructions["0x0043ebd2"]["bytes"] == "d2 e2"
    assert instructions["0x0043ebdb"]["bytes"] == "88 50 03"
    assert instructions["0x0043ebc9"]["bytes"] == "88 48 01"
    assert instructions["0x0043ebcc"]["bytes"] == "88 48 05"
    assert report["mask_evidence"]["owner_mask"]["offset"] == 3
    assert report["mask_evidence"]["owner_mask"]["width"] == "byte"
    assert "8..15" in report["mask_evidence"]["owner_mask"]["implication"]
    assert report["mask_evidence"]["player_index_storage"] == {
        "offsets": [1, 5],
        "width": "byte",
        "basis": "decoded mov byte ptr [eax+1],cl and [eax+5],cl",
    }
    assert report["mask_evidence"]["opponent_mask"] == {
        "offset": 4,
        "width": "byte",
        "semantics": "OR of 1<<other.player_num for different-team players",
        "basis": "existing static field evidence; no new runtime execution",
    }


def test_boundary_candidates_are_decoded_and_common_eight_is_noise():
    report = _report()
    expected_counts = {
        "player_struct_base": 191,
        "player_struct_stride": 30,
        "player_struct_original_end": 8,
        "player_struct_target_end": 0,
    }
    counts = {
        name: len(records)
        for name, records in report["boundary_operand_candidates"].items()
    }
    assert counts == expected_counts
    for name, records in report["boundary_operand_candidates"].items():
        expected = int(report["player_struct"][{
            "player_struct_base": "base",
            "player_struct_stride": "stride",
            "player_struct_original_end": "original_end",
            "player_struct_target_end": "target_end",
        }[name]], 16)
        for record in records:
            assert int(record["value"], 16) == expected
            assert record["evidence"] == "decoded_capstone_operand"
            assert record["semantic_status"] == "UNRESOLVED"
            assert record["bytes"]
            assert record["instruction"].startswith("0x")
            assert record["operands"]
    assert len(report["immediate_loop_bound_8_candidates"]) == 2795
    assert report["candidate_policy"]["immediate_loop_bound_8"].startswith(
        "common-number noise"
    )
    assert report["candidate_policy"]["boundary_operands"] == (
        "decoded operands only; semantic use unresolved"
    )


def test_unresolved_obligations_and_no_runtime_claims():
    report = _report()
    assert report["unresolved"] == {
        "table_relocation": "UNRESOLVED",
        "mask_widening_all_consumers": "UNRESOLVED",
        "lobby_start_positions_win_ai": "UNRESOLVED",
        "save_version": "UNRESOLVED",
        "lan_protocol": "UNRESOLVED",
    }
    assert report["candidate_policy"]["base_index_memory"] == (
        "effective address depends on runtime registers"
    )
    assert report["activation"]["status"] == "NO-GO"
