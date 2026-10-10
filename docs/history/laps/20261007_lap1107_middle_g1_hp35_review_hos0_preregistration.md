# 2026-10-07 | lap1107 | G1 middle — H-P35 독립 검수·수용 + H-OS0(혼자하기 PS7·PS5 화면 HD) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1106 work → middle 검수 요청), STATUS "다음 한 가지", lap1106 기록, lap1105 사전등록 §3. INBOX 새 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1107_preserved_lap1106_escalate_sol.txt`로 byte 일치 보존(SHA256 `696b2e806afd28b3…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). save006 `616b7997…0d064` MATCH. 세 pair run의 baseline·candidate `source_exe_sha256`/`private_exe_sha256`도 모두 같은 값이다.
- fixture: p1·p2 = 비합성 save006(index 7), s1 = 비합성 save000. 활성 8인 증명 아님.

## 1. 독립 재계산 (새 스크립트, 새 실행 아님)

- 스크립트: 공유 temp `20261007_lap1107_middle_review/recalc_lap1107.py`(`51d781b9bd08dd73…`) → `recalc_lap1107.json`(`f0c1845e3a233043…`). 새로 작성했다. work의 `recalc_hp35.py`·`oracle_ps35.py`와 제품 helper는 쓰지 않았다. 식은 lap954와 같다: present별 HD = `(covered − stale) / 480,000`.

### 1-1. 귀속(ESCALATE 1번) — 일치

- census a `census_raw.jsonl` `30de6859…`(work 기록과 같음)·b `44fee43f…`. 두 run 모두 PS35 `present_boundary` 64개, 모든 present에서 `unknown_pixels` = 380,518(최소=최대), `unknown_index_top[0]` = (index 0, 380,518) → unknown 전부 검정이다. `assigned + unknown = 480,000`이 모든 present에서 성립한다.
- 마지막 present writer 픽셀(a·b 같음): rle_clip 2,149·rle_plain 6,584·block_copy 88,880·rle_tinted 1,869·`dd_surface_blt` 0. bbox `[240,100,559,524]` 하나. present source surface는 64/64 `0x01E6D920`이다.
- census trace의 `BltFast`(return `0x00493CCB`)는 모두 같은 서명이다: PS35, dest `0x01E6D920`(= present source) ← src `0x01E6DE78` 800×600, src rect NULL, x=y=0, flags 16. 상세 기록 수는 a 104·b 77이다. 이 값은 method당 상세 기록 상한(256) 안의 표본이고 총 호출 수가 아니다.
- 결론: "검정 배경 = 매 프레임 같은 값을 다시 쓰는 offscreen BltFast(값이 같아 writer_pixels 0), 패널 = `0x466280` 부분 사각형"은 raw와 맞는다. P35-1 ≥95% 귀속 PASS를 확인한다.
- **정정 1:** lap1106 기록 §2의 "census `dd_surface_blt` calls 63"은 raw `surface_blt_summary`의 `calls_ps3` 64·`captured` 64·`capture_missed` 0이다(a·b 같음). 결론은 바뀌지 않는다.

### 1-2. 상태별 HD·안전(ESCALATE 2번) — 일치

| run | 상태 | present | HD 첫 / min / p50 | stale max | 마지막40 stale 합 | V1 outside max | inside diff 범위 | 경과 p95 |
|---|---|---|---|---|---|---|---|---|
| p1 save006 | PS9 | 67 | 100 / 100 / 100 | 0 | 0 | 0 | 116,238~116,276 | 14ms |
| | **PS35** | 215 | **100 / 100 / 100** | 0 | 0 | 0 | 20,799~21,141 | 13ms |
| | PS3 | 868 | 100 / 99.287 / 99.315 | 0 | 0 | 0 | 108,816~110,980 | 7ms |
| p2 save006 | PS9 / **PS35** / PS3 | 68 / 212 / 867 | 100 / **100** / 99.287 (min) | 0 | 0 | 0 | — | 16 / 14 / 7ms |
| s1 save000 | PS9 / **PS35** / PS3 | 66 / 68 / 10 | 100 / **100** / 98.618 (min) | 0 | 0 | 0 | PS35 20,806~20,833 | 15 / 13 / 6ms |

