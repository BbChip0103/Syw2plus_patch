#!/usr/bin/env python3
"""lap576 middle: W47 summary 비참조 raw/후보 독립 검수.

원본과 W47 raw는 읽기만 한다. F4 copy/restore 거부 계약은 임시 디렉터리에서만
검사하며, ``run_summary.json``은 열지 않는다.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from patches.population import supply_ledger_32bit as ledger  # noqa: E402
from patches.population.g2_full_capacity_persistence_compat_v1 import (  # noqa: E402
    build_candidate,
)
from tools import runtime_env  # noqa: E402

RAW = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/"
    "20260925_lap575_w47_f4_integrated_mixed_144k"
)
PRESERVED_EXE = ROOT / "local/runtime/20260925_021841_1993113_0/game/syw2plus_original.exe"
EXPECTED_ORIGINAL = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
EXPECTED_BASE = "a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68"
EXPECTED_COMBINED = "dfdc91adb88a732d96dff96f78648f03406003bffce1b22a7e5836317f963883"
EXPECTED_TYPES = {5, 7, 46, 2}
EXPECTED_ANCHORS = {
    0: [2, 2], 1: [27, 2], 2: [52, 2], 3: [77, 2],
    4: [2, 52], 5: [27, 52], 6: [52, 52], 7: [77, 52],
}
MEMORY_FIELDS = {
    "rss_kb", "vm_size_kb", "vm_swap_kb", "smaps_pss_kb",
    "smaps_rss_kb", "smaps_swap_pss_kb", "host_mem_available_kb",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_path(path: Path) -> str:
    return sha(path.read_bytes())


def apply_f4(data: bytes, *, reverse: bool = False) -> tuple[bytes, list[dict[str, object]]]:
    out = bytearray(data)
    sites: list[dict[str, object]] = []
    rows = reversed(ledger.EDITS) if reverse else ledger.EDITS
    for va, before, after in rows:
        expected, replacement = (after, before) if reverse else (before, after)
        offset = va - ledger.IMAGE_BASE
        actual = bytes(out[offset : offset + len(expected)])
        sites.append({
            "va": f"0x{va:08x}",
            "expected": expected.hex(),
            "actual": actual.hex(),
            "replacement": replacement.hex(),
            "pass": actual == expected and len(expected) == len(replacement),
        })
        if actual != expected:
            raise AssertionError(f"F4 bytes mismatch at 0x{va:08x}")
        out[offset : offset + len(replacement)] = replacement
    return bytes(out), sites


def main() -> int:
    # F1 / patch safety: exact input, old/new bytes, rejection, copy-only, non-overlap, restore.
    original_path = runtime_env.DEFAULT_SOURCE / runtime_env.ORIGINAL_EXE
    original_before = original_path.read_bytes()
    base, _ = build_candidate(original_before, 4001)
    combined, forward_sites = apply_f4(base)
    restored_base, reverse_sites = apply_f4(combined, reverse=True)
    original_after = original_path.read_bytes()

    base_diff = {i for i, (a, b) in enumerate(zip(original_before, base)) if a != b}
    f4_spans = [
        set(range(va - ledger.IMAGE_BASE, va - ledger.IMAGE_BASE + len(before)))
        for va, before, _after in ledger.EDITS
    ]
    f4_union = set().union(*f4_spans)
    f4_internal_overlap = sum(
        len(f4_spans[i] & f4_spans[j])
        for i in range(len(f4_spans)) for j in range(i + 1, len(f4_spans))
    )

    wrong_version_rejected = False
    try:
        ledger.patched_bytes(b"unsupported-version")
    except ValueError:
        wrong_version_rejected = True

    base_wrong_version_rejected = False
    try:
        build_candidate(b"unsupported-version", 4001)
    except (ValueError, RuntimeError):
        base_wrong_version_rejected = True

    with tempfile.TemporaryDirectory(prefix="lap576-f4-copy-") as temp_dir:
        temp = Path(temp_dir)
        source = temp / "source.exe"
        target = temp / "candidate.exe"
        source.write_bytes(original_before)
        source_hash_before = sha_path(source)
        created_hash = ledger.create_copy(source, target)
        source_unchanged_after_create = sha_path(source) == source_hash_before
        target_is_exact_f4 = target.read_bytes() == ledger.patched_bytes(original_before)
        restored_hash = ledger.restore(target)
        copy_restore_exact = target.read_bytes() == original_before

    patch_checks = {
        "original_sha": sha(original_before) == EXPECTED_ORIGINAL,
        "original_unchanged_during_review": original_before == original_after,
        "base_sha": sha(base) == EXPECTED_BASE,
        "combined_sha": sha(combined) == EXPECTED_COMBINED,
        "preserved_exe_sha": sha_path(PRESERVED_EXE) == EXPECTED_COMBINED,
        "forward_old_bytes_15": len(forward_sites) == 15 and all(x["pass"] for x in forward_sites),
        "combined_new_bytes_15": all(
            combined[va - ledger.IMAGE_BASE : va - ledger.IMAGE_BASE + len(after)] == after
            for va, _before, after in ledger.EDITS
        ),
        "reverse_new_bytes_15": len(reverse_sites) == 15 and all(x["pass"] for x in reverse_sites),
        "reverse_exact_base": restored_base == base,
        "combined_nonoverlap_base": not (base_diff & f4_union),
        "f4_internal_nonoverlap": f4_internal_overlap == 0,
        "wrong_version_rejected": wrong_version_rejected,
        "base_wrong_version_rejected": base_wrong_version_rejected,
        "copy_source_unchanged": source_unchanged_after_create,
        "copy_target_exact": target_is_exact_f4,
        "copy_restore_exact": copy_restore_exact,
        "copy_hashes_exact": created_hash == sha(ledger.patched_bytes(original_before))
        and restored_hash == EXPECTED_ORIGINAL,
    }

    receipts = json.loads((RAW / "seed_receipts.json").read_text(encoding="utf-8"))
    t0 = json.loads((RAW / "t0_positions.json").read_text(encoding="utf-8"))
    receipt_ops = {int(row["op"]) for row in receipts}
    forbidden_ops = sorted(receipt_ops - {5, 6, 7})
    receipt_failures = [
        row for row in receipts
        if not row["receipt"].get("ok")
        or (row["op"] in (5, 6) and row["receipt"].get("fixture_added", 0) < row["qty"])
    ]
    receipt_shape = Counter((row["owner"], row["op"], row["type"]) for row in receipts)
    expected_receipt_shape = Counter()
    for owner in range(8):
        expected_receipt_shape[(owner, 7, 0)] = 1
        expected_receipt_shape[(owner, 5, 5)] = 1
        expected_receipt_shape[(owner, 6, 7)] = 1
        expected_receipt_shape[(owner, 5, 2)] = 1
        expected_receipt_shape[(owner, 6, 46)] = 1
    anchors_pass = all(
        row["op"] == 7 or row["anchor"] == EXPECTED_ANCHORS[row["owner"]]
        for row in receipts
    )

    t0_counts: dict[int, Counter[int]] = defaultdict(Counter)
    for unit in t0:
        t0_counts[int(unit["owner"])][int(unit["type"])] += 1
    t0_fixture: dict[str, dict[str, object]] = {}
    b2 = True
    for owner in range(8):
        counts = t0_counts[owner]
        total = sum(counts.values())
        share = max(counts.values(), default=0) / total if total else 1.0
        owner_pass = EXPECTED_TYPES <= counts.keys() and counts[2] >= 10 and share <= 0.85
        b2 &= owner_pass
        t0_fixture[str(owner)] = {
            "total": total,
            "types": dict(sorted(counts.items())),
            "type2": counts[2],
            "max_share": round(share, 9),
            "pass": owner_pass,
        }

    records = []
    with (RAW / "samples.jsonl").open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if line.strip():
                record = json.loads(line)
                record["_line"] = line_number
                records.append(record)
    if not records:
        raise AssertionError("samples.jsonl is empty")

    violations = Counter()
    ledger_checks = 0
    bldg_values: list[int] = []
    memory_missing = 0
    previous_tick: int | None = None
    previous_live: int | None = None
    inferred_births = 0
    inferred_deaths = 0
    last_used = [None] * 8
    last_change_tick = [records[0]["tick"]] * 8
    vm_values: list[int] = []

    for index, sample in enumerate(records):
        tick = int(sample["tick"])
        owners = sample.get("owners", [])
        ledgers = sample.get("ledger_raw", [])
        if previous_tick is not None and tick < previous_tick:
            violations["tick_regression"] += 1
        previous_tick = tick
        if len(owners) != 8 or [row.get("owner") for row in owners] != list(range(8)):
            violations["owner_shape"] += 1
        if len(ledgers) != 8 or [row.get("owner") for row in ledgers] != list(range(8)):
            violations["ledger_shape"] += 1
        if sample.get("live") != sample.get("sum_count"):
            violations["live_count_mismatch"] += 1
        if sample.get("sum_count") != sum(row.get("count", -1) for row in owners):
            violations["owner_sum_mismatch"] += 1
        if previous_live is not None:
            delta = int(sample["live"]) - previous_live
            inferred_births += max(delta, 0)
            inferred_deaths += max(-delta, 0)
        previous_live = int(sample["live"])
        for field in MEMORY_FIELDS:
            if field not in sample or sample[field] is None:
                memory_missing += 1
        vm_values.append(int(sample["vm_size_kb"]))
        for owner, ledger_row in zip(owners, ledgers):
            used = int(owner["used"])
            if not 0 <= used <= 5000:
                violations["used_range"] += 1
            if not 0 <= int(owner["count"]) <= int(owner["count_cap"]):
                violations["count_range"] += 1
            if int(owner["cap"]) != 5000:
                violations["cap_not_5000"] += 1
            if int(owner["ai"]) != 1:
                violations["not_ai"] += 1
            if int(ledger_row["used_hi"]) != 0:
                violations["used_hi"] += 1
            if int(ledger_row["used32"]) != used:
                violations["used32_bridge"] += 1
            if not 0 <= int(ledger_row["used32"]) <= 5000:
                violations["used32_range"] += 1
            bldg_values.append(int(ledger_row["bldg"]))
            ledger_checks += 1
            owner_id = int(owner["owner"])
            if last_used[owner_id] is None or last_used[owner_id] != used:
                last_change_tick[owner_id] = tick
                last_used[owner_id] = used

    t0_used = [int(row["used"]) for row in records[0]["owners"]]
    b1 = (
        len(receipts) == 40
        and receipt_shape == expected_receipt_shape
        and not receipt_failures
        and receipt_ops == {5, 6, 7}
        and not forbidden_ops
        and anchors_pass
        and all(4900 <= used <= 5000 for used in t0_used)
    )
    log_text = (RAW / "w47_orchestrator.log").read_text(encoding="utf-8")
    events_empty = (RAW / "events.jsonl").read_bytes() == b""
    crash_markers = [marker for marker in ("FATAL", "RUN_ERROR", "fault", "crash") if marker.lower() in log_text.lower()]
    b3 = not violations and events_empty and not crash_markers
    b5 = int(records[-1]["tick"]) >= 144000
    vm_nondecreasing = all(a <= b for a, b in zip(vm_values, vm_values[1:]))
    vm_growth = (vm_values[-1] - vm_values[0]) / vm_values[0] if vm_values[0] else float("inf")
    b6 = memory_missing == 0 and vm_nondecreasing and vm_growth <= 0.05
    f2 = (
        violations["used_hi"] == 0
        and violations["used32_bridge"] == 0
        and violations["used32_range"] == 0
    )
    run_checks = {
        "F1": all(patch_checks.values()),
        "B1": b1,
        "B2": b2,
        "B3": b3,
        "B5": b5,
        "B6": b6,
        "F2": f2,
    }
    final_tick = int(records[-1]["tick"])
    first_tick = int(records[0]["tick"])
    tick_span = max(1, final_tick - first_tick)
    owner_freeze = {
        str(owner): {
            "last_change_tick": last_change_tick[owner],
            "frozen_ticks": final_tick - last_change_tick[owner],
            "frozen_ratio": round((final_tick - last_change_tick[owner]) / tick_span, 9),
        }
        for owner in range(8)
    }

    report = {
        "schema": "lap576_w47_middle_independent_review_v1",
        "summary_excluded": True,
        "raw_sha256": {
            name: sha_path(RAW / name)
            for name in (
                "w47_run.py", "seed_receipts.json", "receipts.json",
                "t0_positions.json", "samples.jsonl", "events.jsonl",
                "bridge_build/_inmm.dll", "w47_orchestrator.log",
            )
        },
        "patch": {
            "checks": patch_checks,
            "all_pass": all(patch_checks.values()),
            "base_diff_bytes": len(base_diff),
            "f4_sites": len(ledger.EDITS),
            "base_f4_overlap_bytes": len(base_diff & f4_union),
            "f4_internal_overlap_bytes": f4_internal_overlap,
            "forward_sites": forward_sites,
        },
        "fixture": {
            "receipt_count": len(receipts),
            "operations_seen": sorted(receipt_ops),
            "forbidden_operations": forbidden_ops,
            "receipt_failures": len(receipt_failures),
            "anchors_pass": anchors_pass,
            "t0_used": t0_used,
            "t0_live": len(t0),
            "owners": t0_fixture,
        },
        "raw": {
            "records": len(records),
            "sample_index_first_last": [records[0]["sample"], records[-1]["sample"]],
            "tick_first_last": [first_tick, final_tick],
            "wall_seconds": records[-1]["t"],
            "max_live": max(int(row["live"]) for row in records),
            "violations": dict(violations),
            "events_empty": events_empty,
            "crash_markers": crash_markers,
            "ledger_checks": ledger_checks,
            "bldg_min_max": [min(bldg_values), max(bldg_values)],
            "bldg_negative": sum(value < 0 for value in bldg_values),
            "memory_missing": memory_missing,
            "vm_first_last_kb": [vm_values[0], vm_values[-1]],
            "vm_growth_ratio": vm_growth,
            "vm_nondecreasing": vm_nondecreasing,
            "rss_min_max_kb": [min(row["rss_kb"] for row in records), max(row["rss_kb"] for row in records)],
            "pss_min_max_kb": [min(row["smaps_pss_kb"] for row in records), max(row["smaps_pss_kb"] for row in records)],
            "host_available_min_kb": min(row["host_mem_available_kb"] for row in records),
            "aggregate_live_delta_births_deaths": [inferred_births, inferred_deaths],
            "owner_freeze": owner_freeze,
        },
        "checks": run_checks,
        "verdict": "ACCEPT / STABLE_MIXED_144K_F4" if all(run_checks.values()) else "REJECT",
    }
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if all(run_checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
