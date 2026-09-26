#!/usr/bin/env python3
"""Prove the R6-B-R11 exclusive-create regression is non-vacuous."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PROBE = ROOT / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TEST = ROOT / "tests/test_review_probe_output.py"
PROBE_ANCHOR = '    with args.output.open("x", encoding="utf-8") as stream:'
PROBE_MUTATION = '    with args.output.open("w", encoding="utf-8") as stream:'
PROBE_DECLARATION = (
    "PROBE = ROOT / "
    '"docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"'
)


def _tail(output: str) -> list[str]:
    return output.strip().splitlines()[-4:]


def _failed_tests(output: str) -> list[str]:
    return [
        line.strip()
        for line in output.splitlines()
        if "FAILED " in line and "::" in line
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        print(f"refusing to overwrite existing evidence: {args.output}")
        return 2

    source = PROBE.read_text(encoding="utf-8")
    if source.count(PROBE_ANCHOR) != 1:
        raise SystemExit("exclusive-create mutation anchor is not unique")
    mutated_source = source.replace(PROBE_ANCHOR, PROBE_MUTATION, 1)

    test_source = TEST.read_text(encoding="utf-8")
    if test_source.count(PROBE_DECLARATION) != 1:
        raise SystemExit("test probe declaration anchor is not unique")

    with tempfile.TemporaryDirectory(prefix="lap245_r11_") as raw:
        work = Path(raw)
        mutated_probe = work / PROBE.name
        mutated_probe.write_text(mutated_source, encoding="utf-8")
        mutated_test = work / TEST.name
        mutated_test.write_text(
            test_source.replace(
                PROBE_DECLARATION,
                f"PROBE = Path({str(mutated_probe)!r})",
                1,
            ),
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(mutated_test)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

    report = {
        "lap": 245,
        "target": "G1 Stage B R6-B-R11",
        "game_executions": 0,
        "source_sha256": hashlib.sha256(PROBE.read_bytes()).hexdigest(),
        "mutation": {
            "description": "replace exclusive open mode x with truncating mode w",
            "mutated_source_sha256": hashlib.sha256(
                mutated_source.encode("utf-8")
            ).hexdigest(),
            "pytest_returncode": result.returncode,
            "caught": result.returncode != 0,
            "failed_tests": _failed_tests(result.stdout),
            "stdout_tail": _tail(result.stdout),
            "stderr_tail": _tail(result.stderr),
        },
        "verdict": "PASS" if result.returncode != 0 else "FAIL",
    }
    try:
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(report, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError:
        print(f"refusing to overwrite existing evidence: {args.output}")
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"report -> {args.output}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
