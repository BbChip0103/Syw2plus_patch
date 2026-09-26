#!/usr/bin/env python3
"""lap221 middle: independent review probe for the G1 Stage B F2 identity repair.

Written from scratch for the review.  It does not import any repository test
helper and does not reuse the lap220 work-tier fixtures.  It answers three
questions:

1. Is absolute slot equality removed from the FAIL predicate (lap214 F2)?
2. Did the repair create any new overall ``PASS`` path?
3. Is the normalized identity really translation-invariant and fail-closed?
"""

from __future__ import annotations

import importlib.util
import json
import random
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "tools" / "compare_g1_stage_b.py"
SPEC = importlib.util.spec_from_file_location("compare_g1_stage_b_lap221", SOURCE)
assert SPEC and SPEC.loader
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


# Fixture is deliberately different from lap220: two owner-0 units share a
# type so that a slot<->position swap is invisible to the scene signature.
UNITS: list[dict[str, Any]] = [
    {"slot": 501, "owner": 0, "type": 70, "world": {"x": 200, "y": 300}},
    {"slot": 502, "owner": 0, "type": 70, "world": {"x": 240, "y": 300}},
    {"slot": 503, "owner": 0, "type": 12, "world": {"x": 210, "y": 340}},
    {"slot": 601, "owner": 1, "type": 49, "world": {"x": 500, "y": 700}},
    {"slot": 602, "owner": 1, "type": 7, "world": {"x": 520, "y": 720}},
]
SELECTED_SLOT = 501
SELECTED_TYPE = 70


def _scene(units: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "unit_slots": deepcopy(UNITS if units is None else units),
        "world_bounds": {"width": 1024, "height": 1024},
    }


def _select_stage(tag: str, content: list[int], before_count: int, after_count: int,
                  slot: int, unit_type: int) -> dict[str, Any]:
    stage: dict[str, Any] = {
        "tag": tag,
        "result": "PASS",
        "content": content,
        "before": {"selection": {"count": before_count, "selected_slot": slot,
                                 "selected_type": unit_type}},
        "after": {"selection": {"count": after_count, "selected_slot": slot,
                                "selected_type": unit_type}},
    }
    if tag == "drag_select":
        stage["before"]["drag_to"] = {"content": [550, 350]}
    return stage


def _evidence(*, slot: int = SELECTED_SLOT, unit_type: int = SELECTED_TYPE,
              units: list[dict[str, Any]] | None = None,
              unit_select_after: int = 1, drag_after: int = 3) -> dict[str, Any]:
    return {
        "scene": _scene(units),
        "inputs": [
            _select_stage("unit_select", [410, 270], 0, unit_select_after, slot, unit_type),
            {"tag": "production", "result": "BLOCKED", "content": [670, 490],
             "before": {}, "after": {}},
            _select_stage("drag_select", [350, 180], 1, drag_after, slot, unit_type),
            {"tag": "minimap", "result": "PASS", "content": [150, 520],
             "before": {"camera": [100, 100]}, "after": {"camera": [300, 200]}},
        ],
    }


def _stage_statuses(report: dict[str, Any]) -> dict[str, str]:
    return {tag: value["status"] for tag, value in report["stages"].items()}


def _selection_stages(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in evidence["inputs"] if item["tag"] in ("unit_select", "drag_select")]


def _case(cases: dict[str, Any], name: str, expected: str, report: dict[str, Any],
          note: str = "") -> None:
    cases[name] = {
        "expected": expected,
        "actual": report["status"],
        "stages": _stage_statuses(report),
        "note": note,
    }


def _translate(units: list[dict[str, Any]], dx: int, dy: int) -> list[dict[str, Any]]:
    moved = deepcopy(units)
    for item in moved:
        item["world"]["x"] += dx
        item["world"]["y"] += dy
    return moved


