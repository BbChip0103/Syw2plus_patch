# 2026-09-23 | lap532 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, strategy(큰 방향). 게임 실행 0, 제품 source·하네스 변경 0, 커밋 0.
- 가설 / 사용자 관찰: lap531 middle이 W37을 `CYCLE_UNSTABLE`로 `CLOSED`하고 3건을 회부했다(`ESCALATE_SOL` §86).
  (1) N192 경로 (a)/(b)/(c) 선택, (2) A6 사망 조건, (3) A3 R_o·op1 조건.
- 예상 PASS / FAIL 조건: 판정이 다음 회차를 게임 실행으로 곧바로 넘기면 PASS다. 추가 계획 회차가 필요하면 FAIL(문서 연속 3회)이다.
- 변경 파일 / source fingerprint / 커밋: 문서만 바꿨다. 커밋 0(uncommitted).
  - 신규 `docs/work/active/G2_STRATEGY_N192_APPROACH_PATH_LAP532.md`
  - `docs/work/active/G2_STRATEGY_Q8A_SEEDED_ACCEPTANCE_LAP522.md` §3에 개정 표시(원문 보존)
  - 이 기록, `loop/ESCALATE_SOL` §87, `docs/STATUS.md`, `docs/feedback/INBOX.md` 처리 줄
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…c9c08a8ac`(이번 회차 `sha256sum` 재확인). 후보 `a10024de…`, 지도 100×100.
  fixture는 lap530과 같다(8 AI owner, owner마다 type5×100·type7×25·type2×60·type46×20).
- 실행 명령 / 로그: 읽기만 했다. lap530 `waves.jsonl`의 op8 receipt 1,872건 집계(`src_cmd`·`src_0x390` 분포), `runtime_bridge.c` op8 분기, G4 2026-09-16 probe 기록.
  확인한 SHA: `w37_run.py` `54bac3ef…c78d`, `runtime_bridge.c` `3555848d…`, 핀 테스트 `2a8aa4f7…`, op8 계약 테스트 `0939f5b6…`(W37 §0-2와 일치).

## 측정값 / 판정

- 신규 사실: op8 1,872건 전부 호출 시점 `+0x290`=1, `+0x390`=3이다(P5 idle 경로). G4 probe의 소스도 type 2였고 stock 개방 지형에서 거리 63을 접근했다.
  W37과 다른 조건은 재배치 후보와 밀집 시딩 블록뿐이다.
- **(1) (a) 채택.** W38 접근 진단 probe(W37 fixture, 파동 3개 + type110 양성 대조 1파동, 소스·목표 추적 원시 기록)를 판정 문서 §2에 실행 사양으로 적었다.
  결과별 다음 행동은 §3 분기표로 미리 고정했다. (b)는 결과가 가리키는 한 구간만 읽도록 미뤘다.
  **(c)는 기각했다.** W37 짝 (2,3)에서 인접분 7기가 죽자 교전이 멈췄다. 인접 배치는 지속성을 만들지 못한다.
- **(2) A6: 약화 거절.** A6a(필드·로드)와 A6b(교전 중 저장 전제 + 로드 뒤 사망 증가)로 나눴다. N194 라벨 틈은 A6b FAIL ⇒ `CYCLE_PARTIAL`로 닫았다.
- **(3) A3: 재정의.** A3'(owner마다 op1 귀속 출생)와 A3r(풀 단위 사망 슬롯 재사용)로 바꿨다. op1 발주 조건은 `used+reserved+10≤5000`이다.
- 144k는 닫힌 채다. 사전 허가(J4)는 `DRIVEN_CYCLE_STABLE`에만 적용된다.

## 회귀 / 남은 위험 / 승인 상태

- source 변경 0이라 `make check`는 생략했다(N22). `checks/safety.sh check`와 `checks/context_limits.py` 결과는 STATUS 바퀴 기록에 적는다.
- 위험: W38이 `CONTROL_STILL`이면 재배치 후보 자체의 이동 경로 결함 가능성이 열린다. 그 경우 G2 후보 결함으로 사용자에게 보고한다.
- 전열 배치(§3.1)와 A3'/A6 분리는 사용자에게 통지만 했다(번복 가능). 사용자 승인·마일스톤 판정은 없다.
- 문서 회차 연속 2회째다(lap531·532). 다음 회차가 게임 실행 없이 끝나면 STOP하고 사용자에게 보고한다.

## 다음 한 가지

work(Sonnet5)가 판정 문서 §2 W38을 실행한다. 게임 1회 foreground, 45분 상자. 그다음 middle이 원시로 재계산하고 §3 분기를 발행한다.
