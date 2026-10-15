#!/usr/bin/env python3
"""Version-specific G2 4093-slot port for official ESL 2614.

The 2614 profile reuses the audited 2610 array geometry and state/persistence
emitters, but owns its source SHA, layer-1 text replay checks, and the 2614-only
new-code gates. It never changes a legacy version pin. The official 2614 input
is immutable; callers receive candidate bytes in memory.
"""
from __future__ import annotations

import hashlib
import struct
from pathlib import Path
from typing import Any

import pefile

from patches.esl2610 import (
    g2_newcode_2610,
    g2_persist_2610,
    g2_reloc_2610,
    g2_scan,
    g2_spike_build,
    g2_state_2610,
    pe_extend,
)

OFFICIAL_SHA256 = "ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf"
OFFICIAL_EXE = "[ESL]Syw2plus 2614.exe"
STOCK_ORACLE = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"
STOCK_ORACLE_SHA256 = g2_spike_build.STOCK_SHA256
CAPACITY = g2_reloc_2610.CAPACITY
UNIT_STRIDE = g2_scan.UNIT_STRIDE

# 2614 added pool-specific code in the expanded .bldrecv payload and new
# .a16code regions. These exact operands were absent in 2613 (the corresponding
# .bldrecv bytes were not file-backed and the .a16code regions were zero).
# Each entry is (VA, old operand, new-value rule, operand kind).
POOL_END_DISP_SITES = (0x012106CA, 0x01210E67, 0x0121116F, 0x01211360,
                       0x019F03BA, 0x019F6242)
POOL_SPAN_SITES = (0x012106D0, 0x01210E6D, 0x01211175, 0x01211366)
POOL_SPAN_POSITIVE_SITES = {0x012116E3: 0x226C80}
POOL_SPAN_MINUS_STRIDE_SITES = (0x019F03C3, 0x019F6248)
POOL_BASE_MAGIC_SITES = (0x012106E1, 0x01210E84, 0x019F03D4, 0x019F625A)
POOL_END_OFFSET_SITES = {
    0x0121188F: 0x31C,
    0x019F27C7: 0x2A4,
    0x019F8624: 0x2A4,
    0x019FB144: 0x2A4,
    0x019FE6A6: 0x2A4,
}
EXIST_END_SITES_2614 = (0x019F29E2, 0x019FAC86, 0x019FE1E8)
DIV_TEST_INV = g2_newcode_2610.DIV_TEST_INV

# The two accesses below use EDI=1AB6080 from 0x19F6D4E beyond a control-flow
# boundary, which the generic bounded register-base scan deliberately stops
# before. Their exact operands are still within the pinned .r17data profile.
MANUAL_REGB_BASE_ROWS_2614 = (
    {"load_va": 0x019F6D4E, "load_old": "bf8060ab01", "base": 0x01AB6080,
     "use_va": 0x019F6DEB, "old_disp": 0x23280, "old_target": 0x01AD9300,
     "why": "EDI remains .r17data first-table base across branch; fixed grid3 target"},
    {"load_va": 0x019F6D4E, "load_old": "bf8060ab01", "base": 0x01AB6080,
     "use_va": 0x019F6E58, "old_disp": 0x12C0, "old_target": 0x01AB7340,
     "why": "EDI remains .r17data first-table base across branch; per-unit table2 target"},
)


def _state_profile_2614() -> tuple[g2_state_2610.StateSection, ...]:
    """Extend the owned .r17data state map for the 2614-only new tail."""
    old = next(sec for sec in g2_state_2610.STATE_SECTIONS if sec.name == ".r17data")
    arrays = old.arrays + (
        g2_state_2610._pu("a16_tail_u32_0", 0x01AB6080, 4),
        g2_state_2610._pu("a16_tail_u32_1", 0x01AB7340, 4),
        g2_state_2610._pu("a16_tail_u32_2", 0x01AB8600, 4),
    )
    replacement = g2_state_2610.StateSection(
        ".r17data", old.start, 0x109000, arrays, old.whole,
    )
    return tuple(replacement if sec.name == old.name else sec
                 for sec in g2_state_2610.STATE_SECTIONS)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _profile_base(data: bytes) -> None:
    digest = _sha(data)
    if digest != OFFICIAL_SHA256:
        raise ValueError(f"not the pinned official ESL2614 EXE: {digest}")
    if b".g2bss" in pe_extend.section_names(data):
        raise ValueError("G2 already applied")


