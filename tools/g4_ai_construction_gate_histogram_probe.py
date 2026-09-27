#!/usr/bin/env python3
"""G4 free-for-all AI *construction* (building) gate rejection histogram
(STATUS 2026-09-27 14:45 운영자 방향, lap714 후속 v2 step ①): "AI 건설
결정 루틴... 정적으로 특정하고 같은 방식으로 건설 거부 사유 히스토그램을
owner별 raw 수집".

Read-only for the protected original EXE, same `process_vm_readv`-based
primitive every other probe in this repo uses
(`patches.population.runtime_driver.read`). No breakpoint/detour.

This is the *construction* counterpart of
`tools/g4_ai_gate_histogram_probe.py` (which covers *unit production*).
The two decision routines are separate original functions with separate
gates; lap714 found unit production 100% blocked by `H_AVAIL`/`PREREQ_OWN`,
which only explains why the AI can't produce certain *units* -- it does
not explain why the AI never builds the *buildings* those units need.
This probe answers that: it reimplements, from this lap's fresh
disassembly of `FUN_0043DBB0`/`FUN_0043DB00` (building on
`analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md`),
the gate order the original AI applies to every candidate building type
before it will ever add that type to its weighted construction pick:

  1. FACTION_BLOCK -- `FUN_0043DBB0` detects the owner's faction purely
     from live roster unit kinds (7=Joseon, 21/70=Ming, 75=Japan) via a
     5-way jump table (`0x0043E084`, selector byte `0x0043E098`); any
     other kind (including a *new* worker kind a scenario/mod might add)
     hits the jump table's default (no-op) case and never sets any of the
     four `+0x314C/+0x3150/+0x3154/+0x3158` flags. A building's
     `nation_kind` (from `tools/g4_ai_construction_table.py`) is rejected
     outright if the owner's matching flag is false -- checked here via a
     **live read of those four flags**, not a reimplementation of the
     roster scan (the conditional Ming/kind70 case calls a separate
     placement-check function this probe does not reproduce).
  2. SCENARIO_UNAVAIL -- `TYPE_SPEC_BASE + building_type*STRIDE + 0x4C`
     bit `0x2` (the same table `g4_ai_gate_histogram_probe.py` uses for
     units, offset `+0x4C` instead of `+0x24/+0x32/+0x34`).
  3. BUILD_COUNT_CAP -- `FUN_0043DB00`'s first check: only when
     `ai_flag(+0x2)==1` and `OVERRIDE_SWITCH==0`, reject if
     `total_buildings(+0x200E) >= floor(+0x2010/5)`.
  4. PREREQ_BUILDING -- `FUN_0043DB00` + `FUN_00422EB0`: reject if
     `prereq_building_type != 0` and player `+0x2FB8[prereq_building_type]
     == 0` (owner does not yet own that building type).
  5. PREREQ_OWN -- reject if `prereq_own_kind != 0` and player
     `+0x315C[prereq_own_kind] == 0`.
  6. TYPE_CAP -- per-building-kind cap `floor(typemax*N/6) + (typemax if
     that quotient % 12 != 0 else 0)`, where `N` is the owner's live count
     of completed buildings + buildings under construction (roster scan,
     `+0x1D8` bit `0x2` = completed, `+0x290 == 0xC` = under construction
     using the target kind at `+0x324`). Reject if the building_type's own
     live count >= this cap.
  7. else WOULD_BUILD -- the type enters `FUN_0043DBB0`'s weighted random
     pick (not modeled here: an LCG-driven scoring step, plus a 2/3-odds
     temporary disable of building kinds 41/56/68 -- neither changes
     whether a *structurally blocked* type ever becomes buildable, only
     which *already-eligible* type wins the tick's pick).
"""

from __future__ import annotations

