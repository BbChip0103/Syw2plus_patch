#!/usr/bin/env python3
"""Paired original20->~10 / v4-candidate50->21-49 selection-shrink STOP leak
check (R1, ``loop/ESCALATE_SOL`` lap719 section, 2026-09-27 17:25 operator
direction).

lap719's independent review confirmed v4's chunked order-dispatch path (any
order-type header not in lap676's known non-order set, whenever the live
selection exceeds 20) is unchanged from v3 except for which headers take it:
the wrapper always copies three fixed 20-unit windows of the *global*
selection-entries array (``entries[0:20]``, ``entries[20:40]``,
``entries[40:50]``) and dispatches the original order-builder body once per
non-empty window. Every raw measurement so far only ever exercised this with
the live selection sitting at its post-drag maximum (50 for the candidate, 20
for the original) -- nobody has selected 50, then *shrunk* the live selection
below 50 while still above 20, and checked whether the units that fell out of
the new selection (but still occupy the tail of the fixed-size copy windows)
receive the order anyway. That is the open risk (R1) this probe measures
directly: it is a structural question about the copy windows, not about any
one order type, so STOP (pending word ``0x1000002``) stands in for the whole
order-type family.

Protocol, both variants: solo lobby, the same worker-centered 55-unit dense
type-2 fixture as the other G5 probes (slot 1198's pre-existing worker makes
56 selectable units total), full-rectangle drag-select (candidate expected
50/56, original capped 20/56), then an in-run search over smaller
left-anchored sub-rectangles (same top/bottom edges, receding right edge)
until the *replacement* drag-select lands the live count inside the target
band (21-49 for the candidate to stay on the chunked path; a rough half,
5-19, for the original control). The units dropped by the shrink but not
newly re-added are the ``deselected`` set -- read directly from the game's
own selection-count semantics, not inferred. The STOP button is then clicked
once and every unit in the union of (still-selected, deselected) is sampled
for ``unit+0x384`` (pending order word) at 20ms resolution for 2.5s.

PASS requires every still-selected unit to show ``0x1000002`` at least once
*and* zero deselected units to ever show it. A hit on any deselected unit is
the R1 leak this probe exists to catch, in which case the next work should
build a v5 that clamps the chunked copies to the live selection count instead
of always copying all three fixed windows.

The full (pre-count) selection-entries buffer is also read before and after
the shrink drag purely as diagnostic evidence for whether the underlying
storage actually leaves stale handles past the new live count -- it does not
gate the PASS/FAIL verdict, which is behavioral (did the unit's own pending
word change), not structural.

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
from tools.g5_command_coverage_probe import BUTTONS
from tools.g5_attack_move_broadcast_probe import MINIMAP_CLICK
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
STOP_PENDING = 0x1000002

# Left-anchored sub-rectangles: same top/bottom edges as the full drag, right
# edge receding from the full extent down toward the left edge. Tried in this
# order (largest first) until the resulting live count lands in the variant's
# target band.
SHRINK_RIGHT_EDGES = [690, 650, 610, 570, 530, 490, 450, 410, 370, 330, 290, 250]


def read_pending(pid: int, slot: int) -> int:
    base = UNIT_BASE + slot * UNIT_STRIDE
    return int.from_bytes(read_memory(pid, base + UNIT_PENDING_COMMAND_OFFSET, 4), "little")


def read_full_buffer(pid: int, base: int, capacity: int) -> dict[str, Any]:
    raw = [
        int.from_bytes(read_memory(pid, base + 4 + i * 4, 4), "little", signed=False)
        for i in range(capacity)
    ]
    count = int.from_bytes(read_memory(pid, base, 4), "little", signed=True)
    return {"count_field": count, "raw_all": [hex(v) for v in raw], "slots_all": [v & 0xFFF for v in raw]}


def sample_ever(pid: int, slots: list[int], act, window: float = 2.5, interval: float = 0.02) -> dict[str, Any]:
    before = {s: read_pending(pid, s) for s in slots}
    act()
    start = time.monotonic()
    ever: dict[int, set[int]] = {s: set() for s in slots}
    last: dict[int, int] = {}
    n_samples = 0
    while time.monotonic() - start < window:
        for s in slots:
            v = read_pending(pid, s)
            ever[s].add(v)
            last[s] = v
        n_samples += 1
        time.sleep(interval)
    return {
        "n_samples": n_samples,
        "before": {s: hex(v) for s, v in before.items()},
        "ever": {s: sorted(hex(v) for v in vs) for s, vs in ever.items()},
        "ever_raw": {s: sorted(vs) for s, vs in ever.items()},
        "last": {s: hex(v) for s, v in last.items()},
    }


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
    target_band = (21, 49) if variant == "candidate" else (5, 19)

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-selection-shrink-leak-probe.v1", "variant": variant, "status": "UNKNOWN",
        "provenance": {"source_sha256": sha256(source_exe), "private_exe_sha256": private_sha,
                       "candidate_sha256": candidate_sha},
        "target_band": list(target_band), "shrink_attempts": [], "captures": [], "inputs": [],
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

        for req in dense_fixture_requests(worker):
            r = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=req["x"], y=req["y"], count=req["count"])
            if not r.get("ok") or r.get("fixture_added") != req["count"]:
                raise ProbeError(f"fixture failed: {r}")
        time.sleep(1)
        snap("01-after-fixture")

        # --- full drag: establish the maximal live selection (50 candidate / 20 original)
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(0.8)
        initial_sel = sel()
        result["initial_selection"] = initial_sel
        result["initial_full_buffer"] = read_full_buffer(pid, sel_base, sel_cap)
        snap("02-after-full-drag")
        if not alive():
            raise ProbeError("game not alive after full drag")

        # --- shrink: search receding-width sub-rectangles for the target band
        lo, hi = target_band
        best: dict[str, Any] | None = None
        for right_edge in SHRINK_RIGHT_EDGES:
            box_end = (right_edge, DRAG_END[1])
            click(*DRAG_START, drag_to=box_end)
            time.sleep(0.6)
            candidate_sel = sel()
            attempt = {"right_edge": right_edge, "count": candidate_sel["count"],
                       "slots": list(candidate_sel["slots"])}
            result["shrink_attempts"].append(attempt)
            n = candidate_sel["count"]
            in_band = lo <= n <= hi
            is_better = (
                best is None
                or (in_band and not (lo <= best["count"] <= hi))
                or (in_band and abs(n - (lo + hi) // 2) < abs(best["count"] - (lo + hi) // 2))
            )
            if is_better:
                best = {"right_edge": right_edge, "box_end": list(box_end), "count": n, "selection": candidate_sel}
            if in_band:
                break
        if best is None or best["count"] == 0 or best["count"] >= initial_sel["count"]:
            raise ProbeError(f"could not find a proper shrink subset: {result['shrink_attempts']}")
        result["shrink_choice"] = {k: v for k, v in best.items() if k != "selection"}
        result["shrink_in_band"] = lo <= best["count"] <= hi

        # re-apply the winning box as the final live selection for the STOP test
        click(*DRAG_START, drag_to=tuple(best["box_end"]))
        time.sleep(0.8)
        partial_sel = sel()
        result["partial_selection"] = partial_sel
        result["partial_full_buffer"] = read_full_buffer(pid, sel_base, sel_cap)
        snap("03-after-shrink-drag")
        if not alive():
            raise ProbeError("game not alive after shrink drag")

        partial_slots = sorted(set(partial_sel["slots"]))
        deselected_slots = sorted(set(initial_sel["slots"]) - set(partial_slots))
        result["partial_slots"] = partial_slots
        result["deselected_slots"] = deselected_slots
        if not deselected_slots:
            raise ProbeError("shrink drag did not actually drop any previously selected units")

        all_slots = sorted(set(partial_slots) | set(deselected_slots))
        obs = sample_ever(pid, all_slots, lambda: click(*BUTTONS["stop"]), window=2.5)
        result["stop_observation"] = obs
        snap("04-after-stop")
        result["alive_after_stop"] = alive()
        if not result["alive_after_stop"]:
            raise ProbeError("game not alive after stop click")

        leaked = [s for s in deselected_slots if STOP_PENDING in obs["ever_raw"][s]]
        missed = [s for s in partial_slots if STOP_PENDING not in obs["ever_raw"][s]]
        result["leaked_slots"] = leaked
        result["missed_slots"] = missed
        if leaked:
            result["status"] = "FAIL_LEAK"
        elif missed:
            result["status"] = "FAIL_INCOMPLETE_STOP"
        else:
            result["status"] = "PASS_NO_LEAK"
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
    print(json.dumps({k: res.get(k) for k in
                       ("status", "error", "variant", "source_unchanged", "shrink_choice",
                        "leaked_slots", "missed_slots")}, ensure_ascii=False))
    return 0 if res.get("status") == "PASS_NO_LEAK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
