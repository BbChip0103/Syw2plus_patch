# W25 — N116 분리 probe: 정산 게이트가 cap을 재검사하는가 (lap480 middle 발행)

- 발행: lap480 middle (Claude Code claude-opus-5 / high), 2026-09-22 KST.
- 근거 경계: `loop/ESCALATE_SOL` §47 판정②(W25 1장·게임 1회·source 변경 0·새 스크립트만·재시도 없음).
- **상태: `CLOSED` — 2026-09-22 lap483(work)이 §4+§8을 1회 실행하고, lap484(middle)가 원시 재계산으로
  독립 검수해 §7("라벨 확정 시 CLOSED")을 충족했다. 확정 라벨 `PRECONDITION_NOT_MET`,
  정정 사유 `order_terminated_without_production_at_tick1943`(lap483이 적은 "정산 전 사망"은 오귀속,
  N122). 측정 ACCEPT(불일치 0) / 해석 REJECT(tick1943을 §1의 답으로 승격하지 않음, N123).
  신규 N119~N123과 strategy 회부 2건(Q2 144k 개방 여부 / Q3 op4 2콜 허용 여부)은
  `loop/ESCALATE_SOL`§50, 전문은 `docs/history/laps/20260922_lap484_middle_g2_w25_independent_review.md`.**
  (이전 상태 `READY_FOR_WORK`(lap481 strategy D2 채택, §49 R1·R2)와 그 이전 `BLOCKED_PENDING_STRATEGY`
  사유는 §2·§8에 원문 그대로 보존한다.)

## 1. 묻는 것 (변경 없음)

수락된 생산 주문의 **정산(finalization)이 `used+비용 ≤ cap`을 재검사하는가?**
- 재검사한다 ⇒ `used`가 정산 직전에 `cap−비용` 위로 올라가면 예약이 영구히 남는다
  ⇒ lap406/412/449에서 관측된 미해소 `reserved`(N68: owner4/7이 24k 내내 `{used 4995, reserved 10}`)의
  **직접 기전 재현**.
- 재검사하지 않는다 ⇒ 정산은 cap 무관 ⇒ N68의 원인은 다른 곳(후보 회귀 포함)이며 lap412가 예약한
  stock 대조로 넘긴다.

이 카드는 **기전 probe이지 G2 안정성 증거가 아니다.** 결과를 cap 근접 안정성/제품 완료에 쓰지 않는다.

## 2. §47(ii) 절차가 도달 불가인 이유 (실행 전 확정, 바이트 근거)

§47(ii)는 "op1 1건 수락(`reserved`=10) → 정산 전에 **op5로** `cap−비용 < used ≤ cap`까지 상승"이다.
그러나 진단 브리지 자체가 그 상승을 막는다:

- `patches/population/runtime_bridge.c:211` (op5/op6 공통 가드):
  `if ((LONG)old_used + (LONG)U32(p+0x1c) + (LONG)fixture_cost > S16(p+0x2012)) → "fixture_exceeds_unreserved_supply"`
- 필드 대응은 같은 파일 `ledger()` (99~102행): `reserved=U32(p+0x1c)`, `used=S16(p+0x200c)`,
  `cap=S16(p+0x2012)`, `count=S16(p+0x200a)`.
- 즉 가드는 **`used + reserved + cost ≤ cap`** 이며 이는 N112가 엔진 수락 규칙으로 확정한 식과 동일하다.
- 따라서 `reserved=10`이 살아 있는 동안 op5/op6가 성공시킬 수 있는 최대값은
  **`used ≤ cap − reserved = 4990`**(성공한 시딩 1건의 사후값 `used+cost ≤ cap−reserved`).
  목표 구간은 `used ≥ 4991`. **정확히 1 supply 모자라며, 허용 type {5,7,46}의 최소 비용이 10이라
  더 잘게 접근할 수도 없다.**
- 실측 정합: lap476 원시 669표본의 `max(used+reserved)`가 **정확히 5,000**(초과 0건)으로,
  가드+엔진 규칙이 이 상한을 실제로 유지했음을 보여준다.

