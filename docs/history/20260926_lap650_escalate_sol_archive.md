# loop/ESCALATE_SOL 전문 보존 (lap650 strategy 해제 전)

- 원문 SHA256: `a30d048012e99423827c1deff024b4713f07016ca5b2c9b14ed6ff2bccc8158c`, 줄 수: 318
- 해제 사유: lap650 strategy가 lap649 승격 질문(EXE writer 귀속)을 FUN_0041DC40 frame 0x230 부족으로 귀속·FEASIBLE 판정. 상세 `docs/history/laps/20260926_lap650_strategy_g5_consumer_frame_fix.md`.

---

## §178 — lap630 work: **G5 검증 경로 prepare가 디스크 부족으로 중단** (2026-09-25 KST)

최신 INBOX/STATUS의 19:25 운영자 결정에 따라 원본을 먼저 검증된 `tools.runtime_env` 경로로 띄우려 했다. 원본/후보 모두 공통 direct-Wine fault를 이미 기록했으므로, 이번에는 코드나 후보를 추가 수정하지 않고 `prepare → 격리 prefix → bridge chain`의 원본 진입부터 확인하는 범위였다.

- 읽은 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (불변)
- lap629 후보 SHA: `ebd46050cb061a4793bcf9dbc86e196bd71ab45050d881bb13c64258a8c83e8c` (이번 바퀴 미수정)
- 확인한 명령: `.venv/bin/python tools/runtime_env.py prepare --runtime-root local/runtime/g5-lap630-original`
- 결과: `OSError: [Errno 28] No space left on device` at `_new_run()` while creating `local/runtime/g5-lap630-original`; run directory/게임/prefix/bridge는 생성되지 않음.
- 환경: `df -B1` available `13,378,916,352` bytes; `du -sh local/runtime` `269G`; inode pressure는 12%로 원인이 아님.
- 제품 실행: 원본 prepare 이후 단계 0회, G5 후보 prepare/실행 0회, 55기 fixture/드래그/명령 전달/저장로드 0회.
- 변경: 제품 코드·패치·테스트 0. STATUS·이 history·이 승격 파일만 기록. `make check`는 실행하지 않음(직전 lap629의 867 passed는 현재 바퀴 증거가 아님).

### 승격 작업자가 이어서 검증할 것

1. 기존 `local/runtime`와 공유 temp 증거의 보존 필요성을 먼저 확인한다. 과거 런타임을 임의 삭제하지 말고, 안전한 보존/정리 범위 또는 별도 실행 위치를 확정한다.
2. 공간 확보 후 원본을 최신 결정의 `tools.runtime_env prepare` 경로로 새 private copy/prefix/display에서 실행해 PS3 도달 여부를 새 manifest/raw로 확인한다. 실패하면 정확한 로그와 cleanup을 보존하고 원인별로 다시 승격한다.
3. 원본 경로가 성립할 때만 G5 후보 hash/허용 계약을 fail-closed로 연결하고 같은 fixture에서 후보를 실행한다. 후보의 정상 초기화 전에는 55기 드래그, 50기 명령, G5 PASS를 주장하지 않는다.

## §179 — lap631 work: **원본 PS3는 성립했지만 G5 후보 runtime/drag 계약이 없어 승격** (2026-09-25 KST)

lap630의 공간 blocker가 해소된 현재 상태에서, 최신 운영자 지시의 검증된 `tools.runtime_env prepare → private prefix/display → bridge` 경로를 원본에 먼저 적용했다. 원본/참고 저장소는 읽기 전용으로 사용했고 제품 코드·패치·테스트는 수정하지 않았다.

