# W24 — 혼합 구성(건물 포함) + 전투/사망/슬롯 재사용 순환 cap 근접 24k soak (lap461 middle 발행)

- 발행: lap461 middle (Claude Code `claude-opus-5` / high), 2026-09-21 KST
- 상위 근거: `loop/ESCALATE_SOL` §38(lap460 strategy 판정 5건, 특히 **판정 5**),
  `G2_CAP_PROXIMITY_SEEDED_SOAK_LAP445.md`(W21) §0 경계·§10·§11,
  `G2_A1_MAP_LEVER_LONG_WINDOW_LAP457.md`(W23) §4 판정식 선례, lap448 원시 712표본·16 receipt.
- 실행 역할: **work** (Claude Code `claude-sonnet-5` / high). 이 카드는 middle이 쓴 계획이며
  middle은 구현하지 않는다. work가 실행하고 **다음 middle이 독립 검수**한다.
- 후보: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (핀 복사 금지 — 현재 source 재빌드로 SHA 확인, N53).
- **활성 카드는 이 1장뿐이다**(§38 판정5 의무⑤). W21·W22·W23은 CLOSED(STATUS 기준).
  `docs/work/active/`의 과거 카드 파일은 이력 보존용이며 삭제하지 않는다.

## 0. 이 카드가 사는 경계 (위반 시 다음 middle은 내용을 보지 않고 REJECT)

1. **(ㄱ) 축 안에서만 움직인다**(§38 판정1). gate-legal 시딩 기반 cap 근접 + soak가 증거 축이며,
   이것은 **모델의 검증 기준이고 3단 사용자 마일스톤 승인을 대체하지 않는다.**
2. **op4(장부 직접 write) 금지.** 시딩은 원본 배치 `0x42ECB0` → 원본 생산 gate `0x43EDA0` →
   원본 spawn `0x443190` 경로만 쓴다(W21 §2-2에서 확인된 gate-legal 경로).
3. **(ㄴ) 미승인 — AI/경로/생산 로직·게임 바이너리 동작 변경 금지**(2026-09-21 00:20 사용자 지시의
   명시 예외가 아직 없다). 본 카드에서 전투가 발생하지 않더라도 **AI를 건드려 발생시키지 않는다.**
   그 상황의 올바른 출력은 §7의 `NO_ENGAGEMENT`이며, 그것은 실패가 아니라 **측정 결과**다.
4. **144k 카드 발행 금지 유지**(§38 판정5). 해제는 이 카드 실행 + 독립검수 ACCEPT 이후다.
5. **F4 즉시 STOP 조건**(§38 판정4): 어느 표본에서든 owner 장부에 **음수·랩·32,767 근접**이
   관측되면 그 자리에서 중단하고 표본을 보존한 뒤 보고한다. (B) 재심 사유다.

## 1. 이 카드가 답하는 단 하나의 질문

> **수리후보가 "cap 근접 + 안정"을 넘어, 혼합 구성(건물 계층 포함)과 전투/사망/슬롯 재사용
> 순환까지 포함한 상태로 24k tick을 버티는가? 그리고 그 두 축을 fixture 범위 안에서 만들 수
> 있는가?**

`CYCLE_STABLE` / `NO_ENGAGEMENT` / `CYCLE_UNSTABLE` / `ARM_FAIL` 중 하나로 끝낸다.

## 2. middle이 이번 회차에 확인해 준 것 (work는 같은 것을 다시 파지 말 것)

### 2-1. 건물 계층은 **정적으로 결정할 수 없다** — 런타임 표 읽기가 유일한 길

`patches/population/runtime_bridge.c:177`은 seeding 타입을 **하드코딩**한다:

```c
DWORD fixture_type = op == 5 ? 5u : 7u;          /* L177 */
DWORD type_offset = fixture_type*0x394u;
SHORT fixture_cost = S16(0x9b5238u+type_offset);  /* cost   = +0x00 */
SHORT width  = S16(0x9b523eu+type_offset);        /* width  = +0x06 */
SHORT height = S16(0x9b5240u+type_offset);        /* height = +0x08 */
/* L190-193 가드: type != fixture_type, cost 불일치,
   (U32(0x9b524cu+type_offset) & 14u) != 0,  width/height 가 1..8 밖  → 거부 */
```

