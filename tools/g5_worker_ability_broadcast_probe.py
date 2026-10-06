#!/usr/bin/env python3
"""G5 checklist C: worker special-ability button paired original20 / candidate50.

STATUS 2026-09-28 08:15/10:06 operator direction: (C) 특수능력/변신 cannot be
closed on "existence confirmed" alone (lap731) -- every ability button that
exists this boot (solo lobby nation is randomized per boot, lap730) must be
paired-measured original20 vs candidate50 the same way gather (lap729) and
repair (lap730) already were.

Unlike gather/repair (a plain ground right-click that the live engine already
turns into a distinctive pending word), the worker's ability buttons
(``ABILITY_BUTTONS`` -- grid cells beyond stop/move, labelled v/i/f; lap731
found only 1-2 of these are non-empty per boot, the rest are blank/no-op) have
no known pending-word signature ahead of time. lap735 run1 tried
click-to-characterize on the lone pre-existing worker before spawning the
fixture (click each cell once, watch for a state change) and found this
*consumes* the ability: the same button, same worker, same input, produced a
state change (``+0x290`` -> 8) the first time and nothing at all the second
time on the group-broadcast test -- a one-shot/cooldown effect, not a cap
truncation. Clicking a candidate ability before the real measurement would
bias every run toward a false FAIL.

This probe instead identifies which cells are populated **without touching
them**: after the calibration drag (worker alone selected), it crops each
candidate cell from the already-captured command-grid screenshot and checks
pixel variance -- lap735 run1's own captures show populated cells at
mean~57-100/std~55-69 (icon art) vs empty cells at mean~11/std~8 (flat
background), a wide, unambiguous margin. Only cells that are visually
populated are ever clicked, and each is clicked exactly once, on a fixture
that has never seen this ability before, immediately followed by the
selected-count response measurement -- so the paired original20/candidate50
comparison is never contaminated by a prior use.

For the response measurement itself, it does not assume a pending-word
signature either: it tracks, **per slot**, whether the button click (plus a
worker-relative ground follow-up click, in case the ability is target-mode
like gather/attack) ever changes that slot's ``+0x290`` command or ``+0x384``
pending word away from its own pre-click value, sampled every 10ms for 4s
(same cadence as ``g5_command_coverage_probe.observe``). This works
regardless of which concrete ability a given boot's nation happens to have,
because the selection-array broadcast gate under test (``0x41F0A4``, already
shown opcode-independent across move/stop/hold/patrol/attack/group-assign/
gather/repair, lap729) is exercised the same way no matter the ability's
specific effect.

Method:
1. Boot solo lobby (identical sequence to every other G5 checklist probe).
2. With only the lone pre-existing worker selected (calibration drag),
   pixel-crop each of the 3 ability cells (v/i/f) from the command-grid
   screenshot and classify populated vs empty by variance -- no clicks.
3. Spawn a worker-type-only dense fixture (same 7x8 grid as
   ``g5_worker_gather_command_probe``), select everything with one full
   drag, then for each populated cell click it once (plus one worker-
   relative ground follow-up click) while tracking **every selected slot**
   for a command/pending change vs its own immediately-prior value. PASS =
   every selected slot changes (stock: <=20; candidate: up to 50/51, i.e.
   not truncated to the first 20 array entries).
4. If no cell is populated, the boot's nation has no worker special ability
   at all (S/M only or blank cells) -- reported as
   ``no_ability_this_boot`` (N/A for *this* run only, not a repo-wide claim;
   lap731 already sampled 2 other boots that did have V/F abilities).

The protected original is only read (SHA before/after); the candidate is
rebuilt from it and SHA-verified against the pinned v6 hash.
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
from PIL import Image

from patches.selection import g5_selection_cap50_v6 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, SupplyProbe, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    selection_snapshot, unit_snapshot,
    sha256, write_json, capture,
)
from tools.g5_command_coverage_probe import read_rows_bulk, RESELECT_START, RESELECT_END
from tools.g5_worker_gather_command_probe import worker_grid_requests, spawned_worker_slots
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
# v6 (lap733 death-recall fix); pinned SHA reconfirmed by lap734.
TARGET_SHA = "fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f"
# lap730's fixture-type-agnostic fork: the shared runtime_bridge.c restricts
# op=5/6 fixture_type to a curated allow-list that does not include most
# solo-lobby worker types (nation is randomized per boot, lap730), so this
# probe uses the same private fork g5_worker_repair_command_probe.py already
# validated for that reason (structural checks + real engine Place/Gate,
# never touches the shared G2-pinned runtime_bridge.c).
ABILITY_BRIDGE_SOURCE = REPO / "patches/population/g5_c_repair_bridge.c"
ABILITY_BUTTONS = {"v": (740, 503), "i": (777, 503), "f": (667, 538)}
# lap735 run1 measured populated cells at std~55-69 vs empty cells at
# std~8 (flat background) on the 800x600 render; 20 sits well inside the gap.
CELL_POPULATED_STD_THRESHOLD = 20.0
FAST_WINDOW = 1.5
FAST_INTERVAL = 0.01
SAMPLE_INTERVAL = 0.1


def cell_std(screenshot: Path, x: int, y: int, radius: int = 12) -> float:
    """Pixel stddev of a ``radius``-px square centered on a command-grid cell.
    A populated icon (any art) reads far higher than the flat single-colour
    background of an empty cell -- see ``CELL_POPULATED_STD_THRESHOLD``."""
    arr = np.array(Image.open(screenshot).convert("L"))
    crop = arr[y - radius:y + radius, x - radius:x + radius]
    return float(crop.std())


def responded_slots(pid: int, slots: list[int], act, window: float) -> dict[str, Any]:
    """Per-slot: did command(+0x290) or pending(+0x384) ever differ from this
    slot's own pre-``act`` value, sampled at the same cadence as
    ``g5_command_coverage_probe.observe``. Unlike ``observe`` (which
    aggregates by value, useful when the target value is known in advance),
    this reports a plain per-slot boolean so an a-priori-unknown ability
    signature still yields a clean received/selected count."""
    slots = [s for s in slots if 0 < s < 1200]
    before = read_rows_bulk(pid, slots)
    act()
    start = time.monotonic()
    responded: dict[int, bool] = {s: False for s in slots}
    last: dict[int, dict[str, int]] = {}
    n_samples = 0
    while (elapsed := time.monotonic() - start) < window:
        last = read_rows_bulk(pid, slots)
        n_samples += 1
        for s, row in last.items():
            if row["command"] != before[s]["command"] or row["pending"] != before[s]["pending"]:
                responded[s] = True
        time.sleep(FAST_INTERVAL if elapsed < FAST_WINDOW else SAMPLE_INTERVAL)
    return {
        "n_slots": len(slots), "n_samples": n_samples,
        "responded_count": sum(1 for v in responded.values() if v),
        "responded_slots": sorted(s for s, v in responded.items() if v),
        "not_responded_slots": sorted(s for s, v in responded.items() if not v),
        "final_command": {str(s): last.get(s, {}).get("command") for s in slots},
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
    bridge_dir = artifact_root / "ability_bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200",
                    "--bridge-source", str(ABILITY_BRIDGE_SOURCE)],
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
        "schema": "syw2plus.g5-worker-ability-broadcast.v1", "variant": variant, "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": private_sha, "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [], "inputs": [], "ability_probes": {},
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

        # --- screen calibration (worker only), same method as every checklist probe.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        cal_sel = sel()
        if VISIBLE_WORKER_SLOT not in cal_sel["slots"]:
            raise ProbeError(f"worker not selected for calibration: {cal_sel}")
        snap("00-worker-selected-command-grid")
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
        ground_screen = w2s((wx + 4, wy - 4))

        def press_ability(pt: tuple[int, int]) -> None:
            click(*pt)
            click(*ground_screen, button=3)

        # --- step 1: identify which of v/i/f cells are populated this boot,
        # by pixel variance on the calibration-drag capture -- no clicks, so
        # nothing is used up before the real (fixture) measurement below.
        grid_capture = artifact_root / "00-worker-selected-command-grid.png"
        cell_variance = {name: cell_std(grid_capture, *pt) for name, pt in ABILITY_BUTTONS.items()}
        active_cells = [name for name, v in cell_variance.items() if v > CELL_POPULATED_STD_THRESHOLD]
        result["cell_variance"] = cell_variance
        result["active_cells_this_boot"] = active_cells
        for name in ABILITY_BUTTONS:
            result["ability_probes"][name] = {"cell_variance": cell_variance[name], "populated": name in active_cells}

        if not active_cells:
            result["status"] = "COMPLETE_NO_ABILITY_THIS_BOOT"
        else:
            # --- step 2: spawn worker-type fixture, full-drag select, broadcast each active ability.
            xdo("key", "s")
            time.sleep(0.5)
            requests = worker_grid_requests(worker)
            for req in requests:
                r = supply.call(op=5, owner=0, unit_type=worker_type, x=req["x"], y=req["y"], count=req["count"])
                if not r.get("ok") or r.get("fixture_added") != req["count"]:
                    raise ProbeError(f"fixture failed: {r}")
            time.sleep(1)
            snap("02-after-worker-fixture")
            fixture = spawned_worker_slots(pid, worker_type, VISIBLE_WORKER_SLOT)
            result["fixture_spawned"] = len(fixture)
            if len(fixture) != len(requests):
                raise ProbeError(f"expected {len(requests)} spawned workers, found {len(fixture)}")

            for name in active_cells:
                pt = ABILITY_BUTTONS[name]
                click(*RESELECT_START, drag_to=RESELECT_END)
                time.sleep(0.8)
                selection = sel()
                snap(f"03-after-fulldrag-before-{name}")
                slots = list(selection["slots"])
                if not slots:
                    raise ProbeError(f"full drag selected nothing before ability {name}")
                broadcast = responded_slots(pid, slots, lambda pt=pt: press_ability(pt), 4.0)
                snap(f"04-after-broadcast-{name}")
                if not alive():
                    raise ProbeError(f"game not alive after broadcast of ability {name}")
                summary = {
                    "selected_count": selection["count"], "selected_unique": selection["unique_slots"],
                    "responded_count": broadcast["responded_count"],
                    "all_selected_responded": broadcast["responded_count"] == selection["unique_slots"],
                    "capacity": sel_cap,
                }
                result["ability_probes"][name]["broadcast_probe"] = broadcast
                result["ability_probes"][name]["broadcast_summary"] = summary
                xdo("key", "s")
                time.sleep(0.4)
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
    print(json.dumps({k: res.get(k) for k in ("status", "error", "variant", "source_unchanged",
                                                "active_cells_this_boot")}, ensure_ascii=False))
    return 0 if res.get("status") in ("COMPLETE", "COMPLETE_NO_ABILITY_THIS_BOOT") else 2


if __name__ == "__main__":
    raise SystemExit(main())