- 디스크 독립 확인: `df -B1` available `227,295,465,472` bytes, `du -sh local/runtime` `73G`, inode 사용 12%. 이전 lap630의 `13,378,916,352` bytes/`269G` 기록과 달라 현재 공간 blocker는 해소된 상태다.
- source 계약: 저장소 내부 `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch/Syw2plus`는 `unsafe source directory`로 거부됐다. `tools/runtime_env.py`의 보호 계약에 맞춰 참고 저장소 `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus`를 사용했고 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`가 일치했다.
- 원본 runtime: `prepare --runtime-root local/runtime/g5-lap631-original --bridge tools/inmm_stub/_inmm.dll --timeout 60` exit0, `check` exit0. manifest `local/runtime/g5-lap631-original/20260925_205009_3887898_0/manifest.json`, private prefix/display, copied original SHA와 bridge SHA `a23dfbcff26f731c04c7a41ff4ff1c9efa62d2963053adae6a49ab8a750dcee2`를 보존했다.
- 원본 실행: `g1-baseline`은 `surface_ps3=true`, `PS5→PS3; tick=2`, last tick `376`, cleanup `ok=true`를 남겼지만 고정 미니맵 단계의 `FAIL_NO_EFFECT`로 exit2/`overall=FAIL`이다. 이 run은 G5 제품 PASS가 아니며, raw·manifest·캡처는 현재 run 디렉터리와 공유 temp에 보존했다.
- 후보 blocker: 보존 후보 `ebd46050cb061a4793bcf9dbc86e196bd71ab45050d881bb13c64258a8c83e8c`는 존재하지만 `runtime_env`의 `check_runtime`가 `syw2plus_original.exe`의 원본 SHA를 강제한다. G5 후보를 선택해 실행하는 CLI/manifest/provenance/50기 drag reader가 현재 없으므로, 후보를 `game.exe`로 우회하거나 manifest를 임의 수정하면 안전·진위 계약을 깨뜨린다.

### 승격 작업자가 이어서 검증할 것

1. G5 후보의 허용 파일명/후보 SHA와 원본 SHA를 함께 기록하는 새 fail-closed runtime contract를 정한다. `check_runtime`의 원본 보호를 약화하지 않는다.
2. 같은 private prefix/display 경로에서 후보 executable을 실제로 선택하는 launch path와 candidate provenance를 구현·회귀 검증한다.
3. 그 뒤에만 55기 자기 소유 living-unit fixture, 원본 count20 대 후보 count50, 51번째 미선택, 50기 이동 명령 raw, canary·cleanup·save/load를 실행한다. 현재 후보 실행과 G5 PASS는 SKIP이다.

판정: **`BLOCKED(candidate_runtime_contract_and_known_harness_tail)`**. 상세 work 기록은 `docs/history/laps/20260925_lap631_work_g5_runtime_candidate_contract_blocked.md`다.

## §180 — lap632 work: **G5 후보는 PS3/55기까지 갔지만 selection fixture/필수 Fast가 막힘** (2026-09-25 KST)

최신 21:05 운영자 결정의 W47 연결 패턴을 새 fail-closed probe `tools/g5_candidate_drag_probe.py`로 구현했다. `prepare()`와 original `check_runtime()`를 먼저 통과시킨 뒤 private `syw2plus_original.exe`에 후보 바이트만 주입하고 후보 SHA/provenance를 별도 기록했다. stock-layout bridge는 G5 storage `0x0108c000`과 겹치지 않는 `0x0066B790` 풀을 사용했다.

- 후보/원본: candidate `ebd46050cb061a4793bcf9dbc86e196bd71ab45050d881bb13c64258a8c83e8c`; protected source `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 실행: fresh private Wine/Xvfb foreground run 6회. r1 type5는 원본 cap1500에서 `fixture_added=42/55`로 중단. r2~r6는 type7/type46과 좌표·미니맵을 조정했고, 최종 r6 type46은 `fixture_added=55`, `used=1120/1500`, PS3, camera `[40,40]`, cleanup residual0/source unchanged를 확보했다.
- G5 관측: final r6 selection `count=1`, raw `0x204ae` (compressed low12 slot `1198`), unique1; 우클릭 후 command raw도 1건뿐이다. count50/51번째 경계·50기 명령·save/load는 검증하지 못했다. 캡처/raw/provenance는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap632_g5_candidate_drag_r6/`에 있다.
- 필수 Fast: `make check`는 **exit2** collection 단계에서 `patches/population/test_g2_esl2606_pool4092_owner500.py`의 import error를 보고했다(889 collected, 1 error). 후속 targeted G5+해당 test는 9 passed였지만 full Fast의 최초 실패를 성공으로 승격하지 않는다. `.venv/bin/ruff`가 없어 직접 lint는 exit127; probe pycompile/mypy follow-imports=skip, safety/context는 PASS.

판정: **`BLOCKED(selection_fixture_visibility_and_fast_gate)`**. G5 후보 실행 계약은 존재하지만 실제 55기 화면 fixture가 드래그에 들어오는 좌표/렌더링 계약이 닫히지 않았고 필수 full Fast도 현재 세션에서 통과하지 않았다.

### 승격 작업자가 이어서 검증할 것

1. 현재 작업 트리에서 full `make check` collection ImportError를 fresh하게 재현하고, ruff 실행기 부재를 환경/설치 상태로 분리한다. 기존 사용자 파일을 삭제·복원하거나 baseline을 갱신하지 않는다.
2. r6 provenance의 55기 live rows와 camera `[40,40]`를 바이트/raw로 독립 재검토해 화면에 보이는 living-unit fixture 좌표와 drag rectangle을 정한다. 후보 compressed selection entry는 `raw & 0xFFF` 규칙을 유지하되 50개를 직접 읽을 때까지 PASS로 쓰지 않는다.
3. 새 private prefix/display에서 원본 count20 대 후보 count50, 51번째 미선택, 50기 이동 raw, canary/cleanup/save-load를 다시 수행한다. 그 전에는 G5 PASS나 사용자 마일스톤 승인을 주장하지 않는다.

## §181 — lap633 work: **필수 `make check`가 SIGTERM으로 완주하지 못해 G5 재실행 중단** (2026-09-25 KST)

lap632 r6의 G5 raw/provenance를 독립 확인했다. 55개 live row는 x `1..177`, y `50..53`으로 분산되어 있고 camera `[40,40]`, selection `0→1(slot1198)`이었다. 따라서 fixture/드래그 사각형 가설은 유지되지만, 원본 동일 fixture 대조나 후보 50기 경계 재실행을 시작하지 않았다.

- 실행 명령: `make check` foreground fresh run.
- 관측: pytest 893개 수집, 15% 진행 후 약 136초 뒤 `make: *** [Makefile:5: test] Terminated`, process exit 143. assertion/collection의 최종 판정과 lint/typecheck는 도달하지 못했다.
- 보조 검사: `python3 checks/context_limits.py`=`CONTEXT_PASS`; `bash checks/safety.sh`=`SAFETY_PASS`.
- 변경: 제품 코드·패치·테스트·원본·후보 0. 상세 `docs/history/laps/20260925_lap633_work_g5_fast_gate_timeout_escalated.md`.

### 승격 작업자가 이어서 검증할 것

1. exit143의 실행기/세션 시간 제한 원인을 먼저 확인하고, 필수 `make check`를 완주할 안전한 foreground 경로를 확정한다. 전체 Fast가 완주되기 전에는 targeted PASS를 전체 PASS로 승격하지 않는다.
2. Fast가 통과하거나 원인이 명확히 보존된 뒤, 새 격리 run에서 동일 fixture를 원본에 먼저 드래그해 count20을 측정한다. 원본 대조가 성립할 때만 후보에서 count50·51번째 미선택·50기 명령 raw를 측정한다.
3. 그 전에는 G5 PASS·50기 명령·save/load·사용자 마일스톤 승인을 주장하지 않는다.

## §182 — lap634 work: **원본 동일 fixture 선행 대조가 count20을 만들지 못해 승격** (2026-09-25 KST)

lap633의 다음 작업 지시대로 후보보다 먼저 원본을 새 private Wine/Xvfb runtime에서 같은 type46×55 engine-seeded fixture로 실행했다. probe에 `--variant original|candidate`를 추가해 원본은 stock selection base `0x00899024`/capacity20을 읽고 후보는 relocated base/capacity50을 읽도록 했으며, 원본/후보 source 계약은 분리하지 않았다.

- 명령: `.venv/bin/python tools/g5_candidate_drag_probe.py --variant original --runtime-root local/runtime/g5-lap634-original --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap634_g5_original_drag`
- 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (before/after 동일). 후보 SHA는 이번 실행에서 설치/실행하지 않음; 보존 후보 `ebd46050cb061a4793bcf9dbc86e196bd71ab45050d881bb13c64258a8c83e8c`.
- runtime: prepare/check PASS, PS3 tick2, `fixture_added=55`, after used `1120/1500`, live57, private cleanup residual0/ok=true. `make doctor` exit0, targeted G5 patch tests 8 passed, probe py_compile PASS.
- 핵심 raw: original stock selection before `count=0`, after `count=1`, raw `0x204ae`, slot1198, unique1; camera after the existing minimap click `[19,90]`; move command raw nonzero1. Full provenance/captures: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap634_g5_original_drag/`.
- 판정: **`BLOCKED(original_fixture_or_camera_contract)`**. 원본 count20이라는 필수 선행 대조가 실패했으므로 후보 50/51 경계, 50기 명령, save/load, fresh `make check`는 SKIP이다. 이를 후보 패치 결함·G5 제품 FAIL·마일스톤 승인으로 해석하지 않는다.

