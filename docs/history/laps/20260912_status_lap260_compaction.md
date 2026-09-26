# STATUS 원문 보존 — lap260 압축 직전

- 원문 경로: `docs/STATUS.md` (lap258 work 기록 시점 상태)
- 원문 SHA256: `1fc18fd7ffaa3d0ecbede08529db2eefab1604476b1269415943bccbf7c6f676`
- 원문 줄 수: 130
- 보존 이유: lap260 middle이 R27 승인 결과를 추가하면 130줄 상한을 넘으므로 loop/PROMPT.md에 따라 먼저 전체 원문을 보존한다.

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

- R15: 직접 selection reader 실패가 run/stage budget 소진보다 우선하는
  `UNKNOWN_STATE_READ_FAILURE`와 `finished_elapsed`/`remaining_budget_after`/
  `stage_budget_exhausted`/`run_budget_exhausted` provenance — lap253 work 구현, lap254 middle
  독립 검수는 M4(`stage_budget_exhausted` 상수 True) 생존으로 **범위 승인 FAIL**이었다.
  lap255 work가 테스트만으로 4-case semantic 회귀(R25)를 추가했고, lap256 middle이 독립
  재측정해 **R15 범위를 승인**했다: 변이 9종 생존 0, 범위 밖 사살 0, 105-case 독립 행렬
  불일치 0. SUT 로직은 lap253 이후 무변경이다.

- R26: lap257 work가 직접 reader failure observation에 `stage_budget_state`(`WITHIN_STAGE_BUDGET`/
  `STAGE_BUDGET_EXHAUSTED`/`STAGE_START_UNKNOWN`/`STAGE_BUDGET_UNAVAILABLE`)를 추가했다.
  lap258 middle 독립 검수는 **범위 승인 FAIL(커버리지)** — C3 변이 8종 중 M5(우선순위 역전) 생존.
  production 호출(`tools/runtime_env.py:2636`)은 `stage_started`를 넘기지 않아 `(budget None,
  start None)`이 유일한 실제 도달 조합인데 R26 회귀는 없는 `stage_started=0.0`을 고정한다.
- R27: production과 동일한 `(budget=None, stage_started=None)` 직접 reader 회귀를 추가해
  `STAGE_BUDGET_UNAVAILABLE` 우선 계약을 고정했다. SUT 로직은 변경하지 않았고 middle 검수 전이다.
최상위 증거 차단 S1은 원본↔원본도 nation/player spawn이 달라 scene mismatch가 나는
비결정성이다. F2-R2 때문에 장면 통제는 slot 대응 결정성도 함께 풀어야 한다. 상위 재결 전에는
fresh Stage B를 실행하지 않고 게임 없는 수리만 한 바퀴 한 건씩 진행한다.
모델 라우팅: Luna/high(work), Claude Opus5/high(middle), Astra/medium(strategy). Astra는 큰
분기·교착에서만 약 10 lap당 1회 이하이며 마지막 호출은 runtime lap214였다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 표시·논리 좌표 증거 있음; R26, R2/S1, fresh pair, WM_CLOSE 필요 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

**R27 독립 검수**: 새 middle tier가 production shape 회귀와 우선순위 계약을 검수한다. 승인 뒤 큐는
R19 → R20 → R21 → R22 → R23 → R24 → F2-R1 → F3-R1 → F3-R2 → F6-R2다.
Stage B·게임/Wine/Xvfb는 S1/F2-R2 상위 재결 전까지 금지한다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1/F2-R2:** random seed·scene·slot 대응 결정성이 없다. 상위 재결 전 Stage B 양쪽 run,
  원본 재실행, R6-A/R6-C 금지.
- **R6-B-R2:** count 1→0 선택 상실을 응답으로 볼지는 Astra/사용자 재결 전 수정 금지.
- offline 큐: **R19**(R17 회귀가 함수명 `drive_wait` 하나에만 걸려 있어 개명 시 조기-거부
  삭제를 놓친다 — lap244), **R20**(저장소 밖 미러 변이 하네스에 M0 대조군이 없어 재배치 실패를
  "검출"로 오독 — lap246), **R21**(probe 출력이 직렬화 전에 `open("x")`로 파일을 만들어 쓰기
  실패가 절단 증거를 남기고 R7이 재시도를 막는다 — lap248), **R22**(R13의 세 성질이 단일 테스트
  하나에만 걸려 있다 — lap250), **R23**(`read_coverage` 소비자가 runtime_env 밖에 0개 — lap250),
  **R24**(R14 `read_failure` 소비자도 0개이고 record 최상위 `selection_count`는 실패/미관측 모두
  null — lap252), F2-R1/F3-R1/F3-R2/F6-R2.
- 후보 WM_CLOSE teardown 결함과 실제 후보 scene/input evidence는 미해결이다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- lap146~252: Stage A/R1~R14와 F2/F3 수리·독립 승인, 각 lap의 행렬·M0 대조군·변이 근거는
  `docs/history/laps/`와 lap254 압축 원문에 있다. 마지막 Fast는 lap252에서 274 passed/safety PASS.
