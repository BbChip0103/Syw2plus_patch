# 2026-10-06 | lap1063 | G1 work — H-D2r 스크롤 hold stale 수리(0x467B00 띠 분할 + 0x4685C0 diff 미러)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap.
- 가설: lap1062 §3 — 스크롤 hold 일시 stale = 화면 직접 writer `0x467B00`(높이 >160 reject_size)·`0x4685C0`(미후킹)의 미미러. 둘을 계수로 분리해 한 회차에 고친다.
- 사전등록 PASS(lap1062 §3): D2r-1 표본 (3,157)·(5,341) stale 0/12·`0x467B00` reject_size 0·reject 사각형 안 37,523→≤375 / D2r-2 표본 (465,6) 0/6·`blend_4685C0_invocations`>0·p227..230 24,825→≤250 / D2r-3 hold 합 93,956→≤18,791 / D2r-4 비회귀(pair PASS·안전0·I-0·I-1 p95 ≤ 고정+16·마지막40 0·save000 p298..338 0·HOLD 사유 동일·`make check`) / FAIL 크래시·안전·install 실패·원본 인자/반환 변경.
- 변경 파일(uncommitted): `tools/inmm_stub/g1_overlay_blt.h`(`g1_overlay_blt_apply_banded` 신설, 공유 상수·`g1_overlay_blt_accepts`·`g1_overlay_blt_apply` 불변), `tools/inmm_stub/g1_mirror2x.c`(`mirror_blend_clip` 높이 reject 제거·띠 apply·`band_calls`, 신규 hook `0x4685C0` `mirror_blend_skip` = clip 이름 치환 복제, 전용 320×600 before 버퍼 2개, install/restore/계수), `tools/inmm_stub/g1_mirror2x.h`, `tools/inmm_stub/direct_draw_trace.c`(계수 `blend_467B00_band_calls`·`blend_4685C0_*`, 두 번째 builder 8192→9216·trace line 8192→10240), 테스트 `tests/test_g1_overlay_blt.py`(띠 = 전체 프레임 Scale2x 동등 C 테스트)·`tests/test_g1_rect_fill.py`(clip 계약 보강·skip 계약·builder 크기).
- 해시 접두(SHA256): g1_mirror2x.c `dc8c6ede…`·g1_overlay_blt.h `b826229f…`·direct_draw_trace.c `8239385c…`·g1_mirror2x.h `43218a30…`·_inmm.dll `3bd1663c…`(ignored 산출물)·test_g1_overlay_blt.py `d30d0c13…`·test_g1_rect_fill.py `69b8ffdd…`. 원본 EXE SHA `b56986e0…08a8ac`, `0x4685C0` old bytes `83 EC 18 53 55`는 lap1062 objdump(`od_4685C0_lap1062.txt`)와 일치(읽기만).
- R-0(테스트 먼저): 띠 테스트 RED(`g1_overlay_blt_apply_banded` 미정의 컴파일 실패) → helper 구현 GREEN. builder 최악 합 테스트 RED(8,246 > 8,192) → 9,216 GREEN. 단위 테스트: 띠 200/570/600/161/160/1행·scale2x on/off = 전체 프레임 Scale2x 대비 일치, ≤160행 단일 띠 = 기존 apply와 byte 동일, 폭 321·화면 밖·높이 0 reject(미러 불변). 관련 3 파일 63 passed, make lint·typecheck PASS, SAFETY_PASS.
- 실행: 공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1063_work_d2r/`(`run_d2r.sh` `c3645d93…`, `analyze_d2r.py` `b4bf2043…`, `rect_split_d2r.py` `c44be9fc…`, `analysis_d2r.json` `c73cacd1…`), 로그 `logs/gates/lap1063_d2r_{diag1,diag2,nd1,nd2,s6,s0}.{log,exit}`, 순차·load ≤8, 게임 사본 각 run 뒤 삭제. diag = lap1061 옵션(save006 D-2 hold UP/DOWN 24, `--layer-drift --screen-watch --drift-samples "3,157;5,341;465,6" --stale-mask 129-143,227-230`), nd = lap1058 옵션, s6 = save006 고정 카메라(lap1056 `MASK6`), s0 = save000 `--scene-actions none --performance-window --layer-drift`(lap1056 `MASK`). pair-result SHA 접두 diag1 `0efbea66`·diag2 `3041e6a1`·nd1 `a632d8d3`·nd2 `cc0d4d5e`·s6 `bb5df665`·s0 `35b9f57f`. exit 0·0·0·0·0·2(s0 HOLD).

## 측정(work 자체 계산, 판정 아님 — middle 독립 검수 필요)

| 항목 | 기준(이전) | 결과 |
|---|---|---|
| hold 창 stale 합(ps3 idx 123..291) | 진단 lap1061 93,956 / 비진단 lap1058 >100 present 19·최대 12,976 | diag1 **1**·diag2 **761**(최대 254, 5 present)·nd1 **1**·nd2 **1** |
| D2r-1 표본 (3,157)·(5,341) stale present | 18/18(두 표본 + (465,6) 합) | diag1·diag2 모두 **0**(표본 71/48/62 present) |
| D2r-1 `blend_467B00_reject_size` | hold 중 12 | 4 scroll run 모두 **0**(`w` 레코드 467B00 `clipped` 12 = 전부 미러) |
| D2r-1 reject 사각형 안 stale | 37,523 | diag1 0·diag2 0(마스크 511 px는 사각형 밖) |
| D2r-2 표본 (465,6) stale | 6/6 | **0** (4685C0 `w` 레코드 6 = `clipped`, 미러됨) |
| D2r-2 p227..230 | 24,825 | diag1·diag2 **0** |
| `blend_4685C0` | 미후킹 | invocations 23,235~23,275·mirrored 16·reject_target/size/guard **0**·reject_bounds 23,2xx(화면 밖 호출) |
| `blend_467B00_band_calls` | — | 15(띠 ≥2 호출) |
| D2r-3 p141..143 꼬리 | 7,087 | diag1 0·nd 0·diag2 p143 249(좌표 bbox [301,357,332,376], 두 hook 사각형 밖) |
| D2r-4 pair / 안전 7종 / cleanup / source_unchanged | — | diag·nd·s6 PASS·안전 전부 0·cleanup·source_unchanged true |
| I-0 | — | 24칸×2·clamp 없음·lane 카메라 열 동일·최종 (158,101) (4 run 모두) |
| I-1 hold p95 vs 고정 / tps 비 | lap1061 12/12 | diag 12/12·11/11, nd 7/7·7/8, 비 1.0008~1.0089 |
| 마지막40 | 0 | 6 run 모두 0 |
| save006 고정 카메라(s6) | lap1056 r2 stale 합 293,064·steady 마스크 0 | pair PASS·V2/V2s/V2q PASS·stale 합 292,586·마스크 프레임 300..848 전부 0(880 프레임은 이 run에 없음, 6..12 초기 프레임은 lap1056 r2와 동일)·마지막40 0 |
| save000(s0) | lap1056 r_s0 HOLD(input_effect HOLD·V2/V2s/V2q BLOCKED, 나머지 PASS) | status HOLD, 같은 gate가 같은 값(input_effect HOLD·minimap PASS·performance PASS·loaded PASS·scale2x PASS·V2계열 BLOCKED)·stale 윈도(p298..338 포함) 전부 0·안전0·`blend_467B00_reject_size` 0 |

판정 후보(work): D2r-1·D2r-2·D2r-3·D2r-4 사전등록 기준 충족 → **H-D2r PASS(partial)**. 공개 한계: (1) diag2에서만 일시 stale 761 px(p132 254·p133 49·p135 208·p143 249·p296 232, 좌표 x301..334·y357..398, 두 hook 호출 사각형 밖; nd 2 run·diag1 0) — 원인 UNKNOWN(진단 옵션 동반 변동 또는 다른 미후킹 writer), 사전등록 기준(≤18,791) 안. (2) 마스크 구간 밖 present의 stale 합은 이번에 측정하지 않았다(hold 합은 전 present 대상). (3) s6 1회라 r1∩r3 교집합 기준 대신 마스크 프레임별 합으로 비교. (4) `blend_4685C0_reject_bounds`는 화면 밖 호출이라 정상. save000 pair HOLD는 기존 사유와 gate별 동일.

## 다음 한 가지

middle(Opus) H-D2r 독립 검수 → 수용 시 p141..143 좌하단 꼬리·diag2 761 px 잔여 판단, 또는 가장자리 마우스 스크롤·HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 중 선택. 변경은 uncommitted, 커밋 0, 전체 `make check` 결과는 STATUS에 보강한다.
