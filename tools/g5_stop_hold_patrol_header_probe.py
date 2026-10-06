#!/usr/bin/env python3
"""Measure the v3 chunk-wrapper hook site's order-type header word for
STOP / HOLD / PATROL (2026-09-27 15:49 operator direction, step (1)).

``docs/history/laps/20260927_direct_g5_v3_command_coverage.md`` found that
the candidate v3 build (``patches/selection/g5_selection_cap50_v3.py``)
receives STOP/HOLD/PATROL clicks on only exactly 20 of 50 selected units,
and *inferred* (from the pending-word convention already established for
MOVE=3/ATTACK=4) that their ``word [esp+8]`` order-type header values are
STOP=2, HOLD=0x27, PATROL=0x23 -- none of which are in the wrapper's
real-order-type whitelist ``{1, 3, 4, 7, 8, 9}``, which would explain the
fall-through to the unchunked 20-unit original body. This probe measures
the header directly instead of inferring it, reusing lap681's non-invasive
gdb trace (``g5_v3_order_type_header_trace.py``: breaks once per call at
the hook site ``0x004AE550`` and reads ``word ptr [esp+8]`` off the stack).

The hook site is the function's own unmodified entry point -- this run uses
the *protected original* EXE unpatched, so the measurement does not depend
on the v3 candidate build at all (the caller-side stack layout that pushes
the type argument is identical in both).

Flow: boot to a solo lobby, drag-select the lone pre-existing worker
(slot 1198, before any fixture exists -- same "worker only" selection lap682/
lap707's screen calibration uses). lap682 found a single hardcoded
destination pixel is not map-independent (the solo lobby is unseeded), so
this probe validates a handful of candidate screen points with the worker
alone (right-click, poll ``+0x384`` for ``0x1000003`` = plain MOVE) and uses
the first one that works, both as a sanity check (``type_header`` should
read ``3``) and to give STOP/HOLD something to act on. It then successively
traces STOP button, HOLD button, and PATROL button + ground-click.

Read-only: the protected original EXE is never modified, only read (SHA
before/after).
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

from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError,
    SupplyProbe,
    DRAG_START,
    DRAG_END,
    STOCK_SELECTION_BASE,
    STOCK_SELECTION_CAPACITY,
    SEED_TYPE,
    VISIBLE_WORKER_SLOT,
    UNIT_BASE,
    UNIT_STRIDE,
    UNIT_PENDING_COMMAND_OFFSET,
    selection_snapshot,
    unit_snapshot,
    dense_fixture_requests,
    sha256,
    write_json,
    capture,
)
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_v3_order_type_header_probe import run_trace_phase
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap717-stop-hold-patrol-header"

BUTTONS = {"stop": (667, 503), "hold": (740, 538), "patrol": (703, 538)}
RESELECT_START = (12, 40)
RESELECT_END = (788, 470)
# lap682 found a single hardcoded destination pixel is not map-independent
# (the solo lobby is unseeded); candidates are validated in-run instead of
# trusting one fixed point.
DESTINATION_CANDIDATES = [
    (300, 420), (400, 300), (350, 250), (450, 350),
    (300, 350), (500, 300), (250, 300), (400, 420),
]


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

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

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-stop-hold-patrol-header-probe.v1",
        "status": "UNKNOWN",
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
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

        def xdo(*args: str) -> None:
            subprocess.run(["xdotool", *args], env=env, stdout=log, stderr=log, timeout=10, check=True)

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "drag_to": list(drag_to) if drag_to else None, "button": button})

        xdo("windowfocus", outer)
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

        click(*MINIMAP_CLICK)
        time.sleep(1)
        result["captures"] = [capture(display, artifact_root / "00a-pre-drag.png", log)]
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(0.8)
        sel = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["worker_only_selection"] = sel
        result["captures"].append(capture(display, artifact_root / "00b-after-worker-select.png", log))
        if sel["count"] != 1 or VISIBLE_WORKER_SLOT not in sel["slots"]:
            raise ProbeError(f"worker-only selection did not settle: {sel}")

        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

        def worker_order_at(screen: tuple[int, int]) -> list[str]:
            xdo("key", "s")
            time.sleep(0.6)
            got: set[str] = set()
            click(*screen, button=3)
            t0 = time.monotonic()
            while time.monotonic() - t0 < 0.4:
                got.add(hex(int.from_bytes(
                    read_memory(pid, wbase + UNIT_PENDING_COMMAND_OFFSET, 4), "little")))
                time.sleep(0.005)
            return sorted(got)

        validation: list[dict[str, Any]] = []
        destination_screen: tuple[int, int] | None = None
        for cand in DESTINATION_CANDIDATES:
            orders = worker_order_at(cand)
            ok = "0x1000003" in orders
            validation.append({"screen": list(cand), "worker_pending_seen": orders, "move_ok": ok})
            if ok:
                destination_screen = cand
                break
        result["destination_validation"] = validation
        if destination_screen is None:
            raise ProbeError(f"no candidate destination produced a plain MOVE order: {validation}")
        xdo("key", "s")
        time.sleep(0.5)
        result["destination_screen"] = list(destination_screen)

        # lap717 first pass (single worker only) found the hook site is
        # never hit for a confirmed single-unit MOVE order (pending
        # 0x1000003 achieved, zero header-hit events) -- spawn the same
        # dense 55-unit fixture prior G5 laps use and select the whole
        # group, since FUN_004AE550 appears to be specifically the
        # multi-unit "broadcast the current selection" path.
        supply = SupplyProbe(prefix)
        for req in dense_fixture_requests(worker):
            r = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=req["x"], y=req["y"], count=req["count"])
            if not r.get("ok") or r.get("fixture_added") != req["count"]:
                raise ProbeError(f"fixture failed: {r}")
        time.sleep(1)
        result["captures"].append(capture(display, artifact_root / "00c-after-fixture.png", log))

        click(*RESELECT_START, drag_to=RESELECT_END)
        time.sleep(0.8)
        group_sel = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["group_selection"] = group_sel
        result["captures"].append(capture(display, artifact_root / "00d-after-group-select.png", log))
        if group_sel["count"] < 2:
            raise ProbeError(f"group reselect did not gather multiple units: {group_sel}")

        control_root = artifact_root / "gdb_control"

        def do_move(marker_flag: Path) -> None:
            click(*destination_screen, button=3)
            marker_flag.write_text("1", encoding="utf-8")

        def do_stop(marker_flag: Path) -> None:
            click(*BUTTONS["stop"])
            marker_flag.write_text("1", encoding="utf-8")

        def do_hold(marker_flag: Path) -> None:
            click(*BUTTONS["hold"])
            marker_flag.write_text("1", encoding="utf-8")

        def do_patrol(marker_flag: Path) -> None:
            click(*BUTTONS["patrol"])
            time.sleep(0.15)
            click(*destination_screen)
            marker_flag.write_text("1", encoding="utf-8")

        phases: dict[str, Any] = {}

        # Sanity check first: confirm this trace mechanism reads a plain MOVE
        # click as type_header==3 on THIS (original, unpatched) EXE, matching
        # lap681's finding on the candidate build -- the hook site's stack
        # layout is caller-controlled and identical in both.
        phases["move_sanity"] = run_trace_phase(
            pid, control_root / "move", label="move", action=do_move, post_marker_wait=1.5,
        )
        result["captures"].append(capture(display, artifact_root / "01-after-move.png", log))

        phases["stop"] = run_trace_phase(
            pid, control_root / "stop", label="stop", action=do_stop, post_marker_wait=1.5,
        )
        result["captures"].append(capture(display, artifact_root / "02-after-stop.png", log))

        # give it another move order so hold has something to hold against
        click(*destination_screen, button=3)
        time.sleep(0.4)
        phases["hold"] = run_trace_phase(
            pid, control_root / "hold", label="hold", action=do_hold, post_marker_wait=1.5,
        )
        result["captures"].append(capture(display, artifact_root / "03-after-hold.png", log))

        phases["patrol"] = run_trace_phase(
            pid, control_root / "patrol", label="patrol", action=do_patrol, post_marker_wait=1.5,
        )
        result["captures"].append(capture(display, artifact_root / "04-after-patrol.png", log))

        result["phases"] = phases

        summary: dict[str, Any] = {}
        for name, phase in phases.items():
            events = phase.get("events", [])
            headers = sorted({e["type_header"] for e in events if e.get("type_header") is not None})
            summary[name] = {
                "hits_total": phase.get("hits"),
                "post_marker_hits": phase.get("post_marker_hits"),
                "headers_seen_after_marker": headers,
            }
        result["header_summary"] = summary
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
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps(result.get("header_summary", result), ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "TRACE_COMPLETE" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
