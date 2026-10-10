# 2026-10-07 | lap1140 | G1 middle — H-TM0 독립 검수, 사용자등록 팝업 stale 위치 확정, H-TM1 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행·C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1139 work → middle 검수 요청, `f4d3866a…`). INBOX 새 사용자 지시 없음(마지막 = root 12:53 전달·재개, lap1139 처리 메모), APPROVALS 새 반려·사용자 시험 결과 없음(lap1136 재요청 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문 byte 일치 보존 `docs/history/laps/20261007_lap1140_preserved_lap1139_escalate_sol.txt`(SHA256 `f4d3866affaf9a0e…`, `cmp` 일치) 뒤 삭제. middle 대상 요청이므로 이번 회차가 처리한다(root 대상 아님).
- 가설: lap1139 수치·판정이 raw에서 그대로 재현되고, 사용자변경 PS9 팝업 stale는 팝업 영역에 있다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- source 대조: `tools/g1_saved_scene_probe.py` `b8fa67498b0c`·`tests/test_g1_new_game_path.py` `6d970743391d` = lap1139 기록 일치. lap1139 최종 `make check` 로그 `logs/gates/lap1139-work-full-check2.log` 끝줄 **1796 passed·5 skipped/781.98s**, `.exit`=0 직접 확인.
- fixture: 없음(lap1139 raw 재사용, 새 실행 없음).

## 1. 새 스크립트 재계산(하네스·work `recalc_tm0.py` import 없음)

공유 temp `20261007_lap1140_middle_review/`: `recheck_lap1140.py`(`995ba12b3a1d`) → `recheck_lap1140.json`(`67226747d4bb`), `scale2x_popup_lap1140.py`(`f525f4eb791d`, 독자 Scale2x 구현) → `scale2x_popup_lap1140.json`(`47b77ac71570`). 입력 = lap1139 최종 4 run + srccheck/user의 raw trace jsonl·PNG.

| run | 결과 JSON SHA(기록 대조) | 후보 present 구간 (내 계산) | 안전·dropped | 모드 호출(PS9 뒤) |
|---|---|---|---|---|
| scenario | `0ac4393d0b2e` 일치 | PS9 73 → **PS15 1,076**: 첫 100·나머지 min/p50 100/100·stale 0 | 9종 max 0·success min 1·hresult≠0 0·두 lane dropped 0·bad line 0 | 0 |
| user | `9ebbdf2da1a2` 일치 | **PS9 1,793**: 첫 100 → 나머지 min/p50 **84.1002/84.1002·stale max 76,319**(첫 stale = present 65, 마우스 업 21 ms 뒤, 뒤 절반 값 76,319 하나뿐 = 정착), covered 480,000 고정 | 동일 0 | 0 |
| prologue | `cd35a5819ce5` 일치 | PS9 1,101 100/100 | 동일 0 | 후보 PS30 `640×480×16→640×480`·`800×600×8→1600×1200` 1쌍(시도 1회), baseline PS30 동일 1쌍(800×600 유지) |
| charroom | `fe793fa01895` 일치 | PS9 1,045 100/100 | 동일 0 | 0 |
| srccheck/user | `dd8bc80405e9` 일치 | PS9 1,764: 84.1002/84.1002·76,319 | 동일 0 | 0 |

