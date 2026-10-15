#!/usr/bin/env python3
"""Run a display-only G1 on/off comparison on official ESL 2613 or a pinned variant."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from tools import esl2613_runtime, g1_saved_scene_probe as probe, runtime_env


REPO = Path(__file__).resolve().parents[1]
VARIANTS = {
    "g2_g6_g8": (
        REPO.parent / "260921_temp" / "[ESL]Syw2plus 2613_G2_G6_G8.exe",
        "1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d",
    ),
    "g2_g6_g8_g9": (
        REPO.parent / "260921_temp" / "[ESL]Syw2plus 2613_G2_G6_G8_G9_자리고정.exe",
        "b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556",
    ),
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def run(args: argparse.Namespace) -> dict[str, Any]:
    exe = args.variant_exe.resolve() if args.variant_exe else None
    dll = args.default_on_dll.resolve()
    hd_layout = args.hd_layout.resolve()
    artifact_root = args.artifact_root.resolve()
    runtime_root = args.runtime_root.resolve()
    if args.variant not in ("official", *VARIANTS):
        raise SystemExit(f"unsupported variant: {args.variant}")
    expected_sha = esl2613_runtime.ESL2613_SHA256 if args.variant == "official" else VARIANTS[args.variant][1]
    if args.variant == "official":
        if exe is not None:
            raise SystemExit("official target uses the pinned runtime source; do not pass --variant-exe")
    else:
        expected_path, expected_sha = VARIANTS[args.variant]
        if exe is None or exe != expected_path.resolve() or digest(exe) != expected_sha:
            raise SystemExit("variant EXE path/SHA does not match the pinned read-only input")
    if not dll.is_file() or not hd_layout.is_dir():
        raise SystemExit("default-on DLL or HD layout is missing")
    if artifact_root.exists() or runtime_root.exists():
        raise SystemExit("output/runtime path already exists")
    artifact_root.mkdir(parents=True)
    runtime_root.mkdir(parents=True)

    original_prepare = probe._prepare_lane_game

    def prepare_target(runtime_dir: Path, _bridge: Path | None, *, esl2613: bool | None = None):
        manifest = original_prepare(runtime_dir, None, esl2613=True)
        game = Path(manifest["game"]["root"])
        if exe is not None:
            private_exe = game / runtime_env.ORIGINAL_EXE
            shutil.copy2(exe, private_exe)
        shutil.copy2(dll, game / "_inmm.dll")
        return manifest

    probe.ESL2613 = True
    probe._prepare_lane_game = prepare_target
    close_dir = artifact_root / "close_helper"
    subprocess.run(
        [sys.executable, "-m", "tools.win32_close_fixture", "build",
         "--out-dir", str(close_dir)], cwd=REPO, check=True,
    )
    close_helper = close_dir / "win32_close_helper.exe"
    original_source = runtime_env.DEFAULT_SOURCE
    _, source_exe = runtime_env.validate_original_source(original_source)
    source_sha = digest(source_exe)
    if source_sha != runtime_env.ORIGINAL_SHA256:
        raise SystemExit("protected original source SHA mismatch")

    lanes: dict[str, Any] = {}
    cases = (
        ("new_game_off", "baseline", True),
        ("new_game_on", "candidate", True),
        ("save006_off", "baseline", False),
        ("save006_on", "candidate", False),
    )
    for label, variant, start_new_game in cases:
        lane_artifacts = artifact_root / label
        lane_runtime = runtime_root / label
        result = probe._run_lane(
            variant=variant,
            bridge=None,
            runtime_root=lane_runtime,
            artifact_root=lane_artifacts,
            close_helper=close_helper,
            hd_source="scale2x" if variant == "candidate" else None,
            hd_sidecar_layout=hd_layout if variant == "candidate" else None,
            new_game_path=start_new_game,
            new_game_start=start_new_game,
            fixture="save006",
            scene_actions="none",
            display_only=True,
            lane_label=f"g1-hdsingle-{args.variant}-{label}",
        )
        asset_access_path = Path(result["private_prefix"]) / "drive_c" / "inmm_asset_log.jsonl"
        if asset_access_path.is_file():
            asset_log = lane_artifacts / "asset_access_raw.jsonl"
            shutil.copy2(asset_access_path, asset_log)
            asset_lines = asset_log.read_text(encoding="utf-8", errors="replace").splitlines()
            result["asset_access"] = {
                "path": str(asset_log), "sha256": digest(asset_log), "opens": len(asset_lines),
                "hd_named_open_count": sum("_hd." in line.lower() for line in asset_lines),
            }
        else:
            result["asset_access"] = {"status": "MISSING", "hd_named_open_count": None}
        private_exe_sha = result.get("private_exe_sha256")
        result["variant_exe_sha256"] = expected_sha
        result["private_exe_matches_variant"] = private_exe_sha == expected_sha
        result["default_on_dll_sha256"] = digest(dll)
        result["lane_label"] = label
        lanes[label] = result

    _, after_source_exe = runtime_env.validate_original_source(original_source)
    source_unchanged = digest(after_source_exe) == source_sha
    passed = source_unchanged and all(
        lane.get("status") == "PASS"
        and lane.get("private_exe_matches_variant")
        and lane.get("cleanup", {}).get("ok")
        and lane.get("source_unchanged")
        and lane.get("asset_access", {}).get("hd_named_open_count") == 0
        for lane in lanes.values()
    ) and all(
        lanes[f"new_game_{suffix}"].get("new_game_start", {}).get("status") == "PASS"
        for suffix in ("off", "on")
    ) and all(
        lanes[f"save006_{suffix}"].get("actions", [])[-1].get("result") == "PASS"
        for suffix in ("off", "on")
    )
    summary = {
        "schema": "syw2plus.g1-variant-display.v1",
        "status": "PASS" if passed else "FAIL",
        "variant": args.variant,
        "variant_exe": str(exe),
        "variant_exe_sha256": expected_sha,
        "official_2613_sha256": esl2613_runtime.ESL2613_SHA256,
        "display_only": True,
        "source_unchanged": source_unchanged,
        "scope": ["PS", "simulation tick", "camera during new-game path", "screen captures"],
        "excluded": ["unit pool", "SFX", "shadow", "state snapshot", "supply/control bridge"],
        "lanes": lanes,
    }
    result_path = artifact_root / "variant-display-result.json"
    result_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    return {"status": summary["status"], "result": str(result_path),
            "lanes": {name: lane.get("status") for name, lane in lanes.items()}}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("official", *VARIANTS), required=True)
    parser.add_argument("--variant-exe", type=Path, help="required for a pinned variant; omitted for official 2613")
    parser.add_argument("--default-on-dll", type=Path, required=True)
    parser.add_argument("--hd-layout", type=Path, required=True,
                        help="single-file _hd.* layout copied into each candidate private game")
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args()
    if (args.variant == "official") != (args.variant_exe is None):
        parser.error("--variant-exe must be omitted for official and supplied for pinned variants")
    try:
        result = run(args)
    except (OSError, RuntimeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
