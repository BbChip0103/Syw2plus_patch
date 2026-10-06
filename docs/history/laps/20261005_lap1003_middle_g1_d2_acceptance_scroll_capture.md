# 2026-10-05 | lap1003 | G1 D-2 스크롤 성능 독립 검수 → 다음 work 스크롤 뒤 캡처(H-D2c)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high, Fast OFF / middle 1 lap(진단·확인). 게임 실행·source·gate·commit 0.
- 가설 / 검수 대상: lap1002 work D-2(현재 source 그대로 `--terrain-scroll` pair 2회)의 D2-0~D2-3 PASS(partial) 판정이 raw에서 그대로 재현되는가, 창 정의·D2-2 대체 규칙이 타당한가, reject 계수가 고정 카메라 실행과 같은 수준인가.
- 예상 PASS / FAIL 조건: lap1001 handoff 사전등록 그대로(D2-1 스크롤 창 PS3 present ≥20·p95 ≤ 같은 run 고정 p95+16, D2-2 ≥0.95, D2-3 안전 7종 0·hook reject 보고·cleanup). 재계산 값이 work 보고와 1개라도 다르면 불수용.
- 변경 파일 / source fingerprint / 커밋: 문서만(이 기록, `docs/STATUS.md`), `loop/ESCALATE_SOL` 처리·삭제(원문 SHA `9d33e7ce…7413`, 아래 부록). source 불변 확인 — `g1_mirror2x.c` `42245a20…a5210`, `.h` `2ee0ff0f…675a`, `direct_draw_trace.c` `0669e798…c1c2`, `tests/test_g1_rect_fill.py` `34f804f9…7334`. uncommitted.
- 원본 SHA / 후보 SHA / 환경 / fixture: lap1002 그대로(원본 EXE `b56986e0…08a8ac`, save006 `616b7997…a064`, synthetic false, 활성8인 부하 증명 아님). 새 실행 없음.
- 실행 명령 / 산출물: 새 스크립트 `temp/Syw2plus_patch/20261005_lap1003_middle_review/recalc_lap1003.py`(SHA `a5e84e2a…e6c0`; `analyze_d2.py`·제품 helper 미사용, trace_raw·pair-result 직접 파싱, p95는 nearest-rank·선형보간 둘 다) → `recalc_lap1003.json`(SHA `a292da2e…b3bb0`). 입력 SHA: s1/s2 pair `8f10a9e1…`/`62f2e348…`, candidate trace `f2094944…`/`bb44396e…`(work 기록과 일치). 비교 대상 work `analysis_d2.json` `b0a5e885…`.
- 측정값 / 판정(재계산, s1 / s2):
  - D2-0: parity status PASS·bool 11개 전부 true·action full-state diff 비어 있음·scene_state_equal true(2/2). 카메라 두 lane 동일 `[158,101]`→DOWN`[159,102]`→RIGHT`[160,101]`. **전사 정정:** work가 UNKNOWN으로 적은 스크롤 coverage는 candidate `actions[].coverage_30_present`에 있다 — DOWN p50 **474,565**(0.9887), RIGHT **474,804**(0.9892), 직전 키 474,838/474,587, scroll_gate PASS(layer_move Δ 1/512·transfer Δ 112~113/89·outside_diff 0). lap908 참고값 346,526/335,727보다 높다(gate 아님).
  - D2-1: PS3 present 1,532/1,533(전체 1,958/1,951), sim_tick 단조. 고정 창(sim_tick 24570..24691) n=123 p95 **6/6**(선형 6.0) max 7/9. 스크롤 창(24692..24824) n=133 p95 **6/6** max 9/9 → 한도 22 이하 **PASS 2/2**. 민감도: DOWN만(24692..24728) n=37 p95 7/8(선형 6.2/7.2), RIGHT만 p95 6/6, 스크롤 뒤 n=1,276/1,277 p95 6/7 max 11/13. 카메라 변화 프레임(24693·24789) elapsed 4~6 ms, 스파이크 없음.
  - D2-2: 스크롤 20.0061/20.0152 ÷ 고정 19.9505/19.9571 ticks/s = **1.0028/1.0029**(≥0.95 PASS). baseline trace에 `sim_tick`·`mirror2x_present` 0건 확인 → 대체 규칙 적용은 handoff 문언대로이며 타당. 두 lane 최종 상태 diff 0이 baseline 대비 진행 동일성을 보강한다.
  - D2-3: 안전 7종 전 present max 0·필드 누락 0, writer/terrain clip mismatch 7종 0, rect_fill·rect_border·flip_rle·blend reject 전부 0(계수 work 보고와 일치), textout restore 1, dropped 0, cleanup ok·prefix 프로세스 [] (양 lane) → **PASS**.
  - reject 수준(lap1000 고정 r1~r3 대조): `textout_iat_reject_target` 5,554/5,561 vs 5,562/5,544/5,537 — 프레임 수와 무관한 상수, **같은 수준**. `overlay_blt_rejects` 1,638/1,639 vs 1,014/898/898 — 절대값은 크나 실행 길이(PS3 present 1,532 vs 868~886, blend 호출 1,538 vs 892)에 비례하며 blend 호출당 1.065 vs 1.007~1.137 → **같은 수준**(mirrored_calls 792/793 vs 791~792 동일). 둘 다 안전 계수 아님.
  - work `analysis_d2.json`의 n·p50·p95·max·ticks/s·비율·textout 계수와 **불일치 0**.
