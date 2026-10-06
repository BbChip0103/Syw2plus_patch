#!/usr/bin/env python3
"""G5 checklist E: 50-selection portrait/info panel, HUD, health-bar display.

STATUS 2026-09-28 lap737 handoff: (A)-(D) are complete; (E) UI is the next
open item -- "50 selected -> portrait/info panel display, click, scroll; HUD
breakage; selection indicator (health bar) for all 50" was never exercised
by any prior probe (lap658/659 explicitly recorded it as SKIP: "the current
harness has no real input path" for portrait/info-panel UI).

This probe gives it a real input path using the same solo-lobby bootstrap,
worker-centered dense SEED_TYPE=2 fixture and DRAG_START/DRAG_END rectangle
every other G5 checklist probe already uses (lap658/682/717/723/724/734), so
results stay directly comparable (original 20 vs candidate 50, same fixture
positions).

What "portrait/info panel" concretely is in this engine (confirmed by
inspecting existing lap734 v6 roundtrip captures before writing this probe):
a diamond-shaped portrait slot bottom-left of the HUD that stays *black* for
both a lone selected worker and a 20/50-unit group (this engine never draws
per-unit portraits for a multi-selection -- only a text info line such as
"체력 500/500" for a single unit, which is itself blank/absent for a group
selection in both original and candidate). This probe re-confirms that live
for this run rather than trusting old opportunistic captures, and adds the
three things no earlier capture set covers: a click on that panel, a scroll
(mouse wheel) over it, and a per-unit health-bar visibility count.

Health-bar count method: each selected unit draws a small solid-green 5-dot
bar above its sprite (measured RGB exactly (0,188,0) on this capture, dots
~2px with a 1px gap between them, total width ~13px; distinct from the cyan
selection-corner brackets flanking it). This is counted by flood-fill
connected-component labelling (no scipy/cv2 dependency in this venv) over a
green color threshold with a radius-2 neighbor connection (radius-1/8-conn
undercounts to ~0 because the 1px gap between dots breaks strict 8-
connectivity -- verified against a hand-counted 13/13-selected capture,
where radius-1 fragments each bar into ~5 sub-4px pieces below the size
filter and radius-2 recovers exactly 13/13), cropped to the game viewport
only (excludes the HUD strip so HUD art is never miscounted as a bar). A
dense 1-tile-pitch fixture is known to visually overlap sprites (lap726/727/
728 documented this artifact for click isolation), so this probe also drags
a smaller sub-rectangle of the *same* fixture (same density) to get a same-
density, smaller-selection control count -- if the bar-shown/selected ratio
is roughly the same for the partial and full drag, a shortfall from the
nominal selected count is a density/occlusion artifact, not a rendering cap;
if the candidate's ratio collapses specifically past 20 selected, that would
indicate a real truncation.

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
from typing import Any, Callable, Mapping, cast

import numpy as np
from PIL import Image

from patches.selection import g5_selection_cap50_v6 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, SupplyProbe, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    SEED_TYPE, SEED_COUNT, VISIBLE_WORKER_SLOT,
    selection_snapshot, unit_snapshot, dense_fixture_requests, fixture_units,
    sha256, write_json, capture,
)
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
# v6 (lap733 death-recall fix); pinned SHA reconfirmed by lap734/735/736/737.
TARGET_SHA = "fdc913b5f42dc7cc2dcb258d3ecac43e2a2a79a24e4ce10ee362e8ded173805f"

# Portrait/info-panel diamond, measured from the lap734 v6 roundtrip captures
# (0,440)-(270,600) crop: the black diamond center sits at roughly (85, 550)
# in the same 800x600 click-coordinate space DRAG_START/ABILITY_BUTTONS use.
PORTRAIT_POINT = (85, 550)
# A smaller sub-rectangle of the same worker-centered dense grid, to get a
# same-density partial-selection control count without a second boot.
PARTIAL_DRAG_START = (200, 170)
PARTIAL_DRAG_END = (470, 300)
GAME_VIEWPORT = (0, 0, 800, 440)  # excludes the HUD strip (y>=440)
GREEN_BAR_MIN_PIXELS = 5
GREEN_BAR_MIN_WIDTH = 8
GREEN_BAR_CONNECT_RADIUS = 2
MINIMAP_CLICK_POINT = (235, 555)


def _components(mask: np.ndarray, *, radius: int = GREEN_BAR_CONNECT_RADIUS) -> list[tuple[int, int, int, int, int]]:
    """Flood fill with an N-pixel neighbor radius; returns (size, minx, maxx,
    miny, maxy) per blob. radius=1 (strict 8-connectivity) fragments each
    5-dot bar into ~5 isolated sub-4px pieces because the dots have a 1px
    gap between them -- radius=2 bridges that gap (verified: recovers
    exactly 13/13 on a hand-countable 13-unit capture where radius=1 finds
    0 bar-sized blobs)."""
    ys, xs = np.nonzero(mask)
    coords = set(zip(ys.tolist(), xs.tolist()))
    seen: set[tuple[int, int]] = set()
    comps: list[tuple[int, int, int, int, int]] = []
    offsets = [(dy, dx) for dy in range(-radius, radius + 1) for dx in range(-radius, radius + 1)]
    for y, x in zip(ys.tolist(), xs.tolist()):
        if (y, x) in seen:
            continue
        stack = [(y, x)]
        seen.add((y, x))
        size = 0
        minx = maxx = x
        miny = maxy = y
        while stack:
            cy, cx = stack.pop()
            size += 1
            minx, maxx = min(minx, cx), max(maxx, cx)
            miny, maxy = min(miny, cy), max(maxy, cy)
            for dy, dx in offsets:
                npt = (cy + dy, cx + dx)
                if npt in coords and npt not in seen:
                    seen.add(npt)
                    stack.append(npt)
        comps.append((size, minx, maxx, miny, maxy))
    return comps


def count_health_bars(image_path: Path, *, region: tuple[int, int, int, int] = GAME_VIEWPORT) -> dict[str, Any]:
    arr = np.array(Image.open(image_path).convert("RGB").crop(region))
    r, g, b = arr[..., 0].astype(int), arr[..., 1].astype(int), arr[..., 2].astype(int)
    mask = (g > 170) & (r < 100) & (b < 100)
    comps = _components(mask)
    bars = [c for c in comps if c[0] >= GREEN_BAR_MIN_PIXELS and (c[2] - c[1]) >= GREEN_BAR_MIN_WIDTH]
    return {"green_px": int(mask.sum()), "raw_components": len(comps), "bar_count": len(bars)}


def hud_region_stats(image_path: Path, *, region: tuple[int, int, int, int]) -> dict[str, Any]:
    """Plain mean/std sanity signal -- a corrupted/blank HUD renders as a
    near-uniform block; live HUD art never does (icons/borders/text)."""
    arr = np.array(Image.open(image_path).convert("L").crop(region))
    return {"mean": float(arr.mean()), "std": float(arr.std())}


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")

    candidate_bytes: bytes | None = None
    candidate_sha: str | None = None
    if variant == "candidate":
        candidate_bytes = g5.build_candidate(source_exe.read_bytes())[0]

    bridge_dir = artifact_root / "stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
    )
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge, timeout=60)
    game = Path(cast(str, cast(Mapping, manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping, manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private original copy failed pre-install check")
    if candidate_bytes is not None:
        private_exe.write_bytes(candidate_bytes)
        candidate_sha = sha256(private_exe)
        if candidate_sha != TARGET_SHA:
            raise ProbeError(f"G5 candidate SHA mismatch: {candidate_sha}")
    private_exe_sha = sha256(private_exe)
    selection_base = g5.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    selection_capacity = g5.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY
    expected_full = selection_capacity

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-ui-selection-hud.v1", "variant": variant, "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": private_exe_sha, "candidate_sha256": candidate_sha,
                       "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [], "inputs": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    game_proc: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
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

        def wait_for(pred: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> dict[str, Any]:
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

        def snap(name: str) -> Path:
            result["captures"].append(capture(display, artifact_root / f"{name}.png", log))
            return artifact_root / f"{name}.png"

        def sel() -> dict[str, Any]:
            return selection_snapshot(pid, base=selection_base, capacity=selection_capacity)

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
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        result["worker"] = worker

        # --- step 1: lone-worker baseline -- portrait panel + info text with
        # exactly one unit selected, and a click/scroll probe on that panel.
        click(*MINIMAP_CLICK_POINT)
        time.sleep(1)
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        solo_sel = sel()
        if VISIBLE_WORKER_SLOT not in solo_sel["slots"] or solo_sel["count"] != 1:
            raise ProbeError(f"expected the lone pre-existing worker only: {solo_sel}")
        snap("00-solo-selected")
        result["solo_selection"] = solo_sel
        click(*PORTRAIT_POINT)
        time.sleep(0.3)
        result["solo_portrait_click"] = {"selection_after": sel(), "alive": alive()}
        snap("01-solo-portrait-click")
        click(*PORTRAIT_POINT, button=4)
        time.sleep(0.2)
        click(*PORTRAIT_POINT, button=5)
        time.sleep(0.3)
        result["solo_portrait_scroll"] = {"selection_after": sel(), "alive": alive()}
        snap("02-solo-portrait-scroll")

        # --- step 2: spawn the dense worker-centered fixture (same positions
        # every other G5 checklist probe uses) and re-select the lone worker
        # before seeding so the fixture stays anchored the same way.
        supply = SupplyProbe(prefix)
        fixture_requests = dense_fixture_requests(worker)
        receipts = []
        for req in fixture_requests:
            r = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=req["x"], y=req["y"], count=req["count"])
            receipts.append(r)
            if not r.get("ok") or r.get("fixture_added") != req["count"]:
                raise ProbeError(f"dense fixture batch failed: {r}")
        if sum(int(r.get("fixture_added", 0)) for r in receipts) != SEED_COUNT:
            raise ProbeError(f"dense fixture total failed: {receipts}")
        time.sleep(1)
        result["fixture_units"] = fixture_units(pid)
        snap("03-after-fixture")

        # --- step 3: same-density partial selection (control for occlusion).
        click(*PARTIAL_DRAG_START, drag_to=PARTIAL_DRAG_END)
        time.sleep(1)
        partial = sel()
        partial_capture = snap("04-after-partial-drag")
        result["partial_selection"] = partial
        result["partial_bars"] = count_health_bars(partial_capture)

        # --- step 4: full drag -- the actual (E) target state (20 original /
        # 50 candidate).
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        full = sel()
        if full["count"] == 0:
            click(*DRAG_START, drag_to=DRAG_END)
            time.sleep(1)
            full = sel()
        result["full_selection"] = full
        full_capture = snap("05-after-full-drag")
        result["full_bars"] = count_health_bars(full_capture)
        result["hud_sanity"] = {
            "portrait_panel": hud_region_stats(full_capture, region=(10, 460, 175, 600)),
            "command_grid": hud_region_stats(full_capture, region=(650, 480, 800, 600)),
            "f_slot_row": hud_region_stats(full_capture, region=(270, 490, 645, 525)),
        }

        # --- step 5: portrait panel click + scroll with the full group
        # selected -- the actual untested (E) interaction.
        before_click_sel = full
        click(*PORTRAIT_POINT)
        time.sleep(0.3)
        after_click_sel = sel()
        snap("06-full-portrait-click")
        click(*PORTRAIT_POINT, button=4)
        time.sleep(0.2)
        click(*PORTRAIT_POINT, button=5)
        time.sleep(0.3)
        after_scroll_sel = sel()
        snap("07-full-portrait-scroll")
        result["full_portrait_interaction"] = {
            "before_click": before_click_sel,
            "after_click": after_click_sel,
            "after_scroll": after_scroll_sel,
            "alive_after_click": alive(),
            "alive_after_scroll": alive(),
            # A click/scroll on a panel that never draws anything for a
            # group selection is expected to be a no-op, not a crash or an
            # unrelated deselect -- record which one happened rather than
            # assuming.
            "selection_unchanged_by_click": after_click_sel["slots"] == before_click_sel["slots"],
            "selection_unchanged_by_scroll": after_scroll_sel["slots"] == after_click_sel["slots"],
        }
        if not alive():
            raise ProbeError("game not alive after portrait panel click/scroll")

        # Re-select before leaving so a following probe (or a human) sees the
        # full group, not whatever the panel interaction left behind.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(0.5)

        full_pass = full["count"] == expected_full and full["unique_slots"] == expected_full
        bar_pass = result["full_bars"]["bar_count"] > (STOCK_SELECTION_CAPACITY if variant == "candidate" else 0)
        no_crash = result["full_portrait_interaction"]["alive_after_click"] and result["full_portrait_interaction"]["alive_after_scroll"]
        result["checks"] = {
            "full_selection_at_capacity": full_pass,
            "bars_exceed_legacy_cap_for_candidate": bar_pass if variant == "candidate" else None,
            "hud_regions_not_blank": all(v["std"] > 3.0 for v in result["hud_sanity"].values()),
            "no_crash_on_portrait_interaction": no_crash,
        }
        result["status"] = "COMPLETE" if all(v is not False for v in result["checks"].values()) else "FAIL"
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
        "status", "error", "variant", "source_unchanged", "full_selection", "full_bars",
        "partial_selection", "partial_bars", "checks",
    )}, ensure_ascii=False, default=str))
    return 0 if res.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
