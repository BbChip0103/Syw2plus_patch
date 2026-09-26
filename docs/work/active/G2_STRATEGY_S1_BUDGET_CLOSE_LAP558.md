# G2 strategy — W43R 종료 규칙 적용·S1 예산 폐쇄·사용자 재질문 (lap558)

- 판정: lap558 strategy (Claude Code `claude-opus-5-5`/high, INBOX 2026-09-23·2026-09-24 14:34 라우팅 "strategy는 claude-opus-5-5 유지"), 2026-09-24 KST.
- 입력: lap557 middle `REJECT / BLOCKED(harness_contract)`(`ESCALATE_SOL`§111), lap555 raw(`temp/Syw2plus_patch/g2_capacity/20260924_lap555_w43r_fresh_s1_2stage_24k/`), lap554 판정 §5 종료 규칙(`G2_STRATEGY_W43R_FRESH_BUDGET_LAP554.md`).
- 이 문서는 게임 코드·하네스·기준을 바꾸지 않는다. 기준 A1~A8′·허용목록 {5,7,46,2}·후보 SHA 그대로. G2 제품 합격·사용자 마일스톤 승인이 아니다.

## 1. 판정

**lap554 §5를 문구대로 적용한다. S1 스크립트 교전 트랙의 모델 권한 실행 예산은 `CLOSED`다. strategy 예외 재허가는 하지 않는다.**
라벨은 `BLOCKED(harness_contract)`이며, 이는 **제품 `NOT_FEASIBLE`이 아니다.** 제품/원본 결함 증거는 없고 네 짝 전열 배치의 존재 여부는 `UNKNOWN`이다.
다음은 사용자 질문 Q10(§4)이다. 답이 오기 전 게임 재실행·하네스 수리·anchor 변경·24k/144k는 하지 않는다(STOP).

## 2. 근거

1. **raw 독립 재확인(lap558).** `layout_plan.json` `a05934d5…dd70`, `seed_receipts.json` `feb6d3b9…64ca`, `t0_positions.json` `cb7003c0…7413`, 하네스 `43be0aa8…d14f`, `run_summary.json` `acea400f…3938`가 lap557·§110 기록과 일치한다. 계획↔실제를 따로 다시 셌다: type2는 owner0~5 일치·6/7 불일치, type46은 8/8 불일치, gap 점유 pair(0,1)=52(전부 type46)·(2,3)=2·(4,5)=0·(6,7)=67(type46 50+owner6 type2 17). 시딩 호출은 owner마다 type2→type46이다(`w43_run.py:1660-1674`). lap557 결론과 같다.
2. **사전 등록 규칙.** lap554 §5는 W43R이 `BLOCKED(harness_contract)`로 끝나면 예산을 닫고 (가)(나)(다)를 다시 묻는다고 실행 **전에** 정했다.
3. **예외 연장 계보.** 이 경로에서 strategy는 이미 네 번 "마지막 실행"을 스스로 늘렸다: lap538(W40 "마지막") → lap542(W41 "마지막") → lap545(W41R "결과와 무관하게 마지막") → lap554(W43R, 실패 시 폐쇄). 같은 역할이 다섯 번째로 규칙을 풀면 정지 규칙이 의미를 잃는다. 사용자 2026-09-15 11:46 지시("안 될 것 같으면 빠르게 보고")와 11:35 지시(하네스 보수에 머무는 운영 교정)도 같은 쪽을 가리킨다.
4. **실패 원인은 도구다.** 그래서 선택지에 "도구를 고쳐 1회" (마)를 **사용자 선택지로** 올린다. strategy가 고르지 않는다. 옛 (가)(나)(다)만 물으면 가장 싼 길을 가린 부정확한 질문이 된다.
5. **문서 회차 연속.** lap557(middle)·lap558(strategy) 두 회차 연속으로 제품·실행 증거가 늘지 않았다. PROMPT ③에 따라 세 번째 문서 회차를 만들지 않고 사용자 응답 전 STOP한다.

## 3. 신규 관찰 N206 (가설, 실행 미검증)

lap555에서 type46 anchor는 type5/type7과 같은 띠 anchor였다: owner0~3 `(2|27|52|77, 2)`, owner4~7 `(…, 52)`(`seed_receipts.json`). 띠 유닛이 rows2~8·52~58을 먼저 차지하므로 type46(3×3)은 그 아래로 밀려 실제 rows **9~25**와 **59~72**를 채웠다. planner가 고른 pair 행 13/21/23/31·59/67이 정확히 그 폭포 구간에 있었다.
footprint와 명령 순서를 정확히 모사해도 **type46 anchor를 고정하면** 네 짝이 들어갈 행이 모자랄 수 있다. 대략 계산하면 rows 26~33은 8행이고 34~44는 N202 지형 제약이 있다. rows 45~51은 7행이며 73~99는 27행(9행 짝 세 개)이다. 지형 마스크 원시가 저장된 적이 없어(lap547 지적) 오프라인으로 확정할 수 없다.
따라서 (마)를 고르면 **planner가 type46 anchor도 live mask로 함께 고르게** 해야 성립 가능성이 생긴다. 이것은 추측성 anchor 변경이 아니라 H29 탐색 범위 확장이다.