- 판정: **H-D2 PASS(partial) 수용**(D2-0~D2-3 2/2). 한계(명시): ① 이 하네스의 "스크롤"은 **1칸 이동 2회**뿐이다 — terrain RLE 호출 증분이 카메라 변화 때 16·30회에 그친다. 키를 누르고 있는 연속 스크롤·가장자리 스크롤의 성능은 측정되지 않았다(D2-5 후보, 이번 수용에 포함 안 함). ② D2-4 스크롤 뒤 화면의 원본 대비 시각 일치는 여전히 UNKNOWN. G1 제품 마감·사용자 승인 아님.
- 회귀 / 남은 위험: 회귀 0. 남은 G1: pair HOLD(V2s raw 2,857 사용자 판단 큐), 스크롤 뒤 시각 일치(UNKNOWN), 연속 스크롤 성능, 두 번째 장면, 성분 D, PS35·P6/P7 HD 혼합 화질, burst UNKNOWN, 사용자 승인. 마일스톤 경계 아님 → 일반 middle→work 연결. 디스크 여유 79GiB.
- 다음 한 가지: **work H-D2c(스크롤 뒤 캡처 하네스)** — 아래 handoff.

## Handoff — work H-D2c (스크롤 뒤 baseline/candidate 캡처, FEASIBLE)

- 왜: D-2의 유일 UNKNOWN. 스크롤 상태에서 새 hook 6개가 안전·성능은 지켰지만 화면이 원본과 맞는지는 본 적이 없다.
- 근거(정적, 이번 회차 확인): `tools/g1_saved_scene_probe.py` `_capture(display, run_id, pid, tag, crop, output, log)`(L1932)가 이미 있고, `--terrain-scroll` 흐름은 최종 관측 barrier(tick 24860)와 `final_scene_read` 뒤 `result["terrain_scroll"]`를 만든다(L3869 부근). 그 직후 두 lane 모두 `_capture(..., "scroll_after", <기존 캡처와 같은 crop>, ...)`를 호출하면 된다. 비교는 pair 쪽 `capture_visual_comparisons`(현재 tag 5개)에 같은 비교 함수를 재사용한다 → FEASIBLE.
- 최소 변경(제품 DLL 변경 0, 하네스만):
  1. `--terrain-scroll`일 때만 최종 관측 뒤 `scroll_after` 캡처(두 lane).
  2. pair에서 `scroll_after`를 기존 V1(v2)/V2q/Scale2x/V2s 비교에 **진단용 tag로만** 추가. `v2s_capture_gate.required_tags`·각 gate의 필수 tag·validator·한도는 바꾸지 않는다(gate 의미 변경 금지).
  3. 회귀 테스트 1개 RED→GREEN(terrain-scroll 모드에서 scroll_after 캡처·진단 비교가 생기고 required_tags 불변).
