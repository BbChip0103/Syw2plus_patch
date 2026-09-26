import importlib.util
import sys
import struct
import json
import hashlib
from dataclasses import replace
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location(
    "offline_storage_v1", Path(__file__).with_name("offline_storage_v1.py")
)
assert spec is not None and spec.loader is not None
patch = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = patch
spec.loader.exec_module(patch)
SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


def _operand_ranges(rows):
    return {
        i
        for row in rows
        for i in range(row.file_offset + row.operand_offset, row.file_offset + row.operand_offset + 4)
    }


@pytest.fixture
def original():
    if not SOURCE.exists():
        pytest.skip("Local original game required")
    return SOURCE.read_bytes()


def test_exact_input_and_layout(original):
    pe = patch.parse_pe(original)
    assert patch.digest(original) == patch.ORIGINAL_SHA256
    assert pe.image_base == 0x400000
    assert pe.size_of_image == 0xC8F000
    layout = patch.storage_layout(pe.size_of_image)
    assert layout.section_rva % pe.section_alignment == 0
    assert layout.section_rva >= pe.size_of_image
    assert all(v % 4 == 0 for v in layout.arena_offsets.values())
    assert layout.capacity == 4001
    assert layout.unit_size == 0x758


def test_build_preserves_source_and_has_private_rw_nonexec_section(original):
    result = patch.build_candidate(original)
    assert result[: len(original)] != original
    assert original == SOURCE.read_bytes()
    pe = patch.parse_pe(result)
    section = next(s for s in pe.sections if s.name == patch.SECTION_NAME)
    assert section.virtual_address >= 0xC8F000
    assert section.characteristics & patch.IMAGE_SCN_MEM_READ
    assert section.characteristics & patch.IMAGE_SCN_MEM_WRITE
    assert not section.characteristics & patch.IMAGE_SCN_MEM_EXECUTE
    assert pe.number_of_sections == 6
    assert pe.size_of_image > 0xC8F000
    assert patch.inspect_candidate(result)["family_patch_count"] == 120
    assert patch.inspect_candidate(result)["creation_patch_count"] == 13
    assert patch.inspect_candidate(result)["owner_lifecycle_patch_count"] == 4


def test_family_and_allocator_changes_are_guarded(original):
    result = patch.build_candidate(original)
    changed = {i for i, (a, b) in enumerate(zip(original, result[: len(original)])) if a != b}
    pe = patch.parse_pe(original)
    expected = set()
    expected.update(range(pe.e_lfanew + 4 + 2, pe.e_lfanew + 4 + 4))
    opt = pe.e_lfanew + 4 + 20
    expected.update(range(opt + 4, opt + 12))
    expected.update(range(opt + 56, opt + 56 + 4))
    expected.update(
        range(
            pe.section_table + pe.number_of_sections * 40,
            pe.section_table + (pe.number_of_sections + 2) * 40,
        )
    )
    for row in patch.PATCHES:
        expected.update(
            range(row.file_offset + row.operand_offset, row.file_offset + row.operand_offset + 4)
        )
    expected.update(_operand_ranges(patch.CREATION_PATCHES))
    expected.update(_operand_ranges(patch.OWNER_LIFECYCLE_PATCHES))
    expected.update(range(patch.ALLOCATOR_FILE_OFFSET, patch.ALLOCATOR_FILE_OFFSET + 61))
    expected.update(range(0x1B576, 0x1B576 + 5))
    expected.update(range(0x3FFD4, 0x3FFD4 + 5))
    expected.update(
        range(patch.INIT_CALL_VA - patch.IMAGE_BASE, patch.INIT_CALL_VA - patch.IMAGE_BASE + 5)
    )
    assert changed <= expected
    assert len(patch.PATCHES) == 120
    assert (
        result[patch.ALLOCATOR_FILE_OFFSET : patch.ALLOCATOR_FILE_OFFSET + 61]
        != patch.ALLOCATOR_BYTES
    )
    assert (
        result[patch.ALLOCATOR_FILE_OFFSET : patch.ALLOCATOR_FILE_OFFSET + 13]
        == patch.ALLOCATOR_BYTES[:13]
    )
    allocator = result[patch.ALLOCATOR_FILE_OFFSET : patch.ALLOCATOR_FILE_OFFSET + 61]
    allocator_changed = {
        i - patch.ALLOCATOR_FILE_OFFSET
        for i in changed
        if patch.ALLOCATOR_FILE_OFFSET <= i < patch.ALLOCATOR_FILE_OFFSET + 61
    }
    expected_allocator_changed = {
        i
        for i, (before, after) in enumerate(zip(patch.ALLOCATOR_BYTES, allocator))
        if before != after
    }
    assert allocator_changed == expected_allocator_changed
    assert allocator_changed <= (
        set(range(0x0D, 0x11)) | set(range(0x14, 0x18)) | set(range(0x33, 0x37))
    )


