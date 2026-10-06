import hashlib
import importlib.util
import sys
from pathlib import Path

import capstone
import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v5.py")
spec = importlib.util.spec_from_file_location(MODULE.stem, MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"
EXPECTED_CANDIDATE_SHA256 = "29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146"


@pytest.fixture
def original() -> bytes:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    return SOURCE.read_bytes()


def test_build_is_deterministic_and_matches_pinned_sha(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    assert len(candidate) == len(original)
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] == EXPECTED_CANDIDATE_SHA256


def test_cave_fits_within_limit(original: bytes) -> None:
    _candidate, report = mod.build_candidate(original)
    cave_end = int(report["hook"]["cave_end_exclusive"], 16)
    assert cave_end <= mod.CAVE_LIMIT


def _decode_gate(candidate: bytes, report: dict) -> list[capstone.CsInsn]:
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        gate_off = mod._va_to_file_offset(pe, mod.CAVE_BASE)
        body_addr = int(report["hook"]["body_addr"], 16)
        data = candidate[gate_off : gate_off + (body_addr - mod.CAVE_BASE)]
    finally:
        pe.close()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    return list(md.disasm(data, mod.CAVE_BASE))


def _symbolic_gate(candidate: bytes, report: dict, other_mod) -> list[tuple[str, str]]:
    """The order-type gate as (mnemonic, operand) pairs with any jump target
    resolved to ``"original_body"``/``"check_count"`` instead of a raw
    address -- both labels legitimately land at different absolute addresses
    between v4 and v5 (v5's check_count block is longer), so only the
    resolved-symbol sequence, not the raw bytes, is comparable across them.
    """
    insns = _decode_gate(candidate, report)
    check_count_idx = next(
        i for i, insn in enumerate(insns)
        if insn.mnemonic == "movzx" and hex(other_mod.SELECTION_BASE) in insn.op_str
    )
    body_addr = int(report["hook"]["body_addr"], 16)
    check_count_addr = insns[check_count_idx].address
    out = []
    for insn in insns[:check_count_idx]:
        op = insn.op_str
        if op == hex(body_addr):
            op = "original_body"
        elif op == hex(check_count_addr):
            op = "check_count"
        out.append((insn.mnemonic, op))
    return out


def test_order_type_gate_structure_unchanged_from_v4(original: bytes) -> None:
    """v5 only widens ``check_count``; the leading order-type gate (v4's
    inverted lap676 non-order allow-list) must stay the same sequence of
    comparisons/branches into ``original_body``/``check_count`` -- the raw
    encoded bytes legitimately differ because v5's longer check_count block
    moves ``original_body`` further away, changing jump displacement sizes.
    """
    from patches.selection import g5_selection_cap50_v4 as v4

    v5_candidate, v5_report = mod.build_candidate(original)
    v4_candidate, v4_report = v4.build_candidate(original)
    assert _symbolic_gate(v5_candidate, v5_report, mod) == _symbolic_gate(v4_candidate, v4_report, v4)


def test_sparse_scan_covers_exactly_entries_20_to_49(original: bytes) -> None:
    """Structural regression for the R3 fix: the widened gate must scan a
    30-dword window starting at ``entries[20]`` (``CHUNK1_OFFSET``) -- i.e.
    exactly ``entries[20:50]`` -- before it is willing to fall through to the
    original unchunked body, and a live count > 20 must still go straight to
    the chunk-building path without running the scan at all.
    """
    candidate, report = mod.build_candidate(original)
    insns = _decode_gate(candidate, report)
    check_count_idx = next(
        i for i, insn in enumerate(insns)
        if insn.mnemonic == "movzx" and hex(mod.SELECTION_BASE) in insn.op_str
    )
    tail = insns[check_count_idx:]

    # movzx eax,[SELECTION_BASE]; cmp eax,20; jg <do_chunk>
    assert tail[1].mnemonic == "cmp" and tail[1].op_str.endswith(f"0x{mod.CHUNK_UNITS:x}")
    assert tail[2].mnemonic == "jg"
    do_chunk_addr = int(tail[2].op_str, 16)

    # mov esi, CHUNK1_OFFSET; mov ecx, 30 (entries[20:50])
    mov_esi = next(i for i in tail if i.mnemonic == "mov" and i.op_str.startswith("esi,"))
    mov_ecx = next(i for i in tail if i.mnemonic == "mov" and i.op_str.startswith("ecx,"))
    assert mov_esi.op_str == f"esi, {hex(mod.CHUNK1_OFFSET)}"
    assert mov_ecx.op_str == f"ecx, {hex(mod.SPARSE_SCAN_UNITS)}"
    assert mod.CHUNK1_OFFSET + mod.SPARSE_SCAN_UNITS * 4 == mod.ENTRIES + mod.TARGET_CAPACITY * 4

    # the "no live tail slot" exit must jmp to original_body, not do_chunk.
    jmp_original = [i for i in tail if i.mnemonic == "jmp"]
    assert len(jmp_original) == 1
    assert jmp_original[0].op_str != hex(do_chunk_addr)

    # do_chunk (count > 20) is reached without touching esi/ecx (no push/pop
    # of them precedes it on that path) -- the very next instruction group
    # after the jg target is the existing chunk-building prologue.
    do_chunk_insn = next(i for i in insns if i.address == do_chunk_addr)
    assert do_chunk_insn.mnemonic == "push" and do_chunk_insn.op_str == "ebp"


def test_chunk_and_restore_body_matches_v4_modulo_relocation(original: bytes) -> None:
    """Everything from ``do_chunk`` (the pre-existing chunk-building
    prologue) through the relocated original body must be unchanged from
    v4 -- v5 only widens the count-check gate ahead of it."""
    from patches.selection import g5_selection_cap50_v4 as v4

    v5_candidate, v5_report = mod.build_candidate(original)
    v4_candidate, v4_report = v4.build_candidate(original)

    v5_pe = pefile.PE(data=v5_candidate, fast_load=True)
    v4_pe = pefile.PE(data=v4_candidate, fast_load=True)
    try:
        v5_body_addr = int(v5_report["hook"]["body_addr"], 16)
        v4_body_addr = int(v4_report["hook"]["body_addr"], 16)
        v5_body_off = mod._va_to_file_offset(v5_pe, v5_body_addr)
        v4_body_off = v4._va_to_file_offset(v4_pe, v4_body_addr)
        v5_tail = bytearray(v5_candidate[v5_body_off : v5_body_off + mod.BODY_LEN])
        v4_tail = bytearray(v4_candidate[v4_body_off : v4_body_off + mod.BODY_LEN])

        v5_insns = _decode_gate(v5_candidate, v5_report)
        do_chunk_addr = next(
            i.address for i in v5_insns if i.mnemonic == "push" and i.op_str == "ebp"
        )
        chunk_len = v5_body_addr - do_chunk_addr
        v5_gate_off = mod._va_to_file_offset(v5_pe, mod.CAVE_BASE)
        v4_gate_off = mod._va_to_file_offset(v4_pe, mod.CAVE_BASE)
        v5_chunk_start = v5_gate_off + (do_chunk_addr - mod.CAVE_BASE)
        v4_chunk_start = v4_gate_off + (v4_body_addr - mod.CAVE_BASE) - chunk_len
        v5_chunk_bytes = v5_candidate[v5_chunk_start : v5_chunk_start + chunk_len]
        v4_chunk_bytes = v4_candidate[v4_chunk_start : v4_chunk_start + chunk_len]
    finally:
        v5_pe.close()
        v4_pe.close()

    assert bytes(v5_chunk_bytes) == bytes(v4_chunk_bytes), (
        "chunk-building/backup/restore bytes from do_chunk onward must be unchanged from v4"
    )

    for call_site, _target in mod.EXTERNAL_CALLS:
        rel32_off = call_site - mod.HOOK_SITE + 1
        v5_tail[rel32_off : rel32_off + 4] = b"\x00\x00\x00\x00"
        v4_tail[rel32_off : rel32_off + 4] = b"\x00\x00\x00\x00"
    assert bytes(v5_tail) == bytes(v4_tail), "original body bytes (modulo call relocation) must be unchanged from v4"
