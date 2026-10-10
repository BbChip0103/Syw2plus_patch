# 2026-10-07 | lap1126 | G1 middle — H-RS0 독립 검수(FAIL 수용·귀속 정정) + H-RS1(PS27·PS29 stale 위치·writer) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1125 work → middle 검수 요청), STATUS 다음 한 가지, lap1125 기록, lap1124 사전등록 §4. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1126_preserved_lap1125_escalate_sol.txt`로 byte 일치 보존(SHA256 `cdda0998…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: lap1125 raw만 사용(`g7defeat` = lap982 orig `save001.dat` `57872666…`, 타이틀 불러오기 → ps 3→27→29 "패배했습니다.").
- artifact SHA(ESCALATE_SOL과 일치): result a `87229984…`·b `4054a569…`, candidate trace a `96f8e0cb…`·b `88630c94…`, census29 raw `6067e5e2…`.
- source 동일성: `g1_mirror2x.c` `98d261be…`·`g1_mirror2x.h` `815b58e6…`·`direct_draw_trace.c` `6bf459cb…`·`g1_pause_snapshot.h` `cdcbc36b…`(lap1124와 같음 = 제품 C 변경 0), probe `b52c12d2…`·`tests/test_g1_result_screen.py` `843ab57a…`(work 기록과 같음). lap1125 full check 로그(07:28:47) 뒤 수정된 tools/tests/checks/patches 파일 0.

## 1. 독립 재계산 (새 스크립트)

- 스크립트: 공유 temp `20261007_lap1126_middle_review/recalc_lap1126.py`(`2ee9b3cc…`) → `recalc_lap1126.json`(`5f04c0d7…`). work 창 경계(`line_start/end`)를 쓰지 않고 **program_state 연속 구간 + input trace의 LBUTTONDOWN 시각**(탭 (500,57)·(606,57)·(713,57), 확인 (712,561))으로 직접 나눴다. HD = (covered − stale)/480,000(하네스 계약과 같은 정의).

| run | 창 | presents | HD 첫·min·p50 | stale 첫→max(→끝) | 1 present 증가 최빈 | 비고 |
|---|---|---|---|---|---|---|
| a | PS27 | 1,174(7.99초) | 80.754·80.754·80.754 | 92,383 고정(첫 present stale, 이후 uncovered) | 0 | menu copy 0, 원본 프레임 hash 21종(1,021회 한 hash) |
| a | PS29 탭 전 | 427 | **99.985**·**98.36**·98.36 | 72→7,874(111 present째 정체) | **+72 ×96** | menu copy 1/present, hash 변화 0 |
| a | 탭 병사 | 237 | 98.36·98.36·99.171 | 7,874→3,980 | 0/+36 | |
| a | 탭 건물 | 238 | 99.171·99.171·99.171 | 3,980 | 0/+36 | |
| a | 탭 자원 | 240 | 99.171·99.171·100 | 3,980→0 | 0 | |
| a | 확인 뒤 PS9 | 294 | 100·100·100 | 0 | 0 | |
| b | PS27 | 1,055 | 80.754·80.754·80.754 | 92,383 고정 | 0 | |
| b | PS29 탭 전 | 413 | 99.985·**98.36**·98.36 | 72→7,874(111) | **+72 ×96** | |
| b | 탭 병사/건물/자원 | 218/231/241 | min 98.36/99.171/99.171 | 7,874→3,980 / 3,980 / 3,980→0 | | |
| b | 확인 뒤 PS9 | 297 | 100·100·100 | 0 | 0 | |

- 공통(2/2): 상태 구간 `[9,35,3,27,29,9]`, trace `dropped_count` 0, 전체 present V1 outside·안전 7종·fallback·hresult≠0 모두 0, success min 1, 경과 p95 PS27 6/7ms·PS29 12~13ms·PS9 12ms.
- **work 판정 지표와 불일치 0**(PS29 min 98.36% 2/2·+72/present 선형·7,874 정체·탭 병사 7,874→3,980·건물 3,980·자원 →0·PS9 100%·PS27 80.754%·stale 92,383).
- 정정 1(경미): work의 PS29 `hd_first` 99.925/99.955는 work 창이 PS29 첫 present 몇 개 뒤에서 시작해서다. 실제 첫 PS29 present는 stale 72 → 99.985%. 판정 영향 없음.
- **정정 2(공개 누락):** 확인 클릭 뒤 PS9로 넘어가기 직전 **PS29 마지막 present 1개가 stale 478,002(HD 0.416%)**(a·b 동일). work 창(`tab_resources` 끝 → `after_confirm` PS9)이 이 present를 빼서 공개되지 않았다. 아래 §2처럼 stale 픽셀은 현재 논리 색의 nearest 2×로 출력되므로 내용 오류가 아니라 한 프레임(약 7ms) HD→nearest 전환이다. 판정(이미 FAIL)에는 영향 없고 backlog로 둔다.

