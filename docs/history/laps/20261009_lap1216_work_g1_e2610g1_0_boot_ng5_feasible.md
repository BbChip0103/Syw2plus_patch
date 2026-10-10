# 2026-10-09 | lap 1216 | G1 work — H-E2610G1-0: 현재 G1 DLL을 공식 ESL 2610 EXE에서 켜기(가능성 판정)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`/high, work(실무) 1 lap. 하네스·테스트 변경만(제품 C 변경 0), 커밋 0.
- 입력: STATUS "다음 한 가지"(work H-E2610G1-0), lap1215 middle 사양 §5. INBOX 새 사용자 지시 없음(마지막 = lap1215 처리 메모), APPROVALS 새 반려·시험 결과 없음, `loop/STOP`·`loop/ESCALATE_SOL` 없음(시작 시 확인).
- 가설: DLL 계약·훅 바이트가 2610에서 같으므로 현재 트리 G1 DLL(팩 끔·기본 env)은 2610 EXE에서 1600×1200 미러로 타이틀→대기실→인게임까지 안전 0으로 동작한다. 깨지는 곳은 위험 ①~⑤ 중 하나로 귀속된다.
- 사전등록 PASS/FAIL: E0-0 RED→GREEN / E0-1 테스트 RED→GREEN·플래그 없으면 기존 동작 동일 / E0-2 두 lane PS3 도달·훅 설치 실패 0·안전 7종 0 / E0-3 입력 효과 두 lane 같음·PS3 stale·안전 0·p95 HQ2002와 나란히.
- 원본 SHA: `[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac`·2610 EXE `c5530cf4…3938d` 직접 재계산 MATCH(실행 뒤 재확인도 MATCH). 모든 run `source_unchanged` true 2/2. 격리 game 사본·prefix·빈 Xvfb, 팩 끔·`--hd-source scale2x`, fixture 없음(새 게임). `game` 사본은 lane 종료 때 이미 지워졌다(잔존 0, prefix·output 보존).

## 0. 변경 파일(모두 uncommitted; 같은 파일들에 lap1099~1215 미커밋 변경이 이미 있다)

- `tests/test_g1_scratch_bltfast.py`(`b4936ce51a2d`): **E0-0** 단언 2개. (a) `adopt`의 `has_record` 분기가 `HeapAlloc`·`lpVtbl` 변경보다 앞서 `return;`으로 끝남(변이 m2), (b) `scratch_bltfast_at_present`의 마지막 문장이 큐 `reset`(변이 m3). 6 passed. 저장소 밖 사본(`/tmp/lap1216_mut`)에서 m2 → `test_scratch_bltfast_adopts_an_uncloned_back_buffer_vtable` RED, m3 → `test_scratch_bltfast_flush_diffs_against_expected_before_the_present_loop` RED, 원본 복원 GREEN.
- `tools/g1_saved_scene_probe.py`(`0087623ba00e`): **E0-1** `--esl2610`(`--new-game-path` 필요, 없으면 `parser.error`). 모듈 전역 `ESL2610`(기본 False), `_prepare_lane_game`(끔 = 기존 `runtime_env.prepare` 호출 그대로, 켬 = 2610 EXE SHA 검사 뒤 `esl2610_runtime.prepare`, manifest에 `esl2610_overlays`), `_selection_array`(2610은 `SELECTION_ENTRIES_VA`·100칸), `_selection_slots`·`_selection_observation` 일반화, `_selection_memory`(켬일 때 runtime_env가 `0x899028`에서 읽는 첫 슬롯 읽기를 2610 배열로 돌림; count `0x899024`는 그대로). `esl2610_runtime.py`·`runtime_env.py`·`patches/esl2610/`는 읽기·import만(수정 0).
- `tests/test_g1_saved_scene_probe.py`(`281cfbb4bd3a`): 새 테스트 4개(준비 경로·선택 배열 분기, 잘못된 EXE 거부, 플래그 기본 끔·`--new-game-path` 요구, 선택 읽기 리다이렉트 범위). 추가 전 RED(3 failed, 속성 부재) → GREEN.
- 하네스 실행 스크립트(공유 temp `20261009_lap1216_work_e2610g1/scripts/`): `run.sh`(`e1ed0a0eac28`), `ana.py`(`17f8d9a5400e`).

## 1. E0-2 부팅 probe (run B0: `--esl2610 --new-game-path --new-game-start`, 1 cycle, 수리 불필요)

공유 temp `20261009_lap1216_work_e2610g1/run_B0/`(`new-game-path-result.json` `54dd6bfd0cb1`), exit 0·status PASS.

