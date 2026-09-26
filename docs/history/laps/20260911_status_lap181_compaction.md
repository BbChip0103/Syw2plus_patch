# STATUS pre-compaction snapshot — lap 181

A-12 Stage A3 구현 및 독립 검수 직전 보존한 `docs/STATUS.md` 원문이다.

- pre-compaction SHA256: `0ef4c5fa507ed0d6cd82a8c90b82a19e496d136e0f1f64c62ac2a3b481f8bd4c`
- line count: `175`

---

# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

G1~G4는 제품 단위로 모두 미완료다. 최우선 G1은 원본 800×600 논리 구도/UI를 유지한
1600×1200 정수 2배 출력이다. G2는 전비 5000 숫자 패치만 있고 8인 부하·개체 풀/메모리
확장 증명이 없다. G3 16인과 G4 길찾기·AI는 구현 전이다.

pinned DxWrapper 후보는 private install/uninstall, SHA 고정, byte-exact restore, opt-in
`ddraw=n,b`, module evidence를 갖췄다. 반복 fresh runtime에서 client/capture 1600×1200,
logical DirectDraw 800×600, scale 2×2, 선변환 없는 입력, PS9→PS7→PS3를 확인했다.

lap166 P4는 close 전 30초간 tick `46→1013`(약 33.3/s)과 서로 다른 캡처 4장으로 후보의 실제
인게임 지속 렌더를 증명했다. WM_CLOSE 후에는 tick 1026에서 50.04초간 정지하고, 같은 시각
`Lock2 DDERR_SURFACELOST` 로그가 1ms 안에 100줄 상한을 채우며 process exit/summary/DLL detach가
없다. lap168 P5는 현재 harness의 builtin `ddraw=b` 대조군이 정상 exit, summary 1, validator PASS,
`DDERR_SURFACELOST` 0임을 보여 미종료 결함을 DxWrapper native 경로에 귀속했다.

Astra/medium lap170은 약 10회의 work/middle 뒤 큰 분기에서만 호출됐다. P5 경로 표기 오류로
직접 판정은 중단했지만, lap171 Opus가 실제 산출물 SHA 6/6과 N 귀속을 재확인했다. 상위 방향은
소스 없는 DxWrapper 설정 수리를 추측하지 않고 **G1 실제 표시·입력 합격 증거를 먼저 완성**하는
것이다. Lock 계측 P6는 종료 수리용 2순위 카드다.

lap172 work는 카드2 Stage A를 구현했다. 원본/후보 공용 입력 시퀀스, production fail-closed
BLOCKED 후 후속 관측 계속, menu 대칭 판정, 매 단계 즉시 evidence flush, 승인 주소 장면 evidence,
`--g1-input-sequence` opt-in과 회귀가 추가됐다. 게임은 실행하지 않았다. `make check` 196 passed,
Ruff/compileall/mypy/context/safety PASS다.

lap173 Opus 독립 검수는 source SHA 2/2와 허용 범위, A-1~A-5 핵심 구현을 승인했지만 Stage A를
**조건부 반려**했다. 후보 verdict가 입력 결과를 보지 않아 production BLOCKED에도 overall PASS가
가능하며, 이 불변식을 직접 잠그는 필수 회귀가 없다. 좌표 단언과 90초 전체 예산 판단도 명시적으로
잠가야 한다. Stage B는 A-6~A-9 수리와 새 middle 승인 전까지 금지다.

lap174 work는 A-6~A-8을 최소 변경으로 수리했다. baseline·후보가 공용 입력 판정 함수를 사용하고,
후보 overall이 opt-in required input을 만족해야만 PASS가 되며 입력 관측/production BLOCKED/teardown을
분리 기록한다. 시퀀스 테스트는 논리 좌표 전송과 production 미전송을 단언한다. A-9는 기존 단일
`started + timeout` 예산을 유지하고 단계별 마감시한은 도입하지 않기로 기록했으며, Stage B에서
단계별 monotonic 구간·tick·총 elapsed를 실측할 계획이다. 게임 실행은 0회다.

lap175 middle 독립 재검수는 A-6·A-7·A-8을 정적 검증으로 **승인**했다. 술어 결합 순서, baseline·후보
공용 함수 사용, 호출부 전달, 5개 태그 전원 PASS 대조 케이스, 전송 좌표와 production `(670,490)`
미전송, ×2 무선변환을 코드와 회귀에서 확인했다. 그러나 **Stage A 승인은 보류**다. 이유 둘: 이 세션이
`make check`/`pytest`/`safety.sh`를 권한 문제로 재실행하지 못해 lap174의 198 passed를 독립 재현하지
못했고, A-9 기록이 실제로 대기하는 세 wait의 예산을 다루지 않았다. 실측으로 기동→PS3 ≈8.4초,
builtin close+finalization ≈2.3초이며 후보 close 정체는 ≈50초다. 즉 dwell 0 후보 run은 PS3 이후 약
81초를 세 입력 wait와 close 전체가 공유하고, `_wait_state`는 `record()` 이전에 예외를 던지므로 한
단계 무반응이 그 단계와 이후 증거를 통째로 없앤다. FAIL과 예산 소진 UNKNOWN도 현재 메시지로
분리되지 않는다.

