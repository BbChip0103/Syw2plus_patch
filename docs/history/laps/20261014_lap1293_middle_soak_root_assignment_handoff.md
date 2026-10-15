# 2026-10-14 KST | lap1293 middle | G1 2614 soak 원인 확인·기존 root 배정 handoff

- 지정 역할: middle(진단·계획·확인), Codex App 새 세션. 실제 resolved model/effort는 별도 실행 argv 증거가 없어 추측하지 않는다. 루프 번호1293은 읽기만 했다.
- 순서: PROMPT① 합격 기준 → ② AGENTS/INBOX 최신 지시·APPROVALS 반려/STATUS 전체/DESIGN1~4/MODEL_ROUTING → ③ 안전·역할·종료 조건 → ④ 이전 lap1291/1292 검수·현재 원인 확인 → ⑤ 기록·인계 보존 → ⑥ 문서 관련 검증. STOP 없음. 게임코드 hands-on·하네스 수정 없음.
- 목표/가설: root/Sol 확인·work 배정 요구가 아직 미결인지 최신 INBOX와 대조하고, 480초 주장/raw 충돌을 직접 재계산한다. raw 충돌이면 HOLD 유지·승격 종료; 원본/후보/raw 무변경과 실행 가능한 work handoff 보존이 종료 조건이다.
- 최신 근거: INBOX 2026-10-14 00:57 root가 lap1291 HOLD를 이미 수용하고 최소 수리를 work에 배정했다. STATUS의 배정 대기 문구는 뒤처진 큐 기록이다. 승인 취소·추가 승인 요청·새 strategy/middle 카드 없이 기존 배정을 실행할 차례다. lap1292는 코드/게임 변화가 없는 역할 경계 인계였으며 제품 진척으로 세지 않는다.

## 직접 확인 / 판정

- 상위 결과 PASS·lane PASS와 nested trace_summary FAIL 동시 존재. raw8192행, summary install_status failed/drop10932, overflow event_limit2개. 단순 해시/전사 오류가 아니다. **480초 안정성 수용 HOLD**.
- dwell PS3 presents3623개/183.474초. 최초 PS3 raw event 기준 PS27 196.834초·PS29 205.037초, 마지막present→summary257.971초 누락. lap1291 수치와 일치. root00:57의 약197초 종료 표현은 PS27 전환 기준이며 PS29는 약205초다. 승패 종료는 크래시 재현이 아니다. 실제 패배 화면의 기존 독립 검수는 재사용하며 이번에 새 이미지 판정은 하지 않았다.
- 현재 source에서 `tools/g1_esl2614_display_probe.py:157`은 lane.status/사본제거로 상위 PASS를 결합하며 nested FAIL은 합격식에 없다. `tools/g1_saved_scene_probe.py:2804`는 PS3 present의 존재·화질·안전계수만 판정하고 목표시간 coverage를 검사하지 않는다. `tools/inmm_stub/direct_draw_trace.c:39`의8192 예산/event_limit 분기는 raw overflow와 부합한다. 원인 추정은 이 직접 확인 범위로 제한한다.
- `tools/esl2614_runtime.py`의 입력 상수는 여전히 상위 폴더다. 실제 중첩 EXE SHA ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf MATCH. 후보 WINMM d2ce1637574340dbd306fa4a41a591461c899cc03c987568ee018b576ec65c53 MATCH. 새 빌드source 동일성은 확인하지 않았으며 과거Fast/source mismatch를 현재PASS로 쓰지 않는다.
- 원본/후보SHA·fixture: 이번 fresh 실행 없음. 기존 공식2614 신규게임/PS3 dwell, 이전save006 fixture 메타데이터는 원문 result에 유지. 이번 회차 활성플레이어·지도·군대·생성·음악·자체저장로드를 새 실측하지 않았다. 기존4 lane는 lap1291 scoped 확인을 재사용하며 다시 승인하지 않는다.

## work 명시 handoff — root00:57 승인 범위 그대로

