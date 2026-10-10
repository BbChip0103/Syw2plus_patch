# 2026-10-07 | lap1111 | G1 middle — H-NG3 독립 검수·수용 + H-NG4(새 게임 진행 장면 스크롤·시간 경과 HD) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1110 work → middle 검수 요청), STATUS "다음 한 가지", lap1110 기록, lap1109 사전등록 §5. INBOX 새 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1111_preserved_lap1110_escalate_sol.txt`로 byte 일치 보존(SHA256 `b8b09501c5eb738d…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: 새 게임 경로(PS9→PS7→PS5→PS3), save 불필요, 활성 8 player records(owner 0 사람·1~7 AI 표기, 활성 8인 부하 증거 아님).

## 1. 독립 재계산 (새 스크립트, 새 실행 아님)

- 스크립트: 공유 temp `20261007_lap1111_middle_review/recalc_lap1111.py`(`e9c7f7f2…`) → `recalc_lap1111.json`(`6d076f82…`). 새로 작성했다(work `recalc_ng3.py` 미사용). 식: present별 HD = `(covered − stale)/480,000`, 계수 증가 = 상태 마지막 값 − 직전 상태 마지막 값.
- trace SHA: a `88740fc9…`·b `12a750b5…` — ESCALATE 기재와 같음.

| run | 상태 | present(연속) | HD 첫 / min(index≥1) / p50 | 98.6% 미만(index≥1) | stale min~max·마지막40 중앙값 | V1 outside | 안전 7종 | menu/partial/frame copy 증가 | 경과 p95 |
|---|---|---|---|---|---|---|---|---|---|
| a | PS9 | 70 | 100/100/100 | 0 | 0 | 0 | 0 | 70/0/0 | 14ms |
| a | PS7 | 157 | 98.166/98.166/98.166 | 156 | 8,793~8,803·8,803 | 0 | 0 | 157/0/0 | 16ms |
| a | PS5 | 735 | 99.024/98.719/98.801 | 0 | 4,684~6,147·6,145 | 0 | 0 | 735/0/0 | 14ms |
| a | **PS3** | **264** | **100/100/100** | **0** | **0·0** | **0** | **0** | 0/0/0 | **7ms** |
| b | PS9 | 69 | 100/100/100 | 0 | 0 | 0 | 0 | 69/0/0 | 14ms |
| b | PS7 | 153 | 98.166/98.166/98.166 | 152 | 8,793~8,803·8,803 | 0 | 0 | 153/0/0 | 15ms |
| b | PS5 | 735 | 99.024/98.719/98.801 | 0 | 4,684~6,147·6,145 | 0 | 0 | 735/0/0 | 15ms |
| b | **PS3** | **265** | **100/100/100** | **0** | **0·0** | **0** | **0** | 0/0/0 | **7ms** |

- 상태 순서 9→7→5→3(a·b), covered_min 480,000, fallback 0, success 1, summary dropped 0, index≥1 90% 미만 0. PS3 source identity `0x01E6D550`(메뉴 `0x01E758A0`과 다름). result `status` PASS, 두 lane `cleanup.ok`·`source_unchanged` true, scale2x validator PASS(palette 위반 0·outside 합 0).
- 입력(candidate input trace): 클릭 3회 = (184,560)·(608,564)·(608,564), 키 입력 0. 세 번째가 시작 클릭이다(두 번째 뒤 약 9.8초). 즉 이번 두 run은 자동 시작이 일어나지 않았고 g6 규칙의 1회 재클릭으로 시작했다.
- PS3 창 길이 13.1초(a), `primitive_call_count` 34,031→66,117로 증가 — 이 구간에 실제 그리기가 계속됐고 stale 측정이 꺼진 것이 아니다(같은 계측이 save006 PS3에서 과거 비0 stale을 보고했다).
- work 수치와 모두 일치한다. **정정 2(판정 영향 없음):** (1) present 레코드의 `game_tick` 필드는 ms 타임스탬프 성격의 값(2,679,226,671 등)이라 게임 tick이 아니다. work의 "시작 tick baseline 3·candidate 4"는 하네스 메모리 읽기 값이며 trace로는 확인하지 않았다. (2) work 표의 PS5 735 present는 PS5 dwell + 자동 시작 대기 8초 + 시작 클릭 뒤 전환까지 포함한 값이다(lap1108의 90과 구간이 다름). PS5 min 98.719%는 lap1108 98.801%보다 낮지만 90%·98.6% 모두 위다.

## 2. 캡처 직접 열람 + 독자 Scale2x 대조(새 근거)

