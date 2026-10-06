# G1 W70 P3b structure-cost escalation — lap 852

## 판정 요청

P3b clip-key repair의 세 번째/source-informed attempt에서 cache validation은 회복했지만 필수 fixed-window tick-rate gate는 계속 실패했다. middle/strategy가 raw와 implementation을 독립 검토해 현재 P3 compositing 구조를 계속 최적화할지, sentinel 1회화/dirty-rectangle present 등 구조 대안을 새 bounded 카드로 다룰지 판정해 달라. 이 요청은 P3 pass, P4 전환, 사용자 milestone 승인이 아니다.

## 실측 근거

- Pinned original EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`, non-synthetic.
- Final diagnostic pair `lap852_p3b_stride_probe`: baseline 19.999596Hz, candidate 10.699810Hz, ratio `0.535001`, p95 delta `+11ms`, required rate gate FAIL. Scene state equal; source unchanged and cleanup/game removal PASS; 20 intermediate state samples about 1s apart. Input effect HOLD: selection/empty click pass, drag/minimap gate restore/production fail.
- Dedicated Scale2x validator PASS after replay-stride fix: `clip_replay_mismatches=0`, `identity_invalid_sources=0`, key-bound lookup misses0, palette violations0, outside-mask differences0. Full-frame calls0; tagged window has 54 inserts / 220,220 insert-frame bytes, 8,234 hits / 6,960,121 visible compare bytes, 220,220 Scale2x blocks and 220,220 builder input bytes. Viewport full bounds `(0,0,799,599)` are grounded in the pinned original and recorded in `analysis/memory_maps/g1_w70_unclipped_replay_viewport_lap852.md`; field mutations0, restore failures0.
- QPC frequency 10MHz; candidate tagged rows span 19.716s with 9,021 reinvokes. `compose=176,514,872` ticks = 17.6515s (~89% window, 1.956ms/reinvoke); `original_call_a+b=0.0059s`, `scratch_clear=0.0118s`, `hash_lookup=0.0448s`, `bind_compare=0.0051s`, `bind_copy_alloc=0.0003s`, `scale2x_build=0.0015s`. The compose section's visible-area traversal and key-bound block lookup/write consume substantially more than the P3 overhead allowance.
- Viewport field restoration and readback passed on normal return; exception-path restoration was not implemented or exercised and remains a limitation of this lap's evidence.
- Generic nearest-oracle diagnostic remains BLOCKED at 0.990946 vs 0.999. The same result occurs on lap849 pairs5/6/7 with dedicated Scale2x validator PASS; no legacy validator/threshold was changed. Treat this as an unresolved diagnostic, not silently accepted.

## Bounded history and stop

- Pre-repair QPC ON/OFF pair completed: ON10.2498Hz/p95 11ms; OFF10.1998Hz/p95 11ms, only a single-pair noise estimate.
- Attempt1 `lap852_p3b_pair1`: ratio0.7450, p95+9ms, clip replay mismatch11,144, Scale2x BLOCKED. Attempt2 `lap852_p3b_viewport_probe`: ratio0.7450, p95+9ms, Scale2x BLOCKED; the first viewport-mutation counter was mislabeled and is superseded by corrected telemetry. Attempt3 `lap852_p3b_stride_probe`: Scale2x PASS but ratio0.5350 and compose-dominated. Three bounded repair/probe attempts are exhausted.
- Pair-result and candidate raw trace SHA256s: pair1 `0111e26bbd03fe56430e89b0018c4ab3ef970323e88bc951fc6b60f523927218` / raw `f7d8d404588f27bcc16520e7a1f23f58adcbb9bd14baf54af893a7ccc4b24802`; viewport `a59b4427311d7e139ce35f0baf5f171c779f5ad576f2b9b5034b0a7372614570` / raw `8a1b26eb9eebfdc2208c08a989d4e9dcfba66398a4000a287cda257d36cebae1`; stride `67a88165b378166197ad22725a155f1a6144a8dcd50f643c4e360d6a312cf954` / raw `2ec291bf2452527e847a412a56b5f6554c744409c3dcc9c4ed3c06a3588c6536`. Pre ON/OFF pair/raw SHAs and the detailed cost table are in `docs/history/laps/20261002_lap852_work_g1_w70_p3b_clipped_key_cost.md`.
- No fresh three-pair gate was run after the final diagnostic definitively failed its required rate criterion. No code retry beyond this point in lap852. Preserve current dirty worktree, raw artifacts, and no-commit state.
- Final source Fast after handoff edits: `make check` exit 0, 1218 passed / 5 skipped in 764.23s; Ruff, compileall, mypy, and CONTEXT_PASS passed. Five skips require absent pinned local stock/ESL references.

## Scope and next action

The completed work changed G1 cache/compositor instrumentation and probe harness only; no EXE/G2/G5/runtime exclusion path was touched. P3 acceptance remains outstanding, P4 remains prohibited, and G1 milestone/user approval remains absent. STATUS names the next action: middle/strategy independently review the compose-dominated evidence and decide a bounded structural alternative or stop.