### 승격 작업자가 이어서 검증할 것

1. `probe-result.json`의 55 live rows, before/after 캡처, 입력 순서와 camera `[19,90]`를 독립 재검토해 fixture가 실제 화면 안에 있었는지와 minimap click의 효과를 분리한다.
2. 원본에서 count20을 만들 수 있는 living-unit fixture와 camera/drag rectangle 계약을 먼저 확정하고, 같은 fixture를 후보에 적용한다. 후보 재실행 전에는 G5 PASS나 50기 명령을 주장하지 않는다.
3. 선행 원본 대조가 성립한 뒤에만 fresh `make check`를 실행하고, 이번 바퀴의 probe 변경에 대한 전체 Fast 결과를 별도로 기록한다. 사용자가 허용하지 않은 원본/참고 저장소 수정·삭제는 하지 않는다.
## §183 — lap635 work: **원본 dense fixture는 cap20 대조에 성공했지만 후보가 count20에 머물러 필수 runtime 검증 실패** (2026-09-25 KST)

lap634 지시에 따라 probe를 최소 수정했다. PS3에서 raw로 읽은 기존 일꾼 slot1198 주변을 anchor로 삼고, 건물형이 아닌 type2(1×1, 비용13) 55기를 6개 소구역(10+10+10+10+10+5)으로 engine-seed했다. 드래그 입력은 1600 프레임 좌상단 800×600 영역 `(120,120)→(760,540)`을 유지했다.

- 변경: `tools/g5_candidate_drag_probe.py`에 slot1198 raw snapshot, dense type2 fixture 요청, receipt 합계, v3 provenance를 추가했다. SHA256 `655e8a12b8321db5791060632da31c4257491b5b841f61837d552575562dac67`; 원본/참고 저장소·제품 EXE·커밋은 수정하지 않았다.
- 원본 fresh run: protected/private SHA `b56986e0…a8ac`, worker raw `(163,92)`, camera `[161,90]`, type2×55 `used=735/1500`, live57, stock selection `count=20`, unique20, move command nonzero20, cleanup/source unchanged. 결과 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap635_g5_original_dense/probe-result.json`.
- 후보 fresh run: candidate SHA `ebd46050…e8c`, worker raw `(142,142)`, camera `[140,140]`, type2×55 `used=735/1500`, live57, candidate reader base `0x0108c000`/capacity50, 그러나 selection `count=20`, unique20, move command nonzero20. `FAIL_SELECTION_CAP`, process exit2; cleanup/source unchanged. 결과 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap635_g5_candidate_dense/probe-result.json`.
- 기계 검증: probe py_compile PASS, targeted G5/bridge tests `4 passed`. 후보 필수 runtime 검증이 실패했으므로 `make check`, 50/51 경계, save/load는 실행하지 않았다.

### 승격 작업자가 이어서 검증할 것

1. 후보 raw/provenance와 `patches/selection/g5_selection_cap50_v1.py`의 relocation sites를 독립 대조해 relocated base에서 실제 writer가 왜 20개만 커밋하는지 판정한다. 원본 stock cap20 성공은 후보 결함을 설명하지 않으므로 후보 50 PASS로 승격하지 않는다.
2. 원인과 수정 범위를 확정한 뒤에만 새 private runtime에서 원본/후보 동일 dense fixture를 다시 실행하고, candidate count50·unique50·51번째 미선택·명령50을 읽는다. 그 전에는 save/load나 마일스톤 판정을 진행하지 않는다.

판정: **`BLOCKED(candidate_selection_cap_or_relocation_wiring)`**. 이번 바퀴 변경·raw·캡처는 보존되었다.

## §184 — lap636 work: **후보 selection consumer 수리 후에도 count20으로 필수 runtime 검증 실패** (2026-09-25 KST)

lap635의 candidate `count=20` 원인을 좁히기 위해, old-byte 길이 오류로 실제 적용되지 않던 indexed selection reader 3곳을 보강하고 `0x0041DC40` selection consumer의 20-entry local-list 상한/stack frame을 50-entry에 맞춰 후보를 만들었다. local list는 `[esp+0x30]`을 유지하고 임시 word buffer를 `0x80→0x200`, frame을 `0x98→0x230`으로 옮겨 겹침·반환경로 오염을 피했다.

