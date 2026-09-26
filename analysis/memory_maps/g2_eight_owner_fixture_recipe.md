# G2 eight-owner / 5000 fixture recipe (read-only feasibility)

**Date:** 2026-09-17  
**Scope:** existing original-game runtime bridge and telemetry only. No game was
started, no fixture was generated, and no source/binary was changed by this note.
This is a product-proximal experiment recipe, not G2 approval or LAN evidence.

## What is actually established

- The fixed-supply experiment is hash-gated to original EXE SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; the
  two-byte-site copy raises the per-player cap to 5000 while retaining the
  original per-owner count cap 250 and shared 1200-unit table
  (`analysis/memory_maps/population_5000_runtime_0910.md`, lines 20--30, 105--110).
- The only real army fixture is owner 0: 142 type-5 units at cost 35 plus the
  original HQ(type 49, cost 10) and worker(type 7, cost 10) gives 144 entities,
  used=4990; one later original production completion gives 145 entities,
  used=5000 (`analysis/memory_maps/population_5000_runtime_0910.md`, lines 50--66;
  `patches/population/test_fixed_supply_5000.py:84-103`). The entire 142-unit
  army was engine-seeded; only the final worker was normal timed production.
- `runtime_driver.state(..., detailed=True)` already reads all eight player
  structures and the complete 1200-entry table. Player base/stride is
  `0x956770 + owner*0x3ABC`; `nation` is `+0`, `ai` `+2`, `count` `+0x200A`,
  `used` `+0x200C`, count cap `+0x2010`, supply cap `+0x2012`; unit existence is
  `0x8990C8[1200]`, units are `0x66B790 + slot*0x758`
  (`patches/population/runtime_driver.py:104-164`).
- The evidence checker requires one same-PS3 sample with eight configured,
  positive-count owners, cap=5000 and each used>=5000. It explicitly adds
  “behavioral evidence is missing” and treats RSS as non-OOM proof
  (`tools/check_runtime_evidence.py:227-304`). Thus eight configured slots or
  cap fields alone cannot pass G2.

## Opt-in original eight-owner creation boundary

The new control goal `_custom_game_chain_inject_g2_eight_seed42` is an exact,
opt-in PS=7 diagnostic. It rejects a scenario-index override, requires the
original `B93988` gate to be zero, and preflights the complete 48-byte lobby
blob, every setup word, the chain word, and program-state word before writing
anything. It sets the requested ordinary-mode selector (`game_mode=0`; the UI
label is not yet independently proven), `game_type=2`, map selector/size and
terrain/tile fields to zero, and seed 42. Legacy chain goals retain their old
two-entry behavior.

The source blob at `0x00632CC0` is eight contiguous six-byte records consumed by
the original `FUN_0041B9B0`; no PlayerStruct arena write is performed. The
diagnostic fills every record as `(nation=1, player_num=owner,
is_cpu=(owner != 0), self_mask=1<<owner, opponent_mask=0,
team_num=owner)`. The zero opponent field is intentional: the original
initializer derives the enemy mask from the team numbers. This is setup only,
not combat or economy proof. The first observation must be a natural original
readback with all eight owners present and an HQ type 49 plus worker type 7 for
each owner; otherwise stop rather than normalizing the ledger or PlayerStruct.

The implementation is limited to `tools/inmm_stub/control_executor.c`; the
static contract is in `tests/test_g2_eight_owner_setup.py`. It has not been
run in Wine or linked into the shared DLL in this lane.

## Existing bridge entrypoints and a feasible bounded recipe

The private `patches/population/runtime_bridge.c` is the only existing fixture
writer. Requests are eight decimal fields `[id, op, owner, slot, type, x, y,
count]`, and it rejects `owner >= 8`, so the owner domain is exactly 0..7
(`runtime_bridge.c:126-146`). Its operations are:

- **op=4:** sets one owner's rice/wood and `used` directly (`+0x14`, `+0x18`,
  `+0x200C`), with an upper bound of 5000 (`runtime_bridge.c:154-163`). This is
  diagnostic preparation, not natural economy proof.
- **op=5:** only accepts type 5 with observed cost 35, checks map bounds and
  `wanted <= 142`, calls the original placement, allocation gate and spawn,
  then verifies owner/type/live/count/used after every entity
  (`runtime_bridge.c:164-215`). It is explicitly “engine-seeded roster, NOT
  production or resource spending” (`:164-166`).
- **op=1:** calls the original train function at `0x4AF5E0` for a live owned
  unit (`runtime_bridge.c:137-147`). **op=2/3** call original save/load at
  `0x440C20/0x440FF0` (`:148-153`).

A bounded experiment, once an original custom battle genuinely exposes eight
active owners, is therefore:

