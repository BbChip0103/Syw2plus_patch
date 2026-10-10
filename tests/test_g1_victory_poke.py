"""Contracts for the H-VS0 victory-screen HD measurement harness (synthetic ``victory-poke`` trigger)."""

import json
from pathlib import Path

import pytest

from tools import g1_saved_scene_probe as probe

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "tools/g1_saved_scene_probe.py").read_text(encoding="utf-8")


def test_victory_poke_address_and_option_wiring() -> None:
    assert probe.VICTORY_POKE_VA == 0xB63238
    assert probe.VICTORY_READBACK_RETURN == 0x4C7EEB
    assert '"--victory-poke"' in SOURCE
    assert 'parser.error("--victory-poke requires --new-game-start")' in SOURCE
    assert "victory_poke=args.victory_poke" in SOURCE
    assert "victory_poke=victory_poke" in SOURCE
    branch = SOURCE[SOURCE.index("    if args.new_game_path:\n        lanes = {"):]
    branch = branch[: branch.index("new-game-path-result.json")]
    assert '"victory_poke"' in branch
    assert 'lane.get("victory_poke", {}).get("status") == "PASS"' in branch


class _VictoryGame:
    """Fake game: PS3 until the poke; the flag is consumed 0.5 s later, PS24 -> PS25 -> PS29 on a timer."""

    def __init__(self, *, readback: int = 1, reach29: bool = True) -> None:
        self.clock = {"now": 0.0}
        self.flag = 0
        self.readback = readback
        self.reach29 = reach29
        self.poked_at: float | None = None
        self.writes: list[int] = []
        self.clicks: list[tuple[int, int]] = []
        self.left = False

    def write_flag(self, value: int) -> None:
        self.writes.append(value)
        self.flag = self.readback if self.readback != 1 else value
        self.poked_at = self.clock["now"]

    def read_flag(self) -> int:
        if self.poked_at is not None and self.clock["now"] - self.poked_at >= 0.5:
            self.flag = 0
        return self.flag

    def read_ps(self) -> int:
        if self.left:
            return 9
        if self.poked_at is None:
            return 3
        elapsed = self.clock["now"] - self.poked_at
        if elapsed < 1.0:
            return 3
        if elapsed < 4.0:
            return 24
        if elapsed < 6.0 or not self.reach29:
            return 25
        return 29

    def inject(self, point: tuple[int, int], **kw) -> dict:
        self.clicks.append(point)
        if point == probe.RESULT_SCREEN_CONFIRM:
            self.left = True
        return {}


def _run_victory(monkeypatch: pytest.MonkeyPatch, game: _VictoryGame) -> tuple[dict, list[str]]:
    sleeps: list[float] = []
    captures: list[str] = []

    def sleep(seconds: float) -> None:
        sleeps.append(seconds)
        game.clock["now"] += seconds

    monkeypatch.setattr(probe.time, "sleep", sleep)
    monkeypatch.setattr(probe.time, "monotonic", lambda: game.clock["now"])
    monkeypatch.setattr(probe, "_trace_line_count", lambda path: len(sleeps))
    result = probe._victory_poke_window(
        inject=game.inject, read_ps=game.read_ps, read_flag=game.read_flag, write_flag=game.write_flag,
        trace_path=Path("t.jsonl"), capture=captures.append, reach_timeout=30.0)
    return result, captures


def test_victory_poke_pokes_once_then_walks_banner_result_tabs_and_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _VictoryGame()
    result, captures = _run_victory(monkeypatch, game)
    assert result["status"] == "PASS"
    assert game.writes == [1]
    assert result["poke"] == {"va": "0xb63238", "before": 0, "readback": 1, "consumed": True,
                              "consumed_at_ps": 3}
    assert result["states_seen"] == [3, 24, 25, 29]
    assert [w["name"] for w in result["windows"]] == [
        "ps24", "ps25", "ps29", "tab_soldiers", "tab_buildings", "tab_resources", "after_confirm"]
    assert [w["program_state"] for w in result["windows"]] == [24, 25, 29, 29, 29, 29, 9]
    assert game.clicks == [*probe.RESULT_SCREEN_TABS.values(), probe.RESULT_SCREEN_CONFIRM]
    assert "vs_ps24" in captures and "vs_ps25" in captures and "ps29" in captures


