#!/usr/bin/env python3
"""G7 H-G7o observation probe: local player index across pause save, in-game load and title load.

Per run (one private game copy, Wine prefix and Xvfb; ``orig`` = protected original, ``port`` = G2+G5 port):

A  start a solo game at seat ``--seat`` (``lobby-snapshot``: the game's own 0x4B7700 refresh recomputes local)
B  pause menu save (save001.dat copied to the artifact root)
C  pause menu load in the same process (control: the local index is still set)
D  stop the game, start a new process on the same copy, title screen load of that save

Each stage records ``[0xB63FC4]``, the lobby table 0x632C9C..0x632F80, the own id ``[0xC0D11C]``, live units per
owner, a 30 s ps/local watch, and a whole-viewport drag selection with the owners of the selected units.
Observation only for ``orig``/``port``: no product patch, no direct local/owner write after the lobby snapshot.

H-G7r variants: ``cand`` = port + ``g7_title_load_seat_restore``, ``cand67`` = port + G6 + G7 (R4b), ``cand-r5`` = port + G6 +
``g7_save_trailer_local_restore`` (H-G7s).  ``--overwrite-snapshot`` (diagnostic, ``observe`` only) writes the pre-seat
lobby table over the ``0x632F7C`` snapshot just before the pause menu save (the user-failure model, W-1).  ``--seat 0`` keeps the
default solo seat (no lobby snapshot; 1P regression).  ``--existing-save PATH`` skips A-C and title-loads a save made
earlier (R-4: a save written by the unpatched port).
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
from typing import Any, Callable, Mapping, Sequence, cast

from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from patches.population.runtime_driver import write as write_memory
from tools import runtime_env
from tools.g1_saved_scene_probe import LOAD_CONFIRM, LOAD_MENU
from tools.g2_esl2608_phase_a_shift_probe import BASE_SOURCE, copy_overlay
from tools.g2_esl2608_phase_d_saveload_probe import _load_status
from tools.g5_candidate_drag_probe import (
    PAUSE_LOAD_POINT, PAUSE_SAVE_POINT, RESUME_POINT, SAVE_ACTION_POINT, SAVE_MENU_RETURN_POINT,
    SAVE_SLOT_POINT, ProbeError, capture, send_key, sha256, write_json,
)
from patches.selection import g6_shift_click_count_bound as g6_patch
from patches.selection import g7_save_trailer_local_restore as g7r5_patch
from patches.selection import g7_title_load_seat_restore as g7_patch
from tools.g6_shift_click_probe import (
    LAYOUTS as G6_LAYOUTS, LOBBY_DUMP_END, LOBBY_ID_OFFSET, LOBBY_OWN_ID_VA, LOBBY_REFRESH_FLAG_VA,
    LOBBY_SNAPSHOT_VA, LOBBY_TABLE_SIZE, LOBBY_TABLE_VA, LOCAL_INDEX_VA, PORT_EXE, STOCK, _u,
    build_lobby_snapshot, selection_snapshot, unit_row,
)
from tools.s1_load_evidence import SELECTED_INDEX_ADDRESS

REPO = Path(__file__).resolve().parents[1]
SAVE_NAME = "save001.dat"
LEFT_GAME_PS = 27  # lap977: local index not in the participant table -> "left the game" message
WATCH_SECONDS = 30.0
VIEWPORT_DRAG = ((20, 50), (790, 465))
SOLO_FLAG_VA = 0x4ED848  # word, 1 in solo games; the G7 cave restores the lobby table only when it is 1
VARIANTS = ("orig", "port", "cand", "cand67", "cand-r5")
SNAPSHOT_VA = 0x632F7C  # the game-start copy of the live lobby table (0x170 bytes) the R4b recompute read
PORT_EXES = {
    "normal": PORT_EXE,
    "fixed_start": PORT_EXE.parent / (
        "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092_G5_선택50_시험용.exe"
    ),
}
EXPECTED_SEAT = {"S0": 0, "S2": 2}  # save fixture name -> seat the save was made at
LAYOUTS = {"orig": G6_LAYOUTS["orig"], "port": G6_LAYOUTS["port"]}


def layout_key(variant: str) -> str:
    """The G6 probe helpers know only ``orig`` and ``port`` memory layouts; the candidates share the port's."""
    return "orig" if variant == "orig" else "port"