def test_allocator_geometry_and_repeated_apply_guard(original):
    first = patch.build_candidate(original)
    with pytest.raises(ValueError, match="SHA256"):
        patch.build_candidate(first)
    pe = patch.parse_pe(first)
    section = next(s for s in pe.sections if s.name == patch.SECTION_NAME)
    layout = patch.storage_layout(section.virtual_address, section_alignment=pe.section_alignment)
    age_base = patch.IMAGE_BASE + layout.section_rva + layout.arena_offsets["age"]
    exists_base = patch.IMAGE_BASE + layout.section_rva + layout.arena_offsets["exists"]
    allocator = first[patch.ALLOCATOR_FILE_OFFSET : patch.ALLOCATOR_FILE_OFFSET + 61]
    assert struct.unpack_from("<I", allocator, 0x0D)[0] == age_base + 2
    assert struct.unpack_from("<i", allocator, 0x14)[0] == exists_base - age_base
    assert struct.unpack_from("<I", allocator, 0x33)[0] == age_base + patch.CAPACITY * 2
    assert allocator[0x07:0x0D] == patch.ALLOCATOR_BYTES[0x07:0x0D]
    assert allocator[0x18:0x33] == patch.ALLOCATOR_BYTES[0x18:0x33]
    assert allocator[0x37:] == patch.ALLOCATOR_BYTES[0x37:]


def test_typed_fixup_cannot_overlap_allocator(monkeypatch, original):
    collision = patch.PatchRecord(
        patch.ALLOCATOR_VA,
        len(patch.ALLOCATOR_BYTES),
        0,
        int.from_bytes(patch.ALLOCATOR_BYTES[:4], "little"),
        "ARENA_POOL",
        0,
        patch.ALLOCATOR_BYTES,
    )
    monkeypatch.setattr(patch, "PATCHES", patch.PATCHES + (collision,))
    with pytest.raises(ValueError, match="overlapping"):
        patch.build_candidate(original)


def test_storage_raw_is_zero_and_original_sections_are_unchanged(original):
    result = patch.build_candidate(original)
    before = patch.parse_pe(original)
    after = patch.parse_pe(result)
    assert after.size_of_headers == before.size_of_headers
    allowed = set(range(patch.ALLOCATOR_FILE_OFFSET, patch.ALLOCATOR_FILE_OFFSET + 61))
    for row in patch.PATCHES:
        allowed.update(
            range(row.file_offset + row.operand_offset, row.file_offset + row.operand_offset + 4)
        )
    allowed.update(_operand_ranges(patch.CREATION_PATCHES))
    allowed.update(_operand_ranges(patch.OWNER_LIFECYCLE_PATCHES))
    allowed.update(range(0x1B576, 0x1B576 + 5))
    allowed.update(range(0x3FFD4, 0x3FFD4 + 5))
    allowed.update(
        range(patch.INIT_CALL_VA - patch.IMAGE_BASE, patch.INIT_CALL_VA - patch.IMAGE_BASE + 5)
    )
    for old, new in zip(before.sections, after.sections[: before.number_of_sections]):
        assert old == new
        changed = {
            old.raw_pointer + i
            for i, (before_byte, after_byte) in enumerate(
                zip(
                    original[old.raw_pointer : old.raw_pointer + old.raw_size],
                    result[old.raw_pointer : old.raw_pointer + old.raw_size],
                )
            )
            if before_byte != after_byte
        }
        assert changed <= allowed
    section = next(section for section in after.sections if section.name == patch.SECTION_NAME)
    assert result[section.raw_pointer : section.raw_pointer + section.raw_size] == bytes(
        section.raw_size
    )


