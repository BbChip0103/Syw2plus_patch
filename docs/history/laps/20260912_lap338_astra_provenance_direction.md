# 2026-09-12 | lap338 | G1/M1 provenance 상위 계획

- 실제 모델: Codex gpt-6-astra, 지정 Astra major direction; effort는 별도 런타임 메타데이터 미확인.
- 목표/가설: 과거 SHA 재pin 없이 원문 보존과 현재 계약 검사를 분리하면 동일한 검수 교착의 재발을 막을 수 있다.
- 입력: PROMPT ①~⑥, AGENTS, INBOX/APPROVALS, STATUS 전체, DESIGN 1~4, MODEL_ROUTING,
  ESCALATE_SOL 원문, lap337 수리 범위/probe, lap334 봉투 관련 기준. counter=338, 입력 lap=337 차이 보존.
- PASS 조건: 이전 probe 재현·현재 계약 유지·문서 길이 준수·독립 middle handoff. FAIL 조건: 필수 검사 실패.
- 변경: 정책 초안/직전 STATUS 보존/종료 상태/ESCALATE 부록/이 기록만. 전부 uncommitted, 커밋 0.
- 소스 SHA: runtime_env=922a267c27f51fe47d7db69962dadbfdbbded9ff04c6350e8cb7a4c44f8a2575,
  test_lap326=c04a6265229f7e37cb9d4434f0e150c76e1e56d26f0e1c990cb938a06d769823 (직전과 동일).
- 원본/후보 게임 SHA: 이번 직접 측정 SKIP, 게임 접근/실행/입력/PNG/패치/원복 수행 0.
  환경=로컬 오프라인 문서/검사, 활성 인원·지도·군대=N/A, 테스트는 합성 fixture이며 제품 증거 아님.
- 실행: python3 docs/history/laps/probes/20260912_lap337_middle_lap336_repair_scope_probe.py
  → rc0 failures=[]·기록 stdout SHA 일치. 원본 artifact 1/후보 0, R-a/R-b 미수리 확인.
- 실행: make check → 376 passed(56.59s), Ruff/compileall/mypy/CONTEXT_PASS.
  bash checks/safety.sh check → SAFETY_PASS.
- FAIL: STATUS 갱신용 Python 사전 assert `len(s.splitlines())<=130`가 `AssertionError: 131`로 rc1.
  이 실패는 파일 쓰기 전 발생했다. 실패 갱신안 재시도 없이 종료 메타데이터만 보존했다.
- 보조 읽기 오류: 루트 APPROVALS.md 부재 → 실제 docs/feedback/APPROVALS.md 읽음;
  loop/STOP 부재 확인. 빌드/검증 실패와 구분한다.
- 판정: 상위 계획 초안 보존, 문서 게이트 FAIL로 STOP/ESCALATE. 과거 probe 실패는 재실행하지 않음.
  설치 시간 여유는 미실측 UNKNOWN, 과거 소스 동일성 복구도 UNKNOWN. 새 정책 독립 컨펌/제품 승인 없음.
- 다음 한 가지: 새 middle이 ESCALATE lap338의 문서 보존·정책 분리 기준을 검수 후 기존 work 수리로 반환.

## 보존 파일 SHA256
- `docs/work/active/G1_R1_PROVENANCE_DIRECTION_LAP338.md`: `f1e3594de1311671c3e09ed34b9bdf6f6ccd68e19ebf0a0b7f4cc2d9b32410b0`
- `docs/history/laps/20260912_status_lap337_compaction.md`: `e771b22c62eaf9322342844e40de814e5328e08bd65be0b9fcffe1529c42c842`
- `docs/STATUS.md`: `bd7598a7a30f5b4f6767dc7c948316cea4055b20369b9038ffbfd38428f589df`
- `loop/ESCALATE_SOL`: `8586486608c6fabf99ec6b0283efa102175d59bc73743fffaca5d229f4883f6a`
- `logs/lap338_astra/make-check.log`: `bc58c4e0855f63fe849baacf3c6112e4159d98ec134c9654297a1b620103f6de`
- `logs/lap338_astra/previous_probe.stdout.json`: `c38a73f1220faf992155bc5a98fe814e9e8ded316b0935e5eb3f22f0738cdf46`