def _stock(stock: bytes | None) -> bytes:
    if stock is None:
        if not STOCK_ORACLE.is_file():
            raise ValueError(f"required read-only stock oracle is missing: {STOCK_ORACLE}")
        stock = STOCK_ORACLE.read_bytes()
    if _sha(stock) != STOCK_ORACLE_SHA256:
        raise ValueError("pinned Syw2plus stock G2 oracle SHA-256 mismatch")
    return stock


def _g2bss_size(plan: Any, extra_bss: int) -> int:
    direct = sum(int(a["span_4093"], 16) for a in plan.direct_arrays)
    return plan.six_array_span + direct + extra_bss


def _section_raw(image: bytes, name: bytes) -> tuple[int, int, int]:
    pe = pefile.PE(data=image, fast_load=True)
    try:
        sec = next(s for s in pe.sections if s.Name.rstrip(b"\0") == name)
        return int(sec.PointerToRawData), int(sec.SizeOfRawData), int(sec.Misc_VirtualSize)
    finally:
        pe.close()


def _apply_layer1_2614(data: bytes, stock: bytes, *, extra_bss: int) -> tuple[bytes, dict[str, Any]]:
    """Replay only proven stock G2 .text changes after 2614 old-byte checks."""
    plan = g2_reloc_2610.plan_spike(data, require_pinned_base=False)
    image = pe_extend.compact_headers(data)
    size = _g2bss_size(plan, extra_bss)
    image = pe_extend.add_section(image, b".g2bss", b"", (size + 0xFFF) & ~0xFFF,
                                  pe_extend.BSS_RW)
    six_base = pe_extend.section_va(image, b".g2bss")
    delta = six_base - g2_spike_build.STOCK_BLOCK_LO

    from patches.population.g2_full_capacity_persistence_compat_v1 import build_candidate
    stock_candidate, stock_report = build_candidate(stock, CAPACITY)
    runs = g2_spike_build._text_runs(stock, stock_candidate)
    product_only = g2_spike_build._product_only_offsets(stock)
    text_raw, _raw_size, _vsize = _section_raw(image, b".text")
    out = bytearray(image)
    applied = rebased = bulk_rebased = product_skipped = skipped = 0
    checked = 0
    for lo, hi in runs:
        va = pe_extend.IMAGE_BASE + lo
        if any(i in product_only for i in range(lo, hi)):
            product_skipped += 1
            continue
        if va in g2_spike_build.SKIP_VAS:
            skipped += 1
            continue
        off = text_raw + (lo - g2_spike_build.TEXT_RVA)
        old = stock[lo:hi]
        if bytes(out[off:off + hi - lo]) != old:
            raise ValueError(f"2614 .text oracle preimage differs at 0x{va:08x}")
        checked += 1
        length = hi - lo
        new = bytearray(stock_candidate[lo:hi])
        if length == 4:
            dword = int.from_bytes(new, "little")
            if g2_spike_build.STOCK_BLOCK_LO <= dword < g2_spike_build.STOCK_BLOCK_HI:
                new = (dword + delta).to_bytes(4, "little")
                rebased += 1
            elif g2_spike_build.STOCK_RSRC_LO <= dword:
                skipped += 1
                continue
        elif length < 4:
            dword = int.from_bytes(stock_candidate[lo:lo + 4], "little")
            if g2_spike_build.STOCK_BLOCK_LO <= (dword + g2_spike_build.BULK_BASE) & 0xFFFFFFFF < g2_spike_build.STOCK_BLOCK_HI:
                if (stock_candidate[lo + length:lo + 4] != stock[lo + length:lo + 4]
                        or out[off + length:off + 4] != stock[lo + length:lo + 4]):
                    raise ValueError(f"2614 bulk-relative old-byte conflict at 0x{va:08x}")
                new = bytearray(((dword + delta) & 0xFFFFFFFF).to_bytes(4, "little"))
                length = 4
                bulk_rebased += 1
        out[off:off + length] = new
        applied += 1
    candidate = pe_extend._with_checksum(bytes(out))
    return candidate, {
        "status": "G2_LAYER1_STATIC_ONLY",
        "stock_oracle_sha256": _sha(stock),
        "stock_candidate_sha256": stock_report["candidate_sha256"],
        "g2bss_va": hex(six_base), "g2bss_size": hex(size), "rebase_delta": hex(delta),
        "stock_text_runs": len(runs), "text_preimages_checked": checked,
        "text_runs_applied": applied, "text_runs_skipped": skipped,
        "product_runs_skipped": product_skipped, "rebased_dwords": rebased,
        "rebased_bulk_relative_disps": bulk_rebased,
    }


