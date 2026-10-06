# STATUS — 매 바퀴 갱신하는 기억

lap828까지의 직전 전문은 `docs/history/20261001_status_lap828_precompaction.md`에 보존했다
(130줄, SHA256 `a10af3134a650501aaeaf80e4f10f02ca1d15e246595c6d076ac18d7dfb8cf00`).
더 오래된 상태 전문은 `docs/history/20260930_status_lap800_precompaction.md`와
`docs/history/laps/`에 있다. G5 v10은 사용자 3단 승인·종료, G2 ESL2608 점검은 lap806에서
마감했고 현재 최우선은 G1이다.

## 지금 상태

| 목표 | 판정 | 미충족 |
|---|---|---|
| G1 | lap843 middle: W70 P3 배관 `PASS(partial)` 2단 수용, P3 gate `HOLD` | valid paired visual, 3회 baseline 성능·minimap parity, production UNKNOWN, GDI, 전체 HD coverage, 사용자 승인 |
| G2 | ESL2608 체크리스트 종료(제품 결함 미발견), 일부 `UNKNOWN/BLOCKED(env)` | hero runtime, DxWnd·멀티, 미니맵 runtime, middle/사용자 승인 |
| G3 | 사용자 지시로 중단 | 현재 범위 제외 |
| G4 | 사용자 지시로 보류 | candidate AI 정책 없음 |
| G5 | v10 종료·사용자 3단 승인 | 멀티 env 제한 수용 |

## 지금 막힌 것 (Blockers)

lap843이 lap842 raw 1288행·DLL/source SHA를 독립 재계산해 P3 배관의 inside
`946079`, outside `0`, palette/miss/invalid `0/0/0`, scene/source/cleanup·selection/empty/drag PASS를
수용했다. 그러나 candidate loaded/menu PNG가 동일한 전체 검정 캡처이고 3회 fresh
baseline 성능·minimap parity가 없다. P3 배관만 `PASS(partial)`, 단계 gate는 `HOLD` 유지다.

## 검증 상태

- lap817~828의 상세 raw·SHA·gate는 `docs/history/laps/20260930_lap817*`~
  `docs/history/laps/20261001_lap828*`과 위 precompaction archive에 보존했다.
- lap823 middle은 r4~r6 `source_width` 차이를 메뉴→인게임 전환과 census 64-frame 상한 차이로
  독립 재계산해 충돌을 해소했고 P1 baseline을 `PASS(partial)`로 수용했다.
- lap825는 `0x403C10`을 object-copy로 닫고 fixed terrain buffer/cache/composite 후보를 고정했다.
- lap827 middle은 lap826 raw를 독립 재계산해 terrain consumer가 아닌 알려진 primitive destination
  watchpoint였음을 확인했고, census SHA 전사 오류는 raw로 정정했다.
- lap828 work r5: camera `[158,101]→[160,99]`, watchpoint 3/3 write hit, entry
  `0x4324E0/0x433019/0x4332F0`, writer `0x468C93/0x468C9C`; stable key는 UNKNOWN.
- lap829 middle: 세 raw SHA가 기록과 일치하고 entry181/watch-arm1/write3을 재집계했다. 원본
  `0x435400..0x435593`에서 file/frame→YTL source table 식을 확인해 다음 probe를 `FEASIBLE`로 판정했다.
- lap830 work: `0x435400` key 256건(고유25, 비0 247), blitter call 1061건 전부
  `table_equality=true`, 동일 source digest 변형 0, PS3/renderer `0xBA3D30`, write 3/3;
  source unchanged와 cleanup PASS. raw와 상세는
  `docs/history/laps/20261001_lap830_work_g1_w70_p1_asset_key_trace.md` 및
  `analysis/memory_maps/g1_w70_p1_asset_key_trace_lap830.md`에 보존했다.
- lap831 middle: writer/census/probe SHA를 재해시하고 JSON 1502행을 독립 집계했다. key formula
  위반 0, blit equality true 1061/false 0/unknown 0, 전체 key digest 변형 0, asset event 1317건
  전부 PS3·renderer `0xBA3D30/832/600`, write 3/3이었다. lap830 probe SHA 전사 오류는 raw의
  완전한 값으로 정정했다. `RIGHT` no-change/fallback `DOWN` 및 missing summary 한계는 보존한다.