import argparse
import json
import struct
import subprocess
import sys
import threading
import time
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from patches.population.runtime_driver import read as read_memory  # noqa: E402
from tools import g4_ai_construction_table as build_table  # noqa: E402
from tools import runtime_env  # noqa: E402

ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g4-ai-construction-gate-histogram"
DEFAULT_CHAIN_GOAL = "_custom_game_chain_inject_seed1"
OWNERS = (0, 1)

PLAYER_BASE = 0x00956770
PLAYER_STRIDE = 0x3ABC
PLAYER_AI_OFF = 0x002
PLAYER_TOTAL_BUILDINGS_OFF = 0x200E
PLAYER_BUILD_CAP_DENOM_OFF = 0x2010
PLAYER_PREREQ_BUILDING_TABLE_OFF = 0x2FB8   # 0x9598A8 - PLAYER_BASE (built >=1 of building type)
PLAYER_PREREQ_OWN_TABLE_OFF = 0x315C        # same table/offset g4_ai_gate_histogram_probe.py uses
PLAYER_FACTION_FLAG_OFF = {7: 0x314C, 21: 0x3154, 70: 0x3158, 75: 0x3150}

TYPE_SPEC_BASE = 0x009B5228
TYPE_SPEC_STRIDE = 0x394
TYPE_SPEC_BUILD_AVAIL_OFF = 0x4C
TYPE_SPEC_TYPEMAX_OFF = 0x34
BUILD_AVAIL_BIT = 0x2

OVERRIDE_SWITCH = 0x009E1DD8

# patches/population/runtime_driver.py STOCK_POOL: (capacity, unit_base, exists_base)
UNIT_POOL_CAPACITY, UNIT_POOL_BASE, UNIT_EXISTS_BASE = 1200, 0x0066B790, 0x008990C8
UNIT_STRIDE = 0x758
UNIT_TYPE_OFF = 0x8D
UNIT_OWNER_OFF = 0x8E
UNIT_STATE_OFF = 0x1F4
UNIT_COMPLETE_FLAG_OFF = 0x1D8   # bit 0x2 == finished construction
UNIT_ORDER_STATE_OFF = 0x290     # == 0xC while under construction
UNIT_UNDER_CONSTRUCTION_TARGET_KIND_OFF = 0x324

REASONS = (
    "FACTION_BLOCK", "SCENARIO_UNAVAIL", "BUILD_COUNT_CAP",
    "PREREQ_BUILDING", "PREREQ_OWN", "TYPE_CAP", "WOULD_BUILD",
)


class ProbeError(RuntimeError):
    pass


def u8(pid: int, address: int) -> int:
    return read_memory(pid, address, 1)[0]


def i16(pid: int, address: int) -> int:
    return struct.unpack("<h", read_memory(pid, address, 2))[0]


def u16(pid: int, address: int) -> int:
    return struct.unpack("<H", read_memory(pid, address, 2))[0]


def i32(pid: int, address: int) -> int:
    return struct.unpack("<i", read_memory(pid, address, 4))[0]


def read_owner_faction_flags(pid: int, owner: int) -> dict[int, bool]:
    player = PLAYER_BASE + owner * PLAYER_STRIDE
    return {kind: bool(i32(pid, player + off)) for kind, off in PLAYER_FACTION_FLAG_OFF.items()}


def read_owner_static(pid: int, owner: int) -> dict[str, int]:
    player = PLAYER_BASE + owner * PLAYER_STRIDE
    return {
        "ai_flag": u8(pid, player + PLAYER_AI_OFF),
        "total_buildings": u16(pid, player + PLAYER_TOTAL_BUILDINGS_OFF),
        "build_cap_denom": u16(pid, player + PLAYER_BUILD_CAP_DENOM_OFF),
    }


def read_type_spec_build(pid: int, building_type: int) -> dict[str, int]:
    base = TYPE_SPEC_BASE + building_type * TYPE_SPEC_STRIDE
    return {
        "avail": bool(u8(pid, base + TYPE_SPEC_BUILD_AVAIL_OFF) & BUILD_AVAIL_BIT),
        "typemax": i16(pid, base + TYPE_SPEC_TYPEMAX_OFF),
    }


