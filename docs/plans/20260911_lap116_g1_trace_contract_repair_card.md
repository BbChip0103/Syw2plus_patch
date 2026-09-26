# 2026-09-11 lap116 — G1 diagnostic trace contract repair card

## 중간 판정

Codex `gpt-5.6-sol`/high 중간 검수 판정은 **HELPER CONFIRMED / TRACE CONTRACT REVISE /
GAME RUN BLOCKED**다. lap115의 exact-pointer helper는 `xdotool mousemove --sync`를 제거하고
bounded `getmouselocation --shell`로 requested root 좌표를 확인한다. fresh run도 `(608,564)`에서
`(760,40)`으로 이동한 뒤 1회 poll로 exact 좌표를 관측했다. 이는 helper 수리 확인일 뿐 G1 출력이나
필수 입력 승인 아니다.

validator의 9개 Surface7 오류는 원본 DirectDraw 경계나 validator 상수 오류가 아니다. processed
trace의 성공 `CreateSurface` 39건 중 30개 고유 surface가 있고, `0x01E6D848`은 seq50에서 처음
`surface_vtable_methods=49`로 설치·기록된 뒤 seq54..70의 같은 pointer 재반환 9회만 0이다.
`hook_create_surface`는 기존 `slot`이 이미 installed인 분기에서 지역값 `surface_methods=0`을
49로 바꾸지 않으므로, bridge가 자기 추적 상태를 잘못 직렬화한다. validator의 49 요구는 고정
MinGW `IDirectDrawSurface7Vtbl` 크기와 일치하므로 유지한다.

final summary 부재도 원본 게임 증거가 아니다. bridge는 `g1_direct_draw_trace_detach()`에서만
summary를 쓰지만 runner는 PS3 capture 직후 live trace를 복사·검증하고 그 뒤 `finally`에서 owned
process를 종료한다. 실제 source/processed trace 모두 100 events이고 마지막은 seq100 `blt_fast`,
summary는 0개다. 현재 종료 경로로는 detach summary를 검증 입력에 포함할 수 없으므로 bridge/runner
수명주기 계약 결함이다. summary 요구를 삭제하거나 runner가 summary를 합성해서는 안 된다.

## 새 Luna/high 실무 한 가지

한 가지 변경은 **fresh runtime 전에 diagnostic trace가 재사용 surface와 clean finalization을
자기일관되게 기록하도록 bridge/runner 계약을 수리하고 회귀로 잠그는 것**이다. 이 lap에서는 새
게임 실행을 하지 않는다.

- 허용 파일: `tools/inmm_stub/direct_draw_trace.c`, `tools/runtime_env.py`,
  `tests/test_direct_draw_abi.py`, `tests/test_g1_presentation_trace.py`, `tests/test_runtime_env.py` 중
  필요한 최소 집합. 게임 코드/EXE/DLL/assets, validator의 30/49 상수, 좌표, timeout, fixture는
  변경하지 않는다.
- 재사용 surface는 `slot->installed`, pointer identity, 현재 vtable이 보존된 clone인지 확인한 뒤에만
  49를 기록한다. stale record나 vtable 불일치는 `install_status=failed` 또는 동등한 fail-closed
  오류로 남기며 49를 추정 기록하지 않는다.
- runner는 같은 owned game window에 정상 종료를 요청하고 process 종료와 정확히 한 개의 final
  bridge summary를 bounded wait로 확인한 뒤에만 최종 trace를 복사·validator에 넘긴다. summary가
  없거나 game이 정상 종료하지 않으면 BLOCKED로 보존한다. 전역 kill, 다른 prefix/display 접근,
  runner 합성 summary, summary 요구 완화는 금지한다.
- 회귀는 같은 surface 재반환이 49를 유지하는 경우와 stale/vtable mismatch 거부를 직접 고정한다.
  또한 validator 호출이 clean-close/summary 관측 뒤에만 일어나고, summary 부재 시 raw 보존 및
  BLOCKED, cleanup이 owned target에만 제한됨을 고정한다.
- 시작 fingerprint: `direct_draw_trace.c=906562e03c83c52f73003a8fd58c06a8ad7981a9e72a2e64729937eef53b077a`,
  `runtime_env.py=48b8aeee07ae02a96f1211ffc29f9a93f461f4afceac5b13f584cb568ccf62b9`,
  `check_g1_presentation_trace.py=541e8448fdbbde5abb910a3ca5e85b5daa2c80322165a6e9e7796258cd0268bd`.

## 검증과 중단

`tests/test_direct_draw_abi.py`, `tests/test_g1_presentation_trace.py`, 관련 runtime targeted,
저장소 밖 fresh bridge build, `make doctor`, `make check`, `bash checks/safety.sh check`가 모두
PASS해야 한다. 원본 SHA는
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`로 고정하고 원본/게임
복사본을 쓰지 않는다. 예상 밖 실패나 근거 충돌이면 재시도하지 않고 변경·출력·SHA를 보존해
새 Sol/high에 승격한다. 모두 통과해도 새 Sol/high 독립 확인 전 fresh runtime 재실행과 G1/M1
승격은 금지한다.