def main() -> int:  # noqa: C901 - a flat probe is easier to audit than helpers
    baseline = _evidence()
    cases: dict[str, Any] = {}

    # A. control
    _case(cases, "A_identical_pair", "PASS",
          compare.compare_evidence(baseline, deepcopy(baseline)))

    # B. translation invariance: same scene shifted, same slots.
    _case(cases, "B_translated_scene", "PASS",
          compare.compare_evidence(baseline, _evidence(units=_translate(UNITS, 1000, 1000))),
          "normalized identity must be anchor-relative")

    # C. THE regression the repair must catch: slot id and type are equal but
    # the two same-type owner-0 units traded world positions.  The scene
    # signature is unchanged, so the old absolute-slot predicate would PASS.
    swapped = deepcopy(UNITS)
    swapped[0]["world"], swapped[1]["world"] = swapped[1]["world"], swapped[0]["world"]
    _case(cases, "C_slot_position_swap_same_type", "FAIL",
          compare.compare_evidence(baseline, _evidence(units=swapped)),
          "equal slot+type, divergent normalized identity")

    # D. consistent renumbering: slot ids differ, everything else matches.
    renumbered = deepcopy(UNITS)
    for item in renumbered:
        item["slot"] += 400
    renumber_report = compare.compare_evidence(
        baseline, _evidence(slot=SELECTED_SLOT + 400, units=renumbered))
    _case(cases, "D_slot_only_renumbering", "INCONCLUSIVE", renumber_report,
          "must not be FAIL; slot ids are not a parity predicate")
    cases["D_slot_only_renumbering"]["stage_is_unknown_slot"] = all(
        renumber_report["stages"][tag]["status"] == "UNKNOWN_SLOT_CORRESPONDENCE"
        for tag in ("unit_select", "drag_select"))
    cases["D_slot_only_renumbering"]["normalized_identity_equal"] = (
        renumber_report["stages"]["unit_select"]["selected_identity"]["baseline"]
        == renumber_report["stages"]["unit_select"]["selected_identity"]["candidate"])

    # E. selected slot absent from its own scene.
    orphan = _evidence()
    for stage in _selection_stages(orphan):
        stage["after"]["selection"]["selected_slot"] = 9999
    _case(cases, "E_selected_slot_absent_from_scene", "INCONCLUSIVE",
          compare.compare_evidence(baseline, orphan))

    # F. ambiguous slot (duplicate slot id inside one scene).
    duplicated = deepcopy(UNITS)
    duplicated.append({"slot": SELECTED_SLOT, "owner": 0, "type": SELECTED_TYPE,
                       "world": {"x": 200, "y": 300}})
    dup_baseline = _evidence(units=duplicated)
    _case(cases, "F_ambiguous_slot_in_scene", "INCONCLUSIVE",
          compare.compare_evidence(dup_baseline, _evidence(units=duplicated)))

    # G. selection type disagrees with the scene record for that slot.
    mistyped = _evidence()
    for stage in _selection_stages(mistyped):
        stage["after"]["selection"]["selected_type"] = 21
    _case(cases, "G_selected_type_disagrees_with_scene", "INCONCLUSIVE",
          compare.compare_evidence(baseline, mistyped))

    # H. count delta divergence with identical identity.
    _case(cases, "H_count_delta_divergence", "FAIL",
          compare.compare_evidence(baseline, _evidence(drag_after=5)))

    # I. scene mismatch dominates.
    moved_enemy = deepcopy(UNITS)
    moved_enemy[3]["world"] = {"x": 900, "y": 100}
    _case(cases, "I_scene_offsets_differ", "UNKNOWN_SCENE_MISMATCH",
          compare.compare_evidence(baseline, _evidence(units=moved_enemy)))

    # J. selection identity missing entirely.
    headless = _evidence()
    for stage in _selection_stages(headless):
        stage["after"]["selection"].pop("selected_slot")
    _case(cases, "J_selected_slot_missing", "INCONCLUSIVE",
          compare.compare_evidence(baseline, headless))

    # K. latent branch: _stage_report called without evidence falls back to the
    # absolute (slot, type) predicate that F2 was supposed to retire.
    latent_baseline = _select_stage("unit_select", [410, 270], 0, 1, SELECTED_SLOT, SELECTED_TYPE)
    latent_candidate = deepcopy(latent_baseline)
    latent = compare._stage_report("unit_select", latent_baseline, latent_candidate)
    cases["K_stage_report_without_evidence"] = {
        "expected": "PASS",
        "actual": latent["status"],
        "identity_source": latent.get("selected_identity"),
        "note": "documents the dead fallback branch: absolute slot/type used as identity",
    }

    # L. randomized no-PASS-laundering sweep.
    rng = random.Random(20260912)
    sweep_violations: list[dict[str, Any]] = []
    pass_count = 0
    for _ in range(400):
        candidate = _evidence()
        mutations: list[str] = []
        if rng.random() < 0.45:
            delta = rng.choice([-400, 400, 37])
            for item in candidate["scene"]["unit_slots"]:
                item["slot"] += delta
            for stage in _selection_stages(candidate):
                stage["after"]["selection"]["selected_slot"] += delta
            mutations.append("renumber")
        if rng.random() < 0.35:
            units = candidate["scene"]["unit_slots"]
            units[0]["world"], units[1]["world"] = units[1]["world"], units[0]["world"]
            mutations.append("swap_positions")
        if rng.random() < 0.3:
            dx, dy = rng.randint(-50, 50), rng.randint(-50, 50)
            for item in candidate["scene"]["unit_slots"]:
                item["world"]["x"] += dx
                item["world"]["y"] += dy
            mutations.append(f"translate({dx},{dy})")
        if rng.random() < 0.25:
            _selection_stages(candidate)[rng.randint(0, 1)]["after"]["selection"]["count"] += 1
            mutations.append("count")
        if rng.random() < 0.2:
            _selection_stages(candidate)[0]["result"] = "FAIL_NO_EFFECT"
            mutations.append("disputed")
        if rng.random() < 0.15:
            candidate["inputs"].append(deepcopy(candidate["inputs"][0]))
            mutations.append("duplicate_tag")
        report = compare.compare_evidence(baseline, candidate)
        if report["status"] != "PASS":
            continue
        pass_count += 1
        ok = (report["scene"]["status"] == "PASS"
              and not report["input_errors"]["baseline"]
              and not report["input_errors"]["candidate"])
        for tag in ("unit_select", "drag_select"):
            stage = report["stages"][tag]
            ok = (ok
                  and stage["status"] == "PASS"
                  and stage["selected_slot"]["equal"]
                  and stage["selected_identity"]["baseline"] == stage["selected_identity"]["candidate"]
                  and stage["selection_count"]["delta"]["baseline"]
                  == stage["selection_count"]["delta"]["candidate"])
            # PASS stage reports omit source_results, so read the raw inputs.
            for side in (baseline, candidate):
                raw = next(item for item in side["inputs"] if item["tag"] == tag)
                ok = ok and raw.get("result") == "PASS"
        if not ok:
            sweep_violations.append({"mutations": mutations, "status": report["status"]})
    cases["L_random_sweep_pass_invariant"] = {
        "expected": "no_violation",
        "actual": "no_violation" if not sweep_violations else "violation",
        "samples": 400,
        "overall_pass_observed": pass_count,
        "violations": sweep_violations[:5],
        "note": "every overall PASS must carry equal slots, equal normalized identity, "
                "equal count deltas, PASS source results, PASS scene and zero input errors",
    }

    failures = {name: value for name, value in cases.items()
                if value["actual"] != value["expected"]}
    report = {
        "probe": "lap221_f2_identity_review",
        "source": str(SOURCE.relative_to(ROOT)),
        "cases": cases,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
