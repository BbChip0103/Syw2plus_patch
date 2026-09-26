#!/usr/bin/env python3
"""lap211 middle-tier probe: F5 + F4 make overall PASS unreachable for a real
candidate run, because tools/runtime_env.py's candidate selector flow appends
untagged ``{"args": [...], "result": "OBSERVED"}`` records to ``inputs``.

Evidence for the producer shape (not invented):
  local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json
  inputs[0] tag='menu', inputs[1]/{2} have no 'tag' key and result='OBSERVED'
  tools/runtime_env.py:3500-3502 record_input(); :3529 passes it to _g1_selector_flow.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap211_f6_producer_conflict_probe.py
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location(
    "compare_g1_stage_b_f6", ROOT / "tools/compare_g1_stage_b.py"
)
assert SPEC and SPEC.loader
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)

REAL_CANDIDATE = ROOT / "local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json"


def _scene(dx: int = 0, dy: int = 0) -> dict[str, Any]:
    return {
        "unit_slots": [
            {"slot": 1401, "owner": 0, "type": 70, "world": {"x": 50 + dx, "y": 44 + dy}},
            {"slot": 1402, "owner": 0, "type": 33, "world": {"x": 55 + dx, "y": 47 + dy}},
            {"slot": 1403, "owner": 1, "type": 12, "world": {"x": 120 + dx, "y": 130 + dy}},
        ],
        "world_bounds": {"width": 256, "height": 256},
    }


def _stages() -> list[dict[str, Any]]:
    return [
        {"tag": "unit_select", "result": "PASS", "content": [400, 300],
         "before": {"selection": {"count": 0, "selected_slot": 1401, "selected_type": 70}},
         "after": {"selection": {"count": 1, "selected_slot": 1401, "selected_type": 70}}},
        {"tag": "production", "result": "BLOCKED", "content": [700, 560],
         "before": {"selection": {"count": 1}}, "after": {"selection": {"count": 1}}},
        {"tag": "drag_select", "result": "PASS", "content": [300, 200],
         "before": {"selection": {"count": 1, "selected_slot": 1401, "selected_type": 70},
                    "drag_to": {"content": [600, 420]}},
         "after": {"selection": {"count": 1, "selected_slot": 1401, "selected_type": 70}}},
        {"tag": "minimap", "result": "PASS", "content": [120, 500],
         "before": {"selection": {"count": 1}, "camera": [10, 10]},
         "after": {"selection": {"count": 1}, "camera": [44, 12]}},
    ]


# Baseline producer shape: every selector-flow step is tagged (_g1_record_input).
baseline = {
    "scene": _scene(),
    "inputs": [
        {"tag": "menu", "result": "PASS"},
        {"tag": "solo_mode_setup", "result": "PASS"},
        {"tag": "lobby_start_setup", "result": "PASS"},
        *_stages(),
    ],
}

# Candidate producer shape: selector flow goes through the untagged record_input stub.
candidate = {
    "scene": _scene(17, -9),
    "inputs": [
        {"tag": "menu", "result": "PASS"},
        {"args": ["solo_mode", [232, 331]], "result": "OBSERVED"},
        {"args": ["lobby_start", [400, 520]], "result": "OBSERVED"},
        *_stages(),
    ],
}

report = compare.compare_evidence(baseline, candidate)

# Control: the same candidate with the two untagged observation records removed.
control = {"scene": candidate["scene"],
           "inputs": [item for item in candidate["inputs"] if "tag" in item]}
control_report = compare.compare_evidence(baseline, control)

real_tags: list[Any] = []
if REAL_CANDIDATE.is_file():
    real = json.loads(REAL_CANDIDATE.read_text(encoding="utf-8"))
    real_tags = [item.get("tag") if isinstance(item, dict) else "<non-object>"
                 for item in real.get("inputs", [])]

print(json.dumps({
    "probe_set": "lap211_f6_producer_conflict",
    "real_candidate_input_tags": real_tags,
    "all_stage_statuses": {tag: item["status"] for tag, item in report["stages"].items()},
    "scene_status": report["scene"]["status"],
    "candidate_input_errors": report["input_errors"]["candidate"],
    "overall_status_with_observed_records": report["status"],
    "overall_status_without_observed_records": control_report["status"],
    "finding": ("every stage PASSes and the scene matches, yet overall is not PASS purely "
                "because the candidate producer writes untagged OBSERVED records"),
    "verdict": "CONFIRMED" if (
        all(item["status"] == "PASS" for item in report["stages"].values())
        and report["scene"]["status"] == "PASS"
        and report["status"] != "PASS"
        and control_report["status"] == "PASS"
    ) else "NOT_CONFIRMED",
}, ensure_ascii=False, indent=2))
