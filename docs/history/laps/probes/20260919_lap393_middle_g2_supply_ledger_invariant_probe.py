#!/usr/bin/env python3
"""lap393 middle — the supply ledger (+0x200C) global-sum invariant, from bytes.

Read-only static probe over the pinned original EXE. It answers the two
questions lap392 (Astra) escalated, and one the escalation did not ask but
that decides them both:

  Q1  Is lap391's V2 ("per-owner roster minimum > 0 at every sample, therefore
      FUN_00444EF0 mass-absorption cannot have fired between samples") a valid
      invariant?  ->  Requires FUN_00444EF0 to be defeat-triggered. Tested here.

  Q2  Is "stock cap 1500 => global used sum <= 12000 => wrap unreachable" an
      invariant, or only an arithmetic example?  ->  Requires that the ledger
      has exactly one adding writer and one subtracting writer, that the two
      derive the same cost for the same unit, and that production is gated by
      used+cost<=cap. All three tested here.

  Q3  What uniform 8-owner cap is the *largest* one compatible with a 16-bit
      SIGNED ledger?  ->  Follows from Q2 once the invariant holds.

Nothing is read out of a decompiler listing or a prior lap's artifact; the
Ghidra names are used only to choose which addresses to disassemble. Every
claim below is re-derived from the pinned bytes in this process.

rc0 with failures==[] means every assertion held.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, CS_OP_MEM, Cs

ORIGINAL_EXE = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus/syw2plus_original.exe"
)
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

OFF_ROSTER_COUNT = 0x200A
OFF_SUPPLY_USED = 0x200C
OFF_UNIT_CAP = 0x2010
OFF_SUPPLY_CAP = 0x2012

ROSTER_ADD_VA = 0x0043EE30
ROSTER_DEL_VA = 0x0043EEC0
SPAWN_GATE_VA = 0x0043EDA0
MASS_XFER_VA = 0x00444EF0
UNIT_REGISTER_VA = 0x0048BC00  # the one non-transfer roster_add caller's entry

# Stock cap immediates that patches/population/fixed_supply_5000.py rewrites.
# Transcribed by hand from that file so this probe does not import it.
CAP_SITES = (
    (0x0003FFD4, bytes.fromhex("05dc050000")),  # add eax, 0x5DC
    (0x0001B576, bytes.fromhex("66c700dc05")),  # mov word ptr [eax], 0x5DC
)

SIGNED16_MAX = 32767
OWNERS = 8

failures: list[str] = []
notes: dict[str, object] = {}


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


def load_sections(blob: bytes) -> list[dict]:
    pe = struct.unpack_from("<I", blob, 0x3C)[0]
    if blob[pe : pe + 4] != b"PE\0\0":
        raise ValueError("not a PE image")
    n = struct.unpack_from("<H", blob, pe + 6)[0]
    opt = struct.unpack_from("<H", blob, pe + 20)[0]
    base = struct.unpack_from("<I", blob, pe + 24 + 28)[0]
    tab = pe + 24 + opt
    out = []
    for i in range(n):
        e = tab + i * 40
        name = blob[e : e + 8].rstrip(b"\0").decode("ascii", "replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", blob, e + 8)
        out.append(
            {"name": name, "va": base + va, "vsize": vs, "raw": rp, "rawsize": rs}
        )
    return out


def va_to_off(sections: list[dict], va: int) -> int | None:
    for s in sections:
        if s["va"] <= va < s["va"] + max(s["vsize"], s["rawsize"]):
            d = va - s["va"]
            if d < s["rawsize"]:
                return s["raw"] + d
    return None


def disasm_function(md: Cs, blob: bytes, sections, va: int, limit: int = 800):
    off = va_to_off(sections, va)
    body = blob[off : off + limit * 16]
    out, furthest = [], va
    for ins in md.disasm(body, va):
        out.append(ins)
        if ins.mnemonic.startswith("j") and ins.op_str.startswith("0x"):
            tgt = int(ins.op_str, 16)
            if tgt > furthest:
                furthest = tgt
        if ins.mnemonic in ("ret", "retn") and ins.address >= furthest:
            break
        if len(out) >= limit:
            break
    return out


def find_direct_callers(blob: bytes, sections, target: int) -> list[int]:
    hits = []
    for s in sections:
        if s["name"] not in (".text", "CODE"):
            continue
        data = blob[s["raw"] : s["raw"] + s["rawsize"]]
        idx = 0
        while True:
            idx = data.find(b"\xe8", idx)
            if idx < 0 or idx + 5 > len(data):
                break
            rel = struct.unpack_from("<i", data, idx + 1)[0]
            if s["va"] + idx + 5 + rel == target:
                hits.append(s["va"] + idx)
            idx += 1
    return hits


def txt(i) -> str:
    return f"{i.address:08x}  {i.mnemonic} {i.op_str}".rstrip()


def main() -> int:
    actual = hashlib.sha256(ORIGINAL_EXE.read_bytes()).hexdigest()
    if actual != ORIGINAL_SHA256:
        print(json.dumps({"failures": ["original SHA mismatch"], "sha": actual}))
        return 1
    notes["original_sha256"] = actual

    blob = ORIGINAL_EXE.read_bytes()
    sections = load_sections(blob)
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    md.detail = True
    text = next(s for s in sections if s["name"] == ".text")
    data = blob[text["raw"] : text["raw"] + text["rawsize"]]

    # ---- P1: exhaustive .text sweep for every PlayerStruct supply field ----
    # Linear sweep with resync. P2 below bounds what the resync could hide.
    wanted = {OFF_ROSTER_COUNT, OFF_SUPPLY_USED, OFF_UNIT_CAP, OFF_SUPPLY_CAP}
    refs: dict[int, list[tuple[int, str, str, str]]] = {d: [] for d in wanted}
    pos, decoded, skips = 0, 0, []
    while pos < len(data):
        got = False
        for ins in md.disasm(data[pos:], text["va"] + pos):
            got = True
            decoded += 1
            for op in ins.operands:
                if op.type == CS_OP_MEM and op.mem.base != 0 and op.mem.disp in wanted:
                    dst = ins.op_str.split(",")[0].strip()
                    kind = "W" if dst.endswith("]") else "R"
                    refs[op.mem.disp].append((ins.address, ins.mnemonic, ins.op_str, kind))
                    break
            pos = ins.address - text["va"] + ins.size
        if not got:
            skips.append(text["va"] + pos)
            pos += 1
    notes["text_sweep"] = {
        "insns_decoded": decoded,
        "resync_skips": len(skips),
        "resync_skip_vas": [hex(v) for v in skips],
    }
    for d in sorted(wanted):
        notes[f"refs_{hex(d)}"] = [f"[{k}] {a:08x} {m} {o}" for a, m, o, k in refs[d]]

    used = refs[OFF_SUPPLY_USED]
    check(len(used) == 5, f"P1: expected 5 refs to +0x200C, got {len(used)}")
    writers = [r for r in used if r[3] == "W"]
    readers = [r for r in used if r[3] == "R"]
    check(len(writers) == 2, f"P1: expected exactly 2 ledger writers, got {len(writers)}")
    check(len(readers) == 3, f"P1: expected exactly 3 ledger readers, got {len(readers)}")
    wmap = {a: (m, o) for a, m, o, _ in writers}
    check(
        0x0043EE9B in wmap and wmap[0x0043EE9B][0] == "add",
        "P1: the adding writer is not `add` at 0x43EE9B",
    )
    check(
        0x0043EF8B in wmap and wmap[0x0043EF8B][0] == "sub",
        "P1: the subtracting writer is not `sub` at 0x43EF8B",
    )
    for a, m, o, _ in writers:
        check("word ptr" in o, f"P1: ledger write at {a:#x} is not 16-bit: {m} {o}")
    for a, m, o, _ in readers:
        check(m == "movsx", f"P1: ledger read at {a:#x} is not sign-extended: {m} {o}")
    check(
        0x0043EE9B in wmap and wmap[0x0043EE9B][1].endswith(", dx"),
        "P1: adding writer does not add register dx",
    )
    check(
        0x0043EF8B in wmap and wmap[0x0043EF8B][1].endswith(", dx"),
        "P1: subtracting writer does not subtract register dx",
    )

    # ---- P2: what could the resync have hidden? --------------------------
    window = b""
    for v in skips:
        o = v - text["va"]
        window += data[max(0, o - 8) : o + 8]
    for d in sorted(wanted):
        check(
            struct.pack("<I", d) not in window,
            f"P2: displacement {hex(d)} byte-pattern occurs inside a resync window",
        )
    notes["p2_resync_windows_clean"] = True

    # ---- P3: do the two writers derive the SAME cost for the same unit? ---
    # Both tails must (a) scale the unit id by the 1880-byte UnitStruct stride,
    # (b) load the unit's type byte from the same table, (c) index the same
    # cost table with the same 916-byte stride. Register pops are interleaved
    # differently, so compare the arithmetic skeleton, not raw bytes.
    def cost_skeleton(insns, lo: int, hi: int) -> list[str]:
        out = []
        for i in insns:
            if not (lo <= i.address <= hi):
                continue
            if i.mnemonic in ("pop", "push", "dec", "inc", "ret"):
                continue
            if i.mnemonic in ("add", "sub") and hex(OFF_SUPPLY_USED) in i.op_str:
                continue
            out.append(f"{i.mnemonic} {i.op_str}")
        return out

    add_fn = disasm_function(md, blob, sections, ROSTER_ADD_VA)
    del_fn = disasm_function(md, blob, sections, ROSTER_DEL_VA)
    add_sk = cost_skeleton(add_fn, 0x0043EE6D, 0x0043EE9B)
    del_sk = cost_skeleton(del_fn, 0x0043EF55, 0x0043EF8B)
    # The seed differs only in which register holds the unit id (ax vs di).
    add_norm = [s.replace("movsx edx, ax", "movsx edx, ID") for s in add_sk]
    del_norm = [s.replace("movsx edx, di", "movsx edx, ID") for s in del_sk]
    notes["cost_skeleton_add"] = add_norm
    notes["cost_skeleton_sub"] = del_norm
    check(
        add_norm == del_norm,
        "P3: add-path and sub-path cost derivations differ:\n"
        f"  add={add_norm}\n  sub={del_norm}",
    )
    joined = " ".join(add_norm)
    check("0x66b81d" in joined, "P3: cost path does not read the unit type table 0x66b81d")
    check("0x9b5238" in joined, "P3: cost path does not index the cost table 0x9b5238")
    notes["p3_conclusion"] = (
        "roster_del(unit) then roster_add(unit) subtract and add the identical "
        "value, so any ownership transfer conserves the global sum of +0x200C "
        "exactly -- provided the unit's type byte is unchanged in between."
    )

    # ---- P4: production is gated by used + cost <= cap, both sign-extended -
    gate = disasm_function(md, blob, sections, SPAWN_GATE_VA)
    gate_txt = [txt(i) for i in gate]
    notes["spawn_gate_listing"] = gate_txt
    seq = [(i.address, i.mnemonic, i.op_str) for i in gate]
    have_used = any(
        a == 0x0043EDFC and m == "movsx" and hex(OFF_SUPPLY_USED) in o for a, m, o in seq
    )
    have_cap = any(
        a == 0x0043EE03 and m == "movsx" and hex(OFF_SUPPLY_CAP) in o for a, m, o in seq
    )
    have_add = any(a == 0x0043EE0D and m == "add" and o == "edx, eax" for a, m, o in seq)
    have_cmp = any(a == 0x0043EE0F and m == "cmp" and o == "edx, ecx" for a, m, o in seq)
    have_jle = any(a == 0x0043EE11 and m == "jle" for a, m, o in seq)
    have_deny = any(a == 0x0043EE13 and m == "xor" and o == "ax, ax" for a, m, o in seq)
    check(have_used, "P4: gate does not sign-extend +0x200C at 0x43EDFC")
    check(have_cap, "P4: gate does not sign-extend +0x2012 at 0x43EE03")
    check(have_add, "P4: gate does not compute used+cost at 0x43EE0D")
    check(have_cmp, "P4: gate does not compare used+cost against cap at 0x43EE0F")
    check(have_jle, "P4: gate's admit branch at 0x43EE11 is not `jle`")
    check(have_deny, "P4: gate's deny arm at 0x43EE13 does not return 0")
    notes["p4_conclusion"] = (
        "admission is `used + cost <= cap`, so a production-path add can never "
        "leave used above cap. Per-owner used exceeds cap only via the transfer "
        "path, which holds the global sum constant (P3)."
    )

    # ---- P5: roster_add's own admission is a roster-count bound, not a cap --
    add_head = [i for i in add_fn if i.address < 0x0043EE57]
    notes["roster_add_head"] = [txt(i) for i in add_head]
    head = [(i.address, i.mnemonic, i.op_str) for i in add_head]
    check(
        any(a == 0x0043EE30 and hex(OFF_ROSTER_COUNT) in o for a, m, o in head),
        "P5: roster_add does not open by loading the roster count",
    )
    check(
        any(a == 0x0043EE37 and m == "cmp" and o.strip() == "ax, 0x4b0" for a, m, o in head),
        "P5: roster_add admission is not `cmp ax, 0x4B0`",
    )
    overflow = [i for i in add_fn if 0x0043EE3D <= i.address <= 0x0043EE54]
    check(
        not any(hex(OFF_SUPPLY_USED) in i.op_str for i in overflow),
        "P5: the roster-overflow arm touches the ledger",
    )
    # Structural cross-check: 0x4B0 is not a bare magic number. The roster array
    # is indexed [ecx + idx*4 + 0xD4A], so 0x4B0 entries * 4 bytes end exactly at
    # the count field 0x200A -- the bound is the array's own capacity.
    roster_array_base = 0x0D4A
    check(
        any(
            "0xd4a]" in i.op_str and "*4" in i.op_str
            for i in add_fn
            if i.mnemonic == "mov"
        ),
        "P5: roster_add does not index a 4-byte-stride array at +0xD4A",
    )
    check(
        roster_array_base + 0x4B0 * 4 == OFF_ROSTER_COUNT,
        f"P5: {hex(roster_array_base)} + 0x4B0*4 != {hex(OFF_ROSTER_COUNT)}; "
        "the 1200 bound is not the roster array's capacity",
    )
    notes["per_owner_roster_cap"] = 0x4B0
    notes["roster_array"] = {
        "base": hex(roster_array_base),
        "entry_bytes": 4,
        "entries": 0x4B0,
        "ends_at": hex(roster_array_base + 0x4B0 * 4),
        "count_field": hex(OFF_ROSTER_COUNT),
    }

    # ---- P6: is FUN_00444EF0 defeat-triggered? (lap391 V2's premise) -------
    mass = disasm_function(md, blob, sections, MASS_XFER_VA)
    notes["mass_transfer_listing"] = [txt(i) for i in mass]
    for d in sorted(wanted):
        offenders = [txt(i) for i in mass if hex(d) in i.op_str]
        check(
            not offenders,
            f"P6: FUN_00444EF0 references {hex(d)} (would make it supply-aware): {offenders}",
        )
    mass_callers = find_direct_callers(blob, sections, MASS_XFER_VA)
    notes["mass_transfer_direct_callers"] = [hex(v) for v in mass_callers]
    check(len(mass_callers) == 8, f"P6: expected 8 callers of 0x444EF0, got {len(mass_callers)}")
    # Every caller must push a *constant* source owner (or the local-player
    # global) - i.e. the source is chosen by the script, never derived from a
    # defeat test on roster/supply.
    caller_args = []
    for site in mass_callers:
        # Decode the window preceding the call, choosing the start offset whose
        # instruction stream lands exactly on the call site. A window that
        # merely starts N bytes back can desynchronise and silently yield no
        # pushes, which would make the check below vacuous.
        pre: list = []
        for back in range(0x20, 0x80):
            o = va_to_off(sections, site - back)
            cand = list(md.disasm(blob[o : o + back + 8], site - back))
            if any(i.address == site for i in cand):
                pre = [i for i in cand if i.address < site]
                break
        check(bool(pre), f"P6: could not decode a synchronised window before {site:#x}")
        pushes = [i for i in pre if i.mnemonic == "push"][-2:]
        caller_args.append({"call_site": hex(site), "pushes": [txt(i) for i in pushes]})
        check(
            len(pushes) == 2,
            f"P6: fewer than 2 pushes precede the call at {site:#x}",
        )
        # cdecl pushes right-to-left, so the LAST push is arg1 -- the source
        # owner whose whole roster is handed away. It must be either a literal
        # owner id or the local-player global 0xB63FC4, never a value computed
        # from a defeat test.
        src = pushes[-1]
        src_is_imm = src.op_str.startswith("0x") or src.op_str.isdigit()
        src_reg = src.op_str.strip()
        src_from_local_player = any(
            "0xb63fc4" in i.op_str
            and i.op_str.split(",")[0].strip() in (src_reg, src_reg.replace("e", "", 1))
            for i in pre
        )
        check(
            src_is_imm or src_from_local_player,
            f"P6: source-owner argument at {site:#x} is neither an immediate nor "
            f"the local-player global: {txt(src)}",
        )
        caller_args[-1]["source_owner"] = (
            f"imm {src.op_str}" if src_is_imm else f"{src_reg} <- word[0xB63FC4]"
        )
        roster_derived = [
            txt(i)
            for i in pre
            if hex(OFF_ROSTER_COUNT) in i.op_str or hex(OFF_SUPPLY_USED) in i.op_str
        ]
        check(
            not roster_derived,
            f"P6: caller {site:#x} derives an argument from roster/supply: {roster_derived}",
        )
    notes["mass_transfer_caller_args"] = caller_args
    in_script_region = [v for v in mass_callers if 0x004BE000 <= v < 0x004C2000]
    check(
        len(in_script_region) == len(mass_callers),
        "P6: some 0x444EF0 caller lives outside the 0x4BE000-0x4C2000 script region",
    )
    notes["p6_conclusion"] = (
        "FUN_00444EF0 is a slot-loop that reassigns every unit of owner `arg1` "
        "to owner `arg2`; it contains no roster, supply or defeat test, and all "
        "8 call sites are in one 0x4BE000-0x4C2000 region that pushes hardcoded "
        "owner ids (4/6/7) or the local-player global 0xB63FC4. It is scripted "
        "mission logic, NOT a defeat handler. lap391's V2 inference "
        "('no owner hit roster 0, therefore 0x444EF0 cannot have fired') "
        "rests on a premise the bytes do not support."
    )

    # ---- P7: the one non-transfer roster_add caller is narrow -------------
    add_callers = find_direct_callers(blob, sections, ROSTER_ADD_VA)
    del_callers = find_direct_callers(blob, sections, ROSTER_DEL_VA)
    notes["roster_add_direct_callers"] = [hex(v) for v in add_callers]
    notes["roster_del_direct_callers"] = [hex(v) for v in del_callers]
    reg_callers = find_direct_callers(blob, sections, UNIT_REGISTER_VA)
    notes["unit_register_entry"] = hex(UNIT_REGISTER_VA)
    notes["unit_register_direct_callers"] = [hex(v) for v in reg_callers]
    abs_refs = []
    idx = 0
    pat = struct.pack("<I", UNIT_REGISTER_VA)
    while True:
        idx = blob.find(pat, idx)
        if idx < 0:
            break
        abs_refs.append(hex(idx))
        idx += 1
    notes["unit_register_absolute_dword_refs"] = abs_refs
    check(
        not abs_refs,
        f"P7: 0x48BC00 is referenced as an absolute dword (indirect dispatch): {abs_refs}",
    )

    # ---- P8: the stock cap immediates, as the 5000 patch finds them -------
    for foff, want in CAP_SITES:
        got = blob[foff : foff + len(want)]
        check(
            got == want,
            f"P8: stock cap immediate at file {foff:#x} is {got.hex()}, expected {want.hex()}",
        )
    notes["stock_cap_immediate_sites"] = [
        {"file_offset": hex(f), "va": hex(0x00400000 + f), "bytes": w.hex()}
        for f, w in CAP_SITES
    ]
    notes["stock_cap_immediate_value"] = 0x5DC

    # ---- P9: the invariant, and the largest ledger-safe uniform cap -------
    safe_cap = SIGNED16_MAX // OWNERS
    check(OWNERS * safe_cap <= SIGNED16_MAX, "P9: safe-cap arithmetic is wrong")
    check(OWNERS * (safe_cap + 1) > SIGNED16_MAX, "P9: safe cap is not maximal")
    notes["invariant"] = (
        "Let U_o = word[PlayerStruct_o + 0x200C]. P1 shows the only mutations of "
        "U are +cost at 0x43EE9B and -cost at 0x43EF8B; P3 shows a transfer "
        "pairs them on the same unit with the identical cost, so transfers hold "
        "SUM(U_o) constant; P4 shows production admits only while U_o + cost <= "
        "cap_o, so production leaves U_o <= cap_o. Therefore at every instant "
        "SUM(U_o) <= SUM(cap_o), and since every U_o >= 0 under this scheme, "
        "max_o U_o <= SUM(cap_o). A signed-16 wrap needs some U_o > 32767."
    )
    notes["ledger_signed16_max"] = SIGNED16_MAX
    notes["owners"] = OWNERS
    notes["max_ledger_safe_uniform_cap_8_owners"] = safe_cap
    notes["bound_at_stock_1500"] = OWNERS * 1500
    notes["bound_at_target_5000"] = OWNERS * 5000
    notes["wrap_possible_at_stock_1500"] = OWNERS * 1500 > SIGNED16_MAX
    notes["wrap_possible_at_target_5000"] = OWNERS * 5000 > SIGNED16_MAX
    notes["concentration_share_needed_at_5000"] = round(
        SIGNED16_MAX / (OWNERS * 5000), 4
    )
    check(
        OWNERS * 1500 <= SIGNED16_MAX,
        "P9: the stock-1500 bound does not clear the signed-16 ceiling",
    )
    check(
        OWNERS * 5000 > SIGNED16_MAX,
        "P9: the target-5000 bound unexpectedly clears the signed-16 ceiling",
    )

    notes["fail_open"] = [
        "FO-1 P3 assumes the unit's type byte at 0x66B81D+1880*id is unchanged "
        "between the paired roster_del and roster_add. A type-changing transform "
        "spanning that pair would break exact conservation. Not traced here.",
        "FO-2 the cost table at 0x9B5238 lies past .data's raw size (runtime "
        "populated), so the maximum single-unit cost cannot be read statically. "
        "The invariant does not need it; a per-owner-roster*max_cost bound would.",
        "FO-3 save/load restores +0x200C through the bulk blob, outside the two "
        "writers. The invariant covers running play, not a crafted save.",
        "FO-4 the gate at 0x43EDA0 and the registration at 0x48BC00 are separate "
        "calls; this probe does not prove every production caller runs the gate "
        "immediately before registering (TOCTOU window unmeasured).",
        "FO-5 stock cap is `<base> + 0x5DC`, base = dword[esp+0x18] at 0x43FFD0. "
        "base is not resolved statically, so `stock == 1500` is asserted only "
        "for base == 0; the 5000 patch replaces the whole expression with a "
        "constant, which is what the 9/19 fixture ran.",
    ]

    out = {
        "probe": "lap393_middle_g2_supply_ledger_invariant",
        "failures": failures,
        **notes,
    }
    print(json.dumps(out, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
