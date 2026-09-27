# APPROVALS lap707~711 work tier 정보제공 항목 사전압축 원문 (lap712 세션에서 보존)

- [ ] **2026-09-27 lap711 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님):**
  STATUS lap710 handoff(v3 가설: `TRACE_TIMEOUT_S` 90s→150~180s로 원거리 도착률이 오르는지)를
  그대로 수행. `tools/g4_path_baseline_probe.py`에 `--trace-timeout-s` CLI(기본값 기존 상수 그대로,
  회귀 테스트 1개 추가) 추가 후 world (10,49) `long_distance_pan`을 165s로 fresh N=2 실행.
  **run1은 world (93,56) 재추첨**(기존에 이미 BLOCKED 처리된 카메라-복귀 결함을 raw로 재확인,
  새 결함 아님, `cleanup.ok=true`). **재시도한 run2/run3은 둘 다 world (10,49)로 착지,
  `arrival_rate=0.65`(13/20) 동일**, 미도착 7슬롯 최종좌표가 두 run에서 좌표 단위까지
  완전히 일치(추가 75초가 전혀 효과 없음 — 이미 90s 이내 정상상태 도달), 정체/충돌 0건, 미도착
  거리 3.16~4.47타일로 20기 전원이 단일 목적지 좌표 반경 ~4.5타일 안에 몰려 있다. **v3
  `NOT_FEASIBLE`**(가설 2/2 소진) — 미도착은 타임아웃이 아니라 probe가 20기를 한 좌표로 우클릭시키고
  좁은 반경(3타일)으로 도착을 판정하는 측정 기준 자체의 인공물로 결론. 이 수치는 STATUS/APPROVALS에
  이미 반영된 **2026-09-27 12:05 운영자 판정(G4 길찾기 트랙 종료, 자유대전 AI로 전환)**과 별도
  경로로 도달했으나 일치한다(raw 재확인). 원본 SHA 3회 전부 `source_unchanged=true`, 크래시 0,
  게임 EXE/DLL 미변경(probe 하드웨어만). `make check` **1050 passed(851.98s)**,
  ruff/mypy/`CONTEXT_PASS`/`checks/safety.sh check`(`SAFETY_PASS`) 전부 PASS. 근거
  `../history/laps/20260927_lap711_work_g4_v3_timeout_falsified_destination_crowding.md`.
- [ ] **2026-09-27 lap710 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님):**
  10:45 지시 ① "미니맵 우클릭으로 원거리 명령 발행"을 원본에서 실제로 시험 — HUD 좌하단 다이아몬드형
  위젯(미니맵 후보, 진단 캡처로 시각 확인)과 나침반형 다이얼(이전 lap674 `MINIMAP_CLICK=(235,555)`)
  두 후보 모두 우클릭(9점/7점, world (93,56)·(10,49) 두 spawn) 후 워커 `pending_xy`가 클릭 전과
  동일한 `(0,0)`으로 유지되어 이동 명령 미발행, 좌클릭 후 메인 뷰포트 9점 재캘리브레이션의
  `center_world`도 완전 불변(shift=0.0타일)으로 카메라 점프도 없었다. `Tab`/`m`/`M` 키 토글도 새
  오버레이 없음. **`BLOCKED`**(실패 가설 2/2 + 토글 확인 1회). 대신 world (10,49)의 기존
  `long_distance_pan` N=5(lap707, 재실행 없이 `probe-result.json` raw 재분석)를 baseline으로
  채택 — 그 world가 이전에 "대표 scene 제외"였던 것은 다른 probe(`g5_worker_relative_move_attack_probe`,
  짧은 상대offset) 한정 결함이며 `long_distance_pan` 자체엔 결함이 없음(`ever_move_command_count=20/20`
  5/5)을 raw로 확인. 미도착 51/51(100%) 전부 `stagnation_runs=[]`+정상 `path_ratio`(1.0~1.9)+최종거리
  3.16~5.4타일로, 정체/충돌 사례는 0건 — 지배 원인은 `TRACE_TIMEOUT_S=90s` 측정 타임아웃으로 보인다
  (반증 가능한 v3 가설, STATUS "다음 한 가지" 참고). 게임 EXE/제품 코드 미변경(신규 진단 스크립트
  `docs/history/laps/probes/20260927_lap710_minimap_locate_probe.py`만 추가, `make check` lint/
  typecheck/pytest 대상 밖이라 회귀 없음). 원본 SHA 사전 확인 3회, 사후 재확인은 이 스크립트가
  생략함(비차단 갭, 기록됨). 근거
  `../history/laps/20260927_lap710_work_g4_minimap_blocked_longdist_arrival_timeout_classification.md`.
