# 2026-09-11 | lap 154 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Codex hands-on work tier / gpt-5.6-luna / high.
- 가설 / 사용자 관찰: 승인 candidate `f0ce…6785`를 새 private copy의 `dxwrapper.ini`에 설치하고
  해당 실행만 `ddraw=n,b`로 native private `ddraw.dll`을 로드하면 logical 800×600을 유지하면서
  physical client 1600×1200, 입력 PS9→PS7→PS3 및 기존 finalization이 통과한다.
- 예상 PASS / FAIL 조건: config install/loaded module, 2x client/scale, unscaled input,
  summary 1/process exit/DLL detach/validator/owned cleanup 및 byte-exact restore.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `patches/resolution/dxwrapper_config.py` `48d61a6c…37cbaa`,
  `patches/resolution/test_dxwrapper_config.py` `e4cf7ae4…2e1d04`,
  `tools/runtime_env.py` `05a6054e…01cf4b`, `tests/test_runtime_env.py` `782f74eb…2422f`;
  commit 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  original EXE `b56986e0…c08a8ac`; ini old `918e7043…aeea5a2`, candidate
  `f0ce9e64…2566785`; new private runtime `20260911_200415_300054_0`, new prefix/display,
  diagnostic bridge, default two-player random game; G2~G4 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: fresh helper/bridge build under
  `/tmp/syw2plus_lap154.yqZjnb`; prepare with default source; runtime check/doctor-runtime;
  exactly one `g1-presentation-trace ... --dxwrapper-2x`. Evidence root
  `local/runtime/20260911_200415_300054_0/output/g1_presentation_trace`; raw
  `8944ada…1871d9f`, evidence `905effd…7c221e`, provenance `163cdb0…6808f5d`,
  verdict `5e9903a…d709ca`; five 1600×1200 PNG captures under shared temp, PS3 capture
  `122805b6832fda0c865a8e6415816760b45568ee0475e9f71451147e3d36a14f`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): candidate install and loaded private ddraw PASS;
  logical `[800,600]`, client `[1600,1200]`, scale `[2,2]`, unscaled `(184,560)`, PS9→PS7→PS3,
  capture PASS; installed ini restored to old SHA and sidecars removed PASS. Finalization
  `event_count=384`, summary 0, process_exited false, timeout 90s → **BLOCKED**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: targeted 91 PASS; `make check` 182 PASS;
  Ruff/compileall/mypy/context/safety PASS; runtime check and doctor-runtime PASS. Cleanup PASS.
  Native dxwrapper path after PS3 does not produce final summary/exit; cause not yet determined.
  No middle confirmation or user approval; G1~G4 product completion remains unverified.
- 다음 한 가지: Sol/Opus middle tier가 raw 384-event trace와 previous 651-event baseline을
  독립 비교해 native dxwrapper finalization hang versus trace observability defect를 판정하고,
  승인된 단일 probe를 지정할 때까지 재실행하지 않는다.
