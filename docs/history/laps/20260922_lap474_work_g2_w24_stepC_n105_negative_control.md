# 2026-09-22 | lap474 | 목표 G2 (W24 §5 Step C rider — Round 1: N105 음성 대조)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`(세션 모델), 지정 역할 **work**
  (실무). loop/PROMPT.md ①~⑥ 그대로 수행. `docs/MODEL_ROUTING.md`의 실무 대안 provider와 일치.
- 가설 / 사용자 관찰: lap472(middle)이 lap471 Step C 4회차를 측정 ACCEPT·해석 REJECT
  (`STEP_C_CONFOUNDED`)로 판정 — 차단영역 주문이 316표본 전부 `reserved=0`인 것은 확인됐으나
  (N105) producer가 직전 양성대조 주문을 **완료·미해제한 상태**(`progress=100,type=7`)였다는
  교란변수를 분리하지 못해 H-headroom(수락시점 headroom<비용이면 조용히 무시)과 H-producer
  (완료·미해제 생산을 안은 producer는 headroom 무관하게 2차 주문 거부)가 원시로 분리 불가했다.
  lap473(strategy, Fable5)이 `loop/ESCALATE_SOL`§44에서 rider 라인 계속을 판정하며 **잔여 최대
  2 work 회차 하드캡·새 카드 금지**로 Round 1을 고정했다: 양성대조 주문이 **해소된 직후**
  (`used=85`, headroom=4,915≫비용10, **headroom을 건드리지 않음**) 같은 producer 슬롯에 op1로
  **2차 주문**을 걸어 ≥3×L tick 표본화한다. 가설: 이번엔 headroom이 압도적으로 크므로,
  H-headroom이 맞다면 2차 주문이 **수락**되어야 하고(→ H-headroom 유일 생존, Round 2로),
  H-producer가 맞다면 headroom과 무관하게 여전히 **무시**되어야 한다(→ `RIDER_STOCK_REPRO_
  UNDECIDABLE_BY_FIXTURE`로 즉시 종료).
