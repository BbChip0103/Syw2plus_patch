import hashlib
from pathlib import Path

import pytest

from patches.selection import g5_selection_cap50_bisect as mod
from patches.selection import g5_selection_cap50_v1 as v1
from patches.selection import g5_selection_cap50_v2 as v2

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    return SOURCE.read_bytes()


def test_every_builder_preserves_length_and_original_bytes(original: bytes) -> None:
    before = hashlib.sha256(original).hexdigest()
    shas = set()
    for name, builder in mod.BUILDERS.items():
        candidate, report = builder(original)
        assert len(candidate) == len(original), name
        assert hashlib.sha256(original).hexdigest() == before, name
        assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest(), name
        assert report["original_sha256"] == mod.ORIGINAL_SHA256
        shas.add(report["candidate_sha256"])
    # Every bundle produces a distinct byte-for-byte result.
    assert len(shas) == len(mod.BUILDERS)


def test_g1_g3_g5_leave_the_stock_selection_array_untouched(original: bytes) -> None:
    for name in ("G1", "G3", "G5"):
        candidate, report = mod.BUILDERS[name](original)
        assert report["selection_base"] == mod.STOCK_SELECTION_BASE, name
        assert report["selection_capacity"] == mod.STOCK_SELECTION_CAPACITY, name
        assert len(candidate) == len(original)


def test_g2_alone_matches_v1s_relocation_target(original: bytes) -> None:
    candidate, report = mod.build_g2_relocation_only(original)
    assert report["selection_base"] == v1.SELECTION_BASE
    assert report["selection_capacity"] == v1.TARGET_CAPACITY
    # G2 alone must not also apply v1's hit-test/consumer/rotation edits.
    full_v1, _ = v1.build_candidate(original)
    assert candidate != full_v1


def test_v1_full_matches_v1_build_candidate(original: bytes) -> None:
    candidate, report = mod.build_v1_full(original)
    expected, expected_report = v1.build_candidate(original)
    assert candidate == expected
    assert report["candidate_sha256"] == expected_report["candidate_sha256"]


def test_v2_full_matches_v2_build_candidate(original: bytes) -> None:
    candidate, report = mod.build_v2_full(original)
    expected, expected_report = v2.build_candidate(original)
    assert candidate == expected
    assert report["candidate_sha256"] == expected_report["candidate_sha256"]


def test_g4_hooks_alone_are_not_isolable_on_the_plain_original(original: bytes) -> None:
    """v2's H1 hook site overlaps a DIRECT_SITES operand, so its pinned old
    bytes only match a v1-relocated candidate, never the plain original."""
    pe = None
    import pefile

    pe = pefile.PE(data=original, fast_load=True)
    try:
        off = v2._va_to_file_offset(pe, v2.H1_SITE)
        actual = original[off : off + len(v2.H1_OLD)]
        assert actual != v2.H1_OLD
    finally:
        pe.close()
    assert "G4" not in mod.BUILDERS
