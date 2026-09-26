# W28-R — 차단 선입증 + 정산 재개 counterfactual **관측 완주 재취득** (lap494 middle 발행)

- 발행: lap494 middle (Claude Code claude-opus-5 / high), 2026-09-23 KST.
- 상태: **`CLOSED`** — lap496 middle(Claude Code claude-opus-5 / high, 2026-09-23 KST)이 §7대로
  원시만으로 독립 재계산해 **측정 ACCEPT(재현 불일치 0)** 및 **라벨 확정
  `SETTLEMENT_RESUMED_AFTER_HEADROOM`**(attribution=**strong**, `resume_delay_ticks`=**2**).
  근거 `temp/Syw2plus_patch/g2_capacity/20260923_lap496_middle_w28r_review/`
  (`recheck_lap496.py` sha `f9195ffe6cc4e056f98aed9275775c8d0838c1d21e565a88d5669b2a4ad4900b`,
  `recheck_lap496_result.json`, `input_sha256.txt`), 전문
  `docs/history/laps/20260923_lap496_middle_w28r_independent_recheck.md`, 판정 경계 `loop/ESCALATE_SOL` §59.
  실행분: lap495 work(claude-sonnet-5 / high), 전문
  `docs/history/laps/20260923_lap495_work_g2_w28r_settlement_blockage_preproof.md`,
  산출물 `temp/Syw2plus_patch/g2_capacity/20260923_lap495_w28r_settlement_blockage_preproof/`.
  **1회 한정(R-5) 소진 — 재실행 없음.** §8 재개방 3조건 충족 ⇒ lap496이 **W26 발행**
  (`docs/work/active/G2_SEEDED_CAP_PROXIMITY_144K_SOAK_LAP496.md`).
