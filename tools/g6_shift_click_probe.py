#!/usr/bin/env python3
"""G6 H-G6a runtime probe: Shift+click selection add when the local seat is not 1P.

Variants (each run = private game copy, Wine prefix and Xvfb):

``orig``  protected original EXE, stock bridge (1200-slot pool, 20-entry selection)
``port``  deployed G5-selection-50 port on the ESL2608 G2 EXE (4093-slot pool, 50-entry selection)
``cand``  ``port`` + ``g6_shift_click_count_bound`` (H-G6a)

Seat setup (``--seat K``):

``slot0`` (default) keeps the lobby seat 0 and writes K into the owner byte of the unused pool slot 0.  The
Shift+click handler compares that slot's owner (empty selection cells are id 0) with ``[0xB63FC4]`` at
``0x41DD93``, so this reproduces the same compare as local=K without a seat the game would treat as absent.
``keys`` requires the lobby arrow keys to move the seat; they did not move it in lap977 (see lobby rows).
``keys-held`` (H-G6s S-1) holds each arrow key for 0.25 s after an optional focus click (``--focus``) and
records the lobby panel diff plus the ``0x632C9C..0x632F80`` table; ``lobby-snapshot`` (S-2) writes a copy of the
lobby table with seat 0 and seat K swapped to ``0x632E0C`` and sets ``[0xC0D0F4]`` so the game's own refresh
``0x4B7700`` copies it and recomputes the local index through ``0x43AF40`` (no direct local/owner write).

The fixture is a synthetic engine-seeded set (op5, owner = lobby seat): a sparse screen grid for clean single
clicks plus a dense band for the selection-cap fill.  Stages: G6-1 plain click then five Shift+clicks, G6-2
Shift+drag over two units, G6-3 Shift+click removal, G6-4 cap rejection at 50 (cap-50 variants only).
``keys-focus`` (H-G6k) holds Down x3 / Up x3 per focus variant (f0 none, f1 Alt tap, f2 blank click, f3 number
button, f4 XSendEvent), reading the game's key state word and queue count while the key is held (K-1) and the lobby
table / local index afterwards (K-2); the first variant that moves the seat stops the sequence (f5 = Tab tap, added after f0..f4
showed the chat EDIT keeps keyboard focus).
``--lobby-only`` stops after the lobby phase.
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
from typing import Any, Callable, Mapping, cast

import numpy as np

from patches.population.g2_esl2608_runtime_layout import ESL2608_LAYOUT
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from patches.population.runtime_driver import write as write_memory
from patches.selection import g5_esl2608_g2_port as port_patch
from patches.selection import g6_shift_click_count_bound as g6_patch
from patches.selection import g7_save_trailer_local_restore as g7r5_patch
from patches.selection import g7_title_load_seat_restore as g7_patch
from tools import runtime_env
from tools.g2_esl2608_phase_a_shift_probe import (
    BASE_SOURCE, CALIBRATION_POINTS, SEED_TYPE, UNIT_HP_OFFSET, UNIT_OWNER_OFFSET,
    UNIT_PENDING_XY_OFFSET, UNIT_STRIDE, UNIT_TYPE_OFFSET, UNIT_X_OFFSET, UNIT_Y_OFFSET, copy_overlay,
)
from tools.g5_candidate_drag_probe import ProbeError, SupplyProbe, capture, sha256, write_json
from tools.g5_screen_world_calibration import decode_xy, fit_affine

REPO = Path(__file__).resolve().parents[1]
INPUT_ROOT = REPO.parent / "260921_temp"
STOCK = REPO / "Syw2plus" / "syw2plus_original.exe"
PORT_EXE = INPUT_ROOT / (
    "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092_G5_선택50_시험용.exe"
)
PORT_EXES = {
    "normal": PORT_EXE,
    "fixed_start": PORT_EXE.parent / (
        "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092_G5_선택50_시험용.exe"
    ),
}
G2_EXE = INPUT_ROOT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092.exe"
LOCAL_INDEX_VA = 0xB63FC4
# (selection base, capacity, pool base, existence base, pool capacity)
LAYOUTS = {
    "orig": (0x00899024, 20, 0x0066B790, 0x008990C8, 1200),
    "port": (port_patch.G5BSS_VA, 50, ESL2608_LAYOUT.unit_pool_base, ESL2608_LAYOUT.unit_existence_base,
             ESL2608_LAYOUT.capacity),
    "cand": (port_patch.G5BSS_VA, 50, ESL2608_LAYOUT.unit_pool_base, ESL2608_LAYOUT.unit_existence_base,
             ESL2608_LAYOUT.capacity),
    "cand67": (port_patch.G5BSS_VA, 50, ESL2608_LAYOUT.unit_pool_base, ESL2608_LAYOUT.unit_existence_base,
               ESL2608_LAYOUT.capacity),  # H-G6r: port + G6 + G7 (R4b)
    "cand-r5": (port_patch.G5BSS_VA, 50, ESL2608_LAYOUT.unit_pool_base, ESL2608_LAYOUT.unit_existence_base,
                ESL2608_LAYOUT.capacity),  # H-G7s: port + G6 + R5 save trailer
}
LOBBY_TABLE_VA = 0x632C9C
LOBBY_TABLE_SIZE = 0x170
LOBBY_SNAPSHOT_VA = 0x632E0C
LOBBY_REFRESH_FLAG_VA = 0xC0D0F4
LOBBY_DUMP_END = 0x632F80
LOBBY_SLOTS = 8
LOBBY_OWN_ID_VA = 0xC0D11C  # 0x439B90 returns [0xC0D110 + 0xC], the id 0x43AF40 looks for
# 0x632CA0 dword[i] (0x43AF40 matches own DPID), 0x632CC0 6-byte rows, 0x632CF0 dword[i], 0x632D94 15-byte names.
# Solo row i (observed lap979): [type 5=human/computer 0=none, i, flag 0 for row 0 else 1, 1<<i, 0, i]; only the
# content bytes (offsets 0 and 2) move between seats, the position bytes (1, 3, 5) stay with the row.
LOBBY_ROW_CONTENT_BYTES = (0, 2)
LOBBY_ID_OFFSET, LOBBY_ROW_OFFSET, LOBBY_DWORD_OFFSET, LOBBY_NAME_OFFSET = 0x04, 0x24, 0x54, 0xF8
LOBBY_FOCUS_POINTS = {"none": None, "name": (40, 50), "number": (40, 78)}
LOBBY_PANEL_BOX = (0, 0, 190, 520)
LOBBY_CHAT_BOX = (225, 495, 760, 520)  # chat input line under the message board (lap979 caret at (241,509))
HELD_KEYS = ("Right", "Down", "Left", "Up")
REAL_SEAT_METHODS = ("keys", "keys-held", "keys-focus", "lobby-snapshot")
# H-G6k: 0x421630 sets the key state word [0x61E070 + vk*2]; 0x4216B0 appends to the queue counted at 0x61E270.
KEY_STATE_BASE_VA = 0x61E070
KEY_QUEUE_COUNT_VA = 0x61E270
KEY_FOCUS_VARIANTS = (("f0", "none"), ("f1", "alt-tap"), ("f2", "blank-click"), ("f3", "number-button"),
                      ("f4", "xsendevent"), ("f5", "tab"), ("f6", "own-name-click"))
KEY_FOCUS_BLANK_POINTS = ((490, 410), (100, 160))
KEY_FOCUS_KEYS = (("Down", 0x28),) * 3 + (("Up", 0x26),) * 3
KEY_FOCUS_CONTROL = ("a", 0x41)  # positive control: any VK outside the 0x423FAF switch also sets its state word
ISOLATED_TARGET = 10
CLICK_DY = (-12, -20, -6, 0, 6)
SPARSE_ROWS = (110, 180, 250, 320)
SPARSE_COLS = tuple(range(60, 780, 90))
DENSE_ROWS = (385, 410, 435, 458)
DENSE_COLS = tuple(range(150, 770, 38))


def parse_scroll_keys(spec: str) -> list[tuple[str, float]]:
    """``"Down:2.5,Right:1"`` -> [("Down", 2.5), ("Right", 1.0)]: arrow keys held in game to scroll the camera."""
    plan: list[tuple[str, float]] = []
    for part in filter(None, (p.strip() for p in spec.split(","))):
        name, _, seconds = part.partition(":")
        if name not in HELD_KEYS or not seconds or not 0 < float(seconds) <= 10:
            raise ProbeError(f"bad scroll key spec: {part!r}")
        plan.append((name, float(seconds)))
    return plan


def _u(pid: int, va: int, size: int, signed: bool = False) -> int:
    return int.from_bytes(read_memory(pid, va, size), "little", signed=signed)


def selection_snapshot(pid: int, variant: str) -> dict[str, Any]:
    base, cap, *_ = LAYOUTS[variant]
    count = _u(pid, base, 4, signed=True)
    if not 0 <= count <= cap:
        raise ProbeError(f"selection count outside 0..{cap}: {count}")
    raw = [_u(pid, base + 4 + i * 4, 4) for i in range(count)]
    slots = [value & 0xFFF for value in raw]
    return {"count": count, "slots": slots, "unique_slots": len(set(slots))}


def unit_row(pid: int, variant: str, slot: int) -> dict[str, int]:
    _sb, _cap, pool, exists, capacity = LAYOUTS[variant]
    if not 0 < slot < capacity:
        raise ProbeError(f"unit slot outside capacity: {slot}")
    base = pool + slot * UNIT_STRIDE
    return {
        "slot": slot, "exists": _u(pid, exists + slot * 2, 2), "type": _u(pid, base + UNIT_TYPE_OFFSET, 1),
        "owner": _u(pid, base + UNIT_OWNER_OFFSET, 1), "hp": _u(pid, base + UNIT_HP_OFFSET, 4, signed=True),
        "x": _u(pid, base + UNIT_X_OFFSET, 2, signed=True), "y": _u(pid, base + UNIT_Y_OFFSET, 2, signed=True),
    }


def live_units(pid: int, variant: str, owner: int, *, unit_type: int | None = None) -> list[dict[str, int]]:
    _sb, _cap, _pool, exists, capacity = LAYOUTS[variant]
    rows = []
    for slot in range(1, capacity):
        if _u(pid, exists + slot * 2, 2) == 0:
            continue
        row = unit_row(pid, variant, slot)
        if row["owner"] == owner and row["hp"] > 0 and (unit_type is None or row["type"] == unit_type):
            rows.append(row)
    return rows


def build_lobby_snapshot(table: bytes, seat: int, own_id: int | None = None) -> tuple[bytes, dict[str, int]]:
    """Copy of the lobby table with seat 0 and ``seat`` swapped so ``0x43AF40`` selects ``seat``.

    ``0x43AF40`` returns the first index whose id dword equals the own DPID, so entries before ``seat`` must
    differ from it.  The own id (``own_id``, default: the table's first entry) moves to ``seat`` and the
    entries before it become ``own + 1``.
    """
    if len(table) != LOBBY_TABLE_SIZE:
        raise ProbeError(f"lobby table size {len(table)} != {LOBBY_TABLE_SIZE}")
    if not 0 < seat < LOBBY_SLOTS:
        raise ProbeError(f"lobby seat outside 1..{LOBBY_SLOTS - 1}: {seat}")
    out = bytearray(table)
    own = int.from_bytes(table[LOBBY_ID_OFFSET:LOBBY_ID_OFFSET + 4], "little") if own_id is None else own_id
    other = (own + 1) & 0xFFFFFFFF

    def swap(offset: int, size: int, stride: int | None = None) -> None:
        a, b = offset, offset + seat * (stride or size)
        out[a:a + size], out[b:b + size] = table[b:b + size], table[a:a + size]

    for byte in LOBBY_ROW_CONTENT_BYTES:
        swap(LOBBY_ROW_OFFSET + byte, 1, 6)
    swap(LOBBY_DWORD_OFFSET, 4)
    swap(LOBBY_NAME_OFFSET, 15)
    for i in range(LOBBY_SLOTS):
        value = other if i < seat else own
        out[LOBBY_ID_OFFSET + i * 4:LOBBY_ID_OFFSET + i * 4 + 4] = value.to_bytes(4, "little")
    return bytes(out), {"own_id": own, "other_id": other}


def key_focus_verdict(steps: list[dict[str, Any]]) -> dict[str, bool]:
    """K-1 = a held key set the game's key state word; K-2 = the table changed and the game picked a new local."""
    return {"k1_delivered": any(x["key_state"] == 1 for x in steps),
            "k2_moved": any(x["table_changed"] and x["local_index"] != 0 for x in steps)}


def panel_changed_pixels(before: Path, after: Path, box: tuple[int, int, int, int] = LOBBY_PANEL_BOX) -> int:
    """Pixels that differ inside ``box`` (default: the left seat panel) between two lobby captures."""
    from PIL import Image, ImageChops

    a = Image.open(before).convert("RGB").crop(box)
    b = Image.open(after).convert("RGB").crop(box)
    diff = np.asarray(ImageChops.difference(a, b)).max(axis=2)
    return int((diff > 0).sum())


def _install(variant: str, port: str = "normal") -> tuple[bytes | None, dict[str, Any]]:
    """Return the EXE bytes to install (None keeps the private original copy)."""
    if variant == "orig":
        return None, {"sha256": sha256(STOCK)}
    if port not in PORT_EXES:
        raise ProbeError(f"unsupported port: {port}")
    if sha256(PORT_EXES[port]) != g6_patch.PORT_SHA256[port]:
        raise ProbeError("port EXE SHA mismatch")
    port_bytes = PORT_EXES[port].read_bytes()
    if variant == "port":
        return port_bytes, {"sha256": g6_patch.PORT_SHA256[port]}
    candidate, report = g6_patch.build_candidate(port_bytes)
    if variant == "cand67":
        return g7_patch.build_candidate(candidate)
    if variant == "cand-r5":
        return g7r5_patch.build_candidate(candidate)
    return candidate, report


def run_probe(variant: str, seat: int, runtime_root: Path, artifact_root: Path, *,
              lobby_only: bool = False, seat_phase: str = "ps7", key_sequence: str = "Right,Down,Left,Up",
              key_sleep: float = 0.6, seat_method: str = "slot0", focus: str = "none",
              stability_seconds: float = 60.0, key_control_ps3: bool = False,
              port: str = "normal", scroll_keys: str = "") -> dict[str, Any]:
    if variant not in LAYOUTS:
        raise ProbeError(f"unsupported variant: {variant}")
    if focus not in LOBBY_FOCUS_POINTS:
        raise ProbeError(f"unsupported focus: {focus}")
    scroll_plan = parse_scroll_keys(scroll_keys)
    real_seat = seat_method in REAL_SEAT_METHODS
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    sel_base, cap, pool_base, _exists, pool_cap = LAYOUTS[variant]
    exe_bytes, build_report = _install(variant, port)
    bridge_dir = artifact_root / "bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", str(pool_cap),
                    *(["--unit-pool-base", hex(pool_base)] if variant != "orig" else [])],
                   cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("private source copy SHA mismatch before install")
    overlay = copy_overlay(game) if variant != "orig" else []
    if exe_bytes is not None:
        private_exe.write_bytes(exe_bytes)
    result: dict[str, Any] = {
        "schema": "syw2plus.g6-shift-click-probe.v1", "status": "UNKNOWN", "variant": variant, "port": port, "seat": seat,
        "selection_cap": cap,
        "provenance": {"private_exe_sha256": sha256(private_exe), "private_game": str(game),
                        "private_prefix": str(prefix), "overlay_files": len(overlay),
                        "bridge_sha256": sha256(bridge), "build_report": build_report},
        "inputs": [], "lobby": [], "lobby_dumps": [], "stages": {}, "checks": {}, "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    game_proc: Any = None
    display = ""
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
                   SYW2_SUPPLY_PROBE="1")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def wait_for(pred: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45) -> None:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = read_state(pid)
                    if pred(last):
                        return
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda s: s.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        origin = (int(info["x"]), int(info["y"]))

        def click(x: int, y: int, *, button: int = 1, drag_to: tuple[int, int] | None = None) -> None:
            args = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(origin[0] + x), str(origin[1] + y), "--button", str(button)]
            if drag_to is not None:
                args += ["--drag-to", str(origin[0] + drag_to[0]), str(origin[1] + drag_to[1])]
            subprocess.run(args, env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"x": x, "y": y, "button": button,
                                     "drag_to": list(drag_to) if drag_to else None})

        def shift_hold(action: Callable[[], None]) -> None:
            subprocess.run(["xdotool", "keydown", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            time.sleep(0.15)
            try:
                action()
            finally:
                time.sleep(0.15)
                subprocess.run(["xdotool", "keyup", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            time.sleep(0.4)

        def key(name: str) -> None:
            subprocess.run(["xdotool", "key", name], env=env, stdout=log, stderr=log, timeout=10, check=True)
            result["inputs"].append({"key": name})

        def snap() -> dict[str, Any]:
            return selection_snapshot(pid, variant)

        def lobby_state() -> dict[str, Any]:
            return runtime_env._read_local_ready_state(lambda a, n: read_memory(pid, a, n))

        shots = artifact_root / "shots"
        shots.mkdir()

        def shot(label: str) -> None:
            capture(display, shots / f"{time.strftime('%Y%m%d_%H%M%S')}_{label}.png", log)

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)

        def lobby_row(step: str) -> None:
            state = read_state(pid)
            result["lobby"].append({"step": step, "ps": state.get("ps"), "tick": state.get("tick"),
                                    "local_index": _u(pid, LOCAL_INDEX_VA, 4)})

        def press_seat_keys() -> None:
            tried = 0
            while seat and _u(pid, LOCAL_INDEX_VA, 4) != seat and tried < len(keys_plan):
                name = keys_plan[tried]
                if name.startswith("click:"):
                    cx, cy = (int(v) for v in name[6:].split("x"))
                    click(cx, cy)
                else:
                    key(name)
                time.sleep(key_sleep)
                tried += 1
                lobby_row(f"act_{name}")
                shot(f"{phase}_act{tried}_{name.replace(':', '')}")

        def lobby_dump(step: str) -> dict[str, Any]:
            raw = read_memory(pid, LOBBY_TABLE_VA, LOBBY_DUMP_END - LOBBY_TABLE_VA)
            row = {"step": step, "table_hex": raw.hex(), "table_sha256": hashlib.sha256(raw).hexdigest(),
                   "flag": _u(pid, LOBBY_REFRESH_FLAG_VA, 4), "local_index": _u(pid, LOCAL_INDEX_VA, 4),
                   "own_id": _u(pid, LOBBY_OWN_ID_VA, 4)}
            result["lobby_dumps"].append(row)
            return row

        def hold_arrow_keys() -> None:
            """S-1: optional focus click, then each arrow key held 0.25 s; panel diff + table dump per key."""
            point = LOBBY_FOCUS_POINTS[focus]
            if point is not None:
                click(*point)
                time.sleep(0.4)
            shot(f"s1_{focus}_focus")
            prev_shot = sorted(shots.glob("*.png"), key=lambda f: f.stat().st_mtime_ns)[-1]
            prev = lobby_dump(f"s1_{focus}_focus")
            result["s1"] = {"focus": focus, "steps": []}
            for name in HELD_KEYS:
                subprocess.run(["xdotool", "keydown", name], env=env, stdout=log, stderr=log, timeout=10, check=True)
                time.sleep(0.25)
                subprocess.run(["xdotool", "keyup", name], env=env, stdout=log, stderr=log, timeout=10, check=True)
                result["inputs"].append({"key_held": name, "seconds": 0.25})
                time.sleep(0.5)
                shot(f"s1_{focus}_{name}")
                cur_shot = sorted(shots.glob("*.png"), key=lambda f: f.stat().st_mtime_ns)[-1]
                cur = lobby_dump(f"s1_{focus}_{name}")
                result["s1"]["steps"].append({
                    "key": name, "panel_changed_pixels": panel_changed_pixels(prev_shot, cur_shot),
                    "table_changed": cur["table_sha256"] != prev["table_sha256"],
                    "flag": cur["flag"], "local_index": cur["local_index"]})
                prev_shot, prev = cur_shot, cur
            result["s1"]["moved"] = any(x["table_changed"] and x["local_index"] != 0
                                        for x in result["s1"]["steps"])

        def hold_key_focus() -> None:
            """H-G6k: per focus variant hold Down x3 / Up x3, read the key state word and queue while held."""
            nonlocal seat
            shot("k_initial")
            prev_shot = sorted(shots.glob("*.png"), key=lambda f: f.stat().st_mtime_ns)[-1]
            prev = lobby_dump("k_initial")
            result["k"] = {"variants": []}
            for tag, label in KEY_FOCUS_VARIANTS:
                if tag == "f1":
                    subprocess.run(["xdotool", "key", "Alt_L"], env=env, stdout=log, stderr=log, timeout=10, check=True)
                elif tag == "f2":
                    for point in KEY_FOCUS_BLANK_POINTS:
                        click(*point)
                elif tag == "f3":
                    click(*LOBBY_FOCUS_POINTS["number"])
                elif tag == "f6":  # H-G7s W-3: click the own name/row cell, then the arrows
                    click(*LOBBY_FOCUS_POINTS["name"])
                elif tag == "f5":  # the chat subclass handles Tab (0x9); see whether it hands focus to the window
                    subprocess.run(["xdotool", "key", "Tab"], env=env, stdout=log, stderr=log, timeout=10, check=True)
                time.sleep(0.5)
                target = ["--window", str(content)] if tag == "f4" else []
                steps: list[dict[str, Any]] = []
                for name, vk in KEY_FOCUS_KEYS:
                    word_va = KEY_STATE_BASE_VA + vk * 2
                    queue_before = _u(pid, KEY_QUEUE_COUNT_VA, 4)
                    subprocess.run(["xdotool", "keydown", *target, name], env=env, stdout=log, stderr=log,
                                   timeout=10, check=True)
                    time.sleep(0.3)
                    key_state, queue_during = _u(pid, word_va, 2), _u(pid, KEY_QUEUE_COUNT_VA, 4)
                    subprocess.run(["xdotool", "keyup", *target, name], env=env, stdout=log, stderr=log,
                                   timeout=10, check=True)
                    result["inputs"].append({"key_held": name, "seconds": 0.3, "variant": tag})
                    time.sleep(1)
                    shot(f"k_{tag}_{name}")
                    cur_shot = sorted(shots.glob("*.png"), key=lambda f: f.stat().st_mtime_ns)[-1]
                    cur = lobby_dump(f"k_{tag}_{name}")
                    steps.append({"key": name, "key_state": key_state, "queue_before": queue_before,
                                  "queue_during": queue_during, "panel_changed_pixels":
                                  panel_changed_pixels(prev_shot, cur_shot),
                                  "table_changed": cur["table_sha256"] != prev["table_sha256"],
                                  "flag": cur["flag"], "local_index": cur["local_index"]})
                    prev_shot, prev = cur_shot, cur
                name, vk = KEY_FOCUS_CONTROL
                subprocess.run(["xdotool", "keydown", *target, name], env=env, stdout=log, stderr=log,
                               timeout=10, check=True)
                time.sleep(0.3)
                control_state = _u(pid, KEY_STATE_BASE_VA + vk * 2, 2)
                subprocess.run(["xdotool", "keyup", *target, name], env=env, stdout=log, stderr=log,
                               timeout=10, check=True)
                time.sleep(0.5)
                shot(f"k_{tag}_control_{name}")
                control_shot = sorted(shots.glob("*.png"), key=lambda f: f.stat().st_mtime_ns)[-1]
                entry = {"variant": tag, "focus": label, "steps": steps, "control_key": name,
                         "control_key_state": control_state,
                         "control_chat_changed_pixels": panel_changed_pixels(prev_shot, control_shot,
                                                                              LOBBY_CHAT_BOX),
                         **key_focus_verdict(steps)}
                prev_shot = control_shot
                result["k"]["variants"].append(entry)
                if entry["k2_moved"]:
                    result["k"]["moved_variant"] = tag
                    seat = cur["local_index"]
                    break

        def write_lobby_snapshot() -> None:
            """S-2: swapped table copy + refresh flag; the game's 0x4B7700 copies it and recomputes local."""
            before = lobby_dump("s2_before")
            table = bytes.fromhex(before["table_hex"])[:LOBBY_TABLE_SIZE]
            snapshot, ids = build_lobby_snapshot(table, seat, before["own_id"])
            result["s2"] = {"seat": seat, "original_table_hex": table.hex(), "snapshot_hex": snapshot.hex(),
                            "ids": ids, "snapshot_va": hex(LOBBY_SNAPSHOT_VA)}
            write_memory(pid, LOBBY_SNAPSHOT_VA, snapshot)
            write_memory(pid, LOBBY_REFRESH_FLAG_VA, (1).to_bytes(4, "little"))
            deadline = time.monotonic() + 5
            while _u(pid, LOBBY_REFRESH_FLAG_VA, 4) != 0 and time.monotonic() < deadline:
                time.sleep(0.1)
            time.sleep(0.5)
            after = lobby_dump("s2_after")
            shot("s2_after")
            result["s2"].update({
                "flag_consumed": after["flag"] == 0,
                "table_matches_snapshot": bytes.fromhex(after["table_hex"])[:LOBBY_TABLE_SIZE] == snapshot,
                "local_index": after["local_index"], "game_wrote_local": after["local_index"] == seat})

        keys_plan = [k for k in key_sequence.split(",") if k] if seat_method == "keys" else []
        phase = seat_phase

        def seat_action() -> None:
            if seat_method == "keys":
                press_seat_keys()
            elif seat_method == "keys-held":
                hold_arrow_keys()
            elif seat_method == "keys-focus":
                hold_key_focus()
            elif seat_method == "lobby-snapshot":
                write_lobby_snapshot()

        lobby_row("ps7_entry")
        shot("ps7_entry")
        if phase == "ps7":
            seat_action()
        if real_seat and phase == "ps7" and lobby_only:
            result["status"] = "LOBBY_ONLY"
            return result
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        lobby_row("ps5_entry")
        shot("lobby_initial")
        if phase == "ps5":
            seat_action()
        if real_seat:
            shot("lobby_after_seat_method")
            lobby_dump("before_start")
            local = lobby_state()
            if key_control_ps3 and local["local_index"] != seat:
                seat = local["local_index"]  # H-G6k control: start at the seat the lobby kept, only read key words
            if local["local_index"] != seat:
                result["status"] = "BLOCKED"
                result["error"] = f"seat move failed: local_index={local['local_index']} wanted {seat}"
                return result
        if lobby_only:
            result["status"] = "LOBBY_ONLY"
            return result
        # Solo auto-starts shortly after the confirm click; click again only if it did not.
        deadline = time.monotonic() + 8
        while read_state(pid).get("ps") not in (2, 3) and time.monotonic() < deadline:
            time.sleep(0.3)
        if read_state(pid).get("ps") not in (2, 3):
            click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")
        local_ps3 = _u(pid, LOCAL_INDEX_VA, 4)
        result["local_at_ps3"] = local_ps3
        shot("ps3_start")
        if real_seat and local_ps3 != seat:
            raise ProbeError(f"local index changed by start: {local_ps3} != {seat}")
        if key_control_ps3:
            # H-G6k positive control: the same key state words read while PS3 runs.
            time.sleep(6)
            result["ps3_key_control"] = []
            for name, vk in (*KEY_FOCUS_KEYS[:1], KEY_FOCUS_KEYS[3], KEY_FOCUS_CONTROL):
                subprocess.run(["xdotool", "keydown", name], env=env, stdout=log, stderr=log, timeout=10, check=True)
                time.sleep(0.3)
                state_held = _u(pid, KEY_STATE_BASE_VA + vk * 2, 2)
                subprocess.run(["xdotool", "keyup", name], env=env, stdout=log, stderr=log, timeout=10, check=True)
                time.sleep(0.3)
                result["ps3_key_control"].append({"key": name, "vk": vk, "state_held": state_held,
                                                  "state_after": _u(pid, KEY_STATE_BASE_VA + vk * 2, 2),
                                                  "queue": _u(pid, KEY_QUEUE_COUNT_VA, 4)})
            result["status"] = "KEY_CONTROL"
            return result
        if real_seat and stability_seconds > 0:
            # S-2: local stays k, no leave message (captured), seat-k units exist and the AI does not steer them.
            def seat_units() -> dict[int, tuple[int, ...]]:
                return {r["slot"]: (r["x"], r["y"], _u(pid, pool_base + r["slot"] * UNIT_STRIDE
                                                       + UNIT_PENDING_XY_OFFSET, 4))
                        for r in live_units(pid, variant, local_ps3)}

            first = seat_units()
            locals_seen = {_u(pid, LOCAL_INDEX_VA, 4)}
            changed_30 = None
            t0 = time.monotonic()
            while time.monotonic() - t0 < stability_seconds:
                time.sleep(2)
                locals_seen.add(_u(pid, LOCAL_INDEX_VA, 4))
                if read_state(pid).get("ps") != 3:
                    raise ProbeError("game left PS3 during seat stability hold")
                if changed_30 is None and time.monotonic() - t0 >= 30:
                    now = seat_units()
                    changed_30 = sum(1 for slot, v in now.items() if first.get(slot) != v)
            shot("ps3_stability_end")
            result["stability"] = {"seconds": stability_seconds, "locals_seen": sorted(locals_seen),
                                   "owner_units": len(first), "units_changed_by_30s": changed_30}
        # slot0 emulation keeps local at the lobby seat (0) and fixtures owned by it; only the empty-slot
        # owner byte (what the Shift+click loop compares against local) is changed after the setup.
        fx_owner = local_ps3
        anchor_owner = fx_owner
        owned = live_units(pid, variant, anchor_owner)
        result["owned_before_fixture"] = [{"slot": r["slot"], "type": r["type"], "hp": r["hp"],
                                          "x": r["x"], "y": r["y"]} for r in owned]
        # Start units vary per run (hero or worker); the movable one is the lowest-hp non-building.
        worker = next((r for r in owned if r["type"] == 7), min(owned, key=lambda r: r["hp"], default=None))
        if worker is None:
            raise ProbeError(f"no live owner={anchor_owner} unit at start")
        result["worker"] = worker
        supply = SupplyProbe(prefix)
        map_w, map_h = _u(pid, 0x00B3DE34, 2, True), _u(pid, 0x00B3DE36, 2, True)
        worker_base = pool_base + worker["slot"] * UNIT_STRIDE

        def calibrate() -> tuple[Any, Any]:
            if not scroll_plan:  # a scrolled camera no longer shows the anchor; it was selected before the scroll
                click(200, 170, drag_to=(730, 445))  # warm-up drag selecting the anchor, as the port probe
                time.sleep(0.4)
            click(120, 90, button=3)
            time.sleep(0.2)
            samples = []
            for point in CALIBRATION_POINTS:
                click(*point, button=3)
                time.sleep(0.2)
                samples.append((point, decode_xy(_u(pid, worker_base + UNIT_PENDING_XY_OFFSET, 4))))
            result["calibration_samples"] = [[list(p), list(map(int, w))] for p, w in samples]
            return fit_affine(samples)

        def check_alive() -> None:
            if read_state(pid).get("ps") != 3:
                raise ProbeError(f"game left PS3: {read_state(pid).get('ps')}")

        time.sleep(6)  # PS3 renders black for the first seconds; calibrate on the live scene
        if scroll_plan:
            click(200, 170, drag_to=(730, 445))  # select the anchor before the camera leaves it
            time.sleep(0.4)
        for scroll_name, scroll_seconds in scroll_plan:  # fixed-start port: camera begins at the map corner
            subprocess.run([sys.executable, str(REPO / "tools/x11_send_keys.py"), "--display", display,
                            "--hold-ms", str(int(scroll_seconds * 1000)), scroll_name],
                           env=env, stdout=log, stderr=log, timeout=scroll_seconds + 10, check=True)
            result["inputs"].append({"scroll_key": scroll_name, "seconds": scroll_seconds})
            time.sleep(0.5)
        for attempt in range(3):
            matrix, offset = calibrate()
            if abs(np.linalg.det(matrix)) > 1e-6:
                break
            result.setdefault("calibration_retries", []).append(result["calibration_samples"])
            time.sleep(3)
        else:
            raise ProbeError("screen-world calibration failed (singular fit)")
        inverse = np.linalg.inv(matrix)
        def world_to_screen(x: int, y: int) -> tuple[int, int]:
            p = inverse @ (np.array([x, y]) - offset)
            return int(round(p[0])), int(round(p[1]))

        def screen_to_world(x: int, y: int) -> tuple[int, int]:
            w = matrix @ np.array([x, y]) + offset
            return int(round(w[0])), int(round(w[1]))

        # Fixture laid out by screen position: a sparse grid (clean single-unit clicks) and a dense band
        # at the bottom (selection-cap fill).  Points outside the map are dropped.
        sparse_screen = [(x, y) for y in SPARSE_ROWS for x in SPARSE_COLS]
        dense_screen = [(x, y) for y in DENSE_ROWS for x in DENSE_COLS]
        planned: list[tuple[str, tuple[int, int]]] = []
        for kind, pts in (("sparse", sparse_screen), ("dense", dense_screen)):
            for sx, sy in pts:
                wx, wy = screen_to_world(sx, sy)
                if 1 <= wx < map_w - 1 and 1 <= wy < map_h - 1:
                    planned.append((kind, (wx, wy)))
        result["fixture_plan"] = {"sparse": sum(1 for k, _ in planned if k == "sparse"),
                                  "dense": sum(1 for k, _ in planned if k == "dense"),
                                  "owner": fx_owner, "synthetic": True,
                                  "method": "engine-seeded op5 at screen-derived world tiles"}
        for kind, (wx, wy) in planned:
            receipt = supply.call(op=5, owner=fx_owner, unit_type=SEED_TYPE, x=wx, y=wy, count=1)
            if not receipt.get("ok") or receipt.get("fixture_added") != 1:
                raise ProbeError(f"fixture spawn failed at {(wx, wy)}: {receipt}")
        time.sleep(1)
        slot0_owner_va = pool_base + UNIT_OWNER_OFFSET
        if seat_method == "slot0" and seat != fx_owner:
            before = _u(pid, slot0_owner_va, 1)
            write_memory(pid, slot0_owner_va, bytes([seat]))
            result["slot0_owner_poke"] = {"va": hex(slot0_owner_va), "before": before, "to": seat,
                                          "readback": _u(pid, slot0_owner_va, 1),
                                          "local_index": _u(pid, LOCAL_INDEX_VA, 4),
                                          "reason": "lobby arrow-key seat move not reproduced; emulates the "
                                                    "empty-slot owner != local compare at 0x41DD93"}
            if result["slot0_owner_poke"]["readback"] != seat:
                raise ProbeError("slot-0 owner poke did not stick")
        time.sleep(2)
        check_alive()
        fixture = live_units(pid, variant, fx_owner, unit_type=SEED_TYPE)
        sparse_world = {w for k, w in planned if k == "sparse"}
        sparse_rows = [r for r in fixture if (r["x"], r["y"]) in sparse_world]
        shot("fixture")

        def deselect() -> None:
            click(*blank)
            time.sleep(0.2)
            if snap()["count"] != 0:
                raise ProbeError("deselect point selected a unit")

        screen_of = {r["slot"]: world_to_screen(r["x"], r["y"]) for r in fixture}
        # Deselect point: the viewport grid point farthest from every fixture/owned unit (sprites sit ~15px
        # above the foot point), found on the live layout instead of assuming an empty tile.
        pins = [(sx, sy - 15) for sx, sy in screen_of.values()]
        pins += [world_to_screen(r["x"], r["y"]) for r in live_units(pid, variant, fx_owner)]
        blank = max(((x, y) for x in range(120, 700, 30) for y in range(110, 440, 20)),
                    key=lambda g: min((g[0] - px) ** 2 + (g[1] - py) ** 2 for px, py in pins))
        result["blank_point"] = list(blank)
        visible = [(r, screen_of[r["slot"]]) for r in fixture
                   if 5 <= screen_of[r["slot"]][0] <= 795 and 45 <= screen_of[r["slot"]][1] <= 470]

        def isolation_point(slot: int, screen: tuple[int, int]) -> tuple[int, int] | None:
            for dy in CLICK_DY:
                deselect()
                click(screen[0], screen[1] + dy)
                time.sleep(0.3)
                s = snap()
                if s["count"] == 1 and s["slots"] == [slot]:
                    return screen[0], screen[1] + dy
            return None

        check_alive()
        isolated: list[tuple[int, tuple[int, int]]] = []
        for row in sorted(sparse_rows, key=lambda r: (screen_of[r["slot"]][0], screen_of[r["slot"]][1])):
            screen = screen_of[row["slot"]]
            if not 5 <= screen[0] <= 795 or not 45 <= screen[1] <= 470:
                continue
            point = isolation_point(row["slot"], screen)
            if point is not None:
                isolated.append((row["slot"], point))
            if len(isolated) >= ISOLATED_TARGET:
                break
        result["stages"]["fixture"] = {"active_units": len(fixture), "visible_units": len(visible),
                                        "sparse_units": len(sparse_rows), "isolated": len(isolated),
                                        "isolated_rows": isolated, "owner": fx_owner, "synthetic": True}
        if len(isolated) < 9:
            raise ProbeError(f"too few isolated fixture rows: {len(isolated)}")
        deselect()
        check_alive()

        # G6-1: plain click A, then five Shift+clicks B..F.
        (a_slot, a_xy), rest = isolated[0], isolated[1:]
        click(*a_xy)
        time.sleep(0.3)
        g61: dict[str, Any] = {"after_click": snap(), "steps": []}
        for slot, xy in rest[:5]:
            shift_hold(lambda xy=xy: click(*xy))
            g61["steps"].append({"slot": slot, **snap()})
        g61["final"] = snap()
        result["stages"]["g6_1"] = g61
        shot("g6_1_after")

        # G6-2: Shift+drag over two further units (control path).
        deselect()
        click(*a_xy)
        time.sleep(0.3)
        pair = rest[5:7]
        others = [screen_of[s] for s in screen_of if s not in {p[0] for p in pair} | {a_slot}]
        x0, x1 = sorted(p[1][0] for p in pair)
        y0, y1 = sorted(p[1][1] for p in pair)
        rect = ((x0 - 10, y0 - 22), (x1 + 10, y1 + 8))
        g62: dict[str, Any] = {"rect": [list(rect[0]), list(rect[1])], "pair": [p[0] for p in pair],
                               "before": snap(),
                               "foreign_units_in_rect": sum(
                                   1 for ox, oy in others if rect[0][0] <= ox <= rect[1][0]
                                   and rect[0][1] <= oy <= rect[1][1])}
        shift_hold(lambda: click(*rect[0], drag_to=rect[1]))
        g62["after"] = snap()
        result["stages"]["g6_2"] = g62

        # G6-3: Shift+click on an already selected unit removes it.
        selected_now = snap()
        g63: dict[str, Any] = {"before": selected_now}
        victim = next((slot, xy) for slot, xy in isolated if slot in selected_now["slots"] and slot != a_slot)
        shift_hold(lambda: click(*victim[1]))
        g63["victim"] = victim[0]
        g63["after"] = snap()
        result["stages"]["g6_3"] = g63

        # G6-4: at the 50 cap an additional Shift+click is rejected (cand/port only).  The drag rectangle
        # starts right of the left-most isolated unit so that unit stays unselected as the extra.
        if cap >= 50:
            deselect()
            extra_slot, extra_xy = isolated[0]
            click(extra_xy[0] + 40, 40, drag_to=(788, 470))
            time.sleep(0.8)
            g64: dict[str, Any] = {"drag": snap(), "extra_slot": extra_slot}
            if extra_slot not in g64["drag"]["slots"]:
                shift_hold(lambda: click(*extra_xy))
                g64["after_extra"] = snap()
            result["stages"]["g6_4"] = g64
            check_alive()
        shot("final")

        s1, s2, s3 = g61, result["stages"]["g6_2"], result["stages"]["g6_3"]
        counts = [s1["after_click"]["count"], *[x["count"] for x in s1["steps"]]]
        result["checks"] = {
            "plain_click_selects_one": s1["after_click"]["count"] == 1 and s1["after_click"]["slots"] == [a_slot],
            "g6_1_counts": counts,
            "g6_1_grows": counts == [1, 2, 3, 4, 5, 6],
            "g6_1_stuck_at_one": counts == [1] * 6,
            "g6_2_grows": s2["after"]["count"] >= s2["before"]["count"] + 2
            and set(s2["pair"]) <= set(s2["after"]["slots"]),
            "g6_3_removes": s3["after"]["count"] == s3["before"]["count"] - 1
            and s3["victim"] not in s3["after"]["slots"],
            "g6_4_cap": cap < 50 or ("after_extra" in result["stages"]["g6_4"]
                                      and result["stages"]["g6_4"]["after_extra"]["count"] == 50),
            "game_alive": game_proc.poll() is None,
        }
        result["status"] = "COMPLETE"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError, StopIteration,
            runtime_env.RuntimeSafetyError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
        if display:
            capture(display, artifact_root / f"{time.strftime('%Y%m%d_%H%M%S')}_failure.png", log)
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
    parser.add_argument("--variant", choices=sorted(LAYOUTS), required=True)
    parser.add_argument("--seat", type=int, default=1, help="local seat (keys) / empty-slot owner mismatch (slot0); 0 = 1P control")
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--lobby-only", action="store_true")
    parser.add_argument("--seat-phase", choices=("ps7", "ps5"), default="ps7")
    parser.add_argument("--seat-method", choices=("keys", "slot0", "keys-held", "keys-focus", "lobby-snapshot"),
                        default="slot0",
                        help="keys = lobby arrow key taps (not reproduced); slot0 = keep local 0 and set the owner "
                             "byte of the unused pool slot 0 to --seat (same empty-slot compare as local=seat); "
                             "keys-held = arrow keys held 0.25 s (S-1); keys-focus = H-G6k Down/Up held per focus "
                             "variant f0..f4 with the game's key state word read while held, --seat becomes the "
                             "observed local on a seat move; lobby-snapshot = swapped lobby table via the "
                             "game's own 0x4B7700 refresh (S-2)")
    parser.add_argument("--focus", choices=sorted(LOBBY_FOCUS_POINTS), default="none",
                        help="keys-held: click this lobby row element before the held keys")
    parser.add_argument("--stability-seconds", type=float, default=60.0,
                        help="real-seat methods: seconds to hold PS3 and watch local/AI after start")
    parser.add_argument("--key-control-ps3", action="store_true",
                        help="keys-focus: start the game at the kept seat and read the key state words in PS3")
    parser.add_argument("--port", choices=sorted(PORT_EXES), default="normal",
                        help="G5 port the variant is built on (orig ignores it)")
    parser.add_argument("--scroll-keys", default="",
                        help="in game before calibration: arrow keys held to scroll the camera, e.g. Down:2.5,Right:1")
    parser.add_argument("--keys", default="Right,Down,Left,Up", help="comma-separated key plan")
    parser.add_argument("--key-sleep", type=float, default=0.6)
    args = parser.parse_args(argv)
    result = run_probe(args.variant, args.seat, args.runtime_root, args.artifact_root, lobby_only=args.lobby_only,
                       seat_phase=args.seat_phase, key_sequence=args.keys, key_sleep=args.key_sleep,
                       seat_method=args.seat_method, focus=args.focus, stability_seconds=args.stability_seconds,
                       key_control_ps3=args.key_control_ps3, port=args.port,
                       scroll_keys=args.scroll_keys)
    print(json.dumps({"status": result.get("status"), "variant": args.variant, "seat": args.seat,
                      "checks": result.get("checks"), "lobby": result.get("lobby"),
                      "s1": result.get("s1"), "k": result.get("k"), "ps3_key_control": result.get("ps3_key_control"), "s2": {k: v for k, v in result.get("s2", {}).items()
                                                      if not k.endswith("_hex")},
                      "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") in {"COMPLETE", "LOBBY_ONLY", "KEY_CONTROL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
