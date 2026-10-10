# 2026-10-09 | lap 1220 | G1 middle — H-E2611G1-1 독립 검수 + H-E2611G1-2 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`/high, middle(중간계획·컨펌) 1 lap. 게임 run 0·제품/하네스 source 변경 0·커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1219 work, 원문 byte 일치 보존 `docs/history/laps/20261009_lap1220_preserved_lap1219_escalate_sol.txt` SHA256 `9bdab1849bef…`, 보존 뒤 삭제), STATUS "다음 한 가지", lap1217 사전등록 §4, INBOX 최신(18:53 root 메모·18:44 2611 정본). 새 사용자 지시·APPROVALS 반려·사용자 업스케일/G1 시험 결과 없음. `loop/STOP` 없음.
- 원본 안전: 2611 EXE `d9d6bb3d…` 직접 재계산 MATCH(읽기만). lap1219 lane 결과 4 run 전부 `source_unchanged` true(HQ2002 `b56986e0…`), `game_removed` true.

## 1. lap1219 독립 재계산(새 스크립트, trace 직접)

스크립트·산출: 공유 temp `20261009_lap1220_middle_review/recalc_lap1220.py` → `recalc_lap1220.json`(SHA256 `46e12d094f41…`). 두 lane `trace.sha256`은 파일 재계산과 4 run 8 lane 모두 일치.

| run | 상태 순서(candidate) | PS3 present / stale 합 / covered 최소 / p95·max | 안전 7종·hresult·success≠1·viewport 변경 | dropped / event_count | `ret_range_diag`(마지막 1줄) | private EXE |
|---|---|---|---|---|---|---|
| B0 | 9→7→5→3 | 266 / 0 / 480,000 / 8·12 | 전부 0 | 0 / 2,228 | b_kills 0·b_idle 0·textout_kills 0·textout_idle 492 | 두 lane 2611 |
| C1 | 9→7→5 (PS3 없음) | — (PS5 2,582 present stale 0·p95 27·max 53) | 전부 0 | 0 / 3,550 | 전부 0(PS5) | 두 lane 2611 |
| C2 | 9→7→5→3 | 4,577 / 0 / 480,000 / 12·58 | 전부 0 | 0 / 6,493 | b_kills 0·textout_idle 9,112 | 두 lane 2611 |
| C3 | 9→7→5→3 | 4,409 / 0 / 480,000 / 8·18 | 전부 0 | 0 / 6,392 | b_kills 0·textout_idle 8,778 | 두 lane 2611 |

- PS5·PS7·PS9도 4 run 전부 stale 0·안전 0·covered 480,000. install `active`/primitive success 1, `panel_foreign_writer_calls` 0. `scale2x_validator` PASS(candidate 4/4).
- baseline lane trace에는 `ret_range_diag` 0줄(끔 동작 = 이벤트 없음, E1-1 주장과 일치).
- C2 candidate 카메라 [91,54]→RIGHT [99,0]→DOWN [99,80]→LEFT [38,99]→UP **[0,57]** 직접 확인. `ps3_dwell_3.png` 열람: HUD 정상·월드 전부 검음(미탐색 구역) → "맵 밖/미탐색, 관측 부적합" 판정 수용. C3 `ps3_dwell_6.png`(candidate)·baseline 같은 장 열람: 본진 건물·일꾼·`대기 일꾼: 1`·미니맵(두 lane 모두 검은 마름모 = 시작 시야) 정상, 전투·배지 없음(국가는 lane마다 다름 = 무작위 시작).
- **판정: E1-0 PASS·E1-1 PASS·`.idle` 글자 관측 PASS(stale 0)·E1-2 `.kills` INCONCLUSIVE — work 주장과 불일치 0.**

정정 2(판정 영향 없음):
1. work 기록 "확인 클릭 1회 도착" → 실제는 PS7 확인 클릭(608,564)과 PS5 보조 확인 클릭(같은 좌표, `_start_new_game` 8초 대기 뒤 1회 재클릭) **두 번 모두** WndProc에 도착했다. 문제는 두 번째의 down→up 간격이다(§2).
2. work 기록은 candidate `mirror_validator` `BLOCKED`(nearest oracle 0.776)를 적지 않았다. 이것은 `--hd-source scale2x` new-game run의 기존 공개 진단 종류(lap1104·lap1135·lap1216 N1과 같은 0.776)이며 판정에 쓰지 않는다 — 공개 누락만 정정.

