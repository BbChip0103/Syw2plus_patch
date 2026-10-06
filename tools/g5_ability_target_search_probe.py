#!/usr/bin/env python3
"""G5 checklist C: find a firing target for the "v"/"i" worker-ability cells,
then paired-measure original20 / candidate50 the same way gather/repair/"f"
already were.

STATUS 2026-09-28 lap736 "다음 work" item (2): lap735 confirmed the "f" cell
broadcasts to every selected slot (PASS, 20/20 and 50/50) using
``press_ability`` = one command-grid button click + one right-click on a
single fixed worker-relative ground point ``(wx+4, wy-4)``. The same recipe
on the "v"/"i" cells (populated -- pixel variance above threshold, i.e. not
blank this boot) produced zero response from every selected slot on *both*
variants (0/20, 0/50) -- not a truncation pattern (some respond, some don't),
so lap735 left it ``UNKNOWN`` rather than a v6 regression: either the fixed
ground point is not a valid target for these particular abilities (most
worker orders in this engine, e.g. gather, are tile-conditional the way a
plain right-click already is), or the ability needs no ground point at all
and the single extra click after the button cancels/overrides it.

This probe tests both hypotheses on the *lone pre-existing worker* before
ever touching the measurement fixture, exactly the way
``g5_worker_gather_command_probe`` found the gather destination before
spawning anything -- lap735 already showed a real button-press changes
``+0x290`` once and then goes silent (one-shot/cooldown), so every hypothesis
must be tried on a *worker that has never used this ability*, and the first
one that produces a state change is the one used for the real (also
never-used) fixture broadcast:

1. button-only (no ground click) -- mirrors how "S" (stop) already broadcasts
   with no target; if the ability is a self-cast, the earlier probe's forced
   ground click may have been the thing invalidating it.
2. button + ground right-click, swept over ``ABILITY_OFFSET_CANDIDATES``
   (the same worker-relative tile list ``g5_worker_gather_command_probe``
   validated as reachable/open around this fixture) -- mirrors gather's own
   destination search, in case the ability is tile-conditional.

Whichever hypothesis first changes the worker's own ``+0x290``/``+0x384``
away from its pre-attempt value is recorded as this boot's confirmed trigger
for that ability letter, and is applied exactly once, identically, to the
freshly spawned worker-type fixture (never touched by the search) with the
whole selection watched via ``responded_slots`` (imported unmodified from
``g5_worker_ability_broadcast_probe``, which already generalizes "changed
from own pre-input value" instead of assuming a known pending-word).

The boot's nation (worker/HQ unit_type) is randomized each launch (lap730);
only cells other than "f" (already resolved) are attempted, and a boot whose
active cells are already fully resolved is discarded and retried (own full
boot/lobby/PS3 cycle each time, same reboot-sampling shape as
``g5_construction_new_nation_survey_probe``) up to ``--max-attempts``.

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

from patches.selection import g5_selection_cap50_v6 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, SupplyProbe, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    selection_snapshot, unit_snapshot,
    sha256, write_json, capture,
)
from tools.g5_command_coverage_probe import RESELECT_START, RESELECT_END
from tools.g5_worker_ability_broadcast_probe import (
    ABILITY_BUTTONS, CELL_POPULATED_STD_THRESHOLD, cell_std, responded_slots,
)
from tools.g5_worker_gather_command_probe import (
    worker_grid_requests, spawned_worker_slots, GATHER_OFFSET_CANDIDATES,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
# v6 (lap733 death-recall fix); pinned SHA reconfirmed by lap734/735/736.
TARGET_SHA = "fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f"
# lap730's fixture-type-agnostic fork: shared runtime_bridge.c restricts op=5/6
# fixture_type to a curated allow-list that does not include most solo-lobby
# worker types (nation randomized per boot), so this probe reuses the same
# private fork g5_worker_repair_command_probe.py/ability_broadcast_probe.py
# already validated for that reason (never touches the shared G2-pinned
# runtime_bridge.c or the R3 probe's g5_r3_death_bridge.c).
ABILITY_BRIDGE_SOURCE = REPO / "patches/population/g5_c_repair_bridge.c"
# Cells already resolved by lap735 (paired PASS via button+fixed-ground);
# skip them here so boot attempts are spent on the still-unresolved letters.
ALREADY_RESOLVED = {"f"}
ABILITY_OFFSET_CANDIDATES = GATHER_OFFSET_CANDIDATES
SEARCH_WINDOW = 1.5
MAX_OFFSETS_PER_CELL = 8


def worker_state_row(pid: int, wbase: int) -> dict[str, int]:
    return {
        "command": int.from_bytes(read_memory(pid, wbase + 0x290, 2), "little", signed=True),
        "pending": int.from_bytes(read_memory(pid, wbase + 0x384, 4), "little"),
    }


def changed(before: dict[str, int], after: dict[str, int]) -> bool:
    return before["command"] != after["command"] or before["pending"] != after["pending"]


def sample_worker_for(pid: int, wbase: int, window: float) -> dict[str, int]:
    """Last worker state row sampled over ``window`` seconds (10ms cadence)."""
    start = time.monotonic()
    last = worker_state_row(pid, wbase)
    while time.monotonic() - start < window:
        last = worker_state_row(pid, wbase)
        time.sleep(0.01)
    return last


def wait_settle(pid: int, wbase: int, *, quiet: float = 0.6, timeout: float = 3.0) -> dict[str, int]:
    """Poll until ``command``/``pending`` hold steady for ``quiet`` seconds (or
    ``timeout`` elapses), so a post-"s" stop order has time to finish settling
    to idle before it is used as a change-detection baseline -- a run1 boot
    on this lap found ``command`` still transitioning 3->1 on its own ~1s
    after the "s" keypress, which a short fixed sleep read as a false-positive
    "the ability fired" signal with no click at all."""
    last = worker_state_row(pid, wbase)
    stable_since = time.monotonic()
    deadline = stable_since + timeout
    while time.monotonic() < deadline:
        time.sleep(0.05)
        cur = worker_state_row(pid, wbase)
        if cur != last:
            last = cur
            stable_since = time.monotonic()
        elif time.monotonic() - stable_since >= quiet:
            break
    return last


def run_attempt(
    source: Path, runtime_root: Path, artifact_root: Path, *, variant: str, attempt_index: int,
) -> dict[str, Any]:
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
        "schema": "syw2plus.g5-ability-target-search.v1", "variant": variant,
        "attempt_index": attempt_index, "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": private_sha, "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [], "inputs": [], "target_search": {}, "ability_probes": {},
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
        result["nation_signature"] = {"worker_type": worker_type}
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

        # --- identify populated cells this boot without touching them (lap735 method).
        grid_capture = artifact_root / "00-worker-selected-command-grid.png"
        cell_variance = {name: cell_std(grid_capture, *pt) for name, pt in ABILITY_BUTTONS.items()}
        active_cells = [name for name, v in cell_variance.items() if v > CELL_POPULATED_STD_THRESHOLD]
        result["cell_variance"] = cell_variance
        result["active_cells_this_boot"] = active_cells
        target_cells = [c for c in active_cells if c not in ALREADY_RESOLVED]
        result["target_cells_this_boot"] = target_cells
        for name in ABILITY_BUTTONS:
            result["ability_probes"][name] = {"cell_variance": cell_variance[name], "populated": name in active_cells}

        if not target_cells:
            result["status"] = "NO_TARGET_CELL_THIS_BOOT"
            return result

        # --- per target cell: find a trigger recipe on the lone worker, then
        # immediately measure the untouched fixture with that recipe.
        for name in target_cells:
            pt = ABILITY_BUTTONS[name]
            search: dict[str, Any] = {"attempts": []}

            click(*DRAG_START, drag_to=DRAG_END)
            time.sleep(0.6)
            xdo("key", "s")
            before = wait_settle(pid, wbase)
            click(*pt)
            after = sample_worker_for(pid, wbase, SEARCH_WINDOW)
            snap(f"01-{name}-button-only")
            attempt = {"kind": "button_only", "before": before, "after": after, "changed": changed(before, after)}
            search["attempts"].append(attempt)
            recipe: dict[str, Any] | None = None
            if attempt["changed"]:
                recipe = {"kind": "button_only"}
            else:
                for off in ABILITY_OFFSET_CANDIDATES[:MAX_OFFSETS_PER_CELL]:
                    if not alive():
                        break
                    world = (wx + off[0], wy + off[1])
                    screen = list(w2s(world))
                    if not (0 < screen[0] < 790 and 45 < screen[1] < 465):
                        continue
                    click(*DRAG_START, drag_to=DRAG_END)
                    time.sleep(0.5)
                    xdo("key", "s")
                    before = wait_settle(pid, wbase)
                    click(*pt)
                    click(*screen, button=3)
                    after = sample_worker_for(pid, wbase, SEARCH_WINDOW)
                    did_change = changed(before, after)
                    search["attempts"].append({"kind": "button_ground", "offset": list(off), "world": list(world),
                                                "screen": screen, "before": before, "after": after,
                                                "changed": did_change})
                    if did_change:
                        recipe = {"kind": "button_ground", "offset": list(off), "screen": screen}
                        break
            search["confirmed_recipe"] = recipe
            result["target_search"][name] = search
            snap(f"02-{name}-search-done")
            if not alive():
                raise ProbeError(f"game not alive after target search for {name}")
            if recipe is None:
                result["ability_probes"][name]["status"] = "NO_FIRING_TARGET_FOUND"
                continue

            xdo("key", "s")
            time.sleep(0.4)
            requests = worker_grid_requests(worker)
            for req in requests:
                r = supply.call(op=5, owner=0, unit_type=worker_type, x=req["x"], y=req["y"], count=req["count"])
                if not r.get("ok") or r.get("fixture_added") != req["count"]:
                    raise ProbeError(f"fixture failed: {r}")
            time.sleep(1)
            snap(f"03-{name}-after-worker-fixture")
            fixture = spawned_worker_slots(pid, worker_type, VISIBLE_WORKER_SLOT)
            if len(fixture) != len(requests):
                raise ProbeError(f"expected {len(requests)} spawned workers, found {len(fixture)}")

            # --- diagnostic: a small (worker + a couple of neighbours)
            # selection, before touching the full 56-unit fixture -- isolates
            # whether firing depends on selection *size* (e.g. a solo-only
            # ability) rather than on the 20-entry array cap under test.
            pa = w2s((wx - 1, wy - 1))
            pb = w2s((wx + 1, wy + 1))
            duo_box = ((min(pa[0], pb[0]), min(pa[1], pb[1])), (max(pa[0], pb[0]), max(pa[1], pb[1])))
            click(*duo_box[0], drag_to=duo_box[1])
            time.sleep(0.6)
            duo_sel = sel()
            snap(f"04a-{name}-duo-selection")
            duo_before = wait_settle(pid, wbase)
            click(*pt)
            if recipe["kind"] == "button_ground":
                click(*recipe["screen"], button=3)
            duo_after = sample_worker_for(pid, wbase, SEARCH_WINDOW)
            result["ability_probes"][name]["duo_check"] = {
                "selection_slots": duo_sel["slots"], "selection_count": duo_sel["count"],
                "before": duo_before, "after": duo_after, "fired": changed(duo_before, duo_after),
            }
            if not alive():
                raise ProbeError(f"game not alive after duo check for {name}")

            click(*RESELECT_START, drag_to=RESELECT_END)
            time.sleep(0.8)
            selection = sel()
            snap(f"04-{name}-after-fulldrag")
            slots = list(selection["slots"])
            if not slots:
                raise ProbeError(f"full drag selected nothing before ability {name}")

            def act(pt=pt, recipe=recipe) -> None:
                click(*pt)
                if recipe["kind"] == "button_ground":
                    click(*recipe["screen"], button=3)

            broadcast = responded_slots(pid, slots, act, 4.0)
            snap(f"05-{name}-after-broadcast")
            if not alive():
                raise ProbeError(f"game not alive after broadcast of ability {name}")
            summary = {
                "selected_count": selection["count"], "selected_unique": selection["unique_slots"],
                "responded_count": broadcast["responded_count"],
                "all_selected_responded": broadcast["responded_count"] == selection["unique_slots"],
                "capacity": sel_cap, "recipe": recipe,
            }
            result["ability_probes"][name]["broadcast_probe"] = broadcast
            result["ability_probes"][name]["broadcast_summary"] = summary
            result["ability_probes"][name]["status"] = "COMPLETE"
            # fixture is single-use per boot for supply-probe spawning at this
            # worker_type/position set; only one target cell is fully measured
            # per boot to keep every fixture slot's pre-broadcast history clean.
            break
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


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, *, variant: str, max_attempts: int,
) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    attempts: list[dict[str, Any]] = []
    final: dict[str, Any] | None = None
    for i in range(1, max_attempts + 1):
        attempt_root = artifact_root / f"attempt_{i:02d}"
        try:
            attempt = run_attempt(source, runtime_root, attempt_root, variant=variant, attempt_index=i)
        except ProbeError as exc:
            attempt = {"attempt_index": i, "status": "FAIL", "error": f"ProbeError: {exc}"}
        attempts.append({k: attempt.get(k) for k in (
            "attempt_index", "status", "nation_signature", "active_cells_this_boot", "target_cells_this_boot",
            "source_unchanged", "cleanup", "error")})
        if attempt.get("status") not in ("NO_TARGET_CELL_THIS_BOOT",):
            final = attempt
            break
    summary = {
        "schema": "syw2plus.g5-ability-target-search-summary.v1", "variant": variant,
        "attempts_run": len(attempts), "attempts": attempts,
        "final_attempt_status": final.get("status") if final else "EXHAUSTED_NO_TARGET_CELL_BOOT",
        "final_attempt_dir": str(artifact_root / f"attempt_{len(attempts):02d}") if attempts else None,
        "final": final,
    }
    write_json(artifact_root / "summary.json", summary)
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", choices=("original", "candidate"), required=True)
    ap.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    ap.add_argument("--runtime-root", type=Path, required=True)
    ap.add_argument("--artifact-root", type=Path, required=True)
    ap.add_argument("--max-attempts", type=int, default=4)
    args = ap.parse_args(argv)
    res = run_probe(args.source, args.runtime_root, args.artifact_root,
                     variant=args.variant, max_attempts=args.max_attempts)
    print(json.dumps({k: res.get(k) for k in ("variant", "attempts_run", "final_attempt_status")},
                      ensure_ascii=False))
    final = res.get("final") or {}
    return 0 if final.get("status") in ("COMPLETE",) else 2


if __name__ == "__main__":
    raise SystemExit(main())
