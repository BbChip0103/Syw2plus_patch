# 2026-09-11 | lap 180 | 목표 G1 (카드2 Stage A3 / A-12 work)

- 실제 provider/model/effort / 지정 역할:
  Codex work tier / hands-on 구현 작업자 / high. 중간 컨펌과 Stage B 승격은 수행하지 않았다.
- 가설 / 사용자 관찰:
  A-11의 단계 timeout evidence는 단계 진입 전 캡처·클릭 소요로 실제 poll 창이 잘려도
  `FAIL_NO_EFFECT`로 기록할 수 있고, PS3 입력 phase의 31.5초 벽시계에는 네 캡처와
  production provenance 해시 비용이 빠져 있다.
- 예상 PASS / FAIL 조건:
  PASS = 실제 wait 시작·유효 창·poll 계측이 단계 evidence에 남고 잘린 창은 FAIL과 다른
  UNKNOWN으로 분류되며, 입력 phase elapsed/5개 비용 항목과 31.5초 초과 원인이 기록되고,
  모든 기존 PASS 조건이 유지된다. FAIL = 기존 verdict 완화, 관측 증거 소실, 또는 필수 게이트 실패.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA
  `8bab31311bf24a0a7286f95656bf351f42c9bf81fa83b6c71d7b2e1e79269def`;
  `tests/test_runtime_env.py` SHA
  `0c547d3044fe0d421ac47e90e9c6246f3fc64dcd55eba0b6503f426c90d83aa6`.
  기록 파일: `docs/STATUS.md`, 본 lap, `loop/ESCALATE_SOL`. 커밋 없음
  (`LOOP_ALLOW_COMMITS` 미설정); 모든 변경은 uncommitted로 보존한다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 확인.
  게임 실행 0회, Wine/Xvfb/prefix/display 0회, Stage B/P6 0회. synthetic clock/metrics
  fixture만 회귀에 사용했으며 원본/후보 바이너리·baseline/golden은 변경하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python -m pytest -q tests/test_runtime_env.py` → **91 passed**.
  - `make check` → **204 passed**, Ruff/compileall/mypy/CONTEXT_PASS.
  - `bash checks/safety.sh check` → **SAFETY_PASS**.
  - 캡처 없음(게임 미실행).
- 변경 내용:
  A-12-1: `_wait_state`가 `wait_started_elapsed`, `effective_poll_window`, poll count와
  first/last poll 시각을 기록한다. 단계 진입 작업으로 창이 잘리면
  `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`로 분류하고 PASS로 승격하지 않는다.
  A-12-2: PS3 phase가 네 캡처(`selection_after`, `production_before`, `drag_after`,
  `minimap_after`)와 production provenance 비용을 계측하고, 31.5초 초과 시
  `INPUT_PHASE_WALL_CLOCK_EXCEEDED` 구조화 원인을 남긴다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  | 항목 | 판정 | 근거 |
  |---|---|---|
  | A-12-1 wait 관측 메타데이터 | PASS | 새 회귀가 정상 FAIL 창과 2초 선행 작업으로 잘린 창을 구분 |
  | A-12-2 phase over-budget cause | PASS | synthetic 31.6초 fixture가 원인·초과량·측정 항목을 확인 |
  | 1단 기계 게이트 | PASS | `make check` 204 passed 및 `SAFETY_PASS` |
  | 실제 게임/Stage B | SKIP | 카드 금지 범위이며 middle/승격 판단 전 |
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  기존 A-1~A-11 fail-closed와 production BLOCKED 불변식은 유지된다. 실제 동일 장면
  원본/후보 입력 비교, WM_CLOSE 종료 결함, G1 제품 승인, G2~G4 증거는 미검증이다.
  다음 middle tier가 source SHA·A-12 evidence·게이트를 독립 검수해야 하며 사용자 승인은 없다.
- 다음 한 가지:
  middle tier가 A-12를 독립 검수하고, 그 뒤 승격 작업자가 Stage B 개시 여부를 마일스톤으로
  판단한다. 그 전까지 게임 실행/Stage B/P6를 시작하지 않는다.
