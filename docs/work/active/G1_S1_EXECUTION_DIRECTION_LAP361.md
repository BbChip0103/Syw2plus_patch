# lap361 Astra — S1 실행 발효 BLOCKED / middle·work 분리

2026-09-12 / Codex gpt-6-astra / major direction/master-plan. 게임 코드 수정 0.
PROMPT의 counter=361을 사용한다(runtime 메시지 lap360, counter 변경 0).

## 1. 결정과 우선순위

M1 내부 S1 실제 로드 수집을 유지한다. **현재 실행 봉투 BLOCKED, 허가 run=0.**
lap360의 adapter 구현 ACCEPT는 입력으로 보존하지만 실행 가능한 orchestration의 승인은 아니다.
다음 측정 가능한 변화는 private 입력 helper와 accepted collector를 잇는 단일 S1 실행 경로다.
같은 adapter 테스트 반복이나 origin 연구 반복을 구현 진전으로 세지 않는다.
Stage B, WM_CLOSE/P6, G2~G4, M1 종료/M2 이동은 이번 범위가 아니다.

## 2. 독립 입력 검수와 구체 blocker

세 현행 파일 SHA는 lap360 기록의 64자리 값과 정확히 일치한다(전체 값은 lap 기록).
- `tools/runtime_env.py:5352` CLI 호출은 `read_memory`만 전달하고 `trigger`를 전달하지 않는다.
  `:3366`은 trigger=None이면 EVENT_TRIGGER_MISSING/UNKNOWN으로 종료한다. 현재 CLI 실행은 load 수집이 아니다.
- `tools/s1_load_evidence.py:252`의 trigger 호출이 반환된 뒤 `:273`에서 monotonic deadline을 만든다.
  이는 PS3 wait 상한이며 prepare/입력 callback/cleanup을 포함한 총 시간 상한이 아니다.
  기존 R1 상수 alias(default wait)를 실제 load 시간의 실측 근거로 사용할 수 없다.
- evaluator `:513`은 pre와 post selected_index가 모두 요청 슬롯과 같아야 한다.
  lap350 §3은 hit-test가 선택 WORD를 쓴다는 정적 근거만 제공한다. PS35에서 슬롯 1이 이미
  선택됐는지, 선택 입력과 load trigger가 분리 가능한지는 이번 입력으로 확정되지 않는다.
  **추론/미검증:** 첫 슬롯 클릭이 선택과 로드를 함께 일으킨다면 pre 슬롯 조건을 충족할 수
  없을 수 있다. 재현된 결함이라고 단정하거나 evaluator 조건을 완화하지 않는다.

따라서 횟수·좌표만 기입하여 실행을 발효할 구현 근거가 부족하다. 사용자 중단 지시에 따라
추가 조사·구현·필수 검사 재시도 없이 보존하고 ESCALATE_SOL로 넘긴다.

## 3. middle에 요구하는 한 봉투의 필드

| 항목 | 결정 및 middle 수용 조건 |
|---|---|
| 목적/횟수 | 향후 첫 단계는 원본 단일 load 수집 n=1 제안만 검토. 현재 0회; 후보/두 run 결정성은 별도 |
| fixture/slot | save000/group0/1-based slot1을 우선 제안. SHA `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`; 새 fixture 생성 금지. private 전체 복사 경로/복사 전후 SHA 필수 |
| 좌표/trigger | lap350 rect1 strict interior `(400,131)`은 정적 후보점일 뿐 허가 좌표 아님. 실제 origin·무배율 변환·pre selected_index와 선택/로드 사건을 연결하여 제출. Plan C 출처 금지 |
| 시간 | prepare→PS35, pre/입력 callback, PS3 wait, post 수집, cleanup의 각각 수치와 전체 상한·시간 시작점을 명시. 기존 R1 예산 자동 상속 금지; 운영 상한과 실측 성능을 구별 |
| 종료 | private prefix/PID/display만 종료하고 종료 실패를 보존. 전역 종료/재클릭/재실행/자동 연장 금지 |
| artifact | 새 디렉터리에 실행 당시 소스 스냅샷+manifest/SHA, fixture/EXE SHA, 실제 argv/시간/입력 횟수·좌표, pre/wait/post raw, reader 주소·폭, cleanup 결과. 기존 R1과 파일 분리, overwrite 금지 |
| 실패 | 사전 SHA/소유권/슬롯/좌표 결측은 NO_RUN; trigger 실패·timeout·부분 read·pre==post·fixture mismatch는 UNKNOWN과 원시 증거 보존. PS3 단독/open 성공 추정 PASS 금지 |
| 수용 | 기계 수집 유효성은 exact-once+PS35→PS3+직접 raw 변화+8×6 fixture 일치+종료 증거. scene 전체·S1 (A)+(B)·제품 합격과 구별 |

## 4. 역할별 인계와 종료 조건

middle은 §2 세 지점을 먼저 독립 검수하고, pre 슬롯 상태가 정상 UI 사건으로 구성 가능한지
`0x4D5F80` hit-test / `0x4D6B5A..0x4D6BA3` handler 및 기존 private helper를 대상으로
하나의 실행 결선 봉투를 ACCEPT/BLOCKED 판정한다. 부족한 사실은 exact address/function으로
work 읽기 전용 조사 한 개에 한정한다. 동일 정적 탐색/무변경 재시험 반복은 금지한다.
봉투가 성립하면 Luna/Sonnet5/high work가 trigger와 전체 deadline 결선 및 합성 순서/실패 회귀만
구현한다. 다음 새 middle이 targeted/lap354/Fast/safety와 편집 전후 SHA를 독립 검수한다.
그 결과 및 §3의 모든 구체 값이 제출된 뒤 Astra가 실제 실행 n/time/fixture를 별도 발효한다.
본 문서는 계획 승인/실행 허가가 아니며 middle의 게임 구현 대행과 work 자기 최종승인은 금지한다.
사용자의 ESCALATE_SOL 지시에 따라 인계한다. MODEL_ROUTING의 현재 Opus5-only 선택과 Sol
지시 차이는 공개하고 자동 호출/대체하지 않는다. 문서상의 모델 선택을 실제 호출 증거로 쓰지 않는다.
W3/N14/역사적 identity UNKNOWN/반려는 보존한다. 원본·pin·golden·과거 probe·커밋 변경 0.
