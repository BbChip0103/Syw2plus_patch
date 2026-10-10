# 2026-10-07 | lap1122 | G1 middle — H-PM2 독립 검수(사전등록 이탈 판정·기준 대체) + H-PM3 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1121 work → middle 검수 요청), STATUS 다음 한 가지, lap1121 기록, lap1120 사전등록 §3. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1122_preserved_lap1121_escalate_sol.txt`로 byte 일치 보존(SHA256 `caa74463ccc740e3…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: lap1121 raw만 사용(run a·b 수리 켬, off = `SYW2_G1_PAUSE_SNAPSHOT=0`; 새 게임 경로 → act → Esc PS23 → 저장 창 → 돌아가기 → 계속하기, 저장 실행 없음). artifact SHA: trace_raw a `eccb5aea…`·b `6d2353c2…`·off `99108ce5…`, new-game-path-result a `025bfdd4…`·b `ce677f83…`·off `32a42815…`.
- source 동일성: `g1_pause_snapshot.h` `cdcbc36b…`·`g1_mirror2x.c` `98d261be…`·`g1_mirror2x.h` `815b58e6…`·`direct_draw_trace.c` `6bf459cb…`·`Makefile` `d9184cfe…`·`tests/test_g1_pause_snapshot.py` `fb6e3979…`·probe `54c8abbb…`(lap1119/1120과 같음 = 하네스 변경 0 확인). lap1121 full check 로그(`44deea70…`, 06:11:15) 뒤 수정된 tools/tests/checks/patches 파일 0.
- 코드 검토(`g1_mirror2x.c` present 루프): 복원은 `pause_restore_on && !hd_asset`(기존 HD 우선)이고 `g1_pause_restore_pick`이 RESTORE일 때만 `g_covered`·`g_expected_snapshot`·`g_mirror` 2×2를 스냅샷에서 쓴다. 스냅샷은 23 진입 present에서 기존 판정 HD 픽셀만 저장, 23 진입·이탈 양쪽에서 valid 전부 0. 버퍼 할당 실패 시 기능만 끈다. 사전등록 §3 PM2-0과 일치, 결함 없음.

## 1. 독립 재계산 (새 스크립트)

- 스크립트: 공유 temp `20261007_lap1122_middle_review/recalc_lap1122.py`(`883e74cd…`) → `recalc_lap1122.json`(`79cfb28f…`), `locate_residual.py`(`7ce0c587…`) → `locate_residual.json`(`046ee632…`). 열림·닫힘 present는 work 스크립트 정의를 쓰지 않고 present 계수(partial copy 99,200 증가 직전 present, 저장 창 구간 뒤 stale+restore 최대 present)로 다시 찾았다.

| run | 열림 present seq: stale / restore / HD | 닫힘 present seq: stale / restore / HD | 닫힘 다음 present covered 손실 | 정착 PS23 min·p50(n) | PS3 min(n) | p95 |
|---|---|---|---|---|---|---|
| a | 4897: 0 / 51,703 / 99.876% | 6544: **458** / **96,162** / **99.879%** | 479,876→479,418 = **458** | 99.879·99.879(1,250) | 100(1,751) | 7ms |
| b | 4892: 0 / 51,704 / 99.876% | 6588: **458** / **96,160** / **99.879%** | 479,876→479,418 = **458** | 99.879·99.879(1,283) | 100(1,745) | 7ms |
| off | 4910: **51,704** / 0 / 89.105% | 6604: **96,618** / 0 / **79.845%** | 479,876→435,213 = **44,663** | 90.648·90.669(1,295) | 100(1,746) | 7ms |

- fallback 0·hresult≠0 0·success≠1 0(3/3). 복원 이벤트는 run마다 3개뿐: 열림 51,703/51,704, 닫힘 96,162/96,160, PS23 이탈 약 20 present 전 101(a 7774·b 7851).
- **정정 1(전사):** work 기록의 "닫힘 present HD 99.876%"는 실제로 열림 present 값이다(work 스크립트 `close_present` 키가 첫 restore>0 present = 열림 present를 잡음). 닫힘 present HD는 **99.879%**(a·b). 둘 다 ≥98.6%라 판정 영향 없음.

## 2. 이탈 판정

