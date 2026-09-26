# W28 — 차단 선입증 + 정산 재개 counterfactual: H-gate vs H-place 판별 (lap490 middle 발행)

- 발행: lap490 middle (Claude Code claude-opus-5 / high), 2026-09-23 00:0x KST
  (재계산은 2026-09-22 23:5x에 시작해 자정 경계를 넘었다 — temp 디렉터리 이름은 `20260922_…`이다).
- 상태: **`SUPERSEDED_BY_W28R`** — 2026-09-23 lap494 middle이 `loop/ESCALATE_SOL` §57(Q6-C) 경계대로
  `G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_R_LAP494.md`(W28-R)를 발행했다. **이 카드를
  재실행하지 않는다** — 카드가 요구한 게임 1회는 lap491이 소진했고, lap492·lap493이 그 측정을
  **ACCEPT**(재현 불일치 0)했으나 완주 기준선 오적용(D1, 598<600)·"읽기" 문언 미확정(D2)·사망 기록
  경로 결함(D3)으로 **라벨은 확정되지 않았다**. 후속은 전부 W28-R이 운반한다.
  (원래 상태 표기 원문 보존: “상태: **`READY_FOR_WORK`** (work = Claude Code claude-sonnet-5 / high,
  게임 **1회** 실행).”)
- 근거 경계: `loop/ESCALATE_SOL` §54 판정 **Q4=승인**(교정 counterfactual W28 재발행, op4 **정확히 2콜**).
  승계: §49 R1(→아래 §5에서 정정) · §51 R2′ · §52 임계 `T_block=200tick`(N124) · 라벨 3종.
- 선행: `G2_SETTLEMENT_RESUME_COUNTERFACTUAL_LAP486.md`(W27) `CLOSED`
  (라벨 `SETTLEMENT_RESUMED_AFTER_HEADROOM` 확정, **그러나 귀결 "⇒H-gate 확정"은 REJECT** — N127).
- **이 카드는 W27 카드 결함의 교정판이다.** W27 §4-6의 "+50tick 이내 발사"가 정상 정산 지연
  0~4tick 앞에서 **차단이 드러나기 전 개입을 강제**했고(N127), §5 R1 승계가 재개 신호(`used`+비용)를
  그 자체로 위반으로 만들어 **재개 라벨을 문언상 도달 불가능**하게 했다(N128). lap487 work의 실행
  준수는 정확했다 — 고칠 대상은 카드다.

## 1. 묻는 것

W27은 "정산이 cap을 재검사하는가"(§1)에 답하지 못했다. 재개는 관측됐지만 **개입 전에 주문이
막혀 있었다는 측정이 없어**(체류 2tick « `T_block`=200tick, 대조군 분해능 ~4tick) 재개가
H-gate인지 "애초에 막히지 않았음"인지 구분되지 않았다(N127).

이 카드가 묻는 것은 하나이며, W27과 달리 **전건을 먼저 측정으로 성립시킨다**:

> `used+reserved>cap` 상태에서 progress100 주문이 **`T_block`=200tick 이상 미정산으로 지속됨을
> 먼저 입증한 뒤**, `used`를 `cap−비용` 아래로 되돌리면 **정산이 재개되는가?**

- 재개 ⇒ **H-gate 지지(선입증이 성립했으므로 W27보다 강함)**. 차단 원인은 정산 단계의 cap 재검사.
  인과 귀속 강도는 §3의 `T_attrib`로 사전 구분한다.
- 미재개 ⇒ **H-place 지지. H-gate 반증은 아니다** — 대기 중 이미 포기했을 가능성이 남는다.
- 차단이 애초에 200tick에 도달하지 않으면 §5대로 **1회 종결**하고 재시도하지 않는다.

**이 카드는 기전 probe이지 G2 안정성 증거가 아니다.** 결과를 cap 근접 안정성·제품 완료·W26 정량
근거로 재사용하지 않는다(§51 R2′ 승계).

## 2. 실행 전 확정된 입력 (lap490 middle이 원시만으로 독립 재계산)

`run_summary`의 `verdict`/`reason`/`exception`과 lap487/488/489 **서술을 참조하지 않고** lap483·lap487
원시 JSON만 재계산했다. 스크립트·결과:
`temp/Syw2plus_patch/g2_capacity/20260922_lap490_middle_w28_issue/`
(`recheck_lap490.py`, `recheck_lap490_result.json`).

