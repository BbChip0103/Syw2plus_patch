"""Contracts for the H-RS0 result-screen (PS29) HD measurement harness."""

import json
from pathlib import Path

import pytest

from tools import g1_saved_scene_probe as probe

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")
G7_SHA256 = "57872666b436a4620c21cc99ef7c22413809e49de80b401ae5f27aa2e14210b8"


def test_g7defeat_fixture_is_pinned_and_save006_save000_are_unchanged() -> None:
    assert probe.SAVE_FIXTURES["g7defeat"] == ("save001.dat", G7_SHA256, 2)
    assert probe.SAVE_FIXTURES["save006"] == (probe.SAVE_NAME, probe.SAVE_SHA256, probe.SAVE_INDEX)
    assert probe.SAVE_FIXTURES["save000"] == (probe.SAVE000_NAME, probe.SAVE000_SHA256, probe.SAVE000_INDEX)


def test_fixture_path_for_the_reference_fixtures_stays_in_the_reference_save_dir() -> None:
    assert probe._fixture_path("save006") == probe.FIXTURE_SOURCE / "save" / probe.SAVE_NAME
    assert probe._fixture_path("save000") == probe.FIXTURE_SOURCE / "save" / probe.SAVE000_NAME


def test_g7defeat_fixture_never_lives_in_the_read_only_reference_repo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(probe.G7DEFEAT_FIXTURE_ENV, raising=False)
    path = probe._fixture_path("g7defeat")
    assert path.name == "save001.dat"
    assert probe.FIXTURE_SOURCE.resolve() not in path.resolve().parents
    monkeypatch.setenv(probe.G7DEFEAT_FIXTURE_ENV, str(probe.FIXTURE_SOURCE / "save" / "save001.dat"))
    with pytest.raises(probe.ProbeError, match="reference repository"):
        probe._fixture_path("g7defeat")


def test_fixture_check_rejects_a_sha_mismatch(tmp_path: Path) -> None:
    bad = tmp_path / "save001.dat"
    bad.write_bytes(b"not the fixture")
    with pytest.raises(probe.ProbeError, match="fixture SHA mismatch"):
        probe._verify_fixture_file("g7defeat", bad)
    with pytest.raises(probe.ProbeError, match="fixture SHA mismatch"):
        probe._verify_fixture_file("g7defeat", tmp_path / "missing.dat")


def test_run_lane_copies_the_pinned_fixture_file_not_a_reference_save_path() -> None:
    assert "shutil.copy2(fixture_file, private_save)" in SOURCE
    assert "_verify_fixture_file(fixture, fixture_file)" in SOURCE
    assert 'fixture_root / "save" / save_name' not in SOURCE


def test_result_screen_option_needs_the_defeat_fixture_and_scene_actions_none() -> None:
    assert '"--result-screen"' in SOURCE
    assert 'parser.error("--result-screen requires --fixture g7defeat")' in SOURCE
    assert 'parser.error("--result-screen requires --hd-source scale2x")' in SOURCE
    assert "result_screen=True" in SOURCE
    assert "_result_screen_window(" in SOURCE
    assert "required_states=(9, 35, 3, 29) if result_screen" in SOURCE


class _ResultGame:
    """Fake game: PS3 -> PS27 -> PS29 on a timer; tab clicks keep PS29; confirm leaves to PS9."""

    def __init__(self, *, reach29: bool = True, confirm_works: bool = True) -> None:
        self.clock = {"now": 0.0}
        self.reach29 = reach29
        self.confirm_works = confirm_works
        self.clicks: list[tuple[int, int]] = []
        self.left = False

    def read_ps(self) -> int:
        if self.left:
            return 9
        now = self.clock["now"]
        if now < 1.0:
            return 3
        if now < 2.0 or not self.reach29:
            return 27
        return 29

    def inject(self, point: tuple[int, int], **kw) -> dict:
        self.clicks.append(point)
        if point == probe.RESULT_SCREEN_CONFIRM and self.confirm_works:
            self.left = True
        return {}


