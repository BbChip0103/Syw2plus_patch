# 2026-09-11 | lap 110 | G1 DirectDraw trace repair and runtime block

- 실제 provider/model/effort / 지정 역할: Codex `gpt-5.6-luna`/high, hands-on 실무 작업자.
- 가설 / 사용자 관찰: lap109 REVISE 카드대로 typed DirectDraw7 vtable, thunk/IAT 분리,
  원 함수/rollback, emitter·validator 상한, 첫 input 전 install gate를 수리한다.
- 예상 PASS / FAIL 조건: typed ABI와 원 함수 1회/원복, strict validator·fail-before-input,
  targeted/build/Fast/safety 모두 PASS 후 fresh trace가 PS9→PS3 및 IID→DD→surface→desc→present
  chain을 남겨야 PASS. 필수 gate 실패 또는 PS9 미도달은 BLOCKED이며 재시도하지 않는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `tools/inmm_stub/direct_draw_trace.c`, `tools/check_g1_presentation_trace.py`,
  `tools/runtime_env.py`, `tests/test_g1_presentation_trace.py`; 모두 uncommitted.
  source SHA `3f4758d095067452a890a906b6472c8d03e77a0295a1b6af7202292868113438`,
  validator `541e8448fdbbde5abb910a3ca5e85b5daa2c80322165a6e9e7796258cd0268bd`,
  runtime `c417b9f0a60d7a0ef422657534f90ce51796173d3f8781a365ae71e070a7bfa1`,
  test `3ab4bb24f1c0c7c434080b354cdfbdc72544967ed58e74b54f49111b9f423d66`.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  original/private EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  `cmp=0`, candidate 없음. fresh whole copy, new win32 Wine prefix, private Xvfb `:91`,
  `1600x1200x24`, default two-player random fixture, synthetic=false, memory_writes=false,
  control_bridge=false, resource_grant=false, diagnostic bridge=true. G1 PS9 전이라 활성/군대 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `make -C tools/inmm_stub all`; 저장소 밖 fresh bridge build SHA
  `0ae931603134ce6389aadfedb3efd082a5b74af2a98ad10d4baa284dc3ffbd09`;
  targeted `9 passed`; `make check` `145 passed`; `bash checks/safety.sh check` `SAFETY_PASS`;
  `runtime_env.py check`, `make doctor-runtime` 모두 PASS.
  live: `.venv/bin/python tools/runtime_env.py g1-presentation-trace --manifest
  local/runtime/20260911_133318_1248520_0/manifest.json --screen 1600x1200x24 --timeout 90`, exit2.
  raw `local/runtime/20260911_133318_1248520_0/output/g1_presentation_trace/trace_raw.jsonl`
  SHA `53c53901...`; evidence `9eff73d5...`, verdict `9648917b...`, provenance `14e9a864...`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): build/Fast/safety PASS. Live FAIL/BLOCKED:
  90초 동안 PS9 미도달, 마지막 `ps=40`, `tick=0`, inputs/screenshots 0. Raw trace는
  install starting, install complete, direct_draw_create_ex 1건뿐이다. install은
  `0x004E5018` slot과 `0x004D7938` thunk를 분리했지만 raw IID는
  `01E6D080-0000-0000-0000-000000000000`; surface/present/PS3 capture 없음.
  cleanup `ok=true`, prefix processes `[]`, global kill false. G1/M1 승인 없음.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본/후보/baseline/golden 변경 없음.
  다음 Sol/high는 PS40 startup 정지와 raw IID/ABI provenance를 독립 진단해야 한다. IID 단독
  수정이나 runtime 재실행은 이 marker에서 금지. 사용자 마일스톤 승인 없음.
- 다음 한 가지: 새 승격 작업자가 보존된 raw trace와 game log를 대조해 PS40/tick0 및 IID
  provenance의 원인을 독립 확정하고, 필요하면 새 repair card를 작성한다.
