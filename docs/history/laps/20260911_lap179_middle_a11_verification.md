# 2026-09-11 | lap179 | 목표 G1 (카드2 Stage A2 / A-11 독립 검수)

- 실제 provider/model/effort / 지정 역할:
  Claude Code `claude-opus-5` / high / **middle tier(진단·계획·확인)**. 게임 코드 hands-on 수정 없음.

- 가설 / 사용자 관찰:
  lap178 work가 구현한 A-11(Stage A2)이 A-11-1~A-11-4를 실제로 만족하는지, 그리고
  lap171·175·177에서 3회 연속 SKIP이던 1단 게이트를 이 세션이 독립 재현할 수 있는지.

- 예상 PASS / FAIL 조건:
  PASS = (a) source SHA 2/2 MATCH, (b) 진입 레코드가 wait 이전에 flush, (c) 단계 마감시한과
  `FAIL_NO_EFFECT`/`UNKNOWN_BUDGET_EXHAUSTED` 분류가 코드에 실재, (d) UNKNOWN이 PASS로 승격되지
  않음, (e) 단계 예산 합 <= 31.5초, (f) 네 회귀 존재, (g) 1단 게이트 독립 재현.
  FAIL = 위 중 하나라도 결손이거나 PASS 조건이 완화됨.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  이번 바퀴 코드/테스트/바이너리 변경 **0**. 문서만 갱신했다(STATUS, 본 lap 기록, ESCALATE_SOL,
  카드 A-12 추가). 커밋 없음(`LOOP_ALLOW_COMMITS` 미설정, uncommitted 보존).
  검수 대상 fingerprint(lap178 handoff와 2/2 MATCH):
  - `tools/runtime_env.py` `5b56e9085dd92b2d96ed787be438d162f722b2d8c7017af82524023b4b740509`
  - `tests/test_runtime_env.py` `ebc38c0bbbaad2e567ef121efd1358ea03aec94ee9be99c32221ce022a496fca`

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  해당 없음 — **게임 실행 0회**. Wine/Xvfb/prefix/display 미사용, Stage B·P6 미개시.
  보호 EXE SHA `b56986e0…c9c08a8ac`는 변경하지 않았고 재생성한 산출물도 없다.

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `sha256sum tools/runtime_env.py tests/test_runtime_env.py` → 2/2 MATCH
  - `make check` → **202 passed** (pytest 35.20s), Ruff `All checks passed`, compileall OK,
    mypy `Success: no issues found in 9 source files`, `CONTEXT_PASS`
  - `bash checks/safety.sh check` → **SAFETY_PASS**
  - 1회성 인메모리 probe(게임 무관, `_wait_state` 단독 호출, 아래 F-1 근거)
  캡처 없음(게임 미실행).

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):

  | 항목 | 판정 | 근거 |
  |---|---|---|
  | source SHA 2/2 | PASS | 위 해시가 lap178 handoff와 일치 |
  | A-11-1 진입 전 flush | PASS | `begin_stage`(`:2196~2210`)가 entry append 후 `flush()`; click/wait보다 앞섬. 회귀 `flushes[0] == ["unit_select"]`(tests:1731) |
  | A-11-2 단계 마감시한/분류 | PASS | `_wait_state`(`:2616~2655`) `stage_deadline = min(run_deadline, wait_started + stage_budget)`; `remaining <= 0 → UNKNOWN_BUDGET_EXHAUSTED`, 아니면 `FAIL_NO_EFFECT`(`:2645~2648`); `_G1WaitTimeout`(`:249`)이 classification/last/finished_elapsed/remaining_budget_after/predicate_observed 운반 |
  | A-11-2 UNKNOWN 비승격 | PASS | `_g1_input_verdict`(`:2008~2015`)가 required tag 전원 `result == "PASS"` 요구 → UNKNOWN/FAIL은 `required_inputs=False`; `_g1_presentation_verdict`(`:2039~2041`)가 이를 overall에 AND 결합. 회귀 tests:1737~1749가 `overall != "PASS"` 단언 |
  | A-11-3 예산 상한 | PASS | `G1_INPUT_STAGE_BUDGETS` 10/10/10 = 30.0 <= 31.5; 초과 시 import 시점에 `RuntimeSafetyError`(`:1986`). `--timeout` 미변경 |
  | A-11-4 회귀 4종 | PASS | tests:1673(FAIL_NO_EFFECT), :1691(UNKNOWN), :1709(진입 flush + UNKNOWN 비승격), A-10 off-mode(:1265~1288) 유지 |
  | 호출부 배선 | PASS | `baseline_wait`(`:2954`)·`candidate_wait`(`:3307`) 모두 `**kwargs` 전달. kwargs 미전달 `wait_selector`(`:2832`,`:3202`)는 selector flow 전용이며 입력 시퀀스에 쓰이지 않음 |
  | 예외 후 증거 보존 | PASS | `record_timeout`이 `record()`→`flush()` 후 재raise; `_G1WaitTimeout`은 `RuntimeSafetyError` 하위라 `:3345` except가 잡아 `evidence["error"]`로 기록, `evidence["inputs"]`는 같은 list 객체라 보존 |
  | **1단 게이트 독립 재현** | **PASS** | `make check` 202 passed + `SAFETY_PASS`를 이 세션이 직접 실행. lap171·175·177의 3연속 권한 SKIP **해소** |
  | Stage B 개시 | 보류 | 마일스톤 경계 — 아래 F-1/F-2와 ESCALATE 참조 |

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:

  **F-1 (신규, 실측 확인). 단계 예산 시계가 wait이 아니라 단계 진입에서 시작한다.**
  `begin_stage`의 `stage_started`는 `read_camera`/`read_selection`/`capture(...)`/`click(...)`보다
  **앞서** 찍히고, 그대로 `stage_wait → _wait_state(stage_started=...)`로 전달된다
  (`:2233~2236`, `:2630~2634`). 따라서 predicate 실제 polling 창 = 10초 − 진입 후 사전작업 시간이다.
  probe 결과(monotonic 주입, 사전작업 8초 가정): polling 창 `1.75초`, poll 8회인데도 evidence에는
  `finished_elapsed: 10.0`, `classification: FAIL_NO_EFFECT`로 남는다. 즉 **"10초 동안 효과 없음"과
  "사전작업이 예산을 먹어 2초만 관측함"이 현재 필드로 구분되지 않는다.** 진입 레코드에는
  `entered_elapsed`/`remaining_budget_before`/`stage_budget`만 있고 wait 실제 시작 시각 필드가 없다.
  이는 A-11이 제거하려던 모호성(같은 메시지로 두 원인)과 동일 계열의 잔존 결손이다.
  단, 어떤 경우에도 PASS를 만들지 않으므로 **fail-closed는 유지**된다.

  **F-2 (신규, 정적). `T <= 31.5초` 제약은 벽시계 기준인데 구현은 세 wait 창만 묶는다.**
  lap177 유도식 `8.438 + T + 50.04 <= 90`의 T는 PS3 입력 구간 **전체 소요**다. 현재 예산 30초는
  세 단계의 (사전작업+wait)만 덮고, 그 바깥의 `selection_after`·`production_before`·`drag_after`·
  `minimap_after` **4회 scrot 캡처**와 `production` 단계의 `read_production_cell →
  _read_g1_command_cell_provenance(..., _sha256(game/ORIGINAL_EXE))`(**EXE 전체 해시**)는 예산 밖이다.
  남은 슬랙은 `31.5 - 30 = 1.5초`뿐이다. 세 wait이 각각 예산 근처까지 쓰고도 성공하는 "느린 PASS"
  런에서는 입력 구간이 31.5초를 넘겨 close 정체 `50.04초` 관측이 공용 90초에서 잘릴 수 있다.
  (세 단계가 모두 timeout되는 최악은 첫 timeout에서 즉시 raise되므로 발생하지 않는다.)

  **기존 위험 유지:** `menu` 단계 wait(`:2723`, `:3239` 계열)은 단계 예산 없이 공용 마감시한만
  쓴다. PS3 이전 구간이라 A-11 범위 밖이지만, 여기서 정체하면 여전히 전체 예산을 소모한다.

  독립 검수 상태: **A-11 구현은 이 lap에서 middle tier 독립 승인**(정적 코드 + 1단 게이트 실행 재현).
  Stage A 내용 승인(lap177)은 유지되나 여전히 **정적 근거 한정**이며 G1 제품 승인이 아니다.
  사용자 마일스톤 승인은 **여전히 없음**(APPROVALS "확정" 비어 있음).

- 다음 한 가지:
  work tier가 **A-12**(F-1 evidence 필드 + F-2 입력 구간 벽시계 계측)를 구현한다.
  카드 본문은 `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md` lap179 절.
  Stage B 실제 원본/후보 run과 P6는 **A-12 착지와 승격 작업자 판단 전까지 계속 닫힘**.
