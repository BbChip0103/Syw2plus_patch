from __future__ import annotations

from tools import g2_esl2608_high_slot_portrait_probe as probe


def test_high_slot_fixture_uses_the_pinned_esl2608_regions() -> None:
    exists_base, age_base, unit_base = probe.candidate_regions()
    assert (exists_base, age_base, unit_base) == (0x018849F8, 0x018869F2, 0x0112E000)
    assert probe.HIGH_SLOT == 4092


def test_fixture_id_replaces_only_the_slot_bits() -> None:
    source_id = 0x000B0377
    high_slot_id = (source_id & 0xFFFF0000) | probe.HIGH_SLOT
    assert high_slot_id == 0x000B0FFC
    assert high_slot_id & 0xFFF == probe.HIGH_SLOT