⇒ **op5/op6으로는 type 5(cost 35)와 type 7(cost 10) 외에 아무것도 시딩할 수 없다.**
그리고 타입 표 `0x9B5238`은 `.data` raw 끝 `0x4F9000` **바깥(BSS)** 이라(STATUS F4 블로커, W2 실측)
**파일 정적 분석으로 타입 목록을 얻는 것은 불가능**하다. 정적 역추적을 새로 시작하지 말 것.

**남은 유일한 싼 길:** PS3 진입 후 `0x9B5238 + t*0x394`(t=0..199)를 **읽기만** 한다.
샘플러는 이미 Linux 쪽에서 게임 메모리를 직접 읽으므로 **DLL 변경도 새 op도 필요 없다.**

### 2-2. **결정적 — 인접 배치는 이미 있었고, 전투는 일어나지 않았다** (lap448 원시 재계산)

lap451이 "앵커 8개 전부 disjoint"라고 적은 것은 **앵커 좌표가 서로 다르다**는 뜻이며,
**배치 범위가 분리됐다는 뜻이 아니다.** `runtime_bridge.c:200-205`의 배치는 앵커 셀에서
`candidate=(candidate+1)%cells`로 **맵 전체를 선형 주사**한다. lap448 receipt 실측:

| owner | anchor | 시작 셀(= y·100+x) | attempts | 주사 구간 |
|---|---|---|---|---|
| 0 | (2,2) | 202 | 180 | 202‥381 |
| 1 | (27,2) | 227 | 347 | 227‥573 |
| 2 | (52,2) | 252 | 526 | 252‥777 |
| 3 | (77,2) | 277 | 658 | 277‥934 |

⇒ owner0·1·2·3의 배치 구간이 **서로 겹친다**(맵 100×100). 즉 적 소속 유닛이 같은 행에
**셀 단위로 뒤섞여 24,000 tick 동안 인접**해 있었다. 그럼에도 lap448 원시 712표본에서
**owner `count`가 감소한 표본은 단 2건**(tick **10,587**, owner0 `152→150`, owner1 `154→152`)
= 전 소실 **4기 / 1,166기 / 24k tick**이다.

⇒ **"앵커를 붙이면 싸운다"는 레버는 이미 소진됐다.** work는 기하 배치를 새 가설로 삼지 말 것.
남은 fixture 내 가설은 **구성(타입)** 뿐이며(§3), 그것도 실패하면 `NO_ENGAGEMENT`가 정답이다.

### 2-3. lap404 rider의 **차량은 이미 저장소에 있다**

`patches/population/fixed_supply_5000.py` — 원본 `b56986e0…c9c08a8ac`에 **2곳만**, 길이 변화 없이
편집해 **stock 1200 레이아웃 + 전비 cap 5000**을 만든다:
`0x1B576` `66c700dc05`→`66c7008813`(즉치 1500→5000), `0x3FFD4` `05dc050000`→`b888130000`
(`add eax,0x5DC` → `mov eax,0x1388`. **즉치만이 아니라 opcode도 바뀐다** — old bytes 그대로 확인할 것). 재배치 후보가 아니다. 새 패치 모듈을 만들지 말 것.
브리지는 **기본값(`--unit-pool-capacity` 미지정 = 1200)** 으로 빌드한다 ⇒
`runtime_bridge.c`의 1200 리터럴 치환이 일어나지 않고 op1의 `slot < 1200` 가드가 그대로 맞는다.

### 2-4. 주문 1건을 거는 원시 수단 = op1 (원본 Train)

`runtime_bridge.c:137-147` — op1은 살아 있고 owner 소유인 producer 슬롯을 검증한 뒤
**원본 `0x4AF5E0`(Train)** 을 `(U32(unit+0x29c), type, 1)`로 호출한다. 장부 직접 write가 아니다.
op4와 달리 rider에 사용할 수 있다.

### 2-5. N85/N86 결함 위치는 확정돼 있다

`temp/.../20260921_lap458_w23_a1_long_window/compute_verdict458.py`:
- **N85** L18-19 `used_map()`이 `s["owners"]` **전부**를 담는다. `ai_flags_at_ps3`·표본의
  `ai` 필드를 **쓰지 않는다** ⇒ `ai=0` owner가 있는 축(W22 A2형)에 재사용하면 그 owner의
  `used=20`이 조용히 `U_min`이 되어 오판한다.
- **N86** L63-68 verdict 사슬에 **도달 tick·fault 게이트가 없다** ⇒ 24,000에 못 가고 죽은 run도
  `DECAYED`/`SUSTAINED`를 출력한다(N65와 동형). L60-61의 `if U_min24 < 0: pass`는 무동작이다.

