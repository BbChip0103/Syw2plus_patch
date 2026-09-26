# W35 — G2 S0: 시딩 fixture에서 원본 target-order로 교전을 만들 수 있는가 (lap523 middle 발행)

- 발행: lap523 middle (Claude Code `claude-opus-5-5` / high), 2026-09-23 KST. 상태: **`CLOSED`(lap525 middle 독립 검수, `FEASIBLE` 일치 — §7)**.
- 실행: **work** (Claude Code `claude-sonnet-5` / high), 다음 회차. 다음 middle이 **원시 산출물로 독립 검수**한다.
- 상위 근거: `docs/work/active/G2_STRATEGY_Q8A_SEEDED_ACCEPTANCE_LAP522.md` §2·§3·§4 S0, `loop/ESCALATE_SOL` §80 J2·J5.
- 주소 근거: `analysis/memory_maps/g2_original_order_admission_contract_lap523.md`(원본 바이트 재유도, N177~N179).
- **이 카드는 교전 가능성 판정만 한다. G2 합격·A1~A8·3단 승인과 무관하다.**
  모든 산출물에 "시딩 + 스크립트 교전 입력(진단 op8)"이라고 적는다.

## 0. 경계 (위반 시 middle REJECT)

1. **J5 streak:** 이 회차는 실제 게임 실행 회차다. 실행 없이 문서·계획만 남기면 이 카드는 실패다.
   세션 시간이 부족하면 **시작하지 말고** 그 사실만 적는다. 게임은 **foreground 동기로 완주**한다(background 금지, INBOX 09-21 01:01).
2. 제품 EXE 바이트 변경 0. AI·생산·건설 로직 패치 0. op4 0회. 배제 핀 3종과 타입 허용목록 `{5,7,46}` 핀은 수정·면제하지 않는다.
3. **편 번호(`PlayerStruct+0x05`)나 다른 설정 값을 쓰지 않는다.** 비적대가 나오면 바꾸지 말고 `NOT_FEASIBLE(NF-a)`로 보고한다.
   편 변경은 설정 변경이므로 strategy/사용자 판단 사항이다.
4. 원본 SHA `b56986e0…c9c08a8ac` 전후 불변. 격리 복사본·prefix·새 Xvfb display만 쓴다. 남의 display/lock/process를 건드리지 않는다.
5. 실행은 최대 2회다. 2회째는 1회째가 **하네스 결함**(게임 fault가 아님)으로 `BLOCKED`됐고 하네스만 고쳤을 때만 허용한다.

## 1. 구현 (work) — 진단 op8을 `patches/population/runtime_bridge.c`에 추가

**`control_executor.c`의 G4 op를 쓰지 않는다**(stock 풀·owner0/1 하드코딩, N179). 새 op는 `supply_probe_poll` 안에 둔다.
그 함수는 이미 window thread 검사로 **main thread**에서만 실행된다.

- 요청: `id op=8 owner=a slot=src_slot type=tgt_slot rice=0 wood=0 used=0`. `op > 7` 가드를 `op > 8`로 바꾼다.
- 풀 주소는 반드시 리터럴 `0x66b790u`/`0x8990c8u`/`1200`으로 쓴다. `build_runtime_bridge.py --unit-pool-capacity 4001`이
  이 리터럴을 재배치 값으로 치환한다. 다른 표기(매크로·계산식)를 쓰면 치환되지 않는다.
- 호출 전에 fail-closed로 확인한다. 하나라도 어긋나면 **호출하지 않고** reason을 남긴다.
  - `0x415480` 첫 12바이트 `53 56 8B F1 57 8A 86 1C 03 00 00 84`.
  - `1 ≤ src_slot, tgt_slot < 1200`(치환 후 4001), 두 슬롯 존재, HP(`+0xB4`)>0, `+0x31C`≠0.
  - 소스 owner == a, 목표 owner ≠ a, 둘 다 0..7.
  - **N178:** `(목표 U32(+0x29C) & 0xFFFF) == tgt_slot`. 불일치면 `target_uid_slot_mismatch`.
- 호출: `((int (__attribute__((thiscall))*)(void*,DWORD,DWORD,DWORD))0x415480u)(src, tgt_x, tgt_y, tgt_uid)`.
  `tgt_x`=목표 `U16(+0x2A2)`, `tgt_y`=`U16(+0x2A4)`.
- 결과 JSON에 추가(읽기만): `raw_return`, 소스 `+0x290`·`+0x294`·`+0x634`·`+0x390`·`+0x1D8`·`+0x1D4`·`+0x384`(전/후)·`+0x388`·`+0x38C`,
  목표 `+0x1BC`·type·owner·HP, 그리고 **8 owner의 `PlayerStruct+0x00/+0x02/+0x05` byte 배열**(적대 판정 입력, N177).
