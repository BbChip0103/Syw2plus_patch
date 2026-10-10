# 2026-10-07 | lap1109 | G1 middle — H-OS0 독립 검수·수용 + H-NG3(새 게임 시작 직후 PS3 HD) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1108 work → middle 검수 요청), STATUS "다음 한 가지", lap1108 기록, lap1107 사전등록 §3. INBOX 새 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1109_preserved_lap1108_escalate_sol.txt`로 byte 일치 보존(SHA256 `440acb1092efa6ad…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: 새 게임 경로(PS9→PS7→PS5), save 불필요. 키 입력 0.

## 1. 독립 재계산 (새 스크립트, 새 실행 아님)

- 스크립트: 공유 temp `20261007_lap1109_middle_review/recalc_lap1109.py`(`46ecc0ed…`) → `recalc_lap1109.json`(`13e4e6b0…`). 새로 작성했다(work의 `recalc_hos0.py` 미사용). 식: present별 HD = `(covered − stale)/480,000`, 계수 증가 = 상태 마지막 값 − 직전 상태 마지막 값.
- trace SHA: a `9b8ff277…`·b `8003ea15…` — ESCALATE 기재와 같음.

| run | 상태 | present | HD 첫 / min(index≥1) / p50 | stale min~max | V1 outside max | inside diff | menu / partial / frame copy 증가 | 경과 p95 |
|---|---|---|---|---|---|---|---|---|
| a | PS9 | 69 | 100 / 100 / 100 | 0 | 0 | 116,238~116,298 | 69 / 0 / 0 | 14ms |
| a | **PS7** | 158 | **98.166 / 98.166 / 98.166** | 8,793~8,803 | 0 | 107,674~107,748 | 158 / 0 / 0 | 15ms |
| a | **PS5** | 90 | **99.024 / 98.801 / 98.801** | 4,684~5,754 | 0 | 102,956~103,362 | 90 / 0 / 0 | 14ms |
| b | PS9 | 67 | 100 / 100 / 100 | 0 | 0 | 116,238~116,298 | 67 / 0 / 0 | 14ms |
| b | **PS7** | 159 | **98.166 / 98.166 / 98.166** | 8,793~8,803 | 0 | 107,674~107,748 | 159 / 0 / 0 | 15ms |
| b | **PS5** | 92 | **99.024 / 98.801 / 98.802** | 4,684~5,754 | 0 | 102,957~103,362 | 92 / 0 / 0 | 15ms |

- 상태 순서 9→7→5(a·b), present source 1종 `0x01E758A0`, covered_min 480,000, 안전 7종 최대 0, fallback 0, success 1, `frame_copy_rejects` 0, summary dropped 0(a 317·b 318 present, p95 15ms). index≥1 90% 미만 present 0.
- work 수치와 모두 일치한다. 표기 차이 1: work의 PS9 menu_copy "68/66"은 첫 PS9 present 값을 뺀 증가, 이 표의 69/67은 0부터 센 값이다(같은 raw).
- 부분 사각형 경로(H-P35)는 PS7·PS5에서 0회다. lap1107 §1-4가 공개한 "다른 buffer로 가는 부분 복사" 위험은 이 두 화면에서 관측되지 않았다.

## 2. 캡처·미귀속 stale 위치(새 근거)