def _install(variant: str, port: str = "normal") -> tuple[bytes | None, dict[str, Any]]:
    """EXE bytes to install (None keeps the private original copy) and the build report."""
    if variant == "orig":
        return None, {"sha256": sha256(STOCK)}
    if port not in PORT_EXES:
        raise ProbeError(f"unsupported port: {port}")
    if sha256(PORT_EXES[port]) != g6_patch.PORT_SHA256[port]:
        raise ProbeError("port EXE SHA mismatch")
    port_bytes = PORT_EXES[port].read_bytes()
    if variant == "port":
        return port_bytes, {"sha256": g6_patch.PORT_SHA256[port]}
    if variant == "cand-r5":  # H-G7s: port + G6 + R5 save trailer (R4b is not applied)
        return g7r5_patch.build_candidate(g6_patch.build_candidate(port_bytes)[0])
    base = g6_patch.build_candidate(port_bytes)[0] if variant == "cand67" else port_bytes
    return g7_patch.build_candidate(base)


def first_match_index(ids: Sequence[int], own: int) -> int | None:
    """What ``0x43AF40`` returns: the first slot whose id equals the own id."""
    return next((i for i, value in enumerate(ids) if value == own), None)


def classify_repair(ids: Sequence[int], own: int, seat: int) -> str:
    """R1 = recomputing from the loaded table yields the saved seat; otherwise R2 (store the local in the save)."""
    return "R1" if first_match_index(ids, own) == seat else "R2"


def title_list_index(name: str) -> int:
    """Title load list row of ``saveNNN.dat`` (save000 -> 1, save006 -> 7 per ``tools/s1_load_evidence.py``)."""
    return int(name[4:7]) + 1


def owner_tally(rows: Sequence[Mapping[str, int]]) -> dict[int, int]:
    tally: dict[int, int] = {}
    for row in rows:
        if row["hp"] > 0:
            tally[row["owner"]] = tally.get(row["owner"], 0) + 1
    return tally


def defect_reproduced(*, local: int, seat: int, ps_seen: Sequence[int], selected_owners: Sequence[int],
                      owner_units: int) -> bool:
    """G7 symptom after a load: local fell back to 0 for a saved seat != 0 and the game shows it."""
    if local != 0 or seat == 0:
        return False
    return (LEFT_GAME_PS in ps_seen or 0 in selected_owners
            or (owner_units > 0 and seat not in selected_owners))


def repair_verdict(*, local: int, seat: int, ps_seen: Sequence[int], selected_owners: Sequence[int]) -> dict[str, bool]:
    """H-G7r R-1/R-3/R-4: local is the saved seat, no "left the game" ps, and a drag selects only the seat's units."""
    verdict = {"local_is_seat": local == seat, "ps_clean": list(ps_seen) == [3],
               "selection_owned": bool(selected_owners) and all(owner == seat for owner in selected_owners)}
    verdict["repaired"] = all(verdict.values())
    return verdict


def parse_actions(text: str) -> list[str]:
    """``ingame:S0,title:S2,pause-shot`` -> validated action list (names must be known fixture names)."""
    actions = [item.strip() for item in text.split(",") if item.strip()]
    for action in actions:
        kind, _, name = action.partition(":")
        if kind == "pause-shot" and not name:
            continue
        if kind not in ("ingame", "title") or name not in EXPECTED_SEAT:
            raise ProbeError(f"bad action: {action}")
    return actions


def parse_clicks(text: str) -> list[tuple[int, int]]:
    """``400,306;400,300`` -> [(400, 306), (400, 300)]."""
    points: list[tuple[int, int]] = []
    for item in text.split(";"):
        if item.strip():
            x, y = item.split(",")
            points.append((int(x), int(y)))
    return points


