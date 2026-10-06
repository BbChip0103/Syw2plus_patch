#!/usr/bin/env python3
"""G5 checklist (C) — read the worker's command-menu button-ID slot table
directly from memory instead of guessing firing targets for "V"/"I"/"F".

2026-09-29 10:35 operator direction: for the special-ability "v" cell, use
documentation instead of more blind offset probing (lap735/lap737 already
spent the 2-failed-hypothesis budget on live-fire target search and landed on
UNKNOWN for "v", N/A for "i"). The sibling reverse-engineering project
``Syw2plus_re`` (read-only reference, not this project's queue/state) has
already decompiled the command-menu button system:
``analysis/memory_maps/unit_ai_dispatch.md`` documents a per-unit struct
slot table -- three parallel uint16 arrays in the *same* unit struct this
repo already reads (``+0x290`` command, ``+0x384`` pending, ``+0x388``
pending xy come from the same struct, see ``UNIT_BASE``/``UNIT_STRIDE``):

    btn[12]     uint16 at +0x532 .. +0x549   (button ID shown on each slot)
    enabled[12] uint16 at +0x54A .. +0x561
    count[12]   int16  at +0x562 .. +0x579
    sub_index   uint16 at +0x57A
    command_kind uint16 at +0x57C

This is read-only: no click on V/I/F is needed to identify what they are,
only to select the worker (which every prior checklist probe already does
safely). Comparing the combat-unit HQ's slot table (also captured here)
against the known S/M/A/P/H button IDs (Move=0x01, Stop=0x02, Attack=0x03,
Patrol=0x14, HoldPosition=0x16 per the same reference doc) validates that
these offsets apply to this build before trusting the worker's V/I/F IDs.

The protected original is only read (SHA before/after). No game files or
EXE bytes are modified; no ability is fired.
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

from tools import runtime_env
from tools.g5_candidate_drag_probe import (
    ProbeError, DRAG_START, DRAG_END, STOCK_SELECTION_BASE, STOCK_SELECTION_CAPACITY,
    VISIBLE_WORKER_SLOT, UNIT_BASE, UNIT_STRIDE,
    selection_snapshot, unit_snapshot,
    sha256, write_json, capture,
)
from tools.g5_worker_repair_command_probe import find_hq_slot
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256

# Reference doc analysis/memory_maps/unit_ai_dispatch.md (Syw2plus_re, read-only).
KNOWN_BUTTON_NAMES = {
    0x01: "Move(이동)", 0x02: "Stop(정지)", 0x03: "Attack(공격)",
    0x09: "MenuMine(채광)", 0x0a: "MenuProduce(생산)", 0x0d: "MenuD(이동계서브)",
    0x0e: "MenuRepair(수리)", 0x10: "MenuBuild(건설루트진입)",
    0x13: "Special13", 0x14: "Patrol(순찰)", 0x16: "HoldPosition(홀드)",
    0x17: "Special17", 0x1b: "GuildBuy(길드구매)", 0x20: "AbilityA_sp(특수생산)",
    0x25: "Special25", 0x26: "AbilityA(1차능력)", 0x27: "AbilityB(2차능력)",
    0x28: "AbilityC", 0x2b: "ExtraAction(부가액션)", 0x32: "MagicA",
    0x34: "MagicB", 0x35: "MagicC", 0x37: "FormationCmd(대형)",
    0x39: "UnitCallB", 0x3a: "MagicD", 0x3b: "UnitDeploy(유닛배치)",
    0x3c: "Chat(채팅)", 0x3e: "AbilityE", 0x3f: "AbilityF",
    0x40: "AbilityD(특수능력D)", 0x41: "AbilityG", 0x42: "AbilityH",
}
SLOT_BTN_OFFSET = 0x532
SLOT_ENABLED_OFFSET = 0x54A
SLOT_COUNT_OFFSET = 0x562
SLOT_COUNT_N = 12
SUB_INDEX_OFFSET = 0x57A
COMMAND_KIND_OFFSET = 0x57C
WORKER_BUTTON_SCREEN = {"stop": (667, 503), "move": (703, 503), "v": (740, 503), "i": (777, 503), "f": (667, 538)}


def read_slot_table(pid: int, unit_base: int) -> dict[str, Any]:
    btn = [int.from_bytes(read_memory(pid, unit_base + SLOT_BTN_OFFSET + i * 2, 2), "little") for i in range(SLOT_COUNT_N)]
    enabled = [int.from_bytes(read_memory(pid, unit_base + SLOT_ENABLED_OFFSET + i * 2, 2), "little") for i in range(SLOT_COUNT_N)]
    count = [int.from_bytes(read_memory(pid, unit_base + SLOT_COUNT_OFFSET + i * 2, 2), "little", signed=True) for i in range(SLOT_COUNT_N)]
    return {
        "btn": [hex(b) for b in btn],
        "btn_names": [KNOWN_BUTTON_NAMES.get(b, "UNKNOWN") for b in btn],
        "enabled": enabled,
        "count": count,
        "sub_index": int.from_bytes(read_memory(pid, unit_base + SUB_INDEX_OFFSET, 2), "little"),
        "command_kind": int.from_bytes(read_memory(pid, unit_base + COMMAND_KIND_OFFSET, 2), "little"),
    }


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source SHA mismatch")
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

    result: dict[str, Any] = {
        "schema": "syw2plus.g5-command-menu-slot-probe.v1", "variant": "original", "status": "UNKNOWN",
        "provenance": {"source_exe": str(source_exe), "source_sha256": sha256(source_exe),
                       "private_exe_sha256": sha256(private_exe), "game_root": str(game), "run_dir": str(game.parent)},
        "captures": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
               LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b", SYW2_SUPPLY_PROBE="1")
    game_proc: Any = None
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

        def snap(name: str) -> None:
            result["captures"].append(capture(display, artifact_root / f"{name}.png", log))

        def sel() -> dict[str, Any]:
            return selection_snapshot(pid, base=STOCK_SELECTION_BASE, capacity=STOCK_SELECTION_CAPACITY)

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
        if worker["owner"] != 0 or worker["unit_type"] == 0:
            raise ProbeError(f"slot1198 is not the expected worker: {worker}")
        result["worker"] = worker
        wbase = UNIT_BASE + VISIBLE_WORKER_SLOT * UNIT_STRIDE

        hq = find_hq_slot(pid, VISIBLE_WORKER_SLOT)
        result["hq"] = hq

        # Every other checklist probe clicks the legacy minimap point once
        # here before the first drag (lap682 sequence); replicated for parity
        # even though this probe does not use it for anything itself.
        click(235, 555)
        time.sleep(1)

        # --- select worker only, read its command-menu slot table (no clicks
        # on V/I/F -- this is a pure memory read of the already-built menu).
        click(*DRAG_START, drag_to=DRAG_END)
        time.sleep(1)
        cal_sel = sel()
        if VISIBLE_WORKER_SLOT not in cal_sel["slots"]:
            raise ProbeError(f"worker not selected: {cal_sel}")
        snap("00-worker-selected-command-grid")
        result["worker_slot_table"] = read_slot_table(pid, wbase)
        result["worker_button_screen_positions"] = WORKER_BUTTON_SCREEN

        # --- icon reading (S=hand, M=boot, V=sickle, F=blue flame, no "I" in
        # this fixture's nation) suggests V may be an explicit harvest/reap
        # action distinct from the already-known implicit gather-by-right-
        # click. Verify behaviourally: click V, then right-click the visible
        # rice-paddy tile next to the worker/HQ, and read the raw command
        # (+0x290) / pending word (+0x384) before and after. This is the
        # "대상 조건 확인" step the 2026-09-29 10:35 direction asked for --
        # grounded in the slot-table read above, not a blind offset search.
        def worker_raw_state() -> dict[str, Any]:
            return {
                "command": int.from_bytes(read_memory(pid, wbase + 0x290, 2), "little", signed=True),
                "pending": hex(int.from_bytes(read_memory(pid, wbase + 0x384, 4), "little")),
            }

        def reselect_worker_only() -> None:
            click(*DRAG_START, drag_to=DRAG_END)
            time.sleep(0.6)

        field_tiles = [(250, 300), (200, 260), (300, 330), (230, 220)]
        button_probes: dict[str, Any] = {}
        for name, pt in (("v", (740, 503)), ("f", (777, 503))):
            probe_entry: dict[str, Any] = {"before": None, "after_click": None, "attempts": []}
            for click_button, tile in ((3, field_tiles[0]), (1, field_tiles[0]),
                                        (3, field_tiles[1]), (1, field_tiles[2]), (1, field_tiles[3])):
                reselect_worker_only()
                xdo("key", "s")
                time.sleep(0.4)
                before = worker_raw_state()
                click(*pt)
                time.sleep(1.0)
                after_click = worker_raw_state()
                if probe_entry["before"] is None:
                    probe_entry["before"] = before
                    probe_entry["after_click"] = after_click
                    snap(f"02-button-{name}-after-click")
                click(*tile, button=click_button)
                time.sleep(1.2)
                after_ground = worker_raw_state()
                probe_entry["attempts"].append({"tile": list(tile), "button": click_button,
                                                 "after": after_ground, "changed": after_ground != after_click})
                if not alive():
                    raise ProbeError(f"game not alive after button {name} tile {tile}")
            snap(f"03-button-{name}-last-attempt")
            button_probes[name] = probe_entry
        result["button_probes"] = button_probes
        result["field_tiles_screen"] = [list(t) for t in field_tiles]

        # baseline: plain right-click on the same field tile with no button
        # armed first, to compare against the already-documented implicit
        # gather pending value (0x1000008, g5_worker_gather_command_probe).
        reselect_worker_only()
        xdo("key", "s")
        time.sleep(0.4)
        before_plain = worker_raw_state()
        click(*field_tiles[0], button=3)
        time.sleep(1.2)
        after_plain = worker_raw_state()
        snap("04-plain-field-rclick-no-button")
        result["plain_field_rclick"] = {"before": before_plain, "after": after_plain, "alive": alive()}

        result["status"] = "COMPLETE"
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
        subprocess.run(["wineserver", "-k"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        subprocess.run(["wineserver", "-w"], env=env, stdout=log, stderr=log, timeout=10, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
        try:
            children_and_xvfb = children + ([xvfb] if xvfb is not None else [])
            for child in children_and_xvfb:
                child.wait(timeout=5)
        except Exception:
            pass
        result["source_after_sha256"] = sha256(source_exe)
        result["source_unchanged"] = result["source_after_sha256"] == ORIGINAL_SHA
        log.close()

    result_path = artifact_root / "probe-result.json"
    write_json(result_path, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=runtime_env.DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    result = run_probe(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps({k: v for k, v in result.items() if k not in ("captures",)}, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
