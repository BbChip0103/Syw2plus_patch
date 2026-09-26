# STATUS — 매 바퀴 갱신하는 기억

## 지금 상태

2026-09-11 lap105는 두 고정 원본의 DirectDraw presentation-boundary를 읽기 전용으로 대조했다.
두 파일 SHA는 `b56986…a8ac`, `cmp=0`, PE32로 일치했고 DirectDrawCreateEx IAT direct-xref는
`0x00464374` 하나였다. 그러나 `slot +0x14` 후보 49개와 `slot +0x2c` 후보 14개가 복수 generic
surface/array 경계로 남고, 800×600 source를 1600×1200 destination rectangle으로 유일하게 잇는
값·writer·Flip 선택은 고정되지 않았다. 따라서 이번 work probe는 **CONCRETE BLOCKER**이며
구현·G1 승격 없이 `loop/ESCALATE_SOL`로 Astra/high architecture handoff를 남겼다.

| 목표 | 판정 | 근거 / 미충족 |
|---|---|---|
| G1 1600×1200 원본 구성 | 미완료 | OS input origin static path는 lap102 확인; 실제 2배 출력/필수5입력·field/action 의미는 미검증 |
| G2 8인 전비5000 안정성 | 미완료 | 과거1명4990→5000/2진영뿐; 활성8인 스트레스 아님 |
| G3 최대16인 | 미완료 | 9~16인 실제 동작/통신 검증 없음 |
| G4 길찾기/AI 난이도 | 미완료 | 원본 대비 반복 측정·개선 구현 없음 |

## 다음 한 가지

**Astra/high architecture 작업자는 G1 presentation blocker를 검증하라.**
`0x004d7938` IAT→`0x00464374` 생성, `0x00464502/0x00464509`의 800×600 설정, `+0x14` 49개와
`+0x2c` 14개 후보를 출발점으로 surface ownership→rectangle writer→실제 Flip 선택을 독립
호출 그래프와 isolated runtime trace로 확정하라. 단일 기존 경계와 1600×1200 destination을
증명하기 전에는 patch·candidate·G1 PASS를 만들거나 승격하지 않는다.

## 지금 막힌 것 (Blockers)

- lap103의 `.venv/bin/pytest` exit127은 lap104에서 지원 경로와 Fast PASS로 해소됐다. 실패 명령과
  첫 수동 길이 정정은 lap103 원문에 보존한다. 정적 mouse-coordinate origin은 컨펌됐지만
  `0x00437E90` 이후 gameplay command/action 의미와 G1 2배 presentation boundary는 별개 blocker다.
- lap69~96의 해소·정정·static blocker 상세는 기존 compaction 파일, `docs/history/laps/20260911_status_lap100_compaction.md`, 각 lap 원문에 보존한다. primary worker/production direct edge 미증명과 구현 금지는 유지한다.
- group10 `0x498F65`, primary 12-slot table, `0x49B6D0` group2..5는 별개다. 화면 icon이나
  `(670,490)`만으로 동일시하지 않는다.
- lap60 live selection은 slot1199/type70, unit `0x00891CB8`, type flags `0x009C4CC4=0`이다.
  selected state `0x00891D4C=0`은 stable하지만 type predicate가 false라 group2..5 생성 경로는
  관측되지 않았다. alternate count `0`, 첫10 record/flags `0`, geometry `445,545,30,30`은
  before/after 동일하며 UI-list raw 관측일 뿐 production 의미가 아니다.
- G1 실제 2배 출력/입력, G2 8인5000, G3 9~16인, G4 비교 지표 및 사용자 승인은 모두 미검증이다.
- lap105 G1 presentation probe는 두 고정 원본에서 IAT/direct-xref와 old bytes는 일치했지만,
  `+0x14` 49개·`+0x2c` 14개 generic 후보 중 800×600→1600×1200 rectangle의 unique writer/Flip
  edge를 찾지 못해 **CONCRETE BLOCKER**다. 구현·runtime 재실행 없이 `loop/ESCALATE_SOL`로
  Astra/high architecture handoff를 남겼다.
