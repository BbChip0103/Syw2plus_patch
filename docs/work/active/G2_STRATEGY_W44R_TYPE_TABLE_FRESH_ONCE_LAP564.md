# G2 strategy — W44 실행예산 충돌 판정: (B) 주소 수리 + W44R fresh 정확히 1회 (lap564)

- 판정: lap564 strategy (Claude Code `claude-opus-5-5`/high, INBOX 2026-09-24 14:34 "strategy는 claude-opus-5-5 유지"), 2026-09-24 KST.
- 입력: `loop/ESCALATE_SOL` §116(lap562 work)·§117(lap563 middle `ACCEPT / BLOCKED(harness_contract)`), lap561 판정 `G2_STRATEGY_S1_CLOSED_W44_STABLE_MIXED_LAP561.md` §2~§4, lap562 raw `temp/Syw2plus_patch/g2_capacity/20260924_lap562_w44_stable_mixed_24k/`.
- 이 문서는 게임 코드·브리지·temp 하네스를 바꾸지 않는다. G2 제품 합격이나 사용자 마일스톤 승인이 아니다. 사용자가 번복할 수 있다.

## 1. 입력 재확인 (lap564 직접 수행)

1. lap562 raw 해시가 §116·§117과 같다: `w44_run.py` `314bb6e8…8b1f`, `run_summary.json` `5d1d587a…b2d5`, `seed_receipts.json` `75a38eeb…5b1d`, `t0_positions.json` `04653a7c…e014`.
2. summary 없이 receipt/T0만으로 다시 계산했다. op 구성은 `{7:8, 5:16, 6:16}`이고 op4는 0이다. 8 owner 전부 `used=4950`(B1 PASS)이다. receipt 증분에서 역산한 비용은 `{5:35, 7:10, 2:13, 46:20}`이며 단일 값이다. owner마다 `{5:100, 7:26, 2:60, 46:20, 49:1}`, type2=60, 최대 단일 비중 `0.708502`(B2 8/8 PASS)이다. slot 1,656개와 uid 1,656개가 모두 유일하다. 이는 lap563 결과와 같다.
3. `w44_run.py:58-59` `TYPE_TABLE_BASE=0x004F4C00`, `STRIDE=0xA4`는 lap555 `w43_run.py`(`43be0aa8…d14f`) `:110-111`의 `0x9B5228`/`0x394`와 다르다. 올바른 주소는 추측이 아니다. lap550·555·559 세 실행의 `run_summary.type2_row_runtime.cost`가 모두 13이고, 이 값은 위 receipt 역산 type2 비용과 같다.

## 2. 판정: **(B)** — lap561 §3 "재시도 0·strategy 추가 예외 없음"을 이 한 건에 한해 명시적으로 대체한다

근거:

1. **lap562 run은 제품 동작을 하나도 관측하지 못했다.** gate에서 끝났으므로 samples/events가 0B이고 B3~B6은 UNKNOWN이다. (A)로 S5를 제출하면 lap561이 찾은 유일한 공백(건물 포함 혼합 구성의 안정 동작+저장/로드)이 비어 있는 채로 제출된다. 그러면 W44를 아예 돌리지 않은 것과 같다.
2. **결함이 한 곳이고 두 번 독립 확정됐다.** 하네스 상수 두 개만 틀렸다(lap563·lap564 재계산 일치). 올바른 값은 이미 세 번의 실행에서 실측됐다. S1의 반복 연장(lap543~559)은 설계 불확실성(배치 planner·지형) 때문이었다. 이번은 그런 경우가 아니다.
3. **PROMPT ③:** lap563(middle)과 lap564(strategy)는 연속 두 번째 무증가 회차다. 다음 회차는 실제 실행이어야 한다.
4. **사용자 2026-09-15 11:35·11:46 지시:** 하네스 보수에 머물지 말고 새 제품 증거를 우선하라는 지시다. `FEASIBLE`이면 바로 착수한다.
5. 비용: work 1회(게임 약 15~25분; lap552 raw 기준 약 33 tick/s)와 middle 1회.

