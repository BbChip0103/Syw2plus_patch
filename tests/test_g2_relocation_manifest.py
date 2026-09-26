"""Fail-closed tests for the read-only G2 relocation manifest."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from tools.g2_relocation_manifest import (
    ORIGINAL_SHA256,
    generate_manifest,
    validate_manifest,
)


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "Syw2plus" / "syw2plus_original.exe"


@pytest.fixture(scope="module")
def manifest() -> dict:
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")
    return generate_manifest(ORIGINAL)


def test_manifest_is_pinned_complete_and_no_go(manifest: dict):
    validate_manifest(manifest, executable=ORIGINAL)

    assert manifest["source"]["original_sha256"] == ORIGINAL_SHA256
    assert manifest["target_capacity"] == {
        "lower_bound": 4001,
        "final_capacity": None,
        "headroom": "UNRESOLVED",
    }
    assert set(manifest["regions"]) == {
        "unit_pool", "unit_existence", "unit_age", "active_slot_list",
        "category_slot_list_a", "category_slot_list_b",
    }
    assert manifest["obligations"]["candidate_site_semantics_translation"] == {
        "requirement": (
            "resolve containing function, semantic use, operand encoding, old/new expression, "
            "and count/max-index/exclusive-end meaning for every candidate"
        ),
        "status": "UNRESOLVED",
        "evidence": [],
    }
    assert manifest["aliases"]["unit_pool_end_bulk_start"]["names"] == [
        "unit_pool_end", "unit_pool_bulk_start", "live_game_state_base",
    ]
    assert manifest["aliases"]["unit_pool_end_bulk_start"]["meaning"] == (
        "same address; pool half-open end, bulk-scan start, and live game-state "
        "base (full type unresolved)"
    )
    for name, address in (
        ("category_slot_list_a_end_count", "0x0089c2c8"),
        ("category_slot_list_b_end_count", "0x0089d58a"),
    ):
        assert manifest["aliases"][name]["address"] == address
        assert "exclusive end" in manifest["aliases"][name]["meaning"]
        assert "count field" in manifest["aliases"][name]["meaning"]
    for name in ("category_slot_list_a", "category_slot_list_b"):
        assert manifest["regions"][name]["element_size"] == 4
        assert manifest["regions"][name]["element_count"] == 1200
    assert manifest["activation"]["status"] == "NO-GO"
    assert all(
        details["status"] == "UNRESOLVED"
        for details in manifest["obligations"].values()
    )


def test_manifest_preserves_operand_provenance_and_separates_candidates(manifest: dict):
    direct = manifest["direct_references"]
    candidates = manifest["candidates"]

    assert manifest["record_counts"] == {
        "direct_calls": 62,
        "endpoint_refs": 339,
        "absolute_memory_operands": 0,
        "immediate_operand_candidates": 107,
        "base_index_displacement_candidates": 1044,
    }
    for records in (
        *direct["calls"].values(),
        *direct["endpoints"].values(),
        *direct["absolute_memory_regions"].values(),
        *candidates["immediate_operands"].values(),
        *candidates["base_index_displacements"].values(),
    ):
        for record in records:
            assert record["evidence"] == "decoded_capstone_operand"
            assert record["bytes"]
            assert record["instruction"].startswith("0x")
            assert record["operands"]
            assert "containing_function" in record
            if record["containing_function"] is not None:
                assert record["function_role"]
    for records in candidates["base_index_displacements"].values():
        for record in records:
            assert record["effective_address"] == "runtime effective address unresolved"


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("obligations", "active_list"), None),
        (("aliases", "unit_pool_end_bulk_start", "address"), "0xdeadbeef"),
        (("candidates", "immediate_operands", "unit_pool"), []),
    ],
)
def test_validator_rejects_missing_or_tampered_manifest_parts(
    manifest: dict, path: tuple[str, ...], replacement: object,
):
    tampered = deepcopy(manifest)
    cursor = tampered
    for key in path[:-1]:
        cursor = cursor[key]
    if replacement is None:
        del cursor[path[-1]]
    else:
        cursor[path[-1]] = replacement
    with pytest.raises(ValueError):
        validate_manifest(tampered)


def test_validator_rejects_changed_operand_bytes(manifest: dict):
    tampered = deepcopy(manifest)
    tampered["direct_references"]["calls"]["allocator"][0]["bytes"] = "90"
    with pytest.raises(ValueError):
        validate_manifest(tampered)


def test_validator_rejects_changed_candidate(manifest: dict):
    tampered = deepcopy(manifest)
    tampered["candidates"]["immediate_operands"]["unit_pool"][0]["operands"] = "0x66b790"
    with pytest.raises(ValueError):
        validate_manifest(tampered)


def test_semantic_seed_classifies_audited_sites_and_leaves_unknown_null(manifest: dict):
    all_records = []
    for records in (
        *manifest["direct_references"]["calls"].values(),
        *manifest["direct_references"]["endpoints"].values(),
        *manifest["candidates"]["immediate_operands"].values(),
        *manifest["candidates"]["base_index_displacements"].values(),
    ):
        all_records.extend(records)
    expected_sites = {
        "0x0040f4b7": "save_units",
        "0x00442fac": "allocator",
        "0x0048bc7d": "active_add",
        "0x00440f07": "outer_save",
    }
    for instruction, function in expected_sites.items():
        matches = [record for record in all_records if record["instruction"] == instruction]
        assert matches
        assert all(record["containing_function"] == function for record in matches)
        assert all(record["function_role"] for record in matches)

    unknown = [record for record in all_records if record["containing_function"] is None]
    assert unknown
