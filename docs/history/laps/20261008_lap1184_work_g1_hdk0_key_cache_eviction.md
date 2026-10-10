# 2026-10-08 | lap 1184 | G1 work — H-HDK0 ⑥ 메모리 대책: 키·캐시 한도 실측(K-0/K-1) → LRU 축출(K-2)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / high / 실무(work). 커밋 0. 최종 승인은 다음 middle(Opus) 몫.
- 입력: lap1183 middle 사전등록 §5(`20261008_lap1183_middle_g1_hdu0_review_hdk0_preregistration.md`). `loop/STOP`·`loop/ESCALATE_SOL` 없음, INBOX·APPROVALS 새 지시·반려·사용자 G1 시험 결과 없음. 디스크 여유 시작 84 GB, 끝 74 GB.
- 가설: 키 테이블(`g_keys[4096]`)은 축출이 없어 장기 플레이에서 한도 뒤 새 키가 `identity_invalid_sources`로 빠져 HD가 조용히 열화한다. K-1이 증가율을 재서 사전등록 조건(keys ≥2,048 또는 선형 외삽 ≤60분)을 만족하면 LRU 축출이 필요하다.
- 예상 PASS/FAIL: K-0 호스트 테스트 GREEN·NG5에서 `identity_cache_bytes` = 3×`cache_insert_frame_bytes`. K-1 ≥5분 PS3·키 증가 관측·안전 0. K-2 사전등록 §5 측정식.

## 변경 (모두 uncommitted)

| 파일 | 내용 |
|---|---|
| `tools/inmm_stub/g1_hd_asset.c` | K-0 `g1_hd_asset_identity_cache_bytes()`. K-2: 키마다 `last_draw`(전역 `g_draw_clock` 증가분), `pick_lru_key(exclude, need_frames)`·`drop_key_frames(key, with_shade)`·`make_room_for(needed, exclude)`. **키 슬롯 가득**이면 현재 키(`g_current_key`)를 뺀 가장 오래 begin된 키를 해제하고 슬롯을 `memset` 뒤 새 키로 재사용(없으면 기존대로 `identity_invalid_sources`). **캐시 바이트 한도**(`bind`의 2wh·`build_hd_frame`의 4wh 예약)는 다른 키 중 프레임을 가진 가장 오래된 키의 프레임만 해제(키 정체성·음영 복사본은 유지, 다음 draw가 재bind). 카운터 `identity_evictions`, 키 로그 줄 `evict_key`·`evict_bytes`. `G1_HD_KEY_LIMIT`·`G1_HD_CACHE_BYTE_LIMIT`는 `#ifndef`(호스트 테스트용). 진단 env `SYW2_G1_HD_KEY_LIMIT`(1..4096 십진수, 아니면 무시)로 실제 게임에서 테이블을 낮춰 축출을 유도 |
| `tools/inmm_stub/g1_hd_asset.h` | 접근자 2개(`identity_cache_bytes`·`identity_evictions`) |
| `tools/inmm_stub/direct_draw_trace.c` | trace `identity_cache_bytes`·`identity_evictions`(기존 팩 세부 줄 끝에 덧붙임, 다른 동작 변경 0) |
| `tools/g1_saved_scene_probe.py` | K-1 장기 run용 `--new-game-play-keys`·`-hold`·`-dwell`(기본 동작 불변, `--new-game-play` 필요·값 검증) |
| `tests/test_g1_hd_pack.py`·`tests/test_g1_new_game_path.py` | 호스트 테스트 +9(`cache_bytes`, 슬롯 LRU 축출·재등장 시 팩 재적용, 현재 키 보호(한도 1은 요청 거부), 가득 찼을 때 오래된 다른 키 축출, 바이트 예산 축출·재빌드, 음영 키 바이트 축출 뒤 재빌드, env 한도·잘못된 값 무시, 하네스 옵션 2) |

파일 SHA256 앞 16자(최종): `g1_hd_asset.c 6c2b79988b97c58d`·`.h 06410b3b99b99de4`·`direct_draw_trace.c c2baaacddab6f350`·`g1_saved_scene_probe.py 557bda2b963f2b9d`·`tests/test_g1_hd_pack.py 6e06f9245441b5f1`·`tests/test_g1_new_game_path.py 7005173c42da6150`.

