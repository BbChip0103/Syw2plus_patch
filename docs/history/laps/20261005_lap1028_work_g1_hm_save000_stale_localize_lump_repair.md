# 2026-10-05 | lap1028 | G1 work H-M — 남은 save000 stale 위치 확인(M-1)·writer 귀속(M-2) → 덩어리 수리(0x467580 크기 상한 128→160)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 커밋 0.
- 가설: lap1027 사전등록 H-M. (a) 남은 save000 stale(p24..58 덩어리·바닥)은 run마다 같은 위치에 결정적으로 나타난다. (b) 각 위치의 마지막 writer는 기존 미러 패턴으로 설명된다. (c) 귀속된 writer가 단일 기존 패턴·10줄 이하면 즉시 수리한다.
- 예상 PASS / FAIL 조건: M-1 = 덤프 39개·mask 정합 불일치 0·r1∩r2 ≥80%. M-2 = 표본 3점 모두 stale present ≥1·`u` ≥80% EIP 귀속·selftest PASS·무장 fail 0. 수리 = save000 p24..58 중앙값 감소, 다른 창 불변, 안전 0, p95 비악화, save006 비회귀(38프레임 24 px·39프레임 0·신규 0).
- 변경 파일 / source fingerprint / 커밋: 모두 uncommitted.
  - 수리(제품, 1줄): `tools/inmm_stub/g1_overlay_blt.h` `G1_OVERLAY_MAX_HEIGHT 128u → 160u`(`5a076c16…`). 모든 diff 미러가 같은 상한 매크로를 쓰므로 `0x467580`·`0x467B00` 등 전 hook에 같이 적용된다.
  - 진단(opt-in, env 없으면 불변): `tools/inmm_stub/g1_layer_drift.h` 표본 3점 테이블+`g1_layer_drift_samples_parse`(`44ce4f24…`), `g1_mirror2x.c`·`g1_screen_watch.c`가 `SYW2_G1_DRIFT_SAMPLES`를 읽는다(각 번역 단위가 자기 사본을 파싱; `f463bc3e…`·`df2a2360…`), 하네스 `--drift-samples`(`7293dfbe…`).
  - 테스트: `tests/test_g1_mirror2x.py`(+파서 host gcc 테스트 1·+env/플래그 계약 테스트 1; `8096c57f…`), `tests/test_g1_overlay_blt.py`(129 거부 pin → 130·160 수락/161 거부; `f2bb902a…`). 둘 다 RED→GREEN.
- 원본 SHA / fixture: 모든 run `private_exe_sha256` = 원본 `b56986e0…8ac`. save000 `1c703551…19da`(index 1), save006 `616b7997…a064`. 활성8인 부하 증명 아님. 후보 DLL은 하네스가 매 run 빌드한 bridge(run 폴더 `bridge/`).
- 실행 명령 / 로그 / 산출물: 공유 temp `20261005_lap1028_work_hm/`(`run_m1.sh`·`run_m2.sh`·`run_m3.sh`; run 폴더 `m1_s0_r1|r2`·`m2_s0_r1|r2`·`m3_s0_r1|r2`·`m3_s6_r1|r2`; 로그 `logs/gates/lap1028_hm{1,2,3}_*`). 모든 pair exit 2 = 기존 pair HOLD(V2s raw). load 1분: M-1 0.89/2.89, M-2 2.14/5.77, M-3 save000 3.55/3.15·save006 2.75/3.74(전부 ≤8).
  - 분석 스크립트·산출물 SHA256(앞 16자): `analyze_m1.py` `8f9fd175…`→`analysis_m1.json` `baf342d6…`; `analyze_m2.py` `8e4edc19…`→`analysis_m2.json` `d636ecfa…`; `analyze_m3_s0.py` `6ff0aea1…`→`analysis_m3_s0.json` `9f3295fc…`; `analyze_m3_s6.py` `ccf85bef…`→`analysis_m3_s6.json` `d3d313cc…`.
  - 게임 `game` 사본은 runner가 정리했다(남은 것 0). prefix·manifest·output 보존. 디스크 여유 45G.

## 1. M-1 위치 찾기(제품 변경 0) — PASS

`--stale-mask 6,12,24-58/2,71,84-294/30,298-338/10,352,366-399/11`(51자). 두 run 모두 `stale_mask.bin` 18,721,248 B = 39 × (32+480,000) → **덤프 39개**(ordinal 집합 r1=r2).

