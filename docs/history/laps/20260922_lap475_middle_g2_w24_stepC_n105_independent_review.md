# 2026-09-22 | lap475 | 목표 G2 (W24 §5 Step C rider — Round 1 / N105 음성 대조 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`(세션 모델), 지정 역할
  **middle**(중간 계획·컨펌). loop/PROMPT.md ①~⑥ 수행. `docs/MODEL_ROUTING.md` 중간 역할과 일치.
  게임 실행 0·게임 코드 수정 0(컨펌 역할 경계 준수).
- 가설 / 검수 대상: lap474(work)의 Round 1 자기 판정 `PRODUCER_ACCEPTS_SECOND_ORDER`
  (`order_fired=true`, "tick1045 `reserved=10` 발화", tick1419 해소, `headroom_before_second_order
  =4915`)를 **원시 산출물만으로 비참조 재계산**한다. §44 선판정에 따라 ACCEPTS면 H-headroom 유일
  생존·Round 2 정확히 1회, REFUSES/CONTROL_BLOCKED면 즉시 종료 라벨.

## 1. 판정 입력 (원시만)

`temp/Syw2plus_patch/g2_capacity/20260922_lap474_work_n105_negative_control/`

| 파일 | SHA256 | 크기 |
|---|---|---|
| `n105_samples.json` (110표본) | `5b32973c31bcc9c29cac4f09551fabc106086beb97794263759f7027ecf47188` | 41,591B |
| `positive_control_samples.json` (207표본) | `2bbc9b5c2a31e07a7b58906aec9bbb03ee13ad0037d7897e4e3cc2977a7cc5a4` | 58,632B |
| `death_events.json` (1건) | `6cfc882955cf5cb85f68c1e552704a0094d6e544ef37a076a2ae9fb83324fa99` | 127B |
| `n105_run_summary.json` | `bdebae4fc8d86740b8246cfb68f0a47a71825bf79fb146c009b8d7c45dc1071c` | 10,604B |

**판정은 위 3종 원시 표본만으로 내렸다.** `n105_run_summary.json`·`orchestrator_n105.log`·work의
서술은 판정 입력에서 제외했고, 아래 §4의 **서술 오류 출처 추적(provenance)에만** 인용했다
(lap472가 lap471 로그를 다룬 것과 같은 처분). 교차 대조로 lap471 원시
`20260922_lap471_work_stepC_rerun_v4/step_c_samples.json`(316표본)도 재로드했다.

## 2. 측정 축 — **ACCEPT (불일치 0)**

원시만으로 재계산한 값이 work 판정과 전 항목 일치한다.

- 관찰창: 110표본, tick **716→1446**(실현 730tick), tick 단조증가, 표본 간격 4~8tick
  (역행 0건) ⇒ 창 해상도 반론이 성립하지 않는다.
- `headroom` 첫 표본 = **4,915** = `cap`5,000 − `used`85 (독립 산술 일치). 비용 10의 491.5배.
- `reserved` distinct = **{0, 10}** ⇒ 예약이 **실제로 발화했다.** `order_fired`는 110표본 전부
  `true`.
- 해소: tick **1412→1419**에서 `reserved` 10→0, `producer_command` 15→1, `progress` 99→100,
  `count` 4→5, `used` 50→60. work의 `resolved_tick=1419`와 일치.
- 양성대조(207표본, tick11→708): 해소 tick708에서 `reserved` 10→0·`count` 4→5·`used` 75→85,
  최종 producer `(cmd1, progress100, type7)`. 주문 tick10 ⇒ **L = 708−10 = 698tick**(work 값 일치).
  창 예산 `max(300, 3×698)=2,094`도 재유도 일치.
- 사망 1건: sample49 / tick1045 / `count` 5→4 / `used` 85→50(−35, N99의 cost35 기저와 정합)
  / 그 시점 `reserved`=10.
- 장부 정합: `used` distinct {50, 60, 85}. 85→50 = −35(사망), 50→60 = **+10 = 주문 비용**.
  `max(used+reserved)` = 95 ≪ cap 5,000 ⇒ 이 run은 cap 근처에 가지 않았다.
- F4 게이트: 음수·16bit 랩·32,767 근접·라이브 `used>cap` 표본 **전부 0건**.

⇒ 판정 `PRODUCER_ACCEPTS_SECOND_ORDER`는 원시에서 **재유도된다. 측정 ACCEPT.**

