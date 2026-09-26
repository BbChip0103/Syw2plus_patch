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
work 구현 뒤 다음 새 middle 세션이 독립 검수해 **범위 승인**했다(R1 lap226 … R14 lap252).
직접 selection reader 실패 계열 R15/R25(lap256 승인), R26/R27(lap260 승인)도 같은 방식으로
닫혔다. 각 lap의 하네스·행렬·변이 근거와 lap245 무효 증거 판정은 `docs/history/laps/`와 압축
원문(lap237/lap254/lap260/lap266 compaction)에 보존돼 있다. 이 승인들은 모두 기계(1단)
승인이며 제품 G1 증거가 아니다.

**진행 중인 계열 — R17 커버리지 계약.** `tests/test_review_probe_output.py::test_r6b_r17_…`은
lap228 SUT probe의 "출력 preflight 거부가 review 본문보다 먼저"를 고정한다. R19(lap261) →
lap262 검수 FAIL(M6 생존), R28(lap263) → lap264 검수 FAIL(M7 생존), R29(lap265) → **lap266
검수 FAIL(M8 생존)**. 공통 원인은 본문을 **이동 가능한 두 앵커 사이의 줄 구간**으로 유도하고
시작 앵커를 `next()`로 **첫 일치**만 잡는 것이다.

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

**R30 구현(work tier)**: `_review_body_lines()`를 구간 유도에서 **named review result 대입의
합집합**(+ 모든 `json.dump` 줄, 이름 완전성 단언)으로 교체한다. 합집합은 단조라 전처리 이동으로
줄지 않고 decoy 대입은 줄을 더할 뿐이라 M6/M7/M8 이동·decoy 계열을 한 번에 닫는다. lap266이
throwaway 미러에서 이 계약을 미리 측정했다(변이 B: M0 8 passed, 생존자 `[M1]`, M2/M3/M6/M7/M8
전부 사살). 구조적 "전처리 아래 전부" 계약(변이 A)은 M0가 1 failed라 **기각**됐다.
출하 조건: M0 8 passed, M1 생존, M2/M3/M6/M7/M8 사살, R17 단독 하중 유지, `make check` 279 passed.
이후 큐는 R20 → R21 → R22 → R23 → R24 → F2-R1 → F3-R1 → F3-R2 → F6-R2.
Stage B·게임/Wine/Xvfb는 S1/F2-R2 상위 재결 전까지 금지한다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1/F2-R2:** random seed·scene·slot 대응 결정성이 없다. 상위 재결 전 Stage B 양쪽 run,
  원본 재실행, R6-A/R6-C 금지.
- **R6-B-R2:** count 1→0 선택 상실을 응답으로 볼지는 Astra/사용자 재결 전 수정 금지.
- **R29 범위 승인 거부(lap266).** R29는 M7을 닫았고 되돌릴 필요는 없지만 M8이 생존해 R17
  커버리지 계약이 아직 건전하지 않다. R30으로 닫은 뒤 다음 middle이 재검수한다.
- **상위 재결 대기(Astra/사용자):** lap262·264·266 3연속으로 lap228 역사 probe의 *테스트의
  테스트* 강화에 바퀴를 쓰는 동안 G1~G4 제품 증거는 0이다. Stage B가 S1/F2-R2로 막힌 채
  R20~R24/F2-R1/F3-R1/F3-R2/F6-R2 offline 큐를 계속 소진할지, S1 결정성 재결을 먼저 올릴지
  판단이 필요하다.
- offline 큐 대기: **R20**(저장소 밖 미러 변이 하네스에 M0 대조군 없음 — lap246),
  **R21**(probe 출력이 직렬화 전에 `open("x")`로 절단 증거를 남기고 R7이 재시도를 막음 — lap248),
  **R22**(R13의 세 성질이 단일 테스트 하나에만 걸림 — lap250), **R23**(`read_coverage` 소비자가
  runtime_env 밖 0개 — lap250), **R24**(R14 `read_failure` 소비자 0개, record 최상위
  `selection_count`는 실패/미관측 모두 null — lap252), F2-R1/F3-R1/F3-R2/F6-R2.
  `stage_budget_state`도 runtime_env 밖 소비자가 0개이며 R23/R24와 같은 계열로 취급한다.
