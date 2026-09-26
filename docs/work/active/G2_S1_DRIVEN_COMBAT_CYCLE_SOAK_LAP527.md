# W36 — G2 S1: 시딩 군대끼리 원본 명령으로 교전하는 24k 순환 soak (lap527 middle 발행)

- 발행: lap527 middle (Claude Code `claude-opus-5-5` / high), 2026-09-23 KST. 상태: ~~발행, 미실행~~ → **lap528 실행 2회 모두 `ARM_FAIL`, lap529 middle 원시 재계산 일치 ⇒ `CLOSED`(예산 소진). 후속 W37 `G2_S1_DRIVEN_COMBAT_CYCLE_SOAK_R1_LAP529.md`.**
- 실행: **work** (Claude Code `claude-sonnet-5` / high), 다음 회차. 그다음 middle이 **원시 산출물만으로 독립 검수**한다.
- 상위 근거: `docs/work/active/G2_STRATEGY_Q8A_SEEDED_ACCEPTANCE_LAP522.md` §3·§4(A1~A7, S1), `docs/work/active/G2_STRATEGY_S1_FIXTURE_COMPOSITION_LAP526.md` K1~K7(A8', K5), `loop/ESCALATE_SOL` §80·§83·§84.
- 주소 근거: `analysis/memory_maps/g2_type_row_fixture_x_selection_lap527.md`(N184~N186, X 확정), `…/g2_unit_attack_domain_flags_1d8_lap525.md`(N181~N183), `…/g2_original_order_admission_contract_lap523.md`(op8 규약).
- 모든 산출물에 **"시딩 + 스크립트 교전 입력(op8)"** 이라고 적는다. 이 카드는 G2 제품 합격도 3단 승인도 아니다.

## 0. 경계 (위반 시 middle REJECT)

1. **K7 streak:** 이 회차는 반드시 S1 게임 실행으로 끝나야 한다. 게임 실행 없이 끝나면 더 쌓지 말고 STOP하고 사용자에게 보고한다.
   게임은 **foreground 동기로 완주**한다(background 금지, INBOX 09-21 01:01). 세션 시간이 모자라면 **시작하지 말고** 그 사실만 적는다.
2. 제품 EXE 바이트 변경 0. AI·생산·건설 로직 패치 0. op4 0회. 편 byte(`PlayerStruct+0x05`)·설정 값 쓰기 0.
3. 허용목록 확장은 **type 2 한 종만**이다(K6). `(flags&14)`·폭/높이 1~8·supply·accounting·lock 가드와 Place→Gate→Spawn 순서는 바꾸지 않는다.
4. 원본 SHA `b56986e0…c9c08a8ac` 전후 불변. 격리 복사본·prefix·새 Xvfb display만 쓴다. 남의 display/lock/process는 건드리지 않는다.
5. 실행은 최대 2회다. 2회째는 1회째가 **하네스 결함**(게임 fault가 아님)으로 `BLOCKED`됐고 하네스만 고쳤을 때만 허용한다. 게임 fault는 EIP를 기록하고 재시도하지 않는다.

## 1. X 확정 (정적, lap527) — **X = type 2**

- K3 규칙을 원본 초기화 코드(`FUN_0049BEB0`→`FUN_0049BAA0`, 행 = ECX)에서 그대로 적용했다(N184). 후보 6종이 모두 적격이다.
  비용은 2·3=13, 4=15, 12=17, 13=18, 10=20이다. 최저 13에서 2와 3이 동률이므로 **낮은 번호 2**를 고른다.
- type 2 행: 비용 13, 1×1, `+0x24`=0, `+0x4C`=`0x410005`(bit 0x4=1, bit 0x10=0), HP 500.
- 추출 방법의 양성 대조: type 5·7·46·110의 비용·크기·`+0x4C`가 기존 실측과 일치하고, §20 라이브 28타입의 `+0x4C`가 28/28 일치한다.
- **런타임 preflight(N185):** 시딩 전에 실행 중인 게임에서 type 2 행(`0x9B5228+2×0x394` 기준 `+0x10`,`+0x16`,`+0x18`,`+0x24`,`+0x4C`)을 읽는다.
  값이 위와 하나라도 다르면 `ARM_FAIL`로 끝낸다. 다른 후보로 바꾸지 않는다.

## 2. source 변경 (work) — repo 3파일(브리지 1 + 테스트 2) + temp 하네스 1개

1. `patches/population/runtime_bridge.c` op5/op6 조건 한 항:
   `(fixture_type != 5u && fixture_type != 7u && fixture_type != 46u)` → `(fixture_type != 5u && fixture_type != 7u && fixture_type != 46u && fixture_type != 2u)`.
   바로 위 주석에 "lap526 strategy K1/§83 + lap527 W36 §1: bit 0x4 전투 타입 type 2 추가(N182·N184)"를 한 줄 덧붙인다. 다른 줄은 바꾸지 않는다.
2. `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py`: `ALLOWLIST_RE`를 정확히 {5,7,46,2}로 바꾼다. 테스트 이름을 `…_is_exactly_5_7_46_2`로 바꾸고 docstring에 §83·이 카드를 인용한다.
   비공허 테스트는 `"fixture_type != 2u)"` → `"fixture_type != 2u && fixture_type != 99u)"` 치환이 핀을 깨는지로 바꾼다. 가드 4종 테스트는 그대로 둔다.
3. `tests/test_g2_runtime_bridge_op8_order_engagement_contract.py:129`의 허용목록 문자열 단언을 새 조건으로 바꾸고, 메시지에 "W36(lap527)에서 {5,7,46,2}로 개정"이라고 적는다.
4. 하네스: `temp/Syw2plus_patch/g2_capacity/20260923_lap524_w35_s0_order_engagement/w35_run.py`를 **새 폴더에 복사해** `w36_run.py`로 쓴다.
   기동·op7 자원·anchor·`SupplyProbe`·표집·U2/U3 판정기는 그대로 둔다. 새 폴더: `temp/Syw2plus_patch/g2_capacity/<YYYYMMDD>_lap<실행lap>_w36_s1_driven_cycle/`.
   저장/로드는 `…/20260921_lap452_w21_step2_save_load_roundtrip/w21_step2_run.py`의 op2/op3 절차(slot 92, 파일 오프셋 `0x38` 마커 확인)를 그대로 옮긴다.
- 순서: source 변경 → **`make check` 전체 1회**("이번 회차 source 변경", N22) → exit0일 때만 게임. 실패하면 게임을 시작하지 않고 `BLOCKED(gate)`로 보고한다.

## 3. fixture (실행 전 고정)

- 후보: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(N=4001, supply 5000) 계보다. 허용목록 조건이 바뀌므로 **브리지 DLL SHA는 달라진다**(lap524 `c1c7cfde…`).
  현재 source로 다시 빌드하고, 새 브리지 SHA와 `supply_bridge_build.json`(`unit_pool_base`=`0x0108C000`, `unit_existence_base`=`0x017B8658` 기대)을 기록한다. EXE SHA는 lap524와 같아야 한다(다르면 `ARM_FAIL`).
- 자원: op7로 owner마다 rice/wood 1,000,000(W35와 같음).
- 시딩(owner마다, W35 anchor 규칙, 이 순서): op5 type5×100 → op6 type7×25 → op6 type46×20 → op5 type2×60.
  - 기대 `used` = 시작 20(type110×2) + 3,500 + 250 + 400 + 780 = **4,950**. 기대 `count` = 207, 8 owner 합 1,656.
  - A8' 산술: type5 비용 비중 3,500/4,950 = 70.7% ≤ 85%, X 60기 ≥ 10기. 네 타입 모두 보유.
- 시딩 receipt가 하나라도 `ok=false`이거나, 8 owner 중 하나라도 `used`∉[4900,5000]이거나 A8'가 T0에 성립하지 않으면 **`ARM_FAIL`** 이다(숫자 그대로 기록).

## 4. 실행 절차 (게임 1회, STOP_TICK = 24,000)

T0 = 시딩 완료 tick. 표본은 1초 케이던스로 JSONL에 증분 append+flush한다.
**표본마다** tick, 8 owner `(used, reserved, count)`, `live`, 시각, 게임 프로세스 RSS/VM/swap, 호스트 MemAvailable을 **원시로** 싣는다(K5).
풀 스냅샷 차분(slot별 uid `+0x29C`·type·owner·HP)으로 HP 감소와 슬롯 소멸 사건을 이벤트 JSONL에 남긴다.

1. **preflight:** §1 type 2 행 확인. `0x415480` 첫 12바이트(`53 56 8B F1 57 8A 86 1C 03 00 00 84`) 확인.
2. **시딩:** §3.
3. **기준 창 B:** T0부터 1,000 tick 동안 op8을 보내지 않는다. 자연 HP 감소 `B0`와 사망 `D_B`를 센다. 이제 X가 있으므로 자연 자동공격이 나올 수 있다. 값이 몇이든 그대로 적는다.
4. **순환 창 E:** T0+1,000부터 STOP_TICK까지 **600 tick마다 한 파동**을 돈다. 각 파동에서 owner o=0..7 순서로 다음을 한다.
   - (a) **재생산 op1:** o의 `reserved`==0이고 `used`+10 ≤ 5000이면, o의 살아 있는 type46 중 가장 작은 slot을 producer로 op1 type7 1건을 건다.
   - (b) **X 보충:** o의 살아 있는 type2 < 10이면 op5 type2 수량 (10 − 살아 있는 수)을 요청한다. supply 가드 거부는 실패가 아니라 기록 대상이다. 보충 몫은 A4에서 따로 센다.
   - (c) **op8 (결정적 대상 규칙):** 짝 owner p = o XOR 1 (0↔1, 2↔3, 4↔5, 6↔7).
     소스 = o의 살아 있는 type2 중 idle(`+0x290`==1)인 것을 slot 오름차순으로 **최대 6기**.
     각 소스의 목표 = p의 살아 있는 type2 중 Chebyshev 거리 최소(동점은 목표 slot 오름차순). p에 type2가 없으면 p의 살아 있는 모든 유닛 중 같은 규칙.
     한 파동 안에서 같은 목표를 여러 소스가 가질 수 있다. 요청·결과 JSON은 전부 원문 저장한다.
   - 한 파동이 600 tick을 넘기면 다음 파동을 건너뛰고 그 사실을 기록한다(중단하지 않는다).
5. **저장/로드(A6):** tick ≥ 16,000에 처음 오는 파동 **직후** op2 save(slot 92) → 마커 확인 → op3 load(slot 92).
   op2 직후와 op3 직후에 8 owner `(used,reserved,count)`·`live`를 읽는다. 로드 뒤에도 파동은 STOP_TICK까지 계속한다.
6. **종료:** STOP_TICK 도달 → 최종 표본 → 게임 종료 → 잔류 프로세스 0 확인. W26 U2/U3 판정기를 창 전체에 **무조건** 실행한다(N135).
- **60분 상자(빌드·게임 포함, `make check` 제외):** 넘으면 그 시점 원시를 보존하고 `BLOCKED(timebox)`로 끝낸다.

## 5. 측정식 (실행 전 고정 — 사후 재채점 금지, middle은 강화만 가능)

- **사망 D_o** = 창 E에서 owner o 소유 슬롯이 소멸한 사건 수(uid 기준, C3). 교차 확인으로 `count` 감소(C1, op1·보충 증가분 보정)를 함께 적는다. 두 채널이 다르면 둘 다 보고하고 작은 값을 쓴다.
  - **K5 분리:** 소멸한 유닛의 uid가 그 전에 **수락된 op8의 목표 uid**였으면 `op8 기인`, 아니면 `자연 기인`이다. 둘 다 D_o에 넣고 비율을 보고한다.
- **op8 수락** = `raw_return`==1 ∧ 소스 `+0x384` 변화(W35 F1과 같음).
- **재생산 R_o** = op1 주문이 정산된 뒤(`reserved` 10→0 ∧ `count`+1) 나타난 새 type7 슬롯 중, 창 E에서 **이전에 사망한 슬롯**이고 uid가 이전 uid와 다른 것의 수.
  - **양성 대조:** owner마다 첫 op1은 receipt 또는 50 tick 안에 `reserved` 0→10을 보이고, 1,000 tick 안에 producer `production_type`/`progress`가 바뀌어야 한다(W24 PC L=698). 실패한 owner는 A3 FAIL이다(VOID 재발 금지).
- **A4 재접근:** 사망 뒤 `used`가 다시 ≥4,900에 닿은 owner 수. 그중 op1 몫과 보충(op5 type2) 몫을 따로 적는다.
- **A5 무결성(전 표본):** 라이브 `used` ≤ 5000, **`used` < 0 없음**, `reserved`·`count` 음수·int16 이탈 없음, `live`==Σ`count`, `count` ≤ 1200, tick 역행 0, fault/crash 0.
- **A6:** op2 직후 값 == op3 직후 값(8 owner 3필드 + `live`) ∧ op3 뒤 D 합이 증가.
- **A7(기록, 라벨 조건 아님):** RSS/VM/swap·tick 속도·MemAvailable 시계열. 게임 VM이 창 E 뒤 2/3에서 단조 증가하면 명시한다.

| ID | PASS 조건 |
|---|---|
| A1 | T0에 8/8 owner `used`∈[4900,5000] |
| A2 | 8/8 owner D_o ≥ 20 ∧ 각 owner의 사망이 창 E 3등분 중 ≥2구간에 있음 |
| A3 | 8/8 owner 양성 대조 PASS ∧ R_o ≥ 1 |
| A5 | 위반 0 |
| A6 | 위 조건 성립 |
| A8' | T0에 8/8 owner가 type 5·7·46·2 보유, type2 ≥10, 단일 type 비용 비중 ≤85% |

| 라벨 | 조건 |
|---|---|
| **`DRIVEN_CYCLE_STABLE`** | A1·A2·A3·A5·A6·A8' 전부 PASS |
| `ARM_FAIL` | 후보 EXE SHA 불일치 · 시그니처 불일치 · type 2 preflight 불일치 · 시딩 receipt 실패 · A1 또는 A8' 미성립 · 첫 op8 전 fault |
| `NO_ENGAGEMENT` | 무장 성공 ∧ (창 E op8 수락 0건 ∨ 8 owner D_o 합 0) |
| `CYCLE_UNSTABLE` | 무장 성공 ∧ (A5 위반 ∨ 첫 op8 뒤 fault/crash ∨ A6 불일치·로드 실패) — 하위 사유 표기 |
| `CYCLE_PARTIAL` | 무장 성공 ∧ 교전 있음 ∧ A5·A6 PASS ∧ A2 또는 A3 미달 — 숫자 그대로(예: "A2 8명 중 5명") |
| `BLOCKED` | `make check` 실패 · 60분 초과 · main thread 미도달 · 하네스 결함 |

- 여러 조건이 겹치면 우선순위는 `ARM_FAIL` > `BLOCKED` > `CYCLE_UNSTABLE` > `NO_ENGAGEMENT` > `CYCLE_PARTIAL` > `DRIVEN_CYCLE_STABLE`이다.
- `CYCLE_PARTIAL`은 이 카드가 더한 라벨이다. 합격 라벨이 아니고, 144k 사전 허가(J4)는 `DRIVEN_CYCLE_STABLE`에만 적용된다.
- 보고 의무(라벨 조건 아님): `B0`·`D_B`, owner별 D_o(op8/자연 분리)·R_o·A4, op8 요청/수락 수, 파동 건너뜀 수, 보충 요청/수락 수, 소스-목표 최소 거리 분포, A7 시계열.

## 6. 산출물

- 원시: 표본 JSONL, 이벤트 JSONL, op1/op5/op6/op7/op8/op2/op3 결과 JSON 원문, 시딩 receipts, preflight 값, orchestrator 로그, `w36_run.py` 사본, 각 SHA256.
- 브리지 빌드 manifest와 새 브리지 SHA, 원본 SHA 전후, EXE 후보 SHA, 격리 prefix·display, **잔류 프로세스 0**.
- repo 변경 3파일과 하네스의 전후 SHA256, `make check` 결과(통과 수·시간).
- lap 기록 `docs/history/laps/<날짜>_lap<N>_work_w36_s1_driven_cycle.md`. `run_summary.verdict`는 work의 자기판정이며 검수는 middle이 한다.

## 7. 닫히는 조건과 다음

- 다음 middle이 `run_summary`의 verdict를 보지 않고 원시 표본·이벤트·op 결과만으로 §5를 재계산한다. 라벨이 일치하면 `CLOSED`다.
- `ACCEPT` ∧ `DRIVEN_CYCLE_STABLE`이면 그 middle이 **같은 후보의 144k 카드 1장**을 바로 발행한다(lap522 J4). strategy 재판정은 필요 없다.
- 다른 라벨이면 144k는 닫힌 채 strategy에 회부한다. 같은 추측으로 재실행하지 않는다.

## 8. 범위 밖

- (ㄴ) AI/설정 변경, 편 변경, 두 번째 타입 추가(K6), 대상 선정을 G4 AI 개선으로 포장하는 것.
- F4(B) 결합 후보(Q9 미결), 멀티 동기화("8인" 정의 미결), G1/G4.