lap176 work는 A-9R을 기록으로 보강하고 A-10 off-mode 회귀를 추가했다. 세 wait 모두에 대해 단계
진입/종료 monotonic 시각, 잔여 공용 예산, tick 및 predicate 관측을 evidence에 즉시 flush하는
Stage B 기록 방법을 명시했다. 현재 공용 deadline만으로는 FAIL과 예산 소진 UNKNOWN을 분리할 수
없으므로 단계 deadline 또는 동등한 구조화 timeout 원인이 Stage B 전제이며, 이번 바퀴에는 런타임
동작을 바꾸지 않았다. A-10 synthetic 회귀가 추가됐고 `make check` 199 passed, 별도 pytest
199 passed, Ruff/compileall/mypy/context/safety/git diff check가 PASS했다. 게임 실행은 0회다.

lap177 middle 독립 판정은 **Stage A를 내용 승인**했다. A-9R의 세 구조적 주장(`_wait_state`의
공용 마감시한 단독, wait 예외가 `record()` 이전에 발생해 단계·이후 증거 소실, "효과 없음"과
"예산 소진"의 동일 메시지)을 코드로 재확인했고, P5 evidence로 예산 산술도 재계산해 기동→PS3
`8.438초`·close+finalization `2.274초`·PS3 이후 공유 예산 `≈81.6초`를 얻었다. A-10 off-mode 회귀도
유효하다. 다만 **Stage B는 두 이유로 여전히 닫혀 있다**: (1) 단계별 예산/구조화 timeout 원인이
미구현이라 신규 카드 **A-11(Stage A2)** 을 발부했다. (2) 이 세션도 `make check`/`pytest`/`safety.sh`가
권한으로 차단돼 1단 게이트 독립 재현이 3회 연속 SKIP이다. lap166 close 정체 `50.04초`에서
입력 세 단계 총 예산 상한 `T <= 31.5초`를 파생해 A-11에 제약으로 넣었다.

lap178 work는 A-11(Stage A2)를 구현했다. `unit_select`·`drag_select`·`minimap`에 각 10초,
총 30초(상한 31.5초 이하)의 단계 예산을 넣고, 단계 진입 레코드와 tick/잔여 공용 예산을 wait
전에 flush한다. 단계 timeout은 `FAIL_NO_EFFECT`, 공용 deadline 소진은
`UNKNOWN_BUDGET_EXHAUSTED`로 기록하며 어느 경우도 PASS가 아니다. `make check` 202 passed,
runtime 대상 pytest 89 passed, Ruff/compileall/mypy/context/safety PASS, 게임 실행 0회다.

lap179 middle 독립 검수는 **A-11을 승인**했다. source SHA 2/2 MATCH, 진입 레코드의 wait 이전 flush,
`min(run_deadline, wait_started + stage_budget)` 단계 마감시한, `FAIL_NO_EFFECT`/
`UNKNOWN_BUDGET_EXHAUSTED` 분류, UNKNOWN의 PASS 비승격, 예산 합 30.0 <= 31.5, 회귀 4종,
`baseline_wait`/`candidate_wait`의 kwargs 배선, 예외 후 증거 보존을 코드로 확인했다. 무엇보다 이
세션은 `make check` **202 passed** 와 `bash checks/safety.sh check` **SAFETY_PASS** 를 직접 실행해
lap171·175·177의 **3연속 권한 SKIP을 해소**하고 1단 게이트를 처음으로 독립 재현했다.
다만 신규 카드 **A-12(Stage A3)** 를 발부한다. (F-1) 단계 예산 시계가 wait이 아니라 단계 진입에서
시작해 사전 캡처/클릭이 관측 창을 먹는데, evidence에는 여전히 `finished_elapsed: 10.0`,
`FAIL_NO_EFFECT`로만 남는다(주입 probe: 실제 관측 창 1.75초). (F-2) `T <= 31.5초`는 입력 구간
벽시계 제약인데 예산 30초는 세 wait 창만 덮고 4회 캡처와 production의 EXE 전체 해시는 밖에 있어
슬랙이 1.5초뿐이다. 두 결손 모두 PASS를 만들지는 않아 fail-closed는 유지된다.

