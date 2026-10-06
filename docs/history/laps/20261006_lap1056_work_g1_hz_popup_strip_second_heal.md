# 2026-10-06 | lap1056 | G1 work — H-Z 팝업 동반 띠 second heal

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap.
- 가설: 팝업 동안 wined3d가 KEYSRC heal 사각형 밖 띠를 매 present 다시 쓴다(lap1055 정정 1). heal이 활성인 동안 heal 밖 stale bbox를 두 번째 heal로 diff 미러하면 stale이 0이 된다.
- 예상 PASS / FAIL(lap1055 사전등록): Z-0 안전 7종 0·cleanup/source_unchanged true·계수 항등식 / Z-1 save000 p298..338 303/412 → ≤10, 마지막40 0, 표본 stale present 41 → 0 / Z-2 save006 팝업 run 블록 → 0, 신규 stale 0 / Z-3 p95 ≤ 기준+1, tick 비 ≥ 0.99 / Z-4 pair PASS, gate·validator 불변.
- 변경 파일(모두 uncommitted, sha256): `tools/inmm_stub/g1_mirror2x.c` `b87e2f7de7d122b78d2f1103c748b4036c4d47fc71918abf503403917055815c`·`g1_mirror2x.h` `56a5b7be52275c1bb237d54aa30e2cb64d3ca58336917e6e4d4c680952730f8e`·`direct_draw_trace.c` `fef456480b011174b6e16e7d695581f1dd3464a7d3c15fbfcdf504b6747f7bbd`·`tests/test_g1_rect_fill.py` `210e1ef07a3fc5b055f0c54e34d39a548dc0eb23747af4fe4adc55c3bfcea08e`. 제품 변경 내용:
  - `rect_blt_heal2_at_present`: `rect_blt_heal_at_present`가 첫 heal을 한 직후 같은 present에서 호출. 화면 전체를 훑어 첫 heal 사각형 **밖**의 covered이면서 `expected != screen`인 픽셀의 bbox를 구하고, bbox가 `G1_OVERLAY_MAX_*` 이내면 `g1_overlay_blt_apply`로 다시 비교한다. before = stale 픽셀은 expected, 나머지는 화면 값이라 stale 픽셀만 미러된다. 한도를 넘으면 `heal2_skipped`만 올리고 자르지 않는다. 좌표 하드코딩 없음, `G1_OVERLAY_MAX_*`·gate·validator 불변.
  - 계수 `overlay_rect_blt_heal2_presents/pixels/skipped`(trace + header 3 getter + 설치 시 0 초기화). `rect_blt_details` 버퍼 800→960(worst-case 테스트 PASS).
  - Z-1 진단(env-gated `SYW2_G1_LAYER_DRIFT`): heal2 활성 present마다 `{"t":"z",p,in,out,x,y,w,h,hx,hy,hw,hh,ok}` 한 줄(stale가 있을 때만), `0x465E80` 반려 때 `{"t":"q",why,p,x0,y0,x1,y1,c,stride,buf,panel,cache}` 최대 64줄. (첫 시도는 `t:"s"`가 기존 sample 레코드와 충돌해 분석 스크립트가 깨져 `q`로 바꾸고 전체를 다시 실행했다. 첫 실행 산출물은 `…/20261006_lap1056_work_hz/run1_discarded/`·`local/runtime/lap1056_run1_discarded/`·`logs/gates/lap1056_run1_discarded/`에 보존하고 판정에 쓰지 않는다.)
  - 테스트: 구현 뒤에 `test_g1_rect_fill.py` 소스 계약(heal2 정의·스킵·한도·로그·계수)을 추가했다. 선 RED 단계 없음(구현→계약 순서).
- 원본 SHA / 환경 / fixture: 원본 EXE sha256 `b56986e0…08a8ac`, `source_unchanged` 전 run [true,true]. save000 `--scene-actions none --performance-window`(결정론 팝업 p297/298), save006 비합성. 격리 prefix/display, `game` 사본은 run마다 삭제(남은 `game` 0).
- 실행(공유 temp `20261006_lap1056_work_hz/`, 로그 `logs/gates/lap1056_hz_*`): `run_z.sh` = save000 watch pair 2회(`--layer-drift --screen-watch` 표본 `250,224;280,221;300,222`)·save000 성능 pair 2회·save006 pair 2회(launch 1회, 순차, load 대기 규칙). 추가 진단 `run_z2.sh`·`run_z3.sh` = save006 `--layer-drift` ×8(d1~d8). exit: w 2·2, s0 2·2(기존 save000 pair HOLD와 동일: input_effect HOLD·V2/V2s/V2q BLOCKED, lap1051과 gate별 상태 동일), s6 0·0, d1~d8 0. 분석 `analyze_x_s0.py`(lap1051 복사)·`analyze_z_s6.py`(신규).

