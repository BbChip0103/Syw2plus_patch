# lap600 work — W50R inner-slot audit blocked before trace

- 날짜/lap: 2026-09-25 KST / lap600
- 목표: G1 W50R audit-only fresh 정확히 1회. E/L inner source·cache·guard, owner/path, native `GetProcAddress` 기준값을 읽고 R1~R4로 분류한다.
- 가설: DxWrapper inner lazy chain이 early window에서 Wine `d3d9.dll!Direct3DCreate9`를 가리키며, audit-only 기록으로 후속 CAS 가능성을 판정할 수 있다.
- 변경 파일: `tools/inmm_stub/final_d3d9_trace.c`, `tests/test_final_d3d9_trace.py`.
- 구현: inner RVA `0x1BAC60/0x1BACC0/0x1BACC4`, rebased old-bytes gate `0xA969/0xA992`, E/L read-only audit, pointer owner/path 및 native export 기록, audit early probe를 추가했다. audit 경로에는 `LoadLibrary`와 CAS가 없다. 기본 경로의 guard/CAS 조건은 유지했다.
- 원본 SHA: EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; DxWrapper `96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe`; ddraw `3bc7230d1a6023a8fc0ea52b18d7edda94fcb4c0ae3d178f6e1577d68a62bd19`; syw2x `61ef47b28df8aa59059861d28070d5352bb31b3398315d91b80efc2631bf7228`.
- 후보 SHA: C `24a2ef669d5b3bef29cc39d5332d3dac880b412aa35923e686997ccc776cd531`; test `684f4893506c527dc97140dd565018208377f2640b7abd621fa1d4857ddb8241`; bridge `_inmm.dll` `75c918b96e692bbedcf479eb03d142c41460edc278f90316651f66e100428fd0`.
- 실행 명령: `pytest -q tests/test_final_d3d9_trace.py` → `15 passed`; `make -C tools/inmm_stub` → PE32 bridge build exit0(기존 일반 cast 경고만); prepare는 `local/runtime/w50r_lap600_runtime_final/20260925_113137_2778155_0/manifest.json`으로 fresh private copy를 만들었다.
- fresh 실행: `.venv/bin/python -m tools.runtime_env g1-presentation-trace --manifest local/runtime/w50r_lap600_runtime_final/20260925_113137_2778155_0/manifest.json --screen 1600x1200x24 --timeout 90 --win32-close-helper /tmp/syw2plus_lap600_close/win32_close_helper.exe --dxwrapper-2x` (audit env는 `INMM_FINAL_D3D9_TRACE=1 INMM_FINAL_D3D9_AUDIT_ONLY=1 INMM_FINAL_D3D9_WINE_REBASED_HEADER=1`).
- 결과: **FAIL / BLOCKED(harness_import)**. 게임 시작·PS9/PS7/PS5/PS3·E/L trace·capture는 성립하지 않았다. 실행 중 `ModuleNotFoundError: No module named 'patches'`가 `runtime_env.py:7945`에서 발생했고, output verdict는 `BLOCKED`, `screenshots=[]`, `inputs=[]`, evidence SHA `4bcef765c4aa1d9a2831a398b829c3f2d752e35c4c2427804d362ba0010a6845`, verdict SHA `33d6c9b9ee767be3fd602fa5966df17a2c2aa23da6866b5e2ae70f5d5ae347ac`이다.
- cleanup: owned launchers/Xvfb/prefix processes는 0으로 확인됐으나 `wineserver -k` exit1 및 `dxwrapper_config_restored=false`가 evidence에 남았다. private runtime만 대상으로 하며 원본/참고 저장소는 불변이다. prefix/output은 삭제하지 않고 보존했다.
- 검증: `make check`는 필수 fresh 검증 실패 후 실행하지 않음(SKIP). G1 PASS/R1~R4/W50S/G2·G4 판정 아님. 새 캡처/inner raw 0.
- 다음: 승격 작업자가 현재 보존된 manifest/evidence와 실행 환경의 import/cleanup 계약을 독립 검수하고, fresh 재실행 허용 여부와 W50R disposition을 판정해야 한다. 이 세션은 재시도하지 않는다.
