#!/usr/bin/env python3
"""G1 x ESL2608 R5 combination probe (isolated Wine; never touches the inputs).

Modes (each run = private game copy, new Wine prefix, empty Xvfb; no G1 environment variable is set):

``g1``       the staged ``..._R5_G1.exe`` (import name ``_G1MM.dll``) next to the staged ``_G1MM.dll``; the copied
             game folder keeps its original ``_inmm.dll`` (coexistence).
``plain``    the unmodified R5 EXE in the same folder as ``_G1MM.dll`` (control: stock ``_inmm.dll`` must load,
             the game must run at 800x600, no G1 trace).
``env``      the unmodified R5 EXE, the lap1151 ``_inmm.dll`` and the four G1 variables (earlier bundle design).

Per run: window size, DLL install log, PS9 -> lobby (PS7/PS5) -> new game -> PS3 with a dwell, captures, and a
drag-select / minimap-click input check read from game memory.  Results are JSON; no outcome is invented.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any, Callable, Mapping

REPO = Path(__file__).resolve().parents[1]
TEMP_ROOT = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch")
CAPTURES = TEMP_ROOT / "captures"
SCHEMA = "syw2plus.g1-r5-combo-probe.v1"
MODES = ("g1", "plain", "env")
LANES = ("normal", "fixed_start")
R5_SHA256 = {
    "normal": "b582fb1969e8e08076cc69ef93bd99669f65baefebfb9e4d4f88c2b8d90a2dfd",
    "fixed_start": "acf5bd3d7f4657d95cc9bc4db3621dd4184d823416719095c3b714f0f0cbf1a4",
}
G1_EXE_SHA256 = {
    "normal": "9fe0e9f367f4db03e9765a86be548770322b4aff54e449f0720f37982273aa62",
    "fixed_start": "bfddd8d8ac697efd28d415e0132343695c0b95f4f56ae45aa5a9027452fafad9",
}
G1MM_SHA256 = "05bf70105b3d653e050d7dace689e2565b200a3a6775a64bd4b2daa563ec7609"
LAP1151_DLL_SHA256 = "8a3837fb9ef97c33bf60b451bdd47ca066a7e655b482ac9c9a2b5f2b72011d5f"
G1_ENV = {"SYW2_G1_NATIVE_2X_BLIT": "1", "SYW2_G1_MIRROR2X": "1", "SYW2_G1_HD_SOURCE": "scale2x",
          "INMM_STUB_NO_UNIT_TICKS": "1"}
# primitive hook targets named by the DLL's own mirror2x_install event
HOOK_TARGETS = (0x466D50, 0x4664D0, 0x468C30, 0x468CC0, 0x468E10, 0x468F00, 0x4690A0)
SELECTION_BASE_VA = 0x018A6000  # G5 selection-50 port array (count dword, then entries)
SELECTION_CAPACITY = 50
CAMERA_VA = 0x00B42D7C
MINIMAP_POINTS = ((90, 553), (110, 545), (70, 560), (90, 535), (90, 575), (130, 555), (50, 555))
DRAG_BOX = ((30, 60), (780, 440))
STAGES = ("window", "install_log", "to_ps3", "captures", "input")


class ProbeError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_input_sha(path: Path, expected: str, label: str) -> str:
    actual = sha256_file(path)
    if actual != expected:
        raise ProbeError(f"{label} SHA mismatch: {actual} != {expected}")
    return actual


def assert_under(root: Path, path: Path) -> Path:
    """Return the resolved path only if it stays inside ``root`` (no ``..`` or symlink escape)."""
    real_root = root.resolve()
    real = path.resolve()
    if real != real_root and real_root not in real.parents:
        raise ProbeError(f"path escapes the private root {real_root}: {real}")
    return real


def capture_name(stamp: str, lane: str, mode: str, stage: str) -> str:
    return f"{stamp}_g1r5_{lane}_{mode}_{stage}.png"


def parse_trace(text: str) -> dict[str, Any]:
    """Summarise the DLL's present-trace JSONL: install result, failures, observed program states."""
    events = []
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            events.append(value)
    failed = [e for e in events if e.get("event") == "install" and e.get("install_status") == "failed"]
    skipped = [e for e in events if "skipped_old_bytes_mismatch" in json.dumps(e)]
    active = {(e.get("event"), e.get("stage")) for e in events if e.get("install_status") == "active"}
    states = sorted({e["program_state"] for e in events if isinstance(e.get("program_state"), int)})
    present = sum(1 for e in events if e.get("event") == "mirror2x_present")
    return {
        "events": len(events),
        "hook_install_active": ("mirror2x_install", "primitives") in active,
        "dd_install_active": ("install", "complete") in active,
        "install_failed": [{"stage": e.get("stage"), "reason": e.get("reason")} for e in failed],
        "skipped_old_bytes_mismatch": len(skipped),
        "program_states": states,
        "mirror2x_present_events": present,
    }


