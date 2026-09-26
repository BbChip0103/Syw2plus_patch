# 2026-09-21 | lap 462 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / **실무(work)**.
  카드 `docs/work/active/G2_MIXED_COMPOSITION_COMBAT_CYCLE_SOAK_LAP461.md`(W24, lap461 middle 발행)
  Step A→B→C를 실행. Step D는 §9 60분 상자 규칙에 따라 다음 work 회차로 이월(재계획 아님).

- 가설 / 사용자 관찰: 카드 §1 질문 — "수리후보가 cap 근접+안정을 넘어 혼합 구성(건물 계층)과
  전투/사망/슬롯 재사용 순환까지 포함한 상태로 24k tick을 버티는가?" Step A/B/C는 그 질문에
  답하기 전에 필요한 사전조건(구성 결정, 판정기 수리, lap404 rider) 3건을 해소한다.

- 예상 PASS / FAIL 조건: Step A는 `BUILDING_SEEDABLE`/`BUILDING_BLOCKED` 중 하나로 끝나면 PASS.
  Step B는 음성대조 2건이 모두 발화하면 PASS. Step C는 `RIDER_REPRO`/`RIDER_NO_REPRO`/
  `RIDER_BLOCKED` 중 하나로 끝나고 fail-closed 산출물이 남으면 PASS(어느 결과든 그 자체가 증거).

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 저장소 소스 변경 **0건**. `control_executor.c`/`runtime_bridge.c` 재해시로 실행 전후 불변 확인
    (`control_executor.c` sha256 `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`,
    두 스텝 모두 실행 전후 동일).
  - `docs/STATUS.md` 편집(압축+G2/다음한가지/바퀴기록 갱신, 128→124줄).
  - `docs/history/20260921_status_lap462_precompaction.md` 신설(압축 전 전문 보존, SHA
    `0b8d73aa3724c18a59e36368ee1b90fe972a73599be431564fbced5b75b1dc06`, 128줄).
  - `docs/feedback/INBOX.md`에 이 lap 요약 항목 추가(별도 편집).
  - 임시 실행 스크립트/산출물(레포 밖, 커밋 대상 아님): 아래 경로.
  - 커밋: 없음(`LOOP_ALLOW_COMMITS=0`, 기본 유지).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(Step A/C 실행 전후
    직접 재해시로 불변 확인).
  - Step A/B 후보: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(재빌드로 SHA
    확인, N=4001, 8 owner 전원 `ai=1`, goal `_custom_game_chain_inject_g2_eight_ai_seed42`, map
    100×100). bridge dll sha256 `7c195b274c128cc362f7d7bd17c1d0fd75bef4c2514445d74d7bc0528ef5c3ff`.
  - Step C 후보: `fixed_supply_5000.py`가 원본에서 생성(stock 1200 레이아웃 + cap 5000, 2곳 편집,
    길이불변), 산출 sha256 `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`.
    bridge dll(capacity 치환 없음, 기본 1200) sha256 `df6531c678b26e39da341e1b7a74346e766f262ce1d368e674c19ba946e99828`.
    goal `_custom_game_chain_inject_g2_eight_seed42`(non-AI 8인 진입 체인).
  - 격리 전체 게임 사본 + 전용 Wine prefix + 빈 Xvfb display(:91 Step A, :93 Step C), 각 run 후
    `wineserver -k`/Xvfb 종료로 정리, 잔류 프로세스 0.

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 산출물 루트: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/20260921_lap462_w24_stepA_type_table_inventory/`
    - `step_a_run.py` → `type_table_inventory.json`, `fingerprint.json`, `run_summary.json`,
      `orchestrator.log`.
    - `compute_verdict461.py` → `verdict_gate_negative_control.json`(자체 실행 시 재생성).
    - `step_c_run.py` → `step_c_samples.json`, `step_c_run_summary.json`, `orchestrator_stepC.log`.
  - Step A: `python3 step_a_run.py --display :91`, exit 0, verdict `PASS`.
  - Step B: `python3 compute_verdict461.py`, exit 0, `all_fired: true`.
  - Step C: `python3 step_c_run.py --display :93`, exit 0, verdict `RIDER_NO_REPRO`.
  - 사후 검증: `checks/safety.sh check` → `SAFETY_PASS`; 원본 exe 직접 재해시 불변 확인;
    표적 `pytest tests/test_runtime_env.py patches/population/test_fixed_supply_5000.py
    patches/population/test_g2_full_capacity_persistence_compat_v1.py` → **167 passed**
    (source 미변경이므로 전체 `make check`는 재실행하지 않음, N22 규칙).

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **Step A = PASS, 판정 `BUILDING_SEEDABLE`.** 타입 표 `0x9B5238+t*0x394`(t=0..199) 전수 읽기,
    read_failed 0건. B집합(width≥2∧height≥2) 44개, C집합(가드통과) 73개, B∩C 38개
    t={1,40,41,43-74,105-107}. 대표 t=46(cost20,width3,height3,flags0) — cost20 동률
    {46,61,64,67} 중 최소 t로 결정적 선택(코드가 `max()`의 첫 일치 원소를 취함, 관측값 표에
    전수 기록). type5 참조 cost35/w1/h1/f0, type7 참조 cost10/w1/h1/f0(둘 다 op5/op6 하드코딩과
    일치, 대조 확인). flags가 type5/type7과 다른 t 64개를 관측값으로만 나열(해석 안 함).
  - **Step B = PASS.** `compute_verdict461.py`가 원시 samples만 사용. 음성대조 (a) 최종 tick
    12,000 절단 합성 입력 → `ARM_FAIL`(사유 `final_tick 12000 < stop_tick 24000`) 발화 확인.
    (b) 8번째 owner `ai=0,used=20` 합성 입력 → `final_active_used`에서 그 owner 배제, D/verdict
    계산에서도 미포함 확인. 두 건 모두 `fired: true`.
  - **Step C = PASS, 판정 `RIDER_NO_REPRO`.** owner0 PS3 진입 시 `count=2,used=20,cap=5000`(구식
    goal의 기본 시작 유닛 — Step C가 non-AI goal을 쓴 이유는 AI가 같은 관찰 창에서 별도 주문을
    걸어 결과를 오염시키는 것을 막기 위함). op7 자원공급 → 함정1 스모크(op5 wanted=1,
    `fixture_added=1`, `fixture_failed` 미설정 확인) → op5 wanted=141(총 142기, cost35×142=4,970,
    baseline 20 포함 `used=4,990`) → op6 wanted=3(요청 3건 중 1건만 배치되고
    `fixture_exceeds_unreserved_supply`로 중단 — **이는 seeding 실패가 아니라 cap 게이트가
    정확히 설계대로 작동해 `used`를 정확히 5,000에서 멈춘 것**; 배치된 마지막 유닛=슬롯1041,
    type7, owner0) → op1 Train 주문(owner0, slot=1041, type=7, cost10): `ok=true,
    raw_return=1`이나 응답에 담긴 producer 필드(`command/progress/production_type`)는 호출
    전후 불변. 이후 tick12→333(320tick 관찰) 동안 owner0 `reserved`는 **전 표본 0**, `used=5000`
    고정, `count=145` 고정 ⇒ `RIDER_NO_REPRO`(카드 §5 판정식을 그대로 적용).
  - **방법론 유보(미해결, 다음 middle에 인계):** producer로 쓴 슬롯1041은 owner0의 실제 생산
    건물이 아니라 op6로 막 배치된 개체이며, op1 호출이 그 개체에 실제로 무언가를 큐잉했다는
    독립 확증(예: `command` 변화)이 없다. `ok=true/raw_return=1`과 op1 코드 자체의
    "producer_not_alive_or_owned" 미발동만으로 카드 §5가 요구하는 "producer 유효성"을 충족했다고
    보고, 그 결과 `reserved`가 0으로 유지된 것을 그대로 `RIDER_NO_REPRO`로 기록했다. 이 선택이
    lap412(원 발견, AI 자연생산 경로)와 이 rider(수동 op1, 기하학적으로 임의인 producer) 사이의
    실행 경로 차이를 완전히 통제하는지는 검증되지 않았다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 회귀 0건(원본/`control_executor.c`/`runtime_bridge.c` 전부 불변, source 변경 없음).
  - **lap404(가)(전비 장부 rider에서 일시 초과를 허용할지) 잠정채택이 이 결과로 재심 대상으로
    승격된다**(카드 §5 정의 그대로 적용) — **모델은 이 재심을 대신 마감하지 않는다.** 다음
    middle/strategy가 위 방법론 유보를 먼저 검증(가능하면 실제 생산 건물을 producer로 쓴
    재현 시도, 혹은 이 결과를 그대로 인정할지 판단)한 뒤 판정해야 한다.
  - Step D는 실행되지 않았다. §7 최종 verdict(`CYCLE_STABLE`/`NO_ENGAGEMENT`/`CYCLE_UNSTABLE`/
    `ARM_FAIL`)는 미확정.
  - 이 lap의 세 결과(Step A/B/C)는 모두 **자기판정(work)이며 다음 middle의 독립 재계산 검수를
    거치지 않았다.**
  - 144k 카드 발행 금지는 W24 실행+독립검수 ACCEPT까지 유지(§38 판정5).

- 다음 한 가지: 다음 work 회차(Sonnet5)가 카드 §6 규칙대로 Step D(혼합구성 24k soak)를 곧바로
  실행한다 — 재계획·새 카드 금지(§9). 대표 건물타입(t=46) 포함 시 `runtime_bridge.c`의 op5/op6
  type 하드코딩 확장이 필요하므로 그 회차는 source 변경과 통합경계 `make check` 전체 1회를 함께
  수행하고, 판정기는 이 lap의 `compute_verdict461.py`를 그대로 쓴다(수정 없이 재사용, 또는
  §10 이월 결함이 있다면 그 회차가 함께 고친다). 별도로 다음 middle/strategy는 위 방법론
  유보와 lap404(가) 재심을 함께 처리해야 한다.
