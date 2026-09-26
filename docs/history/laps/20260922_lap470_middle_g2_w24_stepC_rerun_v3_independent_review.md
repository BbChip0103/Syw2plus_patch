# 2026-09-22 | lap470 | 목표 G2 (W24 §5 Step C 3회차 독립검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, 지정 역할 **middle**
  (진단·계획·컨펌). 게임 실행 0·게임 코드 hands-on 수정 0·source 변경 0·커밋 0.
  loop/PROMPT.md ①~⑥ 그대로 수행.
- 가설 / 사용자 관찰: STATUS 2026-09-22 "다음 한 가지" — lap469(work)의 `RIDER_NO_REPRO`를
  원시 3종(`positive_control_samples.json`/`step_c_samples.json`/`step_c_run_summary.json`)만으로
  비참조 재계산해 독립검수한다. ACCEPT 하더라도 **W24 CLOSED·144k 금지 해제·lap404(가) 재심
  종결을 자동 판정하지 말고**, lap406/412/449의 장기 미해소와의 모순을 화해시킬 다음 probe를
  지정한다(후보 h1 연속주문 progress리셋·h2 실측자원고갈·h3 producer상태차이).
  내 가설: 그 "모순"을 화해시키기 전에 **이번 run이 정말 같은 상태를 만들었는지**를 먼저 확인한다.
