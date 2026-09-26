#!/usr/bin/env python3
"""lap211 middle-tier independent probe of the R5-B F5 bounded repair.

Deliberately does NOT import tests/test_compare_g1_stage_b.py.  The fixture
below is written from scratch with different slots/types/coordinates so the
verdict does not inherit the repository test's assumptions.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap211_r5b_f5_probe.py
"""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location(
    "compare_g1_stage_b_probe", ROOT / "tools/compare_g1_stage_b.py"
)
assert SPEC and SPEC.loader
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


def _scene(dx: int = 0, dy: int = 0) -> dict[str, Any]:
    return {
        "unit_slots": [
            {"slot": 1401, "owner": 0, "type": 70, "world": {"x": 50 + dx, "y": 44 + dy}},
            {"slot": 1402, "owner": 0, "type": 33, "world": {"x": 55 + dx, "y": 47 + dy}},
            {"slot": 1403, "owner": 1, "type": 12, "world": {"x": 120 + dx, "y": 130 + dy}},
        ],
        "world_bounds": {"width": 256, "height": 256},
    }


def _evidence(dx: int = 0, dy: int = 0, *, camera_after=(44, 12)) -> dict[str, Any]:
    return {
        "scene": _scene(dx, dy),
        "inputs": [
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
             "after": {"selection": {"count": 1}, "camera": list(camera_after)}},
        ],
    }


def _pair() -> tuple[dict[str, Any], dict[str, Any]]:
    # candidate is the same scene translated; slot ids are intentionally
    # identical so that F2 (absolute slot identity, still unresolved) does not
    # confound the F5 verdict.
    return _evidence(), _evidence(17, -9)


RESULTS: list[dict[str, Any]] = []


def record(name: str, expect_status: str, report: dict[str, Any], *,
           expect_errors: list[str] | None = None, side: str = "candidate") -> None:
    actual_errors = report["input_errors"][side]
    ok = report["status"] == expect_status
    if expect_errors is not None:
        ok = ok and actual_errors == expect_errors
    RESULTS.append({
        "probe": name,
        "expect_status": expect_status,
        "actual_status": report["status"],
        "expect_errors": expect_errors,
        "actual_errors": actual_errors,
        "verdict": "PASS" if ok else "FAIL",
    })


ERR = "inputs[{index}].tag is missing or is not a string"

# ---- F5: corrupted extra record on the candidate side must block PASS ------
BAD_TAGS: list[tuple[str, Any]] = [
    ("P1_tag_key_missing", "__OMIT__"),
    ("P2_tag_int", 7),
    ("P3_tag_none", None),
    ("P4_tag_true", True),
    ("P5_tag_false", False),
    ("P6_tag_float", 3.5),
    ("P7_tag_list", ["unit_select"]),
    ("P8_tag_dict", {"tag": "unit_select"}),
    ("P9_tag_bytes", b"unit_select"),
]
for name, tag_value in BAD_TAGS:
    baseline, candidate = _pair()
    extra: dict[str, Any] = {"result": "PASS", "content": [1, 2]}
    if tag_value != "__OMIT__":
        extra["tag"] = tag_value
    candidate["inputs"].append(extra)
    record(name, "INCONCLUSIVE", compare.compare_evidence(baseline, candidate),
           expect_errors=[ERR.format(index=4)])

# ---- F5 on the baseline side as well --------------------------------------
for name, tag_value in (("P10_baseline_tag_missing", "__OMIT__"), ("P11_baseline_tag_none", None)):
    baseline, candidate = _pair()
    extra = {"result": "PASS"}
    if tag_value != "__OMIT__":
        extra["tag"] = tag_value
    baseline["inputs"].append(extra)
    record(name, "INCONCLUSIVE", compare.compare_evidence(baseline, candidate),
           expect_errors=[ERR.format(index=4)], side="baseline")

# ---- index reporting: corrupt record placed first --------------------------
baseline, candidate = _pair()
candidate["inputs"].insert(0, {"result": "PASS"})
record("P12_corrupt_record_first_index0", "INCONCLUSIVE",
       compare.compare_evidence(baseline, candidate), expect_errors=[ERR.format(index=0)])

