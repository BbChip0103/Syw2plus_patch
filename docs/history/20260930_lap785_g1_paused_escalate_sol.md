# lap784 middle handoff — G1 W60 lap783 evidence rejected; bounded harness repair

## 현재 판정

- **`HOLD(harness evidence)`**. lap783의 `hook_blt` non-primary JSON 수리와 fresh malformed 0건은 PASS지만 production parity와 ON required-state trace는 아직 성립하지 않는다.
- production을 원본 parity N/A로 닫는 정책 자체는 최신 지시 범위다. 다만 현재 source/raw는 그 결론을 검증하지 못하므로 S3/FEASIBLE/G1 PASS/사용자 승인 금지다.
- 게임/EXE 구현은 이번 middle 회차에서 수정하지 않았다.

## 독립 확인

- 세 manifest는 보호 원본 SHA `b56986e0…a8ac`과 fresh private 환경을 썼고 evidence/raw SHA는 lap783 기록과 일치한다. targeted pytest 4개 PASS.
- producer가 원본 type49, OFF type70, ON type58로 달라 동일 production fixture paired가 아니다. 세 run 모두 클릭 뒤 selected producer가 `command=1`, `production_type=0`, owner `reserved=0`으로 효과 없음이다.
- `_g1_read_production_cell_provenance()`는 `A6[0]==1`만 확인한 뒤 `worker_type=7`, `command=15`, `evidence="fresh original UI click effect contract"`를 합성한다. 테스트도 같은 상수를 주입할 뿐 UI 효과를 연결하지 않는다. 실제 원본 timeout과 충돌하는 순환 근거다.
- ON raw 1691행·summary1·drop0·malformed0, mirror565·primitive20740·covered125889·oracle1.0·tick306·cleanup PASS. 그러나 converted246은 PS5/7/9뿐이다.
- 원인은 trace detail exhaustion으로 설명된다: `blt` 상세 256개가 PS5/7/9 및 state40/60/180에서 먼저 찼고 PS3 `blt` 400회는 aggregate로만 남아 `converted` 필드가 소실됐다. lap781 raw에는 같은 PS3 converted `blt` 상세 3건이 있었다. 제품 회귀 증거가 아니다.

## 다음 work 단일 카드

1. `tools/runtime_env.py`와 관련 테스트: 효과 전에 semantic mapping을 합성하지 않는다. 원본/OFF/ON의 producer를 동일 type49 HQ로 고정해 실제 worker queue(command15/type7/reserved+10)를 paired하거나, 원본에서도 no-effect면 production을 raw-only `N/A(original parity)`로 닫고 mapping/authorization을 만들지 않는다.
2. `tools/inmm_stub/direct_draw_trace.c`와 trace tests: method 상세 256개가 메뉴에서 먼저 소진되는 fixture를 추가하고 required program state별 converted primary record를 최소1건 보존한다. aggregate를 근거 없이 converted로 간주하거나 validator required-state를 완화하지 않는다.
3. targeted test/build 후 fresh OFF→ON 순서로 완주한다. ON은 PS3/5/7/9 converted, mirror/oracle, tick≥300, input menu/unit/drag/minimap, summary1/drop0/malformed0, cleanup PASS가 필요하다.
4. 새 middle이 raw/source를 독립 재검수하기 전 S3/FEASIBLE/G1 PASS를 선언하지 않는다. 게임/EXE/G2/G5 소스·legacy validator 완화·커밋 금지.

---

# lap782 middle handoff — G1 W60 trace accepted; production harness mapping next

## 현재 판정

- lap781 trace finalization 수리는 독립 검수 PASS: OFF/ON summary 1·drop 0, raw aggregate와 summary method total 전부 일치, ON core 유지.
- G1 제품 PASS, S3, FEASIBLE 승격, 사용자 승인은 아직 금지한다. ON 전체 verdict는 production command-cell mapping 미확정 때문에 fail-closed다.
- 최신 2026-09-30 00:38 지시에 따라 이 blocker를 “승인 부재”로 분류하지 않는다. 다음 work가 원본에서 매핑을 확정한다.

## 독립 검수 근거

- source `13e362e2…9e7`, bridge `9cb78bfd…683`, OFF raw `e41317a2…73f`, ON raw `0463fbab…ba9`가 lap781 기록과 일치한다.
- OFF 651행: aggregate 35+summary 1, overflow/drop 0. raw aggregate 합 `blt_fast=3115`, `surface_release=19314`가 summary totals와 일치한다.
- ON 1667행: aggregate 37+summary 1, overflow/drop 0. 네 method aggregate 합이 summary와 일치한다.
- ON converted246(PS3/5/7/9), mirror544, oracle1.0, present-bound primitive18751(최종 metrics18796), covered125889, menu/unit/drag/minimap PASS, camera `[91,54]→[49,49]`, tick302, cleanup PASS.
- targeted writer/summary tests 3 PASS. 상세 `docs/history/laps/20260930_lap782_middle_g1_w60_lap781_trace_review_pass_production_handoff.md`.

