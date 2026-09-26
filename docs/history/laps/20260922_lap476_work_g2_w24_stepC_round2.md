# 2026-09-22 | lap476 | 목표 G2 (W24 §5 Step C rider — Round 2, 잔여 하드캡 마지막 1회)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`(세션 모델), 지정 역할 **work**
  (실무). loop/PROMPT.md ①~⑥ 그대로 수행. `docs/MODEL_ROUTING.md`의 실무 대안 provider와 일치.
- 가설 / 사용자 관찰: lap475(middle)이 lap474 Round 1(N105 음성 대조)을 측정·해석 모두 ACCEPT해
  H-producer를 반증하고 H-headroom을 유일 생존 가설로 승격시켰다(`ESCALATE_SOL`§45). 단 Round 1은
  "같은 producer에 순차 2차 주문"만 검증했을 뿐, lap406/412/449가 실측한 "producer≥2기가 동시에
  주문을 보유한 채 cap이 정산을 막는" 지속 예약 기전 자체는 아직 검증하지 않았다. §45가 실행 **전**
  고정한 Round 2 요건 5가지: ①producer≥2기가 각 1건 동시 보유 ②headroom≥비용에서 먼저 수락시킨
  뒤 동시 생산이 cap을 채워 정산을 막는 순서 ③지속 판정 문턱을 실행 전 `>k×L`로 고정(k=5) ④판정식·
  라벨을 실행 전 스크립트에 고정하고 N107 5중 증인 전부 계측 ⑤새 카드 금지·source 변경 최소·게임
  실행 1회. 가설: 시딩된 used=4,990(headroom10, `[ORDER_COST,2×ORDER_COST)=[10,20)` 밴드)에서
  producer A/B에 각 1건씩 주문을 걸면, A가 먼저 정산돼 `used`가 5,000에 근접하고 그 뒤 B의 정산이
  cap에 막혀 `reserved`가 lap412/449처럼 수만 tick 지속될 것으로 예상했다.
