#!/usr/bin/env python3
"""Build and validate a fail-closed, read-only G2 relocation manifest.

This module only serializes the existing SHA-pinned Capstone inventory.  It
does not patch or execute the game binary.  Immediate and base/index memory
records remain unresolved candidates; only absolute-memory region operands
are direct region references.  Any unresolved obligation keeps activation at
``NO-GO``.
"""

from __future__ import annotations

import argparse
import hashlib
from importlib import import_module
import json
from pathlib import Path
from typing import Any

try:
    _xref = import_module("tools.g2_unit_pool_xrefs")
except ModuleNotFoundError:  # Running this file directly from the tools directory.
    _xref = import_module("g2_unit_pool_xrefs")

ACTIVE_SLOT_LIST_BASE = _xref.ACTIVE_SLOT_LIST_BASE
ACTIVE_SLOT_LIST_END = _xref.ACTIVE_SLOT_LIST_END
CATEGORY_SLOT_LIST_A_BASE = _xref.CATEGORY_SLOT_LIST_A_BASE
CATEGORY_SLOT_LIST_A_END = _xref.CATEGORY_SLOT_LIST_A_END
CATEGORY_SLOT_LIST_B_BASE = _xref.CATEGORY_SLOT_LIST_B_BASE
CATEGORY_SLOT_LIST_B_END = _xref.CATEGORY_SLOT_LIST_B_END
ORIGINAL_SHA256 = _xref.ORIGINAL_SHA256
UNIT_AGE_BASE = _xref.UNIT_AGE_BASE
UNIT_AGE_END = _xref.UNIT_AGE_END
UNIT_EXISTS_BASE = _xref.UNIT_EXISTS_BASE
UNIT_EXISTS_END = _xref.UNIT_EXISTS_END
UNIT_POOL_BASE = _xref.UNIT_POOL_BASE
UNIT_POOL_END = _xref.UNIT_POOL_END
UNIT_SLOT_COUNT = _xref.UNIT_SLOT_COUNT
UNIT_STRIDE = _xref.UNIT_STRIDE
inventory = _xref.inventory


MANIFEST_VERSION = 1
TARGET_LOWER_BOUND = 4001
UNRESOLVED = "UNRESOLVED"