def find_game_window(tree: str, sizes: tuple[tuple[int, int], ...]) -> tuple[str, str | None, tuple[int, int]]:
    """Outer window id, same-size content child id and size from an ``xwininfo -root -tree`` dump.

    ``runtime_env._game_window_ids`` keys on the stock file name, which the staged EXE does not have.
    """
    import re

    lines = tree.splitlines()
    pattern = re.compile(r"(0x[0-9a-fA-F]+).*?\b(\d{3,4})x(\d{3,4})\+")
    for index, line in enumerate(lines):
        match = pattern.search(line)
        if not match or (int(match.group(2)), int(match.group(3))) not in sizes:
            continue
        size = (int(match.group(2)), int(match.group(3)))
        indent = len(line) - len(line.lstrip())
        for inner in lines[index + 1:]:
            if len(inner) - len(inner.lstrip()) <= indent:
                break
            sub = pattern.search(inner)
            if sub and (int(sub.group(2)), int(sub.group(3))) == size:
                return match.group(1), sub.group(1), size
        return match.group(1), None, size
    raise ProbeError(f"no game window with size in {sizes}")


def hooks_patched(first_bytes: Mapping[int, int]) -> bool:
    """Every hook target starts with a ``jmp rel32`` (0xE9) once the primitives are installed."""
    return set(first_bytes) == set(HOOK_TARGETS) and all(v == 0xE9 for v in first_bytes.values())


def stage_verdict(name: str, result: Mapping[str, Any], mode: str) -> str:
    g1_expected = mode in {"g1", "env"}
    if name == "window":
        size = result.get("window", {}).get("size")
        return "PASS" if size == ([1600, 1200] if g1_expected else [800, 600]) else "FAIL"
    if name == "install_log":
        info = result.get("install_log", {})
        if not g1_expected:
            return "PASS" if info.get("events", 0) == 0 and not info.get("hooks_patched") else "FAIL"
        ok = (info.get("hook_install_active") and info.get("dd_install_active") and not info.get("install_failed")
              and info.get("skipped_old_bytes_mismatch") == 0 and info.get("hooks_patched"))
        return "PASS" if ok else "FAIL"
    if name == "to_ps3":
        info = result.get("to_ps3", {})
        return "PASS" if info.get("reached_ps3") and info.get("alive_at_end") else "FAIL"
    if name == "captures":
        caps = result.get("captures", {})
        return "PASS" if caps and all(c.get("returncode") == 0 for c in caps.values()) else "FAIL"
    if name == "input":
        info = result.get("input", {})
        return info.get("status", "SKIP")
    raise ProbeError(f"unknown stage {name}")


def validate_result(result: Mapping[str, Any]) -> list[str]:
    """Schema problems of a finished result (empty list = well formed)."""
    problems = []
    if result.get("schema") != SCHEMA:
        problems.append("schema")
    if result.get("mode") not in MODES:
        problems.append("mode")
    if result.get("lane") not in LANES:
        problems.append("lane")
    if result.get("status") not in {"PASS", "FAIL", "ERROR"}:
        problems.append("status")
    verdicts = result.get("verdicts")
    if not isinstance(verdicts, dict) or set(verdicts) != set(STAGES) or any(
            v not in {"PASS", "FAIL", "SKIP"} for v in verdicts.values()):
        problems.append("verdicts")
    for key in ("provenance", "cleanup"):
        if not isinstance(result.get(key), dict):
            problems.append(key)
    return problems


# --------------------------------------------------------------------------------------------------------------
# runtime part (needs Wine/Xvfb; exercised by running the probe, not by unit tests)
# --------------------------------------------------------------------------------------------------------------


def _wait_state(read_state: Callable[[], dict[str, Any]], predicate: Callable[[dict[str, Any]], bool],
                label: str, timeout: float = 60.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            last = read_state()
            if predicate(last):
                return last
        except (OSError, ValueError) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.25)
    raise ProbeError(f"{label} timeout; last={last}")


