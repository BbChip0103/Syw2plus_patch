from tools.g5_minimap_click_hittest_probe import (
    MINIMAP_MODE_BUTTONS,
    minimap_effect_summary,
    minimap_mode_effect_summary,
    scan_lut,
)


def test_minimap_effect_requires_pending_xy_change_for_every_selected_unit() -> None:
    before = [
        {"slot": 10, "pending_xy": 100, "pending_command": 0},
        {"slot": 11, "pending_xy": 200, "pending_command": 0},
    ]
    immediate = [
        {"slot": 10, "pending_xy": 101, "pending_command": 3},
        {"slot": 11, "pending_xy": 200, "pending_command": 3},
    ]
    delayed = [
        {"slot": 10, "pending_xy": 101, "pending_command": 3},
        {"slot": 11, "pending_xy": 202, "pending_command": 3},
    ]

    result = minimap_effect_summary(before, immediate, delayed)

    assert result["selected_count"] == 2
    assert result["pending_xy_changed_count"] == 2
    assert result["all_selected_pending_xy_changed"] is True


def test_minimap_effect_does_not_count_unchanged_pending_xy() -> None:
    before = [{"slot": 10, "pending_xy": 100, "pending_command": 0}]
    after = [{"slot": 10, "pending_xy": 100, "pending_command": 3}]

    result = minimap_effect_summary(before, after, after)

    assert result["pending_xy_changed_count"] == 0
    assert result["all_selected_pending_xy_changed"] is False


def test_scan_lut_returns_pixel_coordinates_for_baked_byte() -> None:
    raw = bytes([0xFF] * 20 + [0x12, 0x34] + [0xFF] * 20)

    result = scan_lut(raw)

    assert result["all_0xff"] is False
    assert result["first_non_0xff"]["col_dx"] == 10
    assert result["first_non_0xff"]["row_dy"] == 1


def test_minimap_mode_effect_records_delivery_and_command_values() -> None:
    before = [
        {"slot": 10, "pending_xy": 100, "command": 0, "pending_command": 0},
        {"slot": 11, "pending_xy": 200, "command": 0, "pending_command": 0},
    ]
    immediate = [
        {"slot": 10, "pending_xy": 101, "command": 3, "pending_command": 3},
        {"slot": 11, "pending_xy": 201, "command": 3, "pending_command": 3},
    ]

    result = minimap_mode_effect_summary("move", before, immediate, immediate)

    assert result["mode"] == "move"
    assert result["pending_xy_changed_count"] == 2
    assert result["all_selected_pending_xy_changed"] is True
    assert result["command_changed_count"] == 2
    assert result["pending_command_changed_count"] == 2


def test_minimap_mode_buttons_cover_requested_three_modes() -> None:
    assert set(MINIMAP_MODE_BUTTONS) == {"move", "attack", "patrol"}
