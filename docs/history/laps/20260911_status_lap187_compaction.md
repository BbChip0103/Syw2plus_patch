# STATUS pre-compaction snapshot — lap 187

A-15 구현 및 middle 검수 직전 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `702c354248fa13b120298b356038a0ffa49106fa0ab1a88d26370db041bbc52c`
- line count: `150`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. 최우선 G1은 원본 800×600 논리 구도/UI를 유지한
1600×1200 정수 2배 출력이다. G2는 전비 5000 숫자 패치만 있고 8인 부하·개체 풀/메모리
확장 증명이 없다. G3 16인과 G4 길찾기·AI는 구현 전이다.

pinned DxWrapper 후보는 private install/uninstall, SHA 고정, byte-exact restore, opt-in
`ddraw=n,b`, module evidence를 갖췄다. 반복 fresh runtime에서 client/capture 1600×1200,
logical DirectDraw 800×600, scale 2×2, 선변환 없는 입력, PS9→PS7→PS3를 확인했다.

lap166 P4는 close 전 30초간 tick `46→1013`과 서로 다른 캡처 4장으로 후보의 실제 인게임
지속 렌더를 증명했다. WM_CLOSE 후에는 tick이 멈추고 `Lock2 DDERR_SURFACELOST`가 1ms 안에
100줄 상한을 채우며 정상 teardown이 없다. lap168 P5 builtin `ddraw=b` 대조군은 정상 exit,
summary 1, validator PASS, surface-lost 0으로 종료 결함을 DxWrapper native 경로에 귀속했다.

Astra/medium은 약 10회의 work/middle 뒤 큰 분기 lap170에서 한 번만 호출됐다. 최종 방향은
소스 없는 DxWrapper 수리를 추측하지 않고 **G1 실제 표시·입력 합격 증거를 먼저 완성**하는 것이다.
Lock entry/exit 계측 P6는 종료 수리용 2순위 카드다.

카드2 Stage A는 원본/후보 공용 입력 시퀀스, production fail-closed BLOCKED 후 후속 관측 계속,
menu 대칭 판정, 즉시 evidence flush, 승인 주소 장면 evidence, `--g1-input-sequence` opt-in을 갖췄다.
A-6~A-10은 required input 중 BLOCKED/FAIL 시 overall PASS 금지, 좌표 무변환, off-mode 비개입,
양방향 회귀를 고정한다.

lap178 A-11은 각 단계의 진입/잔여 예산과 `FAIL_NO_EFFECT` 대 `UNKNOWN_BUDGET_EXHAUSTED`를
분리했다. lap179 Opus/auto가 source 2/2, 코드·회귀와 `make check` 202 passed/`SAFETY_PASS`를
직접 재현해 A-11을 승인했다. 과거 middle 권한 SKIP은 `LOOP_PERMISSION_MODE=auto`로 해소됐다.

lap180 A-12(Stage A3)는 관측창 노출과 입력 phase 벽시계를 구현했다. 단계 예산 시계는
`begin_stage`에서 사전작업 **이전에** 시작하며(유지 결정), 각 단계 예산은 10초·합계 30초,
phase 벽시계 상한은 31.5초다. 전체 입력 phase의 경과/항목별 비용과 초과 원인을 예외·cleanup에서도
보존한다. 관측창 잘림은 UNKNOWN이며 PASS가 아니다. 게임은 실행하지 않았다.

lap181 middle(Opus5/auto)은 source SHA 2/2 MATCH, `make check` 204 passed, runtime pytest 91,
Ruff/compileall/mypy/CONTEXT_PASS/SAFETY_PASS를 직접 재현했다. **판정: A-12-2 승인,
A-12-1 조건부 반려.** `_wait_state`의 `window_truncated`가 임계값 없이 잘림>0에서 참이라
실제 run(사전작업 항상 >0)에서는 `FAIL_NO_EFFECT`가 도달 불가다. 9.95초 관측과 2.0초 관측이
같은 UNKNOWN으로 접히며, A-12-1이 요구한 "임계값과 근거 기록"이 없다. 수리 카드는 A-13이다.
Stage B는 계속 닫혀 있다.

lap182 work는 A-13을 구현했다. lap182는 근거를 "lap181 정상 사전작업 상한 0.30초"로 적었으나
(lap183이 정정: 그 값은 실측이 아니라 가짜 시계 probe 입력이다) 실제 채택된 근거는 비율이다.
잘림 허용비율 25%(2.5초) 상수와 실제 잘림량/임계값 evidence를 추가했다. 0초와 0.3초
잘림은 `FAIL_NO_EFFECT`, 8초 잘림은 `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`, 공용 예산
소진은 `UNKNOWN_BUDGET_EXHAUSTED`로 유지되며, 전체 `make check` 205 passed와 safety를 통과했다.
중간 tier 독립 검수 전까지 Stage B는 계속 닫혀 있다.