def _run_result(monkeypatch: pytest.MonkeyPatch, game: _ResultGame) -> tuple[dict, list[float], list[str]]:
    sleeps: list[float] = []
    captures: list[str] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        game.clock["now"] += seconds

    monkeypatch.setattr(probe.time, "sleep", sleep)
    monkeypatch.setattr(probe.time, "monotonic", lambda: game.clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: len(sleeps))
    result = probe._result_screen_window(
        inject=game.inject, read_ps=game.read_ps, trace_path=Path("t.jsonl"), capture=captures.append,
        reach_timeout=20.0)
    return result, sleeps, captures


def test_result_screen_window_walks_ps27_ps29_tabs_and_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _ResultGame()
    result, sleeps, captures = _run_result(monkeypatch, game)
    assert result["status"] == "PASS"
    assert result["states_seen"] == [3, 27, 29]
    assert [w["name"] for w in result["windows"]] == [
        "ps27", "ps29", "tab_soldiers", "tab_buildings", "tab_resources", "after_confirm"]
    assert [w["program_state"] for w in result["windows"]] == [27, 29, 29, 29, 29, 9]
    assert game.clicks == [*probe.RESULT_SCREEN_TABS.values(), probe.RESULT_SCREEN_CONFIRM]
    # the fake PS27 lasts 1 s: only the 0.3 s ps27_early capture fires (ps27 at 2 s and ps27_late at 5 s do not)
    assert captures == ["ps27_early", "ps29", "result_tab_soldiers", "result_tab_buildings",
                        "result_tab_resources", "result_after_confirm"]
    assert result["after_state"] == 9
    assert sleeps.count(probe.RESULT_SCREEN_DWELL_SECONDS) == 1


def test_result_screen_window_captures_ps27_once_after_the_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    """H-RS1 RS1-0: ps27.png is taken once, ps27_capture_delay seconds after PS27 is first seen."""
    game = _ResultGame()
    sleeps: list[float] = []
    captures: list[tuple[str, float]] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        game.clock["now"] += seconds

    monkeypatch.setattr(probe.time, "sleep", sleep)
    monkeypatch.setattr(probe.time, "monotonic", lambda: game.clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: len(sleeps))
    result = probe._result_screen_window(
        inject=game.inject, read_ps=game.read_ps, trace_path=Path("t.jsonl"),
        capture=lambda name: captures.append((name, game.clock["now"])), reach_timeout=20.0,
        ps27_captures=(("ps27_early", 0.25), ("ps27", 0.5), ("ps27_late", 5.0)))
    assert result["status"] == "PASS"
    names = [name for name, _ in captures]
    # PS27 lasts 1 s in the fake game: the early/main captures fire once, the late one never does
    assert names[:3] == ["ps27_early", "ps27", "ps29"] and names.count("ps27") == 1
    assert "ps27_late" not in names
    at = dict(captures)
    assert 1.0 + 0.25 <= at["ps27_early"] < at["ps27"] < 2.0  # PS27 is entered at 1.0 s in the fake game
    assert probe.RESULT_SCREEN_PS27_CAPTURES == (("ps27_early", 0.3), ("ps27", 2.0), ("ps27_late", 5.0))


def test_result_screen_options_wire_the_h_rs1_diagnostics_to_the_candidate_lane() -> None:
    assert '"--stale-mask-state"' in SOURCE
    assert 'choices=(3, 5, 7, 20, 23, 27, 29)' in SOURCE
    assert "--stale-mask-state requires --stale-mask" in SOURCE
    assert 'env["SYW2_G1_STALE_MASK_STATE"] = str(stale_mask_state)' in SOURCE
    branch = SOURCE[SOURCE.index("    if args.result_screen:\n        lanes = {"):]
    branch = branch[: branch.index("passed = all(")]
    for needle in ('stale_mask=args.stale_mask if name == "candidate" else None',
                   "stale_mask_state=args.stale_mask_state",
                   'layer_drift=args.layer_drift if name == "candidate" else False',
                   'screen_watch=args.screen_watch if name == "candidate" else False',
                   "screen_watch_state=args.screen_watch_state",
                   'drift_samples=args.drift_samples if name == "candidate" else None'):
        assert needle in branch
    summary = SOURCE[SOURCE.index('"schema": "syw2plus.g1-result-screen.v1"'):]
    summary = summary[: summary.index("result-screen-result.json")]
    assert '"stale_mask"' in summary and '"screen_watch"' in summary


