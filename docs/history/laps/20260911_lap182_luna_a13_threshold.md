# 2026-09-11 | lap 182 | 목표 G1 (카드2 Stage A / A-13 work)

- 실제 provider/model/effort / 지정 역할:
  Codex work tier / hands-on 구현 작업자 / high. 중간 독립 검수와 Stage B 승격은 수행하지 않았다.
- 가설 / 사용자 관찰:
  A-12의 `window_truncated = 잘림 > 0`은 `begin_stage`의 사전작업이 항상 양수인 실제 run에서
  `FAIL_NO_EFFECT`를 죽은 분류로 만들었다. 고정 10초 단계에서 정상적인 소량 사전작업과
  관측창이 실제로 짧은 경우를 구분해야 한다.
- 예상 PASS / FAIL 조건:
  PASS = 이름 있는 근거 기반 임계값, 실제 잘림량 evidence, 0/소량 잘림의 `FAIL_NO_EFFECT`,
  큰 잘림의 `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`, 공용 예산 소진의 기존 UNKNOWN 우선순위,
  네 분류 회귀와 전체 Fast/safety 게이트 통과. FAIL = PASS 완화, 기존 evidence 삭제/개명,
  예산 우선순위 변경, 필수 게이트 실패.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA `b95d6f458de2e9bf25c63f106bcc300a5ee3eecdd4da6380a3f6893e76a85afe`;
  `tests/test_runtime_env.py` SHA `5de92e6512f1b823157d548c4ea27d6bb35fa2e2e0e20f8c02892872f5322faf`.
  문서 기록은 `docs/STATUS.md`, `loop/ESCALATE_SOL`, 본 lap이며 모두 uncommitted다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
  코드 회귀는 synthetic monotonic clock fixture만 사용했다. 게임/Wine/Xvfb/prefix/display 0회;
  활성 플레이어·지도·군대 fixture 없음. 원본/후보 바이너리·baseline/golden/memory-map 변경 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'wait_state or input_stage_flushes_entry'`
    → **6 passed**.
  - `make check` → **205 passed**, Ruff PASS, compileall PASS, mypy 9 files Success, `CONTEXT_PASS`.
  - `.venv/bin/python -m pytest -q tests/test_runtime_env.py` → **92 passed**.
  - `bash checks/safety.sh check` → **SAFETY_PASS**; `git diff --check` PASS.
  - PNG/게임 실행 증거 없음(이번 카드의 금지 범위).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - `G1_INPUT_MAX_TRUNCATION_RATIO = 0.25`; fixed stage budget 10.0초에서 threshold 2.5초.
  - lap181의 정상 사전작업 관측 상한 0.30초보다 넉넉하고, 8초 사전작업의 2초 유효창은
    threshold를 크게 넘는다. 구현은 `truncation_seconds > threshold`일 때만 `window_truncated`다.
  - 0.0초 잘림 → `FAIL_NO_EFFECT` **PASS**; 0.3초 → `FAIL_NO_EFFECT` **PASS**;
    8.0초 → `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED` **PASS**;
    공용 1초 deadline 소진 → `UNKNOWN_BUDGET_EXHAUSTED` **PASS**. 네 분류 모두 overall PASS가 아님.
  - A-13 코드/회귀 **PASS**; 1단 기계 게이트 **PASS**; 실제 게임/Stage B/P6 **SKIP**(금지·승격 전).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  A-12의 `effective_poll_window`, `poll_count`, `observed_seconds`, `window_truncated`는 유지했고
  `truncation_seconds`·`truncation_threshold_seconds`를 추가했다. `UNKNOWN_BUDGET_EXHAUSTED`는
  여전히 classification 우선순위가 가장 높다. 실제 동일 장면 원본/후보 입력 비교, WM_CLOSE 수리,
  G1 제품 승인, G2~G4 증거는 미검증이다. 다음 middle 세션의 독립 검수와 사용자 Stage B 승인이 없다.
- 다음 한 가지:
  middle tier가 A-13 source SHA·임계값 근거·4개 회귀·전체 게이트를 독립 검수한다. 그 전까지
  Stage B와 P6를 실행하지 않는다.

## A-14 provenance 정정 (lap184 work)

위 기록의 "lap181의 정상 사전작업 관측 상한 0.30초" 문장은 실측을 뜻하지 않는다.
lap181의 0.30초는 실제 게임 실행이 아닌 가짜 시계 회귀 probe의 입력값이었고, 이 프로젝트는
현재까지 실제 게임 run이 0회이므로 사전작업 시간 분포는 **미측정**이다. 실제 채택 근거는
`effective_poll_window / stage_budget >= 0.75`라는 설계 가정이며, `0.25` 값은 변경하지 않았다.
첫 Stage B 실제 run에서 분포를 기록하고 임계값을 재평가해야 한다.

같은 lap의 원래 수치·판정은 provenance 보존을 위해 유지한다. A-14 구현은 timeout evidence에
`truncation_ratio`(9자리), `truncation_threshold_ratio`, `truncation_exceeds_threshold`를
추가해 기존 3자리 `truncation_seconds`만으로는 구분되지 않던 2.4999초/2.5001초 경계를
재구성할 수 있게 했다. 기존 필드·분류 우선순위·값은 유지했다.
