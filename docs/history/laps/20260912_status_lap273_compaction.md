# STATUS 원문 보존 — lap273 압축 직전

- 보존 시각: 2026-09-12 (lap273 middle 세션)
- 원문 SHA256: 355219b9804302d607ab449c1b2989f6dd2fbe6f3779c635fb7fd205e7cbbee3
- 원문 줄 수: 130
- 사유: lap273 middle F3-R2 독립 검수 결과를 STATUS에 반영하며 130줄 상한 유지.

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
work 구현 뒤 다음 새 middle 세션이 독립 검수해 **범위 승인**했다(R1 lap226 … R14 lap252).
직접 selection reader 실패 계열 R15/R25(lap256 승인), R26/R27(lap260 승인)도 같은 방식으로
닫혔다. 각 lap의 하네스·행렬·변이 근거와 lap245 무효 증거 판정은 `docs/history/laps/`와 압축
원문(lap237/lap254/lap260/lap266/lap271 compaction)에 보존돼 있다. 이 승인들은 모두 기계(1단)
승인이며 제품 G1 증거가 아니다.

**종료한 계열 — R17 커버리지 계약(동결).** R19(lap261)/R28(lap263)/R29(lap265)는 각각
lap262/264/266 검수에서 FAIL했고, lap269가 구현한 R30은 lap270 검수에서 **선언 범위 PASS /
R17 계약 종결 FAIL**이었다. R30은 R29보다 실질 개선(하중 5줄→58줄)이지만 신규 반례 **M11**이
`8 passed`로 생존한다. 근본 원인은 body 집합을 **변이 대상 파일 자신의 구문**에서 유도하는 것이라
앵커를 늘려도 고정점이 없다. lap270이 구조 변경 3안을 상위로 올렸고 **R31 착수는 금지**다.
상세는 `docs/history/laps/20260912_lap270_middle_r30_review.md`.

**lap271 middle — offline 큐 Stage B 호출 경로 분류(Astra 항목3) 완료.** 6축 독립 측정 결과
offline 큐 9건 중 **Stage B 선행조건은 F3-R2 한 건뿐**이다. F3-R2는 후보가 실제로 실패해도
카드가 `INCONCLUSIVE`만 내게 만든다(새 PASS 경로는 0건이므로 세탁이 아니라 **FAIL 능력의 상실**).
F2-R1/F3-R1/F6-R2는 경로 위에 있으나 도달 불가한 가드(H), R23/R24는 게이트 소비자 0인 필드(C),
R20/R21/R22는 review 하네스·테스트 전용(N)이다. 주차하되 삭제/PASS 전환은 하지 않는다.
상세와 근거표는 `docs/history/laps/20260912_lap271_middle_offline_queue_classification.md`.

**lap272 work — F3-R2 수리 완료(게임 실행 없음).** comparator가 producer의 측정된 timeout
5종만 `UNKNOWN_DISPUTED_ORACLE`로 분류하고, 하드 `FAIL`은 카드 `FAIL`, `BLOCKED`/`SKIP`/미지·
결측은 `INCONCLUSIVE`로 닫도록 수리했다. 새 PASS 경로는 없으며 다음 새 middle 세션의 독립 검수 대상이다. 상세 `docs/history/laps/20260912_lap272_work_f3_r2.md`.

최상위 증거 차단 S1은 원본↔원본도 nation/player spawn이 달라 scene mismatch가 나는
비결정성이다. F2-R2 때문에 장면 통제는 slot 대응 결정성도 함께 풀어야 한다. lap271이 Astra
항목4의 연구 계약 1쪽을 `docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`에 초안했다
(원본 `save/` 2개·`stagemap/` 24개 등 실재 출발 자산, 6개 재현 항목, RNG 주소 추측 금지,
research blocker 반환도 합격). 상위 재결 전에는 fresh Stage B를 실행하지 않는다.
모델 라우팅: Luna/high(work), Claude Opus5/high(middle), Astra/medium(strategy). Astra는 큰
분기·교착에서만 약 10 lap당 1회 이하이며 마지막 호출은 runtime lap214였다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 표시·논리 좌표 증거 있음; F3-R2, S1/F2-R2, fresh pair, WM_CLOSE 필요 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

**다음 middle(Opus5/high) — lap272 F3-R2 수리 독립 검수 1건(게임 실행 없음).**
새 PASS 경로 0개, timeout 5종의 `UNKNOWN_DISPUTED_ORACLE`, 하드 `FAIL`의 카드 `FAIL`,
`BLOCKED`/`SKIP`/미지·결측의 `INCONCLUSIVE`, M0 및 F1/F4/F5·scene gate·slot 강등 불변을
독립 확인한다. Stage B·게임 예산 0, 범위 승인≠제품 승인. R31과 F2-R1/F3-R1/F6-R2/R20~R24는 건드리지 않는다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **S1/F2-R2:** random seed·scene·slot 대응 결정성이 없다. 상위 재결 전 Stage B 양쪽 run,
  원본 재실행, R6-A/R6-C 금지. lap271 연구 계약은 초안이며 실행 예산 승인이 아니다.
- **R6-B-R2:** count 1→0 선택 상실을 응답으로 볼지는 Astra/사용자 재결 전 수정 금지.
- **R29 범위 승인 거부(lap266) 유지.** R30의 이름 튜플은 SHA 고정 SUT에 결합돼 개명 시
  M9/M10 `completeness_assert` 오탐이 나며, 완화 금지다.
- **상위 재결 대기(Astra/사용자) — 승격됨.** lap261~270 10바퀴 연속 *테스트의 테스트*에 바퀴를
  쓰는 동안 G1~G4 제품 증거 증가는 0이고, lap270이 R30에도 반례 M11이 남음을 보였다. 계열을
  1회로 끝낼 구조 변경 3안을 `loop/ESCALATE_SOL`에 올렸다. 재결 전 R31 착수 금지.
