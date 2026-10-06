#!/usr/bin/env python3
"""Fresh paired Phase-D save/load probe for the ESL2608 G2 executables.

The probe keeps the pinned lane executables and the protected old save read-only.
Each case owns a private game copy, Wine prefix, and Xvfb display.  It first
round-trips a save made by the running build, then replaces that slot with the
protected stock ``save000.dat`` and measures the legacy-load path separately.
The baseline is not required to emit the candidate-only ``N4K8`` marker.
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

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from patches.population.g2_esl2608_runtime_layout import from_build_report  # noqa: E402
from patches.population.runtime_driver import read as read_memory  # noqa: E402
from patches.population.runtime_driver import state as read_state  # noqa: E402
from tools import runtime_env  # noqa: E402
from tools.g2_esl2608_phase_c_production_probe import (  # noqa: E402
    BASE_SOURCE,
    EXPECTED_BASELINE,
    EXPECTED_CANDIDATE,
    LANES,
    build_candidate,
    _copy_overlay,
    _owner_units,
    _wait,
)
from tools.g5_candidate_drag_probe import (  # noqa: E402
    PAUSE_LOAD_POINT, PAUSE_SAVE_POINT, RESUME_POINT, SAVE_ACTION_POINT,
    SAVE_MENU_RETURN_POINT, SAVE_SLOT_POINT, ProbeError, send_key, sha256, write_json,
)

OLD_SAVE = REPO.parent / "Syw2plus" / "save" / "save000.dat"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _unit_signature(pid: int, *, candidate: bool) -> list[dict[str, int]]:
    return [
        {
            key: int(row[key])
            for key in ("slot", "type", "owner", "internal_id", "x", "y")
        }
        for row in _owner_units(pid, candidate=candidate)
    ]


def _marker(save_path: Path, marker: bytes) -> dict[str, Any]:
    raw = save_path.read_bytes()
    return {
        "sha256": _digest(raw),
        "size": len(raw),
        "marker": marker.decode("ascii"),
        "marker_present": marker in raw,
        "marker_offset": raw.find(marker),
    }


def _load_status(game_proc: subprocess.Popen[Any], pid: int, wait: Any) -> dict[str, Any]:
    crashed = game_proc.poll() is not None
    timed_out = False
    error: str | None = None
    if not crashed:
        try:
            wait(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0,
                 "load_complete", 90)
        except ProbeError as exc:
            timed_out = True
            error = str(exc)
    if game_proc.poll() is not None:
        crashed = True
    state: dict[str, Any] = {}
    if not crashed:
        try:
            state = read_state(pid)
        except (OSError, ValueError) as exc:
            crashed = True
            error = f"{type(exc).__name__}: {exc}"
    return {
        "status": "CRASHED" if crashed else "TIMEOUT" if timed_out else "PASS",
        "crashed": crashed,
        "timed_out": timed_out,
        "error": error,
        "state": state,
    }


def run_probe(lane: str, variant: str, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if lane not in LANES or variant not in {"baseline", "candidate"}:
        raise ProbeError(f"unsupported lane/variant: {lane}/{variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    if not OLD_SAVE.is_file():
        raise ProbeError(f"protected old save is missing: {OLD_SAVE}")
    runtime_root = runtime_root.resolve()
    artifact_root = artifact_root.resolve()
    artifact_root.mkdir(parents=True)
    baseline_path = LANES[lane]
    baseline = baseline_path.read_bytes()
    baseline_sha = _digest(baseline)
    if baseline_sha != EXPECTED_BASELINE[lane]:
        raise ProbeError(f"baseline SHA mismatch: {baseline_sha}")
    candidate, build_report = build_candidate(baseline)
    candidate_sha = _digest(candidate)
    if candidate_sha != EXPECTED_CANDIDATE[lane]:
        raise ProbeError(f"candidate SHA mismatch: {candidate_sha}")
    layout = from_build_report(build_report["pool"])
    bridge_dir = artifact_root / "bridge"
    bridge_args = [
        sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
        "--out-dir", str(bridge_dir), "--unit-pool-capacity",
        "4093" if variant == "candidate" else "1200",
    ]
    if variant == "candidate":
        bridge_args += ["--unit-pool-base", hex(layout.unit_pool_base)]
    subprocess.run(bridge_args, cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    output = cast(Mapping[str, Any], manifest["output"])
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("private source copy SHA mismatch before ESL2608 install")
    overlay = _copy_overlay(game)
    private_exe.write_bytes(baseline if variant == "baseline" else candidate)
    expected_private = baseline_sha if variant == "baseline" else candidate_sha
    if sha256(private_exe) != expected_private:
        raise ProbeError("private ESL2608 executable SHA mismatch after install")

    result: dict[str, Any] = {
        "schema": "syw2plus.g2-esl2608-phase-d-saveload.v1",
        "lane": lane, "variant": variant, "status": "UNKNOWN",
        "fixture": {
            "synthetic": False, "old_save_path": str(OLD_SAVE),
            "old_save_sha256": sha256(OLD_SAVE), "old_save_size": OLD_SAVE.stat().st_size,
            "private_exe_sha256": expected_private,
        },
        "provenance": {
            "baseline_path": str(baseline_path), "baseline_sha256": baseline_sha,
            "candidate_sha256": candidate_sha, "private_run_dir": str(output["run_dir"]),
            "private_game": str(game), "private_prefix": str(prefix),
            "overlay_files": overlay, "bridge_sha256": sha256(bridge),
            "build_report": build_report,
        },
        "own_roundtrip": {}, "old_save_load": {}, "cleanup": {}, "inputs": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    game_proc: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
               SYW2_SUPPLY_PROBE="1")
    try:
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env,
                                     stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def wait(predicate: Any, label: str, timeout: float = 45) -> dict[str, Any]:
            return _wait(pid, predicate, label, timeout)

        def click(x: int, y: int) -> None:
            tree = runtime_env._window_tree(display, 10)
            outer, content = runtime_env._game_window_ids(tree)
            if content is None:
                raise ProbeError("game content window not found")
            info = runtime_env._xwininfo_details(display, content, 10)
            origin = (int(info["x"]), int(info["y"]))
            subprocess.run([
                sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                str(origin[0] + x), str(origin[1] + y), "--button", "1",
            ], env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y})

        wait(lambda item: item.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log,
                       timeout=10, check=True)
        click(184, 560)
        wait(lambda item: item.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        wait(lambda item: item.get("ps") == 5, "ps5")
        wait(lambda item: item.get("ps") == 5 and
             runtime_env._read_local_ready_state(
                 lambda address, size: read_memory(pid, address, size)
             ).get("ready_value") == 1, "ready", 15)
        click(608, 564)
        wait(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")
        time.sleep(0.4)

        save_path = game / "save" / "save001.dat"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        own_before = _unit_signature(pid, candidate=variant == "candidate")
        result["own_roundtrip"]["before_save"] = {"tick": read_state(pid).get("tick"),
                                                    "units": own_before}
        # Pause menu: save slot 1, save, resume.
        send_key(display, "Escape", env=env, log=log)
        wait(lambda item: item.get("ps") == 23, "pause_for_save")
        click(*PAUSE_SAVE_POINT)
        time.sleep(0.4)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        time.sleep(0.8)
        if not save_path.is_file():
            raise ProbeError("own save was not created")
        result["own_roundtrip"]["save"] = _marker(save_path, b"N4K8")
        click(*SAVE_MENU_RETURN_POINT)
        click(*RESUME_POINT)
        wait(lambda item: item.get("ps") == 3, "resume_after_save")
        send_key(display, "Escape", env=env, log=log)
        wait(lambda item: item.get("ps") == 23, "pause_for_own_load")
        click(*PAUSE_LOAD_POINT)
        time.sleep(0.4)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        own_load = _load_status(game_proc, pid, wait)
        own_after = _unit_signature(pid, candidate=variant == "candidate") if own_load["status"] == "PASS" else []
        result["own_roundtrip"]["load"] = own_load
        result["own_roundtrip"]["after_load"] = {"units": own_after}
        result["own_roundtrip"]["pass"] = (
            own_load["status"] == "PASS" and own_after == own_before
        )

        # Replace slot 1 with the protected stock save and measure that path.
        shutil.copy2(OLD_SAVE, save_path)
        result["old_save_load"]["seed"] = _marker(save_path, b"N4K8")
        send_key(display, "Escape", env=env, log=log)
        wait(lambda item: item.get("ps") == 23, "pause_for_old_load")
        click(*PAUSE_LOAD_POINT)
        time.sleep(0.4)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        old_load = _load_status(game_proc, pid, wait)
        result["old_save_load"]["load"] = old_load
        result["old_save_load"]["pass"] = old_load["status"] == "PASS"
        result["status"] = "PASS" if result["own_roundtrip"]["pass"] and (
            variant == "baseline" or result["old_save_load"]["pass"]
        ) else "FAIL"
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
        result["game_exit_code_before_cleanup"] = None if game_proc is None else game_proc.poll()
        result["cleanup"] = {
            "prefix_processes_after": runtime_env._prefix_pids(prefix),
            "game_removed": False,
        }
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
                      "variant": args.variant, "own_roundtrip": result.get("own_roundtrip", {}).get("pass"),
                      "old_save_load": result.get("old_save_load", {}).get("pass"),
                      "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
