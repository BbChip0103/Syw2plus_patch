# W31 — 트랙② 건설 선택 로직: 조선 AI 건설 속도 병목 판별 probe (lap515 middle 발행)

발행: 2026-09-23 lap515 middle(Claude Code claude-opus-5-5/high), `loop/ESCALATE_SOL` §73.
지시: `docs/feedback/INBOX.md` 2026-09-23 12:55 트랙②(읽기 전용, (ㄴ) 불필요).
근거: `analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md`(이하 **FG**),
`analysis/memory_maps/ai_production_decision_path_00406770_20260923.md`, lap507 W29 원시, lap513 원시.
역할: **work(Sonnet5) 1회** 실행 → **middle(Opus5.5) 1회** 독립 검수. 상한 한 work 회차/60분·실패 가설 2.

## 0. 이 카드가 바뀐 이유 (STATUS 초안 대비)

STATUS 초안의 측정식 "18개 미건설 종 각각의 추첨 진입 조건 18/18"은 **lap515 정적 probe로 이미 닫혔다**:
18/18 = `FACTION_BLOCK`(FG §1·§2, fixture 전원 조선 `nation=1`, 일꾼 kind 7). 또 `FUN_00406C70`은
**유닛 생산** 추첨이고 건물 건설 결정은 `FUN_0043E0E0`→`FUN_0043DBB0`이다(FG §5). 남은 표적은
"왜 안 짓나"가 아니라 **"조선 AI가 왜 느리게 짓나"** — 조선 유닛 천장 2,835라 5,000에는 건물
≈160채(보급 ≥2,165)가 필요한데 24k tick 관측은 11~20채이고 건설은 끝까지 진행 중이다(FG §4).

## 1. 성격·제약 (위반 시 즉시 중단)

- **읽기 전용 런타임 read + 정적 디스어셈블.** 원본/참고 저장소 쓰기 금지, AI/건설/생산 로직 변경 0,
  메모리 쓰기 0(fixture 설정 기존 경로 제외), 패치 후보 생성 0.
- fixture는 W29와 **동일**(`_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`, 자원 각 1,000,000, cap 5,000,
  `+0x2010`=1,200, lap506 스크립트 그대로 `CAPACITY=4001` N=4001 후보 — W29 후보 SHA `a10024de…`를 재생성·대조).
  결정적 궤적(N144)이라 **게임 실행 1회**, 24,000 tick.
- **장기 실행은 포그라운드 동기 완주**(PROMPT ③ 마지막 항). 시간이 부족하면 시작하지 말고 기록한다.
  lap506 `w29_ceiling_run.py`를 **복사해** 표본 필드만 추가한다(원본 스크립트 수정 금지, 새 파일명).

## 2. 작업 항목 (순서 고정)

- **M-0 정적(실행 전):** `0x43FBBF`가 속한 switch(jump table `0x43FD60`)의 selector 필드·호출 경로를 원본
  바이트로 확정해 `FUN_0043E0E0`의 **호출 케이던스**(tick 조건·owner 순번)를 적는다. `FUN_0043E0E0`의
  상태 2·3·4(`0x43E174`/`0x43E2FD`/`0x43E5A0`)가 각각 무엇을 기다리고 언제 1로 돌아가는지(`FUN_0043F5A0` 포함)를
  바이트 근거로 표 1장. 불명은 UNKNOWN으로 둔다.
- **M-1 런타임 표본(매 20 tick 이하, 8 owner 전원):** PlayerStruct `+0xD34`(건설 상태) · `+0xD36`(선택 건물 kind) ·
  `+0xD38` · `+0x200E`(건물 수) · `+0x200C`(used) · `+0x200A`(count) · `+0x33B0..+0x3477`(200B 후보 마스크, 마지막
  `FUN_0043DBB0` 호출 결과) · `+0x314C..+0x315B`(블록 플래그) · `+0x2FB8`(건물 종별 수, 200 short). 로스터 kind 7
  개수(일꾼)는 종단과 1,000 tick마다. M-0에서 새로 확인된 대기 대상 필드가 있으면 추가한다.
- **M-2 집계:** owner별 (a) 상태별 체류 tick 비율, (b) 상태1 진입 횟수 대비 건물 증가 횟수(선택 성공률),
  (c) 건물 1채당 평균 tick, (d) 후보 마스크 활성 종 수 vs FG §4 한도식으로 재계산한 "한도 미만 후보" 수 시계열.