⇒ §47(ii)를 문자 그대로 실행하면 **결과가 이미 결정된 `PRECONDITION_NOT_MET` 1회**다.
게임 실행 예산 1회를 정보 0에 쓰게 되므로, 실행 전에 §48로 되돌린다(§47 "전제 미성립이면 라벨로
보고하고 strategy로 되돌린다"의 사전 적용).

## 3. 대체 구성안 (strategy 승인 사항, middle이 고르지 않음)

- **D2(권고): op4 직접 장부 write로 목표 상태를 구성.** `runtime_bridge.c:154~163`의 op4는
  `U16(p+0x200c)=request[7]`(≤5000)로 `used`를 직접 쓴다. 가드를 거치지 않으므로
  `{used 4995, reserved 10, cap 5000}` = **N68 관측치와 동일한 상태**를 1회에 구성할 수 있다.
  **경계 문제:** 본 저장소는 G2 증거 산출 경로에서 op4를 명시적으로 배제해 왔다
  (`tools/runtime_env.py` `"op4_used": False`, 핀 `tests/test_g2_stock_stress.py:19`의
  `assert "request(4" not in SOURCE`, `tests/test_g2_eight_owner_setup.py:166`의 `"op4" not in block`).
  그 배제는 "장부만 바꾼 성공" 금지(AGENTS.md)를 지키기 위한 것이므로, **기전 probe 한정으로 op4를
  쓰는 것은 strategy가 명시 승인해야 하는 fixture 경계 확대**다. 승인 시 결과는 "장부 구성 fixture"로
  라벨하고 안정성 주장에 재사용 금지.
- **D3: 관측형** — cap 근접 시딩 후 엔진 자체 생산 경로가 `used+reserved>cap` 상태를 만들 때까지 관측.
  W21 Step1(24k)이 이미 그 상태를 1,263 owner-표본 보유하므로 새 정보는 producer 단위 계측뿐이고,
  비용은 24k soak 1회다. (ㄴ) 미승인 상태에서 AI 레버를 건드리면 경계 위반 위험도 있다.
- **D4: 접는다** — rider 라인과 함께 N68 기전 질문을 보류하고 (ㄴ) 사용자 승인 대기로 되돌린다.

## 4. 실행 절차 (D2 승인 시에만, 게임 1회·source 변경 0·새 스크립트만)

스크립트는 temp 증거 디렉터리에만 둔다(저장소 source 변경 0). 기존
`round2_step_c_rider.py`의 환경·goal·안전 골격을 복사해 쓰되 아래를 고정한다.

1. 후보 기동 → PS3 → `cap==5000` 확인 → op7로 rice/wood 1,000,000.
2. **양성/음성 대조 겸용:** 버리는 producer PC(op6, type46)에 낮은 `used`에서 op1(type7, cost10) 1건.
   정상 정산까지의 tick을 측정해 이번 run의 **L**로 쓴다(lap476 L=698, lap476 A L=695 참고).
   여기서 정산이 안 되면 즉시 `PRECONDITION_NOT_MET`(정산 경로 자체가 죽은 run).
3. 표적 producer A(op6, type46)에 **낮은 `used`(실효 headroom ≫ 비용)** 에서 op1 1건.
   수락 판정은 `reserved` 0→10 **그리고** rice −800 동시 확인(lap474 N107 5중 신호 규칙).
4. 수락 확인 직후(진행도 100 도달 전, ≤0.25L 이내) **op4 1회**로
   `used = cap − 5 = 4995`를 쓰되 rice/wood는 1,000,000을 같이 넘겨 자원을 보존한다.
   op4의 `before`/`after` 장부를 그대로 기록한다. 이 시점 상태는 `used+reserved = 5005 > cap`이며
   이것이 §1이 요구한 유일한 실험 조건이다.
5. **≥5×L tick** 동안 매 표본 기록: `tick, used, reserved, count, rice, wood`,
   producer A의 `command/progress/production_type`, **그리고 producer A 생존 플래그**
   (op0 query의 존재비트·owner·type 일치 — **N115 의무**).

## 5. 사전 고정 판정식 (§47이 고정한 라벨 3종만 쓴다)

- `RESERVED_RESOLVED` — A의 `progress`가 100에 도달한 뒤 `reserved`가 10→0으로 내려가고
  `used`가 +10(=5005) 또는 `count`가 +1 되는 전이를 1건 이상 관측.
  ⇒ 정산은 cap을 재검사하지 않는다. N68은 다른 원인 ⇒ lap412 예약 stock 대조로 이관.
- `SETTLEMENT_BLOCK_REPRO` — A가 **생존**하고 `progress==100`이며 `reserved`가 5×L 이상 10에서
  불변, 그동안 A의 주문이 **한 번도 정산되지 않았다**(N114 수리: 이미 정산된 producer는 stuck 증인에서
  제외하고, 증인은 "해당 producer의 주문이 미정산"임을 명시적으로 추적한 값으로만 삼는다).
  ⇒ 정산 차단 최초 직접 재현. 다음은 후보 회귀 검토 카드가 우선한다.
- `PRECONDITION_NOT_MET` — 위 두 조건 중 어느 쪽도 성립할 수 없는 모든 경우
  (주문 미수락 / op4 거부·범위 초과 / producer 사망 / `progress`가 창 내 100 미도달 /
  2번 대조 정산 실패 / §2 사유로 구성 자체 불가). **사유 문자열을 반드시 남긴다.**
- **재시도·파라미터 변경 재실행 없음**(§47 (iii)). 한 라벨로 1회 종결하고 strategy로 되돌린다.

## 6. 안전·보고 의무

- 원본 SHA 전후 확인, 후보/브리지 SHA 기록, 격리 prefix/Xvfb, 잔류 프로세스 0 확인.
- F4 게이트는 유지하되 **한 가지만 사전 예외**: 4단계 op4 write 이후 `used > cap`가 되는 사건은
  이 실험이 만든 의도된 조건이므로 abort 사유가 아니라 **측정값**이다(발생 즉시 표본을 남기고
  정상 종료 경로로 run을 닫는다). 음수·int16 wrap·포인터 손상은 그대로 즉시 STOP.
- `used`가 실제 유닛 구성과 어긋난 **의도적 장부 desync**임을 산출물 최상단에 명시한다.
  이 run의 어떤 수치도 cap 근접 안정성·G2 완료 근거로 재사용하지 않는다.
- source 변경 0을 3자(before/after/git) 일치로 증명하고, 표적 테스트 + `checks/safety.sh check` +
  `checks/context_limits.py`만 수행한다(동일 source이므로 전체 `make check` 면제, 2026-09-20 21:58 + N22).
- 산출물: `temp/Syw2plus_patch/g2_capacity/20260922_lap481_w25_settlement_gate_probe/`(원시 표본 JSON,
  run summary, 로그, 스크립트 사본, 각 SHA256). lap 기록을 반드시 남긴다(N64 재발 금지).

## 7. 이 카드가 닫히는 조건

- D2 승인 → 위 절차 1회 실행 → middle 독립 검수(원시만 재계산) → 라벨 확정 시 CLOSED.
- D3/D4 채택 → 이 카드는 `SUPERSEDED`로 닫고 새 카드를 발행한다.
- D2 거부 & 대체 없음 → 이 카드는 **게임 실행 없이** `PRECONDITION_NOT_MET`(사유: §2 구조적 도달 불가)로
  CLOSED하고, N68 기전 질문은 (ㄴ) 사용자 승인 대기로 되돌린다.

## 8. lap481 strategy 처분 (2026-09-22, `ESCALATE_SOL`§49 원문이 우선)

- **Q1 = D2 채택.** §4의 4단계 **op4 1콜**만 허용(기전 probe 한정·1회·재시도 없음). D3/D4 기각.
- **R1 (판정식 보강, §5에 추가 적용):** op4 write 이후 매 표본 `used`를 기록한다.
  `RESERVED_RESOLVED`는 정산 전이(`reserved` 10→0) **시점**에 `used ≥ 4991`이 유지됐음을 원시 표본으로
  증명할 때만 성립한다. 정산 전에 `used`가 op4 기록값(4995)에서 이탈(엔진 장부 재계산 등)하면
  `PRECONDITION_NOT_MET`(사유 `ledger_reverted_by_engine`)로 종결하고 `RESERVED_RESOLVED`로 라벨하지 않는다.
- **R2 (op4 허용 범위):** 스크립트는 temp에만, source 변경 0, op4 배제 핀 3종 유지(면제·수정 없음).
  결과는 "장부 구성 fixture" 라벨, cap 근접 안정성·G2 완료·W26 정량 근거 재사용 금지.
- W26 조건은 §47 그대로(측정 ACCEPT + 비`SETTLEMENT_BLOCK_REPRO`).
