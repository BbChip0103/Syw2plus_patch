# 2026-10-08 | lap 1189 | G1 middle — H-HDB0 독립 검수 · H-HDB1(효과 반투명 ② `0x467580` 가중표 혼합 HD 키 경로) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 코드·source 수정 0, 게임 실행 0, 커밋 0.
- 입력: lap1188 work `loop/ESCALATE_SOL`(원문 byte 일치 보존 `docs/history/laps/20261008_lap1189_preserved_lap1188_escalate_sol.txt` SHA256 앞 16자 `feecce5a0803c176`, 보존 뒤 삭제), lap1187 사전등록 §5, lap1188 기록. INBOX·APPROVALS에 새 사용자 지시·반려·G1 시험 결과 없음. `loop/STOP` 없음.
- 원본 SHA: 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` read-only MATCH(이번 회차 직접 재계산). `fnt/imjin2plus.spr` SHA256 `5c278ffd…`(6,018 B). 디스크 여유 약 58 GB.
- 산출물(공유 temp `20261008_lap1189_middle_review/`): `recalc_lap1189.py`(`c55274b2…`)·`recalc_lap1189.json`(`851f759d…`)·`marker_lap1189.py`(`96d4b3a6…`)·`marker_lap1189.json`(`3769966b…`)·`mutation_lap1189.py`(`000a579f…`)·`mutation_lap1189.txt`(`7a2a4cbe…`)·`mutation_lap1189_b.py`(`7e5b0c50…`)·`mutation_lap1189_b.txt`(`6fbaf0c4…`). work 스크립트 `b_metrics.py`는 쓰지 않았다.

## 1. source 정체성

- SHA256 앞 16자 10개가 lap1188 기록과 모두 일치한다(`g1_blend_key.h dc58c1d5…`·`g1_hd_asset.c ba4d9b17…`·`.h a6dbb05c…`·`g1_mirror2x.c 8e57fd36…`·`.h 7cbfaff9…`·`direct_draw_trace.c af5c3391…`·`tools/g1_hd_convert.py 388d21cb…`·`tests/test_g1_blend_key.py cd07bbde…`·`test_g1_hd_pack.py 5e791ab6…`·`test_g1_hd_convert.py 4c06fb23…`).
- `logs/gates/lap1188-work-full-check.log` 이후 바뀐 tools·tests·patches·checks·Makefile 파일은 0개다(`find -newer` 0).

## 2. B-1 독립 확인(work 요청 1)

- **원본 역어셈블(`objdump`, 읽기 전용) `0x4672E0..0x467406`:** 인자는 word `movsx`로 읽는다(x `[esp+0x14]`·y·w·h, rle `[esp+0x24]`). 목적지 행 = `buffer[+0x1514] + y*stride[+0x10] + x`. 행 루프 `0x46732D..0x4673E3`는 `col < w`인 동안 토큰을 읽는다. `0xFE`이면 다음 바이트만큼 `col`을 더한다(0도 허용, 경계 검사 없음). 그 밖의 바이트는 소스 인덱스 s다. 채널 값은 `esi+3·idx+0x419A0/1/2`(= `0x2BBC0+0x15DE0`)에서 읽는다. 결과는 `inverse[esi+0x19A0 + (((dR>>1)+(sR>>1))<<12) + (((dG>>1)+(sG>>1))<<6) + ((dB>>1)+(sB>>1))]`이고 `row[col]`에 쓴다. 행 끝 표지와 길이 필드는 없다. `ret 0x14`. work 서술과 `g1_blend_key.h`의 디코더·식과 일치한다.
- **digest 귀속:** `imjin2plus.spr` 전체 오프셋을 전수 탐색했다. 128바이트 FNV-1a가 `3475a863`인 위치는 **`0xBF4` 하나뿐**이다. 독자 디코더(위 행 규칙)는 **2,958바이트를 소비하고 끝난다. 그 끝이 파일 끝과 같다(잔여 0)**. 불투명 픽셀은 **2,110**개이고 `FE 00` 토큰은 0개다. 팔레트 시작값은 0x3F 이하(6비트)라서 혼합 오프셋은 `< 0x40000`이다.
- **팩 프레임:** `pack_logo`·`pack_marker` `h3475a863_100x64.idx8`는 각각 25,600 B다. 불투명 부분픽셀은 8,440 = 2,110×4다. **1x 마스크 2배 실루엣과 어긋나는 부분픽셀은 0개다.** logo와 marker는 1,937 부분픽셀이 다르고, 그중 키(0xFE) 쪽 차이는 0이다. 즉 색만 다르다.

## 3. 코드 검수(work 요청 2)

- `mirror_blend_rle`(`g1_mirror2x.c` 4851행) 순서: 범위·크기 검사 → 1x before 사본 → (키 시도면) `covered` 사본과 HD 목적지 2w×2h 사본(`g_mirror`) → 원본 호출 → **diff 미러(`g1_overlay_blt_apply`)를 항상 실행** → 키 시도면 `blend_rle_key_apply`. `g1_overlay_blt_apply`는 `screen_hd`·`expected`·`covered`만 쓴다. 1x `after` 버퍼는 읽기만 하므로(`g1_overlay_blt.h` 49~108행) 자기 검사가 보는 1x 결과는 원본 출력 그대로다. **어느 단계에서 실패해도 diff 미러 결과가 남는다. 폴백 = 기존 동작이 성립한다.**
- 자기 검사는 마스크 안 식 일치와 마스크 밖 불변을 함께 본다. 팔레트·역 LUT·스트림 해석 중 하나라도 원본과 다르면 그 호출은 폴백한다. 디코드 한도 `pixels*2+h*2`는 행 규칙이 원본과 같으므로 원본이 이미 읽은 바이트 밖을 읽지 않는다. 한도를 넘는 스트림(`FE 00` 반복)은 실패로 처리된다. 버퍼 크기 `G1_OVERLAY_MAX_WIDTH×MAX_HEIGHT`(320×160, HD 사본 ×4)는 래퍼 크기 검사로 보장된다.
- covered 사본을 diff 미러 **전**에 뜨기 때문에, 이번 호출에서 처음 덮이는 픽셀은 Scale2x로 남는다. 보수적 선택이며 work 한계 3으로 공개됐다(실측 0). 팩 키 부분픽셀이 하나라도 있는 픽셀을 통째로 건너뛰는 규칙은 실루엣을 강제한 팩에서는 발생하지 않는다(위 실루엣 불일치 0).
- `g1_hd_asset_current_pack_frame`은 `pack_applied`인 키의 팩 프레임만 돌려준다. 끔 env는 `g_hd_blend_off` 하나로 키 시도만 끈다(diff 미러는 유지된다).
- **판정: 구조 충분.** 경미 1건: 팩 hit이면 `written`이 0이어도 `keyed`로 센다(이번 실측은 `keyed_pixels = selfcheck_pixels`라 영향 없음, 공개).

## 4. 변이(격리 사본 `/tmp/lap1189_mid_mut`, 저장소 무변경, 기준 148 passed)

대상: `test_g1_blend_key.py`·`test_g1_hd_pack.py`·`test_g1_mirror2x.py`·`test_g1_hd_convert.py`. work 8종과 독립으로 16종을 설계했다.

| 변이 | 결과 |
|---|---|
| k1 건너뛰기 +1 · k2 G 채널을 목적지에서 두 번 읽음 · k3 오프셋 경계 제거 · k8 디코드 한도 제거 | **RED** |
| k4 자기 검사 after 비교 제거 · k5 covered 게이트 제거 · k6 팩 키 부분픽셀도 씀 · k7 d=s | 처음 RED였으나 미사용 인자 경고 때문일 수 있어 **행동만 바꾼 변형 k4b~k7b를 다시 돌렸다 → 모두 의미 테스트로 RED**(`test_selfcheck_accepts…`·`test_apply_hd_blends…`) |
| x2 폴백 미집계 · x4 팩 프레임 크기 검사 제거 · x5(=lap1187 v3) 클립 반전 keyed 뒤 diff 미러 | **RED** |
| a1 끔 env 무시 · a2 팩 미적용 키에도 프레임 반환 · a3 blend hit 미집계 | **RED** |
| **x1** 래퍼에서 키 시도 호출 자체 제거(`if (key_try && 0)`) | **생존** |
| **x3** 자기 검사 불일치 뒤에도 계속 진행(`return FALSE` 제거) | **생존** |

- 생존 2 = 테스트 공백이다. 현재 코드는 맞다(4914행·4826~4827행). x3 상태라면 원본과 식이 어긋나도 HD에 덮어쓰게 된다. 실측 불일치는 0이라 이번 판정에는 영향이 없다. 다음 work 0단계에서 정적 계약 단언 2줄로 막는다(§7 B1-0).

## 5. 런타임 재계산(새 스크립트, candidate trace·키 로그·캡처)

| run | PS3 present·s | 호출 | keyed | 폴백 | 자기 검사 불일치/픽셀 | 호출당 | p95(중앙값) | PS3 stale | 팩 blend hit/miss | exit·status |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | 2,980·148.9 | 2,980 | 0 | 2,980 | 0 / 6,287,800 | 2,110 | 6 (4) | 없음 | 0/1 | 0·PASS |
| K1 | 3,053·152.6 | 3,053 | **3,053** | 0 | 0 / 6,441,830 | 2,110 | 6 (5) | 80.0:90 | 1/0 | 0·PASS |
| K2 | 2,967·148.9 | 2,967 | **2,967** | 0 | 0 / 6,260,370 | 2,110 | 7 (5) | 없음 | 1/0 | 0·PASS |
| O1(끔) | 2,982·149.0 | 2,982 | 0 | 0(시도 0) | — | — | 6 (4) | 77.5:283 | 0/0 | 0·PASS |
| M1(표식) | 2,981·149.0 | 2,981 | **2,981** | 0 | 0 / 6,289,910 | 2,110 | 6 (4) | 없음 | 1/0 | 0·PASS |

- work 수치를 전부 재현했다. 켬 run은 9,001/9,001(100%)이 keyed이고 폴백 0, `keyed_pixels = selfcheck_pixels`다. 5 run 모두 `identity_key_mismatches`·`clip_replay_mismatches`·`identity_invalid_sources`·`scale2x_palette_violations`·fallback·hresult≠0·success=0·evictions가 0이다. 키 로그의 로고 줄은 `3475a863 100×64`이고, 켬 run은 둘째 줄이 `hit`, B0는 `miss`, O1은 줄이 없다(키 시도 0).
- **로고 사각형(HD 1400..1599×754..881):** ps3_start·play·act·building·produce 5장 모두 B0~K1 = B0~K2 = **5,052~5,053 px**, K1~K2 = **0**이다. 같은 장면에서 사각형 밖은 17만~31만 px가 다르다(유닛·시각 차이). 반면 사각형 안은 매 캡처 같은 값이다. 로고가 HUD처럼 고정 위치에 다시 그려진다는 뜻이다.
- **표식 색(보강):** work는 K1과 M1을 그림으로 비교했는데, 두 run은 시작 맵 갈래가 다르다. 그래서 이번에는 **같은 갈래끼리** M1(표식)~O1(끔)을 수치로 비교했다. 로고 사각형 안 차이는 6,457~6,474 px이고, 차이 픽셀 평균 RGB는 O1 (82,73,73) → M1 (66,70,83)이다. 청색 우세 픽셀은 4,207 → 6,051로 늘었다. 같은 갈래 K1~B0(일반 stand-in 팩)은 평균 RGB 차이가 1 이하다. `logo_cmp_marker.png`도 열람했다. 붉은 뱀 모양이 푸르게 나오고, 흰 글자는 같고, 아래 지형이 비친다(반투명). → 교체 그림이 반투명으로 화면에 반영된 것을 확인했다.
- **stale:** K1 80.0 s 90 px 단발, 끔 O1 77.5 s 283 px 단발, B0·K2·M1은 0이다. 같은 시각대 단발은 lap1187 기준(변경 전 E2 76.7:90·U2 76.6:90)과 같은 값이다. 측정식(같은 시각 끔 규모 이하)을 충족한다. 위치(로고 안/밖)는 계측하지 않았다(공개).

### 정정(판정 영향 없음)

- **work 기록의 pair PB 서술 "키 로그에 로고 키 없음(저장 장면은 로고를 그리지 않음)"과 한계 4는 사실이 아니다.** `pair_PB.keys.jsonl`에는 `0x004672E0 3475a863 100×64` 줄이 20개 있다(`hit` 1, `draws` 최대 832). save006 장면도 로고를 그렸고, 키 경로가 팩 hit 상태로 실행됐다. 따라서 pair PB `PASS`(scene_state_equal·V2/V2s/V2q·Scale2x·input_effect·minimap parity)는 **키 경로가 켜진 상태의 비회귀 증거**다. 근거가 약해지는 것이 아니라 강해진다. 다만 pair candidate trace에는 `mirror2x_metrics` 집계 이벤트가 없다. `trace_close`가 `RuntimeSafetyError: owned Win32 PID trace has a mismatched run_id`로 FAIL했는데, 이것은 lap1182 pair P0과 같은 기존 하네스 현상이다. 그래서 PB의 keyed·자기 검사 카운터는 확인할 수 없다(공개).

### 사전등록 이탈(수용)

- 사전등록 B-3은 팩을 "lap1178 `pack_hdf1` + 로고 초안"으로 정했지만, work는 로고 1장 팩만 썼다. 그래서 로고 밑 목적지가 팩 HD 지형인 경우(d가 팩 그림)는 실게임에서 재지 않았다. 다만 식이 부분픽셀 단위이고 d의 출처와 무관하며, 호스트 테스트 `test_apply_hd_blends…`가 임의 HD 목적지로 검증한다. 그래서 판정 영향은 없다고 보고 수용한다. 기본 켬 전(묶음 시험판) 단계에서 전체 팩과 함께 다시 확인한다.

## 6. 판정

**H-HDB0 `PASS(partial, 기술·격리)` 수용.** 세부: B-0 PASS(v3=x5 RED 재현), B-1 PASS(역어셈블 독립 재확인, digest 오프셋 유일, 스트림 EOF 정확 소비, 불투명 2,110, 실루엣 불일치 0), B-2 PASS(구조 충분, 독립 변이 16종 중 RED 14, 생존 2 = 테스트 공백, 코드는 정상), B-3 PASS(partial)(keyed 100%, 자기 검사 불일치 0, 안전 0, p95 6/7/6 ≤ 끔 6+2, 로고 사각형 5,052 px 변화, 결정적 재현, 같은 갈래 표식 색 반영, stale ≤ 끔, pair PASS). 집계: 판정 영향 불일치 0, 정정 1(pair PB 로고 키 경로 실행), 보강 3(digest 전수 유일·EOF, 같은 갈래 표식 수치, 행동 변이 k4b~k7b), 공개 4(x1·x3 공백, stale 위치 미계측, PB 카운터 부재·trace_close 기존 FAIL, 팩 구성 이탈). 기본 켬·사용자 전달 아님. 마일스톤 경계 아님, 사용자 승인 해당 없음.

**다음 순서:** 반투명 계열을 계속한다(lap1187 결정: 변화량 순 `0x467580` → `0x467B00` → `0x4685C0` → `0x467FD0`).

- `0x467580` 역어셈블(이번 회차, `0x467580..0x4676BD`): 인자·목적지 행·스트림 행 규칙(`FE n` 건너뛰기, 폭 끝에서 행 종료)이 `0x4672E0`과 **같다**. 다른 점은 채널 결합 하나다. 채널마다 `t = (int16)T[(d<<6)+s]`이고, T는 renderer `+0x41CA0`의 64×64 16비트 표(`movsx`, 음수 가능)다. 결과는 `inverse[+0x19A0 + (t0<<12) + (t1<<6) + t2]`다. lap954 §5 서술과 일치한다.
- 기존 raw 변화량: lap1186 F0(장기 스크롤 306 s, 끔) 호출 1,332회, clipped 53(4.0%), mirrored 12.06 M px(호출당 약 9,050 px). U1은 30회·0.34 M이고, lap1188 K1(NG5 150 s)은 1회뿐이다. 장면 의존이 크므로 측정은 F0 구성(장기 스크롤)으로 한다.
- 디코더·자기 검사·HD 적용 골격을 그대로 쓰고 결합 함수만 바꾸면 된다. → **`FEASIBLE`**. 차이: (i) 표 값이 음수이거나 오프셋이 `[0,0x40000)` 밖이면 그 픽셀은 계산 불가로 거부한다(1x 자기 검사가 원본과 같은 식을 확인한다). (ii) 이 래퍼(`mirror_blend_wrle`)는 화면 일부가 밖으로 나간 사각형을 교집합만 미러한다. 키 경로도 교집합 오프셋을 다뤄야 한다. (iii) 소스 그림(구름/그림자 추정)의 `.spr` 귀속은 아직 없다.

## 7. 다음 work 사전등록(Sonnet) — H-HDB1: 효과(반투명) ② `0x467580` 가중표 혼합 HD 키 경로

**단계.**
- B1-0(테스트만): 이번 회차 생존 변이 2종을 막는 정적 계약을 추가한다. (a) `mirror_blend_rle`이 diff 미러 성공 뒤 `key_try`면 `blend_rle_key_apply`를 호출한다(x1). (b) `blend_rle_key_apply`가 자기 검사 실패 시 `return FALSE`로 끝난다(x3). x1·x3 변이에서 RED이고 현재 GREEN이어야 한다.
- B1-1(정적·호스트): `g1_blend_key.h`에 표 결합 함수 `g1_blend_table_offset/pixel`(채널별 `(int16)T[(d<<6)+s]`, 결과 오프셋이 음수이거나 ≥0x40000이면 거부)을 더한다. 기존 디코더·자기 검사·HD 적용은 결합 함수만 바꿔 공유한다(복제 금지, 모드 인자나 함수 포인터). 호스트 테스트는 원본 산술 재현(음수 T 포함), 거부, 자기 검사, 교집합 적용을 다룬다. 각 테스트는 변이에서 RED여야 한다.
- B1-2(C): `mirror_blend_wrle`에 키 시도를 넣는다. 조건은 `g1_hd_asset_blend_key_path()`이고 끔 env를 공유한다(`SYW2_G1_HD_PACK_BLEND=0`). 원본 호출 전 교집합의 covered·HD 목적지 사본을 뜨고, diff 미러 뒤 디코드 → 교집합 자기 검사 → `g1_hd_asset_begin(…, <0x467580 writer id>, w, h, x, y)`·identity 바인드 → 팩 hit이면 교집합만 HD 혼합으로 덮어쓴다. 실패하면 폴백(diff 결과 유지)하고 사유를 계수한다. digest는 사각형 전체 스트림 기준이다(클립과 무관한 키). trace에 `blend_467580_keyed_calls/keyed_pixels/key_fallbacks/selfcheck_mismatches/selfcheck_pixels`를 더한다.
- B1-3(귀속): 키 시도·빈 팩 run의 키 로그에서 `0x467580` digest·크기를 모은다. `g1_hd_convert.py`(필요하면 `logo` 계열 확장)로 원본 `.spr`에서 같은 digest를 찾아 팩 stand-in을 만든다. **귀속이 0개면 BLOCKED로 기록하고 B1-4는 키 시도만(빈 팩) 수행한다.** 자기 검사·폴백 무해성은 그것만으로도 측정한다.
- B1-4(run): lap1186 F0 구성(`--new-game-path --new-game-start --new-game-act --new-game-play` + `--new-game-play-keys/-hold/-dwell` 장기 스크롤 ≥300 s)으로 켬 2 run, 끔 1 run(같은 구성), 키 시도·빈 팩 1 run(B0 대응), save006 pair 1회.

**측정식(합격).**
- B1-0: x1·x3에서 RED, 현재 GREEN. B1-1: 호스트에서 원본 산술 재현, 변이 RED.
- B1-4 켬: `0x467580` 화면 안 호출 중 keyed ≥95%(clipped 포함, 폴백 사유 기록). 자기 검사 불일치 0(1이라도 있으면 FAIL, 원인 추적). 안전 7종·fallback·dropped 0. PS3 p95 ≤ 끔 +2 ms. 같은 시각 대조로 stale ≤ 끔 규모(§5 기준). 끔 run은 keyed 0. save006 pair PASS. 호출이 run당 300회 미만이면 표본 부족으로 기록하고 부분 판정만 한다(장면 의존, F0 1,332회 기준).
- 표식 팩(색 맞바꿈)이 가능하면 1 run을 같은 갈래 끔 run과 비교해 색 반영을 수치로 남긴다. 시작 맵 갈래(키 수 ~750/~1,340)를 run마다 기록하고, 다른 갈래끼리는 픽셀 비교하지 않는다.
- 원본 EXE SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 여유 20 GB 미만이면 자기 회차 옛 사본부터 정리하고, 5 GB 미만이면 run 시작 금지.
- **비목표:** `0x467B00`·`0x4685C0`·`0x467FD0`(다음 순서), 실제 업스케일 화질, 기본 켬·사용자 전달, `0x467410`·`0x4676D0`(미관측 형제).
- **중단:** 실패 가설 2회 또는 60분. 표 T가 present 사이에 바뀌는 증거(자기 검사 불일치 발생)가 나오면 키 경로를 멈추고 근거만 남긴다. run 대기는 PID `kill -0`·`.exit` 파일. 커밋·원본/참고 쓰기 금지. 산출물은 공유 temp `<날짜>_lap<N>_work_hdb1/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **backlog 추가:** 팩 hit·written 0 호출의 keyed 집계(경미), pair trace `trace_close` run_id 불일치 FAIL(기존 하네스, lap1182 P0 동일), 기본 켬 전 전체 팩(`pack_hdf1`+로고) 동시 실게임 확인.

## 8. 검사

- 검사 결과는 STATUS 검증 줄에 보강한다. 전체 `make check`는 SKIP한다. 이번 회차는 문서와 공유 temp 스크립트만 바꿨고, tools·tests·C source는 lap1188 full PASS(1979 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDB1(§7)을 진행한다. 사용자 G1 시험 결과가 오면 그것이 최우선이다.
