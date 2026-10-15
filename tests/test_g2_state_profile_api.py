import pytest

from patches.esl2610 import g2_state_2610


def test_default_state_geometry_is_unchanged():
    assert g2_state_2610.block_size() == g2_state_2610.layout(0)["__end__"]
    assert g2_state_2610.section_for(0x01AB5000).name == ".r17data"


def test_opt_in_state_tail_is_disjoint_and_capacity_grown():
    extra = g2_state_2610.StateSection(
        ".profile_tail", 0x03000000, 0x2000,
        (g2_state_2610._pu("profile_unit_array", 0x03000100, 4),),
    )
    assert g2_state_2610.section_for(0x03000100, g2_state_2610.STATE_SECTIONS + (extra,)) is extra
    assert g2_state_2610.block_size((extra,)) >= (
        g2_state_2610.block_size() + extra.new_size
    )


def test_opt_in_state_tail_rejects_overlap():
    extra = g2_state_2610.StateSection(
        ".overlap", 0x01AB4FFF, 0x2000,
        (g2_state_2610._pu("overlap", 0x01AB500F, 4),),
    )
    with pytest.raises(ValueError, match="ranges overlap"):
        g2_state_2610.block_size((extra,))


def test_complete_profile_can_replace_a_section_without_losing_old_arrays():
    old = g2_state_2610.STATE_SECTIONS
    original = next(sec for sec in old if sec.name == ".r17data")
    replacement = g2_state_2610.StateSection(
        original.name, original.start, original.size + 0x67000,
        original.arrays + (g2_state_2610._pu("profile_array", 0x01AB6080, 4),),
    )
    profile = tuple(replacement if sec.name == original.name else sec for sec in old)
    assert g2_state_2610.section_for(0x01AB5000, profile) is replacement
    assert g2_state_2610._array("r17_rs86", profile)[0] is replacement
    assert g2_state_2610._array("profile_array", profile)[0] is replacement
    assert g2_state_2610.block_size(state_profile=profile) > g2_state_2610.block_size()