| 판정 항목 | 결과 |
|---|---|
| mask 정합(mask stale 픽셀 수 = trace `stale_pixels`) | r1·r2 모두 불일치 **0**/39 |
| 재현성(r1∩r2 / 중앙값) | 덩어리 중앙값 3,206·교집합 3,206(**100%**), 바닥 408·408(**100%**), 팝업 704/726·교집합 575(80.4%) — 위치가 결정적 |

덩어리 p24..58(8-이웃 연결 성분, 존재 프레임의 ≥½에서 stale인 픽셀):
- **y300..364 × x542..608, 2,756 px**(전체의 대부분; p24..44에서 1,207→3,177→3,505→2,084, **p46부터 0**). 대표 픽셀 (583,306)은 ordinal 24..44(짝수 11프레임)만 stale.
- 보조: y375..386 × x741..754 80 px(9/18프레임), 나머지는 아래 바닥과 같은 24 px 조각.

바닥(덩어리·팝업 밖 16프레임): 24 px(6행×4열) 조각들이 **전 프레임 고정 위치**에 있다 — y515..520 × x{276,480,514,548,616,621…}, y544..549 × x{656,661,666…}. 이 중 x616..619는 save006에서 보인 성분 D와 같은 좌표다. (480,515)·(656,544)는 39덤프 전부에서 stale.

## 2. M-2 writer 귀속(진단 DLL 변경, env 게이트) — PASS

표본 3점 `--drift-samples "583,306;480,515;656,544"`(덩어리 최대 성분·바닥·바닥 2행). save000 pair 2회(`--layer-drift --screen-watch`).

| 판정 | r1 / r2 |
|---|---|
| selftest | PASS / PASS, 무장 52라운드 fail **0**, 주소 일치 match=7 |
| 표본별 stale present | 덩어리 22/22(p24..45)·바닥 403/404·바닥2 411/412 (≥1) |
| `u`(미설명 변화) 귀속 | 덩어리 5/5·바닥 1/1·바닥2 0/0 (**100%**) |
| 안전 | 0·cleanup [true,true]·source_unchanged [true,true]·scene_equal true |

writer 분류(원본 EXE objdump = SHA 일치 사본, read-only):
- **덩어리 (583,306)**: 마지막 writer `0x467692`(= `0x467580` 반투명 RLE 본문, **이미 hook한 미러**) — 그런데 같은 present의 `w` 레코드가 `0x467580` 호출 `(511,267) 130×130`을 **`reject_size`**로 기록한다(24건; 같은 프레임에 `0x467580 (490,273) 170×120 mirrored`·`0x467B00 clipped (455,506) 160×120`). `G1_OVERLAY_MAX_HEIGHT=128`이라 높이 130인 호출만 미러에서 빠졌고 `snap`은 24(배경)로 남았다. 분류 = **hook된 미러의 크기 상한 거부**. 덩어리의 `0x4662DE`·`0x466BB3`·`0x467692` 순서는 H-B2/B3 때와 같다.
- **바닥 (480,515)·(656,544)**: present마다 wined3d `0x745E99CF`(외부 모듈, `snap` 값 241/242 기록) → `0x46659F`·`0x46651E`(`0x466540`/`0x4664D0` 팔레트·RLE 복사, guard 1) → **마지막 `0x465F01`(값 68, guard 0)**. `scr`=68·`snap`=241/242로 현재 미러는 마지막 쓰기를 따라가지 못한다. `0x465F01`은 함수 `0x465E80`(thiscall 5인자 x0,y0,x1,y1,color·`ret 0x14`·leaf, 좌표 범위 검사 뒤 안쪽 루프 `mov [eax+ebp-1], dl`; 호출처 스택 `0x49B195`·`0x49AF08`)의 안쪽 루프다. `0x465B30`(테두리)·`0x466070`(채움)과 별개의 함수이며 hook 목록에 없다 → 분류 = **미후킹 EXE 함수**.

**판정(바닥): FEASIBLE.** `0x465E80`은 H-F2(`0x465B30` 테두리)와 같은 모양(5인자 `ret 0x14` leaf, 사각형 클립 교집합, 단색 쓰기)이라 같은 `mirror_rect_border` 계열 wrapper로 diff 미러할 수 있다. 다음 work에서 구현한다(아래 §4). 덩어리는 아래 §3에서 이번 lap에 수리했다.

## 3. 덩어리 수리(단일 기존 패턴, 1줄) — save000 pair 2회 + save006 env-off pair 2회