- 예상 PASS / FAIL 조건: `RIDER_REPRO`/`RIDER_NO_REPRO`/`RIDER_WINDOW_INSUFFICIENT`/`CONTROL_BLOCKED`
  중 하나로 정직하게 끝나면 PASS. 게임 크래시/안전 위반/원본 변형이면 FAIL. 판정식은 실행 전
  스크립트(`round2_step_c_rider.py`)에 고정, 사후 재채점 없음(W17/W23/W24 선례 준수).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 메인 레포 변경 **0**
  (`patches/population/runtime_bridge.c`
  `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df`,
  `tools/inmm_stub/control_executor.c`
  `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f`, 실행 전/실행 후/레포 현재
  재해시 **3자 일치**). 새 스크립트/산출물만
  `temp/Syw2plus_patch/g2_capacity/20260922_lap476_work_round2_stepC_rider/`
  (`round2_step_c_rider.py`, `orchestrator_round2.log`, `round2_run_summary.json`,
  `positive_control_samples.json`, `round2_samples.json`, `death_events.json`,
  `finalization_events.json`, `bridge_build_round2/`). 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 재해시 동일,
  `source_unchanged=true`). 후보(`fixed_supply_5000.patched_bytes()`)
  `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`(lap462~475와 동일 벡터,
  stock1200+cap5000). 브리지 기본용량(1200, capacity 치환 없음),
  `dll_sha256=025c89a8a38067e8dd584472ba55fe58bd0e5d152fb715b51bb7f934feb39574`. 격리 전체 게임 사본
  `local/runtime/20260922_191104_1663801_0` + 전용 Wine prefix + 빈 Xvfb `:210`(종료 후 잔류0,
  `/tmp/.X210-lock` 없음). goal `_custom_game_chain_inject_g2_eight_seed42`(non-AI 8인 체인,
  seed42). owner0 1인·producer **3기**(op6 type46 건물 — throwaway PC용 slot1182/id132254(양성대조
  전용, lap462~475와 동일 결정론적 슬롯), Round2 producer A slot1181/id197789, producer B
  slot1180/id263324 — A/B는 이번 lap에서 처음 생성된 신규 producer)·양성대조 op1 type7 주문 1건(PC
  producer)·Round2 op1 type7 주문 2건(A·B 각 1건). op4(장부 직접 write) 0회.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 round2_step_c_rider.py --display :210`(동기 실행,
  세션이 직접 대기, background 미사용). 로그 `orchestrator_round2.log`. 게임 실행 **1회**(1차 시도
  성공, 좌표·discriminator 재시도 불필요 — 기존 검증 좌표만 사용). 캡처 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 양성대조 L=698tick(PC producer, lap471/474와 오차0
  이내로 결정론적 재현). bulk seeding(cost35×139) 후 used=4,990·headroom=10(밴드[10,20) 충족,
  top-up 0회 필요). 주문 A(tick717, slot1181)·주문 B(tick719, slot1180) 둘 다 API 레벨
  `ok=true/raw_return=1`로 "수락"됐고, **A만 실제로 진행**했다(command 1→15, progress0→100,
  tick720→1415, L=695≈PC의 698과 일치) **원시 재계산으로 독립 확인**: `round2_samples.json`
  669표본 전체에서 `reserved` distinct값은 **{0,10}뿐**(20에 도달한 표본 0건), `producer_b_command`
  distinct값은 **{1}뿐**(15 미진입), `producer_b_progress` distinct값은 **{0}뿐** — B는 주문 배치
  직후(tick720)부터 창 종료(tick6306, 5,586tick 경과, 5×L=3,490 초과)까지 **단 한 번도 진행하지
  않았다**. A가 tick1415에 정산(`used`4,955→4,965·`count`145→146 동시, `reserved`10→0)한 **뒤에도**
  B는 재개하지 않았다(A 정산으로 headroom이 다시 열렸음에도 B는 죽은 채로 남음). `finalization_
  events`는 **1건뿐**(A만). rice는 999,200→998,400=−800이 주문 A~B 배치 구간(tick717~719) 사이에
  **한 번만** 발생했고(order A 응답 자체엔 아직 반영 전, order B 응답 시점엔 이미 반영), 그 이후
  rice는 창 끝까지 불변(998,400) — **B는 rice도 전혀 징수되지 않았다**(N107 rice 델타 판별자 기준
  B는 "미수락"과 동일한 징후). F4 안전 게이트(음수·랩·32,767근접·라이브`used>cap`) 전부 0건. 사망
  15건(자연사, `used`를 145→131 단위로 서서히 낮춤, 창 종료 시 headroom=520까지 열림에도 B는
  움직이지 않음). **스크립트의 사전 고정 판정식이 실제로 산출한 라벨은 `RIDER_WINDOW_INSUFFICIENT`**
  (`finalization_events==1`이지만 B의 `progress`가 100에 도달한 적이 없어 "stuck_a/stuck_b" 조건 —
  `progress==100 and stall>5L` — 이 B에는 애초에 성립할 수 없는 구조였음; A는 정산으로 소비돼 stuck
  판정 대상에서 빠짐). **이 라벨의 자동 생성 사유 문구("window too short to distinguish slow-but-
  resolving from sustained-stuck")는 부정확하다** — B는 "느리게 진행 중"이 아니라 **창 시작부터
  끝까지 단 1tick도 진행하지 않았다**(진행값 자체가 고정, "느림"이 아니라 "정지 아님/미개시"에
  가깝다). 사후 재채점은 하지 않고 스크립트가 실제로 계산한 라벨(`RIDER_WINDOW_INSUFFICIENT`)을
  그대로 보고하되, 이 문구 부정확성을 이 자리에서 기록한다(lap475의 N108과 같은 종류의 서술 위험
  회피). targeted `pytest tests/test_runtime_env.py patches/population/test_fixed_supply_5000.py
  patches/population/test_g2_full_capacity_persistence_compat_v1.py` **167 passed**.
  `checks/safety.sh check`→`SAFETY_PASS`. `python3 checks/context_limits.py`→`CONTEXT_PASS`. source
  미변경이므로 전체 `make check`는 이번 회차 면제(2026-09-20 21:58 지시 + N22, 이번 회차 source
  변경 0).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **이 결과는 §45가 설계한 "동시 생산이 cap을
  채워 A/B 둘 다 headroom 안에서 정산을 시도하다 두 번째가 막힌다"는 가설을 재현하지 않았다** —
  `reserved`가 20에 도달한 적이 없고 B의 progress/command가 전혀 움직이지 않았다는 것은, 정산
  단계에서 cap에 막힌 것이 아니라 **B의 주문이 애초에 생산 큐에 진입한 적이 없다**는 뜻이다(rice도
  징수되지 않음). API가 `ok=true`를 반환했음에도 실제 효과가 전무했다는 점은 lap471이 처음 발견한
  "API 레벨 수락 ≠ 실제 개시" 패턴과 같은 계열이지만, **이번엔 headroom 부족이 원인일 수 없다**
  (headroom=10이 B 주문 배치 시점에도 그대로 유지돼 있었다 — `used`는 주문 배치로 변하지 않으므로).
  **잠정 해석(work의 측정 결과, middle의 독립 검수 대상):** lap475가 유일 생존으로 승격시킨
  H-headroom("수락 시점 headroom<비용이면 조용히 무시")은 **불완전하다** — 이번 데이터는 headroom이
  충분했음에도 **두 번째 producer의 동시 주문이 조용히 소실**되는 제3의 기전(가칭 **H-serial**:
  owner당 Train 주문은 한 번에 하나만 실제로 진행되며, 이미 하나가 진행 중일 때 다른 producer에
  걸린 주문은 API가 수락을 보고해도 실제로는 큐에 들어가지 않고, 선행 주문이 끝난 뒤에도 재개되지
  않는다)을 시사한다. **이것이 사실이라면 lap406/412/449가 관측한 "reserved=10이 수만 tick
  지속"은 cap 정산 차단이 아니라 다른 원인(예: 8인 AI 소크의 매우 촘촘한 명령 빈도에서 발생하는
  같은 종류의 동시-주문 소실이 매 tick 재시도되며 reserved만 남는 현상, 또는 완전히 다른 기전)일
  가능성이 열린다 — 이번 run은 그 인과를 직접 증명하지 않았고, n=1 단일 구성(동일 building type,
  동일 owner, 두 producer 동시 배치)에서만 관측됐다.** §44가 고정한 Round 2 하드캡(정확히 1회,
  REPRO/NO_REPRO 미도달 시 같은 라벨로 종료)에 따라, 이 rider 라인은 여기서 하드캡을 소진하고
  종료한다 — **최종 라벨 `RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`**(§44가 사전에 고정한 "REPRO도
  NO_REPRO도 아니면 이 라벨로 종료"에 해당; RIDER_REPRO 미충족 — B가 headroom 소진 후 progress=100
  상태로 멈춘 것이 아니라 애초에 progress=0에서 전혀 움직이지 않았으므로 §45가 정의한 REPRO 조건과
  일치하지 않는다). **단, 이 종료는 §45가 겨냥한 질문(cap 정산 차단)에 대해서만 UNDECIDABLE이며,
  이 run 자체는 H-serial이라는 구체적이고 재현 가능해 보이는 새 관측(원시 669표본으로 독립 재계산
  가능, N107과 동급의 5중 신호로 뒷받침됨: reserved 상한 10 고정·producer_b_command 15 미진입·
  producer_b_progress 0 고정·rice 미징수·finalization 1건뿐)을 남겼다.** 이 관측이 lap404(가)/(나),
  (ㄴ), G2 전체 안정성 판정에 어떤 의미를 갖는지는 middle의 독립 검수와 strategy의 처분이 필요하다
  — work는 이 판단을 대신하지 않는다. **게임실행1·제품코드0·source변경0(3자일치)·targeted167
  passed·`SAFETY_PASS`·`CONTEXT_PASS`·커밋0.** (ㄴ)·lap404(가)/(나)·F4(B)/(C)·3단 사용자 마일스톤
  승인은 여전히 사용자 전권 대기, 모델 미착수.
- 다음 한 가지: 다음 middle이 이 run의 원시 산출물(`round2_samples.json` 669표본,
  `positive_control_samples.json` 209표본, `death_events.json` 15건, `finalization_events.json`
  1건)만으로 위 5중 신호(reserved distinct{0,10}, producer_b_command distinct{1},
  producer_b_progress distinct{0}, rice 미징수, finalization 1건)를 독립 재계산하고, §44대로
  `RIDER_STOCK_REPRO_UNDECIDABLE_BY_FIXTURE`로 W24 rider 라인을 CLOSED 처리할지, 아니면 이번에
  새로 드러난 H-serial 관측을 별도 rider(§44 하드캡과 무관한 새 판정 대상)로 승격할지 strategy에
  회부한다. rider 라인 자체는 §44 하드캡 소진으로 여기서 종료하며, work는 새 카드 없이 같은 추측을
  반복하지 않는다.
