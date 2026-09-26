# W27 — 정산 재개 counterfactual: H-gate vs H-place 판별 (lap486 middle 발행)

- 발행: lap486 middle (Claude Code claude-opus-5 / high), 2026-09-22 KST.
- 근거 경계: `loop/ESCALATE_SOL` §51 판정 Q3=F1(op4 **2콜** 기전 probe 한정 허용, middle이 W27 발행).
  승계 경계 §49 R1·R2 → §51 R2′·R3·임계 재교정 의무·사전 고정 라벨 3종.
- **상태: `CLOSED` (lap488 middle 독립검수로 종결).**
  - lap487(work)가 §4를 게임 1회 동기 실행(1~6단계 완주, **7단계 미실행** — N130).
  - lap488(middle) 원시 재계산 = **측정 ACCEPT**(불일치 1건은 대조군 지연 정의 결함,
    판정 무영향) / **확정 라벨 `SETTLEMENT_RESUMED_AFTER_HEADROOM`**.
  - **단 §5가 그 라벨에 붙인 귀결 "⇒ H-gate 확정"은 채택하지 않는다(N127).**
    개입 전 체류가 **2tick**뿐이라(= `T_block=200`의 1/100, 대조군 분해능 ~4tick 미만)
    "주문이 막혀 있었다"가 측정되지 않았다 ⇒ 정산 재개는 H-gate와 "애초에 막히지 않았음"을
    **구분하지 못한다.** §1의 질문은 **OPEN**이다. 기록 귀결은 **"H-gate 지지, 확정 아님"**.
  - 전문 `docs/history/laps/20260922_lap488_middle_w27_independent_review.md`,
    회부 `loop/ESCALATE_SOL` §53(Q4 교정 재실행 재승인 / Q5 §8 "W27 실행" 충족 여부).
  - **이 카드의 결함은 lap486 middle(=발행자)에게 있다.** §4-6의 "+50tick 이내 발사"가
    정상 정산 지연 0~4tick 앞에서 **차단이 드러나기 전 개입을 강제**했고(N127),
    §5 R1 승계는 재개 신호(`used` +비용)를 그 자체로 위반으로 만들어
    **재개 라벨을 문언상 도달 불가능**하게 했다(N128). lap487의 실행 준수는 정확했다.
- 선행 카드 `G2_SETTLEMENT_GATE_SEPARATION_PROBE_LAP480.md`(W25)는 `CLOSED`
  (라벨 `PRECONDITION_NOT_MET`, 사유 `order_terminated_without_production_at_tick1943`).

## 1. 묻는 것

W25는 "정산이 cap을 재검사하는가"(§1)에 답하지 못했다. 표적 주문은 `used+reserved=5005>cap` 상태에서
progress100으로 529tick 체류한 뒤 **생산 없이 종결**됐고(N122), 그 종결이
**H-gate**(정산이 cap을 재검사하고 포기)인지 **H-place**(배치/스폰 실패 타임아웃)인지 구분되지 않는다(N123).

이 카드가 묻는 것은 하나다:

> 주문이 progress100에서 대기하는 동안 `used`를 `cap−비용` 아래로 되돌리면 **정산이 재개되는가?**

- 재개된다 ⇒ **H-gate 확정**. 체류의 원인은 정산 단계의 cap 재검사이며, N68(24k 미해소 `reserved`)의
  직접 기전이다.
- 재개되지 않는다 ⇒ **H-place 지지**(H-gate 반증은 아니다 — 대기 중 이미 포기했을 수 있다).

**이 카드는 기전 probe이지 G2 안정성 증거가 아니다.** 결과를 cap 근접 안정성·제품 완료·W26 정량
근거로 재사용하지 않는다(§51 R2′).

## 2. 실행 전 확정된 입력 (lap486 middle이 원시 재계산으로 독립 확인)

lap483 원시 산출물만으로 재계산했다(`run_summary.json`·lap483/484/485 서술 미사용).
재계산 스크립트·결과: `temp/Syw2plus_patch/g2_capacity/20260922_lap486_middle_w27_issue/`.

