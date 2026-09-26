#!/usr/bin/env python3
"""lap347 middle: repair only lap346's unequal strict zip in a new artifact.

The failed lap346 probe remains immutable.  This adapter pins its exact bytes,
changes the single five-versus-four adjacency iterator to two four-item slices,
then executes the complete read-only review once from the beginning.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SOURCE = REPO / "docs/history/laps/probes/20260912_lap346_middle_lap345_candidate_r1_artifact_probe.py"
SOURCE_SHA256 = "43940820cbaed6bd3cbc2d068f47c97de9cb0b757df04e227d251a4dda21933c"
BROKEN = "for left, right in zip(stage_names, stage_names[1:], strict=True):"
REPAIRED = "for left, right in zip(stage_names[:-1], stage_names[1:], strict=True):"


def main() -> int:
    source_bytes = SOURCE.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    source = source_bytes.decode("utf-8")
    failures: list[str] = []
    if source_sha != SOURCE_SHA256:
        failures.append("lap346 failed probe changed; preserve it as immutable evidence")
    if source.count(BROKEN) != 1:
        failures.append("lap346 failed probe no longer has exactly one diagnosed 5-to-4 strict zip")
    if REPAIRED in source:
        failures.append("lap346 failed probe was already repaired in place")
    if failures:
        print(json.dumps({"source_sha256": source_sha, "failures": failures}, indent=2))
        return 1

    repaired_source = source.replace(BROKEN, REPAIRED, 1)
    namespace = {"__file__": str(Path(__file__).resolve()), "__name__": "__main__"}
    exec(compile(repaired_source, str(Path(__file__).resolve()), "exec"), namespace)
    return 0


if __name__ == "__main__":
    sys.exit(main())
