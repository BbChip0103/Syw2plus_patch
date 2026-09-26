# G1 HUD resource row — final-output contract probe (2026-09-16)

## 범위와 판정 규칙

이 메모는 pinned 원본 `syw2plus_original.exe`의 HUD 자원 행(리소스 아이콘과
숫자)을 **정적 증거만으로** 고정한다. 대상 원본 SHA-256은
`b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 이다.

검사한 가설은 둘뿐이다.

1. **local SPR target contract:** 기존 원본 자원 행이 resource SPR의 ID/frame/좌표와
   8-bit renderer buffer 쓰기 계약을 유지한다.
2. **final surface / painter order:** 그 쓰기가 실제 1600x1200 최종 surface에
   연결되고 같은 frame의 present 전에 뒤의 HUD/menu/cursor와 합성되는지 확인한다.

(1)은 정적으로 확인할 수 있지만 (2)는 이 문서의 증거만으로 확인되지 않는다.
실제 final 1600 surface identity, present event, draw-to-present frame association이
확보되지 않으면 판정은 `BLOCKED_FINAL_SURFACE_OR_COMPOSITION_ORDER`이다. 800x600
버퍼의 2배 DxWrapper 프리뷰나 native 1600 surface의 존재를 G1 완료로 승격하지 않는다.

## 1. 정확한 원본 call/argument contract

### 1.1 `FUN_0043F250`의 첫 resource draw

원본 VA `0x0043F250`의 첫 16 bytes는 다음과 같다.

```
81 ec 8c 00 00 00 53 55 56 57 8b e9 6a 22 89 6c
```

호출 인자는 stack에 다음 순서로 push된다.

```
0x0043F270: 6a 00       ; frame = 0
0x0043F272: 6a 24       ; sprite/resource id = 0x24 (36)
0x0043F274: 6a 03       ; y = 3
0x0043F276: 6a 0a       ; x = 10
0x0043F27c: e8 ff aa fd ff  ; call 0x00419d80
```

따라서 cdecl helper 관점의 정확한 호출은
`FUN_00419D80(10, 3, 0x24, 0)`이며, x=10, y=3, resource sprite ID=36,
frame=0이다. 이 값은 decompiler 이름 추정이 아니라 위 push bytes와 call target의
결합으로 판정했다. 함수의 직접 caller 중 하나는 `0x0041F5DE` 부근이며
`lea ecx,[eax+0x956770]` 뒤 `call 0x0043F250`을 실행한다.

뒤의 같은 함수에서 첫 행 다음 draw는 frame 1, 그 다음은 frame 2다. 숫자는
`0x0041A370` 경로에서 sprite ID `0x22`를 사용하고, resource icon width와 10을
더해 다음 x를 계산한다. 따라서 frame 0/1/2를 별도 draw call로 유지해야 하며,
단일 확대된 bitmap으로 합치면 이 원본 계약을 보존한 것으로 보지 않는다.

### 1.2 `FUN_00419D80`와 raster callee

`0x00419D80`의 첫 16 bytes:

```
8b 4c 24 0c 8d 04 49 8d 14 49 c1 e0 07 c1 e2 07
```

이 함수는 argument 3(sprite ID)를 이용해 다음 전역 테이블을 조회한다.

```
width   = DWORD [0x0051EE94 + id * 0xBF8]
height  = DWORD [0x0051EE98 + id * 0xBF8]
frameptr= DWORD [0x0051F350 + (frame + id * 0x2FE) * 4]
          + DWORD [0x0051FA84 + id * 0x2FE]
```

그 뒤 `ecx=0x00E5BF18`을 설정하고
`FUN_004664D0(x, y, width, height, frameptr)`를 호출한다. `0x004664D0`의 첫
16 bytes는

```
55 56 8b 74 24 10 8b e9 8b 54 24 0c 57 0f af 75
```

이며 이 callee는 `__thiscall` renderer method이다. `ret 0x14`로 다섯 stack
argument를 정리하므로 caller/worker가 게임 함수를 직접 호출하는 계약이 아니다.
callee는 `renderer+0x10` stride와 `renderer+0x1514` pixel buffer를 사용해
`dst = pixel_buffer + y*stride + x`를 계산한다. 각 row에서 source byte가
`0xFE`이면 다음 byte만큼 destination을 건너뛰고, 그 외 byte만 destination에
그대로 쓴다. 즉 이 경로는 palette RGB를 계산하지 않고 **8-bit palette index를
직접 복사**한다.

`FUN_004664D0` 자체에는 경계 clamp/clip 분기가 없다. `FUN_00465190`의 viewport
범위 predicate와 `FUN_00465130`/초기화 경로의 clip state는 별도 helper이며,
이 resource row callsite가 그 predicate를 통과했음을 보이는 정적 간선은 없다.
따라서 in-map 좌표라는 사실과 최종 clipping 적용은 구분한다.

## 2. sprite identity, frame, payload

### 2.1 ID → 파일 identity

원본 외부 registry `ImgFile.dat`의 해당 rows는 다음과 같다.

```
FILE_MONEYNUMBER 34 fnt\\moneynumber.spr 1
FILE_RESOURCE    36 fnt\\resource.spr    1
```

따라서 ID `0x24`는 `fnt/resource.spr`이며 ID `0x22`는
`fnt/moneynumber.spr`이다. 이 매핑은 43F250 내부에 filename string이 있다는
뜻이 아니라, `ImgFile.dat` registry와 loader table이 제공하는 외부 data-file
identity다.

참조 data copy의 resource SPR는 size 4533, SHA-256
`04a2c1608a64a91922193c82a67895d00391e59cb9faa31b5916238f9416ff40`이다.
header는 `(version=9, width=20, height=24, frame_count=10)`이고 sheet record
`+0xBC8`는 `(compressed_total=1473, sheet_width=200, sheet_height=24)`이다.
SPR pixel data 시작은 `+0xBF4`다. frame 0 block은 409 bytes이고, 위 RLE 규칙으로
정확히 20x24=480 pixels를 소비한다(남은 bytes 0).

### 2.2 frame 0 실제 mask

frame 0를 `0xFE,count` transparent-run으로 decode한 결과:

- opaque 315, transparent 165
- opaque bbox `(x=1,y=1)..(x=18,y=23)`
- row mask (`.`=transparent, `#`=written index):