## 3. Step A — 런타임 타입 표 인벤토리 (게임 1회, 읽기 전용, source 변경 0)

**이 Step이 Step D의 구성을 결정하므로 반드시 먼저 한다.**

1. 후보(`a10024de…`)로 PS3 진입 → 시딩 **전에** `0x9B5238 + t*0x394`(t=0..199)에서
   `cost(+0x00,S16)` / `width(+0x06,S16)` / `height(+0x08,S16)` / `flags(+0x14,U32)`를 읽는다.
2. 산출물 `type_table_inventory.json`: t마다 위 4필드 + **읽기 실패 여부**. 실패는 실패로 적고
   `UNKNOWN`으로 남긴다(추정 금지). 읽기 실패로 프로세스를 죽이지 않는다.
3. 그 표에서 아래 두 집합을 **기계적으로** 뽑아 적는다(해석은 최소로, 근거는 필드값으로):
   - **B집합(건물 후보)**: `width≥2 ∧ height≥2` 인 t. 참고로 op5/op6이 쓰는 type5/type7의
     실측 `width/height`를 같은 표에 **반드시 병기**해 대조 가능하게 한다.
   - **C집합(op5/op6 가드 통과 가능)**: `(flags & 14) == 0 ∧ 1≤width≤8 ∧ 1≤height≤8` 인 t.
4. **판정 (실행 전 고정):**
   - `BUILDING_SEEDABLE` — `B ∩ C ≠ ∅`. 그 중 **cost가 가장 큰 t 하나**를 건물 계층 대표로 택한다.
   - `BUILDING_BLOCKED` — `B ∩ C = ∅`. **이때 `&14` 가드나 width/height 가드를 완화하지 않는다.**
     그 가드의 의미는 아직 모르고(원본 동작), 결과를 만들려고 안전 가드를 푸는 것은
     AGENTS.md 위반이다. 사유(어느 조건에서 걸렸는지)를 t별로 적고 §7 (V4)에 그대로 반영한다.
5. 같은 표에서 **전투 가능성 후보**도 뽑아 적는다: type5/type7 대비 `flags` 비트가 다른 t를
   나열하되, **"이 비트가 공격력이다"라고 단정하지 않는다.** 이름표가 없는 BSS 표이므로
   §3 산출물은 **관측값의 나열**이고, 선택 근거는 §6에서 실측으로 검증된다.

## 4. Step B — 판정기 수리 (게임 실행 0, 판정식 계산 **전에** 끝낸다)

§38 판정5 의무②. **이것은 계측 버그 수리이고 판정식 변경이 아니다.**

1. 새 `compute_verdict461.py`를 쓰되 아래 두 가지를 **먼저** 넣는다:
   - **(N85 수리)** 활성 owner 집합 = **표본의 `ai` 필드가 1인 owner**(표본마다 평가).
     `run_summary`의 요약 필드가 아니라 원시 표본에서 뽑는다. 활성 owner 수를 산출물에 적는다.
   - **(N86 수리)** **`ARM_FAIL` 게이트를 가장 먼저, 배타적으로** 적용한다(§7-1).
     통과하지 못하면 다른 verdict를 **계산조차 하지 않는다**.
2. **음성 대조 2건으로 게이트가 실제로 발화함을 증명한다**(lap441 역주입 선례, 게임 실행 불필요):
   - (a) 마지막 표본을 tick 12,000에서 자른 합성 입력 → `ARM_FAIL` 이 나와야 한다.
   - (b) 한 owner의 `ai`를 0으로, `used`를 20으로 바꾼 합성 입력 → 그 owner가 `U_min`/활성
     집합에서 **제외**되어야 한다.
   두 결과를 `verdict_gate_negative_control.json`에 남긴다. **발화하지 않으면 Step D로 가지 않는다.**
3. 판정기는 `run_summary.json`·서술·로그를 **입력으로 쓰지 않는다**(원시 `samples.jsonl`만).

## 5. Step C — lap404 rider (게임 1회, 짧게. **Step D보다 먼저 한다**)

§38 판정5 의무③. 긴 soak가 잘리면 rider가 또 미뤄지므로(N66 3연속 누락 선례) **앞에 둔다.**

1. 차량: §2-3의 `fixed_supply_5000.py` 산출물(stock 1200 레이아웃 + cap 5000).
   브리지는 capacity 치환 **없이** 빌드. 원본은 읽기 전용, 새 복사본만.