- lap832 final-source rerun: current source bridge SHA `418c79deb6d70130225316edfd70276cbb421bd3799eee6d1e208bee9af8cbc2`;
  pair SHA `0b6a921482e898a6940c7a50136ea3b5e06788d682d71cce4f237ae0b6d4b55e`, candidate trace
  SHA `aa5b77013cac8b6ca9cd1db04c427ed0665b931414238f752f34bedbf7aed12d`. Candidate 651 mirror/
  identity presents, nearest min 1.0, keys/events `189/25839`, identity pixels `182244/480000`,
  invalid 0, stale 750265, scene parity/source unchanged/cleanup PASS. Input minimap/production
  remains UNKNOWN in both lanes; cross-process screenshot nearest ratio `0.939704` is not same-frame proof.
- lap833 middle: key-bound output 미사용·scroll 0회로 P2 gate `HOLD`를 확정했다. 상세
  `docs/history/laps/20261001_lap833_middle_g1_w70_p2_identity_review_hold.md`.
- lap834 work: key-bound block lookup/hit-miss raw와 paired pan stale delta를 구현·검증했다. final pair
  SHA `e808fa5adbfa646a533b83063cca71d03f94dee9da1159ee9ac6b815c0f109fb`, candidate trace SHA
  `8b614a23bb2b0d0e665ded9aadea0a33e3650db8e6cbdbeccec62f6011f33530`, targeted 13 tests·lint·typecheck·DLL
  build·identity validator PASS. 상세 `docs/history/laps/20261001_lap834_work_g1_w70_p2_keybound_identity_scroll_pass.md`.
- lap835 middle: pair/trace/writer/DLL SHA와 JSONL 2048행을 재검산했다. mirror 962/962,
  nearest 1.0, `176/47004/182643`, pixel-read `25559164/0`, invalid0, stale720646 및 camera
  changed delta `+4032`는 일치하나 shared-scratch alias와 failed/drop304 summary로 P2 gate HOLD다. Final Fast는
  **1205 passed, 5 skipped in 774.73s**, validation `d49c9f58df376ccc7eed5cb5c84120e2a2549bfc`, log SHA `fe19af3b194e5726140881b38f5372cbfeb287f6f0f0834f629eab46b3d2d4c8`.
- lap836 work: final pair SHA `d62bb11deab3fba9f824e99578344bc534df8803548b830a378af81f311f5a7d`,
  candidate trace SHA `afdd4bfd7580d0c96a9018349e33b0b98398ef1f3c803ab53f1946251f047c2e`; identity validator
  PASS, mirror `1230`, keys/events/pixels `179/64374/187382`, nearest min `0.9993895833`, stale `808098`,
  trace events `2346`, source unchanged/cleanup/scene parity PASS. Targeted pytest 20, `make lint`,
  `make typecheck`, context/safety and DLL build PASS. Final Fast `make check`: **1205 passed, 5 skipped
  in 742.41s**, Ruff/compileall/mypy/CONTEXT_PASS, exit0. lap837 재검수에서 P2 validator의 mismatch
  분류 누락이 확인돼 이 exit0은 P2 수용 근거가 아니다.
- lap837 middle: pair/raw/DLL SHA와 raw 2347행을 재검산했고 source snapshot 5개가 artifact와 일치했다.
  cache `179/64195/179`, mismatch `66824-64374=2450`, lookup miss/invalid `0/0`, drop0, nearest
  `0.9993895833`, stale `808098`, scene/source/cleanup은 일치한다. targeted 20 tests PASS는 test gap이며
  P2 gate는 `HOLD`; 상세 `docs/history/laps/20261001_lap837_middle_g1_w70_p2_keycache_review_hold.md`.
- lap838 work: keyed-frame refresh와 altered-key 실제 lookup을 구현했다. candidate raw SHA
  `496a03525b45ce0fda9135d55c774bc3a3f07628fda8c721f678907cdedb6c84`, pair SHA
  `a78d35cd9518562b677df8d66a8a598724d9924fb549b98b8a7f488431ef4d78`; 1246 present, nearest min
  `1.0`, normal miss `0`, refresh `2735`, negative miss/mismatch `64810/64810`, drop0, scene/source/
  cleanup PASS. 상세 `docs/history/laps/20261001_lap838_work_g1_w70_p2_keycache_refresh_pass.md`.
- lap839 middle: raw/SHA/refresh 수리는 수용했으나 negative probe가 table lookup 없이 NULL frame으로
  실패를 강제함을 확인했다. P2 `HOLD`; 상세 `docs/history/laps/20261001_lap839_middle_g1_w70_p2_negative_lookup_review_hold.md`.
- lap840 work: full-key search helper를 begin/negative probe가 공유하고 negative attempt/miss/mismatch를
  별도 trace metric으로 추가했다. fresh save006 pair는 candidate 1124 presents, nearest1.0,
  normal miss0, negative `58867/58867/58867`, invalid/drop0, scene/source/cleanup PASS였다. 상세
  `docs/history/laps/20261001_lap840_work_g1_w70_p2_fullkey_negative_lookup.md`.
