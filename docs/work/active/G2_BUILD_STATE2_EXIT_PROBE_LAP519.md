# W33 — 트랙② 조선 AI 건설 오더 상태2 종료 분기 판별 (lap519 middle 발행) — **lap521 `CLOSED`**

발행: 2026-09-23 lap519 middle(Claude Code claude-opus-5-5/high), `loop/ESCALATE_SOL` §77.
지시: `docs/feedback/INBOX.md` 2026-09-23 12:55 트랙②(읽기 전용, (ㄴ) 불필요).
근거: `analysis/memory_maps/ai_build_order_state2_loss_lap519_20260923.md`(이하 **S2L**, N168~N171),
W32 카드 `G2_BUILD_ORDER_FUNNEL_PROBE_LAP517.md`(lap519 `CLOSED`), lap518 원시(`samples.jsonl` `b695365c…`, `type_specs.json` `a23ba1d7…`).
역할: **work(Sonnet5) 1회** → **middle(Opus5.5) 1회** 독립 검수. 상한은 한 work 회차 또는 60분, 실패 가설 2회.

## 0. 왜 이 카드인가

W32 독립 검수(lap519)가 손실 단계를 특정했다. 건설 오더는 두 번째 호출의 **상태2 핸들러 `[0x43E174,0x43E2FD)`**에서
약 70%가 발부 없이 끝나고(N170), 실패율은 선택 종에 따라 1/66~12/14로 갈린다(N171). 상태2의 `F5A0` 종료는
`0x43E252`·`0x43E2D8` 두 곳이다. **어느 종료가 무엇을 검사해 종별 실패율을 만드는지**를 가린다.

## 1. 성격·제약 (위반 시 즉시 중단)

- 읽기 전용이다. AI/건설/생산 로직 변경 0, 메모리 쓰기 0(기존 op7 fixture 경로 제외), 패치 후보 생성 0, 원본/참고 저장소 쓰기 0.
- M-2 게임 실행을 하면 fixture는 W29/W31/W32와 **동일**하다(`_custom_game_chain_inject_g2_eight_ai_d4a1_seed42`, N=4001 후보
  SHA `a10024de…` 재생성·대조). 1회 24,000 tick, **포그라운드 동기 완주**(PROMPT ③). 시간이 부족하면 시작하지 않고 기록한다.
- M-2 스크립트는 lap518 `w32_build_funnel_run.py`(SHA `5054f325…`)를 **복사해** 읽기 필드만 추가한다(새 파일명 `w33_state2_exit_run.py`).

## 2. 작업 항목

- **M-0 정적 해독(필수):** `[0x43E174,0x43E2FD)`의 두 종료 조건을 원본 바이트로 적는다. 비교 피연산자,
  읽는 PlayerStruct/로스터/type_spec 필드, callee `0x43F4F0`·`0x43F550`·`0x4AFDD0`의 반환 의미를 최소 범위로 해독하고,
  `0x43E174` `mov word [edi+0x2014],bp`의 의미도 포함한다. 단언은 probe 파일(`docs/history/laps/probes/`)에 먼저 적고 실행한다.
- **M-1 정적 예측(필수, 게임 실행 없음):** M-0 조건 중 **종에만 의존하는 입력**(type_spec 필드 등)이 있으면 14종
  (40~52·105)의 통과/실패를 예측한다. 그런 다음 S2L §4 표와 대조한다.
- **M-2 런타임(조건부):** M-0 조건이 런타임 상태(일꾼 수·로스터 탐색 결과 등)에 의존하고, 그 입력을 기존 읽기 경로로
  표본할 수 있을 때만 1회 실행한다. 새 읽기 주소와 근거는 실행 전에 카드 §6에 적는다. M-1만으로 §3 판정이 나면 생략한다.

## 3. 사전 고정 판정식 (데이터 개봉 전)

- `EXIT_A_EXPLAINS` — `0x43E252` 조건만으로 M-1 예측(또는 M-2 실측)이 S2L §4 14종의 성공 다수/실패 다수 방향을 **12종 이상** 맞힌다.
- `EXIT_B_EXPLAINS` — `0x43E2D8` 조건만으로 같은 기준을 충족한다.
- `BOTH_REQUIRED` — 어느 하나만으로는 12종 미만이고, 둘을 합치면 12종 이상이다.
- `UNRESOLVED` — 둘을 합쳐도 12종 미만이거나, 해독이 60분 안에 끝나지 않는다(재해석·추측 라벨 금지, 원시만 보고).
- 반증: M-0 해독 결과 `[0x43E174,0x43E2FD)` 안 `F5A0` 종료가 2곳이 아니거나 `+0x3A70` 쓰기가 있으면 S2L §3이 틀린 것이다.
  그 경우 라벨을 붙이지 말고 `S2L_REFUTED`로 보고한다.