## 2. 판단 요청 처리

### (1) FAIL 수용, 귀속은 정정

- **H-RS0 `FAIL` 수용**: 사전등록 PS29 min ≥98.6% 미달 2/2(98.36%), 탭 병사 창도 미달. 나머지 항목(PS9 비회귀 100·V1/안전/fallback/dropped 0·scale2x PASS·캡처 정상)은 충족.
- **정정 3(귀속 근거 철회): "stale은 rle 프리미티브 호출 쪽 누적"은 근거가 없다.** `primitive_stale_pixels_total`은 C에서 매 present stale 합계의 누적값(`g_stale_pixels`, `g1_mirror2x.c` 1877행)이다. 직접 확인: 연속 present의 누적 증가 = 그 present의 `stale_pixels`, 불일치 0/2,832(a)·0/2,662(b), 최종값 5,017,851·4,800,241 = stale 합계. 프리미티브 쪽 신호가 아니다.
- **정정 4(census "미후킹 writer 0"은 결정적이지 않음):** census 지도는 계측 대상 writer 10종(rle_clip·rle_plain·rect_fill·block_copy·rect_border·rle_tinted_clip·rle_tinted·set_pixel·terrain_cache_transfer·dd_surface_blt)에만 픽셀을 배정한다. 계측 밖 writer가 덮어쓴 픽셀은 이전 계측 writer(여기서는 전면 block_copy)에 남는다. 선례: lap1012 census "미후킹 0" 뒤 lap1022 screen watch가 미후킹 `0x467B00`을 찾았다. 그래서 PS29 writer는 **UNKNOWN**이다.
- **새 위치 귀속(캡처 기반, 확정도 높음):** baseline 논리 캡처 `ps29` 대 `result_tab_resources`(자원 탭은 막대 없음·stale 0) 차이를 막대 상자별로 보면 병사 열 빨강/보라 막대 각 **1,990 px**, 건물 열 각 **2,000 px**, **모두 18행**(y189..206·y227..244)·112열(x199..310·x341..452)이다.
  - 병사 탭 정착 stale **3,980 = 1,990×2**(병사 막대 2개)로 정확히 일치한다.
  - +72/present = **막대 4개 × 18행 × 1열/present**(막대가 자라는 애니메이션)이다.
  - 정체값 7,874는 막대 4개 7,980보다 106 작다. 막대 위 숫자(3·19)의 글자 픽셀로 추정하며 UNKNOWN으로 둔다.
  - 즉 **PS29 stale = 결과 표의 그라데이션 막대**이고, 막대 픽셀을 미러가 따라가지 못한다.
  - menu copy 원본 hash는 전면 800×600 전체 hash인데 PS29 내내 변화 0이다. 그래서 막대는 menu copy 원본에 없고, menu copy 뒤 화면에 직접 그려진다.
- writer 단서(미확정, H-RS1에서 확인):
  - (a) census `buffer_summary`에 PS29 세대 화면 밖 버퍼 `0x02246B60`(stride 800)이 있다. rect_fill 1회로 39,237 px, bbox x158..476·y135..257을 칠했고, 이 영역이 막대 표 영역을 포함한다.
  - (b) census 원 호출 흐름에서 PS29 64 present 동안 block_copy는 95회다. 미러 run의 menu copy는 1/present이고 `partial_copy_calls` 증가는 0이다. 따라서 present당 약 0.5회의 추가 block copy가 미러 계수에 보이지 않는다(`transfer_block_copy_to_screen`의 조기 return은 계수가 없다).
  - (c) `0x467B00`·`0x4685C0` 호출 246/240은 PS3 41 present × 6과 맞아 PS29 막대와 무관할 가능성이 크다.

