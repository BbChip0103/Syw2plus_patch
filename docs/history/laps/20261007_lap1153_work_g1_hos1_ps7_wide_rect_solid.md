# 2026-10-07 | lap1153 | G1 work — H-OS1 PS7·PS5 글자·버튼 stale 귀속 → 조건부 수리 1회

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 입력 = STATUS "다음 한 가지" + lap1152 middle 사전등록 §6. INBOX 새 사용자 지시 없음(마지막 = lap1153 root 전달 메모), APPROVALS 새 반려 없음, `loop/STOP`·`loop/ESCALATE_SOL` 없음.
- 원본 SHA: pair `execution_source.unchanged == true`, 모든 new-game-path lane `source_unchanged: true`(원본 EXE `b56986e0…` 불변). 원본/참고 쓰기 0, 커밋 0.
- 가설: PS7 접속방식 화면의 stale ≈ 8,800 논리 px/present는 미후킹이 아니라 **기존 후킹 `0x465E80`(단색 사각형)이 폭 > `G1_OVERLAY_MAX_WIDTH`(320)인 사각형을 `reject_size`로 거부**해서 생긴다.
- fixture: `--new-game-path`(타이틀→PS7→PS5), 비합성 save006 pair, NG5 플래그. 부하 대표성 낮음(메뉴 화면).

## OS1-0 진단 확장 (TDD RED→GREEN)

- `g1_screen_watch.h` `g1_screen_watch_state_parse`에 `"5"`·`"7"` 추가(상수 `G1_SCREEN_WATCH_STATE_PS5/PS7`), 하네스 `--screen-watch-state` choices `(3,5,7,9,20,23,27,29)`. `tests/test_g1_screen_watch.py` 기대값 갱신(기존 `"5"→3` 단정을 `5→5`로 바꿈, `"7"`·`"57"`·`"05"`·`"4"` 추가) — RED 2 failed → GREEN 13 passed. `--new-game-path` 분기는 이미 `layer_drift`/`screen_watch`/`screen_watch_state`를 후보 lane에 전달함을 기존 테스트가 확인.
- 상태별 `reject_target` 분리 계수는 **미구현**(수리 가설이 먼저 확정되어 중단; 다음 work 몫).

## OS1-1 귀속 (격리 1 run `a7`, `--screen-watch-state 7`, 표본 3개)

- 표본: (244,222)·(339,151)·(462,170). 세 표본 모두 같은 run capture(`os1_stale.py`)에서 `stale`(candidate 블록 = nearest이고 독자 Scale2x ≠ nearest) 확인.
- present당 쓰기 순서(p30·p31 동일): slot0 = `0x4662DE`(0x466280 블록 복사, 기존 미러) 뒤 **`0x465F01`**(0x465E80 단색 사각형 내부, 스택 `0x40509B←0x4CB4D9←0x4B9102`)가 마지막; slot1 = `0x4662DE`만; slot2 = `0x4662DE` → `0x466E67`(후킹 guard 안) → `wined3d.dll` tid 288 `0x741299CF`가 마지막.
- 판정 PASS 기준(표본 3개 중 2개가 같은 writer)은 **미충족**(마지막 writer가 셋 다 다름). 그러나 슬롯0이 가리킨 `0x465E80`의 거부 로그가 직접 증거다: 후보 `layer_drift.jsonl`에 `{"why":"size","x0":200,"y0":210,"x1":564,"y1":230,"c":248,"stride":1600,"panel":0,"cache":0}` 13건(로그 상한 64건 중 51건은 stride 360 대상 거부로 소진). 사각형 폭 365 × 높이 21 = 7,665 px ≈ 정착 stale 8,793의 87%, 폭 365 > 320 → `g1_overlay_blt_accepts`가 거부. `menu_copy_calls` = present당 1(800×600 배경 복사) 확인.
- 공개: 슬롯1(배경 복사만)·슬롯2(wined3d 후행 쓰기)의 stale 원인은 이번에 귀속하지 못했다(UNKNOWN). 슬롯2의 wined3d 쓰기는 lap1148 PS20과 같은 계열(미복제 vtable 뒤 버퍼 호출)일 수 있으나 호출 지점 특정 안 함.
- 첫 시도 1: 후보 lane이 PS5 present barrier 타임아웃(`matching_records=0`)으로 FAIL(`new-game-path` 상태 5는 screen watch가 켜진 상태에서 도달 못함). 화면 watch run은 PS7 99 present 기록 뒤 중단 — 후속 측정은 watch 없이 실행했다.

## OS1-2 수리 1회 — `0x465E80` 폭 제한 해제(기본 켬, `SYW2_G1_RECT_SOLID_WIDE=0` 끔)

