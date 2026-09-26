# 2026-09-23 | lap530 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, work(실무).
- 가설 / 사용자 관찰: W36 attempt1/2 모두 owner6에서 `ARM_FAIL`(N187, lap529 확정) — 생산자(type46)를
  type2보다 먼저 시딩하면 그 사이 AI가 자기 차례에 여유를 가로챈다. W37(§0-2)는 시딩 순서만
  `op5 type5x100 -> op6 type7x25 -> op5 type2x60 -> op6 type46x20`(생산자 마지막)으로 바꾸고,
  카드 §2 H1~H5(출생 이벤트, 생산자 추적, 실패경로 기록, do_wave 파동 예외, 자기판정 정렬)를
  하네스에 반영한다. 측정식(A1~A8')과 라벨 우선순위는 카드가 그대로 지정한다.
- 예상 PASS / FAIL 조건: 카드 §3 고정 예측 — type46 요청 직전 8/8 owner `used`=4,550·`reserved`≤20,
  시딩 종료 8/8 `used`=4,950. 반증 조건은 `pre_producer_ledger.reserved`>50 또는 type46 receipt
  `ok=false`(→`ARM_FAIL`, 재실행 금지, strategy 회부).

## 0. 경계 확인 (카드 §0)

- gate 파일 3종 SHA 실행 전 확인, 카드 값과 정확히 일치:
  - `patches/population/runtime_bridge.c` `3555848d...96b0`
  - `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py` `2a8aa4f7...78`
  - `tests/test_g2_runtime_bridge_op8_order_engagement_contract.py` `0939f5b6...fc`
- `make check` 전체 1회(게임 전): **828 passed (511.64s)**, ruff/mypy PASS, `checks/context_limits.py` `CONTEXT_PASS`.
- 실행 후 재확인: 3개 gate 파일 SHA 불변, repo에 신규 트래킹 변경 없음(전체가 아직 untracked 초기 상태),
  `checks/safety.py check` → `SAFETY_PASS`.

## 1. 하네스 (카드 §2, work 작성, temp만)

- `temp/Syw2plus_patch/g2_capacity/20260923_lap528_w36_s1_driven_cycle/w36_run.py`
  (SHA `adb9214d...65d`, 카드가 지정한 값과 일치 확인)를 새 폴더로 복사해
  `temp/Syw2plus_patch/g2_capacity/20260923_lap530_w37_s1_driven_cycle_r1/w37_run.py`로 작성.
- H0: 시딩 순서를 `[(5,5,100),(6,7,25),(5,2,60),(6,46,20)]`로 재배열, type46 호출 직전
  `pre_producer_ledger`(owner별 used/reserved/count) 기록, 재요청 루프 제거(타입당 1회 호출),
  `arm_fail_reason`을 seed_receipt_failed/A1_failed/A8prime_failed 리스트로 변경.
- H1: `diff_events`에 birth 이벤트 추가(신규 슬롯 등장, uid 교체 시 이전 occupant death 뒤 birth).
- H2: `producer_state` 딕셔너리로 op1 producer slot의 production_type/progress 변화를
  Phase E 매 tick 샘플에서 감지해 `producer_change` 이벤트 기록.
- H3: `residual_processes`/`source_sha_after`/`source_unchanged`를 outer `finally`로 이동해
  ARM_FAIL/BLOCKED 등 실패 경로에서도 항상 기록(기존 코드는 성공 경로에서만 기록했다).
- H4: `do_wave()` 호출을 `try/except (OSError, TimeoutError)`로 감싸 `e_stop_reason="read_failed"`로
  처리(기존은 `RUN_ERROR`로 빠져 Phase E 전체 집계 유실).
- H5: 창 B 폴트 라벨을 BLOCKED→ARM_FAIL로 정정, `CYCLE_UNSTABLE` 평가를 `NO_ENGAGEMENT`보다
  먼저 하도록 순서 교체, A5에 `used<0`/`reserved`·`count` 음수·int16 이탈/`count>1200` 추가,
  A8' 비중을 SEED_TYPE5_QTY 고정값 대신 T0 스냅샷 실측 타입별 비용 합의 최댓값으로 계산,
  A2에 Phase E 3등분 중 ≥2구간 사망 조건 추가, A6에 "load 뒤 사망 합 증가(`op3` 뒤 `>0`)" 추가.
- `python3 -c "import ast; ast.parse(...)"` 통과, `ruff check --select F,E9` 통과(정의되지 않은
  이름·미사용 import 없음). w37_run.py 최종 SHA `54bac3ef0a432981ac55ac7876433e77aa5feb7d9e8a34f1e7ea4ccd03ebc78d`.

## 2. 실행 (attempt 1/2 예산)

- `make check` gate 통과 뒤 `.venv/bin/python3 w37_run.py` foreground 동기 실행, isolated
  display `:6530`, prefix `local/runtime/20260923_205722_3106765_0/prefix`, pid 3109206.
- 원본 SHA 불변(`source_sha_before`=`source_sha_after`=`b56986e0...8ac`=`ORIGINAL_SHA`).
  후보 SHA `a10024de...b68`(카드 고정 기댓값과 일치). bridge dll SHA `2931a50c...00f`.
- 종료: exit0, `residual_processes=[]`, `source_unchanged=true`. 하네스 결함으로 인한 `BLOCKED`가
  아니므로(정상 완주) **카드 §0-5에 따라 2회째 실행은 불필요/금지**.

## 3. 측정값 (원시 산출물, work self-verdict — 다음 middle이 독립 재계산)

- **N187 반증되지 않음(FEASIBLE 확정):** `pre_producer_ledger` 8/8 owner `used=4,550`,
  `reserved`=0(owner0-5)/10(owner6-7, type110 생산자), 카드 §3 예측과 정확히 일치.
  `seed_shortfalls=[]`, `seed_receipt_failed=false`. **A1: 8/8 owner `used`=4,950(PASS,
  범위 4900-5000)**. **A8': 8/8 owner 실측 최대타입비중 0.7071(≤0.85) PASS**(전 owner 4타입
  보유·X_TYPE≥10 생존 포함). `ARM_FAIL` 없음 — W36의 N187 문제는 시딩 순서 교체로 해소됐다.
