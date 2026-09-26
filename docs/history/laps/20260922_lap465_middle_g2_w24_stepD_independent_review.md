# 2026-09-22 | lap 465 | 목표 G2 — W24 Step D 독립검수 + Step C 유보 처분

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / **middle(중간계획·컨펌)**.
  게임 코드 hands-on 수정 없음. 게임 실행 **0회**. 커밋 **0**.
- 가설 / 입력: STATUS 「다음 한 가지」 = lap464 Step D 산출물을 **원시 재계산으로 독립검수**하고,
  ACCEPT 시 W24 CLOSED·144k 금지 해제 여부·Step C `RIDER_NO_REPRO`가 연 lap404(가) 재심
  (lap462가 남긴 **방법론 유보** 포함)을 함께 처분한다.
- 판정식: 카드 `G2_MIXED_COMPOSITION_COMBAT_CYCLE_SOAK_LAP461.md` §7(실행 전 고정). 재채점 금지.

## 0. 검수 방법 (비참조)

입력으로 **쓴 것**: `samples.jsonl`(715) · `census_c1/c2/c3.json` · `seed_receipts.json` ·
lap462 `type_table_inventory.json` · lap462 `step_c_run_summary.json` — 전부 원시 산출물.
입력으로 **쓰지 않은 것**: `run_summary.json`, `compute_verdict461.py`, `step_d_run.py`,
`w24_mixed_cycle_soak.md`, lap464 lap 기록 서술.

신규 `recheck465.py`(비참조, 카드 §7을 문자 그대로 구현) 작성 후 실행.
산출물 `temp/Syw2plus_patch/g2_capacity/20260922_lap465_middle_stepD_recheck/`
(`recheck465.py`, `recheck465_output.json`).

## 1. Step D 재계산 결과 — **ACCEPT (불일치 0)**

| 항목 | lap464 보고 | lap465 독립 재계산 | 일치 |
|---|---|---|---|
| 표본 수 | 715 | 715 | ✓ |
| `final_tick` | 24031 | 24031 | ✓ |
| tick 역행 | 0 | 0 | ✓ |
| fault/read failure | 0 | 0 (구조 결손 표본도 0) | ✓ |
| `live == Σcount` 불일치 | 0 (715/715) | 0 — `sum_count` 필드를 믿지 않고 owners에서 **직접 재합산** | ✓ |
| live `used > 5000` | 0 | 0 | ✓ |
| 랩/음수 | 0 | 0 | ✓ |
| `U1_pass` | true 8/8 | true 8/8 | ✓ |
| **`D`** | **12** | **12** | ✓ |
| **`R`** | **0** | **0** (공통슬롯 1,565 전수) | ✓ |
| **verdict** | **`NO_ENGAGEMENT`** | **`NO_ENGAGEMENT`** | ✓ |

부수 기록도 일치: max live 1626, 최소 rice 987,900 / wood 988,080,
`used+reserved>5000` **2,122** owner-표본, `vm_size` 단일값 3,463,232KB, `vm_swap` 전 구간 0,
RSS max 247,880KB@tick12,322 → final 183,636KB, 1MB+ 하강 **6건**(최대 −16,356KB@tick14,907).

### 1-1. 검수기 자체의 비공허성 (역주입 8건, lap441 선례)

내 `recheck465.py`가 공허하지 않음을 **직접 증명**했다 — 합성 입력에 대해 전부 기대대로 발화:

| 주입 | 결과 |
|---|---|
| (0) 원본 그대로 | `NO_ENGAGEMENT` D=12 R=0 |
| (a) tick 12,000 절단 | **`ARM_FAIL`** (이후 verdict 계산 안 함 — N86 수리 집행점) |
| (b) `used=5001` 1건 | **`CYCLE_UNSTABLE`** |
| (c) `live≠Σcount` 1건 | **`CYCLE_UNSTABLE`** |
| (d) 음수 장부 1건 | **`CYCLE_UNSTABLE`** |
| (e) 정합 유지한 사망 60건 + 재사용 1건 | **`CYCLE_STABLE`** (D=72, R=1) |
| (f) C3 `internal_id` 1건 변경 | R=**1** 로 정확히 반영 |
| (g) 시딩후 band 이탈 | `U1_pass=false` |

**(e)가 핵심이다**: 양성 분기 `CYCLE_STABLE`이 실제로 **도달 가능**함을 보였으므로,
`NO_ENGAGEMENT`는 판정기가 구조적으로 양성을 못 내는 탓이 아니라 **실측 결과**다.

