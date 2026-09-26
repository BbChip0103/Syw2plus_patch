# 2026-09-26 | lap 683 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(세션 보고 모델ID), 중간 tier(진단·컨펌), high. 게임 코드·probe·패치 수정 없음.
- 가설 / 사용자 관찰: 2026-09-26 16:08 운영자 판정(INBOX 122행)이 G5 v3 후보 `e5004764…`의 "드래그50·그룹/호출/저장로드50·이동 paired·공격 브로드캐스트·v3 크래시 수정"을 middle 독립 검수로 올렸다. 원시 JSON이 각 주장과 같은 후보 SHA·같은 판정 필드로 일치하면 2단 APPROVE, 아니면 HOLD.
- 예상 PASS / FAIL: 모든 항목이 `e5004764…` 원시 증거로 원본20/후보50 paired이고 판정 필드가 명령 종류를 구분하면 PASS. 다른 후보 SHA의 증거로 대체됐거나, 판정식이 명령 종류를 구분하지 못하거나, 원본 paired가 없으면 해당 항목 HOLD.
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `docs/feedback/INBOX.md`(자체 기록 1항), `docs/feedback/APPROVALS.md`(색인 1항), `loop/ESCALATE_SOL`(lap683 섹션 추가). 제품 코드·도구·테스트·바이너리 0 변경, 커밋 없음(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(이번 세션 `game.exe`·`syw2plus_original.exe` 재해시 일치). 후보 `e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977` — lap680 snapshot/move, lap681 header, lap682 candidate 4개 artifact의 exe 사본 SHA 전부 일치. 격리 Wine/Xvfb 1600×1200, PS3 solo owner0, worker slot1198 앵커 dense 7×8 type2 55기(지도 시드 미고정).

## 실행 명령 / 확인한 원시 자료

1. artifact JSON(공유 `temp/Syw2plus_patch/`) SHA 앞16: lap680 snapshot `20d1ea5b98e62b57`, lap680 fixed_move `6fe7ba1a72bff4ed`, lap681 header `42707b8c14070959`, lap682 original_v2 `53abf77dc1968b5c`, lap682 candidate_v2 `45dc67821ac7e383`. 전부 `source_unchanged=true`, `cleanup.ok=true`.
2. 행 단위 재집계(python, 읽기 전용): 각 JSON의 `samples[].rows`/`after_units`/`final_rows`에서 `(command=+0x290, pending_command=+0x384, pending_xy, target_uid)` 분포를 직접 셌다.
3. `PYTHONPATH=. .venv/bin/python -m pytest -q patches/selection/test_g5_selection_cap50_v{3,2,1}.py tests/test_g5_worker_relative_move_attack_probe.py` → **17 passed**(v3 결정적 SHA 핀 포함).
4. 문서 갱신 후 `python3 checks/context_limits.py` → `CONTEXT_PASS`(STATUS 96·INBOX 124·APPROVALS 87줄), `bash checks/safety.sh check` → `SAFETY_PASS`. 문서만 바뀌어 `make check`는 생략했다(직전 lap682 972 passed).
5. `grep TARGET_SHA tools/g5_*.py`: 부대지정/호출/save-load roundtrip 도구 `tools/g5_candidate_drag_probe.py`는 여전히 `ae495fa5…`(v2)에 고정.

## 측정값 / 판정

- **v3 크래시 수정: APPROVE(좁은 범위).** lap680 fixed_move raw: 청크 호출 지점 `0x4e4db2/0x4e4de0/0x4e4e17` 각 1회, `packed_word_hits=50`, `fatal=None`, accessor 이상값 0. 결정적 SHA 핀 테스트 PASS. 원인(백업 버퍼 `[ebp-0x50]` 프레임 미예약)과 `sub esp,0x50` 1줄 수정은 raw와 모순 없음.
- **이동 paired: APPROVE.** lap682 후보 `command==3` 동시 일치 50/50 @0.15s(`ever_matched=50`), 원본 20/20 @0.15s, 선택 50 vs 20, 같은 self-calibrated 목적지 방식. 후보 SHA 일치.
- **공격 브로드캐스트 50: 불인정(HOLD) — 16:08 판정 근거와 원시 자료가 충돌한다.**
  - lap680 "`+0x384` 공격 pending 50/50"의 판정식은 `pending_command != 1`이다(`tools/g5_pending_broadcast_snapshot_probe_v3.py:21`). 실제 행은 worker `0x10001`×1 + fixture `0x1000001`(xy `0x2e002b`)×49이고, 같은 phase `after_units`는 `command==3` 35 / `command==1` 15 / **`command==4` 0**이다. 즉 이 50은 공격 전용 값이 아니며 이동 계열과 구분되지 않는다.
  - 같은 판정식 때문에 lap681 "MOVE pending 3초 후 50/50"도 실제로는 `0x1000001+command3` 20 / `0x10001+command1` 30이다(idle 후 값 `0x10001`도 "written"으로 셈). 이동은 lap682가 `command==3`으로 따로 입증했으므로 결론에는 영향 없음.
  - 공격 계열의 유일한 >20 신호는 lap681 후보 1회 `command==4` 41/50(1초, `0x1000001`×39+`0x10002`×2)뿐이다. 원본 paired 실행이 없고, lap682의 공격툴바+지면클릭은 후보 0/50·원본 0/20으로 재현되지 않았다(lap682 공격 목적지 primary가 방금 이동한 목적지와 같음).
  - "UI 공격 수렴 0은 원본도 0"이라는 전제는 lap682 1쌍에만 해당하며, 후보가 41을 낸 lap681 입력(고정 픽셀 `(300,420)`, 1초)은 원본으로 돌려본 적이 없다.
- **드래그50·51번째 미선택·부대지정/호출·save/load·UI: v3에서 미실행(HOLD).** lap664/665 승인 증거는 `ae495fa5…`(v2) 기준이다. v3는 선택 entries를 백업·복원하는 wrapper를 추가했고 lap680 크래시가 바로 그 entries[14..19] 오염이었으므로, v3에서 roundtrip 회귀를 다시 확인해야 한다. v3 artifact들은 선택 50(55+worker 중)만 보여 준다.
- **미해결 불일치(기록만):** lap681 header trace는 hook site `0x4AE550`의 클릭 후 hit 0(`post_marker_hits=0`)인데, lap680은 같은 후보에서 청크 호출 지점 3곳이 각 1회 hit했다. marker 순서 문제일 가능성이 높지만 확인되지 않았다.
- 멀티 동기화 `UNKNOWN`, 사용자 milestone 승인 없음.
- **종합: G5 전체 2단 `HOLD/INCONCLUSIVE`.** 제품 G5 PASS 아님.

## work tier handoff (다음 한 가지, middle 재회부 없이)

v3 `e5004764…` 하나로 다음 두 가지를 원본 paired로 실행한다. 둘 다 끝나면 새 middle 세션이 G5 2단을 다시 검수한다.

1. **v3 roundtrip:** `tools/g5_candidate_drag_probe.py`의 TARGET_SHA를 `e5004764…`로 바꾸거나 variant 인자로 받게 한 뒤(테스트 갱신 포함) 후보·원본을 fresh 실행한다. PASS = 후보 selected/recalled/loaded-recalled `50/50/50`, 56개 후보 중 51번째 미선택, stock group20+`+0x344` 필드 49, fault 0, UI 캡처 보존. 원본 = `20/20/20`.
2. **공격 paired:** 판정식을 `command(+0x290)==4` ever-matched(누적 합집합)로 바꾸고 raw `(command,pending,xy,target)` 분포를 함께 저장한다. `pending != 1` 방식은 쓰지 않는다. 입력은 lap681에서 후보 41을 낸 흐름(공격툴바+지면클릭, 이동 목적지와 **다른** 새 목적지)을 쓰고 원본·후보 각 2회 실행한다. 공격 가능 유닛(worker 같은 `+0x1D8` bit 0x4=0 유닛 제외) 기준으로 PASS = 후보 전원(49/49), 원본 전원(≤20)이다. 후보가 21 이상이고 전원에 못 미치면 부분 결과로 기록하고, 모자란 슬롯이 청크 경계(20·40)와 맞는지 확인한다. 후보·원본 모두 0이면 이 입력은 무효 — 목적지를 바꿔 1회 재시도한 뒤 BLOCKED로 기록한다.
