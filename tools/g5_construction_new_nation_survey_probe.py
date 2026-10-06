#!/usr/bin/env python3
"""G5 checklist C construction re-adjudication (2026-09-28 08:15/10:06 operator
direction): sample fresh solo-lobby boots until a nation *not already surveyed*
(lap730/731/735: worker types {7,21,31}, HQ types {49,58,70}) shows up, then run
the same worker command-grid + HQ command-grid survey those laps used on it.

Rationale: lap730/731/735 all confirmed "no construction button" for three
solo-lobby nations, but the operator's 08:15 rejection of the "(C) construction
= N/A" verdict is specifically that the sample so far is too small (this genre
conventionally lets workers build) and a different nation's command grid was
never seen. This EXE does not appear to expose an explicit nation-select UI in
the solo lobby (every prior lap treated it as randomized-at-boot), so the only
way to broaden the sample is to reboot repeatedly and check.

Each attempt is a fully isolated boot (own runtime_env.prepare copy, own Xvfb
display, own wineserver teardown) so a "not new, discard" attempt costs a full
boot/lobby/PS3 cycle but touches nothing else. On the first attempt whose HQ
unit_type is outside the known set, this continues the *same* boot into the
full survey (worker V/I/F-equivalent buttons + HQ 8-button grid, including the
repair/"R" ground-click placement-mode check from g5_hq_command_grid_survey_probe)
instead of tearing down and rebooting, since the nation is only available for
the lifetime of that process.
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

# (worker_type, hq_type) pairs whose HQ command grid + worker ability grid
# were already fully surveyed for a construction/build button (STATUS
# 2026-09-28, lap731: "worker type31/HQ58과 worker type21/HQ70"). lap736's own
# reboot sampling (10 fresh boots, 2 timing strategies) found this solo-lobby
# fixture cycles through only 3 distinct nations -- (7, 49) is the third one
# and appeared in lap729/730 for gather/repair-command probes only, never for
# the HQ-grid/construction survey -- so it is treated as still-needing-survey,
# not "known", even though its worker/HQ type numbers were individually seen
# before.
ALREADY_SURVEYED_SIGNATURES = {(31, 58), (21, 70)}

WORKER_BUTTONS = {"stop": (667, 503), "move": (703, 503), "b3": (740, 503), "b4": (777, 503), "b5": (667, 538)}
HQ_BUTTONS = {"r": (703, 503), "d": (740, 503), "f": (667, 538), "c": (703, 538), "x": (740, 538), "z": (777, 538),
              "t": (777, 503)}
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


def run_attempt(
    source: Path, runtime_root: Path, artifact_root: Path, attempt_index: int, pre_confirm_delay: float = 0.0,
) -> dict[str, Any]:
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
        "schema": "syw2plus.g5-construction-new-nation-survey.v1", "attempt_index": attempt_index,
        "variant": "original", "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": sha256(private_exe), "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [], "inputs": [], "worker_button_probes": {}, "hq_button_probes": {},
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
        if pre_confirm_delay > 0:
            time.sleep(pre_confirm_delay)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            if runtime_env._read_local_ready_state(lambda a, n: read_memory(pid, a, n)).get("ready_value") == 1:
                break
            time.sleep(0.2)
        if pre_confirm_delay > 0:
            time.sleep(pre_confirm_delay)
        result["pre_confirm_delay"] = pre_confirm_delay
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] == 0:
            raise ProbeError(f"slot1198 is not the expected worker: {worker}")
        result["worker"] = worker
        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

        hq = find_hq_slot(pid, VISIBLE_WORKER_SLOT)
        result["hq"] = hq

        worker_type = int(worker["unit_type"])
        hq_type = int(hq["unit_type"])
        result["nation_signature"] = {"worker_type": worker_type, "hq_type": hq_type}
        is_new = (worker_type, hq_type) not in ALREADY_SURVEYED_SIGNATURES
        result["is_new_nation"] = is_new
        if not is_new:
            result["status"] = "KNOWN_NATION_SKIPPED"
            return result

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

        wx, wy = int(worker["x"]), int(worker["y"])
        ground_screen = w2s((wx + 4, wy - 4))

        for name, pt in WORKER_BUTTONS.items():
            if name in ("stop", "move"):
                continue  # already characterized by every prior checklist probe
            reselect_worker_only()
            xdo("key", "s")
            time.sleep(0.4)
            before = worker_state()
            before_slots = existing_slots(pid)
            click(*pt)
            time.sleep(1.5)
            after = worker_state()
            after_click_slots = existing_slots(pid)
            snap(f"01-worker-button-{name}-after-click")
            click(*ground_screen, button=3)
            time.sleep(1.0)
            after_ground = worker_state()
            after_ground_slots = existing_slots(pid)
            snap(f"02-worker-button-{name}-after-ground-followup")
            result["worker_button_probes"][name] = {
                "screen": list(pt), "before": before, "after_click": after,
                "after_ground_followup": after_ground, "alive": alive(),
                "new_slots_after_click": sorted(after_click_slots - before_slots),
                "new_slots_after_ground_followup": sorted(after_ground_slots - before_slots),
            }
            if not alive():
                raise ProbeError(f"game not alive after worker button {name}")

        # --- HQ selection: click the HQ's own tile and run the same 7-button
        # + repair-ground-click survey g5_hq_command_grid_survey_probe used.
        xdo("key", "s")
        time.sleep(0.4)
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
            result["status"] = "HQ_NOT_SELECTABLE"
            return result
        snap("03-hq-selected-baseline")
        baseline_slots = existing_slots(pid)
        result["baseline_slot_count"] = len(baseline_slots)
        open_ground = w2s((int(hq["x"]) - 4, int(hq["y"]) + 5))

        for name in BUTTON_ORDER:
            pt = HQ_BUTTONS[name]
            before_slots = existing_slots(pid)
            click(*pt)
            time.sleep(1.0)
            snap(f"04-hq-button-{name}-tooltip")
            after_click_slots = existing_slots(pid)
            still_alive = alive()
            entry: dict[str, Any] = {
                "screen": list(pt), "alive_after_click": still_alive,
                "new_slots_after_click": sorted(after_click_slots - before_slots),
            }
            if still_alive and name in ("r", "d"):
                click(*open_ground)
                time.sleep(1.5)
                snap(f"05-hq-button-{name}-after-ground-followup")
                after_followup_slots = existing_slots(pid)
                new = sorted(after_followup_slots - before_slots)
                entry["new_slots_after_ground_followup"] = new
                entry["new_slot_details"] = [slot_info(pid, s) for s in new]
                entry["alive_after_followup"] = alive()
            result["hq_button_probes"][name] = entry
            if not entry.get("alive_after_followup", still_alive):
                result["status"] = "PARTIAL_MATCH_ENDED"
                break
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


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, max_attempts: int,
    delays: list[float] | None = None,
) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    attempts: list[dict[str, Any]] = []
    final: dict[str, Any] | None = None
    for i in range(1, max_attempts + 1):
        attempt_root = artifact_root / f"attempt_{i:02d}"
        # lap736 run1 found 5 identical-timing back-to-back boots land on the
        # exact same nation every time (tick-seeded, not wall-clock-random);
        # run2 varied elapsed ticks before the ready-confirm click via
        # (i-1)*7s and cycled through the 3 known nations. Callers targeting
        # a specific still-unsurveyed nation pass an explicit delay list.
        pre_confirm_delay = delays[i - 1] if delays else float((i - 1) * 7)
        try:
            attempt = run_attempt(source, runtime_root, attempt_root, i, pre_confirm_delay)
        except ProbeError as exc:
            attempt = {"attempt_index": i, "status": "FAIL", "error": f"ProbeError: {exc}",
                       "pre_confirm_delay": pre_confirm_delay}
        attempts.append({k: attempt.get(k) for k in (
            "attempt_index", "status", "nation_signature", "is_new_nation", "pre_confirm_delay",
            "source_unchanged", "cleanup", "error")})
        if attempt.get("status") not in ("KNOWN_NATION_SKIPPED",):
            final = attempt
            break
    summary = {
        "schema": "syw2plus.g5-construction-new-nation-survey-summary.v1",
        "attempts_run": len(attempts), "attempts": attempts,
        "final_attempt_status": final.get("status") if final else "EXHAUSTED_ALL_KNOWN_NATIONS",
        "final_attempt_dir": str(artifact_root / f"attempt_{len(attempts):02d}") if attempts else None,
    }
    write_json(artifact_root / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2)[:4000])
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    ap.add_argument("--runtime-root", type=Path, required=True)
    ap.add_argument("--artifact-root", type=Path, required=True)
    ap.add_argument("--max-attempts", type=int, default=5)
    ap.add_argument("--delays", type=str, default=None,
                     help="comma-separated pre-confirm-click delay seconds, one per attempt")
    args = ap.parse_args(argv)
    delays = [float(x) for x in args.delays.split(",")] if args.delays else None
    if delays is not None and len(delays) < args.max_attempts:
        delays = delays + [delays[-1]] * (args.max_attempts - len(delays))
    res = run_probe(args.source, args.runtime_root, args.artifact_root, args.max_attempts, delays)
    ok_statuses = {"COMPLETE", "PARTIAL_MATCH_ENDED", "HQ_NOT_SELECTABLE", "EXHAUSTED_ALL_KNOWN_NATIONS"}
    return 0 if res.get("final_attempt_status") in ok_statuses else 2


if __name__ == "__main__":
    raise SystemExit(main())
