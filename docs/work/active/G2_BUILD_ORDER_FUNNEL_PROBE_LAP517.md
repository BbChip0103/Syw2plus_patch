# W32 — 트랙② 조선 AI 건설 오더 깔때기(점유→시작→발부→완공) 판별 probe (lap517 middle 발행)

발행: 2026-09-23 lap517 middle(Claude Code claude-opus-5-5/high), `loop/ESCALATE_SOL` §75.
지시: `docs/feedback/INBOX.md` 2026-09-23 12:55 트랙②(읽기 전용, (ㄴ) 불필요).
근거: `analysis/memory_maps/ai_build_order_scheduler_0043f5d0_lap517_20260923.md`(이하 **SCH**, N162~N167),
W31 카드 `G2_BUILD_PACE_STATE_PROBE_LAP515.md`(lap517 `CLOSED`), lap516 원시.
역할: **work(Sonnet5) 1회** 실행 → **middle(Opus5.5) 1회** 독립 검수. 상한 한 work 회차/60분·실패 가설 2.

## 0. 왜 이 카드인가

W31은 `+0xD34`만 표본해 라벨 `UNCLASSIFIED`로 끝났다. lap517이 바이트로 확인한 사실(SCH §2):
오더 종류는 `+0xD32`, `+0xD34`는 하위 상태; 스케줄러 `0x43F5D0`은 owner당 8 tick에 1회, 한가할 때(`+0xD32==0`)
`rand%20`의 index 2만 건설, 직전 건설 오더 시작(`+0x33AC`) 후 100 tick 쿨다운. 늘 한가해도 건설 오더 시작
≈91회/24k인데 관측 순증가는 9~18채(10~20%)다. **손실이 깔때기의 어느 단계인지**를 정확한 계수기로 가린다.

## 1. 성격·제약 (위반 시 즉시 중단)

- W31과 동일: 읽기 전용 런타임 read, AI/건설/생산 로직 변경 0, 메모리 쓰기 0(기존 op7 fixture 경로 제외),
  패치 후보 생성 0, 원본/참고 저장소 쓰기 0.
- fixture W29/W31과 **동일**(`_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`, 자원 각 1,000,000, cap 5,000,
  `+0x2010`=1,200, N=4001 후보 SHA `a10024de…` 재생성·대조). **게임 실행 1회, 24,000 tick.**
- **장기 실행은 포그라운드 동기 완주**(PROMPT ③). 시간이 부족하면 시작하지 말고 기록한다.
- lap516 `w31_build_pace_run.py`(SHA `1bb8140a…`)를 **복사해** 표본 필드만 추가한다(원본 수정 금지, 새 파일명
  `w32_build_funnel_run.py`). 표본 간격 0.5초 유지(간격 ≤20 tick). 새 읽기는 이미 읽는 `0x2014`B 버퍼와
  `+0x2FB8..+0x3478` 버퍼 안(`+0xD32`, `+0x33AC`)과 `+0x3A70` dword 1개뿐이다.

## 2. 작업 항목

- **M-1 표본 추가 필드(8 owner 전원, 매 표본):** `+0xD32`(word, 오더 종류) · `+0x33AC`(dword, 건설 오더 시작 tick) ·
  `+0x3A70`(dword, 건설 명령 발부 tick). 기존 W31 필드 유지.
- **M-2 집계(owner별):**
  - `f_idle` = `+0xD32==0` 표본 비율, `f_build` = `+0xD32==1` 비율, 기타 오더 종류별 비율.
  - `S` = `+0x33AC` 값 변화 횟수(건설 오더 시작). 쿨다운 100 > 표본 간격 ≤20이라 누락 불가 — 표본 간 두 번 바뀐
    흔적(간격 <100 tick 증가)이 있으면 그 자체를 결함으로 보고.
  - `C` = `+0x3A70` 값 변화 횟수(건설 명령 발부, 초기값 −10000 제외).
  - `B` = `+0x200E` 증가 합, `D` = 감소 합.
  - `S_exp` = 3,000×`f_idle` / 33 — 한가한 호출 수 추정에 SCH §2 N167의 기대 간격(쿨다운 ≈13호출 + 1/20 롤 평균
    20호출)을 적용한 **단순 모델**이다.
- **M-3 정적 확인(실행 전):** SCH §2의 `+0x3A70` 쓰기 3곳·`+0x33AC` 쓰기 2곳·`+0xD32` 쓰기 목록을 원본 바이트로
  재확인(lap517 probe A6~A8 재실행으로 대체 가능).

## 3. 사전 고정 판정식 (데이터 개봉 전)

