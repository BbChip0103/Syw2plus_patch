# 2026-09-11 | lap112 | STATUS overflow recovery

lap111 middle 기록 뒤 `docs/STATUS.md`가 안전 상한 180줄을 넘어 최종 Fast/safety와 루프가
fail-closed 정지했다. 최신 lap108~111 runtime/ABI 판정과 다음 한 가지는 유지하고, 이미 개별
history가 있는 이전 상세를 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `e054c96376f0b6237e0c40b53ab15b53d0294998a16381a1106e09c0ea2acb36`
- 각 lap 원문과 앞선 compaction 기록은 `docs/history/laps/`에 보존된다.
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 blocker 상세

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

## 이동한 검증 상세

- lap107 read-only 검수에서 두 원본 SHA/cmp/PE, lap105 49/14 및 old bytes, lap73 artifact
  SHA와 cleanup을 재현했다. 첫 수동 scan의 잘못된 file offset 결과는 폐기하고 `objdump -h`의
  `0x1000`으로 정정했다. `make check` **140 passed**, Ruff/compileall/mypy(8 files)/context와
  safety `SAFETY_PASS`. 실제 trace/game/candidate는 SKIP이며 기계 PASS를 계획·제품 승인으로
  승격하지 않는다.

- lap106 문서 대조 완료. `make check` 140 passed, Ruff/compileall/mypy/context/shell syntax
  PASS; safety `SAFETY_PASS`. lap105 수치 독립 재추출·실제 출력/input·후보·G1·사용자 승인은
  미검증이며 기계 PASS를 계획 승인이나 runtime 검증으로 승격하지 않는다.

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

## 이동한 lap96~107 목록

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
- lap106: `docs/history/laps/20260911_lap106_astra_g1_presentation_handoff.md`.
- lap107: `docs/history/laps/20260911_lap107_sol_g1_presentation_plan_review.md`.