- 원시 6종 SHA256 재계산 전부 일치: `window_samples` `420dfe5e…`, `positive_control_samples`
  `acca6f12…`, `supply_probe_call_log` `aecd0094…`, `death_events` `fb6ea9d8…`,
  `finalization_events` `4f53cda1…`, 스크립트 `46f8da26…`.
- 창 350표본 tick 719~3052, **전수 주사 결과 장부 전이 정확히 2건**:
  tick1943 `{used4995,reserved10,count5}→{4985,0,5}`(비균형 차감·count 불변, N120·N122),
  tick2270 `{4985,0,5}→{4975,0,4}`(사망).
- op4 1콜 tick717 `{used70,reserved10}→{used4995,reserved10}`, `r7=4995`, `ok=true`.
- 표적 arm: progress100 최초 tick1414 → 종결 tick1943 = **체류 529tick**.
  **tick1414~1936의 79표본 전부** `alive=true`·`hp=3600`·`progress==100`·`command==15`·
  `reserved==10`·`used==4995`·`order_a_finalized=false` (lap486 신규 전수 확인).
- 대조군: progress100 표본과 정산이 **같은 tick709** ⇒ **지연 0tick**. 음수·랩 0,
  finalization 0건·death 1건.

⇒ lap485 strategy의 spot-check 주장은 불일치 0으로 재현된다. §51 판정의 사실 기반은 성립한다.

## 3. 임계 재교정 (§51 의무, middle이 확정)

**N124(lap486 신규):** 대조군 지연 "0tick"은 **표집 해상도 한계값**이다 — 대조군 표집 간격이
3~4tick이므로 참 지연은 `[0, 4)` 구간 안에서만 알 수 있고 0으로 확정된 것이 아니다.
따라서 §51이 예시한 `max(32×대조지연, 절대200tick)`의 곱셈항은 **0으로 퇴화**하며,
**절대 하한 200tick이 임계를 지배한다.** 곱셈항을 해상도 상한(4tick)으로 읽어도 `32×4=128 < 200`이라
결론은 같다. ⇒ **확정 임계 `T_block = 200tick`.**

**N125(lap486 신규, N121 확증):** 이 임계를 W25에 소급 적용하면 lap483의 체류 522tick(79표본 전구간
조건 충족, §2)은 `T_block=200`을 **2.6배 초과**한다 ⇒ W25가 `PRECONDITION_NOT_MET`(null)로 떨어진 것은
정산 차단이 없어서가 아니라 **임계 `5L=3510`이 과대했기 때문**임이 원시로 확증된다.
이는 §50 Q2 판정(E2, 144k 계속 닫음)의 근거를 강화한다 — 문언 충족을 근거로 W26을 열었다면
교정 결함을 통과 근거로 바꾸는 것이었다.

`T_block`은 이 카드의 `NO_RESUME_WITHIN_WINDOW` 판정에도 그대로 쓴다.

## 4. 실행 절차 (게임 1회·source 변경 0·새 스크립트는 temp에만)

`temp/.../20260922_lap482_work_w25_settlement_gate_probe/w25_settlement_gate_probe.py`
(`46f8da26…`)의 환경·goal·안전 골격을 **복사해** 새 스크립트를 만든다. 저장소 source는 건드리지 않는다.

1. 후보 기동 → PS3 → `cap==5000` 확인 → op7로 rice/wood 1,000,000.
2. **양성 대조(겸 정산 경로 생존 확인):** 버리는 producer PC(op6, type46)에 낮은 `used`에서
   op1(type7, cost10) 1건. 정상 정산까지의 tick을 이번 run의 **L**로 기록하고,
   **progress100 표본 → 정산 표본의 지연**을 별도로 기록한다(§3 임계의 run 내 재확인).
   여기서 정산이 안 되면 즉시 `PRECONDITION_NOT_MET`(사유 `control_settlement_failed`).
3. 표적 producer A(op6, type46)에 **낮은 `used`(실효 headroom ≫ 비용)** 에서 op1 1건.
   수락 판정은 `reserved` 0→10 **그리고** rice −800 동시 확인(N107 5중 신호 규칙).
