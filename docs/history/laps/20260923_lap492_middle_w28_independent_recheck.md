# 2026-09-23 | lap 492 | 목표 G2 (W28 독립 재계산)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high — **middle(중간 tier: 진단·계획·확인)**.
  게임 코드 hands-on 수정 없음. 게임 실행 0회(이번 회차는 검수 회차이며 카드가 요구하는 실행은 lap491이 이미 1회 소진).
- 가설 / 사용자 관찰: STATUS「다음 한 가지」대로, lap491(work)이 산출한 W28 라벨
  `SETTLEMENT_RESUMED_AFTER_HEADROOM`을 카드 §7 의무에 따라 **원시만으로** 재계산해 확정 가능한지 본다.
- 예상 PASS / FAIL 조건: 카드 §5 사전 고정 판정식을 원시 1차 필드에만 적용한 결과가 work 라벨과
  일치하면 라벨 확정(`CLOSED`) + §8 W26 재개방 조건 판정. 불일치하면 정정하고 근거를 남긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  제품 source 변경 **0**. 이번 회차가 만든 것은 temp 분석 스크립트와 문서뿐이다.
  - 신규(temp): `temp/Syw2plus_patch/g2_capacity/20260923_lap492_middle_w28_independent_recheck/recheck_lap492.py`
    (SHA256 `772aaf99f51d5bcb620125485212cd8a830353b92a01d7b9d40b0f2772d7e96c`),
    `recheck_lap492_result.json` (SHA256 `417d11c1f79bfc4c4cc303540ee8a682285acdc5725cb5b9c3d77cc5751fcf80`).
  - 신규(repo, 문서만): 이 lap 기록, `docs/STATUS.md`·`docs/feedback/INBOX.md`·`loop/ESCALATE_SOL` 갱신.
  - 불변 확인: `patches/population/runtime_bridge.c` `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
    `tools/inmm_stub/control_executor.c` `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`,
    `tools/runtime_env.py` `7418dcdfd4391ad46a9c2ffe202b0f0a37ac11a82e8822b02b150470606f90ec`.
  - 커밋 **0**(`LOOP_ALLOW_COMMITS` 미허용, 저장소는 여전히 `unborn` HEAD — "No commits yet on main").
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  이번 회차는 게임을 띄우지 않았다. 검수 대상 run의 fixture는 lap491 기록과 동일하며,
  **장부 구성 fixture**(`used`가 실제 유닛 구성과 어긋난 의도적 desync)임을 그대로 승계한다.
  cap 5000, owner0, producer A type46이 type7(비용10) 1건 생산, count_cap 250.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 recheck_lap492.py` (위 temp 디렉터리). 입력 원시 SHA256:
    `window_samples.json` `a9802a5fe5bab77af8dcd359a15865f5d9787b70f42987483043579d525f88f0`,
    `positive_control_samples.json` `fde5b069a8ac891814b1ed508731f5e08ae0834c9f8fe1e971356c46a9811995`,
    `events.jsonl` `6fbcb01d07830db9f5fcf1b877fc430fa6abbc7970600770cc1f5c65526808b7`,
    `supply_probe_call_log.json` `85c7aab9adb254341f98eb685e1c01cc6d3b33af9e5a6caa80d15105e32cb0d8`,
    work 스크립트 `w28_…_counterfactual.py` `11c49ecbacdcab9040a25815e59a268803923818e00a1083b892afd81d9c8981`.
  - **§7 준수:** `run_summary.json`의 `verdict`/`reason`/`exception`과 work의 판정 로직을 읽지 않았다.
    work가 파생해 둔 보조 필드(`streak_ticks`/`transition`/`order_a_finalized`/`headroom`/`phase`/
    `call2_fired`/`ledger_reverted_so_far`/`producer_a_stall_ticks`)도 **입력에서 배제**하고,
    원시 1차 필드(`tick,used,reserved,count,cap,producer_a_command,producer_a_progress,
    producer_a_survival.alive,rice,wood`)와 원시 콜 로그만으로 재계산했다.
  - 게이트: 표적 186 passed(`test_runtime_env`/`test_g2_eight_owner_setup`/`test_g2_stock_stress`/
    `test_g2_stock_lifecycle`/`test_g2_official_creation`), `SAFETY_PASS`, `CONTEXT_PASS`.
    source 변경 0이므로 784 전체는 재실행하지 않았다(2026-09-20 21:58 지시 + N22; **이번 회차는
    source를 바꾸지 않았다**). op4 배제 핀 3종 현존 재확인(`tools/runtime_env.py:5837` `"op4_used": False`,
    `tests/test_g2_stock_stress.py:20` `assert "request(4" not in SOURCE`,
    `tests/test_g2_eight_owner_setup.py:166` `"op4" not in block.lower()`).