- lap496 재계산 요지(원시만, `run_summary` 미참조): op4 정확히 2콜(r7 4995/4980, 둘 다 ok) ·
  `CALL2_ENGINE_TICK`=**1610**(`tick_before==tick_after`) · `reads.jsonl` 546건이 `window_samples.jsonl`
  542건 + 콜 4블록의 독립 재조립과 **완전 일치** · 관측 완주 **610 ≥ 600**(완주 읽기 tick2212) ·
  AND-3 **정확히 1건**(콜#2 after tick1610 `{4980,10,5}` → 표본 tick1612 `{4990,0,6}`) ·
  차단 선입증 `t0`=**1406**, 발사 직전까지 **74표본 전수** 5중 신호, streak **≥200**, 위반 0 ·
  `CALL2_ENGINE_TICK`±10 구간 `READS` 간격 전부 ≤3(위반 0) · R1′ `ledger_reverted_by_engine`
  **0건**(op4 자신의 write 2건은 `probe_write`로 분리) · `event_crosscheck` 4종 전부 일치 ·
  무결성(음수·wrap·라이브 `used`>cap) **전부 0**.
- 근거 경계: `loop/ESCALATE_SOL` **§57** 판정 **Q6-C 채택** — 결함의 소재는 카드/스크립트이며,
  게임 1회 비용으로 D1·D2·D3를 수리하고 **관측 완주만** 다시 받는다. 경계 R-1~R-6이 이 카드의 범위다.
- 선행: `G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_LAP490.md`(W28) — **측정 ACCEPT(재현 불일치 0,
  §56·§57에서 2회 독립 재현) / 라벨 확정 보류**. W28은 이 카드로 승계되며 재실행하지 않는다.
- **이 카드는 W28의 재협상이 아니다.** 파라미터·판정식·라벨은 W28과 동일하고(R-4), 고치는 것은
  ① 완주 기준선 오적용, ② "읽기"의 문언 미확정 + 콜 주변 표집, ③ 사망 기록 경로 **셋뿐**이다.
- **1회 한정(R-5).** R-1~R-3을 수리하고도 ≥600tick 완주가 다시 미달하면 **Q6-B로 자동 종결**
  (`PRECONDITION_NOT_MET` 확정, 재재실행 없음)하고 미달 원인을 §1 기전 보고에 남긴다.

## 1. 묻는 것 (W28 §1과 동일, 변경 없음)

> `used+reserved>cap` 상태에서 progress100 주문이 **`T_block`=200tick 이상 미정산으로 지속됨을
> 먼저 입증한 뒤**, `used`를 `cap−비용` 아래로 되돌리면 **정산이 재개되는가?**

- 재개 ⇒ **H-gate 지지(선입증이 성립했으므로 W27보다 강함).** 차단 원인은 정산 단계의 cap 재검사.
- 미재개 ⇒ **H-place 지지. H-gate 반증은 아니다** — 대기 중 이미 포기했을 가능성이 남는다.
- 차단이 애초에 200tick에 도달하지 않으면 §5대로 **1회 종결**하고 재시도하지 않는다.

**이 카드는 기전 probe이지 G2 안정성 증거가 아니다.** 결과를 cap 근접 안정성·제품 완료·W26 정량
근거로 재사용하지 않는다(§51 R2′ 승계).

## 2. 실행 전 확정된 입력 — lap494 middle이 lap491 원시만으로 재측정

산출물 `temp/Syw2plus_patch/g2_capacity/20260923_lap494_middle_w28r_issue/`
(`spotcheck_lap494.py`, `spotcheck_lap494_result.json`, `input_sha256.txt`).
입력 SHA256: `window_samples.jsonl` `120d221afb43abea…`, `supply_probe_call_log.json` `85c7aab9adb25434…`,
lap491 스크립트 `11c49ecbacdcab90…`, `death_events.json` `4f53cda18c2baa0c…`(= `[]`의 해시).
`run_summary`의 `verdict`/`reason`/`resume_delay_ticks`/`call2_tick`과 work 파생 보조 필드
(`streak_ticks`/`transition`/`order_a_finalized`/`headroom`/`phase`/`call2_fired`/
`order_a_unbalanced_terminated`/`ledger_reverted_so_far`)는 **입력에서 배제**했다(§7 승계).

**재확인된 실질(변경 없음, 이 카드의 전제):**
- 차단 선입증: `t0`(progress100 최초 표본 tick) = **1414** → 발사 직전 표본 tick **1615**,
  **streak 201tick ≥ `T_block` 200**, 그 구간 **75표본 전수** 5중 신호
  (`alive` ∧ `progress==100` ∧ `reserved==10` ∧ `command==15` ∧ `count==5` 미정산), 위반 표본 **0**.
- op4 **정확히 2콜**(816콜 중). 콜#2 = `id 596`, `r7=4980`, `ok/executed`,
  `before {used4995, reserved10, count5}` → `after {used4980, reserved10, count5}`.
- 재개 전이 1건: `{4980,10,5}`(콜#2 after, 엔진tick**1618**) → `{4990,0,6}`(표본, tick**1620**).

**수리 대상 3건(전부 lap494가 원시·소스에서 재현):**

- **D1 — 완주 기준선 오적용.** 콜#2의 엔진 tick은 `tick_before=tick_after=`**1618**이고 **1615는
  발사 직전 표본 tick**이다. 마지막 표본 tick은 **2216**이므로 카드가 사후 변경 금지로 고정한
  엔진 tick 기준 완주는 2216−1618 = **598 < 600**(2tick 부족). work의 601은 1615 기준이다.
  **소재:** lap491 스크립트 **`:815` `call2_tick = tick`** — 루프 머리에서 읽은 **표본** tick을
  기준선으로 잡고, `:845` `ticks_since_call2 = tick - call2_tick`로 종료를 판단하며
  `:848` 로그가 그것을 "engine tick"으로 **오라벨**한다. `run_summary`의 `call2_tick=1615`·
  `resume_delay_ticks=5`도 같은 오적용의 파생값이다(정답 1618 / **2tick**).
- **D2 — "읽기"의 문언 미확정 + 콜 주변 표집 위반.** `used==4980`은 **550표본 중 0건**이므로
  표본만으로 §5의 AND-3(`used`4980→4990)을 찾으면 **0건**이다. 콜#2 **after 블록을 읽기로
  인정**하면 정확히 1건(1618→1620, 지연 **2tick**). 한편 표본 간격은 min2/max**5**이고
  **>3tick 구간은 창 전체에서 `1615→1620` 단 하나** — 하필 재개가 일어난 구간이다.
  **소재:** 콜 자체가 엔진 tick 3개(1615→1618)를 소비하고 `:871` `time.sleep(DENSE_POLL_S)`가
  루프 말미에 있어, **표본만으로는 콜 구간의 ≤3tick을 물리적으로 만족할 수 없다.**
  ⇒ 요건은 완화하지 않고 **검사 가능한 대상(=병합 읽기열)으로 정의**한다(§3·R-2).
- **D3 — 사망 기록 경로 사망.** 표본 tick**1944**에 `count`6→5 ∧ `used`4990→4970(−20) ∧
  `reserved`0→0인 **사망 1건**이 있는데 `death_events.json`은 `[]`이고 `events.jsonl`에는
  `finalization_balanced` **1건만** 있다. **소재:** lap491 스크립트
  **`:694` `order_open = not order_a_finalized and not order_a_unbalanced_terminated`** +
  **`:695~696` `transition = classify_transition(...) if order_open else "none"`** —
  tick1620 정산으로 `order_a_finalized=True`가 되는 순간 **R1′ 분류기 전체가 꺼진다.**
- **신규 N135 (D3의 더 큰 결과, 판정 무영향이나 반드시 고친다).** 위 게이트는 사망뿐 아니라
  **R1′ 4번(`ledger_reverted_by_engine`)까지** 끈다. 즉 lap491은 재개 직후부터 마지막 표본까지
  **596tick 동안 스크립트 자체의 무결성 채널이 무력**했고, `ledger_reverted_by_engine=False`는
  그 구간에 대해 **검사된 적이 없다**. lap492가 표본 재계산으로 위반 0을 확인해 결과는 무사했지만,
  **fail-closed 장치가 조용히 꺼지는 것은 그 자체로 결함**이다.

## 3. 고정 파라미터 (사후 변경 금지 · W28과 **동일 유지** = R-4)

| 이름 | 값 | 근거 |
|---|---|---|
| `T_BLOCK_TICKS` | **200** | N124 확정 임계(§52). 발사 전건과 무재개 판정에 동일 적용 |
| `T_ATTRIB_TICKS` | **50** | 인과 귀속 구간 |
| `OP4_CONSTRUCT_USED` | **4995** | `used+reserved=5005>cap` |
| `OP4_COUNTERFACTUAL_USED` | **4980** | `used+비용=4990 ≤ cap 5000`, 여유 10 |
| `ORDER_COST` / `ORDER_TYPE` | **10 / 7** | W25·W27·W28 승계 |
| `BLOCKAGE_WATCH_HORIZON_TICKS` | **700** (progress100 최초 **표본** tick 기준) | lap483 종결 529tick을 덮는 값 |
| `WINDOW_AFTER_CALL2_TICKS` | **600** (=3×`T_block`) | §54 관측 완주 |
| op4 콜 수 | **정확히 2** | §51 R2′ |

**R-1 (D1 수리) — 완주 기준선의 유일한 정의.**
`CALL2_ENGINE_TICK := op4 콜#2 결과의 `tick_after``(콜 로그에 기록된 엔진 tick). 완주 판정은
**`tick(r) − CALL2_ENGINE_TICK ≥ 600`인 읽기 `r`이 산출물에 실제로 기록되어 있음**이다.
- **발사 직전 표본 tick(`FIRING_SAMPLE_TICK`)을 기준선으로 쓰는 것을 금지한다.** 그 값은 provenance
  용도로 따로 기록하고, 두 값이 다르면 그 차이(`call2_tick_skew`)를 산출물에 남긴다.
- 종료 조건은 **읽기 tick으로 판정**하되 **`CALL2_ENGINE_TICK + 610`까지 표집을 계속한다**
  (10tick overshoot). 완화가 아니라 표집 간격이 경계를 건너뛰어 599에서 끝나는 것을 막는 여유이며,
  N133(≈33tick/s)대로 벽시계 비용은 0.3초다.
- `resume_delay_ticks`도 **`CALL2_ENGINE_TICK` 기준**으로만 계산한다.

**R-2 (D2 수리) — "읽기"의 정의와 표집 요건.**
`READS`(병합 읽기열) := `window_samples`의 모든 표본 **∪** op4 각 콜의 `before`/`after` 블록,
각각 **엔진 tick을 달고** tick 오름차순으로 정렬한 열. 콜 블록은 `source="op4_call<N>_<before|after>"`로
표시한다.
- **§5의 AND-3 "연속 두 읽기"는 이 `READS` 위에서 판정한다**(콜 after 블록을 읽기로 **인정**한다 —
  문언 확정). 표본만으로 판정하지 않는다.
- **표집 요건: `CALL2_ENGINE_TICK ± 10tick` 구간에서 `READS`의 인접 tick 간격은 ≤3tick**이어야 한다.
  위반 시 그 자체로 **재실행 무효** → `PRECONDITION_NOT_MET`(사유 `sampling_gap_violation`,
  `detail`에 위반 구간 tick). 창 전체에 대해서는 표본 간격 min/max/mean을 보고한다.
  (lap491 데이터에 이 정의를 적용하면 1615→1618→1620 = 간격 3·2로 **적합**이다. 요건을 낮춘 것이
  아니라 콜 지연 3tick 때문에 표본만으로는 도달 불가였던 요건을 **검사 가능하게** 만든 것이다.)
- 콜#2 **직전**에도 표본을 하나 강제로 남긴다(`phase="pre_call2_immediate"`, sleep 없이).
  `READS`는 `reads.jsonl`로 **1급 산출물**로 쓴다 — middle이 다시 꿰매지 않는다.

**R-3 (D3 수리) — 무결성 분류기는 창 전체에서 꺼지지 않는다.**
- `classify_transition`은 **모든 읽기에 대해 무조건 실행**한다. `order_open`은 **주문 상태 전이
  (`resume_balanced`/`unbalanced_termination`)가 주문을 닫는지**만 게이트하며(최초 1건만 주문을 닫는다),
  **사망(`count` 감소)과 R1′ 4번(`reverted`)은 `order_open`과 무관하게 창 끝까지 검사·기록**한다.
- 즉 lap491 `:694~696`의 `if order_open else "none"` 게이트를 제거한다.
- **정산 유닛의 사후 생존을 기록한다(§57 R-3 후단).** 존재배열(`0x8990C8`, slot당 2B, stock 1200slot)을
  콜#2 직전과 AND-3 관측 읽기에서 각각 **1회 일괄 스냅샷**(2,400B 단일 read)해 새로 생긴 slot을
  특정하고(`existence` 0→1 ∧ `owner==0`), 그 slot의 존재/`owner`/`type`/`hp`를 이후 매 표본에서
  producer A와 **같은 방식**으로 폴링한다(`settled_unit_survival`). 특정 실패 시 라벨에 영향을 주지 말고
  `settled_unit_slot=null`과 실패 사유를 남긴다 — 이 항목은 **보고 의무이지 판정 조건이 아니다**.
- **"빈 배열 = 사건 0건" 보고 금지**(§6 재확인). 모든 이벤트 배열은 **관측 읽기 수와 함께** 보고하고,
  종료 시 표본 재계산으로 배열과 대조한 `event_crosscheck` 블록(각 종류별 배열 건수 vs 읽기열
  재계산 건수, 불일치 목록)을 남긴다. 불일치가 있으면 그 자체를 보고한다.

**인과 귀속(사전 고정, 변경 없음):** AND-3 재개 전이가 `CALL2_ENGINE_TICK`으로부터 `≤T_ATTRIB`(50tick)
이면 귀속 **강함**, 50tick 초과~600tick 이내면 귀속 **약함**(middle이 별도 판정). 라벨은 어느 쪽이든
동일하며 `resume_delay_ticks`를 남긴다.

## 4. 실행 절차 (게임 **1회** · source 변경 0 · 새 스크립트는 temp에만)

lap491 스크립트
`temp/Syw2plus_patch/g2_capacity/20260923_lap491_w28_settlement_blockage_preproof/w28_settlement_blockage_preproof_counterfactual.py`
(`11c49ecb…`)를 **복사해** R-1·R-2·R-3만 반영한 새 스크립트를 만든다. 저장소 source는 건드리지 않는다.
후보·구성은 lap491과 동일하다(`fixed_supply_5000.py`, 후보 SHA `0a1da226…`, stock 1200-slot 레이아웃,
`goal=_custom_game_chain_inject_g2_eight_seed42`). **1~7은 W28 §4와 동일하고, 교정은 R-1·R-2·R-3뿐이다.**

1. 후보 기동 → PS3 → `cap==5000` 확인 → op7로 rice/wood 1,000,000.
2. **양성 대조(정산 경로 생존 + predicate 특이도).** 버리는 producer PC(op6, type46)에 낮은 `used`에서
   op1(type7, cost10) 1건, 표집 ≤3tick. 기록: `L`, **표본 tick 기준** progress100→정산 지연,
   `control_delay_resolution_ticks`, 차단 predicate 표본 수.
   - **기대값 정정(N132 승계):** 차단 predicate 히트는 **0건이 아니라 ≤1건이 정상**이고, 판별량은
     히트 유무가 아니라 **연속 지속**이다(대조군 `[0,3]tick` vs 차단창 200tick↑). 히트 1건을
     이상으로 보고하지 말고 **지속 tick과 함께** 보고한다.
   - 정산이 안 되면 즉시 `PRECONDITION_NOT_MET`(사유 `control_settlement_failed`).
3. 표적 producer A(op6, type46)에 **낮은 `used`** 에서 op1 1건. 수락 판정은 `reserved` 0→10
   **그리고** rice −800 동시 확인(N107 5중 신호).
4. **op4 콜 #1 (구성).** 수락 확인 직후(progress<100, ≤0.25·`L` 이내) `used = 4995`를 쓰고
   rice/wood 1,000,000을 같이 넘긴다. before/after 블록과 **엔진 tick**을 기록하고 **`READS`에 넣는다**.
5. **차단 감시 표집(≤3tick).** 매 표본에 `tick, used, reserved, count, rice, wood`, A의
   `command/progress/production_type`, **A 생존 플래그**(존재비트·owner·type, N115),
   주문 미정산 추적값, `phase`를 남긴다. **R-3대로 분류기는 이 시점부터 창 끝까지 무조건 돈다.**
6. **발사 전건 = 차단 선입증(W28과 동일).** progress100 최초 표본 tick을 `t0`으로 두고, `t0` 이후
   **모든 표본이 연속으로** 5중 신호(`alive` ∧ `progress==100` ∧ `reserved==10` ∧ `command==15` ∧
   주문 미정산)를 만족한 상태에서 `현재 표본 tick − t0 ≥ 200`이 되는 **첫 표본 직후** 콜#2를 발행한다.
   - 그 표본 tick을 `FIRING_SAMPLE_TICK`으로 기록하고(기준선으로 쓰지 않는다, R-1),
     **sleep 없이** 곧바로 `phase="pre_call2_immediate"` 표본을 하나 더 남긴 뒤 발사한다(R-2).
   - 연속성이 깨지거나(정산·종결·사망·`command` 변화) `t0+700tick`까지 200tick에 도달하지 못하면
     **발사하지 않고** §5의 `PRECONDITION_NOT_MET`(사유 `no_blockage_ge_t_block_observed`)로
     **1회 종결**한다. `detail`에 깨진 사유와 tick을 남긴다.
   - `progress==100`이 pending 안전 cap(4000tick / 600s) 내에 오지 않으면 같은 라벨,
     `detail=progress100_not_reached_within_horizon`.
7. **op4 콜 #2 (counterfactual) + 재읽기(R-1·R-2).** `used = 4980`을 쓰고 rice/wood는 보존한다.
   - 콜 결과의 `tick_before`/`tick_after`와 before/after 블록을 그대로 기록하고 **`READS`에 넣는다**.
     **`CALL2_ENGINE_TICK = tick_after`를 그 자리에서 확정해 로그에 명시**한다.
   - **직후 재읽기를 sleep 없이** `tick`과 함께 표본으로 기록한다(`phase="post_call2_immediate_reread"`).
     **이 재읽기 결과로 예외를 던지지 않는다** — `used`=4990은 §5의 재개 신호이고 위반이 아니다(N128).
   - 콜#2가 거부되면 `PRECONDITION_NOT_MET`(사유 `op4_call2_rejected`).
8. **관측 완주(R-1).** `CALL2_ENGINE_TICK`부터 **`tick − CALL2_ENGINE_TICK ≥ 610`**이 될 때까지
   ≤3tick 간격으로 **계속** 표집한다. **정산·비균형 종결·사망·AND-3 전이 관측에서 멈추지 않는다.**
   중단은 안전 STOP(음수·int16 wrap·포인터 손상), 게임 프로세스 종료, 벽시계 cap뿐이며 그 경우
   라벨은 `PRECONDITION_NOT_MET`(사유 `observation_incomplete`, `detail`에 사유·도달 tick·
   `tick − CALL2_ENGINE_TICK` 실측값).

**op4는 정확히 2콜**(4단계 1 + 7단계 1). 그 외 어떤 경로로도 op4를 쓰지 않는다(§51 R2′).

## 5. 사전 고정 판정식 (라벨 3종만. 1회 종결 — R-5)

- **`SETTLEMENT_RESUMED_AFTER_HEADROOM`** — 콜#2 이후 **≥600tick 관측 완주**(R-1 기준선) 안에서,
  `READS`(R-2)의 **연속 두 읽기** 사이에 **AND-3 전이**를 1건 이상 관측:
  `reserved` 10→0 **그리고** `used` 4980→**4990**(= 정확히 +비용 10) **그리고** `count` +1.
  ⇒ **차단 선입증(≥200tick)이 성립한 상태의 재개이므로 H-gate 지지가 W27보다 강하다.**
  `resume_delay_ticks`(`CALL2_ENGINE_TICK` 기준)를 남기고 §3의 `T_attrib`로 귀속 강도를 구분한다.
  **⚠ AND다.** `reserved`만 0이 되고 `count`가 불변이면 재개가 아니라 **비균형 종결**(N120)이며
  아래 `NO_RESUME_WITHIN_WINDOW`로 간다. 이 구분을 사후에 완화하지 않는다.
- **`NO_RESUME_WITHIN_WINDOW`** — ≥600tick 관측 **완주**했고 AND-3 전이가 **0건**.
  (비균형 종결·A 사망이 있어도 완주했다면 여기로 오며, 사유에 `unbalanced_termination_at_tick<N>` /
  `producer_a_died_at_tick<N>`을 남긴다.)
  ⇒ **H-place 지지. H-gate 반증은 아니다.** 후속은 §51대로 F2(배치 축 선배제)를 strategy에 재고 요청.
- **`PRECONDITION_NOT_MET`** — 위 둘이 성립할 수 없는 모든 경우. **사유 문자열 필수**이며 아래 표로
  사전 고정한다(새 사유를 실행 중에 만들지 않는다).

| 사유 | `detail` 예 | 의미 |
|---|---|---|
| `control_settlement_failed` | — | 2단계 대조 정산 실패 ⇒ 판정 근거 없음 |
| `order_not_accepted_5fold` | — | 3단계 수락 5중 신호 불성립 |
| `no_blockage_ge_t_block_observed` | `settled_at_tick<N>_without_headroom` | **H-gate 반대 증거 후보**: 구성 상태에서 정산이 그대로 진행(`used`→5005>cap). middle이 해석한다 |
| 〃 | `unbalanced_termination_at_tick<N>_before_preproof` | lap483 tick1943형 종결이 200tick 전에 발생 |
| 〃 | `producer_a_died_at_tick<N>_before_preproof` / `command_changed…` / `horizon_700_exhausted` | 연속성 파괴 또는 지평 소진 |
| 〃 | `progress100_not_reached_within_horizon` | 6단계 전건 미도달 |
| `op4_call2_rejected` | 콜 결과 | 콜#2 거부·범위 초과 |
| `ledger_reverted_by_engine` | 읽기 | 아래 R1′ 4번 위반 |
| **`sampling_gap_violation`** | 위반 구간 tick | **R-2 신규**: `CALL2_ENGINE_TICK ±10tick`에서 `READS` 간격 >3tick |
| `observation_incomplete` | 중단 사유·도달 tick·실측 경과 | 8단계 완주 실패 ⇒ 어느 라벨도 주장 불가. **R-5대로 이 경우 Q6-B 자동 종결** |

- **R1′ (§49 R1 대체, W28 승계 + R-3).** 주문 상태와 **무관하게 창 끝까지** 매 읽기의 `used` 이탈을
  다음으로 **분류**한다:
  1. `used` +비용(정확히 +10) **∧** `reserved`10→0 **∧** `count`+1 ⇒ **재개 신호**(위반 아님).
  2. `count` 감소 ⇒ **사망**(별도 이벤트 기록, 위반 아님). **정산 이후에도 검사한다(D3·N135).**
  3. `used` 감소 **∧** `reserved`10→0 **∧** `count` 불변 ⇒ **비균형 종결**(N120 서명, 기록, 위반 아님).
  4. 그 밖의 모든 이탈 ⇒ `PRECONDITION_NOT_MET`(사유 `ledger_reverted_by_engine`).
  **`used`가 비용만큼 증가하는 것을 위반으로 종결시키지 않는다**(N128 해소).

## 6. 안전·보고 의무

- **증분 기록.** `window_samples.jsonl` · **`reads.jsonl`(R-2 병합 읽기열)** · `events.jsonl`
  (death / finalization / unbalanced_termination / ledger_deviation)을 **읽기마다 append + flush**한다.
  종료 시 요약 JSON과 §3 R-3의 `event_crosscheck`를 별도로 쓴다.
  **빈 배열을 "사건 0건"으로 보고하지 않는다** — 관측 읽기 수와 함께 보고한다.
- **`run_summary`의 자동 `verdict`는 보조 기록일 뿐**이다. 라벨은 원시 필드로 재계산되어야 하며
  work는 라벨을 **확정하지 않는다**(§7). `call2_tick`류 파생 필드는 **엔진/표본 기준을 이름에 명시**한다
  (`call2_engine_tick` / `firing_sample_tick`) — lap491의 모호한 `call2_tick`을 반복하지 않는다.
- **background 금지**(INBOX 2026-09-21 01:01). 모델 세션이 직접 기다려 완주하고 산출물 갱신을 확인한
  뒤 회차를 끝낸다. N133대로 총 게임 시간은 1~2분 규모다.
- 원본 SHA 전후 확인, 후보/브리지 SHA 기록, 격리 prefix/Xvfb 전용, 잔류 프로세스 0 확인.
  **격리 prefix/display가 `/home/dev_00/.wine_syw2_baseline`·`:2`와 겹치지 않는지 먼저 확인**한다
  (§55 환경 관찰: 기원 UNKNOWN인 bare wine 프로세스. 붙거나 pkill 하지 않는다).
  **lap494 관측(조작·정리 없음): 살아 있는 Xvfb는 `:77 :78 :103 :186 :187`이고 `/tmp/.X*-lock`은
  `0 1 11 77 78 99 100 101 102 103 104 105 107 186 187 256`이 점유 중**이다(게임 exe·wine 프로세스는 0건,
  이 회차는 게임을 띄우지 않았다). **이 목록과 겹치지 않는 display를 고르고 남의 것을 정리하지 않는다.**
  lap491이 쓴 `:199`는 lock이 해제된 상태다.
- F4 게이트 유지, **사전 예외 1건**: op4 write 이후 `used > cap`는 이 실험이 만든 의도된 조건이므로
  abort 사유가 아니라 **측정값**이다. 음수·int16 wrap·포인터 손상은 즉시 STOP.
- **`used`가 실제 유닛 구성과 어긋난 의도적 장부 desync**임을 산출물 최상단에 명시한다.
  라벨은 "장부 구성 fixture"이며 cap 근접 안정성·G2 완료·W26 정량 근거로 재사용 금지.
- op4 배제 핀 3종을 **유지·수정·면제하지 않는다**(lap494가 3종 모두 현존 확인):
  `tools/runtime_env.py:5837` `"op4_used": False` / `tests/test_g2_stock_stress.py:20`
  `assert "request(4" not in SOURCE` / `tests/test_g2_eight_owner_setup.py:166` `"op4" not in block.lower()`.
- source 변경 0을 before/after(+git이 생긴 경우 git) 일치로 증명하고, 표적 테스트 +
  `checks/safety.sh check` + `checks/context_limits.py`만 수행한다(동일 source 면제, 2026-09-20 21:58
  지시 + N22). **이 저장소는 아직 `unborn` HEAD이므로 3자 일치의 git 항목은 해당 없음을 명시한다.**
  source를 바꿨다면 면제를 주장하지 말고 전체 게이트를 돌린다.
- 산출물: `temp/Syw2plus_patch/g2_capacity/<YYYYMMDD>_lap<실행lap>_w28r_settlement_blockage_preproof/`
  (원시 표본 JSONL, `reads.jsonl`, 이벤트 JSONL, run summary, 로그, 스크립트 사본, 각 SHA256).
  **lap 기록을 반드시 남긴다**(N64 재발 금지).

## 7. 이 카드가 닫히는 조건

- §4를 **1회** 실행 → middle이 **원시만으로** 재계산(`run_summary`의 `verdict`/`reason`/`exception`과
  work의 판정 스크립트·파생 보조 필드 미참조) → 라벨 확정 시 `CLOSED`.
- **R-5(§57):** 관측 완주가 다시 미달하면 **Q6-B로 자동 종결** —
  `PRECONDITION_NOT_MET`(`observation_incomplete`) 확정, **재재실행 없음**, 미달 원인을 §1 기전 보고에
  남기고 144k는 계속 닫는다. work는 미달을 감추거나 기준선을 바꿔 통과시키지 않는다.
- 차단 선입증 불성립으로 발사하지 못하면 `no_blockage_ge_t_block_observed` **1회 종결·재시도 없음**.
  `detail`이 `settled_at_tick<N>_without_headroom`이면 **H-gate 반대 증거**로 읽힐 수 있으므로
  middle이 별도로 해석하고 필요하면 strategy에 회부한다.

## 8. W26(144k) 재개방 조건 — §57-6이 운반한다

144k는 계속 닫혀 있다. **재개방 조건: W28-R의 ≥600tick 관측 완주(R-1 기준선) + middle 원시 독립검수
ACCEPT + 새 무결성 위반(음수·랩·풀 손상) 0.** 그 전에는 금지 유지이며, 충족 시 **라벨과 무관하게**
middle이 W26을 발행할 수 있다. W26 카드는 다음을 **반드시** 싣는다:

- **N120**(비균형 차감, 종결 1건당 유령 headroom 10, 자연 발생 여부 UNKNOWN),
  **N121·N124·N125**(임계 교정 결함과 확정 임계 `T_block=200`), **N123**(N68 미재현, H-gate/H-place 병존),
  **N126~N134**, 그리고 **N135**(무결성 분류기가 조용히 꺼진 결함)를 **미결 위험으로 명시 기재**.
- `used`/`reserved` 기반 수치는 정산 게이트 질문(§1)이 닫힐 때까지 **"부분 증거" 라벨 강제**.

## 9. 범위 밖 (모델이 착수하지 않는다)

- (ㄴ) G2 한정 최소 AI/설정 변경 — 사용자 전권 대기.
- lap404 (가)/(나) 전비 장부 pending 초과 마감 방식 — 사용자 전권 대기.
- F4 (B)/(C) — §38에서 (C) 채택 상태, 랩/음수 관측 시 즉시 STOP 후 (B) 재심.
- 3단 마일스톤 사용자 승인 — 모델의 기술 컨펌과 구분한다.
- **파라미터·판정식·라벨의 어떤 변경도 범위 밖이다(R-4).** 고치는 것은 R-1·R-2·R-3 셋뿐이다.