### 1-2. 두 독립 채널의 상호 검증 (신규, lap464 미보고)

`D`(표본 `count` 차분)와 census(슬롯 전수)는 **서로 다른 계측 채널**인데 정확히 맞아떨어진다:

- `D`=12의 실체는 **단일 표본쌍**(sample606, **tick 20,410**)의 owner0 `201→197`(4) +
  owner2 `204→196`(8) 뿐이다. 분산된 소모가 아니라 **한 순간의 동시 사건**이다.
- C1에만 있고 C3에 없는 슬롯 = **12개**, owner 분포 **{owner2:8, owner0:4}** — `D` 사건과
  owner·기수가 **정확히 일치**. 즉 12기가 죽었고 그 자리는 24k 끝까지 **재사용되지 않았다**(R=0).
- lap448도 동형(tick10,587, 2 owner 동시, 4기)이었다 ⇒ 이 소모는 전투 순환이 아니라
  **반복되는 단발 사건**이라는 해석이 두 lap에서 일관된다.

`R=0`의 강도: 공통 1,565슬롯 중 `internal_id` 변경 **0건**, `owner` 변경 **0건**.

## 2. 신규 실측 — lap464가 보고하지 않았거나 잘못 귀속한 것

### (N91) `w24_mixed_cycle_soak.md`의 "55 = 시딩 큐 잔여" 귀속은 **사실과 다르다**

산출물은 C3 전용 55슬롯을 "new spawns from the seeding queue draining after C1"이라고 적었다.
census 원시 대조 결과 그 55기의 type은 **{32:33, 94:7, 6:6, 110:4, 52:3, 48:2}** 이고,
이번 회차가 시딩한 type은 **{5, 7, 46}** 뿐이다(C1 분포 `{5:801, 7:408, 46:360, 49:8}`).
⇒ 55기는 시딩 잔여가 아니라 **원본 생산 경로가 24k 동안 실제로 만들어 낸 유닛**이다.
**판정에는 영향 없다**(R은 공통 슬롯의 id 변경으로 정의되며 55기는 C3 전용). 그러나 이것은
**(가) 자연 도달 축에 관한 긍정 증거**이므로 오귀속을 남겨 두면 다음 회차가 잃는다.
규모는 작다 — 24k tick·8 owner에 **55기**, 자원은 96.8% 잔존(N81과 정합)이며,
이번 fixture는 시딩으로 이미 cap에 붙어 있어 **생산 여력 자체가 cap에 막혀 있다**
(W23/A1은 `used` 1,708/5,000으로 cap이 아니라 AI 자체가 멈춘 경우였다 — **다른 상황**).

### (N92) 같은 슬롯·같은 `internal_id`에서 **type 7 → 23 전이 17건** (완전 신규)

공통 1,565슬롯 중 **17건**이 `internal_id`·`owner` 불변인 채 type만 **7→23**으로 바뀌었다
(owner **7:9건, 3:8건**). C2(tick12,020)에서는 type23이 **2기**뿐이었으므로 전이는 주로
**후반부**에 일어났다. `R`은 id 변경으로 정의되므로 **판정 불변**이지만, 엔진이 슬롯을
제자리에서 변형시키는 경로가 존재한다는 뜻이다 ⇒ **"슬롯 재사용" 계측을 id 변경만으로 보는
현재 `R` 정의는 이 부류를 놓친다.** type7·type23은 **둘 다 cost 10**(Step A 표)이라 전비
장부에는 중립이다.

### (N93) 고착 `reserved`는 **10 고정이 아니다** — lap412/N68 서술의 정밀화

최종 표본에서 해소되지 않은 예약을 가진 owner: **owner3(`used=5000, reserved=15`)**,
**owner7(`5000, 15`)**, **owner6(`4990, 15`)**, **owner2(`4960, 10`)**.
지속 구간은 owner3 tick **531‥24,031**(701표본), owner6 **196‥24,031**(711),
owner7 **229‥24,031**(710) — 사실상 **전 구간 미해소**로 lap412/N68 기전이 이 후보·이 구성에서
**재현**된다. 다만 값이 **10이 아니라 15**인 경우가 다수다. Step A 표에서 **cost 15는 type32**이고
이번 run이 실제로 새로 만든 유닛 중 **type32가 33기로 최다**다 ⇒ **`reserved`는 큐에 걸린
주문 타입의 단가를 따른다**는 가설과 정합한다(직접 주문-타입 판독은 없으므로 **가설**로 남긴다).
**반증 1건 확인:** `used`가 정확히 5000인데 `reserved=0`인 owner-표본도 많다
(owner5 688표본, owner0 579, owner2 490) ⇒ **"cap에 붙으면 반드시 예약이 고착"은 아니다**
— 대기 주문이 있는 owner만 고착된다.