## 측정 (산출물 공유 temp `20261008_lap1184_work_hdk0/`, 팩 = lap1178 `pack_hdf1`, NG5 = `--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 60`)

- **원본 보호:** 원본 EXE `b56986e0…` 전·후 MATCH(`orig_sha_before/after.txt`), game 사본 하네스 제거(prefix·manifest·output 보존, run당 약 1.2 GB).
- **K-0:** 호스트 테스트 GREEN(키 2개 bind 뒤 값 = 2×6wh = 48, 리셋 뒤 0, 값 = 3×`cache_insert_bytes`). 실제: K2 마지막 present `identity_cache_bytes` 25,582,224 = 3×8,527,408 (refresh 0).
- **K-1 (실측, 한도 없음):** K1 첫 run은 **후보 레인이 PS5에서 PS3로 못 넘어가 FAIL**(baseline PASS, 크래시·충돌 없음, 하네스 로비 시작 클릭 미반응; 같은 인자 재실행 K2는 PASS — 환경성 단발로 보되 원인 미규명, 공개). 이후 3 run(K2·K3·E2):

| run | PS3 체류 | keys 시작→끝 | 캐시 | invalid | stale(PS3) | p95 |
|---|---|---|---|---|---|---|
| K2 | 306 s | 252→**1209** | 6.4→25.6 MB | 0 | 0 | 6 ms |
| K3 | 306 s | →1233 | 26.3 MB | 0 | 59 px 1 present | 6 ms |
| E2 (한도 1000, 도달 안 함) | 306 s | →789 | 17.1 MB | 0 | ≤90 px 2 present | 6 ms |

  - 카메라는 모든 run에서 맵 한 끝(0)↔끝(99)을 왕복(각 hold 91~99 스텝, 8회 모두 moved). K2 60 s 구간별 키 증가: +351/+407/+86/+110/+3(마지막 66 s는 +3) — 첫 맵 가로지르기에서 대부분 늘고 포화하는 모양. **run마다 새 임의 게임이라 총 키 수 편차가 크다(789~1233).**
  - 4096 도달 선형 외삽은 **창 선택에 따라 달라진다**: 마지막 60 s 1,443분·120 s **51분**·180 s **43.5분**·240 s 19분·전체 15.4분. 사전등록 조건(≤60분)은 창 ≥120 s에서 충족, 조건의 창 정의는 사전등록에 없음(공개). 위 포화 곡선만 보면 이 idle 장면 단일 맵에서는 4096에 안 닿지만, 키가 팔레트·유닛 종류·장면(스테이지 재진입) 누적에 비례하고 한도 뒤 회복 경로가 없어서 **K-2 구현으로 판정**했다(근거: 사전등록 조건 충족 + 회복 불가 + 구현 비용 작음).
- **K-2 (축출, 실제 게임):** 진단 env `SYW2_G1_HD_KEY_LIMIT=600`(<작업 집합 약 1200 → 일부러 thrash):

| run | 소스 | keys / evictions | invalid | cache | stale(PS3) | p95 | fallback·hresult·안전 | pack reject |
|---|---|---|---|---|---|---|---|---|
| E1 | 중간 소스(`g1_hd_asset.c e1aaef60…`) | 600 / 927 | 0 | 12.7 MB | 264·59(축출 전 13.3·15.3 s)·110·79·92(축출 중) = 5 present | 6 ms | 0 | 0 |
| E3 | **최종 소스** | 600 / 824 | 0 | 14.3 MB | 246·59·235·77·18(축출 전 13.2~15.5 s)·2·2(축출 중) = 7 present | 6 ms | 0 | 5 |

  - 축출이 일어난 run에서 `identity_invalid_sources` 0 유지, `identity_lookup_misses`·`key_mismatches`·`hd_mask_outside_diff`·`scale2x_palette_violations` 0, p95 6 ms = 대조(K2 6·K3 6). 팩 hit 1318/1227 > 대조(1033/1053): 축출된 키가 다시 그려질 때 새 키로 bind돼 hit를 다시 센다.
  - **stale 귀속:** 축출 전(키 400대·evictions 0)의 13~15 s 일시 stale(select 구간, 235~264 px)은 lap1169 OFF1(팩 끔)·lap1182 U1과 같은 기존 서명(K2에는 없고 K3·E2에는 있음 = run 간 변동). 축출 중 stale는 E1 79~110 px 3건·E3 2 px 2건으로 비축출 대조(K3 59·E2 90)와 같은 규모라 축출 때문이라는 증거는 못 얻었고, **축출 없음 대조와 "같거나 낫다"를 통계로 증명하지는 못한다**(모든 run의 일시 stale는 소멸, 원인 UNKNOWN).
