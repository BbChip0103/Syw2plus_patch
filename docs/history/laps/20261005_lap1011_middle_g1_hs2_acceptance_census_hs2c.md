# 2026-10-05 | lap1011 | G1 H-S2 save000 두 번째 장면 독립 검수 → 다음 work H-S2c(save000 census writer 지목)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(확인·계획) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 검수 대상: lap1010 work H-S2(하네스만, `tools/g1_saved_scene_probe.py` SHA `7abab17b…fdd0`, `tests/test_g1_saved_scene_probe.py` `7f257d42…1e6b`; 현재 파일 SHA = 두 run `execution_source.before/after` 일치·`unchanged` true)의 S-0~S-3 판정과 S-1 새 잔여 수치가 raw로 재현되는가, save000 로드 정체성이 증거로 서는가.
- 예상 PASS / FAIL 조건: lap1009 사전등록 S-0~S-3. 재계산 불일치·로드 정체성 불성립·required_tags/gate 의미 변화면 FAIL.
- 변경 파일: 이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL`(lap1010 work 요청) 처리 후 삭제, 원문은 아래 부록. source/test 변경 0.
- 원본 SHA / 후보 / fixture: 원본 EXE `b56986e0…08a8ac`(두 lane private 사본 동일), save000 `1c703551…19da`·save006 `616b7997…a064` 이번 직접 재해시 MATCH(synthetic UNKNOWN, 활성8인 부하 증명 아님). bridge 사본 r1=r2, `g1_mirror2x.c` `42245a20…`·`g1_census.c` `341a16c3…`·`g1_rect_fill.h`·`g1_overlay_blt.h` 현재 저장소와 동일; `inmm_stub.c`·`Makefile` 차이는 G2 `runtime_bridge.c`(`supply_probe_poll`) 빌드 주입분뿐 → 제품 source 불변.
- 재계산 방법(제품 helper·work `analyze_lap1010.py` 미사용, 새 스크립트): 공유 temp `20261005_lap1011_middle_review/`
  - `recalc_lap1011.py`(SHA `981b4425…330e`) → `recalc_lap1011.json` `b61fa441…67c7b9`(stdout `ba36c038…6d4e`): pair-result·두 lane trace_raw·stale_mask.bin(헤더 magic/state/covered/stale를 맵에서 재계수)·loaded PNG를 직접 읽고 numpy로 V2/V2s/V2q·nearest, 8-연결 성분, perf 히스토그램 nearest-rank p95.
  - `watch_pixels.txt`(`6649fb13…f0`): r1∩r2·프레임 300∩301 stale 교집합 성분별 3×3 내부 대표 픽셀. `s2_stale_overlay_r1.png`(`fe79ead5…7227`): baseline loaded 위 교집합 표시(진단용).
- 측정 / 판정(r1 / r2; exit 2/2, 로그 `4210e980…`/`16b1277a…`, pair-result `4d0be1eb…`/`6fb9470e…`, candidate trace `cb1183f6…`/`94ba1d4a…`, mask `60fc62c9…`/`0e116b1f…` 기록과 일치):
  - **S-0 재현**: scene state 두 lane 완전 동일(raw 비교 true, units 375·owners 8), snapshot tick baseline **50596**/candidate **50595**, 카메라 (39,53) 시작/끝/스냅샷 전부 동일, owner별 active 124/1/123/124/0/3/0/0 동일, `save_navigation [1]` 두 lane, fixture·EXE SHA 일치, cleanup ok 4/4, source_unchanged true.
  - **save000 로드 정체성 확인**: ① `SAVE_FIXTURES["save000"]` = `s1_load_evidence.FIXTURES["save000.dat"]`(크기 3,093,902·SHA·1-based index 1) 동일 pin, ② 하네스는 `SELECTED_INDEX_ADDRESS` 직접 읽기가 1일 때 확정(handler index-1 = save000), ③ PS3 진입 순간 tick candidate **50590** = lap701 middle이 독립 기록한 save000 `tload=50590`과 일치(save006 장면 tick ~24.7k·카메라 (158,101)와도 다름). → save000 로드 확정.
  - **S-1 재현(새 잔여)**: PS3 present 410, `stale_pixels` 마지막 40 중앙값 **7,675**(r1=r2)·처음 10개 8,267→15,273·전체 중앙값 8,808.5. 마스크 14 프레임(6–12, 30–34, 300, 301) 헤더 전부 일치, 프레임 ≥300 교집합 **20,623 / 20,601**, 전체 교집합 192, r1∩r2 20,472(r1만 151·r2만 129). 성분(r1) 12,651 `y64..168×x38..186`(A)·5,442 `y427..491×x371..502`(B)·1,167 `y0..25×x259..337`(C)·426·143… 총 51개(r2 48개, 상위 4개 동일).
  - **보강(work 미기록)**: A·B·C 영역의 stale은 프레임 6–34에서 **0**(B만 6–12에 50~592 일시)이고 300/301에서만 존재(A 12,668→13,311 증가) → 로드 직후 잔상이 아니라 present 34~300 사이에 생겨 **매 프레임 다시 그려지는**(움직이는) 미러 밖 writer. 초기 8~17k stale은 다른 위치의 일시 성분(전체 교집합 192)이다.
  - **S-2 재현**: nearest diff 124,372(93.52%)·world 흑 3,890→3,855(−35)·**V2s 629**·V2q 265, scale2x gate PASS, loaded PNG SHA r1=r2(두 lane). `mirror_validator` BLOCKED는 save006 pair와 같은 기존 동작.
  - **S-3 재현**: perf 히스토그램 p95 baseline **1**/candidate **7**·max 11(r1=r2), perf meta count 400·dropped 0·창 19.95s, tick rate 19.9996/19.9996 Hz. 안전 7종(clip_replay·viewport×2·palette·mask_outside·cache_clip·identity) trace 전 행 max **0**, panel 안전 5종 0. reject 비0: `panel_transfer_mismatch_cleared` 2,693,918·`overlay_blt_rejects` 451·**`flip_rle_466B50_reject_size` 76**, `textout_iat_reject_target` 6/2(work 미기록, save006에서도 비0 계열).
  - **정정/보강**: work는 reject를 "save006 lap1002 대비 같은 종류"로 적었으나 `flip_rle_466B50_reject_size`는 save006(lap996 F3-3 reject 0)에서 0이었고 **save000에서 새로 76**이다. wrapper는 화면 밖·`G1_OVERLAY_MAX` 320×128 초과 사각형을 거부(원본은 그려짐 → 미러 누락 = stale)하므로 S-1 잔여의 후보 기전이다. 단 A(149×105)는 화면 안·한도 이내라 단일 호출 거부로는 설명되지 않음 → census로 판별.
  - gate: required_tags 5개 불변, status HOLD = `scene-actions none`으로 selection/drag/minimap/production BLOCKED(설계상 예상, gate 의미 불변).
- 판정: **H-S2 PASS(partial) 수용** — S-0·S-2·S-3 재계산 불일치 0, S-1 새 잔여 수치 불일치 0, save000 로드 정체성 3중 근거로 확정. 제품 마감·사용자 승인 아님. G1 pair HOLD(V2s production raw, 사용자 판단 큐) 유지.
- 회귀 / 남은 위험: 제품 회귀 0. save000 고정 카메라 steady stale ≈20.6k(A/B/C)는 G1 시각 결함(HD 화면에 원본 갱신 미반영)이며 다음 수리 대상. save000 present 속도(410/20s)와 save006(868~901) 차이 원인 미조사(두 lane 동일 조건).
- 다음 한 가지: **work H-S2c — save000 census로 A/B/C writer 지목**(아래 handoff). census 결과가 FEASIBLE이면 다음 middle이 미러 hook(또는 flip 거부 수리)을 사전등록한다.

## Handoff — work H-S2c (save000 census writer 지목, 하네스만)

- 정적 확인(이번 middle): `--census-only` 분기(`main`, `_run_lane(variant="baseline", census=True, …)`)는 **`fixture`·`scene_actions`를 넘기지 않아** 그대로면 save006을 로드한다. `_scene_option_error`는 `scene_actions none`+`census_only`를 거부한다. PS3 census는 별도 대기 없이 장면 동작 중 창을 채우는 구조이고, `_LoadedOnlyComplete`는 loaded 캡처(+`--performance-window`) 직후 발생한다. `SYW2_G1_CENSUS_SKIP_PRESENTS`(lap974)는 건너뛴 present 뒤에 map·residual·watch를 무장한다. census 고정 hook 9종에 `0x466B50`·`0x4672E0`·`0x467580`·TextOutA는 **없다**(→ residual로 나타남).
- 최소 변경(제품 DLL·gate·validator·한도 변경 0):
  1. `_scene_option_error`: `census_only`는 `scene_actions none`과 결합 허용(나머지 거부 조합 유지). save000+census-only는 `--scene-actions none` 필수 그대로.
  2. census 분기 `_run_lane(..., fixture=args.fixture, scene_actions=args.scene_actions)` 전달.
  3. loaded-only 경로: `census`(PS3)면 `_LoadedOnlyComplete` 전에 `_wait_census_presents(census_path, 3, timeout)`(timeout ≥ 60+(skip+64)/10 s)로 64 present 창을 채우고 `census_wait` 기록, TIMEOUT이면 ProbeError.
  4. 테스트 RED→GREEN: census+none 허용·다른 조합 거부 불변, census 분기가 fixture를 전달(save000 pin 검사 경유), loaded-only+census에서 창 대기 호출. 기존 save006 census 동작 불변.
- 실행(순차, fresh runtime-root·공유 temp 새 폴더, game 사본은 끝나면 삭제):
  `--census-only --fixture save000 --scene-actions none --census-residual --census-skip-presents 250 --census-watch X,Y`
  - W-A `112,126`, W-B `437,463`, W-C `302,9`(lap1010 r1∩r2·프레임 300∩301 교집합 3×3 내부 대표점, `watch_pixels.txt`).
  - skip 250은 candidate 프레임 300(≈load+15s)에 맞춘 값. census lane은 원본(미러 없음)이라 PS3 present 속도가 다를 수 있으므로 present_boundary 시각으로 창 시간(load 기준 초)을 기록하고, hit 0이면 skip 120으로 1회 재실행.
- 사전등록 PASS/FAIL:
  - C-0 로드·census 유효: `save_navigation [1]`·snapshot tick 50590±20·카메라 (39,53)·units 375, save000/save006/EXE SHA 전후 MATCH, `census_gate` PASS(64 PS3 present·locked_source binding·hook 9종 active), cleanup ok, 크래시 0.
  - C-1 residual: A/B/C bbox 안 lap1010 교집합 픽셀 중 창 내 residual(미후킹 쓰기)로 잡힌 수/비율 기록(A·B·C 각각).
  - C-2 writer: 각 watch hit ≥1, distinct EIP와 원본 objdump(read-only)로 소속 함수 판정 — (a) `0x466B50` 본체 → 미러 wrapper 거부 경로 가설(다음: candidate 쪽 reject 인자 x/y/w/h 기록), (b) `0x467580`/`0x467410`/`0x4676D0` → 미후킹 반투명 변형(lap953 지도 §3), (c) 기존 미러 hook 함수(`0x466070`·`0x465B30`·`0x4672E0`·TextOutA·RLE·overlay) → 해당 wrapper 거부/누락 경로, (d) 새 함수 → 주소·프롤로그·ret·호출자 기록.
  - 판정: A/B/C 중 하나 이상 writer 확정 = FEASIBLE(다음 middle이 수리 사전등록), 세 점 모두 skip 250·120에서 hit 0 = BLOCKED(창 시간·residual 결과와 함께 보고, 같은 추측 반복 금지). census 실패/크래시 = 원인 추적 후 재실행.
- 이후 후보(이번 범위 아님): save000 장면 동작(선택/드래그) 확장, hold keydown 위상 경합 INVALID+재시도, 가장자리 마우스 스크롤, save006 성분 D.

## 부록 — 처리한 `loop/ESCALATE_SOL` 원문

```
lap1010 work(Claude Code claude-sonnet-5-5) G1 H-S2 인계 (마일스톤 경계 아님, 일상 middle 검수 요청).
- 한 일: 하네스만 변경 — g1_saved_scene_probe.py에 옵트인 --fixture save000(SHA 1c703551…19da, index 1; s1_load_evidence.FIXTURES와 동일 pin)·--scene-actions none(loaded+performance-window 후 종료). 테스트 3개 RED→GREEN(192 passed), lint·typecheck PASS. fresh save000 pair 순차 2회(전부 exit 2: scene-actions none이라 non-loaded capture tag BLOCKED → pair HOLD, 예상).
- 결과: S-0 PASS(scene_state_equal·카메라 (39,53)·unit 375·tick 50596/50595), S-2 PASS(V1/V2/V2q PASS·V2s 629·scale2x PASS), S-3 PASS(p95 1/7·ticks 비 1.0000·안전 0), S-1 = 새 잔여: 고정 카메라 stale_pixels 마지막 40 중앙값 7,675·프레임≥300 교집합 20,623/20,601(save006은 0). 큰 성분 y64..168×x38..186(12,651), y427..491×x371..502(5,442), y0..25×x259..337(1,167).
- middle이 확인할 것: 위 수치를 새 스크립트로 독립 재계산, save000 로드 정체성, 다음 work H-S2c(--census-only + save000, 현재 결합 불가라 하네스 한 줄 완화 필요) 사전등록.
- 기록: docs/history/laps/20261005_lap1010_work_g1_hs2_save000_second_scene.md. 증거: …/temp/Syw2plus_patch/20261005_lap1010_work_s2/ (r1,r2,analysis_lap1010.json). 변경 uncommitted.
```

- 처리: 재계산 불일치 0·로드 정체성 확인 → 수용. H-S2c는 "한 줄 완화"가 아니라 위 3가지(결합 허용·fixture 전달·창 대기)가 필요함을 정정해 사전등록.
