# G2 strategy — S1 폐쇄 뒤 다음 한 가지: W44 혼합 구성 안정 동작 24k + 저장/로드 (lap561)

- 판정: lap561 strategy (Claude Code `claude-opus-5-5`/high, INBOX 2026-09-23 strategy 모델 교체 · 2026-09-24 14:34 "strategy는 claude-opus-5-5 유지"), 2026-09-24 KST.
- 입력: lap560 middle `ACCEPT / BLOCKED(harness_budget)`(`ESCALATE_SOL`§114), 사용자 Q10 `(마), 실패 시 (다)`(APPROVALS 2026-09-24 19:02), lap522 판정 §3~§4, W21(lap452/453)·W26(lap497/498) 기록.
- 이 문서는 게임 코드·브리지·하네스를 바꾸지 않는다. G2 제품 합격이나 사용자 마일스톤 승인이 아니다. 사용자가 번복할 수 있다.

## 1. 판정

1. **S1 스크립트 교전 트랙은 사용자 지정 `(다)`로 닫는다.** lap559 raw 3종(`96e2ea97…c65c`/`e7534fa5…d1e`/`882a8dd5…80f`)과 raw 원본/후보(`b56986e0…a8ac`/`a10024de…2d68`)를 다시 해시해 §113·§114와 같음을 확인했다. op8/op9 교전 입력, H29/H29′ planner, 24k 교전 soak은 새 사용자 지시 없이는 되살리지 않는다.
2. **`(다)`의 뜻(lap558 §4 원문):** "교전·사망·재생산 없는 안정 동작으로 G2 해석이 약해진다." 이 약화는 사용자가 골랐다. 모델은 DESIGN §2 G2 원문을 고치지 않는다. 3단 제출문에 "전투·사망·재생산 축은 Q10 (다)로 시험 제외"라고 적고 사용자가 판정한다.
3. **남은 G2 축 대조(`(다)` 적용 후, 같은 후보 `a10024de…`):**

| 축 | 기존 증거 | 상태 |
|---|---|---|
| A1 8/8 cap 근접(시딩) | W21·W26·lap552·555·559 모두 8/8 [4900,5000] | 있음 |
| 24k | W21 Step1(lap448/449) | 있음(건물 없음) |
| 144k | W26 `CAP_PROXIMITY_STABLE_144K`(lap498), N141 "정지 상태 생존" | 있음(건물 없음) |
| 저장/로드 | W21 Step2 1,161슬롯 무손실(lap453) | 있음(건물 없음) |
| **혼합 구성(건물 type46 포함) 안정 동작+저장/로드** | lap552만 해당하나 op8/op9 교전 입력이 섞였고 run 전체가 `REJECT`(lap553) | **없음 → 다음 한 가지** |
| S3 F4(B) 통합 | 후보 `1893ff50…` 실행 0 | Q9 사용자 대기 |
| S4 멀티 동기화 | 없음 | "8인" 정의 사용자 대기 |

4. **다음 한 가지 = W44 work 1회(`FEASIBLE`).** DESIGN "대표적인 저전비 다수/고전비 군대/건물/효과 혼합으로 시험한다"는 `(다)`와 무관하게 남는다. 근거: 시딩 A1 4950×8·A8′ 8/8은 lap552/555/559 세 번 재현됐다. op2/op3 저장/로드는 같은 후보에서 lap552가 필드 일치로 동작했다. W44는 기존 하네스에서 교전 부분을 **빼는** 작업이다.
5. **144k는 새로 열지 않는다.** 같은 후보 W26 144k가 있다. 혼합 구성 144k 추가 여부는 S5 제출에서 사용자가 고른다. 이 결정으로 모델 권한 실행 예산을 더 늘리지 않는다.
6. **PROMPT ③ 무증가 streak:** lap560(middle)·lap561(strategy) 두 문서 회차다. 다음 회차는 반드시 W44 실제 게임 실행이다. 추가 계획/카드 회차는 허가하지 않는다. W44 계약은 아래 §2에 있고, work는 이 문서로 바로 착수한다.

## 2. W44 work 계약 (다음 work 회차가 계획 회차 없이 착수, 재시도 0)