## 2. C1 PS5 정체 귀속(새 근거)

스크립트 `confirm_hold_survey.py` → `confirm_hold_survey.json`(SHA256 `30d6053d82dc…`): 공유 temp의 2026-10-xx work run 중 candidate input trace에 확인 좌표 (608,564) 클릭이 있는 **104 run**에서 WndProc `513`(down)→`514`(up) 간격과 PS3 도달 여부를 대조.

- PS3 도달 102 run: 모든 확인 클릭 간격 **≥104 ms**(하네스 X11 `--hold-ms 120`).
- PS3 미도달 2 run: **lap1184 K1(두 번째 간격 1 ms)**·**lap1219 C1(두 번째 간격 11 ms)**. 두 run 모두 PS5 시작 클릭(마지막)만 짧게 도착했다.
- C1 PS5 구간은 부하가 컸다(p95 27·max 53 ms, 정상 run 16~17). 게임이 바빠 X11 down/up이 WndProc에 거의 동시에 배달되면, 버튼 상태를 프레임마다 읽는 로비가 누름을 놓치는 것으로 설명된다. `_start_new_game`은 이 보조 클릭을 **한 번만** 하고 재시도하지 않으므로 그대로 PS3 timeout이 된다.
- **판정: C1(및 STATUS backlog lap1185 "lap1184 K1 후보 레인 PS5 정체 단발")은 하네스 입력 배달 결함으로 귀속(PLAUSIBLE, 104 run 완전 분리).** 제품(G1 DLL) 귀속 근거 없음: 실패 2건 모두 확인 클릭 전까지 stale 0·안전 0, 같은 DLL에서 102 run 정상. 수리는 하네스(§4 E2-0).

## 3. 독립 변이(저장소 밖 `/tmp/lap1220_mut`, lap1219 새 테스트 2개 대상)

`mutate_lap1220.py` → `mutations_lap1220.json`: 7종 중 **RED 5**(keys `or` 폴백 회귀·캡처마다 dwell 전체 sleep·캡처 이름 off-by-one·결과 키 삭제·dwell 창 분할) / **생존 2 = 테스트 공백**:
- m4 `dwell_captures > 0` → `> 1`: N=1 경계 미검사(테스트는 0·3만).
- m6 CLI `--new-game-play-keys none`이 `()` 대신 기본 키를 넣어도 통과: 테스트가 `NEW_GAME_PLAY_OVERRIDE`를 직접 넣고 CLI 파서는 소스 문자열만 본다. 런타임 C3(play segments 0)이 실제 동작을 보여 주므로 판정 영향은 없다.
비변이 원본 2 테스트 PASS. 변이 사본은 저장소 밖에서만 수정했다.

## 4. 결정 + 다음 work 사전등록 — H-E2611G1-2: 2611 세이브 로드·pair 기준선

**결정: (b).** `.kills` 배지는 UNKNOWN으로 backlog에 둔다. 근거: (1) lap1217 정적 정정대로 `.kills`의 `0x4664D0` 호출 4곳은 반환주소 화이트리스트 없는 일반 primitive B 미러로 간다 — 새 미러 경로가 아니다. (2) 전투를 만들려면 ~250 s 방치 패배 근처 체류(trace 상한 8,192: C3 225 s에 6,392)나 유닛 교전 입력이 필요해 비용 대비 근거가 작다. (3) 2611 사용자 시험판 전에는 save006 full pair를 대신할 2611 기준선이 필수(lap1217 §3 결정 2). 아래 run에서도 `--ret-range-diag`를 켜 `b_kills`가 0보다 크면 부수 관측으로 기록한다.

**가설:** 공식 2611 EXE는 HQ2002 save006(`616b7997…`)을 타이틀 불러오기로 읽을 수 있고(`.text`·데이터 배치 동일, 추가 섹션만 다름), 현재 G1 DLL은 그 장면에서 HQ2002 save006 full pair와 같은 gate를 통과한다.

