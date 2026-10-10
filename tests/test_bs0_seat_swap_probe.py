"""Pure-helper contracts of the H-BS0 seat-swap spike probe (no game launched)."""

from __future__ import annotations

import pytest

from tools import bs0_seat_swap_probe as probe
from tools.g5_candidate_drag_probe import ProbeError


def _row(slot: int, owner: int, *, kind: int = 7, x: int = 0, y: int = 0, flags: int = 0) -> dict[str, int]:
    return {"slot": slot, "owner": owner, "type": kind, "hp": 10, "x": x, "y": y, "flags": flags}


def test_is_cpu_byte_is_player_struct_offset_two() -> None:
    assert probe.is_cpu_va(0) == 0x956772
    assert probe.is_cpu_va(2) == 0x956772 + 2 * 0x3ABC


def test_swap_writes_variant_a_moves_only_the_local_index() -> None:
    assert probe.swap_writes("a", 1) == [(0xB63FC4, (1).to_bytes(4, "little"))]


def test_swap_writes_variant_b_adds_ai_flags_for_seat_zero_and_target() -> None:
    assert probe.swap_writes("b", 2) == [
        (0xB63FC4, (2).to_bytes(4, "little")),
        (probe.is_cpu_va(0), b"\x01"),
        (probe.is_cpu_va(2), b"\x00"),
    ]


def test_swap_writes_variant_c_leaves_the_local_index_to_the_lobby_refresh() -> None:
    assert probe.swap_writes("c", 1) == [(probe.is_cpu_va(0), b"\x01"), (probe.is_cpu_va(1), b"\x00")]


@pytest.mark.parametrize("variant,seat", [("a", 0), ("b", 8), ("x", 1)])
def test_swap_writes_rejects_bad_input(variant: str, seat: int) -> None:
    with pytest.raises(ProbeError):
        probe.swap_writes(variant, seat)


def test_owner_summary_counts_units_and_lose_check_units() -> None:
    rows = [_row(1, 0, flags=0x2), _row(2, 0), _row(3, 1, flags=0x4000), _row(4, 1, flags=0x1)]
    assert probe.owner_summary(rows) == {0: {"units": 2, "qualifying": 1}, 1: {"units": 2, "qualifying": 1}}


def test_spawned_counts_new_slot_type_pairs_of_one_owner() -> None:
    before = [_row(1, 0), _row(2, 1)]
    after = [_row(1, 0), _row(2, 1), _row(5, 0), _row(6, 1), _row(1, 0, kind=9)]
    assert probe.spawned(before, after, 0) == 2  # slot 5, and slot 1 reused by a type 9 unit
    assert probe.spawned(before, after, 1) == 1


def test_moved_counts_units_present_in_both_with_a_new_tile() -> None:
    before = [_row(1, 0, x=5, y=5), _row(2, 0, x=7, y=7), _row(3, 1, x=1, y=1)]
    after = [_row(1, 0, x=6, y=5), _row(2, 0, x=7, y=7), _row(3, 1, x=2, y=1)]
    assert probe.moved(before, after, 0) == 1
    assert probe.moved(before, after, 1) == 1


def test_pick_mobile_returns_the_current_row_of_a_unit_that_moved_earlier() -> None:
    before = [_row(1, 1, x=5, y=5), _row(2, 1, x=9, y=9), _row(3, 0, x=1, y=1)]
    after = [_row(1, 1, x=5, y=5), _row(2, 1, x=8, y=9), _row(3, 0, x=2, y=1)]
    now = [_row(2, 1, x=20, y=21), _row(3, 0, x=2, y=1)]
    assert probe.pick_mobile(before, after, now, 1) == _row(2, 1, x=20, y=21)
    assert probe.pick_mobile(before, after, [], 1) is None


def test_clockwise_order_on_screen_y_down_from_seat_zero() -> None:
    # 2611 4-player map run: seat0 bottom-right, seat1 top-right, seat2 bottom-left (tile y grows downward)
    starts = {0: (117, 103), 1: (103, 12), 2: (24, 117)}
    assert probe.clockwise_order(starts) == [0, 2, 1]
    assert probe.rotation_map([0, 2, 1]) == {0: 2, 2: 1, 1: 0}


def test_clockwise_order_four_corners() -> None:
    starts = {0: (10, 10), 1: (90, 10), 2: (90, 90), 3: (10, 90)}
    assert probe.clockwise_order(starts) == [0, 1, 2, 3]


@pytest.mark.parametrize("ps,lose,win,qualifying,expected", [
    (3, 0, 0, 3, "running"),
    (29, 123, 0, 0, "defeat_legit"),
    (27, 123, 0, 2, "defeat_spurious"),
    (29, 0, 456, 1, "victory"),
    (29, 0, 0, 1, "ended_unknown"),
])
def test_classify_end(ps: int, lose: int, win: int, qualifying: int, expected: str) -> None:
    assert probe.classify_end(ps, lose, win, qualifying) == expected


def _measures(**over: object) -> dict[str, object]:
    base: dict[str, object] = {"end": "running", "local_after": 1, "seat": 1, "human_control": True,
                               "seat0_ai_active": True, "seat_k_ai_stopped": True}
    base.update(over)
    return base


def test_run_verdict_feasible_only_when_every_leg_holds() -> None:
    assert probe.run_verdict(_measures()) == "FEASIBLE"


def test_run_verdict_partial_when_control_moves_but_ai_legs_fail() -> None:
    assert probe.run_verdict(_measures(seat0_ai_active=False)) == "PARTIAL"
    assert probe.run_verdict(_measures(seat_k_ai_stopped=False)) == "PARTIAL"


def test_run_verdict_blocked_on_spurious_defeat_or_no_control() -> None:
    assert probe.run_verdict(_measures(end="defeat_spurious")) == "BLOCKED"
    assert probe.run_verdict(_measures(human_control=False)) == "BLOCKED"
    assert probe.run_verdict(_measures(local_after=0)) == "BLOCKED"


def test_run_verdict_legit_defeat_keeps_the_other_legs() -> None:
    assert probe.run_verdict(_measures(end="defeat_legit")) == "FEASIBLE"
