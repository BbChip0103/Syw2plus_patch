# 2026-09-12 | lap275 STATUS 압축 전 원문 보존

- 원문 SHA256: `dff5d89576c8e6fcb0c31c81c32f7cd8fd8501b5b94a07a8eeac85c4f77e1639`
- 원문 줄 수: 139 (130줄 상한 초과로 압축)
- 압축 사유: lap275 독립 검수 결과와 큐 고갈 승격을 추가하며 상한을 넘었다.

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
원문(lap237/lap254/lap260/lap266/lap271/lap273 compaction)에 보존돼 있다. 이 승인들은 모두
기계(1단) 승인이며 제품 G1 증거가 아니다.

**종료한 계열 — R17 커버리지 계약(동결).** R19(lap261)/R28(lap263)/R29(lap265)는 각각
lap262/264/266 검수에서 FAIL했고, lap269가 구현한 R30은 lap270 검수에서 **선언 범위 PASS /
R17 계약 종결 FAIL**이었다. R30은 R29보다 실질 개선(하중 5줄→58줄)이지만 신규 반례 **M11**이
`8 passed`로 생존한다. 근본 원인은 body 집합을 **변이 대상 파일 자신의 구문**에서 유도하는 것이라
앵커를 늘려도 고정점이 없다. lap270이 구조 변경 3안을 상위로 올렸고 **R31 착수는 금지**다.
상세는 `docs/history/laps/20260912_lap270_middle_r30_review.md`.

**lap271 middle — offline 큐 분류 완료.** 6축 독립 측정으로 offline 큐 9건 중 **Stage B
선행조건은 F3-R2 한 건뿐**임을 확인했다(F2-R1/F3-R1/F6-R2=도달 불가 가드, R23/R24와
`stage_budget_state`=게이트 소비자 0, R20~R22=하네스·테스트 전용). 주차하되 삭제/PASS 전환은
하지 않는다. 같은 lap이 S1 연구 계약 1쪽을
`docs/work/active/G1_S1_DETERMINISM_RESEARCH_CONTRACT.md`에 초안했다(실재 출발 자산, 6개 재현
항목, RNG 주소 추측 금지, research blocker 반환도 합격). 상세는 lap271 기록.

**lap274 work — F3-R2-R1 수리(게임 0회).** producer 두 실제 경로의 6종 어휘에
`UNKNOWN_STATE_READ_COVERAGE`를 보완하고 AST 드리프트 회귀를 추가했다.
**lap275 middle — 독립 검수 완료, 선언 범위 승인(1단 기계).** 스코프 규칙이 다른 자체 AST
유도가 같은 6종을 냈고(양방향 차 0), classification이 comparator가 읽는 `inputs[i]["result"]`에
실제로 도달함을 처음 확인했다. 169칸 전수 행렬과 변이 귀속으로 회귀가 실제 사살자임도 확인했다.
상세 `..._lap274_work_f3_r2_r1.md`, `..._lap275_middle_f3_r2_r1_review.md`, 이전 근거는
`..._lap273_middle_f3_r2_review.md`.

**F3-R2가 닫히며 실행 가능한 offline 큐가 비었다.** lap271 분류상 나머지 8건은 Stage B를
열지 못하고, Stage B는 S1/F2-R2 재결 전 금지다. 다음 경로는 상위 재결뿐이며 lap275 항목으로
`loop/ESCALATE_SOL`에 승격했다.

최상위 증거 차단 S1은 원본↔원본도 nation/player spawn이 달라 scene mismatch가 나는
비결정성이다. F2-R2 때문에 장면 통제는 slot 대응 결정성도 함께 풀어야 한다. 상위 재결 전에는
fresh Stage B를 실행하지 않는다.
모델 라우팅: Luna/high(work), Claude Opus5/high(middle), Astra/medium(strategy). Astra는 큰
분기·교착에서만 약 10 lap당 1회 이하이며 마지막 호출은 runtime lap214였다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 표시·논리 좌표 증거 있음; F3-R2 2단, S1/F2-R2, fresh pair, WM_CLOSE 필요 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

