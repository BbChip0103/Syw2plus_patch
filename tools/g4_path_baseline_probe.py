#!/usr/bin/env python3
"""G4-P1 pathfinding baseline probe (lap704), now with an optional candidate
variant (lap708, ``patches.pathing.g4_move_retry_budget_v1``).

STATUS's "다음 한 가지" asks for a repeatable raw scene that selects the
protected original executable's stock 20-unit selection cap, right-clicks a
worker-relative destination at least 20 tiles away, and records a per-tick
``(tick, x, y, command, hp)`` trace for every selected slot until arrival or
timeout.

This reuses the in-run screen->world self-calibration, dense fixture
seeding, selection snapshot and capture helpers already validated by
``tools/g5_worker_relative_move_attack_probe.py`` (imported, not copied, and
that file is not modified).  The G4/G2 fixed-seed two-player custom-game
chain (``runtime_env.g1_baseline`` with a ``G4_FIXED_CHAIN_GOALS`` goal) is
not used here: that chain has no fixture-seeding hook (no ``SupplyProbe``
call site) and is built around AI-controller sampling on a two-player
lobby, not a player-issued selected-unit move trace, so wiring it in for
this probe would be a second, unproven integration rather than the "reuse"
this card asks for.  This probe instead reuses the already-fixture-compatible
G5 solo flow, with the explicit caveat (per STATUS) that the unseeded solo
lobby places the worker (and therefore the whole scene) at a different
absolute map location each run -- terrain is not identical run to run.

Read-only with respect to the protected source executable: the source SHA
is checked before and after every run and only a private per-run copy is
ever executed.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any, Mapping

import numpy as np

from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError,
    SupplyProbe,
    DRAG_START,
    DRAG_END,
    STOCK_SELECTION_BASE,
    STOCK_SELECTION_CAPACITY,
    SEED_TYPE,
    VISIBLE_WORKER_SLOT,
    UNIT_BASE,
    UNIT_STRIDE,
    UNIT_COMMAND_OFFSET,
    UNIT_X_OFFSET,
    UNIT_Y_OFFSET,
    UNIT_HP_OFFSET,
    UNIT_PENDING_XY_OFFSET,
    selection_snapshot,
    unit_snapshot,
    dense_fixture_requests,
    sha256,
    write_json,
    capture,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g4-lap704-path-baseline"

CALIBRATION_SCREEN_POINTS = [
    (250, 200), (475, 200), (700, 200),
    (250, 320), (475, 320), (700, 320),
    (250, 440), (475, 440), (700, 440),
]
# lap704 run1 clicked screen (1375, 337) -- outside the real game window --
# and got zero movement from *every* selected slot, including the
# pre-existing worker; a same-run near-fixture control click at (604, 243)
# (inside the window) moved only the worker, not the 19 fixture units. The
# Xvfb desktop is 1600x1200, but this probe runs the *unpatched* protected
# original executable (G1's 1600x1200 presentation patch is deliberately not
# applied here), so ``runtime_env._game_window_ids`` only matches its native
# 800x600 content window; ``click()`` coordinates are relative to that
# window's own top-left (via ``crop``), so anything past its measured
# width/height lands in the surrounding Xvfb desktop, not on distant ground.
# lap705: rather than re-guess the box, derive it from the same
# ``content_info`` xwininfo reading the probe already takes for ``crop``, so
# the safe screen box is tied to the real measured window, not an assumed
# 800x600. ``HUD_HEIGHT_RATIO`` keeps the same y>=480-of-600 HUD cutoff G5's
# probes use, scaled to whatever height is actually measured.
SAFE_SCREEN_MARGIN_PX = 40
HUD_HEIGHT_RATIO = 480 / 600
ARRIVAL_RADIUS_TILES = 3.0
STAGNATION_TICKS = 20
TRACE_POLL_INTERVAL_S = 0.15
TRACE_TIMEOUT_S = 90.0
# lap705 (06:05 operator direction, following lap704 BLOCKED): reuse
# tools/g5_worker_relative_move_attack_probe.py's fixture/drag/right-click
# procedure unchanged (verified identical here -- same dense_fixture_requests,
# owner=0/SEED_TYPE spawn via SupplyProbe op=5, same 9-point calibration) and
# change only the destination distance and add a per-tick trajectory trace.
# lap704's >=20-tile requirement was not reachable on a fixed camera: the
# in-run affine calibration measured ~32-36 screen px per world tile in this
# run's isometric projection, so 20 tiles is ~640-720px -- wider than the
# ~720x420px safe box itself. These candidates instead escalate along the
# single world axis lap682 already proved safe (dy only, no x component),
# picking the largest magnitude that still lands inside the measured window,
# which is "long distance" relative to lap682's own dy=6/dy=-4 baseline
# without inventing a new camera-movement mechanism.
LONG_DISTANCE_OFFSET_MAGNITUDES = (12, 10, 8)

# lap707 (operator strategy 07:45): the single-axis click above tops out
# around 12 tiles because it is bounded by the measured window, not the map.
# To reach STATUS's >=20-tile requirement, pan the camera itself: hold an
# arrow key (docs/history/laps/20260926_direct_g2_2608_scroll_rally_check.md
# observed ~20 world tiles/axis from a 1.5s hold in this engine's input
# layer, which G2's variant confirmed is byte-identical to the protected
# original in the input/scroll code path) and re-run the same worker-only
# 9-point calibration used for the initial mapping -- right-clicking issues
# a move order for whatever is *currently* selected, so this can only run
# while just the worker is selected, before the real 20-unit test group
# exists (see ``sample_calibration``'s docstring).
CAMERA_PAN_KEY_HOLD_MS = 1200
CAMERA_PAN_MAX_ATTEMPTS_PER_DIRECTION = 4
CAMERA_PAN_TARGET_DISTANCE_TILES = 20.0
# lap707 run2/5/6/7 observed the same-duration reverse hold reproducibly
# landing on unexplored fog-of-war instead of the worker's start view at one
# spawn world (asymmetric/edge-clamped scroll), so the return is verified
# and corrected in a closed loop rather than trusted open-loop.
CAMERA_RETURN_MAX_CORRECTIONS = 3
CAMERA_RETURN_TOLERANCE_TILES = 3.0
# ``dense_fixture_requests`` deliberately starts its grid at dy=-3 instead of
# dy=-4 "so its upper row does not overlap the nearby base footprint" --i.e.
# the base sits close to the worker on the -Y side. A destination farther out
# on that same axis forces the path to cross or detour around that footprint
# instead of inventing a new, unverified obstacle-detection mechanism.
OBSTACLE_ROW_OFFSET_MAGNITUDE = 8


def safe_screen_box(window_width: int, window_height: int) -> tuple[int, int, int, int]:
    """Real click-safe box for the measured content window, margin-inset and
    HUD-excluded (see ``HUD_HEIGHT_RATIO``/``SAFE_SCREEN_MARGIN_PX`` above)."""
    margin = SAFE_SCREEN_MARGIN_PX
    return (margin, window_width - margin, margin, int(window_height * HUD_HEIGHT_RATIO))


def _safe_box_margin(point: tuple[float, float], box: tuple[int, int, int, int]) -> float:
    """Distance from ``point`` to the nearest edge of ``box`` (negative if outside)."""
    x0, x1, y0, y1 = box
    return min(point[0] - x0, x1 - point[0], point[1] - y0, y1 - point[1])


def _screen_to_world(screen: tuple[int, int], matrix: np.ndarray, offset: np.ndarray) -> tuple[float, float]:
    point = matrix @ np.array(screen) + offset
    return float(point[0]), float(point[1])


def pan_candidate_ok(
    world: tuple[float, float], worker_start: tuple[int, int], target_distance: float,
) -> tuple[bool, float]:
    """Whether a camera-pan calibration sample is both on the 180x180 map and
    at least ``target_distance`` tiles from where the worker started."""
    dist = math.hypot(world[0] - worker_start[0], world[1] - worker_start[1])
    in_bounds = 0 <= world[0] < 180 and 0 <= world[1] < 180
    return (in_bounds and dist >= target_distance, dist)


def read_unit_trace_row(pid: int, slot: int) -> dict[str, Any]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
        "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
        "command": int.from_bytes(read_memory(pid, base + UNIT_COMMAND_OFFSET, 2), "little", signed=True),
        "hp": int.from_bytes(read_memory(pid, base + UNIT_HP_OFFSET, 2), "little", signed=True),
    }


def trace_movement(
    pid: int, slots: list[int], destination: tuple[int, int], *, timeout: float, interval: float,
) -> dict[str, Any]:
    """Sample one row per distinct game tick for every selected slot until
    every slot has been observed within ``ARRIVAL_RADIUS_TILES`` of
    ``destination`` at least once (the ``ever_matched`` technique from
    ``g5_worker_relative_move_attack_probe.poll_convergence``, applied here
    to a full per-tick trace instead of a single convergence count), or
    ``timeout`` elapses.
    """
    dest_x, dest_y = destination
    samples: list[dict[str, Any]] = []
    last_tick: int | None = None
    start = time.monotonic()
    deadline = start + timeout
    ever_arrived: set[int] = set()
    while True:
        tick = int(read_state(pid).get("tick", 0))
        if tick != last_tick:
            rows = [read_unit_trace_row(pid, slot) for slot in slots if 0 < slot < 1200]
            for row in rows:
                dist = math.hypot(row["x"] - dest_x, row["y"] - dest_y)
                row["distance_to_destination"] = round(dist, 3)
                if dist <= ARRIVAL_RADIUS_TILES:
                    ever_arrived.add(int(row["slot"]))
            samples.append({"tick": tick, "elapsed_s": round(time.monotonic() - start, 2), "rows": rows})
            last_tick = tick
        if len(ever_arrived) >= len(slots):
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(interval)
    return {
        "samples": samples,
        "ever_arrived_slots": sorted(ever_arrived),
        "ever_arrived_count": len(ever_arrived),
        "expected_count": len(slots),
        "converged": len(ever_arrived) >= len(slots),
        "timed_out": time.monotonic() >= deadline and len(ever_arrived) < len(slots),
    }


def compute_metrics(
    trace: Mapping[str, Any], slots: list[int], destination: tuple[int, int],
    start_positions: Mapping[int, tuple[int, int]],
) -> dict[str, Any]:
    dest_x, dest_y = destination
    per_slot: dict[int, dict[str, Any]] = {
        slot: {
            "arrival_tick": None, "path_length": 0.0, "last_xy": None, "ever_move_command": False,
            "stagnation_runs": [], "_run": 0, "_run_start_tick": None,
        }
        for slot in slots
    }
    for sample in trace["samples"]:
        tick = sample["tick"]
        for row in sample["rows"]:
            slot = row["slot"]
            state = per_slot[slot]
            xy = (row["x"], row["y"])
            if row["command"] == 3:
                state["ever_move_command"] = True
            if state["last_xy"] is not None:
                state["path_length"] += math.hypot(xy[0] - state["last_xy"][0], xy[1] - state["last_xy"][1])
                # "not idle" (command != 1) rather than requiring command==3
                # specifically, so a stall that shows up as some other
                # non-idle state (e.g. a blocked repath attempt) is still
                # caught.
                stalled = (
                    xy == state["last_xy"]
                    and row["command"] != 1
                    and row["distance_to_destination"] > ARRIVAL_RADIUS_TILES
                )
                if stalled:
                    if state["_run"] == 0:
                        state["_run_start_tick"] = tick
                    state["_run"] += 1
                else:
                    if state["_run"] >= STAGNATION_TICKS:
                        state["stagnation_runs"].append(
                            {"start_tick": state["_run_start_tick"], "length_ticks": state["_run"]}
                        )
                    state["_run"] = 0
                    state["_run_start_tick"] = None
            state["last_xy"] = xy
            if state["arrival_tick"] is None and row["distance_to_destination"] <= ARRIVAL_RADIUS_TILES:
                state["arrival_tick"] = tick
    for state in per_slot.values():
        if state["_run"] >= STAGNATION_TICKS:
            state["stagnation_runs"].append({"start_tick": state["_run_start_tick"], "length_ticks": state["_run"]})
        del state["_run"]
        del state["_run_start_tick"]

    per_slot_rows = []
    path_ratios = []
    for slot in slots:
        state = per_slot[slot]
        start_xy = start_positions.get(slot)
        straight_line = math.hypot(dest_x - start_xy[0], dest_y - start_xy[1]) if start_xy else None
        path_ratio = (
            state["path_length"] / straight_line if straight_line and straight_line > 0 else None
        )
        if path_ratio is not None:
            path_ratios.append(path_ratio)
        per_slot_rows.append({
            "slot": slot,
            "start_xy": list(start_xy) if start_xy else None,
            "final_xy": list(state["last_xy"]) if state["last_xy"] else None,
            "arrived": state["arrival_tick"] is not None,
            "arrival_tick": state["arrival_tick"],
            "path_length": round(state["path_length"], 3),
            "straight_line_distance": round(straight_line, 3) if straight_line is not None else None,
            "path_ratio": round(path_ratio, 3) if path_ratio is not None else None,
            "stagnation_runs": state["stagnation_runs"],
            "ever_move_command": state["ever_move_command"],
        })

    arrival_ticks = [row["arrival_tick"] for row in per_slot_rows if row["arrival_tick"] is not None]
    final_xs = [row["final_xy"][0] for row in per_slot_rows if row["final_xy"] is not None]
    final_ys = [row["final_xy"][1] for row in per_slot_rows if row["final_xy"] is not None]
    return {
        "per_slot": per_slot_rows,
        "arrival_rate": len(arrival_ticks) / len(slots) if slots else None,
        "arrived_count": len(arrival_ticks),
        "expected_count": len(slots),
        "ever_move_command_count": sum(1 for row in per_slot_rows if row["ever_move_command"]),
        "arrival_tick_median": statistics.median(arrival_ticks) if arrival_ticks else None,
        "arrival_tick_max": max(arrival_ticks) if arrival_ticks else None,
        "stagnating_slot_count": sum(1 for row in per_slot_rows if row["stagnation_runs"]),
        "path_ratio_median": statistics.median(path_ratios) if path_ratios else None,
        "path_ratio_max": max(path_ratios) if path_ratios else None,
        "final_position_variance": {
            "x": round(statistics.pvariance(final_xs), 3) if len(final_xs) > 1 else 0.0,
            "y": round(statistics.pvariance(final_ys), 3) if len(final_ys) > 1 else 0.0,
        },
    }


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, *, scenario: str = "auto",
    variant: str = "original", trace_timeout_s: float = TRACE_TIMEOUT_S,
) -> dict[str, Any]:
    if variant not in {"original", "candidate", "candidate_v2"}:
        raise ProbeError(f"unknown variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_sha: str | None = None
    candidate_bytes: bytes | None = None
    if variant == "candidate":
        from patches.pathing.g4_move_retry_budget_v1 import (
            digest as g4_digest,
            patched_bytes as g4_patched_bytes,
        )

        candidate_bytes = g4_patched_bytes(source_exe.read_bytes())
        candidate_sha = g4_digest(candidate_bytes)
    elif variant == "candidate_v2":
        from patches.pathing.g4_search_margin_budget_v2 import (
            digest as g4_digest,
            patched_bytes as g4_patched_bytes,
        )

        candidate_bytes = g4_patched_bytes(source_exe.read_bytes())
        candidate_sha = g4_digest(candidate_bytes)

    bridge_dir = artifact_root / "stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
    )
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge, timeout=60)
    manifest_output = manifest.get("output")
    manifest_game = manifest.get("game")
    manifest_wine = manifest.get("wine")
    if not isinstance(manifest_output, Mapping) or not isinstance(manifest_game, Mapping) or not isinstance(manifest_wine, Mapping):
        raise ProbeError("runtime manifest sections are malformed")
    run_dir_text = str(manifest_output.get("run_dir"))
    game_root_text = str(manifest_game.get("root"))
    prefix_root_text = str(manifest_wine.get("prefix"))
    manifest_path = Path(run_dir_text) / "manifest.json"
    original_check = runtime_env.check_runtime(manifest_path)
    game = Path(game_root_text)
    prefix = Path(prefix_root_text)
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private original copy failed pre-install check")

    if variant in {"candidate", "candidate_v2"}:
        assert candidate_bytes is not None and candidate_sha is not None
        private_exe.write_bytes(candidate_bytes)
        if sha256(private_exe) != candidate_sha:
            raise ProbeError("private candidate copy failed post-install check")

    if scenario not in {"auto", "long_distance_pan", "obstacle_row"}:
        raise ProbeError(f"unknown scenario: {scenario}")
    result: dict[str, Any] = {
        "schema": "syw2plus.g4-path-baseline-probe.v1",
        "status": "UNKNOWN",
        "variant": variant,
        "scenario": scenario,
        "trace_timeout_s": trace_timeout_s,
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
            "private_exe_sha256": sha256(private_exe),
            "candidate_sha256": candidate_sha,
            "original_manifest_check": original_check,
            "bridge_sha256": sha256(bridge),
        },
        "inputs": [],
        "captures": [],
    }
    log_path = artifact_root / "probe.log"
    log = log_path.open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    display = ""
    pid: int | None = None
    try:
        env = dict(
            os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
            LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
            SYW2_SUPPLY_PROBE="1",
        )
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,1600x1200"],
            cwd=game, env=env, stdout=log, stderr=log,
        ))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def state() -> dict[str, Any]:
            assert pid is not None
            return read_state(pid)

        def wait_for(predicate, label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = state()
                    if predicate(last):
                        return last
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda item: item.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window was not found")
        content_info = runtime_env._xwininfo_details(display, content, 10)
        crop = (int(content_info["x"]), int(content_info["y"]))

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "drag_to": list(drag_to) if drag_to else None, "button": button})

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda item: item.get("ps") == 7, "ps7")

        def read_selector() -> dict[str, Any]:
            assert pid is not None
            return runtime_env._read_lobby_selector(lambda address, size: read_memory(pid, address, size))

        if read_selector().get("selected") == "solo":
            click(344, 169)
            time.sleep(0.5)
        click(462, 169)
        deadline = time.monotonic() + 10
        while read_selector().get("selected") != "solo" and time.monotonic() < deadline:
            time.sleep(0.2)
        if read_selector().get("selected") != "solo":
            raise ProbeError("solo selector did not settle")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 5, "ps5")
        ready_deadline = time.monotonic() + 12
        ready: dict[str, Any] = {}
        while time.monotonic() < ready_deadline:
            ready = runtime_env._read_local_ready_state(lambda address, size: read_memory(pid, address, size))
            if ready.get("ready_value") == 1:
                break
            time.sleep(0.2)
        if ready.get("ready_value") != 1:
            raise ProbeError(f"local lobby did not become ready: {ready}")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        result["worker"] = worker
        result["terrain_note"] = (
            "unseeded solo lobby: worker absolute map position differs run to run; "
            "fixed-seed two-player chain not used (no fixture-seeding hook, see module docstring)"
        )
        worker_x, worker_y = int(worker["x"]), int(worker["y"])
        supply = SupplyProbe(prefix)

        click(*MINIMAP_CLICK)
        time.sleep(1)
        result["captures"].append(capture(display, artifact_root / "after-minimap.png", log))

        # --- Self-calibration: fit world = M @ screen + c from this run's
        # own camera, using the single pre-fixture worker as the only
        # selectable unit (same technique as g5_worker_relative_move_attack_probe).
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        calibration_selection = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["calibration_selection"] = calibration_selection
        if VISIBLE_WORKER_SLOT not in calibration_selection["slots"]:
            raise ProbeError(f"worker slot not selected for calibration: {calibration_selection}")

        def sample_calibration(label: str) -> dict[str, Any]:
            """9-point screen->world affine sample reusing the worker-only
            selection above. This must only run before the real 20-unit test
            group is selected (see scenario branches below) -- right-clicking
            issues a move order for whatever is *currently* selected, so
            calling this again after the real selection exists would send
            stray orders to the units under test."""
            samples: list[tuple[tuple[int, int], tuple[int, int]]] = []
            points: list[dict[str, Any]] = []
            for point in CALIBRATION_SCREEN_POINTS:
                click(*point, button=3)
                time.sleep(0.4)
                base = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE
                raw = int.from_bytes(read_memory(pid, base + UNIT_PENDING_XY_OFFSET, 4), "little", signed=False)
                world = decode_xy(raw)
                samples.append((point, world))
                points.append({"screen": list(point), "world": list(world)})
            matrix, offset = fit_affine(samples)
            residuals = [
                float(np.max(np.abs(matrix @ np.array(point) + offset - np.array(world))))
                for point, world in samples
            ]
            return {
                "label": label, "points": points, "matrix": matrix, "offset": offset,
                "max_abs_residual": max(residuals) if residuals else None,
            }

        initial_cal = sample_calibration("initial")
        result["calibration"] = {
            "points": initial_cal["points"],
            "matrix": initial_cal["matrix"].tolist(),
            "offset": initial_cal["offset"].tolist(),
            "max_abs_residual": initial_cal["max_abs_residual"],
        }
        matrix_inv = np.linalg.inv(initial_cal["matrix"])
        offset = initial_cal["offset"]

        def world_to_screen(world: tuple[int, int]) -> tuple[int, int]:
            point = matrix_inv @ (np.array(world) - offset)
            return int(round(point[0])), int(round(point[1]))

        def pan_camera(key: str, hold_ms: int) -> None:
            subprocess.run(
                [sys.executable, str(REPO / "tools/x11_send_keys.py"), "--display", display,
                 key, "--hold-ms", str(hold_ms)],
                env=env, stdout=log, stderr=log, timeout=hold_ms / 1000 + 10, check=True,
            )

        # lap707: determine (and, for long_distance_pan, pre-compute) the
        # scenario's destination now, while only the worker is selected --
        # camera panning issues no click/order, but ``sample_calibration``
        # does, so it must stay confined to this worker-only window.
        screen_center = (
            (CALIBRATION_SCREEN_POINTS[0][0] + CALIBRATION_SCREEN_POINTS[-1][0]) // 2,
            (CALIBRATION_SCREEN_POINTS[0][1] + CALIBRATION_SCREEN_POINTS[-1][1]) // 2,
        )
        pan_replay: dict[str, Any] | None = None
        if scenario == "long_distance_pan":
            attempts: list[dict[str, Any]] = []
            for key in ("Down", "Up"):
                cumulative_ms = 0
                for _ in range(CAMERA_PAN_MAX_ATTEMPTS_PER_DIRECTION):
                    pan_camera(key, CAMERA_PAN_KEY_HOLD_MS)
                    cumulative_ms += CAMERA_PAN_KEY_HOLD_MS
                    cal = sample_calibration(f"pan-{key}-{cumulative_ms}ms")
                    center_world = _screen_to_world(screen_center, cal["matrix"], cal["offset"])
                    ok, dist = pan_candidate_ok(center_world, (worker_x, worker_y), CAMERA_PAN_TARGET_DISTANCE_TILES)
                    attempts.append({
                        "key": key, "cumulative_hold_ms": cumulative_ms,
                        "center_world": list(center_world), "distance_tiles": round(dist, 3),
                        "accepted": ok, "max_abs_residual": cal["max_abs_residual"],
                    })
                    if ok:
                        pan_replay = {
                            "key": key, "cumulative_hold_ms": cumulative_ms,
                            "center_world": center_world, "distance_tiles": dist,
                        }
                        break
                    if not (0 <= center_world[0] < 180 and 0 <= center_world[1] < 180):
                        break  # ran off the map edge this direction; try the other one
                if pan_replay is not None:
                    break
            result["camera_pan"] = {"attempts": attempts, "accepted": pan_replay is not None}
            if pan_replay is not None:
                # Pan back to the original camera position so the upcoming
                # real 20-unit selection drag (fixed screen coords) still
                # lands on the fixture instead of empty panned-to ground.
                # A same-duration reverse hold is not reliably symmetric (an
                # early run observed the reverse hold landing on unexplored
                # fog-of-war instead of the worker's start view -- see
                # lap707 history entry), so close the loop: verify the
                # return with the same worker-only calibration sample used
                # for panning, and nudge further if it is still off by more
                # than CAMERA_RETURN_TOLERANCE_TILES.
                reverse_key = "Up" if pan_replay["key"] == "Down" else "Down"
                forward_key = pan_replay["key"]
                forward_delta = np.array(pan_replay["center_world"]) - np.array((worker_x, worker_y))
                forward_unit = forward_delta / np.linalg.norm(forward_delta)
                pan_rate_tiles_per_ms = pan_replay["distance_tiles"] / pan_replay["cumulative_hold_ms"]
                pan_camera(reverse_key, pan_replay["cumulative_hold_ms"])
                time.sleep(0.3)
                return_attempts: list[dict[str, Any]] = []
                for _ in range(CAMERA_RETURN_MAX_CORRECTIONS):
                    verify_cal = sample_calibration("return-verify")
                    verify_world = np.array(_screen_to_world(screen_center, verify_cal["matrix"], verify_cal["offset"]))
                    residual = verify_world - np.array((worker_x, worker_y))
                    signed_along_forward = float(np.dot(residual, forward_unit))
                    drift = float(np.linalg.norm(residual))
                    return_attempts.append({
                        "center_world": verify_world.tolist(), "drift_tiles": round(drift, 3),
                        "signed_along_forward_tiles": round(signed_along_forward, 3),
                    })
                    if drift <= CAMERA_RETURN_TOLERANCE_TILES:
                        break
                    correction_key = reverse_key if signed_along_forward > 0 else forward_key
                    correction_ms = int(min(CAMERA_PAN_KEY_HOLD_MS, max(150, abs(signed_along_forward) / pan_rate_tiles_per_ms)))
                    pan_camera(correction_key, correction_ms)
                    time.sleep(0.3)
                result["camera_return"] = return_attempts

        fixture_requests = dense_fixture_requests(worker)
        result["fixture"] = {"owner": 0, "type": SEED_TYPE, "requests": fixture_requests}
        receipts: list[dict[str, Any]] = []
        for request in fixture_requests:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=request["x"], y=request["y"], count=request["count"])
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"dense fixture batch failed: {receipt}")
        time.sleep(1)
        result["captures"].append(capture(display, artifact_root / "after-fixture.png", log))

        safe_box = safe_screen_box(int(content_info["width"]), int(content_info["height"]))
        result["safe_screen_box"] = {
            "box": list(safe_box),
            "window_width": int(content_info["width"]),
            "window_height": int(content_info["height"]),
        }
        chosen_destination: dict[str, Any] | None = None
        destination_candidates: list[dict[str, Any]] = []
        if scenario == "long_distance_pan":
            if pan_replay is None:
                raise ProbeError(f"camera pan could not reach >= {CAMERA_PAN_TARGET_DISTANCE_TILES} tiles: {result.get('camera_pan')}")
            destination_world = (int(round(pan_replay["center_world"][0])), int(round(pan_replay["center_world"][1])))
            destination_screen = screen_center
            chosen_destination = {
                "offset": None, "world": list(destination_world), "screen": list(destination_screen),
                "distance_tiles": pan_replay["distance_tiles"], "safe_box_margin": None, "usable": True,
                "reason": "camera_pan_long_distance",
                "camera_pan_key": pan_replay["key"], "camera_pan_hold_ms": pan_replay["cumulative_hold_ms"],
            }
            result["destination_candidates"] = [chosen_destination]
        elif scenario == "obstacle_row":
            # -1 (worker_y - magnitude) first: the base footprint sits on the
            # worker's -Y side (see OBSTACLE_ROW_OFFSET_MAGNITUDE above); +1 is
            # a map-edge fallback only, and would not be expected to cross it.
            for magnitude in (OBSTACLE_ROW_OFFSET_MAGNITUDE, OBSTACLE_ROW_OFFSET_MAGNITUDE - 1, OBSTACLE_ROW_OFFSET_MAGNITUDE - 2):
                for sign in (-1, 1):
                    dy = sign * magnitude
                    dest_world = (worker_x, worker_y + dy)
                    if not all(0 <= value < 180 for value in dest_world):
                        destination_candidates.append({
                            "offset": [0, dy], "world": list(dest_world), "distance_tiles": abs(dy),
                            "usable": False, "reason": "outside 180x180 map",
                        })
                        continue
                    dest_screen = world_to_screen(dest_world)
                    margin = _safe_box_margin(dest_screen, safe_box)
                    usable = margin >= 0
                    row = {
                        "offset": [0, dy], "world": list(dest_world), "screen": list(dest_screen),
                        "distance_tiles": abs(dy), "safe_box_margin": margin, "usable": usable,
                        "reason": ("obstacle_row (base-footprint side)" if sign < 0 else "obstacle_row (map-edge fallback side)") if usable else "outside measured safe screen box",
                    }
                    destination_candidates.append(row)
                    if usable and chosen_destination is None:
                        chosen_destination = row
                if chosen_destination is not None:
                    break
            result["destination_candidates"] = destination_candidates
            if chosen_destination is None:
                raise ProbeError(f"no obstacle-row destination candidate is usable: {destination_candidates}")
            obstacle_world_list = [int(v) for v in chosen_destination["world"]]
            obstacle_screen_list = [int(v) for v in chosen_destination["screen"]]
            destination_world = (obstacle_world_list[0], obstacle_world_list[1])
            destination_screen = (obstacle_screen_list[0], obstacle_screen_list[1])
        else:
            usable_rows: list[dict[str, Any]] = []
            # lap682's own proven MOVE destinations are dy=+6/dy=-4 (dx=0); escalate
            # magnitude along that same axis/direction pair, largest first, so the
            # chosen destination is the longest one that still measures inside the
            # real window -- "long distance" relative to lap682, not a guessed
            # off-screen extrapolation (lap704 run1's failure mode).
            for magnitude in LONG_DISTANCE_OFFSET_MAGNITUDES:
                for dy in (magnitude, -magnitude):
                    dx = 0
                    dest_world = (worker_x + dx, worker_y + dy)
                    distance = math.hypot(dx, dy)
                    if not all(0 <= value < 180 for value in dest_world):
                        destination_candidates.append({
                            "offset": [dx, dy], "world": list(dest_world), "distance_tiles": distance,
                            "usable": False, "reason": "outside 180x180 map",
                        })
                        continue
                    dest_screen = world_to_screen(dest_world)
                    margin = _safe_box_margin(dest_screen, safe_box)
                    usable = margin >= 0
                    row = {
                        "offset": [dx, dy], "world": list(dest_world), "screen": list(dest_screen),
                        "distance_tiles": distance, "safe_box_margin": margin, "usable": usable,
                        "reason": None if usable else "outside measured safe screen box",
                    }
                    destination_candidates.append(row)
                    if usable:
                        usable_rows.append(row)
            result["destination_candidates"] = destination_candidates
            # Prefer the largest usable distance, breaking ties toward the larger
            # safe-box margin (furthest from clipping).
            chosen_destination = max(
                usable_rows, key=lambda row: (row["distance_tiles"], row["safe_box_margin"]), default=None,
            )
            if chosen_destination is None:
                raise ProbeError(f"no worker-relative long-distance destination candidate is usable: {destination_candidates}")
            destination_world_list = [int(v) for v in chosen_destination["world"]]
            destination_screen_list = [int(v) for v in chosen_destination["screen"]]
            destination_world = (destination_world_list[0], destination_world_list[1])
            destination_screen = (destination_screen_list[0], destination_screen_list[1])
        result["destination"] = chosen_destination

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        after = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["selection_after"] = after
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))
        if after["count"] != STOCK_SELECTION_CAPACITY or after["unique_slots"] != STOCK_SELECTION_CAPACITY:
            raise ProbeError(f"drag did not select the original 20-unit cap: {after}")
        slots = after["slots"]
        start_positions = {
            slot: (row["x"], row["y"])
            for slot, row in ((s, read_unit_trace_row(pid, s)) for s in slots)
        }

        if scenario == "long_distance_pan" and pan_replay is not None:
            # Replay the exact same hold used during the worker-only pan
            # planning phase, now that the real 20-unit group is selected and
            # its start positions are recorded -- no calibration right-clicks
            # happen in between, so this selection is never touched before
            # the one real move-order click below.
            pan_camera(pan_replay["key"], pan_replay["cumulative_hold_ms"])
            time.sleep(0.3)

        click(*destination_screen, button=3)
        click_tick = int(state().get("tick", 0))
        result["move_click"] = {"screen": list(destination_screen), "world": list(destination_world), "click_tick": click_tick}
        trace = trace_movement(
            pid, slots, destination_world, timeout=trace_timeout_s, interval=TRACE_POLL_INTERVAL_S,
        )
        result["captures"].append(capture(display, artifact_root / "after-move-click.png", log))
        metrics = compute_metrics(trace, slots, destination_world, start_positions)

        result["before_selected_count"] = len(slots)
        result["expected_count"] = STOCK_SELECTION_CAPACITY
        result["trace_sample_count"] = len(trace["samples"])
        result["trace_converged"] = trace["converged"]
        result["trace_timed_out"] = trace["timed_out"]
        # Raw per-tick (tick, x, y, command, hp) rows per slot, as STATUS's
        # "다음 한 가지" requires -- kept in full so a reviewer can audit the
        # arrival/stagnation/path-ratio metrics against the underlying trace.
        result["trace"] = trace
        result["metrics"] = metrics
        result["move_command_reached_all_selected"] = after["count"] == STOCK_SELECTION_CAPACITY
        result["status"] = "PATH_TRACE_COMPLETE"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError) as exc:
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
        cleanup_error: str | None = None
        cur_env = locals().get("env", os.environ)
        try:
            subprocess.run(["wineserver", "-k"], env=cur_env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=cur_env, stdout=log, stderr=log, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            cleanup_error = f"{type(exc).__name__}: {exc}"
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
                xvfb.wait(timeout=5)
        result["cleanup"] = {
            "error": cleanup_error,
            "owned_children_stopped": all(child.poll() is not None for child in children),
            "xvfb_stopped": xvfb is None or xvfb.poll() is not None,
            "prefix_processes_after": runtime_env._prefix_pids(prefix),
        }
        result["cleanup"]["ok"] = not result["cleanup"]["prefix_processes_after"] and cleanup_error is None
        result["source_sha_after"] = sha256(source_exe)
        result["source_unchanged"] = result["source_sha_after"] == ORIGINAL_SHA
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument(
        "--scenario", choices=("auto", "long_distance_pan", "obstacle_row"), default="auto",
        help="auto=lap704-706 single-axis <=12-tile default; long_distance_pan=lap707 camera-pan "
             ">=20-tile destination; obstacle_row=lap707 base-footprint-side destination",
    )
    parser.add_argument(
        "--variant", choices=("original", "candidate", "candidate_v2"), default="original",
        help="candidate=lap708 patches.pathing.g4_move_retry_budget_v1 (move-order local-step "
             "detour retry budget 4->8); candidate_v2=lap709 "
             "patches.pathing.g4_search_margin_budget_v2 (FUN_0041AF90 pathfinder bounding-box "
             "margin 30->60 tiles) swapped into the private copy after prepare()",
    )
    parser.add_argument(
        "--trace-timeout-s", type=float, default=TRACE_TIMEOUT_S,
        help="lap710 v3 hypothesis: override the movement-trace timeout (default "
             f"{TRACE_TIMEOUT_S}s) to test whether long_distance_pan non-arrivals are a probe "
             "timeout artifact rather than a pathing/AI defect",
    )
    args = parser.parse_args(argv)
    result = run_probe(
        args.source, args.runtime_root, args.artifact_root,
        scenario=args.scenario, variant=args.variant, trace_timeout_s=args.trace_timeout_s,
    )
    print(json.dumps({k: v for k, v in result.items() if k not in {"metrics", "trace"}}, ensure_ascii=False, indent=2))
    if "metrics" in result:
        print(json.dumps({"metrics": result["metrics"]}, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "PATH_TRACE_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
