# W26 — G2 gate-legal 시딩 cap 근접 **144k** soak (lap496 middle 발행)

> **상태: `CLOSED` (2026-09-23, lap498 middle / Claude Code `claude-opus-5` / high).**
> lap497(work)이 §1을 1회 실행해 `CAP_PROXIMITY_STABLE_144K`(부분 증거)를 산출했고,
> lap498 middle이 `run_summary.json`을 열지 않고 `samples.jsonl`(4,287행)·`events.jsonl`(6행)
> 원시만으로 U0~U3·U6와 종합 판정식을 재구현해 재계산한 결과 **불일치 0**으로 §4 종결 조건을 충족했다.
> U4는 lap498이 `UNKNOWN` → **(a) 호스트 페이지 회수**로 해소(§1 U4 수리 의무 이행).
> **신규 N141(8 owner 전원 정지 — 이 soak이 잰 것은 "부하 지속"이 아니라 "정지 상태 생존") ·
> N142(U6 3건 중 자연발생 동형은 owner4/7 2건뿐, owner2는 다른 현상) · N143.**
> 이 카드의 어떤 수치도 §0 item1대로 **G2 제품 완료나 3단 사용자 마일스톤 승인을 대체하지 않는다.**
> 전문 `docs/history/laps/20260923_lap498_middle_w26_independent_recheck.md` · `loop/ESCALATE_SOL` §61.
> 후속은 §61 **Q7**(strategy/사용자 전권)이며 middle은 후속 work 카드를 발행하지 않았다.

- 발행: lap496 middle (Claude Code `claude-opus-5` / high), 2026-09-23 KST. 상태: **`CLOSED`(lap498)**.
- 실행 역할: **work** (Claude Code `claude-sonnet-5` / high). 이 카드는 middle이 쓴 계획이며
  middle은 구현하지 않는다. work가 실행하고 **다음 middle이 원시로 독립 검수**한다.
- 발행 근거(3조건 전부 충족): `G2_SETTLEMENT_BLOCKAGE_PREPROOF_COUNTERFACTUAL_R_LAP494.md`(W28-R) §8 —
  ① ≥600tick 관측 완주(R-1 기준선, 실측 **610**) ② middle 원시 독립검수 **ACCEPT**(lap496, 불일치 0)
  ③ 새 무결성 위반(음수·랩·풀 손상) **0**. 경계 `loop/ESCALATE_SOL` §57-6 → **§59**.
- 축의 상위 근거: `ESCALATE_SOL` §51 판정①(“**W26 = 144k seeded cap-proximity soak**, W21 Step1과 같은
  축, tick144,000”), §38 판정((ㄱ) 채택 = gate-legal 시딩을 G2 증거 축으로 인정).
- 선행 실측 기준선: W21 Step1(lap448 실행 / lap449 middle ACCEPT) — 후보 `a10024de…` N=4001,
  8 owner, tick24,029까지 `CAP_PROXIMITY_STABLE`(**부분 증거**).
  전문 `docs/history/laps/20260921_lap449_middle_g2_w21_step1_independent_review.md`.

## 0. 이 카드가 사는 경계 (lap444 §1 승계 · 위반 시 middle REJECT)

1. **(나) 직접 시딩 단독으로 G2 완료를 주장하지 않는다.** STATUS·산출물·요약의 모든 기재는
   **“부분 증거(cap 근접 안정성, 전투 축 미시험, 시딩 fixture)”** 로만 한다.
   **3단 사용자 마일스톤 확인을 대체하지 않는다.**
2. 시딩은 **gate-legal**(op5/op6이 원본 생산 gate `0x43EDA0`을 실제 호출하고 반환 슬롯을 검증).
   **op4(장부 직접 write)는 이 카드에서 전면 금지**다 — 배제 핀 3종
   (`tools/runtime_env.py:5837` `"op4_used": False` / `tests/test_g2_stock_stress.py:20`
   `assert "request(4" not in SOURCE` / `tests/test_g2_eight_owner_setup.py:166`
   `"op4" not in block.lower()`)을 **유지·수정·면제하지 않는다.**
   (W28-R이 op4를 쓴 것은 기전 probe 한정의 예외였고 그 카드와 함께 닫혔다.)
