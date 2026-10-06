# G1 middle lap968 — lap966 H-E3 수용 · 다음 work 가설 H-T(툴팁 BltFast 미러)

- 작성: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(중간계획·독립 검수). 게임/source/실행/commit 0.
- 입력(읽기 전용): 공유 temp `20261005_lap966_work_unclipped_bind/{r1,r2}`, 비교 기준 `20261005_lap963_work_terrain_edge/r1`, census map `20261004_lap951_census_residual_ps3_r6/artifacts/census/census_map.bin`(SHA256 `e8c0b590…113d`).
- 산출(공유 temp `20261005_lap968_middle_review/`, 제품 helper import 없음): `recalc_lap968.py` `c32262d4…fe9f` → `recalc_lap968.json` `e8fbcf5a…20a`; `residual_class_lap968.py` `401577c5…1267` → `residual_class_lap968.json` `d35a3717…a265`; 시각 확인 `side_prod_overlay_lap968.png`·`crop_*_lap968.png`·`hud_full_lap968.png`.

## 1. 독립 재계산 (lap966 주장 대비 불일치 0)

| 항목 | lap963 r1 | lap966 r1 | lap966 r2 |
|---|---|---|---|
| 덤프 / steady(서수≥300) | 51 / 39 | 51 / 39 | 51 / 39 |
| steady 교집합 stale | 9,880 | **7,181** | **7,181** |
| F-1 x≥760·y<480 | 3,512 | **813** | **813** |
| 가장자리 행 288~379(마름모) | 1,438 | **0** | **0** |
| 가장자리 행 380~440(로고) | 1,541 | 792 | 792 |
| y<480 / y≥480 | 6,243 / 3,637 | 3,544 / 3,637 | 3,544 / 3,637 |
| keys − inserts (최종) | 766−763=3 | 764−764=**0** | 765−765=**0** |
| `cache_edge_unclipped_binds` | 없음 | 8 | 8 |
| PS3 present | 886 | 890 | 895 |
| 안전 계수 최대(clip mismatch·viewport mutation/restore·palette·outside diff) | 0 | 0 | 0 |

- r1·r2 교집합 픽셀 완전 동일. lap963 대비 제거 2,703, 새로 생긴 stale 4px(x783~788·y425~430, 로고 반투명 내부). 파일 SHA(mask/trace/pair)는 lap966 기록 prefix와 전부 일치.

## 2. 판정 (a) — H-E3 PASS(partial) 수용

- 기전 확인: 오른쪽 가장자리 마름모 stale 1,438→0, 바인드 누락 key 3→0, 바인드 계수 8, 결정적(r1=r2). 성능·안전 악화 0.
- F-1 813(≤750)·F-2 7,181(≤7,150) **수치 FAIL은 그대로 기록**한다(사후 임계 변경 없음). 미달 원인은 사전 예측이 P6 로고 잔여를 643으로 낮게 잡은 것이다. 남은 가장자리 813 = 로고 792 + 시계 21이며, 로고는 lap952/954 수용된 P6 명시 잔여다. lap965 §5 반증 조건("계수≥1인데 마름모 잔여")에는 해당하지 않는다(마름모 잔여 0).
- 따라서 compose lookup 가설(lap965 §5 부수 관찰)로 넘어갈 근거는 없다. strategy 재호출 조건(lap965 §6)도 충족하지 않는다.

## 3. 판정 (c) — r1 minimap `same_unit_before_after` HOLD는 비제품 관측 경쟁

- r1 baseline lane `unit_after`: slot124 `command=1`, `pending_command=16777219`, `pending_xy=5767258`(이미 목표 좌표). 다른 세 관측(r1 candidate, r2 baseline/candidate)은 `command=3`, `pending=16777217`, `production_type=5767258`. 즉 baseline 원본 lane이 명령을 아직 소비하기 전 tick에 관측한 것이다. `effect`·`same_result`·`same_camera`·`exact_gate_restore`는 r1도 PASS다.
- 수리한 mirror 경로가 없는 원본 lane의 관측 시점 문제이므로 제품 결함이 아니다. 이번 lap에서는 별도 진단으로만 둔다. 다음 pair에서 다시 나오면(누적 2회) work가 하네스 관측을 "command 전이 또는 N tick 대기"로 고치는 별도 lap을 연다. 기준·gate는 바꾸지 않는다.

## 4. 남은 7,181 분해 (lap966 r1, 영역별, census 근사)

| 덩어리 | px | 비율 | census last-writer | 비고 |
|---|---|---|---|---|
| HUD 상자 x618~718·y500~539 | **3,492** | 48.6% | dd_surface_blt 100% | 아래 §5 H-T |
| P6 반투명 로고 x700~799·y378~440 | 2,102 | 29.3% | terrain(lap953 blend hook 이전 census라 오귀속) | P6 명시 잔여, 수리 대상 아님 |
| 유닛 덩어리 x681~723·y215~254 | 961 | 13.4% | terrain 833·rle_tinted_clip 128 | 캡처에서 100% nearest, 다음 후보 |
| 선택 HP 바 x401~494·y153~159 | 423 | 5.9% | 혼합(rect_border·tinted_clip·terrain) | 후보 |
| HUD 기타 / 시계 / 나머지 | 145 / 21 / 37 | 2.8% | — | — |

- 정정: STATUS·lap966의 "y<480·x700~760 약 1,895"는 독립 덩어리가 아니다. 로고 왼쪽 1,310 + 유닛 548 + 37이다.