1. 단일 work 소유: `tools/g1_esl2614_display_probe.py` 결과결합/soak 판정, 필요한 `tools/g1_saved_scene_probe.py` 시간·상태 관측, `tools/esl2614_runtime.py` 중첩 입력 대응, 필요한 `tools/inmm_stub/direct_draw_trace.c`의480초 관측을 막는 예산 부분 및 관련 회귀만. 다른 세션 G5·G2/G6/G8/G9와 HD 형식/안전핀은 비접촉.
2. 보존 raw 입력으로 nestedFAIL/drop·PS3시간부족/PS29 전환이 상위PASS가 되지 않는 회귀를 먼저 실행한다. 기존 short lane/drop0 성공은 유지한다. 현재 raw/기준을 수정하여 성공시키지 않는다.
3. 입력 SHA 거부·새 전체게임사본/private prefix/빈 display·소유 프로세스 종료·game사본 제거를 유지한다. root가 수용한 중첩 원본을 이동하지 않는다. 수리 뒤 빌드source와 DLL SHA를 새로 기록한다.
4. 실패 soak만 실제 재실행: 경기 종료가 늦는 명시된 save/설정을 쓰거나 같은 조건으로 재시작해 **PS3 누적480초를 별도로 관측**한다. 메뉴/패배 이후 시간·기록 손실은 제외한다. 승패 종료/크래시/도구 오류·부분 결과를 구분한다. 이 fixture는 공개한다.
5. 동일조건 공식2614 G1-off MCI 대조로 DLL 귀속만 확인한다. MCI0-call이면 음악 재생은 UNKNOWN/Windows 사용자 확인 대상으로 남긴다. 관련pytest+lint+typecheck → 실제 실패경로 시험 → fresh middle 확인. 전체make check는 전달 후보 고정 직전1회(root)이며 이번에 실행하지 않는다.
6. 추가 계획 회차로 연장하지 않는다. 연속 문서/보조 확인 상한에 도달했으므로 바로 제품시험 복귀를 위한 승인된 최소수리를 work에서 실행한다. 이 middle 세션은 역할 경계와 사용자 raw충돌 종료 규칙 때문에 실행/수리를 시작하지 않고 `loop/ESCALATE_SOL`을 남긴다.

## 실행 / 보존 / 검증 범위

- 명령: `python3 ../temp/Syw2plus_patch/20261014_lap1293_middle_soak_handoff/recalculate.py` → HOLD_RAW_CONFLICT 산출(exit0은 진단 완료이며 제품PASS/계획 승인 아님). 실제 게임 실행은0.
- 독립 JSON/스크립트는 공유temp 위 디렉터리. result SHA a2e5b7b384a1fc2af32a6f91fb12104b5a8632d4e00a10adda1173dc3de381fa, raw SHA86ba52c4b19c634f7363113346aee68bd482d5507750528a315505d1bda57541. 대상소스4개SHA는review.json에 남겼다. 전구간crash0·잔상0·오디오·Windows·2614 자체save roundtrip·G1 사용자 마일스톤은 미검증이다.
- 변경 파일: STATUS, 이 lap기록, `loop/ESCALATE_SOL`, lap1292 ESCALATE 보존파일; 공유temp 진단2개. 이전 미커밋 코드·문서·raw·게임/prefix·다른세션 산출물은 보존했다. INBOX/APPROVALS의 기존 사용자 지시·미결은 수정하지 않았다. 커밋·전달·deploy0(uncommitted).
- lap1292 ESCALATE2190B/SHA565e93aa4bb50b14cde02c7f2b3fdd1b81840289bc5229fb0cb927cbdf9e57c3는 `20261014_lap1293_preserved_lap1292_escalate_sol.md`에 byte-exact 보존 후 현재 marker 갱신.
- 제품Fast/빌드/게임/전체check SKIP: 문서-only 진단·실질raw충돌 승격 종료다. 문서/안전 검사와 대상SHA 불변 최종 결과는 아래에 기록한다.
- 다음 한 가지는 STATUS만 관리한다. 승격자는 root00:57 배정이 유효함을 적용해 work 최소수리를 실행시키고, 그 새 실행의480초coverage/누락0/상위판정·실패구분을 fresh middle에서 확인한다. 현재480초/마일스톤은 마감하지 않는다.

## 최종 문서·안전 확인

- `python3 checks/context_limits.py` CONTEXT_PASS; `python3 checks/safety.py check --require-game` SAFETY_PASS; `git diff --check` exit0. STATUS69/INBOX316/APPROVALS90줄, Blockers정확히1개.
- 대상소스4개·공식EXE·후보DLL SHA 불변, lap1293 읽기전용 불변, 이전marker byte-exact MATCH. review.json SHA b101b1600be1b6bc2bc32e4197cb8e2ef72971a2b4824b4fc23d2371e1c9af22. 전구현트리 동일성/과거Fast 현재수용은 주장하지 않는다.
- 결과: 원인·root배정 확인 완료,480초제품수용HOLD. 사용자 규칙대로 ESCALATE_SOL과 work handoff를 보존하고 종료한다.
