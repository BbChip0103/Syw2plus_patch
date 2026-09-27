# STATUS — 매 바퀴 갱신하는 기억

이전(lap678~687) 상세 서술은 원문 SHA256 보존 후 압축했다:
`docs/history/20260926_status_lap688_precompaction.md`(원문 152줄, SHA256
`2b98e3b9e0b3757b7607efbf671a391fa89c504699e7d40cd33c5c52f6dab839`). 각 lap의 전체 근거는
`docs/history/laps/20260926_lap67{6,7,8,9}_*.md`·`lap68{0..8}_*.md`에 그대로 있다.

lap688~699 상세(G5 milestone 승인, G2 8인×10000 시도·A/B 판정·사용자 종료 결정)는 원문 SHA256
보존 후 압축했다: `docs/history/20260927_status_lap699_precompaction.md`(원문 130줄, SHA256
`3dae83a4115372fd3ddf019f82cafd65d2be926456a4074f2d5e3c0a73dcd4be`). 각 lap 전체 근거는
`docs/history/laps/20260926_lap68{8,9,90}_*.md`·`20260926_lap69{1,2,3,4}_*.md`·
`20260927_lap69{5,6,7,8,9}_*.md`에 그대로 있다.

lap700~703 상세(G4 W2 post-load ABI/계약 수리, save006 non-vacuous `EXACT_POSTLOAD_EDGE_PASS`
확정, middle 독립검수 CONFIRMED·G4 W2 종결)는 원문 SHA256 보존 후 압축했다:
`docs/history/20260927_status_lap705_precompaction.md`(원문 130줄, SHA256
`84379b51011c4efd38c4c70588b7f0599a04af535734881635e2307b6cbb8003`). 각 lap 전체 근거는
`docs/history/laps/20260927_lap70{0,1,2,3}_*.md`에 그대로 있다.

lap704~707 상세(G4-P1 원본 길찾기 baseline: spawn world 양분 확정, obstacle_row/long_distance_pan
scenario baseline)는 원문 SHA256 보존 후 압축했다: `docs/history/20260927_status_lap709_precompaction.md`
(원문 139줄, SHA256 `2157ada80c321316b7b14808b3017e168593515ae3a9a78a21a3d34ac792c1b6`). 각 lap
전체 근거는 `docs/history/laps/20260927_lap70{4,5,6,7}_work_*.md`에 그대로 있다.

## 지금 상태

**G5는 2026-09-26 21:54 사용자 판단으로 단일플레이 milestone 승인, 최우선 지시 종료**(멀티 동기화는
`UNKNOWN` 메모 유지, 명령당 60B 레코드 최대3회 발행).

**G2는 2026-09-27 03:21 사용자 판단으로 전비10000 트랙 종료, 전비5000(달성 판단 유지)으로 복귀.**
10000 후보(lap691~699, `g2_supply10000_*`)와 근거는 보존만 하고 더 진행하지 않는다.

**G4 W2(post-load AI 유지 계측)는 lap702 non-vacuous `EXACT_POSTLOAD_EDGE_PASS`(save006 slot7,
`_g4_postload_contract` fail-closed 불변식) 달성 후 lap703 middle 독립 검수로 CONFIRMED·종결**
(제품 G4 PASS 아님 — candidate AI 정책 자체가 여전히 없다, `candidate_present=false`). 상세는 위
압축 포인터.

**lap704~707(work) G4-P1 원본 길찾기 baseline:** worker spawn world는 **(93,56)**(짧은 거리
이동 20/20, 재현 확정) 또는 **(10,49)**(0/20, 길찾기 지표에서 제외) 둘 중 하나뿐이다(706).
world (93,56)의 `obstacle_row`(8타일) baseline N=3 PASS(arrival 0.85~0.90, path_ratio_max
2.540); `long_distance_pan`(≥20타일)은 (93,56)에서 카메라 팬 원위치 복귀 6/6 실패로
BLOCKED(707, 상세는 Blockers 절). 상세 `docs/history/laps/20260927_lap70{4,5,6,7}_work_*.md`.