3. **혼합 구성 최소 2계층**: op5(type5, cost **35**)와 op6(type7, cost **10**)를 함께 쓴다.
   **알려진 범위 한계(숨기지 말 것):** 브리지 fixture에 **건물 계층이 없다.** DESIGN §G2가 요구하는
   “건물 포함” 구성은 이 카드로 **충족되지 않으며** (가) 경로의 몫이다. 산출물에 명시한다.
4. **AI/생산 정책/게임 바이너리 변경은 범위 밖**이다. 필요해지는 순간 즉시 strategy 재에스컬레이션
   (lap444 §2). 이 카드 범위는 fixture/설정/계측뿐이다.
5. 실행은 **게임 1회 · foreground · 동기**. background 금지(INBOX 2026-09-21 01:01).
   144k는 W21 Step1(24k, 실측 ≈33tick/s·N133)의 6배이므로 **벽시계 70~90분 규모**다.
   모델 세션이 직접 기다려 완주하고 산출물 갱신을 확인한 뒤 회차를 끝낸다.
   세션 시간이 부족하면 **시작하지 말고** 그 사실을 STATUS에 적는다 — 중간 종료는 `PARTIAL_SOAK`이며
   완주로 쓰지 않는다.

## 1. 실행 전에 고정하는 판정식 (사후 재채점 금지 · W21 §1에서 STOP_TICK만 변경)

| 이름 | 값 | 비고 |
|---|---|---|
| `STOP_TICK` | **144,000** | §51이 고정한 축. 유일한 변경점 |
| cap | **5,000** | 실행 전 PS3에서 확인 |
| 시딩 대역 | live `used` ∈ **[4900, 5000]** / 8 owner | U1 |
| 후보 | `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68` | **핀 복사 금지 — 현재 source 재빌드로 SHA 확인(N53)** |
| 표집 | W21 Step1과 동일 케이던스 | 간격 min/max/mean 보고 의무 |

- **(U0) owner0 활성**: owner0의 `(used,count)`가 단일값에 고정되지 않고 증가하면 PASS.
  FAIL이면 **“8인”을 주장하지 않고** “7인 + 미활성 1”로 기재하고 **진행한다**(중단하지 않는다).
- **(U1) cap 근접 도달**: 시딩 종료 시점 **8 owner 전부** live `used` ∈ [4900, 5000]. 도달 owner 수를 적는다.
- **(U2) cap 근접 안정성**: U1 이후 **tick ≥ 144,000** 까지 fault/crash/read failure **0**
  ∧ 라이브 `used > 5000` 표본 **0건**.
- **(U3) 장부 정합**: 전 표본 `live == Σ owner.count`. 1건이라도 불일치면 FAIL.
- **(U4) 메모리**: RSS 하강을 (a) 호스트 페이지 회수 (b) 게임 측 해제 (c) 미해명 중 하나로 귀속.
  귀속 실패는 `UNKNOWN`으로 남기고 FAIL로 세지 않되 **해명됐다고 쓰지 않는다.**
  **lap449 §160-161 수리 의무 승계:** 표본에 `/proc/<pid>/smaps_rollup`을 실어 잔여 UNKNOWN을 가른다.
- **(U6, 신규) 정산 게이트 관측**: 매 표본에서 owner별 `used+reserved>cap`를 판정하고,
  성립 owner마다 **연속 지속 tick**을 추적한다(§2-N136). 값은 판정 조건이 아니라 **보고 의무**다.

