# 2026-09-12 | lap323 | G1/M1 — 관측 봉투 상위 판정 및 중단

- 실제 provider/model/effort: Codex gpt-6-astra/high, major direction/master-plan. 게임 구현 0.
- 번호: 사용자 runtime lap322와 달리 읽기 전용 loop/.lap_counter=323. counter 변경/복원 0.
- 목표/가설: §14.7의 입력 없는 exact-site 관측과 기존 실행 금지의 양립성 판정.
- 성공/실패 기준: 시작·도달·계측·종료의 근거가 금지와 양립하면 검토 가능, 누락/충돌이면 반려 후 승격.
- 변경: G1_OBSERVATION_DIRECTION_LAP323.md 상위 판정, STATUS 다음 한 가지 갱신,
  20260912_status_lap322_compaction.md 원문/SHA 보존, 본 기록, loop/ESCALATE_SOL, logs/lap323/.
  모두 uncommitted. 커밋/푸시 0. 게임 코드·tools/tests/probe/pin/baseline/golden 수정 0.
- 이전 바퀴 검수: lap322 probe fresh 재실행 rc0, failures=[], 최종 저장 report와 byte-identical.
  SHA 7d04b9b2ceaace6f29c09f615476cb95491020e3a476b048a2783514e35757ac.
  재현성 확인이며 독립 알고리즘 재검수/실제 실행 증거 아님.
- 명령: python3 docs/history/laps/probes/20260912_lap322_middle_runtime_envelope_review_probe.py;
  bash checks/safety.sh check. logs/lap323/*stdout,*stderr에 보존. SAFETY_PASS, rc0.
- 필수 문서 검사 FAIL: 저장 전 STATUS 초안 assert len(new.splitlines())<=130에서 131줄,
  AssertionError: 131, 작성 명령 rc1. archive와 방향 문서는 이미 저장됐고 초안은 STATUS에 미저장.
  사용자 중단 조건에 따라 수정-재검사 루프와 make check를 진행하지 않았다.
  종료 기록만 기존 STATUS의 다음 한 가지 자리에 기록. 최종 길이 관측은 해시 장부에 보존한다.
- 원본·후보 SHA: 원본 보호 검사는 SAFETY_PASS, 후보 없음. runtime_env·기존 probe의 전후 SHA는 장부.
- fixture/환경/활성 인원/지도/군대: 정적 읽기·문서, 실제 게임 0; 나머지 N/A.
  기존 probe의 save/sprite/과거 PNG 입력은 읽기 전용이며 새 runtime 증거로 승격하지 않는다.
- 판정: 제출 형태 실행 봉투 REJECT, 구성 시점 관측 UNKNOWN, Fast SKIP(중단), 문서 길이 검사 FAIL.
- 미검증: 새 격리 시작·입력 0으로 구성 도달·exact-site 계측 경로 미제출.
  make check와 최종 문서 검수는 새 middle이 수행한다. 재시도/강제 마감 없음.
- 다음 행동: STATUS 단일 큐. middle은 실행 금지별 변경 필요·90초 이내 예산·실패 보존·work 경계를 판정.
  실제 구현은 별도 work 세션, 이후 새 middle 독립 검수. 마일스톤 종료/이동 0, G1~G4 미완료 유지.
- 정정: lap322 STATUS/§14 서두의 bcf4…는 문서 추가 전 report; 최종 7d04…는 lap322 provenance에 명시됨.
  테스트 수 불변은 소스 무변경 증거가 아니다. 이번 전후 해시를 사용한다.

## 수신 lap322 ESCALATE_SOL 원문 보존

SHA256: e72bb67943b8a3ab5ec951b93a54582ff028044fd6fac65ccc560527ef96d415

```text
lap=322
role=middle (Claude Code claude-opus-5/high) — 문서 심사 완료, 관측 허가 요청
reason=§13 여섯 행 판정 완료(§14). 남은 UNKNOWN은 정적으로 해소 불가하며 관측 1건이 필요하다. 마일스톤 마감 아님.
handoff=docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md §14 (판정 §14.0, 봉투 §14.7, N4/W3 §14.8)
verdicts=fixture REJECT; §5(a) 부분 ACCEPT(위치·라벨만); §5(c) REJECT; 하네스 경계 REJECT; §5(b),(e) 예산 REJECT; §5(d),§6 ACCEPT-WITH-CONDITION; 패키지 REJECT
next=상위가 §14.7 최소 관측 봉투 1건을 허가/거부한다. 대상=구성 시점 0x4D6312가 읽는 ds:0xE5BF1C/0xE5BF20 값 1회 관측. 입력 0·클릭 0·쌍 0. 800x600→후보A(240,145), 640x480→후보B(160,85), 그 외→두 후보 폐기 후 blocker 반환.
rationale=후보 A/B는 두 가설이 아니라 하나의 중심식을 두 화면 전역 쌍에 대입한 결과다(§14.3, sprite 헤더 [9,320,310,1] 재유도). 따라서 A/B 선택은 구성 시점 전역값과 동치이고, 이 tier는 이를 더 좁힐 남은 정적 수단을 특정하지 못했다(정적 지렛대 소진 선언).
requested_change=기존 금지 중 "runtime 예산 0" 한 줄만 변경 요청. Stage B·클릭·원본 재실행·하네스 수정·W3 재pin 금지는 유지 요청.
if_denied=§5(c)와 A/B는 UNKNOWN 유지. 정적 CFG 재개는 요청하지 않는다. 유일한 독립 진행분은 §14.1 fixture 모델 반증(실행 예산 0).
corrections=N6(lap284 probe의 ps_states_waited·ps35_references 두 정규식이 집합 소속 형태에 fail-open; 결론은 형태 무관 스캔으로 재성립, 수치 영향 0). §5(d) flush는 stage가 아니라 레코드 단위(호출 9곳). 예산 기구 G1_INPUT_STAGE_BUDGETS는 이미 존재하며 25% 임계는 트리 안에서 이미 "측정이 아닌 가정"으로 선언됨.
constraints=이번 바퀴 게임/Wine/Xvfb/Stage B/PNG/클릭/runtime 예산 0. tools/tests/probe/pin/baseline/golden 무변경(make check 361 불변이 증거). work 실행 카드 미개시. 커밋/푸시 0.
approval=middle 기술 판정이며 사용자 마일스톤 승인도 제품 증거도 아니다. process exit0은 승인/검증이 아니다.
```