- op8은 유닛 레코드와 장부에 **아무것도 쓰지 않는다**. 원본 함수만 쓴다.
- 테스트: `tests/`에 op8 계약 테스트를 추가한다. 최소 ① 시그니처 12바이트 비교 존재 ② op8 분기에 `U16(..)=`/`U32(..)=`/`U8(..)=` 대입 0건
  ③ uid 하위 16비트 == slot 검사 존재 ④ `PlayerStruct+5` 쓰기 0건 ⑤ 기존 op4 핀·허용목록 핀 무변경.
- source를 바꿨으므로 **실행 뒤 `make check` 전체 게이트**를 한 번 돈다(N22). 표적 테스트만으로 면제하지 않는다.

## 2. 실행 (게임 1회, foreground)

- 후보: `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`(N=4001). 핀 복사 금지, 현재 source로 다시 빌드해 SHA 확인(N53).
  lap523 middle이 메모리 안 재빌드로 일치를 이미 확인했으나 work도 다시 확인한다.
- 하네스: `temp/Syw2plus_patch/g2_capacity/20260923_lap497_w26_seeded_cap_proximity_144k/w26_run.py`를 **새 폴더에 복사해** 쓴다.
  기동·op7 자원·시딩(op5 type5×138 + op6 type7×5, 사분면 anchor)·표집 코드는 그대로 둔다. `STOP_TICK`과 아래 단계만 바꾼다.
  새 폴더: `temp/Syw2plus_patch/g2_capacity/<YYYYMMDD>_lap<실행lap>_w35_s0_order_engagement/`.
- 단계:
  1. 시딩 완료 → A1 수치(8 owner `used`)를 기록한다. [4900,5000] 미달이어도 **중단하지 않고** 숫자를 적는다(S0 판정 입력 아님).
  2. **기준 창 B:** op8 없이 1,000 tick을 표집한다. 전 유닛 HP 감소 사건 수 `B0`, 사망 수 `D_B`를 센다(N87 대조).
  3. **쌍 선택(Python, 읽기 전용):** owner a=0..7마다 idle(`+0x290`==1)이고 mobile combat(type row `+0x4C` bit0 ∧ `+0x5C`>0)인 소스와,
     다른 owner의 살아 있는 유닛 사이 Chebyshev 거리 최소 쌍 1개를 고른다. 동점은 소스 slot, 목표 slot 오름차순이다.
     slot ≥1200 쌍이 후보에 있으면 **최소 1쌍은 slot ≥1200을 포함**하게 고른다(없으면 없다고 적는다).
  4. **op8 최대 8회**(owner당 1회). 요청마다 결과 JSON을 원문 저장한다.
  5. **관측 창 O:** 마지막 op8부터 6,000 tick. 1초 케이던스 표본에 소스·목표의 좌표/HP/명령/존재를 싣는다. 창 전체에 W26 U2/U3 판정기를 무조건 실행한다(N135).
- 60분 상자(빌드 포함): 넘으면 그 시점 원시를 보존하고 `BLOCKED(timebox)`로 끝낸다.

## 3. 판정식 (실행 전 고정 — 사후 재채점 금지)

쌍마다 다음을 잰다.
- **F1 수락:** `raw_return`==1 ∧ `+0x384`가 바뀜 ∧ 50 tick 안에 소스 `+0x290`≠1.
- **F2 접근:** 소스 좌표가 2개 이상으로 바뀌고, 소스-목표 Chebyshev 거리 최솟값을 기록한다.
- **F3 피해:** O 안에서 목표 HP가 감소한다. 목표가 사망하면 사망 tick도 적는다. 귀속은 "주문한 쌍의 목표"까지만 주장한다(G4 선례).
- **F4 무결성:** fault/crash 0, 전 표본 `live`==Σ`count`, 라이브 `used`≤5000, 음수·int16 이탈 0, tick 역행 0.

| 라벨 | 조건 |
|---|---|
| **`FEASIBLE`** | F1∧F2∧F3을 모두 만족한 쌍 ≥1 ∧ F4 |
| `NOT_FEASIBLE(NF-a)` 비적대 | 모든 쌍이 호출 전 편 byte 동일로 판정되거나, `raw_return`==0이고 P3에서 거부됨(`PlayerStruct+5` 배열로 입증) |
| `NOT_FEASIBLE(NF-b)` 무피해 | F1 쌍이 있고 거리 ≤1을 600 tick 이상 유지했는데 F3=0 |
| `BLOCKED` | 시그니처 불일치 · 후보 SHA 불일치 · N178 불일치 · idle mobile combat 소스 0기 · fault/crash(EIP 기록, **재시도 금지**) · main thread 미도달 · 창 종료 시 접근 중(거리 감소 중)이라 F3 판정 불가 · 60분 초과 |