**종합 판정 (사전 고정):** `U1 ∧ U2 ∧ U3` = **`CAP_PROXIMITY_STABLE_144K`(부분 증거)** /
U1 미달 = `SEED_SHORTFALL` / U2 위반 = `CAP_PROXIMITY_UNSTABLE`(= 새 결함, **즉시 중단·에스컬레이션**) /
완주 전 종료 = `PARTIAL_SOAK`(도달 tick과 사유 필수, 완주로 쓰지 않는다).

- **N65 수리 의무(실행 전).** W21 Step1 실행기 `w21_step1_run.py:551-558`의 verdict 식은
  `fault`/`any_owner_over_5000`/`U1_pass`/`stop_reason`만 쓰고 **`U3_pass`를 쓰지 않는다.**
  같은 스크립트를 재사용하면 U3가 깨진 run도 `CAP_PROXIMITY_STABLE`을 출력한다.
  **종합판정 식에 `U3_pass`를 넣고**, 넣었음을 산출물에 명시한다.
- **F4 게이트 유지:** int16 랩·음수·포인터 손상 관측 시 **즉시 STOP**하고 (B) 재심으로 회부한다
  (§38에서 (C) 채택 상태). 관측 자체를 숨기거나 baseline을 고쳐 통과시키지 않는다.

## 2. 반드시 싣는 미결 위험 (W28-R §8 의무 기재 — 삭제·축약 금지)

이 카드의 어떤 수치도 아래 미결 위험을 닫지 않는다. 검수자는 이 목록을 판정 입력으로 쓴다.

- **N120** — 비균형 종결: `reserved 10→0`과 동시에 `used −10`인데 수락이 `used`에 올린 적 없는 비용이다.
  종결 1건당 **유령 headroom 10**이 생기며 **자연 발생 여부 UNKNOWN**. 이 soak에서 발생하면 전이를 기록한다.
- **N121** — 임계 교정 결함: `SETTLEMENT_BLOCK_REPRO`류 임계를 “주문→해소 L”로 잡으면 대조군 대비
  176배 초과도 null이 된다. 확정 임계는 **N124**가 대체한다.
- **N123** — 이 계보는 **N68을 재현하지 못한 run이 있다**(N68은 24k 무기한, lap483은 529tick 뒤 종결).
  H-gate/H-place는 **병존**한다.
- **N124 · N125** — 대조군 지연 “0tick”은 표집 해상도 한계값이며, 확정 차단 임계는 **`T_block`=200tick**.
  lap483 표적 arm은 tick1414~1936의 79표본 전부가 5중 신호였다.
- **N126~N130** — W27 계보의 서술·계측 결함(동일 트랜잭션 창 서술 철회 / R1 자기모순(N128) /
  빈 배열을 사건 0건으로 보고(N129) / §4 7단계 미실행(N130)). **전부 W28-R에서 수리·해소됐으나
  같은 실수의 재발 금지 항목으로 남긴다.**
- **N131~N134** — 서술 정정(N131), 대조군 특이도의 정량화(N132), tick 속도 ≈33tick/s(N133),
  `progress==100` 표본이 종결 이후에도 이어짐(N134 — **이 soak의 progress 기반 해석에 직접 영향**).
- **N135** — 무결성 분류기가 **조용히 꺼진** 결함(lap491에서 596tick 동안 `ledger_reverted_by_engine`이
  검사된 적 없었다). **이 카드의 모든 fail-closed 장치는 창 전체에서 무조건 실행돼야 하며,
  “빈 배열 = 사건 0건” 보고를 금지한다**(관측 표본 수와 함께 보고).
- **N87** — 전투/사망/슬롯 재사용 축은 **기하(fixture)로 만들 수 없음이 실측**됐다(24k 내내 셀 단위
  인접인데 소실 4기/1,166기). 이 soak도 **전투 축은 시험하지 않는다.**
- **W23 A1 `DECAYED`** — 자연 도달은 fixture/config 축에서 `NOT_FEASIBLE` 확정. 이 카드는 시딩 축이다.
- **`used`/`reserved` 기반 수치는 전부 “부분 증거” 라벨을 강제**한다(W28-R §8 승계).