**이 허가로 lap561 §3의 나머지(결과 분기·S5 제출·STOP)는 그대로다.** W44R은 모델 권한으로 도는 W44 계열의 **마지막** 실행이다. 라벨이 `STABLE_MIXED_24K`가 아니면 원인이 하네스여도 재실행하지 않는다. 그 경우 middle이 분류하고 S5 제출 후 STOP한다. 이 규칙은 strategy 재회부로 다시 열지 않는다. 새 사용자 지시만 열 수 있다.

## 3. W44R work 계약 (다음 work 회차가 계획 회차 없이 착수)

1. **파생 원본:** lap562 `w44_run.py` SHA `314bb6e846dc627f7d7c574ed173420bacc121cdbfbbce541a33c7259a3f8b1f`. 새 비중첩 디렉터리 `temp/Syw2plus_patch/g2_capacity/<date>_lap<lap>_w44r_stable_mixed_24k/`를 쓴다. `bridge_build`가 없는 새 디렉터리여야 한다(lap555 `FileExistsError` 교훈). prefix도 새로 만든다. display는 lock 파일이 없는 새 번호를 쓰고 `:6553`은 재사용하지 않는다. lap562 raw는 읽기만 한다.
2. **허용 변경(이것뿐):**
   - **C1** `TYPE_TABLE_BASE = 0x9B5228`, `TYPE_TABLE_STRIDE = 0x394`.
   - **C2** B2 계산 직전 교차검증: 네 타입의 table cost가 seed receipt의 per-unit `used` 증분과 모두 같아야 한다. 하나라도 다르면 `RUN_ERROR(harness_cost_mismatch)`로 soak 없이 끝낸다. `ARM_FAIL`로 기록하지 않는다. 기대값은 `{5:35, 7:10, 2:13, 46:20}`이다.
   - **C3** 시딩 직후 계산한 anchors가 카드 목록 `[(2,2),(27,2),(52,2),(77,2),(2,52),(27,52),(52,52),(77,52)]`과 다르면 `RUN_ERROR`로 끝낸다(assert).
   - **C4** 저장/로드 raw 보강(기준 불변): op2 직전에 tick을 새로 읽는다(`pre_save.tick_fresh`). op2와 op3 사이에 풀 4-튜플 `post_save` 스냅샷을 남긴다. op3 직후 tick을 둔다(기존 `post_load.tick`).
   - **C5** 자기 라벨 정직성: `B6_pass=True` 하드코딩을 없앤다. 아래 §4 B6 정의로 계산하거나 `null`(middle 판정)로 둔다. 로드 시 tick 역행(`post_load.tick < pre_save.tick_fresh`)을 B4 자기 계산에 넣는다.
   - 위 변경의 회귀 테스트. 그 밖의 줄은 바꾸지 않는다. `diff`를 raw에 남긴다.
3. **변경하지 않는 것:** B1~B6 임계값, 라벨과 우선순위, SEEDS 수량·순서, op 집합 `{2,3,5,6,7}`, 표본 간격, `STOP_TICK=24000`, `SAVE_LOAD_MIN_TICK=16000`, `SAVE_SLOT=92`, `MAX_WALL_S=3000`, 후보 `a10024de…`, W26 helper import.
4. **게임 전 검증(하나라도 FAIL이면 게임을 시작하지 않고 `BLOCKED(gate)`로 기록):**
   - `py_compile`와 import 합성.
   - 오프라인 회귀 ①: lap562 `seed_receipts.json`·`t0_positions.json`과 고정 비용으로 B1/B2 8/8 PASS, share `0.708502`.
   - 오프라인 회귀 ②: lap562 오판 비용 `{5:26675, 7:0, 2:26, 46:0}`을 넣으면 C2가 `RUN_ERROR(harness_cost_mismatch)`를 낸다.
   - 정적 검사: `request(` 호출의 op가 `{2,3,5,6,7}`뿐이다.
   - `checks/safety.sh check`=`SAFETY_PASS`, 원본 SHA `b56986e0…a8ac`, 핀 4건.
   - 제품 repo source를 바꾸지 않으므로 `make check` 재실행은 필요 없다(INBOX 2026-09-20 21:58 규칙; "이번 회차 source 변경 없음"을 함께 적는다).
   - 남은 시간이 45분 미만이면 시작하지 않고 기록한다. 장기 실행은 foreground로 끝까지 기다린다.
