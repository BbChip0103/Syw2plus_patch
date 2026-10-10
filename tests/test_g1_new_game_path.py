"""Contracts for the H-OS0 new-game path (PS9 -> PS7 -> PS5) measurement harness."""

import json
from pathlib import Path

import pytest

from tools import g1_saved_scene_probe as probe

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
G6_SOURCE = (ROOT / "tools/g6_shift_click_probe.py").read_text(encoding="utf-8")


def test_new_game_click_points_match_the_g6_probe() -> None:
    # Same logical 800x600 coordinates the G6 probe uses for PS9->PS7 and PS7->PS5.
    assert probe.NEW_GAME_MENU == (184, 560)
    assert probe.NEW_GAME_CONFIRM == (608, 564)
    assert "click(184, 560)" in G6_SOURCE
    assert "click(608, 564)" in G6_SOURCE


def test_census_state_accepts_the_new_game_screens() -> None:
    assert "choices=(3, 5, 7, 9, 29, 35)" in SOURCE


def test_new_game_walk_runs_before_the_load_click_and_leaves_by_state_complete() -> None:
    walk = SOURCE.index("if new_game_walk:")
    assert SOURCE.index("if census and census_state == 9:") < walk
    assert walk < SOURCE.index("load_clicks = [_inject(display, origin, LOAD_MENU")
    branch = SOURCE[walk:SOURCE.index("load_clicks = [_inject(display, origin, LOAD_MENU")]
    assert "_walk_new_game_path(" in branch
    assert "raise _CensusStateComplete()" in branch


def test_new_game_walk_is_candidate_trace_or_census_only() -> None:
    assert "new_game_walk = new_game_path or (census and census_state in (5, 7))" in SOURCE
    # The candidate trace validator must not demand PS3/PS35 on a menu-only walk.
    assert "else (9, 7, 5, 3) if new_game_start else (9, 7, 5) if new_game_path else (3, 9, 35)" in SOURCE


def test_new_game_option_is_candidate_scale2x_only_and_exclusive_with_census() -> None:
    assert '"--new-game-path"' in SOURCE
    assert 'parser.error("--new-game-path requires --hd-source scale2x")' in SOURCE
    assert 'parser.error("--new-game-path cannot be combined with --census-only")' in SOURCE


class _Recorder:
    def __init__(self, states: list[int]) -> None:
        self.states = states
        self.clicks: list[tuple[int, int]] = []

    def state(self, pid: int, detailed: bool) -> dict:
        return {"ps": self.states.pop(0) if len(self.states) > 1 else self.states[0]}


def test_click_until_state_retries_only_while_still_in_the_previous_state(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _Recorder([9, 7])
    monkeypatch.setattr(probe.runtime_driver, "state", recorder.state)
    monkeypatch.setattr(probe, "_inject", lambda display, origin, point, scale, env, log, **kw: (
        recorder.clicks.append(point) or {"point": list(point)}))
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: None)
    result = probe._click_until_state(
        1, "d", (0, 0), probe.NEW_GAME_MENU, 2, {}, None, from_ps=9, to_ps=7)
    assert recorder.clicks == [(184, 560), (184, 560)]  # still PS9 after 1s -> one retry
    assert result["to"]["ps"] == 7


def test_click_until_state_does_not_resend_after_the_transition(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _Recorder([7])
    monkeypatch.setattr(probe.runtime_driver, "state", recorder.state)
    monkeypatch.setattr(probe, "_inject", lambda display, origin, point, scale, env, log, **kw: (
        recorder.clicks.append(point) or {"point": list(point)}))
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: None)
    result = probe._click_until_state(
        1, "d", (0, 0), probe.NEW_GAME_CONFIRM, 1, {}, None, from_ps=9, to_ps=7)
    assert recorder.clicks == [(608, 564)]
    assert len(result["clicks"]) == 1


def test_new_game_start_option_requires_the_new_game_path() -> None:
    assert '"--new-game-start"' in SOURCE
    assert 'parser.error("--new-game-start requires --new-game-path")' in SOURCE
    assert "new_game_start=args.new_game_start" in SOURCE


def test_new_game_start_adds_ps3_to_the_required_candidate_states() -> None:
    assert "else (9, 7, 5, 3) if new_game_start else (9, 7, 5)" in SOURCE
    assert "start_game=new_game_start" in SOURCE


def test_new_game_summary_gates_on_the_scale2x_validator() -> None:
    assert 'lanes["candidate"].get("scale2x_validator", {}).get("status") == "PASS"' in SOURCE
    assert '"new_game_start"' in SOURCE  # published in the summary lane fields


def _start_recorder(monkeypatch: pytest.MonkeyPatch, states: list[int]) -> _Recorder:
    recorder = _Recorder(states)
    monkeypatch.setattr(probe.runtime_driver, "state", recorder.state)
    monkeypatch.setattr(probe, "_inject", lambda display, origin, point, scale, env, log, **kw: (
        recorder.clicks.append(point) or {"point": list(point)}))
    monkeypatch.setattr(probe, "_wait_state", lambda pid, predicate, label, **kw: {"ps": 3, "tick": 5})
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: None)
    return recorder


def test_start_new_game_does_not_click_when_the_solo_lobby_auto_starts(monkeypatch: pytest.MonkeyPatch) -> None:
    recorder = _start_recorder(monkeypatch, [5, 2])
    result = probe._start_new_game(1, "d", (0, 0), 2, {}, None)
    assert recorder.clicks == []
    assert result["clicks"] == []
    assert result["to"]["ps"] == 3


def _lobby_after_clicks(monkeypatch: pytest.MonkeyPatch, clicks_needed: int | None) -> list[tuple[int, int]]:
    """PS5 until ``clicks_needed`` confirm clicks arrived (never when None), then PS2; the clock advances 3 s per read."""
    clicks: list[tuple[int, int]] = []
    monkeypatch.setattr(probe.runtime_driver, "state", lambda pid, detailed: {
        "ps": 2 if clicks_needed is not None and len(clicks) >= clicks_needed else 5})
    monkeypatch.setattr(probe, "_inject", lambda display, origin, point, scale, env, log, **kw: (
        clicks.append(point) or {"point": list(point)}))
    monkeypatch.setattr(probe, "_wait_state", lambda pid, predicate, label, **kw: {"ps": 3, "tick": 5})
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: None)
    ticks = iter(range(0, 100000, 3))
    monkeypatch.setattr(probe.time, "monotonic", lambda: float(next(ticks)))
    return clicks


def test_start_new_game_clicks_once_when_the_first_click_starts_the_game(monkeypatch: pytest.MonkeyPatch) -> None:
    clicks = _lobby_after_clicks(monkeypatch, 1)
    result = probe._start_new_game(1, "d", (0, 0), 2, {}, None)
    assert clicks == [(608, 564)]  # PS2 reached after the first click: no second click
    assert len(result["clicks"]) == 1


