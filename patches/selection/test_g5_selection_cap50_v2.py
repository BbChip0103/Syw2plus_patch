import hashlib
import importlib.util
import sys
from pathlib import Path

import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v2.py")
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


def _offset(pe: pefile.PE, va: int) -> int:
    return mod._va_to_file_offset(pe, va)


def _target(candidate: bytes, site: int) -> int:
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        off = _offset(pe, site)
    finally:
        pe.close()
    assert candidate[off] == 0xE9
    return site + 5 + int.from_bytes(candidate[off + 1 : off + 5], "little", signed=True)


def test_build_is_v1_plus_three_pinned_hooks_and_private_caves(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    v1_candidate, v1_report = mod.v1.build_candidate(original)
    assert len(candidate) == len(original)
    assert report["v1_candidate_sha256"] == hashlib.sha256(v1_candidate).hexdigest()
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] != report["original_sha256"]
    assert report["candidate_sha256"] != v1_report["candidate_sha256"]
    assert _target(candidate, mod.H1_SITE) == mod.H1_CAVE
    assert _target(candidate, mod.H2_SITE) == mod.H2_CAVE
    assert _target(candidate, mod.H3_SITE) == mod.H3_CAVE

    pe = pefile.PE(data=original, fast_load=True)
    try:
        for site, old in ((mod.H1_SITE, mod.H1_OLD), (mod.H2_SITE, mod.H2_OLD), (mod.H3_SITE, mod.H3_OLD)):
            off = _offset(pe, site)
            assert v1_candidate[off : off + len(old)] == old
            assert candidate[off : off + len(old)] != old
        for address, payload in ((mod.H1_CAVE, mod.H1_CODE), (mod.H2_CAVE, mod.H2_CODE), (mod.H3_CAVE, mod.H3_CODE)):
            off = _offset(pe, address)
            assert candidate[off : off + len(payload)] == payload
    finally:
        pe.close()


def test_cave_is_mapped_inside_text_without_raw_growth(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    assert len(candidate) == len(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        text = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".text")
        text_start = mod.IMAGE_BASE + int(text.VirtualAddress)
        assert text_start + int(text.Misc_VirtualSize) >= mod.CAVE_END
        assert int(text.Misc_VirtualSize) <= int(text.SizeOfRawData)
        assert report["cave"]["cave_end_exclusive"] == mod.CAVE_END
        assert report["cave"]["text_virtual_size"] == int(text.Misc_VirtualSize)
    finally:
        pe.close()


def test_hook_code_contains_expected_bounds_calls_and_rejoin_targets(original: bytes) -> None:
    candidate, _ = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        blobs = []
        for address, payload in ((mod.H1_CAVE, mod.H1_CODE), (mod.H2_CAVE, mod.H2_CODE), (mod.H3_CAVE, mod.H3_CODE)):
            off = _offset(pe, address)
            blobs.append(candidate[off : off + len(payload)])
        h1, h2, h3 = blobs
        assert b"\xc8\x90\x89\x00" in h1  # stock existence array reference
        assert b"\x44\x03\x00\x00" in h1  # unit +0x344 clear
        assert (0x0108C054).to_bytes(4, "little") in h2
        assert bytes.fromhex("0f b7 03 69 c0 58 07 00 00 05 d4 ba 66 00") in h2
        assert (0x0040F750).to_bytes(4, "little") not in h2  # call is rel32, not a raw pointer
        assert b"\x44\x03\x00\x00" in h3
        assert b"\x32" in h3  # 50 guard
        # FUN_0040F790 is stdcall-like (ret 4); H3 must not clean its
        # argument a second time and shift the pushad frame before FUN_0040F7D0.
        assert bytes.fromhex("e8 63 22 f3 ff 83 c4 04") in h3
        assert bytes.fromhex("e8 79 aa f2 ff 83 c4 04 83 f8 01") not in h3
        assert bytes.fromhex("e8 79 aa f2 ff 90 90 90 83 f8 01") in h3
        assert (0x00416F40).to_bytes(4, "little") not in h3
        assert len(h1) < mod.H2_CAVE - mod.H1_CAVE
        assert len(h2) < mod.H3_CAVE - mod.H2_CAVE
    finally:
        pe.close()


def test_ai_remove_center_and_other_untouched_ranges_are_byte_identical(original: bytes) -> None:
    candidate, _ = mod.build_candidate(original)
    pe = pefile.PE(data=original, fast_load=True)
    try:
        for start, end in mod.IMMUTABLE_RANGES:
            old = _offset(pe, start)
            new = _offset(pe, end - 1) + 1
            assert candidate[old:new] == original[old:new], (hex(start), hex(end))
    finally:
        pe.close()


def test_original_is_not_mutated_and_restore_is_exact(original: bytes) -> None:
    before = hashlib.sha256(original).hexdigest()
    candidate, _ = mod.build_candidate(original)
    assert hashlib.sha256(original).hexdigest() == before == mod.ORIGINAL_SHA256
    assert mod.restore_candidate(candidate, original) == original
    with pytest.raises(ValueError):
        mod.restore_candidate(candidate[:-1] + b"x", original)