2. op7로 자원 공급 → **owner 1명**에게 op5/op6 시딩으로 live `used`를 **cap(5000)에 최대한
   근접**시킨다(달성값을 그대로 기록. 1200 슬롯이므로 143기 내외로 충분).
   §5 함정1대로 **op5 `wanted=1` 스모크 1건**을 먼저 보내 `fixture_failed` 잠금을 확인한다.
3. 그 owner의 살아 있는 슬롯 하나를 producer로 삼아 **op1로 cost 10짜리 주문 1건**을 건다.
4. 이후 **≥300 tick** 동안 그 owner의 `(used, reserved, count)`를 표본화한다.
5. **판정 (실행 전 고정):**
   - `RIDER_REPRO` — `used`가 cap에 붙은 상태에서 `reserved`가 **10**이 되고 관측 창 끝까지
     해소되지 않는다 ⇒ lap412 기전이 **stock 고유**임이 확인 ⇒ §38 판정3의 (가) 잠정 채택이
     **유지**된다.
   - `RIDER_NO_REPRO` — `reserved`가 0으로 유지되거나 즉시 해소된다 ⇒ **후보 고유 회귀로 승격**
     하고 (가)를 재심 대상으로 올린다(§38 판정3 후단). 이 경우 Step D는 그대로 진행하되
     이 사실을 §8 산출물 첫 줄에 적는다.
   - `RIDER_BLOCKED` — cap 근접 실패 / 살아 있는 producer 없음 / op1이 `producer_not_alive_or_owned`
     또는 gate 거부 ⇒ **정확한 reason 문자열과 장부를 적고 끝낸다.** 우회 패치 금지.

## 6. Step D — 본체: 혼합 구성 24k soak (게임 1회)

fixture 축은 lap448과 동일(N=4001 신후보 / 8 owner 전원 `ai=1` / seed42 / 격리 사본·전용 prefix·
빈 display / op7 자원 공급 / op4 금지). **바꾸는 것은 구성(타입)뿐이다.**

1. **구성 규칙:** Step A가 `BUILDING_SEEDABLE`이면 대표 건물 타입을 시딩 구성에 포함해
   **비용 기준 단일 type 비중을 85% 이하**로 만든다(N67: lap448은 99.0%였다).
   `BUILDING_BLOCKED`이면 type5/type7만으로 진행하고 **그 사실과 사유를 산출물에 적는다**
   — 건물 축은 닫히지 않은 채 남으며, **닫혔다고 쓰지 않는다.**
   - 건물 타입을 시딩하려면 `runtime_bridge.c`의 op5/op6 타입 하드코딩을 **확장**해야 한다.
     허용 범위: **Place→Gate(`0x43EDA0`)→Spawn 순서와 매 개체 장부 검증(L218-224)을 그대로 유지**
     한 채 허용 타입 집합만 넓히는 것. **가드 완화·검증 생략·op4 사용은 금지.**
     이때는 source 변경이므로 통합 경계에서 `make check` 전체 1회 + "이번 회차 source 변경" 명시(N22).
2. **접촉 기하는 lap448과 동일하게 둔다**(§2-2 — 새 기하 가설 금지).
3. 시딩 완료 후 **STOP_TICK ≥ 24,000**까지 샘플링한다.
4. **표본 필드는 lap448 합집합 이상**(N63): `tick,t,live,sum_count,max_slot_index,rss_kb,
   vm_size_kb,vm_swap_kb,host_mem_available_kb,pid` + owner별 `{owner,ai,rice,wood,count,used,
   reserved,cap,count_cap}`. **(U4) 유지(§38 의무④):** `/proc/<pid>/smaps_rollup`의
   `Private_Clean`/`Private_Dirty`/`Referenced`를 계속 넣는다(lap452가 추가한 필드를 빼지 말 것).
5. **슬롯 재사용 계측 (이번 카드의 새 요구).** 전수 census를 **3회만** 찍는다 —
   **C1: 시딩 직후 / C2: tick≈12,000 / C3: tick≈24,000**. 각 census는 슬롯 `0..N-1` 전수로
   `(slot, existence, internal_id, type, owner)`를 기록한다(lap452가 이미 한 방식).
   매 표본마다 찍지 않는다(비용).
6. **하지 말 것:** `max_slot_index_seen`을 점유·확장 근거로 쓰지 않는다(N55).
   `tools/inmm_stub/` 진단 채널의 유닛 수를 판정 근거로 쓰지 않는다(W21 §5-2).

