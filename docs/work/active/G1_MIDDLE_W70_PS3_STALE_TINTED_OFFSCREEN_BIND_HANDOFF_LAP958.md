# G1 lap957 PS3 stale mask 독립 수용 · tinted 화면 밖 origin 바인드 수리 인계 — lap958

## 판정과 범위

- 지정 역할 middle(Claude Code `claude-opus-5-5`, high, Fast OFF), 진단·계획·확인. 게임·하네스·source·test·DLL·validator 변경0, 새 게임 실행0, commit0. `loop/.lap_counter` 958 읽기만.
- lap957 opt-in stale mask 장치(`SYW2_G1_STALE_MASK`)를 **PASS(partial) 수용**한다. partial 사유: save006 한 fixture, census 정렬은 다른 run(lap951 r6) 근사, burst 미재현(UNKNOWN), 동적 API 실패 주입 미검증(기존과 같음).
- 분류 진단(≥95% 단일 클래스)은 lap957 기록대로 **미충족**이 맞다. 그러나 이번 검수에서 steady stale의 대부분이 **한 가지 구현 경로 결함**으로 설명된다(§3). 이는 측정 해석이며 coverage 합격이 아니다. 임계값·gate·PS3 통계량 해석 변경 없음.
- milestone 경계·근거 충돌·미설명 실패 없음 → ESCALATE_SOL 조건 없음. lap956 §7 strategy 조건(정상 stale ≥50%가 후킹 가능 writer 밖) **불성립**.

## 1. 독립 재계산 (제품 helper·lap957 스크립트 미사용)

- source 5파일 SHA = lap957 기록(`g1_stale_mask.h bcb41a84…a064`, `g1_mirror2x.c d2e4357a…2c30`, `Makefile afefc2e8…d9920`, probe `c4579726…d431`, test `edbe1ef0…019c3`). stale_mask.bin r1 `1600c13b…5165`·r2 `f28bca41…2e56`, raw r1 `4f8f5d3a…415e`·r2 `b8f7367e…a889`·r3 `216e7b27…c490` 일치. 원본 `game.exe b56986e0…a8ac`·`save006.dat 616b7997…d064` read-only MATCH.
- 공유 temp `20261004_lap958_middle_review/recalc_lap958.py`(SHA256 `ba184bc2…7e00`) → `recalc_lap958.json`(`ba45cd93…b1c`):
  - 장치: r1 51·r2 42 덤프 전부 magic/state/480000·맵 합(1+2, 2) == header == 같은 PS3 서수 `mirror2x_present` 레코드 covered/stale, **불일치 0**.
  - steady(서수 ≥300, 68덤프): stale 평균 42,786.8, `rle_tinted` 75.45·terrain_cache_transfer 14.43·dd_surface_blt 8.40·rle_plain 0.87·rle_tinted_clip 0.57%; 미커버 dd_surface_blt 91.14%; residual 겹침 평균 2,441.1 — lap957 표와 **정확히 일치**. 초기 6~12·30~34 표도 일치.
  - **새 사실: steady stale은 고정 픽셀 집합이다.** 서수 ≥300 모든 덤프의 교집합 r1 41,861·r2 41,806(합집합 44,308/45,445). 시간 의존 현상이 아니라 매 프레임 같은 픽셀이 stale이다.

## 2. 원본 writer 의미 (`0x466EA0` 읽기 전용 objdump)

- 루프 본체 `0x466F8C~0x466FC8`: `al=[src+ebp]`, `0xFE`면 다음 바이트만큼 건너뜀, 아니면 `[esi+edx] = lut[al]`. **목적지를 읽지 않는다**(lap911 `no_dest_read`와 일치). 따라서 sentinel 0x00/0xFF 두 재생에서 불투명 픽셀은 a==b이고 "목적지 의존이라 compose 제외" 가설은 기각.
- 함수 머리 `0x466ECF~0x466F6C`가 렌더러 viewport `[+0x4D0,+0x4D4,+0x4D8,+0x4DC]`로 **스스로 클립**한다. 하네스 `G1_RENDERER_VIEWPORT 0x4D0u`와 같은 필드.

## 3. 원인 판정: 비클립 tinted 경로가 화면 밖 origin 스프라이트를 영구 미바인드

