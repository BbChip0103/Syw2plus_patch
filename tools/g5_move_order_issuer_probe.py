#!/usr/bin/env python3
"""Dynamically attribute the G5 selection-broadcast order issuer.

lap672-676 spent 12+ live runs trying to prove or falsify a *static* guess
about which function issues an order to every selected unit, and lap676's
xref scan falsified the standing "FUN_004AE550 = broadcast packer"
hypothesis outright. This probe stops guessing statically and instead reads
the answer directly out of the running candidate: it drag-selects the same
55-unit fixture used by every prior G5 probe (50 selectable), then performs
one already-known-good PLAIN right-click move (lap664's confirmed 50/50
broadcast) and one attack-toolbar+ground-click (lap674's confirmed
all-command-3 input) while a read-only gdb trace
(``tools/g5_order_issuer_entry_trace.py``) counts entries into a short list
of previously-identified candidate functions
(``op8_issuer_FUN_00415480`` / ``alt_issuer_FUN_00415880`` /
``group_assign_FUN_00445D30`` / ``order_consumer_FUN_0040F7D0`` /
``per_tick_dispatch_FUN_0048DDD0`` / ``attack_tick_gate_FUN_00471AF0`` /
``selection_toggle_FUN_00412D90`` / ``deselect_all_FUN_00417080``).

Whichever function's entry count during the move phase is >= the selected
count (50 for candidate, 20 for original) is the real broadcast issuer (or a
function it calls indirectly one level down, if none matches exactly); the
same count during the attack phase tells us whether that same function's
attack branch is reached for all selected units or stops short.

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
    STOCK_SELECTION_BASE,
    STOCK_SELECTION_CAPACITY,
    SEED_TYPE,
    SEED_COUNT,
    VISIBLE_WORKER_SLOT,
    selection_snapshot,
    unit_snapshot,
    dense_fixture_requests,
    sha256,
    write_json,
    capture,
)
from tools.g5_attack_move_broadcast_probe import (
    ATTACK_BUTTON,
    MINIMAP_CLICK,
    read_unit_full,
    is_attack_move,
)

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
TARGET_SHA = "ae495fa5a1498597c265ad9bcae6444f564ade92adb311a3c413c4fb9996b5b7"
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap677-order-issuer-trace"
GDB_SCRIPT = REPO / "tools" / "g5_order_issuer_entry_trace.py"


def run_gdb_phase(pid: int, control: Path, *, label: str, action) -> dict[str, Any]:
    """Attach a short read-only gdb trace, run ``action()``, detach, and return the summary."""
    control.mkdir(parents=True, exist_ok=True)
    armed = control / "armed.json"
    stop_flag = control / "stop.flag"
    summary_path = control / "entry-summary.json"
    events_path = control / "entry-events.jsonl"
    for stale in (armed, stop_flag, summary_path, events_path):
        stale.unlink(missing_ok=True)
    env = dict(os.environ, G5_ORDER_ISSUER_TRACE_CONTROL=str(control))
    log_path = control / f"gdb-{label}.log"
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
            raise ProbeError(f"{label}: gdb trace did not arm before timeout")
        time.sleep(0.2)
        try:
            action()
        finally:
            # lap677 run7/run8 held this window to 0.5s and saw only
            # 16-19/50 selected units reach the pending-order consumer;
            # widen it so a slower per-tick drain (rather than a real
            # broadcast cap) has a fair chance to finish within one phase.
            time.sleep(3.0)
            stop_flag.write_text("1", encoding="utf-8")
            # Every armed breakpoint's ``stop()`` returns False (non-invasive
            # trace), so gdb auto-resumes internally without ever returning
            # control to the script's ``gdb.execute("continue")`` call -- the
            # stop.flag file is never polled in practice. SIGINT is the
            # standard "Ctrl-C" async interrupt: it stops the running
            # inferior and returns control to the script, which then sees
            # stop.flag and reaches its own ``finally: gdb.execute("detach")``
            # cleanly. A raw SIGKILL here (tried in run6) can leave the
            # ptrace-stopped inferior orphaned and corrupt the next attach.
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
    summary: dict[str, Any] = {"label": label}
    if summary_path.exists():
        summary.update(json.loads(summary_path.read_text(encoding="utf-8")))
    else:
        summary["error"] = "no entry-summary.json written"
    return summary


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    source_exe = source / runtime_env.ORIGINAL_EXE
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_path = artifact_root / "g5_selection_cap50.exe"
    candidate_sha: str | None = None
    if variant == "candidate":
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

    if variant == "candidate":
        private_exe.write_bytes(candidate_path.read_bytes())
        if sha256(private_exe) != TARGET_SHA:
            raise ProbeError("private candidate SHA verification failed")
    selection_base = g5.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    selection_capacity = g5.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY
    expected_count = selection_capacity

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-move-order-issuer-probe.v1",
        "status": "UNKNOWN",
        "variant": variant,
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
            "candidate_sha256": candidate_sha,
            "private_exe_sha256": sha256(private_exe),
            "original_manifest_check": original_check,
            "bridge_sha256": sha256(bridge),
        },
        "inputs": [],
        "calibration_points": [],
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

        # lap677 run1-4 found the lone-worker calibration drag (the original
        # g5_screen_world_calibration.py / g5_attack_move_broadcast_probe.py
        # approach) unreliable here: the worker spawns standing on/against
        # the town hall's footprint, and a drag rectangle covering both
        # selects the *building* exclusively (its HP/defense panel appears,
        # but the unit-selection array at 0x899024 stays empty) rather than
        # the worker unit. run5 then found the affine-fit calibration itself
        # unreliable once 50 units share the selection: ``pending_xy`` is
        # transient (cleared as soon as the order is consumed into the live
        # ``x``/``y`` fields, apparently within one tick under simultaneous
        # 50-unit load) and read back as (0, 0) every time. This probe does
        # not need pixel-accurate targeting -- any valid empty-ground click
        # exercises the same broadcast code path -- so skip the affine
        # calibration entirely and use a screen point visually confirmed
        # (after-calibration-drag.png) to be open sand to the fixture's
        # upper-right, clear of the fixture/building/HUD.
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

        # lap677 run7 found (700, 180) lands on the decorative farmland tile
        # (visually confirmed in after-move-click.png) where a plain
        # right-click move produces zero effect on any selected unit; (300,
        # 420) is confirmed-open sand just below-left of the fixture
        # formation in the same capture, clear of farmland/building/HUD.
        destination_screen = (300, 420)
        result["destination_screen_computed"] = list(destination_screen)

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selection_after"] = after
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))
        if after["count"] != expected_count or after["unique_slots"] != expected_count:
            raise ProbeError(f"drag did not select the full fixture: {after}")

        control_root = artifact_root / "gdb_control"

        # --- Phase MOVE: the already-confirmed-working plain move broadcast
        # (lap664: candidate50/original20 both receive command==3 for every
        # selected unit). Trace which candidate function(s) are entered once
        # per selected unit during this single click.
        before_move = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]

        def do_move_click() -> None:
            click(*destination_screen, button=3)

        move_summary = run_gdb_phase(pid, control_root / "move", label="move", action=do_move_click)
        time.sleep(0.3)
        after_move = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]
        result["captures"].append(capture(display, artifact_root / "after-move-click.png", log))
        move_command_count = sum(1 for row in after_move if row.get("command") == 3)

        # --- Phase ATTACK: lap674's exact confirmed-FAIL input (attack
        # toolbar button + ground click at the same destination). Trace the
        # same candidate functions during this click.
        def do_attack_click() -> None:
            click(*ATTACK_BUTTON, button=1)
            time.sleep(0.1)
            click(*destination_screen, button=1)

        attack_summary = run_gdb_phase(pid, control_root / "attack", label="attack", action=do_attack_click)
        time.sleep(0.3)
        after_attack = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]
        result["captures"].append(capture(display, artifact_root / "after-attack-click.png", log))
        attack_move_count = sum(1 for row in after_attack if is_attack_move(row))

        result["before_move"] = before_move
        result["move_phase"] = {
            "summary": move_summary,
            "selected_count": len(before_move),
            "command3_count_after": move_command_count,
        }
        result["attack_phase"] = {
            "summary": attack_summary,
            "selected_count": len(before_move),
            "attack_move_count_after": attack_move_count,
        }
        result["status"] = "TRACE_COMPLETE"
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
    parser.add_argument("--variant", choices=("original", "candidate"), default="candidate")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root, variant=args.variant)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "TRACE_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
