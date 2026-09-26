# 2026-09-11 | lap115 이후 | STATUS compaction 기록

`docs/STATUS.md`가 160줄에 도달해 다음 work/runtime 기록의 안전 여유가 부족했다. 최신 lap113~114
판정과 다음 한 가지는 유지하고, 이미 개별 history가 있는 이전 상세를 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `123ddefd0462e0a13fb15a4802cf581c8b6c1211b0dc037bcf1cfa3d246ef086`
- 각 lap 원문과 앞선 compaction 기록은 `docs/history/laps/`에 보존된다.
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 상단 요약

lap111 Sol 중간 독립 진단은 lap110 fresh trace의 PS40/tick0 정지 원인을 확정했다.
`DirectDrawCreateEx`의 실제 ABI/원본 caller는 `(GUID*, LPVOID*, REFIID, IUnknown*)`인데 bridge가
2·3번째 인자를 반대로 선언했다. 반환 뒤 expected IID 첫 DWORD `0x15E65EC0`을 객체로 오인해
DLL fault RVA `0xA90D`에서 vtable read fault를 냈으며 game log/runtime 주소와 정확히 일치한다.
판정은 REVISE(root cause confirmed)였으며 lap112에서 문서 길이 상태와 필수 게이트를 회복했다. lap113
수리 후에도 새 Sol/high 독립 검수와 사용자 마일스톤 전까지 G1/M1은 미완료다.

lap110 Luna 실무 수리는 typed vtable/IAT 분리/원 함수 연결/상한·validator·첫 input gate를 구현해
Fast를 통과했지만 native API signature를 회귀 계약으로 묶지 않아 위 ABI 결함을 놓쳤다. 보존 raw는
install complete와 DirectDrawCreateEx 1건뿐이고 surface/present/capture는 없다.

## 이동한 blocker 상세

- lap111은 lap110 PS40/tick0의 충분 원인을 DirectDrawCreateEx arg2/arg3 ABI 역전으로 확정했다.
  원본 caller/IID bytes, source와 trace 값, relocated DLL fault instruction, Wine read fault가 일치한다.
  lap113 수리 전 근거이며 synthetic validator PASS만으로 native ABI 회귀를 닫지 않았다.
- lap105 보고상 G1 presentation probe는 두 고정 원본에서 IAT/direct-xref와 old bytes는 일치했지만,
  `+0x14` 49개·`+0x2c` 14개 generic 후보 중 800×600→1600×1200 rectangle의 unique writer/Flip
  edge를 찾지 못해 **CONCRETE BLOCKER**다. 구현·runtime 재실행 없이 `loop/ESCALATE_SOL`로
  Astra/high architecture handoff를 남겼다. lap106은 원문을 보존하고 이 handoff의 역할과
  조사 합격 기준만 정정했다. 수치/바이트/runtime의 새 독립 컨펌은 없으며 구현 금지는 유지한다.
- lap107은 올바른 PE `.text` mapping으로 lap105의 `+0x14` 49개/`+0x2c` 14개와 8개 old bytes를
  독립 재현했다. lap73 raw artifact hash/cleanup/1600×1200 root/800×600 content도 재확인했으나
  `g1_baseline.json.boundary=null`이고 repo에 DirectDraw COM trace가 없다. generic 후보는 더 세지
  않고 다음 측정 변경을 trace harness로 제한한다. diagnostic bridge side effect는 별도 위험이다.
- lap108은 DirectDraw trace 모듈/validator/runtime command를 구현했다. targeted **67 passed**,
  `make check` **143 passed**, Ruff/compileall/mypy/context/safety와 doctor-runtime `ok=true`다.
  새 run `local/runtime/20260911_130656_1056206_0`의 trace install은 `runtime_contract`에서
  실패했고 identity/present event는 없다. `1600x1200` root/`800x600` content/PS9 capture는
  있었지만 후속 xdotool도 timeout(exit2)이라 BLOCKED이며, 자세한 SHA/명령/cleanup은
  `docs/history/laps/20260911_lap108_luna_g1_presentation_trace_implementation.md`와
  `loop/ESCALATE_SOL`에 보존했다.
- lap109는 DDRAW import `FirstThunk RVA=0xE5018`과 thunk `0x4D7938 -> [0x4E5018]`을 독립
  재추출해 현재 상수 비교가 반드시 실패함을 확인했다. 또한 원 함수 미대입, Surface7 index
  6/8/12/23(헤더상 5/7/11/22), vtable 32/64 copy(실제 30/49), 미사용 reentry/method cap과
  runner/validator fail-closed 누락 때문에 전체 구현을 **REVISE**했다. IAT-only live 재실행 금지다.

## 이동한 검증 상세

- lap112는 `docs/STATUS.md` 139줄과 SHA를 확인하고, `bash checks/safety.sh check`
  `SAFETY_PASS`, `make check` **145 passed**, Ruff/compileall/mypy/context PASS를 재현했다. 문서·이력만
  갱신했으며 source/private/candidate/runtime/game/fixture는 SKIP이고 G1/M1·사용자 승인은 없다.

- lap111은 원본/private SHA/cmp/PE, import/thunk/caller/IID bytes와 lap110 source/artifact SHA를
  재현해 ABI 역전→raw 잘못된 identity→DLL/Wine fault를 연결했다. 초기 `make check` **145 passed**,
  doctor/safety PASS였으나 문서 갱신 뒤 최종 `make check`는 STATUS **183>180** 때문에
  **13 failed, 132 passed**; 뒤의 safety는 SKIP됐다. 재시도 없이 승격했고 fresh runtime/candidate는 SKIP다.

- lap109는 source/private SHA·cmp·PE와 lap108 artifact SHA를 재현했다. raw validator BLOCKED,
  targeted **67 passed**, `make check` **143 passed**, Ruff/compileall/mypy/context/safety PASS,
  저장소 밖 private C build PASS(DLL SHA `80a80627...`, 기존 경고 유지). 새 runtime/game/capture는
  SKIP이며 기계/build PASS를 runtime 계약 또는 G1 승인으로 승격하지 않는다.

- lap110은 repair card의 typed `IDirectDraw7Vtbl`/`IDirectDrawSurface7Vtbl`(30/49),
  `0x004D7938` thunk와 `0x004E5018` IAT 분리, loader target/original pointer/rollback,
  method 256·event 2048 reserve, strict schema validator, PS9 뒤 첫 input 전 install gate를
  구현했다. targeted **9 passed**, `make check` **145 passed**, fresh private build/safety/doctor
  PASS다. 허용된 fresh trace 1회는 exit2: PS9 미도달, 마지막 `ps=40,tick=0`; raw trace는
  install 2건과 `direct_draw_create_ex` 1건뿐이며 IID raw는
  `01E6D080-0000-0000-0000-000000000000`이다. surface/present/PS3 capture는 없고 cleanup은
  PASS다. 이 세션에서 재시도하지 않는다.

## 이동한 lap108~112 목록

- lap108: `docs/history/laps/20260911_lap108_luna_g1_presentation_trace_implementation.md`.
- lap109: `docs/history/laps/20260911_lap109_sol_g1_presentation_trace_confirmation.md`.
- lap110: `docs/history/laps/20260911_lap110_luna_g1_presentation_trace_repair_and_runtime_block.md`.
- lap111: `docs/history/laps/20260911_lap111_sol_g1_presentation_trace_runtime_diagnosis.md`.
- lap112: `docs/history/laps/20260911_lap112_worker_status_gate_recovery.md`.
