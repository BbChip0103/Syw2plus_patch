# G1 W70 P1 terrain context closure — `0x403C10` is not a pixel writer

Date: 2026-10-01
Lap: 825
Role: work / hands-on read-only attribution
Confidence: high for the `0x403C10` classification; low for the still-unobserved terrain destination writer

## Protected input and raw bytes

- Protected original: `Syw2plus/syw2plus_original.exe`
- Original SHA-256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- `0x00403B20` old prologue bytes: `53 66 8B 5C 24 1C 56 8B F1 F6 C3 01 74 32 66 8B`
- `0x00403C10` old prologue bytes: `56 57 8B 7C 24 0C 8D 51 0C 85 FF 75 05 BF 0C 9A 51`
- No original or reference repository was written. No EXE was patched.

The raw disassembly of `0x00403C10` is:

```text
00403C10  push esi
00403C11  push edi
00403C12  mov  edi,[esp+0x0c]       ; source argument
00403C16  lea  edx,[ecx+0x0c]       ; destination is object + 0x0c
00403C19  test edi,edi
00403C1B  jne  00403C22
00403C1D  mov  edi,0x00519A0C       ; default source
00403C22  strlen-like repne scasb
00403C33  rep  movsd
00403C3D  rep  movsb
00403C41  ret  0x4
```

This routine has no renderer-buffer address calculation, no 800x600 stride use, and no pixel loop. Its destination is the vtable object's `this + 0x0c`; the call is reached from `0x403B20` through the object's vtable slot `+0x30`. Therefore the `0x403C10` path is a sprite/data-object copy, not the terrain pixel writer.

## Fresh runtime evidence

Command:

```text
PYTHONPATH="$PWD" python3 tools/g1_saved_scene_probe.py \
  --runtime-root local/runtime/g1_w70_lap825_p1_writer_attribution \
  --artifact-root ../temp/Syw2plus_patch/g1_w70_lap825_p1_writer_attribution \
  --census-only
```

Fixture: protected original, private Wine32 prefix and Xvfb, non-synthetic `save006.dat`, logical render surface 800x600, no candidate EXE, no G1 product patch. The game copy was removed after the run.

| Evidence | Result |
|---|---|
| Probe status | `PASS` |
| Terrain context calls | 27; all `method_0x30 = 0x00403C10` |
| Terrain-context primitive pixels | 0; no nested primitive call carried `terrain_0x403B20` |
| Context-map terrain pixels | 0 across 48 valid records |
| Offscreen DirectDraw | 72 `BltFast` records, all PS35, `832x600 <- 800x600`, caller `0x00493CCB` |
| Present attribution | 64/64 boundaries, `assigned_pixels=480000`, ratio 100 |
| Cleanup | `prefix_processes_after=[]`, `game_removed=true`, `ok=true` |

Artifact hashes:

- census raw: `c31e10f792043f84e59c72e35def5e54b7016d02ee7bce17d5c926db97cf81e0`
- census map: `e9c86a4674ba4bf2099487970160870358eeac5af13a5e3e8d877a836b852dc8`
- context map: `090781d6fbe45d8b83979dd0afe2823fab069dc1ae152c0b8acb7cf033d79922`
- DirectDraw trace: `27eb09e5ba301bd7bdcde86d920ea8896bbd92a39617634e071280f3b58ab979`
- diagnostic bridge: `d645d31b2fe14ec8fba1e65048f34c669fb820fd26ea047718a1e661c48739ce`

## Boundary

`0x403C10` is closed as a non-pixel copy path. This does **not** identify the actual terrain destination/pixel writer: cached terrain copy, the vtable object's later consumer, DirectDraw/GDI paths, and W70 candidate rendering remain outside this result. G1 remains HOLD; no HD coverage or product completion is claimed.

Next one thing: use a bounded read-only live write trace to attribute the actual terrain destination/pixel writer after the `0x403C10` object-copy path. Do not start W70 candidate/Scale2x/GDI implementation until that attribution is recorded.
