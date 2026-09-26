# lap107 — G1 DirectDraw presentation provenance work 카드

상태: Sol/high 중간 검토 **REVISE 후 실행 가능**. Luna/high 전용 단일 카드다.
게임 patch·candidate 생성·G1 PASS·M1 종료가 아니다. 현재 큐는 `docs/STATUS.md`만 따른다.

## 중간 판정

lap106의 다음 두 판단은 ACCEPT한다.

1. 원본의 실제 출력 경로 식별과 후보 1600×1200 구현/검증을 분리한다.
2. 원본 출력이 800×600이어도 실제 interface/object/surface/present provenance를 연결하면
   조사 PASS가 될 수 있다. 원본에 이미 1600×1200 destination이 있어야 한다고 요구하지 않는다.

전체 판정은 **REVISE**다. 현재 `tools/runtime_env.py g1-baseline`은
`0x00E5BF18` renderer 6필드, viewport, X11 geometry, 모듈, 캡처와 장면만 수집한다.
lap73 원시 `g1_baseline.json`의 `boundary`도 null이다. 저장소에는 DirectDraw COM object,
vtable method, 호출자, source/destination rectangle을 같은 run에서 기록하는 구현이 없다.
따라서 기존 명령을 다시 실행하지 말고 아래 최소 관측 기능과 1회 trace를 한 카드로 수행한다.

## 단일 가설과 범위

가설: SHA-pinned EXE의 `DirectDrawCreateEx` IAT를 diagnostic `_inmm.dll`에서 관측 전용으로
감싸고, 반환된 `IDirectDraw7`과 그 `CreateSurface` 반환 object의 실제 vtable method를 감싸면,
선택 mode의 surface 생성부터 primary/backbuffer의 Blt/BltFast/Flip까지 동일 run/tick으로 연결할
수 있다.

허용 변경:

- `tools/inmm_stub/`에 환경변수로만 활성화되는 G1 DirectDraw trace 모듈과 빌드 입력 추가.
- `tools/runtime_env.py`에 instrumented manifest 전용 `g1-presentation-trace` 실행/수집/검증 경계.
- 구조화 로그 validator와 회귀 테스트. 기존 유틸리티를 우선 재사용하며 새 dependency는 금지.
- `analysis/memory_maps/`에는 runtime으로 확인한 주소만 SHA·old bytes·출처와 함께 추가.

금지 변경:

- 원본/참고 EXE·DLL·game data, candidate, resolution bytes, baseline/golden, 5입력 좌표/판정 완화.
- 기존 `g1-baseline` FAIL을 PASS로 변경하거나 diagnostic bridge 장면을 stock 실행으로 표기.
- 외부 wrapper/복수 mode 지원/실제 2배 출력 구현. 필요해지면 Astra로 재이관한다.

## 선행 정적 guard

두 고정 원본을 모두 다시 확인한다.