## 측정값 / 판정

### A. work와 일치하는 부분 (측정 재현 성공)

- **차단 선입증 성립.** `t0` = progress100 최초 표본 tick **1414**(sample 255) → tick **1615**(sample 329)에서
  `tick − t0` = **201 ≥ `T_block`200**. 그 구간 **75표본 전수**가 5중 신호를 만족한다:
  `alive` 550/550 · `progress==100` 전부 · `reserved==10` 전부 · `command==15` 전부 ·
  `count==5`(미정산) 전부 · `used==4995` 전부 · `used+reserved`는 **오직 5005**(전 표본 cap 초과).
  구간 내 최대 표집 간격 **3tick**(요건 충족). 연속성 파괴 없음.
- **op4 정확히 2콜**(R2′ 준수). 전체 816콜 히스토그램 `{7:1, 6:2, 1:2, 0:809, 4:2}`.
  콜#1 엔진 tick **718**: `{used70,reserved10,count5}` → `{used4995,reserved10,count5}`.
  콜#2 엔진 tick **1618**: `{4995,10,5}` → `{4980,10,5}`. 둘 다 `ok=true/executed`.
- **AND-3 재개 전이 1건 관측**(단, 아래 D2 단서 필요): `{used4980, reserved10, count5}`(콜#2 after 블록,
  엔진 tick1618) → `{used4990, reserved0, count6}`(표본 330, tick**1620**). `reserved`10→0 ∧
  `used`+정확히10 ∧ `count`+1 전부 성립. 비균형 종결(N120 서명)이 아니다.
- **무결성 위반 0:** 음수 표본 0, int16 wrap 표본 0, R1′ 미분류 장부 이탈 **0건**
  (⇒ `ledger_reverted_by_engine` 0), 비균형 종결 0건, A 생존 550/550.
- **양성 대조 재현:** `L`(주문→정산) = **702tick**(tick8→710), progress100 최초 표본 tick707 →
  정산 표본 tick710 ⇒ **표본 tick 기준 지연 3tick**, `control_delay_resolution_ticks` **3**,
  정산 전이 `{used40→50, reserved10→0, count3→4, command15→1}`. 표집 간격 min2/max3/mean2.742(요건 충족).

### B. work 보고와 어긋나는 부분 (정정 3건)

- **D1 (라벨을 뒤집는 정정) — 콜#2 엔진 tick은 1615가 아니라 1618이다.**
  원시 `supply_probe_call_log.json`의 op4 콜#2는 `tick_before=1618`·`tick_after=1618`이다.
  **1615는 발사 전건이 충족된 마지막 표본 tick**일 뿐 엔진 tick이 아니다(콜#1도 엔진 tick718 vs
  첫 표본 tick720으로 같은 관계다). 카드 §3·§4-8은 관측 완주 기준선을 **"콜#2 엔진 tick"**으로
  명시 고정했다. 그 기준선으로 계산하면 마지막 표본 tick2216 − 1618 = **598tick < 600tick**이다
  (work의 601은 1615 기준). ⇒ §4-8 관측 완주 요건 **미충족(2tick 부족)**,
  §5 문언상 라벨은 `PRECONDITION_NOT_MET`(사유 `observation_incomplete`).
  파생 정정: `resume_delay_ticks`는 **2tick**(1620−1618)이며 work/`events.jsonl`의 5는 1615 기준이다.
  귀속 강도는 어느 기준이든 `T_attrib`50 이내이므로 **강함**으로 동일하다.