1. Use the existing fixed-supply copied EXE and original UI/custom-game path to
   configure owners 0..7. Do not synthesize `nation`, `ai`, or roster fields in
   the bridge. Before any seed request, capture detailed state and require all
   eight owners to have nonzero nation, intended AI/human role, live starting
   HQ/worker, and distinct identities.
2. For each owner, record a separate op=4 preparation only if the run is
   explicitly labelled *assisted ledger setup*. Set resources high and used=20
   only after confirming the original starting HQ+worker cost from the type table;
   never count this write as normal production.
3. For each owner, issue one op=5 request with `type=5`, `count=142`, and a
   disjoint map anchor. The bridge scans forward from the anchor, so the
   anchor must be recorded and `fixture_attempts`, placement result, owner,
   live flag, distinct internal IDs, and post-seed used/cost sum must be checked.
   A 142-seed owner reaches 144 entities and used=4990 if the two starting
   entities are exactly the documented 20 supply.
4. For each owner, choose its actual live HQ slot from detailed readback and
   issue op=1 for type 7 once. Wait for the original production transition and
   capture before/pending/completed states. The expected assisted fixture target
   is 145 entities and used=5000 per owner; it is not proof that 142 units were
   naturally trained.
5. At every stage read the whole 1200-slot table and all eight player records.
   The arithmetic upper bound is 8*144=1152 seeded entities and 8*145=1160
   after one worker each, leaving 48/40 raw slots, or at most 47/39 usable
   slots with the reserved sentinel, before buildings, dead records, enemy
   entities, and allocator reservations. Therefore the nominal arithmetic fits
   both per-owner 250 and global 1200, but the real run must prove shared
   occupancy and allocator failures are absent.
6. Save and load once through the original save/load calls only after all eight
   owners pass the same-sample structural gate. Compare every owner’s
   `(slot, internal_id, type, owner, hp, x, y, command)` plus ledger and
   pending-production state before/after. Existing owner-0 save011/012 evidence
   cannot be promoted to eight-owner persistence.

A useful request sequence (IDs strictly increasing) is conceptually:
`op4(owner, used=20) -> op5(owner, type=5, x=anchor_x, y=anchor_y,
count=142) -> op1(owner, hq_slot, type=7)` for owner 0 through 7, with detailed
readback between every request. The existing bridge has no multi-owner batch
operation; interleaving is unsafe because `fixture_failed` permanently locks the
fixture after an accounting error (`runtime_bridge.c:175-179, 207-215`).

## Concrete blockers / non-claims

1. **No existing owner-generation path.** The bridge can address owner 0..7 but
   does not create a nation, AI participant, HQ, or worker for an inactive owner.
   Prior real snapshots show owner 0 active and owner 1 minimally active while
   owners 2..7 have nation=0/count=0 (`patches/population/verification_0910/
   run3_real_army_5000.json` and `run4_final_24k_snapshot.json`). The normal
   custom-game UI path for eight active owners must be reached and read back;
   otherwise the recipe is blocked, not replaced by direct memory writes.
2. **“High-cost army” is not implemented by the fixture.** The pinned type table
   records type 5 cost 35, type 25/26 cost 50, and type 103 cost 65
   (`patches/population/verification_0910/type_costs.json`), but op=5 deliberately
   rejects every type except type 5. No existing harness proves normal production
   of 142 high-cost units for any owner. The proposed recipe is therefore an
   assisted type-5 accounting stress case plus one original production step.
3. **Shared-pool margin is only arithmetic.** 1160 < 1200 and 145 < 250 are
   necessary conditions, not a proof: map occupancy, buildings, reservations,
   allocator sentinel behavior, and death/production churn still need detailed
   readback. `analysis/memory_maps/population_5000_runtime_0910.md:105-110`
   explicitly keeps the original shared pool and count limits.
4. **Persistence and normal economy remain open.** Existing save/load evidence
   demonstrates owner 0 only and the bridge op=4 writes the ledger directly.
   Save/load serializer coverage for all eight active owners, normal resources,
   production, combat losses, and re-production is unverified.
5. **LAN/multiplayer is not established.** Eight local player records and a
   successful local custom battle do not prove peer synchronization, rejection
   of incompatible peers, or network ownership semantics. Keep this recipe
   local/free-battle only and report LAN as UNKNOWN.

## Verdict

**FEASIBLE as a bounded assisted local fixture probe; not yet a product recipe.**
The existing 1200-slot/per-owner arithmetic and op=5 accounting checks are enough
to define a safe next measurement, but there is no current harness path that
both (a) genuinely activates owners 0..7 through original setup and (b) naturally
produces eight high-cost 5000 armies. Until those two facts are observed in one
private run, G2 remains INCOMPLETE/UNKNOWN and no 8-owner, high-cost, LAN, or
release claim is justified.
