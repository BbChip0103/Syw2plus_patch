# 2026-09-12 | lap 219 | 목표 G1 Stage B — F2 identity 재정의

- 실제 provider/model/effort / 지정 역할: Codex hands-on work tier / high.
- 가설 / 사용자 관찰: 절대 engine slot id는 원본↔후보 parity 술어로 안전하게 쓸 수 없다.
  각 run의 scene에서 선택 slot을 `(owner, type, anchor 기준 상대 world offset)`으로 해소하면
  slot 번호 차이는 FAIL이 아니라 관측 가능한 불확실성으로 닫고, 정규화 identity/count 발산은
  실제 FAIL로 보존할 수 있다.
- 예상 PASS / FAIL 조건: 대응되는 slot 번호만 다르면 `UNKNOWN_SLOT_CORRESPONDENCE`,
  scene에 없는 slot 또는 selection/scene 모순은 `INCONCLUSIVE`, normalized identity/count
  delta가 다르면 `FAIL`, 정상 pair는 `PASS`.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/compare_g1_stage_b.py` SHA256
  `f3dfc1263852c2dbe48c078fc0ffd3c2200026df2d930b38b6522870112bef0c`,
  `tests/test_compare_g1_stage_b.py` SHA256
  `f7b6add02484eda9f1acf0d24bccec519a1b89fe6977ec85579d0899698fe437`.
  커밋 없음(`LOOP_ALLOW_COMMITS=0`). 보존 `loop/ESCALATE_SOL` 및 `docs/STATUS.md`도 갱신했다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 게임 실행 0회,
  PNG 0장, Wine/Xvfb 미사용. 저장소 synthetic fixture로 slot 대응/누락 및 count 발산을
  검증했다. 보존 원본/후보 evidence는 읽기 전용 comparator만 실행했다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_compare_g1_stage_b.py` → **14 passed**;
  보존 pair comparator → `INCONCLUSIVE`, scene `INCONCLUSIVE`, production
  `NOT_COMPARED`, candidate historical untagged input errors 2건, exit 2;
  `LOOP_DRY_RUN=0 bash checks/safety.sh check` → **SAFETY_PASS**;
  `make check` → pytest **238 passed**, Ruff PASS, compileall PASS, mypy FAIL at
  `tools/compare_g1_stage_b.py:270` (`Any | None` assigned to `int`).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): F2 구현의 targeted 동작은 PASS 범위이나,
  필수 `make check`가 mypy에서 실패했으므로 **이번 바퀴 전체 결과는 ESCALATE**다. 제품 G1,
  Stage B, 마일스톤 승인이 아니며 후보/원본 새 게임 실행은 SKIP(상위 S1 차단 유지)다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 타입 오류를 고치지 않은 현재 트리의
  완료 주장은 금지된다. 다음 승격 작업자는 타입 수리 후 `make check`/safety를 fresh 재실행하고,
  독립 probe에서 대응 slot UNKNOWN, 누락 slot INCONCLUSIVE, normalized/count 발산 FAIL,
  정상 pair PASS를 확인해야 한다. F3-R1/R2, R6-B, S1, WM_CLOSE teardown은 미해결이며
  후보 Stage B run·원본 재실행은 계속 금지한다.
- 다음 한 가지: 승격 작업자가 line 270 타입 오류를 수리하고 필수 gate 및 F2 독립 검수를
  완료한 뒤에만 다음 work 카드 R6-B를 판단한다.
