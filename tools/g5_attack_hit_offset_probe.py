#!/usr/bin/env python3
"""One original-only run: clean op8 ground truth + UI attack-click y-offset sweep.

lap670 calibrated the screen->world affine transform exactly (residual <0.44
tile) but the UI "A"+left-click attack command still never wrote the target
UID at ``+0x38C``. lap670's op8 (bridge dispatch) ground-truth check ran
*after* a UI attack click had already forced the unit into an unrelated
command state, so its result was contaminated. This probe separates the two
checks in one run:

1. Calibrate the affine transform exactly as lap670 did (9 plain right-click
   move samples), then compute the exact screen point for the seeded owner1
   target -- no "A" key is pressed yet, so the unit's command state is still
   whatever the last plain move order left it in.
2. Issue one bridge op=8 attack order (``FUN_00415480``) *before any UI
   attack click in this run* and read ``+0x384/+0x388/+0x38C`` right after.
   This isolates "does the engine's own order function accept this exact
   fixture" from "is the UI input path broken".
3. Only after that clean read, sweep the UI attack click's screen Y upward
   in fixed pixel steps (isometric sprites are drawn above the tile floor,
   so the exact tile-center click may miss the unit's clickable hitbox) and
   record ``+0x38C`` attribution at each offset, stopping at first success.

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

from tools import runtime_env
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools.g5_candidate_drag_probe import (
    ProbeError,
    SupplyProbe,
    DRAG_START,
    DRAG_END,
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
from tools.g5_screen_world_calibration import (
    CALIBRATION_SCREEN_POINTS,
    CAMERA_ADDRESS,
    ENEMY_OFFSET,
    fit_affine,
    op8_attack_order,
    read_unit,
)

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
# Sweep upward (smaller screen Y) in fixed steps; the fitted affine put the
# per-world-tile vertical screen delta at roughly 15-17px (half-tile), so
# 8px steps cover up to ~4.5 tiles of sprite height above the tile floor.
Y_SWEEP_OFFSETS = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]


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
        "schema": "syw2plus.g5-attack-hit-offset-probe.v1",
        "status": "UNKNOWN",
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
            "private_exe_sha256": sha256(private_exe),
            "original_manifest_check": original_check,
            "bridge_sha256": sha256(bridge),
        },
        "inputs": [],
        "calibration_points": [],
        "y_sweep": [],
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
        wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        result["worker"] = worker

        enemy_world = (int(worker["x"]) + ENEMY_OFFSET[0], int(worker["y"]) + ENEMY_OFFSET[1])
        if any(not 0 <= value < 180 for value in enemy_world):
            raise ProbeError(f"enemy target falls outside the map: {enemy_world}")
        supply = SupplyProbe(prefix)
        target_receipt = supply.call(op=5, owner=1, unit_type=SEED_TYPE, x=enemy_world[0], y=enemy_world[1], count=1)
        if not target_receipt.get("ok") or target_receipt.get("fixture_added") != 1:
            raise ProbeError(f"enemy fixture failed: {target_receipt}")
        target_slot = int(target_receipt.get("producer", {}).get("slot", 0))
        target_base = 0x0066B790 + target_slot * 0x758
        target_handle = int.from_bytes(read_memory(pid, target_base + 0x29C, 4), "little")
        result["enemy_fixture"] = {
            "requested_world": list(enemy_world), "slot": target_slot, "handle": target_handle,
            "receipt": target_receipt,
        }

        click(235, 555)
        time.sleep(1)
        camera_origin = list(
            int.from_bytes(read_memory(pid, CAMERA_ADDRESS + offset, 4), "little", signed=True)
            for offset in (0, 4)
        )
        result["camera_after_minimap"] = camera_origin
        result["captures"] = [capture(display, artifact_root / "after-fixture.png", log)]

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        selection = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["selection"] = selection
        if VISIBLE_WORKER_SLOT not in selection["slots"]:
            raise ProbeError(f"worker slot not selected for calibration: {selection}")
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))

        # --- Step 1: calibrate the screen->world affine with plain right
        # clicks only.  No "A" key is pressed anywhere before this point in
        # the run, so the unit's command state stays in whatever a plain
        # move order leaves it in.
        samples: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for point in CALIBRATION_SCREEN_POINTS:
            click(*point, button=3)
            time.sleep(0.4)
            unit = read_unit(pid, VISIBLE_WORKER_SLOT)
            world = tuple(unit["pending_xy"])
            samples.append((point, world))
            result["calibration_points"].append({"screen": list(point), "world": list(world), "raw": unit})

        matrix, offset = fit_affine(samples)
        result["fit"] = {"matrix": matrix.tolist(), "offset": offset.tolist()}
        import numpy as np

        residuals = []
        for point, world in samples:
            predicted = matrix @ np.array(point) + offset
            residuals.append({"screen": list(point), "world": list(world),
                               "predicted": predicted.tolist(),
                               "error": (predicted - np.array(world)).tolist()})
        result["fit_residuals"] = residuals
        result["fit_max_abs_error"] = max(abs(v) for row in residuals for v in row["error"])

        matrix_inv = np.linalg.inv(matrix)
        target_screen_float = matrix_inv @ (np.array(enemy_world) - offset)
        target_screen = (int(round(target_screen_float[0])), int(round(target_screen_float[1])))
        result["target_screen_computed"] = {"float": target_screen_float.tolist(), "rounded": list(target_screen)}
        if not (0 <= target_screen[0] <= 1580 and 0 <= target_screen[1] <= 460):
            raise ProbeError(f"computed attack screen point unsafe/out of viewport: {target_screen}")

        # --- Step 2: clean bridge op=8 ground truth.  This is the first and
        # only attack-shaped command issued so far in this run -- no UI "A"
        # key has been sent yet, so the unit's +0x290 command state cannot
        # already have been forced into an unrelated branch by a prior UI
        # attack click (that was lap670's contamination).
        #
        # Static disassembly of FUN_00415480 (this lap) found the issuer
        # only accepts a new order when +0x290 (current command) is 1
        # (idle), 4 (already attacking), 0x23, or 3-with-+0x294==1; every
        # prior attempt caught the unit mid-move (command 3 or 8) without
        # +0x294 set, which the issuer rejects unconditionally at 0x41562f.
        # Wait for the unit to settle into idle (command==1) before issuing,
        # which the idle branch (0x4154f3) accepts without the +0x294 gate.
        idle_deadline = time.monotonic() + 15
        while time.monotonic() < idle_deadline and read_unit(pid, VISIBLE_WORKER_SLOT)["command"] != 1:
            time.sleep(0.2)
        pre_op8_unit = read_unit(pid, VISIBLE_WORKER_SLOT)
        result["op8_waited_for_idle"] = pre_op8_unit["command"] == 1
        op8_result = op8_attack_order(supply, owner=0, src_slot=VISIBLE_WORKER_SLOT, tgt_slot=target_slot)
        time.sleep(0.3)
        post_op8_unit = read_unit(pid, VISIBLE_WORKER_SLOT)
        result["op8_clean_ground_truth"] = {
            "pre_unit_state": pre_op8_unit,
            "order_result": op8_result,
            "post_unit_state": post_op8_unit,
            "target_uid_matches": post_op8_unit["pending_target_uid"] == target_handle,
        }
        result["captures"].append(capture(display, artifact_root / "after-op8-clean.png", log))

        # --- Step 3: sweep the UI attack click's screen Y upward in fixed
        # pixel steps.  Isometric sprites are drawn above the tile floor, so
        # the exact tile-center click computed above may land below the
        # unit's clickable hitbox.  Per the FUN_00415480 gate found in step
        # 2, wait for the unit to be idle (command==1) before each attempt
        # instead of re-issuing a move (which would force command back to
        # 3/8 and get rejected regardless of click precision).
        sweep_hit = None
        for dy in Y_SWEEP_OFFSETS:
            probe_point = (target_screen[0], target_screen[1] + dy)
            if not (0 <= probe_point[0] <= 1580 and 0 <= probe_point[1] <= 460):
                result["y_sweep"].append({"dy": dy, "screen": list(probe_point), "skipped": "out_of_viewport"})
                continue
            attempt_deadline = time.monotonic() + 10
            while time.monotonic() < attempt_deadline and read_unit(pid, VISIBLE_WORKER_SLOT)["command"] != 1:
                time.sleep(0.2)
            waited_idle = read_unit(pid, VISIBLE_WORKER_SLOT)["command"] == 1
            send_key(display, "a", env=env, log=log)
            click(*probe_point, button=1)
            time.sleep(0.05)
            immediate = read_unit(pid, VISIBLE_WORKER_SLOT)
            time.sleep(0.3)
            after = read_unit(pid, VISIBLE_WORKER_SLOT)
            hit = immediate["pending_target_uid"] == target_handle or after["pending_target_uid"] == target_handle
            entry = {
                "dy": dy, "screen": list(probe_point),
                "waited_idle": waited_idle,
                "immediate": immediate, "after": after,
                "target_uid_matches": hit,
            }
            result["y_sweep"].append(entry)
            if hit:
                sweep_hit = entry
                result["captures"].append(capture(display, artifact_root / f"y-sweep-hit-dy{dy}.png", log))
                break
        result["y_sweep_hit"] = sweep_hit
        result["captures"].append(capture(display, artifact_root / "after-y-sweep.png", log))

        op8_pass = result["op8_clean_ground_truth"]["target_uid_matches"]
        sweep_pass = sweep_hit is not None
        if op8_pass or sweep_pass:
            result["status"] = "PASS_ATTACK_ATTRIBUTION"
        else:
            result["status"] = "FAIL_ATTACK_ATTRIBUTION"
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