1. **파생 원본:** lap555 `w43_run.py` SHA `43be0aa8f96f20429d6e6cd77b3aeac7b71bdd0e7f09550959e02cd3ed8fd14f`. lap559 H29′ 파생본은 쓰지 않는다. 새 비중첩 디렉터리 `temp/Syw2plus_patch/g2_capacity/<date>_lap<lap>_w44_stable_mixed_24k/`, 새 prefix, 사용 중이 아닌 새 display. 기존 lap552/555/559 raw·`bridge_build`는 읽기만 한다.
2. **빼는 것:** H29/H29′ planner, H30 방향 교대, op9/op8 발행, 파동(`prepare/dispatch_cycle_wave`), op1 재생산 발주, 교전 판정. 결과적으로 op1/op4/op8/op9 발행 0건이어야 하고 raw receipt로 증명한다.
3. **남기는 것(바이트 변경 최소):** PS3 진입·cap `[5000]*8` 확인·type2 row preflight·H21a 자기검증·op7 자원·시딩 순서 type5→type7→(owner별) type2→type46. **모든 type의 anchor는 owner별 띠 anchor** `[(2,2),(27,2),(52,2),(77,2),(2,52),(27,52),(52,52),(77,52)]`로 둔다(W21/W26 fixture와 같음). 수량 type5×100·type7×25·type2×60·type46×20 불변.
4. **실행 흐름:** 시딩 → T0 gate(B1·B2) → 실패 시 soak 없이 `ARM_FAIL`로 끝냄 → AI 자연 동작만으로 진행 → tick≥16,000에서 op2 저장(slot 92)·op3 로드 1회 → tick≥24,000에서 종료. 1초 간격 표본에 8 owner `(used,reserved,count,count_cap)`, coherent `live`(lap555 `coherent_counter_sample` 재사용), tick, RSS/VM/swap/host available을 남긴다. 저장 직전·로드 직후 풀 전수 스냅샷 `(slot,uid,type,owner)`을 남긴다.
5. **게임 전 검증:** import 합성 회귀(lifecycle/A5 self-test 유지 + "op1/op8/op9 호출 경로 없음" 정적 검사 신규) PASS, W43 계약 테스트·`checks/safety.sh check`=`SAFETY_PASS`, 핀 4건(`9548de80…`,`2a8aa4f7…`,`b0b89e0c…`,`695631f1…`)과 원본 SHA 일치. 남은 시간이 30분 미만이면 시작하지 않고 기록한다. 장기 실행은 foreground로 끝까지 기다린다.

### 합격 기준 (실행 전 고정 — middle은 강화만 가능, 완화 금지)

| ID | 기준 |
|---|---|
| B1 도달 | 시딩 종료 8/8 owner 라이브 `used` ∈ [4900,5000], op5/op6만, op4 0 |
| B2 구성 | owner마다 type5·7·46·2 보유, type2 live ≥10, 단일 type 비중 ≤0.85(A8′) |
| B3 무결성 | 전 표본 라이브 `used` ≤5000, coherent `live`==Σ`count`, 음수·int16 이탈 0, `count`≤`count_cap`, fault/crash 0, tick 역행은 로드 1회 외 0 |
| B4 저장/로드 | op2·op3 성공, marker 일치, 8 owner `(used,reserved,count)`·`live` 저장 직전=로드 직후, 풀 4-튜플 lost0/mismatch0/new0, 로드 시 tick 역행 관측(로드가 상태를 실제로 바꿨다는 증거) |
| B5 기간·입력 | 로드 뒤 tick ≥24,000 도달, op1/op4/op8/op9 발행 0 |
| B6 자원 | RSS/VM/swap/host available 기록, 게임 VM 단조 증가 없음. 호스트 부하 조건을 명시 |

- 보고 전용(합격 기준 아님, 사후 재채점 금지): owner별 장부 마지막 변화 tick·동결 비율(N141 비교), 자연 사망/출생 수(lifecycle 중복 제거), type46 실제 좌표.
- 라벨(우선순위 순): `RUN_ERROR` > `ARM_FAIL`(B1/B2) > `CYCLE_UNSTABLE`(B3/B6) > `SAVELOAD_FAIL`(B4) > `WINDOW_SHORT`(B5) > `STABLE_MIXED_24K`(B1~B6 PASS).

## 3. 결과 분기 (strategy 추가 예외 없음)

- **다음 middle:** summary를 입력에서 빼고 samples/스냅샷/receipt raw로 B1~B6을 독립 재계산한다.
- **ACCEPT + `STABLE_MIXED_24K`:** middle은 추가 실행 없이 S5 3단 제출문(APPROVALS 제출 양식)을 만든다. 넣을 것: W21·W26·W44 수치, N141, 미충족·제외 목록(Q10 (다)로 제외한 전투·사망·재생산 / S3 Q9 / S4 "8인" 정의 / 혼합 구성 144k 미실행). 그 뒤 STOP해 사용자 판정을 기다린다.
- **그 밖의 라벨 또는 REJECT:** 재실행하지 않는다. 결과를 제품 발견 또는 하네스 결함으로 분류해 S5 제출문에 실패로 넣고 STOP한다. `CYCLE_UNSTABLE`이 건물 포함 구성에서만 나오면 G2 제품 결함 후보로 사용자에게 보고한다.

## 4. 금지

AI/생산/건설 로직 패치, op4, 허용목록 확장, `(flags&14)` 가드 완화, 제품 EXE 바이트 변경, 144k, S1 교전 재개, lap552/555/559 raw 덮어쓰기. 새 middle ACCEPT 전 G2 PASS 주장 금지.
