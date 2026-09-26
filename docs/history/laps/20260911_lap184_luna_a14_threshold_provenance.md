# 2026-09-11 | lap 184 | 목표 G1 (카드2 Stage A / A-14 work)

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
  중간 독립 검수와 Stage B 승격은 수행하지 않았다.
- 가설 / 사용자 관찰: A-13의 2.5초 경계는 실제 측정값이 아니라 설계 가정이며,
  3자리 반올림 evidence는 2.4999초와 2.5001초를 구분하지 못한다.
- 예상 PASS / FAIL 조건: 주석·기록이 synthetic probe를 실측으로 부르지 않고, 값 `0.25`·기존
  필드·분류 순서를 유지하며, 고정밀 비교 evidence와 경계 회귀가 추가되고 Fast/safety가 통과한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py`, `tests/test_runtime_env.py`,
  `docs/history/laps/20260911_lap182_luna_a13_threshold.md`, `docs/STATUS.md`,
  `loop/ESCALATE_SOL`, 본 기록. 커밋 없음(`LOOP_ALLOW_COMMITS` 미설정).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 EXE SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변. 실제 게임/Wine/
  Xvfb/prefix/display 0회; synthetic monotonic-clock fixture만 사용; 플레이어/지도/군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python -m pytest -q tests/test_runtime_env.py -k 'wait_state or input_verdict'`
  → 10 passed; 전체 게이트는 아래 최종 검증에서 실행했다. PNG/실행 증거 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  `truncation_ratio`를 9자리, `truncation_threshold_ratio`,
  `truncation_exceeds_threshold`를 evidence에 추가했다. 2.4999초는 ratio `0.24999`,
  `FAIL_NO_EFFECT`, 2.5001초는 ratio `0.25001`, `UNKNOWN_OBSERVATION_WINDOW_TRUNCATED`로
  구분된다. A-14 코드/회귀 PASS; 실제 게임·Stage B·P6 SKIP(금지·사용자 승인 전).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 기존 3자리
  `truncation_seconds`는 유지하고 threshold `0.25`와 `UNKNOWN_BUDGET_EXHAUSTED` 우선순위도
  유지했다. 실제 pre-poll 분포는 미측정이며 첫 승인된 Stage B run에서 재평가해야 한다.
  새 middle 독립 검수와 사용자 Stage B 승인은 없다.
- 다음 한 가지: 새 middle tier가 source SHA, A-14 provenance/evidence, 회귀와 전체 게이트를
  독립 검수한다. 그 전까지 Stage B/P6를 실행하지 않는다.

## 최종 검증

- `.venv/bin/python -m pytest -q tests/test_runtime_env.py` → 94 passed.
- `make check` → 207 passed; Ruff/compileall/mypy/CONTEXT_PASS.
- `bash checks/safety.sh check` → `SAFETY_PASS`; `git diff --check` → PASS.
- 변경 후 게임 실행 0회; protected EXE SHA 재확인 불변.

최종 SHA: `tools/runtime_env.py` `c2adaa2eeff163dc144cbce657c0d9a1ddc1b26ef2bbd8b6b3d14f7a285b5850`,
`tests/test_runtime_env.py` `a674892c4631ed23caba3a1ca2faf781f24e20f56f3e0dd800bcd92ca67b4c16`,
`docs/history/laps/20260911_lap182_luna_a13_threshold.md`
`88c12cff2c38c3ea25cafdaa6556adaf6850fce7fcd42a2ff7152d01566ea489`.
