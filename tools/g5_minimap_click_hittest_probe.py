#!/usr/bin/env python3
"""G5 user item (2), minimap sub-question -- find and exercise the actual
mouse-click -> minimap-region -> world-coordinate handler (2026-09-29 12:37
operator direction: "1 lap 한정" breakpoint investigation of the minimap
click input handler).

Static disassembly of the protected original (this lap) found the concrete
routing chain the operator described, downstream of the widget lap759
already confirmed is constructed once at new-game start (``this`` =
``0x00639350``, X/Y = (0, 509)):

  * The click router (``~0x41e440``-``0x41e60c``) reads the last mouse
    position and calls the widget's own hit-test method,
    ``FUN_004516A0(this=0x639350, mouse_x, mouse_y, &out_tile_x,
    &out_tile_y)``. Only if that call returns 0 (fail) does the router fall
    back to the already-well-characterised main-viewport hit-test
    (``0x00417db0``, see ``tools/g5_screen_world_calibration.py``).
  * ``FUN_004516A0`` bounds-checks the click at screen x in
    [widget.x, widget.x+0xB4] = [0,180], y in (widget.y, widget.y+0x5A] =
    (509,599] for this session -- almost exactly the "diamond" HUD region
    lap710 already click-tested (x in [0,176], y in [511,598]) and found to
    have zero effect on any selected unit.
  * If in bounds, it looks up two interleaved LUT bytes per screen pixel at
    ``this+0x13eea + (dy*180 + dx)*2`` (dy=mouse_y-widget.y, dx=mouse_x-
    widget.x) -- an isometric screen-offset -> tile-delta table. It returns
    1 (success) only if *neither* byte is the sentinel ``0xFF``
    ("outside the diamond map render"); otherwise it returns 0 (fail).
  * ``FUN_00451130`` (the widget ctor lap759 traced) *unconditionally*
    fills that whole LUT region with ``0xFF`` (``or eax,0xffffffff; rep
    stos``) before doing anything else -- then, in the same function body,
    loops over the map's tiles (bound: a dword field at ``this+0x2baa0``)
    baking real (non-``0xFF``) tile-delta bytes into the diamond-shaped
    subset of the LUT that corresponds to actual map terrain.

This means the *geometric* hit-test bounds are real and correct (matching
what lap710 already click-tested), but whether any click inside them can
ever succeed depends entirely on whether that baking loop actually ran with
a non-zero tile count. This probe answers that empirically and completely
non-invasively:

  1. Reads the raw LUT bytes directly from the live process (no gdb write,
     no control-flow change) and reports the exact non-0xFF byte count.
  2. Arms a non-invasive gdb entry-count trace (``tools/
     g5_minimap_hittest_entry_trace.py``) on ``FUN_004516A0`` and its two
     return sites, so real xdotool clicks on the widget region can show
     whether the hit-test function is *reached at all* by input in this
     environment (the operator's literal ask), independent of whether the
     LUT was baked.
  3. If the LUT contains any non-``0xFF`` pixel, converts its (row, col)
     back to an absolute screen coordinate and clicks it, checking whether
     any fixture unit's ``pending_xy``/``pending_command`` changes --  a
     real, closeable minimap-click PASS if so. If the LUT is uniformly
     ``0xFF``, clicking cannot ever succeed via this path in this build/
     session and the probe records that as the (now much more specific)
     root cause instead of retrying blindly.

Read-only: the protected original is only read (SHA before/after run). No
game files or EXE bytes are modified.
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

from tools import runtime_env
from tools.g5_candidate_drag_probe import ProbeError, sha256, write_json, capture
from tools.g5_candidate_drag_probe import (
    DRAG_END,
    DRAG_START,
    SEED_COUNT,
    SEED_TYPE,
    STOCK_SELECTION_BASE,
    STOCK_SELECTION_CAPACITY,
    VISIBLE_WORKER_SLOT,
    SupplyProbe,
    dense_fixture_requests,
    selection_snapshot,
    unit_snapshot,
)
from tools.g5_attack_move_broadcast_probe import read_unit_full
from tools.g5_command_coverage_probe import MINIMAP_CENTER
from patches.selection import g5_selection_cap50_v10 as g5_v10
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from patches.population.runtime_driver import write as write_memory

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
GDB_SCRIPT = REPO / "tools" / "g5_minimap_hittest_entry_trace.py"
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap762-minimap-hittest"

# lap763 follow-up (2026-09-29 12:57 direction): the router's own gate call
# (`call 0x41c450` at 0x41e43d, immediately before it would call the widget
# hit-test) was found empirically (this lap) to return 0 on every single
# observed invocation (9430/9430 at its own return-check site 0x41e442), and
# its inputs trace to a *lobby "game type" selection* (word @ 0x975914,
# itself copied at new-game-init time from the lobby UI's own accessor
# result stored at 0x632d42) rather than to rendering/ddraw/focus state --
# only game_type==3 makes the new-game-init path set this flag to 1. This
# probe can optionally force the flag directly (diagnostic-only write into
# the private spawned copy, same scope as the existing G5 stale-tail
# fixture writes) to test the operator's explicit fallback instruction: "그
# 플래그를 브리지로 켜서 원본 미니맵 우클릭 이동을 성립시킨 뒤 원본20/v10 50
# paired" -- i.e. if forcing it open makes the hit-test reachable, the
# root cause is confirmed to be this game-type gate, not a dead renderer.
GATE_FLAG_VA = 0x0097597C

# G5 lap768 operator direction: exercise the minimap target through the
# command-panel mode buttons, not only the plain right-click path.  These
# coordinates are the already-established 800x600 render coordinates from
# g5_command_coverage_probe.py / g5_attack_move_broadcast_probe.py.
MINIMAP_MODE_BUTTONS = {
    "move": (703, 503),
    "attack": (663, 536),
    "patrol": (703, 536),
}
MINIMAP_STOP_BUTTON = (667, 503)

WIDGET_VA = 0x00639350
LUT_A_OFFSET = 0x13EEA
LUT_A_ROW_STRIDE_PIXELS = 180  # 0xB4
LUT_A_ROWS = 90  # 0x5A, dy in (0, 90]; row index used below is dy-1
LUT_A_BYTES = LUT_A_ROW_STRIDE_PIXELS * LUT_A_ROWS * 2  # 2 bytes/pixel = 0x7E90

# Diamond-vertex screen points lap710 already click-tested behaviourally
# (H1, falsified: zero effect) -- reused here so this lap's breakpoint/LUT
# evidence directly explains that prior negative result instead of treating
# it as a fresh, disconnected observation.
LAP710_DIAMOND_POINTS = [(88, 511), (176, 550), (88, 598), (0, 550), (90, 554)]


def static_finding() -> dict[str, Any]:
    return {
        "widget_va": hex(WIDGET_VA),
        "hittest_fn": "0x004516A0",
        "hittest_bounds_screen": {"x": [0, 180], "y_exclusive_lower": 509, "y_inclusive_upper": 599},
        "lut_a_offset": hex(LUT_A_OFFSET),
        "lut_a_index_formula": "dy = mouse_y - widget.y (1..89); index2 = dy*180 - widget.x + mouse_x; "
                                "byte0 = table[index2*2] (tile dx), byte1 = table[index2*2+1] (tile dy); "
                                "sentinel 0xFF in either byte => outside the diamond render, hit-test fails",
        "ctor_fills_lut_with_0xFF": (
            "FUN_00451130 (widget ctor, lap759-confirmed single call at new-game start) does "
            "`or eax,0xffffffff; lea edi,[esi+0x13eea]; rep stos` unconditionally before anything "
            "else, then loops over `[this+0x2baa0]` map tiles baking real (non-0xFF) deltas into "
            "the diamond-shaped subset of the same table -- so success depends on that loop having "
            "run with a non-zero tile count, not on rendering/ddraw at all."
        ),
        "router_fallback": (
            "The click router at ~0x41e440-0x41e60c tries FUN_004516A0 (this=widget) first; only on "
            "failure (return 0) does it fall back to the main-viewport hit-test 0x00417db0 already "
            "used by tools/g5_screen_world_calibration.py."
        ),
        "lap710_cross_reference": (
            "lap710's 'diamond' H1 click points (x in [0,176], y in [511,598]) are inside the "
            "[0,180]x(509,599] bounds computed here -- so lap710's observed zero-effect must come "
            "from the LUT lookup failing (sentinel), not from the geometric bounds test failing."
        ),
    }


def scan_lut(raw: bytes) -> dict[str, Any]:
    non_ff = [(i, b) for i, b in enumerate(raw) if b != 0xFF]
    result: dict[str, Any] = {
        "length": len(raw), "non_0xff_count": len(non_ff),
        "all_0xff": len(non_ff) == 0,
    }
    if non_ff:
        first_index_bytes, first_value = non_ff[0]
        pixel_index = first_index_bytes // 2
        row = pixel_index // LUT_A_ROW_STRIDE_PIXELS
        col = pixel_index % LUT_A_ROW_STRIDE_PIXELS
        result["first_non_0xff"] = {
            "byte_offset_in_table": first_index_bytes, "value": first_value,
            "pixel_index": pixel_index, "row_dy": row + 1, "col_dx": col,
            "screen_xy_guess": [col, row + 1 + 509],
        }
        result["sample_non_0xff"] = non_ff[:20]
    return result


def arm_trace(pid: int, control: Path, *, deadline_s: float) -> subprocess.Popen:
    control.mkdir(parents=True, exist_ok=True)
    for stale in ("armed.json", "stop.flag", "entry-summary.json", "entry-events.jsonl"):
        (control / stale).unlink(missing_ok=True)
    env = dict(os.environ, G5_MINIMAP_HITTEST_TRACE_CONTROL=str(control),
               G5_MINIMAP_HITTEST_TRACE_DEADLINE=str(deadline_s))
    log_path = control / "gdb.log"
    log = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(["gdb", "-p", str(pid), "--batch", "-x", str(GDB_SCRIPT)],
                             env=env, stdout=log, stderr=log)
    proc._probe_log = log  # type: ignore[attr-defined]
    return proc


def stop_trace(proc: subprocess.Popen, control: Path) -> dict[str, Any]:
    (control / "stop.flag").write_text("1", encoding="utf-8")
    proc.send_signal(signal.SIGINT)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
    log = getattr(proc, "_probe_log", None)
    if log is not None:
        log.close()
    summary_path = control / "entry-summary.json"
    if summary_path.exists():
        return json.loads(summary_path.read_text(encoding="utf-8"))
    return {"error": "no entry-summary.json written"}


def minimap_effect_summary(
    before: list[dict[str, Any]],
    immediate: list[dict[str, Any]],
    delayed: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize whether one minimap click reached every selected unit.

    ``pending_xy`` is the primary product signal: it is the queued world
    destination written by the original order path.  Command fields are
    recorded as supporting evidence but do not replace the destination check.
    """
    immediate_by_slot = {int(row["slot"]): row for row in immediate}
    delayed_by_slot = {int(row["slot"]): row for row in delayed}
    rows: list[dict[str, Any]] = []
    for row in before:
        slot = int(row["slot"])
        now = immediate_by_slot.get(slot, {})
        later = delayed_by_slot.get(slot, {})
        before_xy = row.get("pending_xy")
        observed_xy = now.get("pending_xy")
        if observed_xy == before_xy:
            observed_xy = later.get("pending_xy")
        changed = observed_xy != before_xy
        command_changed = (
            now.get("command") != row.get("command")
            or later.get("command") != row.get("command")
            or now.get("pending_command") != row.get("pending_command")
            or later.get("pending_command") != row.get("pending_command")
        )
        rows.append({
            "slot": slot,
            "command_before": row.get("command"),
            "pending_command_before": row.get("pending_command"),
            "pending_xy_before": before_xy,
            "pending_xy_immediate": now.get("pending_xy"),
            "pending_xy_delayed": later.get("pending_xy"),
            "pending_xy_changed": changed,
            "command_changed": command_changed,
            "command_immediate": now.get("command"),
            "command_delayed": later.get("command"),
            "pending_command_immediate": now.get("pending_command"),
            "pending_command_delayed": later.get("pending_command"),
        })
    changed_count = sum(bool(row["pending_xy_changed"]) for row in rows)
    command_changed_count = sum(bool(row["command_changed"]) for row in rows)
    return {
        "selected_count": len(rows),
        "pending_xy_changed_count": changed_count,
        "command_changed_count": command_changed_count,
        "all_selected_command_changed": bool(rows) and command_changed_count == len(rows),
        "all_selected_pending_xy_changed": bool(rows) and changed_count == len(rows),
        "rows": rows,
    }


