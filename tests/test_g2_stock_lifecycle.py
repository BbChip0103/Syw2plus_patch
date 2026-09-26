"""Offline lifecycle guards for the narrow G2 stock save/load boundary."""

import hashlib
import json
from pathlib import Path
import struct
from typing import Any

import pytest

from tools import runtime_env


def _cost_read(address: int, size: int) -> bytes:
    assert size == 2
    unit_type = (address - 0x9B5228 - 0x10) // 0x394
    return struct.pack("<h", 35 if unit_type == 5 else 10 if unit_type in (7, 49) else 1)


def _stock() -> dict[str, Any]:
    players = []
    units: list[dict[str, Any]] = []
    next_id = 1
    for owner in range(8):
        players.append({"owner": owner, "cap": 5000, "used": 5000,
                        "reserved": 10 if owner == 4 else 0, "count": 145})
        units.append({"internal_id": next_id, "slot": next_id, "owner": owner,
                      "type": 49, "hp": 100, "command": 15 if owner == 4 else 1,
                      "production_type": 7 if owner == 4 else 0,
                      "progress": 100 if owner == 4 else 0})
        next_id += 1
        units.extend({"internal_id": next_id + index, "slot": next_id + index,
                      "owner": owner, "type": 7, "hp": 100}
                     for index in range(2))
        next_id += 2
        units.extend({"internal_id": next_id + index, "slot": next_id + index,
                      "owner": owner, "type": 5, "hp": 100}
                     for index in range(142))
        next_id += 142
    return {"players": players, "units": units}


def _fresh() -> dict[str, Any]:
    stock = _stock()
    units = [unit for unit in stock["units"] if unit["type"] in (49, 7)]
    # Keep only the natural HQ + one worker for each owner.
    selected: list[dict[str, Any]] = []
    for owner in range(8):
        selected.extend(unit for unit in units if unit["owner"] == owner and len(
            [item for item in selected if item["owner"] == owner]
        ) < 2)
    players = [{"owner": owner, "cap": 5000, "used": 20,
                "reserved": 0, "count": 2} for owner in range(8)]
    return {"ps": 3, "players": players, "units": selected}


def _pending() -> dict[str, Any]:
    return {"owner": 4, "internal_id": 4 * 145 + 1, "slot": 4 * 145 + 1,
            "type": 49, "command": 15, "production_type": 7,
            "progress": 100, "reserved": 10, "stable_tick": True,
            "tick_before": 1000, "tick_after": 1000}


def _native(op: int) -> dict[str, Any]:
    return {"op": op, "owner": 0, "ps": 3, "ok": True, "raw_return": 1,
            "thread": 42, "tick_before": 1000, "tick_after": 1000,
            "provenance": {"bridge_sha256": runtime_env.G2_APPROVED_BRIDGE_SHA256,
                            "caller": "0x42334C",
                            "thread_check": "window_thread_equals_current_thread"}}


def _save_file(tmp_path: Path) -> tuple[Path, str]:
    path = tmp_path / "save" / "save001.dat"
    path.parent.mkdir()
    path.write_bytes(b"private-native-save-v1")
    return path, hashlib.sha256(path.read_bytes()).hexdigest()


def test_save_boundary_accepts_exact_roster_and_native_op2(tmp_path: Path) -> None:
    save_path, digest = _save_file(tmp_path)
    result = runtime_env.g2_stock_lifecycle(
        "save", stock_snapshot=_stock(), read_memory=_cost_read,
        native_result=_native(2), save_path=save_path, save_slot=1,
        save_previously_absent=True,
        expected_save_sha256=digest, pending_witness=_pending(),
    )
    assert result["status"] == "PASS"
    assert result["classification"] == "G2_STOCK_SAVE_BOUNDARY_PASS"
    assert result["product_pass_claim"] is False


def test_load_boundary_requires_byte_identical_fresh_private_copy(tmp_path: Path) -> None:
    save_path, digest = _save_file(tmp_path)
    loaded = tmp_path / "fresh" / "save" / "save001.dat"
    loaded.parent.mkdir(parents=True)
    loaded.write_bytes(save_path.read_bytes())
    result = runtime_env.g2_stock_lifecycle(
        "load", stock_snapshot=_stock(), fresh_snapshot=_fresh(),
        loaded_snapshot=_stock(), read_memory=_cost_read, native_result=_native(3),
        save_path=save_path, loaded_save_path=loaded, save_slot=1,
        save_previously_absent=True,
        expected_save_sha256=digest, pending_witness=_pending(),
    )
    assert result["status"] == "PASS"
    assert result["classification"] == "G2_STOCK_FRESH_LOAD_BOUNDARY_PASS"