```
00 ....................
01 ........###.........
02 .......#########....
03 ......##########....
04 .....############...
05 ....##############..
06 ....###############.
07 ....##############..
08 ....###############.
09 .....##############.
10 ......#############.
11 ....###############.
12 ...###############..
13 ..###############...
14 ..################..
15 .##################.
16 .##################.
17 .##################.
18 .##################.
19 .##################.
20 ..################..
21 ...############.....
22 ....##########......
23 .....#######........
```

이는 frame 0의 실제 opaque shape를 보이는 증거다. frame 0을 임의의 단색
rectangle 또는 800x600 결과를 먼저 확대해 만든 mask로 대체한 것은 이 contract와
다르다. 다만 이 파일은 원본 data 설치본의 reference copy이며, 1600용 고해상도
교체 자산의 존재를 증명하지 않는다.

### 2.3 palette와 transparency

`FUN_00493080 @ 0x00493080`가 `pal/imjin2.pal`을 주 palette로 읽고, 별도
night/result/menu palette를 로드한다. `FUN_00492740`은 6-bit VGA palette 값을
8-bit 값으로 확장(`component << 2`)해 renderer palette에 설치한다. 반면
43F250→419D80→4664D0 경로의 직접 writer는 palette table을 조회하지 않고
SPR index를 복사한다. transparency는 color-key가 아니라 `0xFE,count`가 만드는
write omission이다. 따라서 최종 surface가 8-bit indexed인지, wrapper가 어느
시점에 palette를 변환하는지는 별도 runtime evidence가 필요하다.

## 3. 정적 painter order와 same-frame 한계

`FUN_004245D0`의 render phase에서 호출되는 `FUN_0041C020` 내부의 정적 순서는
다음과 같이 확인된다(각 call의 성공/조건 분기는 별도다).

```
... initial lock / cursor-selection conditional work ...
FUN_004B35D0
FUN_004161D0
lock
FUN_0041F570
  └─ (guard 통과 시) FUN_0043F250
unlock
FUN_00434070 / FUN_00438870 / FUN_0041A550 (조건부)
FUN_0041C490
FUN_0041C5C0
... map/camera conditional work ...
FUN_0049ACC0
FUN_004C70F0
FUN_004B3780
FUN_004A9BA0
FUN_004AA0C0
... optional editor/debug work ...
```

따라서 같은 `FUN_0041C020` invocation 안에서는 resource row가 뒤의 selected
HUD/menu/cursor 관련 call보다 앞선다는 **call-granularity** 사실은 있다.
하지만 이 목록은 present event ID, swap/flip serial, back-buffer generation을
가지지 않는다. `FUN_0041C020` invocation과 `IDirectDrawSurface7::Flip` 또는
wrapper present를 같은 frame으로 결합했다는 증거는 없다. 후속 HUD/menu/cursor가
실제로 같은 final image에 그려졌는지도 현재는 UNKNOWN이다.

## 4. final 1600 surface / present 연결 조사

### 4.1 renderer object와 DirectDraw boundary

`ecx=0x00E5BF18`은 4664D0 renderer singleton이다. 기존 memory map에서 관측된
fields는 다음과 같다.

```
+0x04 width, +0x08 height, +0x0C bpp, +0x10 stride, +0x14 internal height
+0x1508 / +0x150C DirectDraw surfaces
+0x1514 locked pixel buffer
+0x1518 DirectDraw interface
+0x151C back/new surface
```

`FUN_00464EC0`의 lock path가 `+0x1514`, `+0x10`, `+0x14`를 갱신한다는 것은
resource writer의 destination boundary를 설명하지만, 그것이 1600x1200 최종
present surface라는 뜻은 아니다.

DirectDraw import의 pinned boundary는 다음과 같다.