## 4. 사용자 질문 Q10 (모델은 고르지 않음; strategy 권고는 (마))

- **(가)** G2 한정 최소 AI 변경 예외((ㄴ)).
- **(나)** "8인"을 사람 슬롯으로 보고 fixture 재구성(가능성 미조사).
- **(다)** S1 교전 트랙 중단. 교전·사망·재생산 없는 "안정 동작"으로 G2 해석이 약해진다.
- **(마) 신규·권고:** 시험 도구만 고쳐 fresh 게임 **정확히 1회**. 게임·AI·기준은 바꾸지 않는다. 비용은 work 1회(게임 약 15~25분 포함)와 middle 1회다. 결과가 middle `ACCEPT`+교전 성립이 아니면 **추가 질문 없이** 사용자가 함께 지정한 대체안((가)/(나)/(다) 중 하나)으로 넘어간다. strategy 추가 예외는 없다.

**답 형식 권고:** "(마), 실패 시 (다)"처럼 대체안까지 한 번에 주면 재질문 회차가 사라진다.

## 5. (마) 선택 시 work 계약 (지금은 실행 금지 — 사용자 답 뒤 다음 work가 계획 회차 없이 바로 착수)

1. 파생 원본: lap555 `w43_run.py` SHA `43be0aa8…d14f`. 새 비중첩 temp 디렉터리 `g2_capacity/<date>_lap<lap>_w43r2_s1_2stage_24k/`. 기존 lap552/lap555 raw·`bridge_build`는 건드리지 않는다.
2. **H29′ 모델 수리:** (a) 실제 명령 순서 그대로 owner0→7마다 type2→type46을 replay한다. (b) 각 type의 width/height로 원본 `FUN_0042ECB0` full footprint를 점유한다(type46 3×3, `runtime_bridge.c:176-223` 근거). all-type2-first·1셀 모사는 금지다. (c) type46 anchor도 탐색 변수로 둔다. 조건은 모든 pair의 source/target/gap 행과 footprint가 겹치지 않는 것이다. 후보 순서는 결정적으로 고정하고 raw에 남긴다.
3. **raw 보강:** T0 전 terrain·occupancy 원시 mask를 저장하고 SHA를 기록한다. middle이 오프라인으로 planner를 재실행할 수 있어야 한다.
4. **폐루프 gate:** owner마다 시딩 직후 실제 좌표를 읽어 계획과 비교한다. 첫 불일치에서 op9 전에 `BLOCKED(gate:layout_drift)`로 끝낸다. 실행 중 재계획·anchor 추측 보정은 금지한다.
5. **게임 전 회귀:** lap555 입력으로 기존 planner의 false-complete(owner0 type46 첫 divergence)를 재현하는 테스트를 만든다. 수정 planner는 같은 입력에서 false-complete를 내지 않아야 한다. 가능한 경우 lap555 실제 type46 좌표를 footprint 모사로 재현해야 한다. mask가 없어 재현할 수 없는 부분은 `UNKNOWN`으로 적는다. 이어 합성 회귀·계약 테스트·핀 4건(`9548de80…`,`2a8aa4f7…`,`b0b89e0c…`,`695631f1…`)·`SAFETY_PASS`를 확인한다.
6. **실행:** fresh prefix·빈 display·foreground **1회**, 재시도 0. 남은 시간이 25분 미만이면 시작하지 않고 기록한다. H29′에 완전해가 없으면 시딩 없이 `BLOCKED(gate:no_four_pair_layout)`로 끝난다. 이것은 현재 fixture 지형에서 네 짝 배치가 불가능하다는 실측 결론이며, 사용자 지정 대체안으로 넘어간다.
7. 이후 절차는 lap554 §4-5와 W43 카드의 A1~A8′·라벨 우선순위를 그대로 따른다. 새 middle ACCEPT와 `DRIVEN_CYCLE_STABLE` 전에는 144k를 열지 않는다. N205 사전 등록도 유지한다.

## 6. 사용자 통지 문안 (INBOX 게시본과 동일 취지)

W43 재실행은 교전 전 배치 단계에서 무효가 됐다. 원인은 게임이 아니라 우리 시험 도구가 유닛 배치를 잘못 예측한 것이다. 건물형 유닛(type46)이 3×3칸을 차지하는데 도구는 1칸으로 셌고, 배치 순서도 실제와 달랐다.
실행 전에 정한 규칙대로 모델 판단으로 하는 재시도는 여기서 멈추고 여쭙는다. 도구만 고쳐 한 번 더 하는 안(마)을 권하지만, 이 경로에서 "마지막 1회"를 이미 여러 번 늘렸으므로 사용자가 정해 주셔야 한다.