- lap253: R15 work — 직접 reader 실패의 `UNKNOWN_STATE_READ_FAILURE` 우선순위와
  `finished_elapsed`/`remaining_budget_after`/budget exhaustion provenance를 추가했다. 새 deadline
  회귀 포함 targeted 11 passed, `make check` 275 passed, Ruff/compileall/mypy 10 files,
  `CONTEXT_PASS`, safety PASS; 게임/Wine/Xvfb/PNG 0회.
- lap254: R15 독립 검수 **FAIL(커버리지)**. C0 12 passed/128 deselected, C1 독립 행렬 74-case
  불일치 0(실패 72건 전부 `UNKNOWN_STATE_READ_FAILURE`), C1b 같은 소진 조건의 `_wait_state`는
  실제로 `UNKNOWN_BUDGET_EXHAUSTED`라 비대칭이 실재함, C2 미러 M0 140 = 실제 140,
  C3 변이 5종 중 **M4 생존**(M1/M2/M3/M5는 각 1건 사살·범위 밖 0건). `make check` 275 passed,
  `CONTEXT_PASS`, safety PASS, 게임/Wine/Xvfb/PNG 0회. SUT 지문은 검수 전후 동일하다.
- lap255: R25 work **PASS** — `tests/test_runtime_env.py`에 4-case semantic regression 추가.
  targeted 5 passed, 새 임시 mirror M0 144 passed, M4 상수 True는 3건 사살·M6 상수 False는
  2건 사살·인접 범위 밖 0건,
  `make check` 279 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, safety PASS;
  게임/Wine/Xvfb/PNG 0회. `tools/runtime_env.py`와 원본 pin 불변, R15 독립 범위 승인은 대기.
- lap256: R25 독립 검수 **PASS → R15 범위 승인(기계 1단)**. C0 16 passed/128 deselected,
  C1 독립 행렬 105-case 불일치 0(stage 5종 × `stage_started` {None,100.0,104.25} × offset
  {0,5,9.999,10.0,10.001,25,40}), C2 미러 M0 144 passed, C3 변이 9종 **생존 0/범위 밖 0**:
  M4 상수 True 3건(inside·미상·production), M6 상수 False 2건·M7 `>=`→`>` 2건(경계),
  M8 미상 start→run start 1건, M9 budget None→0 1건, M1/M2/M3/M5는 R15 테스트 사살 유지.
  네 case가 각각 개별 하중을 받는다. `make check` 279 passed, Ruff/compileall/mypy 10 files,
  `CONTEXT_PASS`, safety PASS; 게임/Wine/Xvfb/PNG 0회. SUT·테스트 지문은 검수 전후 동일.
- lap257: R26 work 구현 — 직접 reader provenance에 `stage_budget_state`를 추가하고 4-case 의미
  회귀를 보강했다. targeted 5 passed, 임시 미러 M0 5 passed, 상수 상태 고정 3 failed 및
  unavailable/start-unknown 축약 3 failed, `make check` 279 passed, Ruff/compileall/mypy
  10 files, `CONTEXT_PASS`, safety PASS; 게임/Wine/Xvfb/PNG 0회. middle 독립 검수 전이다.
- lap258: R26 독립 검수 **FAIL(커버리지)**. C0 14 passed/130 deselected, C1 독립 행렬 160-case
  (stage 5종 × `stage_started` {None,0.0,4.25,100.0} × offset 8종) 불일치 0·네 상태 모두 관측,
  C2 미러 M0 144 = 실저장소 144, C3 변이 8종 중 **M5 우선순위 역전 생존**(나머지 7종 사살,
  범위 밖 0건). M5는 production 호출 출력을 `STAGE_BUDGET_UNAVAILABLE`→`STAGE_START_UNKNOWN`으로
  바꾸지만 144 테스트가 전부 통과한다. `make check` 279 passed, Ruff/compileall/mypy 10 files,
  `CONTEXT_PASS`, safety PASS; 게임/Wine/Xvfb/PNG 0회. SUT·테스트 지문은 lap257 기록값과 동일.
- lap258 work R27: production shape 회귀와 `UNAVAILABLE` 우선 계약 주석을 추가했다. targeted 6 passed,
  `make check` 279 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`; 게임/Wine/Xvfb/PNG
  0회. SUT 로직·원본 pin·보호 자산은 불변이며 middle 독립 검수 전이다.
- latest work: `docs/history/laps/20260912_lap258_work_r27.md`; latest middle:
  `docs/history/laps/20260912_lap258_middle_r26_review.md`; probe/report
  `...probes/20260912_lap258_r26_review_probe.py`, `..._report.json`.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap237_compaction.md`,
  `docs/history/laps/20260912_status_lap254_compaction.md`.

## 바퀴 기록

- lap2~256과 STATUS 원문: `docs/history/laps/`; probe는 `docs/history/laps/probes/`.
- current escalation: `loop/ESCALATE_SOL`(lap258 work → middle R27 독립 검수; 남은 상위
  escalation은 S1/F2-R2뿐); handoff:
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md` (lap258 R27 완료, 다음 middle 검수).