- lap97 middle은 lap96의 두 SHA/cmp/PE, 207-byte old bytes, 7개 branch/call, helper 반환과
  LIFO stack provenance를 독립 확인해 **CONFIRM PASS**했다. 다만 `0x0041EC3D` 진입 전 CX·ESI의
  production source는 미증명이므로 callback/worker/unit/primary sender edge는 계속 BLOCKED다.
- lap98 Luna는 `0x0041EBF6`의 CX state mapper chain과 `0x0041EC71`의 ESI active-record table
  chain을 각각 old bytes/direct xref로 고정했지만 input→record writer 및 mapper→enqueue direct edge를
  찾지 못했다. 기계 계약은 PASS, production sender 의미는 **CONCRETE BLOCKER**로 유지한다.
- lap99 middle은 두 원본의 SHA/cmp/PE, upstream raw bytes 7개, caller `3/1/11/134`와
  mapper 내 enqueue call 부재를 독립 재현해 lap98을 **CONFIRM PASS**했다. 공유 state/table의
  production 의미는 미확정이므로 work-tier CFG/writer probe 전 구현을 금지한다.
- lap100 Luna는 두 원본의 SHA/cmp/PE, updater→state-load branch 10개, `0x009E1DCC` writer
  10개 및 `0x00892FFE` writer 18개의 old bytes를 재현해 read-only contract로 고정했다.
  정적 chain은 PASS지만 production sender/action 의미와 G1은 UNKNOWN/BLOCKED다.
- lap101 middle은 독립 raw-byte/`objdump` 재추출로 lap100을 **CONFIRM PASS**했다.
  첫 Capstone full-linear probe는 비명령 byte에서 decode가 중단돼 FAIL/폐기했고,
  해당 결과는 근거로 사용하지 않았다. production action/direct edge blocker는 유지한다.
- lap102 Luna는 두 고정 원본의 SHA/cmp/PE32 확인 뒤 Win32 WndProc 등록·message dispatch,
  WM_MOUSEMOVE 좌표 저장, event-ring writer/reader, `0x00637734/0x00637736` writer/reader,
  `0x00437E90` updater call의 old bytes와 direct targets를 SHA-gated contract로 고정했다.
  targeted **13 passed**, `make check` **140 passed**, Ruff/compileall/mypy/context PASS,
  safety `SAFETY_PASS`, doctor `ok=true`/original verified다. runtime manifest/game/fixture/candidate는
  SKIP이고, gameplay meaning·1600×1200·사용자 마일스톤 승인은 없다.

## 검증 상태

- lap104는 `Makefile`의 `PYTHON ?= .venv/bin/python`/`-m pytest` 계약과 pytest 9.0.2를 확인했다.
  `.venv/bin/python -m pytest -q tests/test_binary_contract.py` **13 passed**, 이어 `make check`
  **140 passed**; Ruff/compileall/mypy/context와 최종 safety PASS다. 두 원본 SHA/cmp도 고정값과 일치했고
  candidate/runtime/game/fixture/capture는 SKIP이다. lap102 static contract만 CONFIRM PASS다.

- lap103은 두 원본 SHA/cmp/PE, `RegisterClassA`/`DispatchMessageA`, WM_MOUSEMOVE 분기,
  old-byte 범위 36/36, direct call 6/6 및 ring→좌표 global→updater 흐름을 독립 재추출했다.
  `make doctor`는 top-level `ok=true`/original verified, runtime manifest absent였다. 필수 targeted
  gate는 launcher 부재로 exit127 FAIL, `make check`/runtime/game/fixture/candidate는 SKIP이다.

