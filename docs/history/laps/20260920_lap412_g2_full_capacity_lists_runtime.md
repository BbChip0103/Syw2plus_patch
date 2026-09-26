# 2026-09-20 | lap 412 | G2 full capacity-dependent list relocation

## Target

Close the next concrete gate toward stable eight-player supply-5000 play:
prove more than 1200 simultaneously live units in the original engine without
overwriting the stock packed active/category lists.  This is not save/load,
LAN, 24k/144k, or product completion.

## Implementation

- Added `full_tail_relocation_storage_layout_v1.py`, which keeps the N=1200
  byte-identity anchor and relocates all six capacity-dependent regions below
  the relocated `.rsrc`: UnitStruct pool, existence, age, category A,
  category B, and active-slot list.  The three trailing live counters remain
  WORDs after their expanded arrays.
- Added `g2_full_unit_capacity_v1.py`, which applies the existing pool
  fixups plus decoded references for category A/B and active list.
- Added compositions for supply 5000 and for the N=4001/supply5000/owner1200
  next-step candidate.
- Added diagnostic-only op6, identical in boundary shape to the established
  op5 fixture but restricted to the original type-7 worker (observed cost 10),
  so a bounded test can exceed 1200 live entities without falsifying the
  supply ledger.

Decoded original reference inventory after the first implementation:

| region | decoded sites |
| --- | ---: |
| unit pool | 1014 |
| existence | 34 |
| age | 4 |
| category A | 18 |
| category B | 3 |
| active list | 260 initially, 262 after lifecycle alias repair |

## Runtime experiment 1 — creation PASS, lifecycle FAIL

Candidate SHA: `d10c416c0b19f2a0a3c936e920db62bdbb66c0bee317cb4024ef1bde88650745`.

- Fresh private Wine prefix and private complete game copy.
- Original eight-player seed-42 chain reached PS3.
- Type-7 diagnostic seeding reached 1225 and then 1249 simultaneously live
  entities in a 1250-slot candidate.
- Slots 1200..1249 were live; active count, active entries, and existence
  initially agreed exactly.  A further allocation at 1249 live units returned
  zero without changing owner accounting.
- At roughly 445 seconds of soak, the game remained alive but active-list
  integrity failed: duplicate slots 10/13, missing 1/2/4/1249, and invalid
  entries 0/64981.  Therefore the candidate is rejected for lifecycle use.

Root cause: `FUN_00442FE0` copies the last active element through two encoded
`active_base - 2` aliases (`0x00443075`, `0x0044308C`, displacement
`0x00974FA6`).  A half-open scan beginning at `0x00974FA8` could not discover
them.  The neighboring DWORD at `0x00974FA4` is a distinct scalar and remains
untouched.  The two aliases are now explicit, old-byte-bounded fixups.

Rejected-run evidence:

- `.../20260920_full_capacity_1201/runtime/live1201_list_validation.json`
  SHA `ddd0966efd27e843731235e9fe584d8dc6ccbe2a7cdc9e0dc92551aa769b1f17`
- `.../runtime/list_corruption_detail.json`
  SHA `c0cff72bbea924243a7c99258f31e15aebaffb0e4dbd0847c0a514c761f6409a`
- screenshot (external only):
  `captures/20260920_142842_supply5000_full1201-corruption-shot.png`
  SHA `1d4ac2a62f4f21a31e1bbd8eb92ea3135c9b5bf158783f09fdb3545fb78ce5d1`

## Runtime experiment 2 — alias repair delays but does not close the failure

Repaired candidate SHA:
`66adee3f341b1cd96a80a76ddfac205c9264ae878db07ba08e3f2dc2eb47cf65`.

The same fresh eight-player test filled exactly 1249 live entities.  The
active-list/existence invariant stayed exact through 555 wall seconds and tick
20336, but failed at 560 seconds / tick 20503.  The failure was simpler than
experiment 1 but persistent across ten rapid rereads: active count and
existence count were both 1249, while the active list contained slot 3 twice
and omitted the still-live HQ in slot 1249.  No invalid or nonexistent slot
value remained.  The owned game, Wine prefix, desktop, and Xvfb processes were
then stopped; prefix-process residue was empty.

Evidence:

