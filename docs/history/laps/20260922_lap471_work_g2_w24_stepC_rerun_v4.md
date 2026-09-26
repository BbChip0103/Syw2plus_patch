# 2026-09-22 | lap471 | 목표 G2 (W24 §5 Step C 4회차)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 지정 역할 **work**
  (실무). loop/PROMPT.md ①~⑥ 그대로 수행.
- 가설 / 사용자 관찰: lap470(middle)이 lap469 Step C 3회차를 `STEP_C_PRECONDITION_NOT_MET`으로
  REJECT했다 — 측정은 무결했으나(N98) rider가 차단 영역(`used+reserved>cap`)에 단 한 tick도
  들어가지 않았다(headroom 15 ≥ 주문비용 10). 원인은 구조적(N99): cost-35 단일 기저 시딩은
  `85+35k`만 도달하므로 `used=4,985`(headroom15)에서 양자화되어 멈춘다. STATUS/`ESCALATE_SOL`§42-6
  이 실행 **전** 고정한 4가지: (i) op6(type7,cost10) 1기 top-up으로 `used=4,995`(headroom5<주문비용10)
  를 만든다, (ii) 수락 게이트를 `used<4900` 절대하한에서 `cap-used≥주문비용⇒RIDER_BLOCKED`(전제
  미성립) 의미론적 게이트로 바꾼다, (iii) 예산(3×L)/실현/`ticks_in_blocking_regime`(체류)을 분리
  보고한다, (iv) 양성대조 표본에 producer 필드를 넣고(N102) 창 내 `count` 감소(사망)를 별도
  기록한다(N103). 가설: 이 4가지를 적용하면 lap412 기전이 옳은 경우 `RIDER_REPRO`
  (`used+reserved=5,005>5,000` 유지·progress 정체), 옳지 않으면 `RIDER_NO_REPRO`(후보 고유 회귀)
  중 하나로 판정된다.
