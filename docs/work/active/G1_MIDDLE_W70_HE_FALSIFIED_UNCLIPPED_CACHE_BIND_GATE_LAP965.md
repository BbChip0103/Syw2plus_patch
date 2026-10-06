# G1 lap963 H-E 반증 독립 검수 · H-E2 재정의(비클립 cache 바인드 폭 게이트) 인계 — lap965

## 판정 요약

- 지정 역할 middle(Claude Code `claude-opus-5-5`, high, Fast OFF). 게임·하네스·source·test·DLL·validator 변경 0, 새 게임 실행 0, commit 0. `loop/.lap_counter` 965 읽기만.
- **lap963 H-E 반증을 수용한다.** 제품 helper와 lap963 분석 스크립트 없이 재계산했다. 가장자리(x≥760·y<480) steady 교집합 stale 3,512, 교집합 전체 9,880, y<480 6,243이 lap961·lap963에서 같다. 두 교집합은 픽셀 단위로 동일하다. cache clipped 시도 107·verify 실패 0·첫 viewport `[0,0,831,511]`도 trace 원문과 일치한다.
- **`g1_mirror_replay_viewport`는 유지한다.** cache frame(832×512)에 맞는 올바른 viewport이고, 안전 0·E-3 악화 없음이 측정됐다. 되돌리면 재실행 비용만 든다. 계수 3개도 유지한다.
- **lap962의 대안 H-E2(전송 offset)는 기각한다.** `transfer_cache_to_screen`은 항등 매핑(`row*832+col → row*800+col`)이다. stale은 흩어져 있지 않고 타일 격자에 정확히 맞는다(§2).
- **새 원인(H-E3, FEASIBLE):** `g1_mirror2x.c` 비클립 바인드 분기(약 1563~1567행)가 대상과 상관없이 `width <= 800u`·`origin_x <= 800u - width`를 요구한다. cache 대상 frame 폭은 832다. 그래서 cache x=768에 놓인 64×32 마름모 타일(cache 안에 완전히 들어가므로 비클립)은 새 key일 때 바인드되지 않는다. `g1_hd_asset_current_ready()`가 거짓이라 `compose_cache_layer`가 호출되지 않는다. 그 결과 이전 장면에서 compose된 layer 값(covered=1, 옛 expected)이 남아, 매 transfer마다 stale로 판정된다.

## 1. 재계산 (입력 SHA는 lap963 기록과 일치)

스크립트 공유 temp `20261005_lap965_middle_review/recalc_lap965.py`(`2d9a0cbc…76ad`) → `recalc_lap965.json`(`78aec654…c5c3`).
입력: lap963 mask `c70976a2…3eff`·trace `807cb0f1…6075`·pair `9e738803…e043`, lap961 mask `8db4a04b…d27`·trace `bf5f30df…6c4f`·pair `b5df22d4…dd9c`.
현재 source SHA(`g1_mirror2x.c` `1ec6468d…4019`, `g1_mirror_frame.h` `e8210cc6…87d7`, `g1_mirror2x.h` `f7139abd…66c3`, `direct_draw_trace.c` `a929c02f…21ee`, `tests/test_g1_mirror2x.py` `e7d80f97…7b75`)도 lap963 기록과 같다.

| 항목 | lap961 r1 | lap963 r1 |
|---|---|---|
| mask 덤프 / steady(ord≥300) | 51 / 39 | 51 / 39 |
| 교집합 전체 / y<480 / x≥760·y<480 | 9,880 / 6,243 / 3,512 | 9,880 / 6,243 / 3,512 |
| layer_move_calls(전 구간) | 0 | 0 |
| layer_compose_calls 증가(0-150 / 150-300 / 300-600 / 600-끝) | 620 / 9 / 21 / 4 | 620 / 9 / 21 / 4 |
| 최종 misses / inserts / keys | — | 771 / 763 / 766 |

- 덤프별 가장자리 stale: ord 6~34는 808, ord 300 이후는 3,512로 일정하다. 그 사이(present 60~150)에 compose가 620회 늘고 `layer_covered_pixels`가 423,936→425,984로 바뀐다. 이것은 cache 전체 재그리기다(minimap 클릭 카메라 이동; scroll memmove 0회).
- 끝까지 바인드되지 않은 key는 3개다(keys−inserts). frame 없이 끝난 miss 사건은 8회다(misses−inserts).

## 2. stale 기하 — x=800 중심 마름모의 왼쪽 절반

`he3_geometry_lap965.py`(`0d4d40dd…2d6d`) → `he3_geometry_lap965.json`(`8b6dda84…529a`).
- 열별 stale은 x=760에서 8, x=799에서 180으로 선형 증가한다. 행 288~480에서 32행 주기의 삼각형(꼭짓점 x≈768, 밑변 x=800)이 6개 있다. 이것은 origin_x=768·폭 64·높이 32 마름모 타일의 화면 안쪽 절반이다.
- 가장자리 stale 3,512 중 **2,869px(81.7%)가 이 마름모 안**이다. 행 288~480의 마름모 픽셀 3,072 중 2,868이 stale이다. 나머지 643px은 게임 시계 글자(행 13~18, x 746~769)와 반투명 로고(P6 명시 잔여, 행 380~440)다.
- crop(`edge_crop_loaded_lap965.png` `f067c3b3…24fe1`, `edge_crop_production_lap965.png` `44dbd8a2…b8b3`): 원본/후보 화면은 같은 지면이다(stale 픽셀은 nearest로 대체되어 보이는 깨짐 없음). overlay에서 오른쪽 끝 톱니 삼각형이 확인된다.

## 3. 원인 경로 (정적, 현재 source)

