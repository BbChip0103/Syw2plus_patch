# 2026-10-05 | lap1007 | G1 H-D2h 키 유지 연속 스크롤 독립 검수 → 다음 work 맵 안쪽 왕복 hold(H-D2i)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(확인·계획) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 검수 대상: lap1006 work H-D2h(하네스만, `tools/g1_saved_scene_probe.py` SHA `d949d0b8…af8e`, `tests/test_g1_saved_scene_probe.py` `a4c772b9…c896`; 현재 파일 SHA = 두 run `execution_source` before/after 일치)의 H-0~H-2 판정과 candidate lane HOLD 해석이 raw로 재현되는가.
- 예상 PASS / FAIL 조건: lap1005 사전등록 H-0~H-2. 재계산 불일치·required_tags 변화·lane 카메라 불일치면 FAIL.
- 변경 파일: 이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL`(lap1006 work 요청) 처리 후 삭제, 원문은 아래 부록. source/test 변경 0.
- 원본 SHA / 후보 / fixture: 원본 EXE `b56986e0…08a8ac`, save006 `616b7997…a064`(synthetic false, 활성8인 부하 증명 아님). bridge 사본 source 파일은 s1=s2=lap1004 사본 SHA 동일. 현재 저장소 `inmm_stub.c`·`Makefile`과의 차이는 G2 `runtime_bridge.c`(`supply_probe_poll`) 빌드 주입분뿐(lap1004 사본도 같음) → 제품 source 불변.
- 재계산 방법(제품 helper·work `analyze_d2h.py` 미사용, 새 스크립트): 공유 temp `20261005_lap1007_middle_review/`
  - `recalc_lap1007.py`(SHA `e27bb3a8…f275`) → `recalc_lap1007.json` `9229ed75…eb2a`: pair-result·camera_observations·candidate trace_raw·scroll_after PNG 직접 읽기, numpy V1/V2/V2s/V2q·독자 Scale2x(AdvMAME2x)·행/열 shift(lag) 검사, 성능 창·coverage/stale 시계열, lap1004 pair 대조.
  - 육안: `scroll_after_base_cand.png`(`8fb6ac99…d5eb`, 원본 | 후보 nearest 축소).
- 측정 / 판정(s1 / s2; 입력 pair-result `5b3632c7…`/`5ab82b13…`, 로그 `fc7c51a7…`/`871563de…` 일치):
  - **H-0 재현**: 두 lane·두 run 카메라 샘플 열 전부 동일. DOWN (158,101)→(179,128) 이동 27(전이 24 = 대각 21 + x=179 clamp 뒤 y+2 ×3), RIGHT (179,128)→(179,80) 이동 48(전이 24, 전부 x clamp 상태 y−2). 전이 간격 중앙값 50ms = 1 tick(≈20 tick/s) → 키 반복이 아니라 tick 구동이라 결정적. keydown 입력 tick 24692/24788 정확, keyup은 `release_tick`(24716/24812), emission hold 1,197~1,200ms. parity 세부(same_order·same_camera_after_each_key·action/complete/end state·snapshot source) 전부 true, action/final full state diff 비어 있음.
  - **H-1 재현**: 고정 n=123 p95 **7/6**·hold 창(24692..24824) n=133 p95 **6/6**·max 7/9, ticks/s 비 **1.0036/1.0031**, DOWN·RIGHT 누름 구간(각 25 present) p95 6. 안전 7종 max 0, mirror reject 비0은 `overlay_blt_rejects` 1,579/1,578뿐·textout reject_target 5,586/5,575(기존 수준), cleanup ok 4/4. `layer_move_calls` 1→12,981·transfer 124→1,485/1,484·unsupported 0, terrain RLE 362→993.
  - **H-2 재현**: scroll_after 보고값 전부 일치(불일치 0): nearest diff 72,131·V2 149,558→149,779(+221)·**V2s 1,692**·V2q 0. 4 PNG SHA 두 run 동일(baseline `8e843d0f…`, candidate `72787056…`). 독자 Scale2x 대비 99.37%, V2s 중 Scale2x 설명 1,638·**비설명 54**(lap962 범위 80~254 이하), 완벽 Scale2x 기준 V2s 3,012. 행/열 diff 최대 8.6%/9.1%·30% 초과 0. lag 검사: 이동 0 불일치 3.8%, ±16/±32행·±32/±64열 51.6~59.9% → 띠 어긋남·잔상 없음. 육안 지형·건물·HUD(`96807 30031 1893/2300`) 일치. 원본 loaded→scroll_after 차이 96% = 사실상 새 화면.
  - required_tags 5개(scroll_after 없음) lap1004와 동일 → gate 의미 불변.
- **판정 정정 1 — candidate lane HOLD 원인:** work 기록은 "DOWN hold 직후 12 tick 뒤 key_before"라 과도 상태처럼 썼으나, raw상 key_before 373,850은 (179,128) **정상 상태 값**(관측 24728..24787 60 present p50 373,808)이고 RIGHT p50 332,922는 도착 화면 (179,80) 정상 상태(331,934/331,940)와 같다. 두 정상 화면의 비 **0.888 < 0.9**. 즉 90% 규칙이 서로 다른 화면을 비교해 실패한 것이며, 차이는 맵 밖 흑 면적: 화면당 stale 3,861(고정) → 102,988 → 144,772이고 144,772는 원본 scroll_after 월드 흑 149,558과 같은 규모다. stale은 mirror가 덮었던 화소의 소스가 바뀐 것으로 nearest로 대체되며(`g1_mirror2x.c` present 루프) V2 +221로 시각 결함 없음. 결론(1칸용 하위 기준이 다칸 hold에 부적합, 제품 결함 아님)은 수용, 이유는 위로 정정. gate 변경 불요.
- **판정 정정 2 — work 기록 누락:** `minimap_diagnostic_parity` **HOLD**(lap1004 PASS)·`same_unit_before_after` false. hold가 카메라를 맵 가장자리 (179,80)에 남긴 채 이후 selection·drag·minimap·production 동작이 다른 장면에서 실행됐다: minimap 클릭 카메라 (179,80)→(179,80) 무변화(lap1004 (160,101)→(89,89)), 관측 유닛이 slot 278(type 63, 정지)에서 slot 1098(type 31, 이동 중)로 바뀌고 lane 간 위치 y 75 vs 77(유닛 관측이 tick 고정이 아님). 제품 결함 근거는 없으나 **hold 모드에서는 이후 tag(selection/drag/minimap/production) 장면이 이전 lap과 비교 불가**(V2s minimap 442→1,506 등). `input_effect_comparison` HOLD(selection_target·drag_capture_binding false)는 lap1004에도 같아 기존.
- 판정: **H-D2h PASS(partial) 수용**(D2-5 연속 스크롤 1 장면·맵 가장자리 관측). 제품 마감·사용자 승인 아님. G1 pair HOLD(V2s production raw, 사용자 판단 큐) 유지.
- 회귀 / 남은 위험: 제품 회귀 0. 하네스 hold 모드의 이후 장면 오염(위 정정 2), 맵 내부 연속 재그리기 미측정(이번 RIGHT는 전부 x clamp slide), 가장자리 화면의 화면당 stale ~10만~14.5만 fallback(성능 영향 없음, writer 미식별).
- 다음 한 가지: **work H-D2i(맵 안쪽 왕복 hold)** — 아래 handoff. 두 번째 장면보다 먼저인 이유: 같은 하네스·같은 save에서 변수 하나(키 방향)만 바꿔 위 두 한계(clamp·이후 장면 오염)를 함께 없앤다.

## Handoff — work H-D2i (맵 안쪽 왕복 hold, FEASIBLE)

- 근거(정적·raw): DOWN은 x를 늘려 21칸 만에 x=179에서 clamp, RIGHT는 y를 −2씩 미끄러짐(clamp 없이 128→80). `_scroll_camera_steps` 부호표는 DOWN(1,1)·RIGHT(1,−1)만 있고 `_latest_scroll_keydown/_keyup`은 UP/LEFT 가상키(0x26/0x25)를 이미 지원. UP(−1,−1) 24 tick이면 (158,101)→(134,77), 다시 DOWN 24 tick이면 (158,101)로 복귀(x ≤158이라 clamp 없음) → FEASIBLE.
- 최소 변경(제품 DLL·gate·validator·한도 변경 0, 하네스만):
  1. 옵트인 `--terrain-scroll-keys`(기본 `DOWN,RIGHT` 불변). `UP,DOWN`이면 첫 키는 기존 `down_*` tick 슬롯, 둘째 키는 `right_*` 슬롯을 쓴다(tick plan·snapshot 5개 불변).
  2. `_scroll_camera_steps`·`_expected_scroll_camera`에 UP(−1,−1)·LEFT(−1,+1) 추가. hold 모드에서 clamp 없음 검사 `|dx|==|dy|==전이 수`를 진단 필드로 기록.
  3. 테스트 RED→GREEN: 키 순서 옵션 파싱·기본 불변, UP/LEFT 부호, 왕복 시 end camera == start camera.
- 실행: lap1006 r2와 같은 명령 + `--terrain-scroll-keys UP,DOWN`, fresh runtime-root·공유 temp 새 폴더, 순차 2회. exit 2(V2s production raw 기존 gate)는 예상.
- 사전등록 PASS/FAIL:
  - I-0 하네스: 키당 이동 ≥20칸·clamp 없음(|dx|==|dy|), 두 lane 카메라 샘플 열 동일, **최종 카메라 == (158,101)**, parity 세부 true. 최종 카메라가 다르면 이후 tag 비교는 UNKNOWN으로 두고 성능만 판정.
  - I-1 성능: hold 창 p95 ≤ 고정 p95+16·ticks/s 비 ≥0.95, 안전 7종 0, reject 기존 수준, cleanup ok, **두 키 scroll_gate PASS**(맵 안쪽이라 90% 규칙이 공정해야 함; HOLD면 coverage/stale 시계열로 원인 기록).
  - I-2 시각(진단): scroll_after V1/V2/V2q PASS, V2s raw·비설명 기록, lag 검사 이동 0 최선. 추가: 같은 카메라로 돌아왔으므로 각 lane scroll_after vs 자기 loaded 차이를 기록(후보 차이가 원본 차이보다 크게 늘면 스크롤 잔상 의심).
  - I-3 이후 장면: `minimap_diagnostic_parity` PASS 복귀(lap1004 수준), `input_effect_comparison`은 lap1004와 같은 checks.
  - FAIL: I-1이 2/2 실패 → 성능 결함, `g1_perf_sections`로 원인 지목 후 다음 work 수리. 1/2만이면 3번째 실행.
- 이후 후보(이번 범위 아님): 두 번째 장면 pair, 가장자리 마우스 스크롤, 가장자리 stale fallback writer 식별.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문

```
lap1006 work(claude-sonnet-5-5) -> middle(Opus) 독립 검수 요청: G1 H-D2h(키 유지 연속 스크롤, 하네스만·제품 변경 0).
기록: docs/history/laps/20261005_lap1006_work_g1_d2h_hold_scroll.md (uncommitted)
결과: `--terrain-scroll-hold` 추가(sim_tick 기반 keyup, 테스트 5개 RED->GREEN), r1 FAIL 보존(카메라 맵 가장자리 slide를 (n,n)로 가정한 하네스 결함, 수정), r2 fresh pair 2회(exit 2=V2s raw 기존 HOLD) H-0/H-1/H-2 PASS: 이동 27/48칸·lane 카메라 동일, hold 창 p95 6/6·비 1.0036/1.0031·안전0·reject 기존 수준.
middle이 확인할 것: 1) pair-result·trace_raw·scroll_after PNG를 helper 없이 재계산, 2) handoff 전제 정정(게임 비정지 주 경로라 tick 기반 keyup) 타당성, 3) candidate lane HOLD(RIGHT scroll_gate 90% 하위 기준)가 hold 부적합이라는 판정, 4) 맵 가장자리 clamp 한계 때문에 맵 안쪽 방향 hold 또는 두 번째 장면 중 무엇을 다음에 할지.
```

- 위 2) 확인: `_wait_for_exact_tick`은 1ms 폴링, `_snapshot_with_live_read`는 in-process 파일 대기라 주 경로에서 게임을 멈추지 않는다 → lap1005 handoff의 "checkpoint 정지" 전제는 오류였고 work 정정(tick 기반 keyup)이 타당.
