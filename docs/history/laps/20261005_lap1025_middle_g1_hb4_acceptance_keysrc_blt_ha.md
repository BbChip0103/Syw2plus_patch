# 2026-10-05 | lap1025 | G1 middle — H-B4 독립 검수(PASS 수용) → 표본 A·남은 stale 71.6% = 미러 없는 KEYSRC `Blt` 귀속 → work H-A 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 실행·source 변경·커밋 0.
- 가설: lap1024 work H-B4(`0x467B00` diff 미러)의 B4-0~B4-5 수치가 raw로 재현되는가. 재현되면 남은 화면 stale 성분 중 다음 work를 정한다.
- 예상 PASS / FAIL 조건: 새 스크립트로 재계산한 판정 영향 불일치가 0이어야 한다. diff는 H-B `mirror_blend_wrle`와 동형이어야 한다(16비트 부호 확장, 화면 교집합, reject, 원 인자로 원본 호출, before 버퍼 독립).
- 변경 파일 / 커밋: 이 기록, `docs/STATUS.md`, `loop/ESCALATE_SOL` 삭제(원문은 아래 부록). 공유 temp `20261005_lap1025_middle_review/`(모두 uncommitted):
  - `recalc_lap1025.py` SHA256 `3fd59698824c600d7983dd6b6d69e2bbc13408a6a26497d68d77f56c6c3cdc37` → `recalc_lap1025.json` `ab9cc5f13df7afff2a88fa4c4a3bfd262d855580885ae1e513d94e2d720124b0`·`recalc_stdout.txt` `fb2b0362…a111`
  - `recalc2_lap1025.py` `6353fd1658d63a577e291072c5fb3011d6258536ae1bc1c7478d9595ccd0e565` → `recalc2_lap1025.json` `c02f045a297e76d514a30bb06cf429ef1c52e07e49ba54d5bb8d6114bdefb336`
  - `recalc3_lap1025.py` `60500e1d1b054286e93fb03354264f58cea18938f19c19ce400ab290473b8624` → `recalc3_lap1025.json` `4917e648a736fac95037c57b7b8a25eb02287e4064c14fc65127b36667b59174`
- 원본 SHA / fixture: 4 run pair-result의 `source_exe_sha256`·`private_exe_sha256` = 원본 `b56986e0…8ac`(재계산 스크립트로 확인). save000 `1c703551…19da`(index 1), save006 `616b7997…a064`. 활성8인 부하 증명 아님.
- 검수한 source: 현재 `g1_mirror2x.c` `0fb12c3b…e152`, `g1_mirror2x.h` `c3e80bf5…f18a`, `direct_draw_trace.c` `a6c28fe2…a703`, `tests/test_g1_rect_fill.py` `60e2861d…53be`. 모두 work 기록과 같다. 4 run bridge 사본(`g1_mirror2x.c`·`.h`·`direct_draw_trace.c`·`g1_layer_drift.h`)도 현재 source와 같다. bridge `_inmm.dll`은 run마다 SHA가 다르다(work 기록의 "run마다 재링크"와 일치).

## 1. 독립 재계산(`analyze_hb4.py`·`analyze_hb4_s6.py`·제품 helper 미사용)

비교 기준: lap1022 hb3 s0 2 run(screen watch 켬)과 lap1020 hb2 s0 v2 2 run(layer drift만). 두 기준의 화면 stale 창 값은 서로 같다.

