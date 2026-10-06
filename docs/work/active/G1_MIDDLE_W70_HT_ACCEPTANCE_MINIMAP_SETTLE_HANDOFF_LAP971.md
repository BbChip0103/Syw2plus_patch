# G1 middle lap971 — lap969 H-T 수용 · 다음 work = minimap 관측 settle 하네스 수리(H-M)

- 작성: Claude Code `claude-opus-5-5`, high, Fast OFF / middle(중간계획·독립 검수). 게임/source/실행/commit 0.
- 입력(읽기 전용): 공유 temp `20261005_lap969_work_tooltip_bltfast/{r1,r2}`, 비교 기준 `20261005_lap966_work_unclipped_bind/{r1,r2}`.
- 산출(공유 temp `20261005_lap971_middle_review/`, 제품·lap969 분석 helper import 없음): `recalc_lap971.py` SHA256 `9e793cb53b8f67753c3f105d770c7eed75238c809caae95dd1cab70660a862a8` → `recalc_lap971.json` `a24ad448f0447f1cfd96c80c097e50b87326e7a2b88cca30ad2d5d703ad5dfc6`.

## 1. 독립 재계산 (lap969 주장 대비 불일치 0)

| 항목 | lap966 r1 | lap969 r1 | lap969 r2 |
|---|---|---|---|
| 덤프 / steady(서수≥300) | 51 / 39 | 51 / 39 | 51 / 39 |
| steady 교집합 stale | 7,181 | **3,689** | **3,689** |
| HUD 상자 x618~718·y500~539 | 3,492 | **0** | **0** |
| 유닛 덩어리 x681~723·y215~254 | 961 | 961 | 961 |
| 선택 HP 바 x401~494·y153~159 | 423 | 423 | 423 |
| 가장자리 x≥760·y<480(로고+시계) | 813 | 813 | 813 |
| 그 밖 | 1,492 | 1,492 | 1,492 |
| steady stale mean | 7,461 | 3,763 | 3,975 |
| PS3 present / p50 / p95(nearest-rank) | 890 / 6 / 10ms | 899 / 5 / 9ms | 891 / 5 / 10ms |
| cov p50 (covered−stale)/480,000 | 97.78% | 98.51% | 98.49% |
| overlay calls / pixels / rejects | — | 794 / 2,772,648 / 940 | 793 / 2,769,156 / 903 |
| 안전 최대(clip mismatch·viewport mutation/restore·palette·outside diff·cache verify·identity key mismatch) | 0 | 0 | 0 |
| V1(scale2x)/V2/V2q / input effect | PASS / PASS / PASS / PASS | 같음 | 같음 |
| V2s / minimap parity / pair | FAIL / HOLD / HOLD | FAIL / HOLD / HOLD | FAIL / HOLD / HOLD |

- lap969 r1·r2 교집합 픽셀 완전 동일. lap966 대비 제거 3,492 = **전부 HUD 상자 안**, 새 stale 0px. 파일 SHA(mask `8a71fd86…cd4c`/`64ca4744…2fb2`, trace `bf319206…3b27`/`eb4e3fb0…7892`, pair `6e942831…d589`/`0cb56531…f90e`)는 lap969 기록 prefix와 일치. source SHA `g1_overlay_blt.h` `b5cc2149…482d`·`g1_mirror2x.c` `75eeddeb…2d13`·`direct_draw_trace.c` `59fc1481…9bbe`·`tests/test_g1_overlay_blt.py` `dd61cea8…e2fe`도 일치(uncommitted 그대로).

## 2. 판정 — H-T PASS(partial) 수용

- 사전등록 T-1(상자 ≤1,750 → 0)·T-2(교집합 ≤5,450 → 3,689)·T-3(present≥854, p95≤28ms, 안전0, V1/V2/V2q PASS) 충족, 반증 조건(계수 0 / 상자≥3,000 / 안전>0) 해당 없음. 호출당 3,492px = 상자 전체라 기전도 맞다. 결정적(r1=r2).
- T-3의 "minimap effect PASS"는 effect=PASS로 충족, `same_unit_before_after` HOLD는 §3대로 비제품 관측 경쟁이다.
- 구현 검토(읽기만): gate는 비primary·비패널 source·colorkey·src rect·≤320×128·800+×600 대상·화면 안으로 좁다. 한계 1개 기록: 바뀐 픽셀만 Scale2x 블록을 다시 쓰므로, 상자 경계에 붙은 **바뀌지 않은** 픽셀의 2×2 블록은 옛 이웃 기준으로 남을 수 있다. V1 scale2x gate PASS·outside diff 0이라 현 validator 범위 안이며 지금 수리 대상은 아니다. 다른 장면의 colorkey BltFast 형태 evidence는 없다(두 번째 장면 미검증 그대로).
- 사용자 마일스톤 승인 아님. V2s raw production 2,780/2,784 → pair HOLD는 APPROVALS 사용자 판단 큐 그대로.

