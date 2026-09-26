#!/usr/bin/env python3
"""lap244 middle: independent re-review of the lap243 G1-R6-B-R10 repair.

Written for this review.  It imports no repository test helper, reuses no
lap242/lap243 fixture or report, and never runs the game.  The subject under
test (SUT) is the shipped review probe

    docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py

whose evidence-output boundary lap243 repaired after the lap242 middle review
returned FAIL:

  R6-B-R7   an existing report must never be overwritten.
  R6-B-R10  an unusable output path must be classified *before* the probe body
            runs, with a fail-closed ``exit 2`` and no raw traceback.
  R6-B-R16  a non-searchable output parent makes ``Path.exists()`` raise
            ``PermissionError``; that must be classified, not leaked.
  R6-B-R17  the early existing-evidence refusal must be a real early exit, and
            deleting it must be detected by the shipped regression.

Five questions the lap243 work record does not close on its own:

Q1 CLASSIFICATION.  Does the shipped guard classify every reachable unusable
   output path fail-closed, including shapes the repo tests do not cover
   (deep-missing parent, symlinked parents, an existing directory at the
   output path, a write-only parent)?
Q2 EARLINESS.  Measured independently of lap243's call profiler -- by line
   tracing the SUT file itself -- does *no* module-level body statement run on
   any refusal, with a healthy run as the positive control for the tracer?
Q3 MUTATION.  Against a mirrored copy of the SUT, does the shipped regression
   suite actually fail for each way the repair can be removed?  A regression
   that cannot fail is not evidence.
Q4 SEMANTICS.  Is the written report a real measurement (deterministic across
   fresh paths, bound to the reviewed runtime_env source, zero game runs)?
Q5 PROVENANCE.  Do the reviewed artefacts still hash to the lap243 record, and
   are the protected files untouched by this review?

No product EXE/DLL/asset/baseline/golden file is read or written, and this
probe never modifies the SUT: mutations are applied to copies inside a
temporary tree.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[4]
SUT = ROOT / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TESTS = ROOT / "tests/test_review_probe_output.py"
RUNTIME = ROOT / "tools/runtime_env.py"
PY = sys.executable

DEFAULT_OUTPUT = Path(__file__).with_name(
    "20260912_lap244_r6b_r10_reverify_report.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_refusal(path: Path) -> str | None:
    """This probe holds itself to the same evidence-output contract."""

    try:
        if path.exists():
            return f"refusing to overwrite existing evidence: {path}"
        parent = path.parent
        if not parent.is_dir():
            return f"refusing to write evidence: parent is not a directory: {parent}"
        if not os.access(parent, os.W_OK | os.X_OK):
            return f"refusing to write evidence: parent is not writable: {parent}"
    except OSError as exc:
        return f"refusing to write evidence: output path unavailable: {path}: {exc}"
    return None


def run_sut(output: Path, *, cwd: Path | None = None) -> dict[str, Any]:
    proc = subprocess.run(
        [PY, str(SUT), "--output", str(output)],
        capture_output=True, text=True, check=False,
        cwd=str(cwd) if cwd else None,
    )
    return {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


# ------------------------------------------------------------------- Q1 -----
# Each case builds a fixture directory, returns the --output path it should be
# driven with, and a checker that the fixture survived untouched.
CaseBuilder = Callable[[Path], tuple[Path, Callable[[], bool], Path | None]]


def _mode_guard(path: Path, mode: int) -> None:
    path.chmod(mode)


def safe_exists(path: Path) -> bool | None:
    """``None`` when the path cannot even be interrogated (unsearchable parent)."""

    try:
        return path.exists()
    except OSError:
        return None


def build_cases() -> list[dict[str, Any]]:
    """(id, intent, builder, expected exit, expected classification token)."""

    def missing_parent(d: Path):
        return d / "nope" / "report.json", lambda: not (d / "nope").exists(), None

    def deep_missing_parent(d: Path):
        return d / "a" / "b" / "c" / "report.json", lambda: not (d / "a").exists(), None

    def parent_is_file(d: Path):
        parent = d / "parent-file"
        parent.write_text("not a directory\n", encoding="utf-8")
        return (parent / "report.json",
                lambda: parent.read_text(encoding="utf-8") == "not a directory\n",
                None)

    def parent_symlink_to_file(d: Path):
        target = d / "target-file"
        target.write_text("payload\n", encoding="utf-8")
        link = d / "link-to-file"
        link.symlink_to(target)
        return (link / "report.json",
                lambda: target.read_text(encoding="utf-8") == "payload\n",
                None)

    def parent_dangling_symlink(d: Path):
        link = d / "dangling"
        link.symlink_to(d / "does-not-exist")
        return link / "report.json", lambda: link.is_symlink(), None

    def read_only_parent(d: Path):
        parent = d / "read-only"
        parent.mkdir()
        parent.chmod(0o500)
        return parent / "report.json", lambda: True, parent

    def non_searchable_parent(d: Path):
        parent = d / "no-search"
        parent.mkdir()
        parent.chmod(0o600)
        return parent / "report.json", lambda: True, parent

    def write_only_parent(d: Path):
        parent = d / "write-only"
        parent.mkdir()
        parent.chmod(0o300)
        return parent / "report.json", lambda: True, parent

    def existing_evidence(d: Path):
        out = d / "existing-report.json"
        out.write_bytes(b"preserve this historical evidence\n")
        return (out,
                lambda: out.read_bytes() == b"preserve this historical evidence\n",
                None)

    def existing_directory_at_output(d: Path):
        out = d / "report.json"
        out.mkdir()
        (out / "keep").write_text("inner\n", encoding="utf-8")
        return out, lambda: (out / "keep").is_file(), None

    def existing_symlinked_evidence(d: Path):
        target = d / "real-report.json"
        target.write_bytes(b"historical\n")
        link = d / "link-report.json"
        link.symlink_to(target)
        return link, lambda: target.read_bytes() == b"historical\n", None

    def healthy_new_path(d: Path):
        return d / "fresh.json", lambda: True, None

    def healthy_parent_symlink(d: Path):
        real = d / "real-dir"
        real.mkdir()
        link = d / "link-dir"
        link.symlink_to(real, target_is_directory=True)
        return link / "fresh.json", lambda: True, None

    def healthy_nested(d: Path):
        nested = d / "x" / "y"
        nested.mkdir(parents=True)
        return nested / "fresh.json", lambda: True, None

    return [
        {"id": "C01_missing_parent", "build": missing_parent, "exit": 2,
         "token": "output parent is not a directory"},
        {"id": "C02_deep_missing_parent", "build": deep_missing_parent, "exit": 2,
         "token": "output parent is not a directory"},
        {"id": "C03_parent_is_file", "build": parent_is_file, "exit": 2,
         "token": "output parent is not a directory"},
        {"id": "C04_parent_symlink_to_file", "build": parent_symlink_to_file, "exit": 2,
         "token": "output parent is not a directory"},
        {"id": "C05_parent_dangling_symlink", "build": parent_dangling_symlink, "exit": 2,
         "token": "output parent is not a directory"},
        {"id": "C06_read_only_parent", "build": read_only_parent, "exit": 2,
         "token": "output parent is not writable"},
        {"id": "C07_non_searchable_parent", "build": non_searchable_parent, "exit": 2,
         "token": "output path unavailable"},
        {"id": "C08_write_only_parent", "build": write_only_parent, "exit": 0,
         "token": "report -> "},
        {"id": "C09_existing_evidence", "build": existing_evidence, "exit": 2,
         "token": "refusing to overwrite existing evidence"},
        {"id": "C10_existing_directory_at_output", "build": existing_directory_at_output,
         "exit": 2, "token": "refusing to overwrite existing evidence"},
        {"id": "C11_existing_symlinked_evidence", "build": existing_symlinked_evidence,
         "exit": 2, "token": "refusing to overwrite existing evidence"},
        {"id": "C12_healthy_new_path", "build": healthy_new_path, "exit": 0,
         "token": "report -> "},
        {"id": "C13_healthy_parent_symlink", "build": healthy_parent_symlink, "exit": 0,
         "token": "report -> "},
        {"id": "C14_healthy_nested", "build": healthy_nested, "exit": 0,
         "token": "report -> "},
    ]


def classification_matrix(workdir: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for case in build_cases():
        d = workdir / case["id"]
        d.mkdir(parents=True)
        restore: Path | None = None
        try:
            output, preserved, restore = case["build"](d)
            existed_before = safe_exists(output)
            run = run_sut(output)
            fixture_ok = preserved()
            wrote = output.exists() if restore is None else None
        finally:
            if restore is not None:
                _mode_guard(restore, 0o700)
                wrote = output.exists()
        entry = {
            "id": case["id"],
            "expect_exit": case["exit"],
            "expect_token": case["token"],
            "exit": run["exit"],
            "stdout_tail": run["stdout"].strip().splitlines()[-1] if run["stdout"].strip() else "",
            "token_present": case["token"] in run["stdout"],
            "traceback": "Traceback" in run["stderr"],
            "stderr_len": len(run["stderr"]),
            "fixture_preserved": fixture_ok,
            "existed_before": existed_before,
            "exists_after": bool(wrote),
        }
        # A refusal must leave the filesystem exactly as it found it; a healthy
        # run must create a report that was not already there.
        if case["exit"] == 0:
            path_ok = not bool(existed_before) and bool(wrote)
        else:
            path_ok = bool(wrote) == bool(existed_before)
        entry["path_state_ok"] = path_ok
        entry["verdict"] = "AGREES" if (
            entry["exit"] == case["exit"]
            and entry["token_present"]
            and not entry["traceback"]
            and entry["fixture_preserved"]
            and path_ok
        ) else "DEFECT"
        results.append(entry)
    return results


# ------------------------------------------------------------------- Q2 -----
TRACER = """
import json, runpy, sys
target = sys.argv[1]
output = sys.argv[2]
lines = set()
def local(frame, event, arg):
    if event == 'line' and frame.f_code.co_filename == target:
        lines.add(frame.f_lineno)
    return local
