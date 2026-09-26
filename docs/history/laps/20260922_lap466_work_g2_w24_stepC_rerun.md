# lap466 (work, Claude Code `claude-sonnet-5` / high) -- W24 Step C rerun, RIDER_REPRO

- 날짜: 2026-09-22 KST
- 목표: G2, W24 §5 Step C 재실행 (lap465 middle이 VOID 처분한 것을 §40-2 두 필수조건으로 재실행)
- 가설: lap404 rider(cap 근접 owner의 대기 주문 `reserved` 고착)가 stock cap5000 구성에서
  **성공한 op6 생산 건물** producer + **양성 대조 선행** 조건 하에서도 재현되는가.
- 변경파일: 없음(메인 레포). 새 스크립트/산출물만
  `temp/Syw2plus_patch/g2_capacity/20260922_lap466_w24_stepC_rerun/`(script `step_c_run_v2.py`,
  `w24_step_c_rerun.md`, `step_c_run_summary.json`, `step_c_samples.json`,
  `positive_control_samples.json`, `orchestrator_stepC_v2.log`)에 저장.
  `runtime_bridge.c`/`control_executor.c`는 실행 전후 sha256 동일(변경 0, N22).
- 원본·후보SHA: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(불변,
  실행 전후 재해시 일치). 후보(`fixed_supply_5000` 적용)
  `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`. 브리지 DLL
  `4d2c738c6ff85666f2bfa46cbcb2eb5a551671126803fab35e6296b3202dc049`.
- 실행명령: `python3 step_c_run_v2.py --display :96` (동기 실행, 세션이 직접 대기, background 미사용).
- 수치:
  - Step A/B는 lap462 결과 재사용(카드 §2 지시대로 다시 파지 않음).
  - producer 배치: `op6 wanted=1 type=46`(cost20/w3/h3) anchor(10,10) → `ok:true fixture_added:1`,
    `producer_slot=1182 id=132254`.
  - 양성 대조: owner0 `used=75`에서 같은 producer_slot에 `op1 type=7` 주문 →
    417표본(0.05s 간격) 중 `reserved`가 실제로 0이 아닌 값을 거쳐 **`reserved=0·used+10`으로
    해소**(`positive_control_fired=true positive_control_resolved=true`), producer 자체 필드
    `production_type: 0→7`, `progress: 0→100`으로 독립 확증.
  - cap 근접 단계: `op5 type5 wanted=142` anchor(50,50)으로 `used=4985 count=145`까지 시딩(부분
    충족, cap 게이트 정상 작동) → 같은 producer_slot(1182, 이 시점에도 살아있고 owner0 소유
    확인)에 두 번째 `op1 type=7` 주문 → tick714→1035(65표본, 320tick 이상) 전 구간
    `reserved=10` 불변, `used=4985` 불변, 해소 0건.
  - 판정(카드 §5 실행 전 고정): `final.used(4985)>=4900 ∧ final.reserved==10` ⇒ **`RIDER_REPRO`**.
- PASS/FAIL/SKIP: `RIDER_REPRO`(PASS로 종료 — 카드 §5의 세 가지 결과 중 하나로 정직 종료).
  targeted `pytest tests/test_runtime_env.py patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` **167 passed**(lap462와 동일
  기준선). `checks/safety.sh check` → `SAFETY_PASS`. `python3 checks/context_limits.py` →
  `CONTEXT_PASS`. source 변경 0이므로 전체 `make check`는 이번 회차 면제 대상(2026-09-20 21:58
  지시, INBOX N22 정정 조건 "이번 회차에 source를 바꾸지 않았다" 충족).
- fixture: 격리 전체 게임 사본(`local/runtime/20260922_124213_3671818_0`) + 전용 Wine prefix +
  빈 Xvfb `:96`. 게임 실행 1회. wineserver -k로 정리, 실행 후 잔류 wine/Xvfb/game.exe 프로세스
  0(다른 저장소 `Syw2plus_re_loop` 소유 프로세스는 미조치). 커밋 0.
- 다음 행동: 이 결과(그리고 lap462 §2 Step A/B, lap464/465의 Step D `NO_ENGAGEMENT` ACCEPT)를
  **다음 middle이 원시 산출물만으로 독립 재검수**한다. ACCEPT 시 W24 CLOSED와 144k 금지 해제
  여부, 그리고 lap404(가) 재심(§40-2가 열었던 것)의 종결을 함께 판정한다. 모델은 (ㄴ)·
  F4(B)/(C)·마일스톤 승인에 착수하지 않는다.
- 상세 산출물:
  `temp/Syw2plus_patch/g2_capacity/20260922_lap466_w24_stepC_rerun/w24_step_c_rerun.md`.
