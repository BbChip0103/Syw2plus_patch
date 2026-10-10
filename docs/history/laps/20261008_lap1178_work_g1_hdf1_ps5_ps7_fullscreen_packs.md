# 2026-10-08 | lap1178 | G1 work — H-HDF1: PS5 대기실·PS7 접속 방식 전체 화면 그림 팩(각 화면 팔레트, C 변경 0)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / work(실무). middle 검수는 `loop/ESCALATE_SOL`로 요청한다(자기 승인 없음).
- 입력: lap1177 middle §6 사전등록(`docs/history/laps/20261008_lap1177_middle_g1_hdpal_review_hdf1_preregistration.md`). `loop/STOP`·사용자 G1 시험 결과·INBOX 새 지시·APPROVALS 반려 없음. 디스크 여유 94 GB.
- 가설: PS5(`titlelobby.spr`, hash `0x100DF815`)·PS7(`titleprotocol.spr`, `0xE8FD3BBC`) 배경도 PS9처럼 매 present 800×600 블록 복사이므로 도구 `fullscreen --pal`로 `e24d0e6d/f100df815_800x600.idx8`·`84428eed/fe8fd3bbc_800x600.idx8`를 만들면 **C 변경 0**으로 두 화면 배경이 팩으로 바뀌고 변색은 없다.
- 예상 PASS(사전등록 §6): PS5·PS7 fullscreen hits = 각 상태 menu 호출 수·rejects 0·loads ≤ 2(화면당 1) / 캡처 차 ≤ 3.0·>16 비율 ≤ 5% / p95 ≤ H1+2 ms·HD min ≥ H1−0.1 / PS3 HD min ≥ 99.9·안전 7종·fallback·dropped 0·matched hit 비율 H1 ±2%p / `hd_pack_pal_misses` 감소 / 원본 SHA 불변·game 사본 삭제.

## 1. 변경 파일 / source fingerprint

**source·테스트·도구·하네스 변경 0.** lap1177 기록 SHA와 전부 일치하고 `logs/gates/lap1177-middle-focused.log`보다 새로운 파일 0(`find -newer`): `g1_hd_asset.c` `2253b963bcbfec56`·`.h` `467c7a9f721bf91d`·`direct_draw_trace.c` `eb760613a213ab08`·`g1_hd_pack.h` `fb13d7fb0c94ce6b`·`g1_mirror2x.c` `33e7328a3ad9362b`·`g1_hd_convert.py` `5f91271056851b28`·`test_g1_hd_convert.py` `d084e99a427be7af`·`test_g1_hd_pack.py` `ca0d56d3263c5026`.
산출물은 전부 공유 temp `20261008_lap1178_work_hdf1/`(`pack_hdf1_new`·`pack_hdf1`·`run_F1`·`run_F1.keys.jsonl`·`metrics_*`·`crops`·`scripts`). 새 팩 파일(SHA256):
- `e24d0e6d/f100df815_800x600.idx8` `5907ba8de198b96387dee9dc2cadafb885a395e40b645096681b3158dfab80d9`(1,920,000 B)
- `84428eed/fe8fd3bbc_800x600.idx8` `b3c8b3f8ad1925529ff665474dd641dbd994415ddf2327e68c519aa7bf41191e`(1,920,000 B)
합본 팩 `pack_hdf1/` = lap1176 `pack_pal`(`cecc4681/`·`296963d9/`) **하드링크** + 위 2개(디스크 추가 3.84 MB). run 결과 SHA256 앞 16자: `new-game-path-result.json` `231707ec2f2220af`·`candidate/trace_raw.jsonl` `14e151cd1a2c3cdc`·`run_F1.keys.jsonl` `8d19e0749a4258a0`.

## 2. 실행 환경

