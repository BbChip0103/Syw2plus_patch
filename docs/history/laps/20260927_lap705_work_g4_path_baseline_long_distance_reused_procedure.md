# 2026-09-27 | lap 705 | 목표 G4 (G4-P1 원본 길찾기 baseline)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 (실무), STATUS 2026-09-27 06:05
  운영자 지시 그대로 수행.
- 가설 / 사용자 관찰: lap704가 BLOCKED — 새 `tools/g4_path_baseline_probe.py`(12방향 컴퍼스 목적지
  후보, `MIN_DESTINATION_DISTANCE_TILES=20`)에서 조밀 fixture 19기가 1틱도 이동하지 않았다. 06:05
  지시는 "새로 추측하지 말고 `tools/g5_worker_relative_move_attack_probe.py`(lap682, 원본 20/20
  이동 수렴 2/2 재현 검증됨)의 fixture 생성·드래그·우클릭 절차를 그대로 재사용하고, 차이는 목적지
  거리와 궤적 기록만 추가"하라고 지정했다. 두 스크립트를 줄 단위로 대조한 결과 **fixture
  생성·드래그·9점 보정 절차는 이미 완전히 동일**했다(둘 다
  `tools.g5_candidate_drag_probe`에서 동일 상수/헬퍼를 import: `owner=0`, `SEED_TYPE`,
  `dense_fixture_requests`, `SupplyProbe.call(op=5, ...)`, `DRAG_START/DRAG_END`,
  `CALIBRATION_SCREEN_POINTS` 9점, `MINIMAP_CLICK`) — **1줄 diff: 유닛
  type·소유자·스폰 방식·9회 보정 클릭 여부 차이는 0건**, 실제 차이는 lap704가 새로 추가한
  `MIN_DESTINATION_DISTANCE_TILES=20` 목적지 탐색(12방향 컴퍼스, 대각선 포함)과 궤적 기록
  로직뿐이었다. 이 12방향 탐색이 실측 window 20타일 밖 지점을 골라(예: run1 클릭
  `[1375,337]`, 실측 원본 창은 800×600 — `runtime_env._game_window_ids` 기본
  `allowed_sizes=((800,600),)`) 실제 렌더 영역 밖을 클릭한 것으로 드러났다(회차 내부 재검산: 위
  12개 후보 전부 실측 박스 밖). 원인은 좌표 추측이 아니라 **측정 안 된 창 크기 가정**이었다.
