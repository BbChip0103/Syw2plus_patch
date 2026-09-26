#!/usr/bin/env python3
"""Dense-50 MOVE+ATTACK convergence probe against a v2 variant missing one hook.

lap686 found the attack-broadcast regression collapses between V1_FULL
(18/49 ``ever_command4_count``) and V2_FULL (0/49) -- a delta across all
three control-group hooks (H1/H2/H3) at once. This wrapper runs the same
dense-fixture convergence probe (``tools/g5_worker_relative_move_attack_probe.py``)
against a candidate built with exactly one of those hooks skipped
(``patches/selection/g5_selection_cap50_v2_partial.py``), so whichever
variant recovers V1_FULL-level attack sustain names the missing hook as the
interference source.

Read-only with respect to the protected source tree: the candidate SHA is
computed fresh from the pinned original for the requested ``--skip-hook``
before the run, so no hardcoded SHA pin is required for a bundle this probe
has not seen before.
"""

from __future__ import annotations

import argparse
import json
import types
from pathlib import Path

from patches.selection import g5_selection_cap50_v2_partial as partial
from tools import g5_worker_relative_move_attack_probe as base
from tools import runtime_env

REPO = base.REPO
DEFAULT_SOURCE = base.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap687-v2-partial-convergence"


def _make_g5(skip: str) -> types.SimpleNamespace:
    module = types.SimpleNamespace()
    module.SELECTION_BASE = partial.SELECTION_BASE
    module.TARGET_CAPACITY = partial.TARGET_CAPACITY
    module.build_candidate = lambda original: partial.build_candidate(original, skip=skip)
    return module


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str, skip_hook: str) -> dict:
    if skip_hook not in partial.HOOKS:
        raise ValueError(f"skip_hook must be one of {partial.HOOKS}, got {skip_hook!r}")
    g5_module = _make_g5(skip_hook)
    original_g5, original_sha = base.g5, base.TARGET_SHA
    base.g5 = g5_module
    if variant == "candidate":
        source_exe = source.expanduser().resolve() / runtime_env.ORIGINAL_EXE
        _candidate_bytes, report = g5_module.build_candidate(source_exe.read_bytes())
        base.TARGET_SHA = report["candidate_sha256"]
    try:
        result = base.run_probe(source, runtime_root, artifact_root, variant=variant)
    finally:
        base.g5, base.TARGET_SHA = original_g5, original_sha
    result["skip_hook"] = skip_hook
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("original", "candidate"), default="candidate")
    parser.add_argument("--skip-hook", choices=partial.HOOKS, required=True)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(
        args.source, args.runtime_root, args.artifact_root,
        variant=args.variant, skip_hook=args.skip_hook,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "CONVERGENCE_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