def read_prereq_owned(pid: int, owner: int, kind: int) -> bool:
    if kind == 0:
        return True
    player = PLAYER_BASE + owner * PLAYER_STRIDE
    return u16(pid, player + PLAYER_PREREQ_BUILDING_TABLE_OFF + kind * 2) != 0


def read_prereq_own(pid: int, owner: int, kind: int) -> bool:
    if kind == 0:
        return True
    player = PLAYER_BASE + owner * PLAYER_STRIDE
    return u16(pid, player + PLAYER_PREREQ_OWN_TABLE_OFF + kind * 2) != 0


def read_live_units(pid: int) -> list[dict[str, int]]:
    exists = struct.unpack(
        f"<{UNIT_POOL_CAPACITY}h", read_memory(pid, UNIT_EXISTS_BASE, UNIT_POOL_CAPACITY * 2),
    )
    units: list[dict[str, int]] = []
    for slot, active in enumerate(exists):
        if not active:
            continue
        base = UNIT_POOL_BASE + slot * UNIT_STRIDE
        raw = read_memory(pid, base, UNIT_STRIDE)
        units.append({
            "slot": slot,
            "type": raw[UNIT_TYPE_OFF],
            "owner": raw[UNIT_OWNER_OFF],
            "complete": bool(struct.unpack_from("<i", raw, UNIT_COMPLETE_FLAG_OFF)[0] & 0x2),
            "order_state": struct.unpack_from("<i", raw, UNIT_ORDER_STATE_OFF)[0],
            "under_construction_kind": struct.unpack_from("<h", raw, UNIT_UNDER_CONSTRUCTION_TARGET_KIND_OFF)[0],
        })
    return units


def owner_building_counts(units: Sequence[Mapping[str, int]], owner: int) -> tuple[dict[int, int], int]:
    """Per-kind live building counts + total N, mirroring `FUN_0043DBB0`'s
    own roster scan (0x0043DE00-0x0043DE73): completed buildings counted by
    their own type, buildings under construction counted by their target
    kind. Both contribute to the shared total `N`."""

    counts: dict[int, int] = {}
    total = 0
    for unit in units:
        if unit["owner"] != owner:
            continue
        if unit["complete"]:
            counts[unit["type"]] = counts.get(unit["type"], 0) + 1
            total += 1
        if unit["order_state"] == 0xC:
            kind = unit["under_construction_kind"]
            counts[kind] = counts.get(kind, 0) + 1
            total += 1
    return counts, total


def type_cap(*, typemax: int, total_n: int) -> int:
    if total_n <= 0:
        return typemax
    quotient = (typemax * total_n) // 6
    if quotient % 12 != 0:
        quotient += typemax
    return quotient


def classify_candidate(
    *, record: Mapping[str, Any], faction_flags: Mapping[int, bool], static: Mapping[str, int],
    override_switch: int, type_spec: Mapping[str, int], prereq_building_owned: bool,
    prereq_own_owned: bool, current_count: int, total_n: int,
) -> str:
    """Pure decision function -- mirrors `FUN_0043DBB0`'s roster-driven
    faction gate, then `FUN_0043DB00`'s cap/prereq gates in the original's
    own branch order, then the per-kind type cap `FUN_0043DBB0` applies to
    its surviving candidate list."""

    nation_kind = record["nation_kind"]
    if not faction_flags.get(nation_kind, False):
        return "FACTION_BLOCK"

    if not type_spec["avail"]:
        return "SCENARIO_UNAVAIL"

    if static["ai_flag"] == 1 and override_switch == 0:
        cap = static["build_cap_denom"] // 5
        if static["total_buildings"] >= cap:
            return "BUILD_COUNT_CAP"

    if record["prereq_building_type"] != 0 and not prereq_building_owned:
        return "PREREQ_BUILDING"

    if record["prereq_own_kind"] != 0 and not prereq_own_owned:
        return "PREREQ_OWN"

    cap = type_cap(typemax=type_spec["typemax"], total_n=total_n)
    if current_count >= cap:
        return "TYPE_CAP"

    return "WOULD_BUILD"


