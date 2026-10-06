# G1 W70 P1 fixed terrain writer trace — lap 828

Date: 2026-10-01
Lap: 828
Role: work / hands-on read-only attribution
Verdict: `BLOCKED/strategy` for writer-to-asset-key attribution; G1 remains HOLD

## Protected inputs and scope

- Protected original: `../Syw2plus_re/Syw2plus/syw2plus_original.exe`, SHA-256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- Non-synthetic fixture: `save006.dat`, SHA-256 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
- No original/reference repository, EXE, DLL, save, or product patch was written. Runtime used private Wine32/prefix and Xvfb; the game copy and prefix processes were cleaned up.

## Work change

The read-only GDB trace pins fixed terrain buffer `0x00BA3D30..0x00C0BD30` (832x512), arms exactly three byte watchpoints at `(64,64)`, `(416,256)`, `(768,448)`, and records entries `0x004324E0`, `0x00433019`, and `0x004332F0`. The saved-scene trace lane sends a real `RIGHT` key after load and records camera movement. No game-memory write API or product patch was added.

Source hashes after the change:

- `tools/g1_terrain_writer_trace.py`: `15502de9ce3c8d11acbf99f28b420f9ff35bbcd81a238629b8d23a98884b73f7`
- `tools/g1_saved_scene_probe.py`: `67998a2db785ef0784a79ec7e87af28e214e984683cfd70e9ceaccc641516312`
- `tests/test_g1_terrain_writer_trace.py`: `33728f55e67b44c49cb63c66a23daa1e3705d8fe2a80dec5ff495b3ab2ab0d52`

## Fresh runtime evidence

Final fresh run: `../temp/Syw2plus_patch/g1_w70_lap828_p1_fixed_terrain_r5/census/`.

- Probe exit 0/PASS; source unchanged; cleanup PASS (`game_removed=true`, `prefix_processes_after=[]`).
- Natural input: `RIGHT`, camera `[158,101] -> [160,99]`.
- Fixed watchpoints: 3 armed and all 3 hit at one loaded-scene redraw. Addresses: `0x00BB0D70`, `0x00BD7ED0`, `0x00BFF030`.
- Entry observations: `0x4324E0`, `0x433019`, and `0x4332F0` each produced bounded samples; `0x403B20` and `0x403C10` were also observed.
- Writer EIP: `0x00468C93` for the first/third point and `0x00468C9C` for the middle point. Raw hashes: writer events `b7e9fc9c5d1e5c71ac64ac1e5747bef631c1f6536fc962d2e65287a88aa45178`, census `53c2d3bf5fff852ec549746e1fa92e9f92509038a15555c18a062ae88541d957`, presentation trace `b32f7bc5e33a680dde370bf090e69163d46641af54a419230aa9bf0f5ac5e0cc`.
- GDB's own summary file was not persisted before bounded termination; raw JSONL was flushed and is the evidence artifact. This is a harness limitation, not a product PASS.

## Static attribution and boundary

Protected-original disassembly shows `0x468C60..0x468CB7` reading a two-byte source header and copying source bytes with `rep movsd` at `0x468C93` and `rep movsb` at `0x468C9A`. Wrapper `0x468C30` computes a renderer destination from `renderer+0x1514` and stride; callers include `0x435593` and `0x435910`.

The live source candidates identify a source byte stream and destination copy, not a stable resource/tile key. Neither the entry stack samples nor writer registers expose an asset ID/key, and no source-pointer-to-asset table was observed. The fixed-buffer writer is proven, but writer→asset-key attribution is `UNKNOWN/BLOCKED`.

Do not implement W70, Scale2x, GDI, or production changes from this evidence. Strategy/Sol must decide whether to trace the two callers and a resource table, or close P1 as not feasible and choose the next G1 route.