def test_bad_version_and_tampered_patch_refuse(original):
    with pytest.raises(ValueError, match="SHA256"):
        patch.build_candidate(b"bad")
    data = bytearray(original)
    data[patch.ALLOCATOR_FILE_OFFSET] ^= 1
    with pytest.raises(ValueError, match="SHA256"):
        patch.build_candidate(bytes(data))


def test_copy_restore_and_collision(original, tmp_path):
    source = tmp_path / "input.exe"
    target = tmp_path / "candidate.exe"
    source.write_bytes(original)
    patch.create_copy(source, target)
    assert source.read_bytes() == original
    with pytest.raises(FileExistsError):
        patch.create_copy(source, target)
    assert patch.restore(target) == patch.ORIGINAL_SHA256
    assert target.read_bytes() == original
    target.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="exact"):
        patch.restore(target)


def test_creation_recipe_is_exactly_thirteen_pinned_sites(original):
    expected = {
        0x00443241: (7, 3, 0x0066B790),
        0x0048BC56: (8, 4, 0x008990C8),
        0x0048BC65: (10, 4, 0x00899A28),
        0x0048BC76: (7, 3, 0x00975908),
        0x0048BC7D: (8, 4, 0x00974FA8),
        0x0048BC85: (6, 2, 0x00975908),
        0x0048BC92: (7, 3, 0x00975908),
        0x0048BCA1: (7, 3, 0x0089C2C8),
        0x0048BCAE: (7, 3, 0x0089B008),
        0x0048BCB5: (7, 3, 0x0089C2C8),
        0x0048BCBE: (7, 3, 0x0089D58A),
        0x0048BCCB: (7, 3, 0x0089C2CA),
        0x0048BCD2: (7, 3, 0x0089D58A),
    }
    assert len(patch.PATCHES) == 120
    assert patch.PATCH_SOURCE_SHA256 == "e13195a4a88a35b944dc48dff3b8b584d8402dff9e33dfe3f6adb275edce5ace"
    frozen = [
        (row.va, row.instruction_length, row.operand_offset, row.old_target,
         row.region, row.field_offset, row.old_bytes.hex())
        for row in patch.PATCHES
    ]
    assert hashlib.sha256(json.dumps(frozen, separators=(",", ":")).encode()).hexdigest() == (
        "79663639ea1c8950644133dcd90339a3015ba8cd2991e527d6cac4d4ad854c2a"
    )
    assert len(patch.CREATION_PATCHES) == 13
    assert {row.va: (row.instruction_length, row.operand_offset, row.old_target)
            for row in patch.CREATION_PATCHES} == expected
    assert {0x0048BC35, 0x0048BC3F}.isdisjoint(expected)
    for row in patch.CREATION_PATCHES:
        assert original[row.file_offset : row.file_offset + row.instruction_length] == row.old_bytes
    scales = {
        "ARENA_POOL": 8, "ARENA_EXISTS": 2, "ARENA_AGE": 2,
        "ARENA_ACTIVE": 2, "ARENA_CATA": 4, "ARENA_CATB": 4,
        "COUNTER_ACTIVE": None, "COUNTER_CATA": None, "COUNTER_CATB": None,
    }
    assert all((8 if row.region == "ARENA_POOL" else
                2 if row.region in {"ARENA_EXISTS", "ARENA_AGE", "ARENA_ACTIVE"} else
                4 if row.region in {"ARENA_CATA", "ARENA_CATB"} else None) == scales[row.region]
               for row in patch.CREATION_PATCHES)


