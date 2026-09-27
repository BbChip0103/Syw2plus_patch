# 2026-09-27 | lap 707 | 목표 G4 (G4-P1 원본 길찾기 baseline, 약점 조건)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 (실무, 세션 자체 확인 "이번 세션은
  일반 작업자다"). STATUS "다음 한 가지"(2026-09-27 07:45 운영자 판정, strategy 대행) 수행:
  대표 baseline scene worker world **(93,56)**에서 길찾기 약점이 드러나는 조건(거리 20타일
  이상, 장애물/좁은 통로 목적지 1개)으로 원본 baseline N=3을 확보한다.
- 가설: (a) 카메라를 팬(방향키 hold)하면 단일축 클릭으로는 닿지 않는 20타일 이상 거리의 목적지를
  만들 수 있다(lap704/705가 확인한 클릭 안전박스 한계는 "카메라가 고정"이라는 전제에서만 성립).
  (b) `dense_fixture_requests`가 dy=-4 대신 -3부터 시작해 "본진 footprint와 겹치지 않게" 격자를
  민 것이 사실이면, 그 라인(dy=-8, worker 기준 -Y쪽)을 지나는 목적지는 경로가 그 footprint를
  가로지르거나 돌아가야 한다.
- 예상 PASS / FAIL 조건: 두 조건 각각 world (93,56)에서 fresh N=3, `source_unchanged=true`,
  `cleanup.ok=true`, exit0. 실패하면 원인을 원본 raw로 좁혀 기록한다(추측 금지).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): `tools/g4_path_baseline_probe.py`
  (`--scenario {auto,long_distance_pan,obstacle_row}` 추가, 기존 기본 `auto`는 무변경 — 회귀
  테스트로 확인), `tests/test_g4_path_baseline_probe.py`(신규 순수 로직 테스트 4개: `_screen_to_world`,
  `pan_candidate_ok` 경계 3종, `OBSTACLE_ROW_OFFSET_MAGNITUDE` 하한). uncommitted,
  `LOOP_ALLOW_COMMITS=0`. 게임 EXE/DLL 미변경.
- 설계: `long_distance_pan`은 worker만 선택된 캘리브레이션 단계(진짜 20기 선택 전, 우클릭 캘리브레이션
  포인트가 아직 테스트 대상 유닛에 영향을 못 주는 유일한 구간)에서 방향키를 hold해 카메라를 이동시키고
  9점 캘리브레이션을 재샘플링해 화면 중심이 가리키는 world 좌표와 원래 worker 위치 간 거리를 확인,
  20타일 이상이면 채택 → 원위치로 되감기 → (원본 위치에서) 실제 55기 fixture 배치·20기 드래그 선택 →
  동일 hold를 재생해 같은 팬 상태로 복귀 → 목적지 클릭. 실제 테스트 유닛에는 캘리브레이션 우클릭이
  전혀 닿지 않도록 순서를 지켰다(오염 없음, 코드 주석에 근거 명시). `obstacle_row`는 카메라를 건드리지
  않고 기존 안전박스 내에서 `worker_y - 8`(본진 footprint 추정 방향, 실패 시 `worker_y + 8`로 폴백)을
  목적지로 고른다.
- 원본 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(전 실행 실행 전후 불변,
  `source_unchanged=true` 전부). 환경 `[ESL]Syw2plus/` 소스, 1600x1200x24 Xvfb, `SYW2_SUPPLY_PROBE=1`.
  활성 플레이어: 솔로(비고정 시드) 1인 × 17회(long_distance_pan 11회 + obstacle_row 6회). 군대/fixture:
  기존 워커(슬롯1198) + owner0 type2 55기 dense fixture, 원본 20-cap 드래그로 20기 선택.
- 실행 명령(대표, 각 새 runtime-root/artifact-root): `PYTHONPATH=. .venv/bin/python
  tools/g4_path_baseline_probe.py --scenario {long_distance_pan|obstacle_row} --runtime-root
  local/runtime/g4-lap707-<scenario>-run<N> --artifact-root
  .../temp/Syw2plus_patch/20260927_lap707_g4_path_baseline_scenarios/<scenario>-run<N>`.
  결과 JSON SHA256(대표): longdist-run1 `135421d7…303dc0`, run9 `ce6c2e6f…5abae`, obstacle-run1
  `c656a86b…3e1f2`, obstacle-run4 `0c851e68…4307e7`(경로: `<artifact-root>/probe-result.json`, 전체
  17개 해시는 이 lap 세션 로그에 보존). 로그
  `logs/gates/20260927_lap707_g4_path_baseline_scenarios_make_check.log`.
- **관측된 spawn world는 이번 17회를 포함해 누적 25회(lap705~707) 전부 (93,56) 또는 (10,49) 둘
  중 하나뿐이었다** — "비고정 시드"가 실제로는 극소수 후보 집합을 순환하는 것으로 보인다(원인 미확인,
  관찰 기록). world 배분: 이번 lap 17회 중 (93,56) 9회, (10,49) 8회.

## 측정값 / 판정

**obstacle_row @ world (93,56) — N=3 확보, PASS(하네스)**: obstacle-run1/4/6 전부
`PATH_TRACE_COMPLETE`, `cleanup.ok=true`, `source_unchanged=true`, 목적지 `(93,48)`(dy=-8, 거리
8타일). `ever_move_command_count=20/20`(3/3), `arrival_rate` 0.85/0.90/0.90(중앙 0.90),
`arrival_tick_median` 303/325.5/310, `path_ratio_median` 1.065/1.071/1.047(중앙 ~1.06),
**`path_ratio_max` 2.540/1.986/1.933**(run1이 가장 나쁨), `stagnating_slot_count=0`(3/3). 대조군
world (10,49)에서 같은 목적지 방향(dy=-8, `(10,41)`)은 obstacle-run2/3/5 전부
`ever_move_command_count=0/20`, `arrival_rate=0.05` — lap706이 다른 목적지(`(10,39)`, dy=-10)로
확인한 "이 world는 -Y쪽 이동 명령 자체가 나가지 않는다"를 **독립된 목적지로 재확인**(world (10,49)는
운영자 판정대로 baseline 제외 대상이며 이 lap은 그 제외 판정을 흔들지 않는다).

