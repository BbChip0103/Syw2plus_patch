#!/usr/bin/env python3
"""lap710 scratch probe: boot the protected original to ps3 (playing) and
capture a full-window screenshot so the minimap widget's screen box can be
located visually, before any calibration/click logic is written. Read-only
w.r.t. the protected source; only a private per-run copy is executed.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, sha256, capture,
    DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    SEED_TYPE, VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    selection_snapshot, unit_snapshot,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
import numpy as np
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

SHARED_TEMP = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch")
ARTIFACT_ROOT = SHARED_TEMP / "20260927_lap710_minimap_calibration"
RUNTIME_ROOT = REPO / "local" / "runtime" / "lap710-minimap-calibration-runtime"

# lap710 visual read of full-window.png (docs/history/laps/20260927_lap710_*):
# the isometric diamond bottom-left of the HUD (screen roughly x in [0,176],
# y in [511,598], vertices top(88,511) right(176,550) bottom(88,598)
# left(0,550)) is the candidate minimap; the round frame above it is an
# (empty) portrait socket and the dialed gauge further right is a separate
# compass/clock widget -- neither of those two is tested here.
MINIMAP_PROBE_POINTS = [
    (88, 554), (44, 532), (132, 532), (44, 576), (132, 576),
    (88, 520), (88, 588), (20, 550), (156, 550),
]
COMPASS_DIAL_PROBE_POINTS = [
    (235, 555), (215, 540), (255, 540), (215, 575), (255, 575), (235, 527), (235, 585),
]
VIEWPORT_CALIBRATION_POINTS = [
    (250, 200), (475, 200), (700, 200),
    (250, 320), (475, 320), (700, 320),
    (250, 440), (475, 440), (700, 440),
]


def main() -> int:
    if ARTIFACT_ROOT.exists():
        raise ProbeError(f"artifact root must be new: {ARTIFACT_ROOT}")
    ARTIFACT_ROOT.mkdir(parents=True)
    source, source_exe = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    if sha256(source_exe) != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("protected source executable SHA mismatch before run")

    bridge_dir = ARTIFACT_ROOT / "stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
    )
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=RUNTIME_ROOT, bridge=bridge, timeout=60)
    game = Path(str(manifest["game"]["root"]))
    prefix = Path(str(manifest["wine"]["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE

    log_path = ARTIFACT_ROOT / "probe.log"
    log = log_path.open("a", encoding="utf-8")
    children: list[subprocess.Popen] = []
    xvfb = None
    display = ""
    pid: int | None = None
    result: dict = {}
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

        def state() -> dict:
            assert pid is not None
            return read_state(pid)

        def wait_for(predicate, label: str, timeout: float = 45) -> dict:
            deadline = time.monotonic() + timeout
            last: dict = {}
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
        result["content_info"] = {k: content_info[k] for k in ("x", "y", "width", "height")}

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda item: item.get("ps") == 7, "ps7")

        def read_selector() -> dict:
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
        ready: dict = {}
        while time.monotonic() < ready_deadline:
            ready = runtime_env._read_local_ready_state(lambda address, size: read_memory(pid, address, size))
            if ready.get("ready_value") == 1:
                break
            time.sleep(0.2)
        if ready.get("ready_value") != 1:
            raise ProbeError(f"local lobby did not become ready: {ready}")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")

        time.sleep(1)
        result["capture_full"] = str(capture(display, ARTIFACT_ROOT / "full-window.png", log))

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        result["worker"] = worker

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        worker_selection = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["worker_selection"] = worker_selection
        if VISIBLE_WORKER_SLOT not in worker_selection["slots"]:
            raise ProbeError(f"worker slot not selected for calibration: {worker_selection}")

        def read_worker_pending() -> tuple[int, int]:
            base = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE
            raw = int.from_bytes(read_memory(pid, base + UNIT_PENDING_XY_OFFSET, 4), "little", signed=False)
            return decode_xy(raw)

        before_probe = read_worker_pending()
        result["pending_before_probe"] = list(before_probe)
        minimap_samples = []
        for point in MINIMAP_PROBE_POINTS:
            click(*point, button=3)
            time.sleep(0.4)
            world = read_worker_pending()
            minimap_samples.append({"screen": list(point), "world": list(world)})
        result["minimap_right_click_samples"] = minimap_samples

        compass_samples = []
        for point in COMPASS_DIAL_PROBE_POINTS:
            click(*point, button=3)
            time.sleep(0.4)
            world = read_worker_pending()
            compass_samples.append({"screen": list(point), "world": list(world)})
        result["compass_dial_right_click_samples"] = compass_samples

        def calibrate_viewport(label: str) -> dict:
            samples = []
            for point in VIEWPORT_CALIBRATION_POINTS:
                click(*point, button=3)
                time.sleep(0.4)
                world = read_worker_pending()
                samples.append((point, world))
            matrix, offset = fit_affine(samples)
            screen_center = (475, 320)
            center_world = matrix @ np.array(screen_center) + offset
            return {
                "label": label, "matrix": matrix.tolist(), "offset": offset.tolist(),
                "center_world": center_world.tolist(),
            }

        cal_before = calibrate_viewport("before-minimap-left-click")
        result["viewport_calibration_before"] = cal_before

        # sanity/functional test: does a *left*-click on the candidate
        # minimap diamond move the camera (viewport center world shifts)?
        minimap_left_click_point = MINIMAP_PROBE_POINTS[5]  # (88, 520), near the diamond's top vertex
        click(*minimap_left_click_point, button=1)
        time.sleep(1)
        result["capture_after_minimap_left_click"] = str(
            capture(display, ARTIFACT_ROOT / "after-minimap-left-click.png", log)
        )
        cal_after = calibrate_viewport("after-minimap-left-click")
        result["viewport_calibration_after"] = cal_after
        result["viewport_center_shift_tiles"] = float(
            np.linalg.norm(np.array(cal_after["center_world"]) - np.array(cal_before["center_world"]))
        )

        click(*COMPASS_DIAL_PROBE_POINTS[0], button=1)
        time.sleep(1)
        result["capture_after_compass_left_click"] = str(
            capture(display, ARTIFACT_ROOT / "after-compass-left-click.png", log)
        )
        cal_after_compass = calibrate_viewport("after-compass-left-click")
        result["viewport_calibration_after_compass"] = cal_after_compass
        result["viewport_center_shift_tiles_compass"] = float(
            np.linalg.norm(np.array(cal_after_compass["center_world"]) - np.array(cal_after["center_world"]))
        )

        def press_key(key: str) -> None:
            subprocess.run(
                [sys.executable, str(REPO / "tools/x11_send_keys.py"), "--display", display, key],
                env=env, stdout=log, stderr=log, timeout=10, check=True,
            )

        for key in ("Tab", "m", "M"):
            press_key(key)
            time.sleep(0.6)
            result[f"capture_after_key_{key}"] = str(
                capture(display, ARTIFACT_ROOT / f"after-key-{key}.png", log)
            )
        result["status"] = "OK"
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
        try:
            subprocess.run(["wineserver", "-k"], env=os.environ, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=os.environ, stdout=log, stderr=log, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError):
            pass
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
                xvfb.wait(timeout=5)
        log.close()
    print(result)
    return 0 if result.get("status") == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
