import importlib.util
import struct
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "base_preserving_storage_layout_v1", Path(__file__).with_name("base_preserving_storage_layout_v1.py")
)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original():
    if not SOURCE.exists():
        pytest.skip("Local original game required")
    return SOURCE.read_bytes()


# ---------------------------------------------------------------------------
# N=1200 identity -- the top-level regression anchor (handoff card §3.4).
# ---------------------------------------------------------------------------

# The pinned N=1200 table from
# docs/work/active/G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md §1.
PINNED_TABLE = {
    "unit_pool": (0x0066B790, 0x00892410, 0x758),
    "unit_existence": (0x008990C8, 0x00899A28, 2),
    "unit_age": (0x00899A28, 0x0089A388, 2),
    "category_slot_list_a": (0x0089B008, 0x0089C2C8, 4),
    "category_slot_list_b": (0x0089C2CA, 0x0089D58A, 4),
    "active_slot_list": (0x00974FA8, 0x00975908, 2),
}


def test_n1200_regions_match_pinned_table_byte_for_byte():
    result = mod.layout(1200)
    assert len(result.regions) == 6
    for region in result.regions:
        start, end, elem = PINNED_TABLE[region.name]
        assert region.elem_size == elem
        assert region.old_start == start == region.new_start
        # `end` in the pinned table is the array-only end (count field, if any,
        # is the immediately-following live WORD); the region's full old_end
        # folds that count in, so it must be >= the table's array-only end and
        # exactly `count_bytes` past it.
        assert region.old_end == end + region.count_bytes
        assert region.new_end == region.old_end
        assert region.delta == 0


def test_n1200_size_of_image_matches_pinned_original():
    assert mod.layout(1200).size_of_image == 0xC8F000


# ---------------------------------------------------------------------------
# §3-5 Part A: `0x892410` triple-alias exposure -- derived, never re-hardcoded.
# ---------------------------------------------------------------------------


def test_bulk_state_base_is_the_pinned_alias_at_n1200():
    assert mod.layout(1200).bulk_state_base == 0x00892410


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_bulk_state_base_shifts_by_unit_pool_growth_on_expansion(n):
    expected = 0x00892410 + 0x758 * (n - 1200)
    assert mod.layout(n).bulk_state_base == expected


@pytest.mark.parametrize("n", (1200, *mod.ENGINEERING_TEST_CAPACITIES))
def test_bulk_state_base_is_always_derived_from_unit_pool_new_end(n):
    result = mod.layout(n)
    assert result.bulk_state_base == result.regions[0].new_end
    assert result.regions[0].name == "unit_pool"


# ---------------------------------------------------------------------------
# §3-5 Part B: BULK start/end/length + PlayerStruct base/end/stride, per the
# Astra 2026-09-18 major-branch decision
# (`g2_capacity/20260918_post_layout_major_decision.json`) completing Part A
# and Part B together in this same module/tests.
# ---------------------------------------------------------------------------


def test_bulk_length_and_end_are_the_pinned_values_at_n1200():
    result = mod.layout(1200)
    assert result.bulk_length == 0x000E397C
    assert result.bulk_end == 0x00975D8C
    assert result.bulk_end == result.bulk_state_base + result.bulk_length


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_bulk_start_length_end_match_astra_pinned_equations_on_expansion(n):
    """Independent restatement of the Astra decision's pinned equations
    (`newBULKstart=0x892410+1880*d`, `newBULKlength=0xE397C+14*d`,
    `newBULKend=oldBULKend+1894*d`), not a call into the module under test --
    this is the module's *check*, not its implementation."""
    d = n - 1200
    old_bulk_end = 0x00892410 + 0x000E397C
    expected_start = 0x00892410 + 1880 * d
    expected_length = 0x000E397C + 14 * d
    expected_end = old_bulk_end + 1894 * d

    result = mod.layout(n)
    assert result.bulk_state_base == expected_start
    assert result.bulk_length == expected_length
    assert result.bulk_end == expected_end


def test_n4001_bulk_start_and_length_match_astra_decision_checks():
    result = mod.layout(4001)
    assert result.bulk_state_base == 0x00D97DE8
    assert result.bulk_length == 0x000ED2AA


