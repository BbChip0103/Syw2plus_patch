# 2026-10-07 | lap1115 | G1 work — H-NG5 새 게임 행동(선택·생산·드래그 이동) + 스크롤 + 60초 dwell PS3 HD

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(hands-on 구현) 1 lap. 제품 C 소스 변경 0, 커밋 0.
- 입력: lap1113 middle 사전등록 §5(H-NG5), INBOX 2026-10-07 03:55 root 복구 메모(lap1114 work 중단 — 기록·STATUS 없음), lap1114 남은 산출물 검수. APPROVALS 새 반려 없음, `loop/STOP`·`loop/ESCALATE_SOL` 없음.
- 가설: 새 게임에서 농민 선택·건물 선택(HP 바·생산 패널)·농민 생산·드래그 선택·우클릭 이동·새 유닛이 있어도 미러 경로가 같아 PS3 HD ≥90%(관측은 ≥98.6%)·V1·안전 7종 0이 유지된다.
- 예상 PASS: 모든 창 index≥1 HD ≥90%, V1·안전 0, dropped 0, scale2x PASS, 선택 효과 ≥1, 생산 또는 이동 효과 ≥1, 2/2 run.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). 후보 DLL = lap1106 H-P35 트리(제품 C 무변경). fixture: 새 게임 경로 PS9→PS7→PS5→PS3, save 없음, 활성 8 player records(활성 8인 부하 증거 아님).

## 1. lap1114 잔여 검수 (재사용 판단)

- lap1114 하네스 변경(`tools/g1_saved_scene_probe.py` `_new_game_act_window`·`--new-game-act`·`trace_dropped_count` gate, `tests/test_g1_new_game_path.py`)은 코드 읽기로 §5 NG5-0과 대조했다: 선택 수(`_selection_observation`) → 건물 클릭 → 생산 버튼 → 자원/`used` 변화 → 드래그 선택 + 우클릭 이동(유닛 tile 변화) → dwell, 창별 PS3 present 요약, 창 PASS에 `dropped_count==0`. 클릭 재시도는 선택 1회(좌표 2개)·생산 좌표 2개.
- lap1114 run 이력(복구 판정): a·b(`ng5_a/b`)는 생산 버튼 좌표가 틀려 `produce.effect=false`(자원 변화 없음, 이동 효과만으로 PASS)였던 **이전 하네스 버전**이라 근거에서 제외한다. 하네스 수정(`produce` 좌표 `(668,539)`)이 02:57:12에 저장됐고 c가 02:57:15에 시작했으므로 **c는 현재 하네스 run**이다. d는 03:04 중단(exit 없음)·결과 없음 → 근거 아님. d의 `game` 사본(aborted, 프로세스 없음)만 삭제했다(`local/runtime/lap1114_ng5_d` 나머지 보존).
- 현재 하네스 테스트: `tests/test_g1_new_game_path.py`·`tests/test_g1_saved_scene_probe.py` **244 passed/11.51s**, `make lint`·`make typecheck` PASS(재실행).

## 2. 측정 — 현재 하네스 2 run (c = lap1114 산출물 재사용, e = 이번 lap 신규)

명령(e): `.venv/bin/python -u tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap1115_ng5_e --artifact-root <공유 temp>/20261007_lap1115_work_hng5/ng5_e --hd-source scale2x --new-game-path --new-game-start --new-game-act --new-game-play` (c도 같은 플래그; 로그 `logs/gates/lap1114-ng5-c.log` `a5acef3d…`·`logs/gates/lap1115-ng5-e.log` `89bf01cf…`, exit 0×2, 최상위 status PASS).

새 스크립트 재계산(`recalc_ng5.py` 공유 temp `20261007_lap1115_work_hng5/`, 후보 `trace_raw.jsonl`에서 창 줄 범위로 present HD = `(covered−stale)/480,000`을 직접 계산):

