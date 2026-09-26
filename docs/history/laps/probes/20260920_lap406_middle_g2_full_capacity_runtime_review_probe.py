#!/usr/bin/env python3
"""lap406 middle — independent review of the self-claimed lap410/412 lineage.

Read-only.  Builds candidates in memory from the pinned original, re-derives the
two claimed repairs from original bytes, measures PE-section coverage of the
relocated block at every capacity actually used, and re-hashes the recorded
runtime artifacts.  Nothing is written except this probe's JSON output; the
original EXE and every runtime directory are only read.

Acceptance items come from docs/work/active/G2_STRATEGY_DIRECTION_LAP404.md §C.

Run:  PYTHONPATH=. python3 docs/history/laps/probes/20260920_lap406_middle_g2_full_capacity_runtime_review_probe.py
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

import capstone
import pefile

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from patches.population import full_tail_relocation_storage_layout_v1 as full_layout  # noqa: E402
from patches.population import g2_full_capacity_persistence_compat_v1 as compat_mod  # noqa: E402
from patches.population import g2_full_capacity_persistence_v1 as persist_mod  # noqa: E402
from patches.population import g2_full_capacity_supply5000_owner1200_v1 as product_mod  # noqa: E402
from patches.population import g2_full_unit_capacity_supply5000_v1 as combined_mod  # noqa: E402
from patches.population import g2_full_unit_capacity_v1 as capacity_mod  # noqa: E402

IMAGE_BASE = 0x00400000
STOCK = 1200

ORIGINAL_PATHS = (
    REPO_ROOT / "Syw2plus" / "syw2plus_original.exe",
    REPO_ROOT.parent / "Syw2plus" / "syw2plus_original.exe",
)
PINNED_ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

# Candidate SHAs as recorded by the self-claimed lap410/412 records.
RECORDED_CANDIDATES = {
    "n1250_supply5000": "c3bd799fefd31ffb8d02ed7e1d08bb734890c7e637c7eb3ffe4dc236004df5d3",
    "n4001_supply5000_owner1200": "20b95a94711590e1bd41559ce76a9de6e40c155948f8d559b1090909fc342794",
    "persistence_compat_n4001": "4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe",
    "persistence_sidecar_n4001": "1e90f62fdcecb49d47d85af54bef17744bb7ae9d895a43b1923fd59405a30093",
}

RUNTIME_ROOT = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity")

# (run directory under RUNTIME_ROOT + artifact basename, SHA recorded in the
# lap410/412 records).  Each run writes into a timestamped `runtime_*` child, so
# the basename is resolved by search rather than pinned to one timestamp.
RECORDED_ARTIFACTS = {
    "active_integrity_soak.jsonl": (
        "20260920_full_capacity_category_b_self_count/runtime/active_integrity_soak.jsonl",
        "94d8b0981558af26a2cee1ee155c96dd46b93bd57c163b3dc9f0ded21539f06e",
    ),
    "active_integrity_soak_summary.json": (
        "20260920_full_capacity_category_b_self_count/runtime/active_integrity_soak_summary.json",
        "c4c4c9be9369b29675c4c551167542fdb3751fd31dd6429206e0529c059d0c51",
    ),
    "seed_receipts.json": (
        "20260920_n4001_eight_owner_supply5000/runtime/seed_receipts.json",
        "dd2034995e93329ea5700c0b3e84a3c27af2b400694e2913e4e06991154f03bf",
    ),
    "postseed_snapshot.json": (
        "20260920_n4001_eight_owner_supply5000/runtime/postseed_snapshot.json",
        "f5e2968962d5fefb10d7d00b8d0c70e3d70da6030d562ea176b186216bed089d",
    ),
    "n4001_integrity_soak.jsonl": (
        "20260920_n4001_eight_owner_supply5000/runtime/n4001_integrity_soak.jsonl",
        "a797deef5e1295ae6dcbd23c2ca146960d2b9921b56778e8ca8d59519a8937ca",
    ),
    "n4001_integrity_soak_summary.json": (
        "20260920_n4001_eight_owner_supply5000/runtime/n4001_integrity_soak_summary.json",
        "62e6cb714dc8d7822f3b62e932fd72b6e791bc3ce5cd3149ae70d95524b7765c",
    ),
    "n4001_integrity_144k_extension.jsonl": (
        "20260920_n4001_eight_owner_supply5000/runtime/n4001_integrity_144k_extension.jsonl",
        "29054e47ef8033a6e0512f307d633145a26233cf93c6cfea9b6559277a7a0018",
    ),
    "n4001_integrity_144k_extension_summary.json": (
        "20260920_n4001_eight_owner_supply5000/runtime/n4001_integrity_144k_extension_summary.json",
        "1a3e175cae0a69d4237fa48c30423355c962e30a14d0ef4ba0e141bc901f84b7",
    ),
    "persistence_roundtrip_summary.json": (
        "20260920_n4001_persistence_sidecar/runtime/persistence_roundtrip_summary.json",
        "edf6a02a8af99cc89be06ec29d84a1faeeafd428c66720edb82952fb2f7cdeef",
    ),
    "frozen4000_verification.json": (
        "20260920_n4001_persistence_sidecar/runtime/frozen4000_verification.json",
        "b4a3a3a27a3bc0fb07ba954bc97fd1fb48b344a06c30b168310460f49322691d",
    ),
    "frozen4000_snapshot.json": (
        "20260920_n4001_persistence_sidecar/runtime/frozen4000_snapshot.json",
        "cf2c03563d86aa5e26b2ef0986b78f4d716e8af9b02f72abe7ad19449ef24799",
    ),
    "postload_integrity_soak.jsonl": (
        "20260920_n4001_postload_soak/runtime/postload_integrity_soak.jsonl",
        "5ca1be02c4f99080a86dcb983194efb4726759ed8de91bd78be8803910e8cdc1",
    ),
    "postload_integrity_soak_summary.json": (
        "20260920_n4001_postload_soak/runtime/postload_integrity_soak_summary.json",
        "667fdeaea1a87279a49ee4b93412754ea260b9a34b4cb88c0ff32f56e9625b58",
    ),
    "legacy_fallback_verification.json": (
        "20260920_n4001_persistence_compat/runtime/legacy_fallback_verification.json",
        "b88580620191f9c997efca34f282d39240e7d7745fb74339aac722b3056bcce7",
    ),
    "legacy_smoke.json": (
        "20260920_n4001_persistence_compat/runtime/legacy_smoke.json",
        "1e2eeff7809cec2175867a2040e2418412b5e51ffc6a6a4f05cf02a68aec60ad",
    ),
    "compat_new_format_verification.json": (
        "20260920_n4001_persistence_compat/runtime/compat_new_format_verification.json",
        "44589873c8206ade6a9b9219ba13f92010a213aec99c98c25509e74cd781335d",
    ),
    "list_corruption_detail.json": (
        "20260920_full_capacity_1201/runtime/list_corruption_detail.json",
        "c0cff72bbea924243a7c99258f31e15aebaffb0e4dbd0847c0a514c761f6409a",
    ),
    "live1201_list_validation.json": (
        "20260920_full_capacity_1201/runtime/live1201_list_validation.json",
        "ddd0966efd27e843731235e9fe584d8dc6ccbe2a7cdc9e0dc92551aa769b1f17",
    ),
    "active_alias_fix_soak.jsonl": (
        "20260920_full_capacity_1201_fix1/runtime/active_alias_fix_soak.jsonl",
        "95bdc81db5bc697d6c2b9951b3b34767091938f6b0829990cbec8d6115d1b3f3",
    ),
    "second_corruption_detail.json": (
        "20260920_full_capacity_1201_fix1/runtime/second_corruption_detail.json",
        "5c169c85c0769a982f8dadbb9e1b34f56bed664d42bfd9382ae1ada31d47a3f4",
    ),
}

failures: list[str] = []
notes: list[str] = []


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(condition: bool, message: str) -> bool:
    if not condition:
        failures.append(message)
    return condition


# ---------------------------------------------------------------- C1 originals
def item_original_paths() -> dict[str, Any]:
    out: dict[str, Any] = {"paths": {}}
    for path in ORIGINAL_PATHS:
        if not path.exists():
            failures.append(f"C1: original path missing: {path}")
            out["paths"][str(path)] = None
            continue
        digest = sha256(path.read_bytes())
        out["paths"][str(path)] = digest
        check(digest == PINNED_ORIGINAL_SHA, f"C1: {path} SHA {digest} != pinned")
    return out


# ------------------------------------------------- C2 candidate reproduction
def item_candidate_reproduction(original: bytes) -> dict[str, Any]:
    out: dict[str, Any] = {"rebuilt": {}, "n1200_identity": {}}

    candidate, _report = combined_mod.build_candidate(original, 1250)
    digest = sha256(candidate)
    out["rebuilt"]["n1250_supply5000"] = digest
    check(
        digest == RECORDED_CANDIDATES["n1250_supply5000"],
        f"C2: n1250_supply5000 rebuild {digest} != recorded",
    )

    candidate, _report = product_mod.build_candidate(original, 4001)
    digest = sha256(candidate)
    out["rebuilt"]["n4001_supply5000_owner1200"] = digest
    check(
        digest == RECORDED_CANDIDATES["n4001_supply5000_owner1200"],
        f"C2: n4001 product rebuild {digest} != recorded",
    )

    candidate, _report = persist_mod.build_candidate(original, 4001)
    digest = sha256(candidate)
    out["rebuilt"]["persistence_sidecar_n4001"] = digest
    check(
        digest == RECORDED_CANDIDATES["persistence_sidecar_n4001"],
        f"C2: persistence sidecar rebuild {digest} != recorded",
    )

    candidate, _report = compat_mod.build_candidate(original, 4001)
    digest = sha256(candidate)
    out["rebuilt"]["persistence_compat_n4001"] = digest
    check(
        digest == RECORDED_CANDIDATES["persistence_compat_n4001"],
        f"C2: persistence compat rebuild {digest} != recorded",
    )

    # N=1200 identity.  The invariant that the relocation work owns is that the
    # *capacity/relocation stage* is byte-identical at stock capacity.  The
    # persistence compositions additionally carry the deliberate, separately
    # pinned supply-5000 and owner-1200 constant edits, which are capacity
    # independent, so they are compared against that product baseline instead.
    product_1200 = product_mod.build_candidate(original, 1200)[0]
    for label, builder, baseline, baseline_name in (
        (
            "g2_full_unit_capacity_v1",
            lambda: capacity_mod.build_candidate(original, 1200)[0],
            original,
            "original",
        ),
        (
            "g2_full_capacity_persistence_v1",
            lambda: persist_mod.build_candidate(original, 1200)[0],
            product_1200,
            "supply5000+owner1200 product candidate",
        ),
        (
            "g2_full_capacity_persistence_compat_v1",
            lambda: compat_mod.build_candidate(original, 1200)[0],
            product_1200,
            "supply5000+owner1200 product candidate",
        ),
    ):
        built = builder()
        identical = built == baseline
        entry: dict[str, Any] = {
            "identical_to": baseline_name,
            "identical": identical,
            "also_identical_to_original": built == original,
        }
        if not identical:
            diff = [i for i in range(len(baseline)) if built[i] != baseline[i]]
            runs: list[dict[str, Any]] = []
            start = prev = diff[0]
            for offset in diff[1:]:
                if offset != prev + 1:
                    runs.append({"file_offset": f"0x{start:08x}", "length": prev - start + 1})
                    start = offset
                prev = offset
            runs.append({"file_offset": f"0x{start:08x}", "length": prev - start + 1})
            entry["changed_bytes"] = len(diff)
            entry["changed_runs"] = runs[:40]
            entry["changed_run_count"] = len(runs)
        out["n1200_identity"][label] = entry
        check(identical, f"C2: {label} at N=1200 is not byte-identical to its {baseline_name}")
    if not out["n1200_identity"]["g2_full_capacity_persistence_v1"]["also_identical_to_original"]:
        notes.append(
            "C2: the persistence candidates are not byte-identical to the ORIGINAL at "
            "N=1200 because they always carry the supply-5000 and owner-1200 constant "
            "edits; the relocation stage itself is identity (see g2_full_unit_capacity_v1)."
        )
    return out


# ----------------------------------------------------- C3 PE section coverage
def _section_intervals(data: bytes) -> list[tuple[str, int, int]]:
    pe = pefile.PE(data=data, fast_load=True)
    try:
        return [
            (
                section.Name.rstrip(b"\0").decode("ascii", "replace"),
                IMAGE_BASE + int(section.VirtualAddress),
                IMAGE_BASE + int(section.VirtualAddress) + int(section.Misc_VirtualSize),
            )
            for section in pe.sections
        ]
    finally:
        pe.close()


def _uncovered_bytes(intervals: list[tuple[str, int, int]], start: int, end: int) -> int:
    covered = 0
    cursor = start
    for _name, low, high in sorted(intervals, key=lambda item: item[1]):
        low = max(low, cursor)
        high = min(high, end)
        if high > low:
            covered += high - low
            cursor = high
    return (end - start) - covered


def item_section_coverage(original: bytes) -> dict[str, Any]:
    out: dict[str, Any] = {}
    cases = (
        ("n1250_supply5000", lambda: combined_mod.build_candidate(original, 1250)[0], 1250),
        ("n4001_supply5000_owner1200", lambda: product_mod.build_candidate(original, 4001)[0], 4001),
        ("persistence_sidecar_n4001", lambda: persist_mod.build_candidate(original, 4001)[0], 4001),
        ("persistence_compat_n4001", lambda: compat_mod.build_candidate(original, 4001)[0], 4001),
    )
    for label, builder, capacity in cases:
        candidate = builder()
        intervals = _section_intervals(candidate)
        result = full_layout.layout(capacity)
        block_start = result.regions[0].new_start
        block_end = result.regions[-1].new_end
        uncovered = _uncovered_bytes(intervals, block_start, block_end)
        per_region = {}
        for region in result.regions:
            per_region[region.name] = _uncovered_bytes(intervals, region.new_start, region.new_end)
        out[label] = {
            "capacity": capacity,
            "block": [f"0x{block_start:08x}", f"0x{block_end:08x}"],
            "block_bytes": block_end - block_start,
            "uncovered_bytes": uncovered,
            "uncovered_by_region": per_region,
            "sections": [
                {"name": name, "start": f"0x{low:08x}", "end": f"0x{high:08x}"}
                for name, low, high in intervals
            ],
        }
        check(uncovered == 0, f"C3: {label} leaves {uncovered} relocated bytes outside every section")

    # Which capacities does a pytest anchor actually gate?  lap402's G-c only
    # becomes a standing gate for the capacities a test names.
    test_source = (REPO_ROOT / "patches/population/test_g2_full_unit_capacity_v1.py").read_text()
    anchored = sorted(
        capacity
        for capacity in (1250, 4001)
        if f"test_n{capacity}_data_section_covers_every_relocated_region" in test_source
    )
    out["pytest_coverage_anchors"] = {
        "capacities_with_anchor": anchored,
        "capacities_built_by_this_probe": [1250, 4001],
        "unanchored": [c for c in (1250, 4001) if c not in anchored],
    }
    if out["pytest_coverage_anchors"]["unanchored"]:
        notes.append(
            "C3: section coverage measures clean at every capacity, but no pytest anchor "
            f"gates capacities {out['pytest_coverage_anchors']['unanchored']} "
            "(the product capacity is 4001) -- work must add one."
        )
    return out


# --------------------------------------------- C5 byte re-derivation of repairs
def _decode_at(data: bytes, va: int) -> capstone.CsInsn:
    offset = va - IMAGE_BASE
    engine = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    engine.detail = True
    return next(engine.disasm(bytes(data[offset : offset + 16]), va))


def item_repairs(original: bytes) -> dict[str, Any]:
    out: dict[str, Any] = {"active_alias": {}, "category_b_self_count": {}}
    candidate_1250 = capacity_mod.build_candidate(original, 1250)[0]
    candidate_1200 = capacity_mod.build_candidate(original, 1200)[0]
    active_1250 = full_layout.layout(1250).regions[5]
    catb_1250 = full_layout.layout(1250).regions[4]

    # Repair 1 — the two encoded `active_base - 2` aliases.
    patched_windows: list[tuple[int, int]] = []
    for va in capacity_mod.ACTIVE_LAST_ELEMENT_ALIAS_SITES:
        insn = _decode_at(original, va)
        needle = struct.pack("<I", capacity_mod.ACTIVE_LAST_ELEMENT_OLD_DISPLACEMENT)
        window = bytes(original[va - IMAGE_BASE : va - IMAGE_BASE + insn.size])
        positions = [i for i in range(len(window) - 3) if window[i : i + 4] == needle]
        disps = [
            int(op.mem.disp) & 0xFFFFFFFF
            for op in insn.operands
            if op.type == capstone.x86.X86_OP_MEM
        ]
        expected_new = struct.pack("<I", active_1250.new_start - 2)
        actual_new = bytes(
            candidate_1250[va - IMAGE_BASE + positions[0] : va - IMAGE_BASE + positions[0] + 4]
        ) if positions else b""
        out["active_alias"][f"0x{va:08x}"] = {
            "text": f"{insn.mnemonic} {insn.op_str}",
            "size": insn.size,
            "mem_displacements": [f"0x{value:08x}" for value in disps],
            "old_encoding_positions": positions,
            "patched_to": actual_new.hex(),
            "expected": expected_new.hex(),
        }
        check(
            capacity_mod.ACTIVE_LAST_ELEMENT_OLD_DISPLACEMENT in disps,
            f"C5: 0x{va:08x} does not carry displacement 0x974FA6",
        )
        check(len(positions) == 1, f"C5: 0x{va:08x} old displacement not uniquely encoded")
        check(actual_new == expected_new, f"C5: 0x{va:08x} not patched to relocated active_base-2")
        if positions:
            patched_windows.append((va - IMAGE_BASE + positions[0], 4))

    out["active_alias"]["patched_file_windows"] = [
        f"0x{start:08x}" for start, _size in patched_windows
    ]

    # Repair 2 — the category-B guard at 0x004A3692.
    insn = _decode_at(original, 0x004A3692)
    disps = [
        int(op.mem.disp) & 0xFFFFFFFF
        for op in insn.operands
        if op.type == capstone.x86.X86_OP_MEM
    ]
    old_rel = 0x0089C2C8 - capacity_mod.CATEGORY_BULK_BASE
    category_a = full_layout.REGIONS[3]
    stock_a_count = category_a.base + category_a.elem_size * STOCK
    out["category_b_self_count"] = {
        "va": "0x004a3692",
        "text": f"{insn.mnemonic} {insn.op_str}",
        "size": insn.size,
        "mem_displacements": [f"0x{value:08x}" for value in disps],
        "stock_absolute_target": f"0x{capacity_mod.CATEGORY_BULK_BASE + old_rel:08x}",
        "stock_category_a_count_va": f"0x{stock_a_count:08x}",
        "new_relative": f"0x{catb_1250.new_start + catb_1250.array_new_span - capacity_mod.CATEGORY_BULK_BASE:08x}",
    }
    check(
        old_rel in disps,
        "C5: 0x004A3692 does not carry the stock category-A count displacement",
    )
    check(
        capacity_mod.CATEGORY_BULK_BASE + old_rel == stock_a_count,
        "C5: stock target of 0x004A3692 is not category A's count WORD",
    )
    # N=1200 must not see the semantic repair at all.
    sites_1200 = capacity_mod.collect_fixup_sites(original, 1200)["category_slot_list_b"]
    guard_present_1200 = any(site.va == 0x004A3692 for site in sites_1200)
    out["category_b_self_count"]["present_at_n1200"] = guard_present_1200
    check(not guard_present_1200, "C5: category-B self_count repair leaks into N=1200")
    check(candidate_1200 == original, "C5: N=1200 candidate is not byte-identical")

    # Non-overlap: every applied 4-byte fixup window must be disjoint, and the
    # union of changed bytes in the candidate must equal that union exactly.
    all_sites = capacity_mod.collect_fixup_sites(original, 1250)
    windows: list[tuple[int, int, str]] = []
    for region, sites in all_sites.items():
        for site in sites:
            if site.va in capacity_mod.B2_EXCLUDED_VAS or site.new_value == site.old_value:
                continue
            insn = _decode_at(original, site.va)
            window = bytes(original[site.va - IMAGE_BASE : site.va - IMAGE_BASE + insn.size])
            needle = struct.pack("<I", site.old_value & 0xFFFFFFFF)
            positions = [i for i in range(len(window) - 3) if window[i : i + 4] == needle]
            if len(positions) != 1:
                failures.append(f"C5: 0x{site.va:08x} ({region}) old value not uniquely encoded")
                continue
            windows.append((site.va - IMAGE_BASE + positions[0], 4, region))
    occupied: dict[int, str] = {}
    overlaps: list[str] = []
    for start, size, region in windows:
        for offset in range(start, start + size):
            if offset in occupied and occupied[offset] != region:
                overlaps.append(f"0x{offset:08x} ({occupied[offset]} vs {region})")
            occupied[offset] = region
    out["fixup_windows"] = {
        "count": len(windows),
        "distinct_bytes": len(occupied),
        "overlaps": overlaps,
    }
    check(not overlaps, f"C5: overlapping fixup windows: {overlaps[:5]}")

    # Scalar predecessor 0x00974FA4 lives in BSS, not in .text; confirm no
    # applied .text fixup writes an address in [0x974FA4, 0x974FA8).
    bad = [
        f"0x{site.va:08x}"
        for sites in all_sites.values()
        for site in sites
        if 0x00974FA4 <= site.new_value < 0x00974FA8
    ]
    out["active_alias"]["new_values_landing_in_scalar_predecessor"] = bad
    check(not bad, f"C5: fixups still target the untouched scalar at 0x974FA4: {bad}")
    return out


# ------------------------------------------------- C4 runtime artifact hashes
def _resolve_artifact(relative: str) -> list[Path]:
    """Find the recorded basename anywhere under the run directory."""
    run_dir = RUNTIME_ROOT / relative.split("/", 1)[0]
    name = relative.rsplit("/", 1)[-1]
    if not run_dir.is_dir():
        return []
    return sorted(run_dir.rglob(name))


def item_runtime_artifacts() -> dict[str, Any]:
    out: dict[str, Any] = {"matched": [], "mismatched": [], "missing": []}
    for label, (relative, recorded) in RECORDED_ARTIFACTS.items():
        candidates = _resolve_artifact(relative)
        if not candidates:
            out["missing"].append({"label": label, "searched": relative})
            continue
        digests = {str(path): sha256(path.read_bytes()) for path in candidates}
        entry = {
            "label": label,
            "recorded": recorded,
            "copies": digests,
            "matching_paths": [path for path, digest in digests.items() if digest == recorded],
        }
        if entry["matching_paths"]:
            out["matched"].append(entry)
        else:
            out["mismatched"].append(entry)
    check(not out["mismatched"], f"C4: {len(out['mismatched'])} runtime artifact hash mismatches")
    check(not out["missing"], f"C4: {len(out['missing'])} recorded artifacts are absent on disk")

    # Re-run the offline verifier the record names, against the preserved bundle.
    from patches.population.verify_g2_persistence_artifacts import verify_bundle

    bundle = next(
        (RUNTIME_ROOT / "20260920_n4001_persistence_sidecar").glob("runtime_*/frozen4000_snapshot.json"),
        None,
    )
    if bundle is None:
        failures.append("C4: persistence bundle for the offline verifier not found")
    else:
        result = verify_bundle(bundle.parent)
        out["offline_verifier"] = {"run_dir": str(bundle.parent), "report": result}
        check(bool(result.get("ok")), "C4: offline persistence verifier did not report ok")
        check(
            result.get("sidecar_sha256") == result.get("serialized_sha256"),
            "C4: saved sidecar bytes differ from frozen post-load memory",
        )
    return out


def main() -> int:
    original_path = next((path for path in ORIGINAL_PATHS if path.exists()), None)
    if original_path is None:
        print(json.dumps({"failures": ["original EXE not found"]}, indent=2))
        return 1
    original = original_path.read_bytes()

    report: dict[str, Any] = {
        "probe": Path(__file__).name,
        "lap": 406,
        "role": "middle",
        "c1_originals": item_original_paths(),
        "c2_candidate_reproduction": item_candidate_reproduction(original),
        "c3_section_coverage": item_section_coverage(original),
        "c5_repairs": item_repairs(original),
        "c4_runtime_artifacts": item_runtime_artifacts(),
    }
    report["notes"] = notes
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