- source(`g1_mirror2x.c` `mirror_tinted_rle`→`mirror_reinvoke(..., G1_TINTED_RLE, FALSE)`): 새 key의 identity frame 바인드는 clipped=FALSE면 `origin_x,origin_y ≥ 0`·`origin ≤ 800−w / surface_height−h`일 때만 수행(`else if` 분기). 화면 밖에 걸친 스프라이트는 바인드가 안 되고 `g1_hd_asset_current_ready()`가 거짓 → compose 0 → 그 픽셀의 `g_expected_snapshot`은 아래 terrain 값으로 남아 present에서 stale→최근접.
- 위치 증거(`geom_lap958.py` `15e96731…8e95` → `geom_lap958.json` `021759a7…ce80`, overlay `stale_intersection_r1_lap958.png` `8d3e9c7d…4160`): census-tinted steady stale 31,998px는 bbox x37~799·y0~486, HUD 띠(y≥512) 0. 같은 run `production.png`(baseline, 카메라 이동 뒤)와 나란히 보면 빨간 덩어리는 **화면 위쪽 가장자리에 걸린 건물 줄**(x≈170–600, 700–770, y 0~100)과 일치하고, 화면 안에 완전히 들어온 건물(중앙 x390–500, y140–270 등)은 stale이 아니다.
- 렌더 증거(`png_block_lap958.py` `d37c9837…61da` → `png_block_lap958.json` `1863aa3b…fc78`, 같은 run candidate `production.png` `d15ffc9b…44ca`): steady 교집합 stale 픽셀의 2×2 블록 비균일 비율 **0.0**(전부 최근접 fallback), 일치 픽셀은 0.237(Scale2x). 위쪽 줄 영역(y0~99, x160~779) stale 26,951px = 교집합의 64%.
- 보조 지표: present 레코드 `identity_cache_misses`가 서수 400에 24,540으로 계속 누적(바인드 안 된 key 재조우), `tinted_rle_466ea0_covered`는 초기 8,160에서 멈춤.
- 나머지 클래스(수리 대상 아님, 기록만): terrain 14.43%는 오른쪽 가장자리 띠(x≥770 1,264px)와 화면 고정 로고 — lap951 r6 census는 lap953 blend hook 이전이라 P6 로고를 terrain으로 귀속(P6 명시 잔여). dd_surface_blt 8.40%는 HUD 상자(x540~718·y500~590, 미후킹 HUD surface).
- 한계: per-call 바인드 실패 사유는 직접 계측하지 않았다(위치·렌더·source 세 근거의 일치로 판정). 그래서 §4는 사전등록 예측으로 반증 가능하게 둔다.

## 4. 다음 work 인계 (1 lap, FEASIBLE — 계획 회차 없음)

목표: `rle_tinted`(`0x466EA0`) 화면 밖 origin 호출도 identity frame을 바인드해 위쪽 건물 줄 stale을 HD로 덮는다. 최소 변경.

1. **변경(단일 지점):** `mirror_tinted_rle`이 `mirror_reinvoke`에 넘기는 clipped 인자를, origin이 `[0, 800−w] × [0, surface_height−h]` 밖일 때만 TRUE로 한다(화면 안 호출은 지금과 같은 FALSE 경로, 동작 불변). TRUE 경로는 이미 `rle_tinted_clip`이 쓰는 원점(0,0)·전체 viewport 재생 → `verify_unclipped_frame_in_viewport`(origin 오프셋 적용) → 바인드다. viewport 저장/복원·mismatch 계수는 기존 그대로. 새 env·새 raw 키 없음(기존 `viewport_replays` 등이 늘 뿐).
2. RED→GREEN: 정적 계약 테스트(화면 밖 조건에서 TRUE, 화면 안 FALSE)와 기존 `test_g1_mirror2x.py` 전체. 기존 pin(`mirror_details[2048]` 등) 수정 금지. `make lint`·`make typecheck` 먼저.
3. 실행: fresh save006 scale2x 1 pair, lap957 r1과 **같은 `--stale-mask 6-12,30-34,300-301,585-620,880`**. 비교 기준은 lap957 r1/r2.
4. 사전등록 예측(진단, 새 gate 아님):
   - P-1: steady(서수 ≥300) 교집합 stale 중 위쪽 줄 영역(y0~99, x160~779)이 lap957 r1 26,951px에서 ≤20%(≤5,390px)로 준다.
   - P-2: steady stale 평균이 lap957 42.8k보다 줄고, PS3 p50 HD coverage가 90.41%보다 오른다(값 공개).
   - P-3: steady 구간 `identity_cache_misses` 증가율이 lap957 r1(서수 300→880 구간)보다 낮다.
   - 안전: V1 outside diff 0, palette violation 0, `clip_replay_mismatches` 0, `viewport_field_mutations`/`viewport_restore_failures` 0, Scale2x gate PASS, 원본 EXE/save MATCH, source_unchanged, game 사본 삭제(manifest/output/prefix 보존).
   - 성능: present `elapsed_ms` p50/p95·`primitive_reinvoke_elapsed_ms_max`를 lap957 r1과 나란히 공개(P5-T C 기준 ratio ≥0.95·p95 ≤ baseline+16ms를 참고로 대조, 기준 변경 없음).
5. P-1이 틀리면(위쪽 줄 stale이 그대로) 같은 lap에서 원인 추적: `mirror_reinvoke` tinted 호출의 분기별 계수(early return·asset_started·needs_identity·verify 실패·바인드 실패·ready·compose 수)를 **opt-in**으로 추가해 한 번 더 실행하고 기록한다. 그래도 설명 못 하면 HOLD로 middle에 넘긴다.
6. 디스크: 여유 18GiB(<20GiB). 실행 전 PROMPT 규칙대로 자기 회차 game 사본 정리, 종료된 private prefix 회수는 lossless archive·검증·restore 확인 뒤에만. `local/runtime/<run>` 전체 삭제 금지.

## 5. strategy 재호출 조건

- 기존 조건(lap933 §6·lap938 §7·lap944 §6·lap946·lap952 §6·lap956 §7) 유지.
- 추가: §4 수리 뒤 위쪽 줄 stale이 바인드·compose가 성공했는데도(계수로 확인) 남아 있을 때 — 즉 후킹된 tinted 출력 뒤에 미후킹 writer가 같은 픽셀을 바꾸는 경우.
