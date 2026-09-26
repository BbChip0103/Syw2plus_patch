#!/usr/bin/env python3
"""lap214 middle probe — raw-data adjudication of F2 / F3 / R6-B.

Read-only over preserved evidence.  Builds its own synthetic fixtures instead of
importing the repository test-suite, so the comparator is exercised
independently.  Never starts the game.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "tools"))

import compare_g1_stage_b as C  # noqa: E402

RUN_A = REPO / "local/runtime/20260912_010714_2914723_0/output/g1_a/evidence.json"
RUN_B = REPO / "local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def stage(evidence: dict, tag: str) -> dict | None:
    for item in evidence.get("inputs", []):
        if isinstance(item, dict) and item.get("tag") == tag:
            return item
    return None


def synthetic(slot: int, unit_type: int) -> dict:
    """A minimal, self-contained PASS-shaped evidence object."""

    scene = {
        "unit_slots": [
            {"slot": 1199, "owner": 0, "type": 70, "world": {"x": 161, "y": 90}},
            {"slot": 1198, "owner": 0, "type": 21, "world": {"x": 163, "y": 92}},
            {"slot": 1197, "owner": 1, "type": 49, "world": {"x": 140, "y": 40}},
            {"slot": 1196, "owner": 1, "type": 7, "world": {"x": 142, "y": 42}},
        ],
        "world_bounds": {"width": 180, "height": 180},
    }

    def sel(count: int, slot_value: int | None, type_value: int | str) -> dict:
        return {"count": count, "selected_slot": slot_value, "selected_type": type_value}

    return {
        "scene": scene,
        "inputs": [
            {"tag": "unit_select", "result": "PASS", "content": [410, 270],
             "before": {"selection": sel(0, None, "UNKNOWN")},
             "after": {"selection": sel(1, slot, unit_type)}},
            {"tag": "drag_select", "result": "PASS", "content": [350, 180],
             "before": {"selection": sel(1, slot, unit_type),
                        "drag_to": {"content": [550, 350]}},
             "after": {"selection": sel(2, slot, unit_type)}},
            {"tag": "minimap", "result": "PASS", "content": [150, 520],
             "before": {"selection": sel(2, slot, unit_type), "camera": [161, 90]},
             "after": {"selection": sel(2, slot, unit_type), "camera": [40, 120]}},
        ],
    }


results: dict[str, object] = {}

# ---------------------------------------------------------------- P1 scene control
run_a, run_b = load(RUN_A), load(RUN_B)
pair = C.compare_evidence(run_a, run_b)
results["P1_same_binary_pair"] = {
    "question": "do two independent runs of the ORIGINAL binary compare as one scene?",
    "status": pair["status"],
    "scene_checks": pair["scene"]["checks"],
    "nations": {
        "run_a": {k: v.get("nation") for k, v in run_a["scene"]["owners"].items()
                  if v.get("active_units")},
        "run_b": {k: v.get("nation") for k, v in run_b["scene"]["owners"].items()
                  if v.get("active_units")},
    },
    "replay_seed_observed": run_b["scene"]["reproduction_identifier"]["replay_seed_observed"],
}

# ---------------------------------------------------------------- P2 / F2 slot identity
slots = {
    "run_a": sorted((u["slot"], u["owner"], u["type"], u["world"]["x"], u["world"]["y"])
                    for u in run_a["scene"]["unit_slots"]),
    "run_b": sorted((u["slot"], u["owner"], u["type"], u["world"]["x"], u["world"]["y"])
                    for u in run_b["scene"]["unit_slots"]),
}
slot_ids = {name: [row[0] for row in rows] for name, rows in slots.items()}
owner_of_slot = {name: {row[0]: row[1] for row in rows} for name, rows in slots.items()}
base = synthetic(1199, 70)
results["P2_F2_slot_identity"] = {
    "question": "is an absolute slot id a sound cross-run parity predicate?",
    "slot_ids_equal_across_runs": slot_ids["run_a"] == slot_ids["run_b"],
    "slot_ids": slot_ids,
    "slot_to_owner_equal": owner_of_slot["run_a"] == owner_of_slot["run_b"],
    "types_equal_across_runs": (
        [row[2] for row in slots["run_a"]] == [row[2] for row in slots["run_b"]]
    ),
    "types": {name: [row[2] for row in rows] for name, rows in slots.items()},
    "slot_only_divergence_verdict":
        C.compare_evidence(base, synthetic(1100, 70))["stages"]["unit_select"]["status"],
    "type_only_divergence_verdict":
        C.compare_evidence(base, synthetic(1199, 71))["status"],
    "identical_pair_verdict": C.compare_evidence(base, synthetic(1199, 70))["status"],
}

# ---------------------------------------------------------------- P3 / F3 disputed oracle
drag = stage(run_b, "drag_select")
assert drag is not None
after = drag["after"]
results["P3_F3_disputed_oracle"] = {
    "question": "may a FAIL_NO_EFFECT label be inherited as a card FAIL?",
    "recorded_result": drag["result"],
    "timeout_cause": drag.get("timeout_cause"),
    "after_has_selection_key": "selection" in after,
    "after_last_observation": after.get("last"),
    "before_identity": [drag["before"]["selection"]["selected_slot"],
                        drag["before"]["selection"]["selected_type"]],
    "after_last_identity": [after["last"]["selected_slot"], after["last"]["selected_type"]],
    "identity_changed": (
        [drag["before"]["selection"]["selected_slot"],
         drag["before"]["selection"]["selected_type"]]
        != [after["last"]["selected_slot"], after["last"]["selected_type"]]
    ),
    "comparator_selection_reads_after_last":
        C._selection(drag, "after") is not None,
    "comparator_stage_verdict_on_this_record":
        C._stage_report("drag_select", drag, drag)["status"],
}

# ---------------------------------------------------------------- P4 / R6-B drag gate
results["P4_R6B_drag_gate"] = {
    "question": "is count>=2 a grounded drag-success predicate?",
    "expected_string": drag["expected"],
    "observed_count": [drag["before"]["selection"]["count"], after["last"]["count"]],
    "observed_first_slot": [drag["before"]["selection"]["first_slot"],
                            after["last"]["first_slot"]],
    "engine_responded": (
        drag["before"]["selection"]["first_slot"] != after["last"]["first_slot"]
    ),
    "band_select_semantics_in_memory_maps": False,
}

print(json.dumps(results, ensure_ascii=False, indent=2, sort_keys=True))
