#!/usr/bin/env python3
"""G5 checklist C survey, part 2: what do the HQ's R/D/T/F/C/X/Z command-grid
buttons do (construction/production), following up on
``g5_worker_ability_hq_ui_survey_probe`` (lap731 run1).

Run1 found the lone worker's own grid (unit_type varies per boot -- solo
lobby nation is randomized, lap730) has no construction-looking icon: this
boot's worker (type 31) showed only S(stop)/M(move)/V("묻기", tooltip
confirmed)/F("불끄기", tooltip confirmed) -- a farm-tool bind action and a
fire-extinguish action, neither resembling "place a building". The HQ's own
grid, captured when clicking the HQ's own tile, has 8 filled buttons instead
of the combat-fixture's 5 or the worker's 4: row1 S/R/D/T, row2 F/C/X/Z,
where R is a hammer icon (the conventional "construct" glyph in this genre)
and F/C/X/Z are unit-portrait icons (wolf-head/helmet/gray-figure/mounted
rider -- looks like a production choice list, not a per-unit ability).

This probe tests that hypothesis directly, cheapest and least destructive
button first: click the HQ, then for each of R, D, F, C, X, Z (T -- the red
crossed-swords icon -- is tested **last** since it looks like "disband/raze"
and may end the match) capture a tooltip screenshot, snapshot the 1200-slot
owner/type existence table before/after, and (for R specifically) try a
follow-up left-click on nearby open ground to see whether a placement mode
was armed. This is read-only-intent (the protected original is only read,
SHA before/after) but necessarily exploratory: a genuinely destructive button
in this list is expected and accepted (isolated throwaway prefix/copy).
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

from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    selection_snapshot, unit_snapshot,
    sha256, write_json, capture,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS
from tools.g5_worker_repair_command_probe import find_hq_slot
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
EXISTS_TABLE = 0x008990C8
HQ_BUTTONS = {
    "r": (703, 503), "d": (740, 503),
    "f": (667, 538), "c": (703, 538), "x": (740, 538), "z": (777, 538),
    "t": (777, 503),
}
BUTTON_ORDER = ["r", "d", "f", "c", "x", "z", "t"]  # t (looks destructive) last
HQ_FOOTPRINT_OFFSET_CANDIDATES = [
    (0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1),
    (2, 1), (1, 2), (2, 2), (-2, 0), (0, -2), (2, 0), (0, 2),
]


def existing_slots(pid: int) -> set[int]:
    exists = read_memory(pid, EXISTS_TABLE, 1200 * 2)
    return {slot for slot in range(1200) if int.from_bytes(exists[slot * 2:slot * 2 + 2], "little") != 0}


def slot_info(pid: int, slot: int) -> dict[str, Any]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "unit_type": int.from_bytes(read_memory(pid, base + 0x8D, 1), "little"),
        "owner": int.from_bytes(read_memory(pid, base + 0x8E, 1), "little"),
        "x": int.from_bytes(read_memory(pid, base + 0x2A2, 2), "little", signed=True),
        "y": int.from_bytes(read_memory(pid, base + 0x2A4, 2), "little", signed=True),
    }


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
    bridge_dir = artifact_root / "stock_bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
                   cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge, timeout=60)
    game = Path(cast(str, cast(Mapping, manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping, manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private copy pre-install check failed")

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-hq-command-grid-survey.v1", "variant": "original", "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": sha256(private_exe), "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [], "inputs": [], "button_probes": {},
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

        def alive() -> bool:
            if game_proc.poll() is not None:
                return False
            try:
                read_state(pid)
                return True
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

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "drag_to": list(drag_to) if drag_to else None, "button": button})

        def snap(name: str) -> None:
            result["captures"].append(capture(display, artifact_root / f"{name}.png", log))

        def sel() -> dict[str, Any]:
            return selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)

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
        if worker["owner"] != 0 or worker["unit_type"] == 0:
            raise ProbeError(f"slot1198 is not the expected worker: {worker}")
        result["worker"] = worker
        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

        hq = find_hq_slot(pid, VISIBLE_WORKER_SLOT)
        result["hq"] = hq

        click(*MINIMAP_CLICK)
        time.sleep(1)

        # --- screen calibration (worker only), same method as every other checklist probe.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        cal_sel = sel()
        if VISIBLE_WORKER_SLOT not in cal_sel["slots"]:
            raise ProbeError(f"worker not selected for calibration: {cal_sel}")

        def worker_pending_xy() -> tuple[int, int]:
            return decode_xy(int.from_bytes(read_memory(pid, wbase + UNIT_PENDING_XY_OFFSET, 4), "little"))

        samples = []
        for pt in CALIBRATION_SCREEN_POINTS:
            click(*pt, button=3)
            time.sleep(0.4)
            samples.append((pt, worker_pending_xy()))
        matrix, offset = fit_affine(samples)
        resid = max(float(np.max(np.abs(matrix @ np.array(p) + offset - np.array(w)))) for p, w in samples)
        result["screen_calibration"] = {"max_abs_residual": resid}
        minv = np.linalg.inv(matrix)

        def w2s(world: tuple[int, int]) -> tuple[int, int]:
            p = minv @ (np.array(world) - offset)
            return int(round(p[0])), int(round(p[1]))

        xdo("key", "s")
        time.sleep(0.4)

        # --- select the HQ.
        hq_screen: list[int] | None = None
        for off in HQ_FOOTPRINT_OFFSET_CANDIDATES:
            world = (int(hq["x"]) + off[0], int(hq["y"]) + off[1])
            screen = list(w2s(world))
            if not (0 < screen[0] < 790 and 45 < screen[1] < 465):
                continue
            click(*screen)
            time.sleep(0.6)
            s = sel()
            if hq["slot"] in s["slots"]:
                hq_screen = screen
                break
        result["hq_screen"] = hq_screen
        if hq_screen is None:
            raise ProbeError("could not select the HQ by left-click")
        snap("00-hq-selected-baseline")
        baseline_slots = existing_slots(pid)
        result["baseline_slot_count"] = len(baseline_slots)

        # a nearby open-ground screen point for placement/target follow-ups
        open_ground = w2s((int(hq["x"]) - 4, int(hq["y"]) + 5))

        for name in BUTTON_ORDER:
            pt = HQ_BUTTONS[name]
            before_slots = existing_slots(pid)
            click(*pt)
            time.sleep(1.0)
            snap(f"01-hq-button-{name}-tooltip")
            after_click_slots = existing_slots(pid)
            still_alive = alive()
            entry: dict[str, Any] = {
                "screen": list(pt), "alive_after_click": still_alive,
                "new_slots_after_click": sorted(after_click_slots - before_slots),
            }
            if still_alive and name in ("r",):
                # candidate "construct" button: try a follow-up placement click
                click(*open_ground)
                time.sleep(1.5)
                snap(f"02-hq-button-{name}-after-ground-followup")
                after_followup_slots = existing_slots(pid)
                new = sorted(after_followup_slots - before_slots)
                entry["new_slots_after_ground_followup"] = new
                entry["new_slot_details"] = [slot_info(pid, s) for s in new]
                entry["alive_after_followup"] = alive()
            result["button_probes"][name] = entry
            if not entry.get("alive_after_followup", still_alive):
                result["status"] = "PARTIAL_MATCH_ENDED"
                break
            # reselect the HQ before the next button (some buttons may have
            # changed selection, e.g. spawning and auto-selecting a unit).
            click(*hq_screen)
            time.sleep(0.5)

        if result["status"] == "UNKNOWN":
            result["status"] = "COMPLETE"
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
            xvfb.wait(timeout=5)
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix)}
        result["source_sha_after"] = sha256(source_exe)
        result["source_unchanged"] = result["source_sha_after"] == ORIGINAL_SHA
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    ap.add_argument("--runtime-root", type=Path, required=True)
    ap.add_argument("--artifact-root", type=Path, required=True)
    args = ap.parse_args(argv)
    res = run_probe(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps({k: res.get(k) for k in ("status", "error", "source_unchanged")}, ensure_ascii=False))
    return 0 if res.get("status") in ("COMPLETE", "PARTIAL_MATCH_ENDED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
