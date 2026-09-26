# 2026-09-16 — G1 DxWrapper 최종 합성 경계 공식 근거

- **판정:** `BLOCKED_FINAL_SURFACE_OR_COMPOSITION_ORDER`
- **담당/범위:** Luna/high, 공식 upstream primary-source 확인 및 로컬 pinned artifact 대조만 수행.
- **금지/미실행:** 게임 실행, runtime/source/바이너리/ini 변경, 새 dependency·build, commit/push 없음.
- **질문:** private DxWrapper 2x profile의 최종 Dd7to9 surface/device/present 경계가 원본 HUD SPR 한 개(frame `0x24`)의 high-resolution replacement 또는 post-upscale compositor 연결점이 될 수 있는가?

## 결정 요약

정확한 private DLL은 PE version resource와 timestamp로 공식 release `v1.0.6542.21`과 강하게 일치한다. 해당 tag의 소스에서 다음 흐름은 닫힌다.

1. 게임의 DirectDraw `Blt`는 wrapper의 `CopySurface`로 surface 내용을 갱신하고 `EndWritePresent`를 호출한다.
2. primary surface의 D3D9 `surfaceTexture`/선택적 `displayTexture`는 surface description의 크기로 생성된다. 이 후보의 논리 원본 surface는 로컬 증거상 `800x600`이다.
3. primary present는 texture를 바인딩한 textured primitive를 그린 뒤 D3D9 device `Present(nullptr, nullptr, nullptr, nullptr)`를 호출한다.
4. `DdrawUseNativeResolution`은 display/back-buffer 크기를 monitor 기준으로 정하고, integer clamp/aspect 옵션은 그 원본 texture를 최종 display에 배치한다.

따라서 최종 wrapper surface를 가로채는 것만으로는 이미 원본 `800x600`에 합성된 SPR의 identity/frame을 복원할 수 없다. whole-frame texture override는 whole composed frame 교체이지 SPR replacement가 아니다. 이 exact version의 config/source inventory에는 per-SPR identity map, 고해상도 texture replacement API, post-upscale composition callback이 문서화되어 있지 않다. 그러므로 이 카드에서는 G1 연결을 **BLOCKED**로 유지한다.

## 두 가설과 결과

| 가설 | 확인 근거 | 결과 |
|---|---|---|
| H1. `Dd7to9=1` + native resolution/integer scaling이 최종 compositor가 되어 한 SPR을 1600 destination에서 대체한다. | config는 DirectDraw→D3D9 변환과 display scaling만 설정한다. tag 소스는 primary surface texture를 그려 Present한다. | **기각.** 최종 입력이 이미 합성된 원본 surface이고 SPR identity 경계가 없다. |
| H2. wrapper는 원본 surface를 texture로 복사·스케일·present하고, SPR 단위 replacement는 게임-side composition 이전에 해야 한다. | `Blt → CopySurface → EndWritePresent`; `surfaceTexture/displayTexture → textured primitive → D3D9 Present`; native/integer 옵션은 display 배치만 변경. | **현재 증거와 일치.** 단, 실제 게임 draw hook/paint order/mask/clip ABI는 별도 조사 미완료이므로 구현 승인 아님. |

## 로컬 provenance (읽기 전용 확인)

| 항목 | 관측값 / 의미 |
|---|---|
| private `dxwrapper.dll` | SHA-256 `96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe`; PE32 i386; version resource `FileVersion/ProductVersion 1.0.6542.21`; PE timestamp 2021-05-30 (local `objdump -p` 관측). |
| private stub `ddraw.dll` | SHA-256 `3bc7230d1a6023a8fc0ea52b18d7edda94fcb4c0ae3d178f6e1577d68a62bd19`; PE32 i386. |
| private original `dxwrapper.ini` | SHA-256 `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`. |
| approved candidate ini | SHA-256 `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`; `Dd7to9=1`, `DdrawUseNativeResolution=1`, `DdrawIntegerScalingClamp=1`, `DdrawMaintainAspectRatio=1`; target display `1600x1200`, source composition `800x600`. |
| exact upstream version basis | Official release `v1.0.6542.21`, published 2021-05-30, tag commit short `6be8057`. PE version/timestamp agree with this release. |
| binary linkage limitation | GitHub release API exposes zip assets but no digest used here to prove private DLL SHA equals a particular release zip. Thus this is a strong version/resource basis, not byte-identical release-asset proof. |
| game-side anchor | Local G1 evidence records `0x43F250 → 0x419D80(10,3,0x24,0)`. Local follow-up now binds this call to `fnt/resource.spr`, frame `0`, size `20x24`, with mask area `315`; draw-order/ABI ownership is still a separate question. |

