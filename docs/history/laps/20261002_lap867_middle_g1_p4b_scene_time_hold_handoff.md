# 2026-10-02 | lap867 | G1 W70 P4b scene-time independent review — HOLD

- 역할: 사용자 지정 middle(진단·계획·확인), Codex. 실제 세션 모델 ID/effort는 노출되지 않아 Sol/Opus/high 실행을 주장하지 않는다. 게임/하네스/validator 구현·빌드·새 게임 실행·커밋·subagent 모두0.
- 순서: PROMPT①~⑥, AGENTS, INBOX 최신 지시/APPROVALS 반려, STATUS 전체, DESIGN1~4, MODEL_ROUTING, P4b 카드·주소 문서, lap866 기록·marker·r4/r5 원문을 읽었다. lap counter867 읽기만. STOP 파일 없음.
- 가설/측정식: 같은 save006·DOWN→RIGHT 뒤 scene parity를 동일 simulation 시점으로 비교했는지 확인한다. PASS에는 같은 입력·각 카메라·scene 및 Scale2x/coverage·source/cleanup이 필요하다. 시점 불일치로 직접 원인을 분리할 수 없으면 HOLD·승격하며 fresh pair/C/P5/G1 마감 금지.
- 원본: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 새 read-only 재해시. 비합성 fixture `Syw2plus_re/Syw2plus/save/save006.dat` SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 새 재해시. loaded558 unit·8 player records는 활성8인 부하 증명이 아니다.
- 실행 근거는 이전 private Wine/Xvfb pair다. 화면/입력 결과에 대한 새 visual verdict 없음. 현재 private game 사본 양쪽 없음·원문 cleanup.ok true 확인, prefix/raw/manifest는 보존한다.

## 독립 재계산

원문 root: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap866_p4b_scroll_ack_{r4,r5}/`.
재계산 artifact와 실행 스크립트: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap867_middle_p4b_review/{recomputed.json,recalculate.py}`.
명령: `PYTHONPATH=. .venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261002_lap867_middle_p4b_review/recalculate.py`.
artifact SHA `3e53190eb8bf40a49f418d6a29bb160bcceb229fe6ec3eb1241fac5dbf5c4909`.
helper의 첫2회는 출력 전 경로 오류(repo.parent.parent/원본 save 위치 추측)로 실패했으며 fixture.source_root와 source를 읽어 바로 수정·재실행했다. 제품/게이트 실패가 아니며 설명되지 않은 실패로 세지 않는다.

| run/key | baseline stable tick → wait end | candidate stable tick → wait end | scene units B/C | equality |
|---|---|---|---:|---|
| r4 DOWN |24587→24617 (+30)|24616→UNAVAILABLE|561/563|false|
| r4 RIGHT |24623→24653 (+30)|24647→UNAVAILABLE|563/563|true|
| r5 DOWN |24614→24650 (+36)|24619→24655 (+36)|563/563|true|
| r5 RIGHT |24656→24692 (+36)|24674→24710 (+36)|564/566|false|

- Loaded scenes match (558/558) in both runs. r4 DOWN candidate-only tuples `(slot,type,owner,internal_id)` are `(35,102,2,983075)` and `(36,7,5,917540)`; owner2 cap is 2100/2300. RIGHT/final match. r5 RIGHT/final candidate-only tuples are `(32,111,0,131104)` and `(33,111,0,65569)`; all other unit identity tuples and player identities match. The two runs differ in distinct records.
- r5 pre-input waits are B24579→24609 / C24583→24613; loaded snapshot ticks B24572/C24574. Each wait PASS proves arrival at its own target, without proving cross-lane equal time.
- r5 RIGHT candidate needs19 stability samples, with repeated/skipped ticks; baseline needs6. The stability counter resets on duplicate ticks, so polling cadence can extend this barrier. This is an observed mechanism; its direct causal relationship to the extra2 unit records remains UNKNOWN.
- r5 ready/keydown/keyup/exact-one-step cameras PASS: both lanes `[158,101]→[159,102]→[160,101]`. Camera parity does not resolve scene HOLD.
- Independently extracted30 PS3 presents after each candidate transition: lower-medians r4 DOWN/RIGHT365287/353639, r5 DOWN/RIGHT365287/353683. Arrays match probe records element by element. Unsupported/outside diff are0 throughout every window; move deltas1/512, transfer deltas31/31(r4),31/30(r5). Coverage≥264000 and≥key-before×0.9 pass.
- r5 first40 fixed-camera PS3 presents give first20/last20 medians337648.5/355734, persistence PASS. Unmodified Scale2x validator rerun PASS: r4 total993 (PS3 786), r5 total1017 (PS3 813). lap866's “937 present” is a transcription error, corrected in an appended note; raw SHA matches.
- r5 subsequent selection is UNKNOWN in both lanes (count0, expected slot151), drag selects slot278 in both and PASS. input_effect_comparison remains HOLD; equal UNKNOWN is not full input PASS. No production-mapping scope expansion.