### (N94) 카드 §7 판정 사다리가 **전역이 아니다** (카드 결함, 이번 판정에는 미적용)

§7-3 `CYCLE_STABLE`은 `U1 ∧ D≥50 ∧ R≥1`, §7-4 `NO_ENGAGEMENT`는 "**위 cap 근접은 성립하지만**
D<50 또는 R=0". ⇒ `U1_pass=false`인 경우 3·4 어느 쪽도 성립하지 않아 **verdict가 정의되지
않는다**. 이번 run은 `U1_pass=true`라 영향이 없으나, 다음 카드는 이 구멍을 닫아야 한다.

### (N95) `P_max` 수치의 분모 차이 (경미, 판정 무관)

lap464는 `P_max=0.7114`(분모에 baseline 20/owner 포함), 내 receipt-기반 재계산은
**0.7147**(시딩 비용만, 39,180 중 type5가 28,000). 둘 다 목표 **≤0.85** 충족. 정의 차이일 뿐 결함 아님.

## 3. Step C(`RIDER_NO_REPRO`) 처분 — **판정 근거로 채택하지 않는다(VOID)**

lap462가 "다음 middle이 검토"로 남긴 방법론 유보를 원시 `step_c_run_summary.json`으로 확인했고,
유보는 **타당할 뿐 아니라 결정적**이다:

1. **producer가 생산 건물이 아니다.** `producer_from_op6` = **slot 1041 / type 7**
   (Step A 표: type7 = cost10, **width1×height1**) — 1×1 일반 유닛이다.
   더구나 그 슬롯을 만든 `op6_main_result`는 **`ok:false`,
   `reason:"fixture_exceeds_unreserved_supply"`** 로 **실패한 호출**이며, Step C는 그 실패 호출이
   남긴 슬롯을 producer로 삼았다.
2. **주문이 큐에 들어갔다는 증거가 없다.** `op1_result`는 `ok:true / raw_return:1`이지만
   `before`와 `after`가 **완전히 동일**(`used=5000, reserved=0, count=145`)하고,
   lap462 자신도 op1 전후 그 유닛의 `command/progress/production_type`이 불변이라고 적었다.
3. ⇒ 관측된 `reserved=0`은 **"stock은 cap에서 예약을 안 만든다"**(후보 고유 회귀)와
   **"주문이 애초에 큐에 안 들어갔다"**(시험 자체가 무효)를 **구분하지 못한다**.
   후자를 배제할 **양성 대조가 없다.**

**결론:** 카드 §5 판정식을 문자대로 적용한 lap462의 **절차는 옳다**. 무효인 것은 그 라벨에
카드가 붙여 둔 **추론**(`RIDER_NO_REPRO` ⇒ "후보 고유 회귀로 승격·lap404(가) 재심")이다.
그 추론은 "주문이 실제로 걸렸다"를 전제하는데 이 run은 그 전제를 세우지 못했다.
⇒ **lap404(가) 재심을 Step C 근거로 열지 않는다.** (가) 되물음은 **사용자 판단 대기 그대로**이며,
§38의 **(가) 잠정 채택도 번복하지 않는다**(번복할 증거가 없다는 뜻이지 확증됐다는 뜻이 아니다).

덧붙여 Step C의 stock 차량은 `count_cap=**250**`으로 관측됐다(카드 §2-3이 전제한 1200-슬롯
레이아웃과 별개 축인 **owner당 유닛 수 상한**). owner0은 count 145로 여기에 걸리지는 않았다.

## 4. W24 카드 처분 — **CLOSED 아님 (Step A/B/D만 충족)**

| Step | 상태 | 근거 |
|---|---|---|
| A 타입표 인벤토리 | **충족** | `type_table_inventory.json` 200엔트리·read_failed 0, B∩C 38, 대표 t=46 재확인 |
| B 판정기 수리 | **충족** | N85/N86 수리 확인 + 내 독립 역주입 8건으로 게이트 발화·양성 도달성 재증명 |
| C lap404 rider | **미충족(VOID)** | §3 — 양성 대조 부재로 무효. §38 의무③이 실질적으로 이행되지 않았다 |
| D 혼합구성 24k soak | **충족·ACCEPT** | §1 — 불일치 0, `NO_ENGAGEMENT` |
| §8 fail-closed 산출물 | **존재·항목 완비** | 요구 행 전부 있음(N91 귀속 오류 1건은 §2에서 정정) |

