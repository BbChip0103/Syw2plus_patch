# 2026-09-12 | lap 215 | 목표 G1 — F6 producer 회귀 가드

- 실제 provider/model/effort / 지정 역할: Codex work tier (`gpt-5.6-luna`/high), hands-on 구현 작업자.
- 가설 / 사용자 관찰: 공용 `_g1_record_selector_input()` 테스트만으로는 실제 원본/후보 producer
  closure가 helper를 우회해 untagged `OBSERVED` 레코드를 만들도록 되돌아가도 통과한다. 양쪽
  selector producer의 recorder wiring을 직접 고정하면 F6 비대칭 회귀를 기계적으로 잡을 수 있다.
- 예상 PASS / FAIL 조건: `g1_baseline`의 `input_record`와 `g1_presentation_trace`의
  `record_input`이 각각 `_g1_record_selector_input()`을 호출하고 `_g1_selector_flow`에 전달되며,
  recorder 본문에 과거 untagged `OBSERVED` stub이 없으면 PASS. 어느 producer라도 우회하면 FAIL.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tests/test_runtime_env.py`만 변경. `tools/runtime_env.py` 및 comparator는 변경 0.
  `tests/test_runtime_env.py` sha256
  `601ebfc821cf98804741c07bc07780019708d799632ab9a839947f75ea010528`.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회, PNG 0장,
  Wine/Xvfb 미사용, 원본·후보 바이너리/보존 evidence/baseline/golden 변경 0.
  fixture는 AST로 실제 `g1_baseline`/`g1_presentation_trace` 소스의 중첩 recorder와
  `_g1_selector_flow` 연결을 검사하며 플레이어·지도·군대는 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `pytest -q tests/test_runtime_env.py -k 'selector_producers_guard_against_untagged_recorder_regression or selector_flow or selector_input_recorder'`
  → `6 passed, 105 deselected`.
  `make check` → `234 passed in 39.22s`, Ruff PASS, compileall PASS, mypy Success(10 files),
  `CONTEXT_PASS`. `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`.
  새 실행/캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): F6-R1 기계 가드 **PASS**. 두 실제 producer의
  recorder 정의가 tagged helper를 정확히 한 번 호출하고, selector flow 인자로 연결되며,
  `OBSERVED` stub 문자열이 없는 조건을 각각 통과했다. 전체 Fast도 PASS.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 F6 구현과 좌표·예산·comparator 판정은
  변경하지 않았다. 다음 middle이 새 테스트가 producer 우회 회귀를 실제로 차단하는지 독립 검수해야
  하며, 이번 결과는 F6-R1 한정 기술 검증이지 제품 G1 PASS나 마일스톤 사용자 승인이 아니다.
  S1 장면 통제 차단으로 Stage B 후보/원본 재실행은 계속 금지한다.
- 다음 한 가지: 다음 work 바퀴는 승인된 범위 안의 `F3 comparator 수리`이며, F2 identity/R6-B
  런타임 술어 변경과 S1 재결·게임 실행은 이 바퀴에서 하지 않는다.