|원문|SHA256|
|---|---|
|r4 pair|c07ea2c0d78aa5a440f8a19ab5c9679051ccb2010f97badcca4ae1e6c78529ed|
|r4 baseline raw|006ed2326981c505433ebf6f2850325eb3dd2e50c503c9ffbff075beaade917f|
|r4 candidate raw|f47a62601efc5c3f46a820e08be812ffab37875bc179d877f3f284f5aad3b826|
|r5 pair|5349b4288e3e056a95832f5e327eae9d5fc5af9742214f676f94faf0fab2b1f4|
|r5 baseline raw|c3eabf685e581419d83af6290fb21d36b17dfa3b9634c7008f84525fe93a23b6|
|r5 candidate raw|ae2c8fbcfafa499df3aa436af2c42b71726b0b9d83b020a2b113701644104f07|
|r5 DLL|b03ddac8afca33b211008579f80012ab28ceafd77c8abd54558250e929a47828|

- DLL matches build manifest; all42 original_stub_inputs match current source SHA. Probe/test/C bridge SHAs match lap866 record. Artifact holds47 source snapshots for final recheck. No rebuild or new generated-transform/install-rollback runtime validation.

## 판정과 work handoff

**HOLD: equal simulation time is unproven; product divergence cause UNKNOWN.** Confirmed measurement defect: `tools/g1_saved_scene_probe.py:1193` uses lane-local stable_tick+36 after a candidate-only coverage wait, then drops snapshot tick via `state(pid,True)`→`_scene_identity()`. `runtime_driver.state:290` reads tick first, then players/existence/individual units sequentially, without an end-tick/coherence check. window.end_tick is not the scene-read end tick. Equal deltas, cameras, or some equal scenes do not prove equal ticks. Old trace.game_tick is a time value; do not substitute it for simulation tick or accumulate across load rewind.

Escalated middle should confirm this evidence and the following narrow work scope, without another broad plan or game implementation:

1. **Work edits only `tools/g1_saved_scene_probe.py` and its tests.** Keep EXE, HD/DLL implementation, validators/thresholds, shared runtime_driver, G2/G5 unchanged. Keep existing scene identity and separately retain actual detailed-snapshot sim_tick_before/after, monotonic_before/after, PS3/camera. Tick/PS/camera change during read→INCOHERENT/INVALID; never filter newly created/dead tuples to obtain equality.
2. Preregister common input and common post-action observation ticks on the same save's absolute simulation axis. Retain same DOWN→RIGHT order and exact-one-step cameras. Coverage collection must not determine scene timing; compute it offline from raw. DOWN/RIGHT/final require common-tick coherent snapshots and complete scene/player diffs. Timeout/missed target/incoherent read→INVALID/HOLD; lane-local+36 or tolerance windows cannot certify equality. No game-memory writes or new gdb dependency.
3. Feasibility of coherent common-tick capture with current read cost is unverified. First bound batch reads/faster polling with tick brackets; if unavailable, report measured duration/cross-tick evidence. Do not assume pause input works. Any suspension scheme first needs private-target ownership, proven stationary tick and exception recovery; this review does not authorize a new suspension implementation.
4. Regression requirements: different lane starts with equal deltas must be rejected; coverage wait must not shift snapshot time; cross-tick/missed-target reads must be rejected; same-tick unit divergence must HOLD. Next work immediately repairs→new gdb-free private save006 pair (Python-only, no DLL rebuild needed), preserving old raw. Traceable defects follow PROMPT③ repair/rerun.
5. Coherent same-tick divergence→preserve changed/common/new/dead/player records and escalate product diagnosis. Equality would resolve only this timing ambiguity. Full B' criteria and independent middle review remain required; C fresh3/P5/G1 user milestone remain unapproved.

## 변경·검증·종료

- Changes only this record, STATUS, APPROVALS, ESCALATE_SOL, prior-marker full archive and appended lap866 numerical correction; temp receives read-only recalculation script/artifact. Game/source/raw edits0, commits0. Prior marker byte-exact archive: `docs/history/20261002_lap867_prior_lap866_escalate_sol_archive.md`.
- Fresh `make doctor`: protected original verified; optional runtime manifest absent, runtime.ok=false is not new runtime PASS. `make lint`/`make typecheck` PASS (10 files). Focused `.venv/bin/python -m pytest tests/test_g1_saved_scene_probe.py tests/test_g1_hd_scale2x_probe.py -q`: **26 passed in0.10s**.
- Full `make check`/new build/new runtime **SKIP** under user's instruction to preserve/escalate/end on unclear or conflicting implementation evidence. This user instruction overrides patch-validation skill's `Run make doctor then make check`. Read lap866 full log:1235passed/5skipped/896.35s, exit0; it is not a current document-fingerprint PASS.
- Final safety/context/scoped whitespace/source invariance results go only into STATUS. Current queue remains solely in STATUS. Preserve ESCALATE_SOL for escalated middle to confirm work boundary; product HOLD, no milestone closure.
