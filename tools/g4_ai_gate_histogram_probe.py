#!/usr/bin/env python3
"""G4 free-for-all AI production gate rejection histogram (STATUS 2026-09-27
13:45 운영자 방향, lap713 후속): "라이브로 어느 게이트가 owner1 발주를 막는지 계측".

Read-only for the protected original EXE. No breakpoint/detour is installed
in the game process -- this reuses the same `process_vm_readv`-based memory
read primitive every other probe in this repository uses
(`patches.population.runtime_driver.read`), applied to the *additional*
per-owner/per-kind gate tables `analysis/memory_maps/
ai_production_decision_path_00406770_20260923.md` (lap501) identified but
did not classify live, plus the `FUN_00406C70` prerequisite/tech gates that
document's `FUN_0043E7F0`-only model did not cover (see
`tools/g4_ai_production_table.py`).

For each sample tick, for each owner and each live, dispatch-eligible
production building it owns, every production-table record matching that
building's type is classified into exactly one rejection reason (or
`WOULD_ACCEPT`) using the *same* live tables the original game's AI reads --
never the outcome of an actual production attempt (the game only tests one
randomly-chosen candidate per building per 20-tick cycle; this probe
enumerates all of them every tick to get a complete, evidence-dense
breakdown rather than waiting out the RNG). The two are cross-checked by
`schema_version` in the output: `would_accept_units` here should track
`production_count_proxy`/`army_unit_count` growth from the existing
`g4_ai_behavior_probe.py` run over the same window when a run captures both.
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
from tools import g4_ai_production_table as prod_table  # noqa: E402
from tools import runtime_env  # noqa: E402

ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g4-ai-gate-histogram"
DEFAULT_CHAIN_GOAL = "_custom_game_chain_inject_seed1"
OWNERS = (0, 1)

# -- addresses, all cited from analysis/memory_maps/
# ai_production_decision_path_00406770_20260923.md (lap501) and this lap's
# FUN_00406C70 disassembly (tools/g4_ai_production_table.py docstring). --
PLAYER_BASE = 0x00956770
PLAYER_STRIDE = 0x3ABC
PLAYER_AI_OFF = 0x002
PLAYER_TOTAL_UNITS_OFF = 0x200A
PLAYER_PREREQ_COUNT_TABLE_OFF = 0x7F0     # 0x956F60 - PLAYER_BASE
PLAYER_PREREQ_OWN_TABLE_OFF = 0x315C      # 0x9598CC - PLAYER_BASE
PLAYER_TECH_RESEARCHED_TABLE_OFF = 0x331C  # 0x959A8C - PLAYER_BASE
PLAYER_HERO_COOLDOWN_BASE_OFF = 0x4D0
PLAYER_HERO_COUNT_OFF = 0x980

TYPE_SPEC_BASE = 0x009B5228
TYPE_SPEC_STRIDE = 0x394
TYPE_SPEC_FLAGS_OFF = 0x24
TYPE_SPEC_RATIO_CAP_OFF = 0x32
TYPE_SPEC_TYPEMAX_OFF = 0x34

COUNT_TABLE = 0x0089A388          # + (kind + owner*200)*2, i16
OVERRIDE_SWITCH = 0x009E1DD8      # i16, 0 == use TYPE_SPEC_TYPEMAX_OFF
SCENARIO_TYPEMAX_TABLE = 0x00B3DE70  # + (kind + owner*0x19C)*2, i16
AVAIL_FLAG_TABLE = 0x00B3E000        # + (kind + owner*0x19C)*2, i16
TECH_DEF_TABLE = 0x009E2F38          # + tech_kind*24, i32 (0 == undefined)

FLAG_HERO = 0x8
FLAG_CROWD_A = 0x4
FLAG_CROWD_B = 0x400
CROWD_RADIUS_TILES = 5
CROWD_THRESHOLD = 7

# patches/population/runtime_driver.py STOCK_POOL: (capacity, unit_base, exists_base)
UNIT_POOL_CAPACITY, UNIT_POOL_BASE, UNIT_EXISTS_BASE = 1200, 0x0066B790, 0x008990C8
UNIT_STRIDE = 0x758
UNIT_TYPE_OFF = 0x8D
UNIT_OWNER_OFF = 0x8E
UNIT_STATE_OFF = 0x1F4        # G-1: must equal 100 to be dispatch-eligible
UNIT_AUTORESPOND_FLAG_OFF = 0x1D8  # G-3: bit 0x80000
UNIT_X_OFF = 0x2A2
UNIT_Y_OFF = 0x2A4

REASONS = (
    "NATION_MISMATCH", "PREREQ_COUNT", "PREREQ_OWN", "TECH_NOT_RESEARCHED",
    "HERO_COOLDOWN", "HERO_CAP", "H_AVAIL", "H_TYPEMAX", "H_RATIO",
    "H_CROWD", "WOULD_ACCEPT",
)


class ProbeError(RuntimeError):
    pass


def i16(pid: int, address: int) -> int:
    return struct.unpack("<h", read_memory(pid, address, 2))[0]


def u16(pid: int, address: int) -> int:
    return struct.unpack("<H", read_memory(pid, address, 2))[0]


def i32(pid: int, address: int) -> int:
    return struct.unpack("<i", read_memory(pid, address, 4))[0]


def read_type_spec(pid: int, kind: int) -> dict[str, int]:
    base = TYPE_SPEC_BASE + kind * TYPE_SPEC_STRIDE
    return {
        "flags": u16(pid, base + TYPE_SPEC_FLAGS_OFF),
        "ratio_cap": i16(pid, base + TYPE_SPEC_RATIO_CAP_OFF),
        "typemax": i16(pid, base + TYPE_SPEC_TYPEMAX_OFF),
    }


def read_owner_dynamic(pid: int, owner: int, kinds: Sequence[int]) -> dict[str, Any]:
    """Everything that can change tick-to-tick, for one owner and the given
    kind set. One PlayerStruct-relative small read per (owner, kind) --
    cheap relative to the game's own per-tick work; see module docstring."""

    player = PLAYER_BASE + owner * PLAYER_STRIDE
    total_units = u16(pid, player + PLAYER_TOTAL_UNITS_OFF)
    per_kind: dict[int, dict[str, int]] = {}
    for kind in kinds:
        per_kind[kind] = {
            "count": u16(pid, COUNT_TABLE + (kind + owner * 200) * 2),
            "prereq_count_current": u16(pid, player + PLAYER_PREREQ_COUNT_TABLE_OFF + kind * 2),
            "prereq_owned": u16(pid, player + PLAYER_PREREQ_OWN_TABLE_OFF + kind * 2),
            "tech_researched": u16(pid, player + PLAYER_TECH_RESEARCHED_TABLE_OFF + kind * 2),
            "hero_cooldown": u16(pid, player + PLAYER_HERO_COOLDOWN_BASE_OFF + kind * 2),
        }
    return {
        "total_units": total_units,
        "hero_count": u16(pid, player + PLAYER_HERO_COUNT_OFF),
        "per_kind": per_kind,
    }


