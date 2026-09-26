#!/usr/bin/env python3
"""lap389 middle probe — owner transfer (0x476ED0) vs supply cap (+0x2012).

Read-only static probe over the pinned original EXE. It answers four narrow
questions at *original instruction boundaries* (no decompiler trust):

  Q1  Does FUN_00476ED0 have any comparison against the player supply cap
      field (+0x2012) or any non-constant return value?
  Q2  Where is the used-supply field (+0x200C) actually mutated on the
      transfer path, and what admission test guards it?
  Q3  Which call sites reach 0x476ED0 directly (E8 rel32), and does any of
      them consume the return value (test/cmp on eax/al right after)?
  Q4  Does the *spawn* admission gate (the function that does compare
      +0x2012 against +0x200C) share code with the transfer path?

Everything is derived from bytes; the Ghidra listing in the reference repo is
used only to choose which addresses to look at. Exit 0 with failures=[] means
every assertion below held.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs

ORIGINAL_EXE = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus/syw2plus_original.exe"
)
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

TRANSFER_VA = 0x00476ED0
ROSTER_ADD_VA = 0x0043EE30
ROSTER_DEL_VA = 0x0043EEC0
SPAWN_GATE_VA = 0x0043EDA0

PLAYER_BASE = 0x00956770
PLAYER_STRIDE = 0x00003ABC
OFF_RESERVE = 0x001C
OFF_ROSTER_COUNT = 0x200A
OFF_SUPPLY_USED = 0x200C
OFF_UNIT_CAP = 0x2010
OFF_SUPPLY_CAP = 0x2012


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_sections(blob: bytes) -> list[dict]:
    pe_off = struct.unpack_from("<I", blob, 0x3C)[0]
    if blob[pe_off : pe_off + 4] != b"PE\0\0":
        raise ValueError("not a PE image")
    n_sections = struct.unpack_from("<H", blob, pe_off + 6)[0]
    opt_size = struct.unpack_from("<H", blob, pe_off + 20)[0]
    image_base = struct.unpack_from("<I", blob, pe_off + 24 + 28)[0]
    table = pe_off + 24 + opt_size
    out = []
    for i in range(n_sections):
        ent = table + i * 40
        name = blob[ent : ent + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, rawsize, rawptr = struct.unpack_from("<IIII", blob, ent + 8)
        out.append(
            {
                "name": name,
                "va": image_base + vaddr,
                "vsize": vsize,
                "raw": rawptr,
                "rawsize": rawsize,
            }
        )
    return out


def va_to_off(sections: list[dict], va: int) -> int | None:
    for s in sections:
        if s["va"] <= va < s["va"] + max(s["vsize"], s["rawsize"]):
            delta = va - s["va"]
            if delta < s["rawsize"]:
                return s["raw"] + delta
    return None


def disasm(md: Cs, blob: bytes, sections: list[dict], va: int, count: int):
    off = va_to_off(sections, va)
    if off is None:
        return []
    return list(md.disasm(blob[off : off + count * 16], va, count=count))


def disasm_function(md: Cs, blob: bytes, sections: list[dict], va: int, limit=400):
    """Linear sweep from `va` until the ret that is not followed by more code
    of this function (first ret at depth 0 after the last forward jump)."""
    off = va_to_off(sections, va)
    body = blob[off : off + limit * 16]
    insns = []
    furthest = va
    for ins in md.disasm(body, va):
        insns.append(ins)
        if ins.mnemonic.startswith("j") and ins.op_str.startswith("0x"):
            try:
                tgt = int(ins.op_str, 16)
            except ValueError:
                tgt = 0
            if tgt > furthest:
                furthest = tgt
        if ins.mnemonic in ("ret", "retn") and ins.address >= furthest:
            break
        if len(insns) >= limit:
            break
    return insns


def find_direct_callers(blob: bytes, sections: list[dict], target_va: int) -> list[int]:
    """All E8 rel32 sites whose computed target equals target_va, restricted to
    executable sections. Reports the VA of the E8 byte."""
    hits = []
    for s in sections:
        if s["name"] not in (".text", "CODE"):
            continue
        data = blob[s["raw"] : s["raw"] + s["rawsize"]]
        base = s["va"]
        idx = 0
        while True:
            idx = data.find(b"\xe8", idx)
            if idx < 0 or idx + 5 > len(data):
                break
            rel = struct.unpack_from("<i", data, idx + 1)[0]
            if base + idx + 5 + rel == target_va:
                hits.append(base + idx)
            idx += 1
    return hits


def main() -> int:
    failures: list[str] = []
    notes: dict[str, object] = {}

    actual_sha = sha256(ORIGINAL_EXE)
    if actual_sha != ORIGINAL_SHA256:
        print(json.dumps({"failures": ["original SHA mismatch"], "sha": actual_sha}))
        return 1
    notes["original_sha256"] = actual_sha

    blob = ORIGINAL_EXE.read_bytes()
    sections = load_sections(blob)
    notes["sections"] = [
        {"name": s["name"], "va": hex(s["va"]), "vsize": s["vsize"]} for s in sections
    ]
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = False

    # ---- Q1: transfer function body -------------------------------------
    xfer = disasm_function(md, blob, sections, TRANSFER_VA)
    if not xfer:
        failures.append("Q1: could not disassemble 0x476ED0")
        print(json.dumps({"failures": failures}, indent=2))
        return 1
    xfer_end = xfer[-1].address + xfer[-1].size
    notes["transfer"] = {
        "va": hex(TRANSFER_VA),
        "end_va": hex(xfer_end),
        "length": xfer_end - TRANSFER_VA,
        "insn_count": len(xfer),
        "listing": [f"{i.address:08x}  {i.mnemonic} {i.op_str}".rstrip() for i in xfer],
    }

    supply_cap_refs = [
        f"{i.address:08x}  {i.mnemonic} {i.op_str}"
        for i in xfer
        if hex(OFF_SUPPLY_CAP) in i.op_str or hex(OFF_SUPPLY_USED) in i.op_str
    ]
    notes["transfer_supply_field_refs"] = supply_cap_refs
    if supply_cap_refs:
        failures.append(
            "Q1: 0x476ED0 unexpectedly references +0x200C/+0x2012 directly"
        )

    # Return value: prove the function is single-exit with a constant return.
    # Structural argument (not decompiler trust):
    #   (a) exactly one `ret` in the body, at the very end;
    #   (b) every conditional branch targets an address inside the body, so no
    #       path leaves early;
    #   (c) the instruction immediately reaching that ret writes eax = 1 and no
    #       later instruction touches eax.
    rets = [i for i in xfer if i.mnemonic in ("ret", "retn")]
    notes["transfer_ret_sites"] = [
        f"{i.address:08x}  {i.mnemonic} {i.op_str}".rstrip() for i in rets
    ]
    if len(rets) != 1:
        failures.append(f"Q1: expected a single ret in 0x476ED0, got {len(rets)}")

    conditional = [
        f"{i.address:08x}  {i.mnemonic} {i.op_str}"
        for i in xfer
        if i.mnemonic.startswith("j") and i.mnemonic != "jmp"
    ]
    notes["transfer_conditional_branches"] = conditional
    for i in xfer:
        if i.mnemonic.startswith("j") and i.op_str.startswith("0x"):
            tgt = int(i.op_str, 16)
            if not (TRANSFER_VA <= tgt < xfer_end):
                failures.append(
                    f"Q1: branch at {i.address:#x} leaves the body (-> {tgt:#x})"
                )

    tail = [i for i in xfer if i.address >= rets[0].address - 8] if rets else []
    tail_txt = [f"{i.address:08x}  {i.mnemonic} {i.op_str}".rstrip() for i in tail]
    notes["transfer_tail"] = tail_txt
    const_return = any(
        i.mnemonic == "mov" and i.op_str.replace(" ", "") == "eax,1" for i in tail
    )
    if not const_return:
        failures.append(f"Q1: no constant `mov eax, 1` in the tail: {tail_txt}")
    # nothing after that write may redefine eax
    after_const = []
    seen = False
    for i in tail:
        if seen:
            after_const.append(i)
        if i.mnemonic == "mov" and i.op_str.replace(" ", "") == "eax,1":
            seen = True
    if any("eax" in i.op_str.split(",")[0] for i in after_const):
        failures.append("Q1: eax is redefined after the constant return write")

    # calls made by the transfer function, in order
    xfer_calls = []
    for i in xfer:
        if i.mnemonic == "call" and i.op_str.startswith("0x"):
            xfer_calls.append({"site": hex(i.address), "target": i.op_str})
    notes["transfer_calls"] = xfer_calls
    targets = {c["target"] for c in xfer_calls}
    for need in (ROSTER_ADD_VA, ROSTER_DEL_VA):
        if hex(need) not in targets:
            failures.append(f"Q2: transfer does not call {hex(need)}")

    # ---- Q2: roster add/del own the +0x200C mutation --------------------
    for label, va in (("roster_add", ROSTER_ADD_VA), ("roster_del", ROSTER_DEL_VA)):
        fn = disasm_function(md, blob, sections, va)
        used_refs = [
            f"{i.address:08x}  {i.mnemonic} {i.op_str}"
            for i in fn
            if hex(OFF_SUPPLY_USED) in i.op_str
        ]
        cap_refs = [
            f"{i.address:08x}  {i.mnemonic} {i.op_str}"
            for i in fn
            if hex(OFF_SUPPLY_CAP) in i.op_str
        ]
        count_cmps = [
            f"{i.address:08x}  {i.mnemonic} {i.op_str}"
            for i in fn
            if i.mnemonic == "cmp" and hex(OFF_ROSTER_COUNT) in i.op_str
        ]
        notes[label] = {
            "va": hex(va),
            "insn_count": len(fn),
            "supply_used_refs": used_refs,
            "supply_cap_refs": cap_refs,
            "roster_count_cmps": count_cmps,
            "listing": [
                f"{i.address:08x}  {i.mnemonic} {i.op_str}".rstrip() for i in fn
            ],
        }
        if not used_refs:
            failures.append(f"Q2: {label} does not touch +0x200C")
        if cap_refs:
            failures.append(
                f"Q2: {label} unexpectedly references the supply cap +0x2012"
            )

    # ---- Q3: direct callers of the transfer -----------------------------
    callers = find_direct_callers(blob, sections, TRANSFER_VA)
    caller_detail = []
    for site in callers:
        after = disasm(md, blob, sections, site + 5, 4)
        consumes = any(
            (ins.mnemonic in ("test", "cmp") and ins.op_str.split(",")[0].strip()
             in ("eax", "al", "ax"))
            or (ins.mnemonic in ("mov", "movzx") and ins.op_str.split(",")[-1].strip()
                in ("eax", "al", "ax"))
            for ins in after[:2]
        )
        caller_detail.append(
            {
                "call_site": hex(site),
                "next": [f"{i.address:08x}  {i.mnemonic} {i.op_str}".rstrip()
                         for i in after],
                "consumes_return": consumes,
            }
        )
    notes["transfer_direct_callers"] = caller_detail
    notes["transfer_direct_caller_count"] = len(callers)
    if not callers:
        failures.append("Q3: no direct E8 caller of 0x476ED0 found")
    consumers = [c for c in caller_detail if c["consumes_return"]]
    notes["transfer_callers_consuming_return"] = [c["call_site"] for c in consumers]

    # ---- Q4: the spawn gate that *does* compare the cap ------------------
    gate = disasm_function(md, blob, sections, SPAWN_GATE_VA, limit=600)
    gate_cap_refs = [
        f"{i.address:08x}  {i.mnemonic} {i.op_str}"
        for i in gate
        if hex(OFF_SUPPLY_CAP) in i.op_str
    ]
    gate_unit_cap_refs = [
        f"{i.address:08x}  {i.mnemonic} {i.op_str}"
        for i in gate
        if hex(OFF_UNIT_CAP) in i.op_str
    ]
    notes["spawn_gate"] = {
        "va": hex(SPAWN_GATE_VA),
        "insn_count": len(gate),
        "supply_cap_refs": gate_cap_refs,
        "unit_cap_refs": gate_unit_cap_refs,
    }
    if not gate_cap_refs:
        failures.append("Q4: spawn gate 0x43EDA0 has no +0x2012 comparison")
    gate_callers = find_direct_callers(blob, sections, SPAWN_GATE_VA)
    notes["spawn_gate_direct_caller_count"] = len(gate_callers)
    notes["spawn_gate_direct_callers"] = [hex(v) for v in gate_callers]
    if TRANSFER_VA <= (min(gate_callers) if gate_callers else 0) < xfer_end:
        failures.append("Q4: transfer calls the spawn gate (unexpected sharing)")
    if any(TRANSFER_VA <= v < xfer_end for v in gate_callers):
        failures.append("Q4: spawn gate is called from inside the transfer body")

    # ---- Q5: ledger width/signedness of +0x200C -------------------------
    # The used-supply field is a 16-bit word that is mutated with a 16-bit add
    # and read back sign-extended by the production gate. That makes the
    # reachable ledger range [-32768, 32767], which matters once 8 x cap
    # exceeds 32767.
    ledger_add = [
        i
        for i in disasm_function(md, blob, sections, ROSTER_ADD_VA)
        if hex(OFF_SUPPLY_USED) in i.op_str
    ]
    gate_used_read = [i for i in gate if hex(OFF_SUPPLY_USED) in i.op_str]
    notes["ledger_width"] = {
        "add_site": [f"{i.address:08x}  {i.mnemonic} {i.op_str}" for i in ledger_add],
        "gate_read": [f"{i.address:08x}  {i.mnemonic} {i.op_str}" for i in gate_used_read],
    }
    if not all("word ptr" in i.op_str for i in ledger_add):
        failures.append("Q5: ledger add is not a 16-bit word write")
    if not all(i.mnemonic == "movsx" for i in gate_used_read):
        failures.append("Q5: gate does not read +0x200C sign-extended")
    notes["ledger_signed_max"] = 32767
    notes["eight_owner_cap_sum_at_5000"] = 8 * 5000
    notes["ledger_overflow_headroom_at_5000"] = 32767 - 8 * 5000
    notes["ledger_overflow_headroom_at_stock_1500"] = 32767 - 8 * 1500

    # roster add/del sharing: who else registers into +0xD4A / +0x200C?
    for label, va in (("roster_add", ROSTER_ADD_VA), ("roster_del", ROSTER_DEL_VA)):
        sites = find_direct_callers(blob, sections, va)
        notes[f"{label}_direct_callers"] = [hex(v) for v in sites]
        notes[f"{label}_shared_with_non_transfer"] = [
            hex(v) for v in sites if not (TRANSFER_VA <= v < xfer_end)
        ]

    # exact old bytes of the transfer prologue (patch anchor candidate)
    off = va_to_off(sections, TRANSFER_VA)
    notes["transfer_first_16_bytes"] = blob[off : off + 16].hex()
    notes["transfer_bytes_sha256"] = hashlib.sha256(
        blob[off : off + (xfer_end - TRANSFER_VA)]
    ).hexdigest()

    result = {"probe": "lap389_owner_transfer_cap", "failures": failures, **notes}
    print(json.dumps(result, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
