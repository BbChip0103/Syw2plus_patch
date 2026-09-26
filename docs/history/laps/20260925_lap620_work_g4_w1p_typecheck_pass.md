# 2026-09-25 | lap 620 | 목표 G4

- 실제 provider/model/effort / 지정 역할: 현재 Codex 세션 / hands-on work 역할. 하위 모델 호출 없음.
- 가설 / 사용자 관찰: lap619에서 `_g4_shadow_provenance()`의 `dict[str, Any]` 반환값을 이질적 `provenance` dict 안에 넣은 뒤 재인덱싱해 mypy가 `object`로 넓혔다. 동일 결과를 명시적 지역 변수로 한 번만 참조하면 fail-closed 의미를 바꾸지 않고 타입 오류를 제거할 수 있다.
- 예상 PASS / FAIL 조건: provenance 활성·비활성·missing·empty·외부 symlink 5개 회귀 유지, targeted pytest·safety·전체 `make check` PASS. 실패 시 변경 보존 후 `loop/ESCALATE_SOL` 승격; 게임 실행·재시도 금지.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted:)
  - `tools/runtime_env.py`: `46b6c43e83bac98b242be4d932b500189e10528d22998b788aa0196a4603e563`
  - `tests/test_runtime_env.py`: `7030dd1f8bca3329b79f8c37a781a2dffe4aac2e7cfd1ca67f6f5b5101f364cd`
  - `_g4_shadow_provenance(prefix, env)` 결과를 `dict[str, Any]` 지역 변수 `g4_shadow_provenance`에 한 번 저장하고 provenance/verdict가 이를 함께 참조하도록 최소 수정. 커밋 없음, uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 EXE·게임·bridge·save 미접촉, 후보 바이너리 없음, Wine/게임 실행 없음, 활성 플레이어·지도·군대·fixture 해당 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k g4_shadow_provenance` → 5 passed, 156 deselected.
  - `bash checks/safety.sh check` → `SAFETY_PASS`.
  - `make check` → 851 passed in 491.35s; Ruff PASS, compileall PASS, mypy 10 files PASS, `CONTEXT_PASS`.
  - 장기 실행 로그는 호출 출력으로 보존되며 새 캡처·게임 raw·공유 temp 산출물 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted/typecheck/Fast는 PASS. W1P 코드 수리와 기계 검증만 완료했으며 G4 제품 runtime 증거·`FEASIBLE_BASELINE`·G4 PASS는 SKIP/보류. G1/G2/G3에는 변경 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 5개 fail-closed provenance 회귀와 전체 회귀 PASS. 다음 새 middle의 diff·회귀·Fast 독립 검수가 남았고, 그 뒤 strategy가 fresh exact-one runtime 필요 여부를 판정한다. 사용자 3단 승인 없음. G4 기존 fresh raw는 lap616/617 계보의 증거이며 이번 회차에서 재사용·승격하지 않음.
- 다음 한 가지: 다음 새 middle이 lap620 최소 타입 수리와 검증 결과를 독립 검수한다. 검수 전 게임 실행, raw backfill, bridge/제품 AI 수정, G4 PASS 승격을 하지 않는다.