5. **실행 뒤:** 결과 라벨과 무관하게 재실행하지 않는다. raw와 source 전후 SHA, 잔류 프로세스 0, display 해제를 기록하고 middle로 넘긴다.

## 4. 판정 기준 (lap561 §2 B1~B6 그대로, B6만 조작적 정의를 실행 전에 고정)

- B1~B5: lap561 문서 §2 표 원문 그대로다. middle은 강화만 할 수 있고 완화는 금지다.
- **B6 조작적 정의(신규 고정, 완화 아님):** 모든 coherent 표본에 `rss_kb`, `vm_size_kb`, `vm_swap_kb`, `host_mem_available_kb`가 있어야 한다. 그리고 각 segment(로드 전·후)의 `vm_size_kb` 계열이 "비감소이면서 끝값이 첫 값보다 5% 넘게 큰" 경우가 없어야 PASS다. 호스트 부하 조건(동시 게임 프로세스 수, `host_mem_available_kb` 최소값)은 보고한다.
- **B4 판정 보조(분류 규칙, 기준 완화 아님):** `pre_save.tick_fresh == save_receipt.tick_before`이면 저장 순간 상태가 고정된 것으로 보고 strict 비교한다. 두 값이 다르고 `pre_save` 풀이 `post_save` 풀과 다르면, 저장 순간 상태를 확정할 수 없다. 이 경우 B4는 PASS가 아니며 `SAVELOAD_FAIL`이다. 다만 middle은 원인을 "제품 저장 손실"이 아닌 "하네스 스냅샷 경합(`SAVELOAD_UNPINNED`)"으로 분류한다. `pre_save == post_save`이고 `post_load`가 그와 다르면 제품 저장/로드 결함 후보로 보고한다.
- 보고 전용(사후 재채점 금지): N141 비교(owner별 장부 마지막 변화 tick·동결 비율), 자연 사망/출생 수, type46 좌표, lap562 대비 T0 동일성.

## 5. 결과 분기 (lap561 §3 유지)

- 다음 middle은 summary를 입력에서 빼고 samples/스냅샷/receipt raw로 B1~B6을 독립 재계산한다. diff가 §3.2 허용 범위 안인지도 확인한다. 범위 밖이면 `REJECT`다.
- **ACCEPT + `STABLE_MIXED_24K`:** 추가 실행 없이 S5 3단 제출문을 만들고 STOP한다.
- **그 밖:** 재실행 없이 제품 발견과 하네스 결함 중 어디인지 분류한다. S5 제출문에 실패로 넣고 STOP한다. 건물 포함 구성에서만 `CYCLE_UNSTABLE`이 나오면 G2 제품 결함 후보로 사용자에게 보고한다.

## 6. 금지

AI/생산/건설 로직 패치, op1/op4/op8/op9, 허용목록 확장, `(flags&14)` 가드 완화, 제품 EXE·브리지 source 바이트 변경, 144k, S1 교전 재개, 기존 raw 덮어쓰기, §3.2 밖 하네스 변경. 새 middle ACCEPT 전에 G2 PASS를 주장하지 않는다. Q9·Q7-B·"8인" 정의와 사용자 마일스톤 승인은 미결 그대로다.

## 7. 기록된 위험

- **N207(신규):** lap561 §2.1은 lap555 `w43_run.py`에서 파생하라고 했다. 실제 W44는 W26 `w26_run.py` helper를 import해 새로 작성했다(429줄). lap563은 이 차이를 지적하지 않았다. 교전 제거·시딩 순서·수량·anchor(lap562 `anchors` 8개가 카드 목록과 같음)·op2/op3 방식(W43 `:1914-1946`과 같은 구조)은 카드 내용과 맞는다. 그래서 lap564는 이 차이를 **허용 편차**로 판정한다. 대신 B3~B6 경로는 게임에서 한 번도 실행되지 않았으므로 W44R이 첫 실행이다. 여기서 하네스 결함이 나도 §2 종료 규칙이 적용된다.
- AI 자연 생산은 `used` 여유 50 안에서 저장 직전 경합을 만들 수 있다. §4 B4 보조 규칙으로 분류한다.
