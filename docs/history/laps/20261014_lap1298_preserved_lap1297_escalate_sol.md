lap1297 work requests a fresh middle/Sol independent review of the scoped G1-off/on MCI comparison.

Review only the preserved lap record and artifacts:
- `docs/history/laps/20261014_lap1297_work_g1_mci_pair.md`
- `../temp/Syw2plus_patch/captures/20261014_165000_lap1297_mci_pair/g1-esl2614-result.json`
- Both lane `probe-result.json`, `trace_raw.jsonl`, private-prefix `inmm_state_log.jsonl`, `inmm_stub.log`, and empty `inmm_mci_log.jsonl` files listed in the lap record.

Verify the pinned EXE/proxy SHAs, that the same proxy logged both conditions, off 800x600 and render flags disabled, on 1600x1200, and the empty MCI logs. Keep the scoped conclusion to 0 calls observed in these conditions. The overall runner is HOLD because off has no PS3 present dwell coverage; the 60-second off dwell was configured but not certified by present trace. No rerun is requested unless independent review finds a concrete evidence conflict. Music playback, Windows/DxWnd and G1 milestone approval remain unknown.
