Role handoff: fresh middle independent review requested (lap1299 work).

Scope completed: H-TR2614G1 staging only. No milestone/user approval, delivery, commit, or whole `make check` was performed. The staged drop-in overlay is under:
`../temp/Syw2plus_patch/20261014_tr2614g1/user_test_staging/`

Review these independent claims before root proceeds:
1. Original ESL2614 EXE SHA `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf` remains unchanged; source is read-only.
2. `winmm.dll` staged SHA `3976fa88070bbea192700d7a7e9034a67130410e7074bc1bb2431fa63f9c59e4`. It was rebuilt from 65 DLL build inputs matching lap1296's recorded source. The prior tested candidate SHA `0e5ef5fdb1b191957ad61e5c5976271a82c19156028f0b068722f770b4f9d728` is no longer available as a file, so work ran this new SHA once in an isolated 2614 new-game display probe. Result SHA `a157f7ccb5566ef4973ba878dba0d11f2070df3daf23d3b0db4d2630e4603a82`: PASS, PS3 60.8s/1217 presents, trace drop0, cleanup PASS, game copy removed.
3. HD input had 782 files; 773 staged. Nine changed-source HD derivatives were excluded; current 2614 original SHA and excluded HD SHA are in `manifest.json`. Independently verify all 777 `SHA256SUMS` entries.
4. `operator_helpers/` contains two optional BAT helpers only; the drop-in payload is DLL + 773 HD files. DxWnd behavior is explicitly unverified. No user-facing txt or EXE is included.
5. Targeted tests 276 passed; lint/typecheck/doctor exit0. Doctor's optional generic runtime manifest is absent, but the run's private manifest/cleanup is recorded. Do not repeat the same candidate run unless review finds a material conflict.

After scoped PASS, root should freeze the candidate and run same-source `make check` once before asking the user whether to deliver. Windows/audio/user G1 approval remains open.

Record: `docs/history/laps/20261014_lap1299_work_g1_tr2614_staging.md`
