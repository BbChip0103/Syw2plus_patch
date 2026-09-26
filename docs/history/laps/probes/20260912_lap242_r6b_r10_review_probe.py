"""lap242 middle-tier review probe for G1 R6-B-R10 probe output-path classification.

Independently re-derives, game-free, whether the lap241 repair of
``20260912_lap228_r6b_r3_review_probe.py`` really closes an unusable
``--output`` path *before* the review body runs, with a classified ``exit 2``
and no raw traceback, while keeping the R6-B-R7 protections (existing evidence
refusal, exclusive creation) and the report content unchanged.

The harness is written from scratch for this review: it does not import or
reuse ``tests/test_review_probe_output.py``.  Every case drives the shipped
probe as a subprocess against fixtures in a temporary directory.  No process
memory is read, no product asset is touched, and no game/Wine/Xvfb run is
started.  Mutation cases patch a *copy* of the probe in a temporary directory
and re-point the work tier's regression suite at that copy, so the shipped
probe file is never modified.  The report is written with exclusive creation so
an existing report is never overwritten (R6-B-R7 rule).

Questions this probe answers that the lap241 work record did not close:

1. CLASSIFICATION.  Is every unusable output shape closed with ``exit 2``, a
   classified message and no traceback -- including shapes the work tier never
   tested (deep missing parent, symlinked parent, dangling symlink, existing
   directory, non-executable parent, relative path)?
2. EARLINESS.  Is the guard genuinely *before* the review body, or merely
   before the final write?  Answered structurally (AST statement order) and
   dynamically (the refusal path never executes the case grid).
3. PRESERVATION.  Do the R6-B-R7 protections and pre-existing evidence survive,
   including the default report path that must never be clobbered?
4. SEMANTICS.  Is the report produced on a healthy path still identical to the
   stored lap228 evidence, i.e. did the guard change no measurement?
5. MUTATION SENSITIVITY.  Does the shipped regression suite actually fail when
   each guard clause is removed or weakened?
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[4]
PROBE = REPO / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
STORED_REPORT = REPO / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_report.json"
SUITE = REPO / "tests/test_review_probe_output.py"
PYTHON = sys.executable

SENTINEL = b"preserve this historical evidence\n"
NOT_A_DIR = "output parent is not a directory"
NOT_WRITABLE = "output parent is not writable"
UNAVAILABLE = "output path unavailable"
EXISTING = "refusing to overwrite existing evidence"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_probe(output: Path, *, cwd: Path | None = None) -> dict[str, Any]:
    """Drive the shipped probe once and capture everything a reviewer needs."""

    started = time.monotonic()
    completed = subprocess.run(
        [PYTHON, str(PROBE), "--output", str(output)],
        capture_output=True, text=True, check=False, cwd=None if cwd is None else str(cwd),
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "seconds": time.monotonic() - started,
    }


# ------------------------------------------------------------------- Q1/Q3 ---
# Each builder returns (output path, expected exit, expected message or None,
# a callable asserting nothing on disk was harmed).

def _case_missing_parent(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    out = tmp / "absent" / "report.json"
    return out, 2, NOT_A_DIR, lambda: not out.exists() and not out.parent.exists()


def _case_deep_missing_parent(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    out = tmp / "a" / "b" / "c" / "report.json"
    return out, 2, NOT_A_DIR, lambda: not (tmp / "a").exists()


def _case_file_parent(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    parent = tmp / "parent-file"
    parent.write_bytes(SENTINEL)
    out = parent / "report.json"
    return out, 2, NOT_A_DIR, lambda: parent.read_bytes() == SENTINEL


def _case_symlinked_file_parent(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    target = tmp / "link-target-file"
    target.write_bytes(SENTINEL)
    parent = tmp / "link-to-file"
    parent.symlink_to(target)
    out = parent / "report.json"
    return out, 2, NOT_A_DIR, lambda: target.read_bytes() == SENTINEL


def _case_dangling_symlink_parent(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    parent = tmp / "dangling-parent"
    parent.symlink_to(tmp / "never-created")
    out = parent / "report.json"
    return out, 2, NOT_A_DIR, lambda: not (tmp / "never-created").exists()


def _case_read_only_parent(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    parent = tmp / "read-only"
    parent.mkdir(mode=0o500)
    out = parent / "report.json"
    return out, 2, NOT_WRITABLE, lambda: list(parent.iterdir()) == []


def _case_non_executable_parent(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    parent = tmp / "no-search"
    parent.mkdir(mode=0o600)
    out = parent / "report.json"
    return out, 2, UNAVAILABLE, lambda: True


def _case_existing_file(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    out = tmp / "existing.json"
    out.write_bytes(SENTINEL)
    return out, 2, EXISTING, lambda: out.read_bytes() == SENTINEL


def _case_existing_directory(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    out = tmp / "existing-dir"
    out.mkdir()
    (out / "keep.txt").write_bytes(SENTINEL)
    return out, 2, EXISTING, lambda: (out / "keep.txt").read_bytes() == SENTINEL


def _case_symlink_to_existing(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    target = tmp / "real-evidence.json"
    target.write_bytes(SENTINEL)
    out = tmp / "link-to-evidence.json"
    out.symlink_to(target)
    return out, 2, EXISTING, lambda: target.read_bytes() == SENTINEL


def _case_dangling_output_symlink(tmp: Path) -> tuple[Path, int, str, Callable[[], bool]]:
    """A dangling link is not readable evidence; it must still fail closed."""

    out = tmp / "dangling-report.json"
    out.symlink_to(tmp / "no-such-target.json")
    return out, 2, None, lambda: not (tmp / "no-such-target.json").exists()


FAILING_CASES: tuple[tuple[str, Callable[[Path], tuple[Path, int, str, Callable[[], bool]]]], ...] = (
    ("C01_missing_parent", _case_missing_parent),
    ("C02_deep_missing_parent", _case_deep_missing_parent),
    ("C03_file_parent", _case_file_parent),
    ("C04_symlinked_file_parent", _case_symlinked_file_parent),
    ("C05_dangling_symlink_parent", _case_dangling_symlink_parent),
    ("C06_read_only_parent", _case_read_only_parent),
    ("C07_non_executable_parent", _case_non_executable_parent),
    ("C08_existing_file", _case_existing_file),
    ("C09_existing_directory", _case_existing_directory),
    ("C10_symlink_to_existing", _case_symlink_to_existing),
    ("C11_dangling_output_symlink", _case_dangling_output_symlink),
)


def classification_cases(tmp_root: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for name, builder in FAILING_CASES:
        tmp = tmp_root / name
        tmp.mkdir(parents=True)
        out, expected_code, expected_message, intact = builder(tmp)
        run = run_probe(out)
        message_ok = expected_message is None or expected_message in run["stdout"]
        no_traceback = "Traceback" not in run["stderr"]
        preserved = bool(intact())
        ok = (run["returncode"] == expected_code and message_ok
              and no_traceback and preserved)
        results.append({
            "id": name,
            "expected_returncode": expected_code,
            "returncode": run["returncode"],
            "expected_message": expected_message,
            "message_ok": message_ok,
            "no_traceback": no_traceback,
            "fixtures_preserved": preserved,
            "seconds": round(run["seconds"], 3),
            "stdout_tail": run["stdout"].strip().splitlines()[-1:] or [""],
            "verdict": "PASS" if ok else "DEFECT",
        })
        _restore_modes(tmp)
    return results


def _restore_modes(tmp: Path) -> None:
    """chmod fixtures back so the temporary tree can be removed."""

    for path in tmp.rglob("*"):
        if path.is_dir() and not path.is_symlink():
            path.chmod(0o700)


def healthy_cases(tmp_root: Path) -> tuple[list[dict[str, Any]], float, Path]:
    """A usable path must still produce exit 0 and a real report."""

    results: list[dict[str, Any]] = []

    plain = tmp_root / "H01_plain"
    plain.mkdir(parents=True)
    out = plain / "fresh-report.json"
    run = run_probe(out)
    report = json.loads(out.read_text(encoding="utf-8")) if out.exists() else {}
    results.append({
        "id": "H01_new_path",
        "returncode": run["returncode"],
        "report_written": out.exists(),
        "lap": report.get("lap"),
        "surgicality_verdict": report.get("summary", {}).get("surgicality_verdict"),
        "seconds": round(run["seconds"], 3),
        "verdict": "PASS" if (run["returncode"] == 0 and report.get("lap") == 228) else "DEFECT",
    })
    healthy_seconds = run["seconds"]

    linked = tmp_root / "H02_symlinked_dir_parent"
    linked.mkdir(parents=True)
    real = linked / "real-dir"
    real.mkdir()
    parent = linked / "link-to-dir"
    parent.symlink_to(real)
    out2 = parent / "report.json"
    run2 = run_probe(out2)
    results.append({
        "id": "H02_symlinked_dir_parent",
        "returncode": run2["returncode"],
        "report_written": (real / "report.json").exists(),
        "verdict": "PASS" if (run2["returncode"] == 0 and (real / "report.json").exists())
                   else "DEFECT",
    })

    relative = tmp_root / "H03_relative"
    relative.mkdir(parents=True)
    run3 = run_probe(Path("relative-report.json"), cwd=relative)
    results.append({
        "id": "H03_relative_path",
        "returncode": run3["returncode"],
        "report_written": (relative / "relative-report.json").exists(),
        "verdict": "PASS" if (run3["returncode"] == 0
                              and (relative / "relative-report.json").exists()) else "DEFECT",
    })
    return results, healthy_seconds, plain / "fresh-report.json"


# --------------------------------------------------------------------- Q2 ---

def earliness_structural() -> dict[str, Any]:
    """The guard must precede the review body in module statement order."""

    tree = ast.parse(PROBE.read_text(encoding="utf-8"))
    guard_line: int | None = None
    for node in tree.body:
        if (isinstance(node, ast.If) and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__"):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Raise):
                    guard_line = node.lineno
    body_names = {"NEGATIVE_PATTERNS", "reachability", "surgicality", "preservation", "waits"}
    body_lines = [
        node.lineno for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id in body_names for t in node.targets)
    ]
    ok = guard_line is not None and bool(body_lines) and guard_line < min(body_lines)
    return {
        "guard_statement_line": guard_line,
        "first_body_statement_line": min(body_lines) if body_lines else None,
        "body_statements_found": len(body_lines),
        "ok": ok,
    }


def earliness_dynamic(refusal_seconds: float, healthy_seconds: float) -> dict[str, Any]:
    """Wall-clock observation only.

    Interpreter start-up dominates both runs here, so the ratio cannot
    discriminate "body skipped" from "body ran fast".  It is recorded for the
    record and deliberately kept out of the verdict; ``earliness_traced`` and
    ``earliness_structural`` carry that burden instead.
    """

    return {
        "refusal_seconds": round(refusal_seconds, 3),
        "healthy_seconds": round(healthy_seconds, 3),
        "ratio": round(refusal_seconds / healthy_seconds, 3) if healthy_seconds else None,
        "verdict_input": False,
        "note": "startup-dominated; not a discriminator",
    }


def earliness_traced(tmp_root: Path) -> dict[str, Any]:
    """Trace the refusal run: no review-body function may execute."""

    tmp = tmp_root / "T01_trace"
    tmp.mkdir(parents=True)
    tracer = tmp / "trace_probe.py"
    tracer.write_text(
        "import runpy, sys\n"
        "seen = set()\n"
        "def hook(frame, event, arg):\n"
        "    if event == 'call':\n"
        "        seen.add(frame.f_code.co_name)\n"
        "    return None\n"
        "sys.argv = ['probe', '--output', sys.argv[2]]\n"
        "sys.setprofile(hook)\n"
        "code = 0\n"
        "try:\n"
        "    runpy.run_path(sys.argv[0] if False else %r, run_name='__main__')\n"
        "except SystemExit as exc:\n"
        "    code = exc.code\n"
        "finally:\n"
        "    sys.setprofile(None)\n"
        "import json\n"
        "print(json.dumps({'code': code, 'seen': sorted(seen)}))\n" % str(PROBE),
        encoding="utf-8",
    )
    out = tmp / "absent" / "report.json"
    completed = subprocess.run(
        [PYTHON, str(tracer), "--output", str(out)],
        capture_output=True, text=True, check=False,
    )
    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    body_functions = {"observe", "observe_raw", "make_reader", "legacy_predicate"}
    executed = sorted(body_functions & set(payload["seen"]))
    ok = payload["code"] == 2 and not executed and "output_refusal" in payload["seen"]
    return {
        "exit_code": payload["code"],
        "guard_executed": "output_refusal" in payload["seen"],
        "body_functions_executed": executed,
        "ok": ok,
    }


# --------------------------------------------------------------------- Q4 ---

def report_semantics(fresh_report: Path) -> dict[str, Any]:
    """The guard must not have changed a single measured value."""

    stored = json.loads(STORED_REPORT.read_text(encoding="utf-8"))
    fresh = json.loads(fresh_report.read_text(encoding="utf-8"))
    # ``source_sha256`` is the probe's own source fingerprint and must change
    # once lap241 edited the probe; everything it measures must not.
    provenance_only = {"source_sha256"}
    differing = sorted(k for k in set(stored) | set(fresh) if stored.get(k) != fresh.get(k))
    measured_differences = sorted(set(differing) - provenance_only)
    return {
        "stored_report": str(STORED_REPORT.relative_to(REPO)),
        "stored_sha256": sha256(STORED_REPORT),
        "fresh_sha256": sha256(fresh_report),
        "byte_identical": stored == fresh,
        "differing_top_level_keys": differing,
        "provenance_only_keys": sorted(provenance_only),
        "measured_differences": measured_differences,
        "ok": not measured_differences,
    }


# --------------------------------------------------------------------- Q5 ---

MUTATIONS: tuple[tuple[str, str, str], ...] = (
    ("M1_drop_is_dir_check",
     '        if not parent.is_dir():\n'
     '            return f"refusing to write evidence: output parent is not a directory: {parent}"\n',
     ''),
    ("M2_drop_access_check",
     '        if not os.access(parent, os.W_OK | os.X_OK):\n'
     '            return f"refusing to write evidence: output parent is not writable: {parent}"\n',
     ''),
    ("M3_drop_exists_check",
     '        if path.exists():\n'
     '            return f"refusing to overwrite existing evidence: {path}"\n',
     ''),
    ("M4_guard_exit_zero",
     '        raise SystemExit(2)\n',
     '        raise SystemExit(0)\n'),
    ("M5_guard_raises_raw",
     '        print(refusal)\n        raise SystemExit(2)\n',
     '        raise OSError(refusal)\n'),
)


def _mirror(tmp: Path, probe_source: str) -> Path:
    """Place the probe copy where its own ``parents[4]`` root resolves.

    The probe computes ``ROOT = Path(__file__).resolve().parents[4]`` and loads
    ``ROOT/tools/runtime_env.py``.  A flat temporary copy therefore dies at
    import before any mutation can be observed, which would make every mutant
    look "detected" for the wrong reason.  The mirror reproduces the depth and
    ships a *copy* of ``runtime_env.py`` so the real source is never loaded
    from a mutated tree.
    """

    probes = tmp / "mirror" / "docs" / "history" / "laps" / "probes"
    probes.mkdir(parents=True)
    tools = tmp / "mirror" / "tools"
    tools.mkdir(parents=True)
    shutil.copy2(REPO / "tools" / "runtime_env.py", tools / "runtime_env.py")
    copy = probes / PROBE.name
    copy.write_text(probe_source, encoding="utf-8")
    return copy


def _run_suite_against(copy: Path, tmp: Path, suite_source: str) -> subprocess.CompletedProcess[str]:
    suite = tmp / "test_mutated_probe_output.py"
    suite.write_text(
        re.sub(
            r'PROBE = ROOT / "docs/history/laps/probes/[^"]+"',
            f"PROBE = Path({str(copy)!r})",
            suite_source,
        ),
        encoding="utf-8",
    )
    return subprocess.run(
        [PYTHON, "-m", "pytest", "-q", str(suite)],
        capture_output=True, text=True, check=False, cwd=str(REPO),
    )


def mutation_cases(tmp_root: Path) -> list[dict[str, Any]]:
    """Re-point the shipped suite at a mirrored copy; every mutant must fail.

    ``M0_control`` is the unmutated copy: it must pass, otherwise the mutant
    failures prove nothing about the guard.
    """

    source = PROBE.read_text(encoding="utf-8")
    suite_source = SUITE.read_text(encoding="utf-8")
    results: list[dict[str, Any]] = []

    control_tmp = tmp_root / "M0_control"
    control_tmp.mkdir(parents=True)
    control = _run_suite_against(_mirror(control_tmp, source), control_tmp, suite_source)
    results.append({
        "id": "M0_control",
        "mutation_applied": False,
        "suite_returncode": control.returncode,
        "detected": control.returncode == 0,
        "summary_line": control.stdout.strip().splitlines()[-1:] or [""],
        "verdict": "PASS" if control.returncode == 0 else "DEFECT",
    })

    for name, old, new_text in MUTATIONS:
        tmp = tmp_root / name
        tmp.mkdir(parents=True)
        applied = source.replace(old, new_text, 1)
        completed = _run_suite_against(_mirror(tmp, applied), tmp, suite_source)
        detected = applied != source and completed.returncode != 0
        results.append({
            "id": name,
            "mutation_applied": applied != source,
            "suite_returncode": completed.returncode,
            "detected": detected,
            "summary_line": completed.stdout.strip().splitlines()[-1:] or [""],
            "verdict": "PASS" if detected else "DEFECT",
        })
    return results


def baseline_suite() -> dict[str, Any]:
    """The unmutated suite must pass, or mutation detection means nothing."""

    completed = subprocess.run(
        [PYTHON, "-m", "pytest", "-q", str(SUITE)],
        capture_output=True, text=True, check=False, cwd=str(REPO),
    )
    return {
        "returncode": completed.returncode,
        "summary_line": (completed.stdout.strip().splitlines() or [""])[-1],
        "ok": completed.returncode == 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path,
                        default=Path(__file__).with_name(
                            "20260912_lap242_r6b_r10_review_report.json"))
    args = parser.parse_args(argv)
    if args.report.exists():
        print(f"refusing to overwrite existing evidence: {args.report}")
        return 2

    default_report_before = sha256(STORED_REPORT)
    with tempfile.TemporaryDirectory(prefix="lap242_r10_") as raw:
        tmp_root = Path(raw)
        classification = classification_cases(tmp_root / "classification")
        healthy, healthy_seconds, fresh_report = healthy_cases(tmp_root / "healthy")
        refusal_seconds = min(case["seconds"] for case in classification
                              if case["id"].startswith(("C01", "C02", "C03")))
        structural = earliness_structural()
        dynamic = earliness_dynamic(refusal_seconds, healthy_seconds)
        traced = earliness_traced(tmp_root / "trace")
        semantics = report_semantics(fresh_report)
        baseline = baseline_suite()
        mutations = mutation_cases(tmp_root / "mutations")

    default_report_after = sha256(STORED_REPORT)

    defects = [case["id"] for case in classification + healthy if case["verdict"] == "DEFECT"]
    undetected = [case["id"] for case in mutations if not case["detected"]]
    control_ok = all(case["detected"] for case in mutations if case["id"] == "M0_control")
    ok = (not defects and not undetected and control_ok and structural["ok"]
          and traced["ok"] and semantics["ok"] and baseline["ok"]
          and default_report_before == default_report_after)

    report = {
        "lap": 242,
        "tier": "middle",
        "subject": "G1 R6-B-R10 review-probe output-path classification",
        "reviewed_files": {
            str(PROBE.relative_to(REPO)): sha256(PROBE),
            str(SUITE.relative_to(REPO)): sha256(SUITE),
        },
        "classification": classification,
        "healthy": healthy,
        "earliness_structural": structural,
        "earliness_dynamic": dynamic,
        "earliness_traced": traced,
        "report_semantics": semantics,
        "baseline_suite": baseline,
        "mutations": mutations,
        "stored_report_sha256_before": default_report_before,
        "stored_report_sha256_after": default_report_after,
        "summary": {
            "classification_cases": len(classification),
            "healthy_cases": len(healthy),
            "defects": defects,
            "mutation_control_passes": control_ok,
            "mutations_total": len(MUTATIONS),
            "mutations_detected": len(MUTATIONS) - len(undetected),
            "undetected_mutations": undetected,
        },
        "verdict": "PASS" if ok else "FAIL",
    }
    with open(args.report, "x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    print(f"verdict={report['verdict']} report -> {args.report}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
