#!/usr/bin/env python3
"""lap254 middle: independent review of the lap253 G1-R6-B-R15 repair.

lap253 claims that a *direct* selection reader failure inside
``_g1_read_selection_stage`` is classified ``UNKNOWN_STATE_READ_FAILURE`` even
when the run/stage deadline was reached at the same instant -- i.e. budget
exhaustion must not hide the failed state read behind
``UNKNOWN_BUDGET_EXHAUSTED`` the way ``_wait_state`` does for poll loops -- and
that the observation now carries ``finished_elapsed``,
``remaining_budget_after``, ``stage_budget_exhausted`` and
``run_budget_exhausted`` timing provenance.  Its evidence is "targeted 11
passed" plus the Fast suite.  Passing tests do not show the timing fields are
computed correctly away from the single fixture point, do not show the priority
claim is non-vacuous (the two code paths could agree by accident), and do not
show any of it is load-bearing.

This probe rebuilds the check from scratch:

C0. BASELINE.  Do the shipped direct-reader cases pass against the real repo?
C1. INDEPENDENT MATRIX.  Call ``_g1_read_selection_stage`` directly across a
    cross product of stage x stage_started x forced finish time x exception
    type, with a fake clock, and compare every observation field against an
    expectation model written here from the stated contract -- including a
    successful-read control and an uncaught-exception-type control.
C1b. ASYMMETRY CONTROL.  Under a budget-exhausted clock where *every* read
    fails, does ``_wait_state`` really answer ``UNKNOWN_BUDGET_EXHAUSTED``?
    If it did not, R15's priority claim would be vacuous rather than a repair.
C1c. CONSUMER SCAN.  Does anything outside tools/runtime_env.py read the new
    timing fields?  R23/R24 recorded the same question for read_coverage and
    read_failure.
C2. MIRROR CONTROL (M0).  Does an unmutated, depth-matched copy of the
    repository reproduce the real tests/test_runtime_env.py result?  Without
    this control a relocation failure reads as a "kill" (lap246 R20 lesson).
C3. MUTATIONS.  Against that mirror: (M1) priority inverted so an exhausted
    run budget wins, (M2) the new timing fields dropped from the observation,
    (M3) run_budget_exhausted pinned False, (M4) stage_budget_exhausted pinned
    True, (M5) the exception-level timing zeroed.  Each must kill at least one
    shipped test, otherwise that part of R15 is unasserted.

No game, Wine, Xvfb or PNG capture is involved; the probe is pure Python.
The report path is guarded before the body runs (R6-B-R7/R10/R11) and the
payload is serialised *before* the file is exclusively created (lap248 R21),
so a serialisation failure cannot leave truncated evidence behind.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
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

MUTATIONS: dict[str, tuple[str, str]] = {
    # Revert R15: let an exhausted budget outrank the concrete read failure,
    # exactly the _wait_state ordering R15 says must not apply here.
    "M1_priority_inverted": (CLASSIFICATION_ANCHOR, (
            "            classification=(\n"
            "                \"UNKNOWN_BUDGET_EXHAUSTED\" if remaining_budget_after <= 0.0\n"
            "                else \"UNKNOWN_STATE_READ_FAILURE\"\n"
            "            ),\n"
    )),
    # Drop the new timing provenance from the observation.
    "M2_timing_fields_dropped": (TIMING_FIELDS_ANCHOR, ""),
    # Pin the run-budget flag so it can never report exhaustion.
    "M3_run_budget_flag_pinned_false": (RUN_FLAG_ANCHOR, (
            "            \"run_budget_exhausted\": False,\n"
    )),
    # Pin the stage-budget flag so it always claims exhaustion.
    "M4_stage_budget_flag_pinned_true": (STAGE_FLAG_ANCHOR, (
            "            \"stage_budget_exhausted\": True,\n"
    )),
    # Keep the observation but zero the exception-level timing.
    "M5_exception_timing_zeroed": (EXC_TIMING_ANCHOR, (
            "            finished_elapsed=0.0,\n"
            "            remaining_budget_after=0.0,\n"
    )),
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
    for line in stdout.splitlines():
        if not (line.startswith("FAILED ") or line.startswith("ERROR ")):
            continue
        node = line.split(" ", 1)[1].split(" - ")[0].strip()
        if "::" not in node:
            continue
        failed.add(node.split("::")[-1].split("[")[0])
    summary = [
        ln for ln in stdout.splitlines()
        if " passed" in ln or " failed" in ln or " error" in ln
    ]
    return {
        "returncode": proc.returncode,
        "failed_tests": sorted(failed),
        "summary": summary[-1] if summary else "",
    }


# --------------------------------------------------------------------------
# C1: independent expectation model.
#
# Written from the contract, not from the implementation: the stage budget
# table is restated here so a silent change to the shipped table shows up as a
# mismatch instead of being inherited.
# --------------------------------------------------------------------------
EXPECTED_STAGE_BUDGETS: dict[str, float] = {
    "unit_select": 10.0, "drag_select": 10.0, "minimap": 10.0,
}
EXPECTED_READ_ERROR_RATIO_THRESHOLD = 0.25


def expected_observation(
    *, stage: str, read_point: str, started: float, timeout: float,
    stage_started: float | None, finished: float, provenance: str,
) -> dict[str, object]:
    stage_budget = EXPECTED_STAGE_BUDGETS.get(stage)
    finished_elapsed = max(0.0, finished - started)
    remaining = max(0.0, started + timeout - finished)
    return {
        "stage": stage,
        "stage_budget": stage_budget,
        "stage_started_elapsed": (
            round(max(0.0, stage_started - started), 3)
            if stage_started is not None else None
        ),
        "finished_elapsed": round(finished_elapsed, 3),
        "remaining_budget_after": round(remaining, 3),
        "stage_budget_exhausted": bool(
            stage_budget is not None and stage_started is not None
            and finished >= stage_started + stage_budget
        ),
        "run_budget_exhausted": remaining <= 0.0,
        "direct_reader": "selection",
        "direct_reader_failure": True,
        "direct_read_point": read_point,
        "direct_read_attempt_count": 1,
        "direct_read_error_count": 1,
        "poll_count": 0,
        "poll_attempt_count": 0,
        "read_error_count": 1,
        "first_read_error_provenance": provenance,
        "last_read_error_provenance": provenance,
        "successful_poll_ratio": 0.0,
        "read_error_ratio": None,
        "read_error_coverage_threshold_ratio": EXPECTED_READ_ERROR_RATIO_THRESHOLD,
        "read_error_coverage_exceeds_threshold": None,
        "observation_source": "direct_selection_reader",
    }


class _Clock:
    def __init__(self, value: float) -> None:
        self.value = value

    def __call__(self) -> float:
        return self.value


def _with_clock(value: float, fn):
    real = runtime_env.time.monotonic
    runtime_env.time.monotonic = _Clock(value)
    try:
        return fn()
    finally:
        runtime_env.time.monotonic = real


EXCEPTIONS = {
    "oserror": (OSError, "injected direct selection read failure"),
    "valueerror": (ValueError, "injected bad selection payload"),
    "struct_error": (struct.error, "unpack requires a buffer of 4 bytes"),
}
# started=0.0, timeout=10.0 throughout: before the deadline, one tick short of
# it, exactly on it, and past it.
FINISH_TIMES = (2.5, 9.999, 10.0, 12.5)
STAGE_CASES = (
    ("unit_select", "before_click", 0.0),
    ("unit_select", "before_click", None),
    ("drag_select", "after_drag", 3.0),
    ("minimap", "after_minimap", 0.0),
    ("production", "before_production", None),
    ("production", "before_production", 1.0),
)


def matrix() -> dict[str, object]:
    mismatches: list[dict[str, object]] = []
    cases = 0
    classifications: dict[str, int] = {}

    for stage, read_point, stage_started in STAGE_CASES:
        for finished in FINISH_TIMES:
            for kind, (exc_type, exc_message) in EXCEPTIONS.items():
                cases += 1
                label = f"{stage}/{read_point}/ss={stage_started}/t={finished}/{kind}"

                def reader() -> dict[str, object]:
                    raise exc_type(exc_message)

                def call():
                    return runtime_env._g1_read_selection_stage(
                        reader, stage=stage, read_point=read_point,
                        started=0.0, timeout=10.0, stage_started=stage_started,
                    )

                try:
                    _with_clock(finished, call)
                except runtime_env._G1WaitTimeout as exc:
                    caught = exc
                except Exception as exc:  # noqa: BLE001
                    mismatches.append({
                        "case": label, "field": "exception_type",
                        "expected": "_G1WaitTimeout", "actual": type(exc).__name__,
                    })
                    continue
                else:
                    mismatches.append({
                        "case": label, "field": "exception",
                        "expected": "_G1WaitTimeout", "actual": "no exception raised",
                    })
                    continue

                classifications[caught.classification] = (
                    classifications.get(caught.classification, 0) + 1
                )
                provenance = f"{exc_type.__name__}: {exc_message}"
                model = expected_observation(
                    stage=stage, read_point=read_point, started=0.0, timeout=10.0,
                    stage_started=stage_started, finished=finished, provenance=provenance,
                )
                actual = dict(caught.observation)

                if caught.classification != "UNKNOWN_STATE_READ_FAILURE":
                    mismatches.append({
                        "case": label, "field": "classification",
                        "expected": "UNKNOWN_STATE_READ_FAILURE",
                        "actual": caught.classification,
                    })
                if caught.last is not None:
                    mismatches.append({
                        "case": label, "field": "last",
                        "expected": None, "actual": caught.last,
                    })
                if caught.predicate_observed is not False:
                    mismatches.append({
                        "case": label, "field": "predicate_observed",
                        "expected": False, "actual": caught.predicate_observed,
                    })
                # The exception carries the *unrounded* budget numbers.
                for attr, want in (
                    ("finished_elapsed", max(0.0, finished - 0.0)),
                    ("remaining_budget_after", max(0.0, 10.0 - finished)),
                ):
                    got = getattr(caught, attr)
                    if abs(got - want) > 1e-9:
                        mismatches.append({
                            "case": label, "field": f"exc.{attr}",
                            "expected": want, "actual": got,
                        })
                if read_point not in str(caught):
                    mismatches.append({
                        "case": label, "field": "message_read_point",
                        "expected": read_point, "actual": str(caught),
                    })
                for key, want in model.items():
                    got = actual.get(key, "<missing>")
                    if got != want:
                        mismatches.append({
                            "case": label, "field": key,
                            "expected": want, "actual": got,
                        })
                extra = sorted(set(actual) - set(model))
                if extra:
                    mismatches.append({
                        "case": label, "field": "unexpected_observation_keys",
                        "expected": [], "actual": extra,
                    })

    # N0 control: a successful read must pass straight through, untouched.
    payload = {"count": 2, "selected_slot": 7, "selected_type": 58}
    got = _with_clock(99.0, lambda: runtime_env._g1_read_selection_stage(
        lambda: dict(payload), stage="unit_select", read_point="before_click",
        started=0.0, timeout=10.0, stage_started=0.0,
    ))
    cases += 1
    if got != payload:
        mismatches.append({
            "case": "N0_successful_read", "field": "return",
            "expected": payload, "actual": got,
        })

    # N1 control: an exception type outside the caught tuple must propagate
    # unchanged rather than being relabelled as a read failure.
    cases += 1
    def _boom() -> dict[str, object]:
        raise RuntimeError("not a read failure")

    try:
        _with_clock(1.0, lambda: runtime_env._g1_read_selection_stage(
            _boom, stage="unit_select", read_point="before_click",
            started=0.0, timeout=10.0, stage_started=0.0,
        ))
    except runtime_env._G1WaitTimeout as exc:
        mismatches.append({
            "case": "N1_uncaught_exception_type", "field": "exception_type",
            "expected": "RuntimeError", "actual": f"_G1WaitTimeout({exc.classification})",
        })
    except RuntimeError:
        pass
    else:
        mismatches.append({
            "case": "N1_uncaught_exception_type", "field": "exception",
            "expected": "RuntimeError", "actual": "no exception raised",
        })

    return {
        "cases": cases,
        "classifications": classifications,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:40],
    }


def asymmetry_control() -> dict[str, object]:
    """R15 is only a repair if _wait_state really answers BUDGET_EXHAUSTED."""

    clock = [0.0]
    real_monotonic = runtime_env.time.monotonic
    real_sleep = runtime_env.time.sleep
    runtime_env.time.monotonic = lambda: clock[0]
    runtime_env.time.sleep = lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    try:
        def unreadable(_detailed: bool) -> dict[str, object]:
            raise OSError("selected-unit read failed")

        observation: dict[str, object] = {}
        try:
            runtime_env._wait_state(
                unreadable, lambda _item: False,
                started=0.0, timeout=1.0, message="selection did not change",
                stage="drag_select", stage_budget=10.0, stage_started=0.0,
                wait_observation=observation,
            )
        except runtime_env._G1WaitTimeout as exc:
            poll_classification = exc.classification
            poll_read_errors = exc.observation.get("read_error_count")
        else:
            poll_classification = "<no timeout raised>"
            poll_read_errors = None
    finally:
        runtime_env.time.monotonic = real_monotonic
        runtime_env.time.sleep = real_sleep

    direct_classification = None
    try:
        _with_clock(1.0, lambda: runtime_env._g1_read_selection_stage(
            lambda: (_ for _ in ()).throw(OSError("selected-unit read failed")),
            stage="drag_select", read_point="before_drag",
            started=0.0, timeout=1.0, stage_started=0.0,
        ))
    except runtime_env._G1WaitTimeout as exc:
        direct_classification = exc.classification

    return {
        "poll_loop_classification_at_exhausted_budget": poll_classification,
        "poll_loop_read_error_count": poll_read_errors,
        "direct_read_classification_at_exhausted_budget": direct_classification,
        "asymmetry_is_real": bool(
            poll_classification == "UNKNOWN_BUDGET_EXHAUSTED"
            and direct_classification == "UNKNOWN_STATE_READ_FAILURE"
        ),
    }


def consumer_scan() -> dict[str, object]:
    fields = ("run_budget_exhausted", "stage_budget_exhausted")
    hits: dict[str, list[str]] = {field: [] for field in fields}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in {".py", ".sh", ".md", ".json"}:
            continue
        rel = path.relative_to(ROOT)
        parts = set(rel.parts)
        if parts & {".git", "__pycache__", ".venv", "local", "logs", ".pytest_cache"}:
            continue
        if rel == Path("tools/runtime_env.py"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for field in fields:
            if field in text:
                hits[field].append(str(rel))
    return {
        "hits": hits,
        "code_consumers_outside_runtime_env": sorted({
            item for field in fields for item in hits[field]
            if item.endswith((".py", ".sh")) and not item.startswith("tests/")
        }),
    }


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
        "lap": 254,
        "role": "middle",
        "subject": "G1-R6-B-R15 direct selection reader failure priority and timing provenance",
        "source_sha256": {
            "tools/runtime_env.py": sha256(RUNTIME_ENV),
            "tests/test_runtime_env.py": sha256(TEST_FILE),
        },
        "game_executions": 0,
        "wine_executions": 0,
    }

    report["c0_baseline"] = run_pytest(ROOT, [
        "tests/test_runtime_env.py", "-k",
        " or ".join(sorted(R15_TESTS | DIRECT_READER_ADJACENT)),
    ])
    report["c1_matrix"] = matrix()
    report["c1b_asymmetry"] = asymmetry_control()
    report["c1c_consumers"] = consumer_scan()

    source = RUNTIME_ENV.read_text(encoding="utf-8")
    anchors = {name: anchor in source for name, (anchor, _) in MUTATIONS.items()}
    report["anchors_present"] = anchors
    if not all(anchors.values()):
        report["c2_mirror_control"] = {"skipped": "mutation anchor not found"}
        report["c3_mutations"] = {"skipped": "mutation anchor not found"}
    else:
        with tempfile.TemporaryDirectory(prefix="lap254_r15_") as tmp:
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
                result["killed_r15"] = sorted(killed & R15_TESTS)
                result["killed_direct_reader_adjacent"] = sorted(
                    killed & DIRECT_READER_ADJACENT
                )
                result["killed_other"] = sorted(
                    killed - R15_TESTS - DIRECT_READER_ADJACENT
                )
                mutants[name] = result
                target.write_text(pristine, encoding="utf-8")
            report["c3_mutations"] = mutants

    baseline_ok = report["c0_baseline"]["returncode"] == 0
    matrix_ok = report["c1_matrix"]["mismatch_count"] == 0
    asymmetry_ok = bool(report["c1b_asymmetry"]["asymmetry_is_real"])
    control = report.get("c2_mirror_control", {})
    control_ok = control.get("returncode") == 0
    mutants = report.get("c3_mutations", {})
    mutation_ok = bool(mutants) and all(
        isinstance(item, dict) and item.get("failed_tests")
        for item in mutants.values()
    )
    report["verdict"] = {
        "c0_baseline": "PASS" if baseline_ok else "FAIL",
        "c1_matrix": "PASS" if matrix_ok else "FAIL",
        "c1b_asymmetry": "PASS" if asymmetry_ok else "FAIL",
        "c2_mirror_control": "PASS" if control_ok else "FAIL",
        "c3_mutations": "PASS" if mutation_ok else "FAIL",
        "overall": "PASS" if (
            baseline_ok and matrix_ok and asymmetry_ok and control_ok and mutation_ok
        ) else "FAIL",
    }

    # R21 lesson: serialise first so a payload defect cannot leave a truncated
    # evidence file that R6-B-R7 then refuses to let us replace.
    payload = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    print(json.dumps(report["verdict"], indent=2))
    print(json.dumps(report["c1b_asymmetry"], indent=2))
    print(json.dumps(report["c1_matrix"]["mismatches"], indent=2)[:4000])
    return 0 if report["verdict"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
