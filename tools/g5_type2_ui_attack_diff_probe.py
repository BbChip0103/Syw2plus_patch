#!/usr/bin/env python3
"""One original-only run: find the enemy sprite by screen diff, then attack-click it.

lap672 (six original-only runs) found that a screen->world affine fit from the
worker's own calibration moves carries both horizontal and vertical error when
applied to a *different* unit's position -- a 50-point 2D sweep around the
naively-computed target screen point still missed the enemy sprite's hitbox
every time. The 2026-09-26 09:25 operator decision drops the coordinate-math
approach entirely: instead of computing where the enemy sprite *should* be,
capture the screen immediately before and immediately after the enemy unit is
seeded, diff the two captures, and click the centroid of the pixels that
changed (that is, by construction, where the new sprite was drawn). A few
+/-8px retries around that centroid cover residual anti-aliasing/animation
noise without reintroducing a wide blind sweep.

A second, fully independent unit pair (spawned far from the camera, at the
opposite corner of the map) exercises the 2026-09-26 lap672 self-recorded
open question ((1) in its "next work" note): does the unmodified engine
order issuer (bridge op=8) accept an attack order when called immediately
after both fixtures exist, while the tick is still low, before any of this
probe's own UI actions have run? Keeping this pair spatially and temporally
separate from the diff-based click pair means a result here cannot leak into
(or be explained by) the click-path attacker's own state.

Read-only investigation: no product EXE bytes are changed here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, cast

import numpy as np
from PIL import Image

from tools import runtime_env
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools.g5_candidate_drag_probe import (
    ProbeError,
    SupplyProbe,
    DRAG_START,
    DRAG_END,
    UNIT_BASE,
    UNIT_STRIDE,
    UNIT_COMMAND_OFFSET,
    UNIT_PENDING_TARGET_UID_OFFSET,
    STOCK_SELECTION_BASE,
    STOCK_SELECTION_CAPACITY,
    SEED_TYPE,
    VISIBLE_WORKER_SLOT,
    selection_snapshot,
    unit_snapshot,
    sha256,
    write_json,
    capture,
    send_key,
)
from tools.g5_screen_world_calibration import op8_attack_order, read_unit

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE

# Phase A pair: isolated at the far side of the (0..179, 0..179) map, well
# outside the camera viewport the minimap click centers on the worker, so it
# never contributes a pixel to the phase B diff captures.
PHASE_A_ATTACKER_WORLD = (172, 172)
PHASE_A_TARGET_WORLD = (174, 172)

# Phase B pair: same worker-relative anchor lap666-672 already validated
# stays inside the visible viewport and the DRAG_START/DRAG_END rectangle.
ATTACKER_OFFSET_FROM_WORKER = (2, 2)
# Farther than lap672's (3, -1) (which showed inconsistent auto-aggro at
# ~3.16 tiles); pushed out to ~6.7 tiles to leave more margin outside
# whatever the engine's own engagement/aggro radius is, while lap668-671's
# fits show offsets of this rough magnitude stay inside the safe viewport
# band (0<=x<=1580, 0<=y<=460).
TARGET_OFFSET_FROM_ATTACKER = (6, -3)
# The play-area ROI used for the diff (excludes the bottom command HUD).
DIFF_ROI = (0, 0, 1600, 480)
DIFF_THRESHOLD = 30
# lap673 run1's raw two-frame diff (no stability baseline) produced a
# dominant ~18k-pixel blob straddling the bottom command panel plus dozens
# of 100-1000px blobs scattered across the whole play area -- ambient idle
# animation and HUD updates, not the new sprite. STABILITY_GAP_S is the
# spacing between the two "nothing new yet" baseline captures used to mask
# out any pixel that was already moving on its own before the new unit
# existed; MIN/MAX_BLOB_PIXELS bound what is plausible for one small unit
# sprite at 1600x1200.
STABILITY_GAP_S = 0.15
STABILITY_TOLERANCE = 18
MIN_BLOB_PIXELS = 40
MAX_BLOB_PIXELS = 4000
RETRY_OFFSETS = [(0, 0), (8, 0), (-8, 0), (0, 8), (0, -8), (8, 8), (-8, -8), (8, -8), (-8, 8)]


def read_unit_slim(pid: int, slot: int) -> dict[str, Any]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "command": int.from_bytes(read_memory(pid, base + UNIT_COMMAND_OFFSET, 2), "little", signed=True),
        "pending_target_uid": int.from_bytes(
            read_memory(pid, base + UNIT_PENDING_TARGET_UID_OFFSET, 4), "little", signed=False,
        ),
    }


def _load_rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)


def _label_components(mask: np.ndarray) -> tuple[np.ndarray, int]:
    """8-connected component labeling with plain numpy (no scipy dependency).

    ``make check`` runs under ``.venv/bin/python`` (a separate interpreter
    from the ``python3`` this tool was first exercised with), which does not
    have scipy installed; adding it would be an undeclared new project
    dependency for one diagnostic tool. A boolean mask over one 1600x1200
    capture has at most a few tens of thousands of set pixels even before
    stability filtering, so a plain flood fill is fast enough here.
    """
    labels = np.zeros(mask.shape, dtype=np.int32)
    height, width = mask.shape
    ys, xs = np.nonzero(mask)
    unvisited = set(zip(ys.tolist(), xs.tolist()))
    current_label = 0
    while unvisited:
        start = unvisited.pop()
        current_label += 1
        stack = [start]
        labels[start] = current_label
        while stack:
            y, x = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    neighbor = (y + dy, x + dx)
                    if 0 <= neighbor[0] < height and 0 <= neighbor[1] < width and neighbor in unvisited:
                        unvisited.discard(neighbor)
                        labels[neighbor] = current_label
                        stack.append(neighbor)
    return labels, current_label


def sprite_diff_centroid(
    before_path: Path, after_path: Path, *, roi: tuple[int, int, int, int] = DIFF_ROI,
    threshold: int = DIFF_THRESHOLD, stability_reference_path: Path | None = None,
    stability_tolerance: int = STABILITY_TOLERANCE,
    min_blob_pixels: int = MIN_BLOB_PIXELS, max_blob_pixels: int = MAX_BLOB_PIXELS,
) -> dict[str, Any]:
    """Locate the pixel cluster that changed between two same-size captures.

    ``roi`` is ``(x0, y0, x1, y1)`` and restricts the search to the play area
    so the bottom command HUD cannot be mistaken for the new sprite.

    Ambient motion (idle-unit animation cycles, water/flag shimmer, HUD
    counters ticking) changes plenty of pixels on its own between two
    captures a fraction of a second apart, and several of those regions are
    the same rough size as a single unit sprite -- confirmed directly by an
    initial run's raw two-frame diff, which produced dozens of 100-1000px
    blobs scattered across the whole play area with no reliable way to pick
    the real one. ``stability_reference_path`` is an *earlier* capture of the
    same scene, taken before ``before_path`` with nothing new spawned yet;
    any pixel that already changed between it and ``before_path`` is ambient
    motion and is excluded before diffing against ``after_path``, so only a
    genuinely new object can register there. Among the surviving connected
    components the candidate is the largest one sized like a single unit
    sprite (``min_blob_pixels``..``max_blob_pixels``); if none fits that
    range the largest overall surviving blob is still reported for
    diagnosis, flagged ``confident_single_blob: false``.
    """
    before = _load_rgb(before_path)
    after = _load_rgb(after_path)
    if before.shape != after.shape:
        raise ProbeError(f"capture shape mismatch: {before.shape} vs {after.shape}")
    diff = np.abs(after - before).sum(axis=2)
    x0, y0, x1, y1 = roi
    mask = np.zeros_like(diff, dtype=bool)
    mask[y0:y1, x0:x1] = diff[y0:y1, x0:x1] > threshold
    ambient_excluded = 0
    if stability_reference_path is not None:
        reference = _load_rgb(stability_reference_path)
        if reference.shape != before.shape:
            raise ProbeError(f"stability reference shape mismatch: {reference.shape} vs {before.shape}")
        ambient = np.abs(before - reference).sum(axis=2) > stability_tolerance
        ambient_excluded = int((mask & ambient).sum())
        mask &= ~ambient
    pixel_count = int(mask.sum())
    if pixel_count == 0:
        return {
            "pixel_count": 0, "centroid": None, "centroid_float": None, "bbox": None,
            "roi": list(roi), "threshold": threshold, "ambient_excluded_pixels": ambient_excluded,
            "confident_single_blob": False, "component_count": 0, "component_sizes_top5": [],
        }
    labeled, component_count = _label_components(mask)
    sizes = [int((labeled == label).sum()) for label in range(1, component_count + 1)]
    sized_candidates = [
        (index + 1, size) for index, size in enumerate(sizes)
        if min_blob_pixels <= size <= max_blob_pixels
    ]
    if sized_candidates:
        sized_candidates.sort(key=lambda item: item[1], reverse=True)
        best_label = sized_candidates[0][0]
        confident = True
    else:
        best_label = int(np.argmax(sizes)) + 1
        confident = False
    blob_mask = labeled == best_label
    ys, xs = np.nonzero(blob_mask)
    weights = diff[ys, xs].astype(np.float64)
    total_weight = float(weights.sum())
    cx = float((xs.astype(np.float64) * weights).sum() / total_weight)
    cy = float((ys.astype(np.float64) * weights).sum() / total_weight)
    bbox = {"x0": int(xs.min()), "x1": int(xs.max()), "y0": int(ys.min()), "y1": int(ys.max())}
    return {
        "pixel_count": int(blob_mask.sum()),
        "centroid": [int(round(cx)), int(round(cy))],
        "centroid_float": [cx, cy],
        "bbox": bbox,
        "roi": list(roi),
        "threshold": threshold,
        "ambient_excluded_pixels": ambient_excluded,
        "confident_single_blob": confident,
        "component_count": int(component_count),
        "component_sizes_top5": sorted(sizes, reverse=True)[:5],
    }


def candidate_click_points(centroid: tuple[int, int]) -> list[tuple[int, int]]:
    seen: set[tuple[int, int]] = set()
    points: list[tuple[int, int]] = []
    for dx, dy in RETRY_OFFSETS:
        point = (centroid[0] + dx, centroid[1] + dy)
        if point in seen:
            continue
        if not (0 <= point[0] <= 1580 and 0 <= point[1] <= 460):
            continue
        seen.add(point)
        points.append(point)
    return points


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    source_exe = source / runtime_env.ORIGINAL_EXE
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    bridge_dir = artifact_root / "stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(__import__("os").environ, PYTHONPATH=str(REPO)),
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

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-type2-ui-attack-diff-probe.v1",
        "status": "UNKNOWN",
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
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
    import os
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
        state_ps3 = wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")
        result["tick_at_game_start"] = state_ps3.get("tick")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        result["worker"] = worker
        supply = SupplyProbe(prefix)

        # --- Phase A: op8 tick-low ground truth, isolated far from the
        # camera so it cannot appear in any phase B diff capture.
        phase_a_attacker_receipt = supply.call(
            op=5, owner=0, unit_type=SEED_TYPE,
            x=PHASE_A_ATTACKER_WORLD[0], y=PHASE_A_ATTACKER_WORLD[1], count=1,
        )
        if not phase_a_attacker_receipt.get("ok") or phase_a_attacker_receipt.get("fixture_added") != 1:
            raise ProbeError(f"phase A attacker fixture failed: {phase_a_attacker_receipt}")
        phase_a_attacker_slot = int(phase_a_attacker_receipt.get("producer", {}).get("slot", 0))
        phase_a_target_receipt = supply.call(
            op=5, owner=1, unit_type=SEED_TYPE,
            x=PHASE_A_TARGET_WORLD[0], y=PHASE_A_TARGET_WORLD[1], count=1,
        )
        if not phase_a_target_receipt.get("ok") or phase_a_target_receipt.get("fixture_added") != 1:
            raise ProbeError(f"phase A target fixture failed: {phase_a_target_receipt}")
        phase_a_target_slot = int(phase_a_target_receipt.get("producer", {}).get("slot", 0))
        phase_a_target_base = UNIT_BASE + phase_a_target_slot * UNIT_STRIDE
        phase_a_target_handle = int.from_bytes(read_memory(pid, phase_a_target_base + 0x29C, 4), "little")
        tick_before_op8 = read_state(pid).get("tick")
        phase_a_op8 = op8_attack_order(supply, owner=0, src_slot=phase_a_attacker_slot, tgt_slot=phase_a_target_slot)
        phase_a_post_unit = read_unit(pid, phase_a_attacker_slot)
        result["phase_a_tick_low_op8"] = {
            "attacker_slot": phase_a_attacker_slot,
            "target_slot": phase_a_target_slot,
            "target_handle": phase_a_target_handle,
            "tick_before_call": tick_before_op8,
            "order_result": phase_a_op8,
            "post_unit_state": phase_a_post_unit,
            "order_accepted": bool(phase_a_op8.get("ok")) and phase_a_op8.get("raw_return") == 1,
            "target_uid_matches": phase_a_post_unit["pending_target_uid"] == phase_a_target_handle,
        }

        # --- Phase B: diff-based enemy hit-test, spawned near the worker.
        click(235, 555)
        time.sleep(1)
        result["captures"] = [capture(display, artifact_root / "before-attacker-1.png", log)]
        time.sleep(STABILITY_GAP_S)
        result["captures"].append(capture(display, artifact_root / "before-attacker-2.png", log))

        attacker_world = (int(worker["x"]) + ATTACKER_OFFSET_FROM_WORKER[0],
                           int(worker["y"]) + ATTACKER_OFFSET_FROM_WORKER[1])
        target_world = (attacker_world[0] + TARGET_OFFSET_FROM_ATTACKER[0],
                         attacker_world[1] + TARGET_OFFSET_FROM_ATTACKER[1])
        for label, world in (("attacker", attacker_world), ("target", target_world)):
            if any(not 0 <= value < 180 for value in world):
                raise ProbeError(f"{label} world position falls outside the map: {world}")

        attacker_receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE,
                                        x=attacker_world[0], y=attacker_world[1], count=1)
        if not attacker_receipt.get("ok") or attacker_receipt.get("fixture_added") != 1:
            raise ProbeError(f"type2 attacker fixture failed: {attacker_receipt}")
        attacker_slot = int(attacker_receipt.get("producer", {}).get("slot", 0))
        attacker_base = UNIT_BASE + attacker_slot * UNIT_STRIDE
        attacker_handle = int.from_bytes(read_memory(pid, attacker_base + 0x29C, 4), "little")
        result["attacker_fixture"] = {
            "requested_world": list(attacker_world), "slot": attacker_slot,
            "handle": attacker_handle, "receipt": attacker_receipt,
        }
        time.sleep(0.3)
        result["captures"].append(capture(display, artifact_root / "after-attacker.png", log))
        result["attacker_diff"] = sprite_diff_centroid(
            artifact_root / "before-attacker-2.png", artifact_root / "after-attacker.png",
            stability_reference_path=artifact_root / "before-attacker-1.png",
        )

        time.sleep(STABILITY_GAP_S)
        result["captures"].append(capture(display, artifact_root / "before-target-2.png", log))
        target_receipt = supply.call(op=5, owner=1, unit_type=SEED_TYPE,
                                      x=target_world[0], y=target_world[1], count=1)
        if not target_receipt.get("ok") or target_receipt.get("fixture_added") != 1:
            raise ProbeError(f"type2 target fixture failed: {target_receipt}")
        target_slot = int(target_receipt.get("producer", {}).get("slot", 0))
        target_base = UNIT_BASE + target_slot * UNIT_STRIDE
        target_handle = int.from_bytes(read_memory(pid, target_base + 0x29C, 4), "little")
        result["target_fixture"] = {
            "requested_world": list(target_world), "slot": target_slot,
            "handle": target_handle, "receipt": target_receipt,
        }
        # Before any click/drag touches either fixture: if the attacker is
        # already locked onto the target's exact handle here, that is
        # autonomous AI aggro, not the click path under test.
        result["attacker_state_immediately_after_spawn"] = read_unit_slim(pid, attacker_slot)
        time.sleep(0.3)
        result["captures"].append(capture(display, artifact_root / "after-target.png", log))
        target_diff = sprite_diff_centroid(
            artifact_root / "before-target-2.png", artifact_root / "after-target.png",
            stability_reference_path=artifact_root / "after-attacker.png",
        )
        result["target_diff"] = target_diff
        if target_diff["pixel_count"] == 0:
            raise ProbeError("no new sprite pixels detected after seeding the target")
        centroid = cast(tuple[int, int], tuple(target_diff["centroid"]))

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        attacker_selection = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["attacker_selection"] = attacker_selection
        result["captures"].append(capture(display, artifact_root / "after-attacker-select.png", log))
        if attacker_slot not in attacker_selection["slots"]:
            raise ProbeError(f"type2 attacker slot not selected via UI drag: {attacker_selection}")

        auto_aggro_before_input = (
            result["attacker_state_immediately_after_spawn"]["pending_target_uid"] == target_handle
        )
        result["auto_aggro_before_input"] = auto_aggro_before_input

        click_attempts: list[dict[str, Any]] = []
        click_hit: dict[str, Any] | None = None
        if not auto_aggro_before_input:
            for point in candidate_click_points(centroid):
                idle_deadline = time.monotonic() + 10
                while time.monotonic() < idle_deadline and read_unit_slim(pid, attacker_slot)["command"] != 1:
                    time.sleep(0.2)
                waited_idle = read_unit_slim(pid, attacker_slot)["command"] == 1
                send_key(display, "a", env=env, log=log)
                click(*point, button=1)
                time.sleep(0.05)
                immediate = read_unit_slim(pid, attacker_slot)
                time.sleep(0.3)
                after_click = read_unit_slim(pid, attacker_slot)
                hit = immediate["pending_target_uid"] == target_handle or after_click["pending_target_uid"] == target_handle
                entry = {
                    "screen": list(point), "waited_idle": waited_idle,
                    "immediate": immediate, "after": after_click, "target_uid_matches": hit,
                }
                click_attempts.append(entry)
                if hit:
                    click_hit = entry
                    result["captures"].append(capture(display, artifact_root / f"hit-{point[0]}-{point[1]}.png", log))
                    break
        result["click_attempts"] = click_attempts
        result["click_hit"] = click_hit
        result["captures"].append(capture(display, artifact_root / "after-click-attempts.png", log))

        if auto_aggro_before_input:
            result["status"] = "INCONCLUSIVE_AUTO_AGGRO"
        elif click_hit is not None:
            result["status"] = "PASS_TYPE2_UI_ATTACK_DIFF"
        else:
            result["status"] = "FAIL_TYPE2_UI_ATTACK_DIFF"
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
        cur_env = locals().get("env", __import__("os").environ)
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
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "").startswith("PASS") and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