## 3. 사전 고정 판정식 (데이터 개봉 전)

owner별 지배 병목을 **체류 비율 최대 상태**로 정하고 다음 라벨 하나를 붙인다:
- `SELECT_EMPTY` — 상태1 체류가 최대이고 "한도 미만 후보" 0인 표본이 상태1 표본의 ≥50%.
- `SELECT_OK_EXEC_WAIT` — 상태 2/3/4 중 하나의 체류가 최대 ⇒ 선택 뒤 실행(배치·일꾼·건설 시간) 대기가 병목.
  M-0 표로 어느 대기인지 이름을 붙이고, 이름을 못 붙이면 `EXEC_WAIT_UNKNOWN`.
- `CADENCE_BOUND` — 상태 전이 간격이 M-0 호출 주기와 같고 상태 체류가 고르게 짧다 ⇒ 호출 빈도 자체가 병목.
- 위 셋에 안 들면 `UNCLASSIFIED`(재해석 금지, 원시 그대로 보고).
**부가 산술(필수):** owner별 관측 건설 속도로 조선 건물 보급 2,165 도달 예상 tick을 선형 외삽하고
"외삽일 뿐"이라고 병기한다. 전투로 건물 수가 감소한 사건(`+0x200E` 감소)은 따로 센다.

## 4. 산출

`analysis/memory_maps/`에 결과 문서 1장, 원시 `temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_work_w31_build_pace/`
(스크립트·`samples.jsonl`·요약 JSON, SHA 기록), lap 기록, STATUS. 원본 SHA 전후 불변 확인.

## 5. 이 카드가 허가하지 않는 것

AI/건설 로직 변경·패치, 다른 진영 fixture 신규 구성((ㄴ)/Q8 범위), 144k 연장, G1/G4 재개.
결과가 어떤 라벨이든 **다음 조치 선택(변경 여부)은 사용자 전결**이다 — 모델은 선택지와 근거만 남긴다.

## 6. 진행 기록

- 2026-09-23 lap515 middle: 발행. FG probe 18/18 PASS(산출 SHA `7acf03c9…`). 게임 실행 0.
- 2026-09-23 lap516 work(Sonnet5): M-0(정적) + M-1(24k 런타임, 8 owner, 1,439표본) + M-2(집계) 완료,
  `PROBE_OK`. 신규 발견: `+0xD34`는 건설 전용이 아니라 20종 AI 오더 공용 필드이고, 실패 시
  `FUN_0043F5A0`이 그것을 0으로 리셋(재시도 아니라 오더 종료). 상태0(비활성) 지배 85.6~87.9%,
  상태1은 표본 해상도(~17tick)에서 0회 포착, 그런데도 건물은 owner당 9~18채 순증가(감소 0).
  라벨 = **`UNCLASSIFIED` 8/8**(재해석 금지, `CADENCE_BOUND`와 정성적으로만 부합, 재무장 스케줄러
  미해독). 전문 `docs/history/laps/20260923_lap516_work_w31_build_pace_state_probe.md`,
  근거 `analysis/memory_maps/ai_build_pace_state_probe_lap516_20260923.md`. 다음 = middle 독립 검수.
- 2026-09-23 lap517 middle(Opus5.5) 독립 검수 ⇒ **W31 `CLOSED`**(라벨 `UNCLASSIFIED` 8/8 유지). probe
  `docs/history/laps/probes/20260923_lap517_middle_w31_independent_review.py` 16/16 PASS(산출 SHA `8802218b…`).
  M-2 원시 비참조 재집계 불일치 0/8(ACCEPT). M-0 부분 기각: 오더 종류는 `+0xD32`(실행 switch 27칸),
  `+0xD34`는 하위 상태(N162) · `FUN_0043F5A0`은 성공·실패 공통 종료(N163) · 재무장 스케줄러 `0x43F5D0` 해독
  (owner당 8 tick 1회, `rand%20` index2, 100 tick 쿨다운, N164) · "상태0=비활성" 기각(N165) · 외삽식 카드 이탈(N166)
  · 건설 오더 천장 ≈91/24k 대비 관측 10~20%(N167). 근거 `analysis/memory_maps/ai_build_order_scheduler_0043f5d0_lap517_20260923.md`.
  후속 = W32 `G2_BUILD_ORDER_FUNNEL_PROBE_LAP517.md`.