- 열람: a candidate `ps3_start.png`(1600×1200)·baseline(800×600) — 새 게임 시작 직후(농장 밭·정자·농민 1·자원 5000/5000·인구 20/1500·하단 HUD·미니맵 검정·로고). 배치·비율·HUD 위치가 같다. 공개 한계 1(고정 카메라·안개·유닛 거의 없음 → 부하 대표성 낮음)을 그대로 인정한다.
- 대조 스크립트 `cmp_ps3_lap1111.py`(`a98ad7e8…`) → `cmp_ps3_lap1111.json`(`a0f2fa21…`): baseline 캡처를 내 Scale2x(RGB, 가장자리 복제)로 확대해 candidate 2×2 블록과 비교. a(같은 nation 3): 480,000 중 435,299 일치(90.7%). b는 lane별 nation이 달라(2 vs 1) 다른 장면이라 비교 의미 없음(0.27 일치, 예상대로).
- a 차이 위치(`ng3_a_ps3_diff_vs_own_scale2x.png` 열람): 작물·농민·등불·나침반 바늘·우측 효과 = 애니메이션 위상(두 lane 캡처 시각이 다름: baseline 6+12초, candidate 6초+present 256), 그리고 지형 전체의 **얇은 마름모 격자**.
- 격자 특성(`lattice_lap1111.py` `338d87d2…`·보조 `cmp_ps3_lap1111_lib.py` `651bf6da…` → `lattice_lap1111.json` `528f8e42…`; 차이 지도 `ng3_a_ps3_diff_vs_own_scale2x.png` `f38c310d…`·확대 `ng3_a_cand_terrain_crop_x4.png` `20aa807b…`): 정적 지형 영역(y300..449·x0..249) 37,500 블록 중 1,013(2.7%)이 전체 프레임 Scale2x와 다르고, 그 서브픽셀은 **전부 원본 3×3 이웃 색**이며 평균 RGB 차이 4.18, 676은 nearest와 같다. 즉 타일 단위 Scale2x(타일 경계에서 이웃 참조가 잘림)와 전체 프레임 Scale2x의 차이이고, 흑색 seam이 아니다. x4 확대(`ng3_a_cand_terrain_crop_x4.png`) 열람에서 경계선은 보이지 않는다. DESIGN이 허용한 확대 화질 차이로 판정하며 결함으로 올리지 않는다(stale 0과 모순 없음 — stale은 HD 미러 미갱신 픽셀이지 전체 프레임 Scale2x와의 차이가 아니다).

## 3. 하네스 diff 검수

- `_start_new_game`(tools/g1_saved_scene_probe.py 2083~2100): PS5에서 최대 8초 동안 0.3초 간격으로 PS∈{2,3} 대기 → 아니면 `NEW_GAME_CONFIRM`(608,564) 1회 → `ps==3 and tick>0` 대기. `tools/g6_shift_click_probe.py` 529~534행과 같은 규칙이다(직접 대조). 재클릭은 최대 1회이며 raw 입력이 그 1회를 보여 준다.
- `_walk_new_game_path(start_game=True)`: PS5 dwell·캡처 뒤 시작 → 6초 → candidate PS3 mirror present ≥256(timeout 120초), baseline 12초 추가 → `_scene_identity`·`ps3_start` 캡처. `stop_at`에서 시작 분기 뒤 반환하므로 기존 PS7/PS5 경로는 그대로다.
- 옵션: `--new-game-start`는 `--new-game-path` 없이 parser error, validator `required_states` (9,7,5,3)/(9,7,5)/(3,9,35) 분기, 요약 `status`가 candidate `scale2x_validator.status == "PASS"`를 포함(lap1109 §3 결함 수리 확인, 5917행).
- 남은 경미한 점(수리 불요): baseline·candidate 캡처 시각 차이(위 §2)와 lane별 nation 무작위 — 사전등록대로 pair 픽셀 비교는 gate가 아니다.
- focused 테스트 3파일(`test_g1_new_game_path.py`·`test_g1_saved_scene_probe.py`·`test_g1_census.py`) **259 passed/20.29s**(로그 `logs/gates/lap1111-middle-focused.log` `37a6e87f…`). 하네스·테스트 SHA: `g1_saved_scene_probe.py e0680c75…`·`test_g1_new_game_path.py c0f75fa8…`·`test_g1_census.py 74af4e06…`(lap1110 full PASS 1715 때와 같음).

## 4. 판정

- **H-NG3 `PASS(partial, 기술·격리)` 수용.** 정정 2(위 §1, 판정 영향 없음). 새 게임 시작 직후 PS3 HD 100%(2/2)·V1 0·안전 7종 0·dropped 0·scale2x PASS. 제품 C 변경 없음 → G1 후보 DLL은 lap1106 H-P35 트리 그대로. 사용자 합격도 G1 마감도 아니다.
- 공개: 시작 직후 장면은 부하 대표성이 낮다(스크롤·시간 경과·유닛 증가 뒤 미측정), 맵 이름 raw 없음, PS2 present 0, 픽셀 정확 오라클 UNKNOWN, 타일 경계 Scale2x 격자(허용 화질 차이).
- 시험판 재스테이징: 계속 보류(lap1109 §4 사유 유지 — 제품 변경 없음, 사용자 lap1104 판 시험 중일 수 있음).

