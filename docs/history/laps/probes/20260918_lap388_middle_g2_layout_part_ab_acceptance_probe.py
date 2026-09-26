#!/usr/bin/env python3
"""lap388 middle(Opus5/high) — independent re-derivation review of lap386 Part A +
lap387 Part B in `patches/population/base_preserving_storage_layout_v1.py`.

Read-only.  Launches nothing, writes nothing into the repo, never touches the
original or reference trees.  Prints one JSON report; exit 0 iff `failures` is
empty.

Method (middle tier: diagnose/confirm, do not implement).  The pinned ground
facts are transcribed *locally* here from their own sources -- the Astra
2026-09-18 major-branch decision (`g2_capacity/20260918_post_layout_major_decision.json`,
`bulk_equations`) and the lap380/lap381 structural table -- and every expected
value is recomputed from those local transcriptions.  The module under review is
imported only to read its answers, never to derive the expectation.  Section G9
first *reproduces* two plausible wrong implementations and asserts this probe
rejects them, so a green report is not vacuous.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
ORIGINAL_EXE = (
    REPO_ROOT.parent / "Syw2plus_re" / "Syw2plus" / "syw2plus_original.exe"
).resolve()
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

sys.path.insert(0, str(REPO_ROOT / "patches" / "population"))
import base_preserving_storage_layout_v1 as mod  # noqa: E402

# ---------------------------------------------------------------------------
# Locally transcribed pinned facts.  Deliberately NOT imported from the module
# under review.

IMAGE_BASE = 0x400000
STOCK = 1200

# Astra `bulk_equations`, transcribed verbatim from the decision JSON:
#   newBULKstart  = 0x892410 + 1880*d
#   newBULKlength = 0xE397C  +   14*d
#   newBULKend    = oldBULKend + 1894*d
PIN_BULK_START_1200 = 0x892410
PIN_BULK_LENGTH_1200 = 0x0E397C
PIN_BULK_END_1200 = PIN_BULK_START_1200 + PIN_BULK_LENGTH_1200  # 0x975D8C
PIN_START_RATE = 1880
PIN_LENGTH_RATE = 14
PIN_END_RATE = 1894
PIN_N4001_START = 0xD97DE8
PIN_N4001_LENGTH = 0xED2AA

# Astra: "PlayerStruct array preserves eight members and stride0x3ABC".
PIN_PS_BASE = 0x956770
PIN_PS_STRIDE = 0x3ABC
PIN_PS_COUNT = 8

# lap380/lap381 structural table: (name, base, elem_size, trailing count bytes).
PIN_REGIONS = (
    ("unit_pool", 0x0066B790, 0x758, 0),
    ("unit_existence", 0x008990C8, 2, 0),
    ("unit_age", 0x00899A28, 2, 0),
    ("category_slot_list_a", 0x0089B008, 4, 2),
    ("category_slot_list_b", 0x0089C2CA, 4, 2),
    ("active_slot_list", 0x00974FA8, 2, 2),
)

# Save site pushes the bulk source/length; load site freads the same pair.
SAVE_SITE_VA = 0x440F02
LOAD_SITE_VA = 0x4412DC
SITE_WINDOW = 0x40

SWEEP = (1200, 1201, 1500, 2400, 4001, 9601, 9904, 40000, 123457)

failures: list[str] = []
observations: dict[str, object] = {}


def check(name: str, ok: bool, detail: object = "") -> None:
    if not ok:
        failures.append(f"{name}: {detail}")


def cumulative_below(va: int, d: int) -> int:
    """Independent piecewise-linear insertion below `va`: sum of per-slot growth
    of every pinned region whose base is strictly below `va`."""
    return sum(elem * d for _n, base, elem, _c in PIN_REGIONS if base < va)


# ---------------------------------------------------------------------------
# G1 -- are `BULK_OLD_LENGTH` / the `0x892410` alias really pinned binary facts,
# or transcription?  Re-read them out of the original executable's bytes.


@dataclass(frozen=True)
class Sections:
    entries: tuple[tuple[bytes, int, int, int, int], ...]  # name, va, vsz, rp, rsz

    def va_to_off(self, va: int) -> int | None:
        rva = va - IMAGE_BASE
        for _name, sva, vsz, rp, rsz in self.entries:
            if sva <= rva < sva + max(vsz, rsz):
                local = rva - sva
                if local < rsz:
                    return rp + local
                return None
        return None


def parse_sections(data: bytes) -> Sections:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    num = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    table = pe + 24 + opt_size
    out = []
    for i in range(num):
        off = table + i * 40
        name = data[off : off + 8].rstrip(b"\0")
        vsz, va, rsz, rp = struct.unpack_from("<IIII", data, off + 8)
        out.append((name, va, vsz, rp, rsz))
    return Sections(tuple(out))


def g1_binary_ground_facts() -> None:
    if not ORIGINAL_EXE.is_file():
        failures.append("G1: pinned original executable not readable")
        return
    data = ORIGINAL_EXE.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    observations["g1_original_sha256"] = digest
    check("G1.sha", digest == ORIGINAL_SHA256, digest)
    if digest != ORIGINAL_SHA256:
        return

    sections = parse_sections(data)
    observations["g1_sections"] = [
        {"name": n.decode(), "va": hex(IMAGE_BASE + v), "raw_size": s}
        for n, v, _vs, _rp, s in sections.entries
    ]

    want_len = struct.pack("<I", PIN_BULK_LENGTH_1200)
    want_src = struct.pack("<I", PIN_BULK_START_1200)
    for label, site in (("save", SAVE_SITE_VA), ("load", LOAD_SITE_VA)):
        off = sections.va_to_off(site)
        if off is None:
            failures.append(f"G1.{label}: VA {site:#x} has no raw bytes")
            continue
        lo = max(0, off - SITE_WINDOW)
        window = data[lo : off + SITE_WINDOW]
        found_len = want_len in window
        found_src = want_src in window
        observations[f"g1_{label}_site"] = {
            "va": hex(site),
            "file_offset": hex(off),
            "window_bytes": 2 * SITE_WINDOW,
            "length_immediate_0xE397C_present": found_len,
            "address_immediate_0x892410_present": found_src,
        }
        check(
            f"G1.{label}.length_immediate",
            found_len,
            f"{PIN_BULK_LENGTH_1200:#x} not found within +/-{SITE_WINDOW:#x} of {site:#x}",
        )
        check(
            f"G1.{label}.address_immediate",
            found_src,
            f"{PIN_BULK_START_1200:#x} not found within +/-{SITE_WINDOW:#x} of {site:#x}",
        )

    # The module's two Part B constants must equal what the binary carries.
    check("G1.module_bulk_old_length", mod.BULK_OLD_LENGTH == PIN_BULK_LENGTH_1200,
          hex(mod.BULK_OLD_LENGTH))
    check("G1.module_ps_base", mod.PLAYER_STRUCT_BASE == PIN_PS_BASE, hex(mod.PLAYER_STRUCT_BASE))
    check("G1.module_ps_stride", mod.PLAYER_STRUCT_STRIDE == PIN_PS_STRIDE,
          hex(mod.PLAYER_STRUCT_STRIDE))
    check("G1.module_ps_count", mod.PLAYER_STRUCT_COUNT == PIN_PS_COUNT, mod.PLAYER_STRUCT_COUNT)

    # `0x892410` must NOT appear as a literal constant in the module source
    # (Part A contract: derived, never hardcoded).
    src = (REPO_ROOT / "patches" / "population" / "base_preserving_storage_layout_v1.py").read_text()
    code_lines = [
        ln for ln in src.splitlines()
        if "0x892410" in ln and not ln.lstrip().startswith("#")
    ]
    # docstring mentions are allowed; an assignment/expression use is not.
    offending = [ln.strip() for ln in code_lines if "=" in ln.split("#")[0] and "`" not in ln]
    observations["g1_literal_0x892410_mentions"] = len(code_lines)
    check("G1.alias_not_hardcoded", not offending, offending)


# ---------------------------------------------------------------------------
# G2/G3/G4 -- BULK start/length/end.


def g2_bulk_equations() -> None:
    rows = []
    for n in SWEEP:
        d = n - STOCK
        res = mod.layout(n)
        exp_start = PIN_BULK_START_1200 + PIN_START_RATE * d
        exp_len = PIN_BULK_LENGTH_1200 + PIN_LENGTH_RATE * d
        exp_end = PIN_BULK_END_1200 + PIN_END_RATE * d
        check(f"G2.start.n{n}", res.bulk_state_base == exp_start,
              f"{res.bulk_state_base:#x} != {exp_start:#x}")
        check(f"G2.length.n{n}", res.bulk_length == exp_len,
              f"{res.bulk_length:#x} != {exp_len:#x}")
        check(f"G2.end.n{n}", res.bulk_end == exp_end, f"{res.bulk_end:#x} != {exp_end:#x}")

        # G3 -- the two aliases must also fall out of the *general* mapper, not
        # just out of the three properties ("excluded end aliases map by
        # explicit semantics").  `0x892410` is unit_pool's exclusive end and
        # simultaneously the inclusive first byte of the gap above it; the old
        # BULK end is an address the mapper has never been told about.
        start_via_map = mod.map_va(PIN_BULK_START_1200, n)
        end_via_map = mod.map_va(PIN_BULK_END_1200, n)
        check(f"G3.start_alias.n{n}", start_via_map.new_va == res.bulk_state_base,
              f"{start_via_map.new_va} vs {res.bulk_state_base:#x}")
        check(f"G3.start_alias_is_unit_pool_exclusive_end.n{n}",
              res.regions[0].new_end == res.bulk_state_base, "")
        check(f"G3.start_alias_not_inside_unit_pool.n{n}",
              res.regions[0].new_start < res.bulk_state_base, "")
        check(f"G3.end_alias.n{n}", end_via_map.new_va == res.bulk_end,
              f"{end_via_map.new_va} vs {res.bulk_end:#x}")

        rows.append({
            "n": n,
            "bulk_start": hex(res.bulk_state_base),
            "bulk_length": hex(res.bulk_length),
            "bulk_end": hex(res.bulk_end),
        })
    observations["g2_bulk_sweep"] = rows

    # G2b -- N=1200 identity against the pinned trio.
    base = mod.layout(STOCK)
    check("G2b.identity_start", base.bulk_state_base == PIN_BULK_START_1200, hex(base.bulk_state_base))
    check("G2b.identity_length", base.bulk_length == PIN_BULK_LENGTH_1200, hex(base.bulk_length))
    check("G2b.identity_end", base.bulk_end == PIN_BULK_END_1200, hex(base.bulk_end))


def g4_n4001_byte_exact() -> None:
    res = mod.layout(4001)
    observations["g4_n4001"] = {
        "bulk_start": hex(res.bulk_state_base),
        "bulk_length": hex(res.bulk_length),
        "bulk_end": hex(res.bulk_end),
        "astra_pinned_start": hex(PIN_N4001_START),
        "astra_pinned_length": hex(PIN_N4001_LENGTH),
    }
    check("G4.start", res.bulk_state_base == PIN_N4001_START, hex(res.bulk_state_base))
    check("G4.length", res.bulk_length == PIN_N4001_LENGTH, hex(res.bulk_length))


# ---------------------------------------------------------------------------
# G5 -- PlayerStruct mapping.


def g5_player_struct() -> None:
    rows = []
    old_span = PIN_PS_COUNT * PIN_PS_STRIDE
    for n in SWEEP:
        d = n - STOCK
        ps = mod.player_struct_layout(n)
        res = mod.layout(n)
        exp_base = PIN_PS_BASE + cumulative_below(PIN_PS_BASE, d)
        check(f"G5.base.n{n}", ps.new_base == exp_base, f"{ps.new_base:#x} != {exp_base:#x}")
        check(f"G5.span_invariant.n{n}", ps.new_end - ps.new_base == old_span,
              ps.new_end - ps.new_base)
        check(f"G5.stride.n{n}", ps.stride == PIN_PS_STRIDE, hex(ps.stride))
        check(f"G5.count.n{n}", ps.count == PIN_PS_COUNT, ps.count)
        check(f"G5.fits_in_mapped_bulk.n{n}",
              res.bulk_state_base <= ps.new_base and ps.new_end <= res.bulk_end,
              f"[{ps.new_base:#x},{ps.new_end:#x}) vs [{res.bulk_state_base:#x},{res.bulk_end:#x})")
        block = mod.map_va(PIN_PS_BASE, n)
        check(f"G5.host_block.n{n}", block.block_name == "gap_after_category_slot_list_b",
              block.block_name)
        # every member start maps to base + k*stride
        for k in (0, 1, PIN_PS_COUNT - 1):
            m = mod.map_va(PIN_PS_BASE + k * PIN_PS_STRIDE, n)
            check(f"G5.member{k}.n{n}", m.new_va == ps.new_base + k * PIN_PS_STRIDE,
                  f"{m.new_va} vs {ps.new_base + k * PIN_PS_STRIDE:#x}")
        rows.append({"n": n, "new_base": hex(ps.new_base), "new_end": hex(ps.new_end),
                     "shift_per_slot": (ps.new_base - PIN_PS_BASE) // d if d else 0})
    observations["g5_player_struct"] = rows
    # The independent per-slot shift rate for PlayerStruct is 1880+2+2+4+4=1892
    # (active_slot_list sits *above* it), i.e. NOT the BULK start's 1880 and NOT
    # the BULK end's 1894.  Pin that distinction explicitly.
    rates = {r["shift_per_slot"] for r in rows if r["shift_per_slot"]}
    observations["g5_shift_rate"] = sorted(rates)
    check("G5.shift_rate_is_1892", rates == {1892}, sorted(rates))


# ---------------------------------------------------------------------------
# G6 -- the five folded sidecar regions, and unit_pool's exclusion.


def g6_sidecars() -> None:
    rows = []
    for n in SWEEP:
        res = mod.layout(n)
        inside = []
        for region in res.regions[1:]:
            ok = res.bulk_state_base <= region.new_start and region.new_end <= res.bulk_end
            check(f"G6.{region.name}.n{n}", ok,
                  f"[{region.new_start:#x},{region.new_end:#x}) escapes the mapped bulk")
            inside.append(region.name)
        check(f"G6.sidecar_count.n{n}", len(inside) == 5, inside)
        pool = res.regions[0]
        check(f"G6.unit_pool_excluded.n{n}",
              pool.new_start < res.bulk_state_base and pool.new_end == res.bulk_state_base,
              f"[{pool.new_start:#x},{pool.new_end:#x})")
        # The five per-slot element sizes must sum to Astra's 14.
        rate = sum(r.elem_size for r in res.regions[1:])
        check(f"G6.length_rate.n{n}", rate == PIN_LENGTH_RATE, rate)
        rows.append({"n": n, "sidecars": inside, "per_slot_growth": rate})
    observations["g6_sidecars"] = rows[:2]


# ---------------------------------------------------------------------------
# G7 -- mapped_offset semantics.


def g7_mapped_offset() -> None:
    n = 4001
    d = n - STOCK
    # (a) both endpoints in the same size-invariant foreign block -> identity.
    a, b = PIN_PS_BASE, PIN_PS_BASE + 3 * PIN_PS_STRIDE
    check("G7.same_block_identity", mod.mapped_offset(a, b, n) == b - a,
          mod.mapped_offset(a, b, n))
    # (b) endpoints straddling four growing regions -> naive difference is WRONG
    #     by exactly (2+2+4+4)*d.  This is what proves the function is not a
    #     naive passthrough.
    got = mod.mapped_offset(PIN_BULK_START_1200, PIN_PS_BASE, n)
    naive = PIN_PS_BASE - PIN_BULK_START_1200
    check("G7.cross_region_delta", got - naive == (2 + 2 + 4 + 4) * d, got - naive)
    observations["g7_bulk_relative_player_struct_offset"] = {
        "n": n, "naive": hex(naive), "mapped": hex(got), "correction": got - naive,
    }
    # (c) unmappable endpoints must raise, never silently return 0/identity.
    for lo, hi in ((0x401000, PIN_PS_BASE), (PIN_PS_BASE, 0x7FFFFFFF)):
        try:
            mod.mapped_offset(lo, hi, n)
        except ValueError:
            pass
        else:
            failures.append(f"G7.unmappable_not_rejected: ({lo:#x},{hi:#x})")


# ---------------------------------------------------------------------------
# G8 -- regressions the acceptance must not have broken.


def g8_regressions() -> None:
    data = ORIGINAL_EXE.read_bytes()
    identity = mod.build_layout_artifact(data, STOCK)
    check("G8.n1200_artifact_identity", identity == data, "artifact differs from original at N=1200")
    try:
        mod.build_layout_artifact(b"not the original", 4001)
    except ValueError:
        pass
    else:
        failures.append("G8.wrong_sha_not_rejected")
    try:
        mod.layout(STOCK - 1)
    except ValueError:
        pass
    else:
        failures.append("G8.shrink_not_rejected")
    check("G8.suffix_guard", mod.NON_LAUNCHABLE_SUFFIX == ".pelayout", mod.NON_LAUNCHABLE_SUFFIX)


# ---------------------------------------------------------------------------
# G9 -- falsification.  Reproduce two plausible wrong implementations and prove
# this probe's expectations reject them (a green report is then discriminating).


def g9_falsification() -> None:
    d = 4001 - STOCK
    # (i) the `regions[1:5]` transcription that appears in STATUS lap387: folds
    #     only four sidecars, dropping active_slot_list's 2 bytes/slot.
    wrong_len = PIN_BULK_LENGTH_1200 + (2 + 2 + 4 + 4) * d
    check("G9.regions_1_5_variant_is_rejected", wrong_len != PIN_N4001_LENGTH,
          "a 4-sidecar bulk_length would have matched the pin")
    # (ii) PlayerStruct base shifted at the BULK start's rate (1880) instead of
    #      its own 1892.
    wrong_base = PIN_PS_BASE + PIN_START_RATE * d
    right_base = PIN_PS_BASE + cumulative_below(PIN_PS_BASE, d)
    check("G9.ps_rate_confusion_is_detectable", wrong_base != right_base,
          "1880 and 1892 PlayerStruct rates are indistinguishable")
    observations["g9_falsification"] = {
        "four_sidecar_length_n4001": hex(wrong_len),
        "correct_length_n4001": hex(PIN_N4001_LENGTH),
        "ps_base_at_1880_rate": hex(wrong_base),
        "ps_base_at_1892_rate": hex(right_base),
    }


def main() -> int:
    g1_binary_ground_facts()
    g2_bulk_equations()
    g4_n4001_byte_exact()
    g5_player_struct()
    g6_sidecars()
    g7_mapped_offset()
    g8_regressions()
    g9_falsification()
    report = {
        "probe": "lap388_middle_g2_layout_part_ab_acceptance",
        "role": "middle(Opus5/high) independent re-derivation; read-only; no runtime",
        "module_sha256": hashlib.sha256(
            (REPO_ROOT / "patches" / "population" / "base_preserving_storage_layout_v1.py").read_bytes()
        ).hexdigest(),
        "tests_sha256": hashlib.sha256(
            (REPO_ROOT / "patches" / "population" / "test_base_preserving_storage_layout_v1.py").read_bytes()
        ).hexdigest(),
        "observations": observations,
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