## 3. 신규 근거 — 수락/거부가 원시 5중으로 독립 확인된다 (N107)

work는 `order_fired=true` 하나를 "결정적 신호"로 들었으나, 원시에는 **서로 독립인 증인이 5개**
있고 전부 같은 방향이다. 이것이 이번 검수가 더한 가장 큰 값이다.

1. **`reserved` 0→10**: 양성대조 마지막 표본(tick708)이 `reserved=0`, 창 첫 표본(tick716)이
   `reserved=10`.
2. **`producer_command` 1→15**: 15는 "생산 중" 값이다. **lap471 차단영역 창 316표본에서
   `command`는 {1, 7, 22}뿐이고 15에 한 번도 진입하지 않았다**(lap472 N105의 핵심 관측).
   이번 창은 {1, 15} ⇒ 같은 producer가 이번엔 실제로 생산 상태에 들어갔다.
3. **`producer_progress` 0→100 연속 진행**: 창 표본이 0..100의 거의 모든 정수를 거치고
   `producer_last_progress_change_tick`이 716부터 1419까지 **99개의 서로 다른 값**으로 계속
   갱신된다 ⇒ 정지한 잔여 값이 아니라 **살아 움직이는 생산 타이머**다(lap471 1차 시도가
   오판했던 stale `progress=100`과 정반대의 원시 서명).
4. **자원 장부 −800**: 양성대조 전 구간 `rice`=999,200, 창 전 구간 `rice`=**998,400**.
   차 800은 1차 주문이 소비한 양(1,000,000→999,200)과 **정확히 같다** ⇒ 엔진이 2차 주문의
   비용을 실제로 징수했다. **대조적으로 lap471 창 316표본의 `rice`는 999,200에서 한 번도
   움직이지 않았다** ⇒ lap471에서는 징수 자체가 없었다(= 주문 미수락)는 독립 확증이다.
   이는 lap471의 `RIDER_ORDER_NOT_ACCEPTED` 라벨도 **소급 강화**한다.
5. **유닛 실물화**: tick1419에 `count` 4→5 **와 동시에** `used` 50→60(+10 = type7 비용)
   ⇒ 주문이 예약에서 끝난 것이 아니라 **실제 유닛으로 완결**됐다.

## 4. 해석 축 — **ACCEPT**, 단 서술 2건 정정 (N108, N109)

### N108 (정정) — "tick1045 발화"는 **사실이 아니다.** 실제 발화는 tick 716 이하다.

STATUS·INBOX·lap474 기록·`ESCALATE_SOL` 인용문이 공통으로 적은
"**tick1045에 `reserved`가 10으로 실제 발화(사망이벤트 `count5→4`와 동시)**"는 원시와 어긋난다.
`reserved`는 **창의 첫 표본인 tick716에서 이미 10**이었고, 창 전체에서 `reserved` 전이는
tick1412→1419(10→0, 해소) **단 1회뿐**이다. tick1045는 `count` 5→4·`used` 85→50인 **사망
이벤트일 뿐이며 `reserved`는 그 전후로 10에서 변하지 않았다.**

- 출처 추적: 스크립트·로그에는 이 오류가 없다. 로그는 tick1045를 `death event`로만 적었고
  verdict 문구도 발화 tick을 주장하지 않는다(`resolved_tick=1419`만 기재). 즉 **계측 결함이
  아니라 work가 로그의 사망 이벤트 줄을 발화 시점으로 오독한 서술 오류**다.
- 방향: 이 오류는 결과를 **약하게** 적은 쪽이다. 실제로는 주문 tick 직후 **1tick 이내**에
  예약이 잡혔으므로 수락은 work가 쓴 것보다 훨씬 즉각적이고 강하다. 따라서 판정 자체는
  뒤집히지 않으나, 다음 회차가 "발화까지 329tick 지연"이라는 존재하지 않는 현상을 설명하려
  드는 낭비를 막기 위해 **STATUS·INBOX에서 정정한다**(원문은 삭제하지 않고 보존).

### N109 (정정) — `count_increased=false`는 플래그 산물이고, `count`는 실제로 증가했다.