class ConstructionGateHistogramSampler:
    def __init__(self, pid: int, records: Sequence[Mapping[str, Any]], owners: Sequence[int] = OWNERS):
        self.pid = pid
        self.owners = tuple(owners)
        self.records = list(records)
        self.histogram: dict[int, dict[str, int]] = {
            owner: {reason: 0 for reason in REASONS} for owner in self.owners
        }
        self.by_building_type: dict[tuple[int, int, str], int] = {}
        self.sample_count = 0
        self.faction_flags_ever_true: dict[int, set[int]] = {owner: set() for owner in self.owners}
        self._stop = threading.Event()
        self.error: str | None = None

    def sample_once(self) -> None:
        override_switch = u16(self.pid, OVERRIDE_SWITCH)
        units = read_live_units(self.pid)
        for owner in self.owners:
            faction_flags = read_owner_faction_flags(self.pid, owner)
            for kind, on in faction_flags.items():
                if on:
                    self.faction_flags_ever_true[owner].add(kind)
            static = read_owner_static(self.pid, owner)
            counts, total_n = owner_building_counts(units, owner)
            for record in self.records:
                bt = record["building_type"]
                type_spec = read_type_spec_build(self.pid, bt)
                prereq_building_owned = read_prereq_owned(self.pid, owner, record["prereq_building_type"])
                prereq_own_owned = read_prereq_own(self.pid, owner, record["prereq_own_kind"])
                reason = classify_candidate(
                    record=record, faction_flags=faction_flags, static=static,
                    override_switch=override_switch, type_spec=type_spec,
                    prereq_building_owned=prereq_building_owned, prereq_own_owned=prereq_own_owned,
                    current_count=counts.get(bt, 0), total_n=total_n,
                )
                self.histogram[owner][reason] += 1
                key = (owner, bt, reason)
                self.by_building_type[key] = self.by_building_type.get(key, 0) + 1
        self.sample_count += 1

    def run(self, duration_seconds: float, period_seconds: float) -> None:
        deadline = time.monotonic() + duration_seconds
        while time.monotonic() < deadline and not self._stop.is_set():
            tick_started = time.monotonic()
            try:
                self.sample_once()
            except (OSError, struct.error) as exc:
                self.error = str(exc)
                return
            time.sleep(max(0.0, period_seconds - (time.monotonic() - tick_started)))

    def stop(self) -> None:
        self._stop.set()

    def result(self) -> dict[str, Any]:
        return {
            "sample_count": self.sample_count,
            "error": self.error,
            "owners": {
                str(owner): {
                    "histogram": self.histogram[owner],
                    "faction_flags_ever_true": sorted(self.faction_flags_ever_true[owner]),
                    "by_building_type": [
                        {"building_type": bt, "reason": reason, "count": count}
                        for (o, bt, reason), count in sorted(
                            self.by_building_type.items(), key=lambda kv: -kv[1],
                        )
                        if o == owner
                    ],
                }
                for owner in self.owners
            },
        }


def _find_game_pid(needle: bytes, timeout: float) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for proc_dir in Path("/proc").iterdir():
            if not proc_dir.name.isdigit():
                continue
            try:
                cmdline = (proc_dir / "cmdline").read_bytes()
            except (FileNotFoundError, ProcessLookupError, PermissionError):
                continue
            if needle in cmdline and b"explorer" not in cmdline:
                return int(proc_dir.name)
        time.sleep(0.5)
    raise ProbeError(f"game process matching {needle!r} not found within {timeout}s")