| 항목 | work | 재계산 r1 / r2 |
|---|---|---|
| B4-0 scene | 카메라 (39,53)·tick 50600/50599·50601/50599 | 카메라 (39,53)→(39,53)·units 375·scene_state_equal true. tick(원본/후보) 50599/50600·50599/50601(work는 후보/원본 순서로 적음, 값 동일) |
| B4-0 계수 | inv 14,099 = 2,832+11,211+56 / 14,150 = 2,838+11,256+56 | 같음. reject_target·guard 0, 항등식 true(not_ready 0) |
| 안전·cleanup·source | 0·true·true | 안전 키 중 0이 아닌 것은 `panel_transfer_mismatch_cleared`뿐이다(lap1013에서 판별력 없다고 정리한 계수). cleanup [true,true]. source_unchanged [true,true,true] |
| B4-1 표본 stale | A 41·B 0·C 0 | A 41(구간 [298]·[299]·[300]·[301..338])·B 0·C 0. 기준 2+2 run은 A 41·B 135·C 210 |
| B4-2 귀속 | `drift_unattributed` A5/B1/C1, w `467B00` clipped 330·mirrored 213 | 같음. u = A p298·299·300·301·339, B p168, C p339(기준 u는 5/19/25). `467B00` w 중 표본 값 변화 345 |
| B4-3 화면 stale | p0..83 656·p84..206 245·p207..365 656·합산 362.5·p366.. 414.5/399.5·마지막40 414.5 | 같음. 기준 4,661·6,215·6,944·6,481·424.5~427·424.5 |
| B4-4 성능 | p95 7 ms·비 1.000003/1.000001 | pair p95 7/7, PS3 `elapsed_ms` 최근순위 p95 7/7, 비 1.0000031/1.0000013 |
| B4-5 save006 | 38프레임 24 px·39프레임 0·신규 0·p95 7·cov p50 99.30% | 38프레임 r1∩r2 24 px(y515..520×x616..619). lap1022 기준 대비 신규 0·제거 0. 프레임 880은 두 run 모두 있고 stale 0 px라 **39프레임 교집합 0**. PS3 p95 7/7 ms(max 11/9)·cov p50 0.993. layer_drift·screen_watch 파일 미생성(env-off). `blend_467B00` inv 58,224/62,214 = mirrored 84/87 + reject_bounds 58,140/62,127 |

**판정 영향 불일치는 0이다.** 전사 차이는 tick 표기 순서 1건뿐이다(값 동일).

## 2. diff 검수(lap1022 bridge `46ef3979…` 대비)
- 추가된 것: `#define G1_BLEND_CLIP 0x00467B00u`·길이 5, 원본 포인터, 320×128 before 버퍼(`g_blend_clip_before`, 다른 wrapper와 공유 안 함), 계수 9개, hook state, getter 9개, `mirror_blend_clip`, install 체인 1줄(old bytes `83 EC 14 33 C0`), reset 9줄, restore·`installed` 조건·`g_original_blend_clip = NULL`. 기존 줄 변경은 restore 조건식 줄바꿈 1곳뿐이다.
- `mirror_blend_clip` 본문은 `mirror_blend_wrle`와 같은 구조다. 다른 점은 이름·버퍼·계수·`G1_BLEND_CLIP` 태그뿐이다.
  - 인자 4개를 `(int16_t)`로 부호 확장한다.
  - renderer·buffer·stride·높이 600·캐시/패널 buffer 검사를 한다.
  - 화면 교집합을 구하고, 비면 `reject_bounds`, 320×128를 넘으면 `reject_size`로 센다. before 복사는 크기 검사 뒤에만 하므로 overflow가 없다.
  - 원본은 **원래 DWORD 인자 그대로** 호출한다.
  - `g1_overlay_blt_apply`가 실패하면 `reject_size`로 센다.
  - `layer_drift_write_begin/end`로 감싼다.
- 원본은 자체 클립 사각형(`[ecx+0x4D0..0x4DC]`, lap1023 §2)으로만 쓴다. 그래서 화면 교집합 diff는 상위집합이고 안전하다.
- reject_bounds 11,211/14,099(79.5%)는 화면 밖이거나 크기 0인 호출이다. w 레코드에 `467B00` reject_size 항목은 없다(w는 표본이 걸린 호출만 기록). reject_size 56(0.4%)의 (w,h)는 미기록이다. 수용 범위 안이다.
- `tests/test_g1_panel_layer.py:115`의 소스 형태 pin(`mirror_details[4096]`→`[5000]`)은 metrics 문자열 버퍼 확장에 따른 기대값 동반 수정이다. 안전 pin/golden이 아니므로 수용한다.

