# 2026-10-08 | lap 1187 | G1 middle — H-HDU1 독립 검수(⑥ 마감) · H-HDB0(효과 반투명 `0x4672E0` HD 혼합 키 경로) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 코드·source 수정 0, 게임 실행 0.
- 입력: lap1186 work `loop/ESCALATE_SOL`(원문 byte 일치 보존 `docs/history/laps/20261008_lap1187_preserved_lap1186_escalate_sol.txt` SHA256 앞 16자 `1f1ebb6048aa21ac`, 보존 뒤 삭제), lap1185 사전등록 §5, lap1186 기록. INBOX·APPROVALS에 새 사용자 지시·반려·G1 시험 결과 없음(19:3x HD 그림 경로 지시 ⑥-2 단계). `loop/STOP` 없음.
- 원본 SHA: 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` read-only MATCH(이번 회차 직접 재계산). 디스크 여유 64 GB.
- 산출물: 공유 temp `20261008_lap1187_middle_review/` — `corr_lap1187.py`(`a44fc03e…`)·`corr_lap1187.json`(`e64ea995…`)·`corr_lap1187_attempt1.json`(`8ac052ad…`)·`mutation_lap1187.py`(`5dd8e1f4…`)·`mutation_lap1187.txt`(`6d6d2228…`).

## 1. source 정체성

- source SHA256 앞 16자 6개가 lap1186 기록과 일치(`g1_hd_asset.c 2e81f935…`·`.h 4f9b2f5a…`·`g1_mirror2x.c 1a12e15f…`·`.h 4f5f4e75…`·`direct_draw_trace.c b398b2e5…`·`tests/test_g1_hd_pack.py 14b9e2e5…`). `logs/gates/lap1186-work-full-check.log` 뒤 바뀐 tools·tests·patches·checks·Makefile 0(`find -newer` 0).
- run별 측정 DLL 소스(`bridge/`): U1·U2·U3·F0·F1·pair PU 모두 위 5개 C 파일이 현재 source와 byte 동일.

## 2. 코드 검수(work 요청 2)

- `mirror_flip_clip`(`g1_mirror2x.c` 4429행): `active`는 `g1_flip_rle_region`이 화면 교집합을 돌려줄 때만 켜진다. `region.wrap`은 사각형이 `[0,stride)×[0,600)`을 벗어나기만 해도 켜지는 표시라, viewport로 자르는 이 writer에서는 "가장자리 스프라이트" 자체다. 실측 U1 wrap 6,721 중 reject_bounds 6,713(화면 밖), 나머지 8 = 화면 안 클립 호출. 따라서 `!region.wrap` 제외는 오류였고 제거가 맞다.
- 키 경로 조건 SHORT 범위·1≤w≤800·1≤h≤600은 `mirror_reinvoke`의 `origin_x/y = (SHORT)args`·`width ≤ G1_CACHE_WIDTH`·`height ≤ 600` 전제와 맞는다. 원본 호출 1회 → `mirror_reinvoke(…, G1_FLIP_CLIP, TRUE)`(scratch 재호출은 trampoline 직접 호출이라 재귀 없음, `g_primitive_guard`로 중첩 차단) → `g_reinvoke_composed`일 때만 diff 미러 생략. 순서·guard는 `mirror_tinted_clip_rle`(3827행)과 같다. ready가 아니면 기존 diff 미러로 간다. **충분하다고 판정.**
- **변이(격리 사본 `/tmp/lap1187_mid_mut`, 저장소 무변경).** 대상 `test_g1_hd_pack.py`+`test_g1_mirror2x.py`. 사본 기준 101 passed + 1 failed(`test_p4b_cache_layer_hooks…` = 사본에 `analysis/` 미복사로 인한 FileNotFoundError, 저장소에서는 PASS 확인) → 아래 RED는 그 1개를 뺀 수.

| 변이 | 내용 | 결과 |
|---|---|---|
| m3 | 기존 키 hit 때 `last_draw` 갱신 제거 | **RED 1** (`test_key_table_full_keeps_a_key_that_was_begun_again_over_an_older_one`) |
| m5 | `build_hd_frame`의 `make_room_for(hd_bytes, key)`→`NULL` | **RED 1** (`test_cache_budget_too_small_for_the_hd_frame_fails_the_bind_instead_of_evicting_the_key_being_built`) |
| v1 | `is_flip_pack_writer`에서 `G1_HD_FLIP_CLIP` 제거 | **RED 2** |
| v2 | 래퍼 조건에 `!region.wrap` 복원 | **RED 1** |
| v3 | keyed 뒤 `active = FALSE` 제거(키 합성 뒤 diff 미러도 실행) | **생존** |
| v4 | `mirror_reinvoke(…, TRUE)`→`FALSE` | **RED 1** |
| v5 | `key_fallbacks` 증가 제거 | **RED 1** |

  - lap1185 테스트 공백 m3·m5는 닫혔다(work U1-0 재현).
  - v3 생존 = 새 공백 1. 현재 코드는 맞다(4503행). 변이 상태면 키 합성한 HD 위에 같은 사각형의 Scale2x diff가 다시 덮여 화질만 떨어진다(안전 영향 없음). 다음 work 0단계에서 정적 계약 단언 1줄로 막는다(§5).

## 3. 런타임 재계산(새 스크립트, candidate trace·키 로그)

| run | PS3 present·s | 화면 안 클립 반전 keyed / diff / 폴백 | wrap / reject_bounds | 키 `0x466BE0` lut_hit | p95 | 안전 7종·fallback·evictions | PS3 stale(초:px) |
|---|---|---|---|---|---|---|---|
| U1 | 6,113·305.8 | **12** / 0 / 0 | 6,721 / 6,713 | 3 | 6 | 0 | 13.2:135, 15.4:116, 15.4:91, 15.5:305, 141.2:79, 141.4:92, 225.5:79 |
| U2 | 6,117·305.8 | **2** / 0 / 0 | 8,568 / 8,566 | 2 | 6 | 0 | 76.6:90 |
| U3 | 6,119·305.9 | **2** / 0 / 0 | 8,483 / 8,481 | 2 | 7 | 0 | 없음 |
| F0(끔) | 6,112·305.8 | 0 / 14 / — | 8,257 / 8,247 | — | 6 | 0 | 13.4:59, 15.5:77, 141.2:2, 225.5:2 |
| F1(끔) | 6,115·305.7 | 0 / 2 / — | 6,941 / 6,939 | — | 7 | 0 | 15.4:22 |
| attempt1 U1(참고) | 6,114·305.9 | 4 / 10 / 0 | 6,879 / 6,869 | 3 | 6 | 0 | 15.5:18, 141.2:2, 141.3:79, 225.5:2, 225.5:79 |

- work 수치 전부 재현: 켬 16호출 100% keyed·폴백 0·reject_size/guard/target 0, 키 7개 전부 첫 bind `lut_hit`, 키 로그 신규 키 수 = trace `identity_keys`(1164·776·789·1214·742), p95, 안전 0, run exit 0·status PASS. pair PU `PASS`(scene_state_equal·input_effect·minimap parity·V2/V2s/V2q·Scale2x PASS).

### stale 판정(work 요청 3) — 시각 상관을 기존 raw로 수행

키 로그 줄 순서는 신규 키 생성(`draws 1`) 순서와 같고, 그 누적 수가 trace의 present별 `identity_keys`와 일치하므로(5 run 모두 최종값 일치) 각 `0x466BE0` 키 사건을 present 시각 창으로 옮길 수 있다(`corr_lap1187.py`). 따라서 (b) 상관 probe는 새 run 없이 수행했다.

| run | `0x466BE0` 키 사건(초) | 같은 시각 stale |
|---|---|---|
| U1 | 77.3(첫 draw·lut_hit 2키), 141.2~141.3(재draw), 141.3~161.8(draw 4), 225.5(새 키 lut_hit) | 77.3 없음 · **141.2:79·141.4:92** · **225.5:79** |
| U2 | 75.4~76.6(32×32 2키) | **76.6:90** |
| U3 | 98.8(2키) | 없음 |
| attempt1 | 141.3(110×80 2키), 225.5~225.6 | **141.3:79** · **225.5:79**(같은 시각 2 px도) |

1. **15.5 s 305 px(측정식 단발 >264)는 이 변경과 무관하다.** U1의 첫 `0x466BE0` 키 사건은 77.3 s다. 15.5 s에는 키 경로가 한 번도 실행되지 않았다. 13~15.5 s 군집은 선택 동작 시점의 기존 일시 stale이며, 변경 전·끔 run에도 있다(E1 59+264, E3 246+59+235+77+18, K3 59, E2 67, F0 59+77, F1 22, U2·U3 0). U1 합 647은 E3 합 635와 같은 규모다.
2. **15.5 s 뒤 합 250(>110)은 클립 반전 유닛이 화면 가장자리에 나타나는 장면 사건과 시각이 겹친다. 하지만 키 경로 고유 결함은 아니다.** 근거: (a) 키 경로가 없던 변경 전 소스 E1(diff 미러)도 같은 시각 141.1·141.3 s에 **같은 값 79·92**를 냈다(lap1185 재계산). E2(변경 전·축출 없음) 76.7 s 90은 U2 76.6 s 90과 값이 같다. (b) 79 px는 스프라이트 80×60(U1)과 110×80(attempt1)에서 똑같다. 스프라이트 내용이나 키 HD 합성에서 생긴 결함이면 크기에 따라 달라야 한다. (c) 모두 다음 present에서 사라지는 단발(≤92 px, 0.02%)이다. 같은 시각 diff run의 값은 2 px(F0·E3) 또는 79/92 px(E1)로 갈린다. 쌍봉 분포가 경로와 무관하게 나타난다.
3. **측정식 정정:** 사전등록 "15.5 s 뒤 합 ≤110"은 K2·K3(이 장면 사건이 2 px였거나 없던 run)만 보고 정했다. 변경 전 E1도 같은 창에서 281로 이 기준을 넘었다. 기준이 기존 변동 폭보다 좁았다. 판정은 "같은 시각에 변경 전 diff run에도 같은 값이 있는가"로 대체하고, 그 기준으로 **충족**한다.
4. **남는 불확실성(공개):** 79/92 px 쌍봉이 어떤 run에서 나는지는 설명하지 못한다. stale 사각형 위치를 계측하지 않았다. 클립 반전 가장자리 등장 시 1 present 일시 stale는 경로와 무관한 기존 현상으로 backlog에 둔다(위치·writer 귀속 UNKNOWN).

## 4. 판정

**H-HDU1 `PASS(partial, 기술·격리)` 수용.** U1-0 PASS(m3·m5 RED 재현), U1-1 PASS(호스트 GREEN, 독립 변이 6종 중 RED 5, 생존 1 = v3 테스트 공백, 코드는 정상), U1-2 PASS(partial): 키 경로 100%·폴백 0·안전 0·p95 6/6/7·끔 대조 keyed 0·pair PASS. stale 측정식은 §3 정정으로 충족한다. 판정에 영향을 주는 불일치 0, 정정 1(측정식 기준), 보강 2(시각 상관·15.5 s 무관 확정), 공개 3(v3 공백, 79/92 쌍봉 미설명, 표본 16호출). 기본 켬·사용자 전달 아님. 마일스톤 경계 아님, 사용자 승인 해당 없음.

**⑥ 마감.** 유닛 경로(`0x466B50`·`0x466BE0` 키 경로화)와 메모리 대책(H-HDK0)을 모두 수용했다. 19:3x 지시 ①~⑥은 기술·격리 수준에서 닫힌다.

**다음 순서 결정(19:3x "효과(반투명)는 후순위; 그 middle이 계속 여부 결정").** 계속한다. 근거:
- DESIGN G1: "교체한 그림이 800×600 최종 버퍼로 축소됐다 다시 확대되는 구조는 G1 합격 경로로 보지 않는다." 반투명 writer는 지금 800×600 결과를 Scale2x로 diff 미러한다. 사용자가 교체한 그림도 이 경로에서는 그 구조가 된다.
- 기존 raw로 잰 남은 그림 writer 화면 변화량(U1·F0, PS3 306 s 기준, `mirror2x_metrics` `*_mirrored_pixels`): `0x4672E0` **12.56 M/12.54 M**(매 present 1회, HUD 로고 100×64), `0x467580` 0.34 M/**12.06 M**(장면 의존), `0x467B00` 0.18 M/2.97 M, `0x4685C0` 1.38 M/0.08 M, `0x467FD0` 0.20 M/0.10 M. 단색 채우기(`0x465FC0`·`0x465E80`)는 그림이 아니다. 반투명 계열이 남은 그림 경로 중 가장 크다. 그중 `0x4672E0`은 매 present 같은 위치에 그려져 측정이 결정적이다.
- 혼합식은 이미 정적으로 확정됐다(`analysis/memory_maps/g1_blend_writers_4672e0_467580_lap953.md` §2·§5). `0x4672E0` = 목적지 의존 50% 평균: 채널마다 `(d>>1)+(s>>1)`. 채널 값은 renderer `+0x419A0` 팔레트 표에서 읽고, 결과는 역 LUT `+0x19A0`으로 조회한다. 두 표는 H-HDS1 음영 LUT와 같은 입력이고, 시작 때 1회만 구축된다(lap1179). HD 미러는 같은 팔레트의 인덱스 버퍼다. 따라서 HD 결과 = 역LUT[avg(HD 목적지, HD 팩 소스)]를 subpixel마다 계산할 수 있다 → `FEASIBLE`.

## 5. 다음 work 사전등록(Sonnet) — H-HDB0: 효과(반투명) ① `0x4672E0` HD 혼합 키 경로

**단계.**
- B-0(테스트만): `tests/test_g1_hd_pack.py` 또는 `test_g1_mirror2x.py`에 정적 계약 1줄 — `mirror_flip_clip`이 keyed 뒤 diff 미러를 건너뛴다(`active = FALSE`). 이 회차 변이 v3에서 RED, 현재 GREEN.
- B-1(정적·호스트): `0x4672E0` 본체(`0x46734D..0x4673CF`) 역어셈블로 RLE 행 구조(행 끝·건너뛰기 `0xFE n`)를 확정하고, 1x 디코더를 쓴다. 이 디코더는 소스 인덱스와 마스크를 낸다. 스트림 길이를 정해 digest `(digest, w, h)` 이름을 만든다. 원본 `.spr`·기존 추출물(lap1157)에서 같은 digest를 찾아 로고 프레임을 귀속한다. 도구 `pack`에 이 writer 이름 규칙을 더한다. 찾지 못하면 `BLOCKED`로 기록하고 B-2로 가지 않는다.
- B-2(C): 래퍼 `mirror_blend_rle`에 키 경로를 넣는다. 조건은 팩 켬·이름 hit·renderer 표 digest 유효다. 원본 호출 1회 뒤 HD 소스 subpixel이 불투명인 곳만 HD 미러 = 역LUT[채널별 (d>>1)+(s>>1)]로 쓴다. d = 현재 HD 미러 subpixel, s = 팩 프레임 인덱스다. **자기 검사:** 같은 호출에서 1x 디코더 소스와 before 버퍼로 같은 식을 계산해 원본 출력과 비교한다. 불일치가 1개라도 있으면 그 호출은 기존 diff 미러로 폴백하고, 사유를 계수한다. 끔 env `SYW2_G1_HD_PACK_BLEND=0`. trace에 `blend_4672E0_keyed_calls`·`_key_fallbacks`·`_selfcheck_mismatches`·`_selfcheck_pixels`를 더한다. 호스트 테스트: 혼합식 hit, 자기 검사 불일치 → 폴백, 끔 env, 팩 miss → 기존 경로. 각각 수리 전 RED·후 GREEN·변이 RED.
- B-3(run): 팩 = lap1178 `pack_hdf1` + 로고 team-safe 초안 1장. 화질 평가가 아니라 경로 검증이다. NG5(`--new-game-path --new-game-start --new-game-act --new-game-play`, PS3 ≥120 s) 켬 2 run + 끔(`SYW2_G1_HD_PACK_BLEND=0`) 1 run, save006 pair 1회(비회귀).

**측정식(합격).**
- B-0: v3에서 RED, 현재 GREEN. B-1: 디코더 1x 결과가 원본 실행 결과와 일치한다(호스트에서 원본 혼합식 재현 또는 실게임 자기 검사 불일치 0). 로고 digest 귀속 1개 이상.
- B-3 켬: PS3 present당 `0x4672E0` 호출 중 keyed ≥95%, 자기 검사 불일치 0, 폴백은 사유를 기록한다. 안전 7종·fallback·dropped 0. PS3 p95 ≤ 끔 대조 +2 ms. 로고 사각형(x700..799·y377..440 → HD 2배) 캡처가 끔 run과 다르다 = HD 소스가 실제로 화면에 반영됐다. 로고 밖 stale는 끔 run 규모를 넘지 않는다. 같은 시각 비교로 판정한다(§3 기준). 끔 run: keyed 0, 기존 diff 미러 수치와 같은 규모. save006 pair PASS.
- 원본 EXE SHA 전후 불변, game 사본 삭제, prefix·manifest·output 보존. 디스크 여유 5 GB 미만이면 run 시작 금지(현재 64 GB).
- **비목표:** `0x467580`·`0x467B00`·`0x4685C0`·`0x467FD0`(다음 순서, 변화량 순), 실제 업스케일 화질, 기본 켬·사용자 전달, 활성 8인 부하.
- **중단:** 실패 가설 2회 또는 60분. B-1에서 RLE 구조나 digest 귀속이 안 되면 `BLOCKED`로 근거만 남긴다. 그때 B-0만 남기고, 다음 middle이 `0x467580`으로 순서를 바꿀지 정한다. run 대기는 PID `kill -0`·`.exit` 파일(INBOX 12:47 규칙). 커밋·원본/참고 쓰기 금지. 산출물 공유 temp `<날짜>_lap<N>_work_hdb0/`. C 변경이 있으므로 lap 기록 → `make lint`·`make typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).
- **backlog 추가:** 클립 반전 유닛 가장자리 등장 1 present stale 79/92 쌍봉(경로 무관, 위치 UNKNOWN), 15.5 s 선택 군집 최대값 변동(18~305).

## 6. 검사

- 검사 결과는 STATUS 검증 줄에 보강한다. 전체 `make check` SKIP: 이번 회차는 문서와 공유 temp 스크립트만 바꿨다. tools·tests·C source는 lap1186 full PASS(1965 passed) 그대로다.

## 다음 행동

work(Sonnet) H-HDB0(§5). 사용자 G1 시험 결과가 오면 그것이 최우선이다.
