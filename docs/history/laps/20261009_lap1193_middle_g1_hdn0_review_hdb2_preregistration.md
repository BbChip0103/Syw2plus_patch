# 2026-10-09 | lap 1193 | G1 middle — H-HDN0 검수 + work H-HDB2(`0x467B00` 클립 가중표 혼합 키 경로) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간(middle, 진단·확인). 게임 실행·C source 수정·커밋 0. 변이 시험은 Sonnet 하위 에이전트가 격리 사본(공유 temp)에서 수행했다(저장소 비접촉, 끝난 뒤 사본이 저장소 source와 `diff` 일치).
- 입력: `loop/ESCALATE_SOL`(lap1192 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261009_lap1193_preserved_lap1192_escalate_sol.txt`(SHA256 앞 `7c037986324316c8`), 보존 뒤 삭제. `loop/STOP` 없음. INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 33 GB.
- 가설(검수): lap1192 N-0~N-5 수치가 raw에서 재현된다. 확장 이름 조회는 기본 이름이 없을 때만 동작한다. 확장 hit는 맞는 프레임만 고른다.
- 산출물(공유 temp `20261009_lap1193_middle_review/`, SHA256 앞 16자): `split_recalc_lap1193.py` `4263cdfb5eab7403`·`.json` `d42b16a76c748572`, `recalc_lap1193.py` `527570afa3d84ae9`·`.json` `2d8b7a6cb820fa5e`, `pack_files_check.py` `47728145c1741d03`·`pack_files_check_lap1193.json` `ac2e651f4d09cf2c`, `name_check.c` `674c957b3e77c481`, `orig_467B00.asm` `b418601f9c5537d8`, `mut/mutation_lap1193.py` `472e41f0312c0228`·`.txt` `454db4ae37b33c4d`.

## 1. source·원본 정체성

- source SHA256 앞 16자 9개가 lap1192 기록과 일치한다: `g1_hd_pack.h 526ecfeb…`·`g1_hd_asset.c 1c648f23…`·`.h d92c7798…`·`direct_draw_trace.c e306ea68…`·`g1_hd_convert.py fcea3f37…`·`test_g1_hd_pack.py 348cb5b4…`·`test_g1_hd_convert.py 5ada57fd…`·`test_g1_blend_key.py 53477c54…`·`_inmm.dll d4ec493e…`. `logs/gates/lap1192-work-full-check.log` 뒤로 `tools/`·`patches/`·`tests/` 변경 0(`find -newer`). 그 로그의 결과는 `2005 passed, 5 skipped in 800.88s`다.
- 원본 EXE SHA `b56986e0…`는 work 전·후 기록과 이번 회차 재계산이 모두 MATCH다. `local/runtime/lap1192_hdn0_*` 6개에 `game` 사본은 없다.

## 2. C 확장 조회 독립 검토(`g1_hd_asset.c`·`g1_hd_pack.h`)

- **우선순위:** `read_pack_frame`은 기본 이름 `CreateFileA`가 실패했을 때만 `open_extended_pack_file`을 부른다(`note_missing_file` 뒤). 기본 이름 파일이 있으면 마커는 열지 않는다.
- **마커 검사:** 파일 크기 정확히 4 B·상위 크기 0·`ReadFile` 4 B를 먼저 확인한다. 그다음 L ∈ [129, 65536]과 `readable_range(source, L)`를 확인한다. 이 셋을 통과해야만 L바이트 FNV-1a를 계산한다. 마커가 불량이면 `g_last_ext = 2`이고 결과는 MISS다.
- **소스 포인터:** `g_current_source`는 `g1_hd_asset_begin_with_aux`가 기존 키 hit 경로(824행)와 새 키 경로(887행) 모두에서 설정한다. `build_hd_frame`의 호출처는 1곳(1446행 identity 결합 직후 `g_current_key`)뿐이다. 그래서 해시 대상은 지금 그리는 스트림이다. 32비트 대상에서는 키의 `source` DWORD와 같은 값이고, 호스트 64비트에서만 다르다.
- **identity refresh·축출 재조립:** PACK_HIT 키만 파일을 다시 읽는다. 다시 읽을 때도 현재 스트림의 L바이트로 p8을 새로 계산한다. 그래서 같은 주소에 다른 그림이 들어오면 맞는 파일을 찾거나 miss가 된다. 낡은 그림은 쓰지 않는다.
- **카운트:** `g_last_ext`는 `build_hd_frame` 팩 블록 입구(1182행)와 `read_pack_frame` 입구에서 0이 된다. 그래서 SKIP_AUX·NONE·LUT_REJECT·SHADE_REJECT 경로는 0을 본다. ext 카운터는 `pack_state == PACK_UNTRIED` 블록 안에서만 증가한다.
- **최악의 마커:** 크기가 다른 마커나 L 범위 밖 마커는 miss로 끝나고 `ext_rejects`에 잡힌다. 범위 안이지만 틀린 L이면 p8이 어떤 파일과도 맞지 않아 miss다. 같은 p8 파일이 있어도 다른 실루엣이면 `g1_hd_pack_valid`가 reject한다. 잘못된 그림이 그려지려면 서로 다른 그림의 L바이트 FNV가 32비트에서 충돌하고 실루엣까지 같아야 한다.
- **이름 버퍼:** 확장 이름은 최대 `h`+8+`_`+3+`x`+3+`_`+5+`_`+8+`.idx8` = 37자다. `name[64]`이고 `cursor + 28 > output_size` 가드가 있다(현재 호출처에서는 동등 변이, §4 c10).

## 3. 도구 오프라인 독립 재계산(`split_recalc_lap1193.py`)

- 도구 코드(`_split_by_prefix`·`ext_candidates`·`stream_ranges`·`fnv1a_prefixes`)는 쓰지 않았다. 오프셋 표·다음 시작까지 범위·FNV-1a·그룹화·최소 L 탐색을 새로 구현했다. 1x 그림은 수용된 추출기 디코더(lap1158)로만 만들었다.
- 결과: 충돌 이름 **677**·충돌 프레임 4,612 → 확장 **674**(프레임 4,506)·남은 **3**(`h150e1aec`·`h2b9b3809`·`h2f6cbf38`, 모두 `86×60`, 106프레임). L 분포는 256 = 263·512 = 175·1024 = 77·2048 = 17·4096 = 5·8192 = 3, 최소 160·최대 12,173이다. 도구 `digest_index.json`과 비교하면 이름·L·p8별 구성원 차이가 **0**이고, 남은 충돌 목록도 같다. 불변식 위반은 0이다(L ≥ 129, 모든 구성원 범위 ≥ L, p8당 그림 1개).
- **남은 3개의 귀속(보강):** 모두 `char/bullk*.spr`(소 유닛 계열) 프레임이다.
- **C 헤더 이름 텍스트:** `g1_hd_pack.h`를 gcc로 컴파일한 `name_check`로 팩 디렉터리의 실제 파일 이름을 다시 만들었다(`pack_files_check.py`). `pack_ext`는 마커 2/2·확장 파일 4/4가 일치했다. `pack_ng5`는 마커 84/84·확장 파일 205/205가 일치했다. 확인 항목: L = 전역 index의 L, p8 ∈ 그 이름의 그림 집합, 크기 = 4·w·h, 같은 이름의 기본 파일 없음.
- **전역 충돌 안전(보강):** 두 팩의 기본 이름 파일(193·823개) 가운데 전역 충돌·확장 이름은 **0**이다. `pack`은 HD가 없는 파일까지 6개 폴더 전부를 훑어 충돌을 판정하므로, 일부 파일만 담은 팩도 다른 파일의 프레임에 잘못된 기본 이름 그림을 주지 않는다.

## 4. 변이 재현(격리 사본, 새 변이 16종 — work 변이와 겹치지 않게 설계)

| 변이 | 내용 | 결과 |
|---|---|---|
| c1 | L 하한 129 제거 | RED |
| c2 | L 상한 65536 제거 | RED |
| c3 | 현재 소스 대신 키 32비트 포인터 | RED |
| c4 | `build_hd_frame` 팩 블록 입구 `g_last_ext = 0` 제거 | **생존** |
| c5 | `read_pack_frame` 입구 `g_last_ext = 0` 제거 | 생존(동등: c4 리셋이 항상 앞선다) |
| c6 | 불량 마커를 "시도함"(1)으로 | RED |
| c7 | 마커 크기 `!= 4` → `< 4` | RED |
| c8 | 확장 해시 FNV 시드 0 | RED |
| c9 | ext 카운트를 첫 시도 밖(매 재조립)으로 | **생존** |
| c10 | 확장 이름 버퍼 가드 제거 | 생존(동등: 버퍼 64 B ≥ 최대 38 B) |
| p1 | 스트림 범위를 파일 끝까지 | RED |
| p2 | 분리 판정 `all` → `any` | **생존** |
| p3 | 접두 해시 길이 1 차이 | RED |
| p4 | 후보 시작 256 → 128 | RED |
| p5 | 구성원 최장 범위 사용 | RED |
| p6 | 마커 big-endian | RED |

- 기준선은 GREEN(112 passed)이다. RED는 11이다. 생존 5 가운데 c5·c10은 동등 변이다. **c4·c9·p2는 테스트 공백이다(현재 코드는 정상).** 위험은 p2가 가장 크다. 일부 그림만 가르는 L을 받아들이면 한 p8에 두 그림이 묶이고, 한쪽 HD를 다른 쪽에 그린다. 실루엣이 같으면 막히지 않는다. 현재 코드는 `all`이고 §3 재계산의 불변식 위반이 0이므로 산출물에는 영향이 없다. c4·c9는 진단 카운터만 틀어진다. 세 공백 모두 다음 work의 회귀 단언으로 넘긴다(§7 B2-0).

## 5. raw 재계산(`recalc_lap1193.py`, trace 마지막 present·metrics + 키 로그)

| run | PS3 present·s | p95 | stale 최대 | 안전 7종 | ext hit/miss/reject | `0x467580` 호출(clipped)·keyed·폴백·불일치/px | 확장 이름 키(키 로그) | `e88d0c4c` |
|---|---|---|---|---|---|---|---|---|
| X1 | 6,031·301.5 | 6 | 92 | 0 | 2/0/0 | 292(10)·292·0·0/693,695 | hit 2·miss 160(팩에 없는 파일) | 두 src 모두 hit |
| X2 | 6,032·301.5 | 6 | 255 | 0 | 2/0/0 | 824(97)·824·0·0/9,691,280 | hit 2·miss 53 | 두 src 모두 hit |
| Q1 끔 | 6,037·301.8 | 6 | 0 | 0 | 0/0/0 | 63(6)·50·13·0/744,397 | miss 56 | 두 src 모두 miss |
| T1 | 6,037·301.8 | 6 | 0 | 0 | **127/0/0** | 450(3)·450·0·0/5,088,969 | hit 31·shade_hit 90·lut_hit 6 = 127 | 두 src 모두 hit |
| T0 끔 | 6,105·305.2 | 6 | 259 | 0 | 0/0/0 | 10(0)·10·0·0/117,364 | miss 60 | 나오지 않음 |

- work 표의 수치는 모두 일치한다. 안전 7종 = present 최대 `fallback`·`hresult`·`identity_invalid_sources`·`scale2x_palette_violations`·`identity_key_mismatches`·`viewport_restore_failures`·`clip_replay_mismatches`. T1 확장 키 writer 분포도 work와 같다(`0x468C30` 8·`0x468F00` 12·`0x468CC0` 38·`0x4690A0` 52·`0x466540` 4·`0x466EA0` 2·`0x4664D0` 9·`0x467580` 2).
- pair PX: `status PASS`, `scene_state_equal` true다. V2/V2s/V2q/Scale2x·input_effect·minimap parity·loaded가 PASS이고, 캡처 5종(loaded·selection·drag·minimap·production)도 PASS다. 키 로그 `0x467580` hit은 8키다. 후보 `trace_close FAIL`과 `mirror_validator BLOCKED`는 기존 하네스 문제다(lap1189 backlog).
- X1·X2의 확장 이름 miss 160·53은 팩 `pack_ext`에 그 파일(지형 등)이 없어 생긴 일반 miss다. 마커가 없으므로 `ext_misses`가 0인 것과 맞는다.

## 6. 판정

**H-HDN0 `PASS(partial, 기술·격리)` 수용.** N-0 PASS(lap1191 생존 4종 단언), N-1 PASS(도구, work 5/5·이번 회차 6종 중 RED 5), N-2 PASS(C 구조 검토 §2, work 8/8·이번 회차 10종 중 RED 6·동등 2), N-3 PASS, N-4 PASS(674/677 독립 재현, 도구 대비 차이 0), N-5 PASS(i X1·X2 keyed 100%·`e88d0c4c` 두 프레임 hit·불일치 0·안전 0·p95 6, ii pair PASS, iii T1 127/127).

- **(a) 남은 3개(`char/bullk*.spr` `86×60`, 106프레임 = 전 프레임의 0.24%)는 backlog로 둔다.** 구성원 스트림이 서로의 접두라 범위 안 접두 길이로는 가를 수 없다. 전체 스트림 해시는 writer별 파서가 필요하다. 이 유닛의 실제 업스케일 팩이 들어올 때 다시 판단한다.
- **(b) 마커 열기 비용은 수용한다.** 기본 이름이 없는 키에서만 키당 1회(첫 시도, HIT 키의 refresh 제외) `CreateFileA` 1번이 더 든다. 다섯 run 모두 p95 6으로 같고, draw 경로 비용은 0이다.
- **(c) 추가 육안 run은 요구하지 않는다.** 확장 hit가 나려면 지금 그리는 스트림의 L바이트 FNV가 도구가 특정 그림에 붙인 p8과 같아야 한다. 그 위에 실루엣 검사가 있다. 그리고 오프라인 재계산에서 p8당 그림이 1개임을 독립 확인했다. 그래서 "맞는 프레임" 근거로 충분하다. 실제 화질은 업스케일 팩이 들어올 때 본다.
- **(d)** pair `trace_close FAIL`·`mirror_validator BLOCKED`는 기존 하네스 문제로 판정에 영향이 없다.
- 집계: 판정 영향 불일치 0, 정정 0, 보강 3(남은 충돌 = `bullk` 계열, 기본 이름 파일의 전역 충돌 0, refresh 때 p8 재계산), 공개 2(테스트 공백 c4·c9·p2, 확장 hit의 시각 검증은 stand-in 팩까지). 기본 켬·사용자 전달 아님. 마일스톤 경계 아님.

## 7. 다음 work 사전등록(Sonnet) — H-HDB2: `0x467B00` 클립 가중표 혼합 HD 키 경로

**정적 근거(이번 회차 `orig_467B00.asm`, 읽기 전용, 원본 SHA 일치).**
- 인자: thiscall ecx = renderer, 스택 5개(x·y·w·h는 하위 16비트 `movsx`, 다섯째 = 스트림 포인터), `ret 0x14`. 목적지 = `[ecx+0x1514] + y·[ecx+0x10] + x`.
- 클립: 사각형 `[ecx+0x4D0]` left·`+0x4D4` top·`+0x4D8` right·`+0x4DC` bottom이고, **오른쪽·아래는 포함 경계**다. `x+w−1 < left` 또는 `y+h−1 < top`이면 즉시 반환한다. 아래가 잘리면 그 행들은 **파싱하지 않는다**(행 수 = h − (y+h−1−bottom)). 위가 잘린 행은 **파싱하되 쓰지 않는다**. 열은 `x+col ∈ [left, right]`만 쓴다.
- 스트림 문법은 `0x467580`과 같다. `FE n` → col += n(2바이트)이고, 그 밖의 바이트는 1픽셀이다. 행은 col ≥ w에서 끝나고 스트림 위치는 행 사이에 이어진다.
- 혼합식도 `0x467580`과 같다. d = 목적지 바이트, s = 스트림 바이트이고, `t_k = movsx word [ecx + ((pal_d[k]<<6) + pal_s[k])·2 + 0x41CA0]`, 결과 `[ecx + ((t0<<6)+t1)<<6 + t2 + 0x19A0]`이다. 즉 **`0x467580` + renderer 클립**이다. 현재 diff 미러는 `mirror_blend_clip`(lap1024 H-B4)이고, 화면 교집합만 미러한다.
- 최근 run의 화면 안 호출 수(`blend_467B00_mirrored_calls`): X1 133·X2 335·T1 58. 전체 호출은 14~18만 회이고, 대부분 화면 밖이라 `reject_bounds`다.

**단계.**
- B2-0(테스트만, 이번 회차 생존 변이 막기): (p2) 그림 3개에서 작은 L은 하나만 가르고 큰 L은 셋 다 가를 때 큰 L을 고르는지, 어떤 L도 다 못 가르면 conflict로 남는지 확인하는 도구 테스트. (c4) ext 불량 마커 키 바로 뒤의 SKIP_AUX 또는 LUT_REJECT 키에서 `ext_rejects`가 늘지 않는지 확인하는 호스트 시나리오. (c9) 확장 HIT 키를 identity refresh로 다시 읽을 때 `ext_hits`가 그대로인지 확인하는 호스트 시나리오. 세 변이 모두 RED, 현재 GREEN이어야 한다.
- B2-1(C, `mirror_blend_clip`): H-HDB1 공유 코어 `blend_key_apply`(weights = `+0x41CA0`, writer id `0x467B00`)를 붙인다. 키 = 전체 스트림 사각형 (x, y, w, h)다. 자기 검사·그리기 영역 = 사각형 ∩ **원본 호출 전에 읽은** renderer 클립 사각형(포함 경계 → 반열림 `[left, right+1)×[top, bottom+1)`) ∩ 화면 `[0,800)×[0,600)`이다. 스냅샷은 원본 호출 전에 뜨고, 키 시도는 diff 미러 성공 뒤에 한다. 폴백 때는 diff 결과를 유지한다. 끔 env는 기존 `SYW2_G1_HD_PACK_BLEND=0`을 공유한다. 카운터 `blend_467B00_keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels` + `blend_467B00_key_clip_cut`(renderer 클립이 화면 교집합보다 좁아 영역이 잘린 keyed 호출)을 trace에 넣는다. 복제 코어 금지.
- B2-2(호스트 테스트, RED→GREEN): 클립 사각형이 화면보다 좁을 때(왼·위·오른·아래 각각) 키 그리기가 클립 안에만 머무는지, 오른쪽·아래 포함 경계, 위가 잘린 행의 스트림 연속성, 완전히 바깥이면 키를 시도하지 않는지 확인한다. 변이(클립 무시·오른쪽 배타 경계·클립을 원본 호출 뒤에 읽기·writer id 교체·weights NULL)는 RED여야 한다.
- B2-3(귀속): 키 로그의 `0x467B00` digest를 6개 폴더 `.spr` 프레임에 귀속한다(독립 헤더 파서, 미귀속 수 기록). 귀속된 파일로 팩을 만든다(team-safe 초안 stand-in, 확장 이름 포함).
- B2-4(run): (i) lap1190/1192 F0 구성(dwell 56)으로 켬 2 run과 같은 팩에 `SYW2_G1_HD_PACK_BLEND=0`인 끔 1 run. (ii) save006 pair 1회. (iii) 켬 두 run의 `0x467B00` 화면 안 호출 합이 300 미만이면, lap1022/1024에서 이 writer가 관측된 save000 pair 1회를 더한다.

**측정식(합격).**
- B2-0·B2-2 변이 전부 RED.
- B2-4(i): `0x467B00` 화면 안 호출 가운데 팩 귀속 키 호출의 keyed ≥95%(팩에 없는 파일 키는 따로 적음). 자기 검사 불일치 0. `key_clip_cut` ≥1(renderer 클립 경계가 실제로 시험됐다는 뜻; 0이면 그 항목만 SKIP으로 기록). 안전 7종·dropped 0. p95 ≤ 끔+2. stale ≤ 끔 규모. `0x467580` keyed·불일치는 lap1192 수준을 유지(비회귀).
- B2-4(ii) pair PASS. (iii)을 돌리면 화면 stale이 lap1024 H-B4 수치(p84..365 362.5)보다 나빠지지 않아야 한다.
- 안전: 원본 EXE SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 20 GB 미만이면 자기 회차 옛 사본부터 정리하고, 5 GB 미만이면 run을 시작하지 않는다.
- **비목표:** `0x4685C0`·`0x467FD0`(그다음 차례), 실제 업스케일 화질, 기본 켬·사용자 전달, 남은 충돌 3개.
- **중단:** 실패 가설 2회 또는 60분. 키 그리기가 클립 밖에 쓴 증거(자기 검사 불일치 급증·HUD 위 얼룩)가 나오면 즉시 끄고 근거만 남긴다. run 대기는 PID `kill -0` 또는 `.exit` 파일로 한다(`pgrep -f` 자기 일치 금지). 커밋 금지, 원본/참고 쓰기 금지. 산출물은 공유 temp `<날짜>_lap<N>_work_hdb2/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수) 순서로 한다.
- **backlog 추가:** 남은 충돌 3개 = `char/bullk*.spr` `86×60`(실제 유닛 팩 때 재판단).

## 8. 검사

- 검사 결과는 STATUS 검증 줄에 보강한다. 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1192 full PASS(2005 passed) 그대로이므로 전체 `make check`는 SKIP한다.

## 다음 행동

work(Sonnet) H-HDB2(§7)를 진행한다. 그다음 `0x4685C0`, `0x467FD0` 순이다. 사용자 G1 시험 결과가 오면 그것이 최우선이다.
