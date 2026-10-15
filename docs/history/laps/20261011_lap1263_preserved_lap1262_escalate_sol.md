# lap1262 work escalation — conflicting silhouette evidence

Reason for escalation: the latest root instruction in `docs/feedback/INBOX.md` says the four opaque pixels in `fnt/tree_plus.spr.hd/0000.idx8` lie outside the original silhouette and directs transparent cleanup plus a regression test. The fresh lap1261 middle report confirms four runtime-mask/sidecar mismatches but explicitly says the available evidence does not establish that they are outside the original full silhouette (or distinguish clipping semantics). This is a substantive implementation-evidence conflict, not a transcription issue.

Evidence to review:
- `docs/history/laps/20261011_lap1260_work_g1_hd_reject_and_variant_layout_handoff.md`
- `docs/history/laps/20261011_lap1261_middle_g1_variant_display_boundary_handoff.md`
- `analysis/memory_maps/g1_esl2613_g2_variant_display_boundary_lap1261.md`
- middle evidence JSON SHA256 `77e58803e1ac16f4800230e18c9f4537e50d565111fb247a38328bb49cdd5062`
- raw key log SHA256 `84eaef270355bd914012545a0dcc0266cc16145291a30241dd2118c191a9962f`

Required Sol decision: independently compare the four identified pixels against the exact source frame and its palette/clipping/identity semantics; decide whether converter cleanup is technically justified and state the minimal allowed transform/test. If that cannot be established, keep the sidecar unchanged and retain the rejection. Also confirm the work ordering after this decision; lap1261 separately authorized a bounded display-only G1 variant probe.

Work status: no code, test, sidecar, or variant executable changed in lap1262; no game/build/test run; no commit or delivery. Existing uncommitted changes and raw evidence are preserved. Lap record: `docs/history/laps/20261011_lap1262_work_escalate_silhouette_evidence.md`. STATUS records one blocker and the Sol handoff.
