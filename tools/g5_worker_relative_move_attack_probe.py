#!/usr/bin/env python3
"""Paired original20/candidate50 MOVE+ATTACK convergence with a self-calibrated
worker-relative destination (lap682).

lap681 found that the original ``tools/g5_move_attack_convergence_probe.py``
destination -- a single hardcoded screen pixel ``(300, 420)`` -- is not
map-independent: the G5 dense-fixture flow enters a plain, unseeded "solo"
lobby, so the worker's spawn position and surrounding terrain differ every
run.  Two of three attempted paired runs landed that fixed pixel on invalid
ground and got a complete 0/50 non-response for both MOVE and ATTACK.

Rather than port the G4/G2 fixed-seed custom-game creation chain (a two-player
flow with its own player-count/AI assumptions that the G5 dense-fixture flow
has never used), this probe reuses the technique
``tools/g5_screen_world_calibration.py`` already validated for the same
problem: fit the screen->world affine map ``world = M @ screen + c`` in-run
from a handful of small right-click samples on the single pre-fixture worker,
then invert it to compute the screen point for a *worker-relative* world
tile.  That tile is chosen just outside the dense-fixture grid footprint
(``dense_fixture_requests`` covers dx in -3..3, dy in -3..4), so it is
adjacent to ground already proven open by 55 successful fixture spawns,
without needing a new terrain/walkability memory reader.  If the primary
offset still produces zero convergence (e.g. blocked by scenery), the probe
retries once with the opposite-side offset before giving up -- the explicit
"invalid destination -> adjacent tile retry" contract from lap681's next
step.

Read-only: touches no product EXE bytes beyond the already-approved G5
selection-cap50 v3 candidate build; the "original" variant runs the
protected source executable unmodified (verified by SHA both before and
after).
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, cast

import numpy as np

from patches.selection import g5_selection_cap50_v3 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError,
    SupplyProbe,
    DRAG_START,
    DRAG_END,
    STOCK_SELECTION_BASE,
    STOCK_SELECTION_CAPACITY,
    SEED_TYPE,
    SEED_COUNT,
    VISIBLE_WORKER_SLOT,
    UNIT_BASE,
    UNIT_STRIDE,
    UNIT_COMMAND_OFFSET,
    UNIT_PENDING_COMMAND_OFFSET,
    UNIT_PENDING_XY_OFFSET,
    UNIT_PENDING_TARGET_UID_OFFSET,
    selection_snapshot,
    unit_snapshot,
    dense_fixture_requests,
    sha256,
    write_json,
    capture,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import ATTACK_BUTTON, MINIMAP_CLICK
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
TARGET_SHA = "e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977"
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap682-worker-relative-convergence"
# lap688: raw comparison of the two identical lap687 skip=H1 dense-50 runs
# (0/49 vs 18/49 ever_command4_count from the exact same candidate/input)
# found the attack-destination *screen* point stayed nearly fixed (121,383 vs
# 121,384 -- ruling out the calibration/destination-transform as the wobble
# source) while the *absolute world* position swung from y=27 to y=169 out of
# a 0..180 map -- the unseeded solo lobby spawns the worker (and therefore
# every worker-relative offset) at a different absolute map location each
# run. This first looked like spawn-position-dependent pathfinding/congestion
# timing, but lap688's later raw N=5 comparison (see the attack-target-spawn
# comment below) falsified that: the real cause was the attack target being
# auto-aggro'd to death by nearby friendlies before the explicit click ever
# fired, a race that spawn timing (not congestion) controlled. These wider
# poll/sample windows are kept only as a defensive buffer against slow ticks,
# not because congestion timing was confirmed.
POLL_INTERVAL = 0.5
POLL_TIMEOUT = 30.0
RETRY_POLL_TIMEOUT = 20.0
# Calibration grid: same nine screen points g5_screen_world_calibration.py
# already validated for a single-unit affine fit under this game's camera.
CALIBRATION_SCREEN_POINTS = [
    (250, 200), (475, 200), (700, 200),
    (250, 320), (475, 320), (700, 320),
    (250, 440), (475, 440), (700, 440),
]
# One tile beyond the dense fixture grid's dy edges (grid covers dy -3..4,
# dx -3..3), so both candidates sit next to ground already proven open by
# the 55 fixture spawns without needing a terrain reader.
PRIMARY_DEST_OFFSET = (0, 6)
FALLBACK_DEST_OFFSET = (0, -4)
# lap683 middle flagged that lap682's attack click reused the exact tile MOVE
# had just walked to, which cannot show a broadcast-scope difference between
# move and attack. These stay on the same lap682-proven-open dy=6 row but
# shift sideways so the attack destination is never the tile MOVE used.
ATTACK_PRIMARY_DEST_OFFSET = (3, 6)
ATTACK_FALLBACK_DEST_OFFSET = (-3, 6)
SAFE_SCREEN_BOX = (0, 1580, 0, 460)
# 2026-09-26 16:35 operator direction: the live +0x290 command==4 state never
# appears for a UI attack click even in the original (lap684 run1/run2), so
# the judgment field is wrong, not the input. lap678's writer trace pinned
# the exact pending word an attack click writes to +0x384; move writes
# 0x1000003 and idle reads back 0x1000001/0x10001, so this value is unique
# to an attack order actually being queued.
ATTACK_PENDING_WORD = 0x1000004
# lap688: widened from 3.0s alongside POLL_TIMEOUT above as a defensive
# buffer against slow ticks; the actual attack-probe wobble cause turned out
# to be the auto-aggro spawn-timing race fixed below, not congestion timing.
ATTACK_SAMPLE_WINDOW_S = 12.0
ATTACK_SAMPLE_INTERVAL_S = 0.1


def read_unit_full(pid: int, slot: int) -> dict[str, Any]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "command": int.from_bytes(read_memory(pid, base + UNIT_COMMAND_OFFSET, 2), "little", signed=True),
        "pending_command": int.from_bytes(
            read_memory(pid, base + UNIT_PENDING_COMMAND_OFFSET, 4), "little", signed=False,
        ),
        "pending_xy": int.from_bytes(
            read_memory(pid, base + UNIT_PENDING_XY_OFFSET, 4), "little", signed=False,
        ),
        "pending_target_uid": int.from_bytes(
            read_memory(pid, base + UNIT_PENDING_TARGET_UID_OFFSET, 4), "little", signed=False,
        ),
    }


def poll_convergence(
    pid: int, slots: list[int], *, predicate, expected_count: int, timeout: float, interval: float,
    fast_window: float = 3.0, fast_interval: float = 0.15,
) -> dict[str, Any]:
    """Poll until every selected slot has been *observed* matching at least
    once, not until all of them match *simultaneously*.

    lap682's first candidate50 run found that a nearby worker-relative
    destination lets the fastest units finish (and drop out of the
    transient ``command==3``/``==4`` state) before the slowest ones even
    start, so an instantaneous "matched right now" snapshot never reaches
    ``expected_count`` even though the broadcast itself reached every unit.
    Tracking the running union of ever-matched slots answers the actual
    question (did the order reach all selected units) instead of demanding
    an instant that may not exist.  Polling starts fast (``fast_interval``
    for ``fast_window`` seconds) so short-lived matches on nearby units are
    not missed between samples.
    """
    curve: list[dict[str, Any]] = []
    deadline = time.monotonic() + timeout
    start = time.monotonic()
    final_rows: list[dict[str, Any]] = []
    ever_matched: set[int] = set()
    converged_at: float | None = None
    while True:
        rows = [read_unit_full(pid, slot) for slot in slots if 0 < slot < 1200]
        for row in rows:
            if predicate(row):
                ever_matched.add(int(row["slot"]))
        matched = sum(1 for row in rows if predicate(row))
        elapsed = time.monotonic() - start
        curve.append({"elapsed_s": round(elapsed, 2), "matched_count": matched, "ever_matched_count": len(ever_matched)})
        final_rows = rows
        if len(ever_matched) >= expected_count:
            converged_at = elapsed
            break
        if time.monotonic() >= deadline:
            break
        time.sleep(fast_interval if elapsed < fast_window else interval)
    return {
        "curve": curve,
        "final_matched_count": sum(1 for row in final_rows if predicate(row)),
        "ever_matched_count": len(ever_matched),
        "converged": converged_at is not None,
        "converged_at_s": converged_at,
        "final_rows": final_rows,
    }


def _in_safe_box(point: tuple[float, float]) -> bool:
    x0, x1, y0, y1 = SAFE_SCREEN_BOX
    return x0 <= point[0] <= x1 and y0 <= point[1] <= y1


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    source_exe = source / runtime_env.ORIGINAL_EXE
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_path = artifact_root / "g5_selection_cap50.exe"
    candidate_sha: str | None = None
    if variant == "candidate":
        candidate_path.write_bytes(g5.build_candidate(source_exe.read_bytes())[0])
        candidate_sha = sha256(candidate_path)
        if candidate_sha != TARGET_SHA:
            raise ProbeError(f"G5 candidate SHA mismatch: {candidate_sha}")

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
    run_dir_text = cast(str, manifest_output.get("run_dir"))
    game_root_text = cast(str, manifest_game.get("root"))
    prefix_root_text = cast(str, manifest_wine.get("prefix"))
    manifest_path = Path(run_dir_text) / "manifest.json"
    original_check = runtime_env.check_runtime(manifest_path)
    game = Path(game_root_text)
    prefix = Path(prefix_root_text)
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private original copy failed pre-install check")

    if variant == "candidate":
        private_exe.write_bytes(candidate_path.read_bytes())
        if sha256(private_exe) != TARGET_SHA:
            raise ProbeError("private candidate SHA verification failed")
    selection_base = g5.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    selection_capacity = g5.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY
    expected_count = selection_capacity

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-worker-relative-move-attack-probe.v1",
        "status": "UNKNOWN",
        "variant": variant,
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
            "candidate_sha256": candidate_sha,
            "private_exe_sha256": sha256(private_exe),
            "original_manifest_check": original_check,
            "bridge_sha256": sha256(bridge),
        },
        "inputs": [],
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
        supply = SupplyProbe(prefix)

        click(*MINIMAP_CLICK)
        time.sleep(1)
        result["captures"] = [capture(display, artifact_root / "after-minimap.png", log)]

        # --- Self-calibration: fit world = M @ screen + c from this run's own
        # camera, using the single pre-fixture worker as the only selectable
        # unit.  Done *after* the minimap click so the fit matches the final
        # camera the rest of the run uses.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        calibration_selection = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["calibration_selection"] = calibration_selection
        if VISIBLE_WORKER_SLOT not in calibration_selection["slots"]:
            raise ProbeError(f"worker slot not selected for calibration: {calibration_selection}")
        samples: list[tuple[tuple[int, int], tuple[int, int]]] = []
        calibration_points: list[dict[str, Any]] = []
        for point in CALIBRATION_SCREEN_POINTS:
            click(*point, button=3)
            time.sleep(0.4)
            base = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE
            raw = int.from_bytes(read_memory(pid, base + UNIT_PENDING_XY_OFFSET, 4), "little", signed=False)
            world = decode_xy(raw)
            samples.append((point, world))
            calibration_points.append({"screen": list(point), "world": list(world)})
        matrix, offset = fit_affine(samples)
        residuals = [
            float(np.max(np.abs(matrix @ np.array(point) + offset - np.array(world))))
            for point, world in samples
        ]
        result["calibration"] = {
            "points": calibration_points,
            "matrix": matrix.tolist(),
            "offset": offset.tolist(),
            "max_abs_residual": max(residuals) if residuals else None,
        }
        matrix_inv = np.linalg.inv(matrix)

        def world_to_screen(world: tuple[int, int]) -> tuple[int, int]:
            point = matrix_inv @ (np.array(world) - offset)
            return int(round(point[0])), int(round(point[1]))

        fixture_requests = dense_fixture_requests(worker)
        result["fixture"] = {"owner": 0, "type": SEED_TYPE, "count": SEED_COUNT, "requests": fixture_requests}
        receipts: list[dict[str, Any]] = []
        for request in fixture_requests:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=request["x"], y=request["y"], count=request["count"])
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"dense fixture batch failed: {receipt}")
        if sum(int(receipt.get("fixture_added", 0)) for receipt in receipts) != SEED_COUNT:
            raise ProbeError(f"dense fixture total failed: {receipts}")
        time.sleep(1)
        result["captures"].append(capture(display, artifact_root / "after-fixture.png", log))

        def compute_destinations(offsets: list[tuple[int, int]]) -> list[dict[str, Any]]:
            rows: list[dict[str, Any]] = []
            for dx, dy in offsets:
                dest_world = (worker_x + dx, worker_y + dy)
                if not all(0 <= value < 180 for value in dest_world):
                    rows.append({"offset": [dx, dy], "world": list(dest_world), "usable": False, "reason": "outside 180x180 map"})
                    continue
                dest_screen = world_to_screen(dest_world)
                usable = _in_safe_box(dest_screen)
                rows.append({
                    "offset": [dx, dy], "world": list(dest_world), "screen": list(dest_screen),
                    "usable": usable, "reason": None if usable else "outside safe screen box",
                })
            return rows

        worker_x, worker_y = int(worker["x"]), int(worker["y"])
        destinations = compute_destinations([PRIMARY_DEST_OFFSET, FALLBACK_DEST_OFFSET])
        result["destination_candidates"] = destinations
        usable_destinations = [d for d in destinations if d.get("usable")]
        if not usable_destinations:
            raise ProbeError(f"no worker-relative destination candidate is on-screen: {destinations}")
        primary_destination = usable_destinations[0]
        retry_destination = usable_destinations[1] if len(usable_destinations) > 1 else None

        # The attack destination must never equal the move destination (see
        # ATTACK_PRIMARY_DEST_OFFSET comment above), so it gets its own
        # worker-relative candidate list and retry pair.
        attack_destinations = compute_destinations([ATTACK_PRIMARY_DEST_OFFSET, ATTACK_FALLBACK_DEST_OFFSET])
        result["attack_destination_candidates"] = attack_destinations
        usable_attack_destinations = [d for d in attack_destinations if d.get("usable")]
        if not usable_attack_destinations:
            raise ProbeError(f"no worker-relative attack destination candidate is on-screen: {attack_destinations}")
        attack_primary_destination = usable_attack_destinations[0]
        attack_retry_destination = usable_attack_destinations[1] if len(usable_attack_destinations) > 1 else None

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selection_after"] = after
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))
        if after["count"] != expected_count or after["unique_slots"] != expected_count:
            raise ProbeError(f"drag did not select the full fixture: {after}")
        slots = after["slots"]

        # --- Phase MOVE: poll for command==3 convergence; retry once at the
        # opposite-side worker-relative tile if the primary destination
        # produces zero movement (still-invalid ground).
        move_screen = tuple(primary_destination["screen"])
        click(*move_screen, button=3)
        move_result = poll_convergence(
            pid, slots, predicate=lambda row: row["command"] == 3,
            expected_count=expected_count, timeout=POLL_TIMEOUT, interval=POLL_INTERVAL,
        )
        result["captures"].append(capture(display, artifact_root / "after-move-click.png", log))
        move_result["destination"] = primary_destination
        if move_result["ever_matched_count"] == 0 and retry_destination is not None:
            retry_screen = tuple(retry_destination["screen"])
            click(*retry_screen, button=3)
            retry_move_result = poll_convergence(
                pid, slots, predicate=lambda row: row["command"] == 3,
                expected_count=expected_count, timeout=RETRY_POLL_TIMEOUT, interval=POLL_INTERVAL,
            )
            retry_move_result["destination"] = retry_destination
            result["move_convergence_primary"] = move_result
            result["move_convergence_retry"] = retry_move_result
            move_result = retry_move_result
        result["captures"].append(capture(display, artifact_root / "after-move-retry.png", log))

        # lap688: raw comparison of 5 fresh original-20 runs found the exact
        # same "0/attack_capable" total miss (raw_command_histogram all-3,
        # observed_target_uids empty) recurring even for the *original* exe
        # (2 of 5 runs), while the passing runs converged the MOVE phase just
        # as fast (<0.5s) -- ruling out congestion/timing-budget as this
        # failure mode's cause. What differs is that the target used to sit
        # exactly next to the dense friendly fixture from before the drag
        # select through the whole (now up to 30s) MOVE poll, i.e. lap672's
        # already-flagged auto-aggro confound: a lone owner-1 unit parked a
        # couple of tiles from 19-50 armed owner-0 units for many seconds is
        # frequently auto-engaged and killed by nearby idle units *before*
        # the explicit attack click ever fires, leaving nobody left to issue
        # the order against. Spawning the target immediately before the
        # attack click (instead of before the drag/MOVE phase) cuts that
        # exposure window from several seconds to a fraction of one.
        attack_target_world = tuple(int(v) for v in attack_primary_destination["world"])
        target_receipt = supply.call(
            op=5, owner=1, unit_type=SEED_TYPE,
            x=attack_target_world[0], y=attack_target_world[1], count=1,
        )
        if not target_receipt.get("ok") or target_receipt.get("fixture_added") != 1:
            raise ProbeError(f"attack target fixture failed: {target_receipt}")
        attack_target_slot = int(target_receipt.get("producer", {}).get("slot", 0))
        if not 0 < attack_target_slot < 1200:
            raise ProbeError(f"attack target slot missing: {target_receipt}")
        attack_target_base = UNIT_BASE + attack_target_slot * UNIT_STRIDE
        attack_target_handle = int.from_bytes(read_memory(pid, attack_target_base + 0x29C, 4), "little")
        result["attack_target_fixture"] = {
            "owner": 1, "type": SEED_TYPE, "world": list(attack_target_world),
            "screen": attack_primary_destination["screen"],
            "slot": attack_target_slot, "handle": attack_target_handle,
        }

        # --- Phase ATTACK: sample the pending-command word for the exact
        # ATTACK_PENDING_WORD value over a fixed post-click window and take
        # the peak simultaneous count, per the 2026-09-26 16:35 operator
        # direction (the live +0x290 command==4 state never appeared for a
        # UI attack click even against the original -- see lap684's
        # run1/run2 -- so the judgment field, not the input, was wrong).
        # Uses its own worker-relative destination (never the tile MOVE just
        # walked to) and its own retry pair.
        attack_capable_slots = [slot for slot in slots if slot != VISIBLE_WORKER_SLOT]
        attack_expected_count = len(attack_capable_slots)

        def sample_attack_window(destination: Mapping[str, Any]) -> dict[str, Any]:
            screen = tuple(destination["screen"])
            click(*ATTACK_BUTTON, button=1)
            time.sleep(0.1)
            click(*screen, button=1)
            dest_world = tuple(int(v) for v in destination["world"])
            deadline = time.monotonic() + ATTACK_SAMPLE_WINDOW_S
            curve: list[dict[str, Any]] = []
            best_pending_count = 0
            best_rows: list[dict[str, Any]] = []
            ever_command4: set[int] = set()
            target_uids: set[int] = set()
            start = time.monotonic()
            while time.monotonic() < deadline:
                rows = [read_unit_full(pid, slot) for slot in attack_capable_slots if 0 < slot < 1200]
                pending_count = sum(1 for row in rows if row["pending_command"] == ATTACK_PENDING_WORD)
                for row in rows:
                    if row["command"] == 4:
                        ever_command4.add(int(row["slot"]))
                    if row["pending_target_uid"]:
                        target_uids.add(int(row["pending_target_uid"]))
                curve.append({"elapsed_s": round(time.monotonic() - start, 2), "pending_exact_count": pending_count})
                if pending_count >= best_pending_count:
                    best_pending_count = pending_count
                    best_rows = rows
                time.sleep(ATTACK_SAMPLE_INTERVAL_S)
            pending_xy_match_count = sum(
                1 for row in best_rows if decode_xy(row["pending_xy"]) == dest_world
            )
            return {
                "destination": destination,
                "curve": curve,
                "max_pending_exact_count": best_pending_count,
                "rows_at_max": best_rows,
                "ever_command4_count": len(ever_command4),
                "observed_target_uids": sorted(target_uids),
                "pending_xy_match_count": pending_xy_match_count,
            }

        attack_result = sample_attack_window(attack_primary_destination)
        if attack_result["max_pending_exact_count"] == 0 and attack_retry_destination is not None:
            retry_attack_result = sample_attack_window(attack_retry_destination)
            result["attack_sample_primary"] = attack_result
            result["attack_sample_retry"] = retry_attack_result
            attack_result = retry_attack_result
        result["captures"].append(capture(display, artifact_root / "after-attack-click.png", log))

        # Raw command-value distribution at the peak sample, per lap683's
        # "pending!=1 is not an attack judgment" finding -- record the actual
        # +0x290 command histogram alongside the exact-pending-word count so
        # a later reviewer can audit what "attack" was actually counted from.
        command_histogram: dict[str, int] = {}
        for row in attack_result["rows_at_max"]:
            key = str(row.get("command"))
            command_histogram[key] = command_histogram.get(key, 0) + 1
        attack_result["raw_command_histogram"] = command_histogram

        result["before_selected_count"] = len(slots)
        result["expected_count"] = expected_count
        result["attack_capable_count"] = attack_expected_count
        result["move_convergence"] = move_result
        result["attack_window"] = attack_result
        result["move_pass"] = move_result["ever_matched_count"] == expected_count
        result["attack_pass"] = attack_result["max_pending_exact_count"] == attack_expected_count
        result["status"] = "CONVERGENCE_COMPLETE"
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
