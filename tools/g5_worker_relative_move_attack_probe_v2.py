#!/usr/bin/env python3
"""Same self-calibrated MOVE+ATTACK convergence probe as
``g5_worker_relative_move_attack_probe.py``, run against the **v2** (relocated
selection, no chunked dispatch) candidate instead of v3.

2026-09-26 17:55 operator direction: lap685 found the v3 chunked builder and
its real per-unit writer dispatch loop treat MOVE and ATTACK identically
(byte/count-identical across all 3 chunks), which rules out the *chunking*
mechanism itself as the source of the reproducible original-100%/candidate
~0% ``ever_command4_count`` gap (lap684). Before chasing a downstream
revalidation function, run the cheap discriminating experiment: does the
same gap already exist in v2, which only relocates the 20-capacity
selection array to 50 capacity and has no chunking at all? If v2 also shows
``ever_command4_count`` near 0, the cause is unrelated to chunking --
something about the v1/v2 selection-array relocation itself (e.g. attack
validation/target-keep code that still reads the stock array base
``0x899024``/``0x899028``/``0x899078``) breaks ATTACK sustain even for a
plain, unchunked selection. If v2's ATTACK sustains normally (~matching its
own selection count), the cause is chunking-specific and lap685's plan (A)
(trace ``FUN_0040C640``'s revert point) is the right next step.

Read-only: touches no product EXE bytes beyond the already-approved G5
selection-cap50 v2 candidate build.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from patches.selection import g5_selection_cap50_v2 as g5_v2
from tools import g5_worker_relative_move_attack_probe as base

TARGET_SHA = "ae495fa5a1498597c265ad9bcae6444f564ade92adb311a3c413c4fb9996b5b7"
REPO = base.REPO
DEFAULT_SOURCE = base.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap685-v2-worker-relative-convergence"


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict:
    original_g5, original_sha = base.g5, base.TARGET_SHA
    base.g5, base.TARGET_SHA = g5_v2, TARGET_SHA
    try:
        return base.run_probe(source, runtime_root, artifact_root, variant=variant)
    finally:
        base.g5, base.TARGET_SHA = original_g5, original_sha


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("original", "candidate"), default="candidate")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root, variant=args.variant)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "CONVERGENCE_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