- **save006 pair(`pair.sh`, 팩 env, 한도 기본):** P1(중간 소스)·P2(**최종 소스**) 둘 다 status PASS·scene_state_equal·V2/V2s/V2q/Scale2x PASS. 키 약 790개, 축출 로그 0(비회귀 확인 용도).
- **호스트 테스트·변이:** `tests/test_g1_hd_pack.py` 52 passed(hd_pack·new_game_path·mirror2x 3파일 합 170 passed). 변이 5종 RED — (1) 슬롯 축출 제거 2건, (2) 바이트 축출 제거 1건, (3) 현재 키 보호 제거 1건, (4) 바이트 회계 누락 2건, (5) 바이트 축출이 음영 복사본까지 해제 1건.

## 판정

- **K-0 PASS, K-1 PASS(partial)** (≥5분·키 포화 곡선 관측, 외삽은 창 의존이라 사전등록 조건 충족 판정은 공개 사항으로 middle 몫), **K-2 `PASS(partial, 기술·격리)`**: 축출 정확성(호스트)과 실제 게임 thrash 2 run 안정(invalid 0·안전 0·p95 불변)은 입증, stale "같거나 낫다"는 run 간 변동 때문에 통계적으로 미입증.
- 기본 켬·사용자 전달 아님(팩 env 실험 경로 + 진단 env 한도). 마일스톤 경계 아님.

## 한계·공개

1. 캐시 바이트 한도 경로(128 MiB)는 실제 게임에서 도달한 적 없다(최대 26 MB) — 호스트 테스트로만 검증. 실제 게임 축출은 키 슬롯 경로(진단 env로 유도).
2. E1·P1은 최종 소스 이전 빌드다(바이트 축출 때 음영 복사본 해제 방지 수정 전). 바뀐 줄은 바이트 경로에만 있고 그 경로는 두 run에서 실행되지 않았다. 최종 소스로 E3·P2를 다시 실행했다.
3. 새 키 수는 임의 게임마다 다르다(789~1233). 4096 도달 시각 추정은 이 idle 장면 한 맵 기준이고 전투·여러 스테이지·낮밤 팔레트 변화는 미관측.
4. `last_draw`는 DWORD 증가 시계라 약 2^32 begin 뒤(수십 시간급)에 순서가 뒤집힐 수 있다(오래 켜 둔 세션에서 LRU가 일시 부정확해질 뿐 안전 영향 없음).
5. 한도 1은 현재 키만 있는 상태에서 새 요청을 거부한다(진단 env 극단값). 실제 한도 4096에서는 해당 없음.
6. 슬롯 재사용은 선형 키 탐색을 그대로 쓴다(키 4096개 × draw마다 비교 비용은 기존과 같음). 축출 키 재등장은 팩 파일을 다시 읽는다(디스크 I/O) — thrash run에서도 p95 불변.
7. 첫 K1 run의 후보 레인 PS5→PS3 미전환은 원인 미규명 단발(재실행 PASS).
8. 바이트 축출이 음영 키의 프레임만 해제하고 복사본(`shade_map`·`shade_lut`)을 유지하는 근거는 lap1179 middle의 "음영 LUT 표는 시작 때 1회만 구축"이다. 이 가정이 틀리면 H-HDS1r가 막은 낡은 LUT 재적용과 같은 문제가 생기므로 middle이 판정해 달라.

## 다음 행동

middle(Opus) 독립 검수: source SHA 대조·호스트 테스트·변이 재실행, K-1·E1·E3 trace에서 `identity_keys`·`identity_evictions`·stale 새 스크립트 재계산, 한계 8(음영 복사본 유지) 판정, K-2 수용 시 ⑥ 마감 여부와 INBOX 19:3x 이후 순서 결정. 사용자 G1 시험 결과가 오면 최우선.
