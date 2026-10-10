#!/usr/bin/env python3
"""SPIKE-ONLY 2610 candidate: relocate the six stock unit-capacity arrays.

This is **not** a deliverable build and is gated behind an explicit ``spike=True``
flag that writes only into a caller-supplied private directory, never a
deliverable path.  :mod:`patches.esl2610.g2_pool4093_2610` stays fail-closed.

The transform is the accepted 2608/stock G2 ``.text`` relocation, rebased onto
2610.  The accepted stock builder (``g2_full_capacity_persistence_compat_v1``)
produces, at capacity 4093, a byte-exact set of ``.text`` edits that relocate
the unit pool, existence/age words and the three slot lists into a packed block
at stock tail base ``0x108C000``.  1330 of its 1335 ``.text`` edit runs have
identical *old* bytes on 2610 (verified), and because both the stock build and
this build use the same packed geometry, every relocated address differs only
by a constant base delta.  So this builder:

* compacts the 2610 headers and appends one ``.g2bss`` section at the image tail
  holding the six-array packed block (``+delta`` from the stock block);
* replays each stock ``.text`` edit run onto 2610 at the same VA, adding
  ``delta`` to any changed dword that falls inside the stock relocated block and
  copying every other changed byte verbatim (counts, the ``-2N`` displacement,
  the destroy-all/post-load bounds are base-independent);
* skips five runs that are 2610-specific (the kept official 1008 cap, the two
  ESL NOP/prefixed-write collisions, and two accesses 2610 redirected into new
  modules) and the save/load wrapper redirects (save/load is not exercised by
  the live memory-safety spike).

What this spike deliberately does **not** do: the four direct-indexed per-unit
arrays and the ~40 new official modules keep their stock references, so at
slot > 1200 the first new module that touches a high slot is expected to fail --
that first-failing module is the isolation result the runtime spike records.
The static build is validated byte-exact against the rebased stock candidate.
"""

from __future__ import annotations

import hashlib
from typing import Any

import pefile

from patches.esl2610 import g2_reloc_2610, pe_extend
from patches.population.full_tail_relocation_storage_layout_v1 import layout as _stock_layout

STOCK_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
CAPACITY = g2_reloc_2610.CAPACITY
_STOCK = _stock_layout(CAPACITY)
STOCK_BLOCK_LO = _STOCK.regions[0].new_start           # 0x108C000
STOCK_BLOCK_HI = _STOCK.regions[-1].new_end            # 0x17F09D4
STOCK_RSRC_LO = _STOCK.rsrc.new_start                  # moved .rsrc (wrapper caves)
TEXT_RVA = 0x1000
BULK_BASE = 0x00892410  # bulk game-state object; its methods reach the lists relative to it
TEXT_SPAN = 0xE3AE5

# 2610-specific runs (by VA) that must NOT be replayed from the stock candidate.
# The oracle's non-G2 *product* edits (owner cap 1200, fixed supply 5000) are
# excluded separately by :func:`_product_only_offsets`, so the official 1008 cap
# and the official supply formula stay untouched.
SKIP_VAS = {
    0x0047BA11,  # ESL NOP'd test site (2610 already 0x90...), stock relocates here
    0x0047E51D,  # ESL prefixed unit-write collision
    0x004B0604,  # 2610 redirected this access into a new module (jmp)
    0x004B1FC9,  # 2610 redirected this access into a new module (jmp)
    # The oracle's save/load stream call redirects into its .rsrc caves: their
    # rel32 happens to fall inside the stock block range and would be "rebased"
    # into a call into .g2bss.  Layer 4 (g2_persist_2610) redirects these.
    0x00440F0D, 0x004412DD, 0x00440C71, 0x00441041,
}


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _product_only_offsets(stock: bytes) -> set[int]:
    """File offsets the oracle's non-G2 product layer changes (owner cap, supply).

    The same product composition built at capacity 1200 leaves the capacity
    layer a no-op, so its diff against stock is exactly the product edits.
    """
    from patches.population.g2_full_capacity_supply5000_owner1200_v1 import (
        build_candidate as build_product,
    )

    product, _ = build_product(stock, 1200)
    return {i for i in range(len(stock)) if stock[i] != product[i]}


