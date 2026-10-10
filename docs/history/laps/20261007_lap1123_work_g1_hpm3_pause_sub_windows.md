# 2026-10-07 | lap1123 | G1 work — H-PM3 PS23 불러오기·환경설정 하위 창 닫힘 HD 격리 실행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실구현) 1 lap. 커밋 0.
- 입력: STATUS 다음 한 가지(lap1122 사전등록 §3 `20261007_lap1122_middle_g1_hpm2_review_hpm3_preregistration.md`). INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP`·`ESCALATE_SOL` 없음(시작 시).
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만), 프로브가 매 run 두 lane `source_unchanged=true`. 원본/참고 쓰기 0.
- 가설 H-PM3: R-a(PS23 진입 스냅샷 복원)는 writer와 무관하므로 불러오기 창·환경설정 창을 닫은 뒤에도 같은 present에 HD가 돌아오고 정착 PS23 HD가 유지된다.
- 제품 C 변경 0(`g1_mirror2x.c` `98d261be…`·`g1_pause_snapshot.h` `cdcbc36b…` lap1122와 동일). 하네스·테스트만 변경.

## 변경 (전부 uncommitted)
- `tools/g1_saved_scene_probe.py`: 옵트인 `--new-game-menu-subs load,options`(`--new-game-menu` 필요, 없으면 현행 저장 창만·창 목록 불변). `PAUSE_SUB_WINDOWS`(불러오기 열기 (400,273)·닫기 (464,372) = 저장 창 돌아가기와 같은 위치, 환경설정 열기 (400,203)·닫기 **Esc만**), `parse_menu_subs`. 창 순서 `pause → save_window → pause_return → load_window → pause_return_load → options_window → pause_return_options → resume`. 불러오기 실행(316,372)·환경설정 창 안 클릭은 하지 않는다. 하위 창이 PS23으로 안 돌아오면 `sub_close[sub]="none"`·FAIL·순회 중단. 결과에 `sub_close`.
- 하위 창 순회는 창마다 dwell 3초(`NEW_GAME_MENU_SUBS_DWELL_SECONDS`): 게임 present trace 버퍼가 8,192 이벤트(`TRACE_MAX_EVENTS`)라 10초×8창이면 넘친다(아래 run a: dropped 5,662). 하위 창 없는 기존 경로는 10초 그대로.
- `tests/test_g1_new_game_path.py`: 하위 창 테스트 7개 추가(RED: `subs` 인자 없음 TypeError → GREEN 42 passed; 창 목록 불변·순서·클릭 금지 좌표·Esc 닫기·PS23 밖 하위 창 기록·미복귀 FAIL+중단·dwell 단축·옵션 배선/검증). 중간에 test 결함 1(Stuck 시나리오가 load_state=23이라 닫힘으로 보임) 고침.

## 실행 (격리 run 4회, `--hd-source scale2x --new-game-path --new-game-start --new-game-act --new-game-menu --new-game-menu-subs load,options`, 공유 temp `20261007_lap1123_work_hpm3/pm3_{a,b,c,off}`)
- a: dwell 10초 시안 — trace dropped 5,662로 load_window 이후 창 present 0 → **근거 제외**(하네스 수정 전 run, FAIL). 캡처로 불러오기 창·환경설정 창 열림·닫기 좌표(464,372)·Esc 닫기 확인.
- b·c: 수리 켬(dropped 0, exit 0). off: `SYW2_G1_PAUSE_SNAPSHOT=0`(exit 2 = 수리 끔 창 HD<90 결함 재현, 의도).
- 하위 창 상태: 두 하위 창 모두 PS23 유지(`states` load_window·options_window 23), 닫힘 후 PS23, resume PS3. 닫기: 불러오기 click, 환경설정 esc(전부 b·c·off 동일).
- 재계산 스크립트(공유 temp): `recalc_lap1123.py`(창별 HD)·`recalc2_lap1123.py`(닫힘 present·밴드 균일)·출력 `recalc_{a,b,c,off}.json`·`recalc2_lap1123.json`.

| run | 닫힘 창 | 닫힘 present stale / restore / HD | restore+stale | 다음 present covered 손실 | 정착 min / p50(n) |
|---|---|---|---|---|---|
| b | 불러오기 | 165 / 95,156 / 99.939% | 95,321 | 165 | 99.939 / 99.939 (396) |
| b | 환경설정 | 10 / 85,357 / 99.939% | 85,367 | 10 | 99.939 / 99.939 (406) |
| c | 불러오기 | 165 / 95,812 / 99.939% | 95,977 | 165 | 99.939 / 99.939 (389) |
| c | 환경설정 | 10 / 85,541 / 99.939% | 85,551 | 10 | 99.939 / 99.939 (387) |
| off | 불러오기 | 96,562 / 0 / 79.857% | 96,562 | **44,622** | 79.857 / 90.678 (402) |
| off | 환경설정 | 86,288 / 0 / 79.990% | 86,288 | **34,795** | 79.990 / 90.718 (409) |

- 기준 대조(사전등록 PASS 항목, b·c 공통): 닫힘 present HD ≥98.6 ✓(99.939)·정착 min ≥98.6 ✓·restore+stale vs off 같은 present stale ±2%: 불러오기 b −1.29%·c −0.61%, 환경설정 b −1.07%·c −0.85% ✓·닫힘 다음 손실 ≤1,000 ✓(165/10)·PS3 resume 창 71 present HD 100% ✓·act 창 PS3 min 99.946(c select/drag; b 100%)·V1 outside·안전 7종 0·fallback 0·success_min 1·`trace_dropped_count` 0·scale2x validator PASS·p95 7~8ms(off 7ms, 증가 ≤1ms) ✓·캡처 열람: run a `load_window.png`·`options_window.png`·`pause_return_options.png`, run b `pause_return_load.png`(깨짐·흑색 띠 0; 환경설정은 Esc로만 닫고 창 안 클릭 0이라 값 변경 경로 없음, run c·off 캡처 육안 열람은 생략).
- 밴드 2×2 균일 비율(하위 창 − 메뉴 패널: 불러오기 x240..313·x486..559, 환경설정 x257..313·x487..543, y100..409): pause.png → pause_return_*.png — 불러오기 b 75.53→75.66·c 75.82→75.93, 환경설정 b 75.77→75.42·c 75.73→75.40(Δ ≤0.35%p ✓), off 77.14→99.36·76.90→99.26(결함 재현).
- 공개 한계: 하위 창 열림 present 복원/stale·이탈 직전 복원 계수는 판정 middle(저장 창과 같은 51.7k 열림 복원 패턴: save 51,636/51,850, load 51,705/51,973, options 51,672/51,908 — 같은 메뉴 패널 영역 스냅샷 값). 영구 잔여는 불러오기 닫힘 165 px(lap1121 458과 다른 act 장면)·환경설정 닫힘 10 px. 모든 PS23 하위 창이 PS23 유지라 state 귀속 필요 없음. `mirror_validator` BLOCKED는 lap1121 이전부터 동일(nearest oracle 장면 불일치, 게이트 아님). 불러오기·설정 변경·세이브 쓰기 0. 부하 대표성 낮음.

## 판정(work 보고, 최종은 middle)
- **H-PM3 `PASS(partial, 기술·격리)`**(b·c 2/2, 하위 창 2개 모두; off 대조가 두 하위 창 결함을 재현해 판정 제외 조건 없음). partial 사유: 부하 대표성 낮음·영구 잔여 165/10 px writer 미귀속·열림·이탈 복원 판정 middle·dwell 3초(하위 창 순회만).
- 원본 SHA MATCH·game 사본 없음(하네스가 run 끝에 지움)·전부 uncommitted.

## 검사
- 하네스 변경 뒤 `make lint typecheck` PASS. 전체 `make check`·`checks/safety.sh check`는 아래 STATUS 검사 줄에 보강.

## 다음 행동
middle(Opus) 검수: b·c raw에서 닫힘 present·밴드·PS3 present를 새 스크립트로 재계산하고 PASS(partial) 수용 여부를 정한다. 수용되면 남은 HD coverage(승패 화면·타이틀·혼자하기 대기실·PS2 로딩)를 사전등록.
