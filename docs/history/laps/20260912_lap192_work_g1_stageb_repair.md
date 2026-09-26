# 2026-09-12 | lap 192 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 지정 work; Codex `gpt-5.6-luna`/high 설정. hands-on 구현.
- 가설 / 사용자 관찰: `49B6D0 ineligible`은 원본 정상 분기이며, provenance 증거 실패가 뒤의
  무관한 입력 단계를 중단시키는 하네스 제어흐름이 H1/H2의 원인이다. R1~R4만 수리하고
  R5/Stage B 재실행은 승인 경계로 남긴다.
- 예상 PASS / FAIL 조건: stable-ineligible fixture에서 production 클릭은 호출되지 않고
  `BLOCKED`/기존 사유/진단 필드가 기록되며 `drag_select`/`minimap`이 실행된다;
  `required_inputs` FAIL 및 verdict overall non-PASS 불변식 유지; 후보 진단/캐시가 baseline과
  대칭; per-run evidence가 최종 error/진단/inputs를 보존; HQ 식별은 근거 없이 추측하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA256
  `8955789be2a8f39d221e09a0da1010e896f87b0f464106bcc928d5c372c40bd3`,
  `tests/test_runtime_env.py` SHA256
  `7054d441f0ff5bf33e71d0c55397ee4da36f957efe7dd53459a96a03bed1d197`.
  R1/R2/R3/R4 구현 및 회귀 테스트 추가, uncommitted, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보/게임 run 없음;
  stable-ineligible `_command_cell_reader_fixture(branch_type_flags=0)`; 플레이어/지도/군대 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make check` → **210 passed**, Ruff/compileall/mypy/
  CONTEXT_PASS; targeted `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k
  'g1_scene_snapshot or g1_shared_input_sequence or g1_input_verdict or g1_input_stage_flushes
  or g1_flush_input_stage'` → 7 passed; `bash checks/safety.sh check` → `SAFETY_PASS`.
  게임/Stage B 0회, 새 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): R1~R4 구현 및 targeted PASS. R4 HQ 판별은
  `UNKNOWN` provenance로 보존. Stage B 재실행/R5는 승인 경계로 SKIP. 제품 G1은 미완료.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: production BLOCKED 세탁 방지 유지;
  실제 원본/후보 비교, WM_CLOSE 종료 결함, random seed 동일성, G2~G4 증거는 미검증.
  다음 middle이 R1~R4를 독립 검수해야 하며 사용자 승인 없이는 R5/Stage B를 실행하지 않는다.
- 다음 한 가지: 다음 새 middle 세션이 R1~R4를 독립 검수한다. 게임 run 금지.
