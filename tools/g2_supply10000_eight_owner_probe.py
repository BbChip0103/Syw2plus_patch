#!/usr/bin/env python3
"""lap694 work -- G2 전비10000 8인 동시 실측.

STATUS lap693 다음 한 가지: lap692에서 확정한 owner-1인 fixture 조합
(type103 cost65 x153 + type5 cost35 x1, 개인 개체 156 = used 10000, 실측
per-owner live gate ~242 이내)을 8인 모두에게 순서대로 적용해, 전역 1200
슬롯 유닛 테이블이 8*156=1248을 감당하는지 raw로 측정한다. 8인 활성화는
기존에 검증된 `_custom_game_chain_inject_g2_eight_seed42` 컨트롤 목표를
그대로 재사용한다(운영자 22:52 결정으로 새 원본 경로 `[ESL]Syw2plus/`
기준). g1_baseline()의 5000 전용 파이프라인(승인 브리지 SHA/roster 5000
가정/24k observer)은 건드리지 않고, 저수준 프리미티브만 재사용한다.

이 probe는 8인 모두를 채우는 것을 성공 조건으로 요구하지 않는다 -- 목적은
병목의 정확한 위치(어느 owner에서 몇 기 만에 거부되는지, 거부 사유)를
raw로 기록하는 것이다.

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

TARGET_USED = 10000
STARTING_USED = 20  # HQ(type49,cost10) + worker(type7,cost10)
# lap692-confirmed single-owner fixture: 153*65 + 1*35 + 20 = 10000, count=156.
FIXTURE_PLAN = ({"type": 103, "cost": 65, "count": 153}, {"type": 5, "cost": 35, "count": 1})
SHARED_POOL_CAPACITY = 1200


def player_summary(pid: int) -> list[dict[str, Any]]:
    snapshot = read_state(pid)
    return [
        {
            "owner": p["owner"], "nation": p["nation"], "ai": p["ai"],
            "count": p["count"], "used": p["used"],
            "count_cap": p["count_cap"], "cap": p["cap"],
        }
        for p in snapshot["players"]
    ]


def global_live_count(pid: int) -> int:
    return len(read_state(pid, detailed=True)["units"])


def read_map_dims(pid: int) -> tuple[int, int]:
    w = int.from_bytes(read_memory(pid, 0xB3DE34, 2), "little", signed=True)
    h = int.from_bytes(read_memory(pid, 0xB3DE36, 2), "little", signed=True)
    return w, h


def owner_anchor(owner: int, map_width: int, map_height: int) -> tuple[int, int]:
    col = owner % 4
    row = owner // 4
    ax = 5 + col * max(1, (map_width - 10) // 4)
    ay = 5 + row * max(1, (map_height - 10) // 2)
    return min(ax, map_width - 1), min(ay, map_height - 1)


def run_probe(source: Path, runtime_root: Path, artifact_root: Path) -> dict[str, Any]:
    if artifact_root.exists():
        raise ProbeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    source = source.expanduser().resolve()
    _, source_exe = runtime_env.validate_original_source(source)
    if sha256(source_exe) != ORIGINAL_SHA:
        raise ProbeError("protected source executable SHA mismatch before run")

    bridge_dir = artifact_root / "eight_owner_bridge"
    subprocess.run(
        [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
         "--out-dir", str(bridge_dir), "--unit-pool-capacity", str(SHARED_POOL_CAPACITY)],
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

    candidate_path = game / "g2_supply_10000_eight.exe"
    candidate_sha = create_copy(original_copy, candidate_path)

    result: dict[str, Any] = {
        "schema": "syw2plus.g2-supply10000-eight-owner-probe.v1",
        "status": "UNKNOWN",
        "target_used_per_owner": TARGET_USED,
        "fixture_plan_per_owner": list(FIXTURE_PLAN),
        "shared_pool_capacity": SHARED_POOL_CAPACITY,
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

        chain_result = runtime_env._g4_send_control_goal(prefix, runtime_env.G2_CREATION_GOAL, 30.0)
        result["chain_inject"] = chain_result
        if chain_result.get("ok") is not True:
            raise ProbeError(f"G2 eight-owner chain inject failed: {chain_result.get('reason')}")
        wait_for(lambda item: item.get("ps") == 3 and int(item.get("tick", 0)) > 0, "ps3_eight_owner", timeout=45)

        assert pid is not None
        pre_players = player_summary(pid)
        pre_live = global_live_count(pid)
        result["pre_fixture_players"] = pre_players
        result["pre_fixture_global_live"] = pre_live
        owners_present = {p["owner"] for p in pre_players if p["nation"]}
        if owners_present != set(range(8)):
            raise ProbeError(f"eight-owner creation incomplete; owners with nonzero nation: {sorted(owners_present)}")

        map_width, map_height = read_map_dims(pid)
        result["map_dims"] = {"width": map_width, "height": map_height}

        supply = SupplyProbe(prefix)
        owner_reports: list[dict[str, Any]] = []
        locked = False
        for owner in range(8):
            ax, ay = owner_anchor(owner, map_width, map_height)
            receipts: list[dict[str, Any]] = []
            total_added = 0
            owner_locked = False
            if not locked:
                for item in FIXTURE_PLAN:
                    remaining = item["count"]
                    while remaining > 0 and not owner_locked:
                        batch = min(remaining, 200)
                        receipt = supply.call(op=5, owner=owner, unit_type=item["type"], x=ax, y=ay, count=batch)
                        receipts.append(receipt)
                        added = int(receipt.get("fixture_added", 0))
                        total_added += added
                        if receipt.get("reason") == "fixture_locked_after_accounting_failure":
                            owner_locked = True
                            locked = True
                            break
                        if not receipt.get("ok") or added < batch:
                            break
                        remaining -= added
            post_players = player_summary(pid)
            post_live = global_live_count(pid)
            owner_reports.append({
                "owner": owner,
                "anchor": {"x": ax, "y": ay},
                "receipts": receipts,
                "total_added": total_added,
                "wanted": sum(p["count"] for p in FIXTURE_PLAN),
                "post_used": post_players[owner]["used"],
                "post_count": post_players[owner]["count"],
                "post_cap": post_players[owner]["cap"],
                "global_live_after": post_live,
                "reached_target": post_players[owner]["used"] >= TARGET_USED,
                "locked_after_this_owner": locked,
            })
            if locked:
                break
        result["owner_reports"] = owner_reports

        final_players = player_summary(pid)
        final_live = global_live_count(pid)
        result["final_players"] = final_players
        result["final_global_live"] = final_live
        owners_attempted = len(owner_reports)
        owners_reached_target = sum(1 for r in owner_reports if r["reached_target"])
        result["owners_attempted"] = owners_attempted
        result["owners_reached_target"] = owners_reached_target
        if owners_reached_target == 8:
            result["status"] = "PASS_ALL_EIGHT_SUPPLY10000"
        elif owners_reached_target > 0 or owners_attempted > 0:
            result["status"] = "MEASURED_GLOBAL_POOL_BOTTLENECK"
        else:
            result["status"] = "FAIL_NO_OWNER_REACHED_TARGET"
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
    return 0 if result.get("status", "").startswith(("PASS", "MEASURED")) and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