def run_probe(variant: str, seat: int, runtime_root: Path, artifact_root: Path, *,
              watch_seconds: float = WATCH_SECONDS, existing_save: Path | None = None,
              scenario: str = "observe", actions: Sequence[str] = (), saves: Mapping[str, Path] | None = None,
              exit_clicks: Sequence[tuple[int, int]] = (), port: str = "normal",
              overwrite_snapshot: bool = False) -> dict[str, Any]:
    if variant not in VARIANTS:
        raise ProbeError(f"unsupported variant: {variant}")
    if not 0 <= seat < 8:
        raise ProbeError("seat must be 0..7")
    if scenario not in ("observe", "x"):
        raise ProbeError(f"unsupported scenario: {scenario}")
    if overwrite_snapshot and (scenario != "observe" or existing_save is not None):
        raise ProbeError("--overwrite-snapshot needs the observe scenario without --existing-save")
    if scenario == "x" and (existing_save is not None or not actions):
        raise ProbeError("scenario x needs actions and no --existing-save")
    for name, path in (saves or {}).items():
        if name not in EXPECTED_SEAT or not path.is_file():
            raise ProbeError(f"bad save fixture {name}: {path}")
    if existing_save is not None and not existing_save.is_file():
        raise ProbeError(f"existing save not found: {existing_save}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    lay = layout_key(variant)
    _sel, _cap, pool_base, exists_base, pool_cap = LAYOUTS[lay]
    exe_bytes, build_report = _install(variant, port)
    bridge_dir = artifact_root / "bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", str(pool_cap),
                    *(["--unit-pool-base", hex(pool_base)] if lay != "orig" else [])],
                   cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("private source copy SHA mismatch before install")
    overlay = copy_overlay(game) if lay != "orig" else []
    if exe_bytes is not None:
        private_exe.write_bytes(exe_bytes)
    result: dict[str, Any] = {
        "schema": "syw2plus.g7-save-load-probe.v1", "status": "UNKNOWN", "variant": variant, "seat": seat,
        "port": port,
        "provenance": {"private_exe_sha256": sha256(private_exe), "private_game": str(game),
                        "private_prefix": str(prefix), "overlay_files": len(overlay),
                        "bridge_sha256": sha256(bridge), "build_report": build_report},
        "stages": {}, "checks": {}, "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    display = ""
    env: dict[str, str] = dict(os.environ)
    shots = artifact_root / "shots"
    shots.mkdir()
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        proc: dict[str, Any] = {}

        def launch() -> None:
            """Start explorer + game, wait for the title (ps9), locate the content window."""
            explorer = subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game, env=env,
                                        stdout=log, stderr=log)
            time.sleep(1)
            game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
            children.extend([explorer, game_proc])
            proc.update(game=game_proc, pid=game_proc.pid)
            wait_for(lambda s: s.get("ps") == 9, "ps9")
            outer, content = runtime_env._game_window_ids(runtime_env._window_tree(display, 10))
            if content is None:
                raise ProbeError("game content window not found")
            info = runtime_env._xwininfo_details(display, content, 10)
            proc.update(origin=(int(info["x"]), int(info["y"])))
            subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)

        def stop_game() -> None:
            for child in children:
                if child.poll() is None:
                    child.terminate()
            for child in children:
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
            children.clear()
            kill_env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
            subprocess.run(["wineserver", "-k"], env=kill_env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=kill_env, stdout=log, stderr=log, timeout=30, check=False)

        def wait_for(pred: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> None:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = read_state(proc["pid"])
                    if pred(last):
                        return
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None) -> None:
            ox, oy = proc["origin"]
            args = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(ox + x), str(oy + y)]
            if drag_to is not None:
                args += ["--drag-to", str(ox + drag_to[0]), str(oy + drag_to[1])]
            subprocess.run(args, env=env, stdout=log, stderr=log, timeout=10, check=True)

        def shot(label: str) -> None:
            capture(display, shots / f"{time.strftime('%Y%m%d_%H%M%S')}_{label}.png", log)

        def dump(step: str) -> dict[str, Any]:
            pid = proc["pid"]
            raw = read_memory(pid, LOBBY_TABLE_VA, LOBBY_DUMP_END - LOBBY_TABLE_VA)
            ids = [int.from_bytes(raw[LOBBY_ID_OFFSET + 4 * i:LOBBY_ID_OFFSET + 4 * i + 4], "little")
                   for i in range(8)]
            own = _u(pid, LOBBY_OWN_ID_VA, 4)
            rows = [unit_row(pid, lay, slot) for slot in range(1, pool_cap)
                    if _u(pid, exists_base + slot * 2, 2) != 0]
            return {"step": step, "ps": read_state(pid).get("ps"), "local_index": _u(pid, LOCAL_INDEX_VA, 4),
                    "own_id": own, "solo_flag": _u(pid, SOLO_FLAG_VA, 2), "table_ids": ids, "first_match": first_match_index(ids, own),
                    "table_hex": raw.hex(), "table_sha256": hashlib.sha256(raw).hexdigest(),
                    "flag": _u(pid, LOBBY_REFRESH_FLAG_VA, 4), "owner_units": owner_tally(rows)}

        def watch(step: str) -> dict[str, Any]:
            """Sample ps/local for ``watch_seconds`` after a load, then one whole-viewport drag selection."""
            pid = proc["pid"]
            ps_seen: list[int] = []
            locals_seen: set[int] = set()
            t0 = time.monotonic()
            while time.monotonic() - t0 < watch_seconds:
                state = read_state(pid)
                if state.get("ps") not in ps_seen:
                    ps_seen.append(state.get("ps"))
                locals_seen.add(_u(pid, LOCAL_INDEX_VA, 4))
                time.sleep(1)
            shot(f"{step}_watch_end")
            selected_owners: list[int] = []
            selection: dict[str, Any] = {}
            if read_state(pid).get("ps") == 3:
                click(*VIEWPORT_DRAG[0], drag_to=VIEWPORT_DRAG[1])
                time.sleep(0.8)
                selection = selection_snapshot(pid, lay)
                selected_owners = [unit_row(pid, lay, s)["owner"] for s in selection["slots"] if s]
                shot(f"{step}_drag_select")
            end = dump(f"{step}_end")
            return {"ps_seen": ps_seen, "locals_seen": sorted(locals_seen), "selection": selection,
                    "selected_owners": selected_owners, "end": end}

        def game_alive() -> bool:
            return proc["game"].poll() is None

        def start_game() -> dict[str, Any]:
            """Solo lobby -> seat via the game's own refresh (seat != 0) -> in-game ps3; returns the a_start stage."""
            launch()
            pid = proc["pid"]
            click(184, 560)
            wait_for(lambda s: s.get("ps") == 7, "ps7")
            click(462, 169)
            time.sleep(0.5)
            ids = None
            if seat:  # seat 0 = the default solo seat, no snapshot (1P regression)
                before = dump("lobby_before")
                table = bytes.fromhex(before["table_hex"])[:LOBBY_TABLE_SIZE]
                snapshot, ids = build_lobby_snapshot(table, seat, before["own_id"])
                write_memory(pid, LOBBY_SNAPSHOT_VA, snapshot)
                write_memory(pid, LOBBY_REFRESH_FLAG_VA, (1).to_bytes(4, "little"))
                deadline = time.monotonic() + 5
                while _u(pid, LOBBY_REFRESH_FLAG_VA, 4) != 0 and time.monotonic() < deadline:
                    time.sleep(0.1)
                time.sleep(0.5)
            click(608, 564)
            wait_for(lambda s: s.get("ps") == 5, "ps5")
            if _u(pid, LOCAL_INDEX_VA, 4) != seat:
                raise ProbeError(f"seat setup failed: local={_u(pid, LOCAL_INDEX_VA, 4)} wanted {seat}")
            deadline = time.monotonic() + 8
            while read_state(pid).get("ps") not in (2, 3) and time.monotonic() < deadline:
                time.sleep(0.3)
            if read_state(pid).get("ps") not in (2, 3):
                click(608, 564)
            wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")
            time.sleep(6)
            stage = {"lobby_ids": ids, **dump("a_start")}
            if seat:
                proc["lobby_before_table"] = table  # the pre-seat table, kept for --overwrite-snapshot
            shot("a_start")
            return stage


        def run_cross() -> dict[str, Any]:
            """H-G7x: start at ``seat`` once, then run ``actions`` (``ingame:S0``, ``title:S2``, ``pause-shot``) in order.

            ``ingame:NAME`` = pause menu load of save NAME (file copied over save001.dat first); ``title:NAME`` = leave the
            game for the title (``exit_clicks`` after Escape), record the local index there, then title load NAME.
            Each step records the local index before/after and the 30 s watch; expected seat = ``EXPECTED_SEAT[NAME]``.
            """
            out: dict[str, Any] = {"start_seat": seat, "actions": list(actions), "steps": []}
            out["a_start"] = start_game()
            pid = proc["pid"]
            save_path = game / "save" / SAVE_NAME
            save_path.parent.mkdir(parents=True, exist_ok=True)
            for index, action in enumerate(actions):
                kind, _, name = action.partition(":")
                step: dict[str, Any] = {"action": action, "before": dump(f"x{index}_before")}
                if kind == "pause-shot":
                    send_key(display, "Escape", env=env, log=log)
                    wait_for(lambda s: s.get("ps") == 23, "pause_shot")
                    time.sleep(0.5)
                    shot(f"x{index}_pause_menu")
                    out["steps"].append(step)
                    continue
                if name not in (saves or {}):
                    raise ProbeError(f"unknown save name in action: {action}")
                shutil.copy2((saves or {})[name], save_path)
                step["save_sha256"] = sha256(save_path)
                expected = EXPECTED_SEAT[name]
                if kind == "ingame":
                    send_key(display, "Escape", env=env, log=log)
                    wait_for(lambda s: s.get("ps") == 23, "pause_for_load")
                    click(*PAUSE_LOAD_POINT)
                    time.sleep(0.4)
                    click(*SAVE_SLOT_POINT)
                    click(*SAVE_ACTION_POINT)
                    step["load"] = _load_status(proc["game"], pid, wait_for)
                    time.sleep(0.5)
                elif kind == "title":
                    send_key(display, "Escape", env=env, log=log)
                    wait_for(lambda s: s.get("ps") == 23, "pause_for_exit")
                    for point_index, point in enumerate(exit_clicks):
                        click(*point)
                        time.sleep(1.0)
                        shot(f"x{index}_exit_click{point_index}")
                    wait_for(lambda s: s.get("ps") == 9, "title_after_exit", 60)
                    time.sleep(1.0)
                    step["title_return"] = dump(f"x{index}_title_return")
                    shot(f"x{index}_title_return")
                    click(*LOAD_MENU)
                    time.sleep(1.0)
                    if read_state(pid).get("ps") == 9:
                        click(*LOAD_MENU)
                    wait_for(lambda s: s.get("ps") == 35, "ps35")
                    target_row, navigation = title_list_index(SAVE_NAME), []
                    for _ in range(20):
                        current = _u(pid, SELECTED_INDEX_ADDRESS, 2)
                        navigation.append(current)
                        if current == target_row:
                            break
                        subprocess.run([sys.executable, str(REPO / "tools/x11_send_keys.py"), "--display", display,
                                        "DOWN"], env=env, stdout=log, stderr=log, timeout=10, check=True)
                        time.sleep(0.3)
                    else:
                        raise ProbeError(f"title list navigation did not reach {target_row}: {navigation}")
                    click(*LOAD_CONFIRM)
                    wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "title_loaded_ps3", 90)
                    time.sleep(0.5)
                    step["navigation"] = navigation
                else:
                    raise ProbeError(f"unknown action: {action}")
                step["loaded"] = dump(f"x{index}_loaded")
                step["watch"] = watch(f"x{index}")
                step["expected_seat"] = expected
                step["verdict"] = repair_verdict(local=step["loaded"]["local_index"], seat=expected,
                                                 ps_seen=step["watch"]["ps_seen"],
                                                 selected_owners=step["watch"]["selected_owners"])
                out["steps"].append(step)
            out["game_alive"] = game_alive()
            return out


        if existing_save is None and scenario == "observe":
            result["stages"]["a_start"] = start_game()
            pid = proc["pid"]
            # ---- B: pause menu save
            if overwrite_snapshot:
                before_table = proc.get("lobby_before_table")
                if before_table is None:
                    raise ProbeError("--overwrite-snapshot needs --seat != 0 (no pre-seat table)")
                snap_before = read_memory(pid, SNAPSHOT_VA, LOBBY_TABLE_SIZE)
                write_memory(pid, SNAPSHOT_VA, before_table)
                snap_after = read_memory(pid, SNAPSHOT_VA, LOBBY_TABLE_SIZE)
                result["snapshot_overwrite"] = {"before_sha256": hashlib.sha256(snap_before).hexdigest(),
                                                "after_sha256": hashlib.sha256(snap_after).hexdigest(),
                                                "wrote_pre_seat_table": snap_after == before_table,
                                                "was_equal_to_pre_seat_table": snap_before == before_table}
            save_path = game / "save" / SAVE_NAME
            save_path.parent.mkdir(parents=True, exist_ok=True)
            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda s: s.get("ps") == 23, "pause_for_save")
            click(*PAUSE_SAVE_POINT)
            time.sleep(0.4)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            time.sleep(1.0)
            if not save_path.is_file():
                raise ProbeError("save was not created")
            shutil.copy2(save_path, artifact_root / SAVE_NAME)
            result["stages"]["b_save"] = {"size": save_path.stat().st_size, "sha256": sha256(save_path),
                                          **dump("b_save")}
            click(*SAVE_MENU_RETURN_POINT)
            click(*RESUME_POINT)
            wait_for(lambda s: s.get("ps") == 3, "resume_after_save")

            # ---- C: in-game load (control)
            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda s: s.get("ps") == 23, "pause_for_load")
            click(*PAUSE_LOAD_POINT)
            time.sleep(0.4)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            c_load = _load_status(proc["game"], pid, wait_for)
            time.sleep(0.5)
            result["stages"]["c_ingame_load"] = {"load": c_load, **dump("c_loaded")}
            if c_load["status"] == "PASS":
                result["stages"]["c_ingame_load"]["watch"] = watch("c")
            stop_game()

        if scenario == "x":
            result["x"] = run_cross()
        else:
            # ---- D: new process, title screen load of the same save
            launch()
            pid = proc["pid"]
            if existing_save is not None:
                (game / "save").mkdir(parents=True, exist_ok=True)
                shutil.copy2(existing_save, game / "save" / SAVE_NAME)
                result["existing_save"] = {"path": str(existing_save), "sha256": sha256(existing_save)}
            result["stages"]["d_title"] = dump("d_title_before_load")
            click(*LOAD_MENU)
            time.sleep(1.0)
            if read_state(pid).get("ps") == 9:
                click(*LOAD_MENU)
            wait_for(lambda s: s.get("ps") == 35, "ps35")
            target_row, navigation = title_list_index(SAVE_NAME), []
            for _ in range(20):
                current = _u(pid, SELECTED_INDEX_ADDRESS, 2)
                navigation.append(current)
                if current == target_row:
                    break
                subprocess.run([sys.executable, str(REPO / "tools/x11_send_keys.py"), "--display", display, "DOWN"],
                               env=env, stdout=log, stderr=log, timeout=10, check=True)
                time.sleep(0.3)
            else:
                raise ProbeError(f"title list navigation did not reach {target_row}: {navigation}")
            click(*LOAD_CONFIRM)
            wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "title_loaded_ps3", 90)
            time.sleep(0.5)
            result["stages"]["d_title_load"] = {"navigation": navigation, **dump("d_loaded")}
            result["stages"]["d_title_load"]["watch"] = watch("d")

            d = result["stages"]["d_title_load"]
            own = d["own_id"]
            d_watch = d["watch"]
            result["checks"] = {
                "d_local": d["local_index"],
                "d_local_zero": d["local_index"] == 0,
                "d_defect_reproduced": defect_reproduced(
                    local=d["local_index"], seat=seat, ps_seen=d_watch["ps_seen"],
                    selected_owners=d_watch["selected_owners"], owner_units=d["owner_units"].get(seat, 0)),
                "d_first_match": d["first_match"], "d_own_id": own, "d_solo_flag": d["solo_flag"],
                "repair_class": classify_repair(d["table_ids"], own, seat),
                "repair": repair_verdict(local=d["local_index"], seat=seat, ps_seen=d_watch["ps_seen"],
                                         selected_owners=d_watch["selected_owners"]),
                "game_alive": game_alive(),
            }
            if existing_save is None:
                a, c = result["stages"]["a_start"], result["stages"]["c_ingame_load"]
                result["checks"].update({
                    "a_local_is_seat": a["local_index"] == seat,
                    "c_local_kept": c["local_index"] == seat and c.get("watch", {}).get("locals_seen") == [seat],
                    "c_repair": repair_verdict(local=c["local_index"], seat=seat,
                                               ps_seen=c.get("watch", {}).get("ps_seen", []),
                                               selected_owners=c.get("watch", {}).get("selected_owners", [])),
                    "d_table_ids_restored": d["table_ids"] == a["table_ids"],
                })
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
        kill_env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
        subprocess.run(["wineserver", "-k"], env=kill_env, stdout=log, stderr=log, timeout=10, check=False)
        subprocess.run(["wineserver", "-w"], env=kill_env, stdout=log, stderr=log, timeout=10, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=5)
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix)}
        if game.exists():
            shutil.rmtree(game)
        result["cleanup"]["game_removed"] = not game.exists()
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--port", choices=sorted(PORT_EXES), default="normal")
    parser.add_argument("--seat", type=int, default=2)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--watch-seconds", type=float, default=WATCH_SECONDS)
    parser.add_argument("--existing-save", type=Path, default=None)
    parser.add_argument("--overwrite-snapshot", action="store_true",
                        help="W-1 diagnostic: write the pre-seat table over 0x632F7C before the pause save")
    parser.add_argument("--x-actions", default="", help="H-G7x: e.g. ingame:S0 or title:S2,title:S0 (enables scenario x)")
    parser.add_argument("--save", action="append", default=[], metavar="NAME=PATH", help="fixture S0/S2 for scenario x")
    parser.add_argument("--exit-clicks", default="", help="pause-menu clicks that leave for the title, e.g. 400,306;400,300")
    args = parser.parse_args(argv)
    saves = {name: Path(path) for name, _, path in (item.partition("=") for item in args.save)}
    result = run_probe(args.variant, args.seat, args.runtime_root, args.artifact_root,
                       watch_seconds=args.watch_seconds, existing_save=args.existing_save,
                       scenario="x" if args.x_actions else "observe", actions=parse_actions(args.x_actions),
                       saves=saves, exit_clicks=parse_clicks(args.exit_clicks), port=args.port,
                       overwrite_snapshot=args.overwrite_snapshot)
    print(json.dumps({"status": result.get("status"), "variant": args.variant, "seat": args.seat,
                      "checks": result.get("checks"),
                      "x": [(step["action"], step.get("verdict")) for step in result.get("x", {}).get("steps", [])],
                      "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
