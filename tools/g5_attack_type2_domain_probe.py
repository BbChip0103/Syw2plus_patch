#!/usr/bin/env python3
"""Decisive minimal test: does a SEED_TYPE=2 attacker clear the domain gate?

lap671's clean op8 (bridge dispatch, no UI) ground-truth check kept returning
raw_return=0 even with the source unit idle. Static disassembly of
``FUN_00415880`` (the P6 admission gate, matching the already-documented
``analysis/memory_maps/g2_unit_attack_domain_flags_1d8_lap525.md`` N182)
showed the source's own ``+0x1D8`` bit ``0x4`` must be set to attack a
domain-1 target (``+0x1BC==1``). The G5 probe's source was always
``VISIBLE_WORKER_SLOT`` (unit_type 31); its ``+0x1D8`` measured
``0x10001`` in lap671, which does not have bit ``0x4`` set. lap525 already
found type 2 (``SEED_TYPE``, the actual G5 army fixture type) DOES carry
bit ``0x4`` and can attack other type-2 units.

This probe spawns one owner0 SEED_TYPE=2 unit (not the worker) and one
owner1 SEED_TYPE=2 unit, waits for both to be idle, and issues one clean
bridge op=8 order from the type-2 attacker. If ``raw_return==1`` and
``+0x38C`` attributes to the target's handle, the domain-mismatch
hypothesis is confirmed and the fix for G5's attack test is "use a fixture
unit as the attacker, not the pre-existing worker" -- no engine/candidate
change required. Read-only investigation: no product EXE bytes change.
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
from tools.g5_candidate_drag_probe import ProbeError, SupplyProbe, SEED_TYPE, sha256, write_json
from tools.g5_screen_world_calibration import op8_attack_order, read_unit

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE


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
        "schema": "syw2plus.g5-attack-type2-domain-probe.v1",
        "status": "UNKNOWN",
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
            "private_exe_sha256": sha256(private_exe),
            "original_manifest_check": original_check,
            "bridge_sha256": sha256(bridge),
        },
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

        def click(x: int, y: int, *, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(x), str(y), "--button", str(button)]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)

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

        supply = SupplyProbe(prefix)
        attacker_world = (90, 90)
        target_world = (91, 90)
        attacker_receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=attacker_world[0], y=attacker_world[1], count=1)
        if not attacker_receipt.get("ok") or attacker_receipt.get("fixture_added") != 1:
            raise ProbeError(f"attacker fixture failed: {attacker_receipt}")
        target_receipt = supply.call(op=5, owner=1, unit_type=SEED_TYPE, x=target_world[0], y=target_world[1], count=1)
        if not target_receipt.get("ok") or target_receipt.get("fixture_added") != 1:
            raise ProbeError(f"target fixture failed: {target_receipt}")
        attacker_slot = int(attacker_receipt.get("producer", {}).get("slot", 0))
        target_slot = int(target_receipt.get("producer", {}).get("slot", 0))
        target_base = 0x0066B790 + target_slot * 0x758
        target_handle = int.from_bytes(read_memory(pid, target_base + 0x29C, 4), "little")
        result["attacker"] = {"slot": attacker_slot, "world": list(attacker_world), "receipt": attacker_receipt}
        result["target"] = {"slot": target_slot, "handle": target_handle, "world": list(target_world), "receipt": target_receipt}

        idle_deadline = time.monotonic() + 15
        while time.monotonic() < idle_deadline and read_unit(pid, attacker_slot)["command"] != 1:
            time.sleep(0.2)
        pre_unit = read_unit(pid, attacker_slot)
        result["attacker_idle_before_order"] = pre_unit["command"] == 1
        result["pre_unit_state"] = pre_unit

        op8_result = op8_attack_order(supply, owner=0, src_slot=attacker_slot, tgt_slot=target_slot)
        time.sleep(0.3)
        post_unit = read_unit(pid, attacker_slot)
        result["op8_result"] = op8_result
        result["post_unit_state"] = post_unit
        result["target_uid_matches"] = post_unit["pending_target_uid"] == target_handle
        result["raw_return"] = op8_result.get("op8", {}).get("raw_return")
        result["status"] = (
            "PASS_TYPE2_DOMAIN_ATTACK"
            if result["raw_return"] == 1 and result["target_uid_matches"]
            else "FAIL_TYPE2_DOMAIN_ATTACK"
        )
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