- (a) **MessageBox·`_inmmserv.exe` 대기: 없음.** 두 lane `probe.log`에 MessageBox 0, 새 게임이 PS3까지 진행(위험 ① 비발현).
- (b) candidate `mirror2x_install` active·`primitive_install_success` 1·`install_status` active→complete, `set_display_mode` 800×600×8 → 전달 1600×1200 7회·hresult 0(나머지 5회는 640×480×32 구조적 skip, HQ2002와 같은 패턴).
- (c) 상태 순서 **PS9→PS7→PS5→PS3**, 두 lane 모두 PS3 도달·`new_game_start` PASS. 캡처 `candidate/ps3_start.png` 1600×1200, 자원 5000/5000·인구 20/1500(2610 상한 표시) 육안 확인. 하네스 클릭 좌표는 2610 메뉴와 그대로 맞았다(위험 ② 창모드 HQCDD: ddraw 경로 정상, 비발현).
- (d) present(264 PS3·716 PS5·156 PS7·65 PS9): stale 전부 0, `covered` 480,000, 안전 7종(`fallback`·`hd_mask_outside`·팔레트 위반·viewport 복원 실패·cache clip verify 실패·clip replay 불일치·identity key 불일치)·hresult≠0·success≠1 전부 0. `scale2x_validator` PASS(`hd_mask_outside` 0). `mirror_validator` BLOCKED = 이미 HQ2002 NG5(`run_NON` 6,982 present, 같은 `nearest oracle 0.776`)에 있는 scale2x 켬의 기대 결과라 비교 불가 항목(lane `status` PASS는 HQ2002와 동일 기준).
- (e) 훅 설치 실패·old bytes 불일치·primitive verify 실패: 0(`primitive_install_success` 1, `textout_iat_install_mismatch` 0, `dropped_count` 0). → **판정 NOT_FEASIBLE 조건 없음.**
- (f) `0x4664D0` 패널 관련(위험 ③): `panel_unbound_transfers`·`panel_lock_failures`·`panel_pointer_mismatches`·`panel_foreign_writer_calls` 0, `panel_bound_transfers` 264. 2610 고유 `.kills`/`.idle` 오버레이가 패널 화이트리스트 밖에서 호출한 흔적은 이 구간(대기실~PS3 시작)에서 관측되지 않았다.

## 2. E0-3 인게임 NG5

### N0 (키 RIGHT,DOWN,LEFT,UP×2, hold 20·dwell 56 — HQ2002 NON과 같은 명령) → FAIL, 원인 둘 모두 하네스·게임 동작

- **하네스 결함(수리):** candidate `new_game_act` select slot이 0·`building_selected` false. 원인 = `runtime_env._read_selection`이 첫 슬롯을 옛 주소 `0x899028`에서 읽음(위험 ④). `_selection_memory` 리다이렉트로 수리(E0-1 보강, 위 §0).
- **게임 동작(제품 결함 아님):** 두 lane **모두** PS3 ~250 s 뒤 "패배했습니다"(결과 화면, `baseline/ps3_play.png`·`candidate/ps3_play.png`: 우리 병사 7·건물 18~19, 컴퓨터 병사 75~115·건물 270~299). 2610 AI는 방치한 플레이어를 약 4분 안에 이긴다(HQ2002 NG5는 PS3 유지). candidate는 PS27·PS29로 넘어가 present가 9,815개로 늘고 trace 이벤트 상한 8,192를 넘겨 `trace_dropped_count` 2,701 → act FAIL. 결과 화면 구간(PS27 951·PS29 206 present)은 stale 0·안전 0.
- PS3 4,990 present 중 stale>0 은 2개(114 px @tick 223751126, 2 px @223814527), 다른 run에서 **재현되지 않음**(N1 0/4,305). 미귀속 관측으로 기록(위치·계수만, 사양대로).

### N1 (키 RIGHT,DOWN,LEFT,UP — 패배 전에 끝나게 줄임) → PASS, exit 0

`run_N1/new-game-path-result.json`(`7bbeaafb88ff`).