- **이탈 1(닫힘 복원 96,162 vs 사전등록 40k~46k) — 수용, 원인 = lap1120 사전등록 범위 산정 오류.** 닫힘 present에서 on의 (restore + stale) = 96,620/96,618 = off의 닫힘 stale 96,618과 같다. 즉 복원 집합은 off에서 stale이던 집합 전부에서 458을 뺀 것이다. off에서 그 stale은 띠(다음 present 영구 손실 44,663) + 메뉴 패널 영역(다음 present 패널 copy가 재덮음 96,618−44,663 = 51,955)이다. 그러므로 on 복원 = 띠 약 44,205 + 패널 영역 약 51,957(교차 run 산술). lap1118 재계산(복귀 stale 95.4k 중 패널 재덮음 51.3k)이 이미 패널 몫을 보여 줬는데 lap1120이 띠만으로 범위를 잡았다. 캡처 확인: b의 정착 `pause_return.png` on↔off 논리 픽셀 차이 10,479 = 띠 10,086 + 패널 **0** + 바깥 393(바깥 393은 `pause.png` on↔off 차이와 같은 위치 x218..252·y543..575 = 수리 무관). 영구 효과는 띠에만 있다(a는 act 장면이 off와 달라 바깥 16,953 차이, 패널 0은 같음).
- **이탈 2(열림 present 복원 51,703/51,704 vs 0 기대) — 수용, 거짓 복원 아님.** off의 같은 present stale이 정확히 51,704이고 on은 그 present stale 0이다. 복원 조건이 "화면 픽셀 == 진입 스냅샷 값"이므로 그 present에 실제로 보이는 논리 색의 HD 2×2를 낸 것이다(미러 밖 열림 그리기로 생기던 1 present 일시 stale을 가림, 원인 writer는 그대로). PS23 이탈 직전 101 px도 같은 조건의 일시 복원이며 off에서 그 구간은 띠 nearest가 이미 남아 있어 대조 불가 — 공개 잔여로 둔다.
- **띠 2×2 균일 ≤10% 기준 — 폐기·대체.** 기준이 잘못 산정됐다(Scale2x HD 상태의 평지 띠도 균일 블록 76.7~77.4%). 대체 기준과 결과:
  - (i) 같은 run `pause.png` 대비 `pause_return.png` 띠 균일 비율 차 ≤1%p: a 76.72→76.72, b 77.36→77.37 **PASS**; off 77.36→99.36(결함 재현).
  - (ii) `pause.png`↔`pause_return.png` 띠 논리 픽셀 차이: on a 725·b 727 vs off 10,813. on 차이 중 304는 같은 논리 색에 2×2 세부만 다른 픽셀(lap1120 공개 한계 "패널 값 == 월드 값 약 1,840 px는 닫힌 뒤 패널 HD 유지"), nearest로 바뀐 것 a 231·b 234(닫힘 영구 손실 458의 보이는 부분). 패널 207·우측 124 차이는 off와 같은 값 = 메뉴 hover/커서, 수리 무관.
- **H-PM2 판정: `PASS(partial, 기술·격리)` 수용.** 사전등록 PASS 항목(닫힘 HD ≥98.6·정착 min ≥98.6·PS3 100·안전/V1/fallback/hresult/dropped 0·scale2x PASS·p95 증가 0·열림 present ≥89·off 결함 재현)은 2/2 충족, 이탈 2건은 위 근거로 수용, 띠 기준은 대체 기준 (i) PASS. partial 사유: 영구 잔여 458 px(0.095%, 닫힘 때 진입 스냅샷과도 다른 값 = 위치는 띠 안 추정, writer 미귀속)·진입 present stale 291(off 동일, 아래)·저장 실행/불러오기/옵션 하위 창 미측정·부하 대표성 낮음.
- 진입 present stale 291(첫 PS23 present, on·off 모두, 이후 PS23 내내 nearest): lap1117 PM0 b와 다른 상태(act 뒤 진입) — 원인 미조사, 0.061%, backlog.

## 3. 다음 work 사전등록(Sonnet) — H-PM3: PS23 다른 하위 창(불러오기·환경설정) 닫힘 HD