## 3. 판정
**H-B4를 수용한다(PASS, 기술 부분 — 제품/마일스톤 마감 아님).**
- 표본 B 135→0, C 210→0.
- 화면 stale p84..365 6,481→362.5(−94%), p0..83 4,661→656.
- 성능 무영향, save006 비회귀.
- 프레임 880을 포함한 39프레임 교집합 0을 직접 확인했다. lap1000 r1 이후 미검증이던 backlog "프레임 880 부재 run의 39프레임 검증"이 이것으로 해소됐다.
- 화질 한계: 목적지 의존 혼합의 1x 결과를 확대한다. H-B와 같은 수준이며 P6 범주다.

## 4. 새 근거 — H-B4 뒤 남은 save000 stale의 71.6%는 미러 경로가 없는 KEYSRC `Blt`다

### 4.1 화면 stale 분해(recalc2, r1 = r2)
| 창 | H-B4 중앙값 | 기준 중앙값 |
|---|---|---|
| p0..23 | 441 | 1,968 |
| p24..58(일시 덩어리) | 3,444 | 4,551 |
| p59..83 | 216 | 6,317 |
| p84..297 | 316 | 6,315.5 |
| **p298..338(표본 A 구간)** | **16,261** | 22,944 |
| p339..365 | 591 | 7,331 |
| p366.. | 414.5/399.5 | 424.5~427 |

- H-B4 뒤 stale 총합 895,111 px·present 중 640,929(**71.6%**)가 p298..338 41 present에 몰려 있다. 기준에서는 32.1%였다.
- A 구간을 빼면 p0..365 중앙값은 351이다.

### 4.2 writer 귀속(recalc3, trace `blt` 이벤트를 PS3 present 순번에 매핑)
- 후보 r1·r2와 lap1022 r1 모두 PS3 present **298·299·300·301**에서 같은 호출이 나온다: `IDirectDrawSurface7::Blt`, flags `0x1008000`(DDBLT_WAIT|DDBLT_KEYSRC), 호출처 `0x004D3ABC`.
  - 목적지는 present 원본 back buffer(`0x01E75340`, 832×600 = `mirror2x_present.source_identity`)다.
  - 원본 surface는 `0x01E6D898`이고 source_rect NULL(원본 surface 전체)이다.
  - 목적지 사각형이 커진다: (86,94)-(137,132) 51×38 → 102×76 → 153×115 → **(26,49)-(196,177) 170×128**. 확대 열림 애니메이션이다.
- 표본 A (112,126)은 네 사각형 모두 안에 있다. A stale 구간 [298]·[299]·[300]·[301..338]과 u 값 94·215·163·187(lap1023)이 이 4회와 present 단위로 맞는다. lap1022/1023의 "A = `wined3d.dll` tid 288 쓰기"는 이 Blt를 wined3d가 별도 스레드에서 실행한 것으로 설명된다.
- **원본 lane(baseline)에도 같은 사각형·호출처·flags의 Blt가 5회 있다**(마지막 170×128이 2회). 원본 게임 동작이다.
- 후보 `hook_blt`(`direct_draw_trace.c:1176`)에는 census/trace만 있고 **미러 경로가 없다**. overlay diff 미러(`g1_mirror2x_overlay_blt_begin/end`)는 BltFast 전용이다. 그래서 이 쓰기는 HD 화면에 반영되지 않고, 1x 내용이 다시 그려지는 p339까지 stale로 남는다.
- 170×128은 `G1_OVERLAY_MAX_WIDTH/HEIGHT`(320×128) 안이다. 기존 `g1_overlay_blt_apply` diff 미러로 처리할 수 있다 → **FEASIBLE**.
- 한계:
  - trace `blt` 이벤트는 유형당 256개에서 잘린다. 후보는 p301 이후 Blt 반복 여부가 보이지 않는다(원본은 5회).
  - save006에는 KEYSRC Blt가 0이다(flags `0x1000000` 3회·호출처 `0x0049581B`가 있으나 save006 stale는 0).
  - 원본 surface `0x01E6D898`이 무엇인지(800×600 화면 사본으로 추정)는 미확인이며 diff 미러에는 필요 없다.

