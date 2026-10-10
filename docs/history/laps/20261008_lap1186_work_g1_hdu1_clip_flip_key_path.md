# 2026-10-08 | lap 1186 | G1 work — H-HDU1 ⑥-2: `0x466BE0` 클립 반전 유닛 키 경로 + H-HDK0 회귀 테스트 2개

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1185 middle 사전등록 §5(`20261008_lap1185_middle_g1_hdk0_review_hdu1_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 74 GB, 끝 65 GB.
- 가설: `0x466BE0`은 `0x466B50`의 클립 형제라 `0x466540`(tinted clip)과 같은 viewport replay 키 경로에 flip writer로 얹을 수 있다. 가장자리에서 잘린 반전 유닛은 지금 diff 미러(Scale2x 품질)로 그려진다.
- 예상 PASS/FAIL: 사전등록 §5 측정식(U1-0 변이 RED·U1-1 호스트 테스트·U1-2 키 경로 ≥90%·p95 ≤8·안전 0·stale 규모·pair PASS).

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tests/test_g1_hd_pack.py` | **U1-0** 테스트 2개: `lru_recency`(키 A 재-begin 뒤 다른 키가 현재 키가 되면 새 키는 A가 아니라 B를 축출) · `build_self`(캐시 20 B 한도에서 identity 8 B는 들어가고 HD 16 B는 못 들어갈 때 bind가 실패하고 자기 identity를 축출하지 않음, `invalid_sources` +1·캐시 0 복귀). **U1-1** 호스트 테스트: `clip_flip_*`(hit·miss·bad_digest·off = 기존 flip 시나리오를 writer `0x466BE0`로), `flip_writers_apart`(writer가 키 정체성에 들어감), 클립 래퍼 정적 계약, trace 필드 |
| `tools/inmm_stub/g1_hd_asset.c`·`.h` | `G1_HD_FLIP_CLIP 0x00466BE0u` 추가, `is_flip_pack_writer`가 두 writer를 받음(팩 반전·반전 마스크 검사·LUT·`SYW2_G1_HD_PACK_FLIP=0` 끔을 `0x466B50`과 공유, 새 env 없음) |
| `tools/inmm_stub/g1_mirror2x.c`·`.h` | `invoke_original`에 `G1_FLIP_CLIP` 분기, `mirror_flip_clip`이 원본 호출 뒤 `active && g1_hd_asset_flip_key_path()`이고 x,y가 SHORT 범위·1≤w≤800·1≤h≤600이면 `mirror_reinvoke(…, G1_FLIP_CLIP, clipped=TRUE)`(전체 스프라이트 사각형, viewport replay로 written 마스크) → 준비되면 keyed, 아니면 기존 diff 미러(`key_fallbacks`). 카운터·접근자 `keyed_calls`·`key_fallbacks` |
| `tools/inmm_stub/direct_draw_trace.c` | 트레이스 `flip_clip_466BE0_keyed_calls`·`_key_fallbacks`(버퍼 480→560) |

파일 SHA256 앞 16자(최종): `g1_hd_asset.c 2e81f935f249eb2b`·`.h 4f9b2f5a3abc6d6d`·`g1_mirror2x.c 1a12e15f4ba5a32b`·`.h 4f5f4e75393b68ff`·`direct_draw_trace.c b398b2e5ba9d5db9`·`tests/test_g1_hd_pack.py 14b9e2e5aa9c4b3f`.

## 측정 (산출물 공유 temp `20261008_lap1186_work_hdu1/`, 팩 = lap1178 `pack_hdf1`, 하네스 = lap1184 장기 스크롤 NG5 `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 60`, 한도 기본)

- **원본 보호:** 원본 EXE `b56986e0…` 전·후 MATCH. game 사본 삭제(중단 attempt 1의 U2 사본 포함), prefix·manifest·output 보존.
- **U1-0 (테스트만, 동작 변경 0):** 새 테스트 2개 현재 코드 GREEN. lap1185 변이 재현: m3(hit 때 `last_draw` 갱신 제거) 기존 테스트 52 passed(생존) → 새 `lru_recency` **RED**, m5(`build_hd_frame`이 `make_room_for(…, NULL)`) 기존 생존 → 새 `build_self` **RED**. 기존 `evict_keys` 시나리오가 m3를 못 잡은 이유: 만진 키가 곧 현재 키라 축출에서 제외됨(현재 키 보호). 새 시나리오는 만진 뒤 다른 키(s2)를 현재 키로 만들어 최근성만 남긴다.
- **U1-1 호스트 테스트 변이:** (u1) 클립 writer를 flip writer에서 제거 → `clip_flip` hit RED. (u2) `read_pack_frame`의 팩 반전을 `0x466B50`에만 → RED. (u3) 래퍼 `G1_FLIP_CLIP, TRUE`→`FALSE` → 정적 계약 RED. (u4) 아래 attempt 1의 `!region.wrap`을 되돌림 → RED. 파일 전체 57 passed, `make lint`·`make typecheck` PASS.
- **attempt 1 (가설 1 실패, 수정):** 첫 구현은 mirror_flip_rle처럼 `!region.wrap`을 조건에 뒀다. run U1: 화면 안 클립 반전 호출 14회 중 **키 4(28.6%)·diff 10**(전부 `region.clipped`). `g1_flip_rle_region`의 `wrap`은 사각형이 [0,stride)×[0,600)을 벗어나기만 해도 켜지는데, 이 writer는 wrap하지 않고 viewport로 자른다 → 가장자리 스프라이트를 모조리 제외하고 있었다. `!region.wrap` 제거(정적 테스트로 고정). attempt 1 산출물은 `attempt1_wrap_condition/`에 보존, 측정식 근거로 쓰지 않는다.
- **U1-2 (현재 source, 켬 U1·U2·U3, 끔 F0·F1 `SYW2_G1_HD_PACK_FLIP=0`, 모두 candidate·baseline PASS, PS3 306 s):**

| run | 클립 반전 화면 안 호출 | keyed | 폴백 | `lut_hit` 키 | stale(PS3 present, 초:px) | p95 | 안전·fallback·dropped | 팩 reject |
|---|---|---|---|---|---|---|---|---|
| U1 | 12 (클립 8) | **12** | 0 | 3 | 13.2:135, 15.4:116, 15.4:91, 15.5:**305**, 141.2:79, 141.4:92, 225.5:79 | 6 | 0 | 1 |
| U2 | 2 (클립 2) | **2** | 0 | 2 | 76.6:90 | 6 | 0 | 2 |
| U3 | 2 (클립 2) | **2** | 0 | 2 | 없음 | 7 | 0 | — |
| F0(끔) | 14 (클립 10) | 0 | — | — | 13.4:59, 15.5:77, 141.2:2, 225.5:2 | 6 | 0 | 0 |
| F1(끔) | 2 (클립 2) | 0 | — | — | 15.4:22 | 7 | 0 | 2 |
| attempt1 U1(참고) | 14 | 4 | 0 | — | 15.5:18, 141.2:2, 141.3:79, 225.5:2, 225.5:79 | 6 | 0 | — |

  - **키 경로 처리율:** 켬 3 run 합 화면 안 16호출 중 키 경로 **16 (100%, ≥90%)**, 폴백 0, `reject_size`·`reject_guard`·`reject_target` 0. 키 로그의 `0x466BE0` 키 7개(80×60 5·32×32 2; U1 3·U2 2·U3 2)는 전부 첫 bind에서 `lut_hit`(reject 0), 같은 키 재draw는 hit 유지. `identity_invalid_sources` 0·`identity_lookup_misses`·`identity_key_mismatches`·`hd_mask_outside_diff_subpixels`·`scale2x_palette_violations` 0.
  - **p95:** 켬 6·6·7, 끔 6·7 (≤ lap1184 대조 6 + 2 = 8 충족).
  - **stale 측정식(단발 ≤264 px·15.5 s 뒤 합 ≤110):** U2(90)·U3(0)·끔 F0(77)·F1(22) 충족. **U1은 문자 그대로 미충족**: 15.5 s에 305 px(>264), 15.5 s 뒤 79+92+79=250(>110). 모두 다음 present에서 소멸하는 단발이며 최대 0.064%(305/480000).
  - **귀속 단서와 한계:** U1의 141.2:79·141.4:92·225.5:79는 같은 장면 시나리오(결정적 스크롤)의 141 s·225 s 전환 시점에 반복되고, 크기가 **이 변경 전** lap1184 E1(141.1:79·141.3:92)과 attempt 1(키 4, 141.3:79·225.5:79)에도 있다. 반대로 F0·E3·U2·U3에는 없거나 2 px다 → 이 변경만의 증상이 아님을 시사하나 n이 작아 배제는 못 한다. 15.5 s select 군집(U1 135/116/91/305)은 대조 군집(E1 264, E3 246/235, F0 77)과 같은 시점·같은 패턴이지만 U1이 최댓값을 넘는다. **U1이 클립 반전 호출이 가장 많았던 run(12 vs 2~4)이기도 해서**, 키 경로가 stale 원인이라는 가설을 이 표본으로 반증할 수 없다(UNKNOWN). 구체 stale 사각형·writer 귀속은 하지 않았다.
- **save006 pair(`pair.sh PU`, 팩 env, 한도 기본):** status **PASS**·scene_state_equal true·V2/V2s/V2q/Scale2x PASS·input_effect PASS (비회귀 용도).

## 판정

- **U1-0 PASS**(새 테스트 2개: 현재 GREEN, 변이 m3·m5 RED). **U1-1 PASS(기술)**(호스트 GREEN·변이 RED 4, 래퍼 구조 정적 검사).
- **U1-2: 키 경로 ≥90%(100%)·안전 0·p95·pair·끔 대조(키 0) 충족, stale 규모 측정식은 U1 1 run이 문자 그대로 미충족** → 전체 판정 **`PASS(partial, 기술·격리)` 보류, stale는 UNKNOWN**. 근거가 서로 충돌하지 않지만(키 경로 정상 동작) 합격식 일부 미충족이라 이 회차에서 임의로 닫지 않고 middle 판정을 요청한다. 기본 켬·사용자 전달 아님(팩 env 실험 경로). 마일스톤 경계 아님.

## 한계·공개

1. 화면 안 클립 반전 호출은 run마다 2~14회로 적다(임의 게임·idle 장면). 키 경로 100%는 16호출 표본이다.
2. stale 귀속은 시도하지 않았다(필요하면 클립 반전 호출 시각과 stale present의 시각 상관 계측이 다음 probe).
3. 팩이 없는 반전 키(`miss`)·클립 identity reject 경로는 실게임에서 관측되지 않았다(호스트 테스트만).
4. 기본 켬 빌드(`SYW2_G1_DEFAULT_ON`) 재빌드·사용자 전달은 하지 않았다.
5. backlog(lap1185) 그대로: 141 s 축출 연관 stale, 재등장 첫 bind 클립 identity reject, 스테이지 재진입 키 누적, `last_draw` 순환.

## 다음 행동

middle(Opus)이 U1 stale를 어떻게 볼지 판정: (a) 표본 부족 + E1(변경 전)에도 같은 크기 → 수용하고 ⑥ 마감, (b) 클립 반전 호출 시각-stale 상관 probe 1회 요청. 사용자 G1 시험 결과가 오면 최우선.