`G1_OVERLAY_MAX_HEIGHT 128→160`. 근거: 거부된 호출이 130×130(2 px 초과), 같은 상한 매크로를 쓰는 모든 hook이 같은 규칙을 공유하고 before 버퍼는 `G1_OVERLAY_MAX_*`로 크기가 따라간다(코드 변경 없음). 160은 130에 여유를 둔 값이며 다른 호출의 크기 분포는 측정하지 않았다.

save000(r1 / r2, 기준 = lap1027 H-A v2 r1 / M-1 r1):

| 항목 | 기준 | 수리 후 |
|---|---|---|
| p24..58 stale 중앙값 | 3,444 | **216 / 216**(덩어리 소멸, 바닥 수준) |
| `blend_467580_reject_size` / `blend_467B00_reject_size` | 28 / 56 | **0 / 0** (`0x467580` 호출 3,589 = mirrored 3,589) |
| 다른 창 p0..83 / p84..297 / p298..338 / p339..365 / 마지막 40 | 656 / 316 / 858 / 591 / 414.5 | 216 / 316 / 858·727 / 591 / 414.5 (p0..83도 656→216은 p24..58이 이 창에 있어서 같이 줄어든 것) |
| 표본 A/B/C stale present | 0/0/0 | 0/0/0, `drift_unattributed` [5,1,1] 동일 |
| p95 | 7 | **7 / 7**(원본 0 / 1) |
| 안전·cleanup·source_unchanged·scene_equal | 0·true·true·true | 0·[true,true]·[true,true]·true |
| rect_blt / heal | inv 5 = mirrored 5·heal 44 | 같음(inv 5·mirrored 5·heal 44/559,476) |

save006(env-off, `--stale-mask 6-12,30-34,300-301,585-620,880`, 기준 lap1026 v2 r1·r3):
- r1∩r2 38프레임(≥300, 880 제외) **24 px**(y515..520 × x616..619 = 성분 D), 39프레임(880 포함) **0**, 기준 대비 신규 **0**·제거 0. p95 7/7(max 17/16), cov p50 99.2975%, 안전 0, cleanup·source_unchanged true.
- save006에는 `0x467580` 호출 16개가 크기 거부로 남는다(160 초과 폭/높이로 추정, 수치만 기록; stale 영향 없음). `0x467B00` reject_size는 0.
- 두 run 모두 pair `HOLD`(V2s raw production FAIL, 기존 사용자 판단 큐). V2/V2q/Scale2x/input_effect/minimap/loaded 게이트 PASS.

## 4. 남은 작업과 다음 한 가지

- save000 남은 stale 약 52%는 바닥 24 px 조각 군(약 17개)이다 → writer는 **미후킹 `0x465E80`**(§2). 다음 work **H-N**: `0x465E80`을 `0x465B30`과 같은 diff 미러 wrapper로 hook(old bytes는 SHA 일치 EXE `0x465E80`에서 `8B 41 10 53 55 8B 6C 24 0C 56 3B E8 57` — 명령 경계가 맞는 5바이트 `8B 41 10 53 55`(mov eax,[ecx+10]; push ebx; push ebp)가 steal 후보; 호출처 스택 `0x49B195`·`0x49AF08` 확인), save000 pair 2회 + save006 env-off pair 2회로 바닥 약 400 px 감소를 검증한다. census는 같은 주소를 hook하므로 `--census-only`로만 쓴다.
- 바닥 중 wined3d(`0x745E99CF`)가 snap 값 241/242를 쓰는 부분은 `0x465E80` 미러가 마지막 쓰기를 따라가면 같이 해소되는지 H-N에서 확인한다. 해소되지 않으면 표본 두 점을 다시 귀속한다.
- 팝업 p298..338 858/727과 save006 성분 D(24 px, 이번에 같은 좌표가 save000 바닥에도 있음)는 H-N 뒤 재분해한다.

## 회귀 / 남은 위험 / 독립 검수
- 상한 128→160은 전 hook의 수락 범위를 넓힌다. 이번 pair들에서 p95·안전·save006은 불변이지만 save000/save006 밖 장면(큰 팝업 연속)은 미측정이다. before 버퍼 10개 × 51,200 B, scratch +50 KB 정도의 정적 메모리 증가.
- 진단 env 파서는 번역 단위마다 사본을 쓴다(헤더 정적 테이블). env 없으면 기본 표본 A/B/C와 동작이 바이트 수준에서 같다(host 테스트가 기본값 고정).
- 사용자 승인 아님. 독립 검수 대기(middle). G6/G7 사용자 합격(APPROVALS lap989) 대기는 비차단.
- 다음 한 가지: middle 독립 검수 후 work H-N(`0x465E80` diff 미러).