- 예상 PASS / FAIL 조건: 세 판정(`RIDER_REPRO`/`RIDER_NO_REPRO`/`RIDER_WINDOW_INSUFFICIENT`) 중
  하나로 정직하게 끝나면 PASS. 게임 크래시/안전 위반/원본 변형이면 FAIL. **실제 결과는 이 셋
  어디에도 속하지 않는 4번째 상태였다(아래 참고) — 사후 재채점 없이 그 상태를 정직하게 보고한다.**
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 메인 레포 변경 **0**
  (`patches/population/runtime_bridge.c` `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
  `tools/inmm_stub/control_executor.c` `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`,
  실행 전/실행 후/레포 현재 재해시 **3자 일치**). 새 스크립트/산출물만
  `temp/Syw2plus_patch/g2_capacity/20260922_lap471_work_stepC_rerun_v4/`
  (`step_c_run_v4.py`, `orchestrator_stepC_v4.log`, `step_c_run_summary.json`, `step_c_samples.json`,
  `positive_control_samples.json`, `death_events.json`, 그리고 discriminator 결함이 드러난
  1차 시도 원문을 보존한 `attempt1_stale_progress_false_positive/`). 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 재해시 동일).
  후보(`fixed_supply_5000.patched_bytes()`) `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`
  (lap462~470과 동일 벡터, stock1200+cap5000). 격리 전체 게임 사본
  `local/runtime/20260922_134627_427834_0` + 전용 Wine prefix + 빈 Xvfb `:199`. goal
  `_custom_game_chain_inject_g2_eight_seed42`(non-AI 8인 체인). owner0 1인·producer 1기
  (op6 type46 건물, slot1182)·양성대조 op1 type7 주문 1건·차단영역 op1 type7 주문 1건.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 step_c_run_v4.py --display :199`(동기 실행,
  세션이 직접 대기, background 미사용). 로그 `orchestrator_stepC_v4.log`. 총 3회 게임 실행:
  (1) top-up anchor `(100,100)`이 이번 run의 지도(140×140이 아님 — `(50,50)`은 유효, `(100,100)`은
  `invalid_fixture_coordinates`로 거부)에서 무효라 `RIDER_BLOCKED`로 조기 종료, (2) anchor를
  `(20,40)`으로 정정해 재실행했으나 **discriminator 결함**(아래 참고)으로 `RIDER_NO_REPRO` 오판정 —
  원문은 `attempt1_stale_progress_false_positive/`에 보존, (3) discriminator 수정 후 재실행해
  아래 최종 결과를 얻음. 캡처 없음(화면 비교 아님).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **전제(headroom<주문비용)는 이번에 처음으로 성립했다**
  — 양성대조 L=700tick(주문tick9→해소tick709, 209표본), 시딩 `used=4,985`(cost-35×140), top-up
  1기(op6 type7 cost10)로 `used=4,995`, **headroom=5 < 주문비용10** ⇒ (ii) 게이트 통과, 차단영역
  주문 배치. **그러나 주문은 창 전체(719→2,825tick, 2,106tick 실현, 예산2,100)에서 단 한 번도
  `reserved>0`이 되지 않았다** — `reserved`는 316표본 전부 `0`, `count`는 증가한 적이 없다
  (146→142, 자연사망 4건으로만 감소). producer의 `progress`(항상 100)·`production_type`(항상7)은
  **직전 양성대조 주문이 완료된 값이 그대로 고정**되어 있었을 뿐, 이번 차단영역 주문이 실제로
  시작됐다는 증거가 아니다(command만 1→22→7로 흘렀는데 이는 건물의 다른 내부 상태 전이로 보이며
  `reserved`/`count`와 무관). ⇒ **`used+reserved>cap` 표본 0건**(headroom이 죽음으로 5→130까지
  회복된 뒤에도 계속 0건) ⇒ `ticks_in_blocking_regime=0`. 판정 **`RIDER_ORDER_NOT_ACCEPTED`**
  (카드 §5-5의 세 라벨 중 어디에도 속하지 않는 4번째 상태, 스크립트가 명시적으로 새로 도입 —
  `RIDER_NO_REPRO`로 오분류하지 않도록 (iv) 계측으로 잡아낸 것). **PASS**(측정이 정직하게 완결됨,
  크래시/안전위반 없음). targeted `pytest tests/test_runtime_env.py
  patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` **167 passed**.
  `checks/safety.sh check`→`SAFETY_PASS`. `python3 checks/context_limits.py`→`CONTEXT_PASS`. source
  미변경이므로 전체 `make check`는 이번 회차 면제(2026-09-20 21:58 지시, 이번 회차 source 변경 0).
  게임 실행 3회, 종료 후 이 run 소유 wine/Xvfb 잔류 0(`/tmp/.X199-lock` 없음, 프로세스 목록에 없음).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **이 결과는 lap412 기전("`used`가 cap 아래로
  내려가야 예약이 해소된다")을 반증하지도 지지하지도 않는다** — 애초에 예약이 생성된 적이 없기
  때문이다. 가장 단순한 설명(work의 잠정 해석, middle 재검수 필요): 원본 Train() 경로가 주문
  **수락 시점**에 `headroom<주문비용`이면 예약을 만들지 않고 **조용히 무시**하며, 이 거부는
  일회성(그 뒤 headroom이 죽음으로 회복돼도 재시도되지 않음 — 애초에 op1을 한 번만 불렀으므로).
  이것이 사실이라면, lap406/412/449가 본 "reserved=10이 수만 tick 지속"은 **이 fixture(사후
  top-up 뒤 단발 주문)로는 재현 불가능한 별종 메커니즘**이다 — 그 실제 8인 AI 소크에서는 주문이
  headroom≥비용이던 시점에 이미 수락돼 예약이 생성된 뒤, **다른 동시 생산**이 그 사이 cap을
  다 써버려 완료 시점에 정산이 막혔을 가능성이 높다(단발/사후 top-up이 아니라 **지속적 동시
  생산 흐름**이 필요한 구조). 이 해석은 **work의 잠정 판단이며 middle의 독립 검수·판정 대상이다.**
  **절차 경고(카드 §42-6-2 그대로 인용):** Step C는 lap462·466·467·469·470 + 이번으로 **6회차**를
  소비했다. 이번은 처음으로 전제(headroom<비용)를 만드는 데 성공했으나 `RIDER_REPRO`/
  `RIDER_NO_REPRO` 어느 쪽도 아닌 카드가 예상하지 못한 4번째 상태로 끝났다 — **카드 §5의 판정
  체계 자체가 이 결과를 다루지 못하므로, 다음 middle의 원시 재계산 뒤 strategy가 rider 자체를
  계속할지(fixture를 "지속 생산 흐름" 구조로 재설계) 중단할지 판정해야 한다**(PROMPT③, 카드가
  이미 예고한 절차). work는 이 판단을 대신하지 않는다. (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자
  마일스톤 승인은 여전히 사용자 전권 대기, 모델 미착수.
- 다음 한 가지: 다음 middle이 이 run의 원시 산출물(`step_c_samples.json`,
  `positive_control_samples.json`, `death_events.json`, `step_c_run_summary.json`)만으로
  `RIDER_ORDER_NOT_ACCEPTED` 판정(특히 `reserved` 316표본 전부 0, `order_fired=false`,
  `count_increased=false`)을 독립 재계산한다. 그 뒤 middle/strategy가 위 "일회성 수락 시점 거부"
  해석을 검증하고, W24 §5 Step C의 rider fixture를 지속 생산 흐름 구조로 재설계할지 아니면 이
  rider 라인 자체를 strategy 판정으로 종료할지 결정한다. work는 새 카드 없이 같은 추측을
  반복하지 않는다.
