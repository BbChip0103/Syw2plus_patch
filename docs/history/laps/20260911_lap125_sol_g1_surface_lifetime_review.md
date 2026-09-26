# 2026-09-11 | lap 125 | 목표 G1

- 실제 provider/model/effort / 지정 역할: 사용자 지정 중간 tier 진단·계획·확인 역할. 저장소 기본 라우팅은 Codex `gpt-5.6-sol`/high이나 현재 대화 표면은 실제 model ID/effort attestation을 제공하지 않아 exit 0에서 추정하지 않았다. 게임 코드·원본·후보는 수정하지 않았다.
- 가설 / 사용자 관찰: lap124의 seq50 정상 clone 호출 뒤 같은 pointer가 seq54부터 거부된 것은 raw-pointer keyed surface record가 COM 수명 종료를 추적하지 못한 결과이며, Release=0에서 record를 폐기하는 최소 수리 범위와 정확한 회귀를 정할 수 있다.
- 예상 PASS / FAIL 조건: raw/provenance/evidence/verdict SHA 및 seq/count가 handoff와 일치하고, source에서 가능한 decision 변화와 미관측 경계를 분리하며, 게임 재실행 없이 work tier가 실행할 단일 수명주기 수리와 기계 측정식을 정하면 PASS다. source와 raw가 충돌하거나 수리 근거를 좁힐 수 없으면 REVISE/ESCALATE다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 구현 변경 없음. 검수 source는 `surface_reuse_contract.h=24cef29a881c21d4b462e7be3fd631ca46d8b2e1dc0948f8259e899b51e9a3d4`, `direct_draw_trace.c=cf9bc6e5b7fca3a66b58ed3dc0411ea1f3265e0dab1c9a53d3a2ff3ed0c40724`, `test_direct_draw_abi.py=7fc3d4784f5dd9ee041b13975b10098e57eb3d899307095dbb27108eb5ac1abb`, `runtime_env.py=26028b0ab7d45cd601dedc879dbec206f981ad8ed99612b06e51b3f0346e6733`. 기록 시 `docs/STATUS.md=5cb6dcd835aa5f4d90164f899b233edea11d20fc8d5e0490452635fa063bc5fe`, work handoff `fe4ca384d63bdd8b530deaec8c133eb3d828df1a388d13bd2826be8ccfaf3d7c`다. 본 이력도 추가했고 소진 marker `loop/ESCALATE_SOL=389a70bbfcc110cb641206bc87110b1d29719daacef6d27f763a0d1e1ad992b6`은 아래에 원문 보존 후 제거했다. `LOOP_ALLOW_COMMITS=0`, commit/push 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: lap124 보호 원본/private copy SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, bridge `ce73048451a51268489cb96efade4d5257b7f6250961372dc488e833b02f321f`, manifest `local/runtime/20260911_153632_2237875_0/manifest.json`, Xvfb `:91`/1600x1200x24와 diagnostic-only fixture를 read-only 대조했다. 게임·활성 플레이어·지도·군대·제품 후보는 새로 실행하지 않아 SKIP/N/A다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sed`/`nl`/`rg`/`jq`/`sha256sum` 정적·raw 대조; `.venv/bin/python -m pytest -q tests/test_direct_draw_abi.py`; `make check`; `make doctor`; `bash checks/safety.sh check`; raw `trace_raw.jsonl=18e5791f26d8dd8e7758d81f26c3215babd4722e28763eb5eb434e2b62d8f863`, provenance `b425fde7e524b738e9917620db4565bb41f8df00a3849389a5d6f0ac52efc7df`, evidence `f8fcc695f89294b40fd426491744fc41ec3b20351de6aa1549aaba374344ab1a`, verdict `97014d20d41490f6a25e0496afe8e355367588899a0e453045674a08fa1b3b3a`. PNG/runtime/game capture는 만들지 않았다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): raw 79 events/단일 run/thread, install active seq2, seq50 `0x01E6D848` CreateSurface active·49, seq51 GetSurfaceDesc·49, seq52 Blt·49, seq54 첫 install failure, 이후 같은 pointer failed CreateSurface·0이 9회다. install failed 9 + create failed 9 = failed-status 18이며 unique returned surface는 16이다. 기존 ABI targeted **5 passed**; `make check` **162 passed**, Ruff/compileall/mypy/context PASS; doctor top `ok=true`/original verified(현재 root runtime manifest 부재는 optional `runtime.ok=false`), safety `SAFETY_PASS`다. 판정은 **LAP124 FAILURE CONFIRMED / SURFACE LIFETIME CONTRACT REVISE / GAME RUN BLOCKED**다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: current vtable이 stored clone에서 이탈한 것은 강한 정황이나 failure event가 reason/pointer를 합쳐 `Release()==0`과 stored-original 복귀를 직접 관측하지 못했다. 그러므로 Release 수명 추적과 exact failure serialization을 함께 요구하고 raw pointer 동일성만으로 자동 rebind/49 기록은 금지한다. fresh runtime/G1/M1·사용자 승인은 BLOCKED/미승인이다.
- 다음 한 가지: 새 Codex `gpt-5.6-luna`/high work tier가 `docs/plans/20260911_lap125_g1_surface_lifetime_repair_handoff.md`의 허용 범위에서 Release=0 record retirement와 exact failure evidence를 구현·회귀하고 게임은 실행하지 않는다.

## 소진 전 `loop/ESCALATE_SOL` 원문

```text
# lap124 work -> Sol/high G1 fresh runtime failure