- "다수 방향" 기준은 S2L §4 발부율 0.5다. 43(3/5)·47(8/17)·52(6/17)처럼 경계에 가까운 종도 그대로 센다.

## 4. 산출

`analysis/memory_maps/`에 결과 1장, probe(`docs/history/laps/probes/`)와 산출 SHA, lap 기록, STATUS를 남긴다.
M-2를 실행했으면 원시를 `temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_work_w33_state2_exit/`에 둔다. 원본 SHA 전후 불변을 확인한다.

## 5. 이 카드가 허가하지 않는 것

상태2 조건·선택표·쿨다운 수정 같은 AI/건설 로직 변경과 패치, 다른 진영 fixture 신규 구성((ㄴ)/Q8 범위), 144k 연장, G1/G4 재개는 허가하지 않는다.
결과가 어떤 라벨이든 **다음 조치(변경 여부) 선택은 사용자 전결**이다. 모델은 선택지와 근거만 남긴다.
이 카드가 정적만으로 끝나면 lap519에 이어 **실행 증거 무증가 2회째**다. 그다음 회차는 strategy/middle이 트랙② 지속 여부를
먼저 판정해야 한다(PROMPT ③).

## 6. 진행 기록

- 2026-09-23 lap519 middle: 발행. W32 독립 검수 probe 12/12 PASS(산출 SHA `8f22385b…` 2회 동일), 게임 실행 0.
- 2026-09-23 lap520 work(Sonnet5): M-0 완료(단언 8/8 PASS, S2L §3 미반증). EXIT_A=첫 루프
  종-무관(사이트 소유권 맵+랜덤), EXIT_B=`AFDD0(edi,kind,...)` 종-의존(`0x9B5228+kind*0x394`
  레코드 `+0x16`/`+0x18`, kind 41/56/68 반경 오버라이드). M-1 = `UNRESOLVED_STATIC_ONLY`
  (종-의존 파라미터가 `.data` raw 밖, 즉 런타임 전용이라 순수 정적 신호는 kind41 1종뿐 ⇒
  14종 중 13종 정적 판별 불가). 신규 발견 필드 `+0x3A74`(word, EXIT_B 전용 마커, 리셋 미검증).
  M-2 새 읽기 주소 선언: `TYPESPEC_BASE(0x9B5228)+kind*0x394+0x16`/`+0x18`(기존
  `read_type_specs()` 확장, **PS3 시점 단발 스냅샷으로 충분 — 24k tick 소크 불필요**),
  보조로 `+0x3A74`(리셋 검증 필요). 게임실행0·source변경0·커밋0·`SAFETY_PASS`·`CONTEXT_PASS`.
  probe `docs/history/laps/probes/20260923_lap520_work_w33_state2_exit_decode.py`(8/8 PASS,
  산출 SHA `899db3f9…` 2회 동일). 근거 `analysis/memory_maps/ai_build_state2_exit_decode_lap520_20260923.md`.
  **실행 증거 무증가 2회째(lap519도 게임실행0) — 카드 §5대로 다음은 strategy/middle이 트랙②
  지속 여부를 먼저 판정한다.**
- 2026-09-23 lap521 middle(Opus5.5) 독립 검수 ⇒ **`CLOSED`(라벨 미부여)**.
  - M-0 뼈대는 ACCEPT다. EXIT_A는 callee F4F0까지 종-무관이다.
  - 정정 N172~N176:
    - `0x4A4E70`이 kind를 받는다. 41/56/68은 술어 `0x4A4BF0`로 간다.
    - `+0x16`/`+0x18`은 footprint다.
    - M-1 "정적 불가" 전제는 REJECT다. 참고 캡처 `d7bf3e1f…`가 런타임 표와 152/152 일치한다.
    - `+0x3A74`는 sticky 플래그라 카운터로 쓸 수 없다.
    - 두 번째 F4F0 경로가 누락됐다.
  - footprint 예측은 11/14(R1)·12/14(R2)이고 반례는 50·105다. 사후 임계라서 §3 라벨을 부여하지 않았다.
  - 트랙② 진단은 이 깊이에서 종료한다. M-2는 발행하지 않는다.
  - 근거: `analysis/memory_maps/ai_build_state2_footprint_review_lap521_20260923.md`, `ESCALATE_SOL` §79.