- 예상 PASS / FAIL 조건: 원시 재계산이 lap469 수치와 일치하면 측정 무결성 ACCEPT. 카드 §5가
  묻는 상태(“`used`가 cap에 붙은 상태”)가 원시에서 성립하지 않으면 라벨과 무관하게 REJECT.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 source 변경 **0**
  (`patches/population/runtime_bridge.c` `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
  `tools/inmm_stub/control_executor.c` `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`
  — lap469 summary의 before/after와 레포 현재 직접 재해시가 **3자 일치**).
  이번 lap 산출물은 문서 4건(이 기록·`loop/ESCALATE_SOL`§42·STATUS·INBOX)과
  `temp/Syw2plus_patch/g2_capacity/20260922_lap470_middle_stepC_v3_recheck/`
  (`recheck470.py`, `recheck470_output.json`)뿐. 커밋 0(uncommitted 보존).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 직접 재해시
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` = 핀 값 **불변**
  (`Syw2plus/조선의반격 오리지날 실행.exe`, 읽기 전용). 차량 provenance 재유도 —
  원본에 `fixed_supply_5000.patched_bytes()` 적용 SHA가 run의 `candidate_sha256`
  `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`와 **일치**, EDITS는
  `0x1B576`·`0x3FFD4` 2곳뿐 ⇒ **stock 1200 레이아웃 + cap 5000** 확정(카드 §2-3 준수).
  검수 대상 fixture는 lap469의 owner0 1인·producer 1기(op6 type46, slot1182)·op1 type7 주문 1건.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 recheck470.py`(위 temp 경로, 게임 실행 없음).
  판정 입력은 원시 3종뿐 — lap469 서술 `w24_step_c_rerun_v3.md`·`orchestrator_stepC_v3.log`·
  STATUS/INBOX 요약은 **입력에서 제외**했다. 게이트: `checks/safety.sh check`→`SAFETY_PASS`,
  `python3 checks/context_limits.py`→`CONTEXT_PASS`, targeted
  `pytest tests/test_runtime_env.py patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` → **167 passed**
  (source 미변경이므로 전체 `make check`는 2026-09-20 21:58 지시로 면제 — **이번 회차 source 변경 0**).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **REJECT = `STEP_C_PRECONDITION_NOT_MET`**
  (Step C 3회 연속 무효). 측정 무결성 자체는 **ACCEPT**. 상세 N98~N104는 아래.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **W24 CLOSED 아님 · 144k 발행 금지 유지 ·
  lap404(가) 재심 종결 안 함**(이번 run은 (가)에 증거를 **주지도 빼지도** 않는다 — N83과 같은 이유).
  **(ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤 승인은 사용자 전권 대기**, 이번 회차에
  어느 것도 대신 고르지 않았다. 나는 middle이므로 §5 수리 자체를 구현하지 않고 work로 넘긴다.
- 다음 한 가지: **work가 W24 §5 Step C를 4회차 재실행**한다(새 카드 금지, §42-5의 4개 고정 사항).
  핵심은 **cost-10 top-up으로 `used=4995`(headroom 5 < 주문비용 10)를 만든 뒤** 주문을 거는 것.

---

## 1. 측정 무결성은 ACCEPT — lap469가 고친 것은 고쳤다

lap467의 두 REJECT 사유는 실제로 해소됐고, lap469의 자기 서술 수치는 원시와 일치한다.

| 항목 | lap469 주장 | 내 비참조 재계산 | 일치 |
|---|---|---|---|
| 양성대조 표본 | 415 | 415 (tick 12‥709) | ✔ |
| L | 698 tick | 698 (주문 tick11 = `op1_positive_control_result.tick_before` → 해소 tick709) | ✔ |
| 시딩 후 장부 | `used4985, count145` | `used4985, count145` | ✔ |
| 해소 tick | 1418 | 1418 (`reserved` 10→0) | ✔ |
| 해소 시 장부 | `used4950→4960(+10), count144→145` | 동일 | ✔ |
| progress 하강 | 없음 | 0건 (109 구간: +1 100건 / 0 9건) | ✔ |
| 해소 후 재고착 | 없음(5표본) | 5표본, 재고착 0 | ✔ |
| 판정 | `RIDER_NO_REPRO` | 스크립트 고정 판별식 재적용 결과 동일 | ✔ |

`step_c_run_v3.py:558-584`의 판정 분기가 실행 **전** 고정한 3분 판별식과 **문자 그대로 일치**하고,
산출된 라벨이 그 분기의 출력임을 확인했다 — **사후 재채점은 없다.** 이 축은 ACCEPT다.

## 2. 그런데도 REJECT인 이유 — 카드 §5가 묻는 상태가 만들어지지 않았다

### N98 (결정적) — rider는 차단 영역에 **단 한 tick도** 들어가지 않았다

`step_c_samples.json` 110표본 전수 재계산:

- `max(used + reserved)` = **4,995** ≤ cap 5,000 ⇒ **`used+reserved > cap` 표본 0건**
- 라이브 `used > cap` 표본 0건
- **headroom(`cap − used`) 최소 15 / 최대 50**, 주문 비용은 **10**
- ⇒ **headroom < 주문비용인 표본 0건, 차단 영역 체류 0 tick**

대조군(이 run이 반증한다고 주장한 세 soak, 각 middle이 원시 재계산한 값):

| run | used | reserved | headroom | 주문 충당 가능? |
|---|---|---|---|---|
| lap406 (144k, owner5/6) | 5,000 | 10 | **0** | 불가 |
| lap412 (24k, owner7) | 5,000 | 10 | **0** | 불가 |
| lap449 (24k, owner4/7) | 4,995 | 10 | **5** | 불가 |
| **lap469 rider** | **4,985** | 10 | **15** | **가능** |

세 soak은 전부 headroom < 10이라 예약을 **충당할 수 없는** 상태였고, lap469는 headroom 15로
**언제나 충당 가능한** 상태였다. `RIDER_NO_REPRO`는 참이지만, **조사 대상과 다른 상태에 대해
참**이다. 카드 §5-5의 `RIDER_REPRO` 조건은 "`used`가 **cap에 붙은 상태**에서"로 시작하는데
그 전제가 성립하지 않았으므로, 세 라벨 중 어느 것도 이 run에 적용될 수 없다.

### N99 — 우연이 아니라 **구조적**이다 (시딩 기저의 양자화)

원인은 `step_c_run_v3.py:472`의 수락 게이트다:

```python
if owner0_seeded["used"] < 4900:      # 절대 하한 4900
    verdict = "RIDER_BLOCKED"
```

이 게이트는 **의미론적 조건(`cap − used < 주문비용`)이 아니라 임의의 절대 하한**을 본다.
그리고 대량 시딩은 op5 = **type 5(cost 35) 단일 기저**이므로 도달 가능한 `used`는
`85 + 35k`뿐이다. 원시로 확인: `85 + 140×35 = 4,985`이고 141번째는 `5,020 > 5,000`이라
게이트가 거부했다(`op5_bulk_result.reason = "fixture_exceeds_unreserved_supply"`, 부분충전
140기, `count 5→145`). ⇒ **cost-35 기저만으로는 잔여 headroom이 항상 15로 남아 차단 영역이
원리적으로 도달 불가능하다.** 4회차에서 게이트만 고쳐서는 안 되고 **시딩 기저를 바꿔야** 한다.

### N100 — “lap406/412/449와의 모순”은 **소멸한다**. h1~h3는 시기상조다

lap412가 확정한 기전은 "`used`가 cap 아래로 내려가야만 예약이 해소된다"이다. 이번 rider는
**시작부터 `used`가 cap보다 15 아래**였으므로 그 해소 조건을 **이미 충족한 채로 출발**했다.
즉 이번의 빠른 해소는 lap412 기전과 **모순이 아니라 정확히 그 기전이 예측하는 결과**다.

⇒ STATUS·INBOX·lap469 기록이 "액면 모순"으로 적고 화해 가설로 올린 **h1(연속주문 progress
리셋)·h2(실측 자원 고갈)·h3(producer 상태차이)는 존재하지 않는 모순을 설명하려는 것이므로
철회한다.** work는 h1~h3에 회차를 쓰지 말 것. 더 단순한 설명(h0 = 차단 전제 미성립)이 원시로
성립하며, 그것으로 전부 설명된다.

### N101 — 지연 시간이 N98을 뒷받침한다

cap 근접 주문 지연 = 1,418 − 716 = **702 tick**, 양성대조 L = **698 tick**. 차이 4 tick(0.6%).
`used=85`(headroom 4,915)일 때와 `used=4,985`(headroom 15)일 때의 생산 소요가 **사실상 같다**
⇒ 주문은 어떤 식으로도 **지연·차단되지 않았다.** 이것은 `RIDER_NO_REPRO`의 강한 확증인
동시에, 이 run이 차단 현상에 대해 **아무 정보도 주지 않는다**는 증거이기도 하다.

### N102 (서술 정정, 판정에 비영향) — “양성대조와 동일 기울기”는 측정값이 아니다

STATUS/INBOX/lap469 기록은 progress가 "양성대조와 동일 기울기 0.143266/tick"으로 올랐다고
적었다. 그러나 `positive_control_samples.json`의 표본 키는
`sample,tick,owner,rice,wood,reserved,count,used,count_cap,cap`뿐으로 **producer/progress 필드가
아예 없다** ⇒ 양성대조의 기울기는 **측정된 적이 없다.** 0.143266은 `100/698`, 즉 양성대조의
**지연 시간**에서 역산한 값이다. 정확한 서술은 "기울기 일치"가 아니라 **"지연 시간 동등"**
(N101)이다. 또 "정확히 1씩 단조 증가"도 부정확하다 — 109개 연속 구간 중 **+1이 100개, 0이 9개**
(하강 0)로 **단조 비감소**다. 이번 창에서 실측한 기울기는 `99/(1412−716) = 0.142241`.
*4회차는 양성대조 표본에도 producer 필드를 넣어 이 주장을 검증 가능하게 만들 것.*

### N103 (미보고 사실) — 창 안에서 유닛 1기가 죽었다. fixture는 정지 상태가 아니었다

원시 장부 전이는 창 전체에서 **2건**뿐인데, 그 중 첫 번째가 보고되지 않았다:

- tick **1,050**: `used 4,985→4,950 (−35)`, `count 145→144` ⇒ **cost-35 type-5 유닛 1기 소실**
- tick **1,418**: `used 4,950→4,960 (+10)`, `count 144→145` ⇒ 생산 완료(보고된 해소)

lap469 기록은 이 fixture를 "시딩 정지 상태"로 서술했으나 실제로는 **사망 이벤트를 포함**한다.
판정에는 영향이 없다(사망 이전부터 headroom 15로 이미 충당 가능). 그러나 사망은 lap412가
지목한 **바로 그 해소 조건**이므로, 4회차에서 차단 영역에 진입한 뒤 사망이 일어나면
`RIDER_REPRO`/`NO_REPRO`가 오염된다 ⇒ **창 내 `count` 감소를 별도 계측·보고하고 판정에서
분리**해야 한다.

### N104 — 관찰창 2,094 tick은 **예산이지 실현값이 아니다**

`window_ticks`(예산) = 2,094이지만 실제 `observed_window_ticks` = **729 tick**(1,445 − 716),
= 1.045×L이다(해소가 창을 조기 종료시켰으므로 절차 위반은 아니다). 그러나 STATUS·INBOX는
"창2,094tick"을 실현값처럼 적은 뒤 lap406의 16,213 tick과 나란히 놓아 **모순을 부분적으로
제조**했다. 정직한 3개 숫자는 **예산 2,094 / 실현 729 / 차단영역 체류 0**이다.

## 3. 판정과 그 귀결

- **Step C = `STEP_C_PRECONDITION_NOT_MET`** (lap462 VOID · lap466→lap467 `INCONCLUSIVE` ·
  lap469→이번 `PRECONDITION_NOT_MET`으로 **3회 연속 무효**).
- **W24 CLOSED 아님.** Step A(`BUILDING_SEEDABLE`)·B(판정기 수리+음성대조)·D(`NO_ENGAGEMENT`,
  lap465 ACCEPT)는 그대로 유효하고, **C만 여전히 미충족**이다.
- **144k 발행 금지 유지**(§38 판정5 해제 조건 미성립). 마일스톤 경계라 middle 단독 해제 금지.
- **lap404 (가) 잠정채택은 유지되며 재심도 종결되지 않는다** — 이번 run은 (가)에 대해
  **증거를 주지 않는다**(차단 현상이 발생조차 하지 않았으므로). N83과 같은 처분이다.
- **h1/h2/h3 철회**(N100). 모순이 없으므로 화해 probe도 필요 없다.
- 측정 무결성·차량 provenance·source 불변·원본 불변은 **ACCEPT**.

## 4. 승격/후속 작업자에게 넘기는 것

**(work, 다음 회차 — W24 §5 Step C 4회차. 새 카드 금지.)** `loop/ESCALATE_SOL` §42-5의 고정
사항 4개를 실행 **전에** 코드로 박고 재실행한다. 요지는 시딩 기저를 cost-10으로 마감해
`used=4,995`(headroom 5 < 주문비용 10 = lap449가 실측한 바로 그 상태)를 만드는 것이며,
`runtime_bridge.c`의 allow-list가 이미 `{5,7,46}`이라 **source 변경 없이 op6(type 7, cost 10)로
가능**하다.

**(strategy/사용자)** Step C는 이미 lap462·466·467·469 + 이번 검수로 **5회차**를 소비했다.
4회차도 전제 성립에 실패하면 rider 자체를 계속할지 strategy가 먼저 판정해야 한다(PROMPT ③).

**(사용자 전권, 모델 착수 금지)** **(ㄴ)** G2 한정 최소 AI/설정 변경 허용 여부, lap404 **(가)/(나)**,
F4 **(B)/(C)**, 3단 마일스톤 승인 — 전부 대기 상태 그대로다.
