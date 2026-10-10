# G1 stale253 / primitive A — lap1241 read-only attribution

- Official input: `../patch_history/[ESL]Syw2plus 2613.exe`, SHA256
  `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`.
- Read-only command: `i686-w64-mingw32-objdump -d -Mintel --start-address=0x466d50 --stop-address=0x466ea0 '../patch_history/[ESL]Syw2plus 2613.exe'`.
- Raw disassembly: shared `temp/Syw2plus_patch/20261010_lap1241_middle_review/primitive_a_2613.asm`.
- Entry `0x466D50`: exact seven old bytes `83 ec 14 8b 54 24 1c` match
  `G1_TARGET_A` / `expected_a` in `tools/inmm_stub/g1_mirror2x.c`.
- Instruction `0x466E64`: bytes `88 1c 02`, `mov BYTE PTR [edx+eax],bl`.
  `0x466E67` is the next instruction; hardware write traps report that post-write EIP.
  This write is inside the already-hooked primitive; it is not a new missing entry hook.
- `mirror_primitive_a` executes the original, then `mirror_reinvoke` under the
  primitive guard. Reinvoke uses two scratch buffers, restores the renderer buffer,
  verifies clipped identity capture, restores the four viewport fields, and composes
  the screen or cache target. The older lap852 map is HQ2002 provenance; this note
  separately checks the 2613 entry/write bytes and does not transfer unrelated offsets.

## Runtime boundary

Lap1240 uninstrumented run: PS3 ordinal62 stale253, bbox `(435,180)–(466,199)`.
Its three later watch samples `(438,182),(450,185),(462,197)` are all actually stale
in that mask. Separate watched run: all selected ordinals55–90 stale0; p66 sample2
`scr=snap=228,cov=1`, cache/layer expected both93. Its normal screen write at
`0x466E67` does not establish the earlier stale writer or a faulty replay.

Hardware `t:x` records have a present label, EIP, values and guard, but no timestamp.
The claimed +9ms is `p66 tick312315094 - click312315085`; it is not the exact hit
time. Stack `st[]` is a filtered scan of EXE-looking words, not an unwound call stack.
`guard=1` is also the normal outer wrapper state, so it does not prove guard bypass.
Moved `--drift-samples` changes point values only: `t:r` rectangles and cache event
overlap geometry remain the older fixed regions. Do not attribute this bbox from
their counts or the stale sample's `ev[]` alone.

Root cause remains UNKNOWN. Work must first obtain stale and diagnostic values
from the same candidate present; no new hook, replay alteration or gate weakening
is justified by this static/runtime evidence.
