#!/usr/bin/env python3
"""lap400 middle — independent review of the lap399 N=1210 pool candidate.

Read-only, SHA-pinned, no game execution, no binary/memory writes.  The
original EXE is only ever read; the candidate is rebuilt into memory from the
original bytes by the lap399 module itself (no file is written).

PROMPT (6) 2-dan: a new confirm session independently checks the previous work
session's result.  lap399 (`docs/history/laps/20260920_lap399_work_g2_unit_pool
_expansion_candidate_and_boot_probe.md`) claimed:

  C1  N=1300 is unsafe because the grown pool footprint crosses
      category_slot_list_a/b and the FO-3 gap; N<=1217 is the safe bound and
      N=1210 was adopted.
  C2  The patcher's re-scanned site counts agree with two earlier independent
      probes (pool disp 986 / imm 28, existence 32/2, age 2/3-raw).
  C3  The candidate EXE `303c78f8...` is reproducible from the pinned original.
  C4  The observed `PS=40` boot stall is NOT a defect of the patch, because a
      byte-identical original renamed to `control_renamed_original.exe` stalls
      identically.

This probe re-derives C1-C3 from bytes and adds the check lap399 did not make:

  D1  overrun    which .text literal-address sites fall inside the address
                 range the grown pool physically occupies at N=1210,
                 `[pool_old_end, pool_old_end + stride*(N-1200))`.  lap399
                 checked this range against catA/catB/the FO-3 gap only; it
                 never asked whether the range is *referenced at all*.
  D2  applied    how many fixups the candidate actually applies per region.
                 `base_preserving_storage_layout_v1` keeps unit_pool's base
                 fixed by construction, so the pool delta is 0 and every one
                 of the pool sites counted in C2 is applied ZERO times.
  D3  dest       whether the relocated existence/age destination is inside the
                 bulk save/load blob `[0x892410, +0xE397C)` that `fread`
                 overwrites wholesale at load time.
  D4  tail       reference count in the image-tail destination that work card
                 W3 section B-1 actually asked for ("grow the image tail,
                 above `.rsrc`"), for comparison with D1.

Every check appends to `failures`; rc is 1 if any failed.  `failures == []`
certifies only the byte facts listed above -- no runtime or product claim.

Usage:
  python3 docs/history/laps/probes/20260920_lap400_middle_g2_pool_overrun_probe.py \
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

from patches.population.base_preserving_storage_layout_v1 import (  # noqa: E402
    BULK_OLD_LENGTH,
    ORIGINAL_SHA256,
    REGIONS,
    layout,
)
from patches.population.g2_unit_pool_expansion_v1 import (  # noqa: E402
    build_candidate,
    collect_fixup_sites,
)

IMAGE_BASE = 0x00400000
STOCK_CAPACITY = 1200
CANDIDATE_N = 1210
LAP399_CANDIDATE_SHA = "303c78f81f816ed82e495fa4545cc23af3fa7200344eb029b4e9f31cabe96522"

DEFAULT_EXE = Path("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus/syw2plus_original.exe")

# lap399 section 1's three collision landmarks, re-pinned here for C1.
CAT_A_BASE = 0x0089B008
CAT_B_BASE = 0x0089C2CA
FO3_GAP_BASE = 0x0089A388


def _text_literals(data: bytes) -> list[tuple[int, str, int, str, str]]:
    """Every `.text` operand that encodes a literal 32-bit value, as
    (insn_va, "disp"|"imm", value, mnemonic, op_str)."""
    pe = pefile.PE(data=data, fast_load=True)
    try:
        section = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".text")
        va = IMAGE_BASE + int(section.VirtualAddress)
        raw = int(section.PointerToRawData)
        text = data[raw : raw + int(section.SizeOfRawData)]
    finally:
        pe.close()
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    engine.detail = True
    engine.skipdata = True
    out: list[tuple[int, str, int, str, str]] = []
    for insn in engine.disasm(text, va):
        if insn.mnemonic == ".byte":
            continue
        for op in insn.operands:
            if op.type == capstone.x86.X86_OP_MEM:
                out.append(
                    (insn.address, "disp", int(op.mem.disp) & 0xFFFFFFFF, insn.mnemonic, insn.op_str)
                )
            elif op.type == capstone.x86.X86_OP_IMM:
                out.append(
                    (insn.address, "imm", int(op.imm) & 0xFFFFFFFF, insn.mnemonic, insn.op_str)
                )
    return out


def _in_range(literals, lo: int, hi: int):
    return [item for item in literals if lo <= item[2] < hi]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, default=DEFAULT_EXE)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    failures: list[str] = []
    report: dict[str, object] = {
        "probe": "lap400_middle_g2_pool_overrun",
        "reviews": "docs/history/laps/20260920_lap399_work_g2_unit_pool_expansion_candidate_and_boot_probe.md",
        "read_only": True,
        "game_executed": False,
    }

    original = args.exe.read_bytes()
    original_sha = hashlib.sha256(original).hexdigest()
    report["original"] = {"path": str(args.exe), "sha256": original_sha}
    if original_sha != ORIGINAL_SHA256:
        failures.append(f"original SHA mismatch: {original_sha}")
        report["failures"] = failures
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    pool, existence, age = REGIONS[0], REGIONS[1], REGIONS[2]
    pool_old_end = pool.base + pool.elem_size * STOCK_CAPACITY

    # ---- C1: lap399's N=1300 rejection and its N<=1217 bound -----------------
    c1: dict[str, object] = {}
    for n in (1210, 1217, 1218, 1300):
        end = layout(n).regions[0].new_end
        c1[str(n)] = {
            "pool_new_end": f"0x{end:08x}",
            "crosses_fo3_gap": end > FO3_GAP_BASE,
            "crosses_cat_a": end > CAT_A_BASE,
            "crosses_cat_b": end > CAT_B_BASE,
        }
    if not c1["1300"]["crosses_cat_a"]:  # type: ignore[index]
        failures.append("C1: N=1300 was expected to cross category_slot_list_a")
    if c1["1217"]["crosses_fo3_gap"] or not c1["1218"]["crosses_fo3_gap"]:  # type: ignore[index]
        failures.append("C1: the N<=1217 FO-3 gap bound did not reproduce")
    report["C1_lap399_n1300_rejection"] = {"verdict": "REPRODUCED", "per_n": c1}

    # ---- C2 / C3: collected site counts and candidate identity ---------------
    sites = collect_fixup_sites(original)
    collected = {
        region: {
            "disp": sum(1 for s in group if s.op_kind == "disp"),
            "imm": sum(1 for s in group if s.op_kind == "imm"),
            "total": len(group),
        }
        for region, group in sites.items()
    }
    if collected["unit_pool"] != {"disp": 986, "imm": 28, "total": 1014}:
        failures.append(f"C2: pool site counts changed: {collected['unit_pool']}")
    report["C2_collected_sites"] = collected

    candidate, build_report = build_candidate(original, CANDIDATE_N)
    candidate_sha = hashlib.sha256(candidate).hexdigest()
    if candidate_sha != LAP399_CANDIDATE_SHA:
        failures.append(f"C3: candidate SHA does not reproduce: {candidate_sha}")
    if hashlib.sha256(args.exe.read_bytes()).hexdigest() != ORIGINAL_SHA256:
        failures.append("C3: original changed during the build")
    identity, _ = build_candidate(original, STOCK_CAPACITY)
    if identity != original:
        failures.append("C3: N=1200 identity regression does not hold")
    report["C3_candidate"] = {
        "sha256": candidate_sha,
        "matches_lap399": candidate_sha == LAP399_CANDIDATE_SHA,
        "n1200_identity": identity == original,
        "original_unchanged": True,
    }

    # ---- D2: how many fixups are ACTUALLY applied ----------------------------
    applied = build_report["b3_fixup_site_counts"]
    deltas = build_report["deltas"]
    report["D2_applied_fixups"] = {"counts": applied, "deltas": deltas}
    if applied["unit_pool"] != 0:  # type: ignore[index]
        failures.append("D2: expected the base-preserving layout to apply 0 pool fixups")
    report["D2_finding"] = (
        "unit_pool delta is 0 -- the pool is NOT relocated.  All 1014 collected "
        "pool sites are applied 0 times.  The pool grows IN PLACE, which work "
        "card W3 section B-1 (lap397 A6) declared NOT_FEASIBLE and required to "
        "be replaced by relocation into new image-tail space."
    )

    # ---- D1: what the in-place growth physically overruns ---------------------
    literals = _text_literals(original)
    overrun_lo = pool_old_end
    overrun_hi = pool.base + pool.elem_size * CANDIDATE_N
    overrun = _in_range(literals, overrun_lo, overrun_hi)
    bulk_base_refs = _in_range(literals, pool_old_end, pool_old_end + 1)
    report["D1_overrun"] = {
        "range": f"[0x{overrun_lo:08x}, 0x{overrun_hi:08x})",
        "bytes": overrun_hi - overrun_lo,
        "text_literal_sites": len(overrun),
        "disp": sum(1 for x in overrun if x[1] == "disp"),
        "imm": sum(1 for x in overrun if x[1] == "imm"),
        "exact_bulk_base_literals": len(bulk_base_refs),
        "sample": [
            {"va": f"0x{a:08x}", "kind": k, "value": f"0x{v:08x}", "insn": f"{m} {o}"}
            for a, k, v, m, o in overrun[:8]
        ],
        "fixed_up_by_candidate": 0,
    }
    if not overrun:
        failures.append("D1: expected the overrun range to be referenced")
    report["D1_finding"] = (
        "At N=1210 the grown pool occupies the first 18,800 bytes of the live "
        "state / bulk save blob that starts exactly at pool_old_end 0x892410.  "
        "Those bytes are referenced by the listed .text sites, none of which "
        "the candidate rewrites -> slots 1200..1209 alias live globals.  "
        "S-6 (adjacent state undamaged) is violated by construction, and any "
        "S-2 observation of existence[slot>=1200] on this candidate could be "
        "bulk-load residue rather than a real allocation."
    )

    # ---- D3: is the relocated existence/age destination inside the bulk blob? -
    result = layout(CANDIDATE_N)
    dest_lo = result.regions[1].new_start
    dest_hi = result.regions[2].new_end
    bulk_lo, bulk_hi = pool_old_end, pool_old_end + BULK_OLD_LENGTH
    report["D3_existence_age_destination"] = {
        "range": f"[0x{dest_lo:08x}, 0x{dest_hi:08x})",
        "direct_text_literals": len(_in_range(literals, dest_lo, dest_hi)),
        "bulk_blob": f"[0x{bulk_lo:08x}, 0x{bulk_hi:08x})",
        "inside_bulk_blob": bulk_lo <= dest_lo and dest_hi <= bulk_hi,
        "finding": (
            "No direct literal references, but the destination lies inside the "
            "fixed-length bulk blob that load `fread`s wholesale at 0x4412DC "
            "and save writes from 0x440F02.  Loading save000 overwrites the "
            "relocated existence/age arrays with old-layout bytes."
        ),
    }
    if not (bulk_lo <= dest_lo and dest_hi <= bulk_hi):
        failures.append("D3: existence/age destination was expected inside the bulk blob")

    # ---- D4: the image-tail destination W3 B-1 actually asked for -------------
    pe = pefile.PE(data=original, fast_load=True)
    try:
        data_sec = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".data")
        data_end = IMAGE_BASE + int(data_sec.VirtualAddress) + int(data_sec.Misc_VirtualSize)
        size_of_image = int(pe.OPTIONAL_HEADER.SizeOfImage)
    finally:
        pe.close()
    need = pool.elem_size * CANDIDATE_N + existence.elem_size * CANDIDATE_N + age.elem_size * CANDIDATE_N
    tail_hits = _in_range(literals, data_end, data_end + need)
    report["D4_tail_destination"] = {
        "data_bss_end": f"0x{data_end:08x}",
        "size_of_image": f"0x{size_of_image:08x}",
        "bytes_needed_pool_existence_age": need,
        "range": f"[0x{data_end:08x}, 0x{data_end + need:08x})",
        "text_literal_sites": len(tail_hits),
        "sites": [
            {"va": f"0x{a:08x}", "kind": k, "value": f"0x{v:08x}", "insn": f"{m} {o}"}
            for a, k, v, m, o in tail_hits
        ],
        "finding": (
            "The tail destination carries orders of magnitude fewer literal "
            "collisions than the in-place overrun; any residual hit must be "
            "classified by the implementing session before it is used."
        ),
    }

    report["verdict"] = {
        "C1_n1300_unsafe": "ACCEPT (reproduced)",
        "C2_site_counts": "ACCEPT (reproduced)",
        "C3_candidate_reproducible": "ACCEPT (reproduced, original unchanged)",
        "C4_ps40_not_caused_by_patch": "NOT CHECKED HERE (runtime claim; see lap400 record)",
        "candidate_n1210": "REJECT -- in-place growth aliases live state (D1/D2/D3)",
        "next": "relocate pool+existence+age into virgin image-tail space (D4)",
    }
    report["failures"] = failures
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    print(encoded, end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