def read_owner_scenario(pid: int, owner: int, kinds: Sequence[int]) -> dict[int, dict[str, int]]:
    """Static-per-run scenario/availability tables; caller caches this."""

    override_switch = u16(pid, OVERRIDE_SWITCH)
    out: dict[int, dict[str, int]] = {}
    for kind in kinds:
        idx = kind + owner * 0x19C
        out[kind] = {
            "avail_flag": i16(pid, AVAIL_FLAG_TABLE + idx * 2),
            "scenario_typemax": i16(pid, SCENARIO_TYPEMAX_TABLE + idx * 2) if override_switch else None,
        }
    return out


def read_tech_def_exists(pid: int, tech_kind: int) -> bool:
    return i32(pid, TECH_DEF_TABLE + tech_kind * 24) != 0


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
            "state": struct.unpack_from("<i", raw, UNIT_STATE_OFF)[0],
            "autorespond": bool(struct.unpack_from("<i", raw, UNIT_AUTORESPOND_FLAG_OFF)[0] & 0x80000),
            "x": struct.unpack_from("<h", raw, UNIT_X_OFF)[0],
            "y": struct.unpack_from("<h", raw, UNIT_Y_OFF)[0],
        })
    return units


def crowd_density(units: Sequence[Mapping[str, int]], owner: int, kind: int, tile: tuple[int, int]) -> int:
    tx, ty = tile
    return sum(
        1 for u in units
        if u["owner"] == owner and u["type"] == kind
        and abs(u["x"] - tx) <= CROWD_RADIUS_TILES and abs(u["y"] - ty) <= CROWD_RADIUS_TILES
    )