- 보고 의무(판정 조건 아님): `B0`·`D_B`, 쌍별 `raw_return`·거부 술어(P1~P6 중 무엇인지 결과 JSON으로 추정한 것), slot ≥1200 포함 여부, 8 owner 편 byte 배열, O 동안 비주문 유닛의 HP 감소 수.
- 부분 결과는 숫자 그대로 적는다(예: "8쌍 중 F1 5쌍, F3 2쌍").
- `FEASIBLE`이면 **다음 work가 곧바로 S1 24k 교전 순환 soak**다. 추가 계획 회차를 끼우지 않는다(strategy §4).
- `NOT_FEASIBLE`·`BLOCKED`면 같은 추측을 반복하지 않는다. 근거·대안·목표 영향을 적고 middle/strategy에 넘긴다.
  `NF-a`는 편 설정 변경이 필요하다는 뜻이므로 **strategy/사용자 회부**다(strategy 문서 §2 번복 조건과 같은 층위).

## 4. 산출물

- 원시: 표본 JSONL(증분 append+flush), 이벤트 JSONL, op8 결과 JSON 원문, 시딩 receipts, orchestrator 로그, 스크립트 사본, 각 SHA256.
- 브리지 빌드 manifest(`supply_bridge_build.json`, `unit_pool_base`=`0x0108C000`, `unit_existence_base`=`0x017B8658` 기대).
- 원본 SHA 전후, 후보 SHA, 격리 prefix·display, **잔류 프로세스 0**.
- lap 기록 `docs/history/laps/<날짜>_lap<N>_work_w35_s0_order_engagement.md`(N64 재발 금지). source 변경 파일과 전후 해시를 적는다.

## 5. 닫히는 조건

§2를 1회(예외 시 2회) 실행한다. 다음 middle이 `run_summary`의 verdict를 보지 않고 원시 표본과 op8 결과만으로 F1~F4를 재계산한다.
라벨이 일치하면 `CLOSED`다. 그 middle은 `FEASIBLE`일 때 S1 카드를 바로 발행한다(strategy §4의 A1~A8 사용, 완화 금지).

## 6. 범위 밖

- (ㄴ) AI/설정 변경, 편 번호 변경, 명령 대상 선정을 G4 AI 개선으로 포장하는 것.
- 144k(S1 ACCEPT 전 발행 금지), F4(B) 결합 후보(Q9 미결), 멀티 동기화("8인" 정의 미결).

## 7. 독립 검수 (lap525 middle, Claude Code `claude-opus-5-5` / high)

- `run_summary.verdict`를 보지 않고 `op8_results.json`·`observation_samples.jsonl`만으로 재계산했다. 결과는 owner0(src 2821→tgt 3439)가 F1∧F2∧F3, F4 PASS다.
  나머지 7쌍은 F1=0이다. ⇒ **`FEASIBLE`로 lap524 `verdict_corrected.json`과 일치하며 `CLOSED`.** 산출물 SHA는 lap524 기록과 전부 일치했다.
- 단서(판정 불변):
  - F2 좌표 변화는 목표 사망 뒤의 이동이다. 원거리 접근은 입증되지 않았다.
  - F4의 `live`/`used`는 원시 표본에 없어 집계값·하네스 코드로만 확인했다. "음수 0" 절은 검사되지 않았다.
- **거부 원인 해석은 정정한다(N181~N183, `analysis/memory_maps/g2_unit_attack_domain_flags_1d8_lap525.md`).**
  `+0x1D8`은 타입 행 `+0x4C` 고정값이다. 허용목록 {5,7,46}은 bit 0x4가 없어 1군(`+0x1BC`==1, fixture 전부)을 공격할 수 없다.
  수락 소스는 비시딩 type 110이었다. ⇒ S0는 원본 명령 경로가 재배치 슬롯에서 동작함을 입증했다. **시딩 군대끼리의 교전은 입증하지 않았다.**
- 그래서 §3의 "`FEASIBLE`이면 곧바로 S1"을 이번에는 적용하지 않는다. A8·strategy §5 허용목록 금지와 A2가 충돌하므로 strategy에 회부한다(`loop/ESCALATE_SOL` §82).
