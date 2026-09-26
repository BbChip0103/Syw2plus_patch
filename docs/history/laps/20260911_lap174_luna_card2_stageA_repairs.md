# 2026-09-11 | lap 174 | 목표 G1 (카드2 Stage A A-6~A-9 수리)

- 실제 provider/model/effort / 지정 역할: Codex GPT-5 현재 세션(모델 effort 메타데이터 미노출) / hands-on work; 프로젝트 지정 work route는 Codex `gpt-5.6-luna`/high.
- 가설 / 사용자 관찰: 후보 verdict가 production `BLOCKED` 입력을 보지 않아 teardown/validator가 PASS인 경우 overall PASS로 세탁될 수 있고, 기존 회귀가 좌표 전송과 양쪽 불변식을 잠그지 못했다. 공용 순수 판정 함수와 호출 좌표 단언으로 Stage A 반려 사유를 제거한다.
- 예상 PASS / FAIL 조건: opt-in 입력 시 5개 태그가 모두 `PASS`일 때만 required input이 참이고, production `BLOCKED`이면 baseline·후보 overall이 PASS가 아니어야 한다. unit/drag/minimap은 논리 좌표 그대로 전송되고 production `(670,490)`은 전송되지 않아야 한다. 기존 off 경로·전체 Fast 게이트가 유지되어야 한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py`, `tests/test_runtime_env.py`, `docs/STATUS.md`, 본 기록. 커밋 없음.
  코드 SHA: `tools/runtime_env.py` `8893761db973cbb0dab5fdee0a1a26cc3bf7c9f5db1324c4ec9641f1d41bdc9c`,
  `tests/test_runtime_env.py` `81c34cc6b83645c0cc7371599f37079750678d11789a86754980bf4077ea3567`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 보호 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 후보 바이너리 변경 없음.
  게임 실행 0회, 활성 플레이어·지도·군대 N/A. 테스트는 synthetic in-memory fixture이며 원본/후보
  runtime fixture를 실행하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_input or g1_menu or g1_scene or production_click'` → 7 passed.
  `make check` → 198 passed; Ruff, compileall, mypy, context check PASS.
  `bash checks/safety.sh check` → `SAFETY_PASS`; `git diff --check` PASS.
  새 캡처·게임 로그 없음. 이전 증거/원본·제품 assets는 읽기만 했다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): A-6 PASS(후보 required input이 overall에 반영),
  A-7 PASS(양쪽 BLOCKED 불변식 및 all-PASS 대조 회귀), A-8 PASS(전송 좌표 및 미전송 production 단언).
  A-9 기록: `_g1_run_input_sequence`의 모든 wait는 기존 `started`/`timeout` 공용 deadline을 사용하며,
  이번 Stage A에서는 단계별 deadline을 추가하지 않았다. production BLOCKED는 효과 wait를 건너뛰므로
  추가 대기 없이 후속 단계로 간다. Stage B를 열 때 fresh run에서 각 단계 호출 전후의 monotonic
  구간, before/after tick, 전체 `elapsed_seconds`를 함께 수집하고, 90초 공용 deadline 소진·단계
  미관측을 별도 BLOCKED/UNKNOWN으로 판정한다. Stage B 실제 실행은 하지 않았다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: Fast 회귀 없음. Stage A는 새 middle의 독립
  검수 전까지 승인으로 승격하지 않는다. G1 실제 원본/후보 입력 parity, 동일 장면 Tier-2 조건,
  WM_CLOSE 종료 결함, production mapping, G2~G4는 미검증이다. 사용자 마일스톤 승인 없음.
- 다음 한 가지: 새 middle tier가 source SHA와 변경 범위, `_g1_input_verdict`/`_g1_presentation_verdict`,
  7개 대상 회귀, `make check`·safety 결과 및 A-9 예산 판단을 독립 검수한다. 승인 전 Stage B/P6/
  게임 실행을 시작하지 않는다.