- code thunk `0x004D7938`: bytes `ff 25 18 50 4e 00`, 즉 `jmp [0x004E5018]`
- runtime IAT slot: `0x004E5018` (`DirectDrawCreateEx`)
- IDirectDraw7: `CreateSurface` index 6, `SetDisplayMode` index 21
- IDirectDrawSurface7: `Blt` index 5, `BltFast` index 7, `Flip` index 11,
  `GetSurfaceDesc` index 22

이전 lap108 trace의 Surface indices 6/8/12/23 및 64-word vtable 복사는 typed
vtable contract와 맞지 않아 runtime final-surface 증거로 사용할 수 없다.

### 4.2 현재 hook/Wrapper evidence의 한계

`tools/inmm_stub/direct_draw_trace.c`는 `SYW2_G1_PRESENT_TRACE=1`일 때 typed
DirectDraw7/Surface7 vtable을 clone하여 `CreateSurface`,
`SetDisplayMode`, `GetSurfaceDesc`, `Blt`, `BltFast`, `Flip`, `Release`를
기록하도록 되어 있고 trace path는
`C:\\inmm_g1_present_trace.jsonl`이다. `control_state_bridge`/CSB는
program state와 game tick을 제공할 뿐 painter draw-site와 present를 연결하지
않는다.

`patches/resolution/dxwrapper_config.py`의 pinned profile은
`Dd7to9=1`, `DdrawUseNativeResolution=1`, integer scaling/aspect clamp 및
800x600 source composition을 1600x1200 display에 적용하는 **프리뷰 설정**이다.
이 설정과 private `ddraw.dll`의 로드는 final detail sprite가 실제 1600 target에
직접 쓰였다는 증거가 아니다. 기존 `g1_directdraw_presentation.md`의 trace에는
install/starting 및 runtime-contract failure만 있고 resolved IAT target, surface
identity, present event가 없다.

`FUN_00416CF0`의 GDI `StretchBlt` 경로도 존재하지만, 이는 title/background 또는
capture 계열 경로일 수 있으며 43F250 resource row와 PS3 final present를 잇는
caller/serial 증거가 없다. 따라서 이 경로를 최종 게임 surface로 혼동하지 않는다.

## 5. 결론과 필요한 다음 증거

| 항목 | 판정 | 근거/잔여 사각 |
|---|---|---|
| 원본 call bytes와 cdecl args | **CONFIRMED** | 43F250/419D80 objdump, x=10 y=3 id=0x24 frame=0 |
| ID 0x24 → resource SPR | **CONFIRMED** | ImgFile.dat row 36 + registry/loader chain |
| SPR frame dimensions/mask/RLE | **CONFIRMED (reference copy)** | 20x24, frame0 409-byte decode, 0xFE skip |
| palette identity/index semantics | **PARTIAL** | imjin2 load와 indexed copy는 확인; final palette conversion 시점 UNKNOWN |
| direct row clipping | **UNKNOWN** | 4664D0에 clip 없음; caller predicate/target bounds 간선 미확정 |
| resource 후속 HUD/menu/cursor call order | **STATIC CONFIRMED** | 41C020 call order; 조건부 call |
| same-frame composition | **UNKNOWN** | draw invocation과 Flip/present serial 결합 없음 |
| 실제 final 1600 surface identity | **UNKNOWN** | `+0x1514`는 locked buffer일 뿐 해상도 관측 없음 |
| final present path | **UNKNOWN** | typed hook source는 있으나 valid runtime event artifact 없음 |

정확한 다음 수집 경계는 private isolated run에서만 허용된다: (a) typed
`CreateSurface/GetSurfaceDesc/Lock/Flip` event에 surface identity, width/height,
pitch를 남기고, (b) resource draw boundary의 frame marker와 same-frame present
serial을 결합하고, (c) 뒤의 HUD/menu/cursor call의 결과가 동일 final surface에
포함되는지 확인한다. 이 증거가 없으면 최종 상태는
**`BLOCKED_FINAL_SURFACE_OR_COMPOSITION_ORDER`**이며, 이 문서는 구현/게임 실행/
제품 G1 완료 선언이 아니다.

## 증거 출처

- pinned binary: `../Syw2plus_re/Syw2plus/syw2plus_original.exe`
- resource registry: `../Syw2plus_re/Syw2plus/ImgFile.dat`
- reference asset: `../Syw2plus_re/Syw2plus/fnt/resource.spr`
- static HUD/render references: `../Syw2plus_re/analysis/disasm/ingame_render_pipeline.md`,
  `analysis/memory_maps/original_qhd_probe_0910.md`, `analysis/memory_maps/g1_directdraw_presentation.md`
- trace source: `tools/inmm_stub/direct_draw_trace.c`
- profile source: `patches/resolution/dxwrapper_config.py`

검증 명령 예시는 `sha256sum`, `objdump -D -Mintel --start-address=...`, 그리고
`resource.spr`의 `+0xBF4` frame-0 RLE decode이다. 본 조사에서 원본/실행 파일,
DLL, runtime, 게임, 보호 sibling을 변경하지 않았다.
