#!/usr/bin/env python3
"""lap236 middle-tier non-vacuity check for `tests/test_review_probe_output.py`.

Copies the lap228 review probe and the lap235 regression test into a throwaway
directory, applies guard-weakening mutations to the copy only, and records which
mutations the regression test actually catches.  The repository files are never
modified.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
PROBE = ROOT / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TEST = ROOT / "tests/test_review_probe_output.py"

EXISTS_GUARD = """    if args.output.exists():
        print(f"refusing to overwrite existing evidence: {args.output}")
        raise SystemExit(2)
"""
EXCLUSIVE_OPEN = '''    with args.output.open("x", encoding="utf-8") as stream:'''
TRUNCATING_OPEN = '''    with args.output.open("w", encoding="utf-8") as stream:'''
ARG_DEFAULT = '''        "--output", type=Path, default=DEFAULT_OUTPUT,'''

MUTATIONS: list[tuple[str, str, list[tuple[str, str]]]] = [
    ("M0_unmutated", "no mutation; the regression test must pass", []),
    ("M1_drop_exists_check", "early existence check removed; only O_EXCL remains",
     [(EXISTS_GUARD, "")]),
    ("M2_drop_exclusive_creation", "O_EXCL removed; only the early check remains",
     [(EXCLUSIVE_OPEN, TRUNCATING_OPEN)]),
    ("M3_drop_both_guards", "both guards removed; existing evidence is clobbered",
     [(EXISTS_GUARD, ""), (EXCLUSIVE_OPEN, TRUNCATING_OPEN)]),
    ("M4_ignore_output_argument", "--output parsed but the report always goes to the default",
     [(EXISTS_GUARD, ""),
      (EXCLUSIVE_OPEN, '    with DEFAULT_OUTPUT.open("x", encoding="utf-8") as stream:')]),
]


def run_case(cid: str, description: str, edits: list[tuple[str, str]],
             workroot: Path) -> dict[str, Any]:
    work = workroot / cid
    (work / "docs/history/laps/probes").mkdir(parents=True)
    (work / "tests").mkdir(parents=True)
    (work / "tools").mkdir(parents=True)
    shutil.copy2(ROOT / "tools/runtime_env.py", work / "tools/runtime_env.py")
    shutil.copy2(TEST, work / "tests" / TEST.name)
    source = PROBE.read_text(encoding="utf-8")
    applied = []
    for old, new in edits:
        if old not in source:
            return {"id": cid, "description": description, "error": f"anchor missing: {old[:60]}"}
        source = source.replace(old, new, 1)
        applied.append(old.strip().splitlines()[0][:80])
    (work / "docs/history/laps/probes" / PROBE.name).write_text(source, encoding="utf-8")
    # The default report path must exist in the copy so the default-path branch
    # behaves like the repository does.
    (work / "docs/history/laps/probes"
     / "20260912_lap228_r6b_r3_review_report.json").write_text("{}\n", encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", str(work / "tests" / TEST.name)],
        capture_output=True, text=True, check=False, cwd=str(work))
    tail = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    return {
        "id": cid, "description": description, "mutations_applied": applied,
        "pytest_returncode": result.returncode,
        "pytest_tail": tail,
        "test_catches_mutation": result.returncode != 0,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        print(f"refusing to overwrite existing evidence: {args.output}")
        return 2

    with tempfile.TemporaryDirectory() as raw:
        workroot = Path(raw)
        cases = [run_case(cid, desc, edits, workroot) for cid, desc, edits in MUTATIONS]

    report = {
        "lap": 236,
        "role": "middle (Claude Code claude-opus-5/high)",
        "subject": "non-vacuity of tests/test_review_probe_output.py (lap235 R6-B-R7)",
        "cases": cases,
        "summary": {
            "unmutated_passes": next(c["pytest_returncode"] == 0 for c in cases
                                     if c["id"] == "M0_unmutated"),
            "caught": [c["id"] for c in cases
                       if c["id"] != "M0_unmutated" and c.get("test_catches_mutation")],
            "missed": [c["id"] for c in cases
                       if c["id"] != "M0_unmutated" and not c.get("test_catches_mutation")],
        },
    }
    try:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError:
        print(f"refusing to overwrite existing evidence: {args.output}")
        return 2
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"report -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
