# 2026-10-08 | lap1173 | G1 work — H-HDF0 ⑤ 전체 화면 raw 그림(타이틀) 경로 귀속 → HD 팩 1장 적용

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). 커밋 0.
- 입력: lap1172 middle 사전등록 §6(`20261008_lap1172_middle_g1_hds1_review_hdf0_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 5.8 GB(<20 GB, 이 회차 옛 사본 없음 → 규칙대로 run 1회분 ≥5 GB로 시작, 실행 3회: F1·OFF1·G1; 종료 4.2 GB, 각 run prefix 약 1.3 GB는 보존, game 사본은 하네스가 실행 직후 삭제 `game_removed` true 6/6; 다른 회차 산출물·원본 삭제 0). **디스크가 더 줄어 다음 run은 4.2 GB로 시작 불가(≥5 GB 규칙) — 다음 work 전에 root가 여유를 확보해야 한다.**
- 가설: 800×600 raw `.spr` 전체 화면 그림은 한 지점(소프트웨어 block copy `0x466280`, 훅 `mirror_cache_copy`)으로 화면에 오르고, 그 1x 블록의 전 바이트 FNV-1a(이미 계산되는 `menu_copy_hash`)가 원본 파일 프레임과 정확히 대응한다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…a8ac` 전후 MATCH(`orig_sha_before/after.txt`). 환경: 격리 Wine·Xvfb 1600×1200 `tools/g1_saved_scene_probe.py --hd-source scale2x`(기본 save006 pair 2 run F1·OFF1, NG5 `--new-game-path --new-game-start --new-game-act` 1 run G1). 활성 8 player records(부하 증명 아님). 산출물 공유 temp `20261008_lap1173_work_hdf0/`.

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_hd_pack.h` | 이름 포맷을 `g1_hd_pack_format_name(prefix,…)`로 분리(`g1_hd_pack_name`=`h`, 동작 불변), 전체 화면용 `g1_hd_pack_fullscreen_name` = `f<digest8>_<w>x<h>.idx8` |
| `tools/inmm_stub/g1_hd_asset.c/.h` | `g1_hd_asset_fullscreen_frame(hash,w,h)`: 팩 env 있고 scale2x이고 `SYW2_G1_HD_PACK_FULLSCREEN≠0`일 때 `<pack>\f<hash8>_<w>x<h>.idx8`(크기 정확히 2w×2h, 키 색 0xFE가 한 바이트라도 있으면 reject) 읽기. 마지막 hit 프레임 1개 캐시(타이틀 block copy는 매 present), miss·reject 이름 8개까지 기억해 디스크 재접근 없음. 카운터 hits/misses/rejects/loads(호출당 계수) |
| `tools/inmm_stub/g1_mirror2x.c` | `transfer_block_copy_to_screen`의 800×600 분기: 기존 hash 계산·Scale2x 복사 **뒤** scale2x일 때 팩 프레임이 있으면 `g_mirror` 1600×1200을 덮어쓴다(coverage·expected는 기존 Scale2x 경로 그대로) |
| `tools/inmm_stub/direct_draw_trace.c` | present 레코드에 `hd_pack_fullscreen_hits/misses/rejects/loads` 4필드(`mirror_pack_details` 760→1000) |
| `tools/g1_hd_convert.py` | `fullscreen` 명령: 파일 크기 == 헤더+fw×fh×프레임(진짜 raw)인 `.spr`를 받아 `f<FNV-1a 전 바이트>` 이름의 2w×2h `.idx8` 작성. 업스케일러 RGB(`--rgb`) 또는 바이큐빅 stand-in → 팔레트 최근접(키 254 제외) |
| `tests/test_g1_hd_pack.py`·`tests/test_g1_hd_convert.py` | 호스트 테스트 +7(이름·hit 캐시·miss 유지·miss/reject(키·크기)·끔 env·trace 필드·미러 배선) +4(이름=엔진 hash·RGB 양자화·키 제외·거부). 변이 확인 3개: 로더 키 검사 제거 → FAIL, 캐시 제거 → FAIL, 도구 후보에 254 포함 → FAIL(처음엔 테스트가 약해 통과해 RGB 테스트를 강화한 뒤 재확인) |

## 측정

- **F-0(오프라인, `f0.json`·`f1_fullhash.json`):** raw `.spr` ≥640×480(Online 지도 제외) 84프레임·고유 이름 21개, 선두 128 B 이름 충돌 10개(73프레임: 브리핑 3 세트 각 12장·select_stage 25장 등은 위쪽이 같은 검정). 128 B 규칙으로 유일한 전면 그림은 11장뿐이므로 **전체 화면 그림은 128 B 키 대신 전 바이트 hash 키를 쓴다**(F-2 설계 근거). 전 바이트 hash는 고유 80/84.
- **F-1(귀속, 판정 `FEASIBLE`):** PS9 타이틀 그림 = `0x466280` block copy(lap949 census: PS9 메뉴 93.97%·훅 `mirror_cache_copy`)의 800×600 packed 원본이고, 그 전 바이트 FNV-1a 값 **1777000796**(lap955 이래 모든 run에서 불변)이 `yfnt/title.spr` 프레임 0과 **정확히 일치**(독립 재계산, 480,000 바이트·0xFE 0개). 팔레트 `pal/title_plus.PAL`×4 렌더가 PS9 캡처 `menu_after.png`와 90.08% 화소 완전 일치(나머지 = 버튼 등 다른 writer, 인덱스→색 일관성 94%). EXE 문자열 `yfnt\title.spr`·`pal\title_plus.pal` 존재. **정정:** lap1172 §5가 든 `fnt/launchscreen_plus.spr`는 타이틀이 아니라 로딩 화면("여럿이 하기를 설정중입니다")이다. `yfnt/title.spr`는 추출기가 sheet 레코드 0이라 `rle`(fallback)로 분류했지만 파일 크기 = 0xBF4+480,000 정확, 0xFE 없음 → 실제 raw. 같은 방식 hash 대응: PS5 hash 269350933 = `yfnt/titlelobby.spr`, PS7 hash 3908910012 = `yfnt/titleprotocol.spr`(후속 후보, 이번 비목표).
- **팩:** `g1_hd_convert.py fullscreen --pal title_plus.PAL yfnt/title.spr` → `f69eae15c_800x600.idx8`(1,920,000 B, sha256 `3da00c8c…c190b`, 바이큐빅 stand-in), 이름 hex = 1777000796.
- **F-2 run(전부 exit 0, `source_unchanged`·`game_removed` true, pair `status` PASS, scale2x_gate PASS, `hd_mask_outside_diff` 0):**

| run | 팩 | PS9 present | fullscreen hits/loads/misses/rejects (PS9 마지막) | menu_copy calls·hash 변화 | PS9 HD min | PS9 p95 | 비고 |
|---|---|---|---|---|---|---|---|
| F1 | `pack_f`(f 파일만) | 72 | **72/1/0/0** | 72·0 | 100 | 14 | PS3 881 present HD min 99.261·p95 7(hits 불변 72) |
| OFF1 | 같은 팩 + `SYW2_G1_HD_PACK_FULLSCREEN=0` | 68 | 0/0/0/0 | 68·0 | 100 | 13 | 끔 스위치 입증(카운터 전부 0), PS3 869 present min 99.287·p95 7 |
| G1 | `pack_cf` = lap1169 `pack_c` 하드링크 + f 파일, NG5 | 70 | **70/1/0/0** | 70·0 | 100 | 14 | PS3 1536 present HD min **99.948**·p95 7·안전 합 0·fallback 0·dropped 0·scale2x PASS·`mirror_validator` BLOCKED(lap1171 S2·OFF1 동일) |

  - hits = menu_copy 호출 수(PS9에서 매 present). G1에서 PS7(159 present)·PS5(733 present)의 800×600 block copy는 f… 파일이 없어 miss 합 892(= 159+733, 호출당 계수, 디스크 읽기 아님), reject 0.
  - **p95:** 사전등록 "PS9 p95 ≤ 9"는 이 하네스 PS9에서 팩 없이도 13~14 ms다(lap996 r1 13·lap1024 s0_r2 14, OFF1 13) → 판별력 없는 기준이라 켬/끔 대조로 대체: 켬 14 vs 끔 13(72 present의 p95, 표본 차). PS3 p95 7 불변.
  - **크롭(공유 temp `crops/F1_*`·`OFF1_*`·`G1_*`, 위 = baseline 1x 최근접 2배, 아래 = 후보):** `F1_logo`(로고 곡선·획이 계단 없이 부드러움, 구도·글자 위치 동일)·`F1_face`(얼굴·투구 질감 부드럽고 윤곽·밝기 동일)·`F1_buttons`(버튼 8개 색·글자 baseline과 동일, 깨끗). 2×2 블록 평균 대비 baseline 평균 절대 차: 위쪽 그림 F1 2.51(켬)·OFF1 0.78(Scale2x)·버튼 영역 F1 0.38. 비균일 2×2 블록 비율 F1 0.424 vs OFF1 0.224(HD 디테일 증가).
- **결함 발견(별개, 이번 변경 무관, 판정 영향 FAIL로 공개): 합본 팩 G1의 PS9 버튼 변색.** G1 `menu.png` 버튼 영역(`G1_buttons.png`)이 빨강·노랑 잡음으로 깨져 baseline 대비 평균 차 **11.05**(25.4% 화소 >16)로 F1 0.38보다 크다. G1 PS9에서 `hd_pack_hits` 3→6 = `yfnt/TitelMainButton_plus.Spr` 프레임 3개(100×36)가 lap1169 `pack_c`에서 hit. 원인: 그 팩 프레임은 `imjin2.pal`로 양자화됐는데 타이틀 화면의 실제 팔레트는 `title_plus.PAL`이라 같은 인덱스가 다른 색(독립 계산: HD 블록 평균 − 1x 불투명 평균 절대 차 imjin2 기준 4.76/5.08/5.89 vs title_plus 기준 19.46/21.39/15.13). 즉 **HD 팩 프레임은 화면 팔레트마다 따로 만들어야 한다**(PS3 NG5는 imjin2 화면이라 lap1169·1171 합격은 유효). 이 회차는 수리하지 않았다(범위 밖, 한 바퀴 한 가지). backlog H-HDPAL.

## 판정

**H-HDF0 `PASS(partial, 기술·격리)`** — F-0·F-1 `FEASIBLE`(귀속 확정·hash 정확 일치), F-2 켬 2 run(F1·G1) hits=호출 수·loads 1·misses/rejects 0·안전 0·PS9 HD 100, 끔 대조 입증, F1 크롭에서 구도 동일·질감만 부드러움, G1 PS3 NG5 비회귀(HD min 99.948·안전 0). **단서/미충족:** (1) 합본 팩 PS9 버튼 변색(위, H-HDPAL, 사용자 전달·기본 켬 전 필수); (2) PS9 p95 기준 판별력 없음(위); (3) 한 장(타이틀)만, 화질 평가 아님(바이큐빅 stand-in), 기본 켬·사용자 전달 아님; (4) PS5/PS7 전면 그림(`titlelobby`·`titleprotocol`)은 같은 방식으로 후속 가능, 브리핑 36장은 전 바이트 hash로 33개 고유(c0110=c0111·j0110=j0111·k0110=k0111 동일 그림 쌍만 중복, 같은 그림이라 충돌 아님)라 같은 방식이 가능하지만 미관측(브리핑은 `0x4D4620` 합성 경로, lap1148); (5) 디스크 4.2 GB로 다음 run 불가.

## 검사

- `make lint`·`make typecheck` PASS(구현 후). 목표 테스트 `test_g1_hd_pack.py`·`test_g1_hd_convert.py`·`test_g1_mirror2x.py`·`test_g1_panel_layer.py`·`test_g1_census.py` 135 PASS. 전체 `make check` 결과는 STATUS 검증 줄에 보강한다.
- 변경 파일 SHA256(앞 16자): `g1_hd_asset.c` `fdeb20ff9fa19756`·`g1_hd_asset.h` `9695ff2289d19f03`·`g1_hd_pack.h` `f30559b696bbae1d`·`g1_mirror2x.c` `d9b67b5fb495c66a`·`direct_draw_trace.c` `6c68b3054e624146`·`tools/g1_hd_convert.py` `d84706e1a8143a53`·`tests/test_g1_hd_pack.py` `2aaf0bd83167024b`·`tests/test_g1_hd_convert.py` `185bb07097fc2cf3`.
- 측정 스크립트(공유 temp `20261008_lap1173_work_hdf0/scripts/`): `f0_digest.py`·`f1_fullhash.py`·`f1_compare_png.py`·`f1_consistency.py`·`f1_pal.py`·`render.py`·`metrics_f.py`·`metrics_ng5.py`·`crops_f.py`·`run.sh`.

## 다음 행동

middle(Opus) 독립 검수 → (a) 새 스크립트로 hash 1777000796 = `yfnt/title.spr` 일치·팩 이름·trace 카운터·PS9 HD/p95·크롭 재계산, (b) `transfer_block_copy_to_screen` 덮어쓰기 코드와 로더(키 검사·캐시·miss 슬롯 8 한계), (c) 합본 팩 PS9 버튼 변색 귀속(imjin2 vs title_plus)과 H-HDPAL 사전등록, (d) 다음 work 후보: H-HDPAL(화면 팔레트별 팩 수리)·PS5/PS7 전면 그림 같은 방식·브리핑. 디스크 여유가 5 GB 미만이면 다음 run work는 시작하지 말고 root 보고. 사용자 G1 시험 결과가 오면 최우선.