| 단계 | 할 일 | PASS 조건 |
|---|---|---|
| E2-0 하네스 수리(§2) | `_start_new_game` 보조 확인 클릭을 PS5에 머무는 동안 최대 3회(간격 ≥4 s)로 늘리고 각 클릭을 결과에 남긴다. 테스트: 첫 보조 클릭 뒤 PS5 유지 → 재클릭, PS2/3 도달 → 추가 클릭 없음(RED→GREEN). 테스트 공백 m4(N=1)·m6(CLI `none` → `()` 배선)도 닫는다. | 테스트 RED→GREEN, 기존 new-game 테스트 통과 |
| E2-1 하네스 | `--esl2610 requires --new-game-path` 제한을 save006 saved-scene 경로에도 풀어 lane을 2611 private EXE로 실행(선택 배열 리다이렉트 재사용). lane 결과에 `private_exe_sha256` 기록. HQ2002 기본 경로는 byte·동작 불변. | 파서·lane 준비 테스트 RED→GREEN, HQ2002 경로 기존 테스트 통과 |
| E2-2 로드 가능성 | 2611·save006 타이틀 불러오기 1 run(팩 끔, `--hd-source scale2x`, `--ret-range-diag`, 장면 동작 없음 가능한 최소 옵션). | 두 lane PS3·tick>0 도달, 장면 상태(플레이어·유닛 수) 두 lane 동일, MessageBox·크래시 0, candidate stale 0·안전 0·dropped 0 |
| E2-3 pair 기준선 | E2-2 PASS면 save006 full pair 1 run(+재현 1 run): 기존 gate 그대로(입력효과 7/7·V2/V2s W-1 unexplained ≤2,000·V2q·Scale2x·minimap parity·steady stale). | 기존 HQ2002 full pair와 같은 gate PASS. 실패 항목은 HQ2002 lap1151 결과와 나란히 기록 |

**결론 규칙:**
- E2-2가 **두 lane 모두** 실패(로드 거부·크래시·즉시 패배) → save006은 2611과 비호환: `NOT_FEASIBLE(save006)`로 기록하고 증상·상태 순서만 남긴다. 다음 middle이 2611 안에서 만든 세이브 fixture로 갈지 정한다(이 회차에서 세이브 생성 금지).
- candidate만 실패 → `FAIL(귀속)`: 위치·계수·캡처만 기록, 수리는 다음 회차.
- E2-3 일부 gate 실패 → 하네스 좌표 문제(2611 UI 차이)인지 제품 차이인지 귀속만 하고 gate·validator는 바꾸지 않는다.
- E2-2·E2-3 PASS → `PASS(partial, 기술·격리)`, 다음 middle이 2611 시험판(a) 범위를 정한다.

**하지 않는 것:** G1 미러 로직·validator·gate 변경, 팩 켬, 시험판 재스테이징, 세이브 fixture 생성, G2/G5/G6/G7 접촉, 별도 2610/2611 세션 파일(`tools/esl2610_runtime.py`·`patches/esl2610/`·`tools/g2_esl2610_*`) 수정, 2611/원본 EXE·save006·`patch_history`·`260921_temp` 쓰기.

**검사:** 테스트 RED→GREEN, `make typecheck`, `make test`(`make lint`는 별도 세션 untracked F401 2건으로 실패할 수 있음 — 고치지 않고 기록), 변경 파일 ruff, SAFETY. 장기 run은 PID·`.exit` 파일로 끝까지 기다린다(`pgrep -f` 자기 일치 금지), run마다 `game` 사본만 삭제.

**우선순위 예외:** 사용자 업스케일 결과나 G1 시험 결과가 INBOX에 오면 그것이 최우선이다.

## 5. 검증

- focused `test_g1_saved_scene_probe.py`·`test_g1_new_game_path.py`·`test_esl2610_runtime.py` **301 passed/12.59s**(`.venv/bin/python`, 로그 `logs/gates/lap1220-middle-focused.log`). 처음 시스템 `python3`(Pillow 10.2)로 돌린 8 failed는 `Image.get_flattened_data` 부재 = 내 실행 환경 오류이며 Makefile `PYTHON=.venv/bin/python`(Pillow 12.1.1)에서는 통과 — 제품·하네스 결함 아님.
- 전체 `make check` SKIP: 이 회차 변경은 문서·공유 temp뿐, 루프 source는 lap1219 `make test` PASS 2218 그대로(바뀐 source 0).
- SAFETY·CONTEXT 결과는 STATUS에 적는다.

## 6. 다음 한 가지

work H-E2611G1-2(위 §4). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선.
