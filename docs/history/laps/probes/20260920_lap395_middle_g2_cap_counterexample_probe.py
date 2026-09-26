#!/usr/bin/env python3
"""lap395 middle — independent review of lap394 (Astra) cap-invariant counterexample.

Read-only. Nothing is imported from a prior lap's probe or module; the lap393
probe is opened as TEXT only, to audit what it actually asserted.

Questions this probe answers:

  A2  Does lap393's `failures == []` constitute a proof of the global-sum
      invariant in its P9 note?  -> Audit the assertions inside the P9 block.

  A3  Is lap394's transfer-then-reproduce counterexample valid under lap393's
      own P1..P4 byte premises?  -> Re-derive it as a transition system.

  A4  Is the counterexample a one-off `+d`, or a pump?  -> Iterate it.

  A5  Which limits does a TRANSFER actually pass through, as opposed to a
      PRODUCTION?  -> Re-disassemble the gate, roster_add and roster_del.

  A6  Astra asked: is there some OTHER bound that excludes repeated
      transfer+production?  -> The roster/pool * max_unit_cost bound, tested
      against the 9/19 run's own cost evidence.

rc0 with failures == [] means every assertion held.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_X86, CS_MODE_32, Cs

ROOT = Path("/home/dev_00/sharedfolder/260320_Syw2plus")
ORIGINAL_EXE = ROOT / "Syw2plus/syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

LAP393_PROBE = (
    ROOT / "Syw2plus_patch/docs/history/laps/probes"
    / "20260919_lap393_middle_g2_supply_ledger_invariant_probe.py"
)
SAMPLES = (
    ROOT / "temp/Syw2plus_patch/g2_capacity"
    / "20260919_eight_owner_5000_stability_actual_v1/official_run1"
    / "g2_stock_24k_observation/samples.jsonl"
)
SAMPLES_SHA256 = "76903a8dcc094fa7c477ffc76048240fbca38cf78b126599a906c3a05f0e7180"

OFF_ROSTER_COUNT = 0x200A
OFF_SUPPLY_USED = 0x200C
OFF_UNIT_COUNT_CAP = 0x2010
OFF_SUPPLY_CAP = 0x2012

SPAWN_GATE_VA = 0x0043EDA0
ROSTER_ADD_VA = 0x0043EE30
ROSTER_DEL_VA = 0x0043EEC0

ROSTER_ARRAY_LIMIT = 0x4B0  # 1200, the only bound roster_add enforces
SIGNED16_MAX = 32767
OWNERS = 8

failures: list[str] = []
notes: dict[str, object] = {}


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


# --------------------------------------------------------------------------
# PE helpers (independent parse; no prior-lap layout module)
# --------------------------------------------------------------------------
def load_pe(path: Path):
    blob = path.read_bytes()
    pe = struct.unpack_from("<I", blob, 0x3C)[0]
    nsec = struct.unpack_from("<H", blob, pe + 6)[0]
    optsz = struct.unpack_from("<H", blob, pe + 20)[0]
    base = struct.unpack_from("<I", blob, pe + 24 + 28)[0]
    secs = []
    for i in range(nsec):
        o = pe + 24 + optsz + i * 40
        name = blob[o : o + 8].rstrip(b"\0").decode()
        vsize, vaddr, rsize, rptr = struct.unpack_from("<IIII", blob, o + 8)
        secs.append(
            {
                "name": name,
                "va": base + vaddr,
                "vsize": vsize,
                "rsize": rsize,
                "rptr": rptr,
            }
        )
    return blob, base, secs


def read_va(blob, secs, va: int, n: int) -> bytes:
    for s in secs:
        if s["va"] <= va < s["va"] + max(s["vsize"], s["rsize"]):
            off = va - s["va"] + s["rptr"]
            if va - s["va"] >= s["rsize"]:
                return b""  # BSS tail: no raw bytes on disk
            return blob[off : off + n]
    return b""


def in_raw_data(secs, va: int) -> bool:
    """True iff the VA has initialised bytes in the file image."""
    for s in secs:
        if s["va"] <= va < s["va"] + s["rsize"]:
            return True
    return False


def disasm(blob, secs, va: int, n: int):
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    return list(md.disasm(read_va(blob, secs, va, n), va))


def main() -> int:
    # ---- A1: pins -------------------------------------------------------
    raw = ORIGINAL_EXE.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    check(got == ORIGINAL_SHA256, f"A1: original EXE SHA {got} != pinned")
    notes["original_sha256"] = got

    blob, base, secs = load_pe(ORIGINAL_EXE)
    notes["sections"] = [
        {
            "name": s["name"],
            "va": hex(s["va"]),
            "vsize": hex(s["vsize"]),
            "raw_end_va": hex(s["va"] + s["rsize"]),
        }
        for s in secs
    ]

    # ---- A2: what did lap393's P9 block actually assert? ----------------
    src = LAP393_PROBE.read_text()
    notes["lap393_probe_sha256"] = hashlib.sha256(src.encode()).hexdigest()
    p9_start = src.index("# ---- P9:")
    p9_end = src.index('notes["fail_open"]')
    p9 = src[p9_start:p9_end]
    p9_checks = re.findall(r"check\(\s*(.+?),\s*\n", p9)
    notes["lap393_p9_assertions"] = [c.strip() for c in p9_checks]
    # Every P9 assertion is pure arithmetic over OWNERS/SIGNED16_MAX constants.
    for c in p9_checks:
        check(
            ("SIGNED16_MAX" in c or "safe_cap" in c) and "OWNERS" in c,
            f"A2: unexpected non-arithmetic P9 assertion: {c}",
        )
    # The decisive point: nowhere in the whole lap393 probe is a state
    # transition (a transfer followed by a production) evaluated.
    for token in ("used[", "transfer(", "produce(", "for _ in range"):
        check(
            token not in src,
            f"A2: lap393 probe unexpectedly simulates transitions ({token})",
        )
    notes["A2_verdict"] = (
        "lap393 P9 contains exactly "
        f"{len(p9_checks)} assertions, all of them arithmetic over "
        "SIGNED16_MAX//OWNERS. The probe never evaluates a transfer->produce "
        "transition. Its `failures == []` therefore certifies the division, "
        "NOT the invariant prose in notes['invariant']."
    )

    # ---- A3: re-derive lap394's counterexample as a transition system ----
    # Semantics taken from the bytes (see A5), not from lap393's prose:
    #   transfer(a,b,d): used[a] -= d ; used[b] += d      (no cap consulted)
    #   produce(o,d)   : allowed iff used[o] + d <= cap[o]; then used[o] += d
    def counterexample(cap: int, d: int = 1) -> dict:
        used = [cap] * OWNERS
        start_sum = sum(used)
        used[0] -= d
        used[1] += d
        transfer_sum = sum(used)
        gate_ok = used[0] + d <= cap  # production gate, owner 0
        used[0] += d
        return {
            "cap": cap,
            "start_sum": start_sum,
            "sum_after_transfer": transfer_sum,
            "production_gate_satisfied": gate_ok,
            "sum_after_reproduce": sum(used),
            "claimed_bound": OWNERS * cap,
            "max_owner_used": max(used),
        }

    a3 = [counterexample(c) for c in (1500, 4095, 5000)]
    notes["A3_counterexample"] = a3
    for row in a3:
        check(
            row["sum_after_transfer"] == row["claimed_bound"],
            f"A3: transfer failed to conserve the sum at cap {row['cap']}",
        )
        check(
            row["production_gate_satisfied"],
            f"A3: the reproduce step is not gate-legal at cap {row['cap']}",
        )
        check(
            row["sum_after_reproduce"] == row["claimed_bound"] + 1,
            f"A3: reproduce did not exceed SUM(cap) at cap {row['cap']}",
        )
    # lap394 published these three totals; reproduce them exactly.
    check(
        [r["sum_after_reproduce"] for r in a3] == [12001, 32761, 40001],
        "A3: lap394's published totals 12001/32761/40001 not reproduced",
    )

    # ---- A4: the counterexample is a PUMP, not a one-off ----------------
    def pump(cap: int, cost: float, roster_limit: int, pool: int) -> dict:
        """Drain every donor into owner 1, letting donors re-produce.

        Ledgers start self-consistent: an owner holding `n` units of mean
        cost `cost` carries `n * cost` supply, and the stock steady state is
        as many units as its cap affords. Each cycle:

          1. a donor hands one unit to owner 1  (roster_del + roster_add:
             no cap and no count_cap consulted - see A5), and
          2. that donor re-produces one unit if the production gate allows
             it (used + cost <= cap) and the global unit pool has a slot.

        Owner 1 is never the producer, so it never meets the gate. Its
        ledger is bounded only by its roster array and the unit pool.
        """
        steady = min(int(cap // cost), pool // OWNERS)
        roster = [steady] * OWNERS
        used = [r * cost for r in roster]
        world = sum(roster)
        cycles = 0
        produced = 0
        # at most one pass over every slot the pool can ever hold
        while roster[1] < roster_limit and used[1] <= SIGNED16_MAX:
            donor = next(
                (o for o in range(OWNERS) if o != 1 and roster[o] > 0), None
            )
            if donor is None:
                break
            used[donor] -= cost
            roster[donor] -= 1
            used[1] += cost
            roster[1] += 1
            cycles += 1
            # the donor refills, strictly through the gate
            if world < pool and used[donor] + cost <= cap:
                used[donor] += cost
                roster[donor] += 1
                world += 1
                produced += 1
        return {
            "cap": cap,
            "unit_cost": cost,
            "roster_limit": roster_limit,
            "unit_pool": pool,
            "start_units_per_owner": steady,
            "transfers": cycles,
            "gate_legal_productions": produced,
            "receiver_units": roster[1],
            "receiver_used": round(used[1], 1),
            "global_sum": round(sum(used), 1),
            "claimed_bound_sum_cap": OWNERS * cap,
            "wrapped_signed16": used[1] > SIGNED16_MAX,
        }

    # Use the run's own cheapest observed per-owner mean cost (most
    # conservative: a cheaper unit puts LESS supply on each roster slot).
    # Unit pool 1199 is the figure STATUS carries (observed peak 1176).
    observed_min_mean_cost = 29.43  # owner 1, final sample: 5003/170
    a4 = [
        pump(cap, cost=observed_min_mean_cost, roster_limit=ROSTER_ARRAY_LIMIT, pool=1199)
        for cap in (1500, 4095, 5000)
    ]
    notes["A4_pump"] = a4
    for row in a4:
        # SUM(cap) is only the binding ceiling while the world is cap-limited.
        # At cap 5000 the 1199-slot unit pool binds first (steady state
        # 149 < 5000/29.43), so total supply legitimately stays below
        # 8*cap there; the minimal A3 counterexample already shows the
        # SUM(cap) break directly.
        cap_bound_regime = row["start_units_per_owner"] < row["cap"] // row["unit_cost"]
        if not cap_bound_regime:
            check(
                row["global_sum"] > row["claimed_bound_sum_cap"],
                f"A4: pump did not break SUM(cap) at cap {row['cap']}",
            )
        check(
            row["wrapped_signed16"],
            f"A4: pump did not reach the signed-16 ceiling at cap {row['cap']} "
            f"(receiver_used={row['receiver_used']})",
        )
    notes["A4_verdict"] = (
        "The receiver's ledger is bounded by its ROSTER and the unit pool, "
        "NOT by SUM(cap). At the run's own cheapest observed unit cost the "
        "pump crosses 32767 at every cap tested - including the stock 1500 "
        "and the proposed-safe 4095. The caps differ only in how much work "
        "it takes: cap 5000 needs 7 extra productions, stock 1500 needs 799."
    )

    # ---- A5: which limits does each path actually enforce? --------------
    gate = disasm(blob, secs, SPAWN_GATE_VA, 0x80)
    gate_txt = "\n".join(f"{i.mnemonic} {i.op_str}" for i in gate)
    add = disasm(blob, secs, ROSTER_ADD_VA, 0x90)
    add_txt = "\n".join(f"{i.mnemonic} {i.op_str}" for i in add)
    dele = disasm(blob, secs, ROSTER_DEL_VA, 0xF0)
    del_txt = "\n".join(f"{i.mnemonic} {i.op_str}" for i in dele)

    def refs(text: str, off: int) -> int:
        return len(re.findall(rf"0x{off:x}\b", text))

    gate_refs = {
        "roster_count_0x200a": refs(gate_txt, OFF_ROSTER_COUNT),
        "supply_used_0x200c": refs(gate_txt, OFF_SUPPLY_USED),
        "unit_count_cap_0x2010": refs(gate_txt, OFF_UNIT_COUNT_CAP),
        "supply_cap_0x2012": refs(gate_txt, OFF_SUPPLY_CAP),
    }
    add_refs = {
        "roster_count_0x200a": refs(add_txt, OFF_ROSTER_COUNT),
        "supply_used_0x200c": refs(add_txt, OFF_SUPPLY_USED),
        "unit_count_cap_0x2010": refs(add_txt, OFF_UNIT_COUNT_CAP),
        "supply_cap_0x2012": refs(add_txt, OFF_SUPPLY_CAP),
    }
    notes["A5_gate_field_refs"] = gate_refs
    notes["A5_roster_add_field_refs"] = add_refs

    # the production gate consults BOTH caps
    check(
        gate_refs["unit_count_cap_0x2010"] >= 2,
        "A5: production gate does not consult the unit count cap +0x2010",
    )
    check(
        gate_refs["supply_cap_0x2012"] >= 1,
        "A5: production gate does not consult the supply cap +0x2012",
    )
    check(
        "movsx edx, word ptr [ecx + 0x200c]" in gate_txt
        and "cmp edx, ecx" in gate_txt
        and "jle" in gate_txt,
        "A5: production gate does not compare used+cost against the cap",
    )
    # roster_add consults NEITHER cap - only the 1200 array bound
    check(
        add_refs["unit_count_cap_0x2010"] == 0,
        "A5: roster_add unexpectedly consults +0x2010",
    )
    check(
        add_refs["supply_cap_0x2012"] == 0,
        "A5: roster_add unexpectedly consults +0x2012",
    )
    check(
        f"cmp ax, {ROSTER_ARRAY_LIMIT:#x}" in add_txt,
        "A5: roster_add does not bound the roster at 0x4b0",
    )
    check(
        "add word ptr [ecx + 0x200c], dx" in add_txt,
        "A5: roster_add is not the +0x200C adding writer",
    )
    check(
        "sub word ptr [ecx + 0x200c], dx" in del_txt,
        "A5: roster_del is not the +0x200C subtracting writer",
    )
    # the two writers derive the cost through the same tables (conservation)
    for tag, txt in (("add", add_txt), ("del", del_txt)):
        check(
            "0x66b81d" in txt and "0x9b5238" in txt,
            f"A5: roster_{tag} does not derive cost via 0x66b81d/0x9b5238",
        )
    notes["A5_verdict"] = (
        "PRODUCTION passes count<count_cap(+0x2010) AND used+cost<=cap(+0x2012). "
        "TRANSFER reaches the ledger through roster_add/roster_del, which "
        "enforce ONLY the 1200-entry array bound and consult NEITHER cap. "
        "So a transfer may raise an owner's used past its cap and its count "
        "past its count_cap, up to 1200 entries."
    )

    # ---- A6: is there another bound? roster * max_unit_cost -------------
    # FO-2 re-derived independently: both tables live past the raw image.
    cost_tbl_initialised = in_raw_data(secs, 0x9B5238)
    type_tbl_initialised = in_raw_data(secs, 0x66B81D)
    check(
        not cost_tbl_initialised and not type_tbl_initialised,
        "A6: cost/type tables are in raw data; max cost should be readable",
    )
    notes["A6_cost_table_statically_readable"] = cost_tbl_initialised
    notes["A6_type_table_statically_readable"] = type_tbl_initialised

    sdata = SAMPLES.read_bytes()
    check(
        hashlib.sha256(sdata).hexdigest() == SAMPLES_SHA256,
        "A6: samples.jsonl SHA does not match the pinned run",
    )
    rows = [json.loads(line) for line in sdata.decode().splitlines() if line.strip()]
    per_owner = {}
    for r in rows:
        for p in r["snapshot"]["players"]:
            if p["count"]:
                per_owner.setdefault(p["owner"], []).append(p["used"] / p["count"])
    means = {o: sum(v) / len(v) for o, v in per_owner.items()}
    min_mean = min(means.values())
    max_mean = max(means.values())
    notes["A6_observed_mean_cost_per_unit"] = {
        str(o): round(m, 3) for o, m in sorted(means.items())
    }
    notes["A6_samples"] = len(rows)

    # the cost at which a full 1200-entry roster exactly reaches the ceiling
    breakeven = SIGNED16_MAX / ROSTER_ARRAY_LIMIT
    notes["A6_breakeven_mean_cost_for_1200_roster"] = round(breakeven, 4)
    notes["A6_bound_at_observed_min_mean"] = round(min_mean * ROSTER_ARRAY_LIMIT, 1)
    notes["A6_bound_at_observed_max_mean"] = round(max_mean * ROSTER_ARRAY_LIMIT, 1)
    check(
        min_mean > breakeven,
        "A6: observed mean cost is below the 1200-roster breakeven; the "
        "roster bound might rescue the ceiling after all",
    )
    notes["A6_verdict"] = (
        f"The only remaining structural bound on one owner's ledger is "
        f"roster_limit * mean_unit_cost. Breakeven mean cost for a 1200 "
        f"roster is {breakeven:.2f}; every owner in the pinned run sits at "
        f"{min_mean:.1f}..{max_mean:.1f}. The bound therefore evaluates to "
        f"{min_mean * ROSTER_ARRAY_LIMIT:,.0f}..{max_mean * ROSTER_ARRAY_LIMIT:,.0f}, "
        f"all of it above 32767. This bound does NOT restore safety, and it "
        f"is CAP-INDEPENDENT: it is the same at stock 1500 as at 5000."
    )

    # ---- A7: at cap 5000, transfers ALONE already clear the ceiling -----
    first = rows[0]["snapshot"]["players"]
    total_used_first = sum(p["used"] for p in first)
    total_units_first = sum(p["count"] for p in first)
    notes["A7_first_sample_total_used"] = total_used_first
    notes["A7_first_sample_total_units"] = total_units_first
    concentration_fits_roster = total_units_first <= ROSTER_ARRAY_LIMIT
    notes["A7_all_units_fit_one_roster"] = concentration_fits_roster
    check(
        concentration_fits_roster and total_used_first > SIGNED16_MAX,
        "A7: pure concentration of the observed fixture does not exceed 32767",
    )
    notes["A7_verdict"] = (
        f"In the pinned cap-5000 fixture the whole world is {total_units_first} "
        f"units carrying {total_used_first:,} supply. {total_units_first} <= 1200, "
        f"so roster_add would accept every one of them into a single owner. No "
        f"production is needed: transfers alone reach {total_used_first:,} > 32767. "
        f"At cap<=4095 this particular path stays under the ceiling "
        f"(8*4095 = 32,760), which is exactly why A4's pump matters."
    )

    # ---- A8: completeness caveat, stated rather than claimed away -------
    notes["A8_completeness"] = [
        "The 5 direct-displacement refs to +0x200C bound only the "
        "`[reg + 0x200C]` addressing form. Writes through a computed or "
        "aliased base (absolute VA, bulk blob restore, memcpy of a "
        "PlayerStruct) are NOT covered by that sweep and are not claimed here.",
        "save/load restores +0x200C through the bulk blob outside both "
        "writers (lap393 FO-3 stands).",
        "The pump's REACHABILITY in a real supported 8-owner free-for-all is "
        "UNKNOWN. This probe settles arithmetic and gate structure only; it "
        "ran no game.",
        "The global unit pool (~1199 observed peak 1176) may bind before the "
        "1200-entry roster does; both are above the A6 breakeven, so the "
        "conclusion is unchanged, but the exact limiter is not pinned here.",
    ]

    out = {
        "probe": "lap395_middle_g2_cap_counterexample_review",
        "failures": failures,
        **notes,
    }
    print(json.dumps(out, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