- **D2 (라벨 도달 경로의 단서) — `used=4980`은 어떤 window 표본에도 없다.**
  §5의 AND-3은 `used` **4980→4990**으로 값까지 고정돼 있는데, 창 내 표본만으로 탐지하면
  AND-3은 **0건**이다. 표본에 기록된 전이는 tick1615 `{4995,10,5}` → tick1620 `{4990,0,6}`
  (`used`가 4995에서 4990으로 **감소**)뿐이다. §5를 만족시키려면 **콜#2 after 블록(엔진 tick 기록이
  있는 장부 읽기)을 "연속 두 읽기"의 첫 읽기로 포함**해야 한다. 카드 §4-7이 콜의 tick과 before/after
  블록 기록을 의무화하고 §5가 "콜#2 직후 재읽기도 탐지 창에 포함"을 적었으므로 그 포함이 카드의
  의도로 읽히지만, **문언이 "표본"과 "읽기"를 구분하지 않아 확정적이지 않다.**
  더구나 재개는 **1615→1620의 5tick 간격** 안에서 일어났고 이는 §3의 **≤3tick 표집 요건을 위반한
  유일한 구간**이다(창 전체 min2/max**5**/mean2.725, 위반 1건, 그 외 최대 3tick).
  ⇒ 재개 시점은 표본만으로는 **[1615,1620] 5tick 창**으로만, 콜 after 블록을 쓰면 2tick으로만 분해된다.
- **D3 (보고 정정, 라벨 무영향) — 사망 0건이 아니라 1건이다.**
  표본 448 tick1941 `{used4990, count6}` → 표본 449 tick**1944** `{used4970, count5}`:
  `count` −1 ∧ `used` −20. R1′ 2번(사망)으로 분류되어 **위반은 아니지만**,
  `death_events.json`은 `[]`이고 lap491 기록·STATUS·INBOX는 **"사망0"**으로 보고했다.
  카드 §6이 금지한 "빈 배열을 사건 0건으로 보고"에 해당한다. 관측은 이 사망에서 멈추지 않았다
  (§4-8 취지는 이 부분에서 충족). `used`가 −20인데 정산 유닛 비용은 10이므로 **죽은 개체는 그 유닛이
  아니다**(구성 fixture의 다른 개체). 이 run의 "정산된 유닛이 이후 살아남았는가"는 **미측정**이다.

### C. N132(대조군 차단 predicate 히트) 해석 — middle 판정

히트 **1건**을 재현했다(표본255, tick707, `{progress100, reserved10, command15, count3}`).
**그러나 "기대 0"이라는 N132의 서술 자체가 부정확했다.** 정산 지연이 표본 tick 기준 3tick이고
표집 간격이 3tick이면 progress100과 정산 사이에 과도상태 표본이 **최대 1개 들어오는 것이 정상**이다.
lap487 대조군에서 0건이었던 것은 특이도가 아니라 **표집이 더 성겼기 때문**(mean 3.353)으로 읽어야 한다.

올바른 비교량은 히트 **존재**가 아니라 **연속 지속 길이**다. 같은 척도(첫 progress100 표본 tick 기준
연속 성립 구간)로 재계산하면:

| | 차단 predicate 연속 지속 | 표본 수 |
|---|---|---|
| 양성 대조(건강한 정산) | **0 tick** (tick707 1표본, tick710에 `reserved`0·`command`1로 깨짐) | 1 |
| 차단 창(구성 상태) | **201 tick** | 75 |

