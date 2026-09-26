"""Isolated runtime setup boundaries; no Wine/X11 process is started here."""

from __future__ import annotations

import ast
import hashlib
import inspect
import json
from pathlib import Path
import subprocess
import struct
import textwrap
import time

import pytest

from tools import runtime_env


def test_generated_screenshots_are_outside_patch_repo():
    assert runtime_env.SCREENSHOT_ROOT == Path(
        "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures"
    )
    assert not runtime_env.SCREENSHOT_ROOT.is_relative_to(runtime_env.REPO_ROOT)


def test_unit_record_offsets_are_shared_with_runtime_driver():
    from patches.population import runtime_driver

    expected = {
        "G1_UNIT_INTERNAL_ID_OFFSET": 0x29C,
        "G1_UNIT_X_OFFSET": 0x2A2,
        "G1_UNIT_Y_OFFSET": 0x2A4,
    }
    for name, offset in expected.items():
        assert getattr(runtime_env, name) == offset
        assert getattr(runtime_driver, name) == offset
    assert runtime_driver.G4_CONTROLLER_OPCODE_OFFSET == 0x0D32
    assert runtime_driver.G4_CONTROLLER_ARGUMENT_OFFSET == 0x0D34


def test_runtime_driver_control_goal_uses_protocol_string_request_id():
    from patches.population import runtime_driver

    assert runtime_driver.control_goal_payload(2, "goal", 90_000) == {
        "version": "1",
        "request_id": "2",
        "goal": "goal",
        "timeout_ms": 90_000,
    }


def test_runtime_driver_decodes_bounded_original_ai_group_targets():
    from patches.population import runtime_driver

    data = bytearray(runtime_driver.PLAYER_STRUCT_SIZE)
    struct.pack_into("<h", data, runtime_driver.G4_GROUP_COUNT_OFFSET, 1)
    base = runtime_driver.G4_GROUP_BASE_OFFSET
    struct.pack_into("<4h", data, base, 31, 47, 3, 2)
    struct.pack_into("<h", data, runtime_driver.G4_ROUTE_MEMBER_COUNT_OFFSET + 3 * 2, 7)
    ids_offset = runtime_driver.G4_ROUTE_MEMBER_IDS_OFFSET + 3 * 20 * 4
    struct.pack_into("<7I", data, ids_offset, 101, 102, 103, 104, 105, 106, 107)
    struct.pack_into("<2hi", data, base + 0x2D8, 4, 1, 1234)

    decoded = runtime_driver.decode_g4_groups(bytes(data))

    assert decoded == {
        "status": "OK",
        "count": 1,
        "groups": [{
            "index": 0, "target_x": 31, "target_y": 47, "route_id": 3,
            "state": 2, "member_count": 7, "member_ids": [101, 102, 103, 104, 105, 106, 107], "waypoint_count": 4,
            "waypoint_index": 1, "last_update_tick": 1234,
        }],
    }


def test_runtime_driver_rejects_unbounded_ai_group_count():
    from patches.population import runtime_driver

    data = bytearray(runtime_driver.PLAYER_STRUCT_SIZE)
    struct.pack_into("<h", data, runtime_driver.G4_GROUP_COUNT_OFFSET, 3)
    assert runtime_driver.decode_g4_groups(bytes(data)) == {
        "status": "UNSUPPORTED_COUNT", "count": 3, "groups": [],
    }


def test_runtime_driver_does_not_decode_negative_ai_route_as_member_table():
    from patches.population import runtime_driver

    data = bytearray(runtime_driver.PLAYER_STRUCT_SIZE)
    struct.pack_into("<h", data, runtime_driver.G4_GROUP_COUNT_OFFSET, 1)
    struct.pack_into("<h", data, runtime_driver.G4_GROUP_BASE_OFFSET + 4, -1)
    decoded = runtime_driver.decode_g4_groups(bytes(data))
    group = decoded["groups"][0]
    assert group["member_count"] is None
    assert group["member_ids"] == []


def test_g4_ai_metric_summary_tracks_stable_slot_damage_and_gap():
    samples = [
        {
            "tick": 10,
            "units": [
                {"slot": 1, "internal_id": 11, "type": 7, "owner": 0, "hp": 100, "x": 10, "y": 10},
                {"slot": 2, "internal_id": 22, "type": 7, "owner": 1, "hp": 100, "x": 20, "y": 18},
            ],
            "players": [{"owner": 1, "controller_opcode": 18, "controller_argument": 101}],
        },
        {
            "tick": 20,
            "units": [
                {"slot": 1, "internal_id": 11, "type": 7, "owner": 0, "hp": 80, "x": 12, "y": 10},
                {"slot": 3, "internal_id": 33, "type": 7, "owner": 1, "hp": 100, "x": 18, "y": 15},
            ],
            "players": [{"owner": 1, "controller_opcode": 0, "controller_argument": 0}],
        },
    ]
    assert runtime_env._g4_ai_metric_summary(samples) == {
        "sample_count": 2,
        "first_tick": 10,
        "last_tick": 20,
        "first_unit_count": 2,
        "last_unit_count": 2,
        "slot_disappearances": 1,
        "hp_decrease_same_unit": 1,
        "min_faction_gap": 6,
        "controller_nonzero_samples": 1,
        "controller_transition_count": 1,
        "controller_opcodes_observed": [18],
    }


def _fake_tree(tmp_path: Path) -> tuple[Path, Path, str]:
    source = tmp_path / "source"
    source.mkdir()
    exe = source / runtime_env.ORIGINAL_EXE
    exe.write_bytes(b"verified test original")
    digest = hashlib.sha256(exe.read_bytes()).hexdigest()
    (source / "data.dat").write_bytes(b"asset")
    return source, exe, digest


def test_validate_rejects_wrong_hash_and_links(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source, exe, _ = _fake_tree(tmp_path)
    monkeypatch.setattr(runtime_env, "ORIGINAL_SHA256", "0" * 64)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="SHA-256"):
        runtime_env.validate_original_source(source)
    exe.unlink()
    exe.symlink_to(source / "data.dat")
    with pytest.raises(runtime_env.RuntimeSafetyError, match="linked"):
        runtime_env.validate_original_source(source)


def test_g4_shadow_provenance_records_private_artifact_and_rows(tmp_path: Path):
    prefix = tmp_path / "prefix"
    shadow = prefix / runtime_env.G4_AI_SHADOW_RELATIVE_PATH
    shadow.parent.mkdir(parents=True)
    shadow.write_text('{"tick": 1}\n{"tick": 2}\n', encoding="utf-8")

    provenance = runtime_env._g4_shadow_provenance(
        prefix, {runtime_env.G4_AI_SHADOW_ENV: "1"}
    )

    assert provenance["enabled"] is True
    assert provenance["environment_value"] == "1"
    assert provenance["relative_path"] == "drive_c/inmm_ai_shadow.jsonl"
    assert provenance["path"] == str(shadow.resolve())
    assert provenance["private_prefix"] is True
    assert provenance["exists"] is True
    assert provenance["sha256"] == hashlib.sha256(shadow.read_bytes()).hexdigest()
    assert provenance["row_count"] == 2
    assert provenance["status"] == "PASS"
    assert provenance["pass"] is True
    assert provenance["error"] is None


@pytest.mark.parametrize(
    ("env_value", "artifact", "expected_error"),
    [
        ("0", '{"tick": 1}\n', None),
        ("1", None, "missing or linked"),
        ("1", "", "empty"),
    ],
)
def test_g4_shadow_provenance_never_promotes_invalid_or_disabled_artifact(
    tmp_path: Path, env_value: str, artifact: str | None, expected_error: str | None,
):
    prefix = tmp_path / "prefix"
    shadow = prefix / runtime_env.G4_AI_SHADOW_RELATIVE_PATH
    shadow.parent.mkdir(parents=True)
    if artifact is not None:
        shadow.write_text(artifact, encoding="utf-8")

    provenance = runtime_env._g4_shadow_provenance(
        prefix, {runtime_env.G4_AI_SHADOW_ENV: env_value}
    )

    assert provenance["pass"] is False
    if env_value == "0":
        assert provenance["status"] == "DISABLED"
        assert provenance["environment_value"] is None
        assert provenance["sha256"] is None
        assert provenance["row_count"] is None
    else:
        assert provenance["status"] == "FAIL"
        assert expected_error in provenance["error"]


def test_g4_shadow_provenance_rejects_external_symlink(tmp_path: Path):
    prefix = tmp_path / "prefix"
    shadow = prefix / runtime_env.G4_AI_SHADOW_RELATIVE_PATH
    shadow.parent.mkdir(parents=True)
    external = tmp_path / "outside.jsonl"
    external.write_text('{"tick": 1}\n', encoding="utf-8")
    shadow.symlink_to(external)

    provenance = runtime_env._g4_shadow_provenance(
        prefix, {runtime_env.G4_AI_SHADOW_ENV: "1"}
    )

    assert provenance["status"] == "FAIL"
    assert provenance["pass"] is False
    assert "symlink" in provenance["error"]


def test_g4_exact_postload_provenance_requires_marker_adjacent_bounded_edges(tmp_path: Path):
    prefix = tmp_path / "prefix"
    shadow = prefix / runtime_env.G4_AI_SHADOW_RELATIVE_PATH
    shadow.parent.mkdir(parents=True)
    source = {"full_id": 101, "slot": 1, "owner": 3, "command": 1,
              "pending": 1, "pending_xy": 0}
    events: list[dict[str, object]] = [{
        "schema_version": 2, "event": "load_complete", "run_id": "run-1",
        "pid": 7, "tid": 8, "seq": 1, "slot": 1, "result": 1,
        "tpre": 8, "tload": 10, "next_owner": 3, "source": source,
        "candidate_present": False, "candidate_issue_count": 0,
    }]
    for index in range(17):
        events.append({
            "schema_version": 2, "event": "ai_shadow", "run_id": "run-1",
            "pid": 7, "tid": 8, "seq": index + 2, "load_marker_seq": 1,
            "tick": index + 11, "owner": (index + 11) & 7,
            "entry_ecx": 0x956770 + ((index + 11) & 7) * 0x3ABC,
            "raw_mode": {"program_state": 3, "committed_local": 1,
                         "scenario_selector": 0, "network_mode": 0,
                         "network_modal": 0, "gate_a": 0, "gate_b": 0},
            "source": source, "tick_rewind": False,
            "same_tick_reentry": False, "original_call": "forwarded_once",
            "candidate_present": False, "candidate_issue_count": 0,
        })
    shadow.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")

    provenance = runtime_env._g4_shadow_provenance(
        prefix, {runtime_env.G4_AI_SHADOW_ENV: "1"},
        require_postload=True, expected_run_id="run-1",
    )

    assert provenance["pass"] is True
    assert provenance["marker_count"] == 1
    assert provenance["postload"]["pass"] is True


def test_g4_exact_postload_provenance_rejects_missing_marker_or_short_window(tmp_path: Path):
    prefix = tmp_path / "prefix"
    shadow = prefix / runtime_env.G4_AI_SHADOW_RELATIVE_PATH
    shadow.parent.mkdir(parents=True)
    shadow.write_text(json.dumps({"event": "ai_shadow", "run_id": "run-1", "seq": 1}) + "\n", encoding="utf-8")

    provenance = runtime_env._g4_shadow_provenance(
        prefix, {runtime_env.G4_AI_SHADOW_ENV: "1"},
        require_postload=True, expected_run_id="run-1",
    )

    assert provenance["pass"] is False
    assert provenance["status"] == "FAIL"
    assert "requires one marker" in provenance["error"]


def test_prepare_uses_private_copy_and_owned_prefix(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source, _, digest = _fake_tree(tmp_path)
    repo = tmp_path / "repo"
    runtime_root = repo / "local" / "runtime"
    monkeypatch.setattr(runtime_env, "REPO_ROOT", repo)
    monkeypatch.setattr(runtime_env, "ORIGINAL_SHA256", digest)
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return None

    monkeypatch.setattr(runtime_env, "_run", fake_run)
    class FakeXvfb:
        def poll(self):
            return None
        def terminate(self):
            return None
        def wait(self, timeout=None):
            return 0
        def kill(self):
            return None
    monkeypatch.setattr(runtime_env, "_xvfb", lambda log: (FakeXvfb(), ":199"))
    manifest = runtime_env.prepare(source, runtime_root=runtime_root)
    game = Path(manifest["game"]["root"])
    prefix = Path(manifest["wine"]["prefix"])
    assert game != source
    assert (game / runtime_env.ORIGINAL_EXE).stat().st_ino != (source / runtime_env.ORIGINAL_EXE).stat().st_ino
    assert json.loads((prefix / ".syw2plus-runtime-owner.json").read_text())["prefix"] == str(prefix)
    assert calls == [["wineboot", "-u"], ["wineserver", "-k"], ["wineserver", "-w"]]
    assert runtime_env.check_runtime(Path(manifest["output"]["run_dir"]) / "manifest.json")["ok"] is True


def test_prepare_rejects_foreign_runtime_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source, _, digest = _fake_tree(tmp_path)
    monkeypatch.setattr(runtime_env, "ORIGINAL_SHA256", digest)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="local/runtime"):
        runtime_env.prepare(source, runtime_root=tmp_path / "not-private")


def test_prepare_rejects_source_output_containment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    source, _, digest = _fake_tree(tmp_path)
    repo = tmp_path / "repo"
    monkeypatch.setattr(runtime_env, "REPO_ROOT", repo)
    monkeypatch.setattr(runtime_env, "ORIGINAL_SHA256", digest)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="must not contain"):
        runtime_env.prepare(source, runtime_root=source / "runtime")


def test_smoke_timeout_is_fail_closed(tmp_path: Path):
    with pytest.raises(runtime_env.RuntimeSafetyError, match="between 1 and 90"):
        runtime_env.smoke(tmp_path / "missing.json", timeout=91)


def test_g1_baseline_has_fixed_screen_and_timeout(tmp_path: Path):
    with pytest.raises(runtime_env.RuntimeSafetyError, match="fixed 1600x1200x24"):
        runtime_env.g1_baseline(tmp_path / "missing.json", screen="1024x768x24")
    with pytest.raises(runtime_env.RuntimeSafetyError, match="between 1 and 90"):
        runtime_env.g1_baseline(tmp_path / "missing.json", timeout=91)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="between 0 and 300"):
        runtime_env.g1_baseline(tmp_path / "missing.json", g4_sample_seconds=301)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="between 0.05 and 2"):
        runtime_env.g1_baseline(tmp_path / "missing.json", g4_sample_period=0.01)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="approved fixed-seed"):
        runtime_env.g1_baseline(
            tmp_path / "missing.json", g4_sample_seconds=1, g4_chain_goal="unsafe"
        )
    with pytest.raises(runtime_env.RuntimeSafetyError, match="requires G4 sampling"):
        runtime_env.g1_baseline(
            tmp_path / "missing.json", g4_chain_goal="_custom_game_chain_inject_seed42"
        )
    with pytest.raises(runtime_env.RuntimeSafetyError, match="not approved"):
        runtime_env.g1_baseline(
            tmp_path / "missing.json", g4_sample_seconds=1,
            g4_chain_goal="_custom_game_chain_inject_seed42", g4_candidate_exe="unknown.exe",
        )
    with pytest.raises(runtime_env.RuntimeSafetyError, match="fixed-seed sampling"):
        runtime_env.g1_baseline(
            tmp_path / "missing.json", g4_candidate_exe="g4_controller_cadence_50.exe"
        )
    with pytest.raises(runtime_env.RuntimeSafetyError, match="not approved"):
        runtime_env.g1_baseline(
            tmp_path / "missing.json", g4_sample_seconds=10,
            g4_chain_goal="_custom_game_chain_inject_seed1",
            g4_intervention_goal="unsafe",
        )
    with pytest.raises(runtime_env.RuntimeSafetyError, match="inside the sample window"):
        runtime_env.g1_baseline(
            tmp_path / "missing.json", g4_sample_seconds=10,
            g4_chain_goal="_custom_game_chain_inject_seed1",
            g4_intervention_goal="_g4_issue_idle_attack_probe",
            g4_intervention_delay=10,
        )