⇒ lap464가 예상한 "ACCEPT 시 W24 CLOSED"를 **그대로 집행하지 않는다.** Step C가 무효인 채로
닫으면 §38 의무③을 **이행하지 않고 이행했다고 기록**하게 된다(AGENTS.md "skip/exit0을 승인으로
쓰지 않는다"). **W24는 Step C 재실행만 남기고 열어 둔다.**

**144k 발행 금지도 유지한다** — §38 판정5의 해제 조건은 "이 카드 실행 + 독립검수 ACCEPT"인데
카드가 아직 닫히지 않았다. 또한 이것은 마일스톤 경계 판정이므로 middle이 단독으로 풀지 않는다.

## 5. 변경 파일 / fingerprint / 안전

- **게임 코드·제품 코드 변경 0** (middle 역할 경계 준수). 게임 실행 **0회**. 커밋 **0**.
- 이번 회차 repo **source 변경 0** ⇒ INBOX 2026-09-20 21:58 규칙대로 전체 `make check`를
  재실행하지 않고 표적 검사만 수행(N22 명시: **이번 회차에 source를 바꾸지 않았다**).
  - 표적 `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py` **5 passed**
  - `checks/safety.sh check` → **`SAFETY_PASS`**
  - `python3 checks/context_limits.py` → **`CONTEXT_PASS`**
- 원본 `/home/dev_00/syw2plus-run/game.exe` **직접 재해시**
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — **불변**.
- `patches/population/runtime_bridge.c` `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df` (lap464 기록과 일치, 이번 회차 무변경).
- `tools/inmm_stub/control_executor.c` `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f` (불변).
- `patches/population/fixed_supply_5000.py` `637223431639ad9becb57eb7ebe35a3e3dfc471c5cccf714032abdc14779a91c`.
- 잔류 프로세스: wine/game.exe **0건**. 실행 중인 `Xvfb`는 `ps` 추적 결과 **다른 저장소**
  (`Syw2plus_re_loop/tools/run_xvfb.sh`) 소유라 이 프로젝트 잔류가 아니며, AGENTS.md대로
  **건드리지 않았다**.
- 신규 파일(저장소 밖 temp): `20260922_lap465_middle_stepD_recheck/recheck465.py` + `recheck465_output.json`.

## 6. 다음 한 가지 (work 회차로 넘기는 명시 handoff)

**Step C 재실행 1건만.** 새 카드를 만들지 않고 **W24 §5를 그대로 재실행**하되 아래 2개를 더한다:

1. **생산 건물을 producer로 쓴다.** `op6`로 **type 46**(Step A 실측 cost20/**3×3**/flags0,
   B∩C 대표)을 **성공한 호출로** 배치하고 그 슬롯을 producer로 삼는다.
   **실패한 op6 호출이 남긴 슬롯을 producer로 쓰지 않는다**(이번 무효의 직접 원인).
2. **양성 대조를 먼저 건다(이것이 없으면 결과를 판정에 쓰지 않는다).**
   같은 stock 차량·같은 producer 선택 방식으로 owner의 `used`가 **cap보다 충분히 낮은 상태**에서
   op1 주문을 걸어 **`reserved > 0`이 실제로 발생함**을 먼저 보인다.
   - 양성 대조가 **발화하면** → 그 다음 cap 근접 상태에서 같은 주문을 걸고 §5 판정식 적용.
     이때의 `RIDER_NO_REPRO`만이 "후보 고유 회귀"를 의미한다.
   - 양성 대조가 **발화하지 않으면** → op1 경로 자체가 이 차량에서 주문을 만들지 못한다는 뜻이므로
     `RIDER_BLOCKED`로 정직하게 끝내고 **우회 패치를 만들지 않는다**(카드 §5 후단).
3. 부수: `reserved` 값이 **주문 타입 단가를 따르는지**(N93 가설)를 같은 run에서 관측만 해 둔다.
4. 금지 유지: op4 금지, 가드 완화 금지, AI/생산 로직 변경 금지((ㄴ) 미승인), 144k 금지.

**사용자/strategy 판정이 필요한 것(모델이 고르지 않음):** (ㄴ) G2 한정 최소 AI 변경 허용 여부,
lap404 (가)/(나), F4 (B)/(C) — 전부 기존 상태 그대로 대기. 이번 회차는 어느 것도 대신 고르지 않았다.