owner별로 아래를 **모두** 평가해 성립하는 라벨을 전부 적고, 주 라벨은 비율이 가장 작은 단계로 정한다:
- `OCCUPANCY_BOUND` — `f_idle` < 0.5 (다른 오더 점유가 과반).
- `START_SHORTFALL` — `S` < 0.7 × `S_exp` (한가한데도 시작이 모델보다 적음 ⇒ SCH 모델 누락 요인 존재).
- `EXEC_FAIL_BOUND` — `C/S` < 0.5 (부지·일꾼 실패로 발부 전에 종료).
- `COMPLETION_BOUND` — `B/C` < 0.5 (발부했으나 건물 수로 이어지지 않음: 일꾼 이탈·완공 전 소실·계수 차이).
- `CADENCE_BOUND` — 위 넷이 모두 불성립(한가·시작·발부·완공이 모두 모델대로 ⇒ 1/20 롤과 쿨다운이 속도를 결정).
- 전원 판정 불가(필드 읽기 실패 등)면 `UNCLASSIFIED`(재해석 금지).
**반증 조건:** `S`가 `S_exp`의 1.3배 초과이거나 `+0xD32==1`이 아닌 표본에서 `+0x33AC`가 바뀌면 SCH §2 모델이 틀린
것이므로 라벨을 붙이지 말고 `MODEL_REFUTED`로 원시를 보고한다.
**부가:** lap516과 같은 궤적인지(owner별 건물 수 시작→끝·max used가 lap516과 일치하는지) 결정성 대조(N144).

## 4. 산출

`analysis/memory_maps/`에 결과 1장, 원시 `temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_work_w32_build_funnel/`
(스크립트·`samples.jsonl`·요약 JSON, SHA 기록), lap 기록, STATUS. 원본 SHA 전후 불변 확인.

## 5. 이 카드가 허가하지 않는 것

AI/건설 로직 변경·패치(예: 선택표·쿨다운 수정), 다른 진영 fixture 신규 구성((ㄴ)/Q8 범위), 144k 연장, G1/G4 재개.
결과가 어떤 라벨이든 **다음 조치 선택(변경 여부)은 사용자 전결**이다 — 모델은 선택지와 근거만 남긴다.

## 6. 진행 기록

- 2026-09-23 lap517 middle: 발행. W31 독립 검수 probe 16/16 PASS(산출 SHA `8802218b…`), 게임 실행 0.
- 2026-09-23 lap518 work: M-1/M-2/M-3 1회 포그라운드 실행 `PROBE_OK`(tick24,005 완주, fault0,
  N144 결정성 lap516과 불일치0/8). **§3 반증조건②가 8/8 owner에서 성립 ⇒ `MODEL_REFUTED`**(시작의
  26.6~44.3%가 `+0x33AC` 변화 표본에서 `+0xD32≠1`로 관측, 방향성은 `EXEC_FAIL_BOUND`: `C/S` 전원
  0.125~0.307<0.5). `S_short_gap_defects` 8/8 0건(쿨다운 위반 없음), `S/S_exp` 1.02~1.25(<1.3배,
  반증조건① 불성립). 게임실행1(24,005tick)·source변경0·커밋0·`SAFETY_PASS`. 전문
  `analysis/memory_maps/ai_build_order_funnel_probe_lap518_20260923.md`,
  `docs/history/laps/20260923_lap518_work_w32_build_order_funnel_probe.md`. 다음=middle 독립 검수.
- 2026-09-23 lap519 middle(Opus5.5) 독립 검수 ⇒ **`CLOSED`**. 원시 비참조 재집계에서 f_idle·S·C·B·D·반증표본이 8/8 일치했다
  (probe `docs/history/laps/probes/20260923_lap519_middle_w32_independent_review.py`, 12/12 PASS, 산출 SHA `8f22385b…` 2회 동일).
  사전 등록 규칙대로 라벨은 소급해 붙이지 않는다(`MODEL_REFUTED` 문구 유지). 다만 반증의 대상은 SCH 모델이 아니라
  **§3 반증식 자체**였다(N168). `+0x33AC`·`+0xD32=1` 쓰기는 분리할 수 없고(`0x43F88E`), 반증표본 265/267은 다음 호출(시작+8)
  이후에 찍혔다. 손실 단계는 두 번째 호출의 **상태2 `0x43E174`**다(334건 중 69.8% 종료·발부 0, N170). 실패율은 선택 종에
  따라 크게 다르다(N171). 근거 `analysis/memory_maps/ai_build_order_state2_loss_lap519_20260923.md`. 후속은 W33
  `G2_BUILD_STATE2_EXIT_PROBE_LAP519.md`.