4. **op4 콜 #1 (구성).** 수락 확인 직후(progress<100, ≤0.25L 이내) `used = cap − 5 = 4995`를 쓰되
   rice/wood 1,000,000을 같이 넘겨 자원을 보존한다. before/after 장부를 그대로 기록한다.
   이 상태 `used+reserved = 5005 > cap`이 W25가 만든 것과 동일한 구성이다.
5. **pending 구간 표집을 조밀하게.** 4단계 이후 **표집 간격 ≤3tick**으로 올린다
   (W25 창은 6~7tick이었다 — 5단계 마감과 재개 시점을 tick 단위로 분해하려면 필요하다).
   매 표본: `tick, used, reserved, count, rice, wood`, A의 `command/progress/production_type`,
   **A 생존 플래그**(op0 존재비트·owner·type 일치, N115 의무), 주문 미정산 추적값(N114 수리).
6. **op4 콜 #2 (counterfactual).** 전제 검사(R3)를 **모두** 만족할 때만 발행한다:
   A `alive` · `progress==100` · `reserved==10` · `command==15` · 주문 미정산.
   **발행 시점: progress100 최초 확인 후 +50tick 이내.** 이 창을 놓치면 재시도 없이
   `PRECONDITION_NOT_MET`(사유 `counterfactual_window_missed`).
   이미 종결됐으면 `PRECONDITION_NOT_MET`(사유 `order_terminated_before_counterfactual`).
   **쓰는 값: `used = 4980`** (`used+비용 = 4990 ≤ cap`, 여유 10). rice/wood는 동일하게 보존.
   before/after 장부를 그대로 기록한다.
7. **관측:** 6단계 이후 **≥600tick**(=3×`T_block`) 또는 종결/사망까지 계속 표집한다.
   600tick은 W25 종결 시점(counterfactual 예상 발행 ~tick1464 + 600 = 2064 > 1943)을 덮도록 잡았다.

**op4는 정확히 2콜**(4단계 1 + 6단계 1). 그 외 어떤 경로로도 op4를 쓰지 않는다(§51 R2′).

## 5. 사전 고정 판정식 (§51이 고정한 라벨 3종만 쓴다. 1회 종결)

- **`SETTLEMENT_RESUMED_AFTER_HEADROOM`** — 6단계 이후 관측 창 안에서
  `reserved` 10→0 **그리고** `used` +비용 **그리고** `count` +1 인 전이를 1건 이상 관측.
  ⇒ **H-gate 확정.** 정산은 cap을 재검사하며 N68의 직접 기전이다.
  **⚠ 세 조건은 AND다.** `reserved`만 0으로 내려가고 `count`가 불변이면 그것은 재개가 아니라
  W25 tick1943과 같은 **비균형 종결**(N120)이므로 아래 `NO_RESUME_WITHIN_WINDOW`로 간다.
  이 구분이 이 카드의 핵심 판별자이며 사후에 완화하지 않는다.
- **`NO_RESUME_WITHIN_WINDOW`** — 6단계 이후 `T_block=200tick` 이상, A가 **생존**한 채
  `progress==100`·주문 미정산이 유지되고 위 3조건 AND 전이가 0건.
  (비균형 종결 1건만 관측된 경우도 여기에 포함하고, 사유에 `unbalanced_termination_at_tick<N>`을 남긴다.)
  ⇒ **H-place 지지. H-gate 반증은 아니다** — 대기 중 이미 포기했을 가능성이 남는다.
  후속은 §51대로 F2(배치 축 선배제)를 strategy에 재고 요청한다.
- **`PRECONDITION_NOT_MET`** — 위 둘 중 어느 쪽도 성립할 수 없는 모든 경우
  (주문 미수락 / op4 거부·범위 초과 / A 사망 / 창 내 progress100 미도달 /
  2단계 대조 정산 실패 / R3 전제 불성립 / counterfactual 창 놓침).
  **사유 문자열을 반드시 남긴다.**
- **R1 승계(§49):** op4 write 이후 매 표본 `used`를 기록한다. 판정 전이 시점에 `used`가
  op4 기록값에서 엔진에 의해 이탈하면 `PRECONDITION_NOT_MET`(사유 `ledger_reverted_by_engine`)로
  종결하고 재개 라벨로 쓰지 않는다.