### N136 (신규, lap496) — W28-R이 확정한 기전은 **N68을 그대로 설명한다**

W28-R 확정 라벨 `SETTLEMENT_RESUMED_AFTER_HEADROOM`(strong, 2tick)의 실질은
**“정산 단계가 장부 `used`를 cap에 재검사한다”**(H-gate 지지)이다. 그런데 N68 실측은
lap448 24k soak에서 owner4·owner7이 **`(used 4995, reserved 10)`** 로 `used+cost=5005>cap 5000`인
상태를 **마지막 표본까지 해소하지 못한 것**이었다 — W28-R이 인위적으로 만든 차단 조건과 **동형**이다.
⇒ N68은 “미해명 이상”이 아니라 **확정된 정산 cap 재검사의 예상된 귀결**로 읽어야 한다.

**단 과대해석 금지:** W28-R은 op4로 장부를 **인위 desync**시켜 만든 기전 probe다. 기전이 존재함은
확정이나, **cap 근접에서 그 기전이 자연 발생한다는 것까지 증명하지는 않았다**(N123 병존 유지).
**(U6)이 바로 그 간극을 이 soak에서 직접 측정한다** — 시딩만으로(op4 없이) `used+reserved>cap`가
생기고 그것이 `T_block`=200tick 이상 지속되면, 그때 비로소 자연 발생이 실측된다.

**이것은 사용자 전권 대기 중인 lap404 (가)/(나)에 직접 입력을 주지만, 모델은 고르지 않는다.**
(U6) 결과를 수치로 적고 되물음 항목에 증거만 추가한다.

## 3. 산출물·보고 의무

- `temp/Syw2plus_patch/g2_capacity/<YYYYMMDD>_lap<실행lap>_w26_seeded_cap_proximity_144k/`
  에 원시 표본 JSONL(증분 append+flush), 이벤트 JSONL, run summary, orchestrator 로그,
  스크립트 사본, 각 SHA256.
- 원본 exe SHA 전후 확인(`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`),
  후보/브리지 SHA 기록, 격리 prefix·전용 Xvfb display, **잔류 프로세스 0 확인**.
  `/home/dev_00/.wine_syw2_baseline`·`:2`와 겹치지 않게 하고 **남의 display/lock을 정리하지 않는다**(§55).
- source 변경 0을 before/after 일치로 증명한다. 이 저장소는 `unborn` HEAD이므로 git 항목은 해당 없음을
  명시한다. source를 바꿨다면 면제를 주장하지 말고 **전체 게이트**를 돌린다(2026-09-20 21:58 지시 + N22).
- **lap 기록을 반드시 남긴다**(N64 재발 금지). 표집 간격 min/max/mean과 표본 수를 함께 적는다.

## 4. 이 카드가 닫히는 조건

§1을 **1회** 실행 → 다음 middle이 **원시만으로** 재계산(`run_summary`의 `verdict`/`reason`과 work의
파생 보조 필드 미참조) → 종합 판정 확정 시 `CLOSED`.
`CAP_PROXIMITY_UNSTABLE`이면 즉시 중단·원인 카드 우선이며 144k 재시도는 strategy 판정 사항이다.

## 5. 범위 밖 (모델이 착수하지 않는다)

- (ㄴ) G2 한정 최소 AI/설정 변경 — **사용자 전권 대기.**
- lap404 (가)/(나) 전비 장부 pending 초과 마감 방식 — **사용자 전권 대기**((U6)은 증거만 더한다).
- F4 (B)/(C) — §38에서 (C) 채택, 랩/음수 관측 시 즉시 STOP 후 (B) 재심.
- 3단 마일스톤 사용자 승인 — 모델의 기술 컨펌과 구분한다.
- 건물 계층 구성·전투 축·자연 도달 — 전부 이 카드 밖이며 (가)/(ㄴ)의 몫이다.
