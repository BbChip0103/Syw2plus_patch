#!/usr/bin/env python3
"""lap250 middle: independent review of the lap249 G1-R6-B-R13 repair.

The lap249 work record claims that `_wait_state` now finalises its read
coverage on the *successful* return path, that the coverage is projected into
the Stage B stage record and the `input_checks` verdict, and that a
read-error-heavy window still does not gate an already observed successful
predicate.  Its evidence is "targeted 21 passed" plus the full Fast suite.
Passing tests do not show that the new call is load-bearing, do not show that
it failed to introduce a gate, and do not cover the sequence matrix.

This probe rebuilds the check from scratch:

C0. BASELINE.  Do the shipped R13 cases pass against the real repository?
C1. INDEPENDENT MATRIX.  Drive `_wait_state` directly over every poll
    sequence in {read-error, readable-but-unmatched}^0..3 followed by a
    matching poll (15 cases) and compare every coverage field, the returned
    state and the projections with an expectation model written here from the
    stated contract, not read off the implementation.
C1b. TIMEOUT CONTROL.  Re-drive the same reader over {error, unmatched}^4
    with no matching poll (16 cases) to show the timeout classification
    contract R13 promised not to touch still holds.
C2. MIRROR CONTROL (M0).  Does an unmutated, depth-matched copy of the
    repository reproduce the real `tests/test_runtime_env.py` result?  Without
    this control a relocation failure reads as a "kill" (lap246 R20 lesson).
C3. MUTATIONS.  Against that mirror, which tests die when (M1) the success
    path stops finalising coverage, (M2) the success path is made to gate on
    insufficient coverage, (M3) the stage-record projection is removed and
    (M4) the verdict's `wait_observation` fallback is removed?  Each mutation
    must kill at least one shipped test, otherwise that part of R13 is
    unasserted.

No game, Wine, Xvfb or PNG capture is involved; the probe is pure Python.
The report path is guarded before the body runs (R6-B-R7/R10) and the payload
is serialised *before* the file is exclusively created (R6-B-R11), so a
serialisation failure cannot leave truncated evidence behind (lap248 R21).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
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

THRESHOLD = 0.25
COVERAGE_FIELDS = (
    "poll_count", "poll_attempt_count", "read_error_count",
    "successful_poll_ratio", "read_error_ratio",
    "read_error_coverage_threshold_ratio", "read_error_coverage_exceeds_threshold",
    "first_read_error_provenance", "last_read_error_provenance",
)

# --- mutation anchors -----------------------------------------------------
# M1/M2 act on the success return path of `_wait_state`.
SUCCESS_ANCHOR = (
    "            if predicate(last):\n"
    "                update_read_coverage()\n"
    "                finished = time.monotonic()\n"
)
# M3 acts on the stage-record projection in `_g1_run_input_sequence`.
STAGE_ANCHOR = (
    "        coverage = _g1_read_coverage(wait_observation)\n"
    "        if coverage is not None:\n"
    '            stage_entry["read_coverage"] = coverage\n'
)
# M4 acts on the verdict fallback in `_g1_input_verdict`.
FALLBACK_ANCHOR = (
    "            if coverage is None:\n"
    '                coverage = _g1_read_coverage(item.get("wait_observation"))\n'
)

MUTATIONS: dict[str, tuple[str, str]] = {
    # Revert the R13 call: coverage on the success path stays stale.
    "M1_success_coverage_not_finalised": (SUCCESS_ANCHOR, (
        "            if predicate(last):\n"
        "                finished = time.monotonic()\n"
    )),
    # Over-strong variant: an already observed success is thrown away when the
    # read-error ratio is high.  R13 explicitly promised NOT to do this.
    "M2_success_gated_on_coverage": (SUCCESS_ANCHOR, (
        "            if predicate(last):\n"
        "                update_read_coverage()\n"
        '                if observation["read_error_coverage_exceeds_threshold"]:\n'
        "                    break\n"
        "                finished = time.monotonic()\n"
    )),
    # Drop the stage-record projection.
    "M3_stage_projection_removed": (STAGE_ANCHOR, ""),
    # Drop the verdict's wait_observation fallback.
    "M4_verdict_fallback_removed": (FALLBACK_ANCHOR, ""),
}

R13_TESTS = {
    "test_g1_wait_state_pass_exposes_read_coverage_without_gating_response",
    "test_g1_shared_input_sequence_blocks_production_but_reaches_later_stages",
}
BASELINE_TESTS = sorted(R13_TESTS | {
    "test_g1_wait_state_classifies_unreadable_polls_as_unknown",
    "test_g1_wait_state_preserves_corruption_when_read_coverage_is_unknown",
    "test_g1_wait_state_keeps_boundary_read_error_coverage_as_hard_no_effect",
})


def output_refusal(path: Path) -> str | None:
    try:
        if path.exists():
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
# Stated contract (restated here from the R13 claim, not from the code):
#   * When a poll satisfies the predicate, `_wait_state` returns that state.
#     Read errors seen earlier in the same window never withhold that answer.
#   * The observation handed back to the caller describes the whole window:
#     attempts counts every poll, successes count readable polls including the
#     matching one, errors count unreadable polls, and the two ratios plus the
#     threshold flag are consistent with those final counts.
#   * The first/last read-error provenance is present exactly when at least
#     one poll failed to read.
#   * That same set of nine fields is what `_g1_read_coverage` projects, and
#     `_g1_input_verdict` reports it per budgeted stage from either the stage
#     record or the raw wait observation.
# --------------------------------------------------------------------------
MATCH_STATE = {"ps": 7}
UNMATCHED_STATE = {"ps": 5}


def expected_success(seq: tuple[str, ...]) -> dict[str, object]:
    attempts = len(seq)
    errors = sum(1 for s in seq if s == "E")
    successes = attempts - errors
    ratio = errors / attempts
    return {
        "returned": dict(MATCH_STATE),
        "poll_attempt_count": attempts,
        "poll_count": successes,
        "read_error_count": errors,
        "successful_poll_ratio": round(successes / attempts, 9),
        "read_error_ratio": round(ratio, 9),
        "read_error_coverage_threshold_ratio": THRESHOLD,
        "read_error_coverage_exceeds_threshold": ratio > THRESHOLD,
        "has_first_provenance": errors > 0,
        "has_last_provenance": errors > 0,
    }


def expected_timeout(seq: tuple[str, ...]) -> str:
    attempts = len(seq)
    errors = sum(1 for s in seq if s == "E")
    successes = attempts - errors
    unavailable = errors > 0 and (successes == 0 or seq[-1] == "E")
    if unavailable:
        return "UNKNOWN_STATE_READ_FAILURE"
    if (errors / attempts) > THRESHOLD:
        return "UNKNOWN_STATE_READ_COVERAGE"
    return "FAIL_NO_EFFECT"


def _import_runtime_env():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import tools.runtime_env as runtime_env  # noqa: PLC0415

    return runtime_env


def _drive(seq: tuple[str, ...]) -> dict[str, object]:
    """Run one poll sequence against `_wait_state` on a fake clock."""

    runtime_env = _import_runtime_env()
    clock = [0.0]
    real_monotonic = runtime_env.time.monotonic
    real_sleep = runtime_env.time.sleep
    runtime_env.time.monotonic = lambda: clock[0]
    runtime_env.time.sleep = lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    pending = list(seq)
    wait_observation: dict[str, object] = {}

    def read_state(_detailed: bool) -> dict[str, object]:
        symbol = pending.pop(0) if pending else "N"
        if symbol == "E":
            raise OSError("transient state read failed")
        return dict(MATCH_STATE if symbol == "Y" else UNMATCHED_STATE)

    try:
        try:
            returned = runtime_env._wait_state(
                read_state, lambda item: item.get("ps") == 7,
                started=0.0, timeout=10.0, message="state was not observed",
                stage="unit_select", stage_budget=1.0, stage_started=0.0,
                wait_observation=wait_observation,
            )
        except runtime_env._G1WaitTimeout as timeout:
            return {
                "responded": False,
                "classification": timeout.classification,
                "observation": dict(timeout.observation),
            }
        return {
            "responded": True,
            "returned": returned,
            "observation": dict(wait_observation),
        }
    finally:
        runtime_env.time.monotonic = real_monotonic
        runtime_env.time.sleep = real_sleep


def success_matrix() -> dict[str, object]:
    runtime_env = _import_runtime_env()
    mismatches: list[dict[str, object]] = []
    sequences: list[tuple[str, ...]] = []
    for length in range(4):
        for prefix in itertools.product("EN", repeat=length):
            sequences.append((*prefix, "Y"))
    high_error_but_answered = 0
    for seq in sequences:
        tag = "".join(seq)
        want = expected_success(seq)
        got = _drive(seq)
        if not got["responded"]:
            mismatches.append({"sequence": tag, "error": "predicate answer withheld",
                               "classification": got.get("classification")})
            continue
        observation = got["observation"]
        diff: dict[str, object] = {}
        if got["returned"] != want["returned"]:
            diff["returned"] = {"want": want["returned"], "got": got["returned"]}
        for field in COVERAGE_FIELDS:
            if field in ("first_read_error_provenance", "last_read_error_provenance"):
                continue
            if observation.get(field) != want[field]:
                diff[field] = {"want": want[field], "got": observation.get(field)}
        for field, key in (
            ("first_read_error_provenance", "has_first_provenance"),
            ("last_read_error_provenance", "has_last_provenance"),
        ):
            if (observation.get(field) is not None) != want[key]:
                diff[field] = {"want_present": want[key], "got": observation.get(field)}
        # Internal consistency: the ratios must be reconstructible from the counts.
        attempts = observation.get("poll_attempt_count")
        if attempts != (observation.get("poll_count", 0) + observation.get("read_error_count", 0)):
            diff["counts_do_not_sum"] = {
                "attempts": attempts, "poll_count": observation.get("poll_count"),
                "read_error_count": observation.get("read_error_count"),
            }
        # Projection: `_g1_read_coverage` must expose exactly the nine fields.
        coverage = runtime_env._g1_read_coverage(observation)
        if coverage is None:
            diff["coverage_projection"] = "None"
        elif set(coverage) != set(COVERAGE_FIELDS) or any(
            coverage[field] != observation[field] for field in COVERAGE_FIELDS
        ):
            diff["coverage_projection"] = coverage
        # Verdict: both the stage-record route and the raw-observation route.
        via_record = runtime_env._g1_input_verdict(
            [{"tag": "unit_select", "result": "PASS", "read_coverage": coverage}],
            enabled=True,
        )
        via_observation = runtime_env._g1_input_verdict(
            [{"tag": "unit_select", "result": "PASS", "wait_observation": observation}],
            enabled=True,
        )
        if via_record["read_coverage"].get("unit_select") != coverage:
            diff["verdict_via_record"] = via_record["read_coverage"]
        if via_observation["read_coverage"].get("unit_select") != coverage:
            diff["verdict_via_observation"] = via_observation["read_coverage"]
        # A PASS stage must stay PASS no matter how poor the read coverage was.
        full_pass = runtime_env._g1_input_verdict(
            [{"tag": tag_name, "result": "PASS",
              "wait_observation": observation if tag_name == "unit_select" else None}
             for tag_name in runtime_env.G1_REQUIRED_INPUT_TAGS],
            enabled=True,
        )
        if full_pass["required_inputs"] is not True:
            diff["required_inputs_gated"] = full_pass["required_inputs"]
        if want["read_error_coverage_exceeds_threshold"]:
            high_error_but_answered += 1
        if diff:
            mismatches.append({"sequence": tag, "diff": diff})
    return {
        "cases": len(sequences),
        "mismatches": mismatches,
        "answered_despite_insufficient_coverage": high_error_but_answered,
    }


def timeout_matrix() -> dict[str, object]:
    mismatches: list[dict[str, object]] = []
    sequences = list(itertools.product("EN", repeat=4))
    for seq in sequences:
        tag = "".join(seq)
        got = _drive(seq)
        if got["responded"]:
            mismatches.append({"sequence": tag, "error": "unexpected predicate response"})
            continue
        want = expected_timeout(seq)
        if got["classification"] != want:
            mismatches.append({
                "sequence": tag,
                "diff": {"want": want, "got": got["classification"]},
            })
            continue
        observation = got["observation"]
        if observation.get("poll_attempt_count") != 4:
            mismatches.append({
                "sequence": tag, "error": "unexpected poll attempts",
                "poll_attempt_count": observation.get("poll_attempt_count"),
            })
    return {"cases": len(sequences), "mismatches": mismatches}


def build_mirror(stage: Path) -> Path:
    # Match the real repository's path depth (5 components under "/") so that
    # any parents[N] root resolution behaves identically.
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
        "lap": 250,
        "role": "middle",
        "subject": "G1-R6-B-R13 PASS-path read coverage exposure",
        "source_sha256": {
            "tools/runtime_env.py": sha256(RUNTIME_ENV),
            "tests/test_runtime_env.py": sha256(TEST_FILE),
        },
        "game_executions": 0,
        "wine_executions": 0,
    }

    report["c0_baseline"] = run_pytest(ROOT, [
        "tests/test_runtime_env.py", "-k", " or ".join(BASELINE_TESTS),
    ])
    report["c1_success_matrix"] = success_matrix()
    report["c1b_timeout_matrix"] = timeout_matrix()

    source = RUNTIME_ENV.read_text(encoding="utf-8")
    anchors = {
        "success_path": SUCCESS_ANCHOR in source,
        "stage_projection": STAGE_ANCHOR in source,
        "verdict_fallback": FALLBACK_ANCHOR in source,
    }
    report["anchors_present"] = anchors
    if not all(anchors.values()):
        report["c2_mirror_control"] = {"skipped": "mutation anchor not found"}
        report["c3_mutations"] = {"skipped": "mutation anchor not found"}
    else:
        with tempfile.TemporaryDirectory(prefix="lap250_r13_") as tmp:
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
                result["killed_r13"] = sorted(killed & R13_TESTS)
                result["killed_other"] = sorted(killed - R13_TESTS)
                mutants[name] = result
                target.write_text(pristine, encoding="utf-8")
            report["c3_mutations"] = mutants

    baseline_ok = report["c0_baseline"]["returncode"] == 0
    matrix_ok = not report["c1_success_matrix"]["mismatches"]
    timeout_ok = not report["c1b_timeout_matrix"]["mismatches"]
    control = report.get("c2_mirror_control", {})
    control_ok = control.get("returncode") == 0
    mutants = report.get("c3_mutations", {})
    m1 = mutants.get("M1_success_coverage_not_finalised", {})
    m2 = mutants.get("M2_success_gated_on_coverage", {})
    m3 = mutants.get("M3_stage_projection_removed", {})
    m4 = mutants.get("M4_verdict_fallback_removed", {})
    mutation_ok = all(
        isinstance(item, dict) and item.get("failed_tests")
        for item in (m1, m2, m3, m4)
    ) and all(
        not item.get("killed_other") for item in (m1, m2, m3, m4)
    )
    report["verdict"] = {
        "c0_baseline": "PASS" if baseline_ok else "FAIL",
        "c1_success_matrix": "PASS" if matrix_ok else "FAIL",
        "c1b_timeout_matrix": "PASS" if timeout_ok else "FAIL",
        "c2_mirror_control": "PASS" if control_ok else "FAIL",
        "c3_mutations": "PASS" if mutation_ok else "FAIL",
        "overall": "PASS" if (
            baseline_ok and matrix_ok and timeout_ok and control_ok and mutation_ok
        ) else "FAIL",
    }

    # R21 lesson: serialise first so a payload defect cannot leave a truncated
    # evidence file that R6-B-R7 then refuses to let us replace.
    payload = json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    print(json.dumps(report["verdict"], indent=2))
    return 0 if report["verdict"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
