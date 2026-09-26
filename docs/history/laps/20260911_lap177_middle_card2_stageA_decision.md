# 2026-09-11 | lap 177 | 목표 G1 (카드2 Stage A 독립 판정)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` 비대화형 세션 /
  middle tier(진단·계획·확인). 구현은 하지 않았다. 지정 middle route와 일치한다.
- 가설 / 사용자 관찰: lap176 work의 A-9R 기록과 A-10 회귀가 lap175 middle이 건 두 조건을
  충족하는가, 그리고 1단 게이트를 이 세션이 독립 재현할 수 있는가.
- 예상 PASS / FAIL 조건: (1) A-9R이 PS3 이후 **세 개의 실제 wait** 기준으로 진입/종료 시각과
  잔여 예산, FAIL·UNKNOWN 분리 방법을 명시하면 PASS. (2) A-10이 off-mode에서 production
  `BLOCKED` 입력 목록에 대해 `required_inputs=True`와 기존 overall을 고정하면 PASS.
  (3) `make check`/`pytest`/`safety.sh`를 이 세션이 실제로 재실행하면 게이트 조건 PASS,
  실행 불가면 SKIP(권한)이며 lap176 수치를 독립 검수로 승격하지 않는다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/STATUS.md`, `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, 본 기록,
  `loop/ESCALATE_SOL`. 코드/테스트/바이너리 변경 0건. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
  검수 대상 SHA는 lap176 기록과 **2/2 MATCH**:
  - `tools/runtime_env.py` `8893761db973cbb0dab5fdee0a1a26cc3bf7c9f5db1324c4ec9641f1d41bdc9c`
    (lap176 기록은 마지막 한 글자가 잘린 63자 표기였다. 앞 63자는 일치하며 실제 값은 위와 같다.)
  - `tests/test_runtime_env.py` `ab523a67e0f9e97c524e03fddb6b600985e43ca0b1da9ce3153a4c804c565762`
  - lap174→lap176 사이 `tools/runtime_env.py`는 변경되지 않았다(lap175 기록과 동일 SHA).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 바이너리 변경 없음.
  게임 실행 0회, Stage B 0회, P6 0회. 활성 플레이어·지도·군대 N/A.
  타이밍 재계산의 fixture는 기존 lap168 P5 산출물
  `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json`(재생성 없음).

- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `sha256sum tools/runtime_env.py tests/test_runtime_env.py` → 위 2/2 MATCH.
  - `grep`/`Read`로 `_wait_state`(`:2502`), `_g1_run_input_sequence`(`:2131`),
    `_g1_input_verdict`(`:1967`), `_g1_presentation_verdict`(`:2009`), `_g1_baseline_verdict`(`:2041`),
    후보 호출부(`:3147~3178`), A-10 테스트(`tests:1265~1288`) 정적 검증.
  - `grep -o '"elapsed_seconds":...' <P5 evidence>` → dwell 표본 `1.0…30.0`, 이후 `0.082`,
    `38.438`, `39.44`, `40.445`, `40.712`.
  - **차단됨(SKIP 권한):** `make check`, `.venv/bin/python -m pytest -q`,
    `bash checks/safety.sh check`, 인라인 `python3 -c` 모두 "requires approval"로 거부됐다.
    우회 실행은 시도하지 않았다. 새 캡처·게임 로그 없음.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **A-9R PASS(독립 확인).** lap176이 주장한 세 구조적 사실을 코드로 직접 재확인했다.
    (1) `_wait_state:2502~2513`은 `started + timeout` **공용 마감시한만** 가지며 0.25초 폴링 후
    `:2513`에서 예외를 던진다. 후보 `candidate_wait:3162~3163`과 baseline `:2811`이 모두 같은
    `started`/`timeout`을 넘긴다 ⇒ 단계별 예산은 존재하지 않는다.
    (2) `_g1_run_input_sequence`에서 `wait(...)`는 `:2162`/`:2211`/`:2241`이고 대응 `record(...)`는
    `:2171`/`:2220`/`:2250`이다. 즉 wait 예외는 **`record()`/`flush()` 이전에** 발생해 해당 단계와
    이후 단계 증거를 통째로 잃는다.
    (3) `:2513`의 메시지는 "효과 없음"과 "예산 소진"이 **동일 문자열**이고 `last=` 관측만 덧붙는다
    ⇒ FAIL과 UNKNOWN을 기계적으로 분리할 수 없다.
    production은 wait에 들어가지 않는다(`:2190~2204`, `waited=False`) — L171-1 유지 확인.
  - **예산 산술 독립 재계산 PASS.** P5 evidence의 dwell 표본이 `30.0`에서 끝나고 그 직후 run 표본이
    `38.438`이므로 기동→PS3 `38.438 - 30 = 8.438초`, close+finalization `40.712 - 38.438 = 2.274초`다.
    lap175의 ≈8.4초/≈2.3초와 일치한다. `timeout=90`, dwell 0 ⇒ PS3 이후 가용 예산
    `90 - 8.438 ≈ 81.6초`가 세 입력 wait와 close/finalization 전체에 공유된다.
  - **파생 상한(이번 바퀴 신규).** lap166 후보 close 정체는 50.04초다. 정체 구간을 자르지 않으려면
    입력 전체 소요 `T`가 `8.438 + T + 50.04 <= 90` ⇒ **`T <= 31.5초`** 여야 한다.
    A-9R의 "입력이 약 30초를 넘기면 close-stall 관측이 잘린다"는 서술은 이 수치로 뒷받침된다.
  - **A-10 PASS.** `tests:1265~1288`은 `G1_REQUIRED_INPUT_TAGS` 5개 중 production만 `BLOCKED`인
    목록에 대해 `enabled=False`에서 `required_inputs is True`, `production_blocked is True`,
    baseline overall `PASS`, 후보 `checks["required_inputs"] is True`·overall `PASS`,
    `production.blocked is True`를 단언한다. `_g1_input_verdict:1990~1995`의 `not enabled or (…)`
    결합과 일치하며, on-mode 대조 케이스(`tests:1224`, `:1251`)가 이미 있어 공허하지 않다.
  - **1단 게이트 독립 재현 SKIP(권한) — 3회 연속(lap171, lap175, lap177).** lap176의
    `199 passed`/`SAFETY_PASS`는 독립 검수 결과로 승격하지 않는다.
  - **범위 준수 PASS.** lap176은 `tests/test_runtime_env.py`와 문서만 바꿨고 `tools/runtime_env.py`
    SHA는 유지됐다. 게임 실행/Stage B/P6/커밋 0건.

- 판정 결론:
  - **Stage A 내용 승인(GRANTED).** A-1~A-5(lap173) · A-6~A-8(lap175) · A-9R·A-10(이번 바퀴)로
    카드2 Stage A의 요구 항목은 모두 충족됐다. 이 승인은 **정적 코드 근거**에 한한다.
  - **Stage A 게이트 재현 조건 UNMET.** 환경 권한 문제이며 work tier의 결함이 아니다.
  - **Stage B는 여전히 CLOSED.** 게이트 재현과 무관하게, A-9R이 드러낸 단계별 예산 부재가
    독립적인 기술 선행조건이다. 신규 카드 **A-11(Stage A2)**로 카드에 기록했다.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: A-1~A-10 승인 유지. G1 실제 원본/후보 입력
  parity, Tier-2 동일 장면, WM_CLOSE 종료 결함, production mapping, G2~G4, 사용자 마일스톤 승인은
  모두 미검증이다. 이 세션은 게이트를 실행하지 못했으므로 1단 결과는 여전히 work tier 수치뿐이다.

- 다음 한 가지: work tier가 **A-11(Stage A2)** 을 구현한다 — 세 입력 단계에 단계별 마감시한 또는
  동등한 구조화 timeout 원인을 넣고, 단계 진입 직전/종료 직후 예산 레코드를 즉시 flush해
  `FAIL_NO_EFFECT`와 `UNKNOWN_BUDGET_EXHAUSTED`를 분리한다. 게임 실행/Stage B/P6는 계속 금지다.