def run_probe(lane: str, mode: str, runtime_root: Path, artifact_root: Path, inputs: Mapping[str, Path],
              *, dwell: float = 30.0) -> dict[str, Any]:
    from patches.population import runtime_driver
    from tools import runtime_env

    if lane not in LANES or mode not in MODES:
        raise ProbeError(f"unsupported lane/mode: {lane}/{mode}")
    artifact_root.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    r5 = inputs[f"r5_{lane}"]
    g1_exe = inputs[f"g1_{lane}"]
    provenance: dict[str, Any] = {
        "r5_sha256": check_input_sha(r5, R5_SHA256[lane], "R5 EXE"),
        "g1mm_sha256": check_input_sha(inputs["g1mm"], G1MM_SHA256, "_G1MM.dll"),
        "g1_exe_sha256": check_input_sha(g1_exe, G1_EXE_SHA256[lane], "G1 EXE"),
        "lap1151_dll_sha256": check_input_sha(inputs["lap1151"], LAP1151_DLL_SHA256, "lap1151 _inmm.dll"),
    }
    result: dict[str, Any] = {
        "schema": SCHEMA, "lane": lane, "mode": mode, "status": "ERROR", "provenance": provenance,
        "env_g1_set": mode == "env", "window": {}, "install_log": {}, "to_ps3": {}, "captures": {},
        "input": {"status": "SKIP"}, "cleanup": {}, "verdicts": {}, "errors": [],
    }
    from tools.g2_esl2608_phase_a_shift_probe import BASE_SOURCE, copy_overlay

    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, timeout=90)
    run_dir = Path(str(manifest["output"]["run_dir"]))  # type: ignore[index]
    game = Path(str(manifest["game"]["root"]))  # type: ignore[index]
    prefix = Path(str(manifest["wine"]["prefix"]))  # type: ignore[index]
    for path in (run_dir, game, prefix):
        assert_under(runtime_root, path)
    copy_overlay(game)
    shutil.copy2(inputs["g1mm"], game / "_G1MM.dll")
    exe_src = g1_exe if mode == "g1" else r5
    exe_name = exe_src.name
    shutil.copy2(exe_src, game / exe_name)
    if mode == "env":
        shutil.copy2(inputs["lap1151"], game / "_inmm.dll")
    original_inmm = sha256_file(game / "_inmm.dll")
    provenance.update({"private_run_dir": str(run_dir), "game_inmm_sha256": original_inmm, "exe_name": exe_name,
                       "game_exe_sha256": sha256_file(game / exe_name)})
    log_path = artifact_root / f"{lane}_{mode}.log"
    log = log_path.open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all", LANG="ko_KR.UTF-8",
               LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
    for key in G1_ENV:
        env.pop(key, None)
    if mode == "env":
        env.update(G1_ENV)
    try:
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game, env=env,
                                         stdout=log, stderr=log))
        time.sleep(1)
        proc = subprocess.Popen(["wine", str(game / exe_name)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(proc)
        pid = proc.pid

        def state() -> dict[str, Any]:
            return runtime_driver.state(pid)

        def read(addr: int, size: int) -> bytes:
            return runtime_driver.read(pid, addr, size)

        _wait_state(state, lambda s: s.get("ps") == 9, "ps9", 90)
        tree = runtime_env._window_tree(display, 20)
        sizes = ((1600, 1200), (800, 600)) if mode != "plain" else ((800, 600),)
        try:
            outer, content, _size = find_game_window(tree, sizes)
        except ProbeError:
            result["window"] = {"tree_excerpt": tree[:3000]}
            raise
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 20)
        size = [int(info["width"]), int(info["height"])]
        origin = (int(info["x"]), int(info["y"]))
        scale = 2 if size == [1600, 1200] else 1
        result["window"] = {"size": size, "origin": list(origin), "scale": scale, "tree_excerpt": tree[:1500]}

        def shot(stage: str) -> None:
            path = assert_under(CAPTURES.parent, CAPTURES / capture_name(stamp, lane, mode, stage))
            CAPTURES.mkdir(parents=True, exist_ok=True)
            run = subprocess.run(["scrot", str(path)], env=dict(os.environ, DISPLAY=display), stdout=log,
                                 stderr=log, timeout=15, check=False)
            record: dict[str, Any] = {"path": str(path), "returncode": run.returncode}
            if run.returncode == 0 and path.is_file():
                record["sha256"] = sha256_file(path)
            result["captures"][stage] = record

        def click(x: int, y: int, *, button: int = 1, drag_to: tuple[int, int] | None = None,
                  shift: bool = False) -> None:
            args = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(origin[0] + x * scale), str(origin[1] + y * scale), "--button", str(button),
                    "--hold-ms", "120"]
            if drag_to is not None:
                args += ["--drag-to", str(origin[0] + drag_to[0] * scale), str(origin[1] + drag_to[1] * scale),
                         "--hold-ms", "150"]
            if shift:
                subprocess.run(["xdotool", "keydown", "Shift_L"], env=env, stdout=log, stderr=log, check=True)
            try:
                subprocess.run(args, env=env, stdout=log, stderr=log, timeout=15, check=True)
            finally:
                if shift:
                    subprocess.run(["xdotool", "keyup", "Shift_L"], env=env, stdout=log, stderr=log, check=False)

        time.sleep(1.0)
        shot("ps9_title")
        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=False)
        click(184, 560)
        _wait_state(state, lambda s: s.get("ps") == 7, "ps7", 30)
        time.sleep(0.5)
        shot("ps7_solo_menu")
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        _wait_state(state, lambda s: s.get("ps") == 5, "ps5", 30)
        _wait_state(state, lambda s: s.get("ps") == 5 and runtime_env._read_local_ready_state(read).get(
            "ready_value") == 1, "ready", 20)
        time.sleep(0.5)
        shot("ps5_lobby")
        click(608, 564)
        s3 = _wait_state(state, lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3", 120)
        time.sleep(5)
        shot("ps3_ingame")
        t0 = time.monotonic()
        first_tick = int(state().get("tick", 0))
        while time.monotonic() - t0 < dwell and proc.poll() is None:
            time.sleep(1)
        last = state()
        shot("ps3_dwell")
        result["to_ps3"] = {"reached_ps3": True, "tick_at_ps3": int(s3.get("tick", 0)), "tick_first": first_tick,
                            "tick_last": int(last.get("tick", 0)), "ps_last": last.get("ps"),
                            "dwell_seconds": round(time.monotonic() - t0, 1), "alive_at_end": proc.poll() is None}
        first_bytes = {addr: read(addr, 1)[0] for addr in HOOK_TARGETS}
        trace_file = prefix / "drive_c" / "inmm_g1_present_trace.jsonl"
        text = trace_file.read_text(encoding="utf-8", errors="replace") if trace_file.is_file() else ""
        summary = parse_trace(text)
        summary["hooks_patched"] = hooks_patched(first_bytes)
        summary["hook_first_bytes"] = {hex(a): hex(v) for a, v in first_bytes.items()}
        result["install_log"] = summary
        if trace_file.is_file():
            shutil.copy2(trace_file, artifact_root / f"{lane}_{mode}.trace.jsonl")
        try:
            result["input"] = _input_check(read, click, state, shot)
        except (ProbeError, OSError, subprocess.SubprocessError) as exc:
            result["input"] = {"status": "SKIP", "reason": f"{type(exc).__name__}: {exc}"}
        result["to_ps3"]["alive_after_input"] = proc.poll() is None
    except (ProbeError, runtime_env.RuntimeSafetyError, OSError, subprocess.SubprocessError, ValueError) as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")
    finally:
        result["cleanup"] = _cleanup(prefix, game, run_dir, children, xvfb, env, artifact_root, lane, mode, log)
    verdicts = {name: stage_verdict(name, result, mode) for name in STAGES}
    result["verdicts"] = verdicts
    core = ("window", "install_log", "to_ps3")
    result["status"] = "ERROR" if result["errors"] and "to_ps3" not in result else (
        "PASS" if all(verdicts[n] == "PASS" for n in core) else "FAIL")
    problems = validate_result(result)
    if problems:
        raise ProbeError(f"malformed result: {problems}")
    (artifact_root / f"{lane}_{mode}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False),
                                                       encoding="utf-8")
    return result


def _input_check(read: Callable[[int, int], bytes], click: Callable[..., None], state: Callable[[], dict[str, Any]],
                 shot: Callable[[str], None]) -> dict[str, Any]:
    """Drag-select and minimap click from the same logical points; observed only through game memory."""
    import struct

    def selection() -> list[int]:
        count = struct.unpack("<i", read(SELECTION_BASE_VA, 4))[0]
        if not 0 <= count <= SELECTION_CAPACITY:
            raise ProbeError(f"selection count out of range: {count}")
        return [v & 0xFFF for v in struct.unpack(f"<{count}I", read(SELECTION_BASE_VA + 4, 4 * count))]

    out: dict[str, Any] = {"status": "SKIP", "selection_cap_checked": False,
                           "g5_over_20_skip_reason": "no >20 unit fixture without the supply bridge (fabricating "
                                                     "units is out of scope); shift-click (G6) needs calibrated unit "
                                                     "screen positions and a non-1P seat, not measured"}
    out["selection_before"] = selection()
    click(*DRAG_BOX[0], drag_to=DRAG_BOX[1])
    time.sleep(1.0)
    out["drag_box"] = [list(DRAG_BOX[0]), list(DRAG_BOX[1])]
    out["selection_after_drag"] = selection()
    shot("ps3_after_drag")
    cam0 = struct.unpack("<2i", read(CAMERA_VA, 8))
    attempts = []
    for point in MINIMAP_POINTS:
        click(*point)
        time.sleep(1.2)
        now = struct.unpack("<2i", read(CAMERA_VA, 8))
        attempts.append({"point": list(point), "camera": list(now)})
        if list(now) != list(cam0):
            break
    shot("ps3_after_minimap")
    cam1 = struct.unpack("<2i", read(CAMERA_VA, 8))
    out.update({"camera_before": list(cam0), "camera_after_minimap": list(cam1), "ps_after": state().get("ps"),
                "minimap_attempts": attempts})
    out["drag_selected"] = len(out["selection_after_drag"]) > 0
    out["minimap_moved_camera"] = list(cam0) != list(cam1)
    # drag selection is the mapping check; the minimap result is reported next to the control run, not judged alone
    out["status"] = "PASS" if out["drag_selected"] else "FAIL"
    return out


def _cleanup(prefix: Path, game: Path, run_dir: Path, children: list[Any], xvfb: Any, env: Mapping[str, str],
             artifact_root: Path, lane: str, mode: str, log: Any) -> dict[str, Any]:
    info: dict[str, Any] = {}
    wine_env = dict(env, WINEPREFIX=str(prefix))
    try:
        subprocess.run(["wineserver", "-k"], env=wine_env, timeout=20, check=False, stdout=log, stderr=log)
        subprocess.run(["wineserver", "-w"], env=wine_env, timeout=30, check=False, stdout=log, stderr=log)
    except subprocess.SubprocessError as exc:
        info["wineserver_error"] = str(exc)
    for child in children:
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
    if xvfb is not None and xvfb.poll() is None:
        xvfb.terminate()
        try:
            xvfb.wait(timeout=5)
        except subprocess.TimeoutExpired:
            xvfb.kill()
    log.close()
    stub_log = prefix / "drive_c" / "inmm_stub.log"
    if stub_log.is_file():
        shutil.copy2(stub_log, artifact_root / f"{lane}_{mode}.inmm_stub.log")
    shutil.rmtree(game, ignore_errors=True)
    shutil.rmtree(prefix, ignore_errors=True)
    info.update({"game_removed": not game.exists(), "prefix_removed": not prefix.exists(), "run_dir": str(run_dir)})
    return info


# --------------------------------------------------------------------------------------------------------------
# relaunch: consecutive runs in ONE game copy and ONE Wine prefix (the user's "second launch" symptom)
# --------------------------------------------------------------------------------------------------------------

# "builtin": Wine's ddraw (what the other probes use); "native": the game folder's own ddraw.dll, which is what a
# Windows double-click loads (the application directory wins over system32 for a non-KnownDLL).
DDRAW_OVERRIDES = {"builtin": "ddraw=b", "native": "ddraw=n,b"}
EXIT_BUTTON = (410, 560)  # "종료하기" on the PS9 title screen, logical 800x600 coordinates
CRASH_MARKERS = ("unhandled exception", "c0000005", "page fault", "err:seh", "backtrace", "fatal", "assertion")


def snapshot_tree(root: Path) -> dict[str, tuple[int, int]]:
    """Relative path -> (size, mtime_ns) of every non-directory entry under ``root`` (symlinks not followed)."""
    out: dict[str, tuple[int, int]] = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            full = Path(base) / name
            try:
                st = full.lstat()
            except OSError:
                continue
            out[full.relative_to(root).as_posix()] = (st.st_size, st.st_mtime_ns)
    return out


def diff_snapshots(before: Mapping[str, tuple[int, int]], after: Mapping[str, tuple[int, int]]) -> dict[str, Any]:
    changed = [{"path": k, "size": [before[k][0], after[k][0]], "mtime_changed": before[k][1] != after[k][1]}
               for k in sorted(before.keys() & after.keys()) if before[k] != after[k]]
    return {"added": sorted(after.keys() - before.keys()), "removed": sorted(before.keys() - after.keys()),
            "changed": changed}


def diff_reg_text(before: str, after: str) -> dict[str, list[str]]:
    """Line-level registry diff (added/removed lines, order kept)."""
    old, new = set(before.splitlines()), set(after.splitlines())
    return {"added": [x for x in after.splitlines() if x not in old and x.strip()],
            "removed": [x for x in before.splitlines() if x not in new and x.strip()]}


def environ_has_prefix(environ: bytes, prefix: str) -> bool:
    return f"WINEPREFIX={prefix}".encode() in environ.split(b"\0")


def scan_crash_lines(text: str) -> list[str]:
    return [line.strip()[:300] for line in text.splitlines() if any(m in line.lower() for m in CRASH_MARKERS)]


def relaunch_verdict(runs: list[Mapping[str, Any]]) -> str:
    if not runs:
        return "NO_RUNS"
    if not runs[0].get("reached_ps9"):
        return "RUN1_FAILED"
    for index, run in enumerate(runs[1:], start=2):
        if not run.get("reached_ps9") or run.get("exited_early"):
            return f"REPRODUCED_RUN{index}"
    return "NOT_REPRODUCED"


def prefix_game_processes(prefix: Path, exe_name: str, proc_root: Path = Path("/proc")) -> list[dict[str, Any]]:
    """Processes of THIS prefix whose command line mentions the game EXE (read-only /proc scan)."""
    found = []
    for entry in proc_root.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            cmd = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace")
            if exe_name.lower() in cmd.lower() and environ_has_prefix((entry / "environ").read_bytes(), str(prefix)):
                found.append({"pid": int(entry.name), "cmdline": cmd[:200]})
        except OSError:
            continue
    return found


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _prefix_snapshot(game: Path, prefix: Path) -> dict[str, Any]:
    small = {f.name: f.read_bytes().hex() for f in game.iterdir() if f.is_file() and f.stat().st_size <= 1024}
    return {"game": snapshot_tree(game), "drive_c": snapshot_tree(prefix / "drive_c"), "small": small,
            "user_reg": _read_text(prefix / "user.reg"), "system_reg": _read_text(prefix / "system.reg")}


def _snapshot_diff(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    return {"game": diff_snapshots(before["game"], after["game"]),
            "drive_c": diff_snapshots(before["drive_c"], after["drive_c"]),
            "small_changed": [{"path": k, "before_hex": before["small"][k], "after_hex": after["small"][k]}
                              for k in sorted(before["small"].keys() & after["small"].keys())
                              if before["small"][k] != after["small"][k]],
            "user_reg": diff_reg_text(before["user_reg"], after["user_reg"]),
            "system_reg": diff_reg_text(before["system_reg"], after["system_reg"])}


def run_relaunch(lane: str, mode: str, runtime_root: Path, artifact_root: Path, inputs: Mapping[str, Path], *,
                 runs: int = 2, exit_method: str = "button", ingame_first: bool = False, keep_wine: bool = False,
                 drop_after_run1: tuple[str, ...] = (), readonly_after_run1: tuple[str, ...] = (),
                 ddraw: str = "builtin", tag: str = "") -> dict[str, Any]:
    """Start/stop the same EXE ``runs`` times in one game copy and one prefix; diff what each run leaves behind."""
    from patches.population import runtime_driver
    from tools import runtime_env
    from tools.g2_esl2608_phase_a_shift_probe import BASE_SOURCE, copy_overlay

    if lane not in LANES or mode not in MODES or exit_method not in {"button", "wm_close"} or ddraw not in DDRAW_OVERRIDES:
        raise ProbeError(f"unsupported lane/mode/exit: {lane}/{mode}/{exit_method}")
    artifact_root.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    exe_src = inputs[f"g1_{lane}"] if mode == "g1" else inputs[f"r5_{lane}"]
    provenance = {"exe_sha256": check_input_sha(exe_src, (G1_EXE_SHA256 if mode == "g1" else R5_SHA256)[lane], "EXE"),
                  "g1mm_sha256": check_input_sha(inputs["g1mm"], G1MM_SHA256, "_G1MM.dll")}
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, timeout=90)
    run_dir = Path(str(manifest["output"]["run_dir"]))  # type: ignore[index]
    game = Path(str(manifest["game"]["root"]))  # type: ignore[index]
    prefix = Path(str(manifest["wine"]["prefix"]))  # type: ignore[index]
    for path in (run_dir, game, prefix):
        assert_under(runtime_root, path)
    copy_overlay(game)
    shutil.copy2(inputs["g1mm"], game / "_G1MM.dll")
    exe_name = exe_src.name
    shutil.copy2(exe_src, game / exe_name)
    name = f"relaunch_{tag + '_' if tag else ''}{lane}_{mode}"
    log_path = artifact_root / f"{name}.log"
    log = log_path.open("a", encoding="utf-8")
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8",
               WINEDLLOVERRIDES=DDRAW_OVERRIDES[ddraw], WINEDEBUG="err+all,fixme-all,+seh,+loaddll,+process")
    for key in G1_ENV:
        env.pop(key, None)
    result: dict[str, Any] = {"schema": "syw2plus.g1-r5-relaunch.v1", "lane": lane, "mode": mode, "tag": tag,
                              "exit_method": exit_method, "keep_wine": keep_wine, "provenance": provenance,
                              "runs": [], "diffs": [], "errors": [], "cleanup": {}}
    xvfb: Any = None
    children: list[Any] = []
    locked: list[tuple[Path, int]] = []
    try:
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        wine_started = False
        base = _prefix_snapshot(game, prefix)
        previous = base
        for index in range(1, runs + 1):
            if not wine_started:
                children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game,
                                                 env=env, stdout=log, stderr=log))
                time.sleep(1)
                wine_started = True
            log.flush()
            offset = log_path.stat().st_size
            run = _one_relaunch_run(index, game, prefix, exe_name, env, display, log, stamp, lane, mode, tag,
                                    exit_method, ingame_first and index == 1, runtime_driver, runtime_env)
            log.flush()
            run["wine_debug_crash_lines"] = scan_crash_lines(log_path.read_bytes()[offset:].decode("utf-8", "replace"))
            run["wine_log_range"] = [offset, log_path.stat().st_size]
            stub = _read_text(prefix / "drive_c" / "inmm_stub.log").splitlines()
            run["stub_log_lines"] = len(stub)
            run["stub_log_tail"] = stub[-4:]
            run["drive_c_inmm_files"] = {k: v[0] for k, v in snapshot_tree(prefix / "drive_c").items()
                                         if "/" not in k and k.lower().startswith(("inmm_", "supply", "g1_"))}
            if not keep_wine:
                _wine_stop(prefix, env, log)
                wine_started = False
                children = [c for c in children if c.poll() is None]
            current = _prefix_snapshot(game, prefix)
            result["diffs"].append({"after_run": index, **_snapshot_diff(previous, current)})
            if index == 1:
                result["diff_baseline_to_run1"] = _snapshot_diff(base, current)
                for rel in drop_after_run1:
                    target = assert_under(run_dir, run_dir / rel)
                    if target.is_file():
                        target.unlink()
                        run.setdefault("dropped_before_next_run", []).append(rel)
                for pattern in readonly_after_run1:  # simulate files/dirs the next run cannot write
                    for target in sorted(run_dir.glob(pattern)):
                        assert_under(run_dir, target)
                        mode = target.stat().st_mode & 0o7777
                        locked.append((target, mode))
                        target.chmod(mode & ~0o222)
                        run.setdefault("readonly_before_next_run", []).append(str(target.relative_to(run_dir)))
                current = _prefix_snapshot(game, prefix)
            previous = current
            result["runs"].append(run)
            if not run.get("reached_ps9") and index == 1:
                break
    except (ProbeError, runtime_env.RuntimeSafetyError, OSError, subprocess.SubprocessError, ValueError) as exc:
        result["errors"].append(f"{type(exc).__name__}: {exc}")
    finally:
        for target, mode in reversed(locked):
            target.chmod(mode)
        result["cleanup"] = _cleanup(prefix, game, run_dir, children, xvfb, env, artifact_root, lane,
                                     f"relaunch_{mode}", log)
        result["cleanup"]["leftover_game_processes"] = prefix_game_processes(prefix, exe_name)
    result["verdict"] = relaunch_verdict(result["runs"])
    (artifact_root / f"{name}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def _wine_stop(prefix: Path, env: Mapping[str, str], log: Any) -> None:
    wine_env = dict(env, WINEPREFIX=str(prefix))
    subprocess.run(["wineserver", "-k"], env=wine_env, timeout=20, check=False, stdout=log, stderr=log)
    subprocess.run(["wineserver", "-w"], env=wine_env, timeout=30, check=False, stdout=log, stderr=log)


def _one_relaunch_run(index: int, game: Path, prefix: Path, exe_name: str, env: dict[str, str], display: str,
                      log: Any, stamp: str, lane: str, mode: str, tag: str, exit_method: str, ingame: bool,
                      runtime_driver: Any, runtime_env: Any) -> dict[str, Any]:
    rec: dict[str, Any] = {"run": index, "reached_ps9": False, "exited_early": False, "exit_code": None,
                           "window": {}, "normal_exit": None, "exit_how": None, "ps_seen": []}
    started = time.monotonic()
    proc = subprocess.Popen(["wine", str(game / exe_name)], cwd=game, env=env, stdout=log, stderr=log)
    pid = proc.pid
    deadline = started + 90
    state: dict[str, Any] = {}
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            rec["exited_early"] = True
            break
        try:
            state = runtime_driver.state(pid)
        except (OSError, ValueError):
            state = {}
        ps = state.get("ps")
        if isinstance(ps, int) and ps not in rec["ps_seen"]:
            rec["ps_seen"].append(ps)
        if ps == 9:
            rec["reached_ps9"] = True
            break
        time.sleep(0.25)
    rec["seconds_to_ps9_or_exit"] = round(time.monotonic() - started, 1)
    rec["last_state"] = {k: state.get(k) for k in ("ps", "tick")}
    if not rec["reached_ps9"]:
        rec["exit_code"] = proc.poll()
        rec["exited_early"] = proc.poll() is not None
        rec["window_tree_excerpt"] = runtime_env._window_tree(display, 10)[:1500]
        if proc.poll() is None:  # never reached the title and still alive: stop only this run's launcher
            proc.terminate()
        return rec

    def shot(stage: str) -> None:
        path = CAPTURES / f"{stamp}_g1r5_relaunch{'_' + tag if tag else ''}_{lane}_{mode}_run{index}_{stage}.png"
        CAPTURES.mkdir(parents=True, exist_ok=True)
        subprocess.run(["scrot", str(path)], env=dict(os.environ, DISPLAY=display), stdout=log, stderr=log,
                       timeout=15, check=False)
        rec.setdefault("captures", {})[stage] = str(path)

    tree = runtime_env._window_tree(display, 20)
    try:
        outer, content, size = find_game_window(tree, ((1600, 1200), (800, 600)))
        info = runtime_env._xwininfo_details(display, content or outer, 20)
        origin = (int(info["x"]), int(info["y"]))
        rec["window"] = {"size": list(size), "origin": list(origin)}
    except ProbeError as exc:
        rec["window"] = {"error": str(exc), "tree_excerpt": tree[:1500]}
        outer, origin, size = None, (0, 0), (800, 600)
    scale = 2 if size == (1600, 1200) else 1

    def click(x: int, y: int) -> None:
        subprocess.run([sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                        str(origin[0] + x * scale), str(origin[1] + y * scale), "--button", "1", "--hold-ms", "120"],
                       env=env, stdout=log, stderr=log, timeout=15, check=True)

    def read_state() -> dict[str, Any]:
        return runtime_driver.state(pid)

    time.sleep(1.0)
    shot("ps9_title")
    if outer:
        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=False)
    if ingame:
        click(184, 560)
        _wait_state(read_state, lambda s: s.get("ps") == 7, "ps7", 30)
        time.sleep(0.5)
        click(462, 169)
        time.sleep(0.5)
        click(608, 564)
        _wait_state(read_state, lambda s: s.get("ps") == 5, "ps5", 30)
        _wait_state(read_state, lambda s: s.get("ps") == 5 and runtime_env._read_local_ready_state(
            lambda a, n: runtime_driver.read(pid, a, n)).get("ready_value") == 1, "ready", 20)
        time.sleep(0.5)
        click(608, 564)
        _wait_state(read_state, lambda s: s.get("ps") == 3 and int(s.get("tick", 0)) > 0, "ps3", 120)
        time.sleep(8)
        shot("ps3_ingame")
        exit_method = "wm_close"  # the title exit button is only valid at PS9
    rec["exit_method_used"] = exit_method
    if exit_method == "button":
        click(*EXIT_BUTTON)
        rec["exit_how"] = "title_exit_button"
    else:
        subprocess.run(["wine", "taskkill", "/im", exe_name], env=env, stdout=log, stderr=log, timeout=30,
                       check=False)
        rec["exit_how"] = "wm_close_via_taskkill"
    try:
        proc.wait(timeout=30)
        rec["normal_exit"] = True
    except subprocess.TimeoutExpired:
        rec["normal_exit"] = False
        shot("exit_timeout")
        subprocess.run(["wine", "taskkill", "/im", exe_name], env=env, stdout=log, stderr=log, timeout=30,
                       check=False)
        rec["exit_how"] += "+taskkill_fallback"
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.terminate()
            rec["exit_how"] += "+terminate"
    rec["exit_code"] = proc.poll()
    for _ in range(20):
        if not prefix_game_processes(prefix, exe_name):
            break
        time.sleep(0.5)
    rec["leftover_after_exit"] = prefix_game_processes(prefix, exe_name)
    return rec


