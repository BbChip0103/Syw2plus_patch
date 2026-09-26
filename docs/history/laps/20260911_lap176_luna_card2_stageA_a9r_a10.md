# 2026-09-11 | lap 176 | 목표 G1 (카드2 A-9R 기록 및 A-10 회귀)

- 실제 provider/model/effort / 지정 역할: Codex GPT-5 현재 세션(모델 effort 메타데이터 미노출) /
  hands-on work; 프로젝트 지정 work route는 Codex `gpt-5.6-luna`/high.
- 가설 / 사용자 관찰: A-9 기록은 production 한 건이 아니라 PS3 이후 실제 세 wait 전체의 예산을
  다뤄야 하며, off-mode에서도 production `BLOCKED` 관측이 기존 verdict를 바꾸지 않는 회귀가 필요하다.
- 예상 PASS / FAIL 조건: 세 wait의 진입 시각·잔여 예산과 FAIL/UNKNOWN 분리 방법이 기록되고,
  `enabled=False`에서 required input이 True로 비개입하며 기존 baseline·후보 verdict가 유지되면 PASS.
  게임 실행/Stage B/P6를 시작하면 범위 FAIL이다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tests/test_runtime_env.py`에 A-10 회귀 1건 추가, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`, 본 기록, `loop/ESCALATE_SOL` 갱신.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`). `tools/runtime_env.py` SHA
  `8893761db973cbb0dab5fdee0a1a26cc3bf7c9f5db1324c4ec9641f1d41bdc9`; 변경 테스트 SHA
  `ab523a67e0f9e97c524e03fddb6b600985e43ca0b1da9ce3153a4c804c565762`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 EXE 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 바이너리 변경 없음.
  게임 실행 0회, 활성 플레이어·지도·군대 N/A. 테스트는 synthetic in-memory fixture이며 실제
  원본/후보 runtime은 실행하지 않았다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'g1_input_verdict or g1_shared_input_sequence or g1_menu or g1_scene or production_click'` → 8 passed, 78 deselected.
  `make check` → pytest 199 passed, Ruff PASS, compileall PASS, mypy PASS, `CONTEXT_PASS`.
  `.venv/bin/python -m pytest -q` → 199 passed. `bash checks/safety.sh check` → `SAFETY_PASS`.
  `git diff --check` → PASS. 새 캡처·게임 로그 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - A-9R PASS(기록): 현재 세 wait가 공용 `started + timeout`을 공유한다는 사실, 약 81초 예산
    공유와 약 30초 close-stall 관측 절단 위험, `record()` 이전 예외로 인한 증거 유실,
    run-wide elapsed/동일 예외 메시지의 FAIL·UNKNOWN 혼동을 기록했다. Stage B 전에는 단계별
    진입/종료 monotonic 경과·잔여 예산·tick·predicate 관측을 flush하고, 단계 deadline 또는
    구조화 timeout 원인이 있어야 `FAIL_NO_EFFECT`와 `UNKNOWN_BUDGET_EXHAUSTED`를 구분한다.
    이번 바퀴에는 런타임 deadline을 변경하지 않았다.
  - A-10 PASS: off-mode에서 production BLOCKED가 `required_inputs=True`, baseline·후보
    `overall=PASS`를 유지하고 production blocked 관측은 별도 필드로 남기는 회귀 추가.
  - 1단 Fast PASS: 위 명령의 199 passed 및 정적 검사 전부 PASS. 실제 게임/통합 증거는 SKIP(범위).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: A-6~A-8 middle 승인 유지, A-9R/A-10은
  이번 work 결과다. Stage A 전체는 새 middle 독립 판정 전까지 보류. G1 실제 원본/후보 입력
  parity, Tier-2 동일 장면, WM_CLOSE 종료, production mapping, G2~G4, 사용자 승인은 미검증.
- 다음 한 가지: middle tier가 이번 변경 SHA와 A-9R/A-10, `make check`·pytest·safety 결과를
  독립 확인하고 Stage A 승인 여부만 판정한다. 승인 전 게임 실행·Stage B·P6는 금지한다.
