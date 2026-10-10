#!/usr/bin/env python3
"""H-BS0 spike ("기지가 바뀐다", 조종권 교체) on the pinned ESL 2611 EXE: can a running solo game hand the human the
controls of computer seat ``k`` and hand seat 0 to the computer, without a defeat or crash?

One run = private game copy, new Wine prefix and Xvfb, the pinned EXE unchanged (no product code).  The solo lobby is
the default 2-seat one (``--players 2``) or a 4-player map with computer rows in slots 1..2 (``--players 3``).  After
``--swap-after`` seconds in game (ps3) the variant writes:

``a``  ``[0xB63FC4] = k`` only (local seat index)
``b``  ``a`` + player ``is_cpu`` byte (``0x956770 + owner*0x3ABC + 2``): seat 0 -> 1, seat k -> 0
``c``  ``b``'s ``is_cpu`` writes + the lobby snapshot route (``0x632E0C`` copy with seat 0/k swapped, ``[0xC0D0F4]=1``)
       so the game's own refresh ``0x4B7700`` -> ``0x43AF40`` recomputes the local index (only if it runs in game)

Checks: a stale pre-swap selection of seat 0 units gets a right-click; the camera (``0xB42D7C``) jumps to seat k's
start tile, a drag selects, a right-click must re-target the selected seat-k units; the same at seat 0's start; then
``--observe`` seconds of 5 s samples (ps, local, ``is_cpu``, resources, AI controller words, units per owner,
units the lose check counts).  Win/lose (``0x4C4040``): lose when no live unit with ``flags & 0x4002`` has
owner == local (timer ``0x975910``), win when no such unit of another team (timer ``0x97590C``); both 2 s later.
Start tiles: ``0xB3DE58 + i*0x338`` (x, y dwords; filled by ``0x42FB50`` from the map list ``0xB42D38``/count
``0xB42D78``).
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import time
from typing import Any, Callable, cast

from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from patches.population.runtime_driver import write as write_memory
from tools import esl2610_runtime, runtime_env
from tools import g6_shift_click_probe as g6
from tools.g5_candidate_drag_probe import ProbeError, capture, sha256, write_json

REPO = Path(__file__).resolve().parents[1]
VARIANTS = ("a", "b", "c")
LOCAL_INDEX_VA = 0xB63FC4
PLAYER_BASE, PLAYER_STRIDE, IS_CPU_OFFSET = 0x956770, 0x3ABC, 0x2
CAMERA_VA = 0xB42D7C  # camera centre tile (x, y dwords); writing it moves the view
START_TABLE_VA, START_STRIDE = 0xB3DE58, 0x338
MAP_START_LIST_VA, MAP_START_COUNT_VA = 0xB42D38, 0xB42D78
WIN_TIMER_VA, LOSE_TIMER_VA = 0x97590C, 0x975910
POOL, EXISTS, POOL_CAP, UNIT_STRIDE = 0x66B790, 0x8990C8, 1200, 0x758
UNIT_FLAGS_OFFSET, LOSE_CHECK_FLAGS = 0x1D8, 0x4002
UNIT_PENDING_XY_OFFSET = 0x388
LOBBY_TABLE_VA, ROWS_OFFSET, DWORD_OFFSET = 0x632C9C, 0x24, 0x54
# Solo lobby map list (observed lap ESL2611 G8/G9 exploration): down arrow, first row, 30 scrolls -> first 4-player map
MAP_LIST_DOWN, MAP_ROW0, MAP_SCROLLS_4P = (748, 298), (520, 122), 30
VIEW_DRAG = ((200, 120), (790, 470))
CENTER_DRAG = ((270, 130), (570, 370))  # around the tile the camera is centred on
MOVE_POINT = (300, 380)
SAMPLE_SECONDS = 5.0
GRACE_SECONDS = 25.0  # production queued by the AI before the swap may still finish
PS_INGAME = 3


def is_cpu_va(owner: int) -> int:
    return PLAYER_BASE + owner * PLAYER_STRIDE + IS_CPU_OFFSET


def swap_writes(variant: str, seat: int) -> list[tuple[int, bytes]]:
    """Memory writes of one variant (``c`` leaves the local index to the game's lobby refresh)."""
    if variant not in VARIANTS:
        raise ProbeError(f"unsupported variant: {variant}")
    if not 0 < seat < 8:
        raise ProbeError(f"seat outside 1..7: {seat}")
    local = [(LOCAL_INDEX_VA, seat.to_bytes(4, "little"))]
    ai = [(is_cpu_va(0), b"\x01"), (is_cpu_va(seat), b"\x00")]
    return {"a": local, "b": local + ai, "c": ai}[variant]


def owner_summary(rows: list[dict[str, int]]) -> dict[int, dict[str, int]]:
    """Units per owner and the ones the lose check ``0x4448E0`` counts (``flags & 0x4002``)."""
    out: dict[int, dict[str, int]] = {}
    for row in rows:
        entry = out.setdefault(row["owner"], {"units": 0, "qualifying": 0})
        entry["units"] += 1
        entry["qualifying"] += int(bool(row["flags"] & LOSE_CHECK_FLAGS))
    return dict(sorted(out.items()))


def spawned(before: list[dict[str, int]], after: list[dict[str, int]], owner: int) -> int:
    known = {(r["slot"], r["type"]) for r in before}
    return sum(1 for r in after if r["owner"] == owner and (r["slot"], r["type"]) not in known)


def moved(before: list[dict[str, int]], after: list[dict[str, int]], owner: int) -> int:
    old = {(r["slot"], r["type"]): (r["x"], r["y"]) for r in before if r["owner"] == owner}
    return sum(1 for r in after if r["owner"] == owner and (r["slot"], r["type"]) in old
               and old[(r["slot"], r["type"])] != (r["x"], r["y"]))


def pick_mobile(before: list[dict[str, int]], after: list[dict[str, int]], now: list[dict[str, int]],
                owner: int) -> dict[str, int] | None:
    """Current row of an ``owner`` unit that moved between ``before`` and ``after`` (a unit that can take MOVE)."""
    old = {(r["slot"], r["type"]): (r["x"], r["y"]) for r in before if r["owner"] == owner}
    went = {(r["slot"], r["type"]) for r in after if r["owner"] == owner
            and (r["slot"], r["type"]) in old and old[(r["slot"], r["type"])] != (r["x"], r["y"])}
    return next((r for r in now if (r["slot"], r["type"]) in went), None)


def clockwise_order(starts: dict[int, tuple[int, int]]) -> list[int]:
    """Seats in screen-clockwise order (tile y grows downward) around the start centroid, beginning at seat 0."""
    cx = sum(p[0] for p in starts.values()) / len(starts)
    cy = sum(p[1] for p in starts.values()) / len(starts)
    angle = {seat: math.atan2(y - cy, x - cx) for seat, (x, y) in starts.items()}
    first = angle[min(starts)]
    return sorted(starts, key=lambda seat: (angle[seat] - first) % (2 * math.pi))


def rotation_map(order: list[int]) -> dict[int, int]:
    """Seat -> the next seat clockwise (whose units that seat's controller receives on a rotation)."""
    return {seat: order[(i + 1) % len(order)] for i, seat in enumerate(order)}


def classify_end(ps: int, lose_timer: int, win_timer: int, qualifying_local: int) -> str:
    if ps == PS_INGAME and not lose_timer and not win_timer:
        return "running"
    if lose_timer:
        return "defeat_legit" if qualifying_local == 0 else "defeat_spurious"
    if win_timer:
        return "victory"
    return "ended_unknown"


def run_verdict(m: dict[str, Any]) -> str:
    """FEASIBLE = control moved, game kept its rules, seat 0 now AI, seat k AI stopped; PARTIAL = control only."""
    if m["end"] in ("defeat_spurious", "ended_unknown") or m["local_after"] != m["seat"] or not m["human_control"]:
        return "BLOCKED"
    if m["seat0_ai_active"] and m["seat_k_ai_stopped"]:
        return "FEASIBLE"
    return "PARTIAL"


def _rows(pid: int) -> list[dict[str, int]]:
    exists = read_memory(pid, EXISTS, POOL_CAP * 2)
    rows = []
    for slot in range(1, POOL_CAP):
        if exists[slot * 2:slot * 2 + 2] == b"\0\0":
            continue
        u = read_memory(pid, POOL + slot * UNIT_STRIDE, UNIT_STRIDE)
        hp = struct.unpack_from("<i", u, 0xB4)[0]
        if hp <= 0:
            continue
        rows.append({"slot": slot, "owner": u[0x8E], "type": u[0x8D], "hp": hp,
                     "x": struct.unpack_from("<h", u, 0x2A2)[0], "y": struct.unpack_from("<h", u, 0x2A4)[0],
                     "flags": struct.unpack_from("<I", u, UNIT_FLAGS_OFFSET)[0],
                     "pending": struct.unpack_from("<I", u, UNIT_PENDING_XY_OFFSET)[0]})
    return rows


def run_probe(variant: str, seat: int, players: int, swap_after: float, observe: float,
              runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    swap_writes(variant, seat)
    if not 1 <= seat < players:
        raise ProbeError(f"seat {seat} is not a computer seat of a {players}-player game")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    exe = esl2610_runtime.ESL2610_EXE.read_bytes()
    if sha256(esl2610_runtime.ESL2610_EXE) != esl2610_runtime.ESL2610_SHA256:
        raise ProbeError("ESL2611 EXE SHA mismatch")
    manifest, overlay = esl2610_runtime.prepare(exe, runtime_root)
    game = Path(cast(str, manifest["game"]["root"]))  # type: ignore[index]
    prefix = Path(cast(str, manifest["wine"]["prefix"]))  # type: ignore[index]
    private_exe = game / runtime_env.ORIGINAL_EXE
    result: dict[str, Any] = {
        "schema": "syw2plus.bs0-seat-swap-probe.v1", "status": "UNKNOWN", "variant": variant, "seat": seat,
        "players": players, "swap_after": swap_after, "observe": observe,
        "provenance": {"private_exe_sha256": sha256(private_exe), "overlay_files": len(overlay)},
        "samples": [], "checks": {}, "captures": [],
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    display = ""
    origin = (0, 0)
    pid = 0
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

        def u(va: int, size: int = 4, signed: bool = False) -> int:
            return int.from_bytes(read_memory(pid, va, size), "little", signed=signed)

        def click(x: int, y: int, *, button: int = 1, drag_to: tuple[int, int] | None = None) -> None:
            args = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(origin[0] + x), str(origin[1] + y), "--button", str(button)]
            if drag_to is not None:
                args += ["--drag-to", str(origin[0] + drag_to[0]), str(origin[1] + drag_to[1])]
            subprocess.run(args, env=env, stdout=log, stderr=log, timeout=10, check=True)

        def shot(label: str) -> None:
            path = artifact_root / f"{time.strftime('%Y%m%d_%H%M%S')}_{label}.png"
            capture(display, path, log)
            result["captures"].append(path.name)

        def selection() -> list[dict[str, int]]:
            count = u(esl2610_runtime.SELECTION_COUNT_VA, 4, True)
            if not 0 <= count <= esl2610_runtime.SELECTION_CAPACITY:
                raise ProbeError(f"selection count outside range: {count}")
            slots = [u(esl2610_runtime.SELECTION_ENTRIES_VA + i * 4) & 0xFFF for i in range(count)]
            return [{"slot": s, "owner": u(POOL + s * UNIT_STRIDE + 0x8E, 1), "type": u(POOL + s * UNIT_STRIDE + 0x8D, 1),
                     "pending": u(POOL + s * UNIT_STRIDE + UNIT_PENDING_XY_OFFSET)} for s in slots]

        def camera_to(xy: tuple[int, int]) -> None:
            write_memory(pid, CAMERA_VA, struct.pack("<ii", *xy))
            time.sleep(1.0)

        def command_test(label: str, at: tuple[int, int], *, select: bool = True,
                         box: tuple[tuple[int, int], tuple[int, int]] = CENTER_DRAG) -> dict[str, Any]:
            """Optionally drag-select the view, right-click MOVE_POINT, report which selected units re-targeted."""
            camera_to(at)
            if select:
                click(*box[0], drag_to=box[1])
                time.sleep(0.8)
            before = selection()
            click(*MOVE_POINT, button=3)
            time.sleep(0.6)
            targets = Counter(now for e in before
                              if (now := u(POOL + e["slot"] * UNIT_STRIDE + UNIT_PENDING_XY_OFFSET)) != e["pending"])
            shot(label)
            return {"camera": list(at), "selected": before, "owners": dict(Counter(e["owner"] for e in before)),
                    "retargeted": sum(targets.values()),
                    "target": hex(targets.most_common(1)[0][0]) if targets else None}

        def sample(label: str, rows: list[dict[str, int]]) -> dict[str, Any]:
            s = read_state(pid)
            summary = owner_summary(rows)
            local = u(LOCAL_INDEX_VA)
            out = {"label": label, "t": round(time.monotonic() - t0, 1), "ps": s["ps"], "tick": s["tick"],
                   "local": local, "alive": game_proc.poll() is None,
                   "win_timer": u(WIN_TIMER_VA), "lose_timer": u(LOSE_TIMER_VA),
                   "players": [{k: p[k] for k in ("owner", "nation", "ai", "rice", "wood", "used", "controller_opcode",
                                                  "controller_argument")} for p in s["players"][:players]],
                   "owners": {str(k): v for k, v in summary.items()},
                   "types": {str(o): dict(sorted(Counter(r["type"] for r in rows if r["owner"] == o).items()))
                             for o in range(players)}}
            return out

        # ---------------- lobby -> game
        wait_for(lambda s: s.get("ps") == 9, "ps9")
        time.sleep(2)
        outer, content = runtime_env._game_window_ids(runtime_env._window_tree(display, 10))
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        origin = (int(info["x"]), int(info["y"]))
        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        time.sleep(1)
        if players > 2:
            for _ in range(MAP_SCROLLS_4P):
                click(*MAP_LIST_DOWN)
                time.sleep(0.4)
            click(*MAP_ROW0)
            time.sleep(1)
            table = bytearray(read_memory(pid, LOBBY_TABLE_VA, 0x170))
            for slot in range(2, players):
                table[ROWS_OFFSET + slot * 6:ROWS_OFFSET + slot * 6 + 6] = bytes([5, slot, 1, 1 << slot, 0, slot])
                struct.pack_into("<I", table, DWORD_OFFSET + slot * 4, 1)
            write_memory(pid, LOBBY_TABLE_VA, bytes(table))
        result["lobby_rows"] = [read_memory(pid, LOBBY_TABLE_VA + ROWS_OFFSET + i * 6, 6).hex() for i in range(8)]
        shot("lobby")
        click(608, 564)
        wait_for(lambda s: s.get("ps") == PS_INGAME and int(s.get("tick", 0)) > 0, "ps3", 90)
        t0 = time.monotonic()
        starts = {i: (u(START_TABLE_VA + i * START_STRIDE, 4, True), u(START_TABLE_VA + i * START_STRIDE + 4, 4, True))
                  for i in range(players)}
        order = clockwise_order(starts)
        result["start_tiles"] = {str(k): list(v) for k, v in starts.items()}
        result["map_start_list"] = [list(struct.unpack_from("<ii", read_memory(pid, MAP_START_LIST_VA, 64), i * 8))
                                    for i in range(u(MAP_START_COUNT_VA))]
        result["clockwise_order"] = order
        result["rotation_map"] = {str(k): v for k, v in rotation_map(order).items()}
        rows0 = _rows(pid)
        result["samples"].append(sample("start", rows0))
        shot("start")
        while time.monotonic() - t0 < swap_after:
            time.sleep(SAMPLE_SECONDS)
            result["samples"].append(sample("pre", _rows(pid)))
        rows_pre_end = _rows(pid)
        result["checks"]["pre_swap_seat_k_spawned"] = spawned(rows0, rows_pre_end, seat)
        # stale selection: seat 0 units selected before the swap
        camera_to(starts[0])
        click(*VIEW_DRAG[0], drag_to=VIEW_DRAG[1])
        time.sleep(0.8)
        stale = selection()

        # ---------------- swap
        writes = swap_writes(variant, seat)
        for va, data in writes:
            write_memory(pid, va, data)
        result["writes"] = [[hex(va), data.hex()] for va, data in writes]
        if variant == "c":
            raw = read_memory(pid, g6.LOBBY_TABLE_VA, g6.LOBBY_TABLE_SIZE)
            snapshot, ids = g6.build_lobby_snapshot(raw, seat, u(g6.LOBBY_OWN_ID_VA))
            write_memory(pid, g6.LOBBY_SNAPSHOT_VA, snapshot)
            write_memory(pid, g6.LOBBY_REFRESH_FLAG_VA, (1).to_bytes(4, "little"))
            deadline = time.monotonic() + 5
            while u(g6.LOBBY_REFRESH_FLAG_VA) != 0 and time.monotonic() < deadline:
                time.sleep(0.1)
            consumed = u(g6.LOBBY_REFRESH_FLAG_VA) == 0
            if not consumed:
                write_memory(pid, g6.LOBBY_REFRESH_FLAG_VA, (0).to_bytes(4, "little"))
            result["lobby_route"] = {"ids": ids, "refresh_consumed": consumed, "local_after": u(LOCAL_INDEX_VA)}
        t_swap = time.monotonic()
        rows_swap = _rows(pid)
        result["samples"].append(sample("swap", rows_swap))
        result["checks"]["stale_selection"] = {**command_test("stale_seat0_after_swap", starts[0], select=False),
                                               "selected_before_swap": len(stale)}
        now = _rows(pid)
        for owner, name in ((seat, "seat_k_command"), (0, "seat0_command")):
            unit = pick_mobile(rows0, rows_pre_end, now, owner)
            at = (unit["x"], unit["y"]) if unit else starts[owner]
            result["checks"][name] = {**command_test(name, at), "aimed_unit": unit}
        camera_to(starts[seat])
        rows_grace: list[dict[str, int]] | None = None
        rows_end = rows_swap
        while time.monotonic() - t_swap < observe:
            time.sleep(SAMPLE_SECONDS)
            rows_end = _rows(pid)
            if rows_grace is None and time.monotonic() - t_swap >= GRACE_SECONDS:
                rows_grace = rows_end
            s = sample("post", rows_end)
            result["samples"].append(s)
            if s["ps"] != PS_INGAME or not s["alive"]:
                break
        shot("end_seat_k")
        camera_to(starts[0])
        shot("end_seat0")
        last = result["samples"][-1]
        post = [s for s in result["samples"] if s["label"] in ("swap", "post")]

        def rice_spent(owner: int, after_t: float = 0.0) -> bool:
            seq = [s["players"][owner]["rice"] for s in post if s["t"] >= after_t]
            return any(b < a for a, b in zip(seq, seq[1:]))

        grace_t = post[0]["t"] + GRACE_SECONDS
        c = result["checks"]
        c["seat0_spawned"] = spawned(rows_swap, rows_end, 0)
        c["seat0_moved"] = moved(rows_swap, rows_end, 0)
        c["seat0_rice_spent"] = rice_spent(0)
        c["seat_k_spawned_after_grace"] = spawned(rows_grace, rows_end, seat) if rows_grace else None
        c["seat_k_rice_spent_after_grace"] = rice_spent(seat, grace_t)
        c["seat_k_controller_after"] = [last["players"][seat]["controller_opcode"],
                                        last["players"][seat]["controller_argument"]]
        k_cmd = c["seat_k_command"]
        # units are cleared on the result screen: judge the lose check on the last in-game sample
        ingame = [s for s in post if s["ps"] == PS_INGAME] or post
        local_q = ingame[-1]["owners"].get(str(ingame[-1]["local"]), {}).get("qualifying", 0)
        c["last_ingame_local_qualifying"] = local_q
        measures = {
            "end": classify_end(last["ps"], last["lose_timer"], last["win_timer"], local_q),
            "local_after": last["local"], "seat": seat,
            "human_control": bool(k_cmd["selected"]) and set(k_cmd["owners"]) == {seat} and k_cmd["retargeted"] > 0,
            "seat0_ai_active": c["seat0_spawned"] > 0 or c["seat0_rice_spent"],
            "seat_k_ai_stopped": c["seat_k_spawned_after_grace"] == 0 and not c["seat_k_rice_spent_after_grace"],
        }
        result["measures"] = measures
        result["verdict"] = run_verdict(measures)
        result["status"] = "COMPLETE"
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError, IndexError, StopIteration,
            runtime_env.RuntimeSafetyError) as exc:
        result["status"] = "FAIL"
        result["error"] = f"{type(exc).__name__}: {exc}"
        if display:
            capture(display, artifact_root / f"{time.strftime('%Y%m%d_%H%M%S')}_failure.png", log)
    finally:
        result["game_alive_before_cleanup"] = bool(children) and children[-1].poll() is None
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
        subprocess.run(["wineserver", "-w"], env=kill_env, stdout=log, stderr=log, timeout=30, check=False)
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
    parser.add_argument("--seat", type=int, default=1)
    parser.add_argument("--players", type=int, choices=(2, 3), default=3)
    parser.add_argument("--swap-after", type=float, default=20.0)
    parser.add_argument("--observe", type=float, default=75.0)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.variant, args.seat, args.players, args.swap_after, args.observe,
                       args.runtime_root, args.artifact_root)
    print(json.dumps({"status": result.get("status"), "verdict": result.get("verdict"), "error": result.get("error")},
                     ensure_ascii=False))
    return 0 if result.get("status") == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
