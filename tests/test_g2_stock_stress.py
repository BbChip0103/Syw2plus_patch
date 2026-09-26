"""Regression guards for the explicit native G2 stock stress phase."""

import json
from pathlib import Path
import struct
from typing import Any

import pytest

from tools import runtime_env


SOURCE = Path(runtime_env.__file__).read_text(encoding="utf-8")


def test_stress_is_opt_in_and_supply_probe_environment_is_explicit() -> None:
    assert "g2_stock_stress: bool = False" in SOURCE
    assert 'if g2_stock_stress or g2_stock_lifecycle is not None:\n        env["SYW2_SUPPLY_PROBE"] = "1"' in SOURCE
    assert '"op4_used": False' in SOURCE
    assert "request(4" not in SOURCE


def test_stress_is_exact_g2_only_and_uses_fail_stop_native_ops() -> None:
    assert "G2 stock stress requires the exact G2 creation goal" in SOURCE
    assert "G2 stock stress cannot be mixed with G4 interventions" in SOURCE
    assert "request(5, owner" in SOURCE
    assert "request(1, owner" in SOURCE
    assert SOURCE.index("request(1, owner") < SOURCE.index("request(5, owner")
    assert '"operations": "native_op1_then_op5_per_owner"' in SOURCE
    assert "atomic same-HQ witness" in SOURCE
    assert 'current_hq.get("command") == 15' in SOURCE
    assert 'producer.get("type") != 49' in SOURCE
    assert 'producer.get("production_type")' in SOURCE
    assert 'result.get("ps") != 3' in SOURCE
    assert '0x00B3DE58 + owner * 0x338' in SOURCE
    assert "no retry" in SOURCE
    assert "deadline = phase_started + min(300.0, max_seconds)" in SOURCE
    assert '"retries": 0' in SOURCE


def test_stress_enforces_original_pool_owner_cap_and_native_costs() -> None:
    assert "remaining_seeds = 8 - owner" in SOURCE
    assert "len(before_units) + pending_slots + 142 * remaining_seeds + 8 > 1199" in SOURCE
    assert "seed_count + 142 + 1 > 242" in SOURCE
    assert 'item.get("cap") != 5000' in SOURCE
    assert "0x9B5228 + unit_type * 0x394 + 0x10" in SOURCE
    assert "costs.get(5) != 35" in SOURCE
    assert '"ASSISTED_LOCAL_HIGH_COST_ONLY"' in SOURCE
    assert '"g2_stock_stress.json"' in SOURCE


def test_default_call_does_not_enable_stress(tmp_path: Path) -> None:
    with pytest.raises(runtime_env.RuntimeSafetyError, match="requires the exact G2"):
        runtime_env.g1_baseline(
            tmp_path / "missing.json", timeout=5, g2_stock_stress=True,
        )


def _initial_snapshot(_detailed: bool = True) -> dict[str, Any]:
    players = [
        {"owner": owner, "cap": 5000, "used": 20, "reserved": 0, "count": 2}
        for owner in range(8)
    ]
    units = []
    for owner in range(8):
        units.extend([
            {"internal_id": owner * 2 + 1, "slot": owner * 2 + 1,
             "owner": owner, "type": 49, "hp": 100},
            {"internal_id": owner * 2 + 2, "slot": owner * 2 + 2,
             "owner": owner, "type": 7, "hp": 100},
        ])
    return {"players": players, "units": units}


def test_return_one_without_atomic_admission_is_partial_and_not_retried(tmp_path: Path) -> None:
    """The native call's unconditional return value cannot prove admission."""
    prefix = tmp_path / "prefix"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    output = tmp_path / "out"
    # Pre-seed the mocked bridge response for request id 1.  It deliberately
    # models 4AF5E0's return-one/no-action case without its atomic evidence.
    (drive_c / "supply_probe_result.json").write_text(
        json.dumps({"id": 1, "ok": True, "raw_return": 1}), encoding="utf-8"
    )

    def read_memory(address: int, size: int) -> bytes:
        if size == 4 and 0x00B3DE58 <= address < 0x00B3DE58 + 8 * 0x338:
            owner = (address - 0x00B3DE58) // 0x338
            offset = (address - 0x00B3DE58) % 0x338
            return struct.pack("<i", owner * 10 + (0 if offset == 0 else 1))
        assert size == 2
        unit_type = (address - 0x9B5228 - 0x10) // 0x394
        return struct.pack("<h", 35 if unit_type == 5 else 10 if unit_type in (7, 49) else 1)

    evidence = runtime_env._g2_stock_stress_phase(
        prefix, output, _initial_snapshot, read_memory, max_seconds=2.0,
    )

    assert evidence["pass"] is False
    assert evidence["status"] == "PARTIAL_UNKNOWN"
    assert "atomic same-HQ witness" in evidence["stop_reason"]
    assert len(evidence["requests"]) == 1
    request = (drive_c / "supply_probe_request.txt").read_text(encoding="ascii")
    assert request.split()[1] == "1"
    assert "request(5" not in request
    assert evidence["retries"] == 0


