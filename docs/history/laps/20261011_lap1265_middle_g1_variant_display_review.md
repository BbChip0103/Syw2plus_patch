# 2026-10-11 | lap1265 | H-G1VARIANT2613 fresh middle review

- 지정 역할: fresh middle / 독립 검수. Native verifier `gpt-6.1-sol`, high. 읽기 전용; 제품 코드·게임·전달 변경 없음.
- 검수 대상: lap1264 G2+G6+G8 / G2+G6+G8+G9 display-only Wine probe. 상세 work 기록 `docs/history/laps/20261011_lap1264_work_g1_variant_display_only.md`.
- 원본/후보 SHA: official 2613 `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`; G2+G6+G8 `1e83466eab020818a6c0e9057508d71451af3ee1098af43ebefc20de8ab96e3d`; G2+G6+G8+G9 `b612109b8cd9e313927871a5a35f28cc09b9c95f80626c938f4d42192cb00556`.
- Raw result JSON 2개에서 각 8개 lane의 PASS, private EXE match, trace close/summary, drop0, detach/flush complete, cleanup, game copy 제거, 종료 후 prefix process 0을 확인했다. 두 변형의 새 게임은 program state 3, save006 타이틀 로드는 약 tick24567–24571.
- candidate 최종 mirror trace hit/reject/fallback: G2+G6+G8 newgame `340/0/0`, save006 `279/0/0`; G9 newgame `337/1/0`, save006 `255/0/0`.
- G9 새 게임 reject 1건은 key log에서 writer `0x00466EA0`, digest `44c611f6`, 96×112, written5257/opaque5261, opaque_unwritten4, 첫/끝 `[51,104]`/`[53,105]`. sidecar `fnt/tree_plus.spr.hd/0000.idx8`과 일치하며 기존 lap1260–1263의 공개된 runtime-mask reject다. asset 투명화/guard 변경 근거는 없고 원인 UNKNOWN 유지.
- 기계검사: 기존 `logs/gates/lap1264-work-make-check-rerun.log` exit0, 2195 passed/9 skipped, Ruff/mypy/context PASS를 대조. 현재 검수는 문서-only이며 full Fast·게임 재실행은 SKIP(동일 raw/소스, 불일치 없음). lap1264 구현/테스트 SHA는 현재 작업트리와 일치.
- 판정: **scoped PASS / 제품 기준 partial**. 이 증거는 두 pinned 변형에서 G1 off/on display startup/newgame/save006 title-load의 Wine 생존만 지지한다. Windows 실행, G2 unit/pool, 8인 부하, G9 자리순서, multiplayer, 24k/144k, 사용자 G1 승인은 미검증.
- 다음 한 가지: 사용자에게 scoped 결과와 알려진 reject/미검증 경계를 보고하고 변형판 전달 필요 여부를 확인한다. G1 마일스톤 완료로 승격하지 않는다.