def test_g1_baseline_preserves_partial_g4_samples_when_intervention_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    """A failed intervention must not discard the prior observation window."""

    manifest = tmp_path / "run" / "manifest.json"
    manifest.parent.mkdir()
    manifest.write_text("{}")
    game = tmp_path / "run" / "game"
    game.mkdir()
    (game / runtime_env.ORIGINAL_EXE).write_bytes(b"fake executable")
    prefix = tmp_path / "run" / "prefix"
    prefix.mkdir()
    output = tmp_path / "run" / "output"
    output.mkdir()
    checked = {"ok": True}
    data = {"wine": {"created_new": True}}
    monkeypatch.setattr(runtime_env, "check_runtime", lambda _path: checked)
    monkeypatch.setattr(runtime_env, "_manifest", lambda _path: (data, game, prefix, output))
    monkeypatch.setattr(runtime_env, "_prefix_pids", lambda _prefix: [])
    monkeypatch.setattr(runtime_env, "_existing_state", lambda _prefix: False)
    monkeypatch.setattr(runtime_env, "_run", lambda *args, **kwargs: None)

    class FakeProcess:
        _alive = True
        pid = 4242

        def poll(self):
            return None if self._alive else 0

        def terminate(self):
            self._alive = False

        def wait(self, timeout=None):
            self._alive = False
            return 0

        def kill(self):
            self._alive = False

    monkeypatch.setattr(runtime_env, "_xvfb", lambda _log, _screen: (FakeProcess(), ":199"))
    monkeypatch.setattr(runtime_env.subprocess, "Popen", lambda *args, **kwargs: FakeProcess())
    class FakeCompleted:
        returncode = 0

    monkeypatch.setattr(runtime_env.subprocess, "run", lambda *args, **kwargs: FakeCompleted())
    window_reads: list[str] = []

    def fake_window_tree(display, deadline):
        window_reads.append(display)
        return "baseline" if len(window_reads) == 1 else "Window id: 0x1 (the root window)"

    monkeypatch.setattr(runtime_env, "_window_tree", fake_window_tree)
    monkeypatch.setattr(runtime_env, "_window_ids", lambda tree: {"base"} if tree == "baseline" else {"base", "new"})
    monkeypatch.setattr(runtime_env, "_game_window_ids", lambda _tree: ("0x2", "0x3"))
    def fake_xwininfo(display, window_id, deadline):
        if window_id == "0x3":
            return {"width": 800, "height": 600, "x": 10, "y": 20}
        return {"width": 1600, "height": 1200, "x": 0, "y": 0}

    monkeypatch.setattr(runtime_env, "_xwininfo_details", fake_xwininfo)
    monkeypatch.setattr(runtime_env, "_module_evidence", lambda *args, **kwargs: {"status": "OK"})
    monkeypatch.setattr(runtime_env, "_read_surface", lambda *args, **kwargs: {"values": [0, 800, 600]})
    monkeypatch.setattr(runtime_env, "_move_pointer_exact", lambda *args, **kwargs: {"x": 0, "y": 0})
    monkeypatch.setattr(
        runtime_env, "_capture_screenshot",
        lambda *args, **kwargs: (tmp_path / "shot.png", {"sha256": "shot"}),
    )
    monkeypatch.setattr(
        runtime_env, "_g1_selector_flow",
        lambda *args, **kwargs: ({"ps": 7}, {"sha256": "selector"}, {}),
    )
    monkeypatch.setattr(runtime_env, "_g1_menu_input_pass", lambda *args, **kwargs: True)
    scene = {
        "ps": 3,
        "tick": 1,
        "players": [{"nation": 1}, {"nation": 2}],
        "units": [{"owner": 0}, {"owner": 1}],
    }
    wait_states = [
        {"ps": 9},
        {"ps": 7},
        dict(scene),
    ]
    monkeypatch.setattr(runtime_env, "_wait_state", lambda *args, **kwargs: wait_states.pop(0))
    monkeypatch.setattr(runtime_env, "_g1_scene_snapshot", lambda *args, **kwargs: {
        "owners": {"0": {"nation": 1}, "1": {"nation": 2}},
        "unit_slots": [], "owner0_hq_world": None, "owner0_hq_candidates": None,
        "owner0_hq_type": {"status": "UNKNOWN"}, "world_bounds": {"width": 100, "height": 100},
        "camera": {},
    })
    # The imported runtime driver is only used by the local state() wrapper
    # during the sampling loop; return one stable presample before failure.
    from patches.population import runtime_driver
    monkeypatch.setattr(runtime_driver, "state", lambda pid, detailed: dict(scene))
    def fake_send_control_goal(prefix, goal, timeout):
        if goal == "_custom_game_chain_inject_seed1":
            return {"ok": True}
        raise runtime_env.RuntimeSafetyError("fake intervention failure")

    monkeypatch.setattr(runtime_env, "_g4_send_control_goal", fake_send_control_goal)
    monkeypatch.setattr(runtime_env, "_g1_input_verdict", lambda *args, **kwargs: {"required_inputs": False})
    monkeypatch.setattr(runtime_env, "_g1_baseline_verdict", lambda **kwargs: {"overall": "BLOCKED", **kwargs})
    monkeypatch.setattr(runtime_env, "_record_g1_command_cell_error", lambda *args, **kwargs: None)
    monkeypatch.setattr(runtime_env, "_g1_finalize_input_phase", lambda *args, **kwargs: None)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="fake intervention failure"):
        runtime_env.g1_baseline(
            manifest, timeout=5, g4_sample_seconds=0.2, g4_sample_period=0.05,
            g4_chain_goal="_custom_game_chain_inject_seed1",
            g4_intervention_goal="_g4_issue_idle_attack_probe", g4_intervention_delay=0.05,
        )

    evidence = json.loads((output / "g1_a" / "evidence.json").read_text())
    smoke = evidence["g4_ai_smoke"]
    assert len(smoke["samples"]) >= 1
    assert smoke["error"] == "fake intervention failure"
    intervention = evidence["g4_intervention"]
    assert intervention["goal"] == "_g4_issue_idle_attack_probe"
    assert intervention["requested_delay_seconds"] == 0.05
    assert intervention["status"] == "error"
    assert intervention["error"] == "fake intervention failure"
    assert evidence["cleanup"]["ok"] is True
    assert evidence["error"] == "fake intervention failure"


def test_g1_presentation_cli_forwards_opt_in_dxwrapper_profile(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}

    def fake_trace(manifest: Path, **kwargs: object) -> dict[str, object]:
        captured["manifest"] = manifest
        captured.update(kwargs)
        return {"overall": "BLOCKED"}

    monkeypatch.setattr(runtime_env, "g1_presentation_trace", fake_trace)
    result = runtime_env.runtime_main([
        "g1-presentation-trace", "--manifest", str(tmp_path / "manifest.json"),
        "--dxwrapper-2x", "--g1-input-sequence",
    ])
    assert result == 0
    assert captured["dxwrapper_2x"] is True
    assert captured["screen"] == "1600x1200x24"
    assert captured["g1_input_sequence"] is True


def test_g1_presentation_cli_forwards_native_2x_blit_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}

    def fake_trace(manifest: Path, **kwargs: object) -> dict[str, object]:
        captured["manifest"] = manifest
        captured.update(kwargs)
        return {"overall": "BLOCKED"}

    monkeypatch.setattr(runtime_env, "g1_presentation_trace", fake_trace)
    result = runtime_env.runtime_main([
        "g1-presentation-trace", "--manifest", str(tmp_path / "manifest.json"),
        "--native-2x-blit",
    ])
    assert result == 0
    assert captured["native_2x_blit"] is True
    assert captured["dxwrapper_2x"] is False


def test_g1_presentation_cli_forwards_native_2x_stretch_opt_in(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    captured: dict[str, object] = {}

    def fake_trace(manifest: Path, **kwargs: object) -> dict[str, object]:
        captured["manifest"] = manifest
        captured.update(kwargs)
        return {"overall": "BLOCKED"}

    monkeypatch.setattr(runtime_env, "g1_presentation_trace", fake_trace)
    result = runtime_env.runtime_main([
        "g1-presentation-trace", "--manifest", str(tmp_path / "manifest.json"),
        "--native-2x-blit", "--native-2x-stretch",
    ])
    assert result == 0
    assert captured["native_2x_blit"] is True
    assert captured["native_2x_stretch"] is True


def test_g1_presentation_cli_rejects_stretch_without_split(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
):
    result = runtime_env.runtime_main([
        "g1-presentation-trace", "--manifest", str(tmp_path / "manifest.json"),
        "--native-2x-stretch",
    ])
    assert result == 2
    assert "requires --native-2x-blit" in capsys.readouterr().err


def test_g1_presentation_cli_rejects_native_2x_with_dxwrapper(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
):
    result = runtime_env.runtime_main([
        "g1-presentation-trace", "--manifest", str(tmp_path / "manifest.json"),
        "--native-2x-blit", "--dxwrapper-2x",
    ])
    assert result == 2
    assert "mutually exclusive" in capsys.readouterr().err


def test_ps3_dwell_zero_does_not_read_or_capture():
    calls: list[str] = []

    def reader() -> dict[str, object]:
        calls.append("read")
        return {"ps": 3, "tick": 1}

    def capture(_tag: str) -> dict[str, object]:
        calls.append("capture")
        return {}

    assert runtime_env._observe_ps3_dwell(0, reader, capture) is None
    assert calls == []


def test_ps3_dwell_records_tick_samples_and_capture_failure():
    now = 0.0
    states = iter(({"ps": 3, "tick": 10}, {"ps": 3, "tick": 11}))
    captured: list[str] = []

    def monotonic() -> float:
        return now

    def sleep(seconds: float) -> None:
        nonlocal now
        now += seconds

    def reader() -> dict[str, object]:
        return next(states)

    def capture(tag: str) -> dict[str, object]:
        captured.append(tag)
        if tag == "ps3_dwell_plus_1s":
            raise RuntimeError("synthetic capture failure")
        return {"sha256": "a" * 64}

    result = runtime_env._observe_ps3_dwell(
        2, reader, capture, monotonic=monotonic, sleep=sleep,
    )

    assert result is not None
    assert [sample["tick"] for sample in result["samples"]] == [10, 11]  # type: ignore[index]
    assert captured == ["ps3_dwell_plus_1s"]
    assert result["screenshots"][0]["error"] == "RuntimeError: synthetic capture failure"  # type: ignore[index]


def test_g1_window_parser_keeps_game_and_content_child():
    tree = """
Window id: 0x21f (the root window)
  0xe00003 (\"syw2plus_original.exe\" \"syw2plus_original.exe\")  1x1+0+0  +0+0
  0xe00001 \"조선의반격\" (\"syw2plus_original.exe\" \"syw2plus_original.exe\")  800x600+10+20  +10+20
     0x800142 (has no name): ()  800x600+0+0  +10+20
"""
    assert runtime_env._game_window_ids(tree) == ("0xe00001", "0x800142")


def test_g1_window_parser_accepts_1600x1200_presentation_child_when_requested():
    tree = """
Window id: 0x21f (the root window)
  0xa00001 "조선의반격": ("syw2plus_original.exe" "syw2plus_original.exe")  1600x1200+0+0  +0+0
     0x800103 (has no name): ()  1600x1200+0+0  +0+0
"""
    assert runtime_env._game_window_ids(
        tree, allowed_sizes=((800, 600), (1600, 1200)),
    ) == ("0xa00001", "0x800103")


def test_g1_logical_surface_contract_requires_original_dimensions(tmp_path: Path):
    events = [
        {"event": "set_display_mode", "seq": 1, "width": 800, "height": 600, "bpp": 8},
        {"event": "create_surface", "seq": 2, "returned_surface": "0x1000",
         "descriptor": {"flags": 33, "backbuffer_count": 1}},
        {"event": "get_surface_desc", "seq": 3, "surface": "0x1000",
         "actual_desc": {"width": 800, "height": 600}},
    ]
    trace = tmp_path / "trace.jsonl"
    trace.write_text("\n".join(json.dumps(event) for event in events) + "\n")
    evidence = runtime_env._presentation_logical_surface_contract(trace)
    assert evidence["logical_content_size"] == [800, 600]
    assert evidence["last_set_display_mode"]["width"] == 800
    assert evidence["primary_surface"]["actual_desc"] == {"width": 800, "height": 600}


def test_g1_surface_reader_records_documented_fields():
    def read(address: int, size: int) -> bytes:
        if address == 0x00E5BF18:
            return struct.pack("<6I", 3, 800, 600, 8, 800, 600)
        assert address == 0x00B3AC80 and size == 16
        return struct.pack("<4i", 0, 0, 799, 599)

    evidence = runtime_env._read_surface(read, 3)
    assert evidence["values"] == [3, 800, 600, 8, 800, 600]
    assert evidence["viewport"] == [0, 0, 799, 599]


def test_g1_local_setup_path_keeps_visible_controls_separate():
    assert runtime_env.G1_SETUP_POINTS == {
        "multiplayer_mode": (344, 169),
        "solo_mode": (462, 169),
        "connection_confirm": (608, 564),
        "lobby_start": (608, 564),
    }
    assert runtime_env.G1_NEUTRAL_POINT == (760, 40)


def test_move_pointer_exact_accepts_pointer_already_at_target(monkeypatch: pytest.MonkeyPatch):
    calls: list[list[str]] = []

    def fake_run(argv, **kwargs):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "X=760\nY=40\nSCREEN=0\n", "")

    monkeypatch.setattr(runtime_env.subprocess, "run", fake_run)
    result = runtime_env._move_pointer_exact(
        {"DISPLAY": ":199"}, (760, 40), timeout=0.1,
    )

    assert result["verified"] is True
    assert result["before_root"] == [760, 40]
    assert result["move"]["attempted"] is False
    assert calls == [["xdotool", "getmouselocation", "--shell"]]


def test_move_pointer_exact_polls_until_target_is_observed(monkeypatch: pytest.MonkeyPatch):
    calls: list[list[str]] = []
    positions = iter(["X=1\nY=2\n", "X=760\nY=40\n"])

    def fake_run(argv, **kwargs):
        calls.append(argv)
        if argv[1] == "getmouselocation":
            return subprocess.CompletedProcess(argv, 0, next(positions), "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(runtime_env.subprocess, "run", fake_run)
    result = runtime_env._move_pointer_exact(
        {"DISPLAY": ":199"}, (760, 40), timeout=0.1,
    )

    assert result["verified"] is True
    assert result["before_root"] == [1, 2]
    assert result["last_observed_root"] == [760, 40]
    assert result["move"]["polls"] == 1
    assert calls == [
        ["xdotool", "getmouselocation", "--shell"],
        ["xdotool", "mousemove", "760", "40"],
        ["xdotool", "getmouselocation", "--shell"],
    ]


def test_move_pointer_exact_rejects_bounded_coordinate_mismatch(monkeypatch: pytest.MonkeyPatch):
    def fake_run(argv, **kwargs):
        if argv[1] == "getmouselocation":
            return subprocess.CompletedProcess(argv, 0, "X=1\nY=2\n", "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    monkeypatch.setattr(runtime_env.subprocess, "run", fake_run)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="requested root coordinate") as caught:
        runtime_env._move_pointer_exact(
            {"DISPLAY": ":199"}, (760, 40), timeout=0.01, poll_interval=0.001,
        )

    message = str(caught.value)
    assert "requested=[760, 40]" in message
    assert "before=[1, 2]" in message
    assert "last_observed=[1, 2]" in message
    assert "returncode': 0" in message


@pytest.mark.parametrize(
    ("stdout", "returncode", "message"),
    [("X=oops\nY=40\n", 0, "malformed"), ("", 1, "query failed")],
)
def test_move_pointer_exact_rejects_malformed_or_failed_query(
    monkeypatch: pytest.MonkeyPatch, stdout: str, returncode: int, message: str,
):
    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, returncode, stdout, "query-error")

    monkeypatch.setattr(runtime_env.subprocess, "run", fake_run)
    with pytest.raises(runtime_env.RuntimeSafetyError, match=message) as caught:
        runtime_env._move_pointer_exact({"DISPLAY": ":199"}, (760, 40), timeout=0.1)

    assert "requested=[760, 40]" in str(caught.value)


class _ExitedProcess:
    returncode = 0

    def poll(self) -> int:
        return self.returncode


def test_g1_trace_finalization_closes_owned_window_before_accepting_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(json.dumps({"run_id": "run-1", "event": "summary"}) + "\n")
    calls: list[tuple[int, Path]] = []

    def fake_close(display, pid, helper, env, deadline, log):
        calls.append((pid, helper))
        return {"result": {"status": "PASS", "requested_pid": pid,
                            "match_count": 1, "post_result": True}}

    monkeypatch.setattr(runtime_env, "_request_owned_game_close", fake_close)
    helper = tmp_path / "helper.exe"
    result = runtime_env._finalize_presentation_trace(
        ":199", 123, helper, {"DISPLAY": ":199"}, None, _ExitedProcess(), trace,
        "run-1", time.monotonic(), 0.2,
    )

    assert result["status"] == "PASS"
    assert result["summary_count"] == 1
    assert calls == [(123, helper)]


def test_g1_trace_finalization_blocks_after_owned_process_exit_without_summary(tmp_path: Path):
    trace = tmp_path / "trace.jsonl"
    raw = json.dumps({"run_id": "run-1", "event": "blt_fast"}) + "\n"
    trace.write_text(raw)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="expected one summary"):
        runtime_env._wait_for_clean_trace_close(
            _ExitedProcess(), trace, "run-1", time.monotonic(), 0.2,
        )

    assert trace.read_text() == raw