work는 "사망으로 상쇄돼 `count`는 순증가 없이 5→4→5로 원위치, `count_increased=false`"라고
적었다. 원시에서 tick1419의 `count` 4→5는 `used` +10을 동반한 **진짜 생산 완결**이다.
플래그가 false인 이유는 기준선이 사망 **이전** 값 5였기 때문이며, 유닛이 나오지 않았다는
뜻이 아니다. §3-5가 그 증인이다. 판정에는 영향 없다(`order_fired`가 이미 true).

### 해석 판정

§44가 실행 **전** 고정한 판별식 그대로 적용한다. 같은 producer(slot1182/id132254)가
**lap471과 동일한 `(cmd1, progress100, type7)` "완료·미해제" 상태**에서 2차 주문을 받았고
(양성대조 마지막 원시 표본 tick708이 그 상태를 직접 기록한다), 이번에는 수락·생산·완결했다.
⇒ **H-producer("완료·미해제 생산을 안은 producer는 headroom 무관하게 2차 주문을 거부한다")는
반증됐다.** lap472가 분리 불가로 남긴 두 가설 중 하나가 제거되므로 **H-headroom이 유일 생존
가설로 승격**한다. §44 선판정에 따라 **Round 2를 정확히 1회** 허용한다.

**범위 제한(과대 해석 금지):** 이번 run은 H-headroom을 **적극적으로 증명하지 않는다.**
경쟁 가설 하나를 제거했을 뿐이다. "수락 시점 headroom<비용이면 조용히 무시하고 그 거부는
일회성"이라는 lap471 work의 해석은 여전히 **직접 증거가 없다**. 다만 lap471 창에서 사망으로
headroom이 5→130까지 회복된 뒤에도 재발화가 없었고 rice 징수도 0이었다는 원시(§3-4)가
"일회성" 쪽과 정합하기는 한다.

### N110 (잔여 교란, 기록만) — 두 arm의 차이는 headroom 하나가 아니다

"유일한 통제 차이가 headroom"은 엄밀하게는 과장이다. 두 arm은 `used` 4,995 vs 85와 함께
**owner 유닛 수 146 vs 5**도 다르다. 다만 (a) `used`와 `count`는 headroom을 조작하면 필연적으로
따라 움직이는 **같은 조작의 부산물**이지 독립 교란이 아니고, (b) `count_cap`은 두 arm 모두
250으로 비구속(146<250, 5<250)이며 lap472가 이미 배제했고, (c) rice/wood는 두 arm 모두 충분하다.
따라서 "유닛 수 자체가 주문을 억제한다"는 제3가설만이 원리적으로 남지만 지지 증거가 없다.
Round 2 설계는 이 축을 굳이 새로 열지 말고 §44가 예약한 지속생산 재설계에만 쓴다.

### lap404 (가)에 주는 증거 — **없음**

`max(used+reserved)` = 95이고 `used+reserved>cap` 표본 0건이다. 차단 현상이 발생할 수 없는
구성이므로 **이 run은 (가)/(나) 되물음에 새 증거를 주지 않는다**(N83·§42-5·§43과 동일 처분).
`reserved=10`이 696tick 지속한 것은 정상 생산 소요 L=698과 같은 값이며 lap406/412/449가 본
"수만 tick 해소되지 않는 예약"과는 **다른 현상**이다.

## 5. 변경 파일 / source fingerprint / 커밋