def default_inputs() -> dict[str, Path]:
    temp = REPO.parent / "260921_temp"
    tail = "_G2_개인500_공용4092_G5_선택50_G6G7_세이브자리수정R5"
    head = "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000"
    stage = TEMP_ROOT / "20261007_g1r5_combo" / "user_test_staging"
    names = {"normal": head + tail, "fixed_start": head + "_시작자리고정" + tail}
    out = {"lap1151": temp / "G1_1600x1200_시험판_20261007_lap1151" / "_inmm.dll", "g1mm": stage / "_G1MM.dll"}
    for lane, name in names.items():
        out[f"r5_{lane}"] = temp / "archive" / f"{name}.exe"
        out[f"g1_{lane}"] = stage / f"{name}_G1.exe"
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=LANES, required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--relaunch", type=int, default=0, help="N>=2: N consecutive runs in one game copy/prefix")
    parser.add_argument("--exit-method", choices=("button", "wm_close"), default="button")
    parser.add_argument("--ingame-first", action="store_true", help="relaunch: run 1 goes solo -> PS3 before exit")
    parser.add_argument("--keep-wine", action="store_true", help="relaunch: keep wineserver alive between runs")
    parser.add_argument("--drop-after-run1", action="append", default=[], metavar="REL",
                        help="relaunch: delete this file (relative to the private run dir) before run 2")
    parser.add_argument("--readonly-after-run1", action="append", default=[], metavar="GLOB",
                        help="relaunch: chmod a-w these paths (glob, relative to the private run dir) before run 2")
    parser.add_argument("--ddraw", choices=("builtin", "native"), default="builtin",
                        help="relaunch: builtin Wine ddraw or the game folder's native ddraw.dll")
    parser.add_argument("--tag", default="")
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--dwell", type=float, default=30.0)
    args = parser.parse_args(argv)
    sys.path.insert(0, str(REPO))
    if args.relaunch:
        rel = run_relaunch(args.lane, args.mode, args.runtime_root, args.artifact_root, default_inputs(),
                           runs=args.relaunch, exit_method=args.exit_method, ingame_first=args.ingame_first,
                           keep_wine=args.keep_wine, drop_after_run1=tuple(args.drop_after_run1),
                           readonly_after_run1=tuple(args.readonly_after_run1), ddraw=args.ddraw,
                           tag=args.tag)
        print(json.dumps({"verdict": rel["verdict"], "errors": rel["errors"],
                          "runs": [{k: r.get(k) for k in ("run", "reached_ps9", "exited_early", "exit_code",
                                                          "normal_exit", "exit_how")} for r in rel["runs"]]},
                         ensure_ascii=False))
        return 0
    result = run_probe(args.lane, args.mode, args.runtime_root, args.artifact_root, default_inputs(),
                       dwell=args.dwell)
    print(json.dumps({k: result[k] for k in ("lane", "mode", "status", "verdicts", "errors")}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
