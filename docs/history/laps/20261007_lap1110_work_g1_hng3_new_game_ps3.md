# 2026-10-07 | lap1110 | G1 work — H-NG3 새 게임 시작 직후 PS3 HD(두 번째 장면)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. 제품 C 소스 변경 0, 커밋 0.
- 가설: 새 게임 PS3도 불러오기 PS3와 같은 미러 경로로 그려지므로 HD ≥98.6%·V1·안전 0.
- 예상 PASS(사전등록 §5): PS3 index≥1 모든 present HD ≥90%·V1 outside 0·안전 7종 0·dropped 0·scale2x validator PASS·2/2 run.
- 변경 파일(uncommitted): `tools/g1_saved_scene_probe.py`(sha256 `e0680c75…`)·`tests/test_g1_new_game_path.py`(`c0f75fa8…`). 제품 `tools/inmm_stub/*` 이번 lap 변경 없음(후보 DLL = lap1106 H-P35 트리).
- 원본 SHA: `b56986e018b43293…` 4 lane 모두 private·source 일치, `source_unchanged` true, cleanup ok. fixture: 새 게임 경로(save 불필요, 첫 맵 기본), 활성 8 player records(local seat 0).

## 변경 (NG3-0, TDD RED→GREEN)

- `_start_new_game`: g6 probe 511~536행 규칙. PS5에서 최대 8초 PS2/PS3 대기 → 아니면 `(608,564)` **1회** → `ps==3 and tick>0` 대기.
- `_walk_new_game_path(start_game=)`: PS5 dwell·캡처 뒤 시작 → 6초 대기 → candidate는 PS3 mirror present ≥256 대기(timeout 120s)·baseline은 12초 추가 대기 → `ps3_start` 캡처·`_scene_identity`.
- `--new-game-start`(`--new-game-path` 필수), `_run_lane(new_game_start=)`, candidate validator `required_states=(9,7,5,3)`(시작 시)·요약 lane 필드에 `new_game_start`.
- §3 결함 수리: 요약 `status`가 candidate `scale2x_validator.status == "PASS"`를 포함.
- 테스트: `test_g1_new_game_path.py` +5(옵션 계약 3·시작 규칙 행동 2 — auto-start 시 클릭 0, 미시작 시 클릭 1회), 기존 required_states 계약 1건을 새 식으로 갱신. RED 5 failed → GREEN 12 passed. lint·typecheck PASS.

## 실행 (NG3-1, 격리 run 2회)

- 명령: `.venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1110_ng3_{a,b} --artifact-root <공유temp>/20261007_lap1110_work_hng3/ng3_{a,b} --hd-source scale2x --new-game-path --new-game-start`. exit 0 ×2, status PASS, scale2x validator PASS, mirror validator BLOCKED(nearest oracle 0.776 < 0.999 — lap1106·1108과 같은 기존 사유, scale2x 모드 gate 아님). 로그 `logs/gates/lap1110-ng3-{a,b}.log`(`c46cb7fc…`·`edcf09b7…`).
- 분석: 공유 temp `…/20261007_lap1110_work_hng3/recalc_ng3.py`(`6cc0ea9a…`) → `recalc_ng3.json`(`0f9afbbe…`). 식: HD = (covered − stale)/480,000.
- 클릭: 네 lane 모두 PS7·PS5·시작 전환 각 클릭 1회(raw `actions`: 시작 클릭도 1회 — PS5 dwell 동안 자동 시작이 일어나지 않아 `(608,564)` 1회 사용). 시작 tick baseline 3·candidate 4.

| run | 상태 | present | HD 첫 / min(≥1) / p50 | stale min~max·마지막40 중앙값 | V1 outside | 안전 7종 | menu/partial/frame copy 증가 | 경과 p95 |
|---|---|---|---|---|---|---|---|---|
| a | PS9 | 70 | 100 / 100 / 100 | 0 | 0 | 0 | 70/0/0 | 14ms |
| a | PS7 | 157 | 98.166 / 98.166 / 98.166 | 8,793~8,803 | 0 | 0 | 157/0/0 | 16ms |
| a | PS5 | 735 | 99.024 / 98.719 / 98.801 | 4,684~6,147·6,145 | 0 | 0 | 735/0/0 | 14ms |
| a | **PS3(시작)** | **264** | **100 / 100 / 100** | **0 / 0** | **0** | **0** | 0/0/0 | **7ms** |
| b | PS9 | 69 | 100 / 100 / 100 | 0 | 0 | 0 | 69/0/0 | 14ms |
| b | PS7 | 153 | 98.166 / 98.166 / 98.166 | 8,793~8,803 | 0 | 0 | 153/0/0 | 15ms |
| b | PS5 | 735 | 99.024 / 98.719 / 98.801 | 4,684~6,147·6,145 | 0 | 0 | 735/0/0 | 15ms |
| b | **PS3(시작)** | **265** | **100 / 100 / 100** | **0 / 0** | **0** | **0** | 0/0/0 | **7ms** |

- 상태 순서 9→7→5→3(PS2 present는 미러 trace에 없음), fallback 0·success 1·dropped 0(a·b), 90% 미만 present 0(PS3 포함 전 상태), 98.6% 미만은 PS3에 0(PS7 98.166%는 H-OS0 공개 그대로).
- 캡처 직접 열람(a candidate·baseline `ps3_start.png`): 새 게임 시작 직후 장면(농장 밭·정자·농민 1·자원 5000/5000·인구 20/1500·하단 HUD·미니맵 검정), candidate 1600×1200이 baseline 800×600과 같은 배치·비율. SHA a candidate `bfb1ea8e…`·baseline `6972c2bc…`, b candidate `fb0c2980…`·baseline `a8b42b46…`. trace SHA a `88740fc9…`·b `12a750b5…`.

## 판정

- **H-NG3 `PASS(partial, 기술·격리)`**: 사전등록 기준 전부 충족 2/2(PS3 HD 100%·V1 0·안전 0·dropped 0·scale2x PASS).
- 한계(공개): (1) 이 장면은 시작 직후 고정 카메라·안개·유닛 거의 없음이라 PS3 stale 0이 부하 장면의 HD를 대표하지 않는다(save006·save000 PS3 min 99.26/98.60은 별도 기존 수치). 스크롤·유닛 증가 뒤 새 게임 장면은 미측정. (2) 맵 이름은 raw에 없고 캡처로만 확인(농장 시작 지형, 기본 첫 맵 기대와의 일치는 UNKNOWN). (3) baseline·candidate 시작 시 nation이 무작위로 달라(a: 3·3 / b: 2·1 owner 0) pair 픽셀 비교·입력효과는 gate 아님(사전등록대로). (4) PS2 로딩 화면 HD·검정 구간 길이는 미측정(PS2 mirror present 0건). (5) 픽셀 정확 오라클·PS7·PS5 글자 stale 귀속·`--census-state 5|7` 실행은 그대로 UNKNOWN. 사용자 합격·G1 마감 아님.
- 원본 SHA 불변·game 사본은 harness가 삭제(prefix·manifest·output 보존)·전부 uncommitted. 시험판 재스테이징 없음.

## 다음 한 가지

middle(Opus): 이 기록의 독립 재계산·H-NG3 수용 여부 판정. 이후 후보: 새 게임 PS3의 스크롤·유닛 증가 시점 HD(부하 장면), HUD/GDI·전체 HD coverage·G1 사용자 승인 요청 준비. 사용자 G1 시험 결과가 오면 최우선.
