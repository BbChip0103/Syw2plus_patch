# 2026-09-11 21:14 KST | lap 164 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
- 가설 / 사용자 관찰: close 이후 게임이 계속 살아 있고 DirectDraw 호출이 없는 현상을 finalization
  `tick` 증가 여부로 분기한다. tick 정지면 wrapper/driver 경로 후보, 증가면 close 의미론 후보.
- 예상 PASS / FAIL 조건: 새 private runtime에서 `tick` 표본의 첫/마지막/단조성을 확보하고 process,
  close, cleanup을 함께 판정한다. 필수 runtime이 정상 finalization하지 않으면 BLOCKED로 승격한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품/도구/테스트 코드 변경 0.
  이번 lap 기록 파일은 `loop/ESCALATE_SOL`, 이 문서, `docs/STATUS.md`이며 커밋 없음
  (`LOOP_ALLOW_COMMITS` 미설정). `tools/runtime_env.py` SHA
  `f05b4c1c8e77f07a2b90a8fb6c833444ca090691531c2f6d7a91fb9cbc1750c8`, 테스트 SHA
  `9de4d1e68f0e68e503474446c0a38575d963034136e164ae4eacd5830c616ebd`로 이전 바이트와 동일.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 EXE
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; dxwrapper source
  `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`, candidate
  `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`; bridge
  `5bb790acdf841f806e55ddbfc89050bc13c422ae7dfe30a5fb3c0d05e86f3ae8`; helper
  `7f74f168ce1787bc767803b085109cef73c8f3c35d810299dfa755a3bfc88d21`. display `:91`, private
  win32 prefix, 1600x1200x24 output / 800x600 logical, default two-player random-game fixture.
  G2~G4 부하·군대·멀티 조건은 아님.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 -m tools.win32_close_fixture build --out-dir /tmp/syw2plus_lap164_build.sbNB9i/helper`
    RC0; helper PE32.
  - `python3 patches/population/build_runtime_bridge.py --out-dir /tmp/syw2plus_lap164_build.sbNB9i/bridge`
    RC0; bridge PE32.
  - `make check`: `190 passed in 35.16s`, ruff/compileall/mypy/context limits PASS.
  - `bash checks/safety.sh check`: `SAFETY_PASS`.
  - `.venv/bin/python tools/runtime_env.py prepare --bridge /tmp/syw2plus_lap164_build.sbNB9i/bridge/_inmm.dll --timeout 60`
    RC0, run `local/runtime/20260911_211043_913631_0`; manifest check RC0.
  - `.venv/bin/python tools/runtime_env.py g1-presentation-trace --manifest
    local/runtime/20260911_211043_913631_0/manifest.json --screen 1600x1200x24 --timeout 90
    --win32-close-helper /tmp/syw2plus_lap164_build.sbNB9i/helper/win32_close_helper.exe --dxwrapper-2x`
    **RC2/BLOCKED**, clean finalization timeout, process_exited false, summary 0, event 384.
  - PS3 capture: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260911_211120_20260911_211043_913631_0-presentation_915444_ps3_scene_1789128680509213475.png`
    (actual output path is recorded in evidence; captured PNG SHA
    `af94e7982a133c78f6869d2ca171e5e3bddedbe9818c5706c902cf7a560b294a`).
  - run manifest/evidence/verdict/provenance/raw/install trace SHA는 `loop/ESCALATE_SOL`에 보존.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - build/prepare/check/safety: PASS.
  - display/input/scene: 1600x1200, logical 800x600, 2x2, `(184,560)`, PS9→PS7→PS3: PASS for
    this diagnostic smoke fixture.
  - finalization reader: 78 samples from 9.341s to 89.583s, `ps=3` all, `tick=16` all; tick is
    constant (no increase/rollback/read error): PASS as measurement, H-candidate as diagnostic result.
  - raw trace: 384 events, `program_state=3` zero, `program_state=2` 30: OBSERVED but conflicts with
    reader PS3 and visible PS3 capture.
  - close transport: PASS; liveness two samples S→R, 36 threads, main tid +310 jiffies vs process
    +320: OBSERVED; summary/normal exit: FAIL/BLOCKED.
  - screenshot: visible game world/HUD at 1600x1200, not black: OBSERVED. This prevents treating the
    raw-trace absence alone as proof of no PS3 rendering.
  - cleanup/config restore/owned process residue: PASS; G1 product completion and milestone approval: NO.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: source/product binaries unmodified, no code
  regression identified. Required finalization failed and evidence has a live-reader/raw-trace/state
  semantic conflict. No second-tier review or user milestone approval. `loop/ESCALATE_SOL` created;
  retry and cause-fix are prohibited for this lap.
- 다음 한 가지: middle tier가 fresh run evidence를 독립 검수해 tick=16 정지, visible PS3 capture,
  reader PS3와 raw trace state mismatch를 판정하고, 그 뒤 EIP/wchan 또는 PS3 dwell 중 다음 probe
  하나만 승인한다.
