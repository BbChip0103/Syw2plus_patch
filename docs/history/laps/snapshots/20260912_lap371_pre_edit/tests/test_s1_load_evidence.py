"""Synthetic regression checks for the isolated S1 load-evidence reader."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import s1_load_evidence as s1


def _fixture(tmp_path: Path, *, teams: tuple[int, ...] = (1,) * 8) -> tuple[Path, list[dict[str, object]]]:
    raw = bytearray(2_259_634 + 7 * s1.PLAYER_STRIDE + s1.PLAYER_RECORD_SIZE)
    records: list[dict[str, object]] = []
    for owner, team in enumerate(teams):
        opponent = sum(1 << other for other, other_team in enumerate(teams) if other != owner and other_team != team)
        record = bytes((2, owner, 1, 1 << owner, opponent, team))
        offset = 2_259_634 + owner * s1.PLAYER_STRIDE
        raw[offset:offset + 6] = record
        records.append({"owner": owner, "raw_hex": record.hex(" ")})
    path = tmp_path / "fixture.dat"
    path.write_bytes(raw)
    return path, records


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _spec(path: Path, index: int = 1) -> str:
    s1.FIXTURES["synthetic.dat"] = s1.FixtureSpec("synthetic.dat", path.stat().st_size, _sha(path), index, 2_259_634)
    return "synthetic.dat"


def _live_reader(players: list[dict[str, object]]):
    calls = 0

    def read(address: int, size: int) -> bytes:
        nonlocal calls
        calls += 1
        phase = "pre" if calls <= 11 else "post"
        if address == s1.GROUP_WORD_ADDRESS and size == 2:
            return (0).to_bytes(2, "little")
        if address == s1.SELECTED_INDEX_ADDRESS and size == 2:
            return (1).to_bytes(2, "little")
        if address == s1.PROGRAM_STATE_ADDRESS and size == 2:
            return (35 if phase == "pre" else 3).to_bytes(2, "little")
        for owner, player in enumerate(players):
            if address == s1.PLAYER_BASE + owner * s1.PLAYER_STRIDE and size == 6:
                raw = bytes.fromhex(str(player["raw_hex"]))
                if phase == "pre":
                    raw = bytes((1, *raw[1:]))
                return raw
        raise AssertionError(f"unexpected read {address:#x}/{size}")

    return read


def test_direct_pre_post_eight_slot_fixture_pass(tmp_path: Path):
    path, players = _fixture(tmp_path)
    name = _spec(path)
    reader = _live_reader(players)
    pre = s1.read_s1_snapshot(reader, phase="pre")
    after = s1.read_s1_snapshot(reader, phase="post")
    result = s1.evaluate(
        fixture_path=path, fixture_name=name, group_word=0, selected_index=1,
        post=s1.collected_load_observation(pre, after),
    )
    assert result["status"] == "PASS"
    assert result["classification"] == "LOAD_RESTORED_PLAYER_STRUCTS"
    assert result["fixture"]["group_word"] == 0
    assert result["fixture"]["selected_index"] == 1
    assert len(result["fixture_players"]) == 8
    assert result["fixture_players"][1]["self_bit_mask"] == 2
    assert result["load"]["open_status"] == "not_directly_observable"


def test_event_boundary_orders_trigger_wait_and_post_reads(tmp_path: Path):
    path, players = _fixture(tmp_path)
    events: list[str] = []
    phase = "pre"

    def read(address: int, size: int) -> bytes:
        nonlocal phase
        if address == s1.GROUP_WORD_ADDRESS and size == 2:
            return (0).to_bytes(2, "little")
        if address == s1.SELECTED_INDEX_ADDRESS and size == 2:
            return (1).to_bytes(2, "little")
        if address == s1.PROGRAM_STATE_ADDRESS and size == 2:
            if phase == "pre":
                return (35).to_bytes(2, "little")
            if phase == "loading":
                events.append("wait_ps")
                phase = "post"
            else:
                events.append("post_ps")
            return (3).to_bytes(2, "little")
        for owner, player in enumerate(players):
            if address == s1.PLAYER_BASE + owner * s1.PLAYER_STRIDE and size == 6:
                raw = bytes.fromhex(str(player["raw_hex"]))
                if phase == "pre":
                    raw = bytes((1, *raw[1:]))
                events.append(f"{phase}_player")
                return raw
        raise AssertionError(f"unexpected read {address:#x}/{size}")

    def trigger() -> None:
        nonlocal phase
        events.append("trigger")
        phase = "loading"

    observation = s1.collect_load_event_boundary(read, trigger=trigger, timeout=1)
    assert events.index("trigger") > events.index("pre_player")
    assert events.index("wait_ps") > events.index("trigger")
    assert events.index("post_ps") > events.index("wait_ps")
    assert events.index("post_player") > events.index("post_ps")
    assert observation["event_boundary"]["trigger_invocations"] == 1


@pytest.mark.parametrize("reported_count", [0, 2])
def test_event_boundary_rejects_non_exact_trigger_count(tmp_path: Path, reported_count: int):
    path, players = _fixture(tmp_path)

    with pytest.raises(s1.S1EventBoundaryError, match="exactly one") as caught:
        s1.collect_load_event_boundary(
            _live_reader(players), trigger=lambda: reported_count, timeout=1,
        )

    assert caught.value.classification == "TRIGGER_COUNT_MISMATCH"
    assert caught.value.boundary["trigger_invocations"] == 1


def test_event_boundary_timeout_is_fail_closed(tmp_path: Path):
    path, players = _fixture(tmp_path)
    now = 0.0
    reader = _live_reader(players)
    calls = 0

    def monotonic() -> float:
        return now

    def sleep(seconds: float) -> None:
        nonlocal now
        now += seconds

    def read(address: int, size: int) -> bytes:
        nonlocal calls
        calls += 1
        if calls >= 12 and address == s1.PROGRAM_STATE_ADDRESS:
            return (35).to_bytes(2, "little")
        return reader(address, size)

    with pytest.raises(s1.S1EventBoundaryError) as caught:
        s1.collect_load_event_boundary(
            read, trigger=lambda: None, timeout=0.5,
            monotonic=monotonic, sleep=sleep,
        )

    assert caught.value.classification == "PS3_WAIT_TIMEOUT"
    assert caught.value.boundary["status"] == "UNKNOWN"


def test_event_boundary_wait_read_failure_is_fail_closed(tmp_path: Path):
    path, players = _fixture(tmp_path)
    reader = _live_reader(players)
    calls = 0

    def read(address: int, size: int) -> bytes:
        nonlocal calls
        calls += 1
        if calls == 12:
            return b"short"
        return reader(address, size)

    with pytest.raises(s1.S1EventBoundaryError) as caught:
        s1.collect_load_event_boundary(read, trigger=lambda: None, timeout=1)

    assert caught.value.classification == "PS3_WAIT_READ_FAILURE"


def test_event_boundary_can_reuse_gated_pre_snapshot_once(tmp_path: Path):
    path, players = _fixture(tmp_path)
    phase = "pre"
    events: list[str] = []

    def read(address: int, size: int) -> bytes:
        if address == s1.GROUP_WORD_ADDRESS and size == 2:
            return (0).to_bytes(2, "little")
        if address == s1.SELECTED_INDEX_ADDRESS and size == 2:
            return (1).to_bytes(2, "little")
        if address == s1.PROGRAM_STATE_ADDRESS and size == 2:
            if phase == "pre":
                return (35).to_bytes(2, "little")
            events.append("wait_ps")
            return (3).to_bytes(2, "little")
        for owner, player in enumerate(players):
            if address == s1.PLAYER_BASE + owner * s1.PLAYER_STRIDE and size == 6:
                raw = bytes.fromhex(str(player["raw_hex"]))
                if phase == "pre":
                    raw = bytes((1, *raw[1:]))
                events.append(f"{phase}_player")
                return raw
        raise AssertionError(f"unexpected read {address:#x}/{size}")

    pre = s1.read_s1_snapshot(read, phase="pre")

    def trigger() -> int:
        nonlocal phase
        events.append("trigger")
        phase = "post"
        return 1

    observation = s1.collect_load_event_boundary(
        read, trigger=trigger, timeout=1, pre_snapshot=pre,
        precondition=lambda sample: {"slot": sample["selected_index"]},
    )
    assert events.count("pre_player") == 8
    assert events.index("trigger") > max(index for index, event in enumerate(events) if event == "pre_player")
    assert observation["pre"] == pre
    assert observation["event_boundary"]["precondition"] == {"slot": 1}


def test_event_boundary_trigger_delay_consumes_absolute_event_deadline(tmp_path: Path):
    path, players = _fixture(tmp_path)
    reader = _live_reader(players)
    pre = s1.read_s1_snapshot(reader, phase="pre")
    now = 0.0

    def monotonic() -> float:
        return now

    def trigger() -> None:
        nonlocal now
        now = 2.0

    with pytest.raises(s1.S1EventBoundaryError) as caught:
        s1.collect_load_event_boundary(
            reader, trigger=trigger, timeout=10, pre_snapshot=pre,
            event_started=0.0, event_deadline=1.0, monotonic=monotonic,
        )
    assert caught.value.classification == "EVENT_DEADLINE_EXPIRED"
    assert caught.value.boundary["trigger_invocations"] == 1


def test_open_failure_at_ps3_is_unknown_not_pass(tmp_path: Path):
    path, _ = _fixture(tmp_path)
    name = _spec(path)
    result = s1.evaluate(
        fixture_path=path, fixture_name=name, group_word=0, selected_index=1,
        post={"ps": 3, "load": {"open_succeeded": False}, "players": []},
    )
    assert result["status"] == "UNKNOWN"
    assert result["classification"] == "OPEN_FAILURE_PS3"


@pytest.mark.parametrize("selected_index", [0, 2, 8, 99])
def test_wrong_slot_is_fail_closed(tmp_path: Path, selected_index: int):
    path, _ = _fixture(tmp_path)
    name = _spec(path)
    result = s1.evaluate(fixture_path=path, fixture_name=name, group_word=0, selected_index=selected_index)
    assert result["status"] == "UNKNOWN"
    assert result["classification"] == "INVALID_SLOT"


def test_wrong_sha_is_unknown_and_raw_bytes_are_not_used(tmp_path: Path):
    path, _ = _fixture(tmp_path)
    s1.FIXTURES["synthetic.dat"] = s1.FixtureSpec("synthetic.dat", path.stat().st_size, "0" * 64, 1, 2_259_634)
    result = s1.evaluate(fixture_path=path, fixture_name="synthetic.dat", group_word=0, selected_index=1)
    assert result["status"] == "UNKNOWN"
    assert result["classification"] == "FIXTURE_IDENTITY_MISMATCH"
    assert result["fixture_players"] == []


def test_reader_missing_and_partial_post_read_are_unknown(tmp_path: Path):
    path, players = _fixture(tmp_path)
    name = _spec(path)
    missing = s1.evaluate(fixture_path=path, fixture_name=name, group_word=0, selected_index=1)
    assert missing["classification"] == "READER_MISSING"
    partial = s1.evaluate(
        fixture_path=path, fixture_name=name, group_word=0, selected_index=1,
        post={"ps": 3, "load": {"open_succeeded": True}, "players": players[:7]},
    )
    assert partial["classification"] == "UNTRUSTED_READER_EVIDENCE"


def test_copied_matching_payload_without_collector_provenance_is_unknown(tmp_path: Path):
    path, players = _fixture(tmp_path)
    name = _spec(path)
    result = s1.evaluate(
        fixture_path=path, fixture_name=name, group_word=0, selected_index=1,
        post={"ps": 3, "load": {"open_succeeded": True}, "players": players},
    )
    assert result["status"] == "UNKNOWN"
    assert result["classification"] == "UNTRUSTED_READER_EVIDENCE"


def test_direct_pre_post_without_change_is_unknown(tmp_path: Path):
    path, players = _fixture(tmp_path)
    name = _spec(path)
    reader = _live_reader(players)
    sample = dict(s1.read_s1_snapshot(reader, phase="post"), ps=3)
    before = dict(sample, phase="pre", ps=35)
    result = s1.evaluate(
        fixture_path=path, fixture_name=name, group_word=0, selected_index=1,
        post=s1.collected_load_observation(before, sample),
    )
    assert result["classification"] == "PRE_POST_NO_CHANGE"


def test_group_or_program_state_read_failure_is_unknown(tmp_path: Path):
    path, _ = _fixture(tmp_path)
    name = _spec(path)

    def read(_address: int, _size: int) -> bytes:
        raise OSError("unmapped")

    with pytest.raises(s1.S1ReadError) as caught:
        s1.read_s1_snapshot(read, phase="pre")
    assert caught.value.owner == -1
    result = s1.evaluate(
        fixture_path=path, fixture_name=name, group_word=0, selected_index=1,
        post={"collector_error": {"message": str(caught.value)}},
    )
    assert result["classification"] == "READER_READ_FAILURE"


def test_read_post_player_structs_rejects_partial_record():
    def read(_address: int, _size: int) -> bytes:
        return b"short"

    with pytest.raises(s1.S1ReadError) as caught:
        s1.read_post_player_structs(read)
    assert caught.value.owner == 0
    assert caught.value.requested == 6
    assert caught.value.actual == 5


def test_cli_writes_only_new_s1_artifact(tmp_path: Path):
    path, _ = _fixture(tmp_path)
    name = _spec(path)
    post = tmp_path / "post.json"
    post.write_text(json.dumps({"ps": 3, "load": {"open_succeeded": False}}), encoding="utf-8")
    output = tmp_path / "s1_load_evidence.json"
    assert s1.main([
        "--fixture", str(path), "--fixture-name", name, "--group-word", "0",
        "--selected-index", "1", "--post-json", str(post), "--output", str(output),
    ]) == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["classification"] == "OPEN_FAILURE_PS3"
    assert s1.main([
        "--fixture", str(path), "--fixture-name", name, "--group-word", "0",
        "--selected-index", "1", "--output", str(output),
    ]) == 2


def test_runtime_env_exposes_the_same_isolated_s1_cli_lane(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    path, _ = _fixture(tmp_path)
    name = _spec(path)
    captured: dict[str, object] = {}

    def fake_evaluate(**kwargs):
        captured.update(kwargs)
        return {"status": "UNKNOWN", "classification": "READER_MISSING"}

    monkeypatch.setattr(s1, "evaluate", fake_evaluate)
    output = tmp_path / "s1_load_evidence.json"
    from tools import runtime_env

    result = runtime_env.g1_s1_load_evidence(
        path, fixture_name=name, group_word=0, selected_index=1, output=output,
    )
    assert result["classification"] == "READER_MISSING"
    assert captured["fixture_path"] == path
    assert json.loads(output.read_text(encoding="utf-8"))["classification"] == "READER_MISSING"


def test_runtime_env_live_lane_reads_group_ps_and_all_player_structs(tmp_path: Path):
    path, players = _fixture(tmp_path)
    name = _spec(path)
    from tools import runtime_env

    result = runtime_env.g1_s1_load_evidence(
        path, fixture_name=name, group_word=0, selected_index=1,
        read_memory=_live_reader(players), trigger=lambda: 1,
    )
    assert result["status"] == "PASS"
    assert result["classification"] == "LOAD_RESTORED_PLAYER_STRUCTS"
    assert result["load"]["pre_ps"] == 35
    assert result["load"]["post_ps"] == 3
    assert len(result["post_ps3_players"]) == 8


def test_runtime_env_live_lane_without_trigger_never_reads_immediate_post(tmp_path: Path):
    path, _ = _fixture(tmp_path)
    name = _spec(path)
    calls: list[tuple[int, int]] = []

    def read(address: int, size: int) -> bytes:
        calls.append((address, size))
        return b"\x00\x00"

    from tools import runtime_env

    result = runtime_env.g1_s1_load_evidence(
        path, fixture_name=name, group_word=0, selected_index=1, read_memory=read,
    )
    assert result["status"] == "UNKNOWN"
    assert result["classification"] == "READER_READ_FAILURE"
    assert result["event_boundary"]["classification"] == "EVENT_TRIGGER_MISSING"
    assert calls == []


def test_runtime_main_dispatches_single_owner_original_command(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    from tools import runtime_env

    captured: dict[str, object] = {}

    def fake_command(source: Path, *, runtime_root: Path) -> dict[str, object]:
        captured.update({"source": source, "runtime_root": runtime_root})
        return {"status": "NO_RUN", "classification": "IDENTITY_MISMATCH"}

    monkeypatch.setattr(runtime_env, "g1_s1_original_load_evidence", fake_command)
    source = tmp_path / "source"
    runtime_root = tmp_path / "runtime"
    assert runtime_env.runtime_main([
        "g1-s1-original-load-evidence", "--source", str(source),
        "--runtime-root", str(runtime_root),
    ]) == 0
    assert captured == {"source": source, "runtime_root": runtime_root}


def _fake_original_command_lane(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *, cleanup_ok: bool = True,
                                evaluate_delay: float = 0.0, cleanup_delay: float = 0.0,
                                prepare_delay: float = 0.0, pre_delay: float = 0.0,
                                stage_delays: dict[str, float] | None = None,
                                trigger_delay: float = 0.0, wait_delay: float = 0.0, artifact_delay: float = 0.0,
                                pre_slot: int = 1,
                                existing: str | None = None):
    """Install only fake process/input boundaries; call the production command."""
    from tools import runtime_env

    clock = {"now": 0.0}
    monkeypatch.setattr(runtime_env.time, "monotonic", lambda: clock["now"])
    source = tmp_path / "source"
    (source / "save").mkdir(parents=True)
    source_exe = source / runtime_env.ORIGINAL_EXE
    source_exe.write_bytes(b"source")
    (source / "save" / "save000.dat").write_bytes(b"fixture")
    run = tmp_path / "run"
    game, prefix, output = run / "game", run / "prefix", run / "output"
    game.mkdir(parents=True)
    prefix.mkdir()
    output.mkdir()
    manifest_path = run / "manifest.json"
    manifest_path.write_text("{}", encoding="utf-8")
    if existing == "final":
        (output / "s1_original_load_evidence.json").write_text("old", encoding="utf-8")
    elif existing == "temporary":
        (output / ".s1_original_load_evidence.json.tmp").write_text("old", encoding="utf-8")
    prepared: dict[str, object] = {"launched": False, "trigger": 0}
    stage_delays = stage_delays or {}

    monkeypatch.setattr(runtime_env, "validate_original_source", lambda path: (source, source_exe))
    def fake_prepare(*_args, **kwargs):
        clock["now"] += prepare_delay
        return {"output": {"run_dir": str(run)}}
    monkeypatch.setattr(runtime_env, "prepare", fake_prepare)
    monkeypatch.setattr(runtime_env, "check_runtime", lambda _path: {"ok": True})
    monkeypatch.setattr(runtime_env, "_manifest", lambda _path: ({}, game, prefix, output))
    monkeypatch.setattr(runtime_env, "_s1_file_identity", lambda path, **kwargs: {
        "path": str(path), "status": "PASS", "expected_size": kwargs["expected_size"],
        "expected_sha256": kwargs["expected_sha256"], "actual_size": kwargs["expected_size"],
        "actual_sha256": kwargs["expected_sha256"],
    })
    monkeypatch.setattr(runtime_env, "_s1_snapshot_sources", lambda _output: {"files": []})
    monkeypatch.setattr(runtime_env, "_prefix_pids", lambda _prefix: [])
    monkeypatch.setattr(runtime_env, "_existing_state", lambda _prefix: {})
    monkeypatch.setattr(runtime_env, "_g1_r1_read_origin_checked", lambda *_args, **_kwargs: {"x": 240, "y": 145, "tag": 8})
    monkeypatch.setattr(runtime_env, "_window_tree", lambda *_args: "Window id: 0x1 (the root window)")
    monkeypatch.setattr(runtime_env, "_game_window_ids", lambda _tree: ("0x1", "0x2"))
    monkeypatch.setattr(runtime_env, "_xwininfo_details", lambda _display, window, _timeout: {
        "width": 1600 if window == "0x1" else 800,
        "height": 1200 if window == "0x1" else 600,
        "x": 10, "y": 20,
    })
    monkeypatch.setattr(runtime_env, "_xvfb", lambda *_args: (SimpleNamespace(poll=lambda: 0), ":99"))

    class FakeProcess:
        pid = 1234
        def poll(self):
            return 0
        def terminate(self):
            return None
        def kill(self):
            return None
        def wait(self, **_kwargs):
            return 0

    monkeypatch.setattr(runtime_env.subprocess, "Popen", lambda *_args, **_kwargs: FakeProcess())
    calls: list[list[str]] = []
    def fake_run(argv: list[str], **_kwargs):
        calls.append(list(argv))
        if argv[-2:] == ["410", "151"]:
            clock["now"] += trigger_delay
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(runtime_env.subprocess, "run", fake_run)
    def fake_wait(*_args, **kwargs):
        stage = kwargs["stage"]
        clock["now"] += stage_delays.get(stage, 0.0)
        if stage in stage_delays and stage_delays[stage] > kwargs["stage_budget"]:
            raise runtime_env.RuntimeSafetyError(f"synthetic {stage} timeout")
        return {"ps": 9 if stage == "launch_to_ps9" else 35}
    monkeypatch.setattr(runtime_env, "_wait_state", fake_wait)
    def fake_snapshot(*_args, **_kwargs):
        clock["now"] += pre_delay
        return {
            "_collector_token": s1._COLLECTOR_TOKEN, "phase": "pre", "ps": 35,
            "group_word": 0, "selected_index": pre_slot, "players": [], "read_points": [],
        }
    monkeypatch.setattr(s1, "read_s1_snapshot", fake_snapshot)
    def fake_collect(_read, *, trigger, **kwargs):
        prepared["trigger"] = int(trigger())
        clock["now"] += wait_delay
        if kwargs.get("event_deadline") is not None and clock["now"] >= kwargs["event_deadline"]:
            raise s1.S1EventBoundaryError(
                "EVENT_DEADLINE_EXPIRED", "synthetic event deadline", boundary={
                    "status": "UNKNOWN", "trigger_invocations": 1,
                },
            )
        now = clock["now"]
        return {
            "_collector_token": s1._COLLECTOR_TOKEN, "collector": "fake",
            "event_boundary": {"status": "COMPLETE", "wait_ps": [3], "trigger_invocations": 1,
                                "post_started": now, "post_finished": now},
            "post": {"_collector_token": s1._COLLECTOR_TOKEN, "phase": "post", "ps": 3,
                      "group_word": 0, "selected_index": 1, "players": [], "read_points": []},
        }
    monkeypatch.setattr(s1, "collect_load_event_boundary", fake_collect)
    def fake_evaluate(**_kwargs):
        clock["now"] += evaluate_delay
        return {"status": "PASS", "classification": "SYNTHETIC_PASS"}
    monkeypatch.setattr(s1, "evaluate", fake_evaluate)
    real_install = s1._install_new_json_payload
    def fake_install(path: Path, payload: str, **kwargs: object) -> None:
        clock["now"] += artifact_delay
        real_install(path, payload, **kwargs)
    monkeypatch.setattr(s1, "_install_new_json_payload", fake_install)
    def fake_cleanup(**_kwargs):
        cleanup_started = clock["now"]
        clock["now"] += cleanup_delay
        return {"ok": cleanup_ok, "owned_launchers_stopped": cleanup_ok,
                "xvfb_stopped": cleanup_ok, "prefix_processes_after": [],
                "residue_pids": [], "error": None if cleanup_ok else "synthetic cleanup failure",
                "started_elapsed": cleanup_started,
                "finalization_deadline_elapsed": min(runtime_env.G1_S1_TOTAL_DEADLINE,
                                                      cleanup_started + runtime_env.G1_S1_CLEANUP_RESERVE)}
    monkeypatch.setattr(runtime_env, "_s1_cleanup", fake_cleanup)
    prepared["calls"] = calls
    prepared["output"] = output
    prepared["clock"] = clock
    return runtime_env, source, run, prepared


def test_original_command_cleanup_is_before_one_final_artifact_and_fail_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, cleanup_ok=False)
    result = runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    artifact = json.loads((state["output"] / "s1_original_load_evidence.json").read_text(encoding="utf-8"))
    assert result["status"] == "UNKNOWN"
    assert result["classification"] == "CLEANUP_FAILURE"
    assert artifact["status"] == "UNKNOWN"
    assert artifact["cleanup"]["ok"] is False


def test_original_command_post_evaluate_timeout_is_unknown_and_artifact_is_not_pass(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, evaluate_delay=3.001)
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    artifact = json.loads((state["output"] / "s1_original_load_evidence.json").read_text(encoding="utf-8"))
    assert artifact["status"] != "PASS"


def test_original_command_load_trigger_is_exact_once_and_unscaled(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path)
    result = runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    calls = state["calls"]
    assert result["status"] == "PASS"
    assert state["trigger"] == 1
    load_clicks = [argv for argv in calls if any(item.endswith("x11_mouse_click.py") for item in argv)
                   and argv[-2:] == ["410", "151"]]
    assert len(load_clicks) == 1
    assert "--repeat" not in load_clicks[0]


@pytest.mark.parametrize("delay, should_pass", [(4.999, True), (5.001, False)])
def test_original_command_trigger_stage_boundary_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, delay: float, should_pass: bool,
):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, trigger_delay=delay)
    if should_pass:
        assert runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")["status"] == "PASS"
    else:
        with pytest.raises(runtime_env.RuntimeSafetyError):
            runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
        assert json.loads((state["output"] / "s1_original_load_evidence.json").read_text(encoding="utf-8"))["status"] != "PASS"


@pytest.mark.parametrize("delay, should_pass", [(9.999, True), (10.001, False)])
def test_original_command_ps3_wait_stage_boundary_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, delay: float, should_pass: bool,
):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, wait_delay=delay)
    if should_pass:
        assert runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")["status"] == "PASS"
    else:
        with pytest.raises(runtime_env.RuntimeSafetyError):
            runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
        assert json.loads((state["output"] / "s1_original_load_evidence.json").read_text(encoding="utf-8"))["status"] != "PASS"


@pytest.mark.parametrize("existing", ["final", "temporary"])
def test_original_command_rejects_artifact_collisions_before_launch(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, existing: str):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, existing=existing)
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    collision = (state["output"] / "s1_original_load_evidence.json" if existing == "final"
                 else state["output"] / ".s1_original_load_evidence.json.tmp")
    assert collision.read_text(encoding="utf-8") == "old"


def test_original_command_hard_deadline_does_not_install_late_artifact(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, cleanup_delay=151.0)
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    assert not state["output"].joinpath("s1_original_load_evidence.json").exists()


@pytest.mark.parametrize("delay, should_pass", [(9.999, True), (10.001, False)])
def test_original_command_cleanup_and_artifact_reserve_boundary_is_fail_closed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, delay: float, should_pass: bool,
):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, cleanup_delay=delay)
    if should_pass:
        assert runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")["status"] == "PASS"
    else:
        with pytest.raises(runtime_env.RuntimeSafetyError):
            runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
        assert not state["output"].joinpath("s1_original_load_evidence.json").exists()


def test_original_command_installer_delay_after_cleanup_deadline_does_not_install_artifact(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, artifact_delay=10.001)
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    assert not state["output"].joinpath("s1_original_load_evidence.json").exists()


def test_original_command_removes_artifact_from_late_noncompliant_installer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path)

    def late_install(path: Path, payload: str, **_kwargs: object) -> None:
        state["clock"]["now"] = 151.0  # type: ignore[index]
        path.write_text(payload, encoding="utf-8")

    from tools import s1_load_evidence as s1
    monkeypatch.setattr(s1, "_install_new_json_payload", late_install)
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    assert not state["output"].joinpath("s1_original_load_evidence.json").exists()


def test_original_command_pre_slot_mismatch_makes_zero_load_triggers(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, pre_slot=7)
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    assert state["trigger"] == 0


def test_original_command_prepare_cap_includes_command_entry_to_prepare(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    runtime_env, source, _run, _state = _fake_original_command_lane(monkeypatch, tmp_path, prepare_delay=60.001)
    with pytest.raises(runtime_env.RuntimeSafetyError, match="60 second cap"):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")


@pytest.mark.parametrize("stage", ["launch_to_ps9", "input_to_ps35"])
def test_original_command_wait_stage_caps_fail_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, stage: str):
    from tools import runtime_env as runtime_module
    runtime_env, source, _run, state = _fake_original_command_lane(
        monkeypatch, tmp_path, stage_delays={stage: runtime_module.G1_S1_STAGE_BUDGETS[stage] + 0.001},
    )
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    artifact = state["output"] / "s1_original_load_evidence.json"
    assert artifact.exists()
    assert json.loads(artifact.read_text(encoding="utf-8"))["status"] != "PASS"


def test_original_command_direct_pre_cap_fails_closed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, pre_delay=2.001)
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    assert json.loads((state["output"] / "s1_original_load_evidence.json").read_text(encoding="utf-8"))["status"] != "PASS"


def test_original_command_trigger_delay_consumes_absolute_event_deadline(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    runtime_env, source, _run, state = _fake_original_command_lane(monkeypatch, tmp_path, trigger_delay=141.0)
    with pytest.raises(runtime_env.RuntimeSafetyError):
        runtime_env.g1_s1_original_load_evidence(source, runtime_root=tmp_path / "runtime")
    artifact = json.loads((state["output"] / "s1_original_load_evidence.json").read_text(encoding="utf-8"))
    assert artifact["input"]["load_trigger"]["invocation_count"] == 1
    assert artifact["status"] != "PASS"
