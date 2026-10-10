# 2026-10-07 | lap1113 | G1 middle — H-NG4 독립 검수·수용 + H-NG5(새 게임 몇 분 플레이: 선택·생산) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1112 work → middle 검수 요청), STATUS "다음 한 가지", lap1112 기록, lap1111 사전등록 §5. INBOX 새 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1113_preserved_lap1112_escalate_sol.txt`로 byte 일치 보존(SHA256 `2ced41eb271aa07e…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: 새 게임 경로(PS9→PS7→PS5→PS3), save 불필요, 활성 8 player records(활성 8인 부하 증거 아님).

## 1. 독립 재계산 (새 스크립트, 새 실행 아님)

- 스크립트: 공유 temp `20261007_lap1113_middle_review/recalc_lap1113.py`(`9a82af73…`) → `recalc_lap1113.json`(`311f45fd…`). 새로 작성했다(work `recalc_ng4.py` 미사용). 식: present별 HD = `(covered − stale)/480,000`. 창은 `probe-result.json` `new_game_play.windows`의 줄 번호를 1부터 세는 닫힌 구간으로 잘랐다.
- trace SHA: a `c9920bd3…`·b `5e3a7761…`, `ps3_play.png` a `e08727f9…`·b `47ae9e35…` — ESCALATE·work 기재와 같다.

| run | PS3 present(길이) | HD 첫/min(index≥1)/p50 | 90%·98.6% 미만 | stale max | V1 outside·안전 7종·fallback·hresult≠0 | dropped(events) | 경과 p95(max) | present 최대 간격 |
|---|---|---|---|---|---|---|---|---|
| a | 1,712 (85.53초) | 100/100/100 | 0·0 | 0 | 0·0·0·0 | 0 (3,796) | 6ms (9) | 58ms |
| b | 1,713 (85.57초) | 100/100/100 | 0·0 | 0 | 0·0·0·0 | 0 (3,800) | 6ms (10) | 59ms |

- 창별(a/b): 스크롤 4구간 각 41 present·1,999~2,008ms, dwell 1,201 present·60.0초, 전 창 HD min 100%·stale 0·V1 0·안전 0, 경과 p95 6~8ms. 창 사이 간격 996~1,049ms(hold 2,000ms·gap 1,000ms와 일치). 상태 순서 9→7→5→3, covered_min 480,000, success 1, method별 dropped 0. result·최상위 `status` PASS, scale2x validator PASS, `source_unchanged`·`cleanup.ok` true.
- 창 present 수 41 vs 하네스 40: 하네스는 `lines[start:end]`(키 down 직후 줄부터)로 자르고, 나는 `line_start` 줄 하나를 더 포함했다. 셈 규칙 차이일 뿐 work 오류가 아니다.
- 스크롤 중 그림이 실제로 바뀌었다: source hash 변화 스크롤 구간 25~40/41·dwell 596~717/1,201. 정지 프레임을 잰 것이 아니다.
- 키 4구간 카메라(probe-result raw): a (8,47)→(48,7)→(88,47)→(48,87)→(9,48) = 40/40/40/39, b 마지막 (8,47) = 40/40/40/40. hold 2,000ms ×4. dwell 뒤 카메라 그대로(마우스 가장자리 스크롤 없음).
- **정정 1(판정 영향 없음): baseline 이동 칸이 더 많은 이유는 "게임 tick이 더 빠름"이 아니다.** 두 lane 모두 PS3 present가 초당 20.0회다(baseline trace aggregate `blt_fast` 화면 대상 1,805회/90.16초 = 20.02/s, candidate `blt` 1,708회/85.36초 = 20.01/s). baseline 54/80/61/42는 맵 가장자리에서 한 축이 막히면 남은 축이 tick당 2칸 움직이는 것으로 설명된다(`SCROLL_CAMERA_SIGNS_EDGE`·H-D2h). 직접 재구성: RIGHT 대각 8 tick→(99,46), 이어서 y −2/tick 23 tick→(99,0) 모서리 정지(31 tick). DOWN x 막힘·y +2 ×40 = 80. LEFT 대각 19 + x −2 ×21 = 40 tick. UP 대각 38 + y −2 ×2 = 40 tick. 모두 2초당 약 40 tick이며 candidate와 같다. 즉 이 장면에서 candidate가 느려진 근거는 없다.
- 입력 trace: candidate 512 events(상한) = 클릭 WndProc 513/514 각 3 + GetCursorPos 506, 마지막 ts가 스크롤 창 이전이다. 키 수신 raw는 없다(WM_KEY*는 계측 대상 아님). 키 전달은 카메라 이동과 present 내용 변화로 확인한다(work 공개 한계 5와 같다).

## 2. 캡처 직접 열람

