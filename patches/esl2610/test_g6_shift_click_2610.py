from __future__ import annotations

import struct

import pefile
import pytest

from patches.esl2610 import g6_shift_click_2610 as mod
from patches.esl2610 import pe_extend


@pytest.fixture(scope="module")
def base() -> bytes:
    if not pe_extend.BASE_PATH.exists():
        pytest.skip("local pinned ESL2610 executable required")
    return pe_extend.BASE_PATH.read_bytes()


def _rel_target(data: bytes, va: int) -> int:
    off = pe_extend.va_to_offset(data, va)
    return va + 5 + struct.unpack_from("<i", data, off + 1)[0]


def test_hook_jumps_to_cave_and_cave_bounds_loop_by_count(base):
    out, report = mod.build_candidate(base)
    cave = pe_extend.section_va(out, mod.SECTION_NAME)
    hook = pe_extend.va_to_offset(out, mod.HOOK_VA)
    assert out[hook] == 0xE9 and out[hook + 5 : hook + 8] == b"\x90" * 3
    assert _rel_target(out, mod.HOOK_VA) == cave
    c = pe_extend.va_to_offset(out, cave)
    assert out[c : c + 4] == bytes.fromhex("3b7c2410")  # cmp edi,[esp+0x10] (compacted count)
    assert out[c + 4 : c + 6] == bytes.fromhex("7c0a")  # jl cont
    assert out[c + 6 : c + 11] == b"\xa1" + struct.pack("<I", 0xB938E0)  # eax = clicked unit
    assert _rel_target(out, cave + 11) == mod.LOOP_EXIT_VA
    assert out[c + 16 : c + 24] == mod.HOOK_OLD
    assert _rel_target(out, cave + 24) == mod.LOOP_RESUME_VA
    assert report["cave_va"] == hex(cave)


def test_only_hook_bytes_header_and_new_section_change(base):
    out, _ = mod.build_candidate(base)
    compact = pe_extend.compact_headers(base)
    old = pefile.PE(data=compact, fast_load=True)
    new = pefile.PE(data=out, fast_load=True)
    assert len(new.sections) == len(old.sections) + 1
    hook = pe_extend.va_to_offset(out, mod.HOOK_VA)
    for a, b in zip(old.sections, new.sections):
        da, db = a.get_data(), b.get_data()
        if a.Name.rstrip(b"\0") == b".text":
            rel = hook - a.PointerToRawData
            assert da[:rel] == db[:rel] and da[rel + 8 :] == db[rel + 8 :]
        else:
            assert da == db


def test_loop_tail_and_count_slot_are_the_2613_layout(base):
    # The official 2613 handler restores the 100-entry loop bound; the cave
    # bounds by the actual count either way.
    loop_cmp = pe_extend.va_to_offset(base, 0x41DDE4)
    assert base[loop_cmp : loop_cmp + 5] == bytes.fromhex("83ff647c99")
    store = pe_extend.va_to_offset(base, 0x41DD74)
    assert base[store : store + 4] == bytes.fromhex("894c2410")  # mov [esp+0x10],ecx


def test_composes_on_already_compacted_image_and_rejects_double_apply(base):
    other = pe_extend.add_section(pe_extend.compact_headers(base), b".x", b"\x90", 0x1000, pe_extend.CODE_RX)
    out, _ = mod.build_candidate(other, require_pinned_base=False)
    assert pe_extend.section_names(out)[-1] == mod.SECTION_NAME
    with pytest.raises(ValueError):
        mod.build_candidate(out, require_pinned_base=False)


def test_rejects_unpinned_base_by_default(base):
    with pytest.raises(ValueError, match="SHA256"):
        mod.build_candidate(base[:-1] + b"\x01")
