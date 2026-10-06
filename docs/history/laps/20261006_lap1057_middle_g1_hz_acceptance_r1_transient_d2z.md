# 2026-10-06 | lap1057 | G1 middle — H-Z 독립 검수·r1 증가형 stale 판정 → work H-D2z 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source 변경·commit 0.
- 입력: lap1056 work `loop/ESCALATE_SOL`(SHA256 `1c7193f5df8d64f99a7c55968694c9ade683ea3f3e2f2529f7dcb41c1c9145e9`, 원문은 아래 부록, 처리 뒤 삭제), 기록 `20261006_lap1056_work_g1_hz_popup_strip_second_heal.md`, 산출물 공유 temp `20261006_lap1056_work_hz/`(14 run; `run1_discarded`는 판정 제외).
- 가설(검수 대상): 팝업 동안 KEYSRC heal 사각형 밖 동반 띠를 second heal로 diff 미러하면 save000 p298..338·save006 팝업 블록이 0이 되고 신규 stale·성능 회귀가 없다.
- 사전등록 PASS/FAIL(lap1055): Z-0 안전 7종 0·cleanup/source_unchanged·계수 항등식 / Z-1 save000 p298..338 → ≤10·마지막40 0·표본 stale present 0 / Z-2 save006 팝업 run 블록 0·신규 stale 0 / Z-3 p95 ≤ 기준+1·tick 비 ≥0.99 / Z-4 pair·gate·validator 불변.

## 1. 제품 코드 검토(읽기만)

- 해시 재확인: `g1_mirror2x.c` `b87e2f7d…`·`.h` `56a5b7be…`·`direct_draw_trace.c` `fef45648…`·`tests/test_g1_rect_fill.py` `210e1ef0…` = 인계 값, 14 run `bridge/` 사본 3개 모두 현재 source와 일치.
- `rect_blt_heal2_at_present`는 `rect_blt_heal_at_present` 안, `if (!g_rect_blt_heal_active) return;`과 apply 성공 뒤에서만 호출된다 → **heal 비활성 present에서는 실행 경로가 없다**. 판정 기준(covered ∧ expected≠screen)은 present 루프의 `stale_now` 정의(같은 조건, 그 뒤 covered 해제)와 같고 heal2가 그보다 먼저 돈다. before = stale은 expected·나머지는 화면 값이라 stale 픽셀만 바뀐다. bbox 한도 `G1_OVERLAY_MAX_WIDTH/HEIGHT`(320×160) = `g_rect_blt_before` 크기와 같고 넘치면 skipped만 센다. 좌표 하드코딩 0, gate·validator·한도 상수 불변. 결함 없음.
- 한계(비차단): 선 RED 없이 구현 뒤 소스 계약 테스트를 붙였다(work 기록이 공개). 기능 단위 테스트가 아닌 소스 문자열 계약이라 동작은 런타임 run으로만 증명된다.

## 2. 독립 재계산(work `analyze_*`·`isect_x.py` 미사용)

스크립트 `temp/…/20261006_lap1057_middle_review/recalc_lap1057.py`(SHA256 `339832b5…2fdb`, lap1052/1055 middle 파서 기반) → `recalc_lap1057.json` `25e26342…0420`·`recalc_lap1057.txt` `ddfc41ed…f8e8`. 과거 corpus 스캔 `scan_lap1057.py` `81f21c04…87f2` → `scan_lap1057.json` `5ddf8f65…edcf`(2026-10-03~06 candidate trace 211 run).

| 항목 | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|
| Z-0 | 14 run 안전 7종 max 0·trace 파싱 실패 0·cleanup [T,T]·source_unchanged [T,T]·EXE `b56986e0…` 양 lane·9 family 항등식 전부 성립. drift 8 run(w×2·s0×2·d2·d3·d4·d8)에서 `heal2_pixels = Σ z.out(ok)`·`heal2_presents = z ok 수`, skipped 0, z bbox ∩ heal 사각형 0 | 같음 | 일치·PASS |
| Z-1 save000 | w r1/r2·s0 r1/r2: p298..338 합 **0**·최대 0·마스크 298/308/318/328/338 0 px·마지막40 0; 표본 (250,224)(280,221)(300,222) stale present **0/0/0** ×2(drift `s` 기록 cov=1∧scr≠snap 직접 계산) | 0/0, 0/0/0 | 일치·PASS |
| Z-1 귀속 | z bbox (240,218)-w61..109×9, 첫 heal(`in`=0) present에서 이미 out 303/320/360/434; `q` 반려 = size (240,110)-(565,337) color 254 stride 800 + target 2개 | 같음 | 일치 |
| Z-2 save006 팝업 run | s6 r2·d2·d3·d4·d8: 팝업 창(aggregate KEYSRC `blt` call_seq → present) 이후 +60 present stale 합 0, 3 present 이상 늦은 구간 0, 마지막40 0. r2 stale 합 293,064 = lap1053 s6 r1(팝업 없음) 293,064 | 같음 | 일치·PASS |
| Z-2 신규 | d1·d5·d6·d7(팝업 없음) 늦은 구간 0 | 같음 | 일치 |
| Z-3 | 히스토그램 nearest-rank p95 기준/후보 w 1/11·0/11, s0 0/7·0/7; tick 비 1.0000036·1.0000033·1.0000066·0.99988 (lap1051 기준 s0 7/7·w 11~12) | 같음 | 일치·PASS |
| Z-4 | save000 4 run HOLD(기존 사유), save006 s6·d 10 run PASS | 같음 | 일치 |

