#!/usr/bin/env python3
"""Read-only W49S evidence audit for lap593 middle review."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from PIL import Image


REPO = Path("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch")
RUN = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/"
    "g2_capacity/20260925_lap592_w49s_lobby_start"
)
SUMMARY = RUN / "run_summary.json"
RUNNER = RUN / "w49s_run.py"
CAPTURE = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/"
    "20260925_085244_lap592_w49s_lobby_configured.png"
)
ORIGINAL = REPO.parent / "Syw2plus_re" / "Syw2plus" / "syw2plus_original.exe"
CANDIDATE = (
    REPO / "local/runtime/20260925_085217_1252194_0/game/syw2plus_original.exe"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    runner_text = RUNNER.read_text(encoding="utf-8")
    tree = ast.parse(runner_text)
    map_click_calls = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else None
        if name != "click":
            continue
        if any(isinstance(arg, ast.Starred) and isinstance(arg.value, ast.Name)
               and arg.value.id == "MAP_SIZE_CLICK" for arg in node.args):
            map_click_calls += 1

    owners = summary["active8_gate"]["owners"]
    residual_pids = summary["residual_processes"]
    with Image.open(CAPTURE) as image:
        dimensions = list(image.size)

    summary_write = runner_text.index('atomic_json(OUT / "run_summary.json", result)')
    first_cleanup = runner_text.index("game_proc.terminate()")
    result = {
        "active_nation_count": sum(1 for row in owners.values() if row["nation"]),
        "candidate_sha256": sha256(CANDIDATE),
        "capture_dimensions": dimensions,
        "capture_sha256": sha256(CAPTURE),
        "events_size": (RUN / "events.jsonl").stat().st_size,
        "map_100x100": summary["active8_gate"]["map_100x100"],
        "map_size": summary["map_size"],
        "map_size_click_calls": map_click_calls,
        "original_sha256": sha256(ORIGINAL),
        "owners_with_hq49_worker7": [
            int(owner) for owner, row in owners.items()
            if row["hq49"] and row["worker7"]
        ],
        "residual_pids_alive_now": [pid for pid in residual_pids if Path(f"/proc/{pid}").exists()],
        "runner_contains_6561": ":6561" in runner_text,
        "runner_display": summary["display"],
        "runner_sha256": sha256(RUNNER),
        "samples_size": (RUN / "samples.jsonl").stat().st_size,
        "summary_sha256": sha256(SUMMARY),
        "summary_written_before_cleanup": summary_write < first_cleanup,
        "verdict": summary["verdict"],
        "x6560_lock_exists_now": Path("/tmp/.X6560-lock").exists(),
        "x6561_lock_exists_now": Path("/tmp/.X6561-lock").exists(),
    }
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