- lap841 middle: artifact/current source 전 입력과 DLL manifest SHA를 대조하고 raw 2241행을 독립
  집계했다. normal hit/miss `31526270/0`, refresh3668, negative attempt/miss/mismatch
  `58867/58867/58867`, nearest1.0, invalid/drop0, same-frame false0이었다. 관련 pytest20,
  identity·saved-scene mirror validator, doctor/lint/typecheck/diff-check PASS로 P2를 수용했다. 상세
  `docs/history/laps/20261001_lap841_middle_g1_w70_p2_fullkey_review_pass.md`.
- lap841 final Fast: `make check` **1205 passed, 5 skipped in 744.02s**, Ruff/compileall/mypy/
  `CONTEXT_PASS`, exit0; 사전 `SAFETY_PASS`, log SHA `c7c95f2e021f156387580b81d5a4e38c599442bba70100f38e88523347a272d9`.
- lap842 work: P3 source `scale2x`를 key-bound 원천 frame cache에 연결하고 compositor를 4-way block
  write로 수리했다. targeted pytest 24, lint/typecheck, 강제 DLL build PASS. save006 fresh pair
  candidate 230 present, P3 validator PASS(`inside 946079`, `outside 0`, palette0, lookup miss0),
  scene/source/cleanup PASS; input selection/empty/drag PASS, minimap/production HOLD. raw/pair/DLL SHA와
  상세는 `docs/history/laps/20261001_lap842_work_g1_w70_p3_scale2x.md` 및 공유 temp artifact다.
- lap842 final Fast: `make check` **1208 passed, 5 skipped in 745.76s**, Ruff/compileall/mypy 및
  `CONTEXT_PASS`, exit0. 로그 SHA `a60fb9f40d9b8cb28eafef397dd0db0efc108eb1599bc55910a5b869ad794925`.
- lap843 middle: manifest 39개 source·DLL/raw/pair SHA 일치, 230 present 집계·P3 validator·targeted 19·
  doctor/lint/typecheck PASS. candidate loaded/menu black capture와 성능 1회 gap으로 P3 gate HOLD.
  Final Fast **1208 passed, 5 skipped in 745.38s**, exit0, log SHA `882583da66593e1f56c270bb6291a2317b5f8afd13495267c000dbc3923e2773`.

## 다음 한 가지

- **다음 = work tier가 P3 gate를 완주한다.** post-first-present valid paired capture와 3회 fresh
  baseline/candidate tick·present 성능, minimap diagnostic-gate parity를 남긴다; 통과 전 P4 금지.
- lap830의 camera 변화는 `RIGHT` 단독이 아니라 기존 probe fallback `DOWN`으로 확인됐다;
  RIGHT 단독 이동 성공은 주장하지 않는다.
- HD 출처 결정(lap819): 기본은 원천 프레임 단위 palette-index Scale2x, 대안은
  `SYW2_G1_HD_PACK`; 최종 800 프레임 전체 필터는 금지한다.
- G1 사용자 3단 승인은 없고 S3 합성 패턴은 opt-in 진단일 뿐이다.
- 금지: 원본/참고 저장소 쓰기, 게임 EXE/G2/G5/legacy validator 변경, 기존 raw 덮어쓰기, 커밋.

## 바퀴 기록

- lap801~816 요약은 위 precompaction archive, 상세는 `docs/history/laps/`에 보존했다.
- lap817~828은 W60 saved-scene 계측 독립검수→W70 전략→P1 writer census/terrain route
  반증·고정 writer trace 순으로 진행했다. 현재 구현 증거는 baseline partial이며 W70 candidate나
  실제 HD asset 경로는 아직 없다.
- lap829(middle): lap828 raw와 원본 disassembly를 독립 대조해 asset-key 경로를 `FEASIBLE`로 판정하고,
  광범위 resource-table 조사 대신 exact table-equality runtime probe로 work handoff를 좁혔다.
- lap830(work) asset-key fresh trace → lap831(middle) raw·disassembly 독립 재검수
  `PASS(partial)`; 다음은 P2 identity mapping이다.
- lap832(work) identity sidecar ledger fresh pair → lap833(middle) HOLD → lap834(work) key-bound
  block lookup·camera stale delta fresh pair → lap835(middle) shared-scratch/drop HOLD → lap836(work)
  keyed owned cache fresh pair → lap837(middle) real mismatch 2450·negative test gap으로 P2 `HOLD`
  → lap838(work) refresh/real negative lookup fresh pair `PASS(partial)` → lap839(middle) synthetic
  negative HOLD → lap840(work) shared full-key search·fresh pair → lap841(middle) P2 `PASS(partial)`.
