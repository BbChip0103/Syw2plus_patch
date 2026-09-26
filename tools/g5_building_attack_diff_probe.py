#!/usr/bin/env python3
"""One original-only run: attack-click a building target (bigger hitbox than a unit).

lap673 (two original-only runs) found that a small mobile-unit target's
sprite cannot be reliably isolated from this game's own widespread ambient
screen churn (idle-animation cycles / likely palette-style redraw) using a
before/after capture diff, even with a stability baseline that successfully
isolated the *attacker's own* sprite. The 2026-09-26 09:55 operator decision
switches the target to an owner1 *building* (unit_type 46, a 3x3-tile,
mostly static structure already confirmed legal to spawn via the same op5
fixture protocol and already known combat-domain-eligible, i.e.
``+0x1BC==1``) instead of a mobile unit: a building's sprite is far larger
and does not walk/idle-cycle, so its diff footprint should be both bigger
(easier to size-filter past ambient noise) and steadier (no locomotion
animation of its own to confuse the stability baseline).

As instructed, the attacker/building pairing's engine-level legality is
checked first via the unmodified order issuer (bridge op=8) on an isolated,
off-camera fixture pair, before any UI click is attempted on the on-camera
pair. The UI step tries a plain right-click on the building's diff centroid
first (a right-click landing on an enemy sprite is the conventional stock
RTS "attack" affordance, distinct from a right-click landing on open ground,
which lap667 already showed just issues a move); a 'A'+left-click fallback
at the same points is also recorded in case the engine requires explicit
attack-mode entry even against a building.

Read-only investigation: no product EXE bytes are changed here.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, cast

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
    STOCK_SELECTION_BASE,
    STOCK_SELECTION_CAPACITY,
    SEED_TYPE,
    VISIBLE_WORKER_SLOT,
    selection_snapshot,
    unit_snapshot,
    sha256,
    write_json,
    capture,
    send_key,
)
from tools.g5_screen_world_calibration import op8_attack_order
from tools.g5_type2_ui_attack_diff_probe import (
    STABILITY_GAP_S,
    read_unit_slim,
    sprite_diff_centroid,
)

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE

# unit_type 46: 3x3-tile Joseon production building, already confirmed
# op5/op6-fixture-legal and combat-domain-eligible (+0x1BC==1) by prior G2
# work (analysis/memory_maps/g2_unit_attack_domain_flags_1d8_lap525.md).
BUILDING_TYPE = 46

# Phase A pair: isolated at the far side of the map, well outside the
# camera viewport the minimap click centers on the worker, matching
# lap673's isolation strategy so it never contributes a pixel to a phase B
# capture and its op8 call cannot leak into the click-path attacker's state.
PHASE_A_ATTACKER_WORLD = (172, 172)
PHASE_A_BUILDING_WORLD = (175, 172)

# Phase B pair: same worker-relative attacker anchor as lap666-673. The
# building is placed a little farther out than lap673's mobile-unit offset
# to keep its 3x3 footprint clear of the attacker's own tile and outside
# whatever the engine's aggro/engagement radius is.
ATTACKER_OFFSET_FROM_WORKER = (2, 2)
TARGET_OFFSET_FROM_ATTACKER = (7, -3)
DIFF_ROI = (0, 0, 1600, 480)
DIFF_THRESHOLD = 30
# A 3x3-tile building's screen footprint is far larger than one unit
# sprite; widen the accepted blob-size band accordingly.
MIN_BUILDING_BLOB_PIXELS = 200
MAX_BUILDING_BLOB_PIXELS = 30000
RETRY_OFFSETS = [(0, 0), (10, 0), (-10, 0), (0, 10), (0, -10), (10, 10), (-10, -10), (10, -10), (-10, 10)]


def candidate_click_points(centroid: tuple[int, int]) -> list[tuple[int, int]]:
    seen: set[tuple[int, int]] = set()
    points: list[tuple[int, int]] = []
    for dx, dy in RETRY_OFFSETS:
        point = (centroid[0] + dx, centroid[1] + dy)
        if point in seen:
            continue
        if not (0 <= point[0] <= 1580 and 0 <= point[1] <= 460):
            continue
        seen.add(point)
        points.append(point)
    return points


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    source_exe = source / runtime_env.ORIGINAL_EXE
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    bridge_dir = artifact_root / "stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(__import__("os").environ, PYTHONPATH=str(REPO)),
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
        "schema": "syw2plus.g5-building-attack-diff-probe.v1",
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
    import os
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
        state_ps3 = wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")
        result["tick_at_game_start"] = state_ps3.get("tick")

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        result["worker"] = worker
        supply = SupplyProbe(prefix)

        # --- Phase A: op8 ground truth that a type2 attacker can legally
        # attack a type46 building target, isolated far from the camera.
        phase_a_attacker_receipt = supply.call(
            op=5, owner=0, unit_type=SEED_TYPE,
            x=PHASE_A_ATTACKER_WORLD[0], y=PHASE_A_ATTACKER_WORLD[1], count=1,
        )
        if not phase_a_attacker_receipt.get("ok") or phase_a_attacker_receipt.get("fixture_added") != 1:
            raise ProbeError(f"phase A attacker fixture failed: {phase_a_attacker_receipt}")
        phase_a_attacker_slot = int(phase_a_attacker_receipt.get("producer", {}).get("slot", 0))
        phase_a_building_receipt = supply.call(
            op=5, owner=1, unit_type=BUILDING_TYPE,
            x=PHASE_A_BUILDING_WORLD[0], y=PHASE_A_BUILDING_WORLD[1], count=1,
        )
        if not phase_a_building_receipt.get("ok") or phase_a_building_receipt.get("fixture_added") != 1:
            raise ProbeError(f"phase A building fixture failed: {phase_a_building_receipt}")
        phase_a_building_slot = int(phase_a_building_receipt.get("producer", {}).get("slot", 0))
        phase_a_building_base = UNIT_BASE + phase_a_building_slot * UNIT_STRIDE
        phase_a_building_handle = int.from_bytes(read_memory(pid, phase_a_building_base + 0x29C, 4), "little")
        tick_before_op8 = read_state(pid).get("tick")
        phase_a_op8 = op8_attack_order(supply, owner=0, src_slot=phase_a_attacker_slot, tgt_slot=phase_a_building_slot)
        phase_a_post_unit = read_unit_slim(pid, phase_a_attacker_slot)
        result["phase_a_building_domain_op8"] = {
            "attacker_slot": phase_a_attacker_slot,
            "building_slot": phase_a_building_slot,
            "building_handle": phase_a_building_handle,
            "tick_before_call": tick_before_op8,
            "order_result": phase_a_op8,
            "post_unit_state": phase_a_post_unit,
            "order_accepted": bool(phase_a_op8.get("ok")) and phase_a_op8.get("raw_return") == 1,
            "target_uid_matches": phase_a_post_unit["pending_target_uid"] == phase_a_building_handle,
        }
        if not result["phase_a_building_domain_op8"]["order_accepted"]:
            # The 09:55 operator instruction requires this live confirmation
            # before any UI click is attempted; fail closed rather than
            # spend a UI click sweep on a pairing the engine itself rejects.
            result["status"] = "BLOCKED_BUILDING_DOMAIN_REJECTED"
            result["captures"] = []
            raise ProbeError(
                f"engine rejected type2->type46 attack order: {result['phase_a_building_domain_op8']}"
            )

        # --- Phase B: diff-based building hit-test, spawned near the worker.
        click(235, 555)
        time.sleep(1)
        result["captures"] = [capture(display, artifact_root / "before-attacker-1.png", log)]
        time.sleep(STABILITY_GAP_S)
        result["captures"].append(capture(display, artifact_root / "before-attacker-2.png", log))

        attacker_world = (int(worker["x"]) + ATTACKER_OFFSET_FROM_WORKER[0],
                           int(worker["y"]) + ATTACKER_OFFSET_FROM_WORKER[1])
        building_world = (attacker_world[0] + TARGET_OFFSET_FROM_ATTACKER[0],
                           attacker_world[1] + TARGET_OFFSET_FROM_ATTACKER[1])
        for label, world in (("attacker", attacker_world), ("building", building_world)):
            if any(not 0 <= value < 180 for value in world):
                raise ProbeError(f"{label} world position falls outside the map: {world}")

        attacker_receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE,
                                        x=attacker_world[0], y=attacker_world[1], count=1)
        if not attacker_receipt.get("ok") or attacker_receipt.get("fixture_added") != 1:
            raise ProbeError(f"type2 attacker fixture failed: {attacker_receipt}")
        attacker_slot = int(attacker_receipt.get("producer", {}).get("slot", 0))
        attacker_base = UNIT_BASE + attacker_slot * UNIT_STRIDE
        attacker_handle = int.from_bytes(read_memory(pid, attacker_base + 0x29C, 4), "little")
        result["attacker_fixture"] = {
            "requested_world": list(attacker_world), "slot": attacker_slot,
            "handle": attacker_handle, "receipt": attacker_receipt,
        }
        time.sleep(0.3)
        result["captures"].append(capture(display, artifact_root / "after-attacker.png", log))
        result["attacker_diff"] = sprite_diff_centroid(
            artifact_root / "before-attacker-2.png", artifact_root / "after-attacker.png",
            stability_reference_path=artifact_root / "before-attacker-1.png",
        )

        time.sleep(STABILITY_GAP_S)
        result["captures"].append(capture(display, artifact_root / "before-building-2.png", log))
        building_receipt = supply.call(op=5, owner=1, unit_type=BUILDING_TYPE,
                                        x=building_world[0], y=building_world[1], count=1)
        if not building_receipt.get("ok") or building_receipt.get("fixture_added") != 1:
            raise ProbeError(f"type46 building fixture failed: {building_receipt}")
        building_slot = int(building_receipt.get("producer", {}).get("slot", 0))
        building_base = UNIT_BASE + building_slot * UNIT_STRIDE
        building_handle = int.from_bytes(read_memory(pid, building_base + 0x29C, 4), "little")
        result["building_fixture"] = {
            "requested_world": list(building_world), "slot": building_slot,
            "handle": building_handle, "receipt": building_receipt,
        }
        # Before any click/drag touches either fixture: if the attacker is
        # already locked onto the building's exact handle here, that is
        # autonomous AI aggro, not the click path under test.
        result["attacker_state_immediately_after_spawn"] = read_unit_slim(pid, attacker_slot)
        time.sleep(0.3)
        result["captures"].append(capture(display, artifact_root / "after-building.png", log))
        building_diff = sprite_diff_centroid(
            artifact_root / "before-building-2.png", artifact_root / "after-building.png",
            stability_reference_path=artifact_root / "after-attacker.png",
            min_blob_pixels=MIN_BUILDING_BLOB_PIXELS, max_blob_pixels=MAX_BUILDING_BLOB_PIXELS,
        )
        result["building_diff"] = building_diff
        if building_diff["pixel_count"] == 0:
            raise ProbeError("no new sprite pixels detected after seeding the building")
        centroid = cast(tuple[int, int], tuple(building_diff["centroid"]))

        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        attacker_selection = selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        result["attacker_selection"] = attacker_selection
        result["captures"].append(capture(display, artifact_root / "after-attacker-select.png", log))
        if attacker_slot not in attacker_selection["slots"]:
            raise ProbeError(f"type2 attacker slot not selected via UI drag: {attacker_selection}")

        auto_aggro_before_input = (
            result["attacker_state_immediately_after_spawn"]["pending_target_uid"] == building_handle
        )
        result["auto_aggro_before_input"] = auto_aggro_before_input

        right_click_attempts: list[dict[str, Any]] = []
        attack_key_attempts: list[dict[str, Any]] = []
        click_hit: dict[str, Any] | None = None
        if not auto_aggro_before_input:
            # Try a plain right-click on the sprite first (stock RTS
            # convention: right-clicking an enemy unit/building issues an
            # attack directly, whereas right-clicking open ground issues a
            # move -- lap667 already showed the latter with a missed click).
            for point in candidate_click_points(centroid):
                idle_deadline = time.monotonic() + 10
                while time.monotonic() < idle_deadline and read_unit_slim(pid, attacker_slot)["command"] != 1:
                    time.sleep(0.2)
                waited_idle = read_unit_slim(pid, attacker_slot)["command"] == 1
                click(*point, button=3)
                time.sleep(0.05)
                immediate = read_unit_slim(pid, attacker_slot)
                time.sleep(0.3)
                after_click = read_unit_slim(pid, attacker_slot)
                hit = immediate["pending_target_uid"] == building_handle or after_click["pending_target_uid"] == building_handle
                entry = {
                    "screen": list(point), "waited_idle": waited_idle,
                    "immediate": immediate, "after": after_click, "target_uid_matches": hit,
                }
                right_click_attempts.append(entry)
                if hit:
                    click_hit = {**entry, "input": "right_click"}
                    result["captures"].append(capture(display, artifact_root / f"hit-rc-{point[0]}-{point[1]}.png", log))
                    break
            if click_hit is None:
                # Fallback: explicit attack-mode entry ('A') + left-click,
                # in case the engine requires it even against a building.
                for point in candidate_click_points(centroid):
                    idle_deadline = time.monotonic() + 10
                    while time.monotonic() < idle_deadline and read_unit_slim(pid, attacker_slot)["command"] != 1:
                        time.sleep(0.2)
                    waited_idle = read_unit_slim(pid, attacker_slot)["command"] == 1
                    send_key(display, "a", env=env, log=log)
                    click(*point, button=1)
                    time.sleep(0.05)
                    immediate = read_unit_slim(pid, attacker_slot)
                    time.sleep(0.3)
                    after_click = read_unit_slim(pid, attacker_slot)
                    hit = immediate["pending_target_uid"] == building_handle or after_click["pending_target_uid"] == building_handle
                    entry = {
                        "screen": list(point), "waited_idle": waited_idle,
                        "immediate": immediate, "after": after_click, "target_uid_matches": hit,
                    }
                    attack_key_attempts.append(entry)
                    if hit:
                        click_hit = {**entry, "input": "a_plus_left_click"}
                        result["captures"].append(capture(display, artifact_root / f"hit-a-{point[0]}-{point[1]}.png", log))
                        break
        result["right_click_attempts"] = right_click_attempts
        result["attack_key_attempts"] = attack_key_attempts
        result["click_hit"] = click_hit
        result["captures"].append(capture(display, artifact_root / "after-click-attempts.png", log))

        if auto_aggro_before_input:
            result["status"] = "INCONCLUSIVE_AUTO_AGGRO"
        elif click_hit is not None:
            result["status"] = "PASS_BUILDING_UI_ATTACK_DIFF"
        else:
            result["status"] = "FAIL_BUILDING_UI_ATTACK_DIFF"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError) as exc:
        if result["status"] == "UNKNOWN":
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
        cur_env = locals().get("env", __import__("os").environ)
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
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "").startswith("PASS") and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
