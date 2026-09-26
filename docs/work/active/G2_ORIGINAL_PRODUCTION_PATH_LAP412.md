# W9 — 원본 생산 명령 경로로 near-cap 도달 (P2) (발행: lap412 middle, 수행: 다음 work 회차)

> **상태(lap414 middle 추기):** lap413 work가 수행해 **FAIL**(§3 (a) `used≥4900` 미도달, 후보가
> tick11,928에서 두 번 재현 crash). lap414가 원시 산출물로 독립 검수해 그 FAIL을 **ACCEPT**했다.
> 이 카드는 닫히지 않았고 **수리 후 복귀 대상**이다. 후속은 `G2_POOL_SCOPE_1200_FAULT_ROOT_CAUSE_LAP414.md`(W10).
> §4의 되물음1 귀속 probe(stock `used=5000` + 주문1건 → `reserved`)는 **아직 미수행**이다.

- 발행자 / 역할: lap412 Claude Code `claude-opus-5` / high / middle. 근거는
  `docs/history/laps/20260920_lap412_middle_g2_w8_soak_independent_review.md`.
- 수행 역할: **work (Sonnet5/high)**. **이것은 실제 게임 실행 카드다.** 계획·재검수·하네스 정비
  회차로 되돌리지 않는다. lap412가 제품 증거 0회차였으므로 PROMPT ③ "연속 최대 2회"의 2회차가 된다.
- 선행 상태: W8 **CLOSED**(lap412 ACCEPT). 확장 풀의 지속 안정성은 닫혔다.
- 목표 연결: G2 = 활성 8인 각각 전비 5000. 이 카드는 **"원본 명령으로 그 상태에 도달한다"** 축이다.

## 1. 왜 이 카드인가 (범위의 근거)

AGENTS.md: "생성/자원 fixture는 명시. **원본 명령을 우회한 성공**/낮은 부하만의 성공은 부족하다."
지금까지의 near-4000 상태는 전부 진단 브리지 `op=6` 시딩으로 만들었다. 시딩이 gate-legal이어도
그것은 **원본 생산 경로가 아니다**. 이 갭이 닫히기 전에는 G2를 제품 완료로 부를 수 없다.

## 2. 대상 고정 (변경 금지)

- 후보: `g2_full_capacity_v1_n4001_persistence_compat`
  SHA `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`.
- 원본: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 읽기 전용, 실행 전후 재해시.
- 브리지: `--unit-pool-capacity 4001`로 **새로 빌드**, 배포 전 `unit_pool_base=0x0108C000` /
  `unit_existence_base=0x017B8658` 눈으로 확인(lap409의 stock 재사용 사고 재발 금지).
- 격리: `tools.runtime_env.prepare()`로 **신규** 사본 + prefix + 빈 display. 기존 run 재사용 금지.
- 후보 바이트·wrapper 배치·핀 SHA·목표 숫자(8인/5000/4001) 변경 **전부 금지**.

## 3. 성공 / 실패 측정식 (먼저 적고 시작한다)

브리지의 역할을 **관측과 원본 명령 발행으로만** 제한한다. `op=6` 직접 유닛 주입은 이 카드에서 금지.

PASS 조건:
- (a) 최소 1 owner가 **원본 생산 경로만으로** `used`를 5000 근처(**≥4,900**)까지 올린다.
- (b) 그 생산이 원본 경로임을 바이트/호출 수준으로 명시한다 — 사용한 진입점 주소와 그것이
  생산 gate `0x43EDA0`(count cap `+0x2010` / supply cap `+0x2012` 둘 다 강제)를 **통과**했음을 보인다.
  gate를 우회하거나 `roster_add 0x43EE30`을 직접 부르면 **그 run은 실패로 적는다**(F4 계보의 교훈).
- (c) 그 상태에서 slot≥1200 유닛이 **원본 생산으로** 실제 생성된다(최소 1건, 슬롯·id 기록).
- (d) 자원(rice/wood)을 어떻게 공급했는지 fixture로 **명시**한다. 자원 주입은 허용하되
  **유닛·전비 장부 직접 조작은 금지**하고, 주입 사실과 값을 산출물에 적는다.

FAIL/BLOCKED 조건: 원본 경로 진입점을 찾지 못하거나 gate 통과를 증명할 수 없으면
**추측으로 밀지 말고** `BLOCKED`으로 적고 그때까지의 주소·시도·근거를 남긴다.
실패 가설 2회 또는 60분 안에 `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED` 판정.

8 owner 전원·24k soak은 이 카드의 PASS 조건이 **아니다**. 경로가 성립하면 그 다음 카드다.

## 4. 같은 회차에 끼워 넣을 귀속 probe (별도 회차 금지, 시간 상자 20분)

되물음 1의 **미증명 귀속**을 한 번의 관측으로 닫는다.

**stock 원본**(`b56986e0…`, 재배치 없음)을 cap 5000 설정으로 띄워 한 owner를 `used=5000`까지 채우고
생산 주문 1건을 건 뒤 `reserved`를 읽는다.

- stock에서도 `used=5000, reserved=10`이 나오면 → "원본 고유 동작" 귀속 **증명**, 되물음 1은 (가)로
  확정 가능(사용자 판단은 그대로 사용자 몫).
- 안 나오면 → **후보 고유 회귀**로 승격하고 P3를 앞당긴다. 이 경우 이 카드의 결론보다 우선한다.

20분을 넘기면 중단하고 그때까지의 관측만 적는다. 이것 때문에 §3을 미루지 않는다.

## 5. 범위 밖

- strict cap 정책 결정 / 전비 장부 32bit 확장(N19·F4·되물음) — 사용자 답변 대기, 착수 금지.
- LAN(P4), 반복·장기 soak, G1, G4, G3(중단).
- 풀 용량 최종값 결정(N23) — `4001`은 공학 시험값이다. 이 카드에서 바꾸지 않는다.
- soak 번들 검증기 승격(N24) — P4로 미룬다.

## 6. 검사

- 표적: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py -q`.
- **source를 바꿨으면** 통합 경계에서 `make check` 1회(현재 기준선 **785**). 안 바꿨으면 재실행하지
  않되, 면제를 주장할 때 **"이번 회차에 source를 바꾸지 않았다"를 기록에 함께 적는다**(N22 재발 방지).
- 매회 `checks/safety.sh check` → `SAFETY_PASS`, 원본 2경로 재해시 불변, 종료 후 잔류 프로세스 0.
- **산출물에 명시할 것(N21 재발 방지):** 이 회차의 어떤 결론도 `inmm_stub.c`/`ai_shadow.c`/
  `sfx_hook.c`/`control_executor.c` 채널 산출물에 근거하지 않는다는 문장.

## 7. 산출물

증거는 `temp/Syw2plus_patch/g2_capacity/<날짜>_lap<N>_original_production/`에 두고
`docs/history/laps/`에 lap 기록(LAP_TEMPLATE 필드)을 남긴다. STATUS 「다음 한 가지」를 갱신한다.
lap 번호는 `loop/.lap_counter` 값을 그대로 쓴다(N18 재발 방지).

## 8. 중단 조건

- 크래시/포인터 손상/저장 이상이 나오면 숨기지 말고 수치와 함께 보고하고 멈춘다.
- baseline·핀·golden을 고쳐 통과시키지 않는다.
- 자기 결과를 자기가 최종 승인하지 않는다. 다음 middle 회차가 독립 검수한다.
