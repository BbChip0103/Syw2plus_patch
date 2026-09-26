"""lap216 middle-tier independent probe: does the lap215 F6-R1 guard bite?

No game run.  Re-implements the lap215 AST guard predicate independently from
``tests/test_runtime_env.py`` and applies it to the *real* producer sources
(``g1_baseline`` / ``g1_presentation_trace``) plus mutated copies.

Three control classes:
  * ``real``      - unmutated source, must report 0 violations.
  * ``negative``  - regression shapes the guard claims to block, must report >0.
  * ``gap``       - real bypass shapes the guard does NOT block (0 violations);
                    each is also executed through the real ``_g1_selector_flow``
                    and the real comparator tag reader to see whether the
                    downstream fail-closed path still catches it.

Run from the repository root:
  .venv/bin/python docs/history/laps/probes/20260912_lap216_f6_r1_guard_review_probe.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from tools import compare_g1_stage_b as comparator  # noqa: E402
from tools import runtime_env  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
SOURCE = (REPO / "tools/runtime_env.py").read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)
TOP = {node.name: node for node in TREE.body if isinstance(node, ast.FunctionDef)}


def sha256(path: str) -> str:
    return hashlib.sha256((REPO / path).read_bytes()).hexdigest()


def guard_violations(producer_source: str, recorder_name: str) -> list[str]:
    """Independent restatement of the four lap215 guard assertions."""

    failures: list[str] = []
    tree = ast.parse(textwrap.dedent(producer_source))
    recorder_defs = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == recorder_name
    ]
    if len(recorder_defs) != 1:
        return [f"recorder_defs={len(recorder_defs)}"]
    body = recorder_defs[0]

    helper_calls = [
        node for node in ast.walk(body)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "_g1_record_selector_input"
    ]
    if len(helper_calls) != 1:
        failures.append(f"helper_calls={len(helper_calls)}")
    if any(isinstance(node, ast.Constant) and node.value == "OBSERVED"
           for node in ast.walk(body)):
        failures.append("observed_stub_constant_present")

    flow_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        and node.func.id == "_g1_selector_flow"
    ]
    if not any(len(node.args) >= 5 and isinstance(node.args[4], ast.Name)
               and node.args[4].id == recorder_name for node in flow_calls):
        failures.append("flow_recorder_argument_missing")
    return failures


def recorder_segment(producer: str, recorder_name: str) -> str:
    for node in ast.walk(TOP[producer]):
        if isinstance(node, ast.FunctionDef) and node.name == recorder_name:
            segment = ast.get_source_segment(SOURCE, node)
            assert segment is not None
            return segment
    raise AssertionError(f"{producer}.{recorder_name} not found")


def reindent(block: str, indent: str) -> str:
    """Indent every line but the first: ``get_source_segment`` drops the leading indent."""

    lines = textwrap.dedent(block).strip("\n").splitlines()
    return "\n".join(
        line if index == 0 or not line.strip() else indent + line
        for index, line in enumerate(lines)
    )


def segment_indent(recorder_name: str) -> str:
    for line in SOURCE.splitlines():
        if line.lstrip().startswith(f"def {recorder_name}("):
            return line[: len(line) - len(line.lstrip())]
    raise AssertionError(f"no def line for {recorder_name}")


STUB = """
def {name}(*args) -> dict[str, Any]:
    entry = {{"args": list(args), "result": "OBSERVED"}}
    inputs.append(entry)
    return entry
"""

SILENT_BYPASS = """
def {name}(tag, x, y, before, expected, after, actual, result) -> dict[str, Any]:
    entry = {{"args": [tag, x, y], "result": result}}
    inputs.append(entry)
    return entry
"""

CONDITIONAL_BYPASS = """
def {name}(tag: str, x: int, y: int, before: object, expected: str,
           after: object, actual: str, result: str) -> dict[str, Any]:
    if tag == "solo_mode_setup":
        entry = {{"args": [tag, x, y], "result": result}}
        inputs.append(entry)
        return entry
    return _g1_record_selector_input(
        inputs, tag=tag, x=x, y=y, content_crop=content_crop, scale=input_scale,
        before=before, expected=expected, after=after, actual=actual, result=result,
        flush=flush_input_stage,
    )