- protected source SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (before/after 불변).
- candidate SHA: `3877194855f54a8b63ea064a6be9f405485bffcb98286198f9a3f5a785459757`; private candidate 설치/해시 확인 PASS.
- targeted 회귀: `patches/selection/test_g5_selection_cap50_v1.py tests/test_g5_selection_inventory.py patches/population/test_runtime_bridge_contract.py` → **10 passed**; py_compile/build length/SHA PASS.
- fresh foreground runtime: `.venv/bin/python tools/g5_candidate_drag_probe.py --variant candidate --runtime-root local/runtime/g5-lap636-candidate --artifact-root /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap636_g5_candidate_cap50`.
- fixture/provenance: isolated Wine/Xvfb 1600×1200, PS3 tick2, owner0 type2×55 dense rows, used `735/1500`, live57; cleanup residual0/ok=true; source unchanged.
- 필수 결과: relocated reader `0x0108c000`/capacity50인데도 selection `count=20`, unique20, move command nonzero20, probe exit2 `FAIL_SELECTION_CAP`. 50/51·save/load·full `make check`는 SKIP.
- raw/captures/provenance: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap636_g5_candidate_cap50/`; 상세 `docs/history/laps/20260925_lap636_work_g5_selection_consumer_cap_failed.md`.

### 승격 작업자가 이어서 검증할 것

1. 위 candidate private run의 raw/capture와 candidate bytes를 독립 대조해 `0x0041DC40` consumer 진입·선택 count writer·new array `[20]` write를 hardware watchpoint 또는 동등한 instruction trace로 구분한다.
2. writer가 20번째에서 멈추는지, 50개를 썼다가 consumer가 20개로 재구성하는지, 또는 drag hit-test가 20개만 전달하는지 중 하나로 원인을 판정한다. 현재 결과만으로 특정 원인을 확정하지 않는다.
3. 원인·안전 범위를 확정하고 새 후보를 만든 뒤에만 원본 동일 fixture 대조, candidate 50/51, 50기 명령, canary/save-load를 재실행한다. 그 전에는 G5 PASS나 마일스톤 승인을 주장하지 않는다.

판정: **`BLOCKED(candidate_selection_cap_persists_after_consumer_patch)`**. 현재 변경·raw·캡처·미커밋 상태는 보존되었다.

## §185 — lap637 work: **writer hardware trace가 21번째 시도를 보이지 않아 상위 경계 미해결로 승격** (2026-09-25 KST)

lap636 candidate에 opt-in gdb hardware trace를 붙여 같은 private runtime/fixture를 foreground 실행했다. trace는 count `0x0108c000`, `0x0108c050` (`base+20*4`), consumer entry `0x0041DC40`, writer entry `0x00412D90`를 모두 hardware 방식으로 무장했다. 첫 동적 return-breakpoint 버전은 유용한 raw event 뒤 gdb SIGSEGV가 났고, return breakpoint를 제거한 두 번째 trace는 정상적으로 raw summary를 남겼다.

- clean trace: `consumer_entries=1`, `writer_entries=20`, count write 20회, target write 1회, 21번째 칸 `0x0108c054` write 0회. writer 호출 return address는 모두 `0x0040f7f6`이다. 따라서 관측 경로는 20번째 뒤 writer 호출 자체가 더 오지 않았지만, drag hit-test가 20개만 넘겼는지 consumer가 20개로 재구성했는지는 아직 미판정이다.
- candidate probe: relocated base `0x0108c000`, capacity50에서도 `count=20`, unique20, movement command20, exit2 `FAIL_SELECTION_CAP`; 50/51·50기 명령·save/load는 SKIP. raw/provenance/capture는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap637c_g5_writer_trace/`와 `.../20260925_lap637c_g5_candidate_cap50/`에 보존했다.
- Fast: targeted 10 passed; full `make check` **894 passed in 689.10s**, Ruff/compileall/mypy/`CONTEXT_PASS` PASS. source SHA before/after와 private cleanup는 PASS.

판정: **`BLOCKED(candidate_upstream_selection_writer_boundary_unresolved)`**. 현재 결과만으로 추가 `0x14` 바이트 패치를 추측하지 않는다.

### 승격 작업자가 이어서 검증할 것

1. 새 후보를 만들기 전에 `0x0041E220` caller와 `0x0041E1D6` call loop의 `[esp+0x10]` count source를 instruction trace로 귀속하고, hit-test 20개 전달과 consumer 재구성을 분리한다.
2. exact old bytes/비중첩/restore 회귀를 추가한 원인 확정 후보에서만 원본 count20 대 후보 count50/51·50기 명령·canary/save-load를 재실행한다.

## §186 — lap638 work: **upstream count는 20으로 확인됐지만 setter 분기 미귀속으로 승격** (2026-09-25 KST)

lap637 지시에 따라 새 private candidate runtime에서 `0x0041E1D6` loop, `0x0041E220` caller, writer를 read-only gdb로 추적했다. 첫 trace는 caller의 per-tick noise로 event-limit에 도달했고, 필터를 고친 두 번째 trace는 loop20/writer20을 확인했다. 세 번째 trace는 count-build 후보 `0x0041DD74`, gate `0x0041E06A`, load `0x0041E154`와 relocated buffer를 함께 걸었지만, 실제 attach 구간에서는 해당 setter 분기가 잡히지 않아 exact patch site는 미확정이다.

- 후보 SHA `3877194855f54a8b63ea064a6be9f405485bffcb98286198f9a3f5a785459757`; 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
- clean refined trace: `0x0041E1D6` 20회, `ebp=ebx=20`, breakpoint 기준 `esp+0x1c=20`; relocated `0x0108c000+20*4` 뒤는 0이며 writer `0x00412D90` 20회, return `0x0040F7F6`.
- candidate probe는 selection20/unique20/movement20/exit2 `FAIL_SELECTION_CAP`; 50/51·50기 명령·save/load는 SKIP. raw/probe는 `temp/Syw2plus_patch/20260925_lap638c_g5_upstream_trace/`에 보존.
- 도구 변경은 `tools/g5_selection_upstream_trace.py`뿐이며 제품 패치·원본·참고 저장소는 수정하지 않았다. `make check` 896 passed/646.06s, Ruff/compileall/mypy/CONTEXT_PASS, `SAFETY_PASS`.

판정: **`BLOCKED(candidate_upstream_count_setter_unresolved)`**.

### 승격 작업자가 이어서 검증할 것

1. 새 후보/추측 `0x14→0x32` 패치 전에 `0x0041E1D6` count20을 생성하는 실제 hit-test/caller 분기를 같은 실행에서 instruction trace로 귀속한다. `0x0041DD74`·`0x0041E06A`·`0x0041E154`의 분기와 후보 buffer source를 연결하고, `0x0041E220` per-tick noise와 selection path를 분리한다.
2. 원인 확정 뒤 old bytes·비중첩·정확한 원복 회귀를 추가한 후보만 private runtime에서 재드래그한다. 원본 count20 대 후보 count50/51, 50기 명령, canary/save/load를 그때 측정한다.
3. 현재는 G5 PASS·마일스톤 승인·50기 명령 전달을 주장하지 않는다.

## §187 — lap639 work: **count20 setter와 실제 hit-test 후보 열거 경계 미귀속으로 BLOCKED** (2026-09-25 KST)

