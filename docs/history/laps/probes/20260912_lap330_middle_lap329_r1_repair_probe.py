#!/usr/bin/env python3
"""lap330 middle probe — independent review of the lap329 repair of D1/D1b/D2/D3.

Read-only with respect to the game: no Wine, no Xvfb, no click, no game process, no
patching, no write to any memory.  The only code executed is the harness itself with
synthetic readers, plus one deliberately failing `process_vm_readv` against *this*
process at address 0 so that the real read-error shape is observed rather than copied
by hand from the implementation under review.

Questions answered (docs/work/active/G1_R1_MIDDLE_IMPLEMENTATION_REVIEW_LAP328.md):
  R-a/D1/D1b  does a post-click origin read failure now land in COLLECTION_ERROR with
              errno / requested_size / actual_size / site as separate fields?
  R-b/D2      do the two R1 waits actually carry the declared stage budgets, and do the
              four modes come out as four different classifications when the real
              classifier runs?
  R-c/D3      do the synthetic tests reach the real classifier instead of asserting a
              string they injected themselves?
  R-d         are F1..F8 / P1 and the shared-code invariants still intact?

Every check appends to `failures` (probe-contract violations) or `findings` (defects
demonstrated by evaluating the shipped code) as it runs, and the report is assembled
from whatever ran, so a missing site cannot raise before the JSON is emitted (N4 trap).
This probe does not assert the SHA of its own stdout and does not import any earlier
lap probe.
"""

from __future__ import annotations

import ast
import ctypes
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
RUNTIME_ENV = REPO / "tools" / "runtime_env.py"
R1_TESTS = REPO / "tests" / "test_lap326_r1_load_origin.py"

# SHA256 recorded by the lap329 work record for the files under review.  A mismatch
# means the artifact moved under this review and the verdict does not apply.
EXPECTED_SHA = {
    "tools/runtime_env.py":
        "997ff15b13115ccebd9d8832b3b066add589b755d9cc6e8a77d987696cc46eed",
    "tests/test_lap326_r1_load_origin.py":
        "81acc11eab97cc04b797724360a81561a227c8454571290782f611aa936cac72",
}
FORBIDDEN_TOKENS = ("process_vm_writev", "ptrace", "PTRACE_", "winedbg", "int3")
PRODUCTION_COMMANDS = ("prepare", "check", "smoke", "g1-baseline", "g1-presentation-trace")
PRODUCTION_STAGE_BUDGET_KEYS = ("drag_select", "minimap", "unit_select")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_function(tree: ast.Module, name: str) -> ast.FunctionDef | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    return None


def called_names(node: ast.AST) -> list[str]:
    names: list[str] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            if isinstance(sub.func, ast.Name):
                names.append(sub.func.id)
            elif isinstance(sub.func, ast.Attribute):
                names.append(sub.func.attr)
    return names