- 안전 7종(`clip_replay_mismatches`·`viewport_field_mutations`·`viewport_restore_failures`·`scale2x_palette_violations`·`hd_mask_outside_diff_subpixels`·`cache_clip_verify_failures`·`identity_key_mismatches`)은 세 run 후보 lane의 모든 present에서 최대 0이다. `summary.dropped_count` 0, fallback 0, success 전부 1.
- 계수 증가는 상태별로 나눠 셌다. `frame_copy_calls`와 `partial_copy_calls`는 **PS35에서만** 늘고 present 수와 같다(215/212/68). `frame_copy_rejects` 0. `menu_copy_calls`는 PS9에서만 늘어난다(첫 값 포함 67/68/66). 부분 사각형 경로는 측정한 PS9·PS3에서 한 번도 돌지 않았다.
- pair gate: p1·p2 status PASS. input_effect·minimap parity·loaded·V2·V2s·V2q·Scale2x 모두 PASS, scene_state_equal true. s1 status HOLD(input_effect HOLD·V2/V2s/V2q BLOCKED, minimap·loaded·Scale2x PASS). 이것은 `--scene-actions none` fixture 한계이고 사전등록이 허용한 HOLD다.
- bridge source: 세 run의 bridge `g1_frame_copy.h 66c2e337…`·`g1_mirror2x.c 0953140e…`·`g1_mirror2x.h 9bd5374e…`·`direct_draw_trace.c 186cc622…`는 현재 트리와 같다. bridge `inmm_stub.c`(`4ad87bf4…`)는 트리(`6d312824…`)에 probe가 넣는 `supply_probe_poll` 선언·호출 2줄만 더한 것이다(diff 직접 확인). 기존 bridge 조립 방식과 같다.
- 사전등록 §3 P35-2 ①~⑤를 모두 충족한다. PS35 전환 present(index 0)도 100%다. lap1105가 공개한 save006 PS35 주기 stale 6.3k도 이번 raw에서는 0이다.

### 1-3. 독립 시각 대조(ESCALATE 4번)

- baseline census b `load_screen.png`(`f98735b4…`, 800×600 RGB)를 내 Scale2x(RGB 동치, 가장자리 복제)로 계산했다. nearest와 다른 subpixel은 **21,131**이고 work 값과 같다. 이 차이는 모두 패널 bbox 안에 있다(bbox 안 21,131). 후보 trace PS35 `hd_mask_inside_diff_subpixels`는 20,799~21,141이다. 근사 일치다.
- **부분 사각형 고리 위험 정량(새 근거):** 같은 PNG에서 bbox `[240..559]×[100..524]`를 잘라 가장자리 복제로 Scale2x한 값과 전체 프레임 Scale2x의 같은 영역 값을 비교했다. 다른 subpixel은 **14**뿐이다(bbox 안 HD 차이 21,131의 0.07%). 실제 부분 사각형 좌표는 raw에 표본이 없다(census block_copy 표본 32개는 모두 PS9). 그래서 bbox로 근사했다. 결론: 고리 차이는 실재하지만 작다. 허용된 화질 차이(Scale2x 모서리)이며 위치·비율 결함이 아니다.
- 후보 PS35 화면 PNG의 픽셀 정확 비교는 여전히 없다. PS35는 V2/V2s 태그 밖이므로 수용을 막지 않는다. UNKNOWN으로 공개한다.

### 1-4. source diff 검수(ESCALATE 3번)

