# 2026-09-11 | lap 183 | 목표 G1 (카드2 Stage A / A-13 독립 검수)

- 실제 provider/model/effort / 지정 역할:
  Claude Code `claude-opus-5` / high / middle tier(진단·계획·컨펌). hands-on 게임 코드 수정 없음.
  work tier(lap182 Luna/high)의 A-13 결과를 독립 검수했다. 게임/Wine/Xvfb/Stage B/P6 실행 0회.

- 가설 / 사용자 관찰:
  lap181이 조건부 반려한 A-12-1의 결손(`window_truncated`가 임계값 없이 `잘림 > 0`이라
  `FAIL_NO_EFFECT`가 실제 run에서 도달 불가)이 A-13으로 실제로 수리됐는지, 그리고 A-13 카드가
  요구한 "명시적 임계값 + 산출 근거 기록 + 4개 분류 회귀 + 게이트"가 형식이 아니라
  실질로 충족됐는지 확인한다.

- 예상 PASS / FAIL 조건:
  PASS = source SHA 2/2 MATCH, 임계값이 이름 있는 모듈 상수, 임계값 이내 잘림에서
  `FAIL_NO_EFFECT` 재도달, 임계값 초과에서 `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`,
  `UNKNOWN_BUDGET_EXHAUSTED` 우선순위 유지, A-12 evidence 필드 무삭제·무개명,
  A-13 금지 항목 무변경, 전체 게이트 독립 재현.
  FAIL = PASS 완화, 분류 접힘 잔존, 금지 항목 변경, 게이트 미재현, 근거 조작.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  검수 역할이므로 코드 변경 0. 검수 대상 fingerprint를 직접 재계산해 lap182 기록과 대조:
  `tools/runtime_env.py` `b95d6f458de2e9bf25c63f106bcc300a5ee3eecdd4da6380a3f6893e76a85afe` **MATCH**;
  `tests/test_runtime_env.py` `5de92e6512f1b823157d548c4ea27d6bb35fa2e2e0e20f8c02892872f5322faf` **MATCH**.
  → source SHA **2/2 MATCH**.
  이번 바퀴 문서 변경: `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`,
  `loop/ESCALATE_SOL`, 본 lap. 모두 uncommitted(`LOOP_ALLOW_COMMITS` 미설정, 기본 0).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는
  `tools/runtime_env.py:159` `ORIGINAL_SHA256`에서 불변 확인. 후보 바이너리/baseline/golden/
  memory-map 변경 없음. 검수 probe는 synthetic monotonic clock fixture만 사용했다.
  활성 플레이어·지도·군대 fixture 없음(이번 카드의 범위 밖).

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `sha256sum tools/runtime_env.py tests/test_runtime_env.py` → 위 2/2 MATCH.
  - `make check` → **205 passed**, Ruff PASS, compileall PASS, mypy 9 files Success, `CONTEXT_PASS`, exit 0.
  - `.venv/bin/python -m pytest -q tests/test_runtime_env.py` → **92 passed**, exit 0.
  - `bash checks/safety.sh check` → **SAFETY_PASS**, exit 0.
  - 독립 경계 probe `/tmp/lap183_probe.py`(가짜 monotonic 주입, 예산 10초 / run 여유 20초):

    | 사전작업 | effective_poll_window | truncation_seconds | classification |
    |---|---|---|---|
    | 0.00초 | 10.00 | 0.000 | `FAIL_NO_EFFECT` |
    | 0.05초 | 9.95 | 0.050 | `FAIL_NO_EFFECT` |
    | 0.30초 | 9.70 | 0.300 | `FAIL_NO_EFFECT` |
    | 2.4999초 | 7.50 | 2.500(반올림) | `FAIL_NO_EFFECT` |
    | 2.5000초 | 7.50 | 2.500 | `FAIL_NO_EFFECT` |
    | 2.5001초 | 7.50 | 2.500(반올림) | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |
    | 2.75초 | 7.25 | 2.750 | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |
    | 8.00초 | 2.00 | 8.000 | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |
    | 9.90초 | 0.10 | 9.900 | `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` |

  - PNG/게임 실행 증거 없음(이번 카드의 금지 범위).

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **A-13 판정: 승인(조건부 문서 정정 1건 동반).**
  - 임계값 상수 `G1_INPUT_MAX_TRUNCATION_RATIO = 0.25`(`tools/runtime_env.py:1990`)는 이름 있는
    모듈 수준 값이다. 고정 10초 단계에서 threshold = 2.5초. A-13이 허용한 두 근거 형태 중
    **`effective_poll_window / stage_budget` 비율** 형태를 실제로 채택했다. **PASS.**
  - 죽은 분류 수리 **PASS.** 위 probe에서 0.00/0.05/0.30초 사전작업이 모두 `FAIL_NO_EFFECT`로
    복귀했다. lap181이 지적한 "9.95초 무효과와 2.00초 잘림이 같은 라벨로 접힘"은 해소됐다.
  - 임계값 경계 **PASS.** 판정은 엄격 부등호(`truncation_seconds > threshold`)이며 2.5000초는
    `FAIL_NO_EFFECT`, 2.5001초부터 UNKNOWN이다. 단조롭고 역전 없음.
  - `UNKNOWN_BUDGET_EXHAUSTED` 우선순위 **유지 PASS.** `tools/runtime_env.py:2770`에서 여전히
    최우선이며, run 예산이 더 빡빡하면 `stage_deadline == stage_started + stage_budget`이 거짓이라
    `window_truncated`가 아예 참이 될 수 없다. 이때 루프는 `run_deadline`에서 종료하므로
    `remaining <= 0`이 보장돼 BUDGET_EXHAUSTED로만 귀결된다(코드 경로로 확인).
  - evidence 필드 **PASS.** `stage`/`stage_budget`/`stage_started_elapsed`/`wait_started_elapsed`/
    `effective_poll_window`/`poll_count`/`first_poll_elapsed`/`last_poll_elapsed`/`observed_seconds`/
    `remaining_budget_after`/`window_truncated` 전부 보존, `truncation_seconds`·
    `truncation_threshold_seconds`가 추가됐다. `stage_wait`(`:2297~2303`)와
    `record_timeout`(`:2288`)이 관측 dict를 in-place로 항목 evidence에 flush하므로
    timeout·정상 양 경로에서 새 필드가 실제로 보존된다.
  - 회귀 4건 **PASS.** `tests/test_runtime_env.py:1679/1704/1728/1783`가 (a)0초→`FAIL_NO_EFFECT`,
    (b)0.3초→`FAIL_NO_EFFECT`, (c)8초→`UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`,
    (d)공용 예산 소진→`UNKNOWN_BUDGET_EXHAUSTED`를 고정한다. (b)(c)는 `!= "PASS"`를 명시하고
    (a)(d)는 등가 단언이 더 강하다. 세탁 없음은 `_g1_input_verdict`가 required 5태그 전원
    `result == "PASS"`를 요구하고 세 분류 중 어느 것도 PASS가 아니라는 점에서 유지된다.
  - A-13 금지 항목 **무변경 PASS.** `G1_INPUT_STAGE_BUDGETS` 10/10/10,
    `G1_INPUT_PHASE_WALL_CLOCK_BUDGET = 31.5`, `begin_stage`의 `stage_started`가 사전작업
    **이전** 위치(A-12 유지 결정), `ORIGINAL_SHA256` 모두 그대로다.
  - lap181의 선택적 부수 정리 **반영됨.** 중복 절 `stage_deadline - wait_started < stage_budget`은
    `stage_deadline == stage_started + stage_budget`으로 교체됐고 거동 변화는 없다
    (`min()`이 같은 피연산자를 그대로 돌려주므로 float 동등 비교가 정확하다).
  - **FAIL 1건(문서/주석, 비차단):** `tools/runtime_env.py:1987~1989` 주석이
    "the **measured** normal pre-poll work was <=0.30s (lap181)"라고 적는다. lap181 원문은 0.30초를
    **가짜 시계 probe 입력**으로 명시했고, 이 프로젝트의 실제 게임 run은 지금까지 0회이므로
    실측된 사전작업 시간은 **존재하지 않는다**. 채택된 근거 자체는 비율 형태라 A-13 요구를
    충족하지만, 주석과 lap182 기록이 synthetic probe 값을 실측으로 승격해 적었다.
    AGENTS.md "과거 증거를 현재 성공으로 자동 승격하지 않는다"에 어긋나므로 정정 카드 A-14로 넘긴다.
  - **부수 발견(증거 정밀도, 비차단):** `truncation_seconds`는 소수 3자리 반올림이라
    2.4999초와 2.5001초가 evidence에서 똑같이 `2.5`로 보이면서 `window_truncated`만 다르다.
    경계 근처 run의 evidence만 읽고는 분류 이유를 재구성할 수 없다. A-14에 함께 넘긴다.
  - 실제 게임/Stage B/P6 **SKIP**(금지·승격 전). G1 제품 판정 **미완료**. G2~G4 **미완료**.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  이번 바퀴 회귀 추가 0(검수 역할). 남은 위험: A-13 임계값 2.5초는 **설계 가정**이며 실측
  사전작업 분포로 검증된 값이 아니다. 첫 실제 run에서 사전작업이 2.5초를 넘으면 정상 run이
  통째로 UNKNOWN으로 접혀 lap181 결손이 형태만 바꿔 재발한다. Stage B 첫 run은 실제
  `truncation_seconds` 분포를 반드시 기록하고 임계값을 재평가해야 한다.
  실제 동일 장면 원본/후보 입력 비교, WM_CLOSE 종료 결함, G2~G4 증거는 전부 미검증이다.
  본 판정은 **모델 기술 컨펌**이며 사용자 마일스톤 승인이 아니다.
  `docs/feedback/APPROVALS.md`에 Stage B 사용자 승인은 여전히 없다.

- 다음 한 가지:
  work tier(Luna/high 또는 Sonnet5/high)가 A-14(주석/기록 근거 정정 + 경계 evidence 정밀도)를
  수행한다. Stage B와 P6는 사용자 승인 전까지 계속 닫는다.

- uncommitted 파일 해시 (`LOOP_ALLOW_COMMITS` 미설정, 기본 0 → 커밋 없음):
  - `docs/STATUS.md` `fe4d09816158a6fac6151299335b845319f9af2603577bada5c344c8483a4ef9`
  - `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`
    `681a59a246e192d083e3e5d829078f746f61c603c3c9a991459f06dcfc6d6bf5`
  - `loop/ESCALATE_SOL` `19c8e12c2b294fe1375c65ab397d7da32b2be43f911e602ef70ccac21e4a628b`
  - 코드 파일 2개는 검수 후에도 SHA 불변(위 2/2 MATCH와 동일)을 재확인했다.
  - 문서 변경 후 게이트 재실행: `make check` **205 passed** / `CONTEXT_PASS` / exit 0,
    `bash checks/safety.sh check` **SAFETY_PASS** / exit 0.