def _mapped_sites(six_base: int, capacity: int) -> list[tuple[int, int, int, str, str]]:
    geo, pack = g2_reloc_2610._GEO_BY_NAME, g2_reloc_2610._PACK_BASE
    new_pool = six_base + (geo["unit_pool"].new_start - pack)
    new_exist = six_base + (geo["unit_existence"].new_start - pack)
    new_span = UNIT_STRIDE * capacity
    new_end = new_pool + new_span
    new_exist_end = new_exist + 2 * capacity
    rows: list[tuple[int, int, int, str, str]] = []
    for va in POOL_END_DISP_SITES:
        rows.append((va, (-g2_scan.POOL[1]) & 0xFFFFFFFF, (-new_end) & 0xFFFFFFFF,
                     "disp", "pool_end_relative_range"))
    for va in POOL_SPAN_SITES:
        rows.append((va, (-UNIT_STRIDE * g2_scan.STOCK_CAPACITY) & 0xFFFFFFFF,
                     (-new_span) & 0xFFFFFFFF, "imm", "pool_span_guard"))
    for va, old in POOL_SPAN_POSITIVE_SITES.items():
        rows.append((va, old, new_span, "imm", "pool_span_loop_extent"))
    for va in POOL_SPAN_MINUS_STRIDE_SITES:
        old = -(UNIT_STRIDE * (g2_scan.STOCK_CAPACITY - 1)) & 0xFFFFFFFF
        rows.append((va, old, (-(new_span - UNIT_STRIDE)) & 0xFFFFFFFF,
                     "imm", "pool_span_guard_excluding_last_slot"))
    new_magic = (-new_pool * DIV_TEST_INV) & 0xFFFFFFFF
    for va in POOL_BASE_MAGIC_SITES:
        rows.append((va, 0xCDE33D50, new_magic, "imm", "pool_pointer_divisibility_magic"))
    for va, offset in POOL_END_OFFSET_SITES.items():
        rows.append((va, g2_scan.POOL[1] + offset, new_end + offset,
                     "imm", "pool_end_field_sentinel"))
    for va in EXIST_END_SITES_2614:
        rows.append((va, g2_scan.EXIST[1], new_exist_end, "imm", "existence_end_sentinel"))
    return rows