def test_g1_finalization_records_close_before_wait_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    evidence: dict[str, object] = {}

    monkeypatch.setattr(
        runtime_env, "_request_owned_game_close",
        lambda *args, **kwargs: {"result": {"status": "PASS", "post_result": True}},
    )

    def fail_wait(*args, **kwargs):
        raise runtime_env.RuntimeSafetyError("probe timeout")

    monkeypatch.setattr(runtime_env, "_wait_for_clean_trace_close", fail_wait)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="probe timeout"):
        runtime_env._finalize_presentation_trace(
            ":199", 123, tmp_path / "helper.exe", {"DISPLAY": ":199"}, None,
            _ExitedProcess(), tmp_path / "trace.jsonl", "run-1", time.monotonic(), 1,
            evidence,
        )

    assert evidence["trace_finalization"] == {
        "close_transport": {"result": {"status": "PASS", "post_result": True}},
    }


def test_g1_finalization_collects_two_owned_liveness_samples(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    class RunningProcess:
        pid = 123
        returncode = None

        def poll(self) -> None:
            return None

    snapshots: list[int] = []

    def snapshot(pid: int) -> list[dict[str, object]]:
        snapshots.append(pid)
        return [{"pid": pid, "state": "R", "utime": len(snapshots),
                 "stime": 0, "threads": 2}]

    monkeypatch.setattr(runtime_env, "_owned_runtime_process_snapshot", snapshot)
    trace = tmp_path / "trace.jsonl"
    trace.write_text(json.dumps({"run_id": "run-1", "event": "blt_fast"}) + "\n")
    samples: list[dict[str, object]] = []
    with pytest.raises(runtime_env.RuntimeSafetyError, match="timed out"):
        runtime_env._wait_for_clean_trace_close(
            RunningProcess(), trace, "run-1", time.monotonic(), 0.01,
            poll_interval=0.001, liveness_samples=samples, liveness_delay=0,
        )

    assert snapshots == [123, 123]
    assert [sample["sample"] for sample in samples] == [1, 2]
    assert all(sample["processes"][0]["state"] == "R" for sample in samples)  # type: ignore[index]


def test_g1_finalization_collects_program_state_and_two_screenshots(tmp_path: Path):
    trace = tmp_path / "trace.jsonl"
    trace.write_text(json.dumps({"run_id": "run-1", "event": "summary"}) + "\n")
    started = time.monotonic() - 10
    states: list[dict[str, object]] = []
    screenshots: list[dict[str, object]] = []

    result = runtime_env._wait_for_clean_trace_close(
        _ExitedProcess(), trace, "run-1", started, 12,
        program_state_reader=lambda: {"ps": 2},
        finalization_program_state=states,
        screenshot_capture=lambda tag: {"path": f"/{tag}.png", "sha256": "a" * 64,
                                        "dimensions": [1600, 1200]},
        finalization_screenshots=screenshots,
        finalization_started=started,
        program_state_interval=0,
    )

    assert result["status"] == "PASS"
    assert states and states[0]["ps"] == 2
    assert [item["tag"] for item in screenshots] == [
        "close_plus_5s", "timeout_minus_5s",
    ]
    assert all(item["dimensions"] == [1600, 1200] for item in screenshots)


@pytest.mark.parametrize(
    ("reader_states", "expected_ticks", "expected_tick_errors"),
    [
        ([{"ps": 3, "tick": 10}, {"ps": 3, "tick": 11}], [10, 11, 11], []),
        ([{"ps": 3, "tick": 10}, {"ps": 3, "tick": 10}], [10, 10, 10], []),
        ([{"ps": 3}, {"ps": 3}], [], ["program state reader returned no integer tick"] * 3),
    ],
    ids=["tick-increases", "tick-stalls", "tick-missing"],
)
def test_g1_finalization_records_tick_observations_without_losing_ps(
    tmp_path: Path,
    reader_states: list[dict[str, object]],
    expected_ticks: list[int],
    expected_tick_errors: list[str],
):
    class RunningThenExitedProcess:
        returncode = 0

        def __init__(self) -> None:
            self.poll_count = 0

        def poll(self) -> int | None:
            self.poll_count += 1
            return None if self.poll_count < 3 else self.returncode

    trace = tmp_path / "trace.jsonl"
    trace.write_text(json.dumps({"run_id": "run-1", "event": "summary"}) + "\n")
    states: list[dict[str, object]] = []
    reader_index = 0

    def reader() -> dict[str, object]:
        nonlocal reader_index
        state = reader_states[min(reader_index, len(reader_states) - 1)]
        reader_index += 1
        return state

    result = runtime_env._wait_for_clean_trace_close(
        RunningThenExitedProcess(), trace, "run-1", time.monotonic() - 10, 12,
        poll_interval=0.011, program_state_reader=reader,
        finalization_program_state=states, program_state_interval=0.001,
    )

    assert result["status"] == "PASS"
    assert [sample["ps"] for sample in states] == [3, 3, 3]
    assert [sample["tick"] for sample in states if "tick" in sample] == expected_ticks
    assert [sample["tick_error"] for sample in states if "tick_error" in sample] == expected_tick_errors


def test_owned_liveness_snapshot_stays_within_process_tree(tmp_path: Path):
    proc_root = tmp_path / "proc"
    for pid in (10, 11):
        (proc_root / str(pid) / "task" / str(pid)).mkdir(parents=True)
    (proc_root / "10" / "task" / "10" / "children").write_text("11\n")
    (proc_root / "11" / "task" / "11" / "children").write_text("")

    def stat(pid: int, state: str, utime: int, stime: int, threads: int) -> str:
        fields = [state, "1"] + ["0"] * 18
        fields[11], fields[12], fields[17] = str(utime), str(stime), str(threads)
        return f"{pid} (owned wine process) " + " ".join(fields) + "\n"

    (proc_root / "10" / "stat").write_text(stat(10, "R", 12, 3, 4))
    (proc_root / "11" / "stat").write_text(stat(11, "S", 8, 2, 1))
    (proc_root / "10" / "task" / "10" / "stat").write_text(stat(10, "R", 12, 3, 4))
    (proc_root / "10" / "task" / "12").mkdir()
    (proc_root / "10" / "task" / "12" / "stat").write_text(stat(12, "S", 4, 1, 2))
    (proc_root / "11" / "task" / "11" / "stat").write_text(stat(11, "S", 8, 2, 1))

    assert runtime_env._owned_runtime_process_pids(10, proc_root) == [10, 11]
    assert runtime_env._linux_process_stat(10, proc_root) == {
        "pid": 10, "state": "R", "utime": 12, "stime": 3, "threads": 4,
    }
    snapshot = runtime_env._owned_runtime_process_snapshot(10, proc_root)
    assert snapshot[0]["threads_detail"] == [
        {"tid": 10, "state": "R", "utime": 12, "stime": 3, "threads": 4},
        {"tid": 12, "state": "S", "utime": 4, "stime": 1, "threads": 2},
    ]
    assert snapshot[1]["threads_detail"] == [
        {"tid": 11, "state": "S", "utime": 8, "stime": 2, "threads": 1},
    ]


def test_dxwrapper_logs_are_copied_and_hashed(tmp_path: Path):
    game = tmp_path / "game"
    output = tmp_path / "output"
    game.mkdir()
    (game / "dxwrapper-original.log").write_bytes(b"Lock2 Error\n")
    (game / "not-a-wrapper.log").write_bytes(b"ignore\n")
    config: dict[str, object] = {}

    runtime_env._preserve_dxwrapper_logs(game, output, config)

    records = config["wrapper_logs"]
    assert isinstance(records, list)
    assert len(records) == 1
    record = records[0]
    assert record["path"] == str(output / "wrapper_logs" / "dxwrapper-original.log")
    assert record["sha256"] == hashlib.sha256(b"Lock2 Error\n").hexdigest()


def test_g1_trace_pipeline_orders_close_exit_summary_copy_and_validator(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    trace = tmp_path / "trace.jsonl"
    trace.write_text("raw trace\n", encoding="utf-8")
    raw_copy = tmp_path / "output" / "trace_raw.jsonl"
    trace_copy = tmp_path / "output" / "trace.jsonl"
    trace_copy.parent.mkdir()
    evidence: dict[str, object] = {}
    order: list[str] = []

    def fake_close(display, pid, helper, env, deadline, log):
        assert pid == 123
        order.append("close")
        return {"result": {"status": "PASS", "requested_pid": pid,
                            "match_count": 1, "post_result": True}}

    monkeypatch.setattr(runtime_env, "_request_owned_game_close", fake_close)

    class Process:
        returncode = 0

        def poll(self) -> int:
            order.append("exit")
            return self.returncode

    def finalization_state(trace_path: Path, run_id: str) -> dict[str, object]:
        assert trace_path == trace
        assert run_id == "run-1"
        order.append("summary")
        return {"ready": True, "reason": "one final summary observed", "summary_count": 1,
                "event_count": 1}

    monkeypatch.setattr(runtime_env, "_trace_finalization_state", finalization_state)
    real_copy = runtime_env.shutil.copy2

    def copy(source: Path, destination: Path):
        order.append("copy")
        return real_copy(source, destination)

    monkeypatch.setattr(runtime_env.shutil, "copy2", copy)
    from tools import check_g1_presentation_trace

    def validate(path: Path, *, capture: dict[str, object]):
        assert path == trace_copy
        assert capture == {"run_id": "run-1"}
        order.append("validator")
        return {"status": "PASS"}

    monkeypatch.setattr(check_g1_presentation_trace, "validate", validate)
    runtime_env._finalize_copy_validate_presentation_trace(
        ":199", 123, tmp_path / "helper.exe", {"DISPLAY": ":199"}, None,
        Process(), trace, raw_copy, trace_copy, "run-1", time.monotonic(), 0.2,
        {"run_id": "run-1"}, evidence,
    )

    assert order == ["close", "exit", "summary", "copy", "validator"]
    assert evidence["trace_finalization"]["summary_count"] == 1
    assert evidence["validator"] == {"status": "PASS"}


@pytest.mark.parametrize(
    ("events", "exited", "message"),
    [
        ([{"event": "blt_fast"}], True, "expected one summary"),
        ([{"event": "summary"}, {"event": "summary"}], True, "expected one summary"),
        ([{"event": "summary"}, {"event": "blt_fast"}], True, "summary is not the final"),
        ([{"event": "summary"}], False, "timed out"),
    ],
)
def test_g1_trace_pipeline_preserves_raw_and_skips_validator_until_clean_close(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
    events: list[dict[str, object]], exited: bool, message: str,
):
    trace = tmp_path / "trace.jsonl"
    raw = "\n".join(json.dumps({"run_id": "run-1", **event}) for event in events) + "\n"
    trace.write_text(raw, encoding="utf-8")
    raw_copy = tmp_path / "output" / "trace_raw.jsonl"
    trace_copy = tmp_path / "output" / "trace.jsonl"

    monkeypatch.setattr(
        runtime_env, "_request_owned_game_close",
        lambda *args, **kwargs: {"result": {"status": "PASS", "requested_pid": 123,
                                               "match_count": 1, "post_result": True}},
    )
    from tools import check_g1_presentation_trace

    def unexpected_validator(*args, **kwargs):
        pytest.fail("validator must not run before clean finalization")

    monkeypatch.setattr(check_g1_presentation_trace, "validate", unexpected_validator)

    class Process:
        returncode = 0 if exited else None

        def poll(self) -> int | None:
            return self.returncode

    with pytest.raises(runtime_env.RuntimeSafetyError, match=message):
        runtime_env._finalize_copy_validate_presentation_trace(
            ":199", 123, tmp_path / "helper.exe", {"DISPLAY": ":199"}, None,
            Process(), trace, raw_copy, trace_copy, "run-1", time.monotonic(), 0.01, {}, {},
        )

    assert raw_copy.read_text(encoding="utf-8") == raw
    assert not trace_copy.exists()


def test_g1_trace_pipeline_separates_install_snapshot_from_growing_final_raw(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
):
    trace = tmp_path / "trace.jsonl"
    install_copy = tmp_path / "output" / "trace_install.jsonl"
    raw_copy = tmp_path / "output" / "trace_raw.jsonl"
    trace_copy = tmp_path / "output" / "trace.jsonl"
    install_events = [
        {"run_id": "run-1", "event": "install", "install_status": "active", "stage": "complete"},
    ] + [{"run_id": "run-1", "event": "install_detail", "seq": index}
         for index in range(2, 117)]
    install_raw = "".join(json.dumps(event) + "\n" for event in install_events).encode()
    trace.write_bytes(install_raw)
    gate = runtime_env._presentation_trace_install_gate(trace, install_copy, "run-1")
    assert gate["install_trace"] == str(install_copy)
    assert install_copy.read_bytes() == install_raw

    final_events = install_events + [
        {"run_id": "run-1", "event": "blt_fast", "seq": index}
        for index in range(117, 618)
    ]
    final_raw = "".join(json.dumps(event) + "\n" for event in final_events).encode()

    class GrowingProcess:
        returncode = 0

        def poll(self) -> int:
            trace.write_bytes(final_raw)
            return self.returncode

    monkeypatch.setattr(
        runtime_env, "_request_owned_game_close",
        lambda *args, **kwargs: {"result": {"status": "PASS", "requested_pid": 123,
                                               "match_count": 1, "post_result": True}},
    )
    from tools import check_g1_presentation_trace

    validator_calls: list[Path] = []

    def unexpected_validator(path: Path, **kwargs: object):
        validator_calls.append(path)
        pytest.fail("validator must not run before clean finalization")

    monkeypatch.setattr(check_g1_presentation_trace, "validate", unexpected_validator)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="expected one summary"):
        runtime_env._finalize_copy_validate_presentation_trace(
            ":199", 123, tmp_path / "helper.exe", {"DISPLAY": ":199"}, None,
            GrowingProcess(), trace, raw_copy, trace_copy, "run-1", time.monotonic(), 0.2, {}, {},
        )

    assert len(install_copy.read_bytes().splitlines()) == 116
    assert install_copy.read_bytes() == install_raw
    assert len(raw_copy.read_bytes().splitlines()) == 617
    assert raw_copy.read_bytes() == final_raw
    assert validator_calls == []
    assert not trace_copy.exists()


def test_g1_lobby_mode_reader_uses_documented_committed_word_field():
    def read(address: int, size: int) -> bytes:
        assert address == runtime_env.G1_COMMITTED_MODE_ADDRESS and size == 2
        return struct.pack("<H", 1)

    assert runtime_env._read_lobby_mode(read) == 1


def test_g1_selector_reader_requires_two_documented_dword_states():
    reads: list[tuple[int, int]] = []

    def read(address: int, size: int) -> bytes:
        reads.append((address, size))
        values = {
            0x0106A6A4: 1,
            0x0106A86C: 0,
        }
        return struct.pack("<I", values[address])

    assert runtime_env._read_lobby_selector(read) == {
        "multiplayer": 1,
        "solo": 0,
        "selected": "multiplayer",
    }
    assert reads == [(0x0106A6A4, 4), (0x0106A86C, 4)]


@pytest.mark.parametrize("values", [(0, 0), (1, 1), (2, 0), (0, 2)])
def test_g1_selector_reader_rejects_non_one_hot_states(values: tuple[int, int]):
    def read(address: int, size: int) -> bytes:
        assert size == 4
        value = values[0] if address == 0x0106A6A4 else values[1]
        return struct.pack("<I", value)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="one-hot"):
        runtime_env._read_lobby_selector(read)


def test_g1_local_ready_reader_uses_bounded_index_and_dword_slot():
    reads: list[tuple[int, int]] = []

    def read(address: int, size: int) -> bytes:
        reads.append((address, size))
        values = {
            runtime_env.G1_LOCAL_PLAYER_INDEX_ADDRESS: 3,
            runtime_env.G1_READY_STATE_BASE_ADDRESS + 3 * 4: 1,
        }
        return struct.pack("<I", values[address])

    assert runtime_env._read_local_ready_state(read) == {
        "local_index": 3,
        "ready_address": runtime_env.G1_READY_STATE_BASE_ADDRESS + 3 * 4,
        "ready_value": 1,
    }
    assert reads == [
        (runtime_env.G1_LOCAL_PLAYER_INDEX_ADDRESS, 4),
        (runtime_env.G1_READY_STATE_BASE_ADDRESS + 3 * 4, 4),
    ]


@pytest.mark.parametrize("local_index", [-1, 8, 0xFFFFFFFF])
def test_g1_local_ready_reader_rejects_out_of_range_index(local_index: int):
    def read(address: int, size: int) -> bytes:
        assert address == runtime_env.G1_LOCAL_PLAYER_INDEX_ADDRESS and size == 4
        return struct.pack("<I", local_index & 0xFFFFFFFF)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="local player index"):
        runtime_env._read_local_ready_state(read)


def test_g1_local_ready_reader_rejects_unknown_ready_value():
    def read(address: int, size: int) -> bytes:
        assert size == 4
        value = 0 if address == runtime_env.G1_LOCAL_PLAYER_INDEX_ADDRESS else 2
        return struct.pack("<I", value)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="ready DWORD"):
        runtime_env._read_local_ready_state(read)


