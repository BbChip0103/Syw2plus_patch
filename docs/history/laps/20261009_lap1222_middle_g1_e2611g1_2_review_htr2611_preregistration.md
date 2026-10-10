# 2026-10-09 | lap 1222 | G1 middle — H-E2611G1-2 검수 · 2611 시험판 (a) 결정 · H-TR2611 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`/high, middle(중간계획·컨펌) 1 lap. 게임 실행·제품/하네스 source 변경·커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1221 work, 원문 byte 일치 보존 `docs/history/laps/20261009_lap1222_preserved_lap1221_escalate_sol.txt` SHA256 `6b62dbad6cc4…`, 보존 뒤 삭제), STATUS "다음 한 가지", lap1220 사전등록 §4, INBOX 최신(18:53 root 메모·18:44 2611 정본). 새 사용자 지시·APPROVALS 반려·사용자 업스케일/G1 시험 결과 없음. `loop/STOP` 없음.
- 원본 안전: 2611 EXE `d9d6bb3dca11…` 직접 재계산 MATCH(읽기만). 3 run 6 lane 전부 `source_unchanged` true(HQ2002 `b56986e0…`)·`game_removed` true.

## 1. 독립 재계산(새 스크립트, trace·pair-result 직접)

스크립트·산출: 공유 temp `20261009_lap1222_middle_review/recalc_lap1222.py`(`b0c67273…`) → `recalc_lap1222.json`(SHA256 `7027ff68b2e2…`). 6 lane `trace.sha256` 기록값 = 파일 재계산, JSON 깨진 줄 0.

| run | pair status · 장면(재계산) | 게이트 6종 | candidate PS3 present / stale 합 / covered 최소 / p95·max | PS9·PS35 | 안전 8종·hresult·success≠1 | 두 lane EXE |
|---|---|---|---|---|---|---|
| e22 | PASS · 같음(8인·559) | 전부 PASS | 789 / **0** / 476,474 / 7·13 | stale 0 | 전부 0 | 2611 |
| e23_1 | PASS · 같음 | 전부 PASS | 788 / **257**(1 present) / 476,556 / 7·12 | stale 0 | 전부 0 | 2611 |
| e23_2 | PASS · 같음 | 전부 PASS | 789 / **668**(2 present) / 476,556 / 8·13 | stale 0 | 전부 0 | 2611 |

- V2s production unexplained 190/198/194(≤2,000), loaded 135/30/24 — work 값 일치. HQ2002 lap1151 pair 직접 재확인: PASS·게이트 6종 PASS·production unexplained 200·PS3 896 present stale 0·candidate 상태 순서 같음.
- e22 `ret_range_diag` 마지막 줄 `b_kills` 15·`b_idle` 0·`textout_kills` 8·`textout_idle` 1,536 — work 값 일치.
- 캡처 열람 `e23_2/candidate/production.png`: 건물 선택·HUD·초상 줄·미니맵 정상, 깨짐 없음.
- **판정: E2-1·E2-2·E2-3 work 주장과 수치 불일치 0.**

정정 2(판정 영향 없음):
1. **stale 시점.** work 기록 "후반(game_tick 232.08M~232.22M, 캡처 production 구간) 단발 stale"은 틀렸다. game_tick 값은 절대 시계일 뿐이다. 실제는 PS3 진입 뒤 **3.1 s(PS3 present 순번 63, e23_1·e23_2 둘 다)와 4.4 s(순번 88, e23_2)**로, 약 39.7 s PS3 구간의 앞쪽이다. 입력 trace 대조: 세 present 모두 **하네스 클릭 down 직전 4~33 ms의 present**(63 = 미니맵 왼클릭 (129,571) 0.55 s 뒤·건물 클릭 (450,195) 직전, 88 = 생산 버튼 (668,540) 직전)이고, 다음 present에서 0으로 돌아왔다. 세 present 모두 stale이 `primitive_stale_pixels_total` 증가분과 같다(primitive 재호출 경로 안 stale). e22는 같은 순번 63이 클릭 down 6 ms **뒤**였고 stale 0. trace에 위치 필드가 없어 위치·writer 귀속은 UNKNOWN 그대로다.
2. **E2-0 런타임 미실행 공개 누락.** e22·e23은 save006 로드 경로라 `_start_new_game`(확인 클릭 재시도)을 지나지 않는다. E2-0은 단위 테스트로만 확인됐고 실제 run 증거는 0이다.

## 2. 독립 변이(저장소 밖 `/tmp/lap1222_mut`, 끝나고 삭제)

`mutate_lap1222.py`(`1ab54927…`) → `mutations_lap1222.json`(`38bbc0c6…`). 판정 기준 = 변이 없는 사본에서 녹색인 `tests/test_g1_new_game_path.py` 76개 + `tests/test_g1_saved_scene_probe.py -k "esl2610 or main or parser or option"` 9개. (사본 트리에서는 scroll-orchestration 테스트 70개가 경로 의존 fixture 때문에 변이 없이도 실패하므로 기준에서 뺐다. 실제 저장소에서는 통과 — §4.)

| 변이 | 결과 |
|---|---|
| m1 최대 클릭 3→99 | RED |
| m2 재시도 간격 제거(wait 0) | RED |
| m3 PS2/3 도달 뒤에도 클릭 | RED(3) |
| m4 `>=`→`>`(4회) | RED |
| m5 `--esl2610` 무시 | RED |
| m6 `--new-game-path` 요구 복원 | RED |
| m7 클릭 결과 대신 빈 기록 | **생존** |
| m8 간격 4→3 s | RED |