**lap708~709(work) G4 길찾기 개선 후보 v1/v2 — 실패 가설 2/2 도달:** v1(로컬 4방향 nudge
재시도 한도 `0x40C395` 4→8, lap708)과 v2(`FUN_0041AF90` bounding-box 탐색 마진 30→60타일,
lap709, vtable 대상 `0x46b840` 정적 확정) 둘 다 obstacle_row world (93,56) paired에서
`path_ratio_max`/`arrival_rate`가 원본과 완전히 동일하거나 악화됐다(`H1`/`H2` 모두
FALSIFIED). `FUN_0046B840`(실제 그리드 탐색 본체)의 per-call 스텝 예산 상수는 정적 조사만으로는
확정하지 못했다(컴파일러 재적재로 스택 산수 신뢰 구간 이탈, `analysis/memory_maps/
g4_move_order_local_step_retry_20260927.md` §7.2). **2026-09-27 10:45 운영자 판정이 이
FALSIFIED 결과를 전제로 다음 방향(원거리 도착률 지표 전환)을 이미 정해 별도 strategy 판정
요청은 생략한다**(아래 "다음 한 가지" 참고). 상세
`docs/history/laps/20260927_lap70{8,9}_work_g4_*.md`.

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | 제품 미완료 | 1600×1200 원본 구도 외 사용자/제품 승인 |
| G2 | 전비5000 단계 달성(복귀). 8인×10000 트랙 종료(10000 후보 근거는 보존) | 사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 제품 미완료. W1/W2 종결, P1 baseline N=3(lap707), 개선후보 v1/v2 H1/H2 모두 FALSIFIED(lap708~709) | long_distance_pan (93,56) 도구결함 BLOCKED, AI 개선 candidate 채택된 것 없음(제품 비교 불가), 사용자 승인 |
| G5 | **단일플레이 milestone 승인(2026-09-26 21:54 사용자)** | 멀티 동기화 `UNKNOWN`(별도 표시, 최우선 지시 종료) |

## 지금 막힌 것 (Blockers)

**대표 scene world (93,56)에서 `long_distance_pan`(≥20타일) baseline이 도구 결함으로 막혀 있다.**
lap707이 카메라 팬(방향키 hold)으로 20타일 이상 목적지를 만드는 메커니즘 자체는 world (10,49)에서
5/5 성공시켰지만, world (93,56)에서는 팬 원위치 복귀가 6/6 전부 실패한다 — 동일시간 되돌림과
축투영 폐루프 보정(1축) 둘 다 실패, Down/Up 키의 세계좌표 이동 벡터가 이 world에서 평행하지 않은
것으로 관측됐다(2D 오차, 원인 미확정). 2026-09-27 10:45 운영자 판정으로 카메라 팬 대신
**미니맵 우클릭**으로 우회하기로 확정했다(아래 "다음 한 가지" 참고, 되돌림 계산 시도는 중단).

## 검증 상태

lap709(work, 자체 raw 관측·독립 검수 아님): 신규 테스트 7개 PASS(총 1049), `make check`
**1049 passed(837.09s)**(로그
`logs/gates/20260927_lap709_g4_search_margin_v2_make_check.log`) + ruff/compileall/mypy/
`CONTEXT_PASS`/`checks/safety.sh check`(`SAFETY_PASS`) 전부 PASS. 원본 SHA 4회 전부
`cleanup.ok=true`·`source_unchanged=true`·크래시0. 후보 SHA
`ab66669d795a1d89a018aa3e4c32a7d353fe7c03297becdddde55a5dbaf57a40` 4회 전부 `patched_bytes`
재계산과 일치. world (93,56) 매치 표본(unit_type 21/31) 각각 원본·후보 `path_ratio_max`/
`arrival_rate`가 소수점까지 완전 동일 — `H2 FALSIFIED`.

lap708(work, 자체 raw 관측): make check 1042 passed(849.56s), SAFETY_PASS, 신규 테스트 15개,
원본/후보 SHA 전부 불변·일치. 상세는
`docs/history/laps/20260927_lap708_work_g4_move_retry_budget_v1_falsified.md`.

lap703(middle, 독립 검수): G4 W2 `EXACT_POSTLOAD_EDGE_PASS`(save006) CONFIRMED·종결. 상세는 위
압축 포인터(`docs/history/20260927_status_lap705_precompaction.md`).

