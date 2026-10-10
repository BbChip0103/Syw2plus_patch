#!/usr/bin/env python3
"""G6 x save/load on ESL 2610: does the Shift+click defect (non-1P seat) survive the official 2610 G7 save/load path?

One run = private 2610 game copy, Wine prefix and Xvfb.  ``base2610`` = pinned official EXE, ``cand2610`` = + G6 layer.

A  start a solo game at ``--seat`` (seat != 0: the game's own lobby refresh ``0x4B7700`` at the ps5 lobby), calibrate the
   screen, seed a sparse fixture of owner=seat units, pause-menu save
B  in-game load (same process): record ``[0xB63FC4]``, ps, owners of units, then the G6 suite
C  new process, title screen load of the same save: same records and suite
G6 suite = G6-0 (empty selection, Shift+click A), G6-1 (click A, five Shift+clicks), G6-2 (Shift+drag control).
The camera/screen mapping calibrated before the save is reused after a load only when the scene screenshot is unchanged;
otherwise the suite is recorded as BLOCKED(camera) instead of guessing positions.
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
from typing import Any, Callable, cast

import numpy as np

from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from patches.population.runtime_driver import write as write_memory
from tools import esl2610_runtime, runtime_env
from tools import g6_shift_click_probe as g6
from tools.g1_saved_scene_probe import LOAD_CONFIRM, LOAD_MENU
from tools.g2_esl2608_phase_d_saveload_probe import _load_status
from tools.g5_candidate_drag_probe import (
    PAUSE_LOAD_POINT, PAUSE_SAVE_POINT, RESUME_POINT, SAVE_ACTION_POINT, SAVE_MENU_RETURN_POINT, SAVE_SLOT_POINT,
    ProbeError, SupplyProbe, capture, send_key, sha256, write_json,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g7_save_load_probe import owner_tally, title_list_index
from tools.s1_load_evidence import SELECTED_INDEX_ADDRESS

REPO = Path(__file__).resolve().parents[1]
SAVE_NAME = "save001.dat"
SCENE_BOX = (0, 40, 800, 470)
SCENE_DIFF_LIMIT = 6.0  # mean abs pixel diff; idle animation gives ~3, a shifted camera far more


def scene_diff(before: Path, after: Path) -> float:
    from PIL import Image

    x0, y0, x1, y1 = SCENE_BOX
    a = np.asarray(Image.open(before).convert("RGB"), dtype=np.int16)[y0:y1, x0:x1]
    b = np.asarray(Image.open(after).convert("RGB"), dtype=np.int16)[y0:y1, x0:x1]
    return float(np.abs(a - b).mean())


def run_probe(variant: str, seat: int, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if variant not in g6.ESL2610_VARIANTS:
        raise ProbeError(f"unsupported variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    _sel, cap, pool_base, _exists, pool_cap = g6.LAYOUTS[variant]
    exe_bytes, build_report = g6._install(variant)
    bridge_dir = artifact_root / "bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"), "--out-dir",
                    str(bridge_dir), "--unit-pool-capacity", str(pool_cap)],
                   cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest, overlay = esl2610_runtime.prepare(cast(bytes, exe_bytes), runtime_root, bridge=bridge)
    game = Path(cast(str, manifest["game"]["root"]))  # type: ignore[index]
    prefix = Path(cast(str, manifest["wine"]["prefix"]))  # type: ignore[index]
    private_exe = game / runtime_env.ORIGINAL_EXE
    result: dict[str, Any] = {
        "schema": "syw2plus.g6-saveload-2610-probe.v1", "status": "UNKNOWN", "variant": variant, "seat": seat,
        "provenance": {"private_exe_sha256": sha256(private_exe), "build_report": build_report,
                        "overlay_files": len(overlay), "bridge_sha256": sha256(bridge)},
        "stages": {}, "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    shots = artifact_root / "shots"
    shots.mkdir()
    children: list[Any] = []
    xvfb: Any = None
    display = ""
    proc: dict[str, Any] = {}
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all", LANG="ko_KR.UTF-8",
                   LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display

        def wait_for(pred: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> None:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = read_state(proc["pid"])
                    if pred(last):
                        return
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        def launch() -> None:
            explorer = subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game, env=env,
                                        stdout=log, stderr=log)
            time.sleep(1)
            game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
            children.extend([explorer, game_proc])
            proc.update(game=game_proc, pid=game_proc.pid)
            wait_for(lambda s: s.get("ps") == 9, "ps9")
            outer, content = runtime_env._game_window_ids(runtime_env._window_tree(display, 10))
            if content is None:
                raise ProbeError("game content window not found")
            info = runtime_env._xwininfo_details(display, content, 10)
            proc.update(origin=(int(info["x"]), int(info["y"])))
            subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)

        def stop_game() -> None:
            for child in children:
                if child.poll() is None:
                    child.terminate()
            for child in children:
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
            children.clear()
            kill_env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
            subprocess.run(["wineserver", "-k"], env=kill_env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=kill_env, stdout=log, stderr=log, timeout=30, check=False)

        def click(x: int, y: int, *, button: int = 1, drag_to: tuple[int, int] | None = None) -> None:
            ox, oy = proc["origin"]
            args = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(ox + x), str(oy + y), "--button", str(button)]
            if drag_to is not None:
                args += ["--drag-to", str(ox + drag_to[0]), str(oy + drag_to[1])]
            subprocess.run(args, env=env, stdout=log, stderr=log, timeout=10, check=True)

        def shift_hold(action: Callable[[], None]) -> None:
            subprocess.run(["xdotool", "keydown", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            time.sleep(0.15)
            try:
                action()
            finally:
                time.sleep(0.15)
                subprocess.run(["xdotool", "keyup", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            time.sleep(0.4)

        def shot(label: str) -> Path:
            path = shots / f"{time.strftime('%Y%m%d_%H%M%S')}_{label}.png"
            capture(display, path, log)
            return path

        def u(va: int, size: int, signed: bool = False) -> int:
            return g6._u(proc["pid"], va, size, signed)

        def snap() -> dict[str, Any]:
            return g6.selection_snapshot(proc["pid"], variant)

        def alive() -> bool:
            return proc["game"].poll() is None

        def record(label: str) -> dict[str, Any]:
            pid = proc["pid"]
            rows = [g6.unit_row(pid, variant, s) for s in range(1, pool_cap) if u(g6.LAYOUTS[variant][3] + s * 2, 2)]
            return {"label": label, "alive": alive(), "ps": read_state(pid).get("ps"),
                    "local_index": u(g6.LOCAL_INDEX_VA, 4), "owner_units": owner_tally(rows)}

        # ---------------- A: start at seat, calibrate, fixture, save
        launch()
        pid = proc["pid"]
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        if seat:
            raw = read_memory(pid, g6.LOBBY_TABLE_VA, g6.LOBBY_DUMP_END - g6.LOBBY_TABLE_VA)
            snapshot, _ids = g6.build_lobby_snapshot(raw[:g6.LOBBY_TABLE_SIZE], seat, u(g6.LOBBY_OWN_ID_VA, 4))
            write_memory(pid, g6.LOBBY_SNAPSHOT_VA, snapshot)
            write_memory(pid, g6.LOBBY_REFRESH_FLAG_VA, (1).to_bytes(4, "little"))
            deadline = time.monotonic() + 5
            while u(g6.LOBBY_REFRESH_FLAG_VA, 4) != 0 and time.monotonic() < deadline:
                time.sleep(0.1)
            time.sleep(0.5)
        if u(g6.LOCAL_INDEX_VA, 4) != seat:
            result["status"] = "BLOCKED"
            result["error"] = f"seat move failed: local_index={u(g6.LOCAL_INDEX_VA, 4)} wanted {seat}"
            return result
        deadline = time.monotonic() + 8
        while read_state(pid).get("ps") not in (2, 3) and time.monotonic() < deadline:
            time.sleep(0.3)
        if read_state(pid).get("ps") not in (2, 3):
            click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")
        owner = u(g6.LOCAL_INDEX_VA, 4)
        time.sleep(6)
        owned = g6.live_units(pid, variant, owner)
        worker = next((r for r in owned if r["type"] == 7), min(owned, key=lambda r: r["hp"]))
        worker_base = pool_base + worker["slot"] * g6.UNIT_STRIDE
        supply = SupplyProbe(prefix)
        map_w, map_h = u(0x00B3DE34, 2, True), u(0x00B3DE36, 2, True)

        def calibrate() -> tuple[Any, Any]:
            click(200, 170, drag_to=(730, 445))
            time.sleep(0.4)
            click(120, 90, button=3)
            time.sleep(0.2)
            samples = []
            for point in g6.CALIBRATION_POINTS:
                click(*point, button=3)
                time.sleep(0.2)
                samples.append((point, decode_xy(u(worker_base + g6.UNIT_PENDING_XY_OFFSET, 4))))
            return fit_affine(samples)

        for _attempt in range(3):
            matrix, offset = calibrate()
            if abs(np.linalg.det(matrix)) > 1e-6:
                break
            time.sleep(3)
        else:
            raise ProbeError("calibration failed")
        inverse = np.linalg.inv(matrix)

        def world_to_screen(x: int, y: int) -> tuple[int, int]:
            p = inverse @ (np.array([x, y]) - offset)
            return int(round(p[0])), int(round(p[1]))

        def screen_to_world(x: int, y: int) -> tuple[int, int]:
            w = matrix @ np.array([x, y]) + offset
            return int(round(w[0])), int(round(w[1]))

        planned = []
        for sy in g6.SPARSE_ROWS:
            for sx in g6.SPARSE_COLS:
                wx, wy = screen_to_world(sx, sy)
                if 1 <= wx < map_w - 1 and 1 <= wy < map_h - 1:
                    planned.append((wx, wy))
        for wx, wy in planned:
            receipt = supply.call(op=5, owner=owner, unit_type=g6.ESL2610_SEED_TYPE, x=wx, y=wy, count=1)
            if not receipt.get("ok") or receipt.get("fixture_added") != 1:
                raise ProbeError(f"fixture spawn failed at {(wx, wy)}: {receipt}")
        time.sleep(2)
        fixture = g6.live_units(pid, variant, owner, unit_type=g6.ESL2610_SEED_TYPE)
        screen_of = {r["slot"]: world_to_screen(r["x"], r["y"]) for r in fixture}
        pins = [(sx, sy - 15) for sx, sy in screen_of.values()]
        blank = max(((x, y) for x in range(120, 700, 30) for y in range(110, 440, 20)),
                    key=lambda g: min((g[0] - px) ** 2 + (g[1] - py) ** 2 for px, py in pins))
        result["stages"]["a_start"] = {**record("a_start"), "fixture_units": len(fixture), "blank": list(blank)}
        click(*blank)
        time.sleep(0.4)
        scene_before = shot("a_before_save")
        send_key(display, "Escape", env=env, log=log)
        wait_for(lambda s: s.get("ps") == 23, "pause_for_save")
        click(*PAUSE_SAVE_POINT)
        time.sleep(0.4)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        time.sleep(1.0)
        save_path = game / "save" / SAVE_NAME
        if not save_path.is_file():
            raise ProbeError("save was not created")
        shutil.copy2(save_path, artifact_root / SAVE_NAME)
        result["stages"]["a_save"] = {"sha256": sha256(save_path), "size": save_path.stat().st_size}
        click(*SAVE_MENU_RETURN_POINT)
        click(*RESUME_POINT)
        wait_for(lambda s: s.get("ps") == 3, "resume_after_save")

        def suite(label: str, scene_ref: Path) -> dict[str, Any]:
            out: dict[str, Any] = {**record(f"{label}_loaded")}
            time.sleep(4)
            out["ps_after_4s"] = read_state(proc["pid"]).get("ps")
            out["local_after_4s"] = u(g6.LOCAL_INDEX_VA, 4)
            scene = shot(f"{label}_scene")
            out["scene_diff"] = scene_diff(scene_ref, scene)
            if out["scene_diff"] > SCENE_DIFF_LIMIT:
                out["suite"] = "BLOCKED(camera: scene differs from the calibrated one)"
                return out
            if out["local_after_4s"] != owner:
                out["note"] = f"local {out['local_after_4s']} != fixture owner {owner}: own units are not selectable"

            def deselect() -> None:
                click(*blank)
                time.sleep(0.2)
                if snap()["count"] != 0:
                    raise ProbeError("deselect point selected a unit")

            def isolation_point(slot: int, screen: tuple[int, int]) -> tuple[int, int] | None:
                for dy in g6.CLICK_DY:
                    deselect()
                    click(screen[0], screen[1] + dy)
                    time.sleep(0.3)
                    s = snap()
                    if s["count"] == 1 and s["slots"] == [slot]:
                        return screen[0], screen[1] + dy
                return None

            isolated: list[tuple[int, tuple[int, int]]] = []
            for slot, screen in sorted(screen_of.items(), key=lambda kv: kv[1]):
                if not 5 <= screen[0] <= 795 or not 45 <= screen[1] <= 470:
                    continue
                point = isolation_point(slot, screen)
                if point is not None:
                    isolated.append((slot, point))
                if len(isolated) >= 9:
                    break
            out["isolated"] = len(isolated)
            if len(isolated) < 9:
                out["suite"] = f"BLOCKED(isolated {len(isolated)} < 9; selection of own units)"
                out["selection_after_click_try"] = snap()
                return out
            deselect()
            (a_slot, a_xy), rest = isolated[0], isolated[1:]
            before = snap()
            shift_hold(lambda: click(*a_xy))
            g60 = {"before": before["count"], "after": snap(), "alive": alive()}
            deselect()
            click(*a_xy)
            time.sleep(0.3)
            counts = [snap()["count"]]
            for _slot, xy in rest[:5]:
                shift_hold(lambda xy=xy: click(*xy))
                counts.append(snap()["count"])
            deselect()
            click(*a_xy)
            time.sleep(0.3)
            pair = rest[5:7]
            x0, x1 = sorted(p[1][0] for p in pair)
            y0, y1 = sorted(p[1][1] for p in pair)
            b2 = snap()["count"]
            shift_hold(lambda: click(x0 - 10, y0 - 22, drag_to=(x1 + 10, y1 + 8)))
            out["g6_0"] = {"before": g60["before"], "after_count": g60["after"]["count"],
                           "after_slots": g60["after"]["slots"], "expect_slot": a_slot, "alive": g60["alive"]}
            out["g6_1_counts"] = counts
            out["g6_2"] = [b2, snap()["count"]]
            out["alive_end"] = alive()
            out["verdict"] = {
                "g6_0_adds": g60["before"] == 0 and g60["after"]["slots"] == [a_slot] and g60["alive"],
                "g6_1_grows": counts == [1, 2, 3, 4, 5, 6], "g6_1_stuck": counts == [1] * 6,
                "g6_2_control_grows": out["g6_2"][1] >= out["g6_2"][0] + 2, "alive": out["alive_end"]}
            return out

        # ---------------- B: in-game load (same process)
        send_key(display, "Escape", env=env, log=log)
        wait_for(lambda s: s.get("ps") == 23, "pause_for_load")
        click(*PAUSE_LOAD_POINT)
        time.sleep(0.4)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        load = _load_status(proc["game"], pid, wait_for)
        result["stages"]["b_ingame_load"] = {"load": {k: load[k] for k in ("status", "crashed", "timed_out", "error")}}
        if load["status"] == "PASS":
            time.sleep(0.5)
            result["stages"]["b_ingame_load"].update(suite("b", scene_before))
        stop_game()

        # ---------------- C: new process, title load
        launch()
        pid = proc["pid"]
        result["stages"]["c_title"] = record("c_title_before_load")
        click(*LOAD_MENU)
        time.sleep(1.0)
        if read_state(pid).get("ps") == 9:
            click(*LOAD_MENU)
        wait_for(lambda s: s.get("ps") == 35, "ps35")
        target_row, navigation = title_list_index(SAVE_NAME), []
        for _ in range(20):
            current = u(SELECTED_INDEX_ADDRESS, 2)
            navigation.append(current)
            if current == target_row:
                break
            subprocess.run([sys.executable, str(REPO / "tools/x11_send_keys.py"), "--display", display, "DOWN"],
                           env=env, stdout=log, stderr=log, timeout=10, check=True)
            time.sleep(0.3)
        else:
            raise ProbeError(f"title list navigation did not reach {target_row}: {navigation}")
        click(*LOAD_CONFIRM)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "title_loaded_ps3", 90)
        time.sleep(0.5)
        result["stages"]["c_title_load"] = {"navigation": navigation, **suite("c", scene_before)}
        result["status"] = "COMPLETE"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError, StopIteration,
            runtime_env.RuntimeSafetyError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
        if display:
            capture(display, artifact_root / f"{time.strftime('%Y%m%d_%H%M%S')}_failure.png", log)
    finally:
        result["game_alive_before_cleanup"] = bool(proc) and proc["game"].poll() is None
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
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=sorted(g6.ESL2610_VARIANTS), required=True)
    parser.add_argument("--seat", type=int, default=2)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.variant, args.seat, args.runtime_root, args.artifact_root)
    print(json.dumps({"status": result.get("status"), "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
