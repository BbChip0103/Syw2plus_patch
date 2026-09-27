# 2026-09-27 | lap 706 | 목표 G4 (G4-P1 원본 길찾기 baseline)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 (실무), STATUS "다음 한 가지"
  (lap705 handoff (a): 동일 하네스를 N≥5로 반복해 `ever_move_command_count`와 워커 spawn world
  좌표의 상관관계를 raw로 확인) 그대로 수행.
- 가설: lap705는 같은 코드·같은 목적지 거리(10타일)로 3회 중 2회(worker world (93,56)) 이동명령
  20/20 도달, 1회(worker world (10,39) 부근 — 실제로는 정확히 (10,49))는 0/20이었다. 가설은
  "지형/스폰 위치 의존"(같은 world에서 반복 시 결과가 같다) vs "지형과 무관한 흔들림"(같은
  world에서도 결과가 다르다)이었다. 코드/도구 변경 없음(`tools/g4_path_baseline_probe.py`
  lap705 상태 그대로 재사용, 수정 0건).
- 예상 PASS / FAIL 조건: STATUS 지시 그대로 — 같은 world에서 반복 시 결과가 같으면 지형 의존
  CONFIRMED(관찰로 기록), 같은 world에서도 결과가 다르면 클릭 타이밍/틱 동기화 쪽 조사로 이동.
- 변경 파일: 없음(도구/제품 코드 0 변경, uncommitted 기존 diff는 이 lap이 만든 것이 아님 —
  `git status`로 재확인). 게임 EXE/DLL 미변경.
- 원본 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(5회 모두 실행 전후 불변,
  `source_unchanged=true`). 환경 `[ESL]Syw2plus/` 소스, 1600x1200x24 Xvfb, `SYW2_SUPPLY_PROBE=1`.
  활성 플레이어: 솔로(비고정 시드) 1인 × 5회. 군대/fixture: 기존 워커(슬롯1198) + owner0 type2
  55기 dense fixture(1198 제외 7x8-1 격자), 원본 20-cap 드래그로 20기 선택. 목적지: 워커 기준
  world (0,-10) 오프셋, 10타일(lap705와 동일 로직, `LONG_DISTANCE_OFFSET_MAGNITUDES=(12,10,8)`
  중 10이 매회 채택).
- 실행 명령(5회, 각 새 runtime-root/artifact-root):
  `PYTHONPATH=. .venv/bin/python tools/g4_path_baseline_probe.py --runtime-root
  local/runtime/g4-lap706-baseline-run{1..5} --artifact-root
  .../temp/Syw2plus_patch/20260927_lap706_g4_path_baseline_repeat/run{1..5}` → 5회 모두 exit0.
  결과 JSON SHA256: run1 `140f5c41126c41fafc51e8d53fdc23b86f825672803e3f32ceb1a7f6d1a6e253`, run2
  `46a56a73be97908b5c823c05e0c399d268ee4a42c4752794c1b9d602c6bc690a`, run3
  `4733795e80178661d70bdc2f92c429377bc85345ed0851431e6f8c42518a8fcf`, run4
  `95aab5eff3a487a621c9ca9a0a8d0caab716b88f8b16582f66e05767b1b1c0c9`, run5
  `af4da14171febae9aa3af3fdcd05079937c20f83387e7ee599fcf71ec2e49c37`
  (경로: `<artifact-root>/probe-result.json`).
  각 run 종료 후 `local/runtime/g4-lap706-baseline-run{N}/*/game` 사본만 삭제(디스크 위생,
  manifest/output/prefix/log 보존).