def test_creation_targets_and_nonoperand_bytes_are_precise(original):
    result = patch.build_candidate(original)
    pe = patch.parse_pe(result)
    storage = next(section for section in pe.sections if section.name == patch.SECTION_NAME)
    layout = patch.storage_layout(storage.virtual_address, section_alignment=pe.section_alignment)
    for row in patch.CREATION_PATCHES:
        old = original[row.file_offset : row.file_offset + row.instruction_length]
        new = result[row.file_offset : row.file_offset + row.instruction_length]
        target = patch._target(row, layout)
        assert struct.unpack_from("<I", new, row.operand_offset)[0] == target
        for index, (before, after) in enumerate(zip(old, new)):
            if row.operand_offset <= index < row.operand_offset + 4:
                continue
            assert before == after, hex(row.va)


def test_creation_and_frozen_family_cfg_are_unchanged_except_disp32(original):
    capstone = pytest.importorskip("capstone")
    result = patch.build_candidate(original)
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True

    def decode(data, start, end):
        return list(decoder.disasm(data[start - patch.IMAGE_BASE : end - patch.IMAGE_BASE], start))

    ranges = ((0x443190, 0x443257, 71), (0x48BC00, 0x48BD05, 52),
              (0x48B000, 0x48B204, 133), (0x411A00, 0x411FF4, 335))
    allowed = {row.file_offset + i for row in patch.CREATION_PATCHES
               for i in range(row.operand_offset, row.operand_offset + 4)}
    for start, end, expected_count in ranges:
        before = decode(original, start, end)
        after = decode(result, start, end)
        assert len(before) == len(after) == expected_count
        assert [(i.address, i.size, i.mnemonic, tuple(i.groups)) for i in before] == [
            (i.address, i.size, i.mnemonic, tuple(i.groups)) for i in after
        ]
        for old, new in zip(before, after):
            for index, (before_byte, after_byte) in enumerate(zip(old.bytes, new.bytes)):
                if old.address - patch.IMAGE_BASE + index in allowed:
                    continue
                assert before_byte == after_byte
    assert [i.address for i in decode(original, 0x48BC00, 0x48BD05)
            if i.mnemonic == "ret"] == [0x48BD04]


def test_creation_validation_rejects_unknown_or_nonidentical_overlap(monkeypatch, original):
    good = patch.CREATION_PATCHES[0]
    bad_region = patch.PatchRecord(0x00443241, 7, 3, 0x0066B790, "UNKNOWN", 0,
                                   good.old_bytes)
    monkeypatch.setattr(patch, "CREATION_PATCHES", (bad_region,))
    with pytest.raises(ValueError, match="unknown creation patch region"):
        patch.build_candidate(original)

    overlap = patch.PatchRecord(0x00443240, 8, 3, 0x0066B790, "ARENA_POOL", 0,
                                bytes.fromhex("808d0cc590b76601"))
    monkeypatch.setattr(patch, "CREATION_PATCHES", (good, overlap))
    with pytest.raises(ValueError, match="non-identical or partial typed overlap"):
        patch.build_candidate(original)


@pytest.mark.parametrize(
    "mutated",
    [
        lambda row: replace(row, region="ARENA_EXISTS"),
        lambda row: replace(row, field_offset=1),
        lambda row: replace(row, operand_offset=2),
    ],
)
def test_creation_exact_site_metadata_collision_is_rejected(monkeypatch, original, mutated):
    good = patch.CREATION_PATCHES[0]
    monkeypatch.setattr(patch, "CREATION_PATCHES", (good, mutated(good)))
    with pytest.raises(ValueError, match="non-identical or partial typed overlap"):
        patch.build_candidate(original)


