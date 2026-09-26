# lap451 — middle: W21 §7 Step3 대조표 독립 검수 = **ACCEPT(정정 1건)**

- 날짜: 2026-09-21 KST
- lap: 451 (`loop/.lap_counter` = 451)
- 역할/모델: **middle(중간 계획·컨펌)** — Claude Code `claude-opus-5` / high
- 목표: G2 (활성 8인 각각 전비 5000 안정성). G1/G3/G4는 INBOX 2026-09-21 00:20 지시로 범위 밖.
- 대상: lap450 work가 발행한 W21 §7 Step3 fail-closed 산출물
  `lap413_stock_comparison.md` (SHA `1a439f094f52ceccc904a01fc7169fc6fbc80533978984902b5bf787e6a7d577`)
- 게임 실행: **0회** / 제품·도구 source 변경: **0** / 커밋: **0**

## 1. 가설(= 검수 질문)

lap450이 표에 적은 **모든 수치 셀이 원시 표본으로 재계산했을 때 일치하는가**, 그리고
카드 §7이 요구한 최소 컬럼·행이 빠짐없이 채워졌는가.

## 2. 방법 — 비참조 재계산

lap449의 방법을 그대로 따랐다. **판정 입력에서 제외한 것**: lap450의 markdown 본문,
각 run의 `run_summary.json` 집계 필드, `progress.json`의 집계 필드, Root 회수 서술.
**판정 입력으로 쓴 것**: 원시 표본 파일뿐이다.

- `20260921_lap413_original_ai_production/samples.json` (21표본)
- `20260921_lap413_original_ai_production_repro2/samples.json` (16표본)
- `20260921_lap413_stock_ai_control/samples.json` (18표본)
- `20260921_lap442_repaired_p2_long_soak/samples.jsonl` (721표본)
- `20260921_lap448_..._root_recovery/samples.jsonl` (712표본)

스크립트·결과: `temp/Syw2plus_patch/g2_capacity/20260921_lap451_middle_review/`
(`recheck451.py`, `recheck451_result.json`).
fixture 행은 원시 `seed_receipts.json`과 각 run 스크립트의 goal 문자열로 따로 확인했고,
page fault 주소는 원시 표본에 없는 사실이라 lap450이 입력으로 명시한
`20260921_lap413_p2_comparison_summary.json`에서 **출처를 밝혀** 대조했다.

## 3. 결과 — 15개 수치 셀 중 14개 일치, 1개 불일치

| 셀 | lap450 표 | recheck451 재계산 | 판정 |
|---|---|---|---|
| lap413 구후보 표본 수 | run1 21 / repro2 16 | 21 / 16 | 일치 |
| stock 표본 수 | 18 | 18 | 일치 |
| lap442 / lap448 표본 수 | 721 / 712 | 721 / 712 | 일치 |
| lap413 구후보 도달 tick | 11,928(두 run) | 11,928(두 run 마지막 표본) | 일치 |
| stock 도달 tick | 13,804 | 13,804 | 일치 |
| **lap442 도달 tick** | **23,997** | **24,030** | **불일치 → N69** |
| lap448 도달 tick | 24,029 | 24,029 | 일치 |
| lap413 구후보 max live | 468(두 run 동일) | 468 / 468 | 일치 |
| stock max live | 405 | 405 | 일치 |
| lap442 / lap448 max live | 583 / 1,247 | 583 / 1,247 | 일치 |
| lap413 owner별 max used | `[20,495,593,1010,608,1208,1208,1176]`/1208 | 동일(두 run 모두) | 일치 |
| stock owner별 max used | `[20,572,848,730,350,967,966,1006]`/1006 | 동일 | 일치 |
| lap442 owner별 max used | `[20,570,1183,1111,620,1333,1698,1466]`/1698 | 동일 | 일치 |
| lap448 owner별 max used | `[5000,4995,5000,4995,4995,5000,4995,4995]`/5000 | 동일 | 일치 |
| fixture(op/자원/seed/N/goal) | 표 마지막 행 | 아래 §4 | 일치 |

부수적으로 원시 표본에서 추가 확인한 것(표의 주장은 아니지만 검수 중 계산됨):
lap442·lap448 두 soak 모두 **`live == Σ owner.count` 불일치 0건**, **live `used`>5000 0건**,
tick 단조 증가 위반 0건. lap449의 (U3)·(U2) 재계산과 독립적으로 같은 값이 나왔다.

## 4. fixture 행 원시 확인

- goal 문자열을 각 run 스크립트에서 직접 grep: lap442 = `_custom_game_chain_inject_g2_eight_seed42`
  (**구식 goal**), lap448 = `_custom_game_chain_inject_g2_eight_ai_seed42`(**신 goal**). 표와 일치.