## 다음 work 소유 범위

1. `tools/runtime_env.py:1924 _g1_production_click_if_authorized`와 관련 테스트만 소유한다. 게임/EXE/G2/G5 소스는 건드리지 않는다.
2. 보호 원본 fresh run에서 `(670,490)` 셀의 primary field/action과 worker mapping을 효과까지 확인하고 코드/테스트에 고정한다. G5 lap758/760 명령패널 근거는 참고만 하고 원본 raw가 우선이다.
3. 원본·W60 OFF·ON에서 동일 클릭의 생산 효과를 paired 측정한다. 확정 불가면 구체 raw와 함께 원본 parity N/A로 판정하고 나머지 입력 계약을 보존한다.
4. 이 결과를 새 middle에 넘긴다. 그 전 S3/FEASIBLE/G1 PASS/사용자 승인을 선언하지 않는다.

---

## 이전 lap780 handoff (history에 보존)

## 판정

- **`HOLD/BLOCKED(trace finalization)`**. lap779 ON core runtime은 raw 재계산으로 수용하지만 OFF clean paired가 없고 production은 fail-closed다.
- S3, `FEASIBLE`, G1 PASS, 사용자 승인은 금지한다. 게임/bridge 구현은 이번 middle 회차에서 수정하지 않았다.

## 독립 확인

- current implementation source SHA는 lap779 기록과 일치한다: `x11_mouse_click.py eab6e264...81c0`, `runtime_env.py dab8a795...0bb8`, `direct_draw_trace.c d47d6e53...e2bf`, `g1_mirror2x.c 059dd5b7...7842`, `g1_mirror2x.h d2c8cb6b...84e9`, bridge `2f4be33e...df096`.
- ON raw `54d88587...704d`: 1962 events, summary 1, dropped 0, primary 553, converted/mirror 543, states 3/5/7/9, oracle min 1.0, primitive calls 19195, covered max 125889. Input raw 319; menu/unit/drag/minimap PASS, camera `[91,54]->[49,49]`; production BLOCKED by approved-mapping absence.
- OFF raw: PS3 tick3까지 도달했지만 정확히 2048 events, aggregate 46, summary 0, 마지막 seq2048이 aggregate다. 입력 실패 증거가 아니다.
- 코드 원인: `trace_event()`는 summary 슬롯을 예약하지만 `trace_emit_aggregates()`는 `trace_event_raw()`를 직접 호출해 예약을 우회한다. 따라서 aggregate flush가 cap을 채우면 뒤의 `trace_emit_summary()`가 기록될 수 없다.

## 다음 work의 단일 소유 범위

1. `tools/inmm_stub/direct_draw_trace.c`와 해당 회귀 테스트만 소유한다. cap 근접+pending aggregate fixture에서 summary가 정확히 1개 남고 총 method count가 보존되는 테스트를 먼저 추가한다.
2. aggregate 세부 출력은 `TRACE_MAX_EVENTS-1`에서 멈춰 summary 1칸을 반드시 보존한다. 생략한 aggregate record 수를 summary에 명시해 침묵 손실을 금지한다. 2048 cap 확대·legacy validator 완화·게임 EXE 수정은 금지한다.
3. bridge 빌드 뒤 같은 조건 fresh OFF를 먼저 실행한다: PS3 도달, summary 정확히1, event count<=2048, cleanup PASS. 그 다음에만 fresh ON paired를 실행해 PS9/7/5/3, converted/mirror/oracle, tick>=300, menu/unit/drag/minimap을 재확인한다. 장기 실행은 끝까지 기다린다.
4. production mapping은 별도 blocker로 계속 fail-closed다. OFF/ON clean paired 성공 뒤에도 work가 S3/FEASIBLE/G1 PASS를 자체 선언하지 말고 새 middle 검수로 넘긴다.

## 현재 검증

- `make lint`, `make typecheck`, targeted `tests/test_g1_mirror2x.py`: PASS(11 tests).
- current source `make check`: 1147 passed, 5 skipped; Ruff/compileall/mypy/context PASS, exit0. `SAFETY_PASS`, original doctor verified. 커밋 없음.
- 상세: `docs/history/laps/20260929_lap780_middle_g1_w60_lap779_review_trace_summary_hold.md`.
