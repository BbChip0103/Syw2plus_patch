#!/usr/bin/env python3
"""Paired isolated display probe for official ESL2614 with G1 WINMM routing."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any

from tools import esl2614_runtime, g1_saved_scene_probe as probe, runtime_env


REPO = Path(__file__).resolve().parents[1]
DEFAULT_HD = (REPO.parent / "temp" / "Syw2plus_patch" /
              "20261013_lap1281_work_hdsingle" / "native_layout_repaired_r1")
EXCLUDED_2614_HD = {
    "fnt/portrait_plus_hd.spr", "fnt/button_plus_hd.Spr",
    *(f"tile/{name}/castle2_hd.ytl" for name in
      ("bright", "dark", "green", "normal", "brown", "volcano", "snow")),
}


def lane_passed(row: dict[str, Any], *, case: str, soak_seconds: int = 0) -> bool:
    if not row.get("private_game_copy_removed_after_run"):
        return False
    if row.get("status") != "PASS":
        return False
    trace_close = row.get("trace_close")
    trace_summary = row.get("trace_summary")
    if not (
        isinstance(trace_close, dict) and trace_close.get("status") == "PASS"
        and isinstance(trace_summary, dict) and trace_summary.get("status") == "PASS"
    ):
        return False
    if case != "soak":
        return True
    play = row.get("new_game_play")
    if not (
        isinstance(play, dict)
        and play.get("status") == "PASS"
        and isinstance(play.get("present_summary"), dict)
        and play["present_summary"].get("status") == "PASS"
    ):
        return False
    dwell = (
        play.get("present_summary", {}).get("windows", {}).get("dwell")
        if isinstance(play, dict) else None
    )
    return (
        isinstance(dwell, dict)
        and dwell.get("unexpected_states") == []
        and isinstance(dwell.get("observed_seconds"), (int, float))
        and dwell["observed_seconds"] >= soak_seconds
    )


def soak_ps3_coverage(row: dict[str, Any], *, requested_seconds: int) -> dict[str, Any]:
    play = row.get("new_game_play")
    dwell = (
        play.get("present_summary", {}).get("windows", {}).get("dwell")
        if isinstance(play, dict) else None
    )
    if not isinstance(dwell, dict):
        return {"status": "FAIL", "requested_seconds": requested_seconds,
                "observed_seconds": 0.0, "reason": "missing_dwell_window"}
    observed = dwell.get("observed_seconds")
    status = "PASS" if (
        isinstance(observed, (int, float))
        and observed >= requested_seconds
        and dwell.get("unexpected_states") == []
    ) else "FAIL"
    return {
        "status": status,
        "requested_seconds": requested_seconds,
        "observed_seconds": observed,
        "presents": dwell.get("presents"),
        "total_presents": dwell.get("total_presents"),
        "by_state": dwell.get("by_state"),
        "unexpected_states": dwell.get("unexpected_states"),
    }


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def filtered_hd(source: Path, output: Path) -> dict[str, Any]:
    if not source.is_dir() or source.is_symlink() or output.exists():
        raise ValueError("HD input must be a real directory and filtered output must be new")
    output.mkdir(parents=True)
    copied = 0
    removed: list[str] = []
    for item in sorted(source.rglob("*")):
        if item.is_symlink():
            raise ValueError(f"linked HD input refused: {item}")
        if not item.is_file():
            continue
        rel = item.relative_to(source).as_posix()
        if rel in EXCLUDED_2614_HD:
            removed.append(rel)
            continue
        target = output / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
        copied += 1
    if set(removed) != EXCLUDED_2614_HD:
        raise ValueError(f"2614 source-change exclusion mismatch: removed={sorted(removed)}")
    return {"source": str(source.resolve()), "filtered": str(output.resolve()),
            "files": copied, "excluded_2614_changed_assets": sorted(removed)}


def run_lane(*, candidate: bool, case: str, hd: Path, runtime_parent: Path,
             artifact_parent: Path, close_helper: Path,
             soak_seconds: int = 0, install_proxy: bool | None = None,
             native_ddraw: bool = False,
             no_virtual_desktop: bool = False) -> dict[str, Any]:
    probe.ESL2614 = True
    proxy_installed = candidate if install_proxy is None else install_proxy
    probe.ESL2614_G1_ENABLED = proxy_installed
    variant = "candidate" if candidate else "baseline"
    runtime_root = runtime_parent / case / variant
    artifact_root = artifact_parent / case / variant
    new_game = case in {"new_game", "soak"}
    probe.NEW_GAME_PLAY_OVERRIDE.clear()
    if case == "soak":
        probe.NEW_GAME_PLAY_OVERRIDE.update({"keys": (), "hold": 0,
                                             "dwell": float(soak_seconds),
                                             "dwell_captures": 3})
    result = probe._run_lane(
        variant=variant, bridge=None, runtime_root=runtime_root,
        artifact_root=artifact_root, close_helper=close_helper,
        new_game_path=new_game, new_game_start=new_game,
        new_game_play=(case == "soak"), hd_source="scale2x" if candidate else None,
        native_ddraw=native_ddraw, no_virtual_desktop=no_virtual_desktop,
        hd_sidecar_layout=hd if candidate else None, fixture="save006",
        scene_actions="none", display_only=True,
        performance_window=(case == "save006"), lane_label=f"g1-esl2614-{case}-{variant}",
    )
    private_game = Path(str(result.get("private_game", ""))).resolve()
    run_dir = private_game.parent
    expected_runtime = runtime_root.resolve()
    if private_game.name != "game" or run_dir.parent != expected_runtime:
        raise runtime_env.RuntimeSafetyError("refusing to remove an unexpected private game path")
    if runtime_env._prefix_pids(Path(result["private_prefix"])):
        raise runtime_env.RuntimeSafetyError("private Wine prefix still owns a process after lane cleanup")
    if private_game.exists():
        shutil.rmtree(private_game)
    result["private_game_copy_removed_after_run"] = not private_game.exists()
    result["esl2614_exe_sha256"] = esl2614_runtime.ESL2614_SHA256
    result["g1_winmm_installed"] = proxy_installed
    result["g1_winmm_sha256"] = sha256(esl2614_runtime.G1_WINMM) if proxy_installed else None
    drive_c = Path(result["private_prefix"]) / "drive_c"
    proxy_logs: dict[str, Any] = {}
    for name in ("inmm_stub.log", "inmm_mci_log.jsonl", "inmm_state_log.jsonl",
                 "inmm_asset_log.jsonl", "g1_hd_key.jsonl"):
        log = drive_c / name
        raw = log.read_bytes() if log.is_file() else b""
        text = raw.decode("utf-8", errors="replace")
        proxy_logs[name] = {
            "path": str(log), "exists": log.is_file(),
            "sha256": hashlib.sha256(raw).hexdigest() if log.is_file() else None,
            "bytes": len(raw), "lines": len(text.splitlines()),
            "g1_initialized": "polling worker started" in text,
            "mci_play_rows": sum("MCI_PLAY" in row or "msg=0x806" in row for row in text.splitlines()),
            "hd_asset_open_rows": sum("_hd." in row.lower() for row in text.splitlines()),
        }
    result["proxy_logs"] = proxy_logs
    if case == "soak":
        result["soak_ps3_coverage"] = soak_ps3_coverage(result, requested_seconds=soak_seconds)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hd-layout", type=Path, default=DEFAULT_HD)
    parser.add_argument("--runtime-parent", type=Path, required=True)
    parser.add_argument("--artifact-parent", type=Path, required=True)
    parser.add_argument("--soak-seconds", type=int, default=0)
    parser.add_argument("--soak-only", action="store_true")
    parser.add_argument("--mci-pair-seconds", type=int, default=0,
                        help="run matched G1-off/on new-game observation with WINMM proxy in both lanes")
    parser.add_argument("--force-music", action="store_true",
                        help="private diagnostic fixture: set INMM_STUB_FORCE_MUSIC_ON=1")
    parser.add_argument("--startup-only", action="store_true",
                        help="run one candidate new-game startup lane; requires a user-shaped startup option")
    parser.add_argument("--candidate-native-ddraw", action="store_true",
                        help="candidate only: load app-local ddraw.dll (ASI Loader/plugins) with ddraw=n,b;winmm=n,b")
    parser.add_argument("--candidate-no-virtual-desktop", action="store_true",
                        help="candidate only: launch without Wine's /desktop wrapper to exercise mode-switch failure")
    args = parser.parse_args()
    if args.mci_pair_seconds and args.soak_seconds:
        parser.error("--mci-pair-seconds and --soak-seconds are mutually exclusive")
    if args.startup_only and not (args.candidate_native_ddraw or args.candidate_no_virtual_desktop):
        parser.error("--startup-only requires --candidate-native-ddraw and/or --candidate-no-virtual-desktop")
    if args.startup_only and (args.soak_only or args.soak_seconds or args.mci_pair_seconds):
        parser.error("--startup-only cannot be combined with soak or MCI-pair modes")
    if not args.startup_only and (args.candidate_native_ddraw or args.candidate_no_virtual_desktop):
        parser.error("user-shaped startup options require --startup-only")
    esl2614_runtime.verify_source()
    if args.force_music:
        os.environ["INMM_STUB_FORCE_MUSIC_ON"] = "1"
    runtime_parent = args.runtime_parent.resolve()
    artifact_parent = args.artifact_parent.resolve()
    if runtime_parent.exists() or artifact_parent.exists():
        parser.error("runtime and artifact parent paths must be new")
    runtime_parent.mkdir(parents=True)
    artifact_parent.mkdir(parents=True)
    filtered = filtered_hd(args.hd_layout.resolve(), artifact_parent / "_hd_2614_safe")
    helper_dir = artifact_parent / "close_helper"
    import subprocess
    subprocess.run([sys.executable, "-m", "tools.win32_close_fixture", "build",
                    "--out-dir", str(helper_dir)], cwd=REPO, check=True)
    close_helper = helper_dir / "win32_close_helper.exe"
    rows: list[dict[str, Any]] = []
    if args.startup_only:
        rows.append(run_lane(candidate=True, case="new_game", hd=Path(filtered["filtered"]),
                             runtime_parent=runtime_parent,
                             artifact_parent=artifact_parent,
                             close_helper=close_helper,
                             native_ddraw=args.candidate_native_ddraw,
                             no_virtual_desktop=args.candidate_no_virtual_desktop))
    elif args.mci_pair_seconds:
        if not 30 <= args.mci_pair_seconds <= 180:
            parser.error("--mci-pair-seconds must be in [30, 180]")
        for candidate in (False, True):
            rows.append(run_lane(candidate=candidate, case="soak", hd=Path(filtered["filtered"]),
                                 runtime_parent=runtime_parent,
                                 artifact_parent=artifact_parent,
                                 close_helper=close_helper,
                                 soak_seconds=args.mci_pair_seconds,
                                 install_proxy=True))
    elif not args.soak_only:
        for case in ("new_game", "save006"):
            for candidate in (False, True):
                rows.append(run_lane(candidate=candidate, case=case, hd=Path(filtered["filtered"]),
                                     runtime_parent=runtime_parent,
                                     artifact_parent=artifact_parent,
                                     close_helper=close_helper))
    if args.soak_seconds:
        if not 60 <= args.soak_seconds <= 540:
            parser.error("--soak-seconds must be in [60, 540] to remain within one runner call")
        rows.append(run_lane(candidate=True, case="soak", hd=Path(filtered["filtered"]),
                             runtime_parent=runtime_parent,
                             artifact_parent=artifact_parent,
                             close_helper=close_helper,
                             soak_seconds=args.soak_seconds))
    source_after, exe_after = esl2614_runtime.verify_source()
    row_cases = (
        [("new_game", row) for row in rows[:2]]
        + [("save006", row) for row in rows[2:4]]
        + [("soak", row) for row in rows[4:]]
        if args.startup_only else (
            [("soak", row) for row in rows] if args.soak_only else
            [("new_game", row) for row in rows[:2]]
            + [("save006", row) for row in rows[2:4]]
            + [("soak", row) for row in rows[4:]]
        )
    )
    if args.mci_pair_seconds:
        row_cases = [("soak", row) for row in rows]
        off, on = rows
        off_mci = off.get("proxy_logs", {}).get("inmm_mci_log.jsonl")
        on_mci = on.get("proxy_logs", {}).get("inmm_mci_log.jsonl")
        mci_pair = {
            "observation_seconds": args.mci_pair_seconds,
            "same_exe_sha256": off.get("esl2614_exe_sha256") == on.get("esl2614_exe_sha256"),
            "same_proxy_sha256": off.get("g1_winmm_sha256") == on.get("g1_winmm_sha256"),
            "off_mci_log": off_mci,
            "on_mci_log": on_mci,
            "off_render_disabled": off.get("variant_config", {}).get("w60_mirror") is False,
            "on_render_enabled": on.get("variant_config", {}).get("w60_mirror") is True,
        }
        mci_pair["status"] = "PASS" if (
            mci_pair["same_exe_sha256"] and mci_pair["same_proxy_sha256"]
            and off_mci and off_mci.get("exists") and on_mci and on_mci.get("exists")
            and mci_pair["off_render_disabled"] and mci_pair["on_render_enabled"]
        ) else "HOLD"
    else:
        mci_pair = None
    summary = {"schema": "syw2plus.g1-esl2614-display.v1", "status": "PASS" if rows and all(
        lane_passed(row, case=case, soak_seconds=(args.mci_pair_seconds or args.soak_seconds))
        for case, row in row_cases) and sha256(exe_after) == esl2614_runtime.ESL2614_SHA256
        and (mci_pair is None or mci_pair["status"] == "PASS") else "HOLD",
        "source_root": str(source_after), "source_exe_sha256": sha256(exe_after),
        "g1_winmm_sha256": sha256(esl2614_runtime.G1_WINMM),
        "forced_music_fixture": args.force_music,
        "mci_pair": mci_pair,
        "filtered_hd": filtered, "lanes": rows,
        "scope": "Wine isolated display/runtime evidence only; no Windows, milestone, or multiplayer approval",
    }
    result_path = artifact_parent / "g1-esl2614-result.json"
    result_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": summary["status"], "result": str(result_path),
                      "lanes": [row.get("status") for row in rows]}, ensure_ascii=False))
    return 0 if summary["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
