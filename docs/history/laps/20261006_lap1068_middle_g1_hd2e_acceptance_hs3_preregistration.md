# 2026-10-06 | lap1068 | G1 middle — H-D2e 독립 검수 + H-S3 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간계획·컨펌) 1 lap. 게임 실행·제품 source·하네스·테스트 변경 0, commit 0.
- 입력: lap1067 work `loop/ESCALATE_SOL`(SHA256 `dd5c05157887cf8945910d76f06603aa4361c9dab528490620942ead8ed70eee`, 원문 아래 부록) → 처리 뒤 삭제.
- 가설(검수 대상): lap1066 §3 H-D2e — 가장자리 마우스 스크롤도 키 hold와 같은 화면 경로를 타므로 현재 후보에서 hold 창 stale·성능이 키 hold와 같은 수준이다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` 직접 재계산 MATCH. fixture: 비합성 save006(D-2 위/아래 가장자리 왕복), lap1067 e1·e2 산출물만 읽음.

## 1. 독립 재계산(work `analyze_d2e.py` 미사용)

공유 temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1068_middle_review/`:
`recalc_lap1068.py` `7e24f147…1d8e` → `recalc_lap1068.json` `249be776…f67b`.
입력 pair-result SHA 접두 e1 `5679852f0922`·e2 `a816764b7e65`(ESCALATE 기재와 일치), candidate trace `5672faee…`·`fe722edf…`, stale_mask SHA = pair-result 기재 값(2 run).
키 hold 대조: lap1065 nd1·nd2(같은 save006 D-2 왕복·같은 tick 계획) 같은 스크립트로 재계산.

| 항목 | 사전등록(lap1066 §3) | middle 재계산(e1 / e2) | work 보고 | 판정 |
|---|---|---|---|---|
| E-0 이동 | 두 lane ≥1칸·같은 칸 수·최종=시작·clamp 기록 | baseline·candidate 모두 UP (158,101)→(134,77) **24칸**·DOWN →(158,101) **24칸**, 관측 25개·전부 대각 1칸 단위·clamp_free true, 두 lane 카메라 관측열 **동일**(2/2 action), 최종 snapshot (158,101) | 동일 | 일치·PASS |
| E-0 입력 tick | 목표 tick | 24692/24692·24788/24788, release tick 24716/24812(관측 −12), release_reason `release_tick` | 동일 | 일치 |
| E-0 실제 포인터 입력 | (BLOCKED 아님 증명) | 게임 측 `GetCursorPos` 494회 중 logical **(400,0) 24회 연속**(UP) → (400,300) → **(400,599) 23/24회 연속**(DOWN) → (400,300); input trace에 WM_KEYDOWN/UP(256/257) **0**(513/514/516/517 클릭만), `game_wm_keydown` null·`receiver_waived_for_edge` true | 실제 포인터 | 일치·PASS |
| E-1 | hold p95 ≤ 고정+16·tps 비 ≥0.95 | hold(24692..24824) p95 **7/7**(고정 7/7)·비 **1.0021/1.0021** | 동일 | 일치·PASS |
| E-2 | hold 창 stale 합 ≤10 | ps3 idx 123..291(169개) 합 **1/1**(idx 125 단발)·최대 1·>100 0 = 키 hold nd1/nd2와 **같은 위치·같은 값** | 동일 | 일치·PASS |
| 마지막40 | 0 | 0/0(ps3 1,179/1,179) | 0 | 일치·PASS |
| stale_mask | — | 40 프레임(0..1170/30) 중 0번만 16,985 px(로드 과도), 나머지 0 | — | 정보 |
| pair·안전·cleanup | PASS·0·true | gate 10개 전부 PASS(input_effect·minimap·terrain_scroll_parity·loaded·scroll_after·V2·V2s·V2q·scale2x), 안전 7종 max 0, cleanup ok·game_removed·prefix 프로세스 0(4 lane), source_unchanged true·source SHA 원본 | 동일 | 일치·PASS |

결정론 확인: e1·e2 candidate ps3 stale 열 전체(1,179개) 해시 `8052cfdb4afd`로 같다(trace 파일 해시는 다름).
**관찰(비차단):** e1 DOWN 구간 `GetCursorPos` y=599 기록이 23회(e2 24회)인데 카메라 이동은 두 run 모두 24칸이다. 게임 이동량은 in-process 카메라 관측으로 판정하므로 영향 없음(입력 trace 표본 수는 판정 근거가 아니다).

## 2. 코드 검토(`tools/g1_saved_scene_probe.py` `a80bb317…`, `tests/test_g1_saved_scene_probe.py` `368e06a6…`, 둘 다 git 미추적)

