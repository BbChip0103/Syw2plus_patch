# lap102 Luna G1-A coordinate input provenance probe

## Goal / role

- Date/lap: 2026-09-11 KST / lap102
- Provider/model/effort/role: Codex / gpt-5.6-luna / high / work-tier hands-on implementation
- Goal: Trace exactly one `0x00637734/0x00637736` coordinate path from the original OS
  input/message handler to the existing `0x00437E90` updater. Do not implement gameplay or
  claim G1 completion.

## Hypothesis and expected result

- Hypothesis: the coordinate words consumed at `0x0041E626/0x0041E62C` originate from the
  original Win32 message pump through the WndProc mouse-message event ring.
- Expected pass: both fixed originals have the same pinned SHA and exact old bytes at the
  WndProc registration, message dispatch, mouse coordinate, event-ring, coordinate-word, and
  updater call boundaries; direct call targets agree with instruction boundaries.
- Fail condition: any SHA, old-byte, or direct-target drift, or an ambiguous break in this
  single path. No alternate bit-state path was enumerated in this lap.

## Observation / implementation

- `RegisterClassA` receives WndProc `0x00423DC0` from `0x00423C34` and is called at `0x00423C8B`;
  main loop `DispatchMessageA` is the IAT call at `0x004232FC`.
- WM_MOUSEMOVE handler `0x0042434B` decodes `lParam`, stores low/high coordinates at
  `0x00C0CB58/0x00C0CB5C`, and calls event-ring writer `0x004216B0` at `0x0042436F`.
- The game tick calls `0x0041C740` at `0x00423FE8`, then `0x0041E220` at `0x0041C81E`;
  `0x0041E220` reads the event ring through `0x004217B0` at `0x0041E299`.
- Conversion call `0x0041E464→0x004516A0` is followed by writes at `0x0041E4AF/0x0041E4B6`
  to `0x00637734/0x00637736`. The updater loads these words at `0x0041E626/0x0041E62C` and
  calls `0x00437E90` at `0x0041E635`.
- Added `INPUT_PROVENANCE_BYTES` and `INPUT_PROVENANCE_CALLS` to the read-only SHA-gated binary
  contract, plus one regression test. No original/reference/candidate executable was modified.

## Evidence / environment

- Fixed originals:
  - `Syw2plus/syw2plus_original.exe`
  - `/home/dev_00/sharedfolder/260320_Syw2plus/syw2plus_original.exe`
- Both SHA-256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; `cmp` PASS.
  The original is PE32 i386; file offset mapping remains `VA - 0x00400000`.
- Post-write SHA-256 (excluding this self-referential history file) is:
  `tools/check_binary_contract.py` = `d025811b451f82b55a78245de1e2c00b611c525a7d052a2a4cae9bdc3f6f795b`,
  `tests/test_binary_contract.py` = `8eaf12175810feefc32a60963cc8999f873821ed4c8c253b55b7f43de96d36ce`,
  `docs/STATUS.md` = `b6be8c25d55fe3e176b301618a7a1f8e45aed0e22b8654cecbcaef6649d74c38`,
  `analysis/memory_maps/player_offsets.md` =
  `8ac8a45cee82f0a12d3fce242b87af7f4fd79039a5991d4e37a7a1fd362fe79c`.
  No commit was created (`LOOP_ALLOW_COMMITS=0`).

## Commands / results

- `pytest -q tests/test_binary_contract.py` → **13 passed**.
- `make check` → **140 passed**; Ruff, compileall, mypy, and `CONTEXT_PASS` all passed.
- `.venv/bin/python checks/safety.py` → `SAFETY_PASS`.
- `make doctor` → `ok=true`, original `verified`; runtime manifest absent, so runtime/game/fixture
  execution was SKIP and no runtime success was claimed.

## Metrics / judgment / next

- Static coordinate OS-input provenance: **PASS**.
- Gameplay action/field meaning, 1600×1200 output, actual input behavior, G1: **UNKNOWN / BLOCKED**.
- Regression risk: low for repository code; the contract is read-only and fail-closed on SHA/bytes.
  Runtime remains intentionally untouched.
- Independent review: required from next Sol/Opus5/high middle; no user milestone approval.
- Next one: independently re-extract the contract and decide whether this static OS-input path is
  the production gameplay action path or where the exact semantic break remains. Until then,
  prohibit implementation, game run, fixture, and coordinate changes.
