# 2026-09-25 direct G2 ESL2606 owner500/pool4092 portrait regression audit

## User report / decision

User reports that clicking a newly recruitable general's center-bottom portrait no longer moves to the building that can produce it, and asks for further bug search and definite checks. The delivered test EXE (`af7880d2…342ba3f3`) is **use-held**; its adjacent warning file is updated. No original/reference EXE or save was written, no commit/deploy was made, and no corrected EXE was placed in `260921_temp`.

## One bounded fix and evidence

Full byte/call-chain explanation is `analysis/memory_maps/g2_esl2606_idle_portrait_producer_scan_20260925.md`. The original `FUN_004183A0` producer finder still used three 1200-slot operands after the global pool became 4093 slots. The patcher now changes only those three complete instructions (6 differing immediate bytes versus the held candidate), with exact preimage, overlap, SHA/version, copy-only and restore guards. Corrected private candidate SHA `ce3465e7…9ec20c9ac`; original reference SHA `4a03895d…2f5210c6f8` unchanged.

Regression tests were written before implementation and failed as intended (missing `producer_lookup_capacity`/fixup), then passed **6/6** after implementation. Ruff, mypy and compileall passed. `make doctor` passed setup/original SHA; fresh `make check` completed **896 passed/667.08 s**, Ruff, compileall, mypy, context and shell syntax exit 0. Separate `checks/safety.py` reported `SAFETY_PASS`. This is stage-1 mechanical verification only, not next-session independent review or user milestone approval.

Fresh isolated Wine runs (each a complete game copy, owned prefix and Xvfb; raw under `local/runtime/`, screenshots under shared `temp/Syw2plus_patch/captures/`): `runtime_env.prepare` kept `game/syw2plus_original.exe` at stock SHA; the launched `game/portrait_probe.exe` or `game/g2_ingame_probe.exe` was a *separate copied* old/fixed ESL probe. Each JSON's `source_sha256` is the probe binary identity, not the manifest's stock EXE.

| Axis | Evidence | Judgment |
|---|---|---|
| Stock `save006.dat`, two available idle portraits | Reference/held/fixed all made both clicks move camera; `local/runtime/g2_portrait_compare_*/*/output/portrait_probe.json` | Low-slot control PASS; does not reproduce user's high-slot failure |
| Explicit synthetic high-slot producer 4092, same visible portrait | Held camera `[49,159]→[49,159]`; fixed `[49,159]→[158,95]`; `local/runtime/g2_portrait_synthetic_*/*/output/portrait_probe.json` | Confirmed old regression and local correction for this path; fixture is synthetic, not natural recruitment |
| Fresh new-game high-slot input | Corrected worker selected/moved; HQ selected/production completed; ESC and cleanup; `local/runtime/g2_portraitfix_smoke/*/output/g2_ingame_probe.json` | Narrow smoke PASS |
| Fresh new-game high-slot save/reload | Private `save/save001.dat`, active slots 4089–4092 identical existence/ID before/after; `local/runtime/g2_portrait_roundtrip/*/output/g2_ingame_probe.json` | Four-unit early-game roundtrip PASS |
| Same-process restart | Unused high-slot age sentinel `0x4444` cleared after confirmed restart; PS3 re-entered; `local/runtime/g2_portrait_restart_probe2/*/output/g2_ingame_probe.json` | Narrow reset PASS |

## Additional audit: false positives and unresolved risks

An independent 1200-site read-only scan initially flagged five `0x0089A388` references as stale `unit_age` pointers. Cross-checking their index formula (`unit_kind + owner*200`) and the layout boundary showed that `0x0089A388` is the adjacent per-kind count table, not the moved age array. **Do not patch those sites.** Another 1200 loop at `0x00422DC7` invokes a no-op callee chain, and `0x004A3222` clearing only old arrays did not reproduce live high-slot staleness under the tested load/restart paths. It remains a static coverage question, not proven safe in all paths; no writer trace was collected. The first load-reset probe's `RESET_FAIL` misclassified nonzero age in *dead* slots (existence/ID zero), while the first restart probe stopped at a confirmation dialog (PS23) before restart. Neither failed run is product-failure evidence.

Post-patch read-only same-session audit independently confirmed the three exact edits and guards, the five per-kind-table false positives, and the probe-vs-stock manifest distinction. This does **not** count as the required next-new-session independent acceptance review.

The owner-count `500` edit is the **normal-new-game per-owner roster seed/policy**, not a claim that every defensive 1200-count check was changed; e.g. `0x0043EE37` remains 1200. Unproven: naturally recruiting a general in a fresh high-slot game; long-duration behavior; 8 simultaneously active players at supply5000; high-slot producer save/load after recruitment; remove/reuse under heavy churn; multiplayer sync; the separately named fixed-start ESL2606 variant. Therefore **corrected candidate remains private/HOLD**, not a G2 product PASS or user-approved milestone. The user may supply their exact save/screenshot for natural-path reproduction, but absence does not turn synthetic evidence into natural evidence.
