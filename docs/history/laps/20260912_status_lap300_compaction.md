# docs/STATUS.md 원문 보존 — lap300 압축 직전

- 보존 시점: 2026-09-12, lap 300 (middle/Opus5/high)
- 원문 SHA256: `620d91fd8ab2a938e790c002897006db12dfd1b6db3c8199e5396fc7faebf426`
- 원문 줄 수: 125
- 사유: lap300 판정을 반영하면 130줄 상한을 넘으므로 loop/PROMPT.md에 따라 원문을 먼저 보존한다.
- 이 파일의 승인/반려/미결 근거는 삭제하지 않는다.

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력. 제품 기준은
DESIGN, 사람 승인 원문은 feedback/APPROVALS와 INBOX를 따르며 사용자의 2026-09-12 01:03 bounded
repair→fresh validation 허가는 제품/출시 승인이 아니다. DxWrapper 출력/30초 렌더 과거 근거는 있으나
실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.

lap275 middle이 F3-R2-R1을 선언 범위 승인(offline 기계 증거, producer 6종·comparator 일치, 새 PASS
경로 0). lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을 지우지 않는다.

G1-S1 계약 계보(상세 `…/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.1~§4.7, 근거는 lap276~296 기록):
Astra 방향 → 측정식 반려·대체 → work 정적 조사 → 여섯 행 CONFIRMED → 교차검증 수용(정정 2건) →
상수 3개를 `tools/runtime_env.py`로 승격 → 새 objdump 독립 검수(정정 1건). 이 계보는 **S1 fixture의
정적 타당성**이며 두 run의 값 동일성·제품 증거·Stage B 허가·마일스톤 종료가 아니다.

runtime/load 계보(상세 `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md`): lap283 Astra 결정
→ lap284 middle이 여섯 필수 입력을 ACCEPT1/조건부1/REJECT4로 판정 → lap290~296은 전부 lap280
probe 하네스 건전성이었고 lap296이 lap295 수리를 ACCEPT해 §4.4.3 종결 → lap297 Astra가 세 결정
(tick report-only / load 별도 evidence / fixture 후보 유지)을 내고 승격 → **lap298 middle이 §10에서
ACCEPT·ACCEPT·ACCEPT-WITH-CORRECTION으로 판정**하고 lap284 §7의 "타이틀 불러오기 좌표" 가설을
열어 게임 실행 0으로 좌표를 확정했다. **runtime 예산 요청 없음, Stage B 0 유지.** 제품 G1~G4
증거는 여전히 0이고 S1 카드 종결은 REJECT 유지.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |

## 다음 한 가지

**다음 한 가지: 새 middle(Opus5/high)이 lap299 work의 정적 레이아웃 probe와 lap296 §4.7.6
guard 수리를 독립 검수한다.** 정적 후보는 7 rect/버튼 geometry만 다루며, 슬롯 클릭·로드 전이는
UNKNOWN이다. 그 전에는 하네스·게임/Wine/Xvfb/Stage B/PNG/runtime 예산을 변경·실행하지 않는다.

## 지금 막힌 것 (Blockers)

- S1/F2-R2 실제 결정성 미해결. Stage B·원본 재실행·Wine/Xvfb·R6-A/R6-C 금지. production 클릭
  금지(정상 비활성은 BLOCKED로 남기고 후속 입력은 계속). 원본/제품 EXE·DLL/assets/baseline/golden
  변경, evidence 재사용, blind retry, PASS 완화 금지.
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은 기계
  검사 밖이며 (B) 원시 필드 대조로만 확인한다. overall PASS도 충분조건이 아니다.
- `scene.owners`는 owner0~7, offsets는 owner0/1만 본다. owner8~15는 장면 서명에 안 보인다(G3 위험).
- R17 구조 재결 미완료·R31 금지, R29 범위 승인 거부(lap266), R30 M11 생존 유지, R6-B-R2의
  count 1→0 응답 판정 미결(규칙 변경 금지). lap274 추출기의 M-d/M-e 생존은 알려진 드리프트 사각으로
  6종 불일치로 해석하지 않고 수리하지 않는다.
- 나머지 offline 8건은 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24 및 stage_budget_state,
  N=R20/R21/R22. 삭제/PASS 전환 없음.
- **W2(lap296 §4.7.4):** `runtime_driver.py`는 아직 매직 리터럴을 읽는다. (a) line 84 `0x8990C8`·
  line 89 `0x66B790`/`0x758`은 승격 가능, (b) line 100 `0x8D`는 probe 가드 선행,
  (c) line 101 `0x8E`는 상수 부재·값 미재유도라 명명 **금지**.
- **lap296 수리 후:** lap280 line 129-130의 `type`/`owner` scrape가 명명 failure로 닫혔다.
  lap296 review의 target SHA mismatch(`88d86211…`→`8a5eee47…`)는 §4.7.6 4항의 stale
  EXPECTED_SHA이며, W2 변이는 crash 없이 exit1/비제로 report를 냈다. §4.6.2 판정은 유효하다.
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결. lap288/289: lap279/lap280/lap284-middle 세 probe는 아직 `0x440FF0` 창을 써서 legacy window 오분류
  위험이 남는다(수치 영향 0; lap289가 work probe만 `0x440F5B`로 좁혔다). **lap292 사각:** 이름 결합
  단언이 reader 이름을 안 봐 `x=i(G1_UNIT_X_OFFSET)`류 폭 드리프트는 통과한다(기록만, §4.5.4).
- **프로세스 사각:** 상수/앵커 승격 시 결합된 과거 probe를 재실행하지 않으면 잠복 결함이 재발한다
  (lap294·lap296 사례). **provenance:** lap287 편집 경고는 lap290 부록, lap293 `ESCALATE_SOL`은
  lap294 부록 A, lap297 `ESCALATE_SOL`(`760a977e…4a8aa84c`)은 lap298 부록 A에 보존.
- S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐이다. 두 run의 실제 값 동일성은
  미검증이며 Stage B/runtime pair는 상위 승인 전 금지.
- map-layer serializer **28쌍** 모델은 lap286이 재현해 ACCEPT(`1,400,702`+`30.5`). 한계: 네 fixture가
  전부 정사각·짝수 변이라 (a) 오프셋 210/212의 width/height 배정과 (b) halving layer `((w/2)*h)/2` 대
  `(w*h)//4`를 구분 불가(홀수 변 fixture는 게임 실행을 요구). owner `+0x8E` 상속 가정 미재유도,
  runtime layer 의미·save/load 동일성 미검증.
- **G3 저장 포맷:** bulk 블록 `0x892410..0x975D8C`에 PlayerStruct 8개(`0x956770..0x973D50`)는 들어
  가지만 16개는 `0x991330`까지 필요해 `0x1B5A4` 바이트 넘친다. 현재 포맷에 9~16번을 직렬화할 공간이
  구조적으로 없다. G1 범위에서 수리하지 않는다.
- **로드 경로 부재(lap284, lap298 재측정):** `tools/runtime_env.py`의 `save` 참조 **0**, PS35 참조
  **0**, PS 대기값 **{3,5,7,9}**. 수정 대상 함수·기록 위치 미확정 → "연구 하네스" 행 **REJECT**.
- **실행 봉투 미성립(lap284 §5 (a)~(e)):** lap298이 (a)의 1차 클릭만 줄였고 (b) 3 MB save 로드가
  90초 상한에 드는지, (c) 두 save 중 선택 절차, (d) PS5 미도달 run의 수집/flush/종료, (e) run별·총
  wall-clock 예산은 전부 미제출 → 봉투 행 **REJECT** 유지.
- **PS35→PS3 미도달 실패 모드(lap284 §6 조건):** evidence 스키마에 보존 형태가 없어 실행 전 필드
  선언이 필요하나 미선언 → "안전·회귀" 행 ACCEPT-WITH-CONDITION.
- **fixture 확정 근거 부재:** save000/save006 유지는 옳으나 선택 근거가 되기로 한 lap284 §7 카드
  4항(nation/활성 구성/절대 유닛 수)이 lap286~289에서 산출되지 않았다. 공통 사실은 "owner id ≥8
  record 0개"뿐이고 save000 선호는 근거 없는 잠정이다.
- **Plan C 함정(lap298 §10.3 봉인):** 공유 temp의 800×600 `…_d1app2r3_21_load_screen.png`
  (`5e95ed92…d17e5879`)는 원본 로드 대화상자가 **아니다**. 슬롯 문자열은
  `Syw2plus_re/plan_c/src/ui/save_load_screen.cpp`(`f2232e91…90ff41ec`)가 만든다 → 좌표 출처 금지.
  그 모듈이 인용하는 `0x519A0C`/`0xB3AD74`/`0x1088B5C`는 원본 raw 크기 밖이라(`0x4D60B0`은 안)
  섹션 virtual size/다른 모듈 확인이 선행돼야 한다.
- **lap284 tick 순환 의존은 해소됐다(lap297 결정1 + lap298 ACCEPT).** 연구 쌍 tick은 허용오차 없는
  report-only이고 철회 범위는 연구 쌍 입력 요구뿐이며 제품 S1의 (A)+(B)는 그대로다. **`(296,505)`의
  한계:** 위치·라벨만 확정이고 **클릭 결과는 관측된 바 없으며** 슬롯 선택 UI·로드 후 전이는 UNKNOWN.

## 검증 상태

**lap299 work (fresh static probe `5c4bbc1a…86037b77`, report `8e735a9a…76d2bb0b`, exit0):**
원본 `b56986e0…c9c08a8ac`의 `FUN_004D60B0`에서 `this+0x408`, count7, stride16,
`0x118×0x18`, top offsets와 mode `0x3EB/0x3ED`를 재유도했다. sprite header `[9,320,310,1]`을
800×600 중심식에 대입해 title `(240,145)`, 7 rect `[260,119..540,347]`, OK/Cancel
`(276,360)/(426,360)`을 산출했다. 세 geometry check PASS; 캡처/게임/클릭 전이 0.
`make check` **292 passed(49.18s)**, ruff/compileall/mypy/CONTEXT_PASS, `SAFETY_PASS`.
lap298의 `(296,505)`는 위치·라벨만 확정된 상태로 유지한다.

lap296 middle이 lap295 수리를 ACCEPT(자체 mutant 6종, 80 B 복원 SHA로 범위 증명).
lap286 middle이 save 레이아웃 모델을 독립 재현(ACCEPT-WITH-CORRECTION): 경계 `0x440C20..0x440F5A`,
직접 fwrite 22 / layer 28 / helper 3 / roster 1, `1,400,702`와 `30.5` 독립 유도, 네 fixture 모두
**owner id ≥8 record 0개**. 정정2로 `roster_records` 반증력은 **정수배 검사 4건**뿐이고 lap288은
경계·mutation ACCEPT / 카드 종결 REJECT였다. lap284 middle: lap283 fingerprint 9/9 일치, save
페이로드 50개, 첫 layer 앞 고정 22,978 B, map block 오프셋 70, 폭/높이 210/212.
lap279~299 수치는 `docs/history/laps/`에 있고 실제 게임 검증으로 승격하지 않는다. G1 제품 증거 0.
이전 STATUS 원문은 `…_status_lap276/284/288/290/294/296/298_compaction.md`에 보존했다.

## 바퀴 기록

lap2~276 상세와 압축 원문은 `docs/history/laps/`.
lap277~283: middle이 측정식을 반려·대체하고 여섯 행 CONFIRMED로 교체, work가 유닛 오프셋 상수 3개
승격, middle이 새 objdump로 독립 검수. G3 저장 블로커 발견 후 lap283 Astra가 runtime/G3 결정.
lap284~289: middle이 여섯 필수 입력을 판정해 runtime 예산 보류, 저장 레이아웃 카드를 work에 인계,
lap286이 독립 재현, work가 경계 수리·`0x440F5B` 축소했다. 과거 PS3 run의 scene.tick은 폴링 산물.
lap290~296: middle이 lap280 traceback을 상수 승격발 하네스 결합 결함으로 확정 → work 수리 → middle
검수 → work 승격 → middle이 무방비 소비처 확정 → work가 line 156·167 가드 → lap296이 **ACCEPT**하고
§4.4.3 종결. lap297: Astra가 세 결정을 내리고 승격. lap298: middle이 그 세 결정을 ACCEPT·ACCEPT·
ACCEPT-WITH-CORRECTION으로 판정하고, lap284 §7이 "지금 열지 않음"으로 남긴 타이틀 스크린샷 가설을
열어 **불러오기 좌표 `(296,505)`를 게임 실행 0으로 확정**했다. Plan C 로드 화면 캡처는 원본 증거에서
봉인했고, 봉투 (b)~(e)·연구 하네스 행은 REJECT로 유지해 runtime 예산 요청을 내지 않았다.
lap299: work가 원본 `FUN_004D60B0`과 sprite header로 800×600 정적 레이아웃을 재유도하고 geometry
probe·make check·safety를 PASS했다. 새 middle 독립 검수 전까지 제품 G1/S1/Stage B 판정은 그대로다.