def _command_cell_reader_fixture(
    *,
    selected_slot: int = 7,
    selected_count: int = 1,
    unit_active: int = 1,
    unit_type: int = 58,
    target_groups: tuple[int, ...] = (2,),
    boundary_target: bool = False,
    duplicate_group: int | None = None,
    empty_pool: bool = False,
    branch_type_flags: int = runtime_env.G1_COMMAND_BRANCH_REQUIRED_MASK,
    selected_unit_state: int = 0,
    alternate_count: int = 0,
    alternate_records: tuple[tuple[int, int], ...] | None = None,
    alternate_flags: tuple[int, ...] | None = None,
    alternate_geometry: tuple[int, int, int, int] = (100, 200, 30, 40),
    primary_values: tuple[tuple[int, ...], ...] | None = None,
):
    ranges: list[tuple[int, bytes]] = []

    def add(address: int, raw: bytes) -> None:
        ranges.append((address, raw))

    add(runtime_env.G1_SELECTION_COUNT_ADDRESS, struct.pack("<i", selected_count))
    add(runtime_env.G1_SELECTION_FIRST_SLOT_ADDRESS, struct.pack("<h", selected_slot))
    add(
        runtime_env.G1_UNIT_EXISTS_BASE_ADDRESS + selected_slot * 2,
        struct.pack("<h", unit_active),
    )
    unit_address = runtime_env.G1_UNIT_BASE_ADDRESS + selected_slot * runtime_env.G1_UNIT_STRIDE
    add(unit_address + runtime_env.G1_UNIT_TYPE_OFFSET, struct.pack("<B", unit_type))
    type_address = runtime_env.G1_UNIT_TYPE_TABLE_BASE_ADDRESS + unit_type * runtime_env.G1_UNIT_STRIDE
    add(type_address, struct.pack("<4I", 0x101, 0x202, 0x303, 0x404))
    branch_type_address = (
        runtime_env.G1_COMMAND_BRANCH_TYPE_FLAGS_BASE_ADDRESS
        + unit_type * runtime_env.G1_COMMAND_BRANCH_TYPE_FLAGS_STRIDE
    )
    add(branch_type_address, struct.pack("<B", branch_type_flags))
    add(
        unit_address + runtime_env.G1_SELECTED_UNIT_COMMAND_STATE_OFFSET,
        struct.pack("<I", selected_unit_state),
    )
    if alternate_records is None:
        alternate_records = tuple((0, 0) for _ in range(runtime_env.G1_ALTERNATE_UI_RECORD_COUNT))
    if alternate_flags is None:
        alternate_flags = tuple(0 for _ in range(runtime_env.G1_ALTERNATE_UI_RECORD_COUNT))
    assert len(alternate_records) == runtime_env.G1_ALTERNATE_UI_RECORD_COUNT
    assert len(alternate_flags) == runtime_env.G1_ALTERNATE_UI_RECORD_COUNT
    add(
        unit_address + runtime_env.G1_ALTERNATE_UI_COUNT_OFFSET,
        struct.pack("<H", alternate_count),
    )
    add(
        unit_address + runtime_env.G1_ALTERNATE_UI_RECORDS_OFFSET,
        b"".join(struct.pack("<2H", *record) for record in alternate_records),
    )
    add(
        runtime_env.G1_ALTERNATE_UI_FLAGS_BASE_ADDRESS,
        b"".join(struct.pack("<H", value) for value in alternate_flags),
    )
    add(
        runtime_env.G1_ALTERNATE_UI_GEOMETRY_BASE_ADDRESS,
        struct.pack("<4H", *alternate_geometry),
    )
    if primary_values is None:
        primary_values = tuple(
            tuple(0 for _ in range(runtime_env.G1_PRIMARY_COMMAND_TABLE_WORD_COUNT))
            for _ in runtime_env.G1_PRIMARY_COMMAND_TABLE_BLOCKS
        )
    assert len(primary_values) == len(runtime_env.G1_PRIMARY_COMMAND_TABLE_BLOCKS)
    assert all(
        len(values) == runtime_env.G1_PRIMARY_COMMAND_TABLE_WORD_COUNT
        for values in primary_values
    )
    primary = bytearray(runtime_env.G1_PRIMARY_COMMAND_TABLE_READ_SIZE)
    for values, (_name, offset) in zip(primary_values, runtime_env.G1_PRIMARY_COMMAND_TABLE_BLOCKS):
        struct.pack_into("<12H", primary, offset, *values)
    add(runtime_env.G1_PRIMARY_COMMAND_TABLE_BASE_ADDRESS, bytes(primary))

    pool = bytearray(runtime_env.G1_COMMAND_CELL_POOL_READ_SIZE)
    for slot in runtime_env.G1_COMMAND_CELL_POOL_SLOTS:
        raw = bytearray(runtime_env.G1_COMMAND_CELL_READ_SIZE)
        group = 0 if empty_pool else (slot + 1 if slot <= 4 else 0)
        if duplicate_group in runtime_env.G1_COMMAND_CELL_GROUPS and slot == 5:
            group = duplicate_group
        if group in runtime_env.G1_COMMAND_CELL_GROUPS:
            base_x = 600
            delta_x = 140
            x = base_x + (group - 2) * delta_x
            if group in target_groups:
                x = base_x
            y = 450
            width = 100
            height = 100
            if boundary_target and group == target_groups[0]:
                x = runtime_env.G1_COMMAND_CELL_TARGET[0]
            struct.pack_into("<I", raw, runtime_env.G1_COMMAND_CELL_ACTIVE_OFFSET, 1)
            struct.pack_into("<I", raw, runtime_env.G1_COMMAND_CELL_GROUP_OFFSET, group)
            struct.pack_into(
                "<4i", raw, runtime_env.G1_COMMAND_CELL_X_OFFSET, x, y, width, height
            )
            struct.pack_into("<I", raw, runtime_env.G1_COMMAND_CELL_CATEGORY_OFFSET, 0x43)
            struct.pack_into("<I", raw, runtime_env.G1_COMMAND_CELL_FLAG_OFFSET, 0x40000)
            struct.pack_into(
                "<I", raw, runtime_env.G1_COMMAND_CELL_CLICK_CALLBACK_OFFSET,
                runtime_env.G1_COMMAND_CELL_CLICK_CALLBACK,
            )
            struct.pack_into(
                "<I", raw, runtime_env.G1_COMMAND_CELL_HIT_CALLBACK_OFFSET,
                runtime_env.G1_COMMAND_CELL_HIT_CALLBACK,
            )
        offset = (slot - runtime_env.G1_COMMAND_CELL_POOL_FIRST_SLOT) * runtime_env.G1_COMMAND_CELL_POOL_STRIDE
        pool[offset:offset + runtime_env.G1_COMMAND_CELL_READ_SIZE] = raw
    add(runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START, bytes(pool))

    def read(address: int, size: int) -> bytes:
        for start, raw in ranges:
            if start <= address and address + size <= start + len(raw):
                return raw[address - start:address - start + size]
        raise AssertionError(f"unexpected read {address:#x}+{size}")

    return read


def test_g1_selection_evidence_records_approved_slot_and_type():
    evidence = runtime_env._read_g1_selection_evidence(
        _command_cell_reader_fixture(selected_slot=7, selected_count=1, unit_type=58)
    )

    assert evidence["count"] == 1
    assert evidence["first_slot"] == 7
    assert evidence["selected_slot"] == 7
    assert evidence["selected_type"] == 58
    assert "G1_UNIT_BASE_ADDRESS" in evidence["selected_type_provenance"]


def test_g1_selection_evidence_keeps_identity_failure_nonfatal():
    evidence = runtime_env._read_g1_selection_evidence(
        _command_cell_reader_fixture(selected_slot=7, selected_count=1, unit_active=0)
    )

    assert evidence["selected_slot"] == 7
    assert evidence["selected_type"] == "UNKNOWN"
    assert evidence["selected_type_provenance"].startswith("_CommandCellSnapshotError:")


def test_g1_selection_evidence_marks_empty_selection_as_unknown_without_type_read():
    evidence = runtime_env._read_g1_selection_evidence(
        _command_cell_reader_fixture(selected_slot=-1, selected_count=0)
    )

    assert evidence["selected_slot"] is None
    assert evidence["selected_type"] == "UNKNOWN"
    assert evidence["selected_type_provenance"] == "no selected unit: selection count is zero"


def test_g1_command_cell_reader_fails_closed_before_memory_read_on_sha_mismatch():
    reads: list[tuple[int, int]] = []

    def read(address: int, size: int) -> bytes:
        reads.append((address, size))
        raise AssertionError("SHA mismatch must be checked before memory reads")

    with pytest.raises(runtime_env.RuntimeSafetyError, match="unexpected executable SHA-256"):
        runtime_env._read_g1_command_cell_provenance(read, "0" * 64)
    assert reads == []


def test_g1_command_cell_reader_records_type_base_cells_and_strict_hit():
    read = _command_cell_reader_fixture()

    evidence = runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)

    assert evidence["selection"] == {"count": 1, "first_slot": 7}
    assert evidence["unit"]["active"] == 1
    assert evidence["unit"]["type"] == 58
    assert evidence["type_command"] == {
        "address": "0x00686878",
        "values": [0x101, 0x202, 0x303, 0x404],
    }
    branch = evidence["command_branch"]
    assert branch["call_address"] == "0x0049B6D0"
    assert branch["stable"] is True
    assert branch["eligible"] is True
    assert branch["before_pool"]["type_predicate"] == {
        "address": "0x009C21D4",
        "raw_value": 0x08,
        "mask": "0x08",
        "masked_value": 0x08,
        "passes": True,
    }
    assert branch["before_pool"]["selected_unit_predicate"] == {
        "address": "0x0066EB8C",
        "offset": "0x94",
        "raw_value": 0,
        "passes": True,
    }
    assert branch["before_pool"]["phase"] == "before_pool"
    assert branch["after_pool"]["phase"] == "after_pool"
    assert [cell["group"] for cell in evidence["cells"]] == [2, 3, 4, 5]
    assert [cell["x"] for cell in evidence["cells"]] == [600, 740, 880, 1020]
    assert evidence["target"]["hit_group"] == 2
    assert evidence["primary_command_table"]["stable"] is True
    assert evidence["primary_command_table"]["before"]["size"] == 0x60
    assert tuple(evidence["primary_command_table"]["before"]["blocks"]) == ("A6", "BE", "D6", "EE")
    assert evidence["cells"][0]["callbacks"] == {
        "click": "0x0049B530",
        "hit": "0x0049B640",
    }


def test_g1_command_cell_pool_uses_allocator_bounds_and_one_contiguous_read():
    calls: list[tuple[int, int]] = []
    fixture = _command_cell_reader_fixture()

    def read(address: int, size: int) -> bytes:
        calls.append((address, size))
        return fixture(address, size)

    evidence = runtime_env._read_g1_command_cell_provenance(
        read, runtime_env.ORIGINAL_SHA256
    )

    assert runtime_env.G1_COMMAND_CELL_POOL_COUNT == 29
    assert runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START == (
        runtime_env.G1_COMMAND_CELL_POOL_BASE_ADDRESS
        + runtime_env.G1_COMMAND_CELL_POOL_FIRST_SLOT * runtime_env.G1_COMMAND_CELL_POOL_STRIDE
    )
    assert runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_END == (
        runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START
        + runtime_env.G1_COMMAND_CELL_POOL_COUNT * runtime_env.G1_COMMAND_CELL_POOL_STRIDE
    )
    assert calls.count(
        (runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START,
         runtime_env.G1_COMMAND_CELL_POOL_READ_SIZE)
    ) == 1
    assert calls.count(
        (runtime_env.G1_PRIMARY_COMMAND_TABLE_BASE_ADDRESS,
         runtime_env.G1_PRIMARY_COMMAND_TABLE_READ_SIZE)
    ) == 2
    assert all(
        address != runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_END
        for address, _size in calls
    )
    assert evidence["snapshot_attempts"] == 1


def test_g1_command_cell_reader_polls_empty_then_accepts_coherent_snapshot():
    valid = _command_cell_reader_fixture()
    empty = _command_cell_reader_fixture(empty_pool=True)
    pool_reads = 0

    def read(address: int, size: int) -> bytes:
        nonlocal pool_reads
        if address == runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START:
            pool_reads += 1
            return (empty if pool_reads == 1 else valid)(address, size)
        return valid(address, size)

    evidence = runtime_env._read_g1_command_cell_provenance(
        read,
        runtime_env.ORIGINAL_SHA256,
        started=time.monotonic(),
        timeout=0.2,
        poll_interval=0.001,
    )

    assert pool_reads == 2
    assert evidence["snapshot_attempts"] == 2
    assert [cell["group"] for cell in evidence["cells"]] == [2, 3, 4, 5]


def test_g1_command_cell_reader_preserves_bounded_diagnostics_on_permanent_empty_pool():
    read = _command_cell_reader_fixture(empty_pool=True)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="coherent snapshot timed out") as caught:
        runtime_env._read_g1_command_cell_provenance(
            read,
            runtime_env.ORIGINAL_SHA256,
            started=time.monotonic(),
            timeout=0.01,
            poll_interval=0.001,
        )

    diagnostics = getattr(caught.value, "command_cell_diagnostics")
    assert 1 <= len(diagnostics) <= runtime_env.G1_COMMAND_CELL_DIAGNOSTIC_ATTEMPTS
    assert diagnostics[-1]["attempt"] >= 1
    assert "timestamp" in diagnostics[-1]
    assert diagnostics[-1]["raw"] == []
    assert diagnostics[-1]["command_branch"]["stable"] is True
    assert diagnostics[-1]["command_branch"]["eligible"] is True


@pytest.mark.parametrize(
    ("fixture_kwargs", "message"),
    [
        ({"selected_slot": 1200}, "selected-unit slot"),
        ({"unit_type": 0}, "selected unit has unsupported type"),
        ({"target_groups": (2, 3)}, "one strict hit"),
        ({"boundary_target": True}, "one strict hit"),
    ],
)
def test_g1_command_cell_reader_rejects_invalid_selection_type_or_hit(
    fixture_kwargs: dict[str, object], message: str
):
    read = _command_cell_reader_fixture(**fixture_kwargs)

    with pytest.raises(runtime_env.RuntimeSafetyError, match=message):
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)


def test_g1_command_cell_reader_rejects_duplicate_valid_group_cell():
    read = _command_cell_reader_fixture(duplicate_group=2)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="expected one command cell"):
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)


@pytest.mark.parametrize(
    "fixture_kwargs",
    [{"branch_type_flags": 0}, {"selected_unit_state": 1}],
)
def test_g1_command_cell_reader_fails_closed_when_49b6d0_predicate_is_false(
    fixture_kwargs: dict[str, object],
):
    read = _command_cell_reader_fixture(**fixture_kwargs)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="49B6D0 ineligible") as caught:
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)

    branch = caught.value.branch_evidence
    assert branch["stable"] is True
    assert branch["eligible"] is False
    before = {key: value for key, value in branch["before_pool"].items() if key != "phase"}
    after = {key: value for key, value in branch["after_pool"].items() if key != "phase"}
    assert before == after
    snapshot = caught.value.alternate_snapshot
    assert snapshot["stable"] is True
    assert snapshot["before"]["count"]["raw_value"] == 0
    assert len(snapshot["before"]["records"]["values"]) == 10
    assert len(snapshot["before"]["flags"]["values"]) == 10
    assert snapshot["before"]["geometry"]["fields"] == {
        "base_x": 100, "base_y": 200, "x_pitch": 30, "height": 40,
    }
    assert caught.value.primary_snapshot["stable"] is True
    assert caught.value.primary_snapshot["before"]["blocks"]["A6"]["values"][-1]["raw_value"] == 0


def test_g1_production_click_stays_closed_for_eligible_raw_snapshot():
    read = _command_cell_reader_fixture()
    production_cell = runtime_env._read_g1_command_cell_provenance(
        read, runtime_env.ORIGINAL_SHA256
    )
    calls: list[str] = []

    blocked = runtime_env._g1_production_click_if_authorized(
        production_cell, lambda: calls.append("mouse subprocess")
    )

    assert calls == []
    assert blocked == {
        "status": "BLOCKED",
        "reason": "production click blocked: primary field/action and worker mapping are not approved",
    }


def test_g1_input_geometry_does_not_pre_scale_logical_coordinates():
    geometry = runtime_env._g1_input_geometry((37, 41, 1600, 1200), (2.0, 2.0), 410, 270)

    assert geometry["content"] == [410, 270]
    assert geometry["x11"] == [447, 311]
    assert geometry["scale"] == [2.0, 2.0]


def test_g1_menu_predicate_is_shared_and_requires_changed_capture():
    before = {"ps": 9, "screenshot": {"sha256": "before"}}
    after = {"ps": 7, "screenshot": {"sha256": "after"}}

    assert runtime_env._g1_menu_input_pass(before, after)
    assert not runtime_env._g1_menu_input_pass(
        before, {"ps": 7, "screenshot": {"sha256": "before"}}
    )


