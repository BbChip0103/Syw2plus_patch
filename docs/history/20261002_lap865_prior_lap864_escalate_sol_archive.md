# lap864 G1 W70 P4b: independent middle review required

Do not start P4 C or mark B' PASS yet. Review the evidence in
`docs/history/laps/20261002_lap864_work_g1_p4b_cache_layer_input_parity_hold.md`
and the exact r4 pair/raw under
`/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_101200_p4b_scroll_r4/`.

The candidate cache-layer gates pass for both movement forms: DOWN uses one
whole-buffer move and has 30-present p50 365,324; RIGHT uses 512 row moves and
has p50 352,704. Both exceed 264,000 and 90% of key-before, with unsupported
move 0, outside diff 0, Scale2x validator PASS, loaded scene equal, source EXE
unchanged, and cleanup PASS.

The paired input parity gate is HOLD: same gdb-free DOWN→RIGHT order and
WM_KEYDOWN/UP receipt, but baseline DOWN moved `[158,101]→[171,114]` (13 cells,
2ms observed hold) while candidate moved `[158,101]→[159,102]` (one cell,
29ms). RIGHT moved one cell in both lanes. The reason is unknown after the
bounded work-lap attempts. Independently inspect the receiver raw and camera
sampling timing, determine whether the baseline result is a harness artifact
or an original/candidate behavior difference, and set the next work condition.
Do not use candidate-only coverage as parity proof and do not start C before
the B' parity disposition. Also state whether the legacy mirror validator's
1203 nearest-oracle errors are expected under the separately passing Scale2x
validator or require an additional unchanged-legacy check.

Evidence: pair `8f0ef603d98e191a6a0113deaa40d7a807674e5a18b1b56809973799525b3a08`;
candidate raw `b54754c6a728404ac5fc1a6b2e2f95eb7f048ee7e06cf1e1180d8170be00f980`;
baseline raw `a9808508e03b638068ade83c1a4c12ddad6f9d0a042e629b5f3a73dd55887662`.
Original SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