### (2) 화면에 보이는 결함인가 — 기준 유지, 시각 심각도 낮음으로 기록

- C 확인(`g1_mirror2x.c` 1836~1880행): 모든 논리 픽셀의 출력 기본값은 현재 논리 색 nearest 2×다. stale 픽셀은 HD 대신 그 nearest가 나가고 `g_covered`가 해제된다. **내용·색 오류가 아니라 Scale2x 대신 nearest로 보이는 화질 차이다.**
- 막대는 행마다 같은 색인 가로 그라데이션이다. 그래서 Scale2x와 nearest가 막대 안쪽에서 같고 끝·모서리만 다르다.
- 독립 캡처 분류(`visible_check_lap1126.py` `e89859d0…`·`visible_check_lap1126.json` `608d308e…`; 후보 2×2 블록을 baseline 논리 프레임의 Scale2x/nearest/둘 다 아님으로 분류):

  | 캡처 시점 | stale | 둘 다 아님 | nearest만(가시) | 합계 |
  |---|---|---|---|---|
  | ps29 | 7,874 | 661 | 509 | 1,170 |
  | 병사 탭 | 3,980 | 578 | 446 | 1,024 |
  | 건물 탭 | 3,980 | 576 | 475 | 1,051 |
  | 자원 탭 | 0 | 507 | 389 | 896 |

  a·b 값은 같다. stale 0인 자원 탭에도 896이 있으므로 이 바닥값은 per-sprite HD와 전면 Scale2x 기준 차이(기존 성격)다. stale 7,874가 더하는 화면 차이는 **약 274 논리 px(0.06%)**뿐이다.
- **결정:** 사전등록 기준 PS29 HD ≥98.6%는 **유지**한다(기준·validator 무완화 원칙). 지표 재정의(스크린샷 비교로 대체)는 하지 않는다. FAIL은 "시각 심각도 낮음(막대 그라데이션, 가시 차이 약 274 px)"으로 기록하고, 수리 우선순위는 PS27 뒤로 둔다.

### (3) 최소 C 변경 사전등록 — 채택(아래 §3 H-RS1)

- stale mask는 `program_state == 3`만 덤프하도록 하드코딩되어 있다(`g1_mirror2x.c` 1763~1772행).
- screen watch는 `g1_screen_watch_state_parse`가 3/23만 받는다(`g1_screen_watch.h` 74~77행).
- 그래서 PS27/PS29 위치·writer 귀속에는 옵트인 C 변경이 필요하다. env가 없으면 동작은 그대로다.

### (4) PS27·승리 화면 우선순위

- **PS27이 PS29보다 우선이다.** 패배 뒤 결과 표 전에 약 8초(1,055~1,174 present) 동안 화면 19.2%(92,383 논리 px)가 nearest로 고정된다.
  - 첫 present에서 stale 92,383이 생기고, 그 뒤 covered에서 빠진 채 다시 덮이지 않는다(menu copy 0, 프리미티브 1/present).
  - 사용자 가시 손실이 PS29 막대(약 274 px)보다 훨씬 크다. 캡처가 없어 어떤 화면인지는 UNKNOWN이다.
- 승리 화면은 별도 fixture가 필요하고 PS29 막대 귀속으로 대부분 공유될 가능성이 커서 backlog에 둔다.

## 3. 다음 work 사전등록(Sonnet) — H-RS1: PS27·PS29 stale 위치·writer 귀속 → 조건부 최소 수리

- **가설 H-RS1:** PS27의 92,383 px와 PS29 막대(약 7.9k px)는 각각 미러가 따라가지 않는 단일 writer 경로가 그린다. 위치와 EIP를 잡으면 기존 미러 계열(block copy·frame copy·overlay Blt·rect fill)의 확장으로 덮을 수 있다.
- **RS1-0 옵트인 진단(C+하네스, TDD):**
  - `SYW2_G1_STALE_MASK_STATE`(기본 3, 허용 3·23·27·29): stale mask 덤프 대상 상태를 고르고 ordinal은 그 상태 기준으로 센다. env가 없으면 현행 PS3 동작과 같다.
  - `g1_screen_watch_state_parse`에 27·29를 허용한다(3·23 동작 불변).
  - 하네스 `--stale-mask-state`·`--screen-watch-state` choices에 27·29를 넣고 `--result-screen` 경로에 배선한다. **PS27 캡처 `ps27.png`**(PS27 진입 약 2초 뒤, candidate·baseline)를 추가한다.
  - 테스트 RED→GREEN: parse 경계(미지정·잘못된 값 → 3), 기존 3/23 불변, 하네스 인자 배선.