## 3. UNKNOWN 판정 — save006 r1 p651..664 증가형 stale

- r1 stale: p651 5 → 157 → 987 → 1,531 → 2,061 → 2,673 → 2,941 → **4,211** → 2,125 → 2,125 → 2,428 → 2,669 → 2,817 → 2,889(p664), p665~734 0. 덤프 프레임(6..12·300·420..480/3·585·620)이 구간 밖이라 위치는 미확인.
- **팝업 시점 확정(새 근거):** r1 trace `aggregate` 레코드에서 back buffer KEYSRC `blt` 5회 = call_seq 8022..8102 → present **p394..398**, 짝 `blt_fast` 18+13회 = p394..411. heal 21 present = heal2 18 + 3 quiet(다른 run도 heal = heal2 + 3: 44/41·56/53·100/97), `heal2_pixels` 5,760 = 18×320(같은 팝업 폭 320은 d3 41×320 = 13,120). 다른 KEYSRC 호출 없음(`keysrc_calls` 5). → heal은 p414 무렵 끝났고 **p651..664에는 heal·heal2 실행 경로가 없다**. 그 구간 stale이 heal 중이었다면 heal2가 먼저 보고 apply(픽셀 증가) 또는 skipped(0)였어야 하는데 둘 다 아니다.
- **부하 흔적:** r1만 present 간격 p95 **142 ms**·최대 375 ms(211 run 중 최고; 나머지 save006 52~61, lap1051 s6 r1 83), present 735/46.6 s(다른 run 886~901/44.9 s). 시작 load 2.10은 낮았으나 실행 중 간격이 불규칙(p640..670 23~176 ms). 같은 증가형 모양은 211 run 어디에도 없다(H-V 이전 p764..787 1,328 px 증가형은 시각 38.8 s 고정·r1 42.0 s와 불일치).
- 판정: **H-Z 무관(코드 경로 부재로 입증), 원인 UNKNOWN의 부하 동반 일시 stale, 자가 해소(p665 0).** H-Z 회귀 아님 → H-Z 수용을 막지 않는다. backlog로 등록하고, 정상 간격(p95 ≤60 ms) run에서 재현되거나 2회 이상 재현되면 재개방한다(그때 `--layer-drift`+그 구간 `--stale-mask`로 위치·writer 확인).
- 정정(work 기록): "heal 활성 시간과 겹치는지는 drift 로그가 없어 UNKNOWN" → trace aggregate call_seq로 팝업 p394..411 확정, 겹침 없음.

## 4. 판정

- **H-Z PASS(partial) 수용.** Z-0~Z-4 사전등록 조건 전부 충족, 재계산 불일치 0. 이로써 save000·save006 두 fixture의 고정 카메라 stale(마지막40·팝업 구간)이 0이다. partial 사유: 제품 마감·사용자 G1 승인 아님, D-2 연속 스크롤은 H-B~H-Z hook 스택 이전(lap1008)에만 측정, r1 transient 원인 UNKNOWN(backlog).
- 사용자 승인 상태: G1 사용자 마일스톤 미요청. G6/G7 사용자 합격(APPROVALS lap989) 대기, 루프 비차단.

## 5. Handoff — work H-D2z (현행 hook 스택에서 D-2 왕복 hold 재측정)