- `tools/inmm_stub/g1_mirror2x.c`(`8c924715ccbd`): `g_rect_solid_before` 800×600로 확대, `g_rect_solid_tile`·`g_rect_solid_wide_calls`·env `SYW2_G1_RECT_SOLID_WIDE` 추가. 폭>320 또는 높이>160인 사각형은 기존 `g1_overlay_blt_apply_tiled`로 적용(H-D2t 선례), 작은 사각형은 기존 `g1_overlay_blt_apply` 그대로, 끔이면 기존 `reject_size`. `g1_mirror2x.h`·`direct_draw_trace.c`(`ee3f5d06fa25`): `rect_solid_465E80_wide_calls` 노출.
- 테스트: `tests/test_g1_rect_fill.py::test_rect_solid_wide_rect_is_tiled_with_default_on_env_gate` RED(1 failed) → GREEN, 파일 32 passed.

## 측정 (공유 temp `20261007_lap1153_work_hos1/`, `os1_measure.json`)

| run | PS7 정착 HD min | PS7 정착 stale max | PS7 capture nearest 블록 | PS5 정착 HD min | PS9 |
|---|---|---|---|---|---|
| on1 | **99.627** | 1,790 | 798 | 98.801 | 100 |
| on2 | **99.627** | 1,790 | 798 | 98.801 | 100 |
| off1(`=0`) | 98.166 | 8,803 | 799 | 98.801 | 100 |

- off1은 lap1108/1109 기준값(98.166, 799)을 재현한다. PS7 `reject_size` off 149 = present 수, on `wide_calls` 155 = PS7 present 수(정확히 present당 1 호출).
- **판정: PS7 `partial`.** HD min ≥99.5 충족(99.627), 그러나 "nearest 블록 ≥80% 감소"는 **미충족**(799→798): 막대 내부는 단색이라 캡처 판별 블록 지표에 원래 없었고, 남은 stale 1,790 px는 막대·목록 **글자**(x200~360·y200~260, 글자 겉 테두리 포함)다. **PS5는 무변화(FAIL)** — 이 수리의 대상이 아님(PS5 stale 5,754는 x440~520·y120~260 글자 영역).
- 비회귀: NG5 `--new-game-start --new-game-act --new-game-play` 1 run(`ng5`, exit 0, PASS) PS3 2,984 present HD min **100**·PS9 100·hresult 0·fallback 0·scale2x PASS(mirror validator BLOCKED는 off1·lap1108과 동일 원인, 상태 5 요구 충족 판정 문제). ng5 `wide_calls` 누계 151 = 같은 run PS7 present 151개와 일치 → PS3에서 폭 > 320(또는 높이 > 160) 사각형 호출은 0(PS3 경로 동작 무변화), 그래도 규칙 확인용으로 save006 full pair 1 run(`pair`, exit 0) `status PASS`·`scene_state_equal true`·input_effect·minimap parity·V2/V2s/V2q/Scale2x gate 전부 PASS·`execution_source.unchanged true`(pair-result `d28b3baa662e`).
- ng5의 `rect_solid_465E80_reject_target` 8,016(전체 8,842 중), on1 1,597(1,842 중): 거부의 대부분은 stride 360 같은 **비화면 버퍼** 대상이다. 그 버퍼가 나중에 화면으로 복사되는 경로(미후킹 가능)가 PS5·PS7 남은 글자·버튼 stale의 유력 후보지만 이번에 확인하지 못했다(UNKNOWN).

## 변경 파일(전부 uncommitted)

`tools/inmm_stub/g1_screen_watch.h`·`g1_mirror2x.c`·`g1_mirror2x.h`·`direct_draw_trace.c`, `tools/g1_saved_scene_probe.py`, `tests/test_g1_screen_watch.py`·`tests/test_g1_rect_fill.py`. 스크립트(공유 temp): `scripts/run_os1.sh`·`run_ng.sh`·`os1_stale.py`·`os1_measure.py`·`os1_nr.py`.

## 실행·정리

디스크 66G→62G, `local/runtime/lap1153_os1_*/game` 사본 0개(자동 정리됨), 원본/참고 쓰기·`260921_temp`·APPROVALS 쓰기 0.

## 다음 행동

middle(Opus) 검수: raw 새 스크립트 재계산, 독립 재조립(현재 트리 DLL), 판정(PS7 partial·PS5 FAIL) 확인. 다음 work 제안 H-OS2: ① OS1-0 잔여 = `0x465E80`·TextOutA `reject_target`을 program state별·대상 buffer별 분리 계수(옵트인), ② PS5(`--screen-watch-state 5`)는 watch가 PS7→PS5 전환을 막으므로 `--screen-watch-state 5`를 PS5 진입 후 arm하는 방식 또는 watch 없이 상태별 계수만으로 귀속. 사용자 G1 시험 결과가 오면 최우선.
