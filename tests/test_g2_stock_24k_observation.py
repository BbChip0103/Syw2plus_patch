"""Offline contract tests for the default-off G2 stock observer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tools import runtime_env


class _Clock:
    def __init__(self) -> None:
        self.value = 0.0

    def monotonic(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


def _gate() -> dict[str, Any]:
    return {
        "goal": runtime_env.G2_CREATION_GOAL,
        "candidate": runtime_env.G2_CREATION_CANDIDATE,
        "bridge_sha256": runtime_env.G2_APPROVED_BRIDGE_SHA256,
        "lifecycle": "load",
        "fresh_creation_gate": {"status": "PASS", "units": 16},
        "load_result": {
            "status": "PASS",
            "classification": "G2_STOCK_FRESH_LOAD_BOUNDARY_PASS",
            "save_sha256": runtime_env.G2_STOCK_24K_SAVE_SHA256,
            "witness_sha256": runtime_env.G2_STOCK_24K_WITNESS_SHA256,
        },
        "post_load_effects": {
            "ui_actions": 0, "input_actions": 0, "bridge_requests": 0,
            "save_actions": 0, "stress_interventions": False,
        },
    }


def _snapshot(tick: int, *, changed_id: bool = False) -> dict[str, Any]:
    players = [
        {"owner": owner, "cap": 5000, "count": 145, "used": 5000,
         "reserved": 10 if owner == 4 else 0,
         "resources": {"food": 1000 + owner, "gold": 2000 + owner}}
        for owner in range(8)
    ]
    units: list[dict[str, Any]] = []
    for owner in range(8):
        slot = owner * 2
        unit_id = (200 if changed_id else 100) + owner
        units.append({"internal_id": unit_id, "slot": slot, "owner": owner,
                      "type": 49, "hp": 0 if owner == 7 else 100})
        units.append({"internal_id": 300 + owner, "slot": slot + 1, "owner": owner,
                      "type": 7, "hp": 100})
    return {"ps": 3, "tick": tick, "players": players, "units": units}


def _observer_kwargs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    monkeypatch.setattr(runtime_env, "G2_ARTIFACT_ROOT", tmp_path)
    return {"enabled": True, **_gate()}


def test_observation_is_default_off_and_does_not_read_or_create_output(tmp_path: Path) -> None:
    calls: list[str] = []

    def reader(_detailed: bool) -> dict[str, Any]:
        calls.append("read")
        return {}

    result = runtime_env.g2_stock_24k_observe(
        tmp_path / "disabled", snapshot_reader=reader,
    )
    assert result == {
        "status": "DISABLED", "observation_opt_in": False,
        "product_pass_claim": False, "samples": 0,
    }
    assert calls == []
    assert not (tmp_path / "disabled").exists()


def test_observation_gate_rejects_wrong_profile_or_postload_effects() -> None:
    args = _gate()
    with pytest.raises(runtime_env.RuntimeSafetyError, match="fixed-supply"):
        runtime_env.validate_g2_stock_24k_observation_gate(
            enabled=True, **{**args, "candidate": "wrong.exe"}
        )
    with pytest.raises(runtime_env.RuntimeSafetyError, match="post-load"):
        runtime_env.validate_g2_stock_24k_observation_gate(
            enabled=True, **{**args, "post_load_effects": {"ui_actions": 1}}
        )


def test_observation_streams_duration_milestone_and_separates_dead_occupied_units(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _Clock()

    def full_reader(_detailed: bool) -> dict[str, Any]:
        tick = 1000 + int(clock.value // 5) * 6000
        return _snapshot(tick, changed_id=clock.value >= 5)

    def light_reader() -> dict[str, Any]:
        tick = 1000 + int(clock.value // 5) * 6000
        return {"ps": 3, "tick": tick}

    result = runtime_env.g2_stock_24k_observe(
        tmp_path / "observe", snapshot_reader=full_reader,
        light_reader=light_reader, process_reader=lambda: {"alive": True, "pss_bytes": 1234},
        monotonic=clock.monotonic, sleep=clock.sleep,
        **_observer_kwargs(tmp_path, monkeypatch),
    )
    assert result["status"] == "PASS_DURATION_MILESTONE"
    assert result["attained_tick_delta"] == 24000
    assert result["product_pass_claim"] is False
    assert result["death_reuse"] == "IDENTITY_REUSE_OBSERVED_DEATH_UNPROVEN"
    assert any(event["reuse_claimed"] is False for event in result["events"])
    lines = (tmp_path / "observe" / "samples.jsonl").read_text().splitlines()
    assert len(lines) == result["samples"]
    sample = json.loads(lines[0])
    assert len(sample["snapshot"]["roster_by_owner"]) == 8
    assert sample["snapshot"]["occupied_dead_unit_count"] == 1
    assert sample["snapshot"]["live_unit_count"] == 15
    assert sample["tick_bracket"]["atomic_ledger_proof"] is False


def test_stalled_ticks_hit_wall_timeout_without_fake_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _Clock()
    result = runtime_env.g2_stock_24k_observe(
        tmp_path / "timeout", snapshot_reader=lambda _detailed: _snapshot(1000),
        light_reader=lambda: {"ps": 3, "tick": 1000},
        monotonic=clock.monotonic, sleep=clock.sleep,
        **_observer_kwargs(tmp_path, monkeypatch),
    )
    assert result["status"] == "TIMEOUT_PARTIAL"
    assert result["attained_tick_delta"] == 0
    assert result["product_pass_claim"] is False


def test_tick_reversal_is_partial_not_wrapped_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _Clock()
    full_ticks = iter((1000, 7000, 500))
    current = [1000]

    def full_reader(_detailed: bool) -> dict[str, Any]:
        current[0] = next(full_ticks, 500)
        return _snapshot(current[0])

    result = runtime_env.g2_stock_24k_observe(
        tmp_path / "reverse", snapshot_reader=full_reader,
        light_reader=lambda: {"ps": 3, "tick": current[0]},
        monotonic=clock.monotonic, sleep=clock.sleep,
        **_observer_kwargs(tmp_path, monkeypatch),
    )
    assert result["status"] == "TICK_REVERSAL_PARTIAL"
    assert result["reason"] and "decreased" in result["reason"]
    assert result["product_pass_claim"] is False


def test_invalid_wall_clock_is_partial(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    readings = iter((0.0, -1.0))

    def clock() -> float:
        return next(readings, -1.0)

    result = runtime_env.g2_stock_24k_observe(
        tmp_path / "clock", snapshot_reader=lambda _detailed: _snapshot(1000),
        light_reader=lambda: {"ps": 3, "tick": 1000},
        monotonic=clock, sleep=lambda _seconds: None,
        **_observer_kwargs(tmp_path, monkeypatch),
    )
    assert result["status"] == "INVALID_CLOCK_PARTIAL"
    assert result["product_pass_claim"] is False


def test_reader_returning_after_wall_ceiling_cannot_claim_duration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _Clock()

    def slow_reader(_detailed: bool) -> dict[str, Any]:
        clock.value = runtime_env.G2_STOCK_OBSERVATION_WALL_SECONDS + 1
        return _snapshot(100000)

    result = runtime_env.g2_stock_24k_observe(
        tmp_path / "late", snapshot_reader=slow_reader,
        light_reader=lambda: {"ps": 3, "tick": 100000},
        monotonic=clock.monotonic, sleep=clock.sleep,
        **_observer_kwargs(tmp_path, monkeypatch),
    )
    assert result["status"] == "TIMEOUT_PARTIAL"
    assert result["product_pass_claim"] is False


def _passing_load_result() -> dict[str, Any]:
    return {
        "status": "PASS", "pass": True,
        "classification": "G2_STOCK_FRESH_LOAD_BOUNDARY_PASS",
        "save_sha256": runtime_env.G2_STOCK_24K_SAVE_SHA256,
        "witness_sha256": runtime_env.G2_STOCK_24K_WITNESS_SHA256,
    }


def test_parent_dispatch_is_default_off_and_failed_load_never_collects() -> None:
    calls: list[str] = []
    def invoke() -> dict[str, Any]:
        calls.append("collector")
        return {"status": "OBSERVING"}
    disabled = runtime_env._g2_stock_24k_dispatch_after_load(
        requested=False, load_result=None, invoke=invoke,
    )
    assert disabled["status"] == "DISABLED"
    assert disabled["collector_calls"] == 0
    rejected = runtime_env._g2_stock_24k_dispatch_after_load(
        requested=True, load_result={**_passing_load_result(), "witness_sha256": "wrong"}, invoke=invoke,
    )
    assert rejected["status"] == "SKIPPED_LOAD_NOT_PASS"
    assert rejected["collector_calls"] == 0
    assert calls == []


def test_parent_dispatch_invokes_once_after_pinned_load_and_suppresses_postload_actions() -> None:
    calls: list[str] = []

    def invoke() -> dict[str, Any]:
        calls.append("collector")
        return {"status": "TIMEOUT_PARTIAL", "product_pass_claim": False}

    result = runtime_env._g2_stock_24k_dispatch_after_load(
        requested=True, load_result=_passing_load_result(),
        invoke=invoke,
    )
    assert calls == ["collector"]
    assert result["status"] == "COLLECTOR_INVOKED"
    assert result["collector_calls"] == 1
    assert result["post_load_actions"] == {"ui": 0, "bridge": 0, "input": 0}
    assert result["observation"]["product_pass_claim"] is False


def test_g1_parent_flag_reaches_runtime_gate_and_preserves_default_limits(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runtime_env, "G2_ARTIFACT_ROOT", tmp_path)
    witness = tmp_path / "witness.json"
    witness.write_text("{}", encoding="utf-8")
    artifact = tmp_path / "run"

    def stop_at_runtime_gate(_manifest: Path) -> dict[str, Any]:
        raise runtime_env.RuntimeSafetyError("runtime-gate-sentinel")

    monkeypatch.setattr(runtime_env, "check_runtime", stop_at_runtime_gate)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="runtime-gate-sentinel"):
        runtime_env.g1_baseline(
            tmp_path / "missing-manifest.json", g4_chain_goal=runtime_env.G2_CREATION_GOAL,
            g4_candidate_exe=runtime_env.G2_CREATION_CANDIDATE, g4_sample_seconds=0,
            g2_artifact_output=artifact, g2_stock_lifecycle="load", g2_lifecycle_slot=1,
            g2_lifecycle_expected=witness, g2_stock_24k_observation=True,
        )
    with pytest.raises(runtime_env.RuntimeSafetyError, match="forbids"):
        runtime_env.g1_baseline(
            tmp_path / "missing-manifest.json", g4_chain_goal=runtime_env.G2_CREATION_GOAL,
            g4_candidate_exe=runtime_env.G2_CREATION_CANDIDATE, g4_sample_seconds=1,
            g2_artifact_output=tmp_path / "run-invalid", g2_stock_lifecycle="load",
            g2_lifecycle_slot=1, g2_lifecycle_expected=witness, g2_stock_24k_observation=True,
        )


def test_parent_file_pin_preflight_rejects_wrong_witness_before_game_calls(tmp_path: Path) -> None:
    game = tmp_path / "game"
    (game / "save").mkdir(parents=True)
    (game / "save" / "save001.dat").write_bytes(b"save")
    witness = tmp_path / "witness.json"
    witness.write_text("{}", encoding="utf-8")
    with pytest.raises(runtime_env.RuntimeSafetyError, match="pinned fresh-load witness"):
        runtime_env._g2_stock_24k_load_file_pins(game, witness)


def test_parent_dispatch_real_observer_arguments_pass_gate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    clock = _Clock()
    monkeypatch.setattr(runtime_env, "G2_ARTIFACT_ROOT", tmp_path)

    def invoke() -> dict[str, Any]:
        return runtime_env.g2_stock_24k_observe(
            tmp_path / "parent-real", enabled=True,
            goal=runtime_env.G2_CREATION_GOAL,
            candidate=runtime_env.G2_CREATION_CANDIDATE,
            bridge_sha256=runtime_env.G2_APPROVED_BRIDGE_SHA256,
            lifecycle="load", stock_stress=False,
            fresh_creation_gate={"status": "PASS", "units": 16},
            load_result=_passing_load_result(),
            post_load_effects={
                "ui_actions": 0, "input_actions": 0, "bridge_requests": 0,
                "save_actions": 0, "stress_interventions": False,
            },
            snapshot_reader=lambda _detailed: _snapshot(25000),
            light_reader=lambda: {"ps": 3, "tick": 1000},
            process_reader=lambda: {"alive": True},
            monotonic=clock.monotonic, sleep=clock.sleep,
        )

    result = runtime_env._g2_stock_24k_dispatch_after_load(
        requested=True, load_result=_passing_load_result(), invoke=invoke,
    )
    assert result["status"] == "COLLECTOR_INVOKED"
    assert result["observation"]["product_pass_claim"] is False


def test_stock_active_list_snapshot_reports_duplicate_missing_and_exact() -> None:
    existence = bytearray(2400)
    for slot in (1, 2, 3):
        existence[slot * 2:slot * 2 + 2] = (1).to_bytes(2, "little")

    def reader(address: int, size: int) -> bytes:
        values = {
            0x00975908: (3).to_bytes(2, "little"),
            0x00974FA8: b"\x01\x00\x02\x00\x02\x00",
            0x008990C8: bytes(existence),
        }
        assert len(values[address]) == size
        return values[address]

    result = runtime_env._g2_stock_active_list_snapshot(reader)
    assert result["exact_set_match"] is False
    assert result["duplicates"] == [2]
    assert result["missing"] == [3]
    assert result["unexpected"] == []


def test_stock_observer_stops_on_two_persistent_active_list_mismatches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = _Clock()
    monkeypatch.setattr(runtime_env, "G2_ARTIFACT_ROOT", tmp_path)
    result = runtime_env.g2_stock_24k_observe(
        tmp_path / "active-mismatch", enabled=True, **_gate(),
        snapshot_reader=lambda _detailed: _snapshot(1000),
        light_reader=lambda: {"ps": 3, "tick": 1000},
        process_reader=lambda: {"alive": True},
        active_list_reader=lambda: {
            "active_count": 16, "active_unique": 15, "existence_count": 16,
            "duplicates": [2], "missing": [3], "unexpected": [],
            "exact_set_match": False,
        },
        monotonic=clock.monotonic, sleep=clock.sleep,
        target_ticks=24000, sample_seconds=2,
    )
    assert result["status"] == "ACTIVE_LIST_MISMATCH_PARTIAL"
    assert result["samples"] == 2
