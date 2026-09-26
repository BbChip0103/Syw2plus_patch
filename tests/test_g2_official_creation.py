"""Focused guards for the opt-in G2 official-launch path."""

from __future__ import annotations

import inspect
import struct
from pathlib import Path

import pytest

from tools import runtime_env


def _creation_state() -> tuple[dict[str, object], dict[int, bytes]]:
    players = [
        {"owner": owner, "nation": 1, "ai": 0 if owner == 0 else 1,
         "count": 2, "used": 20, "reserved": 0, "cap": 5000}
        for owner in range(8)
    ]
    units = []
    for owner in range(8):
        units.extend([
            {"slot": owner * 2 + 1, "internal_id": owner * 2 + 1,
             "owner": owner, "type": 49, "hp": 100},
            {"slot": owner * 2 + 2, "internal_id": owner * 2 + 2,
             "owner": owner, "type": 7, "hp": 100},
        ])
    raw: dict[int, bytes] = {}
    for owner in range(8):
        self_mask = 1 << owner
        raw[0x956770 + owner * 0x3ABC] = bytes((1, owner, 0 if owner == 0 else 1,
                                                self_mask, 0xFF ^ self_mask, owner))
        raw[0xB3DE58 + owner * 0x338] = struct.pack("<i", 10 + owner * 3)
        raw[0xB3DE5C + owner * 0x338] = struct.pack("<i", 20 + owner * 3)
    raw.update({
        0x632D42: struct.pack("<H", 0), 0x632D44: struct.pack("<H", 2),
        0x632D48: struct.pack("<H", 0), 0x632D4A: struct.pack("<H", 0),
        0x632D92: struct.pack("<H", 42),
    })
    return {"ps": 3, "tick": 1, "players": players, "units": units}, raw


def test_g2_creation_gate_accepts_eight_owner_natural_boundary() -> None:
    state, raw = _creation_state()

    def read(address: int, size: int) -> bytes:
        value = raw[address]
        assert len(value) == size
        return value

    result = runtime_env._g2_initial_creation_gate(state, read)
    assert result["status"] == "PASS"
    assert result["normalization_performed"] is False
    assert len(result["records"]) == 8
    assert result["owners"]["7"]["hq49"] == 1


def test_g2_creation_gate_rejects_duplicate_or_missing_full_id() -> None:
    state, raw = _creation_state()
    state["units"][1]["internal_id"] = state["units"][0]["internal_id"]  # type: ignore[index]

    result = runtime_env._g2_initial_creation_gate(state, lambda address, size: raw[address])
    assert result["status"] == "BLOCKED"
    assert any("full IDs" in failure for failure in result["failures"])


@pytest.mark.parametrize(
    ("owner", "address", "packed"),
    [
        (0, 0xB3DE58, struct.pack("<i", 100)),
        (1, 0xB3DE5C + 0x338, struct.pack("<i", 100)),
        (2, 0xB3DE58 + 2 * 0x338, struct.pack("<I", 0x80000000)),
    ],
)
def test_g2_creation_gate_rejects_start_coordinate_bounds(
    owner: int, address: int, packed: bytes,
) -> None:
    state, raw = _creation_state()
    raw[address] = packed

    def read(address: int, size: int) -> bytes:
        value = raw[address]
        assert len(value) == size
        return value

    result = runtime_env._g2_initial_creation_gate(state, read)
    assert result["status"] == "BLOCKED"
    assert any("start point" in failure for failure in result["failures"])
    assert owner in {item["owner"] for item in result["starts"]}


def test_g2_creation_gate_rejects_duplicate_start_coordinates() -> None:
    state, raw = _creation_state()
    raw[0xB3DE58 + 1 * 0x338] = raw[0xB3DE58]
    raw[0xB3DE5C + 1 * 0x338] = raw[0xB3DE5C]

    def read(address: int, size: int) -> bytes:
        value = raw[address]
        assert len(value) == size
        return value

    result = runtime_env._g2_initial_creation_gate(state, read)
    assert result["status"] == "BLOCKED"
    assert any("not distinct" in failure for failure in result["failures"])


def test_g2_api_and_static_candidate_guards_are_present() -> None:
    signature = inspect.signature(runtime_env.g1_baseline)
    signature.bind(
        Path("/tmp/manifest.json"),
        g4_chain_goal=runtime_env.G2_CREATION_GOAL,
        g4_candidate_exe=runtime_env.G2_CREATION_CANDIDATE,
        g2_artifact_output=Path(
            "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/run"
        ),
    )
    source = Path(runtime_env.__file__).read_text(encoding="utf-8")
    assert "fixed_supply_5000.patched_bytes" in source
    assert runtime_env.G2_APPROVED_BRIDGE_SHA256 in source
    assert 'recorded_support.get("_inmm.dll") != G2_APPROVED_BRIDGE_SHA256' in source
    assert '_sha256(bridge) != G2_APPROVED_BRIDGE_SHA256' in source
    assert 'evidence["g2_eight_owner_creation"]' in source
    assert "manifest_output_preserved" in source


@pytest.mark.parametrize(
    ("goal", "candidate", "artifact", "match"),
    [
        (runtime_env.G2_CREATION_GOAL, None, Path("/tmp/g2"), "approved fixed-supply"),
        (runtime_env.G2_CREATION_GOAL, runtime_env.G2_CREATION_CANDIDATE, None, "external artifact"),
        (runtime_env.G2_CREATION_GOAL, runtime_env.G2_CREATION_CANDIDATE, Path("relative"), "absolute path"),
        ("_custom_game_chain_inject_seed42", None, Path("/tmp/g2"), "only valid"),
    ],
)
def test_g2_launch_argument_guards_run_before_manifest_access(
    tmp_path: Path, goal: str, candidate: str | None, artifact: Path | None, match: str,
) -> None:
    with pytest.raises(runtime_env.RuntimeSafetyError, match=match):
        runtime_env.g1_baseline(
            tmp_path / "missing.json", timeout=5, g4_sample_seconds=10,
            g4_chain_goal=goal, g4_candidate_exe=candidate,
            g2_artifact_output=artifact,
        )