- **가설 H-PM3:** R-a는 writer와 무관하므로 PS23의 다른 하위 창(불러오기 창·환경설정 창)도 닫힌 뒤 같은 present에 HD가 복원되고 정착 PS23 HD가 유지된다. 하위 창이 PS23을 벗어나면(state ≠ 23) 스냅샷이 무효화돼 복원되지 않는다 — 그 경우 FAIL이 아니라 새 귀속으로 기록한다.
- **PM3-0 하네스(TDD):** `tools/g1_saved_scene_probe.py` `_new_game_menu_window`에 옵트인 하위 창 순회 옵션(예: `--new-game-menu-subs load,options`; 없으면 현행 저장 창만, 기존 경로 불변).
  - 메뉴 버튼 논리 좌표는 lap1121 캡처(`pause_return.png`) 기준 추정: 계속하기(400,132)·게임목적(400,168, 회색)·환경설정(400,203)·저장하기(400,238)·불러오기(400,273). 실행 전 캡처로 확인하고 다르면 고친다.
  - 각 하위 창의 "돌아가기"/닫기 좌표는 첫 run에서 하위 창 캡처로 찾는다. **불러오기 실행·확인 버튼과 환경설정 값 변경 버튼은 절대 누르지 않는다**(세이브 로드·설정 파일 쓰기 방지). 닫기 버튼이 없으면 Esc를 시도하고 결과 state를 기록한다.
  - 창 이름: `pause` → `load_window` → `pause_return_load` → `options_window` → `pause_return_options` → `resume`(각 dwell·캡처). 단위 테스트 RED→GREEN(순서·클릭 금지 좌표 미포함·옵션 없을 때 기존 창 목록 불변).
- **PM3-1 격리 run:** 수리 켬 2회 + 수리 끔(`SYW2_G1_PAUSE_SNAPSHOT=0`) 1회, `--hd-source scale2x --new-game-path --new-game-start --new-game-act --new-game-menu` + 하위 창 옵션.
  - **PASS(켬 2/2, 하위 창마다):** 닫힘 present HD ≥98.6%·정착 PS23 min ≥98.6%·닫힘 present (restore+stale)가 off 같은 present stale의 ±2% 안·닫힘 다음 present covered 손실 ≤1,000 px·PS3 HD 100%·V1/안전 7종/fallback/hresult 0·dropped 0·scale2x PASS·경과 p95 증가 ≤2ms·`pause_return_*.png` 띠(하위 창 − 메뉴 패널 영역, 캡처로 사각형 확정) 균일 비율이 같은 run `pause.png` ±1%p·캡처 정상.
  - off 대조가 하위 창 닫힘 결함을 보이지 않으면(손실 ≤1,000) 그 하위 창은 "결함 없음"으로 기록하고 PASS 항목에서 제외한다.
  - 열림 present·이탈 직전 복원 계수는 공개만(판정 middle). 하위 창이 state ≠ 23이면 그 사실·state 값·HD 수치를 기록하고 수리 없이 넘긴다.
  - **FAIL:** 위 항목 미달. 구현·하네스·좌표 결함이면 같은 회차에 고쳐 재실행(구현 우선). 실패 가설 2회 또는 60분이면 BLOCKED로 근거와 함께 넘긴다.
- 공통: 하네스 변경 뒤 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 158GiB 여유), game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지, 시험판 재스테이징 없음(lap1104 판본 유지). 사용자 G1 시험 결과가 들어오면 그것이 최우선이다.

backlog 추가: H-PM2 영구 잔여 458 px writer·위치, 진입 present stale 291(act 뒤 PS23 진입), PS23 이탈 직전 복원 101. 그 뒤 남은 HD coverage(승패 화면·타이틀·혼자하기 대기실·PS2 로딩)는 STATUS 순서대로.

## 4. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS에만 쓴다.
- 전체 `make check` SKIP: 이번 변경은 문서뿐이고 하네스·테스트·C source는 lap1121 full PASS(1745) 때와 같다(머리 source 동일성).

## 다음 한 가지

work(Sonnet): §3 H-PM3 — PM3-0 하위 창 순회 옵션(TDD) → PM3-1 격리 켬 2회 + 끔 1회 → 하위 창별 PASS/FAIL, middle 검수 요청.
