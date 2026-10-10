#!/usr/bin/env python3
"""Independent replication of the G2 live lane with other conditions (map seed 99, long window, light acceleration).

Wraps ``tools.g2_esl2610_spike_probe.live_probe`` unchanged; only the control goal sent by the probe is rewritten from
``..._eight_ai_seed42`` to ``..._eight_ai_seed99`` (accepted literal of the control executor).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools import g2_esl2610_spike_probe as spike
from tools import runtime_env

SEED_GOAL_OLD = "_custom_game_chain_inject_g2_eight_ai_seed42"
SEED_GOAL_NEW = "_custom_game_chain_inject_g2_eight_ai_seed99"


def remap_goal(goal: str) -> str:
    return SEED_GOAL_NEW if goal == SEED_GOAL_OLD else goal


def _use_frozen(args: argparse.Namespace) -> None:
    """Freeze (or load) the layer 1-3 spike EXE so a concurrent edit of the g2_* modules cannot change the run."""
    from patches.esl2610 import g2_persist_2610

    g2_persist_2610.apply = lambda image, *_a, **_k: (image, {"skipped": "layers 1-3 only"})  # type: ignore[assignment]
    if args.freeze:
        args.freeze.mkdir(parents=True, exist_ok=True)
        exe, report = spike.build_candidate("cand_full")
        (args.freeze / "spike_l123.exe").write_bytes(exe)
        (args.freeze / "report.json").write_text(json.dumps(report))
        print(json.dumps({"sha256": spike._sha256(exe)}))
        return
    exe = (args.frozen / "spike_l123.exe").read_bytes()
    report = json.loads((args.frozen / "report.json").read_text())
    spike.build_candidate = lambda variant="candidate": (exe, report)  # type: ignore[assignment]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=["base", *spike.CANDIDATE_VARIANTS], required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--tick-seconds", type=float, default=420.0)
    parser.add_argument("--accelerate", type=int, default=50)
    parser.add_argument("--g9", action="store_true")
    parser.add_argument("--skip-persist", action="store_true")
    parser.add_argument("--freeze", type=Path, help="build the layer 1-3 candidate into this dir and exit")
    parser.add_argument("--frozen", type=Path, help="use the EXE+report frozen in this dir instead of building")
    args = parser.parse_args(argv)
    if args.freeze or args.frozen:
        _use_frozen(args)
        if args.freeze:
            return 0
    original = runtime_env._g4_send_control_goal
    sent: list[str] = []

    def send(prefix: Path, goal: str, timeout: float) -> dict[str, Any]:
        sent.append(remap_goal(goal))
        return original(prefix, sent[-1], timeout)

    if args.skip_persist and not args.frozen:  # layer 4 (save-format persistence) is not part of the live lane; its callsite check fails on 2611
        from patches.esl2610 import g2_persist_2610

        g2_persist_2610.apply = lambda image, *_a, **_k: (image, {"skipped": "replication runs layers 1-3 only"})  # type: ignore[assignment]

    runtime_env._g4_send_control_goal = send  # type: ignore[assignment]
    out = spike.live_probe(args.runtime_root, args.artifact_root, variant=args.variant,
                           tick_seconds=args.tick_seconds, accelerate=args.accelerate, g9=args.g9)
    out["replication"] = {"sent_goals": sent, "skip_persist": args.skip_persist}
    (args.artifact_root / "replication.json").write_text(json.dumps(out["replication"]))
    print(json.dumps({k: out.get(k) for k in ("status", "variant", "peak_live", "chain_inject")}, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