- [ ] **2026-09-27 lap709 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님):**
  lap708 handoff(§3, `FUN_0041AF90` vtable 대상 특정) 완료. `.text`/`.rdata` raw 파싱으로
  전역 싱글턴 경로탐색 엔진(`ds:0xb92cbc`, 생성자 `FUN_0041AE70(this,200,200)` at `0x424ca6`,
  vtable `0x4e57e0`)의 vtable 두 번째 슬롯 = `0x46b840`(실제 그리드 탐색 본체, open-list
  기반 8방향 확장)을 확정했다. 유일하게 애매함 없이 확정되는 상수인 bounding-box 마진
  (`0x1E`=30타일, 4개 exact byte)을 60타일로 배증한 후보 v2(`patches/pathing/
  g4_search_margin_budget_v2.py`)를 빌드해 `tools/g4_path_baseline_probe.py --variant
  candidate_v2`로 연결했다. obstacle_row world (93,56) 원본 N=3 대 후보 N=3 paired 측정
  결과 **`H2 FALSIFIED`**: 매치되는 `unit_type=21`/`unit_type=31` 표본 둘 다 `path_ratio_max`·
  `arrival_rate`가 원본과 소수점까지 완전 동일했다(사전 명시한 반대 가설 — 장애물이 이미
  원본 30타일 마진 안에 있어 마진 확대가 무의미하다 — 와 일치). `FUN_0046B840`의 실제
  per-call 스텝 예산 상수는 컴파일러 재적재 패턴 때문에 정적으로 확정하지 못했다(과다 확신
  금지, gdb 런타임 확인 필요, §7.2). 원본 SHA 8회 불변, 후보 SHA
  `ab66669d795a1d89a018aa3e4c32a7d353fe7c03297becdddde55a5dbaf57a40` 4회 일치, 크래시 0.
  `make check` 1049 passed(837.09s), ruff/mypy/CONTEXT_PASS/SAFETY_PASS 전부 PASS, 신규
  테스트 7개. 근거 `../history/laps/20260927_lap709_work_g4_search_margin_budget_v2_falsified.md`,
  `../../analysis/memory_maps/g4_move_order_local_step_retry_20260927.md`§7. **실패 가설 2/2
  도달 — 2026-09-27 10:45 운영자 판정이 이 결과를 전제로 이미 다음 방향(원거리 도착률 지표
  전환, 미니맵 우클릭)을 정했으므로 이 lap은 별도 strategy 승격을 요청하지 않는다.**
- [ ] **2026-09-27 lap708 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님):**
  08:55 지시(G4 길찾기 개선 후보 v1 구현) 완료. `Unit+0x290==3`(MOVE) per-tick 핸들러 유일 호출
  경로(`0x48E706→0x40C390→0x40B7E0(mode=4)→0x40B810`)를 정적으로 특정해, 로컬 4방향 nudge
  재시도 최대 횟수(`mode`=4)를 8로 올리는 1바이트 후보(`patches/pathing/g4_move_retry_budget_v1.py`,
  파일 오프셋 `0xC395` `6a04→6a08`)를 빌드하고 `tools/g4_path_baseline_probe.py --variant
  candidate`로 원본/후보를 연결했다. obstacle_row world (93,56) 원본 N=3 대 후보 N=3 paired
  측정 결과 **`H1 FALSIFIED`**: 매치되는 `unit_type=21` 표본에서 `path_ratio_max`가 완전히
  동일(1.9328098099980875)했고 `arrival_rate`는 18/20→17/20으로 소폭 하락했다. 이 v1은
  채택하지 않는다(반증 증거로 파일만 보존). 원본 SHA 10회 불변, 후보 SHA
  `62a100fc65b8b454aa357a9dce8dccbc6e5785dde3c48c50eb6c54250ce5b72a` 5회 일치, 크래시 0.
  `make check` 1042 passed(849.56s), ruff/mypy/CONTEXT_PASS/SAFETY_PASS 전부 PASS, 신규
  테스트 15개. 근거 `../history/laps/20260927_lap708_work_g4_move_retry_budget_v1_falsified.md`,
  `../../analysis/memory_maps/g4_move_order_local_step_retry_20260927.md`. **다음 work가
  §3(`FUN_0041AF90` 실제 탐색 진입점, bounding-box 마진 `0x1E`)을 특정해 v2를 시도한다 —
  실패 가설 1/2 소비.**
- [ ] **2026-09-27 lap707 work tier(Claude Code Sonnet, 정보 제공용 — 새 middle 검수 요청 아님):**
  07:45 지시(대표 scene world (93,56)에서 길찾기 약점 조건 N=3) 부분 완료. `tools/g4_path_baseline_probe.py`에
  `--scenario {long_distance_pan,obstacle_row}` 추가(기본 `auto` 무변경, 회귀로 확인). `obstacle_row`
  (8타일, 본진 footprint 방향)는 world (93,56)에서 N=3 확보 **PASS**(`arrival_rate` 0.85/0.90/0.90,
  `path_ratio_max` 2.540/1.986/1.933, `ever_move_command_count=20/20` 3/3, 정체0). `long_distance_pan`
  (≥20타일, 카메라 팬)은 메커니즘 자체는 world (10,49)에서 N=5 **PASS**했지만 world (93,56)에서는
  팬 원위치 복귀가 6/6 전부 실패(fail-closed `ProbeError`, 크래시·오염 없음) — 동일시간 되돌림과
  축투영 폐루프 보정 2회 모두 실패, Down/Up 키의 세계좌표 이동 벡터가 이 world에서 비평행으로
  관측됨(원인 미확정, 가설 실패 2회 도달로 이번 lap에서 중단). 원본 SHA 17회 전부 불변, cleanup
  전부 ok. `make check` 1034 passed(866.09s) + 무관 flaky 1건(단독 재실행 PASS), SAFETY_PASS.
  **G4 개선 후보 1차 지표로 `path_ratio_max=2.540`(obstacle_row, world (93,56))을 제안.** 근거
  `../history/laps/20260927_lap707_work_g4_path_baseline_scenario_probes.md`.