REGION_GEOMETRY: dict[str, dict[str, Any]] = {
    "unit_pool": {
        "start": f"0x{UNIT_POOL_BASE:08x}",
        "end": f"0x{UNIT_POOL_END:08x}",
        "element_size": UNIT_STRIDE,
        "element_count": UNIT_SLOT_COUNT,
    },
    "unit_existence": {
        "start": f"0x{UNIT_EXISTS_BASE:08x}",
        "end": f"0x{UNIT_EXISTS_END:08x}",
        "element_size": 2,
        "element_count": UNIT_SLOT_COUNT,
    },
    "unit_age": {
        "start": f"0x{UNIT_AGE_BASE:08x}",
        "end": f"0x{UNIT_AGE_END:08x}",
        "element_size": 2,
        "element_count": UNIT_SLOT_COUNT,
    },
    "active_slot_list": {
        "start": f"0x{ACTIVE_SLOT_LIST_BASE:08x}",
        "end": f"0x{ACTIVE_SLOT_LIST_END:08x}",
        "element_size": 2,
        "element_count": UNIT_SLOT_COUNT,
    },
    "category_slot_list_a": {
        "start": f"0x{CATEGORY_SLOT_LIST_A_BASE:08x}",
        "end": f"0x{CATEGORY_SLOT_LIST_A_END:08x}",
        "element_size": 4,
        "element_count": UNIT_SLOT_COUNT,
    },
    "category_slot_list_b": {
        "start": f"0x{CATEGORY_SLOT_LIST_B_BASE:08x}",
        "end": f"0x{CATEGORY_SLOT_LIST_B_END:08x}",
        "element_size": 4,
        "element_count": UNIT_SLOT_COUNT,
    },
}
ALIASES: dict[str, dict[str, Any]] = {
    "unit_pool_end_bulk_start": {
        "address": "0x00892410",
        "names": ["unit_pool_end", "unit_pool_bulk_start", "live_game_state_base"],
        "meaning": (
            "same address; pool half-open end, bulk-scan start, and live game-state "
            "base (full type unresolved)"
        ),
    },
    "unit_existence_end_unit_age_base": {
        "address": "0x00899a28",
        "names": ["unit_existence_end", "unit_age_base"],
        "meaning": "same address; existence half-open end and age-array base",
    },
    "category_slot_list_a_end_count": {
        "address": "0x0089c2c8",
        "names": ["category_slot_list_a_end", "category_slot_list_a_count"],
        "meaning": "same address; list-A exclusive end and live dword count field",
    },
    "category_slot_list_b_end_count": {
        "address": "0x0089d58a",
        "names": ["category_slot_list_b_end", "category_slot_list_b_count"],
        "meaning": "same address; list-B exclusive end and live dword count field",
    },
}
OBLIGATIONS: dict[str, str] = {
    "function_meaning_reachability": "prove function meaning and code reachability",
    "candidate_site_semantics_translation": (
        "resolve containing function, semantic use, operand encoding, old/new expression, "
        "and count/max-index/exclusive-end meaning for every candidate"
    ),
    "initialization_reset": "prove initialization and reset coverage for every expanded region",
    "active_list": "prove active-list capacity, insertion, removal, and bounds behavior",
    "bulk_unit_save_order_versioning": "prove bulk/unit save order and versioning compatibility",
    "lan_id_protocol_incompatible_peer_rejection": (
        "prove LAN ID/protocol compatibility and incompatible-peer rejection"
    ),
    "fixtures_stress": "pass fixtures, stress, and regression validation",
}
SEMANTIC_FUNCTIONS: dict[str, tuple[int, int, str]] = {
    "save_units": (0x0040F4B0, 0x0040F4F0, "unit roster save lifecycle"),
    "load_units": (0x0040F4F0, 0x0040F540, "unit roster load lifecycle"),
    "allocator": (0x00442FA0, 0x00442FE0, "unit allocation lifecycle"),
    "destruction": (0x00442FE0, 0x00443170, "unit destruction lifecycle"),
    "destroy_all": (0x00443170, 0x00443190, "bulk unit destruction lifecycle"),
    "active_add": (0x0048BC00, 0x0048BD10, "active-slot insertion lifecycle"),
    "outer_save": (0x00440C20, 0x00440F60, "outer save serialization lifecycle"),
    "outer_load": (0x00440FF0, 0x00441560, "outer load deserialization lifecycle"),
}

# The SHA pin makes these counts deterministic. They provide a second
# fail-closed check so deleting records and recomputing a local digest cannot
# silently turn an incomplete manifest into an apparently valid one.
EXPECTED_COUNTS = {
    "direct_calls": 62,
    "endpoint_refs": 339,
    "absolute_memory_operands": 0,
    "immediate_operand_candidates": 107,
    "base_index_displacement_candidates": 1044,
}
EXPECTED_RECORD_DIGEST = "8bb364af441ff24fcf7a04e32ffd2a49bba764c869b26ccd178a628d0cd8a6c5"


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _record(record: dict[str, Any]) -> dict[str, Any]:
    copied = dict(record)
    copied["containing_function"] = None
    return copied


def _classify_record(record: dict[str, Any]) -> tuple[str, str] | None:
    address = int(record["instruction"], 16)
    for name, (start, end, role) in SEMANTIC_FUNCTIONS.items():
        if start <= address < end:
            return name, role
    return None