- 근거: lap1008 H-D2i(맵 안쪽 UP→DOWN 24칸 왕복 hold)는 H-B·H-B4·H-A·H-M·H-N·H-U~H-Z 미러가 붙기 전 제품이었다. 이후 hook 10여 개와 heal2(present마다 화면 스캔, heal 활성 중)가 늘었으므로 스크롤 중 stale·성능 회귀가 G1 남은 항목(D-2) 중 가장 직접적인 공백이다. 제품 변경 없이 측정만 하는 회차다.
- 실행: lap1008 명령 그대로(새 runtime-root·공유 temp 새 폴더), `tools/g1_saved_scene_probe.py --hd-source scale2x --terrain-scroll --terrain-scroll-hold --terrain-scroll-keys UP,DOWN --p4b-s-snapshot --reference-completed-states <lap1008과 같은 경로> --stale-mask <hold 창 포함 3프레임 간격>`, save006, 순차 2회(1/2만 실패면 3회째). load 대기 규칙·game 사본 삭제 유지. 하네스 옵션이 현재 source에 없으면 BLOCKED로 기록하고 새로 쓰지 않는다.
- 사전등록 PASS/FAIL:
  - D2z-0: 안전 7종 0·cleanup ok·source_unchanged·9 family 항등식·`heal2_skipped` 기록(>0이면 사유 공개).
  - D2z-1: lap1008 I-0(24칸·clamp 없음·최종 카메라 (158,101)·parity)·I-1(hold 창 p95 ≤ 고정+16·ticks/s 비 ≥0.95) 유지.
  - D2z-2: hold 창 present별 `stale_pixels` 중앙값·최대와 왕복 복귀 뒤 마지막40 중앙값 기록. 복귀 뒤 마지막40 **0**이면 PASS, >0이면 FAIL이 아니라 새 잔여로 bbox·덤프와 함께 기록(다음 work census/watch).
  - D2z-3: scroll_after V1/V2/V2q PASS·V2s W-1(unexplained ≤2,000)·`minimap_diagnostic_parity`·`input_effect_comparison` lap1008 수준.
  - FAIL: candidate 크래시·안전 위반·I-1 회귀 → 원인 지목 후 다음 work 수리.
- 다음: H-D2z 수용 뒤 남은 G1 항목(가장자리 마우스 스크롤·HUD/GDI·전체 HD coverage·사용자 승인 요청 준비) 중 선택.
- backlog 추가: r1 부하 동반 증가형 stale(위 §3 재개방 조건). 기존 backlog(미후킹 `0x467E60`, save000 overlay BltFast rejects, 다중 팝업 heal 등) 유지.

## 6. 검사

- 기록 freeze 뒤 SAFETY_PASS·CONTEXT_PASS, focused `.venv/bin/python -m pytest tests/test_g1_rect_fill.py tests/test_g1_mirror2x.py tests/test_g1_overlay_blt.py`(lap1055와 같은 3 파일). 결과는 STATUS 줄에 보강한다. 전체 `make check` SKIP(문서만 변경, source 불변·lap1056 full PASS 1639).

## 부록 — lap1056 `loop/ESCALATE_SOL` 원문(SHA256 `1c7193f5…45e9`)

```
lap1056 work(Sonnet) → middle(Opus) 인계. 사유: H-Z 구현·실행 완료, 다음 한 가지가 middle 독립 검수(work는 자기 결과를 승인할 수 없는 역할 경계, MODEL_ROUTING).

middle이 할 일:
1. 제품 변경 검토: tools/inmm_stub/g1_mirror2x.c `rect_blt_heal2_at_present`(첫 heal 밖 covered∧expected≠screen bbox를 second heal), `rect_solid_reject_log`, 계수 heal2_*; direct_draw_trace.c(rect_blt_details 960); tests/test_g1_rect_fill.py. 해시: g1_mirror2x.c b87e2f7d…, .h 56a5b7be…, direct_draw_trace.c fef45648…, test 210e1ef0….
2. 산출물 `temp/Syw2plus_patch/20261006_lap1056_work_hz/`(r_w_r1/2·r_s0_r1/2·r_s6_r1/2·r_d1~8, run1_discarded는 판정 제외)를 work 스크립트(analyze_*) 없이 새 스크립트로 재계산: save000 p298..338 303/412→0·마지막40 0·표본 3점 stale 0·heal2_pixels=Σz.out, save006 팝업 run(r2,d2,d3,d4,d8) 블록 0.
3. **판정 필요 UNKNOWN**: save006 r1(735 present)의 p651..664 증가형 stale(157→4211→2889, 665에서 0)이 heal2/팝업과 관련인지 별개 사건인지(r1은 drift 없음; 이전 40 run·이후 8 run 재현 0).
4. 수용 시 다음 work: 고정 카메라 stale 잔여 0 확인 뒤 D-2 연속 스크롤/두 번째 장면 사전등록.
기록 docs/history/laps/20261006_lap1056_work_g1_hz_popup_strip_second_heal.md.
```
