from __future__ import annotations

import ast
import importlib.util
import re
from copy import deepcopy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "compare_g1_stage_b", ROOT / "tools/compare_g1_stage_b.py"
)
assert SPEC and SPEC.loader
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


def _producer_timeout_classifications() -> set[str]:
    """Derive the current producer vocabulary without pinning a source SHA."""

    tree = ast.parse((ROOT / "tools/runtime_env.py").read_text(encoding="utf-8"))
    producer_functions = {"_g1_read_selection_stage", "_wait_state"}
    literals: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in producer_functions:
            continue
        literals.update(
            item.value
            for item in ast.walk(node)
            if isinstance(item, ast.Constant)
            and isinstance(item.value, str)
            and re.fullmatch(r"^(?:FAIL|UNKNOWN)_[A-Z0-9_]+$", item.value)
        )
    return literals


def scene(*, offset: tuple[int, int] = (0, 0), alternate_type: bool = False,
          bounds: tuple[int, int] = (180, 180)) -> dict[str, object]:
    ox, oy = offset
    return {
        "unit_slots": [
            {"slot": 1199, "owner": 0, "type": 70, "world": {"x": 161 + ox, "y": 90 + oy}},
            {"slot": 1198, "owner": 0, "type": 21 if not alternate_type else 22,
             "world": {"x": 163 + ox, "y": 92 + oy}},
            {"slot": 1197, "owner": 1, "type": 49, "world": {"x": 140 + ox, "y": 40 + oy}},
            {"slot": 1196, "owner": 1, "type": 7, "world": {"x": 142 + ox, "y": 42 + oy}},
        ],
        "world_bounds": {"width": bounds[0], "height": bounds[1]},
    }


def stage(tag: str, before_count: int, after_count: int, *, camera_before=None,
          camera_after=None, slot: int = 1199, unit_type: int = 70) -> dict[str, object]:
    before: dict[str, object] = {"selection": {"count": before_count}}
    after: dict[str, object] = {"selection": {"count": after_count}}
    if tag != "minimap":
        before["selection"] = {"count": before_count, "selected_slot": slot, "selected_type": unit_type}
        after["selection"] = {"count": after_count, "selected_slot": slot, "selected_type": unit_type}
    else:
        before["camera"] = camera_before
        after["camera"] = camera_after
    result: dict[str, object] = {"tag": tag, "result": "PASS", "content": [410, 270],
                                 "before": before, "after": after}
    if tag == "drag_select":
        result["content"] = [350, 180]
        before["drag_to"] = {"content": [550, 350]}
    if tag == "minimap":
        result["content"] = [150, 520]
    return result


def evidence(*, candidate_offset=(0, 0), alternate_type=False, stage_overrides=None):
    stages = [
        stage("unit_select", 0, 1),
        stage("production", 1, 1),
        stage("drag_select", 1, 1),
        stage("minimap", 1, 1, camera_before=[161, 90], camera_after=[81, 0]),
    ]
    if stage_overrides:
        for tag, update in stage_overrides.items():
            next(item for item in stages if item["tag"] == tag).update(update)
    return {"scene": scene(offset=candidate_offset, alternate_type=alternate_type), "inputs": stages}


def test_matching_translated_scene_and_input_deltas_pass_without_slot_scene_key():
    baseline = evidence()
    candidate = deepcopy(evidence(candidate_offset=(20, -7)))
    candidate["scene"]["unit_slots"][1]["slot"] = 900  # type/offset, not absolute slot, define scene parity.
    report = compare.compare_evidence(baseline, candidate)
    assert report["status"] == "PASS"
    assert report["production"]["status"] == "NOT_COMPARED"
    assert all(item["status"] == "PASS" for item in report["stages"].values())


def test_selected_slot_difference_is_unknown_after_scene_resolution():
    baseline = evidence()
    candidate = deepcopy(evidence())
    candidate["scene"]["unit_slots"][0]["slot"] = 900
    for item in candidate["inputs"]:
        if item["tag"] in {"unit_select", "drag_select"}:
            item["before"]["selection"]["selected_slot"] = 900
            item["after"]["selection"]["selected_slot"] = 900
    report = compare.compare_evidence(baseline, candidate)
    assert report["status"] == "INCONCLUSIVE"
    for tag in ("unit_select", "drag_select"):
        selected = report["stages"][tag]
        assert selected["status"] == "UNKNOWN_SLOT_CORRESPONDENCE"
        assert selected["selected_identity"]["baseline"] == [0, 70, -2, -2]
        assert selected["selected_identity"]["candidate"] == [0, 70, -2, -2]
        assert selected["selected_slot"]["equal"] is False


def test_selected_slot_missing_from_scene_is_inconclusive():
    candidate = evidence()
    unit_select = next(item for item in candidate["inputs"] if item["tag"] == "unit_select")
    unit_select["after"]["selection"]["selected_slot"] = 900
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["stages"]["unit_select"]["status"] == "INCONCLUSIVE"
    assert report["stages"]["unit_select"]["reason"] == (
        "selected slot is not present in scene.unit_slots"
    )


def test_scene_mismatch_is_unknown_not_fail_or_pass():
    report = compare.compare_evidence(evidence(), evidence(alternate_type=True))
    assert report["status"] == "UNKNOWN_SCENE_MISMATCH"
    assert all(item["status"] == "UNKNOWN_SCENE_MISMATCH" for item in report["stages"].values())


def test_selection_delta_divergence_is_fail():
    candidate = evidence(stage_overrides={
        "drag_select": {"before": {"selection": {"count": 1}, "drag_to": {"content": [550, 350]}},
                         "after": {"selection": {"count": 2, "selected_slot": 1198,
                                                   "selected_type": 21}}}
    })
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "FAIL"
    assert report["stages"]["drag_select"]["status"] == "FAIL"


