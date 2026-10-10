# 2026-10-08 | lap 1188 | G1 work — H-HDB0: 효과(반투명) ① `0x4672E0`(HUD 로고 50% 혼합) HD 키 경로

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1187 middle 사전등록 §5(`20261008_lap1187_middle_g1_hdu1_review_hdb0_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 65 GB, 끝 약 58 GB.
- 가설: 0x4672E0은 목적지 의존 50% 평균 RLE라 (a) 스트림을 1x로 직접 디코드해 원본 출력과 같은 식으로 자기 검사하고, (b) 기존 identity 키 장부(`h<digest>_<w>x<h>.idx8` 팩)에 no-aux 키로 얹어, (c) HD 목적지 부분픽셀과 팩 프레임을 같은 식으로 섞으면 diff 미러(Scale2x of 혼합 결과) 대신 교체한 HD 그림이 반투명으로 화면에 들어간다.
- 예상 PASS/FAIL: 사전등록 §5 측정식(B-0 변이 RED·B-1 디코더 일치+digest 귀속·B-3 keyed ≥95%·자기 검사 불일치 0·안전 0·p95 ≤ 끔+2·로고 사각형 캡처가 끔과 다름·로고 밖 stale ≤ 끔 규모·pair PASS).

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_blend_key.h` (신규) | 순수 함수 4개: `g1_blend_decode_rle`(행은 열이 폭에 닿으면 끝, `FE n` = n열 건너뛰기, n=0 허용, 길이 한도 초과 시 실패) · `g1_blend_lut_offset`/`g1_blend_pixel`(`((c0<<6)+c1)<<6+c2`, 채널 = (d>>1)+(s>>1), 오프셋 ≥ 0x40000이면 거부) · `g1_blend_selfcheck`(원본 1x 출력 = 식 결과, 마스크 밖 불변) · `g1_blend_apply_hd`(마스크∧covered 인 픽셀의 2×2를 HD 목적지 사본과 팩 프레임으로 혼합, 팩 키 부분픽셀이 하나라도 있으면 그 픽셀은 건너뜀) |
| `tools/inmm_stub/g1_hd_asset.c`·`.h` | `SYW2_G1_HD_PACK_BLEND`(0 = 끔), `g1_hd_asset_blend_key_path()`, `g1_hd_asset_current_pack_frame()`(현재 키의 팩 hit 프레임, 아니면 NULL), 자기 카운터 `pack_blend_hits/misses/rejects`(aux 없는 기존 팩 읽기 경로 그대로 사용) |
| `tools/inmm_stub/g1_mirror2x.c`·`.h` | `mirror_blend_rle`: 키 시도 조건이면 원본 호출 **전에** covered 사본·HD 목적지 사본(2w×2h)을 뜨고, 원본 호출 뒤 **기존 diff 미러를 그대로 실행한 다음** `blend_rle_key_apply`(디코드 → 자기 검사 → `g1_hd_asset_begin`/`bind_identity_frame` → 팩 프레임 → `g1_blend_apply_hd`)로 덮어쓴다. 어떤 단계든 실패하면 diff 미러의 Scale2x 블록이 그대로 남는다(`key_fallbacks`). 카운터 `keyed_calls`·`keyed_pixels`·`key_fallbacks`·`selfcheck_mismatches`·`selfcheck_pixels` |
| `tools/inmm_stub/direct_draw_trace.c` | 트레이스 `blend_4672E0_keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels`·`hd_pack_blend_hits/misses/rejects` |
| `tools/g1_hd_convert.py` | 새 하위 명령 `logo`: 프레임 수 0인 단일 RLE `.spr`(`fnt/imjin2plus.spr`)를 엔진과 같은 행 규칙으로 읽고(스트림 정확히 소비 검사) `h<digest8>_<w>x<h>.idx8`(2w×2h, 키 0xFE, 실루엣 강제) 작성. 기존 `pack`은 프레임 수 0 파일을 `unsupported`로 넘기므로 로고 이름이 `digest_index`에 없었다 |
| `tests/test_g1_blend_key.py` (신규) | 호스트 컴파일 헤더 테스트 5·정적 계약 4(B-0 포함) |
| `tests/test_g1_hd_pack.py` | 로더 시나리오 `blend_hit/miss/reject/off` 3테스트 |
| `tests/test_g1_hd_convert.py` | `logo` 테스트 2개 |

파일 SHA256 앞 16자(최종): `g1_blend_key.h dc58c1d5d1ba5fc5`·`g1_hd_asset.c ba4d9b17373bd64a`·`.h a6dbb05c342cc89f`·`g1_mirror2x.c 8e57fd363008a2a2`·`.h 7cbfaff97e9526b1`·`direct_draw_trace.c af5c3391e74efbaa`·`tools/g1_hd_convert.py 388d21cb068f3b97`·`tests/test_g1_blend_key.py cd07bbdeb6c39ee6`·`test_g1_hd_pack.py 5e791ab616d42d63`·`test_g1_hd_convert.py 4c06fb23ee2c8815`.

## B-1 정적 확정 (원본 EXE 읽기 전용 디스어셈블, SHA `b56986e0…` 전·후 MATCH)

- `0x4672E0..0x467406` 재디스어셈블: 인자 = x,y,w,h(스택 word `movsx`)·rle. 행 루프는 `col < w` 동안 토큰을 읽는다: `0xFE` → `col += next byte`(0이면 아무것도 안 함), 그 외 → 목적지 `[buffer + y*pitch + x + col]`에 `inverse[((dst c0>>1 + src c0>>1)<<6 + (c1 합))<<6 + (c2 합)]`. 행 끝 표지·스트림 길이 필드 없음 → 사전등록의 "스트림 길이"는 디코드로만 정해진다. 팔레트 = `renderer+0x419A0` RGB 3바이트, 역 LUT = `renderer+0x19A0`(lap953/954와 일치).
- **로고 귀속(digest):** 실게임 키 로그 `{"writer":"0x004672E0","w":100,"h":64,"digest":"3475a863","pal":"cecc4681"}` = **`fnt/imjin2plus.spr`** 의 `0xBF4`(스트림 시작)부터 128바이트 FNV-1a `3475a863`(직접 재계산 일치). 헤더 프레임 수 = 0(그래서 `g1_hd_extract`/`pack`이 `unsupported`로 건너뛰었다), 스트림 2,958바이트를 행 규칙으로 디코드하면 **정확히 2,958바이트를 소비·불투명 2,110픽셀**(`FE 00` 없음). 실게임 자기 검사 평균 불투명 수 = 6,287,800/2,980 = 2,110.0과 일치.
- **B-1 디코더 일치(실게임):** B0 run(팩 없음, 자기 검사만 켠 로고 호출 2,980회)·K1·K2·M1·PB에서 **자기 검사 불일치 0**(원본 실행 결과 = 식 결과, 마스크 밖 불변, 합 25,000,000+ 픽셀). 디코더·식이 원본과 같다는 근거는 정적 디스어셈블 + 이 실측이다.

## 측정 (산출물 공유 temp `20261008_lap1188_work_hdb0/`, 하네스 `--new-game-path --new-game-start --new-game-act --new-game-play` PS3 약 150 s, 기본 한도)

팩: B0 = 빈 팩(미스) · K1·K2·O1 = `pack_logo`(로고 bicubic stand-in 1장, `logo_pack_report.json` sha `c97a29f4…`) · M1 = `pack_marker`(같은 그림의 R/B 채널을 맞바꿈, sha `e61f2c78…`, 경로 확인용). 팩 pal 디렉터리 `cecc4681`.

| run | 구성 | PS3 present·s | 로고 호출 | keyed | 폴백 | 자기 검사 불일치 / 픽셀 | p95 | PS3 최대 stale(초:px) | candidate·baseline |
|---|---|---|---|---|---|---|---|---|---|
| B0 | 빈 팩, 키 시도 | 2,980·149 | 2,980 | 0 | 2,980(팩 miss 1) | 0 / 6,287,800 | 6 | 없음 | PASS |
| K1 | `pack_logo` 켬 | 3,053·153 | 3,053 | **3,053** | 0 | 0 / 6,441,830 | 6 | 80.0:90 | PASS |
| K2 | `pack_logo` 켬 | 2,967·149 | 2,967 | **2,967** | 0 | 0 / 6,260,370 | 7 | 없음 | PASS |
| O1 | `pack_logo`, `SYW2_G1_HD_PACK_BLEND=0` | 2,982·149 | 2,982 | 0(시도 0) | 0 | — | 6 | 77.5:283 | PASS |
| M1 | `pack_marker` 켬 | 2,981·149 | 2,981 | **2,981** | 0 | 0 / 6,289,910 | 6 | 없음 | PASS |
| PB | save006 pair, `pack_logo` | — | 키 로그에 로고 키 없음(저장 장면은 로고를 그리지 않음) | — | — | — | — | — | status **PASS**, scene_state_equal true, V2/V2s/V2q/Scale2x/input_effect/minimap PASS |

- **키 경로 처리율:** 켬 3 run(K1·K2·M1) 합 로고 호출 9,001 중 keyed **9,001(100%, ≥95%)**, 폴백 0, 자기 검사 불일치 0, `keyed_pixels = selfcheck_pixels`(불투명 2,110×호출, covered 게이트로 빠진 픽셀 0). 팩 카운터 `hd_pack_blend_hits 1·misses 0·rejects 0`(키 1개), 끔 run 0/0/0. `identity_invalid_sources`·`identity_evictions`·`identity_key_mismatches`·`scale2x_palette_violations` 0, fallback 0.
- **p95 ≤ 끔+2:** 켬 6·7·6, 끔(O1) 6, 키 시도만 켠 B0 6 → 충족. 안전/하네스: 5 run 모두 `new_game_start`·`play`·`act`·`scale2x_validator` PASS(`mirror_validator`는 이 하네스의 전 run 공통 BLOCKED 값, 변경 전후 같음). 트레이스에서 dropped·hresult·violation·mismatch·invalid 계열 필드 비영 0(K1·K2 점검).
- **stale:** 켬 K1 80.0 s 90 px(단발)·K2 0·M1 0, 끔 O1 77.5 s 283 px(단발), 키 시도만 B0 0. 켬 run 최대 stale(90)은 끔 O1(283) 이하 → 측정식(같은 시각 끔 규모 이하) 충족. stale 위치가 로고 사각형 안인지 밖인지는 계측하지 않았다(UNKNOWN). 80 s 전후의 단발은 lap1187이 확정한 "클립 반전 가장자리 등장" 기존 현상(U2 76.6:90·E2 76.7:90)과 같은 크기·시각대이며 이 경로 고유 증거는 없다.
- **로고 사각형 캡처가 끔과 다름:** 같은 장면을 쓴 run끼리(B0·K1·K2: 같은 시작 맵, 아래 주의) 로고 사각형(1400..1599×754..881, 25,600 px)에서 B0(diff 미러) vs K1·K2 = **5,052~5,053 px 다름**(4개 캡처 모두), K1 vs K2 = **0 px**(결정적 재현). M1(R/B 맞바꾼 팩) 캡처에서 로고의 붉은 뱀 모양이 **푸른색**으로 나온다(`logo_cmp_marker.png` 열람: 왼쪽 K1 붉음 · 오른쪽 M1 푸름, 글자 흰색 부분은 같다) → 교체한 HD 그림이 반투명으로 화면에 들어가는 것을 눈으로 확인.
- **주의(하네스 비결정):** 새 게임 시작 맵이 run마다 두 갈래다(키 수 ~750: B0·K1·K2, ~1,340: O1·M1). 그래서 O1·M1과의 픽셀 비교는 장면 차이가 섞여 판정에 쓰지 않았고(O1 vs 모든 run 16.7k~25.6k px 다름), 같은 갈래인 B0·K1·K2만 로고 사각형 비교에 썼다. 끔 대조 O1은 stale·p95·keyed 0 용도다.
- **원본 보호:** EXE SHA `b56986e0…` 전·후 MATCH(`orig_sha_before.txt`·종료 전 재확인). 새 게임 사본 삭제(하네스가 run 종료 때 삭제, `local/runtime/lap1188_hdb0_*` 6개에 prefix 약 600 MB씩 보존).

## 변이·테스트

- B-0: `mirror_flip_clip` keyed 분기의 `active = FALSE;` 제거(lap1187 변이 v3) → 새 `test_clip_flip_wrapper_skips_the_diff_mirror_after_a_keyed_draw` **RED**, 현재 GREEN.
- 새 변이 8종(건너뛰기 +1·covered 게이트 제거·`after` 비교 제거·목적지를 팩에서 읽음·자기 검사 비활성·시도 무조건 켬·env 무시·hit 미집계) 모두 RED. 처음 하나(자기 검사 비활성)가 정적 테스트 부분문자열 매치로 생존했다가 `if (!g1_blend_selfcheck(` 단언으로 닫았다.
- `make lint`·`make typecheck` PASS. 호스트 테스트: 새 `test_g1_blend_key.py` 9 + `test_g1_hd_pack.py` blend 3 + `test_g1_hd_convert.py` logo 2 PASS.

## 판정

- **B-0 PASS · B-1 PASS**(실루엣 2,110·스트림 2,958 정확 소비·digest `3475a863` = `fnt/imjin2plus.spr`, 실게임 자기 검사 불일치 0) · **B-2 PASS(기술)** · **B-3 PASS(partial, 기술·격리)**: keyed 100%(≥95%), 자기 검사 불일치 0, 안전 0, p95 ≤ 끔+2, 로고 캡처가 끔과 다름(B0 대비 5,052 px, 표식 팩으로 색 반영 육안 확인), 로고 밖 stale ≤ 끔, pair PASS.
- 전체 `PASS(partial, 기술·격리)`. 기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

## 한계·공개

1. 팩 그림은 bicubic stand-in(경로 검증용)이며 실제 업스케일 화질 평가가 아니다. 표식 팩 M1은 색만 바꾼 확인용이다.
2. 키 시도 비용: 호출마다 1x 디코드+자기 검사(약 6,400 px)·HD 사본 25 KB. p95는 6~7이지만 이 장면(로고 1개)만 측정했다.
3. 목적지 HD 부분픽셀은 diff 미러가 만든 현재 `g_mirror`(그 전 writer가 그린 HD)를 쓴다. 로고 밑 HD 지형이 팩 그림이거나 Scale2x이거나 섞인 경우도 같은 식을 쓰므로 일관되지만, 목적지가 covered가 아닌 픽셀은 diff 미러 결과를 그대로 둔다(이번 측정 9,001호출에서 해당 0).
4. PB save006 pair는 로고를 그리지 않아 이 경로의 비회귀 증거는 "다른 경로가 안 깨짐"까지다.
5. 하네스 맵 갈래 비결정(위) — 이번 판정에 영향 없으나 끔 대조 run의 용도를 제한했다. 같은 갈래 끔 대조는 B0(diff 미러)로 대신했다.
6. 정적 테스트 일부는 문자열 계약이다(변이 RED 확인).
7. `0x467580`·`0x467B00`·`0x4685C0`·`0x467FD0` 반투명 writer는 미착수(다음 순서).

## 다음 행동

middle(Opus)이 H-HDB0를 검수해 `PASS(partial, 기술·격리)`를 수용하고, 반투명 다음 writer(`0x467580` → `0x467B00` → `0x4685C0` → `0x467FD0`, 변화량 순)를 사전등록한다. 사용자 G1 시험 결과가 오면 최우선.