def test_deadline_expires_before_native_cost_read_or_snapshot(tmp_path: Path) -> None:
    calls: list[tuple[int, int]] = []

    def read_memory(address: int, size: int) -> bytes:
        calls.append((address, size))
        return struct.pack("<h", 1)

    evidence = runtime_env._g2_stock_stress_phase(
        tmp_path / "prefix", tmp_path / "out", _initial_snapshot,
        read_memory, max_seconds=0.0,
    )

    assert evidence["status"] == "PARTIAL_UNKNOWN"
    assert "deadline expired during cost read" in evidence["stop_reason"]
    assert calls == []


def _mock_read_memory(address: int, size: int) -> bytes:
    if size == 4 and 0x00B3DE58 <= address < 0x00B3DE58 + 8 * 0x338:
        owner = (address - 0x00B3DE58) // 0x338
        offset = (address - 0x00B3DE58) % 0x338
        return struct.pack("<i", owner * 10 + (0 if offset == 0 else 1))
    assert size == 2
    unit_type = (address - 0x9B5228 - 0x10) // 0x394
    return struct.pack("<h", 35 if unit_type == 5 else 10 if unit_type in (7, 49) else 1)


def test_async_hq49_admission_is_observed_before_op5(tmp_path: Path) -> None:
    prefix = tmp_path / "prefix"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    output = tmp_path / "out"
    (drive_c / "supply_probe_result.json").write_text(json.dumps({
        "id": 1, "op": 1, "owner": 0, "ps": 3, "ok": True, "raw_return": 1,
        "before": {"used": 20, "reserved": 0, "cap": 5000, "count": 2},
        "after": {"used": 20, "reserved": 0, "cap": 5000, "count": 2},
        "producer": {"id": 1, "slot": 1, "type": 49, "owner": 0,
                      "command": 1, "progress": 0, "production_type": 0},
    }), encoding="utf-8")
    pending = _initial_snapshot()
    pending_players = [dict(item) for item in pending["players"]]
    pending_players[0]["reserved"] = 10
    pending["players"] = pending_players
    pending_units = [dict(item) for item in pending["units"]]
    pending_units[0].update({"command": 15, "production_type": 7, "progress": 0})
    pending["units"] = pending_units
    calls = 0

    def state(_detailed: bool = True) -> dict[str, Any]:
        nonlocal calls
        calls += 1
        return pending if calls >= 2 else _initial_snapshot()

    evidence = runtime_env._g2_stock_stress_phase(
        prefix, output, state, _mock_read_memory, max_seconds=0.35,
    )

    assert evidence["pass"] is False
    assert evidence["owners"]["0"]["op1"]["admission_mode"] == "pending_same_hq"
    assert len(evidence["requests"]) == 1
    assert evidence["requests"][0]["producer"]["type"] == 49
    assert evidence["retries"] == 0


def test_return_one_no_action_times_out_without_false_admission(tmp_path: Path) -> None:
    prefix = tmp_path / "prefix"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    output = tmp_path / "out"
    (drive_c / "supply_probe_result.json").write_text(json.dumps({
        "id": 1, "op": 1, "owner": 0, "ps": 3, "ok": True, "raw_return": 1,
        "before": {"used": 20, "reserved": 0, "cap": 5000, "count": 2},
        "after": {"used": 20, "reserved": 0, "cap": 5000, "count": 2},
        "producer": {"id": 1, "slot": 1, "type": 49, "owner": 0,
                      "command": 1, "progress": 0, "production_type": 0},
    }), encoding="utf-8")
    evidence = runtime_env._g2_stock_stress_phase(
        prefix, output, _initial_snapshot, _mock_read_memory, max_seconds=0.15,
    )
    assert evidence["pass"] is False
    assert "admission was not observed" in evidence["stop_reason"]
    assert len(evidence["requests"]) == 1
    assert evidence["retries"] == 0


def test_wrong_hq_type_cannot_supply_worker_admission(tmp_path: Path) -> None:
    prefix = tmp_path / "prefix"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    output = tmp_path / "out"
    (drive_c / "supply_probe_result.json").write_text(json.dumps({
        "id": 1, "op": 1, "owner": 0, "ps": 3, "ok": True, "raw_return": 1,
        "before": {"used": 20, "reserved": 0, "cap": 5000, "count": 2},
        "after": {"used": 20, "reserved": 10, "cap": 5000, "count": 2},
        "producer": {"id": 1, "slot": 1, "type": 7, "owner": 0,
                      "command": 15, "progress": 0, "production_type": 7},
    }), encoding="utf-8")
    evidence = runtime_env._g2_stock_stress_phase(
        prefix, output, _initial_snapshot, _mock_read_memory, max_seconds=1.0,
    )
    assert evidence["pass"] is False
    assert "atomic same-HQ witness" in evidence["stop_reason"]
    assert len(evidence["requests"]) == 1