### 4.3 나머지 성분(backlog로 보존)
- p24..58 일시 덩어리(중앙값 3,444)는 writer 미확인이다.
- p0..23 441과 바닥 192~656은 이 창들에 공통인 소량 성분이다. 정체는 미조사다.

## 5. 다음 work H-A 사전등록(Sonnet work 1 lap, 제품 변경)

목표: 원본 게임의 back buffer 대상 `IDirectDrawSurface7::Blt`(KEYSRC 확대 Blt 포함) 결과를 HD 화면에 diff 미러한다. 이것으로 save000 표본 A stale과 p298..338 덩어리를 없앤다.

### 5.1 구현 범위(최소, BltFast overlay 미러 동형)
- `g1_mirror2x.c`/`.h`: `g1_mirror2x_overlay_rect_blt_begin/end`(이름은 work가 정한다)를 추가한다. 입력은 목적지 사각형(`LPRECT dst`)이다.
  - 조건: `g_mirror && g_covered && g_expected_snapshot`, 목적지 ≠ primary, Lock READONLY 성공, `desc.dwWidth ≥ 800`·`dwHeight == 600`·`lPitch ≥ 800`이어야 한다.
  - dst가 NULL이면 surface 전체를 뜻하므로 reject_size로 센다. 그렇지 않으면 dst ∩ [0,800)×[0,600)을 쓰고, 비면 reject_bounds다. 320×128을 넘으면 reject_size다.
  - before 복사는 기존 BltFast용 `g_overlay_before`와 **분리된** 버퍼로 한다.
  - 원본 Blt 결과가 SUCCEEDED일 때만 다시 Lock해서 `g1_overlay_blt_apply`를 부른다.
  - flags는 거르지 않는다(COLORFILL/KEYSRC/stretch 모두 diff로 안전하다). 단 계수에 KEYSRC·COLORFILL 호출 수를 따로 센다.
- `direct_draw_trace.c` `hook_blt`: `g1_mirror2x_enabled() && read_state(0x004ED818) == 3 && !record->is_primary`일 때만 begin/end로 원본 호출을 감싼다. present 자체 Blt(목적지 1600×1200 primary 쪽)는 primary·크기 조건으로 제외된다. work가 실제 identity로 확인한다.
- 계수: `overlay_rect_blt_{invocations, mirrored_calls, mirrored_pixels, changed_calls, clipped_calls, keysrc_calls, colorfill_calls, reject_bounds, reject_size, reject_lock}`를 metrics에 추가한다. 이벤트 256 상한에 기대지 않는다.
- 테스트: 기존 overlay BltFast 계약 테스트 형식으로 RED→GREEN. 검사 대상은 hook_blt가 begin→original→end 순서인지, PS3·non-primary 조건, dst NULL/화면 밖/크기 초과 reject, 버퍼 분리다.

### 5.2 실행(순차)
- save000 pair 2회: lap1024 `run.sh` s0 인자 그대로(`--fixture save000 --scene-actions none --performance-window --layer-drift`, screen watch 끔).
- save006 env-off 비회귀 pair 2회: lap1024 s6 인자 그대로.
- 실행 후 `game` 사본만 삭제한다. 디스크 여유는 현재 68G다.

### 5.3 사전등록 판정
- **A-0 유효**: 안전 0(`panel_transfer_mismatch_cleared` 제외), cleanup·source_unchanged true, 카메라 (39,53)·units 375여야 한다. `overlay_rect_blt_invocations` > 0이고 `keysrc_calls` ≥ 4여야 한다. invocations = mirrored + reject_bounds + reject_size + reject_lock 항등식이 성립해야 한다.
- **A-1 표본(주 판정)**: 표본 A stale present 41 → **≤2**(두 run 모두)여야 한다. B·C는 0 유지(≤2)여야 한다.
- **A-2 화면 stale**: p298..338 중앙값 16,261 → **≤1,000**이어야 한다. 다른 창은 H-B4 값 대비 +10% 이내여야 한다(p0..83 ≤722·p84..297 ≤348·p339..365 ≤651·마지막40 ≤456).
- **A-3 성능**: p95 ≤16 ms, ticks/s 비 ≥0.95.
- **A-4 save006 비회귀**: 38프레임 r1∩r2 = 24 px(성분 D)·신규 0이어야 한다. 프레임 880이 있으면 39프레임 0이어야 한다. p95 ≤16·안전 0이어야 한다. `overlay_rect_blt` 계수는 공개한다.
- FAIL이면 원인(Lock 실패·identity·크기·KEYSRC 처리)을 기록하고 1회 수리 후 재실행한다. 그래도 FAIL이면 인계한다.