## 7. 실행 전에 고정하는 판정식 (사후 재채점 금지 — W17/W23 선례)

**활성 owner 집합 = 표본의 `ai==1` owner**(N85 수리 반영).

정의:
- **`D`** = Σ over 연속 표본 pairs of `max(0, count_prev − count_now)`, 활성 owner 전체 합.
  (사망의 **하한**이다. 증가로 상쇄된 사망은 세지 못한다 — 이 한계를 산출물에 적는다.)
- **`R`** = C1에서 live이고 C3에서도 live이면서 **`internal_id`가 달라진** 슬롯 수
  (= 그 슬롯이 죽고 재사용됐다는 직접 증거).
- **`P_max`** = 시딩 비용 기준 최대 단일 type 비중.

**판정 (이 순서로 배타 적용):**

1. **`ARM_FAIL`** — 최종 tick < 24,000 **또는** fault/crash/read failure > 0 **또는** PS3 진입 실패.
   fault tick과 마지막 표본을 적고 끝낸다. **다른 verdict를 계산하지 않는다.** 되살리려고
   즉흥 패치하지 않는다. (N86 수리의 실제 집행 지점)
2. **`CYCLE_UNSTABLE`** — live `used > 5000` 표본 ≥1건 **또는** `live ≠ Σcount` 표본 ≥1건
   **또는** §0-5의 랩/음수 관측. ⇒ **새 결함. 즉시 중단·에스컬레이션.**
3. **`CYCLE_STABLE`** — 시딩 종료 시 활성 owner **전원** live `used ∈ [4900,5000]`
   **∧** `D ≥ 50` **∧** `R ≥ 1`.
   ⇒ 혼합 구성 + 사망/재사용 순환을 포함한 24k 안정성. **여전히 부분 증거다.**
4. **`NO_ENGAGEMENT`** — 위 cap 근접은 성립하지만 `D < 50` 또는 `R = 0`.
   ⇒ **전투/사망 축은 fixture 범위에서 만들 수 없다는 실측 결론.** 안정성 증거는 유효하다.
   이 경우 **(ㄴ) 사용자 승인 없이는 이 축이 닫히지 않는다**는 사실만 보고하고 끝낸다.
   **모델은 AI/생산 정책 변경에 착수하지 않는다.**

**고정 임계 `D ≥ 50`의 근거(실행 전에 박는다):** lap448은 같은 fixture·인접 배치·24k에서
`D = 4`(1,166기 중 4기, §2-2)였다. 50은 그 **12.5배**이고 시딩 규모의 약 4%다. 즉 `D ≥ 50`은
lap448에서 이미 관측된 우발적 소모로는 **도달할 수 없는 값**이며, 넘으면 전투 순환이 실제로
돌았다는 뜻이다. `R ≥ 1`은 "죽은 자리가 다시 쓰였다"의 최소 직접 증거다.

**실행 전 기대값(사후 서사 방지 — 반드시 산출물에 미리 적어라):**
구성 변경이 전투에 영향을 주지 않는다면 **`D ≈ 4`, `R = 0`, verdict = `NO_ENGAGEMENT`**.
`P_max`는 lap448 기준 **0.990**이며 이번 목표는 **≤0.85**다.

**부수 기록(판정에 쓰지 않음, 반드시 보고):** owner별 max `used`, max live, 최소 rice/wood,
`used+reserved>5000` owner-표본 수(N68 계열 — lap448은 1,263건이었다), (U4) 메모리 하강 이벤트.

## 8. fail-closed 산출물 (없으면 다음 middle은 내용을 보지 않고 REJECT — N66 선례)

`temp/Syw2plus_patch/g2_capacity/<이번 run 디렉터리>/w24_mixed_cycle_soak.md`

최소 내용(수치를 모르면 `UNKNOWN`이라고 쓰되 **행 자체를 비우지 않는다**):
- 첫 줄에 **Step C rider 판정 한 단어**(`RIDER_REPRO`/`RIDER_NO_REPRO`/`RIDER_BLOCKED`)
- Step A 판정 한 단어(`BUILDING_SEEDABLE`/`BUILDING_BLOCKED`) + `B∩C` 목록 + 대표 t와 근거 필드값
- Step B 음성 대조 2건의 결과(발화 여부)
- 설정 fingerprint: 후보 EXE SHA(재빌드 확인), `dll_sha256`(**`bridge_sha256` 아님** — N62),
  `control_executor.c`/`runtime_bridge.c`의 **as-run sha256과 회차 종료 시 repo sha256 둘 다**(N80-1),
  goal 문자열, 로비 config, 실측 `map_width×map_height`, 활성 owner 수, `pid`+`cmdline`
