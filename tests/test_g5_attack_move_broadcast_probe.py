"""Regression contract for the G5 attack-move broadcast probe.

lap674 stopped relying on hitting an enemy sprite with the mouse (9
consecutive sprite hit-test failures across lap672/lap673) and instead counts
how many drag-selected units accept an attack-move order issued to a ground
point. These are the pure-logic pieces that do not require Wine/X11.
"""

from __future__ import annotations

from tools.g5_attack_move_broadcast_probe import (
    DESTINATION_OFFSET_FROM_WORKER,
    broadcast_summary,
    engaged_summary,
    is_attack_move,
    main,
    run_probe,
)


def test_is_attack_move_matches_live_command_state() -> None:
    assert is_attack_move({"command": 4, "pending_command": 0})
    assert not is_attack_move({"command": 3, "pending_command": 0})


def test_is_attack_move_matches_pending_low_word_even_without_live_state() -> None:
    # An attack-move order (A + ground click, no unit under the cursor)
    # flips the pending command's low 16 bits before the live +0x290 state
    # catches up; this is what lets a broadcast count as accepted the
    # instant the click lands.
    assert is_attack_move({"command": 1, "pending_command": 0x10004})
    assert not is_attack_move({"command": 1, "pending_command": 0x10003})


def test_is_attack_move_ignores_missing_fields() -> None:
    assert not is_attack_move({})
    assert not is_attack_move({"command": None, "pending_command": None})


def test_broadcast_summary_counts_hits_from_either_sample() -> None:
    before = [{"slot": 10, "command": 1, "pending_command": 0}, {"slot": 11, "command": 1, "pending_command": 0}]
    immediate = [{"slot": 10, "command": 1, "pending_command": 0x10004}, {"slot": 11, "command": 1, "pending_command": 0}]
    delayed = [{"slot": 10, "command": 4, "pending_command": 0}, {"slot": 11, "command": 1, "pending_command": 0}]
    summary = broadcast_summary(before, immediate, delayed)
    assert summary["selected_count"] == 2
    assert summary["attack_move_command_count"] == 1
    assert not summary["all_selected_broadcast"]


def test_broadcast_summary_all_selected_requires_every_slot() -> None:
    before = [{"slot": 1, "command": 1, "pending_command": 0}]
    immediate = [{"slot": 1, "command": 4, "pending_command": 0}]
    delayed = [{"slot": 1, "command": 4, "pending_command": 0}]
    summary = broadcast_summary(before, immediate, delayed)
    assert summary["all_selected_broadcast"]


def test_broadcast_summary_empty_selection_is_not_all_broadcast() -> None:
    summary = broadcast_summary([], [], [])
    assert summary["selected_count"] == 0
    assert not summary["all_selected_broadcast"]


def test_engaged_summary_requires_command_and_target_match() -> None:
    final = [
        {"slot": 1, "command": 4, "pending_target_uid": 99},
        {"slot": 2, "command": 4, "pending_target_uid": 1},
        {"slot": 3, "command": 3, "pending_target_uid": 99},
    ]
    summary = engaged_summary(final, enemy_handle=99)
    assert summary["engaged_target_match_count"] == 1
    assert summary["rows"][0]["engaged_target_match"]
    assert not summary["rows"][1]["engaged_target_match"]
    assert not summary["rows"][2]["engaged_target_match"]


def test_destination_offset_clears_the_dense_fixture_footprint() -> None:
    # The dense fixture grid spans dx -3..3, dy -3..4 around the worker
    # (tools/g5_candidate_drag_probe.py:dense_fixture_requests); the seeded
    # enemy must sit outside that box so it is not already inside a
    # broadcast unit's aggro radius before the attack-move click is issued.
    dx, dy = DESTINATION_OFFSET_FROM_WORKER
    assert abs(dx) > 3 or abs(dy) > 4
    assert all(abs(v) < 20 for v in DESTINATION_OFFSET_FROM_WORKER)


def test_module_exposes_runtime_entry_points() -> None:
    assert callable(run_probe)
    assert callable(main)