def test_start_new_game_reclicks_while_the_lobby_stays_in_ps5(monkeypatch: pytest.MonkeyPatch) -> None:
    """H-E2611G1-2 E2-0: lap1184 K1 / lap1219 C1 lost the one confirm click (down->up 1-11 ms), so retry while still PS5."""
    clicks = _lobby_after_clicks(monkeypatch, 2)
    result = probe._start_new_game(1, "d", (0, 0), 2, {}, None)
    assert clicks == [(608, 564), (608, 564)]
    assert len(result["clicks"]) == 2 and result["to"]["ps"] == 3


def test_start_new_game_records_each_click_result_as_returned_by_inject(monkeypatch: pytest.MonkeyPatch) -> None:
    clicks = _lobby_after_clicks(monkeypatch, 2)
    monkeypatch.setattr(probe, "_inject", lambda display, origin, point, scale, env, log, **kw: (
        clicks.append(point) or {"point": list(point), "n": len(clicks)}))
    result = probe._start_new_game(1, "d", (0, 0), 2, {}, None)
    assert result["clicks"] == [{"point": [608, 564], "n": 1}, {"point": [608, 564], "n": 2}]


def test_start_new_game_stops_reclicking_after_three_confirm_clicks(monkeypatch: pytest.MonkeyPatch) -> None:
    clicks = _lobby_after_clicks(monkeypatch, None)
    result = probe._start_new_game(1, "d", (0, 0), 2, {}, None)
    assert len(clicks) == probe.NEW_GAME_CONFIRM_MAX_CLICKS == 3
    assert len(result["clicks"]) == 3


def test_start_new_game_waits_the_retry_gap_between_confirm_clicks(monkeypatch: pytest.MonkeyPatch) -> None:
    """The gap between clicks must be >= 4 s of game clock, not back-to-back."""
    clicks = _lobby_after_clicks(monkeypatch, None)
    stamps: list[float] = []
    clock = iter(range(0, 100000, 1))
    monkeypatch.setattr(probe.time, "monotonic", lambda: float(next(clock)))
    monkeypatch.setattr(probe, "_inject", lambda display, origin, point, scale, env, log, **kw: (
        stamps.append(probe.time.monotonic()) or clicks.append(point) or {"point": list(point)}))
    probe._start_new_game(1, "d", (0, 0), 2, {}, None)
    assert probe.NEW_GAME_CONFIRM_RETRY_GAP >= 4.0
    assert all(later - earlier >= probe.NEW_GAME_CONFIRM_RETRY_GAP for earlier, later in zip(stamps, stamps[1:]))


def test_new_game_play_option_requires_new_game_start() -> None:
    assert '"--new-game-play"' in SOURCE
    assert 'parser.error("--new-game-play requires --new-game-start")' in SOURCE


def test_new_game_play_gates_the_summary_and_threads_into_the_walk() -> None:
    assert "new_game_play=args.new_game_play" in SOURCE
    assert 'lane.get("new_game_play", {}).get("status") == "PASS" for lane in lanes.values()' in SOURCE
    assert "start_game=new_game_start, play=new_game_play, read_camera=" in SOURCE


def _play_recorder(monkeypatch: pytest.MonkeyPatch, cameras: list[list[int]]) -> dict:
    record: dict = {"edges": [], "sleeps": [], "lines": 0}
    queue = list(cameras)
    monkeypatch.setattr(probe, "_send_key_edge", lambda display, env, key, *, down: (
        record["edges"].append((key, down)) or 1))
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: record["sleeps"].append(seconds))

    def count(path: Path) -> int:
        record["lines"] += 10
        return record["lines"]

    monkeypatch.setattr(probe, "_trace_line_count", count)
    record["read_camera"] = lambda: queue.pop(0)
    return record


def test_new_game_play_window_holds_four_directions_then_dwells(monkeypatch: pytest.MonkeyPatch) -> None:
    # RIGHT (+,-), DOWN (+,+), LEFT (-,+), UP (-,-): camera moves along each key's signs.
    cameras = [[10, 10], [13, 7], [13, 7], [16, 10], [16, 10], [12, 14], [12, 14], [8, 10], [8, 10]]
    record = _play_recorder(monkeypatch, cameras)
    result = probe._new_game_play_window(
        display=":9", env={}, read_camera=record["read_camera"], trace_path=Path("t.jsonl"))
    assert record["edges"] == [("RIGHT", True), ("RIGHT", False), ("DOWN", True), ("DOWN", False),
                               ("LEFT", True), ("LEFT", False), ("UP", True), ("UP", False)]
    assert [seg["key"] for seg in result["segments"]] == ["RIGHT", "DOWN", "LEFT", "UP"]
    assert [seg["steps"] for seg in result["segments"]] == [3, 3, 4, 4]
    assert all(seg["moved"] for seg in result["segments"])
    assert result["status"] == "PASS"
    assert record["sleeps"].count(2.0) == 4
    assert 60.0 in record["sleeps"]
    assert [w["name"] for w in result["windows"]] == [
        "scroll_RIGHT", "scroll_DOWN", "scroll_LEFT", "scroll_UP", "dwell"]
    assert all(w["line_end"] >= w["line_start"] for w in result["windows"])


def test_new_game_play_window_takes_keys_hold_and_dwell_from_the_long_run_override(monkeypatch: pytest.MonkeyPatch) -> None:
    cameras = [[10, 10], [13, 7], [13, 7], [16, 10], [16, 10], [19, 7], [19, 7], [22, 10], [22, 10]]
    record = _play_recorder(monkeypatch, cameras)
    monkeypatch.setitem(probe.NEW_GAME_PLAY_OVERRIDE, "keys", ("RIGHT", "DOWN", "RIGHT", "DOWN"))
    monkeypatch.setitem(probe.NEW_GAME_PLAY_OVERRIDE, "hold", 15.0)
    monkeypatch.setitem(probe.NEW_GAME_PLAY_OVERRIDE, "dwell", 120.0)
    result = probe._new_game_play_window(
        display=":9", env={}, read_camera=record["read_camera"], trace_path=Path("t.jsonl"))
    assert [seg["key"] for seg in result["segments"]] == ["RIGHT", "DOWN", "RIGHT", "DOWN"]
    assert record["sleeps"].count(15.0) == 4 and 120.0 in record["sleeps"] and 2.0 not in record["sleeps"]


def test_new_game_play_long_run_options_require_play_and_validate_their_values() -> None:
    for option in ("--new-game-play-keys", "--new-game-play-hold", "--new-game-play-dwell"):
        assert f'"{option}"' in SOURCE
    assert 'parser.error("--new-game-play-keys/-hold/-dwell require --new-game-play")' in SOURCE
    assert "must list keys from" in SOURCE and "must be >= 0" in SOURCE


def test_new_game_play_window_fails_when_a_key_does_not_move_the_camera(monkeypatch: pytest.MonkeyPatch) -> None:
    cameras = [[10, 10], [10, 10], [10, 10], [13, 13], [13, 13], [10, 16], [10, 16], [7, 13], [7, 13]]
    record = _play_recorder(monkeypatch, cameras)
    result = probe._new_game_play_window(
        display=":9", env={}, read_camera=record["read_camera"], trace_path=Path("t.jsonl"))
    assert result["segments"][0]["moved"] is False
    assert result["status"] == "FAIL"


