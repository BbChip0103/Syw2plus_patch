# G1 W50B — native 1600 primary + 원본 800 blit 2배 가능성 (lap605 middle 발행, 2026-09-25 KST)

- 발행: lap605 middle. 실제 모델은 Codex native 중간 tier(모델 ID·effort 비노출). 게임 실행·제품/하네스 source·binary 변경 0.
- 근거: `docs/STATUS.md` 2026-09-25 12:25 운영자 결정, `G1_STRATEGY_W50_HD_FINAL_OUTPUT_ACQUISITION_LAP596.md` §6, `G1_STRATEGY_W50RX_HARNESS_EXCEPTION_LAP602.md` §4, `loop/ESCALATE_SOL` §154.
- 수행 역할: **work**(Codex `gpt-5.6-luna`, high). 계획 회차를 끼우지 않는다. 그다음 새 middle이 raw를 독립 검수한다.
- 목표/중단점: 원본 내부 800×600 합성은 유지하고 native DirectDraw primary만 1600×1200으로 만든 뒤, 기존 최종 `Blt`가 원본 한 프레임을 정수 2배로 전사할 수 있는지 **60분 또는 실패 가설 2회 중 먼저 도달할 때** `FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED`로 판정한다.

## 1. 이미 고정된 경계

핀 원본 SHA-256은 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`이다.

1. `0x00464564..0x0046457C`는 renderer의 `+0x04/+0x08/+0x0C`(800/600/8)를 인자로 `IDirectDraw7::SetDisplayMode`(`vtable+0x54`)를 호출하고 return VA는 `0x0046457D`다. 이 호출 뒤 게임 필드는 그대로 남는다.
2. `FUN_004922D0`은 `DAT_0104FB2C` offscreen을 `max(renderer.width,832) × renderer.height`로 만든다. 원본이면 832×600이다.
3. PS3 최종 전사 `0x0041C3C4..0x0041C3E3`은 destination `DAT_00E5D434`, source `DAT_0104FB2C`, destination rect `NULL`, source rect `(0,DAT_008929A0,renderer.width,renderer.height)`, flags `0x01000000`으로 `IDirectDrawSurface7::Blt`(`vtable+0x14`)를 정확히 한 번 호출한다. return VA는 `0x0041C3E4`다.
4. 기존 `direct_draw_trace.c`는 실제 `SetDisplayMode/CreateSurface/GetSurfaceDesc/Blt`를 typed vtable로 관측하고 원본 메서드를 한 번 전달한다. 기본 OFF다.

따라서 첫 가설은 전역 1600 패치 74곳을 다시 쓰는 것이 아니다. **게임이 요청한 800×600×8 값은 trace에 보존하되, 정확한 SetDisplayMode 호출에만 1600×1200×8을 전달**한다. 그러면 게임 renderer/offscreen은 800계열로 남고 primary만 native 1600이 될 수 있다. 이 분리가 raw로 성립하는지가 이번 카드의 질문이다.

## 2. 허용 변경

### H1 — split-mode 전달(첫 가설)

`tools/inmm_stub/direct_draw_trace.c`와 전용 회귀 테스트에 새 명시 opt-in `SYW2_G1_NATIVE_2X_BLIT=1`을 추가한다.

- 플래그 없음: 현재처럼 요청 width/height/bpp를 그대로 정확히 한 번 전달한다.
- 플래그 있음: 아래를 **모두** 만족할 때만 `(800,600,8)` 대신 `(1600,1200,8)`을 원본 `SetDisplayMode`에 정확히 한 번 전달한다.
  - 핀 원본 image base/호출 old bytes가 §1과 일치.
  - 요청이 정확히 800×600×8이고 return address가 `0x0046457D`.
  - refresh/flags는 바꾸지 않는다.
- trace에는 `requested_width/height/bpp`, `forwarded_width/height/bpp`, `native_2x_opt_in`, caller, HRESULT를 함께 남긴다. 조건 불일치는 원값 전달+구조화된 skip이며 성공으로 세지 않는다.
- exact PS3 present call(`return_address=0x0041C3E4`)에서만 원본 `GetSurfaceDesc` 포인터로 destination/source desc를 읽어 HRESULT와 함께 기록한다. `Blt` 인자·surface·refcount·vtable은 바꾸지 않고 원본 `Blt`는 정확히 한 번만 호출한다.

`tools/runtime_env.py`에는 ambient env에 기대지 않는 `g1-presentation-trace --native-2x-blit` 명시 플래그를 추가한다. 이 플래그는 위 env를 정확히 `1`로 설정하고 evidence/provenance에 기록하며 `--dxwrapper-2x`와 동시 사용을 거부한다. `observational_only`는 false로 기록하고 개입 범위를 SetDisplayMode 전달값 한 건으로 공개한다.

### H2 — 명시 destination rect(조건부 두 번째 가설)

H1 raw에서 primary=1600×1200, source=832×600, source rect=800×600, exact caller/HRESULT=0가 모두 성립했는데도 `destination_rect=NULL`이 full-primary 2배 전사로 작동하지 않은 경우에만 허용한다.

- 별도 opt-in `SYW2_G1_NATIVE_2X_DSTRECT=1`과 CLI `--native-2x-dstrect`로 exact `0x0041C3E4` call에 한해 local destination rect `{0,0,1600,1200}`을 전달한다. 이 CLI는 `--native-2x-blit` 없이는 거부한다.
- H1의 surface/rect/flags gate가 하나라도 다르면 H2를 실행하지 않는다.
- 다른 `Blt/BltFast`, renderer field, source rect, sprite draw, primary pixels를 건드리지 않는다. fresh 두 번째 실행이 최종이다.

## 3. 실행 전 회귀

최소 회귀는 다음을 잠근다.

1. 기본 OFF와 비대상 mode/caller/bpp는 인자를 byte-for-byte 그대로 한 번 전달한다.
2. H1 exact gate만 800×600×8 요청을 1600×1200×8로 전달하며 refresh/flags를 보존한다.
3. trace가 requested/forwarded 값을 분리하고, exact present desc 관측은 쓰기·추가 `Blt`·추가 refcount 변경을 하지 않는다.
4. `--native-2x-blit`과 `--dxwrapper-2x` 동시 사용을 거부하고 provenance에 opt-in을 남긴다. `--native-2x-dstrect` 단독 사용도 거부한다.
5. PE32 bridge build, targeted tests, `checks/safety.sh check`가 PASS해야 fresh를 시작한다.

하나라도 실패하면 게임을 띄우지 않고 `BLOCKED(preflight:<이유>)`로 보존·승격한다. 테스트를 통과시키려고 기존 pin/baseline을 갱신하지 않는다.

## 4. fresh 실행(동기 foreground, 최대 2회)

- 읽기 전용 원본에서 새 전체 게임 사본·새 win32 prefix·빈 Xvfb display를 만든다. runtime root는 validator가 허용하는 `local/runtime/<run>/game` direct-child 형태로 고정하고 W50R/W50RX 산출물은 재사용하지 않는다.
- 새 bridge만 private 사본에 설치한다. 원본 EXE를 실행하며 `ddraw=b`; DxWrapper/native1600 EXE patch/새 DLL·Wine/의존성은 사용하지 않는다.
- H1을 정확히 1회 실행한다. PS9→PS7→PS5→PS3, tick>0, PS3 neutral capture까지 완료한다. 한 실행 ≤15분, 전체 회차 ≤60분이다. 셸 background 금지.
- H2 조건이 정확히 성립하고 시간이 남을 때만 fresh H2를 정확히 1회 실행한다. 그 외 blind retry는 없다.
- 캡처는 공유 `temp/Syw2plus_patch/captures/`에 `YYYYMMDD_HHMMSS_` 접두사로 보존하고 manifest/raw/evidence/provenance/cleanup SHA를 기록한다.

## 5. 실행 전 판정식

### `FEASIBLE(native_1600_blit_2x)`

같은 fresh run에서 모두 성립해야 한다.

1. exact SetDisplayMode event가 requested `800×600×8`, forwarded `1600×1200×8`, HRESULT 0, return VA `0x0046457D`다.
2. PS3 renderer는 width=800, height=600, bpp=8을 유지한다. exact present source desc는 width=832, height=600이고 source rect의 유효 크기는 800×600이다.
3. exact `0x0041C3E4` present destination desc는 1600×1200, flags `0x01000000`, `Blt` HRESULT 0다. H1은 destination rect NULL, H2는 정확히 full 1600 rect다.
4. PS3 tick>0이고 1600×1200 캡처에 월드/HUD가 보인다. 2×2 block-equality와 `800×600 top-left downsample → nearest 2× re-expand` pixel equality가 각각 **≥0.999**다. 검정/단색 화면은 기각한다.
5. 원본 EXE SHA 전후 동일, private bridge/manifest SHA 일치, DxWrapper 미로드, owned prefix/display 잔류0이다.

이 판정은 **whole-frame 2배 전사 가능성**만 뜻한다. HD SPR 디테일, 원본/후보 입력 전체, painter order, W51, G1 PASS, 사용자 승인이 아니다.

### `NOT_FEASIBLE(native_1600_blit_2x)`

H1과, 그 사전조건이 성립한 경우의 H2까지 수행했으며 exact raw가 다음 중 하나를 구조적으로 보일 때만 사용한다: primary가 1600으로 분리되지 않음, renderer/source가 800계열로 유지되지 않음, exact final `Blt`가 full-primary 2배 전사를 지원하지 않음. H2 사전조건이 성립하지 않는 구조적 반증에는 H2를 억지로 실행하지 않는다. 하네스/입력/시간 실패를 불가능으로 쓰지 않는다.

### `BLOCKED(<이유>)`

preflight·private 실행·PS3 입력·trace finalization·cleanup 실패, 또는 H2 조건 미성립 상태에서 H1이 판별력을 주지 못한 경우다. 보존 후 재시도하지 않는다.

## 6. 금지와 다음 handoff

- 원본/참고 저장소 쓰기, 원본 EXE patch, `native_1600_probe.py` 후보 실행, DxWrapper 2× 혼합, primary 직접 pixel write, 마지막-pass 임의 overlay, HD asset/SPR 합성, CAS/W50S/W51, 새 dependency, baseline/golden 갱신, 커밋, G1 PASS 주장을 금지한다.
- 기존 G2 산출물과 W50R/W50RX raw를 바꾸거나 삭제하지 않는다.
- 결과와 무관하게 다음 새 middle이 summary가 아닌 raw event/desc/capture/SHA로 §5를 독립 재계산한다.
- middle이 `FEASIBLE`을 ACCEPT하기 전에는 HD detail/SPR identity 합성 카드를 발행하지 않는다. `NOT_FEASIBLE`/`BLOCKED`가 ACCEPT되면 그때 strategy가 G1 지속 또는 G4 전환을 판정한다.