- lap448 `seed_receipts.json` 전수: **8 owner 전부** op5 `fixture_added=138` + op6 `fixture_added=5`,
  `ok=true`/`reason=executed`, 실패 receipt 0건. 앵커는 owner당 1개씩 **8개 전부 서로 다름**
  (`(2,2),(27,2),(52,2),(77,2),(2,52),(27,52),(52,52),(77,52)`) ⇒ 카드 §4-1 "disjoint 앵커" 충족.
- 비용 산술 독립 확인: owner1 기준 `20 + 138×35 + 5×10 = 4,900` = 시딩 후 실측 `used` 4,900.
  ⇒ 표의 `cost35`/`cost10` 표기는 수치로 뒷받침된다(N67의 "99.0% 단일 type" 유보는 그대로 유효).
- 카드 §5 함정1 대비 **op5 `wanted=1` 스모크**가 시딩 전에 실행돼 `ok=true`로 기록돼 있다
  (`step1_orchestrator.log` 09:34:49). 표의 주장은 아니지만 함정 이행 증거로 남긴다.

## 5. 신규 관찰

### N69 (정정, 판정 불변) — lap442 도달 tick은 23,997이 아니라 **24,030**이다

lap450은 이 셀을 `run_summary.json.final_tick`(=23,997)에서 가져왔다. 원시 721표본의 마지막
tick은 **24,030**이고, lap442 자신의 `run.stdout`도
`tick=24030 reached STOP_TICK=24000; stopping sampler`라고 적는다. 즉 `final_tick` 필드가
**표본보다 33 tick 작게** 보고된다.

원인은 **N61과 같은 계열의 계측 버그**다 — `w20_step2_run.py`가 `tick >= STOP_TICK` 검사에서
먼저 `break`(L350~353)하고, `last_tick` 갱신(L355~356)은 그 **뒤**에 있어 마지막으로 읽은 tick이
`result["final_tick"]`(L366)에 반영되지 않는다. lap447이 Step0 샘플러에서 발견한 것과 동일한
형태이며, 이번 검수로 **lap442(W20) 산출물에도 같은 결함이 있었음**이 확인됐다.

- **판정 영향 없음**: W20 (T2) 판정은 "어느 owner도 2500/4900에 도달하지 않음"에 걸리며 tick 값에
  의존하지 않는다. 오히려 정정 방향이 유리하다 — 23,997은 카드가 요구한 24,000 **미만**이고
  실제 값 24,030은 **충족**한다. (T2)를 뒤집거나 강화하는 재채점은 하지 않는다.
- **Step1(lap448)에는 이 결함이 없다**: `w21_step1_run.py`가 L455~457에 `final_tick_seen`을
  STOP_TICK 검사 **앞**에서 기록하도록 고쳤고(N61 수리), 실제로 `final_tick`24,029 == 원시 마지막
  표본 tick 24,029다. ⇒ **N61 수리는 이번 검수로 원시 대조를 통해 독립 확인됐다.**
- 조치: 다음 work가 `lap413_stock_comparison.md`의 해당 셀을 **24,030(원시 표본 기준)** 으로
  고치고, 23,997은 "`run_summary.final_tick`, 계측 버그로 과소 보고"라고 각주로 남긴다.
  표 전체를 다시 만들지 말고 한 셀 + 각주만 고친다.

### N70 (표현 정정) — stock 열의 "정상 종료성 정지"는 관측이 아니라 해석이다

원시 18표본이 말하는 것은 `tick 13,116 live 405` → `tick 13,804 live 0`이고 그 뒤 **4표본 동안
tick이 13,804에 고정**된 것뿐이다. "정상 종료"인지, 장면 전환/게임오버로 읽기 경로가 바뀐 것인지,
다른 정지인지는 **이 산출물로 구분되지 않는다**. `progress.json`도 `stalled`로만 적는다.
⇒ 표기를 `tick 정지(13,804) + 유닛 0 관측, 정지 원인 UNKNOWN`으로 낮춘다.

**단, 대조 자체는 약해지지 않는다.** stock은 tick 11,109에 live 378, tick 12,112에 live 383으로
문제의 11,928을 **유닛이 살아 있는 채로** 지나갔다. "stock은 fault tick을 통과했다"는 주장은
원시 표본으로 지지된다. 함께 유지할 한계는 stock의 owner 최대 `used`가 1,006이라
**cap 근처를 전혀 가보지 않았다**는 점이다(표에 이미 있음).

### N65 재확인 — 아직 수리되지 않았다

`w21_step1_run.py` L551~558을 직접 읽어 verdict 식이 `fault` / `any_owner_over_5000` /
`U1_pass` / `stop_reason`만 쓰고 **`U3_pass`를 참조하지 않음**을 재확인했다. lap450은 이 수리를
하지 않았고(게임 실행 없는 표 발행 회차였으므로 정당), **Step2 재사용 전 수리 의무는 그대로 살아 있다**.

## 6. 판정