- `_scroll_edge_point`: x = origin+400·scale(가운데 열), UP = origin y(첫 행), DOWN = origin y+600·scale−1(마지막 행), release = origin+300·scale. `origin`·`scale`은 `_run_lane`의 content 창 `xwininfo` 좌표와 `2 if candidate else 1`(크기 1600×1200/800×600 검증 뒤) → 두 lane 같은 logical 좌표. 실측 GetCursorPos logical (400,0)/(400,599)/(400,300)과 일치.
- `_send_pointer_edge`: scroll용 X11 연결 재사용 후 HEAD에 이미 있던 `x11_mouse_click._move`(`XTestFakeMotionEvent(screen −1)`+`XFlush`)만 호출. 버튼 이벤트 없음.
- `_send_scroll_until_camera_change(send_edge=)`: 기본값 None이면 `_send_key_edge` 그대로 → 기존 키 경로 불변. finally에서 up(=가운데 복귀) 보장.
- 슬롯 루프: edge면 루프 전에 포인터를 가운데로 두고, keyup 대기 0초, `valid`에서 receiver 요구만 면제(`terrain_scroll_edge or (...)`). 그 외 tick barrier·snapshot·scroll_motion_ok 조건은 키 hold와 같다. `terrain_scroll_hold = terrain_scroll_hold or terrain_scroll_edge` → release tick 의미 동일.
- `_scroll_edge_option_error`: `--terrain-scroll` 필요·hold/keys 배타(keys 기본 `DOWN,RIGHT` 비교), main은 edge면 `UP,DOWN` 강제.
- 테스트 4개(좌표·주입·배타·배선 문자열) 직접 실행: `-k "edge or scroll"` **127 passed/2.56s**.
- 판정: 결함 없음. 한계: 위/아래 가장자리·가운데 열만, 좌우·모서리·사람 속도 포인터 이동 미측정.

판정: **H-D2e PASS(partial) 수용** — E-0·E-1·E-2·비회귀 사전등록 기준 전부 충족. 키 hold와 가장자리 마우스 스크롤 모두 save006 D-2 왕복에서 비진단 stale이 idx 125 1 px만 남는다. 제품 G1 마감·사용자 승인은 아니다.

## 3. work H-S3 사전등록(다음 work, Sonnet) — 두 번째 장면(save000) 스크롤

근거: D-2 스크롤 측정·수리(H-D2z~H-D2e)는 전부 save006이다. save000(두 번째 장면)은 `_scene_option_error`가 `--scene-actions none`을 강제하고 none은 `--terrain-scroll`을 거부해 고정 카메라 stale만 측정됐다(STATUS "두 번째 장면" 미충족). tick 계획은 `_build_common_tick_plan(loaded_tick)`으로 장면 독립이고, 스크롤 블록(`if terrain_scroll:` 3819~)은 save006 전용 selection/drag/minimap/production 뒤에 있다.
가설: 현재 후보는 다른 맵(save000)의 키 hold 스크롤에서도 hold 창 stale이 save006 수준(≤10)이다. 아니면 새 미후킹 writer가 드러난다.

1. **S3-0 하네스(테스트 먼저 RED→GREEN):** `--scene-actions none` + `--terrain-scroll`(+`--terrain-scroll-hold` 또는 `--terrain-scroll-edge`) 결합을 허용하고, none이면 save006 전용 장면 동작만 건너뛰고 스크롤 블록을 실행한 뒤 종료한다. terrain-trace·rice·scroll-phase와 none 결합 거부는 유지, save006 기본 경로·기존 테스트 불변. `--p4b-s-snapshot`의 lap888 reference는 save006 전용이므로 save000에서는 쓰지 않거나(비-snapshot barrier 경로) 거부 사유를 기록한다.
2. **카메라 방향 선택:** save000 로드 카메라를 먼저 읽고, 24칸 왕복이 clamp 없이 되는 방향 쌍(`--terrain-scroll-keys` UP,DOWN/DOWN,UP/LEFT,RIGHT 등)을 고른다. 근거를 기록한다.
3. **실행:** save000 키 hold 비진단 pair 2(순차, load ≤8, `--stale-mask`에 hold 창 포함). hold 창 합 >10이면 진단 1회(`--layer-drift --screen-watch --drift-samples` 3점)로 writer 귀속까지(수리는 다음 회차). 비회귀로 save006 키 hold nd 1 run.

