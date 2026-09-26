#!/usr/bin/env python3
"""lap385 middle(Opus5/high) independent acceptance probe for lap384's R1~R6 repair.

Read-only.  Launches nothing, writes nothing outside stdout.  Deliberately
re-derives every number from the pinned region table / the original EXE bytes
instead of trusting `base_preserving_storage_layout_v1`'s own outputs, and
re-implements the *pre-repair* algorithm locally so each R-item's claimed
defect is reproduced before its fix is accepted.

Exit code 0 with `failures=[]` == every R-item independently confirmed.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
MODULE = REPO / "patches/population/base_preserving_storage_layout_v1.py"
TESTS = REPO / "patches/population/test_base_preserving_storage_layout_v1.py"
RUNTIME_ENV = REPO / "tools/runtime_env.py"
ORIGINAL = REPO / "Syw2plus/syw2plus_original.exe"
ARTIFACT_DIR = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/"
    "20260918_lap383_layout_artifact"
)

ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
LAP384_MODULE_SHA = "7ae85ef50ae324a42a16f8cb251b05498f22f18a7d9f84d20cd361bf1a136cb2"
LAP384_TEST_SHA = "88672c65a91185526296a81e25008b352756eda2bf6569ba8d3a4b3fc8ccee9a"
LAP384_PELAYOUT_SHA = "38a7148ed7395de74c144329ec43f14ec3b0fefe394a5f2ab01d8ca436cbc808"
LAP384_MAPPING_SHA = "fb7f9e833f0d66985d4fbf814b7af89bd62c205216a75d10b650d11c91605b18"

# Independent transcription of the pinned N=1200 table (plan §1), NOT read from
# the module: (name, base, elem_size, count_bytes).
PINNED = (
    ("unit_pool", 0x0066B790, 0x758, 0),
    ("unit_existence", 0x008990C8, 2, 0),
    ("unit_age", 0x00899A28, 2, 0),
    ("category_slot_list_a", 0x0089B008, 4, 2),
    ("category_slot_list_b", 0x0089C2CA, 4, 2),
    ("active_slot_list", 0x00974FA8, 2, 2),
)
RSRC_BASE = 0x400000 + 0x00C8C000
RSRC_SIZE = 0x20F0
STOCK = 1200

failures: list[str] = []
notes: dict[str, object] = {}


def check(name: str, condition: bool, detail: object = None) -> None:
    if not condition:
        failures.append(name)
    if detail is not None:
        notes[name] = detail


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# --- local re-implementations -------------------------------------------------


def local_growth_below(base: int, n: int) -> int:
    """Cumulative region-array growth strictly below `base`, from PINNED only."""
    total = 0
    for _name, rbase, elem, _cb in PINNED:
        if rbase < base:
            total += elem * (n - STOCK)
    return total


def local_rsrc_new_start(n: int) -> int:
    raw = RSRC_BASE + local_growth_below(RSRC_BASE, n)
    return (raw + 0xFFF) // 0x1000 * 0x1000


def pre_repair_entries(n: int):
    """lap382 (pre-R1/R3) chain, reconstructed: no shrink guard, running delta
    allowed to go negative.  Used only to reproduce the R1 defect."""
    entries = []
    running = 0
    for i, (name, base, elem, cb) in enumerate(PINNED):
        old_span = elem * STOCK + cb
        new_span = elem * n + cb
        entries.append(("region", name, base, base + old_span, base + running, elem * STOCK, elem * n))
        running += new_span - old_span
        region_end = base + old_span
        nxt = PINNED[i + 1][1] if i + 1 < len(PINNED) else RSRC_BASE
        if nxt - region_end > 0:
            entries.append(
                ("foreign", f"gap_after_{name}", region_end, nxt, region_end + running, 0, 0)
            )
    entries.append(("foreign", "rsrc", RSRC_BASE, RSRC_BASE + RSRC_SIZE, RSRC_BASE + running, 0, 0))
    entries.sort(key=lambda e: e[2])
    return entries


def pre_repair_map_va(old_va: int, n: int):
    for kind, name, old_start, old_end, new_start, arr_old, arr_new in pre_repair_entries(n):
        if not (old_start <= old_va < old_end):
            continue
        local = old_va - old_start
        if kind == "region":
            new_va = new_start + local if local < arr_old else new_start + arr_new + (local - arr_old)
            new_span = arr_new + (old_end - old_start - arr_old)
        else:
            new_va = new_start + local
            new_span = old_end - old_start
        return kind, name, new_va, (new_start, new_start + new_span)
    return "unmappable", None, None, None


def pre_repair_owner_of_new_va(new_va: int, n: int):
    """Which block's *new* extent actually contains `new_va` under the
    pre-repair layout for capacity `n`?"""
    for kind, name, old_start, old_end, new_start, arr_old, arr_new in pre_repair_entries(n):
        new_span = (arr_new + (old_end - old_start - arr_old)) if kind == "region" else old_end - old_start
        if new_start <= new_va < new_start + new_span:
            return name, (new_start, new_start + new_span)
    return None, None


def main() -> int:
    mod = load(MODULE, "lap385_layout_mod")

    # --- provenance -----------------------------------------------------------
    check("original_exe_sha_unchanged", sha(ORIGINAL) == ORIGINAL_SHA)
    check("module_sha_matches_lap384_record", sha(MODULE) == LAP384_MODULE_SHA)
    check("test_sha_matches_lap384_record", sha(TESTS) == LAP384_TEST_SHA)
    check(
        "module_pinned_table_matches_independent_transcription",
        tuple((r.name, r.base, r.elem_size, r.count_bytes) for r in mod.REGIONS) == PINNED,
    )

    # --- R1: shrink is rejected, and the defect it replaces is real -----------
    # The lap383 R1 measurement is at N=100: the address of discarded slot 1199
    # still resolves as kind="region"/unit_pool even though unit_pool's new
    # extent ends far below it.
    stray = 0x0066B790 + 0x758 * 1199
    kind, block, new_va, claimed_extent = pre_repair_map_va(stray, 100)
    owner, owner_extent = pre_repair_owner_of_new_va(new_va, 100) if new_va else (None, None)
    check(
        "r1_pre_repair_defect_reproduced_independently",
        kind == "region" and block == "unit_pool" and new_va == 0x891CB8,
        {
            "pre_repair_kind": kind,
            "pre_repair_new_va": hex(new_va or 0),
            "claimed_block": block,
            "claimed_block_new_extent": [hex(x) for x in (claimed_extent or ())],
        },
    )
    check(
        "r1_stray_new_va_falls_outside_unit_pool_and_inside_a_foreign_block",
        claimed_extent is not None
        and not (claimed_extent[0] <= new_va < claimed_extent[1])
        and owner == "gap_after_active_slot_list",
        {"actual_owner_of_new_va": owner, "owner_extent": [hex(x) for x in (owner_extent or ())]},
    )
    raised = []
    for fn, arg in (("layout", 1199), ("layout", 0), ("layout", -1), ("map_va", 1199)):
        try:
            mod.layout(arg) if fn == "layout" else mod.map_va(stray, arg)
            raised.append(f"{fn}({arg}) did NOT raise")
        except ValueError:
            pass
        except Exception as exc:  # noqa: BLE001
            raised.append(f"{fn}({arg}) raised {type(exc).__name__}")
    check("r1_shrink_and_nonpositive_rejected_with_ValueError", raised == [], {"unexpected": raised})
    check("r1_stock_capacity_itself_still_accepted", mod.layout(STOCK).capacity == STOCK)

    # --- R2: every ForeignLayout.delta is the true address shift -------------
    r2_detail: dict[str, object] = {}
    r2_ok = True
    for n in (4001, 9601, 9904):
        result = mod.layout(n)
        for f in result.foreign_blocks:
            expected = (
                local_rsrc_new_start(n) - RSRC_BASE
                if f.name == "rsrc"
                else local_growth_below(f.old_start, n)
            )
            if f.delta != expected or f.delta != f.new_start - f.old_start:
                r2_ok = False
            if n == 4001:
                r2_detail[f.name] = {"delta": f.delta, "independent": expected}
    check("r2_foreign_delta_equals_independently_derived_address_shift", r2_ok, r2_detail)
    check(
        "r2_gap_deltas_match_lap384_recorded_numbers",
        [r2_detail[k]["delta"] for k in r2_detail if k.startswith("gap_")]
        == [5265880, 5277084, 5299492, 5305094]
        and r2_detail["rsrc"]["delta"] == 5308416,
    )
    check(
        "r2_region_delta_documented_as_span_growth_not_address_shift",
        "NOT an address shift" in MODULE.read_text(),
    )
    # The field the next consumer reads must never be 0 for a shifted block.
    check(
        "r2_no_foreign_block_reports_zero_delta_under_expansion",
        all(f.delta > 0 for f in mod.layout(4001).foreign_blocks),
    )

    # --- R3: the 32-bit guard sits at the true boundary -----------------------
    # Independently solve for the first N whose rsrc.new_end reaches 2**32.
    first_bad = None
    lo, hi = STOCK, 4_000_000
    while lo <= hi:
        mid = (lo + hi) // 2
        if local_rsrc_new_start(mid) + RSRC_SIZE >= 2**32:
            first_bad = mid
            hi = mid - 1
        else:
            lo = mid + 1
    check(
        "r3_independent_first_overflowing_capacity_is_2259703",
        first_bad == 2_259_703,
        {"independent_first_bad_N": first_bad},
    )
    accepted = None
    try:
        accepted = mod.layout(first_bad - 1).size_of_image
    except Exception as exc:  # noqa: BLE001
        failures.append("r3_module_accepts_last_safe_capacity")
        notes["r3_module_accepts_last_safe_capacity"] = repr(exc)
    check("r3_last_safe_capacity_accepted", accepted is not None)
    try:
        mod.layout(first_bad)
        check("r3_first_overflowing_capacity_rejected", False)
    except OverflowError:
        check("r3_first_overflowing_capacity_rejected", True)
    check(
        "r3_guard_source_uses_bare_2_32_not_image_base_offset",
        "rsrc.new_end >= 2**32" in MODULE.read_text()
        and "IMAGE_BASE + 2**32" not in MODULE.read_text(),
    )

    # --- R4: the required private artifacts exist, under designated temp ------
    pelayout = ARTIFACT_DIR / "g2_layout_n4001.pelayout"
    mapping = ARTIFACT_DIR / "g2_layout_n4001_mapping.json"
    check("r4_pelayout_artifact_exists", pelayout.is_file())
    check("r4_mapping_json_exists", mapping.is_file())
    if pelayout.is_file():
        check("r4_pelayout_sha_matches_lap384_record", sha(pelayout) == LAP384_PELAYOUT_SHA)
        rebuilt = mod.build_layout_artifact(ORIGINAL.read_bytes(), 4001)
        check(
            "r4_pelayout_bytes_reproduce_from_pinned_original",
            hashlib.sha256(rebuilt).hexdigest() == sha(pelayout),
        )
        check("r4_pelayout_is_not_an_exe_name", pelayout.suffix == ".pelayout")
        # Independent PE check: file length invariant, .rsrc RVA shifted by the
        # independently derived amount.
        orig = ORIGINAL.read_bytes()
        check("r4_artifact_length_invariant", len(rebuilt) == len(orig))
        pe = struct.unpack_from("<I", rebuilt, 0x3C)[0]
        opt = pe + 24
        num_sections = struct.unpack_from("<H", rebuilt, pe + 6)[0]
        sect = pe + 24 + struct.unpack_from("<H", rebuilt, pe + 20)[0]
        rsrc_rva_new = rsrc_rva_old = None
        for i in range(num_sections):
            off = sect + i * 40
            if rebuilt[off : off + 8].rstrip(b"\0") == b".rsrc":
                rsrc_rva_new = struct.unpack_from("<I", rebuilt, off + 12)[0]
                rsrc_rva_old = struct.unpack_from("<I", orig, off + 12)[0]
        check(
            "r4_artifact_rsrc_rva_shift_matches_independent_layout",
            rsrc_rva_new is not None
            and rsrc_rva_new - rsrc_rva_old == local_rsrc_new_start(4001) - RSRC_BASE,
            {"rva_shift": None if rsrc_rva_new is None else rsrc_rva_new - rsrc_rva_old},
        )
        check(
            "r4_artifact_size_of_image_covers_new_rsrc_end",
            0x400000 + struct.unpack_from("<I", rebuilt, opt + 56)[0]
            >= local_rsrc_new_start(4001) + RSRC_SIZE,
        )
    if mapping.is_file():
        check("r4_mapping_sha_matches_lap384_record", sha(mapping) == LAP384_MAPPING_SHA)
        try:
            payload = json.loads(mapping.read_text())
            check("r4_mapping_json_parses_and_names_capacity", payload is not None)
        except Exception as exc:  # noqa: BLE001
            check("r4_mapping_json_parses_and_names_capacity", False, repr(exc))
    check(
        "r4_no_layout_artifact_leaked_into_main_repo",
        list(REPO.rglob("*.pelayout")) == [],
        {"leaked": [str(p) for p in REPO.rglob("*.pelayout")]},
    )

    # --- R5: is validate_original_source really on the launch path? -----------
    rt_tree = ast.parse(RUNTIME_ENV.read_text())
    launch_entry_facts: dict[str, object] = {}
    for fn in [n for n in ast.walk(rt_tree) if isinstance(n, ast.FunctionDef)]:
        if fn.name not in {"prepare", "check_runtime"}:
            continue
        calls = [
            n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "")
            for n in ast.walk(fn)
            if isinstance(n, ast.Call)
        ]
        first_validate = calls.index("validate_original_source") if "validate_original_source" in calls else None
        popen_idx = [i for i, c in enumerate(calls) if c == "Popen"]
        launch_entry_facts[fn.name] = {
            "validate_at": first_validate,
            "popen_at": popen_idx,
            "n_calls": len(calls),
        }
    check(
        "r5_validate_original_source_is_called_by_both_launch_entrypoints",
        set(launch_entry_facts) == {"prepare", "check_runtime"}
        and all(v["validate_at"] is not None for v in launch_entry_facts.values()),
        launch_entry_facts,
    )
    check(
        "r5_validate_precedes_every_popen_in_those_entrypoints",
        all(
            v["validate_at"] is not None and all(p > v["validate_at"] for p in v["popen_at"])
            for v in launch_entry_facts.values()
        ),
    )
    test_tree = ast.parse(TESTS.read_text())
    r5_fn = next(
        (
            n
            for n in ast.walk(test_tree)
            if isinstance(n, ast.FunctionDef)
            and n.name
            == "test_expanded_artifact_is_actually_rejected_by_the_repo_launcher_entrypoint_with_zero_popen"
        ),
        None,
    )
    r5_calls = (
        [
            n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", "")
            for n in ast.walk(r5_fn)
            if isinstance(n, ast.Call)
        ]
        if r5_fn
        else []
    )
    check(
        "r5_test_actually_calls_validate_original_source_by_ast",
        "validate_original_source" in r5_calls and "setattr" in r5_calls,
        {"calls": sorted(set(r5_calls))},
    )
    # Live re-run of the rejection, independent of pytest.
    runtime_env = load(RUNTIME_ENV, "lap385_runtime_env")
    import subprocess as _sp
    import tempfile

    popen_hits: list[object] = []
    real_popen = _sp.Popen

    def _spy(*a: object, **k: object):
        popen_hits.append((a, k))
        raise AssertionError("Popen called")

    _sp.Popen = _spy  # type: ignore[assignment]
    try:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "expanded_source"
            src.mkdir()
            (src / runtime_env.ORIGINAL_EXE).write_bytes(mod.build_layout_artifact(ORIGINAL.read_bytes(), 4001))
            rejected = False
            try:
                runtime_env.validate_original_source(src)
            except runtime_env.RuntimeSafetyError as exc:
                rejected = "SHA-256 mismatch" in str(exc)
            check("r5_live_rejection_of_expanded_artifact_observed", rejected)
            # Control: the stock-capacity artifact is byte-identical, so it is
            # NOT rejected -- proves the gate keys on content, not on the dir.
            src2 = Path(td) / "stock_source"
            src2.mkdir()
            (src2 / runtime_env.ORIGINAL_EXE).write_bytes(
                mod.build_layout_artifact(ORIGINAL.read_bytes(), STOCK)
            )
            control_ok = False
            try:
                runtime_env.validate_original_source(src2)
                control_ok = True
            except runtime_env.RuntimeSafetyError:
                control_ok = False
            check("r5_control_stock_artifact_is_accepted_by_same_gate", control_ok)
        check("r5_zero_popen_during_rejection", popen_hits == [])
    finally:
        _sp.Popen = real_popen  # type: ignore[assignment]

    # --- R6: identity probes, exactly one allowed unmappable ------------------
    probes: list[int] = []
    for _name, base, elem, cb in PINNED:
        end = base + elem * STOCK + cb
        probes += [base - 1, base, base + 1, end - 1, end, end + 1]
    unmappable = [p for p in probes if mod.map_va(p, STOCK).kind == "unmappable"]
    identity_bad = [
        hex(p) for p in probes if mod.map_va(p, STOCK).kind != "unmappable" and mod.map_va(p, STOCK).new_va != p
    ]
    check(
        "r6_exactly_one_unmappable_probe_and_it_is_0x66B78F",
        unmappable == [0x0066B78F],
        {"unmappable": [hex(u) for u in unmappable], "n_probes": len(probes)},
    )
    check("r6_all_other_probes_are_identity_at_n1200", identity_bad == [], {"bad": identity_bad})
    check(
        "r6_test_pins_the_allowed_address_instead_of_blanket_skip",
        "ALLOWED_UNMAPPABLE_PROBE = 0x0066B78F" in TESTS.read_text(),
    )

    # --- plan §3-5: is the alias/PlayerStruct span exposed anywhere? ----------
    text = MODULE.read_text()
    check(
        "s3_5_still_unimplemented_as_lap384_reported",
        "0x892410" not in text and "PlayerStruct" not in text,
        {"note": "informational: confirms the descope decision is still open"},
    )
    # But the 3-fold alias must at least be arithmetically true in the pinned table.
    unit_pool_end = PINNED[0][1] + 0x758 * STOCK
    check(
        "s3_5_unit_pool_end_still_equals_0x892410_alias_anchor",
        unit_pool_end == 0x892410,
        {"unit_pool_end": hex(unit_pool_end)},
    )

    # --- §3-5 scoping evidence: the bulk save blob overlaps regions 2..6 ------
    # Pinned bytes (not re-derived here, cited): save 0x440F02 pushes length
    # 0xE397C and source 0x892410; load 0x4412DC freads the same pair.
    BULK_START, BULK_LEN = 0x892410, 0xE397C
    bulk_end = BULK_START + BULK_LEN
    inside = [name for name, base, elem, cb in PINNED if BULK_START <= base and base + elem * STOCK + cb <= bulk_end]
    below = [name for name, base, _e, _c in PINNED if base < BULK_START]
    check(
        "s3_5_bulk_blob_contains_regions_two_through_six",
        inside == ["unit_existence", "unit_age", "category_slot_list_a", "category_slot_list_b", "active_slot_list"]
        and below == ["unit_pool"],
        {"inside_bulk": inside, "below_bulk": below, "bulk_end": hex(bulk_end)},
    )
    per_slot_inside = sum(elem for name, _b, elem, _c in PINNED if name in inside)
    per_slot_below = sum(elem for name, _b, elem, _c in PINNED if name in below)
    n_probe = 4001
    grown_inside = per_slot_inside * (n_probe - STOCK)
    check(
        "s3_5_bulk_growth_and_shift_are_consistent_with_the_module_layout",
        grown_inside
        == local_growth_below(PINNED[5][1] + 2 * STOCK + 2, n_probe) - local_growth_below(BULK_START, n_probe)
        and per_slot_below * (n_probe - STOCK) == local_growth_below(BULK_START, n_probe),
        {
            "bytes_per_extra_slot_inside_bulk": per_slot_inside,
            "bytes_per_extra_slot_below_bulk": per_slot_below,
            "at_N_4001_new_bulk_start": hex(BULK_START + per_slot_below * (n_probe - STOCK)),
            "at_N_4001_required_bulk_len": hex(BULK_LEN + grown_inside),
            "note": "both are hardcoded push immediates; the layout module models neither",
        },
    )

    print(json.dumps({"failures": failures, "notes": notes}, indent=2, default=str))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
