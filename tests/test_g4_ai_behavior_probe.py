"""Pure regression tests for the G4 AI behavior baseline metric computation.

No game/EXE/Wine dependency: these feed synthetic ``g4_ai_smoke.samples``
(the same schema ``tools/runtime_env.py g1-baseline`` records) straight into
``compute_behavior_metrics``.
"""
from __future__ import annotations

import pytest

from tools.g4_ai_behavior_probe import compute_behavior_metrics


def _unit(slot, owner, unit_type, hp, command=1, internal_id=None):
    return {
        "slot": slot, "owner": owner, "type": unit_type, "hp": hp, "command": command,
        "internal_id": internal_id if internal_id is not None else slot,
    }


def _player(owner, rice, wood):
    return {"owner": owner, "rice": rice, "wood": wood}


def test_identifies_worker_as_lower_hp_of_initial_pair_and_counts_idle():
    samples = [
        {
            "elapsed_seconds": 0.0,
            "players": [_player(0, 100, 100), _player(1, 100, 100)],
            "units": [
                _unit(1, 0, 49, hp=1000, command=1, internal_id=1),  # HQ (high HP)
                _unit(2, 0, 7, hp=25, command=1, internal_id=2),  # worker (low HP), idle
                _unit(1, 1, 49, hp=1000, command=1, internal_id=101),
                _unit(2, 1, 7, hp=25, command=1, internal_id=102),
            ],
        },
        {
            "elapsed_seconds": 60.0,
            "players": [_player(0, 160, 130), _player(1, 90, 80)],
            "units": [
                _unit(1, 0, 49, hp=1000, command=1, internal_id=1),
                _unit(2, 0, 7, hp=25, command=3, internal_id=2),  # now moving, not idle
                _unit(3, 0, 21, hp=40, command=1, internal_id=3),  # newly produced soldier
                _unit(1, 1, 49, hp=1000, command=1, internal_id=101),
                _unit(2, 1, 7, hp=25, command=1, internal_id=102),
            ],
        },
    ]
    result = compute_behavior_metrics(samples)
    owner0 = result["owners"]["0"]
    assert owner0["worker_type"] == 7
    assert owner0["hq_type"] == 49
    assert owner0["initial_unit_count"] == 2
    assert owner0["production_count_proxy"] == 1  # internal_id 3 is new
    assert owner0["idle_worker_count_mean"] == pytest.approx(0.5)  # idle at t0, not at t60
    assert owner0["idle_worker_count_max"] == 1
    assert owner0["army_unit_count_first"] == 0
    assert owner0["army_unit_count_last"] == 1  # the new soldier, excludes HQ/worker types
    assert owner0["resource_stock_first"] == 200
    assert owner0["resource_stock_last"] == 290
    assert owner0["resource_income_per_min"] == pytest.approx(90.0)

    owner1 = result["owners"]["1"]
    assert owner1["production_count_proxy"] == 0
    assert owner1["resource_income_per_min"] == pytest.approx(-30.0)


def test_first_attack_elapsed_seconds_is_earliest_command_4_sample():
    samples = [
        {
            "elapsed_seconds": 0.0,
            "players": [_player(0, 0, 0), _player(1, 0, 0)],
            "units": [
                _unit(1, 0, 49, hp=1000, internal_id=1),
                _unit(2, 0, 7, hp=25, internal_id=2),
                _unit(1, 1, 49, hp=1000, internal_id=101),
                _unit(2, 1, 7, hp=25, internal_id=102),
            ],
        },
        {
            "elapsed_seconds": 10.0,
            "players": [_player(0, 0, 0), _player(1, 0, 0)],
            "units": [
                _unit(1, 0, 49, hp=1000, internal_id=1),
                _unit(2, 0, 7, hp=25, internal_id=2),
                _unit(3, 0, 21, hp=40, command=4, internal_id=3),  # attacking
                _unit(1, 1, 49, hp=1000, internal_id=101),
                _unit(2, 1, 7, hp=25, internal_id=102),
            ],
        },
    ]
    result = compute_behavior_metrics(samples)
    assert result["owners"]["0"]["first_attack_elapsed_seconds"] == 10.0
    assert result["owners"]["1"]["first_attack_elapsed_seconds"] is None


def test_raises_on_empty_samples():
    with pytest.raises(ValueError):
        compute_behavior_metrics([])


def test_handles_owner_with_fewer_than_two_initial_units():
    samples = [
        {
            "elapsed_seconds": 0.0,
            "players": [_player(0, 0, 0), _player(1, 0, 0)],
            "units": [_unit(1, 0, 49, hp=1000, internal_id=1)],
        },
    ]
    result = compute_behavior_metrics(samples)
    owner0 = result["owners"]["0"]
    assert owner0["worker_type"] is None
    assert owner0["hq_type"] is None
    assert owner0["initial_unit_count"] == 1
