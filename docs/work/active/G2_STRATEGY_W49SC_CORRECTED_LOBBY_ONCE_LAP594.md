# G2 W49SC — W49S 교정 실행 정확히 1회 (lap594 strategy, 2026-09-25 KST)

- 입력: `loop/ESCALATE_SOL` §143(lap593 middle `REJECT / BLOCKED(harness_contract)`), 기록 `docs/history/laps/20260925_lap593_middle_w49s_harness_contract_reject.md`, W49S 카드 `docs/work/active/G2_STRATEGY_W49S_LOBBY_START_SCREEN_LAP589.md`(SHA256 `27ff03a5…5f88`, **이 회차에서 수정하지 않음**), lap592 raw `temp/Syw2plus_patch/g2_capacity/20260925_lap592_w49s_lobby_start/`(runner `8386a87b…6bef`, summary `0463d5e0…01ca`), 로비 PNG `62b0d8be…e3f0`.
- **G2 PASS·마일스톤 마감·G1/G4 재개가 아니다.** 결과는 S5′ 제출문 부록 B로만 붙인다.

## 1. 판정: (B) — lap592는 W49S 예산에 산입하지 않고 교정 work 정확히 1회를 예외 허가한다

strategy가 독립 확인한 사실:

1. lap592 runner는 카드 §3.3 S0(로비까지만 확인, ≤60분)를 수행하지 않았다. 슬롯 6곳을 한 번씩 누르는 고정 순서를 검증 없이 실행했고, 주석의 "한 번 누르면 AI로 바뀐다"는 근거가 없다. PNG에서 3~8번은 그대로 `없음`이다.
2. `MAP_SIZE_CLICK=(345,205)`는 선언과 summary 기록만 있고 `click()` 호출은 0회다. 주석 "기본 큰 지도=100×100"은 틀렸다. 로비는 `전장지도`, 선택 지도는 `(8인,180X180) 구절판 v1.0`이며, PS3의 실제 크기도 `[180,180]`이다.
3. runner는 카드 §3.5("S1 캡처 **직후**·시딩 전")와 순서가 반대다. active8 gate를 `start` 캡처보다 먼저 실행하고 예외로 끝냈다. `captures=[]`다. W49S가 존재하는 유일한 이유인 H-path, 즉 로비로 시작하면 월드가 렌더되는지는 **측정되지 않았다.**

이유:

- N216의 "실패하면 닫고 다시 실행하지 않는다"는 카드를 실제로 수행한 run에 적용하는 규칙이다. 고정 입력도, 측정 순서도 지키지 않은 run은 카드 run이 아니다. 선례: lap584 하네스 순환 참조 뒤 운영자 결정(수리 후 fresh 1회), 2026-09-12 승인 원칙(bounded repair → fresh validation, blind retry 금지).
- 사용자 Q12-4 "화면 1회"의 뜻은 유효한 화면 시도 한 번이다. 이 시도는 아직 이루어지지 않았다. (A)로 닫으면 "미검증"의 원인이 우리 하네스라서 사용자에게 줄 정보가 없다. (B)의 비용은 work 한 회차다.
- 재시도 예산 판단은 Q11 상시 위임에 따라 strategy 권한이다. 비가역·범위 밖 결정이 아니다.

**N218(최종 예외):** 이 예외는 한 번뿐이다. W49SC가 어떤 이유로든 실패하면 화면 축은 "미검증 확정"으로 닫는다. 하네스 결함도 예외가 아니며, 그 결함은 공개한다. 이후 재정정·재계획·재실행은 없다. lap594로 구현 무변경이 2회 연속이므로 **lap595는 반드시 이 카드의 work**다.

**N217(보고 전용, 신규):** lap592 로비 PNG에서 게임 UI는 1600×1200 화면의 좌상단 800×600만 차지한다. 기본 로비는 1번 `신규사용자`, 2번 `컴퓨터`, 3~8번 `없음`이다. 전장 종류는 `전장지도`, 지도의 크기는 `큰 지도`다. 목록의 8인 지도는 모두 180×180이다. G1(1600×1200 구성)과의 관계는 G2 성립 전까지 조사하지 않는다.

## 2. W49S 대비 변경점 (나머지 조건은 W49S 카드 그대로)

