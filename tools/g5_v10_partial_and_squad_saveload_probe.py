#!/usr/bin/env python3
"""G5 v10 supplementary save/load measurement (lap757 work, 2026-09-29 09:55
operator instruction item (1)): mid-range unassigned selection counts and a
selection mixed with an existing control group (Ctrl+number squad), neither
of which lap756's v10 runtime evidence exercised (it only measured a full
50-unit drag).

v10 (``patches/selection/g5_selection_cap50_v10.py``) does not special-case
``count`` at all -- on save it unconditionally appends the live count dword
plus all 50 entry dwords after the legacy mirror call, and on load (magic
present) it overwrites the full 204-byte array and then clamps count to 50.
So the mid-range case is expected to behave identically to the already-PASS
50-unit case; this probe exists to confirm that empirically rather than
leave it as an unmeasured inference, and to check the orthogonal control-
group subsystem (``GROUP1_BASE_ADDRESS`` / unit+0x344``, a completely
separate storage path the original engine already owns) for any
interaction/corruption when a squad and an oversized live selection are
both live at save time.

Two rounds in one boot, using the same exact per-unit click+shift-click
multi-select technique ``g5_group_shift_add_death_recall_probe`` already
validated (drag geometry cannot hit an exact count, see that module's
docstring):

- Round A (unassigned mid-count): select exactly 25 units, no group. Save,
  deselect, load. PASS = selection count/slots after load == before save.
- Round B (squad mixed with a mid/large count): define group 1 from 15
  units (Ctrl+1), deselect, then select a *different* 35-unit set (no group
  reassignment) so the live selection at save time is unassigned and does
  not equal the squad membership. Save, deselect, load. PASS = (a) selection
  count/slots after load == the 35-unit set saved, (b) pressing "1" recalls
  exactly the original 15-member squad (group storage round-tripped
  independently of the oversized live selection saved alongside it).

Read-only diagnostics on top of the existing G5 runtime harness; no product
EXE/original bytes are modified by this probe itself.
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

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from patches.selection import g5_selection_cap50_v10 as g5  # noqa: E402
from tools import runtime_env  # noqa: E402
from tools.g5_candidate_drag_probe import (  # noqa: E402
    ProbeError, DRAG_START, DRAG_END, STOCK_SELECTION_BASE,
    SEED_TYPE, VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    selection_snapshot, unit_snapshot, fixture_units, fixture_unit_group_snapshot,
    control_group_snapshot, sha256, write_json, capture, send_key,
    PAUSE_SAVE_POINT, PAUSE_LOAD_POINT, SAVE_SLOT_POINT, SAVE_ACTION_POINT,
    SAVE_MENU_RETURN_POINT, RESUME_POINT,
)
from tools.g5_r3_sparse_selection_probe import Bridge  # noqa: E402
from tools.g5_screen_world_calibration import decode_xy, fit_affine  # noqa: E402
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK  # noqa: E402
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS  # noqa: E402
from patches.population.runtime_driver import read as read_memory  # noqa: E402
from patches.population.runtime_driver import state as read_state  # noqa: E402

ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
V10_SHA = "c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad"
SEL_BASE = g5.SELECTION_BASE
SEL_CAP = g5.TARGET_CAPACITY
ROUND_A_COUNT = 25
ROUND_B_SQUAD_COUNT = 15
ROUND_B_LIVE_COUNT = 35
# Same 7x9 pool (worker's own row excluded) g5_group_shift_add_death_recall_probe
# uses, sized comfortably above round B's 35 so isolation-check attrition from
# terrain/HQ obstruction cannot starve either round.
CANDIDATE_DX = tuple(range(-3, 4))
CANDIDATE_DY = (-4, -3, -2, -1, 1, 2, 3, 4, 5)


def candidate_cells() -> list[tuple[int, int]]:
    return [(dx, dy) for dy in CANDIDATE_DY for dx in CANDIDATE_DX]


def run(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
    candidate_bytes, _ = g5.build_candidate(source_exe.read_bytes())
    bridge_dir = artifact_root / "bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
    )
    bridge_dll = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge_dll, timeout=60)
    game = Path(cast(str, cast(Mapping, manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping, manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private copy pre-install check failed")
    private_exe.write_bytes(candidate_bytes)
    private_sha = sha256(private_exe)
    if private_sha != V10_SHA:
        raise ProbeError(f"v10 candidate SHA mismatch: {private_sha}")

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-v10-partial-and-squad-saveload.v1", "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": private_sha, "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [], "inputs": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
    game_proc: Any = None
    try:
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid
        bridge = Bridge(prefix)

        def alive() -> bool:
            if game_proc.poll() is not None:
                return False
            try:
                return int(read_state(pid).get("ps", -1)) == 3
            except (OSError, ValueError, ProbeError):
                return False

        def wait_for(pred, label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = read_state(pid)
                    if pred(last):
                        return last
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": str(exc)}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda s: s.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        crop = (int(info["x"]), int(info["y"]))

        def xdo(*args: str) -> None:
            subprocess.run(["xdotool", *args], env=env, stdout=log, stderr=log, timeout=10, check=True)

        def click(x: int, y: int, *, button: int = 1, mod: str | None = None) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if mod:
                xdo("keydown", mod)
                time.sleep(0.15)
            try:
                subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            finally:
                if mod:
                    time.sleep(0.15)
                    xdo("keyup", mod)
            result["inputs"].append({"x": x, "y": y, "button": button, "mod": mod})

        def press(key: str, mod: str | None = None) -> None:
            xdo("key", f"{mod}+{key}" if mod else key)
            result["inputs"].append({"key": key, "mod": mod})

        def snap(name: str) -> None:
            result["captures"].append(capture(display, artifact_root / f"{name}.png", log))

        def sel() -> dict[str, Any]:
            s = selection_snapshot(pid, base=SEL_BASE, capacity=SEL_CAP)
            s["legacy_count"] = int.from_bytes(read_memory(pid, STOCK_SELECTION_BASE, 4), "little", signed=True)
            return s

        xdo("windowfocus", outer)
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")

        def selector() -> Any:
            return runtime_env._read_lobby_selector(lambda a, n: read_memory(pid, a, n)).get("selected")

        if selector() == "solo":
            click(344, 169)
            time.sleep(0.5)
        click(462, 169)
        deadline = time.monotonic() + 10
        while selector() != "solo" and time.monotonic() < deadline:
            time.sleep(0.2)
        if selector() != "solo":
            raise ProbeError("solo selector did not settle")
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if runtime_env._read_local_ready_state(lambda a, n: read_memory(pid, a, n)).get("ready_value") == 1:
                break
            time.sleep(0.2)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected worker: {worker}")
        result["worker"] = worker
        click(*MINIMAP_CLICK)
        time.sleep(1)
        snap("00-after-minimap")

        click(*DRAG_START)
        subprocess.run(
            [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
             str(crop[0] + DRAG_START[0]), str(crop[1] + DRAG_START[1]), "--button", "1",
             "--drag-to", str(crop[0] + DRAG_END[0]), str(crop[1] + DRAG_END[1])],
            env=env, stdout=log, stderr=log, timeout=10, check=True,
        )
        time.sleep(1)
        cal_sel = sel()
        if VISIBLE_WORKER_SLOT not in cal_sel["slots"]:
            raise ProbeError(f"worker not selected for calibration: {cal_sel}")
        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

        def worker_pending_xy() -> tuple[int, int]:
            return decode_xy(int.from_bytes(read_memory(pid, wbase + UNIT_PENDING_XY_OFFSET, 4), "little"))

        samples = []
        for pt in CALIBRATION_SCREEN_POINTS:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + pt[0]), str(crop[1] + pt[1]), "--button", "3"]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            time.sleep(0.4)
            samples.append((pt, worker_pending_xy()))
        matrix, offset = fit_affine(samples)
        resid = max(float(np.max(np.abs(matrix @ np.array(p) + offset - np.array(w)))) for p, w in samples)
        result["screen_calibration"] = {"max_abs_residual": resid}
        minv = np.linalg.inv(matrix)

        def w2s(world: tuple[float, float]) -> tuple[int, int]:
            p = minv @ (np.array(world) - offset)
            return int(round(p[0])), int(round(p[1]))

        wx, wy = int(worker["x"]), int(worker["y"])

        requested: list[dict[str, Any]] = []
        for dx, dy in candidate_cells():
            world = (wx + dx, wy + dy)
            if not (0 <= world[0] < 180 and 0 <= world[1] < 180):
                continue
            r = bridge.call(op=5, owner=0, type_=SEED_TYPE, rice=world[0], wood=world[1], used=1)
            if not r.get("ok") or r.get("fixture_added") != 1:
                raise ProbeError(f"fixture spawn failed at {world}: {r}")
            requested.append({"dx": dx, "dy": dy, "world": list(world)})
        time.sleep(1)
        snap("01-after-fixture")

        fixture = fixture_units(pid)
        by_xy = {(u["x"], u["y"]): u["slot"] for u in fixture}
        for entry in requested:
            entry["slot"] = by_xy.get(tuple(entry["world"]))
        resolved = [e for e in requested if e["slot"] is not None]
        result["spawn_pool"] = {"requested": len(requested), "resolved": len(resolved)}
        if len(resolved) < ROUND_B_SQUAD_COUNT + ROUND_B_LIVE_COUNT:
            raise ProbeError(f"too few resolved candidates: {len(resolved)}")

        dgx = wx - 8 if wx >= 8 else wx + 8
        dgy = wy - 8 if wy >= 8 else wy + 8
        deselect_pt = w2s((dgx, dgy))

        def do_deselect() -> None:
            click(*deselect_pt)
            time.sleep(0.4)

        def unit_screen(entry: Mapping[str, Any]) -> tuple[int, int]:
            return w2s(cast(tuple[int, int], tuple(entry["world"])))

        click_dy = None
        for dy in (-12, -20, -6, 0, -28):
            do_deselect()
            ux, uy = unit_screen(resolved[0])
            click(ux, uy + dy)
            time.sleep(0.5)
            s = sel()
            if s["count"] == 1 and s["slots"] == [resolved[0]["slot"]]:
                click_dy = dy
                break
        result["click_dy"] = click_dy
        if click_dy is None:
            raise ProbeError("no click offset gave an isolated single-unit selection")

        isolated: list[dict[str, Any]] = []
        for entry in resolved:
            do_deselect()
            ux, uy = unit_screen(entry)
            click(ux, uy + click_dy)
            time.sleep(0.4)
            s = sel()
            if s["count"] == 1 and s["slots"] == [entry["slot"]]:
                isolated.append(entry)
            if len(isolated) >= ROUND_B_SQUAD_COUNT + ROUND_B_LIVE_COUNT:
                break
        result["isolated_count"] = len(isolated)
        if len(isolated) < ROUND_B_SQUAD_COUNT + ROUND_B_LIVE_COUNT:
            raise ProbeError(f"not enough isolated candidates: {len(isolated)}")

        def multiselect(entries: list[Mapping[str, Any]]) -> dict[str, Any]:
            do_deselect()
            ux, uy = unit_screen(entries[0])
            click(ux, uy + click_dy)
            time.sleep(0.25)
            for entry in entries[1:]:
                ux, uy = unit_screen(entry)
                click(ux, uy + click_dy, mod="shift")
                time.sleep(0.25)
            return sel()

        def do_save() -> dict[str, Any]:
            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda s: s.get("ps") == 23, "pause_for_save")
            click(*PAUSE_SAVE_POINT)
            time.sleep(0.5)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            time.sleep(0.8)
            save_path = game / "save" / "save001.dat"
            if not save_path.is_file():
                raise ProbeError(f"private save was not created: {save_path}")
            info = {"sha256": sha256(save_path), "size": save_path.stat().st_size}
            click(*SAVE_MENU_RETURN_POINT)
            click(*RESUME_POINT)
            wait_for(lambda s: s.get("ps") == 3, "resume_after_save")
            return info

        def do_load() -> None:
            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda s: s.get("ps") == 23, "pause_for_load")
            click(*PAUSE_LOAD_POINT)
            time.sleep(0.5)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "load_complete", 90)
            time.sleep(0.5)

        # --- Round A: unassigned mid-count (25), no group.
        round_a: dict[str, Any] = {}
        a_before = multiselect(isolated[:ROUND_A_COUNT])
        round_a["before_save"] = a_before
        snap("02-round-a-before-save")
        if a_before["count"] != ROUND_A_COUNT or len(set(a_before["slots"])) != ROUND_A_COUNT:
            raise ProbeError(f"round A pre-save selection wrong: {a_before}")
        round_a["save"] = do_save()
        do_deselect()
        do_load()
        a_after = sel()
        round_a["after_load"] = a_after
        snap("03-round-a-after-load")
        round_a["pass"] = (
            a_after["count"] == ROUND_A_COUNT
            and set(a_after["slots"]) == set(a_before["slots"])
            and len(set(a_after["slots"])) == ROUND_A_COUNT
        )
        result["round_a"] = round_a
        if not alive():
            raise ProbeError("game not alive after round A")

        # --- Round B: pre-existing 15-unit squad (group 1), then a different
        # unassigned 35-unit live selection at save time.
        round_b: dict[str, Any] = {}
        do_deselect()
        squad_entries = isolated[:ROUND_B_SQUAD_COUNT]
        squad_sel = multiselect(squad_entries)
        if squad_sel["count"] != ROUND_B_SQUAD_COUNT:
            raise ProbeError(f"round B squad pre-select wrong: {squad_sel}")
        press("1", mod="ctrl")
        time.sleep(0.5)
        group_after_assign = control_group_snapshot(pid)
        fixture_group_after_assign = fixture_unit_group_snapshot(pid, squad_entries)
        squad_members_engine = {row["slot"] for row in fixture_group_after_assign["rows"] if row["group"] == 1}
        round_b["group_after_assign"] = {
            "control_group": group_after_assign, "engine_members": sorted(squad_members_engine),
        }
        if squad_members_engine != {e["slot"] for e in squad_entries}:
            raise ProbeError(f"group1 assign mismatch: {sorted(squad_members_engine)}")
        snap("04-round-b-after-squad-assign")

        live_entries = isolated[ROUND_B_SQUAD_COUNT:ROUND_B_SQUAD_COUNT + ROUND_B_LIVE_COUNT]
        b_before = multiselect(live_entries)
        round_b["before_save"] = b_before
        snap("05-round-b-before-save")
        if b_before["count"] != ROUND_B_LIVE_COUNT or len(set(b_before["slots"])) != ROUND_B_LIVE_COUNT:
            raise ProbeError(f"round B pre-save live selection wrong: {b_before}")
        overlap = {e["slot"] for e in live_entries} & squad_members_engine
        round_b["live_selection_overlaps_squad"] = sorted(overlap)

        round_b["save"] = do_save()
        do_deselect()
        do_load()
        b_after_live = sel()
        round_b["after_load_live_selection"] = b_after_live
        snap("06-round-b-after-load")
        live_pass = (
            b_after_live["count"] == ROUND_B_LIVE_COUNT
            and set(b_after_live["slots"]) == set(b_before["slots"])
            and len(set(b_after_live["slots"])) == ROUND_B_LIVE_COUNT
        )
        round_b["live_selection_pass"] = live_pass
        if not alive():
            raise ProbeError("game not alive after round B load")

        do_deselect()
        press("1")
        time.sleep(0.6)
        recalled = sel()
        round_b["squad_recall_after_load"] = recalled
        snap("07-round-b-squad-recall")
        squad_pass = (
            recalled["count"] == ROUND_B_SQUAD_COUNT
            and set(recalled["slots"]) == {e["slot"] for e in squad_entries}
        )
        round_b["squad_recall_pass"] = squad_pass
        round_b["pass"] = bool(live_pass and squad_pass)
        result["round_b"] = round_b
        if not alive():
            raise ProbeError("game not alive after squad recall")

        result["status"] = "PASS" if (round_a["pass"] and round_b["pass"]) else "FAIL"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError) as exc:
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
        subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        subprocess.run(["wineserver", "-w"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
                xvfb.wait(timeout=5)
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix)}
        result["cleanup"]["ok"] = not result["cleanup"]["prefix_processes_after"]
        result["source_sha_after"] = sha256(source_exe)
        result["source_unchanged"] = result["source_sha_after"] == ORIGINAL_SHA
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "PASS" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
