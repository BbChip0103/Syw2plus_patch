from __future__ import annotations

import hashlib

import pytest

from patches.population import g2_esl2608_runtime_layout as runtime_layout
from tools import g2_esl2608_phase_a_shift_probe as probe


def test_phase_a_lanes_are_pinned_to_lap787_inputs() -> None:
    assert set(probe.LANES) == {"normal", "fixed_start"}
    assert all(len(value) == 64 for value in probe.EXPECTED_BASELINE.values())
    assert all(len(value) == 64 for value in probe.EXPECTED_CANDIDATE.values())
    assert probe.SELECTION_CAPACITY == 20


def test_build_candidate_recreates_both_current_candidates_when_inputs_exist() -> None:
    if not probe.LEGACY.is_file() or not probe.STOCK.is_file() or not all(
        path.is_file() for path in probe.LANES.values()
    ):
        pytest.skip("pinned ESL2608 inputs are unavailable")
    for lane, source in probe.LANES.items():
        candidate, report = probe.build_candidate(source.read_bytes())
        assert hashlib.sha256(candidate).hexdigest() == probe.EXPECTED_CANDIDATE[lane]
        assert report["candidate_sha256"] == probe.EXPECTED_CANDIDATE[lane]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == probe.EXPECTED_BASELINE[lane]


def test_selection_snapshot_accepts_only_stock_capacity(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_read(_pid: int, address: int, size: int) -> bytes:
        if address == probe.STOCK_SELECTION_BASE:
            return (20).to_bytes(4, "little", signed=True)
        return (address // 4).to_bytes(size, "little")

    monkeypatch.setattr(probe, "read_memory", fake_read)
    snapshot = probe.selection_snapshot(1)
    assert snapshot["count"] == 20
    assert snapshot["unique_slots"] == 20


def test_selection_snapshot_rejects_candidate_cap_in_this_g2_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(probe, "read_memory", lambda _pid, _address, _size: (21).to_bytes(4, "little", signed=True))
    with pytest.raises(probe.ProbeError, match="0..20"):
        probe.selection_snapshot(1)


def test_esl2608_layout_matches_builder_report_and_rejects_generic_base() -> None:
    resolved = runtime_layout.from_build_report({
        "pool_base_va": "0x0112e000",
        "relocation_delta": "0xa2000",
    })
    assert resolved.unit_pool_base == 0x0112E000
    assert resolved.unit_existence_base == 0x018849F8
    assert resolved.unit_stride == 0x758
    with pytest.raises(ValueError, match="unexpected ESL2608 pool base"):
        runtime_layout.from_pool_base(0x0108C000)


def test_esl2608_layout_rejects_wrong_builder_delta() -> None:
    with pytest.raises(ValueError, match="relocation delta"):
        runtime_layout.from_build_report({
            "pool_base_va": "0x0112e000",
            "relocation_delta": "0x0",
        })