def test_g1_scene_snapshot_records_approved_scene_identity():
    memory = {
        runtime_env.G1_MAP_WIDTH_ADDRESS: struct.pack("<2h", 96, 88),
        0x00B42D7C: struct.pack("<2i", 7, 6),
    }

    def read(address: int, size: int) -> bytes:
        value = memory[address]
        assert len(value) == size
        return value

    snapshot = runtime_env._g1_scene_snapshot(
        {
            "tick": 123,
            "players": [
                {"owner": 0, "nation": 1}, {"owner": 1, "nation": 2},
            ],
            "units": [
                {"slot": 1199, "owner": 0, "type": 49, "x": 7, "y": 6},
                {"slot": 1198, "owner": 0, "type": 7, "x": 15, "y": 2},
            ],
        },
        read,
    )

    assert snapshot["owners"]["0"] == {"nation": 1, "active_units": 2}
    assert snapshot["owners"]["1"] == {"nation": 2, "active_units": 0}
    assert snapshot["owner0_hq_world"] is None
    assert snapshot["owner0_hq_candidates"] is None
    assert snapshot["owner0_hq_type"] == {
        "status": "UNKNOWN",
        "observed_owner0_types": [7, 49],
        "reason": "no approved HQ discriminator; type 49 is fixture-specific",
    }
    assert snapshot["world_bounds"]["width"] == 96
    assert snapshot["world_bounds"]["height"] == 88
    assert snapshot["tick"] == 123


def _run_g1_selection_sequence_with_injected_reader(
    tmp_path: Path, failure: str | None = None, direct_failure_call: int | None = None,
):
    run_dir = tmp_path / (failure or "success")
    run_dir.mkdir(parents=True)
    inputs: list[dict[str, object]] = []
    evidence: dict[str, object] = {}
    selection_reads = 0
    camera = [7, 6]
    state_counter = {"tick": 10}
    sent_clicks: list[tuple[int, int]] = []
    sent_drags: list[tuple[int, int, int, int]] = []

    def read_selection() -> dict[str, object]:
        nonlocal selection_reads
        counts = (0, 1, 1, 1, 2, 2)
        selected_count = counts[min(selection_reads, len(counts) - 1)]
        selection_reads += 1
        if direct_failure_call == selection_reads:
            raise OSError("injected direct selection read failure")
        fixture = _command_cell_reader_fixture(
            selected_slot=7,
            selected_count=selected_count,
            unit_active=0 if failure == "snapshot" and selected_count > 0 else 1,
            unit_type=58,
        )
        if failure not in {"oserror", "struct_error"}:
            return runtime_env._read_g1_selection_evidence(fixture)

        identity_address = (
            runtime_env.G1_UNIT_EXISTS_BASE_ADDRESS + 7 * 2
            if selected_count > 0
            else None
        )

        def failing_reader(address: int, size: int) -> bytes:
            if address == identity_address:
                if failure == "oserror":
                    raise OSError("injected selected-unit read failure")
                raise struct.error("injected short selected-unit read")
            return fixture(address, size)

        return runtime_env._read_g1_selection_evidence(failing_reader)

    def runtime_state() -> dict[str, object]:
        state_counter["tick"] += 1
        return {"ps": 3, "tick": state_counter["tick"]}

    def game_state() -> dict[str, object]:
        return {"ps": 3, "tick": state_counter["tick"], "players": []}

    def capture(tag: str) -> dict[str, object]:
        return {"sha256": tag, "dimensions": [1600, 1200]}

    def wait(reader, predicate, message, **kwargs):
        assert kwargs["stage"] in runtime_env.G1_INPUT_STAGE_BUDGETS
        if "minimap" in message:
            camera[:] = [81, 0]
        result = reader(True)
        if predicate(result):
            return result
        raise runtime_env._G1WaitTimeout(
            message, classification="UNKNOWN_SELECTION_OBSERVATION_CORRUPTED",
            last=result, finished_elapsed=1.0, remaining_budget_after=80.0,
            observation=kwargs["wait_observation"],
        )

    def read_production_cell() -> dict[str, object]:
        return runtime_env._read_g1_command_cell_provenance(
            _command_cell_reader_fixture(branch_type_flags=0), runtime_env.ORIGINAL_SHA256,
        )

    def flush() -> None:
        runtime_env._g1_flush_input_stage(run_dir, evidence, inputs)

    try:
        runtime_env._g1_run_input_sequence(
            inputs=inputs, content_crop=(37, 41, 1600, 1200), scale=(2.0, 2.0),
            capture=capture, runtime_state=runtime_state, game_state=game_state,
            read_selection=read_selection, read_camera=lambda: list(camera), wait=wait,
            click=lambda x, y: sent_clicks.append((x, y)),
            drag=lambda x, y, to_x, to_y: sent_drags.append((x, y, to_x, to_y)),
            read_production_cell=read_production_cell, flush=flush,
            started=time.monotonic() - 1.0, timeout=90.0,
        )
    except runtime_env._G1WaitTimeout:
        if failure is None and direct_failure_call is None:
            raise
    flushed = json.loads((run_dir / "evidence.json").read_text(encoding="utf-8"))
    return flushed, sent_clicks, sent_drags


def test_g1_selection_sequence_persists_type_evidence_for_both_runtime_paths(tmp_path: Path):
    baseline, _, _ = _run_g1_selection_sequence_with_injected_reader(tmp_path / "baseline")
    candidate, _, _ = _run_g1_selection_sequence_with_injected_reader(tmp_path / "candidate")

    for flushed in (baseline, candidate):
        by_tag = {item["tag"]: item for item in flushed["inputs"]}
        assert by_tag["unit_select"]["before"]["selection"]["selected_type"] == "UNKNOWN"
        assert by_tag["unit_select"]["before"]["selection"]["selected_slot"] is None
        assert by_tag["unit_select"]["after"]["selection"]["selected_slot"] == 7
        assert by_tag["unit_select"]["after"]["selection"]["selected_type"] == 58
        assert by_tag["drag_select"]["before"]["selection"]["selected_slot"] == 7
        assert by_tag["drag_select"]["before"]["selection"]["selected_type"] == 58
        assert by_tag["drag_select"]["after"]["selection"]["selected_slot"] == 7
        assert by_tag["drag_select"]["after"]["selection"]["selected_type"] == 58

    for tag in ("unit_select", "drag_select"):
        baseline_item = baseline["inputs"][
            [item["tag"] for item in baseline["inputs"]].index(tag)
        ]
        candidate_item = candidate["inputs"][
            [item["tag"] for item in candidate["inputs"]].index(tag)
        ]
        assert baseline_item["result"] == candidate_item["result"] == "PASS"
        assert baseline_item["before"]["selection"] == candidate_item["before"]["selection"]
        assert baseline_item["after"]["selection"] == candidate_item["after"]["selection"]


@pytest.mark.parametrize("failure", ["snapshot", "oserror", "struct_error"])
def test_g1_selection_reader_failures_timeout_closed_with_provenance(
    tmp_path: Path, failure: str,
):
    flushed, sent_clicks, sent_drags = _run_g1_selection_sequence_with_injected_reader(
        tmp_path, failure
    )
    by_tag = {item["tag"]: item for item in flushed["inputs"]}

    after = by_tag["drag_select"]["after"]["last"]
    assert after["selected_slot"] == 7
    assert after["selected_type"] == "UNKNOWN"
    assert after["selected_type_provenance"].startswith(
        ("_CommandCellSnapshotError:", "OSError:", "error:")
    )
    assert [item["tag"] for item in flushed["inputs"]] == [
        "unit_select", "production", "drag_select",
    ]
    assert by_tag["drag_select"]["result"] == "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED"
    assert by_tag["drag_select"]["timeout_cause"] == "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED"
    assert sent_drags == [(350, 180, 550, 350)]
    assert sent_clicks == [(410, 270)]


@pytest.mark.parametrize(
    ("direct_failure_call", "expected_tag", "expected_point", "expected_clicks", "expected_drags"),
    [
        (1, "unit_select", "before_click", [], []),
        (4, "drag_select", "before_drag", [(410, 270)], []),
        (6, "drag_select", "after_drag", [(410, 270)], [(350, 180, 550, 350)]),
        (7, "minimap", "before_minimap", [(410, 270)], [(350, 180, 550, 350)]),
        (8, "minimap", "after_minimap", [(410, 270), (150, 520)], [(350, 180, 550, 350)]),
    ],
)
def test_g1_direct_selection_reader_failure_is_stage_diagnosed(
    tmp_path: Path, direct_failure_call: int, expected_tag: str, expected_point: str,
    expected_clicks: list[tuple[int, int]], expected_drags: list[tuple[int, int, int, int]],
):
    flushed, sent_clicks, sent_drags = _run_g1_selection_sequence_with_injected_reader(
        tmp_path, direct_failure_call=direct_failure_call,
    )
    by_tag = {item["tag"]: item for item in flushed["inputs"]}
    failed = by_tag[expected_tag]
    observation = failed["wait_observation"]

    assert failed["result"] == "UNKNOWN_STATE_READ_FAILURE"
    assert failed["timeout_cause"] == "UNKNOWN_STATE_READ_FAILURE"
    assert observation["direct_reader"] == "selection"
    assert observation["direct_reader_failure"] is True
    assert observation["direct_read_point"] == expected_point
    assert observation["direct_read_attempt_count"] == 1
    assert observation["direct_read_error_count"] == 1
    assert observation["poll_count"] == 0
    assert observation["poll_attempt_count"] == 0
    assert observation["first_read_error_provenance"] == (
        "OSError: injected direct selection read failure"
    )
    assert observation["last_read_error_provenance"] == observation[
        "first_read_error_provenance"
    ]
    assert failed["predicate_observed"] is False
    assert sent_clicks == expected_clicks
    assert sent_drags == expected_drags


def test_g1_direct_selection_reader_failure_precedes_exhausted_run_budget(
    monkeypatch: pytest.MonkeyPatch,
):
    """A direct read failure remains the specific UNKNOWN at the deadline."""

    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: 10.0)

    def unreadable() -> dict[str, object]:
        raise OSError("injected direct selection read failure")

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._g1_read_selection_stage(
            unreadable,
            stage="unit_select",
            read_point="before_click",
            started=0.0,
            timeout=10.0,
            stage_started=0.0,
        )

    observation = caught.value.observation
    assert caught.value.classification == "UNKNOWN_STATE_READ_FAILURE"
    assert caught.value.classification != "UNKNOWN_BUDGET_EXHAUSTED"
    assert caught.value.finished_elapsed == 10.0
    assert caught.value.remaining_budget_after == 0.0
    assert observation["finished_elapsed"] == 10.0
    assert observation["remaining_budget_after"] == 0.0
    assert observation["stage_budget_exhausted"] is True
    assert observation["run_budget_exhausted"] is True
    assert observation["direct_reader_failure"] is True


@pytest.mark.parametrize(
    (
        "stage", "stage_started", "finished", "expected_stage_budget",
        "expected_exhausted", "expected_stage_budget_state",
    ),
    [
        ("unit_select", 0.0, 9.999, 10.0, False, "WITHIN_STAGE_BUDGET"),
        ("unit_select", 0.0, 10.0, 10.0, True, "STAGE_BUDGET_EXHAUSTED"),
        ("unit_select", None, 10.0, 10.0, False, "STAGE_START_UNKNOWN"),
        ("production", 0.0, 10.0, None, False, "STAGE_BUDGET_UNAVAILABLE"),
    ],
)
def test_g1_direct_selection_reader_stage_budget_exhaustion_is_semantic(
    monkeypatch: pytest.MonkeyPatch,
    stage: str,
    stage_started: float | None,
    finished: float,
    expected_stage_budget: float | None,
    expected_exhausted: bool,
    expected_stage_budget_state: str,
):
    """The direct-reader provenance must distinguish all budget states."""

    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: finished)

    def unreadable() -> dict[str, object]:
        raise OSError("injected direct selection read failure")

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._g1_read_selection_stage(
            unreadable,
            stage=stage,
            read_point="before_click",
            started=0.0,
            timeout=10.0,
            stage_started=stage_started,
        )

    observation = caught.value.observation
    assert caught.value.classification == "UNKNOWN_STATE_READ_FAILURE"
    assert observation["stage_budget"] == expected_stage_budget
    assert observation["stage_budget_exhausted"] is expected_exhausted
    assert observation["stage_budget_state"] == expected_stage_budget_state
    assert observation["run_budget_exhausted"] is (finished >= 10.0)


def test_g1_production_direct_selection_reader_failure_stays_blocked_and_continues(
    tmp_path: Path,
):
    flushed, sent_clicks, sent_drags = _run_g1_selection_sequence_with_injected_reader(
        tmp_path, direct_failure_call=3,
    )
    by_tag = {item["tag"]: item for item in flushed["inputs"]}
    production = by_tag["production"]

    assert production["result"] == "BLOCKED"
    assert production["waited"] is False
    failure = production["selection_read_failure"]
    assert failure["direct_read_point"] == "before_production"
    assert failure["direct_reader_failure"] is True
    # R27: this is the production call shape (no configured stage budget and
    # no stage_started argument).  An unavailable budget outranks an unknown
    # stage start so a priority-reorder mutation cannot relabel this failure.
    assert failure["stage_budget"] is None
    assert failure["stage_started_elapsed"] is None
    assert failure["stage_budget_state"] == "STAGE_BUDGET_UNAVAILABLE"
    assert [item["tag"] for item in flushed["inputs"]] == [
        "unit_select", "production", "drag_select", "minimap",
    ]
    assert sent_clicks == [(410, 270), (150, 520)]
    assert sent_drags == [(350, 180, 550, 350)]


def test_g1_production_selection_snapshots_mark_direct_read_failure_unavailable(
    tmp_path: Path,
):
    flushed, _, _ = _run_g1_selection_sequence_with_injected_reader(
        tmp_path, direct_failure_call=3,
    )
    production = next(item for item in flushed["inputs"] if item["tag"] == "production")

    for point in ("before", "after"):
        selection = production[point]["selection"]
        assert selection["status"] == "UNAVAILABLE"
        assert selection["count"] is None
        assert selection["read_failure"] is True


def test_g1_production_selection_snapshot_has_no_failure_marker_on_success(
    tmp_path: Path,
):
    flushed, _, _ = _run_g1_selection_sequence_with_injected_reader(tmp_path)
    production = next(item for item in flushed["inputs"] if item["tag"] == "production")

    for point in ("before", "after"):
        assert "read_failure" not in production[point]["selection"]


def test_g1_selection_sequence_keeps_wait_predicates_and_budgets_fixed():
    assert runtime_env.G1_INPUT_STAGE_BUDGETS == {
        "unit_select": 10.0, "drag_select": 10.0, "minimap": 10.0,
    }
    assert runtime_env.G1_INPUT_STAGE_BUDGET_TOTAL == 30.0
    assert runtime_env.G1_INPUT_PHASE_WALL_CLOCK_BUDGET == 31.5
    source = inspect.getsource(runtime_env._g1_run_input_sequence)
    assert 'int(item.get("count", 0)) >= 1' in source
    assert 'diagnostics=drag_wait_observation' in source
    assert 'int(item.get("count", 0)) >= 2' not in source


def test_g1_selection_response_accepts_count_or_identity_change_only():
    before = {"count": 1, "selected_slot": 1199, "selected_type": 70}

    assert runtime_env._g1_selection_responded(
        before, {"count": 2, "selected_slot": 1199, "selected_type": 70}
    )
    assert runtime_env._g1_selection_responded(
        before, {"count": 1, "selected_slot": 1198, "selected_type": 21}
    )
    # R6-B-R2 remains undecided: preserve the existing count 1 -> 0 response
    # semantics while R6-B-R3 rejects only impossible negative counts.
    assert runtime_env._g1_selection_responded(
        before, {"count": 0, "selected_slot": None, "selected_type": "UNKNOWN"}
    )
    assert not runtime_env._g1_selection_responded(
        before, {"count": 1, "selected_slot": 1199, "selected_type": 70}
    )


@pytest.mark.parametrize(
    ("before", "after"),
    [
        (
            {"count": 1, "selected_slot": 1199, "selected_type": 70},
            {"count": 1, "selected_slot": 1198, "selected_type": "UNKNOWN",
             "selected_type_provenance": "OSError: selected-unit read failed"},
        ),
        (
            {"count": 1, "selected_slot": 1199, "selected_type": 70},
            {"count": 1, "selected_slot": 1199, "selected_type": "UNKNOWN",
             "selected_type_provenance": "selected unit slot is not active"},
        ),
        (
            {"count": 1, "selected_slot": 1199, "selected_type": "UNKNOWN",
             "selected_type_provenance": "baseline read failed"},
            {"count": 1, "selected_slot": 1198, "selected_type": 21},
        ),
    ],
)
def test_g1_selection_response_rejects_corrupted_observations(
    before: dict[str, object], after: dict[str, object],
):
    diagnostics: dict[str, object] = {}

    assert not runtime_env._g1_selection_responded(
        before, after, diagnostics=diagnostics,
    )
    assert diagnostics["selection_observation"]["status"] == "CORRUPTED"


