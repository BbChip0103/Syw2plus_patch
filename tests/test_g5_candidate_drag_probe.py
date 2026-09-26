"""Regression contract for the live-worker G5 runtime fixture."""

from __future__ import annotations

from tools.g5_candidate_drag_probe import (
    ATTACK_TARGET_SCREEN,
    ATTACK_TARGET_OFFSET,
    attack_observation,
    dense_fixture_requests,
)


def test_g5_fixture_shifts_one_row_positive_and_keeps_55_unique_cells() -> None:
    worker = {"x": 142, "y": 42}

    requests = dense_fixture_requests(worker)
    coordinates = {(item["x"], item["y"]) for item in requests}

    assert len(requests) == 55
    assert len(coordinates) == 55
    assert (worker["x"], worker["y"]) not in coordinates
    assert {y - worker["y"] for _, y in coordinates} == {-3, -2, -1, 0, 1, 2, 3, 4}
    assert min(x for x, _ in coordinates) == worker["x"] - 3
    assert max(x for x, _ in coordinates) == worker["x"] + 3


def test_g5_attack_observation_requires_command_and_target_for_every_member() -> None:
    before = [{"slot": 10, "command": 0}, {"slot": 11, "command": 0}]
    after = [
        {"slot": 10, "command": 1, "pending_command": 0x10001, "pending_target_uid": 0},
        {"slot": 11, "command": 1, "pending_command": 0x10001, "pending_target_uid": 0},
    ]
    immediate = [
        {"slot": 10, "command": 4, "pending_command": 0x10004, "pending_target_uid": 99},
        {"slot": 11, "command": 4, "pending_command": 0x10004, "pending_target_uid": 99},
    ]

    report = attack_observation(before, after, 99, immediate=immediate, target_uid=99)

    assert report["pass"] is True
    assert report["attack_command_count"] == 2
    assert report["target_match_count"] == 2


def test_g5_attack_observation_rejects_non_attack_or_wrong_target() -> None:
    before = [{"slot": 10, "command": 0}, {"slot": 11, "command": 0}]
    after = [
        {"slot": 10, "command": 1, "pending_command": 0x10001, "pending_target_uid": 99},
        {"slot": 11, "command": 4, "pending_command": 0x10004, "pending_target_uid": 100},
    ]

    report = attack_observation(before, after, 99, target_uid=99)

    assert report["pass"] is False
    assert report["attack_command_count"] == 1
    assert report["target_match_count"] == 1


def test_g5_attack_input_contract_is_world_and_screen_pinned() -> None:
    assert ATTACK_TARGET_OFFSET == (7, -1)
    assert ATTACK_TARGET_SCREEN == (580, 450)
