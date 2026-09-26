# G4 Astra/medium — major branch after waypoint movement (2026-09-16)

## Decision

**FEASIBLE: bounded opt-in idle-combat reinforcement candidate.** Not product/AI-quality approval.
Astra/medium는 큰 분기에서만 사용했다. Sol/high는 중간 계획·컨펌, Luna/high는 실무를 수행한다.

원본 길찾기 교체 대신 원본 AI current waypoint로 roster 밖 idle combat source의 명령 누락을
보완한다. 적 검색/target ID 주입/group 가입/생성/경제/생산 변경은 하지 않는다.

## Prerequisite / next middle story

현재 CHB/_imeGetTime diagnostic 반복은 정상 simulation scheduler의 증거가 아니다.
제품 후보를 이 경로의 외부 wall-clock 반복으로 구현하지 않는다.

Sol/high 중간 계획 확인 대상으로 **읽기 전용 정상 AI/simulation hook 경계 조사**만 넘긴다.
Luna는 원본 caller/callshape/빈도/mode/save-load/reset을60–90분 또는 실패2회 안에 확정해야 한다.
Exact old bytes/normal phase/지원 모드/loadreset을 입증하지 못하면 **BLOCKED**로 종료한다.
추가 one-shot 반복/CHB 전수 수리/엔진 재현으로 조사 범위를 넓히지 않는다.

## Candidate / validation constraints

- 원본 AI current waypoint와 기존 AI/live/full-ID/idlecommand/pending/type/map/all200 roster guards.
- 고정 simulation-tick cadence 및 owner/slot 순서, owner당 한 source, 기존 명령 덮어쓰기 금지.
- DLL 비저장카운터만으로 결정론 주장 금지. 중복/새게임/load 상태는 simulation save와 일관되어야 함.
- SHA/oldbytes pin, opt-in/원복, 지원하지 않는 실행 mode fail-closed.
- 동일 bridge OFF/ON, seed1+추가seed fresh 반복, 같은 simulation tick의 발행 결정 대조.
- 도착/idle 체류뿐 아니라 실제 전투 참여/공격 지연 측정; 이동 증가만으로 전략 개선 주장 금지.
- 인간 owner개입0·생성0·경제생산경로무변경·identity교체/명령덮어쓰기0·save/load 회귀.
- LAN/replay 비활성 경계 증명 전 활성화 금지; LAN 동기화/장기/제품은 별도 검증.
- G1 UI tail/G2/G3 blocker를 이 후보로 해소된 것으로 처리하지 않는다.

첫 seed1 movement PASS의 fresh one-shot repeat는 별도 Luna 실행 중이며 이 기록 시점 PENDING.

## Sol/high middle CONFIRM — discovery only

경계 anchor `0x41C770 → 0x41CB40 → 0x41CBE5(call 0x43F5D0)`를 시작점으로 exact PE/callshape·빈도·mode·save/reset을 읽기 전용으로 조사하도록 확인했다. Static owner=`saved tick & 7`이므로 단순tick%300은owner0/4만 방문하는 cadence 오류를 만든다. 제품 hook은 미승인. Luna/high에 새 단일 분석표 `analysis/memory_maps/g4_normal_ai_insertion_contract_20260916.md`를 할당했다. 경계/지원mode/load 일관성 UNKNOWN이 남으면BLOCKED, 구현 전에 exact contract의fresh Sol 검수 필수.

## Discovery followup — narrow mode/postload dependency only

Luna normalAI 경계표 완료 후 Sol은 exactboundary/owner/serializer 사실을ACCEPT했다. 제품activation은미승인. ECX-only ABI/cadence owner선택/Unitpending serializer 위치/두caller-vslogicaltick 구분을 좁게정정하도록 반환했다. 다음은positive localfreebattle allowlist와firstpostload normaltick 경로만 닫는bounded조사다. B93982/88 전체writer/reader나이미확인한group/issuer 의미를 다시전수조사하지않는다. mode discriminator 또는postloadincrement edge를닫지못하면구체BLOCKED, CHB외부반복제품화없음.