## 5. 다음 work 사전등록(Sonnet) — H-NG4: 새 게임 진행 장면(스크롤 + 시간 경과) PS3 HD

**근거:** 사용자는 시험에서 새 게임을 시작해 화면을 움직이며 몇 분 플레이한다(APPROVALS lap1104 절차 ⑤). 지금 새 게임 PS3 근거는 고정 카메라 13초뿐이다. save006·save000 불러오기 장면에는 스크롤 측정(lap1002~1009)이 있으나 새 게임 장면에는 없다.

**가설:** 새 게임 장면에서 카메라를 움직이고 시간이 흘러도(안개 걷힘·지형/작물/건물 새로 그림) 미러 경로가 같으므로 PS3 HD ≥98.6%·V1·안전 0이 유지된다.

- **NG4-0 하네스(TDD):** `--new-game-start`에 진행 창 옵션 추가(이름 구현자 재량, 예 `--new-game-play`; `--new-game-start` 필수). `ps3_start` 캡처 뒤: (1) 방향키 hold 4구간 RIGHT→DOWN→LEFT→UP 각 2.0초(기존 `--terrain-scroll-hold` 계열의 XTest 키 경로 재사용, 키 사이 1초), 각 구간 전후 카메라 좌표(기존 `_scroll_camera_steps` 등 runtime state)를 기록; (2) 무입력 60초 dwell; (3) `ps3_play` 캡처. candidate는 이 창 전체의 PS3 present를 trace로 남기고, baseline은 같은 입력·시간을 따른다. 기존 3/9/35·OS0·NG3 경로 불변. 테스트 RED→GREEN.
- **NG4-1 측정(격리 run 2회, `--hd-source scale2x`):** 진행 창 PS3 present 수·HD 첫/min(index≥1)/p50·98.6% 미만 개수와 시각(스크롤 구간 안/밖)·stale max·마지막 40 중앙값·V1 outside max·안전 7종·dropped·scale2x validator·경과 p95(스크롤 구간/dwell 분리)·키 구간별 카메라 이동 칸 수.
  - **PASS:** 진행 창 index≥1 모든 present HD ≥90%, V1 outside 0, 안전 7종 0, dropped 0, scale2x PASS, 키 4구간 모두 카메라 이동 ≥1칸(입력 전달 확인), 2/2 run. 98.6% 미만 present가 있으면 PASS라도 개수·위치를 공개하고 middle이 귀속 여부를 정한다.
  - **FAIL/귀속:** 90% 미만이면 수리하지 않고 위치(캡처 Scale2x 비교, lap1109 `locate_stale_lap1109.py`·이 lap `cmp_ps3_lap1111.py` 방식 재사용 가능)와 trace 단서를 넘긴다(가설 1개).
  - **BLOCKED:** 키가 PS3에서 카메라를 움직이지 않으면(맵 모서리 등) 반대 방향 키로 1회만 바꿔 보고, 그래도 안 되면 상태값·캡처와 함께 넘긴다. 60분 또는 실패 가설 2회(PROMPT ③).
- 판정 밖 기록: 시작 위치(카메라 좌표)·nation, lane 간 픽셀 차이(무작위 시작이라 gate 아님), 진행 창 동안 AI 인구 변화.
- 공통: source를 바꾸면 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 89GiB) 확인, 끝나면 game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지. 사용자 시험판 재스테이징 없음(§4). 사용자 G1 시험 결과가 들어오면 그것이 최우선.

backlog(유지): PS7·PS5 글자·버튼 모서리 stale 1.2~1.8%(TextOutA `reject_target`·`0x465E80` `reject_target` 단서), `--census-state 5|7` 실제 실행, 타이틀·옵션·게임 중 저장 창·승패 화면 HD, PS2 로딩 화면, 픽셀 정확 오라클, throttle ord 123 writer, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`를 돌린다. 결과는 STATUS에만 쓴다. focused 테스트는 §3(259 passed).
- 전체 `make check`는 SKIP한다. 이번 변경은 문서뿐이고 하네스·테스트 SHA는 lap1110 full PASS(1715) 때와 같다.

## 다음 한 가지

work(Sonnet): §5 H-NG4 — NG4-0 하네스(진행 창: 키 hold 4구간 + 60초 dwell) → NG4-1 측정 2회. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
