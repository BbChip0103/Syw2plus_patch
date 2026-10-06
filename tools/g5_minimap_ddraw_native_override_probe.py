#!/usr/bin/env python3
"""G5 user item (2), sub-question (2): does the shipped native ``ddraw.dll``
(2.3MB DirectDraw wrapper, present under ``[ESL]Syw2plus/``) make the
bottom-left diamond HUD widget render anything other than solid black under
Wine, and if so does a right-click inside it then issue a move order the way
a real minimap would?

Prior negative evidence (read-only, no code path changed here):
  - lap677/lap710 (docs/history/laps/20260927_lap710_..._minimap_blocked...):
    with Wine's *builtin* ddraw (``WINEDLLOVERRIDES=ddraw=b``, the override
    every other G5/G4 probe in this tree uses), the diamond widget at screen
    (relative to the 800x600 game content window) x in [0,176] y in [511,598]
    stayed solid black across 9 right-clicks + 9 left-clicks, and the
    "compass dial" widget at (235,555) was independently falsified as a
    rotating clock/direction indicator, not a minimap.
  - lap759 (g5_minimap_widget_ctor_lap759.md): the minimap *widget struct*
    (static address 0x639350/0x639354, X/Y fields) is not dead code -- it is
    initialized to (0, 509) once, at new-game start, in the same code region
    as the rest of new-game init. So the engine does set up a minimap widget;
    only the on-screen rendering has never been observed.

This probe's only new variable is the DirectDraw backend: it boots the
*same* solo lobby twice, once with the override every prior probe used
(``ddraw=b``, builtin -- the negative-control repeat) and once with the
override never tried before (``ddraw=n,b``, prefer the native DLL shipped
next to the original EXE, falling back to builtin only if Wine can't load
it). Both runs crop the identical diamond rectangle from a full-screen
capture and record simple pixel statistics (unique color count, stddev) so
the two variants can be compared without relying on a human eyeballing a
PNG. If the native run's crop is not statistically flat black, a right-click
in the same rectangle is then attempted and the live worker's
``pending_xy``/``pending command`` fields are read to see if a move order
was queued (the same PASS signal ``g5_attack_move_broadcast_probe``/
``g5_worker_relative_move_attack_probe`` use for other order types).

Only the protected original is used (read-only; SHA verified before and
after every run). No candidate/EXE bytes are touched. No global queue/state
outside this run's private ``local/runtime/<run>`` directory is read or
written.
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

from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError,
    DRAG_START,
    DRAG_END,
    UNIT_BASE,
    UNIT_STRIDE,
    UNIT_PENDING_COMMAND_OFFSET,
    UNIT_PENDING_XY_OFFSET,
    VISIBLE_WORKER_SLOT,
    unit_snapshot,
    sha256,
    write_json,
    capture,
)
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256

# lap710's measured diamond rectangle, screen-relative to the 800x600 game
# content window (not the 1600x1200 Xvfb desktop). This wider box also
# includes the surrounding stone-frame decoration and the dragon-head status
# icon above it, so it is kept only for visual/archival captures.
DIAMOND_BOX = (0, 511, 176, 598)  # (left, top, right, bottom)
# lap760 sampled this run's builtin-ddraw baseline screenshot pixel-by-pixel
# (python3 -c crop scan) and found this smaller rectangle is pure flat black
# (unique_colors==1, stddev==0.0) with zero contamination from the frame
# decoration -- it sits fully inside the diamond interior, so it is the
# actual render-signal region compared between ddraw variants.
DIAMOND_INNER_BOX = (60, 540, 120, 570)
DIAMOND_CLICK = (88, 554)  # visual center, same point lap710 right/left-clicked

DDRAW_VARIANTS = {
    "builtin_control": "ddraw=b",
    "native_test": "ddraw=n,b",
}


def crop_stats(png_path: Path, box: tuple[int, int, int, int]) -> dict[str, Any]:
    img = Image.open(png_path).convert("RGB")
    crop = img.crop(box)
    arr = np.asarray(crop)
    colors = np.unique(arr.reshape(-1, 3), axis=0)
    return {
        "box": list(box),
        "size": list(crop.size),
        "unique_colors": int(colors.shape[0]),
        "mean_rgb": [float(x) for x in arr.reshape(-1, 3).mean(axis=0)],
        "stddev_rgb": [float(x) for x in arr.reshape(-1, 3).std(axis=0)],
        "is_flat": bool(colors.shape[0] <= 2 and float(arr.std()) < 1.0),
    }


def run_variant(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    dll_override = DDRAW_VARIANTS[variant]
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")

    manifest = runtime_env.prepare(source, runtime_root=runtime_root, timeout=60)
    game = Path(cast(str, cast(Mapping, manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping, manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private copy pre-install check failed")
    private_sha = sha256(private_exe)

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-minimap-ddraw-native-override.v1", "variant": variant,
        "dll_override": dll_override, "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": private_sha, "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32",
               WINEDEBUG=os.environ.get("SYW2_WINEDEBUG", "-all"),
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES=dll_override)
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
        crop_origin = (int(info["x"]), int(info["y"]))
        result["content_window"] = {"x": crop_origin[0], "y": crop_origin[1],
                                     "width": int(info.get("width", 0)), "height": int(info.get("height", 0))}

        def xdo(*args: str) -> None:
            subprocess.run(["xdotool", *args], env=env, stdout=log, stderr=log, timeout=10, check=True)

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop_origin[0] + x), str(crop_origin[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop_origin[0] + drag_to[0]), str(crop_origin[1] + drag_to[1])]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)

        def snap(name: str) -> Path:
            path = artifact_root / f"{name}.png"
            result["captures"].append(capture(display, path, log))
            return path

        def selector() -> Any:
            return runtime_env._read_lobby_selector(lambda a, n: read_memory(pid, a, n)).get("selected")

        xdo("windowfocus", outer)
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")
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
        time.sleep(1.5)  # let one animation frame settle before the baseline capture

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] == 0:
            raise ProbeError(f"slot1198 is not the expected worker: {worker}")
        result["worker_before"] = worker

        before_png = snap("00-ingame-before-minimap-click")
        result["diamond_before"] = crop_stats(before_png, DIAMOND_BOX)
        result["diamond_inner_before"] = crop_stats(before_png, DIAMOND_INNER_BOX)

        # select the worker first (as every prior order probe does) so a
        # queued move order is attributable to *this* click, not idle noise.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(0.6)

        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

        def pending() -> dict[str, int]:
            return {
                "command": int.from_bytes(read_memory(pid, wbase + UNIT_PENDING_COMMAND_OFFSET, 4), "little"),
                "xy_raw": int.from_bytes(read_memory(pid, wbase + UNIT_PENDING_XY_OFFSET, 4), "little"),
            }

        result["pending_before_click"] = pending()
        click(*DIAMOND_CLICK, button=3)
        time.sleep(0.6)
        result["pending_after_click"] = pending()

        after_png = snap("01-ingame-after-minimap-rightclick")
        result["diamond_after"] = crop_stats(after_png, DIAMOND_BOX)
        result["diamond_inner_after"] = crop_stats(after_png, DIAMOND_INNER_BOX)
        result["worker_after"] = unit_snapshot(pid, VISIBLE_WORKER_SLOT)

        result["minimap_render_signal"] = not result["diamond_inner_before"]["is_flat"]
        result["minimap_click_signal"] = result["pending_before_click"] != result["pending_after_click"]
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
    ap.add_argument("--variant", choices=tuple(DDRAW_VARIANTS), required=True)
    args = ap.parse_args(argv)
    res = run_variant(args.source, args.runtime_root, args.artifact_root, variant=args.variant)
    print(json.dumps(
        {k: res.get(k) for k in ("status", "error", "variant", "dll_override", "source_unchanged",
                                  "minimap_render_signal", "minimap_click_signal",
                                  "diamond_inner_before", "pending_before_click", "pending_after_click")},
        ensure_ascii=False))
    return 0 if res.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
