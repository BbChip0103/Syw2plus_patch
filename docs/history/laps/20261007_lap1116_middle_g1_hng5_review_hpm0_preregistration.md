# 2026-10-07 | lap1116 | G1 middle — H-NG5 독립 검수·수용 + H-PM0(게임 중 일시정지 메뉴·저장 창 HD) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1115 work → middle 검수 요청), STATUS "다음 한 가지", lap1115 기록, lap1113 사전등록 §5, INBOX 03:55 root 복구 메모. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1116_preserved_lap1115_escalate_sol.txt`로 byte 일치 보존(SHA256 `ed23770e9a012f22…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만).
- fixture: 새 게임 경로(PS9→PS7→PS5→PS3), save 없음, 활성 8 player records(활성 8인 부하 증거 아님).
- STATUS 압축: 기록 전 128줄 → 원문 SHA256 `328f58efb2217d86…` 전문을 `docs/history/20261007_status_lap1116_precompaction.md`에 byte-exact 보존(`cmp` 일치) 뒤 lap1099~1113 줄과 옛 포인터를 포인터로 대체.

## 1. lap1114 복구 판정 검수 (ESCALATE 1번)

- 하네스 `tools/g1_saved_scene_probe.py` mtime 02:57:12.81, c pid 파일 02:57:15.23, b exit 02:56:50.51 → b는 하네스 저장 전에 끝났고 c는 저장 뒤 시작했다. 하네스 SHA `5af61982…`는 그 뒤 바뀌지 않았다(lap1115 full check 뒤 새로 바뀐 source 파일 0).
- result raw: a·b 두 lane 모두 `produce.clicks = [[704,504],[668,504]]`·`effect=false`(이전 좌표), c·e는 `[[668,539]]`·`effect=true`. d는 `new-game-path-result.json`·trace 없음, `.exit` 없음, candidate 캡처만 `ps3_produce`까지.
- 후보 DLL: c `c1e3bc9e…`·e `c0c7f22b…`·lap1112 ng4_a는 PE 빌드 타임스탬프 2곳(COFF `0x88`·export `0x51A04`)과 checksum(`0xD8`) 6 B 외 byte 동일 → 제품 C 무변경(lap1106 트리) 확인.
- **판정: a·b 제외·c 재사용·d 근거 아님 — work 판정과 일치.**

## 2. 독립 재계산 (새 스크립트, 새 실행 아님)

- 스크립트: 공유 temp `20261007_lap1116_middle_review/recalc_lap1116.py`(`9ab03597…`) → `recalc_lap1116.json`(`c1593d0f…`). 새로 작성했다(work `recalc_ng5.py` 미사용). 식: present별 HD = `(covered − stale)/480,000`. 창은 result 줄 번호를 1부터 세는 닫힌 구간(lap1113 규칙)으로 잘랐고, 창과 무관하게 run 전체 PS3 present도 따로 셌다.
- trace SHA: c `9dd7187d…`·e `bba45953…`, result c `84e1b231…`·e `40bf59c3…`.

| run | events / dropped(summary·method·present) | 전체 PS3 present(길이) | HD min(index≥1) | 98.6%·90% 미만 | stale≠0 present | V1·안전 7종·fallback·hresult≠0 | 경과 p95 |
|---|---|---|---|---|---|---|---|
| c | 5,065 / 0·0·0 | 2,978 (148.8초) | 100 | 0·0 | 없음 | 0·0·0·0 | 6ms |
| e | 5,115 / 0·0·0 | 2,977 (148.8초) | 99.966 | 0·0 | seq 3750 하나(162 px) | 0·0·0·0 | 6ms |