def _present(seq: int, covered: int = 480000, stale: int = 0, **extra) -> str:
    row = {"seq": seq, "event": "mirror2x_present", "program_state": 3, "covered_pixels": covered,
           "stale_pixels": stale, "hd_mask_outside_diff_subpixels": 0, "fallback": 0, "success": 1,
           "elapsed_ms": 7, **extra}
    return json.dumps(row)


def test_play_present_summary_reports_hd_and_passes_a_clean_window(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    lines = [_present(1)] + [_present(i, stale=4800) for i in range(2, 6)] + [_present(6)]
    trace.write_text("\n".join(lines) + "\n")
    out = probe._summarize_play_presents(trace, [{"name": "dwell", "line_start": 1, "line_end": 6}])
    dwell = out["windows"]["dwell"]
    assert dwell["presents"] == 5
    assert dwell["hd_min"] == pytest.approx(99.0)
    assert dwell["below_986"] == 0
    assert dwell["below_90"] == 0
    assert out["status"] == "PASS"


def test_play_present_summary_fails_below_90_percent_and_on_safety_counters(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    trace.write_text("\n".join([_present(1), _present(2, stale=100000),
                                _present(3, hd_mask_outside_diff_subpixels=4)]) + "\n")
    out = probe._summarize_play_presents(trace, [{"name": "dwell", "line_start": 0, "line_end": 3}])
    dwell = out["windows"]["dwell"]
    assert dwell["below_90"] == 1
    assert dwell["below_986_list"][0]["seq"] == 2
    assert dwell["v1_outside_max"] == 4
    assert out["status"] == "FAIL"


def test_play_present_summary_fails_a_window_with_no_ps3_presents(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    trace.write_text(_present(1, program_state=5) + "\n")
    out = probe._summarize_play_presents(trace, [{"name": "dwell", "line_start": 0, "line_end": 1}])
    assert out["windows"]["dwell"]["presents"] == 0
    assert out["status"] == "FAIL"


def test_new_game_act_option_requires_new_game_start_and_gates_the_summary() -> None:
    assert '"--new-game-act"' in SOURCE
    assert 'parser.error("--new-game-act requires --new-game-start")' in SOURCE
    assert "new_game_act=args.new_game_act" in SOURCE
    assert 'lane.get("new_game_act", {}).get("status") == "PASS" for lane in lanes.values()' in SOURCE
    assert "act=new_game_act, read_selection=" in SOURCE


class _ActGame:
    """Fake game: a click selects, the produce click spends rice, a right click moves the selection."""

    def __init__(self, *, select_after: int = 1, spend: bool = True, move: bool = True) -> None:
        self.clicks: list[tuple[tuple[int, int], dict]] = []
        self.select_after = select_after
        self.spend = spend
        self.move = move
        self.count = 0
        self.slot: int | None = None
        self.rice = 5000
        self.pos = (10, 10)
        self.first_clicks = 0

    def inject(self, point: tuple[int, int], **kw) -> dict:
        self.clicks.append((point, kw))
        if kw.get("button") == 3:
            self.pos = (12, 14) if self.move else self.pos
        elif kw.get("drag_to") is not None:
            self.count, self.slot = 2, 7
        elif point in probe.NEW_GAME_ACT_PRODUCE:
            self.rice = 4950 if self.spend else self.rice
        else:
            self.first_clicks += 1
            if self.first_clicks >= self.select_after:
                self.count, self.slot = 1, 7 if point == probe.NEW_GAME_ACT_FARMER else 9
        return {}

    def state(self) -> dict:
        return {"players": [{"owner": 0, "rice": self.rice, "wood": 5000, "used": 20}],
                "units": [{"slot": 7, "owner": 0, "x": self.pos[0], "y": self.pos[1]}]}

    def selection(self) -> dict:
        return {"count": self.count, "selected_slot": self.slot,
                "selected_slots": [7, 8] if self.count == 2 else ([self.slot] if self.count else [])}


def _run_act(monkeypatch: pytest.MonkeyPatch, game: _ActGame) -> tuple[dict, list[float]]:
    sleeps: list[float] = []
    clock = {"now": 0.0}
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: (sleeps.append(seconds),
                                                              clock.__setitem__("now", clock["now"] + seconds)))
    monkeypatch.setattr(probe.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: len(sleeps))
    result = probe._new_game_act_window(
        inject=game.inject, read_state=game.state, read_selection=game.selection, trace_path=Path("t.jsonl"))
    return result, sleeps


def test_new_game_act_window_selects_produces_moves_then_dwells(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _ActGame()
    result, sleeps = _run_act(monkeypatch, game)
    assert result["status"] == "PASS"
    assert [w["name"] for w in result["windows"]] == ["select", "produce", "drag_move", "dwell"]
    assert result["actions"]["select"]["effect"] is True
    assert result["actions"]["produce"]["effect"] is True
    assert result["actions"]["produce"]["rice"] == [5000, 4950]
    assert result["actions"]["drag_move"]["drag"]["effect"] is True
    assert result["actions"]["drag_move"]["move"]["effect"] is True
    assert probe.NEW_GAME_ACT_DWELL_SECONDS in sleeps
    assert game.clicks[0][0] == probe.NEW_GAME_ACT_FARMER
    assert game.clicks[-1][1] == {"button": 3}


def test_new_game_act_window_retries_the_farmer_click_once(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _ActGame(select_after=2)
    result, _ = _run_act(monkeypatch, game)
    assert [c[0] for c in game.clicks[:2]] == [probe.NEW_GAME_ACT_FARMER, probe.NEW_GAME_ACT_FARMER_RETRY]
    assert result["actions"]["select"]["point"] == list(probe.NEW_GAME_ACT_FARMER_RETRY)
    assert result["status"] == "PASS"


def test_new_game_act_window_fails_without_a_selection_effect(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _ActGame(select_after=99)
    result, _ = _run_act(monkeypatch, game)
    assert result["actions"]["select"]["effect"] is False
    assert result["status"] == "FAIL"


def test_new_game_act_window_passes_on_move_when_production_has_no_effect(monkeypatch: pytest.MonkeyPatch) -> None:
    result, _ = _run_act(monkeypatch, _ActGame(spend=False))
    assert result["actions"]["produce"]["effect"] is False
    assert result["actions"]["drag_move"]["move"]["effect"] is True
    assert result["status"] == "PASS"


def test_new_game_act_window_fails_when_neither_production_nor_move_has_an_effect(
        monkeypatch: pytest.MonkeyPatch) -> None:
    result, _ = _run_act(monkeypatch, _ActGame(spend=False, move=False))
    assert result["status"] == "FAIL"


def test_trace_dropped_count_reads_the_final_summary_event(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    trace.write_text("\n".join([json.dumps({"event": "summary", "dropped_count": 0}),
                                json.dumps({"event": "textout_iat_restore"})]) + "\n")
    assert probe._trace_dropped_count(trace) == 0
    trace.write_text(json.dumps({"event": "summary", "dropped_count": 12}) + "\n")
    assert probe._trace_dropped_count(trace) == 12
    trace.write_text(json.dumps({"event": "mirror2x_present"}) + "\n")
    assert probe._trace_dropped_count(trace) is None
    assert probe._trace_dropped_count(tmp_path / "missing.jsonl") is None


def test_new_game_act_run_gates_the_candidate_on_trace_dropped_count() -> None:
    assert '_trace_dropped_count(trace_copy)' in SOURCE
    assert 'result["new_game_act"]["status"] = "FAIL"' in SOURCE


def test_new_game_menu_option_requires_new_game_start_and_gates_the_summary() -> None:
    assert '"--new-game-menu"' in SOURCE
    assert 'parser.error("--new-game-menu requires --new-game-start")' in SOURCE
    assert "new_game_menu=args.new_game_menu" in SOURCE
    assert 'lane.get("new_game_menu", {}).get("status") == "PASS" for lane in lanes.values()' in SOURCE
    assert "menu=new_game_menu, read_ps=" in SOURCE
    assert 'result["new_game_menu"]["status"] = "FAIL"' in SOURCE


class _MenuGame:
    """Fake game: Esc opens the pause menu (PS23), the save click opens a save window, return/resume step back."""

    def __init__(self, *, esc_works_after: int = 1, save_state: int = 23, resume_works: bool = True) -> None:
        self.ps = 3
        self.keys: list[str] = []
        self.clicks: list[tuple[int, int]] = []
        self.esc_works_after = esc_works_after
        self.save_state = save_state
        self.resume_works = resume_works
        self.in_save = False

    def send_key(self, key: str) -> None:
        self.keys.append(key)
        if key == "ESC" and self.ps == 3 and len(self.keys) >= self.esc_works_after:
            self.ps = 23

    def inject(self, point: tuple[int, int], **kw) -> dict:
        self.clicks.append(point)
        if point == probe.PAUSE_SAVE_POINT and self.ps == 23 and not self.in_save:
            self.ps, self.in_save = self.save_state, True
        elif point == probe.SAVE_MENU_RETURN_POINT and self.in_save:
            self.ps, self.in_save = 23, False
        elif point == probe.RESUME_POINT and self.ps == 23 and self.resume_works:
            self.ps = 3
        return {}

    def read_ps(self) -> int:
        return self.ps


def _run_menu(monkeypatch: pytest.MonkeyPatch, game: _MenuGame) -> tuple[dict, list[float], list[str]]:
    sleeps: list[float] = []
    captures: list[str] = []
    clock = {"now": 0.0}
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: (sleeps.append(seconds),
                                                              clock.__setitem__("now", clock["now"] + seconds)))
    monkeypatch.setattr(probe.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: len(sleeps))
    result = probe._new_game_menu_window(
        inject=game.inject, send_key=game.send_key, read_ps=game.read_ps, trace_path=Path("t.jsonl"),
        capture=captures.append)
    return result, sleeps, captures


def test_new_game_menu_window_opens_saves_returns_and_resumes(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _MenuGame(save_state=31)
    result, sleeps, captures = _run_menu(monkeypatch, game)
    assert result["status"] == "PASS"
    assert [w["name"] for w in result["windows"]] == ["pause", "save_window", "pause_return", "resume"]
    assert captures == ["pause", "save_window", "pause_return", "ps3_resume"]
    assert game.clicks == [probe.PAUSE_SAVE_POINT, probe.SAVE_MENU_RETURN_POINT, probe.RESUME_POINT]
    assert probe.SAVE_ACTION_POINT not in game.clicks
    assert result["states"] == {"pause": 23, "save_window": 31, "pause_return": 23, "resume": 3}
    assert result["save_state_changed"] is True
    assert sleeps.count(probe.NEW_GAME_MENU_DWELL_SECONDS) == 4


def test_new_game_menu_window_discloses_a_save_window_that_keeps_ps23(monkeypatch: pytest.MonkeyPatch) -> None:
    result, _, _ = _run_menu(monkeypatch, _MenuGame(save_state=23))
    assert result["status"] == "PASS"
    assert result["save_state_changed"] is False


def test_new_game_menu_window_retries_escape_once_after_a_focus_click(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _MenuGame(esc_works_after=2)
    result, _, _ = _run_menu(monkeypatch, game)
    assert game.keys == ["ESC", "ESC"]
    assert game.clicks[0] == probe.NEW_GAME_MENU_FOCUS_POINT
    assert result["status"] == "PASS"
    assert result["escape_attempts"] == 2


def test_new_game_menu_window_is_blocked_when_escape_never_opens_the_menu(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _MenuGame(esc_works_after=99)
    result, _, captures = _run_menu(monkeypatch, game)
    assert result["status"] == "BLOCKED"
    assert result["states"]["pause"] == 3
    assert game.keys == ["ESC", "ESC"]
    assert captures == []


def test_new_game_menu_window_fails_when_resume_does_not_return_to_ps3(monkeypatch: pytest.MonkeyPatch) -> None:
    result, _, _ = _run_menu(monkeypatch, _MenuGame(resume_works=False))
    assert result["status"] == "FAIL"
    assert result["states"]["resume"] == 23


class _SubWindowGame(_MenuGame):
    """_MenuGame plus the load (button 불러오기) and options (환경설정) sub windows of the pause menu."""

    def __init__(self, *, options_close_by_click: bool = False, load_state: int = 23,
                 options_state: int = 23, **kw) -> None:
        super().__init__(**kw)
        self.sub: str | None = None
        self.load_state = load_state
        self.options_state = options_state
        self.options_close_by_click = options_close_by_click

    def send_key(self, key: str) -> None:
        if key == "ESC" and self.sub == "options":
            self.keys.append(key)
            self.sub, self.ps = None, 23
            return
        super().send_key(key)

    def inject(self, point: tuple[int, int], **kw) -> dict:
        if self.ps == 23 and self.sub is None and not self.in_save:
            if point == probe.PAUSE_SUB_WINDOWS["load"]["open"]:
                self.clicks.append(point)
                self.sub, self.ps = "load", self.load_state
                return {}
            if point == probe.PAUSE_SUB_WINDOWS["options"]["open"]:
                self.clicks.append(point)
                self.sub, self.ps = "options", self.options_state
                return {}
        if self.sub == "load" and point == probe.PAUSE_SUB_WINDOWS["load"]["close"]:
            self.clicks.append(point)
            self.sub, self.ps = None, 23
            return {}
        return super().inject(point, **kw)


def _run_subs(monkeypatch: pytest.MonkeyPatch, game: _MenuGame, subs: tuple[str, ...]) -> tuple[dict, list[str]]:
    clock = {"now": 0.0}
    captures: list[str] = []
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: clock.__setitem__("now", clock["now"] + seconds))
    monkeypatch.setattr(probe.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: 0)
    result = probe._new_game_menu_window(
        inject=game.inject, send_key=game.send_key, read_ps=game.read_ps, trace_path=Path("t.jsonl"),
        capture=captures.append, subs=subs)
    return result, captures


def test_new_game_menu_window_without_subs_keeps_the_save_only_window_list(monkeypatch: pytest.MonkeyPatch) -> None:
    result, captures = _run_subs(monkeypatch, _SubWindowGame(), ())
    assert [w["name"] for w in result["windows"]] == ["pause", "save_window", "pause_return", "resume"]
    assert captures == ["pause", "save_window", "pause_return", "ps3_resume"]


def test_new_game_menu_sub_walk_dwells_shorter_to_fit_the_trace_buffer(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []
    clock = {"now": 0.0}
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: (sleeps.append(seconds),
                                                              clock.__setitem__("now", clock["now"] + seconds)))
    monkeypatch.setattr(probe.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: 0)
    game = _SubWindowGame()
    probe._new_game_menu_window(inject=game.inject, send_key=game.send_key, read_ps=game.read_ps,
                                trace_path=Path("t.jsonl"), capture=lambda name: None, subs=("load", "options"))
    assert sleeps.count(probe.NEW_GAME_MENU_SUBS_DWELL_SECONDS) == 8
    assert probe.NEW_GAME_MENU_DWELL_SECONDS not in sleeps
    assert probe.NEW_GAME_MENU_SUBS_DWELL_SECONDS < probe.NEW_GAME_MENU_DWELL_SECONDS


def test_new_game_menu_window_walks_the_load_and_options_sub_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _SubWindowGame()
    result, captures = _run_subs(monkeypatch, game, ("load", "options"))
    assert result["status"] == "PASS"
    assert [w["name"] for w in result["windows"]] == [
        "pause", "save_window", "pause_return", "load_window", "pause_return_load",
        "options_window", "pause_return_options", "resume"]
    assert captures == ["pause", "save_window", "pause_return", "load_window", "pause_return_load",
                        "options_window", "pause_return_options", "ps3_resume"]
    assert result["sub_close"] == {"load": "click", "options": "esc"}
    assert result["states"]["pause_return_load"] == 23 and result["states"]["pause_return_options"] == 23


def test_new_game_menu_sub_windows_never_click_an_action_or_an_options_point(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _SubWindowGame()
    _run_subs(monkeypatch, game, ("load", "options"))
    assert probe.SAVE_ACTION_POINT not in game.clicks and probe.LOAD_CONFIRM not in game.clicks
    assert game.clicks == [probe.PAUSE_SAVE_POINT, probe.SAVE_MENU_RETURN_POINT,
                           probe.PAUSE_SUB_WINDOWS["load"]["open"], probe.PAUSE_SUB_WINDOWS["load"]["close"],
                           probe.PAUSE_SUB_WINDOWS["options"]["open"], probe.RESUME_POINT]
    assert game.keys == ["ESC", "ESC"]


def test_new_game_menu_sub_window_that_leaves_ps23_is_recorded_with_its_state(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _SubWindowGame(load_state=31)
    result, _ = _run_subs(monkeypatch, game, ("load",))
    assert result["states"]["load_window"] == 31
    assert result["states"]["pause_return_load"] == 23
    assert result["status"] == "PASS"


def test_new_game_menu_sub_window_that_never_returns_fails_and_stops_the_walk(monkeypatch: pytest.MonkeyPatch) -> None:
    class Stuck(_SubWindowGame):
        def inject(self, point, **kw):
            if self.sub == "load" and point == probe.PAUSE_SUB_WINDOWS["load"]["close"]:
                self.clicks.append(point)
                return {}
            return super().inject(point, **kw)

    result, captures = _run_subs(monkeypatch, Stuck(load_state=31), ("load", "options"))
    assert result["status"] == "FAIL"
    assert "options_window" not in [w["name"] for w in result["windows"]]
    assert result["sub_close"]["load"] == "none"


def test_new_game_menu_subs_option_is_validated_and_wired() -> None:
    assert '"--new-game-menu-subs"' in SOURCE
    assert "new_game_menu_subs=" in SOURCE
    assert "subs=new_game_menu_subs" in SOURCE
    assert 'parser.error("--new-game-menu-subs requires --new-game-menu")' in SOURCE
    assert probe.parse_menu_subs("") == ()
    assert probe.parse_menu_subs("load,options") == ("load", "options")
    with pytest.raises(ValueError):
        probe.parse_menu_subs("load,save")


def _mirror_row(seq: int, state: int, **extra) -> str:
    row = {"event": "mirror2x_present", "seq": seq, "program_state": state, "covered_pixels": 480_000,
           "stale_pixels": 0, "elapsed_ms": 5, "fallback": 0, "success": 1}
    row.update(extra)
    return json.dumps(row)


def test_menu_present_summary_counts_every_program_state(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    trace.write_text("\n".join([_mirror_row(1, 3, menu_copy_calls=0, frame_copy_rejects=0),
                                _mirror_row(2, 23, menu_copy_calls=2, frame_copy_rejects=0),
                                _mirror_row(3, 23, menu_copy_calls=7, frame_copy_rejects=1)]) + "\n")
    window = [{"name": "pause", "line_start": 0, "line_end": 3}]
    only_ps3 = probe._summarize_play_presents(trace, window)
    assert only_ps3["windows"]["pause"]["presents"] == 1
    every = probe._summarize_play_presents(trace, window, program_state=None)
    summary = every["windows"]["pause"]
    assert every["status"] == "PASS"
    assert summary["presents"] == 3
    assert summary["by_state"] == {"3": 1, "23": 2}
    assert summary["counter_span"]["menu_copy_calls"] == 7
    assert summary["counter_span"]["frame_copy_rejects"] == 1


def test_menu_present_summary_fails_a_window_without_mirror_presents(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    trace.write_text(_mirror_row(1, 3) + "\n")
    result = probe._summarize_play_presents(
        trace, [{"name": "save_window", "line_start": 1, "line_end": 1}], program_state=None)
    assert result["status"] == "FAIL"


# --- H-TM0: title menu buttons (scenario / user / charroom / prologue) -------------------------------------


def test_title_button_points_are_the_unmeasured_menu_buttons() -> None:
    assert probe.TITLE_BUTTONS == {
        "scenario": (75, 505), "user": (190, 505), "charroom": (410, 505), "prologue": (75, 560),
        "quit": (410, 560)}
    # The measured and the excluded buttons are never offered.
    assert probe.LOAD_MENU not in probe.TITLE_BUTTONS.values()
    assert probe.NEW_GAME_MENU not in probe.TITLE_BUTTONS.values()
    assert (302, 560) not in probe.TITLE_BUTTONS.values()  # HQNET: external connection
    assert probe.TITLE_BUTTON_SINGLE_CLICK == {"quit"}


class _TitleGame:
    """Fake title menu: a click moves PS9 to ``target`` after ``lag`` seconds, then follows ``after``."""

    def __init__(self, clock: dict, *, target: int | None = 14, lag: float = 0.5,
                 after: tuple[tuple[float, int], ...] = ()) -> None:
        self.clock, self.target, self.lag, self.after = clock, target, lag, after
        self.clicks: list[tuple[int, int]] = []
        self.click_at: float | None = None

    def inject(self, point: tuple[int, int], **kw) -> dict:
        self.clicks.append(point)
        if self.click_at is None and self.target is not None:
            self.click_at = self.clock["now"]
        return {}

    def read_ps(self) -> int:
        if self.click_at is None:
            return 9
        elapsed = self.clock["now"] - self.click_at
        if elapsed < self.lag:
            return 9
        state = self.target
        for at, ps in self.after:
            if elapsed >= at:
                state = ps
        return state


def _run_title(monkeypatch: pytest.MonkeyPatch, make_game, button: str = "scenario"):
    clock = {"now": 0.0}
    captures: list[str] = []
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: clock.__setitem__("now", clock["now"] + seconds))
    monkeypatch.setattr(probe.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: int(clock["now"] * 10))
    game = make_game(clock)
    result = probe._title_button_window(
        inject=game.inject, read_ps=game.read_ps, trace_path=Path("t.jsonl"), capture=captures.append,
        button=button)
    return result, game, captures, clock


def test_title_button_window_clicks_once_records_the_state_column_and_captures_twice(
        monkeypatch: pytest.MonkeyPatch) -> None:
    result, game, captures, _ = _run_title(
        monkeypatch, lambda clock: _TitleGame(clock, target=14, lag=0.4, after=((6.0, 15),)), "user")
    assert result["status"] == "PASS"
    assert game.clicks == [probe.TITLE_BUTTONS["user"]]
    assert result["button"] == "user" and result["clicks"] == [list(probe.TITLE_BUTTONS["user"])]
    assert captures == ["user_3s", "user_8s"]
    assert result["first_state"] == 14
    assert [row["ps"] for row in result["states"]] == [14, 15]
    assert result["states"][0]["at"] == 0.0 and 4.5 <= result["states"][1]["at"] <= 6.5
    assert result["observed_seconds"] >= probe.TITLE_BUTTON_OBSERVE_SECONDS
    assert result["window"]["line_end"] > result["window"]["line_start"]


def test_title_button_window_retries_the_click_once_while_still_on_the_menu(
        monkeypatch: pytest.MonkeyPatch) -> None:
    class Lossy(_TitleGame):
        def inject(self, point, **kw):
            self.clicks.append(point)
            if len(self.clicks) == 2 and self.click_at is None:
                self.click_at = self.clock["now"]
            return {}

    result, game, _, _ = _run_title(monkeypatch, lambda clock: Lossy(clock, target=14, lag=0.0))
    assert result["status"] == "PASS"
    assert game.clicks == [probe.TITLE_BUTTONS["scenario"]] * 2


def test_title_button_window_is_in_place_when_the_menu_never_changes(monkeypatch: pytest.MonkeyPatch) -> None:
    result, game, captures, clock = _run_title(monkeypatch, lambda clock: _TitleGame(clock, target=None))
    assert result["status"] == "IN_PLACE"
    assert "PS9" in result["reason"]
    assert len(game.clicks) == 2  # one retry only, never a third click
    assert captures == ["scenario_inplace_a", "scenario_inplace_b"]
    assert clock["now"] >= probe.TITLE_BUTTON_LEAVE_TIMEOUT


def test_title_button_window_does_not_retry_when_the_trace_shows_a_transient_state(
        monkeypatch: pytest.MonkeyPatch) -> None:
    # A movie attempt leaves PS9 for ~1 s; the poll can miss it, the trace does not.
    clock = {"now": 0.0}
    game = _TitleGame(clock, target=None)
    captures: list[str] = []
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: clock.__setitem__("now", clock["now"] + seconds))
    monkeypatch.setattr(probe.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: int(clock["now"] * 10))
    result = probe._title_button_window(
        inject=game.inject, read_ps=game.read_ps, trace_path=Path("t.jsonl"), capture=captures.append,
        button="prologue", trace_states=lambda line_start: [9, 30, 9])
    assert game.clicks == [probe.TITLE_BUTTONS["prologue"]]
    assert result["status"] == "PASS" and result["first_state"] == 30
    assert result["trace_states"] == [9, 30, 9]
    assert captures == ["prologue_3s", "prologue_8s"]


def test_trace_program_states_collapses_runs_and_skips_end_of_run_bookkeeping(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    rows = [{"event": "blt", "program_state": 9}, {"event": "blt", "program_state": 9},
            {"event": "set_display_mode", "program_state": 30}, {"event": "blt", "program_state": 9},
            {"event": "aggregate", "program_state": 15}, {"event": "summary", "program_state": 15},
            {"event": "blt"}]
    trace.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    assert probe._trace_program_states(trace, 0) == [9, 30, 9]
    assert probe._trace_program_states(trace, 3) == [9]
    assert probe._trace_program_states(tmp_path / "missing.jsonl", 0) == []


def test_title_button_window_keeps_the_first_non_menu_state_even_when_it_returns_to_the_menu(
        monkeypatch: pytest.MonkeyPatch) -> None:
    result, _, _, _ = _run_title(
        monkeypatch, lambda clock: _TitleGame(clock, target=14, lag=0.4, after=((2.0, 9),)))
    assert [row["ps"] for row in result["states"]] == [14, 9]
    assert result["status"] == "PASS"


def test_title_button_state_summary_splits_runs_modes_and_the_transition_present(tmp_path: Path) -> None:
    trace = tmp_path / "trace.jsonl"
    rows = [
        _mirror_row(1, 9),
        json.dumps({"event": "set_display_mode", "program_state": 14, "width": 640, "height": 480, "bpp": 16,
                    "forwarded_width": 640, "forwarded_height": 480, "forwarded_bpp": 16,
                    "native_2x_applied": 0}),
        _mirror_row(2, 14, stale_pixels=96_000),
        _mirror_row(3, 14, stale_pixels=4_800),
        _mirror_row(4, 14, stale_pixels=0, hd_mask_outside_diff_subpixels=0),
        _mirror_row(5, 15),
        _mirror_row(6, 14, stale_pixels=0),
    ]
    trace.write_text("\n".join(rows) + "\n")
    summary = probe._summarize_state_runs(trace, 1, len(rows))
    assert [(run["ps"], run["presents"]) for run in summary["runs"]] == [(14, 3), (15, 1), (14, 1)]
    first = summary["runs"][0]
    assert first["hd_first"] == 80.0  # the transition present is reported separately
    assert first["hd_min_after_first"] == 99.0 and first["stale_max"] == 96_000
    assert summary["runs"][1]["hd_min_after_first"] == 100.0  # single-present run falls back to its only value
    assert summary["modes"] == [{"ps": 14, "request": [640, 480, 16], "forwarded": [640, 480, 16],
                                 "native_2x_applied": 0}]
    assert summary["fallback_max"] == 0 and summary["success_min"] == 1
    assert set(summary["safety_max"]) == set(probe._PLAY_SAFETY_FIELDS)


def test_title_button_option_is_validated_and_wired() -> None:
    assert '"--title-button"' in SOURCE
    assert 'choices=tuple(TITLE_BUTTONS)' in SOURCE
    assert "title_button=args.title_button" in SOURCE
    assert 'parser.error("--title-button requires --hd-source scale2x")' in SOURCE
    assert "if title_button:" in SOURCE
    # It runs after the PS9 capture and before the load click, like the new-game walk.
    branch = SOURCE.index("if title_button:")
    assert SOURCE.index('if census and census_state == 9:') < branch < SOURCE.index(
        "load_clicks = [_inject(display, origin, LOAD_MENU")
    assert "validate_trace(trace_copy, required_states=(9,))" in SOURCE
    assert 'result["title_button"]["status"] = "FAIL"' in SOURCE
    assert "syw2plus.g1-title-button.v1" in SOURCE
    assert "state_sequences_match" in SOURCE
    assert 'finals["baseline"] == finals["candidate"]' in SOURCE
    assert "final_states_match" in SOURCE


def test_title_button_window_fast_poll_catches_a_state_shorter_than_the_slow_poll(
        monkeypatch: pytest.MonkeyPatch) -> None:
    class Blink(_TitleGame):
        def read_ps(self) -> int:
            elapsed = self.clock["now"] - (self.click_at if self.click_at is not None else self.clock["now"])
            return 150 if self.click_at is not None and 0.2 <= elapsed < 0.3 else 9

    result, game, _, _ = _run_title(monkeypatch, lambda clock: Blink(clock), "charroom")
    assert game.clicks == [probe.TITLE_BUTTONS["charroom"]]  # no second click: the blink was seen
    assert result["status"] == "PASS" and result["first_state"] == 150
    assert [row["ps"] for row in result["states"]] == [150, 9]


# --- H-TM2: quit button is clicked once and a vanished game is a result ------------------------------------


def test_title_button_quit_in_place_popup_is_never_clicked_a_second_time(
        monkeypatch: pytest.MonkeyPatch) -> None:
    result, game, captures, clock = _run_title(monkeypatch, lambda clock: _TitleGame(clock, target=None), "quit")
    assert result["status"] == "IN_PLACE"
    assert game.clicks == [probe.TITLE_BUTTONS["quit"]]  # a retry could hit the confirmation's yes/no
    assert result["clicks"] == [[410, 560]]
    assert captures == ["quit_inplace_a", "quit_inplace_b"]
    assert clock["now"] >= probe.TITLE_BUTTON_LEAVE_TIMEOUT


def test_title_button_quit_without_a_confirmation_is_classified_exited(monkeypatch: pytest.MonkeyPatch) -> None:
    class Closing(_TitleGame):
        def read_ps(self) -> int:
            if self.click_at is not None and self.clock["now"] - self.click_at >= 0.4:
                raise OSError(3, "read: no such process")
            return 9

    result, game, captures, clock = _run_title(monkeypatch, lambda clock: Closing(clock, target=14), "quit")
    assert result["status"] == "EXITED"
    assert game.clicks == [probe.TITLE_BUTTONS["quit"]] and captures == []
    assert result["states"] == [] and "gone" in result["reason"]
    assert clock["now"] < probe.TITLE_BUTTON_LEAVE_TIMEOUT


def test_title_button_vanished_game_still_raises_for_the_other_buttons(monkeypatch: pytest.MonkeyPatch) -> None:
    class Closing(_TitleGame):
        def read_ps(self) -> int:
            raise OSError(3, "read: no such process")

    with pytest.raises(OSError):
        _run_title(monkeypatch, lambda clock: Closing(clock), "scenario")


def test_title_button_summary_accepts_an_exited_window_with_fewer_captures() -> None:
    assert '("PASS", "IN_PLACE", "EXITED")' in SOURCE
    assert '(1 if windows[name].get("status") == "EXITED" else 3)' in SOURCE


# --- H-SC0: scenario chapter 1 start (PS15 시작하기 -> briefing / loading / in-game) -----------------------


class _ScenarioGame:
    """Fake scenario screen: PS15 until a click lands, then ``timeline`` ((seconds after the landed click, ps))."""

    def __init__(self, clock: dict, *, timeline: tuple[tuple[float, int], ...], lost_clicks: int = 0,
                 start_ps: int = 15) -> None:
        self.clock, self.timeline, self.lost, self.start_ps = clock, timeline, lost_clicks, start_ps
        self.clicks: list[tuple[int, int]] = []
        self.keys: list[str] = []
        self.landed_at: float | None = None

    def inject(self, point: tuple[int, int], **kw) -> dict:
        self.clicks.append(point)
        if len(self.clicks) > self.lost and self.landed_at is None:
            self.landed_at = self.clock["now"]
        return {}

    def send_key(self, key: str) -> None:
        self.keys.append(key)

    def read_ps(self) -> int:
        if self.landed_at is None:
            return self.start_ps
        elapsed = self.clock["now"] - self.landed_at
        state = self.start_ps
        for at, ps in self.timeline:
            if elapsed >= at:
                state = ps
        return state


def _run_scenario(monkeypatch: pytest.MonkeyPatch, game_for, **kw):
    clock = {"now": 0.0}
    captures: list[str] = []
    monkeypatch.setattr(probe.time, "sleep", lambda seconds: clock.__setitem__("now", clock["now"] + seconds))
    monkeypatch.setattr(probe.time, "monotonic", lambda: clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: int(clock["now"] * 10))
    game = game_for(clock)
    result = probe._scenario_start_window(
        inject=game.inject, read_ps=game.read_ps, trace_path=Path("t.jsonl"), capture=captures.append,
        send_key=game.send_key, **kw)
    return result, game, captures, clock


def test_scenario_start_point_is_the_start_button_and_never_the_leave_button() -> None:
    assert probe.SCENARIO_START == (605, 563)
    assert probe.SCENARIO_START != (722, 563)  # 나가기
    assert probe.SCENARIO_PS == 15


def test_scenario_start_clicks_once_and_captures_each_state_and_ps3_at_10_and_30_seconds(
        monkeypatch: pytest.MonkeyPatch) -> None:
    result, game, captures, clock = _run_scenario(
        monkeypatch, lambda c: _ScenarioGame(c, timeline=((0.3, 16), (5.0, 17), (20.0, 3))))
    assert result["status"] == "PASS"
    assert game.clicks == [probe.SCENARIO_START] and result["clicks"] == [list(probe.SCENARIO_START)]
    assert [row["ps"] for row in result["states"]][-3:] == [16, 17, 3]
    assert result["ps3_entered_after_seconds"] is not None
    assert captures[:2] == ["scenario_ps16", "scenario_ps17"]
    assert captures[-3:] == ["scenario_ps3", "scenario_ps3_10s", "scenario_ps3_30s"]
    assert result["ps3_held_seconds"] >= 30.0
    assert game.keys == []
    assert result["window"]["line_end"] > result["window"]["line_start"]


def test_scenario_start_retries_the_click_once_when_the_screen_never_changes(
        monkeypatch: pytest.MonkeyPatch) -> None:
    result, game, _, _ = _run_scenario(
        monkeypatch, lambda c: _ScenarioGame(c, timeline=((0.2, 3),), lost_clicks=1))
    assert result["status"] == "PASS"
    assert game.clicks == [probe.SCENARIO_START] * 2
    assert len(result["clicks"]) == 2


def test_scenario_start_never_clicks_a_third_time_and_is_in_place_when_ps15_stays(
        monkeypatch: pytest.MonkeyPatch) -> None:
    result, game, _, _ = _run_scenario(
        monkeypatch, lambda c: _ScenarioGame(c, timeline=(), lost_clicks=9))
    assert result["status"] == "IN_PLACE"
    assert len(game.clicks) == 2
    assert result["states"] == [] or [row["ps"] for row in result["states"]] == [15]


def test_scenario_start_without_ps3_ends_after_the_observation_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    result, _, _, clock = _run_scenario(
        monkeypatch, lambda c: _ScenarioGame(c, timeline=((0.3, 16),)), observe=40.0, esc_after=1e9)
    assert result["status"] == "PASS"
    assert result["ps3_entered_after_seconds"] is None
    assert [row["ps"] for row in result["states"]][-1] == 16
    assert 40.0 <= result["observed_seconds"] < 50.0


def test_scenario_start_sends_one_esc_when_a_non_game_state_sticks_for_60_seconds(
        monkeypatch: pytest.MonkeyPatch) -> None:
    result, game, _, _ = _run_scenario(
        monkeypatch, lambda c: _ScenarioGame(c, timeline=((0.3, 30),)), observe=90.0)
    assert game.keys == ["ESC"]
    assert result["escape_sent_at"] is not None and 59.0 <= result["escape_sent_at"] <= 64.0
    assert len(game.clicks) == 1


def test_scenario_start_requires_ps15_before_the_click(monkeypatch: pytest.MonkeyPatch) -> None:
    result, game, captures, _ = _run_scenario(
        monkeypatch, lambda c: _ScenarioGame(c, timeline=(), start_ps=9))
    assert result["status"] == "BLOCKED" and "PS15" in result["reason"]
    assert game.clicks == [] and captures == []


def test_scenario_start_vanished_game_is_exited(monkeypatch: pytest.MonkeyPatch) -> None:
    class Crashing(_ScenarioGame):
        def read_ps(self) -> int:
            if self.landed_at is not None and self.clock["now"] - self.landed_at > 3.0:
                raise OSError(3, "read: no such process")
            return super().read_ps()

    result, _, _, _ = _run_scenario(monkeypatch, lambda c: Crashing(c, timeline=((0.3, 16),)))
    assert result["status"] == "EXITED"
    assert [row["ps"] for row in result["states"]][-1] == 16


def test_scenario_start_option_is_validated_and_wired() -> None:
    assert '"--scenario-start"' in SOURCE
    assert 'parser.error("--scenario-start requires --title-button scenario")' in SOURCE
    assert "scenario_start=args.scenario_start" in SOURCE
    assert "_scenario_start_window(" in SOURCE
    assert 'window["scenario_start"]' in SOURCE
    assert 'result["title_button"]["scenario_start"]["trace_dropped_count"]' in SOURCE


def test_scenario_play_point_is_the_play_button_and_never_the_back_button() -> None:
    assert probe.SCENARIO_PLAY == (600, 548)  # 게임하기 (briefing PS20 capture: x1100..1300 y1062..1130 at 2x)
    assert probe.SCENARIO_BRIEFING_PS == 20
    assert probe.SCENARIO_PLAY[0] > 400  # 돌아가기 is the left button (~x200) and 다시보기 the middle one (~x400)


def test_scenario_play_clicks_the_play_button_after_the_briefing_dwell_and_then_watches_ps3(
        monkeypatch: pytest.MonkeyPatch) -> None:
    class Briefing(_ScenarioGame):
        """PS16 -> PS20 briefing until 게임하기 lands, then PS21 loading and PS3 8 s later."""

        play_landed: float | None = None

        def inject(self, point, **kw):
            if point == probe.SCENARIO_PLAY:
                self.clicks.append(point)
                self.play_landed = self.clock["now"]
                return {}
            return super().inject(point, **kw)

        def read_ps(self) -> int:
            if self.play_landed is not None:
                elapsed = self.clock["now"] - self.play_landed
                return 3 if elapsed >= 8.0 else 21
            return super().read_ps()

    result, game, captures, _ = _run_scenario(
        monkeypatch, lambda c: Briefing(c, timeline=((0.3, 16), (1.0, 20))), play=True)
    assert result["status"] == "PASS"
    assert game.clicks == [probe.SCENARIO_START, probe.SCENARIO_PLAY]
    assert result["play_clicks"] == [list(probe.SCENARIO_PLAY)]
    assert result["briefing_dwell_seconds"] >= probe.SCENARIO_BRIEFING_DWELL_SECONDS
    assert [row["ps"] for row in result["states"]] == [16, 20, 21, 3]
    assert "scenario_ps20_dwell" in captures
    assert captures[-3:] == ["scenario_ps3", "scenario_ps3_10s", "scenario_ps3_30s"]
    assert result["ps3_held_seconds"] >= 30.0


def test_scenario_play_retries_the_play_click_once_and_never_clicks_the_back_button(
        monkeypatch: pytest.MonkeyPatch) -> None:
    class Lossy(_ScenarioGame):
        def inject(self, point, **kw):
            self.clicks.append(point)
            if point == probe.SCENARIO_START:
                self.landed_at = self.clock["now"]
            elif len([c for c in self.clicks if c == probe.SCENARIO_PLAY]) == 2:
                self.play_at = self.clock["now"]
            return {}

        play_at: float | None = None

        def read_ps(self) -> int:
            if self.play_at is not None:
                return 3
            return super().read_ps()

    result, game, _, _ = _run_scenario(
        monkeypatch, lambda c: Lossy(c, timeline=((0.3, 20),)), play=True)
    assert result["status"] == "PASS"
    assert game.clicks == [probe.SCENARIO_START] + [probe.SCENARIO_PLAY] * 2
    assert all(point[0] > 400 for point in game.clicks)


def test_scenario_play_option_is_validated_and_wired() -> None:
    assert '"--scenario-play"' in SOURCE
    assert 'parser.error("--scenario-play requires --scenario-start")' in SOURCE
    assert "scenario_play=args.scenario_play" in SOURCE


def test_scenario_briefing_dwell_option_is_validated_and_wired() -> None:
    assert '"--scenario-briefing-dwell"' in SOURCE
    assert 'parser.error("--scenario-briefing-dwell requires --scenario-play")' in SOURCE
    assert "scenario_briefing_dwell=args.scenario_briefing_dwell" in SOURCE
    assert "briefing_dwell=scenario_briefing_dwell" in SOURCE


def test_scenario_play_honours_a_longer_briefing_dwell(monkeypatch: pytest.MonkeyPatch) -> None:
    class Briefing(_ScenarioGame):
        play_landed: float | None = None

        def inject(self, point, **kw):
            if point == probe.SCENARIO_PLAY:
                self.clicks.append(point)
                self.play_landed = self.clock["now"]
                return {}
            return super().inject(point, **kw)

        def read_ps(self) -> int:
            if self.play_landed is not None:
                return 3
            return super().read_ps()

    result, _, _, _ = _run_scenario(
        monkeypatch, lambda c: Briefing(c, timeline=((0.3, 20),)), play=True, briefing_dwell=50.0)
    assert 50.0 <= result["briefing_dwell_seconds"] < 52.0