**lap483(W25) 원시 — 차단이 `T_block`을 넘는다는 전제의 근거:**
- `window_samples` `420dfe5e…`, 스크립트 `46f8da26…` (SHA 일치).
- 350표본 tick 719~3052, **표집 간격 min 6 / max 7 / mean 6.685tick**(W28은 ≤3tick으로 올린다).
- 전수 주사 장부 전이 **정확히 2건**: tick1943 `{4995,10,5}→{4985,0,5}`(비균형 차감, N120·N122),
  tick2270 `{4985,0,5}→{4975,0,4}`(사망).
- progress100 최초 tick**1414** → 종결 tick**1943** = **체류 529tick**(= `T_block`의 2.6배).
  그 구간 **79표본 전부** `alive`·`hp3600`·`progress==100`·`command==15`·`reserved==10`·
  `used==4995`·미정산(N125 재현, 불일치 0).
- **(N134 신규)** `progress==100` 표본은 종결 **이후에도** tick3052까지 이어져 총 246건이다
  ⇒ `progress==100` 단독은 "주문 계류" 신호가 아니다. 차단 판정은 **5중 신호 연접만** 쓴다.

**lap487(W27) 원시 — 무엇이 빠졌는지:**
- `window_samples` `75a1cb83…`, `supply_probe_call_log` `42202061…`, 스크립트 `a5182ac3…`.
- 260표본 tick 712~1408, **표집 간격 min 2 / max 3 / mean 2.687tick**(≤3tick 요건은 이미 충족).
- `progress==100` 표본 **정확히 1건(tick1408, 마지막 표본)**, `call2_fired=true` 표본 **0건**,
  A 생존 260/260 ⇒ **§4-7 관측 미실행**(N130 재현).
- 477콜 히스토그램 `{0:470, 1:2, 4:2, 6:2, 7:1}` ⇒ **op4 정확히 2콜**(R2′ 준수).
- op4 콜#1: 엔진 tick710 `{used70,reserved10,count5}→{used4995,reserved10,count5}`.
- op4 콜#2: 엔진 tick**1410** `before {4995,10,5}` → `after {4980,10,5}` = **아직 재개 전**.
  재개는 tick 없는 재읽기 `{used4990, reserved0, count6}`에서만 보인다(N126 재현).
  - **(N131 정정)** `ESCALATE_SOL`§54의 spot-check 서술 "콜#2 엔진 사후블록 tick1410
    `{used4995,reserved10,count5}`"는 원시의 **before** 블록을 옮겨 적은 것이다. 원시 **after**는
    `{used4980, reserved10, count5}`다. 둘 다 "재개 전"이므로 **판정 무영향**이며 lap488/STATUS
    서술이 원시와 일치한다.
- 스크립트 자기모순 확인: `w27_…py:745~754`가 콜#2 직후 재읽기에서 `used != 4980`이면
  `RuntimeError`를 던진다 — 재개 신호(`used`=4990)가 곧 예외 조건이었다(N128 재현).
  그 예외로 post-call2 표본이 **0건**이 됐고 세 이벤트 배열이 `[]`가 됐다(N129 재현, "사건 0건" 아님).
- 대조군 지연 정의 결함 확인(`:454`): `pc_end_tick 703 − pc_progress100_tick 702 = 1`은 루프 종료
  **재읽기** tick 기준이다. **표본 tick 기준 정답은 0tick** — 표본207(tick702)이 `progress==100`과
  정산(`reserved`10→0·`used`40→50·`count`3→4)을 **같은 표본**에 담고 직전 표본은 tick698
  (`progress==99`)이다. 대조군 표집 간격 min 3 / max 4 / mean 3.353tick ⇒ **참 지연은 `[0,4)`**.
- **(N132 신규)** 그 대조군에서 **차단 predicate(progress100 ∧ `reserved`==10 ∧ `command`==15 ∧
  미정산) 표본은 0/208**이고, 정산 표본에서는 `producer_command`가 15→1로 함께 바뀐다
  ⇒ 건강한 정산 경로는 이 predicate를 **한 표본도** 만들지 않는다(특이도 지지).
  따라서 lap483의 79표본 연속 성립은 대조군 대비 이례적이다. W28은 이 특이도 검사를
  **run 내에서** 반복한다(§4-2).