- **실행 전 기대값**(§7) 과 그 근거 한 줄
- 시딩 구성표: type별 기수·단가·비용합·비중, `P_max`
- `D` / `R` / cap 근접 owner 수 / 각 수치의 산출 근거 표본·census
- 무결성: `live==Σcount` 불일치 수, live `used>5000` 표본 수, tick 역행 수, fault/read failure 수,
  최소 rice/wood, 랩·음수 관측 여부
- (U4) 메모리: 1MB 이상 RSS 하강 이벤트와 `vm_size`/`vm_swap`/`smaps_rollup` 동반 변화
- 마지막 줄에 §7 판정식을 적용한 **최종 한 단어**

## 9. 운영 규칙

- Step A+B+C는 짧다. **Step D(24k ≈ 12분 + setup)까지 한 회차 60분 상자에 들면 같은 회차에
  끝낸다.** 상자를 넘으면 Step D만 **다음 work 회차가 곧바로 실행**한다 — 재계획·새 카드 금지
  (PROMPT ③: `FEASIBLE`이면 계획 회차를 쌓지 않는다).
- 장기 실행은 **동기 실행 또는 root 소유 exec 세션**. 셸 background로 넘기고 회차를 끝내지 않는다
  (INBOX 2026-09-21 01:01). "background 실행 중" 문구만으로 활성 프로세스를 주장하지 않고
  PID/산출물 갱신을 확인한다.
- **work는 자체 lap 기록을 `docs/history/laps/`에 남긴다(N64).** lap456 이후 유지되고 있다.
- 격리 전체 게임 사본 + 전용 Wine prefix + 빈 Xvfb display. 원본/참고 저장소 쓰기 금지,
  전역 pkill 금지, 다른 프로세스/로그 정리 금지.
- 커밋 금지(`LOOP_ALLOW_COMMITS=0`). 변경 파일은 **경로와 sha256**으로 남긴다.
- source를 바꿨으면 통합 경계에서 `make check` 전체 1회 + "이번 회차에 source를 바꿨다" 명시(N22).
  안 바꿨으면 표적 테스트 + `checks/safety.sh check` + **원본 직접 재해시**만.
- 후보는 **재빌드로 SHA 확인**(N53). 원본 `b56986e0…c9c08a8ac` 불변 재확인.
- `local/runtime` 여유가 10G 아래면 lap429 선례대로 **실행 전에 중단하고 보고**한다.

## 10. 이월된 미수리 계측 결함 (이 카드가 상속하지 않더라도 소멸하지 않는다)

`.../20260921_lap452_.../w21_step2_run.py`의 **N71**(창 전용 라벨이 24k 판정과 같은 문자열
`CAP_PROXIMITY_STABLE`, `u1_pass` 하드코딩), **N72**(`U5_pass`가 `new_after_load` 미게이트),
**N73**(presave 스냅샷이 op2 save 이전) — **그 파일을 다시 쓰는 회차가 진다.**
Step D의 census 코드를 그 스크립트에서 가져오면 **N71~N73을 함께 고친다.**
**N80-3**(`test_g2_legacy_goals_compute_identical_config_to_pre_w22_source`가 C 소스를 읽지 않아
C 변경으로 실패할 수 없음)은 `tests/test_g2_eight_owner_setup.py`에 살아 있다 — §6-1로
`runtime_bridge.c`를 바꾸는 회차는 이 사각을 **반드시 보고**한다.

## 11. 이 카드가 끝나도 **아직 아닌 것**

G2 제품 완료 아님. `CYCLE_STABLE`이어도 얻는 것은 **"gate-legal 시딩으로 만든 cap 근접 상태에서
혼합 구성·사망/재사용을 포함해 24k tick 안정"** 이라는 **부분 증거**다.
미검증으로 남는 것: **원본 생산 경로로의 자연 도달((가) — §38에서 fixture 축 `NOT_FEASIBLE` 확정,
남은 진입로는 사용자 승인 대기 중인 (ㄴ))**, 144k 장주기, LAN/지원 동기화, (U4) 잔여 UNKNOWN,
`BUILDING_BLOCKED`인 경우의 건물 계층. 사용자 마일스톤 승인(3단)은 별개다.