def _attach_semantic_seed(records: dict[str, Any]) -> dict[str, Any]:
    classified_counts = {name: 0 for name in SEMANTIC_FUNCTIONS}
    all_records = (
        *records["direct"]["calls"].values(),
        *records["direct"]["endpoints"].values(),
        *records["direct"]["absolute_memory_regions"].values(),
        *records["candidates"]["immediate_operands"].values(),
        *records["candidates"]["base_index_displacements"].values(),
    )
    for record_group in all_records:
        for record in record_group:
            classification = _classify_record(record)
            if classification is None:
                continue
            name, role = classification
            record["containing_function"] = name
            record["function_role"] = role
            classified_counts[name] += 1
    ranges = {
        name: {
            "start": f"0x{start:08x}",
            "end": f"0x{end:08x}",
            "role": role,
            "classified_record_count": classified_counts[name],
        }
        for name, (start, end, role) in SEMANTIC_FUNCTIONS.items()
    }
    return {"ranges": ranges, "unclassified_record_count": sum(
        1 for record_group in all_records for record in record_group
        if record["containing_function"] is None
    )}


def _records_from_report(report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    direct = {
        "calls": {
            name: [_record(item) for item in details["direct_call_xrefs"]]
            for name, details in report["functions"].items()
        },
        "endpoints": {
            name: [_record(item) for item in details["decoded_xrefs"]]
            for name, details in report["endpoints"].items()
        },
        "absolute_memory_regions": {
            name: [_record(item) for item in details["decoded_xrefs"]]
            for name, details in report["regions"].items()
        },
    }
    candidates = {
        "immediate_operands": {
            name: [_record(item) for item in details["immediate_operand_candidates"]]
            for name, details in report["regions"].items()
        },
        "base_index_displacements": {
            name: [_record(item) for item in details["base_index_displacement_candidates"]]
            for name, details in report["regions"].items()
        },
    }
    return direct, candidates


def _counts(direct: dict[str, Any], candidates: dict[str, Any]) -> dict[str, int]:
    return {
        "direct_calls": sum(len(items) for items in direct["calls"].values()),
        "endpoint_refs": sum(len(items) for items in direct["endpoints"].values()),
        "absolute_memory_operands": sum(
            len(items) for items in direct["absolute_memory_regions"].values()
        ),
        "immediate_operand_candidates": sum(
            len(items) for items in candidates["immediate_operands"].values()
        ),
        "base_index_displacement_candidates": sum(
            len(items) for items in candidates["base_index_displacements"].values()
        ),
    }


def manifest_from_inventory(report: dict[str, Any]) -> dict[str, Any]:
    """Convert a SHA-pinned inventory report to a fail-closed manifest."""

    if report.get("source", {}).get("sha256") != ORIGINAL_SHA256:
        raise ValueError("manifest source is not the pinned original")
    direct, candidates = _records_from_report(report)
    counts = _counts(direct, candidates)
    records = {"direct": direct, "candidates": candidates}
    semantic_seed = _attach_semantic_seed(records)
    return {
        "manifest_version": MANIFEST_VERSION,
        "source": {
            "original_sha256": ORIGINAL_SHA256,
            "path": report["source"]["path"],
        },
        "target_capacity": {
            "lower_bound": TARGET_LOWER_BOUND,
            "final_capacity": None,
            "headroom": "UNRESOLVED",
        },
        "regions": REGION_GEOMETRY,
        "aliases": ALIASES,
        "direct_references": direct,
        "candidates": candidates,
        "semantic_seed": semantic_seed,
        "record_counts": counts,
        "record_digest": _canonical_digest(records),
        "obligations": {
            name: {"requirement": requirement, "status": UNRESOLVED, "evidence": []}
            for name, requirement in OBLIGATIONS.items()
        },
        "activation": {
            "status": "NO-GO",
            "reason": "activation is prohibited while any relocation obligation is unresolved",
        },
    }


def generate_manifest(executable: Path) -> dict[str, Any]:
    """Read the pinned original and return a manifest; never writes an EXE."""

    return manifest_from_inventory(inventory(executable))


def _required_record_fields(record: dict[str, Any]) -> bool:
    return all(field in record for field in (
        "instruction", "bytes", "mnemonic", "operands", "evidence", "value",
        "containing_function",
    ))


def _validate_records(manifest: dict[str, Any]) -> None:
    direct = manifest["direct_references"]
    candidates = manifest["candidates"]
    for group in (
        *direct["calls"].values(),
        *direct["endpoints"].values(),
        *direct["absolute_memory_regions"].values(),
        *candidates["immediate_operands"].values(),
        *candidates["base_index_displacements"].values(),
    ):
        for record in group:
            if not isinstance(record, dict) or not _required_record_fields(record):
                raise ValueError("record is missing decoded instruction provenance")
            if record["evidence"] != "decoded_capstone_operand":
                raise ValueError("record is not decoded Capstone evidence")
            if record["containing_function"] is not None:
                classification = _classify_record(record)
                if classification is None or record["containing_function"] != classification[0]:
                    raise ValueError("containing function mapping is invalid")
                if record.get("function_role") != classification[1]:
                    raise ValueError("function role mapping is invalid")
    for region_name, records in direct["absolute_memory_regions"].items():
        for record in records:
            if record.get("kind") != "memory_absolute":
                raise ValueError(f"non-absolute record in direct region {region_name}")
    for region_name, records in candidates["immediate_operands"].items():
        start = int(manifest["regions"][region_name]["start"], 16)
        end = int(manifest["regions"][region_name]["end"], 16)
        for record in records:
            if record.get("kind") != "immediate_operand":
                raise ValueError(f"invalid immediate candidate in {region_name}")
            value = int(record["value"], 16)
            if not start <= value < end or record.get("operand_type") != "immediate":
                raise ValueError(f"out-of-range or malformed immediate candidate in {region_name}")
    for region_name, records in candidates["base_index_displacements"].items():
        start = int(manifest["regions"][region_name]["start"], 16)
        end = int(manifest["regions"][region_name]["end"], 16)
        for record in records:
            if record.get("kind") != "memory_base_index_displacement_candidate":
                raise ValueError(f"invalid base/index candidate in {region_name}")
            value = int(record["value"], 16)
            if not start <= value < end:
                raise ValueError(f"out-of-range base/index candidate in {region_name}")
            if record.get("effective_address") != "runtime effective address unresolved":
                raise ValueError(f"resolved effective address in {region_name}")


def _validate_semantic_seed(manifest: dict[str, Any]) -> None:
    seed = manifest.get("semantic_seed")
    if not isinstance(seed, dict) or set(seed) != {"ranges", "unclassified_record_count"}:
        raise ValueError("semantic seed is missing or malformed")
    ranges = seed["ranges"]
    if not isinstance(ranges, dict) or set(ranges) != set(SEMANTIC_FUNCTIONS):
        raise ValueError("semantic seed ranges are missing or tampered")
    expected_counts = {name: 0 for name in SEMANTIC_FUNCTIONS}
    unclassified = 0
    direct = manifest["direct_references"]
    candidates = manifest["candidates"]
    all_records = (
        *direct["calls"].values(),
        *direct["endpoints"].values(),
        *direct["absolute_memory_regions"].values(),
        *candidates["immediate_operands"].values(),
        *candidates["base_index_displacements"].values(),
    )
    for record_group in all_records:
        for record in record_group:
            classification = _classify_record(record)
            if classification is None:
                unclassified += 1
                if record.get("containing_function") is not None:
                    raise ValueError("unclassified record has a containing function")
                continue
            name, role = classification
            expected_counts[name] += 1
            if record.get("containing_function") != name or record.get("function_role") != role:
                raise ValueError("audited function semantic mapping is missing or tampered")
    expected_ranges = {
        name: {
            "start": f"0x{start:08x}",
            "end": f"0x{end:08x}",
            "role": role,
            "classified_record_count": expected_counts[name],
        }
        for name, (start, end, role) in SEMANTIC_FUNCTIONS.items()
    }
    if ranges != expected_ranges or seed["unclassified_record_count"] != unclassified:
        raise ValueError("semantic seed ranges or classified counts are tampered")


def validate_manifest(
    manifest: dict[str, Any], *, executable: Path | None = None,
) -> None:
    """Raise ``ValueError`` unless the manifest is complete and untampered.

    If ``executable`` is supplied, the entire direct/candidate inventory is
    regenerated from that SHA-pinned file and compared to the manifest.
    """

    if manifest.get("manifest_version") != MANIFEST_VERSION:
        raise ValueError("unsupported or missing manifest version")
    if manifest.get("source", {}).get("original_sha256") != ORIGINAL_SHA256:
        raise ValueError("original SHA-256 is missing or tampered")
    if manifest.get("target_capacity") != {
        "lower_bound": TARGET_LOWER_BOUND, "final_capacity": None, "headroom": "UNRESOLVED"
    }:
        raise ValueError("target capacity is missing or prematurely resolved")
    if manifest.get("regions") != REGION_GEOMETRY:
        raise ValueError("region geometry is missing or tampered")
    if manifest.get("aliases") != ALIASES:
        raise ValueError("required alias semantics are missing or tampered")
    expected_obligations = {
        name: {"requirement": requirement, "status": UNRESOLVED, "evidence": []}
        for name, requirement in OBLIGATIONS.items()
    }
    if manifest.get("obligations") != expected_obligations:
        raise ValueError("obligations are missing or tampered")
    if manifest.get("activation", {}).get("status") != "NO-GO":
        raise ValueError("activation must remain NO-GO while obligations are unresolved")
    if not isinstance(manifest.get("direct_references"), dict):
        raise ValueError("direct references are missing")
    if not isinstance(manifest.get("candidates"), dict):
        raise ValueError("candidate references are missing")
    if set(manifest["direct_references"]) != {
        "calls", "endpoints", "absolute_memory_regions",
    }:
        raise ValueError("direct reference categories are missing or tampered")
    if set(manifest["candidates"]) != {
        "immediate_operands", "base_index_displacements",
    }:
        raise ValueError("candidate categories are missing or tampered")
    _validate_records(manifest)
    _validate_semantic_seed(manifest)
    records = {
        "direct": manifest["direct_references"],
        "candidates": manifest["candidates"],
    }
    if manifest.get("record_digest") != _canonical_digest(records):
        raise ValueError("record digest mismatch")
    if manifest["record_digest"] != EXPECTED_RECORD_DIGEST:
        raise ValueError("record digest does not match the pinned original inventory")
    if manifest.get("record_counts") != _counts(
        manifest["direct_references"], manifest["candidates"]
    ):
        raise ValueError("record counts do not match records")
    if manifest["record_counts"] != EXPECTED_COUNTS:
        raise ValueError("record counts do not match the pinned original inventory")
    if executable is not None:
        expected = generate_manifest(executable)
        if expected["record_digest"] != manifest["record_digest"]:
            raise ValueError("manifest records do not match the pinned executable")


def summary(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return a compact evidence artifact without instruction record bodies."""

    return {
        "manifest_version": manifest["manifest_version"],
        "source": manifest["source"],
        "target_capacity": manifest["target_capacity"],
        "regions": manifest["regions"],
        "aliases": manifest["aliases"],
        "semantic_seed": manifest["semantic_seed"],
        "record_counts": manifest["record_counts"],
        "record_digest": manifest["record_digest"],
        "obligations": {
            name: details["status"] for name, details in manifest["obligations"].items()
        },
        "activation": manifest["activation"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, help="SHA-pinned original executable")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", action="store_true")
    parser.add_argument("--validate", type=Path, metavar="MANIFEST")
    args = parser.parse_args(argv)
    if args.validate is not None:
        manifest = json.loads(args.validate.read_text(encoding="utf-8"))
        validate_manifest(manifest, executable=args.exe)
        print("PASS: manifest schema is complete and untampered; activation remains NO-GO")
        return 0
    if args.exe is None:
        parser.error("--exe is required when --validate is not used")
    manifest = generate_manifest(args.exe)
    validate_manifest(manifest)
    payload = summary(manifest) if args.summary else manifest
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
