# 2026-09-11 | lap94 work 시작 전 | STATUS compaction 기록

`docs/STATUS.md`가 167줄에 도달해 다음 work/middle 기록의 안전 여유가 부족했다. 최신 판정과
lap87~93 이력은 유지하고, 오래된 runtime SHA 상세 및 lap52~86 목록을 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `c9f4d7d971b6a30ed80b74762d483596e3258af105e3be237c02899c0978172a`
- 각 lap 원문은 `docs/history/laps/`에도 보존된다.
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 runtime/source SHA 상세

- lap60 새 run manifest `local/runtime/20260911_065344_2240721_0/manifest.json` SHA
  `be3023c43ebec7a76ec7bb09a99f0c9fd5c9cb27c93ab6af64d38d7836e1d5fe`, private EXE SHA는 원본과
  같은 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다. `output/g1_baseline.json`
  SHA `24c9656326482a5a21b294729c7ff840653c116693286f04c28b70ed761ac737`, verdict SHA
  `8ae22317aaf77b161c36341bd0e0dd85363c23d507e54c17a4946d9e986e6825`, provenance SHA
  `bbdafe049307a3f8d4fcd7b57aa9126e68eac006e46f3471d9538db141b82e7d`다. `make check` **116 passed**,
  Ruff/compileall/mypy/context PASS, safety `SAFETY_PASS`, `make doctor-runtime MANIFEST=...` `ok=true`다.
  최초 인자 없는 doctor-runtime 호출은 Makefile 사용법 오류였고, manifest 명시 재검증은 통과했다.

- lap56 run manifest `local/runtime/20260911_063022_2078607_0/manifest.json` SHA
  `3d8d4f8d2a0f5cefd98e6a6d6fd6f3a964669cc4c4f56849f9c36738651e5de6`, private EXE SHA는 원본과
  같은 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다. G1 artifact는
  `output/g1_baseline.json` SHA `cca12b7fa9aace138a891cd53d2309357749f196e3b751111885701af08aa63a`,
  verdict SHA `8dfddc65a78385e5eefa9266074bd33defd0c2030be16dc5fda4d108742397c3`이며 상세 PNG
  경로/해시는 해당 JSON에 보존했다. Fast는 `114 passed`, Ruff/compileall/mypy/context PASS,
  safety `SAFETY_PASS`, doctor-runtime `ok=true`다.

- lap58 변경 source SHA: `tools/runtime_env.py`
  `e605e041816856bc88458df8bfad85e2e77cdac40f4ba6cab1e6e7d4e3d32dd5`,
  `tests/test_runtime_env.py`
  `58ea272f06d78f1edc672d4f569d7a7e3bd6ea0d644f3b68d6a6bd06931e024c`.
  원본/참고 EXE·DLL·assets와 runtime run은 변경하지 않았고 후보 EXE SHA는 없음.

## 이동한 lap52~86 목록

- lap52: `docs/history/laps/20260911_lap52_luna_g1a_command_branch_contract.md`.
- lap53: `docs/history/laps/20260911_lap53_sol_g1a_command_branch_review.md`.
- lap54: `docs/history/laps/20260911_lap54_luna_g1a_selection_identity_repair.md`.
- lap55: `docs/history/laps/20260911_lap55_sol_g1a_selection_identity_confirmation.md`.
- lap56: `docs/history/laps/20260911_lap56_luna_g1a_live_ineligible.md`.
- lap57: `docs/history/laps/20260911_lap57_sol_g1a_live_ineligible_review.md`.
- lap58: `docs/history/laps/20260911_lap58_luna_g1a_alternate_snapshot_repair.md`.
- lap59: `docs/history/laps/20260911_lap59_sol_g1a_alternate_snapshot_review.md`.
- lap60: `docs/history/laps/20260911_lap60_luna_g1a_alternate_snapshot_live_ineligible.md`.
- lap61: `docs/history/laps/20260911_lap61_sol_g1a_primary_command_table_diagnosis.md`.
- lap62: `docs/history/laps/20260911_lap62_sol_g1a_primary_command_table_escalation.md`.
- lap63: `docs/history/laps/20260911_lap63_sol_g1a_primary_single_selection_review.md`.
- lap64: `docs/history/laps/20260911_lap64_sol_g1a_exact_single_selection_confirmation.md`.
- lap65: `docs/history/laps/20260911_lap65_sol_g1a_exact_single_selection_gate_recovery.md`.
- lap66: `docs/history/laps/20260911_lap66_luna_g1a_exact_single_selection_implementation.md`.
- lap67: `docs/history/laps/20260911_lap67_sol_g1a_exact_single_selection_review.md`.
- lap68: `docs/history/laps/20260911_lap68_luna_g1a_selection_count_evidence_repair.md`.
- lap69: `docs/history/laps/20260911_lap69_sol_g1a_selection_count_evidence_confirmation.md`.
- lap70: `docs/history/laps/20260911_lap70_luna_g1a_production_fail_closed_gate.md`.
- lap71: `docs/history/laps/20260911_lap71_sol_g1a_production_fail_closed_confirmation.md`.
- lap72: `docs/history/laps/20260911_lap72_sol_g1a_fail_closed_gate_recovery.md`.
- lap73: `docs/history/laps/20260911_lap73_luna_g1a_private_baseline_evidence.md`.
- lap74: `docs/history/laps/20260911_lap74_sol_g1a_private_baseline_confirmation.md`.
- lap75: `docs/history/laps/20260911_lap75_luna_g1a_primary_cell_static_trace.md`.
- lap76: `docs/history/laps/20260911_lap76_sol_g1a_primary_cell_static_confirmation.md`.
- lap77: `docs/history/laps/20260911_lap77_luna_g1a_primary_dispatch_dataflow.md`.
- lap78: `docs/history/laps/20260911_lap78_sol_g1a_primary_dispatch_confirmation.md`.
- lap79: `docs/history/laps/20260911_lap79_luna_g1a_render_helper_side_effect.md`.
- lap80: `docs/history/laps/20260911_lap80_sol_g1a_render_helper_confirmation.md`.
- lap81: `docs/history/laps/20260911_lap81_luna_g1a_record_reader_xref.md`.
- lap82: `docs/history/laps/20260911_lap82_sol_g1a_record_reader_confirmation.md`.
- lap83: `docs/history/laps/20260911_lap83_sol_status_gate_recovery.md`.
- lap84: `docs/history/laps/20260911_lap84_luna_g1a_input_dispatch_chain.md`.
- lap85: `docs/history/laps/20260911_lap85_sol_g1a_input_dispatch_confirmation.md`.
- lap86: `docs/history/laps/20260911_lap86_luna_g1a_exact_record_consumer_enumeration.md`.
