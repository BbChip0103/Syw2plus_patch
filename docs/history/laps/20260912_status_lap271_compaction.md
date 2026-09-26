# STATUS 원문 보존 — lap271 압축 직전

출처: `docs/STATUS.md` (lap270 상태)
- sha256: `c37944cbf13b5068d4e2aa2ea524f5f4183bc94f903d5ac1d13d6bfa8d61d4a1`
- 줄 수: 127
- 보존 시점: 2026-09-12 lap271 middle, 압축 전

```markdown
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

**종료한 계열 — R17 커버리지 계약.** `tests/test_review_probe_output.py::test_r6b_r17_…`은
lap228 SUT probe의 "출력 preflight 거부가 review 본문보다 먼저"를 고정한다. R19(lap261)/R28(lap263)/
R29(lap265)는 각각 lap262/264/266 검수에서 M6/M7/M8 생존으로 FAIL했다. lap268이 R30(변이 B =
named review result 대입의 합집합) 범위를 승인하고 lap269 work가 구현했다. **lap270 middle 독립
검수: 선언 범위 PASS, R17 계약 종결 FAIL.** M1~M10 수치는 완전히 재현되고 R17이 단독 사살자이며
R30은 R29보다 실질 개선(하중 5줄→58줄)이지만, 신규 반례 **M11**(7개 이름 전부를 별칭으로 계산하고
거부를 report write 위로 옮긴 뒤 canonical 이름을 그 아래에서 재바인딩)이 `8 passed`로 생존한다.
근본 원인은 body 집합을 **변이 대상 파일 자신의 구문**에서 유도하는 것이라 앵커를 늘려도 고정점이
없다. lap270은 R31을 열지 않고 구조 변경 제안을 상위로 올렸다.

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

**다음 middle(Claude Opus5/high) — Astra 항목3/4:** offline 큐 결함(R20~R24, F2-R1/F3-R1/F3-R2/
F6-R2)을 실제 Stage B producer/comparator 호출 경로로 분류하고, S1 결정성 연구 계약 1쪽을 초안한다.
**R31을 열지 않는다.** R17 계열 구조 변경(SUT SHA 단언 + 절대 줄 번호 고정, 또는 줄 커버리지 대신
거부 전 부작용 0회 단언)은 `loop/ESCALATE_SOL` lap270 항목에 대한 Astra/사용자 재결 이후에만 착수한다.
Stage B·게임 예산 0, 범위 승인≠제품 승인.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1/F2-R2:** random seed·scene·slot 대응 결정성이 없다. 상위 재결 전 Stage B 양쪽 run,
  원본 재실행, R6-A/R6-C 금지.
- **R6-B-R2:** count 1→0 선택 상실을 응답으로 볼지는 Astra/사용자 재결 전 수정 금지.
- **R29 범위 승인 거부(lap266) 유지.** R30의 이름 튜플은 SHA 고정 SUT에 결합돼 개명 시
  M9/M10 `completeness_assert` 오탐이 나며, 완화 금지다.
- **상위 재결 대기(Astra/사용자) — 승격됨.** lap261~270 10바퀴 연속 *테스트의 테스트*에 바퀴를
  쓰는 동안 G1~G4 제품 증거 증가는 0이고, lap270이 R30에도 반례 M11이 남음을 보였다. 계열을
  1회로 끝낼 구조 변경 제안을 `loop/ESCALATE_SOL`에 올렸다. 재결 전 R31 착수 금지.
- offline 큐 대기: **R20**(저장소 밖 미러 변이 하네스에 M0 대조군 없음 — lap246),
  **R21**(probe 출력이 직렬화 전에 `open("x")`로 절단 증거를 남기고 R7이 재시도를 막음 — lap248),
  **R22**(R13의 세 성질이 단일 테스트 하나에만 걸림 — lap250), **R23**(`read_coverage` 소비자가
  runtime_env 밖 0개 — lap250), **R24**(R14 `read_failure` 소비자 0개, record 최상위
  `selection_count`는 실패/미관측 모두 null — lap252), F2-R1/F3-R1/F3-R2/F6-R2.
  `stage_budget_state`도 runtime_env 밖 소비자가 0개이며 R23/R24와 같은 계열로 취급한다.
- 후보 WM_CLOSE teardown 결함과 실제 후보 scene/input evidence는 미해결이다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- **lap270 middle R30 독립 검수(기계 1단): 선언 범위 PASS / R17 계약 종결 FAIL.**
  검수 대상 지문은 lap269 기록과 동일(test `862fd64a…`, SUT probe `16f74629…`,
  runtime_env `e4f6a834…`)하며 검수 전후 불변. helper swap 없이 저장소 테스트 파일 그대로 미러링.
  C1 비공허성(신규): body **81줄**, 정상 run 268줄 중 **body 58줄 실행**, 거부 run 48줄 중
  **body 0줄**(최대 실행 줄 128) → R29의 5줄/0줄 공허 상태 대비 실질 개선.
  C2 mirror M0 `8 passed` = 실저장소 `8 passed`. C3 M1~M10 **lap269 선언값과 완전 일치**
  (생존 `[M1]`, M2/M3/M6/M7/M8 `r17_coverage_assert`, M9/M10 `completeness_assert`).
  C4 R17 단언 한 줄만 제거하면 M2/M3/M6/M7/M8 전부 `8 passed`로 부활 → **R17 단독 사살자**,
  R7/R10/R11/R15/R25/R26/R27 무손상. C5 **신규 M11 생존(`8 passed`)**: 거부는 정상(rc 2)이나
  **260줄이 거부 전에 실행**되고(baseline 48) body가 81→8줄로 붕괴해 단언이 다시 공허해진다.
  게임/Wine/Xvfb/PNG 0회. 상세 `docs/history/laps/20260912_lap270_middle_r30_review.md`,
  probe/report `..._probes/20260912_lap270_r30_review_probe.py`(`e7cd8593…`)/`_report.json`(`aefd3d27…`).
- lap270 `make check` `279 passed (45.47s)`, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`,
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`. 제품 증거 아님.
- lap269 work: R30 구현(`_review_body_lines()` 합집합 + report write + completeness 단언),
  targeted `8 passed`, `make check` `279 passed (43.15s)`. lap270이 독립 재현함.
- lap146~252: Stage A/R1~R14와 F2/F3 수리·독립 승인, lap253~260: R15/R25/R26/R27 수리와 승인.
  각 lap의 행렬·M0 대조군·변이 근거는 `docs/history/laps/`와 lap254/lap260 압축 원문에 있다.
- lap261~266(R19/R28/R29): 각 work 구현 → 다음 middle 검수 **FAIL(커버리지)**, 생존자 M6/M7/M8.
  상세는 `..._lap265_work_r29.md` 등 각 lap 기록에 있다.
- **lap266 middle R29 독립 검수 FAIL(커버리지, 기계 1단)**: C0 8 passed; C1 계약 독립 재유도
  (preflight 123~130, anchor 137, `json.dump` 412, helper body `[137,412]` 276줄; 정상 run 201줄
  실행, 거부 run **0줄** → baseline에서 비공허); C2 미러 M0 8 = 실저장소 8; C3 변이 7종에서
  M1 의도 생존(오탐 0), M2/M3/M6/**M7 사살**(R29의 lap264 결함 수리 확인), 신규 **M8**
  (M7 + `NEGATIVE_PATTERNS` 개명 + report write 직전 decoy 별칭) **8 passed 생존** — helper body가
  5줄로 줄고 그중 0줄 실행이라 단언이 다시 공허한데, module-level review 문 171/231줄이 거부
  전에 실행된다(baseline 거부는 15줄). C4: 앵커 변경에 사살 귀속, `assert review_start <
  report_write_line`은 하중 0, R17 제거 시 5종 모두 생존. R30 후보 계약을 미러에서 선측정
  (변이 A 기각: M0 1 failed / 변이 B 채택: 생존자 `[M1]`). Fast·safety 전부 PASS, 게임 0회. 상세
  `docs/history/laps/20260912_lap266_middle_r29_review.md`, probe/report
  `..._probes/20260912_lap266_r29_review_probe.py`, `..._lap266_r29_review_report.json`,
  `..._lap266_r30_feasibility_probe.py`/`_report.json`, `..._lap266_r30b_feasibility_probe.py`/`_report.json`.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap237_compaction.md`,
  `..._lap254_compaction.md`, `..._lap260_compaction.md`,
  `..._lap266_compaction.md`(SHA256 `99cf172ae6c063000137e26ae08cfac18e9e3c4743c4c37b90c52f27bf4597d7`, 128줄).

## 바퀴 기록

- lap2~266과 STATUS 원문: `docs/history/laps/`; probe는 `docs/history/laps/probes/`.
- lap267 Astra: 기존 지문/JSON 대조, 상위 우선순위와 middle/work 경계 기록. R29 FAIL 유지.
- lap268 middle: R30 범위 승인 + work 실행 계약 인계. R29 반려 유지.
- lap269 work: R30 구현·Fast/변이 검증 완료, 기록 `docs/history/laps/20260912_lap269_work_r30.md`.
- lap270 middle: R30 독립 검수 완료(범위 PASS / 계약 FAIL), 신규 반례 M11 기록, 구조 변경 제안 승격.
- 현재 라우팅: 다음은 **middle tier Astra 항목3/4**. 상위 미결(S1/F2-R2/R6-B-R2 + R17 계열 구조
  변경)은 Astra/사용자 재결 대기.
```
