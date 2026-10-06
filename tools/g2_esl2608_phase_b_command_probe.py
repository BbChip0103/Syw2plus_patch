#!/usr/bin/env python3
"""Fresh paired Phase-B command probe for the ESL2608 G2 executables.

This probe deliberately keeps the stock selection cap at 20.  It reuses the
Phase-A sparse 100-unit fixture, then measures real UI MOVE, ATTACK, STOP,
HOLD, and PATROL orders for the same 20 selected units plus one unselected
sentinel.  The private game copy, Wine prefix, and Xvfb are unique per run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, cast

import numpy as np

from patches.population.g2_esl2608_runtime_layout import from_build_report
from patches.population.runtime_driver import read as read_memory
from tools import runtime_env
from tools.g2_esl2608_phase_a_shift_probe import (
    BASE_SOURCE, DATA_OVERLAY, LANES, EXPECTED_BASELINE, EXPECTED_CANDIDATE,
    CALIBRATION_POINTS, SEED_TYPE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    UNIT_INTERNAL_ID_OFFSET, UNIT_OWNER_OFFSET, UNIT_HP_OFFSET, UNIT_TYPE_OFFSET,
    UNIT_X_OFFSET, UNIT_Y_OFFSET, VISIBLE_WORKER_SLOT, build_candidate, find_worker,
    live_fixture, unit_layout, selection_snapshot,
)
from tools.g5_candidate_drag_probe import ProbeError, SupplyProbe, capture, sha256, write_json
from tools.g5_screen_world_calibration import decode_xy, fit_affine

REPO = Path(__file__).resolve().parents[1]
STOCK_SELECTION_BASE = 0x00899024
BUTTONS = {"stop": (667, 503), "attack": (667, 538), "patrol": (703, 538), "hold": (740, 538)}
ATTACK_PENDING_LOW16 = 4
MOVE_PENDING_LOW16 = 3


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


def _row(pid: int, slot: int, *, candidate: bool) -> dict[str, int]:
    base, _exists, capacity = unit_layout(candidate)
    if not 0 < slot < capacity:
        raise ProbeError(f"slot outside selected layout: {slot}")
    block = read_memory(pid, base + slot * UNIT_STRIDE + 0x290, 0x100)
    return {
        "slot": slot,
        "command": int.from_bytes(block[0:2], "little", signed=True),
        "pending": int.from_bytes(block[0xF4:0xF8], "little"),
        "pending_xy": int.from_bytes(block[0xF8:0xFC], "little"),
    }


def _observe(
    pid: int, selected: list[int], sentinel: int, *, candidate: bool,
    action: Callable[[], None], label: str, window: float = 4.0,
    predicate: Callable[[dict[str, int]], bool] | None = None,
) -> dict[str, Any]:
    slots = selected + [sentinel]
    before = {slot: _row(pid, slot, candidate=candidate) for slot in slots}
    action()
    seen: dict[int, list[dict[str, int]]] = {slot: [] for slot in slots}
    deadline = time.monotonic() + window
    samples = 0
    while time.monotonic() < deadline:
        for slot in slots:
            seen[slot].append(_row(pid, slot, candidate=candidate))
        samples += 1
        time.sleep(0.01 if time.monotonic() + 2.5 >= deadline else 0.05)

    def delta(slot: int, row: dict[str, int]) -> bool:
        base = before[slot]
        return any(row[key] != base[key] for key in ("command", "pending", "pending_xy"))

    def matched(slot: int, row: dict[str, int]) -> bool:
        return predicate(row) if predicate is not None else delta(slot, row)

    selected_rows = {slot: rows for slot, rows in seen.items() if slot != sentinel}
    selected_match = {slot for slot, rows in selected_rows.items() if any(matched(slot, row) for row in rows)}
    sentinel_rows = seen[sentinel]
    sentinel_delta = any(delta(sentinel, row) for row in sentinel_rows)
    pending_values = sorted({hex(row["pending"]) for rows in seen.values() for row in rows})
    command_values = sorted({row["command"] for rows in seen.values() for row in rows})
    return {
        "label": label, "selected_count": len(selected), "sentinel": sentinel,
        "samples": samples, "before": before,
        "selected_match_count": len(selected_match),
        "selected_match_slots": sorted(selected_match),
        "selected_all_matched": len(selected_match) == len(selected),
        "sentinel_changed": sentinel_delta,
        "sentinel_final": seen[sentinel][-1] if seen[sentinel] else before[sentinel],
        "pending_values": pending_values, "command_values": command_values,
        "selected_final": {str(slot): rows[-1] for slot, rows in selected_rows.items() if rows},
    }


def _find_phase_b_worker(pid: int, *, candidate: bool) -> dict[str, int]:
    """Use the pinned anchor first, then a bounded live-worker scan.

    ESL2608 normal startup has occasionally changed the unit type at stock
    slot 1198 while retaining the same live owner-0 anchor.  Phase B only
    needs a live selectable anchor for calibration and fixture placement, not
    a specific worker type, so the fallback remains constrained to the
    protected pool, owner 0, and positive HP.
    """
    try:
        return find_worker(pid, candidate=candidate)
    except ProbeError as original:
        if candidate:
            raise
        base, exists_base, capacity = unit_layout(False)
        anchor = base + VISIBLE_WORKER_SLOT * UNIT_STRIDE
        anchor_exists = int.from_bytes(read_memory(pid, exists_base + VISIBLE_WORKER_SLOT * 2, 2), "little")
        anchor_owner = int.from_bytes(read_memory(pid, anchor + UNIT_OWNER_OFFSET, 1), "little")
        anchor_type = int.from_bytes(read_memory(pid, anchor + UNIT_TYPE_OFFSET, 1), "little")
        anchor_hp = int.from_bytes(read_memory(pid, anchor + UNIT_HP_OFFSET, 4), "little", signed=True)
        if anchor_exists and anchor_owner == 0 and anchor_type != 0 and anchor_hp > 0:
            return {
                "slot": VISIBLE_WORKER_SLOT, "exists": anchor_exists, "type": anchor_type,
                "owner": anchor_owner, "hp": anchor_hp,
                "x": int.from_bytes(read_memory(pid, anchor + UNIT_X_OFFSET, 2), "little", signed=True),
                "y": int.from_bytes(read_memory(pid, anchor + UNIT_Y_OFFSET, 2), "little", signed=True),
                "internal_id": int.from_bytes(read_memory(pid, anchor + UNIT_INTERNAL_ID_OFFSET, 4), "little"),
                "pool_mode": 0,
            }
        for slot in range(1, capacity):
            exists = int.from_bytes(read_memory(pid, exists_base + slot * 2, 2), "little")
            if not exists:
                continue
            unit = base + slot * UNIT_STRIDE
            unit_type = int.from_bytes(read_memory(pid, unit + UNIT_TYPE_OFFSET, 1), "little")
            owner = int.from_bytes(read_memory(pid, unit + UNIT_OWNER_OFFSET, 1), "little")
            hp = int.from_bytes(read_memory(pid, unit + UNIT_HP_OFFSET, 4), "little", signed=True)
            if owner == 0 and unit_type != 0 and hp > 0:
                return {
                    "slot": slot, "exists": exists, "type": unit_type, "owner": owner,
                    "hp": hp,
                    "x": int.from_bytes(read_memory(pid, unit + UNIT_X_OFFSET, 2), "little", signed=True),
                    "y": int.from_bytes(read_memory(pid, unit + UNIT_Y_OFFSET, 2), "little", signed=True),
                    "internal_id": int.from_bytes(read_memory(pid, unit + UNIT_INTERNAL_ID_OFFSET, 4), "little"),
                    "pool_mode": 0,
                }
        raise ProbeError(f"stock worker anchor and bounded worker scan failed: {original}") from original


def _wait_state(pid: int, predicate: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            last = runtime_env._read_state(pid) if hasattr(runtime_env, "_read_state") else {}
        except (OSError, ValueError):
            last = {}
        if predicate(last):
            return last
        time.sleep(0.25)
    raise ProbeError(f"{label} timeout; last={last}")


def _combat_target_snapshot(pid: int, slot: int, *, candidate: bool) -> dict[str, int | bool]:
    base, exists_base, _capacity = unit_layout(candidate)
    unit = base + slot * UNIT_STRIDE
    exists = int.from_bytes(read_memory(pid, exists_base + slot * 2, 2), "little")
    return {
        "exists": bool(exists),
        "owner": int.from_bytes(read_memory(pid, unit + UNIT_OWNER_OFFSET, 1), "little"),
        "hp": int.from_bytes(read_memory(pid, unit + UNIT_HP_OFFSET, 4), "little", signed=True),
        "x": int.from_bytes(read_memory(pid, unit + UNIT_X_OFFSET, 2), "little", signed=True),
        "y": int.from_bytes(read_memory(pid, unit + UNIT_Y_OFFSET, 2), "little", signed=True),
        "command": int.from_bytes(read_memory(pid, unit + 0x290, 2), "little", signed=True),
    }


def _observe_combat_target(
    pid: int, target_slot: int, initial: dict[str, int | bool], *, candidate: bool,
    window: float = 20.0, interval: float = 0.1,
) -> dict[str, Any]:
    """Observe a spawned enemy after an already-issued UI attack order.

    Command acceptance alone is not a combat result.  This records the target
    HP/liveness curve and only reports combat evidence when damage or target
    destruction is actually observed.
    """
    samples: list[dict[str, Any]] = []
    deadline = time.monotonic() + window
    started = time.monotonic()
    while time.monotonic() < deadline:
        row = _combat_target_snapshot(pid, target_slot, candidate=candidate)
        samples.append({"elapsed_s": round(time.monotonic() - started, 3), **row})
        if not row["exists"]:
            break
        time.sleep(interval)
    hp_values = [int(row["hp"]) for row in samples if row["exists"]]
    initial_hp = int(initial["hp"])
    min_hp = min(hp_values) if hp_values else initial_hp
    destroyed = any(not bool(row["exists"]) for row in samples)
    return {
        "target_slot": target_slot,
        "initial": initial,
        "samples": samples,
        "sample_count": len(samples),
        "initial_hp": initial_hp,
        "min_hp": min_hp,
        "final": samples[-1] if samples else initial,
        "damage_observed": min_hp < initial_hp,
        "destroyed": destroyed,
        "combat_observed": destroyed or min_hp < initial_hp,
    }


def run_probe(
    lane: str, variant: str, runtime_root: Path, artifact_root: Path, *, require_combat: bool = False,
) -> dict[str, Any]:
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
                   "--out-dir", str(bridge_dir), "--unit-pool-capacity", "4093" if variant == "candidate" else "1200"]
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
        "schema": "syw2plus.g2-esl2608-phase-b-command.v1", "status": "UNKNOWN",
        "lane": lane, "variant": variant,
        "fixture": {"synthetic": True, "owner": 0, "type": SEED_TYPE, "active_minimum": 100,
                     "selected": 20, "unselected_sentinel": 1},
        "provenance": {"lane_source": str(baseline_path), "baseline_sha256": baseline_sha,
                        "candidate_sha256": candidate_sha, "private_exe_sha256": expected_private,
                        "private_run_dir": str(run_dir), "private_game": str(game), "private_prefix": str(prefix),
                        "overlay_files": overlay, "bridge_sha256": sha256(bridge), "build_report": build_report},
        "inputs": [], "stages": {}, "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    game_proc: Any = None
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        from patches.population.runtime_driver import state as read_state
        def wait_for(pred: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = read_state(pid)
                    if pred(last):
                        return last
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda s: s.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        origin = (int(info["x"]), int(info["y"]))

        def click(x: int, y: int, *, button: int = 1, drag_to: tuple[int, int] | None = None) -> None:
            args = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(origin[0] + x), str(origin[1] + y), "--button", str(button)]
            if drag_to is not None:
                args += ["--drag-to", str(origin[0] + drag_to[0]), str(origin[1] + drag_to[1])]
            subprocess.run(args, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "button": button, "drag_to": list(drag_to) if drag_to else None})

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        wait_for(lambda s: s.get("ps") == 5 and runtime_env._read_local_ready_state(lambda a, n: read_memory(pid, a, n)).get("ready_value") == 1, "ready", 15)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")
        worker = _find_phase_b_worker(pid, candidate=variant == "candidate")
        supply = SupplyProbe(prefix)
        map_width = int.from_bytes(read_memory(pid, 0x00B3DE34, 2), "little", signed=True)
        map_height = int.from_bytes(read_memory(pid, 0x00B3DE36, 2), "little", signed=True)
        x_offsets = tuple(dx for dx in range(-30, 31, 3) if 0 < worker["x"] + dx < map_width)[:10]
        points = [(worker["x"] + dx, worker["y"] + dy) for dy in range(-10, 0) for dx in x_offsets
                  if 0 < worker["x"] + dx < map_width and 0 < worker["y"] + dy < map_height]
        if len(points) < 100:
            raise ProbeError(f"insufficient fixture points: {len(points)}")
        for x, y in points[:100]:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=x, y=y, count=1)
            if not receipt.get("ok") or receipt.get("fixture_added") != 1:
                raise ProbeError(f"fixture spawn failed at {(x, y)}: {receipt}")
        time.sleep(1)
        fixture = live_fixture(pid, candidate=variant == "candidate")
        if len(fixture) < 100:
            raise ProbeError(f"active fixture below 100: {len(fixture)}")
        ordered = sorted(fixture, key=lambda row: (row["y"], row["x"], row["slot"]))
        click(200, 170, drag_to=(730, 445))
        time.sleep(0.4)
        click(120, 90, button=3)
        time.sleep(0.2)
        base, _exists, _cap = unit_layout(variant == "candidate")
        worker_base = base + worker["slot"] * UNIT_STRIDE
        samples = []
        for point in CALIBRATION_POINTS:
            click(*point, button=3)
            time.sleep(0.2)
            samples.append((point, decode_xy(int.from_bytes(read_memory(pid, worker_base + UNIT_PENDING_XY_OFFSET, 4), "little"))))
        matrix, offset = fit_affine(samples)
        inverse = np.linalg.inv(matrix)
        def world_to_screen(x: int, y: int) -> tuple[int, int]:
            p = inverse @ (np.array([x, y]) - offset)
            return int(round(p[0])), int(round(p[1]))
        visible = [(row, world_to_screen(row["x"], row["y"])) for row in ordered
                   if 5 <= world_to_screen(row["x"], row["y"])[0] <= 795 and 45 <= world_to_screen(row["x"], row["y"])[1] <= 470]
        if len(visible) < 21:
            raise ProbeError(f"fewer than 21 visible rows: {len(visible)}")
        blank = world_to_screen(worker["x"], worker["y"] - 8)
        def deselect() -> None:
            click(*blank)
            time.sleep(0.2)
            if selection_snapshot(pid)["count"] != 0:
                raise ProbeError("deselect point selected a unit")
        isolated: list[tuple[dict[str, int], tuple[int, int], int]] = []
        for target, screen in visible:
            for dy in (-12, -20, -6, 0, 6):
                deselect()
                click(screen[0], screen[1] + dy)
                time.sleep(0.25)
                snap = selection_snapshot(pid)
                if snap["count"] == 1 and snap["slots"] == [target["slot"]]:
                    isolated.append((target, screen, dy))
                    break
            if len(isolated) >= 21:
                break
        if len(isolated) < 21:
            raise ProbeError(f"fewer than 21 isolated rows: {len(isolated)}")
        selected_rows = isolated[:20]
        sentinel_row = isolated[20]
        deselect()
        for index, (_row_data, screen, dy) in enumerate(selected_rows):
            if index:
                subprocess.run(["xdotool", "keydown", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
                time.sleep(0.12)
            click(screen[0], screen[1] + dy)
            if index:
                time.sleep(0.12)
                subprocess.run(["xdotool", "keyup", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            time.sleep(0.15)
        selected = selection_snapshot(pid)["slots"]
        if len(selected) != 20 or len(set(selected)) != 20:
            raise ProbeError(f"20-unit selection failed: {selected}")
        sentinel = sentinel_row[0]["slot"]

        def reselect_current() -> None:
            """Reselect the visible current 20-unit group after it moves."""
            nonlocal selected, sentinel
            click(12, 40, drag_to=(788, 470))
            time.sleep(0.8)
            restored = selection_snapshot(pid)
            if restored["count"] != 20 or restored["unique_slots"] != 20:
                raise ProbeError(f"current 20-unit reselection failed: {restored}")
            selected = list(restored["slots"])
            live = live_fixture(pid, candidate=variant == "candidate")
            alternatives = [row["slot"] for row in live if row["owner"] == 0 and row["slot"] not in selected]
            if not alternatives:
                raise ProbeError("current 20-unit reselection left no unselected sentinel")
            sentinel = alternatives[0]

        result["stages"]["fixture"] = {"active_units": len(fixture), "selected": selected, "sentinel": sentinel,
                                         "worker": worker, "calibration_samples": [[list(p), list(w)] for p, w in samples],
                                         "calibration_max_residual": max(float(np.max(np.abs(matrix @ np.array(p) + offset - np.array(w)))) for p, w in samples)}
        dest_world = (worker["x"], worker["y"] + 6)
        dest_screen = world_to_screen(*dest_world)
        if not (10 <= dest_screen[0] <= 790 and 45 <= dest_screen[1] <= 470):
            raise ProbeError(f"move destination outside viewport: {dest_world}/{dest_screen}")

        def stage(name: str, action: Callable[[], None], *, predicate: Callable[[dict[str, int]], bool] | None = None,
                  window: float = 4.0, pre: Callable[[], None] | None = None) -> None:
            if pre is not None:
                pre()
            result["stages"][name] = _observe(pid, selected, sentinel, candidate=variant == "candidate",
                                                action=action, label=name, window=window, predicate=predicate)

        stage("move", lambda: click(*dest_screen, button=3), predicate=lambda row: (row["pending"] & 0xFFFF) == MOVE_PENDING_LOW16)
        stage("stop", lambda: click(*BUTTONS["stop"]), pre=lambda: (click(*dest_screen, button=3), time.sleep(0.6)))
        stage("hold", lambda: click(*BUTTONS["hold"]), window=6.0, pre=reselect_current)
        stage("patrol", lambda: (click(*BUTTONS["patrol"]), time.sleep(0.12), click(*dest_screen)),
              window=6.0, pre=reselect_current)
        click(*BUTTONS["stop"])
        time.sleep(0.5)
        reselect_current()
        attack_world = (worker["x"] + 3, worker["y"] + 6)
        attack_screen = world_to_screen(*attack_world)
        receipt = supply.call(op=5, owner=1, unit_type=SEED_TYPE, x=attack_world[0], y=attack_world[1], count=1)
        target_slot = int(receipt.get("producer", {}).get("slot", 0))
        if not receipt.get("ok") or receipt.get("fixture_added") != 1 or not target_slot:
            raise ProbeError(f"attack target spawn failed: {receipt}")
        target_base, _target_exists, _target_cap = unit_layout(variant == "candidate")
        target_handle = int.from_bytes(read_memory(pid, target_base + target_slot * UNIT_STRIDE + UNIT_INTERNAL_ID_OFFSET, 4), "little")
        target_owner = int.from_bytes(read_memory(pid, target_base + target_slot * UNIT_STRIDE + UNIT_OWNER_OFFSET, 1), "little")
        target_hp = int.from_bytes(read_memory(pid, target_base + target_slot * UNIT_STRIDE + UNIT_HP_OFFSET, 4), "little", signed=True)
        if target_owner != 1 or target_hp <= 0:
            raise ProbeError(f"attack target not live after spawn: slot={target_slot}, owner={target_owner}, hp={target_hp}")
        result["stages"]["attack_fixture"] = {"slot": target_slot, "handle": target_handle,
                                                "world": list(attack_world), "screen": list(attack_screen)}
        target_initial = _combat_target_snapshot(pid, target_slot, candidate=variant == "candidate")
        if require_combat and (not target_initial["exists"] or int(target_initial["hp"]) <= 0):
            raise ProbeError(f"attack target was not live immediately before attack: {target_initial}")
        stage("attack", lambda: (click(*BUTTONS["attack"]), time.sleep(0.1), click(*attack_screen)),
              predicate=lambda row: row["command"] == 4 or (row["pending"] & 0xFFFF) == ATTACK_PENDING_LOW16,
              window=8.0 if not require_combat else 4.0)
        if require_combat:
            result["stages"]["combat"] = _observe_combat_target(
                pid, target_slot, target_initial, candidate=variant == "candidate",
            )
        result["status"] = "PASS" if all(
            result["stages"][name]["selected_all_matched"] and not result["stages"][name]["sentinel_changed"]
            for name in ("move", "stop", "hold", "patrol", "attack")
        ) and (not require_combat or result["stages"]["combat"]["combat_observed"]) else "FAIL"
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
    parser.add_argument(
        "--require-combat", action="store_true",
        help="after the UI attack order, require observed target HP loss or destruction",
    )
    args = parser.parse_args(argv)
    result = run_probe(
        args.lane, args.variant, args.runtime_root, args.artifact_root,
        require_combat=args.require_combat,
    )
    print(json.dumps({"status": result.get("status"), "lane": args.lane, "variant": args.variant,
                      "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
