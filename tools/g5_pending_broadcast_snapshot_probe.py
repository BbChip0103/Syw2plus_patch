#!/usr/bin/env python3
"""Directly count how many selected units receive a pending broadcast order.

lap677 run7-run9 found that raw breakpoint entry counts into
``FUN_0040C640``/``FUN_00415880`` cannot answer "how many of the 50 selected
units actually received a pending order from the click" -- ``FUN_0040C640``
runs once per *live* unit every tick regardless of whether that unit has a
pending order, so its entry count tracks the live population, not the
broadcast. lap677's own "다음 한 가지" asks for the field value directly: read
``unit+0x384`` (the pending-command word) for every selected unit at an
instant before this tick's consumption pass has touched any of them.

This probe drag-selects the same dense (or, with ``--fixture-layout
sparse``, a widely spaced control) 55-unit type2 fixture used by every prior
G5 order-issuer probe, arms a read-only gdb snapshot trace
(``tools/g5_pending_broadcast_snapshot_trace.py``) that takes an atomic
memory read of every selected unit's pending-command word the instant the
per-unit consumer function is entered, then performs the already-confirmed
plain move click (lap664) and the already-confirmed attack-toolbar+ground
click (lap674) while the trace is armed. The first post-click snapshot's
``pending_written_count`` (units with ``pending_command != 1``) is the direct
answer to "how many did the broadcast actually reach" -- not a proxy call
count.

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
    UNIT_BASE,
    UNIT_STRIDE,
    UNIT_COMMAND_OFFSET,
    UNIT_PENDING_COMMAND_OFFSET,
    UNIT_PENDING_XY_OFFSET,
    UNIT_PENDING_TARGET_UID_OFFSET,
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
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap678-pending-broadcast-snapshot"
GDB_SCRIPT = REPO / "tools" / "g5_pending_broadcast_snapshot_trace.py"


def sparse_fixture_requests(worker: Mapping[str, Any]) -> list[dict[str, int]]:
    """Return a widely spaced 55-cell grid so no two fixture units are adjacent.

    lap677's next-work asked for a sparse control fixture to rule out the
    dense 7x8 grid's rearmost row failing to path-find (rather than a real
    broadcast/consumption cap) as the explanation for the ~14-16/50 units
    that actually moved. This grid uses a step of 2 world tiles on both axes
    (8 columns x 7 rows, dropping one cell to land on exactly 55) so every
    unit's four neighbours are two tiles away -- no shared or bordering
    tiles, unlike the dense grid's step-1 packing.
    """
    worker_x = int(worker["x"])
    worker_y = int(worker["y"])
    columns = [-7, -5, -3, -1, 1, 3, 5, 7]
    rows = [-7, -5, -3, -1, 1, 3, 5]
    requests: list[dict[str, int]] = []
    for dy in rows:
        for dx in columns:
            requests.append({"x": worker_x + dx, "y": worker_y + dy, "count": 1})
    requests = requests[:SEED_COUNT]
    if any(not 0 <= item[axis] < 180 for item in requests for axis in ("x", "y")):
        raise ProbeError(f"sparse fixture falls outside the 180x180 map: {requests}")
    if sum(item["count"] for item in requests) != SEED_COUNT:
        raise ProbeError(f"sparse fixture count mismatch: {requests}")
    return requests


def read_unit_full(pid: int, slot: int) -> dict[str, Any]:
    base = UNIT_BASE + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "command": int.from_bytes(read_memory(pid, base + UNIT_COMMAND_OFFSET, 2), "little", signed=True),
        "pending_command": int.from_bytes(
            read_memory(pid, base + UNIT_PENDING_COMMAND_OFFSET, 4), "little", signed=False,
        ),
        "pending_xy": int.from_bytes(
            read_memory(pid, base + UNIT_PENDING_XY_OFFSET, 4), "little", signed=False,
        ),
        "pending_target_uid": int.from_bytes(
            read_memory(pid, base + UNIT_PENDING_TARGET_UID_OFFSET, 4), "little", signed=False,
        ),
    }


def run_snapshot_phase(
    pid: int, control: Path, *, label: str, selection_base: int, selection_capacity: int,
    action,
) -> dict[str, Any]:
    """Attach the pending-broadcast snapshot trace, run ``action()``, detach."""
    control.mkdir(parents=True, exist_ok=True)
    armed = control / "armed.json"
    stop_flag = control / "stop.flag"
    marker_flag = control / "click_marker.flag"
    summary_path = control / "trace-summary.json"
    samples_path = control / "snapshots.jsonl"
    for stale in (armed, stop_flag, marker_flag, summary_path, samples_path):
        stale.unlink(missing_ok=True)
    write_json(control / "target.json", {
        "selection_base": hex(selection_base),
        "selection_capacity": selection_capacity,
        "unit_base": hex(UNIT_BASE),
        "unit_stride": hex(UNIT_STRIDE),
        "command_offset": hex(UNIT_COMMAND_OFFSET),
        "pending_offset": hex(UNIT_PENDING_COMMAND_OFFSET),
        "pending_xy_offset": hex(UNIT_PENDING_XY_OFFSET),
        "pending_target_uid_offset": hex(UNIT_PENDING_TARGET_UID_OFFSET),
    })
    env = dict(os.environ, G5_PENDING_SNAPSHOT_CONTROL=str(control))
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
            raise ProbeError(f"{label}: gdb snapshot trace did not arm before timeout")
        time.sleep(0.2)
        try:
            action(marker_flag)
        finally:
            # Give the breakpoint a window to collect its post-marker
            # samples (see MAX_POST_MARKER_SAMPLES in the trace script)
            # before ending the phase.
            time.sleep(1.0)
            stop_flag.write_text("1", encoding="utf-8")
            # See tools/g5_move_order_issuer_probe.py::run_gdb_phase for why
            # SIGINT (not SIGKILL) is required here: non-invasive
            # (``stop()`` always ``False``) breakpoints make gdb auto-resume
            # internally, so only an async interrupt returns control to the
            # script's own ``finally: detach``.
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
        summary["error"] = "no trace-summary.json written"
    samples: list[dict[str, Any]] = []
    if samples_path.exists():
        for line in samples_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                samples.append(json.loads(line))
    summary["samples"] = samples
    summary["first_sample_pending_written_count"] = (
        samples[0].get("pending_written_count") if samples else None
    )
    return summary


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, *, variant: str, fixture_layout: str,
) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if fixture_layout not in {"dense", "sparse"}:
        raise ProbeError(f"unsupported fixture layout: {fixture_layout}")
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
        "schema": "syw2plus.g5-pending-broadcast-snapshot-probe.v1",
        "status": "UNKNOWN",
        "variant": variant,
        "fixture_layout": fixture_layout,
        "provenance": {
            "source_root": str(source),
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

        fixture_requests = (
            dense_fixture_requests(worker) if fixture_layout == "dense" else sparse_fixture_requests(worker)
        )
        result["fixture"] = {
            "owner": 0, "type": SEED_TYPE, "count": SEED_COUNT, "layout": fixture_layout,
            "requests": fixture_requests,
        }
        receipts: list[dict[str, Any]] = []
        for request in fixture_requests:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=request["x"], y=request["y"], count=request["count"])
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"{fixture_layout} fixture batch failed: {receipt}")
        if sum(int(receipt.get("fixture_added", 0)) for receipt in receipts) != SEED_COUNT:
            raise ProbeError(f"{fixture_layout} fixture total failed: {receipts}")
        time.sleep(1)
        result["captures"].append(capture(display, artifact_root / "after-fixture.png", log))

        # lap677 run7-run9 confirmed (700, 180) lands on farmland (no-op) and
        # (300, 420) is open sand below-left of the dense fixture; the
        # sparse fixture's footprint is wider (columns -7..7, rows -7..5) but
        # this destination remains outside both layouts' occupied cells.
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

        # --- Phase MOVE: lap664's confirmed-working plain move broadcast
        # (candidate50/original20 both eventually reach command==3 for every
        # selected unit). Snapshot the pending word immediately after this
        # click as a known-good baseline for the snapshot method itself.
        def do_move_click(marker_flag: Path) -> None:
            click(*destination_screen, button=3)
            marker_flag.write_text("1", encoding="utf-8")

        move_snapshot = run_snapshot_phase(
            pid, control_root / "move", label="move",
            selection_base=selection_base, selection_capacity=selection_capacity,
            action=do_move_click,
        )
        time.sleep(0.3)
        after_move = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]
        result["captures"].append(capture(display, artifact_root / "after-move-click.png", log))
        move_command_count = sum(1 for row in after_move if row.get("command") == 3)

        # --- Phase ATTACK: lap674's exact confirmed-FAIL input (attack
        # toolbar button + ground click at the same destination). This is
        # the click under test.
        def do_attack_click(marker_flag: Path) -> None:
            click(*ATTACK_BUTTON, button=1)
            time.sleep(0.1)
            click(*destination_screen, button=1)
            marker_flag.write_text("1", encoding="utf-8")

        attack_snapshot = run_snapshot_phase(
            pid, control_root / "attack", label="attack",
            selection_base=selection_base, selection_capacity=selection_capacity,
            action=do_attack_click,
        )
        time.sleep(0.3)
        after_attack = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]
        result["captures"].append(capture(display, artifact_root / "after-attack-click.png", log))

        result["before_selected_count"] = len(after["slots"])
        result["move_phase"] = {
            "snapshot": move_snapshot,
            "selected_count": len(after["slots"]),
            "command3_count_after": move_command_count,
        }
        result["attack_phase"] = {
            "snapshot": attack_snapshot,
            "selected_count": len(after["slots"]),
            "after_units": after_attack,
        }
        move_pending = move_snapshot.get("first_sample_pending_written_count")
        attack_pending = attack_snapshot.get("first_sample_pending_written_count")
        result["pending_broadcast_summary"] = {
            "selected_count": expected_count,
            "move_pending_written_immediate": move_pending,
            "attack_pending_written_immediate": attack_pending,
            "move_broadcast_reached_all_selected": move_pending == expected_count,
            "attack_broadcast_reached_all_selected": attack_pending == expected_count,
        }
        result["status"] = "SNAPSHOT_COMPLETE"
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
    parser.add_argument("--fixture-layout", choices=("dense", "sparse"), default="dense")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(
        args.source, args.runtime_root, args.artifact_root,
        variant=args.variant, fixture_layout=args.fixture_layout,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "SNAPSHOT_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
