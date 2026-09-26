# STATUS 원문 보존 — lap288 압축 직전

- 원문 경로: docs/STATUS.md
- 원문 SHA256: a1a8c402bf0c125abcf38469cdd31d451f73ee88b93f2f0e46e18462d89fe73e
- 원문 줄 수: 143
- 보존 시각: 2026-09-12 KST (lap 288, middle tier)
- 사유: PROMPT의 130줄 상한 초과. 아래는 압축 전 전체 원문이며 승인·반려·미결 근거를 삭제하지 않았다.

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4 모두 제품 미완료. M1/G1 유지: 원본 800×600 구도와 입력을 유지한 1600×1200 출력.
제품 기준은 DESIGN, 사람 승인 원문은 feedback/APPROVALS와 INBOX를 따른다.
사용자의 2026-09-12 01:03 bounded repair→fresh validation 허가는 제품/출시 승인이 아니다.
DxWrapper 출력/30초 렌더 과거 근거는 있으나 실제 scene/input 쌍과 WM_CLOSE 결함이 남았다.

lap275 middle이 F3-R2-R1을 선언 범위 승인(offline 기계 증거, producer 6종·comparator 일치,
새 PASS 경로 0). lap270 R30 선언 범위 PASS와 R17 계약 종결 FAIL은 함께 유효하며 M11 생존을
지우지 않는다. 나머지 offline 8건은 lap271 H/C/N 분류로 주차됐고 Stage B 선행조건이 아니다.

G1-S1 계약 계보(상세는 `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md`, lap 단위 근거는
`docs/history/laps/`의 lap276~282 기록): Astra 방향 → 측정식 반려·대체 → work 정적 조사 →
여섯 행 전부 CONFIRMED로 교체 → 다른 추출 경로 교차검증 수용(정정 2건) → 상수 3개를
`tools/runtime_env.py`로 승격 → 새 objdump 독립 검수 ACCEPT-WITH-CORRECTION(정정 1건).
이 계보는 **S1 fixture의 정적 타당성**이며 두 run의 실제 값 동일성·제품 증거·Stage B
허가·마일스톤 종료가 아니다. comparator/producer/PASS 규칙은 전 구간 무변경이다.

lap283 Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정하고 실행 계약 누락으로
승격했다(`docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md`).
**lap284 middle이 그 여섯 필수 입력을 판정했다**
(`docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md`): 측정식 ACCEPT,
실패 보존 ACCEPT-WITH-CONDITION, fixture·하네스 연결·tick·실행 봉투 **REJECT**.
따라서 **runtime 예산 요청 없음, Stage B 0 유지**. 게임/Wine/Xvfb/실행은 0이다.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 미완료 | S1/F2-R2 결정성, fresh pair, 실제 입력, WM_CLOSE |
| G2 | 미완료 | 활성8인 전비5000·풀/메모리·저장/지원동기화 증거 |
| G3 | 미완료 | 활성9~16번 실제 플레이/직렬화/지원 통신 |
| G4 | 미완료 | 원본 대비 반복 경로/전략 지표와 개선 |

## 다음 한 가지

**다음 한 가지: work tier(Luna/Sonnet5)가 정정1을 원래 대상 파일에 적용한다.**
`docs/history/laps/probes/20260912_lap284_work_save_layout_probe.py:26`의 `SAVE_END`를
`0x440F5B`로 좁히고 `0x4DA4A9` 단언을 **그 파일에** 넣은 뒤, 나머지 세 probe의 `0x440FF0`/
`LOAD_ENTRY` 사용처를 재실행 대조해 출력 불변을 보인다. 실행 예산 0; 게임 실행·하네스 로드 경로
구현·PASS 규칙 변경 금지.
상위(Astra) 큐 3건은 `…MIDDLE_LAP284.md` §8에 있다: tick report-only 제안, 로드 경로가
PS5→PS3 endpoint 규칙을 우회하는 구조 문제, fixture 열거에서 save011/012가 빠진 건.