메인 레포 제품 코드 변경 **0**. `patches/population/runtime_bridge.c`
`2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
`tools/inmm_stub/control_executor.c`
`40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`
— lap474 실행 전/후 기록값과 **레포 현재 재해시가 3자 일치**. 문서 4건만 변경
(이 lap 기록·`loop/ESCALATE_SOL`§45·`docs/STATUS.md`·`docs/feedback/INBOX.md`). 커밋 **0**
(`LOOP_ALLOW_COMMITS` 미설정). 원본 EXE 비접촉(`SAFETY_PASS`).

## 6. 검사

- targeted `pytest tests/test_runtime_env.py patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` → **167 passed**.
- `checks/safety.sh check` → **SAFETY_PASS**.
- `python3 checks/context_limits.py` → **CONTEXT_PASS**.
- 전체 `make check`는 면제 — **이번 회차 source 변경 0**이고 직전 lap473/474와 동일 source다
  (2026-09-20 21:58 지시 + N22 단서 준수). 이것은 Fast 검사이며 실제 앱 24k/144k 증거가 아니다.
- 게임 실행 **0회**(middle 역할).

## 7. 판정 요약

| 축 | 판정 |
|---|---|
| 측정 무결성 | **ACCEPT** (불일치 0, 독립 증인 5중) |
| 라벨 `PRODUCER_ACCEPTS_SECOND_ORDER` | **ACCEPT** |
| 해석(H-producer 반증 / H-headroom 유일 생존) | **ACCEPT** (§4 범위 제한 첨부) |
| 서술 정확성 | **정정 2건** (N108 발화 tick, N109 count 증가) |
| W24 | **CLOSED 아님**, 144k 금지 유지 |
| lap404 (가) | 증거 0, 잠정 채택 유지 |

## 8. 다음 한 가지 (work 회차, 잔여 하드캡 **1회 = 마지막**)

§44가 예약한 **Round 2**를 다음 work가 실행한다. 이번 ACCEPT로 착수 조건이 충족됐다.
목적은 lap406/412/449가 관측한 **"수만 tick 해소되지 않는 `reserved=10`"이 headroom 부족의
지속적 재현인지**를 가리는 것이다. 최소 재설계 요건:

1. producer **≥2기**가 **각각 1건**의 주문을 동시에 보유하는 지속 생산 흐름을 만든다
   (lap471~474의 단발 주문 fixture로는 원리적으로 재현 불가함이 §4에서 확인됐다).
2. 주문을 **headroom ≥ 비용인 시점에 먼저 수락시키고**, 그 **뒤에** 동시 생산이 cap을 채워
   정산을 막는 순서를 만든다(lap471 work가 세운 가설의 직접 시험).
3. 관찰창은 `reserved` 지속이 정상 생산 소요 L을 **초과**함을 보일 수 있어야 한다 —
   이번 run에서 L=698과 예약 지속 696이 사실상 같았으므로, **지속 판정 문턱을 실행 전에
   `> k×L`로 고정**한다(사후 재채점 금지).
4. 판정식·라벨(`RIDER_REPRO`/`RIDER_NO_REPRO`/`UNDECIDABLE`)은 실행 전 스크립트에 박는다.
   §3의 5중 증인(`reserved`·`command`=15·`progress` 시계열·**rice 징수 델타**·`count`+`used`)을
   전부 계측한다. 특히 **rice 델타는 이번에 발견된 가장 값싼 수락/거부 판별자**이므로 필수다.
5. 새 카드 금지·source 변경 최소·게임 실행 1회 목표. 이 회차가 **하드캡의 마지막**이며,
   REPRO/NO_REPRO 미도달이면 §44대로 `RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`로 종료한다.

Round 2 결과의 독립 검수 뒤 **W24 CLOSED 여부를 middle이 확정**하고, 그때까지 **144k 금지는
유지**된다(§38 판정5 불변). (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은
여전히 **사용자 전권 대기**이며 모델은 착수하지 않는다.

## 9. 커밋 없음 — 변경 파일 해시 (⑤ 준수)

`LOOP_ALLOW_COMMITS` 미설정이므로 커밋하지 않고 uncommitted 상태와 해시를 남긴다.

| 파일 | SHA256 |
|---|---|
| `docs/STATUS.md` (126줄) | `6808097edf53cc97602a146ecffa27774b6d0b54b5baf643ff200548d62f5ab0` |
| `docs/feedback/INBOX.md` (396줄) | `315a9232c161027ad2342f5f913c3e19c47f214c6dcda48996863a68750fd908` |
| `loop/ESCALATE_SOL` (§45 추가) | `a98f0b28a0341750c23befa9d04bc782b573e0b721cf3ad22af15ad6d0b7df94` |
| `docs/history/20260922_status_lap475_precompaction.md` (130줄) | `e3bd537501c32c35ff4eefecbb900034133b34b23057174f9b9ded58705c8369` |
| `docs/history/20260922_inbox_lap475_precompaction.md` (392줄) | `871ae0138a9e811800f216dd55d0f190634c75dae3eab3e83d38e7909804e438` |

STATUS·INBOX 압축은 전문 스냅샷 보존 후 수행했고 승인·반려·미결 근거는 삭제하지 않았다.
`loop/.lap_counter`(475)는 읽기만 했다. 에스컬레이션 없음 — 게이트 전부 통과, 원시-서술 충돌은
원시 우선으로 결정적으로 해소, 마일스톤 경계 판정(W24 CLOSED)은 이번 lap이 아니며 §44가 이
분기를 실행 전 선판정해 뒀다.