PASS 기준:
- S3-1: 두 lane 같은 카메라 관측열·≥1칸 이동·최종 = 시작·clamp 기록·`terrain_scroll_parity` PASS.
- S3-2: hold 창 p95 ≤ 고정+16·tps 비 ≥0.95.
- S3-3: hold 창 stale 합 ≤10. 초과면 FAIL이 아니라 새 잔여로 기록하고 표본 귀속까지.
- 비회귀: 안전 7종 0·cleanup·source_unchanged·마지막40 0, save006 nd hold 창 합 1 유지. save000 V2계열 capture gate BLOCKED(`scene-actions none`의 required tag 부재)는 기존 사유로 공개하며 gate 의미는 바꾸지 않는다.
- BLOCKED: settle barrier·tick barrier가 save000에서 실패하면 원인을 추적해 하네스를 고치고 재실행(구현 우선). 같은 세션 3회 수리 뒤에도 설명 불가일 때만 근거와 함께 인계.
- FAIL: 크래시·안전 위반·두 lane 이동 칸 수 불일치가 2 run 재현.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·CONTEXT, focused(`test_g1_saved_scene_probe`·`test_g1_rect_fill`·`test_g1_mirror2x`·`test_g1_overlay_blt`). 결과는 STATUS에만 보강한다.
- 전체 `make check` SKIP(문서만 변경, source·하네스는 lap1067 full PASS 1647과 같은 해시; 다음 work H-S3가 하네스 변경 뒤 실행).

## 다음 한 가지

work(Sonnet) H-S3: §3 S3-0 하네스 → save000 키 hold pair 2 → (필요 시 진단 1) → save006 nd 비회귀 1 → `make check`. 그다음 후보: 좌우 가장자리·모서리 스크롤, HUD/GDI, G1 사용자 승인 요청 준비. backlog: save006 lap1056 r1 부하 동반 stale, 미후킹 `0x467E60`, 진단 동반 영역 x301..334·y357..398, save000 overlay BltFast rejects, 다중 팝업 heal, hold keydown 위상 경합. G6/G7은 사용자 합격(APPROVALS lap989) 대기, 루프를 막지 않는다.

## 부록: lap1067 `loop/ESCALATE_SOL` 원문(byte 그대로)

```
lap1067 work(Claude Code claude-sonnet-5-5) 역할 경계 인계 — H-D2e(가장자리 마우스 스크롤) 하네스 구현·실행 완료, 사전등록 기준 work 자체 계산상 전부 충족. work는 자기 결과를 승인하지 않으므로 fresh Opus middle 독립 재계산이 필요하다.
승격 작업자가 할 일:
1. 공유 temp /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261006_lap1067_work_d2e/ 의 {e1,e2}/pair-result.json·candidate/trace_raw.jsonl 을 work 스크립트(analyze_d2e.py) 없이 새 스크립트로 재계산. pair-result SHA 접두: e1 5679852f0922, e2 a816764b7e65.
2. 검증 항목: E-0 baseline·candidate 모두 UP (158,101)→(134,77) 24칸·DOWN →(158,101) 24칸·clamp 없음·최종=시작·두 lane 카메라 관측열 동일(camera_observations)·input tick 24692/24788 = 목표; E-1 hold 창(down_input_tick..right_observation_tick) p95 7(고정 7)·tps 비 1.0021; E-2 hold 창(down_input_tick..final_observation_tick, ps3 idx 123..291) stale 합 1(idx 125 단발)·마지막40 0; pair gate 전부 PASS·안전 7종 0·cleanup ok·source_unchanged true; edge 모드가 실제 포인터 입력임(actions[].scroll_edge true·receiver_waived_for_edge true·키 receiver 미요구).
3. 코드 검토: tools/g1_saved_scene_probe.py `_scroll_edge_point`(UP=origin y 행·DOWN=origin y+600*scale-1·release=가운데)·`_send_pointer_edge`·`_send_scroll_until_camera_change(send_edge=)`(기본 경로 불변)·`_scroll_edge_option_error`·슬롯 루프의 edge 분기(receiver 면제·keyup 대기 0초·시작 전 포인터 가운데)·`terrain_scroll_hold = terrain_scroll_hold or terrain_scroll_edge`. 테스트 4개(tests/test_g1_saved_scene_probe.py 끝). 수용 시 다음 work(HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비 중 선택) 사전등록.
기록 docs/history/laps/20261006_lap1067_work_g1_hd2e_edge_mouse_scroll.md. 변경은 tools/g1_saved_scene_probe.py·tests/test_g1_saved_scene_probe.py(둘 다 git 미추적, uncommitted)뿐이며 제품 C/bridge 불변.
```
