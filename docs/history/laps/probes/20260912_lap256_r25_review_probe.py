#!/usr/bin/env python3
"""lap256 middle: independent review of the lap255 G1-R6-B-R25 repair.

lap254 rejected the R15 *range* (not its implementation) because mutation M4 --
``stage_budget_exhausted`` pinned to the constant ``True`` -- survived the whole
shipped suite: one of R15's four provenance fields had no regression behind it.
lap255 (R25) answers with a tests-only change: a four-case parameterized
regression over ``_g1_read_selection_stage`` that pins the flag to ``False``
inside the stage budget, ``True`` at the exact boundary, and ``False`` when
either ``stage_started`` or the stage budget is unknown.  ``tools/runtime_env.py``
is unchanged.

Passing tests still do not show the flag is computed correctly away from those
four points, do not show each of the four cases is individually load-bearing,
and do not by themselves close the R15 range -- that needs the other three
fields to still be covered too.  This probe rebuilds the check from scratch:

C0. BASELINE.  Do the R25 cases and every direct-reader-adjacent test pass in
    the real repository?
C1. INDEPENDENT MATRIX.  Call ``_g1_read_selection_stage`` over a grid far
    wider than the shipped four cases (stage x stage_started x finish time,
    including sub-boundary, exact-boundary and past-boundary instants and a
    non-zero stage start) and compare ``stage_budget``, ``stage_started_elapsed``,
    ``stage_budget_exhausted``, ``run_budget_exhausted``, ``finished_elapsed``
    and ``remaining_budget_after`` against an expectation model written here
    from the contract, not copied from the implementation.
C2. MIRROR CONTROL (M0).  An unmutated, depth-matched copy of the repository
    must reproduce the real suite result, otherwise a relocation failure would
    read as a "kill" (lap246 R20 lesson).
C3. MUTATIONS.  Against that mirror: the four lap254 mutations that already
    had kills (M1 priority inverted, M2 timing fields dropped, M3 run flag
    pinned False, M5 exception timing zeroed), the lap254 survivor M4 (stage
    flag pinned True), and three new stage-flag semantics mutations that each
    target exactly one claimed distinction -- M6 pinned False, M7 strict ``>``
    at the boundary, M8 unknown ``stage_started`` folded to the run start, M9
    unknown stage budget folded to 0.  Every one must kill at least one test,
    with no kills outside the direct-reader-adjacent range.

Per-case attribution is kept (full parameterized node ids) so the report shows
*which* of the four R25 cases each mutation dies on.

No game, Wine, Xvfb or PNG capture is involved; the probe is pure Python.
The report path is guarded before the body runs (R6-B-R7/R10/R11) and the
payload is serialised *before* the file is exclusively created (lap248 R21).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
RUNTIME_ENV = ROOT / "tools" / "runtime_env.py"
TEST_FILE = ROOT / "tests" / "test_runtime_env.py"
PYTHON = ROOT / ".venv" / "bin" / "python"

sys.path.insert(0, str(ROOT / "tools"))
import runtime_env  # noqa: E402


# --- mutation anchors -----------------------------------------------------
CLASSIFICATION_ANCHOR = (
            "            classification=\"UNKNOWN_STATE_READ_FAILURE\",\n"
)
TIMING_FIELDS_ANCHOR = (
            "            \"finished_elapsed\": round(finished_elapsed, 3),\n"
            "            \"remaining_budget_after\": round(remaining_budget_after, 3),\n"
)
RUN_FLAG_ANCHOR = (
            "            \"run_budget_exhausted\": remaining_budget_after <= 0.0,\n"
)
STAGE_FLAG_ANCHOR = (
            "            \"stage_budget_exhausted\": bool(\n"
            "                stage_budget is not None\n"
            "                and stage_started is not None\n"
            "                and finished >= stage_started + stage_budget\n"
            "            ),\n"
)
EXC_TIMING_ANCHOR = (
            "            finished_elapsed=finished_elapsed,\n"
            "            remaining_budget_after=remaining_budget_after,\n"
)


def _stage_flag(expression: str) -> str:
    return f"            \"stage_budget_exhausted\": {expression},\n"


MUTATIONS: dict[str, tuple[str, str]] = {
    # lap254 mutations that already had kills; re-run so the R15 range verdict
    # rests on this session's own measurement rather than on a quoted number.
    "M1_priority_inverted": (CLASSIFICATION_ANCHOR, (
            "            classification=(\n"
            "                \"UNKNOWN_BUDGET_EXHAUSTED\" if remaining_budget_after <= 0.0\n"
            "                else \"UNKNOWN_STATE_READ_FAILURE\"\n"
            "            ),\n"
    )),
    "M2_timing_fields_dropped": (TIMING_FIELDS_ANCHOR, ""),
    "M3_run_budget_flag_pinned_false": (RUN_FLAG_ANCHOR, (
            "            \"run_budget_exhausted\": False,\n"
    )),
    "M5_exception_timing_zeroed": (EXC_TIMING_ANCHOR, (
            "            finished_elapsed=0.0,\n"
            "            remaining_budget_after=0.0,\n"
    )),
    # The lap254 survivor R25 claims to kill.
    "M4_stage_budget_flag_pinned_true": (STAGE_FLAG_ANCHOR, _stage_flag("True")),
    # New: one mutation per claimed distinction.
    "M6_stage_budget_flag_pinned_false": (STAGE_FLAG_ANCHOR, _stage_flag("False")),
    "M7_stage_boundary_strict_greater": (STAGE_FLAG_ANCHOR, (
            "            \"stage_budget_exhausted\": bool(\n"
            "                stage_budget is not None\n"
            "                and stage_started is not None\n"
            "                and finished > stage_started + stage_budget\n"
            "            ),\n"
    )),
    "M8_unknown_stage_start_folded_to_run_start": (STAGE_FLAG_ANCHOR, (
            "            \"stage_budget_exhausted\": bool(\n"
            "                stage_budget is not None\n"
            "                and finished >= (\n"
            "                    started if stage_started is None else stage_started\n"
            "                ) + stage_budget\n"
            "            ),\n"
    )),
    "M9_unknown_stage_budget_folded_to_zero": (STAGE_FLAG_ANCHOR, (
            "            \"stage_budget_exhausted\": bool(\n"
            "                stage_started is not None\n"
            "                and finished >= stage_started + (\n"
            "                    0.0 if stage_budget is None else stage_budget\n"
            "                )\n"
            "            ),\n"
    )),
}

R25_TESTS = {
    "test_g1_direct_selection_reader_stage_budget_exhaustion_is_semantic",
}
R15_TESTS = {
    "test_g1_direct_selection_reader_failure_precedes_exhausted_run_budget",
}
DIRECT_READER_ADJACENT = {
    "test_g1_direct_selection_reader_failure_is_stage_diagnosed",
    "test_g1_production_direct_selection_reader_failure_stays_blocked_and_continues",
    "test_g1_production_selection_snapshots_mark_direct_read_failure_unavailable",
    "test_g1_production_selection_snapshot_has_no_failure_marker_on_success",
    "test_g1_selection_reader_failures_timeout_closed_with_provenance",
}


def output_refusal(path: Path) -> str | None:
    try:
        if path.exists() or path.is_symlink():
            return f"refusing to overwrite existing evidence: {path}"
        parent = path.parent
        if not parent.is_dir():
            return f"refusing to write evidence: output parent is not a directory: {parent}"
        if not os.access(parent, os.W_OK | os.X_OK):
            return f"refusing to write evidence: output parent is not writable: {parent}"
    except OSError as exc:
        return f"refusing to write evidence: output path unavailable: {path}: {exc}"
    return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_pytest(root: Path, args: list[str]) -> dict[str, object]:
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "-p", "no:cacheprovider", "-q", *args],
        cwd=str(root), capture_output=True, text=True, timeout=900,
    )
    stdout = proc.stdout + proc.stderr
    failed: set[str] = set()
    failed_nodes: set[str] = set()
    for line in stdout.splitlines():
        if not (line.startswith("FAILED ") or line.startswith("ERROR ")):
            continue
        node = line.split(" ", 1)[1].split(" - ")[0].strip()
        if "::" not in node:
            continue
        leaf = node.split("::")[-1]
        failed_nodes.add(leaf)
        failed.add(leaf.split("[")[0])
    summary = [
        ln for ln in stdout.splitlines()
        if " passed" in ln or " failed" in ln or " error" in ln
    ]
    return {
        "returncode": proc.returncode,
        "failed_tests": sorted(failed),
        "failed_nodes": sorted(failed_nodes),
        "summary": summary[-1] if summary else "",
    }


# --------------------------------------------------------------------------
# C1: independent expectation model, restated from the contract so a silent
# change to the shipped stage-budget table shows up as a mismatch.
# --------------------------------------------------------------------------
EXPECTED_STAGE_BUDGETS: dict[str, float] = {
    "unit_select": 10.0, "drag_select": 10.0, "minimap": 10.0,
}


def expected_fields(
    *, stage: str, started: float, timeout: float,
    stage_started: float | None, finished: float,
) -> dict[str, object]:
    budget = EXPECTED_STAGE_BUDGETS.get(stage)
    finished_elapsed = max(0.0, finished - started)
    remaining = max(0.0, started + timeout - finished)
    if budget is None or stage_started is None:
        exhausted = False
    else:
        exhausted = finished >= stage_started + budget
    return {
        "stage_budget": budget,
        "stage_started_elapsed": (
            round(max(0.0, stage_started - started), 3)
            if stage_started is not None else None
        ),
        "finished_elapsed": round(finished_elapsed, 3),
        "remaining_budget_after": round(remaining, 3),
        "stage_budget_exhausted": exhausted,
        "run_budget_exhausted": remaining <= 0.0,
    }


def _with_clock(now: float, call):
    real = runtime_env.time.monotonic
    runtime_env.time.monotonic = lambda: now
    try:
        return call()
    finally:
        runtime_env.time.monotonic = real


def matrix() -> dict[str, object]:
    started = 100.0
    timeout = 30.0
    cases = 0
    mismatches: list[dict[str, object]] = []
    truth: list[dict[str, object]] = []
    for stage in ("unit_select", "drag_select", "minimap", "production", "menu"):
        for stage_started in (None, 100.0, 104.25):
            base = 100.0 if stage_started is None else stage_started
            for offset in (0.0, 5.0, 9.999, 10.0, 10.001, 25.0, 40.0):
                finished = base + offset
                cases += 1
                try:
                    _with_clock(finished, lambda: runtime_env._g1_read_selection_stage(
                        _raise_os_error,
                        stage=stage, read_point="before_click",
                        started=started, timeout=timeout,
                        stage_started=stage_started,
                    ))
                except runtime_env._G1WaitTimeout as exc:
                    observation = exc.observation or {}
                    if exc.classification != "UNKNOWN_STATE_READ_FAILURE":
                        mismatches.append({
                            "stage": stage, "stage_started": stage_started,
                            "finished": finished, "field": "classification",
                            "expected": "UNKNOWN_STATE_READ_FAILURE",
                            "actual": exc.classification,
                        })
                    expected = expected_fields(
                        stage=stage, started=started, timeout=timeout,
                        stage_started=stage_started, finished=finished,
                    )
                    for field, want in expected.items():
                        got = observation.get(field)
                        if got != want:
                            mismatches.append({
                                "stage": stage, "stage_started": stage_started,
                                "finished": finished, "field": field,
                                "expected": want, "actual": got,
                            })
                    truth.append({
                        "stage": stage, "stage_started": stage_started,
                        "offset": offset,
                        "stage_budget_exhausted": observation.get(
                            "stage_budget_exhausted"
                        ),
                    })
                else:
                    mismatches.append({
                        "stage": stage, "stage_started": stage_started,
                        "finished": finished, "field": "exception",
                        "expected": "_G1WaitTimeout", "actual": "no exception raised",
                    })
    return {
        "cases": cases,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:40],
        "stage_flag_truth_table": truth,
    }


def _raise_os_error() -> dict[str, object]:
    raise OSError("injected direct selection read failure")


def build_mirror(stage: Path) -> Path:
    # Match the real repository's path depth (5 components under "/").
    mirror = stage / "sharedfolder" / "260320_Syw2plus" / "Syw2plus_patch"
    mirror.parent.mkdir(parents=True)
    shutil.copytree(
        ROOT, mirror,
        ignore=shutil.ignore_patterns(
            ".git", "__pycache__", "local", "logs", ".venv", ".pytest_cache",
        ),
    )
    return mirror


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    refusal = output_refusal(args.output)
    if refusal is not None:
        print(refusal, file=sys.stderr)
        return 2

    report: dict[str, object] = {
        "lap": 256,
        "role": "middle",
        "subject": "G1-R6-B-R25 stage_budget_exhausted semantic regression; R15 range decision",
        "source_sha256": {
            "tools/runtime_env.py": sha256(RUNTIME_ENV),
            "tests/test_runtime_env.py": sha256(TEST_FILE),
        },
        "game_executions": 0,
        "wine_executions": 0,
    }

    report["c0_baseline"] = run_pytest(ROOT, [
        "tests/test_runtime_env.py", "-k",
        " or ".join(sorted(R25_TESTS | R15_TESTS | DIRECT_READER_ADJACENT)),
    ])
    report["c1_matrix"] = matrix()

    source = RUNTIME_ENV.read_text(encoding="utf-8")
    anchors = {name: anchor in source for name, (anchor, _) in MUTATIONS.items()}
    report["anchors_present"] = anchors
    if not all(anchors.values()):
        report["c2_mirror_control"] = {"skipped": "mutation anchor not found"}
        report["c3_mutations"] = {"skipped": "mutation anchor not found"}
    else:
        with tempfile.TemporaryDirectory(prefix="lap256_r25_") as tmp:
            mirror = build_mirror(Path(tmp))
            target = mirror / "tools" / "runtime_env.py"
            pristine = target.read_text(encoding="utf-8")
            report["c2_mirror_control"] = run_pytest(mirror, ["tests/test_runtime_env.py"])
            mutants: dict[str, object] = {}
            for name, (anchor, replacement) in MUTATIONS.items():
                mutated = pristine.replace(anchor, replacement)
                if mutated == pristine:
                    mutants[name] = {"error": "anchor did not apply"}
                    continue
                target.write_text(mutated, encoding="utf-8")
                shutil.rmtree(mirror / "tools" / "__pycache__", ignore_errors=True)
                result = run_pytest(mirror, ["tests/test_runtime_env.py"])
                killed = set(result["failed_tests"])
                result["killed_r25"] = sorted(killed & R25_TESTS)
                result["killed_r25_cases"] = sorted(
                    node for node in result["failed_nodes"]
                    if node.split("[")[0] in R25_TESTS
                )
                result["killed_r15"] = sorted(killed & R15_TESTS)
                result["killed_direct_reader_adjacent"] = sorted(
                    killed & DIRECT_READER_ADJACENT
                )
                result["killed_other"] = sorted(
                    killed - R25_TESTS - R15_TESTS - DIRECT_READER_ADJACENT
                )
                mutants[name] = result
                target.write_text(pristine, encoding="utf-8")
            report["c3_mutations"] = mutants

    baseline_ok = report["c0_baseline"]["returncode"] == 0
    matrix_ok = report["c1_matrix"]["mismatch_count"] == 0
    control = report.get("c2_mirror_control", {})
    control_ok = control.get("returncode") == 0
    mutants = report.get("c3_mutations", {})
    mutation_ok = bool(mutants) and all(
        isinstance(item, dict) and item.get("failed_tests")
        for item in mutants.values()
    )
    out_of_range = sorted({
        name for name, item in mutants.items()
        if isinstance(item, dict) and item.get("killed_other")
    })
    survivors = sorted({
        name for name, item in mutants.items()
        if isinstance(item, dict) and not item.get("failed_tests")
    })
    report["mutation_survivors"] = survivors
    report["mutations_with_out_of_range_kills"] = out_of_range
    report["verdict"] = {
        "c0_baseline": "PASS" if baseline_ok else "FAIL",
        "c1_matrix": "PASS" if matrix_ok else "FAIL",
        "c2_mirror_control": "PASS" if control_ok else "FAIL",
        "c3_mutations": "PASS" if mutation_ok else "FAIL",
        "c3_kill_scope": "PASS" if not out_of_range else "FAIL",
        "overall": "PASS" if (
            baseline_ok and matrix_ok and control_ok and mutation_ok and not out_of_range
        ) else "FAIL",
    }

    # R21 lesson: serialise first so a payload defect cannot leave a truncated
    # evidence file that R6-B-R7 then refuses to let us replace.
    payload = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    print(json.dumps(report["verdict"], indent=2))
    print(json.dumps({
        "survivors": survivors,
        "out_of_range": out_of_range,
        "matrix_cases": report["c1_matrix"]["cases"],
        "matrix_mismatches": report["c1_matrix"]["mismatch_count"],
    }, indent=2))
    return 0 if report["verdict"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