- **RS1-1 위치(격리 run ≥1, `--result-screen --fixture g7defeat --hd-source scale2x`):**
  - PS27 mask ordinal 0·1·200, PS29 mask ordinal 5·60·150(탭 클릭 전)을 덤프한다.
  - 기록: PS27 stale bbox·면적(92,383 재현)과 `ps27.png` 열람으로 화면 정체, PS29 mask가 막대 상자 x199..452·y189..244 안인지(예상 ≥95%).
  - 진단 켬이 HD 수치를 바꾸지 않는지(PS27 80.754·PS29 98.36 재현)도 기록한다.
- **RS1-2 writer(격리 run, screen watch 상태 27 → 29 각각 1회):**
  - 표본은 RS1-1 mask 안 픽셀로 한다.
  - EIP·tid·호출처·ret 바이트 수를 기록하고, 표본 변화의 ≥90%를 귀속한다.
  - 필요하면 PM1-1b ddraw Blt/BltFast 호출 표도 함께 본다(`0x02246B60` 같은 화면 밖 버퍼 → 화면 전송 경로 확인).
- **RS1-3 조건부 수리(같은 회차, 구현 우선):**
  - writer가 기존 미러 계열로 덮을 수 있는 경로이면 최소 미러 확장을 구현하고 격리 2회를 돌린다. 예: `transfer_block_copy_to_screen`의 계수 없는 조기 return, BltFast/Blt 전면·부분 복사, rect fill 대상 화면 밖 버퍼 → 화면 전송.
  - 새 writer 함수 hook이 필요하거나 원인이 둘 이상이면 수리 없이 귀속만 넘긴다.
  - 조기 return에 계수를 붙이는 것(진단)은 수리 여부와 무관하게 허용한다.
- **PASS(귀속):** PS27·PS29 각각 mask 위치 확정 + 표본 ≥90% EIP 귀속 + 진단 켬 HD 수치 재현 + V1/안전 7종/fallback/dropped 0.
- **PASS(수리, 시도 시 2/2):**
  - PS27 min ≥98.6%(첫 전환 present 1개는 공개만), PS29·각 탭 min ≥98.6%, 확인 뒤 PS9 100%.
  - V1/안전 7종/fallback/hresult 0·dropped 0·scale2x PASS·경과 p95 증가 ≤2ms·캡처 정상.
  - **비회귀 1 run**(new-game 경로 `--new-game-start --new-game-act` 또는 save006 기본 장면에서 PS3 HD·안전 0).
- **FAIL/BLOCKED:** 위치·EIP가 서로 맞지 않거나 표본 귀속 <90%면 원인 후보와 근거를 남기고 middle로 넘긴다. 실패 가설 2회 또는 60분이면 BLOCKED.
- 공개 한계(미리 적음): 패배 화면만 측정한다(승리 화면 UNKNOWN). PS29 마지막 present stale 478,002(1 present)는 backlog이고 이번 PASS 항목이 아니다. 부하 대표성은 낮다.
- 공통: C·하네스 변경 뒤 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 약 150GiB 여유), game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지, 시험판 재스테이징 없음(lap1104 판본 유지). 사용자 G1 시험 결과가 들어오면 그것이 최우선이다.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS에만 쓴다.
- 전체 `make check` SKIP: 이번 변경은 문서뿐이다. 하네스·테스트·C source는 lap1125 full PASS(1766) 때와 같다(위 source 동일성, check 로그 뒤 변경 0).

## 다음 한 가지

work(Sonnet): §3 H-RS1 — RS1-0 옵트인 진단(stale mask·screen watch 상태 27/29, PS27 캡처, TDD) → RS1-1 위치 → RS1-2 writer → 조건부 RS1-3 최소 수리, middle 검수 요청.