## 지금 막힌 것 (Blockers)

- S1/F2-R2 실제 결정성은 미해결. Stage B, 원본 재실행, Wine/Xvfb, R6-A/R6-C 금지.
- comparator는 scene 4축과 선택 slot만 본다. nation/전체 slot id/절대 selection·camera/tick은
  기계 검사 밖이며 (B) 원시 필드 대조로만 확인한다. overall PASS도 충분조건이 아니다.
- `scene.owners`는 owner0~7, offsets는 owner0/1만 본다. owner8~15는 장면 서명에 안 보인다(G3 위험).
- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- R17 구조 재결 미완료, R31 금지. R29 범위 승인 거부(lap266), R30 M11 생존 유지.
- lap274 추출기의 M-d(세 번째 함수), M-e(접두어 밖 분류) 생존은 알려진 미래 드리프트 사각.
  현재 6종 불일치로 해석하지 않으며 수리 계열은 열지 않는다.
- R6-B-R2의 count 1→0 응답 판정은 미결. 규칙 변경 금지.
- 나머지 offline 8건은 주차: H=F2-R1/F3-R1/F6-R2, C=R23/R24 및 stage_budget_state,
  N=R20/R21/R22. 삭제/PASS 전환 없음.
- `runtime_driver.py`는 `type=u[0x8D]`, `0x66B790`, `0x758`, `0x8990C8`을 여전히 매직
  리터럴로 읽는다. `runtime_env.py`에 동일 값 상수가 이미 있으므로 드리프트 사각이다(W2).
- 후보 WM_CLOSE teardown 결함, 실제 후보 scene/input evidence, G2~G4 증거 미해결.
- **lap288 신규:** `SAVE_END=0x440FF0`을 아직 들고 있는 probe 4개(lap279/lap280/lap284_middle_
  runtime/lap284_work). lap279/280은 `LOAD_ENTRY=0x440FF0`까지 두어 `0x440F60`·`0x440F96`의 두
  루틴을 save로 잘못 귀속한다. 틈에 fwrite 호출이 0건이라 **수치 영향은 없고** 오분류 위험만 남는다.
- **lap288 신규 provenance:** lap287(work)이 middle 소유 probe를 편집해 단일 작성자 규칙을 넘었고
  편집 전 SHA가 없어 `logs/lap286/…json`을 그 경로에서 재생성할 수 없다. 두 로그 차이는 필드 2개뿐.
- S1 여섯 행은 정적 CONFIRMED지만 **fixture 타당성**일 뿐이다. 두 run의 실제 값 동일성은
  미검증이며 Stage B/runtime pair는 상위 승인 전 금지.
- map-layer serializer **28쌍**의 save 쪽 static 모델은 lap286 middle이 다른 추출 경로로
  재현해 ACCEPT했다(상수항 `1,400,702` + 면적계수 `30.5`). 남은 한계: 네 fixture가 전부
  **정사각·짝수 변**이라 (a) 파일 오프셋 210/212의 width/height 배정과 (b) halving layer의 기계
  공식 `((w/2)*h)/2` 대 probe의 `(w*h)//4`를 구분할 수 없다. 홀수 변 지도에서 갈라진다.
  unit record owner 필드 `+0x8E`는 work에서 상속한 가정이며 아직 재유도되지 않았다.
  runtime layer 값의 의미·save/load 값 동일성은 여전히 미검증이다.
- **G3 저장 포맷:** save/load bulk 블록은 `0x892410..0x975D8C`다. PlayerStruct 8개
  (`0x956770..0x973D50`)는 들어가지만 16개는 `0x991330`까지 필요해 `0x1B5A4` 바이트 넘친다.
  현재 포맷에 9~16번 플레이어를 직렬화할 공간이 구조적으로 없다. G1 범위에서 수리하지 않는다.