## 3. minimap HOLD 원인 확정 — 첫 변화 샘플에서 폴링이 멈춤

- 4개 pair(lap966 r1·r2, lap969 r1·r2) × 2 lane의 minimap action raw: `pending_xy` 목표 좌표(5767258/5767259/5832794/5963864)와 camera는 8개 관측 모두 같다.
- HOLD 3회는 전부 baseline lane이 **samples=1, elapsed 0.0s**에서 끝났고 그 값이 command=1·pending 16777219(명령 소비 전 중간 상태)다. PASS 관측 5개는 samples=2, 0.16s에서 command=3·pending 16777217(소비 후)이다.
- 원인: `tools/g1_saved_scene_probe.py` minimap 블록의 `_poll_observation(..., lambda item: minimap_changed(...))`는 "선택 유닛 전원의 pending_xy 또는 pending_command가 바뀜"이 처음 참인 샘플을 `unit_after`로 쓴다. 중간 상태도 이 조건을 만족하므로, 우클릭 직후 첫 읽기가 소비 전 tick에 걸리면 그 lane만 중간 상태를 기록한다. 제품(mirror) 경로와 무관하며 원본 lane에서도 생긴다.

## 4. 다음 work 가설 H-M (Sonnet work 1 lap, FEASIBLE)

- 변경(하네스만, 제품 source·validator·비교식 불변): minimap 우클릭 대기와 fallback 대기의 종료 조건에 **명령 소비(settle)**를 더한다. 예: 순수 함수 `_minimap_command_settled(prior_units, units)` = `_minimap_command_effect(...)["all_selected_changed"]` 이고 선택 유닛 전원이 `OBSERVED`이며 각 유닛 `command != prior command`. camera 변화 경로는 기존대로 둔다. timeout 3.0s·`right_pass`/`minimap_result` 판정식·`_compare_minimap_diagnostic_parity`(exact 비교)는 바꾸지 않는다. timeout이면 기존처럼 wait status UNKNOWN을 기록한다(숨기지 않음).
- 회귀 테스트(먼저 작성): 중간 상태(command=1·pending 16777219·xy 변경) → settled False, 소비 상태(command=3) → True, 미변화 → False, 한 유닛만 소비 → False. 기존 `test_minimap_effect_requires_valid_selected_unit_witnesses` 유지.
- 실행: lap969와 같은 명령의 fresh save006 scale2x pair 2회(`--hd-source scale2x --stale-mask 6-12,30-34,300-301,585-620,880`). 끝나면 `game` 사본만 정리.
- PASS(사전등록): M-1 두 run 모두 `minimap_diagnostic_parity` PASS이고 4개 lane `unit_after`가 소비 상태(command≠1). M-2 lap969 수치 재현: 교집합 3,689(±0)·HUD 상자 0·안전 0·present≥854·p95≤28ms·V1/V2/V2q/input PASS. pair는 V2s raw로 계속 HOLD일 수 있으며 그것은 M 판정과 별개로 기록한다.
- FAIL/반증: (i) 두 lane 모두 소비 상태인데 `unit_after`가 다르다 → 실제 parity 차이이므로 하네스 수리 중단·ESCALATE_SOL. (ii) 어느 lane이든 wait UNKNOWN(3s 안에 소비 안 됨) → 소비 정의 재검토, 기준 완화 금지. (iii) M-2 회귀(교집합 증가·안전>0) → H-T 재검수.
- 위험: 소비 뒤 유닛 이동으로 x,y가 lane 간 다른 시점에 바뀔 수 있다. 현재 0.16s 관측에서는 x,y 불변이었다. 재현되면 (i)로 기록하고 x,y 처리 방안은 middle이 정한다.

## 5. 그 다음 후보 (H-M 검수 뒤 middle이 정의)

- (b) 유닛 덩어리 x681~723·y215~254 961px(lap968 분해: x700~760 구간의 548px 포함), (c) 선택 HP 바 x401~494·y153~159 423px. P6 로고 2,102는 명시 잔여 유지.
- strategy 재호출 조건 추가 없음. H-M은 하네스 lap이지만 실제 fresh 실행 증거를 늘리므로 문서만 회차 연속 제한(③)에 걸리지 않는다.
