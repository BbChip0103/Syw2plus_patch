#!/usr/bin/env python3
"""Fresh offline review of lap340's bounded R-a/R-b repair."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools import runtime_env  # noqa: E402


SNAPSHOT = ROOT / "docs/history/laps/snapshots/lap340_pre_edit"
EXPECTED_CURRENT = {
    "tools/runtime_env.py": "965e370989fdad63ec9da25a3f5b3f3a3c66e364d668ab1d48965e141ddb547b",
    "tests/test_lap326_r1_load_origin.py": (
        "891b60ebb87cb44de38ae64a69d952378b976b82bb99f90498f628a7e15b4265"
    ),
}
EXPECTED_SNAPSHOT = {
    "tools/runtime_env.py": (
        "922a267c27f51fe47d7db69962dadbfdbbded9ff04c6350e8cb7a4c44f8a2575",
        248099,
    ),
    "tests/test_lap326_r1_load_origin.py": (
        "c04a6265229f7e37cb9d4434f0e150c76e1e56d26f0e1c990cb938a06d769823",
        9367,
    ),
}
ARTIFACT_LITERAL = re.compile(r"\.?[A-Za-z0-9_-]+\.(?:json|lock|log)").fullmatch


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stage_started(function: object, stage: str) -> str:
    tree = ast.parse(inspect.cleandoc(inspect.getsource(function)))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        keywords = {item.arg: item.value for item in node.keywords if item.arg}
        stage_value = keywords.get("stage")
        if isinstance(stage_value, ast.Constant) and stage_value.value == stage:
            value = keywords.get("stage_started")
            if value is None:
                raise AssertionError(f"missing stage_started for {stage}")
            return ast.unparse(value)
    raise AssertionError(f"missing stage {stage}")


def artifact_names(function: object) -> set[str]:
    tree = ast.parse(inspect.cleandoc(inspect.getsource(function)))
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and ARTIFACT_LITERAL(node.value)
        and ("r1_load_origin" in node.value or "r1-load-origin" in node.value)
    }


def main() -> int:
    failures: list[str] = []
    manifest = json.loads((SNAPSHOT / "manifest.json").read_text())
    required = {
        "lap": 340,
        "role": "work",
        "reviewing_document": "docs/work/active/G1_R1_MIDDLE_PROVENANCE_ENVELOPE_LAP339.md",
        "scope": "R-a/R-b repair only",
        "historical_identity": "UNKNOWN",
        "covers_execution": False,
    }
    for key, expected in required.items():
        if manifest.get(key) != expected:
            failures.append(f"manifest {key} differs")
    if not manifest.get("collected_at"):
        failures.append("manifest collected_at missing")

    manifest_files = {
        item["relative_path"]: (item["sha256"], item["bytes"])
        for item in manifest.get("files", [])
    }
    if manifest_files != EXPECTED_SNAPSHOT:
        failures.append("manifest file inventory differs")

    for relative_path, (expected_sha, expected_bytes) in EXPECTED_SNAPSHOT.items():
        data = (SNAPSHOT / relative_path).read_bytes()
        if (sha256(data), len(data)) != (expected_sha, expected_bytes):
            failures.append(f"snapshot bytes differ: {relative_path}")
    for relative_path, expected_sha in EXPECTED_CURRENT.items():
        if sha256((ROOT / relative_path).read_bytes()) != expected_sha:
            failures.append(f"current source SHA differs: {relative_path}")

    before_runtime = (SNAPSHOT / "tools/runtime_env.py").read_text()
    after_runtime = (ROOT / "tools/runtime_env.py").read_text()
    old = "stage_budget=G1_R1_PS9_STAGE_BUDGET, stage_started=launch_started,"
    new = "stage_budget=G1_R1_PS9_STAGE_BUDGET, stage_started=started,"
    if before_runtime.count(old) != 1 or before_runtime.count(new) != 1:
        failures.append("snapshot R-b old/new sites are not one candidate plus one origin")
    if after_runtime != before_runtime.replace(old, new, 1):
        failures.append("runtime_env diff exceeds the authorized candidate R-b argument")

    origin_names = artifact_names(runtime_env.g1_r1_load_origin)
    candidate_names = artifact_names(runtime_env.g1_r1_candidate_load_origin)
    if origin_names != {
        "r1_load_origin.json",
        ".r1-load-origin.lock",
        "r1_load_origin.log",
    }:
        failures.append("origin artifact names differ")
    if candidate_names != {
        "r1_load_origin_candidate.json",
        ".r1-load-origin-candidate.lock",
        "r1_load_origin_candidate.log",
    }:
        failures.append("candidate artifact names differ")
    if origin_names & candidate_names:
        failures.append("artifact lanes overlap")
    if stage_started(runtime_env.g1_r1_load_origin, "r1_ps9") != "started":
        failures.append("origin PS9 budget excludes preparation")
    if stage_started(runtime_env.g1_r1_candidate_load_origin, "candidate_ps9") != "started":
        failures.append("candidate PS9 budget excludes preparation")

    candidate_artifacts = sorted(
        str(path.relative_to(ROOT))
        for base in (ROOT / "local", ROOT / "logs")
        if base.exists()
        for pattern in (
            "r1_load_origin_candidate.json",
            ".r1-load-origin-candidate.lock",
            "r1_load_origin_candidate.log",
        )
        for path in base.rglob(pattern)
    )
    if candidate_artifacts:
        failures.append("candidate artifact exists despite zero-run boundary")

    report: dict[str, Any] = {
        "lap": 342,
        "reviewed_lap": 340,
        "imported_runtime_env": str(Path(runtime_env.__file__).resolve().relative_to(ROOT)),
        "snapshot": manifest_files,
        "current_sha": EXPECTED_CURRENT,
        "origin_names": sorted(origin_names),
        "candidate_names": sorted(candidate_names),
        "origin_ps9_stage_started": stage_started(runtime_env.g1_r1_load_origin, "r1_ps9"),
        "candidate_ps9_stage_started": stage_started(
            runtime_env.g1_r1_candidate_load_origin, "candidate_ps9"
        ),
        "candidate_artifacts": candidate_artifacts,
        "failures": failures,
    }
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