원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전(`orig_sha_before.txt`)·후(`orig_sha_after.txt`) MATCH. 격리 Wine·Xvfb 1600×1200, `tools/g1_saved_scene_probe.py --hd-source scale2x`, fixture = NG5(`--new-game-path --new-game-start --new-game-act`, 활성 8 player records, 부하 증명 아님). 실행 DLL = 하네스 bridge 빌드 `_inmm.dll` `8823d294…`(lap1176 H1 `d51eddb4…`와 6 B만 다름 — 오프셋 137·138·217·218·362501·362502 = PE 타임스탬프·체크섬 영역, 코드 동일). 격리 run 1회(F1), 대조 = lap1176 H1(같은 하네스, 두 파일 없음). game 사본은 하네스가 삭제(`local/runtime/lap1178_hdf1_F1/game` 부재, baseline·candidate 산출물 1.2 GB 보존). 디스크 여유 94→92 GB.

## 3. F-0 (오프라인)

`scripts/f0.py`(`f0.json`): `yfnt/titlelobby.spr`·`titleprotocol.spr` 크기 483,060 = 헤더 3,060(lap1174 title.spr과 같은 구조) + 800×600 화소 480,000(헤더 앞 12 B `09 00 00 00 20 03 00 00 58 02 00 00` = 9·800·600), 파일 끝 800×600 화소 전 바이트 FNV-1a = `0x100DF815`·`0xE8FD3BBC`(사전등록 hash 일치) → 팩 이름 `f100df815`·`fe8fd3bbc`(도구 산출 이름과 일치). 0xFE 원본 0·팩 0(키 색 reject 없음). 팩 2×2 평균 vs 1x 평균 절대 차(화소당 RGB):

| 팩 | 자기 팔레트 | 다른 `title`/`protocol`/`lobby` | title_plus | imjin2 |
|---|---|---|---|---|
| lobby(PS5) | **0.646** (≤2.5) | protocol 1.600 | 2.199 | 8.546 |
| protocol(PS7) | **0.523** (≤2.5) | lobby 2.225 | 2.285 | 7.560 |

자기 팔레트가 가장 작아 팔레트가 올바르다(F-0 합격).

## 4. F-1 결과 (run_F1, status PASS·source_unchanged True·scale2x PASS)

상태별 연속 구간(`mirror2x_present`, 누적 카운터의 구간 끝 값·차):

| 상태 | present | fullscreen hits(구간) | misses | rejects | loads(누적) | HD min | p95 ms | H1 p95 / HD min |
|---|---|---|---|---|---|---|---|---|
| PS9 타이틀 | 66 | 66(=66) | 0 | 0 | 1 | 100 | 14 | 14 / 100 |
| PS7 접속 방식 | 157 | **157**(= 223−66, = 157) | 0 | 0 | 2 | 99.709 | 16 | 14 / 99.709 |
| PS5 대기실 | 710 | **710**(= 933−223) | 0 | 0 | 3 | 98.949 | 15 | 14 / 98.949 |
| PS3 인게임 | 1,537 | 933 유지(menu 복사 0) | 0 | 0 | 3 | 100 | 7 | 7 / 100 |

