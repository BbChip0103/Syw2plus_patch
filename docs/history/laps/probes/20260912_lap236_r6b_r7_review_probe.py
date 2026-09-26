#!/usr/bin/env python3
"""lap236 middle-tier independent review of G1-R6-B-R7 (probe evidence output guard).

Reviews the lap235 work-tier repair of
`docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py`:
an explicit `--output`, refusal of existing paths with exit 2, and exclusive
creation so a concurrent rerun cannot clobber recorded evidence.

The probe never writes inside the repository except to the `--output` path it is
given, and it only reads the preserved lap228/lap230 reports (hash comparison).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
TARGET = ROOT / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
DEFAULT_REPORT = ROOT / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_report.json"
LAP230_RERUN = ROOT / "docs/history/laps/probes/20260912_lap230_lap228probe_rerun_report.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_probe(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TARGET), *args],
        capture_output=True, text=True, check=False, cwd=str(cwd) if cwd else None,
    )


def case(cid: str, question: str, expected: str, observed: str, agrees: bool,
         detail: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "id": cid, "question": question, "expected": expected, "observed": observed,
        "verdict": "AGREES" if agrees else "DEFECT", "detail": detail or {},
    }


def preservation_cases(tmp: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    # A1 - ordinary existing file with content.
    a1 = tmp / "a1.json"
    body = b'{"historical": "evidence"}\n'
    a1.write_bytes(body)
    r = run_probe(["--output", str(a1)])
    out.append(case(
        "A1_existing_file", "existing report refused and preserved byte-for-byte",
        "exit 2, bytes unchanged",
        f"exit {r.returncode}, bytes {'unchanged' if a1.read_bytes() == body else 'CHANGED'}",
        r.returncode == 2 and a1.read_bytes() == body
        and "refusing to overwrite existing evidence" in r.stdout,
        {"stdout": r.stdout.strip()[:200]}))

    # A2 - existing zero-byte file (falsy content must still be protected).
    a2 = tmp / "a2.json"
    a2.touch()
    r = run_probe(["--output", str(a2)])
    out.append(case(
        "A2_existing_empty_file", "zero-byte existing file is still protected",
        "exit 2, size 0 preserved", f"exit {r.returncode}, size {a2.stat().st_size}",
        r.returncode == 2 and a2.stat().st_size == 0))

    # A3 - existing directory at the output path.
    a3 = tmp / "a3dir"
    a3.mkdir()
    (a3 / "keep.txt").write_text("keep\n", encoding="utf-8")
    r = run_probe(["--output", str(a3)])
    out.append(case(
        "A3_existing_directory", "a directory output path is refused, not clobbered",
        "exit 2, directory intact",
        f"exit {r.returncode}, dir {'intact' if (a3 / 'keep.txt').exists() else 'LOST'}",
        r.returncode == 2 and (a3 / "keep.txt").exists()))

    # A4 - symlink resolving to an existing sentinel must not be written through.
    target = tmp / "a4_target.json"
    sentinel = b"sentinel-through-symlink\n"
    target.write_bytes(sentinel)
    a4 = tmp / "a4_link.json"
    a4.symlink_to(target)
    r = run_probe(["--output", str(a4)])
    kept = target.read_bytes() == sentinel
    out.append(case(
        "A4_symlink_to_existing", "symlink to existing evidence is refused",
        "exit 2, target bytes unchanged",
        f"exit {r.returncode}, target {'unchanged' if kept else 'CHANGED'}",
        r.returncode == 2 and kept))

    # A5 - dangling symlink: exists() is False, so only O_EXCL can fail-close here.
    dangling_target = tmp / "a5_missing.json"
    a5 = tmp / "a5_link.json"
    a5.symlink_to(dangling_target)
    r = run_probe(["--output", str(a5)])
    out.append(case(
        "A5_dangling_symlink", "dangling symlink cannot be used to write through the guard",
        "exit 2, no file created at the symlink target",
        f"exit {r.returncode}, target exists={dangling_target.exists()}",
        r.returncode == 2 and not dangling_target.exists(),
        {"stdout": r.stdout.strip()[:200], "stderr_tail": r.stderr.strip()[-200:]}))

    # A6 - default path (no --output) while the preserved lap228 report exists.
    before = sha256(DEFAULT_REPORT)
    r = run_probe([])
    after = sha256(DEFAULT_REPORT)
    out.append(case(
        "A6_default_path_protected", "no-arg rerun refuses the preserved lap228 report",
        "exit 2, report sha256 unchanged",
        f"exit {r.returncode}, sha {'unchanged' if before == after else 'CHANGED'}",
        r.returncode == 2 and before == after,
        {"sha256_before": before, "sha256_after": after}))

    # A7 - import path (__name__ != "__main__") bypasses the early exists() check,
    #      so the exclusive-creation branch is the only remaining guard.
    before = sha256(DEFAULT_REPORT)
    imp = subprocess.run(
        [sys.executable, "-c",
         "import importlib.util,sys;"
         f"spec=importlib.util.spec_from_file_location('lap228probe', {str(TARGET)!r});"
         "m=importlib.util.module_from_spec(spec);"
         "sys.modules['lap228probe']=m;spec.loader.exec_module(m)"],
        capture_output=True, text=True, check=False)
    after = sha256(DEFAULT_REPORT)
    out.append(case(
        "A7_import_hits_exclusive_creation",
        "import (non-__main__) run still fail-closes on the existing default report",
        "nonzero exit, report sha256 unchanged",
        f"exit {imp.returncode}, sha {'unchanged' if before == after else 'CHANGED'}",
        imp.returncode != 0 and before == after,
        {"stdout": imp.stdout.strip()[-200:], "stderr_tail": imp.stderr.strip()[-200:]}))

    return out


def creation_cases(tmp: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    b1 = tmp / "b1_fresh.json"
    r = run_probe(["--output", str(b1)])
    ok = r.returncode == 0 and b1.exists()
    report: dict[str, Any] = json.loads(b1.read_text(encoding="utf-8")) if ok else {}
    out.append(case(
        "B1_fresh_path_written", "an explicit new path receives a full report",
        "exit 0, lap 228, surgicality AGREES",
        f"exit {r.returncode}, lap {report.get('lap')}, "
        f"surgicality {report.get('summary', {}).get('surgicality_verdict')}",
        ok and report.get("lap") == 228
        and report.get("summary", {}).get("surgicality_verdict") == "AGREES",
        {"stderr_tail": r.stderr.strip()[-200:]}))

    b2 = tmp / "b2_fresh.json"
    r2 = run_probe(["--output", str(b2)])
    same = b1.exists() and b2.exists() and b1.read_bytes() == b2.read_bytes()
    out.append(case(
        "B2_deterministic_rerun", "two fresh runs produce identical evidence",
        "exit 0 and byte-identical reports",
        f"exit {r2.returncode}, identical={same}", r2.returncode == 0 and same))

    # B3 - verdict-bearing content must still reproduce the preserved lap230 rerun.
    # `source_sha256` is expected to differ: runtime_env.py changed in lap231/lap233.
    lap230 = json.loads(LAP230_RERUN.read_text(encoding="utf-8"))
    def verdicts(doc: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in doc.items() if k != "source_sha256"}
    matches_lap230 = bool(report) and verdicts(report) == verdicts(lap230)
    out.append(case(
        "B3_matches_preserved_lap230_rerun",
        "the guarded probe still reproduces the preserved lap230 rerun verdicts",
        "all fields except source_sha256 identical to "
        "20260912_lap230_lap228probe_rerun_report.json",
        f"identical={matches_lap230}", matches_lap230,
        {"lap230_source_sha256": lap230.get("source_sha256"),
         "fresh_source_sha256": report.get("source_sha256"),
         "source_sha256_differs": lap230.get("source_sha256") != report.get("source_sha256")}))

    if report:
        summary = report.get("summary", {})
        clean = (summary.get("reachability_defects") == []
                 and summary.get("preservation_defects") == [])
        out.append(case(
            "B4_review_semantics_unchanged",
            "the output guard did not weaken the R6-B-R3 review verdicts",
            "reachability/preservation defect lists empty",
            f"reachability={summary.get('reachability_defects')}, "
            f"preservation={summary.get('preservation_defects')}, "
            f"wait={summary.get('wait_defects')}", clean,
            {"wait_defects": summary.get("wait_defects")}))
    return out


def diagnosability_cases(tmp: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []

    # C1 - missing parent directory: nothing is destroyed, but the failure only
    #      surfaces after the whole probe body has run.
    c1 = tmp / "missing_dir" / "report.json"
    r = run_probe(["--output", str(c1)])
    out.append(case(
        "C1_missing_parent_directory",
        "an unwritable output path fails without a classified message",
        "exit 2 with the refusal message, or a clear early error",
        f"exit {r.returncode}, stderr_has_traceback={'Traceback' in r.stderr}, "
        f"created={c1.exists()}",
        r.returncode == 2 and not c1.exists(),
        {"stderr_tail": r.stderr.strip()[-300:], "stdout_tail": r.stdout.strip()[-200:]}))

    # C2 - read-only parent directory.
    c2dir = tmp / "readonly"
    c2dir.mkdir()
    os.chmod(c2dir, 0o500)
    c2 = c2dir / "report.json"
    r = run_probe(["--output", str(c2)])
    out.append(case(
        "C2_readonly_parent_directory",
        "a permission failure is reported as a guard refusal, not a raw traceback",
        "exit 2 with the refusal message",
        f"exit {r.returncode}, stderr_has_traceback={'Traceback' in r.stderr}, "
        f"created={c2.exists()}",
        r.returncode == 2 and not c2.exists(),
        {"stderr_tail": r.stderr.strip()[-300:]}))
    os.chmod(c2dir, 0o700)

    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="JSON report path; an existing path is refused")
    args = parser.parse_args(argv)
    if args.output.exists():
        print(f"refusing to overwrite existing evidence: {args.output}")
        return 2

    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        preservation = preservation_cases(tmp)
        creation = creation_cases(tmp)
        diagnosability = diagnosability_cases(tmp)

    cases = preservation + creation + diagnosability
    report = {
        "lap": 236,
        "role": "middle (Claude Code claude-opus-5/high)",
        "subject": "G1-R6-B-R7 probe evidence output guard (lap235 work tier)",
        "target_probe_sha256": sha256(TARGET),
        "preserved_lap228_report_sha256": sha256(DEFAULT_REPORT),
        "preserved_lap230_rerun_sha256": sha256(LAP230_RERUN),
        "preservation_cases": preservation,
        "creation_cases": creation,
        "diagnosability_cases": diagnosability,
        "summary": {
            "total": len(cases),
            "agrees": sum(1 for c in cases if c["verdict"] == "AGREES"),
            "defects": [c["id"] for c in cases if c["verdict"] == "DEFECT"],
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