lap180 work는 A-12(Stage A3)를 구현했다. `_wait_state`가 실제 wait 시작 시각, 유효 관측 창,
poll 수/첫·마지막 poll 시각을 단계 evidence에 남기고, 단계 진입 선행 작업으로 창이 잘리면
`UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`로 분류해 `FAIL_NO_EFFECT`와 구분한다. PS3 입력 phase는
`input_phase_elapsed`와 `selection_after`/`production_before`/`drag_after`/`minimap_after` 캡처 및
production provenance 비용을 기록하고, 31.5초 초과 시 `INPUT_PHASE_WALL_CLOCK_EXCEEDED` 원인을
남긴다. 새 회귀 포함 `make check` 204 passed, Ruff/compileall/mypy/CONTEXT_PASS,
`bash checks/safety.sh check` SAFETY_PASS; 게임 실행 0회다.

모델 라우팅은 Luna/high(work), Claude Opus5/high(middle/judge), Astra/medium(strategy)이다.
Astra는 자동/정기 호출하지 않고 큰 분기·반복 교착에서만, 대략 work/middle 10 lap당 1회 이하로
쓴다. high는 medium으로 고위험 복수 경로를 결정할 수 없을 때만 쓴다.

| 목표 | 판정 | 현재 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | 후보 2배 표시·논리 구도·입력·30초 지속 렌더 PASS; A-12 구현 및 1단 게이트 204 passed/SAFETY_PASS; middle 독립 검수 전 Stage B CLOSED; WM_CLOSE 종료 결함 |
| G2 8인 전비5000 안정성 | 미완료 | 숫자 패치 외 8인 부하·개체 풀/메모리 확장 증명 없음 |
| G3 최대16인 | 미완료 | 9~16인 로비/상태/통신/시뮬레이션 미구현 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 지표·개선 구현 없음 |

## 다음 한 가지

 middle tier가 **A-12(Stage A3)를 독립 검수**한다. source SHA, wait 관측 창/분류, phase 비용·
 31.5초 초과 원인, 새 회귀와 1단 게이트를 재현한다. 그 전까지 게임 실행/Stage B/P6는 계속 금지다.

## 지금 막힌 것 (Blockers)

- 원본/제품 EXE·DLL/assets/baseline/golden 변경 금지. 보호 EXE SHA:
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 실패 run/prefix/display/build 재사용, 임의 retry, validator/summary/exit 요구 완화 금지.
- A-12는 lap180 work에서 구현됐지만 middle 독립 검수와 승격 작업자 판단 전까지 Stage B 실제
  원본/후보 run과 P6는 시작하지 않는다. Stage B는 마일스톤 경계다.
- Stage A 내용은 lap177에서 승인됐지만 **정적 근거 한정**이다. 이를 G1 제품 승인으로 쓰지 않는다.
- **[lap179 해소됨]** 비대화형 Claude middle 세션의 게이트 권한 교착(lap171·175·177 3연속 SKIP)은
  lap179에서 풀렸다. `make check` 202 passed, `SAFETY_PASS`를 middle 세션이 직접 실행했다.
  다음 middle 바퀴에서 다시 차단되면 재발로 기록하고 `loop/ESCALATE_SOL`에 올린다.
- production 입력 효과를 관측하지 못하면 BLOCKED이며 required input 전체가 PASS일 수 없다.
- 원본/후보 동일 시작 상태는 아직 증명되지 않았다. random seed 미노출 때문에 Tier-1/Tier-2로 분리한다.
- minimap은 단순 변화가 아니라 camera 절대 목적지 비교가 필요하다.
- DxWrapper 종료 결함은 무시하지 않지만 표시 합격 증거를 막는 선행조건으로 두지 않는다.
- G1 실제 나란히 비교/입력 증거와 G2~G4 제품 증거는 아직 없다.

## 검증 상태

- lap146~166: diagnostic 종료 PASS, 후보 2배 표시·입력·30초 지속 렌더 PASS, 후보 close 후 미종료.
  Fast는 192까지 증가했고 safety/build/cleanup/config 원복 PASS.
- lap167~169: P4 독립 검수와 builtin P5 대조. P5 normal exit/summary/validator PASS로 N 확정.
- lap170 Astra: 큰 분기 검토 1회, medium. 현물 경로 오류로 직접 판정 SKIP, 코드 변경 없음.
- lap171 middle: P5 SHA 6/6 재확인, 카드2 결손과 Tier 경계 확정. 명령 검증은 권한상 SKIP.
- lap172 work: Stage A 구현, `make check` 196 passed, 정적 검사/safety PASS, 게임 run 0.
- lap173 middle: source 2/2와 범위 PASS; A-1~A-5 승인, A-6~A-9 결손으로 조건부 반려.
- lap174 work: A-6~A-8 구현 및 A-7/A-8 회귀 추가, `make check` 198 passed, Ruff/compileall/mypy/context/safety PASS, 게임 run 0; A-9 예산 판단 기록.
- lap175 middle: source SHA 2/2 MATCH, A-6·A-7·A-8 정적 승인, P5 산출물 해시 재확인(재생성 없음),
  게임 run 0. 필수 게이트 재실행은 SKIP(권한), A-9 불충분으로 A-9R 신설, off 모드 회귀 결손 A-10 신설.
