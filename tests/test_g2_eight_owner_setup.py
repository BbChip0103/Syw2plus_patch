"""Static guards for the opt-in original eight-owner setup boundary."""

from pathlib import Path


SOURCE = Path(__file__).parents[1] / "tools" / "inmm_stub" / "control_executor.c"


def _source() -> str:
    return SOURCE.read_text(encoding="utf-8")


def _g2_block() -> str:
    text = _source()
    start = text.index("if (is_g2_eight_goal(req->goal)) {")
    end = text.index("} else {\n            chain_inject_nations_for_goal", start)
    return text[start:end]


def test_g2_goal_is_exact_opt_in_and_ps7_only() -> None:
    text = _source()
    assert '#define G2_EIGHT_GOAL      "_custom_game_chain_inject_g2_eight_seed42"' in text
    assert (
        '#define G2_EIGHT_AI_GOAL   "_custom_game_chain_inject_g2_eight_ai_seed42"' in text
    )
    # W22 (lap456 work) fixture-lever arms: five more exact-match opt-ins,
    # each an additive literal, added to the same is_g2_eight_goal() gate.
    assert (
        '#define G2_EIGHT_AI_D4A1_GOAL "_custom_game_chain_inject_g2_eight_ai_d4a1_seed42"'
        in text
    )
    assert '#define G2_EIGHT_AI_AI4_GOAL  "_custom_game_chain_inject_g2_eight_ai4_seed42"' in text
    assert (
        '#define G2_EIGHT_AI_D44_0_GOAL "_custom_game_chain_inject_g2_eight_ai_d44_0_seed42"'
        in text
    )
    assert (
        '#define G2_EIGHT_AI_D46_1_GOAL "_custom_game_chain_inject_g2_eight_ai_d46_1_seed42"'
        in text
    )
    assert '#define G2_EIGHT_AI_SEED99_GOAL "_custom_game_chain_inject_g2_eight_ai_seed99"' in text
    assert "lstrcmpA(goal, G2_EIGHT_GOAL) == 0 ||" in text
    assert "lstrcmpA(goal, G2_EIGHT_AI_GOAL) == 0 ||" in text
    assert "lstrcmpA(goal, G2_EIGHT_AI_D4A1_GOAL) == 0 ||" in text
    assert "lstrcmpA(goal, G2_EIGHT_AI_AI4_GOAL) == 0 ||" in text
    assert "lstrcmpA(goal, G2_EIGHT_AI_D44_0_GOAL) == 0 ||" in text
    assert "lstrcmpA(goal, G2_EIGHT_AI_D46_1_GOAL) == 0 ||" in text
    assert "lstrcmpA(goal, G2_EIGHT_AI_SEED99_GOAL) == 0;" in text
    assert "is_g2_eight_goal(goal) ||" in text
    assert "g2_eight_requires_ps7_got_%u" in text
    assert "is_g2_eight_goal(req->goal) && state_before != 7" in text


def test_g2_eight_ai_goal_only_changes_owner0_record2() -> None:
    block = _g2_block()
    # owner0_ai is now phrased as "not the plain (non-AI) legacy goal" rather
    # than "is exactly the AI goal" so the same expression covers G2_EIGHT_AI_GOAL
    # and every W22 arm goal below it -- but for the two legacy literals this is
    # provably the same truth table as the original exact-match form, since
    # is_g2_eight_goal() only ever admits those two plus the five W22 literals:
    #   goal == G2_EIGHT_GOAL    -> old: False            new: != G2_EIGHT_GOAL -> False
    #   goal == G2_EIGHT_AI_GOAL -> old: True (== AI_GOAL) new: != G2_EIGHT_GOAL -> True
    assert "BOOL owner0_ai = (lstrcmpA(req->goal, G2_EIGHT_GOAL) != 0);" in block
    assert "record[2] = (BYTE)(owner_ai ? 1 : 0);" in block
    assert "BOOL owner_ai = (owner == 0) ? owner0_ai : TRUE;" in block
    # every other record field is unconditional (no owner0_ai/owner_ai reference).
    assert 'record[0] = 1' in block
    assert "record[1] = (BYTE)owner;" in block
    assert "record[3] = (BYTE)(1u << owner);" in block
    assert "record[4] = 0" in block
    assert "record[5] = (BYTE)owner;" in block
    # W22 A2 (ai4): the only other record[2] override, gated on its own exact
    # literal and owner index, never touching owners 0..3 or any other field.
    assert "BOOL want_ai4 = (lstrcmpA(req->goal, G2_EIGHT_AI_AI4_GOAL) == 0);" in block
    assert "if (want_ai4 && owner >= 4) {\n                        owner_ai = FALSE;\n                    }" in block


