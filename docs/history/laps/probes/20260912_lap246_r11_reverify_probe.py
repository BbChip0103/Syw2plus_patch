#!/usr/bin/env python3
"""lap246 middle: independent re-review of the lap245 G1-R6-B-R11 regression.

Written for this review.  It reuses no lap245 harness object: the mutation
mirror, the controls and the failure accounting are rebuilt here.

The lap245 work record claims the new dangling-symlink regression in
``tests/test_review_probe_output.py`` is non-vacuous because mutating the
lap228 probe's ``open("x")`` into ``open("w")`` produced "8 failed" including
the R11 test.  A mutation that kills *every* test in the file is the shape of
a broken mirror, not of a targeted guard: the R7 refusal, the R10 parent
classifications and the R17 earliness case are all decided by the preflight
``output_refusal`` and can never observe the writer's open mode.  This probe
answers four questions the lap245 record did not close:

C0. BASELINE.  Do the 8 shipped regressions pass against the real probe?
C1. MIRROR CONTROL.  Does an *unmutated* probe copy, relocated the way lap245
    relocated it (a shallow ``/tmp`` directory), still pass?  If it does not,
    the lap245 "8 failed" carries no mutation information at all.
C2. FAITHFUL MIRROR.  Does an unmutated copy at the depth the probe's own
    ``parents[4]`` root resolution requires reproduce the baseline?
C3. TARGETED MUTATION.  Against that faithful mirror, which tests does
    ``open("x") -> open("w")`` actually kill, and does the R11 case die for
    the right reason (the truncating writer follows the dangling symlink and
    creates the target it must refuse to touch)?

The report path is guarded before the body runs (R6-B-R7/R10 conventions) and
is written with exclusive creation (R6-B-R11).
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
PROBE = ROOT / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TEST = ROOT / "tests/test_review_probe_output.py"
RUNTIME_ENV = ROOT / "tools" / "runtime_env.py"
PROBE_ANCHOR = '    with args.output.open("x", encoding="utf-8") as stream:'
PROBE_MUTATION = '    with args.output.open("w", encoding="utf-8") as stream:'
PROBE_DECLARATION = (
    "PROBE = ROOT / "
    '"docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"'
)
R11_TEST = "test_r6b_r11_exclusive_create_rejects_dangling_output_symlink"
PREFLIGHT_TESTS = {
    "test_r6b_r7_refuses_to_overwrite_existing_report",
    "test_r6b_r10_rejects_missing_parent_before_running_probe",
    "test_r6b_r10_rejects_non_directory_parent",
    "test_r6b_r10_rejects_read_only_parent",
    "test_r6b_r10_classifies_non_searchable_parent_without_traceback",
    "test_r6b_r17_existing_evidence_refusal_precedes_review_body",
}


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


def _failed(stdout: str) -> list[str]:
    return sorted(
        line.split("::")[-1].split()[0]
        for line in stdout.splitlines()
        if line.startswith("FAILED ") and "::" in line
    )


def _tail(text: str, lines: int = 4) -> list[str]:
    return text.strip().splitlines()[-lines:]


def run_pytest(test_file: Path) -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(test_file)],
        cwd=str(ROOT), capture_output=True, text=True, check=False,
    )
    return {
        "returncode": result.returncode,
        "failed_tests": _failed(result.stdout),
        "stdout_tail": _tail(result.stdout),
        "stderr_tail": _tail(result.stderr),
    }


def write_case(work: Path, *, layout: str, mutate: bool) -> Path:
    """Materialise a probe copy plus a test file pointed at that copy."""

    if layout == "shallow":            # the lap245 relocation
        probe_dir = work
    else:                              # parents[4]-faithful mirror
        probe_dir = work / "docs" / "history" / "laps" / "probes"
        probe_dir.mkdir(parents=True)
        (work / "tools").mkdir()
        shutil.copyfile(RUNTIME_ENV, work / "tools" / "runtime_env.py")
    source = PROBE.read_text(encoding="utf-8")
    if source.count(PROBE_ANCHOR) != 1:
        raise SystemExit("exclusive-create anchor is not unique")
    if mutate:
        source = source.replace(PROBE_ANCHOR, PROBE_MUTATION, 1)
    probe_copy = probe_dir / PROBE.name
    probe_copy.write_text(source, encoding="utf-8")

    test_source = TEST.read_text(encoding="utf-8")
    if test_source.count(PROBE_DECLARATION) != 1:
        raise SystemExit("test probe declaration anchor is not unique")
    test_copy = work / TEST.name
    test_copy.write_text(
        test_source.replace(
            PROBE_DECLARATION, f"PROBE = Path({str(probe_copy)!r})", 1),
        encoding="utf-8")
    return test_copy


def direct_r11_behaviour(work: Path, *, mutate: bool) -> dict:
    """Drive the dangling-symlink case straight at the probe copy."""

    case = work / ("direct_mutated" if mutate else "direct_control")
    case.mkdir()
    test_file = write_case(case, layout="mirror", mutate=mutate)
    probe_copy = case / "docs/history/laps/probes" / PROBE.name
    scratch = case / "scratch"
    scratch.mkdir()
    target = scratch / "future-report.json"
    link = scratch / "report.json"
    link.symlink_to(target)
    result = subprocess.run(
        [sys.executable, str(probe_copy), "--output", str(link)],
        cwd=str(ROOT), capture_output=True, text=True, check=False)
    return {
        "test_file": str(test_file),
        "returncode": result.returncode,
        "stdout_tail": _tail(result.stdout, 2),
        "stderr_tail": _tail(result.stderr, 2),
        "link_still_symlink": link.is_symlink(),
        "target_created": target.exists(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    refusal = output_refusal(args.output)
    if refusal is not None:
        print(refusal)
        return 2

    cases: dict[str, dict] = {}
    cases["C0_baseline_real_probe"] = run_pytest(TEST)
    with tempfile.TemporaryDirectory(prefix="lap246_r11_") as raw:
        work = Path(raw)
        shallow = work / "shallow"
        shallow.mkdir()
        cases["C1_unmutated_shallow_copy"] = run_pytest(
            write_case(shallow, layout="shallow", mutate=False))
        mirror = work / "mirror"
        mirror.mkdir()
        cases["C2_unmutated_faithful_mirror"] = run_pytest(
            write_case(mirror, layout="mirror", mutate=False))
        mutated = work / "mutated"
        mutated.mkdir()
        cases["C3_mutated_faithful_mirror"] = run_pytest(
            write_case(mutated, layout="mirror", mutate=True))
        direct = {
            "control_x_mode": direct_r11_behaviour(work, mutate=False),
            "mutated_w_mode": direct_r11_behaviour(work, mutate=True),
        }

    c1, c2, c3 = (cases["C1_unmutated_shallow_copy"],
                  cases["C2_unmutated_faithful_mirror"],
                  cases["C3_mutated_faithful_mirror"])
    findings = {
        "baseline_green": cases["C0_baseline_real_probe"]["returncode"] == 0,
        "lap245_mutation_signal_vacuous": c1["returncode"] != 0,
        "lap245_unmutated_shallow_failures": len(c1["failed_tests"]),
        "faithful_mirror_green": c2["returncode"] == 0,
        "targeted_mutation_failures": c3["failed_tests"],
        "targeted_mutation_kills_r11_only": c3["failed_tests"] == [R11_TEST],
        "preflight_tests_survive_mutation": not (
            set(c3["failed_tests"]) & PREFLIGHT_TESTS),
        "control_refuses_dangling_symlink": (
            direct["control_x_mode"]["returncode"] == 2
            and not direct["control_x_mode"]["target_created"]),
        "mutation_writes_through_dangling_symlink": (
            direct["mutated_w_mode"]["target_created"]),
    }
    r11_non_vacuous = (
        findings["baseline_green"]
        and findings["faithful_mirror_green"]
        and R11_TEST in c3["failed_tests"]
        and findings["control_refuses_dangling_symlink"]
        and findings["mutation_writes_through_dangling_symlink"])
    report = {
        "lap": 246,
        "role": "middle",
        "target": "G1-R6-B-R11 (lap245 work)",
        "game_executions": 0,
        "probe_sha256": hashlib.sha256(PROBE.read_bytes()).hexdigest(),
        "test_sha256": hashlib.sha256(TEST.read_bytes()).hexdigest(),
        "runtime_env_sha256": hashlib.sha256(RUNTIME_ENV.read_bytes()).hexdigest(),
        "cases": cases,
        "direct_r11_behaviour": direct,
        "findings": findings,
        "verdict": {
            "r11_regression_non_vacuous": r11_non_vacuous,
            "lap245_evidence_valid": not findings["lap245_mutation_signal_vacuous"],
        },
    }
    try:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError:
        print(f"refusing to overwrite existing evidence: {args.output}")
        return 2
    except OSError as exc:
        print(f"refusing to write evidence: {args.output}: {exc}")
        return 2
    print(json.dumps({"findings": findings, "verdict": report["verdict"]},
                     indent=2, sort_keys=True))
    print(f"report -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
