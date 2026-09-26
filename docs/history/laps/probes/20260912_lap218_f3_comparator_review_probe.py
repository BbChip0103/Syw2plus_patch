#!/usr/bin/env python3
"""lap218 middle-tier independent review probe for G1 card2 defect F3.

Rebuilds the Stage B evidence fixtures from scratch (it deliberately does not
import ``tests/test_compare_g1_stage_b.py`` helpers) and exercises
``tools/compare_g1_stage_b.py`` over two groups:

* group A reproduces the claims lap217 made for the F3 repair;
* group B probes for verdict laundering or verdict erosion the repair may have
  introduced.

The probe never starts the game and never writes outside this probe report.
"""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location(
    "lap218_compare", ROOT / "tools/compare_g1_stage_b.py"
)
assert SPEC and SPEC.loader
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


def scene(*, shift: tuple[int, int] = (0, 0), owner1_type: int = 66) -> dict[str, Any]:
    dx, dy = shift
    return {
        "unit_slots": [
            {"slot": 811, "owner": 0, "type": 33, "world": {"x": 120 + dx, "y": 60 + dy}},
            {"slot": 812, "owner": 0, "type": 44, "world": {"x": 124 + dx, "y": 63 + dy}},
            {"slot": 813, "owner": 1, "type": 55, "world": {"x": 90 + dx, "y": 20 + dy}},
            {"slot": 814, "owner": 1, "type": owner1_type, "world": {"x": 95 + dx, "y": 26 + dy}},
        ],
        "world_bounds": {"width": 200, "height": 200},
    }


def select_stage(tag: str, *, before: int, after: int, slot: int = 811,
                 unit_type: int = 33, result: str = "PASS") -> dict[str, Any]:
    entry: dict[str, Any] = {
        "tag": tag,
        "result": result,
        "content": [400, 300] if tag == "unit_select" else [300, 200],
        "before": {"selection": {"count": before, "selected_slot": slot,
                                 "selected_type": unit_type}},
        "after": {"selection": {"count": after, "selected_slot": slot,
                                "selected_type": unit_type}},
    }
    if tag == "drag_select":
        entry["before"]["drag_to"] = {"content": [520, 380]}
    return entry


def minimap_stage(*, before_camera: list[int], after_camera: list[int],
                  result: str = "PASS") -> dict[str, Any]:
    return {
        "tag": "minimap",
        "result": result,
        "content": [140, 500],
        "before": {"camera": before_camera},
        "after": {"camera": after_camera},
    }


def evidence(*, shift: tuple[int, int] = (0, 0), owner1_type: int = 66) -> dict[str, Any]:
    return {
        "scene": scene(shift=shift, owner1_type=owner1_type),
        "inputs": [
            select_stage("unit_select", before=0, after=1),
            {"tag": "production", "result": "BLOCKED", "content": [700, 540],
             "before": {"selection": {"count": 1}}, "after": {"selection": {"count": 1}}},
            select_stage("drag_select", before=1, after=1),
            minimap_stage(before_camera=[120, 60], after_camera=[40, 0]),
        ],
    }


def find(doc: dict[str, Any], tag: str) -> dict[str, Any]:
    return next(item for item in doc["inputs"] if item["tag"] == tag)


def timeout_selection_after(*, count: int, slot: int, unit_type: int) -> dict[str, Any]:
    return {"wait": "not observed", "tick": None,
            "last": {"count": count, "selected_slot": slot, "selected_type": unit_type}}


CASES: list[tuple[str, str, Any, dict[str, Any]]] = []


def case(name: str, group: str, build, expected: dict[str, Any]) -> None:
    CASES.append((name, group, build, expected))


# ---------------------------------------------------------------- group A ---
def a1():
    base, cand = evidence(), evidence(shift=(11, -4))
    for doc in (base, cand):
        drag = find(doc, "drag_select")
        drag["result"] = "FAIL_NO_EFFECT"
        drag["after"] = timeout_selection_after(count=1, slot=812, unit_type=44)
    return base, cand


case("A1_both_disputed_selection_last", "A", a1,
     {"overall": "INCONCLUSIVE", "stage": ("drag_select", "UNKNOWN_DISPUTED_ORACLE"),
      "identity": [812, 44]})


def a2():
    base, cand = evidence(), evidence()
    drag = find(cand, "drag_select")
    drag["result"] = "FAIL_NO_EFFECT"
    drag["after"] = {"wait": "not observed", "tick": None}
    return base, cand


