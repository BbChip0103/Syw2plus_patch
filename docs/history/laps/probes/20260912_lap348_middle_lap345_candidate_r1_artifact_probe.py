#!/usr/bin/env python3
"""lap348 middle: apply the two approved lap346 review-probe repairs.

The failed lap346 probe and lap347 adapter remain immutable evidence.  This
adapter pins both files, repairs only the unequal adjacency zip and the
65-character harness SHA transcription, then runs the complete read-only
lap345 artifact review once from the beginning.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SOURCE = REPO / "docs/history/laps/probes/20260912_lap346_middle_lap345_candidate_r1_artifact_probe.py"
PRIOR_ADAPTER = REPO / "docs/history/laps/probes/20260912_lap347_middle_lap345_candidate_r1_artifact_probe.py"
SOURCE_SHA256 = "43940820cbaed6bd3cbc2d068f47c97de9cb0b757df04e227d251a4dda21933c"
PRIOR_ADAPTER_SHA256 = "22c5e2977f5b95e01d24a9065fb1551db654cedb3ee947cac430f587e8b4db55"
BROKEN_ZIP = "for left, right in zip(stage_names, stage_names[1:], strict=True):"
REPAIRED_ZIP = "for left, right in zip(stage_names[:-1], stage_names[1:], strict=True):"
BROKEN_HARNESS_SHA = "965e370989fdad63ec09da25a3f5b3f3a3c66e364d668ab1d48965e141ddb547b"
REPAIRED_HARNESS_SHA = "965e370989fdad63ec9da25a3f5b3f3a3c66e364d668ab1d48965e141ddb547b"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    prior_adapter_sha = sha256(PRIOR_ADAPTER)
    source = source_bytes.decode("utf-8")
    failures: list[str] = []

    if source_sha != SOURCE_SHA256:
        failures.append("lap346 failed probe changed; preserve it as immutable evidence")
    if prior_adapter_sha != PRIOR_ADAPTER_SHA256:
        failures.append("lap347 failed adapter changed; preserve it as immutable evidence")
    if source.count(BROKEN_ZIP) != 1 or REPAIRED_ZIP in source:
        failures.append("lap346 probe no longer has exactly one diagnosed 5-to-4 strict zip")
    if source.count(BROKEN_HARNESS_SHA) != 1 or REPAIRED_HARNESS_SHA in source:
        failures.append("lap346 probe no longer has exactly one diagnosed 65-character harness SHA")
    if len(BROKEN_HARNESS_SHA) != 65 or len(REPAIRED_HARNESS_SHA) != 64:
        failures.append("harness SHA repair is not the reviewed 65-to-64 character change")
    if sha256(REPO / "tools/runtime_env.py") != REPAIRED_HARNESS_SHA:
        failures.append("live harness does not match the reviewed 64-character SHA")

    if failures:
        print(
            json.dumps(
                {
                    "source_sha256": source_sha,
                    "prior_adapter_sha256": prior_adapter_sha,
                    "failures": failures,
                },
                indent=2,
            )
        )
        return 1

    repaired_source = source.replace(BROKEN_ZIP, REPAIRED_ZIP, 1)
    repaired_source = repaired_source.replace(BROKEN_HARNESS_SHA, REPAIRED_HARNESS_SHA, 1)
    namespace = {"__file__": str(Path(__file__).resolve()), "__name__": "__main__"}
    exec(compile(repaired_source, str(Path(__file__).resolve()), "exec"), namespace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