- a candidate `ps3_play.png`(1600×1200): 시작 장면 근처(카메라 (9,48)), 정자·농민 1·밭·숲, 자원 5000/5000·인구 20/1500, 하단 HUD·F1~F11·명령 패널·로고 정상이다. 깨짐·흑색 띠·어긋남은 보이지 않는다.
- b candidate `ps3_play.png`: 다른 nation 건물(한옥)이고 나머지는 a와 같다. 정상이다.
- a baseline `ps3_play.png`(800×600): 카메라 (0,57) 맵 가장자리라 월드가 전부 미탐색 검정이고 HUD는 정상이다. lane마다 시작 위치가 달라(candidate (8,47), baseline (91,54)) pair 픽셀 비교는 사전등록대로 gate가 아니다.
- 미니맵이 두 lane 모두 검정이다. 시작 직후의 원래 동작이며 lane 사이 차이는 없다.

## 3. 하네스 diff 검수 (`tools/g1_saved_scene_probe.py` `affc8dee…`, `tests/test_g1_new_game_path.py` `50c181ea…`)

- `_new_game_play_window`(2116~2150): 사전등록 §5 NG4-0과 일치한다 — RIGHT→DOWN→LEFT→UP, hold 2.0초(`finally`로 key up 보장), gap 1.0초, 구간 전후 `read_camera`, `_scroll_camera_steps`(가장자리 미끄러짐 허용), 무입력 dwell 60초, 창 줄 범위 기록, 모든 구간 이동 ≥1칸이면 PASS.
- `_summarize_play_presents`(2153~): 창별 PS3 present HD·90%/98.6% 미만·stale·V1·안전 7종·fallback·success·경과 p95. PASS 조건은 present>0·90% 미만 0(index 0 포함, 사전등록보다 엄격)·fallback 0·success 1·안전 7종(V1 포함) 0이다.
- 옵션: `--new-game-play`는 `--new-game-start` 없이 parser error(5994). 최상위 `status`는 두 lane `new_game_play.status`·scale2x validator·cleanup·source_unchanged를 gate한다(6031~6035).
- 경미(수리 불요): 창 PASS가 trace `dropped_count`를 직접 gate하지 않는다. 이번 run은 summary dropped 0이고 위 재계산이 확인했다. 다음 work(§5)가 trace 상한에 가까워지므로 거기서 gate를 추가한다.
- 테스트 19건(lap1108 7·lap1110 5·lap1112 7). focused 3파일 **266 passed/20.30s**(로그 `logs/gates/lap1113-middle-focused.log` `6d0c2552…`). 하네스·테스트 SHA는 lap1112 full PASS(1722) 때와 같다.

## 4. 판정

- **H-NG4 `PASS(partial, 기술·격리)` 수용.** 정정 1(위 §1, 판정 영향 없음; 오히려 "baseline이 더 빠름"이라는 성능 걱정을 없앤다). 새 게임 진행 창(스크롤 4구간 + 60초 dwell, 1,712/1,713 present) PS3 HD 100%·stale 0·V1 0·안전 7종 0·dropped 0·scale2x PASS·이동 ≥39칸, 2/2 run. 제품 C 변경 없음 → G1 후보 DLL은 lap1106 H-P35 트리 그대로다. 사용자 합격도 G1 마감도 아니다.
- 공개 한계 유지: 안개·정지 지형·유닛 1명이라 부하 대표성이 낮다. 60초 dwell은 몇 분 플레이가 아니다. 선택·생산·이동 명령·HP 바·생산 패널 GDI 글자가 있는 새 게임 장면은 아직 측정하지 않았다.
- 시험판 재스테이징: 계속 보류(lap1109 §4 사유 유지). 사용자가 lap1104 판(`94213374…`, H-P35 이전)으로 시험 중일 수 있다. 결과가 오면 최신 트리 재스테이징 여부를 함께 정한다.

## 5. 다음 work 사전등록(Sonnet) — H-NG5: 새 게임 몇 분 플레이(선택·생산·이동) PS3 HD

**근거:** ESCALATE 4번 선택지 중에서 "부하 있는 새 게임 장면"과 "HUD/GDI"를 한 run에 묶는다. 사용자 시험 절차 ④·⑤(유닛 클릭·드래그 선택·생산 버튼, 몇 분 플레이)가 새 게임에서 그대로 하는 일이고, 지금 새 게임 근거에는 선택 HUD·생산 패널 글자·HP 바·유닛 증가가 없다. 사용자 승인 요청 준비만 하는 것은 제품 근거를 늘리지 않으므로 고르지 않았다(PROMPT ③ 연속 문서 회차 제한).

