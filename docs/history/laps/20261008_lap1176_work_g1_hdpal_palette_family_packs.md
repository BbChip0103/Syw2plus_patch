# 2026-10-08 | lap1176 | G1 work — H-HDPAL: HD 팩을 화면 팔레트별 디렉터리로 분리

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). middle 검수는 `loop/ESCALATE_SOL`로 요청한다(자기 승인 없음).
- 입력: lap1174 middle §6 사전등록. lap1175 work(강제 종료, 기록 없음)의 소스 잔여물을 인계: `g1_hd_pack.h`(`g1_hd_pack_format_pal`)·`g1_hd_asset.c`(`pack_file_path`·`<pack>\<pal8>\` 조회·fullscreen pal 캐시)·`g1_mirror2x.c`(패널 팩 pal8 경로)·`direct_draw_trace.c`·`tools/g1_hd_convert.py`(`--pal` 필수·`palette_pal8`)·호스트 테스트. 이 회차가 코드 전체를 검수·재실행했고(호스트 111 passed 확인 후 시작) lap1175 run_P1(중단 run)은 근거로 쓰지 않았다.
- 가설: 그림이 표시되는 화면 팔레트를 엔진이 읽어 `<pack>\<pal8>\<이름>`으로 조회하면, 다른 팔레트 화면에서는 팩이 miss → Scale2x로 떨어져 변색이 사라지고 인게임 HD는 유지된다.
- 예상 PASS(사전등록): 팔레트 소스 1개 확정·PS9/PS5/PS3 pal = title_plus/titlelobby_plus/imjin2 / PS9 버튼 2×2 평균 차 ≤1.0(G1 11.05) / PS9 fullscreen hits = menu 호출 수·rejects 0 / PS3 HD min ≥99.9·tinted·음영·지형 matched hit 비율 lap1171 수준 / 안전 7종·fallback·dropped 0.

## 1. 변경 파일 / source fingerprint (전부 uncommitted)

| 파일 | 내용 | SHA256 앞 16자 |
|---|---|---|
| `tools/inmm_stub/g1_hd_asset.c` | `g1_hd_asset_palette_digest`: 화면 팔레트 = renderer `+0x15A0` PALETTEENTRY 배열. **in-game 계열 규칙**(아래 §3)·키 로그 `pal_change` 진단 줄·`g_pal_logged` | `2253b963bcbfec56` |
| `tools/inmm_stub/g1_hd_asset.h` | `g1_hd_asset_palette_family()`·주석 | `467c7a9f721bf91d` |
| `tools/inmm_stub/direct_draw_trace.c` | trace `hd_pal_family` 필드 추가 | `eb760613a213ab08` |
| `tests/test_g1_hd_pack.py` | 호스트 테스트 +4(family 3·key log pal_change 1), 기존 pal 테스트를 "10개 항목이 start보다 밝은 화면"으로 정정 | `ca0d56d3263c502b` |
| (lap1175 인계, 변경 없음 확인) `g1_hd_pack.h`·`g1_mirror2x.c`·`tools/g1_hd_convert.py`·`tests/test_g1_hd_convert.py` | `<pal8>` 경로·`--pal` 필수 | `fb13d7fb…`·`33e7328a…`·`5f912710…`·`d084e99a…` |

후보 DLL `tools/inmm_stub/_inmm.dll` SHA256 `8d0549c2b05d43bc617ce8efdf2efc5ac402b5e13f482d4d4084c81bb613879d`(최종 소스, 아래 H1 run이 이 DLL). 앞 DLL `02c4aef7…`(G1·F0·F1·F2 run)은 키 로그 중복 줄(`g_pal_logged`)만 다르다.

## 2. 환경 / fixture / 원본

원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전(`orig_sha_before.txt`)·후 MATCH. 격리 Wine·Xvfb 1600×1200, `tools/g1_saved_scene_probe.py --hd-source scale2x`. NG5 = `--new-game-path --new-game-start --new-game-act`(활성 8 player records, 부하 증명 아님), 저장 pair = 기본 save006. 산출물 공유 temp `20261008_lap1176_work_hdpal/`(`run_*`·`pack_pal`·`scripts`·`metrics_*`·`crops`). 합본 팩 `pack_pal/` = `cecc4681/`(기존 `pack_cf`의 `h*`·`w004663e0_*` 25,634개 **하드링크**, 디스크 0) + `296963d9/f69eae15c_800x600.idx8`(하드링크). 디스크 여유 109→95 GB(prefix 보존, game 사본은 하네스가 삭제).

## 3. 결과

**HP-S(정적, 원본 EXE 직접 역어셈블 독립 확인):** 파일 팔레트 로더 `0x465600`·배열 로더 `0x465840`이 렌더러 `+0x15A0`(256×R,G,B,flags, 파일값 `<<2`)을 채우고 `CreatePalette`(`[ecx+0x14]`)·`SetEntries`(`[edx+0x18]`)에 그대로 넘긴다 → 화면 팔레트 소스 = `+0x15A0`. `+0x419A0`(768 B)은 LUT 초기화 `0x465300`이 한 번 만든 6비트 복사본이고 **실행 중 바뀌지 않으며 `imjin2.pal`과 같다**(P0c 키 로그 7줄 전부 `start*4` = imjin2, pal8 `cecc4681` 직접 재계산).

**HP-0(NG5, 빈 팩 3 run P0·P0b·P0c, 진단 로그 `pal_change`):** PS9 `296963d9` = `title_plus.PAL`·PS5 `e24d0e6d` = `titlelobby_plus.PAL`·PS7 `84428eed` = `titleprotocol_plus.PAL`(**PS7 팔레트 신규 식별**, `titlesession_plus`와 동일). **PS3 = `156a9281`(1,531 present 전부) ≠ imjin2(`cecc4681`)**: `.pal` 37개 어디에도 없고 `imjin2.pal`을 어둡게 한 값(채널별 모두 ≤ imjin2, 평균 밝기비 0.89). 같은 NG5 안에서도 `b0f3b229`(0.91)→`abeda7a5`(0.86)→`156a9281`(0.89)로 바뀌는 낮밤/페이드 계열이다. → 사전등록 §6 "PS3 pal = imjin2" **불일치(사실 기록)**. 정확 일치만 쓰면 PS3 HD가 꺼지고 night*.pal 하드링크는 이 값들을 덮지 못한다(연속 변화라 열거 불가). **소스 교체 1회(결정):** 소스는 그대로 `+0x15A0`, 팩 디렉터리 id만 바꾼다.

**규칙(구현):** 화면 팔레트의 항목 중 `start*4`(`+0x419A0`×4)보다 한 채널이라도 밝은 항목이 **8개 이하**면 in-game 계열 → id = FNV(start*4) = `cecc4681`(imjin2 팩 디렉터리), 아니면 정확한 화면 팔레트 FNV. 근거(오프라인 대조): in-game 3종 밝은 항목 0, title/lobby/protocol 217~229, `imjin2.pal`·`titlestaff1_plus.PAL` 0, `night1~4`·`00~10.pal` ≥18(`11.pal`은 0이라 in-game 계열로 분류되나 게임이 쓰는 값인지 미확인). 이유: 팩 프레임은 인덱스이고, 어두워진 imjin2는 같은 인덱스 의미에 모든 색이 어두워진 것뿐이라 imjin2 양자화 팩이 그대로 맞는다. 안전 쪽 실패: 한 번이라도 의미가 다른 팔레트(타이틀 등)는 자기 `pal8` 디렉터리만 읽고, 없으면 Scale2x. 같은 규칙을 fullscreen·패널 팩 조회가 공유한다(`g1_hd_asset_palette_digest`). trace `hd_pal_digest`·`hd_pal_family`·`hd_pal_changes`·`hd_pack_pal_misses`, 키 로그 줄 `pal`.

**호스트 테스트:** `tests/test_g1_hd_pack.py`·`test_g1_hd_convert.py`·`test_g1_mirror2x.py` **115 passed**. 변이 확인: 허용 8→0이면 `test_up_to_eight_brighter_entries_…` RED, 원복 GREEN. 신규 테스트 = 어두워진 start 팔레트가 start 디렉터리 사용·키·`palette_changes` 불변, 8개 허용·9개 이탈, 키 로그 `pal_change` 1줄(family 내 어두워짐은 변화 아님).

**HP-1 run(합본 팩 `pack_pal`; 최종 DLL = H1, 직전 DLL = G1·F1·F2·F0):**

| run | 내용 | 결과 |
|---|---|---|
| G1 / **H1**(최종 DLL) NG5 | PS9 버튼 2×2 평균 차(캡처 `menu.png`, x20..480·y480..590) | **0.380**(>16 비율 0.0058; lap1173 G1 11.053·F1 0.380) — 합격 ≤1.0 |
| 〃 | PS9 fullscreen | hits 67/67(=menu 호출, rejects 0, loads 1) |
| 〃 | PS3 HD cov min / p95 / 안전 7종 / fallback / dropped | 100.0 / 7 ms / 0 / 0 / 0, scale2x validator PASS, `hd_mask_outside_diff` 0 |
| 〃 | matched hit 비율 | 지형 100%·음영 100%·tinted 0.9897(reject 2 = lap1169 tree_plus 명시 예외 키 `44c611f6`)·in-game(`cecc4681`) 키는 이름이 팩에 있는 것 전부 hit(hit 132·lut_hit 194·shade_hit 148, 팩에 이름이 있는데 miss인 in-game 키 0) |
| 〃 | 타이틀 계열 키의 팔레트 | title/protocol/lobby 키 중 imjin2 팩 파일과 이름이 같은 24개(`296963d9` 5·`84428eed` 10·`e24d0e6d` 9) = **`miss` → Scale2x**(변색 경로 차단), pal 디렉터리 부재 `hd_pack_pal_misses` 30 |
| 〃 | PS5·PS7 캡처 vs baseline 2×2 평균 차 | PS5 0.376(lap1173 G1 0.666)·PS7 0.368(0.807) — 변색 경로가 사라져 개선 |
| 〃 | PS5·PS7 HD cov min | 98.949·99.709(lap1173과 동일) |
| F1 save006 pair | PS9 fullscreen 69/69·**pair PASS**·PS9 HD 100·버튼 0.38 | PS3 HD min 98.439(15 present<99, 2 present<98.6) |
| F2(같은 설정 재실행) | pair PASS·PS3 HD min **99.287**(<99 0) | F0(빈 팩 대조) min 99.287·<99 0 → F1 dip = 16 present 일시 stale(1.5k→4.2k px 후 0으로 해소, 이 구간 pack hits/misses/keys 불변)로 팩 무관, 재현 안 됨 |

크롭 `crops/G1_buttons.png`(위 baseline·아래 후보) 열람: 버튼 8개 테두리·바탕·글자 변색·잡음 없음.

**판정: `PASS(partial, 기술·격리)`.** 합격 기준 전 항목 충족(PS3 팔레트 사전등록 불일치는 위 규칙으로 처리·공개). 팩은 imjin2·title_plus 외 팔레트용 프레임이 아직 없다(PS5·PS7 전면 그림·타이틀 버튼 title 팔레트판은 비목표).

## 4. 공개 한계 / 위험
- (공개) in-game 계열 규칙은 휴리스틱(≤8개 밝은 항목). 낮밤 외 다른 PS3 팔레트(밝은 항목 9개 이상 섬광·다른 스테이지 팔레트 파일)는 Scale2x로 폴백(안전 쪽). 여러 스테이지·시간대 실측은 미실시.
- (공개) 팔레트 id는 틱당 한 번 계산(GetTickCount), 같은 ms 안 변경은 다음 ms 반영.
- (공개) `+0x419A0`이 start 이후 바뀌지 않는다는 점은 P0 7줄(전부 동일)로만 확인.
- (공개) PS7 팔레트는 `titleprotocol_plus.PAL`로 확인했으나 PS7·PS5 전면 팩 그림은 없음(다음 ⑤ 확장).
- (미충족 없음) 하드링크 팩이므로 `pack_cf`(lap1173) 평면 구조는 이제 읽히지 않는다 — 구 팩을 쓰는 다른 실행은 `<pal8>` 디렉터리로 옮겨야 한다.

## 5. 명령
`scripts/run.sh P0|P0b|P0c <pack_empty> --new-game-path --new-game-start --new-game-act`(HP-0), `scripts/run.sh G1|H1 <pack_pal> --new-game-path --new-game-start --new-game-act`, `scripts/run.sh F0 <pack_empty>`·`F1|F2 <pack_pal>`(save006 pair), `scripts/regions.py`·`metrics_f.py`·`metrics_ng5.py`·`crops_f.py`. 원본 SHA 전후 MATCH, 커밋 0.

## 다음 행동
middle(Opus) 검수: 키 로그 `pal_change`·trace `hd_pal_*`·원본 `.pal` 대조로 pal8 값과 규칙 재계산, PS3 규칙의 안전성 판정, 이후 ⑤ 확장(PS5 `titlelobby`·PS7 `titleprotocol` 전면 그림을 각 화면 팔레트로) 또는 H-HDS1r. 사용자 G1 시험 결과가 오면 최우선.