- 캡처 레이아웃(후보 vs baseline nearest-2x 차 비율): scenario 0.0541·user 0.0513 → lap1139 표 일치. 메뉴 대비 변화 bbox도 일치(user baseline `[190,145,670,524]`·후보 `[380,290,1087,1049]`).
- 이전 시도 보존물 대조: user stale 76,319가 prelim·attempt2·attempt3·attempt4·최종·srccheck **6 run 전부 동일**(기록의 "5 run"보다 1개 더). prelim prologue 후보 PS30 모드 호출 4개(시도 2회) → attempt2부터 2개(1회) = 결함 2 수리 효과 확인. attempt 단계의 FAIL은 전부 게이트(열 비교·최종 상태) 판정이며 화면 수치는 run마다 같다 → 결함 1~4 수리는 측정값을 바꾸지 않고 판정 방식만 고쳤다. **타당.**
- 캐릭오픈방 가드: 소켓 표본 127회(`ss_samples.txt` 타임스탬프 줄 127) 중 wine·`.exe`·Syw2plus 문자열 0, 두 lane `probe.log` socket/connect/dplay/wsock 0 → 기록 일치.
- **불일치 0.** 정정 1: 재현 run 수 "5 run" → srccheck 포함 6 run(수치 동일, 판정 영향 없음). 공개 1: 트레이스 상태 열은 하네스 `trace_states`(관측 창 안)와 내 전체 열이 다르다(예: scenario baseline 전체 트레이스에는 PS15 14줄이 있으나 하네스 창 열은 `[9]`). 기록이 이미 "트레이스 열은 공개만"이라 판정 영향 없음. 내 `recheck_lap1140.json`의 `blocks_popup_190_145_544_525`·`blocks_outside_popup` 필드는 상자를 넓게 잡고 바깥 계산이 전체와 같게 나온 스크립트 결함이라 쓰지 않는다(아래 §2의 `scale2x_popup_lap1140.json`이 대체).

## 2. 사용자등록 팝업 stale 위치 확정(C 변경 없이 캡처로)

팝업 논리 창 = x256..543·y145..455(캡처 열람 판독, 면적 약 89.3k = lap1139 추정과 같음). 독자 Scale2x(baseline)와 후보 캡처를 2×2 블록 단위로 비교했다(Scale2x ≠ nearest인 "판별 가능" 블록만 셈).

| 캡처 | 팝업 안: 판별 가능 / 후보=nearest(stale 증거) / 후보=Scale2x | 팝업 밖 stale 증거 |
|---|---|---|
| user `user_inplace_a`(최종·srccheck 동일) | 23,501 / **21,656(92.2%)** / 1,607 | 653 |
| 대조 charroom·prologue(같은 PS9 메뉴, HD 100%) | 19,191 / **0** / 19,191 | 614·617 |
| 대조 scenario(PS15) | 19,775 / 0 / 19,775 | 198 |

- 팝업 밖 600여 블록은 HD 100% run에도 같은 수준으로 있으므로 캡처 시점·커서 잡음이다. **stale는 팝업 안에 있다.** stale 76,319 ≈ 팝업 면적의 85%.
- 팝업 안 세부(블록 왼쪽 위 칸 기준): 초상화 상자 2,103/2,107·위 테두리·제목 1,413/1,445·오른쪽 아래 1,652/1,686·왼쪽 띠 494/495가 nearest, **ID 버튼 열은 181/636만 nearest**. present 계수도 맞물린다: 팝업 열림 뒤 `bbox_calls`가 present당 9 → 13(+4 = 버튼 4개가 기존 미러 primitive로 그려짐), `identity_cache_inserts` 3 → 8.
- 해석: **팝업 바탕(돌 질감 패널·초상화·테두리)을 그리는 writer가 미러 경로 밖이고, 버튼은 이미 미러된다.** 색 오류는 없다(캡처 열람: 후보 팝업 = baseline nearest 확대와 같은 모습, 내용 정상). 가시 영향 = 팝업 바탕이 Scale2x 대신 nearest(허용된 화질 차 범주)이므로 시각 심각도는 낮다. 다만 G1 상태 HD 기준(≥90%)에는 미달이므로 수리 후보로 유지한다.

## 3. 판정

- **H-TM0 `PASS(partial, 기술·격리 관측)` 수용.** 시나리오 PS15 HD OK, 사용자변경 = PS9 팝업 수리 후보(위치 확정·writer UNKNOWN), 서장 = Wine 영상 재생 불가로 화면 없음 BLOCKED(lap1137과 같은 한계), 캐릭오픈방 = 방 열기 즉시 PS9 복귀·외부 접속 근거 없음 → 화면 없음 BLOCKED. 두 BLOCKED는 환경 한계이며 같은 추측으로 재시도하지 않는다(실제 Windows 동작은 사용자 시험 범위).
- 하네스 결함 4건 수리는 판정 방식 수리로 타당하다(측정값 6 run 동일).

## 4. 다음 work 사전등록(Sonnet) — H-TM1: 사용자등록 팝업 바탕 writer 귀속 → 미러 수리

