#!/usr/bin/env python3
"""lap402 middle -- independent review of lap401's W4 §1 B-1 tail relocation.

Read-only, SHA-pinned, no game execution, no binary writes, no memory writes.
The original EXE is only ever read; candidates are rebuilt in memory.

lap401 (work, `claude-sonnet-5`/high) implemented
`patches/population/tail_relocation_storage_layout_v1.py` and rewired
`g2_unit_pool_expansion_v1.py` onto it, reporting R1/R2/Ga/Gb PASS.  This
probe does NOT trust that probe's `failures == []`; it re-derives the same
byte facts through its own code path and then asks the question that work
card W4 §4's two gates (G-a, G-b) do not ask:

    *Is the relocated block actually inside a declared PE section?*

Checks (each appends to `failures`; rc 1 if any fail):

  C1  identity    N=1200 candidate is byte-identical to the original.
  C2  counts      N=1210 `b3_fixup_site_counts` == the work card's pinned
                  `{"unit_pool":1014,"unit_existence":34,"unit_age":4}`.
  C3  fixups      Independent re-derivation of lap401's `_patch_literal`
                  re-decode repair (lap401 review target 2): disassemble
                  original and candidate `.text` side by side and require
                  (a) identical instruction boundaries -- no length drift,
                  (b) the set of instructions whose literal operands
                  changed is EXACTLY the 4 B-2 sites plus the B-3 sites,
                  (c) every changed B-3 literal equals old + that region's
                  relocation delta.  A window bug that patched the wrong
                  occurrence would show up here as a changed site outside
                  the expected set, or a wrong new value.
  C4  Ga          original `.text` has no unclassified literal reference
                  into the new tail destination (re-derived).
  D1  coverage    NEW -- every byte of the relocated pool/existence/age
                  block lies inside some section's declared virtual extent
                  [VA, VA+VirtualSize) in the candidate's own section
                  table.  This is the mechanism `build_layout_artifact`
                  claims to provide by growing `.data` VirtualSize.
  D2  repair      Report the `.data` VirtualSize that WOULD cover the block
                  and whether it still satisfies the module's own
                  "must not overlap the new .rsrc RVA" guard -- i.e. is the
                  defect repairable without changing the placement design.

`failures == []` would certify only these byte facts.  It is not a runtime,
product, or milestone claim; no candidate has ever been executed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import capstone
import pefile

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patches.population.g2_unit_pool_expansion_v1 import (  # noqa: E402
    B2_SITES,
    _decode,
    _text_section,
    build_candidate,
    collect_fixup_sites,
)
from patches.population.tail_relocation_storage_layout_v1 import (  # noqa: E402
    ORIGINAL_SHA256,
    layout,
)

IMAGE_BASE = 0x00400000
STOCK_CAPACITY = 1200
CANDIDATE_N = 1210
DEFAULT_EXE = Path("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus/syw2plus_original.exe")

EXPECTED_B3_COUNTS = {"unit_pool": 1014, "unit_existence": 34, "unit_age": 4}
G_A_KNOWN_NON_ADDRESS_SITES = frozenset({0x00401402})


def sections(data: bytes) -> list[dict[str, int | str]]:
    pe_off = struct.unpack_from("<I", data, 0x3C)[0]
    num = struct.unpack_from("<H", data, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe_off + 20)[0]
    table = pe_off + 24 + opt_size
    out = []
    for i in range(num):
        off = table + i * 40
        name = data[off : off + 8].rstrip(b"\0").decode()
        vsz, va, rsz, rp = struct.unpack_from("<IIII", data, off + 8)
        out.append(
            {
                "name": name,
                "va": IMAGE_BASE + va,
                "rva": va,
                "virtual_size": vsz,
                "virtual_end": IMAGE_BASE + va + vsz,
                "raw_size": rsz,
                "raw_ptr": rp,
            }
        )
    return out


def literal_sites(data: bytes) -> dict[int, tuple[int, tuple]]:
    """{insn_va: (size, tuple of (kind, value) literal operands)} for all of .text."""
    pe = pefile.PE(data=data, fast_load=True)
    try:
        text_va, _raw, text_bytes = _text_section(pe)
    finally:
        pe.close()
    out: dict[int, tuple[int, tuple]] = {}
    for insn in _decode(text_bytes, text_va):
        lits = []
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_MEM:
                lits.append(("disp", int(op.mem.disp) & 0xFFFFFFFF))
            elif op.type == capstone.x86.X86_OP_IMM:
                lits.append(("imm", int(op.imm) & 0xFFFFFFFF))
        out[insn.address] = (insn.size, tuple(lits))
    return out


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

    # ---- C1: identity anchor -------------------------------------------------
    cand_1200, _rep_1200 = build_candidate(original, STOCK_CAPACITY)
    c1_identity = cand_1200 == original
    if not c1_identity:
        failures.append("C1: N=1200 candidate is not byte-identical to the original")

    # ---- C2: pinned fixup counts --------------------------------------------
    cand, report = build_candidate(original, CANDIDATE_N)
    c2_counts = report["b3_fixup_site_counts"]
    if c2_counts != EXPECTED_B3_COUNTS:
        failures.append(f"C2: b3_fixup_site_counts {c2_counts} != {EXPECTED_B3_COUNTS}")

    result = layout(CANDIDATE_N)
    deltas = {r.name: r.new_start - r.old_start for r in result.regions}

    # ---- C3: independent re-derivation of the applied fixups -----------------
    before = literal_sites(original)
    after = literal_sites(cand)

    c3_boundary_drift = sorted(
        hex(va) for va in set(before) | set(after) if before.get(va, (None,))[0] != after.get(va, (None,))[0]
    )
    if c3_boundary_drift:
        failures.append(f"C3: instruction boundary/length drift at {c3_boundary_drift[:20]}")

    changed = {va for va in before if va in after and before[va][1] != after[va][1]}

    b2_vas = {site["va"] for site in B2_SITES}
    sites_by_region = collect_fixup_sites(original)
    expected_b3_vas: dict[int, str] = {}
    for region, region_sites in sites_by_region.items():
        if deltas[region] == 0:
            continue
        for site in region_sites:
            expected_b3_vas[site.va] = region

    expected_changed = b2_vas | set(expected_b3_vas)
    unexpected = sorted(hex(va) for va in changed - expected_changed)
    missing = sorted(hex(va) for va in expected_changed - changed)
    if unexpected:
        failures.append(f"C3: instruction(s) changed that no fixup site covers: {unexpected[:20]}")
    if missing:
        failures.append(f"C3: expected fixup site(s) left unpatched: {missing[:20]}")

    # every changed B-3 literal must be exactly old + that region's delta
    c3_wrong_value = []
    for va, region in expected_b3_vas.items():
        delta = deltas[region]
        olds = [v for _k, v in before[va][1]]
        news = [v for _k, v in after[va][1]]
        if len(olds) != len(news):
            c3_wrong_value.append(hex(va))
            continue
        for o, n in zip(olds, news):
            if n != o and n != ((o + delta) & 0xFFFFFFFF):
                c3_wrong_value.append(f"{hex(va)}:0x{o:08x}->0x{n:08x}")
    if c3_wrong_value:
        failures.append(f"C3: B-3 literal(s) not equal to old+delta: {c3_wrong_value[:20]}")

    # ---- C4: Ga re-derivation ------------------------------------------------
    tail_lo, tail_hi = result.regions[0].new_start, result.regions[-1].new_end
    c4_hits = {
        va: lits
        for va, (_sz, lits) in before.items()
        if any(tail_lo <= v < tail_hi for _k, v in lits)
    }
    c4_unclassified = {va: v for va, v in c4_hits.items() if va not in G_A_KNOWN_NON_ADDRESS_SITES}
    if c4_unclassified:
        failures.append(
            f"C4: unclassified reference(s) into the tail destination: "
            f"{ {hex(k): v for k, v in c4_unclassified.items()} }"
        )

    # ---- D1: is the relocated block inside a declared section? ---------------
    cand_sections = sections(cand)
    covered = 0
    for byte_range in [(r.new_start, r.new_end) for r in result.regions]:
        lo, hi = byte_range
        for sec in cand_sections:
            covered += max(0, min(hi, int(sec["virtual_end"])) - max(lo, int(sec["va"])))
    block_size = tail_hi - tail_lo
    uncovered = block_size - covered

    d1_per_region = []
    for r in result.regions:
        inside = 0
        for sec in cand_sections:
            inside += max(0, min(r.new_end, int(sec["virtual_end"])) - max(r.new_start, int(sec["va"])))
        d1_per_region.append(
            {
                "region": r.name,
                "new_start": hex(r.new_start),
                "new_end": hex(r.new_end),
                "span": r.new_end - r.new_start,
                "bytes_inside_a_declared_section": inside,
                "fully_covered": inside == r.new_end - r.new_start,
            }
        )

    if uncovered:
        failures.append(
            f"D1: {uncovered} of {block_size} bytes of the relocated pool/existence/age block "
            f"lie outside every declared section extent in the candidate's own section table"
        )

    data_sec = next(s for s in cand_sections if s["name"] == ".data")
    orig_data_sec = next(s for s in sections(original) if s["name"] == ".data")
    rsrc_sec = next(s for s in cand_sections if s["name"] == ".rsrc")
    first_bad_pool_slot = None
    pool = result.regions[0]
    if int(data_sec["virtual_end"]) < pool.new_end:
        first_bad_pool_slot = (int(data_sec["virtual_end"]) - pool.new_start) // pool.elem_size

    # ---- D2: is the defect repairable in place? ------------------------------
    required_data_vsz = tail_hi - int(data_sec["va"])
    d2_fits_under_guard = int(data_sec["rva"]) + required_data_vsz <= int(rsrc_sec["rva"])

    report_out = {
        "lap": 402,
        "role": "middle (review of lap401 work)",
        "provider_model_effort": "Claude Code claude-opus-5 / high",
        "work_card": "docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md",
        "reviewed": "docs/history/laps/20260920_lap401_work_g2_unit_pool_tail_relocation.md",
        "original_sha256": original_sha,
        "candidate_n": CANDIDATE_N,
        "candidate_sha256": report["candidate_sha256"],
        "c1_n1200_identity": c1_identity,
        "c2_b3_fixup_site_counts": c2_counts,
        "c3_instruction_boundary_drift": c3_boundary_drift,
        "c3_changed_site_count": len(changed),
        "c3_expected_changed_site_count": len(expected_changed),
        "c3_unexpected_changed_sites": unexpected,
        "c3_missing_fixup_sites": missing,
        "c3_wrong_value_sites": c3_wrong_value,
        "c4_tail_destination_range": [hex(tail_lo), hex(tail_hi)],
        "c4_hits": {hex(va): v for va, v in c4_hits.items()},
        "relocation_deltas": {k: hex(v) for k, v in deltas.items()},
        "d1_candidate_sections": [
            {
                "name": s["name"],
                "va": hex(int(s["va"])),
                "virtual_size": hex(int(s["virtual_size"])),
                "virtual_end": hex(int(s["virtual_end"])),
            }
            for s in cand_sections
        ],
        "d1_relocated_block": [hex(tail_lo), hex(tail_hi)],
        "d1_block_size": block_size,
        "d1_bytes_inside_a_declared_section": covered,
        "d1_bytes_outside_every_section": uncovered,
        "d1_per_region": d1_per_region,
        "d1_first_pool_slot_outside_data_vsize": first_bad_pool_slot,
        "d2_original_data_virtual_size": hex(int(orig_data_sec["virtual_size"])),
        "d2_candidate_data_virtual_size": hex(int(data_sec["virtual_size"])),
        "d2_candidate_data_vsize_growth": int(data_sec["virtual_size"]) - int(orig_data_sec["virtual_size"]),
        "d2_required_data_virtual_size": hex(required_data_vsz),
        "d2_required_growth": required_data_vsz - int(orig_data_sec["virtual_size"]),
        "d2_repair_fits_under_existing_rsrc_guard": d2_fits_under_guard,
        "d2_slack_bytes_to_new_rsrc_rva": int(rsrc_sec["rva"]) - (int(data_sec["rva"]) + required_data_vsz),
        "failures": failures,
    }

    text = json.dumps(report_out, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text)
    print(text)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
