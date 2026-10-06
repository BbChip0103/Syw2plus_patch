#!/usr/bin/env python3
"""G5 checklist (H): 50-unit repeated-command long-run stability probe.

STATUS.md's accepted G5 candidate is v7 (``patches/selection/
g5_selection_cap50_v7.py``).  Checklist item (H) asks for "50기 반복 명령
수천 tick 단일플레이 격리 실행 안정성" -- a single isolated run that keeps
the same 50-unit drag selection alive across thousands of original engine
ticks while repeatedly cycling move/stop/hold/patrol orders at it, watching
for a crash, a process exit, or the live selection array losing its 50/50
shape.

Reference tick rate: ``docs/history/laps/20260911_status_lap168_compaction.md``
and the G2 24k observation (``docs/history/laps/
20260917_g2_stock_24k_observation_card.md``, 470.013s/15626 ticks) both put
the original engine's PS3 simulation at about 33.3 ticks/second, so a few
thousand ticks is a few minutes of wall time, not the 45-minute G2 ceiling.

This is read-only against the protected source; only the private per-run
copy is patched, exactly like the other G5 probes it borrows setup code
from.
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

from patches.selection import g5_selection_cap50_v7 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError,
    SupplyProbe,
    DRAG_START,
    DRAG_END,
    SEED_TYPE,
    VISIBLE_WORKER_SLOT,
    UNIT_BASE,
    UNIT_STRIDE,
    UNIT_COMMAND_OFFSET,
    UNIT_PENDING_COMMAND_OFFSET,
    selection_snapshot,
    unit_snapshot,
    dense_fixture_requests,
    fixture_units,
    sha256,
    write_json,
    capture,
)
from tools.g5_command_coverage_probe import BUTTONS
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256

DESTINATION_CANDIDATES = [
    (300, 420), (400, 300), (350, 250), (450, 350),
    (300, 350), (500, 300), (250, 300), (400, 420),
]
TARGET_TICKS = 8_000
WALL_SECONDS = 900.0
SAMPLE_SECONDS = 1.0
ACTION_EVERY_SAMPLES = 5


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, *,
    target_ticks: int = TARGET_TICKS, wall_seconds: float = WALL_SECONDS,
) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
    candidate_bytes, build_report = g5.build_candidate(source_exe.read_bytes())
    candidate_sha = build_report["candidate_sha256"]

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
        raise ProbeError("private copy pre-install check failed")
    private_exe.write_bytes(candidate_bytes)
    private_sha = sha256(private_exe)
    if private_sha != candidate_sha:
        raise ProbeError(f"candidate SHA mismatch: {private_sha}")
    sel_base = g5.SELECTION_BASE
    sel_cap = g5.TARGET_CAPACITY

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-long-run-stability-probe.v1",
        "status": "UNKNOWN",
        "provenance": {
            "source_sha256": sha256(source_exe),
            "private_exe_sha256": private_sha,
            "candidate_sha256": candidate_sha,
            "v7_report": build_report,
        },
        "target_ticks": target_ticks,
        "wall_seconds": wall_seconds,
        "sample_seconds": SAMPLE_SECONDS,
        "action_every_samples": ACTION_EVERY_SAMPLES,
        "captures": [],
        "inputs": [],
        "samples": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(
        os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
        LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
        SYW2_SUPPLY_PROBE="1",
    )
    try:
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,1600x1200"],
            cwd=game, env=env, stdout=log, stderr=log,
        ))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def wait_for(pred: Callable[[Mapping[str, Any]], bool], label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = read_state(pid)
                    if pred(last):
                        return last
                except (OSError, ValueError) as exc:
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

        def snap(name: str) -> None:
            result["captures"].append(capture(display, artifact_root / f"{name}.png", log))

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
        click(*MINIMAP_CLICK)
        time.sleep(1)

        # Validate two real ground move destinations with the worker alone
        # selected, the same technique lap739's stop/hold/patrol probe used,
        # before the 50-unit fixture exists to disturb the reading.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(0.8)
        worker_sel = selection_snapshot(pid, base=sel_base, capacity=sel_cap)
        if worker_sel["count"] != 1 or VISIBLE_WORKER_SLOT not in worker_sel["slots"]:
            raise ProbeError(f"worker-only selection did not settle: {worker_sel}")
        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

        def worker_order_at(screen: tuple[int, int]) -> list[str]:
            xdo("key", "s")
            time.sleep(0.6)
            got: set[str] = set()
            click(*screen, button=3)
            t0 = time.monotonic()
            while time.monotonic() - t0 < 0.4:
                got.add(hex(int.from_bytes(read_memory(pid, wbase + UNIT_PENDING_COMMAND_OFFSET, 4), "little")))
                time.sleep(0.005)
            return sorted(got)

        validation: list[dict[str, Any]] = []
        points: list[tuple[int, int]] = []
        for cand in DESTINATION_CANDIDATES:
            orders = worker_order_at(cand)
            ok = "0x1000003" in orders
            validation.append({"screen": list(cand), "orders": orders, "ok": ok})
            if ok:
                points.append(cand)
            if len(points) == 2:
                break
        result["destination_validation"] = validation
        if len(points) < 2:
            raise ProbeError(f"fewer than two valid move destinations found: {validation}")
        point_a, point_b = points[0], points[1]
        result["points"] = {"a": list(point_a), "b": list(point_b)}
        xdo("key", "s")
        time.sleep(0.3)

        supply = SupplyProbe(prefix)
        for request in dense_fixture_requests(worker):
            receipt = supply.call(
                op=5, owner=0, unit_type=SEED_TYPE,
                x=request["x"], y=request["y"], count=request["count"],
            )
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"dense fixture batch failed: {receipt}")
        time.sleep(1)
        result["fixture_units"] = fixture_units(pid)
        snap("00-after-fixture")

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        selection = selection_snapshot(pid, base=sel_base, capacity=sel_cap)
        result["selection_initial"] = selection
        snap("01-after-drag")
        if selection["count"] != 50 or selection["unique_slots"] != 50:
            raise ProbeError(f"initial 50-selection did not settle: {selection}")
        slots = list(cast(list[int], selection["slots"]))

        def moving_count() -> int:
            count = 0
            for slot in slots:
                base = UNIT_BASE + slot * UNIT_STRIDE
                command = int.from_bytes(read_memory(pid, base + UNIT_COMMAND_OFFSET, 2), "little", signed=True)
                if command != 0:
                    count += 1
            return count

        def patrol() -> None:
            click(*BUTTONS["patrol"])
            time.sleep(0.15)
            click(*point_a)

        actions: list[tuple[str, Callable[[], None]]] = [
            ("move_a", lambda: click(*point_a, button=3)),
            ("stop", lambda: click(*BUTTONS["stop"])),
            ("move_b", lambda: click(*point_b, button=3)),
            ("hold", lambda: click(*BUTTONS["hold"])),
            ("patrol", patrol),
            ("stop", lambda: click(*BUTTONS["stop"])),
        ]
        action_index = 0
        started = time.monotonic()
        deadline = started + wall_seconds
        first_tick: int | None = None
        last_tick: int | None = None
        sample_index = 0
        crash_detected = False
        selection_regressions = 0
        status = "OBSERVING"
        reason: str | None = None

        while True:
            now = time.monotonic()
            if now >= deadline:
                status, reason = "TIMEOUT_PARTIAL", f"{wall_seconds}s wall ceiling before {target_ticks} ticks"
                break
            if game_proc.poll() is not None:
                status, reason = "CRASH", f"game process exited rc={game_proc.poll()}"
                crash_detected = True
                break
            try:
                snapshot = read_state(pid)
            except (OSError, ValueError) as exc:
                status, reason = "CRASH", f"state read failed: {type(exc).__name__}: {exc}"
                crash_detected = True
                break
            tick = int(snapshot.get("tick", -1))
            ps = snapshot.get("ps")
            if first_tick is None:
                first_tick = tick
            last_tick = tick
            if ps != 3:
                status, reason = "NON_PS3_PARTIAL", f"left ps3 at tick={tick} ps={ps}"
                break
            try:
                sel_now = selection_snapshot(pid, base=sel_base, capacity=sel_cap)
            except ProbeError as exc:
                status, reason = "SELECTION_READ_ERROR", str(exc)
                break
            regression = sel_now["count"] != 50 or sel_now["unique_slots"] != 50
            if regression:
                selection_regressions += 1
            sample: dict[str, Any] = {
                "t": now - started, "tick": tick, "ps": ps,
                "selection_count": sel_now["count"], "selection_unique": sel_now["unique_slots"],
                "selection_regression": regression, "moving_count": moving_count(),
            }
            if sample_index % ACTION_EVERY_SAMPLES == 0:
                label, act = actions[action_index % len(actions)]
                act()
                action_index += 1
                sample["action"] = label
                result["inputs"].append({"action": label, "t": now - started, "tick": tick})
            result["samples"].append(sample)
            sample_index += 1
            if len(result["samples"]) % 40 == 0:
                snap(f"progress-{len(result['samples']):04d}")
            if first_tick is not None and tick - first_tick >= target_ticks:
                status, reason = "COMPLETE", None
                break
            time.sleep(SAMPLE_SECONDS)

        result["status_reason"] = reason
        result["first_tick"] = first_tick
        result["last_tick"] = last_tick
        result["ticks_observed"] = None if first_tick is None or last_tick is None else last_tick - first_tick
        result["selection_regressions"] = selection_regressions
        result["crash_detected"] = crash_detected
        snap("99-final")
        if not crash_detected:
            result["final_selection"] = selection_snapshot(pid, base=sel_base, capacity=sel_cap)
        result["status"] = status
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        cleanup_error: str | None = None
        try:
            subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            cleanup_error = f"{type(exc).__name__}: {exc}"
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
                xvfb.wait(timeout=5)
        result["cleanup"] = {
            "error": cleanup_error,
            "owned_children_stopped": all(child.poll() is not None for child in children),
            "xvfb_stopped": xvfb is None or xvfb.poll() is not None,
            "prefix_processes_after": runtime_env._prefix_pids(prefix),
            "global_kill_used": False,
        }
        result["cleanup"]["ok"] = not result["cleanup"]["prefix_processes_after"] and cleanup_error is None
        result["source_sha_after"] = sha256(source_exe)
        result["source_unchanged"] = result["source_sha_after"] == ORIGINAL_SHA
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--target-ticks", type=int, default=TARGET_TICKS)
    parser.add_argument("--wall-seconds", type=float, default=WALL_SECONDS)
    args = parser.parse_args(argv)
    result = run_probe(
        args.source, args.runtime_root, args.artifact_root,
        target_ticks=args.target_ticks, wall_seconds=args.wall_seconds,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    ok = (
        result.get("status") == "COMPLETE"
        and not result.get("crash_detected")
        and result.get("selection_regressions", 1) == 0
        and result.get("cleanup", {}).get("ok")
        and result.get("source_unchanged")
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