@pytest.mark.parametrize("case", ["c4_read_failure", "c5_inactive_slot", "c7_recovery", "d1_negative_count"])
def test_g1_selection_response_rejects_reader_generated_corruption(case: str):
    def evidence(*, selected_count: int = 1, unit_active: int = 1, read_failure: bool = False):
        fixture = _command_cell_reader_fixture(
            selected_slot=7,
            selected_count=selected_count,
            unit_active=unit_active,
            unit_type=58,
        )
        if not read_failure:
            return runtime_env._read_g1_selection_evidence(fixture)

        identity_address = runtime_env.G1_UNIT_EXISTS_BASE_ADDRESS + 7 * 2

        def failing_reader(address: int, size: int) -> bytes:
            if address == identity_address:
                raise OSError("injected selected-unit read failure")
            return fixture(address, size)

        return runtime_env._read_g1_selection_evidence(failing_reader)

    if case == "c4_read_failure":
        before = evidence()
        after = evidence(read_failure=True)
    elif case == "c5_inactive_slot":
        before = evidence()
        after = evidence(unit_active=0)
    elif case == "c7_recovery":
        before = evidence(unit_active=0)
        after = evidence()
    else:
        before = evidence()
        after = evidence(selected_count=-1)

    diagnostics: dict[str, object] = {}
    assert not runtime_env._g1_selection_responded(
        before, after, diagnostics=diagnostics,
    )
    assert diagnostics["selection_observation"]["status"] == "CORRUPTED"

    if case == "c4_read_failure":
        assert after["selected_type"] == "UNKNOWN"
        assert after["selected_type_provenance"].startswith("OSError:")
    elif case == "c5_inactive_slot":
        assert after["selected_type"] == "UNKNOWN"
        assert after["selected_type_provenance"].startswith("_CommandCellSnapshotError:")
    elif case == "c7_recovery":
        assert before["selected_type"] == "UNKNOWN"
        assert before["selected_type_provenance"].startswith("_CommandCellSnapshotError:")
        assert after["selected_type"] == 58
    else:
        assert after["count"] == -1
        assert after["selected_slot"] is None
        assert after["selected_type"] == "UNKNOWN"
        assert after["selected_type_provenance"].startswith("_CommandCellSnapshotError:")


@pytest.mark.parametrize(
    ("before", "after"),
    [
        (
            {"count": 1, "selected_slot": 1199, "selected_type": 70},
            {"count": -1, "selected_slot": None, "selected_type": "UNKNOWN",
             "selected_type_provenance": "unsupported selected-unit count"},
        ),
        (
            {"count": -1, "selected_slot": None, "selected_type": "UNKNOWN",
             "selected_type_provenance": "unsupported selected-unit count"},
            {"count": 1, "selected_slot": 1198, "selected_type": 21},
        ),
    ],
)
def test_g1_selection_response_rejects_negative_count_observations(
    before: dict[str, object], after: dict[str, object],
):
    diagnostics: dict[str, object] = {}

    assert not runtime_env._g1_selection_responded(
        before, after, diagnostics=diagnostics,
    )
    assert diagnostics["selection_observation"]["status"] == "CORRUPTED"


def test_g1_selection_response_timeout_preserves_corruption_provenance(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep",
        lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )
    before = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    after = {
        "count": 1, "selected_slot": 1198, "selected_type": "UNKNOWN",
        "selected_type_provenance": "OSError: selected-unit read failed",
    }
    wait_observation: dict[str, object] = {}

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: after,
            lambda item: runtime_env._g1_selection_responded(
                before, item, diagnostics=wait_observation,
            ),
            started=0.0, timeout=10.0, message="drag response was not observed",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
            wait_observation=wait_observation,
        )

    assert caught.value.classification == "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED"
    assert caught.value.observation["selection_observation"]["after"][
        "selected_type_provenance"
    ].startswith("OSError:")


def test_g1_selection_response_final_sound_observation_clears_stale_corruption():
    before = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    corrupted = {
        "count": 1, "selected_slot": 1198, "selected_type": "UNKNOWN",
        "selected_type_provenance": "OSError: transient selected-unit read failure",
    }
    unchanged = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    diagnostics: dict[str, object] = {}

    assert not runtime_env._g1_selection_responded(
        before, corrupted, diagnostics=diagnostics,
    )
    first = diagnostics["selection_observation"]
    assert first["status"] == "CORRUPTED"
    assert first["corrupted_poll_count"] == 1
    assert first["first_corruption_provenance"] == first["last_corruption_provenance"]

    assert not runtime_env._g1_selection_responded(
        before, unchanged, diagnostics=diagnostics,
    )
    final = diagnostics["selection_observation"]
    assert final["status"] == "SOUND"
    assert final["before"] == before
    assert final["after"] == unchanged
    assert final["corrupted_poll_count"] == 1
    assert final["first_corruption_provenance"]["after"][
        "selected_type_provenance"
    ].startswith("OSError:")
    assert final["last_corruption_provenance"] == final["first_corruption_provenance"]


def test_g1_selection_response_wait_uses_final_sound_status_for_no_effect(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep",
        lambda seconds: clock.__setitem__(0, clock[0] + seconds),
    )
    before = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    negative = {
        "count": -1, "selected_slot": None, "selected_type": "UNKNOWN",
        "selected_type_provenance": "unsupported selected-unit count",
    }
    unchanged = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    polls = iter([negative])
    wait_observation: dict[str, object] = {}

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: next(polls, unchanged),
            lambda item: runtime_env._g1_selection_responded(
                before, item, diagnostics=wait_observation,
            ),
            started=0.0, timeout=10.0, message="selection did not change",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
            wait_observation=wait_observation,
        )

    assert caught.value.classification == "FAIL_NO_EFFECT"
    selection_observation = caught.value.observation["selection_observation"]
    assert selection_observation["status"] == "SOUND"
    assert selection_observation["corrupted_poll_count"] == 1
    assert selection_observation["first_corruption_provenance"]["after"][
        "count"
    ] == -1


def test_g1_shared_input_sequence_blocks_production_but_reaches_later_stages():
    inputs: list[dict[str, object]] = []
    flushes: list[list[str]] = []
    selection = {"count": 0, "first_slot": -1}
    camera = [7, 6]
    state_counter = {"tick": 10}
    waits: list[str] = []

    def capture(tag: str) -> dict[str, object]:
        return {"sha256": tag, "dimensions": [1600, 1200]}

    def runtime_state() -> dict[str, object]:
        state_counter["tick"] += 1
        return {"ps": 3, "tick": state_counter["tick"]}

    def game_state() -> dict[str, object]:
        return {"ps": 3, "tick": state_counter["tick"], "players": []}

    def wait(reader, predicate, message, **kwargs):
        assert kwargs["stage"] in runtime_env.G1_INPUT_STAGE_BUDGETS
        assert kwargs["stage_budget"] == 10.0
        waits.append(message)
        kwargs["wait_observation"].update({
            "poll_count": 1, "poll_attempt_count": 1, "read_error_count": 0,
            "successful_poll_ratio": 1.0, "read_error_ratio": 0.0,
            "read_error_coverage_threshold_ratio": 0.25,
            "read_error_coverage_exceeds_threshold": False,
            "first_read_error_provenance": None, "last_read_error_provenance": None,
        })
        if "selection" in message and "drag" not in message:
            selection.update(count=1, first_slot=7, selected_slot=1199, selected_type=70)
        elif "drag" in message:
            selection.update(count=1, first_slot=7, selected_slot=1198, selected_type=21)
        else:
            camera[:] = [81, 0]
        result = reader(True)
        assert predicate(result)
        return result

    sent_clicks: list[tuple[int, int]] = []
    sent_drags: list[tuple[int, int, int, int]] = []
    phase_metrics: dict[str, object] = {"items": {}}

    def read_production_cell() -> dict[str, object]:
        return runtime_env._read_g1_command_cell_provenance(
            _command_cell_reader_fixture(branch_type_flags=0), runtime_env.ORIGINAL_SHA256,
        )

    result = runtime_env._g1_run_input_sequence(
        inputs=inputs, content_crop=(37, 41, 1600, 1200), scale=(2.0, 2.0),
        capture=capture, runtime_state=runtime_state, game_state=game_state,
        read_selection=lambda: dict(selection), read_camera=lambda: list(camera), wait=wait,
        click=lambda x, y: sent_clicks.append((x, y)),
        drag=lambda x, y, to_x, to_y: sent_drags.append((x, y, to_x, to_y)),
        read_production_cell=read_production_cell,
        flush=lambda: flushes.append([str(item["tag"]) for item in inputs]),
        started=time.monotonic() - 1.0, timeout=90.0,
        phase_metrics=phase_metrics,
    )

    assert [item["tag"] for item in inputs] == [
        "unit_select", "production", "drag_select", "minimap",
    ]
    assert inputs[1]["result"] == "BLOCKED"
    assert inputs[1]["waited"] is False
    assert inputs[1]["provenance_error"].startswith("_CommandCellSnapshotError:")
    assert inputs[1]["command_branch"]["stable"] is True
    assert inputs[1]["command_branch"]["eligible"] is False
    assert inputs[1]["alternate_ui_snapshot"] is not None
    assert inputs[1]["primary_command_table"] is not None
    assert waits == [
        "owner0 HQ selection did not change 0->>=1",
        "owner0 HQ/worker drag did not produce a selection-state response",
        "fixed minimap click did not change camera",
    ]
    assert result["camera_after_minimap"] == [81, 0]
    assert flushes[-1] == ["unit_select", "production", "drag_select", "minimap"]
    assert sent_clicks == [(410, 270), (150, 520)]
    assert sent_drags == [(350, 180, 550, 350)]
    assert inputs[2]["before"]["selection"]["count"] == 1
    assert inputs[2]["after"]["selection"]["count"] == 1
    assert inputs[2]["before"]["selection"] != inputs[2]["after"]["selection"]
    assert (670, 490) not in sent_clicks
    assert inputs[0]["x11"] == [447, 311]
    assert inputs[2]["x11"] == [387, 221]
    assert inputs[2]["before"]["drag_to"]["x11"] == [587, 391]
    assert inputs[3]["x11"] == [187, 561]
    assert all(inputs[index]["entered_elapsed"] >= 0 for index in (0, 2, 3))
    assert all(inputs[index]["predicate_observed"] is True for index in (0, 2, 3))
    assert all(inputs[index]["remaining_budget_after"] <= 90.0 for index in (0, 2, 3))
    assert all("read_coverage" in inputs[index] for index in (0, 2, 3))
    input_checks = runtime_env._g1_input_verdict(inputs, enabled=True)
    assert set(input_checks["read_coverage"]) == {"unit_select", "drag_select", "minimap"}
    assert set(phase_metrics["items"]) == {
        "capture:selection_after", "capture:production_before", "capture:drag_after",
        "capture:minimap_after", "production_provenance",
    }
    assert phase_metrics["items"]["production_provenance"]["status"] == "ERROR"


def test_g1_input_verdict_blocks_both_paths_when_production_is_blocked():
    inputs = [
        {"tag": tag, "result": "BLOCKED" if tag == "production" else "PASS"}
        for tag in runtime_env.G1_REQUIRED_INPUT_TAGS
    ]

    baseline_checks = runtime_env._g1_input_verdict(inputs, enabled=True)
    baseline = runtime_env._g1_baseline_verdict(
        error=None,
        checks={"required_inputs": baseline_checks["required_inputs"]},
        input_checks=baseline_checks,
        cleanup={"ok": True},
    )
    candidate = runtime_env._g1_presentation_verdict(
        error=None, cleanup={"ok": True}, validator={"status": "PASS"},
        inputs=inputs, input_sequence=True,
    )

    assert baseline_checks["required_inputs"] is False
    assert baseline_checks["production_blocked"] is True
    assert baseline["overall"] != "PASS"
    assert candidate["checks"]["required_inputs"] is False
    assert candidate["overall"] != "PASS"
    assert candidate["production"]["blocked"] is True
    assert candidate["teardown"]["cleanup_ok"] is True


def test_g1_input_verdict_accepts_all_five_passed_inputs():
    inputs = [{"tag": tag, "result": "PASS"} for tag in runtime_env.G1_REQUIRED_INPUT_TAGS]

    checks = runtime_env._g1_input_verdict(inputs, enabled=True)
    verdict = runtime_env._g1_presentation_verdict(
        error=None, cleanup={"ok": True}, validator={"status": "PASS"},
        inputs=inputs, input_sequence=True,
    )

    assert checks["required_inputs"] is True
    assert verdict["overall"] == "PASS"
    assert verdict["input_observations"] == {tag: ["PASS"] for tag in runtime_env.G1_REQUIRED_INPUT_TAGS}


def test_g1_input_verdict_off_mode_does_not_block_existing_verdict():
    inputs = [
        {"tag": tag, "result": "BLOCKED" if tag == "production" else "PASS"}
        for tag in runtime_env.G1_REQUIRED_INPUT_TAGS
    ]

    checks = runtime_env._g1_input_verdict(inputs, enabled=False)
    baseline = runtime_env._g1_baseline_verdict(
        error=None,
        checks={"original_hash": True, "required_inputs": checks["required_inputs"]},
        input_checks=checks,
        cleanup={"ok": True},
    )
    candidate = runtime_env._g1_presentation_verdict(
        error=None, cleanup={"ok": True}, validator={"status": "PASS"},
        inputs=inputs, input_sequence=False,
    )

    assert checks["required_inputs"] is True
    assert checks["production_blocked"] is True
    assert baseline["overall"] == "PASS"
    assert candidate["checks"]["required_inputs"] is True
    assert candidate["overall"] == "PASS"
    assert candidate["production"]["blocked"] is True


def test_g1_production_click_stays_closed_when_ineligible_snapshot_fails():
    read = _command_cell_reader_fixture(branch_type_flags=0)
    calls: list[str] = []

    with pytest.raises(runtime_env.RuntimeSafetyError, match="49B6D0 ineligible") as caught:
        production_cell = runtime_env._read_g1_command_cell_provenance(
            read, runtime_env.ORIGINAL_SHA256
        )
        runtime_env._g1_production_click_if_authorized(
            production_cell, lambda: calls.append("mouse subprocess")
        )

    assert calls == []
    assert caught.value.primary_snapshot["stable"] is True


def test_g1_command_cell_error_record_keeps_primary_snapshot_in_output_evidence():
    read = _command_cell_reader_fixture(branch_type_flags=0)
    with pytest.raises(runtime_env.RuntimeSafetyError) as caught:
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)

    evidence: dict[str, object] = {}
    runtime_env._record_g1_command_cell_error(evidence, caught.value)

    assert evidence["primary_command_table"] == caught.value.primary_snapshot
    assert evidence["command_branch"] == caught.value.branch_evidence
    assert evidence["alternate_ui_snapshot"] == caught.value.alternate_snapshot


@pytest.mark.parametrize("block_index", range(4))
def test_g1_primary_command_table_preserves_each_raw_block_without_field_meaning(block_index: int):
    values = [
        tuple(0 for _ in range(runtime_env.G1_PRIMARY_COMMAND_TABLE_WORD_COUNT))
        for _ in runtime_env.G1_PRIMARY_COMMAND_TABLE_BLOCKS
    ]
    values[block_index] = tuple(index + 1 for index in range(runtime_env.G1_PRIMARY_COMMAND_TABLE_WORD_COUNT))
    read = _command_cell_reader_fixture(primary_values=tuple(values))

    evidence = runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)
    block_name = runtime_env.G1_PRIMARY_COMMAND_TABLE_BLOCKS[block_index][0]
    assert evidence["primary_command_table"]["before"]["blocks"][block_name]["values"][-1]["raw_value"] == 12


def test_g1_alternate_ui_snapshot_preserves_nonzero_raw_values_and_bounds():
    records = tuple((index + 1, 0x100 + index) for index in range(10))
    flags = tuple(0x200 + index for index in range(10))
    read = _command_cell_reader_fixture(
        branch_type_flags=0,
        alternate_count=3,
        alternate_records=records,
        alternate_flags=flags,
        alternate_geometry=(640, 480, 70, 22),
    )

    with pytest.raises(runtime_env.RuntimeSafetyError, match="49B6D0 ineligible") as caught:
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)

    snapshot = caught.value.alternate_snapshot["before"]
    assert snapshot["count"]["address"] == "0x0066F1B6"
    assert snapshot["count"]["raw_value"] == 3
    assert snapshot["records"]["values"][0]["raw_words"] == [1, 0x100]
    assert snapshot["records"]["values"][-1]["raw_words"] == [10, 0x109]
    assert snapshot["flags"]["values"][0]["raw_value"] == 0x200
    assert snapshot["flags"]["values"][-1]["raw_value"] == 0x209
    assert snapshot["geometry"]["fields"] == {
        "base_x": 640, "base_y": 480, "x_pitch": 70, "height": 22,
    }

    out_of_bounds = _command_cell_reader_fixture(branch_type_flags=0, alternate_count=11)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="count is out of bounds") as bounded:
        runtime_env._read_g1_command_cell_provenance(
            out_of_bounds, runtime_env.ORIGINAL_SHA256
        )
    assert bounded.value.alternate_snapshot["count"]["raw_value"] == 11