- lap101은 두 원본 SHA/cmp와 PE `.text` mapping, updater→state-load branch 10개,
  `0x009E1DCC` writer 10개 및 `0x00892FFE` writer 18개의 old bytes를 독립 재현했다. targeted
  **12 passed**, `make check` **139 passed**, Ruff/compileall/mypy/context PASS, safety
  `SAFETY_PASS`, doctor top-level `ok=true`/original verified다. runtime manifest/game/fixture/candidate는 SKIP이다.

- lap92~97의 binary-contract 및 middle 검증 수치 상세는 `docs/history/laps/20260911_status_lap100_compaction.md`와 각 lap 원문에 보존한다.

- lap57~65의 원본 분기·alternate/primary table 진단, runtime SHA, 테스트 결과 상세는
  `docs/history/laps/20260911_status_lap71_overflow_recovery.md`와 각 lap 원문에 보존한다.

- lap66~72의 exact-single-selection, count evidence, production no-click 및 overflow 복구 상세는
  `docs/history/laps/20260911_status_lap77_compaction.md`와 각 lap 원문에 보존한다.

- lap73~80의 private evidence run, primary-panel/dataflow, render-helper 및 IAT 검수 상세는
  `docs/history/laps/20260911_status_lap82_compaction.md`와 각 lap 원문에 보존한다.

- lap81~85의 record xref, STATUS gate recovery, input chain과 semantic-label 검수 상세는
  `docs/history/laps/20260911_status_lap86_compaction.md`와 각 lap 원문에 보존한다.

- lap87~91의 xref 정정, dequeue probe 및 guard truth-table REVISE 상세는
  `docs/history/laps/20260911_status_lap92_compaction.md`와 각 lap 원문에 보존한다.

- lap92는 두 고정 원본 SHA/cmp/PE 매핑과 `0x004AC420` caller/callee를 재확인하고,
  `0x004AC47F..0x004AC4DF` guard bytes·5개 branch target·call/skip truth table 계약을 추가했다.
  `make check` **134 passed**, Ruff/compileall/mypy/context와 safety PASS, doctor top `ok=true`/original
  verified다. 후보·game·fixture는 SKIP이며 상세는 lap92 원문이다.

- lap56·58·60의 runtime manifest/verdict/source SHA 상세는 `docs/history/laps/20260911_status_lap94_prework_compaction.md`와 각 lap 원문에 보존한다.
- lap94는 generic ring producer/consumer chain conflict와 read-only contract 상세를
  `docs/history/laps/20260911_lap94_luna_g1a_generic_ring_boundary_probe.md`에 보존한다.

## 바퀴 기록

- lap2~51 상세는 `docs/history/laps/`에 보존한다.
- lap52~86 상세 목록은 `docs/history/laps/20260911_status_lap94_prework_compaction.md`와 각 lap 원문에 보존한다.
- lap87~95 상세 목록은 `docs/history/laps/20260911_status_lap100_compaction.md`와 각 lap 원문에 보존한다.
- lap96: `docs/history/laps/20260911_lap96_luna_g1a_dispatch_block_contract.md`.
- lap97: `docs/history/laps/20260911_lap97_middle_g1a_dispatch_block_confirmation.md`.
- lap98: `docs/history/laps/20260911_lap98_luna_g1a_upstream_provenance_probe.md`.
- lap99: `docs/history/laps/20260911_lap99_middle_g1a_upstream_provenance_confirmation.md`.
- lap100: `docs/history/laps/20260911_lap100_luna_g1a_upstream_cfg_writer_probe.md`.
- lap101: `docs/history/laps/20260911_lap101_middle_g1a_upstream_cfg_writer_confirmation.md`.
- lap102: `docs/history/laps/20260911_lap102_luna_g1a_coordinate_input_provenance_probe.md`.
- lap103: `docs/history/laps/20260911_lap103_middle_g1a_coordinate_input_provenance_confirmation.md`.
- lap104: `docs/history/laps/20260911_lap104_middle_g1a_verification_invocation_confirmation.md`.
- lap105: `docs/history/laps/20260911_lap105_luna_g1a_presentation_boundary_probe.md`.