| run | 이벤트 | dropped | select | produce | drag_move | dwell(액션 뒤) | scroll R/D/L/U | dwell(스크롤 뒤) |
|---|---|---|---|---|---|---|---|---|
| c | 5,065 | 0 | 4 / min 100% | 33 / 100% | 23 / 100% | 1,200 / 100% | 40·40·40·41 / 100% | 1,200 / 100% |
| e | 5,115 | 0 | 4 / 100% | 33 / 100% | 23 / 100% | 1,200 / 100% | 40·40·41·40 / **99.966%**(LEFT 1 present, stale 162) | 1,200 / 100% |

- HD <98.6% present 0·<90% 0, stale max c 0·e 162(scroll_LEFT 1 present, 다음 present에서 해소), V1 outside 0, 안전 7종 0, fallback 0, success 1, 경과 p95 4~7ms, scale2x validator PASS, cleanup ok·source_unchanged true, 후보 `trace_dropped_count` 0.
- 입력 효과(c·e·두 lane 공통): 선택 수 0→1(slot 1198, 좌표 (418,322) 첫 시도), 건물 선택(slot 1199) 뒤 생산 버튼 `(668,539)` 1회 → 쌀 5000→4200(−800)·`used` 20→20(큐 대기, 인구는 생산 완료 때 증가)·나무는 baseline 5000→4700·후보 5000→5000(lane마다 nation이 무작위라 비용 구성이 다를 수 있음, 판정 밖 기록), 드래그 선택 효과 true(slot [1198]), 우클릭 이동 뒤 유닛 tile 변화 true. 키 4구간 candidate 이동 40칸×4(c)·40칸(e), `camera_after_dwell` (8,47).
- 캡처 직접 열람(c candidate `ps3_building`/`ps3_produce`/`ps3_act` 1600×1200): 건물 선택 시 HP 막대·체력 4800/4800·방어력 33/33·생산 큐 1%·농민 초상·명령 패널 글자가 정상 렌더링되고, 생산 뒤 두 번째 농민이 나타나 선택 원·HP 막대·좌측 초상이 정상이다. 깨짐·흑색 띠·어긋남 없음.
- e candidate `ps3_act` 열람: 다른 nation(건물 모양 상이, 쌀 4200·나무 4700·인구 30/1500)이고 새 유닛 선택 원·HP 막대·체력 500/500·명령 패널 정상, 깨짐 없음. 나무 비용 차이(c 후보 5000 vs e 4700)는 nation 차이로 보이나 귀속은 UNKNOWN(판정 밖).
- trace 상한: c 5,065·e 5,115 events(상한 8,192 미만, dropped 0).

## 3. 판정

- **H-NG5 `PASS(partial, 기술·격리)`**: 선택·건물 선택·생산 클릭·드래그 선택·이동 명령·새 유닛·몇 분(행동 약 1분 + 스크롤 8초 + dwell 60초×2 ≈ 4분 이내) 동안 PS3 HD min 99.966%(e 1 present)·그 외 100%·V1/안전 0·dropped 0·scale2x PASS, 현재 하네스 2/2. 사용자 합격도 G1 마감도 아니다.
- 공개 한계: 생산 큐 `used`는 아직 대기라 인구 증가 근거는 새 유닛이 보이는 `ps3_act` 캡처(c·e 열람)로 확인, 안개·정지 지형이라 부하 대표성 낮음, 전투·다수 유닛·건설·AI 변화 없음, pair 픽셀 비교 gate 아님, a·b는 이전 하네스 버전 이력으로 제외(투명하게 기록), d 중단. 선택 HUD·HP 바·생산 패널 글자는 두 run에서 stale 0이므로 PS7·PS5의 TextOutA `reject_target` 단서(backlog)는 PS3 새 게임에서 재현되지 않았다.
- 제품 C 변경 없음 → 후보 DLL은 lap1106 H-P35 트리 그대로.

## 4. 검사

- `make check`는 이 기록 freeze 뒤 1회 실행하고 결과는 STATUS에만 쓴다(PROMPT ⑥).

## 다음 한 가지

middle(Opus): H-NG5 독립 재계산·수용 판정. 이어 work: 전체 HD coverage(타이틀·옵션·저장 창·승패 화면) 또는 G1 사용자 승인 요청 준비. 사용자 G1 시험 결과가 들어오면 그것이 최우선이다.
