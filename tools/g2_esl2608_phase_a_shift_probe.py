#!/usr/bin/env python3
"""Fresh paired Phase-A selection probe for the two ESL2608 G2 executables.

The probe keeps the protected source and ``../260921_temp`` read-only.  Each
run gets a complete private game copy, a new Wine prefix, and a private Xvfb.
It seeds 25 owner-0 units, then records the stock 20-entry selection contract:
1-unit selection, 19-unit drag, 19->20 Shift add, Ctrl+1 recall, 20->20
21st-unit rejection, and Shift remove/re-add.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Mapping, cast

from patches.population import g2_esl2608_pool4092_owner500 as pool_patch
from patches.population import g2_esl2608_supply1500_500_5000 as supply_patch
from patches.population.g2_esl2608_runtime_layout import (
    ESL2608_LAYOUT,
    from_build_report as esl2608_layout_from_build_report,
)
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools import runtime_env
from tools.g5_candidate_drag_probe import ProbeError, SupplyProbe, capture, sha256, write_json
from tools.g5_screen_world_calibration import decode_xy, fit_affine

REPO = Path(__file__).resolve().parents[1]
INPUT_ROOT = REPO.parent / "260921_temp" / "archive"
BASE_SOURCE = REPO.parent / "[ESL]Syw2plus"
DATA_OVERLAY = INPUT_ROOT.parent / "[ESL]Syw2plus 2608"
LEGACY = INPUT_ROOT / "[ESL]Syw2plus 2606_장수7명_전비1600-200-3000.exe"
STOCK = REPO / "Syw2plus" / "syw2plus_original.exe"
LANES = {
    "normal": INPUT_ROOT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1600-200-3000.exe",
    "fixed_start": INPUT_ROOT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1600-200-3000_시작자리고정.exe",
}
EXPECTED_BASELINE = {
    "normal": "cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3",
    "fixed_start": "f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973",
}
EXPECTED_CANDIDATE = {
    "normal": "83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60",
    "fixed_start": "1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f",
}

STOCK_SELECTION_BASE = 0x00899024
SELECTION_CAPACITY = 20
UNIT_STRIDE = 0x758
UNIT_X_OFFSET = 0x2A2
UNIT_Y_OFFSET = 0x2A4
UNIT_TYPE_OFFSET = 0x8D
UNIT_OWNER_OFFSET = 0x8E
UNIT_HP_OFFSET = 0xB4
UNIT_INTERNAL_ID_OFFSET = 0x29C
UNIT_PENDING_XY_OFFSET = 0x388
VISIBLE_WORKER_SLOT = 1198
SEED_TYPE = 2
CALIBRATION_POINTS = [(180, 150), (390, 150), (600, 150),
                      (180, 270), (390, 270), (600, 270),
                      (180, 390), (390, 390), (600, 390)]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_candidate(source: bytes) -> tuple[bytes, dict[str, Any]]:
    intermediate, first = pool_patch.build_candidate(source, LEGACY.read_bytes(), STOCK.read_bytes())
    candidate, second = supply_patch.build_candidate(intermediate)
    return candidate, {"pool": first, "supply": second, "candidate_sha256": digest(candidate)}


def selection_snapshot(pid: int) -> dict[str, Any]:
    count = int.from_bytes(read_memory(pid, STOCK_SELECTION_BASE, 4), "little", signed=True)
    if not 0 <= count <= SELECTION_CAPACITY:
        raise ProbeError(f"selection count outside stock 0..20: {count}")
    raw = [int.from_bytes(read_memory(pid, STOCK_SELECTION_BASE + 4 + i * 4, 4), "little")
           for i in range(count)]
    slots = [value & 0xFFF for value in raw]
    return {"count": count, "raw_entries": raw, "slots": slots,
            "unique_slots": len(set(slots))}


def unit_layout(candidate: bool) -> tuple[int, int, int]:
    if not candidate:
        return 0x0066B790, 0x008990C8, 1200
    return (ESL2608_LAYOUT.unit_pool_base, ESL2608_LAYOUT.unit_existence_base,
            ESL2608_LAYOUT.capacity)


def unit_row(pid: int, slot: int, *, candidate: bool) -> dict[str, int]:
    unit_base, exists_base, capacity = unit_layout(candidate)
    if not 0 < slot < capacity:
        raise ProbeError(f"unit slot outside capacity: {slot}")
    base = unit_base + slot * UNIT_STRIDE
    return {
        "slot": slot,
        "exists": int.from_bytes(read_memory(pid, exists_base + slot * 2, 2), "little"),
        "type": int.from_bytes(read_memory(pid, base + UNIT_TYPE_OFFSET, 1), "little"),
        "owner": int.from_bytes(read_memory(pid, base + UNIT_OWNER_OFFSET, 1), "little"),
        "hp": int.from_bytes(read_memory(pid, base + UNIT_HP_OFFSET, 4), "little", signed=True),
        "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
        "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
        "internal_id": int.from_bytes(read_memory(pid, base + UNIT_INTERNAL_ID_OFFSET, 4), "little"),
    }


def live_fixture(pid: int, *, candidate: bool) -> list[dict[str, int]]:
    _unit_base, exists_base, capacity = unit_layout(candidate)
    rows = []
    for slot in range(1, capacity):
        if int.from_bytes(read_memory(pid, exists_base + slot * 2, 2), "little") == 0:
            continue
        row = unit_row(pid, slot, candidate=candidate)
        if row["owner"] == 0 and row["type"] == SEED_TYPE and row["hp"] > 0:
            rows.append(row)
    return rows


def find_worker(pid: int, *, candidate: bool) -> dict[str, int]:
    if not candidate:
        row = unit_row(pid, VISIBLE_WORKER_SLOT, candidate=False)
        if row["owner"] == 0 and row["type"] == 7 and row["hp"] > 0:
            row["pool_mode"] = 0
            return row
        raise ProbeError(f"stock worker anchor invalid: {row}")
    _unit_base, exists_base, capacity = unit_layout(True)
    fallback: dict[str, int] | None = None
    for slot in range(1, capacity):
        if int.from_bytes(read_memory(pid, exists_base + slot * 2, 2), "little") == 0:
            continue
        row = unit_row(pid, slot, candidate=True)
        if row["owner"] == 0 and row["hp"] > 0:
            if row["type"] == 7:
                row["pool_mode"] = 1
                return row
            if fallback is None:
                fallback = row
    if fallback is not None:
        fallback["pool_mode"] = 1
        return fallback
    try:
        snapshot = read_state(pid, detailed=True, profile="g2_esl2608_pool4092_owner500")
        for item in snapshot.get("units", []):
            if item.get("owner") == 0 and item.get("hp", 0) > 0:
                return {
                    "slot": int(item["slot"]), "exists": 1, "type": int(item["type"]),
                    "owner": int(item["owner"]), "hp": int(item["hp"]),
                    "x": int(item["x"]), "y": int(item["y"]),
                    "internal_id": int(item["internal_id"]), "pool_mode": 1,
                }
    except (OSError, ValueError, KeyError, TypeError):
        pass
    # Diagnostic only: if relocation initialization is absent, distinguish it
    # from a reader-address error by checking the untouched stock pool.
    for slot in range(1, 1200):
        row = unit_row(pid, slot, candidate=False)
        if row["owner"] == 0 and row["hp"] > 0:
            row["pool_mode"] = 0
            return row
    raise ProbeError("relocated candidate has no live owner-0 anchor unit")


def copy_overlay(game: Path) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for item in sorted(DATA_OVERLAY.rglob("*")):
        if item.is_symlink() or not item.is_file() or item.suffix.lower() in {".exe", ".xlsx"}:
            continue
        relative = item.relative_to(DATA_OVERLAY)
        target = game / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        copied.append({"path": str(relative), "sha256": sha256(target), "bytes": target.stat().st_size})
    return copied


def _wait_state(pid: int, predicate: Any, label: str, timeout: float = 45) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            last = read_state(pid)
            if predicate(last):
                return last
        except (OSError, ValueError, ProbeError) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.25)
    raise ProbeError(f"{label} timeout; last={last}")


def run_probe(lane: str, variant: str, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if lane not in LANES or variant not in {"baseline", "candidate"}:
        raise ProbeError(f"unsupported lane/variant: {lane}/{variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    baseline_path = LANES[lane]
    baseline = baseline_path.read_bytes()
    baseline_sha = digest(baseline)
    if baseline_sha != EXPECTED_BASELINE[lane]:
        raise ProbeError(f"baseline SHA mismatch: {baseline_sha}")
    candidate, build_report = build_candidate(baseline)
    candidate_sha = digest(candidate)
    if candidate_sha != EXPECTED_CANDIDATE[lane]:
        raise ProbeError(f"candidate SHA mismatch: {candidate_sha}")
    candidate_layout = esl2608_layout_from_build_report(build_report["pool"])

    bridge_dir = artifact_root / "bridge"
    bridge_capacity = 4093 if variant == "candidate" else 1200
    bridge_command = [
        sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
        "--out-dir", str(bridge_dir), "--unit-pool-capacity", str(bridge_capacity),
    ]
    if variant == "candidate":
        bridge_command.extend(["--unit-pool-base", hex(candidate_layout.unit_pool_base)])
    subprocess.run(bridge_command, cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    run_dir = Path(cast(str, cast(Mapping[str, Any], manifest["output"])["run_dir"]))
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("private source copy SHA mismatch before 2608 install")
    overlay = copy_overlay(game)
    private_exe.write_bytes(baseline if variant == "baseline" else candidate)
    expected_private = baseline_sha if variant == "baseline" else candidate_sha
    if sha256(private_exe) != expected_private:
        raise ProbeError("private 2608 executable SHA mismatch after install")
    result: dict[str, Any] = {
        "schema": "syw2plus.g2-esl2608-phase-a-shift.v1", "status": "UNKNOWN",
        "lane": lane, "variant": variant,
        "fixture": {"synthetic": True, "owner": 0, "type": SEED_TYPE,
                     "active_minimum": 25, "selection_capacity": 20},
        "provenance": {
            "baseline_path": str(baseline_path), "baseline_sha256": baseline_sha,
            "candidate_sha256": candidate_sha, "private_exe_sha256": expected_private,
            "private_run_dir": str(run_dir), "private_game": str(game), "private_prefix": str(prefix),
            "base_source": str(BASE_SOURCE), "data_overlay": str(DATA_OVERLAY),
            "overlay_files": overlay, "bridge_sha256": sha256(bridge),
            "bridge_capacity": bridge_capacity, "build_report": build_report,
        },
        "inputs": [], "stages": {}, "cleanup": {},
    }
    log_path = artifact_root / "probe.log"
    log = log_path.open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    game_proc: Any = None
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
                   SYW2_SUPPLY_PROBE="1")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env,
                                     stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid
        _wait_state(pid, lambda s: s.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        origin = (int(info["x"]), int(info["y"]))

        def click(x: int, y: int, *, button: int = 1,
                  drag_to: tuple[int, int] | None = None) -> None:
            args = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(origin[0] + x), str(origin[1] + y), "--button", str(button)]
            if drag_to is not None:
                args += ["--drag-to", str(origin[0] + drag_to[0]), str(origin[1] + drag_to[1])]
            subprocess.run(args, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "button": button,
                                     "drag_to": list(drag_to) if drag_to else None})

        def key(name: str, *, ctrl: bool = False) -> None:
            args = ["xdotool", "keydown", "ctrl", "key", name, "keyup", "ctrl"] if ctrl else ["xdotool", "key", name]
            subprocess.run(args, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"key": name, "ctrl": ctrl})

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log,
                       timeout=10, check=True)
        click(184, 560)
        _wait_state(pid, lambda s: s.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        _wait_state(pid, lambda s: s.get("ps") == 5, "ps5")
        _wait_state(pid, lambda s: s.get("ps") == 5 and
                    runtime_env._read_local_ready_state(lambda a, n: read_memory(pid, a, n)).get("ready_value") == 1,
                    "ready", timeout=15)
        click(608, 564)
        _wait_state(pid, lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")
        worker = find_worker(pid, candidate=variant == "candidate")
        result["stages"]["bootstrap"] = {"worker": worker}
        supply = SupplyProbe(prefix)
        map_width = int.from_bytes(read_memory(pid, 0x00B3DE34, 2), "little", signed=True)
        map_height = int.from_bytes(read_memory(pid, 0x00B3DE36, 2), "little", signed=True)
        x_offsets = tuple(
            dx for dx in range(-30, 31, 3)
            if 0 < worker["x"] + dx < map_width
        )[:10]
        y_offsets = tuple(range(-10, 0))
        points = [
            (worker["x"] + dx, worker["y"] + dy)
            for dy in y_offsets for dx in x_offsets
            if 0 < worker["x"] + dx < map_width and 0 < worker["y"] + dy < map_height
        ]
        if len(points) < 100:
            raise ProbeError(f"map cannot fit Phase-A sparse fixture: width={map_width}, height={map_height}, points={points}")
        for x, y in points[:100]:
            request = supply.call(op=5, owner=0, unit_type=SEED_TYPE,
                                  x=x, y=y, count=1)
            if not request.get("ok") or request.get("fixture_added") != 1:
                raise ProbeError(f"fixture spawn failed at {(x, y)}: {request}")
        time.sleep(1)
        fixture = live_fixture(pid, candidate=variant == "candidate")
        if len(fixture) < 100:
            raise ProbeError(f"active fixture below 100: {len(fixture)}")
        # The placement helper may advance around occupied cells.  Use the
        # authoritative post-spawn rows, not requested coordinates.  The
        # first four rows are selected; the fifth row provides rejection.
        ordered = sorted(fixture, key=lambda row: (row["y"], row["x"], row["slot"]))
        if len(ordered) < 25:
            raise ProbeError(f"fixture mapping incomplete: {ordered}")
        # Fit the screen/world transform using right-click pending coordinates.
        # Select the live worker before sampling; without a selected unit the
        # pending target remains constant and the affine fit is singular.
        click(200, 170, drag_to=(730, 445))
        time.sleep(0.4)
        click(120, 90, button=3)
        time.sleep(0.2)
        anchor_candidate = bool(worker.get("pool_mode", int(variant == "candidate")))
        unit_base, _exists, _capacity = unit_layout(anchor_candidate)
        worker_base = unit_base + worker["slot"] * UNIT_STRIDE
        samples: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for point in CALIBRATION_POINTS:
            click(*point, button=3)
            time.sleep(0.2)
            raw = int.from_bytes(read_memory(pid, worker_base + UNIT_PENDING_XY_OFFSET, 4), "little")
            samples.append((point, decode_xy(raw)))
        matrix, offset = fit_affine(samples)
        inverse = __import__("numpy").linalg.inv(matrix)

        def world_to_screen(x: int, y: int) -> tuple[int, int]:
            point = inverse @ (__import__("numpy").array([x, y]) - offset)
            return int(round(point[0])), int(round(point[1]))

        visible_rows = [
            (row, world_to_screen(row["x"], row["y"]))
            for row in ordered
            if 5 <= world_to_screen(row["x"], row["y"])[0] <= 795
            and 45 <= world_to_screen(row["x"], row["y"])[1] <= 470
        ]
        if len(visible_rows) < 21:
            raise ProbeError(f"selection fixture has fewer than 21 visible rows: {visible_rows}")
        result["stages"]["fixture"] = {"active_units": len(fixture), "map_width": map_width,
                                         "map_height": map_height,
                                         "calibration_max_residual": float(max(
                                             max(abs(v) for v in (matrix @ __import__("numpy").array(p) + offset - __import__("numpy").array(w)))
                                             for p, w in samples))}
        # Sparse rows make individual hit-tests unambiguous.  Verify every
        # target plain-click first; sprites at different world rows can need
        # different y offsets even under one camera transform.
        blank = world_to_screen(worker["x"], worker["y"] - 8)

        def deselect() -> dict[str, Any]:
            click(*blank)
            time.sleep(0.25)
            snapshot = selection_snapshot(pid)
            if snapshot["count"] != 0:
                raise ProbeError(f"deselect point was not empty: {snapshot}")
            return snapshot

        isolated_rows: list[tuple[dict[str, int], tuple[int, int]]] = []
        isolated_offsets: list[int] = []
        for target, screen in visible_rows:
            found: int | None = None
            for dy in (-12, -20, -6, 0, 6):
                deselect()
                x, y = screen
                click(x, y + dy)
                time.sleep(0.3)
                probe_selection = selection_snapshot(pid)
                if probe_selection["count"] == 1 and probe_selection["slots"] == [target["slot"]]:
                    found = dy
                    break
            if found is not None:
                isolated_rows.append((target, screen))
                isolated_offsets.append(found)
            if len(isolated_rows) >= 21:
                break
        if len(isolated_rows) < 21:
            raise ProbeError(f"fewer than 21 isolated live rows: {isolated_rows}")
        selected_targets = [row for row, _screen in isolated_rows[:20]]
        screen_coords = [screen for _row, screen in isolated_rows[:20]]
        rejected_target, rejected_screen = isolated_rows[20]
        click_offsets = isolated_offsets[:20]
        rejected_offset = isolated_offsets[20]
        result["stages"]["fixture"]["isolated_rows"] = len(isolated_rows)
        result["stages"]["fixture"]["selected_targets"] = selected_targets
        result["stages"]["fixture"]["rejected_target"] = rejected_target
        result["stages"]["fixture"]["screen_coords"] = screen_coords
        deselect()
        select_one_index = 0

        def select_one(index: int, *, shift: bool) -> None:
            x, y = screen_coords[index]
            if shift:
                subprocess.run(["xdotool", "keydown", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
                time.sleep(0.15)
            try:
                click(x, y + click_offsets[index])
            finally:
                if shift:
                    time.sleep(0.15)
                    subprocess.run(["xdotool", "keyup", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            time.sleep(0.25)

        select_one(select_one_index, shift=False)
        stage: dict[str, Any] = {"select_1": selection_snapshot(pid)}
        if stage["select_1"]["count"] != 1:
            raise ProbeError(f"plain one-unit selection failed: {stage['select_1']}")
        for index in range(1, 19):
            select_one(index, shift=True)
            observed = selection_snapshot(pid)
            if observed["count"] != index + 1:
                raise ProbeError(f"Shift step {index} failed: expected={index + 1}, observed={observed}, target={selected_targets[index]}")
        stage["select_19"] = selection_snapshot(pid)
        if stage["select_19"]["count"] != 19:
            raise ProbeError(f"Shift accumulation to 19 failed: {stage['select_19']}")
        select_one(19, shift=True)
        stage["shift_19_to_20"] = selection_snapshot(pid)
        key("1", ctrl=True)
        deselect()
        stage["group_cleared"] = selection_snapshot(pid)
        key("1", ctrl=True)
        time.sleep(0.35)
        stage["group_recall"] = selection_snapshot(pid)
        outside = rejected_screen
        subprocess.run(["xdotool", "keydown", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
        time.sleep(0.15)
        click(outside[0], outside[1] + cast(int, rejected_offset))
        time.sleep(0.15)
        subprocess.run(["xdotool", "keyup", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
        time.sleep(0.4)
        stage["shift_20_to_21_reject"] = selection_snapshot(pid)
        select_one(19, shift=True)
        stage["shift_remove_20"] = selection_snapshot(pid)
        select_one(19, shift=True)
        stage["shift_readd_20"] = selection_snapshot(pid)
        result["stages"]["selection"] = stage
        result["status"] = "PASS" if (
            stage["select_1"]["count"] == 1 and stage["select_19"]["count"] == 19 and
            stage["shift_19_to_20"]["count"] == 20 and stage["group_recall"]["count"] == 20 and
            stage["shift_20_to_21_reject"]["count"] == 20 and
            stage["shift_remove_20"]["count"] == 19 and stage["shift_readd_20"]["count"] == 20
        ) else "FAIL"
        capture(display, artifact_root / f"{time.strftime('%Y%m%d_%H%M%S')}_final.png", log)
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
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
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
        subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        subprocess.run(["wineserver", "-w"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=5)
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix),
                              "game_removed": False}
        if game.exists():
            shutil.rmtree(game)
        result["cleanup"]["game_removed"] = not game.exists()
        result["source_data_sha_after"] = sha256(baseline_path)
        result["source_data_unchanged"] = result["source_data_sha_after"] == baseline_sha
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=sorted(LANES), required=True)
    parser.add_argument("--variant", choices=("baseline", "candidate"), required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.lane, args.variant, args.runtime_root, args.artifact_root)
    print(json.dumps({"status": result.get("status"), "lane": args.lane,
                      "variant": args.variant, "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
