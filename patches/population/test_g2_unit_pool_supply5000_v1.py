from pathlib import Path
import hashlib

from patches.population.fixed_supply_5000 import EDITS
from patches.population.g2_unit_pool_supply5000_v1 import build_candidate


ORIGINAL = Path(__file__).resolve().parents[2] / "Syw2plus" / "syw2plus_original.exe"


def test_combined_candidate_applies_exact_supply_edits_after_pool_relocation() -> None:
    candidate, report = build_candidate(ORIGINAL.read_bytes(), 1210)
    assert report["capacity"] == 1210
    assert len(report["supply_edits"]) == len(EDITS)
    for offset, _before, after in EDITS:
        assert candidate[offset : offset + len(after)] == after
    assert report["sha256"]


def test_n1250_runtime_probe_candidate_has_pinned_identity() -> None:
    # SHA changed under W19 (lap439/440): the underlying pool scanner now
    # rejects 25 false-positive imm sites it used to (wrongly) relocate --
    # see test_g2_unit_pool_expansion_v1.py::
    # test_fixup_site_counts_match_prior_independent_probes.
    candidate, report = build_candidate(ORIGINAL.read_bytes(), 1250)
    expected = "c8f7e015e4f6b4791996285e9b0325b5b33a694795a2b478c33c380dac1d87ff"
    assert report["sha256"] == expected
    assert hashlib.sha256(candidate).hexdigest() == expected