case("A2_disputed_without_after_last", "A", a2,
     {"overall": "INCONCLUSIVE", "stage": ("drag_select", "INCONCLUSIVE")})


def a3():
    base, cand = evidence(), evidence(shift=(11, -4))
    for doc in (base, cand):
        mini = find(doc, "minimap")
        mini["result"] = "FAIL_NO_EFFECT"
        mini["after"] = {"wait": "not observed", "tick": None,
                         "last": {"camera": [40, 0], "tick": None}}
    return base, cand


case("A3_disputed_minimap_last_camera", "A", a3,
     {"overall": "INCONCLUSIVE", "stage": ("minimap", "UNKNOWN_DISPUTED_ORACLE")})


case("A4_clean_pair_still_passes", "A", lambda: (evidence(), evidence(shift=(11, -4))),
     {"overall": "PASS", "stage": ("drag_select", "PASS")})


def a5():
    base, cand = evidence(), evidence()
    drag = find(cand, "drag_select")
    drag["result"] = "FAIL_NO_EFFECT"
    drag["after"] = timeout_selection_after(count=1, slot=811, unit_type=33)
    return base, cand


case("A5_one_sided_dispute", "A", a5,
     {"overall": "INCONCLUSIVE", "stage": ("drag_select", "UNKNOWN_DISPUTED_ORACLE")})


def a6():
    base, cand = a1()
    find(cand, "drag_select")["after"]["last"] = {"count": 7, "selected_slot": 999,
                                                  "selected_type": 3}
    return base, cand


case("A6_disputed_with_diverging_observation_is_not_fail", "A", a6,
     {"overall": "INCONCLUSIVE", "stage": ("drag_select", "UNKNOWN_DISPUTED_ORACLE")})


def a7():
    base, cand = evidence(), evidence()
    del find(cand, "unit_select")["result"]
    return base, cand


case("A7_missing_result_key_is_not_pass", "A", a7,
     {"overall": "INCONCLUSIVE", "stage": ("unit_select", "UNKNOWN_DISPUTED_ORACLE")})


def a8():
    base, cand = a1()
    cand["scene"] = scene(owner1_type=77)
    return base, cand


case("A8_scene_gate_still_dominates_dispute", "A", a8,
     {"overall": "UNKNOWN_SCENE_MISMATCH", "stage": ("drag_select", "UNKNOWN_SCENE_MISMATCH")})


def a9():
    base, cand = a1()
    cand["inputs"].append(deepcopy(find(cand, "unit_select")))
    return base, cand


case("A9_f4_input_errors_preserved", "A", a9,
     {"overall": "INCONCLUSIVE", "stage": ("drag_select", "UNKNOWN_DISPUTED_ORACLE"),
      "candidate_input_errors": ["duplicate input tag: unit_select"]})


def a10():
    base, cand = a1()
    del find(cand, "minimap")["before"]["camera"]
    return base, cand


case("A10_f1_missing_camera_preserved", "A", a10,
     {"overall": "INCONCLUSIVE", "stage": ("minimap", "INCONCLUSIVE")})


def a11():
    base, cand = a1()
    find(cand, "drag_select")["content"] = [301, 200]
    return base, cand


case("A11_disputed_geometry_difference_still_fails", "A", a11,
     {"overall": "FAIL", "stage": ("drag_select", "FAIL")})


def a12():
    base, cand = evidence(), evidence()
    for doc in (base, cand):
        drag = find(doc, "drag_select")
        drag["result"] = "UNKNOWN_BUDGET_EXHAUSTED"
        drag["after"] = timeout_selection_after(count=1, slot=811, unit_type=33)
    return base, cand


case("A12_budget_exhausted_classification_is_disputed", "A", a12,
     {"overall": "INCONCLUSIVE", "stage": ("drag_select", "UNKNOWN_DISPUTED_ORACLE")})


# ---------------------------------------------------------------- group B ---
def b1():
    """result=PASS but the stage carries the timeout ``after.last`` shape."""
    base, cand = evidence(), evidence(shift=(11, -4))
    for doc in (base, cand):
        drag = find(doc, "drag_select")
        drag["after"] = timeout_selection_after(count=1, slot=811, unit_type=33)
    return base, cand


case("B1_pass_result_with_timeout_shaped_after", "B", b1,
     {"overall": "PASS", "stage": ("drag_select", "PASS")})