- `.../runtime/active_alias_fix_soak.jsonl`
  SHA `95bdc81db5bc697d6c2b9951b3b34767091938f6b0829990cbec8d6115d1b3f3`
- `.../runtime/second_corruption_detail.json`
  SHA `5c169c85c0769a982f8dadbb9e1b34f56bed664d42bfd9382ae1ada31d47a3f4`

This proves that the two missed `active_base - 2` aliases were a real defect,
but not the only reason the long-running list diverges.  Before another binary
edit, the next discriminator is an exact stock-capacity saturation control at
the same tick range.

## Runtime experiment 3 — deterministic category-B overflow isolated

The stock-capacity control remained exact through 24,000 ticks, while both
expanded candidates failed immediately after absolute tick 20480.  The failed
expanded image had `active[0] == 3`, a duplicate slot 3, and a missing still-
live slot 1249.  This matches a DWORD full ID written one element beyond the
category-B array: the low WORD overwrites B's count and the high generation
WORD overwrites `active[0]`.

`FUN_004A3690` searches and decrements category B but the stock instruction at
`0x004A3692` loads category A's count.  In the saturated all-B fixture this
prevents correct swap-removal and permits a later B insertion at `B[capacity]`.
For expanded layouts only, that guard/last-element index now loads category
B's own relocated count.  N=1200 remains byte-identical.

N=1250 + supply5000 candidate SHA:
`c3bd799fefd31ffb8d02ed7e1d08bb734890c7e637c7eb3ffe4dc236004df5d3`.
With exactly 1249 live entities it passed 24,027 ticks / 721.5 seconds, 144
samples, including the prior deterministic failure point, with exact
existence/active/category-B counts and no duplicate or missing slot.

- `active_integrity_soak.jsonl` SHA
  `94d8b0981558af26a2cee1ee155c96dd46b93bd57c163b3dc9f0ded21539f06e`
- `active_integrity_soak_summary.json` SHA
  `c4c4c9be9369b29675c4c551167542fdb3751fd31dd6429206e0529c059d0c51`

## Runtime experiment 4 — eight owners at supply 5000

N=4001 + supply5000 + owner-count1200 candidate SHA:
`20b95a94711590e1bd41559ce76a9de6e40c155948f8d559b1090909fc342794`.
A separately built N=4001 diagnostic bridge (SHA
`326f51bb7089f06f01bc44c612f996ba31c35ab17ea487adbfbf606a1eb51175`)
seeded all eight owners to `used + reserved == 5000`.  The original engine
reached 4000 simultaneously live units (500 per owner) and passed 24,076
ticks / 723.5 seconds over 144 samples.  Combat/death reduced the final live
count to 3979, but existence, active and category-B counts remained exact with
no duplicate, missing or unexpected slot.

During the subsequent 144k continuation, owner 6 temporarily showed
`used=5000,reserved=10` before returning to 5000 total.  The same class of
short over-cap reservation/transfer state was already captured in the stock
1200-slot control history, so it is tracked as a pre-existing strict-cap issue,
not attributed to the relocated pool.  It still requires a separate product
decision/fix because the requested cap is strict.

The preserved trace narrows this further.  Owner 6 progressed from
`used=4990,reserved=0,count=500` at tick 33582, to `4990+10,count=500` at
33750, and then `5000+10,count=501` at 33917.  The reservation remained until
tick 50130 and then cleared; live `used` never exceeded 5000.  Owner 5 later
showed the same bounded pattern.  Static decompilation also shows that
`FUN_0043F0C0` already admits a new reservation only when
`used + reserved + new_cost <= cap`, while the final spawn gate
`FUN_0043EDA0` checks `used + completing_cost <= cap`.  The strongest current
inference is an intra-tick ordering window: the completing order releases its
reservation before roster accounting, allowing the next queue entry to be
reserved before the completion raises `used`; that next entry cannot become a
live over-cap unit and is eventually cancelled.  Exact call/write order is
not yet instrumented, so this is not promoted to a causal proof.

Two tempting one-site fixes are unsafe and were not made: adding `reserved`
again at the final spawn gate double-counts the order currently completing,
while clamping the reservation field would detach queue/resource state from
its accounting.  The present evidence therefore distinguishes a temporary
pending/UI total of 5010 from live-unit supply: in this 144k run the latter
remained at or below 5000.

