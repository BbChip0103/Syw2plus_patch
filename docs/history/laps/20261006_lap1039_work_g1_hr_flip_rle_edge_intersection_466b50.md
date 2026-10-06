# 2026-10-06 | lap1039 | G1 work H-R — `0x466B50` 화면 가장자리 교집합 미러(`mirror_flip_rle`)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 모든 변경 uncommitted.
- 가설: lap1038 middle 사전등록(§H-R) — 기후킹 `0x466B50`은 x·y·w·h를 32비트 부호값 그대로 쓰고 클립하지 않는데 wrapper는 사각형 전체가 화면 안일 때만 미러해서, 가장자리에 걸친 호출이 통째로 `reject_size`(75/76)였다. 화면 교집합만 diff 미러하면 표본 B 4·C 22의 `0x466BB3` stale이 0이 된다.
- 변경 파일:
  - `tools/inmm_stub/g1_rect_fill.h`: 순수 함수 `g1_flip_rle_region()`+`G1FlipRleRegion`(int32 해석, int64 합산, 교집합·`clipped`·`wrap` 판정) — 호스트 gcc로 경계 테스트 가능하게 분리.
  - `tools/inmm_stub/g1_mirror2x.c`: `mirror_flip_rle` 재작성(인자 `a_x..a_h` → int32 교집합, 전용 before 버퍼에 교집합만 복사, `g1_overlay_blt_apply`에 교집합 좌표, 원 인자 6개를 1회 그대로 전달, `layer_drift_write_begin/end(…G1_FLIP_RLE…, why, x, y, w, h)` 추가), 신규 계수 `reject_bounds`·`clipped_calls`·`wrap_calls`(+reset·accessor).
  - `tools/inmm_stub/g1_mirror2x.h` accessor 3개, `tools/inmm_stub/direct_draw_trace.c` 요약 키 `flip_rle_466B50_{reject_bounds,clipped_calls,wrap_calls}` + `flip_rle_details[240→400]`(`mirror_details[6600]` 유지: 최악 약 6,141+약 135 < 6,600).
  - `tests/test_g1_rect_fill.py`: `test_flip_rle_hook_table_and_wrapper_contract` 갱신(원 인자 1회·int32·drift 기록·계수 9개), 신규 `test_flip_rle_region_intersects_screen_like_unclipped_original`(x+w=800/801/832/833, x=-1, y+h=600/601, y=-3, w·h≤0, 16비트 아님 `0x00010010`·`0xFFFFFFF0`, `INT32_MAX` 오버플로).
  - 절차 정정: 구현을 먼저 쓰고 테스트를 맞췄다(RED 선행 확인 없음). 호스트 gcc 테스트로 경계값은 GREEN 확인했다.
- 원본 SHA / 후보: 원본 EXE `b56986e0…8ac`(pair-result `source_unchanged` true 전 run). source sha256: `g1_mirror2x.c` `4c4a4152…ef5421`, `g1_mirror2x.h` `8521fc27…`, `g1_rect_fill.h` `dbd3e2f8…`, `direct_draw_trace.c` `b8fa55a2…`, `test_g1_rect_fill.py` `22605564…`. old bytes `51 53 56 57 8B 7C 24 18`은 기존 설치 검증을 그대로 쓴다.
- 실행(공유 temp `20261006_lap1039_work_hr/`, 로그 `logs/gates/lap1039_hr_*`): `run_r.sh` `7c891077…` — save000 watch pair 2회(`--layer-drift --screen-watch --drift-samples "695,468;766,139;799,315" --stale-mask …`, lap1037 w와 동일 인자), save000 성능 후보/대조 교대 2쌍(A/B/A/B, 1분 load ≤4.5 대기 최대 30분, 실제 대기 40/0/0/20초), save006 env-off pair 2회. 대조 = `ctl_patch.py` `fe82b8cc…`가 H-P·H-Q·H-R 세 wrapper 첫 줄에 `return g_original_…`(CONTROL-TEMP)를 임시 삽입, 매 대조 뒤 product 사본(`g1_mirror2x.c.product`)으로 복원: restore sha `4c4a4152…` = product, `CONTROL-TEMP` 0건(2회 모두, 최종 소스도 확인). 8 run 전부 pair exit 2 = 기존 pair HOLD(V2s raw)이며 이번 변경과 무관.
  - **무효 처리한 첫 launch:** 첫 launch의 pid 확인이 실패해 `run_r.sh`를 한 번 더 띄웠고 두 인스턴스가 동시에 돌았다. 두 스크립트와 probe 자식만 종료하고(소스 product 복원·sha 일치 확인) 산출물은 공유 temp `invalid_concurrent_launch/`, `logs/gates/invalid_lap1039_concurrent/`, `local/runtime/invalid_concurrent_*`로 격리 보존했다(수치 미사용). 이후 단일 인스턴스로 전체를 다시 실행한 결과만 아래에 쓴다.
  - 분석: `analyze_r_s0.py` `094e8e61…`(lap1037 `analyze_q_s0.py` + `flip_rle_466B50_*` 전 키), `analyze_r_s6.py` `29d829e8…`(기준 = lap1037 `q_s6_r1/r2`), `isect_r.py` `90534742…`(lap1037 동일). lap1037 `q_w_r1/r2`에 `isect_r.py`를 돌려 2,064를 재현해 방식을 확인했다. 요약 `s0_summary.json` `4a72fa6a…`, `s6_summary.json` `71c2cd04…`.