- `g1_frame_copy.h`: `accepts`는 `width·height>0`, `x≤800`, `y≤600`, `width≤800−x`, `height≤600−y`를 검사한다. 오버플로 없는 경계 검사다. `apply`는 사각형의 모든 픽셀을 covered=1·expected=src로 둔다. 값이 같아도 covered로 둔다. Scale2x는 기존 `g1_scale2x_build_masked`를 쓴다(mask 전부 1). 화면 HD stride 1600을 확인한다.
- `transfer_block_copy_to_screen`: HEAD에서는 `(0,0,800,600)`만 받았다. 지금은 화면 안의 모든 사각형을 받는다. 캐시 base·패널 bound buffer 제외, `stride≥800`·`height≥600`·`readable_bytes`는 HEAD와 같다. 전체 프레임만 `menu_copy_*`·hash 진단을 갱신하고, 부분 사각형은 `partial_copy_*`만 갱신한다.
  - **위험(공개, 차단 아님):** 대상 renderer buffer가 present source인지는 HEAD와 마찬가지로 확인하지 않는다. 다른 800폭 이상 offscreen buffer로 가는 부분 복사가 있으면, 화면 좌표의 expected·covered가 잘못 표시된다. 그러면 present에서 stale로 잡혀 nearest로 남는다. 즉 화질 손실이지 오표시는 아니다(V1 outside 0이 이를 감시한다). PS9·PS3에서는 부분 경로 호출이 0이었다. 다른 화면은 미측정이므로 아래 H-OS0에서 `partial_copy_calls`와 stale을 함께 본다.
- `g1_mirror2x_frame_blt_copy`: source를 `DDLOCK_READONLY`로 잠그고, `lPitch==800`·800×600일 때만 반영한다. 할당이나 lock에 실패하면 reject로 센다. 모든 경로에서 Unlock한다. present마다 HeapAlloc 2.4MB를 하지만 PS35 p95 13~14ms로 사전등록 상한 26ms 안이다.
- `hook_blt_fast` 게이트: 원본 호출 **뒤**에 `SUCCEEDED`·비primary·return `0x00493CCB`·src NULL·x=y=0·colorkey 없음·source 800×600·dest 폭≥800·높이 600·PS35를 모두 확인한다. 범위가 좁고 원본 결과를 바꾸지 않는다(읽기만). dest identity는 확인하지 않지만, census에서 이 caller의 dest는 1종(`0x01E6D920`)뿐이다.
- 판정 밖 관찰: 이번 trace에서 상태 40·60·180의 640×480×16 모드 요청은 native 2x를 건너뛴다(`exact_800x600x8_call_gate_mismatch`). 이것은 lap149 이후 알려진 시작 시 모드 탐색이고, 마지막 모드는 800×600×8→1600×1200이다. 새 결함이 아니다.

## 2. 판정

- **H-P35 `PASS(partial, 기술·격리)` 수용.** 정정 1(§1-1). PS35 불러오기 화면 HD는 9.4%에서 100%가 됐다(save006 2/2·save000 1). PS9·PS3 비회귀, V1 0, 안전 7종 0, pair gate save006 2/2. 사용자 합격도 G1 마감도 아니다.
- 남은 공개 항목: 후보 PS35 픽셀 정확 오라클 UNKNOWN, 부분 사각형 고리 근사 14 subpixel, 부분 경로의 다른 화면 영향 미측정.
- **시험판 재스테이징: 지금은 하지 않는다.** 사용자가 lap1104 시험판(`94213374…`)으로 시험 중일 수 있다. 결과가 오기 전에 DLL을 바꾸면 피드백이 어느 판의 결과인지 섞인다. H-P35는 화질만 바꾸고 위치·입력 동작은 바꾸지 않는다. 그래서 다음 화면 측정(H-OS0) 결과와 묶어 다음 middle이 한 번에 재스테이징 여부를 정한다. 사용자 결과가 먼저 오면 그것을 최우선으로 처리한다.

## 3. 다음 work 사전등록(Sonnet) — H-OS0: 새 게임 경로 화면(PS7 지도·설정, PS5 혼자하기 대기실) HD coverage 측정 → 미달 시 귀속