def test_result_screen_window_fails_and_records_states_when_ps29_never_arrives(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _ResultGame(reach29=False)
    result, _, captures = _run_result(monkeypatch, game)
    assert result["status"] == "FAIL"
    assert "PS29 not reached" in result["reason"]
    assert result["states_seen"] == [3, 27]
    assert game.clicks == []
    assert captures == ["ps27_early", "ps27", "ps27_late", "result_unreached"]  # PS27 never ends: all taken


def test_result_screen_window_fails_when_confirm_does_not_leave_ps29(monkeypatch: pytest.MonkeyPatch) -> None:
    result, _, _ = _run_result(monkeypatch, _ResultGame(confirm_works=False))
    assert result["status"] == "FAIL"
    assert "confirm" in result["reason"]
    assert result["after_state"] == 29


def _trace(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def _present(seq: int, state: int, stale: int = 0, **extra) -> dict:
    return {"event": "mirror2x_present", "seq": seq, "program_state": state, "covered_pixels": 480_000,
            "stale_pixels": stale, "fallback": 0, "success": 1, "elapsed_ms": 7, **extra}


def _windows(first_stale: int = 0, tab_stale: int = 0, after_state: int = 9, after_stale: int = 0):
    rows = [_present(0, 27), _present(1, 27)]
    rows += [_present(2, 29, stale=first_stale)] + [_present(3 + i, 29) for i in range(4)]
    rows += [_present(10 + i, 29, stale=tab_stale if i == 1 else 0) for i in range(6)]
    rows += [_present(20 + i, after_state, stale=after_stale) for i in range(3)]
    windows = [
        {"name": "ps27", "program_state": 27, "line_start": 0, "line_end": 2},
        {"name": "ps29", "program_state": 29, "line_start": 2, "line_end": 7},
        {"name": "tab_soldiers", "program_state": 29, "line_start": 7, "line_end": 13},
        {"name": "after_confirm", "program_state": after_state, "line_start": 13, "line_end": 16},
    ]
    return rows, windows


def test_result_screen_summary_passes_when_every_window_clears_the_floor(tmp_path: Path) -> None:
    rows, windows = _windows()
    _trace(tmp_path / "t.jsonl", rows)
    summary = probe._summarize_result_screen(
        tmp_path / "t.jsonl", {"windows": windows, "after_state": 9})
    assert summary["status"] == "PASS"
    assert summary["windows"]["ps29"]["presents"] == 5
    assert summary["windows"]["ps27"]["presents"] == 2


def test_result_screen_summary_discloses_but_allows_a_low_first_transition_present(tmp_path: Path) -> None:
    rows, windows = _windows(first_stale=100_000)
    _trace(tmp_path / "t.jsonl", rows)
    summary = probe._summarize_result_screen(
        tmp_path / "t.jsonl", {"windows": windows, "after_state": 9})
    assert summary["status"] == "PASS"
    assert summary["first_present_below_floor"] == ["ps29"]


def test_result_screen_summary_fails_a_low_later_present_in_a_tab_window(tmp_path: Path) -> None:
    rows, windows = _windows(tab_stale=50_000)
    _trace(tmp_path / "t.jsonl", rows)
    summary = probe._summarize_result_screen(
        tmp_path / "t.jsonl", {"windows": windows, "after_state": 9})
    assert summary["status"] == "FAIL"
    assert summary["criteria"]["tab_soldiers_hd"] is False


def test_result_screen_summary_requires_ps9_after_confirm_to_stay_at_the_menu_floor(tmp_path: Path) -> None:
    rows, windows = _windows(after_stale=5_000)  # 98.96% > 98.6 but < the PS9 99.9 floor
    _trace(tmp_path / "t.jsonl", rows)
    summary = probe._summarize_result_screen(
        tmp_path / "t.jsonl", {"windows": windows, "after_state": 9})
    assert summary["status"] == "FAIL"
    assert summary["criteria"]["after_confirm_hd"] is False


def test_result_screen_summary_fails_on_a_safety_counter(tmp_path: Path) -> None:
    rows, windows = _windows()
    rows[4]["hd_mask_outside_diff_subpixels"] = 3
    _trace(tmp_path / "t.jsonl", rows)
    summary = probe._summarize_result_screen(
        tmp_path / "t.jsonl", {"windows": windows, "after_state": 9})
    assert summary["status"] == "FAIL"
    assert summary["criteria"]["safety_clean"] is False