## 수치

| 항목 | 기준(lap1037 w·s0·s6) | lap1039 |
|---|---|---|
| R-0 항등식 `inv = mirrored + reject_*`(`flip_rle_466B50`) | — | w r1 781=770+11, w r2 778=767+11, s0 r1·r2 780=769+11, save006 945=945 / 950=950 전부 성립. reject_target/size/guard 0 |
| R-0 안전 7종·cleanup·source_unchanged·scene_state_equal | 0/true/true/true | 전 run 0/true/true/true(ps3 410~412·save006 880/894) |
| R-0 관측 | — | w r1·r2: `reject_bounds` 11·`clipped_calls` 65·`wrap_calls` **0**, mirrored_pixels 381,512/379,456. save006: clipped 0·wrap 0·bounds 0(모두 화면 안) |
| w 레코드(466B50, 42/41건) | — | clipped 36/35·mirrored 6. 기하: `789,306 26×25`(p8~188 9주기, x+w=815), `724..752,96 80×80`(p185~189), `780..795,299..311 25×25`(p306~310, p367~370). 전부 x+w ≤ 832라 행 넘김 없음 |
| **R-1** `reject_size` | 75/76 | **0** (전 run) — 75/76 → clipped 65 + bounds 11로 이동 |
| **R-1** 표본 stale present B / C | 4 / 22 | **0 / 0**(w r1·r2). A는 1(`0x46884E`, p229) 불변 |
| **R-2** 마지막40 stale 중앙값 | 26 | **26 / 26**(w r1·r2) — 미달(< 26 필요). 대조(세 미러 off) 596/624.5 |
| **R-2** w r1∩r2 39덤프 합 | 2,064 | **2,776** — 미달(< 2,064 필요), max 433→714 |
| R-2 표본 A | ≤1 | 1 |
| **R-3** 성능 후보 p95(s0 r1·r2) / ticks | ≤7ms·비 0.999~1.001 | **7 / 7** ms·tick_rate 19.99962/19.99965 vs baseline 19.99957/19.99949 → 비 1.0000 |
| R-3 대조(미러 off) p95 | — | 9 / 13 (후보보다 높음). load 시작: 후보 3.09·4.04, 대조 4.98·5.30 |
| **R-4** save006 env-off r1∩r2 / 신규 | 38프레임 0·신규 0·p95 ≤8 | **38프레임 0·39프레임 0**·기준 대비 신규 0·제거 0·cov p50 99.31%·게이트 v2/v2q/scale2x/input/minimap/loaded PASS, v2s FAIL(기존 raw gate). p95 **9**(r1, 시작 load 7.66)·**7**(r2) — r1은 ≤8 문자 기준 미달 |

### R-2 해석(미달이지만 신규 stale 없음)

