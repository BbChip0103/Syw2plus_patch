#!/usr/bin/env python3
"""G4 free-for-all AI behavior baseline (2026-09-27 12:05 운영자 판정 다음 work ①②).

Runs the original executable's fixed-seed two-player AI-vs-AI custom game
chain (``runtime_env.G4_FIXED_CHAIN_GOALS``, e.g. ``_custom_game_chain_inject_seed1``)
through the existing ``tools/runtime_env.py g1-baseline`` harness and derives
behavior metrics from the already-recorded ``g4_ai_smoke.samples`` (players +
units snapshots, no new instrumentation): resource income, a lifetime
production-count proxy, army/idle-worker unit counts, and first-attack time.

Read-only for ``--variant original`` (default): no candidate AI, no EXE byte
edits, no memory writes beyond the existing approved fixed-seed chain's own
control-bridge fixture setup (``synthetic=True``, disclosed by ``g1-baseline``
itself). ``--variant candidate`` (lap713, STATUS 2026-09-27 13:05 판정) writes
a *named* candidate exe (``g4_production_crowd_cap_14.exe``,
``runtime_env.G4_CANDIDATE_EXES``) alongside the untouched private original
copy via ``patches.ai.g4_production_crowd_cap_v1.create_copy`` and launches
it through ``runtime_env.py g1-baseline --g4-candidate-exe`` -- the same
approved mechanism the existing G4 controller-cadence/gather-cooldown
candidates use. The protected read-only source directory is never touched
(verified below and by ``source_unchanged`` in the result).

Worker/HQ type identification is fixture-derived, not hardcoded per nation:
the fixed-seed chain starts each owner with exactly one HQ (highest HP) and
one worker (lowest HP) unit (see ``analysis/memory_maps/g2_supply10000_...``
and ``docs/history/laps/20260916_g4_ai_evidence_inventory.md`` for the
underlying two-starting-unit fixture fact). "army_unit_count" therefore
excludes the *initial* HQ/worker types only; buildings constructed later
with a different type still count toward it -- this is a disclosed
approximation, not a verified building/military classifier.
"""

from __future__ import annotations

import argparse
import json
import shutil
import statistics
import subprocess
import sys
import time
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import runtime_env  # noqa: E402

ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g4-ai-behavior-baseline"
DEFAULT_CHAIN_GOAL = "_custom_game_chain_inject_seed1"
OWNERS = (0, 1)


class ProbeError(RuntimeError):
    pass


def _mean(values: Sequence[float]) -> float | None:
    return statistics.fmean(values) if values else None


def _worker_and_hq_types(initial_units: Sequence[Mapping[str, Any]], owner: int) -> tuple[Any, Any]:
    """Identify (worker_type, hq_type) from the owner's units in the *first*
    sample only. The fixed-seed chain's own gate requires exactly a live
    HQ+worker per owner at start (see ``_g2_initial_creation_gate`` for the
    same two-starting-unit invariant on the sibling 8-owner fixture); the
    worker is the lower-HP of the pair, the HQ the higher-HP one."""
    owned = [u for u in initial_units if u.get("owner") == owner and isinstance(u.get("hp"), int)]
    if len(owned) < 2:
        return None, None
    ordered = sorted(owned, key=lambda u: u["hp"])
    return ordered[0].get("type"), ordered[-1].get("type")


