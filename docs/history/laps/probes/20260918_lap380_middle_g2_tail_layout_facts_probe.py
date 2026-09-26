#!/usr/bin/env python3
"""lap380 middle read-only probe: re-derive the tail-layout structural facts.

Independently re-derives, from the pinned original image only, the facts that the
lap379 feasibility card and the Astra base-preserving branch depend on.  Reads
bytes; never writes, never patches, never launches the game.

Exit 0 only when every assertion holds; each failure is printed and counted.
"""

from __future__ import annotations

import hashlib
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
ORIGINAL = REPO / "Syw2plus/syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

IMAGE_BASE = 0x400000
UNIT_BASE_VA = 0x0066B790
UNIT_STRIDE = 0x758
UNIT_END_VA = 0x00892410  # also the documented bulk-save start
STOCK_SLOTS = 1200

failures: list[str] = []


def check(name: str, condition: bool, detail: str) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}: {detail}")
    if not condition:
        failures.append(name)


def main() -> int:
    data = ORIGINAL.read_bytes()
    check(
        "original_sha256",
        hashlib.sha256(data).hexdigest() == ORIGINAL_SHA256,
        hashlib.sha256(data).hexdigest(),
    )

    pe = struct.unpack_from("<I", data, 0x3C)[0]
    check("pe_signature", data[pe : pe + 4] == b"PE\0\0", data[pe : pe + 4].hex())
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    optsz = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24

    image_base = struct.unpack_from("<I", data, opt + 28)[0]
    sec_align = struct.unpack_from("<I", data, opt + 32)[0]
    file_align = struct.unpack_from("<I", data, opt + 36)[0]
    size_of_image = struct.unpack_from("<I", data, opt + 56)[0]
    check("image_base", image_base == IMAGE_BASE, hex(image_base))
    print(f"[INFO] section_alignment={hex(sec_align)} file_alignment={hex(file_align)}")
    print(f"[INFO] size_of_image={hex(size_of_image)} number_of_sections={nsec}")

    nrva = struct.unpack_from("<I", data, opt + 92)[0]
    dirs: dict[int, tuple[int, int]] = {}
    for i in range(nrva):
        rva, size = struct.unpack_from("<II", data, opt + 96 + i * 8)
        if rva or size:
            dirs[i] = (rva, size)
            print(f"[INFO] datadir[{i}] rva={hex(rva)} size={hex(size)}")

    sec_table = pe + 24 + optsz
    sections = []
    for i in range(nsec):
        off = sec_table + i * 40
        name = data[off : off + 8].rstrip(b"\0").decode("ascii", "replace")
        vsz, va, rsz, rp = struct.unpack_from("<IIII", data, off + 8)
        chars = struct.unpack_from("<I", data, off + 36)[0]
        sections.append((name, va, vsz, rp, rsz, chars))
        print(
            f"[INFO] section {name:<8} va={hex(va)} vsz={hex(vsz)} "
            f"raw={hex(rp)} rsz={hex(rsz)} va_end={hex(IMAGE_BASE + va + vsz)} chars={hex(chars)}"
        )

    # Unit body geometry: base + stride * 1200 must land exactly on the bulk start.
    computed_end = UNIT_BASE_VA + UNIT_STRIDE * STOCK_SLOTS
    check(
        "unit_end_equals_bulk_start",
        computed_end == UNIT_END_VA,
        f"{hex(UNIT_BASE_VA)} + {hex(UNIT_STRIDE)}*{STOCK_SLOTS} = {hex(computed_end)}",
    )

    # Which section owns the Unit body, and is the whole Unit tail beyond raw data?
    owner = None
    for name, va, vsz, rp, rsz, _chars in sections:
        lo = IMAGE_BASE + va
        if lo <= UNIT_BASE_VA < lo + vsz:
            owner = (name, lo, vsz, rp, rsz)
    check("unit_body_has_owning_section", owner is not None, str(owner))
    if owner is not None:
        name, lo, vsz, rp, rsz = owner
        raw_end_va = lo + rsz
        virt_end_va = lo + vsz
        print(
            f"[INFO] unit owner section={name} va={hex(lo)} "
            f"raw_end_va={hex(raw_end_va)} virtual_end_va={hex(virt_end_va)}"
        )
        check(
            "unit_body_is_entirely_bss",
            UNIT_BASE_VA >= raw_end_va,
            f"unit_base {hex(UNIT_BASE_VA)} >= raw_end {hex(raw_end_va)}",
        )
        check(
            "bulk_start_is_entirely_bss",
            UNIT_END_VA >= raw_end_va,
            f"bulk_start {hex(UNIT_END_VA)} >= raw_end {hex(raw_end_va)}",
        )
        check(
            "unit_tail_inside_owning_section",
            UNIT_END_VA <= virt_end_va,
            f"bulk_start {hex(UNIT_END_VA)} <= virtual_end {hex(virt_end_va)}",
        )

    # Sections that sit above the Unit tail must move if space is inserted there.
    movers = [s for s in sections if IMAGE_BASE + s[1] >= UNIT_END_VA]
    print(f"[INFO] sections_at_or_above_bulk_start={[s[0] for s in movers]}")
    check(
        "resource_directory_present",
        2 in dirs,
        f"resource rva={hex(dirs[2][0]) if 2 in dirs else 'none'}",
    )
    if 2 in dirs:
        rsrc_rva = dirs[2][0]
        rsrc_va = IMAGE_BASE + rsrc_rva
        check(
            "resource_lies_above_unit_tail",
            rsrc_va >= UNIT_END_VA,
            f"rsrc_va={hex(rsrc_va)} bulk_start={hex(UNIT_END_VA)}",
        )

    # A relocation directory would let the loader rebase; its absence is the reason
    # every absolute VA above the tail has to be fixed up by hand.
    check(
        "no_base_relocation_directory",
        5 not in dirs,
        f"basereloc={'absent' if 5 not in dirs else hex(dirs[5][0])}",
    )

    print()
    print(f"failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
