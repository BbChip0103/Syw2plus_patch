# 2026-10-06 | lap1064 | G1 middle — H-D2r 독립 검수 + H-D2t 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·테스트 변경 0, commit 0.
- 입력: lap1063 work `loop/ESCALATE_SOL`(2,063 B, SHA256 `332e43f0634e3a8eb2b30e7ea1fc59702701d5e41cc62029684f447f9b937dc5`, 원문 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1062 §3 H-D2r — 스크롤 hold 일시 stale = `0x467B00`(높이 >160 reject_size)·`0x4685C0`(미후킹)의 미미러. R-1 띠 분할 + R-2 `0x4685C0` diff 미러로 고친다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` 직접 재계산 MATCH. objdump `0x4685C0` = `83 EC 18 | 53 | 55`(5 B 명령 경계) 직접 재확인(읽기만). fixture: 비합성 save006(D-2 hold·고정 카메라)·save000, lap1063 6 run 산출물만 읽음.

## 1. 독립 재계산(work `analyze_d2r.py`·`rect_split_d2r.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1064_middle_review/`:
`recalc_lap1064.py` `0b41dd29…fd55` → `recalc_lap1064.json` `0947e192…f5a2`, `tail_lap1064.py` `c5039ea5…8d38` → `tail_lap1064.json` `7e95e4db…c12a`.
입력 pair-result SHA 접두 6개(diag1 `0efbea66`·diag2 `3041e6a1`·nd1 `a632d8d3`·nd2 `cc0d4d5e`·s6 `bb5df665`·s0 `35b9f57f`) ESCALATE 기재와 일치.
6 run의 `bridge/` 소스(`g1_mirror2x.c` `dc8c6ede`·`g1_overlay_blt.h` `b826229f`·`direct_draw_trace.c` `8239385c`·`g1_mirror2x.h` `43218a30`)가 현재 작업 트리와 전부 같다 → 측정한 제품 = 검토한 코드. 실행 옵션은 lap1061 `run_d2w.sh`·lap1058 `run_d2z_mask.sh`·lap1056 `run_z.sh`(MASK·MASK6)와 같다.

| 항목 | 사전등록(lap1062 §3) | middle 재계산 | work 보고 | 판정 |
|---|---|---|---|---|
| hold 창 stale 합(ps3 idx, down_input..final_observation) | ≤18,791(기준 93,956) | diag1 **1**(123..291)·diag2 **761**(123..290, 최대 254·>100 3)·nd1 **1**·nd2 **1** | 1/761/1/1 | 일치·PASS |
| D2r-1 표본 (3,157)·(5,341) stale present | 0/12 | diag1·diag2 0(표본 n 71/48) | 0 | 일치·PASS |
| D2r-1 `blend_467B00_reject_size` | 0 | 6 run 모두 0, `w` 467B00 `clipped` 12(diag1/diag2) | 0 | 일치·PASS |
| D2r-1 lap1061 reject 사각형 안 stale | ≤375(기준 37,523) | 4 run 모두 **0** | 0 | 일치·PASS |
| D2r-2 표본 (465,6) | 0/6 | diag1·diag2 0(n 62), `w` 4685C0 `clipped` 6 | 0 | 일치·PASS |
| D2r-2 `blend_4685C0` | invocations>0·hold 중 reject 0 | invocations 23,235/23,235/23,274/23,275·mirrored 16·mirrored_pixels 48,627(4 run 동일)·reject_target/size/guard 0·reject_bounds = invocations − 16 | 동일 | 일치·PASS |
| D2r-2 p227..230 | ≤250(기준 24,825) | 4 run **0** | 0 | 일치·PASS |
| `blend_467B00_band_calls` | 기록 | 15(4 scroll run), s6·s0 0 | 15 | 일치 |
| p141..143 꼬리 | 기록(기준 7,087) | diag1·nd1·nd2 0, diag2 249(p143) | 동일 | 일치 |
| D2r-4 pair·안전 7종·cleanup·source_unchanged | PASS·0·true | diag/nd/s6 PASS(gate 전부 PASS)·안전 max 0(6 run)·cleanup ok·game_removed·source_unchanged true(6 run) | 동일 | 일치·PASS |
| I-0 | 24칸×2·clamp 없음·최종 (158,101) | 카메라 y 101→77→101 범위 24(4 run)·final_scene_snapshot (158,101) | 동일 | 일치·PASS |
| I-1 hold p95 / tps 비 | ≤ 고정+16 / ≥0.95 | diag1 12/12·diag2 11/11·nd1 7/7·nd2 7/8, 비 1.0008/1.0089/1.0033/1.0036 | 12/12·11/11·7/7·7/8 | 일치·PASS |
| 마지막40 | 0 | 6 run 중앙값 0·합 0 | 0 | 일치·PASS |
| save006 고정 카메라 steady | 교집합 0(880 포함) | 마스크 프레임 300..848 전부 0, 초기 6..12는 lap1056 r_s6_r1/r2와 ±1 px. **frame 880은 이 run 마스크에 없음**(ps3 868) | 동일(880 없음 공개) | 정정 1 |
| save000 | p298..338 0·HOLD 사유 동일 | 마스크 39 프레임(p298..338 포함) 합 0·gate 9개가 lap1056 r_s0_r1·r_s0_r2와 **gate별 동일**(input_effect HOLD·V2/V2s/V2q BLOCKED·나머지 PASS)·안전 0 | 동일 | 일치·PASS |
| watch 손실 | — | dropped 0·overflow 0(diag 두 run) | — | 일치 |

**정정 1(비차단):** 사전등록 D2r-4는 "save006 고정 카메라 steady 교집합 0(880 포함)"이나 s6는 1회 run이고 ps3 868 present라 frame 880이 마스크에 없다. 같은 마스크 300..848 0과 마지막40 0으로 대신 확인했고, 880은 미측정으로 남긴다(lap1051 r1과 같은 유형).

## 2. 새 근거

- **p141..143 꼬리(lap1062 UNKNOWN)는 별개 writer가 아니다.** lap1061 r1·r2에서 p141 3,301·p142 2,158은 100%, p143 1,628 중 1,379가 앞선 `0x467B00` reject 사각형(p129..140) 합집합 안이고 그 present에는 `w` 기록이 없다 → 앞서 반려된 쓰기가 다음 덮어쓰기 전까지 남은 잔존 stale. R-1 뒤 3/4 run 0으로 해소. p143의 나머지 249 px가 아래 잔여 영역이다.
- **diag2 잔여 761 px = 진단 모드 동반 영역.** diag2 p132 254·p133 49·p135 208·p143 249(bbox x301..334·y357..398)와 p296 232(창 밖, hold 합에는 포함)는 lap1061 r1의 같은 present stale에 **픽셀 단위로 전부 포함**되고(p135는 r2에 없음), 어떤 `0x467B00`·`0x4685C0` 사각형과도 교차 0. 같은 영역은 비진단 run(lap1058 m1, lap1063 nd1·nd2)에서 0, 진단 run에서는 lap1061 2/2·lap1063 1/2. lap1062 §1 W-0("진단 옵션 동반 소변동 132·133·135·143·230")과 같은 현상이다 → 제품 잔여가 아니라 진단(drift observe hook·DR watch) 동반 변동으로 판정. writer는 미귀속으로 남긴다.
- hold 뒤 p313..315(tick 24882..24884, 카메라 (158,101)) 일시 stale은 4 run 모두 재현: diag1 239/639·diag2 610/1,011/18·nd1 159/559/959·nd2 80/479/879(lap1060 결정론 관측과 같은 위치). save006 고정 카메라 s6에는 같은 유형 0 → 스크롤 뒤 상태와 관련된 유일한 남은 반복 stale.

## 3. 코드 검토

- `g1_overlay_blt_apply_banded`: 폭·x·y·높이(≤600)·화면 경계를 띠 적용 전에 검증, 띠 ≤160행, 각 띠가 `g1_overlay_blt_apply`(halo = 실제 post frame에서 읽음)를 호출하므로 Scale2x 이웃이 단일 패스와 같다. 공유 상수·`g1_overlay_blt_accepts`·`g1_overlay_blt_apply` 불변. 결함 없음.
- `mirror_blend_clip`: 높이 reject 제거, 폭 >320만 reject_size, before 버퍼 320×600 = 최대 복사량과 일치. 원본 호출 인자·반환 불변.
- `mirror_blend_skip`: `mirror_blend_clip` 본문을 `blend_clip→blend_skip`·`BLEND_CLIP→BLEND_SKIP`로 치환한 결과와 **문자열 동일**(middle 직접 확인), old bytes `83 EC 18 53 55` = objdump, install/restore·설치 확인 경로 포함.
- `direct_draw_trace.c`: 두 번째 builder 9,216·trace line 10,240. `trace_record_serialize`는 잘라내지 않고 용량 초과 시 FALSE(이벤트 drop 계수)로 처리 → 잘린 JSON 위험 없음. 새 세부 문자열 최악 396 B ≤ 480.
- focused `test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt` **63 passed/0.71s**(middle 직접 실행).

판정: **H-D2r PASS(partial) 수용** — R-1·R-2 사전등록 기준 전부 충족, 정정 1 비차단. 스크롤 hold(키 UP/DOWN) 일시 stale은 비진단 run에서 1 px(p125, 기존 단발)만 남는다. 제품 G1 마감·사용자 승인은 아니다.

## 4. work H-D2t 사전등록(다음 work, Sonnet)

가설: hold 뒤 p313..315(tick 24882..24884) 3-present 일시 stale은 hold 뒤 장면 동작 시점의 미미러/반려 writer 하나다. 진단과 수리를 한 회차에서 한다(구현 우선).

1. **T-0 위치(비진단 1회):** lap1063 `run_d2r.sh`의 nd 옵션에서 `--stale-mask 129-143,227-230`을 `--stale-mask 310-316`으로만 바꿔 save006 1회. p313..315 bbox·픽셀 수와 이 시점 장면 동작(actions 순서·tick)을 기록.
2. **T-1 귀속(진단 1회):** T-0 bbox 안 stale 픽셀 3점을 `--drift-samples`로, `--layer-drift --screen-watch` 동반 1회. 표본 stale present의 마지막 writer EIP·`w` 기록·계수로 writer 확정(진단 동반 변동은 위 §2처럼 비진단 run과 대조).
3. **T-2 수리(같은 회차):** writer가 기존 hook의 reject(사유별 계수)면 그 한도만 최소 수정, 미후킹 함수면 objdump 경계·인자 확인 뒤 기존 diff 미러 복제 패턴으로 hook 1개. 테스트 먼저(RED→GREEN), builder 최악 합 테스트 유지. 진단만으로 writer가 wined3d·GDI 등 hook 불가로 나오면 수리 없이 근거와 함께 HOLD로 인계.
4. **실행:** 수리 시 비진단 pair 2·save006 고정 카메라 1·save000 1(순차, load ≤8).

PASS 기준:
- T-1: 표본 stale present 마지막 writer 귀속 ≥ 90%.
- T-2: p313..315 stale 합(nd 기준 1,677/1,438) → 비진단 2 run 모두 ≤ 1% 또는 0, 새 hook 계수 invocations > 0·reject_target/size/guard 0.
- 비회귀: hold 창 stale 합 ≤ 10(nd 기준 1), pair PASS·안전 7종 0·cleanup·source_unchanged, I-0·I-1(p95 ≤ 고정+16·tps 비 ≥0.95), 마지막40 0, save006 마스크 300..848 0, save000 p298..338 0·HOLD 사유 lap1056과 gate별 동일, `make check` PASS.
- FAIL: 크래시·안전 위반·install 실패·원본 호출 인자/반환 변경·p95 > 고정+16.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused(`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`). 결과는 STATUS에만 보강한다.
- 전체 `make check` SKIP(문서만 변경, source는 lap1063 full PASS 1641과 같은 해시; 다음 work H-D2t가 변경 뒤 실행).

## 다음 한 가지

work(Sonnet) H-D2t: §4 T-0 → T-1 → T-2(가능하면) → 비회귀 → `make check`. 그다음 후보: 가장자리 마우스 스크롤(하네스 미지원, 입력 경로 추가 필요)·HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. backlog: save006 lap1056 r1 부하 동반 stale, 미후킹 `0x467E60`, save000 overlay BltFast rejects, 다중 팝업 heal, 진단 동반 영역 x301..334·y357..398 writer 미귀속.

## 부록: lap1063 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1063 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-D2r 구현·실행 완료, 사전등록 기준 work 자체 계산상 충족. work는 자기 결과를 승인하지 않으므로 fresh Opus middle 독립 검수가 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1063_work_d2r/ 의 {diag1,diag2,nd1,nd2,s6,s0}/pair-result.json·candidate/{trace_raw,layer_drift,screen_watch}.jsonl·stale_mask.bin 을 work 스크립트(analyze_d2r.py·rect_split_d2r.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: diag1 0efbea66, diag2 3041e6a1, nd1 a632d8d3, nd2 cc0d4d5e, s6 bb5df665, s0 35b9f57f.
2. 검증 항목: hold 창(ps3 idx 123..291) stale 합 diag1 1·diag2 761·nd1 1·nd2 1 (기준 lap1061 93,956); 표본 (3,157)·(5,341)·(465,6) stale 0/0 (diag 두 run); blend_467B00_reject_size 0·band_calls 15·blend_4685C0 invocations 23,2xx·mirrored 16·reject_target/size/guard 0; 안전 7종 0·cleanup·source_unchanged·I-0·I-1 p95; s6 마스크 프레임 300..848 0; s0 HOLD가 lap1056 r_s0와 gate별 동일; diag2 일시 stale 761 px(p132/133/135/143/296, x301..334·y357..398)의 원인 판단.
3. 코드 검토: tools/inmm_stub/g1_overlay_blt.h `g1_overlay_blt_apply_banded`(검증 선행·≤160행 띠·halo는 실제 post frame), tools/inmm_stub/g1_mirror2x.c `mirror_blend_clip`(높이 reject 제거)·`mirror_blend_skip`(old bytes 83 EC 18 53 55 = lap1062 objdump, clip 이름 치환 복제는 tests/test_g1_rect_fill.py 가 문자열 동일성으로 강제)·전용 320×600 버퍼; direct_draw_trace.c builder 9216·trace line 10240(trace_record_serialize 가 잘라내지 않는지). 수용 시 다음 work(p141..143 꼬리·diag2 잔여·가장자리 스크롤·HUD/GDI·사용자 승인 요청 준비 중 선택) 사전등록.
기록 docs/history/laps/20261006_lap1063_work_g1_hd2r_blend_band_split_4685c0_mirror.md. 변경은 전부 uncommitted(g1_mirror2x.c·g1_overlay_blt.h·g1_mirror2x.h·direct_draw_trace.c·두 테스트).
```