reason=the one allowed fresh G1 presentation trace reached the verified DirectDraw install, then failed on a repeated surface identity/clone contract before the first input gate. The mandatory runtime gate therefore failed and G1/M1 cannot be promoted.
classification=FRESH_RUNTIME_INSTALL_GATE_FAIL_SURFACE_REUSE_BLOCKED
stop=Preserve this run's raw/log/evidence/verdict and do not rerun the game, reuse its prefix/display, alter validator constants, patch binaries, commit, or push. The work tier has ended after the required single attempt.

run=
- manifest: local/runtime/20260911_153632_2237875_0/manifest.json
- private game copy and original executable SHA: b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac
- diagnostic bridge SHA: ce73048451a51268489cb96efade4d5257b7f6250961372dc488e833b02f321f
- display: :91, Xvfb 1600x1200x24; prefix was newly created and is now owned-clean
- fixture: new full private copy, default two-player random game, synthetic=false, memory_writes=false, control_bridge=false, resource_grant=false, diagnostic_bridge=true

evidence=
- raw trace: local/runtime/20260911_153632_2237875_0/output/g1_presentation_trace/trace_raw.jsonl
- raw SHA-256: 18e5791f26d8dd8e7758d81f26c3215babd4722e28763eb5eb434e2b62d8f863
- provenance SHA-256: b425fde7e524b738e9917620db4565bb41f8df00a3849389a5d6f0ac52efc7df
- evidence SHA-256: f8fcc695f89294b40fd426491744fc41ec3b20351de6aa1549aaba374344ab1a
- verdict SHA-256: 97014d20d41490f6a25e0496afe8e355367588899a0e453045674a08fa1b3b3a
- event summary: 79 events; install active/complete at seq2; first failure seq54, stage=surface_vtable, reason=reused_surface_identity_or_clone_mismatch; 18 failed events; active present events were blt seq48 and seq52 only; no user input, PS3 capture, final summary, or validator PASS
- cleanup: owned_launchers_stopped=true, xvfb_stopped=true, prefix_processes_after=[], global_kill_used=false, ok=true

required_review=
1. Independently inspect the raw event sequence and confirm that the error is caused by the production diagnostic bridge's repeated surface record/reuse path, not by an invented G1 product result. Preserve the distinction between the initial active install/present events and the later fail-closed surface failures.
2. Review `tools/inmm_stub/direct_draw_trace.c` and `surface_reuse_contract.h` against the observed repeated `returned_surface=0x01E6D848` / install failure sequence. Decide the minimal authorized repair scope and required regression cases; do not rerun this lap's game run.
3. Keep G1/M1 and product approval blocked. A future work run, if explicitly authorized after review, must use a new full copy, new Win32 prefix, unused display, fresh bridge, and the exact one-run rule again.

validation_before_run=
- make check: 162 passed; Ruff/compileall/mypy/context PASS
- make doctor: ok=true, protected original verified
- bash checks/safety.sh check: SAFETY_PASS
- runtime_env.py check and make doctor-runtime: ok=true
```
