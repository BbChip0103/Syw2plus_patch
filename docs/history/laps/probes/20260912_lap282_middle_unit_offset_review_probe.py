"""lap282 middle probe — independent review of the lap281 work-tier offset promotion.

Read-only. Re-derives, from a fresh `objdump` of the read-only original, every
claim lap281 recorded in `analysis/memory_maps/population_runtime_bridge_0910.md`
and in `docs/history/laps/20260912_lap281_work_unit_offsets.md`, and additionally
checks two things lap281 did NOT check: field-width exclusivity around each
offset, and whether the cited accessor addresses are real function entries.

No game, no Wine, no Xvfb, no Stage B, no writes to the original tree.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap282_middle_unit_offset_review_probe.py
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
RUNTIME_ENV = REPO / "tools" / "runtime_env.py"
DRIVER = REPO / "patches" / "population" / "runtime_driver.py"
MEMORY_MAP = REPO / "analysis" / "memory_maps" / "population_runtime_bridge_0910.md"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

UNIT_BASE, UNIT_STRIDE = 0x0066B790, 0x758
FIELDS = {
    "internal_id": (0x29C, 4, "DWORD"),
    "x": (0x2A2, 2, "WORD"),
    "y": (0x2A4, 2, "WORD"),
}
# lap281's memory map cites one address per field, but not consistently:
# 0x40F540 is a function ENTRY, while 0x40F5D0/0x40F5F0 are READ instructions
# inside functions whose entries are 0x40F5C0/0x40F5E0. Model both explicitly.
CITED_ADDRS = {"internal_id": 0x40F540, "x": 0x40F5D0, "y": 0x40F5F0}
ACCESSORS = {  # field -> (function entry, read instruction)
    "internal_id": (0x40F540, 0x40F550),
    "x": (0x40F5C0, 0x40F5D0),
    "y": (0x40F5E0, 0x40F5F0),
}
CITED_PAIRS = [(0x4069C7, 0x4069D1), (0x40815D, 0x40816B)]

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\t([0-9a-f ]+)\t(\S+)\s*(.*?)\s*$")
CALL_RE = re.compile(r"call\s+.*?0x([0-9a-f]+)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disassemble(path: Path) -> list[tuple[int, str, str]]:
    out = subprocess.run(
        ["objdump", "-D", "-Mintel", "-j", ".text", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    rows = []
    for line in out.splitlines():
        m = LINE_RE.match(line)
        if m:
            rows.append((int(m.group(1), 16), m.group(3), m.group(4)))
    return rows


def scaling_is_slot_times_stride(rows: list[tuple[int, str, str]], read_addr: int) -> bool:
    """The five instructions before the read must compute slot*235, read via *8."""
    idx = next(i for i, r in enumerate(rows) if r[0] == read_addr)
    window = [f"{op} {args}" for _, op, args in rows[max(0, idx - 5):idx]]
    wanted = ["lea eax,[ecx+ecx*2]", "shl eax,0x4", "sub eax,ecx", "lea eax,[eax+eax*4]"]
    return all(w in window for w in wanted)


def main() -> int:
    failures: list[str] = []
    record: dict[str, object] = {}

    actual_sha = sha256(EXE)
    record["original_exe_sha256"] = actual_sha
    if actual_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {actual_sha}")
        print(json.dumps({"failures": failures}, indent=2))
        return 1

    rows = disassemble(EXE)
    by_addr = {addr: (op, args) for addr, op, args in rows}
    record["text_instructions"] = len(rows)

    env_src = RUNTIME_ENV.read_text()
    driver_src = DRIVER.read_text()
    doc_src = MEMORY_MAP.read_text()

    # --- C2/C3: constants defined centrally and consumed by the driver -------
    consts = {"internal_id": "G1_UNIT_INTERNAL_ID_OFFSET",
              "x": "G1_UNIT_X_OFFSET", "y": "G1_UNIT_Y_OFFSET"}
    for field, (off, _w, _p) in FIELDS.items():
        name = consts[field]
        if f"\n{name} = 0x{off:X}\n" not in env_src:
            failures.append(f"{name} not defined as 0x{off:X} in tools/runtime_env.py")
        if f"                    {name},\n" not in driver_src.replace("\r", ""):
            if f"{name}," not in driver_src:
                failures.append(f"{name} not imported by runtime_driver.py")
        if f"({name})" not in driver_src:
            failures.append(f"{name} not used as a reader offset in runtime_driver.py")
    for literal in ("0x29C", "0x2A2", "0x2A4", "0x29c", "0x2a2", "0x2a4"):
        if literal in driver_src:
            failures.append(f"magic literal {literal} still present in runtime_driver.py")

    # --- C4: slot-0 absolute addresses --------------------------------------
    abs_addr = {f: UNIT_BASE + off for f, (off, _w, _p) in FIELDS.items()}
    record["slot0_absolute"] = {f: f"0x{a:X}" for f, a in abs_addr.items()}
    for f, expected in (("internal_id", 0x66BA2C), ("x", 0x66BA32), ("y", 0x66BA34)):
        if abs_addr[f] != expected:
            failures.append(f"{f} slot-0 address 0x{abs_addr[f]:X} != 0x{expected:X}")

    # --- C5/C6: read sites, widths, and slot*0x758 scaling -------------------
    record["read_sites"] = {}
    for field, (_entry, read_addr) in ACCESSORS.items():
        want_ptr = FIELDS[field][2]
        want_hex = f"0x{abs_addr[field]:x}"
        if read_addr not in by_addr:
            failures.append(f"{field}: no instruction at 0x{read_addr:X}")
            continue
        op, args = by_addr[read_addr]
        ok_ptr = f"{want_ptr} PTR" in args and want_hex in args
        ok_scale = "*8+" in args and scaling_is_slot_times_stride(rows, read_addr)
        record["read_sites"][field] = {
            "read_at": f"0x{read_addr:X}", "insn": f"{op} {args}",
            "width_ok": ok_ptr, "slot_stride_ok": ok_scale,
        }
        if not ok_ptr:
            failures.append(f"{field}: 0x{read_addr:X} does not read {want_ptr} {want_hex}")
        if not ok_scale:
            failures.append(f"{field}: 0x{read_addr:X} index scaling is not slot*0x{UNIT_STRIDE:X}")

    # --- C11: are the cited addresses real function entries? ----------------
    calls: dict[int, int] = {}
    for _addr, op, args in rows:
        if op.startswith("call"):
            m = CALL_RE.search(f"{op} {args}")
            if m:
                t = int(m.group(1), 16)
                calls[t] = calls.get(t, 0) + 1
    record["entry_check"] = {}
    for field, (entry, read_addr) in ACCESSORS.items():
        cited = CITED_ADDRS[field]
        record["entry_check"][field] = {
            "cited_in_memory_map": f"0x{cited:X}",
            "callers_of_cited": calls.get(cited, 0),
            "function_entry": f"0x{entry:X}",
            "callers_of_entry": calls.get(entry, 0),
            "read_instruction": f"0x{read_addr:X}",
            "cited_addr_is_the_entry": cited == entry,
        }
        if calls.get(entry, 0) == 0:
            failures.append(f"{field}: claimed entry 0x{entry:X} has no call sites")
    record["memory_map_cites_entry_uniformly"] = all(
        v["cited_addr_is_the_entry"] for v in record["entry_check"].values()
    )

    # --- C7: paired reference counts ----------------------------------------
    counts = {}
    for field in ("x", "y"):
        want = f"0x{abs_addr[field]:x}"
        counts[field] = sum(1 for _a, _o, args in rows if want in args)
    record["reference_counts"] = counts
    if counts["x"] != counts["y"]:
        failures.append(f"x/y reference counts differ: {counts}")
    if counts["x"] != 115:
        failures.append(f"x reference count {counts['x']} != recorded 115")

    # --- C8: width exclusivity (no sub-field access inside any field) -------
    occupied = {}
    for field, (off, width, _p) in FIELDS.items():
        for b in range(1, width):
            occupied[UNIT_BASE + off + b] = field
    intrusions = []
    for _a, _o, args in rows:
        for addr, field in occupied.items():
            if f"0x{addr:x}" in args:
                intrusions.append({"field": field, "addr": f"0x{addr:X}", "insn": args})
    record["interior_byte_references"] = intrusions
    if intrusions:
        failures.append(f"interior byte access splits a declared field: {intrusions}")

    # --- C8b: internal_id is always read 4 bytes wide -----------------------
    id_hex = f"0x{abs_addr['internal_id']:x}"
    widths = {}
    for _a, _o, args in rows:
        if id_hex in args:
            m = re.search(r"(BYTE|WORD|DWORD|QWORD) PTR", args)
            key = m.group(1) if m else "none"
            widths[key] = widths.get(key, 0) + 1
    record["internal_id_widths"] = widths
    if set(widths) != {"DWORD"}:
        failures.append(f"internal_id referenced at non-DWORD widths: {widths}")

    # --- C9: signed reads justify the driver's signed struct codes ----------
    signed = {}
    for field in ("x", "y"):
        want = f"0x{abs_addr[field]:x}"
        signed[field] = sum(1 for _a, op, args in rows if want in args and op == "movsx")
    record["movsx_reads"] = signed
    for field in ("x", "y"):
        if signed[field] == 0:
            failures.append(f"{field}: no movsx read found; signed '<h' decode unjustified")

    # --- C10: representative paired reads ------------------------------------
    pairs = []
    for a, b in CITED_PAIRS:
        ia, ib = by_addr.get(a), by_addr.get(b)
        fields = set()
        for insn in (ia, ib):
            if insn:
                for field in ("x", "y"):
                    if f"0x{abs_addr[field]:x}" in insn[1]:
                        fields.add(field)
        pairs.append({"addrs": [f"0x{a:X}", f"0x{b:X}"], "fields": sorted(fields)})
        if fields != {"x", "y"}:
            failures.append(f"cited pair 0x{a:X}/0x{b:X} is not an x/y pair: {sorted(fields)}")
    record["cited_pairs"] = pairs

    # --- doc consistency ------------------------------------------------------
    for field, (off, _w, _p) in FIELDS.items():
        if f"+0x{off:X}" not in doc_src:
            failures.append(f"memory map does not cite +0x{off:X} for {field}")

    record["failures"] = failures
    print(json.dumps(record, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
