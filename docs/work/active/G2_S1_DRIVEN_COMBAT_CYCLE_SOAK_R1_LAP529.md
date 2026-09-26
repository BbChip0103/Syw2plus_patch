# W37 — G2 S1 재무장 카드: W36과 같은 측정, 시딩 순서만 바꾼다(N187 대응) (lap529 middle 발행)

- 발행: lap529 middle (Claude Code `claude-opus-5-5` / high), 2026-09-23 KST. 상태: **발행, 미실행**.
- 실행: **work** (Claude Code `claude-sonnet-5` / high), 다음 회차. 그다음 middle이 **원시 산출물만으로 독립 검수**한다.
- 상위 근거: W36 카드 `docs/work/active/G2_S1_DRIVEN_COMBAT_CYCLE_SOAK_LAP527.md`(§1·§4·§5·§7·§8은 **이 카드에서도 그대로 유효**하다), lap522 A1 정의("시딩 종료 시 8/8 owner 라이브 `used`∈[4900,5000], op5/op6만, op4 0회"), `loop/ESCALATE_SOL` §84·§85.
- W36은 실행 예산 2회를 다 썼고 `ARM_FAIL`로 `CLOSED`됐다(lap529 검수). 이 카드는 **새 예산**을 가진다.
- 모든 산출물에 **"시딩 + 스크립트 교전 입력(op8)"** 이라고 적는다. 이 카드는 G2 제품 합격도 3단 승인도 아니다.

## 0. 경계 (위반 시 middle REJECT)

1. W36 §0 1~4를 그대로 따른다. 게임은 **foreground 동기로 완주**한다. 게임 실행 없이 끝나면 STOP하고 사용자에게 보고한다.
2. **repo source 변경 0.** lap528이 바꾼 3파일은 아래 SHA와 같아야 한다. 다르면 게임을 시작하지 않고 `BLOCKED(gate)`로 끝낸다.
   - `patches/population/runtime_bridge.c` `3555848d5389dc44699967cc7e44428f67d1e90be587e114c26fd907127f96b0`
   - `tests/test_g2_runtime_bridge_fixture_type_allowlist_pin.py` `2a8aa4f788ae35c869300726da65907ae0d82f28b69868c15c6212ae27605478`
   - `tests/test_g2_runtime_bridge_op8_order_engagement_contract.py` `0939f5b6a1aecbaf07479d53bdf40044ae550f7b97284f38779da655478f9fc7`
3. **`make check` 전체 1회**를 게임 전에 돌린다. 이유: 루프 게이트의 마지막 full-test source(`640ecfdd…`)가 현재 source(`1dca8083…`)와 다르다. exit0일 때만 게임을 시작한다.
4. 시딩 **수량·타입·op 번호·가드·허용목록은 W36 §3과 같다.** 바뀌는 것은 owner 안의 **순서** 하나다(§2). A1·A8'·§5 측정식·라벨은 바꾸지 않는다.
5. 실행은 최대 2회다. 2회째는 1회째가 **하네스 결함으로 `BLOCKED`** 됐고 하네스만 고쳤을 때만 허용한다. `ARM_FAIL`은 재실행 사유가 아니다(lap528 attempt2는 이 조건 밖이었다).

## 1. N187 원인 (lap529 원시 재계산, 확정)

- 원시: `temp/Syw2plus_patch/g2_capacity/20260923_lap528_w36_s1_driven_cycle/{attempt1_arm_fail/,}seed_receipts.json`.
- owner6 receipt: type46 시딩 직후(tick 61) `reserved`=0, 다음 op인 type2 요청 때(tick 62) `reserved`=**220**. 한 tick 안에서 0→220이다. 두 attempt가 tick까지 같다.
- 220 = 생산자 22기 × 10 이다. 생산자는 방금 시딩한 type46 20기와 시작 유닛 type110 2기다(type7 비용 10 = 250/25, type110 비용 10 = 20/2).
  그 순간 여유는 830이었는데 610을 남겼다. 그러므로 type5(100기)·type7(25기)은 그 AI 차례에 주문을 내지 않았다(생산자가 아니다).
- owner0~5는 type46→type2 사이 1~2 tick에 AI 차례가 오지 않았다. 차례가 온 것은 type2까지 채운 뒤다(여유 50 ⇒ 최종 `reserved` 40~45).
- attempt2 owner7은 시딩 **전**(tick 66, `used`=20)에 이미 `reserved`=10이었다. type110도 생산자라는 뜻이다.
- **결론:** 생산자(type46)를 시딩한 뒤에 큰 항목을 채우면, 그 사이에 AI 차례가 오는 owner는 여유를 AI 주문에 빼앗긴다. AI 노이즈가 아니라 **시딩 순서 결함**이다.

## 2. 하네스 변경 (work, temp만)

`temp/Syw2plus_patch/g2_capacity/20260923_lap528_w36_s1_driven_cycle/w36_run.py`(SHA `adb9214d56bffa640cfa5bca5f1b45dfba042c68c6a1511b8bec21f68f7dc65d`)를 **새 폴더에 복사해** `w37_run.py`로 쓴다.
새 폴더: `temp/Syw2plus_patch/g2_capacity/<YYYYMMDD>_lap<실행lap>_w37_s1_driven_cycle_r1/`. 아래 외에는 바꾸지 않는다.