@pytest.mark.parametrize("n", (1200, *mod.ENGINEERING_TEST_CAPACITIES))
def test_bulk_length_is_derived_from_the_five_regions_inside_the_blob_not_unit_pool(n):
    result = mod.layout(n)
    inside_blob = result.regions[1:]
    assert [r.name for r in inside_blob] == [
        "unit_existence",
        "unit_age",
        "category_slot_list_a",
        "category_slot_list_b",
        "active_slot_list",
    ]
    assert result.bulk_length == mod.BULK_OLD_LENGTH + sum(r.delta for r in inside_blob)


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_five_sidecar_regions_fit_inside_the_mapped_bulk_block(n):
    result = mod.layout(n)
    for region in result.regions[1:]:
        assert result.bulk_state_base <= region.new_start
        assert region.new_end <= result.bulk_end


def test_player_struct_layout_matches_pinned_base_stride_count_at_n1200():
    layout = mod.player_struct_layout(1200)
    assert layout.new_base == mod.PLAYER_STRUCT_BASE == 0x00956770
    assert layout.stride == mod.PLAYER_STRUCT_STRIDE == 0x3ABC
    assert layout.count == mod.PLAYER_STRUCT_COUNT == 8
    assert layout.new_end == layout.new_base + 8 * 0x3ABC == 0x00973D50


@pytest.mark.parametrize("n", (1200, *mod.ENGINEERING_TEST_CAPACITIES))
def test_player_struct_span_is_capacity_invariant_only_base_shifts(n):
    """PlayerStruct sits in a size-invariant foreign block -- unlike the six
    storage regions, its span must never grow with N (Astra: stride/member
    count unchanged), only its base address shifts."""
    layout = mod.player_struct_layout(n)
    assert layout.new_end - layout.new_base == 8 * 0x3ABC
    assert layout.stride == 0x3ABC
    assert layout.count == 8


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_player_struct_span_fits_inside_the_mapped_bulk_block(n):
    result = mod.layout(n)
    layout = mod.player_struct_layout(n)
    assert result.bulk_state_base <= layout.new_base
    assert layout.new_end <= result.bulk_end


@pytest.mark.parametrize("n", (1200, *mod.ENGINEERING_TEST_CAPACITIES))
def test_player_struct_layout_is_derived_via_mapped_offset_not_reused_old_span(n):
    """The base-plus-old-span shortcut happens to agree here because
    PlayerStruct's containing block shifts uniformly, but the module must
    not take that shortcut -- assert it actually used two `map_va` lookups
    by cross-checking against `mapped_offset` directly."""
    layout = mod.player_struct_layout(n)
    old_end = mod.PLAYER_STRUCT_BASE + mod.PLAYER_STRUCT_COUNT * mod.PLAYER_STRUCT_STRIDE
    offset = mod.mapped_offset(mod.PLAYER_STRUCT_BASE, old_end - 1, n)
    assert layout.new_end == layout.new_base + offset + 1


def test_mapped_offset_matches_naive_difference_inside_a_single_foreign_block():
    h1_start = 0x0089A388
    h1_probe = h1_start + 100
    n = 4001
    assert mod.mapped_offset(h1_start, h1_probe, n) == 100


def test_mapped_offset_rejects_unmappable_endpoints():
    with pytest.raises(ValueError):
        mod.mapped_offset(0x00401000, 0x0089A388, 4001)
    with pytest.raises(ValueError):
        mod.mapped_offset(0x0089A388, 0x00401000, 4001)


# lap383 R6: the only probe address below that is legitimately unmappable --
# it is one byte below unit_pool's base, i.e. outside every tracked region/
# foreign block, not a boundary this module has any basis to map. Every other
# probe below must resolve and be asserted identity; a blanket `continue` on
# any unmappable result would silently tolerate future regressions turning
# other boundaries unmappable too.
ALLOWED_UNMAPPABLE_PROBE = 0x0066B78F


@pytest.mark.parametrize(
    "region_key",
    list(PINNED_TABLE),
)
def test_n1200_map_va_is_identity_at_every_boundary_and_its_neighbors(region_key):
    start, end, _elem = PINNED_TABLE[region_key]
    for probe in (start - 1, start, start + 1, end - 1, end, end + 1):
        mapped = mod.map_va(probe, 1200)
        if mapped.kind == "unmappable":
            assert probe == ALLOWED_UNMAPPABLE_PROBE, (
                f"unexpected unmappable probe 0x{probe:X} (region {region_key}); "
                "only the below-unit_pool boundary may be unmappable"
            )
            continue
        assert mapped.new_va == probe


