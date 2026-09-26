# Original PE32 QHD experiment — 2026-09-10

> **2026-09-10 사용자 정정:** 이 파일은 시야 확장 참고 실험이다. 원본 UI/스프라이트
> 상대 크기와 구도를 유지하는 실제 요구는 미충족. `PRODUCT_GOAL.md`가 현재 목표다.


Target SHA256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (`Syw2plus/syw2plus_original.exe`). Read-only pefile + Capstone x86 corroboration of Ghidra output. No original asset/binary writes.

## Verified patch surfaces

- Mode3 width immediate VA `0x464505`=800; height `0x46450c`=600. `FUN_004644a0.c:33-81`; raw `mov [esi+4],800`, `mov [esi+8],600`. Table `0x464b68`: modes 1..5=320x200,640x480,800x600,1024x768,1280x1024 (8-bit);6..8=640x480,800x600,1024x768 (16-bit). Not game-wide support evidence.
- Game init `FUN_0041b480.c:24-28` clip globals `0xb3ac80/84/88/8c`; right=831, bottom=511, renderer clip setter also receives these values.
- `0x432911/16/1b`: push 512,832,`0xba3d30`; call `0x464e00` (binder, NOT allocator). Static 832x512 terrain buffer ends `0xc0bd30` (another global pointer, `FUN_00431ab0.c:30`).
- `0x432954/59`: push 511,831 for renderer clip. `FUN_004324e0.c:200-205`.
- `0x43296c` follows clip call; branch to `0x433019` bypasses fixed scrolling/cache invalidation, leaving full terrain draw loop `FUN_004324e0.c:451-522`. Experiment deliberately trades original cache optimization for redraw.
- `0x41bf3f/44/49`: push terrain pointer,512,832 for final composite; `FUN_0041bf20.c:8-12`.
- Terrain scan bounds are camera +/-16: `FUN_004324e0.c:455-516` and preliminary scans before `0x432911`; overlay scans `FUN_004332f0.c:38-85` and subsequent loops. Capstone instruction operand patching expands bounds to +/-64, excluding pixel increment `0x43347c` and stack adjustment `0x434038`.
- Terrain dirty lookup `0x105796c` in `FUN_004351d0`, `00435680`, `00435b90`, `00435e40`, `004360f0`; clipping converts x/64,y/32 and indexes x*16+y. Experimental private 64KiB all-one mask eliminates dirty false skips while preserving bounded lookup storage. This is full redraw, not a production incremental-cache design.
- Offscreen surfaces follow display width/height (`FUN_004922d0.c:15-40`); Lock obtains actual pitch (`FUN_00464ec0.c:35-40`).

## Safety/validation contract

Experimental patch ONLY creates a distinct output from SHA-pinned original, adds a private `.qhd` PE section, saves explicit byte manifest and immutable backup, and offers SHA-checked restore. Original file is never overwritten. Runtime uses private copied data root, private Wine prefix, free Xvfb :193. Existing `_inmm.dll` control bridge is diagnostic navigation, not proof of stock startup. Screenshots/raw original process memory needed before claiming runtime feasibility. No claim of completed UI/gameplay compatibility.

## Runtime-discovered boundary: row-offset lookup (2026-09-10 04:24 KST)

Two controlled failures (full startup QHD and deferred display change at PS7) share root cause: `FUN_004644a0.c:312-320` writes `height+1` dwords at renderer+0x4f0. Only 1024 slots precede renderer metadata at+0x14f0; DirectDraw interface at+0x1518 is overwritten at row1034. Raw `0x46498e: 8d8ef0040000 lea ecx,[esi+0x4f0]`, then `0x464998 mov [ecx],edx`, increment stride4 and row*pitch through height. QHD height1440 overruns. Result faults before PS9 at464d7e or after PS7 at465777 are therefore not proof of an unsupported 32-bit resolution. Safe boundary repair relocates this initializer table into private PE section (height+1 dwords). Bounded renderer function scan found no other +0x4f0 accesses; this remains static evidence, not a universal absence proof.

## Full-redraw cache-clear repair