- **재시도·파라미터 변경 재실행 없음.** 한 라벨로 1회 종결하고 middle 검수로 되돌린다.

## 6. 안전·보고 의무

- 원본 SHA 전후 확인, 후보/브리지 SHA 기록, 격리 prefix/Xvfb 전용, 잔류 프로세스 0 확인.
- **background 금지(INBOX 2026-09-21 01:01, lap463·lap482 2회 위반).** 모델 세션이 직접 기다려
  완주하고 산출물 갱신을 확인한 뒤 회차를 끝낸다.
- F4 게이트 유지, **사전 예외 1건**: op4 write 이후 `used > cap`가 되는 사건은 이 실험이 만든
  의도된 조건이므로 abort 사유가 아니라 **측정값**이다. 음수·int16 wrap·포인터 손상은 즉시 STOP.
- **N120 관측 의무:** 종결(비균형 차감)이 발생하면 그 장부 전이를 before/after로 남긴다.
  별도 카드로 추적할지는 W27 결과 후 strategy가 판정한다(§51).
- **`used`가 실제 유닛 구성과 어긋난 의도적 장부 desync**임을 산출물 최상단에 명시한다.
  라벨은 "장부 구성 fixture"이며 cap 근접 안정성·G2 완료·W26 정량 근거로 재사용 금지.
- op4 배제 핀 3종을 **유지·수정·면제하지 않는다**(lap486이 3종 모두 현존 확인):
  `tools/runtime_env.py:5837` `"op4_used": False` / `tests/test_g2_stock_stress.py:19`
  `assert "request(4" not in SOURCE` / `tests/test_g2_eight_owner_setup.py:166` `"op4" not in block.lower()`.
- source 변경 0을 3자(before/after/git) 일치로 증명하고, 표적 테스트 + `checks/safety.sh check` +
  `checks/context_limits.py`만 수행한다(동일 source이므로 전체 `make check` 면제,
  2026-09-20 21:58 지시 + N22). source를 바꿨다면 면제를 주장하지 말고 전체 게이트를 돌린다.
- 산출물: `temp/Syw2plus_patch/g2_capacity/20260922_lap487_w27_settlement_resume_counterfactual/`
  (원시 표본 JSON, run summary, 로그, 스크립트 사본, 각 SHA256).
  **lap 기록을 반드시 남긴다**(N64 재발 금지).

## 7. 이 카드가 닫히는 조건

- §4 1회 실행 → middle 독립 검수(원시만 재계산) → 라벨 확정 시 `CLOSED`.
- R3 전제 불성립으로 counterfactual을 발행하지 못하면 `PRECONDITION_NOT_MET` 1회로 닫고
  §51대로 F2 재고를 strategy에 회부한다.

## 8. W26(144k) 재개방 조건 — §51 Q2=E2 (이 카드가 운반한다)

144k는 계속 닫혀 있다. **재개방 조건(§47 조건을 대체):**
**W27 실행 + middle 측정 ACCEPT + 새 무결성 위반(음수·랩·풀 손상) 0** ⇒ **라벨과 무관하게**
middle이 W26을 발행할 수 있다. 단 W26 카드는 다음을 **반드시** 싣는다:

- **N120**(비균형 차감, 종결 1건당 유령 headroom 10, 자연 발생 여부 UNKNOWN),
  **N121·N124·N125**(임계 교정 결함과 그 확정 임계 `T_block=200`),
  **N123**(N68 미재현, H-gate/H-place 병존)을 **미결 위험으로 명시 기재**.
- `used`/`reserved` 기반 수치는 정산 게이트 질문이 닫힐 때까지 **"부분 증거" 라벨 강제**.

## 9. 범위 밖 (모델이 착수하지 않는다)

- (ㄴ) G2 한정 최소 AI/설정 변경 — 사용자 전권 대기.
- lap404 (가)/(나) 전비 장부 pending 초과 마감 방식 — 사용자 전권 대기.
- F4 (B)/(C) — §38에서 (C) 채택 상태, 랩/음수 관측 시 즉시 STOP 후 (B) 재심.
- 3단 마일스톤 사용자 승인 — 모델의 기술 컨펌과 구분한다.