- **H0 (N187 수리) 시딩 순서:** owner마다 op5 type5×100 → op6 type7×25 → **op5 type2×60 → op6 type46×20**. 생산자를 마지막에 둔다.
  - type46 요청 **직전에** 그 owner의 `(used,reserved,count)`를 읽어 `pre_producer_ledger`로 저장한다(판정용이 아니라 기록용).
  - 재요청 루프는 없앤다(타입당 1회 호출). 모든 owner를 끝까지 시도해 진단을 남긴다. receipt가 하나라도 `ok=false`면 `ARM_FAIL`이다(W36 §3 문구 그대로).
  - `arm_fail_reason`은 `seed_receipt_failed`·`A1_failed`·`A8prime_failed` 중 해당하는 것을 **모두** 리스트로 적는다.
- **H1 출생 이벤트:** `diff_events`가 새 슬롯 등장과 같은 슬롯의 uid 교체 때 `{"kind":"birth", slot, owner, type, uid, tick}`을 남긴다. 이것이 없으면 R_o(이전 사망 슬롯의 새 uid)를 원시로 재계산할 수 없다.
- **H2 생산자 추적:** op1에 쓴 producer slot마다, 그 뒤 표본에서 `production_type`·`progress`가 바뀔 때 `{"kind":"producer_change", slot, owner, tick, production_type, progress}`를 남긴다. A3 양성 대조(1,000 tick 안 변화)를 원시로 확인하기 위해서다.
- **H3 실패 경로 기록:** `residual_processes`·`source_sha_after`·`source_unchanged`를 바깥 `finally`에서 계산한다. 지금은 성공 경로에서만 적혀 lap528 두 attempt 모두 비어 있다.
- **H4 파동 예외:** `do_wave()` 호출을 `try/except (OSError, TimeoutError)`로 감싸 `e_stop_reason="read_failed"`로 처리한다. 지금은 `RUN_ERROR`로 빠져 창 E 전체 집계가 사라진다.
- **H5 자기판정 정렬(원시 판정은 middle 몫):**
  - 창 B fault(첫 op8 전)는 `ARM_FAIL`로 적는다(W36 §5 표). 지금은 `BLOCKED`로 적는다.
  - `CYCLE_UNSTABLE` 판정을 `NO_ENGAGEMENT`보다 먼저 평가한다. 지금 코드 `:967`/`:969` 순서가 W36 §5 우선순위와 반대다.
  - A5에 `used<0`, `reserved`·`count` 음수·int16 이탈, `count>1200`을 더한다. 지금은 `used>5000`과 `used` int16 범위만 본다.
  - A8' 비중은 T0 스냅샷의 **실제 보유 수**로 모든 타입 중 최댓값을 쓴다. 지금은 `SEED_TYPE5_QTY` 고정값을 쓴다.
  - A2에 창 E 3등분 중 ≥2구간 조건을 넣고, A6에 "op3 뒤 사망 합 증가"를 넣는다.

H1~H5는 W36 하네스를 lap529 middle이 카드 §4·§5와 대조한 결과다(창 E는 한 번도 실행되지 않아 드러나지 않았다). 측정식을 바꾸는 것이 아니라 카드대로 맞추는 것이다.

## 3. 실행 전 예측 (고정)

- owner o의 type46 요청 직전: `used`=20+3,500+250+780=**4,550**, `reserved` ≤ 20(생산자는 type110 2기뿐이라서). type46 20기 = 400 ≤ 5,000−4,550−20 = 430 ⇒ receipt `ok`.
- 시딩 종료: 8/8 owner `used`=**4,950**, `count`=207 ⇒ A1 PASS. 이후 AI 주문은 여유 50 안에서만 가능하다(`reserved` ≤ 50).
- **반증 조건:** 어떤 owner라도 `pre_producer_ledger.reserved` > 50이거나 type46 receipt가 `ok=false`면, type2도 생산자라는 뜻이다(§1 추론이 틀림). 이때는 `ARM_FAIL`로 끝내고 재실행하지 않는다. 다음 middle이 strategy에 A1 "시딩 종료"의 정의를 회부한다(선택지: AI 예약 정산 뒤 측정 / `used+reserved` 근접 판정).

## 4. 실행 절차·측정식·라벨·산출물

- W36 §4(preflight → 시딩 → 창 B 1,000 tick → 창 E 600 tick 파동 → tick ≥16,000 첫 파동 뒤 op2/op3 → STOP_TICK 24,000)를 그대로 따른다. **60분 상자**도 같다.
- W36 §5 측정식·A1~A8' 표·라벨·우선순위를 그대로 쓴다. 사후 재채점은 금지이고 middle은 강화만 할 수 있다.
- 산출물은 W36 §6과 같고, 추가로 `pre_producer_ledger`, birth/producer_change 이벤트, `waves.jsonl`, `save_load_result.json`, `w37_run.py` 사본과 각 SHA256을 남긴다.
- lap 기록: `docs/history/laps/<날짜>_lap<N>_work_w37_s1_driven_cycle_r1.md`.

## 5. 닫히는 조건과 다음

- 다음 middle이 `run_summary`의 verdict를 보지 않고 원시 표본·이벤트·op 결과만으로 W36 §5를 재계산한다. 라벨이 일치하면 `CLOSED`다.
- `ACCEPT` ∧ `DRIVEN_CYCLE_STABLE`이면 그 middle이 **같은 후보의 144k 카드 1장**을 바로 발행한다(lap522 J4).
- `ARM_FAIL`이 다시 나오면 같은 추측으로 재실행하지 않고 §3 반증 조건대로 strategy에 회부한다. 다른 라벨이면 W36 §7대로 strategy에 회부한다.