def classify_candidate(
    *, record: Mapping[str, Any], owner_nation: int, dynamic: Mapping[str, Any],
    scenario: Mapping[str, Any], type_spec: Mapping[str, int], tech_def_exists: bool,
    crowd_count: int | None,
) -> str:
    """Pure decision function -- mirrors FUN_00406C70 then FUN_0043E7F0 then
    FUN_00406B00's crowd check, in the original's own branch order."""

    # FUN_00406C70's nation lookup defaults out-of-range values to bit0
    # (Joseon) rather than rejecting outright (0x00406d5a `ja`-to-default).
    nation_bit = 1 << ((owner_nation - 1) if owner_nation in (1, 2, 3, 4) else 0)
    if not record["nation_mask"] & nation_bit:
        return "NATION_MISMATCH"

    kind = record["produce_kind"]
    per_kind = dynamic["per_kind"][kind]

    prereq_count_kind = record["prereq_count_kind"]
    if prereq_count_kind != -1:
        prereq_dyn = dynamic["per_kind"].get(prereq_count_kind, per_kind)
        if prereq_dyn["prereq_count_current"] < record["prereq_count_min"]:
            return "PREREQ_COUNT"

    for slot_key in ("prereq_own_kind_a", "prereq_own_kind_b"):
        prereq_kind = record[slot_key]
        if prereq_kind != -1:
            prereq_dyn = dynamic["per_kind"].get(prereq_kind, per_kind)
            if prereq_dyn["prereq_owned"] == 0:
                return "PREREQ_OWN"

    tech_kind = record["tech_kind"]
    if tech_kind != -1 and tech_def_exists:
        tech_dyn = dynamic["per_kind"].get(tech_kind, per_kind)
        if tech_dyn["tech_researched"] == 0:
            return "TECH_NOT_RESEARCHED"

    flags = type_spec["flags"]
    if flags & FLAG_HERO:
        if per_kind["hero_cooldown"] > 0:
            return "HERO_COOLDOWN"
        if dynamic["hero_count"] >= 5:
            return "HERO_CAP"

    avail_flag = scenario["avail_flag"]
    if avail_flag == 0:
        return "H_AVAIL"

    typemax = scenario["scenario_typemax"] if scenario["scenario_typemax"] is not None else type_spec["typemax"]
    if per_kind["count"] >= typemax:
        return "H_TYPEMAX"

    total = dynamic["total_units"]
    if total > 0:
        percent = per_kind["count"] * 100 // total
        if percent > type_spec["ratio_cap"]:
            return "H_RATIO"

    if flags & (FLAG_CROWD_A | FLAG_CROWD_B) and crowd_count is not None and crowd_count >= CROWD_THRESHOLD:
        return "H_CROWD"

    return "WOULD_ACCEPT"