def test_n1200_build_layout_artifact_is_byte_identical_to_original(original):
    assert mod.build_layout_artifact(original, 1200) == original


# ---------------------------------------------------------------------------
# Expansion: non-overlap, order, monotonicity, alignment, overflow.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_expansion_regions_and_foreign_blocks_do_not_overlap_and_stay_ordered(n):
    result = mod.layout(n)
    entries = result.entries_in_address_order()
    # Old-address order must equal new-address order (no reordering) and every
    # consecutive pair must be non-overlapping and strictly increasing.
    for a, b in zip(entries, entries[1:]):
        assert a.old_end <= b.old_start
        assert a.new_end <= b.new_start
        assert a.new_start < b.new_start


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_expansion_regions_grow_by_exactly_elem_times_delta_capacity(n):
    result = mod.layout(n)
    for region in result.regions:
        expected_array_growth = region.elem_size * (n - mod.STOCK_CAPACITY)
        assert region.delta == expected_array_growth
        assert region.array_new_span - region.array_old_span == expected_array_growth


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_expansion_foreign_blocks_keep_original_size_and_relative_order(n):
    result = mod.layout(n)
    baseline = mod.layout(1200)
    assert [f.name for f in result.foreign_blocks] == [f.name for f in baseline.foreign_blocks]
    for grown, base in zip(result.foreign_blocks, baseline.foreign_blocks):
        assert grown.old_end - grown.old_start == base.old_end - base.old_start
        assert grown.new_end - grown.new_start == base.old_end - base.old_start


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_expansion_foreign_blocks_shift_by_cumulative_insertion_below_not_delta_zero(n):
    """lap381 correction: foreign blocks move by the growth *below* them; only the
    block below the lowest region (there is none -- unit_pool is the base) has a
    true delta of 0. Every foreign block here sits above at least unit_pool, so
    its `.delta` field itself (not a re-derived new_start-old_start) must track
    the accumulated region growth beneath it, not be 0 (lap383 R2: the field
    previously hardcoded 0 for every gap, reproducing the exact error lap381
    corrected -- assert the field, not a recomputation that would mask that)."""
    result = mod.layout(n)
    if n == mod.STOCK_CAPACITY:
        pytest.skip("delta is trivially 0 at the stock baseline")
    for foreign in result.foreign_blocks:
        assert foreign.delta > 0
        assert foreign.delta == foreign.new_start - foreign.old_start


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_expansion_rsrc_new_start_is_section_aligned(n):
    result = mod.layout(n)
    rsrc = result.foreign_blocks[-1]
    assert rsrc.name == "rsrc"
    assert rsrc.new_start % mod.SECTION_ALIGNMENT == 0


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_expansion_size_of_image_is_aligned_and_covers_rsrc(n):
    result = mod.layout(n)
    rsrc = result.foreign_blocks[-1]
    assert result.size_of_image % mod.SECTION_ALIGNMENT == 0
    assert mod.IMAGE_BASE + result.size_of_image >= rsrc.new_end


def test_layout_rejects_non_positive_capacity():
    with pytest.raises(ValueError):
        mod.layout(0)
    with pytest.raises(ValueError):
        mod.layout(-1)


def test_layout_rejects_shrink_below_stock_capacity():
    """lap383 R1: n < STOCK_CAPACITY must be rejected outright, not silently
    accepted with a negative running_delta that maps a discarded slot's address
    outside its own region."""
    with pytest.raises(ValueError, match="STOCK_CAPACITY"):
        mod.layout(mod.STOCK_CAPACITY - 1)


def test_map_va_rejects_shrink_instead_of_silently_mapping_outside_its_region():
    """lap383 R1 measured regression: map_va(unit_pool.base + 0x758*1199, 1199)
    used to return kind="region", new_va=0x891CB8 -- a live address inside
    gap_after_active_slot_list, a *different* foreign block entirely."""
    stray = 0x0066B790 + 0x758 * 1199
    with pytest.raises(ValueError, match="STOCK_CAPACITY"):
        mod.map_va(stray, 1199)


def test_layout_rejects_32bit_overflow():
    with pytest.raises(OverflowError):
        mod.layout(2**31)


