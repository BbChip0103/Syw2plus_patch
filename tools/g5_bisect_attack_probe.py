#!/usr/bin/env python3
"""Sparse (<=20-unit) ATTACK-sustain probe for the lap685 18:19 bisection plan.

lap684/lap685 established a reproducible gap: with the full 55-unit dense
fixture and a 49/50-unit drag, the original sustains
``+0x384==ATTACK_PENDING_WORD``/``command==4`` for ~100% of the selection
over a 3s window, while every v2/v3 G5 candidate sustains it for ~0%. lap685
ruled out chunking (v2, unchunked, fails identically to v3) and ruled out
leftover literal references to the stock 20-entry selection array (a
Capstone-wide scan found none).

The 2026-09-26 18:19 operator decision is to bisect the remaining v1/v2 edit
bundles by running the *same* attack-sustain measurement against a fixture
small enough (<=20 units) that none of these bundles need to actually
exceed the stock 20-unit capacity to be exercised -- so a bundle that
already breaks attack sustain at this small scale is a strong, cheap
signal, and a bundle that passes at this scale merely defers judgment to a
later >20 test. See ``patches/selection/g5_selection_cap50_bisect.py`` for
the bundle builders (``G1``/``G2``/``G3``/``G5`` in isolation, plus
``V1_FULL``/``V2_FULL`` for the G4 control-group-hooks delta, which cannot be
isolated on the plain original -- see that module's docstring).

This reuses the worker-relative self-calibration technique from
``tools/g5_worker_relative_move_attack_probe.py`` (lap682), trimmed to a
19-unit sparse fixture (worker + 19 = 20, matching the original's proven
stock capacity) and dropping the MOVE phase entirely -- only ATTACK sustain
is in scope for this bisection.

Read-only with respect to the protected source tree: every build lands in a
fresh ``artifact_root``/private runtime copy, and the source SHA is checked
both before and after.
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

import numpy as np

from patches.selection import g5_selection_cap50_bisect as bisect
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
    selection_snapshot,
    unit_snapshot,
    sha256,
    write_json,
    capture,
)
from tools.g5_screen_world_calibration import decode_xy, fit_affine
from tools.g5_attack_move_broadcast_probe import ATTACK_BUTTON, MINIMAP_CLICK
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap686-bisect"

UNIT_BASE = 0x0066B790
UNIT_STRIDE = 0x758
UNIT_COMMAND_OFFSET = 0x290
UNIT_PENDING_COMMAND_OFFSET = 0x384
UNIT_PENDING_XY_OFFSET = 0x388
UNIT_PENDING_TARGET_UID_OFFSET = 0x38C

# Sparse fixture: a 5x4 worker-centered grid minus the worker's own cell.
# Strict subset of the dense 7x8 grid (dx -3..3, dy -3..4) that lap682-685
# already proved spawns on open, selectable ground -- no new terrain risk.
SPARSE_DX = range(-2, 3)
SPARSE_DY = range(-2, 2)
SPARSE_SEED_COUNT = len(list(SPARSE_DX)) * len(list(SPARSE_DY)) - 1  # 19

CALIBRATION_SCREEN_POINTS = [
    (250, 200), (475, 200), (700, 200),
    (250, 320), (475, 320), (700, 320),
    (250, 440), (475, 440), (700, 440),
]
# Outside the sparse grid's dy edge (-2..1) and the dense grid's proven-open
# footprint, on the same dy=6 row lap682-685 used for MOVE/ATTACK.
ATTACK_PRIMARY_DEST_OFFSET = (3, 6)
ATTACK_FALLBACK_DEST_OFFSET = (-3, 6)
SAFE_SCREEN_BOX = (0, 1580, 0, 460)
ATTACK_PENDING_WORD = 0x1000004
ATTACK_SAMPLE_WINDOW_S = 3.0
ATTACK_SAMPLE_INTERVAL_S = 0.1


def sparse_fixture_requests(worker: Mapping[str, Any]) -> list[dict[str, int]]:
    worker_x = int(worker["x"])
    worker_y = int(worker["y"])
    requests: list[dict[str, int]] = []
    for dy in SPARSE_DY:
        for dx in SPARSE_DX:
            if dx == 0 and dy == 0:
                continue
            requests.append({"x": worker_x + dx, "y": worker_y + dy, "count": 1})
    if any(not 0 <= item[axis] < 180 for item in requests for axis in ("x", "y")):
        raise ProbeError(f"sparse fixture falls outside the 180x180 map: {requests}")
    if sum(item["count"] for item in requests) != SPARSE_SEED_COUNT:
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


def _in_safe_box(point: tuple[float, float]) -> bool:
    x0, x1, y0, y1 = SAFE_SCREEN_BOX
    return x0 <= point[0] <= x1 and y0 <= point[1] <= y1


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, *, variant: str, bundle: str | None,
) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if variant == "candidate" and bundle not in bisect.BUILDERS:
        raise ProbeError(f"unsupported bundle: {bundle}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    source_exe = source / runtime_env.ORIGINAL_EXE
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_path = artifact_root / "g5_bisect_candidate.exe"
    candidate_report: dict[str, Any] | None = None
    if variant == "candidate":
        assert bundle is not None
        built, candidate_report = bisect.BUILDERS[bundle](source_exe.read_bytes())
        candidate_path.write_bytes(built)

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
        candidate_sha = sha256(private_exe)
        assert candidate_report is not None
        if candidate_sha != candidate_report["candidate_sha256"]:
            raise ProbeError("private candidate SHA verification failed")
        selection_base = int(candidate_report["selection_base"])
        selection_capacity = int(candidate_report["selection_capacity"])
    else:
        selection_base = STOCK_SELECTION_BASE
        selection_capacity = STOCK_SELECTION_CAPACITY

    expected_count = SPARSE_SEED_COUNT + 1  # fixture + pre-existing worker

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-bisect-attack-probe.v1",
        "status": "UNKNOWN",
        "variant": variant,
        "bundle": bundle,
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
            "candidate_report": candidate_report,
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

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        calibration_selection = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["calibration_selection"] = calibration_selection
        if VISIBLE_WORKER_SLOT not in calibration_selection["slots"]:
            raise ProbeError(f"worker slot not selected for calibration: {calibration_selection}")
        samples: list[tuple[tuple[int, int], tuple[int, int]]] = []
        calibration_points: list[dict[str, Any]] = []
        for point in CALIBRATION_SCREEN_POINTS:
            click(*point, button=3)
            time.sleep(0.4)
            base = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE
            raw = int.from_bytes(read_memory(pid, base + UNIT_PENDING_XY_OFFSET, 4), "little", signed=False)
            world = decode_xy(raw)
            samples.append((point, world))
            calibration_points.append({"screen": list(point), "world": list(world)})
        matrix, offset = fit_affine(samples)
        residuals = [
            float(np.max(np.abs(matrix @ np.array(point) + offset - np.array(world))))
            for point, world in samples
        ]
        result["calibration"] = {
            "points": calibration_points,
            "matrix": matrix.tolist(),
            "offset": offset.tolist(),
            "max_abs_residual": max(residuals) if residuals else None,
        }
        matrix_inv = np.linalg.inv(matrix)

        def world_to_screen(world: tuple[int, int]) -> tuple[int, int]:
            point = matrix_inv @ (np.array(world) - offset)
            return int(round(point[0])), int(round(point[1]))

        fixture_requests = sparse_fixture_requests(worker)
        result["fixture"] = {"owner": 0, "type": SEED_TYPE, "count": SPARSE_SEED_COUNT, "requests": fixture_requests}
        receipts: list[dict[str, Any]] = []
        for request in fixture_requests:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=request["x"], y=request["y"], count=request["count"])
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"sparse fixture batch failed: {receipt}")
        if sum(int(receipt.get("fixture_added", 0)) for receipt in receipts) != SPARSE_SEED_COUNT:
            raise ProbeError(f"sparse fixture total failed: {receipts}")
        time.sleep(1)
        result["captures"].append(capture(display, artifact_root / "after-fixture.png", log))

        def compute_destinations(offsets: list[tuple[int, int]]) -> list[dict[str, Any]]:
            rows: list[dict[str, Any]] = []
            for dx, dy in offsets:
                dest_world = (worker_x + dx, worker_y + dy)
                if not all(0 <= value < 180 for value in dest_world):
                    rows.append({"offset": [dx, dy], "world": list(dest_world), "usable": False, "reason": "outside 180x180 map"})
                    continue
                dest_screen = world_to_screen(dest_world)
                usable = _in_safe_box(dest_screen)
                rows.append({
                    "offset": [dx, dy], "world": list(dest_world), "screen": list(dest_screen),
                    "usable": usable, "reason": None if usable else "outside safe screen box",
                })
            return rows

        worker_x, worker_y = int(worker["x"]), int(worker["y"])
        attack_destinations = compute_destinations([ATTACK_PRIMARY_DEST_OFFSET, ATTACK_FALLBACK_DEST_OFFSET])
        result["attack_destination_candidates"] = attack_destinations
        usable_attack_destinations = [d for d in attack_destinations if d.get("usable")]
        if not usable_attack_destinations:
            raise ProbeError(f"no worker-relative attack destination candidate is on-screen: {attack_destinations}")
        attack_primary_destination = usable_attack_destinations[0]
        attack_retry_destination = usable_attack_destinations[1] if len(usable_attack_destinations) > 1 else None

        attack_target_world = tuple(int(v) for v in attack_primary_destination["world"])
        target_receipt = supply.call(
            op=5, owner=1, unit_type=SEED_TYPE,
            x=attack_target_world[0], y=attack_target_world[1], count=1,
        )
        if not target_receipt.get("ok") or target_receipt.get("fixture_added") != 1:
            raise ProbeError(f"attack target fixture failed: {target_receipt}")
        attack_target_slot = int(target_receipt.get("producer", {}).get("slot", 0))
        if not 0 < attack_target_slot < 1200:
            raise ProbeError(f"attack target slot missing: {target_receipt}")
        attack_target_base = UNIT_BASE + attack_target_slot * UNIT_STRIDE
        attack_target_handle = int.from_bytes(read_memory(pid, attack_target_base + 0x29C, 4), "little")
        result["attack_target_fixture"] = {
            "owner": 1, "type": SEED_TYPE, "world": list(attack_target_world),
            "screen": attack_primary_destination["screen"],
            "slot": attack_target_slot, "handle": attack_target_handle,
        }
        time.sleep(0.5)

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selection_after"] = after
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))
        if after["count"] != expected_count or after["unique_slots"] != expected_count:
            raise ProbeError(f"drag did not select the full sparse fixture: {after}")
        slots = after["slots"]
        attack_capable_slots = [slot for slot in slots if slot != VISIBLE_WORKER_SLOT]
        attack_expected_count = len(attack_capable_slots)

        def sample_attack_window(destination: Mapping[str, Any]) -> dict[str, Any]:
            screen = tuple(destination["screen"])
            click(*ATTACK_BUTTON, button=1)
            time.sleep(0.1)
            click(*screen, button=1)
            dest_world = tuple(int(v) for v in destination["world"])
            deadline = time.monotonic() + ATTACK_SAMPLE_WINDOW_S
            curve: list[dict[str, Any]] = []
            best_pending_count = 0
            best_rows: list[dict[str, Any]] = []
            ever_command4: set[int] = set()
            target_uids: set[int] = set()
            start = time.monotonic()
            while time.monotonic() < deadline:
                rows = [read_unit_full(pid, slot) for slot in attack_capable_slots if 0 < slot < 1200]
                pending_count = sum(1 for row in rows if row["pending_command"] == ATTACK_PENDING_WORD)
                for row in rows:
                    if row["command"] == 4:
                        ever_command4.add(int(row["slot"]))
                    if row["pending_target_uid"]:
                        target_uids.add(int(row["pending_target_uid"]))
                curve.append({"elapsed_s": round(time.monotonic() - start, 2), "pending_exact_count": pending_count})
                if pending_count >= best_pending_count:
                    best_pending_count = pending_count
                    best_rows = rows
                time.sleep(ATTACK_SAMPLE_INTERVAL_S)
            pending_xy_match_count = sum(
                1 for row in best_rows if decode_xy(row["pending_xy"]) == dest_world
            )
            return {
                "destination": destination,
                "curve": curve,
                "max_pending_exact_count": best_pending_count,
                "rows_at_max": best_rows,
                "ever_command4_count": len(ever_command4),
                "observed_target_uids": sorted(target_uids),
                "pending_xy_match_count": pending_xy_match_count,
            }

        attack_result = sample_attack_window(attack_primary_destination)
        if attack_result["max_pending_exact_count"] == 0 and attack_retry_destination is not None:
            retry_attack_result = sample_attack_window(attack_retry_destination)
            result["attack_sample_primary"] = attack_result
            result["attack_sample_retry"] = retry_attack_result
            attack_result = retry_attack_result
        result["captures"].append(capture(display, artifact_root / "after-attack-click.png", log))

        command_histogram: dict[str, int] = {}
        for row in attack_result["rows_at_max"]:
            key = str(row.get("command"))
            command_histogram[key] = command_histogram.get(key, 0) + 1
        attack_result["raw_command_histogram"] = command_histogram

        result["before_selected_count"] = len(slots)
        result["expected_count"] = expected_count
        result["attack_capable_count"] = attack_expected_count
        result["attack_window"] = attack_result
        result["attack_pass"] = attack_result["ever_command4_count"] == attack_expected_count
        result["status"] = "ATTACK_SUSTAIN_MEASURED"
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
    parser.add_argument("--bundle", choices=tuple(bisect.BUILDERS), default=None)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, default=DEFAULT_RUNTIME_ROOT)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.variant == "candidate" and args.bundle is None:
        parser.error("--bundle is required when --variant=candidate")
    result = run_probe(args.source, args.runtime_root, args.artifact_root, variant=args.variant, bundle=args.bundle)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "ATTACK_SUSTAIN_MEASURED" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