- `seed_receipts.json` SHA
  `dd2034995e93329ea5700c0b3e84a3c27af2b400694e2913e4e06991154f03bf`
- `postseed_snapshot.json` SHA
  `f5e2968962d5fefb10d7d00b8d0c70e3d70da6030d562ea176b186216bed089d`
- `n4001_integrity_soak.jsonl` SHA
  `a797deef5e1295ae6dcbd23c2ca146960d2b9921b56778e8ca8d59519a8937ca`
- `n4001_integrity_soak_summary.json` SHA
  `62e6cb714dc8d7822f3b62e932fd72b6e791bc3ce5cd3149ae70d95524b7765c`

The same owned process then completed a further 120,152 ticks / 3606.7
seconds over 714 samples.  Combined with the first gate, the saturated scene
ran for 144,228 observed ticks.  The scene reached 4000 live units; after
combat/death it ended at 3899, with existence, active and category-B still
exact and with no duplicate, missing or unexpected slot.  The owned game,
Wine server, desktop and Xvfb were stopped afterward; prefix residue was zero.

- `n4001_integrity_144k_extension.jsonl` SHA
  `29054e47ef8033a6e0512f307d633145a26233cf93c6cfea9b6559277a7a0018`
- `n4001_integrity_144k_extension_summary.json` SHA
  `1a3e175cae0a69d4237fa48c30423355c962e30a14d0ef4ba0e141bc901f84b7`

## Runtime experiment 5 — expanded save/load round-trip PASS

The stock bulk save block excludes the five relocated arrays.  Experimental
candidate `1e90f62fdcecb49d47d85af54bef17744bb7ae9d895a43b1923fd59405a30093`
redirects the stock bulk writer/reader through bounded wrappers in verified
zero padding at the relocated `.rsrc` tail.  The wrappers retain the original
bulk operation and then stream existence, age, category A, category B, and the
active list.  The post-load slot walk is raised from 1200 to 4001.

Two actual same-candidate round trips passed in a private Wine runtime:

1. At 1332 live units, slot 98 was saved, 100 type-7 units were added to
   owner 0, and the slot was loaded.  The load returned to tick 1987 and the
   frozen post-load state had existence/category-B/active counts all equal to
   1332, with 1332 unique active slots and no missing or unexpected slot.
2. Near capacity, the eight owners held 3993 live units while each was at or
   immediately below supply 5000.  Slot 97 was saved, slot 98 was loaded to
   replace it with the smaller 1332-unit state, and slot 97 was then loaded
   again.  The frozen post-load state returned to tick 3092 with 3993 units.
   Existence, category B, active count and unique active count were all 3993,
   again with zero missing or unexpected slot.

In both cases the complete 56,020-byte relocated-array image found in the
save file at offset 1,704,974 was byte-identical to frozen post-load memory.
For the near-capacity case both sides hash to
`163da09837183d35f9a0cf343d77470e8b8803f6325f54a916f8e5a81a4ebab2`.
The 9,268,562-byte slot-97 save hashes to
`93191795db90466a9ecd2d872b07de9e8d42d2ce746df3898f62acab0ec5f0d4`.

- `persistence_roundtrip_summary.json` SHA
  `edf6a02a8af99cc89be06ec29d84a1faeeafd428c66720edb82952fb2f7cdeef`
- `frozen4000_verification.json` SHA
  `b4a3a3a27a3bc0fb07ba954bc97fd1fb48b344a06c30b168310460f49322691d`
- `frozen4000_snapshot.json` SHA
  `cf2c03563d86aa5e26b2ef0986b78f4d716e8af9b02f72abe7ad19449ef24799`
- Reproducible offline verifier:
  `python3 -m patches.population.verify_g2_persistence_artifacts <run-dir>`.
  Its actual report is PASS with SHA
  `7dfaaf87acc7417eb49a6814a0ac373d51d12f362ba8d06df81ac443f857d8d3`;
  focused verifier tests: `2 passed`, Ruff PASS.

This closes same-candidate expanded-array persistence, not the final save
product contract.  Old stock saves have no magic/version discriminator and
must not yet be loaded with this experimental candidate.  Compatibility or a
clear fail-closed rejection path remains required before release.

