"""Targeted checks for the read-only G2 unit-pool xref inventory."""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.g2_unit_pool_xrefs import ORIGINAL_SHA256, inventory


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_CANDIDATES = (
    ROOT.parent / "Syw2plus_re" / "Syw2plus" / "syw2plus_original.exe",
    ROOT / "Syw2plus" / "syw2plus_original.exe",
)


def _original() -> Path:
    for candidate in ORIGINAL_CANDIDATES:
        if candidate.is_file():
            return candidate
    pytest.skip("local original executable is unavailable")


def test_inventory_is_sha_pinned_and_geometry_is_not_an_activation_claim():
    report = inventory(_original())

    assert report["status"] == "PASS"
    assert report["source"]["sha256"] == ORIGINAL_SHA256
    assert report["source"]["pe32"] is True
    assert report["pool_geometry"]["geometry_check"] is True
    assert report["pool_geometry"]["end_bulk_start"] == "0x00892410"
    assert int(report["pool_geometry"]["unit_age_end"], 16) - int(
        report["pool_geometry"]["unit_age_base"], 16
    ) == 1200 * 2
    assert int(report["pool_geometry"]["active_slot_list_end"], 16) - int(
        report["pool_geometry"]["active_slot_list_base"], 16
    ) == 1200 * 2
    assert int(report["pool_geometry"]["category_slot_list_a_end"], 16) - int(
        report["pool_geometry"]["category_slot_list_a_base"], 16
    ) == 1200 * 4
    assert int(report["pool_geometry"]["category_slot_list_b_end"], 16) - int(
        report["pool_geometry"]["category_slot_list_b_base"], 16
    ) == 1200 * 4
    assert report["coverage"] == "INCOMPLETE"
    assert report["activation"]["status"] == "NO-GO"


def test_known_calls_and_endpoints_are_decoded_operands_not_raw_patterns():
    report = inventory(_original())
    functions = report["functions"]

    expected_sites = {
        "allocator": "0x0041f159",
        "destruction": "0x00407101",
        "spawn": "0x0040712c",
        "save_roster": "0x00440f35",
        "load_roster": "0x00441305",
    }
    for name, site in expected_sites.items():
        sites = {item["instruction"] for item in functions[name]["direct_call_xrefs"]}
        assert site in sites
        assert all(item["evidence"] == "decoded_capstone_operand"
                   for item in functions[name]["direct_call_xrefs"])

    endpoints = report["endpoints"]
    assert endpoints["unit_pool_base"]["decoded_xrefs"]
    assert endpoints["unit_existence_base"]["decoded_xrefs"]
    assert endpoints["unit_existence_end"]["decoded_xrefs"]
    assert report["evidence_policy"]["raw_pattern_scan"] is False
    assert report["evidence_policy"]["accepted_xref_evidence"] == (
        "decoded instruction operand only"
    )
    assert report["evidence_policy"]["unbounded_byte_patterns"] == (
        "not counted as xrefs"
    )
    assert report["xref_counts"]["direct_call_targets"] == {
        "destruction": 13,
        "spawn": 29,
        "allocator": 18,
        "save_roster": 1,
        "load_roster": 1,
    }
    assert report["xref_counts"]["decoded_endpoint_operands"] == {
        "unit_pool_bulk_start": 179,
        "unit_existence_base": 34,
        "unit_pool_base": 115,
        "unit_existence_end": 4,
        "allocator_sidecar_end": 6,
        "allocator_sidecar_start": 1,
    }


def test_region_records_are_in_range_decoded_operands_and_not_activation_evidence():
    report = inventory(_original())

    expected_ranges = {
        "unit_pool": (0x0066B790, 0x00892410),
        "unit_existence": (0x008990C8, 0x00899A28),
        "unit_age": (0x00899A28, 0x0089A388),
        "active_slot_list": (0x00974FA8, 0x00975908),
        "category_slot_list_a": (0x0089B008, 0x0089C2C8),
        "category_slot_list_b": (0x0089C2CA, 0x0089D58A),
    }
    for name, (start, end) in expected_ranges.items():
        region = report["regions"][name]
        assert int(region["start"], 16) == start
        assert int(region["end"], 16) == end
        # Only an absolute memory operand proves a direct region reference.
        for record in region["decoded_xrefs"]:
            value = int(record["value"], 16)
            assert start <= value < end
            assert record["evidence"] == "decoded_capstone_operand"
            assert record["operand_type"] == "absolute_memory"
            assert isinstance(record["operand_index"], int)
            assert record["operand_index"] >= 0
            assert record["kind"] == "memory_absolute"

        # In-range immediates are useful candidates, but their semantic role
        # is unresolved and they are not direct region references.
        for record in region["immediate_operand_candidates"]:
            value = int(record["value"], 16)
            assert start <= value < end
            assert record["evidence"] == "decoded_capstone_operand"
            assert record["operand_type"] == "immediate"
            assert isinstance(record["operand_index"], int)
            assert record["kind"] == "immediate_operand"

        # Base/index displacements are separate relocation candidates because
        # the runtime effective address cannot be resolved statically.
        for record in region["base_index_displacement_candidates"]:
            value = int(record["value"], 16)
            assert start <= value < end
            assert record["evidence"] == "decoded_capstone_operand"
            assert record["operand_type"] == "base_index_memory"
            assert record["addressing"] == "base/index-dependent"
            assert record["effective_address"] == "runtime effective address unresolved"
            assert record["kind"] == "memory_base_index_displacement_candidate"

    assert report["xref_counts"]["absolute_memory_operands"] == {
        "unit_pool": 0,
        "unit_existence": 0,
        "unit_age": 0,
        "active_slot_list": 0,
        "category_slot_list_a": 0,
        "category_slot_list_b": 0,
    }
    assert report["xref_counts"]["immediate_operand_candidates"] == {
        "unit_pool": 30,
        "unit_existence": 2,
        "unit_age": 3,
        "active_slot_list": 72,
        "category_slot_list_a": 0,
        "category_slot_list_b": 0,
    }
    assert report["xref_counts"]["base_index_displacement_candidates"] == {
        "unit_pool": 986,
        "unit_existence": 32,
        "unit_age": 2,
        "active_slot_list": 17,
        "category_slot_list_a": 6,
        "category_slot_list_b": 1,
    }

    assert report["evidence_policy"]["region_reference_scope"] == (
        "decoded absolute memory operands are direct region references; "
        "immediates and base/index-dependent memory operands are candidates only"
    )
    assert report["evidence_policy"]["immediate_operand_scope"] == (
        "in-range relocation candidates; semantic role unresolved"
    )
    assert report["evidence_policy"]["base_index_displacement_scope"] == (
        "in-range relocation candidates; runtime effective address unresolved"
    )
    assert report["evidence_policy"]["overlapping_endpoint_semantics"] == (
        "unit_age starts at unit_existence_end (0x00899a28); "
        "allocator_sidecar_start (0x00899a2a) remains a historical endpoint"
    )
    assert report["activation"]["status"] == "NO-GO"
