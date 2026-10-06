from __future__ import annotations

import pytest

from tools import g2_esl2608_phase_b_command_probe as probe


def test_phase_b_inputs_and_scope_are_pinned() -> None:
    assert set(probe.LANES) == {"normal", "fixed_start"}
    assert set(probe.BUTTONS) == {"stop", "attack", "patrol", "hold"}
    assert probe.MOVE_PENDING_LOW16 == 3
    assert probe.ATTACK_PENDING_LOW16 == 4


def test_phase_b_recreates_current_candidates_when_inputs_exist() -> None:
    if not probe.LANES["normal"].is_file():
        pytest.skip("pinned ESL2608 inputs are unavailable")
    for lane, source in probe.LANES.items():
        candidate, _report = probe.build_candidate(source.read_bytes())
        assert probe._digest(candidate) == probe.EXPECTED_CANDIDATE[lane]


def test_observe_classifies_selected_and_unselected(monkeypatch: pytest.MonkeyPatch) -> None:
    rows = {
        1: {"slot": 1, "command": 0, "pending": 0, "pending_xy": 0},
        2: {"slot": 2, "command": 0, "pending": 0, "pending_xy": 0},
        3: {"slot": 3, "command": 0, "pending": 0, "pending_xy": 0},
    }
    calls = {"n": 0}

    def fake_row(_pid: int, slot: int, *, candidate: bool) -> dict[str, int]:
        del candidate
        if calls["n"] > 0 and slot in (1, 2):
            return {**rows[slot], "pending": 0x1000003}
        return rows[slot]

    monkeypatch.setattr(probe, "_row", fake_row)
    monkeypatch.setattr(probe.time, "sleep", lambda _seconds: calls.__setitem__("n", calls["n"] + 1))
    result = probe._observe(1, [1, 2], 3, candidate=False, action=lambda: None,
                            label="move", window=0.001,
                            predicate=lambda row: (row["pending"] & 0xFFFF) == 3)
    assert result["selected_match_count"] == 2
    assert result["selected_all_matched"] is True
    assert result["sentinel_changed"] is False


def test_combat_observation_accepts_target_destruction(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        probe, "_combat_target_snapshot",
        lambda _pid, _slot, *, candidate: {
            "exists": False, "owner": 1, "hp": 100, "x": 0, "y": 0, "command": 0,
        },
    )
    result = probe._observe_combat_target(
        1, 77, {"exists": True, "owner": 1, "hp": 100, "x": 5, "y": 5, "command": 1},
        candidate=False,
    )
    assert result["destroyed"] is True
    assert result["damage_observed"] is False
    assert result["combat_observed"] is True