- fullscreen hits = 상태별 present 수(= menu 호출 수에서 첫 호출 1 제외), 전체 933 = 66+157+710, **misses 0·rejects 0**, loads 화면당 1(총 3). H1은 PS7 miss 164·PS5 miss 755였다. `hd_pack_pal_misses` **30 → 0**(H1 30).
- HD min은 H1과 동일(PS7 99.709·PS5 98.949 — 미러가 이미 덮던 면적이라 coverage 지표는 변하지 않음, 판정은 hit 카운터가 맡음). PS7 p95 16 = H1 14+2(사전등록 상한 경계), PS5 15.
- PS3 HD min 100·dwell 1,200 present 전체 100·select/produce/drag 100. 안전 7종 합 0·fallback 0·`trace_dropped` 0·`hd_mask_outside_diff` 0·V1/scale2x validator PASS. `mirror_validator`는 H1과 같은 BLOCKED(이번 변경 무관, 기존 상태).
- in-game 키(같은 코드·팩 `cecc4681`, 장면 변동): ab matched hit 0.7736(H1 0.7526, +2.1%p 높아짐), 지형 1.0, tinted 0.9895(0.9897), 음영 1.0(1.0); 키 first 결과 hit 137·miss 70·shade_hit 138·lut_hit 188·reject 2(H1 128·68·149·193·2). reject 2 = lap1169 tree_plus `0x466EA0` 96×112 `44c611f6` 예외 키 그대로(새 reject 0, `lut_rejects`·`shade_rejects` 0).
- 캡처(`capture_diff.txt`, candidate 2× → 2×2 평균 vs baseline): PS5 평균 차 **0.650**·p99 7.33·>16 비율 0.13%, PS7 **0.505**·p99 5.00·0.05%(H1: 0.375/0.368). 비균일 2×2 블록 PS5 28.3%·PS7 27.0%(H1 20.1·21.1% — 팩의 바이큐빅 stand-in이 1x 반복보다 디테일이 있음).
- 크롭 열람(`crops/F1_ps5_mid.png`·`F1_ps5_bottom.png`·`F1_ps7_top.png`, 위 baseline 2배 nearest·아래 후보): 하늘·석재 패널·잔디·버튼·한글 글자 변색·잡음·줄무늬 없음, 구도 동일, 질감만 부드러움.

## 5. 판정

**H-HDF1 `PASS(partial, 기술·격리)`**: 사전등록 §6 측정식 전부 충족(위 표) — 단 `ab matched hit` +2.1%p는 ±2%p 문구를 +0.1%p 넘지만 비율이 **높아진** 방향이고 코드·ab 팩은 H1과 동일(장면 변동)이라 미충족이 아닌 공개로 둔다.
미충족 없음. 공개 한계: (1) 단일 run, 장면 길이 PS5 710·PS7 157 present — 팩 hit 100%는 이 장면의 고정 그림 기준, (2) 화질 평가 아님(바이큐빅 stand-in)·기본 켬 아님·사용자 전달 아님, (3) 다른 전체 화면(브리핑·결과·로딩·옵션)은 비목표라 미관측, (4) `pack_cf` 평면 팩은 `<pal8>` 이전 필수(lap1176 공개 유지), (5) 화면 팔레트 계열 규칙 공개 위험(lap1177 §3-3)은 그대로. 새 안전 위험·근거 충돌 없음.

## 6. 명령

`.venv/bin/python tools/g1_hd_convert.py fullscreen --pal "../[ESL]Syw2plus/pal/titlelobby_plus.PAL" "../[ESL]Syw2plus/yfnt/titlelobby.spr" --out <W>/pack_hdf1_new`(protocol도 동일, `titleprotocol_plus.PAL`), `scripts/f0.py`, `cp -al pack_pal pack_hdf1 && cp -al pack_hdf1_new/* pack_hdf1/`, `scripts/run.sh F1 <W>/pack_hdf1 --new-game-path --new-game-start --new-game-act`(PID 대신 `.exit` 파일 대기), `scripts/metrics_f.py`·`metrics_ng5.py <W> F1 <W>/pack_hdf1/cecc4681`·`crops_ps.py`. 커밋 0, 원본/참고 쓰기 0.

## 7. 검사

source·테스트·도구·C 변경 0이라 `make check`·lint·typecheck 생략(lap1176 full PASS 1944 passed 그대로, 그 뒤 바뀐 tools·tests·source·Makefile 0 확인). `checks/safety.sh check`·CONTEXT 결과는 STATUS 검증 줄에 보강한다.

## 다음 행동

middle(Opus) 검수: 키 로그·trace 구간 카운터·팩 hash·팔레트 평균 차·캡처 차 독립 재계산, PS7 p95 16(경계)의 환경 변동 여부, 그다음 work H-HDS1r(음영 LUT refresh 결함, 기본 켬·전달 전 필수) → ⑥ 유닛 경로. 사용자 G1 시험 결과가 오면 최우선.
