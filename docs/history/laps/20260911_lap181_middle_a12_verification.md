# 2026-09-11 | lap 181 | 목표 G1 (카드2 Stage A / A-12 독립 검수)

- 실제 provider/model/effort / 지정 역할:
  Claude Code `claude-opus-5` / high / `LOOP_PERMISSION_MODE=auto`.
  지정 역할 = middle tier(진단·계획·확인). 게임 코드 hands-on 수정 없음, 게임 실행 0회.

- 가설 / 사용자 관찰:
  lap180 work가 보고한 A-12-1(관측창 노출·분류)과 A-12-2(입력 phase 벽시계)가
  카드 요구를 실제로 충족하는가. exit 0과 lap180 자기보고는 승인 근거가 아니다.

- 예상 PASS / FAIL 조건:
  PASS = (a) source SHA 2/2 MATCH, (b) 1단 게이트 수치 독립 재현,
  (c) A-12-1 네 요구(관측창 필드, poll 계측, **임계값+근거 기록한 별도 분류**, 회귀)와
  A-12-2 네 요구가 코드/회귀로 확인, (d) PASS 조건 완화 0.
  FAIL = 어느 하나라도 미충족. 수리는 하지 않고 좁은 카드로 승격한다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  검수 대상(무변경): `tools/runtime_env.py`
  `8bab31311bf24a0a7286f95656bf351f42c9bf81fa83b6c71d7b2e1e79269def` (lap180 보고와 MATCH)
  `tests/test_runtime_env.py`
  `0c547d3044fe0d421ac47e90e9c6246f3fc64dcd55eba0b6503f426c90d83aa6` (MATCH)
  이번 바퀴 변경: `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(A-13 발부),
  본 기록, `loop/ESCALATE_SOL`. 전부 uncommitted (`LOOP_ALLOW_COMMITS` 미설정, 기본 0).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
  Wine/Xvfb/prefix/display 생성 0, 후보 run 0, 플레이어/지도/군대 fixture 해당 없음(정적 검수).

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `sha256sum tools/runtime_env.py tests/test_runtime_env.py`
  `make check` → `/tmp/lap181_makecheck.log`
  `bash checks/safety.sh check`
  `.venv/bin/python checks/context_limits.py`
  `_wait_state` 분류 probe(가짜 시계, 게임 무관, /tmp 밖 파일 생성 없음).
  캡처(PNG) 0장 — 게임을 실행하지 않았다.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - `make check` **204 passed**, Ruff PASS, compileall PASS, mypy 9 files Success, **CONTEXT_PASS**.
  - runtime pytest **91** (`tests/test_runtime_env.py` 46+45) — lap180 수치와 일치.
  - `bash checks/safety.sh check` → **SAFETY_PASS**.
  - source SHA **2/2 MATCH**.
  - **A-12-2 = PASS.** `_g1_measure_phase_item`(`tools/runtime_env.py:2038`)가 4회 캡처
    (`G1_PHASE_CAPTURE_TAGS`)와 `production_provenance`를 개별 계측하고,
    `_g1_finalize_input_phase`(`:2063`)가 `input_phase_elapsed`·`budget_status`·
    `over_budget_cause{kind=INPUT_PHASE_WALL_CLOCK_EXCEEDED, excess_seconds, measured_items}`를
    남긴다. baseline(`:3071/3101/3140`)과 후보(`:3447/3481/3533`) 양쪽에서 정상·예외·cleanup
    3경로 모두 finalize한다. 회귀 `test_g1_input_phase_over_budget_has_structured_cause`.
  - **A-12-1 = 조건부 FAIL(반려).** 네 요구 중 셋은 충족한다:
    `wait_started_elapsed`/`effective_poll_window`/`poll_count`/`first_poll_elapsed`/
    `last_poll_elapsed`/`observed_seconds`/`remaining_budget_after`가 기록되고, 정상 대 잘림
    회귀 2건이 있다. **미충족은 세 번째 요구**다 — "유효 관측 창이 단계 예산 대비 지나치게
    짧으면(임계값은 구현자가 정하되 **근거를 기록**) 별도 원인으로 분류한다".
    `_wait_state`(`:2707~2713`)의 `window_truncated`는 임계값 없이 **잘림 > 0**이면 참이다.
    `begin_stage`(`:2252`)가 `stage_started`를 `read_camera`/`read_selection`/`capture`/`click`
    **이전에** 찍으므로 실제 run에서는 `wait_started > stage_started`가 **항상** 성립한다.
    가짜 시계 probe(예산 10초, run 여유 충분):
      사전작업 0.00초 → `FAIL_NO_EFFECT`, window 10.0
      사전작업 0.05초 → `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`, window 9.95
      사전작업 0.30초 → `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`, window 9.70
      사전작업 8.00초 → `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`, window 2.00
    ⇒ `FAIL_NO_EFFECT`는 실제 run에서 **도달 불가한 죽은 분류**이고, A-12-1이 없애려던 접힘
    ("10초 무효과"와 "2초만 봤음"이 구분되지 않는다)이 **반대 방향으로 재현**된다.
    Stage B 영향: L171-4의 "무반응 배제"가 무효과를 FAIL로 기록할 수 없고 전부 UNKNOWN이 되어,
    후보 결함과 관측 부족을 분리하지 못한 채 무한 재시도를 부른다.
  - **세탁 없음(확인됨).** `_g1_input_verdict`(`:1996`)는 required 5태그 전원 `result == "PASS"`를
    요구하고, 세 분류 중 어느 것도 `PASS`가 아니다. `_g1_presentation_verdict`(`:2085`)의
    overall도 `required_inputs`를 그대로 쓴다. 즉 이번 결손은 **PASS 완화가 아니라 FAIL 소실**이다.
  - **부수 발견(코드, 비차단):** `window_truncated`의 `stage_deadline - wait_started < stage_budget`
    절은 앞선 두 절에 의해 항상 참인 중복 조건이다.
  - **부수 발견(문서, 수리함):** lap181 이전 STATUS는 "단계 예산 시계는 실제 입력 주입 직전에
    시작하며 각 wait는 9초, 합계 27초"라고 적었다. 코드는 `begin_stage` 시작이고
    `G1_INPUT_STAGE_BUDGETS`는 10/10/10 = **30초**(상한 31.5초)다. lap180 원기록에는 이 문장이
    없으므로 STATUS 전사 오류다. 또 STATUS의 lap180 기록 경로 `..._stage_a3.md`는 실재하지 않고
    실제 파일은 `..._stageA3.md`다(lap170과 같은 종류의 경로 오기). 둘 다 이번 바퀴에 정정했다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  회귀 추가 0(검수 역할). 남은 위험: A-13 수리 전에는 Stage B의 무반응 판정이 성립하지 않는다.
  Stage B는 첫 실제 원본/후보 게임 run이며 **마일스톤 경계**다. `docs/feedback/APPROVALS.md`에
  사용자 승인은 여전히 없다. G1 실제 나란히 비교, WM_CLOSE 종료 결함, G2~G4는 전부 미충족이다.
  본 판정은 모델 기술 컨펌이며 사용자 마일스톤 승인이 아니다.

- 다음 한 가지:
  work tier(Luna/high 또는 Sonnet5/high)가 카드 **A-13**을 구현한다 —
  `_wait_state`의 잘림 분류에 근거를 기록한 임계값을 도입해 `FAIL_NO_EFFECT`를 실제 run에서
  도달 가능하게 만든다. 게임 실행·Stage B·P6는 계속 금지.
