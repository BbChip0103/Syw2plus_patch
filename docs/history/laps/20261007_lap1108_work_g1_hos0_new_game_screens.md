# 2026-10-07 | lap1108 | G1 work — H-OS0 새 게임 경로 화면(PS7 접속방식·PS5 혼자하기 대기실) HD coverage 측정

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work 1 lap. 커밋 0, 전부 uncommitted.
- 목표·가설: lap1107 사전등록 §3 — PS7·PS5가 H-P35 뒤 HD ≥90%이거나 미달 픽셀이 census로 귀속된다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — 두 run baseline·candidate의 `source_exe_sha256`·`private_exe_sha256` 모두 MATCH, `source_unchanged` true. 제품 C 소스 변경 0(bridge는 기존 트리).
- fixture: 새 게임 경로라 save 불필요. 키 입력 0(채팅 EDIT 포커스 비접촉). 클릭 = g6 probe와 같은 논리 좌표.

## 변경 파일

- `tools/g1_saved_scene_probe.py`(`dbe31957…`): 상수 `NEW_GAME_MENU=(184,560)`·`NEW_GAME_CONFIRM=(608,564)`(g6 probe 출처 주석), `_click_until_state`(클릭 후 1초 지나도 이전 상태일 때만 1회 재시도), `_walk_new_game_path`(PS9→PS7→PS5, 각 화면에서 candidate는 mirror2x_present 64개·census는 census window·baseline은 8초 대기 뒤 캡처, 시작 클릭 전에 종료), `_run_lane(new_game_path=)`, `--census-state` choices `(3,5,7,9,35)`, 새 `--new-game-path`(scale2x 필수·`--census-only`와 배타; baseline·candidate 두 lane, `new-game-path-result.json`), candidate trace validator `required_states=(9,7,5)`(이 모드만).
- `tests/test_g1_new_game_path.py`(신규 7건, `5221503d…`): 소스 계약 5 + `_click_until_state` 동작 2(재시도·무재전송). RED 7 failed → GREEN. `tests/test_g1_census.py`(`74af4e06…`): 기존 PS35 소스 계약의 choices 문자열만 새 값으로 갱신.

## 실행·수치 (OS0-1, 격리 run 2회: `--hd-source scale2x --new-game-path`)

- 명령: `.venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1108_ng_{a,b} --artifact-root <공유temp>/20261007_lap1108_work_hos0/ng_{a,b} --hd-source scale2x --new-game-path` exit 0 ×2, status PASS, scale2x validator PASS, cleanup ok·game 사본 삭제·`source_unchanged`. 한 번에 PS7·PS5 진입(`(184,560)`→PS7, `(608,564)`→PS5; 사전등록 대로 `(462,169)` 불필요). 네 lane(a·b × baseline·candidate) 모두 두 전환에서 클릭 1회씩, 재시도 0(raw `actions`). 남은 `local/runtime/lap1108_ng_*`(각 1.2GB)는 private prefix·manifest·output으로 보존했다(game 사본만 삭제).
- 식: present별 HD = (covered − stale)/480,000. 스크립트 `recalc_hos0.py`(`2e8cfab0…`) → `recalc_hos0.json`(`0f96ab1b…`).

| run | 상태 | present | HD 첫 / min / p50 | stale max | V1 outside max | inside diff 범위 | 경과 p95 |
|---|---|---|---|---|---|---|---|
| a | PS9 | 69 | 100 / 100 / 100 | 0 | 0 | 116,238~116,298 | 14ms |
| a | **PS7** | 158 | **98.166 / 98.166 / 98.166** | 8,803 | 0 | 107,674~107,748 | 15ms |
| a | **PS5** | 90 | **99.024 / 98.801 / 98.801** | 5,754 | 0 | 102,956~103,362 | 14ms |
| b | PS9 | 67 | 100 / 100 / 100 | 0 | 0 | 116,238~116,298 | 14ms |
| b | **PS7** | 159 | **98.166 / 98.166 / 98.166** | 8,803 | 0 | 107,674~107,748 | 15ms |
| b | **PS5** | 92 | **99.024 / 98.801 / 98.802** | 5,754 | 0 | 102,957~103,362 | 15ms |

- 안전 7종 최대 0(두 run 전 present), dropped 0, fallback 0, success 전부 1, covered_min 480,000(전 픽셀 covered). `menu_copy_calls`가 PS9·PS7·PS5 모두에서 present 수만큼 늘고(a: 68/158/90, b: 66/159/92) `partial_copy_calls`·`frame_copy_calls`·`frame_copy_rejects`는 0 — PS7·PS5는 PS9와 같은 전체 프레임 메뉴 복사 경로다. H-P35의 부분 사각형 경로는 이 화면에서 돌지 않았다.
- 판정: PS7 98.166%·PS5 98.801% ≥ 90%, index≥1 90% 미만 present 0, V1 0, 안전 0, 2/2 → **H-OS0 PASS(partial, 기술·격리)**. census 귀속은 미달이 없어 실행하지 않았다(`--census-state 5|7` 하네스는 구현·소스 계약 테스트만, 실행은 미검증).
- 화면 확인: candidate 캡처 `ps7.png`(`72e8e3b6…`, 접속방식 선택: IPX 대전/혼자하기 버튼·목록), `ps5.png`(`03e4219b…`, 혼자하기 대기실: 1P·컴퓨터·맵 목록) 직접 열람, 1600×1200 UI 정상. baseline `ps7.png`(`03768243…`)·`ps5.png`(`b179c67a…`).

## 공개 UNKNOWN·한계

- stale 잔여 PS7 8,803 px(1.83%)·PS5 5,754 px(1.20%)는 귀속하지 않았다(90% 기준 충족이라 사전등록상 census 불필요). 위치는 화면 가장자리·버튼 등 추정이며 raw에 없다.
- 후보 PS7·PS5 픽셀 정확 Scale2x 오라클 없음(PS35와 같은 한계; 화면 태그 V2/V2s 밖). nearest oracle 값(0.776~0.799)은 `mirror_validator`가 identity용 임계 0.999로 BLOCKED를 내지만 scale2x 모드의 gate가 아니다(기존 pair에서도 scale2x validator만 gate).
- 게임 시작(PS5 → PS3 새 게임 진입) 이후는 측정하지 않았다(사전등록 §3 "가능하면" 항목; 시작 클릭 시 맵 생성이라 별도 가설).
- 타이틀 이전·옵션·게임 중 저장 창·승패 화면 HD는 미측정(backlog). 사용자 시험판 재스테이징 없음(사전등록 §2).
- 검사 결과(make check)는 STATUS에 보강한다.

## 다음 행동

middle(Opus): H-OS0 독립 재계산(두 trace·캡처) 후 수용, 시험판 재스테이징 여부(H-P35·H-OS0 묶음)와 다음 한 가지(게임 시작 직후 PS3 진입·옵션·저장 창·승패 화면 중 선택, 또는 G1 사용자 승인 요청 준비) 결정. 사용자 G1 시험 결과가 먼저 오면 그것을 최우선으로 처리한다.
