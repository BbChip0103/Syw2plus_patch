import hashlib
from pathlib import Path

import pefile
import pytest

from patches.selection import g5_selection_cap50_v1 as v1
from patches.selection import g5_selection_cap50_v2 as v2
from patches.selection import g5_selection_cap50_v2_partial as partial

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    return SOURCE.read_bytes()


def _target(candidate: bytes, site: int) -> int:
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        off = v1._va_to_file_offset(pe, site)
    finally:
        pe.close()
    return candidate[off]


def test_rejects_unknown_hook() -> None:
    with pytest.raises(ValueError):
        partial.build_candidate(b"\x00" * 4, skip="H4")


@pytest.mark.parametrize("skip", partial.HOOKS)
def test_applies_exactly_two_of_three_hooks(original: bytes, skip: str) -> None:
    candidate, report = partial.build_candidate(original, skip=skip)
    assert len(candidate) == len(original)
    assert report["skip"] == skip
    assert set(report["applied_hooks"]) == set(partial.HOOKS) - {skip}
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()

    v1_candidate, _v1_report = v1.build_candidate(original)
    sites = {"H1": v2.H1_SITE, "H2": v2.H2_SITE, "H3": v2.H3_SITE}
    for name, site in sites.items():
        pe = pefile.PE(data=candidate, fast_load=True)
        try:
            off = v1._va_to_file_offset(pe, site)
        finally:
            pe.close()
        if name == skip:
            # The skipped hook's site keeps its v1 bytes: no jump installed.
            assert candidate[off : off + 9] == v1_candidate[off : off + 9]
        else:
            assert candidate[off] == 0xE9


def test_all_three_partial_variants_and_full_v2_are_pairwise_distinct(original: bytes) -> None:
    shas = {skip: partial.build_candidate(original, skip=skip)[1]["candidate_sha256"] for skip in partial.HOOKS}
    full_candidate, full_report = v2.build_candidate(original)
    all_shas = list(shas.values()) + [full_report["candidate_sha256"]]
    assert len(set(all_shas)) == len(all_shas)
