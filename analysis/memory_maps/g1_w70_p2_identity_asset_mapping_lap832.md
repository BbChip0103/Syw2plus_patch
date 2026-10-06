# G1 W70 P2 identity asset mapping — lap 832

## Contract

P2 uses `SYW2_G1_HD_SOURCE=identity`. The protected original primitive decodes
the source frame into the sentinel A/B buffers; the candidate records a bounded
key `(writer, source pointer, width, height, FNV-1a digest of 128 source bytes)`
and marks only pixels written by that original primitive. The existing nearest
2x present path consumes the same-frame value, so this is an identity-source
oracle, not a claim of Scale2x detail or a user-supplied HD pack.

## Implementation

- `tools/inmm_stub/g1_hd_asset.c/.h`: opt-in bounded key ledger (256 keys),
  readable-source guard, persistent identity coverage mask, invalid-source and
  stale-compatible counters. It has no CRT dependency and never writes the
  protected EXE or game state.
- `g1_mirror2x.c/.h`: binds each primitive re-invocation to the identity key,
  marks written logical pixels, keeps the mirror coverage between presents, and
  invalidates only pixels whose expected 800 value changed.
- `direct_draw_trace.c`: records `hd_source`, identity key/event/pixel counts,
  invalid-source count, and the existing nearest/stale metrics.
- `tools/g1_saved_scene_probe.py`: candidate-only `--hd-source identity` lane.
  `tools/g1_hd_identity_probe.py` validates the completed raw trace.

## Source and fixture

- Protected original: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- Non-synthetic `save006.dat`: `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064`.
- Private Wine32 game copies, private prefixes, Xvfb 1600x1200x24; candidate
  diagnostic DLL only; original EXE remained unchanged.

## Fresh paired evidence

Command: `PYTHONPATH="$PWD" python3 tools/g1_saved_scene_probe.py
--runtime-root local/runtime/g1_w70_lap832_p2_identity
--artifact-root ../temp/Syw2plus_patch/g1_w70_lap832_p2_identity
--hd-source identity`

Artifact: `../temp/Syw2plus_patch/g1_w70_lap832_p2_identity/pair-result.json`
SHA-256 `c329738ab1381f011f9799611cedc5ead7a7c9da58d357f2c32a952404d92046`.
Candidate trace SHA `aa07b5d89cade7c1621c1f755add0fb450d2a50b5cdfdcd63fc42a6ad7bd9f6d`.

| metric | result |
|---|---:|
| candidate mirror presents | 684 |
| nearest same-frame oracle minimum | 1.000000 |
| identity keys / events | 188 / 25,442 |
| identity pixels (persistent logical mask) | 182,650 / 480,000 (38.052%) |
| invalid source samples | 0 |
| stale pixels (cumulative present observations) | 775,141 |
| scene state parity | PASS |
| candidate source unchanged / cleanup | PASS / PASS |

Selection, empty click, and drag matched. Minimap and production were UNKNOWN
in both lanes (the existing save006 fixture does not produce those effects), so
they are not product input PASS. Screenshot pair nearest ratio was 0.939704;
it is not the same-frame oracle and is retained as a cross-process visual
limitation. P2 remains `PASS(partial)` pending middle review; P3 Scale2x,
GDI, full HD coverage, and user approval remain open.

## Validation at record time

- Targeted pytest: `11 passed`.
- Private bridge build: passed; DLL SHA
  `d457689b0cae89f6a4c33482a764a7437fd1d49d2a7ae0461726e45bac769991`.
- Full Fast gate: pending when this record is written; final gate result is
  added to `docs/STATUS.md` only after the gate.
