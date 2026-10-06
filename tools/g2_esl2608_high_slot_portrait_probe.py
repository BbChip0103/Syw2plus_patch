#!/usr/bin/env python3
"""Paired ESL2608 portrait lookup probe for a relocated high-slot unit.

The baseline run exercises the same saved-game portrait control at a stock
slot.  The candidate run copies that live unit to slot 4092 in the candidate
pool, clears duplicate low-slot records, and clicks the same portrait.  A
camera focus change is the runtime effect: it proves the portrait consumer
resolved the producer after the candidate relocation.  The fixture is written
only into the owned game process and is never written to an EXE or save file.
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

from patches.population.g2_esl2608_runtime_layout import (
    ESL2608_LAYOUT,
    ESL2608_RELOCATION_DELTA,
    REFERENCE_LAYOUT,
    from_build_report,
)
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools import runtime_env
from tools.g2_esl2608_phase_a_shift_probe import (
    BASE_SOURCE,
    DATA_OVERLAY,
    EXPECTED_BASELINE,
    EXPECTED_CANDIDATE,
    LANES,
    UNIT_STRIDE,
    build_candidate,
)

REPO = Path(__file__).resolve().parents[1]
SAVE_SOURCE = REPO.parent / "Syw2plus" / "save" / "save006.dat"
PORTRAIT_CLICK = (366, 565)
MINIMAP_REPOSITION = (35, 560)
DESELECT = (460, 410)
SAVE_MENU_LOAD = (296, 505)
SAVE006_ROW = (340, 336)
SAVE006_LOAD = (316, 372)
PORTRAIT_PRODUCER_ADDRESS = 0x00B93980
UNIT_INTERNAL_ID_OFFSET = 0x29C
UNIT_TYPE_OFFSET = 0x8D
UNIT_OWNER_OFFSET = 0x8E
UNIT_HP_OR_PRODUCER_FLAG_OFFSET = 0x1F4
HIGH_SLOT = 4092
STOCK_CAPACITY = 1200


class ProbeError(RuntimeError):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return digest(path.read_bytes())


def copy_overlay(game: Path) -> list[dict[str, Any]]:
    copied: list[dict[str, Any]] = []
    for source in sorted(DATA_OVERLAY.rglob("*")):
        if source.is_symlink() or not source.is_file() or source.suffix.lower() in {".exe", ".xlsx"}:
            continue
        target = game / source.relative_to(DATA_OVERLAY)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        copied.append({"path": str(source.relative_to(DATA_OVERLAY)), "sha256": sha256(target)})
    return copied


def wait_state(
    pid: int, predicate: Callable[[dict[str, Any]], bool], label: str, timeout: float = 45,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last: dict[str, Any] = {}
    while time.monotonic() < deadline:
        try:
            last = read_state(pid, False)
            if predicate(last):
                return last
        except (OSError, ValueError, KeyError, ProbeError) as exc:
            last = {"error": f"{type(exc).__name__}: {exc}"}
        time.sleep(0.25)
    raise ProbeError(f"{label} timeout; last={last}")


def read_u32(pid: int, address: int) -> int:
    return int.from_bytes(read_memory(pid, address, 4), "little")


def camera(pid: int) -> tuple[int, int]:
    raw = read_memory(pid, 0x00B42D7C, 8)
    return (int.from_bytes(raw[:4], "little", signed=True),
            int.from_bytes(raw[4:], "little", signed=True))


def player_summary(pid: int) -> dict[str, Any]:
    state = read_state(pid, False)
    player = state["players"][0]
    return {
        "ps": state["ps"],
        "tick": state["tick"],
        "camera": list(camera(pid)),
        "nation": player["nation"],
        "count": player["count"],
        "used": player["used"],
        "count_cap": player["count_cap"],
        "cap": player["cap"],
    }


def click(display: str, origin: tuple[int, int], x: int, y: int, env: Mapping[str, str], log: Any) -> None:
    command = [
        sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
        str(origin[0] + x), str(origin[1] + y),
    ]
    subprocess.run(command, env=env, stdout=log, stderr=log, timeout=10, check=True)
    time.sleep(0.7)


def capture(
    display: str, tag: str, env: Mapping[str, str], log: Any, artifact_root: Path,
) -> dict[str, str]:
    capture_root = REPO.parent / "temp" / "Syw2plus_patch" / "captures"
    capture_root.mkdir(parents=True, exist_ok=True)
    path = capture_root / f"{time.strftime('%Y%m%d_%H%M%S')}_g2_esl2608_lap805_{tag}.png"
    subprocess.run(["scrot", str(path)], env=env, stdout=log, stderr=log, timeout=10, check=True)
    record = {"path": str(path), "sha256": sha256(path)}
    (artifact_root / f"capture_{tag}.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def private_write(pid: int, address: int, data: bytes) -> None:
    fd = os.open(f"/proc/{pid}/mem", os.O_RDWR)
    try:
        written = os.pwrite(fd, data, address)
        if written != len(data):
            raise ProbeError(f"short private fixture write at 0x{address:x}: {written}/{len(data)}")
    finally:
        os.close(fd)


def candidate_regions() -> tuple[int, int, int]:
    regions = {region.name: region for region in REFERENCE_LAYOUT.regions}
    return (
        regions["unit_existence"].new_start + ESL2608_RELOCATION_DELTA,
        regions["unit_age"].new_start + ESL2608_RELOCATION_DELTA,
        ESL2608_LAYOUT.unit_pool_base,
    )


def install_fixture(pid: int) -> dict[str, Any]:
    exists_base, age_base, unit_base = candidate_regions()
    producer = read_u32(pid, PORTRAIT_PRODUCER_ADDRESS)
    if not 0 < producer < STOCK_CAPACITY:
        raise ProbeError(f"saved portrait producer is not a stock slot: {producer}")
    source_unit = bytearray(read_memory(pid, unit_base + producer * UNIT_STRIDE, UNIT_STRIDE))
    kind = source_unit[UNIT_TYPE_OFFSET]
    owner = source_unit[UNIT_OWNER_OFFSET]
    source_id = int.from_bytes(source_unit[UNIT_INTERNAL_ID_OFFSET:UNIT_INTERNAL_ID_OFFSET + 4], "little")
    if source_id == 0 or kind == 0:
        raise ProbeError(f"saved producer is not a live unit: slot={producer} kind={kind} id={source_id:#x}")
    if int.from_bytes(read_memory(pid, exists_base + HIGH_SLOT * 2, 2), "little") != 0:
        raise ProbeError("candidate high slot 4092 was already occupied")

    matching_slots: list[int] = []
    for slot in range(1, STOCK_CAPACITY):
        exists = int.from_bytes(read_memory(pid, exists_base + slot * 2, 2), "little")
        if not exists:
            continue
        row = read_memory(pid, unit_base + slot * UNIT_STRIDE, UNIT_STRIDE)
        if (row[UNIT_TYPE_OFFSET] == kind and row[UNIT_OWNER_OFFSET] == owner
                and int.from_bytes(row[UNIT_HP_OR_PRODUCER_FLAG_OFFSET:UNIT_HP_OR_PRODUCER_FLAG_OFFSET + 4], "little") == 100):
            matching_slots.append(slot)
    if producer not in matching_slots:
        raise ProbeError(f"producer {producer} missing from portrait scan candidates: {matching_slots}")

    new_id = (source_id & 0xFFFF0000) | HIGH_SLOT
    source_unit[UNIT_INTERNAL_ID_OFFSET:UNIT_INTERNAL_ID_OFFSET + 4] = new_id.to_bytes(4, "little")
    old_exists = read_memory(pid, exists_base + producer * 2, 2)
    old_age = read_memory(pid, age_base + producer * 2, 2)
    private_write(pid, unit_base + HIGH_SLOT * UNIT_STRIDE, bytes(source_unit))
    private_write(pid, exists_base + HIGH_SLOT * 2, old_exists)
    private_write(pid, age_base + HIGH_SLOT * 2, old_age)
    for slot in matching_slots:
        private_write(pid, exists_base + slot * 2, b"\0\0")
    return {
        "producer_before": producer,
        "high_slot": HIGH_SLOT,
        "kind": kind,
        "owner": owner,
        "source_id": hex(source_id),
        "high_slot_id": hex(new_id),
        "cleared_slots": matching_slots,
    }


def run_probe(lane: str, variant: str, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if lane not in LANES or variant not in {"baseline", "candidate"}:
        raise ProbeError(f"unsupported lane/variant: {lane}/{variant}")
    if artifact_root.exists():
        raise ProbeError(f"artifact root already exists: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source_path = LANES[lane]
    baseline = source_path.read_bytes()
    if digest(baseline) != EXPECTED_BASELINE[lane]:
        raise ProbeError(f"baseline SHA mismatch for {lane}: {digest(baseline)}")
    candidate, report = build_candidate(baseline)
    candidate_sha = digest(candidate)
    if candidate_sha != EXPECTED_CANDIDATE[lane]:
        raise ProbeError(f"candidate SHA mismatch for {lane}: {candidate_sha}")
    layout = from_build_report(report["pool"])
    bridge_dir = artifact_root / "bridge"
    bridge_args = [
        sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
        "--out-dir", str(bridge_dir), "--unit-pool-capacity", "4093" if variant == "candidate" else "1200",
    ]
    if variant == "candidate":
        bridge_args += ["--unit-pool-base", hex(layout.unit_pool_base)]
    subprocess.run(bridge_args, cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)))
    bridge = bridge_dir / "_inmm.dll"
    manifest = runtime_env.prepare(BASE_SOURCE, runtime_root=runtime_root, bridge=bridge, timeout=90)
    run_dir = Path(cast(str, cast(Mapping[str, Any], manifest["output"])["run_dir"]))
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    overlay = copy_overlay(game)
    if not SAVE_SOURCE.is_file():
        raise ProbeError(f"portrait fixture save is missing: {SAVE_SOURCE}")
    private_save = game / "save" / "save006.dat"
    private_save.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SAVE_SOURCE, private_save)
    installed = baseline if variant == "baseline" else candidate
    private_exe.write_bytes(installed)
    expected_private_sha = digest(installed)
    if sha256(private_exe) != expected_private_sha:
        raise ProbeError("private ESL2608 executable hash mismatch")

    result: dict[str, Any] = {
        "schema": "syw2plus.g2-esl2608-high-slot-portrait.v1",
        "status": "UNKNOWN", "lane": lane, "variant": variant,
        "source_sha256": digest(baseline), "candidate_sha256": candidate_sha,
        "private_exe_sha256": expected_private_sha,
        "fixture": {"saved_game": "save006.dat", "save_sha256": sha256(private_save),
                    "synthetic_high_slot": variant == "candidate", "slot": HIGH_SLOT},
        "manifest": str(run_dir / "manifest.json"), "private_game": str(game), "private_prefix": str(prefix),
        "overlay_files": overlay, "events": [], "cleanup": {},
    }
    log_path = artifact_root / "probe.log"
    log = log_path.open("a", encoding="utf-8")
    children: list[subprocess.Popen[Any]] = []
    xvfb: subprocess.Popen[Any] | None = None
    display: str | None = None
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
                   SYW2_SUPPLY_PROBE="1")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"], cwd=game, env=env,
                                         stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid
        wait_state(pid, lambda state: state.get("ps") == 9, "menu_ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("game content window not found")
        info = runtime_env._xwininfo_details(display, content, 10)
        origin = (int(info["x"]), int(info["y"]))
        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)

        click(display, origin, *SAVE_MENU_LOAD, env, log)
        wait_state(pid, lambda state: state.get("ps") == 35, "save_menu_ps35")
        click(display, origin, *SAVE006_ROW, env, log)
        click(display, origin, *SAVE006_LOAD, env, log)
        wait_state(pid, lambda state: state.get("ps") == 3 and state.get("tick", 0) > 0, "loaded_ps3", 90)
        time.sleep(1)
        result["loaded"] = player_summary(pid)
        result["captures"] = {"loaded": capture(display, f"{lane}_{variant}_loaded", env, log, artifact_root)}

        click(display, origin, *DESELECT, env, log)
        click(display, origin, *MINIMAP_REPOSITION, env, log)
        click(display, origin, *DESELECT, env, log)
        result["before_portrait"] = player_summary(pid)

        if variant == "candidate":
            # Resolve the saved portrait's stock producer first; this is only
            # a calibration click and is not counted as high-slot evidence.
            click(display, origin, *PORTRAIT_CLICK, env, log)
            result["fixture"] = {**result["fixture"], **install_fixture(pid)}
            click(display, origin, *MINIMAP_REPOSITION, env, log)
            click(display, origin, *DESELECT, env, log)
            result["before_portrait"] = player_summary(pid)

        click(display, origin, *PORTRAIT_CLICK, env, log)
        result["after_portrait"] = player_summary(pid)
        result["portrait_producer_pointer_after"] = read_u32(pid, PORTRAIT_PRODUCER_ADDRESS)
        result["captures"]["after_portrait"] = capture(
            display, f"{lane}_{variant}_after_portrait", env, log, artifact_root,
        )
        result["checks"] = {
            "portrait_focus_changed": result["after_portrait"]["camera"] != result["before_portrait"]["camera"],
            "candidate_fixture_high_slot": variant != "candidate" or result["fixture"]["high_slot"] == HIGH_SLOT,
        }
        result["status"] = "PASS" if all(result["checks"].values()) else "FAIL"
    except Exception as exc:
        result["status"] = "FAIL"
        result["error"] = repr(exc)
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
        if display is not None:
            try:
                subprocess.run(["wineserver", "-k"], env={**os.environ, "WINEPREFIX": str(prefix)},
                               stdout=log, stderr=log, timeout=10, check=False)
                subprocess.run(["wineserver", "-w"], env={**os.environ, "WINEPREFIX": str(prefix)},
                               stdout=log, stderr=log, timeout=10, check=False)
            except Exception as exc:
                result["cleanup_error"] = repr(exc)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
                xvfb.wait(timeout=5)
        result["cleanup"]["prefix_processes_after"] = runtime_env._prefix_pids(prefix)
        if game.exists():
            shutil.rmtree(game)
        result["cleanup"]["game_removed"] = not game.exists()
        result["source_unchanged"] = sha256(source_path) == digest(baseline)
        result["cleanup"]["ok"] = not result["cleanup"]["prefix_processes_after"] and result["cleanup"]["game_removed"]
        log.close()
        (artifact_root / "probe-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lane", choices=sorted(LANES), required=True)
    parser.add_argument("--variant", choices=("baseline", "candidate"), required=True)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.lane, args.variant, args.runtime_root, args.artifact_root)
    print(json.dumps({"status": result["status"], "lane": args.lane, "variant": args.variant,
                      "checks": result.get("checks"), "error": result.get("error")}, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
