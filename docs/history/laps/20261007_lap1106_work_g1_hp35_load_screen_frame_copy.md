# 2026-10-07 | lap1106 | G1 work — H-P35 불러오기 화면(PS35) 배경·패널 HD 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high, Fast OFF / work(hands-on 구현) 1 lap. 컨펌·마일스톤 승인 권한 없음. 커밋 0.
- 목표: lap1105 사전등록 H-P35 — PS35(불러오기 슬롯 화면) HD 9.4% → ≥90%.
- 가설: PS35 배경은 매 프레임 같은 검정을 다시 쓰는 writer라 diff 기반 미러가 못 보고, 패널은 `0x466280` 부분 사각형이라 전체 프레임 조건에서 걸러진다.
- 입력: STATUS "다음 한 가지", lap1105 기록 §3. INBOX 새 지시 없음, APPROVALS 새 반려 없음, `loop/STOP`·`loop/ESCALATE_SOL` 없음(lap1105 root 전달분은 이미 처리·보존됨).
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — probe `source_exe_sha256`/`private_exe_sha256` 5 run 모두 MATCH(읽기만). 비합성 save006/save000 fixture, 활성 8인 증명 아님.

## 1. P35-0 하네스(TDD)

- `tests/test_g1_census.py::test_probe_census_state_35_waits_in_load_screen_before_slot_navigation` RED(`choices=(3, 9, 35)` 부재) → GREEN. `tools/g1_saved_scene_probe.py`: `--census-state` choices에 35, `wait35` 직후 `if census and census_state == 35:` 분기(census window 대기 → `load_screen` 캡처 → `_CensusStateComplete`). PS9 분기·PS3 기본 불변, C 스텁 변경 없음(파서가 0..99를 이미 받음). 사전등록에 없던 `load_screen` 캡처는 §4 독립 대조용으로 추가했다.

## 2. P35-1 귀속(census-only, save006, r_a `census_raw.jsonl` `30de6859…`)

- 실행: `.venv/bin/python tools/g1_saved_scene_probe.py --census-only --census-state 35 --runtime-root local/runtime/lap1106_census_ps35_a/runtime --artifact-root <공유temp>/20261007_lap1106_work_hp35/lap1106_census_ps35_a/artifacts` exit 0, gate PASS(64 present, 10 check).
- PS35 last-writer(480,000): rle_clip 2,149 · rle_plain 6,584 · block_copy 88,880 · rle_tinted 1,869 · **unknown 380,518(79.3%)**. unknown은 모든 present에서 `unknown_index_top` index 0(검정) 100%, 표 64 present 동안 불변. writer가 닿은 영역 bbox `[240,100,559,524]`(320×425 패널).
- 귀속: 검정 배경 = 매 프레임 offscreen `BltFast`(dest `0x01E6D920`=present source·832 pitch ← src `0x01E6DE78` 800×600, x=y=0, src rect NULL, flags 16, caller `0x00493CCB`; trace 104건·census `dd_surface_blt` calls 63·writer_pixels 0 = 값이 같아 diff가 못 잡음). 패널 block_copy는 `(0,0,800,600)`이 아니라 부분 사각형(그래서 `menu_copy_calls` 불변, 미러가 조용히 거름). 미커버 435k 중 검정 BltFast 380.5k + 패널 block_copy 부분 사각형이 대부분 → **P35-1 ≥95% 귀속 PASS**(가설 (a)+(c) 결합; (b) 새 blitter 아님). rect_fill 1건(`0x00465E80`, 158,135-477,258, 별도 buffer `0x029A3920`)은 1회성.

## 3. 변경(source, 전부 uncommitted)