**가설:** 새 게임에서 유닛을 선택하고 생산·이동 명령을 내리며 몇 분이 지나도(선택 상자·HP 바·생산 패널·GDI 글자·새 유닛 sprite) 미러 경로가 같으므로 PS3 HD ≥98.6%·V1·안전 0이 유지된다.

- **NG5-0 하네스(TDD):** `--new-game-play` 뒤에 붙는 새 옵션(이름은 구현자가 정한다. 예 `--new-game-act`, `--new-game-play` 필수). 순서: (1) 농민 클릭 선택 → 선택 수 ≥1 확인(기존 `runtime_env._read_g1_selection_count` 또는 `_selection_observation` 재사용), (2) 본진 건물 클릭 → 생산 버튼 1회 이상 → 자원 감소 또는 생산 큐 변화 확인(읽을 수 있는 runtime 값; 없으면 `ps3_act` 캡처의 자원 숫자로 대신하고 그 사실을 공개), (3) 드래그 선택 1회 + 빈 땅 우클릭 이동 명령 1회, (4) 무입력 dwell. 클릭 좌표는 `ps3_start` 캡처·카메라 기준 고정 논리 좌표로 시작해도 된다. 대신 선택 수 변화로 확인하고, 실패하면 1회만 다른 좌표로 재시도한다. lane마다 nation이 무작위라 건물 모양이 다를 수 있다. **창 PASS에 trace `dropped_count == 0`을 추가**한다(§3 경미 사항). 기존 NG3/NG4·3/9/35 경로는 바꾸지 않는다. 테스트 RED→GREEN.
- **trace 상한:** DLL `event_limit` 8,192는 고정이다(제품 C를 바꾸지 않는다). lap1112는 85초에 3,796 events였으므로, 행동 + dwell 합계 PS3 창은 약 3분 이하로 잡고 dropped 0을 확인한다. 상한에 걸리면 dwell을 줄여 다시 실행하고 그 사실을 기록한다.
- **NG5-1 측정(격리 run 2회, `--hd-source scale2x`):** 창별(선택/생산/이동/dwell) PS3 present 수·HD 첫/min(index≥1)/p50·98.6% 미만 개수와 seq·stale max·마지막 40 중앙값·V1 outside·안전 7종·dropped·scale2x validator·경과 p95, 입력 효과(선택 수, 자원/생산 변화, 이동 명령 뒤 유닛 위치 또는 캡처), `ps3_act`·`ps3_end` 캡처.
  - **PASS:** 모든 창 index≥1 present HD ≥90%, V1 0, 안전 7종 0, dropped 0, scale2x PASS, 선택 효과 ≥1, 생산 또는 이동 효과 ≥1, 2/2 run. 98.6% 미만 present가 있으면 PASS라도 개수·seq·위치를 공개하고, middle이 귀속(선택 HUD·GDI 글자·HP 바 등 기존 backlog writer와 대조)을 정한다.
  - **FAIL/귀속:** 90% 미만이면 수리하지 않는다. 위치(캡처와 독자 Scale2x 비교. lap1111 `cmp_ps3_lap1111.py`·lap1109 `locate_stale_lap1109.py` 방식)와 trace 단서(`textout_iat_reject_target`·`*_reject_*` 계수 변화)를 넘긴다(가설 1개).
  - **BLOCKED:** 클릭으로 선택이 안 되면(좌표·포커스) 재시도 1회 뒤 상태값·캡처와 함께 넘긴다. 60분 또는 실패 가설 2회(PROMPT ③).
- 판정 밖 기록: nation·시작 카메라, AI 인구 변화, lane 사이 픽셀 차이(gate 아님).
- 공통: source를 바꾸면 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 87GiB)를 확인하고, 끝나면 game 사본을 지운다. 원본/참고 쓰기 금지, 커밋 금지, 시험판 재스테이징 없음. 사용자 G1 시험 결과가 들어오면 그것이 최우선이다.

backlog(유지): PS7·PS5 글자·버튼 모서리 stale 1.2~1.8%(TextOutA `reject_target`·`0x465E80` `reject_target` 단서), `--census-state 5|7` 실제 실행, 타이틀·옵션·게임 중 저장 창·승패 화면 HD, PS2 로딩 화면, 픽셀 정확 오라클, throttle ord 123 writer, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역, 입력 trace 512 상한(키 수신 raw 부재).

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`를 돌린다. 결과는 STATUS에만 쓴다. focused 테스트는 §3(266 passed).
- 전체 `make check`는 SKIP한다. 이번 변경은 문서뿐이고 하네스·테스트 SHA는 lap1112 full PASS(1722) 때와 같다.

## 다음 한 가지

work(Sonnet): §5 H-NG5 — NG5-0 하네스(선택·생산·이동 + dwell, dropped gate) → NG5-1 측정 2회. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
