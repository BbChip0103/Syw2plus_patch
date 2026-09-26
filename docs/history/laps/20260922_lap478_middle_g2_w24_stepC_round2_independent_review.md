# 2026-09-22 | lap478 | 목표 G2 (W24 §5 Step C rider — Round 2 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`(세션 모델), effort high,
  지정 역할 **middle**(중간계획·컨펌). `docs/MODEL_ROUTING.md`의 중간계획/컨펌 대안 provider와 일치.
  게임 실행 0·게임 코드 수정 0·source 변경 0·커밋 0. loop/PROMPT.md ①~⑥ 그대로 수행.
- **lap 번호 주의(기록만, 판정 무관):** `loop/.lap_counter`=**478**이고 `logs/loop-2026-09-22.log`도
  이 세션을 `LAP 478 START`로 적는다. 직전 work 세션은 **runtime lap477**이었으나 자기 기록을
  `lap476`으로 적어 기록 계열이 runtime보다 1 뒤처져 있다(그래서 `lap477` 기록 파일은 없다).
  PROMPT "현재 파일 값이 이번 runtime lap 번호"를 따라 이 기록은 **lap478**로 적고, 이전 기록의
  `lap476` 명칭은 고치지 않고 그대로 인용한다(N64 계열 — 기록/런타임 번호 불일치).

- 가설 / 사용자 관찰: 직전 work 회차(기록명 lap476)가 §44 하드캡 마지막 1회인 Round 2를 실행하고
  최종 라벨 `RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`를 제안하면서, "headroom이 충분했는데도
  두 번째 producer의 동시 주문이 조용히 소실"됐다는 제3 기전(가칭 **H-serial**)을 새 관측으로
  남기고 middle 독립검수·strategy 회부를 요청했다. 이번 회차의 질문은 둘뿐이다:
  (1) 원시 산출물만으로 5중 신호가 재계산되는가(측정), (2) H-serial 해석이 원시에서 지지되는가.

- 예상 PASS / FAIL 조건: 원시 4종만으로 비참조 재계산해 불일치 0이면 측정 ACCEPT. 해석은 원시가
  단일 기전만 지지할 때만 ACCEPT. 판정 입력에서 `round2_run_summary.json`·work 서술은 제외하고,
  오류 출처 추적과 "실행 전 고정" 확인에만 `round2_step_c_rider.py`·`orchestrator_round2.log`를 쓴다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 메인 레포 **제품/게임 코드 변경 0**.
  문서만 변경: 이 기록, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL`(§46),
  `docs/history/20260922_inbox_lap478_precompaction.md`(INBOX 압축 전 원문 보존).
  source 재해시 **3자 일치**(work 기록값·레포 현재값 동일): `patches/population/runtime_bridge.c`
  `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
  `tools/inmm_stub/control_executor.c`
  `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`. 커밋 0(uncommitted 보존).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 이번 회차는 게임 미실행.
  검수 대상 run의 원시 산출물 4종 해시(이번에 직접 계산):
  `round2_samples.json` `f43479205e43fd7bf363d37440c651894707044aa10341f72823e1a30b447eab`(669표본),
  `positive_control_samples.json` `ab0fca551976f07277a2d19abe0beecf4b461c36c088743d135f9c9224a570c3`(209표본),
  `finalization_events.json` `ff2559885f3b1197f45848620f1bc55ee3aa36935bdc3abb664064800f0d8d19`(1건),
  `death_events.json` `cc3b5767a62d1846a812eef2e50c5ff41478a8217eb77f78524348ddcd3018fb`(15건).
  출처 추적용: `round2_step_c_rider.py` `fd932b851b34233e534dcf7fce7b6d2a41e13ac013dac3f983997665131236be`,
  `orchestrator_round2.log` `fa42324b1174a5c6de181435c0931fc6abc7fecf1ff2037daa6d542777424779`.

- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3`로 원시 JSON 4종 비참조 재계산(세션 내 일회성
  스크립트, 산출물 없음), `python3 -m pytest tests/test_runtime_env.py
  patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py`,
  `bash checks/safety.sh check`, `python3 checks/context_limits.py`. 캡처 없음. 게임 실행 0.

## 측정값 / 판정 — **측정 ACCEPT(불일치 0) / 해석 REJECT(`ROUND2_PRECONDITION_NOT_MET`)**

### 1. 5중 신호 재계산: 전부 일치 (측정 ACCEPT)

| 신호 | work 보고 | 이번 재계산 | 일치 |
|---|---|---|---|
| `reserved` distinct | {0,10}, 20 미도달 | {0:586표본, 10:83표본} | ✔ |
| `producer_b_command` distinct | {1} | {1:669} | ✔ |
| `producer_b_progress` distinct | {0} | {0:669} | ✔ |
| rice 징수 | B분 없음 | 창 669표본 전부 998,400 불변 | ✔ |
| finalization | 1건(A만) | 1건 tick1415 `used`4955→4965·`count`145→146 | ✔ |

추가 재계산(전부 일치): 창 tick720→6306(실현 5,586, 역행 0표본), A `command`1→15·`progress`
1→100 연속 99회 갱신 후 tick1415 `(1,100)`으로 정산, A의 L=1415−720=695(양성대조 L=708−10=**698**과
3tick 차), 양성대조 209표본 rice 999,200 불변, F4 게이트(음수·랩·32,767근접·라이브 `used`>cap)
**전부 0**, 장부 정합: 창 전체 `used` 변화 −510 = 사망 −520 + 정산 +10(16전이 전수 일치).
`producer_b_production_type`도 669표본 전부 **0**(work가 적지 않은 6번째 증인, 같은 방향).

### 2. (N111) **해석 REJECT — "headroom이 충분했다"가 원시와 어긋난다**

work의 H-serial 해석은 "B 주문 시점에도 headroom=10이 그대로였다(`used`는 주문으로 변하지 않으므로)"에
전적으로 기댄다. 그러나 **원시 주문 응답이 그것을 직접 반증한다**: 주문 B의 엔진 read `before`는
`{rice 998400, reserved 10, used 4990, cap 5000}`이다(주문 A의 `before`는 `{999200, reserved 0}`).
즉 **B가 발행된 tick719에는 A의 예약 10이 이미 장부에 올라와 있었고**, 미결 예약을 포함한
**실효 headroom = cap − used − reserved = 5000 − 4990 − 10 = 0 < 비용 10**이었다.
work가 쓴 headroom은 `used`만 본 값이라 A의 예약을 세지 않는다. ⇒ **"headroom 충분"이라는 전제가
성립하지 않으므로, 그 전제 위에 세운 H-serial은 이 run에서 지지되지 않는다.**

### 3. (N112) **실효 headroom 규칙이 4개 수락 판정 전부를 설명한다 — 새 기전은 불필요**

| 회차 | 주문 시점 `used` | `reserved` | 비용 | `used+reserved+비용` vs cap5000 | 실제 결과 |
|---|---|---|---|---|---|
| lap471 | 4,995 | 0 | 10 | 5,005 **>** 5000 | 조용히 무시(`RIDER_ORDER_NOT_ACCEPTED`) |
| lap474 | 85 | 0 | 10 | 95 ≤ 5000 | 수락·정산 |
| lap476 A | 4,990 | 0 | 10 | 5,000 **=** 5000 | 수락·정산 |
| lap476 B | 4,990 | **10** | 10 | 5,010 **>** 5000 | 조용히 무시 |

규칙 **"`used + reserved + 비용 ≤ cap`일 때만 수락"** 이 4/4를 맞히며 경계(등호)까지 맞는다.
H-headroom은 폐기가 아니라 **"실효 headroom(미결 예약 포함)"으로 정정·강화**된다. 반대로 H-serial
("owner당 동시 1건")은 **lap471을 설명하지 못한다**(동시 주문이 없었는데도 거부됨) ⇒ 단독 대체
가설이 될 수 없고, 이 run은 두 기전을 분리하지도 않았다. **H-serial은 별도 판정 대상으로 승격할
근거가 없다**(추가 기전으로 존재할 가능성 자체는 반증되지 않았다 — 분리 probe가 있어야 한다).
또 이 규칙 아래에서는 "A 정산 후 headroom이 열렸는데 B가 재개하지 않았다"는 work의 미스터리가
**미스터리가 아니다** — B의 주문은 애초에 등록된 적이 없으므로 재개할 대상이 없다.

### 4. (N113) **§45 요건 ①②는 구성상 성립 불가였다 — 이 run은 "재현 실패"가 아니라 "미시험"이다**

§45는 ①producer 2기가 각 1건을 **동시 보유** ②둘 다 수락된 **뒤** 동시 생산이 cap을 채워 정산을
막을 것을 요구했는데, 스크립트가 고른 headroom 밴드는 `[비용, 2×비용) = [10,20)`이었다.
N112 규칙 아래에서 이 밴드는 **두 번째 수락을 수학적으로 불가능하게 만든다**(첫 수락이 실효
headroom을 0으로 만든다). ⇒ 요건 ①이 성립한 적이 없고, ②의 "정산 차단"은 **시험된 적이 없다.**
따라서 STATUS/INBOX의 "§45가 겨냥한 기전은 **재현되지 않았다**"는 서술은 강하다 —
정확한 서술은 "**해당 상태에 도달하지 못해 시험되지 않았다**"이다(정정 대상).
덧붙여 이 fixture는 정산 차단을 만들 수도 없었다: `used`4,990 + 비용10 = 5,000 ≤ cap이라
tick1072의 사망(−35)이 없었더라도 A의 정산은 막히지 않는다.

### 5. (N114) **사전 고정 판정식의 잠재 결함 — 라벨이 "맞는 이유"로 나오지 않았다**

`RIDER_WINDOW_INSUFFICIENT`가 나온 실제 이유는 `final.reserved == 0`이다. 스크립트의 stuck 항을
직접 재계산하면 `stuck_a = (progress_a==100) and (stall_a 4891 > 임계 3490) = **True**`이다
(정산 후 A의 `progress`는 100에 고정되고 `last_progress_change_tick`이 1415에서 멈추므로).
⇒ (a) 스크립트가 자동 생성한 사유 문구("the other has not yet met the stuck threshold")는 **자기
출력 숫자와 모순**이고, (b) work 기록의 "A는 정산으로 소비돼 stuck 판정 대상에서 빠졌다"도
**사실이 아니다**(A는 stuck 집합 안에 있었다). 더 중요한 것은 (c) **잠재 위양성**이다 — 만약 B의
예약이 창 끝까지 남아 `reserved>0`이었다면, 판정식은 **이미 정산이 끝난 A를 증인으로** 삼아
`RIDER_REPRO`를 선언했을 것이다. 정산 완료 producer를 stuck 후보에서 배제하는 항이 없다.
이 판별자를 재사용하는 후속 probe는 이 항을 먼저 고쳐야 한다.

### 6. (N115) 부수 정정 2건(판정에 영향 없음, 기록)

- **사망 15건 = 유닛 16기.** tick3647 이벤트 1건이 `count`139→137(2기)이다. 이벤트 수 15는 맞고
  유닛 손실은 16기다(STATUS "사망 15건"은 이벤트 수로 읽어야 한다).
- **사망한 개체 중 cost-20이 1건 있다(tick2685).** 이 구성에서 cost20 개체는 op6로 놓은 type46
  건물 3기(PC/A/B)뿐이므로(초기 `count`2/`used`20 2기가 cost10 2기라면), **producer 건물 1기가
  창 도중 파괴됐을 가능성**이 있다. 표본에 producer 생존/소유 플래그가 없어 **어느 것인지 확정
  불가(UNKNOWN)**. B의 침묵은 tick720부터이므로 tick2685 사망이 원인일 수는 없지만, 이후 구간의
  `producer_b_*` 읽기가 살아 있는 개체를 읽은 것이라는 보장도 없다. 후속 probe는 producer
  생존/소유를 매 표본 계측해야 한다. (비AI 8인 체인에서 무엇이 유닛을 죽이는지도 UNKNOWN이다.)

### 7. rider 라인 종결 라벨

§44가 실행 **전** 고정한 대로 REPRO/NO_REPRO 어느 쪽에도 도달하지 못했으므로 최종 라벨
**`RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`** 에 **동의하고 rider 라인을 종료**한다(하드캡 소진,
재연장 없음). 단 §44의 종결 처분 문구를 이번 근거로 좁힌다: "허용 수단 내 판정 불능"이 아니라
**"밴드 선택으로 인해 설계된 상태에 도달하지 못했고, 도달 가능한 설계는 존재한다"**(N116).

### 8. (N116) 분리 가능한 최소 설계 — **제안만 하고 착수하지 않는다(strategy 판정 사항)**

N112 규칙이 맞다면 주문만으로는 정산 차단이 **구조적으로 도달 불가**하다(수락 시 `used+reserved
≤cap`이 보장되므로 정산도 항상 가능). lap406/412/449의 "수만 tick 미해소 `reserved`"가 성립하려면
**수락 이후에 `used`가 예약을 거치지 않는 경로로 상승**해야 한다. 이번 run이 그 경로를 이미 보유
한다: op5 시딩은 `used`를 125→4,990으로 올리면서 `reserved`를 0으로 유지했다.
⇒ 게임 1회·source 변경 0으로 결판 가능한 설계: **(i)** 실효 headroom ≫ 비용에서 op1 1건 수락
(`reserved`=10 확인) → **(ii)** 정산 전에 op5로 `used`를 `cap−비용 < used ≤ cap`까지 올림 →
**(iii)** `progress`가 100에 도달한 뒤 `reserved`가 해소되는지 ≥5×L 관측. 해소되면 정산은 cap과
무관(후보 회귀 승격 검토), 미해소면 **§45가 겨냥한 정산 차단이 처음으로 직접 재현**된다.
이 설계는 H-serial도 부수적으로 가른다(동시 주문이 없으므로 H-serial 예측은 "해소").
**§44 하드캡은 소진됐으므로 이 probe는 새 승인이 필요하다 — middle은 카드를 발행하지 않고
`loop/ESCALATE_SOL`§46으로 strategy에 회부한다.**

- 커밋 0(`LOOP_ALLOW_COMMITS` 미허용)이므로 uncommitted 문서 해시로 이력을 남긴다(이 기록 자신은 제외):
  `docs/STATUS.md` `95eaf51e0a7eb35ab0d0e3976bdab65fc1bb183eedcc9c9f872513974f027e68`,
  `docs/feedback/INBOX.md` `2e37fa65749974f291e07cc78f3a867b7b3f92d876261e8da60166f8aa7b42a2`,
  `loop/ESCALATE_SOL` `e3486659765a1e3e50b56fd67434671cc2d12486b18232a300b3d5c8b5aefe75`,
  `docs/history/20260922_inbox_lap478_precompaction.md`
  `9b66c3bda4a5189bb40c9023731ff970b80e9f705a8d7b584a4a46ac4c1c285c`.

## 검사 결과

- targeted `pytest tests/test_runtime_env.py patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` → **167 passed**.
- `bash checks/safety.sh check` → `SAFETY_PASS`. `python3 checks/context_limits.py` → `CONTEXT_PASS`.
- 이번 회차 **source 변경 0**(위 3자 일치)이므로 전체 `make check`는 면제(2026-09-20 21:58 지시 + N22).
  이것은 Fast 검사이며 실제 앱/24k/144k 증거가 아니다.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **W24 CLOSED와 144k 금지 해제는 이번 회차에서 확정하지 않는다.** §44는 "어느 분기든 W24 CLOSED는
  middle 독립검수로 확정"이라고 적었지만, 카드 본체(Step D)의 실측 결과가 `NO_ENGAGEMENT`(전투·사망·
  재사용 순환 미발생)이고 Step C는 위와 같이 **미시험**으로 끝났다. 즉 카드가 물은 "혼합 구성 +
  전투 순환에서 8인 cap 근접 안정성"에 **긍정 증거가 없다**. §38 판정5의 144k 해제 조건("카드 실행 +
  독립검수 ACCEPT")을 이 상태에 적용할지는 마일스톤 경계 판단이므로 **strategy에 회부**한다.
  보수적으로 **144k 금지는 유지**한 채 회부한다.
- lap404 (가)에 주는 증거는 이번에도 **0**이다: 창 전체 `max(used+reserved)` = **정확히 5,000**이고
  `>cap` 표본 0건이라 N68 현상(5,005/5,010)이 발생할 수 없는 구성이다(N83·§42-5·§43·§45와 동일 처분).
  (가) 잠정 채택 유지, 사용자 전권 대기.
- 미검증으로 남는 것: (a) N112 규칙의 **바이트 수준 확인**(원본 Train 경로가 실제로 `reserved`를
  더해 비교하는지 — 지금은 4개 런타임 관측의 귀납일 뿐이다), (b) 정산 차단 기전(N116 설계 필요),
  (c) producer 생존/소유 계측 부재(N115), (d) 비AI 체인에서의 사망 원인.
- (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 **여전히 사용자 전권 대기**, 모델 미착수.
- 이번 회차는 middle의 독립 검수이며, **이 검수 자체의 상위 판정은 strategy(§46)에 넘긴다.**

- 다음 한 가지: **strategy(Astra 또는 Fable)가 `loop/ESCALATE_SOL`§46의 3건을 판정한다** —
  ①W24를 CLOSED로 볼지와 144k 금지 해제 여부(Step D `NO_ENGAGEMENT` + Step C 미시험 상태에서),
  ②N116 분리 probe(게임 1회·source 0)를 새 카드로 허용할지 아니면 G2 rider 라인 전체를 접을지,
  ③H-serial을 판정 대상에서 제외(이번 권고)하는 데 동의하는지. work는 그 판정 전까지 같은
  추측을 반복하지 않는다(PROMPT③ 하드캡·새 카드 금지 준수).