## 5. 다음 work 가설 H-T (FEASIBLE, Sonnet 1 lap)

**관찰:** candidate trace에 PS3 `blt_fast` — caller `0x004960A5`, source `0x01E6DDA0`(300×100 offscreen), source_rect `{0,0,101,40}`, flags 17(`SRCCOLORKEY|WAIT`), 대상 = 비primary 832×600 back buffer, 위치 (618,500), `mirror_gate_reject=not_primary`, `mirror_handled=0`. 대상 사각형 x618~718·y500~539가 stale 상자와 일치한다. 입력 trace의 커서는 끝까지 논리 (668,540)(F 버튼)에 머문다 → 커서 hover 툴팁 surface다(lap944 같은 칸 툴팁 `일본 농부 800/300/10`, lap962 §3 (c)).
**기전:** 패널 전송(`g1_mirror2x_panel_transfer`)이 그 칸을 covered·expected로 채운 뒤, 미러되지 않는 툴팁 BltFast가 같은 픽셀을 바꾼다 → present에서 expected≠pixel → 매 프레임 nearest fallback(stale). 화면 내용은 맞고 화질만 nearest다.

### 5.1 최소 구현
1. `hook_blt_fast`(direct_draw_trace.c 1444행 원본 호출 주변, `g1_mirror2x_panel_transfer` 옆)에 overlay 미러 1개: 대상 비primary, source가 패널 surface가 아님, `flags & DDBLTFAST_SRCCOLORKEY`, 사각형 크기 ≤320×128이고 화면 800×600 안, PS3일 때만. 원본 호출 **전**에 대상 사각형을 read-only lock으로 복사하고, 호출 **후** 다시 lock해 **바뀐 픽셀만** mask로 잡는다(census `g1_census_surface_blt_begin/end`와 같은 방식).
2. 바뀐 픽셀에 대해 post-Blt 대상 프레임(사각형+1px 경계, 화면 밖은 clamp)으로 `g1_scale2x_build_masked`를 돌려 `g_mirror` 2×2를 쓰고 `g_expected_snapshot=post 값`, `g_covered=1`. 판정/복사 로직은 host 테스트 가능한 header helper로 뺀다(`g1_panel_layer.h`의 `g1_panel_apply_transfer` 형식).
3. 계수(진단, 기존 키·pin 불변): `overlay_blt_mirrored_calls`, `overlay_blt_mirrored_pixels`, `overlay_blt_rejects`.
4. host 테스트: 바뀐 픽셀만 covered, colorkey 투명(불변) 픽셀은 기존 covered 유지, 경계 clamp, 크기 상한 거부, primary 대상 거부.

### 5.2 실행
`make lint`·`make typecheck`·focused → fresh save006 scale2x pair 1회(필요하면 2회). 명령과 `--stale-mask 6-12,30-34,300-301,585-620,880`은 lap961/963/966과 같다. 비교 기준 lap966 r1.

### 5.3 사전등록 예측(진단, 새 gate 아님)
- T-1: `overlay_blt_mirrored_calls` ≥1(PS3), HUD 상자 x618~718·y500~539 steady 교집합 3,492 → **≤1,750**(≥50% 제거). 툴팁 글자가 BltFast 뒤 GDI(`GetDC`+`TextOutA`)로 그려지면 글자 픽셀은 남을 수 있다(lap950 §GDI 오귀속) — 그래서 100%가 아니라 50%로 잡는다.
- T-2: 교집합 전체 7,181 → **≤5,450**. 다른 덩어리(로고 2,102·유닛 961·HP 423)는 ±5% 안.
- T-3: present ≥854·p95 ≤28ms·안전 0·V1/V2/V2q/Scale2x PASS·palette violation 0·outside diff 0·minimap effect PASS·원본 EXE/save MATCH·`source_unchanged`·game 사본만 삭제.
- V2s raw는 공개만 한다(기존 gate 불변). lap966 2,776/2,784보다 +200 넘게 오르면 회귀로 middle에 보고한다.

### 5.4 반증
- 계수 0 → 이 경로가 실행되지 않는다(조건이 너무 좁음). 조건과 실제 trace 필드를 대조해 기록하고 H-T HOLD.
- 계수 ≥1인데 상자 stale이 ≥3,000 그대로 → BltFast 뒤 다른 writer가 덮는다. 남은 픽셀을 그 frame의 post-Blt 값과 비교해 GDI 글자 후보로 기록하고 middle에 넘긴다.
- 안전 계수 >0 또는 V1/V2/V2q/Scale2x FAIL → 수리 되돌림 판단을 middle에 넘긴다. covered 축소로 맞추지 않는다.

## 6. strategy 재호출 조건

기존(lap933 §6·lap938 §7·lap944 §6·lap946·lap952 §6·lap956 §7·lap958 §5·lap960 §6·lap962 §6·lap965 §6) 유지. 추가: H-T 반증(계수≥1·상자 그대로)이고 GDI 글자 경로도 hook 불가로 판정될 때.

## 7. 범위 밖·금지

V2s gate 의미 변경(W-1 자동 적용)·한도·V1/V2/V2q·Scale2x validator·PS3 통계량·golden 변경, 과거 raw/pair-result 재작성, covered 축소, 캡처 시점·영역 변경, P6 로고 수리 재개, G2/G5 수정·G3/G4 재개, 원본/참고 저장소 쓰기, commit/publish/deploy.
