# 2026-09-25 | lap 599 | 목표 G1 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, effort 세션 비노출. 지정 역할은 strategy이고 계약 모델 `claude-fable-5`/Astra를 대신한다. subagent 사용0.
- 가설 / 사용자 관찰: 입력은 `ESCALATE_SOL` §148이다(lap598 middle: W50 raw ACCEPT, top slot native 전제 REJECT). strategy가 판정할 것은 W50R audit-only 1회 허용, 또는 W50 §6 G1 대안/G4 전환이다. INBOX에 새 사용자 지시는 없다(최신 09:52 운영자 결정 계보 그대로).
- 예상 PASS / FAIL 조건: 판정 1건과 실행 전 고정된 결과 분류·다음 handoff가 문서로 나오면 PASS다. 게임 실행·제품/하네스 source 변경이 생기면 FAIL.
- 이전 바퀴 검수 (lap598, 읽기 전용): 원본 DxWrapper `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus/dxwrapper.dll` SHA256 `96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe`가 lap598 기록과 일치한다. `i686-w64-mingw32-objdump -d`로 `0x1000A750..0x1000A9B0`, `0x100DE640..0x100DE680`, `0x10136180..0x101361EA`를 읽었다. redirector가 inner guard `0x101BACC4`·inner cache `0x101BACC0`·inner source `0x101BAC60`을 쓰는 구조를 독립 확인했고 §148과 일치한다. old bytes: `0x1000A969` `ff 35 60 ac 1b 10`, `0x1000A992` `89 0d c0 ac 1b 10`.
- 신규 근거 **N220**(정적, 런타임 미증명): inner cache는 redirector 첫 호출 때 `validate(inner source) ? inner source : 0`으로 채워진다. validator `0x10136180`은 0과 stub `0x1011A180`/`0x100506F0`을 거부하고, 목록에 없는 0이 아닌 주소는 통과시킨다. 그러므로 factory/device=0 early 창에서는 inner guard=0·inner cache=0일 가능성이 높고, 그때 의미 있는 slot은 inner source다. §148의 "inner source == inner cache == native" 조건을 guard 상태별 R1/R2로 정정했다.
- 판정: §148 동의, **G1 계속, W50R audit-only fresh 정확히 1회 허용**(W50 fresh 예산 3회 중 마지막). 결과 분류 R1~R4와 조건부 W50S(1회), R3이면 acquisition 분기를 닫고 G1 대안/G4를 판정하는 것까지 실행 전에 고정했다. 카드 `docs/work/active/G1_STRATEGY_W50R_INNER_SLOT_AUDIT_LAP599.md`.
- 변경 파일 / 커밋: 모두 uncommitted. 신규: 위 카드, 이 기록. 수정: `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL`(§149). SHA256은 STATUS lap599 검증 줄에 적는다.
- 원본 SHA / 후보 SHA / 환경 / fixture: 게임 실행0. 참조 원본 `b56986e0…a8ac`, DxWrapper `96c44319…e8fe`, ini `918e7043…a5a2`. 원본/참고 저장소는 읽기만 했다.
- 실행 명령 / 검증: `objdump`(읽기 전용), 문서 반영 뒤 `make check`와 `checks/safety.sh check`. Fast일 뿐 G1 증거가 아니다. 결과는 STATUS lap599 검증 줄.
- 측정값 / 판정: 게임 실행0이라 G1 수치 없음. strategy 판정 PASS(문서 산출물). G1 제품 미완료, W50 `BLOCKED(plan_contract)` 유지, W50R 미실행.
- 회귀 / 남은 위험: N220이 틀릴 수 있다(예: early 창 전에 다른 경로가 redirector를 이미 불렀으면 guard가 초기화돼 R2가 된다; 분류가 이를 흡수한다). inner source가 다른 wrapper 층이면 R3로 닫는다. WM_CLOSE 정상 종료 FAIL은 별도 위험으로 계속된다. 실행 증거 없는 회차가 lap598·599로 2연속이므로 다음은 반드시 실제 실행 work다. 사용자 승인 없음.
- 다음 한 가지: work가 W50R 카드 §3대로 audit 기록 확장·회귀 테스트 뒤 fresh 1회 동기 실행 → middle 독립 검수.