lap638의 지시에 따라 후보 private runtime에 드래그 전 gdb를 attach하고 `0x0041E1D6` loop/count, `0x00412D90` writer, `0x0041DE76` 삽입 블록, `0x0041DD51/69` 스캔, count 대입 지점을 함께 기록했다. 초기 두 invocation은 각각 trace 환경변수 누락과 `continue.flag` handshake 누락으로 drag 전 중단되었고, 두 원인은 호출 래퍼 로그로 확인해 보수했다. corrected foreground runs는 후보 runtime을 실제 drag까지 완주했다.

- 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변, 후보 SHA `3877194855f54a8b63ea064a6be9f405485bffcb98286198f9a3f5a785459757` 유지.
- 최종 upstream trace: `0x0041E1D6` 20회, breakpoint 기준 count20, writer20회, `0x0041DE76` 0회, `0x0041DD51/69` 0회, `0x0041DD74` 0회. `0x0041E1BC`에서 count20은 관측했지만 그 값을 만든 실제 hit-test/caller 분기는 연결하지 못했다.
- 보조 hardware watch: count write20회, consumer entry1회, writer entry20회. candidate probe는 selection20/unique20/movement20/exit2 `FAIL_SELECTION_CAP`; 50/51·50기 명령·save/load는 SKIP. 모든 private runtime cleanup residual0, source unchanged.
- Fast: `make check` **896 passed in 616.36s**, Ruff/compileall/mypy/`CONTEXT_PASS`, `SAFETY_PASS`.
- raw: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap639f_g5_upstream_trace/`, `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap639e_g5_watch_trace/`; 상세 `docs/history/laps/20260925_lap639_work_g5_upstream_count_blocked.md`.

판정: **`BLOCKED(candidate_upstream_count_setter_unresolved)`**. `0x14→0x32` 추측 패치와 50/51 재실행을 하지 않는다.

### 승격 작업자가 이어서 검증할 것

1. drag input timestamp와 같은 실행의 `0x0041DC40` frame에서 `[esp+0x10]`이 20으로 바뀌는 instruction/caller를 귀속하고, `0x0041E220` per-tick noise·`0x0041E1D6` command loop·실제 hit-test 후보 buffer를 분리한다.
2. count source가 확정된 뒤 exact old bytes, non-overlap, restore 회귀를 추가한 새 후보만 만든다. 원본 count20 대 후보 count50/51, 50기 명령을 그때 측정한다.
3. 현재 G5 PASS·50기 명령·save/load·마일스톤 승인을 주장하지 않는다.

## §188 — lap640 work: **hit-test 20 cap fixed, but required original full-drag control failed** (2026-09-26 KST)

lap639의 운영자 지시에 따라 `0x004384B0` 진입 인자와 반환 후 caller buffer/count를 fresh candidate runtime에서 추적했다. `FUN_004384B0`의 첫 인자 출력 buffer에는 20개가 기록되고 둘째 인자 count pointer에는 20이 기록됐다. 같은 실행에서 호출 경로의 `FUN_004386E0` 내부 `0x0043877A`가 26회 hit됐고, 마지막 calls는 `EAX=20`에서 literal `0x14`를 비교했다. 따라서 exact old-byte 후보를 `0x0043877A: 66 3d 14 00 → 66 3d 32 00`으로 추가했다.

- candidate SHA: `a123498ab6378df17536718b7ec64389423fb0b7d0800a417cb3d476a1a9bc98`.
- patched trace: compare right `0x32`, append helper 26회, count26/writer26, crash 없음.
- same fixture with old drag: candidate selection21/movement21; cap20을 넘긴 것은 확인했으나 50은 아님.
- drag was adjusted to content `(20,20)→(780,470)` to include upper rows. Required protected-original control with that identical input failed at selection5/movement5 (`FAIL_ORIGINAL_SELECTION`, exit2), so candidate 50 run was not started after the control failure.
- source SHA remained `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; cleanup/source unchanged. Full Fast `897 passed in 591.82s`, Ruff/compileall/mypy/context/safety PASS.
- raw/provenance: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260925_lap640d_g5_hit_append_limit/`, `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap640g_g5_patched_trace/`, `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap640h_g5_original_full_drag/`.

### 승격 작업자가 이어서 검증할 것

1. Do not treat the `0x14→0x32` edit as G5 PASS. First independently repair/verify the original camera, drag rectangle, and visible living-unit fixture so the identical input yields stock count20.
2. Only after that original control passes, rerun candidate `a123498a…` in a new private runtime and measure count50, unique50, 51st rejection, 50 command recipients, canary/cleanup, and save/load.
3. Preserve the lap640 candidate and raw artifacts; do not overwrite the protected source, auto-update golden/baseline, or claim milestone approval.

판정: **`BLOCKED(original_same_input_control_failed)`**. Current changes and evidence are preserved; G5 product PASS remains unclaimed.

## §189 — lap641 work: **candidate 36/50 with Wine crash after original control passed** (2026-09-26 KST)

lap641은 lap640의 원본 대조 실패를 해소하기 위해 probe의 드래그를 `(120,120)→(760,540)`로 복구하고, owner0 type2×55를 11×5(`(167,96..100)`, 각 count11)로 배치했다. 원본 동일 probe는 camera `[161,90]`, selection/movement `20/20`, `PASS_ORIGINAL_CAP20`으로 통과했다. 후보 `a123498a6378df17536718b7ec64389423fb0b7d0800a417cb3d476a1a9bc98`는 private EXE 교체·relocated storage `0x0108c000`/capacity50·source 보호·cleanup을 통과했지만 selection/movement `36/36`에서 멈추고 `FAIL_SELECTION_CAP`으로 종료했다. `probe.log`에는 `wine: Unhandled exception 0x80000004`가 있고 after-drag capture에는 Wine crash dialog가 남았다.

- 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변; source/private cleanup residual0.
- fixture raw/provenance/capture: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap641_g5_candidate_11x5/`; 원본 control은 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap641_g5_original_control/`.
- `checks/context_limits.py`는 `CONTEXT_PASS`; full `make check`는 필수 runtime 실패 뒤 재실행하지 않았다. 50/51·50기 명령·save/load·G5 PASS는 미검증이다.

### 승격 작업자가 이어서 검증할 것

1. 위 raw/capture와 candidate bytes를 독립 대조해 crash를 selection relocation, command path, fixture overlap, harness 종료 중 하나로 귀속한다.
2. 11×5 world grid의 실제 drag hit-test 포함 수를 camera/world→screen 변환과 unit raw로 계산해 `0x0043877A` edit 효과와 fixture 범위를 분리한다.
3. 원인·안전 범위 확정 전 재시도 금지. 새 후보가 승인되면 original20 → candidate50/51 → command50 → canary/save-load 순으로 fresh isolated runtime에서 검증한다.

판정: **`BLOCKED(candidate_runtime_36_and_crash)`**. 현재 변경·raw·capture·미커밋 상태는 보존되었다.

## §190 — lap642 work: **clean candidate still stops at 36 and fails required runtime gate** (2026-09-26 KST)

lap641의 harness 의심을 분리하기 위해 gdb/trace 환경변수 없이 probe fixture를 7×8(7+7+7+7+7+7+7+6=55)로 좁혔다. 같은 probe/입력의 protected original은 새 foreground isolated runtime에서 `PASS_ORIGINAL_CAP20`을 재현했다. candidate `a123498a6378df17536718b7ec64389423fb0b7d0800a417cb3d476a1a9bc98`는 relocated storage `0x0108c000`/capacity50과 private SHA를 확인했지만 selection/movement `36/36`, exit2 `FAIL_SELECTION_CAP`으로 끝났다. 이번 clean log에는 `wine: Unhandled illegal instruction at address 047A0480`가 남아, 이전 `0x80000004` 해석과 같은 원인이라고 단정하지 않는다.

- source SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` before/after 불변; candidate SHA 동일; cleanup residual0/`ok=true`; original/candidate 전비 `5000/5000`, fixture owner0/type2×55.
- original raw/capture/provenance: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap642_g5_original_7x8/`; candidate: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap642_g5_candidate_7x8/`.
- probe 변경 파일 SHA: `tools/g5_candidate_drag_probe.py` = `45460b196d8e76406f1781638ea55fe2457f392503145cfadf664bc94ceb4f26`; 제품 EXE/원본/참고 저장소는 수정하지 않았다. full `make check`, 50/51, 50기 명령, canary/save-load는 필수 runtime 실패로 SKIP.

