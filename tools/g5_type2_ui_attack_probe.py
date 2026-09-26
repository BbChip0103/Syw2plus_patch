#!/usr/bin/env python3
"""One original-only run: UI-path attack test with a type2 unit as attacker.

lap671 found the root cause of every prior G5 attack-attribution failure: the
probes so far (g5_screen_world_calibration.py, g5_attack_hit_offset_probe.py)
always used the pre-existing worker (slot 1198, unit_type 31) as the attacker.
Static disassembly of the original P6 domain gate (``FUN_00415880``) showed the
worker's ``+0x1D8`` bit ``0x4`` is 0, which makes the engine unconditionally
reject any attack order against a domain-flagged target (``+0x1BC==1``)
regardless of click precision or UI state -- a raw bridge op8 call proved this
directly (``PASS_TYPE2_DOMAIN_ATTACK``, tools/g5_attack_type2_domain_probe.py).
The G5 55-unit fixture itself is unit_type 2, which *does* have that domain
bit set.

This probe repeats the same UI path (drag-select, right-click calibration,
'A'+left-click attack with a y-offset sweep) but uses a freshly seeded type2
unit as the attacker instead of the worker, to check whether the UI input
path itself (as opposed to the engine's own order function) can carry a
domain-eligible unit's attack order. The worker is still used to calibrate
the screen->world affine transform (harmless move orders only; it never
issues an attack) since its position relative to the camera after the
minimap click is already a documented stable anchor.

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
from tools.g5_screen_world_calibration import (
    CALIBRATION_SCREEN_POINTS,
    CAMERA_ADDRESS,
    fit_affine,
    op8_attack_order,
    read_unit,
)

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
# Place the type2 attacker a few tiles from the worker (well inside the
# 9-point calibration grid's screen coverage) and the type2 target a further
# few tiles from the attacker, matching the offset magnitudes lap668-671
# already validated stay inside the 1600x1200 viewport after a minimap click.
ATTACKER_OFFSET_FROM_WORKER = (2, 2)
TARGET_OFFSET_FROM_ATTACKER = (3, -1)
Y_SWEEP_OFFSETS = [0, -8, -16, -24, -32, -40, -48, -56, -64, -72]
# A first attempt found the worker-fitted affine, when applied to a
# different (freshly spawned) unit's world position, carries a horizontal
# error too (observed directly: the enemy's true screen position differed
# from the naive inverse-affine point by tens of pixels in X as well as Y),
# so a Y-only sweep at a fixed X can miss the target's hitbox entirely.
X_SWEEP_OFFSETS = [0, -24, 24, -48, 48]


def read_unit_slim(pid: int, slot: int) -> dict[str, Any]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "command": int.from_bytes(read_memory(pid, base + UNIT_COMMAND_OFFSET, 2), "little", signed=True),
        "pending_target_uid": int.from_bytes(
            read_memory(pid, base + UNIT_PENDING_TARGET_UID_OFFSET, 4), "little", signed=False,
        ),
    }


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
        "schema": "syw2plus.g5-type2-ui-attack-probe.v1",
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
        supply = SupplyProbe(prefix)

        click(235, 555)
        time.sleep(1)
        camera_origin = list(
            int.from_bytes(read_memory(pid, CAMERA_ADDRESS + offset, 4), "little", signed=True)
            for offset in (0, 4)
        )
        result["camera_after_minimap"] = camera_origin
        result["captures"] = [capture(display, artifact_root / "after-worker.png", log)]

        # --- Step 1: calibrate the screen->world affine using the worker's
        # own plain right-click moves, *before* the type2 attacker/target
        # exist. The worker never issues an attack in this probe; it is only
        # a stable, pre-validated position anchor to fit the transform. Doing
        # this before spawning the attacker also avoids a first-attempt bug:
        # calibrating with the attacker already selected alongside the
        # worker would send the attacker along on every calibration move.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        worker_selection = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["worker_selection_for_calibration"] = worker_selection
        if VISIBLE_WORKER_SLOT not in worker_selection["slots"]:
            raise ProbeError(f"worker slot not selected for calibration: {worker_selection}")
        result["captures"].append(capture(display, artifact_root / "after-worker-drag.png", log))

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
        result["fit_max_abs_error"] = max(abs(v) for row in residuals for v in row["error"])

        matrix_inv = np.linalg.inv(matrix)

        def to_screen(world: tuple[int, int]) -> tuple[int, int]:
            float_point = matrix_inv @ (np.array(world) - offset)
            return (int(round(float_point[0])), int(round(float_point[1])))

        # --- Step 2: spawn the type2 attacker/target *after* calibration,
        # relative to the worker's original (pre-calibration) position, then
        # reuse the same broad drag rectangle that already reliably selects
        # units near the worker (confirmed directly: an earlier run's drag
        # here selected both the worker and a nearby type2 unit together).
        # No precision single-unit click is needed -- whatever else the
        # rectangle also picks up (e.g. the worker, wherever its calibration
        # moves left it) is irrelevant, since the check below reads the
        # attacker's own slot fields directly rather than depending on an
        # exact-membership selection.
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
        # Immediately after both fixtures exist, before any calibration
        # click or drag touches either of them: if this already shows an
        # attack command/target match, the engagement is autonomous AI
        # aggro (both are combat-capable type2 units in proximity), not
        # something the UI attack click below caused.
        result["attacker_state_immediately_after_spawn"] = read_unit_slim(pid, attacker_slot)
        result["captures"].append(capture(display, artifact_root / "after-fixture.png", log))

        target_screen = to_screen(target_world)
        result["target_screen_computed"] = list(target_screen)
        if not (0 <= target_screen[0] <= 1580 and 0 <= target_screen[1] <= 460):
            raise ProbeError(f"computed target screen point unsafe/out of viewport: {target_screen}")

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        attacker_selection = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["attacker_selection"] = attacker_selection
        result["captures"].append(capture(display, artifact_root / "after-attacker-select.png", log))
        if attacker_slot not in attacker_selection["slots"]:
            raise ProbeError(f"type2 attacker slot not selected via UI drag: {attacker_selection}")

        # --- Step 3: click-independent ground truth (bridge op=8) on the
        # same fixture, isolating "does the UI input path work" from "does
        # the engine's own order function accept this exact fixture" -- the
        # same separation lap670/671 used, now with the correct attacker
        # type.
        idle_deadline = time.monotonic() + 15
        while time.monotonic() < idle_deadline and read_unit(pid, attacker_slot)["command"] != 1:
            time.sleep(0.2)
        pre_op8_unit = read_unit(pid, attacker_slot)
        result["op8_waited_for_idle"] = pre_op8_unit["command"] == 1
        op8_result = op8_attack_order(supply, owner=0, src_slot=attacker_slot, tgt_slot=target_slot)
        time.sleep(0.3)
        post_op8_unit = read_unit(pid, attacker_slot)
        result["op8_clean_ground_truth"] = {
            "pre_unit_state": pre_op8_unit,
            "order_result": op8_result,
            "post_unit_state": post_op8_unit,
            # Require the order itself to have been accepted, not just a
            # target_uid match that could already be sitting there from
            # autonomous AI aggro before this order was even issued (a
            # rejected order with a pre-existing match must not count).
            "order_accepted": bool(op8_result.get("ok")) and op8_result.get("raw_return") == 1,
            "target_uid_matches": post_op8_unit["pending_target_uid"] == target_handle,
        }
        result["captures"].append(capture(display, artifact_root / "after-op8-clean.png", log))

        # --- Step 4: sweep the UI attack click's screen position in a small
        # X/Y grid around the naively-computed point (isometric sprites are
        # drawn above the tile floor, and the worker-fitted affine carries a
        # horizontal error too when applied to a different unit), waiting
        # for the attacker to settle idle before each attempt per the
        # FUN_00415480 gate found in lap671.
        sweep_hit = None
        for dx in X_SWEEP_OFFSETS:
            if sweep_hit is not None:
                break
            for dy in Y_SWEEP_OFFSETS:
                probe_point = (target_screen[0] + dx, target_screen[1] + dy)
                if not (0 <= probe_point[0] <= 1580 and 0 <= probe_point[1] <= 460):
                    result["y_sweep"].append({"dx": dx, "dy": dy, "screen": list(probe_point), "skipped": "out_of_viewport"})
                    continue
                attempt_deadline = time.monotonic() + 10
                while time.monotonic() < attempt_deadline and read_unit_slim(pid, attacker_slot)["command"] != 1:
                    time.sleep(0.2)
                waited_idle = read_unit_slim(pid, attacker_slot)["command"] == 1
                send_key(display, "a", env=env, log=log)
                click(*probe_point, button=1)
                time.sleep(0.05)
                immediate = read_unit_slim(pid, attacker_slot)
                time.sleep(0.3)
                after = read_unit_slim(pid, attacker_slot)
                hit = immediate["pending_target_uid"] == target_handle or after["pending_target_uid"] == target_handle
                entry = {
                    "dx": dx, "dy": dy, "screen": list(probe_point),
                    "waited_idle": waited_idle,
                    "immediate": immediate, "after": after,
                    "target_uid_matches": hit,
                }
                result["y_sweep"].append(entry)
                if hit:
                    sweep_hit = entry
                    result["captures"].append(capture(display, artifact_root / f"sweep-hit-dx{dx}-dy{dy}.png", log))
                    break
        result["y_sweep_hit"] = sweep_hit
        result["captures"].append(capture(display, artifact_root / "after-y-sweep.png", log))

        # Both type2 units are combat-capable and were spawned within a few
        # tiles of each other; if the attacker was already locked onto the
        # target's exact handle before any calibration/select/attack input
        # ran, that is autonomous AI aggro, not evidence the UI attack click
        # path works, and any later "hit" below is contaminated by it.
        auto_aggro_before_input = (
            result["attacker_state_immediately_after_spawn"]["pending_target_uid"] == target_handle
        )
        result["auto_aggro_before_input"] = auto_aggro_before_input
        op8_pass = result["op8_clean_ground_truth"]["order_accepted"] and result["op8_clean_ground_truth"]["target_uid_matches"]
        sweep_pass = sweep_hit is not None
        if auto_aggro_before_input:
            result["status"] = "INCONCLUSIVE_AUTO_AGGRO"
        elif op8_pass and sweep_pass:
            result["status"] = "PASS_TYPE2_UI_ATTACK"
        elif op8_pass or sweep_pass:
            result["status"] = "PASS_PARTIAL_TYPE2_UI_ATTACK"
        else:
            result["status"] = "FAIL_TYPE2_UI_ATTACK"
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
