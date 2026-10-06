#!/usr/bin/env python3
"""Paired original20 / v4-candidate50 STOP / HOLD / PATROL functional check
(2026-09-27 15:49 operator direction, step (3), narrowed to the three
commands ``docs/history/laps/20260927_direct_g5_v3_command_coverage.md``
found capped at 20/50 on the v3 candidate).

``patches/selection/g5_selection_cap50_v4.py`` inverts v3's chunk-wrapper
gate: instead of an explicit "known real order type" allow-list
``{1, 3, 4, 7, 8, 9}``, it chunks any order-type header that is *not* one of
lap676's statically-verified known non-order/UI-notification opcodes. This
probe tests the functional prediction directly (how many of the selected
units actually receive the STOP/HOLD/PATROL pending word), the same way
``g5_command_coverage_probe.py`` measured the v3 FAIL, since lap717 found
gdb breakpoint tracing at the wrapper's own entry point does not observe
real order dispatch for STOP/HOLD/PATROL (or even MOVE) reliably enough to
use as a precondition here -- reusing ``g5_command_coverage_probe.py``'s
already-proven bulk-sample ``observe()`` helper instead.

Read-only for the original variant (protected EXE only read, SHA before/
after); the candidate variant rebuilds v4 from the protected original and
SHA-verifies it before installing into the isolated per-run copy.
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

from patches.selection import g5_selection_cap50_v4 as g5
from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, SupplyProbe, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    SEED_TYPE, VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE, UNIT_PENDING_COMMAND_OFFSET,
    selection_snapshot, unit_snapshot, dense_fixture_requests, sha256, write_json, capture,
)
from tools.g5_command_coverage_probe import BUTTONS, RESELECT_START, RESELECT_END, observe
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
DESTINATION_CANDIDATES = [
    (300, 420), (400, 300), (350, 250), (450, 350),
    (300, 350), (500, 300), (250, 300), (400, 420),
]


def run_probe(source: Path, runtime_root: Path, artifact_root: Path, *, variant: str) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
    candidate_bytes: bytes | None = None
    candidate_sha: str | None = None
    if variant == "candidate":
        candidate_bytes, build_report = g5.build_candidate(source_exe.read_bytes())
        candidate_sha = build_report["candidate_sha256"]

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
    private_sha = sha256(private_exe)
    if variant == "candidate" and private_sha != candidate_sha:
        raise ProbeError(f"candidate SHA mismatch: {private_sha}")
    sel_base = g5.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    sel_cap = g5.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-stop-hold-patrol-v4-probe.v1", "variant": variant, "status": "UNKNOWN",
        "provenance": {"source_sha256": sha256(source_exe), "private_exe_sha256": private_sha,
                       "candidate_sha256": candidate_sha},
        "steps": {}, "captures": [], "inputs": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
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
                return int(read_state(pid).get("ps", -1)) == 3
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
            s = selection_snapshot(pid, base=sel_base, capacity=sel_cap)
            if variant == "candidate":
                legacy = int.from_bytes(read_memory(pid, STOCK_SELECTION_BASE, 4), "little", signed=True)
                s["legacy_count"] = legacy
            return s

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
        supply = SupplyProbe(prefix)
        click(*MINIMAP_CLICK)
        time.sleep(1)
        snap("00-after-minimap")

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(0.8)
        worker_sel = selection_snapshot(pid, base=sel_base, capacity=sel_cap)
        result["worker_only_selection"] = worker_sel
        snap("00b-after-worker-select")
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

        for req in dense_fixture_requests(worker):
            r = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=req["x"], y=req["y"], count=req["count"])
            if not r.get("ok") or r.get("fixture_added") != req["count"]:
                raise ProbeError(f"fixture failed: {r}")
        time.sleep(1)
        snap("01-after-fixture")

        def reselect(label: str) -> list[int]:
            click(*RESELECT_START, drag_to=RESELECT_END)
            time.sleep(0.8)
            s = sel()
            result["steps"].setdefault(label, {})["selection"] = s
            return list(s["slots"])

        def step(label: str, act, window: float, *, pre=None) -> list[int]:
            slots = reselect(label)
            if pre is not None:
                pre()
            obs = observe(pid, slots, act, window)
            st = result["steps"][label]
            st["observe"] = obs
            st["alive_after"] = alive()
            snap(f"{len(result['steps']):02d}-{label}")
            if not st["alive_after"]:
                raise ProbeError(f"game not alive after {label}")
            return slots

        slots = step("stop_button", lambda: click(*BUTTONS["stop"]), 3.0,
                     pre=lambda: (click(*destination_screen, button=3), time.sleep(0.6)))
        slots = step("hold_button", lambda: click(*BUTTONS["hold"]), 3.0)
        slots = step("patrol_button", lambda: (click(*BUTTONS["patrol"]), time.sleep(0.15),
                                               click(*destination_screen)), 6.0)
        click(*BUTTONS["stop"])
        time.sleep(0.5)
        result["final_selected_count"] = len(slots)
        result["status"] = "COMPLETE"
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
    ap.add_argument("--variant", choices=("original", "candidate"), required=True)
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--runtime-root", type=Path, required=True)
    ap.add_argument("--artifact-root", type=Path, required=True)
    args = ap.parse_args(argv)
    res = run_probe(args.source, args.runtime_root, args.artifact_root, variant=args.variant)
    print(json.dumps({k: res.get(k) for k in ("status", "error", "variant", "source_unchanged")}, ensure_ascii=False))
    return 0 if res.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
