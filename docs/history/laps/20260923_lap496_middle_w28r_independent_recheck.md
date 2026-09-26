# lap496 (middle, Claude Code claude-opus-5 / high) — W28-R 원시 독립 재계산 → 라벨 확정 · W28-R `CLOSED` · W26 발행

- 날짜 / lap: 2026-09-23 KST / **lap496** (`loop/.lap_counter` = 496)
- 역할: **middle(중간계획·컨펌)**. 진단·검증·발행만 수행하고 **게임 구현·게임 실행은 하지 않는다.**
  게임 실행 **0** · 게임 코드 수정 **0** · 제품 source 변경 **0** · 커밋 **0**.
- 목표: `docs/STATUS.md`「다음 한 가지」 — lap495 산출물을 **원시만으로** 독립 재계산해
  W28-R(`docs/work/active/G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_R_LAP494.md`) §7
  종결 조건(라벨 확정 또는 `CLOSED`)을 판정하고, ACCEPT 시 §8에 따라 W26(144k) 재개방 여부를 판단한다.
- 가설: 없음(검수 회차). 카드 §5의 **사전 고정 판정식**을 원시에 그대로 적용해 라벨이 재현되는지만 본다.

## 1. 입력 격리 — `run_summary` 미참조 (카드 §7)

`run_summary.json`은 **한 번도 읽지 않았다.** 원시 파일에 섞여 있는 work 파생 보조 필드는 로드
시점에 전부 제거했다: `transition` / `streak_start_tick` / `streak_ticks` / `order_a_finalized` /
`order_a_unbalanced_terminated` / `call2_fired` / `ledger_reverted_so_far` / `headroom` / `phase` /
`producer_a_stall_ticks` / `producer_a_last_progress_change_tick`.
남은 입력은 `tick` / `used` / `reserved` / `count` / `rice` / `wood` /
`producer_a_command` / `producer_a_progress` / `producer_a_survival` / `settled_unit_survival`
와 op4 콜 로그의 `tick_before`·`tick_after`·`before`·`after` 블록뿐이다.

- 변경 파일: **저장소 source 변경 0.** 새 파일은 `temp/`의 재계산 스크립트 1개뿐:
  `temp/Syw2plus_patch/g2_capacity/20260923_lap496_middle_w28r_review/recheck_lap496.py`
  (sha256 `f9195ffe6cc4e056f98aed9275775c8d0838c1d21e565a88d5669b2a4ad4900b`).
  산출물 `recheck_lap496_result.json` (`e1230a606c691ac19614b99e8e219f9a37fb4052c352129e941ceeb69992b188`),
  `input_sha256.txt`. **uncommitted** (`unborn` HEAD, `LOOP_ALLOW_COMMITS=0`).
- 입력 SHA256(전부 lap495 기록값과 일치): `reads.jsonl` `24da5adf34a47f2366e675b61637f1e77486bb5a1bcd5c20d9e5fa482d7c91b0`,
  `window_samples.jsonl` `a466cbb01b447063c2c614a3f3d649e00913d2d6505b1ea6be2054cb27f22434`,
  `supply_probe_call_log.json` `75d29f5db68acdedd4c49c44737f854ef3aa552de3bbed6d7a3da3756b0c8dc2`,
  `events.jsonl` `d989d0f4e724b45f4bd97ac2ec785fa90c147a720bab7f9ab4eddb7cf3cf08de`,
  lap495 스크립트 `df535d937c1f2f31f0c6e2cc4731871cce380ee0af975b4c432a53b8b68fc56a`.
