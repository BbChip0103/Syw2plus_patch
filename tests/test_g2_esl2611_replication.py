"""Pure-helper contract of the G2 2611 replication wrapper."""

from tools import g2_esl2611_replication as rep


def test_remap_goal_only_rewrites_seed42_eight_ai() -> None:
    assert rep.remap_goal(rep.SEED_GOAL_OLD) == rep.SEED_GOAL_NEW
    assert rep.remap_goal("_custom_game_chain_inject_g2_eight_seed42") == "_custom_game_chain_inject_g2_eight_seed42"