lap183 middle(Opus5/auto)은 source SHA 2/2 MATCH, `make check` 205 passed, runtime pytest 92,
Ruff/compileall/mypy/CONTEXT_PASS/SAFETY_PASS를 직접 재현하고 독립 경계 probe를 돌렸다.
**판정: A-13 승인.** 사전작업 0.00/0.05/0.30초가 모두 `FAIL_NO_EFFECT`로 복귀해 lap181의 죽은
분류가 해소됐고, 경계는 엄격 부등호(2.5000초 FAIL / 2.5001초 UNKNOWN)로 단조롭다.
`UNKNOWN_BUDGET_EXHAUSTED` 우선순위와 A-12 evidence 필드는 유지, 금지 항목은 무변경이다.
동반 정정 카드 A-14: 주석의 "measured pre-poll work <=0.30s (lap181)"는 사실이 아니다 —
lap181 원문은 그 값을 가짜 시계 probe 입력으로 적었고 실제 게임 run은 0회라 실측치가 없다.
2.5초는 **실측이 아닌 설계 가정**이며, Stage B 첫 run이 실제 잘림 분포로 재평가해야 한다.

lap184 work는 A-14를 구현했다. 코드 주석과 lap182 기록의 0.30초 근거를 가짜 시계 probe로
정정하고 실제 사전작업 분포는 미측정임을 명시했다. 기존 3자리 `truncation_seconds`는
유지하면서 9자리 `truncation_ratio`와 threshold ratio/비교 결과를 evidence에 추가했고,
2.4999초/2.5001초 경계 회귀를 고정했다. 값 0.25·분류 순서·기존 필드는 불변이다.

lap185 middle(Opus5/auto)은 source SHA 3/3 MATCH, `make check` 207 passed, runtime pytest 94,
targeted 10, Ruff/compileall/mypy 9파일/CONTEXT_PASS/SAFETY_PASS를 직접 재현하고 lap184 테스트를
쓰지 않는 독립 경계 probe를 돌렸다. **판정: A-14 승인.** 3자리 `truncation_seconds`는
2.4999/2.5000/2.50004/2.5001을 모두 2.5로 접지만 9자리 `truncation_ratio`는 이를 분리하며,
2.5000초 정확값은 `FAIL_NO_EFFECT`로 남아 엄격 부등호가 유지된다. 주석 provenance 정정도 확인했다.
동반 카드 A-15: `stage_deadline=min(run_deadline, …)`에서 run 예산이 clamp하면
`truncation_seconds`가 사전작업이 아닌 예산 소진을 재고, ratio 0.7 > threshold 0.25인데
`truncation_exceeds_threshold`가 False로 기록된다(probe: pre-poll 2.0초/timeout 5.0초).
분류는 `UNKNOWN_BUDGET_EXHAUSTED`로 올바르나 evidence가 자기모순이며, Stage B가 기록해야 할
실제 잘림 분포를 오염시킨다. 두 원인을 분리 기록하고 clamp 회귀를 고정해야 한다.

lap186 work는 A-15를 구현했다. `truncation_seconds`/ratio는 stage 시작 후 wait 진입 전의
pre-poll 잘림만 기록하고, run deadline에 의한 축소는 `run_deadline_clamped`와
`run_deadline_clamp_seconds`로 분리했다. pre-poll 2.0초/run timeout 5.0초/stage budget 10.0초
fixture는 effective window 3.0초, pre-poll 2.0초/ratio 0.2/threshold 초과 false,
`UNKNOWN_BUDGET_EXHAUSTED`를 기록하도록 회귀 고정했다. `make check` 208 passed,
SAFETY_PASS이며 게임/Wine/Stage B/P6 실행은 0회다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Astra는 자동/정기 호출하지 않고 큰 분기·반복 교착에서만, 대략 work/middle 10 lap당 1회 이하로
쓴다. high는 medium으로 고위험 복수 경로를 결정할 수 없을 때만 쓴다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 후보 2배 표시·논리 구도·입력·30초 지속 렌더 PASS; A-14 lap185 middle 독립 승인(독립 경계 probe 포함); 실제 원본/후보 입력 비교 없음; WM_CLOSE 종료 결함 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

