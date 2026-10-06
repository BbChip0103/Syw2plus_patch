# STATUS 검증상태 lap751~760 원문 보존 (2026-09-29, lap763 압축)

SHA256 `92372da17c42f857a444b6369443337e53c64f7e41fbce5b243da35915e53236`(원문 40줄)

**lap751**: `tools/g5_stale_tail_probe.py`에 `--restart-dump-only`·`--menu-exit-fresh` 게이트 2개
추가(기존 S1~S5 분기 무변경). v7 restart-dump-only → `RESTART_DUMP_TAIL_CLEARED`. 원본·v8
menu-exit-fresh(fixture 이전) → 둘 다 `MENU_EXIT_FRESH_BLOCKED_SAME_AS_FIXTURED`. pytest
(v7/v8) 9 passed, `make check` 1115 passed·5 skipped(783.17s), ruff/mypy/`CONTEXT_PASS`,
`SAFETY_PASS`. 3회 실행 전부 `source_unchanged=true`·`cleanup.ok=true`. 제품 코드 0 변경.
**lap752(middle)**: 보호 원본 `b56986e0…` 확인, v8 재빌드 `ef46d1ac…` 일치. 정적: `0x892410` 즉치 179건
(thiscall 177·push 2), this-상대 `0x6c14`/`0x6c18` 각 1건 = `0x4a3060` 안뿐, v8 `0x0108C000` 참조 `.text`10·
`.rsrc`2에 0 채우기 없음(로드 래퍼 제외). `make check` 1115 passed·5 skipped(880.57s), `SAFETY_PASS`·`CONTEXT_PASS`.
게임 실행 0회, 제품 코드 0 변경.
**lap753(work)**: v9(`patches/selection/g5_selection_cap50_v9.py`, `0x4a3168` 1지점 hook, cave `.rsrc`
0x2200~0x2240, 재빌드 SHA `18181cdef6c7…`, pytest 7개 PASS) + `tools/g5_stale_tail_probe.py
--newgame-stale-probe`(신규 게이트, 선택 배열 직접 stale 주입 + 재시작). 결과: 원본
`NEWGAME_STALE_CLEARED`, v8 `NEWGAME_STALE_PERSISTED`, v9 `NEWGAME_STALE_CLEARED`(falsification 삼각
확정). v9 S1/S2/S4 회귀 `PASS_NO_STALE_TAIL_EFFECT`. `make check` 1122 passed·5 skipped(774.79s),
ruff/mypy/`CONTEXT_PASS`·`SAFETY_PASS`. `runtime_driver.py`에 `write()` 추가(진단 전용, 기존 `read()`와
같은 격리 범위). 호출자 gdb 귀속(②)은 work 판단으로 생략(근거는 lap 상세 참고).
**lap754(middle)**: 보호 원본 `b56986e0…`, v8 `ef46d1ac…`·v9 `18181cde…` 재빌드 일치. hook/cave 디스어셈블·
호출자 3곳·this-상대 disp 재스캔(2건) 확인, lap753 raw 재계산 일치. G5 pytest 56 passed, `make check` 1122
passed·5 skipped(730.26s), ruff/mypy/`CONTEXT_PASS`, `SAFETY_PASS`. 게임 실행 0회, 제품 코드 0 변경.
**lap756(work)**: v10(`patches/selection/g5_selection_cap50_v10.py`, hook 2곳 `0x00440F1E`/`0x004412EE`
= 각 save/load 루프의 진짜 마지막 block-transfer 호출, magic+전체50배열 트레일러, 재빌드 SHA
`c3ceaa25dea9…`, pytest 9 PASS) + `tools/g5_v10_foreign_save_load_probe.py`(신규, cross-build 로드 전용).
런타임 3-way 전부 PASS: ① v10 자체 save→load count=50/50 전부 복원(`legit_slots_after_load` 50개 일치,
`commanded_outside_legit_selection`=[]), ② 원본EXE가 v10세이브 로드 → 크래시0·레거시20 정상,
③ v10이 원본세이브 로드 → 크래시0·앞20 복원·21~50 zero(기존 v7~v9 폴백 그대로, 회귀 없음). 개발 중
1차 시도는 `.rsrc`(R+X, W아님) 안에 scratch를 둬 로드 시 write access violation 크래시 1회 발생 →
`v1.STORAGE_END`(R+W `.data`)로 이동해 해소(2/2 이후 크래시 0). `make check` 1131 passed·5
skipped(714.79s), ruff/mypy·`CONTEXT_PASS`·`SAFETY_PASS`. 4회 실행 전부 `source_unchanged`·`cleanup.ok`.
**lap757(work)**: `tools/g5_v10_partial_and_squad_saveload_probe.py`(신규) — Round A(25기 미지정
선택) 저장/로드 25/25 PASS, Round B(부대1=15기 Ctrl+1 + 별도 35기 미지정 라이브 선택 동시 저장)
로드 후 라이브35/35 PASS + "1" 소환 시 원래 부대1 15명 정확 복원 PASS(사이드카·부대 저장소 간섭
없음). `make check` 1131 passed·5 skipped(757.84s), `SAFETY_PASS`. 크래시0, `source_unchanged`,
`cleanup.ok`.
**lap760(work)**: 항목(2) ① 수확(V) paired — 랜덤국가 op=5 fixture 5회 `unsupported_army_fixture_type`
(lap730 기존 관측 재확인) 후 이미 검증된 private fork `g5_c_repair_bridge.c`(고정 allow-list 대신
구조적 게이트, 공유 G2-pinned 파일 무변경)로 해소 — 원본20/20·v10 50/50 전원 채집 pending PASS.
② 미니맵 native ddraw.dll override 3변형(builtin/native/native+LoadLibrary) 전부 렌더·클릭 신호
없음 — 원인 아님을 반증(UNKNOWN 유지). `pytest -ra` 1131 passed·5 skipped(662.41s),
ruff/mypy/compileall/`CONTEXT_PASS`/`SAFETY_PASS` 개별 실행 전부 PASS(제품 코드 무변경). 크래시0,
`source_unchanged` 전부 true, `cleanup.ok`.
