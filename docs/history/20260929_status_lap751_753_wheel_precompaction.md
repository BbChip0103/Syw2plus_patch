# STATUS 바퀴 기록 압축 보존 — lap751~753 (2026-09-29, lap757 세션)

원문 17줄, SHA256 `73369b17116c3a86a7bc05cd6967a38496745d9d803e0547df6f3d2b1f4c1375`
(`docs/STATUS.md` "바퀴 기록" 섹션에서 이 3개 항목을 그대로 옮김; 내용은 이미
`docs/STATUS.md`의 "검증 상태" 섹션에도 같은 lap들의 수치가 요약돼 있어 "바퀴 기록"에서는
중복 제거 목적으로 압축한다. 판정/근거는 변경 없이 원문 그대로 아래에 보존한다).

- lap753(work, Sonnet5): v9 빌드 + falsifiable stale-injection paired probe(신규
  `--newgame-stale-probe`). 원본/v8/v9 3-way = `CLEARED`/`PERSISTED`/`CLEARED`(사전 등록한 결과 그대로
  확정). v9 S1/S2/S4 `PASS_NO_STALE_TAIL_EFFECT`. `make check` 1122 passed·5 skipped, `SAFETY_PASS`.
  제품 코드 신규 1개(v9)만 추가, v1~v8 바이트 무변경(pytest로 diff 범위 고정). 다음은 middle F/S3
  재검수. 상세 `docs/history/laps/20260928_lap753_work_g5_f_s3_v9_newgame_init_falsified_confirmed.md`.
- lap752(middle, Opus5): F 최종 재검수 = `HOLD` 유지. lap751 analogy 거부 — 원본 `0x4a3060`(새 게임
  초기화 3 호출자)이 레거시 선택 count/엔트리를 직접 0으로 만들지만 v8 새 배열은 빠짐(H-NEWGAME-INIT,
  정적 확정). (A) 표가 this-상대 쓰기 2건을 놓침. v9 1지점 + stale 주입 probe를 work에 handoff.
  `make check` 1115 passed·5 skipped, `SAFETY_PASS`. 상세
  `docs/history/laps/20260928_lap752_middle_g5_f_s3_newgame_init_gap_v9_handoff.md`.
- lap751(work, Sonnet5): lap750 핸드오프 ①②를 처리. probe에 `--restart-dump-only`·`--menu-exit-fresh`
  게이트 2개 추가(기존 흐름 무변경). ① v7 restart-dump-only = `RESTART_DUMP_TAIL_CLEARED`(재시작은
  해체(dec) 경로, 로드 경로 아님). ② 원본·v8 menu-exit-fresh(fixture 이전) 둘 다
  `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`(환경 제약, fixture 무관 확정). v9 트리거 미성립으로
  v9 미착수. pytest 9 passed, `make check` 1115 passed·5 skipped, `SAFETY_PASS`. 제품 코드 0 변경.
  다음은 middle F 최종 재검수. 상세
  `docs/history/laps/20260928_lap751_work_g5_s3_restart_attribution_menu_exit_env_confirmed.md`.