QHD input run reached PS3 tick1238; mouse(1280,730) selected original HQ slot1199, Right changed camera(7,6)->(81,0). Screenshot showed stale terrain after camera movement because the experimental bypass skipped original cache-clearing paths. Safe repair: clear ONLY private terrain framebuffer on every redraw, preserve all registers/flags, then resume original loop at0x433019. Place bounded27-byte x86 trampoline at verified-zero original `.text` padding VA0x4e4b00; expand `.text` VirtualSize only inside existing SizeOfRawData/nextsection boundary. No executable permission added to framebuffer. Original branch0x43296c goes through this trampoline. This is required correctness work, not optimization.

## Final runtime result and scope

Final candidate SHA256 `c4b912d96e623de91b7cc25de35c57395d8de1e01801e948f45b5b456b80f993`, 74 guarded code edits plus new data section and bounded header updates. It retains x86 PE32. Source original SHA is unchanged.

Evidence root `/home/dev_00/sharedfolder/260320_Syw2plus/temp/20260910_qhd_probe/`:

| Run | Result | Evidence |
|---|---|---|
| `filename_control` | Unpatched original renamed: PS3 and tick1084; 800×600/832×512 | runtime.log, snapshots, PNGs |
| `qhd_fullredraw_r1` | Startup crash at464d7e | runtime.log; title screenshot |
| `qhd_deferred_r2` | Deferred mode writes afterPS7; failure at465777/PS2 | runtime.log, initial.json, screenshot |
| `qhd_rowrepair` | Row table repaired; PS3 true2560×1440, tick1092 | snapshots/PNGs |
| `qhd_input_r1` | Actual HQ selection/camera input pass; stale strip reproduced aftercamera | hq_click_wide/camera_right snapshots+PNGs |
| `qhd_clear_input` | Stale strip removed, actual input reverified, PS3 tick10→1238 | verdict.json; all snapshots/PNGs |

Final raw width/height/pitch =2560/1440/2560, bpp8; viewport0,0,2559,1439. Actual X11 click(1280,730) changed selected count0→1 and first roster slot1199 (HQ panel shown). Right key moved camera(7,6)→(81,0). Actual mouse(2400,700) is correctly recorded. Before-camera-move raw cache nonzero bboxx925..1975,y512..991 spans1051pixels (greater than original832). Reads are asynchronous, not frame-fenced full-frame measurements; presented screenshots corroborate wider terrain at native sprite scale. No fog reveal or renderer injection was used by instrumentation.

Raw `.text` dword search for0x4f0 returns immediate-byte addresses448b28,464990,480680,4c55ea; bounded graphics disassembly finds the row initializer46498e only. No raw direct reference to absolute legacy row basee5c408 was found. This supports the local repair; it is not a proof that every possible indirect consumer is absent. Actual singleton renderer values and stable COM pointers are recorded in snapshots.

Remaining explicit limits: HUD anchored inconsistently, all rendering/effects cases untested, no long/large-army performance or native Windows/LAN validation in this lane. This is **positive original32bit QHD feasibility evidence**, not a finished release claim. No Plan C implementation used as proof.

Verification: four pytest safety tests, ruff, py_compile, original source hash, no residual private Xvfb/game process. Existing broader workspace changes were not touched.

### Runtime probe observation addresses (same SHA-pinned build)

- `0x004ED818` uint32 PROGRAM_STATE (3=in-game).
- `0x008924B8` uint32 game logic tick.
- `0x00E5BF18` singleton renderer; fields +0/+4/+8/+0xc/+0x10/+0x14 are mode,width,height,bpp,stride,currentheight; COM/pixel fields sampled at+0x1508..+0x1527.
- `0x00B3AC80` four int32 viewport bounds (left,top,right,bottom).
- `0x00B42D7C`, `0x00B42D80` int32 camera tile coordinates (map renderer object offsets+0x4fd4/+0x4fd8).
- `0x004ED814`, `0x004ED816` int16 current mouse x,y.
- `0x00899024` int32 selection count; `0x00899028` first selected roster entry (int16 slot followed by entry metadata). `FUN_0049acc0` consumes selection globals; runtime selected slot1199 independently corroborated by original HQ portrait/stats panel.