- 예상 PASS / FAIL 조건: `PRODUCER_ACCEPTS_SECOND_ORDER`/`PRODUCER_REFUSES_SECOND_ORDER`/
  `CONTROL_BLOCKED` 중 하나로 정직하게 끝나면 PASS. 게임 크래시/안전 위반/원본 변형이면 FAIL.
  판정식은 실행 전 스크립트에 고정(사후 재채점 없음, W17/W23/W24 선례 준수).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 메인 레포 변경 **0**
  (`patches/population/runtime_bridge.c` `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
  `tools/inmm_stub/control_executor.c` `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`,
  실행 전/실행 후/레포 현재 재해시 **3자 일치**). 새 스크립트/산출물만
  `temp/Syw2plus_patch/g2_capacity/20260922_lap474_work_n105_negative_control/`
  (`n105_negative_control.py`, `orchestrator_n105.log`, `n105_run_summary.json`,
  `n105_samples.json`, `positive_control_samples.json`, `death_events.json`,
  `bridge_build_n105/`). 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 재해시 동일,
  `source_unchanged=true`). 후보(`fixed_supply_5000.patched_bytes()`)
  `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`(lap462~471과 동일 벡터,
  stock1200+cap5000). 브리지 기본용량(1200, capacity 치환 없음) 빌드,
  `dll_sha256=8ee4d98fcc35b339ced9ab014a35ced0295d5353404af58997ecb133f3442530`. 격리 전체 게임 사본
  `local/runtime/20260922_140941_737205_0` + 전용 Wine prefix + 빈 Xvfb `:200`(종료 후 잔류 0,
  `/tmp/.X200-lock` 없음). goal `_custom_game_chain_inject_g2_eight_seed42`(non-AI 8인 체인, seed42).
  owner0 1인·producer 1기(op6 type46 건물, **slot1182/internal_id132254** — lap462~473과 동일
  결정론적 슬롯)·양성대조 op1 type7 주문 1건·**같은 producer에 2차 op1 type7 주문 1건**(headroom
  미접촉). op4(장부 직접 write) 0회.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 n105_negative_control.py --display :200`(동기 실행,
  세션이 직접 대기, background 미사용). 로그 `orchestrator_n105.log`. 게임 실행 **1회**(1차 시도에서
  성공, 좌표/discriminator 재시도 불필요 — lap471과 달리 좌표는 이미 검증된 값만 사용). 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 양성대조 L=698tick(주문tick10→해소tick708, 207표본,
  lap471의 700과 오차1 이내로 결정론적 재현). 해소 직후 owner0 `used=85`(rice999,200 소비,
  cost10 정합), `headroom=cap(5000)-used(85)=4,915`(비용10의 **491.5배**, "건드리지 않음" 확인).
  같은 producer(slot1182, command=1/progress=100/production_type=7 — lap471과 **동일한 "완료·
  미해제" 상태**로 2차 주문 진입, N105 교란변수가 이번에도 그대로 존재)에 op1 2차 주문을 걸자
  `raw_return=1`로 즉시 수락 응답. 관찰창(예산2,094tick=3×698, 실현730tick) 내에서 **tick1045에
  `reserved`가 10으로 실제 발화**(사망이벤트 로그와 동시 관측 — owner0 유닛 1기가 그 tick에
  자연사망, `count5→4`), tick1419에 `progress=100·reserved=0`으로 **해소**(사망으로 상쇄돼
  `count`는 순증가 없이 5→4→5로 원위치, `count_increased=false`이나 `order_fired=true`가
  결정적 신호). **판정 `PRODUCER_ACCEPTS_SECOND_ORDER`**(`order_fired=true`) — **PASS**(측정이
  정직하게 완결됨, 크래시/안전위반 없음). targeted `pytest tests/test_runtime_env.py
  patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` **167 passed**.
  `checks/safety.sh check`→`SAFETY_PASS`. `python3 checks/context_limits.py`→`CONTEXT_PASS`. source
  미변경이므로 전체 `make check`는 이번 회차 면제(2026-09-20 21:58 지시, 이번 회차 source 변경 0,
  직전 lap473이 확인한 것과 동일 source).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **이번 결과는 `loop/ESCALATE_SOL`§44가
  실행 전 고정한 대로 H-producer("완료·미해제 생산을 안은 producer는 headroom 무관하게 2차
  주문을 거부")를 **반증**하고 H-headroom("수락시점 headroom<비용이면 조용히 무시")을 **유일
  생존 가설로 승격**시킨다 — producer가 lap471과 똑같이 "완료·미해제"(`progress=100,type=7`)
  상태였음에도, 이번엔 headroom이 압도적으로 컸기 때문에(4,915≫10) 2차 주문이 실제로 발화·해소
  됐다. lap471의 `RIDER_ORDER_NOT_ACCEPTED`(headroom5<10, `reserved` 316표본 전부 0)와 이번
  `PRODUCER_ACCEPTS_SECOND_ORDER`(headroom4,915, `reserved`가 실제로 10까지 발화)의 **유일한
  통제 차이가 headroom**이므로, 원본 Train() 경로는 producer의 진행 상태와 무관하게 수락 시점
  headroom<주문비용일 때만 조용히 무시한다는 해석이 이번 대조로 지지된다. **단, 이것은 work의
  측정 결과이며 middle의 원시 재계산 독립 검수가 아직 없다** — `n105_samples.json`(관찰창
  전체)·`positive_control_samples.json`·`death_events.json`·`n105_run_summary.json`만으로
  `order_fired`/`headroom_before_second_order`/`resolved_tick`을 재계산해야 한다. §44에 따라
  ACCEPTS 결과는 **Round 2를 정확히 1회 허용**한다(producer≥2기·각 1주문 지속생산 최소 재설계) —
  단 이는 다음 middle 독립검수 뒤 착수해야 한다(PROMPT③ "한 바퀴 한 가지 가설/변경", 이번 lap은
  Round 1 하나만 수행). 잔여 하드캡은 **이번 소비 후 1 work 회차**. (ㄴ)·lap404(가)/(나)·
  F4(B)/(C)·3단 사용자 마일스톤 승인은 여전히 사용자 전권 대기, 모델 미착수. W24 CLOSED 아님,
  144k 금지 유지(§38 판정5 불변).
- 다음 한 가지: 다음 middle이 이 run의 원시 산출물만으로 `PRODUCER_ACCEPTS_SECOND_ORDER`
  (`order_fired=true`, tick1045 `reserved=10` 발화, tick1419 해소, `headroom_before_second_order
  =4915`)를 독립 재계산한다. ACCEPT 시 §44가 예약한 **Round 2**(같은 producer 또는 신규
  producer가 **동시에 ≥2건**의 주문/생산 흐름을 유지하는 최소 재설계 — lap406/412/449가 관측한
  "수만 tick 지속되는 reserved=10"이 headroom 부족의 **지속적 재현**인지 검증)를 다음 work
  회차가 실행한다. REJECT 시 원인(교란변수 재발 여부 포함)을 정리하고 strategy 재판정을 요청한다.
