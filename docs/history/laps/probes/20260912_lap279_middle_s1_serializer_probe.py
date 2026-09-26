"""lap279 middle probe — independent static review of the lap278 S1 six-row table.

Read-only. Runs objdump over the ORIGINAL exe and extracts the save/load block
tables, then maps the approved read-only addresses onto them. No game, no Wine,
no Xvfb, no Stage B, no writes to the original tree.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap279_middle_s1_serializer_probe.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

SAVE_ENTRY, SAVE_END = 0x440C20, 0x440FF0
LOAD_ENTRY, LOAD_END = 0x440FF0, 0x442E00
FWRITE, FREAD = "0x4da39f", "0x4da4a9"

# Approved read-only addresses, quoted from tools/runtime_env.py.
APPROVED = {
    "G1_SELECTION_COUNT_ADDRESS": 0x00899024,
    "G1_SELECTION_FIRST_SLOT_ADDRESS": 0x00899028,
    "G1_UNIT_EXISTS_BASE_ADDRESS": 0x008990C8,
    "G1_UNIT_BASE_ADDRESS": 0x0066B790,
    "G1_MAP_WIDTH_ADDRESS": 0x00B3DE34,
    "G1_MAP_HEIGHT_ADDRESS": 0x00B3DE36,
    "camera _read_camera": 0x00B42D7C,
    "logic tick": 0x008924B8,
    "player base 0x956770": 0x00956770,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disasm(start: int, stop: int) -> str:
    return subprocess.run(
        ["objdump", "-D", "-Mintel", "-j", ".text",
         f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(EXE)],
        check=True, capture_output=True, text=True,
    ).stdout


def blocks(text: str, callee: str) -> list[dict[str, object]]:
    """Recover fwrite/fread(ptr, size, count, file) from the 4 preceding pushes."""
    pushes: list[tuple[str, int | None]] = []
    out: list[dict[str, object]] = []
    for line in text.splitlines():
        m = re.match(r"\s*([0-9a-f]+):\t[0-9a-f ]+\t(\S+)\s*(.*)", line)
        if not m:
            continue
        addr, op, args = m.group(1), m.group(2), m.group(3).strip()
        if op == "push":
            val = int(args, 16) if re.fullmatch(r"0x[0-9a-f]+", args) else None
            pushes.append((args, val))
        elif op == "call":
            if callee in args and len(pushes) >= 4:
                file_a, count, size, ptr = pushes[-4:]
                out.append({
                    "at": addr, "ptr": ptr[1], "ptr_raw": ptr[0],
                    "size": size[1], "count": count[1], "file": file_a[0],
                })
            pushes = []
    return out


def literal(bs: list[dict[str, object]]) -> list[tuple[int, int]]:
    return [(b["ptr"], b["size"] * b["count"])  # type: ignore[operator]
            for b in bs if b["ptr"] is not None and b["size"] is not None and b["count"] is not None]


def main() -> int:
    failures: list[str] = []
    actual = sha256(EXE)
    if actual != EXPECTED_EXE_SHA:
        print(f"FAIL original exe sha mismatch: {actual}", file=sys.stderr)
        return 2

    save = blocks(disasm(SAVE_ENTRY, SAVE_END), FWRITE)
    load = blocks(disasm(LOAD_ENTRY, LOAD_END), FREAD)
    save_lit, load_lit = literal(save), literal(load)

    # (1) save and load must describe the same block table, in the same order.
    if save_lit != load_lit:
        failures.append("save/load literal block tables differ")

    # (2) every approved address except the unit roster must land in a block.
    coverage: dict[str, object] = {}
    for name, addr in APPROVED.items():
        hit = next(((p, n) for p, n in load_lit if p <= addr < p + n), None)
        coverage[name] = (
            {"block": f"{hit[0]:#010x}", "size": hit[1], "offset": addr - hit[0]}
            if hit else None
        )
    for name in APPROVED:
        if name == "G1_UNIT_BASE_ADDRESS":
            if coverage[name] is not None:
                failures.append("unit roster unexpectedly inside a bulk block")
        elif coverage[name] is None:
            failures.append(f"approved address not covered: {name}")

    # (3) the roster is serialized per-slot by 0x40F4B0 (save) / 0x40F4F0 (load).
    roster_save = disasm(0x40F4B0, 0x40F4F0)
    roster_load = disasm(0x40F4F0, 0x40F540)
    for label, text, callee in (("save", roster_save, FWRITE), ("load", roster_load, FREAD)):
        for needle in ("0x66b790", "0x8990c8", "0x758", "0x899a28", callee):
            if needle not in text:
                failures.append(f"roster {label} path missing {needle}")

    # (4) roster geometry: 1200 slots of 0x758 ends exactly where the bulk block starts.
    slots = (0x899A28 - 0x008990C8) // 2
    roster_end = 0x0066B790 + slots * 0x758
    if slots != 1200:
        failures.append(f"exists-array implies {slots} slots, expected 1200")
    if roster_end != 0x00892410:
        failures.append(f"roster end {roster_end:#x} != bulk block start 0x892410")

    # (5) map bounds are load-bearing: 0x42A920 reads +0x8c/+0x8e off the 0xB3DDA8 block.
    layer = disasm(0x42A920, 0x42A960)
    for needle in ("ecx+0x8e", "ecx+0x8c", "imul", FWRITE):
        if needle not in layer:
            failures.append(f"map-layer serializer missing {needle}")

    # (6) 8 player structs fit the bulk block; 16 do not (G3 boundary).
    bulk = next((p, n) for p, n in load_lit if p == 0x00892410)
    fits8 = 0x00956770 + 8 * 0x3ABC <= bulk[0] + bulk[1]
    fits16 = 0x00956770 + 16 * 0x3ABC <= bulk[0] + bulk[1]
    if not fits8 or fits16:
        failures.append(f"player-struct coverage unexpected: fits8={fits8} fits16={fits16}")

    report = {
        "exe_sha256": actual,
        "save_fwrite_calls": len(save),
        "load_fread_calls": len(load),
        "literal_blocks": len(load_lit),
        "block_table_identical": save_lit == load_lit,
        "approved_address_coverage": coverage,
        "roster": {
            "slots": slots, "stride": 0x758,
            "span": [f"{0x0066B790:#010x}", f"{roster_end:#010x}"],
            "save_fn": "0x0040f4b0", "load_fn": "0x0040f4f0",
        },
        "player_structs": {"fits_8": fits8, "fits_16": fits16,
                           "bulk_block_end": f"{bulk[0] + bulk[1]:#010x}"},
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