- 캡처 SHA: candidate a `ps7.png 72e8e3b6…`·`ps5.png 03e4219b…`, b `ps7.png 72e8e3b6…`(a와 같음)·`ps5.png d5f599b4…`(a와 다름 — b는 커서가 확인 버튼 위, 화면 내용 동일), baseline `ps7.png 03768243…`·`ps5.png b179c67a…`(a·b 같음). 직접 열람: PS7 = 접속방식(IPX 대전/혼자하기·DirectPlay 목록·확인/취소), PS5 = 혼자하기 대기실(1P·컴퓨터·자리 3~8 없음·설정 7항·맵 목록). 1600×1200 배치·비율 정상.
- 위치 확인: `locate_stale_lap1109.py`(`4b8b5a54…`) → `locate_stale_lap1109.json`(`74a7ba9c…`). baseline 800×600 캡처를 내 Scale2x(RGB, 가장자리 복제)로 확대해 candidate 2×2 블록과 비교했다. "nearest와 같고 Scale2x와 다른" 블록(= 잔여 stale 중 눈에 보이는 부분): PS7 799 px, PS5 2,426~2,427 px. 오버레이 PNG(`ng_a_ps7_stale_overlay.png`·`ng_a_ps5_stale_overlay.png`) 직접 열람 결과 **위치는 글자(사용자 이름·버튼 글자·목록 글자·설정 항목)와 버튼 테두리 모서리**다. 화면 전체 HD와 맞음 PS7 478,696·PS5 476,050 px.
- 단서(귀속 아님): 같은 run의 `textout_iat_metrics`는 호출 11,950 중 mirrored 6,441·`reject_target` 4,699, `rect_solid_465E80`은 1,869 중 `reject_target` 1,620이다. 이 계수는 run 전체 누계라 상태별 분리가 안 된다. 메뉴 글자가 present source가 아닌 대상으로 그려진 뒤 복사되거나, 대상 판정이 메뉴 화면에서 거부되는 것으로 의심한다. 90% 기준은 충족하므로 지금 수리 대상이 아니다(backlog).

## 3. 하네스 diff 검수

- `_click_until_state`: 클릭 1회 → 1초 뒤 여전히 `from_ps`일 때만 1회 재클릭 → `to_ps` 대기. 기존 LOAD_MENU 재시도와 같은 원칙(전환 뒤 맹목 재클릭 없음). 테스트 2건이 재시도·무재전송을 고정한다. raw `actions`에서 네 lane 모두 클릭 1회씩.
- `_walk_new_game_path`: PS9→PS7(184,560)→PS5(608,564), 좌표는 `tools/g6_shift_click_probe.py` 348·511행과 같다(직접 대조). candidate는 상태별 mirror present 64개, baseline은 8초 대기 뒤 캡처, `stop_at`에서 종료해 PS5 시작 전 멈춘다. census 모드(`--census-only --census-state 5|7`)는 `stop_at=census_state`로 같은 경로를 쓰지만 **실행된 적 없다**(소스 계약 테스트만, UNKNOWN 유지).
- validator: candidate는 `required_states=(9,7,5)`로 mirror validator를 돌린다. 결과 BLOCKED는 nearest oracle 0.776 < identity 임계 0.999이며, lap1106 save006·save000 pair에서도 같은 BLOCKED였다(`20261007_lap1106_work_hp35/p1,p2,s1` 직접 확인). scale2x 모드 gate는 `scale2x_validator`이고 a·b 모두 PASS(palette violations 0·outside diff 0).
- **결함(경미, 이번 판정에는 영향 없음):** `--new-game-path` 요약 `status`는 lane `status`·`cleanup.ok`·`source_unchanged`만 보고 `scale2x_validator.status`를 보지 않는다(pair 모드는 6011행에서 이것을 gate로 쓴다). 이번 두 run은 scale2x PASS였으므로 결론은 같다. 다음 work가 이 gate를 추가한다(§5 NG3-0).
- 그 밖: 새 게임 경로에서도 save fixture를 private game에 복사·SHA 확인한다(무해, 쓰이지 않음). focused 테스트 4파일 258 passed(로그 `logs/gates/lap1109-middle-focused.log`).

## 4. 판정

- **H-OS0 `PASS(partial, 기술·격리)` 수용.** 정정 0(표기 차이 1). PS7 98.166%·PS5 98.801%(2/2), V1 0, 안전 7종 0, 부분/frame copy 0. 제품 C 변경 없음이므로 G1 후보 DLL은 lap1106 H-P35 트리 그대로다. 사용자 합격도 G1 마감도 아니다.
- 공개: PS7·PS5 잔여 stale 1.2~1.8% = 글자·버튼 모서리(위치 확인, writer 미귀속), 픽셀 정확 오라클 UNKNOWN, `--census-state 5|7` 실행 미검증.
- **시험판 재스테이징: 계속 보류.** H-OS0는 제품 변경이 없고, 바뀐 제품은 H-P35(불러오기 화면 화질)뿐이다. 사용자가 lap1104 판(`94213374…`)으로 시험 중일 수 있어 피드백 판본이 섞이지 않게 한다. 사용자 결과가 오거나, 다음 제품 수리가 생겨 묶을 때 middle이 재조립·재스테이징한다.