"""


def mutate(producer: str, recorder_name: str, kind: str) -> str:
    source = ast.get_source_segment(SOURCE, TOP[producer])
    assert source is not None
    segment = recorder_segment(producer, recorder_name)
    indent = segment_indent(recorder_name)
    if kind == "real":
        return source
    if kind == "flow_wiring_dropped":
        mutated = source.replace(
            f"capture_neutral, {recorder_name})", "capture_neutral, lambda *a, **k: None)"
        ).replace(
            f"capture_neutral, {recorder_name},", "capture_neutral, lambda *a, **k: None,"
        )
        assert mutated != source, "flow call site pattern not found"
        return mutated
    if kind == "flush_dropped":
        return source.replace(
            segment, segment.replace("flush=flush_input_stage,", "flush=lambda: None,")
        )
    if kind == "tag_laundered":
        return source.replace(segment, segment.replace("tag=tag,", "tag=None,"))
    template = {"observed_stub": STUB, "silent_bypass": SILENT_BYPASS,
                "conditional_bypass": CONDITIONAL_BYPASS}[kind]
    return source.replace(segment, reindent(template.format(name=recorder_name), indent))


def selector_state(name: str) -> dict[str, object]:
    return {"multiplayer": 1 if name == "multiplayer" else 0,
            "solo": 1 if name == "solo" else 0, "selected": name}


def run_recorder(producer_source: str, recorder_name: str) -> dict[str, object]:
    """Drive the (possibly mutated) recorder through the real selector flow."""

    inputs: list[dict[str, object]] = []
    flushes: list[int] = []
    segment = None
    for node in ast.walk(ast.parse(textwrap.dedent(producer_source))):
        if isinstance(node, ast.FunctionDef) and node.name == recorder_name:
            segment = ast.get_source_segment(textwrap.dedent(producer_source), node)
    assert segment is not None
    namespace: dict[str, object] = {
        "_g1_record_selector_input": runtime_env._g1_record_selector_input,
        "inputs": inputs, "content_crop": (37, 41, 1600, 1200),
        "input_scale": (2.0, 2.0),
        "flush_input_stage": lambda: flushes.append(len(inputs)), "Any": object,
    }
    exec(textwrap.dedent(segment), namespace)  # noqa: S102 - repo source under test
    state = {"ps": 7, "selector": selector_state("multiplayer")}
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

    error: str | None = None
    try:
        runtime_env._g1_selector_flow(read_state, wait_for, click, capture_neutral,
                                      namespace[recorder_name])
    except Exception as exc:  # noqa: BLE001 - classification is the observation
        error = f"{type(exc).__name__}: {exc}"
    _by_tag, input_errors = comparator._inputs_by_tag({"inputs": inputs})
    return {
        "records": len(inputs),
        "tags": [item.get("tag") for item in inputs],
        "untagged_records": sum(1 for item in inputs if not isinstance(item.get("tag"), str)),
        "flush_calls": len(flushes),
        "comparator_input_errors": input_errors,
        "runtime_error": error,
    }


CASES = [
    ("real", "real", "unmutated repository source"),
    ("observed_stub", "negative", "lap211/212 pre-repair untagged OBSERVED stub"),
    ("silent_bypass", "negative", "direct inputs.append bypass without the OBSERVED literal"),
    ("flow_wiring_dropped", "negative", "selector flow no longer receives the named recorder"),
    ("conditional_bypass", "gap", "one untagged branch, helper still called exactly once"),
    ("flush_dropped", "gap", "helper called but per-record flush disabled"),
    ("tag_laundered", "gap", "helper called with tag=None"),
]

PRODUCERS = [("g1_baseline", "input_record"), ("g1_presentation_trace", "record_input")]


def main() -> int:
    results = []
    for producer, recorder_name in PRODUCERS:
        for kind, expectation, note in CASES:
            mutated = mutate(producer, recorder_name, kind)
            assert kind == "real" or mutated != ast.get_source_segment(SOURCE, TOP[producer]), (
                f"mutation {kind} did not change {producer}")
            violations = guard_violations(mutated, recorder_name)
            entry: dict[str, object] = {
                "producer": producer, "recorder": recorder_name, "mutation": kind,
                "class": expectation, "note": note,
                "guard_violations": violations,
                "guard_blocks": bool(violations),
            }
            if expectation in {"real", "gap"} and producer == "g1_presentation_trace":
                entry["runtime_effect"] = run_recorder(mutated, recorder_name)
            entry["verdict"] = (
                "OK" if (expectation == "negative") == bool(violations) else "UNEXPECTED"
            )
            results.append(entry)

    report = {
        "probe": "lap216_f6_r1_guard_review",
        "game_runs": 0,
        "source_sha256": {
            path: sha256(path) for path in
            ("tools/runtime_env.py", "tests/test_runtime_env.py", "tools/compare_g1_stage_b.py")
        },
        "cases": results,
        "summary": {
            "negative_controls_blocked": sum(
                1 for item in results if item["class"] == "negative" and item["guard_blocks"]),
            "negative_controls_total": sum(1 for item in results if item["class"] == "negative"),
            "gap_controls_unblocked": sum(
                1 for item in results if item["class"] == "gap" and not item["guard_blocks"]),
            "gap_controls_total": sum(1 for item in results if item["class"] == "gap"),
            "real_sources_clean": all(
                not item["guard_blocks"] for item in results if item["class"] == "real"),
            "unexpected": [item["mutation"] for item in results if item["verdict"] == "UNEXPECTED"],
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
