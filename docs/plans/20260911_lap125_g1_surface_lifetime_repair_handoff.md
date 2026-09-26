# 2026-09-11 lap125 — G1 surface lifetime repair handoff

## 중간 판정

Codex 기본 라우팅 `gpt-5.6-sol`/high 중간 검수 판정은 **LAP124 FAILURE CONFIRMED /
SURFACE LIFETIME CONTRACT REVISE / GAME RUN BLOCKED**다. 현재 대화 표면은 실제 model ID/effort
attestation을 제공하지 않으므로 실행 결과에서 이를 추정하지 않는다.

lap124 raw/provenance/evidence/verdict SHA는 handoff와 모두 일치한다. raw는 단일 run/thread의 79개
event이며 seq2 install active/complete 뒤 seq50에서 `0x01E6D848`을 49-method surface로 설치했다.
seq51 `GetSurfaceDesc`, seq52 `Blt`가 같은 pointer의 clone wrapper를 실제 호출한 뒤, seq53
`SetDisplayMode(800,600)` 다음 seq54에서 첫 `reused_surface_identity_or_clone_mismatch`가 발생했다.
이후 같은 pointer가 9회 반환되며 install failed 9개와 method-count 0인 CreateSurface 9개, 합계
failed-status event 18개가 생겼다. PS3/input/capture/final summary/validator PASS는 없다.

`surface_record()`는 raw pointer만 key로 쓰고 record를 detach 전에는 폐기하지 않는다.
Surface7 clone은 `GetSurfaceDesc/Blt/BltFast/Flip`만 감싸며 COM `Release` 수명 종료를 추적하지 않는다.
seq50~52가 record의 object/clone/wrapper/original 필드가 coherent했음을 보이고 그 뒤 record의 고정
필드는 쓰이지 않으므로, seq54 거부는 현재 `object->lpVtbl`이 저장 clone과 더 이상 같지 않다는
**강한 정황**이다. 단, 현재 실패 event가 16개 decision reason과 actual/stored vtable pointer를 한
문구로 합치므로 `current vtable == stored original` 및 `Release()==0` 자체는 raw로 직접 증명되지 않았다.
따라서 주소 동일성을 같은 COM 수명으로 간주해 즉시 49를 재사용한 lap123 계약은 충분하지 않다.
이는 diagnostic bridge 수명주기 결함 판정이며 원본 게임/G1 제품 결과가 아니다.

## 새 Luna/high 실무 한 가지

한 가지 변경은 **Surface7 record를 COM 수명에 맞춰 폐기하고, 실패 reason을 다음 raw에서 식별 가능하게
만드는 최소 diagnostic bridge 수리**다. 이 work lap에서는 게임/runtime을 실행하지 않는다.

- 허용 파일은 `tools/inmm_stub/surface_reuse_contract.h`, `tools/inmm_stub/direct_draw_trace.c`,
  `tests/test_direct_draw_abi.py`이며, lifecycle event를 validator의 bounded method로 추가할 때만
  `tools/check_g1_presentation_trace.py`, `tests/test_g1_presentation_trace.py`를 포함한다. 게임 코드,
  EXE/DLL/assets, runner, 좌표/timeout/fixture, validator의 DD=30/Surface=49 상수는 변경하지 않는다.
- `SurfaceRecord`에 원본 `Release`를 저장하고 private clone의 `Release`를 production wrapper로 바꾼다.
  wrapper는 저장 원본을 정확히 한 번 호출한다. 반환 refcount가 0이면 파괴된 `self`를 다시 읽거나
  원복하지 않고 record를 비운 뒤 해당 private clone만 해제해 slot을 재사용 가능하게 한다. 0보다 크면
  record/clone을 유지한다. 다른 surface/DD record나 전역 상태를 폐기하지 않는다.
- shared native decision에는 Release wrapper/original coherence와 `Release()==0 -> retire`,
  `Release()>0 -> keep` 수명 결정을 포함한다. production과 host harness가 같은 결정을 호출해야 하며
  source 문자열만 확인하는 token-only PASS는 금지한다.
- 기존 pointer가 남은 reuse 분기는 현재/clone/original/wrapper를 계속 fail-closed로 검사한다. 실패 event에는
  decision reason 번호 또는 안정된 reason 이름, actual object vtable, stored clone vtable, stored original
  vtable을 기록한다. 주소가 같다는 이유로 49를 추정하거나 vtable을 자동 재결합하지 않는다.
- bounded lifecycle evidence는 refcount 0 폐기 여부와 같은 주소의 다음 CreateSurface가 `new install/49`로
  처리됐는지를 구분해야 한다. event를 추가하면 method/total limit과 final summary count 계약도 함께 잠근다.

## 필수 회귀와 중단

- native executable regression은 coherent same-lifetime reuse=49, Release>0 keep, Release=0 retire,
  retire 뒤 같은 주소의 fresh install 가능, 이 cycle 9회에서 slot 증가/failed=0을 실행한다.
- 기존 stale/uninstalled와 identity/vtable/wrapper/original 단일 불일치 전부는 failed·0·고유 reason을
  유지하고, Release wrapper/original 단일 불일치도 추가한다. zero-retire 의미 반전 mutation은 실패해야 한다.
- targeted ABI/trace tests, fresh out-of-tree PE32 bridge build, `make doctor`, `make check`,
  `bash checks/safety.sh check`가 모두 PASS해야 한다. 보호 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`는 불변이어야 한다.
- 예상 밖 실패나 Release ABI/해제 순서 근거 충돌이면 재시도하지 않고 SHA/출력을 보존해 새 Sol/high에
  승격한다. 모두 PASS해도 새 Sol/high 독립 확인 전 fresh runtime 재실행과 G1/M1 승격은 금지한다.
