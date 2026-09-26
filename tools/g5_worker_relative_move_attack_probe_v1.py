#!/usr/bin/env python3
"""Same self-calibrated MOVE+ATTACK convergence probe as
``g5_worker_relative_move_attack_probe.py``, run against **v1 alone**
(relocated selection, no control-group hooks, no chunked dispatch) at full
dense-fixture (49/50-unit) scale.

2026-09-26 lap686 bisection: the 18:19 operator plan's cheap ``<=20``-scale
discriminator (``tools/g5_bisect_attack_probe.py``) found that *every*
individual v1/v2 edit bundle -- including v1 as a whole (13/19
``ever_command4_count``) and v2 as a whole (12/19, ``max_pending_exact_count
19/19``) -- sustains attack about as well as the original (17/19) when
selection stays at or below the stock 20-unit capacity. That falsifies the
premise that a single bundle is broken "even at <=20" the way the operator's
plan expected, and means the regression is scale-dependent: it only appears
once selection actually exceeds 20 (lap684/685's ``ever_command4_count
<=1/49`` for v2/v3).

The one bundle-scale split not yet tested at *that* scale is v1 alone
(without v2's H1/H2/H3 control-group hooks). lap685 already showed v2 (with
hooks) fails at 49/50-selection scale identically to v3 (chunked). This probe
answers whether v1 *alone*, at the same 49/50-selection scale, also fails
(regression is inherent to v1's relocation/consumer-widen/hit-test/rotation
edits) or sustains normally (regression is specific to the H1/H2/H3 hooks,
i.e. bundle G4).

Read-only: touches no product EXE bytes beyond the already-approved G5
selection-cap50 v1 candidate build; the "original" variant runs the
protected source executable unmodified (verified by SHA both before and
after).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from patches.selection import g5_selection_cap50_v1 as g5_v1
from tools import g5_worker_relative_move_attack_probe as base

TARGET_SHA = "6c8f73ba5626a978abaa09bb56adc46ee5da39bdd16d05c71285ce10d8f20b25"
REPO = base.REPO
DEFAULT_SOURCE = base.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap686-v1-worker-relative-convergence"


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict:
    original_g5, original_sha = base.g5, base.TARGET_SHA
    base.g5, base.TARGET_SHA = g5_v1, TARGET_SHA
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