- Phase B(baseline, tick70→1075): 정상 완주, `B0`/`D_B` 0(원시 미별도확인, self 계산상 무이벤트).
- Phase E(tick1075→24001, 39 waves 전량 실행, `skipped_waves=[]`): `op8_requested=op8_accepted=1872`
  (100% 수락), `repro_requested=repro_accepted=5`, `replenish_requested=0`(X_TYPE 항상 ≥10 생존).
  `D_o_by_owner`={0:4,1:0,2:7,3:3,4:3,5:1,6:0,7:0}=합계18. `D_o_by_owner_segment`(3등분)=
  owner0[0,4,0] owner2[7,0,0] owner3[2,1,0] owner4[0,3,0] owner5[0,1,0] — **owner1/6/7은 사망 0**.
- **A5(무결성) 전항목 PASS**: `used>5000` 0건, `live/count` 불일치 0, tick 역행 0,
  `used`/`reserved`/`count` int16 이탈·음수·`count>1200` 전부 0건. `fault_or_crash=false`.
- **save/load(A6)**: tick16176에서 실행. `save ok=true, marker_match=true, load ok=true`,
  post_save/post_load 8/8 owner `used`/`reserved`/`count`/`live`(1686) 완전 일치(필드 정합 PASS).
  **그러나 H5 신규 체크(load 뒤 사망 합 증가) `deaths_after_load=0`으로 FAIL** → `A6_pass=false`.
- **신규 실측(N191, 원시 재확인 완료, 해석은 middle 몫):** 사망/hp_decrease의 실제 마지막 발생
  시각은 **tick13095**이며, load(tick16176)는 그보다 **이후**다. tick13095~24001(10,906틱, 런
  전체의 약 45%) 동안 `hp_decrease` 0건·`death` 0건이 이 구간 전체에 걸쳐 있고, 이 무활동 구간은
  save/load 발생 **전 3,081틱부터 이미 시작**돼 있었다. 즉 이번 A6 FAIL은 로드가 원인이라기보다
  **로드 이전에 이미 진행 중이던 교전 소강**을 로드 이후 구간에서 잡아낸 것일 가능성이 있다 —
  로드 자체의 인과는 이 데이터만으로 확정할 수 없다. 반면 같은 구간에서도 `op8` 발주는 wave37/38
  (tick23298/23885)까지 `raw_return=1 "executed"`로 계속 수락됐다(요청은 accept되지만 피해가
  기록되지 않음). `producer_change` 17건·`birth` 56건(전체, load 후 8건)은 정상 관측됐다(H1/H2
  계측 자체는 작동).
- **self_label = `CYCLE_UNSTABLE`**(H5 우선순위상 A6 실패가 A2/engagement 평가보다 먼저 걸림).
  `A2_pass`도 별도로 실패였을 것이다(owner1/6/7 사망0, 대부분 owner가 20+ 및 2/3구간 조건 미달).

## 4. 회귀 / 남은 위험 / 독립 검수 상태

- 산출물 및 SHA256: `w37_run.py` `54bac3ef...78d`, `pre_producer_ledger.json` `8d542b51...99f`,
  `seed_receipts.json` `93c05862...31`, `waves.jsonl` `5c86d669...0fc`,
  `save_load_result.json` `4a48d1d9...926`, `events.jsonl` `320554f4...3d`,
  `samples.jsonl` `2391002584...b7`, `run_summary.json` `2e917f42...806`,
  `resource_receipts.json` `1b67c8d3...cf`. 전체 경로
  `temp/Syw2plus_patch/g2_capacity/20260923_lap530_w37_s1_driven_cycle_r1/`.
- 게임실행1(attempt1, 완주)·source(repo 트래킹) 변경0·커밋0. temp 하네스 변경1(`w37_run.py` 신규).
- 이 lap은 work self-verdict만이다. 카드 §5대로 **다음 middle이 원시 표본/이벤트/waves만으로
  A1-A8'·라벨을 독립 재계산**해야 한다. `CYCLE_UNSTABLE`이 `ARM_FAIL`이 아니므로 카드 §5 "다른
  라벨" 경로 — middle 검수 뒤 strategy 회부 대상이다. 특히 N191(교전 소강이 로드 이전부터 시작)은
  A6 라벨의 인과 해석에 영향을 줄 수 있어 middle이 우선 확인해야 한다.
- 사용자 승인/마일스톤 판정 없음(불변).

## 5. 다음 한 가지

**middle(Opus5.5): lap530 원시 산출물을 `run_summary.json`의 verdict를 보지 않고 독립
재계산**하여 W36 §5 라벨을 재확정하고, N191(교전 소강 시점이 load 이전인지)을 별도로 판정한다.
`CLOSED`면 카드 §5대로 `CYCLE_UNSTABLE`(또는 재계산 결과 라벨)을 W36 §7 절차로 strategy에 회부한다.