def _text_runs(stock: bytes, stock_cand: bytes) -> list[tuple[int, int]]:
    raw = pefile.PE(data=stock, fast_load=True)
    try:
        text = next(s for s in raw.sections if s.Name.rstrip(b"\0") == b".text")
        rp = int(text.PointerToRawData)
        span = int(text.SizeOfRawData)
    finally:
        raw.close()
    runs: list[tuple[int, int]] = []
    i = rp
    end = rp + span
    while i < end:
        if stock[i] == stock_cand[i]:
            i += 1
            continue
        start = i
        while i < end and stock[i] != stock_cand[i]:
            i += 1
        runs.append((start, i))  # file offsets, == RVA offsets since text rp==0x1000==rva
    return runs


def build_spike_candidate(data: bytes, stock: bytes, *, extra_bss: int = 0
                          ) -> tuple[bytes, dict[str, Any]]:
    pe_extend.verify_base(data)
    if _digest(stock) != STOCK_SHA256:
        raise ValueError("pinned stock EXE SHA256 mismatch")
    # Lazy import so the deliverable builder never pulls the stock oracle path.
    from patches.population.g2_full_capacity_persistence_compat_v1 import (
        build_candidate as build_stock,
    )

    stock_cand, _ = build_stock(stock, CAPACITY)

    # One .g2bss for the six-array block + the four direct-indexed arrays.
    plan = g2_reloc_2610.plan_spike(data, require_pinned_base=False)
    g2bss_size = plan.six_array_span + sum(
        int(a["span_4093"], 16) for a in plan.direct_arrays
    ) + extra_bss  # extra_bss: room a later layer packs after the arrays
    image = pe_extend.compact_headers(data)
    image = pe_extend.add_section(
        image, b".g2bss", b"", (g2bss_size + 0xFFF) & ~0xFFF, pe_extend.BSS_RW
    )
    six_base = pe_extend.section_va(image, b".g2bss")
    delta = six_base - STOCK_BLOCK_LO

    out = bytearray(image)
    raw = pefile.PE(data=bytes(out), fast_load=True)
    try:
        text = next(s for s in raw.sections if s.Name.rstrip(b"\0") == b".text")
        text_rp = int(text.PointerToRawData)
    finally:
        raw.close()

    runs = _text_runs(stock, stock_cand)
    product_only = _product_only_offsets(stock)
    applied = skipped = rebased = product_skipped = bulk_rebased = 0
    for lo, hi in runs:
        va = pe_extend.IMAGE_BASE + lo  # text rp == rva base (0x1000)
        if any(i in product_only for i in range(lo, hi)):
            product_skipped += 1
            continue
        if va in SKIP_VAS:
            skipped += 1
            continue
        # verify 2610 old bytes match stock old bytes at this run
        off2610 = text_rp + (lo - TEXT_RVA)
        if bytes(out[off2610 : off2610 + (hi - lo)]) != stock[lo:hi]:
            # a 2610-specific delta we did not anticipate: fail closed
            raise ValueError(f"unexpected 2610 .text divergence at VA 0x{va:08x}")
        length = hi - lo
        new = bytearray(stock_cand[lo:hi])
        if length == 4:
            dword = int.from_bytes(new, "little")
            if STOCK_BLOCK_LO <= dword < STOCK_BLOCK_HI:
                new = (dword + delta).to_bytes(4, "little")
                rebased += 1
            elif STOCK_RSRC_LO <= dword:
                # a wrapper/.rsrc address (save/load path) -- skip, not exercised
                skipped += 1
                continue
        elif length < 4:
            # A displacement relative to the bulk game-state object (this =
            # 0x892410) whose high byte did not change: the oracle points it
            # into its packed block, so it needs the same rebase as an
            # absolute address.
            dword = int.from_bytes(stock_cand[lo : lo + 4], "little")
            if STOCK_BLOCK_LO <= (dword + BULK_BASE) & 0xFFFFFFFF < STOCK_BLOCK_HI:
                if (stock_cand[lo + length : lo + 4] != stock[lo + length : lo + 4]
                        or out[off2610 + length : off2610 + 4] != stock[lo + length : lo + 4]):
                    raise ValueError(f"bulk-relative run at VA 0x{va:08x} is not a dword")
                new = bytearray(((dword + delta) & 0xFFFFFFFF).to_bytes(4, "little"))
                length = 4
                bulk_rebased += 1
        out[off2610 : off2610 + length] = new
        applied += 1

    candidate = pe_extend._with_checksum(bytes(out))
    report = {
        "schema": "syw2plus.esl2610.g2-spike.v1",
        "status": "SPIKE_STATIC_ONLY_RUNTIME_PENDING",
        "input_sha256": _digest(data),
        "candidate_sha256": _digest(candidate),
        "capacity": CAPACITY,
        "g2bss_va": hex(six_base),
        "rebase_delta": hex(delta),
        "text_runs_applied": applied,
        "text_runs_skipped": skipped,
        "product_runs_skipped": product_skipped,
        "rebased_address_dwords": rebased,
        "rebased_bulk_relative_disps": bulk_rebased,
        "note": "six-array relocation only; direct-index arrays and new modules "
        "keep stock refs (expected first-failing-module isolation at slot>1200)",
    }
    return candidate, report


