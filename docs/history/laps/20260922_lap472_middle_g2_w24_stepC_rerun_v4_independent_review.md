# 2026-09-22 | lap472 | 목표 G2 (W24 §5 Step C 4회차 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, 지정 역할 **middle**
  (진단·계획·컨펌). 게임 실행 **0**, 게임 코드 hands-on 수정 **0**, source 변경 **0**, 커밋 **0**.
- 가설 / 사용자 관찰: STATUS 「다음 한 가지」 = lap471(work)의 `RIDER_ORDER_NOT_ACCEPTED`를
  원시 3종만으로 비참조 재계산해 독립 검수하고, work의 잠정 해석("원본 Train()이 수락 시점
  headroom<비용이면 예약을 조용히 무시하며 그 거부는 일회성")을 검증한다.
- 예상 PASS / FAIL 조건: 원시 재계산이 lap471 수치와 일치하면 측정 축 ACCEPT. 일치하더라도
  해석이 원시로 뒷받침되지 않으면 해석 축은 별도로 REJECT/UNPROVEN으로 처분한다.

## 1. 판정 입력 경계 (lap470 §42 선례 그대로)

판정 입력은 **원시 3종뿐**이다:

| 파일 | sha256 | 표본 |
|---|---|---|
| `step_c_samples.json` | `0ab5cf2bd4f2fc12ecb0dc1f064893a3397ec0b4b4b164b60f08ddb6b57d187d` | 316 |
| `positive_control_samples.json` | `ab6371d0f094883334ef715613e5d2a4febe5775d3d13c2e4fb91228ddc2a6b0` | 209 |
| `death_events.json` | `db316f23767cff03a989c33edb4adcfec32171c74aaf991c846698506490bf45` | 4 |

`step_c_run_summary.json`·`orchestrator_stepC_v4.log`·lap471 서술·STATUS/INBOX 요약은 **재계산
입력에서 제외**했다(§3까지). §4의 교란 분석에서만 로그를 **provenance 보조**로 인용한다 —
그 인용은 판정을 바꾸지 않고 **다음 probe를 결정**하는 데만 쓴다.
재계산 산출물: `temp/Syw2plus_patch/g2_capacity/20260922_lap472_middle_stepC_v4_recheck/`
(`recheck472.py`, `recheck472_output.json`).

## 2. 측정 축 — 전 항목 일치, 불일치 **0** ⇒ **ACCEPT**

| lap471 주장 | lap472 원시 재계산 | 일치 |
|---|---|---|
| 316표본 전부 `reserved=0` | `distinct_reserved=[0]`, `max=0`, `>0` 표본 **0건** | ✓ |
| `order_fired=false` | `any(reserved>0)` = **false** (표본 필드와도 일치) | ✓ |
| `count` 증가 0건, 146→142 | 증가 이벤트 **0건**, 감소 4건, 첫146/끝142 | ✓ |
| `count_increased=false` | 142 > 146 = **false** | ✓ |
| `used+reserved>cap` 0건 | 0건, `max(used+reserved)`=**4,995** ≤ cap 5,000 | ✓ |
| `ticks_in_blocking_regime=0` | 진입 표본 없음 ⇒ **0** | ✓ |
| 전제 headroom 5 < 비용 10 | 창 첫 표본 `used=4,995`, `cap=5,000` ⇒ headroom **5** | ✓ |
| 창 실현 2,106 / 예산 2,100 | 719→2,825 = **2,106** tick | ✓ |
| 사망 4건(cost35×3+cost20×1) | tick 1053/1514/2163/2571, `used` 4995→4960→4925→4890→4870 | ✓ |
| producer `progress`/`type` 고정 | `progress` 전 표본 **100**, `production_type` 전 표본 **7** | ✓ |
| headroom 5→130 회복 후에도 0건 | headroom max **130**, ≥비용 표본 266건, 그 구간 `reserved` 전부 0 | ✓ |

보강 확인:
- **표본 무결성:** tick 단조 비감소, 역행 0, 중앙 표본 간격 **7 tick**, `cap` 단일값 5,000.
- **F4 STOP 게이트(§0-5):** 음수·랩·32,767 근접 **0건**. 라이브 `used>cap` **0건**.
  `count_cap`=250, `count>count_cap` 0건. 최소 rice 999,200 / wood 1,000,000(자원 고갈 아님).
- **사망 목록 교차검증:** `death_events.json` 4건이 표본에서 재유도한 `count` 감소 4건과
  tick·전후값까지 **완전 일치**(N103의 (iv) 분리 계측이 실제로 작동).
  4건 모두 `reserved=0` 상태에서 발생 ⇒ 예약과 인과 없음.
- **(N106, 신규) 장부 항등식이 독립적으로 성립한다:** 초기 4기 75 + 대량시딩 140×35=4,900 +
  양성대조 산출 1기 10 + top-up 1기 10 = **4,995**, 기수 140+4+1+1 = **146**. 관측치와 정확히
  일치하고, cost-20 사망 1건은 초기 4기 중 1기로 설명된다(75 = 35+20+10+10 형태).
  ⇒ 시딩 구성 서술과 장부가 서로를 검증한다.

**표본 해상도 반론 차단:** "짧은 예약을 샘플러가 놓쳤을 수 있다"는 성립하지 않는다 —
같은 producer·같은 type의 양성대조에서 예약은 **698 tick(208표본) 지속**했고 이번 창의
표본 간격은 7 tick이다. 게다가 `count`가 한 번도 늘지 않았다는 **독립 증인**이 있다.

## 3. 판정 라벨 축 — 사후 유리 재채점 아님 ⇒ **ACCEPT**

`step_c_run_v4.py:678-710`의 판정 사슬을 원시에 직접 적용하면 `order_fired=false ∧
count_increased=false` ⇒ **`RIDER_ORDER_NOT_ACCEPTED`** 가 그대로 나온다(재유도 일치).

이 라벨은 회차 중간에 **추가**된 것이므로 "사후 재채점"(카드 §7 금지) 여부를 따로 심사했다.
**심사 결과 위반 아님**, 근거 셋:
1. 새 분기는 `RIDER_REPRO`(`final_reserved≠0` 요구 ⇒ `order_fired` 함의)와 **배타적**이고,
   `RIDER_NO_REPRO`가 성립하려면 이제 `order_fired`가 필요하다 ⇒ **유리한 결론을 만들지 않고
   기존의 거짓 결론을 결론 없음으로 낮춘다.** 방향이 보수적이다.
2. 1차 시도 원시(`attempt1_stale_progress_false_positive/step_c_samples.json`, 5표본)를 직접
   재계산하니 `reserved` 전부 0·`count` 전부 146·`used` 전부 4,995로 **최종 run과 물리가 동일**
   하다. 즉 라벨 변경은 **다른 데이터를 다르게 채점한 것이 아니라 같은 물리를 바르게 분류**한 것이다.
   1차는 27 tick 만에 "해소"로 오판해 중단했고, 최종 run은 창을 2,106 tick으로 완주했다.
3. 구 판별자(`reserved==0 and progress==100`)가 왜 거짓인지 원시로 확인된다 —
   `producer_last_progress_change_tick`이 **316표본 전부 719**(창 시작)로, 창 안에서 progress는
   **한 번도 변하지 않았다.** 100은 창 시작 시점에 이미 고정된 값이다.

## 4. 해석 축 — **REJECT / UNPROVEN (N105, 결정적)**

work의 잠정 해석은 "**headroom<비용**이라서 Train()이 예약을 만들지 않고 조용히 무시했다"이다.
**원시는 이 인과를 지지하지 않는다 — fixture가 두 변수를 동시에 바꿨기 때문이다.**

양성대조 표본에서 producer 상태 전이를 재계산하면:

| 국면 | `producer_command` | `progress` | `production_type` | `reserved` |
|---|---|---|---|---|
| 1차 주문 **직전**(로그 provenance) | 1 | **0** | **0** | 0 |
| 1차 주문 생산 중 (208표본) | **15** | 0→99 단조 | 7 | **10** |
| 1차 주문 완료 (tick 709) | 1 | **100** | **7** | 0 |
| 2차(차단영역) 주문 **직전** | 1 | **100** | **7** | 0 |
| 2차 주문 창 전체 (316표본) | 1(261)→22(15)→7(40) | **100 고정** | **7 고정** | **0** |

⇒ **1차 주문을 수락한 producer 상태(`progress=0, production_type=0`)와 2차 주문을 받은
producer 상태(`progress=100, production_type=7`)가 다르다.** 완료된 생산이 **해제되지 않은 채**
남아 있었고, 창 전체에서 `command`가 생산 중 값 **15에 단 한 번도 진입하지 않았다.**

따라서 최소 두 가설이 **모든 원시 표본과 똑같이 정합**한다:

- **H-headroom** (work 주장): 수락 시점 `headroom<비용`이면 Train()이 조용히 무시한다.
- **H-producer** (신규): 완료·미해제 생산을 안고 있는 producer는 headroom과 무관하게 2차 주문을
  받지 않는다. 이 fixture는 **같은 producer 슬롯 1182에 주문을 연속 2건** 걸었다.

원시 3종으로는 둘을 **분리할 수 없다.** 부수적으로 로그(provenance)에 따르면 2차 op1은
`ok:true / reason:'executed' / raw_return:1` 로 **원본 Train()이 성공을 반환**했는데도 예약이
생기지 않았다 — 이것은 두 가설 **어느 쪽도 배제하지 못한다**(둘 다 "성공 반환 + 무동작"과 정합).
자원 고갈·`count_cap` 도달은 §2에서 이미 배제됐다(rice 999,200 / count 146 < cap 250).

⇒ **"거부는 headroom 때문이며 일회성"이라는 인과 서술은 미증명이다.** STATUS/INBOX는 이 해석을
**work의 잠정 판단이자 미검증**으로만 기록해야 하며, lap406/412/449의 "reserved=10 수만 tick
지속"이 이 fixture로 **원리적으로 재현 불가능**하다는 파생 결론도 함께 미증명이다.

## 5. 판정

- **측정 무결성 = ACCEPT** (재계산 불일치 0, F4 게이트 전부 0, 사망 분리 계측 작동).
- **판정 라벨 `RIDER_ORDER_NOT_ACCEPTED` = ACCEPT** (원시에서 재유도, 사후 유리 재채점 아님).
- **인과 해석 = REJECT(UNPROVEN)** — N105 교란(producer 잔여 상태 vs headroom).
- **Step C 4회차 = `STEP_C_CONFOUNDED`** ⇒ `RIDER_REPRO`/`RIDER_NO_REPRO` **여전히 미도달**
  (lap462 VOID · lap466→467 `INCONCLUSIVE` · lap469→470 `PRECONDITION_NOT_MET` · 이번
  `CONFOUNDED`로 **4회 연속 무효**, Step C 누적 **7회차**).
- **W24 CLOSED 아님**(A·B·D 유효, C만 미충족) · **144k 발행 금지 유지**(§38 판정5 해제 조건
  미성립, 마일스톤 경계라 middle 단독 해제 금지) · **lap404 (가) 잠정채택 유지·재심 종결 안 함**
  (이번 run도 (가)에 증거를 주지 않는다 — 차단 현상이 발생조차 하지 않았다, N83/§42-5와 동일 처분).
- 이번 회차 검사: targeted `pytest tests/test_runtime_env.py
  patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` **167 passed**(lap471 수치
  독립 재현) · `checks/safety.sh check` → **SAFETY_PASS**(원본 pin `b56986e0…c9c08a8ac` 불변) ·
  `python3 checks/context_limits.py` → **CONTEXT_PASS**. source 미변경이므로 전체 `make check`는
  면제(2026-09-20 21:58 지시, **이번 회차 source 변경 0**). 레포 현재 재해시가 lap471의 실행 전/후
  기록과 **3자 일치**: `runtime_bridge.c` `2a3ad84b…04d04df`, `control_executor.c` `40003d06…701f5f`.

## 6. 승격 작업자가 이어서 검증/판정할 것 (`loop/ESCALATE_SOL` §43)

1. **(strategy, 먼저)** PROMPT③ 절차 경고가 발효 중이다 — Step C는 7회차를 소비했고 4회 연속
   무효다. rider 라인을 **계속할지 종료할지 판정**한다. 다만 **N105 덕분에 그 판정이 싸졌다**:
   아래 2의 음성 대조 1건이 "fixture 설계 자체가 무효"인지 "headroom 가설이 살아 있는지"를
   가르며, 게임 실행 ≈2분·source 변경 0·새 카드 0으로 끝난다. middle 권고는 **음성 대조를 먼저
   돌린 뒤 판정**이다. middle은 계속/종료를 대신 고르지 않는다.
2. **(work, 승인 시 1회, W24 §5 Step C 안에서 — 새 카드 금지)** **N105 음성 대조.**
   양성대조 주문이 해소된 직후(`used=85`, headroom **4,915 ≫ 비용 10**) **같은 producer
   슬롯 1182에 op1 2차 주문을 한 건 더** 걸고 ≥3×L tick 표본화한다. 실행 **전** 고정 판정식:
   - `PRODUCER_REFUSES_SECOND_ORDER` — `reserved`가 창 내내 0 ∧ `count` 증가 0
     ⇒ 원인은 **producer 잔여 상태**이며 headroom과 무관 ⇒ **Step C rider fixture(단일 producer
     연속 주문)는 설계상 무효**이고, "지속 생산 흐름" 재설계도 **producer를 여러 기 쓰지 않으면
     같은 함정에 빠진다.** lap471 해석은 기각된다.
   - `PRODUCER_ACCEPTS_SECOND_ORDER` — `reserved`가 10이 되고 정상 해소
     ⇒ producer 잔여 상태는 원인이 아니다 ⇒ **H-headroom이 유일 생존 가설로 승격**되고
     lap471 해석이 지지된다. 이때 비로소 "지속 생산 흐름" 재설계가 의미를 가진다.
   - `CONTROL_BLOCKED` — op1이 거부되거나 PS3 진입 실패 ⇒ 정확한 reason 문자열과 장부를 적고
     끝낸다. **우회 패치·가드 완화·op4 금지.**
   금지: 이 대조는 **headroom을 건드리지 않는다**(대량 시딩 전에 실행). 두 변수를 다시 섞지 말 것.
3. **(사용자 전권, 모델 착수 금지)** **(ㄴ)** G2 한정 최소 AI/설정 변경 허용 여부, lap404
   **(가)/(나)**, F4 **(B)/(C)**, 3단 마일스톤 승인 — 전부 대기 상태 그대로다. 이번 회차는
   어느 것도 대신 고르지 않았다.

- 다음 한 가지: **strategy가 §6-1을 판정**한다(권고: §6-2 음성 대조 1건 선행). middle/work는
  그 전에 Step C rider에 새 계획 회차를 쌓지 않는다(PROMPT③ — 같은 추측 반복 금지).

## 7. 변경 파일 / 커밋 (LOOP_ALLOW_COMMITS=0 ⇒ uncommitted + 해시 보존, PROMPT⑤)

게임 코드·제품 코드·`patches/`·`tools/` 변경 **0**. 문서/에스컬레이션만 갱신했다.

| 파일 | 회차 종료 시 sha256 |
|---|---|
| `docs/STATUS.md` (108줄) | `42e89ca8a9bb7aa39fb6abf13db13b2abfe33bc40b2b079c1f65abf66278b972` |
| `docs/feedback/INBOX.md` (392줄) | `c4c1abba68f36cc4ec4bb8ac97182b23eb73bb778f3153e0c9083690acc30b3c` |
| `loop/ESCALATE_SOL` (§43 추가) | `9078abd095e72c716b3216953f4a82f7322a27f541de67b4c09442107d1f4d20` |
| 이 기록 파일(§7 추가 전) | `b0b9c7d67a0b944b817a424c20b88e569845ebf8c57bbe5ab037368722237ee3` |
| `docs/history/20260922_inbox_lap472_precompaction.md` (390줄) | `87ac134e9ed85703724e21b0c5188f243dd216ab0c36f78e19655e8d85569df2` |
| `docs/history/20260922_status_lap472_precompaction.md` (94줄) | `4a8fb1ae8a0c9dc70f774a42f019fb6c84427dac9c1054d71d9954ff8ac5bb3b` |

재계산 산출물(메인 레포 밖, 공유 temp):
`temp/Syw2plus_patch/g2_capacity/20260922_lap472_middle_stepC_v4_recheck/recheck472.py`·
`recheck472_output.json`. 원본/참고 저장소 쓰기 0, 게임 실행 0, 잔류 프로세스 0(실행 없음).