class FakeClock:
    """Stand-in for the `time` module so waits are deterministic and instant."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


# --------------------------------------------------------------------------- A
def check_artifacts(report: dict[str, Any], failures: list[str]) -> None:
    observed = {
        "tools/runtime_env.py": sha256(RUNTIME_ENV),
        "tests/test_lap326_r1_load_origin.py": sha256(R1_TESTS),
    }
    report["A_artifacts"] = {
        "observed_sha256": observed,
        "expected_sha256": EXPECTED_SHA,
        "match": observed == EXPECTED_SHA,
    }
    if observed != EXPECTED_SHA:
        failures.append("A: artifact SHA does not match the lap329 work record")


# --------------------------------------------------------------------------- B
def check_call_sites(tree: ast.Module, report: dict[str, Any], failures: list[str]) -> None:
    """R-b: the declared budgets must be at the R1 call sites, not in the shared dict."""

    func = find_function(tree, "g1_r1_load_origin")
    sites: list[dict[str, Any]] = []
    if func is None:
        failures.append("B: g1_r1_load_origin not found")
    else:
        for sub in ast.walk(func):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
                    and sub.func.id == "_wait_state":
                sites.append({
                    keyword.arg: ast.unparse(keyword.value)
                    for keyword in sub.keywords if keyword.arg is not None
                })
    report["B_wait_call_sites"] = sites
    expected = [
        {"stage": "'r1_ps9'", "stage_budget": "G1_R1_PS9_STAGE_BUDGET",
         "stage_started": "started"},
        {"stage": "'r1_ps35'", "stage_budget": "G1_R1_PS35_STAGE_BUDGET",
         "stage_started": "ps35_stage_started"},
    ]
    observed = [
        {key: site.get(key) for key in ("stage", "stage_budget", "stage_started")}
        for site in sites
    ]
    report["B_wait_call_sites_expected"] = expected
    report["B_wait_call_sites_match"] = observed == expected
    if observed != expected:
        failures.append("B: R1 wait call sites do not carry the declared stage budgets")


def check_shared_invariants(
    env: Any, tree: ast.Module, report: dict[str, Any], failures: list[str],
) -> None:
    """R-b/R-d: the shared wait and the production budget dict must be untouched."""

    wait = find_function(tree, "_wait_state")
    wait_source = ast.unparse(wait) if wait is not None else ""
    r1_tokens = sorted({
        token for token in ("r1_ps9", "r1_ps35", "G1_R1_", "_g1_r1_")
        if token in wait_source
    })
    budgets = dict(getattr(env, "G1_INPUT_STAGE_BUDGETS", {}))
    report["B_shared_invariants"] = {
        "wait_state_found": wait is not None,
        "r1_tokens_inside_wait_state": r1_tokens,
        "stage_budget_keys": sorted(budgets),
        "stage_budget_total": round(sum(budgets.values()), 6),
        "ps9_budget": getattr(env, "G1_R1_PS9_STAGE_BUDGET", None),
        "ps35_budget": getattr(env, "G1_R1_PS35_STAGE_BUDGET", None),
    }
    if r1_tokens:
        failures.append("B: _wait_state body mentions R1-specific names")
    if sorted(budgets) != list(PRODUCTION_STAGE_BUDGET_KEYS):
        failures.append("B: G1_INPUT_STAGE_BUDGETS keys changed")
    if (getattr(env, "G1_R1_PS9_STAGE_BUDGET", None),
            getattr(env, "G1_R1_PS35_STAGE_BUDGET", None)) != (40.0, 20.0):
        failures.append("B: R1 stage budgets are not the declared 40s/20s")


def check_mode_separation(env: Any, report: dict[str, Any], failures: list[str]) -> None:
    """R-b/R-c: run the real classifier and show the four modes are four values."""

    real_time = env.time
    observed: dict[str, dict[str, Any]] = {}
    try:
        scenarios = [
            # name, timeout, stage, budget, stage_started, reader behaviour
            ("ps9_unreached_within_stage", 90.0, "r1_ps9", 40.0, 0.0, "never"),
            ("ps35_unreached_within_stage", 90.0, "r1_ps35", 20.0, 45.0, "never"),
            ("ps35_run_deadline_exhausted", 90.0, "r1_ps35", 20.0, 85.0, "never"),
            ("ps35_all_reads_fail", 90.0, "r1_ps35", 20.0, 45.0, "raise"),
            ("ps35_reached", 90.0, "r1_ps35", 20.0, 45.0, "reach"),
            # control: the lap328 shape, no stage budget at all
            ("control_no_stage_budget", 90.0, "r1_ps35", None, None, "never"),
        ]
        for name, timeout, stage, budget, stage_started, behaviour in scenarios:
            clock = FakeClock(stage_started if stage_started is not None else 0.0)
            env.time = clock

            def read_state(_detailed: bool, behaviour: str = behaviour) -> dict[str, Any]:
                if behaviour == "raise":
                    raise OSError(14, "read 4242:1088b5c, got -1/6")
                return {"ps": 35 if behaviour == "reach" else 7}

            entry: dict[str, Any] = {"behaviour": behaviour, "stage_budget": budget}
            try:
                returned = env._wait_state(
                    read_state, lambda item: item.get("ps") == 35,
                    0.0, timeout, "probe wait", stage=stage,
                    stage_budget=budget, stage_started=stage_started,
                )
            except env._G1WaitTimeout as exc:
                record = env._g1_r1_wait_failure_record(exc)
                entry.update({
                    "outcome": "timeout",
                    "wait_classification": exc.classification,
                    "r1_mode": record["classification"],
                    "r1_status": record["status"],
                    "remaining_budget_after": exc.observation.get("remaining_budget_after"),
                    "poll_count": exc.observation.get("poll_count"),
                    "read_error_count": exc.observation.get("read_error_count"),
                    "run_deadline_clamped": exc.observation.get("run_deadline_clamped"),
                    "window_truncated": exc.observation.get("window_truncated"),
                })
            else:
                entry.update({"outcome": "reached", "returned_ps": returned.get("ps")})
            observed[name] = entry
    finally:
        env.time = real_time

    # mode 2 comes from the comparator, not from a wait
    reached_unchanged = env._g1_r1_compare_origin(
        {"x": 0, "y": 0, "tag": 0}, {"x": 0, "y": 0, "tag": 0},
    )
    reached_changed = env._g1_r1_compare_origin(
        {"x": 0, "y": 0, "tag": 0}, {"x": 240, "y": 145, "tag": 8},
    )
    modes = {
        "mode1_unreached": observed.get("ps35_unreached_within_stage", {}).get("r1_mode"),
        "mode2_reached_unchanged": reached_unchanged.get("classification"),
        "mode3_timeout": observed.get("ps35_run_deadline_exhausted", {}).get("r1_mode"),
        "mode4_collection_error": observed.get("ps35_all_reads_fail", {}).get("r1_mode"),
    }
    report["B_mode_separation"] = {
        "observed": observed,
        "modes": modes,
        "distinct_mode_values": len(set(modes.values())),
        "reached_changed_status": reached_changed.get("status"),
        "reached_unchanged_status": reached_unchanged.get("status"),
    }
    expected_modes = {
        "mode1_unreached": "UNREACHED",
        "mode2_reached_unchanged": "REACHED_UNCHANGED",
        "mode3_timeout": "TIMEOUT",
        "mode4_collection_error": "COLLECTION_ERROR",
    }
    if modes != expected_modes:
        failures.append(f"B: four failure modes are not separable: {modes}")
    if observed.get("ps9_unreached_within_stage", {}).get("r1_mode") != "UNREACHED":
        failures.append("B: the PS9 stage budget does not produce UNREACHED")
    if observed.get("ps35_reached", {}).get("outcome") != "reached":
        failures.append("B: a reaching predicate did not return")
    if reached_changed.get("status") != "OBSERVED":
        failures.append("B: a changed origin is not reported as OBSERVED")


# --------------------------------------------------------------------------- C
def check_collection_error(env: Any, report: dict[str, Any], failures: list[str]) -> None:
    """R-a/D1b: use a real process_vm_readv failure, not a hand-copied string."""

    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from patches.population import runtime_driver

    ctypes.set_errno(0)
    real_error: OSError | None = None
    try:
        runtime_driver.read(0, 0, env.G1_R1_ORIGIN_READ_SIZE)
    except OSError as exc:  # expected: reading address 0 of pid 0 cannot succeed
        real_error = exc
    entry: dict[str, Any] = {
        "real_read_raised": real_error is not None,
        "real_message": str(real_error) if real_error is not None else None,
        "real_errno_is_int": isinstance(getattr(real_error, "errno", None), int),
    }
    if real_error is None:
        failures.append("C: a read of pid 0 address 0 unexpectedly succeeded")
    else:
        def failing_read(address: int, size: int) -> bytes:
            raise real_error

        records: dict[str, Any] = {}
        for site in ("pre", "post"):
            try:
                env._g1_r1_read_origin_checked(failing_read, site=site)
            except env._G1R1CollectionError as exc:
                record = env._g1_r1_collection_failure_record(
                    exc, evidence={"input": {"count": 1 if site == "post" else 0}},
                )
                diagnostics = record.get("observation", {}).get("collection_error", {})
                records[site] = {
                    "status": record.get("status"),
                    "classification": record.get("classification"),
                    "errno": diagnostics.get("errno"),
                    "requested_size": diagnostics.get("requested_size"),
                    "actual_size": diagnostics.get("actual_size"),
                    "site": diagnostics.get("site"),
                    "exception_type": diagnostics.get("exception_type"),
                    "fields_present": sorted(diagnostics),
                }
        entry["records"] = records
        for site, record in records.items():
            if record["classification"] != "COLLECTION_ERROR":
                failures.append(f"C: {site} read failure is not COLLECTION_ERROR")
            if not isinstance(record["errno"], int):
                failures.append(f"C: {site} record lost errno")
            if record["requested_size"] != env.G1_R1_ORIGIN_READ_SIZE:
                failures.append(f"C: {site} record lost the requested size")
            if record["actual_size"] != -1:
                failures.append(f"C: {site} record lost the actual short-read length")
            if (record["site"] or {}).get("phase") != site:
                failures.append(f"C: {site} record lost the site phase")
        if sorted(records) != ["post", "pre"]:
            failures.append("C: not both origin sites were exercised")
    report["C_collection_error"] = entry


def check_post_failure_routing(
    tree: ast.Module, report: dict[str, Any], report_findings: list[str],
    failures: list[str],
) -> None:
    """D1: statements after the click must not be able to reach the generic handler."""

    func = find_function(tree, "g1_r1_load_origin")
    handlers: list[str] = []
    origin_read_calls: list[str] = []
    generic_ternary_present = False
    if func is None:
        failures.append("D1: g1_r1_load_origin not found")
    else:
        for sub in ast.walk(func):
            if isinstance(sub, ast.Try):
                for handler in sub.handlers:
                    handlers.append(ast.unparse(handler.type) if handler.type else "bare")
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \
                    and sub.func.id in {"_g1_r1_read_origin", "_g1_r1_read_origin_checked"}:
                origin_read_calls.append(ast.unparse(sub))
            if isinstance(sub, ast.IfExp) and "post" in ast.unparse(sub):
                generic_ternary_present = True
    report["D1_routing"] = {
        "handler_order": handlers,
        "origin_read_calls": sorted(origin_read_calls),
        "generic_handler_post_ternary_present": generic_ternary_present,
    }
    dedicated_first = any("_G1R1CollectionError" in item for item in handlers)
    if not dedicated_first:
        failures.append("D1: no dedicated _G1R1CollectionError handler")
    if any(call.startswith("_g1_r1_read_origin(") for call in origin_read_calls):
        failures.append("D1: an origin read bypasses the checked wrapper")
    if generic_ternary_present:
        report_findings.append(
            "D1 residual (not a regression): the generic handler still carries the "
            "`COLLECTION_ERROR if evidence.get('post') is not None else TIMEOUT` ternary. "
            "It is now dead for read failures because the post read raises "
            "_G1R1CollectionError, which an earlier handler catches, but the dead branch "
            "remains a latent trap: any future statement added after the click that raises "
            "OSError/ValueError before evidence['post'] is set would be recorded TIMEOUT.",
        )


# --------------------------------------------------------------------------- D
def check_test_adequacy(report: dict[str, Any], failures: list[str]) -> None:
    """R-c/D3: every mode test must call the real classifier, not restate its input."""

    tree = ast.parse(R1_TESTS.read_text(encoding="utf-8"))
    classifiers = {
        "_wait_state", "_g1_r1_read_origin_checked", "_g1_r1_compare_origin",
        "_g1_r1_read_origin", "_g1_r1_read_wait_state", "runtime_main",
    }
    results: dict[str, Any] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            names = called_names(node)
            results[node.name] = {
                "classifiers_invoked": sorted(set(names) & classifiers),
                "injects_mode_string": "_g1_r1_failure_record" in names,
            }
    source = R1_TESTS.read_text(encoding="utf-8")
    stubs = sorted({
        marker for marker in ("skip", "xfail", ".only", "pytest.mark.skip", "TODO", "FIXME")
        if marker in source
    })
    report["D3_test_adequacy"] = {
        "tests": results,
        "test_count": len(results),
        "tests_without_classifier": sorted(
            name for name, item in results.items() if not item["classifiers_invoked"]
        ),
        "tests_injecting_mode_string": sorted(
            name for name, item in results.items() if item["injects_mode_string"]
        ),
        "stub_markers": stubs,
    }
    tautological = [name for name, item in results.items() if item["injects_mode_string"]]
    if tautological:
        failures.append(f"D3: tests still assert self-injected mode strings: {tautological}")
    no_classifier = [name for name, item in results.items() if not item["classifiers_invoked"]]
    if no_classifier:
        failures.append(f"D3: tests never reach a classifier: {no_classifier}")
    if stubs:
        failures.append(f"D3: stub or skip markers present: {stubs}")


# --------------------------------------------------------------------------- E
def check_structural_clauses(
    env: Any, tree: ast.Module, report: dict[str, Any], failures: list[str],
) -> None:
    """R-d: F1..F8 and P1 must survive the repair."""

    source = RUNTIME_ENV.read_text(encoding="utf-8")
    func = find_function(tree, "g1_r1_load_origin")
    r1_calls = called_names(func) if func is not None else []
    r1_source = ast.unparse(func) if func is not None else ""
    forbidden_hits = {
        token: sum(
            path.read_text(encoding="utf-8", errors="replace").count(token)
            for path in sorted((REPO / "tools").rglob("*.py"))
        )
        for token in FORBIDDEN_TOKENS
    }
    dispatch_present = {
        command: f'"{command}"' in source or f"'{command}'" in source
        for command in PRODUCTION_COMMANDS
    }
    origin_reads = re.findall(r"read_memory\(G1_R1_ORIGIN_ADDRESS, G1_R1_ORIGIN_READ_SIZE\)", source)
    predicates = [
        ast.unparse(sub) for sub in ast.walk(func) if isinstance(sub, ast.Lambda)
    ] if func is not None else []
    precondition = find_function(tree, "g1_r1_load_origin")
    precondition_source = ast.unparse(precondition) if precondition is not None else ""
    report["E_structural"] = {
        "F1_production_dispatch": dispatch_present,
        "F1_production_helpers_called_from_r1": sorted(
            name for name in r1_calls
            if name in {"_g1_flush_input_stage", "_capture_screenshot", "_g1_capture"}
        ),
        "F2_forbidden_token_hits_in_tools": forbidden_hits,
        "F3_origin_read_sites": len(origin_reads),
        "F4_wait_predicates": sorted(
            predicate for predicate in predicates if "G1_R1_WAIT_PS_STATES" in predicate
        ),
        "F4_literal_state_in_predicates": sorted(
            predicate for predicate in predicates
            if re.search(r"==\s*(9|35)\b", predicate)
        ),
        "F5_evidence_files": sorted(set(re.findall(r"r1_load_origin\.(?:json|log)", source))),
        "F8_click_injection_sites_in_r1": r1_source.count("x11_mouse_click.py"),
        "F8_screenshot_calls_in_r1": sorted(
            name for name in r1_calls if "screenshot" in name or "capture" in name
        ),
        "P1_precondition_gate": (
            '"precondition"' in precondition_source or "'precondition'" in precondition_source
        ) and "BLOCKED_PRECONDITION" in precondition_source,
        "wait_ps_states": list(getattr(env, "G1_R1_WAIT_PS_STATES", ())),
        "click_point": list(getattr(env, "G1_R1_CLICK_POINT", ())),
    }
    if not all(dispatch_present.values()):
        failures.append("E: a production subcommand disappeared from the dispatcher")
    if any(count for count in forbidden_hits.values()):
        failures.append(f"E: forbidden instrumentation token present: {forbidden_hits}")
    if len(origin_reads) != 1:
        failures.append(f"E: origin read sites != 1 ({len(origin_reads)})")
    if r1_source.count("x11_mouse_click.py") != 1:
        failures.append("E: R1 click injection sites != 1")
    if report["E_structural"]["F8_screenshot_calls_in_r1"]:
        failures.append("E: R1 captures screenshots")
    if list(getattr(env, "G1_R1_WAIT_PS_STATES", ())) != [9, 35]:
        failures.append("E: G1_R1_WAIT_PS_STATES changed")
    if not report["E_structural"]["P1_precondition_gate"]:
        failures.append("E: the P1 precondition gate is missing")


def main() -> int:
    failures: list[str] = []
    findings: list[str] = []
    report: dict[str, Any] = {"probe": Path(__file__).name, "lap": 330}

    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from tools import runtime_env as env

    tree = ast.parse(RUNTIME_ENV.read_text(encoding="utf-8"))
    check_artifacts(report, failures)
    check_call_sites(tree, report, failures)
    check_shared_invariants(env, tree, report, failures)
    check_mode_separation(env, report, failures)
    check_collection_error(env, report, failures)
    check_post_failure_routing(tree, report, findings, failures)
    check_test_adequacy(report, failures)
    check_structural_clauses(env, tree, report, failures)

    report["findings"] = findings
    report["fail_open"] = [
        "static plus synthetic only: this probe does not establish that the click reaches "
        "the load dialog, that pre is really (0,0,0), that the 40s/20s split is enough, or "
        "that teardown closes WM_CLOSE",
        "the 40s/20s allocation stays a design assumption; the first run measures it",
        "the repository has no commits, so `_wait_state` being unmodified is argued from "
        "its body containing no R1 names and from the full suite, not from a byte diff "
        "against the lap328 artifact",
        "mode 2 is produced by the comparator on synthetic samples; a real early return "
        "inside 0x4D60B0 would look the same and stays UNKNOWN by design",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
