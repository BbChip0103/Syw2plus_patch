#!/usr/bin/env python3
"""lap328 middle probe — independent pre-execution review of the lap327 G1-R1 implementation.

Read-only with respect to the game: no Wine, no Xvfb, no click, no game process, no patching.
The only code executed is the harness itself with synthetic readers.

Questions this probe answers (docs/work/active/G1_R1_MIDDLE_ENVELOPE_LAP326.md section 5 and 4):
  1. Does the implementation satisfy the structural clauses F1..F8 and P1?
  2. Do the four declared failure modes actually come out distinguishable in the record?

Every check appends to `failures` as it runs and the report is assembled from whatever ran,
so a missing site cannot raise before the JSON is emitted (the N4 pre-evaluation trap).
`failures` holds contract violations of the probe's own assertions; `findings` holds defects
the probe demonstrates by evaluating the shipped code, which is the point of the review.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
RUNTIME_ENV = REPO / "tools" / "runtime_env.py"
R1_TESTS = REPO / "tests" / "test_lap326_r1_load_origin.py"

# SHA256 recorded by the lap327 work record for the files under review.
EXPECTED_SHA = {
    "tools/runtime_env.py":
        "0d5a06063eae584540e310be10f82fe71527d8a6f52f005c0d6df8221f1698d3",
    "tests/test_lap326_r1_load_origin.py":
        "ef2ab3968ad11ddf880372ab4783258762eb86bc32dc7a95f020363db9575c9a",
}
FORBIDDEN_TOKENS = ("process_vm_writev", "ptrace", "winedbg", "PTRACE_", "int3")
PRODUCTION_COMMANDS = ("prepare", "check", "smoke", "g1-baseline", "g1-presentation-trace")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def called_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            if isinstance(sub.func, ast.Name):
                names.add(sub.func.id)
            elif isinstance(sub.func, ast.Attribute):
                names.add(sub.func.attr)
    return names


def check_read_shapes(env: Any, report: dict[str, Any], failures: list[str]) -> None:
    """F3: the origin sample is one contiguous six-byte read; PS is a signed WORD."""
    calls: list[list[int]] = []

    def reader(address: int, size: int) -> bytes:
        calls.append([address, size])
        payload = {
            (env.G1_R1_ORIGIN_ADDRESS, 6): b"\xf0\x00\x91\x00\x08\x00",
            (env.G1_R1_PROGRAM_STATE_ADDRESS, 2): b"\x23\x00",
            (env.G1_R1_PROGRAM_STATE_ADDRESS, 4): b"\x23\x00\x00\x00",
            (env.G1_R1_PENDING_STATE_ADDRESS, 2): b"\x22\x00",
        }
        return payload[(address, size)]

    origin = env._g1_r1_read_origin(reader)
    state = env._g1_r1_read_wait_state(reader)
    report["F3_read_shapes"] = {
        "origin_calls": [c for c in calls if c[1] == 6],
        "origin_value": origin,
        "wait_state_calls": [c for c in calls if c[1] != 6],
        "wait_state_value": state,
        "wait_ps_states": list(env.G1_R1_WAIT_PS_STATES),
    }
    if calls[0] != [env.G1_R1_ORIGIN_ADDRESS, 6] or len([c for c in calls if c[1] == 6]) != 1:
        failures.append(f"F3: origin sample is not a single 6-byte read: {calls}")
    if origin != {"x": 240, "y": 145, "tag": 8}:
        failures.append(f"F3: origin unpack changed: {origin}")
    if state["ps"] != 35 or state["ps_word"] != 35 or state["ps_dword"] != 35:
        failures.append(f"F3: PS word/dword decode changed: {state}")
    if tuple(env.G1_R1_WAIT_PS_STATES) != (9, 35):
        failures.append(f"F4: wait states are {env.G1_R1_WAIT_PS_STATES}, not (9, 35)")


def check_structure(tree: ast.Module, report: dict[str, Any], failures: list[str]) -> None:
    """F1/F2/F4/F5/F8: isolation of the research lane from the production G1 path."""
    fn = find_function(tree, "g1_r1_load_origin")
    if fn is None:
        failures.append("F1: g1_r1_load_origin is missing")
        return
    calls = called_names(fn)
    source = RUNTIME_ENV.read_text(encoding="utf-8")
    lambdas = [ast.unparse(node) for node in ast.walk(fn) if isinstance(node, ast.Lambda)]
    clicks = [node for node in ast.walk(fn) if isinstance(node, ast.Call)
              and ast.unparse(node.func) == "subprocess.run"
              and "x11_mouse_click.py" in ast.unparse(node)]
    report["F1_F5_isolation"] = {
        "production_commands_still_dispatched":
            [c for c in PRODUCTION_COMMANDS if f'"{c}"' in source],
        "calls_g1_flush_input_stage": "_g1_flush_input_stage" in calls,
        "calls_capture_screenshot": "_capture_screenshot" in calls,
        "writes_json_paths": sorted(
            set(re.findall(r"output / ['\"]([a-z0-9_.]+)['\"]", ast.unparse(fn)))),
        "raw_read_import": "from patches.population.runtime_driver import read as read_memory"
                           in ast.unparse(fn),
        "wait_predicates": lambdas,
        "click_injection_sites": len(clicks),
    }
    if len(report["F1_F5_isolation"]["production_commands_still_dispatched"]) != len(PRODUCTION_COMMANDS):
        failures.append("F1: a production subcommand disappeared from the dispatcher")
    if "_g1_flush_input_stage" in calls:
        failures.append("F5: the research lane feeds the production input-evidence path")
    if not report["F1_F5_isolation"]["raw_read_import"]:
        failures.append("F2: the research lane does not use runtime_driver.read as its only reader")
    for text in lambdas:
        if "G1_R1_WAIT_PS_STATES" not in text:
            failures.append(f"F4: a wait predicate does not reference the declared constant: {text}")
    if len(clicks) != 1:
        failures.append(f"F8: expected exactly one click injection site, found {len(clicks)}")
    tokens = {token: sorted(
        p.relative_to(REPO).as_posix()
        for p in (REPO / "tools").rglob("*.py")
        if token in p.read_text(encoding="utf-8", errors="replace"))
        for token in FORBIDDEN_TOKENS}
    report["F2_forbidden_tokens"] = tokens
    for token, hits in tokens.items():
        if hits:
            failures.append(f"F2: forbidden instrumentation token {token} appears in {hits}")


def check_precondition(tree: ast.Module, report: dict[str, Any], failures: list[str]) -> None:
    """P1: a PS=9 origin other than (0, 0, 0) must be preserved as a blocker, not clicked past."""
    fn = find_function(tree, "g1_r1_load_origin")
    if fn is None:
        return
    text = ast.unparse(fn)
    guarded = "if not evidence['precondition']['pass']:" in text
    report["P1_precondition"] = {
        "expected_origin_declared": "'expected_origin': [0, 0, 0]" in text,
        "guards_click_on_failure": guarded,
        "blocked_classification": "BLOCKED_PRECONDITION" in text,
    }
    if not all(report["P1_precondition"].values()):
        failures.append(f"P1: precondition handling incomplete: {report['P1_precondition']}")


def check_mode_mapping(tree: ast.Module, report: dict[str, Any], failures: list[str]) -> None:
    """Finding D1: evaluate the shipped classifier for a post-click collection failure."""
    fn = find_function(tree, "g1_r1_load_origin")
    if fn is None:
        return
    assign: ast.If | None = None
    for node in ast.walk(fn):
        if isinstance(node, ast.If) and "mode = " in ast.unparse(node) and "count" in ast.unparse(node):
            assign = node
    if assign is None:
        failures.append("D1: the failure-mode assignment could not be located")
        return
    code = ast.unparse(assign)
    outcomes: dict[str, str] = {}
    for label, evidence in (
        ("before_click", {"input": {"count": 0}}),
        ("after_click_post_missing", {"input": {"count": 1}}),
        ("after_click_post_present", {"input": {"count": 1}, "post": {"x": 0}}),
    ):
        scope: dict[str, Any] = {"evidence": evidence}
        exec(compile(ast.Module(body=[assign], type_ignores=[]), "<mode>", "exec"), scope)
        outcomes[label] = scope["mode"]
    body = ast.unparse(fn)
    post_read = body.index("post = _g1_r1_read_origin(read_for_process)")
    count_set = body.index("'count': 1")
    post_store = body.index("evidence['post'] =")
    report["D1_mode_mapping"] = {
        "source": code,
        "outcomes": outcomes,
        "post_read_is_after_click_and_before_post_store":
            count_set < post_read < post_store,
        "raising_statements_between":
            ["_g1_r1_read_origin -> OSError/ValueError from runtime_driver.read"],
    }
    if outcomes["after_click_post_missing"] != "TIMEOUT":
        report["D1_mode_mapping"]["note"] = "mapping changed since lap327; re-review"
    if not (count_set < post_read < post_store):
        failures.append("D1: could not establish that the post origin read is the reachable raiser")


def check_wait_classification(env: Any, report: dict[str, Any], failures: list[str]) -> None:
    """Finding D2: with no stage budget every non-reach outcome collapses to one class."""
    def never(_detailed: bool) -> dict[str, Any]:
        return {"ps": 7}

    def unreadable(_detailed: bool) -> dict[str, Any]:
        raise OSError(5, "read 1:4ed818, got -1/2")

    results: dict[str, str] = {}
    for label, reader, kwargs in (
        ("no_stage_budget_never_reached", never, {}),
        ("no_stage_budget_all_reads_failed", unreadable, {}),
        ("stage_budget_never_reached", never, {"stage_budget": 0.2}),
    ):
        started = __import__("time").monotonic()
        extra = dict(kwargs)
        if "stage_budget" in extra:
            extra["stage_started"] = started
        try:
            env._wait_state(reader, lambda item: item.get("ps") == 35, started,
                            30.0 if extra else 0.3, "probe wait", stage="probe", **extra)
        except env._G1WaitTimeout as exc:
            results[label] = exc.classification
        else:
            results[label] = "UNEXPECTED_SUCCESS"
    report["D2_wait_classification"] = {
        "observed": results,
        "r1_uses_stage_budget": False,
    }
    if results["stage_budget_never_reached"] != "FAIL_NO_EFFECT":
        failures.append(f"D2: staged control case changed: {results}")
    if results["no_stage_budget_never_reached"] != "UNKNOWN_BUDGET_EXHAUSTED":
        report["D2_wait_classification"]["note"] = "collapse no longer reproduces; re-review"


def check_test_adequacy(report: dict[str, Any], failures: list[str]) -> None:
    """F7: do the synthetic checks exercise the classifier, or only echo their own argument?"""
    tree = ast.parse(R1_TESTS.read_text(encoding="utf-8"))
    tautological: list[str] = []
    exercised: list[str] = []
    for fn in [n for n in tree.body if isinstance(n, ast.FunctionDef)]:
        text = ast.unparse(fn)
        asserted = set(re.findall(r"record\['classification'\] == '([A-Z_]+)'", text))
        supplied = set(re.findall(r"_failure\('([A-Z_]+)'", text))
        if asserted and asserted <= supplied:
            tautological.append(fn.name)
        elif asserted:
            exercised.append(fn.name)
    report["F7_test_adequacy"] = {
        "tautological_mode_tests": sorted(tautological),
        "classifier_exercising_tests": sorted(exercised),
        "real_entrypoint_monkeypatched": "monkeypatch.setattr(runtime_env, 'g1_r1_load_origin'"
                                         in ast.unparse(tree),
    }


def main() -> int:
    failures: list[str] = []
    report: dict[str, Any] = {"probe": Path(__file__).name, "lap": 328,
                              "role": "middle pre-execution review of lap327 work"}
    files = {name: sha256(REPO / name) for name in EXPECTED_SHA}
    report["files"] = files
    for name, digest in files.items():
        if digest != EXPECTED_SHA[name]:
            failures.append(f"file under review changed: {name} is {digest}")

    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from tools import runtime_env as env

    tree = ast.parse(RUNTIME_ENV.read_text(encoding="utf-8"))
    check_read_shapes(env, report, failures)
    check_structure(tree, report, failures)
    check_precondition(tree, report, failures)
    check_mode_mapping(tree, report, failures)
    check_wait_classification(env, report, failures)
    check_test_adequacy(report, failures)

    report["findings"] = [
        "D1: after the single click, any OSError/ValueError from the post origin read is "
        "recorded as classification TIMEOUT, not COLLECTION_ERROR; the COLLECTION_ERROR arm "
        "of that branch is unreachable because nothing between the post read and the post "
        "store can raise. Envelope section 4 requires modes 3 and 4 to be distinguishable.",
        "D2: the R1 waits pass no stage_budget, so the poll loop can only exit at the run "
        "deadline and _wait_state classifies every non-reach outcome UNKNOWN_BUDGET_EXHAUSTED. "
        "Mode 1 (unreached) is unreachable and an in-poll read failure is masked in the "
        "classification field, though read_error_count and provenance survive in observation.",
        "D3: three of the four synthetic mode checks assert the classification string they "
        "themselves passed into _g1_r1_failure_record, so no test covers the D1/D2 mapping.",
    ]
    report["fail_open"] = [
        "this probe is static plus synthetic; it does not establish that the click reaches "
        "the load dialog, that pre is really (0,0,0), or that teardown closes WM_CLOSE",
        "production paths are compared by dispatcher presence and the full suite, not by a "
        "byte diff, because the repository has no commits to diff against",
        "runtime_driver.read raises OSError on a short read, so the len() guards in the R1 "
        "readers are defensive only and the synthetic short-read test shape cannot occur",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
