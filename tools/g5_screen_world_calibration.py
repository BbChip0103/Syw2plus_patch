#!/usr/bin/env python3
"""Calibrate the screen->world hit-test transform in one original-only run.

lap668 found that a guessed attack-click screen point misses the seeded
owner1 target by 1-2 world tiles, so ``+0x38C`` target UID never attributes.
Rather than guess again, this probe issues a small grid of plain right-click
move commands from a single selected unit within one run, reads the resulting
``pending_xy`` for each, and fits the affine map ``world = M @ screen + c``
with least squares.  Because the camera does not move during the run, the
camera origin is folded into ``c`` and does not need to be read separately.
The inverse of that fit gives the exact screen point for the already-seeded
owner1 target's known world position, which is then used for one real
A+left-click attack command to check ``pending_target_uid`` attribution.

This is read-only investigation: no product EXE bytes are changed here.
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
    UNIT_X_OFFSET,
    UNIT_Y_OFFSET,
    UNIT_COMMAND_OFFSET,
    UNIT_PENDING_COMMAND_OFFSET,
    UNIT_PENDING_XY_OFFSET,
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

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
CAMERA_ADDRESS = 0x00B42D7C
MINIMAP_CLICK = (235, 555)
ENEMY_OFFSET = (3, -1)
CALIBRATION_SCREEN_POINTS = [
    (250, 200), (475, 200), (700, 200),
    (250, 320), (475, 320), (700, 320),
    (250, 440), (475, 440), (700, 440),
]


def decode_xy(raw: int) -> tuple[int, int]:
    x = raw & 0xFFFF
    y = (raw >> 16) & 0xFFFF
    if x >= 0x8000:
        x -= 0x10000
    if y >= 0x8000:
        y -= 0x10000
    return x, y


def read_unit(pid: int, slot: int) -> dict[str, Any]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    pending_xy_raw = int.from_bytes(read_memory(pid, base + UNIT_PENDING_XY_OFFSET, 4), "little", signed=False)
    return {
        "slot": slot,
        "command": int.from_bytes(read_memory(pid, base + UNIT_COMMAND_OFFSET, 2), "little", signed=True),
        "pending_command": int.from_bytes(read_memory(pid, base + UNIT_PENDING_COMMAND_OFFSET, 4), "little", signed=False),
        "pending_xy_raw": pending_xy_raw,
        "pending_xy": list(decode_xy(pending_xy_raw)),
        "pending_target_uid": int.from_bytes(read_memory(pid, base + UNIT_PENDING_TARGET_UID_OFFSET, 4), "little", signed=False),
        "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
        "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
    }


def op8_attack_order(supply: SupplyProbe, *, owner: int, src_slot: int, tgt_slot: int) -> dict[str, Any]:
    """Issue one original attack order via the unmodified issuer (bridge op=8).

    This bypasses screen/click hit-test entirely and calls the same
    ``FUN_00415480`` order function the G2 combat probe already validated
    (analysis/memory_maps/g2_unit_attack_cmd4_stop_issuer_0048ddd0_lap540).
    It gives a click-independent ground truth for what an engine-accepted
    attack order actually writes to +0x384/+0x388/+0x38c.
    """
    request_id = supply.next_id
    supply.next_id += 1
    supply.request.write_text(f"{request_id} 8 {owner} {src_slot} {tgt_slot} 0 0 0\n", encoding="ascii")
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        try:
            result = json.loads(supply.result.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            time.sleep(0.05)
            continue
        if result.get("id") == request_id:
            return result
        time.sleep(0.05)
    raise ProbeError(f"op8 attack order request timed out: id={request_id}")


def fit_affine(points: list[tuple[tuple[int, int], tuple[int, int]]]) -> tuple[np.ndarray, np.ndarray]:
    """Fit world = M @ screen + c by least squares; return (M, c)."""
    rows = []
    targets = []
    for (sx, sy), (wx, wy) in points:
        rows.append([sx, sy, 1, 0, 0, 0])
        targets.append(wx)
        rows.append([0, 0, 0, sx, sy, 1])
        targets.append(wy)
    a = np.array(rows, dtype=float)
    b = np.array(targets, dtype=float)
    solution, *_ = np.linalg.lstsq(a, b, rcond=None)
    m = np.array([[solution[0], solution[1]], [solution[3], solution[4]]])
    c = np.array([solution[2], solution[5]])
    return m, c


def run_calibration(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
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
        "schema": "syw2plus.g5-screen-world-calibration.v1",
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
        target_base = UNIT_BASE + target_slot * UNIT_STRIDE
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
        residuals = []
        for point, world in samples:
            predicted = matrix @ np.array(point) + offset
            residuals.append({"screen": list(point), "world": list(world),
                               "predicted": predicted.tolist(),
                               "error": (predicted - np.array(world)).tolist()})
        result["fit_residuals"] = residuals
        max_error = max(abs(v) for row in residuals for v in row["error"])
        result["fit_max_abs_error"] = max_error

        matrix_inv = np.linalg.inv(matrix)
        target_screen_float = matrix_inv @ (np.array(enemy_world) - offset)
        target_screen = (int(round(target_screen_float[0])), int(round(target_screen_float[1])))
        result["target_screen_computed"] = {"float": target_screen_float.tolist(), "rounded": list(target_screen)}
        if not (0 <= target_screen[0] <= 1580 and 0 <= target_screen[1] <= 460):
            raise ProbeError(f"computed attack screen point unsafe/out of viewport: {target_screen}")

        click(*target_screen, button=3)
        time.sleep(0.4)
        verify_unit = read_unit(pid, VISIBLE_WORKER_SLOT)
        result["verify_move"] = {
            "screen": list(target_screen), "expected_world": list(enemy_world),
            "observed_pending_xy": verify_unit["pending_xy"],
            "matches": tuple(verify_unit["pending_xy"]) == tuple(enemy_world),
        }
        result["captures"].append(capture(display, artifact_root / "verify-move.png", log))

        send_key(display, "a", env=env, log=log)
        result["inputs"].append({"key": "a", "attack_mode": True})
        click(*target_screen, button=1)
        time.sleep(0.05)
        attack_immediate = read_unit(pid, VISIBLE_WORKER_SLOT)
        time.sleep(0.3)
        attack_after = read_unit(pid, VISIBLE_WORKER_SLOT)
        result["captures"].append(capture(display, artifact_root / "after-attack.png", log))

        def is_attack(sample: Mapping[str, Any]) -> bool:
            return sample.get("command") == 4 or (sample.get("pending_command", 0) & 0xFFFF) == 4

        attack_hit = is_attack(attack_immediate) or is_attack(attack_after)
        target_hit = (
            attack_immediate["pending_target_uid"] == target_handle
            or attack_after["pending_target_uid"] == target_handle
        )
        result["attack_verification"] = {
            "target_handle": target_handle,
            "immediate": attack_immediate,
            "after": attack_after,
            "attack_command_observed": attack_hit,
            "target_uid_matches": target_hit,
            "pass": attack_hit and target_hit,
        }
        result["status"] = "PASS_CALIBRATED_ATTACK" if result["attack_verification"]["pass"] else "FAIL_CALIBRATED_ATTACK"

        # Click-independent ground truth: does the unmodified engine issuer
        # itself set +0x384/+0x388/+0x38c the way this probe expects, on the
        # exact same fixture?  This isolates "the UI input path is wrong"
        # from "the field/observation contract is wrong".
        op8_result = op8_attack_order(supply, owner=0, src_slot=VISIBLE_WORKER_SLOT, tgt_slot=target_slot)
        result["op8_ground_truth"] = op8_result
        result["op8_ground_truth_unit_state"] = read_unit(pid, VISIBLE_WORKER_SLOT)
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
    result = run_calibration(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "").startswith("PASS") and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