### Post-load simulation gate

A second fresh private process loaded the preserved 3993-unit slot-97 save
into a newly created eight-owner scene and then ran the restored simulation
for 24,085 ticks / 723.7 seconds over 144 samples.  The scene naturally
reached 4000 live units and later ended at 3978 after combat.  Every sample
kept existence, active and category-B counts equal, with a unique exact active
set and no missing or unexpected slot.  PS remained 3.  This proves the loaded
expanded state continues through allocation, death and combat for the normal
24k integration gate; it is stronger than an immediate post-load byte check.

- `postload_integrity_soak.jsonl` SHA
  `5ca1be02c4f99080a86dcb983194efb4726759ed8de91bd78be8803910e8cdc1`
- `postload_integrity_soak_summary.json` SHA
  `667fdeaea1a87279a49ee4b93412754ea260b9a34b4cb88c0ff32f56e9625b58`

The owned game, Wine server, desktop and Xvfb were then stopped.  The private
runtime executable and diagnostic DLL were restored to their pre-run hashes,
the temporary slot-97 copy was removed, and owned process residue was zero.

### Versioned header and stock-save fallback

Compatibility candidate `g2_full_capacity_persistence_compat_v1.py` reserves
the final eight bytes of the otherwise load-ignored 64-byte save description
header for marker `S2P1N4K1`.  A marked save takes the expanded sidecar path.
An unmarked stock save instead copies the five original 1200-capacity arrays
from the loaded bulk block into the relocated prefixes, zeroes the expanded
tails, and moves each category/active count WORD to the new array end.

The first implementation (`de6ffe7f...`) copied count-bearing arrays as a
single prefix.  Its actual stock-save load initially returned success but then
produced `active_count=65161`; it was immediately rejected and preserved.
The fault was exact: the old count WORD landed at old index 1200/2400 rather
than at the new array end.  No unrelated retry or speculative fix was made.

Corrected candidate SHA:
`4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`.
It passed both runtime branches:

- Unmarked stock `save000.dat` SHA
  `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`
  loaded with marker flag 0.  All five original entry prefixes and relocated
  count WORDs matched, every expanded tail was zero, and the frozen state had
  375 existence entries and an exact 375-entry active set.  It then advanced
  2,005 ticks in PS3; the final 381-entry active set remained exact.
- A fresh marked slot-96 save contained literal header `S2P1N4K1`.  Reload set
  marker flag 1, returned exactly to tick 53055, and produced an exact
  382-entry active set.  The full 56,020-byte sidecar at file offset 2,388,174
  was byte-identical to frozen memory; both hash to
  `fce3db052679a4e24372ca3c732d552fe7c558ed01d720d5ff6aa15bd1cdd296`.

- `legacy_fallback_verification.json` SHA
  `b88580620191f9c997efca34f282d39240e7d7745fb74339aac722b3056bcce7`
- `legacy_smoke.json` SHA
  `1e2eeff7809cec2175867a2040e2418412b5e51ffc6a6a4f05cf02a68aec60ad`
- `compat_new_format_verification.json` SHA
  `44589873c8206ade6a9b9219ba13f92010a213aec99c98c25509e74cd781335d`

The private runtime executable/DLL were restored and temporary slot 96 was
removed.  This establishes stock-save migration and marked new-save dispatch;
the compatibility candidate still needs the marked path repeated at the
near-4000-unit scale before becoming the product candidate.

## Verification so far

- Focused persistence and launch-gate suite: `23 passed`.
- Focused capacity regression suite after the runtime work: `44 passed`.
- Ruff: PASS.
- Fresh actual runtime evidence, not an allocator-only or synthetic-memory
  result.

## Remaining non-negotiable gaps

1. Repeat the marked compatibility path at near-4000 live units.  The base
   expanded path already passed that scale; the new header dispatch has so far
   passed stock migration and a 382-unit marked save.
2. Verify supported LAN serialization/determinism.
3. Decide/fix strict handling for the pre-existing transient over-cap reserve.
4. Replace diagnostic seeding with ordinary production/reproduction coverage;
   combat/death already occurred during experiment 4.