def _bounds_decisions_2614(data: bytes) -> dict[int, dict[str, Any]]:
    """Exact .bldrecv classifications absent from the older static maps."""
    known = {
        0x01210548: ("raise", "decoded unit id range before player-record lookup", CAPACITY),
        0x0121054E: ("raise", "paired unsigned upper-bound test for decoded unit id", CAPACITY),
        0x012106D0: ("keep", "pool byte-span rewritten by the 2614 pool map", None),
        0x012107E1: ("raise", "unit id upper bound before existence/pool lookup", CAPACITY),
        0x01210DB7: ("raise", "unit id upper bound before existence/pool lookup", CAPACITY),
        0x01210E6D: ("keep", "pool byte-span rewritten by the 2614 pool map", None),
        0x01210F30: ("raise", "unit id upper bound before existence/pool lookup", CAPACITY),
        0x01211175: ("keep", "pool byte-span rewritten by the 2614 pool map", None),
        0x01211366: ("keep", "pool byte-span rewritten by the 2614 pool map", None),
        0x0121164D: ("raise", "4093-slot temporary per-unit word clear extent", CAPACITY),
        0x012116E3: ("keep", "pool byte-span loop rewritten by the 2614 pool map", None),
        0x01211705: ("keep", "fixed 180x180 terrain-grid cell stride", None),
        0x01211905: ("raise", "unit id upper bound before existence/pool lookup", CAPACITY),
    }
    # New .a16code rows classified from the 2614 control/data flow map. These
    # are profile-specific decisions; they do not alter legacy classifications.
    a16_raise = (
        0x019EE4E3, 0x019EE557, 0x019EE5F5, 0x019EE647, 0x019EE64F,
        0x019F0361, 0x019F036C, 0x019F03C3, 0x019F2FB4, 0x019F2FBD,
        0x019F510D, 0x019F5113, 0x019F61E1, 0x019F61E9, 0x019F6248,
        0x019F6358, 0x019F636F, 0x019F6409, 0x019F64F2, 0x019F667B,
        0x019F68A6, 0x019F6956, 0x019F6C4F, 0x019F6D93, 0x019F6E38,
        0x019F6F6B, 0x019F8639, 0x019F863E, 0x019F8C20, 0x019F8C26,
        0x019FA96D, 0x019FA975, 0x019FB300, 0x019FCB35, 0x019FCC46,
        0x019FCDCA, 0x019FCDD2, 0x019FE862, 0x019FF449, 0x019FF603,
    )
    a16_keep = (
        0x019F2645, 0x019F6522, 0x019F6739, 0x019F67BB, 0x019F67EF,
        0x019F6804, 0x019F6818, 0x019F682E, 0x019F6D67, 0x019F6D7B,
        0x019F700A, 0x019F700F, 0x019F70BA, 0x019F70C4, 0x019F720A,
        0x019FB8C1, 0x019FEF7E,
    )
    for va in a16_raise:
        if va in (0x019F03C3, 0x019F6248):
            known[va] = ("keep", "pool-span-minus-stride rewritten by 2614 pool map", None)
        else:
            known[va] = ("raise", "2614 per-unit ID/index gate or grown per-unit clear length", CAPACITY)
    for va in a16_keep:
        known[va] = ("keep", "fixed 180x180 grid extent/offset, not unit capacity", None)
    from patches.esl2610 import g2_bounds_2610

    found = {insn.address: (kind, value, size)
             for _name, insn, kind, value, size in g2_bounds_2610.family_operands(data)}
    missing = sorted(set(known) - set(found))
    if missing:
        raise ValueError("2614 .bldrecv bound preimage missing: "
                         + ", ".join(f"0x{x:08x}" for x in missing))
    return {
        va: {"old": found[va][1], "kind": found[va][0], "size": found[va][2],
             "decision": decision, "why": why,
             **({"capacity": cap} if cap is not None else {})}
        for va, (decision, why, cap) in known.items()
    }


def _expand_bldrecv_stack_workspace(image: bytes) -> tuple[bytes, dict[str, Any]]:
    """Expand the proven local per-unit word workspace from 1200 to 4093."""
    out = bytearray(image)
    sites = (
        (0x01211347, bytes.fromhex("81 ec 90 09 00 00"),
         bytes.fromhex("81 ec 40 20 00 00"), "sub esp,0x990 -> 0x2040"),
        (0x01211497, bytes.fromhex("81 c4 90 09 00 00"),
         bytes.fromhex("81 c4 40 20 00 00"), "add esp,0x990 -> 0x2040"),
    )
    changed = []
    for va, old, new, why in sites:
        off = pe_extend.va_to_offset(image, va)
        if bytes(out[off:off + len(old)]) != old:
            raise ValueError(f"2614 stack-frame old bytes differ at 0x{va:08x}")
        out[off:off + len(old)] = new
        changed.append({"va": hex(va), "old": old.hex(), "new": new.hex(), "why": why})
    # The array spans EBP-0x2036 through EBP-0x3c after expansion; the loop
    # clear count itself is separately transformed by g2_bounds (1200 words
    # -> 4093 words) at 0x121164D.
    g2_newcode_2610._patch_operand(out, 0x012116D3, 0xFFFFF664, 0xFFFFDFCA, kind="disp")
    changed.append({"va": "0x12116d3", "old_disp": "-0x99c", "new_disp": "-0x2036",
                    "why": "per-unit stack workspace base"})
    return pe_extend._with_checksum(bytes(out)), {"capacity": CAPACITY, "sites": changed}


