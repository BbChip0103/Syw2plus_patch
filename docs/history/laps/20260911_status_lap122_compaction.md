# 2026-09-11 | lap122 이후 | STATUS compaction 기록

`docs/STATUS.md`가 167줄에 도달해 다음 work 기록의 안전 여유가 부족했다. 최신 lap119~121 판정과
다음 한 가지는 유지하고, 이미 개별 history가 있는 lap113~118 상세를 이 파일로 이동했다.

- 이동 전 `docs/STATUS.md` SHA256: `6feb31faa7650716c11ecc52260215538bcf04d56d15f0794c4e298f62a9e3fd`
- 코드, 하네스, 게임, EXE, DLL, 자산, runtime artifact는 변경하지 않았다.

## 이동한 상단 요약

2026-09-11 lap113 Luna 실무 수리는 DirectDrawCreateEx ABI를 `(GUID*, LPVOID*, REFIID, IUnknown*)`로
교정하고 header와 hook의 compile-time 호환 계약 및 native 회귀 3건을 추가했다. 저장소 밖 fresh DLL
build, doctor, `make check` 148 passed, safety가 통과했으며, 새 trace는 expected IID와 실제 DD object를
분리 기록했지만 xdotool timeout으로 BLOCKED됐다. 제품/runtime/G1 승격은 없다.

## 이동한 blocker 상세

- lap113은 위 ABI를 수리하고 native compile contract를 추가했다. fresh run
  `local/runtime/20260911_135729_1465423_0`의 70-event raw trace는 expected IID와 DD object를
  올바르게 기록했지만 `xdotool ... 760 40` timeout(exit2)으로 PS3/present/final summary가 없다.
  PS9→PS7 메뉴 입력과 cleanup=`ok=true`, prefix 잔류 프로세스 없음은 확인했으며 재실행하지 않는다.
- lap114는 ABI 수리 자체를 독립 ACCEPT했지만 raw의 Blt 2건은 null-source clear형이고 PS3/summary/
  complete present가 없다. xdotool timeout 전후 실제 좌표가 없어 원인은 미확정이며, work tier는
  exact-position 검증을 추가한 뒤에만 fresh trace 1회를 수행한다.
- lap115 fresh run `local/runtime/20260911_141737_1611146_0`은 helper로 requested root `(760,40)`을
  실제 관측해 PS9→PS3와 같은-run 800×600 capture까지 도달했다. 그러나 validator는 100 events
  (install2/CreateEx1/set-mode12/CreateSurface39/GetDesc30/Blt2/BltFast14)에서 Surface7 vtable
  method count invalid 9건과 final summary 부재를 보고해 BLOCKED했다. manifest/original/private
  EXE SHA는 `c541f88b...`/`b56986e0...` 일치, raw/evidence/verdict SHA는 lap115 이력에 기록했다.
  cleanup=`ok=true`, prefix residual 없음이며 재실행하지 않는다.
- lap116은 39개 성공 CreateSurface/30개 고유 surface를 재계산했다. `0x01E6D848`은 seq50에서
  49로 설치된 뒤 같은 pointer 재반환 seq54..70 9회만 0이며, source의 installed-slot 분기가
  지역 count를 갱신하지 않는다. summary 0개/마지막 seq100 `blt_fast`이고 runner가 live copy를
  validate한 뒤에야 cleanup하므로 bridge/runner 계약 수리와 새 middle 확인 전 runtime은 BLOCKED다.
- lap117은 `surface_record_reusable`로 installed/object/clone-vtable/wrapper identity를 확인한
  뒤에만 Surface7=49를 기록하고, 불일치는 failed trace로 남긴다. runner는 observed owned window에
  정상 close를 요청한 뒤 process exit와 bridge final summary를 bounded wait하고서만 copy/validator를
  호출하며 summary 부재 raw를 보존한다. targeted 69 passed, 저장소 밖 bridge SHA
  `ba316160...`, `make check` 156 passed, doctor top `ok=true`, safety PASS다. 새 game run은 SKIP,
  새 Sol/high 독립 검수와 runtime/G1 승격은 대기 중이다.