- `tools/inmm_stub/g1_frame_copy.h`(신규): `g1_frame_copy_accepts`·`g1_frame_copy_apply` — 포장된(stride=width) 사각형을 800×600 화면에 **모든 픽셀 covered=1/expected=값/Scale2x(또는 nearest)** 로 반영(값이 같아도 covered). C 런타임 없이 링크되므로 mask 채움은 호출자 몫(`fill_bytes`).
- `g1_mirror2x.c`: `transfer_block_copy_to_screen`이 전체 화면 조건 대신 `g1_frame_copy_accepts`로 모든 in-bounds 사각형을 처리(캐시/패널 대상 제외·`readable_bytes` 유지). 전체 프레임 `(0,0,800,600)`만 기존 `menu_copy_*` 계수·hash 진단 유지, 부분은 `partial_copy_*`. 신규 `g1_mirror2x_frame_blt_copy(destination, source)`: source를 READONLY lock(pitch 800/크기 800×600 확인)해 전체 프레임으로 반영, 실패는 `frame_copy_rejects`.
- `direct_draw_trace.c`: `hook_blt_fast`에서 원본 호출 뒤 `g1_mirror2x_enabled() && SUCCEEDED && !primary && return_address==0x00493CCB && !src && x==y==0 && !SRCCOLORKEY && source 800×600 && dest 폭≥800·높이 600 && 상태 35`일 때만 `g1_mirror2x_frame_blt_copy`. present 행에 `partial_copy_calls/pixels`·`frame_copy_calls/pixels/rejects` 5필드 추가, `layer_details[400→640]`(V-S 최악 길이 테스트 요구).
- `g1_mirror2x.h`·`Makefile`(헤더 의존)·`tests/test_g1_frame_copy.py`(신규 4건: host-gcc 계약·소스 계약 3)·`tests/test_g1_mirror2x.py`(기존 menu block-copy 소스 계약을 새 계약으로 갱신)·`tests/test_g1_census.py`·`tools/g1_saved_scene_probe.py`.
- source SHA256(16): `g1_frame_copy.h 66c2e337…`·`g1_mirror2x.c 0953140e…`·`g1_mirror2x.h 9bd5374e…`·`direct_draw_trace.c 186cc622…`·`g1_saved_scene_probe.py b4c71aff…`·`test_g1_frame_copy.py a1a87715…`. 빌드된 후보 `_inmm.dll`은 run마다 PE 타임스탬프만 다름(p1 `a2b659fb…`, p2 `6987cc5f…`).

## 4. P35-2 측정(공유 temp `20261007_lap1106_work_hp35/`, 새 스크립트 `recalc_hp35.py` `c5ae1bea…`·`oracle_ps35.py` `aecf30ba…`; 제품 helper 미사용)

식: present별 HD = (covered − stale)/480,000(분모 불변). 명령: `.venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1106_<run> --artifact-root <temp>/<run> --hd-source scale2x [--fixture save000 --scene-actions none]`.

| run | 상태 | present | HD min / p50 | stale max | V1 outside | 경과 p95 |
|---|---|---|---|---|---|---|
| p1 save006 | PS9 / **PS35** / PS3 | 67 / 215 / 868 | 100 / **100** / 99.287 | 0 / 0 / 0 | 0 / 0 / 0 | 14 / 13 / 7ms |
| p2 save006 | PS9 / **PS35** / PS3 | 68 / 212 / 867 | 100 / **100** / 99.287 | 0 / 0 / 0 | 0 | 16 / 14 / 7ms |
| s1 save000 | PS9 / **PS35** / PS3 | 66 / 68 / 10 | 100 / **100** / 98.618 | 0 | 0 | 15 / 13 / 6ms |