- **(N133 신규)** 실측 tick 속도 = pending 구간 698tick / 21초 ≈ **33tick/s**
  ⇒ 차단 선입증 200tick ≈ **6초**, 사후 관측 600tick ≈ **18초**. §54의 관측 완주 의무는
  벽시계 비용이 사실상 무료다(기존 cap 600s가 충분). 또한 lap483 종결은 발사 예정 시점(+200)보다
  **약 329tick 뒤**이므로 무재개 경로에서도 종결 전에 `NO_RESUME_WITHIN_WINDOW`의 200tick 요건이
  충족된다 — 단 **완주를 위해 종결·정산·사망에서 표집을 멈추지 않는다**(§4-7).

## 3. 고정 파라미터 (사후 변경 금지)

| 이름 | 값 | 근거 |
|---|---|---|
| `T_BLOCK_TICKS` | **200** | N124 확정 임계(§52). 발사 전건과 무재개 판정에 동일 적용 |
| `T_ATTRIB_TICKS` | **50** | 인과 귀속 구간(아래) |
| `OP4_CONSTRUCT_USED` | **4995** | `used+reserved=5005>cap`, W25/W27과 동일 구성 |
| `OP4_COUNTERFACTUAL_USED` | **4980** | `used+비용=4990 ≤ cap 5000`, 여유 10 |
| `ORDER_COST` / `ORDER_TYPE` | **10 / 7** | W25·W27 승계 |
| `BLOCKAGE_WATCH_HORIZON_TICKS` | **700** (progress100 최초 표본 tick 기준) | lap483 종결 529tick을 덮는 값(§54 의무) |
| `WINDOW_AFTER_CALL2_TICKS` | **600** (=3×`T_block`, op4 콜#2 **엔진 tick** 기준) | §54 관측 완주 |
| 표집 간격 | 대조군·차단감시·사후관측 **모두 ≤3tick**(poll 0.03s 권장) | N127·N132 |

**인과 귀속(사전 고정):** AND-3 재개 전이가 콜#2 엔진 tick으로부터 `≤T_ATTRIB`(50tick)에서
관측되면 귀속 **강함**, 50tick 초과~600tick 이내면 귀속 **약함**(lap483의 자연 종결 시각대와
겹칠 수 있으므로 middle이 별도 판정). 라벨은 어느 쪽이든 동일하며 `resume_delay_ticks`를 남긴다.

## 4. 실행 절차 (게임 **1회** · source 변경 0 · 새 스크립트는 temp에만)

`temp/.../20260922_lap487_w27_settlement_resume_counterfactual/w27_settlement_resume_counterfactual.py`
(`a5182ac3…`)의 환경·goal·안전 골격을 **복사해** 새 스크립트를 만든다. 저장소 source는 건드리지 않는다.
**아래 1~5는 W27과 동일하고, 교정은 2·5·6·7·8과 §5에 있다.**

1. 후보 기동 → PS3 → `cap==5000` 확인 → op7로 rice/wood 1,000,000.
2. **양성 대조(정산 경로 생존 + predicate 특이도).** 버리는 producer PC(op6, type46)에 낮은 `used`에서
   op1(type7, cost10) 1건. **표집 간격을 차단감시와 동일한 ≤3tick으로 올린다**(교정5의 전제).
   기록 의무:
   - `L` = 주문→정산 tick, **그리고 `progress100 표본 tick → 정산 표본 tick` 지연**을
     **표본 tick만으로** 계산한다(`:454` 결함 제거, 루프 종료 재읽기 tick 금지).
   - `control_delay_resolution_ticks` = 정산 표본 tick − 직전 표본 tick (분해능 공개).
   - **차단 predicate(progress100 ∧ `reserved`==10 ∧ `command`==15 ∧ 미정산) 표본 수**(기대 0, N132).
   정산이 안 되면 즉시 `PRECONDITION_NOT_MET`(사유 `control_settlement_failed`).
3. 표적 producer A(op6, type46)에 **낮은 `used`(실효 headroom ≫ 비용)** 에서 op1 1건.
   수락 판정은 `reserved` 0→10 **그리고** rice −800 동시 확인(N107 5중 신호).
4. **op4 콜 #1 (구성).** 수락 확인 직후(progress<100, ≤0.25·`L` 이내) `used = 4995`를 쓰고
   rice/wood 1,000,000을 같이 넘겨 자원을 보존한다. before/after 장부와 **엔진 tick**을 기록한다.
   `used+reserved = 5005 > cap`이 W25/W27과 동일한 구성이다.
5. **차단 감시 표집(≤3tick).** 매 표본에 `tick, used, reserved, count, rice, wood`,
   A의 `command/progress/production_type`, **A 생존 플래그**(op0 존재비트·owner·type 일치, N115),
   주문 미정산 추적값(N114), `phase`를 남긴다.
6. **발사 전건 = 차단 선입증(교정1, W27 "+50tick" 폐기).** progress100 최초 표본 tick을 `t0`으로
   두고, `t0` 이후 **모든 표본이 연속으로** 5중 신호
   (`alive` ∧ `progress==100` ∧ `reserved==10` ∧ `command==15` ∧ 주문 미정산)를 만족한 상태에서
   `현재 표본 tick − t0 ≥ T_BLOCK_TICKS(200)`가 되는 **첫 표본 직후** op4 콜#2를 발행한다.
   - 연속성이 깨지거나(정산·종결·사망·`command` 변화) `t0 + 700tick`까지 200tick에 도달하지 못하면
     **발사하지 않고** §5의 `PRECONDITION_NOT_MET`(사유 `no_blockage_ge_t_block_observed`)로
     **1회 종결**한다. `detail`에 깨진 사유와 tick을 남긴다(§5 표 참조).
   - `progress==100`이 pending 안전 cap(4000tick / 600s) 내에 오지 않으면 같은 라벨,
     `detail=progress100_not_reached_within_horizon`.
7. **op4 콜 #2 (counterfactual) + 재읽기 기록(교정3).** `used = 4980`을 쓰고 rice/wood는 보존한다.
   - 콜의 엔진 `tick_before`/`tick_after`와 before/after 블록을 그대로 기록한다.
   - **직후 재읽기를 `tick`과 함께 하나의 표본으로 기록**한다
     (`phase="post_call2_immediate_reread"`). **이 재읽기 결과로 예외를 던지지 않는다** —
     `used`=4990은 §5의 재개 신호이고 위반이 아니다(N128 해소).
   - 콜#2가 거부되면 `PRECONDITION_NOT_MET`(사유 `op4_call2_rejected`).
8. **관측 완주(교정3·N130 해소).** 콜#2 **엔진 tick**부터 `현재 tick − call2_tick ≥ 600`이 될 때까지
   ≤3tick 간격으로 **계속** 표집한다. **정산·비균형 종결·A 사망·AND-3 전이 관측에서 멈추지 않는다.**
   중단은 안전 STOP(음수·int16 wrap·포인터 손상), 게임 프로세스 종료, 벽시계 cap뿐이며 그 경우
   라벨은 `PRECONDITION_NOT_MET`(사유 `observation_incomplete`, `detail`에 사유·도달 tick).

**op4는 정확히 2콜**(4단계 1 + 7단계 1). 그 외 어떤 경로로도 op4를 쓰지 않는다(§51 R2′).

## 5. 사전 고정 판정식 (라벨 3종만. 1회 종결, 재시도·파라미터 변경 재실행 없음)

- **`SETTLEMENT_RESUMED_AFTER_HEADROOM`** — 콜#2 이후 600tick 관측 **완주** 안에서, tick이 기록된
  연속 두 읽기 사이에 **AND-3 전이**를 1건 이상 관측:
  `reserved` 10→0 **그리고** `used` 4980→**4990**(= 정확히 +비용 10) **그리고** `count` +1.
  (콜#2 직후 재읽기도 이 탐지 창에 **포함**한다 — lap487에서 재개가 거기서만 보였다.)
  ⇒ **차단 선입증(≥200tick)이 성립한 상태의 재개이므로 H-gate 지지가 W27보다 강하다.**
  `resume_delay_ticks`(콜#2 엔진 tick 기준)를 남기고 §3의 `T_attrib`로 귀속 강도를 구분한다.
  **⚠ AND다.** `reserved`만 0이 되고 `count`가 불변이면 재개가 아니라 **비균형 종결**(N120)이며
  아래 `NO_RESUME_WITHIN_WINDOW`로 간다. 이 구분을 사후에 완화하지 않는다.
- **`NO_RESUME_WITHIN_WINDOW`** — 콜#2 이후 600tick 관측 **완주**했고 AND-3 전이가 **0건**.
  (비균형 종결·A 사망이 있어도 완주했다면 여기로 오며, 사유에
  `unbalanced_termination_at_tick<N>` / `producer_a_died_at_tick<N>`을 남긴다.)
  ⇒ **H-place 지지. H-gate 반증은 아니다** — 대기 중 이미 포기했을 가능성이 남는다.
  후속은 §51대로 F2(배치 축 선배제)를 strategy에 재고 요청한다.
- **`PRECONDITION_NOT_MET`** — 위 둘이 성립할 수 없는 모든 경우. **사유 문자열 필수**이며
  아래 표로 사전 고정한다(새 사유를 실행 중에 만들지 않는다).

| 사유 | `detail` 예 | 의미 |
|---|---|---|
| `control_settlement_failed` | — | 2단계 대조 정산 실패 ⇒ 판정 근거 없음 |
| `order_not_accepted_5fold` | — | 3단계 수락 5중 신호 불성립 |
| `no_blockage_ge_t_block_observed` | `settled_at_tick<N>_without_headroom` | **H-gate 반대 증거 후보**: 구성 상태에서 정산이 그대로 진행(`used`→5005>cap). middle이 해석한다 |
| 〃 | `unbalanced_termination_at_tick<N>_before_preproof` | lap483 tick1943형 종결이 200tick 전에 발생 |
| 〃 | `producer_a_died_at_tick<N>_before_preproof` / `command_changed…` / `horizon_700_exhausted` | 연속성 파괴 또는 지평 소진 |
| 〃 | `progress100_not_reached_within_horizon` | 6단계 전건 미도달 |
| `op4_call2_rejected` | 콜 결과 | 콜#2 거부·범위 초과 |
| `ledger_reverted_by_engine` | 표본 | 아래 R1′ 위반 |
| `observation_incomplete` | 중단 사유·도달 tick | 8단계 완주 실패 ⇒ 재개/무재개 어느 라벨도 주장 불가 |

- **R1′ (교정2, §49 R1을 대체).** 주문이 열려 있는 동안 매 표본 `used`를 기록하고, 마지막 op4
  기록값(콜#1 후 4995 / 콜#2 후 4980)에서의 이탈을 다음으로 **분류**한다:
  1. `used` +비용(정확히 +10) **∧** `reserved`10→0 **∧** `count`+1 ⇒ **재개 신호**(위반 아님).
  2. `used` 감소 **∧** `count` 감소 ⇒ **사망**(별도 이벤트로 기록, 위반 아님).
  3. `used` 감소 **∧** `reserved`10→0 **∧** `count` 불변 ⇒ **비균형 종결**(N120 서명, 기록, 위반 아님).
  4. 그 밖의 모든 이탈 ⇒ `PRECONDITION_NOT_MET`(사유 `ledger_reverted_by_engine`).
  **`used`가 비용만큼 증가하는 것을 위반으로 종결시키지 않는다**(N128 해소).

## 6. 안전·보고 의무

- **증분 기록(교정4, N129 해소).** `window_samples.jsonl`·`events.jsonl`(death / finalization /
  unbalanced_termination / ledger_deviation)을 **표본마다 append + flush**한다. 예외가 기록 경로를
  건너뛰어 배열을 비우는 일이 없어야 하고, 종료 시 요약 JSON을 별도로 쓴다.
  **빈 배열을 "사건 0건"으로 보고하지 않는다** — 관측 표본 수와 함께 보고한다.
- **`run_summary`의 자동 `verdict`는 보조 기록일 뿐**이다. 라벨은 원시 필드로 재계산되어야 하며
  work는 라벨을 **확정하지 않는다**(§7).
- **background 금지**(INBOX 2026-09-21 01:01; lap463·lap482 2회 위반). 모델 세션이 직접 기다려
  완주하고 산출물 갱신을 확인한 뒤 회차를 끝낸다. N133대로 총 게임 시간은 1~2분 규모다.
- 원본 SHA 전후 확인, 후보/브리지 SHA 기록, 격리 prefix/Xvfb 전용, 잔류 프로세스 0 확인.
- F4 게이트 유지, **사전 예외 1건**: op4 write 이후 `used > cap`는 이 실험이 만든 의도된 조건이므로
  abort 사유가 아니라 **측정값**이다. 음수·int16 wrap·포인터 손상은 즉시 STOP.
- **`used`가 실제 유닛 구성과 어긋난 의도적 장부 desync**임을 산출물 최상단에 명시한다.
  라벨은 "장부 구성 fixture"이며 cap 근접 안정성·G2 완료·W26 정량 근거로 재사용 금지.
- op4 배제 핀 3종을 **유지·수정·면제하지 않는다**(lap490이 3종 모두 현존 확인):
  `tools/runtime_env.py:5837` `"op4_used": False` / `tests/test_g2_stock_stress.py:20`
  `assert "request(4" not in SOURCE` / `tests/test_g2_eight_owner_setup.py:166` `"op4" not in block.lower()`.
- source 변경 0을 3자(before/after/git) 일치로 증명하고, 표적 테스트 +`checks/safety.sh check`+
  `checks/context_limits.py`만 수행한다(동일 source 면제, 2026-09-20 21:58 지시 + N22).
  source를 바꿨다면 면제를 주장하지 말고 전체 게이트를 돌린다.
- 산출물: `temp/Syw2plus_patch/g2_capacity/<YYYYMMDD>_lap<실행lap>_w28_settlement_blockage_preproof/`
  (원시 표본 JSONL, 이벤트 JSONL, run summary, 로그, 스크립트 사본, 각 SHA256).
  **lap 기록을 반드시 남긴다**(N64 재발 금지).

## 7. 이 카드가 닫히는 조건

- §4를 **1회** 실행 → middle이 **원시만으로** 재계산(run_summary의 `verdict`/`reason`/`exception`과
  work의 판정 스크립트 미참조) → 라벨 확정 시 `CLOSED`.
- 차단 선입증 불성립으로 발사하지 못하면 `PRECONDITION_NOT_MET`
  (사유 `no_blockage_ge_t_block_observed`) **1회 종결·재시도 없음**(§54).
  그 경우 `detail`이 `settled_at_tick<N>_without_headroom`이면 **H-gate 반대 증거**로 읽힐 수 있으므로
  middle이 별도로 해석하고 필요하면 strategy에 회부한다.

## 8. W26(144k) 재개방 조건 — §54가 §8을 대체 (이 카드가 운반한다)

144k는 계속 닫혀 있다. **재개방 조건:** W28이 카드 절차대로 **완결적으로 1회 종결**
(발사했으면 8단계 ≥600tick 관측 완주 포함, 발사 전건 불성립 종결이면 그 자체로 완주)
**+ middle 측정 ACCEPT + 새 무결성 위반(음수·랩·풀 손상) 0** ⇒ **라벨과 무관하게** middle이 W26을
발행할 수 있다. W26 카드는 다음을 **반드시** 싣는다:

- **N120**(비균형 차감, 종결 1건당 유령 headroom 10, 자연 발생 여부 UNKNOWN),
  **N121·N124·N125**(임계 교정 결함과 확정 임계 `T_block=200`), **N123**(N68 미재현, H-gate/H-place 병존),
  그리고 **N126~N134**를 **미결 위험으로 명시 기재**.
- `used`/`reserved` 기반 수치는 정산 게이트 질문(§1)이 닫힐 때까지 **"부분 증거" 라벨 강제**.

## 9. 범위 밖 (모델이 착수하지 않는다)

- (ㄴ) G2 한정 최소 AI/설정 변경 — 사용자 전권 대기.
- lap404 (가)/(나) 전비 장부 pending 초과 마감 방식 — 사용자 전권 대기.
- F4 (B)/(C) — §38에서 (C) 채택 상태, 랩/음수 관측 시 즉시 STOP 후 (B) 재심.
- 3단 마일스톤 사용자 승인 — 모델의 기술 컨펌과 구분한다.