- 프레임별로 보면 새 stale은 없다. 새 r1·r2는 같은 프레임의 기준 r1·r2 어느 쪽에도 없던 stale이 0이다(프레임 234·294·366·399 직접 확인).
- 줄어든 것: p26·p44·p71의 29 px×3 → 0(가장자리 표본 계열)과 p377의 5 → 0. 다른 프레임은 run별 값이 같다(6: 247, 12: 145, 144: 106, 174: 88, 204: 52, 234: 405, 294: 144, 388: 26, 399: 145).
- r1∩r2 합이 늘어난 이유는 기준 쪽 r2에 있던 run 변동(p352 128·p366 290·p234 402·p294 111)이 이번에는 r1과 같아져 교집합이 커진 것이다. 즉 2,064는 기준 r2의 변동이 낮춘 값이었고, 이번 run들은 서로 더 닮았다. 팝업 구간 p298..328(714/253/152/152)은 팝업 상자 run 변동 범위다(lap1031 판정과 동일 유형).
- 남은 stale = 유닛 크기(13×14·약 145 px) 덩어리와 팝업이다. 위치(중심 근처): p6 (409,628)·(483,568), p12 (367,599), p144 (467,779), p174 (452,718), p204 (391,788), p234 (468,754)·(434,675), p294 (448,728), p352 (473,713), p366 (377,783), p388 (470,795 — x=799 가장자리), p399 (220,786 — 가장자리 근처). 표본 3점 밖이므로 writer는 UNKNOWN이다.

## 해석

- **R-1(주 가설) 확정:** 표본 B·C의 마지막 writer가 `0x466B50`의 가장자리 걸침 호출이었고, 교집합 미러로 `reject_size` 75/76이 0이 됐으며 B 4·C 22 stale이 모두 0이다. `w` 레코드가 걸침 기하(26×25 @x=789, 80×80 @x=724~752 등)를 직접 보여준다. wrap(행 넘김) 호출은 이 장면에서 0이다.
- **R-2 미달:** 표본 B·C가 0이 돼도 화면 집계(마지막40 중앙값 26)는 움직이지 않았다. 남은 26은 표본 밖 writer다. 가설의 판정 지표(표본 stale)는 충족했고, 사전등록 R-2 문자 기준은 미달이다. 새 stale은 없다.
- **R-3:** 후보 p95 7/7로 충족, 대조는 오히려 9/13이다. 미러 비용 미검출.
- **R-4:** stale 비회귀는 충족. s6 r1 p95 9는 시작 load 7.66에서 측정한 값이고(r2는 7), 이 장면은 `0x466B50` 호출이 전부 화면 안(clipped 0·bounds 0)이라 H-R 경로가 바뀌지 않는다 → 환경 UNKNOWN(p95 8/8이던 lap1037과 호출 경로 동일).

## 회귀 / 남은 위험 / 독립 검수

- 호스트 테스트: `tests/test_g1_rect_fill.py`·`test_g1_panel_layer.py` 18 passed, `make lint`·`make typecheck` PASS. 전체 `make check`는 기록 freeze 뒤 1회 실행하고 결과는 STATUS에만 보강한다.
- 남은 위험: 표본 3점뿐. `reject_bounds` 11회의 기하는 `w` 레코드에 없다(표본 점을 포함·변화시키지 않으면 기록하지 않음). wrap 경로(x+w>stride, y+h>600)는 이 장면 0회라 실장 검증이 없다(호스트 경계 테스트만). 기준 r2의 run 변동 때문에 r1∩r2 합은 판정 지표로 불안정하다.
- 사용자 승인 상태: 기술 부분 수용 요청일 뿐 G1 마일스톤 승인이 아니다.
- 독립 검수(middle)가 확인할 것: (1) 새 스크립트로 w r1·r2·s0 r1·r2·대조 r1·r2·save006 r1·r2 재계산(항등식·reject_size 75/76→0·표본 B/C 0·마지막40 26·r1∩r2 2,776 및 위 R-2 해석의 프레임별 대조·save006 0), (2) **R-2 판정**: 문자 기준 미달을 "가설 지표 충족·신규 stale 0·교집합 지표 불안정"으로 수용할지, (3) `mirror_flip_rle` 코드 검수(원 인자 6개 1회, int32 해석, 교집합 복사, wrap 조건이 `stride` 기준), (4) R-4 p95 9 판정, (5) 무효 처리한 동시 launch 산출물이 수치에 섞이지 않았는지, (6) 다음 work 사전등록: 남은 유닛 크기 덩어리(위 좌표)의 writer 귀속.
- 다음 한 가지: middle H-R 독립 검수(R-2 판정 포함) → work 남은 유닛 크기 stale 덩어리 writer 귀속(표본 3점 × 여러 run).