def verify_against_oracle(data: bytes, stock: bytes, candidate: bytes) -> dict[str, Any]:
    """Byte-exact self-check: un-rebasing the candidate .text reproduces the
    stock candidate .text at every applied run."""
    from patches.population.g2_full_capacity_persistence_compat_v1 import (
        build_candidate as build_stock,
    )

    stock_cand, _ = build_stock(stock, CAPACITY)
    image = pe_extend.compact_headers(data)
    plan = g2_reloc_2610.plan_spike(data, require_pinned_base=False)
    g2bss_size = plan.six_array_span + sum(int(a["span_4093"], 16) for a in plan.direct_arrays)
    image = pe_extend.add_section(
        image, b".g2bss", b"", (g2bss_size + 0xFFF) & ~0xFFF, pe_extend.BSS_RW
    )
    six_base = pe_extend.section_va(image, b".g2bss")
    delta = six_base - STOCK_BLOCK_LO
    mismatches = 0
    checked = 0
    product_only = _product_only_offsets(stock)
    for lo, hi in _text_runs(stock, stock_cand):
        va = pe_extend.IMAGE_BASE + lo
        if va in SKIP_VAS or any(i in product_only for i in range(lo, hi)):
            continue
        length = hi - lo
        got = bytearray(candidate[lo:hi])  # candidate text rp == 0x1000 too
        sdw = int.from_bytes(stock_cand[lo : lo + 4], "little")
        if length < 4 and STOCK_BLOCK_LO <= (sdw + BULK_BASE) & 0xFFFFFFFF < STOCK_BLOCK_HI:
            cdw = int.from_bytes(candidate[lo : lo + 4], "little")
            got = bytearray(((cdw - delta) & 0xFFFFFFFF).to_bytes(4, "little"))[:length]
        if length == 4:
            dword = int.from_bytes(got, "little")
            if six_base <= dword < six_base + plan.six_array_span:
                got = (dword - delta).to_bytes(4, "little")
            elif STOCK_RSRC_LO <= int.from_bytes(stock_cand[lo:hi], "little"):
                continue  # skipped wrapper addr
        checked += 1
        if bytes(got) != stock_cand[lo:hi]:
            mismatches += 1
    return {"runs_checked": checked, "mismatches": mismatches}


def main() -> None:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("stock", type=Path)
    parser.add_argument("--out", type=Path, help="PRIVATE spike output path (required to write)")
    parser.add_argument("--spike", action="store_true", help="explicitly allow a spike write")
    args = parser.parse_args()
    data = args.source.read_bytes()
    stock = args.stock.read_bytes()
    candidate, report = build_spike_candidate(data, stock)
    report["oracle_check"] = verify_against_oracle(data, stock, candidate)
    if args.out:
        if not args.spike:
            raise SystemExit("refusing to write a spike candidate without --spike")
        deliver = Path(__file__).resolve().parents[1]
        if deliver in args.out.resolve().parents:
            raise SystemExit("refusing to write a spike candidate into a deliverable path")
        args.out.write_bytes(candidate)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