- offline 큐 — lap271 분류로 **선행조건은 F3-R2 하나**이고 나머지 8건은 주차(삭제 아님):
  **H**(경로 위, 도달 불가 가드) F2-R1·F3-R1·F6-R2 / **C**(게이트 소비자 0) R23·R24와 동종인
  `stage_budget_state` / **N**(하네스·테스트 전용) R20·R21·R22. 근거는 lap271 기록/보고서.
- 후보 WM_CLOSE teardown 결함과 실제 후보 scene/input evidence는 미해결이다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- **lap271 middle offline 큐 분류(기계 1단, 독립 측정):** A1 `_stage_report` 호출 **1건**
  (`:357`, 위치 인자 5) + 외부 참조 **0** → F2-R1 폴백 도달 불가. A2 `"last":` 기록 지점
  **1곳**(`runtime_env.py:2551`, `record_timeout`, result=`exc.classification`) → F3-R1 도달 불가.
  **A3 F3-R2 도달 실측**: 후보 카메라가 실제로 안 움직인 상태에서 `FAIL`/`BLOCKED`/`SKIP`과
  timeout 5종 **전부** stage `UNKNOWN_DISPUTED_ORACLE`/overall `INCONCLUSIVE`, 선택 축 하드
  `FAIL`도 동일, 대조군만 `PASS`, `new_pass_paths: []`. A4 `read_coverage`/`read_failure`/
  `stage_budget_state` 게이트 소비자 **0/0**, comparator의 `selection_count`는 자기가 쓰는 키이며
  count 결측은 fail-closed. A5 producer `_write_json`은 직렬화 선행 + 원자 replace, `tools/`의
  `open("x")` **0건**. A6 `open("x")`/`M0_control`은 probes 하위에만. 게임/Wine/Xvfb/PNG 0회.
  probe `docs/history/laps/probes/20260912_lap271_offline_queue_classification_probe.py`
  (`618d23dd…`) / report `..._classification_report.json`(`f1d7dc6b…`).
- **lap272 work F3-R2 (기계 1단):** `tools/compare_g1_stage_b.py`에 producer timeout 5종의 명시
  집합을 두고 하드 `FAIL`은 `FAIL`, `BLOCKED`/`SKIP`/미지·결측은 `INCONCLUSIVE`로 닫았다.
  전용 회귀 포함 comparator `24 passed`; 전체 `make check` `289 passed (45.46s)`, Ruff/compileall/
  mypy 10 files, `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`.
  게임/Wine/Xvfb/PNG 0회, 원본·보호 자산 불변, 제품 G1 증거 아님.
- lap271 `make check` `279 passed (43.72s)`, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`,
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` `SAFETY_PASS`. 제품 증거 아님.
- lap271이 재계산한 lap270 지문 5종(`862fd64a…`/`e4f6a834…`/`16f74629…`/`e7cd8593…`/`aefd3d27…`)은
  **전부 바이트 일치**하고 세션 전후 불변이다. lap270 판정은 그대로 유지한다.
- **lap270 middle R30 독립 검수: 선언 범위 PASS / R17 계약 종결 FAIL.** C1 body 81줄·정상 run
  58줄 실행·거부 run 0줄(R29의 5줄/0줄 대비 개선), C2 미러 M0 = 실저장소 `8 passed`, C3 M1~M10이
  lap269 선언값과 완전 일치, C4 R17 단언 한 줄 제거 시 M2/M3/M6/M7/M8 부활 → **R17 단독 사살자**,
  C5 **신규 M11 생존**(거부 전 260줄 실행, body 81→8줄 붕괴로 단언이 다시 공허).
  상세 `docs/history/laps/20260912_lap270_middle_r30_review.md`.
- lap146~252: Stage A/R1~R14와 F2/F3 수리·독립 승인, lap253~260: R15/R25/R26/R27 수리와 승인.
  lap261~266(R19/R28/R29)은 각 work 구현 → 다음 middle 검수 **FAIL(커버리지)**. 각 lap의 행렬·
  M0 대조군·변이 근거는 `docs/history/laps/`와 lap254/lap260/lap266 압축 원문에 있다.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap237_compaction.md`,
  `..._lap254_compaction.md`, `..._lap260_compaction.md`, `..._lap266_compaction.md`,
  `..._lap271_compaction.md`(SHA256 `c37944cbf13b5068d4e2aa2ea524f5f4183bc94f903d5ac1d13d6bfa8d61d4a1`, 127줄).

## 바퀴 기록

- lap2~266과 STATUS 원문: `docs/history/laps/`; probe는 `docs/history/laps/probes/`.
- lap267 Astra: 상위 우선순위와 middle/work 경계 기록. R29 FAIL 유지. 항목3/4를 middle에 위임.
- lap268 middle: R30 범위 승인 + work 실행 계약 인계. lap269 work: R30 구현.
- lap270 middle: R30 독립 검수(범위 PASS / 계약 FAIL), 신규 반례 M11, 구조 변경 제안 승격.
- lap271 middle: Astra 항목3 offline 큐 분류(선행조건 = F3-R2 하나) + 항목4 S1 연구 계약 초안.
- lap272 work: F3-R2 수리와 기계 검증 완료; 다음 새 middle 독립 검수 대기.
- 현재 라우팅: 다음은 **middle F3-R2 독립 검수 1건**. 상위 미결(S1/F2-R2/R6-B-R2 + R17 계열 구조
  변경 + S1 계약의 실행 예산)은 Astra/사용자 재결 대기.