def _apply_2614_coverage(image: bytes, source: bytes, six_base: int,
                         capacity: int) -> tuple[bytes, bytes, dict[str, Any]]:
    """Apply exact 2614-only operands, then reuse the audited generic layer-2 API.

    The modified source copy is only an inventory/audit view. The actual image
    receives the same exact-byte-guarded writes. Each original source preimage
    is returned in the report; source bytes on disk are never changed.
    """
    out, audit = bytearray(image), bytearray(source)
    entries = []
    for va, old, new, kind, reason in _mapped_sites(six_base, capacity):
        if old == new:
            raise ValueError(f"2614 profile map is unexpectedly no-op at 0x{va:08x}")
        old_off = pe_extend.va_to_offset(source, va)
        old_bytes = bytes(source[old_off:old_off + 16])
        g2_newcode_2610._patch_operand(out, va, old, new, kind=kind)
        g2_newcode_2610._patch_operand(audit, va, old, new, kind=kind)
        entries.append({"va": hex(va), "old_operand": hex(old), "new_operand": hex(new),
                        "kind": kind, "reason": reason, "old_instruction_bytes": old_bytes.hex()})
    return bytes(out), bytes(audit), {"count": len(entries), "sites": entries}


def _add_section(image: bytes, name: bytes, code: bytes, virtual_size: int) -> bytes:
    """Append a profile-owned code section into the compacted, four-slot table."""
    out = pe_extend.add_section(image, name, code, virtual_size, pe_extend.CODE_RX)
    return out


