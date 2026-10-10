"""Pure-helper contracts of the ESL 2611 G8/G9 runtime probe (no game launched)."""

from __future__ import annotations

import struct

from tools import esl2611_g8g9_probe as probe


def test_computer_row_matches_observed_slot_two_layout() -> None:
    assert probe.computer_row(1).hex() == "050101020001"
    assert probe.computer_row(3).hex() == "050301080003"


def test_players_table_rewrites_only_requested_slots() -> None:
    table = bytes(0x170)
    out = probe.players_table(table, 4)
    assert len(out) == len(table)
    for slot in range(1, 4):
        start = probe.ROWS_OFFSET + slot * 6
        assert out[start:start + 6] == probe.computer_row(slot)
        assert struct.unpack_from("<I", out, probe.DWORD_OFFSET + slot * 4)[0] == 1
    assert out[probe.ROWS_OFFSET + 4 * 6:probe.ROWS_OFFSET + 5 * 6] == bytes(6)
    assert out[:probe.ROWS_OFFSET] == table[:probe.ROWS_OFFSET]


def test_centroid() -> None:
    assert probe.centroid([]) is None
    assert probe.centroid([(10, 20), (13, 21)]) == (11.5, 20.5)


def test_hero_writes_cover_flag_state_and_unit_words() -> None:
    base = 0x956770
    writes = dict(probe.hero_writes(base, 2))
    assert writes[0x9B53D0 - 0x184] == b"\x08"
    assert writes[0x9B53D0 + 0x394 - 0x184] == b"\x08"
    assert writes[base + 0x20 + 2] == struct.pack("<H", 1)
    assert writes[base + 0x340] == b"\0\0"
    assert probe.hero_writes(base, 0) == []


def test_mode_value_prefers_frequent_then_larger() -> None:
    assert probe.mode_value([]) is None
    assert probe.mode_value([1500, 1700, 1700, 1500, 1500]) == 1500
    assert probe.mode_value([1500, 1700]) == 1700


def test_expected_supply_formulas() -> None:
    assert probe.expected_supply("base", 0) == 1500
    assert probe.expected_supply("base", 3) == 2100
    assert probe.expected_supply("g9", 3) == 2100
    assert probe.expected_supply("g8", 0) == 1500
    assert probe.expected_supply("g8g9", 3) == 3000
    assert probe.expected_supply("g8", 8) == 5000