def glob(frame, event, arg):
    if frame.f_code.co_filename == target:
        return local
    return None
sys.argv = [target, '--output', output]
code = 0
sys.settrace(glob)
try:
    runpy.run_path(target, run_name='__main__')
except SystemExit as exc:
    code = exc.code if isinstance(exc.code, int) else 1
finally:
    sys.settrace(None)
sys.stderr.write('TRACE ' + json.dumps({'code': code, 'lines': sorted(lines)}) + '\\n')
"""


def body_line_numbers() -> tuple[set[int], int]:
    """Module-level statements that belong to the probe *body* (after the guard)."""

    tree = ast.parse(SUT.read_text(encoding="utf-8"), filename=str(SUT))
    guard_end = None
    for node in tree.body:
        if (isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"):
            guard_end = node.end_lineno
    assert guard_end is not None, "no __main__ guard found in the SUT"
    body: set[int] = set()
    for node in tree.body:
        if node.lineno > guard_end:
            body.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return body, guard_end


def earliness_matrix(workdir: Path) -> list[dict[str, Any]]:
    body, guard_end = body_line_numbers()
    workdir.mkdir(parents=True, exist_ok=True)
    tracer = workdir / "line_tracer.py"
    tracer.write_text(TRACER, encoding="utf-8")
    scenarios = [
        ("E01_existing_evidence", "refusal"),
        ("E02_missing_parent", "refusal"),
        ("E03_parent_is_file", "refusal"),
        ("E04_read_only_parent", "refusal"),
        ("E05_non_searchable_parent", "refusal"),
        ("E06_healthy_control", "healthy"),
    ]
    results: list[dict[str, Any]] = []
    for case_id, kind in scenarios:
        d = workdir / case_id
        d.mkdir()
        restore: Path | None = None
        if case_id == "E01_existing_evidence":
            output = d / "report.json"
            output.write_bytes(b"historical\n")
        elif case_id == "E02_missing_parent":
            output = d / "gone" / "report.json"
        elif case_id == "E03_parent_is_file":
            parent = d / "file"
            parent.write_text("x\n", encoding="utf-8")
            output = parent / "report.json"
        elif case_id == "E04_read_only_parent":
            parent = d / "ro"
            parent.mkdir()
            parent.chmod(0o500)
            restore = parent
            output = parent / "report.json"
        elif case_id == "E05_non_searchable_parent":
            parent = d / "ns"
            parent.mkdir()
            parent.chmod(0o600)
            restore = parent
            output = parent / "report.json"
        else:
            output = d / "fresh.json"
        try:
            proc = subprocess.run(
                [PY, str(tracer), str(SUT), str(output)],
                capture_output=True, text=True, check=False,
            )
        finally:
            if restore is not None:
                restore.chmod(0o700)
        trace_line = [ln for ln in proc.stderr.splitlines() if ln.startswith("TRACE ")]
        payload = json.loads(trace_line[-1][len("TRACE "):]) if trace_line else {}
        traced = set(payload.get("lines", []))
        body_hits = sorted(traced & body)
        entry = {
            "id": case_id, "kind": kind, "exit": payload.get("code"),
            "guard_end_line": guard_end,
            "max_traced_line": max(traced) if traced else None,
            "body_lines_executed": body_hits[:12],
            "body_line_count": len(body_hits),
            "traceback": "Traceback" in proc.stderr,
        }
        if kind == "refusal":
            entry["verdict"] = "AGREES" if (
                entry["exit"] == 2 and not body_hits and not entry["traceback"]
            ) else "DEFECT"
        else:
            # Positive control: the tracer must be able to see body lines at all.
            entry["verdict"] = "AGREES" if (
                entry["exit"] in (0, None) and len(body_hits) > 50
            ) else "DEFECT"
        results.append(entry)
    return results


# ------------------------------------------------------------------- Q3 -----
MUTATIONS: list[dict[str, str]] = [
    {"id": "M0_control", "old": "", "new": "",
     "intent": "unmutated mirror: the shipped regression must pass",
     "expect": "pass"},
    {"id": "M1_drop_oserror_failclose",
     "old": "    except OSError as exc:\n"
            "        return f\"refusing to write evidence: output path unavailable: {path}: {exc}\"\n",
     "new": "    except ZeroDivisionError as exc:\n"
            "        return f\"refusing to write evidence: output path unavailable: {path}: {exc}\"\n",
     "intent": "R16 removed: PermissionError from exists() leaks as a traceback",
     "expect": "fail"},
    {"id": "M2_drop_early_existing_check",
     "old": "        if path.exists():\n"
            "            return f\"refusing to overwrite existing evidence: {path}\"\n\n",
     "new": "",
     "intent": "R17 removed: the existing-evidence refusal only happens after the body",
     "expect": "fail"},
    {"id": "M3_wrong_exit_code",
     "old": "        print(refusal)\n        raise SystemExit(2)\n",
     "new": "        print(refusal)\n        raise SystemExit(3)\n",
     "intent": "classified refusal stops being the fail-closed exit 2",
     "expect": "fail"},
    {"id": "M4_drop_writability_check",
     "old": "        if not os.access(parent, os.W_OK | os.X_OK):\n"
            "            return f\"refusing to write evidence: output parent is not writable: {parent}\"\n",
     "new": "",
     "intent": "read-only parent is only caught late by the exclusive create",
     "expect": "fail"},
    {"id": "M5_drop_isdir_check",
     "old": "        if not parent.is_dir():\n"
            "            return f\"refusing to write evidence: output parent is not a directory: {parent}\"\n",
     "new": "",
     "intent": "missing / non-directory parent loses its classification",
     "expect": "fail"},
]


def mutation_matrix(workdir: Path) -> list[dict[str, Any]]:
    source = SUT.read_text(encoding="utf-8")
    results: list[dict[str, Any]] = []
    for mutation in MUTATIONS:
        d = workdir / mutation["id"]
        probes = d / "docs/history/laps/probes"
        probes.mkdir(parents=True)
        (d / "tests").mkdir()
        (d / "tools").symlink_to(ROOT / "tools", target_is_directory=True)
        if mutation["old"]:
            applied = source.count(mutation["old"])
            mutated = source.replace(mutation["old"], mutation["new"])
        else:
            applied = 1
            mutated = source
        (probes / SUT.name).write_text(mutated, encoding="utf-8")
        shutil.copy2(TESTS, d / "tests" / TESTS.name)
        syntax_ok = True
        try:
            ast.parse(mutated)
        except SyntaxError:
            syntax_ok = False
        proc = subprocess.run(
            [PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=no", "-rf",
             str(d / "tests" / TESTS.name)],
            capture_output=True, text=True, check=False, cwd=str(d),
        )
        failed = sorted({ln.split("::")[-1].split(" ")[0]
                         for ln in proc.stdout.splitlines() if ln.startswith("FAILED")})
        entry = {
            "id": mutation["id"], "intent": mutation["intent"],
            "expect": mutation["expect"],
            "occurrences_replaced": applied,
            "source_changed": mutated != source or mutation["id"] == "M0_control",
            "syntax_ok": syntax_ok,
            "pytest_exit": proc.returncode,
            "failed_tests": failed,
            "summary": proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "",
        }
        if mutation["expect"] == "pass":
            entry["verdict"] = "AGREES" if (proc.returncode == 0 and not failed) else "DEFECT"
        else:
            entry["verdict"] = "AGREES" if (
                applied == 1 and syntax_ok and proc.returncode != 0 and failed
            ) else "DEFECT"
        results.append(entry)
    return results


# ------------------------------------------------------------------- Q4 -----
def report_semantics(workdir: Path) -> dict[str, Any]:
    d = workdir / "semantics"
    d.mkdir(parents=True, exist_ok=True)
    first, second = d / "run1.json", d / "run2.json"
    run_a = run_sut(first)
    run_b = run_sut(second)
    body_a = json.loads(first.read_text(encoding="utf-8"))
    body_b = json.loads(second.read_text(encoding="utf-8"))
    rerun = run_sut(first)
    unchanged = first.read_text(encoding="utf-8") == json.dumps(
        body_a, indent=2, sort_keys=True) + "\n"
    return {
        "run_a_exit": run_a["exit"], "run_b_exit": run_b["exit"],
        "deterministic_across_paths": body_a == body_b,
        "source_sha256_matches_runtime_env": body_a.get("source_sha256") == sha256(RUNTIME),
        "game_executions": body_a.get("game_executions"),
        "surgicality_cases": body_a.get("surgicality", {}).get("cases"),
        "summary": body_a.get("summary"),
        "rerun_exit": rerun["exit"],
        "rerun_refused": "refusing to overwrite existing evidence" in rerun["stdout"],
        "rerun_left_file_unchanged": unchanged,
        "verdict": "AGREES" if (
            run_a["exit"] == 0 and run_b["exit"] == 0
            and body_a == body_b
            and body_a.get("source_sha256") == sha256(RUNTIME)
            and body_a.get("game_executions") == 0
            and body_a.get("summary", {}).get("surgicality_verdict") == "AGREES"
            and not body_a.get("summary", {}).get("reachability_defects")
            and not body_a.get("summary", {}).get("preservation_defects")
            and not body_a.get("summary", {}).get("wait_defects")
            and rerun["exit"] == 2 and unchanged
        ) else "DEFECT",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="lap244 middle R6-B-R10 re-review")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    refusal = output_refusal(args.output)
    if refusal is not None:
        print(refusal)
        return 2

    euid = os.geteuid()
    if euid == 0:
        print("refusing to measure permission cases as root: results would be meaningless")
        return 2

    before = {p.name: sha256(p) for p in (SUT, TESTS, RUNTIME)}
    with tempfile.TemporaryDirectory(prefix="lap244_r10_") as tmp:
        workdir = Path(tmp)
        classification = classification_matrix(workdir / "classification")
        earliness = earliness_matrix(workdir / "earliness")
        mutations = mutation_matrix(workdir / "mutation")
        semantics = report_semantics(workdir / "semantics_root")
    after = {p.name: sha256(p) for p in (SUT, TESTS, RUNTIME)}

    defects = (
        [c["id"] for c in classification if c["verdict"] == "DEFECT"]
        + [e["id"] for e in earliness if e["verdict"] == "DEFECT"]
        + [m["id"] for m in mutations if m["verdict"] == "DEFECT"]
        + ([] if semantics["verdict"] == "AGREES" else ["Q4_report_semantics"])
    )
    verdict = "PASS" if not defects and before == after else "FAIL"
    report = {
        "lap": 244, "role": "middle", "target": "G1-R6-B-R10/R16/R17 (lap243 repair)",
        "python": sys.version.split()[0], "euid": euid,
        "game_executions": 0,
        "artefact_sha256_before": before,
        "artefact_sha256_after": after,
        "classification": classification,
        "earliness": earliness,
        "mutation": mutations,
        "report_semantics": semantics,
        "summary": {
            "classification_defects": [c["id"] for c in classification if c["verdict"] == "DEFECT"],
            "earliness_defects": [e["id"] for e in earliness if e["verdict"] == "DEFECT"],
            "mutation_defects": [m["id"] for m in mutations if m["verdict"] == "DEFECT"],
            "semantics_verdict": semantics["verdict"],
            "artefacts_unchanged": before == after,
        },
        "verdict": verdict,
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
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"verdict={verdict}")
    print(f"report -> {args.output}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
