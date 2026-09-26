# lap111 work-tier repair card — DirectDrawCreateEx ABI order

## 판정과 범위

Sol/high 중간 독립 진단 판정은 **REVISE (root cause confirmed)**다. lap110 bridge의
`DirectDrawCreateEx` 2·3번째 인자 선언이 Win32 헤더 및 원본 caller와 반대다. 다음 Luna/high는
이 ABI 결함과 이를 놓친 회귀 계약만 최소 수정한다. G1 출력 패치, renderer 설계, baseline/golden,
원본/참고 저장소, 보존된 lap110 run은 변경하지 않는다.

## 고정 근거

- MinGW `ddraw.h`: `HRESULT WINAPI DirectDrawCreateEx(GUID *, LPVOID *, REFIID, IUnknown *)`.
- 원본 `0x00464364..0x00464374`: `push 0`, `push 0x004E5928`, `push edi`, `push 0`,
  `call 0x004D7938`; 따라서 arg2=`&out`, arg3=`IID`다.
- 원본 `0x004E5928` 16 bytes는 `c0 5e e6 15 9c 3b d2 11 b9 2f 00 60 97 97 ea 5b`,
  즉 `IID_IDirectDraw7=15E65EC0-3B9C-11D2-B92F-00609797EA5B`다.
- lap110 source는 typedef/hook을 `(GUID *, REFIID, LPVOID *, IUnknown *)`로 선언했다.
  원 함수 호출은 positional values를 그대로 전달해 `HRESULT=0`이지만, 반환 뒤 arg2 output
  storage를 IID로 읽어 `01E6D080-...`, arg3 IID를 output으로 읽어 `dd_object=0x15E65EC0`을 냈다.
- 보존 DLL fault RVA `0xA90D`는 `mov esi,[ebx]`; runtime relocation 뒤 Wine fault
  `0x78CBA90D`와 일치하고 `ebx=0x15E65EC0`이다. game log도 read fault target
  `0x15E65EC0`을 기록했다. 이것이 PS40/tick0 정지의 충분 원인이다.

## 허용 구현

1. `tools/inmm_stub/direct_draw_trace.c`의 함수 포인터와 hook을 헤더와 같은
   `(GUID *guid, LPVOID *out, REFIID iid, IUnknown *outer)` 순서로 고치고 원 함수를 같은 순서로
   한 번만 호출한다. corrected `out`만 DD object/vtable 설치에, corrected `iid`만 IID 기록에 쓴다.
2. 다시 수동 순서를 뒤집어도 build가 성공하지 않도록 `ddraw.h`의 실제 선언과 hook type의
   compile-time 호환 계약을 추가한다. GCC type assertion 또는 동등하게 빌드 실패가 보장되는
   방법을 사용한다. synthetic JSON validator test만 추가한 것은 이 조건을 충족하지 않는다.
3. 이 결함을 재현하는 targeted regression을 추가한다. 최소 검사는 header ABI order,
   original-call positional preservation, 반환 뒤 IID=`15E65EC0-...`와 DD object가 서로 다른
   올바른 sources에서 읽힘을 증명해야 한다. 기존 synthetic trace PASS만 재사용하지 않는다.

## 검증과 stop condition

1. source/private original SHA `b56986e0...`, `cmp=0`, PE32, caller/thunk/IID old bytes를 재확인한다.
2. 새 bridge를 저장소 밖 fresh output으로 빌드하고 경고/타입 계약, DLL SHA, import/원복·범위
   안전을 기록한다. targeted test, `make doctor`, `make check`, `bash checks/safety.sh check`가
   모두 PASS해야 한다.
3. 위 조건이 전부 PASS한 뒤에만 새 전체 game copy/new win32 prefix/unused Xvfb display에서
   90초 상한 trace를 정확히 한 번 실행한다. old lap110 prefix/run 재사용은 금지한다.
4. 성공 조건은 expected IID, 실제 비-null DD object, DD→surface→actual desc→present identity,
   PS9→PS3 같은 run capture, cleanup `ok=true`다. 실패하면 재시도하지 말고 raw trace/game log와
   새 SHA를 보존해 `loop/ESCALATE_SOL`을 갱신한다.
5. 성공해도 다음 새 Sol/high 독립 컨펌과 사용자 판단 전 G1/M1 PASS로 승격하지 않는다.

## 별도 남은 위험

현재 runner는 Wine debugger가 crash process를 붙잡으면 `_wait_state`가 최대 90초 뒤 일반
PS timeout으로만 보고할 수 있다. ABI 수리와 같은 변경에 섞지 않는다. 새 ABI-correct run이 다시
PS9 전에 멈출 때에만 process/crash fail-fast를 다음 단일 진단 카드로 분리한다.
