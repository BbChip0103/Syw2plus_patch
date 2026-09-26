# 2026-09-22 | lap483 | 목표 G2 (W25)

- 실제 provider/model/effort / 지정 역할: Claude Code claude-sonnet-5 / high, 실무(work).
- 가설 / 사용자 관찰: 카드 `docs/work/active/G2_SETTLEMENT_GATE_SEPARATION_PROBE_LAP480.md` §4(§8 R1·R2
  보강 포함, `loop/ESCALATE_SOL`§49 lap481 strategy Q1=D2 채택)를 **그대로, 수정 없이** 1회 실행한다:
  주문 수락 producer A의 정산이 `used+reserved+cost≤cap`을 재검사하는가?
  스크립트는 lap482(work)가 작성했으나 background 후 회차 종료로 게임을 실행하지 못한 채 남겨졌던
  `w25_settlement_gate_probe.py`를 그대로 재사용했다(새로 쓰지 않음, STATUS 지시대로).
- 예상 PASS / FAIL 조건: 카드 §5의 사전 고정 3라벨(`RESERVED_RESOLVED` / `SETTLEMENT_BLOCK_REPRO` /
  `PRECONDITION_NOT_MET`) 중 하나로 재시도 없이 1회 종결(§47(iii)/§49). 절차 자체가 §2에서 도달
  불가로 확정된 자연 경로가 아니라 op4 1콜로 상태를 구성하는 기전 probe이므로, 결과는 "장부 구성
  fixture" 라벨이며 cap 근접 안정성/G2 완료 근거로 재사용하지 않는다(R2).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 레포 source 파일 변경 0(3자 일치, 아래).
  temp 증거 디렉터리에서 lap482가 남긴 stale `bridge_build/`(직전 실패 시도의 빌드 산출물, 판정
  근거 아님)를 삭제 대신 `bridge_build_lap482_partial_attempt_stale/`로 이름 변경해 보존했다
  (재실행 시 `mkdir(exist_ok=False)` 충돌 해소 목적, 스크립트 본문은 무수정). 커밋 없음
  (`LOOP_ALLOW_COMMITS` 기본0, 레포 자체가 unborn HEAD).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 exe SHA256 before/after: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
    (동일, `ORIGINAL_SHA256`과 일치) — 원본 저장소 미변경.
  - 후보(candidate) SHA256: `0a1da2263ff099b9fc35d8c63bb82bbefec6dffbae0dcc7458e32887f3f34ad3`
    (`fixed_supply_5000`, stock 1200 layout·cap5000·2-site patch — lap476/lap482와 동일 vehicle).
  - bridge dll SHA256: `82e9e4de35c65da3cebd7cf71382ffbdd22481f773c926765a7750c51c9e2362`
    (lap482의 실패 빌드 sha `48a4638...`와 다름 — PE 타임스탬프 등 비결정 바이너리 요소이며,
    `runtime_bridge.c`/`control_executor.c` **source** SHA256은 아래와 같이 빌드 전후 불변이라
    "source 변경 0" 주장에는 영향 없음).
  - `patches/population/runtime_bridge.c` SHA256 before/after:
    `2a3ad84bcd04a028fad8ed2f713cbcdae10a83549746a5a8f8aa6ada024d04df` (동일).
  - `tools/inmm_stub/control_executor.c` SHA256 before/after:
    `40003d06f43a3c14320efb5fb305e61e527e8beffd3d6e199ad2f00cf3701f5f` (동일).
  - 환경: 격리 Wine prefix + 전용 Xvfb `:211`(사전 lock 없음 확인 후 사용), 기본 unit-pool capacity
    1200(bridge source 무변경). op4 배제 핀 3종(`tools/runtime_env.py` `"op4_used": False`,
    `tests/test_g2_stock_stress.py:19`, `tests/test_g2_eight_owner_setup.py:166`) 무수정 유지 확인(R2).
  - 활성 플레이어/시나리오: goal `_custom_game_chain_inject_g2_eight_seed42`(비-AI 8인 체인 주입,
    Step C/W24/W25 계보와 동일 vehicle).
  - fixture 라벨: `ledger_construction_fixture_op4_R2_no_reuse_for_cap_proximity_or_G2_completion`
    (op4 1콜 한정, §8 R2).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 w25_settlement_gate_probe.py --display :211` — harness가 추적하는 background 태스크로
    기동한 뒤(잘못된 첫 시도: `nohup ... &`로 셸 자체에서 detach시켜 harness가 launcher만 추적하고
    실제 python3는 추적 밖으로 벗어나는 lap463/482와 같은 실패 패턴이 될 뻔했음 — 즉시 인지하고
    `run_in_background: true`를 python3 명령 자체에 직접 적용해 재기동, 완료까지 세션을 유지하며
    대기해 회차를 종료하지 않았다.
  - 산출물: `temp/Syw2plus_patch/g2_capacity/20260922_lap482_work_w25_settlement_gate_probe/`
    (`run_stdout_2.log`, `run_summary.json`, `window_samples.json`, `positive_control_samples.json`,
    `death_events.json`, `finalization_events.json`, `supply_probe_call_log.json`,
    `bridge_build/`(이번 회차 산출), `bridge_build_lap482_partial_attempt_stale/`(이전 실패분 보존)).
    디렉터리명은 lap482가 만든 것을 그대로 재사용(스크립트 무수정 원칙과 동일하게 경로도 유지).
  - 잔류 프로세스: 종료 후 `pgrep -fal 'wine|Xvfb :211'` 0건 확인.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - PS9→PS7→PS3 전이 PASS, `owner0.cap==5000` 확인 PASS, op7 rice=wood=1,000,000 PASS.
  - 양성대조(PC, producer slot1183 anchor(10,10)): op1 accepted, `L=702` tick(주문→해소, fired&resolved).
    window budget=`max(300,8×702)=5616`, stuck threshold=`5×702=3510`, op4 deadline=`0.25×702≈175`tick.
  - Order A(producer slot1172, anchor(20,10)): op1 accepted, 5중 신호(`reserved 0→10` AND `rice −800`)가
    order_a_tick714 대비 tick716(+2)에 확인 — op4 데드라인(175tick) 내.
  - op4 단일 콜(tick717, order A 대비 +3tick, 데드라인 내): `before(probe)={used70,reserved10,
    rice998400}` → `after(probe)={used4995,reserved10,rice1000000}`. 구성된 `used+reserved=5005>cap
    5000` — §1이 요구한 실험 조건 충족 확인(스크립트 자체 assert 통과).
  - 관측: window 시작 tick717, 실현 2335tick(budget 5616 미도달, 생존조건 위반으로 조기 종료) 후
    tick3052에서 producer A `hp=0`(`alive=False`) 확인, run 종료.
  - **원시 신호(신규, 사전 등록 3라벨 어느 쪽도 직접 포섭하지 못함):** tick1943(그 시점 이미
    `producer_a_progress==100` 유지 중)에 `used 4995→4985(−10)`와 `reserved 10→0`이 **동일 표본에서
    동시에** 발생했으나 `count`는 5로 불변(주문 완결의 표식인 `count+1`이 없음). 스크립트의
    `order_a_finalized` 판별식(`used==last_used+10` AND `count==last_count+1`)도, R1의
    `ledger_reverted`판별식(`reserved>0`이면서 `used<4991`)도 이 전이 시점엔 성립하지 않는다
    (reserved가 그 표본에서 이미 0으로 함께 떨어져 `reserved>0` 조건 자체가 거짓) — 즉 카드 §5가
    예견하지 않은 **제4의 원시 패턴**이다. 표면적으로는 "정산 실패 시 예약분(10)을 `used`에서
    환급하고 주문을 취소"하는 모습과 일치해 §1의 "정산이 cap을 재검사하는가"라는 질문에 강한 시사를
    주지만, work 역할은 이를 라벨로 재해석하지 않는다(사전 고정 판정식 원칙 유지 — 다음 middle의 몫).
  - tick2270에 별도 사망 이벤트(`count 5→4`) — 그 표본에서 producer A 자신은 `hp=3600, alive=True`로
    남아 있어 **producer A 자신의 사망이 아니다**(다른 유닛). producer A 고유 hp는 tick2304부터
    서서히 감소(3600→3571→…→0)해 tick3052에 `alive=False`로 전환 — 전투 피해로 인한 별개의 파괴로
    보이며 tick1943 사건과 시간적으로 무관.
  - `finalization_events=0`, `death_event_count=1`, `safety_violations=0`,
    `ledger_reverted_by_engine=False`(스크립트 판별식 기준, 위 설명대로 이 전이를 포착 못함).
  - **판정 (스크립트가 어떤 표본도 읽기 전에 고정한 §5 판정식 그대로, 수정 없이 채택):**
    `PRECONDITION_NOT_MET` — 사유: producer A가 주문 정산 전에 생존을 잃음(`hp=0`, tick3052).
    재시도 없음(§47(iii)/§49 준수, 이 1회로 카드 §4 실행 종결).
  - 검사: targeted `pytest tests/test_runtime_env.py patches/population/test_fixed_supply_5000.py
    patches/population/test_g2_full_capacity_persistence_compat_v1.py` → **167 passed**(lap478과 동일
    베이스라인). `bash checks/safety.sh check` → `SAFETY_PASS`. `python3 checks/context_limits.py` →
    `CONTEXT_PASS`. 이번 회차 source 변경 0(위 3자 SHA 일치)이므로 전체 `make check`는 면제
    (2026-09-20 21:58 지시 + N22, 이번 회차 source를 바꾸지 않았음을 명시).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - 게임실행1·제품코드0·source변경0(3자 일치)·커밋0·잔류프로세스0.
  - **남은 위험/미해석:** 위 tick1943 원시 전이는 카드 §5 라벨 정의의 사각지대다. 스크립트가 산출한
    `PRECONDITION_NOT_MET`은 §5 판별식을 문자 그대로 적용한 결과로서 유효하지만, 그 판정이 이 run에서
    관측된 **가장 이른 시점의(그리고 가장 직접적일 수 있는) cap 재검사 증거**를 라벨에 반영하지 못한다.
    다음 middle은 원시 `window_samples.json`만으로 재계산해 (a) 이 전이가 실제로 "정산이 cap을
    재검사하고 실패 시 예약을 환급·취소한다"는 §1 질문에 대한 답인지, (b) 카드 §5 라벨 3종을 확장할
    필요가 있는지(재실행 없이 이번 원시로), (c) 이번 스크립트 산출 `PRECONDITION_NOT_MET`을 그대로 둘지
    별도 라벨로 승격할지를 판정해야 한다. R2 경계(장부 구성 fixture, 재사용 금지)는 그대로 적용된다.
  - 독립 검수: 아직 없음(다음 middle 몫).
- 다음 한 가지: middle(Opus5, high)이 이 lap 산출물(특히 `window_samples.json` tick1943 부근, 원시
  supply_probe_call_log/run_summary)을 재계산으로 독립 검수하고, 위 미해석 원시 전이에 대한 라벨
  판정을 내린다. §47/§49의 "재시도 없음"은 유지되므로 게임을 다시 실행하지 않고 기존 원시로만 판단한다.
