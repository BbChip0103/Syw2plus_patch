# 2026-09-12 | lap325 | G1/M1 R1 연구 범위 결정

- 실제 모델/역할: Codex gpt-6-astra/high, major direction/master-plan. 게임 코드 수정 없음.
- 번호: runtime 메시지는 lap324이나 읽기 전용 loop/.lap_counter 실제 값 325를 지시서대로 사용. counter 쓰기 0.
- 목표/가설: R1에 필요한 세 제한 변경을 연구 상한으로 결정하고 middle/work 검증 경계를 분리한다.
- 입력/성공식: INBOX→APPROVALS→STATUS, DESIGN 1~4절, MODEL_ROUTING, lap323/324 방향·판정·기록·probe.
  범위/유효성/판정/실패 보존/역할 인계가 명시되면 상위 산출물 성립. 미정 실행 근거는 승격하며 실행하지 않는다.
- 결정: runtime 1 fresh run≤90초 + 연구 하네스 + 클릭 1회 조건부 상한 허용. 즉시 실행은 0.
  도달 판정과 별도 x/y store 표본 일관성이 미정이므로 ESCALATE_SOL. middle 수용/실무 구현/독립 검수 전 발효 금지.
- 이전 검수: lap324 probe 수정 없이 1회 실행, rc0 failures=[], stdout SHA
  c00eed094885334ecc2fb072defb543ac43e4cd2e32105919518859fbb1e21cf로 이전 보고서와 byte-identical.
  정적 재현성 확인일 뿐 새 독립 알고리즘·게임 runtime 증거 아님. 직접 writer 1/1의 간접 writer 사각 유지.
- 변경 파일: docs/work/active/G1_R1_SCOPE_DIRECTION_LAP325.md, docs/STATUS.md,
  docs/history/laps/20260912_status_lap324_compaction.md, 본 기록, loop/ESCALATE_SOL; logs/lap325 검증 기록.
  모두 uncommitted. 기존 미커밋 파일 보존, git add/commit/push 0.
- 원본 SHA: b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac (재현 probe 확인).
  후보 없음; 게임/Wine/Xvfb/Stage B/PNG/클릭 0; 활성 인원/지도/군대/fixture N/A(정적·문서 세션).
- 실행 명령: python3 docs/history/laps/probes/20260912_lap324_middle_observation_path_probe.py.
  출력 logs/lap325/lap324_probe.{stdout,stderr}. Fast/장부 검사 결과는 아래 최종 검증에 기록한다.
- 판정: 연구 범위 CONDITIONALLY ALLOWED, 즉시 실행 BLOCKED, A/B UNKNOWN, 제품 G1~G4 미완료.
  마일스톤 이동 없음. 구현 진전 0; 반복 정적 CFG 대신 다음 측정의 실행 조건을 좁혔다.
- 다음 한 가지: STATUS의 새 middle 봉투 검수. 구현 근거 불명확은 재시도 없이 보존 후 종료.
- 초기 읽기 경로 정정: 루트 APPROVALS.md는 없어서 docs/feedback/APPROVALS.md를 읽었다.
  loop/STOP·FULL_TEST 없음은 존재 조회 결과이며 필수 검사 실패가 아니다.

## 부록 A — 수신 lap324 ESCALATE_SOL 원문 보존

SHA256: 52f522a24e74ea8b5eac27ae542bbb4785a60e9bf7ba78fc272fd3ef3ddddea2