def test_save_expected_witness_round_trips_into_fresh_load(tmp_path: Path) -> None:
    save_path, digest = _save_file(tmp_path)
    saved = runtime_env.g2_stock_lifecycle(
        "save", stock_snapshot=_stock(), read_memory=_cost_read,
        native_result=_native(2), save_path=save_path, save_slot=1,
        save_previously_absent=True, expected_save_sha256=digest,
        pending_witness=_pending(),
    )
    assert saved["status"] == "PASS"
    expected = {
        "stock_snapshot": saved["stock_snapshot"],
        "pending_witness": saved["pending_witness"],
        "save_sha256": saved["save_sha256"],
    }
    expected_path = tmp_path / "expected.json"
    expected_path.write_text(json.dumps(expected), encoding="utf-8")
    loaded = runtime_env.g2_stock_lifecycle(
        "load", stock_snapshot=expected["stock_snapshot"], fresh_snapshot=_fresh(),
        loaded_snapshot=_stock(), read_memory=_cost_read, native_result=_native(3),
        save_path=save_path, loaded_save_path=save_path, save_slot=1,
        save_previously_absent=True, expected_save_sha256=expected["save_sha256"],
        pending_witness=expected["pending_witness"],
    )
    assert loaded["status"] == "PASS"
    assert expected_path.read_text(encoding="utf-8").startswith("{")


def test_lifecycle_rejects_hash_and_identity_mismatches(tmp_path: Path) -> None:
    save_path, digest = _save_file(tmp_path)
    bad = dict(_pending(), internal_id=99999)
    result = runtime_env.g2_stock_lifecycle(
        "save", stock_snapshot=_stock(), read_memory=_cost_read,
        native_result=_native(2), save_path=save_path, save_slot=1,
        save_previously_absent=True,
        expected_save_sha256=digest, pending_witness=bad,
    )
    assert result["status"] == "BLOCKED"
    assert "pending HQ identity" in result["reason"] or "witness" in result["reason"]
    bad_hash = runtime_env.g2_stock_lifecycle(
        "save", stock_snapshot=_stock(), read_memory=_cost_read,
        native_result=_native(2), save_path=save_path, save_slot=1,
        save_previously_absent=True,
        expected_save_sha256="0" * 64, pending_witness=_pending(),
    )
    assert bad_hash["status"] == "BLOCKED"
    assert "hash mismatch" in bad_hash["reason"]


@pytest.mark.parametrize("op", [2, 3])
def test_existing_bridge_native_op_helper_issues_one_exact_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, op: int,
) -> None:
    prefix = tmp_path / f"prefix{op}"
    drive_c = prefix / "drive_c"
    drive_c.mkdir(parents=True)
    request_id = 223456
    (drive_c / "supply_probe_result.json").write_text(
        json.dumps({"id": request_id, "op": op, "owner": 0, "ps": 3,
                    "ok": True, "raw_return": 1, "thread": 42,
                    "reason": "executed"}), encoding="utf-8"
    )
    monkeypatch.setattr(runtime_env.time, "monotonic_ns", lambda: 123456)
    result = runtime_env._g2_lifecycle_native_op(
        prefix, op=op, owner=0, slot=1, timeout=1.0,
    )
    assert result["op"] == op
    assert result["ps"] == 3
    assert (drive_c / "supply_probe_request.txt").read_text(encoding="ascii").split() == [
        str(request_id), str(op), "0", "1", "0", "0", "0", "0",
    ]


def test_g1_lifecycle_modes_are_exact_g2_and_exclusive(tmp_path: Path) -> None:
    with pytest.raises(runtime_env.RuntimeSafetyError, match="exact G2"):
        runtime_env.g1_baseline(tmp_path / "missing.json", timeout=5,
                                g2_stock_lifecycle="save")
    with pytest.raises(runtime_env.RuntimeSafetyError, match="requires stock stress"):
        runtime_env.g1_baseline(tmp_path / "missing.json", timeout=5,
                                g4_chain_goal=runtime_env.G2_CREATION_GOAL,
                                g4_candidate_exe=runtime_env.G2_CREATION_CANDIDATE,
                                g2_artifact_output=tmp_path / "out",
                                g2_stock_lifecycle="save")
    with pytest.raises(runtime_env.RuntimeSafetyError, match="stock stress disabled"):
        runtime_env.g1_baseline(tmp_path / "missing.json", timeout=5,
                                g4_chain_goal=runtime_env.G2_CREATION_GOAL,
                                g4_candidate_exe=runtime_env.G2_CREATION_CANDIDATE,
                                g2_artifact_output=tmp_path / "out",
                                g2_stock_stress=True, g2_stock_lifecycle="load")