- 창별(c/e): select 5/5·produce 34/34·drag_move 24/24·act dwell 1,201/1,201·scroll 41~42·play dwell 1,201/1,201 present, 모든 창 covered 480,000·success 1·HD p50 100·경과 p95 4~7ms(max 12). present 수는 work보다 창마다 1 많다 — 닫힌 구간 셈 차이(lap1113과 같은 이유)이며 work 오류가 아니다.
- 그림이 실제로 바뀌었다: source hash 변화 produce 23·24/34, drag_move 23·21/24, act dwell 555·790/1,201, play dwell 483·879/1,201. 정지 프레임을 잰 것이 아니다.
- 스크롤 4구간 카메라: c·e 모두 (8,47)→(48,7)→(88,47)→(48,87)→(8,47) = 40칸×4, dwell 뒤 (8,47).
- 입력 효과(raw): 선택 0→1(slot 1198, 첫 좌표), 건물 slot 1199 선택, 생산 `(668,539)` 1회 → 쌀 5000→4200 네 lane 모두, 나무 c 후보만 5000→5000(나머지 −300), `used` 20→20, 드래그 slots [1198], 이동 효과 true(추적 1).
- **e stale 162 귀속(ESCALATE 2번):** seq 3750(줄 3750) = scroll_LEFT 창(줄 3739~3780) 시작 11줄째, 키 down 약 0.2초 뒤(방향 전환 직후). 앞·뒤 present stale 0, `primitive_stale_pixels_total` 증가가 정확히 162라 primitive replay 단위 stale 한 번이다. 0.034%·98.6% 기준 위·다음 present에서 해소되므로 사전등록상 귀속 의무 없음 → **일시 stale로 닫고 수리하지 않는다**(backlog 한 줄로만 남김, c에는 없음).
- 측정 결과는 work 수치와 일치한다. 불일치 0.

## 3. 캡처 직접 열람

- c candidate `ps3_produce.png`(1600×1200): 조선 본진 선택, 머리 위 HP 막대·하단 체력 4800/4800·방어력 33/33·생산 큐 농부 초상 1%·명령 패널(S/R/D/T·F/B/Z·E) 글자 정상, 쌀 4200·나무 5000. 깨짐·흑색 띠·어긋남 없음.
- e candidate `ps3_act.png`: 다른 nation(건물·초상 상이), 이동한 유닛 선택 원·HP 막대, 체력 500/500·방어력 30/30·명령 패널 정상, 우클릭 목표 근처(논리 (540,380)→화면 약 (1080,760))에 이동 표시 sprite. 쌀 4200·나무 4700. 깨짐 없음.
- 판정 밖 관찰: 두 캡처의 화면 인구가 30/1500인데 메모리 `used`는 20이다(lap1113 시작 화면 20/1500). 생산 큐 예약분이 화면에 먼저 반영되는 것으로 보이며 귀속은 UNKNOWN. G1 판정과 무관하다.

## 4. 하네스 검수 (ESCALATE 3번)

- `_new_game_act_window`(2180~2270): 사전등록 NG5-0과 일치 — 농민 선택(재시도 좌표 1개) → 건물 클릭·`ps3_building` → 생산 좌표 2개(두 번째가 재시도) → 쌀/나무 감소 또는 `used` 증가 → `ps3_produce` → 드래그 선택 + 우클릭 이동(유닛 tile 변화) → 60초 dwell. PASS = 선택 효과 AND (생산 OR 이동).
- `trace_dropped_count`(5274~5278): 후보 lane 최종 summary `dropped_count != 0`이면 FAIL, summary가 없으면 None → FAIL(실패 쪽으로 닫힘). 최상위 status는 두 lane `new_game_act.status`를 gate한다(6196~6202). `--new-game-act`는 `--new-game-start` 없이 parser error(6159).
- **경미 결함 1(수리 불요, 판정 영향 없음):** `drag.effect`는 `count >= 1`만 본다. 직전에 건물이 선택돼 count가 이미 1이므로 드래그가 실패해도 true가 된다. 이번 run에서 드래그가 실제로 됐다는 근거는 `drag.slots=[1198]`(건물 1199와 다름)과 그 유닛의 이동 효과 true다. 다음에 이 파일을 고치는 work가 "선택 slot 집합 변화"로 바꾸면 된다(backlog).
- 테스트 `tests/test_g1_new_game_path.py` 27건(그중 act·dropped 8건). focused 3파일 **287 passed/11.92s**(로그 `logs/gates/lap1116-middle-focused.log` `2a901884…`). 하네스·테스트 SHA는 lap1115 full PASS(1730) 때와 같다.

