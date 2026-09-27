#!/usr/bin/env python3
"""lap692 work -- G2 전비10000 1인 실측: 브리지 확장으로 실제 도달 여부 측정.

STATUS lap691 다음 한 가지: `+0x2012`(전비 상한)가 살아있는 프로세스에서 10000으로
읽히는지 확인하고, 브리지를 cost40 계열 type으로 확장하거나 개인 상한(250)을 조정하는
것 중 하나를 선택해 실측한다. 이 probe는 **브리지 확장**을 선택한다.

1차 실행(cost40 type104, gate-legal 확인됨)에서 예상 밖 실측이 나왔다: 원본 Gate
(`0x43eda0`)가 owner당 실제 살아있는 개체수 약 242에서 거부한다(+0x2010에 저장된
"250"은 실제 enforcement 값이 아니다 -- 정확한 원인은 이 lap 범위 밖, 다음 회차 조사
대상). cost40*242=9680<10000이라 cost40 단독으로는 10000에 못 미친다.
따라서 이 probe는 살아있는 type table을 직접 읽어 gate-legal 후보 중 필요 개체수가
안전 여유(<=220, 실측 ~242 한계 아래)로 10000 used에 도달하는 **가장 비싼 타입**을
동적으로 고른다(예상: type103 cost65, 154기로 충분). 8인 동시/전역 풀 병목은 이 probe
범위 밖(다음 회차).

원본/참고 저장소는 읽기 전용, 격리 사본에만 패치를 적용한다.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Mapping, cast

from tools import runtime_env
from patches.population.fixed_supply_10000 import create_copy
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools.g5_candidate_drag_probe import ProbeError, SupplyProbe, sha256, write_json

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE

TARGET_USED = 10000  # acceptance is used>=cap, matching the 5000-stage definition
SAFE_UNIT_MARGIN = 220  # stay below the lap692 measured ~242 real per-owner gate ceiling
STARTING_USED = 20  # HQ(type49,cost10) + worker(type7,cost10)
ANCHOR = (60, 60)


TYPE_TABLE_BASE = 0x009B5228
TYPE_TABLE_STRIDE = 0x394
CANDIDATE_TYPES = (2, 5, 7, 28, 29, 46, 103, 104, 108)


def player_base(owner: int) -> int:
    return 0x00956770 + owner * 0x3ABC


def read_type_entry(pid: int, unit_type: int) -> dict[str, int]:
    offset = unit_type * TYPE_TABLE_STRIDE
    cost = int.from_bytes(read_memory(pid, TYPE_TABLE_BASE + 0x10 + offset, 2), "little", signed=True)
    width = int.from_bytes(read_memory(pid, TYPE_TABLE_BASE + 0x16 + offset, 2), "little", signed=True)
    height = int.from_bytes(read_memory(pid, TYPE_TABLE_BASE + 0x18 + offset, 2), "little", signed=True)
    flags = int.from_bytes(read_memory(pid, TYPE_TABLE_BASE + 0x24 + offset, 4), "little")
    gate_legal = 1 <= width <= 8 and 1 <= height <= 8 and (flags & 14) == 0
    return {"type": unit_type, "cost": cost, "width": width, "height": height,
            "flags": flags, "gate_legal": gate_legal}


def read_player(pid: int, owner: int) -> dict[str, int]:
    p = player_base(owner)
    return {
        "nation": int.from_bytes(read_memory(pid, p + 0x0, 2), "little"),
        "count": int.from_bytes(read_memory(pid, p + 0x200A, 2), "little", signed=True),
        "used": int.from_bytes(read_memory(pid, p + 0x200C, 2), "little", signed=True),
        "count_cap": int.from_bytes(read_memory(pid, p + 0x2010, 2), "little", signed=True),
        "supply_cap": int.from_bytes(read_memory(pid, p + 0x2012, 2), "little", signed=True),
    }


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    source_exe = source / runtime_env.ORIGINAL_EXE
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    bridge_dir = artifact_root / "type28_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", "1200"],
        cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
    )
    bridge = bridge_dir / "_inmm.dll"

    manifest = runtime_env.prepare(source, runtime_root=runtime_root, bridge=bridge, timeout=90)
    manifest_output = manifest.get("output")
    manifest_game = manifest.get("game")
    manifest_wine = manifest.get("wine")
    if not isinstance(manifest_output, Mapping) or not isinstance(manifest_game, Mapping) or not isinstance(manifest_wine, Mapping):
        raise ProbeError("runtime manifest sections are malformed")
    run_dir_text = cast(str, manifest_output.get("run_dir"))
    game_root_text = cast(str, manifest_game.get("root"))
    prefix_root_text = cast(str, manifest_wine.get("prefix"))
    manifest_path = Path(run_dir_text) / "manifest.json"
    original_check = runtime_env.check_runtime(manifest_path)
    game = Path(game_root_text)
    prefix = Path(prefix_root_text)
    original_copy = game / runtime_env.ORIGINAL_EXE
    if sha256(original_copy) != ORIGINAL_SHA:
        raise ProbeError("private original copy failed pre-install check")

    candidate_path = game / "g2_supply_10000.exe"
    candidate_sha = create_copy(original_copy, candidate_path)

    result: dict[str, Any] = {
        "schema": "syw2plus.g2-supply10000-type28-seed-probe.v1",
        "status": "UNKNOWN",
        "target_used": TARGET_USED,
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
            "original_copy_sha256": sha256(original_copy),
            "original_manifest_check": original_check,
            "candidate_sha256": candidate_sha,
            "bridge_sha256": sha256(bridge),
        },
    }
    log_path = artifact_root / "probe.log"
    log = log_path.open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb: Any = None
    pid: int | None = None
    try:
        env = dict(
            os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
            LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
            SYW2_SUPPLY_PROBE="1",
        )
        xvfb, display = runtime_env._xvfb(log, "1024x768x24")
        env["DISPLAY"] = display
        children.append(subprocess.Popen(
            ["wine", "explorer", "/desktop=Default,1024x768"],
            cwd=game, env=env, stdout=log, stderr=log,
        ))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(candidate_path)], cwd=game, env=env, stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def state() -> dict[str, Any]:
            assert pid is not None
            return read_state(pid)

        def wait_for(predicate, label: str, timeout: float = 45) -> dict[str, Any]:
            deadline = time.monotonic() + timeout
            last: dict[str, Any] = {}
            while time.monotonic() < deadline:
                try:
                    last = state()
                    if predicate(last):
                        return last
                except (OSError, ValueError, ProbeError) as exc:
                    last = {"error": f"{type(exc).__name__}: {exc}"}
                time.sleep(0.25)
            raise ProbeError(f"{label} timeout; last={last}")

        wait_for(lambda item: item.get("ps") == 9, "ps9")
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        if content is None:
            raise ProbeError("candidate game content window was not found")

        def click(x: int, y: int, *, button: int = 1) -> None:
            argv = [sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display", display,
                    str(x), str(y), "--button", str(button)]
            subprocess.run(argv, env=env, stdout=log, stderr=log, timeout=10, check=True)

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log, timeout=10, check=True)
        click(184, 560)
        wait_for(lambda item: item.get("ps") == 7, "ps7")

        def read_selector() -> dict[str, Any]:
            assert pid is not None
            return runtime_env._read_lobby_selector(lambda address, size: read_memory(pid, address, size))

        if read_selector().get("selected") == "solo":
            click(344, 169)
            time.sleep(0.5)
        click(462, 169)
        deadline = time.monotonic() + 10
        while read_selector().get("selected") != "solo" and time.monotonic() < deadline:
            time.sleep(0.2)
        if read_selector().get("selected") != "solo":
            raise ProbeError("solo selector did not settle")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 5, "ps5")
        ready_deadline = time.monotonic() + 12
        ready: dict[str, Any] = {}
        while time.monotonic() < ready_deadline:
            ready = runtime_env._read_local_ready_state(lambda address, size: read_memory(pid, address, size))
            if ready.get("ready_value") == 1:
                break
            time.sleep(0.2)
        if ready.get("ready_value") != 1:
            raise ProbeError(f"local lobby did not become ready: {ready}")
        click(608, 564)
        wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3")

        pre_fixture = read_player(pid, 0)
        result["pre_fixture_player0"] = pre_fixture
        result["supply_cap_reads_10000_live"] = pre_fixture["supply_cap"] == TARGET_USED

        type_table = {t: read_type_entry(pid, t) for t in CANDIDATE_TYPES}
        result["type_table_probe"] = type_table
        needed_used = TARGET_USED - STARTING_USED
        candidates = sorted(
            (e for e in type_table.values() if e["gate_legal"] and e["cost"] > 0),
            key=lambda e: e["cost"], reverse=True,
        )
        # Greedy bin-pack the exact remaining supply budget across gate-legal
        # types (largest cost first) so op=5's own accounting check
        # (old_used+cost<=cap) never has to reject an overshoot; a single
        # type rarely divides 9980 exactly, mixing types does.
        plan: list[dict[str, int]] = []
        remainder = needed_used
        for entry in candidates:
            if remainder <= 0:
                break
            units = remainder // entry["cost"]
            if units <= 0:
                continue
            units = min(units, SAFE_UNIT_MARGIN)
            plan.append({"type": entry["type"], "cost": entry["cost"], "count": units})
            remainder -= units * entry["cost"]
        result["fixture_plan"] = plan
        result["fixture_plan_remainder"] = remainder
        if not plan or sum(p["count"] for p in plan) > SAFE_UNIT_MARGIN:
            result["status"] = "BLOCKED_NO_GATE_LEGAL_TYPE_WITHIN_SAFE_MARGIN"
            raise ProbeError(f"could not bin-pack {needed_used} within margin {SAFE_UNIT_MARGIN}: {type_table}")

        supply = SupplyProbe(prefix)
        receipts: list[dict[str, Any]] = []
        total_added = 0
        for item in plan:
            remaining = item["count"]
            while remaining > 0:
                batch = min(remaining, 200)
                receipt = supply.call(op=5, owner=0, unit_type=item["type"], x=ANCHOR[0], y=ANCHOR[1], count=batch)
                receipts.append(receipt)
                added = int(receipt.get("fixture_added", 0))
                total_added += added
                if not receipt.get("ok") or added < batch:
                    break
                remaining -= added
        result["fixture_receipts"] = receipts
        result["total_added"] = total_added

        post_fixture = read_player(pid, 0)
        result["post_fixture_player0"] = post_fixture
        result["status"] = (
            "PASS_SUPPLY10000_SINGLE_OWNER"
            if total_added == sum(p["count"] for p in plan)
            and post_fixture["used"] >= TARGET_USED
            and post_fixture["supply_cap"] == TARGET_USED
            else "FAIL_SUPPLY10000_SINGLE_OWNER"
        )
    except (OSError, subprocess.SubprocessError, ProbeError, ValueError, KeyError) as exc:
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
        cleanup_error: str | None = None
        cur_env = locals().get("env", os.environ)
        try:
            subprocess.run(["wineserver", "-k"], env=cur_env, stdout=log, stderr=log, timeout=10, check=False)
            subprocess.run(["wineserver", "-w"], env=cur_env, stdout=log, stderr=log, timeout=10, check=False)
        except (OSError, subprocess.SubprocessError) as exc:
            cleanup_error = f"{type(exc).__name__}: {exc}"
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
            try:
                xvfb.wait(timeout=5)
            except subprocess.TimeoutExpired:
                xvfb.kill()
                xvfb.wait(timeout=5)
        result["cleanup"] = {
            "error": cleanup_error,
            "owned_children_stopped": all(child.poll() is not None for child in children),
            "xvfb_stopped": xvfb is None or xvfb.poll() is not None,
            "prefix_processes_after": runtime_env._prefix_pids(prefix),
        }
        result["cleanup"]["ok"] = not result["cleanup"]["prefix_processes_after"] and cleanup_error is None
        result["source_sha_after"] = sha256(source_exe)
        result["source_unchanged"] = result["source_sha_after"] == ORIGINAL_SHA
        write_json(artifact_root / "probe-result.json", result)
        log.close()
        game_copy = game
        if game_copy.exists():
            import shutil as _shutil
            _shutil.rmtree(game_copy, ignore_errors=True)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    args = parser.parse_args(argv)
    result = run_probe(args.source, args.runtime_root, args.artifact_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "").startswith("PASS") and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
