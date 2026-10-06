#!/usr/bin/env python3
"""Fresh paired Phase-C production and rally-point probe for ESL2608 G2.

Each invocation owns one private game copy, Wine prefix, and Xvfb display.  The
probe uses real UI clicks to select the HQ, queue a unit, and issue the rally
point.  It records the pre-existing hero count separately from normal unit
count so synthetic fixture units cannot be mistaken for the seven-hero setup.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import time
from typing import Any, Mapping, cast

# Keep the probe directly executable from the repository root as well as via
# pytest/``python -m``; Python otherwise puts only ``tools/`` on sys.path.
# ruff: noqa: E402
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from patches.population.g2_esl2608_runtime_layout import from_build_report
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools import runtime_env
from tools import g4_ai_production_table as production_table
from tools.g2_esl2608_phase_a_shift_probe import (
    BASE_SOURCE,
    DATA_OVERLAY,
    EXPECTED_BASELINE,
    EXPECTED_CANDIDATE,
    LANES,
    UNIT_INTERNAL_ID_OFFSET,
    UNIT_OWNER_OFFSET,
    UNIT_PENDING_XY_OFFSET,
    UNIT_STRIDE,
    UNIT_TYPE_OFFSET,
    UNIT_X_OFFSET,
    UNIT_Y_OFFSET,
    build_candidate,
    live_fixture,
    unit_layout,
    selection_snapshot,
)
from tools.g5_candidate_drag_probe import ProbeError, SupplyProbe, capture, sha256, write_json

HERO_COUNT_ADDRESS = 0x00956770 + 0x980
PLAYER_STRUCT_BASE = 0x00956770
PLAYER_STRUCT_STRIDE = 0x3ABC
MAP_WIDTH_ADDRESS = 0x00B3DE34
MAP_HEIGHT_ADDRESS = 0x00B3DE36
HQ_SELECT = (408, 242)
MINIMAP_BASE = (35, 560)
# The existing ESL2608 UI has the worker production cell at this x coordinate.
WORKER_PRODUCTION = (668, 540)
# Nation-specific hero cells in the existing ESL2608 production grid.
HERO_PRODUCTION_BY_NATION = {1: (776, 540), 2: (704, 540), 3: (704, 540)}
RALLY_MODE_BUTTON = (704, 503)
# The prior point (450, 300) decoded to the HQ tile itself (lap796).  Keep the
# same live command path but click open ground east of the HQ so the writer's
# rally fields have a falsifiable, non-overlapping target.
RALLY_POINT = (600, 300)
HERO_TYPES = frozenset(range(76, 103))
TYPE_SPEC_BASE = 0x009B5228
TYPE_SPEC_STRIDE = 0x394
TYPE_SPEC_FLAGS_OFFSET = 0x24
PLAYER_PREREQ_OWN_BASE = PLAYER_STRUCT_BASE + 0x315C
COMMAND_SLOT_BASE = 0x008930A6
COMMAND_SLOT_COUNT = 12
ACTIVE_ACTION_ADDRESS = 0x00892FFE
RALLY_DESCRIPTOR = 0x11
COMMAND_GRID_ORIGIN = (668, 503)
COMMAND_GRID_STEP = 36
COMMAND_GRID_ROW_Y = (503, 540, 576)
RALLY_TRACE_SCRIPT = REPO / "tools" / "g2_esl2608_rally_trace.py"

# Baseline ESL2608 static contract, pinned by
# analysis/memory_maps/g2_esl2608_phase_c_ui_contract_lap794.md.
RALLY_COMMAND = 0x15
RALLY_WRITER_VAS = (0x004125A5, 0x004125AF)
HERO_ELIGIBILITY_VA = 0x0043E7F0
HERO_ELIGIBILITY_CALLERS = (0x00406B68, 0x0048D1B7)


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _copy_overlay(game: Path) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for source in sorted(DATA_OVERLAY.rglob("*")):
        if source.is_symlink() or not source.is_file() or source.suffix.lower() in {".exe", ".xlsx"}:
            continue
        target = game / source.relative_to(DATA_OVERLAY)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(source.relative_to(DATA_OVERLAY)), "sha256": sha256(target)})
    return copied


def _wait(pid: int, predicate: Any, label: str, timeout: float = 45) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            last = read_state(pid)
            if predicate(last):
                return last
        except (OSError, ValueError, ProbeError) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.25)
    raise ProbeError(f"{label} timeout; last={last}")


def _player(pid: int) -> dict[str, Any]:
    state = read_state(pid)
    player = state["players"][0]
    nation = int(player["nation"])
    hero_count_address = PLAYER_STRUCT_BASE + nation * PLAYER_STRUCT_STRIDE + 0x980
    return {
        "ps": state["ps"], "tick": state["tick"],
        **{key: player[key] for key in ("nation", "count", "used", "rice", "wood", "reserved", "count_cap", "cap")},
        "hero_count_raw": int.from_bytes(read_memory(pid, hero_count_address, 4), "little"),
        "hero_count_address": hero_count_address,
    }


def _unit_row(pid: int, slot: int, *, candidate: bool) -> dict[str, int]:
    base, exists, capacity = unit_layout(candidate)
    if not 0 < slot < capacity:
        raise ProbeError(f"unit slot outside layout: {slot}")
    unit = base + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "exists": int.from_bytes(read_memory(pid, exists + slot * 2, 2), "little"),
        "type": int.from_bytes(read_memory(pid, unit + UNIT_TYPE_OFFSET, 1), "little"),
        "owner": int.from_bytes(read_memory(pid, unit + UNIT_OWNER_OFFSET, 1), "little"),
        "internal_id": int.from_bytes(read_memory(pid, unit + UNIT_INTERNAL_ID_OFFSET, 4), "little"),
        "x": int.from_bytes(read_memory(pid, unit + UNIT_X_OFFSET, 2), "little", signed=True),
        "y": int.from_bytes(read_memory(pid, unit + UNIT_Y_OFFSET, 2), "little", signed=True),
        "pending_xy": int.from_bytes(read_memory(pid, unit + UNIT_PENDING_XY_OFFSET, 4), "little"),
        "command": int.from_bytes(read_memory(pid, unit + 0x290, 2), "little", signed=True),
        "rally_x": int.from_bytes(read_memory(pid, unit + 0x654, 2), "little", signed=True),
        "rally_y": int.from_bytes(read_memory(pid, unit + 0x656, 2), "little", signed=True),
        "production_type": int.from_bytes(read_memory(pid, unit + 0x320, 4), "little"),
        "progress": int.from_bytes(read_memory(pid, unit + 0x1F8, 4), "little"),
    }


def _read_u16(pid: int, address: int, *, signed: bool = False) -> int:
    return int.from_bytes(read_memory(pid, address, 2), "little", signed=signed)


def _command_slots(pid: int) -> list[int]:
    return [_read_u16(pid, COMMAND_SLOT_BASE + 2 * slot) for slot in range(COMMAND_SLOT_COUNT)]


def _command_grid_cell(slot: int) -> tuple[int, int]:
    if not 0 <= slot < 5:
        raise ProbeError(f"rally descriptor slot is not on the first command row: {slot}")
    return (COMMAND_GRID_ORIGIN[0] + COMMAND_GRID_STEP * slot, COMMAND_GRID_ORIGIN[1])


def _command_grid_cell_any(slot: int) -> tuple[int, int]:
    """Map the live 12-slot command array to its 4-column UI grid."""

    if not 0 <= slot < COMMAND_SLOT_COUNT:
        raise ProbeError(f"command slot outside UI grid: {slot}")
    return (
        COMMAND_GRID_ORIGIN[0] + COMMAND_GRID_STEP * (slot % 4),
        COMMAND_GRID_ROW_Y[slot // 4],
    )


def _type_spec(pid: int, kind: int) -> dict[str, int]:
    base = TYPE_SPEC_BASE + kind * TYPE_SPEC_STRIDE
    return {
        "kind": kind,
        "flags": int.from_bytes(read_memory(pid, base + TYPE_SPEC_FLAGS_OFFSET, 2), "little"),
    }


def _hero_contract(pid: int, source: Path, hq_type: int) -> list[dict[str, Any]]:
    """Resolve hero production from the live HQ type, never from nation/coordinates."""

    records = [
        record for record in production_table.production_records(source)
        if record["building_type"] == hq_type and record["produce_kind"] != -1
    ]
    contract: list[dict[str, Any]] = []
    for record in records:
        kind = int(record["produce_kind"])
        spec = _type_spec(pid, kind)
        if spec["flags"] & 0x8:
            contract.append({"record": record, "type_spec": spec})
    if not contract:
        raise ProbeError(f"live HQ type {hq_type} has no hero-flagged production record: {records}")
    return contract


def _ensure_prerequisite(
    pid: int, prefix: Path, *, candidate: bool, kind: int,
) -> dict[str, Any]:
    existing = [row for row in _owner_units(pid, candidate=candidate) if row["type"] == kind]
    if existing:
        return {"kind": kind, "method": "preexisting", "rows": existing}
    supply = SupplyProbe(prefix)
    map_width = _read_u16(pid, MAP_WIDTH_ADDRESS)
    map_height = _read_u16(pid, MAP_HEIGHT_ADDRESS)
    if not 1 < map_width <= 180 or not 1 < map_height <= 180:
        raise ProbeError(f"live map dimensions are invalid for prerequisite fixture: {map_width}x{map_height}")
    # The ESL2608 map family is not fixed-size across normal/fixed-start
    # fixtures.  Start inside the live map; op5's original placement scan
    # finds a legal cell from there.
    points = [
        (max(1, map_width // 2), max(1, map_height // 2)),
        (1, 1),
        (max(1, map_width - 2), max(1, map_height - 2)),
    ]
    last_receipt: dict[str, Any] | None = None
    for x, y in points:
        receipt = supply.call(op=5, owner=0, unit_type=kind, x=x, y=y, count=1)
        last_receipt = receipt
        if receipt.get("ok") and receipt.get("fixture_added") == 1:
            rows = [row for row in _owner_units(pid, candidate=candidate) if row["type"] == kind]
            if len(rows) == 1:
                gate_deadline = time.monotonic() + 10
                prereq_owned = 0
                while time.monotonic() < gate_deadline:
                    prereq_owned = _read_u16(pid, PLAYER_PREREQ_OWN_BASE + kind * 2)
                    if prereq_owned > 0:
                        break
                    time.sleep(0.25)
                return {
                    "kind": kind, "method": "native_engine_op5", "synthetic": True,
                    "requested_world": [x, y], "map_dimensions": [map_width, map_height],
                    "receipt": receipt, "rows": rows, "prereq_owned_cache": prereq_owned,
                }
    raise ProbeError(f"native prerequisite fixture failed for kind {kind}: {last_receipt}")


def _run_rally_trace(pid: int, control: Path, *, click, command_cell: tuple[int, int]) -> dict[str, Any]:
    control.mkdir(parents=True, exist_ok=True)
    armed = control / "armed.json"
    stop_flag = control / "stop.flag"
    summary_path = control / "summary.json"
    events_path = control / "events.jsonl"
    for stale in (armed, stop_flag, summary_path, events_path):
        stale.unlink(missing_ok=True)
    env = dict(os.environ, G2_RALLY_TRACE_CONTROL=str(control))
    log_path = control / "gdb.log"
    with log_path.open("w", encoding="utf-8") as log:
        gdb_proc = subprocess.Popen(
            ["gdb", "-p", str(pid), "--batch", "-x", str(RALLY_TRACE_SCRIPT)],
            env=env, stdout=log, stderr=log,
        )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not armed.exists():
            time.sleep(0.05)
        if not armed.exists():
            gdb_proc.terminate()
            gdb_proc.wait(timeout=10)
            raise ProbeError("rally trace did not arm before timeout")
        time.sleep(0.2)
        try:
            click(*command_cell)
            time.sleep(0.15)
            action = _read_u16(pid, ACTIVE_ACTION_ADDRESS)
            if action != RALLY_COMMAND:
                raise ProbeError(f"rally action was not armed: 0x{action:04x}")
            click(*RALLY_POINT)
            time.sleep(0.8)
        finally:
            stop_flag.write_text("1", encoding="utf-8")
            gdb_proc.send_signal(signal.SIGINT)
            try:
                gdb_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                gdb_proc.kill()
                gdb_proc.wait(timeout=5)
    summary: dict[str, Any] = {}
    if summary_path.exists():
        summary.update(json.loads(summary_path.read_text(encoding="utf-8")))
    else:
        summary["error"] = "no rally trace summary written"
    events: list[dict[str, Any]] = []
    if events_path.exists():
        events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary["events"] = events
    summary["command_cell"] = list(command_cell)
    summary["rally_point"] = list(RALLY_POINT)
    return summary


def _new_owner_units(pid: int, *, candidate: bool, known: set[int]) -> list[dict[str, int]]:
    _base, exists, capacity = unit_layout(candidate)
    rows: list[dict[str, int]] = []
    for slot in range(1, capacity):
        if slot in known or int.from_bytes(read_memory(pid, exists + slot * 2, 2), "little") == 0:
            continue
        row = _unit_row(pid, slot, candidate=candidate)
        if row["owner"] == 0:
            rows.append(row)
    return rows


def _owner_units(pid: int, *, candidate: bool) -> list[dict[str, int]]:
    _base, exists, capacity = unit_layout(candidate)
    rows: list[dict[str, int]] = []
    for slot in range(1, capacity):
        if int.from_bytes(read_memory(pid, exists + slot * 2, 2), "little") == 0:
            continue
        row = _unit_row(pid, slot, candidate=candidate)
        if row["owner"] == 0:
            rows.append(row)
    return rows


def run_probe(lane: str, variant: str, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if lane not in LANES or variant not in {"baseline", "candidate"}:
        raise ProbeError(f"unsupported lane/variant: {lane}/{variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    baseline_path = LANES[lane]
    baseline = baseline_path.read_bytes()
    baseline_sha = _digest(baseline)
    if baseline_sha != EXPECTED_BASELINE[lane]:
        raise ProbeError(f"baseline SHA mismatch: {baseline_sha}")
    candidate, build_report = build_candidate(baseline)
    candidate_sha = _digest(candidate)
    if candidate_sha != EXPECTED_CANDIDATE[lane]:
        raise ProbeError(f"candidate SHA mismatch: {candidate_sha}")
    layout = from_build_report(build_report["pool"])
    bridge_dir = artifact_root / "bridge"
    bridge_args = [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                   "--out-dir", str(bridge_dir), "--unit-pool-capacity",
                   "4093" if variant == "candidate" else "1200",
                   "--bridge-source", str(REPO / "patches/population/g5_c_repair_bridge.c")]
    if variant == "candidate":
        bridge_args += ["--unit-pool-base", hex(layout.unit_pool_base)]
    subprocess.run(bridge_args, cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    run_dir = Path(cast(str, cast(Mapping[str, Any], manifest["output"])["run_dir"]))
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("private source copy SHA mismatch before ESL2608 install")
    overlay = _copy_overlay(game)
    private_exe.write_bytes(baseline if variant == "baseline" else candidate)
    expected_private = baseline_sha if variant == "baseline" else candidate_sha
    if sha256(private_exe) != expected_private:
        raise ProbeError("private ESL2608 executable SHA mismatch after install")
    result: dict[str, Any] = {
        "schema": "syw2plus.g2-esl2608-phase-c-production.v1", "status": "UNKNOWN",
        "lane": lane, "variant": variant,
        "fixture": {"synthetic": False, "ui_production": True, "hero_count_read": True,
                     "rally_point_screen": list(RALLY_POINT), "rally_input_button": 1},
        "provenance": {"baseline_path": str(baseline_path), "baseline_sha256": baseline_sha,
                        "candidate_sha256": candidate_sha, "private_exe_sha256": expected_private,
                        "private_run_dir": str(run_dir), "private_game": str(game),
                        "private_prefix": str(prefix), "overlay_files": overlay,
                        "bridge_sha256": sha256(bridge), "build_report": build_report},
        "inputs": [], "stages": {}, "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    game_proc: Any = None
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
                   SYW2_SUPPLY_PROBE="1")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env,
                                     stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid
        _wait(pid, lambda state: state.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        origin = (int(info["x"]), int(info["y"]))

        def click(x: int, y: int, *, button: int = 1) -> None:
            subprocess.run([sys.executable, str(REPO / "tools/x11_mouse_click.py"),
                            "--display", display, str(origin[0] + x), str(origin[1] + y),
                            "--button", str(button)], env=env, stdout=log, stderr=log,
                           timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "button": button})

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log,
                       timeout=10, check=True)
        click(184, 560)
        _wait(pid, lambda state: state.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        _wait(pid, lambda state: state.get("ps") == 5, "ps5")
        _wait(pid, lambda state: state.get("ps") == 5 and
             runtime_env._read_local_ready_state(lambda address, size: read_memory(pid, address, size)).get("ready_value") == 1,
             "ready", 15)
        click(608, 564)
        _wait(pid, lambda state: state.get("ps") == 3 and int(state.get("tick", 0)) > 0, "ps3")
        time.sleep(1)

        before = _player(pid)
        known_units = {row["slot"] for row in _owner_units(pid, candidate=variant == "candidate")}
        result["stages"]["start"] = {"player": before, "live_owner0_units": len(known_units)}
        # Recenter on the base, then select the HQ using the same production UI
        # contract used by the prior user-facing smoke, without memory writes.
        click(*MINIMAP_BASE)
        time.sleep(0.4)
        click(*HQ_SELECT)
        time.sleep(0.3)
        hq_selection = selection_snapshot(pid)
        if hq_selection["count"] != 1:
            raise ProbeError(f"HQ selection did not produce one selected unit: {hq_selection}")
        command_slots = _command_slots(pid)
        try:
            rally_slot = command_slots.index(RALLY_DESCRIPTOR)
        except ValueError as exc:
            raise ProbeError(f"live command slots contain no rally descriptor 0x11: {command_slots}") from exc
        rally_cell = _command_grid_cell(rally_slot)
        hq_slot = hq_selection["slots"][0]
        hq_unit = _unit_row(pid, hq_slot, candidate=variant == "candidate")
        hero_contract = _hero_contract(pid, baseline_path, hq_unit["type"])
        result["stages"]["hq"] = {
            "selection": hq_selection, "player": _player(pid),
            "unit": hq_unit,
            "command_slots": command_slots, "rally_descriptor": RALLY_DESCRIPTOR,
            "rally_slot": rally_slot, "rally_cell": list(rally_cell),
        }
        result["stages"]["hero_contract"] = {
            "hq_type": hq_unit["type"],
            "candidates": hero_contract,
        }

        worker_before = _player(pid)
        click(*WORKER_PRODUCTION)
        time.sleep(0.35)
        worker_after_order = _player(pid)
        result["stages"]["worker_order"] = {
            "button": list(WORKER_PRODUCTION), "before": worker_before,
            "after": worker_after_order,
            "resource_delta": {"rice": worker_after_order["rice"] - worker_before["rice"],
                                "wood": worker_after_order["wood"] - worker_before["wood"],
                                "reserved": worker_after_order["reserved"] - worker_before["reserved"]},
        }
        hq_rally_before = _unit_row(pid, hq_slot, candidate=variant == "candidate")
        rally_trace = _run_rally_trace(
            pid, artifact_root / "rally_trace", click=click, command_cell=rally_cell,
        )
        hq_rally_after = _unit_row(pid, hq_slot, candidate=variant == "candidate")
        result["stages"]["rally_input"] = {
            "screen": list(RALLY_POINT), "button": 1, "command_cell": list(rally_cell),
            "active_action_after_command_click": RALLY_COMMAND,
            "selection_after": selection_snapshot(pid), "trace": rally_trace,
            "player_after": _player(pid), "hq_before": hq_rally_before, "hq_after": hq_rally_after,
        }

        # Wait for the UI-queued worker, then compare its first observed
        # position/command with the rally input.  The fresh new-game scene may
        # have zero living heroes even for the seven-hero executable family;
        # that is recorded as an unresolved fixture question below rather than
        # synthesized into a passing roster assertion.
        deadline = time.monotonic() + 90
        produced: list[dict[str, int]] = []
        after = worker_after_order
        while time.monotonic() < deadline:
            produced = _new_owner_units(pid, candidate=variant == "candidate", known=known_units)
            after = _player(pid)
            if produced and after["count"] > worker_before["count"]:
                break
            time.sleep(0.5)
        if not produced:
            raise ProbeError(f"UI production produced no new owner-0 unit: before={worker_before}, after={after}")
        result["stages"]["produced"] = {
            "units": [_unit_row(pid, row["slot"], candidate=variant == "candidate") for row in produced],
            "count_before": worker_before["count"], "count_after": after["count"],
            "hero_count_before": before["hero_count_raw"], "hero_count_after": after["hero_count_raw"],
        }
        prerequisite_kinds = sorted({
            int(item["record"]["prereq_own_kind_a"])
            for item in hero_contract
            if int(item["record"]["prereq_own_kind_a"]) >= 0
        })
        prerequisite_fixtures = [
            _ensure_prerequisite(
                pid, prefix, candidate=variant == "candidate", kind=kind,
            )
            for kind in prerequisite_kinds
        ]
        result["stages"]["hero_prerequisites"] = {
            "kinds": prerequisite_kinds,
            "fixtures": prerequisite_fixtures,
        }
        result["fixture"]["prerequisite_engine_seeded"] = prerequisite_fixtures
        hero_before_order = _player(pid)
        hero_kinds = {int(item["record"]["produce_kind"]) for item in hero_contract}
        # The command descriptor is runtime-populated.  Try every live UI cell
        # except rally, and identify acceptance by the HQ's actual queued type;
        # nation-specific coordinates are only a preview and are not a contract.
        preferred_slots = [5, 6, 7, 8, 9, 10, 11, 4, 0, 1, 2]
        hero_attempts: list[dict[str, Any]] = []
        hero_after_order = hero_before_order
        hero_button: tuple[int, int] | None = None
        hero_kind_ordered: int | None = None
        for slot in preferred_slots:
            if slot == rally_slot or command_slots[slot] == 0:
                continue
            cell = _command_grid_cell_any(slot)
            before_hq = _unit_row(pid, hq_slot, candidate=variant == "candidate")
            before_click = _player(pid)
            click(*cell)
            time.sleep(0.35)
            after_hq = _unit_row(pid, hq_slot, candidate=variant == "candidate")
            after_click = _player(pid)
            accepted_kind = after_hq["production_type"] if (
                after_hq["command"] == 15 and after_hq["production_type"] in hero_kinds
            ) else None
            hero_attempts.append({
                "slot": slot, "descriptor": command_slots[slot], "cell": list(cell),
                "before_hq": before_hq, "after_hq": after_hq,
                "before": before_click, "after": after_click,
                "accepted_hero_kind": accepted_kind,
            })
            if accepted_kind is not None:
                hero_button = cell
                hero_kind_ordered = int(accepted_kind)
                hero_after_order = after_click
                break
            # If a different production was accepted, wait for it to finish so
            # the next cell is not silently discarded by a busy HQ.
            if after_hq["command"] == 15 and after_hq["production_type"] != before_hq["production_type"]:
                wait_deadline = time.monotonic() + 90
                while time.monotonic() < wait_deadline:
                    current_hq = _unit_row(pid, hq_slot, candidate=variant == "candidate")
                    if current_hq["command"] != 15:
                        break
                    time.sleep(0.5)
        hero_after_order = hero_after_order if hero_button is not None else _player(pid)
        hero_deadline = time.monotonic() + 90
        produced_slots = {row["slot"] for row in produced}
        hero_units: list[dict[str, int]] = []
        hero_after = hero_after_order
        while time.monotonic() < hero_deadline:
            hero_units = [
                row for row in _owner_units(pid, candidate=variant == "candidate")
                if row["slot"] not in known_units | produced_slots
                and row["type"] in hero_kinds
            ]
            hero_after = _player(pid)
            if hero_units and hero_after["hero_count_raw"] > hero_before_order["hero_count_raw"]:
                break
            time.sleep(0.5)
        result["stages"]["hero_order"] = {
            "button": None if hero_button is None else list(hero_button),
            "kind_ordered": hero_kind_ordered,
            "attempts": hero_attempts, "before": hero_before_order,
            "after_order": hero_after_order, "after_completion": hero_after,
            "hero_units": hero_units,
        }
        result["stages"]["final"] = {"player": after, "live_owner0_units": len(live_fixture(pid, candidate=variant == "candidate"))}
        worker_ordered = worker_after_order["rice"] < worker_before["rice"] or worker_after_order["wood"] < worker_before["wood"] or worker_after_order["reserved"] > worker_before["reserved"]
        production_counted = after["count"] > worker_before["count"]
        rally_changed = (hq_rally_after["rally_x"], hq_rally_after["rally_y"]) != (hq_rally_before["rally_x"], hq_rally_before["rally_y"])
        hero_produced = bool(hero_units) and hero_after["hero_count_raw"] > hero_before_order["hero_count_raw"]
        result["checks"] = {
            "hq_selected_by_ui": hq_selection["count"] == 1,
            "worker_ordered_by_ui": worker_ordered,
            "rally_input_delivered_by_ui": rally_changed,
            "worker_produced": production_counted,
            "hero_produced_by_ui": hero_produced,
        }
        result["status"] = "PASS" if all(result["checks"].values()) else "FAIL"
        capture(display, artifact_root / f"{time.strftime('%Y%m%d_%H%M%S')}_final.png", log)
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        cleanup_env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
        subprocess.run(["wineserver", "-k"], env=cleanup_env, stdout=log, stderr=log, timeout=10, check=False)
        subprocess.run(["wineserver", "-w"], env=cleanup_env, stdout=log, stderr=log, timeout=10, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=5)
        result["game_exit_code_before_cleanup"] = None if game_proc is None else game_proc.poll()
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix), "game_removed": False}
        if game.exists():
            shutil.rmtree(game)
        result["cleanup"]["game_removed"] = not game.exists()
        result["source_data_sha_after"] = sha256(baseline_path)
        result["source_data_unchanged"] = result["source_data_sha_after"] == baseline_sha
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=sorted(LANES), required=True)
    parser.add_argument("--variant", choices=("baseline", "candidate"), required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.lane, args.variant, args.runtime_root, args.artifact_root)
    print(json.dumps({"status": result.get("status"), "lane": args.lane,
                      "variant": args.variant, "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
