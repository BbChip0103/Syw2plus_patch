#!/usr/bin/env python3
"""lap343 middle — lap339 G에서 역사적 STATUS 포인터 단언만 분리한다.

기존 lap339 probe는 불변 이력이므로 수정하지 않는다. 그 probe를 그대로 실행해
현재 계약 실패는 모두 유지하되, PROMPT/AGENTS/DESIGN에 없는 두 live-STATUS
포인터 실패만 역사적 전이 단언으로 분류한다.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
SOURCE = REPO / "docs/history/laps/probes/20260912_lap339_middle_lap338_provenance_policy_probe.py"
SOURCE_SHA256 = "761aec2f1078eb298428b94cfed0231f4739900e0f2528143dbfa31272f8018b"
HISTORICAL_POINTER_FAILURES = {
    "STATUS.md names no compaction holding its previous text",
    "STATUS.md points at no compaction whose declared SHA/line count match its own body",
}


def main() -> int:
    failures: list[str] = []
    source_sha = hashlib.sha256(SOURCE.read_bytes()).hexdigest() if SOURCE.is_file() else None
    if source_sha != SOURCE_SHA256:
        failures.append("lap339 G source changed; historical probe must remain immutable")

    completed = subprocess.run(
        [sys.executable, str(SOURCE)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
    )
    source_report: dict[str, Any] = {}
    try:
        parsed = json.loads(completed.stdout)
        if isinstance(parsed, dict):
            source_report = parsed
        else:
            failures.append("lap339 G stdout is not a JSON object")
    except json.JSONDecodeError:
        failures.append("lap339 G stdout is not valid JSON")

    source_failures = set(source_report.get("failures", []))
    unexpected = sorted(source_failures - HISTORICAL_POINTER_FAILURES)
    if unexpected:
        failures.extend(f"lap339 G current-contract failure: {item}" for item in unexpected)
    expected_rc = 1 if source_failures else 0
    if completed.returncode != expected_rc:
        failures.append(
            f"lap339 G rc {completed.returncode} disagrees with its failures list"
        )

    report = {
        "lap": 343,
        "role": "middle",
        "source_probe": {
            "path": str(SOURCE.relative_to(REPO)),
            "sha256": source_sha,
            "returncode": completed.returncode,
        },
        "historical_pointer_failures_observed": sorted(
            source_failures & HISTORICAL_POINTER_FAILURES
        ),
        "unexpected_contract_failures": unexpected,
        "status": source_report.get("status"),
        "compaction": source_report.get("compaction"),
        "gates_referencing_history_probes": source_report.get(
            "gates_referencing_history_probes"
        ),
        "findings": source_report.get("findings"),
        "failures": sorted(failures),
    }
    print(json.dumps(report, ensure_ascii=False, indent=1, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
