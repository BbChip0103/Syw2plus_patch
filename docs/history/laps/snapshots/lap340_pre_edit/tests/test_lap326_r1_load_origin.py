"""Synthetic, no-execution checks for the isolated G1-R1 observation lane."""

from __future__ import annotations

import struct
from pathlib import Path

import pytest

from tools import runtime_env


def test_r1_stage_budget_unreached_maps_to_mode_one(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )

    def never(_detailed: bool) -> dict[str, object]:
        return {"ps": 7}

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            never, lambda item: item.get("ps") == 35,
            started=0.0, timeout=10.0, message="PS=35 was not observed",
            stage="r1_ps35", stage_budget=0.2, stage_started=0.0,
        )

    assert caught.value.classification == "FAIL_NO_EFFECT"
    record = runtime_env._g1_r1_wait_failure_record(caught.value)
    assert record["status"] == "UNKNOWN"
    assert record["classification"] == "UNREACHED"
    assert record["observation"]["stage_budget"] == 0.2  # type: ignore[index]


def test_r1_synthetic_reached_unchanged_is_not_a_pass():
    record = runtime_env._g1_r1_compare_origin(
        {"x": 0, "y": 0, "tag": 0}, {"x": 0, "y": 0, "tag": 0},
    )
    assert record["status"] == "UNKNOWN"
    assert record["classification"] == "REACHED_UNCHANGED"


def test_r1_run_deadline_exhaustion_maps_to_mode_three(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )

    def never(_detailed: bool) -> dict[str, object]:
        return {"ps": 7}

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            never, lambda item: item.get("ps") == 35,
            started=0.0, timeout=0.3, message="single R1 deadline exhausted",
            stage="r1_ps35", stage_budget=20.0, stage_started=0.0,
        )

    assert caught.value.classification == "UNKNOWN_BUDGET_EXHAUSTED"
    record = runtime_env._g1_r1_wait_failure_record(caught.value)
    assert record["status"] == "UNKNOWN"
    assert record["classification"] == "TIMEOUT"
    assert record["observation"]["remaining_budget_after"] == 0.0  # type: ignore[index]


@pytest.mark.parametrize("site", ["pre", "post"])
def test_r1_origin_oserror_is_collection_error_with_read_provenance(site: str):
    calls: list[tuple[int, int]] = []

    def failing_read(address: int, size: int) -> bytes:
        calls.append((address, size))
        raise OSError(5, "read 123:1088b5c, got -1/6")

    with pytest.raises(runtime_env._G1R1CollectionError) as caught:
        runtime_env._g1_r1_read_origin_checked(failing_read, site=site)

    record = runtime_env._g1_r1_collection_failure_record(
        caught.value, evidence={"input": {"count": 1 if site == "post" else 0}},
    )
    assert calls == [(runtime_env.G1_R1_ORIGIN_ADDRESS, 6)]
    assert record["status"] == "UNKNOWN"
    assert record["classification"] == "COLLECTION_ERROR"
    collection_error = record["observation"]["collection_error"]  # type: ignore[index]
    assert collection_error["errno"] == 5  # type: ignore[index]
    assert collection_error["requested_size"] == 6  # type: ignore[index]
    assert collection_error["actual_size"] == -1  # type: ignore[index]
    assert collection_error["site"] == {  # type: ignore[index]
        "address": hex(runtime_env.G1_R1_ORIGIN_ADDRESS),
        "function": "_g1_r1_read_origin",
        "phase": site,
    }


def test_r1_read_shapes_keep_origin_contiguous_and_ps_word_signed():
    calls: list[tuple[int, int]] = []
    payloads = {
        (runtime_env.G1_R1_ORIGIN_ADDRESS, 6): struct.pack("<hhh", 240, 145, 8),
        (runtime_env.G1_R1_PROGRAM_STATE_ADDRESS, 2): struct.pack("<h", -1),
        (runtime_env.G1_R1_PROGRAM_STATE_ADDRESS, 4): struct.pack("<i", 35),
        (runtime_env.G1_R1_PENDING_STATE_ADDRESS, 2): struct.pack("<h", 140),
    }

    def read(address: int, size: int) -> bytes:
        calls.append((address, size))
        return payloads[(address, size)]

    assert runtime_env._g1_r1_read_origin(read) == {"x": 240, "y": 145, "tag": 8}
    assert runtime_env._g1_r1_read_wait_state(read) == {
        "ps": -1, "ps_word": -1, "ps_dword": 35, "pending_state": 140,
    }
    assert calls == [
        (runtime_env.G1_R1_ORIGIN_ADDRESS, 6),
        (runtime_env.G1_R1_PROGRAM_STATE_ADDRESS, 2),
        (runtime_env.G1_R1_PROGRAM_STATE_ADDRESS, 4),
        (runtime_env.G1_R1_PENDING_STATE_ADDRESS, 2),
    ]