- **D1 S0 로비 탐색(≤60분, 게임 시작 버튼 금지):** 별도 격리 실행으로 로비까지만 들어간다. 매번 cleanup한다. 이 실행은 게임 1회 예산에 들어가지 않는다. 다음 두 가지를 찾는다.
  - 슬롯 3~8(R-1L7) 또는 1~8(R-AI8)을 `컴퓨터`로 만드는 실제 UI 조작. 후보는 왼쪽 클릭, 오른쪽 클릭, 드롭다운 항목 선택, 대기 후 클릭이다.
  - `전장 종류`와 `지도의 크기` 조작.
  - 시도한 조작마다 전후 로비 PNG와 좌표·대기시간을 receipt로 남긴다. 성공한 조작 순서를 고정 스크립트로 적는다.
- **D2 로비 gate(시작 직전):** 게임 시작 직전 로비 PNG에서 8개 슬롯이 모두 `없음`이 아님을 기계적으로 확인하고 receipt를 남긴다. 방법은 lap592 PNG의 `없음` 버튼 영역과 픽셀 비교하는 것이다. S0 예산 안에 이것이 안 되면 `NOT_FEASIBLE(ui_8active)`다. 게임은 시작하지 않는다.
- **D3 지도 크기:** 100×100을 우선한다. S0에서 UI로 100×100을 만들 수 없으면 가장 작은 선택지를 쓰고, 실제 `MAP_W/H`를 기록한다. 이 경우 map 조건은 gate에서 **보고 전용**으로 낮춘다. 이 run은 화면 증거일 뿐이며, 안정성 raw(W46/W47, 100×100)를 대체하지 않는다. 각 owner의 HQ49+worker7 조건은 유지한다. 따라서 시작 fixture가 없는 전장지도는 gate에서 걸러진다.
- **D4 측정 순서:** PS3 직후 `start`를 캡처하고 V1을 계산한 **다음에** active8 gate를 평가한다. gate가 FAIL이어도 `start` PNG와 V1은 raw로 남는다. 이 값이 H-path의 답이다.
- **D5 활성 판정:** `role_pass`는 nation≠0이고 HQ49·worker7이 살아 있는 owner 8명에 대해서만 계산한다. inactive owner의 `ai` flag는 세지 않는다.
- **D6 선언=실행:** runner에 선언한 UI 좌표 상수는 모두 실제로 `click()`된다. AST 테스트로 이것을 잠근다(호출 수 ≥1). 근거 없는 동작 주석은 두지 않는다.
- **D7 cleanup 뒤 결과:** `run_summary.json`은 terminate/wineserver/Xvfb cleanup **뒤에** 쓴다. 같은 display에 대한 post-cleanup receipt(대상 PID 생존 여부, `/tmp/.X*-lock` 유무)를 넣는다.
- **D8 display 하나:** vacancy 확인, Xvfb, 입력, 캡처, summary가 모두 같은 `DISPLAY` 상수 하나를 쓴다. preflight 목록 raw는 run 디렉터리에 저장한다.
- **D9 게임 전 오프라인 gate:** W49S §3의 1·2·4를 수행한다. 여기에 D4/D6/D7/D8의 AST·합성 테스트와 `json.dumps(run_summary)` 합성 테스트를 더한다. 하나라도 FAIL이면 게임 없이 `BLOCKED(gate)`로 끝내고 N218을 적용한다.

## 3. 실행과 종료

- lap592 runner에서 파생한 새 runner를 새 lap 디렉터리에 둔다. lap592 파일은 덮어쓰지 않는다.
- fresh foreground는 **정확히 1회, ≤45분**이다. S0 뒤 남은 시간이 부족하면 게임을 시작하지 않고 기록한다. 그 경우 다음 work가 S0 스크립트를 수정 없이 실행한다.
- 이후 단계·gate·라벨·금지 사항은 W49S §4·§5-4와 같다(교전·저장/로드·AI/fixture/op 변경·카메라 메모리 쓰기·새 Wine/DLL 금지, op `{5,6,7}`만). 결과와 무관하게 재실행은 없다.
- 다음 middle은 summary 없이 PNG·receipt·samples로 V1~V3·R과 D2/D4/D5를 재계산한다. 그다음 strategy가 S5′ 부록 B를 쓴다.