```text
lap=324
role=middle (Claude Code claude-opus-5/high) — lap323 실행 경로 양립성 판정 완료, 권한 결정 요청
reason=제출 봉투(§14.7)는 실행 불가능이 아니라 자기모순으로 확인됐다. 개정안 R1은 성립하지만 금지 3건 변경이 필요하며 그 권한은 이 tier 밖이다. 마일스톤 마감 아님.
handoff=docs/work/active/G1_MIDDLE_OBSERVATION_PATH_LAP324.md (판정 §1~§6), 기록 docs/history/laps/20260912_lap324_middle_observation_path_ruling.md
verdicts=격리 시작 ACCEPT; 도달 BLOCKED(입력 0과 충돌); 계측 BLOCKED(exact-site 기구 부재) → 개정 R1 제시; "한 줄만 변경" 반증; 예산·보존 ACCEPT-WITH-CONDITION; 판정식 재작성 필요; work 카드 0
evidence=probe docs/history/laps/probes/20260912_lap324_middle_observation_path_probe.py (0ed6692b0f1aae911d3cb043286fafff7566308fa69668dff069fa716b2fa7d2), report c00eed094885334ecc2fb072defb543ac43e4cd2e32105919518859fbb1e21cf (연속 2회 byte-identical, rc0, failures=[]); make check rc0 361 passed; SAFETY_PASS; 원본 SHA b56986e0…c08a8ac 불변; 보호 트리 90파일 해시 pre/post 동일
key_facts=(1) 읽기 수단은 process_vm_readv 폴링뿐, process_vm_writev/ptrace/int3/winedbg/gdb 0회 → exact-site 증명 수단 없음. (2) 0x4D6312의 산출물은 ds:0x1088B5C/5E에 영속 저장되고 .text 전수 스캔에서 직접 store가 각각 1개(0x4D632A, 0x4D6348), 나머지 19개는 전부 movsx 읽기, 미분류 0 → 폴링으로 A/B 판별 가능. (3) 하네스 대기 상태는 ps∈{3,4,5,6,7,9}뿐이고 PS35/save/0x1088B5C 참조 0, FUN_004D60B0 직접 caller 2개 → 다이얼로그 구성은 최소 1클릭 필요.
requested_decision=R1의 금지 변경 3건 허가/거부 — (i) runtime 예산 0→fresh run 1회(≤90초), (ii) 하네스 수정 금지→연구 전용 읽기 경로·PS 대기 형태 선언 추가(§14.4 i·ii·iii), (iii) 입력 0→클릭 1회 (296,505). Stage B·원본/후보 쌍·PNG 비교·W3 재pin·baseline/golden·원본 실행 이미지 변경(INT3)은 유지 요청.
if_denied=§5(c)와 A/B는 UNKNOWN 유지. 정적 CFG 재개는 요청하지 않는다(lap322 지렛대 소진 유지). 실행 예산 0으로 가능한 유일한 독립 진행분은 §14.1 fixture 모델 반증이다.
next=승격 작업자가 검증할 것: (1) probe 재실행이 report SHA와 byte-identical인지, (2) 직접 store 1/1 결론이 독립 재유도로 재현되는지와 간접 writer fail-open 표기가 유지되는지, (3) R1 판정식의 UNKNOWN 분기(pre==post/수집 실패)가 PASS로 완화되지 않았는지, (4) 허가 시 work가 만들 evidence 경로가 제품 소비 경로와 파일 수준으로 분리되고 N4 선행 조건 단서가 지켜지는지.
constraints=이번 바퀴 게임/Wine/Xvfb/Stage B/PNG/클릭/runtime 예산 0. tools/tests/checks/patches/baseline 무변경(해시 장부가 증거). work 실행 카드 미개시. 커밋/푸시 0. 재시도/강제 마감 없음.
approval=middle 기술 판정이며 사용자 마일스톤 승인도 제품 증거도 아니다. process exit0은 계획 승인/검증 통과가 아니다.
```

## 최종 검증

- `make check` rc0: 361 passed in 55.05s, Ruff/compileall/mypy(10 files)/CONTEXT_PASS. 로그 `logs/lap325/make_check.{stdout,stderr}`.
- `bash checks/safety.sh check` rc0: SAFETY_PASS. 원본 SHA 불변.
- `logs/lap325/hash_ledger_{pre,post}.json`: 동일, 보호 트리 127파일. 이번 장부는 해당 트리의 비-pyc 파일 전체이며 lap324 90개 표본과 개수 비교로 변경을 추론하지 않는다.
- STATUS 126줄/Blockers 정확히 1개. 이전 130줄 전체 원문과 SHA는 압축본에 보존했다.
- 필수 검사 예상 밖 실패 없음. 승격 사유는 R1 도달/표본 실행 근거 미정이며 수리/재시도/마일스톤 마감 없음.
- 위 PASS는 기계 검사만 뜻한다. 실행/제품 검증 SKIP, A/B UNKNOWN, 즉시 실행 봉투 BLOCKED.
