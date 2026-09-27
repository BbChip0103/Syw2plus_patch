# 2026-09-27 | lap 712 | 목표 G4

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / work tier(실무).
- 가설 / 사용자 관찰: 2026-09-27 12:05 운영자 판정(G4 길찾기 트랙 종료, 자유대전 AI로 전환) 다음 work
  ①②를 그대로 수행 — 기존 G4 AI 계측(`tools/inmm_stub/ai_shadow.c`가 아니라, 그 계측이 이미
  검증한 것과 같은 `state()` player/unit 스냅샷을 쓰는 `tools/runtime_env.py g1-baseline`
  `--g4-chain-goal`/`--g4-sample-seconds` 경로)으로 원본 AI 1 대 1 자유대전(2인, 둘 다
  `ai==1`)을 N분(4.67분=280초) 진행하며 AI 행동 지표(자원 수입·생산량·군대 규모·첫 공격 시각·
  유휴 일꾼 수) 원본 N=3을 측정하고, 가장 약한 지표 1개를 v1 목표로 STATUS에 기록한다.
- 예상 PASS / FAIL 조건: N=3 fresh 실행이 원본 SHA 불변·cleanup ok로 완주하고, 5개 지표를 owner별로
  산출하면 측정 자체는 성립(`FEASIBLE`). 후보 v1 구현은 이 lap에서 "가능하면"(선택)이며, 강제
  예산은 없다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `tools/g4_ai_behavior_probe.py`,
  `tests/test_g4_ai_behavior_probe.py`. 게임 EXE/DLL/원본/참고 저장소는 미변경. uncommitted
  (`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(3회 실행 전후 6/6 불변).
  후보 없음(candidate AI 정책 미도입, 읽기 전용 관측). 소스 루트
  `/home/dev_00/sharedfolder/260320_Syw2plus/[ESL]Syw2plus`(2026-09-26 22:52 경로 전환 이후 기본값).
  `--g4-chain-goal _custom_game_chain_inject_seed1`(기존 2026-09-16 lap이 검증한 고정시드
  2인 자유대전 fixture, `control_bridge=True`/`synthetic=True`, 두 owner 모두 `ai=1`).
  owner0=nation1(HQ type49/worker type7), owner1=nation2(HQ type58/worker type31), 시작
  rice=wood=7500(합계15000)/count=2(HQ+worker)/cap=1500 각 owner 동일. N=3, `--sample-seconds
  280 --sample-period 1.0`(280 sample/run).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python tools/g4_ai_behavior_probe.py
  --chain-goal _custom_game_chain_inject_seed1 --sample-seconds 280 --sample-period 1.0
  --repeats N --artifact-root <temp>/g4_ai/20260927_032708_lap712_g4_ai_behavior_baseline
  --out <temp>/.../behavior_baseline*.json`(첫 1회는 repeats=1로 단독 실행 후 CLI 종료코드 처리
  버그를 고쳐 2회 추가 실행). 산출물
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g4_ai/20260927_032708_lap712_g4_ai_behavior_baseline/`
  아래 `run0_g1_baseline.json`(run0 원문 evidence), `behavior_baseline_runs12.json`(run1/2 원문),
  `behavior_baseline_aggregate_n3.json`(3회 지표 집계). 각 run의 `g1-baseline.log`/prefix는
  해당 `local/runtime/g4-ai-behavior-baseline/run_*/runtime/*/output,prefix`에 보존, `game`
  사본(~600MB~2.7GB)은 회차 종료 직후 삭제(디스크 위생, 코드에 내장).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): `FEASIBLE_BASELINE`(3/3 재현). 280 sample/run 전부
  `ps==3`, tick 8→~5591~5827(run마다 근소한 tick 차이는 있으나 owner별 최종 unit 구성·자원·생산
  수치는 3/3 완전히 동일 — 결정적 고정시드 재현 확정). owner별 지표(3회 값 동일, 대표값 1개):
  - owner0(nation1): `production_count_proxy`=21, `idle_worker_count_mean`=0.679(`max`=3),
    `army_unit_count` 0→16(mean 6.18), `resource_stock` 15000→9792(`income_per_min`≈**-1119**,
    순감소), `first_attack_elapsed_seconds`=None.
  - owner1(nation2): `production_count_proxy`=12, `idle_worker_count_mean`=0.129(`max`=1),
    `army_unit_count` 0→10(mean 3.82), `resource_stock` 15000→23068(`income_per_min`≈**+1734**,
    순증가), `first_attack_elapsed_seconds`=None.
  - 두 owner 모두 280초 동안 `command==4`(공격) 유닛 0, `hp_decrease_same_unit`=0,
    `slot_disappearances`=0 — 전투 접촉 자체가 0건(3/3 재현).
  **가장 약한 지표로 `idle_worker_count`를 채택**: owner0이 owner1보다 평균 유휴 일꾼이
  약 5.3배 많고(0.679 대 0.129, 시작 일꾼 각 1기에서 생산 후에도 이 비율 유지), 이는 owner0의
  순자원 감소(생산/소비가 수입을 추월)와 시간적으로 같이 간다. **단, 이 비대칭은 owner0=nation1
  대 owner1=nation2라는 특정 matchup/slot에 묶여 있어 2026-09-16 lap의
  `NO_GO_GENERIC_AI_IMPROVEMENT`(국가 교환 시 효과가 반전되는 matchup 의존 편향) 선례와 같은
  성격일 수 있다 — 이번 lap은 이 nation 조합 하나만 측정했으므로 범용 AI 결함으로 아직 승격하지
  않는다.** `첫 공격 시각`은 3/3 모두 미관측(280초 내 전투 없음) — 2026-09-16 lap의 동일
  `seed1` fixture(옛 소스 경로 `Syw2plus/`)는 240초 안에 실제 첫 피해(146~198초)를 재현했었다.
  새 소스 경로(`[ESL]Syw2plus`, 2026-09-26 22:52 전환)로 재측정한 이번 lap은 같은 시드에서
  280초까지도 접촉이 없다 — Data/맵 파일 차이 가능성이 있는 **미해결 불일치**로 기록하고 원인은
  조사하지 않았다(범위 밖).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 신규 회귀 테스트 4개(`compute_behavior_metrics`
  순수 함수, 게임/EXE 불필요) 전부 PASS. `make check` **1054 passed(867.50s)**, ruff/compileall/
  mypy/`CONTEXT_PASS`/`checks/safety.sh check`(`SAFETY_PASS`) 전부 PASS. work tier 판단으로
  다음 middle 검수를 강제 요청하지 않는다(제품 후보·EXE 변경 없는 순수 관측, G4-P1 baseline lap
  704~707과 같은 성격). 남은 위험: (1) idle-worker 비대칭이 범용인지 matchup 의존인지 두 번째
  nation 조합(예: 코드 교환) 없이는 알 수 없다. (2) `첫 공격 시각` 불일치(옛 경로 vs 새 경로)는
  원인 미상이며 이번 lap이 조사하지 않았다. (3) `army_unit_count`는 초기 HQ/worker 타입만 제외한
  근사치라 이후 건설된 건물도 포함될 수 있음을 코드 docstring에 명시했다.
- 다음 한 가지: **v1 목표 = idle_worker_count 개선(owner0 계열, 유휴 일꾼 재배치 완료 조건)**,
  단 이 lap은 STATUS에 기록만 하고 구현하지 않는다(2026-09-16 lap이 동일 selector
  `FUN_0043F5D0`의 cooldown 상수(case2/3, opcode1/3)를 blind로 낮춰 두 번 `NO_GO`를 받았고,
  "완료 조건·명령 품질을 직접 계량한 뒤 정하라"는 그 lap의 명시적 지침과 일치하려면 먼저
  `FUN_0043F5D0` case 3가 호출하는 `FUN_004B03D0`(채집지 순환 상태기, 2026-09-16 lap 기록)
  자체의 재배치 완료/실패 조건을 정적으로 특정해야 한다 — 이번 lap은 그 특정 작업을 시작하지
  않았으므로 다음 work가 그 정적 특정부터 한다). 다음 work: ① `FUN_004B03D0`을 Ghidra/objdump로
  읽어 "유휴 일꾼을 새 채집지에 재배정하는" 조건과 실패/재시도 경로를 특정, ② 두 번째 nation
  조합(예: owner0/1 국가를 바꾼 `_custom_game_chain_inject_ming_joseon_seed1` 등)으로 이번
  N=3와 같은 idle_worker_count 측정을 반복해 matchup 의존인지 재확인, ③ 가능하면 그 정적 특정을
  근거로 완료조건 기반 v1 후보 1개를 구현. `첫 공격 시각` 옛/새 경로 불일치는 후순위 별도 관찰로
  보존(이번 lap 범위 밖).