def test_unknown_observation_is_inconclusive_and_never_pass():
    candidate = evidence(stage_overrides={
        "unit_select": {"after": {"selection": {"count": 1, "selected_slot": None,
                                                     "selected_type": "UNKNOWN"}}}
    })
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["stages"]["unit_select"]["status"] == "INCONCLUSIVE"


def test_missing_stage_is_inconclusive():
    candidate = evidence()
    candidate["inputs"] = [item for item in candidate["inputs"] if item["tag"] != "minimap"]
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["stages"]["minimap"]["status"] == "INCONCLUSIVE"


def test_missing_minimap_before_camera_is_inconclusive():
    candidate = evidence()
    minimap = next(item for item in candidate["inputs"] if item["tag"] == "minimap")
    del minimap["before"]["camera"]
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["stages"]["minimap"]["status"] == "INCONCLUSIVE"
    assert report["stages"]["minimap"]["missing"] == ["candidate_before"]


def test_input_errors_prevent_overall_pass():
    candidate = evidence()
    unit_select = next(item for item in candidate["inputs"] if item["tag"] == "unit_select")
    candidate["inputs"].append(deepcopy(unit_select))
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["input_errors"]["candidate"] == ["duplicate input tag: unit_select"]


def test_input_record_without_tag_prevents_overall_pass():
    candidate = evidence()
    candidate["inputs"].append({"result": "PASS"})
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["input_errors"]["candidate"] == [
        "inputs[4].tag is missing or is not a string"
    ]


def test_input_record_with_non_string_tag_prevents_overall_pass():
    candidate = evidence()
    candidate["inputs"].append({"tag": 7, "result": "PASS"})
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["input_errors"]["candidate"] == [
        "inputs[4].tag is missing or is not a string"
    ]


def test_disputed_timeout_reads_after_last_and_never_passes():
    baseline = evidence()
    candidate = evidence()
    for item in (baseline, candidate):
        drag = next(entry for entry in item["inputs"] if entry["tag"] == "drag_select")
        drag["result"] = "FAIL_NO_EFFECT"
        drag["timeout_cause"] = "FAIL_NO_EFFECT"
        drag["after"] = {
            "wait": "not observed",
            "last": {"count": 1, "selected_slot": 1198, "selected_type": 21},
            "tick": None,
        }
    report = compare.compare_evidence(baseline, candidate)
    disputed = report["stages"]["drag_select"]
    assert report["status"] == "INCONCLUSIVE"
    assert disputed["status"] == "UNKNOWN_DISPUTED_ORACLE"
    assert disputed["selected_identity"]["baseline"] == [0, 21, 0, 0]
    assert disputed["selected_identity"]["candidate"] == [0, 21, 0, 0]


def test_disputed_timeout_without_after_last_is_inconclusive():
    candidate = evidence()
    drag = next(entry for entry in candidate["inputs"] if entry["tag"] == "drag_select")
    drag["result"] = "FAIL_NO_EFFECT"
    drag["timeout_cause"] = "FAIL_NO_EFFECT"
    drag["after"] = {"wait": "not observed", "tick": None}
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["stages"]["drag_select"]["status"] == "INCONCLUSIVE"


def test_disputed_minimap_timeout_reads_camera_from_after_last():
    baseline = evidence()
    candidate = evidence()
    for item in (baseline, candidate):
        minimap = next(entry for entry in item["inputs"] if entry["tag"] == "minimap")
        minimap["result"] = "FAIL_NO_EFFECT"
        minimap["timeout_cause"] = "FAIL_NO_EFFECT"
        minimap["after"] = {
            "wait": "not observed",
            "last": {"camera": [81, 0], "tick": None},
            "tick": None,
        }
    report = compare.compare_evidence(baseline, candidate)
    disputed = report["stages"]["minimap"]
    assert report["status"] == "INCONCLUSIVE"
    assert disputed["status"] == "UNKNOWN_DISPUTED_ORACLE"
    assert disputed["camera_destination"] == {"baseline": [81, 0], "candidate": [81, 0]}


@pytest.mark.parametrize("classification", sorted(compare._DISPUTED_SOURCE_RESULTS))
def test_producer_timeout_classifications_are_disputed_not_pass(classification):
    candidate = evidence()
    minimap = next(item for item in candidate["inputs"] if item["tag"] == "minimap")
    minimap["result"] = classification
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["stages"]["minimap"]["status"] == "UNKNOWN_DISPUTED_ORACLE"


def test_disputed_source_results_match_current_producer_vocabulary():
    assert set(compare._DISPUTED_SOURCE_RESULTS) == _producer_timeout_classifications()


def test_hard_fail_is_card_fail():
    candidate = evidence()
    minimap = next(item for item in candidate["inputs"] if item["tag"] == "minimap")
    minimap["result"] = "FAIL"
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "FAIL"
    assert report["stages"]["minimap"]["status"] == "FAIL"


@pytest.mark.parametrize("result", ["BLOCKED", "SKIP", "UNKNOWN_NOT_FROM_PRODUCER", None])
def test_unrecognized_or_missing_result_is_inconclusive(result):
    candidate = evidence()
    minimap = next(item for item in candidate["inputs"] if item["tag"] == "minimap")
    if result is None:
        del minimap["result"]
    else:
        minimap["result"] = result
    report = compare.compare_evidence(evidence(), candidate)
    assert report["status"] == "INCONCLUSIVE"
    assert report["stages"]["minimap"]["status"] == "INCONCLUSIVE"
