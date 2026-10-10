# 2026-10-09 | lap 1221 | G1 work — H-E2611G1-2 2611 세이브 로드·pair 기준선

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`/high, work(실무) 1 lap.
- 가설: 공식 2611 EXE는 HQ2002 save006(`616b7997…`)을 타이틀 불러오기로 읽고, 현재 G1 DLL은 그 장면에서 HQ2002 save006 full pair와 같은 gate를 통과한다(lap1220 middle 사전등록 §4).
- 예상 PASS/FAIL: E2-2 두 lane PS3·tick>0·장면 상태 동일·MessageBox/크래시 0·candidate stale 0·안전 0·dropped 0. E2-3 기존 pair gate PASS(입력효과 7/7·V2/V2s W-1/V2q/Scale2x·minimap parity). 두 lane 모두 로드 실패면 `NOT_FEASIBLE(save006)`.
- 변경 파일(uncommitted, 하네스·테스트만, 제품 C·DLL·validator·gate 변경 0): `tools/g1_saved_scene_probe.py`(`f00c09cfec05`), `tests/test_g1_new_game_path.py`(`da7ea9272480`), `tests/test_g1_saved_scene_probe.py`(`166d455c50038f`).
  - **E2-0** `_start_new_game`: 보조 확인 클릭을 PS2/3 도달 전까지 최대 `NEW_GAME_CONFIRM_MAX_CLICKS=3`회, 간격 `NEW_GAME_CONFIRM_RETRY_GAP=4.0` s로 재시도(첫 클릭 전 대기 8 s는 그대로, 각 클릭은 `clicks`에 남음). 테스트(RED→GREEN): 1회 만에 시작 → 추가 클릭 0, PS5 유지 → 재클릭(2회), 끝까지 PS5면 정확히 3회에서 멈춤, 클릭 간격 ≥4 s. 기존 "정확히 1번" 테스트는 1회 만에 시작하는 의미로 정정(재시도 정책이 바뀐 것이므로). 사양 공백 m4(`dwell_captures` N=1 → `ps3_dwell_1` 캡처+`dwell_captures` 결과)·m6(`NEW_GAME_PLAY_OVERRIDE["keys"] = ()` 배선 소스 단언) 닫음.
  - **E2-1** `--esl2610`의 `--new-game-path` 요구 제거(`parser.error` 삭제, help 갱신): 같은 `_prepare_lane_game`(2611 EXE SHA 검사)·선택 배열 리다이렉트가 save006 saved-scene lane에 그대로 쓰인다. 기존 "필요" 테스트를 `main(["--esl2610"])`가 `validate_original_source` 센티널까지 도달함(`ESL2610=True`, 옵션 없으면 False)으로 교체. `--esl2610` 없는 HQ2002 경로는 코드 동일(`ESL2610` 기본 False).
- 원본/후보 SHA: HQ2002 원본 `b56986e0…` 두 lane `source_unchanged` true·`game_removed` true. 두 lane 비공개 EXE = **2611 `d9d6bb3d…`**(`private_exe_sha256` 직접 확인). fixture save006 `616b79978917…`·플레이어 8·유닛 559(두 lane 동일, `scene_state_equal` true). 팩 끔, `--hd-source scale2x`.
- 실행(모두 `PYTHONPATH=. .venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1221_… --artifact-root <공유 temp>/20261009_lap1221_work_e2611g1_2/… --hd-source scale2x --esl2610 …`, setsid nohup, `.exit` 0):
  - E2-2: `e22`(`--ret-range-diag`; 로그 `logs/gates/lap1221-e22.log`) `pair-result.json` `2d66104b7f6e`.
  - E2-3 pair 1·2: `e23_1`·`e23_2`(`--candidate-no-present-trace --candidate-no-unit-ticks`, lap1151 표준 명령에 `--esl2610`만 추가; `lap1221-e23-{1,2}.log`) `dc4fb0b021d6`·`44d6b1563e56`.
  - 요약 스크립트 `<공유 temp>/scripts/summarize_e2.py` `f7ace4d01af0`(pair-result·trace 직접 읽기).
- 측정·판정:

| run | status | 장면 상태 | input_effect | minimap | V2/V2s/V2q | Scale2x | mirror present(PS3 789/788/789) | 안전·outside diff·palette |
|---|---|---|---|---|---|---|---|---|
| e22 | PASS | 동일(8·559) | PASS | PASS | PASS×3 | PASS | 1070 | 0 |
| e23_1 | PASS | 동일 | PASS | PASS | PASS×3 | PASS | 1065 | 0 |
| e23_2 | PASS | 동일 | PASS | PASS | PASS×3 | PASS | 1050 | 0 |

  - V2s unexplained(production): 190/198/194 ≤2,000(W-1), V2s **raw** production FAIL은 3 run 모두(HQ2002 lap1151 production도 raw FAIL·unexplained 200 — 같은 공개 진단 패턴). loaded unexplained 135/30/24(HQ2002 36), 나머지 태그 33~232.
  - PS3 candidate trace: stale 합 **e22 0**(ret-range-diag 켬)·**e23_1 257(1 present, seq 1422)**·**e23_2 668(2 present: seq 1406 435, seq 1431 233)**, 나머지 present 0. covered 최소 476,474~476,556(캡처 시 팝업 영역)·PS35·PS9 stale 0. p95 7~8 ms·max 12~13 ms. fallback 0, success 최소 1, dropped_count 0(e22 summary 이벤트; e23은 `--candidate-no-present-trace`라 summary 줄 없음). HQ2002 lap1151 같은 장면 stale 0 present. → **e23의 단발 stale 3 present는 후반(game_tick 232.08M~232.22M, 캡처 production 구간) 일시 stale로 공개**하고 귀속은 UNKNOWN(전체 시간순 재현 시 e22는 0, 같은 코드·장면; 2회 중 2회 발생이라 우연이 아닐 수 있으나 pair gate에는 steady stale 항목이 없음).
  - `.kills` 부수 관측: e22 `ret_range_diag` `b_kills` **15**·`b_idle` 0·`textout_kills` 8·`textout_idle` 1,536 — 2611 save006 장면에서 `.kills` 일반 primitive B 경로가 15회 호출됐고 같은 구간 stale 0(candidate PS3 789 present stale 0). 호출은 미러 경로를 지났으므로(stale 0) lap1220 backlog `.kills` UNKNOWN을 부분 완화(관측 증거; 배지 시각 확인은 아님).
  - 캡처 열람(`e22/candidate/production.png`): 건물·HUD·대기 일꾼·미니맵 정상, 깨짐 없음.
- 판정: **E2-0 PASS·E2-1 PASS·E2-2 PASS·E2-3 PASS(2/2, 표준 gate)** → `PASS(partial, 기술·격리)`. 한계: 팩 끔(Scale2x 폴백)·save006 한 장면·사용자 시험 아님·steady stale/pair 픽셀 전수 비교는 별도.
- 호스트 검사: 변경 파일 `ruff` 통과, `make typecheck` PASS, focused `test_g1_new_game_path.py`·`test_g1_saved_scene_probe.py` **301 passed**(RED→GREEN: 새 테스트 3 RED(속성 부재)). `make test`·SAFETY·CONTEXT 결과는 STATUS에 적는다. `make lint`는 별도 2610 세션 untracked 파일 F401 외부 실패일 수 있음(고치지 않음).
- 회귀 / 남은 위험: e23 단발 stale 귀속 UNKNOWN(다음 한 가지 후보), 2611 시험판(a) 범위 미정(middle), `.kills` 배지 시각 확인 UNKNOWN. 원본·2611 EXE·save006·patch_history·260921_temp 쓰기 0, game 사본 3개 삭제, `local/runtime/lap1221_*` output·manifest·prefix 보존.
- 다음 한 가지: middle이 독립 재계산(pair-result·trace)·E2 판정 수용 후 (a) 2611 사용자 시험판 범위 결정. 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선.
