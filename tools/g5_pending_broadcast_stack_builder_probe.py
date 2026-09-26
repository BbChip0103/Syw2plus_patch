#!/usr/bin/env python3
"""Find the code that fills the G5 order-record stack buffer.

``g5_pending_broadcast_staging_probe.py`` proved a 60-byte "pending order"
record is assembled on the stack and copied wholesale (``rep movsd``, PC
``0x4a3c39``) into a global staging buffer at ``0x893130``, and that the
record's unit-list sub-array is a 20-word (40-byte) fixed size. It could not
identify the stack builder itself because the source stack address is only
knowable live (see ``g5_pending_broadcast_stack_builder_trace.py``).

This probe: drags-selects the dense 55-unit fixture (50 reachable), issues a
MOVE order first (learns the stack address from its copy-out write), then
issues an ATTACK order at the *same* stack address (captured by fresh
watchpoints armed after the MOVE click) to find the PC/backtrace of the code
writing the record's unit-count field and its first/last unit-list words.

Read-only investigation: no product EXE bytes are touched beyond the
already-approved G5 selection-cap50 candidate build.

SUPERSEDED (kept for provenance): the second order never re-triggers the
0x893130 marker regardless of destination or wait time --
``g5_pending_broadcast_staging_rotation_probe.py`` found why with a plain
memory diff (no gdb): a second order issued while an earlier one is still in
flight patches the existing 0x893130 record's header fields *in place*
rather than rebuilding+copying a fresh one, so there is nothing to
correlate against for a second click in the same process. The successful
approach (single session, single *first* order, hardcoded stack address) is
``tools/g5_order_record_builder_trace.py`` / ``_probe.py``, which found the
actual builder function and its hardcoded 20-unit loop bound.
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
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap679-stack-builder-trace"
GDB_SCRIPT = REPO / "tools" / "g5_pending_broadcast_stack_builder_trace.py"
MOVE_DESTINATION_SCREEN = (300, 420)
ATTACK_DESTINATION_SCREEN = (60, 300)


def _wait_file(path: Path, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            return True
        time.sleep(0.05)
    return path.exists()


def _stop_gdb(gdb_proc: subprocess.Popen, stop_flag: Path) -> None:
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


def run_trace_phase(pid: int, control: Path, *, move_click, attack_click) -> dict[str, Any]:
    """Two separate gdb attach sessions: ``learn`` then ``fields``.

    A single-session version that created hardware watchpoints and
    self-deleted from inside another watchpoint's ``stop()`` callback
    crashed gdb itself (internal SIGSEGV, see module docstring in
    ``g5_pending_broadcast_stack_builder_trace.py``). Two clean attach/detach
    cycles against the same live pid avoid that entirely.
    """
    control.mkdir(parents=True, exist_ok=True)
    stop_flag = control / "stop.flag"
    base_found = control / "base-found.json"
    events_path = control / "builder-events.jsonl"
    for stale in (stop_flag, base_found, events_path,
                  control / "armed-learn.json", control / "armed-fields.json",
                  control / "trace-summary-learn.json", control / "trace-summary-fields.json"):
        stale.unlink(missing_ok=True)
    phase: dict[str, Any] = {}

    # --- session 1: learn the stack address from the MOVE click's copy-out.
    armed_learn = control / "armed-learn.json"
    env_learn = dict(os.environ, G5_STACK_BUILDER_TRACE_CONTROL=str(control),
                      G5_STACK_BUILDER_TRACE_MODE="learn")
    log_path = control / "gdb-stack-builder-learn.log"
    with log_path.open("w", encoding="utf-8") as log:
        gdb_proc = subprocess.Popen(
            ["gdb", "-p", str(pid), "--batch", "-x", str(GDB_SCRIPT)],
            env=env_learn, stdout=log, stderr=log,
        )
        if not _wait_file(armed_learn, 20):
            gdb_proc.terminate()
            raise ProbeError("stack-builder learn session did not arm before timeout")
        time.sleep(0.2)
        move_click()
        phase["base_found_before_attack"] = _wait_file(base_found, 15)
        try:
            gdb_proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            gdb_proc.terminate()
            gdb_proc.wait(timeout=5)
    if not base_found.exists():
        raise ProbeError("learn session never observed the 0x893130 copy-out during the MOVE click")
    phase["stack_base"] = json.loads(base_found.read_text(encoding="utf-8"))["stack_base"]

    # --- session 2: watch the learned address while issuing the ATTACK click.
    armed_fields = control / "armed-fields.json"
    env_fields = dict(os.environ, G5_STACK_BUILDER_TRACE_CONTROL=str(control),
                       G5_STACK_BUILDER_TRACE_MODE="fields")
    log_path = control / "gdb-stack-builder-fields.log"
    with log_path.open("w", encoding="utf-8") as log:
        gdb_proc = subprocess.Popen(
            ["gdb", "-p", str(pid), "--batch", "-x", str(GDB_SCRIPT)],
            env=env_fields, stdout=log, stderr=log,
        )
        if not _wait_file(armed_fields, 20):
            gdb_proc.terminate()
            raise ProbeError("stack-builder fields session did not arm before timeout")
        time.sleep(0.2)
        try:
            attack_click()
        finally:
            # The three "hot" stack-slot watchpoints trap on every unrelated
            # write to that reused scratch address (hundreds/sec), which
            # slows the debuggee dramatically under gdb's ptrace overhead --
            # a short real-time wait was observed to end before the game's
            # own order-processing tick ever ran. Give it much longer.
            time.sleep(20.0)
            _stop_gdb(gdb_proc, stop_flag)
    summary: dict[str, Any] = {}
    learn_summary_path = control / "trace-summary-learn.json"
    fields_summary_path = control / "trace-summary-fields.json"
    if learn_summary_path.exists():
        summary["learn"] = json.loads(learn_summary_path.read_text(encoding="utf-8"))
    if fields_summary_path.exists():
        summary["fields"] = json.loads(fields_summary_path.read_text(encoding="utf-8"))
    else:
        summary["error"] = "no trace-summary-fields.json written"
    events: list[dict[str, Any]] = []
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    summary["events"] = events
    summary.update(phase)
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
        "schema": "syw2plus.g5-pending-broadcast-stack-builder-probe.v1",
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

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selection_after"] = after
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))
        if after["count"] != selection_capacity or after["unique_slots"] != selection_capacity:
            raise ProbeError(f"drag did not select the full fixture: {after}")

        def do_move_click() -> None:
            click(*MOVE_DESTINATION_SCREEN, button=3)

        def do_attack_click() -> None:
            click(*ATTACK_BUTTON, button=1)
            time.sleep(0.1)
            click(*ATTACK_DESTINATION_SCREEN, button=1)

        trace = run_trace_phase(pid, artifact_root / "gdb_control",
                                 move_click=do_move_click, attack_click=do_attack_click)
        result["captures"].append(capture(display, artifact_root / "after-attack-click.png", log))
        result["stack_builder_trace"] = trace
        result["status"] = "STACK_BUILDER_TRACE_COMPLETE"
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
    return 0 if result.get("status") == "STACK_BUILDER_TRACE_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