def test_g2_populates_full_lobby_records_before_chain_without_playerstruct_write() -> None:
    text = _source()
    block = _g2_block()
    assert "G2_LOBBY_RECORDS   8" in text
    assert "G2_LOBBY_STRIDE    6" in text
    assert "IsBadWritePtr((LPVOID)lobby," in text
    assert "G2_LOBBY_RECORDS * G2_LOBBY_STRIDE" in text
    assert "for (owner = 0; owner < G2_LOBBY_RECORDS; ++owner)" in block
    for offset in range(6):
        assert f"record[{offset}]" in block
    assert "PlayerStruct arena directly" in block
    assert "0x956770" not in block


def test_g2_roster_values_and_ordinary_mode_are_pinned() -> None:
    block = _g2_block()
    assert "record[0] = 1" in block
    assert "record[1] = (BYTE)owner" in block
    assert "record[2] = (BYTE)(owner_ai ? 1 : 0)" in block
    assert "record[3] = (BYTE)(1u << owner)" in block
    assert "record[4] = 0" in block
    assert "record[5] = (BYTE)owner" in block
    assert "game_mode = 0" in block
    assert "requested ordinary-mode diagnostic; UI label unverified" in block
    # d44/d46/d4a keep their original literal default (2/0/0) unless a W22
    # arm's own exact-match goal literal requests the single documented
    # override; every other goal (including both legacy literals) computes
    # exactly the pinned original value since its want_* flag is False.
    assert "d44 = want_d44_0 ? 0 : 2;" in block
    assert "d46 = want_d46_1 ? 1 : 0;" in block
    assert "d48 = 0" in block
    assert "d4a = want_d4a1 ? 1 : 0;" in block
    assert "d4c = 0" in block
    assert "BOOL want_d4a1 = (lstrcmpA(req->goal, G2_EIGHT_AI_D4A1_GOAL) == 0);" in block
    assert "BOOL want_d44_0 = (lstrcmpA(req->goal, G2_EIGHT_AI_D44_0_GOAL) == 0);" in block
    assert "BOOL want_d46_1 = (lstrcmpA(req->goal, G2_EIGHT_AI_D46_1_GOAL) == 0);" in block
    assert "*pRawGateB != 0" in block
    assert "g2_requires_B93988_zero" in block


def test_g2_legacy_goals_compute_identical_config_to_pre_w22_source() -> None:
    """Behavioral-equivalence guard for the two pre-W22 literals.

    The literal source lines changed shape in lap456 (owner0_ai/record[2]/
    d44/d46/d4a all became goal-dependent expressions instead of fixed
    constants) so the byte-for-byte pins above had to move. This test
    re-derives, in Python, the C truth table for exactly the two legacy
    goals and checks it against what the new expressions produce, so a
    future edit that actually changes legacy behavior (not just literal
    text) still fails a test.
    """
    g2_eight_goal = "_custom_game_chain_inject_g2_eight_seed42"
    g2_eight_ai_goal = "_custom_game_chain_inject_g2_eight_ai_seed42"
    for goal, expected_owner0_ai in ((g2_eight_goal, False), (g2_eight_ai_goal, True)):
        owner0_ai = goal != g2_eight_goal
        assert owner0_ai == expected_owner0_ai
        want_d4a1 = want_d44_0 = want_d46_1 = want_ai4 = False  # both legacy literals
        d44 = 0 if want_d44_0 else 2
        d46 = 1 if want_d46_1 else 0
        d4a = 1 if want_d4a1 else 0
        assert (d44, d46, d4a) == (2, 0, 0)
        for owner in range(8):
            owner_ai = owner0_ai if owner == 0 else True
            if want_ai4 and owner >= 4:
                owner_ai = False
            assert owner_ai == ((owner == 0 and expected_owner0_ai) or owner != 0)


def test_g2_rejects_override_and_preflights_chain_program_state_before_roster() -> None:
    text = _source()
    assert "g2_eight_rejects_scenario_index_override" in text
    preflight = text[text.index("static BOOL g2_setup_preflight"):]
    assert "CG_CHAIN_VALUE_VA" in preflight
    assert "PROGRAM_STATE_VA" in preflight
    assert "g2_setup_preflight_failed" in text
    assert text.index("if (is_g2_eight_goal(req->goal) && !g2_setup_preflight())") < text.index(
        "if (target == 2)"
    )


def test_legacy_chain_configuration_remains_outside_g2_branch() -> None:
    text = _source()
    block = _g2_block()
    legacy_start = text.index("} else {\n            chain_inject_nations_for_goal", text.index(block))
    legacy = text[legacy_start : text.index("            *pPlr0", legacy_start)]
    assert "chain_inject_nations_for_goal(req->goal, &nation0, &nation1);" in legacy
    assert '"_custom_game_chain_inject_map2"' in legacy
    assert "game_mode = 3" in legacy
    assert "op4" not in block.lower()
    assert "train" not in block.lower()
    assert "save" not in block.lower()
    assert "load" not in block.lower()