**ACCEPT(정정 1건·표현 정정 1건).** 카드 §7의 fail-closed 조건은 충족됐다 — 파일이 지정 경로에
있고, 최소 컬럼 4개·최소 행 7개가 모두 채워졌으며 빈 행이 없고, 미계측 항목은 `UNKNOWN`으로
명시돼 있다. 수치 셀 15개 중 14개가 원시 재계산과 정확히 일치하고, 1개(N69)는 원시가 아닌
집계 필드를 인용한 데서 온 과소 보고이며 어떤 판정도 바꾸지 않는다.

**N66은 이로써 CLOSED**(W19 Step4·W20 Step3·W21 Step3 3회 연속 누락이 끊겼다).
**U0~U3 판정은 재채점하지 않는다**(lap449 ACCEPT 그대로, U4 PARTIAL 그대로).
**W21 카드는 여전히 CLOSED 아니다** — (U5) 미실행이므로 **144k 발행 금지 유지**.

## 7. 다음 work로의 명시적 handoff (middle은 구현하지 않는다)

카드 §11 순서② **Step2(신후보 `a10024de…` 저장/로드 왕복)** 로 진행한다. 착수 전에 아래 3건을
같은 회차에서 처리한다. 셋 다 게임 실행 없이 되는 준비 작업이거나 Step2 run에 붙는 계측이다.

1. **N69 셀 정정**: `lap413_stock_comparison.md`의 lap442 도달 tick을 **24,030**으로 고치고
   각주 1줄 추가. **두 배치 경로(`20260921_lap450_step3_stock_comparison/`,
   `20260921_lap448_..._root_recovery/`) 양쪽을 같은 해시로 유지**한다. 새 SHA를 기록에 남긴다.
   N70 표현 정정(stock 열 "정상 종료성 정지" → "tick 정지 + 유닛 0, 원인 UNKNOWN")도 함께.
2. **N65 수리**: Step2 실행기가 W21 verdict 식을 재사용한다면 `U3_pass`를 **합에 포함**시킨다.
   판정식 (U0)~(U5) 자체는 실행 전 고정이라 **바꾸지 않는다** — 코드가 판정식을 따라오게 하는
   수리다. source를 바꾸므로 **통합 경계에서 `make check` 전체 1회**(N22, "이번 회차 source 변경
   있음"을 기록에 명시).
3. **(U4) 잔여 UNKNOWN 분리 계측**: 표본에 `/proc/<pid>/smaps_rollup`의
   `Private_Clean`/`Private_Dirty`를 추가한다. 목적은 lap449가 UNKNOWN으로 남긴
   tick 11,288~11,355 −65,760 KB 구간형 하강을 clean 페이지 축출과 게임 측 해제로 가르는 것이다.
   **이번에 새 soak를 다시 돌리라는 뜻이 아니다** — Step2 run에 필드로 얹는다.

Step2 본체 요구는 카드 §6 그대로다: marked compat(마커 `S2P1N4K1`, 파일 오프셋 `0x38`),
cap 근접 상태에서 op2→op3 1왕복, 저장 직전/로드 직후 **같은 표본 경계**의 owner별
`(count,used,reserved)` + 슬롯 단위 `(slot,internal_id,type,owner)` 전수 대조,
그리고 **로드가 상태를 실제로 교체했다는 tick 역행 증거**(없으면 "소실 0"이 "로드 무동작"과
구분되지 않는다). 경계는 lap444 §1 그대로 — 부분 증거 한정, op4 금지, 144k 발행 금지,
AI 코드/바이너리를 바꿔야 하면 즉시 strategy 재에스컬레이션.
운영: 장기 실행은 **동기 또는 root 소유 exec 세션**, **work는 자체 lap 기록을 반드시 남긴다**
(N64 — lap440·442·448 3회 연속 누락).

## 8. 이번 회차 검사

- targeted `tests/test_g2_eight_owner_setup.py` → **6 passed**
- `checks/safety.sh check` → **SAFETY_PASS**
- 원본 **직접 재해시** `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/syw2plus_original.exe`
  = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **불변**
- 두 배치 경로의 `lap413_stock_comparison.md` **SHA 동일** 재확인
  (`1a439f09…a6a7d577`, STATUS 기재와 일치)
- **이번 회차 source 변경 0** ⇒ INBOX 21:58 규칙(N22)대로 통합 `make check` 미실행
- 게임 실행 **0회**, 커밋 **0**(`LOOP_ALLOW_COMMITS=0`)

## 9. 승격하지 않는 것

이번 회차가 늘린 것은 **서술 의무(Step3)의 독립 확인 1건**뿐이다. 제품 증거는 늘지 않았다
(implementation-unchanged 계열 회차임을 스스로 기재한다 — 다음 work는 반드시 Step2 실행으로
제품/실행 증거를 만든다). G2 제품 완료 아님. 미검증: (U5) 저장/로드 왕복, (가) 자연 도달,
144k, LAN/지원 동기화, 건물 포함 구성, 전투/사망/재생산 순환, (U4) −65,760 KB 구간.