- 예상 PASS / FAIL 조건: 06:05 지시는 명시적 PASS/FAIL 식을 주지 않았다 — "baseline 3회를
  측정한다"만 요구. 이 lap은 하네스 자체(선택20·정리·SHA 불변)와 raw 이동 수치(명령 도달 수,
  도착률, 경로비)를 3회 fresh로 raw 기록하는 것을 성공 기준으로 삼았다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g4_path_baseline_probe.py`
  수정(12방향 컴퍼스 탐색 제거 → lap682와 동일한 단일축(dy만) primary/fallback 스타일로 교체,
  `MIN_DESTINATION_DISTANCE_TILES=20`(실측 불가능) 대신 실측 window 크기 기반
  `safe_screen_box()`(`content_info["width"/"height"]`에서 유도, 하드코딩 800×600 가정 제거)와
  `LONG_DISTANCE_OFFSET_MAGNITUDES=(12,10,8)`(lap682 자신의 dy=6/dy=-4보다 명시적으로 먼 거리)
  도입), `tests/test_g4_path_baseline_probe.py` 동기화(3개 신규/수정 단위 테스트).
  `tools/g5_worker_relative_move_attack_probe.py`는 이 lap에서 **수정하지 않음**(git status의
  기존 unstaged diff는 lap688 이전 작업분이며 이 lap이 만든 것이 아님, 확인함).
  uncommitted, `LOOP_ALLOW_COMMITS=0`. 게임 EXE/DLL 미변경.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(3회 모두 실행 전후 불변,
  `source_unchanged=true`). 후보 없음(원본 전용, `--variant` 옵션 없이 항상 original). 환경
  `[ESL]Syw2plus/` 소스, 1600x1200x24 Xvfb(게임 창 자체는 실측 800×600 native), `SYW2_SUPPLY_PROBE=1`
  진단 브리지. 활성 플레이어: 솔로(비고정 시드) 1인. 지도: 미고정(unseeded solo 로비 — run1/run2는
  우연히 워커 world (93,46)로 동일, run3는 (10,39)로 상이 — 지형 run간 상이 명시). 군대/fixture:
  기존 워커(슬롯1198) + `dense_fixture_requests`로 owner0 type2 55기(1198 제외 7x8-1 격자), 원본
  20-cap 드래그로 20기 선택. 목적지: 워커 기준 world (0,-10) 오프셋, 10타일(원본 20-cap 선택
  드래그와 동일 좌표계, lap682의 dy=6/dy=-4보다 명시적으로 먼 거리 — 실측 800×600 창에서
  self-calibration 후 도달 가능한 최대치에 가까움, `LONG_DISTANCE_OFFSET_MAGNITUDES=(12,10,8)`
  중 12·10은 화면 밖으로 탈락, 10이 3회 모두 채택됨).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  1. `PYTHONPATH=. .venv/bin/python tools/g4_path_baseline_probe.py --runtime-root
     local/runtime/g4-lap705-baseline-run1 --artifact-root
     .../temp/Syw2plus_patch/20260927_lap705_g4_path_baseline_run1` → exit0.
  2. 동일 명령 `run2`/`run3`(각각 새 runtime-root/artifact-root) → 모두 exit0.
  결과 JSON SHA256: run1 `f6d17ade2f19cc802cd84e4765f29950cfcb92ff68d596d0a193c961b157df74`,
  run2 `cb2ca1df4f5b0bdf761166adb5583b876082ffcdec33a92fe327497cd04068e0`,
  run3 `6d08f4ffaafe8522a3933eb4c0e4fa444802b201e786924b914237efc57d3543`(각
  `<artifact-root>/probe-result.json`, raw `(tick,x,y,command,hp)` 598 샘플/실행 포함,
  스키마 `syw2plus.g4-path-baseline-probe.v1`). 캡처 4종(`after-minimap/after-fixture/
  after-drag/after-move-click.png`) 각 run artifact-root에 보존. 로그
  `logs/gates/20260927_lap705_g4_path_baseline_make_check.log`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 하네스 자체는 3회 모두 **PASS**(선택20/20, `cleanup.ok
  =true`, `source_unchanged=true`, exit0). 이동 결과는 raw로 **엇갈렸다**:
  - run1: `ever_move_command_count=20/20`, `arrival_rate=0.9`(18/20, 반경3타일), 도착 tick
    중앙 352.5·최대402, `path_ratio_median=1.112`.
  - run2: `ever_move_command_count=20/20`, `arrival_rate=0.85`(17/20), 도착 tick 중앙328·최대382,
    `path_ratio_median=1.156`.
  - run3: `ever_move_command_count=0/20`, `arrival_rate=0.05`(1/20, 우연 근접 추정),
    `path_ratio_median=0.0` — 20기 중 단 한 기도 이동 명령을 받은 관측이 없다.
  같은 코드·같은 거리(10타일)·같은 fixture 절차로 2/3은 명령 도달 20/20을 얻었고 1/3은 0/20이다.
  run1/run2는 워커 절대 world 위치가 우연히 동일(93,46)했고 run3만 달랐다(10,39) — 지형/스폰
  위치 의존일 가능성이 있으나 이번 lap에서 원인 귀속은 하지 않았다(운영자 지시 범위 밖, 추측
  금지). STATUS 판정식(명령도달<20 2회 반복→NOT_FEASIBLE)은 이번 3회에 적용하면 실패 1회뿐이라
  해당하지 않는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 신규 단위 테스트 3개(`test_g4_path_baseline_probe.py`:
  `LONG_DISTANCE_OFFSET_MAGNITUDES`가 lap682 기준선(6)보다 큼, `safe_screen_box()`가 실측
  800x600에서 기존 상수와 동일 박스를 유도, `_safe_box_margin` 부호) 전부 PASS. `make check`
  **1032 passed(842.21s)**, ruff/compileall/mypy/`CONTEXT_PASS` 전부 PASS,
  `checks/safety.sh check` → `SAFETY_PASS`. 남은 위험: run3의 완전 0/20 원인 미귀속(지형/스폰
  의존 가설, 검증 안 됨) — 이 baseline을 "원본 길찾기 성능" 수치로 그대로 쓰기 전에 반복 횟수를
  늘려 지형 의존성을 갈라야 한다. 독립 검수/사용자 승인 없음(work tier 자체 실행 보고, 이번 지시는
  미들 검수 요청 대상이 아님 — 06:05 지시가 요구한 baseline 측정 완료 보고).
- 다음 한 가지: (a) 동일 하네스를 N=5 이상으로 반복해 20/20 vs 0/20의 비율과 워커 spawn world
  좌표의 상관관계를 raw로 확인한다(run1/run2가 우연히 같은 좌표였던 것이 재현 패턴인지 확인).
  (b) G4-P1 원본 baseline 지표(도착률·도착tick·경로비·정체)가 안정적으로 확보되면, 다음은 AI
  개선 candidate가 없다는 미충족 항목(STATUS 표)을 향해 실제 개선 candidate 설계로 넘어간다.
  `tools/g4_path_fixture_preflight.json`의 나머지 BLOCKED 2항목(`movement_command_trace`·
  `repeatability_gate`)은 이번 lap의 raw trace로 상당 부분 해소됐는지 다음 회차가 재확인한다.
