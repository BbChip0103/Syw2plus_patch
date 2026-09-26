# lap109 — G1 DirectDraw trace repair work 카드

상태: Sol/high 중간 독립 검수 **REVISE**. Luna/high 전용 단일 수리 카드다.
게임 patch·candidate·2배 출력 구현·G1 PASS·M1 종료가 아니다.

## 고정 판정

lap108의 raw artifact SHA, 원본/private copy SHA·`cmp=0`, PE old bytes, targeted/Fast/
safety PASS와 live BLOCKED를 독립 재현했다. 설치 실패 원인으로 제시된 주소 혼동은 확인됐다.
`0x004D7938`은 `ff 25 18 50 4e 00`인 코드 thunk이고 DDRAW import `FirstThunk`는
RVA `0x000E5018`, 실제 slot VA `0x004E5018`이다. 현재 상수 비교는 반드시 실패한다.

다만 이 한 상수만 바꾼 재실행은 금지한다. 현재 trace 구현은 원 함수 포인터 미연결,
Surface7 method index 오류, oversized vtable copy, 미사용 재진입/호출상한, 불완전 fail-closed와
validator라는 별도 선행 결함이 있다. 아래를 한 instrumentation 수리로 닫아야 한다.

## 허용 수리 범위

1. thunk `0x004D7938` old bytes와 IAT slot `0x004E5018`을 별도 상수/필드로 다룬다.
   import name, 계산 slot, loader-resolved target, 실제 DDRAW module `[base,end)`를 모두 확인하고
   install event에 실제 값으로 기록한다. guard 실패 이유도 단계별로 기록한다.
2. slot patch 전에 검증한 원 target을 `g_original_create_ex`에 연결한다. patch 또는 protection
   원복이 실패하면 slot을 원복하고 부분 설치 상태를 남기지 않는다. wrapper는 모든 경로에서
   원 함수를 정확히 한 번 호출하고 HRESULT를 그대로 반환한다.
3. 수동 index/word-count 대신 `IDirectDraw7Vtbl`과 `IDirectDrawSurface7Vtbl` typed copy,
   `sizeof`와 named member를 사용한다. 기준 layout은 DD7 30개, Surface7 49개이며 Surface7의
   `Blt/BltFast/Flip/GetSurfaceDesc` index는 5/7/11/22다. 동일 object 중복 patch를 막고,
   재진입 시 logging/hooking만 우회하되 원 호출은 보존한다.
4. method별 256/전체 2048 상한을 실제 emitter에 구현한다. 최초 초과에서 overflow 한 건과
   누적 dropped count를 남기며 summary 공간을 예약한다. vtable/object 고갈도 BLOCKED로 남긴다.
5. 필수 event에 DD/surface vtable, caller/return address, IID, original pointer/module range,
   descriptor/actual desc와 present identity를 채운다. validator는 event별 필드·타입,
   expected IID, active install, summary/dropped=0, object chain, present tick과 PS3 capture 연결을
   검사하고 누락 fixture를 모두 BLOCKED 처리한다.
6. runner는 PS9 관측 직후 첫 캡처/마우스 입력 전에 trace를 bounded read하여 같은 run_id의
   `install active/stage=complete`를 요구한다. missing/failed/malformed이면 raw trace를 output에
   복사하고 cleanup 후 즉시 BLOCKED한다. DLL `DllMain`에서 프로세스를 강제 종료하지 않는다.

원본/참고 EXE·DLL·game data, resolution bytes, candidate, baseline/golden, 기존 raw run은 변경하지
않는다. 새 dependency, 다른 wrapper, generic xref 재탐색, G1 제품 구현으로 범위를 넓히지 않는다.

## 검증 순서와 중단 조건

1. 원본/private SHA·`cmp=0`, PE32, import descriptor/slot/thunk/caller/mode bytes를 재확인한다.
2. fail-before-input helper와 validator negative fixture, typed vtable/원 pointer/rollback·상한 계약을
   검증하는 targeted test를 추가하고 저장소 밖 새 `mktemp -d`에서 bridge를 build한다.
3. targeted 전체, `make check`, `bash checks/safety.sh check`를 통과시킨다. 하나라도 예상 밖 FAIL이면
   재시도/live 금지, 변경과 로그를 보존하고 `loop/ESCALATE_SOL`을 갱신한다.
4. 모두 PASS한 뒤에만 새 전체 copy·새 win32 prefix·빈 Xvfb를 prepare/check/doctor-runtime하고,
   `1600x1200x24`, timeout 90의 `g1-presentation-trace`를 정확히 1회 실행한다.
5. install/identity/desc/present/PS3 연결·cleanup 중 하나라도 없으면 BLOCKED이며 같은 lap 재실행은
   금지한다. 모두 있어도 조사 후보일 뿐이며 다음 새 Sol/high 독립 검수 전 PASS 승격 금지다.

## work-tier handoff 성공식

기계 PASS는 (a) 실패 trace가 첫 입력 전에 중단되는 회귀 테스트, (b) typed vtable과 원 함수 1회
호출/원복 계약, (c) emitter/validator 상한과 필수 schema, (d) targeted/Fast/safety/build PASS,
(e) 단 한 번의 fresh run에서 IID→DD→surface→actual desc→present→같은 PS3 capture identity/tick,
(f) owned cleanup이 모두 성립할 때뿐이다. exit 0이나 800×600 캡처만으로 PASS하지 않는다.