def b2():
    """result=PASS, corrupt ``after.selection`` shadowed by a good ``after.last``."""
    base, cand = evidence(), evidence(shift=(11, -4))
    for doc in (base, cand):
        drag = find(doc, "drag_select")
        drag["after"] = {"selection": "UNKNOWN",
                         "last": {"count": 1, "selected_slot": 811, "selected_type": 33}}
    return base, cand


case("B2_corrupt_after_selection_shadowed_by_last", "B", b2,
     {"overall": "PASS", "stage": ("drag_select", "PASS")})


def b3():
    """A hard non-timeout ``FAIL`` with diverging observations."""
    base, cand = evidence(), evidence(shift=(11, -4))
    mini = find(cand, "minimap")
    mini["result"] = "FAIL"
    mini["after"] = {"camera": [120, 60]}
    return base, cand


case("B3_hard_fail_result_no_longer_reports_card_fail", "B", b3,
     {"overall": "INCONCLUSIVE", "stage": ("minimap", "UNKNOWN_DISPUTED_ORACLE")})


def b4():
    """``before`` has no timeout fallback: it must stay fail-closed."""
    base, cand = evidence(), evidence(shift=(11, -4))
    for doc in (base, cand):
        drag = find(doc, "drag_select")
        drag["result"] = "FAIL_NO_EFFECT"
        drag["before"] = {"last": {"count": 1, "selected_slot": 811, "selected_type": 33},
                          "drag_to": {"content": [520, 380]}}
        drag["after"] = timeout_selection_after(count=1, slot=811, unit_type=33)
    return base, cand


case("B4_before_has_no_last_fallback", "B", b4,
     {"overall": "INCONCLUSIVE", "stage": ("drag_select", "INCONCLUSIVE")})


def b5():
    base, cand = a1()
    find(cand, "drag_select")["after"]["last"] = {"count": "UNKNOWN", "selected_slot": 812,
                                                  "selected_type": 44}
    return base, cand


case("B5_corrupt_last_count_is_inconclusive", "B", b5,
     {"overall": "INCONCLUSIVE", "stage": ("drag_select", "INCONCLUSIVE")})


def b6():
    """Every compared stage disputed at once must not collapse to PASS."""
    base, cand = evidence(), evidence(shift=(11, -4))
    for doc in (base, cand):
        for tag in ("unit_select", "drag_select"):
            item = find(doc, tag)
            item["result"] = "FAIL_NO_EFFECT"
            item["after"] = timeout_selection_after(count=1, slot=811, unit_type=33)
        mini = find(doc, "minimap")
        mini["result"] = "FAIL_NO_EFFECT"
        mini["after"] = {"wait": "not observed", "last": {"camera": [40, 0]}}
    return base, cand


case("B6_all_stages_disputed", "B", b6,
     {"overall": "INCONCLUSIVE", "stage": ("unit_select", "UNKNOWN_DISPUTED_ORACLE")})


def run() -> dict[str, Any]:
    results = []
    for name, group, build, expected in CASES:
        baseline, candidate = build()
        report = compare.compare_evidence(baseline, candidate)
        tag, want_stage = expected["stage"]
        stage_report = report["stages"][tag]
        observed: dict[str, Any] = {
            "overall": report["status"],
            "stage": [tag, stage_report["status"]],
        }
        want: dict[str, Any] = {"overall": expected["overall"], "stage": [tag, want_stage]}
        if "identity" in expected:
            identity = stage_report.get("selected_identity", {})
            observed["identity"] = identity.get("candidate")
            want["identity"] = expected["identity"]
        if "candidate_input_errors" in expected:
            observed["candidate_input_errors"] = report["input_errors"]["candidate"]
            want["candidate_input_errors"] = expected["candidate_input_errors"]
        results.append({
            "case": name, "group": group, "expected": want, "observed": observed,
            "match": want == observed,
            "stage_reason": stage_report.get("reason"),
        })
    unexpected = [item["case"] for item in results if not item["match"]]
    never_pass_violations = [
        item["case"] for item in results
        if item["group"] == "A" and item["case"] != "A4_clean_pair_still_passes"
        and item["observed"]["overall"] == "PASS"
    ]
    return {
        "probe": "lap218_f3_comparator_review",
        "comparator": "tools/compare_g1_stage_b.py",
        "cases": results,
        "unexpected": unexpected,
        "disputed_pass_violations": never_pass_violations,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2, sort_keys=True))
