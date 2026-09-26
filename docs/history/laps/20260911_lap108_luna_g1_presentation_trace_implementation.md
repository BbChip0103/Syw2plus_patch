# 2026-09-11 | lap108 | Luna/high G1 DirectDraw presentation trace implementation

- 지정 역할/model/effort: 일반 작업자, 실무 Luna/high 범위. 상위 방향·중간 컨펌은 수행하지 않았다.
- 목표/가설: SHA-pinned 원본의 DirectDrawCreateEx IAT와 반환 DD/surface vtable을 환경변수로만
  관측해 PS9→PS3 같은 run의 presentation identity를 연결한다. 구현은 진단 bridge에만 둔다.
- 변경파일: `tools/inmm_stub/direct_draw_trace.c`, `tools/inmm_stub/direct_draw_trace.h`,
  `tools/inmm_stub/Makefile`, `tools/inmm_stub/inmm_stub.c`, `tools/check_g1_presentation_trace.py`,
  `tools/runtime_env.py`, `tests/test_g1_presentation_trace.py`, `Makefile`.
  원본/참고 EXE·DLL·game data·candidate·baseline/golden은 변경하지 않았다.
- 원본/후보 SHA: 두 고정 원본 및 private EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  `cmp=0`, PE32; 후보 없음. bridge `/tmp/syw2_g1_trace_build.jbR3yd/_inmm.dll` SHA
  `2b7a2486c810aaa7b3f6f946f5c15d7605a1d8cb0488e0a5d8932f02da765ddb`.
- 선행 guard: `.text` `0x00401000/0x1000/0xE3AE5`, DirectDraw thunk/caller/mode old bytes가
  계획과 일치. `make check` 전후 원본 보호 검사는 PASS.
- 실행명령: `make -C tools/inmm_stub clean all`(build PASS),
  `.venv/bin/python -m pytest -q tests/test_g1_presentation_trace.py tests/test_runtime_env.py tests/test_project_setup.py`,
  `make check`, `bash checks/safety.sh check`, `runtime_env.py prepare --bridge`,
  `runtime_env.py check`, `make doctor-runtime`, 그리고 지정된
  `runtime_env.py g1-presentation-trace --manifest ... --screen 1600x1200x24 --timeout 90` 1회.
- 기계 수치: targeted `67 passed`; Fast `143 passed`; Ruff/compileall/mypy/context/safety PASS;
  doctor-runtime `ok=true`; live는 exit 2. private root `1600x1200`, content `800x600`,
  PS9 screenshot은 생성. trace는 `install/starting`→`install/failed(runtime_contract)` 2 event,
  DirectDraw identity/present event 없음. 이후 xdotool mousemove 10초 timeout.
- fixture/환경: 새 전체 game copy, 새 Wine win32 prefix, private Xvfb, `ddraw=b`, diagnostic bridge=true,
  default two-player random game, synthetic=false, memory_writes=false, control_bridge=false,
  resource_grant=false. 활성 플레이어/군대 N/A. cleanup `ok=true`, global kill false.
- 판정: **BLOCKED/ESCALATE_SOL**. 현재 결과를 G1 또는 M1 PASS로 승격하지 않는다.
- 다음 행동: Sol/high가 raw trace와 `0x004D7938` jump thunk 대 실제 IAT pointer 계약을
  독립 확인하고 fail-closed 수리 범위를 정한다. 본 세션은 재실행하지 않는다.
