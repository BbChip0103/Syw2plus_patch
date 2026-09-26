# 2026-09-12 | lap 220 | 목표 G1 Stage B — F2 필수 gate 수리

- 실제 provider/model/effort / 지정 역할: Codex hands-on work tier / high; 현재 세션 모델 ID는 노출되지 않음.
- 가설 / 사용자 관찰: lap219의 mypy 실패는 `_is_int` 검사 후 `Mapping[str, Any]` 값이 `Any | None`으로
  남은 타입 경계 문제이며 F2 판정 의미와 무관하다.
- 예상 PASS / FAIL 조건: 타입 수리 후 targeted F2 테스트·fresh `make check`·safety가 통과하고, 독립
  synthetic fixture가 정상 PASS, slot-only UNKNOWN, scene 누락 INCONCLUSIVE, identity/count 발산 FAIL을
  모두 예상대로 내야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/compare_g1_stage_b.py` (`f57f5513b00262c0284a60be30b010575a81bc34be3f01eda89b3bc48f09b727`),
  `docs/history/laps/probes/20260912_lap220_f2_identity_probe.py`
  (`0d907af0a9f94a94b069c289f036c319fef17f90913dfd5c4dbd7457a378e778`), report
  (`2e3cffe1ce96ec9e40d3f1c645111b90398903e85c89db1918c4f6583b88e6db`). 기존 테스트 파일은 변경하지
  않았다. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회, 원본/후보
  binary·EXE/DLL/assets/baseline/golden/evidence 변경 0, Wine/Xvfb/PNG 미사용. 독립 probe는 명시적
  synthetic scene/unit-slot fixture이며 저장소 테스트 helper를 사용하지 않는다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_compare_g1_stage_b.py` → 14 passed;
  `.venv/bin/python docs/history/laps/probes/20260912_lap220_f2_identity_probe.py` → 4/4 PASS;
  `make check` → pytest 238 passed, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`;
  보존 pair comparator (`local/runtime/20260912_022912_3830565_0/output/g1_a/evidence.json` ↔
  `local/runtime/20260911_214253_1178505_0/output/g1_presentation_trace/evidence.json`) →
  `INCONCLUSIVE`, `production=NOT_COMPARED`, exit 2.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): targeted/Fast/safety/probe = PASS. 보존 pair는 후보
  scene 누락과 historical untagged inputs 2건 때문에 `INCONCLUSIVE`이며 제품 증거로 승격하지 않았다.
  **F2 work gate PASS; middle 독립 검수 및 제품 G1 PASS는 미완료.**
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: `cast(int, slot)` 한 줄만 의미 변경 없이 수리했다.
  독립 probe의 첫 호출은 probe root 계산이 한 단계 짧아 `docs/tools/...`를 찾지 못해 중단됐고,
  harness 경로를 `parents[4]`로 고친 뒤 동일 fixture를 fresh 재실행해 4/4 PASS를 얻었다. F2의
  `(owner, type, 상대 world offset)` 해소와 slot-only `UNKNOWN_SLOT_CORRESPONDENCE`는 다음 middle이
  독립 검수해야 한다. S1 장면 통제, F3-R1/R2, R6-B, WM_CLOSE, G2~G4는 미해결이며 사용자 제품 승인은 없다.
- 다음 한 가지: 다음 middle 세션이 F2 독립 probe·fresh gate와 보존 pair fail-closed 결과를 검수하고,
  그 전에는 R6-B 구현이나 후보/원본 새 실행을 시작하지 않는다.
