# 2026-09-11 | lap 119 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna`/high 실무 작업자. lap118 Sol의
  `docs/plans/20260911_lap118_g1_trace_regression_handoff.md` 범위만 구현했으며 새 게임/runtime은
  실행하지 않았다.
- 가설 / 사용자 관찰: surface 재사용 계약은 각 identity·clone-vtable·wrapper·original-pointer
  조건을 하나라도 잃으면 회귀되어야 하고, runner는 owned close → process exit → bridge final
  summary 관측 뒤에만 trace copy와 validator를 수행해야 한다.
- 예상 PASS / FAIL 조건: 실행 가능한 finalization pipeline이 성공 시 정확한 순서를 관측하고,
  summary 0/2·비최종 summary·미종료 process에서는 validator 미호출과 raw 보존으로 fail-closed해야
  한다. surface 계약의 단일 조건 mutation은 테스트에서 검출되어야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py=26028b0ab7d45cd601dedc879dbec206f981ad8ed99612b06e51b3f0346e6733`,
  `tests/test_runtime_env.py=9fc7e9f38a8edc0deb8e8818f8d686ad1fe3ea24a303edea4ab6f13caaf96a27`,
  `tests/test_direct_draw_abi.py=23ba3bb35d89a0c0dc31148f1af8cc365b2c4b2f045b54efe92f0ef6b638ffe0`.
  `tools/inmm_stub/direct_draw_trace.c=2b0bd730...`는 변경하지 않았다. 커밋 없음
  (`LOOP_ALLOW_COMMITS=0`), 기존 uncommitted 작업공간에 보존했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `make doctor` original
  `verified`. 제품 후보·게임 실행·활성 플레이어·지도·군대는 SKIP/N/A. 저장소 밖 fresh
  diagnostic bridge build fixture만 사용했고 DLL SHA는
  `e4e10cba278256d4e9d5ac5cae66674d805460f8799d8a193561361795f501a2`다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python -m pytest -q
  tests/test_direct_draw_abi.py tests/test_runtime_env.py tests/test_g1_presentation_trace.py`
  (90 passed); `.venv/bin/python patches/population/build_runtime_bridge.py --out-dir
  /tmp/syw2_g1_lap119_bridge.QVkZeE/bridge`; `make doctor`; `make check` (177 passed,
  Ruff/compileall/mypy/context PASS); `bash checks/safety.sh check` (`SAFETY_PASS`). PNG/runtime
  trace/capture는 만들지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): finalization 성공 회귀는
  `close, exit, summary, copy, validator` 순서 PASS. summary 0/2·비최종·미종료 네 fixture는
  validator 미호출, raw 보존, BLOCKED 예외 PASS. surface 16개 조건과 각 단일 mutation 검출 PASS.
  fresh runtime, G1 2배 출력/입력, G1/M1은 SKIP/BLOCKED다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: runner/bridge 테스트 계약은 강화했지만
  실제 Wine 게임 trace, complete present, 1600×1200 출력과 입력 대응은 검증하지 않았다. 다음
  Sol/high 독립 검수 전 fresh runtime/G1 승격 금지. G2~G4와 사용자 승인은 미검증/미승인이다.
- 다음 한 가지: 새 Codex `gpt-5.6-sol`/high가 lap119 변경과 `make check`/fresh bridge evidence를
  독립 검수하고, fresh runtime 허용 여부를 판정한다.
