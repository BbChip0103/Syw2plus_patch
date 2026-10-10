#!/usr/bin/env python3
"""Wine runtime check of ``patches/ai/shop_table_sync_2608.py`` (cave executes).

Builds the sync candidate from the pinned R5 normal EXE into the artifact
directory, then edits ONE row of the old 2608 AI table (``0x004EC514``) in a
"marker" copy.  The ``.shopai`` working copy keeps the original bytes, so the
only way ``.shopai`` row *i* can become equal to the edited old row at runtime
is the hooked selector (``0x00406C70``) copying the old table over it.

``candidate`` = sync candidate + marker; ``control`` = unhooked R5 + marker
(``.shopai`` row must stay original).  Each run owns a private game copy, Wine
prefix and Xvfb, starts a normal game and samples both tables for ``--window``
seconds.  Inputs and the protected ``260921_temp`` EXEs are only read.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Mapping, cast

# ruff: noqa: E402
REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from patches.ai import shop_table_sync_2608 as sync_patch
from patches.population.g2_esl2608_runtime_layout import ESL2608_LAYOUT
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools import runtime_env
from tools.g2_esl2608_phase_a_shift_probe import BASE_SOURCE, copy_overlay
from tools.g5_candidate_drag_probe import ProbeError, capture, sha256, write_json

R5_NORMAL = REPO.parent / "260921_temp" / "archive" / (
    "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000"
    "_G2_개인500_공용4092_G5_선택50_G6G7_세이브자리수정R5.exe"
)
ROW = sync_patch.TABLE_STRIDE
APPENDED_ROWS = 3
# Row 0 is building 0x31 producing 0x17; its siblings in the same building
# produce 0x25 / 0x3f.  Swapping to 0x25 keeps the row valid for play.
MARKER_FIELD = 4  # produce_kind (i16) offset inside the row
MARKER_NEW_VALUE = 0x0025
CRASH_WORDS = ("Program Error", "Unhandled", "winedbg", "has stopped", "Wine Crash")


def marker_edit(source: bytes, row: int = 0) -> tuple[bytes, dict[str, Any]]:
    """Return ``(edited, info)`` with old-table row ``row`` changed in one field."""

    if not 0 <= row < sync_patch.ROW_COUNT:
        raise ValueError(f"row outside old table: {row}")
    start = sync_patch.OLD_TABLE_FILE_OFFSET + row * ROW
    original = bytes(source[start : start + ROW])
    edited = bytearray(original)
    edited[MARKER_FIELD : MARKER_FIELD + 2] = MARKER_NEW_VALUE.to_bytes(2, "little")
    if bytes(edited) == original:
        raise ValueError("marker would not change the row")
    out = bytearray(source)
    out[start : start + ROW] = edited
    shopai = sync_patch.SHOPAI_FILE_OFFSET + row * ROW
    if bytes(out[shopai : shopai + ROW]) != original:
        raise ValueError(".shopai row does not start equal to the unedited old row")
    return bytes(out), {"row": row, "file_offset": start, "original": original.hex(),
                        "marker": bytes(edited).hex()}


def split_snapshot(shopai: bytes) -> dict[str, bytes]:
    """Split a ``.shopai`` payload read (146 rows + sentinel) into its parts."""

    if len(shopai) != sync_patch.SHOPAI_PAYLOAD_LEN:
        raise ValueError(f".shopai payload length {len(shopai)}")
    rows_end = sync_patch.COPY_LEN
    tail_end = rows_end + APPENDED_ROWS * ROW
    return {"rows": shopai[:rows_end], "appended": shopai[rows_end:tail_end],
            "sentinel": shopai[tail_end:]}


def judge_sample(shopai: bytes, old: bytes, row: int, original: bytes, base_tail: bytes) -> dict[str, Any]:
    """Compare one memory sample with the expectations for ``row``."""

    parts = split_snapshot(shopai)
    mine = parts["rows"][row * ROW : (row + 1) * ROW]
    old_row = old[row * ROW : (row + 1) * ROW]
    return {
        "shopai_row": mine.hex(),
        "shopai_equals_old": mine == old_row,
        "shopai_equals_original": mine == original,
        "rows_all_equal_old": parts["rows"] == old,
        "tail_unchanged": parts["appended"] + parts["sentinel"] == base_tail,
    }


def verdict(variant: str, samples: list[dict[str, Any]], alive: bool, crash: bool) -> dict[str, Any]:
    """Pass/fail with honest handling of 'selector never ran in the window'."""

    if not samples:
        return {"status": "FAIL", "reason": "no samples"}
    synced = [s for s in samples if s["shopai_equals_old"]]
    tail_ok = all(s["tail_unchanged"] for s in samples)
    base = {"alive": alive, "crash_dialog": crash, "tail_unchanged": tail_ok,
            "samples": len(samples), "first_sync_t": synced[0]["t"] if synced else None}
    if not alive or crash or not tail_ok:
        return {**base, "status": "FAIL", "reason": "game died, crash dialog, or appended rows/sentinel changed"}
    if variant == "candidate":
        if synced:
            return {**base, "status": "PASS", "reason": "cave copied the edited old row into .shopai"}
        return {**base, "status": "INCONCLUSIVE",
                "reason": "game alive but the AI never called the selector in the window"}
    if synced:
        return {**base, "status": "FAIL", "reason": "unhooked control changed .shopai"}
    return {**base, "status": "PASS", "reason": "control kept the original .shopai row"}


def _read_tables(pid: int) -> tuple[bytes, bytes]:
    return (read_memory(pid, sync_patch.SHOPAI_VA, sync_patch.SHOPAI_PAYLOAD_LEN),
            read_memory(pid, sync_patch.OLD_TABLE_VA, sync_patch.COPY_LEN))


def run_probe(variant: str, row: int, window: float, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if variant not in {"candidate", "control"}:
        raise ProbeError(f"unsupported variant: {variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = R5_NORMAL.read_bytes()
    source_sha = sha256(R5_NORMAL)
    hooked, report = sync_patch.build_candidate(source)
    exe_bytes, marker = marker_edit(hooked if variant == "candidate" else source, row)
    build_dir = artifact_root / "build"
    build_dir.mkdir()
    built_exe = build_dir / f"r5_{variant}_marker{row}.exe"
    built_exe.write_bytes(exe_bytes)
    parts = split_snapshot(exe_bytes[sync_patch.SHOPAI_FILE_OFFSET :
                                     sync_patch.SHOPAI_FILE_OFFSET + sync_patch.SHOPAI_PAYLOAD_LEN])
    base_tail = parts["appended"] + parts["sentinel"]
    original_row = bytes.fromhex(marker["original"])
    expected_old = exe_bytes[sync_patch.OLD_TABLE_FILE_OFFSET : sync_patch.OLD_TABLE_FILE_OFFSET + sync_patch.COPY_LEN]

    bridge_dir = artifact_root / "bridge"
    subprocess.run([sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
                    "--out-dir", str(bridge_dir), "--unit-pool-capacity", str(ESL2608_LAYOUT.capacity),
                    "--unit-pool-base", hex(ESL2608_LAYOUT.unit_pool_base)],
                   cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    if sha256(private_exe) != runtime_env.ORIGINAL_SHA256:
        raise ProbeError("private source copy SHA mismatch before install")
    overlay = copy_overlay(game)
    private_exe.write_bytes(exe_bytes)
    result: dict[str, Any] = {
        "schema": "syw2plus.ai-shop-table-sync-probe.v1", "status": "UNKNOWN", "variant": variant,
        "window_seconds": window, "marker": marker,
        "provenance": {"source": str(R5_NORMAL), "source_sha256": source_sha,
                        "built_exe": str(built_exe), "private_exe_sha256": sha256(private_exe),
                        "private_game": str(game), "private_prefix": str(prefix),
                        "overlay_files": len(overlay), "bridge_sha256": sha256(bridge),
                        "sync_report": report},
        "stages": {}, "samples": [], "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    game_proc: Any = None
    display = ""
    alive = False
    crash = False
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

        def wait_for(pred: Any, label: str, timeout: float = 45) -> None:
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
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda s: s.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        origin = (int(info["x"]), int(info["y"]))

        def click(x: int, y: int) -> None:
            subprocess.run([sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                            str(origin[0] + x), str(origin[1] + y), "--button", "1"],
                           env=env, stdout=log, stderr=log, timeout=10, check=True)

        # Initial memory (menu): .shopai must still hold the unedited row.
        shopai0, old0 = _read_tables(pid)
        result["stages"]["menu"] = {**judge_sample(shopai0, old0, row, original_row, base_tail),
                                    "old_row": old0[row * ROW:(row + 1) * ROW].hex()}
        if old0 != expected_old:
            raise ProbeError("old table in memory differs from the edited EXE bytes")
        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda s: s.get("ps") == 7, "ps7")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 5, "ps5")
        wait_for(lambda s: s.get("ps") == 5 and runtime_env._read_local_ready_state(
            lambda a, n: read_memory(pid, a, n)).get("ready_value") == 1, "ready", 15)
        click(608, 564)
        wait_for(lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3")
        start = read_state(pid)
        result["stages"]["start"] = {"tick": start["tick"], "players": [
            {k: p[k] for k in ("owner", "nation", "ai", "count")} for p in start["players"]]}

        t0 = time.monotonic()
        while time.monotonic() - t0 < window:
            sample: dict[str, Any] = {"t": round(time.monotonic() - t0, 1)}
            try:
                shopai, old = _read_tables(pid)
                sample.update(judge_sample(shopai, old, row, original_row, base_tail))
                sample["tick"] = read_state(pid)["tick"]
            except (OSError, ValueError) as exc:
                sample["error"] = f"{type(exc).__name__}: {exc}"
            if game_proc.poll() is not None:
                break
            if "error" not in sample:
                result["samples"].append(sample)
            tree_text = str(runtime_env._window_tree(display, 5))
            crash = crash or any(word in tree_text for word in CRASH_WORDS)
            time.sleep(2)
        alive = game_proc.poll() is None
        result["stages"]["end"] = {"alive": alive, "tick": result["samples"][-1].get("tick") if result["samples"] else None}
        capture(display, artifact_root / f"{time.strftime('%Y%m%d_%H%M%S')}_final.png", log)
        result["verdict"] = verdict(variant, result["samples"], alive, crash)
        result["status"] = result["verdict"]["status"]
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
        cleanup_env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
        subprocess.run(["wineserver", "-k"], env=cleanup_env, stdout=log, stderr=log, timeout=10, check=False)
        subprocess.run(["wineserver", "-w"], env=cleanup_env, stdout=log, stderr=log, timeout=10, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=5)
        result["cleanup"] = {"prefix_processes_after": runtime_env._prefix_pids(prefix), "game_removed": False}
        if game.exists():
            shutil.rmtree(game)
        result["cleanup"]["game_removed"] = not game.exists()
        result["source_sha_unchanged"] = sha256(R5_NORMAL) == source_sha
        write_json(artifact_root / "probe-result.json", result)
        log.close()
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("candidate", "control"), required=True)
    parser.add_argument("--row", type=int, default=0)
    parser.add_argument("--window", type=float, default=180.0)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.variant, args.row, args.window, args.runtime_root, args.artifact_root)
    print(json.dumps({"status": result.get("status"), "variant": args.variant,
                      "verdict": result.get("verdict"), "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
