#!/usr/bin/env python3
"""lap273 middle — independent review probe for the lap272 F3-R2 comparator repair.

Offline only.  Never starts the game, never touches Wine/Xvfb, never writes to the
original tree.  Reads tools/runtime_env.py as data (AST) to derive the producer's
result vocabulary independently instead of trusting the comparator's comment.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import itertools
import json
import re
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
COMPARATOR = ROOT / "tools/compare_g1_stage_b.py"
PRODUCER = ROOT / "tools/runtime_env.py"

spec = importlib.util.spec_from_file_location("compare_g1_stage_b", COMPARATOR)
assert spec and spec.loader
compare = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compare)

CLASSIFICATION_SHAPE = re.compile(r"^(?:FAIL|UNKNOWN)_[A-Z0-9_]+$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --- A1: derive the producer vocabulary independently -----------------------
def producer_classifications() -> dict[str, list[int]]:
    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    found: dict[str, list[int]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if CLASSIFICATION_SHAPE.match(node.value):
                found.setdefault(node.value, []).append(node.lineno)
    return dict(sorted(found.items()))


def producer_plain_results() -> dict[str, list[int]]:
    """Non-timeout strings the producer can flush into an input entry's result."""
    tree = ast.parse(PRODUCER.read_text(encoding="utf-8"))
    found: dict[str, list[int]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value in {"PASS", "FAIL", "BLOCKED", "SKIP"}:
            found.setdefault(node.value, []).append(node.lineno)
    return {key: sorted(set(value)) for key, value in sorted(found.items())}


# --- shared offline fixtures (built here, not imported from lap272 tests) ---
def scene(offset: tuple[int, int] = (0, 0)) -> dict:
    ox, oy = offset
    return {
        "unit_slots": [
            {"slot": 1199, "owner": 0, "type": 70, "world": {"x": 161 + ox, "y": 90 + oy}},
            {"slot": 1198, "owner": 0, "type": 21, "world": {"x": 163 + ox, "y": 92 + oy}},
            {"slot": 1197, "owner": 1, "type": 49, "world": {"x": 140 + ox, "y": 40 + oy}},
            {"slot": 1196, "owner": 1, "type": 7, "world": {"x": 142 + ox, "y": 42 + oy}},
        ],
        "world_bounds": {"width": 180, "height": 180},
    }


def stage(tag: str, before_count: int, after_count: int, *, slot: int = 1199,
          unit_type: int = 70, camera_before=None, camera_after=None) -> dict:
    before: dict = {}
    after: dict = {}
    if tag == "minimap":
        before["camera"] = camera_before
        after["camera"] = camera_after
    else:
        before["selection"] = {"count": before_count, "selected_slot": slot, "selected_type": unit_type}
        after["selection"] = {"count": after_count, "selected_slot": slot, "selected_type": unit_type}
    entry: dict = {"tag": tag, "result": "PASS", "content": [410, 270],
                   "before": before, "after": after}
    if tag == "drag_select":
        entry["content"] = [350, 180]
        before["drag_to"] = {"content": [550, 350]}
    if tag == "minimap":
        entry["content"] = [150, 520]
    return entry


def evidence(offset=(0, 0)) -> dict:
    return {
        "scene": scene(offset),
        "inputs": [
            stage("unit_select", 0, 1),
            stage("production", 1, 1),
            stage("drag_select", 1, 1),
            stage("minimap", 1, 1, camera_before=[161, 90], camera_after=[81, 0]),
        ],
    }


def with_result(ev: dict, tag: str, result) -> dict:
    out = deepcopy(ev)
    for item in out["inputs"]:
        if item["tag"] == tag:
            if result is _MISSING:
                item.pop("result", None)
            else:
                item["result"] = result
    return out


class _Missing:
    def __repr__(self) -> str:
        return "<absent>"


_MISSING = _Missing()


def main() -> int:
    report: dict = {
        "probe": "lap273_middle_f3_r2_review",
        "fingerprints": {
            "tools/compare_g1_stage_b.py": sha256(COMPARATOR),
            "tools/runtime_env.py": sha256(PRODUCER),
            "tests/test_compare_g1_stage_b.py": sha256(ROOT / "tests/test_compare_g1_stage_b.py"),
        },
    }

    declared = sorted(compare._DISPUTED_SOURCE_RESULTS)
    derived = producer_classifications()
    report["A1_vocabulary"] = {
        "comparator_declared": declared,
        "producer_derived": {key: value for key, value in derived.items()},
        "missing_from_comparator": sorted(set(derived) - set(declared)),
        "declared_but_not_in_producer": sorted(set(declared) - set(derived)),
        "producer_plain_results": producer_plain_results(),
    }

    # --- A2: per-result matrix on an otherwise-passing control pair ---------
    control_b, control_c = evidence(), evidence(offset=(20, -7))
    baseline_control = compare.compare_evidence(control_b, control_c)
    report["A2_control"] = {
        "overall": baseline_control["status"],
        "stages": {tag: item["status"] for tag, item in baseline_control["stages"].items()},
        "scene": baseline_control["scene"]["status"],
    }

    probe_results = sorted(set(derived)) + ["FAIL", "BLOCKED", "SKIP", "WAT_UNRECOGNIZED", _MISSING]
    matrix = []
    for tag in ("unit_select", "drag_select", "minimap"):
        for result in probe_results:
            candidate = with_result(control_c, tag, result)
            out = compare.compare_evidence(control_b, candidate)
            matrix.append({
                "stage": tag,
                "candidate_result": repr(result) if result is _MISSING else result,
                "stage_status": out["stages"][tag]["status"],
                "overall": out["status"],
            })
    report["A2_matrix"] = matrix

    # --- A3: exhaustive new-PASS search ------------------------------------
    vocabulary = sorted(set(derived)) + ["PASS", "FAIL", "BLOCKED", "SKIP", "WAT_UNRECOGNIZED"]
    pass_paths = []
    for combo in itertools.product(vocabulary, repeat=2):
        for tag in ("unit_select", "drag_select", "minimap"):
            b = with_result(control_b, tag, combo[0])
            c = with_result(control_c, tag, combo[1])
            out = compare.compare_evidence(b, c)
            if out["status"] == "PASS":
                pass_paths.append({"stage": tag, "baseline": combo[0], "candidate": combo[1]})
    non_pass_pass_paths = [item for item in pass_paths
                           if not (item["baseline"] == "PASS" and item["candidate"] == "PASS")]
    report["A3_new_pass_paths"] = {
        "total_pass_combinations": len(pass_paths),
        "pass_with_any_non_PASS_source": non_pass_pass_paths,
    }

    # --- A4: hard FAIL precedence over a disputed sibling -------------------
    b = with_result(control_b, "unit_select", "UNKNOWN_BUDGET_EXHAUSTED")
    c = with_result(control_c, "unit_select", "FAIL")
    mixed = compare.compare_evidence(b, c)
    report["A4_fail_precedence"] = {
        "stage_status": mixed["stages"]["unit_select"]["status"],
        "overall": mixed["status"],
        "source_results": mixed["stages"]["unit_select"].get("source_results"),
    }

    # --- A5: disputed vs. a genuinely failing check ------------------------
    broken = deepcopy(control_c)
    for item in broken["inputs"]:
        if item["tag"] == "minimap":
            item["after"]["camera"] = [161, 90]  # camera did not move
    plain = compare.compare_evidence(control_b, broken)
    disputed = compare.compare_evidence(control_b, with_result(broken, "minimap", "FAIL_NO_EFFECT"))
    hard = compare.compare_evidence(control_b, with_result(broken, "minimap", "FAIL"))
    report["A5_broken_candidate"] = {
        "source_PASS": {"stage": plain["stages"]["minimap"]["status"], "overall": plain["status"]},
        "source_FAIL_NO_EFFECT": {"stage": disputed["stages"]["minimap"]["status"],
                                  "overall": disputed["status"]},
        "source_FAIL": {"stage": hard["stages"]["minimap"]["status"], "overall": hard["status"]},
    }

    # --- A6: scene gate and slot demotion invariance -----------------------
    mismatch = deepcopy(control_c)
    mismatch["scene"]["unit_slots"][0]["type"] = 99
    scene_out = compare.compare_evidence(control_b, mismatch)
    slot_c = deepcopy(control_c)
    slot_c["scene"]["unit_slots"][0]["slot"] = 900
    for item in slot_c["inputs"]:
        if item["tag"] in {"unit_select", "drag_select"}:
            item["before"]["selection"]["selected_slot"] = 900
            item["after"]["selection"]["selected_slot"] = 900
    slot_out = compare.compare_evidence(control_b, slot_c)
    report["A6_invariants"] = {
        "scene_mismatch_overall": scene_out["status"],
        "scene_mismatch_stage": scene_out["stages"]["unit_select"]["status"],
        "slot_demotion_overall": slot_out["status"],
        "slot_demotion_stage": slot_out["stages"]["unit_select"]["status"],
        "production_not_compared": scene_out["production"]["status"],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