## 회귀 / 남은 위험 / 독립 검수
- 이번 lap은 문서·재계산·read-only 검수만 했다. 게임/source/commit은 0이다. 전체 `make check`는 SKIP했다. source가 불변이고 lap1024 full PASS 1621이 유효하다. 다음 work가 DLL 변경 뒤 실행한다. focused 검사 결과는 STATUS에 보강한다.
- 남은 위험:
  - Blt는 wined3d가 별도 스레드에서 실행한다. after Lock이 그 완료를 기다리는지는 BltFast 경로와 같은 가정이며 A-1로 검증한다.
  - KEYSRC 확대는 1x 결과를 확대하므로 HD 디테일이 없다(P6 범주).
- backlog:
  - 갱신: "프레임 880 부재 run의 39프레임 검증"은 해소, "A wined3d tid 288"은 KEYSRC Blt로 귀속
  - 추가: p24..58 일시 덩어리 3,444, 바닥 192~656
  - 유지: save000 `--stale-mask` 부재, save006 짧은 run 꼬리, 성분 D, hold keydown 위상, 가장자리 마우스 스크롤, wrap 쓰기 미추적, save000 overlay BltFast rejects 451
- 사용자 승인 상태: 기술 검수일 뿐 G1 마일스톤 승인이 아니다. G6/G7 사용자 합격(APPROVALS lap989)은 대기 중이며 비차단이다.
- 다음 한 가지: work H-A(위 §5).

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문(lap1024 work, SHA256 `3355344ea4bf24d6f612abccc24c9f40ad18ac8d1344f3e8dcc3bfea9c25b59b`)

```
lap1024 work(Claude Code claude-sonnet-5-5) G1 H-B4 인계 (마일스톤 경계 아님; 사전등록 B4-0~B4-5 전부 PASS, 독립 검수 요청).
- 한 일: g1_mirror2x.c에 hook 0x467B00(old bytes 83 EC 14 33 C0)·mirror_blend_clip(H-B mirror_blend_wrle 동형, 화면 교집합 before→원본→g1_overlay_blt_apply, G1DriftWrite 래핑, 계수 blend_467B00_* 9개)·getter·metrics 추가, direct_draw_trace.c mirror_details 4096→5000, 계약 테스트 RED→GREEN.
- 실행: save000 pair 2회(--layer-drift, screen watch 끔)+save006 env-off pair 2회, 전부 exit 2(기존 pair HOLD). 공유 temp 20261005_lap1024_work_hb4/.
- 결과: 표본 stale B 135→0·C 210→0·A 41 유지, drift_unattributed A5/B1/C1, 화면 stale p84..365 중앙값 362.5(기준 6,215/6,944)·마지막40 414.5, inv=mirrored+reject_bounds+reject_size 일치(reject_size 56=0.4%), p95 7 ms·ticks 비 1.000, save006 r1∩r2 38프레임 24 px(성분 D)·39프레임 0(880 포함)·신규 0·안전 0.
- middle이 확인할 것: (1) 4 run의 layer_drift/trace_raw/stale_mask를 analyze_hb4*.py 없이 새 스크립트로 재계산, (2) g1_mirror2x.c diff(mirror_blend_clip: 16비트 부호 확장·교집합·reject·원본 호출 원 인자·before 버퍼 독립) 검수, (3) 남은 화면 stale(p0..83 656·p207..365 656·p366..~415)과 A wined3d 41 present 중 다음 work 사전등록.
- 기록: docs/history/laps/20261005_lap1024_work_g1_hb4_blend467b00_diff_mirror.md. 변경 uncommitted.
```