- 원본 SHA: `조선의반격 오리지날 실행.exe` = **`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`**
  (lap495 before/after 기록값과 일치). `patches/population/runtime_bridge.c` =
  `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
  `tools/inmm_stub/control_executor.c` = `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`
  — **둘 다 lap494·lap495 기록값과 일치(4바퀴 연속 source drift 0).**
- 실행 명령: `python3 recheck_lap496.py` (순수 재계산, 게임 미기동).

## 2. 수치 — 재현 불일치 **0**

| 항목 | lap496 독립 재계산 | lap495 보고 | 판정 |
|---|---|---|---|
| op4 콜 수 | **2** (806콜 중), r7 = 4995 · 4980, 둘 다 `ok/executed` | 2 | 일치 |
| `CALL2_ENGINE_TICK` | **1610** (`tick_before==tick_after`) | 1610 | 일치 |
| `reads.jsonl` | 546건 = 표본 542 + 콜 4블록, **독립 재조립과 완전 일치** | 546 | 일치 |
| 마지막 읽기 tick | **2220** ⇒ 2220−1610 = **610 ≥ 600** (완주 읽기 tick**2212**) | 610/610 | 일치 |
| AND-3 | **1건**: 콜#2 after(tick1610 `{4980,10,5}`) → 표본(tick1612 `{4990,0,6}`) | 1건 동일 | 일치 |
| `resume_delay_ticks` | **2** ≤ `T_attrib` 50 ⇒ 귀속 **강함** | 2 / strong | 일치 |
| `t0` (progress100 최초 표본) | **1406** | 1406 | 일치 |
| 선입증 streak | **≥200** (74표본 전수 5중 신호, 위반 **0**) | 201 | 일치(N137) |
| 표집 `CALL2±10` | 읽기 10건, 간격 전부 ≤3, 위반 **0** | 위반 없음 | 일치 |
| 창 전체 간격 | min **0** / max **4** / mean **2.7688** (표본만: min1/max4) | min1/max4/mean2.78 | 일치 |
| R1′ `ledger_reverted_by_engine` | **0건** | 0 | 일치 |
| `event_crosscheck` | death/finalization/unbalanced/ledger **4종 전부 일치** | 불일치 0 | 일치 |
| 정산 이후 사망 | tick**1943** `count`6→5, `used`4990→4970 — **포착됨** | 포착 | 일치(N135 회귀 통과) |
| 무결성 | 음수 **0** · int16 wrap **0** · 라이브 `used`>cap **0** | 0 | 일치 |
| `settled_unit_slot` | **1148** (type7/owner0/hp400), 221표본 전부 존재 | 1148 | 일치 |

## 3. 판정 — **측정 ACCEPT + 라벨 확정**

카드 §5 판정식을 원시로 재계산한 결과: 선입증 성립 ∧ 완주 610 ≥ 600 ∧ AND-3 1건 ∧ 표집 위반 0 ∧
R1′ 4번 0건 ⇒ **`SETTLEMENT_RESUMED_AFTER_HEADROOM`**(attribution=**strong**, `resume_delay_ticks`=**2**).
work 산출 라벨과 일치한다. **W28-R = `CLOSED`.**

§1 기전 질문의 답은 **H-gate 지지**다 — 차단(`used+cost>cap`에서 progress100 주문이 ≥200tick 미정산)을
**먼저 입증한 상태**에서 headroom을 되돌리자 2tick 만에 정산이 재개됐으므로, 차단 원인은
**정산 단계의 cap 재검사**다. W27보다 강하다(W27은 차단 자체가 측정되지 않았다 — N127).

**PASS / FAIL / SKIP:** 재계산 PASS · 라벨 확정 PASS · targeted **186 passed**
(`test_runtime_env` / `test_g2_eight_owner_setup` / `test_g2_stock_stress` / `test_g2_stock_lifecycle` /
`test_g2_official_creation`; **이번 회차 source 변경 0**이므로 전체 게이트는 2026-09-20 21:58 지시 + N22에
따라 재실행하지 않음) · `SAFETY_PASS` · `CONTEXT_PASS` · op4 배제 핀 3종 현존 확인 · 게임 실행 0 · 커밋 0.

## 4. fixture

lap495 실행분의 fixture를 그대로 검수했다: 후보 `fixed_supply_5000` `0a1da226…`, stock 1200-slot 레이아웃,
goal `_custom_game_chain_inject_g2_eight_seed42`, owner0 1인, cap=5000.
**`used`는 op4로 인위 desync시킨 장부 구성 fixture**이며 cap 근접 안정성·G2 완료·W26 정량 근거로
재사용 금지(R2′ 승계). 이 카드는 **기전 probe이지 G2 안정성 증거가 아니다.**

## 5. 신규 관측 — N136 ~ N140

전문은 `loop/ESCALATE_SOL` §59. 요지:

- **N136** — 확정된 기전이 **N68을 그대로 설명한다**(N68의 `used4995,reserved10`은 `used+cost 5005>cap`로
  W28-R 차단 조건과 동형). 단 W28-R은 op4 desync 기반이라 **자연 발생까지 증명하지 않았다**(N123 병존).
  W26 **(U6)**이 그 간극을 직접 측정한다. **lap404 (가)/(나)에 입력을 주지만 모델은 고르지 않는다.**
- **N137** (정정, 판정 무영향) — `firing_sample_tick`은 정의가 둘(트리거 표본 **1607**/skew−3 = 카드 문언
  기준으로 **work 값이 옳다**, `pre_call2_immediate` 표본 **1608**/skew−2). R-1이 기준선 사용을 금지하므로
  판정 무영향이고 streak도 201/202 둘 다 ≥200이다.
- **N138** — 대조군 차단 predicate 히트 **0건**(N132의 “≤1건”보다 강하다). 대조군은 progress100 표본에서
  `command`가 이미 15→1로 전이했다. 특이도: **0표본/0tick vs 74표본/≥200tick.**
- **N139** — 정산 유닛 slot1148은 창 끝까지 생존. tick1943 사망은 `used` −20이라 **정산 유닛이 아니다.**
- **N140** (문언 결함, 이번 run 무영향) — R1′를 `READS` 위에서 돌리면 **op4 자신의 write가 4번으로 분류된다.**
  R-2가 콜 블록을 읽기로 인정하면서 R1′ 제외를 문언화하지 않았다. 후속 카드는 반드시 제외를 명시한다.

## 6. 다음 행동

§8 재개방 3조건(완주 610 · middle ACCEPT · 무결성 위반 0)이 **전부 충족**돼 §57-6이 middle에 위임한
범위대로 **W26 발행**: `docs/work/active/G2_SEEDED_CAP_PROXIMITY_144K_SOAK_LAP496.md`(`READY_FOR_WORK`).
축은 W21 Step1과 같은 **gate-legal 시딩**, `STOP_TICK`=**144,000**, **op4 전면 금지**.
N120·N121·N123·N124·N125·N126~N134·N135를 미결 위험으로 명시 기재하고 `used`/`reserved` 수치에
“부분 증거” 라벨을 강제했으며, N65 verdict 식 수리 의무와 (U6) 관측 의무를 실었다.

**다음 한 가지: work(Sonnet5)가 W26을 게임 1회·foreground·동기로 실행**(벽시계 70~90분 규모 —
세션 시간이 부족하면 시작하지 말고 그 사실을 기록한다) → 다음 middle이 원시 독립검수.
**(ㄴ) · lap404 (가)/(나) · F4 (B)/(C) · 3단 사용자 마일스톤 승인은 전부 사용자 전권 대기이며 모델 착수 금지.**