def test_creation_byte_identical_partial_and_reserved_collisions_are_rejected(
    monkeypatch, original,
):
    good = patch.CREATION_PATCHES[0]
    partial_va = 0x00443240
    partial_off = partial_va - patch.IMAGE_BASE
    partial = patch.PatchRecord(
        partial_va, 8, 3, 0x0066B790, "ARENA_POOL", 0,
        original[partial_off : partial_off + 8],
    )
    monkeypatch.setattr(patch, "CREATION_PATCHES", (good, partial))
    with pytest.raises(ValueError, match="non-identical or partial typed overlap"):
        patch.build_candidate(original)

    for va, payload, operand_offset, name in (
        (patch.ALLOCATOR_VA, patch.ALLOCATOR_BYTES, 0, "allocator"),
        (patch.INIT_CALL_VA, patch.INIT_CALL_BYTES, 1, "init call"),
        (0x0041B576, original[0x1B576 : 0x1B576 + 5], 1, "fixed-supply"),
    ):
        row = patch.PatchRecord(
            va, len(payload), operand_offset, 0, "ARENA_POOL", 0, payload,
        )
        monkeypatch.setattr(patch, "CREATION_PATCHES", (row,))
        with pytest.raises(ValueError, match=f"reserved {name}"):
            patch.build_candidate(original)


def test_genuine_full_creation_duplicate_is_congruent(original, monkeypatch):
    normal = patch.build_candidate(original)
    good = patch.CREATION_PATCHES[0]
    monkeypatch.setattr(patch, "CREATION_PATCHES", (good,) + patch.CREATION_PATCHES)
    assert patch.build_candidate(original) == normal


def test_owner_lifecycle_recipe_is_exact_four_byte_fields(original):
    expected = {
        0x0043EE80: (6, 2, 0x0066B81D, 0x8D),
        0x0043EEA2: (6, 2, 0x0066B968, 0x1D8),
        0x0043EF71: (6, 2, 0x0066B81D, 0x8D),
        0x0043EF92: (6, 2, 0x0066B968, 0x1D8),
    }
    assert len(patch.OWNER_LIFECYCLE_PATCHES) == 4
    assert {row.va: (row.instruction_length, row.operand_offset, row.old_target, row.field_offset)
            for row in patch.OWNER_LIFECYCLE_PATCHES} == expected
    for row in patch.OWNER_LIFECYCLE_PATCHES:
        assert row.old_bytes == original[row.file_offset : row.file_offset + row.instruction_length]
        assert row.instruction_length == 6
        assert row.old_bytes[0:2] == bytes.fromhex("8a90")


def test_owner_lifecycle_targets_and_nonoperand_bytes_are_precise(original):
    result = patch.build_candidate(original)
    pe = patch.parse_pe(result)
    storage = next(section for section in pe.sections if section.name == patch.SECTION_NAME)
    layout = patch.storage_layout(storage.virtual_address, section_alignment=pe.section_alignment)
    for row in patch.OWNER_LIFECYCLE_PATCHES:
        old = original[row.file_offset : row.file_offset + row.instruction_length]
        new = result[row.file_offset : row.file_offset + row.instruction_length]
        assert struct.unpack_from("<I", new, row.operand_offset)[0] == patch._target(row, layout)
        for index, (before, after) in enumerate(zip(old, new)):
            if row.operand_offset <= index < row.operand_offset + 4:
                continue
            assert before == after, hex(row.va)