def _run(argv: list[str], *, timeout: float, cwd: Path = REPO) -> dict[str, Any]:
    proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
    if proc.returncode != 0:
        raise ProbeError(f"{argv[:2]} exit={proc.returncode} stderr={proc.stderr[-4000:]}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ProbeError(f"non-JSON stdout from {argv[:2]}: {exc}; stdout={proc.stdout[-2000:]}") from exc


def run_one(
    *, source: Path, runtime_root: Path, artifact_root: Path, chain_goal: str,
    sample_seconds: float, sample_period: float, timeout: float,
) -> dict[str, Any]:
    source, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe.read_bytes()).hexdigest() != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    records = build_table.load_construction_table(source_exe)

    run_tag = f"run_{time.strftime('%Y%m%d_%H%M%S')}_{time.time_ns() % 1_000_000}"
    run_root = runtime_root / run_tag
    run_root.mkdir(parents=True)
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

    baseline_argv = [
        sys.executable, str(REPO / "tools/runtime_env.py"), "g1-baseline",
        "--manifest", str(manifest_path), "--screen", "1600x1200x24",
        "--timeout", "90", "--g4-chain-goal", chain_goal,
        "--g4-sample-seconds", str(sample_seconds), "--g4-sample-period", "1.0",
    ]
    baseline_proc = subprocess.Popen(
        baseline_argv, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )

    sampler_result: dict[str, Any] = {"status": "NOT_STARTED"}
    try:
        pid = _find_game_pid(str(private_exe).encode(), timeout=60.0)
        sampler = ConstructionGateHistogramSampler(pid, records, owners=OWNERS)
        sampler_thread = threading.Thread(
            target=sampler.run, args=(sample_seconds - 2.0, sample_period), daemon=True,
        )
        sampler_thread.start()
        sampler_thread.join(timeout=sample_seconds + 15.0)
        if sampler_thread.is_alive():
            sampler.stop()
            sampler_thread.join(timeout=10.0)
        sampler_result = sampler.result()
        sampler_result["status"] = "OK" if sampler.error is None else "ERROR"
    except ProbeError as exc:
        sampler_result = {"status": "PID_NOT_FOUND", "error": str(exc)}

    try:
        baseline_out, baseline_err = baseline_proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        baseline_proc.kill()
        baseline_out, baseline_err = baseline_proc.communicate()

    evidence_path = run_dir / "output" / "g1_baseline.json"
    baseline: dict[str, Any] = {}
    if evidence_path.exists():
        baseline = json.loads(evidence_path.read_text(encoding="utf-8"))
    source_sha_after = sha256(source_exe.read_bytes()).hexdigest()

    import shutil
    if game_root.exists():
        shutil.rmtree(game_root, ignore_errors=True)

    return {
        "chain_goal": chain_goal,
        "sample_seconds": sample_seconds,
        "sample_period": sample_period,
        "run_root": str(run_root),
        "construction_table": {
            "total_records": len(records),
            "building_types": sorted(r["building_type"] for r in records),
        },
        "source_sha_before": ORIGINAL_SHA,
        "source_sha_after": source_sha_after,
        "source_unchanged": source_sha_after == ORIGINAL_SHA,
        "g1_baseline_cli_exit": baseline_proc.returncode,
        "g1_baseline_stderr_tail": baseline_err[-2000:] if baseline_err else "",
        "cleanup_ok": bool(baseline.get("cleanup", {}).get("ok")),
        "gate_histogram": sampler_result,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--chain-goal", default=DEFAULT_CHAIN_GOAL,
                         choices=sorted(runtime_env.G4_FIXED_CHAIN_GOALS))
    parser.add_argument("--sample-seconds", type=float, default=280.0)
    parser.add_argument("--sample-period", type=float, default=1.0)
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    result = run_one(
        source=args.source, runtime_root=args.runtime_root, artifact_root=args.artifact_root,
        chain_goal=args.chain_goal, sample_seconds=args.sample_seconds,
        sample_period=args.sample_period, timeout=args.timeout,
    )
    output = {"schema": "syw2plus.g4-ai-construction-gate-histogram.v1", "run": result}
    args.out.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
