import hashlib
import importlib.util
import sys
from pathlib import Path

import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v1.py")
spec = importlib.util.spec_from_file_location(MODULE.stem, MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    return SOURCE.read_bytes()


def test_layout_is_private_and_fully_mapped(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    assert len(candidate) == len(original)
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] != report["original_sha256"]
    assert mod.SELECTION_BASE >= mod.RSRC_BASE_VA
    assert mod.SELECTION_BASE + mod.SELECTION_BYTES <= mod.CONTROL_GROUP_BASE
    selection_end = int(report["selection_end_exclusive"], 16)
    assert selection_end - (mod.SELECTION_BASE + mod.ENTRY_BYTES) == mod.TARGET_CAPACITY * mod.ENTRY_BYTES
    assert 0x00899078 - 0x00899028 == mod.STOCK_CAPACITY * mod.ENTRY_BYTES
    assert selection_end <= mod.CONTROL_GROUP_BASE
    assert mod.CONTROL_GROUP_BASE + mod.CONTROL_GROUP_BYTES < report["geometry"]["new_rsrc"]
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        data = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".data")
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        data_end = mod.IMAGE_BASE + int(data.VirtualAddress) + int(data.Misc_VirtualSize)
        assert data_end >= report["geometry"]["new_rsrc"]
        assert mod.SELECTION_BASE + mod.SELECTION_BYTES <= data_end
        assert mod.CONTROL_GROUP_BASE + mod.CONTROL_GROUP_BYTES <= data_end
        assert int(rsrc.VirtualAddress) + mod.IMAGE_BASE == report["geometry"]["new_rsrc"]
    finally:
        pe.close()


def test_all_pinned_selection_sites_are_rewritten_and_slot_index_stays_stock(original: bytes) -> None:
    candidate, _ = mod.build_candidate(original)
    pe = pefile.PE(data=original, fast_load=True)
    try:
        for va, old, old_value in mod.DIRECT_SITES:
            off = mod._va_to_file_offset(pe, va)
            expected = old.replace(
                old_value.to_bytes(4, "little"),
                {
                    0x00899024: mod.SELECTION_BASE,
                    0x00899028: mod.SELECTION_BASE + 4,
                    0x0089902A: mod.SELECTION_BASE + 6,
                }[old_value].to_bytes(4, "little"),
                1,
            )
            assert candidate[off : off + len(old)] == expected, hex(va)
        for va, old in mod.END_SITES:
            off = mod._va_to_file_offset(pe, va)
            expected = old.replace(
                (0x00899078).to_bytes(4, "little"),
                (mod.SELECTION_BASE + mod.ENTRY_BYTES + mod.SELECTION_BYTES).to_bytes(4, "little"),
                1,
            )
            assert candidate[off : off + len(old)] == expected, hex(va)
        slot_index_va = 0x0040F4BC
        off = mod._va_to_file_offset(pe, slot_index_va)
        assert candidate[off : off + 5] == original[off : off + 5]
    finally:
        pe.close()


def test_rotation_sites_are_50_and_group_command_sites_are_not_silently_overwritten(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=original, fast_load=True)
    try:
        for va, old in mod.ROTATION_SITES:
            off = mod._va_to_file_offset(pe, va)
            assert candidate[off : off + len(old)][-1] == 0x32 if len(old) == 3 else candidate[off + 1] == 0x32
        assert report["command_packet"].startswith("unchanged")
        assert report["control_group_fields"].startswith("unchanged")
    finally:
        pe.close()


def test_selection_consumer_is_50_and_uses_disjoint_private_frame_buffers(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    assert report["patched_selection_consumer_sites"] == len(mod.SELECTION_CONSUMER_LIMIT_SITES)
    pe = pefile.PE(data=original, fast_load=True)
    try:
        for va, old, new in mod.SELECTION_CONSUMER_LIMIT_SITES:
            off = mod._va_to_file_offset(pe, va)
            assert original[off : off + len(old)] == old, hex(va)
            assert candidate[off : off + len(new)] == new, hex(va)
    finally:
        pe.close()


def test_selection_consumer_frame_and_clear_cover_all_50_words(original: bytes) -> None:
    candidate, _ = mod.build_candidate(original)
    pe = pefile.PE(data=original, fast_load=True)
    try:
        frame_off = mod._va_to_file_offset(pe, 0x0041DC40)
        frame = int.from_bytes(candidate[frame_off + 2:frame_off + 6], "little")
        clear_off = mod._va_to_file_offset(pe, 0x0041DC4C)
        clear_dwords = int.from_bytes(candidate[clear_off + 1:clear_off + 5], "little")
        assert frame == mod.CONSUMER_FRAME_BYTES
        assert mod.CONSUMER_WORD_BUFFER_OFFSET + 2 * mod.TARGET_CAPACITY <= frame + 0x10
        assert clear_dwords == mod.CONSUMER_CLEAR_DWORDS
        assert clear_dwords * 4 >= 2 * mod.TARGET_CAPACITY
    finally:
        pe.close()


def test_hit_test_append_limit_is_runtime_confirmed_and_patched_to_50(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    assert report["patched_hit_test_append_limit_sites"] == 1
    pe = pefile.PE(data=original, fast_load=True)
    try:
        for va, old, new in mod.HIT_TEST_APPEND_LIMIT_SITES:
            off = mod._va_to_file_offset(pe, va)
            assert original[off : off + len(old)] == old
            assert candidate[off : off + len(new)] == new
    finally:
        pe.close()


def test_original_is_not_mutated_and_wrong_hash_is_rejected(original: bytes) -> None:
    before = hashlib.sha256(original).hexdigest()
    mod.build_candidate(original)
    assert hashlib.sha256(original).hexdigest() == before
    with pytest.raises(ValueError):
        mod.build_candidate(b"not the pinned original")


def test_restore_requires_this_candidate_and_returns_exact_original(original: bytes) -> None:
    candidate, _ = mod.build_candidate(original)
    assert mod.restore_candidate(candidate, original) == original
    with pytest.raises(ValueError):
        mod.restore_candidate(candidate[:-1] + b"x", original)
