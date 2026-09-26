# 2026-09-12 | lap 197 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 지정 work; Codex `gpt-5.6-luna`/high 설정. hands-on 하네스 구현.
- 가설 / 사용자 관찰: N1이 provenance 진단을 기존 top-level `error`에 승격했으므로, evidence만 읽는
  소비자가 비치명 진단을 fatal 중단으로 오독할 수 있다. 기존 `error` 호환성과 판정식은 유지해야 한다.
- 예상 PASS / FAIL 조건: provenance 입력이 있으면 `production_provenance_error`가 top-level에 기록되고,
  fatal-only evidence에는 그 필드가 생기지 않으며, 기존 `error`와 `overall` 계산은 변하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA256 `fd28e3a1aab1d4be65beeb18ba09f01a2ae3a72cc229c8db1f9ab6b66d73a92f`,
  `tests/test_runtime_env.py` SHA256 `9082d1567b46a83e4e7c1ff74ccdd295a48cf79687f50be23a6da3bfd0cf536f`.
  N3 implementation and tests are uncommitted; `LOOP_ALLOW_COMMITS=0`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE/DLL/assets/
  baseline/golden 무변경. 게임 run 0회, Stage B 재실행 0회, R5 0회, PNG 0장. fixture는 tmpdir의
  synthetic input/evidence dictionaries이며 활성 플레이어·지도·군대는 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: targeted
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_flush_input_stage or g1_presentation_verdict or g1_input_verdict'`
  → **7 passed**; `make check` → **213 passed / exit 0**, Ruff·compileall·mypy(9 files)·`CONTEXT_PASS`;
  `bash checks/safety.sh check` → **SAFETY_PASS / exit 0**. 새 게임 로그/캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **N3 구현 PASS (1단).** 비치명 production provenance는
  기존 `evidence["error"]`를 유지하면서 `evidence["production_provenance_error"]`에 구조화 보존한다.
  provenance가 없는 fatal-only flush에는 새 표식이 생기지 않는다. fatal `error`는 verdict에서 그대로
  유지되고 모든 입력이 PASS여도 `overall`은 PASS가 되지 않는다. `required_inputs`/`overall` 계산식,
  production 클릭 차단, R5 술어는 변경하지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted/Fast/safety는 PASS. 다음 middle이 실제
  flush와 fatal/비치명 경로를 독립 검수해야 한다. G1 실제 원본/후보 비교, WM_CLOSE, random seed,
  minimap 절대 목적지, G2~G4 제품 증거는 미검증. R5와 승인 소진된 Stage B 재실행은 새 사용자 승인 필요.
- 다음 한 가지: 다음 middle이 N3와 N1/N2/R1~R4를 독립 검수한 뒤, 별도로 새 사용자 승인 여부를 확인한다.
