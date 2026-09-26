# STATUS 압축 전 원문 보존 — lap266

- 원문: `docs/STATUS.md` (lap266 갱신 직전)
- SHA256: `99cf172ae6c063000137e26ae08cfac18e9e3c4743c4c37b90c52f27bf4597d7`
- 줄 수: 128
- 보존 사유: lap266 middle 검수 결과 추가로 130줄 상한 초과 예상.

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. G1은 원본 800×600 논리 구도/UI를 유지한 1600×1200
정수 2배 출력, G2는 8인 전비 5000과 실제 개체 풀/메모리 확장, G3은 최대 16인, G4는
길찾기·자유대전 AI 개선이다.

DxWrapper 후보는 fresh runtime에서 1600×1200 client/capture, 800×600 logical, 2×2 scale,
선변환 없는 입력, PS9→PS7→PS3와 30초 지속 렌더를 확인했다. WM_CLOSE teardown 결함은
builtin ddraw 대조로 DxWrapper native 경로에 귀속했고 P6 Lock 계측은 주차했다.

사용자는 2026-09-12 01:03 KST “승인. 루프 계속 돌아”로 Stage B evidence가 성립할 때까지
bounded repair→fresh validation을 승인했다. blind retry, run 재사용, 보호 자산 변경은 금지다.

Stage A A-1~A-16과 R1~R5-C/N1~N3, comparator F1/F4/F5, 후보 producer F6은 구현 후
Opus 독립 승인을 받았다. lap204 fresh 원본 drag는 count 1→1이지만 slot/type
1199/70→1198/21로 실제 선택 효과가 있었다. 이에 `FAIL_NO_EFFECT`, 절대 slot id, `count>=2`
규칙을 기각했다. lap214 Astra/medium 이후 Opus가 판정 계약을 재결했고, F3는 `after.last`, F2는
`(owner,type,장면 상대 world offset)` parity를 사용하도록 수리·독립 승인했다.

R6-B는 선택 count 또는 identity의 비퇴행 변화를 응답으로 삼는다. 후속 수리 R1~R14는 각각
work 구현 뒤 다음 새 middle 세션이 독립 검수해 **범위 승인**했다(R1 lap226, R3 lap228,
R4 lap230, R6 lap232, R5 lap234, R7 lap236, R8 lap238, R9 lap240, R10 lap242 FAIL→lap243
수리→lap244 승인, R11 lap246, R12 lap248, R13 lap250, R14 lap252). 각 lap의 하네스·행렬·
변이 근거와 lap245 무효 증거 판정은 `docs/history/laps/`와 압축 원문
`docs/history/laps/20260912_status_lap254_compaction.md`에 보존돼 있다. 이 승인들은 모두
기계(1단) 승인이며 제품 G1 증거가 아니다.

직접 selection reader 실패 계열도 같은 방식으로 닫혔다. **R15**(reader 실패가 budget 소진보다
우선하는 `UNKNOWN_STATE_READ_FAILURE`와 timing provenance)는 lap253 work → lap254 검수 FAIL
→ lap255 work R25(4-case 의미 회귀) → **lap256 범위 승인**. **R26**(`stage_budget_state`
4-상태)은 lap257 work → lap258 검수 **FAIL(커버리지)**: production 호출
(`tools/runtime_env.py:2636`)이 `stage_started`를 넘기지 않고 production에 budget이 없어
`(None, None)`이 유일한 도달 shape인데 회귀가 없는 `stage_started=0.0`을 고정했다.

- **R27**: lap258 work가 그 production shape를 `_g1_run_input_sequence` fixture로 구동해
  `stage_budget=None`/`stage_started_elapsed=None`/`STAGE_BUDGET_UNAVAILABLE`을 고정하고
  우선순위 계약을 주석으로 남겼다(SUT 로직 무변경). **lap260 middle 독립 검수 PASS →
  R26/R27 범위 승인(기계 1단)**: 160-case 독립 행렬 불일치 0, M0 144=144, 변이 11종 생존 0·
  범위 밖 0, lap258 생존자 M5가 R27 회귀 단독으로 사살됐고, R27만 제거하면 M5/M6/M10/M11이
  되살아나 하중이 R27에 귀속됨을 확인했다. R26/R25/R15 커버리지는 약화되지 않았다.