def test_victory_poke_refuses_to_walk_when_the_readback_does_not_stick(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _VictoryGame(readback=7)
    result, captures = _run_victory(monkeypatch, game)
    assert result["status"] == "FAIL"
    assert "readback" in result["reason"]
    assert game.clicks == [] and captures == []


def test_victory_poke_fails_and_records_states_when_the_result_screen_never_arrives(monkeypatch: pytest.MonkeyPatch) -> None:
    game = _VictoryGame(reach29=False)
    result, captures = _run_victory(monkeypatch, game)
    assert result["status"] == "FAIL"
    assert "PS29 not reached" in result["reason"]
    assert result["states_seen"] == [3, 24, 25]
    assert "result_unreached" in captures
    assert game.clicks == []


def _present(seq: int, state: int, stale: int = 0, **extra) -> dict:
    return {"event": "mirror2x_present", "seq": seq, "program_state": state, "covered_pixels": 480_000,
            "stale_pixels": stale, "fallback": 0, "success": 1, "elapsed_ms": 7, **extra}


COUNTERS = {"primary_readback_calls": 1, "primary_readback_converted": 1, "primary_readback_rejects": 0,
            "primary_readback_return_address": 0x4C7EEB,
            "bar_copy_468bb0_calls": 40, "bar_copy_468bb0_mirrored": 40, "bar_copy_468bb0_rejects": 0}


def _walk(tmp_path: Path, *, counters: dict | None = None, consumed: bool = True,
          skip_banner: bool = False):
    rows = [_present(0, 24), _present(1, 24)] if not skip_banner else []
    rows += [_present(2, 29), _present(3, 29), _present(4, 9, **(counters or COUNTERS))]
    path = tmp_path / "t.jsonl"
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    windows = [{"name": "ps24", "program_state": 24, "line_start": 0, "line_end": 2},
               {"name": "ps29", "program_state": 29, "line_start": 2, "line_end": 4},
               {"name": "after_confirm", "program_state": 9, "line_start": 4, "line_end": 5}]
    if skip_banner:
        windows.pop(0)
    return path, {"windows": windows, "after_state": 9,
                  "poke": {"readback": 1, "consumed": consumed}}


def test_victory_summary_passes_when_banner_and_result_clear_the_floor_with_both_repairs_counted(tmp_path: Path) -> None:
    path, walk = _walk(tmp_path)
    summary = probe._summarize_victory(path, walk)
    assert summary["status"] == "PASS"
    assert summary["counters"]["bar_copy_468bb0_calls"] == 40
    assert all(summary["criteria"].values())


def test_victory_summary_fails_a_banner_hd_drop(tmp_path: Path) -> None:
    path, walk = _walk(tmp_path)
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    rows[1]["stale_pixels"] = 400_000  # a later (not first) banner present
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
    summary = probe._summarize_victory(path, walk)
    assert summary["status"] == "FAIL"
    assert summary["criteria"]["ps24_hd"] is False


def test_victory_summary_fails_without_repair_counters_or_the_banner_state(tmp_path: Path) -> None:
    off = {**COUNTERS, "primary_readback_converted": 0, "bar_copy_468bb0_mirrored": 0}
    path, walk = _walk(tmp_path, counters=off)
    summary = probe._summarize_victory(path, walk)
    assert summary["status"] == "FAIL"
    assert summary["criteria"]["readback_mirrored"] is False
    assert summary["criteria"]["bar_copy_mirrored"] is False
    path, walk = _walk(tmp_path, skip_banner=True)
    summary = probe._summarize_victory(path, walk)
    assert summary["criteria"]["banner_reached"] is False and summary["status"] == "FAIL"


def test_victory_summary_requires_the_flag_to_be_consumed(tmp_path: Path) -> None:
    path, walk = _walk(tmp_path, consumed=False)
    summary = probe._summarize_victory(path, walk)
    assert summary["criteria"]["poke_consumed"] is False and summary["status"] == "FAIL"