class GateHistogramSampler:
    """Background sampler: polls the live game process for `duration_seconds`
    and accumulates a per-owner rejection histogram. Static tables (type
    spec, scenario overrides, tech definitions) are read once and cached;
    per-owner/per-kind dynamic tables are re-read every tick."""

    def __init__(self, pid: int, records: Sequence[Mapping[str, Any]], owners: Sequence[int] = OWNERS):
        self.pid = pid
        self.owners = tuple(owners)
        self.records_by_building = {
            bt: prod_table.records_for_building_type(list(records), bt)
            for bt in prod_table.building_types(list(records))
        }
        all_kinds = sorted({r["produce_kind"] for r in records}
                            | {k for r in records for k in
                               (r["prereq_count_kind"], r["prereq_own_kind_a"],
                                r["prereq_own_kind_b"], r["tech_kind"]) if k != -1})
        self._type_spec_cache = {k: read_type_spec(pid, k) for k in all_kinds}
        self._scenario_cache = {
            owner: read_owner_scenario(pid, owner, all_kinds) for owner in self.owners
        }
        self._tech_def_cache = {
            k: read_tech_def_exists(pid, k) for k in all_kinds if k != -1
        }
        self._all_kinds = all_kinds
        self.histogram: dict[int, dict[str, int]] = {
            owner: {reason: 0 for reason in REASONS} for owner in self.owners
        }
        # (owner, building_type, produce_kind, reason) -> count, so a
        # dominant reason in `histogram` can be traced back to the exact
        # record(s) responsible instead of just the gate name.
        self.by_record: dict[tuple[int, int, int, str], int] = {}
        self.sample_count = 0
        self.buildings_seen: dict[int, set[int]] = {owner: set() for owner in self.owners}
        self._stop = threading.Event()
        self.error: str | None = None

    def sample_once(self) -> None:
        units = read_live_units(self.pid)
        nations = {}
        for owner in self.owners:
            nations[owner] = read_memory(self.pid, PLAYER_BASE + owner * PLAYER_STRIDE + 0, 1)[0]
        dynamic_by_owner = {
            owner: read_owner_dynamic(self.pid, owner, self._all_kinds) for owner in self.owners
        }
        for owner in self.owners:
            buildings = [
                u for u in units
                if u["owner"] == owner and u["type"] in self.records_by_building
                and u["state"] == 100 and u["autorespond"]
            ]
            self.buildings_seen[owner].update(u["slot"] for u in buildings)
            for building in buildings:
                for record in self.records_by_building[building["type"]]:
                    kind = record["produce_kind"]
                    type_spec = self._type_spec_cache[kind]
                    needs_crowd = bool(type_spec["flags"] & (FLAG_CROWD_A | FLAG_CROWD_B))
                    crowd_count = (
                        crowd_density(units, owner, kind, (building["x"], building["y"]))
                        if needs_crowd else None
                    )
                    reason = classify_candidate(
                        record=record, owner_nation=nations[owner],
                        dynamic=dynamic_by_owner[owner],
                        scenario=self._scenario_cache[owner][kind],
                        type_spec=type_spec,
                        tech_def_exists=self._tech_def_cache.get(record["tech_kind"], False),
                        crowd_count=crowd_count,
                    )
                    self.histogram[owner][reason] += 1
                    key = (owner, building["type"], kind, reason)
                    self.by_record[key] = self.by_record.get(key, 0) + 1
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
                    "buildings_seen": sorted(self.buildings_seen[owner]),
                    "by_record": [
                        {"building_type": bt, "produce_kind": kind, "reason": reason, "count": count}
                        for (o, bt, kind, reason), count in sorted(
                            self.by_record.items(), key=lambda kv: -kv[1],
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

    records = prod_table.production_records(source_exe)

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
        sampler = GateHistogramSampler(pid, records, owners=OWNERS)
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
        "production_table": {
            "total_production_records": len(records),
            "building_types": sorted(prod_table.building_types(records)),
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
    output = {"schema": "syw2plus.g4-ai-gate-histogram.v1", "run": result}
    args.out.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