- 후보 WM_CLOSE teardown 결함과 실제 후보 scene/input evidence는 미해결이다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- lap146~252: Stage A/R1~R14와 F2/F3 수리·독립 승인, lap253~260: R15/R25/R26/R27 수리와 승인.
  각 lap의 행렬·M0 대조군·변이 근거는 `docs/history/laps/`와 lap254/lap260 압축 원문에 있다.
- lap261~262(R19): work → middle **FAIL(커버리지)**, M6(전처리 If를 본문 아래로) 생존.
- lap263~264(R28): work가 비공허 AST 집합과 `json.dump` anchor 단언 추가 → middle
  **FAIL(커버리지)**, 신규 M7(전처리 블록을 report write 바로 위로) 생존.
- lap265 work R29: `_review_body_lines()`를 `NEGATIVE_PATTERNS`~`json.dump` 구간으로 재고정.
  targeted 8 passed, `make check` 279 passed. 상세 `..._lap265_work_r29.md`.
- **lap266 middle R29 독립 검수 FAIL(커버리지, 기계 1단)**: C0 8 passed; C1 계약 독립 재유도
  (preflight 123~130, anchor 137, `json.dump` 412, helper body `[137,412]` 276줄; 정상 run 201줄
  실행, 거부 run **0줄** → baseline에서 비공허); C2 미러 M0 8 = 실저장소 8; C3 변이 7종에서
  M1 의도 생존(오탐 0), M2/M3/M6/**M7 사살**(R29의 lap264 결함 수리 확인), 신규 **M8**
  (M7 + `NEGATIVE_PATTERNS` 개명 + report write 직전 decoy 별칭) **8 passed 생존** — helper body가
  5줄로 줄고 그중 0줄 실행이라 단언이 다시 공허한데, module-level review 문 171/231줄이 거부
  전에 실행된다(baseline 거부는 15줄). C4: R29 **앵커만** R28 방식으로 되돌리면 M7 부활 →
  사살은 앵커 변경에 귀속; `assert review_start < report_write_line`만 제거해도 M2/M3/M6/M7은
  계속 사살 → **그 단언 자체는 하중 0**(lap265 기록의 C4 귀속 주장은 불완전); R17 제거 시 5종
  모두 생존 → 사살자는 R17 단독, R7/R10/R11·R15/R25/R26/R27 약화 없음. R30 후보 계약을 미러에서
  선측정(변이 A 기각: M0 1 failed / 변이 B 채택: 생존자 `[M1]`). `make check` 279 passed,
  Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, `SAFETY_PASS`; 게임/Wine/Xvfb/PNG 0회.
  SUT/테스트 지문은 검수 전후 동일하고 lap265 기록값과 일치한다. 상세
  `docs/history/laps/20260912_lap266_middle_r29_review.md`, probe/report
  `..._probes/20260912_lap266_r29_review_probe.py`, `..._lap266_r29_review_report.json`,
  `..._lap266_r30_feasibility_probe.py`/`_report.json`, `..._lap266_r30b_feasibility_probe.py`/`_report.json`.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap237_compaction.md`,
  `..._lap254_compaction.md`, `..._lap260_compaction.md`,
  `..._lap266_compaction.md`(SHA256 `99cf172ae6c063000137e26ae08cfac18e9e3c4743c4c37b90c52f27bf4597d7`, 128줄).

## 바퀴 기록

- lap2~266과 STATUS 원문: `docs/history/laps/`; probe는 `docs/history/laps/probes/`.
- current escalation: `loop/ESCALATE_SOL`(lap266 middle: R29 FAIL → work tier R30); handoff:
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md` (R27 승인, R19/R28/R29 반려, 다음 R30 → R20).