1. 지형 RLE/shade(`0x468C30`/`0x468CC0`)는 `clipped=FALSE`로 `mirror_reinvoke`에 들어간다.
2. miss key(`needs_identity_frame`)이고 비클립이면 1563행 분기만 바인드할 수 있다. 조건 `(DWORD)origin_x <= 800u - width`가 cache 대상에도 800을 쓴다. origin_x=768, width=64면 768 > 736이라 분기를 건너뛴다.
3. `g1_hd_asset_current_ready()`가 거짓 → `compose_cache_layer` 미호출 → layer 해당 픽셀의 covered/expected는 이전 장면 값 그대로다.
4. `transfer_cache_to_screen`이 covered=1과 옛 expected를 화면으로 옮긴다 → present에서 expected≠실제 → stale. 다음 프레임에 같은 일이 반복되므로 steady 전 구간에서 지속된다.
- 같은 key를 화면 안쪽(origin_x≤736)에서 먼저 바인드한 타일은 hit로 compose되므로 stale이 아니다. 행 0~288의 같은 열 타일이 정상인 것과 맞다.
- 화면 대상은 frame 폭이 800이라 이 조건이 맞다. 결함은 cache 대상에만 있다.

## 4. 다음 work 인계 (Sonnet, 1 lap, FEASIBLE)

1. **최소 수리:** 1563~1567행 비클립 바인드 분기의 `800u`를 이미 계산된 `frame_width`로 바꾼다(`width <= frame_width`, `(DWORD)origin_x <= frame_width - width`). 화면 대상은 `frame_width==800`이라 동작이 바이트 동일하다. `origin_frame = scratch_a + origin_y*stride + origin_x`는 이미 `range_valid(stride, frame_width, surface_height)`가 검사한 범위 안이다. `g1_hd_asset_bind_identity_frame`의 `width>800` 거부는 타일 폭(64)과 무관하다. 새 env는 없다.
   - 정적/host 테스트: (a) 화면 대상 판정 불변(origin_x=737·width=64 거부), (b) cache 대상 origin_x=768·width=64 허용, origin_x=769 거부, (c) 읽기 범위 `origin_x+width ≤ frame_width ≤ stride`. 판정을 `g1_mirror_frame.h` helper(예: `g1_mirror_unclipped_bind_fits`)로 빼면 lap963 host 테스트 방식(`tests/test_g1_mirror2x.py` 379행 부근)으로 검사할 수 있다.
2. **같은 lap 계수(진단, 기존 키·pin 불변):** cache 대상 비클립 바인드 중 `origin_x > 800-width`인 횟수 1개(`cache_edge_unclipped_binds`). 기존 `identity_keys`·`identity_cache_inserts`도 함께 본다.
3. `make lint`·`make typecheck`·focused → fresh save006 scale2x pair 1회. 명령·`--stale-mask 6-12,30-34,300-301,585-620,880`은 lap961/963과 같다. 비교 기준은 lap963 r1.
4. **사전등록 예측(진단, 새 gate 아님):**
   - F-1: x≥760·y<480 steady 교집합 stale 3,512 → **≤750**(남는 것은 시계 글자·로고 ≈643).
   - F-2: 교집합 전체 9,880 → **≤7,150**. PS3 cov p50 ≥97.2%·min ≥93.7%.
   - F-3: `cache_edge_unclipped_binds` ≥1, 최종 keys−inserts 3 → ≤1.
   - F-4: present ≥854·p95 ≤28ms. 안전 0(clip mismatch·viewport mutation/restore·palette·outside diff)·V1/V2/V2q/Scale2x PASS·minimap parity·원본 EXE/save MATCH·source_unchanged·game 사본만 삭제.
   - V2s raw는 그대로 공개한다(기존 gate 판정 불변, HOLD여도 이 lap의 실패 사유 아님).
5. **반증:** F-1 미달인데 F-3 계수가 ≥1이면 바인드는 되는데 compose가 안 되는 것이다. 이 경우 `compose_cache_layer`의 lookup 실패(`continue`)를 다음 진단 후보로 적고 HOLD로 middle에 넘긴다. F-3 계수가 0이면 이 경로가 실행되지 않는 것이므로 H-E3 기각으로 기록한다. 수리를 위해 covered를 줄이지 않는다.
6. 디스크 여유가 20GiB 미만이면(이번 lap 시작 시 14GiB) PROMPT 규칙대로 game 사본만 정리한다. prefix 회수는 archive·restore 검증 뒤에만 한다. 여유가 확보되지 않으면 실행하지 말고 기록한다.

## 5. 부수 관찰 (이번 수리 범위 밖)

- `compose_cache_layer`는 lookup 실패나 not-ready일 때 해당 픽셀의 옛 layer covered를 지우지 않는다. present의 expected 검사가 대부분 막지만, 옛 expected 값이 우연히 새 값과 같으면 옛 HD 블록이 보일 수 있다. H-E3 결과를 본 뒤 별도 가설로만 다룬다.

## 6. strategy 재호출 조건

기존 조건(lap933 §6·lap938 §7·lap944 §6·lap946·lap952 §6·lap956 §7·lap958 §5·lap960 §6·lap962 §6) 유지. 추가: H-E3 수리 뒤 F-3 계수 ≥1인데 F-1이 미달이고, compose lookup 가설도 기각될 때.

## 7. 범위 밖·금지

V2s gate 의미 변경(W-1 자동 적용)·한도·V1/V2/V2q·Scale2x validator·PS3 통계량·golden 변경, 과거 raw/pair-result 재작성, covered 축소, 캡처 시점·영역 변경, G2/G5 수정·G3/G4 재개, 원본/참고 저장소 쓰기, commit/publish/deploy.
