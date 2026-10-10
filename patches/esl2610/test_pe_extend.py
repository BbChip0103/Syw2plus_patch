from __future__ import annotations

import pefile
import pytest

from patches.esl2610 import pe_extend as mod


@pytest.fixture(scope="module")
def base() -> bytes:
    if not mod.BASE_PATH.exists():
        pytest.skip("local pinned ESL2610 executable required")
    data = mod.BASE_PATH.read_bytes()
    mod.verify_base(data)
    return data


def test_base_header_table_is_full(base):
    assert mod.free_header_slots(base) == 0


def test_compact_headers_frees_slots_and_keeps_image(base):
    out = mod.compact_headers(base)
    assert len(out) == len(base)
    assert out[0x1000:] == base[0x1000:]
    assert mod.free_header_slots(out) == 4
    old = pefile.PE(data=base, fast_load=True)
    new = pefile.PE(data=out, fast_load=True)
    assert new.DOS_HEADER.e_lfanew == 0x40
    assert new.OPTIONAL_HEADER.SizeOfHeaders == old.OPTIONAL_HEADER.SizeOfHeaders
    for a, b in zip(old.sections, new.sections, strict=True):
        assert a.__pack__() == b.__pack__()
    assert [(d.VirtualAddress, d.Size) for d in old.OPTIONAL_HEADER.DATA_DIRECTORY] == [
        (d.VirtualAddress, d.Size) for d in new.OPTIONAL_HEADER.DATA_DIRECTORY
    ]


def test_add_section_appends_after_image_and_updates_headers(base):
    out = mod.add_section(mod.compact_headers(base), b".t1", b"\xcc" * 0x10, 0x3000, mod.CODE_RX)
    pe = pefile.PE(data=out)
    last = pe.sections[-1]
    assert last.Name.rstrip(b"\0") == b".t1"
    assert last.VirtualAddress == 0x16B5000  # 2610 SizeOfImage: first free RVA
    assert last.Misc_VirtualSize == 0x3000 and last.SizeOfRawData == 0x200  # FileAlignment
    assert last.PointerToRawData == len(base)
    assert last.get_data()[:0x10] == b"\xcc" * 0x10
    assert pe.OPTIONAL_HEADER.SizeOfImage == 0x16B5000 + 0x3000
    assert pe.FILE_HEADER.NumberOfSections == 91
    assert pe.OPTIONAL_HEADER.SizeOfCode == pefile.PE(data=base).OPTIONAL_HEADER.SizeOfCode + 0x200
    assert pe.OPTIONAL_HEADER.CheckSum == pe.generate_checksum()
    assert mod.va_to_offset(out, 0x400000 + last.VirtualAddress + 4) == last.PointerToRawData + 4


def test_add_bss_section_has_no_raw_bytes(base):
    out = mod.add_section(mod.compact_headers(base), b".b1", b"", 0x765000, mod.BSS_RW)
    pe = pefile.PE(data=out, fast_load=True)
    last = pe.sections[-1]
    assert (last.SizeOfRawData, last.PointerToRawData) == (0, 0)
    assert pe.OPTIONAL_HEADER.SizeOfImage == 0x16B5000 + 0x765000
    assert len(out) == len(base)


def test_add_section_requires_room_and_unique_names(base):
    with pytest.raises(ValueError, match="header"):
        mod.add_section(base, b".t1", b"\x90", 0x1000, mod.CODE_RX)
    once = mod.add_section(mod.compact_headers(base), b".t1", b"\x90", 0x1000, mod.CODE_RX)
    with pytest.raises(ValueError, match="exists"):
        mod.add_section(once, b".t1", b"\x90", 0x1000, mod.CODE_RX)


def test_compact_is_idempotent_guarded(base):
    with pytest.raises(ValueError, match="already"):
        mod.compact_headers(mod.compact_headers(base))


def test_rejects_unpinned_base(base):
    with pytest.raises(ValueError, match="SHA256"):
        mod.verify_base(base[:-1] + b"\x01")


def test_rejects_previous_official_2612_base_after_2613_repin():
    previous = mod.REPO.parent / "patch_history" / "[ESL]Syw2plus 2612" / "[ESL]Syw2plus 2612.exe"
    if not previous.exists():
        pytest.skip("read-only previous official 2612 executable unavailable")
    with pytest.raises(ValueError, match="SHA256"):
        mod.verify_base(previous.read_bytes())