def test_g1_alternate_ui_snapshot_rejects_value_change_between_coherence_brackets():
    before = _command_cell_reader_fixture(
        branch_type_flags=0,
        alternate_count=1,
        alternate_records=((1, 2),) + ((0, 0),) * 9,
    )
    after = _command_cell_reader_fixture(
        branch_type_flags=0,
        alternate_count=1,
        alternate_records=((1, 3),) + ((0, 0),) * 9,
    )
    after_pool = False

    def read(address: int, size: int) -> bytes:
        nonlocal after_pool
        fixture = after if after_pool else before
        raw = fixture(address, size)
        if address == runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START:
            after_pool = True
        return raw

    with pytest.raises(runtime_env.RuntimeSafetyError, match="alternate UI snapshot changed") as caught:
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)

    branch = caught.value.branch_evidence
    assert branch["stable"] is True
    assert branch["eligible"] is False
    assert branch["alternate_ui_stable"] is False
    assert caught.value.alternate_snapshot["before"]["records"]["values"][0]["raw_words"] == [1, 2]
    assert caught.value.alternate_snapshot["after"]["records"]["values"][0]["raw_words"] == [1, 3]


def test_g1_command_cell_reader_preserves_49b6d0_predicate_change_diagnostic():
    fixture = _command_cell_reader_fixture()
    branch_type_address = (
        runtime_env.G1_COMMAND_BRANCH_TYPE_FLAGS_BASE_ADDRESS
        + 58 * runtime_env.G1_COMMAND_BRANCH_TYPE_FLAGS_STRIDE
    )
    branch_reads = 0

    def read(address: int, size: int) -> bytes:
        nonlocal branch_reads
        if address == branch_type_address:
            branch_reads += 1
            if branch_reads == 2:
                return b"\x00"
        return fixture(address, size)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="49B6D0 predicate changed") as caught:
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)

    branch = caught.value.branch_evidence
    assert branch["stable"] is False
    assert branch["before_pool"]["type_predicate"]["raw_value"] == 0x08
    assert branch["after_pool"]["type_predicate"]["raw_value"] == 0


def test_g1_command_cell_reader_rejects_selection_identity_change_with_before_after_evidence():
    before = _command_cell_reader_fixture()
    after = _command_cell_reader_fixture(
        selected_count=2,
        selected_slot=8,
        unit_active=2,
        unit_type=59,
        primary_values=(
            (1,) + (0,) * 11,
            (0,) * 12,
            (0,) * 12,
            (0,) * 12,
        ),
    )
    calls: list[tuple[int, int]] = []
    after_pool = False

    def read(address: int, size: int) -> bytes:
        nonlocal after_pool
        calls.append((address, size))
        fixture = after if after_pool else before
        raw = fixture(address, size)
        if address == runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START:
            after_pool = True
        return raw

    with pytest.raises(runtime_env.RuntimeSafetyError, match="selection identity changed") as caught:
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)

    branch = caught.value.branch_evidence
    assert branch["selection_identity_stable"] is False
    assert branch["stable"] is False
    assert branch["before_pool"]["selection"] == {"count": 1, "first_slot": 7}
    assert branch["after_pool"]["selection"] == {"count": 2, "first_slot": 8}
    assert branch["before_pool"]["unit"]["active"] == 1
    assert branch["after_pool"]["unit"]["active"] == 2
    assert branch["before_pool"]["unit"]["type"] == 58
    assert branch["after_pool"]["unit"]["type"] == 59
    assert [entry["group"] for entry in caught.value.raw_summary] == [2, 3, 4, 5]
    assert caught.value.primary_snapshot["stable"] is False
    assert caught.value.primary_snapshot["before"]["blocks"]["A6"]["values"][0]["raw_value"] == 0
    assert caught.value.primary_snapshot["after"]["blocks"]["A6"]["values"][0]["raw_value"] == 1
    assert calls.count((runtime_env.G1_SELECTION_COUNT_ADDRESS, 4)) == 2
    assert calls.count((runtime_env.G1_SELECTION_FIRST_SLOT_ADDRESS, 2)) == 2
    assert calls.count((runtime_env.G1_UNIT_EXISTS_BASE_ADDRESS + 7 * 2, 2)) == 1
    assert calls.count((runtime_env.G1_UNIT_EXISTS_BASE_ADDRESS + 8 * 2, 2)) == 1


def test_g1_command_cell_reader_does_not_poll_stable_ineligible_branch():
    fixture = _command_cell_reader_fixture(branch_type_flags=0)
    pool_reads = 0

    def read(address: int, size: int) -> bytes:
        nonlocal pool_reads
        if address == runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START:
            pool_reads += 1
        return fixture(address, size)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="49B6D0 ineligible"):
        runtime_env._read_g1_command_cell_provenance(
            read,
            runtime_env.ORIGINAL_SHA256,
            started=time.monotonic(),
            timeout=0.2,
            poll_interval=0.001,
        )

    assert pool_reads == 1


def test_g1_command_cell_reader_rejects_stable_multi_selection_before_primary_read():
    fixture = _command_cell_reader_fixture(selected_count=2)
    calls: list[tuple[int, int]] = []

    def read(address: int, size: int) -> bytes:
        calls.append((address, size))
        return fixture(address, size)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="exactly one selected unit") as caught:
        runtime_env._read_g1_command_cell_provenance(
            read,
            runtime_env.ORIGINAL_SHA256,
            started=time.monotonic(),
            timeout=0.2,
            poll_interval=0.001,
        )

    guard = caught.value.branch_evidence["selection_count_guard"]
    assert guard == {
        "required": 1,
        "observed": 2,
        "before": {"count": 2},
        "primary_read": False,
    }
    assert (runtime_env.G1_PRIMARY_COMMAND_TABLE_BASE_ADDRESS,
            runtime_env.G1_PRIMARY_COMMAND_TABLE_READ_SIZE) not in calls


@pytest.mark.parametrize("selected_count", [0, 2])
def test_g1_command_cell_reader_records_any_non_single_count_before_detail_or_primary_read(
    selected_count: int,
):
    fixture = _command_cell_reader_fixture(selected_count=selected_count)
    calls: list[tuple[int, int]] = []

    def read(address: int, size: int) -> bytes:
        calls.append((address, size))
        return fixture(address, size)

    with pytest.raises(runtime_env.RuntimeSafetyError, match="exactly one selected unit") as caught:
        runtime_env._read_g1_command_cell_provenance(
            read,
            runtime_env.ORIGINAL_SHA256,
            started=time.monotonic(),
            timeout=0.2,
            poll_interval=0.001,
        )

    guard = caught.value.branch_evidence["selection_count_guard"]
    assert guard == {
        "required": 1,
        "observed": selected_count,
        "before": {"count": selected_count},
        "primary_read": False,
    }
    assert calls == [(runtime_env.G1_SELECTION_COUNT_ADDRESS, 4)]


def test_g1_command_cell_reader_preserves_primary_snapshot_on_raw_change():
    before = _command_cell_reader_fixture()
    after = _command_cell_reader_fixture(
        primary_values=(
            (0,) * 12,
            (0,) * 12,
            (0,) * 12,
            (0,) * 11 + (9,),
        )
    )
    after_pool = False

    def read(address: int, size: int) -> bytes:
        nonlocal after_pool
        fixture = after if after_pool else before
        raw = fixture(address, size)
        if address == runtime_env.G1_COMMAND_CELL_POOL_ALLOCATOR_START:
            after_pool = True
        return raw

    with pytest.raises(runtime_env.RuntimeSafetyError, match="primary command-table snapshot changed") as caught:
        runtime_env._read_g1_command_cell_provenance(read, runtime_env.ORIGINAL_SHA256)

    snapshot = caught.value.primary_snapshot
    assert snapshot["stable"] is False
    assert snapshot["before"]["blocks"]["EE"]["values"][-1]["raw_value"] == 0
    assert snapshot["after"]["blocks"]["EE"]["values"][-1]["raw_value"] == 9


def _capture(sha: str) -> dict[str, object]:
    return {"sha256": sha, "cursor_content": list(runtime_env.G1_NEUTRAL_POINT)}


@pytest.mark.parametrize(
    ("initial", "expected_clicks"),
    [("multiplayer", ["solo_mode"]), ("solo", ["multiplayer_mode", "solo_mode"])],
)
def test_g1_selector_flow_covers_both_initial_branches(
    initial: str, expected_clicks: list[str]
):
    observed_clicks: list[str] = []
    mode = initial

    def selector(name: str) -> dict[str, object]:
        return {
            "multiplayer": int(name == "multiplayer"),
            "solo": int(name == "solo"),
            "selected": name,
        }

    def read_state() -> dict[str, int]:
        return {"ps": 7, "selector": selector(mode)}  # type: ignore[return-value]

    def wait_for(predicate, _message: str) -> dict[str, int]:
        state = read_state()
        assert predicate(state)
        return state

    def click(tag: str, _point: tuple[int, int]) -> None:
        nonlocal mode
        observed_clicks.append(tag)
        if tag == "multiplayer_mode":
            mode = "multiplayer"
        elif tag == "solo_mode":
            mode = "solo"

    captures = []
    records: list[dict[str, object]] = []
    flushes: list[list[str]] = []

    def capture(tag: str) -> dict[str, object]:
        captures.append(tag)
        return _capture(tag)

    def record(tag: str, x: int, y: int, before: object, expected: str,
               after: object, actual: str, result: str) -> dict[str, object]:
        return runtime_env._g1_record_selector_input(
            records,
            tag=tag,
            x=x,
            y=y,
            content_crop=(37, 41, 800, 600),
            scale=(1.0, 1.0),
            before=before,
            expected=expected,
            after=after,
            actual=actual,
            result=result,
            flush=lambda: flushes.append([str(item["tag"]) for item in records]),
        )

    runtime_env._g1_selector_flow(
        read_state, wait_for, click, capture, record
    )

    assert observed_clicks == expected_clicks
    assert mode == "solo"
    assert captures == (
        ["lobby_selector_before", "multiplayer_mode_normalized", "solo_mode_selected"]
        if initial == "solo" else ["lobby_selector_before", "solo_mode_selected"]
    )
    assert records[-1]["tag"] == "solo_mode_setup"
    assert records[-1]["result"] == "PASS"
    expected_tags = (
        ["multiplayer_mode_normalize", "solo_mode_setup"]
        if initial == "solo" else ["multiplayer_mode_normalize", "solo_mode_setup"]
    )
    assert [item["tag"] for item in records] == expected_tags
    assert len({item["tag"] for item in records}) == len(records)
    assert len(flushes) == len(records)


def test_g1_selector_flow_rejects_missing_required_zero_to_one_transition():
    assert not runtime_env._g1_selector_pass(
        "solo", "solo", "solo", 7, _capture("before"), _capture("after")
    )
    assert not runtime_env._g1_selector_pass(
        "multiplayer", None, "multiplayer", 7, _capture("before"), _capture("after")
    )
    assert not runtime_env._g1_selector_pass(
        "multiplayer", None, "solo", 7,
        _capture("before"), {"sha256": "after", "cursor_content": [0, 0]},
    )


def test_g1_selector_input_recorder_writes_tagged_schema_and_flushes():
    inputs: list[dict[str, object]] = []
    flushes: list[list[str]] = []

    entry = runtime_env._g1_record_selector_input(
        inputs,
        tag="solo_mode_setup",
        x=300,
        y=220,
        content_crop=(37, 41, 1600, 1200),
        scale=(2.0, 2.0),
        before={"ps": 7},
        expected="solo selector becomes active",
        after={"ps": 7},
        actual="PS7->PS7",
        result="PASS",
        flush=lambda: flushes.append([str(item["tag"]) for item in inputs]),
    )

    assert entry["tag"] == "solo_mode_setup"
    assert entry["content"] == [300, 220]
    assert entry["x11"] == [337, 261]
    assert entry["scale"] == [2.0, 2.0]
    assert entry["result"] == "PASS"
    assert flushes == [["solo_mode_setup"]]


@pytest.mark.parametrize(
    ("producer", "recorder_name"),
    [
        (runtime_env.g1_baseline, "input_record"),
        (runtime_env.g1_presentation_trace, "record_input"),
    ],
)
def test_g1_selector_producers_guard_against_untagged_recorder_regression(
    producer, recorder_name: str,
):
    """Keep each real runtime producer wired to the tagged recorder helper."""

    tree = ast.parse(textwrap.dedent(inspect.getsource(producer)))
    recorder_defs = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == recorder_name
    ]
    assert len(recorder_defs) == 1
    recorder_body = recorder_defs[0]

    helper_calls = [
        node for node in ast.walk(recorder_body)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_g1_record_selector_input"
    ]
    assert len(helper_calls) == 1
    assert not any(
        isinstance(node, ast.Constant) and node.value == "OBSERVED"
        for node in ast.walk(recorder_body)
    )

    flow_calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_g1_selector_flow"
    ]
    assert any(
        len(node.args) >= 5
        and isinstance(node.args[4], ast.Name)
        and node.args[4].id == recorder_name
        for node in flow_calls
    )


def test_wait_state_passes_true_to_bool_compatible_reader():
    observed: list[bool] = []

    def read_state(detailed: bool) -> dict[str, int]:
        observed.append(detailed)
        return {"ps": 7}

    result = runtime_env._wait_state(
        read_state, lambda item: item.get("ps") == 7,
        time.monotonic(), 1, "state was not observed",
    )

    assert result == {"ps": 7}
    assert observed == [True]


def test_g1_wait_state_pass_exposes_read_coverage_without_gating_response(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    wait_observation: dict[str, object] = {}
    reads: list[object] = [OSError("transient state read failed"), {"ps": 7}]

    def read_state(_detailed: bool) -> dict[str, object]:
        item = reads.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    result = runtime_env._wait_state(
        read_state, lambda item: item.get("ps") == 7,
        started=0.0, timeout=10.0, message="state was not observed",
        stage="unit_select", stage_budget=1.0, stage_started=0.0,
        wait_observation=wait_observation,
    )

    assert result == {"ps": 7}
    assert wait_observation["poll_count"] == 1
    assert wait_observation["poll_attempt_count"] == 2
    assert wait_observation["read_error_count"] == 1
    assert wait_observation["read_error_ratio"] == 0.5
    assert wait_observation["read_error_coverage_exceeds_threshold"] is True
    inputs = [{"tag": "unit_select", "result": "PASS", "wait_observation": wait_observation}]
    verdict = runtime_env._g1_input_verdict(inputs, enabled=True)
    assert verdict["read_coverage"]["unit_select"] == {
        field: wait_observation[field] for field in runtime_env.G1_READ_COVERAGE_FIELDS
    }


def test_g1_wait_state_classifies_unreadable_polls_as_unknown(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    wait_observation: dict[str, object] = {}

    def unreadable(_detailed: bool) -> dict[str, object]:
        raise OSError("selected-unit read failed")

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            unreadable, lambda _item: False,
            started=0.0, timeout=10.0, message="selection did not change",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
            wait_observation=wait_observation,
        )

    observation = caught.value.observation
    assert caught.value.classification == "UNKNOWN_STATE_READ_FAILURE"
    assert caught.value.classification != "FAIL_NO_EFFECT"
    assert observation["poll_count"] == 0
    assert observation["poll_attempt_count"] == 4
    assert observation["read_error_count"] == 4
    assert observation["first_read_error_provenance"] == "OSError: selected-unit read failed"
    assert observation["last_read_error_provenance"] == "OSError: selected-unit read failed"
    assert "selection_observation" not in observation


def test_g1_wait_state_marks_selection_unavailable_after_unreadable_tail(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    before = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    wait_observation: dict[str, object] = {}
    reads = {"count": 0}

    def sound_then_unreadable(_detailed: bool) -> dict[str, object]:
        reads["count"] += 1
        if reads["count"] <= 2:
            return dict(before)
        raise OSError("candidate process state is unavailable")

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            sound_then_unreadable,
            lambda item: runtime_env._g1_selection_responded(
                before, item, diagnostics=wait_observation,
            ),
            started=0.0, timeout=10.0, message="selection did not change",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
            wait_observation=wait_observation,
        )

    observation = caught.value.observation
    assert caught.value.classification == "UNKNOWN_STATE_READ_FAILURE"
    assert observation["poll_count"] == 2
    assert observation["poll_attempt_count"] == 4
    assert observation["read_error_count"] == 2
    assert observation["selection_observation"]["status"] == "UNAVAILABLE"
    assert observation["first_read_error_provenance"].startswith("OSError:")
    assert observation["last_read_error_provenance"].startswith("OSError:")
    assert observation["successful_poll_ratio"] == 0.5
    assert observation["read_error_ratio"] == 0.5
    assert observation["read_error_coverage_exceeds_threshold"] is True


def test_g1_wait_state_rejects_read_error_heavy_window_even_with_readable_tail(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    before = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    wait_observation: dict[str, object] = {}
    reads: list[object] = [
        OSError("transient selected-unit read failed"),
        OSError("transient selected-unit read failed"),
        OSError("transient selected-unit read failed"),
        dict(before),
    ]

    def mostly_unreadable(_detailed: bool) -> dict[str, object]:
        item = reads.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            mostly_unreadable,
            lambda item: runtime_env._g1_selection_responded(
                before, item, diagnostics=wait_observation,
            ),
            started=0.0, timeout=10.0, message="selection did not change",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
            wait_observation=wait_observation,
        )

    observation = caught.value.observation
    assert caught.value.classification == "UNKNOWN_STATE_READ_COVERAGE"
    assert caught.value.classification != "FAIL_NO_EFFECT"
    assert observation["poll_count"] == 1
    assert observation["poll_attempt_count"] == 4
    assert observation["read_error_count"] == 3
    assert observation["successful_poll_ratio"] == 0.25
    assert observation["read_error_ratio"] == 0.75
    assert observation["read_error_coverage_threshold_ratio"] == 0.25
    assert observation["read_error_coverage_exceeds_threshold"] is True
    assert observation["selection_observation"]["status"] == "UNAVAILABLE"


@pytest.mark.parametrize(
    ("reads", "expected_classification"),
    [
        (
            [
                OSError("transient selected-unit read failed"),
                OSError("transient selected-unit read failed"),
                OSError("transient selected-unit read failed"),
                {
                    "count": 1,
                    "selected_slot": 1198,
                    "selected_type": "UNKNOWN",
                    "selected_type_provenance": "OSError: torn selected-unit read",
                },
            ],
            "UNKNOWN_STATE_READ_COVERAGE",
        ),
        (
            [
                {
                    "count": 1,
                    "selected_slot": 1198,
                    "selected_type": "UNKNOWN",
                    "selected_type_provenance": "OSError: torn selected-unit read",
                },
                OSError("transient selected-unit read failed"),
                OSError("transient selected-unit read failed"),
                OSError("transient selected-unit read failed"),
            ],
            "UNKNOWN_STATE_READ_FAILURE",
        ),
    ],
)
def test_g1_wait_state_preserves_corruption_when_read_coverage_is_unknown(
    monkeypatch: pytest.MonkeyPatch,
    reads: list[object],
    expected_classification: str,
):
    """Coverage/read failures must not mask a previously observed corruption."""

    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    before = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    wait_observation: dict[str, object] = {}

    def read_sequence(_detailed: bool) -> dict[str, object]:
        item = reads.pop(0)
        if isinstance(item, BaseException):
            raise item
        return dict(item)

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            read_sequence,
            lambda item: runtime_env._g1_selection_responded(
                before, item, diagnostics=wait_observation,
            ),
            started=0.0, timeout=10.0, message="selection did not change",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
            wait_observation=wait_observation,
        )

    observation = caught.value.observation
    assert caught.value.classification == expected_classification
    assert observation["read_error_ratio"] == 0.75
    assert observation["read_error_coverage_exceeds_threshold"] is True
    selection_observation = observation["selection_observation"]
    assert selection_observation["status"] == "CORRUPTED"
    assert selection_observation["corrupted_poll_count"] == 1
    assert selection_observation["first_corruption_provenance"] == (
        selection_observation["last_corruption_provenance"]
    )


