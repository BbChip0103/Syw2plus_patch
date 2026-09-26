#!/usr/bin/env python3
"""G5 attack-move broadcast probe: original20 vs candidate50, paired.

lap672/lap673 spent 9 sprite-hit-test attempts (affine click math, then
capture-diff centroid search) trying to land a UI click on an enemy's own
screen sprite, and all 9 failed to acquire ``+0x38c`` (pending target uid)
even once -- including g5_screen_world_calibration.py's exact-coordinate
verification, where the click point was the literal inverse of a
freshly-measured world position and the hit-test still missed. The 2026-09-26
10:31 operator decision (loop/ESCALATE_SOL, lap673 section) redefines the G5
attack judgement so it no longer depends on hitting a sprite at all:

  1. UI-drag select every fixture unit (already validated: 50/50 on the
     candidate, 20/20 on the original).
  2. Press 'A' then left-click a *ground* point (an attack-move order) --
     no sprite needs to be under the cursor.
  3. Count how many selected units flip into the attack-move command series
     (``+0x290==4`` or ``(+0x384 & 0xffff)==4``) after that one click. This
     is the primary PASS/FAIL gate: does the product accept an attack order
     for every selected unit, not just 20 of them.
  4. A single owner-1 enemy is seeded near the clicked ground point purely
     as a backup/secondary metric: after the broadcast units walk there,
     count how many reach the live engaged state (``+0x290==4`` with
     ``+0x38c`` equal to that enemy's handle) via autonomous aggro. This
     does not gate PASS/FAIL -- it is recorded for provenance only.

Read-only investigation plus the already-approved G5 selection-cap50
candidate build; no other product EXE bytes are touched here.
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

from patches.selection import g5_selection_cap50_v2 as g5
from tools import runtime_env
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools.g5_candidate_drag_probe import (
    ProbeError,
    SupplyProbe,
    DRAG_START,
    DRAG_END,
    UNIT_BASE,
    UNIT_STRIDE,
    UNIT_COMMAND_OFFSET,
    UNIT_PENDING_COMMAND_OFFSET,
    UNIT_PENDING_XY_OFFSET,
    UNIT_PENDING_TARGET_UID_OFFSET,
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
from tools.g5_screen_world_calibration import (
    CALIBRATION_SCREEN_POINTS,
    fit_affine,
    read_unit,
)

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
TARGET_SHA = "ae495fa5a1498597c265ad9bcae6444f564ade92adb311a3c413c4fb9996b5b7"
DEFAULT_RUNTIME_ROOT = REPO / "local" / "runtime" / "g5-lap674-attack-move-broadcast"
MINIMAP_CLICK = (235, 555)
# lap674 run1 found the rendered/clickable game viewport in this isometric
# original build stops well short of the 1600x1200 desktop (visually
# confirmed: everything past roughly x=800 on screen is black desktop, not
# game canvas), so a screen point computed from a larger world offset (e.g.
# the previously-used (11, -7), which maps to screen x=989) lands outside
# the canvas and is silently dropped -- no unit changed state at all in that
# run. (0, -10) is the largest same-direction offset from the worker that
# still maps inside the confirmed-safe screen box while staying outside the
# worker-centered 7x8 dense fixture grid (dx -3..3, dy -3..4).
DESTINATION_OFFSET_FROM_WORKER = (0, -10)
# lap674 run2 confirmed the keyboard 'a' hotkey + ground left-click (the
# operator's option (1)) does land -- the destination screen point was
# reachable and the click registered -- but the engine only ever issued a
# plain move order (command 3) for every unit, never the attack series
# (command 4). The toolbar has its own dedicated attack button (the sword
# icon in the second command-panel row, confirmed by cropping
# before-attack-move.png from that run); this is the operator's option (2)
# ("공격 버튼+지면 클릭"), tried here instead of the keyboard hotkey.
ATTACK_BUTTON = (663, 536)


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


def is_attack_move(sample: Mapping[str, Any]) -> bool:
    """True once a unit's command/pending word enters the attack series.

    ``+0x290==4`` is the live attack command state; ``+0x384`` (the pending
    command word) carries the same ``4`` in its low 16 bits the instant an
    attack-type order (including an attack-move with no target under the
    cursor) is queued, before the live state field catches up. Matching
    either field means the broadcast reached this unit's order queue.
    """
    command = sample.get("command")
    pending = sample.get("pending_command")
    return command == 4 or (isinstance(pending, int) and (pending & 0xFFFF) == 4)


def broadcast_summary(
    before: list[dict[str, Any]], immediate: list[dict[str, Any]], delayed: list[dict[str, Any]],
) -> dict[str, Any]:
    immediate_by_slot = {int(row["slot"]): row for row in immediate}
    delayed_by_slot = {int(row["slot"]): row for row in delayed}
    rows: list[dict[str, Any]] = []
    for row in before:
        slot = int(row["slot"])
        immediate_row = immediate_by_slot.get(slot, {})
        delayed_row = delayed_by_slot.get(slot, {})
        hit = is_attack_move(immediate_row) or is_attack_move(delayed_row)
        rows.append({
            "slot": slot,
            "command_before": row.get("command"),
            "pending_command_before": row.get("pending_command"),
            "command_immediate": immediate_row.get("command"),
            "pending_command_immediate": immediate_row.get("pending_command"),
            "command_delayed": delayed_row.get("command"),
            "pending_command_delayed": delayed_row.get("pending_command"),
            "attack_move_command": hit,
        })
    count = sum(bool(row["attack_move_command"]) for row in rows)
    return {
        "selected_count": len(rows),
        "attack_move_command_count": count,
        "all_selected_broadcast": len(rows) > 0 and count == len(rows),
        "rows": rows,
    }


def engaged_summary(final: list[dict[str, Any]], enemy_handle: int) -> dict[str, Any]:
    rows = [
        {
            "slot": int(row["slot"]),
            "command_final": row.get("command"),
            "pending_target_uid_final": row.get("pending_target_uid"),
            "engaged_target_match": row.get("command") == 4 and row.get("pending_target_uid") == enemy_handle,
        }
        for row in final
    ]
    return {
        "enemy_handle": enemy_handle,
        "engaged_target_match_count": sum(bool(row["engaged_target_match"]) for row in rows),
        "rows": rows,
    }


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, *, variant: str,
) -> dict[str, Any]:
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
        "schema": "syw2plus.g5-attack-move-broadcast-probe.v1",
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

        # --- Step 1: calibrate the screen->world affine from the worker's
        # own plain right-click moves, before any fixture/enemy unit exists,
        # so no other unit's drag/select/move is disturbed by these moves.
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        worker_selection = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        if VISIBLE_WORKER_SLOT not in worker_selection["slots"]:
            raise ProbeError(f"worker slot not selected for calibration: {worker_selection}")
        result["captures"].append(capture(display, artifact_root / "after-worker-drag.png", log))

        samples: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for point in CALIBRATION_SCREEN_POINTS:
            click(*point, button=3)
            time.sleep(0.4)
            unit = read_unit(pid, VISIBLE_WORKER_SLOT)
            world = tuple(unit["pending_xy"])
            samples.append((point, world))
            result["calibration_points"].append({"screen": list(point), "world": list(world)})
        matrix, offset = fit_affine(samples)
        matrix_inv = np.linalg.inv(matrix)
        residuals = [
            float(np.max(np.abs(matrix @ np.array(point) + offset - np.array(world))))
            for point, world in samples
        ]
        result["fit_max_abs_error"] = max(residuals)

        def to_screen(world: tuple[int, int]) -> tuple[int, int]:
            float_point = matrix_inv @ (np.array(world) - offset)
            return (int(round(float_point[0])), int(round(float_point[1])))

        # --- Step 2: seed the dense 55-unit type2 broadcast fixture around
        # the worker (the same anchor/grid the drag-cap50 probe validated).
        fixture_requests = dense_fixture_requests(worker)
        result["fixture"] = {"owner": 0, "type": SEED_TYPE, "count": SEED_COUNT, "requests": fixture_requests}
        receipts: list[dict[str, Any]] = []
        for request in fixture_requests:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=request["x"], y=request["y"], count=request["count"])
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"dense fixture batch failed: {receipt}")
        result["fixture_receipts"] = receipts
        if sum(int(receipt.get("fixture_added", 0)) for receipt in receipts) != SEED_COUNT:
            raise ProbeError(f"dense fixture total failed: {receipts}")
        time.sleep(1)

        # --- Step 3: seed one owner-1 enemy near the ground point the
        # broadcast click will target. This is placed far outside the dense
        # fixture footprint (dx -3..3, dy -3..4) so it is not already inside
        # any broadcast unit's aggro radius before the attack-move click.
        destination_world = (
            int(worker["x"]) + DESTINATION_OFFSET_FROM_WORKER[0],
            int(worker["y"]) + DESTINATION_OFFSET_FROM_WORKER[1],
        )
        if any(not 0 <= value < 180 for value in destination_world):
            raise ProbeError(f"destination falls outside the map: {destination_world}")
        enemy_receipt = supply.call(op=5, owner=1, unit_type=SEED_TYPE, x=destination_world[0], y=destination_world[1], count=1)
        if not enemy_receipt.get("ok") or enemy_receipt.get("fixture_added") != 1:
            raise ProbeError(f"enemy fixture failed: {enemy_receipt}")
        enemy_slot = int(enemy_receipt.get("producer", {}).get("slot", 0))
        enemy_base = UNIT_BASE + enemy_slot * UNIT_STRIDE
        enemy_handle = int.from_bytes(read_memory(pid, enemy_base + 0x29C, 4), "little")
        result["enemy_fixture"] = {
            "owner": 1, "type": SEED_TYPE, "requested_world": list(destination_world),
            "slot": enemy_slot, "handle": enemy_handle, "receipt": enemy_receipt,
        }
        result["captures"].append(capture(display, artifact_root / "after-fixture.png", log))

        destination_screen = to_screen(destination_world)
        result["destination_screen_computed"] = list(destination_screen)
        # lap674 run1 measured the actual rendered/clickable canvas edge near
        # x=800 (a click at x=989 landed on black desktop and changed
        # nothing); keep a margin inside that edge rather than the
        # 1600-wide desktop bound other probes used for smaller offsets.
        if not (200 <= destination_screen[0] <= 780 and 170 <= destination_screen[1] <= 460):
            raise ProbeError(f"computed destination screen point unsafe/out of viewport: {destination_screen}")

        # --- Step 4: broadcast selection (the already-validated drag path).
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
        result["selection_after"] = after
        result["captures"].append(capture(display, artifact_root / "after-drag.png", log))
        if after["count"] == 0:
            result["drag_retry"] = {"attempted": True, "same_rectangle": True}
            click(*DRAG_START, drag_to=DRAG_END)
            time.sleep(1)
            after = selection_snapshot(pid, base=selection_base, capacity=selection_capacity)
            result["selection_after_retry"] = after
            result["captures"].append(capture(display, artifact_root / "after-drag-retry.png", log))
            if after["count"] == 0:
                raise ProbeError("drag produced no selection after one retry")

        before_attack = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]
        result["captures"].append(capture(display, artifact_root / "before-attack-move.png", log))

        # --- Step 5: the product input under test -- the toolbar attack
        # button, then one ground-point left-click. No sprite hit-test is
        # required.
        click(*ATTACK_BUTTON, button=1)
        result["inputs"].append({"attack_button": list(ATTACK_BUTTON)})
        time.sleep(0.1)
        click(*destination_screen, button=1)
        time.sleep(0.05)
        immediate = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]
        time.sleep(0.3)
        delayed = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]
        result["captures"].append(capture(display, artifact_root / "after-attack-move.png", log))

        result["attack_move_broadcast"] = broadcast_summary(before_attack, immediate, delayed)

        # --- Step 6 (secondary/backup metric only, does not gate PASS):
        # let the broadcast units walk toward the enemy and record how many
        # reach the live engaged state via autonomous aggro.
        time.sleep(6)
        final = [read_unit_full(pid, slot) for slot in after["slots"] if 0 < slot < 1200]
        result["captures"].append(capture(display, artifact_root / "after-settle.png", log))
        result["engaged_after_settle"] = engaged_summary(final, enemy_handle)

        selected_ok = after["count"] == expected_count and after["unique_slots"] == expected_count
        broadcast_ok = result["attack_move_broadcast"]["all_selected_broadcast"]
        if variant == "candidate":
            result["status"] = "PASS_ATTACK_MOVE_BROADCAST" if selected_ok and broadcast_ok else "FAIL_ATTACK_MOVE_BROADCAST"
        else:
            result["status"] = "PASS_ORIGINAL_ATTACK_MOVE_BROADCAST" if selected_ok and broadcast_ok else "FAIL_ORIGINAL_ATTACK_MOVE_BROADCAST"
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
    return 0 if result.get("status", "").startswith("PASS") and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