새 middle tier(Opus5)가 A-15를 독립 검수한다: source SHA, clamp/pre-poll evidence 분리,
`truncation_exceeds_threshold`와 ratio/threshold 일치, clamp 분류 우선순위를 직접 확인한다.
임계값 0.25·분류 우선순위·기존 PASS/FAIL 판정은 변경 금지. Stage B/P6는 사용자 승인 전 계속 금지.
사용자 승인이 없는 Stage B와 P6는 계속 금지다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경 금지. 보호 EXE SHA:
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 실패 run/prefix/display/build 재사용, 임의 retry, validator/summary/exit 요구 완화 금지.
- Stage A 승인 전 Stage B 실제 원본/후보 run과 P6를 시작하지 않는다.
- A-13/A-14는 lap183/lap185 middle 독립 승인을 받았지만 그것은 모델 기술 컨펌이다. Stage B
  개시는 사용자 마일스톤 승인이 있어야 하며 APPROVALS에는 아직 없다.
- A-15 구현은 lap186에서 완료했으나 새 middle 독립 검수가 남았다. Stage B 첫 run 전
  pre-poll 분포로 2.5초 가정을 재평가해야 한다.
- 임계값 2.5초는 실측 사전작업 분포로 검증되지 않은 설계 가정이다. 실제 run의 사전작업이
  2.5초를 넘으면 정상 run이 통째로 UNKNOWN으로 접혀 lap181 결손이 형태만 바꿔 재발한다.
- production 입력 효과 미관측은 BLOCKED이며 required input 전체 PASS가 될 수 없다.
- 원본/후보 동일 시작 상태는 미증명이다. random seed 미노출 때문에 Tier-1/Tier-2로 분리한다.
- minimap은 단순 변화가 아니라 camera 절대 목적지 비교가 필요하다.
- DxWrapper 종료 결함은 실제 수정 대상이지만 표시 합격 증거의 선행조건은 아니다.
- G1 실제 나란히 비교/입력 증거와 G2~G4 제품 증거는 아직 없다.

## 검증 상태

- lap146~169: diagnostic 종료 PASS, 후보 2배 표시·입력·30초 지속 렌더 PASS, DxWrapper close
  결함을 builtin 대조로 귀속. Fast 192/safety/build/cleanup/config 원복 PASS.
- lap170 Astra/medium: 큰 분기 1회. G1 합격 증거 우선, P6 주차.
- lap171~177: Stage A 설계·구현·독립 검수. A-1~A-11 승인, middle 게이트 실행 권한 해소.
- lap178 work: A-11 구현, `make check` 202 passed, runtime pytest 89, safety/static PASS.
- lap179 middle: A-11 독립 승인, Opus가 202 passed/safety 직접 재현, A-12 발부.
- lap180 work: A-12 구현, `make check` 204 passed, runtime pytest 91, safety/static PASS, game 0.
- lap181 middle: A-12-2 승인/A-12-1 조건부 반려, 게이트 204·91·SAFETY_PASS 독립 재현, game 0.
- lap182 work: A-13 구현, `make check` 205 passed, runtime pytest 92, safety/static PASS, game 0.
- lap183 middle: A-13 독립 승인, 게이트 205·92·SAFETY_PASS 직접 재현, 경계 probe, A-14 발부, game 0.
- lap184 work: A-14 주석/기록 provenance 정정 및 경계 evidence 정밀도 구현, 게임/Stage B/P6 0회.
- lap185 middle: A-14 독립 승인, 게이트 207·94·10·SAFETY_PASS 직접 재현, 독립 경계 probe,
  A-15 발부, 게임/Stage B/P6 0회.
- lap186 work: A-15 구현, pre-poll/clamp 분리 및 clamp 회귀, `make check` 208 passed,
  `SAFETY_PASS`, 게임/Stage B/P6 0회.
- pre-compaction snapshot SHA는 `docs/history/laps/20260911_status_lap181_compaction.md` 헤더에 보존.

## 바퀴 기록

- lap2~177 및 이전 STATUS 원문: `docs/history/laps/`.
- latest snapshot: `docs/history/laps/20260911_status_lap181_compaction.md`.
- lap179 middle: `docs/history/laps/20260911_lap179_middle_a11_verification.md`.
- lap180 work: `docs/history/laps/20260911_lap180_luna_g1_card2_stageA3.md`.
- lap181 middle: `docs/history/laps/20260911_lap181_middle_a12_verification.md`.
- lap182 work: `docs/history/laps/20260911_lap182_luna_a13_threshold.md`.
- lap183 middle: `docs/history/laps/20260911_lap183_middle_a13_verification.md`.
- lap184 work: `docs/history/laps/20260911_lap184_luna_a14_threshold_provenance.md`.
- lap185 middle: `docs/history/laps/20260911_lap185_middle_a14_verification.md`.
- current escalation: `loop/ESCALATE_SOL`.
- current handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`.
- model routing: `docs/history/20260911_model_routing_update.md`.