- 입력 효과 두 lane 같음: select slot 1198 count 1(둘 다), produce building 1199 selected·rice 5000→4200·used 20/20(둘 다; wood 4700/5000 차이는 아래 주), drag/move effect true·1198 추적 1. `new_game_start`·`new_game_play`·`new_game_act` 두 lane PASS, 한 번도 결과 화면으로 넘어가지 않음.
- candidate PS3 **4,305 present stale 0**, PS5 684·PS7 156·PS9 62 stale 0, 안전 7종·fallback·hresult 전부 0, trace dropped 0, `scale2x_validator` PASS.
- elapsed_ms p95(PS3): **9**(max 83), HQ2002 NON(lap1214) 6(max 12)·NOFF 8(max 61). 같은 2610의 N0은 6(max 14)·B0 PS3 7(max 22)이라 N1의 9는 호스트 부하 변동으로 판단한다(실행 중 load average 3.7~6, 같은 호스트에서 별도 2610 세션 run 병행). PS5·PS7·PS9 p95는 HQ2002와 15~17 ms로 같다.
- 차이 하나: N1 produce wood가 baseline 5000→4700·candidate 5000→5000. 새 게임은 **시작 국가가 무작위**(`players[0].nation`: N1 baseline 2·candidate 1, B0 2·1, HQ2002 NON 1·3; N0은 둘 다 2)라 시작 건물/유닛(`units` 타입 구성)이 lane마다 달라 생산 비용이 다를 수 있고, 이 변경과 무관한 기존 하네스 성질이다. rice 5000→4200·used 20/20·selected 1198/1199는 두 lane 같다.

## 3. 판정

**`FEASIBLE`** — E0-2(PS3 도달·훅 설치 실패 0·안전 0)·E0-3(N1: 입력 효과 같음·PS3 stale 0·안전 0·p95 허용 범위) PASS. 현재 G1 DLL이 수정 없이 2610에서 켜진다. 위험 ①(MessageBoxW)·②(HQCDD)·③(`0x4664D0`, 이 구간)은 발현하지 않았고, ④(선택 배열)·⑤(`Data`→`ESLData`)는 하네스에서 이미 수리됨/무관(게임이 정상 부팅해 새 게임 데이터를 읽음). 이번 회차에서 고친 것은 하네스뿐이고 제품 C는 그대로다.

- partial 사유: 격리 Wine·새 게임 대기실→인게임 ~84 s 구간만. 2610의 `.kills`/`.idle` 오버레이가 실제로 그려지는 장면(전투 중 킬 수 표시 등)·세이브 로드·저장 fixture(save006 pair)·팩 켬은 미검증. N0의 일시 stale 114 px는 미귀속.
- 2610 게임 동작 주의: 방치한 플레이어는 ~250 s에 패배. 긴 장면 probe(장기 스크롤 등)는 이 동작을 고려해야 한다(건물·유닛 방어 또는 짧은 시나리오).

## 4. 검증

- 호스트 테스트: `tests/test_g1_saved_scene_probe.py` + `tests/test_g1_scratch_bltfast.py` + `tests/test_esl2610_runtime.py` **230 passed**(`.venv/bin/python`; 시스템 Python의 Pillow 10.2에는 `get_flattened_data`가 없어 8개가 실패하므로 Makefile의 `.venv`를 쓴다). `ruff` 통과.
- 실게임 run 3(B0·N0·N1) = 공유 temp `20261009_lap1216_work_e2610g1/`. 디스크 205 GB 여유.

## 5. 다음 한 가지

middle 독립 검수(저장소 밖 새 스크립트로 trace 재계산) 뒤 **2610 전환 범위 결정**: (1) 사용자 시험판을 2610용으로 묶을지, (2) HQ2002 pair 기준선(save006 pair)을 2610에서 다시 만들 수 있는지(세이브가 2610에서 로드되는지)와 `Data`→`ESLData` 자산 경로, (3) 장면 확대(2610 `.kills`/`.idle` 오버레이·전투 장면)를 다음 work probe로 할지.

## 6. 사후 주의(작성 뒤 발견)

- 실행 B0·N0·N1은 모두 **2610 EXE `c5530cf4…`**로 돌았다(각 lane `private_exe_sha256` 직접 확인). 이 기록 작성 뒤 별도 2610 세션이 `tools/esl2610_runtime.py`를 **2611 핫픽스 EXE(`[ESL]Syw2plus 2611.exe` `d9d6bb3d…`, overlay `patch_history/[ESL]Syw2plus 2611`)**로 바꿨다(`ESL2610_EXE`·`ESL2610_SHA256`). `--esl2610`은 그 모듈 값을 그대로 따르므로 지금 다시 돌리면 2611로 부팅한다. **이번 FEASIBLE 판정은 2610 EXE 기준이고 2611은 미검증**이다. 호스트 테스트(`test_g1_saved_scene_probe.py` 등)는 EXE 경로·SHA를 monkeypatch해서 변경 뒤에도 230 passed. 다음 회차는 2611에서 B0 한 run으로 재확인(같은 코드 경로)을 먼저 한다.
