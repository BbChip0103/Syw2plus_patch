#!/usr/bin/env python3
"""lap383 middle(Opus5/high) — independent review probe for lap382's
`patches/population/base_preserving_storage_layout_v1.py`.

READ-ONLY.  Writes nothing except its own stdout.  Does not launch the game,
does not modify the original EXE, does not touch frozen pins.

Purpose: STATUS "다음 한 가지" §4 asks the middle tier to adjudicate lap382's
module WITHOUT reusing the author's own arithmetic/hash self-proof.  So this
probe re-derives the PE facts by walking the original EXE itself and then
exercises the module against those independently derived facts.

Every check prints EXPECT/ACTUAL.  `failures` is the verdict; rc!=0 means at
least one independent check disagreed with the module or with lap382's record.
"""

from __future__ import annotations

import hashlib
import importlib.util
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
ORIGINAL = REPO / "Syw2plus/syw2plus_original.exe"
MODULE = REPO / "patches/population/base_preserving_storage_layout_v1.py"

PINNED_ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
LAP382_MODULE_SHA = "278a00135f9a0b9e7dc2774d9fb0a4d0b16033ca96f678ea84fed32af6ba3a65"

failures: list[str] = []
notes: list[str] = []


def check(name: str, ok: bool, expect: object, actual: object) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}\n        expect={expect!r}\n        actual={actual!r}")
    if not ok:
        failures.append(name)


def note(name: str, detail: object) -> None:
    print(f"[NOTE] {name}: {detail}")
    notes.append(f"{name}: {detail}")


# ---------------------------------------------------------------------------
# 0. provenance
# ---------------------------------------------------------------------------
data = ORIGINAL.read_bytes()
check(
    "original_sha_matches_protected_pin",
    hashlib.sha256(data).hexdigest() == PINNED_ORIGINAL_SHA,
    PINNED_ORIGINAL_SHA,
    hashlib.sha256(data).hexdigest(),
)
module_sha = hashlib.sha256(MODULE.read_bytes()).hexdigest()
check("module_sha_matches_lap382_record", module_sha == LAP382_MODULE_SHA, LAP382_MODULE_SHA, module_sha)

