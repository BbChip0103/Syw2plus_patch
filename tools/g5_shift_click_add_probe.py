#!/usr/bin/env python3
"""G5 checklist B isolated Shift+click individual-add probe.

2026-09-28 05:36 operator direction: lap727 raw showed original
``shift_click_unit``=2 -> ``shift_click_second_unit``=3 (both +1) while v5
showed 1 -> 2 (both +1 too), and the +1-both-times fact was judged a
provisional non-defect (same increment either way) -- but the *starting*
count of 2 for a single plain click on ``anchor1`` in the original is itself
suspicious of sprite overlap in the dense 55-unit/1-tile-pitch fixture
(lap726 already documented this artifact for a different pair).  This probe
removes that ambiguity by construction instead of arguing about it after the
fact: it spawns only a handful of SEED_TYPE units at wide (>=3 tile) spacing,
positively verifies with a plain click that each one is click-isolated
(selects exactly that slot and no other) *before* any Shift step runs, then
Shift-clicks five of them in sequence onto an already-selected first unit and
records the live selection count and slot set after every single step.  A
real per-click add shows count increasing by exactly 1 and the clicked slot
joining the selection at each step; a broken add would show the count
failing to increase (or the wrong slot appearing) despite the click being
click-isolated.

Reuses the same solo-lobby / dense-fixture-adjacent bootstrap and worker
screen<->world calibration as ``g5_command_coverage_probe`` and
``g5_worker_relative_move_attack_probe`` (same seed1-style solo PS3 session,
same 9-point right-click affine fit).  The protected original is only read
(SHA before/after); the candidate is rebuilt from it and SHA-verified against
the pinned v5 hash.
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

from patches.selection import g5_selection_cap50_v5 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, SupplyProbe, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    SEED_TYPE, VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    UNIT_X_OFFSET, UNIT_Y_OFFSET, selection_snapshot, unit_snapshot, fixture_units,
    sha256, write_json, capture,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
# v5 (lap723 R3 fix); pinned SHA reconfirmed by lap724/725/726/727.
TARGET_SHA = "29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146"

# Wide, sparse offsets (tile units) around the worker -- pairwise Manhattan
# distance >=3, unlike the dense 7x8 / 1-tile-pitch G5 fixture that lap726/727
# blamed for sprite overlap at a single click point. More candidates than the
# 6 needed so a failed isolation check (below) can fall back to a spare.
CANDIDATE_OFFSETS = [
    (-3, -3), (3, -3), (-3, 4), (3, 4), (0, -3), (0, 4),
    (-3, 0), (3, 0), (-3, 1), (3, 1),
]
NEEDED = 6


def read_row(pid: int, slot: int) -> dict[str, int]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    block = read_memory(pid, base + 0x290, 0x100)
    return {
        "slot": slot,
        "command": int.from_bytes(block[0:2], "little", signed=True),
        "pending": int.from_bytes(block[0xF4:0xF8], "little"),
        "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
        "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
    }


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
    candidate_bytes: bytes | None = None
    if variant == "candidate":
        candidate_bytes = g5.build_candidate(source_exe.read_bytes())[0]
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
    if candidate_bytes is not None:
        private_exe.write_bytes(candidate_bytes)
    private_sha = sha256(private_exe)
    if variant == "candidate" and private_sha != TARGET_SHA:
        raise ProbeError(f"candidate SHA mismatch: {private_sha}")
    sel_base = g5.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    sel_cap = g5.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-shift-click-add.v1", "variant": variant, "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": private_sha, "game_root": str(game), "run_dir": str(game.parent)},
        "candidates": [], "steps": [], "captures": [], "inputs": [],
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

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1,
                  mod: str | None = None) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            if mod:
                xdo("keydown", mod)
                time.sleep(0.15)
            try:
                subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            finally:
                if mod:
                    time.sleep(0.15)
                    xdo("keyup", mod)
            result["inputs"].append({"x": x, "y": y, "drag_to": list(drag_to) if drag_to else None,
                                     "button": button, "mod": mod})

        def snap(name: str) -> None:
            result["captures"].append(capture(display, artifact_root / f"{name}.png", log))

        def sel() -> dict[str, Any]:
            s = selection_snapshot(pid, base=sel_base, capacity=sel_cap)
            if variant == "candidate":
                legacy = int.from_bytes(read_memory(pid, STOCK_SELECTION_BASE, 4), "little", signed=True)
                s["legacy_count"] = legacy
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
        supply = SupplyProbe(prefix)
        click(*MINIMAP_CLICK)
        time.sleep(1)
        snap("00a-after-minimap-leftclick-legacy-point")

        # --- screen calibration (worker only), same method as lap682/717/723.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        cal_sel = sel()
        if VISIBLE_WORKER_SLOT not in cal_sel["slots"]:
            raise ProbeError(f"worker not selected for calibration: {cal_sel}")
        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

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

        wx, wy = int(worker["x"]), int(worker["y"])

        # --- spawn the sparse, wide-pitch candidate units and keep only the
        # ones that land on-screen with the current camera (no panning).
        onscreen: list[dict[str, Any]] = []
        for off in CANDIDATE_OFFSETS:
            world = (wx + off[0], wy + off[1])
            screen = w2s(world)
            fits = 0 < screen[0] < 790 and 45 < screen[1] < 465
            entry: dict[str, Any] = {"offset": list(off), "world": list(world), "screen": list(screen), "onscreen": fits}
            if fits:
                r = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=world[0], y=world[1], count=1)
                entry["spawn_ok"] = bool(r.get("ok")) and r.get("fixture_added") == 1
            result["candidates"].append(entry)
            if fits:
                onscreen.append(entry)
        time.sleep(1)
        snap("00-after-sparse-fixture")

        fixture = fixture_units(pid)
        by_xy = {(u["x"], u["y"]): u["slot"] for u in fixture}
        for entry in onscreen:
            key = tuple(entry["world"])
            entry["slot"] = by_xy.get(key)
        onscreen = [e for e in onscreen if e.get("slot") is not None]
        if len(onscreen) < NEEDED:
            raise ProbeError(f"fewer than {NEEDED} sparse units placed/resolved: {onscreen}")

        def unit_screen(slot: int) -> tuple[int, int]:
            r = read_row(pid, slot)
            return w2s((r["x"], r["y"]))

        # A ground tile clearly away from every candidate, for deselection.
        deselect_pt = w2s((wx - 8, wy - 8)) if wx >= 8 and wy >= 8 else w2s((wx + 8, wy - 8))

        def do_deselect() -> None:
            click(*deselect_pt)
            time.sleep(0.4)

        # find a click y-offset (sprite drawn above its tile) that selects a
        # single unit, using the first candidate.
        click_dy = None
        probe_slot = onscreen[0]["slot"]
        for dy in (-12, -20, -6, 0, -28):
            do_deselect()
            ux, uy = unit_screen(probe_slot)
            click(ux, uy + dy)
            time.sleep(0.5)
            s = sel()
            if s["count"] == 1 and s["slots"] == [probe_slot]:
                click_dy = dy
                break
        result["click_dy"] = click_dy
        if click_dy is None:
            raise ProbeError("no click offset gave an isolated single-unit selection")

        # --- isolation check: a lone plain click on each candidate must
        # select exactly that slot and nothing else (rules out sprite overlap
        # before any Shift step runs).
        isolated: list[dict[str, Any]] = []
        for entry in onscreen:
            slot = entry["slot"]
            do_deselect()
            ux, uy = unit_screen(slot)
            click(ux, uy + click_dy)
            time.sleep(0.5)
            s = sel()
            ok = s["count"] == 1 and s["slots"] == [slot]
            entry["isolation_check"] = {"count": s["count"], "slots": s["slots"], "isolated": ok}
            if ok:
                isolated.append(entry)
        snap("01-after-isolation-checks")
        result["isolation_summary"] = {"checked": len(onscreen), "isolated": len(isolated)}
        if len(isolated) < NEEDED:
            raise ProbeError(f"fewer than {NEEDED} candidates passed the click-isolation check: {onscreen}")
        sequence = isolated[:NEEDED]
        result["sequence_slots"] = [e["slot"] for e in sequence]

        # --- the actual Shift+click individual-add sequence: plain click on
        # unit 0, then Shift+click units 1..N-1 one at a time.
        do_deselect()
        first = sequence[0]["slot"]
        ux, uy = unit_screen(first)
        click(ux, uy + click_dy)
        time.sleep(0.5)
        s0 = sel()
        result["steps"].append({"i": 0, "slot": first, "mod": None, "count": s0["count"],
                                "slots": s0["slots"], "expected_count": 1,
                                "pass": s0["count"] == 1 and s0["slots"] == [first]})
        expected: list[int] = [first]
        for i, entry in enumerate(sequence[1:], start=1):
            slot = entry["slot"]
            ux, uy = unit_screen(slot)
            click(ux, uy + click_dy, mod="Shift_L")
            time.sleep(0.5)
            s = sel()
            expected.append(slot)
            all_prior_present = all(p in s["slots"] for p in expected)
            result["steps"].append({
                "i": i, "slot": slot, "mod": "Shift_L", "count": s["count"], "slots": s["slots"],
                "expected_count": len(expected),
                "new_slot_present": slot in s["slots"],
                "all_prior_present": all_prior_present,
                "pass": s["count"] == len(expected) and all_prior_present and slot in s["slots"],
            })
        snap("02-after-shift-sequence")

        # bonus: confirm the final selection still takes a broadcast order
        # (all sequence slots, not just the last one, must receive it).
        final_sel = sel()
        before_cmd = {slot: read_row(pid, slot)["command"] for slot in result["sequence_slots"]}
        click(*deselect_pt, button=3)
        t0 = time.monotonic()
        seen_move = {slot: False for slot in result["sequence_slots"]}
        while time.monotonic() - t0 < 2.0:
            for slot in result["sequence_slots"]:
                if read_row(pid, slot)["command"] == 3:
                    seen_move[slot] = True
            time.sleep(0.02)
        result["final_move_check"] = {
            "final_selection": final_sel, "before_command": before_cmd,
            "all_slots_moved": all(seen_move.values()), "seen_move": seen_move,
        }
        snap("03-after-final-move-check")
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
    ap.add_argument("--variant", choices=("original", "candidate"), required=True)
    ap.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    ap.add_argument("--runtime-root", type=Path, required=True)
    ap.add_argument("--artifact-root", type=Path, required=True)
    args = ap.parse_args(argv)
    res = run_probe(args.source, args.runtime_root, args.artifact_root, variant=args.variant)
    print(json.dumps({k: res.get(k) for k in ("status", "error", "variant", "source_unchanged")}, ensure_ascii=False))
    return 0 if res.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