- lap118은 lap117 source fingerprint와 분기/호출 순서, fresh bridge build를 확인했다. 다만 C 회귀는
  source 문자열만 검사하고 stale-uninstalled 분기를 실행하지 않으며, finalization PASS fixture는
  summary와 process exit가 선행돼 실제 순서를 검증하지 않는다. summary 부재도 helper 단독 검사라
  최종 runner의 raw 보존/validator 미호출이 미증명이다. REGRESSION REVISE, fresh runtime BLOCKED다.

## 이동한 검증 상세

- lap113은 원본/private SHA·cmp/PE·caller/IID/IAT bytes, source ABI 수리, targeted 3 passed, fresh
  bridge SHA `b7849b88...`, `make check` 148 passed, doctor/doctor-runtime/safety PASS를 기록했다.
  fresh trace raw SHA `891f4eaf...`, evidence/verdict/provenance와 캡처 SHA는 lap113 원문에 있다.
  live는 xdotool timeout exit2/BLOCKED이며 G1/M1·사용자 승인은 없다.

- lap114는 원본/header/source/test/raw SHA와 캡처를 독립 대조했다. targeted **3 passed**, 저장소 밖
  fresh bridge build PASS, doctor top `ok=true`, `make check` **148 passed**, Ruff/compileall/mypy/context와
  safety PASS다. 새 runtime/game/candidate는 SKIP이며 ABI ACCEPT를 runtime/G1 승인으로 승격하지 않는다.
- lap115는 시작 source SHA와 테스트 SHA를 확인한 뒤 `tools/runtime_env.py`/`tests/test_runtime_env.py`
  만 변경했다. exact-pointer targeted **58 passed**, `make check` **153 passed**, doctor top `ok=true`,
  `bash checks/safety.sh check`=`SAFETY_PASS`; fresh bridge는 저장소 밖 SHA `f2dfad3d...`다. 새
  runtime manifest check PASS이나 trace validator는 Surface7/summary로 BLOCKED이며 G1/M1·사용자
  승인은 없다. 상세 SHA/명령/fixture는 `20260911_lap115_luna_g1_pointer_helper_and_runtime_block.md`에 있다.
- lap116은 보존 원본/private EXE SHA·cmp·PE32, manifest/raw/trace/evidence/provenance/verdict SHA,
  helper/source/validator 결선과 PNG를 독립 대조했다. 새 runtime은 SKIP했다. `make doctor` top
  `ok=true`/original verified, `make check` **153 passed**, Ruff/compileall/mypy/context와 safety PASS다.
  helper만 CONFIRMED하며 trace/runtime/G1/M1·사용자 승인은 BLOCKED/미승인이다.
- lap117은 source SHA와 원본 SHA를 확인한 뒤 direct-draw bridge/runtime/tests만 변경했다. targeted
  **69 passed**, 저장소 밖 fresh bridge build PASS, `make doctor` top `ok=true`/original verified,
  `make check` **156 passed**, Ruff/compileall/mypy/context와 safety `SAFETY_PASS`다. 재사용 surface와
  clean finalization 회귀는 PASS지만 실제 runtime/trace/G1/M1·사용자 승인은 SKIP/미승인이다.
- lap118은 구현 변경 없이 source/test SHA를 독립 대조했다. 저장소 밖 fresh bridge SHA
  `e87cf716...`, `make doctor` top `ok=true`/original verified, `make check` **156 passed**, Ruff/
  compileall/mypy/context와 safety PASS다. source intent만 CONFIRMED했고 행동 회귀는 REVISE,
  runtime/trace/G1/M1·사용자 승인은 BLOCKED/미승인이다.

## 이동한 lap113~118 목록

- lap113: `docs/history/laps/20260911_lap113_luna_g1_presentation_trace_abi_repair.md`.
- lap114: `docs/history/laps/20260911_lap114_sol_g1_presentation_trace_confirmation.md`.
- lap115: `docs/history/laps/20260911_lap115_luna_g1_pointer_helper_and_runtime_block.md`.
- lap116: `docs/history/laps/20260911_lap116_sol_g1_trace_contract_confirmation.md`.
- lap117: `docs/history/laps/20260911_lap117_luna_g1_trace_contract_repair.md`.
- lap118: `docs/history/laps/20260911_lap118_sol_g1_trace_contract_review.md`.
