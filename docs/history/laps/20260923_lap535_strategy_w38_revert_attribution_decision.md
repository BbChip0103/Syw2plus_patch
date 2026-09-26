# 2026-09-23 | lap535 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, strategy(큰 방향). 게임 실행 0, 제품 source·하네스 변경 0, 커밋 0.
- 가설 / 사용자 관찰: lap534 middle이 W38 결과(`PROMOTED_NO_MOVE`×`CONTROL_NA`)를 lap532 §3 분기표 밖으로 보고 회부했다(`ESCALATE_SOL` §88).
  판정할 것: R1(철회 writer 정적 추적) 채택 여부, R2(대조 재설계) 순서, H7 재정의, 전열 배치 보류 여부.
- 예상 PASS / FAIL 조건: 다음 회차를 게임 실행으로 곧바로 넘기면 PASS다. 문서 회차를 한 번 더 요구하면 FAIL(문서 연속 3회)이다.
- 변경 파일 / source fingerprint / 커밋: 문서만 바꿨다. 커밋 0(uncommitted).
  - 신규 `docs/work/active/G2_STRATEGY_W38_REVERT_ATTRIBUTION_LAP535.md`(SHA `77f5de26153994cedce1142b9954d3d791d5024558d31e36b8225167ca26730c`)
  - 이 기록, `loop/ESCALATE_SOL` §89, `docs/STATUS.md`, `docs/feedback/INBOX.md` 처리 줄
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `b56986e0…c9c08a8ac`(이번 회차 `sha256sum` 재확인). 후보 `a10024de…`, 지도 100×100, fixture는 W38과 같다.
- 실행 명령 / 로그: 읽기만 했다(재계산 스크립트 1회 재실행 포함).
  - W38 원시 5종·`w38_run.py`·`runtime_bridge.c`·핀 테스트 2개 SHA 확인(전부 lap533·534·W38 §2 기록과 일치).
  - `python3 recompute_w38.py`(lap534 폴더) 재실행 → `recompute_w38.json` SHA `4b1e350d…04768096` 그대로(같은 내용으로 다시 쓰임).
  - `waves.jsonl` op8 발행 tick 분포, `recompute_w38.json` 소스별 `+0x290` 순서, lap438 `watch_summary.json`·`gdb_watch.py`·`RECOVERY_NOTE.txt`, `ptrace_scope`·gdb 존재.

## 측정값 / 판정

- **독립 확인:** lap534 수치(113/144 즉시 철회, moved 22 = owner3 16·owner7 6, 최소 거리 4 미만 0)를 재실행으로 재현했다.
  신규로 확인한 것: 파동 1~3이 **같은 슬롯**을 고른다(owner0 `3800` 세 파동 모두 1→4→1, owner3 `3185~3190` 세 파동 모두 이동 뒤 복귀). 독립 소스는 48개다.
  op8은 파동당 48건이 약 1.7 tick 간격으로 순차 발행된다.
- **J1:** 분기표를 확장하지 않는다. 전열 배치는 보류한다(N198로 전제 불지지).
- **J2:** R1을 채택하되 **런타임 하드웨어 write watchpoint 귀속 probe(W39)** 로 바꾼다. 철회 슬롯이 결정적이라 writer pc를 1회 실행으로 잡을 수 있다.
  W18(lap438)이 같은 도구로 1회에 pc를 잡았고, 원인은 후보 빌드의 즉시값 재배치 오탐이었다(lap439). pc를 잡은 뒤 그 함수만 원본·후보 바이트로 대조한다.
- **J3:** H7(type110)은 폐기한다. AI 생산에 기대지 않는 H7'(개방 구역 시딩 type2 1:1, 거리 10~20)를 정의만 한다. W39에는 넣지 않는다.
- **J4:** N192 계열 실패 가설 2개(W37·W38) 경계에서 **계속**으로 판정했다. 종결 조건을 고정했다: W39 + 후속 work 1회 뒤에도 `hit` 짝 <2이면 S1 교전 경로를 `BLOCKED`로 닫고 사용자에게 보고한다(후보 결함 확정 시 예외).
- 144k는 닫힌 채다.

## 회귀 / 남은 위험 / 승인 상태

- source 변경 0이라 `make check`는 생략했다(N22). `checks/safety.sh check`와 `checks/context_limits.py` 결과는 STATUS 바퀴 기록에 적는다.
- 위험 1: gdb가 붙은 채 브리지 op8(main thread)이 돌아야 한다. lap438은 op 발행 중에 붙지 않았으므로 이 조합은 처음이다. deadlock이면 `BLOCKED(harness)` 1회 재시도.
- 위험 2: 철회는 op8 뒤 25 tick 안에 일어난다. watch는 반드시 op8 **전에** 걸어야 한다(무장에 1~2초 ≈ 25~50 tick).
- 위험 3: gdb 트리거 pc는 쓰기 명령의 다음 주소다. 명령 시작 역산을 빠뜨리면 함수 귀속이 틀린다.
- 사용자 승인·마일스톤 판정은 없다. 전열 배치 보류와 H7' 정의는 통지다(번복 가능).
- 문서 회차 연속 2회째다(lap534·535). 다음 회차가 게임 실행 없이 끝나면 STOP하고 사용자에게 보고한다.

## 다음 한 가지

work(Sonnet5)가 판정 문서 §2 W39를 실행한다. 게임+gdb 1회 foreground, 45분 상자. 그다음 middle이 원시로 재계산하고 §3 분기를 발행한다.
