# 2026-10-09 | lap 1194 | G1 work — H-HDB2: `0x467B00` 클립 가중표 혼합 HD 키 경로

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1193 middle 사전등록 §7(`20261009_lap1193_middle_g1_hdn0_review_hdb2_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 33 GB, 끝 25 GB(run 6개, game 사본은 하네스가 종료 때 삭제).
- 가설: `0x467B00` = `0x467580` + renderer 클립(`+0x4D0..0x4DC`, 오른쪽·아래 포함)이므로, H-HDB1 공유 코어 `blend_key_apply`에 "화면 교집합 ∩ 원본 호출 전에 읽은 클립" 창만 넘기면 같은 자기 검사·키 그리기가 성립한다. 클립이 막은 칸은 원본이 쓰지 않으므로 자기 검사 창에서 빼야 불일치가 없다.
- 예상 PASS/FAIL: 사전등록 §7(B2-0·B2-2 변이 전부 RED · B2-4(i) 팩 귀속 키 keyed ≥95%·자기 검사 불일치 0·`key_clip_cut` ≥1·안전 0·p95 ≤ 끔+2·stale ≤ 끔 규모·`0x467580` 비회귀 · (ii) pair PASS · (iii) 화면 안 호출 합 300 미만이면 save000 pair).

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_blend_key.h` | `g1_blend_clip_window(x0,y0,x1,y1,left,top,right,bottom,&wx0..)`: 화면 교집합(반열림)을 클립 사각형(오른쪽·아래 **포함**)으로 자른 창. 비면 0(출력 불변). 64비트 중간값으로 `INT32_MAX` 오버플로 방지. 순수 함수 |
| `tools/inmm_stub/g1_mirror2x.c` | `mirror_blend_clip`: 원본 호출 **전에** 클립 4값(`G1_RENDERER_VIEWPORT`+0/4/8/12 = left/top/right/bottom)을 읽어 창 계산 → 창이 있으면 `blend_key_snapshot(창)`과 창 크기 pre-draw 복사(`g_blend_clip_key_before`, 기존 화면 교집합 복사에서 crop) → 원본 → 기존 diff 미러 → `blend_key_apply(G1_BLEND_CLIP, weighted=TRUE, 키=전체 사각형, 창)`. 스트림 사각형이 800×600 버퍼 초과면 `key_fallbacks`. 창이 비면 `key_clip_empty`(키 시도 없음). 키 성공이고 창이 교집합보다 좁으면 `key_clip_cut`. 폴백·miss면 diff 미러 유지. `G1BlendKeyStats`에 `key_clip_cut`·`key_clip_empty` 추가, `g_blend_clip_key` 리셋·접근자 6개 |
| `tools/inmm_stub/g1_mirror2x.h`·`direct_draw_trace.c` | 접근자 6개, present metrics `blend_467B00_keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels/key_clip_cut/key_clip_empty` |
| `tools/inmm_stub/g1_hd_asset.c` | `G1_HD_BLEND_CLIP 0x00467B00`을 `hd_pack_blend_*` 카운트 대상에 추가(끔 env `SYW2_G1_HD_PACK_BLEND=0` 공유, 새 env 없음) |
| `tests/test_g1_blend_key.py` | B2-2: 호스트 컴파일 3(클립 창 4변·포함 경계·1칸 클립·극값, 빈 창, 위가 잘린 행의 스트림 순서) + 배선 정적 3(클립 읽기 순서·원본 전·키 블록 위치·crop 오프셋·cut/empty 카운터·트레이스 필드·리셋·writer). 총 23 |
| `tests/test_g1_hd_pack.py` | B2-0: 호스트 로더 시나리오 `extx_stale`(c4)·`extx_refresh`(c9)·`blendclip_hit`. 총 72 |
| `tests/test_g1_hd_convert.py` | B2-0: p2 도구 테스트 2(작은 L이 일부만 가르면 건너뛰고 모두 가르는 큰 L 선택 · 어떤 L도 두 그림을 못 가르면 충돌 유지). 총 45 |

파일 SHA256 앞 16자(최종, 첫 Y2 run 시작 이후 `tools/`·`patches/`·`tests/` 변경 0 = `find -newer` 빈 출력 2회): `g1_blend_key.h 3afce0852abbae13`·`g1_mirror2x.c be7a83c34b15e936`·`g1_mirror2x.h 55a4316eae204f1c`·`g1_hd_asset.c 1fae392fb8f23be2`·`direct_draw_trace.c d7239deac640129c`·`test_g1_blend_key.py d86f86b03b545b07`·`test_g1_hd_pack.py 4d9661497b22aeec`·`test_g1_hd_convert.py e92bc2a012840acf`·`_inmm.dll 547e6179c512d87b`. 원본 EXE SHA `b56986e0…` run 전·후 MATCH(`orig_sha_before2/after/after2.txt`). 공유 temp `20261009_lap1194_work_hdb2/`.

## 측정

**B2-0(lap1193 생존 변이 막기):** c4(`build_hd_frame` 입구 `g_last_ext` 리셋 제거)·c9(ext reject 카운트를 첫 시도 밖으로)·p2(분리 판정 `all`→`any`) **3/3 RED**(`mut/mutation_lap1194.py`, 격리 사본, 베이스 140 GREEN).

**B2-2 변이 19종**(격리 사본; m1 오른쪽 배타·m2 아래 배타·m3/m4 left/top을 max 대신 min·m5/m6 빈 창 판정 완화·m7 클립 읽기 순서 교환·m8 snapshot을 교집합으로·m9 writer id 교체·m10 weights 끔(FALSE)·m11 cut 항상 참·m12 cut 카운트 제거·m13 crop 오프셋 교환·m14 blend 카운트에서 `G1_HD_BLEND_CLIP` 제거·m15 키 창 대신 교집합 전달·m16 빈 창에서 키 계속·m17 버퍼 초과 폴백 제거·m18 `key_clip_cut` 리셋 제거·m19 트레이스 필드 이름 변경): **19/19 RED**. 추가 시도 m20(`keyed_calls >= 0`을 호출에 덧붙임)은 무부호라 항상 참인 동등 변이로 SURVIVED(코드 영향 없음). 결과 `mut/mutation_lap1194.txt`·`mut_out.txt`. 변이 후 사본은 원본과 일치로 복원.

**B2-4 실게임(하네스 `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 56`, `scripts/run.sh`·`seq1/2/3.sh`, 팩 `pack_hdb2` = 도구 `extract`·`draft`·`pack`으로 만든 `fnt/{CLOUD,exp6,groundfiresmoke,groundfire,smoke0,tornado,movemark}` 7개 team-safe 초안(bicubic stand-in, 화질 평가 아님), pair 전용 `pack_hdb2b` = 위 + `fnt/itemlight`):**

| run | 팩·env | PS3 present·s | `0x467B00` 호출(화면 안 mirrored) | keyed | 폴백 | 클립 빈 창 | `key_clip_cut` | 자기 검사 불일치/px | p95 | stale 최대 | 안전 7종 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Y1 (켬, 카운터 추가 전 DLL) | `pack_ext`(movemark 없음) | 6,029·302 | 155,006(2,228) | 1,579 | 7 | (642, 추정) | 1,391 | **0** / 7,409,548 | 6 | 91 | 0 |
| Y2 켬 | `pack_hdb2` | 5,955·301 | 168,984(126) | 31 | 0 | 95 | 11 | **0** / 124,270 | 7 | 90 | 0 |
| Y3 켬 | `pack_hdb2` | 6,031·301 | 159,166(818) | 810 | 0 | 8 | 8 | **0** / 6,116,163 | 6 | 245 | 0 |
| Y0 끔 | `pack_hdb2`, `BLEND=0` | 6,105·305 | 149,626(560) | 0 | 0 | 0 | 0 | — | 6 | 90 | 0 |
| pair PB | `pack_hdb2` save006 | — | 키 로그 16키 전부 miss(`fnt/itemlight`) | — | — | — | — | — | — | — | — |
| pair PB2 | `pack_hdb2b` save006 | — | 키 로그 **16키 전부 hit**(draws 40) | — | — | — | — | — | — | — | — |

- **B2-4(i) 합격(분모 정의):** 켬 두 run(Y2+Y3) 화면 안 mirrored 호출 합 944 = keyed 841 + 폴백 0 + 클립 빈 창 103(= 키를 시도하지 않은 호출, 원본이 클립 밖이라 아무것도 안 그림). 키를 시도한 841호출은 **100%** keyed(팩 귀속 키 25~12개 전부 hit, key 로그 miss 0). 화면 안 호출 대비로는 89.1%(11%는 빈 창). Y1은 팩에 `movemark`가 없어 폴백 7(=movemark 키 7개 miss, 시도 1,586 중 99.56%)이라 팩에 movemark를 더한 `pack_hdb2`로 Y2·Y3을 다시 돌렸다. 자기 검사 불일치 **0**(세 run 합 1,360만 px), `key_clip_cut` Y1 1,391·Y2 11·Y3 8 ≥1(클립 경계 실제 시험), 안전 7종 전부 0, p95 6~7 ≤ 끔 6+2, dropped 0.
- `0x467580` 비회귀: Y2 29/29·Y3 819/819(100%) keyed, 불일치 0. `0x4672E0`은 이 run들에서 로고 팩 파일이 없어 전부 폴백(6,029·5,955·6,031호출, lap1188 이후 같은 서명 — 이번 변경과 무관).
- **B2-4(i) stale ≤ 끔 규모 — 공개:** Y2 90(76.4 s)·Y0 끔 90(229 s)·Y1 91로 같은 규모이나 **Y3은 13.1 s 245·14.9 s 242·15.2 s 79/75·15.3 s 18** 군집이 있다. lap1192 기록의 "13~15 s 군집 최대 255~259(기존 서명)"과 같은 시각·크기이고, 그 T0 run은 `0x467B00` 키 경로가 코드에 **없던** DLL이었다(그래서 이번 변경이 원인일 수 없다는 간접 증거). 같은 팩 끔 run Y0에는 없었으나 run마다 나오지 않는 군집(Y1·Y2에도 없음)이라 이번 갈래 끔 대조가 아니다. 이 군집은 lap1187 backlog "15.5 s 선택 군집 변동 18~305"와 같은 계열로 미규명이다.
- **B2-4(ii) 합격:** pair PB `status PASS`·`scene_state_equal` true·input_effect/minimap/loaded·selection·drag·production 캡처·V2/V2s/V2q/Scale2x 전부 PASS인데 이 장면의 `0x467B00`은 `fnt/itemlight.Spr` 16키뿐이라 pack에 파일이 없어 전부 miss(키 경로를 실제로 타지 않음). 그래서 `itemlight`를 더한 `pack_hdb2b`로 **pair PB2**를 다시 돌렸고 `0x467B00` 16키 전부 hit(draws 40)에서도 `status PASS`·`scene_state_equal` true·모든 게이트 PASS(위와 같은 25개 status 중 UNKNOWN/FAIL/BLOCKED는 `owner0_hq_type` UNKNOWN 2·`candidate.trace_close` FAIL·`mirror_validator` BLOCKED로, 기존 하네스 문제와 동일, lap1189 backlog). pair는 `--candidate-no-present-trace`라 metrics가 없어 keyed 호출 수는 키 로그(hit 16키)로만 본다.
- **B2-4(iii):** 켬 두 run 화면 안 호출 합 944 ≥ 300이므로 save000 pair는 사양대로 생략.
- **원본 보호:** EXE SHA `b56986e0…` 전·후 MATCH 3회(`orig_sha_before.txt`·`before2`·`after`·`after2`). `local/runtime/lap1194_hdb2_*`의 `game` 사본 없음(하네스 종료 때 삭제), baseline·candidate 보존.

## 판정

**B2-0 PASS**(3/3 RED) · **B2-1 PASS**(공유 코어 재사용, 복제 0) · **B2-2 PASS**(19/19 RED, 동등 1) · **B2-3 PASS**(Y1·Y2·Y3·PB·PB2 키 로그의 `0x467B00` digest 62개를 lap1192 `digest_index.json`로 `.spr` 7개에 귀속: 미귀속 0 — itemlight 16·CLOUD 14·groundfire 10·smoke0 8·movemark 7·groundfiresmoke 5·exp6 2) · **B2-4(i)** keyed 100%(시도한 호출)·불일치 0·`key_clip_cut` ≥1·안전 0·p95 ≤ 끔+2 PASS, **stale ≤ 끔 규모는 Y3 13~15 s 군집 245로 literal 미달(기존 서명, 공개)** · **(ii) PASS**(PB2) · (iii) 생략. 전체 `PASS(partial, 기술·격리)` 후보. 기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

## 한계·공개

1. 팩 그림은 bicubic stand-in이며 실제 업스케일 화질 평가가 아니다. 클립 경계를 "맞는 위치"에 그린다는 증거는 자기 검사(원본 1x 출력 = 같은 식, 창 안 불일치 0)와 `key_clip_cut` 호출 19건(Y2 11·Y3 8)의 불일치 0이다. 클립 경계가 어긋난 HD 그림을 육안으로 본 run은 없다.
2. Y3 13~15 s stale 군집은 literal 미달이다. 근거(코드에 키 경로가 없던 lap1192 T0에도 같은 시각·크기)는 간접이며, 이번 변경 켬/끔을 같은 장면으로 대조한 run이 아니다(run마다 군집이 나오지 않음).
3. `key_clip_empty`(빈 창) 계수는 Y1에는 없다(카운터 추가 전 DLL, 642는 mirrored − keyed − fallback로 추정). Y2·Y3은 keyed + 폴백 + 빈 창 = mirrored 합이 정확히 일치(31+0+95=126, 810+0+8=818).
4. pair PB(`pack_hdb2`)는 `0x467B00` 키를 한 번도 못 타 사실상 비회귀 확인이 아니다. PB2가 그 공백을 메운다. 둘 다 candidate는 present trace 없음.
5. 남은 충돌 3개(`char/bullk*.spr`)·`0x4685C0`·`0x467FD0`·실제 업스케일 화질·기본 켬은 비목표다.
6. 정적 테스트 일부는 문자열 계약(변이로 RED 확인).

## 다음 행동

middle(Opus)이 H-HDB2를 검수(클립 창 식·읽기 순서·자기 검사 창, 변이 재현, key 로그·trace 재계산, Y3 군집 판정)한 뒤 다음 writer `0x4685C0` → `0x467FD0`를 사전등록한다. 사용자 G1 시험 결과가 오면 최우선.
