#!/usr/bin/env python3
"""lap248 middle: independent review of the lap247 G1-R6-B-R12 repair.

The lap247 work record claims `_wait_state` now preserves a selection
`CORRUPTED` diagnosis when a read-error tail or insufficient read coverage
independently makes the timeout UNKNOWN, while the SOUND path keeps its
`UNAVAILABLE` downgrade.  Its evidence is "targeted 4 passed" plus the full
Fast suite.  Passing tests do not show the guard is load-bearing, do not show
the guard is not *too* strong, and do not cover the overlap matrix.

This probe rebuilds the check from scratch:

C0. BASELINE.  Do the shipped R12 cases and the two pre-existing UNAVAILABLE
    regressions pass against the real repository?
C1. INDEPENDENT MATRIX.  Drive `_wait_state` directly over every read
    sequence in {sound, corrupt, error}^4 (81 cases) and compare the final
    selection status, corruption provenance and timeout classification with
    an expectation model written here from the stated contract, not from the
    implementation.
C2. MIRROR CONTROL (M0).  Does an unmutated, depth-matched copy of the
    repository reproduce the real `tests/test_runtime_env.py` result?  Without
    this control a relocation failure reads as a "kill" (lap246 R20 lesson).
C3. MUTATIONS.  Against that mirror, which tests die when the R12 guard is
    (M1) deleted, (M2) made unconditional so nothing is ever downgraded, and
    (M3) inverted?  A load-bearing, correctly-scoped guard must be killed by
    M1 in exactly the R12 cases, by M2 in exactly the UNAVAILABLE cases, and
    by M3 in both.

No game, Wine, Xvfb or PNG capture is involved; the probe is pure Python.
The report path is guarded before the body runs (R6-B-R7/R10) and written
with exclusive creation (R6-B-R11).
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

GUARD_ANCHOR = (
    '        if selection_observation.get("status") != "CORRUPTED":\n'
    '            selection_observation["status"] = "UNAVAILABLE"\n'
)
MUTATIONS = {
    # Delete the guard: the lap247 change is reverted to the lap246 behaviour.
    "M1_guard_deleted": '        selection_observation["status"] = "UNAVAILABLE"\n',
    # Guard always taken: nothing is ever downgraded to UNAVAILABLE.
    "M2_never_downgrades": (
        '        if False:\n'
        '            selection_observation["status"] = "UNAVAILABLE"\n'
    ),
    # Inverted guard: only CORRUPTED is overwritten.
    "M3_guard_inverted": (
        '        if selection_observation.get("status") == "CORRUPTED":\n'
        '            selection_observation["status"] = "UNAVAILABLE"\n'
    ),
}

R12_TESTS = {
    "test_g1_wait_state_preserves_corruption_when_read_coverage_is_unknown",
}
UNAVAILABLE_TESTS = {
    "test_g1_wait_state_marks_selection_unavailable_after_unreadable_tail",
    "test_g1_wait_state_rejects_read_error_heavy_window_even_with_readable_tail",
}
BASELINE_TESTS = sorted(R12_TESTS | UNAVAILABLE_TESTS | {
    "test_g1_wait_state_keeps_boundary_read_error_coverage_as_hard_no_effect",
    "test_g1_selection_response_timeout_preserves_corruption_provenance",
    "test_g1_selection_response_final_sound_observation_clears_stale_corruption",
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
    summary = [ln for ln in stdout.splitlines() if " passed" in ln or " failed" in ln or " error" in ln]
    return {
        "returncode": proc.returncode,
        "failed_tests": sorted(failed),
        "summary": summary[-1] if summary else "",
    }


# --------------------------------------------------------------------------
# C1: independent expectation model.
#
# Stated contract (restated here, not read off the implementation):
#   * The selection observation records the status of the LAST SUCCESSFUL
#     poll: SOUND when both endpoints parse, CORRUPTED otherwise.  It is
#     absent when no poll ever succeeded.
#   * A timeout is UNKNOWN for read reasons when either the tail is
#     unreadable / nothing was ever read (READ FAILURE) or the read error
#     ratio exceeds 25% (READ COVERAGE).
#   * Those read reasons must not overwrite an already-observed CORRUPTED
#     status, but must downgrade a SOUND status to UNAVAILABLE (R6-B-R12).
#   * Classification priority: read failure > read coverage > corrupted
#     selection > no effect.
# --------------------------------------------------------------------------
BEFORE = {"count": 1, "selected_slot": 1199, "selected_type": 70}
SOUND_READ = {"count": 1, "selected_slot": 1199, "selected_type": 70}
CORRUPT_READ = {
    "count": 1, "selected_slot": 1198, "selected_type": "UNKNOWN",
    "selected_type_provenance": "OSError: torn selected-unit read",
}
THRESHOLD = 0.25


def expected(seq: tuple[str, ...]) -> dict[str, object]:
    attempts = len(seq)
    errors = sum(1 for s in seq if s == "E")
    successes = attempts - errors
    successful = [s for s in seq if s != "E"]
    last_success = successful[-1] if successful else None
    unavailable = errors > 0 and (successes == 0 or seq[-1] == "E")
    coverage_short = (errors / attempts) > THRESHOLD
    present = successes > 0
    last_status = (
        None if last_success is None
        else "SOUND" if last_success == "S" else "CORRUPTED"
    )
    if not present:
        status = None
    elif (unavailable or coverage_short) and last_status == "CORRUPTED":
        status = "CORRUPTED"
    elif unavailable or coverage_short:
        status = "UNAVAILABLE"
    else:
        status = last_status
    classification = (
        "UNKNOWN_STATE_READ_FAILURE" if unavailable
        else "UNKNOWN_STATE_READ_COVERAGE" if coverage_short
        else "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED" if last_status == "CORRUPTED"
        else "FAIL_NO_EFFECT"
    )
    return {
        "selection_present": present,
        "selection_status": status,
        "classification": classification,
        "corrupted_poll_count": sum(1 for s in successful if s == "C"),
        "read_error_count": errors,
        "poll_count": successes,
    }


def observe(seq: tuple[str, ...]) -> dict[str, object]:
    sys.path.insert(0, str(ROOT))
    import tools.runtime_env as runtime_env  # noqa: PLC0415

    clock = [0.0]
    real_monotonic = runtime_env.time.monotonic
    real_sleep = runtime_env.time.sleep
    runtime_env.time.monotonic = lambda: clock[0]
    runtime_env.time.sleep = lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    pending = list(seq)
    wait_observation: dict[str, object] = {}

    def read_state(_detailed: bool) -> dict[str, object]:
        symbol = pending.pop(0)
        if symbol == "E":
            raise OSError("transient selected-unit read failed")
        return dict(SOUND_READ if symbol == "S" else CORRUPT_READ)

    try:
        try:
            runtime_env._wait_state(
                read_state,
                lambda item: runtime_env._g1_selection_responded(
                    BEFORE, item, diagnostics=wait_observation,
                ),
                started=0.0, timeout=10.0, message="selection did not change",
                stage="drag_select", stage_budget=1.0, stage_started=0.0,
                wait_observation=wait_observation,
            )
        except runtime_env._G1WaitTimeout as timeout:
            observation = timeout.observation
            selection = observation.get("selection_observation")
            return {
                "selection_present": selection is not None,
                "selection_status": selection.get("status") if selection else None,
                "classification": timeout.classification,
                "corrupted_poll_count": (
                    selection.get("corrupted_poll_count") if selection else 0
                ),
                "read_error_count": observation["read_error_count"],
                "poll_count": observation["poll_count"],
                "first_corruption_provenance": bool(
                    selection and selection.get("first_corruption_provenance")
                ),
                "poll_attempt_count": observation["poll_attempt_count"],
                "responded": False,
            }
        else:
            return {"responded": True}
    finally:
        runtime_env.time.monotonic = real_monotonic
        runtime_env.time.sleep = real_sleep


def matrix() -> dict[str, object]:
    mismatches: list[dict[str, object]] = []
    preserved = 0
    downgraded = 0
    for seq in itertools.product("SCE", repeat=4):
        want = expected(seq)
        got = observe(seq)
        if got.get("responded"):
            mismatches.append({"sequence": "".join(seq), "error": "predicate responded"})
            continue
        if got["poll_attempt_count"] != 4:
            mismatches.append({
                "sequence": "".join(seq), "error": "unexpected poll attempts",
                "poll_attempt_count": got["poll_attempt_count"],
            })
            continue
        diff = {k: {"want": v, "got": got[k]} for k, v in want.items() if got[k] != v}
        if diff:
            mismatches.append({"sequence": "".join(seq), "diff": diff})
        if want["selection_status"] == "CORRUPTED" and (
            got["read_error_count"] > 0
        ):
            preserved += 1
            if not got["first_corruption_provenance"]:
                mismatches.append({
                    "sequence": "".join(seq),
                    "error": "corruption provenance lost while status preserved",
                })
        if want["selection_status"] == "UNAVAILABLE":
            downgraded += 1
    return {
        "cases": 81,
        "mismatches": mismatches,
        "corrupted_preserved_with_read_errors": preserved,
        "sound_downgraded_to_unavailable": downgraded,
    }


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
        "lap": 248,
        "role": "middle",
        "subject": "G1-R6-B-R12 selection CORRUPTED preservation",
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
    report["c1_matrix"] = matrix()

    guard_present = GUARD_ANCHOR in RUNTIME_ENV.read_text(encoding="utf-8")
    report["guard_anchor_present"] = guard_present
    if not guard_present:
        report["c2_mirror_control"] = {"skipped": "guard anchor not found"}
        report["c3_mutations"] = {"skipped": "guard anchor not found"}
    else:
        with tempfile.TemporaryDirectory(prefix="lap248_r12_") as tmp:
            mirror = build_mirror(Path(tmp))
            target = mirror / "tools" / "runtime_env.py"
            pristine = target.read_text(encoding="utf-8")
            report["c2_mirror_control"] = run_pytest(
                mirror, ["tests/test_runtime_env.py"],
            )
            mutants: dict[str, object] = {}
            for name, replacement in MUTATIONS.items():
                target.write_text(
                    pristine.replace(GUARD_ANCHOR, replacement), encoding="utf-8",
                )
                shutil.rmtree(mirror / "tools" / "__pycache__", ignore_errors=True)
                result = run_pytest(mirror, ["tests/test_runtime_env.py"])
                killed = set(result["failed_tests"])
                result["killed_r12"] = sorted(killed & R12_TESTS)
                result["killed_unavailable"] = sorted(killed & UNAVAILABLE_TESTS)
                result["killed_other"] = sorted(killed - R12_TESTS - UNAVAILABLE_TESTS)
                mutants[name] = result
                target.write_text(pristine, encoding="utf-8")
            report["c3_mutations"] = mutants

    baseline_ok = report["c0_baseline"]["returncode"] == 0
    matrix_ok = not report["c1_matrix"]["mismatches"]
    control = report.get("c2_mirror_control", {})
    control_ok = control.get("returncode") == 0
    mutants = report.get("c3_mutations", {})
    m1 = mutants.get("M1_guard_deleted", {})
    m2 = mutants.get("M2_never_downgrades", {})
    m3 = mutants.get("M3_guard_inverted", {})
    mutation_ok = (
        m1.get("killed_r12") == sorted(R12_TESTS)
        and not m1.get("killed_unavailable")
        and not m1.get("killed_other")
        and m2.get("killed_unavailable") == sorted(UNAVAILABLE_TESTS)
        and not m2.get("killed_r12")
        and m3.get("killed_r12") == sorted(R12_TESTS)
        and m3.get("killed_unavailable") == sorted(UNAVAILABLE_TESTS)
    )
    report["verdict"] = {
        "c0_baseline": "PASS" if baseline_ok else "FAIL",
        "c1_matrix": "PASS" if matrix_ok else "FAIL",
        "c2_mirror_control": "PASS" if control_ok else "FAIL",
        "c3_mutations": "PASS" if mutation_ok else "FAIL",
        "overall": "PASS" if (
            baseline_ok and matrix_ok and control_ok and mutation_ok
        ) else "FAIL",
    }

    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(report["verdict"], indent=2))
    return 0 if report["verdict"]["overall"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
