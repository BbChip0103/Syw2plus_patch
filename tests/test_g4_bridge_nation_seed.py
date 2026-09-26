"""Regression guard for fixed-nation goals combined with fixed seeds."""

from pathlib import Path


def test_nation_goal_matching_accepts_seed_suffixes():
    source = (
        Path(__file__).resolve().parents[1]
        / "tools/inmm_stub/control_executor.c"
    ).read_text(encoding="utf-8")
    start = source.index("static void chain_inject_nations_for_goal")
    end = source.index("static void run_chain_inject", start)
    function = source[start:end]
    for goal in (
        "_custom_game_chain_inject_joseon_ming",
        "_custom_game_chain_inject_ming_joseon",
        "_custom_game_chain_inject_ming_japan",
    ):
        assert f'chain_inject_goal_matches(goal, "{goal}")' in function
        assert f'lstrcmpA(goal, "{goal}")' not in function