def test_g1_wait_state_keeps_boundary_read_error_coverage_as_hard_no_effect(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )
    before = {"count": 1, "selected_slot": 1199, "selected_type": 70}
    reads: list[object] = [
        OSError("one selected-unit read failed"),
        dict(before), dict(before), dict(before),
    ]

    def one_error(_detailed: bool) -> dict[str, object]:
        item = reads.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            one_error, lambda _item: False,
            started=0.0, timeout=10.0, message="selection did not change",
            stage="drag_select", stage_budget=1.0, stage_started=0.0,
        )

    observation = caught.value.observation
    assert caught.value.classification == "FAIL_NO_EFFECT"
    assert observation["successful_poll_ratio"] == 0.75
    assert observation["read_error_ratio"] == 0.25
    assert observation["read_error_coverage_exceeds_threshold"] is False


def test_g1_wait_state_classifies_stage_timeout_as_no_effect(monkeypatch: pytest.MonkeyPatch):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds))

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: {"tick": 4}, lambda _item: False,
            started=0.0, timeout=10.0, message="selection did not change",
            stage="unit_select", stage_budget=1.0, stage_started=0.0,
        )

    assert caught.value.classification == "FAIL_NO_EFFECT"
    assert caught.value.remaining_budget_after == 9.0
    assert caught.value.predicate_observed is False
    assert caught.value.last == {"tick": 4}
    assert caught.value.observation["wait_started_elapsed"] == 0.0
    assert caught.value.observation["effective_poll_window"] == 1.0
    assert caught.value.observation["truncation_seconds"] == 0.0
    assert caught.value.observation["truncation_threshold_seconds"] == 0.25
    assert caught.value.observation["window_truncated"] is False
    assert caught.value.observation["poll_count"] == 4


def test_g1_wait_state_keeps_small_observation_window_truncation_as_no_effect(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [0.3]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: {"tick": 4}, lambda _item: False,
            started=0.0, timeout=20.0, message="selection did not change",
            stage="unit_select", stage_budget=10.0, stage_started=0.0,
        )

    assert caught.value.classification == "FAIL_NO_EFFECT"
    assert caught.value.classification != "PASS"
    assert caught.value.observation["effective_poll_window"] == 9.7
    assert caught.value.observation["truncation_seconds"] == 0.3
    assert caught.value.observation["truncation_threshold_seconds"] == 2.5
    assert caught.value.observation["window_truncated"] is False


def test_g1_wait_state_classifies_large_truncated_observation_window_as_unknown(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [8.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: {"tick": 4}, lambda _item: False,
            started=0.0, timeout=20.0, message="selection did not change",
            stage="unit_select", stage_budget=10.0, stage_started=0.0,
        )

    assert caught.value.classification == "UNKNOWN_OBSERVATION_WINDOW_TRUNCATED"
    assert caught.value.classification != "PASS"
    assert caught.value.observation["wait_started_elapsed"] == 8.0
    assert caught.value.observation["effective_poll_window"] == 2.0
    assert caught.value.observation["truncation_seconds"] == 8.0
    assert caught.value.observation["truncation_threshold_seconds"] == 2.5
    assert caught.value.observation["truncation_ratio"] == 0.8
    assert caught.value.observation["truncation_threshold_ratio"] == 0.25
    assert caught.value.observation["truncation_exceeds_threshold"] is True
    assert caught.value.observation["window_truncated"] is True
    assert caught.value.observation["poll_count"] == 8
    assert caught.value.observation["first_poll_elapsed"] == 8.0
    assert caught.value.observation["last_poll_elapsed"] == 9.75


def test_g1_input_phase_over_budget_has_structured_cause(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: 31.6)
    metrics = {
        "items": {
            "capture:selection_after": {"status": "PASS", "elapsed_seconds": 0.4},
            "capture:production_before": {"status": "PASS", "elapsed_seconds": 0.3},
            "capture:drag_after": {"status": "PASS", "elapsed_seconds": 0.5},
            "capture:minimap_after": {"status": "PASS", "elapsed_seconds": 0.2},
            "production_provenance": {
                "status": "PASS", "elapsed_seconds": 0.6,
                "executable_sha256": runtime_env.ORIGINAL_SHA256,
            },
        }
    }

    runtime_env._g1_finalize_input_phase(metrics, 0.0)

    assert metrics["input_phase_elapsed"] == 31.6
    assert metrics["budget_status"] == "OVER_BUDGET"
    assert metrics["over_budget"] is True
    assert metrics["over_budget_cause"]["kind"] == "INPUT_PHASE_WALL_CLOCK_EXCEEDED"
    assert metrics["over_budget_cause"]["excess_seconds"] == 0.1
    assert set(metrics["over_budget_cause"]["measured_items"]) == set(metrics["items"])


def test_g1_wait_state_classifies_shared_budget_exhaustion_as_unknown(monkeypatch: pytest.MonkeyPatch):
    clock = [0.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds))

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: {"tick": 9}, lambda _item: False,
            started=0.0, timeout=1.0, message="camera did not change",
            stage="minimap", stage_budget=10.0, stage_started=0.0,
        )

    assert caught.value.classification == "UNKNOWN_BUDGET_EXHAUSTED"
    assert caught.value.remaining_budget_after == 0.0
    assert caught.value.last == {"tick": 9}


def test_g1_wait_state_separates_pre_poll_truncation_from_run_deadline_clamp(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [2.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: {"tick": 9}, lambda _item: False,
            started=0.0, timeout=5.0, message="camera did not change",
            stage="minimap", stage_budget=10.0, stage_started=0.0,
        )

    observation = caught.value.observation
    assert caught.value.classification == "UNKNOWN_BUDGET_EXHAUSTED"
    assert observation["effective_poll_window"] == 3.0
    assert observation["run_deadline_clamped"] is True
    assert observation["run_deadline_clamp_seconds"] == 5.0
    assert observation["truncation_seconds"] == 2.0
    assert observation["truncation_ratio"] == 0.2
    assert observation["truncation_threshold_ratio"] == 0.25
    assert observation["truncation_exceeds_threshold"] is False
    assert observation["window_truncated"] is False


def test_g1_wait_state_clamp_keeps_threshold_evidence_consistent_above_threshold(
    monkeypatch: pytest.MonkeyPatch,
):
    clock = [4.0]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: {"tick": 9}, lambda _item: False,
            started=0.0, timeout=6.0, message="camera did not change",
            stage="minimap", stage_budget=10.0, stage_started=0.0,
        )

    observation = caught.value.observation
    assert caught.value.classification == "UNKNOWN_BUDGET_EXHAUSTED"
    assert observation["effective_poll_window"] == 2.0
    assert observation["run_deadline_clamped"] is True
    assert observation["run_deadline_clamp_seconds"] == 4.0
    assert observation["truncation_seconds"] == 4.0
    assert observation["truncation_ratio"] == 0.4
    assert observation["truncation_threshold_ratio"] == 0.25
    assert observation["truncation_exceeds_threshold"] is True
    assert observation["window_truncated"] is False


@pytest.mark.parametrize(
    ("pre_poll_seconds", "expected_classification", "expected_exceeds"),
    [
        (2.4999, "FAIL_NO_EFFECT", False),
        (2.5001, "UNKNOWN_OBSERVATION_WINDOW_TRUNCATED", True),
    ],
)
def test_g1_wait_state_evidence_distinguishes_near_threshold_runs(
    monkeypatch: pytest.MonkeyPatch,
    pre_poll_seconds: float,
    expected_classification: str,
    expected_exceeds: bool,
):
    clock = [pre_poll_seconds]
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        runtime_env.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )

    with pytest.raises(runtime_env._G1WaitTimeout) as caught:
        runtime_env._wait_state(
            lambda _detailed: {"tick": 4}, lambda _item: False,
            started=0.0, timeout=20.0, message="selection did not change",
            stage="unit_select", stage_budget=10.0, stage_started=0.0,
        )

    observation = caught.value.observation
    assert caught.value.classification == expected_classification
    assert observation["truncation_ratio"] == round(pre_poll_seconds / 10.0, 9)
    assert observation["truncation_threshold_ratio"] == 0.25
    assert observation["truncation_exceeds_threshold"] is expected_exceeds
    assert observation["window_truncated"] is expected_exceeds


def test_g1_input_stage_flushes_entry_before_timeout_and_keeps_unknown_nonpassing():
    inputs: list[dict[str, object]] = []
    flushes: list[list[str]] = []

    def wait(_reader, _predicate, _message, **_kwargs):
        raise runtime_env._G1WaitTimeout(
            "selection did not change", classification="FAIL_NO_EFFECT", last={"tick": 8},
            finished_elapsed=10.0, remaining_budget_after=80.0,
        )

    with pytest.raises(runtime_env._G1WaitTimeout):
        runtime_env._g1_run_input_sequence(
            inputs=inputs, content_crop=(0, 0, 800, 600), scale=(1.0, 1.0),
            capture=lambda tag: {"sha256": tag}, runtime_state=lambda: {"ps": 3, "tick": 7},
            game_state=lambda: {"ps": 3, "tick": 7}, read_selection=lambda: {"count": 0},
            read_camera=lambda: [0, 0], wait=wait, click=lambda _x, _y: None,
            drag=lambda _x, _y, _to_x, _to_y: None,
            read_production_cell=lambda: {"status": "observed"},
            flush=lambda: flushes.append([str(item["tag"]) for item in inputs]),
            started=0.0, timeout=90.0,
        )

    assert flushes[0] == ["unit_select"]
    assert inputs[0]["timeout_cause"] == "FAIL_NO_EFFECT"
    assert inputs[0]["result"] == "FAIL_NO_EFFECT"
    assert inputs[0]["predicate_observed"] is False
    checks = runtime_env._g1_input_verdict(inputs, enabled=True)
    assert checks["required_inputs"] is False
    unknown_inputs = [
        {"tag": tag, "result": "UNKNOWN_BUDGET_EXHAUSTED" if tag == "unit_select" else "PASS"}
        for tag in runtime_env.G1_REQUIRED_INPUT_TAGS
    ]
    unknown_checks = runtime_env._g1_input_verdict(unknown_inputs, enabled=True)
    assert unknown_checks["required_inputs"] is False
    unknown_verdict = runtime_env._g1_presentation_verdict(
        error=None, cleanup={"ok": True}, validator={"status": "PASS"},
        inputs=unknown_inputs, input_sequence=True,
    )
    assert unknown_verdict["overall"] != "PASS"


def test_g1_flush_input_stage_preserves_final_diagnostic_fields(tmp_path: Path):
    evidence = {
        "error": "stable command-cell branch was not eligible",
        "command_branch": {"stable": True, "eligible": False},
        "primary_command_table": {"before": {"size": 0x60}},
    }
    inputs = [{"tag": "production", "result": "BLOCKED", "provenance_error": "snapshot"}]

    runtime_env._g1_flush_input_stage(tmp_path, evidence, inputs)

    flushed = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    assert flushed["error"] == evidence["error"]
    assert flushed["command_branch"] == evidence["command_branch"]
    assert flushed["primary_command_table"] == evidence["primary_command_table"]
    assert flushed["inputs"] == inputs


def test_g1_flush_input_stage_promotes_production_diagnostics_to_top_level(tmp_path: Path):
    evidence: dict[str, object] = {}
    inputs = [{
        "tag": "production",
        "result": "BLOCKED",
        "provenance_error": "_CommandCellSnapshotError: stable-ineligible",
        "command_cell_diagnostics": [{"attempt": 1}],
        "command_branch": {"stable": True, "eligible": False},
        "alternate_ui_snapshot": {"count": 0},
        "primary_command_table": {"size": 0x60},
    }]

    runtime_env._g1_flush_input_stage(tmp_path, evidence, inputs)

    flushed = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    assert flushed["error"] == inputs[0]["provenance_error"]
    assert flushed["production_provenance_error"] == inputs[0]["provenance_error"]
    assert flushed["command_cell_diagnostics"] == inputs[0]["command_cell_diagnostics"]
    assert flushed["command_branch"] == inputs[0]["command_branch"]
    assert flushed["alternate_ui_snapshot"] == inputs[0]["alternate_ui_snapshot"]
    assert flushed["primary_command_table"] == inputs[0]["primary_command_table"]
    assert flushed["inputs"] == inputs


def test_g1_flush_input_stage_preserves_fatal_error_without_provenance_marker(
    tmp_path: Path,
):
    evidence: dict[str, object] = {"error": "fatal input failure"}
    inputs = [{"tag": "unit_select", "result": "PASS"}]

    runtime_env._g1_flush_input_stage(tmp_path, evidence, inputs)

    flushed = json.loads((tmp_path / "evidence.json").read_text(encoding="utf-8"))
    assert flushed["error"] == "fatal input failure"
    assert "production_provenance_error" not in flushed


def test_g1_presentation_verdict_keeps_fatal_error_and_cannot_pass():
    inputs = [{"tag": tag, "result": "PASS"} for tag in runtime_env.G1_REQUIRED_INPUT_TAGS]

    verdict = runtime_env._g1_presentation_verdict(
        error="fatal input failure", cleanup={"ok": True}, validator={"status": "PASS"},
        inputs=inputs, input_sequence=True,
    )

    assert verdict["error"] == "fatal input failure"
    assert verdict["overall"] != "PASS"


def test_g1_endpoint_contracts_require_ps5_and_local_auto_ready():
    assert runtime_env._g1_confirm_endpoint_pass(4, 5, 1, True)
    assert not runtime_env._g1_confirm_endpoint_pass(4, 5, 0, True)
    assert runtime_env._g1_ready_endpoint_pass(
        5, 5, 1, {"local_index": 0, "ready_value": 1}
    )
    assert not runtime_env._g1_ready_endpoint_pass(
        5, 5, 1, {"local_index": 8, "ready_value": 1}
    )
    assert not runtime_env._g1_ready_endpoint_pass(5, 5, 0, {"local_index": 0, "ready_value": 1})
    assert not runtime_env._g1_ready_endpoint_pass(5, 5, 1, {"local_index": 0, "ready_value": 0})
    assert runtime_env._g1_start_endpoint_pass(5, {"ps": 3, "tick": 1})
    assert not runtime_env._g1_start_endpoint_pass(7, {"ps": 3, "tick": 1})
