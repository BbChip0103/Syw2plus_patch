#!/usr/bin/env python3
"""lap695 work -- G2 전비10000 8인 동시 실측 (전역 4092-슬롯 풀 확장 후).

STATUS/APPROVALS 2026-09-27 00:05 운영자 판정(lap694 승격 해소, strategy 대행):
lap694가 확정한 전역 1200-슬롯 풀 병목을 (a) 고비용 타입 재탐색이 아니라 (b) 전역 풀
확장으로 해소한다. `patches/population/g2_supply10000_pool4092_owner500.py`가 보호
원본(b56986e0) 위에 ESL 계열에서 이미 검증된 4092-슬롯 풀 재배치 + 개인로스터500 +
전비10000을 조합해 만든 새 후보를 이 probe가 실행한다. 8인 활성화는 lap694와 동일한
`_custom_game_chain_inject_g2_eight_seed42`, fixture 구성도 lap692에서 실측한
type103(cost65)x153 + type5(cost35)x1(개인156기, used=10000)을 그대로 재사용한다 --
이번 실측의 유일한 변수는 전역 풀이 1200에서 4092로 커진 것 하나뿐이다
(8*156=1248 <= 4092, 병목이 해소돼야 owner0~7 전원 used=10000에 도달해야 한다).

원본/참고 저장소는 읽기 전용, 격리 사본에만 패치를 적용한다.

lap699 work -- STATUS/APPROVALS 2026-09-27 01:39 운영자 지시(lap698 수용, A/B 판정
대기 중 EXE 무변경 하네스 확장). 이번 lap이 추가한 것:
① `--fixture mixed`: type_costs.json 실측 중앙값(15)에 가까운 게이트-합법 타입(2=13,
   46=20) 혼합 fixture로 1인/8인 개인 상한(count_cap=500)의 실제 `used` 천장을 직접
   측정한다(lap698 결함1의 산술 추정을 raw 실행으로 교체).
② `--discriminative-save-load`: 저장 직후 op=4로 owner0의 `used` 필드만 원본 unit
   레코드를 건드리지 않고 명백히 다른 값으로 바꾼 뒤 로드해, 로드가 실제로 저장된
   값을 복원하는지(변경 무시 no-op이 아닌지) 판별한다(lap698 결함3).
③ `--run-ticks N`: fixture 완료(및 저장/로드) 후 N tick 진행을 기다리고 전역 무결성
   (owner합=active_slot_list=existence bitmap, 중복0)을 재확인한다. 가능하면 owner0→
   owner1 단일 유닛 공격 주문(op=8, 기존 G5 `op8_attack_order` 재사용)을 한 번
   시도한다(lap698 결함2).
EXE는 무변경이며 probe/하네스만 확장한다.
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
from patches.population.g2_supply10000_pool4092_owner500 import create_copy, CAPACITY
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools.g5_candidate_drag_probe import ProbeError, SupplyProbe, sha256, write_json
from tools.g5_screen_world_calibration import op8_attack_order

REPO = Path(__file__).resolve().parents[1]
ORIGINAL_SHA = runtime_env.ORIGINAL_SHA256
DEFAULT_SOURCE = runtime_env.DEFAULT_SOURCE

TARGET_USED = 10000
STARTING_USED = 20  # HQ(type49,cost10) + worker(type7,cost10)
# lap692-confirmed single-owner fixture: 153*65 + 1*35 + 20 = 10000, count=156.
HIGH_COST_FIXTURE_PLAN = ({"type": 103, "cost": 65, "count": 153}, {"type": 5, "cost": 35, "count": 1})
# lap698 결함1/lap699 work: type_costs.json 실측(비용>0 83종, min10/중앙값15/max65)에
# 가까운 게이트-합법 타입(runtime_bridge.c op5/6 allow-list) 혼합. "count"는 의도적으로
# count_cap(500)을 넘는 큰 wanted를 줘서 Gate가 실제로 거부하는 지점(진짜 개인 상한)을
# 직접 측정한다 -- 사전 계산값이 아니라 raw 실행 결과다.
MIXED_FIXTURE_PLAN = ({"type": 2, "cost": 13, "count": 400}, {"type": 46, "cost": 20, "count": 400})
FIXTURE_PLANS = {"high_cost": HIGH_COST_FIXTURE_PLAN, "mixed": MIXED_FIXTURE_PLAN}
SHARED_POOL_CAPACITY = CAPACITY  # 4093 (slot 0 reserved; 4092 usable)
# lap697 work: STATUS/INBOX 2026-09-27 01:05 지시. `read_state(..., detailed=True)`
# defaulted to profile="original" (STOCK_POOL, capacity1200 @ the stock addresses),
# which is why global_live_count always read 0 for this relocated candidate -- the
# stock addresses are stale once the candidate's regions move to the tail. This is
# the profile key registered in both `POOL_PROFILE_LAYOUTS` and
# `FULL_REGION_PROFILES` (runtime_driver.py) for this exact candidate.
PROFILE = "g2_supply10000_pool4092_owner500"
# lap696 work: STATUS 다음 한 가지 ① 저장->로드 1회. UI pause-menu 좌표(G5)는 다른
# 해상도(1600x1200)에서 캘리브레이션됐고 이 G2 1024x768 헤드리스 설정에 이식할 근거가
# 없다. 대신 브리지가 이미 노출한 원본 save/load 함수 직접 호출(op=2/op=3, runtime_env
# G2 lifecycle에서 검증된 경로)을 재사용해 UI 좌표 추측 없이 raw로 저장/로드한다.
SAVE_LOAD_SLOT = 1


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


def global_live_snapshot(pid: int) -> dict[str, Any]:
    snapshot = read_state(pid, detailed=True, profile=PROFILE)
    active = snapshot.get("active_slot_list", {})
    exists_slots = sorted(u["slot"] for u in snapshot["units"])
    return {
        "exists_count": len(exists_slots),
        "exists_slots": exists_slots,
        "active_count": active.get("count"),
        "active_slots": sorted(active.get("slots", [])),
        "duplicate_count": active.get("duplicate_count"),
        "matches_existence_bitmap": active.get("matches_existence_bitmap"),
    }


def global_live_count(pid: int) -> int:
    return global_live_snapshot(pid)["exists_count"]


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


def run_probe(
    source: Path, runtime_root: Path, artifact_root: Path, *, save_load: bool = False,
    fixture: str = "high_cost", owners: int = 8, discriminative_save_load: bool = False,
    run_ticks: int = 0,
) -> dict[str, Any]:
    if fixture not in FIXTURE_PLANS:
        raise ProbeError(f"unknown fixture plan: {fixture}")
    if not 1 <= owners <= 8:
        raise ProbeError(f"owners must be in 1..8: {owners}")
    if discriminative_save_load and not save_load:
        raise ProbeError("--discriminative-save-load requires --save-load")
    fixture_plan = FIXTURE_PLANS[fixture]
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

    candidate_path = game / "g2_supply_10000_pool4092_eight.exe"
    candidate_report = create_copy(original_copy, candidate_path)
    candidate_sha = candidate_report["candidate_sha256"]

    result: dict[str, Any] = {
        "schema": "syw2plus.g2-supply10000-pool4092-eight-owner-probe.v1",
        "status": "UNKNOWN",
        "target_used_per_owner": TARGET_USED,
        "fixture": fixture,
        "owners_requested": owners,
        "fixture_plan_per_owner": list(fixture_plan),
        "shared_pool_capacity": SHARED_POOL_CAPACITY,
        "shared_pool_usable_slots": SHARED_POOL_CAPACITY - 1,
        "owner_count_cap": candidate_report["owner_count_cap"],
        "provenance": {
            "source_root": str(source),
            "source_exe_sha256": sha256(source_exe),
            "original_copy_sha256": sha256(original_copy),
            "original_manifest_check": original_check,
            "candidate_sha256": candidate_sha,
            "candidate_report": candidate_report,
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
        for owner in range(owners):
            ax, ay = owner_anchor(owner, map_width, map_height)
            receipts: list[dict[str, Any]] = []
            total_added = 0
            owner_locked = False
            if not locked:
                for item in fixture_plan:
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
                "wanted": sum(p["count"] for p in fixture_plan),
                "post_used": post_players[owner]["used"],
                "post_count": post_players[owner]["count"],
                "post_count_cap": post_players[owner]["count_cap"],
                "post_cap": post_players[owner]["cap"],
                "global_live_after": post_live,
                "reached_target": post_players[owner]["used"] >= TARGET_USED,
                "count_cap_bound": post_players[owner]["count"] >= post_players[owner]["count_cap"],
                "locked_after_this_owner": locked,
            })
            if locked:
                break
        result["owner_reports"] = owner_reports

        final_players = player_summary(pid)
        final_snapshot = global_live_snapshot(pid)
        final_live = final_snapshot["exists_count"]
        result["final_players"] = final_players
        result["final_global_live"] = final_live
        result["final_global_live_snapshot"] = final_snapshot
        owners_attempted = len(owner_reports)
        owners_reached_target = sum(1 for r in owner_reports if r["reached_target"])
        result["owners_attempted"] = owners_attempted
        result["owners_reached_target"] = owners_reached_target
        if owners_reached_target == owners:
            result["status"] = "PASS_ALL_EIGHT_SUPPLY10000" if owners == 8 else f"PASS_ALL_{owners}_SUPPLY10000"
        elif fixture == "mixed":
            # lap698 결함1: 중앙값-근접 혼합 army는 개인 cap(500)에 먼저 막혀 10000에
            # 못 미친다 -- 이것은 실패가 아니라 그 천장을 raw로 측정한 결과다.
            result["status"] = "MEASURED_INDIVIDUAL_CAP_CEILING"
        elif owners_reached_target > 0 or owners_attempted > 0:
            result["status"] = "MEASURED_GLOBAL_POOL_BOTTLENECK"
        else:
            result["status"] = "FAIL_NO_OWNER_REACHED_TARGET"

        # lap697 work: STATUS/INBOX 2026-09-27 01:05 지시 -- raw cross-check that
        # the 4092-slot global pool has no duplicate live slots and that the
        # per-owner PlayerStruct `count` sum agrees with both the authoritative
        # active_slot_list count and the unit_existence bitmap count.
        owner_count_sum = sum(p["count"] for p in final_players)
        result["global_pool_integrity"] = {
            "owner_count_sum": owner_count_sum,
            "active_slot_list_count": final_snapshot["active_count"],
            "exists_bitmap_count": final_snapshot["exists_count"],
            "duplicate_count": final_snapshot["duplicate_count"],
            "matches_existence_bitmap": final_snapshot["matches_existence_bitmap"],
            "owner_sum_matches_active_count": owner_count_sum == final_snapshot["active_count"],
            "owner_sum_matches_exists_count": owner_count_sum == final_snapshot["exists_count"],
        }
        pass_status = "PASS_ALL_EIGHT_SUPPLY10000" if owners == 8 else f"PASS_ALL_{owners}_SUPPLY10000"
        if result["status"] == pass_status and not (
            final_snapshot["duplicate_count"] == 0
            and final_snapshot["matches_existence_bitmap"]
            and result["global_pool_integrity"]["owner_sum_matches_active_count"]
            and result["global_pool_integrity"]["owner_sum_matches_exists_count"]
        ):
            result["status"] = "FAIL_GLOBAL_POOL_INTEGRITY"

        if save_load and result["status"] == pass_status:
            save_path = game / "save" / f"save{SAVE_LOAD_SLOT:03d}.dat"
            if save_path.exists() or save_path.is_symlink():
                raise ProbeError(f"save slot {SAVE_LOAD_SLOT} is not previously absent: {save_path}")
            save_native = runtime_env._g2_lifecycle_native_op(
                prefix, op=2, owner=0, slot=SAVE_LOAD_SLOT, timeout=30.0,
            )
            if not save_path.is_file() or save_path.is_symlink() or save_path.stat().st_size <= 0:
                raise ProbeError(f"native op2 did not create a fresh save file: {save_path}")
            save_sha256 = sha256(save_path)

            discriminative_mutation: dict[str, Any] | None = None
            if discriminative_save_load:
                # lap698 결함3: 저장 직후 상태 변경 없이 바로 로드하면 no-op 로드도
                # 같은 결과를 낸다(판별 불가). owner0의 unit 레코드는 건드리지 않고
                # op=4(resource-only ledger fixture)로 `used` 필드만 저장된 값(10000)과
                # 명백히 다른 값으로 덮어써, 로드가 실제로 저장 시점 값을 복원하는지
                # (아래 owners_ok_after_load가 owner0도 검사) 판별한다.
                # `_g2_lifecycle_native_op`는 자체 큰(time-based) request id를 쓰고
                # 브리지는 `request[0] <= last_id`인 요청을 무시한다 -- `supply`(작은
                # 순차 id)를 그대로 쓰면 save의 id보다 작아 드롭된다(lap699 최초
                # 실행에서 `id=17` 타임아웃으로 실측). save의 id 다음으로 강제 전진.
                supply.next_id = max(supply.next_id, int(save_native["id"]) + 1)
                pre_mutation = save_native.get("after")
                if not isinstance(pre_mutation, dict):
                    raise ProbeError("save_native response is missing a ledger snapshot")
                mutated_used = 1
                if mutated_used == pre_mutation["used"]:
                    raise ProbeError("mutation target equals saved value; not discriminative")
                mutate_receipt = supply.call(
                    op=4, owner=0, unit_type=0,
                    x=pre_mutation["rice"], y=pre_mutation["wood"], count=mutated_used,
                )
                post_mutation = mutate_receipt.get("after")
                if not mutate_receipt.get("ok") or not isinstance(post_mutation, dict) or post_mutation["used"] != mutated_used:
                    raise ProbeError(f"discriminative mutation did not take effect: {mutate_receipt}")
                discriminative_mutation = {
                    "owner": 0,
                    "pre_mutation_used": pre_mutation["used"],
                    "mutated_used": post_mutation["used"],
                    "mutate_receipt": mutate_receipt,
                }

            load_native = runtime_env._g2_lifecycle_native_op(
                prefix, op=3, owner=0, slot=SAVE_LOAD_SLOT, timeout=30.0,
            )
            # Same last_id ordering hazard as the save-time bump above: any later
            # `supply.call()` (e.g. --run-ticks' op8 attack order) must post an id
            # greater than this native op's, or the bridge silently drops it.
            supply.next_id = max(supply.next_id, int(load_native["id"]) + 1)
            wait_for(lambda item: item.get("ps") == 3, "ps3_after_load", timeout=45)
            loaded_players = player_summary(pid)
            loaded_snapshot = global_live_snapshot(pid)
            loaded_live = loaded_snapshot["exists_count"]
            owners_ok_after_load = sum(
                1 for loaded in loaded_players
                if loaded["used"] == TARGET_USED
                and loaded["count"] == final_players[loaded["owner"]]["count"]
                and loaded["count_cap"] == final_players[loaded["owner"]]["count_cap"]
                and loaded["cap"] == final_players[loaded["owner"]]["cap"]
            )
            if discriminative_mutation is not None:
                discriminative_mutation["restored_used"] = loaded_players[0]["used"]
                discriminative_mutation["restore_confirmed"] = (
                    loaded_players[0]["used"] == discriminative_mutation["pre_mutation_used"]
                    and loaded_players[0]["used"] != discriminative_mutation["mutated_used"]
                )
            loaded_owner_count_sum = sum(p["count"] for p in loaded_players)
            loaded_integrity = {
                "owner_count_sum": loaded_owner_count_sum,
                "active_slot_list_count": loaded_snapshot["active_count"],
                "exists_bitmap_count": loaded_snapshot["exists_count"],
                "duplicate_count": loaded_snapshot["duplicate_count"],
                "matches_existence_bitmap": loaded_snapshot["matches_existence_bitmap"],
                "owner_sum_matches_active_count": loaded_owner_count_sum == loaded_snapshot["active_count"],
                "owner_sum_matches_exists_count": loaded_owner_count_sum == loaded_snapshot["exists_count"],
                "active_slots_unchanged_by_load": set(loaded_snapshot["active_slots"]) == set(final_snapshot["active_slots"]),
            }
            result["save_load"] = {
                "slot": SAVE_LOAD_SLOT,
                "save_path": str(save_path),
                "save_sha256": save_sha256,
                "save_native": save_native,
                "discriminative_mutation": discriminative_mutation,
                "load_native": load_native,
                "loaded_players": loaded_players,
                "loaded_global_live": loaded_live,
                "loaded_global_live_snapshot": loaded_snapshot,
                "loaded_global_pool_integrity": loaded_integrity,
                "owners_ok_after_load": owners_ok_after_load,
            }
            save_load_pass = (
                owners_ok_after_load == owners
                and loaded_integrity["duplicate_count"] == 0
                and loaded_integrity["matches_existence_bitmap"]
                and loaded_integrity["owner_sum_matches_active_count"]
                and loaded_integrity["owner_sum_matches_exists_count"]
                and loaded_integrity["active_slots_unchanged_by_load"]
                and (discriminative_mutation is None or discriminative_mutation["restore_confirmed"])
            )
            result["status"] = f"{pass_status}_SAVE_LOAD" if save_load_pass else "FAIL_SAVE_LOAD_MISMATCH"

        if run_ticks > 0 and result["status"].startswith("PASS"):
            # lap698 결함2: fixture 완료까지 전 구간 tick 3->21(~18 tick)뿐이라 안정성이
            # 미측정이었다. 여기서 N tick을 더 기다린 뒤 전역 무결성을 재확인한다.
            pre_run_tick = int(state().get("tick", 0))
            live_units = read_state(pid, detailed=True, profile=PROFILE)["units"]
            combat_attempt: dict[str, Any] | None = None
            attacker = next((u for u in live_units if u["owner"] == 0 and u["hp"] > 0), None)
            target = next((u for u in live_units if u["owner"] == 1 and u["hp"] > 0), None) if owners > 1 else None
            if attacker is not None and target is not None:
                combat_attempt = op8_attack_order(
                    supply, owner=0, src_slot=attacker["slot"], tgt_slot=target["slot"],
                )
            wait_for(
                lambda item: int(item.get("tick", 0)) >= pre_run_tick + run_ticks,
                "run_ticks_target", timeout=run_ticks / 4 + 120,
            )
            post_run_players = player_summary(pid)
            post_run_snapshot = global_live_snapshot(pid)
            post_run_owner_sum = sum(p["count"] for p in post_run_players)
            result["run_ticks"] = {
                "requested": run_ticks,
                "pre_run_tick": pre_run_tick,
                "post_run_tick": int(state().get("tick", 0)),
                "combat_attempt": combat_attempt,
                "post_run_players": post_run_players,
                "post_run_global_live_snapshot": post_run_snapshot,
                "post_run_owner_count_sum": post_run_owner_sum,
                "population_unchanged": post_run_owner_sum == owner_count_sum,
                "integrity_after_ticks": {
                    "duplicate_count": post_run_snapshot["duplicate_count"],
                    "matches_existence_bitmap": post_run_snapshot["matches_existence_bitmap"],
                    "owner_sum_matches_active_count": post_run_owner_sum == post_run_snapshot["active_count"],
                    "owner_sum_matches_exists_count": post_run_owner_sum == post_run_snapshot["exists_count"],
                },
            }
            if not (
                post_run_snapshot["duplicate_count"] == 0
                and post_run_snapshot["matches_existence_bitmap"]
                and result["run_ticks"]["integrity_after_ticks"]["owner_sum_matches_active_count"]
                and result["run_ticks"]["integrity_after_ticks"]["owner_sum_matches_exists_count"]
            ):
                result["status"] = "FAIL_GLOBAL_POOL_INTEGRITY_AFTER_TICKS"
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
    parser.add_argument("--save-load", action="store_true",
                         help="after all owners reach the target, run one native op2 save + op3 load and re-check accounting")
    parser.add_argument("--fixture", choices=sorted(FIXTURE_PLANS), default="high_cost",
                         help="high_cost (lap691-698 type103/type5 candidate) or mixed (near-median-cost ceiling measurement)")
    parser.add_argument("--owners", type=int, default=8, help="number of owners (1..8) to run the fixture loop for")
    parser.add_argument("--discriminative-save-load", action="store_true",
                         help="requires --save-load; mutate owner0's used field via op=4 between save and load")
    parser.add_argument("--run-ticks", type=int, default=0,
                         help="after PASS (and save-load if requested), wait for this many more ticks and re-verify integrity")
    args = parser.parse_args(argv)
    result = run_probe(
        args.source, args.runtime_root, args.artifact_root, save_load=args.save_load,
        fixture=args.fixture, owners=args.owners,
        discriminative_save_load=args.discriminative_save_load, run_ticks=args.run_ticks,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status", "").startswith(("PASS", "MEASURED")) and result.get("cleanup", {}).get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
