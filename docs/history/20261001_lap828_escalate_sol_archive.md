# lap828 ESCALATE_SOL archive

Source: `loop/ESCALATE_SOL` consumed by lap829 middle review
Original line count: 24
Original SHA256: `61d1ca799eac53c654bce67581651a288809686a98c5e1003f40d241f093cb80`

lap: 828
date: 2026-10-01
role: work
status: BLOCKED/strategy
target: G1 W70 P1 fixed-terrain writer to asset-key attribution

Evidence:
- Original SHA256: b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac
- save006 SHA256: 616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064
- Final raw: ../temp/Syw2plus_patch/g1_w70_lap828_p1_fixed_terrain_r5/census/terrain-trace/writer-events.jsonl
- Raw SHA256: b7e9fc9c5d1e5c71ac64ac1e5747bef631c1f6536fc962d2e65287a88aa45178
- Census SHA256: 53c2d3bf5fff852ec549746e1fa92e9f92509038a15555c18a062ae88541d957
- Present trace SHA256: b32f7bc5e33a680dde370bf090e69163d46641af54a419230aa9bf0f5ac5e0cc

Result:
- Fixed buffer `0x00BA3D30..0x00C0BD30`: 3 watchpoints armed, 3/3 write hits.
- Entries `0x4324E0`, `0x433019`, `0x4332F0` observed; natural RIGHT moved camera `[158,101]` to `[160,99]`.
- Writer EIP `0x468C93/0x468C9C`, original `rep movsd/movsb`; source/destination copy is proven.
- No stable asset/tile/resource key is present in captured entry stack or writer registers. GDB summary did not persist before bounded termination; raw JSONL is preserved.

Handoff for strategy/Sol:
1. Decide whether to trace callers `0x435593/0x435910` and source-pointer/resource-table ownership to recover an asset key.
2. If that route is cache-wide/source-row only or cannot expose a key within one bounded work lap, close P1 as `NOT_FEASIBLE/BLOCKED` and choose the next G1 route.
3. Do not implement W70, Scale2x, GDI, or alter original/candidate binaries from this evidence.
