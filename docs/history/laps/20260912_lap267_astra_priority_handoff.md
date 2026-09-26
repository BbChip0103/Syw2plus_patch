# 2026-09-12 | lap 267 | G1 상위 방향 — 실패 보존 및 실행 분리

- 실제 provider/model/effort / 지정 역할: OpenAI Codex gpt-6-astra / high / major direction.
  사용자 최신 역할 지시를 적용한다. 중간 모델 호출·구현·자기 계획 독립 승인 없음.
- lap: runtime 안내 266과 달리 읽기 전용 `loop/.lap_counter`는 267. 파일 값을 사용했다.
- 목표/가설: 역사 probe의 반복 수리가 제품 증거로 이어지려면 실패 수리의 종료 경계를
  먼저 고정하고 S1/F2-R2의 측정 가능한 조사로 연결해야 한다.
- 입력: PROMPT ①~⑥, AGENTS, INBOX, APPROVALS, STATUS 전체, DESIGN 1~4,
  MODEL_ROUTING, lap266 검수 원문/JSON, 현재 R29 helper, handoff S1/F2-R2/R6-B-R2.
- 이전 바퀴 검수: 출하 테스트/SUT/runtime SHA 3개와 lap266 JSON SHA 2개가 기록과 일치.
  JSON에는 R29 M8 8 passed 생존, 거부 전 review 문 171줄 실행, helper 관측 0줄이 있다.
  R30B 미러는 M0/M1 8 passed, M2/M3/M6/M7/M8 각 1 failed/7 passed다.
  이는 파일·계약 대조이며 이번 세션의 변이 재실행 또는 독립 범위 승인이 아니다.

## 상위 결정 및 중간 역할 검토 계약

1. R29 반려를 유지한다. R30B는 구현 후보이며 일반적인 AST 재작성 전체를 막는 증명이 아니다.
   알려진 이동/decoy 행렬의 통과만 범위 증거로 인정한다. 원래 결과 이름까지 바뀌면 완전성
   검사 실패와 실제 late-refusal 탐지를 구분해야 한다. 새로운 변이를 끝없이 늘려 마감하지 않는다.
2. 실패 게이트 우선 원칙에 따라 R30의 한정 수리 경로를 유지하되, 중간 역할이 먼저 수리 범위와
   종료 기준을 확인한다. 이 기록만으로 work를 실행하거나 R29/R30을 승인하지 않는다.
   work는 tests/test_review_probe_output.py에 한정하고 역사 SUT/게임/보호 자산을 변경하지 않는다.
   M0 8 passed, M1 개명-only 생존, M2/M3/M6/M7/M8 사살과 R17 단독 하중, 기존 회귀 보존,
   fresh make check가 기준이다. 예상 밖 필수 실패·근거 충돌이면 보존 후 ESCALATE_SOL로 종료한다.
   실무 결과는 다음 새 middle 세션에서 별도 검수한다.
3. R30 범위 승인 후 R20 이하 offline 목록을 자동 소진하지 않는다. 제품 증거 차단인 S1/F2-R2의
   실행 가능한 조사 설계가 우선이다. 기존 결함은 주차하며 삭제하거나 PASS로 바꾸지 않는다.
   중간 역할은 각 결함의 실제 Stage B producer/comparator 호출 경로를 확인해 필요한 항목만
   선행조건으로 분류한다. 역사 probe 전용 결함을 제품 게이트라고 가정하지 않는다.
4. S1의 우선 조사 후보는 동일한 초기 상태를 복원하는 지원 저장/로드 또는 고정 시나리오다.
   이는 존재/충분성이 확인되지 않은 가설이다. 현재 파일 근거에서 지원 경로·관련 자산 SHA·
   nation/player/타입/상대 위치/엔진 slot·입력 직전 상태를 함께 재현할 수 있는지 work가 조사하도록
   middle이 한 장의 계약을 만든다. 승인된 seed 주소가 없으므로 RNG 주소/패치를 추측하지 않는다.
   지원 경로가 없으면 정확한 누락 근거를 research blocker로 반환한다.
5. F2-R2 slot 강등과 scene gate는 유지한다. semantic bijection으로 바꾸는 대안은 별도 상위
   재결 사항이며 이번 계획은 허가하지 않는다. R6-B-R2의 count 1→0 계약 충돌도 미결로 보존한다.
   중간 역할은 고정 drag의 의도/관측과 양 계약 근거를 대조해 상위 재결용으로 반환한다.
6. 현재 runtime 실행 예산은 0이다. Stage B/원본 재실행/Wine/Xvfb/R6-A/R6-C를 열지 않는다.
   향후 해금안은 같은 fixture의 원본↔원본 대조부터 설계하고, scene 및 slot 동일성 관측,
   상태 복원 부작용, 원본/후보 SHA·환경·실제 입력·독립 evidence를 명시해야 한다.
   pair 수/시간을 사전 고정하고 mismatch를 INCONCLUSIVE로 보존한다. 맞을 때까지 재시도 금지.
   이 계획에는 새 runtime 예산 승인이 없으며 G1 마감/P6/G2~G4로 이동하지 않는다.

## 종료/보존 및 검증

- 사용자 종료 조건에 따라 기존 필수 검수 반려와 명시된 R6-B-R2 구현 근거 충돌을 보존하고
  middle에 이관한다. 이번 세션에서 수리·변이 재시도·마일스톤 마감을 하지 않는다.
- 현재 다음 한 가지는 docs/STATUS.md만 따른다. 본 문서는 결정 계약이며 별도 실행 큐가 아니다.
- 변경 파일: 본 기록, STATUS, 기존 handoff의 최신 결정 포인터, ESCALATE_SOL,
  이전 STATUS 원문 및 입력 SHA manifest. 모두 uncommitted; 커밋/푸시 없음.
- 원본 EXE pin: b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac.
  새 후보 SHA 없음. 게임/활성 인원/지도/군대/fixture/PNG 없음. 제품 증거 증가 0.
- 검증 명령과 결과는 아래에 추가한다. 패치 생성/원복과 runtime은 SKIP(문서 전용, 실행 금지).
- 계획 상태: middle 독립 검토 대기. 프로세스 exit 0은 계획 승인/제품 PASS가 아니다.

### 이번 세션 fresh 검증 결과

- `make check`: 279 passed (46.25s), Ruff PASS, compileall PASS, mypy 10 files PASS,
  CONTEXT_PASS, shell syntax PASS. 로그: `20260912_lap267_astra_fast.log`.
- `LOOP_DRY_RUN=0 bash checks/safety.sh check`: SAFETY_PASS (원본 및 보호 기준 검사).
- 별도 문서 검사: STATUS 117줄(상한 130줄), Blockers 정확히 하나, 카운터 267 무변경,
  출하 테스트/SUT/runtime SHA 3개 무변경 PASS.
- 역사 변이 실험 재실행 SKIP. R29 반려 유지; R30 구현 및 독립 검수 미실행.
- 필수 Fast는 통과했으나 알려진 검수 반려/계약 충돌은 해결되지 않았다. ESCALATE_SOL 유지.
