#!/usr/bin/env python3
"""Fresh mutation check for the name-independent R19 regression."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
SUT = ROOT / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
TESTS = ROOT / "tests/test_review_probe_output.py"
PY = str(ROOT / ".venv/bin/python")
REPORT = Path(__file__).with_name("20260912_lap261_r19_work_report.json")

EARLY_REFUSAL = (
    "        if path.exists():\n"
    "            return f\"refusing to overwrite existing evidence: {path}\"\n\n"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_mutation(root: Path, source: str) -> dict[str, object]:
    probe = root / "docs/history/laps/probes/20260912_lap228_r6b_r3_review_probe.py"
    probe.parent.mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "tools").symlink_to(ROOT / "tools", target_is_directory=True)
    probe.write_text(source, encoding="utf-8")
    shutil.copy2(TESTS, root / "tests/test_review_probe_output.py")
    proc = subprocess.run(
        [PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=no",
         str(root / "tests/test_review_probe_output.py")],
        cwd=root, capture_output=True, text=True, check=False,
    )
    failed = [line for line in proc.stdout.splitlines() if line.startswith("FAILED")]
    return {
        "exit": proc.returncode,
        "failed_tests": failed,
        "summary": proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else "",
    }


def main() -> int:
    original = SUT.read_text(encoding="utf-8")
    mutations = {
        "M0_control": original,
        "M1_rename_wait_and_drop_early_refusal": (
            original.replace(EARLY_REFUSAL, "", 1)
            .replace("def drive_wait(", "def renamed_wait(", 1)
        ),
    }
    results: dict[str, dict[str, object]] = {}
    with tempfile.TemporaryDirectory(prefix="lap261_r19_") as temp:
        for mutation_id, source in mutations.items():
            results[mutation_id] = run_mutation(Path(temp) / mutation_id, source)

    m0 = results["M0_control"]
    m1 = results["M1_rename_wait_and_drop_early_refusal"]
    verdict = "PASS" if (
        m0["exit"] == 0
        and m1["exit"] != 0
        and any("test_r6b_r17_existing_evidence_refusal_precedes_review_body" in line
                for line in m1["failed_tests"])
    ) else "FAIL"
    report = {
        "lap": 261,
        "role": "work",
        "target": "G1-R19 name-independent R17 regression",
        "game_executions": 0,
        "source_sha256": sha256(SUT),
        "tests_sha256": sha256(TESTS),
        "mutations": results,
        "verdict": verdict,
    }
    with REPORT.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"verdict": verdict, "mutations": results}, indent=2, sort_keys=True))
    print(f"report -> {REPORT}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