def test_owner_lifecycle_cfg_and_cross_family_collision_are_fail_closed(original, monkeypatch):
    capstone = pytest.importorskip("capstone")
    result = patch.build_candidate(original)
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    decoder.detail = True

    def decode(data, start, end):
        return list(decoder.disasm(data[start - patch.IMAGE_BASE : end - patch.IMAGE_BASE], start))

    for start, end, count in ((0x43EE30, 0x43EEB7, 34), (0x43EEC0, 0x43EFA8, 65)):
        before = decode(original, start, end)
        after = decode(result, start, end)
        assert len(before) == len(after) == count
        assert [(i.address, i.size, i.mnemonic, tuple(i.groups)) for i in before] == [
            (i.address, i.size, i.mnemonic, tuple(i.groups)) for i in after
        ]
        owner_ranges = _operand_ranges(patch.OWNER_LIFECYCLE_PATCHES)
        for old, new in zip(before, after):
            for index, (before_byte, after_byte) in enumerate(zip(old.bytes, new.bytes)):
                if old.address - patch.IMAGE_BASE + index in owner_ranges:
                    continue
                assert before_byte == after_byte
    assert [i.address for i in decode(original, 0x43EE30, 0x43EEB7) if i.mnemonic == "ret"] == [
        0x43EE54, 0x43EEB4
    ]
    assert [i.address for i in decode(original, 0x43EEC0, 0x43EFA8) if i.mnemonic == "ret"] == [
        0x43EEEB, 0x43EFA5
    ]

    owner = patch.OWNER_LIFECYCLE_PATCHES[0]
    conflicting = replace(owner, region="ARENA_EXISTS")
    monkeypatch.setattr(patch, "OWNER_LIFECYCLE_PATCHES", (owner, conflicting))
    with pytest.raises(ValueError, match="non-identical or partial typed overlap"):
        patch.build_candidate(original)


def test_creation_candidate_is_deterministic_and_reapply_is_private(original, tmp_path):
    first = patch.build_candidate(original)
    second = patch.build_candidate(original)
    assert first == second
    source = tmp_path / "source.exe"
    target = tmp_path / "candidate.exe"
    source.write_bytes(original)
    patch.create_copy(source, target)
    assert target.read_bytes() == first
    assert Path(str(target) + ".original").read_bytes() == original
    with pytest.raises(FileExistsError):
        patch.create_copy(source, target)
    assert patch.restore(target) == patch.ORIGINAL_SHA256
    assert target.read_bytes() == original
    # A fresh destination proves reapplication remains exclusive and private.
    second_target = tmp_path / "candidate-reapply.exe"
    assert patch.create_copy(source, second_target) == patch.digest(first)


def test_init_stub_section_call_and_sidecar_geometry(original):
    result = patch.build_candidate(original)
    pe = patch.parse_pe(result)
    storage = next(s for s in pe.sections if s.name == patch.SECTION_NAME)
    init = next(s for s in pe.sections if s.name == b".g2ini")
    assert init.characteristics & patch.IMAGE_SCN_MEM_EXECUTE
    assert init.characteristics & patch.IMAGE_SCN_MEM_READ
    assert not init.characteristics & patch.IMAGE_SCN_MEM_WRITE
    assert init.virtual_address % pe.section_alignment == 0
    assert init.raw_pointer % pe.file_alignment == 0
    call_off = patch.INIT_CALL_VA - patch.IMAGE_BASE
    call = result[call_off : call_off + 5]
    assert call[0] == 0xE8
    target = patch.INIT_CALL_VA + 5 + struct.unpack_from("<i", call, 1)[0]
    assert target == patch.IMAGE_BASE + init.virtual_address
    stub = result[init.raw_pointer : init.raw_pointer + init.virtual_size]
    assert stub[0] == 0xE8 and stub[5:8] == bytes.fromhex("9c 60 fc")
    assert (
        patch.ORIGINAL_INIT_VA
        == patch.IMAGE_BASE + init.virtual_address + 5 + struct.unpack_from("<i", stub, 1)[0]
    )
    assert stub.endswith(bytes.fromhex("61 9d c3"))
    layout = patch.storage_layout(storage.virtual_address, section_alignment=pe.section_alignment)
    assert layout.virtual_size == 7577910
    assert len(set(layout.arena_offsets.values())) == 6
    assert all(offset % 4 == 0 for offset in layout.arena_offsets.values())
    assert all(offset % 4 == 0 for offset in layout.counter_offsets.values())
    for name in ("exists", "age", "active", "cata", "catb"):
        address = patch.IMAGE_BASE + layout.section_rva + layout.arena_offsets[name]
        assert struct.pack("<I", address) in stub
    for name in ("active_count", "cata_count", "catb_count"):
        address = patch.IMAGE_BASE + layout.section_rva + layout.counter_offsets[name]
        assert struct.pack("<I", address) in stub


