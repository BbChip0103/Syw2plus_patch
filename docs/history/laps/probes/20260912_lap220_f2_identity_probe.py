#!/usr/bin/env python3
"""Independent synthetic probe for the G1 Stage B F2 identity contract."""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools" / "compare_g1_stage_b.py"
SPEC = importlib.util.spec_from_file_location("compare_g1_stage_b", SOURCE)
assert SPEC and SPEC.loader
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


def _scene(*, selected_slot: int = 1199, selected_type: int = 70) -> dict[str, Any]:
    units = [
        {"slot": selected_slot, "owner": 0, "type": selected_type,
         "world": {"x": 161, "y": 90}},
        {"slot": 1198, "owner": 0, "type": 21, "world": {"x": 163, "y": 92}},
        {"slot": 1197, "owner": 1, "type": 49, "world": {"x": 140, "y": 40}},
        {"slot": 1196, "owner": 1, "type": 7, "world": {"x": 142, "y": 42}},
    ]
    return {"unit_slots": units, "world_bounds": {"width": 180, "height": 180}}


def _stage(tag: str, before_count: int, after_count: int, *, slot: int = 1199,
           unit_type: int = 70) -> dict[str, Any]:
    before: dict[str, Any] = {"selection": {"count": before_count}}
    after: dict[str, Any] = {"selection": {"count": after_count}}
    if tag != "minimap":
        before["selection"] = {"count": before_count, "selected_slot": slot,
                                "selected_type": unit_type}
        after["selection"] = {"count": after_count, "selected_slot": slot,
                               "selected_type": unit_type}
    else:
        before["camera"] = [161, 90]
        after["camera"] = [81, 0]
    result = {"tag": tag, "result": "PASS", "content": [410, 270],
              "before": before, "after": after}
    if tag == "drag_select":
        result["content"] = [350, 180]
        before["drag_to"] = {"content": [550, 350]}
    if tag == "minimap":
        result["content"] = [150, 520]
    return result


def _evidence(*, slot: int = 1199, selected_type: int = 70,
              scene: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "scene": scene if scene is not None else _scene(selected_slot=slot, selected_type=selected_type),
        "inputs": [
            _stage("unit_select", 0, 1, slot=slot, unit_type=selected_type),
            _stage("production", 1, 1, slot=slot, unit_type=selected_type),
            _stage("drag_select", 1, 1, slot=slot, unit_type=selected_type),
            _stage("minimap", 1, 1),
        ],
    }


def main() -> int:
    baseline = _evidence()
    cases: dict[str, dict[str, Any]] = {}

    normal = compare.compare_evidence(baseline, deepcopy(baseline))
    cases["normal_pair"] = {
        "expected": "PASS", "actual": normal["status"],
        "stage_statuses": {tag: value["status"] for tag, value in normal["stages"].items()},
    }

    slot_only = _evidence(slot=900)
    slot_report = compare.compare_evidence(baseline, slot_only)
    cases["slot_only_difference"] = {
        "expected": "INCONCLUSIVE", "actual": slot_report["status"],
        "unit_select": slot_report["stages"]["unit_select"]["status"],
        "drag_select": slot_report["stages"]["drag_select"]["status"],
    }

    missing_scene = deepcopy(baseline)
    missing_scene["inputs"][0]["after"]["selection"]["selected_slot"] = 900
    missing_report = compare.compare_evidence(baseline, missing_scene)
    cases["selected_slot_missing_from_scene"] = {
        "expected": "INCONCLUSIVE", "actual": missing_report["status"],
        "unit_select": missing_report["stages"]["unit_select"]["status"],
    }

    divergent = _evidence(scene=deepcopy(baseline["scene"]))
    drag = next(item for item in divergent["inputs"] if item["tag"] == "drag_select")
    drag["after"]["selection"]["selected_slot"] = 1198
    drag["after"]["selection"]["selected_type"] = 21
    drag["after"]["selection"]["count"] = 2
    divergent_report = compare.compare_evidence(baseline, divergent)
    cases["normalized_identity_and_count_diverge"] = {
        "expected": "FAIL", "actual": divergent_report["status"],
        "drag_select": divergent_report["stages"]["drag_select"]["status"],
    }

    failures = {
        name: value for name, value in cases.items() if value["actual"] != value["expected"]
    }
    report = {"cases": cases, "failures": failures, "status": "PASS" if not failures else "FAIL"}
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
