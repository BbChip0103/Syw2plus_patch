"""lap213 middle-tier independent probe: F6 producer-symmetry review.

No game run.  Extracts the *verbatim source* of both selector input recorder
closures (baseline ``g1_baseline.input_record`` and candidate
``g1_presentation_trace.record_input``), executes the candidate closure source
against the real ``_g1_selector_flow``, and feeds the produced records through
the real comparator tag reader that F5/F4 use.  A negative control reproduces
the pre-repair untagged ``OBSERVED`` stub shape.

Run from the repository root:  .venv/bin/python docs/history/laps/probes/20260912_lap213_f6_producer_review_probe.py
"""
from __future__ import annotations

import ast
import json
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools import compare_g1_stage_b as comparator  # noqa: E402
from tools import runtime_env  # noqa: E402

SOURCE = Path("tools/runtime_env.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)
TOP = {node.name: node for node in TREE.body if isinstance(node, ast.FunctionDef)}


def closures(function: ast.FunctionDef) -> dict[str, str]:
    return {
        node.name: ast.get_source_segment(SOURCE, node)
        for node in ast.walk(function)
        if isinstance(node, ast.FunctionDef) and node is not function
    }


def selector_state(name: str) -> dict[str, object]:
    return {
        "multiplayer": 1 if name == "multiplayer" else 0,
        "solo": 1 if name == "solo" else 0,
        "selected": name,
    }


def run_branch(candidate_source: str, initial: str) -> dict[str, object]:
    inputs: list[dict[str, object]] = []
    flushes: list[int] = []
    namespace: dict[str, object] = {
        "_g1_record_selector_input": runtime_env._g1_record_selector_input,
        "inputs": inputs,
        "content_crop": (37, 41, 1600, 1200),
        "input_scale": (2.0, 2.0),
        "flush_input_stage": lambda: flushes.append(len(inputs)),
        "Any": object,
    }
    exec(textwrap.dedent(candidate_source), namespace)  # noqa: S102 - verbatim repo source
    state = {"ps": 7, "selector": selector_state(initial)}
    counter = iter(range(100))

    def read_state() -> dict[str, object]:
        return dict(state)

    def wait_for(predicate, message):  # type: ignore[no-untyped-def]
        assert predicate(state), message
        return dict(state)

    def click(tag: str, _point: tuple[int, int]) -> None:
        if tag == "multiplayer_mode":
            state["selector"] = selector_state("multiplayer")
        if tag == "solo_mode":
            state["selector"] = selector_state("solo")

    def capture_neutral(tag: str) -> dict[str, object]:
        return {"tag": tag, "sha256": f"sha{next(counter)}",
                "cursor_content": list(runtime_env.G1_NEUTRAL_POINT)}

    runtime_env._g1_selector_flow(read_state, wait_for, click, capture_neutral,
                                  namespace["record_input"])
    _by_tag, input_errors = comparator._inputs_by_tag({"inputs": inputs})
    return {
        "initial_selector": initial,
        "tags": [item.get("tag") for item in inputs],
        "results": [item.get("result") for item in inputs],
        "untagged_records": [item for item in inputs if not isinstance(item.get("tag"), str)],
        "flush_calls": flushes,
        "comparator_input_errors": input_errors,
        "last_record_keys": sorted(inputs[-1].keys()),
        "last_geometry": {"content": inputs[-1]["content"], "x11": inputs[-1]["x11"],
                          "scale": inputs[-1]["scale"]},
    }


def main() -> int:
    baseline_closures = closures(TOP["g1_baseline"])
    candidate_closures = closures(TOP["g1_presentation_trace"])
    baseline_recorder = baseline_closures["input_record"]
    candidate_recorder = candidate_closures["record_input"]
    normalized_baseline = textwrap.dedent(baseline_recorder).replace("input_record", "RECORDER", 1)
    normalized_candidate = textwrap.dedent(candidate_recorder).replace("record_input", "RECORDER", 1)

    report = {
        "probe": "lap213_f6_producer_review",
        "game_runs": 0,
        "recorder_bodies_identical_modulo_name": normalized_baseline == normalized_candidate,
        "baseline_recorder_source": baseline_recorder,
        "candidate_recorder_source": candidate_recorder,
        "branches": [run_branch(candidate_recorder, initial) for initial in ("solo", "multiplayer")],
        "negative_control_untagged_stub": comparator._inputs_by_tag(
            {"inputs": [{"args": ["solo_mode_setup", 462, 169], "result": "OBSERVED"}]}
        )[1],
        "comparator_stages": list(comparator.STAGES),
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
