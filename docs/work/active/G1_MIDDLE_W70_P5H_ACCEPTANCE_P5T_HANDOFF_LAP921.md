# G1 P5-H 부분수용 → P5-T work 인계 — lap921 middle

- 판정: lap920 source-matched GREEN/B′연속2/C3·H2/PH/V1/V2계열/HUD **PASS(partial)**, G1 HOLD.
- 근거: `docs/history/laps/20261004_lap921_middle_g1_p5h_raw_visual_review_pass_partial.md` 및 공유 temp `20261004_lap921_middle_review/recalculation.json`. 보호원본/fixture/build48×6/DLL/raw/snapshot30 SHA MATCH, V1 6713위반0, V2/s/q30tag PASS, C ratio0.9975020002/0.9999823006/0.9999958031·p95Δ13/10/11ms. 입력효과 HOLD·전체PS3 coverage0.8255167~0.8333625는 유지한다.
- lap918 gate 누락과 B′/C 미충족은 lap919 수리+lap920 실행+이번 독립검수로 해소했다. 과거 C2 FAIL은 보존하며 원인 확정/환경 이상치 제외를 주장하지 않는다. 기존 H2 pack 실행 부분수용도 보존한다.
- 실제 API model/effort 메타데이터 미노출, 지정 중간 tier solo. 구현/새runtime/commit0. 다음 작업은 이미 FEASIBLE인 승인된 work 범위이며 재계획 회차로 되돌리지 않는다.

## 다음 work 한 가지

`docs/work/active/G1_STRATEGY_W70_D1R_PRESENT_BINDING_P5_ORDER_LAP911.md` **§5 P5-T**를 그대로 구현한다.

1. `0x00466EA0` rle_tinted·`0x00466540` rle_tinted_clip의 기존 주소/원본 근거와 old-byte pin을 좁게 확인한다. 기존 A/B sentinel 재호출·identity frame·Scale2x 경로와 6인자 wrapper를 사용하고 LUT 포인터+내용digest를 자산/cache key에 넣는다. 원본 호출·격리·정확한 pin/rollback·비중첩을 지킨다. 게임/source 수정은 work tier 단일 writer만 한다.
2. 단위 RED→최소구현→fresh GREEN→B′2→C3 완주. PH-a/b/d·V1/V2/V2s/V2q/Scale2x·snapshot/state/input schedule·30present·C20초/ratio≥0.95/p95Δ≤16ms를 보존한다. 성능 gate의 FAIL/INVALID/누락은 pair HOLD로 유지한다. 기준·validator 완화와 기존 raw/golden 수정은 하지 않는다.
3. 이번 current coverage와 함께 lap911§5의 coverage/stale 개선을 기록한다. tinted writer 호출·covered 수가 늘지 않으면 원인 추적→명확한 구현 수리→재실행한다. source-matched 실제실행이 필요하며 문서/기존exit0은 대체 증거가 아니다. 실패를 숨기지 않고 한계·원인·수리를 기록한다.
4. 기존 입력효과 HOLD(선택대상/미니맵복구/생산)와 GDI/D-2/두번째장면/최종입력/HD90%는 남은 제품 기준이다. PH-a/b PASS나 P5-T 부분 성공만으로 G1 마감/사용자제출로 넘기지 않는다. census 재실행이 필요할 때에만 lap913 계측결함2건을 먼저 수리한다.
5. 기록/handoff 먼저→lint/typecheck→전체Fast 완주→새 middle 독립검수. 설명되지 않는 실패/실제근거 충돌/최종 사용자 경계만 내부 승격한다. 구현 결함은 work가 수리하며 중간 tier에게 구현을 넘기지 않는다.

P5-H→P5-T는 마일스톤 마감이 아니다. 일반 로컬 작업 재허가 질문 없음. G2·G5 종료/G3 중단/G4 보류·개인세션 비접촉·커밋/게시/자동deploy 금지를 유지한다.
