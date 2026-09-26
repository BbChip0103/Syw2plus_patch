# 2026-09-12 | lap 317 | G1 — F1 상위 범위와 검증 인계

- 실제 provider/model/지정 역할: Codex gpt-6-astra / Astra major direction/master-plan.
  high 지시를 따름; 실행 CLI/effort 설정 변경이나 다른 모델 호출 없음.
- 날짜: 2026-09-12 KST. 사용자 배너 lap316, 실제 `loop/.lap_counter`=317; PROMPT에 따라 317 사용, counter 쓰기 없음.
- 목표/가설: 이미 두 차례 수용된 R2 수치를 반복 증명하기보다 F1 전체 바이트 수집만 한정 수리하고,
  성공 기준을 명확히 하면 정적 probe 정비의 범위 확대를 막을 수 있다. M1 유지, 마일스톤 경계 이동 없음.
- 예상 PASS/FAIL: middle이 PE 읽기 우선·정상 접힘 성공/손상 거부·기존 불변식 기준을 각각 판정 가능하면
  문서 산출물 성립. 기준 완화/실행 예산 발급/자기 승인/게임 구현이면 범위 실패.
- 변경 파일: `docs/work/active/G1_ASTRA_F1_SCOPE_LAP317.md`, `docs/STATUS.md`,
  `docs/history/laps/20260912_status_lap316_compaction.md`, 본 기록, `loop/ESCALATE_SOL`.
  전부 uncommitted. 원본/게임 코드/probe/test/기존 report/pin 변경 없음, 커밋·push 없음.
- source fingerprint: `logs/lap317/before_sha256.json`과 종료 `artifact_sha256.json` 참조.
  변경 전 STATUS SHA `b96b79d071b6157cedd817941248ac3c6bdb444b432f99a07692d318a34d295e`, 130줄 전체 원문 보존.
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  후보 SHA/지도/군대/활성 플레이어 해당 없음. Linux 저장소 .venv 정적 검증; 합성 fixture는 기존 회귀 전용.
- 이전 바퀴 검수: lap316 probe/test/report 및 lap315 probe/test/report SHA가 기록과 일치.
  `.venv/bin/python docs/history/laps/probes/20260912_lap316_middle_lap315_v6_review_probe.py`
  → `logs/lap317/previous_review_recheck.json`, exit0, failures=[], 저장 report와 byte-identical,
  SHA `c91a238b8345f74d5f435fa99c872aef99cb54dcb27c4b5861cd97ef141f3af5`.
  기존 독립 검수기의 재현 확인이며 Astra가 새 독립 알고리즘 검수를 작성한 것은 아니다.
  report 내부 lap/role은 생성기 출처 lap316/middle 그대로 보존, lap317 자체 역할을 뜻하지 않는다.
- 측정: 753/753/7/724, unresolved 0, writer 4, 긴 명령 27개, call 31개, 10B reset 두 값 일치.
  게임/Wine/Xvfb/runtime/Stage B/PNG/클릭 0, 구현 진척 0, 제품 증거 0. N1/N2 UNKNOWN 유지.
- 실행 명령: 위 probe; `make check` → `logs/lap317/make-check.log`;
  `bash checks/safety.sh check` → `logs/lap317/safety.log`. 문서 위치 조회 중 루트 APPROVALS 없음은
  실제 `docs/feedback/APPROVALS.md`를 읽어 해결했다. 필수 검증 실패가 아니다.
- 판정: 상위 방향 RECORDED, middle 수용 PENDING, F1 구현 SKIP, 제품 검증 SKIP.
  “접힌 fixture fail-closed”의 정상/손상 구별과 runtime/load 근거 미확정으로 사용자 중단 조건 적용,
  `ESCALATE_SOL`을 생성해 인계한다. 필수 실패 재시도·제품 마감 없음.
- 역할 계약 차이: MODEL_ROUTING의 Opus5 전용과 AGENTS의 Sol/Opus5 차이를 인계 문서에 명시.
  표식은 provider 변경이 아니며 승격 세션이 실제 역할 적합성을 확인한다. 자동 폴백 없음.
- 남은 위험: 기존 STATUS 미결·반려 보존; S1 종결 REJECT, W3 재pin 미승인, 실제 입력/WM_CLOSE 및 G2~G4 미검증.
- 다음 행동: 현재 큐는 STATUS만 따른다. middle이 결정별 수용/반려 후 work 한정 수리를 구체화한다.

- fresh Fast: `make check` PASS — 328 passed(53.31s), Ruff/compileall/mypy/CONTEXT_PASS 및 shell syntax 통과.
  safety SAFETY_PASS. 필수 검증 예상 밖 실패 없음. 계획 승인·제품 성공으로 승격하지 않는다.
- 보존 검증: `logs/lap317/preservation_check.json`의 원본·lap315/316 probe/test/report 7항목 전부 true.
  STATUS 130줄·Blockers 제목 정확히 1개; 새 문서 산출물과 로그 SHA는 `logs/lap317/artifact_sha256.json`.