## 5. 판정

- **H-NG5 `PASS(partial, 기술·격리)` 수용.** 정정 1: work의 "약 4분 이내"는 실제 PS3 present 길이로 148.8초(행동+스크롤+dwell 구간 135.4초)다. 판정 영향 없음. 새 게임에서 선택·건물 선택·생산·드래그·이동·새 유닛이 있는 2.5분 동안 PS3 HD min 99.966%(e 1 present 일시 stale)·나머지 100%·V1/안전 7종 0·dropped 0·scale2x PASS, 2/2 run. 제품 C 변경 없음 → G1 후보 DLL은 lap1106 H-P35 트리 그대로다. 사용자 합격도 G1 마감도 아니다.
- 공개 한계 유지: 안개·정지 지형·유닛 1~2명이라 부하 대표성이 낮다(save006 PS3 min 99.26%·save000 98.60%는 별도 근거). 전투·건설·다수 유닛 없음. pair 픽셀 비교는 gate 아님.
- 시험판 재스테이징: 계속 보류(lap1109 §4 사유 유지 — 사용자가 lap1104 판으로 시험 중일 수 있음).

## 6. 다음 선택 (ESCALATE 4번)

- "G1 사용자 승인 요청 준비"는 고르지 않는다. 시험 요청(APPROVALS lap1104)은 이미 올라가 있고 결과를 기다리는 중이며, 문서만 늘리는 회차는 PROMPT ③ 제한에 걸린다.
- "전체 HD coverage" 중 G1 기록에 측정이 **한 번도 없는** 화면은 게임 중 일시정지 메뉴(Esc → program_state 23)와 그 안의 저장 창이다(G1 laps에서 PS23 측정 0건, 하네스에도 PS23 경로 없음). 사용자 시험 절차 ③·④(메뉴 버튼 위치 대응)가 그대로 지나가는 화면이고, 메뉴 클릭이 상태를 바꾸는지로 후보 lane의 클릭 좌표 대응도 함께 확인된다. 승패 화면은 게임을 끝내야 해서 비용이 크다. 타이틀(PS9 메인 메뉴 100%와 별개 화면인지 미확정)·혼자하기 대기실은 그다음 후보로 남긴다. → **work H-PM0 사전등록.**

## 7. 다음 work 사전등록(Sonnet) — H-PM0: 게임 중 일시정지 메뉴·저장 창 HD

**가설:** 새 게임 PS3에서 Esc로 연 일시정지 메뉴(PS23)와 저장 창도 미러 경로를 타서 index≥1 HD ≥90%·V1·안전 0이다. 반대 가능성: 메뉴가 다른 present 경로(예: 화면 직접 BltFast·GDI)라 mirror present가 없거나 낮다 → 그러면 그것이 G1 coverage 잔여다.

- **PM0-0 하네스(TDD):** 새 옵션(이름은 구현자가 정한다. 예 `--new-game-menu`, `--new-game-start` 필수). 순서: `ps3_start`(그리고 `--new-game-act`가 있으면 그 뒤) → Esc → `ps==23` 대기(다른 값이면 그 값을 기록) → 10초 또는 PS23 mirror present 40개 dwell → `pause` 캡처 → 저장 버튼 클릭 → 1초 뒤 상태 기록 → 10초 dwell → `save_window` 캡처 → 저장 창 돌아가기 클릭 → `pause_return` 캡처 → 계속하기 클릭 → `ps==3` 대기 → 10초 dwell → `ps3_resume` 캡처 → (`--new-game-play`가 있으면 그다음). **저장 실행(SAVE_ACTION)은 누르지 않는다**(파일 쓰기 없음). 좌표 출발점은 G5 probe의 논리 800×600 값 `tools/g5_candidate_drag_probe.py:67-72`(저장 `(400,238)`·돌아가기 `(464,372)`·계속 `(400,132)`)이고, 상태 변화로 확인한다. 상태가 안 바뀌면 1회만 재시도한다.
  - 창 요약은 PS3 전용 `_summarize_play_presents`를 그대로 쓰지 말고 **창 안 모든 program_state의 mirror present**를 state별로 센다. 또 창 안 화면 대상 present 중 mirror present가 아닌 것(예: summary `primary_present_count`와 mirror 수 차이, 창별로 셀 수 있는 raw가 있으면 그것)을 공개한다. 창 PASS = mirror present >0·index≥1 HD ≥90%·V1/안전 0·fallback 0·success 1, run 전체 dropped 0. 기존 NG3/NG4/NG5·3/9/35 경로는 바꾸지 않는다. 테스트 RED→GREEN.
