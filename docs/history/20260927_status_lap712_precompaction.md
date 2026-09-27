# STATUS lap704~711 상세 사전압축 원문 (lap712 세션에서 보존)

## 지금 상태 (lap704~711 서술 원문)

**lap704~707(work) G4-P1 원본 길찾기 baseline:** worker spawn world는 **(93,56)**(짧은 거리
이동 20/20, 재현 확정) 또는 **(10,49)**(0/20, 길찾기 지표에서 제외) 둘 중 하나뿐이다(706).
world (93,56)의 `obstacle_row`(8타일) baseline N=3 PASS(arrival 0.85~0.90, path_ratio_max
2.540); `long_distance_pan`(≥20타일)은 (93,56)에서 카메라 팬 원위치 복귀 6/6 실패로
BLOCKED(707, 상세는 Blockers 절). 상세 `docs/history/laps/20260927_lap70{4,5,6,7}_work_*.md`.

**lap708~709(work) G4 길찾기 개선 후보 v1/v2 — 실패 가설 2/2 도달:** v1(로컬 4방향 nudge
재시도 한도 `0x40C395` 4→8, lap708)과 v2(`FUN_0041AF90` bounding-box 탐색 마진 30→60타일,
lap709, vtable 대상 `0x46b840` 정적 확정) 둘 다 obstacle_row world (93,56) paired에서
`path_ratio_max`/`arrival_rate`가 원본과 완전히 동일하거나 악화됐다(`H1`/`H2` 모두 FALSIFIED).
상세 `docs/history/laps/20260927_lap70{8,9}_work_g4_*.md`.

**lap711(work) v3 가설(타임아웃) — `NOT_FEASIBLE`, G4 길찾기 트랙 종료:** world (10,49)
`long_distance_pan`을 `TRACE_TIMEOUT_S` 90s→165s로 fresh N=2 재실행 — `arrival_rate=0.65`(13/20)
불변, 미도착 7슬롯의 최종좌표가 두 run에서 좌표 단위까지 완전히 동일(추가 75초가 단 1틱도 더
움직이지 못함 = 이미 정상상태 도달). 20기 전원이 단일 목적지 좌표 반경 ~4.5타일 안에 몰려 있고
미도착 7기는 그 군집의 바깥쪽(`ARRIVAL_RADIUS_TILES=3.0` 밖 3.16~4.47타일)일 뿐 — 정체/충돌 0건.
**측정 인공물(단일 좌표+좁은 반경 판정)로 결론, 원본 길찾기 결함 미확인.** 12:05 운영자 판정과
합쳐 G4 길찾기 후보 트랙은 닫는다(보존만). 상세
`docs/history/laps/20260927_lap711_work_g4_v3_timeout_falsified_destination_crowding.md`.

## 검증 상태 (lap711/709/703 원문)

lap711(work, 자체 raw 관측): `make check` **1050 passed(851.98s)**(로그
`logs/gates/20260927_lap711_g4_v3_timeout_make_check_final.log`) + ruff/compileall/mypy/
`CONTEXT_PASS`/`checks/safety.sh check`(`SAFETY_PASS`) 전부 PASS. 신규 회귀 테스트 1개(CLI
`--trace-timeout-s` 기본값/override). 원본 SHA 3회 전부 `source_unchanged=true`, 크래시 0(run1은
기존 world (93,56) 카메라-복귀 결함으로 `ProbeError`, `cleanup.ok=true`로 정상 정리). 후보 없음
(변경은 probe 하드웨어뿐, 게임 EXE 불변).

lap709(work, 자체 raw 관측): `make check` 1049 passed(837.09s) + SAFETY_PASS. world (93,56)
`H2 FALSIFIED`(후보 SHA `ab66669d…`, path_ratio_max/arrival_rate 원본과 완전 동일).

lap703(middle, 독립 검수): G4 W2 `EXACT_POSTLOAD_EDGE_PASS`(save006) CONFIRMED·종결. 상세는 위
압축 포인터(`docs/history/20260927_status_lap705_precompaction.md`).

## 바퀴 기록 (lap711 및 lap691~710 요약 원문)

- lap711(work, 이 세션): STATUS의 v3 가설(타임아웃) 검증 지시를 그대로 수행 —
  `tools/g4_path_baseline_probe.py`에 `--trace-timeout-s` CLI 추가(기본값 불변) 후 world (10,49)
  `long_distance_pan` N=2 fresh 165s 실행: `arrival_rate=0.65`(13/20) 불변, 미도착 7슬롯 최종좌표가
  두 run에서 완전 동일(추가 75초 무효과), 정체/충돌 0건, 20기가 단일 목적지 반경 ~4.5타일에 군집.
  **v3 `NOT_FEASIBLE`**(가설 2/2 소진) — 원인은 타임아웃이 아니라 probe의 단일좌표+3타일 반경 판정
  기준. run1은 world (93,56) 재추첨 — 기존 카메라-복귀 결함 raw 재확인(새 결함 아님). 12:05
  운영자의 G4 트랙 종료 판정과 수치가 일치, 제품 코드 미변경. 상세
  `docs/history/laps/20260927_lap711_work_g4_v3_timeout_falsified_destination_crowding.md`.
- lap691~710(work/middle) 요약: G2 8인×10000 트랙 종료(691~699) → G4 W2 `EXACT_POSTLOAD_EDGE_PASS`
  확정·종결(700~703) → G4-P1 baseline·world 양분(704~707) → 개선후보 v1/v2 FALSIFIED(708~709) →
  미니맵 우회 BLOCKED·v3 가설 수립(710). 상세는 `docs/history/20260927_status_lap699_precompaction.md`,
  `docs/history/20260927_status_lap705_precompaction.md`,
  `docs/history/20260927_status_lap709_precompaction.md`,
  `docs/history/20260927_status_lap710_precompaction.md`와 각
  `docs/history/laps/20260927_lap{691..710}_*.md`.