def build_g2_candidate(data: bytes, *, stock: bytes | None = None,
                       extra_bss: int | None = None,
                       bounds_decisions: dict[int, dict[str, Any]] | None = None,
                       state_profile: tuple[g2_state_2610.StateSection, ...] | None = None) -> tuple[bytes, dict[str, Any]]:
    """Build G2 layers 1–4 on the exact official 2614 input, fail-closed."""
    _profile_base(data)
    stock = _stock(stock)
    state_profile = _state_profile_2614() if state_profile is None else state_profile
    plan = g2_reloc_2610.plan_spike(data, require_pinned_base=False)
    direct = sum(int(a["span_4093"], 16) for a in plan.direct_arrays)
    if extra_bss is None:
        extra_bss = (g2_state_2610.block_size(state_profile=state_profile)
                     + 0x2000 + g2_persist_2610.SCRATCH_BYTES)
    l1, r1 = _apply_layer1_2614(data, stock, extra_bss=extra_bss)
    six_base = int(r1["g2bss_va"], 16)
    l1mapped, audit_source, map_report = _apply_2614_coverage(l1, data, six_base, CAPACITY)
    l2_bytes, r2 = g2_newcode_2610.apply(l1mapped, audit_source, six_base, clamp=CAPACITY)
    l2 = bytearray(l2_bytes)
    # 0x12116E3 is a positive byte-span immediate, but its numeric value
    # (1200 * 0x758) overlaps the legacy pool VA range. The generic address
    # relocator therefore treats it as a pointer and rebases it a second time.
    # Re-assert the already version-guarded profile mapping after layer 2.
    positive_span = POOL_SPAN_POSITIVE_SITES[0x012116E3]
    expected_span = UNIT_STRIDE * CAPACITY
    observed_span = g2_reloc_2610.relocate_value(expected_span, six_base)
    g2_newcode_2610._patch_operand(l2, 0x012116E3, observed_span, expected_span, kind="imm")
    profile_span_off = pe_extend.va_to_offset(l2, 0x012116E3)
    if int.from_bytes(l2[profile_span_off + 2:profile_span_off + 6], "little") != expected_span:
        raise ValueError("2614 positive pool-span loop extent failed final layer audit")
    r2["profile_operand_repairs"] = [{"va": "0x12116e3", "legacy_numeric_overlap": hex(positive_span),
                                      "intermediate_relocated_value": hex(observed_span),
                                      "final_pool_span": hex(expected_span)}]
    state_base = (six_base + g2_reloc_2610.SIX_ARRAY_SPAN + direct + 0xFFF) & ~0xFFF
    profile_decisions = _bounds_decisions_2614(data)
    if bounds_decisions:
        overlap = set(profile_decisions) & set(bounds_decisions)
        if overlap:
            raise ValueError("caller decisions conflict with pinned 2614 profile: "
                             + ", ".join(f"0x{x:08x}" for x in sorted(overlap)))
        profile_decisions.update(bounds_decisions)
    l2 = pe_extend._with_checksum(bytes(l2))
    l3, r3 = g2_state_2610.apply(l2, data, state_base,
                                 bounds_decisions=profile_decisions,
                                 state_profile=state_profile,
                                 extra_regbase_rows=MANUAL_REGB_BASE_ROWS_2614)
    l3, r3_stack = _expand_bldrecv_stack_workspace(l3)
    flag_va = (state_base + g2_state_2610.block_size(state_profile=state_profile) + 0x13) & ~3
    scratch_va = (flag_va + 0x13) & ~0xF
    g2bss_raw, _raw, g2bss_size = _section_raw(l3, b".g2bss")
    del g2bss_raw, _raw
    if scratch_va + g2_persist_2610.SCRATCH_BYTES > six_base + g2bss_size:
        raise ValueError("G2 BSS lacks room for persistence scratch")
    l4, r4 = g2_persist_2610.apply(l3, six_base, state_base, flag_va, scratch_va,
                                   state_profile=state_profile, code_reserved_size=0x1000)
    return l4, {
        "schema": "syw2plus.esl2614.g2-4093.v1",
        "input_sha256": _sha(data), "candidate_sha256": _sha(l4),
        "capacity": CAPACITY, "layers": {"g2bss_and_text": r1,
        "g2newcode_2614_map": map_report, "g2newcode_reuse": r2,
        "g2state": r3, "g2stack_workspace": r3_stack, "g2persistence": r4},
    }


def restore_candidate(candidate: bytes, original: bytes, *, stock: bytes | None = None) -> bytes:
    """Accept only this exact profile's rebuild and return the input byte-exactly."""
    expected, _ = build_g2_candidate(original, stock=stock)
    if candidate != expected:
        raise ValueError("candidate does not match the reproducible ESL2614 G2 profile")
    return original


def build_g2_g5_candidate(data: bytes, *, stock: bytes | None = None,
                          bounds_decisions: dict[int, dict[str, Any]] | None = None,
                          state_profile: tuple[g2_state_2610.StateSection, ...] | None = None
                          ) -> tuple[bytes, dict[str, Any]]:
    """Compose the 2614 G2 image with the OUR 100-capacity G5 algorithm."""
    from patches.esl2614 import g5_selection_2614

    state_profile = _state_profile_2614() if state_profile is None else state_profile
    g2_image, report = build_g2_candidate(data, stock=stock,
                                          bounds_decisions=bounds_decisions,
                                          state_profile=state_profile)
    layers = report["layers"]
    candidate, g5_report = g5_selection_2614.apply(
        g2_image, data, state_base=int(layers["g2state"]["state_base"], 16),
        scratch_va=int(layers["g2persistence"]["scratch_va"], 16),
        state_profile=state_profile)
    report["candidate_sha256"] = _sha(candidate)
    report["layers"]["g5_selection_2614"] = g5_report
    report["schema"] = "syw2plus.esl2614.g2-g5-4093-100.v1"
    return candidate, report

