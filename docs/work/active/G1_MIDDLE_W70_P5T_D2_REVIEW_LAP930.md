# G1 P5-T D2 work 결과 독립 검수 (lap930)

중간 tier solo 검수. 제품 코드/validator/baseline/raw 변경·마일스톤 승인 없음. 다음 work 한 가지를 STATUS에 갱신한다.

## 검수 입력

- Work history: `docs/history/laps/20261004_lap930_work_g1_p5t_d2_clip_cost.md`
- Raw 재계산: 공유temp `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap930_d2_review/recalculate.py` 및 `recalculation.json` (보고서 SHA256 `ce0191726dc7e79157ea18cb612089bc06df576fb017afac853c6b9c2de47d9d`, 입력 SHA 27개)
- D2 diagnostic/acceptance pair raws: 공유temp `20261004_lap930_{d2_diag,d2_diag_r2,p5t_green,p5t_bprime1,p5t_bprime2,p5t_c3}/`
- 원본 EXE/save SHA와 lane cleanup 증거: history 및 재계산 JSON

## 독립 확인할 주장

1. `clip_prepare` whole와 세 bucket은 같은 QPC frequency/호출 경계를 사용하며 bucket 상호 중첩은 없다. Alloc requested bytes와 fill/mask written bytes를 혼합하지 않는다.
2. 이전 raw에서 각 30-event PT-c sample seq/sim_tick와 `span/29`를 재계산한다. PT-c는 GREEN DOWN/RIGHT 52.552/51.379ms, B′1 53.897/52.379ms, B′2 57.000/50.621ms; 연속2 미달인지 확인한다.
3. 동일 camera[158,101]의 late20 PT-d: effective p50 395960.5, stale p50 74863.5, tinted covered 11524/9569/9314, tinted_clip 0. 하한11439을 유지하고 결함/면책을 임의 추론하지 않는다.
4. C3 raw에서 baseline/candidate 20초 duration, tick ratio 0.99747, p95 delta +11ms, drop0, scene/camera 동일성 확인.
5. old nearest `BLOCKED`와 active Scale2x `PASS`를 구분한다. 화면 결함이나 G1 완료로 승격하지 않는다.

## 판정 범위

현재 결과는 P5-T/G1 HOLD이며 사용자 승인이나 마일스톤 경계가 아니다. 다음 비용/화면 work 1개를 정해 work로 넘긴다. 기존 D1/P5-H/G1 범위, 일정·30개·52ms·PT-d·validator·mirror scope 및 과거 raw를 바꾸지 않는다. 새로운 raw 충돌 또는 milestone 경계가 확인되면 그때 runtime 규칙을 따른다.