- lap176 work: A-9R 세 wait의 예산/FAIL·UNKNOWN 기록 방법과 현재 한계를 문서화하고 A-10 off-mode
  회귀 추가. `make check`/pytest 각 199 passed, Ruff/compileall/mypy/context/safety/git diff check
  실제 PASS; runtime_env SHA 유지, 게임 run 0. Stage A는 middle 독립 판정 전까지 보류.
- lap177 middle: SHA 2/2 MATCH, A-9R·A-10 독립 승인 및 Stage A 내용 승인(정적). `_wait_state` 공용
  마감시한·record 이전 예외·동일 예외 메시지를 코드로 재확인, P5 evidence로 8.438/2.274/≈81.6초
  재계산, close 정체 50.04초에서 `T <= 31.5초` 파생. 필수 게이트 재실행은 SKIP(권한) 3회 연속.
  코드 변경 0, 게임 run 0. 신규 카드 A-11(Stage A2) 발부.
- lap178 work: A-11을 `tools/runtime_env.py`·`tests/test_runtime_env.py`에 구현했다. 10초×3 단계
  예산, 진입 전 flush, `FAIL_NO_EFFECT`/`UNKNOWN_BUDGET_EXHAUSTED` 구조화 및 비승격 회귀를
  확인했다. `make check` 202 passed, 대상 pytest 89 passed, Ruff/compileall/mypy/context/safety
  PASS, 게임 run 0. middle 독립 검수 전 Stage B/P6는 닫힘.
- lap179 middle: SHA 2/2 MATCH, A-11-1~A-11-4 독립 승인, 호출부 kwargs 배선/예외 후 증거 보존 확인.
  **1단 게이트 독립 재현 성공** — `make check` 202 passed(Ruff/compileall/mypy/CONTEXT_PASS),
  `bash checks/safety.sh check` SAFETY_PASS. 3연속 권한 SKIP 해소. 코드 변경 0, 게임 run 0.
  신규 카드 A-12(Stage A3) 발부: 단계 예산 시계가 wait이 아닌 단계 진입에서 시작(실측 관측 창
  1.75초 vs 기록 10.0초), `T <= 31.5초` 벽시계 슬랙 1.5초.
- lap180 work: A-12를 `tools/runtime_env.py`·`tests/test_runtime_env.py`에 구현했다. wait 실제
  관측창/poll 계측과 `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`, PS3 phase elapsed·4개 캡처·production
  provenance 비용 및 `INPUT_PHASE_WALL_CLOCK_EXCEEDED` 원인을 추가했다. `make check` 204 passed,
  Ruff/compileall/mypy/CONTEXT_PASS, safety `SAFETY_PASS`, 게임 실행 0회.
- pre-compaction snapshot SHA `25019a38502957de262dc8f2fe7ade104eedfce4c4755f11edc8ec8c44132d84`는 아래 스냅샷 헤더의 기계 산출값을 기준으로 한다.

## 바퀴 기록

- lap2~171 및 이전 STATUS 원문: `docs/history/laps/`.
- latest snapshot: `docs/history/laps/20260911_status_lap174_compaction.md`.
- lap172 work: `docs/history/laps/20260911_lap172_luna_g1_card2_stage_a.md`.
- lap173 middle: `docs/history/laps/20260911_lap173_middle_g1_card2_stage_a_review.md`.
- lap174 work: `docs/history/laps/20260911_lap174_luna_card2_stageA_repairs.md`.
- lap175 middle: `docs/history/laps/20260911_lap175_middle_card2_stageA_reverification.md`.
- lap176 work: `docs/history/laps/20260911_lap176_luna_card2_stageA_a9r_a10.md`.
- lap177 middle: `docs/history/laps/20260911_lap177_middle_card2_stageA_decision.md`.
- lap178 work: `docs/history/laps/20260911_lap178_work_g1_card2_stageA2.md`.
- lap179 middle: `docs/history/laps/20260911_lap179_middle_a11_verification.md`.
- lap180 work: `docs/history/laps/20260911_lap180_luna_g1_card2_stageA3.md`.
- current escalation: `loop/ESCALATE_SOL` (lap180 work → A-12 구현·1단 게이트 PASS, middle 독립 검수와
  Stage B 개시는 마일스톤 경계로 승격 작업자 판단 대기; 게임/Stage B/P6 금지).
- current handoff: `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`.
- model routing: `docs/history/20260911_model_routing_update.md`.