## 공식 upstream facts (exact tag 우선)

- [DxWrapper `v1.0.6542.21` release](https://github.com/elishacloud/dxwrapper/releases/tag/v1.0.6542.21) identifies the pinned upstream version and release date. Current master/recent releases are not substituted for this private binary.
- [Exact-tag `Settings.ini`](https://github.com/elishacloud/dxwrapper/blob/v1.0.6542.21/Settings/Settings.ini#L1-L95) exposes `LoadCustomDllPath`, plugin loading, `Dd7to9`, and scaling controls. `LoadPlugins` loads custom `.asi` libraries; it does not define an SPR identity/replacement callback.
- [Exact-tag `IDirectDrawSurfaceX.cpp`](https://github.com/elishacloud/dxwrapper/blob/v1.0.6542.21/ddraw/IDirectDrawSurfaceX.cpp#L424-L504) implements the DirectDraw surface write path. In the tag source, `Blt` calls `CopySurface` (raw source lines 424–484), then marks dirty and calls `EndWritePresent` (lines 491–504); `BeginWritePresent`/`EndWritePresent` wrap `PresentSurface` (lines 4053–4075).
- [Exact-tag surface creation/present](https://github.com/elishacloud/dxwrapper/blob/v1.0.6542.21/ddraw/IDirectDrawSurfaceX.cpp#L2810-L2895) creates primary `surfaceTexture` (and, where applicable, `displayTexture`) using adjusted `surfaceDesc2.dwWidth/dwHeight`; [primary `PresentSurface`](https://github.com/elishacloud/dxwrapper/blob/v1.0.6542.21/ddraw/IDirectDrawSurfaceX.cpp#L3392-L3527) binds that texture, uses point filtering, and delegates to the parent present.
- [Exact-tag D3D9 present](https://github.com/elishacloud/dxwrapper/blob/v1.0.6542.21/ddraw/IDirectDrawX.cpp#L2987-L3062) begins/ends the D3D9 scene, draws the textured primitive, and calls `d3d9Device->Present(nullptr, nullptr, nullptr, nullptr)`.
- [Exact-tag native display sizing](https://github.com/elishacloud/dxwrapper/blob/v1.0.6542.21/ddraw/IDirectDrawX.cpp#L2097-L2105) obtains monitor dimensions when `DdrawUseNativeResolution` is enabled; this is display/back-buffer sizing, not a per-asset identity mechanism.
- The [official Configuration wiki](https://github.com/elishacloud/dxwrapper/wiki/Configuration) defines `Dd7to9` as DirectX 1–7 to D3D9 conversion, `DdrawUseNativeResolution` as stretching to monitor resolution, and integer/aspect controls as scaling/border behavior. It also describes `DdrawWriteToGDI` as a special surface-to-GDI path, not a post-upscale sprite compositor.
- A later maintainer discussion ([#439](https://github.com/elishacloud/dxwrapper/discussions/439)) describes later dev-build render-target/texture-to-back-buffer changes. It is useful corroboration that a final whole-frame boundary exists, but it is **not** evidence of behavior in the pinned 2021 binary and does not establish a sprite callback.

## Surface identity boundary

```
game SPR draw calls / palette / clip / paint order
        ↓
original DirectDraw primary surface (logical 800x600; already composed)
        ↓  Blt / CopySurface / surfaceTexture (Dd7to9)
wrapper D3D9 textured primitive (scaled destination)
        ↓
d3d9Device->Present (final display)
```

The local HUD candidate call’s `0x24` is before the final surface boundary and is now locally bound to `fnt/resource.spr` frame `0` (`20x24`, mask area `315`), but that identity is not visible as a distinct object after the game has composed the primary surface. Replacing the final texture would replace all pixels (world, HUD, cursor, menus, overlap), not only that SPR/frame. `DdrawWriteToGDI` similarly changes transport/present behavior and is not an identity-aware callback.

## 최소 viable connection (future only; not activated)

The narrowest credible route is a **game-side draw hook before the original 800x600 composition** for one proven sprite identity: retain original logical layout and paint order, bind the actual frame/palette/silhouette/clip, and render that one detail into a native `1600x1200` destination or a pre-present composition surface. The final DxWrapper present can remain unchanged. A wrapper-only `Present`/primary-surface hook is insufficient; an identity-aware custom source hook would require a separately pinned source/build and an approved ABI/ordering plan.

The local slot/frame identity is now recorded as `fnt/resource.spr` frame `0` (`20x24`, mask area `315`); this does not claim that a high-resolution replacement is implemented.

## Limitations / next gate

- Runtime/source/build/game execution was intentionally not performed; no G1 visual or quality proof is produced.
- Private DLL SHA was not cryptographically compared with the upstream release zip asset; version resource and release tag are the available basis.
- No upstream API in this exact config/source inventory binds an original SPR identity, frame, palette, mask, or post-upscale callback. Custom `.asi` loading alone is not that contract.
- Local resource identity for frame `0x24` is closed as `fnt/resource.spr` frame `0` (`20x24`, mask area `315`); exact game-side draw ABI, clipping/paint order, and final compositing ownership remain unknown.
- The wrapper’s later upstream master/discussion behavior must not be backported by assumption.
- Next gate: Sol/Astra must independently pin the pre-composition draw boundary and provide paired actual OFF/ON evidence (unchanged outside mask, native adjacent-pixel detail, no menu/cursor overwrite/ghosting) before any implementation/product activation.

This is an operational provenance association for the same private profile/version basis; it is not a G1 product PASS.

## D3D9 live identity trace — ABI gate (official Microsoft + installed header)

The following is a **supporting contract for the separate opt-in live D3D9 trace lane**, not a product implementation or a replacement for the game-side SPR identity. It must observe the wrapper's actual returned COM objects; it must not create a dummy device merely to obtain a vtable.

### Factory/device acquisition

- [Microsoft `Direct3DCreate9`](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-direct3dcreate9) declares `IDirect3D9 *Direct3DCreate9(UINT SDKVersion)`. Success returns a real `IDirect3D9*`; failure returns `NULL`. Resolve the DLL export dynamically and record the returned pointer. The optional [Microsoft `Direct3DCreate9Ex`](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-direct3dcreate9ex) path returns an `HRESULT` and `IDirect3D9Ex**`; if no typed Ex path is available, record structured `D3D9EX_UNSUPPORTED`/SKIP rather than aliasing it to a fabricated type.
- [Microsoft `IDirect3D9::CreateDevice`](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3d9-createdevice) is:

  ```c
  HRESULT CreateDevice(
      UINT Adapter, D3DDEVTYPE DeviceType, HWND hFocusWindow,
      DWORD BehaviorFlags, D3DPRESENT_PARAMETERS *pPresentationParameters,
      IDirect3DDevice9 **ppReturnedDeviceInterface);
  ```

  It mutates the in/out `D3DPRESENT_PARAMETERS` and returns the actual `IDirect3DDevice9*` through the out pointer. The installed MinGW declaration agrees at `/usr/x86_64-w64-mingw32/include/d3d9.h:198`; interface methods use `STDMETHODCALLTYPE` (`WINAPI`, `/usr/x86_64-w64-mingw32/include/winnt.h:440`).
- [Microsoft `IDirect3D9Ex::CreateDeviceEx`](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3d9ex-createdeviceex) adds `D3DDISPLAYMODEEX *` and returns typed `IDirect3DDevice9Ex**`. Do not call the 9 signature against an Ex vtable or infer Ex from a non-Ex pointer. The installed header places `CreateDevice` in the inherited `IDirect3D9` slot 16 (IUnknown slots 0–2) and `CreateDeviceEx` in the Ex extension slot 19 (after `EnumAdapterModesEx` slot 17 and `GetAdapterDisplayModeEx` slot 18).

### Typed methods and vtable positions

The installed MinGW `d3d9.h` (`DECLARE_INTERFACE_`) gives the ABI below. Slot numbers are zero-based and include the three IUnknown entries; they are a vtable layout aid, not permission to call an untyped/dummy object.

| Interface/method | Typed signature (header spelling) | Slot | Required interpretation |
|---|---|---:|---|
| `IDirect3DDevice9::Reset` | `HRESULT (STDMETHODCALLTYPE *)(IDirect3DDevice9*, D3DPRESENT_PARAMETERS*)` | 16 | in/out presentation parameters; preserve and record HRESULT; a reset starts a new resource generation. |
| `IDirect3DDevice9::Present` | `HRESULT (STDMETHODCALLTYPE *)(IDirect3DDevice9*, const RECT*, const RECT*, HWND, const RGNDATA*)` | 17 | exactly one forward call; NULL rectangles mean the full source/client region per Microsoft. |
| `IDirect3DDevice9::GetBackBuffer` | `HRESULT (STDMETHODCALLTYPE *)(IDirect3DDevice9*, UINT, UINT, D3DBACKBUFFER_TYPE, IDirect3DSurface9**)` | 18 | returns a referenced surface on success; every successful capture must call that surface's `Release` exactly once. |
| `IDirect3DDevice9::GetViewport` | `HRESULT (STDMETHODCALLTYPE *)(IDirect3DDevice9*, D3DVIEWPORT9*)` | 48 | write only on successful call; record `D3DVIEWPORT9` and HRESULT. |
| `IDirect3DDevice9Ex::PresentEx` | `HRESULT (STDMETHODCALLTYPE *)(IDirect3DDevice9Ex*, const RECT*, const RECT*, HWND, const RGNDATA*, DWORD)` | 121 | Ex-only five-argument presentation plus flags; only call on a proven typed Ex vtable. |
| `IDirect3DDevice9Ex::ResetEx` | `HRESULT (STDMETHODCALLTYPE *)(IDirect3DDevice9Ex*, D3DPRESENT_PARAMETERS*, D3DDISPLAYMODEEX*)` | 132 | Ex reset starts/retains resources under its distinct contract; preserve HRESULT and generation. |
| `IDirect3DSurface9::GetDesc` | `HRESULT (STDMETHODCALLTYPE *)(IDirect3DSurface9*, D3DSURFACE_DESC*)` | 12 | inherited `IDirect3DResource9` occupies slots 3–10; record width/height/format/pool only after `D3D_OK`. |
| `IUnknown::Release` (all listed interfaces) | `ULONG (STDMETHODCALLTYPE *)(IUnknown*)` | 2 | decrements COM reference count; return count is diagnostic only and must not drive ownership decisions. |

The signatures and ordering above are directly visible in the installed header: `IDirect3DDevice9` declarations at lines 1207–1252 and `IDirect3DSurface9` declarations at lines 419–445. The target binary is PE32, so the eventual i686 build must validate the same `STDMETHODCALLTYPE`/pointer ABI; only an x86_64 MinGW header is installed in this environment, and no 32-bit compile proof is claimed here.

Microsoft's [Present reference](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-present) specifies the five-argument HRESULT signature and says a stretch may occur from source to destination. [Reset](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-reset) specifies that default-pool/texture memory and device state can be lost and that Reset must run on the device-creation thread. [GetBackBuffer](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-getbackbuffer) explicitly says the returned surface reference count is incremented and must be released. [GetDesc](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3dsurface9-getdesc) and [GetViewport](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9-getviewport) return `HRESULT` and populate caller-owned output structs. The [IUnknown contract](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nn-unknwn-iunknown) makes QueryInterface/AddRef/Release the first three vtable entries; [Release](https://learn.microsoft.com/en-us/windows/win32/api/unknwn/nf-unknwn-iunknown-release) frees the object when its count reaches zero.

### Trace safety rules

1. **Actual-object only:** resolve `Direct3DCreate9`/optional `Direct3DCreate9Ex` exports dynamically; observe the actual returned `IDirect3D9`/typed Ex and the actual device returned by `CreateDevice`/`CreateDeviceEx`. The current discovery says the D3D9 import table is absent; an IAT-only search is therefore not a valid negative result.
2. **Exactly-once forwarding:** each hooked factory/device method forwards once with the original arguments and returns the original HRESULT. No dummy device, recursive self-call, or scalar “false success” is permitted.
3. **Vtable alias/generation safety:** clone/alias only the actual typed interface vtable. Keep the device generation identity; after successful `Reset`/`ResetEx`, invalidate cached back-buffer/surface pointers and reacquire them. Do not use a pre-reset surface in a later generation.
4. **Back-buffer ownership:** a successful `GetBackBuffer` owns one additional surface reference. Call typed `IDirect3DSurface9::Release` exactly once after `GetDesc`/capture; do not release on failed acquisition or release the same pointer in both the method hook and asynchronous consumer.
5. **HRESULT-first records:** record method, generation, thread id, input summary, HRESULT, and output-validity. Parse dimensions/viewport only for successful calls; preserve `D3DERR_*`/`E_*` without coercion to Boolean.
6. **Thread/lost-device gate:** CreateDevice, Reset, and device operations must respect the Microsoft same-thread requirement. If Reset fails, only the documented recovery/reset/test/release subset is safe; the trace must stop querying stale surfaces and emit a structured gap.
7. **Present/reset variants:** for a typed `IDirect3DDevice9Ex`, trace `PresentEx` (slot 121) / `ResetEx` (slot 132) with their actual five-/two-argument signatures. Microsoft documents [PresentEx](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9ex-presentex) and [ResetEx](https://learn.microsoft.com/en-us/windows/win32/api/d3d9/nf-d3d9-idirect3ddevice9ex-resetex) separately. If Ex cannot be proven, emit structured `D3D9EX_UNSUPPORTED` rather than calling guessed extension slots.

This ABI lane can establish the actual final D3D9 target/device/present surface and its lifetime, but it still cannot prove that a final-surface write corresponds to `fnt/resource.spr` frame `0`. That identity remains at the pre-composition game draw boundary.

## Wine PE loader/ImageBase 확인 (별도 read-only upstream lane)

### 사실

- 로컬 runtime은 `wine-9.0 (Ubuntu 9.0~repack-4build3)`이다. Wine upstream `wine-9.0`의 [`dlls/ntdll/unix/virtual.c`, `map_image_into_view`](https://gitlab.winehq.org/wine/wine/-/blob/wine-9.0/dlls/ntdll/unix/virtual.c#L2877-2895)는 dynamic relocation 조건 `image_info->map_addr && (delta = image_info->map_addr - image_info->base)`에서 32-bit/64-bit 분기를 거쳐 **mapped PE header의 `OptionalHeader.ImageBase`를 `image_info->map_addr`로 대입**한 뒤, `.reloc` directory를 순회하며 `process_relocation_block(..., delta)`를 수행한다(실제 loaded view의 pointer인 `ptr`를 별도 인자로 사용).
- 같은 upstream의 [`map_image_view`](https://gitlab.winehq.org/wine/wine/-/blob/wine-9.0/dlls/ntdll/unix/virtual.c#L2978-3034)는 우선 `image_info->map_addr`에 map을 시도한다. [`virtual_map_image`](https://gitlab.winehq.org/wine/wine/-/blob/wine-9.0/dlls/ntdll/unix/virtual.c#L3043-3100)는 성공한 view의 `view->base`를 caller에게 반환한다.
- Wine server의 [`get_image_map_address`](https://gitlab.winehq.org/wine/wine/-/blob/wine-9.0/server/mapping.c#L1315-1330)는 dynamic image의 `map_addr`를 할당·반환한다. 이어 [`map_image_view` handler](https://gitlab.winehq.org/wine/wine/-/blob/wine-9.0/server/mapping.c#L1388-1410)는 성공 view의 `view->base`가 dynamic `mapping->image.map_addr`와 다르면 `STATUS_IMAGE_NOT_AT_BASE`를 설정한다. 따라서 **성공한 upstream Wine dynamic-image mapping에서는 `map_addr == view->base`라는 source-level invariant가 성립**하고, 위의 `OptionalHeader.ImageBase = map_addr` 대입은 loaded base와 일치한다.
- 다만 Wine의 [`virtual_relocate_module`](https://gitlab.winehq.org/wine/wine/-/blob/wine-9.0/dlls/ntdll/unix/virtual.c#L3537-3568) 보조 경로는 module pointer와 header `ImageBase`의 delta를 계산하고 relocations를 적용하지만, 해당 함수 범위에는 header `ImageBase`를 다시 쓰는 대입이 없다. 그러므로 “Wine의 모든 relocation 경로가 항상 header를 loaded base로 덮는다”라고 일반화하지 않는다.

### Windows/native에 대한 경계

Microsoft의 [PE Format](https://learn.microsoft.com/en-us/windows/win32/debug/pe-format)와 [`IMAGE_OPTIONAL_HEADER32::ImageBase`](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-image_optional_header32)는 `ImageBase`를 **image가 memory에 load될 때 첫 byte의 preferred address**로 정의하고, image가 preferred base에 못 올라갈 때 loader가 base relocation을 처리한다고 설명한다. 이 공식 문서들은 native Windows loader가 mapped in-memory `OptionalHeader.ImageBase` field를 actual loaded base로 rewrite한다고 명시하지 않는다. 따라서 현재 증거로는:

- **Wine upstream `wine-9.0` normal mapped-image path:** 조건부로 **YES**, source-level loaded-base write가 확인됨.
- **Wine 전체 relocation 경로:** **조건부/경로 의존**; `virtual_relocate_module`에는 rewrite 근거 없음.
- **Windows native:** Microsoft 문서에서 relocation delta/semantics는 확인되지만 header-field rewrite 여부는 **미확정**. Wine 동작을 native Windows의 invariant로 이식하지 않는다.

### 현재 관측값의 안전한 해석

관측된 raw PE `ImageBase=0x10000000`와 Wine loaded module address `0x76FA0000`의 차이는 relocation이 발생했을 가능성과 일치한다. 그러나 현재 run에서 “memory OptionalHeader.ImageBase check failed”의 실제 read value가 기록되지 않았고, read가 실제 loaded module의 DOS/NT header를 가리켰는지·Wine package가 upstream tag와 byte-identical인지도 닫히지 않았다. 그러므로 이 source fact만으로 local check 결과를 PASS/FAIL 원인으로 단정하지 않는다. 다음 관측이 필요하다: 같은 module handle/base에서 `base + e_lfanew` 및 `OptionalHeader.ImageBase`를 함께 raw-log하고, Wine loader mapping record와 module identity를 동일 run에서 연결한다.

- **Confidence:** upstream `wine-9.0` source behavior는 **높음**(exact tagged source lines 확인); Ubuntu `9.0~repack-4build3`가 해당 source와 동일하다는 점은 **중간**(distro patch/different build bytes 미검증); 현재 local memory read의 원인은 **낮음/미결**(actual read value 미기록).
- **Scope boundary:** 이 확인은 DxWrapper/D3D9 trace 구현이나 runtime 변경을 승인하지 않으며, PE header observation 해석을 위한 factual prerequisite일 뿐이다.
