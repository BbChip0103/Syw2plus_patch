# STATUS lap517 압축 블록 원문 (삭제 없음)

lap517이 `docs/STATUS.md` 「검증 상태」에서 한 블록으로 줄인 lap514·lap513 원문이다. 압축 직전 STATUS는 123줄이었다.

**2026-09-23 lap514(middle, Opus5.5) — lap513 W30 안 B 독립 재계산 = `ACCEPT` ⇒ W30 `CLOSED`**
(전문 `docs/history/laps/20260923_lap514_middle_w30_holeb_independent_recompute.md`, 근거
`analysis/memory_maps/g2_supply_ledger_holeb_acceptance_lap514_20260923.md`, 산출 SHA `0c0ed0d2…`).
원시 `window_hex` 5,768 owner-표본 재추출 `+0x2016` 위반0(tick 16→24,019), 입력 SHA `b8c3b452…`/`030f6a0e…` 일치.
**겹침 기준** 전수 스캔(306,187명령): `[0x200c,0x2010)` = used9+building4+`lea 0x444C63`(→`+0x200a` word 전용, 오탐),
`[0x2016,0x2018)` = `0x43F57F` 1곳(`esi≥1` ⇒ 최저 `+0x2018`). 후보 `1893ff50…` diff 66B 사이트 밖0·역디스어셈블15/15·원복 SHA.
9개 used 소비 전부 32-bit(16-bit 재절단0). 관찰: 단위 M-e/M-f는 Python 산술 모델이라 기계어 근거는 소비 폭 검토가 맡는다;
lap512 `MAX_WALL_S` 변경은 공개된 무해 편차. 게임실행0·제품source변경0·커밋0·`make check`819 passed·`SAFETY_PASS`.

**lap513(work, Sonnet5)** lap512 스크립트 무수정 포그라운드 완주: `HOLE_CONSTANT`·tick24,019·721표본·위반0, 단위23·
`make check`819·`SAFETY_PASS`. 전문 `docs/history/laps/20260923_lap513_work_w30_holeb_runtime_reconfirm.md`.
