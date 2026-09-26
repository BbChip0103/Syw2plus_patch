# G4 seed7 30초 생산 repeatability (2026-09-16)

## 결과

두 번째 고정 scenario로 `_custom_game_chain_inject_seed7`을 선택해 독립 private runtime
두 개에서 각각 30초/15 sample을 수집했다.

- 양쪽 모두 tick summary `13→946`, unit count `4→7`, 최소 진영 거리 81.
- AI(owner 1)는 자원 `7500/7500 → 5950/5950`, reserved `0→10`.
- 관측 unit count sequence는 양쪽 모두 `4,4,4,4,5,5,5,5,5,6,6,6,7,7,7`.
- AI player count/used는 `2/20 → 3/30`.
- HP 감소와 slot 소멸은 30초 구간에서 0.

전체 series에서 세 sample의 생산 progress만 1 차이였다. 그 sample tick도 한쪽이 1 낮았으므로
wall-clock 2초 sampling의 양자화 차이다. comparator는 다른 필드를 모두 exact 비교하고
`progress≤1`, summary tick `≤1`만 허용한다.

- 판정: `FIXED_FIXTURE_REPEATABLE_TOLERANCE`.
- stable signature 양쪽 동일:
  `0ae609986aa82ad25821baad5420d31b3a82dee0ec7c83bec37e01958323e42b`.
- `max_progress_delta=1`, `max_tick_delta=0`.
- report SHA: `811dbd2462167b7f2707fc426bbf34db21e39c2d64688ac6b116abca1eff6507`.
- report: `temp/Syw2plus_patch/g4_ai/20260916_seed7_repeatability.json`.

따라서 두 개의 fixed-seed fixture와 짧은 생산 threshold 기반이 생겼다. 전투/길찾기 판정에는
아직 짧으므로 다음은 장기 capture 또는 실제 intervention point 조사다.
