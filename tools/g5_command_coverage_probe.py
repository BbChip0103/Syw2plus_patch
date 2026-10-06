#!/usr/bin/env python3
"""G5 v3 command coverage: paired original20 / candidate50 for the common
group commands beyond move/attack (2026-09-27 direct session).

Wraps the lap682 worker-relative flow (``g5_worker_relative_move_attack_probe``):
same solo lobby, same dense 55-unit type-2 fixture around the pre-existing
worker (slot 1198), same in-run 9-point screen->world affine.  Adds:

* minimap calibration: right-click inside the minimap diamond with only the
  worker selected, read its +0x388 pending xy, fit minimap->world affine;
* per-command raw sampling of +0x290 (live command) and +0x384 (pending word)
  for every selected slot, reported as "slots that showed value V after the
  input and did not already hold V immediately before it";
* command buttons from the in-game panel (S stop, M move, A attack, P patrol,
  H hold -- letters printed on the buttons, see capture);
* ALT / Ctrl modified drags and clicks, reading the variant's live selection
  count (original 0x899024, candidate relocated 0x0108C000).

Every step records whether the game process is still alive and a capture.
The protected original is only read (SHA before/after); the candidate is
rebuilt from it and SHA-verified.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable, Mapping, cast

import numpy as np

from patches.selection import g5_selection_cap50_v3 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, SupplyProbe, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    SEED_TYPE, SEED_COUNT, VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_XY_OFFSET,
    UNIT_X_OFFSET, selection_snapshot, unit_snapshot, dense_fixture_requests,
    sha256, write_json, capture,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_worker_relative_move_attack_probe import CALIBRATION_SCREEN_POINTS
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
TARGET_SHA = "e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977"

# Command panel buttons (800x600 render coords; letters printed on buttons).
BUTTONS = {"stop": (667, 503), "move": (703, 503), "attack": (667, 538), "patrol": (703, 538), "hold": (740, 538)}
# Minimap diamond measured from lap688 after-fixture capture: left (5,553),
# top (90,510), right (177,553), bottom (90,597).
MINIMAP_CENTER = (90, 553)
MINIMAP_CAL_POINTS = [(90, 553), (60, 553), (120, 553), (90, 535), (90, 571), (70, 543), (110, 563)]
# Reselection box: nearly the whole 800x600 render area above the UI bar.
RESELECT_START = (12, 40)
RESELECT_END = (788, 470)
SAMPLE_INTERVAL = 0.1
DEST_A = (0, 6)   # lap682-proven open tile
DEST_C = (0, 0)   # worker tile (grid centre)


def read_row(pid: int, slot: int) -> dict[str, int]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    block = read_memory(pid, base + 0x290, 0x100)
    xy = read_memory(pid, base + UNIT_X_OFFSET, 4)
    return {
        "slot": slot,
        "command": int.from_bytes(block[0:2], "little", signed=True),
        "pending": int.from_bytes(block[0xF4:0xF8], "little"),
        "pending_xy": int.from_bytes(block[0xF8:0xFC], "little"),
        "x": int.from_bytes(xy[0:2], "little", signed=True),
        "y": int.from_bytes(xy[2:4], "little", signed=True),
    }


def read_rows_bulk(pid: int, slots: list[int]) -> dict[int, dict[str, int]]:
    """One process_vm_readv over the whole slot span (fast, near-atomic sample)."""
    lo, hi = min(slots), max(slots)
    base = UNIT_BASE + lo * UNIT_STRIDE
    blob = read_memory(pid, base, (hi - lo + 1) * UNIT_STRIDE)
    rows: dict[int, dict[str, int]] = {}
    for s in slots:
        o = (s - lo) * UNIT_STRIDE
        rows[s] = {
            "slot": s,
            "command": int.from_bytes(blob[o + 0x290:o + 0x292], "little", signed=True),
            "pending": int.from_bytes(blob[o + 0x384:o + 0x388], "little"),
            "pending_xy": int.from_bytes(blob[o + 0x388:o + 0x38C], "little"),
        }
    return rows


FAST_WINDOW = 1.5
FAST_INTERVAL = 0.01


def observe(pid: int, slots: list[int], act: Callable[[], None], window: float) -> dict[str, Any]:
    """Baseline sample, perform ``act``, then sample ``window`` seconds.

    Sampling uses one bulk read per sample, every 10 ms for the first 1.5 s
    (the stop/hold pending words live < 0.1 s), then every 100 ms.  For each
    field reports, per value V, how many slots showed V after the input while
    their last pre-input value was not V ("changed_to") and how many showed V
    at all ("ever").
    """
    slots = [s for s in slots if 0 < s < 1200]
    before = read_rows_bulk(pid, slots)
    act()
    start = time.monotonic()
    seen: dict[int, dict[str, set[int]]] = {s: {"command": set(), "pending": set()} for s in slots}
    last: dict[int, dict[str, int]] = {}
    curve: list[dict[str, Any]] = []
    n_samples = 0
    while (elapsed := time.monotonic() - start) < window:
        last = read_rows_bulk(pid, slots)
        n_samples += 1
        for s, row in last.items():
            seen[s]["command"].add(row["command"])
            seen[s]["pending"].add(row["pending"])
        if len(curve) < 40 and (n_samples % 5 == 1 or elapsed >= FAST_WINDOW):
            curve.append({"t": round(elapsed, 3),
                          "cmd": _hist(r["command"] for r in last.values()),
                          "pend": _hist(hex(r["pending"]) for r in last.values())})
        time.sleep(FAST_INTERVAL if elapsed < FAST_WINDOW else SAMPLE_INTERVAL)
    out: dict[str, Any] = {"n_slots": len(slots), "n_samples": n_samples,
                           "before_command": _hist(r["command"] for r in before.values()),
                           "before_pending": _hist(hex(r["pending"]) for r in before.values())}
    for field in ("command", "pending"):
        ever: dict[str, int] = {}
        changed: dict[str, int] = {}
        for s in slots:
            for v in seen[s][field]:
                key = hex(v) if field == "pending" else str(v)
                ever[key] = ever.get(key, 0) + 1
                if before[s][field] != v:
                    changed[key] = changed.get(key, 0) + 1
        out[f"{field}_ever"] = dict(sorted(ever.items()))
        out[f"{field}_changed_to"] = dict(sorted(changed.items()))
    out["final_command"] = _hist(r["command"] for r in last.values())
    out["final_pending"] = _hist(hex(r["pending"]) for r in last.values())
    out["final_pending_xy"] = _hist(str(decode_xy(r["pending_xy"])) for r in last.values())
    out["curve_head"] = curve
    return out


def _img_diff(a: Path, b: Path) -> float | None:
    try:
        from PIL import Image, ImageChops
        ia = Image.open(a).convert("L").crop((0, 30, 800, 480))
        ib = Image.open(b).convert("L").crop((0, 30, 800, 480))
        hist = ImageChops.difference(ia, ib).histogram()
        return round(sum(i * n for i, n in enumerate(hist)) / (800 * 450), 2)
    except (OSError, ImportError):
        return None


def _hist(values) -> dict[str, int]:
    h: dict[str, int] = {}
    for v in values:
        h[str(v)] = h.get(str(v), 0) + 1
    return dict(sorted(h.items()))


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
        "schema": "syw2plus.g5-command-coverage.v1", "variant": variant, "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": private_sha, "game_root": str(game), "run_dir": str(game.parent)},
        "steps": {}, "captures": [], "inputs": [],
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
                  mod: str | None = None, clicks: int = 1, interval_ms: int = 150) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            elif clicks > 1:
                argv += ["--repeat", str(clicks), "--interval-ms", str(interval_ms)]
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
                                     "button": button, "mod": mod, "clicks": clicks})

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
        snap("00-after-minimap-leftclick-legacy-point")

        # --- screen calibration (worker only), lap682 method
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
        result["screen_calibration"] = {"samples": [[list(p), list(w)] for p, w in samples],
                                        "matrix": matrix.tolist(), "offset": offset.tolist(), "max_abs_residual": resid}
        minv = np.linalg.inv(matrix)

        def w2s(world: tuple[int, int]) -> tuple[int, int]:
            p = minv @ (np.array(world) - offset)
            return int(round(p[0])), int(round(p[1]))

        # --- minimap calibration (worker only): does minimap right-click issue an order?
        mm_samples: list[dict[str, Any]] = []
        for pt in MINIMAP_CAL_POINTS:
            before_xy = worker_pending_xy()
            before_pend = int.from_bytes(read_memory(pid, wbase + 0x384, 4), "little")
            click(*pt, button=3)
            time.sleep(0.5)
            mm_samples.append({"minimap": list(pt), "before_xy": list(before_xy), "after_xy": list(worker_pending_xy()),
                               "before_pending": hex(before_pend),
                               "after_pending": hex(int.from_bytes(read_memory(pid, wbase + 0x384, 4), "little")),
                               "after_command": int.from_bytes(read_memory(pid, wbase + 0x290, 2), "little", signed=True)})
        snap("01-after-minimap-calibration")
        distinct = {tuple(s["after_xy"]) for s in mm_samples}
        mm_fit: dict[str, Any] = {"samples": mm_samples, "distinct_targets": len(distinct)}
        mm_inv = None
        mm_off = None
        if len(distinct) >= 4:
            mm_matrix, mm_off = fit_affine([(tuple(s["minimap"]), tuple(s["after_xy"])) for s in mm_samples])
            mm_fit["matrix"] = mm_matrix.tolist()
            mm_fit["offset"] = mm_off.tolist()
            mm_fit["max_abs_residual"] = max(
                float(np.max(np.abs(mm_matrix @ np.array(s["minimap"]) + mm_off - np.array(s["after_xy"]))))
                for s in mm_samples)
            mm_inv = np.linalg.inv(mm_matrix)
        result["minimap_calibration"] = mm_fit
        wx, wy = int(worker["x"]), int(worker["y"])

        def dest(off: tuple[int, int]) -> dict[str, Any]:
            world = (wx + off[0], wy + off[1])
            return {"offset": list(off), "world": list(world), "screen": list(w2s(world))}

        # Validate move destinations with the lone worker: a right-click must
        # queue a plain MOVE (pending low word 3), not gather/attack (8/4...).
        def worker_order_at(screen: list[int]) -> list[str]:
            xdo("key", "s")
            time.sleep(0.6)
            got: set[str] = set()
            click(*screen, button=3)
            t0 = time.monotonic()
            while time.monotonic() - t0 < 0.4:
                got.add(hex(int.from_bytes(read_memory(pid, wbase + 0x384, 4), "little")))
                time.sleep(0.005)
            return sorted(got)

        # lap724: some spawn worlds (observed world (93,56), lap723/lap724) are
        # resource-dense around the worker so most nearby offsets queue a
        # gather order (0x1000008) instead of a plain move -- the original 7
        # candidates then yield <2 "move_ok" hits.  Extend the search with
        # more directions/distances (still bounded to the visible screen by
        # the filter below) before giving up.
        validation: list[dict[str, Any]] = []
        chosen: list[dict[str, Any]] = []
        for off in (DEST_A, (0, -4), (3, 6), (-3, 6), (5, 2), (-4, 2), DEST_C,
                    (0, -6), (0, -8), (2, -6), (-2, -6), (4, -4), (-4, -4),
                    (6, -2), (-6, -2), (0, 7), (0, -2), (1, -8), (-1, -8)):
            d = dest(off)
            if not (0 < d["screen"][0] < 790 and 45 < d["screen"][1] < 465):
                continue
            orders = worker_order_at(d["screen"])
            ok = "0x1000003" in orders
            validation.append({**d, "worker_pending_seen": orders, "move_ok": ok})
            if ok:
                chosen.append(d)
            if len(chosen) >= 2:
                break
        result["destination_validation"] = validation
        if len(chosen) < 2:
            raise ProbeError(f"fewer than two valid ground-move destinations: {validation}")
        xdo("key", "s")
        time.sleep(0.5)

        for req in dense_fixture_requests(worker):
            r = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=req["x"], y=req["y"], count=req["count"])
            if not r.get("ok") or r.get("fixture_added") != req["count"]:
                raise ProbeError(f"fixture failed: {r}")
        time.sleep(1)
        snap("02-after-fixture")
        dest_a, dest_c = chosen[0], chosen[1]
        result["destinations"] = {"A": dest_a, "C": dest_c}

        def reselect(label: str) -> list[int]:
            click(*RESELECT_START, drag_to=RESELECT_END)
            time.sleep(0.8)
            s = sel()
            result["steps"].setdefault(label, {})["selection"] = s
            return list(s["slots"])

        def settle(slots: list[int], timeout: float = 12) -> None:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if all(read_row(pid, s)["command"] in (0, 1) for s in slots):
                    return
                time.sleep(0.3)

        def step(label: str, act: Callable[[], None], window: float, *, pre: Callable[[], None] | None = None) -> list[int]:
            slots = reselect(label)
            if pre is not None:
                pre()
            obs = observe(pid, slots, act, window)
            st = result["steps"][label]
            st["observe"] = obs
            st["alive_after"] = alive()
            snap(f"{len(result['steps']):02d}-{label}")
            if not st["alive_after"]:
                raise ProbeError(f"game not alive after {label}")
            return slots

        # 1. move by ground right-click -> A
        slots = step("move_ground_rclick", lambda: click(*dest_a["screen"], button=3), 4.0)
        result["steps"]["move_ground_rclick"]["dest"] = dest_a
        settle(slots)
        # 2. minimap right-click -> C
        if mm_inv is not None and mm_off is not None:
            p = mm_inv @ (np.array(dest_c["world"]) - mm_off)
            mm_pt = (int(round(p[0])), int(round(p[1])))
            slots = step("move_minimap_rclick", lambda: click(*mm_pt, button=3), 4.0)
            result["steps"]["move_minimap_rclick"]["minimap_point"] = list(mm_pt)
            result["steps"]["move_minimap_rclick"]["target_world"] = dest_c["world"]
            settle(slots)
        else:
            result["steps"]["move_minimap_rclick"] = {"skipped": "minimap right-click produced <4 distinct worker targets"}
            click(*dest_c["screen"], button=3)
            time.sleep(3)
        # 3. stop: start a move toward A, then S button
        slots = step("stop_button", lambda: click(*BUTTONS["stop"]), 3.0,
                     pre=lambda: (click(*dest_a["screen"], button=3), time.sleep(0.6)))
        # 4. hold button (window widened from 3.0 to 10.0 on 2026-09-28 lap749 to
        # tell a sampling-window artifact from a real non-delivery regression --
        # candidate v8 showed 0/50..50/50..3/50 pending_changed_to across three
        # window=3.0 runs while the original stayed 20/20 every time)
        slots = step("hold_button", lambda: click(*BUTTONS["hold"]), 10.0)
        # 5. patrol: P button then left-click C
        slots = step("patrol_button", lambda: (click(*BUTTONS["patrol"]), time.sleep(0.15),
                                               click(*dest_c["screen"])), 6.0)
        result["steps"]["patrol_button"]["dest"] = dest_c
        # stop the patrol so the modifier tests start from idle units
        click(*BUTTONS["stop"])
        time.sleep(0.5)
        settle(slots, 5)
        # 6. hotkeys (letters on buttons) as a second input method
        slots = step("stop_hotkey_s", lambda: xdo("key", "s"), 2.5,
                     pre=lambda: (click(*dest_a["screen"], button=3), time.sleep(0.6)))
        slots = step("hold_hotkey_h", lambda: xdo("key", "h"), 2.5)
        slots = step("patrol_hotkey_p", lambda: (xdo("key", "p"), time.sleep(0.15), click(*dest_c["screen"])), 5.0)
        click(*BUTTONS["stop"])
        time.sleep(0.5)
        settle(slots, 5)

        # --- ALT / Ctrl experiments.  A "small box" is ~2x2 tiles around the
        # current position of one fixture unit; clicks target a unit's tile.
        def unit_screen(slot: int) -> tuple[int, int]:
            r = read_row(pid, slot)
            return w2s((r["x"], r["y"]))

        def small_box(slot: int) -> tuple[tuple[int, int], tuple[int, int]]:
            x, y = unit_screen(slot)
            return (x - 30, y - 30), (x + 30, y + 20)

        def deselect() -> None:
            click(*dest_a["screen"])  # left-click on ground (no unit ideally)
            time.sleep(0.5)

        def unit_types(slots_: list[int]) -> dict[str, int]:
            return _hist(int.from_bytes(read_memory(pid, UNIT_BASE + s * UNIT_STRIDE + 0x8D, 1), "little") for s in slots_)

        mods: dict[str, Any] = {}
        all_slots = reselect("mod_setup_all")
        fixture_slots = [s for s in all_slots if s != VISIBLE_WORKER_SLOT]
        pos = {s: (read_row(pid, s)["x"], read_row(pid, s)["y"]) for s in fixture_slots}
        anchor1 = fixture_slots[0]
        anchor2 = max(fixture_slots, key=lambda s: abs(pos[s][0] - pos[anchor1][0]) + abs(pos[s][1] - pos[anchor1][1]))
        mods["anchors"] = {"a1": [anchor1, list(pos[anchor1]), list(unit_screen(anchor1))],
                           "a2": [anchor2, list(pos[anchor2]), list(unit_screen(anchor2))]}

        def record(name: str) -> list[int]:
            time.sleep(0.8)
            s = sel()
            mods[name] = {"count": s["count"], "unique": s["unique_slots"], "types": unit_types(s["slots"]),
                          "slots": s["slots"], "legacy_count": s.get("legacy_count"), "alive": alive()}
            snap(f"mod-{name}")
            if not mods[name]["alive"]:
                raise ProbeError(f"game not alive after {name}")
            return list(s["slots"])

        # find a click offset that selects a single unit (sprite drawn above its tile)
        click_dy = None
        for dy in (-12, -20, -6, 0, -28):
            deselect()
            ux, uy = unit_screen(anchor1)
            click(ux, uy + dy)
            time.sleep(0.6)
            if sel()["count"] > 0:
                click_dy = dy
                break
        mods["unit_click_dy"] = click_dy

        for mod_name, keysym in (("plain", None), ("alt", "Alt_L"), ("ctrl", "Control_L"), ("shift", "Shift_L")):
            deselect()
            b1 = small_box(anchor1)
            click(*b1[0], drag_to=b1[1], mod=keysym)
            record(f"{mod_name}_smalldrag_from_empty")
            # add-to-selection test: plain small drag first, then modified small drag elsewhere
            deselect()
            click(*b1[0], drag_to=b1[1])
            first = record(f"{mod_name}_pre_plain_smalldrag")
            b2 = small_box(anchor2)
            click(*b2[0], drag_to=b2[1], mod=keysym)
            second = record(f"{mod_name}_second_smalldrag")
            mods[f"{mod_name}_second_smalldrag"]["kept_from_first"] = len(set(first) & set(second))
            # single-unit click with modifier
            if click_dy is not None:
                deselect()
                ux, uy = unit_screen(anchor1)
                click(ux, uy + click_dy, mod=keysym)
                record(f"{mod_name}_click_unit")
                # modifier click on a second unit while one is selected
                ux2, uy2 = unit_screen(anchor2)
                click(ux2, uy2 + click_dy, mod=keysym)
                record(f"{mod_name}_click_second_unit")
            # full-screen modified drag
            deselect()
            click(*RESELECT_START, drag_to=RESELECT_END, mod=keysym)
            record(f"{mod_name}_fulldrag")
            # modified full drag on top of an existing full selection
            click(*RESELECT_START, drag_to=RESELECT_END, mod=keysym)
            record(f"{mod_name}_fulldrag_again")

        # G5 checklist B "ALT/Ctrl 클릭 같은 종류 전체 선택": a single modified
        # click on one unit only selects that unit here too (same count==1 as
        # plain_click_unit recorded above) -- no select-all-visible-same-type
        # behaviour is triggered by the modifier alone, distinct from the
        # modifier *drag* add/replace semantics already covered above.
        mods["alt_click_same_type_select"] = mods.get("alt_click_unit", {}).get("count", 0) > 1
        mods["ctrl_click_same_type_select"] = mods.get("ctrl_click_unit", {}).get("count", 0) > 1

        # G5 checklist B "더블클릭 같은 종류 전체 선택": does a plain rapid
        # double left-click on one unit select every same-type unit visible
        # (vs. the plain single click's count==1)?  Live check -- not yet
        # exercised by any prior lap.
        if click_dy is not None:
            deselect()
            ux, uy = unit_screen(anchor1)
            click(ux, uy + click_dy, clicks=2, interval_ms=150)
            record("doubleclick_unit")
            mods["doubleclick_same_type_select"] = mods["doubleclick_unit"]["count"] > 1
        else:
            mods["doubleclick_unit"] = None
            mods["doubleclick_same_type_select"] = None

        # Shift+click toggle-off (G5 checklist B "Shift 제거"): select two
        # distinct units with shift, then shift+click the first one again --
        # PASS = it is removed and the second one stays selected.
        if click_dy is not None:
            deselect()
            ux1, uy1 = unit_screen(anchor1)
            click(ux1, uy1 + click_dy, mod="Shift_L")
            ux2, uy2 = unit_screen(anchor2)
            click(ux2, uy2 + click_dy, mod="Shift_L")
            before_toggle = record("shift_toggle_before_remove")
            click(ux1, uy1 + click_dy, mod="Shift_L")
            after_toggle = record("shift_toggle_after_remove")
            mods["shift_toggle_removed_anchor1"] = anchor1 in before_toggle and anchor1 not in after_toggle
            mods["shift_toggle_kept_anchor2"] = anchor2 in after_toggle
            mods["shift_toggle_count_delta"] = len(before_toggle) - len(after_toggle)
            # Command targeting after the toggle-off: observe the two anchor
            # slots directly (no reselect() in between, unlike step()) so a
            # move order actually distinguishes "still selected" (anchor2)
            # from "removed by shift-click" (anchor1) instead of both being
            # re-swept back into the selection by a fresh full drag.
            toggle_obs = observe(pid, [anchor1, anchor2], lambda: click(*dest_a["screen"], button=3), 3.0)
            mods["shift_toggle_move_observe"] = toggle_obs
            # PASS = exactly 1 of the 2 observed slots (anchor2) picked up the
            # move order; 2 would mean the shift-click removal did not stop
            # anchor1 from still receiving broadcast commands.
            mods["shift_toggle_anchor1_excluded_from_move"] = toggle_obs["command_changed_to"].get("3") == 1
            settle([anchor1, anchor2])
        else:
            mods["shift_toggle_removed_anchor1"] = None
            mods["shift_toggle_kept_anchor2"] = None
            mods["shift_toggle_count_delta"] = None

        result["modifier_tests"] = mods
        # G5 checklist B "51번째 거부": the dense fixture places SEED_COUNT
        # same-type units around the worker (plus the worker itself, also
        # selectable); a capacity-N candidate must select exactly
        # min(SEED_COUNT+1, N) via the plain full drag recorded above.
        plain_full = mods.get("plain_fulldrag", {})
        pool_total = SEED_COUNT + 1
        result["fifty_first_rejection"] = {
            "fixture_total": SEED_COUNT,
            "pool_total_with_worker": pool_total,
            "selected_count": plain_full.get("count"),
            "selected_unique": plain_full.get("unique"),
            "capacity": sel_cap,
            "matches_capacity": plain_full.get("unique") == min(pool_total, sel_cap),
        }
        # confirm the group still takes orders after all modifier selections
        slots = step("move_after_modifier_tests", lambda: click(*dest_a["screen"], button=3), 3.0)
        settle(slots)

        # --- minimap experiments at the end (they may move the camera)
        mmx: dict[str, Any] = {}
        slots = reselect("minimap_setup")

        def mm_obs(name: str, act: Callable[[], None]) -> None:
            before_img = artifact_root / f"mm-{name}-before.png"
            capture(display, before_img, log)
            mmx[name] = observe(pid, slots, act, 3.0)
            mmx[name]["alive"] = alive()
            after_img = artifact_root / f"mm-{name}-after.png"
            capture(display, after_img, log)
            mmx[name]["render_diff"] = _img_diff(before_img, after_img)
            settle(slots, 8)

        mm_obs("rclick_center", lambda: click(*MINIMAP_CENTER, button=3))
        mm_obs("rclick_left", lambda: click(60, 553, button=3))
        mm_obs("move_hotkey_then_lclick", lambda: (xdo("key", "m"), time.sleep(0.15), click(120, 553)))
        mm_obs("move_button_then_lclick", lambda: (click(*BUTTONS["move"]), time.sleep(0.15), click(70, 543)))
        mm_obs("lclick_camera", lambda: click(60, 553))
        mm_obs("rclick_after_camera", lambda: click(110, 563, button=3))
        result["minimap_experiments"] = mmx
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
