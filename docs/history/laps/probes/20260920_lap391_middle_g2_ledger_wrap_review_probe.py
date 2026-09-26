#!/usr/bin/env python3
"""lap391 middle — independent re-derivation of lap390 W1 (F4 ledger-wrap reachability).

Read-only. Does NOT import lap390's script; recomputes every reported number from
samples.jsonl directly, plus adversarial checks lap390 did not run.

rc0 + failures==[] means every lap390 claim this probe can reach was reproduced.
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

TEMP = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch")
RUN = TEMP / "g2_capacity/20260919_eight_owner_5000_stability_actual_v1"
SAMPLES = RUN / "official_run1/g2_stock_24k_observation/samples.jsonl"
LAP390_OUT = TEMP / ("g2_capacity/20260919_owner_transfer_cap/"
                     "lap390_work_ledger_wrap_reachability/output.json")
ANALYSIS = RUN / "independent_analysis_v1/analysis.json"
DRIVER = Path("/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_patch"
              "/patches/population/runtime_driver.py")

# lap390 report + lap389 middle claims, transcribed here by hand so the probe
# does not read its verdict out of the artifact it is auditing.
CLAIM_SAMPLE_COUNT = 146
CLAIM_M1_NEGATIVES = 0
CLAIM_M2_MAX = (5003, 1, 33185, 140)  # used, owner, tick, sample
CLAIM_M3_EVENTS = 0
CLAIM_M4_FIRST = 40000
CLAIM_M4_LAST = 35427
CLAIM_VIOLATIONS = 7  # lap389: samples 140..146, owner1 used 5003 > cap 5000
CLAIM_PER_OWNER = {
    0: (3845, 5000), 1: (4685, 5003), 2: (4920, 5000), 3: (4691, 5000),
    4: (4730, 5000), 5: (3895, 5000), 6: (3938, 5000), 7: (4360, 5000),
}
SIGNED16_CEIL = 32767

failures: list[str] = []
notes: list[str] = []


def check(cond: bool, msg: str) -> None:
    if not cond:
        failures.append(msg)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    check(SAMPLES.is_file(), f"samples.jsonl missing: {SAMPLES}")
    if failures:
        print(json.dumps({"failures": failures}, indent=2))
        return 1

    samples_sha = sha256(SAMPLES)

    # --- A. provenance: which SHA does the surviving machine artifact pin? ---
    analysis_source_sha = json.loads(ANALYSIS.read_text())["source"]["sha256"]
    lap390 = json.loads(LAP390_OUT.read_text())
    lap390_input_sha = lap390["input"]["samples_jsonl_sha256"]
    check(analysis_source_sha == samples_sha,
          f"9/19 analysis source.sha256 {analysis_source_sha} != live {samples_sha}")
    check(lap390_input_sha == samples_sha,
          f"lap390 output.json input sha {lap390_input_sha} != live {samples_sha}")

    # --- B. is M1 (signed16 negative) a valid wrap detector at all? ---
    # The sampler must read +0x200C as a SIGNED word, else a wrap would surface
    # as a large positive / garbage value and M1 would be blind.
    driver_src = DRIVER.read_text()
    check("used=i16(0x200C)," in driver_src,
          "runtime_driver no longer reads used via i16(0x200C)")
    check('struct.unpack_from("<h", data, off)' in driver_src,
          "runtime_driver i16 is not a signed-16 ('<h') unpack")
    # and prove '<h' actually sign-extends, so a wrapped word lands negative
    check(struct.unpack_from("<h", struct.pack("<H", 40000), 0)[0] == -25536,
          "'<h' does not sign-extend as assumed")
    notes.append("M1 valid: sampler already decodes +0x200C as signed16, so a "
                 "ledger wrap is directly observable as a negative 'used'; "
                 "lap390's extra 'signed16 reinterpretation' is an identity, "
                 "not an added decode step.")

    # --- C. recompute M1..M4 from the raw trace ---
    rows = [json.loads(line) for line in SAMPLES.read_text().splitlines() if line.strip()]
    check(len(rows) == CLAIM_SAMPLE_COUNT,
          f"sample count {len(rows)} != claimed {CLAIM_SAMPLE_COUNT}")

    negatives = []
    violations = []
    per_owner: dict[int, list[int]] = {o: [] for o in range(8)}
    per_owner_count: dict[int, list[int]] = {o: [] for o in range(8)}
    totals = []
    best = None  # (used, owner, tick, sample)
    prev_used: dict[int, int] = {}
    m3_events = []

    for row in rows:
        snap = row["snapshot"]
        tick = snap["tick"]
        sample = row["sample"]
        players = snap["players"]
        check(len(players) == 8, f"sample {sample}: {len(players)} players, expected 8")
        total = 0
        for p in players:
            owner, used, cap = p["owner"], p["used"], p["cap"]
            check(isinstance(used, int), f"sample {sample} owner {owner}: used not int")
            total += used
            per_owner[owner].append(used)
            per_owner_count[owner].append(p["count"])
            if used < 0:
                negatives.append({"sample": sample, "tick": tick, "owner": owner,
                                  "used": used})
            if used > cap:
                violations.append({"sample": sample, "tick": tick, "owner": owner,
                                   "used": used, "cap": cap})
            if best is None or used > best[0]:
                best = (used, owner, tick, sample)
            # M3: another owner's roster collapsed to 0 while this owner jumped
            if p["count"] == 0 and prev_used.get(owner, 0) != 0:
                m3_events.append({"sample": sample, "owner": owner,
                                  "kind": "roster_zero_transition"})
            prev_used[owner] = used
        totals.append({"sample": sample, "tick": tick, "total_used": total})

    check(len(negatives) == CLAIM_M1_NEGATIVES,
          f"M1 negatives {len(negatives)} != claimed {CLAIM_M1_NEGATIVES}")
    check(best == CLAIM_M2_MAX, f"M2 {best} != claimed {CLAIM_M2_MAX}")
    check(len(m3_events) == CLAIM_M3_EVENTS,
          f"M3 events {len(m3_events)} != claimed {CLAIM_M3_EVENTS}")
    check(totals[0]["total_used"] == CLAIM_M4_FIRST,
          f"M4 first {totals[0]['total_used']} != claimed {CLAIM_M4_FIRST}")
    check(totals[-1]["total_used"] == CLAIM_M4_LAST,
          f"M4 last {totals[-1]['total_used']} != claimed {CLAIM_M4_LAST}")
    check(len(violations) == CLAIM_VIOLATIONS,
          f"used>cap violations {len(violations)} != lap389's {CLAIM_VIOLATIONS}")
    for owner, (lo, hi) in CLAIM_PER_OWNER.items():
        got = (min(per_owner[owner]), max(per_owner[owner]))
        check(got == (lo, hi), f"owner {owner} used range {got} != claimed {(lo, hi)}")

    # --- D. adversarial checks lap390 did NOT run ---
    # D1. M3 is edge-triggered, so it is blind to an owner defeated BETWEEN
    #     samples that stays at 0. A level check on roster count is gap-proof.
    count_minima = {o: min(v) for o, v in per_owner_count.items()}
    any_defeated = [o for o, m in count_minima.items() if m == 0]
    check(not any_defeated,
          f"owners reached roster 0 (mass-absorption possible): {any_defeated}")
    notes.append(f"D1 gap-proof: per-owner roster count minimum = {count_minima}; "
                 "no owner is ever defeated in this trace, so FUN_00444EF0 "
                 "(mass absorption) cannot have fired between samples either. "
                 "This is strictly stronger than lap390's edge-triggered M3.")

    # D2. how far is the trace from the wrap, in the trace's own units?
    headroom = SIGNED16_CEIL - best[0]
    global_max = max(t["total_used"] for t in totals)
    notes.append(f"D2 headroom: max single-owner used {best[0]}, signed16 ceiling "
                 f"{SIGNED16_CEIL}, headroom {headroom} ({headroom / best[0]:.1f}x "
                 f"the observed maximum). Global sum peak {global_max} exceeds the "
                 "ceiling, so F4's arithmetic premise survives: the wrap is "
                 "unreachable in THIS fixture, not unreachable in principle.")

    # D3. sampling cadence — establish what 'this fixture' actually covered.
    ticks = [t["tick"] for t in totals]
    gaps = [b - a for a, b in zip(ticks, ticks[1:])]
    check(all(g >= 0 for g in gaps), "tick sequence is not monotonic")
    notes.append(f"D3 coverage: ticks {ticks[0]}..{ticks[-1]} "
                 f"(span {ticks[-1] - ticks[0]}), {len(rows)} samples, "
                 f"gap min/median/max {min(gaps)}/{sorted(gaps)[len(gaps)//2]}/{max(gaps)}. "
                 "Sampled, not continuous: a transient wrap that healed inside one "
                 "gap would be invisible. D1 bounds this — no defeat occurred.")

    # D4. cap is uniformly 5000 (the fixture is the one F4 is about)
    caps = {p["cap"] for row in rows for p in row["snapshot"]["players"]}
    check(caps == {5000}, f"cap not uniformly 5000: {sorted(caps)}")

    out = {
        "schema": "syw2plus.g2.lap391_middle_ledger_wrap_review.v1",
        "reviewing": "lap390 work W1 (NOT_FEASIBLE)",
        "samples_jsonl": str(SAMPLES),
        "samples_jsonl_sha256": samples_sha,
        "sample_count": len(rows),
        "m1_negative_count": len(negatives),
        "m2_single_owner_used_max": {"used": best[0], "owner": best[1],
                                     "tick": best[2], "sample": best[3]},
        "m3_edge_event_count": len(m3_events),
        "m4_global_used_first": totals[0],
        "m4_global_used_last": totals[-1],
        "used_over_cap_violations": len(violations),
        "violation_samples": [v["sample"] for v in violations],
        "per_owner_used_range": {str(o): [min(v), max(v)] for o, v in per_owner.items()},
        "per_owner_roster_count_min": {str(o): m for o, m in count_minima.items()},
        "signed16_headroom_from_observed_max": headroom,
        "global_used_sum_peak": global_max,
        "notes": notes,
        "failures": failures,
    }
    print(json.dumps(out, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
