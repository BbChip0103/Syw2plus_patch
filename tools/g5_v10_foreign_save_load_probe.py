#!/usr/bin/env python3
"""Load a save file produced by a *different* build into a fresh instance.

v10 (``patches/selection/g5_selection_cap50_v10.py``) appends a trailing
sidecar to the save stream so a raw >20 drag selection survives save/load in
full. The 2026-09-29 00:59 user judgment held the milestone on exactly this
point being bidirectionally save-compatible: a vanilla original EXE must
still be able to open a v10-written save (no crash, first 20 restored), and
v10 must still be able to open a save the original EXE (or any pre-v10
candidate) wrote (no crash, same known first-20 restore v7..v9 already have).

``tools/g5_stale_tail_probe.py`` only ever exercises a build saving and then
loading *its own* save; this probe instead seeds the isolated copy's save
slot with a save file produced by a *different* run before the game is ever
launched, then does the minimal pause-menu load, so what gets read back is
never anything this same process wrote.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, cast

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from patches.selection import g5_selection_cap50_v10 as v10_module  # noqa: E402
from patches.population.runtime_driver import read as read_memory  # noqa: E402
from patches.population.runtime_driver import state as read_state  # noqa: E402
from tools import runtime_env  # noqa: E402
from tools import g5_candidate_drag_probe as base_probe  # noqa: E402
from tools import g5_stale_tail_probe as stale_probe  # noqa: E402

ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
V10_SHA = "c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad"
STOCK_SELECTION_BASE = base_probe.STOCK_SELECTION_BASE
STOCK_SELECTION_CAPACITY = base_probe.STOCK_SELECTION_CAPACITY
PAUSE_LOAD_POINT = base_probe.PAUSE_LOAD_POINT
SAVE_SLOT_POINT = base_probe.SAVE_SLOT_POINT
SAVE_ACTION_POINT = base_probe.SAVE_ACTION_POINT
full_dump = stale_probe.full_dump
sha256 = base_probe.sha256
write_json = base_probe.write_json
capture = stale_probe.capture
send_key = stale_probe.send_key


class ProbeError(RuntimeError):
    pass


def run(
    source: Path, runtime_root: Path, artifact_root: Path, *, variant: str, seed_save: Path,
) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    seed_save = seed_save.expanduser().resolve()
    if not seed_save.is_file():
        raise ProbeError(f"seed save is not a file: {seed_save}")

    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_bytes: bytes | None = None
    if variant == "candidate":
        candidate_bytes, _report = v10_module.build_candidate(source_exe.read_bytes())
        if __import__("hashlib").sha256(candidate_bytes).hexdigest() != V10_SHA:
            raise ProbeError("v10 candidate SHA mismatch")

    bridge_dir = artifact_root / "stock_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
    )
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge, timeout=60)
    game = Path(cast(str, manifest["game"]["root"]))
    prefix = Path(cast(str, manifest["wine"]["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != ORIGINAL_SHA:
        raise ProbeError("private original copy failed pre-install check")
    if variant == "candidate":
        assert candidate_bytes is not None
        private_exe.write_bytes(candidate_bytes)
        if sha256(private_exe) != V10_SHA:
            raise ProbeError("private candidate SHA verification failed after write")

    save_dir = game / "save"
    save_dir.mkdir(parents=True, exist_ok=True)
    seeded_path = save_dir / "save001.dat"
    shutil.copy2(seed_save, seeded_path)

    base = v10_module.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    capacity = v10_module.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-v10-foreign-save-load-probe.v1",
        "variant": variant,
        "seed_save": {"path": str(seed_save), "sha256": sha256(seed_save), "size": seed_save.stat().st_size},
        "status": "UNKNOWN",
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env: Any = os.environ
    pid: int | None = None
    game_proc: subprocess.Popen[bytes] | None = None
    try:
        env = dict(
            os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
            LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
            SYW2_SUPPLY_PROBE="1",
        )
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game, env=env, stdout=log, stderr=log,
        ))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def state() -> dict[str, Any]:
            assert pid is not None
            return read_state(pid)

        def wait_for(predicate: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = state()
                    if predicate(last):
                        return last
                except (OSError, ValueError):
                    pass
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda item: item.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window was not found")
        content_info = runtime_env._xwininfo_details(display, content, 10)
        crop = (int(content_info["x"]), int(content_info["y"]))

        def click(x: int, y: int, *, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
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

        result["captures"] = [capture(display, artifact_root / "s0-fresh-game.png", log)]
        result["selection_before_load"] = full_dump(pid, base=base, capacity=capacity)

        send_key(display, "Escape", env=env, log=log)
        wait_for(lambda item: item.get("ps") == 23, "pause_for_load")
        click(*PAUSE_LOAD_POINT)
        time.sleep(0.5)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        load_timed_out = False
        try:
            wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "load_complete", 90)
        except ProbeError:
            load_timed_out = True
        time.sleep(0.5)
        result["captures"].append(capture(display, artifact_root / "s1-after-load.png", log))

        crashed = game_proc.poll() is not None
        post_state: dict[str, Any] = {}
        if not crashed:
            try:
                post_state = state()
            except (OSError, ValueError) as exc:
                crashed = True
                post_state = {"error": f"{type(exc).__name__}: {exc}"}
        result["load_timed_out"] = load_timed_out
        result["post_load_state"] = post_state
        result["crashed"] = crashed

        legacy_after_load: dict[str, Any] = {}
        live_after_load: dict[str, Any] = {}
        if not crashed:
            legacy_after_load = full_dump(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
            if variant == "candidate":
                live_after_load = full_dump(pid, base=base, capacity=capacity)
        result["legacy_after_load"] = legacy_after_load
        result["live_after_load"] = live_after_load

        result["status"] = (
            "FOREIGN_LOAD_CRASHED" if crashed
            else "FOREIGN_LOAD_PASS" if not load_timed_out
            else "FOREIGN_LOAD_INCONCLUSIVE_TIMEOUT"
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
        cleanup_error = None
        try:
            subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=env, stdout=log, stderr=log, timeout=10, check=False)
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
    parser.add_argument("--variant", choices=("original", "candidate"), required=True)
    parser.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--seed-save", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run(
        args.source, args.runtime_root, args.artifact_root,
        variant=args.variant, seed_save=args.seed_save,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") == "FOREIGN_LOAD_PASS" and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