**long_distance_pan — world (10,49)에서 N=5 확보(비대표 world), world (93,56)에서는 도구 결함으로
전부 BLOCKED**: 메커니즘 자체(팬→20타일 이상 목적지 계산→클릭)는 world (10,49)에서 5/5 성공
(run1/3/4/8/9, 거리 33.19~34.76타일, `ever_move_command_count=20/20` 전부, `arrival_rate`
0.35~0.65(중앙 0.45), `path_ratio_median` 1.097~1.259, `path_ratio_max` 최대 1.915, 정체0). world
(93,56)에서는 **팬 원위치 복귀가 6/6(run2/5/6/7/10/11) 전부 실패**했다 — 정방향(Down, 1200ms)은
매번 동일하게 `(93,56)→(98,93)`(37.587타일)로 재현됐지만, 역방향(Up, 1200ms)이 같은 시간만큼
되감아도 원위치로 돌아오지 않고 미탐사 fog-of-war 화면(캡처
`.../longdist-run7/after-fixture.png` 참고, 화면 대부분 검은 미탐사 영역)에 남아 20기 선택
드래그가 0을 선택했다(fail-closed로 `ProbeError` → `status=FAIL`, 크래시·오염 없음). 1차 수정
(동일 시간 역방향 hold)과 2차 수정(순방향 축에 투영한 폐루프 보정, `sample_calibration`
재검증+보정 hold, `CAMERA_RETURN_MAX_CORRECTIONS=3`) 모두 이 world에서 실패: 보정 시도의
`signed_along_forward_tiles`는 12.1→2.9→-0.3으로 축 방향 오차는 줄었지만 `drift_tiles`(유클리드
거리)는 21.2→24.6→26.8로 **오히려 커졌다** — 즉 Down/Up 키의 세계좌표 이동 벡터가 이 world에서
평행하지 않다(대각선 성분이 다르다), 1축 보정으로는 못 고친다. 가설 실패 2회(동일시간 되감기,
축투영 폐루프 보정) 도달 — 이번 lap에서는 더 추적하지 않는다(구현 우선 반복 한도 준수).

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

`PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_g4_path_baseline_probe.py` → **8 passed**
(기존 4 + 신규 4). `make check` **1034 passed(866.09s)** + 격리 재실행으로 확인한 flaky 1건
(`test_g1_presentation_trace.py::test_native_serializer_preserves_lap136_shape_and_fail_closed_capacity`,
`wineboot -u`가 병렬 부하에서 30초 타임아웃 — 단독 재실행 시 10.18s PASS, 이 lap의 변경과 무관한
Wine 부팅 경합; 원인 파일은 이 lap이 건드리지 않음), ruff/compileall/mypy(Makefile 지정 10개
파일)/`CONTEXT_PASS`/`checks/safety.sh check`(`SAFETY_PASS`) 전부 PASS. 원본 SHA 17회 전부 불변,
cleanup 전부 ok, 크래시 0. 각 run 종료 후 `local/runtime/g4-lap707-*-run*/*/game` 사본 삭제(디스크
위생, manifest/output/prefix/log 보존).

**남은 위험**: (1) `long_distance_pan`이 world (93,56)에서 막혀 있어 그 world의 "장거리(≥20타일)"
baseline이 아직 없다(obstacle_row만 확보). (2) 카메라 팬의 세계좌표 이동 벡터가 world마다(혹은
방향마다) 다를 수 있다는 것은 이번 lap의 부산물 관찰이며 원인(맵 경계/가속/비선형 스크롤)은
미확정. (3) "비고정 시드"가 사실상 2개 world만 순환하는 관찰은 25회 누적이라 우연이 아닐 가능성이
크지만 세 번째 world가 존재하는지는 미확인. 독립 검수/사용자 승인 없음(work tier 자체 raw 관측
보고, STATUS 07:45 지시가 요구한 baseline N=3 확보 중 obstacle 조건만 완료).

## 다음 한 가지

(a) `long_distance_pan`을 world (93,56)에서 살리려면 1축 보정이 아니라 실제 2D 오차(반환 좌표 -
worker 시작 좌표의 x/y 각 성분)를 독립적으로 줄이는 폐루프가 필요하다 — Down/Up 각각의 세계좌표
이동 벡터를 이 world에서 먼저 따로 측정(왕복 대신 각 키 1회 hold 후 캘리브레이션)한 뒤 역행렬로
정확한 되돌림 hold 시간을 계산하는 방식으로 다시 시도할 것. (b) 그래도 막히면 카메라 팬을 포기하고
미니맵 우클릭(이미 `MINIMAP_CLICK` 상수 존재, 좌표→world 매핑은 미검증)으로 즉시 이동 명령을 발행하는
대체 경로를 새 가설로 검증. (c) `path_ratio_max`(obstacle_row, world (93,56), 최댓값 2.540,
run1)를 G4 개선 후보의 1차 목표 지표로 STATUS에 채택 — 20기 중 최소 1기는 8타일 거리의 단순
우회에서도 직선거리의 2.5배를 걷는다.
