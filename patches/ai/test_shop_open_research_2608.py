import hashlib
import importlib.util
import struct
import sys
from pathlib import Path

import pefile
import pytest

MODULE_PATH = Path(__file__).with_name("shop_open_research_2608.py")
spec = importlib.util.spec_from_file_location("shop_open_research_2608", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = (
    Path("/home/dev_00/sharedfolder/260320_Syw2plus/260921_temp")
    / "[ESL]Syw2plus 2608"
    / "[ESL]Syw2plus 2608.exe"
)


@pytest.fixture(scope="module")
def original() -> bytes:
    if not SOURCE.exists():
        pytest.skip("local pinned ESL 2608 executable required")
    value = SOURCE.read_bytes()
    mod.verify_original(value)
    return value


def test_source_hash_and_table_anchor(original):
    assert hashlib.sha256(original).hexdigest() == mod.ORIGINAL_SHA256
    old = original[mod.OLD_TABLE_FILE_OFFSET : mod.OLD_TABLE_FILE_OFFSET + mod.OLD_TABLE_LEN]
    assert hashlib.sha256(old).hexdigest() == mod.TABLE_SHA256
    assert old[-2:] == b"\xfe\xff"


def test_candidate_preserves_143_rows_and_adds_three_shop_rows(original):
    candidate, report = mod.build_candidate(original)
    assert report["old_row_count"] == 143
    assert report["new_row_count"] == 146
    payload_start = int(report["new_section"]["raw_offset"], 16)
    payload = candidate[payload_start:]
    old_rows = original[mod.OLD_TABLE_FILE_OFFSET : mod.OLD_TABLE_FILE_OFFSET + 143 * 18]
    assert payload[: 143 * 18] == old_rows
    for index, building in enumerate((0x30, 0x39, 0x49), start=143):
        row = payload[index * 18 : (index + 1) * 18]
        assert row == struct.pack(
            "<9H", 0x000F, building, 0xFFFF, 20, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF
        )
    assert payload[146 * 18 : 146 * 18 + 2] == b"\xfe\xff"


def test_candidate_rewrites_all_ten_selector_references(original):
    candidate, report = mod.build_candidate(original)
    assert len(report["selector_fixups"]) == 10
    new_base = int(report["new_section"]["va"], 16)
    for item in report["selector_fixups"]:
        va = int(item["va"], 16)
        off = va - mod.IMAGE_BASE
        # All selector code is in the first .text mapping in this image, so
        # VA==file offset is pinned by the source geometry; use the module's
        # mapper as the actual assertion path as well.
        file_off = mod._va_to_file_offset(candidate, va, 8)
        immediate = struct.unpack_from("<I", candidate, file_off + next(ref.immediate_offset for ref in mod.SELECTOR_REFERENCES if ref.va == va))[0]
        assert immediate == new_base + int(item["table_offset"])
        assert candidate[file_off : file_off + 4] != original[off : off + 4]


def test_candidate_pe_geometry_and_nonoverlap(original):
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        names = [section.Name.rstrip(b"\0") for section in pe.sections]
        assert names.count(b".shopai") == 1
        section = next(section for section in pe.sections if section.Name.rstrip(b"\0") == b".shopai")
        assert section.Misc_VirtualSize == report["new_section"]["virtual_size"]
        assert section.SizeOfRawData == report["new_section"]["raw_size"]
        assert section.PointerToRawData == int(report["new_section"]["raw_offset"], 16)
        assert pe.OPTIONAL_HEADER.SizeOfInitializedData == (
            mod.ORIGINAL_SIZE_OF_INITIALIZED_DATA + section.SizeOfRawData
        )
        assert pe.OPTIONAL_HEADER.SizeOfImage >= section.VirtualAddress + section.Misc_VirtualSize
        ranges = [
            (s.VirtualAddress, s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData))
            for s in pe.sections
        ]
        for index, (start, end) in enumerate(ranges):
            for other_start, other_end in ranges[index + 1 :]:
                assert end <= other_start or other_end <= start
    finally:
        pe.close()


def test_candidate_does_not_mutate_original_and_restore_is_exact(original):
    before = hashlib.sha256(original).hexdigest()
    candidate, report = mod.build_candidate(original)
    assert hashlib.sha256(original).hexdigest() == before
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert mod.restore_candidate(candidate) == original


def test_restore_rejects_noncanonical_section_padding(original):
    candidate, report = mod.build_candidate(original)
    mutated = bytearray(candidate)
    raw_start = int(report["new_section"]["raw_offset"], 16)
    payload_len = report["new_section"]["virtual_size"]
    mutated[raw_start + payload_len] = 0xA5
    with pytest.raises(ValueError, match="padding"):
        mod.restore_candidate(bytes(mutated))


def test_restore_rejects_noncanonical_section_rva(original):
    candidate, report = mod.build_candidate(original)
    mutated = bytearray(candidate)
    pe = pefile.PE(data=mutated, fast_load=True)
    try:
        section = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".shopai")
        header = section.get_file_offset()
    finally:
        pe.close()
    struct.pack_into("<I", mutated, header + 12, int(report["new_section"]["rva"], 16) + 0x1000)
    with pytest.raises(ValueError, match="RVA"):
        mod.restore_candidate(bytes(mutated))


def test_wrong_version_is_refused(original):
    wrong = bytearray(original)
    wrong[0x1234] ^= 0x01
    with pytest.raises(ValueError):
        mod.build_candidate(bytes(wrong))


def test_refuses_existing_destination_and_source_overwrite(original, tmp_path):
    source = tmp_path / "source.exe"
    source.write_bytes(original)
    with pytest.raises(ValueError):
        mod.write_candidate(source, source)
    destination = tmp_path / "candidate.exe"
    destination.write_bytes(b"existing")
    with pytest.raises(FileExistsError):
        mod.write_candidate(source, destination)