### 승격 작업자가 이어서 검증할 것

1. 위 raw/capture와 candidate bytes를 독립 대조해 `36`의 실제 drag hit-test 범위와 `047A0480` illegal-instruction 시점을 분리 귀속한다. fixture 배치가 55기 모두 화면 안인지 world→screen 변환과 unit raw로 확인한다.
2. 원인·안전 범위를 확정한 새 후보가 있을 때만 fresh original20 → candidate50/51 → command50 → canary/save-load 순으로 재실행한다. 그 전에는 재시도·G5 PASS·마일스톤 승인을 주장하지 않는다.

판정: **`BLOCKED(candidate_clean_runtime_36_and_illegal_instruction)`**. 현재 probe 변경·raw·capture·미커밋 상태는 보존되었다.

## §191 — lap643 work: **독립 대조 후에도 G5 후보 원인 미귀속으로 승격** (2026-09-26 KST)

lap642의 기존 raw/capture/candidate bytes를 새 실행 없이 독립 대조했다. protected original의 `probe-result.json`은 동일 drag `(120,120)→(760,540)`에서 `selection_after.count=20`, `movement_command_nonzero=20`, `PASS_ORIGINAL_CAP20`이다. candidate EXE의 재계산 SHA는 `a123498ab6378df17536718b7ec64389423fb0b7d0800a417cb3d476a1a9bc98`로 provenance와 일치하고, relocated storage는 `0x0108c000`/capacity50이다. candidate raw는 selection36/unique36/movement36이며 source `b56986e…` before/after와 cleanup `ok=true`가 유지된다.

- 후보 `after-drag.png`에는 scripted right-click 전에 Wine crash dialog가 보이고, `probe.log`에는 `Unhandled illegal instruction at 047A0480`가 있다. 따라서 이번 clean 증거만으로 crash를 명령 패커/네트워크 20칸 문제로 단정할 수 없다.
- 후보 camera `[40,140]`, fixture bounds `(46..52,146..153)`와 원본 camera `[19,90]`, bounds `(25..31,96..103)`가 달라 36이 drag hit-test가 실제로 포함한 범위인지 별도 world→screen 계산이 필요하다. 55기 fixture 생성 자체와 selection snapshot 36은 raw로 확인됐지만 55기 화면 포함·append 호출 수·illegal PC의 제품 함수 귀속은 미확정이다.
- `python3 checks/context_limits.py`는 `CONTEXT_PASS`. 새 runtime/make check/후보 설계는 필수 runtime 실패와 근거 미확정 때문에 이 랩에서 수행하지 않았다. G5 50/51·50기 명령·save/load·제품 PASS·마일스톤 승인은 금지한다.

### 승격 작업자가 이어서 검증할 것

1. 두 artifact의 unit raw/camera/capture를 독립 대조해 world→screen 변환과 drag rectangle의 실제 포함 수를 계산하고 `0x0043877A` append count와 분리한다.
2. candidate crash capture가 right-click 전에 생성된 사실을 시간/로그 순서와 함께 확인하고, `047A0480`을 selection-after 비동기 경로와 명령 패커 경로 중 하나로 귀속한다. 두 crash signature(`0x80000004`, illegal instruction)를 동일 원인으로 합치지 않는다.
3. 원인·안전 범위를 exact old bytes/non-overlap/restore 회귀로 확정한 뒤에만 fresh isolated original20→candidate50/51→command50→canary/save/load를 수행한다. 원본·golden 자동 갱신과 커밋은 금지.

판정: **`BLOCKED(candidate_clean_runtime_36_and_illegal_instruction_unattributed)`**. 현재 변경과 모든 raw/capture/provenance는 보존되었다.
## §192 — lap644 work: **G5 temporary-buffer overlap repair did not clear the candidate runtime fault** (2026-09-26 KST)