⇒ 분리는 오히려 **더 선명**하다. **N132를 다음과 같이 정정해 승계한다:** 건강한 정산 경로도 차단
predicate를 **1표본까지** 만들 수 있으며 그 지속은 정산 지연에 묶여 `[0,3]tick`을 넘지 않는다.
차단의 판별자는 히트 유무가 아니라 **`T_block` 이상 지속**이다(N124가 고른 임계의 사후 정당화).
이 정정은 lap491의 선입증을 **약화하지 않고 강화**한다.

### D. 라벨 판정

- 카드 §5 사전 고정 판정식을 **카드가 지정한 기준선(콜#2 엔진 tick)으로 문언 그대로** 적용한 기계 산출:
  **`PRECONDITION_NOT_MET` / `observation_incomplete`** (598tick, 2tick 부족).
- 관측 완주 요건만 충족됐다면 나왔을 라벨: **`SETTLEMENT_RESUMED_AFTER_HEADROOM`**(귀속 강함, 2tick).
  실험의 실질(차단 201tick 선입증 → headroom 회복 → 2tick 내 정산 재개)은 **재현 불일치 0으로 확인**됐다.
- **middle은 이 라벨을 확정하지 않는다.** 아래 판정 불가 사유 참조.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **판정 불가 사유(= 이번 회차 escalate 근거).** 두 선택지가 모두 계약을 해친다:
  (a) work 라벨을 확정하면 카드가 **사후 변경 금지**로 못 박은 기준선을 2tick 부족한 실측에 맞춰
  사실상 완화하는 것이다. 이 계보가 lap487→lap488에서 정확히 이 실패(판정식 사후 재해석)를
  REJECT했다. (b) `PRECONDITION_NOT_MET`으로 종결하면 §7의 "1회 종결·재시도 없음"이 걸려,
  **실질적으로 답이 나온 실험을 2tick 때문에 영구히 닫는다.** 어느 쪽도 middle 권한 밖이다.
- **§8 W26(144k) 재개방 조건은 현재 충족되지 않는다.** §8이 "발사했으면 8단계 **≥600tick** 관측 완주
  포함"을 명시했고 실측은 598tick이다. 측정 ACCEPT(불일치 0)와 새 무결성 위반 0은 충족했으나
  완주 항목이 미충족이므로 **middle은 W26을 발행하지 않는다.** 이 판단도 strategy 처분에 종속된다.
- 남은 위험: (1) D2대로 재개 시점이 ≤3tick으로 분해되지 않은 유일한 구간에서 발생했다.
  (2) D3대로 work의 이벤트 기록기가 사망을 놓쳤다 — 같은 기록기가 만든 다른 "0건" 주장
  (`unbalanced_termination_events.json` `[]`)도 **표본 재계산으로만** 0건임을 확인했다(본 회차가 확인함).
  (3) 정산된 유닛의 사후 생존은 미측정(D3).
  (4) 이 결과는 **장부 구성 fixture**의 기전 probe이며 cap 근접 안정성·G2 완료·W26 정량 근거로
  재사용 금지(§51 R2′ 승계) — 변함없다.
- 독립 검수 상태: 이 회차가 lap491에 대한 **2단 독립 검수**다. 측정은 ACCEPT(재현 불일치 0),
  라벨 확정은 보류. 3단 사용자 마일스톤 승인은 없음.
- (ㄴ)·lap404 (가)/(나)·F4 (B)/(C)·3단 마일스톤 승인은 전부 **사용자 전권 대기** 그대로다.

## 다음 한 가지

**strategy(Astra 또는 Fable5)가 `loop/ESCALATE_SOL` §56의 Q6 하나를 판정한다** — W28을 (Q6-A) 실질
완주로 인정해 `SETTLEMENT_RESUMED_AFTER_HEADROOM` 확정·`CLOSED`·§8 재개방 허용, (Q6-B) 기준선 위반으로
`PRECONDITION_NOT_MET` 확정·종결·§8 계속 닫음, (Q6-C) 기준선 오적용을 카드 결함으로 보고 **관측 완주만**
다시 받는 최소 재실행 1회 허용(W28-R) 중 하나. 모델이 대신 고르지 않는다.