## 5. 다음 work 사전등록(Sonnet) — H-NG3: 새 게임 시작 직후 PS3 HD(두 번째 장면)

**근거:** 지금까지 PS3 HD는 save006·save000 불러오기 장면뿐이다. 사용자가 새 게임을 시작하면 PS5 → (PS2) → PS3를 지나고, 이 장면은 STATUS의 "두 번째 장면" 미측정 항목이다. g6 probe에 같은 시작 경로가 있다(511~536행: PS5에서 확인 클릭 뒤 혼자하기는 곧 자동 시작, 8초 안에 PS2/PS3가 아니면 (608,564) 1회 재클릭, `ps==3 and tick>0` 대기, 첫 몇 초는 검정이라 6초 대기).

**가설:** 새 게임 PS3도 불러오기 PS3와 같은 미러 경로로 그려지므로, 시작 직후 장면에서 HD가 불러오기 PS3 수준(≥98.6%)이고 V1·안전이 0이다.

- **NG3-0 하네스(TDD):** `--new-game-path`에 `--new-game-start`(이름은 구현자 재량) 추가: PS5 dwell 뒤 g6 probe와 같은 규칙으로 시작(자동 시작 대기 8초 → 그때도 PS2/PS3가 아니면 (608,564) 1회) → `ps==3 and tick>0` → 6초 뒤 candidate는 PS3 mirror present ≥256개 대기, baseline은 같은 시간 대기 → 캡처 `ps3_start`. 같은 회차에 §3 결함 수리: 요약 `status`에 candidate `scale2x_validator.status == "PASS"`를 포함한다. 기존 3/9/35·OS0 경로 불변. 테스트 RED→GREEN.
- **NG3-1 측정(격리 run 2회, `--hd-source scale2x`):** 상태별(PS2가 있으면 포함) present 수·HD 첫/min/p50·stale max·마지막 40 stale 중앙값·V1 outside max·안전 7종·menu/partial/frame copy 증가·경과 p95, 시작 tick·맵 이름(기본 첫 맵 `(2인,100X100) ESL1 죽음의바다` 기대)·local seat. baseline·candidate 시작 위치가 다를 수 있으므로 pair 픽셀 비교·입력효과는 gate가 아니다(공개).
  - **PASS:** PS3 index≥1 모든 present HD ≥90%, V1 outside 0, 안전 7종 0, dropped 0, scale2x validator PASS, 2/2 run. 98.6% 미만 present가 있으면 PASS라도 개수·위치를 공개하고 middle이 귀속 여부를 정한다.
  - **FAIL/귀속:** 90% 미만이면 수리하지 않고 위치(캡처 Scale2x 비교, lap1109 `locate_stale_lap1109.py` 방식 재사용 가능)와 trace 단서를 넘긴다(가설 1개 규칙).
  - **BLOCKED:** 자동 시작·클릭으로 PS3 진입이 안 되면 상태값·캡처를 남기고 g6 probe 대조와 함께 넘긴다. 60분 또는 실패 가설 2회(PROMPT ③).
- 판정 밖 기록: PS2(로딩) 화면 HD, 시작 직후 검정 구간 길이, 경과 p95.
- 공통: source를 바꾸면 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 91GiB) 확인, 끝나면 game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지. 사용자 시험판 재스테이징 없음(§4).

backlog(유지·추가): **PS7·PS5 글자·버튼 모서리 stale(TextOutA `reject_target` 4,699·`0x465E80` `reject_target` 1,620 단서)**, `--census-state 5|7` 실제 실행, 타이틀(PS9 이전)·옵션·게임 중 저장 창·승패 화면 HD, 후보 PS35 픽셀 정확 오라클, throttle ord 123 writer, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`를 돌린다. 결과는 STATUS에만 쓴다. focused 테스트는 §3(258 passed).
- 전체 `make check`는 SKIP한다. 이번 변경은 문서뿐이고, 하네스·테스트 SHA(`g1_saved_scene_probe.py dbe31957…`·`test_g1_new_game_path.py 5221503d…`·`test_g1_census.py 74af4e06…`)는 lap1108 full PASS(1710) 때와 같다.

## 다음 한 가지

work(Sonnet): §5 H-NG3 — NG3-0 하네스(시작 경로 + 요약 scale2x gate) → NG3-1 측정 2회. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
