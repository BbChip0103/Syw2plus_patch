#!/usr/bin/env python3
"""Compare the offline input evidence from one G1 Stage B pair.

This tool never starts the game.  It compares the state changes recorded in
two ``evidence.json`` files and fails closed when the scene or an observation
is not sufficient for a parity claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence, cast


SCHEMA = "g1-stage-b-compare/v1"
STAGES = ("unit_select", "drag_select", "minimap")
# These are the timeout classifications currently flushed by the Stage B
# producer.  The vocabulary was re-derived from the two producer paths in
# tools/runtime_env.py: the direct UNKNOWN_STATE_READ_FAILURE raise in
# _g1_read_selection_stage (currently line 2183) and the _wait_state
# classification ternary (currently lines 3258-3264).  Keep this list explicit
# so a generic non-PASS check cannot hide producer FAIL results; the comparator
# regression derives those same producer literals by AST and detects drift.
_DISPUTED_SOURCE_RESULTS: frozenset[str] = frozenset({
    "FAIL_NO_EFFECT",
    "UNKNOWN_BUDGET_EXHAUSTED",
    "UNKNOWN_OBSERVATION_WINDOW_TRUNCATED",
    "UNKNOWN_STATE_READ_COVERAGE",
    "UNKNOWN_STATE_READ_FAILURE",
    "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED",
})


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _load_evidence(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"evidence is not an object: {path}")
    return value


def _inputs_by_tag(evidence: Mapping[str, Any]) -> tuple[dict[str, Mapping[str, Any]], list[str]]:
    raw_inputs = evidence.get("inputs")
    if not isinstance(raw_inputs, list):
        return {}, ["inputs is missing or is not a list"]
    by_tag: dict[str, Mapping[str, Any]] = {}
    errors: list[str] = []
    for index, item in enumerate(raw_inputs):
        if not isinstance(item, Mapping):
            errors.append(f"inputs[{index}] is not an object")
            continue
        tag = item.get("tag")
        if not isinstance(tag, str):
            errors.append(f"inputs[{index}].tag is missing or is not a string")
            continue
        if tag in by_tag:
            errors.append(f"duplicate input tag: {tag}")
        else:
            by_tag[tag] = item
    return by_tag, errors


def _scene_unit_records(
    scene: Mapping[str, Any],
) -> tuple[list[tuple[int, int, int, int, int]], tuple[int, int, int]] | None:
    raw_units = scene.get("unit_slots")
    if not isinstance(raw_units, list):
        return None
    units: list[tuple[int, int, int, int, int]] = []
    for item in raw_units:
        if not isinstance(item, Mapping):
            return None
        slot, owner, unit_type = item.get("slot"), item.get("owner"), item.get("type")
        world = item.get("world")
        if (not _is_int(slot) or not _is_int(owner) or not _is_int(unit_type)
                or not isinstance(world, Mapping)
                or not _is_int(world.get("x")) or not _is_int(world.get("y"))):
            return None
        slot_value = cast(int, slot)
        owner_value, type_value = cast(int, owner), cast(int, unit_type)
        x_value, y_value = cast(int, world["x"]), cast(int, world["y"])
        units.append((slot_value, owner_value, type_value, x_value, y_value))
    owner0_units = [item for item in units if item[1] == 0]
    owner1_units = [item for item in units if item[1] == 1]
    if not owner0_units or not owner1_units:
        return None
    # The anchor is deliberately derived from observed type/position, never a
    # slot id.  This makes the scene check translation-invariant across runs.
    anchor = min(
        (unit_type, x, y) for _slot, _owner, unit_type, x, y in owner0_units
    )
    return units, anchor


def _unit_records(scene: Mapping[str, Any]) -> tuple[list[tuple[int, int, int, int]], list[int], list[int]] | None:
    records = _scene_unit_records(scene)
    if records is None:
        return None
    units, (_anchor_type, anchor_x, anchor_y) = records
    owner_types: dict[int, list[int]] = {0: [], 1: []}
    for _slot, owner, unit_type, _x, _y in units:
        if owner in owner_types:
            owner_types[owner].append(unit_type)
    offsets = sorted((owner, unit_type, x - anchor_x, y - anchor_y)
                     for _slot, owner, unit_type, x, y in units if owner in (0, 1))
    return offsets, sorted(set(owner_types[0])), sorted(set(owner_types[1]))


def _scene_signature(evidence: Mapping[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    scene = evidence.get("scene")
    if not isinstance(scene, Mapping):
        return None, ["scene is missing or is not an object"]
    units = _unit_records(scene)
    bounds = scene.get("world_bounds")
    if units is None:
        return None, ["scene.unit_slots does not contain complete owner 0/1 world records"]
    if (not isinstance(bounds, Mapping) or not _is_int(bounds.get("width"))
            or not _is_int(bounds.get("height"))):
        return None, ["scene.world_bounds is incomplete"]
    offsets, owner0_types, owner1_types = units
    return {
        "owner0_unit_types": owner0_types,
        "owner1_unit_types": owner1_types,
        "relative_world_offsets": [list(item) for item in offsets],
        "world_bounds": [bounds["width"], bounds["height"]],
    }, []


def _scene_report(baseline: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    baseline_signature, baseline_errors = _scene_signature(baseline)
    candidate_signature, candidate_errors = _scene_signature(candidate)
    if baseline_signature is None or candidate_signature is None:
        return {
            "status": "INCONCLUSIVE",
            "baseline": baseline_signature,
            "candidate": candidate_signature,
            "errors": [f"baseline: {error}" for error in baseline_errors]
            + [f"candidate: {error}" for error in candidate_errors],
        }
    checks = {
        "owner0_unit_types": baseline_signature["owner0_unit_types"]
        == candidate_signature["owner0_unit_types"],
        "owner1_unit_types": baseline_signature["owner1_unit_types"]
        == candidate_signature["owner1_unit_types"],
        "relative_world_offsets": baseline_signature["relative_world_offsets"]
        == candidate_signature["relative_world_offsets"],
        "world_bounds": baseline_signature["world_bounds"] == candidate_signature["world_bounds"],
    }
    status = "PASS" if all(checks.values()) else "UNKNOWN_SCENE_MISMATCH"
    return {
        "status": status,
        "checks": checks,
        "baseline": baseline_signature,
        "candidate": candidate_signature,
    }


def _selection(stage: Mapping[str, Any], side: str) -> Mapping[str, Any] | None:
    state = stage.get(side)
    if not isinstance(state, Mapping):
        return None
    value = state.get("selection")
    if isinstance(value, Mapping):
        return value
    if side == "after":
        last = state.get("last")
        return last if isinstance(last, Mapping) else None
    return None


def _camera(stage: Mapping[str, Any], side: str) -> list[int] | None:
    state = stage.get(side)
    if not isinstance(state, Mapping):
        return None
    value = state.get("camera")
    if (isinstance(value, Sequence) and not isinstance(value, (str, bytes))
            and len(value) == 2 and all(_is_int(item) for item in value)):
        return list(value)
    if side == "after":
        last = state.get("last")
        value = last.get("camera") if isinstance(last, Mapping) else None
        if (isinstance(value, Sequence) and not isinstance(value, (str, bytes))
                and len(value) == 2 and all(_is_int(item) for item in value)):
            return list(value)
    return None


def _resolve_selected_identity(
    evidence: Mapping[str, Any], selection: Mapping[str, Any]
) -> tuple[list[int] | None, str | None]:
    slot = selection.get("selected_slot")
    unit_type = selection.get("selected_type")
    if not _is_int(slot) or not _is_int(unit_type):
        return None, "selected identity is missing or UNKNOWN"
    scene = evidence.get("scene")
    if not isinstance(scene, Mapping):
        return None, "scene is missing or is not an object"
    records = _scene_unit_records(scene)
    if records is None:
        return None, "scene.unit_slots does not contain complete owner 0/1 world records"
    units, (_anchor_type, anchor_x, anchor_y) = records
    matches = [item for item in units if item[0] == slot]
    if not matches:
        return None, "selected slot is not present in scene.unit_slots"
    if len(matches) != 1:
        return None, "selected slot is ambiguous in scene.unit_slots"
    _slot, owner, scene_type, x, y = matches[0]
    if scene_type != unit_type:
        return None, "selected type disagrees with scene.unit_slots"
    return [owner, scene_type, x - anchor_x, y - anchor_y], None


def _logical_geometry(stage: Mapping[str, Any]) -> Any:
    content = stage.get("content")
    if not (isinstance(content, Sequence) and not isinstance(content, (str, bytes))):
        return None
    geometry: list[Any] = [list(content)]
    if stage.get("tag") == "drag_select":
        before = stage.get("before")
        drag_to = before.get("drag_to") if isinstance(before, Mapping) else None
        destination = drag_to.get("content") if isinstance(drag_to, Mapping) else None
        if not (isinstance(destination, Sequence)
                and not isinstance(destination, (str, bytes))):
            return None
        geometry.append(list(destination))
    return geometry


def _stage_report(tag: str, baseline: Mapping[str, Any] | None,
                  candidate: Mapping[str, Any] | None,
                  baseline_evidence: Mapping[str, Any] | None = None,
                  candidate_evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if baseline is None or candidate is None:
        return {"status": "INCONCLUSIVE", "reason": "required input stage is missing"}
    baseline_geometry = _logical_geometry(baseline)
    candidate_geometry = _logical_geometry(candidate)
    if baseline_geometry is None or candidate_geometry is None:
        return {"status": "INCONCLUSIVE", "reason": "logical input geometry is missing"}
    if baseline_geometry != candidate_geometry:
        return {
            "status": "FAIL",
            "reason": "logical input geometry differs",
            "baseline_geometry": baseline_geometry,
            "candidate_geometry": candidate_geometry,
        }

    details: dict[str, Any] = {
        "geometry": baseline_geometry,
    }
    if tag in {"unit_select", "drag_select"}:
        baseline_before = _selection(baseline, "before")
        baseline_after = _selection(baseline, "after")
        candidate_before = _selection(candidate, "before")
        candidate_after = _selection(candidate, "after")
        counts = [
            item.get("count") if item is not None else None
            for item in (baseline_before, baseline_after, candidate_before, candidate_after)
        ]
        if not all(_is_int(value) for value in counts):
            return {"status": "INCONCLUSIVE", "reason": "selection count is missing or UNKNOWN"}
        count_values = [cast(int, value) for value in counts]
        deltas = {
            "baseline": count_values[1] - count_values[0],
            "candidate": count_values[3] - count_values[2],
        }
        details["selection_count"] = {
            "baseline": [count_values[0], count_values[1]],
            "candidate": [count_values[2], count_values[3]],
            "delta": deltas,
        }
        identities: dict[str, list[Any]] = {}
        observed_identities: dict[str, list[Any]] = {}
        slots: dict[str, int] = {}
        for name, selection in (("baseline", baseline_after), ("candidate", candidate_after)):
            assert selection is not None
            slot, unit_type = selection.get("selected_slot"), selection.get("selected_type")
            if not _is_int(slot) or not _is_int(unit_type):
                return {"status": "INCONCLUSIVE", "reason": "selected identity is missing or UNKNOWN"}
            observed_identities[name] = [slot, unit_type]
            slots[name] = cast(int, slot)
            if baseline_evidence is not None and candidate_evidence is not None:
                evidence = baseline_evidence if name == "baseline" else candidate_evidence
                resolved, reason = _resolve_selected_identity(evidence, selection)
                if resolved is None:
                    return {"status": "INCONCLUSIVE", "reason": reason}
                identities[name] = resolved
            else:
                # Keep direct callers of this internal helper useful for the
                # timeout-oracle probe. Full comparisons always pass evidence
                # so absolute slot ids are never used as a parity predicate.
                identities[name] = [slot, unit_type]
        details["selected_identity"] = identities
        details["observed_selected_identity"] = observed_identities
        details["selected_slot"] = {
            "baseline": slots["baseline"],
            "candidate": slots["candidate"],
            "equal": slots["baseline"] == slots["candidate"],
        }
        checks = {
            "selection_count_delta": deltas["baseline"] == deltas["candidate"],
            "selected_identity": identities["baseline"] == identities["candidate"],
        }
    else:
        cameras = {
            "baseline_before": _camera(baseline, "before"),
            "baseline_after": _camera(baseline, "after"),
            "candidate_before": _camera(candidate, "before"),
            "candidate_after": _camera(candidate, "after"),
        }
        missing = [name for name, value in cameras.items() if value is None]
        if missing:
            return {
                "status": "INCONCLUSIVE",
                "reason": "minimap camera observation is missing or UNKNOWN",
                "missing": missing,
            }
        baseline_camera_before = cameras["baseline_before"]
        baseline_camera_after = cameras["baseline_after"]
        candidate_camera_before = cameras["candidate_before"]
        candidate_camera_after = cameras["candidate_after"]
        assert baseline_camera_before is not None
        assert baseline_camera_after is not None
        assert candidate_camera_before is not None
        assert candidate_camera_after is not None
        details["camera_destination"] = {
            "baseline": baseline_camera_after,
            "candidate": candidate_camera_after,
        }
        checks = {
            "camera_changed_baseline": baseline_camera_before != baseline_camera_after,
            "camera_changed_candidate": candidate_camera_before != candidate_camera_after,
            "camera_destination": baseline_camera_after == candidate_camera_after,
        }
    details["checks"] = checks
    source_results = {"baseline": baseline.get("result"), "candidate": candidate.get("result")}
    if any(result == "FAIL" for result in source_results.values()):
        return {
            "status": "FAIL",
            "reason": "source input stage result is FAIL",
            "source_results": source_results,
            **details,
        }
    if any(isinstance(result, str) and result in _DISPUTED_SOURCE_RESULTS
           for result in source_results.values()):
        return {
            "status": "UNKNOWN_DISPUTED_ORACLE",
            "reason": "source input stage result is a timeout classification; observation is disputed",
            "source_results": source_results,
            **details,
        }
    if any(result != "PASS" for result in source_results.values()):
        return {
            "status": "INCONCLUSIVE",
            "reason": "source input stage result is missing or unrecognized",
            "source_results": source_results,
            **details,
        }
    if not all(checks.values()):
        return {"status": "FAIL", **details}
    if tag in {"unit_select", "drag_select"} and not details["selected_slot"]["equal"]:
        return {
            "status": "UNKNOWN_SLOT_CORRESPONDENCE",
            "reason": "selected slot ids differ; normalized identity is observational only",
            "source_results": source_results,
            **details,
        }
    return {"status": "PASS" if all(checks.values()) else "FAIL", **details}


def compare_evidence(baseline: Mapping[str, Any], candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Return a structured, fail-closed comparison of two evidence objects."""

    baseline_inputs, baseline_input_errors = _inputs_by_tag(baseline)
    candidate_inputs, candidate_input_errors = _inputs_by_tag(candidate)
    scene = _scene_report(baseline, candidate)
    if scene["status"] == "UNKNOWN_SCENE_MISMATCH":
        stages = {tag: {"status": "UNKNOWN_SCENE_MISMATCH", "reason": "scene mismatch"}
                  for tag in STAGES}
    else:
        stages = {
            tag: _stage_report(
                tag,
                baseline_inputs.get(tag),
                candidate_inputs.get(tag),
                baseline,
                candidate,
            )
            for tag in STAGES
        }
    stage_statuses = [report["status"] for report in stages.values()]
    if scene["status"] == "UNKNOWN_SCENE_MISMATCH":
        status = "UNKNOWN_SCENE_MISMATCH"
    elif scene["status"] != "PASS":
        status = "INCONCLUSIVE"
    elif "FAIL" in stage_statuses:
        status = "FAIL"
    elif any(item in {"INCONCLUSIVE", "UNKNOWN_DISPUTED_ORACLE", "UNKNOWN_SLOT_CORRESPONDENCE"}
             for item in stage_statuses):
        status = "INCONCLUSIVE"
    elif baseline_input_errors or candidate_input_errors:
        status = "INCONCLUSIVE"
    else:
        status = "PASS"
    return {
        "schema": SCHEMA,
        "status": status,
        "scene": scene,
        "stages": stages,
        "production": {
            "status": "NOT_COMPARED",
            "reason": "production is fail-closed/BLOCKED and is outside the Stage B parity dimensions",
        },
        "input_errors": {
            "baseline": baseline_input_errors,
            "candidate": candidate_input_errors,
        },
    }


def compare_paths(baseline_path: Path, candidate_path: Path) -> dict[str, Any]:
    return compare_evidence(_load_evidence(baseline_path), _load_evidence(candidate_path))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path, help="original g1-baseline evidence.json")
    parser.add_argument("candidate", type=Path, help="candidate presentation-trace evidence.json")
    args = parser.parse_args(argv)
    try:
        report = compare_paths(args.baseline, args.candidate)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        report = {"schema": SCHEMA, "status": "INCONCLUSIVE", "errors": [str(exc)]}
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
