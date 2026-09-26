import hashlib
import importlib.util
import sys
from pathlib import Path

import pefile
import pytest

spec = importlib.util.spec_from_file_location(
    "g2_unit_pool_expansion_v1", Path(__file__).with_name("g2_unit_pool_expansion_v1.py")
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
# N=1200 identity -- if every fixup formula truly reduces to the stock
# values at the stock capacity, the whole candidate must be byte-identical
# to the original.  This is the strongest single regression anchor: any bug
# that makes a fixup fire when it shouldn't, or computes a wrong "old"
# value, breaks this test without needing to run the game at all.
# ---------------------------------------------------------------------------


def test_n1200_candidate_is_byte_identical_to_original(original):
    patched, report = mod.build_candidate(original, mod.STOCK_CAPACITY)
    assert patched == original
    assert report["candidate_sha256"] == report["original_sha256"]


# ---------------------------------------------------------------------------
# Fixup-site inventory -- cross-checked against the independently-measured
# counts in docs/history/laps/probes/20260920_lap397_middle_g2_unit_pool_
# expansion_probe.py (A4: 986 pool disp sites) and work card W3 §B-3
# ("unit_existence(즉시2/변위32)", "unit_age(즉시3/변위2)").  A mismatch here
# means this module's independent re-scan disagrees with two prior,
# differently-implemented probes -- treated as a bug in this module, not in
# the probes, until proven otherwise.
#
# W19 (lap439/440): the pool imm count dropped from 28 to 3. lap439 found
# that 25 of those 28 "sites" were never pool addresses at all -- bit
# masks, call-argument words, a COLORREF, and (the actual W18/P2 fault root
# cause) an unrelated 50-entry table's own loop bound that happens to fall
# in [pool_base, pool_old_end) by coincidence. Only the 3 genuine
# `mov reg, pool_base` loads survive IMM_SITE_CLASSIFICATION. See
# docs/work/active/G2_IMM_FIXUP_FALSE_POSITIVE_REPAIR_LAP439.md.
# ---------------------------------------------------------------------------


def test_fixup_site_counts_match_prior_independent_probes(original):
    sites = mod.collect_fixup_sites(original)
    pool = sites["unit_pool"]
    existence = sites["unit_existence"]
    age = sites["unit_age"]
    assert sum(1 for s in pool if s.op_kind == "disp") == 986
    assert sum(1 for s in pool if s.op_kind == "imm") == 3  # W19: 28 - 25 false positives
    assert sum(1 for s in existence if s.op_kind == "disp") == 32
    assert sum(1 for s in existence if s.op_kind == "imm") == 2
    assert sum(1 for s in age if s.op_kind == "disp") == 2
    # Work card W3 §B-3 counts 3 raw age immediates; one of them (0x00442fac,
    # a B-2 site) is excluded here to avoid double-patching (see
    # B2_EXCLUDED_VAS), leaving 2 generically-fixed-up age immediates.
    assert sum(1 for s in age if s.op_kind == "imm") == 2


# lap398 originally found these two VAs by hand and hard-excluded them by
# VA (FO4_EXCLUDED_VAS). W19 (lap439/440) replaced that denylist with a
# structural rule (_classify_imm_operand): both are `cmp reg, pool_base`
# preceded by `add reg, 0x8c`, a stride that belongs to a completely
# unrelated 50-entry table, not unit_pool -- the same shape as the actual
# P2 fault root cause (0x0040F051 and 6 more siblings, also `cmp reg,
# pool_base+0x20` after `add reg, 0x8c`). This test fixes the historical
# VAs as a regression anchor without importing them from a denylist that
# no longer exists.
KNOWN_STRIDE_MISMATCH_COLLISION_VAS = frozenset({0x00421349, 0x0048F4B4})


def test_fo4_sites_excluded_from_every_region(original):
    sites = mod.collect_fixup_sites(original)
    touched_vas = {s.va for region in sites.values() for s in region}
    assert touched_vas.isdisjoint(KNOWN_STRIDE_MISMATCH_COLLISION_VAS)
    for va in KNOWN_STRIDE_MISMATCH_COLLISION_VAS:
        assert mod.IMM_SITE_CLASSIFICATION[va] == "NOT_ADDRESS"


def test_b2_sites_excluded_from_generic_region_scan(original):
    sites = mod.collect_fixup_sites(original)
    touched_vas = {s.va for region in sites.values() for s in region}
    assert touched_vas.isdisjoint(mod.B2_EXCLUDED_VAS)


# ---------------------------------------------------------------------------
# W19 (lap439/440) regression anchors -- card
# docs/work/active/G2_IMM_FIXUP_FALSE_POSITIVE_REPAIR_LAP439.md §9 requires
# both required new tests confirm re-injection (fail if the guard is
# disabled), not just pin the current (already-correct) output.
# ---------------------------------------------------------------------------


def test_0x0040f051_immediate_is_never_relocated(original):
    # This exact site (instruction `cmp ebx, 0x0066B7B0` at 0x0040F051,
    # whose 4-byte immediate operand lives at file-offset-equivalent VA
    # 0x0040F053, the address lap439's diff names) is the P2 tick-11,928
    # fault root cause: 0x0066B7B0 is the exclusive end bound of an
    # unrelated 50-entry stride-0x8c table that happens to sit inside
    # [pool_base, pool_old_end). Relocating it turned a 50-iteration loop
    # into a 75,900-iteration one, producing the corrupted values
    # (16538/22432) that crashed the game. See
    # docs/history/laps/20260921_lap439_middle_g2_w18_root_cause_imm_fixup.md.
    patched, _ = mod.build_candidate(original, 1210)
    off = 0x0040F051 - mod.IMAGE_BASE
    assert patched[off : off + 6] == original[off : off + 6]
    assert mod.IMM_SITE_CLASSIFICATION[0x0040F051] == "NOT_ADDRESS"


def test_0x800000_bitmask_immediate_is_never_relocated(original):
    # `test eax, 0x800000` (0x00401BC2, and 10 siblings) is a bit-23 flag
    # check, not an address; relocating it would silently corrupt unrelated
    # gameplay flag logic.
    patched, _ = mod.build_candidate(original, 1210)
    off = 0x00401BC2 - mod.IMAGE_BASE
    assert patched[off : off + 6] == original[off : off + 6]
    assert mod.IMM_SITE_CLASSIFICATION[0x00401BC2] == "NOT_ADDRESS"


def test_guard_disabled_reintroduces_both_regressions(original, monkeypatch):
    # Re-injection proof (lap408 W6 precedent): the two tests above must
    # not be vacuous. Force every in-range imm site to be treated as an
    # address (the pre-W19 behavior) and confirm both anchor sites DO get
    # relocated -- i.e. the guard, not some unrelated invariant, is what
    # keeps them untouched above.
    def _always_address(insns, index, insn, value, base, elem_size, classification, key):
        return "ADDRESS"

    monkeypatch.setattr(mod, "_classify_imm_operand", _always_address)
    patched, _ = mod.build_candidate(original, 1210)
    for va in (0x0040F051, 0x00401BC2):
        off = va - mod.IMAGE_BASE
        assert patched[off : off + 6] != original[off : off + 6]


# ---------------------------------------------------------------------------
# N=1210 candidate -- the actual work card capacity used by this module
# (see module docstring for why 1210, not the work card's suggested 1300).
# ---------------------------------------------------------------------------


def test_n1210_candidate_length_and_hash_are_stable(original):
    patched, report = mod.build_candidate(original, 1210)
    assert len(patched) == len(original)
    assert report["candidate_sha256"] == hashlib.sha256(patched).hexdigest()
    assert report["candidate_sha256"] != report["original_sha256"]


def test_n1210_fo4_sites_are_byte_identical_to_original(original):
    patched, _ = mod.build_candidate(original, 1210)
    for va in KNOWN_STRIDE_MISMATCH_COLLISION_VAS:
        off = va - mod.IMAGE_BASE
        assert patched[off : off + 8] == original[off : off + 8]


def test_n1210_b2_constants_take_expected_new_values(original):
    _, report = mod.build_candidate(original, 1210)
    by_va = {c["va"]: c for c in report["b2_constants"]}
    assert by_va["0x0044317d"]["new_value"] == "0x000004ba"  # N = 1210
    # -2N as an unsigned 32-bit two's complement value.
    assert by_va["0x00442fb1"]["new_value"] == f"0x{(-1210 * 2) & 0xFFFFFFFF:08x}"


def test_n1210_b3_fixup_site_counts_match_work_card_w4(original):
    # Work card W4 §3: with the pool genuinely relocated (delta != 0), the
    # applied count must be exactly this -- 0 for unit_pool is an immediate
    # FAIL per the card (it was lap399's undetected bug: base-preserving
    # delegation silently applied 0 of the collected pool fixups).
    # W19 (lap439/440): unit_pool is 989, not the pre-repair 1014 -- see
    # test_fixup_site_counts_match_prior_independent_probes.
    _, report = mod.build_candidate(original, 1210)
    assert report["b3_fixup_site_counts"] == {
        "unit_pool": 989,
        "unit_existence": 34,
        "unit_age": 4,
    }
    assert report["deltas"]["unit_pool"] != "0x00000000"


def test_n1210_original_bytes_object_is_not_mutated(original):
    before = hashlib.sha256(original).hexdigest()
    mod.build_candidate(original, 1210)
    assert hashlib.sha256(original).hexdigest() == before


def test_n1210_candidate_is_a_structurally_valid_pe(original):
    patched, _ = mod.build_candidate(original, 1210)
    pe = pefile.PE(data=patched, fast_load=True)
    try:
        assert pe.OPTIONAL_HEADER.SizeOfImage >= mod.layout(1210).size_of_image
        matches = [s for s in pe.sections if s.Name.rstrip(b"\0") == b".text"]
        assert len(matches) == 1
        # .text raw bytes must be completely untouched by the B-1 PE-header
        # stage (only .data VirtualSize / .rsrc RVAs / SizeOfImage change);
        # only specific B-2/B-3 sites inside .text may differ.
    finally:
        pe.close()


def test_n1210_candidate_actually_differs_from_original(original):
    patched, _ = mod.build_candidate(original, 1210)
    diff_offsets = [i for i in range(len(original)) if original[i] != patched[i]]
    assert len(diff_offsets) > 0


# ---------------------------------------------------------------------------
# Safety guards
# ---------------------------------------------------------------------------


def test_rejects_capacity_below_stock(original):
    with pytest.raises(ValueError):
        mod.build_candidate(original, mod.STOCK_CAPACITY - 1)


def test_rejects_wrong_original_hash():
    with pytest.raises(ValueError):
        mod.build_candidate(b"not the original exe", 1210)


def test_patch_literal_aborts_on_ambiguous_or_missing_encoding(original):
    pe = pefile.PE(data=original, fast_load=True)
    try:
        out = bytearray(original)
        with pytest.raises(mod.BuildAbortedError):
            # 0 is never a real address literal in this instruction window.
            mod._patch_literal(out, pe, 0x00442FAC, 0xDEADBEEF, 0x11111111)
    finally:
        pe.close()