**근거.** §2로 위치가 확정됐으므로 stale mask 확장(TM 원안 4번)은 건너뛴다. 남은 것은 writer다. 선례: 저장 창 패널(`0x4662DE` 캐시→화면, lap1119)·PS27 역읽기(lap1128)·PS29 막대(`0x468BB0`, lap1127)는 모두 screen watch로 writer를 찾은 뒤 호출 지점 미러로 고쳤다.

- **TM1-0 진단 확장(C·하네스, 옵트인):** `SYW2_G1_SCREEN_WATCH_STATE`에 9를 추가한다(`g1_screen_watch.h` 파서는 현재 3/23/27/29만 받는다; 9는 한 자리 값이라 파서 분기 1개). 하네스 `--screen-watch-state` choices에 9 추가 + `--title-button user`와 병용 허용. TDD(파서·옵션 배선). 기본 off·기존 경로 바이트 불변.
- **TM1-1 귀속(격리 1~2 run):** `--title-button user --layer-drift --screen-watch --screen-watch-state 9`. screen watch는 하드웨어 표본 3개(`G1_SCREEN_WATCH_SAMPLES`, 표본 좌표 env `SYW2_G1_DRIFT_SAMPLES`)이므로 run 1 표본(논리) = 팝업 바탕 `(300,250)` 초상화·`(270,300)` 왼쪽 띠·`(480,400)` 오른쪽 아래, 필요하면 run 2 = `(450,190)` 위 테두리·버튼 대조 `(460,240)`·바탕 `(300,250)` 재확인. 측정: 각 표본의 PS9 팝업 열림 뒤 쓰기 EIP·호출처·스레드·present당 횟수. PASS = run 1 바탕 표본 3개 중 2개 이상이 같은 writer(함수 시작·호출처)로 귀속. writer가 기존 hook 함수면 그 hook이 왜 이 호출을 놓치는지(크기 reject·identity miss 등 present 계수) 적는다.
- **TM1-2 조건부 수리(같은 회차, 구현 우선):** writer가 인자 형태가 분명한 단일 미후킹 함수(또는 호출 지점)이면 기존 선례(H-B4 diff 미러·H-RS3 호출 지점 훅)대로 미러를 구현한다. env 기본 켬 + 끔 대조. 측정: user run 켬 2회·끔 1회, 팝업 정착 HD min(전환 present 제외) **≥98.6%** = PASS, 90~98.6 = PASS(partial), <90 = FAIL. 비회귀: 같은 DLL로 `--title-button scenario` 1회(PS15 100%) + 기존 save006 짧은 pair 또는 new-game 1회 중 하나(안전 0·dropped 0). writer가 여러 개이거나 wined3d/GDI 쪽이면 수리하지 않고 귀속만 기록해 middle에 넘긴다.
- **금지·공통:** 팝업 안 ID 입력/변경/삭제/확인 버튼 클릭 금지(사용자 ID 파일 변경 방지). 종료하기 `(410,560)`·HQNET 미측정 유지(이번 범위 밖). 원본/참고 쓰기·커밋·`260921_temp` 쓰기 금지. 각 run 뒤 `game` 사본 삭제, 디스크 ≥20GiB 확인. C·하네스 변경이 있으므로 lint·typecheck → 기록 freeze → `make check` 1회. **사용자 G1 시험 결과가 오면 그것이 최우선.**
- 연속 규칙: lap1139는 실행 증거가 있는 work다. 이번 middle은 실행 증거 없음 1회째. 다음은 실행 증거를 남기는 work여야 한다.

backlog 유지: Wine 영상 재생 불가, victory-poke readback 경합, 기존 STATUS backlog 전부.

## 5. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS 검증 줄에만 쓴다.
- 전체 `make check` SKIP: 이번 회차 변경은 문서·공유 temp 스크립트뿐이고 C·하네스·테스트 source는 lap1139 full PASS(1796) 때와 같다(위 source 대조).

## 다음 행동

work(Sonnet): §4 H-TM1(TM1-0 진단 확장 → TM1-1 귀속 → 조건부 TM1-2 수리). 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