def test_init_stub_decodes_complete_copy_program(original):
    capstone = pytest.importorskip("capstone")
    result = patch.build_candidate(original)
    pe = patch.parse_pe(result)
    storage = next(s for s in pe.sections if s.name == patch.SECTION_NAME)
    init = next(s for s in pe.sections if s.name == b".g2ini")
    layout = patch.storage_layout(storage.virtual_address, section_alignment=pe.section_alignment)
    stub = result[init.raw_pointer : init.raw_pointer + init.virtual_size]
    decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    instructions = list(decoder.disasm(stub, patch.IMAGE_BASE + init.virtual_address))
    assert sum(i.size for i in instructions) == len(stub)
    assert [i.mnemonic for i in instructions[:4]] == ["call", "pushfd", "pushal", "cld"]
    assert [i.mnemonic for i in instructions[-3:]] == ["popal", "popfd", "ret"]
    assert sum(i.mnemonic == "call" for i in instructions) == 1
    assert all(i.mnemonic not in {"jmp", "je", "jne", "jl", "jg", "ja", "jb"} for i in instructions)
    assert (
        int.from_bytes(instructions[0].bytes[1:], "little", signed=True)
        + instructions[0].address
        + 5
        == patch.ORIGINAL_INIT_VA
    )
    edi_values = [
        int.from_bytes(i.bytes[1:], "little") for i in instructions if i.bytes[:1] == b"\xbf"
    ]
    expected_edi = [
        patch.IMAGE_BASE + layout.section_rva + layout.arena_offsets[name]
        for name in ("exists", "age", "active", "cata", "catb")
    ]
    assert edi_values == expected_edi
    ecx_values = [
        int.from_bytes(i.bytes[1:], "little") for i in instructions if i.bytes[:1] == b"\xb9"
    ]
    assert ecx_values == [600, 1400, 600, 1400, 600, 1400, 1200, 2801, 1200, 2801]
    assert [i.bytes.hex() for i in instructions].count("f3a5") == 5
    assert [i.bytes.hex() for i in instructions].count("f3ab") == 5
    assert [i.bytes.hex() for i in instructions].count("66ab") == 3
    counter_stores = [
        int.from_bytes(i.bytes[2:], "little") for i in instructions if i.bytes[:2] == b"\x66\xa3"
    ]
    assert counter_stores == [
        patch.IMAGE_BASE + layout.section_rva + layout.counter_offsets[name]
        for name in ("active_count", "cata_count", "catb_count")
    ]


def test_typed_fixup_cannot_overlap_original_init_call(monkeypatch, original):
    collision = patch.PatchRecord(
        patch.INIT_CALL_VA,
        len(patch.INIT_CALL_BYTES),
        1,
        int.from_bytes(patch.INIT_CALL_BYTES[1:], "little"),
        "ARENA_POOL",
        0,
        patch.INIT_CALL_BYTES,
    )
    monkeypatch.setattr(patch, "PATCHES", patch.PATCHES + (collision,))
    with pytest.raises(ValueError, match="overlapping"):
        patch.build_candidate(original)


def test_fixed_supply_composition_is_exact(original):
    result = patch.build_candidate(original)
    assert result[0x1B576 : 0x1B576 + 5] == bytes.fromhex("66 c7 00 88 13")
    assert result[0x3FFD4 : 0x3FFD4 + 5] == bytes.fromhex("b8 88 13 00 00")