- source와 새 private copy SHA256:
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp=0`, PE32.
- `.text` VMA/file offset/size: `0x00401000` / `0x1000` / `0xE3AE5`.
- `DDRAW.dll!DirectDrawCreateEx` named import 및 IAT thunk
  `0x004D7938: ff 25 18 50 4e 00`.
- caller `0x00464374: e8 bf 35 07 00`; IID pointer `0x004E5928`는 실제 raw GUID도 로그한다.
- mode3: `0x00464502: c7 46 04 20 03 00 00`,
  `0x00464509: c7 46 08 58 02 00 00`.

위 값 하나라도 다르면 hook/게임 실행 전에 non-retryable BLOCKED로 끝낸다. `+0x14/+0x2c`
generic 49/14개는 회귀 수치일 뿐 interface 의미나 breakpoint allowlist로 사용하지 않는다.

## 관측 구현 계약

`SYW2_G1_PRESENT_TRACE=1`일 때만 다음을 설치한다. 설치 실패나 부분 설치를 계속 진행하지 않는다.

1. EXE import table에서 이름과 기존 target module range를 확인한 뒤 `DirectDrawCreateEx` IAT를
   감싼다. 반환 HRESULT, IID, object, vtable, return address를 기록한다.
2. 실제 반환 object의 vtable에서 `SetDisplayMode`와 `CreateSurface`를 감싼다. 고정 offset만으로
   interface 이름을 붙이지 말고, 위 IID와 호출 결과의 identity chain이 성립한 뒤 의미를 부여한다.
3. 성공한 `CreateSurface`마다 요청 `DDSURFACEDESC2`와 반환 surface object/vtable을 기록하고,
   해당 실제 vtable의 `GetSurfaceDesc`, `Blt`, `BltFast`, `Flip`만 감싼다.
4. wrapper는 원 함수를 정확히 한 번 호출하고 HRESULT를 그대로 반환한다. 원본 인자·surface
   memory·게임 bytes를 바꾸지 않는다. 재진입 guard, vtable 중복 patch guard, VirtualProtect
   원복, FlushInstructionCache와 설치 결과를 기록한다.
5. 상세 이벤트는 method당 최대256개, 전체 최대2048개다. 이후에는 `overflow` 한 건과 count만
   남긴다. overflow가 scene 연결 전에 발생하면 결과는 BLOCKED다.

기존 diagnostic `_inmm.dll`은 stock `_inmm.dll`과 다르고 asset/SFX/MessageBox hook도 포함하므로
fixture를 `diagnostic_bridge=true`로 명시한다. uninstrumented lap73과 PS9→PS3, renderer 800×600,
X11 800×600 content, hashed builtin `ddraw.dll` 관계가 달라지면 원본 presentation 근거로 쓰지 않는다.

## 필수 로그 스키마

모든 JSONL event: `schema`, `run_id`, `seq`, `ts_ms`, `pid`, `thread_id`, `program_state`,
`game_tick`, `event`, `install_status`.

- `direct_draw_create_ex`: EXE caller/return address, IID raw GUID, HRESULT, DD object/vtable.
- `set_display_mode`: object, width/height/bpp/refresh/flags, caller, HRESULT.
- `create_surface`: DD object, descriptor flags/width/height/backbuffer_count/caps/pixel format,
  returned surface/vtable, caller, HRESULT.
- `get_surface_desc`: surface, 실제 width/height/pitch/caps/pixel format, caller, HRESULT.
- `blt`/`blt_fast`/`flip`: destination `this`, source/target object, rect pointer와 4개 값 또는
  명시적 null, flags, EXE caller/return address, HRESULT.
- `install`/`summary`/`overflow`: old target module/range, patched slot, 원 pointer, event count,
  dropped count, detach/flush 결과.

host 증거에는 같은 `run_id`의 manifest/EXE/diagnostic DLL/runtime harness/builtin ddraw SHA,
PS/tick renderer 값, root/client/content 크기, 캡처 경로·SHA, trace SHA, 명령·환경·fixture와 cleanup을
기록한다. 캡처의 game tick과 trace event의 game tick으로 장면을 연결한다.

## 명령과 순서

work tier가 실제 구현에 맞춰 CLI 세부 이름을 추가할 수 있으나 아래 순서와 상한은 바꾸지 않는다.

1. trace validator/guard 단위 테스트와 diagnostic DLL private build. 빌드 출력은 저장소 밖 새
   `mktemp -d`에만 두고 DLL/manifest SHA를 기록한다.
2. `.venv/bin/python -m pytest -q`로 새 targeted tests. 실패 시 재시도/게임 실행 금지.
3. `make check`, `bash checks/safety.sh check`. 예상 밖 실패 시 그대로 보존하고 종료.
4. 새 전체 copy/private win32 prefix/빈 Xvfb만 `prepare --bridge <new DLL>`로 만든 뒤
   `check`와 `make doctor-runtime MANIFEST=<new manifest>`를 통과시킨다.
5. `g1-presentation-trace --manifest <new manifest> --screen 1600x1200x24 --timeout 90` 한 번.
   PS9→기본 2-player PS3 장면까지만 사용하며 production/drag/minimap fixture는 호출하지 않는다.
6. owned launcher, 해당 prefix wineserver, 해당 Xvfb만 종료한다. 전역 pkill/기존 display 연결 금지.

첫 조사 상한은 60~90분, live 실행은 90초 1회다. 필수 gate 예상 밖 실패는 첫 실패에서 멈춘다.

## PASS / BLOCKED와 인계

조사 PASS는 동일 run에서 다음이 모두 성립할 때뿐이다.

- IID로 확인된 DD object → 실제 CreateSurface 반환 surface → actual desc/caps → 실행된
  Blt/BltFast/Flip 중 최종표시 역할 event → PS3 캡처/client 크기가 identity와 tick으로 연결된다.
- 선택된 mode와 복수 surface 단계를 구분하고, rectangle 값 또는 null/implicit semantics를
  그대로 설명한다. 전역 단일 호출이나 1600×1200 destination은 요구하지 않는다.
- module/fixture/log hash와 cleanup이 완전하고 uninstrumented lap73 경계와 차이를 공개한다.

hook 설치/identity chain/actual desc/present event/화면 연결 중 하나라도 없거나 log overflow,
crash, timeout, cleanup 실패가 있으면 **UNKNOWN/BLOCKED**다. 같은 lap에서 generic 후보를 다시
세거나 hook method를 임의 확대하지 않는다. 현 변경·로그를 보존하고 `loop/ESCALATE_SOL`을 만들어
새 Sol/high가 원시 증거와 instrumentation side effect를 검수하게 한다.

PASS여도 제품/계획 승인으로 승격하지 않는다. 다음 새 Sol/high가 독립 검수한 뒤에만 정수2배
적용 위치·입력 역변환·창 정책을 별도 변경 카드로 만들 수 있다.