## 다음 한 가지
**2026-09-27 10:45 운영자 판정(G4 가설 2회 소진 — v1 재시도 한도, v2 탐색 마진 모두 원본과 동일):** obstacle_row(8타일)는 원본도 path_ratio≈1.93·도착 14~18/20으로 개선 여지가 작다. **목표 지표를 원거리 도착률로 전환**(lap707: 33~35타일에서 원본 도착 평균 ≈49%). 다음 work: ① 원거리 명령을 **미니맵 우클릭**으로 발행해 카메라 팬 복귀 문제를 우회(lap707 BLOCKED 해소), world(93,56)에서 원본 N=3, ② 미도착 유닛별 원인 분류(정체 위치·마지막 명령 상태·유닛 간 충돌/대기열 정체 vs 경로 실패)를 raw로 집계, ③ 가장 많은 원인 1개를 v3 가설로 STATUS에 기록(구현은 다음 lap).
**2026-09-27 lap709(work, 자체 기록 — 실패 가설 2/2 소비, 10:45 운영자 판정과 raw로 일치):**
lap708 handoff대로 `FUN_0041AF90` vtable 대상을 정적 확정(전역 싱글턴 경로탐색 엔진
`ds:0xb92cbc`, vtable `0x4e57e0`, 엔트리[1]=`0x46b840` 실제 그리드 탐색 본체)하고, 유일하게
애매함 없이 확정되는 상수인 **bounding-box 마진(30→60타일)**으로 후보 v2를 빌드해 같은
obstacle_row world (93,56) N=3 대 N=3 paired로 측정 — **`H2 FALSIFIED`**: unit_type 21/31
매치 표본 모두 원본·후보 `path_ratio_max`/`arrival_rate`가 소수점까지 완전 동일(장애물이
이미 원본 30타일 마진 안에 있어 마진 확대가 탐색 범위를 바꾸지 못함, 사전에 명시한 반대
가설과 일치). `FUN_0046B840`의 실제 per-call 스텝 예산 상수는 컴파일러 재적재 패턴 때문에
정적으로는 확정하지 못했다(과다 확신 금지, gdb 런타임 확인 필요). 근거
`analysis/memory_maps/g4_move_order_local_step_retry_20260927.md`§7,
`docs/history/laps/20260927_lap709_work_g4_search_margin_budget_v2_falsified.md`. 위
10:45 운영자 판정이 이미 이 결과를 전제로 다음 방향(원거리 도착률 지표 전환·미니맵 우클릭)을
정해 두었으므로, 이 lap은 별도 strategy 판정을 추가 요청하지 않는다 — **다음 work는 위
10:45 지시 ①~③을 그대로 수행**한다.

## 바퀴 기록

- lap709(work, 이 세션): G4 길찾기 개선 후보 v2(`FUN_0041AF90` bounding-box 탐색 마진
  30→60타일, vtable 대상 `0x46b840` 정적 확정) obstacle_row world (93,56) N=3 paired 측정 —
  `H2 FALSIFIED`(path_ratio_max/arrival_rate 완전 불변). make check 1049 passed, SAFETY_PASS,
  신규 테스트 7개. 실패 가설 2/2 도달. 상세
  `docs/history/laps/20260927_lap709_work_g4_search_margin_budget_v2_falsified.md`.
- lap708(work, 이 세션): G4 길찾기 개선 후보 v1(`0x40C395` 로컬 재시도 한도 4→8) obstacle_row
  world (93,56) N=3 paired 측정 — `H1 FALSIFIED`(path_ratio_max 불변, arrival_rate 소폭 하락).
  make check 1042 passed, SAFETY_PASS, 신규 테스트 15개. 상세
  `docs/history/laps/20260927_lap708_work_g4_move_retry_budget_v1_falsified.md`.
- lap704~707(work): world spawn 양분 CONFIRMED, obstacle_row N=3 PASS(2.540)/long_distance_pan
  BLOCKED(707). 상세는 위 압축 포인터(`docs/history/20260927_status_lap709_precompaction.md`)와
  `docs/history/laps/20260927_lap70{4,5,6,7}_work_*.md`.
- lap700~703(work/middle): G4 W2 post-load ABI/계약 수리 → save006 non-vacuous
  `EXACT_POSTLOAD_EDGE_PASS` 최초 raw 달성(lap702) → middle 독립 검수 CONFIRMED·종결(lap703).
  상세는 위 압축 포인터와 각 lap 파일.
- lap691~699(work/middle): G2 8인×10000 트랙 — 전역풀4092 확장 PASS(695)→저장로드 PASS(696)→
  전역열거 도구 수리 PASS(697)→middle 조건부 부분PASS/HOLD(698, 12비트 wire 한계 발견)→
  A/B 판정 자료 보강(699)→**2026-09-27 03:21 사용자 판단으로 트랙 종료, 전비5000 복귀**.
  상세는 `docs/history/20260927_status_lap699_precompaction.md`와 각 lap 파일.

G5의 선택/호출/이동/save-load 부분 runtime 증거와 과거 실패 provenance는 `docs/history/laps/` 및
공유 `temp/Syw2plus_patch/`에 보존한다. G5는 사용자 milestone 승인 완료, 멀티 동기화만 `UNKNOWN`이다.