- **lap284 신규:** 하네스에 저장 로드 경로가 0줄이고(`tools/runtime_env.py`의 save 참조 0,
  PS35 참조 0, 대기 PS는 3/5/7/9뿐) 타이틀의 불러오기 좌표가 저장소 어디에도 없다.
  좌표 확보는 게임 실행 또는 과거 스크린샷 분석을 요구하므로 offline 카드와 분리한다.
- **lap284 신규:** tick 순환 의존 — 계약은 tick 오차 근거 없이는 runtime 예산을 막는데
  로드 경로의 tick 근거는 로드 경로를 한 번 실행해야 나온다. 상위 결재 전 해소 불가.

## 검증 상태

lap284 middle: lap283 fingerprint **9/9 일치**, probe 출력 바이트 동일, exit0 failures=[]
(`logs/lap284/runtime_contract_probe.json`): save 페이로드 순서 50개, 첫 layer 앞 고정 22,978 B,
map block 파일 오프셋 70, 폭/높이 오프셋 210/212. 과거 PS3 run 8건의 scene.tick은 폴링 산물이다.
lap284 work probe도 exit0 failures=[] (`logs/lap284/work_save_layout_probe.json`).
두 lap 모두 `make check` 292 passed, CONTEXT_PASS/SAFETY_PASS, 게임 실행 0.
lap286 middle(독립 검수): 자체 probe `…lap286_middle_save_layout_review_probe.py` exit0
failures=[] (`logs/lap286/middle_save_layout_review.json`), 재실행 **바이트 동일**. lap284 work
probe 재실행도 기록 출력과 바이트 동일. save 함수 실측 경계 `0x440C20`..`0x440F5A`, 직접
fwrite 22 / layer 28(중복 0) / helper 3 / roster 1. 하드코딩 목록·문자열 휴리스틱 없이 유도한
literal `1,249,942` + helper `118,360` + 고정 layer `32,400` = 상수항 `1,400,702`, 면적계수
`30.5`가 work 컴포넌트 합과 일치. 두 면적 차분으로도 30.5 독립 확인. prefix `2,388,902`
(180×180) / `1,705,702`(100×100), roster 해 **375/558/147/149** 일치. 호출 순서 재생 오프셋도
일치(bulk `1,455,954`/`772,754`, player0 `2,259,634`/`1,576,434`). owner 히스토그램을
save011/012까지 확장(`0:144,1:3` / `0:145,1:4`)했고 **네 fixture 모두 owner id ≥8 record 0개**.
무시된 callee 5종(`0x440A80`/`0x440AC0`/`0x4AC3E0`/fopen/fclose) **fwrite 전이 도달 0**.
**정정2:** `roster_records`는 나머지에서 구한 값이라 "정확히 재구성"은 항상 성립한다. 실제
반증력은 **정수배 검사 4건**뿐이며 검사 2종이 아니다. `make check` **292 passed(44.86s)**,
Ruff/compileall/mypy 10 files, CONTEXT_PASS, `SAFETY_PASS`. 원본 EXE SHA 전후 동일.
게임/Wine/Xvfb/Stage B/PNG 0. 상세: `docs/history/laps/20260912_lap286_middle_save_layout_review.md`.
lap287 work가 exclusive `SAVE_END=0x440F5B`/마지막 `ret=0x440F5A`를 고정하고 `0x4DA4A9` 비포함
회귀 단언을 추가했다. **lap288 middle 독립 검수: ACCEPT(수리 내용) / REJECT(카드 종결).**
lap287 probe 재실행은 `logs/lap287/…json` SHA `f0568622…08bc5`와 **바이트 동일**. 자체 probe
`…lap288_middle_boundary_review_probe.py` exit0 failures=[] (`logs/lap288/middle_boundary_review.json`
SHA `86157fad…471c9`), 재실행 바이트 동일. 경계 재유도 CONFIRMED: 창 안 `ret`은 `0x440C62`/
`0x440F5A`뿐, 밖으로 나가는 분기 0, padding이 `0x440F5B`에서 시작, 다음 함수 `0x440F60`.
mutation matrix: M0 exit0/failures0, M1(SAVE_END만 되돌림) exit1 경계단언 kill, M2(되돌림+평면 창)
exit1 failures39이며 `0x4da4a9 … ['0x00440fa4']`가 실제 발화. 단 M1에서 fread 단언은 도달 불가라
**가드가 가장 필요 없는 파일에 붙었고 정정1이 지목한 work probe는 미수리**다. 정정2 문구는 반영됐고
M2에서 네 fixture 전부 `not a multiple of 1880`이 발화해 정수배 검사의 반증력도 실측했다.
`make check` 292 passed(45.95s), Ruff/compileall/mypy 10 files, CONTEXT_PASS, `SAFETY_PASS`.
원본 EXE SHA·fixture 4종 SHA 전후 동일. 게임/Wine/Xvfb/Stage B/PNG 0.
상세: `docs/history/laps/20260912_lap288_middle_boundary_repair_review.md`.
lap283 Astra: lap282 probe/출력 SHA 일치, 재실행 출력 동일·failures=[]. G3 초과 0x1B5A4 재확인.
lap279~282 수치(291~292 passed, 각 probe failures=[], 기록 SHA 전수 일치)는
`docs/history/laps/`에 있다. 그 수치를 실제 게임 검증으로 승격하지 않는다. G1 신규 제품 증거 0.
이전 STATUS 원문은 `docs/history/laps/20260912_status_lap276_compaction.md`와
`…_status_lap284_compaction.md`에 SHA/줄 수와 함께 보존했다. 반려/승격 원문은 삭제하지 않는다.