**근거:** 지금까지 HD를 잰 화면은 PS9(메뉴)·PS35(불러오기)·PS3(게임)뿐이다. 사용자가 새 게임을 시작하면 반드시 PS9 → PS7 → PS5 → PS3를 지난다. 이 경로는 `tools/g6_shift_click_probe.py`에 이미 있다: PS9에서 (184,560) 클릭 → PS7, (608,564) 클릭 → PS5. 부분 사각형 확장(H-P35)이 이 화면들에 미치는 영향도 함께 측정된다.

**가설:** PS7·PS5는 PS35처럼 `0x466280` 부분 사각형이나 같은 값 재기록 writer로 그려진다. 그래서 H-P35 뒤 이미 HD ≥90%이거나, 미달 픽셀이 census로 이름 있는 writer에 귀속된다.

- **OS0-0 하네스(TDD):** `g1_saved_scene_probe.py`에 후보 lane이 PS9 → PS7 → PS5를 지나 각 화면에서 일정 present를 머무는 경로를 추가한다. 하나는 `--census-state` 7·5(census-only)이고, 하나는 측정 run용이다. 클릭 좌표·대기 함수는 G6 probe와 같게 한다(좌표 출처를 주석으로 남긴다). PS5 채팅 EDIT 포커스는 건드리지 않는다(키 입력 없음). 기존 3/9/35 경로는 바꾸지 않는다. 테스트 RED→GREEN.
- **OS0-1 측정(save006 아님, 새 게임 경로라 fixture 불필요; 격리 run 2회):** 후보 lane `--hd-source scale2x`. 상태별로 present 수·HD 첫/min/p50·stale max·V1 outside max·`partial_copy_calls`·`frame_copy_calls`·`menu_copy_calls` 증가·경과 p95를 공개한다. 각 화면 캡처 1장씩(baseline·candidate)을 남긴다. 가능하면 PS5에서 시작해 PS3 진입까지 간다.
  - **PASS:** PS7·PS5 각각 index≥1 모든 present HD ≥90%, V1 outside 0, 안전 7종 0, 2/2 run.
  - **미달 시(같은 회차):** 해당 상태 census-only 1회로 미커버 픽셀을 writer별로 귀속한다(P35-1과 같은 형식, ≥95% 귀속이면 PASS). 수리는 하지 않는다. 귀속 결과와 최소 수리안을 middle에 넘긴다(가설 1개 규칙).
  - **BLOCKED:** 클릭으로 PS7/PS5 진입이 안 되면, 상태값·캡처를 남기고 G6 probe 대조 결과와 함께 넘긴다. 60분 또는 실패 가설 2회 규칙(PROMPT ③)을 따른다.
- 판정 밖 기록: PS7·PS5에서 부분 경로가 present source가 아닌 buffer로 들어가는지(stale 증가로 드러남), 경과 p95.
- 공통: source를 바꾸면 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 93GiB) 확인, 끝나면 game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지.
- 사용자 시험판은 다시 스테이징하지 않는다(§2).

backlog(유지): 타이틀(PS9 이전)·옵션·게임 중 저장 창·승패 화면 HD, 후보 PS35 픽셀 정확 오라클, v3 ord 350 단발 UNKNOWN, `0x4676D0` 미러 여부, 화면 밖 `0x467410` 쓰기, throttle ord 123 writer, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`·focused G1 테스트를 돌린다. 결과는 STATUS에만 쓴다.
- 전체 `make check`는 SKIP한다. 이번 변경은 문서뿐이고, source·하네스·테스트 SHA는 lap1106 full PASS(1703) 때와 같다(§1-2 bridge 대조, 트리 `g1_saved_scene_probe.py b4c71aff…`·`test_g1_frame_copy.py a1a87715…`).

## 다음 한 가지

work(Sonnet): §3 H-OS0 — OS0-0 하네스(PS9→PS7→PS5 경로) → OS0-1 측정 2회 → 미달 시 같은 회차 census 귀속. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