spec = importlib.util.spec_from_file_location("bpsl_under_review", MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

IMAGE_BASE = 0x400000

# ---------------------------------------------------------------------------
# 1. independent PE header / section walk (NOT reusing module constants)
# ---------------------------------------------------------------------------
pe = struct.unpack_from("<I", data, 0x3C)[0]
num_sections = struct.unpack_from("<H", data, pe + 6)[0]
opt_size = struct.unpack_from("<H", data, pe + 20)[0]
opt = pe + 24
section_table = opt + opt_size
size_of_image = struct.unpack_from("<I", data, opt + 56)[0]
sect: dict[bytes, dict[str, int]] = {}
for i in range(num_sections):
    off = section_table + i * 40
    nm = data[off : off + 8].rstrip(b"\0")
    vsz, va, rsz, rp = struct.unpack_from("<IIII", data, off + 8)
    sect[nm] = {"off": off, "vsz": vsz, "va": va, "rsz": rsz, "rp": rp}

check("independent_size_of_image", size_of_image == 0xC8F000, 0xC8F000, hex(size_of_image))
rsrc = sect[b".rsrc"]
dat = sect[b".data"]
check(
    "independent_rsrc_base_va_matches_module_constant",
    IMAGE_BASE + rsrc["va"] == mod.RSRC_BASE_VA,
    hex(mod.RSRC_BASE_VA),
    hex(IMAGE_BASE + rsrc["va"]),
)
check(
    "independent_rsrc_raw_pointer_matches_module_constant",
    rsrc["rp"] == mod.RSRC_RAW_POINTER,
    hex(mod.RSRC_RAW_POINTER),
    hex(rsrc["rp"]),
)
check("independent_rsrc_vsize_matches_module_constant", rsrc["vsz"] == mod.RSRC_SIZE, hex(mod.RSRC_SIZE), hex(rsrc["vsz"]))

# .data coverage of the tail: does .data's declared VirtualSize actually span
# the six regions at N=1200?  The module only guards against overlapping
# `.rsrc`; it never checks that `.data` still *covers* the grown tail.
data_end_va = IMAGE_BASE + dat["va"] + dat["vsz"]
active_end_va = 0x00974FA8 + 2 * 1200 + 2
check(
    "stock_data_vsize_covers_last_region_end",
    data_end_va >= active_end_va,
    f">= {hex(active_end_va)}",
    hex(data_end_va),
)
note("stock_data_slack_below_rsrc", hex(IMAGE_BASE + rsrc["va"] - data_end_va))

# ---------------------------------------------------------------------------
# 2. independent resource-directory walk -> the 9 payload OffsetToData offsets
#    (module hardcodes PAYLOAD_ENTRY_OFFSETS; re-derive them by tree walk)
# ---------------------------------------------------------------------------
found: list[int] = []


def walk(dir_local: int, depth: int) -> None:
    n_named, n_id = struct.unpack_from("<HH", data, rsrc["rp"] + dir_local + 12)
    for k in range(n_named + n_id):
        ent = rsrc["rp"] + dir_local + 16 + k * 8
        _name, off_to = struct.unpack_from("<II", data, ent)
        if off_to & 0x80000000:
            walk(off_to & 0x7FFFFFFF, depth + 1)
        else:
            found.append(off_to)  # local offset of IMAGE_RESOURCE_DATA_ENTRY


walk(0, 0)
found.sort()
check(
    "independent_resource_leaf_count_is_9",
    len(found) == 9,
    9,
    len(found),
)
check(
    "independent_leaf_offsets_match_module_PAYLOAD_ENTRY_OFFSETS",
    tuple(found) == tuple(mod.PAYLOAD_ENTRY_OFFSETS),
    tuple(hex(v) for v in mod.PAYLOAD_ENTRY_OFFSETS),
    tuple(hex(v) for v in found),
)
# and each leaf's OffsetToData must be an RVA inside .rsrc at stock
for lo in found:
    rva = struct.unpack_from("<I", data, rsrc["rp"] + lo)[0]
    if not (rsrc["va"] <= rva < rsrc["va"] + rsrc["vsz"]):
        check(f"leaf_rva_inside_rsrc@{hex(lo)}", False, "inside .rsrc", hex(rva))

# ---------------------------------------------------------------------------
# 3. N=1200 identity, independently
# ---------------------------------------------------------------------------
artifact_1200 = mod.build_layout_artifact(data, 1200)
check("n1200_artifact_byte_identical", artifact_1200 == data, "identical", "identical" if artifact_1200 == data else "DIFFERS")
check("original_file_unmodified_after_build", hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == PINNED_ORIGINAL_SHA, PINNED_ORIGINAL_SHA, "recomputed")

# ---------------------------------------------------------------------------
# 4. OBSERVATION A — ForeignLayout.delta semantics
#    lap381 correction says a foreign block's delta is NOT 0.  The module
#    stores delta=0 for every derived gap (incl. the H1 matrix) while storing
#    an *address shift* in the same field for `.rsrc`.
# ---------------------------------------------------------------------------
r4001 = mod.layout(4001)
gap_deltas = {f.name: f.delta for f in r4001.foreign_blocks}
gap_shifts = {f.name: f.new_start - f.old_start for f in r4001.foreign_blocks}
note("foreign_delta_field_values(N=4001)", gap_deltas)
note("foreign_true_address_shift(N=4001)", gap_shifts)
mismatched = [n for n in gap_deltas if gap_deltas[n] != gap_shifts[n]]
check(
    "foreign_delta_field_equals_true_address_shift",
    not mismatched,
    "delta == new_start-old_start for every foreign block",
    f"mismatch in {mismatched}",
)
region_delta_is_span_growth = all(
    r.delta == r.array_new_span - r.array_old_span for r in r4001.regions
)
note(
    "delta_field_is_overloaded",
    f"RegionLayout.delta=span-growth({region_delta_is_span_growth}), "
    f"ForeignLayout(gap).delta=0, ForeignLayout(rsrc).delta=address-shift",
)

# ---------------------------------------------------------------------------
# 5. OBSERVATION B — 32-bit VA guard uses IMAGE_BASE + 2**32
# ---------------------------------------------------------------------------
lo, hi = 1200, 1 << 31
while lo < hi:  # smallest N whose rsrc.new_end reaches 2**32
    mid = (lo + hi) // 2
    try:
        res = mod.layout(mid)
        reached = res.foreign_blocks[-1].new_end >= 2**32
    except OverflowError:
        reached = True
    if reached:
        hi = mid
    else:
        lo = mid + 1
n_over = lo
try:
    res_over = mod.layout(n_over)
    accepted_end = res_over.foreign_blocks[-1].new_end
    guard_ok = False
except OverflowError:
    accepted_end = None
    guard_ok = True
check(
    "va_guard_rejects_first_N_whose_new_end_reaches_2**32",
    guard_ok,
    f"OverflowError at N={n_over}",
    f"accepted, rsrc.new_end={hex(accepted_end) if accepted_end else None} (>= 2**32)",
)
note("first_N_reaching_2**32_rsrc_end", n_over)

# ---------------------------------------------------------------------------
# 6. OBSERVATION C — N < 1200 (shrink) silently maps discarded slots outside
#    their own new region, possibly into the next block.
# ---------------------------------------------------------------------------
n_small = 100
res_small = mod.layout(n_small)
pool = res_small.regions[0]
discarded_va = 0x0066B790 + 0x758 * 1199  # last stock slot, discarded at N=100
m = mod.map_va(discarded_va, n_small)
inside_own_region = m.new_va is not None and pool.new_start <= m.new_va < pool.new_end
landed_in: list[str] = []
for e in res_small.entries_in_address_order():
    if m.new_va is not None and e.new_start <= m.new_va < e.new_end:
        landed_in.append(e.name)
check(
    "shrink_discarded_slot_is_not_silently_mapped_outside_its_region",
    m.kind == "unmappable" or inside_own_region,
    "kind=='unmappable' or new_va inside unit_pool's new range",
    f"kind={m.kind}, new_va={hex(m.new_va) if m.new_va else None}, "
    f"unit_pool_new=[{hex(pool.new_start)},{hex(pool.new_end)}), lands_in={landed_in}",
)
check(
    "shrink_layout_is_rejected_outright",
    False if res_small.capacity == n_small else True,
    "layout(n<STOCK_CAPACITY) raises (module is an expansion mapper)",
    f"accepted, capacity={res_small.capacity}",
)

# ---------------------------------------------------------------------------
# 7. OBSERVATION D — ±1 identity anchor vs the unmappable policy
#    The lap382 test `continue`s whenever kind=='unmappable', so the anchor
#    silently skips those probes.  Count how many of the 36 probes are skipped.
# ---------------------------------------------------------------------------
PINNED_TABLE = {
    "unit_pool": (0x0066B790, 0x00892410),
    "unit_existence": (0x008990C8, 0x00899A28),
    "unit_age": (0x00899A28, 0x0089A388),
    "category_slot_list_a": (0x0089B008, 0x0089C2C8),
    "category_slot_list_b": (0x0089C2CA, 0x0089D58A),
    "active_slot_list": (0x00974FA8, 0x00975908),
}
skipped: list[str] = []
broken: list[str] = []
for nm, (s, e) in PINNED_TABLE.items():
    for probe in (s - 1, s, s + 1, e - 1, e, e + 1):
        mm = mod.map_va(probe, 1200)
        if mm.kind == "unmappable":
            skipped.append(f"{nm}@{hex(probe)}")
        elif mm.new_va != probe:
            broken.append(f"{nm}@{hex(probe)}->{hex(mm.new_va)}")
check("n1200_identity_holds_for_every_mapped_boundary_probe", not broken, "no identity break", broken)
note("n1200_identity_probes_skipped_as_unmappable", skipped or "none")

# ---------------------------------------------------------------------------
# 8. OBSERVATION E — expansion coverage of `.data` VirtualSize
#    Independently recompute the artifact's .data VirtualSize and check it
#    still covers the grown tail (the module only checks .rsrc non-overlap).
# ---------------------------------------------------------------------------
for n in mod.ENGINEERING_TEST_CAPACITIES:
    art = mod.build_layout_artifact(data, n)
    res = mod.layout(n)
    new_vsz = struct.unpack_from("<I", art, dat["off"] + 8)[0]
    new_rsrc_rva = struct.unpack_from("<I", art, rsrc["off"] + 12)[0]
    new_soi = struct.unpack_from("<I", art, opt + 56)[0]
    last_region_end = max(r.new_end for r in res.regions)
    covered = IMAGE_BASE + dat["va"] + new_vsz >= last_region_end
    check(
        f"expanded_data_vsize_covers_grown_tail(N={n})",
        covered,
        f">= {hex(last_region_end)}",
        hex(IMAGE_BASE + dat["va"] + new_vsz),
    )
    check(
        f"expanded_data_does_not_overlap_rsrc(N={n})",
        dat["va"] + new_vsz <= new_rsrc_rva,
        f"<= {hex(new_rsrc_rva)}",
        hex(dat["va"] + new_vsz),
    )
    check(
        f"expanded_soi_covers_rsrc_end(N={n})",
        IMAGE_BASE + new_soi >= res.foreign_blocks[-1].new_end,
        f">= {hex(res.foreign_blocks[-1].new_end)}",
        hex(IMAGE_BASE + new_soi),
    )
    # independent byte-diff: only documented fields may differ
    allowed: set[int] = set()
    allowed.update(range(opt + 56, opt + 60))
    allowed.update(range(opt + 96 + 2 * 8, opt + 96 + 3 * 8))
    allowed.update(range(dat["off"] + 8, dat["off"] + 12))
    allowed.update(range(rsrc["off"] + 12, rsrc["off"] + 16))
    for lo_ in found:  # independently derived leaf offsets, not module constants
        allowed.update(range(rsrc["rp"] + lo_, rsrc["rp"] + lo_ + 4))
    changed = {i for i, (a, b) in enumerate(zip(data, art)) if a != b}
    check(
        f"expanded_artifact_changes_only_independently_derived_fields(N={n})",
        changed <= allowed,
        "subset of independently derived field byte-ranges",
        sorted(changed - allowed)[:12],
    )

# ---------------------------------------------------------------------------
# 9. OBSERVATION F — bulk/PlayerStruct/count alias reporting (plan §3 point 5)
#    Does the module expose the three-name alias 0x892410 or any bulk-relative
#    derivation at all?  Grep its public surface.
# ---------------------------------------------------------------------------
src = MODULE.read_text()
for token in ("0x892410", "0x00892410", "bulk", "PlayerStruct", "player_struct"):
    note(f"module_mentions[{token}]", token.lower() in src.lower())
exported = sorted(k for k in vars(mod) if not k.startswith("_"))
note("module_public_surface", exported)

# ---------------------------------------------------------------------------
# 10. OBSERVATION G — launcher rejection is a SHA comparison, not a call
# ---------------------------------------------------------------------------
# NB: a plain substring grep gives a FALSE PASS here -- the lap382 test's
# docstring itself narrates "subprocess.Popen".  Parse the AST and look at
# actual call expressions only.
import ast

test_src = (REPO / "patches/population/test_base_preserving_storage_layout_v1.py").read_text()
called_names: set[str] = set()
for node in ast.walk(ast.parse(test_src)):
    if isinstance(node, ast.Call):
        fn = node.func
        if isinstance(fn, ast.Name):
            called_names.add(fn.id)
        elif isinstance(fn, ast.Attribute):
            called_names.add(fn.attr)
note("launcher_test_actual_call_names", sorted(called_names))
calls_launcher = bool(called_names & {"check_runtime", "prepare", "Popen", "run", "launch"})
check(
    "launcher_rejection_test_actually_invokes_a_launcher_entrypoint",
    calls_launcher,
    "test calls check_runtime/prepare (or a mock launcher) and observes the refusal",
    "test only compares ORIGINAL_SHA256 constants and artifact digests",
)

# ---------------------------------------------------------------------------
# 11. deliverable: private `.pelayout` + deterministic mapping under temp
# ---------------------------------------------------------------------------
temp_root = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch")
pelayouts = list(temp_root.rglob("*.pelayout")) if temp_root.exists() else []
check(
    "private_pelayout_artifact_preserved_under_designated_temp",
    bool(pelayouts),
    "at least one .pelayout under temp/Syw2plus_patch",
    [str(p) for p in pelayouts],
)

print()
print(f"failures={failures}")
print(f"note_count={len(notes)}")
sys.exit(1 if failures else 0)
