#!/usr/bin/env python3
"""Paired DxWnd window/profile and camera-scroll probe for ESL2608 G2.

The probe copies the read-only DxWnd bundle and the complete game into a
fresh runtime.  It never edits the source game or the two delivered EXEs.
Each case runs the same generated profile through DxWnd's ``/r:1`` target,
then measures the 800x600 window, arrow-key camera movement, and pointer-at-
edge camera movement.  The candidate lane uses the delivered filename in the
profile so a missing filename profile is observable rather than inferred.
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

from patches.population.runtime_driver import read as read_memory  # noqa: E402
from patches.population.runtime_driver import state as read_state  # noqa: E402
from tools import runtime_env  # noqa: E402
from tools.g2_esl2608_phase_a_shift_probe import (  # noqa: E402
    BASE_SOURCE,
    DATA_OVERLAY,
    EXPECTED_BASELINE,
    LANES,
)
from tools.g5_candidate_drag_probe import ProbeError, write_json  # noqa: E402

INPUT_ROOT = REPO.parent / "260921_temp"
DXWND_SOURCE = REPO.parent / "Syw2plus" / "dxwnd_backup"
DXWND_EXE = "dxwnd.exe"
CAMERA_ADDRESS = 0x00B42D7C
WINDOW_SIZE = (800, 600)
SCREEN = "1600x1200x24"
EDGE_POINT = (795, 300)
ARROW_KEYS = ("Right", "Down", "Left", "Up")
TARGET_FILENAMES = {
    "normal": "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092.exe",
    "fixed_start": "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092.exe",
}
TARGET_SHA = {
    "normal": "83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60",
    "fixed_start": "1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f",
}


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _win_path(path: Path) -> str:
    # Wine's Z: mapping is stable for the private absolute paths used here.
    return "Z:" + str(path.resolve()).replace("/", "\\")


def _copy_overlay(game: Path) -> list[dict[str, str]]:
    copied: list[dict[str, str]] = []
    for source in sorted(DATA_OVERLAY.rglob("*")):
        if source.is_symlink() or not source.is_file() or source.suffix.lower() in {".exe", ".xlsx"}:
            continue
        target = game / source.relative_to(DATA_OVERLAY)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(source.relative_to(DATA_OVERLAY)), "sha256": _digest(target)})
    return copied


def _profile(bundle: Path, game: Path, target: Path, *, title: str,
             bundle_win_path: str | None = None, target_win_path: str | None = None) -> Path:
    """Create a single-target profile from the read-only known-good template."""
    template = DXWND_SOURCE / "dxwnd.ini"
    if not template.is_file():
        raise ProbeError(f"DxWnd bundle template missing: {template}")
    text = template.read_text(encoding="latin-1")
    # Keep only the [window] section and target 0 from the template.  The
    # target flags are the historical Syw2plus windowed profile; the size is
    # deliberately 800x600 so edge scroll is measured without scaling.
    window = text.split("[target]", 1)[0]
    target_lines = text.split("[target]", 1)[1].split("title2=", 1)[0]
    replacements = {
        "exepath": bundle_win_path or _win_path(bundle),
        "title0": title,
        "path0": target_win_path or _win_path(target),
        "startfolder0": _win_path(game),
        "launchpath0": target_win_path or _win_path(target),
        "posx0": "50",
        "posy0": "50",
        "sizx0": str(WINDOW_SIZE[0]),
        "sizy0": str(WINDOW_SIZE[1]),
        "initresw0": "800",
        "initresh0": "600",
    }

    def replace_line(line: str) -> str:
        key, sep, value = line.partition("=")
        if sep and key in replacements:
            return f"{key}={replacements[key]}"
        return line

    profile = bundle / "dxwnd.ini"
    profile.write_text(
        "\n".join(replace_line(line) for line in (window + "[target]\n" + target_lines).splitlines()) + "\n",
        encoding="latin-1",
        errors="replace",
    )
    # DxWnd persists its target state on startup.  A copied profile must be
    # writable inside the owned prefix; a Z: profile can trigger the GUI's
    # "No write capability" warning even when the host file is writable.
    profile.chmod(0o600)
    return profile


def _camera(pid: int) -> list[int]:
    raw = read_memory(pid, CAMERA_ADDRESS, 8)
    return [int.from_bytes(raw[0:4], "little", signed=True), int.from_bytes(raw[4:8], "little", signed=True)]


def _wait(pid: int, predicate: Any, label: str, timeout: float = 45) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            last = read_state(pid)
            if predicate(last):
                return last
        except (OSError, ValueError, ProbeError) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.25)
    raise ProbeError(f"{label} timeout; last={last}")


def _find_target_pid(prefix: Path, target: Path, timeout: float = 30) -> int:
    """Resolve the Win32 target, not the DxWnd launcher, for memory reads."""
    needle = target.name.encode()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        candidates = set(runtime_env._prefix_pids(prefix))
        # DxWnd can create the Win32 target through a Wine server process that
        # does not preserve WINEPREFIX in /proc/environ.  The exact target
        # basename is unique to this private run, so this fallback remains
        # bounded and cannot attach to an unrelated game.
        try:
            candidates.update(int(item.name) for item in Path("/proc").iterdir() if item.name.isdigit())
        except OSError:
            pass
        for candidate in sorted(candidates):
            try:
                cmdline = Path(f"/proc/{candidate}/cmdline").read_bytes()
            except OSError:
                continue
            if needle in cmdline and b"dxwnd.exe" not in cmdline.lower():
                return candidate
        time.sleep(0.25)
    diagnostics: list[str] = []
    for candidate in sorted(runtime_env._prefix_pids(prefix)):
        try:
            diagnostics.append(f"{candidate}:{Path(f'/proc/{candidate}/cmdline').read_bytes()!r}")
        except OSError:
            pass
    raise ProbeError(f"DxWnd target PID not found for {target.name}; prefix_processes={diagnostics}")


def _window(display: str, log: Any) -> tuple[str, dict[str, int]]:
    tree = runtime_env._window_tree(display, 10)
    candidates = runtime_env._game_window_candidates(tree)
    if not candidates:
        raise ProbeError("DxWnd produced no 800x600 game window")
    window_id, width, height = candidates[0]
    details = runtime_env._xwininfo_details(display, window_id, 10)
    return window_id, {"x": int(details["x"]), "y": int(details["y"]), "width": width, "height": height}


def run_probe(lane: str, variant: str, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if lane not in LANES or variant not in {"baseline", "candidate"}:
        raise ProbeError(f"unsupported lane/variant: {lane}/{variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    if not DXWND_SOURCE.is_dir():
        raise ProbeError(f"read-only DxWnd source missing: {DXWND_SOURCE}")
    baseline_path = LANES[lane]
    if _digest(baseline_path) != EXPECTED_BASELINE[lane]:
        raise ProbeError("baseline source SHA mismatch")
    candidate_path = INPUT_ROOT / TARGET_FILENAMES[lane]
    if variant == "candidate" and _digest(candidate_path) != TARGET_SHA[lane]:
        raise ProbeError("delivered candidate SHA mismatch")
    artifact_root = artifact_root.resolve()
    artifact_root.mkdir(parents=True)
    result: dict[str, Any] = {
        "schema": "syw2plus.g2-esl2608-dxwnd-scroll.v1",
        "status": "UNKNOWN", "lane": lane, "variant": variant,
        "profile_target_filename": TARGET_FILENAMES[lane] if variant == "candidate" else runtime_env.ORIGINAL_EXE,
        "source": {"baseline_path": str(baseline_path), "baseline_sha256": _digest(baseline_path)},
        "inputs": [], "stages": {}, "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    game_proc: Any = None
    game: Path | None = None
    prefix: Path | None = None
    try:
        manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, timeout=90)
        game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
        prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
        _copy_overlay(game)
        if variant == "candidate":
            target = game / TARGET_FILENAMES[lane]
            shutil.copy2(candidate_path, target)
            target_sha = TARGET_SHA[lane]
        else:
            target = game / runtime_env.ORIGINAL_EXE
            target_sha = runtime_env.ORIGINAL_SHA256
        if _digest(target) != target_sha:
            raise ProbeError("private profile target SHA mismatch")
        bundle_artifact = artifact_root / "dxwnd"
        shutil.copytree(DXWND_SOURCE, bundle_artifact, symlinks=False)
        bundle = prefix / "drive_c" / "dxwnd"
        shutil.copytree(DXWND_SOURCE, bundle, symlinks=False)
        # Keep the target executable on the same C: volume as DxWnd.  The
        # game data remains in the runtime game copy via startfolder0; this
        # avoids legacy DxWnd path matching failures for Wine's Z: drive.
        profile_target = bundle / target.name
        shutil.copy2(target, profile_target)
        if _digest(profile_target) != target_sha:
            raise ProbeError("private C: profile target SHA mismatch")
        profile = _profile(bundle, game, target, title=f"G2 ESL2608 {lane} {variant}",
                           bundle_win_path="C:\\dxwnd\\",
                           target_win_path=f"C:\\dxwnd\\{target.name}")
        profile_artifact = bundle_artifact / "dxwnd.ini"
        shutil.copy2(profile, profile_artifact)
        result["provenance"] = {
            "private_run_dir": str(Path(cast(str, cast(Mapping[str, Any], manifest["output"])["run_dir"]))),
            "private_game": str(game), "private_prefix": str(prefix),
            "private_target_sha256": _digest(target), "profile": str(profile),
            "profile_artifact": str(profile_artifact), "profile_sha256": _digest(profile),
            "dxwnd_exe_sha256": _digest(bundle_artifact / DXWND_EXE),
            "dxwnd_dll_sha256": _digest(bundle / "dxwnd.dll"),
        }
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
        xvfb, display = runtime_env._xvfb(log, SCREEN)
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=bundle, env=env, stdout=log, stderr=log))
        time.sleep(1)
        profile_arg = r"/c:C:\dxwnd\dxwnd.ini"
        game_proc = subprocess.Popen(["wine", r"C:\dxwnd\dxwnd.exe", profile_arg, "/r:1"],
                                     cwd=bundle, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = _find_target_pid(prefix, target)
        result["provenance"]["dxwnd_launcher_pid"] = game_proc.pid
        result["provenance"]["target_pid"] = pid
        _wait(pid, lambda state: state.get("ps") == 9, "dxwnd_game_ps9", 60)
        window_id, info = _window(display, log)
        result["stages"]["windowed"] = {"window_id": window_id, **info,
                                        "size_pass": (info["width"], info["height"]) == WINDOW_SIZE,
                                        "profile_target_exists": target.is_file()}
        subprocess.run(["xdotool", "windowfocus", window_id], env=env, stdout=log, stderr=log, check=True, timeout=10)
        before = _camera(pid)
        key_records: list[dict[str, Any]] = []
        for key in ARROW_KEYS:
            subprocess.run(["xdotool", "key", "--clearmodifiers", key], env=env,
                           stdout=log, stderr=log, check=True, timeout=10)
            time.sleep(0.5)
            after = _camera(pid)
            key_records.append({"key": key, "before": before, "after": after,
                                "delta": [after[0] - before[0], after[1] - before[1]]})
            before = after
        edge_before = _camera(pid)
        edge_x = info["x"] + info["width"] - 2
        edge_y = info["y"] + info["height"] // 2
        subprocess.run(["xdotool", "mousemove", str(edge_x), str(edge_y)], env=env,
                       stdout=log, stderr=log, check=True, timeout=10)
        time.sleep(2.0)
        edge_after = _camera(pid)
        result["inputs"].append({"kind": "edge_pointer", "root": [edge_x, edge_y]})
        result["stages"]["scroll"] = {
            "keyboard": key_records, "keyboard_moved": any(item["delta"] != [0, 0] for item in key_records),
            "edge": {"before": edge_before, "after": edge_after,
                      "delta": [edge_after[0] - edge_before[0], edge_after[1] - edge_before[1]],
                      "moved": edge_after != edge_before},
        }
        result["stages"]["process"] = {"tick": read_state(pid).get("tick"), "exit_before_cleanup": game_proc.poll()}
        result["status"] = "PASS" if result["stages"]["windowed"]["size_pass"] and result["stages"]["scroll"]["keyboard_moved"] and result["stages"]["scroll"]["edge"]["moved"] else "FAIL"
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
        if prefix is not None:
            cleanup_env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
            subprocess.run(["wineserver", "-k"], env=cleanup_env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=cleanup_env, stdout=log, stderr=log, timeout=10, check=False)
            result["cleanup"]["prefix_processes_after"] = runtime_env._prefix_pids(prefix)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            xvfb.wait(timeout=5)
        if game is not None and game.exists():
            shutil.rmtree(game)
        result["cleanup"]["game_removed"] = game is None or not game.exists()
        result["source"]["baseline_unchanged"] = _digest(baseline_path) == EXPECTED_BASELINE[lane]
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
                      "variant": args.variant, "error": result.get("error")}, ensure_ascii=False))
    return 0 if result.get("status") == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
