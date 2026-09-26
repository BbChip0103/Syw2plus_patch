#!/usr/bin/env python3
"""lap277 middle probe: is the lap271 S1 acceptance formula sufficient?

Offline only.  Never starts the game, never writes to the original tree and
never edits the producer, the comparator or their regressions.  It feeds
synthetic evidence pairs to ``compare_g1_stage_b.compare_evidence`` to decide,
with machine evidence, which of the six lap271 restoration items the formula
``scene.status == "PASS" and no stage is UNKNOWN_SLOT_CORRESPONDENCE``
actually establishes.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.compare_g1_stage_b import compare_evidence  # noqa: E402


def _evidence(*, nation0: int, tick: int, scene_camera: list[int],
              slots: tuple[int, int, int], select_before: int,
              minimap_camera_before: list[int], twin_slot: int | None = None,
              selected_slot: int | None = None) -> dict[str, Any]:
    """Build one evidence object.  Only restoration-relevant knobs vary.

    ``twin_slot`` adds a second owner-0 type-5 unit at the same world position,
    which is the only way to make two runs select the SAME normalized identity
    through a DIFFERENT engine slot id.
    """

    slot_a, slot_b, slot_c = slots
    chosen = slot_a if selected_slot is None else selected_slot
    return {
        "scene": {
            "owners": {
                "0": {"nation": nation0, "active_units": 2},
                "1": {"nation": 9, "active_units": 1},
            },
            "unit_slots": [
                {"slot": slot_a, "owner": 0, "type": 5, "world": {"x": 100, "y": 100}},
                {"slot": slot_b, "owner": 0, "type": 7, "world": {"x": 110, "y": 100}},
                {"slot": slot_c, "owner": 1, "type": 5, "world": {"x": 200, "y": 100}},
            ] + ([{"slot": twin_slot, "owner": 0, "type": 5, "world": {"x": 100, "y": 100}}]
                 if twin_slot is not None else []),
            "world_bounds": {"width": 64, "height": 64},
            "camera": scene_camera,
            "tick": tick,
        },
        "inputs": [
            {
                "tag": "unit_select", "content": [100, 100], "result": "PASS",
                "before": {"selection": {"count": select_before}},
                "after": {"selection": {"count": select_before + 1,
                                        "selected_slot": chosen, "selected_type": 5}},
            },
            {
                "tag": "drag_select", "content": [90, 90], "result": "PASS",
                "before": {"selection": {"count": select_before + 1},
                           "drag_to": {"content": [130, 130]}},
                "after": {"selection": {"count": select_before + 3,
                                        "selected_slot": chosen, "selected_type": 5}},
            },
            {
                "tag": "minimap", "content": [20, 20], "result": "PASS",
                "before": {"camera": minimap_camera_before},
                "after": {"camera": [40, 40]},
            },
        ],
    }


BASELINE_KW = dict(nation0=1, tick=1000, scene_camera=[0, 0], slots=(10, 11, 20),
                   select_before=0, minimap_camera_before=[0, 0])


def _stage(report: dict[str, Any], tag: str) -> str:
    return str(report["stages"][tag]["status"])


def _lap271_formula(report: dict[str, Any]) -> bool:
    """scene PASS AND no stage is UNKNOWN_SLOT_CORRESPONDENCE."""

    return report["scene"]["status"] == "PASS" and all(
        item["status"] != "UNKNOWN_SLOT_CORRESPONDENCE" for item in report["stages"].values()
    )


def main() -> int:
    cases: list[dict[str, Any]] = []
    failures: list[str] = []

    def record(name: str, candidate: dict[str, Any], *, expect_overall: str,
               expect_formula: bool, claim: str,
               baseline: dict[str, Any] | None = None) -> None:
        if baseline is None:
            baseline = _evidence(**BASELINE_KW)  # type: ignore[arg-type]
        report = compare_evidence(baseline, candidate)
        entry = {
            "case": name,
            "claim": claim,
            "overall": report["status"],
            "scene": report["scene"]["status"],
            "stages": {tag: _stage(report, tag) for tag in ("unit_select", "drag_select", "minimap")},
            "lap271_formula": _lap271_formula(report),
            "expected_overall": expect_overall,
            "expected_formula": expect_formula,
        }
        if entry["overall"] != expect_overall:
            failures.append(f"{name}: overall {entry['overall']} != {expect_overall}")
        if entry["lap271_formula"] is not expect_formula:
            failures.append(f"{name}: formula {entry['lap271_formula']} != {expect_formula}")
        cases.append(entry)

    # 1. control: identical evidence reaches PASS, so later cases are not vacuous.
    record("control_identical", _evidence(**BASELINE_KW),  # type: ignore[arg-type]
           expect_overall="PASS", expect_formula=True,
           claim="identical fixture reaches overall PASS")

    # 2. items 1/5/6: nation, engine slot ids of non-selected units, absolute
    #    pre-input selection count, scene camera, scene tick and the minimap
    #    pre-input camera all differ, yet the pair still reaches overall PASS.
    record("blind_to_items_1_5_6",
           _evidence(nation0=4, tick=987654, scene_camera=[50, 50], slots=(10, 111, 120),
                     select_before=5, minimap_camera_before=[3, 3]),
           expect_overall="PASS", expect_formula=True,
           claim="differing nation, non-selected slot ids, absolute selection count, "
                 "scene camera/tick and pre-input camera still reach overall PASS")

    # 3. scene signature ignores every owner outside {0, 1}.
    foreign = _evidence(**BASELINE_KW)  # type: ignore[arg-type]
    foreign["scene"]["unit_slots"].append(
        {"slot": 30, "owner": 2, "type": 5, "world": {"x": 300, "y": 100}})
    foreign["scene"]["owners"]["2"] = {"nation": 3, "active_units": 1}
    record("blind_to_foreign_owner", foreign,
           expect_overall="PASS", expect_formula=True,
           claim="an extra owner-2 unit present only in the candidate still reaches overall PASS")

    # 4. control: multiplicity inside owners 0/1 IS caught by relative offsets.
    duplicate = _evidence(**BASELINE_KW)  # type: ignore[arg-type]
    duplicate["scene"]["unit_slots"].append(
        {"slot": 12, "owner": 0, "type": 7, "world": {"x": 110, "y": 100}})
    duplicate["scene"]["owners"]["0"]["active_units"] = 3
    record("multiplicity_owner01_control", duplicate,
           expect_overall="UNKNOWN_SCENE_MISMATCH", expect_formula=False,
           claim="a duplicate coincident owner-0 unit is caught by relative_world_offsets")

    # 5. vacuity: a missing stage satisfies the negative formula.
    missing_stage = _evidence(**BASELINE_KW)  # type: ignore[arg-type]
    missing_stage["inputs"] = [item for item in missing_stage["inputs"]
                               if item["tag"] != "drag_select"]
    record("vacuous_missing_stage", missing_stage,
           expect_overall="INCONCLUSIVE", expect_formula=True,
           claim="a completely absent drag_select stage satisfies the lap271 formula")

    # 6. vacuity: an unobserved selection count satisfies the negative formula.
    missing_count = _evidence(**BASELINE_KW)  # type: ignore[arg-type]
    del missing_count["inputs"][0]["after"]["selection"]["count"]
    record("vacuous_missing_selection_count", missing_count,
           expect_overall="INCONCLUSIVE", expect_formula=True,
           claim="a missing selection count satisfies the lap271 formula")

    # 7. control: the F2-R2 slot demotion rule is unchanged and still fires.
    #    Both sides carry a coincident type-5 twin, so the normalized identity
    #    is identical and only the engine slot id differs.
    twin_kw = dict(BASELINE_KW, twin_slot=13)
    twin_baseline = _evidence(**twin_kw)  # type: ignore[arg-type]
    twin_candidate = _evidence(**dict(twin_kw, selected_slot=13))  # type: ignore[arg-type]
    record("slot_demotion_control", twin_candidate, baseline=twin_baseline,
           expect_overall="INCONCLUSIVE", expect_formula=False,
           claim="same normalized identity through a different engine slot id still "
                 "demotes to UNKNOWN_SLOT_CORRESPONDENCE")

    report = {
        "probe": "lap277-middle-s1-formula/v1",
        "question": "does the lap271 formula establish the six restoration items?",
        "cases": cases,
        "failures": failures,
        "verdict": "formula_insufficient" if not failures else "probe_self_check_failed",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