def compute_behavior_metrics(
    samples: Sequence[Mapping[str, Any]], owners: Sequence[int] = OWNERS,
) -> dict[str, Any]:
    if not samples:
        raise ValueError("no samples")
    first_units = [u for u in samples[0].get("units", []) if isinstance(u, Mapping)]
    per_owner: dict[str, Any] = {}
    for owner in owners:
        worker_type, hq_type = _worker_and_hq_types(first_units, owner)
        initial_ids = {
            u.get("internal_id") for u in first_units
            if u.get("owner") == owner and u.get("internal_id") is not None
        }
        seen_ids: set[Any] = set(initial_ids)
        idle_worker_series: list[int] = []
        army_series: list[int] = []
        resource_series: list[dict[str, Any]] = []
        first_attack_elapsed: float | None = None
        for sample in samples:
            units = [u for u in sample.get("units", []) if isinstance(u, Mapping)]
            owned = [u for u in units if u.get("owner") == owner]
            for unit in owned:
                internal_id = unit.get("internal_id")
                if internal_id is not None:
                    seen_ids.add(internal_id)
            idle_worker_series.append(
                sum(1 for u in owned if u.get("type") == worker_type and u.get("command") == 1)
            )
            army_series.append(
                sum(1 for u in owned if u.get("type") not in (worker_type, hq_type))
            )
            if first_attack_elapsed is None and any(u.get("command") == 4 for u in owned):
                elapsed = sample.get("elapsed_seconds")
                if isinstance(elapsed, (int, float)):
                    first_attack_elapsed = float(elapsed)
            players = [p for p in sample.get("players", []) if isinstance(p, Mapping)]
            player = next((p for p in players if p.get("owner") == owner), None)
            if player is not None:
                rice, wood = player.get("rice"), player.get("wood")
                elapsed = sample.get("elapsed_seconds")
                if isinstance(rice, int) and isinstance(wood, int) and isinstance(elapsed, (int, float)):
                    resource_series.append({"elapsed_seconds": float(elapsed), "stock": rice + wood})
        income_per_min = None
        if len(resource_series) >= 2:
            duration_seconds = resource_series[-1]["elapsed_seconds"] - resource_series[0]["elapsed_seconds"]
            if duration_seconds > 0:
                income_per_min = (
                    (resource_series[-1]["stock"] - resource_series[0]["stock"]) / (duration_seconds / 60.0)
                )
        per_owner[str(owner)] = {
            "worker_type": worker_type,
            "hq_type": hq_type,
            "initial_unit_count": len(initial_ids),
            "production_count_proxy": max(0, len(seen_ids) - len(initial_ids)),
            "idle_worker_count_mean": _mean([float(v) for v in idle_worker_series]),
            "idle_worker_count_max": max(idle_worker_series) if idle_worker_series else None,
            "army_unit_count_first": army_series[0] if army_series else None,
            "army_unit_count_last": army_series[-1] if army_series else None,
            "army_unit_count_mean": _mean([float(v) for v in army_series]),
            "resource_stock_first": resource_series[0]["stock"] if resource_series else None,
            "resource_stock_last": resource_series[-1]["stock"] if resource_series else None,
            "resource_income_per_min": income_per_min,
            "first_attack_elapsed_seconds": first_attack_elapsed,
        }
    return {"sample_count": len(samples), "owners": per_owner}


