#!/usr/bin/env python3
"""G8/G9 runtime probe on the pinned ESL 2611 EXE: start positions and supply limits of 4..8 player solo games.

Each game = one fresh process on a private game copy (Wine prefix, Xvfb).  The solo lobby only offers two slots, so
after choosing a map of the wanted size from the map list the lobby table rows of slots 3..N are rewritten to the
computer-row layout of slot 2 (``[5, i, 1, 1<<i, 0, i]``, dword[i]=1) before the confirm click.  Per owner it records the
nation/ai bytes, ``[player+0x980]`` (hero count the supply loop writes), ``[player+0x2012]`` (supply limit stored by
``0x43FFD9``) and the start units (type, x, y) with their centroid.

Variants: ``base`` (pinned EXE), ``g8`` (supply), ``g9`` (fixed start), ``g8g9``.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time
from typing import Any, Callable, cast

from patches.esl2610 import g8_supply_1500_500_5000 as g8
from patches.esl2610 import g9_fixed_start as g9
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from patches.population.runtime_driver import write as write_memory
from tools import esl2610_runtime, runtime_env
from tools.g5_candidate_drag_probe import ProbeError, capture, sha256, write_json

REPO = Path(__file__).resolve().parents[1]
VARIANTS = ("base", "g8", "g9", "g8g9")
PLAYER_BASE, PLAYER_STRIDE = 0x956770, 0x3ABC
HERO_COUNT_OFFSET, SUPPLY_LIMIT_OFFSET = 0x980, 0x2012
POOL, EXISTS, POOL_CAP, UNIT_STRIDE = 0x66B790, 0x8990C8, 1200, 0x758
LOBBY_TABLE_VA, ROWS_OFFSET, DWORD_OFFSET = 0x632C9C, 0x24, 0x54
HERO_TABLE_VA, HERO_STRIDE, SUPPLY_CAP = 0x9B53D0, 0x394, 5000
MAP_NAME_OFFSET = 0xBA
MAP_LIST_DOWN, MAP_ROW0_Y, MAP_ROW_DY = (748, 298), 122, 20
# (scroll clicks, row index, expected map-name prefix) per player count; the map name is read back from the lobby table
MAPS = {4: (30, 0, "(4"), 8: (80, 4, "(8")}


def build_variant(variant: str) -> tuple[bytes, dict[str, Any]]:
    base = esl2610_runtime.ESL2610_EXE.read_bytes()
    if sha256(esl2610_runtime.ESL2610_EXE) != esl2610_runtime.ESL2610_SHA256:
        raise ProbeError("ESL2611 EXE SHA mismatch")
    if variant == "base":
        return base, {"sha256": esl2610_runtime.ESL2610_SHA256}
    data, report = base, {}
    if "g9" in variant:
        data, report = g9.build_candidate(data)
    if "g8" in variant:
        data, report = g8.build_candidate(data, require_pinned_base=variant == "g8")
    return data, report


def computer_row(slot: int) -> bytes:
    """Lobby row of an occupied computer slot (observed slot 2: ``050101020001``)."""
    return bytes([5, slot, 1, 1 << slot, 0, slot])


def players_table(table: bytes, count: int) -> bytes:
    """Lobby table copy with slots 1..count-1 (0-based) computer rows and dword[i]=1."""
    out = bytearray(table)
    for slot in range(1, count):
        out[ROWS_OFFSET + slot * 6:ROWS_OFFSET + slot * 6 + 6] = computer_row(slot)
        struct.pack_into("<I", out, DWORD_OFFSET + slot * 4, 1)
    return bytes(out)


def centroid(points: list[tuple[int, int]]) -> tuple[float, float] | None:
    if not points:
        return None
    return (round(sum(p[0] for p in points) / len(points), 1), round(sum(p[1] for p in points) / len(points), 1))


def hero_writes(owner_base: int, count: int) -> list[tuple[int, bytes]]:
    """Synthetic writes making ``count`` hero slots of one owner look alive to ``0x43FDD0`` (state=1, no unit).

    Slot ``i``: flag 8 at ``[0x9B53D0+0x394*i-0x184]`` (table entry in use), state word ``[owner+0x20+2i]``=1 (cleared
    by the function every pass, so it is rewritten continuously), recovery word ``[owner+0x1B0+2i]`` and unit word
    ``[owner+0x340+2i]`` = 0.
    """
    writes: list[tuple[int, bytes]] = []
    for i in range(count):
        writes.append((HERO_TABLE_VA + HERO_STRIDE * i - 0x184, b"\x08"))
        writes.append((owner_base + 0x20 + 2 * i, struct.pack("<H", 1)))
        writes.append((owner_base + 0x1B0 + 2 * i, b"\0\0"))
        writes.append((owner_base + 0x340 + 2 * i, b"\0\0"))
    return writes


def mode_value(samples: list[int]) -> int | None:
    """Most frequent sample (ties: larger), ignoring the transient partial sums seen mid-call."""
    if not samples:
        return None
    counts: dict[int, int] = {}
    for value in samples:
        counts[value] = counts.get(value, 0) + 1
    return max(counts, key=lambda v: (counts[v], v))


def expected_supply(variant: str, heroes: int) -> int:
    if "g8" in variant:
        return min(1500 + 500 * heroes, SUPPLY_CAP)
    return 1500 + 200 * heroes


def sample_supply(pid: int, owner: int, heroes: int, seconds: float = 3.0) -> dict[str, Any]:
    base = PLAYER_BASE + owner * PLAYER_STRIDE
    writes = hero_writes(base, heroes)
    limits: list[int] = []
    counts: list[int] = []
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        for address, data in writes:
            write_memory(pid, address, data)
        limits.append(struct.unpack("<h", read_memory(pid, base + SUPPLY_LIMIT_OFFSET, 2))[0])
        counts.append(struct.unpack("<i", read_memory(pid, base + HERO_COUNT_OFFSET, 4))[0])
        time.sleep(0.002)
    return {"heroes": heroes, "samples": len(limits), "supply_mode": mode_value(limits), "supply_max": max(limits),
            "count_mode": mode_value(counts), "synthetic": True}


def run_game(exe: bytes, count: int, runtime_root: Path, artifact_root: Path, *, label: str,
             heroes: tuple[int, ...] = ()) -> dict[str, Any]:
    scrolls, row, prefix_name = MAPS[count]
    manifest, overlay = esl2610_runtime.prepare(exe, runtime_root)
    game = Path(cast(str, manifest["game"]["root"]))  # type: ignore[index]
    prefix = Path(cast(str, manifest["wine"]["prefix"]))  # type: ignore[index]
    private_exe = game / runtime_env.ORIGINAL_EXE
    result: dict[str, Any] = {"label": label, "players": count, "status": "UNKNOWN", "exe_sha256": sha256(private_exe)}
    log = (artifact_root / f"{label}.log").open("a", encoding="utf-8")
    xvfb: Any = None
    children: list[Any] = []
    display = ""
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all", LANG="ko_KR.UTF-8",
                   LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game, env=env,
                                         stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def wait_for(pred: Callable[[dict[str, Any]], bool], what: str, timeout: float = 60) -> None:
            deadline = time.monotonic() + timeout
            last: Any = None
            while time.monotonic() < deadline:
                try:
                    last = read_state(pid)
                    if pred(last):
                        return
                except (OSError, ValueError, ProbeError) as exc:
                    last = f"{type(exc).__name__}: {exc}"
                time.sleep(0.25)
            raise ProbeError(f"{what} timeout; last={last}")

        wait_for(lambda s: s.get("ps") == 9, "ps9")
        time.sleep(2)
        outer, content = runtime_env._game_window_ids(runtime_env._window_tree(display, 10))
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        origin = (int(info["x"]), int(info["y"]))
        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)

        def click(x: int, y: int) -> None:
            subprocess.run([sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                            str(origin[0] + x), str(origin[1] + y)], env=env, stdout=log, stderr=log, timeout=10,
                           check=True)
            time.sleep(0.5)

        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        time.sleep(1)
        for _ in range(scrolls):
            click(*MAP_LIST_DOWN)
        click(520, MAP_ROW0_Y + MAP_ROW_DY * row)
        time.sleep(1)
        table = read_memory(pid, LOBBY_TABLE_VA, 0x170)
        map_name = bytes(table[MAP_NAME_OFFSET:]).split(b"\0")[0].decode("cp949", "replace")
        result["map"] = map_name
        if not map_name.startswith(prefix_name):
            raise ProbeError(f"wrong map selected: {map_name!r}")
        write_memory(pid, LOBBY_TABLE_VA, players_table(table, count))
        result["rows"] = [read_memory(pid, LOBBY_TABLE_VA + ROWS_OFFSET + i * 6, 6).hex() for i in range(8)]
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3", 90)
        time.sleep(4)
        capture(display, artifact_root / f"{label}.png", log)
        owners: list[dict[str, Any]] = []
        for owner in range(8):
            base = PLAYER_BASE + owner * PLAYER_STRIDE
            head = read_memory(pid, base, 4)
            units = []
            for slot in range(1, POOL_CAP):
                if struct.unpack("<H", read_memory(pid, EXISTS + slot * 2, 2))[0] == 0:
                    continue
                u = POOL + slot * UNIT_STRIDE
                if read_memory(pid, u + 0x8E, 1)[0] != owner or struct.unpack("<i", read_memory(pid, u + 0xB4, 4))[0] <= 0:
                    continue
                units.append((read_memory(pid, u + 0x8D, 1)[0],
                              struct.unpack("<h", read_memory(pid, u + 0x2A2, 2))[0],
                              struct.unpack("<h", read_memory(pid, u + 0x2A4, 2))[0]))
            owners.append({"owner": owner, "nation": head[0], "ai": head[2], "units": len(units),
                           "heroes_0x980": struct.unpack("<i", read_memory(pid, base + HERO_COUNT_OFFSET, 4))[0],
                           "supply_limit": struct.unpack("<h", read_memory(pid, base + SUPPLY_LIMIT_OFFSET, 2))[0],
                           "centroid": centroid([(x, y) for _t, x, y in units]),
                           "first_unit": units[0] if units else None, "unit_list": units[:12]})
        result["owners"] = owners
        result["hero_supply"] = [sample_supply(pid, 0, n) for n in heroes]
        result["game_alive"] = game_proc.poll() is None
        result["status"] = "COMPLETE"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError,
            runtime_env.RuntimeSafetyError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
        if display:
            capture(display, artifact_root / f"{label}_failure.png", log)
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
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANTS, required=True)
    parser.add_argument("--players", type=int, choices=sorted(MAPS), required=True)
    parser.add_argument("--games", type=int, default=3)
    parser.add_argument("--heroes", type=lambda v: tuple(int(x) for x in v.split(",") if x), default=())
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {args.artifact_root}")
    args.artifact_root.mkdir(parents=True)
    exe, report = build_variant(args.variant)
    games = [run_game(exe, args.players, args.runtime_root, args.artifact_root, label=f"game{i + 1}", heroes=args.heroes)
             for i in range(args.games)]
    write_json(args.artifact_root / "result.json", {"variant": args.variant, "players": args.players,
                                                    "build_report": report, "games": games})
    print(json.dumps([(g["label"], g["status"], g.get("error")) for g in games], ensure_ascii=False))
    return 0 if all(g["status"] == "COMPLETE" for g in games) else 2


if __name__ == "__main__":
    raise SystemExit(main())
