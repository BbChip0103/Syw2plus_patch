# 2026-09-11 | lap 188 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna` / high / work tier hands-on 구현.
- 가설 / 사용자 관찰: A-15의 `truncation_exceeds_threshold`가 clamp 여부를 함께 판정해,
  clamped run의 기록 ratio가 threshold를 넘어도 false가 되는 증거 불일치가 있었다. 같은
  레코드의 pre-poll ratio와 threshold만 strict `>`로 비교하면 증거가 일치하고,
  `window_truncated`와 `UNKNOWN_BUDGET_EXHAUSTED` 분류는 유지된다.
- 예상 PASS / FAIL 조건: clamp+pre-poll 4.0초/timeout 6초/stage budget 10초에서
  `truncation_ratio=0.4`, `truncation_threshold_ratio=0.25`,
  `truncation_exceeds_threshold=true`, `window_truncated=false`, 분류
  `UNKNOWN_BUDGET_EXHAUSTED`; 기존 below-threshold clamp와 near-threshold verdict 불변.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/runtime_env.py` SHA256
  `db2113a7f1cf0fbe41f5c4ccb187a71bb9e7adbae371dd8486db46c8dabc4226`,
  `tests/test_runtime_env.py` SHA256
  `0ea2788b99220f66d7c3341b4f39a3f6dcfa09b2bd937ba8810e2a6494b1c61a`;
  uncommitted, `LOOP_ALLOW_COMMITS=0`; docs/STATUS·본 이력·ESCALATE_SOL도 갱신.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  보호 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`;
  제품 후보/실행 후보/활성 플레이어/지도/군대 N/A; Python 3.13.5, pytest 9.0.2;
  synthetic monkeypatched monotonic fixture만 사용, 게임/Wine/Xvfb fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 -m pytest -q tests/test_runtime_env.py -k 'wait_state and
  (separates_pre_poll or clamp_keeps_threshold or near_threshold or shared_budget_exhaustion)'`
  → 5 passed, 91 deselected; `make check` → 209 passed, Ruff PASS, compileall PASS,
  mypy 9 files PASS, `CONTEXT_PASS`; `bash checks/safety.sh check` → `SAFETY_PASS`;
  Bash syntax loop → `SHELL_SYNTAX_PASS`; `sha256sum`으로 보호 SHA/소스 fingerprint 확인.
  캡처 없음(실제 게임 실행 금지).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): A-16 코드·회귀 **PASS**. P2 fixture는
  `effective_poll_window=2.0`, `run_deadline_clamped=true`, `run_deadline_clamp_seconds=4.0`,
  `truncation_seconds=4.0`, ratio `0.4`, threshold `0.25`, exceeds `true`,
  `window_truncated=false`, classification `UNKNOWN_BUDGET_EXHAUSTED`. 기존 P1
  ratio `0.2`/exceeds `false`와 기존 threshold·classification 우선순위 유지 **PASS**.
  Stage B/P6/게임 실행은 **SKIP (지시상 금지)**; G1 제품 합격은 **미완료**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: P2 clamped-above-threshold 회귀를
  `tests/test_runtime_env.py`에 고정했다. A-16은 work tier 결과이므로 자기 승인하지 않는다.
  다음 새 middle 세션이 source hash, full gates, 독립 clamp probe를 검수해야 한다.
  Stage B는 `docs/feedback/APPROVALS.md` 사용자 승인이 없어 계속 닫힘; WM_CLOSE 결함,
  실제 원본/후보 입력 비교, G2~G4 증거도 미해결.
- 다음 한 가지: 새 middle 세션이 A-16을 독립 확인하고, 승인 전 Stage B/P6/game run을 하지 않는다.