- 실행: lap1002와 같은 명령(`--hd-source scale2x --terrain-scroll --p4b-s-snapshot --reference-completed-states …lap888…`) 순차 2회, fresh runtime-root, 공유 temp 새 폴더. exit 2(V2s production raw 기존 gate)는 예상.
- 사전등록 PASS/FAIL:
  - C-0 하네스: terrain_scroll_parity PASS·scene_state_equal true(2/2), 기존 5 tag 판정·required_tags 불변, `scroll_after.png` 두 lane 존재·캡처 시점 기록.
  - C-1 비회귀: 스크롤 창 PS3 p95 ≤ 고정 p95+16, ticks/s 비 ≥0.95, 안전 7종 0, hook reject 0, cleanup ok(lap1002 수준).
  - C-2 시각(scroll_after 진단): V1/V2q/Scale2x PASS 2/2, PNG에 격자·seam·1칸 어긋난 지형 띠 없음(원본/후보 나란히 육안+행/열 단위 차이 프로파일), V2s raw·unexplained 값 기록.
  - FAIL: C-2에서 지형 띠 어긋남·잔상이 2/2 재현 → 위치로 writer 지목(census `--census-only`) 후 다음 work 수리. 1/2만이면 3번째 실행으로 판정. 캡처 시점 차이(게임은 계속 진행)로 생기는 유닛 애니메이션 차이는 기존 tag와 같은 방식으로 다루고 결함으로 세지 않는다.
- 이후 후보(이번 범위 아님): D2-5 연속 스크롤(키 유지 다칸 이동) 성능, 두 번째 장면 pair.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(SHA256 `9d33e7ceab98e5f38492207e918baac7d9c1295321b0ae3dc5c0b1292af77413`)

```
lap1002 work(Claude Code claude-sonnet-5-5) → middle(Opus) 독립 검수 요청: G1 D-2 스크롤 성능 측정 완료(제품·gate 변경 0), 판정은 middle 몫(일반 work→middle 인계).
기록: docs/history/laps/20261005_lap1002_work_g1_d2_scroll_performance.md (uncommitted)
결과: fresh save006 `--hd-source scale2x --terrain-scroll --p4b-s-snapshot` pair 순차 2회(공유 temp 20261005_lap1002_work_d2_scroll/s1,s2, 전부 exit 2 = V2s production raw 2,857>2,000 기존 gate HOLD):
 D2-0 terrain_scroll_parity PASS·scene_state_equal true·state diff 0, D2-1 스크롤 창 n=133 p95 6ms(고정 p95 6, 한도 22)·max 9, D2-2 baseline에 sim_tick 없어 candidate 스크롤÷고정 대체 ticks/s 비 1.0028/1.0029,
 D2-3 안전 7종 0·hook reject 전부 0(overlay_blt_rejects 1,638/1,639·textout reject_target 5,554는 기록만)·cleanup ok·크래시 0, D2-4 스크롤 후 PNG/stale_mask는 하네스에 없어 UNKNOWN(trace stale_pixels 중앙값 고정 3,867/스크롤 2,180/이후 0).
middle이 확인할 것:
 1) s1/s2 trace_raw·probe-result·pair-result를 제품 helper·analyze_d2.py 없이 재계산: 스크롤 창(sim_tick 24692..24824)·고정 창(<24692) present 수·p95, ticks/s 비, 안전·hook 계수(analysis_d2.json 대조).
 2) 창 정의(trace mirror2x_present.sim_tick)와 D2-2 대체 규칙(baseline trace에 sim_tick 없음) 타당성 판정, overlay_blt_rejects·textout reject_target이 이전 고정 실행과 같은 수준인지(lap1000 r1~r3 trace 대조).
 3) source SHA(g1_mirror2x.c 42245a20…, .h 2ee0ff0f…, direct_draw_trace.c 0669e798…, tests/test_g1_rect_fill.py 34f804f9…) 불변 확인.
 4) 수용 시 다음 work 한 가지 선택: 스크롤 후 캡처 하네스(terrain-scroll 종료 시점 baseline/candidate PNG 쌍+Scale2x 비교) 권고, 대안 두 번째 장면 pair.
```