- **PM0-1 측정(격리 run 2회, `--hd-source scale2x --new-game-path --new-game-start --new-game-menu`):** 창별(pause/save_window/pause_return/resume) state별 mirror present 수·HD 첫/min(index≥1)/p50·98.6%·90% 미만 개수와 seq·stale max·V1·안전 7종·fallback·dropped·경과 p95, `menu_copy_calls`·`partial_copy_calls`·`frame_copy_calls`·`*_reject_*` 계수의 창 전후 증가, 상태 전이(23·저장 창 state·3)와 클릭 횟수, 캡처 4장(1600×1200에서 메뉴가 원래 비율·위치인지).
  - **PASS:** 모든 메뉴 창 mirror present >0·index≥1 HD ≥90%, V1·안전 0, dropped 0, scale2x PASS, 클릭으로 상태 전이 3회(23→저장 창→23→3) 성공, resume 뒤 PS3 HD ≥98.6%, 2/2 run. 98.6% 미만 present가 있으면 개수·seq·위치를 공개하고 middle이 귀속한다.
  - **FAIL/귀속:** mirror present 0 또는 HD <90%면 수리하지 않는다. 그 화면을 그린 경로(trace `blt`/`blt_fast` 화면 대상·GDI·menu/partial/frame copy 계수 변화)와 캡처 대 독자 Scale2x 비교(lap1111 `cmp_ps3_lap1111.py` 방식) 위치를 넘긴다(가설 1개).
  - **BLOCKED:** Esc가 게임에 안 들어가거나(포커스) 클릭이 상태를 안 바꾸면 1회 재시도(빈 땅 클릭 뒤 Esc 등) 뒤 상태값·캡처와 함께 넘긴다. 60분 또는 실패 가설 2회(PROMPT ③).
- 판정 밖 기록: nation·시작 카메라, baseline lane 같은 순서의 상태 전이(픽셀 비교는 gate 아님).
- 공통: source를 바꾸면 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 104GiB) 확인, 끝나면 game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지, 시험판 재스테이징 없음. 사용자 G1 시험 결과가 들어오면 그것이 최우선이다.

backlog(유지·추가): e scroll_LEFT 단발 primitive stale 162(lap1116, 귀속 안 함), `drag.effect` 판별력(§4), 승패 화면·타이틀·혼자하기 대기실·옵션 하위 창·PS2 로딩 HD, PS7·PS5 글자·버튼 모서리 stale 1.2~1.8%(TextOutA `reject_target`·`0x465E80` `reject_target` 단서), `--census-state 5|7` 실제 실행, 픽셀 정확 오라클, throttle ord 123 writer, `0x467E60` wrap, lane 위상 경합, 진단 동반 영역, 입력 trace 512 상한, 화면 인구 30 vs 메모리 `used` 20.

## 8. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`를 돌린다. 결과는 STATUS에만 쓴다. focused 테스트는 §4(287 passed).
- 전체 `make check`는 SKIP한다. 이번 변경은 문서뿐이고 하네스·테스트·C source는 lap1115 full PASS(1730) 때와 같다(그 뒤 바뀐 source 파일 0).

## 다음 한 가지

work(Sonnet): §7 H-PM0 — PM0-0 하네스(Esc 메뉴·저장 창·복귀, state별 mirror present 요약) → PM0-1 측정 2회. 사용자 G1 시험 결과가 들어오면 그것을 최우선으로 처리한다.