- PS35 전환 present(index 0)도 100%(stale 0): 전환 때 배경 BltFast가 같은 present 전에 전부 다시 덮는다(lap1105는 첫 present stale 434.7k). 이전 값 PS35 9.4%.
- counter: PS35 `frame_copy_calls` 215/212/68(=present 수)·`frame_copy_rejects` 0, `partial_copy_calls` 같은 수·`menu_copy_calls` 67/68/66(PS9 값 그대로, 부분 사각형이 PS9 hash 진단을 오염시키지 않음).
- pair gate(save006 2/2): status PASS, input_effect·minimap parity·V2/V2s/V2q·Scale2x(trace 1150 present, palette violation 0, outside diff 0)·loaded 전부 PASS, scene_state_equal true. save000(s1)은 `--scene-actions none` fixture 한계로 기존대로 HOLD(input_effect·V2 선택/드래그/미니맵/생산 BLOCKED, loaded PASS) — 사전등록이 허용한 HOLD, 이번 변경 무관.
- PASS 판정(사전등록 §3 P35-2): ① PS35 index≥1 전 present ≥90% 3/3 run(실측 100%) ② PS9 min 100%≥99.4·PS3 min 99.287≥99.2(save006)·98.618≥98.5(save000)·PS3 마지막 40 stale 합 0≤307 ③ V1 outside 0 전 상태 ④ save006 pair 2/2 PASS ⑤ 안전 7종(`clip_replay_mismatches`·`viewport_field_mutations`·`viewport_restore_failures`·`scale2x_palette_violations`·`hd_mask_outside_diff_subpixels`·`cache_clip_verify_failures`·`identity_key_mismatches`) p1·p2·s1 candidate trace 전 present max 0, trace `dropped_count` 0, cleanup ok·`source_unchanged` baseline/candidate true·PS3 p95 7ms≤12·PS35 p95 13~14ms≤26.
- **독립 시각 대조(근사):** baseline census 캡처 `load_screen.png`(800×600)를 RGB 동치로 독자 Scale2x해 "Scale2x와 nearest가 다른 subpixel" 수를 세면 21,131. 후보 trace PS35 `hd_mask_inside_diff_subpixels`는 p1 20,799~21,141·p2 20,799~21,141·s1 20,806~20,833(프레임 애니메이션으로 변동). 약 1.6% 이내 일치 → HD 값이 Scale2x와 같은 면적에서 nearest와 다르다는 근사 확인. **한계:** 후보 PS35 화면 PNG를 직접 캡처하지 않았고 RGB 동치는 팔레트 index 동치와 정확히 같지 않다 — 픽셀 정확 오라클은 UNKNOWN.

## 5. 검사

- 목표 Fast: `test_g1_frame_copy`(4)·`test_g1_mirror2x`·`test_g1_overlay_blt`·`test_g1_presentation_trace`·`test_g1_census`(30)·`test_g1_rect_fill` 합 129 passed → 이후 census 변경분 재확인 30 passed. `make lint`·`make typecheck` PASS. 전체 `make check`는 기록 freeze 뒤 1회(STATUS에 결과).
- 디스크: 실행 전 99GiB, 종료 후 94GiB. 각 run `game` 사본 삭제 확인(`local/runtime/lap1106_*/`에 game 없음), prefix·output·manifest·로그 보존. 다른 프로세스 비접촉.

## 6. 한계·UNKNOWN

- PS35 후보 화면 PNG 직접 캡처·픽셀 정확 Scale2x 비교는 없다(위 근사 일치만). 이 화면은 합격 기준 V2/V2s 태그 밖이다.
- 부분 사각형 Scale2x는 사각형 바깥 이웃을 가장자리 복제로 가정하므로 패널 테두리 고리에서 전체 프레임 Scale2x와 다를 수 있다(직선 경계는 동일, 모서리만 가능). 이번 oracle 근사로는 구분되지 않는다.
- `0x466280` 부분 사각형 확장은 PS35 외 상태(타이틀·대기실·옵션 등)에도 적용된다. 이번에 측정한 상태는 PS9·PS35·PS3뿐이고, 다른 화면은 미측정(기존 backlog)이다. PS3 census block_copy 0px라 PS3은 영향 없음.
- 전체 프레임 BltFast 미러는 PS35 + caller `0x00493CCB` + 800×600 NULL-rect로 좁게 걸어 다른 화면에는 영향이 없다. 매 프레임 full-frame Scale2x 비용은 PS35 경과 p95 13~14ms(PS9 14~16ms와 동급).
- 사용자 시험판 `_inmm.dll`(`94213374…`)은 재스테이징하지 않았다(사전등록대로). 이 변경은 시험판에 들어 있지 않다.
- 수용 판정은 middle 몫. 모델 PASS는 사용자 합격이 아니다.

## 7. 다음 한 가지(제안, middle 확정)

middle(Opus)이 새 스크립트로 raw 3 run을 독립 재계산하고 §2 귀속(unknown 검정 = 같은 값 재기록 BltFast)과 source diff를 검수한다. 수용되면 다음 work 후보: (a) 다른 화면 상태(타이틀·대기실·옵션·저장 창·승패)의 HD coverage 측정, (b) 시험판 재스테이징 여부 판단, (c) 사용자 G1 시험 결과가 오면 그것이 최우선.