# ---- multiple corrupt records ---------------------------------------------
baseline, candidate = _pair()
candidate["inputs"].append({"result": "PASS"})
candidate["inputs"].append({"tag": 9})
record("P13_two_corrupt_records", "INCONCLUSIVE", compare.compare_evidence(baseline, candidate),
       expect_errors=[ERR.format(index=4), ERR.format(index=5)])

# ---- a required stage whose own tag is corrupted ---------------------------
baseline, candidate = _pair()
candidate["inputs"][0]["tag"] = 7
report = compare.compare_evidence(baseline, candidate)
record("P14_required_stage_tag_corrupted", "INCONCLUSIVE", report,
       expect_errors=[ERR.format(index=0)])
RESULTS.append({
    "probe": "P14b_required_stage_becomes_missing",
    "expect_status": "INCONCLUSIVE",
    "actual_status": report["stages"]["unit_select"]["status"],
    "expect_errors": None,
    "actual_errors": report["stages"]["unit_select"].get("reason"),
    "verdict": "PASS" if report["stages"]["unit_select"]["status"] == "INCONCLUSIVE" else "FAIL",
})

# ---- not over-blocking: the clean pair must still PASS ---------------------
baseline, candidate = _pair()
record("P15_clean_translated_pair", "PASS", compare.compare_evidence(baseline, candidate),
       expect_errors=[])

# ---- an extra record with a valid but unknown string tag is not an error ---
baseline, candidate = _pair()
candidate["inputs"].append({"tag": "debug_note", "result": "PASS"})
record("P16_unknown_string_tag_is_ignored", "PASS",
       compare.compare_evidence(baseline, candidate), expect_errors=[])

baseline, candidate = _pair()
candidate["inputs"].append({"tag": "", "result": "PASS"})
record("P17_empty_string_tag_is_ignored", "PASS",
       compare.compare_evidence(baseline, candidate), expect_errors=[])

# ---- F1/F4 regressions must still hold ------------------------------------
baseline, candidate = _pair()
del candidate["inputs"][3]["before"]["camera"]
record("P18_F1_missing_candidate_before_camera", "INCONCLUSIVE",
       compare.compare_evidence(baseline, candidate), expect_errors=[])

baseline, candidate = _pair()
candidate["inputs"].append(deepcopy(candidate["inputs"][0]))
record("P19_F4_duplicate_tag", "INCONCLUSIVE", compare.compare_evidence(baseline, candidate),
       expect_errors=["duplicate input tag: unit_select"])

baseline, candidate = _pair()
candidate["inputs"].append("not-an-object")
record("P20_F4_non_object_entry", "INCONCLUSIVE", compare.compare_evidence(baseline, candidate),
       expect_errors=["inputs[4] is not an object"])

# ---- real divergence must still FAIL, not be softened ---------------------
baseline = _evidence()
candidate = _evidence(17, -9, camera_after=(99, 99))
record("P21_camera_destination_divergence_still_fail", "FAIL",
       compare.compare_evidence(baseline, candidate), expect_errors=[])

baseline = _evidence()
candidate = _evidence(17, -9, camera_after=(10, 10))
record("P22_candidate_camera_frozen_still_fail", "FAIL",
       compare.compare_evidence(baseline, candidate), expect_errors=[])

baseline, candidate = _pair()
candidate["inputs"][2]["after"]["selection"]["count"] = 4
record("P23_selection_delta_divergence_still_fail", "FAIL",
       compare.compare_evidence(baseline, candidate), expect_errors=[])

# ---- corruption must not upgrade a FAIL into INCONCLUSIVE -----------------
baseline = _evidence()
candidate = _evidence(17, -9, camera_after=(99, 99))
candidate["inputs"].append({"result": "PASS"})
record("P24_corrupt_record_does_not_mask_fail", "FAIL",
       compare.compare_evidence(baseline, candidate), expect_errors=[ERR.format(index=4)])

failures = [item for item in RESULTS if item["verdict"] != "PASS"]
print(json.dumps({
    "probe_set": "lap211_r5b_f5_independent",
    "total": len(RESULTS),
    "passed": len(RESULTS) - len(failures),
    "failed": len(failures),
    "results": RESULTS,
}, ensure_ascii=False, indent=2))
raise SystemExit(0 if not failures else 1)
