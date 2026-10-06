#!/usr/bin/env python3
"""G5 checklist (F) H-STALE-TAIL runtime probe (lap745 middle handoff, lap746 work).

``docs/history/laps/20260928_lap745_middle_g5_a_h_independent_review_hold_stale_tail.md``
found (statically, unverified at runtime) that v7's ``LOAD_WRAPPER`` only
mirrors the legacy 20-slot save/load window into the relocated selection
array's first 20 entries; ``entries[20:50]`` keep whatever value they held
immediately before the load. This probe exercises that at runtime, paired
against the unpatched original (which only ever has 20 capacity, so its own
run is the "no stale tail possible" baseline):

- S1 (load-time tail): drag-select the full capacity, save *without*
  deselecting, load the same save *without* deselecting first (worst case:
  the live selection still references entries[20:50] when the load wrapper
  runs), then read the full raw entry buffer (not just ``range(count)``) to
  see whether ``count`` still equals the number of non-zero slots. Follow
  with a right-click move and diff every fixture unit's command/pending
  fields to see whether any unit outside the just-loaded ``entries[0:count]``
  window receives a command (the v5 chunk-dispatch gate triggers on any
  non-zero ``entries[20:50]`` slot, independent of ``count``). Then deselect,
  redrag, and save again to check for a crash.
- S2 (save-time tail flags): read unit byte+0 (the presumed per-unit
  selection flag) and the stock ``selectable`` byte for every fixture unit at
  save time and again after load, to see whether the 21st..50th selected
  units keep a "selected" flag the live selection array no longer agrees
  with.
- S3 (best effort, gated behind ``--attempt-menu-exit``): after S1/S2,
  attempt to leave to the main menu with the redrag selection still live and
  start a new game, then read the full raw entry buffer once more. The pause
  menu's "initial menu" button position is inferred from a captured
  screenshot (``20260925_225720_g2_highslot_save_menu_pause.png``) rather
  than an already-exercised harness path, so this step is opportunistic: on
  any unexpected screen it stops, screenshots, and reports
  ``S3_INCONCLUSIVE`` instead of guessing further clicks.
- S4 (best effort, gated behind ``--attempt-restart``, lap748 work, 2026-09-28
  18:35 operator instruction: pause-menu alternate paths since S3's "초기메뉴"
  is environment-blocked even on the unpatched original). Pause-menu row 6
  ("다시하기"/restart) with the live 50-selection still selected: does the
  restarted match inherit any of it? PASS = selection array clean (count==0,
  nonzero_count==0) once a restart is actually observed (tick resets below
  its pre-restart value); any other outcome (dialog closes back into the same
  battlefield, like S3's "초기메뉴" did) is reported ``S4_INCONCLUSIVE``
  rather than guessed.
- S5 (best effort, gated behind ``--attempt-load-different``, same 18:35
  instruction): "불러오기" (load) a save made *before* the dense fixture / any
  selection existed -- a genuinely different game state, not a reload of this
  probe's own S1 save -- while the live 50-selection is still selected. The
  pre-fixture save is captured once near the start of the run and mirrored to
  a host-side backup file so it survives S1/S2 overwriting the same save
  slot; loading it back is a plain filesystem copy over that slot plus the
  existing in-game load click, so it needs no second save-slot UI. PASS =
  selection array clean after the load, and no unit outside the legit
  (post-load, empty) selection receives a stray command from the
  same-target move click that follows.

Every step is read-only diagnostics on top of the existing G5 runtime
harness; no product EXE/original bytes are modified by this probe itself
(only the same isolated candidate-build-and-run pattern every other G5 probe
in this repository already uses).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Mapping, cast

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from patches.selection import g5_selection_cap50_v7 as v7_module  # noqa: E402
from patches.selection import g5_selection_cap50_v8 as v8_module  # noqa: E402
from patches.selection import g5_selection_cap50_v9 as v9_module  # noqa: E402
from patches.selection import g5_selection_cap50_v10 as v10_module  # noqa: E402
from patches.population.runtime_driver import read as read_memory  # noqa: E402
from patches.population.runtime_driver import write as write_memory  # noqa: E402
from patches.population.runtime_driver import state as read_state  # noqa: E402
from tools import runtime_env  # noqa: E402
from tools import g5_candidate_drag_probe as base_probe  # noqa: E402

DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
CANDIDATE_MODULES = {"v7": v7_module, "v8": v8_module, "v9": v9_module, "v10": v10_module}
# Pinned so a build drift (wrong source, stale cache) fails closed instead of
# silently running whatever bytes happened to come out.
CANDIDATE_SHAS = {
    "v7": "30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef",
    "v8": "ef46d1acd55af2f6007824bb416b3c991ae4afb195fb369b3e86b5ee9182ff08",
    "v9": "18181cdef6c787a2be9a3cf78a2851eb4d764074c972e2b13690f27af0fd2017",
    "v10": "c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad",
}

STOCK_SELECTION_BASE = base_probe.STOCK_SELECTION_BASE
STOCK_SELECTION_CAPACITY = base_probe.STOCK_SELECTION_CAPACITY
UNIT_BASE = base_probe.UNIT_BASE
UNIT_STRIDE = base_probe.UNIT_STRIDE
UNIT_COMMAND_OFFSET = base_probe.UNIT_COMMAND_OFFSET
UNIT_PENDING_COMMAND_OFFSET = base_probe.UNIT_PENDING_COMMAND_OFFSET
UNIT_PENDING_XY_OFFSET = base_probe.UNIT_PENDING_XY_OFFSET
UNIT_PENDING_TARGET_UID_OFFSET = base_probe.UNIT_PENDING_TARGET_UID_OFFSET
UNIT_X_OFFSET = base_probe.UNIT_X_OFFSET
UNIT_Y_OFFSET = base_probe.UNIT_Y_OFFSET
UNIT_SELECTABLE_OFFSET = base_probe.UNIT_SELECTABLE_OFFSET
VISIBLE_WORKER_SLOT = base_probe.VISIBLE_WORKER_SLOT
SEED_TYPE = base_probe.SEED_TYPE
SEED_COUNT = base_probe.SEED_COUNT
DRAG_START = base_probe.DRAG_START
DRAG_END = base_probe.DRAG_END
PAUSE_SAVE_POINT = base_probe.PAUSE_SAVE_POINT
PAUSE_LOAD_POINT = base_probe.PAUSE_LOAD_POINT
SAVE_SLOT_POINT = base_probe.SAVE_SLOT_POINT
SAVE_ACTION_POINT = base_probe.SAVE_ACTION_POINT
SAVE_MENU_RETURN_POINT = base_probe.SAVE_MENU_RETURN_POINT
RESUME_POINT = base_probe.RESUME_POINT
DESELECT_POINT = base_probe.DESELECT_POINT
# 7th pause-menu row ("초기메뉴" / initial menu), inferred from the 35px row
# pitch already confirmed by RESUME_POINT (row1)/PAUSE_SAVE_POINT
# (row4)/PAUSE_LOAD_POINT (row5): y = 132 + (n-1)*35.
PAUSE_MAIN_MENU_POINT = (400, 342)
# "초기 메뉴로 돌아가시겠습니까?" confirm dialog's OK ("확인") button, measured
# from lap746 captures (s3-after-confirm-guess.png): orange border box
# x=[389,449] y=[306,352] -> center (419,329). The prior (400,300) guess was
# ~30px above the button hitbox (still inside the dialog panel, over the
# icon/text area), which is why it never registered a click.
S3_CONFIRM_OK_POINT = (419, 329)
# 6th pause-menu row ("다시하기" / restart), same 35px row pitch as
# PAUSE_MAIN_MENU_POINT (row7): y = 132 + (6-1)*35 = 307.
PAUSE_RESTART_POINT = (400, 307)
MOVE_TARGET = DRAG_END

ProbeError = base_probe.ProbeError
sha256 = base_probe.sha256
write_json = base_probe.write_json
send_key = base_probe.send_key
capture = base_probe.capture
fixture_units = base_probe.fixture_units
unit_snapshot = base_probe.unit_snapshot
dense_fixture_requests = base_probe.dense_fixture_requests
SupplyProbe = base_probe.SupplyProbe


def full_dump(pid: int, *, base: int, capacity: int) -> dict[str, Any]:
    """Read the whole entry buffer regardless of ``count`` (lap745 probe gap)."""
    count = int.from_bytes(read_memory(pid, base, 4), "little", signed=True)
    raw_entries = [
        int.from_bytes(read_memory(pid, base + 4 + index * 4, 4), "little", signed=False)
        for index in range(capacity)
    ]
    slots = [entry & 0xFFF for entry in raw_entries]
    nonzero_indices = [index for index, entry in enumerate(raw_entries) if entry != 0]
    return {
        "base": hex(base),
        "capacity": capacity,
        "count": count,
        "raw_entries": raw_entries,
        "slots": slots,
        "nonzero_indices": nonzero_indices,
        "nonzero_count": len(nonzero_indices),
        "count_matches_nonzero": (0 <= count <= capacity and count == len(nonzero_indices)),
    }


def unit_flags(pid: int, slots: list[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for slot in slots:
        if not 0 < slot < 1200:
            rows.append({"slot": slot, "status": "OUT_OF_STOCK_RANGE"})
            continue
        base = UNIT_BASE + slot * UNIT_STRIDE
        rows.append({
            "slot": slot,
            "byte0": int.from_bytes(read_memory(pid, base, 1), "little"),
            "selectable": int.from_bytes(read_memory(pid, base + UNIT_SELECTABLE_OFFSET, 1), "little"),
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
            "x": int.from_bytes(read_memory(pid, base + UNIT_X_OFFSET, 2), "little", signed=True),
            "y": int.from_bytes(read_memory(pid, base + UNIT_Y_OFFSET, 2), "little", signed=True),
        })
    return rows


def diff_commanded_slots(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> list[int]:
    before_by_slot = {row["slot"]: row for row in before if "command" in row}
    changed: list[int] = []
    for row in after:
        slot = row.get("slot")
        if "command" not in row or slot not in before_by_slot:
            continue
        prior = before_by_slot[slot]
        if row["command"] != prior["command"] or row["pending_command"] != prior["pending_command"]:
            changed.append(slot)
    return changed


def run(
    source: Path, runtime_root: Path, artifact_root: Path, *, variant: str, attempt_menu_exit: bool,
    candidate_version: str = "v7", attempt_restart: bool = False, attempt_load_different: bool = False,
    restart_dump_only: bool = False, menu_exit_fresh: bool = False, newgame_stale_probe: bool = False,
) -> dict[str, Any]:
    if variant not in {"original", "candidate"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if candidate_version not in CANDIDATE_MODULES:
        raise ProbeError(f"unsupported candidate version: {candidate_version}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    # Same fixed-name-vs-SHA-glob mismatch as g5_candidate_drag_probe.run_probe
    # (see its comment): resolve by SHA, not by assuming the legacy file name.
    try:
        _, source_exe = runtime_env.validate_original_source(source)
    except runtime_env.RuntimeSafetyError as exc:
        raise ProbeError(f"protected source executable SHA mismatch before run: {exc}") from exc
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    candidate_module = CANDIDATE_MODULES[candidate_version]
    candidate_sha_expected = CANDIDATE_SHAS[candidate_version]
    candidate_bytes: bytes | None = None
    candidate_sha: str | None = None
    if variant == "candidate":
        candidate_bytes, _report = candidate_module.build_candidate(source_exe.read_bytes())
        candidate_sha = __import__("hashlib").sha256(candidate_bytes).hexdigest()
        if candidate_sha != candidate_sha_expected:
            raise ProbeError(f"{candidate_version} candidate SHA mismatch: {candidate_sha}")

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
        if sha256(private_exe) != candidate_sha_expected:
            raise ProbeError("private candidate SHA verification failed after write")

    base = candidate_module.SELECTION_BASE if variant == "candidate" else STOCK_SELECTION_BASE
    capacity = candidate_module.TARGET_CAPACITY if variant == "candidate" else STOCK_SELECTION_CAPACITY

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-stale-tail-probe.v1",
        "variant": variant,
        "candidate_version": candidate_version if variant == "candidate" else None,
        "candidate_sha256": candidate_sha,
        "selection_base": hex(base),
        "selection_capacity": capacity,
        "status": "UNKNOWN",
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env: Mapping[str, str] = os.environ
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

        def click(x: int, y: int, *, drag_to: tuple[int, int] | None = None, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(crop[0] + x), str(crop[1] + y), "--button", str(button)]
            if drag_to is not None:
                argv += ["--drag-to", str(crop[0] + drag_to[0]), str(crop[1] + drag_to[1])]
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

        # lap750 handoff step 2 (menu_exit_fresh): before this probe ever
        # tries "초기메뉴" the fixture/50-selection is already live (lap747).
        # Every prior attempt (original and candidate alike) bounced back
        # into the same battlefield, which could mean either "this harness
        # can never reach the main menu" (an environment constraint, S3
        # unmeasurable regardless of patch) or "a live dense fixture/
        # selection blocks the transition specifically". Try the exact same
        # click sequence here, on a completely fresh solo match with no
        # fixture and no selection, before doing anything else, to tell
        # those two apart. Standalone: returns immediately, no fixture/drag.
        if menu_exit_fresh:
            fresh: dict[str, Any] = {
                "pre_fixture": True, "pre_selection": True, "captures": [],
            }
            try:
                send_key(display, "Escape", env=env, log=log)
                wait_for(lambda item: item.get("ps") == 23, "pause_for_menu_exit_fresh")
                fresh["captures"].append(capture(display, artifact_root / "fresh-pause-menu-raw.png", log))
                click(*PAUSE_MAIN_MENU_POINT)
                time.sleep(0.8)
                fresh["captures"].append(capture(display, artifact_root / "fresh-after-menu-exit-click.png", log))
                menu_state = state()
                fresh["state_after_click"] = {"ps": menu_state.get("ps"), "tick": menu_state.get("tick")}
                if menu_state.get("ps") == 23:
                    click(*S3_CONFIRM_OK_POINT)
                    ps_trace = []
                    deadline = time.monotonic() + 8
                    menu_state = state()
                    ps_trace.append(menu_state.get("ps"))
                    while time.monotonic() < deadline and menu_state.get("ps") not in (9, 3):
                        time.sleep(0.25)
                        menu_state = state()
                        ps_trace.append(menu_state.get("ps"))
                    fresh["state_after_confirm"] = {"ps": menu_state.get("ps"), "tick": menu_state.get("tick")}
                    fresh["ps_trace_after_confirm"] = ps_trace
                    fresh["captures"].append(capture(display, artifact_root / "fresh-after-confirm.png", log))
                fresh["status"] = (
                    "MENU_EXIT_FRESH_PASS" if menu_state.get("ps") == 9
                    else "MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED"
                )
            except (OSError, subprocess.SubprocessError, ProbeError, ValueError) as exc:
                fresh["status"] = "MENU_EXIT_FRESH_INCONCLUSIVE_ERROR"
                fresh["error"] = f"{type(exc).__name__}: {exc}"
            result["menu_exit_fresh"] = fresh
            result["status"] = fresh["status"]
            return result

        # lap752 middle handoff, v9 work (H-NEWGAME-INIT falsification): does
        # the game's own new-game/restart initializer (0x004A3060, hooked by
        # v9 at 0x004A3168) clear the relocated selection array, independent
        # of whether any unit was ever deselected through the normal
        # toggle/dec path? Write a synthetic stale selection directly into
        # memory -- bypassing every unit's own "selected" byte flag entirely,
        # so the per-unit teardown/dec mechanism v8 alone depends on
        # (lap751) can never be the one to clear it -- then restart and dump.
        # No drag, no fixture, no save/load: this isolates exactly the one
        # invariant lap752's static review flagged as missing in v8.
        if newgame_stale_probe:
            ng: dict[str, Any] = {}
            try:
                inject_base = base if variant == "candidate" else STOCK_SELECTION_BASE
                inject_capacity = capacity if variant == "candidate" else STOCK_SELECTION_CAPACITY
                fake_slots = list(range(1, inject_capacity + 1))
                write_memory(pid, inject_base, struct.pack("<i", inject_capacity))
                for index, slot in enumerate(fake_slots):
                    write_memory(pid, inject_base + 4 + index * 4, struct.pack("<I", slot))
                dump_after_inject = full_dump(pid, base=inject_base, capacity=inject_capacity)
                ng["dump_after_inject"] = dump_after_inject
                if dump_after_inject["count"] != inject_capacity or dump_after_inject["nonzero_count"] != inject_capacity:
                    raise ProbeError(f"stale injection did not take: {dump_after_inject}")
                injected_slots_have_no_selected_flag = all(
                    row.get("byte0") == 0 for row in unit_flags(pid, fake_slots)
                    if isinstance(row.get("byte0"), int)
                )
                ng["injected_slots_have_no_selected_flag"] = injected_slots_have_no_selected_flag

                pre_restart_tick = state().get("tick")
                for attempt in range(3):
                    subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
                    send_key(display, "Escape", env=env, log=log)
                    try:
                        wait_for(
                            lambda item: item.get("ps") == 23,
                            f"pause_for_newgame_stale_restart_attempt{attempt}", timeout=15,
                        )
                        break
                    except ProbeError:
                        if attempt == 2:
                            raise
                ng["pause_attempts"] = attempt + 1
                click(*PAUSE_RESTART_POINT)
                time.sleep(0.8)
                ng["captures"] = [capture(display, artifact_root / "newgame-stale-after-restart-click.png", log)]
                restart_state = state()
                ng["state_after_click"] = {"ps": restart_state.get("ps"), "tick": restart_state.get("tick")}
                if restart_state.get("ps") == 23:
                    click(*S3_CONFIRM_OK_POINT)
                    ps_trace = []
                    deadline = time.monotonic() + 20
                    restart_state = state()
                    ps_trace.append(restart_state.get("ps"))
                    while time.monotonic() < deadline and restart_state.get("ps") != 3:
                        time.sleep(0.25)
                        restart_state = state()
                        ps_trace.append(restart_state.get("ps"))
                    ng["state_after_confirm"] = {"ps": restart_state.get("ps"), "tick": restart_state.get("tick")}
                    ng["ps_trace_after_confirm"] = ps_trace
                    ng["captures"].append(capture(display, artifact_root / "newgame-stale-after-confirm.png", log))
                restarted = bool(
                    restart_state.get("ps") == 3
                    and isinstance(restart_state.get("tick"), (int, float))
                    and isinstance(pre_restart_tick, (int, float))
                    and restart_state["tick"] < pre_restart_tick
                )
                ng["pre_restart_tick"] = pre_restart_tick
                ng["restarted"] = restarted
                if restarted:
                    time.sleep(0.5)
                    dump_after_restart = full_dump(pid, base=inject_base, capacity=inject_capacity)
                    ng["dump_after_restart"] = dump_after_restart
                    ng["status"] = (
                        "NEWGAME_STALE_CLEARED" if dump_after_restart["count"] == 0 and dump_after_restart["nonzero_count"] == 0
                        else "NEWGAME_STALE_PERSISTED"
                    )
                else:
                    ng["status"] = "NEWGAME_STALE_INCONCLUSIVE_UNEXPECTED_SCREEN"
            except (OSError, subprocess.SubprocessError, ProbeError, ValueError) as exc:
                ng["status"] = "NEWGAME_STALE_INCONCLUSIVE_ERROR"
                ng["error"] = f"{type(exc).__name__}: {exc}"
            result["newgame_stale_probe"] = ng
            result["status"] = ng["status"]
            return result

        # S5 setup (lap748 work): capture a save made *before* the dense
        # fixture / any selection exist, so loading it back later is a
        # genuinely different game state rather than a reload of this
        # probe's own S1 save. Backed up host-side (plain file copy) so S1's
        # own save-to-the-same-slot doesn't clobber it.
        early_save: dict[str, Any] = {}
        baseline_backup_path = game / "save" / "baseline_backup.dat"
        if attempt_load_different:
            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda item: item.get("ps") == 23, "pause_for_baseline_save")
            click(*PAUSE_SAVE_POINT)
            time.sleep(0.5)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            time.sleep(0.8)
            baseline_save_path = game / "save" / "save001.dat"
            if not baseline_save_path.is_file():
                raise ProbeError(f"baseline save (pre-fixture) was not created: {baseline_save_path}")
            baseline_selection = full_dump(pid, base=base, capacity=capacity)
            shutil.copy2(baseline_save_path, baseline_backup_path)
            early_save = {
                "sha256": sha256(baseline_save_path),
                "size": baseline_save_path.stat().st_size,
                "selection": baseline_selection,
            }
            click(*SAVE_MENU_RETURN_POINT)
            click(*RESUME_POINT)
            wait_for(lambda item: item.get("ps") == 3, "resume_after_baseline_save")
        result["baseline_save_pre_fixture"] = early_save

        worker = unit_snapshot(pid, VISIBLE_WORKER_SLOT)
        if worker["owner"] != 0 or worker["unit_type"] in {0, SEED_TYPE}:
            raise ProbeError(f"slot1198 is not the expected pre-existing worker: {worker}")
        fixture_requests = dense_fixture_requests(worker)
        supply = SupplyProbe(prefix)
        receipts = []
        for request in fixture_requests:
            receipt = supply.call(op=5, owner=0, unit_type=SEED_TYPE, x=request["x"], y=request["y"], count=request["count"])
            receipts.append(receipt)
            if not receipt.get("ok") or receipt.get("fixture_added") != request["count"]:
                raise ProbeError(f"dense fixture batch failed: {receipt}")
        if sum(int(r.get("fixture_added", 0)) for r in receipts) != SEED_COUNT:
            raise ProbeError(f"dense fixture total failed: {receipts}")
        time.sleep(1)
        fixture_list = fixture_units(pid)
        fixture_slots = [int(row["slot"]) for row in fixture_list]
        result["fixture_slots"] = fixture_slots
        result["captures"] = [capture(display, artifact_root / "s0-after-fixture.png", log)]

        click(235, 555)
        time.sleep(1)

        selection_before_drag = full_dump(pid, base=base, capacity=capacity)
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        selection_after_drag = full_dump(pid, base=base, capacity=capacity)
        result["captures"].append(capture(display, artifact_root / "s1-after-drag.png", log))
        if selection_after_drag["count"] == 0:
            click(*DRAG_START, drag_to=DRAG_END)
            time.sleep(1)
            selection_after_drag = full_dump(pid, base=base, capacity=capacity)
            result["drag_retry"] = True
            if selection_after_drag["count"] == 0:
                raise ProbeError("drag produced no selection after one retry")
        result["selection_before_drag"] = selection_before_drag
        result["selection_after_drag"] = selection_after_drag
        result["fixture_flags_at_drag"] = unit_flags(pid, fixture_slots)

        # lap750 handoff step 1 (restart_dump_only): S4 (lap748) only ever
        # checked ``count``/``nonzero_count`` after restart, which is 0 either
        # way regardless of whether the restart cleared entries[20:50] via the
        # save/LOAD_WRAPPER path (tail stays whatever the load leaves it at)
        # or via per-unit deselect/dec (tail explicitly zeroed). No save/load
        # happens in this mode -- it isolates the restart transition itself so
        # ``full_dump`` before/after can tell those two mechanisms apart
        # before generalizing S4's PASS to the untested S3 (new-game) path.
        if restart_dump_only:
            dump_before_restart = full_dump(pid, base=base, capacity=capacity)
            result["dump_before_restart"] = dump_before_restart
            restart: dict[str, Any] = {}
            try:
                pre_restart_tick = state().get("tick")
                send_key(display, "Escape", env=env, log=log)
                wait_for(lambda item: item.get("ps") == 23, "pause_for_restart_dump_only")
                click(*PAUSE_RESTART_POINT)
                time.sleep(0.8)
                restart["captures"] = [capture(display, artifact_root / "restart-dump-after-click.png", log)]
                restart_state = state()
                restart["state_after_click"] = {"ps": restart_state.get("ps"), "tick": restart_state.get("tick")}
                if restart_state.get("ps") == 23:
                    click(*S3_CONFIRM_OK_POINT)
                    ps_trace = []
                    deadline = time.monotonic() + 20
                    restart_state = state()
                    ps_trace.append(restart_state.get("ps"))
                    while time.monotonic() < deadline and restart_state.get("ps") != 3:
                        time.sleep(0.25)
                        restart_state = state()
                        ps_trace.append(restart_state.get("ps"))
                    restart["state_after_confirm"] = {"ps": restart_state.get("ps"), "tick": restart_state.get("tick")}
                    restart["ps_trace_after_confirm"] = ps_trace
                    restart["captures"].append(capture(display, artifact_root / "restart-dump-after-confirm.png", log))
                restarted = bool(
                    restart_state.get("ps") == 3
                    and isinstance(restart_state.get("tick"), (int, float))
                    and isinstance(pre_restart_tick, (int, float))
                    and restart_state["tick"] < pre_restart_tick
                )
                restart["pre_restart_tick"] = pre_restart_tick
                restart["restarted"] = restarted
                if restarted:
                    time.sleep(0.5)
                    dump_after_restart = full_dump(pid, base=base, capacity=capacity)
                    restart["dump_after_restart"] = dump_after_restart
                    tail_nonzero_after = [
                        index for index in dump_after_restart["nonzero_indices"] if index >= STOCK_SELECTION_CAPACITY
                    ]
                    restart["tail_nonzero_indices_after_restart"] = tail_nonzero_after
                    restart["status"] = (
                        "RESTART_DUMP_TAIL_CLEARED" if not tail_nonzero_after
                        else "RESTART_DUMP_TAIL_PRESERVED"
                    )
                else:
                    restart["status"] = "RESTART_DUMP_INCONCLUSIVE_UNEXPECTED_SCREEN"
            except (OSError, subprocess.SubprocessError, ProbeError, ValueError) as exc:
                restart["status"] = "RESTART_DUMP_INCONCLUSIVE_ERROR"
                restart["error"] = f"{type(exc).__name__}: {exc}"
            result["restart_dump"] = restart
            result["status"] = restart["status"]
            return result

        # --- S1/S2: save with the full selection still live, then load
        # without deselecting first, so the live selection still references
        # entries[20:50] when the load wrapper runs. ---
        send_key(display, "Escape", env=env, log=log)
        wait_for(lambda item: item.get("ps") == 23, "pause_for_save")
        click(*PAUSE_SAVE_POINT)
        time.sleep(0.5)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        time.sleep(0.8)
        save_path = game / "save" / "save001.dat"
        if not save_path.is_file():
            raise ProbeError(f"private save was not created: {save_path}")
        result["save_before_load"] = {"sha256": sha256(save_path), "size": save_path.stat().st_size}
        click(*SAVE_MENU_RETURN_POINT)
        click(*RESUME_POINT)
        wait_for(lambda item: item.get("ps") == 3, "resume_after_save")
        result["selection_after_save_resume"] = full_dump(pid, base=base, capacity=capacity)

        send_key(display, "Escape", env=env, log=log)
        wait_for(lambda item: item.get("ps") == 23, "pause_for_load")
        click(*PAUSE_LOAD_POINT)
        time.sleep(0.5)
        click(*SAVE_SLOT_POINT)
        click(*SAVE_ACTION_POINT)
        wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "load_complete", 90)
        time.sleep(0.5)
        result["captures"].append(capture(display, artifact_root / "s1-after-load.png", log))

        after_load = full_dump(pid, base=base, capacity=capacity)
        result["selection_after_load_no_deselect"] = after_load
        if variant == "candidate":
            result["legacy_after_load"] = full_dump(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)
        legit_slots = set(after_load["slots"][: max(after_load["count"], 0)])
        tail_slots = set(
            slot for index, slot in zip(after_load["nonzero_indices"], [after_load["slots"][i] for i in after_load["nonzero_indices"]])
            if index >= STOCK_SELECTION_CAPACITY
        )
        result["legit_slots_after_load"] = sorted(legit_slots)
        result["stale_tail_slots_after_load"] = sorted(tail_slots)

        fixture_units_after_load = fixture_units(pid)
        fixture_slots_after_load = [int(row["slot"]) for row in fixture_units_after_load]
        result["fixture_slots_after_load"] = fixture_slots_after_load
        flags_after_load = unit_flags(pid, fixture_slots_after_load)
        result["fixture_flags_after_load"] = flags_after_load

        # S1 continued: right-click move, then diff every fixture unit's
        # command/pending fields to see who actually receives it.
        click(*MOVE_TARGET, button=3)
        time.sleep(1)
        flags_after_move = unit_flags(pid, fixture_slots_after_load)
        result["fixture_flags_after_move"] = flags_after_move
        commanded_slots = set(diff_commanded_slots(flags_after_load, flags_after_move))
        result["commanded_slots_after_move"] = sorted(commanded_slots)
        result["commanded_outside_legit_selection"] = sorted(commanded_slots - legit_slots)
        result["captures"].append(capture(display, artifact_root / "s1-after-move.png", log))

        # S2: was a stale-tail unit's own selection flag/selectable byte left
        # dangling relative to what the live array now says is selected.
        result["stale_tail_unit_flags_after_load"] = [
            row for row in flags_after_load if row.get("slot") in tail_slots
        ]

        click(*DESELECT_POINT)
        time.sleep(0.5)
        after_deselect = full_dump(pid, base=base, capacity=capacity)
        result["selection_after_deselect"] = after_deselect
        result["captures"].append(capture(display, artifact_root / "s1-after-deselect.png", log))

        # Most severe risk (docstring risk (4)): if count went negative, a
        # save issued *right now* would have SAVE_WRAPPER's
        # ``cmp ecx,20; jle`` (signed) let the negative count through, and
        # STREAM_SAVE_FN's ``rep movsd`` would then use it as an unsigned
        # repeat count (~4G dwords). Test this worst case directly, before
        # anything else (like a redrag) has a chance to move count away from
        # whatever the deselect just left it at.
        crashed = False
        deselect_save_state: dict[str, Any] = {}
        deselect_save_attempted = after_deselect["count"] < 0
        if deselect_save_attempted:
            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda item: item.get("ps") == 23, "pause_for_deselect_save")
            click(*PAUSE_SAVE_POINT)
            time.sleep(0.5)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            time.sleep(1.5)
            crashed = game_proc.poll() is not None
            try:
                deselect_save_state = state()
            except (OSError, ValueError) as exc:
                crashed = True
                deselect_save_state = {"error": f"{type(exc).__name__}: {exc}"}
            if not crashed:
                click(*SAVE_MENU_RETURN_POINT)
                click(*RESUME_POINT)
                wait_for(lambda item: item.get("ps") == 3, "resume_after_deselect_save")
        result["negative_count_save_crash_check"] = {
            "attempted": deselect_save_attempted,
            "process_alive": not crashed,
            "state": deselect_save_state,
        }

        after_redrag: dict[str, Any] = {}
        resave_state: dict[str, Any] = {}
        if not crashed:
            click(*DRAG_START, drag_to=DRAG_END)
            time.sleep(1)
            after_redrag = full_dump(pid, base=base, capacity=capacity)
            result["selection_after_redrag"] = after_redrag
            result["captures"].append(capture(display, artifact_root / "s1-after-redrag.png", log))

            send_key(display, "Escape", env=env, log=log)
            wait_for(lambda item: item.get("ps") == 23, "pause_for_resave")
            click(*PAUSE_SAVE_POINT)
            time.sleep(0.5)
            click(*SAVE_SLOT_POINT)
            click(*SAVE_ACTION_POINT)
            time.sleep(1.2)
            crashed = game_proc.poll() is not None
            try:
                resave_state = state()
            except (OSError, ValueError) as exc:
                crashed = True
                resave_state = {"error": f"{type(exc).__name__}: {exc}"}
            result["resave_crash_check"] = {"process_alive": not crashed, "state": resave_state}
            result["save_after_redrag"] = {
                "sha256": sha256(save_path) if save_path.is_file() else None,
                "size": save_path.stat().st_size if save_path.is_file() else None,
            }
            if not crashed:
                click(*SAVE_MENU_RETURN_POINT)
                click(*RESUME_POINT)
                wait_for(lambda item: item.get("ps") == 3, "resume_after_resave")
        else:
            result["resave_crash_check"] = {"skipped": "process already crashed at negative-count save"}
            result["save_after_redrag"] = {"skipped": True}

        # --- S4 (best-effort, lap748 work): "다시하기" (restart) with the
        # live 50-selection still selected -- does the restarted match
        # inherit any of it? Independent of S3 (different pause-menu row).
        if attempt_restart and not crashed:
            s4: dict[str, Any] = {}
            try:
                pre_restart_tick = state().get("tick")
                send_key(display, "Escape", env=env, log=log)
                wait_for(lambda item: item.get("ps") == 23, "pause_for_restart")
                s4["captures_pre_click"] = [capture(display, artifact_root / "s4-pause-menu-raw.png", log)]
                click(*PAUSE_RESTART_POINT)
                time.sleep(0.8)
                s4["captures"] = [capture(display, artifact_root / "s4-after-restart-click.png", log)]
                restart_state = state()
                s4["state_after_click"] = {"ps": restart_state.get("ps"), "tick": restart_state.get("tick")}
                if restart_state.get("ps") == 23:
                    click(*S3_CONFIRM_OK_POINT)
                    ps_trace = []
                    deadline = time.monotonic() + 20
                    restart_state = state()
                    ps_trace.append(restart_state.get("ps"))
                    while time.monotonic() < deadline and restart_state.get("ps") != 3:
                        time.sleep(0.25)
                        restart_state = state()
                        ps_trace.append(restart_state.get("ps"))
                    s4["state_after_confirm"] = {"ps": restart_state.get("ps"), "tick": restart_state.get("tick")}
                    s4["ps_trace_after_confirm"] = ps_trace
                    s4["captures"].append(capture(display, artifact_root / "s4-after-confirm.png", log))
                restarted = bool(
                    restart_state.get("ps") == 3
                    and isinstance(restart_state.get("tick"), (int, float))
                    and isinstance(pre_restart_tick, (int, float))
                    and restart_state["tick"] < pre_restart_tick
                )
                s4["pre_restart_tick"] = pre_restart_tick
                s4["restarted"] = restarted
                if restarted:
                    time.sleep(0.5)
                    s4["selection_after_restart"] = full_dump(pid, base=base, capacity=capacity)
                    s4["fixture_slots_after_restart"] = [int(row["slot"]) for row in fixture_units(pid)]
                    s4["status"] = (
                        "S4_PASS_SELECTION_CLEARED"
                        if s4["selection_after_restart"]["count"] == 0 and s4["selection_after_restart"]["nonzero_count"] == 0
                        else "S4_FAIL_SELECTION_CARRIED_OVER"
                    )
                else:
                    s4["status"] = "S4_INCONCLUSIVE_UNEXPECTED_SCREEN"
            except (OSError, subprocess.SubprocessError, ProbeError, ValueError) as exc:
                s4["status"] = "S4_INCONCLUSIVE_ERROR"
                s4["error"] = f"{type(exc).__name__}: {exc}"
            result["s4_restart"] = s4

        # --- S5 (best-effort, lap748 work): "불러오기" a save made before
        # the dense fixture / any selection existed (genuinely different
        # game state, not a reload of this probe's own S1 save) while the
        # live 50-selection is still selected.
        if attempt_load_different and not crashed:
            s5: dict[str, Any] = {}
            try:
                if not baseline_backup_path.is_file():
                    raise ProbeError("baseline backup save missing; --attempt-load-different requires it")
                save_path_local = game / "save" / "save001.dat"
                shutil.copy2(baseline_backup_path, save_path_local)
                s5["selection_before"] = full_dump(pid, base=base, capacity=capacity)
                fixture_before_load_different = [int(row["slot"]) for row in fixture_units(pid)]
                send_key(display, "Escape", env=env, log=log)
                wait_for(lambda item: item.get("ps") == 23, "pause_for_load_different")
                click(*PAUSE_LOAD_POINT)
                time.sleep(0.5)
                click(*SAVE_SLOT_POINT)
                click(*SAVE_ACTION_POINT)
                wait_for(lambda item: item.get("ps") == 3, "load_different_complete", 90)
                time.sleep(0.5)
                s5["captures"] = [capture(display, artifact_root / "s5-after-load-different.png", log)]
                after_load_different = full_dump(pid, base=base, capacity=capacity)
                s5["selection_after_load"] = after_load_different
                fixture_after_load_different = [int(row["slot"]) for row in fixture_units(pid)]
                s5["fixture_slots_after_load"] = fixture_after_load_different
                s5["fixture_units_vanished"] = sorted(
                    set(fixture_before_load_different) - set(fixture_after_load_different)
                )
                stale_tail_slots = sorted(
                    slot for index, slot in zip(
                        after_load_different["nonzero_indices"],
                        [after_load_different["slots"][i] for i in after_load_different["nonzero_indices"]],
                    )
                    if index >= STOCK_SELECTION_CAPACITY
                )
                s5["stale_tail_slots_after_load"] = stale_tail_slots
                flags_before_move = unit_flags(pid, stale_tail_slots) if stale_tail_slots else []
                click(*MOVE_TARGET, button=3)
                time.sleep(1)
                flags_after_move = unit_flags(pid, stale_tail_slots) if stale_tail_slots else []
                s5["stale_tail_commanded_after_move"] = sorted(
                    diff_commanded_slots(flags_before_move, flags_after_move)
                )
                s5["invariant_ok"] = after_load_different.get("count_matches_nonzero", False)
                s5["status"] = (
                    "S5_PASS_NO_CARRYOVER"
                    if after_load_different["count"] == 0 and after_load_different["nonzero_count"] == 0
                    else "S5_FAIL_SELECTION_CARRIED_OVER"
                )
            except (OSError, subprocess.SubprocessError, ProbeError, ValueError) as exc:
                s5["status"] = "S5_INCONCLUSIVE_ERROR"
                s5["error"] = f"{type(exc).__name__}: {exc}"
            result["s5_load_different"] = s5

        # --- S3 (best-effort): quit to the main menu with a live selection,
        # start a new game, and check the array is clean. Not gated on S1/S2
        # PASS since it exercises a different code path (new-game init).
        if attempt_menu_exit and not crashed:
            s3: dict[str, Any] = {}
            try:
                send_key(display, "Escape", env=env, log=log)
                wait_for(lambda item: item.get("ps") == 23, "pause_for_menu_exit")
                # lap747: capture the raw pause menu (all row labels) before
                # clicking any row -- the row-7 guess (PAUSE_MAIN_MENU_POINT)
                # opened *a* confirm dialog, but its confirm button led back
                # into gameplay with an "[ESL] new-user support exited"
                # message rather than a menu transition, so row 7 is
                # probably not the actual "return to main menu" item.
                s3["captures_pre_click"] = [capture(display, artifact_root / "s3-pause-menu-raw.png", log)]
                click(*PAUSE_MAIN_MENU_POINT)
                time.sleep(0.8)
                s3["captures"] = [capture(display, artifact_root / "s3-after-menu-exit-click.png", log)]
                menu_state = state()
                s3["state_after_click"] = {"ps": menu_state.get("ps"), "tick": menu_state.get("tick")}
                if menu_state.get("ps") == 23:
                    # Stock UIs commonly gate a destructive menu jump behind a
                    # yes/no confirm; try the dialog's likely center-bottom
                    # "yes" position once, then stop guessing on any other
                    # outcome.
                    click(*S3_CONFIRM_OK_POINT)
                    # The menu-teardown/main-menu-init transition can take
                    # longer than a fixed 0.8s sleep (lap747 saw a single
                    # post-click read land back on ps==3 with the same
                    # battlefield frame still on screen); poll for a few
                    # seconds and record every observed ps so a genuine
                    # cancel (settles on 3 immediately) is distinguishable
                    # from a slow transition (settles on 9 later).
                    ps_trace = []
                    deadline = time.monotonic() + 8
                    menu_state = state()
                    ps_trace.append(menu_state.get("ps"))
                    while time.monotonic() < deadline and menu_state.get("ps") not in (9, 3):
                        time.sleep(0.25)
                        menu_state = state()
                        ps_trace.append(menu_state.get("ps"))
                    s3["state_after_confirm_guess"] = {"ps": menu_state.get("ps"), "tick": menu_state.get("tick")}
                    s3["ps_trace_after_confirm"] = ps_trace
                    s3["captures"].append(capture(display, artifact_root / "s3-after-confirm-guess.png", log))
                if menu_state.get("ps") == 9:
                    click(184, 560)
                    wait_for(lambda item: item.get("ps") == 7, "s3_ps7")
                    if read_selector().get("selected") != "solo":
                        click(344, 169)
                        time.sleep(0.5)
                    click(462, 169)
                    deadline = time.monotonic() + 10
                    while read_selector().get("selected") != "solo" and time.monotonic() < deadline:
                        time.sleep(0.2)
                    click(608, 564)
                    wait_for(lambda item: item.get("ps") == 5, "s3_ps5")
                    ready_deadline = time.monotonic() + 12
                    ready = {}
                    while time.monotonic() < ready_deadline:
                        ready = runtime_env._read_local_ready_state(lambda a, s: read_memory(cast(int, pid), a, s))
                        if ready.get("ready_value") == 1:
                            break
                        time.sleep(0.2)
                    click(608, 564)
                    wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "s3_ps3")
                    s3["new_game_selection"] = full_dump(pid, base=base, capacity=capacity)
                    s3["status"] = "S3_PASS" if s3["new_game_selection"]["count"] == 0 and s3["new_game_selection"]["nonzero_count"] == 0 else "S3_FAIL_NOT_CLEARED"
                else:
                    s3["status"] = "S3_INCONCLUSIVE_UNEXPECTED_SCREEN"
            except (OSError, subprocess.SubprocessError, ProbeError, ValueError) as exc:
                s3["status"] = "S3_INCONCLUSIVE_ERROR"
                s3["error"] = f"{type(exc).__name__}: {exc}"
            result["s3"] = s3

        invariants_ok = all(
            cast(dict, result.get(key, {})).get("count_matches_nonzero", False)
            for key in (
                "selection_after_drag", "selection_after_save_resume",
                "selection_after_load_no_deselect", "selection_after_deselect",
                "selection_after_redrag",
            )
        )
        no_leak = len(result["commanded_outside_legit_selection"]) == 0
        result["status"] = (
            "PASS_NO_STALE_TAIL_EFFECT" if invariants_ok and no_leak and not crashed
            else "FAIL_STALE_TAIL_CONFIRMED"
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
            "global_kill_used": False,
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
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--attempt-menu-exit", action="store_true",
                        help="best-effort S3 (quit to main menu, start new game, check clean array)")
    parser.add_argument("--attempt-restart", action="store_true",
                        help="best-effort S4 (pause menu '다시하기'/restart, check clean array)")
    parser.add_argument("--attempt-load-different", action="store_true",
                        help="best-effort S5 (pause menu '불러오기' a pre-fixture baseline save)")
    parser.add_argument("--candidate-version", choices=tuple(CANDIDATE_MODULES), default="v7")
    parser.add_argument("--restart-dump-only", action="store_true",
                        help=(
                            "lap750 step 1: drag-select, restart ('다시하기'), full_dump "
                            "before/after only -- no save/load -- to attribute which "
                            "mechanism clears entries[20:50] on restart"
                        ))
    parser.add_argument("--menu-exit-fresh", action="store_true",
                        help=(
                            "lap750 step 2: try '초기메뉴' on a fresh solo match with no "
                            "fixture/selection, before doing anything else, to tell an "
                            "environment-wide menu-exit constraint apart from a "
                            "fixture/selection-specific block"
                        ))
    parser.add_argument("--newgame-stale-probe", action="store_true",
                        help=(
                            "lap752 handoff step 3: inject a synthetic stale selection "
                            "directly into memory (no unit's own selected-flag set, so "
                            "the dec/teardown path can never be the one clearing it), "
                            "restart, and dump -- isolates whether the new-game/restart "
                            "initializer itself (v9's hook) clears the array"
                        ))
    args = parser.parse_args(argv)
    result = run(
        args.source, args.runtime_root, args.artifact_root,
        variant=args.variant, attempt_menu_exit=args.attempt_menu_exit,
        candidate_version=args.candidate_version,
        attempt_restart=args.attempt_restart, attempt_load_different=args.attempt_load_different,
        restart_dump_only=args.restart_dump_only, menu_exit_fresh=args.menu_exit_fresh,
        newgame_stale_probe=args.newgame_stale_probe,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") in {
        "RESTART_DUMP_TAIL_CLEARED", "RESTART_DUMP_TAIL_PRESERVED",
        "MENU_EXIT_FRESH_PASS", "MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED",
        "NEWGAME_STALE_CLEARED", "NEWGAME_STALE_PERSISTED",
    }:
        return 0 if result.get("cleanup", {}).get("ok") else 2
    return 0 if str(result.get("status", "")).startswith("PASS") and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