def test_layout_va_guard_boundary_is_the_true_32bit_limit():
    """lap383 R3 measured regression: the old guard compared rsrc.new_end
    against IMAGE_BASE + 2**32 instead of 2**32, so N=2,259,703 (rsrc.new_end
    == 0x1000000F0, which is > 2**32) was silently accepted."""
    mod.layout(2_259_702)  # rsrc.new_end == 0xFFFFF0F0 < 2**32 -- must not raise
    with pytest.raises(OverflowError):
        mod.layout(2_259_703)  # rsrc.new_end == 0x1000000F0 -- must raise


# ---------------------------------------------------------------------------
# map_va: three explicit categories, never a silent identity/zero fallback.
# ---------------------------------------------------------------------------


def test_map_va_below_unit_pool_is_unmappable_not_identity():
    mapped = mod.map_va(0x00401000, 4001)  # deep inside .text, far below unit_pool
    assert mapped.kind == "unmappable"
    assert mapped.new_va is None


def test_map_va_past_rsrc_end_is_unmappable():
    end_of_rsrc = mod.RSRC_BASE_VA + mod.RSRC_SIZE
    mapped = mod.map_va(end_of_rsrc, 4001)
    assert mapped.kind == "unmappable"
    assert mapped.new_va is None


def test_map_va_inside_h1_foreign_block_shifts_by_growth_below_it():
    h1_start = 0x0089A388  # unit_age end, per the pinned table
    mapped = mod.map_va(h1_start, 4001)
    assert mapped.kind == "foreign"
    regions = mod.layout(4001).regions
    growth_below = sum(r.delta for r in regions if r.old_start < h1_start)
    assert mapped.new_va == h1_start + growth_below


def test_map_va_inside_active_slot_count_field_uses_new_array_span():
    n = 4001
    array_end = 0x00974FA8 + 2 * mod.STOCK_CAPACITY  # old array-only end (before the trailing count)
    mapped = mod.map_va(array_end, n)
    assert mapped.kind == "region"
    assert mapped.block_name == "active_slot_list"
    region = next(r for r in mod.layout(n).regions if r.name == "active_slot_list")
    assert mapped.new_va == region.new_start + region.array_new_span


# ---------------------------------------------------------------------------
# SHA pin, read-only-original, and artifact geometry.
# ---------------------------------------------------------------------------


def test_verify_original_rejects_wrong_sha():
    with pytest.raises(ValueError, match="SHA256"):
        mod.verify_original(b"not the pinned original")


def test_build_layout_artifact_rejects_wrong_sha():
    with pytest.raises(ValueError, match="SHA256"):
        mod.build_layout_artifact(b"not the pinned original", 4001)


def test_build_layout_artifact_does_not_mutate_or_resize_input(original):
    before = bytes(original)
    artifact = mod.build_layout_artifact(original, 4001)
    assert original == before  # caller's bytes object is untouched
    assert len(artifact) == len(original)  # no raw bytes move -- pure header/table edit


@pytest.mark.parametrize("n", mod.ENGINEERING_TEST_CAPACITIES)
def test_build_layout_artifact_only_changes_documented_fields(original, n):
    artifact = mod.build_layout_artifact(original, n)
    result = mod.layout(n)
    pe_off = struct.unpack_from("<I", original, 0x3C)[0]
    opt = pe_off + 24
    opt_header_size = struct.unpack_from("<H", original, pe_off + 20)[0]
    num_sections = struct.unpack_from("<H", original, pe_off + 6)[0]
    section_table = pe_off + 24 + opt_header_size

    allowed: set[int] = set()
    allowed.update(range(opt + 56, opt + 60))  # SizeOfImage
    allowed.update(range(opt + 96 + 2 * 8, opt + 96 + 3 * 8))  # resource data directory
    for i in range(num_sections):
        name, off, _vsz, _va, _rsz, _rp = mod._read_section(original, section_table, i)
        if name == b".data":
            allowed.update(range(off + 8, off + 12))  # VirtualSize
        elif name == b".rsrc":
            allowed.update(range(off + 12, off + 16))  # VirtualAddress
    for local_offset in mod.PAYLOAD_ENTRY_OFFSETS:
        allowed.update(range(mod.RSRC_RAW_POINTER + local_offset, mod.RSRC_RAW_POINTER + local_offset + 4))

    changed = {i for i, (a, b) in enumerate(zip(original, artifact)) if a != b}
    assert changed <= allowed, f"unexpected byte changes outside the documented fields: {sorted(changed - allowed)}"

    if n != mod.STOCK_CAPACITY:
        assert changed, "expansion must change at least the documented header fields"
    rsrc = result.foreign_blocks[-1]
    assert rsrc.name == "rsrc"


