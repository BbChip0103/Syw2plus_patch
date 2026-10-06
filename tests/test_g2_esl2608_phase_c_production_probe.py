from __future__ import annotations

import pytest

from tools import g2_esl2608_phase_c_production_probe as probe


def test_phase_c_inputs_and_scope_are_pinned() -> None:
    assert set(probe.LANES) == {"normal", "fixed_start"}
    assert probe.WORKER_PRODUCTION == (668, 540)
    assert probe.RALLY_MODE_BUTTON == (704, 503)
    assert probe.HERO_PRODUCTION_BY_NATION == {1: (776, 540), 2: (704, 540), 3: (704, 540)}
    assert probe.RALLY_POINT == (600, 300)
    assert probe.HERO_COUNT_ADDRESS == 0x009570F0
    assert probe.PLAYER_STRUCT_STRIDE == 0x3ABC


def test_phase_c_static_ui_contract_is_pinned() -> None:
    assert probe.RALLY_COMMAND == 0x15
    assert probe.RALLY_DESCRIPTOR == 0x11
    assert probe.COMMAND_SLOT_BASE == 0x008930A6
    assert probe.ACTIVE_ACTION_ADDRESS == 0x00892FFE
    assert probe.COMMAND_GRID_ORIGIN == (668, 503)
    assert probe.COMMAND_GRID_STEP == 36
    assert probe.RALLY_WRITER_VAS == (0x004125A5, 0x004125AF)
    assert probe.HERO_ELIGIBILITY_VA == 0x0043E7F0
    assert probe.HERO_ELIGIBILITY_CALLERS == (0x00406B68, 0x0048D1B7)


def test_rally_grid_cell_maps_live_slot_to_first_row() -> None:
    assert probe._command_grid_cell(3) == (776, 503)
    assert probe._command_grid_cell_any(5) == (704, 540)
    assert probe._command_grid_cell_any(8) == (668, 576)


def test_phase_c_recreates_current_candidates_when_inputs_exist() -> None:
    if not probe.LANES["normal"].is_file():
        pytest.skip("pinned ESL2608 inputs are unavailable")
    for lane, source in probe.LANES.items():
        candidate, _report = probe.build_candidate(source.read_bytes())
        assert probe._digest(candidate) == probe.EXPECTED_CANDIDATE[lane]