- 측정값 / 판정: **하네스 자체는 5회 모두 PASS**(선택20/20, `cleanup.ok=true`,
  `source_unchanged=true`, exit0). worker spawn world 좌표별로 완전히 분리된 raw 결과:

  | run | worker world (x,y) | ever_move_command_count | arrival_rate | 비고 |
  |---|---|---|---|---|
  | lap705 run1 | (93,56)† | 20/20 | 0.90 | destination (93,46) |
  | lap705 run2 | (93,56)† | 20/20 | 0.85 | destination (93,46) |
  | lap705 run3 | (10,49)† | 0/20 | 0.05 | destination (10,39) |
  | lap706 run1 | (93,56) | 20/20 | 0.95 | destination (93,46) |
  | lap706 run2 | (10,49) | 0/20 | 0.05 | destination (10,39) |
  | lap706 run3 | (93,56) | 20/20 | 0.70 | destination (93,46) |
  | lap706 run4 | (93,56) | 20/20 | 0.70 | destination (93,46)(run3와 수치 완전 동일) |
  | lap706 run5 | (10,49) | 0/20 | 0.05 | destination (10,39) |

  †lap705 원문은 world를 "(93,46)"·"(10,39)"로 워커 절대좌표처럼 서술했으나 실제로는 그 값은
  **목적지**(worker+오프셋)였다 — 이번 lap이 각 run의 `result["worker"]["x"/"y"]`(워커 자체
  좌표)를 직접 재확인해 worker=(93,56)/(10,49)임을 특정했다(destination = worker + (0,-10)이므로
  (93,46)/(10,39)와 정확히 일치, 오기 아님 — 표기만 명확화).

  **지형 의존 CONFIRMED.** 이 unseeded solo 로비는 사실상 두 개의 관측된 spawn world만
  보였다: world (93,56)에서는 **5/5회 모두** `ever_move_command_count=20/20`(100%), world
  (10,49)에서는 **3/3회 모두** `ever_move_command_count=0/20`(100%, 단 1기만 우연 근접
  `arrival_rate=0.05`). 같은 world에서는 결과가 완벽히 재현되고(run3/run4는 수치까지 동일),
  다른 world 사이에서는 완전히 갈린다 — "클릭 타이밍/틱 동기화 흔들림" 가설은 반증되고
  "지형/스폰 위치 의존" 가설이 raw로 확정됐다. world (10,49) 목적지 (10,39) 근방에 A*가 통과할
  수 없는 장애물/지형이 있어 20기 중 단 한 기도 이동 명령을 발행하지 못하는 것으로 관측된다
  (원인이 되는 정확한 타일 장애물 종류는 이번 lap에서 특정하지 않음 — 관찰 기록 범위).
- 회귀 / 검증: `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_g4_path_baseline_probe.py`
  → `5 passed`(도구 무변경, 기존 회귀 재확인). `checks/safety.sh check` → `SAFETY_PASS`. 전체
  `make check`는 이번 lap에서 코드를 변경하지 않아 재실행하지 않음(직전 lap705가 동일 파일
  상태로 `1032 passed` 확인함 — 이번 lap은 그 실행 증거를 반복 검증한 것이 아니라 신규 raw
  runtime 관측을 추가한 것). 남은 위험: world (10,49) 실패의 정확한 원인(구체적 장애물
  타일/충돌 그리드)은 미귀속. 관측된 spawn world가 2개뿐이라 "unseeded"가 실제로 완전
  랜덤인지, 좁은 후보 집합에서 도는지도 미확인. 독립 검수/사용자 승인 없음(work tier 자체
  raw 관측 보고, 미들 검수 요청 대상 아님 — STATUS 지시가 요구한 반복 측정 완료 보고).
- 다음 한 가지: `analysis/g4_path_fixture_preflight.json`의 BLOCKED 항목
  (`movement_command_trace`·`repeatability_gate`)을 이 raw로 재판정한다 — 이동 명령
  trace/반복성 자체는 확보됐으나(같은 world면 100% 재현), `deterministic_scene_fixture`가
  여전히 BLOCKED(맵/시드 미고정)이므로 "원본 길찾기 baseline"을 단일 대표 수치로 보고하려면
  world (93,56) 계열(성공)과 (10,49) 계열(장애물 실패)을 분리 보고해야 한다. STATUS 표의 G4
  미충족 항목("AI 개선 candidate 없음")을 향한 다음 단계는 이 두 world 중 하나(예: (93,56),
  안정적으로 이동이 성공하는 쪽)를 baseline 대표 scene으로 채택해 개선 candidate 설계 착수
  여부를 strategy/middle이 정하는 것이다.
