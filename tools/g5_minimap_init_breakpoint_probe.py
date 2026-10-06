#!/usr/bin/env python3
"""G5 user item (2), minimap sub-question -- does the minimap widget's own
position-init constructor ever run in this environment?

2026-09-29 10:35 operator direction asked for the root cause of the minimap
rendering as black/unresponsive in this isolated environment. lap758 found
that a *sibling* reverse-engineering project (``Syw2plus_re``, read-only
reference) independently failed to find the minimap render entry point
either, and proposed reading two cafe-community-documented addresses
(``0x451C12``/``0x451C19``, analysis/memory_maps/cafe_community_offsets.md
in that read-only reference) live during a run to see whether "the
subsystem initializes".

This probe first falsifies that premise with a quick static disassembly
(objdump -d on the protected original): ``0x451C10`` is a 14-byte leaf
function --

    451c10: mov DWORD PTR [ecx], 0x0        ; this+0x0 = 0   (X)
    451c16: mov DWORD PTR [ecx+0x4], 0x1fd  ; this+0x4 = 509 (Y)
    451c1d: ret

-- and ``0x451C12``/``0x451C19`` are bytes *inside the two immediate
operands*, i.e. constants baked into .text. Reading them live would show the
same 0/509 bytes whether or not this code ever executes; they carry no
liveness signal. A full ``.text`` xref scan found exactly one direct caller,
``0x451138``, inside a large (~0x1c000-byte) struct-zeroing/initializer
function starting at ``0x451130`` (the "this" pointer, ``ecx``==``esi`` at
the call site, is a large widget-sized struct that gets almost entirely
zeroed right after these first two fields are set to (0, 509) -- plausibly a
default on-screen minimap frame position for an 800x600-era layout).

What *is* a valid liveness signal is whether ``0x451130``/``0x451C10`` are
ever *called* at all: a gdb entry-count trace (``tools/
g5_minimap_init_entry_trace.py``) armed immediately after the Wine process
launches (before the main menu is even reachable) and left running through
menu -> solo lobby -> in-game, plus a few minimap-area interactions
(m/M/Tab keys, right-click on the minimap diamond), covers the whole
observable lifecycle in one isolated run.

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
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from tools.g5_command_coverage_probe import MINIMAP_CENTER
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
GDB_SCRIPT = REPO / "tools" / "g5_minimap_init_entry_trace.py"
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap759-minimap-init-trace"


def arm_full_session_trace(pid: int, control: Path, *, deadline_s: float) -> subprocess.Popen:
    control.mkdir(parents=True, exist_ok=True)
    for stale in ("armed.json", "stop.flag", "entry-summary.json", "entry-events.jsonl"):
        (control / stale).unlink(missing_ok=True)
    env = dict(os.environ, G5_MINIMAP_INIT_TRACE_CONTROL=str(control),
               G5_MINIMAP_INIT_TRACE_DEADLINE=str(deadline_s))
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


def static_finding() -> dict[str, Any]:
    """Re-derive the disassembly finding this probe's docstring describes, so
    the result JSON is self-contained without re-running objdump by hand."""
    return {
        "leaf_xy_writer": "0x00451C10",
        "leaf_disasm": [
            "451c10: c7 01 00 00 00 00     mov DWORD PTR [ecx],0x0",
            "451c16: c7 41 04 fd 01 00 00  mov DWORD PTR [ecx+0x4],0x1fd",
            "451c1d: c3                    ret",
        ],
        "cafe_reference_addresses": {"0x451C12": "minimap X (inside the [ecx] imm32)",
                                      "0x451C19": "minimap Y (inside the [ecx+0x4] imm32)"},
        "premise_falsified": (
            "0x451C12/0x451C19 are bytes of immediate operands baked into "
            ".text -- always 0x00000000 and 0x000001fd whether or not this "
            "code ever executes. Reading them live carries no information "
            "about whether the minimap subsystem is alive; only whether the "
            "*function* is ever called does."
        ),
        "caller": "0x00451138 (sole direct call site, .text xref scan 0x400000-0x800000)",
        "caller_context": (
            "0x00451130 is a large (~0x1c000-byte) struct-zeroing "
            "initializer; ecx/esi ('this') at the 0x451138 call site is the "
            "same object the rest of 0x451130 goes on to zero across a wide "
            "offset range (+0xa .. +0x1bd7a seen), consistent with a "
            "widget-sized struct whose first two dwords are its default "
            "on-screen X/Y (0, 509)."
        ),
    }


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
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
        "schema": "syw2plus.g5-minimap-init-breakpoint-probe.v1", "variant": "original", "status": "UNKNOWN",
        "static_finding": static_finding(),
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": sha256(private_exe), "game_root": str(game), "run_dir": str(game.parent)},
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

        # Arm the full-session trace as early as possible -- before the main
        # menu is even reachable -- so a very-early/startup call to the
        # candidate constructor is not missed. The gdb script itself retries
        # breakpoint creation for up to 10s to absorb the PE-module-not-yet-
        # mapped race right after Popen.
        time.sleep(0.5)
        trace_proc = arm_full_session_trace(pid, control_root, deadline_s=180)
        armed_deadline = time.monotonic() + 20
        while time.monotonic() < armed_deadline and not (control_root / "armed.json").exists():
            if trace_proc.poll() is not None:
                raise ProbeError(f"gdb trace exited before arming (rc={trace_proc.returncode})")
            time.sleep(0.1)
        result["trace_armed"] = (control_root / "armed.json").exists()
        if not result["trace_armed"]:
            raise ProbeError("gdb trace did not arm before timeout")

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

        def click(x: int, y: int, *, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
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

        # Minimap-area interactions -- same coordinates/keys prior probes
        # (lap677/lap710) already exercised with no visible effect. This run
        # doesn't need a new positive result from these; it only needs to
        # give the traced functions every reasonable chance to fire if map
        # load / minimap toggle is what triggers them.
        click(*MINIMAP_CLICK)
        time.sleep(0.5)
        click(*MINIMAP_CENTER, button=3)
        time.sleep(0.5)
        for key in ("m", "shift+m", "Tab"):
            xdo("key", key)
            time.sleep(0.4)
        snap("01-after-minimap-interactions")

        time.sleep(2.0)
        trace_summary = stop_trace(trace_proc, control_root)
        trace_proc = None
        result["trace_summary"] = trace_summary
        result["events_log"] = str(control_root / "entry-events.jsonl")
        result["status"] = "COMPLETE" if "fatal" not in trace_summary or trace_summary.get("fatal") is None else "TRACE_FATAL"
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
    args = parser.parse_args()
    result = run_probe(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps({k: v for k, v in result.items() if k not in ("captures",)}, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
