#!/usr/bin/env python3
"""lap401 work — implement work card W4 §1 (B-1 tail-relocation layout).

Read-only, SHA-pinned, no game execution, no binary/memory writes. The
original EXE is only ever read; the candidate is rebuilt into memory by
`g2_unit_pool_expansion_v1.build_candidate` (no file is written).

W4 (`docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md`) required a
new B-1 layout provider that actually relocates unit_pool/unit_existence/
unit_age to the image tail, because lap400 REJECTed lap399's candidate for
delegating B-1 to `base_preserving_storage_layout_v1` (which keeps
unit_pool's base fixed by construction, so 0 of 1,014 collected pool fixups
were ever applied -- the pool grew in place and overlapped 1,311 live
`.text` literal sites in the bulk save/load blob).

This probe re-derives, from bytes, that the new
`tail_relocation_storage_layout_v1` module + rewired
`g2_unit_pool_expansion_v1` actually closes that gap:

  R1  identity   N=1200 candidate is still byte-identical to the original
                 (the required regression anchor, work card W4 §4).
  R2  applied    the candidate's `b3_fixup_site_counts` at N=1210 matches
                 the work card's required value EXACTLY
                 (unit_pool=1014, unit_existence=34, unit_age=4) -- an
                 unapplied pool ("unit_pool": 0) is an immediate FAIL
                 per the card; this is lap399's undetected defect.
  Ga  destination the ORIGINAL binary has no live `.text` literal reference
                 into the new tail destination `[pool.new_start,
                 age.new_end)`, except the one already-classified
                 non-address site (lap400 D4: `push 0x1100007`).
  Gb  blob       relocating existence/age out of the bulk save/load blob
                 `[0x892410, 0x975D8C)` removes exactly the sites whose
                 literal encoded an existence/age address; it introduces
                 no new reference into the blob and changes the value of
                 no site that remains inside it (i.e. category_slot_list_
                 a/b/active_slot_list are provably untouched).

Every check appends to `failures`; rc is 1 if any failed. `failures == []`
certifies only the byte facts listed above -- no runtime or product claim.
Save/load compatibility is explicitly NOT covered (W4 §6: relocating
existence/age out of the bulk blob necessarily breaks it; that is a
follow-up blocker, not this probe's scope).

Usage:
  python3 docs/history/laps/probes/20260920_lap401_work_g2_pool_tail_relocation_probe.py \
      [--exe PATH] [--output PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import capstone
import pefile

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patches.population.g2_unit_pool_expansion_v1 import (  # noqa: E402
    _decode,
    _text_section,
    build_candidate,
)
from patches.population.tail_relocation_storage_layout_v1 import (  # noqa: E402
    BULK_BLOB_END,
    BULK_BLOB_START,
    ORIGINAL_SHA256,
    layout,
)

CANDIDATE_N = 1210
STOCK_CAPACITY = 1200
DEFAULT_EXE = Path("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus/syw2plus_original.exe")

# lap400 D4's single known non-address false positive in the tail destination.
G_A_KNOWN_NON_ADDRESS_SITES = frozenset({0x00401402})

EXPECTED_B3_COUNTS = {"unit_pool": 1014, "unit_existence": 34, "unit_age": 4}


def _literal_operands_in_range(data: bytes, lo: int, hi: int) -> dict[str, list]:
    pe = pefile.PE(data=data, fast_load=True)
    try:
        text_va, _raw, text_bytes = _text_section(pe)
    finally:
        pe.close()
    insns = _decode(text_bytes, text_va)
    hits: dict[int, tuple[str, int]] = {}
    for insn in insns:
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_MEM:
                value = int(op.mem.disp) & 0xFFFFFFFF
                kind = "disp"
            elif op.type == capstone.x86.X86_OP_IMM:
                value = int(op.imm) & 0xFFFFFFFF
                kind = "imm"
            else:
                continue
            if lo <= value < hi:
                hits[insn.address] = (kind, value)
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, default=DEFAULT_EXE)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    failures: list[str] = []
    original = args.exe.read_bytes()
    original_sha = hashlib.sha256(original).hexdigest()
    if original_sha != ORIGINAL_SHA256:
        failures.append(f"original SHA mismatch: {original_sha} != {ORIGINAL_SHA256}")

    # R1: N=1200 identity.
    patched_1200, report_1200 = build_candidate(original, STOCK_CAPACITY)
    r1_identical = patched_1200 == original
    if not r1_identical:
        failures.append("R1: N=1200 candidate is not byte-identical to original")

    # R2: N=1210 fixup-site counts.
    patched_1210, report_1210 = build_candidate(original, CANDIDATE_N)
    r2_counts = report_1210["b3_fixup_site_counts"]
    if r2_counts != EXPECTED_B3_COUNTS:
        failures.append(f"R2: b3_fixup_site_counts {r2_counts} != {EXPECTED_B3_COUNTS}")

    # Ga: original has no live reference into the new tail destination.
    result = layout(CANDIDATE_N)
    tail_lo, tail_hi = result.regions[0].new_start, result.regions[-1].new_end
    ga_hits = _literal_operands_in_range(original, tail_lo, tail_hi)
    ga_unclassified = {va: v for va, v in ga_hits.items() if va not in G_A_KNOWN_NON_ADDRESS_SITES}
    if ga_unclassified:
        failures.append(f"Ga: unclassified literal reference(s) into tail destination: {ga_unclassified}")

    # Gb: bulk blob references unaffected except the relocated sites.
    before = _literal_operands_in_range(original, BULK_BLOB_START, BULK_BLOB_END)
    after = _literal_operands_in_range(patched_1210, BULK_BLOB_START, BULK_BLOB_END)
    gb_added = {va: v for va, v in after.items() if va not in before}
    gb_changed = {va: (before[va], v) for va, v in after.items() if va in before and before[va] != v}
    if gb_added:
        failures.append(f"Gb: new reference(s) introduced into bulk blob: {gb_added}")
    if gb_changed:
        failures.append(f"Gb: value changed for site still inside bulk blob: {gb_changed}")

    report = {
        "lap": 401,
        "role": "work",
        "provider_model_effort": "Claude Code claude-sonnet-5 / high",
        "work_card": "docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md",
        "original_sha256": original_sha,
        "r1_n1200_identity": r1_identical,
        "r1_n1200_candidate_sha256": report_1200["candidate_sha256"],
        "r2_n1210_b3_fixup_site_counts": r2_counts,
        "r2_n1210_candidate_sha256": report_1210["candidate_sha256"],
        "r2_n1210_deltas": report_1210["deltas"],
        "ga_tail_destination_range": [hex(tail_lo), hex(tail_hi)],
        "ga_hits": {hex(va): list(v) for va, v in ga_hits.items()},
        "gb_bulk_blob_range": [hex(BULK_BLOB_START), hex(BULK_BLOB_END)],
        "gb_before_count": len(before),
        "gb_after_count": len(after),
        "gb_removed_count": len(set(before) - set(after)),
        "gb_added": {hex(va): list(v) for va, v in gb_added.items()},
        "gb_changed": {hex(va): [list(v[0]), list(v[1])] for va, v in gb_changed.items()},
        "failures": failures,
    }

    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text)
    print(text)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
