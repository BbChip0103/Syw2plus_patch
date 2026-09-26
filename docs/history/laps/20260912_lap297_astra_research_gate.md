# 2026-09-12 | lap297 | G1/S1 연구 게이트 상위 재계획

- 실제 provider/model/effort / 지정 역할: Codex gpt-6-astra / high / Astra major
  direction/master-plan. 중간·실무 모델 호출 없음. 사용자 배너 lap296과 달리 읽은
  `loop/.lap_counter`는 297이므로 PROMPT대로 lap297 사용, counter 쓰기 없음.
- 목표/가설: M1 유지. 연구 관측과 제품 판정을 분리하면 tick 오차 선결 요구의 순환을
  끊을 수 있다. lap290~296 하네스 정비 반복은 제품 진척 0으로 재평가했다.
- 예상 PASS/FAIL: middle이 세 방향 결정과 실행 봉투를 근거별 수용/반려 가능하면
  계획 산출물 성립. 제품 PASS 완화/좌표 추측/예산 자동 발급이면 범위 실패.
- 변경 파일: `docs/work/active/G1_ASTRA_RESEARCH_GATE_LAP297.md`, `docs/STATUS.md`,
  본 기록, `loop/ESCALATE_SOL`. 로그는 `logs/lap297/`. 모두 uncommitted, 커밋/푸시 없음.
- 변경: 연구 tick report-only, 별도 load 연구 evidence, save000/save006 후보 유지 결정.
  lap283 tick 선결 조건만 좁게 대체. lap296 §4.7.6 bounded repair 인계는 보존하고
  W2/과거 probe 정비를 제품 준비의 무한 선행조건으로 확대하지 않는다.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  후보 없음. 구현 모듈 2개와 원본·기존 probe/report SHA 전후 동일
  (`logs/lap297/before_sha256.json`, `preservation_check.json`).
- 환경/fixture: Linux 저장소 `.venv` 정적 검수기. 검수기가 임시 복사본 mutant를 실행한다.
  게임 fixture/지도/군대/활성 인원 해당 없음. 게임/Wine/Xvfb/runtime/Stage B/PNG 0회.
- 이전 바퀴 검수: lap296 probe SHA `ba1f23b8769f0daf22e027b42310b6abbe6e24b2bad83a20ac746e7015babea2`
  및 보존 report SHA `a690843f9c4222a8dadd1af18f6b7b89a9eae70728f40ab0249948bd7e0b584d` 일치.
  `.venv/bin/python docs/history/laps/probes/20260912_lap296_middle_lap295_guard_review_probe.py`
  새 실행 exit0·`failures=[]`, 이전 report와 바이트 동일. `blind_spot_verdict=unguarded`는
  예상된 W2 잠복 결함 재현이며 수리 완료로 바꾸지 않는다. 새 독립 검수기를 만든 것은 아니다.
- 실행 명령/로그: 위 probe → `previous_review_recheck.json` 및 stderr,
  `make check` → `make-check.log`, `bash checks/safety.sh check` → `safety.log`.
  최초 APPROVALS 루트 경로 조회는 파일 없음이었고 실제 `docs/feedback/APPROVALS.md`를
  찾아 원문을 읽었다. 필수 검증 실패가 아니라 문서 위치 조회였다.
- 판정: 상위 방향 RECORDED, middle 독립 수용 PENDING, 제품/runtime SKIP.
  load UI/명령/실행 봉투 근거 불명확으로 사용자 중단 조건 적용, `ESCALATE_SOL` 생성.
  표식은 provider 변경이 아니다. MODEL_ROUTING의 Opus5 전용과 사용자 Sol 표식 차이를
  결정문에 명시했으며 자동 폴백/유료 세션/OMX 실행 없음.
- 남은 위험/승인: S1 카드 종결 REJECT, 사용자 마일스톤 승인 없음. R17/R6-B-R2,
  WM_CLOSE, G3 저장 초과 및 모든 기존 미결 보존. 구현 진척 0, 제품 증거 0.
- 다음 행동: 현재 큐는 STATUS만 따른다. middle이 결정문 handoff의 세 결정/봉투를
  검증하고 work 범위 또는 구체 연구 blocker를 확정해야 한다. 이 세션은 실행하지 않는다.
- fresh Fast 판정: PASS — `make check` 292 passed(48.81s), ruff/compileall/mypy,
  CONTEXT_PASS 및 shell syntax 통과. safety는 SAFETY_PASS. STATUS 130줄/Blockers 1개.
  이는 정적/회귀 검증이며 계획 승인·실제 게임 검증이 아니다. 예상 밖 필수 실패 없음.
- 보존: 변경 파일과 로그의 전체 SHA256은 `logs/lap297/artifact_sha256.json`에 기록.
  변경 전 STATUS 원문은 `logs/lap297/status_before.md`에 보존했다.
