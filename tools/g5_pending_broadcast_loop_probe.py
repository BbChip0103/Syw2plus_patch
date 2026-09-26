#!/usr/bin/env python3
"""Find the real G5 pending-order broadcast loop that calls the 0x40ff90 wrapper.

``g5_pending_broadcast_writer_probe.py`` found the per-unit order writer
(``0x412540``) and its immediate thin wrapper (``0x40ff90``, "slot -> unit
address, call 0x412540"), but neither has a decoded-call-immediate static
xref (indirect/table dispatch), so the actual loop that iterates the
selection and calls ``0x40ff90`` once per unit -- and is suspected of
stopping at a literal/stale count of 20 instead of the candidate's relocated
50-capacity selection -- is still unknown.

This probe drag-selects the same fixture, arms a read-only gdb entry trace
on ``0x40ff90`` (``tools/g5_pending_broadcast_loop_entry_trace.py``) that
captures each hit's return address directly from ``[esp]`` (reliable here;
frame-pointer-based ``bt`` was already shown to misread this ebp-less
function family), then sends one attack-toolbar+ground click -- the same
input already shown to write pending orders into exactly the first 20
selected units.

Read-only investigation: no product EXE bytes are touched here beyond the
already-approved G5 selection-cap50 candidate build.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any, Mapping, cast

from patches.selection import g5_selection_cap50_v2 as g5
from tools import runtime_env
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools.g5_candidate_drag_probe import (
    ProbeError,
    SupplyProbe,
    DRAG_START,
    DRAG_END,
    VISIBLE_WORKER_SLOT,
    SEED_TYPE,
    SEED_COUNT,
    selection_snapshot,
    unit_snapshot,
    dense_fixture_requests,
    sha256,
    write_json,
    capture,
)
from tools.g5_attack_move_broadcast_probe import ATTACK_BUTTON, MINIMAP_CLICK

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
TARGET_SHA = "ae495fa5a1498597c265ad9bcae6444f564ade92adb311a3c413c4fb9996b5b7"
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap678-pending-loop-trace"
GDB_SCRIPT = REPO / "tools" / "g5_pending_broadcast_loop_entry_trace.py"


def run_loop_entry_phase(pid: int, control: Path, *, action) -> dict[str, Any]:
    control.mkdir(parents=True, exist_ok=True)
    armed = control / "armed.json"
    stop_flag = control / "stop.flag"
    marker_flag = control / "click_marker.flag"
    summary_path = control / "trace-summary.json"
    events_path = control / "entry-events.jsonl"
    dispatch_events_path = control / "dispatch-events.jsonl"
    for stale in (armed, stop_flag, marker_flag, summary_path, events_path, dispatch_events_path):
        stale.unlink(missing_ok=True)
    env = dict(os.environ, G5_BROADCAST_LOOP_TRACE_CONTROL=str(control))
    log_path = control / "gdb-loop.log"
    with log_path.open("w", encoding="utf-8") as log:
        gdb_proc = subprocess.Popen(
            ["gdb", "-p", str(pid), "--batch", "-x", str(GDB_SCRIPT)],
            env=env, stdout=log, stderr=log,
        )
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not armed.exists():
            time.sleep(0.05)
        if not armed.exists():
            gdb_proc.terminate()
            raise ProbeError("loop entry trace did not arm before timeout")
        time.sleep(0.2)
        try:
            action(marker_flag)
        finally:
            time.sleep(1.0)
            stop_flag.write_text("1", encoding="utf-8")
            gdb_proc.send_signal(signal.SIGINT)
            try:
                gdb_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                gdb_proc.send_signal(signal.SIGINT)
                try:
                    gdb_proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    gdb_proc.kill()
                    gdb_proc.wait(timeout=5)
    summary: dict[str, Any] = {}
    if summary_path.exists():
        summary.update(json.loads(summary_path.read_text(encoding="utf-8")))
    else:
        summary["error"] = "no trace-summary.json written"
    events: list[dict[str, Any]] = []
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    summary["events"] = events
    dispatch_events: list[dict[str, Any]] = []
    if dispatch_events_path.exists():
        for line in dispatch_events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                dispatch_events.append(json.loads(line))
    summary["dispatch_events"] = dispatch_events
    return summary


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    source_exe = source / runtime_env.ORIGINAL_EXE
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_path = artifact_root / "g5_selection_cap50.exe"
    candidate_path.write_bytes(g5.build_candidate(source_exe.read_bytes())[0])
    candidate_sha = sha256(candidate_path)
    if candidate_sha != TARGET_SHA:
        raise ProbeError(f"G5 candidate SHA mismatch: {candidate_sha}")

    bridge_dir = artifact_root / "stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
    )
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge, timeout=60)
    manifest_output = manifest.get("output")
    manifest_game = manifest.get("game")
    manifest_wine = manifest.get("wine")
    if not isinstance(manifest_output, Mapping) or not isinstance(manifest_game, Mapping) or not isinstance(manifest_wine, Mapping):
        raise ProbeError("runtime manifest sections are malformed")
    run_dir_text = cast(str, manifest_output.get("run_dir"))
    game_root_text = cast(str, manifest_game.get("root"))
    prefix_root_text = cast(str, manifest_wine.get("prefix"))
    manifest_path = Path(run_dir_text) / "manifest.json"
    original_check = runtime_env.check_runtime(manifest_path)
    game = Path(game_root_text)
    prefix = Path(prefix_root_text)
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private original copy failed pre-install check")
    private_exe.write_bytes(candidate_path.read_bytes())
    if sha256(private_exe) != TARGET_SHA:
        raise ProbeError("private candidate SHA verification failed")

    selection_base = g5.SELECTION_BASE
    selection_capacity = g5.TARGET_CAPACITY

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-pending-broadcast-loop-probe.v1",
        "status": "UNKNOWN",
        "provenance": {
            "source_exe_sha256": sha256(source_exe),
            "candidate_sha256": candidate_sha,
            "private_exe_sha256": sha256(private_exe),
            "original_manifest_check": original_check,
            "bridge_sha256": sha256(bridge),
        },
        "inputs": [],
    }
    log_path = artifact_root / "probe.log"
    log = log_path.open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    display = ""
    pid: int | None = None
    try:
        env = dict(
            os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
            LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
            SYW2_SUPPLY_PROBE="1",
        )
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

        def state() -> dict[str, Any]:
            assert pid is not None
            return read_state(pid)

        def wait_for(predicate, label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = state()
                    if predicate(last):
                        return last
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda item: item.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window was not found")
        content_info = runtime_env._xwininfo_details(display, content, 10)
        crop = (int(content_info["x"]), int(content_info["y"]))

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "drag_to": list(drag_to) if drag_to else None, "button": button})

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda item: item.get("ps") == 7, "ps7")

        def read_selector() -> dict[str, Any]:
            assert pid is not None
            return runtime_env._read_lobby_selector(lambda address, size: read_memory(pid, address, size))

        if read_selector().get("selected") == "solo":
            click(344, 169)
            time.sleep(0.5)
        click(462, 169)
        deadline = time.monotonic() + 10
        while read_selector().get("selected") != "solo" and time.monotonic() < deadline:
            time.sleep(0.2)
        if read_selector().get("selected") != "solo":
            raise ProbeError("solo selector did not settle")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 5, "ps5")
        ready_deadline = time.monotonic() + 12
        ready: dict[str, Any] = {}
        while time.monotonic() < ready_deadline:
            ready = runtime_env._read_local_ready_state(lambda address, size: read_memory(pid, address, size))
            if ready.get("ready_value") == 1:
                break
            time.sleep(0.2)
        if ready.get("ready_value") != 1:
            raise ProbeError(f"local lobby did not become ready: {ready}")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        result["worker"] = worker
        supply = SupplyProbe(prefix)

        click(*MINIMAP_CLICK)
        time.sleep(1)
        result["captures"] = [capture(display, artifact_root / "after-minimap.png", log)]

        fixture_requests = dense_fixture_requests(worker)
        result["fixture"] = {"owner": 0, "type": SEED_TYPE, "count": SEED_COUNT, "requests": fixture_requests}
        receipts: list[dict[str, Any]] = []
        for request in fixture_requests:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=request["x"], y=request["y"], count=request["count"])
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"dense fixture batch failed: {receipt}")
        if sum(int(receipt.get("fixture_added", 0)) for receipt in receipts) != SEED_COUNT:
            raise ProbeError(f"dense fixture total failed: {receipts}")
        time.sleep(1)

        destination_screen = (300, 420)
        result["destination_screen_computed"] = list(destination_screen)

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selection_after"] = after
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))
        if after["count"] != selection_capacity or after["unique_slots"] != selection_capacity:
            raise ProbeError(f"drag did not select the full fixture: {after}")

        def do_attack_click(marker_flag: Path) -> None:
            click(*ATTACK_BUTTON, button=1)
            time.sleep(0.1)
            click(*destination_screen, button=1)
            marker_flag.write_text("1", encoding="utf-8")

        loop_trace = run_loop_entry_phase(pid, artifact_root / "gdb_control", action=do_attack_click)
        result["captures"].append(capture(display, artifact_root / "after-attack-click.png", log))
        result["loop_trace"] = loop_trace
        return_addresses = sorted({e.get("return_address") for e in loop_trace.get("events", [])})
        result["distinct_return_addresses"] = return_addresses
        result["status"] = "LOOP_TRACE_COMPLETE"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError) as exc:
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
        cur_env = locals().get("env", os.environ)
        try:
            subprocess.run(["wineserver", "-k"], env=cur_env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=cur_env, stdout=log, stderr=log, timeout=10, check=False)
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
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "LOOP_TRACE_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
