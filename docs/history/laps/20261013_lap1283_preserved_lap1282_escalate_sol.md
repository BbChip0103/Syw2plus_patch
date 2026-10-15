lap1282 일반 work 세션 역할 경계 인계 — 구현/검증/전달 변경 없음

현재 STATUS의 다음 한 가지는 lap1281 H-HDSINGLE RLE writer 수리 결과에 대한 fresh middle 독립 검수다. 이번 세션은 hands-on work 역할이므로 자기 work 결과를 middle로 승인하지 않는다. 마일스톤/전달 후보 확정 전 단계에서 역할이 맞지 않는 호출을 확인해 여기서 종료한다.

승격 작업자가 이어서 확인할 것:
1. `docs/history/laps/20261013_lap1281_work_hdsingle_rle_collision_repair.md`의 구현 범위와 결과를 독립적으로 검수한다.
2. lap1280 재현 원인과 lap1281 수리 후보를 대조한다: 3 SPR 파일의 RLE/raw sentinel 길이 충돌 제거, Python mask round-trip 3/3, 투명 마스크·불투명 픽셀 불일치 0, true-raw 처리 보존, C reader 대조.
3. lap1281에서 보고된 targeted 150, lint/typecheck, 공식2613·두 변형의 new-game/save006 on/off 12 display lane 및 owned cleanup 증거를 해당 raw/log와 대조한다. 기존 PASS를 새로 실행한 결과로 표현하지 않는다.
4. mirror validator BLOCKED와 tree_plus reject1 원인 UNKNOWN, Windows/사용자 G1 확인 미검증을 유지한다. 해결되지 않은 필수 기술 충돌이면 HOLD 및 근거를 기록한다.
5. fresh middle 판정 PASS 이후에만 root가 전달 후보 고정과 전달 직전 같은 source의 전체 `make check` 1회를 판단한다. 사용자 전달/마일스톤 승인은 별도다.

참조: `docs/STATUS.md`, `docs/history/laps/20261013_lap1280_middle_hdsingle_native_collision_hold.md`, `docs/history/laps/20261013_lap1281_work_hdsingle_rle_collision_repair.md`.