def test_r1_cli_forwards_only_the_research_lane(monkeypatch: pytest.MonkeyPatch, tmp_path):
    captured: dict[str, object] = {}

    def fake_run(manifest, **kwargs):
        captured["manifest"] = manifest
        captured.update(kwargs)
        return {"status": "UNKNOWN", "classification": "UNREACHED"}

    monkeypatch.setattr(runtime_env, "g1_r1_load_origin", fake_run)
    result = runtime_env.runtime_main([
        "g1-r1-load-origin", "--manifest", str(tmp_path / "manifest.json"),
        "--timeout", "12",
    ])
    assert result == 0
    assert captured == {
        "manifest": tmp_path / "manifest.json",
        "screen": "1600x1200x24",
        "timeout": 12.0,
    }


def test_candidate_geometry_gate_requires_physical_2x_content():
    window = runtime_env._g1_r1_candidate_geometry_gate(
        {"id": "0x1", "x": 0, "y": 0, "width": 1600, "height": 1200},
        {"id": "0x2", "x": 10, "y": 20, "width": 1600, "height": 1200},
    )
    assert window["physical_size"] == [1600, 1200]
    assert window["logical_size"] == [800, 600]
    assert window["scale"] == [2.0, 2.0]

    with pytest.raises(runtime_env._G1R1CandidatePreconditionError) as caught:
        runtime_env._g1_r1_candidate_geometry_gate(
            {"width": 1600, "height": 1200},
            {"width": 800, "height": 600},
        )
    assert runtime_env._g1_r1_candidate_precondition_record(caught.value)["classification"] == "BLOCKED_PRECONDITION"


def test_candidate_click_is_content_plus_logical_point_without_scale():
    geometry = runtime_env._g1_r1_candidate_click_geometry((100, 200, 1600, 1200))
    assert geometry["content"] == [296, 505]
    assert geometry["x11"] == [396, 705]
    assert geometry["scale"] == [2.0, 2.0]
    assert geometry["scale_applied"] == [1.0, 1.0]


def test_candidate_module_gate_accepts_only_private_ddraw(tmp_path: Path):
    game = tmp_path / "game"
    game.mkdir()
    ddraw = game / "ddraw.dll"
    ddraw.write_bytes(b"private-ddraw")
    evidence = {
        "maps_raw": f"{ddraw}\n",
        "modules": [{"path": str(ddraw), "sha256": runtime_env._sha256(ddraw)}],
    }
    result = runtime_env._g1_r1_candidate_module_gate(
        evidence, game, {"ddraw.dll": runtime_env._sha256(ddraw)},
    )
    assert result["status"] == "PASS"
    assert result["syw2x_loaded"] is False

    with pytest.raises(runtime_env._G1R1CandidatePreconditionError):
        runtime_env._g1_r1_candidate_module_gate(
            {**evidence, "maps_raw": f"{ddraw}\nsyw2x.dll\n"},
            game, {"ddraw.dll": runtime_env._sha256(ddraw)},
        )


@pytest.mark.parametrize(
    ("classification", "expected"),
    [
        ("FAIL_NO_EFFECT", "NOT_REACHED"),
        ("UNKNOWN_BUDGET_EXHAUSTED", "TIMEOUT"),
        ("UNKNOWN_STATE_READ_FAILURE", "COLLECTION_ERROR"),
    ],
)
def test_candidate_wait_failure_modes_are_explicit(classification: str, expected: str):
    exc = runtime_env._G1WaitTimeout(
        "synthetic candidate wait", classification=classification, last=None,
        finished_elapsed=1.0, remaining_budget_after=0.0, observation={"samples": 1},
    )
    assert runtime_env._g1_r1_candidate_wait_failure_record(exc)["classification"] == expected


def test_candidate_no_change_and_cleanup_failure_are_not_passes():
    result = runtime_env._g1_r1_candidate_compare_origin(
        {"x": 0, "y": 0, "tag": 0}, {"x": 0, "y": 0, "tag": 0},
    )
    assert result["status"] == "UNKNOWN"
    assert result["classification"] == "NO_CHANGE"
    cleanup = runtime_env._g1_r1_candidate_cleanup_record(
        owned_launchers_stopped=True, xvfb_stopped=True, prefix_target=Path("/private"),
        prefix_processes_after=[], cleanup_error=None,
        dxwrapper_config_restored=False, dxwrapper_config_error="restore failed",
    )
    assert cleanup["ok"] is False
    assert cleanup["dxwrapper_config_restored"] is False


def test_candidate_cli_forwards_separate_artifact_lane(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    captured: dict[str, object] = {}

    def fake_run(manifest, **kwargs):
        captured["manifest"] = manifest
        captured.update(kwargs)
        return {"status": "UNKNOWN", "classification": "BLOCKED_PRECONDITION"}

    monkeypatch.setattr(runtime_env, "g1_r1_candidate_load_origin", fake_run)
    result = runtime_env.runtime_main([
        "g1-r1-candidate-load-origin", "--manifest", str(tmp_path / "manifest.json"),
        "--timeout", "12",
    ])
    assert result == 0
    assert captured == {
        "manifest": tmp_path / "manifest.json",
        "screen": "1600x1200x24",
        "timeout": 12.0,
    }
