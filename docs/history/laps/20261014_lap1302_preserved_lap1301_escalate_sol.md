kind=middle-review-handoff
lap=1301
role=work
target=Sol fresh independent review
scope=H-HDGUARD only; no delivery or milestone approval
record=docs/history/laps/20261014_lap1301_work_g1_hdguard.md

Review the current uncommitted native `_hd` source-hash index and DLL guard. Confirm converter entries map to the emitted `_hd` relative path and SHA-256 of the exact original bytes; inspect strict missing/corrupt-index behavior, path matching, whole-file streaming hash, and the portable SHA implementation. Recompute the preserved ESL2614 trial evidence: official EXE SHA ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf, current DLL SHA 1798913f3ef333bf1cf71caf25714493adf34a3564dae2d42441f227f778001b, mismatch manifest entry char/eaglec1_hd.Spr, runtime hd_source_guard_rejects=1 / matching sidecar hd_pack_hits=391, PS3 60.906 seconds/1216 presents, drop/overflow 0, trace close and cleanup PASS. Raw: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/20261014_hdg1_guard_trial/run_artifacts_r2/soak/candidate/trace_raw.jsonl; result: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/20261014_hdg1_guard_trial/run_artifacts_r2/g1-esl2614-result.json.

Related tests were 129 passed; lint/typecheck and `make -C tools/inmm_stub -B default-on-winmm` passed. Do not rerun full `make check`, rebuild a delivery candidate, or mark G1 complete. The latest APPROVALS legacy2608 Windows failure is a separate, newly reported issue for root to prioritize after this required review; do not merge its evidence with the 2614 trial.