lap644 implemented one exact, evidence-backed candidate repair: `0x0041DE8A` still wrote the 16-bit temporary selection list at `[esp+0x80]`, overlapping the expanded 50-entry local list at `[esp+0x30..0xf4]`; it was relocated to `[esp+0x200]`. Candidate SHA is `af3b482e628a687a6d548b6eb5577db987544d12390e118baeb76facd78140f1` from protected source `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.

- Targeted patch/restore/inventory tests: **10 passed**. Context limits: **CONTEXT_PASS**. Full `make check` was not rerun after the mandatory runtime gate failed.
- Fresh foreground isolated runtime (`runtime_env.prepare`, Wine/Xvfb 1600×1200, solo owner0, synthetic type2×55 dense 7×8) reached PS3 and preserved cleanup/source SHA, but candidate selection was `42/50`, unique42, movement raw42, status `FAIL_SELECTION_CAP`. `probe.log` reports `Unhandled page fault on read access to 00000048 at address 0488048B`; after-drag capture is a Wine crash dialog.
- Prior gate-aligned read-only gdb trace showed selection-loop/writer activity through count36 and the same invalid fault pattern, but did not prove the remaining writer/consumer PC. The single repair is therefore not accepted as a root-cause fix. 50/51, 50-command, canary/save/load, G5 PASS, middle review, and user milestone approval remain forbidden.

### 승격 작업자가 이어서 검증할 것

1. Independently inspect the repaired candidate bytes and gate-aligned raw/capture; attribute `0x0488048B` to the exact remaining fixed-size stack/list writer, keeping `0x80000004`, `0x047A0480`, and `0x0488048B` as separate signatures until proven identical.
2. Add only the exact old-byte/non-overlap/restore repair for that PC, then run fresh isolated original20 control before candidate50/51, command50, canary, and save/load.
3. Do not run `make check` as a substitute for the failed runtime gate; do not update original/golden baselines or commit.

판정: **`BLOCKED(candidate_repaired_runtime_same_fault_unattributed)`**. 현재 변경, repaired candidate, raw/capture/provenance, source SHA, and failed runtime result are preserved.

## §193 — lap646 work: **lap645 G5 module/fault trace still cannot establish a safe repair** (2026-09-26 KST)

이번 세션은 `loop/PROMPT.md`의 일반 hands-on 작업자로서 lap645 산출물만 독립 대조했다. 필수 runtime이 이미 실패했고, 새 실행·추측 패치·`make check` 재시도는 하지 않았다.

- 보호 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
- lap645b candidate: `af3b482e628a687a6d548b6eb5577db987544d12390e118baeb76facd78140f1`; probe result SHA `463115c31d33fe5f3556db01a2e74d9a0de2ff3aedea972641dc4c5f26e709d4`; gdb raw SHA `ebfb4ea0edfd77b87d19bac8fd222f063426c9c1a9cabd6032ad4c0b00f8a789`. Fresh run reached PS3 with owner0/type2×55 dense 7×8 fixture, then selection/movement `35/35`; log reported page-fault write at `0x04810486`, gdb exception snapshot had invalid EIP/stack and no valid backtrace.
- lap645c exact byte follow-up candidate: `7c6e372a576b27843c79cb906d024a4aab044166c4ce4625f39f05475a2b1d4d`; only diff from `af3b482e…` is `0x0041DEBD` temporary offset `[esp+0x84]→[esp+0x204]`. Fresh run reached the same fixture and selection/movement `42/42`, then reported illegal instruction at `0x0488048B`; probe result SHA `41e4618d714dbcabc6296ac16602444fe4505821e61abaf2c5c509e7dc7d2336`.
- Both manifests prove private runtime, candidate SHA replacement, source SHA unchanged, and cleanup; neither proves 50/51, command50, canary, save/load, or G5 PASS. `0x04810486`, `0x047A0480`, and `0x0488048B` remain separate signatures until a valid module/EXE call-chain capture connects them.

### 승격 작업자가 이어서 검증할 것

1. Preserve the lap645 artifacts and independently map the invalid EIP/faulting instruction to a real loaded module or prove stack/list corruption before changing bytes.
2. Attribute the remaining fixed-size writer/consumer to an exact EXE PC and old bytes; add only a non-overlapping, exact-restore repair with regression coverage.
3. Run fresh protected-original count20 control first. Only if it passes may candidate50/51, command50, canary, and save/load resume. Do not substitute `make check` for the failed runtime gate.

판정: **`BLOCKED(candidate_runtime_fault_unattributed)`**. Current source, candidates, raw/capture/provenance, source SHA, and failed runtime evidence are preserved; no product code or original asset was changed.

## §194 — lap647 work: **fresh exception maps/ESP trace still leaves G5 runtime fault unattributed** (2026-09-26 KST)

lap647은 lap645의 invalid EIP 귀속을 위해 `tools/g5_selection_ui_exception_trace.gdb`에 예외 순간 `info proc mappings`와 `x/128wx $esp`를 추가하고, 새 private candidate runtime을 끝까지 실행했다. 제품 패치/원본/참고 저장소/커밋은 0이다.

- 보호 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변. 후보 `7c6e372a576b27843c79cb906d024a4aab044166c4ce4625f39f05475a2b1d4d`는 private EXE와 일치.
- 새 artifact: candidate/probe `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap647_g5_candidate_exception_trace/`; GDB raw `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap647_g5_exception_trace_gate/gdb-module.raw`.
- probe SHA `cbeb822e3aa3702da252626b4dea9a1d087210ffc7a4ce537999df2dc6f96cb0`; GDB raw SHA `285f72b6c1bc7b78ac468b9712912b0b3da9657f4cec1c581b570843c9a6f18d`; trace script SHA `cc823c21912e52a4ab17923d2cf0e27093e863c3ed647e86094b15312bb29d9e`.
- 동일 private Wine/Xvfb 1600×1200, solo owner0, synthetic owner0/type2×55 dense 7×8 fixture에서 `selection/movement=36/36`, `movement_command_nonzero=36`, `FAIL_SELECTION_CAP`, exit2. Cleanup `ok=true`, source unchanged.
- 예외 raw: `SIGSEGV`, `EIP=0x04810486`, `ESP=0x31fa50`. maps의 EXE 범위는 `0x00400000–0x004ec000`이고 EIP를 포함하지 않으며, 유효 DLL 범위에도 귀속되지 않는다. ESP는 `0x047a0480`와 반복 `0x02480248`을 포함하고 backtrace가 깨진다. 따라서 DLL fault나 특정 EXE writer/consumer를 확정하지 못했다.
- Fast evidence: `CONTEXT_PASS`, `SAFETY_PASS`, targeted G5/inventory tests `10 passed`. `make check`, 50/51, command50, canary/save/load는 필수 runtime FAIL의 대체로 실행하지 않았다.

### 승격 작업자가 이어서 검증할 것

1. lap647 candidate/probe/GDB raw와 exact candidate bytes를 독립 대조하고, `0x04810486` 및 이전 `0x047a0480`을 실제 EXE call site와 old bytes에 귀속한다. 두 signature를 같은 원인으로 합치지 않는다.
2. 귀속된 단일 fixed-size writer/consumer에 대해서만 non-overlap·exact restore 회귀를 추가한다. 원본/참고 저장소와 golden/reference는 갱신하지 않는다.
3. 귀속과 회귀가 성립한 뒤에만 fresh protected-original20 control → candidate50/51 → command50 → canary/save/load를 수행한다.

판정: **`BLOCKED(candidate_runtime_fault_unattributed)`**. 현재 변경과 raw/capture/provenance는 보존되었고 G5 PASS·마일스톤 승인은 주장하지 않는다.

## §195 — lap648 work: **return-slot watchpoint 미발생과 필수 drag selection 0으로 승격** (2026-09-26 KST)

lap648은 운영자 지시대로 후보를 드래그 전에 GDB로 attach하고 `0x31FA4C`에 조건부 하드웨어 watchpoint `*(unsigned int*)0x31FA4C > 0x01000000`을 설치했다. watchpoint 1의 무장과 gate marker(`armed.json`, `probe_ready.json`, `continue.flag`)는 raw로 확인됐지만 `RETURN_SLOT_WATCH_HIT`은 0회였다.

- 보호 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변. 후보 `7c6e372a576b27843c79cb906d024a4aab044166c4ce4625f39f05475a2b1d4d`는 private EXE와 일치.
- fresh private Wine/Xvfb 1600×1200, solo owner0, synthetic type2×55 dense 7×8, PS3 fixture에서 probe는 `selection_after=0`, `drag produced no selection`, exit2로 실패했다. cleanup `ok=true`, source unchanged=true.
- GDB raw `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap648_g5_return_watch_b/gdb-return-watch.raw` SHA `b7bc46ac834f35d974ebbb1f1a0f16aafadfb9d36b4d1303d66ce8504ea14655`; probe `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap648_g5_candidate_return_watch_b/probe-result.json` SHA `451d89d0cb037b9d33b89d974124ddfdd67ebd1785dd926ad4deaa8c66e73e25`.
- `make check`, 50/51, command50, canary/save/load 및 writer PC/old bytes 귀속은 필수 runtime 실패와 watchpoint 미발생으로 SKIP. 신규 추적 스크립트는 보존했으며 제품 바이트·원본·참고 저장소·golden·커밋은 변경하지 않았다.

### 승격 작업자가 이어서 검증할 것

1. 위 GDB raw/probe-result/capture와 `tools/g5_selection_return_watch.gdb`를 독립 검수해 watchpoint가 실제 대상 thread/주소를 감시했는지, selection0이 입력/fixture/harness 문제인지 먼저 분리한다.
2. 그 원인과 정확한 writer/consumer PC·old bytes가 확정되기 전에는 새 후보나 추측 패치를 만들지 않는다.
3. 귀속과 non-overlap/exact-restore 회귀가 성립한 경우에만 fresh protected-original20 → candidate50/51 → command50 → canary/save/load 순서를 재개한다.

판정: **`BLOCKED(candidate_return_watch_no_hit_and_selection_zero)`**. 현재 변경·raw·capture·provenance는 보존되었고 G5 PASS·마일스톤 승인은 주장하지 않는다.
## §195 — lap649 work: **G5 runtime reaches watch hit but EXE writer remains unattributed** (2026-09-26 KST)

lap649 followed the current operator instruction exactly: GDB attached to the fresh private candidate runtime, armed four hardware watches at `0x31FA40..0x31FA4C`, continued the game, verified tick `0x008924B8` advanced `93→95`, then injected the drag. The first same-coordinate drag produced selection 0, so the probe performed the one allowed retry; retry selected 36 unique units and the movement command reached all 36. This is still a mandatory G5 runtime failure (`FAIL_SELECTION_CAP`, exit2), not a pass.

- Protected source SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged. Private candidate SHA: `7c6e372a576b27843c79cb906d024a4aab044166c4ce4625f39f05475a2b1d4d`.
- Hardware watch hit: `0x31FA4C`, value `0x02000001`; current EIP `0xe97da80e`, `info symbol` has no symbol, instructions are Wine `/lib/i386-linux-gnu/libc.so.6`, and the backtrace stops with `corrupt stack`. The probe log separately reports page-fault write at invalid EIP `0x04810486`. No valid EXE writer/consumer PC or exact old bytes were established.
- Changed diagnostic files: `tools/g5_candidate_drag_probe.py`, `tools/g5_selection_return_watch.gdb`, and new read-only observer `tools/g5_selection_tick_gate.py`; no product binary, original/reference asset, or commit changed. Targeted regression tests: **10 passed**. Current private game copy was removed after the run; manifest/output/prefix/raw/capture artifacts remain.
- Artifacts: `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap649c_g5_return_watch/gdb-return-watch.raw` SHA `f39df87cd89e1d86af45c348f9a828e09eee018ca6f633aba1ff2246d43d4b37`; candidate result `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap649c_g5_candidate_return_watch/probe-result.json` SHA `9fabb8e848de7f70132c2760f9ce3d3c14790e71794e9c6f6e61cb8545c89f90`; candidate provenance SHA `a90fe052eb59e7dfe57668c92a92275cdfe7da8f663313046bb40c24abd3bdc0`.

### 승격 작업자가 이어서 검증할 것

1. Read-only rerun/inspection of the preserved GDB path with `info proc mappings` at the watch stop, then identify the valid EXE caller frame that initiated the libc copy; do not infer a patch from the invalid EIP.
2. Independently decide whether the `0x31FA4C` write and `0x04810486` page-fault signature are the same stack/list overflow. Require exact EXE old bytes and non-overlap proof before any candidate edit.
3. Only after that attribution, run a fresh protected-original 20-unit control followed by candidate 50/51, 50-command, canary, and save/load gates. Do not claim G5 PASS or milestone approval.

판정: **`BLOCKED(candidate_36_and_libc_watch_hit_exe_caller_unattributed)`**. 제품/원본/참고 저장소 변경 없음.
