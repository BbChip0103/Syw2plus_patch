#!/usr/bin/env python3
"""G5 checklist C: worker repair order paired original20 / candidate50.

STATUS 2026-09-28 06:55 operator direction ("다음 work 우선순위: 수리") asks
for the next checklist (C) special worker command after gather (lap729):
does a worker's repair order (right-click on a *damaged* friendly building)
reach every selected worker-type unit, the same way move/stop/hold/patrol/
gather already were?

Method, reusing the proven solo-lobby bootstrap and 9-point worker screen<->
world affine (lap682/717/723/724/726/727/728/729):

1. Locate the pre-existing owner-0 HQ (the only other starting unit besides
   the visible worker -- ``population_5000_runtime_0910.md``,
   ``g2_eight_owner_fixture_recipe.md``; its *type id* is NOT pinned, see
   ``find_hq_slot``) by scanning the existence table for exclusion, and read
   its live HP (``unit+0xB4``, the same field every other diagnostic op
   already treats as authoritative HP).
2. Right-click the HQ's screen position (from the affine fit) with only the
   live worker selected, both while the HQ is at full/starting HP and after
   halving its HP via a new bridge diagnostic op (11,
   ``patches/population/g5_c_repair_bridge.c`` -- direct, non-lethal write of
   ``unit+0xB4``; see that file's docstring for why a direct write is
   sufficient here, unlike op=10's kill path). lap730 found the pending
   command word (``unit+0x384``) is **the same** (``0x1000008``, gather's
   value) whether the HQ is damaged or not -- this engine appears to issue
   one generic "interact with a friendly structure" order for any own-HQ
   right-click (deposit if carrying resources, repair if the HQ is damaged,
   resolved by the engine after the order is queued, not encoded in the
   order word itself) -- so this probe does not try to find a distinct
   "repair" pending word; instead it reuses ``0x1000008`` for the broadcast
   check and separately confirms repair is actually happening by sampling
   the HQ's own HP for an increase after the order is issued.
3. Spawn a worker-type-only fixture in the same worker-centered grid gather
   used (``g5_worker_gather_command_probe.worker_grid_requests``), full-drag
   select everything visible, and right-click the (still damaged) HQ.
   ``observe()`` (imported unmodified from ``g5_command_coverage_probe``)
   reports, per pending-word value, how many selected slots ever showed it.

PASS = the number of selected slots that ever show the ``0x1000008`` pending
word equals the number of slots actually selected (stock: capped at 20;
candidate: up to 50). The HQ HP delta is recorded as supporting evidence
that this is really a repair order, not a hard gate (physical repair
progress within the observation window depends on worker pathing time and
is not the object under test -- broadcast reach is).

The protected original is only read (SHA before/after); the candidate is
rebuilt from it and SHA-verified against the pinned v5 hash.
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
    ProbeError, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET, UNIT_HP_OFFSET,
    UNIT_X_OFFSET, UNIT_Y_OFFSET, selection_snapshot, unit_snapshot,
    sha256, write_json, capture,
)
from tools.g5_command_coverage_probe import observe, RESELECT_START, RESELECT_END
from tools.g5_r3_sparse_selection_probe import Bridge
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS
from tools.g5_worker_gather_command_probe import spawned_worker_slots, worker_grid_requests
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
# v5 (lap723 R3 fix); pinned SHA reconfirmed by lap724/725/726/727/728/729.
TARGET_SHA = "29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146"
REPAIR_BRIDGE_SOURCE = REPO / "patches/population/g5_c_repair_bridge.c"
MOVE_PENDING = "0x1000003"
STOP_PENDING = "0x1000002"
# lap730 found ``0x1000001`` appears in nearly every ``worker_orders_at``
# sample regardless of the click target (it shows up even on plain-MOVE
# results) -- it is transient/idle noise from the 0.4s poll window catching
# state before the click's own order propagates, not a real order, so it
# must be excluded alongside MOVE/STOP when looking for a "this actually hit
# something" signal.
IDLE_PENDING = "0x1000001"
NON_SIGNAL_PENDING = (IDLE_PENDING, MOVE_PENDING, STOP_PENDING)
EXISTS_TABLE = 0x008990C8
# The HQ's own (x, y) is its placement anchor, not necessarily its footprint
# center (multi-tile buildings; lap730 found some nations' anchor click lands
# just outside the clickable sprite and only yields a plain MOVE). Search a
# small neighborhood, closest first, same technique as
# ``g5_worker_gather_command_probe.GATHER_OFFSET_CANDIDATES``.
HQ_FOOTPRINT_OFFSET_CANDIDATES = [
    (0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (-1, -1),
    (2, 1), (1, 2), (2, 2), (-2, 0), (0, -2), (2, 0), (0, 2),
]


def find_hq_slot(pid: int, exclude: int) -> dict[str, Any]:
    """The lone pre-existing owner-0 unit besides the visible worker.

    ``population_5000_runtime_0910.md`` establishes the solo-lobby fixture
    always starts with exactly two owner-0 units (count=2): the HQ and the
    worker. lap730 found the nation (and therefore the HQ's *type* id, 49 in
    one run vs the visible worker itself reading type31 in another -- solo
    lobby nation is not fixture-pinned, cf. lap671's type31 "일꾼" on a
    different run) is not stable across runs, so this scans by *exclusion*
    (the other owner-0 slot) rather than a hardcoded type id."""
    exists = read_memory(pid, EXISTS_TABLE, 1200 * 2)
    hits: list[dict[str, Any]] = []
    for slot in range(1, 1200):
        if slot == exclude:
            continue
        if int.from_bytes(exists[slot * 2:slot * 2 + 2], "little", signed=False) == 0:
            continue
        base = UNIT_BASE + slot * UNIT_STRIDE
        unit_type = int.from_bytes(read_memory(pid, base + 0x8D, 1), "little")
        owner = int.from_bytes(read_memory(pid, base + 0x8E, 1), "little")
        if owner == 0:
            hits.append({
                "slot": slot,
                "unit_type": unit_type,
                "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
                "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
                "hp": int.from_bytes(read_memory(pid, base + UNIT_HP_OFFSET, 4), "little", signed=True),
            })
    if len(hits) != 1:
        raise ProbeError(f"expected exactly one other owner-0 unit (the HQ), found {hits}")
    return hits[0]


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
    bridge_dir = artifact_root / "repair_bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200",
                    "--bridge-source", str(REPAIR_BRIDGE_SOURCE)],
                   cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge_dll = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge_dll, timeout=60)
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
        "schema": "syw2plus.g5-worker-repair-command.v1", "variant": variant, "status": "UNKNOWN",
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

        hq = find_hq_slot(pid, VISIBLE_WORKER_SLOT)
        result["hq"] = hq
        if hq["hp"] <= 1:
            raise ProbeError(f"HQ hp too low to halve meaningfully: {hq}")

        click(*MINIMAP_CLICK)
        time.sleep(1)
        snap("00a-after-minimap-leftclick-legacy-point")

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

        # --- find a screen point that actually registers as "clicked the HQ"
        # (undamaged: expect something other than a plain MOVE/STOP -- the
        # HQ is the worker's own drop-off point, so lap730's confirmed runs
        # saw gather's 0x1000008 here) rather than assuming the anchor tile
        # is inside the building's clickable footprint.
        hq_search: list[dict[str, Any]] = []
        hq_screen: list[int] | None = None
        baseline_orders: list[str] = []
        for off in HQ_FOOTPRINT_OFFSET_CANDIDATES:
            world = (int(hq["x"]) + off[0], int(hq["y"]) + off[1])
            screen = list(w2s(world))
            if not (0 < screen[0] < 790 and 45 < screen[1] < 465):
                continue
            orders = worker_orders_at(screen)
            hits_building = any(v not in NON_SIGNAL_PENDING for v in orders)
            hq_search.append({"offset": list(off), "world": list(world), "screen": screen,
                              "worker_pending_seen": orders, "hits_building": hits_building})
            if hits_building and hq_screen is None:
                hq_screen = screen
                baseline_orders = orders
        result["hq_footprint_search"] = hq_search
        if hq_screen is None:
            raise ProbeError(f"no offset registered as an HQ click: {hq_search}")
        result["hq_screen"] = hq_screen
        result["baseline_orders_undamaged_hq"] = baseline_orders

        # --- damage the HQ (halve HP) via the new bridge op=11
        new_hp = max(1, int(hq["hp"]) // 2)
        dmg = bridge.call(op=11, owner=0, slot=hq["slot"], rice=new_hp)
        result["damage_report"] = dmg
        if not dmg.get("ok"):
            raise ProbeError(f"HQ damage op failed: {dmg}")
        hq_hp_offset = UNIT_BASE + hq["slot"] * UNIT_STRIDE + UNIT_HP_OFFSET

        def hq_hp() -> int:
            return int.from_bytes(read_memory(pid, hq_hp_offset, 4), "little", signed=True)

        hq_hp_after_damage = hq_hp()
        result["hq_hp_after_damage"] = hq_hp_after_damage
        if not (0 < hq_hp_after_damage < hq["hp"]):
            raise ProbeError(f"HQ hp did not decrease as expected: before={hq['hp']} after={hq_hp_after_damage}")

        # --- post-damage: right-click the now-damaged HQ, record pending word(s).
        # lap730 found this is usually the SAME pending word as the undamaged
        # click (both show gather's 0x1000008 among the samples) -- this
        # engine appears not to encode "repair" as a distinct order word, so
        # reuse whichever non-move/stop word the (already-confirmed-hitting)
        # baseline click produced as the broadcast signature (see module
        # docstring), rather than hardcoding 0x1000008.
        damaged_orders = worker_orders_at(hq_screen)
        result["damaged_orders_damaged_hq"] = damaged_orders
        repair_candidates = [v for v in baseline_orders if v not in NON_SIGNAL_PENDING]
        if not repair_candidates:
            raise ProbeError(f"baseline click had no non-move/stop/idle pending word: {baseline_orders}")
        repair_pending = repair_candidates[0]
        if repair_pending not in damaged_orders:
            raise ProbeError(
                f"expected pending {repair_pending} (seen undamaged) when right-clicking the damaged HQ, "
                f"got {damaged_orders}")
        result["repair_pending"] = repair_pending
        xdo("key", "s")
        time.sleep(0.5)

        # --- spawn a worker-type-only fixture in the worker-centered grid
        requests = worker_grid_requests(worker)
        for req in requests:
            r = bridge.call(op=5, owner=0, type_=worker_type, rice=req["x"], wood=req["y"], used=req["count"])
            if not r.get("ok") or r.get("fixture_added") != req["count"]:
                raise ProbeError(f"fixture failed: {r}")
        time.sleep(1)
        snap("01-after-worker-fixture")
        fixture = spawned_worker_slots(pid, worker_type, VISIBLE_WORKER_SLOT)
        result["fixture_spawned"] = len(fixture)
        if len(fixture) != len(requests):
            raise ProbeError(f"expected {len(requests)} spawned workers, found {len(fixture)}")

        # --- select everything visible with one full drag, then repair-click
        click(*RESELECT_START, drag_to=RESELECT_END)
        time.sleep(0.8)
        selection = sel()
        result["selection"] = selection
        snap("02-after-fulldrag")
        slots = list(selection["slots"])
        if not slots:
            raise ProbeError("full drag selected nothing")

        obs = observe(pid, slots, lambda: click(*hq_screen, button=3), 4.0)
        result["repair_observe"] = obs
        snap("03-after-repair-click")
        if not alive():
            raise ProbeError("game not alive after repair click")

        # Supporting evidence (not a PASS gate, see module docstring): sample
        # the HQ's own HP for a few more seconds to see whether it is
        # actually climbing back up, confirming this is repair and not a
        # no-op ("deposit" with nothing carried).
        hp_curve = [{"t": 0.0, "hp": hq_hp()}]
        t0 = time.monotonic()
        while time.monotonic() - t0 < 6.0:
            time.sleep(0.5)
            hp_curve.append({"t": round(time.monotonic() - t0, 1), "hp": hq_hp()})
        result["hq_hp_curve_after_repair_click"] = hp_curve
        hq_hp_repairing = hp_curve[-1]["hp"] > hq_hp_after_damage

        repaired = obs.get("pending_ever", {}).get(repair_pending, 0)
        result["repair_summary"] = {
            "selected_count": selection["count"], "selected_unique": selection["unique_slots"],
            "repair_pending": repair_pending, "repaired_count": repaired,
            "all_selected_repaired": repaired == selection["unique_slots"],
            "capacity": sel_cap, "hq_hp_rising": hq_hp_repairing,
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
    print(json.dumps({k: res.get(k) for k in ("status", "error", "variant", "source_unchanged")}, ensure_ascii=False))
    return 0 if res.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