**상위(Astra/사용자) 재결 1건 — 실무 작업 없음.** F3-R2 종결로 허용되면서 유용한 work
과제가 0이 됐다. 다음 중 하나를 골라야 한다: (a) S1/F2-R2 결정성 재결 또는 lap271 S1 연구
계약의 실행 예산 승인, (b) lap270 R17 구조 3안 택일(+ lap275가 기록한 추출기 1줄 사각 M-d/M-e
처리 범위), (c) R6-B-R2 재결, (d) 제품 증거 0인 G2~G4로 루프 방향 전환.
재결 전 Stage B·R31·신규 수리 계열 착수 금지.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경, evidence 재사용, blind retry, PASS 완화 금지.
- production 클릭 금지. 정상 비활성은 BLOCKED로 남기고 후속 입력은 계속한다.
- **실행 가능한 work 과제 0 — 상위 재결 없이는 다음 바퀴에 바꿀 것이 없다.** F3-R2는
  lap275가 1단 승인해 닫혔고 남은 offline 8건은 Stage B를 열지 못한다.
- **lap274 회귀의 알려진 사각 2건(수리 금지, 기록만).** 세 번째 함수의 새 분류(M-d)와
  `FAIL_`/`UNKNOWN_` 접두어가 아닌 분류명(M-e)은 `26 passed`로 생존한다. 원인은 추출기의
  함수 화이트리스트와 접두어 정규식이며, R17 계열과 같은 모양이라 재결 전 착수 금지다.
- **S1/F2-R2:** random seed·scene·slot 대응 결정성이 없다. 상위 재결 전 Stage B 양쪽 run,
  원본 재실행, R6-A/R6-C 금지. lap271 연구 계약은 초안이며 실행 예산 승인이 아니다.
- **R6-B-R2:** count 1→0 선택 상실을 응답으로 볼지는 Astra/사용자 재결 전 수정 금지.
- **R29 범위 승인 거부(lap266) 유지.** R30의 이름 튜플은 SHA 고정 SUT에 결합돼 개명 시
  M9/M10 `completeness_assert` 오탐이 나며, 완화 금지다.
- **상위 재결 대기(Astra/사용자) — 승격됨.** lap261~270 10바퀴 연속 *테스트의 테스트*에 바퀴를
  쓰는 동안 G1~G4 제품 증거 증가는 0이고, lap270이 R30에도 반례 M11이 남음을 보였다. 계열을
  1회로 끝낼 구조 변경 3안을 `loop/ESCALATE_SOL`에 올렸다. 재결 전 R31 착수 금지.
- offline 큐 나머지 8건은 lap271 분류대로 주차(삭제 아님): **H** F2-R1·F3-R1·F6-R2 /
  **C** R23·R24와 `stage_budget_state` / **N** R20·R21·R22.
- 후보 WM_CLOSE teardown 결함과 실제 후보 scene/input evidence는 미해결이다.
- G2~G4는 제품 증거가 없다.

## 검증 상태

- **lap275 middle F3-R2-R1 독립 검수 — 선언 범위 PASS(게임 0회):** 자체 AST 유도(파일 전체
  `classification=` 기준)와 comparator 선언이 6종 양방향 일치, producer_only/comparator_only 0.
  `record_timeout`→`record` 9번째 위치인자→`entry["result"]` 연결 확인. 13×13=169칸 전수에서
  hard FAIL 우선·disputed·(PASS,PASS) 1칸뿐·결측 INCONCLUSIVE·scene gate가 hard FAIL도 덮음·
  slot 강등·production 169칸 `NOT_COMPARED`·M0 control PASS. 변이 M-a/M-b/M-c 각각
  `1 failed/25 passed`(회귀 단독 사살), M-d/M-e는 생존(위 블로커). `26 passed`,
  `make check` `291 passed (44.66s)`, `CONTEXT_PASS`, `SAFETY_PASS`. 변이는 `/tmp/lap275_mut/`
  사본에서만 했고 저장소 3파일 해시는 lap274 기록값과 동일. probe
  `3f2d886a…`. 제품 G1 증거는 아니다.