def test_write_layout_artifact_requires_reserved_suffix(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    with pytest.raises(ValueError, match=r"\.pelayout"):
        mod.write_layout_artifact(source, tmp_path / "candidate.exe", 4001)
    assert source.read_bytes() == original


def test_write_layout_artifact_refuses_to_overwrite_source(original, tmp_path):
    # Reserved-suffix source so the suffix guard doesn't preempt the overwrite guard.
    source = tmp_path / "input.exe.pelayout"
    source.write_bytes(original)
    with pytest.raises(ValueError, match="overwrite"):
        mod.write_layout_artifact(source, source, 4001)


def test_write_layout_artifact_refuses_to_shadow_original_exe_name(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    shadow = tmp_path / "syw2plus_original.exe.pelayout"
    with pytest.raises(ValueError, match="shadow"):
        mod.write_layout_artifact(source, shadow, 4001)


def test_write_layout_artifact_writes_isolated_non_launchable_file(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    destination = tmp_path / "g2_layout_probe_n4001.pelayout"
    digest = mod.write_layout_artifact(source, destination, 4001)
    assert destination.read_bytes() == mod.build_layout_artifact(original, 4001)
    assert source.read_bytes() == original  # source untouched
    import hashlib

    assert digest == hashlib.sha256(destination.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# canonical/legacy launcher rejection before Popen.
# ---------------------------------------------------------------------------


def test_expanded_artifact_is_actually_rejected_by_the_repo_launcher_entrypoint_with_zero_popen(
    original, tmp_path, monkeypatch
):
    """lap383 R5: the previous version of this test only compared SHA constants
    -- it never called into tools/runtime_env.py at all, so it was not evidence
    that a real launch-path entrypoint rejects an expanded artifact. This
    version calls `runtime_env.validate_original_source`, the actual gate every
    `prepare`/`check_runtime` launch path runs first, against a source
    directory whose `syw2plus_original.exe` is our expanded artifact, and
    asserts it raises RuntimeSafetyError (SHA mismatch) with subprocess.Popen
    invoked zero times -- a real rejection-before-Popen observation, not a
    constant comparison. (validate_original_source itself never touches
    subprocess; the zero-Popen assertion guards against a future edit adding
    one before the SHA check.)"""
    import subprocess as _subprocess
    import sys as _sys

    popen_calls: list[object] = []

    def _record_popen(*args: object, **kwargs: object) -> None:
        popen_calls.append((args, kwargs))
        raise AssertionError("Popen must not be called by validate_original_source")

    monkeypatch.setattr(_subprocess, "Popen", _record_popen)

    tools_dir = Path(__file__).resolve().parents[2] / "tools"
    spec = importlib.util.spec_from_file_location("runtime_env_pin_check", tools_dir / "runtime_env.py")
    assert spec is not None and spec.loader is not None
    runtime_env = importlib.util.module_from_spec(spec)
    _sys.modules[spec.name] = runtime_env
    spec.loader.exec_module(runtime_env)

    assert runtime_env.ORIGINAL_SHA256 == mod.ORIGINAL_SHA256

    fake_source = tmp_path / "expanded_source"
    fake_source.mkdir()
    artifact = mod.build_layout_artifact(original, 4001)
    (fake_source / runtime_env.ORIGINAL_EXE).write_bytes(artifact)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="SHA-256 mismatch"):
        runtime_env.validate_original_source(fake_source)

    assert popen_calls == []


def test_stock_capacity_artifact_still_satisfies_the_launcher_pin(original):
    """The flip side of the identity anchor: at N=1200 the artifact is
    byte-identical to the pinned original, so (unlike an expansion) it is not
    itself rejected by the SHA gate -- this module makes no claim that a
    no-op layout call produces something non-launchable."""
    artifact = mod.build_layout_artifact(original, mod.STOCK_CAPACITY)
    import hashlib

    assert hashlib.sha256(artifact).hexdigest() == mod.ORIGINAL_SHA256