최상위 증거 차단 S1은 원본↔원본도 nation/player spawn이 달라 scene mismatch가 나는
비결정성이다. F2-R2 때문에 장면 통제는 slot 대응 결정성도 함께 풀어야 한다. 상위 재결 전에는
fresh Stage B를 실행하지 않고 게임 없는 수리만 한 바퀴 한 건씩 진행한다.
모델 라우팅: Luna/high(work), Claude Opus5/high(middle), Astra/medium(strategy). Astra는 큰
분기·교착에서만 약 10 lap당 1회 이하이며 마지막 호출은 runtime lap214였다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 표시·논리 좌표 증거 있음; R20~R24, R2/S1, fresh pair, WM_CLOSE 필요 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

**R29 독립 검수(middle tier)**: lap265 work가 본문 집합을 `NEGATIVE_PATTERNS` 첫 review
계산부터 `json.dump`까지 독립 고정했다. fresh throwaway 변이에서 M0 8 passed, M1 개명-only 생존,
M2/M3/M6/M7 각 1 failed·7 passed, C4 귀속을 확인했다. 다음 큐는 검수 뒤 R20 → R21 → R22 →
R23 → R24 → F2-R1 → F3-R1 → F3-R2 → F6-R2.
Stage B·게임/Wine/Xvfb는 S1/F2-R2 상위 재결 전까지 금지한다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1/F2-R2:** random seed·scene·slot 대응 결정성이 없다. 상위 재결 전 Stage B 양쪽 run,
  원본 재실행, R6-A/R6-C 금지.
- **R6-B-R2:** count 1→0 선택 상실을 응답으로 볼지는 Astra/사용자 재결 전 수정 금지.
- **R29 범위 승인 대기:** machine stage-1 결과이며 제품 G1 증거가 아니다. 승인 뒤 offline 큐: **R20**(저장소 밖 미러 변이 하네스에 M0 대조군이 없어 재배치 실패를 "검출"로 오독 — lap246),
  **R21**(probe 출력이 직렬화 전에 `open("x")`로 파일을 만들어 쓰기 실패가 절단 증거를 남기고
  R7이 재시도를 막는다 — lap248), **R22**(R13의 세 성질이 단일 테스트 하나에만 걸려 있다 —
  lap250), **R23**(`read_coverage` 소비자가 runtime_env 밖에 0개 — lap250),
  **R24**(R14 `read_failure` 소비자도 0개이고 record 최상위 `selection_count`는 실패/미관측
  모두 null — lap252), F2-R1/F3-R1/F3-R2/F6-R2.
  `stage_budget_state`도 runtime_env 밖 소비자가 0개이며 R23/R24와 같은 계열로 취급한다.
- 후보 WM_CLOSE teardown 결함과 실제 후보 scene/input evidence는 미해결이다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- lap146~252: Stage A/R1~R14와 F2/F3 수리·독립 승인, 각 lap의 행렬·M0 대조군·변이 근거는
  `docs/history/laps/`와 lap254 압축 원문에 있다.
- lap253~256(R15/R25): work → lap254 검수 FAIL(M4 생존) → lap255 R25 보강 → lap256 검수 **PASS,
  R15 범위 승인**(C0 16 passed/128 deselected, C1 105-case 불일치 0, C2 144, C3 9종 생존 0).
  상세 `..._lap254_middle_r15_review.md`, `..._lap255_work_r25.md`, `..._lap256_middle_r25_review.md`.
- lap257~258(R26): lap257 work가 `stage_budget_state` 4-상태를 추가했고 lap258 middle이
  **FAIL(커버리지)** 판정했다. C1 160-case 불일치 0, C2 144=144, C3 변이 8종 중 M5만 생존.
  상세는 `..._lap257_work_r26.md`, `..._lap258_middle_r26_review.md`.