def _run(argv: list[str], *, timeout: float, cwd: Path = REPO) -> dict[str, Any]:
    proc = subprocess.run(
        argv, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False,
    )
    if proc.returncode != 0:
        raise ProbeError(f"{argv[:2]} exit={proc.returncode} stderr={proc.stderr[-4000:]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError(f"non-JSON stdout from {argv[:2]}: {exc}; stdout={proc.stdout[-2000:]}") from exc


def run_one(
    *, source: Path, runtime_root: Path, artifact_root: Path, chain_goal: str,
    sample_seconds: float, sample_period: float, timeout: float,
    variant: str = "original",
) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unknown variant: {variant}")
    source, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe.read_bytes()).hexdigest() != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_exe_name = "g4_production_crowd_cap_14.exe"
    if variant == "candidate" and candidate_exe_name not in runtime_env.G4_CANDIDATE_EXES:
        raise ProbeError(f"{candidate_exe_name} is not an approved G4_CANDIDATE_EXES entry")

    run_tag = f"run_{time.strftime('%Y%m%d_%H%M%S')}_{time.time_ns() % 1_000_000}"
    run_root = runtime_root / run_tag
    run_root.mkdir(parents=True)
    # build_runtime_bridge.py refuses an --out-dir inside the repository, so the
    # bridge build (unlike the rest of this run's private state) lives under the
    # caller-provided artifact_root instead of run_root.
    bridge_dir = artifact_root / f"{run_tag}_stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True,
    )
    bridge = bridge_dir / "_inmm.dll"

    prepare_result = _run(
        [sys.executable, str(REPO / "tools/runtime_env.py"), "prepare",
         "--source", str(source), "--bridge", str(bridge),
         "--runtime-root", str(run_root / "runtime"), "--timeout", "60"],
        timeout=90,
    )
    manifest_output = prepare_result.get("output")
    manifest_game = prepare_result.get("game")
    if not isinstance(manifest_output, Mapping) or not isinstance(manifest_game, Mapping):
        raise ProbeError(f"malformed prepare() manifest: {prepare_result}")
    run_dir = Path(str(manifest_output.get("run_dir")))
    manifest_path = run_dir / "manifest.json"
    game_root = Path(str(manifest_game.get("root")))
    private_exe = game_root / runtime_env.ORIGINAL_EXE
    if sha256(private_exe.read_bytes()).hexdigest() != ORIGINAL_SHA:
        raise ProbeError("private original copy failed pre-install check")

    candidate_sha: str | None = None
    if variant == "candidate":
        from patches.ai.g4_production_crowd_cap_v1 import create_copy as g4_create_copy
        candidate_sha = g4_create_copy(private_exe, game_root / candidate_exe_name)

    # g1-baseline's CLI exit code is not the G4 verdict (docs/work/active/
    # G4_REENTRY_ORIGINAL_AI_BASELINE_LAP612.md §2.4): it always writes
    # output/g1_baseline.json in a `finally` block *before* re-raising a
    # RuntimeSafetyError from an unrelated post-sampling G1 input-tail check
    # (e.g. a fixed minimap click that this fixed-seed chain scene does not
    # support). Read that file directly instead of trusting the exit code or
    # relying on stdout, which is empty on that error path.
    baseline_argv = [
        sys.executable, str(REPO / "tools/runtime_env.py"), "g1-baseline",
        "--manifest", str(manifest_path), "--screen", "1600x1200x24",
        "--timeout", "90", "--g4-chain-goal", chain_goal,
        "--g4-sample-seconds", str(sample_seconds), "--g4-sample-period", str(sample_period),
    ]
    if variant == "candidate":
        baseline_argv += ["--g4-candidate-exe", candidate_exe_name]
    baseline_proc = subprocess.run(
        baseline_argv, cwd=REPO, capture_output=True, text=True, timeout=timeout, check=False,
    )
    evidence_path = run_dir / "output" / "g1_baseline.json"
    if not evidence_path.exists():
        raise ProbeError(
            f"g1-baseline produced no evidence file (exit={baseline_proc.returncode}); "
            f"stderr={baseline_proc.stderr[-4000:]}"
        )
    baseline = json.loads(evidence_path.read_text(encoding="utf-8"))
    tail_error = baseline.get("error") if baseline_proc.returncode != 0 else None
    smoke = baseline.get("g4_ai_smoke")
    if not isinstance(smoke, Mapping):
        raise ProbeError(f"g1-baseline evidence missing g4_ai_smoke: keys={list(baseline)}")
    samples = smoke.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ProbeError(f"g4_ai_smoke has no samples: {smoke.get('error')}")
    metrics = compute_behavior_metrics(samples)
    source_sha_after = sha256(source_exe.read_bytes()).hexdigest()

    if game_root.exists():
        shutil.rmtree(game_root, ignore_errors=True)

    return {
        "chain_goal": chain_goal,
        "sample_seconds": sample_seconds,
        "sample_period": sample_period,
        "run_root": str(run_root),
        "prepare": {"output_run_dir": str(run_dir)},
        "variant": variant,
        "candidate_sha256": candidate_sha,
        "source_sha_before": ORIGINAL_SHA,
        "source_sha_after": source_sha_after,
        "source_unchanged": source_sha_after == ORIGINAL_SHA,
        "g1_baseline_cli_exit": baseline_proc.returncode,
        "post_sampling_tail_error": tail_error,
        "cleanup_ok": bool(baseline.get("cleanup", {}).get("ok")),
        "smoke_error": smoke.get("error"),
        "metrics": metrics,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True,
                         help="outside the repo; holds the per-run bridge build (see "
                              "patches/population/build_runtime_bridge.py's --out-dir check)")
    parser.add_argument("--chain-goal", default=DEFAULT_CHAIN_GOAL,
                         choices=sorted(runtime_env.G4_FIXED_CHAIN_GOALS))
    parser.add_argument("--sample-seconds", type=float, default=280.0)
    parser.add_argument("--sample-period", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--variant", choices=("original", "candidate"), default="original")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    runs: list[dict[str, Any]] = []
    for index in range(args.repeats):
        run_result = run_one(
            source=args.source, runtime_root=args.runtime_root, artifact_root=args.artifact_root,
            chain_goal=args.chain_goal, sample_seconds=args.sample_seconds,
            sample_period=args.sample_period, timeout=args.timeout, variant=args.variant,
        )
        run_result["index"] = index
        runs.append(run_result)

    output = {"schema": "syw2plus.g4-ai-behavior-baseline.v1", "runs": runs}
    args.out.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