## 측정(work 자체 계산, 판정 아님 — middle 독립 검수 필요)

| 항목 | 기준(H-X 뒤 lap1051) | H-Z (lap1056) | 판정 |
|---|---|---|---|
| Z-0 | 안전 7종 0 | 18 run 모두 안전 7종 0, cleanup [T,T], source_unchanged [T,T]; heal2 항등식: heal2_pixels = Σ z.out(ok) 8/8 run 일치(예 41×303 = 12,423; d2 43,712; d8 23,002), heal2_skipped 0 | PASS |
| Z-1 save000 p298..338 | 303(watch)/412(s0) | **0 / 0** (4 run) | PASS(≤10) |
| Z-1 마지막40 | 0 | 0 ×4 | PASS |
| Z-1 표본 (250,224)(280,221)(300,222) stale present | A 41, B·C 0 | **0/0/0** ×2 watch run | PASS |
| Z-2 save006 팝업 run(keysrc>0) | 블록 434/360/303/281 px, 41~53 present | r2·d2(팝업 2회)·d3·d4·d8 = 블록 **0**, 마지막40 0; r2 stale 합 293,064 = 팝업 없는 run(lap1053 r1)과 동일 | PASS(5 run) |
| Z-2 신규 stale | — | 팝업 없는 run(d1·d5~d7) 0(1 px 외 없음), steady 신규 0 | PASS |
| Z-2 **r1 예외** | — | s6 r1(735 present, 짧은 run) p651..664에 14 present 증가형 stale(157→987→…→4211→2125→…→2889, 665에서 0). heal 활성 시간과 겹치는지는 drift 로그가 없어 **UNKNOWN**. 이전 40 save006 run에 같은 모양 0, 이번 이후 추가 8 run 재현 0 | **UNKNOWN**(회귀/기존 사건 구분 안 됨) |
| Z-3 | p95 7/7(s0)·11~12(w), tick 비 1.000 | p95 7/7(s0)·11/11(w), tick 비 1.0000036/1.0000033/1.0000066/0.99988 | PASS |
| Z-4 | save000 pair HOLD(기존), save006 PASS | save000 4 run 같은 HOLD(gate별 상태 동일), save006 pair PASS 2/2·V1/V2/V2q/V2s/Scale2x PASS | PASS(save000 HOLD는 기존 사유) |

## Z-1 진단 결과(귀속)
- 띠 y218..226은 `0x465E80`이 **반려한 큰 사각형 (240,110)-(565,337)**(326×228, `reject_size`) 안에 있다. 반려 `q` 레코드: size 1(x240..565 y110..337, color 254, stride 800, 화면 버퍼) + target 2~3(작은 오프스크린 176·360 stride). 즉 띠는 팝업 본체 채움(`0x465E80`)과 같은 영역이며 heal 사각형(KEYSRC Blt 51×38→170×128)과는 서로소(z `in` 0인 첫 5 present에서 `out` 303/320/360이 이미 존재).
- 폭은 글자 길이에 따라 303/320/360/517 px로 팝업별로 다르고(w 61~109 × h 9) 한 팝업 안에서는 41~53 present 동안 일정하다. second heal이 이를 present마다 diff 미러한다. 이로써 lap1055 대안(0x465E80 큰 사각형 행 분할)은 쓰지 않았다.

## 회귀 / 남은 위험 / 독립 검수
- 화면 전체 스캔은 첫 heal 활성 present에서만(팝업당 41~97 present) 돌아 성능 영향은 p95·tick 비로 확인(Z-3). heal이 활성인 동안 heal 밖의 다른 stale도 같이 미러될 수 있으나(한도 이내일 때), 이는 의도된 일반 stale 수리이며 `stale > 한도`는 skipped로 센다.
- **r1 예외(UNKNOWN)**: 팝업 run 6개 중 1개에서 증가형 stale이 14 present. 팝업 동반이 아닌 별개 사건(미후킹 효과)일 가능성과 heal2/팝업 중 새 경로일 가능성을 work가 구분하지 못했다. middle이 r1 아티팩트(`r_s6_r1`, drift 없음)와 추가 8 run을 독립 확인하고, 필요하면 `--layer-drift --stale-mask 640-670/2`로 재현을 더 모으거나 그 구간을 별도 H로 등록한다.
- 사용자 승인 상태: 기술 PASS(partial) 후보일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격은 대기(루프 비차단).
- 다음 한 가지: middle H-Z 독립 검수(재계산·r1 예외 판정·수용 여부) 후 D-2 연속 스크롤·두 번째 장면 후보 선택.