- lap258 work R27: production shape 회귀와 `UNAVAILABLE` 우선 계약 주석 추가. targeted 6 passed,
  `make check` 279 passed, `CONTEXT_PASS`, `SAFETY_PASS`. 상세 `..._lap258_work_r27.md`.
- **lap260 middle R27 독립 검수 PASS(기계 1단)**: C0 14 passed/130 deselected, C1 160-case 불일치 0·
  production 실측 shape `(None, None) → STAGE_BUDGET_UNAVAILABLE`, C2 144=144, C3 11종 생존 0·
  범위 밖 0, C4 R27 제거 시 M5/M6/M10/M11 부활. 상세 `..._lap260_middle_r27_review.md` + probe.
- lap261 work R19: helper 이름 대신 AST 파생 review-body 줄 실행을 추적하도록 R17을 옮겼다.
  targeted 8 passed, R10 reverify PASS, `make check` 279 passed. 상세 `..._lap261_work_r19.md`.
- **lap262 middle R19 독립 검수 FAIL(커버리지, 기계 1단)**: C0 8 passed; C1 preflight end 130·
  본문 137~426(262줄)·성공 205줄·거부 0줄; C2 미러 8=8; C3 M1 생존(오탐 0), M2/M3 R17 단독
  사살, **M6**(전처리 If를 본문 아래로)는 196/262줄 실행 후 거부인데 helper 0줄로 8 passed 생존.
  상세 `..._lap262_middle_r19_review.md`, probe `..._probes/20260912_lap262_r19_review_probe.py`.
- lap263 work R28: 비공허 AST 집합과 `json.dump` anchor 단언 추가. targeted/M0 8 passed,
  M2/M3/M6 각 1 failed. 상세 `docs/history/laps/20260912_lap263_work_r28.md`.
- **lap264 middle R28 독립 검수 FAIL(커버리지, 기계 1단)**: C0 8 passed; C1 계약 독립 재유도
  (전처리 If 1개·123~130, 본문 137~426 262줄, `json.dump` 412줄 포함; 양성 205줄/음성 0줄);
  C2 미러 M0 8 = 실저장소 8; C3 변이 6종에서 M1 의도 생존(오탐 0), M2/M3 R17 단독 사살,
  **M6은 R28이 사살**(C4로 귀속 확인)이지만 신규 **M7**(전처리 `__name__` 블록 전체를 report
  write `try:` 바로 위로 이동)이 **8 passed 생존**한다. M7 거부 run 직접 트레이스: rc 2·증거
  보존이지만 baseline 본문 **198/262줄이 거부 전에 실행**되고 helper는 비공허 17줄 + anchor
  포함을 돌려줘 R28 두 단언이 모두 통과한다. C4: R28만 제거 시 M6/M7 부활, R17만 제거 시
  M2/M3/M6/M7 부활 → R7/R10/R11 및 R15/R25/R26/R27 약화 없음. `make check` 279 passed,
  Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`; 게임/Wine/Xvfb/PNG 0회.
  SUT/테스트 지문은 검수 전후 동일하고 lap263 기록값과 일치한다. 상세
  `docs/history/laps/20260912_lap264_middle_r28_review.md`, probe/report
  `..._probes/20260912_lap264_r28_review_probe.py`, `..._lap264_r28_review_report.json`.
- **lap265 work R29:** 테스트 helper가 `NEGATIVE_PATTERNS`~`json.dump`를 고정하도록 수리했다. targeted
  8 passed; fresh M0/M1/M2/M3/M6/M7 결과와 C4 귀속은 `docs/history/laps/20260912_lap265_work_r29.md`에 기록했다.
  `make check` 279 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`; 게임/Wine/Xvfb/PNG 0회.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap237_compaction.md`,
  `docs/history/laps/20260912_status_lap254_compaction.md`,
  `docs/history/laps/20260912_status_lap260_compaction.md`.

## 바퀴 기록

- lap2~258과 STATUS 원문: `docs/history/laps/`; probe는 `docs/history/laps/probes/`.
- current escalation: `loop/ESCALATE_SOL`(lap265 work: R29 → middle 독립 검수); handoff:
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md` (R27 승인, R19/R28 반려, R29 검수 대기→R20).
