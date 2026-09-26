# 2026-09-11 | lap170 | G1 카드2 검증 경계 재평가

- 실제 provider/model / 지정 역할: OpenAI Codex gpt-6-astra / 상위 방향·master-plan. 세션 effort는 별도 런타임 증거가 없어 단정하지 않는다.
- 목표/가설: 카드2 우선순위를 유지하면서 원본/후보 입력 패리티를 판정 가능한 조건으로 제한할 수 있는가.
- 예상 PASS: 이전 산출물 현물 확인, 동일 사전 상태와 입력별 관측·판정식, middle/work 경계가 명시됨. 근거 누락·충돌은 UNKNOWN/BLOCKED로 승격.
- 이전 바퀴 독립 검수: runtime_env.py SHA와 lap169 handoff 2개 SHA는 기록과 3/3 일치.
  - tools/runtime_env.py: `69b0f16253a850e02537d0d5dddbc97e43b7755cff447860a81e66914fdf0571`
  - G1_CARD2_INPUT_PARITY_HANDOFF.md: `99e888a5ecfbf7421c3b757ccbb44e2251614950a606affa124c0ed1c898ec3c`
  - G1_DXWRAPPER_FINALIZATION_HANDOFF.md: `3fd5b8fe824a7edc2f06caa163ce32fa62c906deb00729ee91d3e571221e2877`
- 검증 실패: Python hashlib로 `local/runtime/20260911_214253_1178505_0/evidence.json`을 읽는 단계에서 FileNotFoundError, exit1. 재시도하지 않았다. 해당 경로에서 읽기 실패한 사실만 확정하며 산출물 전체 유실로 단정하지 않는다. lap169의 P5 CONFIRMED는 역사적 판정으로 보존하고 이번 세션의 재검증 PASS로 쓰지 않는다.
- 원본·후보 SHA: 원본 보호 SHA는 STATUS의 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(이번 현물 검증 SKIP). 새 후보 없음.
- 환경/활성 인원/지도/군대/fixture: 신규 게임 run 0; 모두 N/A. 과거 플레이를 현재 성공으로 승격하지 않음.

## 상위 결정과 middle/work 인계

카드2를 우선하고 P6는 보류한다. G1 마감·G2 전환은 승인하지 않는다. 구현 근거가 불명확한 아래 항목은 middle이 먼저 결정한다. Astra는 게임/하네스 구현을 하지 않는다.

1. 증거 위치: lap168 P5 evidence/provenance/verdict의 실제 경로를 기존 이력에서 찾아 기록된 SHA와 독립 대조한다. 경로 누락이면 문서를 바로잡고, 현물이 없으면 검수 UNKNOWN을 유지한다. 새 게임 run을 대체 증거로 임의 실행하지 않는다.
2. 동일 상태: Stage B 전에 지도·시나리오·seed 또는 재현 가능한 시작 절차·소유자·선택 대상·camera·PS/tick 조건과 fixture 여부를 고정한다. 각 입력 전 사전 상태가 비교 가능해야 한다. 기준 충족 불가 시 비교는 UNKNOWN이며 델타 숫자 일치만으로 PASS하지 않는다.
3. 입력별 효과: unit_select/drag_select는 대상 식별과 기대 선택 집합, minimap은 목적 위치와 기대 camera 변화로 판정한다. 양쪽 무반응(delta=0)이 PASS가 되지 않게 한다. 수치 오차와 정착 시점은 middle이 실행 전에 정하고 work가 테스트로 고정한다.
4. 메뉴: 현재 Stage B 측정식은 선택·드래그·미니맵 3개만 정의한다. 메뉴의 실제 동작·기대 전이·캡처 연결이 확인되기 전 4/5 충족을 주장하지 않는다. production은 미승인 클릭 금지/BLOCKED 유지, 전체 G1 PASS 불가.
5. 판정 분리: 입력 비교 관측값, production 차단, teardown 실패를 각각 기록한다. close 결함을 관측자료 보존의 이유로 설명할 수 있으나 overall/validator/process exit/summary 요구를 완화하지 않는다. G1 출하 전 종료 결함 해소 요구를 유지한다.
6. 실행 경계: middle이 위 조건을 카드2에 반영하고 Stage A 범위를 재확인한 뒤 Luna/Sonnet5 high 실무가 하네스·회귀 테스트만 수행한다. Stage B는 그 다음 새 middle 독립 검수 뒤 별도 개방한다. 필수 게이트 예상 밖 실패는 즉시 보존·승격, 재시도 금지.

- 변경파일: docs/STATUS.md, 본 이력, loop/ESCALATE_SOL. 게임·하네스·테스트·바이너리 변경 0, uncommitted, commit/push 없음.
- 실행명령: loop/PROMPT.md부터 지정 문서 순서로 cat; git status --short; Python hashlib 읽기 검증(3개 일치 후 P5 경로 실패); 문서 보존.
- Fast/make check/safety/build/runtime: SKIP. 필수 이전 증거 확인에서 예상 밖 실패하여 사용자 지시에 따라 승격 종료한다. 과거 192 passed를 현재 PASS로 쓰지 않는다.
- 수치/판정: source/handoff 3/3 MATCH; P5 현물 재검증 BLOCKED; 게임 run 0; 구현 진행 0; 계획 승인/제품 승인 없음.
- 반복 정체 재평가: 이번 lap도 문서만 변경한다. 다음 측정 가능한 구현은 카드2 Stage A의 production 미클릭·후속 단계 진행·overall PASS 불가 회귀 및 opt-in 공용 입력 시퀀스다. 착수 전 blocker는 증거 경로와 비교 사전조건/메뉴 판정 공백의 middle 확인이다. 추가 전략 문서 반복으로 구현 진전을 주장하지 않는다.
- 다음 행동: 현재 큐는 docs/STATUS.md만 참조한다. 이번 인계 요청은 loop/ESCALATE_SOL에 보존한다.

## 이전 STATUS 다음 한 가지 원문 (lap169 provenance; 현재 큐 아님)

## 다음 한 가지

**G1 카드2 Stage A** — `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`가 기준이다.
work tier(Luna/Sonnet5, high)가 `tools/runtime_env.py`와 해당 테스트만 바꾼다:
(A-1) production fail-closed를 "중단"에서 "BLOCKED 기록 후 계속"으로 바꾸되 **클릭은 계속 금지**,
production BLOCKED 동안 overall이 PASS가 될 수 없다는 불변식을 테스트로 고정한다.
(A-2) `g1-presentation-trace`에 opt-in `--g1-input-sequence`를 추가해 PS3 이후 WM_CLOSE 이전에
`unit_select`/`drag_select`/`minimap`을 `g1_baseline`과 **동일 헬퍼·동일 논리 좌표**로 수행한다.
**×2 선변환을 새로 넣지 않는다**(lap149 계약). (A-3) 단계별 전/후 캡처 SHA·selection·camera를
**WM_CLOSE 이전에 flush**한다. (A-4) 회귀 테스트 + `make check` + safety 수치 기록.

**Stage A에서 게임을 실행하지 않는다.** Stage B(원본 1회 + 후보 1회 paired run)는 다음 middle
독립 확인 뒤에 연다. 이 저장소 선례(lap18→19→20→21)와 같은 절차다.

2순위(착수 승인 아님): **P6** wrapper 재시도 주체 판별 probe —
`docs/work/active/G1_DXWRAPPER_FINALIZATION_HANDOFF.md` lap169 절 6.
활성 카드 2개. lap169 자체의 코드 변경은 0이다.

