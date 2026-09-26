import hashlib
import importlib.util
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("shop_open_legacy_combos_2608.py")
spec = importlib.util.spec_from_file_location("shop_open_legacy_combos_2608", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

ROOT = Path("/home/dev_00/sharedfolder/260320_Syw2plus")
SOURCE = ROOT / "260921_temp/[ESL]Syw2plus 2608/[ESL]Syw2plus 2608.exe"
LEGACY = ROOT / "260921_temp/[ESL]Syw2plus 2606.exe"
LEGACY_VARIANTS = {
    "seven-generals": ROOT / "260921_temp/[ESL]Syw2plus 2606_장수7명_전비1600-200-3000.exe",
    "seven-generals-fixed-start": ROOT / "260921_temp/[ESL]Syw2plus 2606_장수7명_전비1600-200-3000_시작자리고정.exe",
}


@pytest.fixture(scope="module")
def original() -> bytes:
    if not SOURCE.exists():
        pytest.skip("local pinned ESL 2608 executable required")
    value = SOURCE.read_bytes()
    mod.SHOP.verify_original(value)
    return value


@pytest.fixture(scope="module")
def legacy() -> bytes:
    if not LEGACY.exists():
        pytest.skip("local pinned ESL 2606 reference required")
    value = LEGACY.read_bytes()
    mod.verify_legacy_2606(value)
    return value


def test_source_and_legacy_hashes_are_pinned(original, legacy):
    assert hashlib.sha256(original).hexdigest() == mod.SOURCE_SHA256
    assert hashlib.sha256(legacy).hexdigest() == mod.LEGACY_2606_SHA256
    assert len(original) == mod.SOURCE_FILE_SIZE
    assert len(legacy) == mod.LEGACY_2606_FILE_SIZE


def test_full_diff_inventory_matches_legacy_variants(original, legacy):
    for variant, chunks in mod.VARIANT_CHUNKS.items():
        assert len({chunk.offset for chunk in chunks}) == len(chunks)
        for chunk in chunks:
            assert legacy[chunk.offset : chunk.end] == chunk.old
            assert original[chunk.offset : chunk.end] == chunk.old
        if variant == "seven-generals":
            assert len(chunks) == 6
        else:
            assert len(chunks) == 8


def test_legacy_variant_sha_and_full_diff_inventory(legacy):
    for variant, path in LEGACY_VARIANTS.items():
        if not path.exists():
            pytest.skip(f"local pinned 2606 variant required: {path.name}")
        patched = path.read_bytes()
        mod.verify_legacy_variant(patched, variant)
        assert hashlib.sha256(patched).hexdigest() == mod.LEGACY_VARIANT_SHA256[variant]
        actual = mod._diff_ranges(legacy, patched)
        expected = sorted((chunk.offset, chunk.end) for chunk in mod.VARIANT_CHUNKS[variant])
        assert actual == expected
        for chunk in mod.VARIANT_CHUNKS[variant]:
            assert patched[chunk.offset : chunk.end] == chunk.new


def test_builds_two_expected_candidate_shas_without_mutating_source(original):
    before = hashlib.sha256(original).hexdigest()
    built = mod.build_candidates(original)
    assert hashlib.sha256(original).hexdigest() == before
    assert built["seven-generals"][1]["candidate_sha256"] == (
        "cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3"
    )
    assert built["seven-generals-fixed-start"][1]["candidate_sha256"] == (
        "f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973"
    )
    for candidate, report in built.values():
        assert report["shop_candidate_sha256"] == mod.SHOP_CANDIDATE_SHA256
        assert hashlib.sha256(candidate).hexdigest() == report["candidate_sha256"]


def test_combo_diff_is_exactly_the_declared_inventory(original):
    shop_candidate, _ = mod.SHOP.build_candidate(original)
    for variant, chunks in mod.VARIANT_CHUNKS.items():
        candidate, _ = mod.build_variant(original, variant)
        assert mod._diff_ranges(shop_candidate, candidate) == sorted(
            (chunk.offset, chunk.end) for chunk in chunks
        )


def test_restore_is_exact_original_for_both_variants(original):
    for variant, (candidate, _report) in mod.build_candidates(original).items():
        assert mod.restore_candidate(candidate, variant) == original


def test_context_and_old_byte_checks_refuse_unsupported_2608(original):
    mutated = bytearray(original)
    mutated[mod.SEVEN_GENERALS_CHUNKS[0].offset - 0x80] ^= 0x01
    with pytest.raises(mod.BuildAbortedError, match="context"):
        mod._check_source_context(bytes(mutated), mod.SEVEN_GENERALS_CHUNKS)

    mutated = bytearray(original)
    mutated[mod.SEVEN_GENERALS_CHUNKS[0].offset] = 0x06
    with pytest.raises(ValueError, match="SHA256"):
        mod.build_candidates(bytes(mutated))


def test_2606_reference_and_unknown_variant_are_refused(original, legacy):
    with pytest.raises(ValueError, match="size|SHA256"):
        mod.build_candidates(legacy)
    with pytest.raises(ValueError, match="unsupported"):
        mod.build_variant(original, "2606")
    wrong_legacy = bytearray(legacy)
    wrong_legacy[0x100] ^= 1
    with pytest.raises(ValueError, match="SHA256"):
        mod.verify_legacy_2606(bytes(wrong_legacy))


def test_write_candidates_is_copy_only_and_exclusive(original, tmp_path):
    source = tmp_path / "source.exe"
    source.write_bytes(original)
    one = tmp_path / "seven.exe"
    two = tmp_path / "fixed.exe"
    reports = mod.write_candidates(
        source,
        {"seven-generals": one, "seven-generals-fixed-start": two},
    )
    assert set(reports) == set(mod.VARIANT_CHUNKS)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == mod.SOURCE_SHA256
    with pytest.raises(FileExistsError):
        mod.write_candidates(
            source,
            {"seven-generals": one, "seven-generals-fixed-start": tmp_path / "new.exe"},
        )


def test_write_rejects_duplicate_output_paths(original, tmp_path):
    source = tmp_path / "source.exe"
    source.write_bytes(original)
    destination = tmp_path / "same.exe"
    with pytest.raises(ValueError, match="distinct"):
        mod.write_candidates(
            source,
            {"seven-generals": destination, "seven-generals-fixed-start": destination},
        )