RED 7/8. 생존 1 = 테스트 공백(사양 "각 클릭을 결과에 남긴다"의 내용 검사 없음, 개수만 검사). 판정 영향 없음(E2-0은 런타임 미실행이고 판정 근거가 아님) — 다음 work가 단언 한 줄로 닫는다.

## 3. 결정 — (a) 2611 사용자 시험판 먼저, e23 단발 stale은 backlog

근거:
1. e23 stale은 3 present(2,366 PS3 present 중), 각 233~435 px, 다음 present 해소, 안전 0, 게이트 영향 0. lap1116이 같은 종류(단발 primitive stale)를 일시 stale로 닫은 선례가 있다.
2. trace에 위치가 없어 귀속에는 screen-watch 위치 run이 따로 필요하고, 클릭 직전 한 present라는 위상 조건이라 재현 비용이 크다(e22에서는 위상이 어긋나 0).
3. 사용자가 실제로 쓰는 EXE는 2611이다. 지금 사용자에게 가 있는 시험판(lap1151 `8a3837fb…`)은 HQ2002용이고 `.bat`가 `[HQ]Syw2plus 2002.exe`를 띄운다. 그 뒤 기본 켬 가시 수리(H-OS1·H-PS5W1 PS5/PS7 글자 등)도 쌓였다.
4. lap1217 결정 순서 (c)→(b)→(a)에서 (b)가 이번에 PASS(partial)됐다.

e23 stale backlog 재개 조건: 아래 H-TR2611 확인 pair 2 run에서 stale present가 다시 생기고 클릭 직전 위상이면 위치 run(screen-watch) 한 회차를 연다. 사용자 보고에 클릭 순간 깜빡임이 있으면 바로 연다.

## 4. 다음 work 사전등록 — H-TR2611: 2611 사용자 시험판 스테이징

**가설:** 현재 트리 G1 DLL(팩 끔, Scale2x)을 2611 게임 폴더의 `_inmm.dll`로 놓고 2611 EXE를 띄우는 `.bat`로 실행하면, 확인 pair가 lap1221 e23과 같은 게이트를 통과한다.

| 단계 | 할 일 | PASS 조건 |
|---|---|---|
| TR-0 테스트 공백 | m7: `_start_new_game` 결과 `clicks` 항목이 `_inject` 반환값 그대로인지 단언(RED→GREEN) | 변이 m7 RED |
| TR-1 확인 pair | lap1221 e23 명령 그대로(`--hd-source scale2x --esl2610 --candidate-no-present-trace --candidate-no-unit-ticks`) save006 pair 2 run | 두 run pair `status` PASS, 두 lane 2611 EXE, 장면 같음, 안전 0. stale present는 위치(순번·PS3 진입 뒤 시간·다음 클릭까지 ms)로 기록 |
| TR-2 새 게임 경로 | 2611 `--esl2610 --new-game-path --new-game-start --new-game-play` 1 run(E2-0 재시도의 첫 런타임 증거) | PS9→7→5→3 도달, 확인 클릭 수 기록, stale 0(일시 stale은 공개), 안전 0 |
| TR-3 스테이징 | 공유 temp `<이번 회차>/user_test_staging/`에 `_inmm.dll` = **TR-1 첫 run `bridge/_inmm.dll` byte 그대로**, `.bat` 2개 = lap1151판과 같은 환경변수 4개·ASCII, direct판은 실행 파일 이름(주석 포함)만 `[ESL]Syw2plus 2611.exe`. via_dxwnd판은 `dxwnd.exe`를 띄우므로 EXE 이름이 없다 — DxWnd 대상 EXE 지정은 사용자 DxWnd 설정 몫이라는 점을 기록(APPROVALS 공개용). **안내문 txt 금지**(사용자 지시 2026-10-07). 각 파일 SHA256 기록, lap1151판 `.bat`와의 diff가 EXE 이름 줄뿐임을 기록 | 파일 3개, diff 확인 |

**하지 않는 것:** 제품 C·validator·gate 변경, 팩 켬, `260921_temp`·`patch_history`·원본/2611 EXE·save006 쓰기, APPROVALS 수정(다음 middle 몫), 별도 2610/2611 세션 파일(`tools/esl2610_runtime.py`·`patches/esl2610/`·`tools/g2_esl2610_*`) 수정, G8/G9 변형 EXE 측정.

**결론 규칙:** TR-1 실패 → 스테이징 하지 않고 실패 항목을 e23과 나란히 귀속만. TR-2 PS5 정체 → 재시도 클릭 기록과 함께 FAIL 귀속(스테이징은 TR-1만으로 진행 가능). 모두 PASS → `PASS(partial, 기술·격리)`, 다음 middle이 검수 뒤 APPROVALS에 2611 시험판 요청을 쓰고 root 대상 `loop/ESCALATE_SOL`로 `260921_temp` 배치를 넘긴다.

**검사:** 테스트 RED→GREEN, `make typecheck`, `make test`(`make lint`는 별도 세션 untracked F401로 실패할 수 있음 — 고치지 않고 기록), 변경 파일 ruff, SAFETY. 장기 run은 PID·`.exit` 파일로 끝까지 기다리고 run마다 `game` 사본만 삭제.

**우선순위 예외:** 사용자 업스케일 결과나 G1 시험 결과가 INBOX에 오면 그것이 최우선이다.

## 5. 검증

- focused 결과·SAFETY·CONTEXT는 STATUS에 적는다. 전체 `make check` SKIP: 이번 회차 변경은 문서·공유 temp뿐, 루프 source는 lap1221 `make test` PASS 2228 그대로(바뀐 source 0).
- STATUS 압축: 원문 128줄·SHA256 `ae177b61c756…`를 `docs/history/20261009_status_lap1222_precompaction.md`에 byte-exact 보존.

## 6. 다음 한 가지

work H-TR2611(위 §4). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선.