- **lap274 work F3-R2-R1 기계 검증(게임 0회):** producer AST 6종과 comparator 집합이 양방향
  일치. 33칸 행렬에서 coverage 포함 6종은 `UNKNOWN_DISPUTED_ORACLE`/overall `INCONCLUSIVE`,
  hard `FAIL`은 `FAIL`, `BLOCKED`/`SKIP`/미지·결측은 `INCONCLUSIVE`. 300칸 전수 탐색 PASS는
  3건(양쪽 `PASS`)뿐이며 비-PASS PASS 경로는 0; hard FAIL 우선과 scene/slot/production 불변.
  대상 회귀 `26 passed`, `make check` `291 passed (44.85s)` + Ruff/compileall/mypy/CONTEXT_PASS,
  safety `SAFETY_PASS`. comparator `9b684cec…`, tests `74b7d337…`, producer 불변 `e4f6a834…`.
  독립 재실행 명령/수치와 fixture는 lap 기록에 남겼고 제품 G1 증거는 아니다.
- **lap273 middle F3-R2 독립 검수:** 수리 전 5종/producer 6종 불일치를 확인한 기계 1단 기록.
  `docs/history/laps/20260912_lap273_middle_f3_r2_review.md`에 원문·probe 근거 보존.
- **lap272 work F3-R2:** comparator 전용 회귀 포함 `24 passed`; `make check` `289 passed
  (45.46s)`; `SAFETY_PASS`. 게임/Wine/Xvfb/PNG 0회, 원본·보호 자산 불변.
- **lap270 middle R30 독립 검수: 선언 범위 PASS / R17 계약 종결 FAIL.** C4에서 R17 단언 한 줄
  제거 시 M2/M3/M6/M7/M8 부활(= R17 단독 사살자), C5 **신규 M11 생존**(body 81→8줄 붕괴).
  상세 `docs/history/laps/20260912_lap270_middle_r30_review.md`.
- lap146~260: Stage A/R1~R14/R15/R25/R26/R27 수리와 독립 승인. lap261~266(R19/R28/R29)은 각
  work 구현 → 다음 middle 검수 **FAIL(커버리지)**.
- pre-compaction 원문: `docs/history/laps/20260912_status_lap237_compaction.md`,
  `..._lap254_compaction.md`, `..._lap260_compaction.md`, `..._lap266_compaction.md`,
  `..._lap271_compaction.md`(`c37944cb…`, 127줄),
  `..._lap273_compaction.md`(`8b6aff38…`; 원문 `355219b9…`, 130줄).

## 바퀴 기록

- lap2~270과 STATUS 원문: `docs/history/laps/`; probe는 `docs/history/laps/probes/`.
- lap271 middle: offline 큐 분류(선행조건 = F3-R2 하나) + S1 연구 계약 초안.
- lap272 work: F3-R2 수리와 기계 검증.
- lap273 middle: lap272 독립 검수 — producer 6종 중 comparator 누락 1종 확인.
- lap274 work: F3-R2-R1 수리·AST 드리프트 회귀와 Fast 검증, 게임 실행 0.
- lap275 middle: F3-R2-R1 독립 검수 — 선언 범위 승인, 사각 2건 기록, 큐 고갈 승격.
- 현재 라우팅: 다음은 **상위(Astra/사용자) 재결 1건**. 실무 과제 없음. 상위 미결은
  S1/F2-R2, R6-B-R2, R17 계열 구조 변경, S1 계약 실행 예산, 루프 방향(G2~G4)이다.
```