def minimap_mode_effect_summary(
    mode: str,
    before: list[dict[str, Any]],
    immediate: list[dict[str, Any]],
    delayed: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize one command-mode button followed by a minimap left-click.

    The minimap destination is the primary delivery signal.  Command fields
    are retained as mode evidence because the same destination can be issued
    as move, attack-move, or patrol depending on the selected mode.
    """
    immediate_by_slot = {int(row["slot"]): row for row in immediate}
    delayed_by_slot = {int(row["slot"]): row for row in delayed}
    rows: list[dict[str, Any]] = []
    for row in before:
        slot = int(row["slot"])
        now = immediate_by_slot.get(slot, {})
        later = delayed_by_slot.get(slot, {})
        before_xy = row.get("pending_xy")
        observed_xy = now.get("pending_xy")
        if observed_xy == before_xy:
            observed_xy = later.get("pending_xy")
        command_values = {now.get("command"), later.get("command")}
        pending_values = {now.get("pending_command"), later.get("pending_command")}
        command_values.discard(None)
        pending_values.discard(None)
        rows.append({
            "slot": slot,
            "pending_xy_before": before_xy,
            "pending_xy_immediate": now.get("pending_xy"),
            "pending_xy_delayed": later.get("pending_xy"),
            "pending_xy_changed": observed_xy != before_xy,
            "command_before": row.get("command"),
            "command_immediate": now.get("command"),
            "command_delayed": later.get("command"),
            "pending_command_before": row.get("pending_command"),
            "pending_command_immediate": now.get("pending_command"),
            "pending_command_delayed": later.get("pending_command"),
            "command_values_observed": sorted(command_values),
            "pending_command_low16_observed": sorted(
                int(value) & 0xFFFF for value in pending_values
            ),
        })
    changed = sum(bool(row["pending_xy_changed"]) for row in rows)
    command_changed = sum(
        row["command_before"] not in row["command_values_observed"] for row in rows
    )
    pending_changed = sum(
        (int(row["pending_command_before"]) & 0xFFFF)
        not in row["pending_command_low16_observed"]
        for row in rows
    )
    return {
        "mode": mode,
        "selected_count": len(rows),
        "pending_xy_changed_count": changed,
        "command_changed_count": command_changed,
        "pending_command_changed_count": pending_changed,
        "all_selected_pending_xy_changed": bool(rows) and changed == len(rows),
        "all_selected_command_changed": bool(rows) and command_changed == len(rows),
        "rows": rows,
    }


def run_probe(source: Path, runtime_root: Path, artifact_root: Path,
              force_gate_flag: bool = False, variant: str = "original") -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
    candidate_sha = None
    candidate_bytes = None
    if variant == "candidate":
        candidate_bytes, candidate_report = g5_v10.build_candidate(source_exe.read_bytes())
        candidate_sha = candidate_report["candidate_sha256"]
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
        if sha256(private_exe) != candidate_sha:
            raise ProbeError("private candidate SHA verification failed")

    selection_base = g5_v10.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    selection_capacity = g5_v10.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-minimap-click-hittest-probe.v2", "variant": variant, "status": "UNKNOWN",
        "force_gate_flag": force_gate_flag,
        "static_finding": static_finding(),
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "candidate_sha256": candidate_sha, "private_exe_sha256": sha256(private_exe),
                       "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
    game_proc: Any = None
    trace_proc: Any = None
    control_root = artifact_root / "gdb_control"
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
                return int(read_state(pid).get("ps", -1)) in (3, 5, 7, 9)
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
        result["reached_ps9"] = True
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        crop = (int(info["x"]), int(info["y"]))

        def xdo(*args: str) -> None:
            subprocess.run(["xdotool", *args], env=env, stdout=log, stderr=log, timeout=10, check=True)

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None,
                  button: int = 1) -> None:
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
        result["reached_ps3"] = True
        snap("00-in-game")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        supply = SupplyProbe(prefix)
        fixture_requests = dense_fixture_requests(worker)
        receipts = []
        for request in fixture_requests:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE,
                                  x=request["x"], y=request["y"], count=request["count"])
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"dense fixture batch failed: {receipt}")
        if sum(int(receipt.get("fixture_added", 0)) for receipt in receipts) != SEED_COUNT:
            raise ProbeError(f"dense fixture total failed: {receipts}")
        time.sleep(1)
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        selected = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["fixture"] = {"owner": 0, "type": SEED_TYPE, "requested_count": SEED_COUNT,
                              "receipts": receipts, "worker": worker}
        result["selection_after_fixture_drag"] = selected
        expected = selection_capacity
        if selected["count"] != expected or selected["unique_slots"] != expected:
            raise ProbeError(f"fixture drag did not select {expected}: {selected}")

        gate_flag_before = int.from_bytes(read_memory(pid, GATE_FLAG_VA, 4), "little", signed=False)
        result["gate_flag_before"] = hex(gate_flag_before)
        if force_gate_flag:
            write_memory(pid, GATE_FLAG_VA, (1).to_bytes(4, "little"))
            gate_flag_after = int.from_bytes(read_memory(pid, GATE_FLAG_VA, 4), "little", signed=False)
            result["gate_flag_after_write"] = hex(gate_flag_after)
            if gate_flag_after != 1:
                raise ProbeError(f"gate flag write did not take: {gate_flag_after:#x}")

        widget_x = int.from_bytes(read_memory(pid, WIDGET_VA, 4), "little", signed=True)
        widget_y = int.from_bytes(read_memory(pid, WIDGET_VA + 4, 4), "little", signed=True)
        result["widget_xy_runtime"] = {"x": widget_x, "y": widget_y}
        lut_raw = read_memory(pid, WIDGET_VA + LUT_A_OFFSET, LUT_A_BYTES)
        result["lut_scan"] = scan_lut(bytes(lut_raw))

        trace_proc = arm_trace(pid, control_root, deadline_s=60)
        armed_deadline = time.monotonic() + 20
        while time.monotonic() < armed_deadline and not (control_root / "armed.json").exists():
            if trace_proc.poll() is not None:
                raise ProbeError(f"gdb trace exited before arming (rc={trace_proc.returncode})")
            time.sleep(0.1)
        result["trace_armed"] = (control_root / "armed.json").exists()
        if not result["trace_armed"]:
            raise ProbeError("gdb trace did not arm before timeout")

        clicked_baked_pixel = False
        first_non_ff = result["lut_scan"].get("first_non_0xff")
        if first_non_ff is not None:
            center_dx = MINIMAP_CENTER[0] - widget_x
            center_dy = MINIMAP_CENTER[1] - widget_y
            center_index = (center_dy * LUT_A_ROW_STRIDE_PIXELS + center_dx) * 2
            center_is_baked = (
                0 <= center_index <= len(lut_raw) - 2
                and lut_raw[center_index] != 0xFF
                and lut_raw[center_index + 1] != 0xFF
            )
            if center_is_baked:
                gx, gy = MINIMAP_CENTER
                target_source = "known_center"
            else:
                gx = widget_x + int(first_non_ff["col_dx"])
                gy = widget_y + int(first_non_ff["row_dy"])
                target_source = "first_non_0xff"
            result["minimap_click_target"] = {
                "screen_xy": [gx, gy], "source": target_source,
                "center_is_baked": center_is_baked,
            }
            if 0 <= gx < 1600 and 0 <= gy < 1200:
                # First exercise the three user-requested command modes.  A
                # stop is issued between modes, but the original selection is
                # intentionally preserved; this isolates the mode->minimap
                # click path without adding a second drag-selection variable.
                mode_results: dict[str, Any] = {}
                for mode, button_xy in MINIMAP_MODE_BUTTONS.items():
                    mode_selection = selection_snapshot(
                        pid, base=selection_base, capacity=selection_capacity,
                    )
                    if (mode_selection["count"] != expected
                            or mode_selection["unique_slots"] != expected):
                        raise ProbeError(
                            f"selection changed before minimap {mode} action: {mode_selection}"
                        )
                    mode_slots = [slot for slot in mode_selection["slots"] if 0 < slot < 1200]
                    before_mode = [read_unit_full(pid, slot) for slot in mode_slots]
                    click(*button_xy)
                    time.sleep(0.15)
                    click(gx, gy)
                    time.sleep(0.15)
                    immediate_mode = [read_unit_full(pid, slot) for slot in mode_slots]
                    time.sleep(0.45)
                    delayed_mode = [read_unit_full(pid, slot) for slot in mode_slots]
                    mode_results[mode] = {
                        "button_xy": list(button_xy),
                        "target_xy": [gx, gy],
                        "selection": mode_selection,
                        "effect": minimap_mode_effect_summary(
                            mode, before_mode, immediate_mode, delayed_mode,
                        ),
                    }
                    click(*MINIMAP_STOP_BUTTON)
                    time.sleep(0.7)
                    if not alive():
                        raise ProbeError(f"game not alive after minimap {mode} action")
                    snap(f"mode-{mode}")
                result["minimap_mode_actions"] = mode_results

                # Retain the original plain minimap right-click measurement as
                # a direct baseline for this same fixture and target.
                before_units = [read_unit_full(pid, slot) for slot in selected["slots"] if 0 < slot < 1200]
                click(gx, gy, button=3)
                time.sleep(0.15)
                immediate_units = [read_unit_full(pid, slot) for slot in selected["slots"] if 0 < slot < 1200]
                time.sleep(0.45)
                delayed_units = [read_unit_full(pid, slot) for slot in selected["slots"] if 0 < slot < 1200]
                result["baked_pixel_click"] = {"screen_xy": [gx, gy]}
                clicked_baked_pixel = True
                result["minimap_command_effect"] = minimap_effect_summary(
                    before_units, immediate_units, delayed_units,
                )
        result["clicked_baked_pixel"] = clicked_baked_pixel

        snap("01-after-hittest-clicks")

        time.sleep(1.5)
        trace_summary = stop_trace(trace_proc, control_root)
        trace_proc = None
        result["trace_summary"] = trace_summary
        result["events_log"] = str(control_root / "entry-events.jsonl")
        effect = result.get("minimap_command_effect", {})
        effect_ok = effect.get("all_selected_pending_xy_changed", False)
        mode_results = result.get("minimap_mode_actions", {})
        mode_ok = bool(mode_results) and all(
            row.get("effect", {}).get("all_selected_pending_xy_changed", False)
            for row in mode_results.values()
        )
        result["status"] = (
            f"PASS_MINIMAP_MODES_{variant.upper()}"
            if effect_ok and mode_ok and not trace_summary.get("fatal") else
            f"PASS_MINIMAP_COMMAND_{variant.upper()}"
            if effect_ok and not trace_summary.get("fatal") else
            "FAIL_MINIMAP_COMMAND" if not trace_summary.get("fatal") else "TRACE_FATAL"
        )
        result["alive_at_end"] = alive()
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if trace_proc is not None and trace_proc.poll() is None:
            try:
                stop_trace(trace_proc, control_root)
            except Exception:
                trace_proc.kill()
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
            children_and_xvfb = children + ([xvfb] if xvfb is not None else [])
            for child in children_and_xvfb:
                child.wait(timeout=5)
        except Exception:
            pass
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix)}
        result["cleanup"]["ok"] = not result["cleanup"]["prefix_processes_after"]
        result["source_after_sha256"] = sha256(source_exe)
        result["source_unchanged"] = result["source_after_sha256"] == ORIGINAL_SHA
        log.close()

    result_path = artifact_root / "probe-result.json"
    write_json(result_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--variant", choices=("original", "candidate"), default="original")
    parser.add_argument("--force-gate-flag", action="store_true",
                         help="diagnostic-only: write 1 to the router gate flag (0x97597c) "
                              "right after reaching ps==3, to test whether that unblocks "
                              "FUN_004516A0 (lap763 finding)")
    args = parser.parse_args()
    result = run_probe(args.source, args.runtime_root, args.artifact_root,
                       args.force_gate_flag, args.variant)
    print(json.dumps({k: v for k, v in result.items() if k not in ("captures",)}, ensure_ascii=False, indent=2))
    return 0 if result["status"].startswith("PASS_MINIMAP_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
