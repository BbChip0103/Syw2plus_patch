#!/usr/bin/env python3
"""G5 checklist C survey: what do the worker's V/I/F command-grid buttons and
the HQ's F1..F11 slots actually do (건설/특수능력/변신/승선-하선 groundwork).

STATUS 2026-09-28 07:35 operator direction asks the next work session to
finish checklist (C) construction/special-ability-transform/embark-disembark
in one probe. Those three items cannot be automated blind: unlike
move/stop/hold/patrol/gather/repair (all discovered from a fixed, already
mapped button layout, ``g5_command_coverage_probe.BUTTONS``), this EXE's
command grid is drawn per selected unit *type* and lap726's capture
(``01-after-minimap-calibration.png``, worker alone selected) shows the lone
worker's grid is **not** the 5-button {stop,move,attack,patrol,hold} set used
for the SEED_TYPE=2 combat fixture -- it is 5 buttons labelled S, M, V, I, F
(row1: S,M,V,I at (667,503)/(703,503)/(740,503)/(777,503); row2: F at
(667,538)). This debug EXE prints the bound hotkey letter on every button (see
``g5_command_coverage_probe`` module docstring), so S/M are confirmed
stop/move by position parity with the combat grid, but V/I/F have no prior
measurement anywhere in this repo.

This probe is read-only survey, not a v5 regression check (construction/
ability/embark are per-unit or per-structure actions, not selection-array
broadcast, so they are not expected to interact with the v3/v4/v5 selection
capacity patch at all -- the checklist's concern per the 2026-09-28 06:55
operator note is existence/parity, "1기만 받는 명령이면 원본과 동일 여부만").
It only runs against the protected original, once:

1. Boot solo lobby (identical sequence to every other G5 checklist probe).
2. Select the lone worker, capture its command grid, then click V, I, F in
   turn (returning to a clean idle state between each with the S/stop
   button), recording: the worker's own command/pending-command/pending-xy
   fields before and 1.5s after each click, whether the click left the
   button in an armed ("awaiting a follow-up ground click", like patrol/
   attack-move) state by probing a subsequent ground left-click and
   re-reading state, and a screenshot each time.
3. Locate the HQ (``g5_worker_repair_command_probe.find_hq_slot``), select it
   with a screen click at its calibrated position, and capture its command
   grid (including the F1..F11 production-slot row) to see whether any
   buildable-unit/building icon appears there -- this engine's construction
   model may live on the HQ's grid rather than the worker's, or may not
   exist as a player action at all (only the AI production tables
   ``analysis/memory_maps/ai_production_decision_path_00406770_20260923.md``
   document *AI* build gating; no prior lap found a player-facing "place a
   building" flow).
4. Record findings; this probe does not assert PASS/FAIL, it produces raw
   evidence for the checklist author (this same lap) to classify each of
   건설/특수능력·변신/승선·하선 as PASS, N/A (with reason), or a new probe
   target.

The protected original is only read (SHA before/after).
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
# Confirmed by parity with g5_command_coverage_probe.BUTTONS (stop/move share
# the same (667,503)/(703,503) cells across unit types); V/I/F are new.
WORKER_BUTTONS = {"stop": (667, 503), "move": (703, 503), "v": (740, 503), "i": (777, 503), "f": (667, 538)}
HQ_FOOTPRINT_OFFSET_CANDIDATES = [
    (0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1),
    (2, 1), (1, 2), (2, 2), (-2, 0), (0, -2), (2, 0), (0, 2),
]


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
        "schema": "syw2plus.g5-worker-ability-hq-ui-survey.v1", "variant": "original", "status": "UNKNOWN",
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
        snap("00-worker-selected-command-grid")

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

        def worker_state() -> dict[str, Any]:
            return {
                "command": int.from_bytes(read_memory(pid, wbase + 0x290, 2), "little", signed=True),
                "pending": hex(int.from_bytes(read_memory(pid, wbase + 0x384, 4), "little")),
                "pending_xy": list(worker_pending_xy()),
            }

        def reselect_worker_only() -> None:
            click(*DRAG_START, drag_to=DRAG_END)
            time.sleep(0.6)

        # find a nearby ground tile (worker-relative) to use as a "follow-up
        # click" probe target for buttons that might arm a targeted mode.
        wx, wy = int(worker["x"]), int(worker["y"])
        ground_screen = w2s((wx + 4, wy - 4))

        for name, pt in WORKER_BUTTONS.items():
            if name in ("stop", "move"):
                continue  # already fully characterized by every prior checklist probe
            reselect_worker_only()
            xdo("key", "s")
            time.sleep(0.4)
            before = worker_state()
            click(*pt)
            time.sleep(1.5)
            after = worker_state()
            snap(f"01-button-{name}-after-click")
            click(*ground_screen, button=3)
            time.sleep(1.0)
            after_ground = worker_state()
            snap(f"02-button-{name}-after-ground-followup")
            result["button_probes"][name] = {
                "screen": list(pt), "before": before, "after_click": after,
                "after_ground_followup": after_ground, "alive": alive(),
            }
            if not alive():
                raise ProbeError(f"game not alive after button {name}")

        # --- HQ selection: click the HQ's own tile and capture its grid.
        xdo("key", "s")
        time.sleep(0.4)
        hq_search: list[dict[str, Any]] = []
        hq_screen: list[int] | None = None
        for off in HQ_FOOTPRINT_OFFSET_CANDIDATES:
            world = (int(hq["x"]) + off[0], int(hq["y"]) + off[1])
            screen = list(w2s(world))
            if not (0 < screen[0] < 790 and 45 < screen[1] < 465):
                continue
            click(*screen)
            time.sleep(0.6)
            s = sel()
            selected_hq = hq["slot"] in s["slots"]
            hq_search.append({"offset": list(off), "world": list(world), "screen": screen,
                              "selection": s, "selected_hq": selected_hq})
            if selected_hq and hq_screen is None:
                hq_screen = screen
                snap("03-hq-selected-command-grid")
        result["hq_selection_search"] = hq_search
        result["hq_screen"] = hq_screen
        if hq_screen is None:
            result["hq_selection_note"] = "no offset selected the HQ by left-click; command grid not captured"

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
    return 0 if res.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