## 바퀴 기록

lap2~276 상세와 압축 원문은 `docs/history/laps/`.
lap277: middle이 측정식 반려·대체 확정, work 조건부 승인. 게임 코드 변경 0.
lap278: work가 원본 저장/불러오기 정적 조사와 여섯 행 판정을 기록했다. 게임 코드 변경 0.
lap279: middle이 다섯 행 UNKNOWN을 반려하고 여섯 행 전부 CONFIRMED로 교체. G3 저장 포맷
블로커 발견. lap280: middle이 다른 추출 경로로 교차검증해 수용, 정정 2건.
lap281: work가 유닛 오프셋 상수 3개를 승격하고 정적 근거를 memory map에 기록했다.
lap282: middle이 새 objdump로 독립 검수해 수용, 폭 배타성·부호 근거 보강, 정정 1건.
lap283: Astra가 runtime 연구/Stage B 분리와 G3 저장 경계를 결정. 실행 계약 누락으로 승격.
lap284: middle이 그 여섯 필수 입력을 ACCEPT 1 / ACCEPT-WITH-CONDITION 1 / REJECT 4로 판정하고
runtime 예산 요청을 보류했다. 저장 파일 레이아웃 모델 offline 카드 한 장을 work에 인계.
lap284 work: serializer/helper static model이 네 fixture 크기와 정확히 일치. 게임 코드 변경 0.
(middle 기록: `docs/history/laps/20260912_lap284_middle_runtime_contract.md`)
lap286: middle이 그 모델을 독립 추출 경로로 재현해 **ACCEPT-WITH-CORRECTION**(정정 2건, 범위
한계 4건). 게임 코드 변경 0, 실행 0. 러너 로그는 lap-0286이나 직전 세션이 자신을 lap284로
기록해 기록 번호가 하나 뒤진다. `loop/.lap_counter`는 읽기만 했다.
lap287: work가 boundary repair probe와 회귀 단언을 추가해 PASS. 게임 코드·원본·fixture 변경 0.
lap288: middle이 그 수리를 독립 검수해 경계·반증력은 ACCEPT, 정정1 대상 파일 미수리로 카드 종결은
REJECT. 게임 코드 변경 0, 실행 0. work tier로 되돌린다.
