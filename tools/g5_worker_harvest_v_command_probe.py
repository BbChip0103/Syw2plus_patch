#!/usr/bin/env python3
"""G5 user item (2) sub-question (1): explicit "V" harvest command paired
original20 / candidate(v10)50.

2026-09-29 11:25 operator direction: select worker(s), press the "V"
command-panel button, then *left*-click a resource tile that
``g5_worker_gather_command_probe`` (lap729/lap737, already PASS) already
proved triggers an *implicit* gather order (``pending == 0x1000008``) via a
plain right-click -- and measure whether the same number of selected slots
receive that order through the explicit V-button path instead.

This is deliberately narrower than lap758's earlier V-button attempt
(``g5_command_menu_slot_probe``): that attempt used four guessed field-tile
screen points and got no response on any of them, on the worker alone (no
broadcast fixture). It could not tell "V does nothing here" apart from
"wrong tile". This probe removes that confound by reusing lap729's own
destination-search method (``GATHER_OFFSET_CANDIDATES``) to first
independently reconfirm a gather-capable tile in *this* run before ever
touching the V button, exactly as g5_worker_gather_command_probe does for
the right-click case.

Only the protected original is read for both variants; the candidate is
rebuilt from it and SHA-verified against the pinned v10 hash before use.
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

from patches.selection import g5_selection_cap50_v10 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, SupplyProbe, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    selection_snapshot, unit_snapshot,
    sha256, write_json, capture,
)
from tools.g5_command_coverage_probe import observe, RESELECT_START, RESELECT_END
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS
from tools.g5_worker_gather_command_probe import (
    GATHER_OFFSET_CANDIDATES, GATHER_PENDING, spawned_worker_slots, worker_grid_requests,
)
from tools.g5_command_menu_slot_probe import WORKER_BUTTON_SCREEN
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
# v10 (lap756, full-50 save/load restore); pinned SHA reconfirmed lap757.
TARGET_SHA = "c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad"
V_BUTTON_SCREEN = WORKER_BUTTON_SCREEN["v"]
# The solo lobby's starting worker *type id* varies by random nation (7/21/
# 23/31/... observed across boots, lap730/lap760), so a fixed allow-list
# can't be curated ahead of time. Reuse the existing private fork that
# already solved this for g5_worker_repair_command_probe (lap730): it drops
# the shared runtime_bridge.c's fixed-type allow-list for op=5/6 in favor of
# the same structural checks (flags bit1/2/3 clear, width/height in [1,8]),
# and never touches the shared, G2-pinned runtime_bridge.c.
BRIDGE_SOURCE = REPO / "patches/population/g5_c_repair_bridge.c"


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
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200",
                    "--bridge-source", str(BRIDGE_SOURCE)],
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
        "schema": "syw2plus.g5-worker-harvest-v-command.v1", "variant": variant, "status": "UNKNOWN",
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
        if worker["owner"] != 0 or worker["unit_type"] == 0:
            raise ProbeError(f"slot1198 is not the expected worker: {worker}")
        worker_type = int(worker["unit_type"])
        result["worker"] = worker
        result["worker_type"] = worker_type
        supply = SupplyProbe(prefix)
        click(*MINIMAP_CLICK)
        time.sleep(1)

        # --- screen calibration (worker only), same method as lap682/717/723/728/729.
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

        # --- re-find a worker-relative destination that is a gather via plain
        # right-click, exactly as g5_worker_gather_command_probe does -- this
        # independently reconfirms the tile in *this* run/build/seed before
        # the V-button test ever touches it.
        def worker_orders_at(screen: list[int]) -> list[str]:
            xdo("key", "s")
            time.sleep(0.6)
            got: set[str] = set()
            click(*screen, button=3)
            t0 = time.monotonic()
            while time.monotonic() - t0 < 0.4:
                got.add(hex(int.from_bytes(read_memory(pid, wbase + 0x384, 4), "little")))
                time.sleep(0.005)
            return sorted(got)

        gather_search: list[dict[str, Any]] = []
        gather_dest: dict[str, Any] | None = None
        for off in GATHER_OFFSET_CANDIDATES:
            world = (wx + off[0], wy + off[1])
            screen = list(w2s(world))
            if not (0 < screen[0] < 790 and 45 < screen[1] < 465):
                continue
            orders = worker_orders_at(screen)
            is_gather = GATHER_PENDING in orders
            gather_search.append({"offset": list(off), "world": list(world), "screen": screen,
                                  "worker_pending_seen": orders, "gather": is_gather})
            if is_gather and gather_dest is None:
                gather_dest = {"offset": list(off), "world": list(world), "screen": screen}
        result["gather_destination_search"] = gather_search
        if gather_dest is None:
            raise ProbeError(f"no offset produced a gather pending word: {gather_search}")
        result["gather_destination"] = gather_dest
        xdo("key", "s")
        time.sleep(0.5)

        # --- spawn a worker-type-only fixture in the worker-centered grid
        requests = worker_grid_requests(worker)
        for req in requests:
            r = supply.call(op=5, owner=0, unit_type=worker_type, x=req["x"], y=req["y"], count=req["count"])
            if not r.get("ok") or r.get("fixture_added") != req["count"]:
                raise ProbeError(f"fixture failed: {r}")
        time.sleep(1)
        snap("01-after-worker-fixture")
        fixture = spawned_worker_slots(pid, worker_type, VISIBLE_WORKER_SLOT)
        result["fixture_spawned"] = len(fixture)
        if len(fixture) != len(requests):
            raise ProbeError(f"expected {len(requests)} spawned workers, found {len(fixture)}")

        # --- select everything visible with one full drag, press the V
        # command-panel button, then LEFT-click the reconfirmed gather tile
        # (the operator's explicit sequence, as opposed to the plain
        # right-click g5_worker_gather_command_probe already validated).
        click(*RESELECT_START, drag_to=RESELECT_END)
        time.sleep(0.8)
        selection = sel()
        result["selection"] = selection
        snap("02-after-fulldrag")
        slots = list(selection["slots"])
        if not slots:
            raise ProbeError("full drag selected nothing")

        def fire() -> None:
            click(*V_BUTTON_SCREEN, button=1)
            time.sleep(0.3)
            click(*gather_dest["screen"], button=1)

        obs = observe(pid, slots, fire, 4.0)
        result["harvest_v_observe"] = obs
        snap("03-after-v-harvest-click")
        if not alive():
            raise ProbeError("game not alive after V harvest click")

        harvested = obs.get("pending_ever", {}).get(GATHER_PENDING, 0)
        result["harvest_v_summary"] = {
            "selected_count": selection["count"], "selected_unique": selection["unique_slots"],
            "harvested_count": harvested, "all_selected_harvested": harvested == selection["unique_slots"],
            "capacity": sel_cap, "all_pending_values_seen": sorted(obs.get("pending_ever", {}).keys()),
        }
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
    print(json.dumps({k: res.get(k) for k in (
        "status", "error", "variant", "source_unchanged", "gather_destination",
        "harvest_v_summary")}, ensure_ascii=False))
    return 0 if res.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
