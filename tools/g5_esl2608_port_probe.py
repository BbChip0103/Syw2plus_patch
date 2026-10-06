#!/usr/bin/env python3
"""Paired runtime probe for the G5 v10 port onto the ESL2608 G2 executables.

``g2``   = the delivered ESL2608 G2 EXE (stock 20-entry selection at 0x899024).
``port`` = ``g5_esl2608_g2_port`` output (50-entry selection in ``.g5bss``).

Both run on the same G2 unit layout (4093-slot relocated pool) with a sparse
100-unit owner-0 fixture.  Stages: full-screen drag selection, Shift+click
rejection of one more unit at the cap, Shift remove/re-add, Ctrl+1 group
assign/recall, and a real UI MOVE and STOP for every selected unit with one
unselected sentinel.  Each run uses a private game copy, Wine prefix and Xvfb.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, cast

import numpy as np

from patches.population.g2_esl2608_runtime_layout import ESL2608_LAYOUT
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from patches.selection import g5_esl2608_g2_port as port_patch
from tools import runtime_env
from tools.g2_esl2608_phase_a_shift_probe import (
    BASE_SOURCE, CALIBRATION_POINTS, SEED_TYPE, UNIT_PENDING_XY_OFFSET, UNIT_STRIDE,
    copy_overlay, find_worker, live_fixture,
)
from tools.g2_esl2608_phase_b_command_probe import BUTTONS, _observe
from tools.g2_esl2608_phase_d_saveload_probe import OLD_SAVE, _load_status
from tools.g5_candidate_drag_probe import (
    PAUSE_LOAD_POINT, PAUSE_SAVE_POINT, RESUME_POINT, SAVE_ACTION_POINT, SAVE_MENU_RETURN_POINT,
    SAVE_SLOT_POINT, ProbeError, SupplyProbe, capture, send_key, sha256, write_json,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine

REPO = Path(__file__).resolve().parents[1]
INPUT_ROOT = REPO.parent / "260921_temp"
STOCK = REPO / "Syw2plus" / "syw2plus_original.exe"
LANES = {
    "normal": INPUT_ROOT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092.exe",
    "fixed_start": INPUT_ROOT
    / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092.exe",
}
SELECTION = {"g2": (0x00899024, 20), "port": (port_patch.G5BSS_VA, 50)}
ISOLATED_TARGET = 100


def selection_snapshot(pid: int, variant: str) -> dict[str, Any]:
    base, cap = SELECTION[variant]
    count = int.from_bytes(read_memory(pid, base, 4), "little", signed=True)
    if not 0 <= count <= cap:
        raise ProbeError(f"selection count outside 0..{cap}: {count}")
    raw = [int.from_bytes(read_memory(pid, base + 4 + i * 4, 4), "little") for i in range(count)]
    slots = [value & 0xFFF for value in raw]
    return {"count": count, "slots": slots, "unique_slots": len(set(slots))}


def _install(lane: str, variant: str) -> tuple[bytes, dict[str, Any]]:
    g2_path = LANES[lane]
    g2 = g2_path.read_bytes()
    if sha256(g2_path) != port_patch.G2_SHA256[lane]:
        raise ProbeError("G2 input SHA mismatch")
    if variant == "g2":
        return g2, {"sha256": port_patch.G2_SHA256[lane]}
    candidate, report = port_patch.build_candidate(STOCK.read_bytes(), g2)
    return candidate, report


def run_probe(lane: str, variant: str, runtime_root: Path, artifact_root: Path,
              foreign_save: Path | None = None) -> dict[str, Any]:
    if lane not in LANES or variant not in SELECTION:
        raise ProbeError(f"unsupported lane/variant: {lane}/{variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    exe_bytes, build_report = _install(lane, variant)
    cap = SELECTION[variant][1]
    bridge_dir = artifact_root / "bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", "4093",
                    "--unit-pool-base", hex(ESL2608_LAYOUT.unit_pool_base)],
                   cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("private source copy SHA mismatch before install")
    overlay = copy_overlay(game)
    private_exe.write_bytes(exe_bytes)
    result: dict[str, Any] = {
        "schema": "syw2plus.g5-esl2608-port-probe.v1", "status": "UNKNOWN",
        "lane": lane, "variant": variant, "selection_cap": cap,
        "provenance": {"private_exe_sha256": sha256(private_exe), "input_sha256": sha256(LANES[lane]),
                        "private_game": str(game), "private_prefix": str(prefix),
                        "overlay_files": len(overlay), "bridge_sha256": sha256(bridge),
                        "build_report": build_report},
        "inputs": [], "stages": {}, "checks": {}, "cleanup": {},
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
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def wait_for(pred: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> None:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = read_state(pid)
                    if pred(last):
                        return
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        def wait_for_state(pred: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> None:
            wait_for(pred, label, timeout)

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
            result["inputs"].append({"x": x, "y": y, "button": button,
                                     "drag_to": list(drag_to) if drag_to else None})

        def shift_click(x: int, y: int) -> None:
            subprocess.run(["xdotool", "keydown", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            time.sleep(0.15)
            try:
                click(x, y)
            finally:
                time.sleep(0.15)
                subprocess.run(["xdotool", "keyup", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            time.sleep(0.3)

        def ctrl_key(name: str) -> None:
            subprocess.run(["xdotool", "keydown", "ctrl", "key", name, "keyup", "ctrl"],
                           env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"key": name, "ctrl": True})

        def snap() -> dict[str, Any]:
            return selection_snapshot(pid, variant)

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        wait_for(lambda s: s.get("ps") == 5 and runtime_env._read_local_ready_state(
            lambda a, n: read_memory(pid, a, n)).get("ready_value") == 1, "ready", timeout=15)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")
        worker = find_worker(pid, candidate=True)
        supply = SupplyProbe(prefix)
        map_w = int.from_bytes(read_memory(pid, 0x00B3DE34, 2), "little", signed=True)
        map_h = int.from_bytes(read_memory(pid, 0x00B3DE36, 2), "little", signed=True)
        xs = tuple(dx for dx in range(-30, 31, 3) if 0 < worker["x"] + dx < map_w)[:10]
        points = [(worker["x"] + dx, worker["y"] + dy) for dy in range(-10, 0) for dx in xs
                  if 0 < worker["y"] + dy < map_h]
        if len(points) < 100:
            raise ProbeError(f"map cannot fit fixture: {len(points)}")
        for x, y in points[:100]:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=x, y=y, count=1)
            if not receipt.get("ok") or receipt.get("fixture_added") != 1:
                raise ProbeError(f"fixture spawn failed at {(x, y)}: {receipt}")
        time.sleep(1)
        fixture = live_fixture(pid, candidate=True)
        if len(fixture) < 100:
            raise ProbeError(f"active fixture below 100: {len(fixture)}")
        fixture_slots = {row["slot"] for row in fixture}
        click(200, 170, drag_to=(730, 445))
        time.sleep(0.4)
        click(120, 90, button=3)
        time.sleep(0.2)
        worker_base = ESL2608_LAYOUT.unit_pool_base + worker["slot"] * UNIT_STRIDE
        samples = []
        for point in CALIBRATION_POINTS:
            click(*point, button=3)
            time.sleep(0.2)
            raw = int.from_bytes(read_memory(pid, worker_base + UNIT_PENDING_XY_OFFSET, 4), "little")
            samples.append((point, decode_xy(raw)))
        matrix, offset = fit_affine(samples)
        inverse = np.linalg.inv(matrix)

        def world_to_screen(x: int, y: int) -> tuple[int, int]:
            p = inverse @ (np.array([x, y]) - offset)
            return int(round(p[0])), int(round(p[1]))

        blank = world_to_screen(worker["x"], worker["y"] - 8)

        def deselect() -> None:
            click(*blank)
            time.sleep(0.25)
            if snap()["count"] != 0:
                raise ProbeError("deselect point selected a unit")

        ordered = sorted(fixture, key=lambda r: (r["y"], r["x"], r["slot"]))
        visible = [(r, world_to_screen(r["x"], r["y"])) for r in ordered]
        visible = [(r, s) for r, s in visible if 5 <= s[0] <= 795 and 45 <= s[1] <= 470]
        isolated: list[tuple[int, tuple[int, int]]] = []
        for row, screen in visible:
            for dy in (-12, -20, -6, 0, 6):
                deselect()
                click(screen[0], screen[1] + dy)
                time.sleep(0.3)
                s = snap()
                if s["count"] == 1 and s["slots"] == [row["slot"]]:
                    isolated.append((row["slot"], (screen[0], screen[1] + dy)))
                    break
            if len(isolated) >= ISOLATED_TARGET:
                break
        if len(isolated) < 4:
            raise ProbeError(f"too few isolated fixture rows: {len(isolated)}")
        result["stages"]["fixture"] = {
            "active_units": len(fixture), "visible_units": len(visible), "isolated": len(isolated),
            "slot_min": min(fixture_slots), "slot_max": max(fixture_slots),
            "slots_above_1200": sum(1 for s in fixture_slots if s >= 1200),
            "worker": worker,
        }
        deselect()

        def drag_all() -> dict[str, Any]:
            click(12, 40, drag_to=(788, 470))
            time.sleep(0.8)
            return snap()

        stage: dict[str, Any] = {"drag": drag_all()}
        result["stages"]["selection"] = stage
        selected = set(stage["drag"]["slots"])
        stage["drag_all_fixture"] = selected <= fixture_slots | {worker["slot"]}
        out_row = next(((slot, xy) for slot, xy in isolated if slot not in selected), None)
        in_row = next(((slot, xy) for slot, xy in isolated if slot in selected), None)
        if out_row is None or in_row is None:
            raise ProbeError(f"need isolated rows both in and out of the drag selection: {isolated}")
        shift_click(*out_row[1])
        stage["reject_extra"] = snap()
        stage["reject_extra_slot"] = out_row[0]
        shift_click(*in_row[1])
        stage["shift_remove"] = snap()
        stage["shift_remove_slot"] = in_row[0]
        shift_click(*in_row[1])
        stage["shift_readd"] = snap()
        assigned = set(stage["shift_readd"]["slots"])
        ctrl_key("1")
        time.sleep(0.3)
        deselect()
        stage["group_cleared"] = snap()
        ctrl_key("1")
        time.sleep(0.4)
        stage["group_recall"] = snap()

        current = list(stage["group_recall"]["slots"])
        sentinel = next(slot for slot in sorted(fixture_slots) if slot not in current)
        dest = world_to_screen(worker["x"], worker["y"] + 6)
        if not (10 <= dest[0] <= 790 and 45 <= dest[1] <= 470):
            raise ProbeError(f"move destination outside viewport: {dest}")
        result["stages"]["move"] = _observe(
            pid, current, sentinel, candidate=True, action=lambda: click(*dest, button=3), label="move")
        result["stages"]["stop"] = _observe(
            pid, current, sentinel, candidate=True, action=lambda: click(*BUTTONS["stop"]), label="stop")
        move, stop = result["stages"]["move"], result["stages"]["stop"]

        # Save with the full group selected, clear the selection, then load.
        ctrl_key("1")
        time.sleep(0.4)
        saved_selection = snap()
        saved_fixture = sorted((r["slot"], r["x"], r["y"]) for r in live_fixture(pid, candidate=True))
        save_path = game / "save" / "save001.dat"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        send_key(display, "Escape", env=env, log=log)
        wait_for(lambda s: s.get("ps") == 23, "pause_for_save")
        click(*PAUSE_SAVE_POINT)
        time.sleep(0.4)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        time.sleep(1.0)
        if not save_path.is_file():
            raise ProbeError("save was not created")
        raw = save_path.read_bytes()
        shutil.copy2(save_path, artifact_root / "own_save001.dat")
        saveload: dict[str, Any] = {
            "selection_before": saved_selection, "size": len(raw), "sha256": sha256(save_path),
            "n4k8": b"N4K8" in raw, "g5sc_offset_from_end": len(raw) - raw.rfind(b"G5SC")
            if b"G5SC" in raw else None,
        }
        result["stages"]["saveload"] = saveload
        click(*SAVE_MENU_RETURN_POINT)
        click(*RESUME_POINT)
        wait_for(lambda s: s.get("ps") == 3, "resume_after_save")
        deselect()
        send_key(display, "Escape", env=env, log=log)
        wait_for(lambda s: s.get("ps") == 23, "pause_for_load")
        click(*PAUSE_LOAD_POINT)
        time.sleep(0.4)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        saveload["load"] = _load_status(game_proc, pid, wait_for_state)
        time.sleep(0.5)
        saveload["selection_after"] = snap()
        after_fixture = sorted((r["slot"], r["x"], r["y"]) for r in live_fixture(pid, candidate=True))
        saveload["fixture_equal"] = after_fixture == saved_fixture
        saveload["fixture_after"] = len(after_fixture)
        shutil.copy2(OLD_SAVE, save_path)
        send_key(display, "Escape", env=env, log=log)
        wait_for(lambda s: s.get("ps") == 23, "pause_for_old_load")
        click(*PAUSE_LOAD_POINT)
        time.sleep(0.4)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        saveload["old_save_load"] = _load_status(game_proc, pid, wait_for_state)
        time.sleep(0.5)
        saveload["old_save_selection"] = snap()
        if foreign_save is not None:
            shutil.copy2(foreign_save, save_path)
            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda s: s.get("ps") == 23, "pause_for_foreign_load")
            click(*PAUSE_LOAD_POINT)
            time.sleep(0.4)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            saveload["foreign_load"] = _load_status(game_proc, pid, wait_for_state)
            time.sleep(0.5)
            saveload["foreign_sha256"] = sha256(foreign_save)
            saveload["foreign_selection"] = snap()
            saveload["foreign_fixture"] = sorted(
                (r["slot"], r["x"], r["y"]) for r in live_fixture(pid, candidate=True))
        checks = {
            "drag_count_is_cap": stage["drag"]["count"] == cap,
            "drag_unique": stage["drag"]["unique_slots"] == stage["drag"]["count"],
            "drag_all_fixture": stage["drag_all_fixture"],
            "reject_keeps_cap": stage["reject_extra"]["count"] == cap
            and out_row[0] not in stage["reject_extra"]["slots"],
            "shift_remove": stage["shift_remove"]["count"] == cap - 1
            and in_row[0] not in stage["shift_remove"]["slots"],
            "shift_readd": stage["shift_readd"]["count"] == cap and in_row[0] in stage["shift_readd"]["slots"],
            "group_cleared": stage["group_cleared"]["count"] == 0,
            "group_recall": stage["group_recall"]["count"] == cap
            and set(stage["group_recall"]["slots"]) == assigned,
            "move_all": move["selected_match_count"] == cap and not move["sentinel_changed"],
            "stop_all": stop["selected_match_count"] == cap and not stop["sentinel_changed"],
            "save_markers": saveload["n4k8"] and (
                saveload["g5sc_offset_from_end"] == 208 if variant == "port"
                else saveload["g5sc_offset_from_end"] is None),
            "load_ok": saveload["load"]["status"] == "PASS",
            "load_selection_restored": saveload["selection_after"]["count"] == cap
            and saveload["selection_after"]["slots"] == saved_selection["slots"],
            "load_fixture_equal": saveload["fixture_equal"],
            "old_save_load_ok": saveload["old_save_load"]["status"] == "PASS"
            and saveload["old_save_selection"]["count"] <= 20,
            "foreign_load_ok": foreign_save is None or (
                saveload["foreign_load"]["status"] == "PASS"
                and len(saveload["foreign_fixture"]) > 0
                and saveload["foreign_selection"]["count"] <= cap),
            "game_alive": game_proc.poll() is None,
        }
        result["checks"] = checks
        result["status"] = "PASS" if all(checks.values()) else "FAIL"
        capture(display, artifact_root / "final.png", log)
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError, StopIteration) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        result["game_exit_code_before_cleanup"] = None if game_proc is None else game_proc.poll()
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        kill_env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
        subprocess.run(["wineserver", "-k"], env=kill_env, stdout=log, stderr=log, timeout=10, check=False)
        subprocess.run(["wineserver", "-w"], env=kill_env, stdout=log, stderr=log, timeout=10, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=5)
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix)}
        if game.exists():
            shutil.rmtree(game)
        result["cleanup"]["game_removed"] = not game.exists()
        result["source_unchanged"] = sha256(LANES[lane]) == port_patch.G2_SHA256[lane]
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=sorted(LANES), required=True)
    parser.add_argument("--variant", choices=sorted(SELECTION), required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--foreign-save", type=Path, help="save made by the other variant to load last")
    args = parser.parse_args(argv)
    result = run_probe(args.lane, args.variant, args.runtime_root, args.artifact_root, args.foreign_save)
    print(json.dumps({"status": result.get("status"), "lane": args.lane, "variant": args.variant,
                      "checks": result.get("checks"), "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
