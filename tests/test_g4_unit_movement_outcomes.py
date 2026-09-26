import pytest

from tools.g4_unit_movement_outcomes import mobile_types, summarize


def test_mobile_types_requires_complete_table():
    with pytest.raises(ValueError, match="expected type rows"):
        mobile_types("{0x1u, 0}, // type 0")


def test_summarize_separates_stationary_mobile_units():
    rows = "\n".join(
        f"{{0x{1 if index in (2, 3) else 2:08X}u, 0}}, // type {index}"
        for index in range(100)
    )
    mobile = mobile_types(rows)
    samples = [
        {"tick": 0, "units": [
            {"internal_id": 1, "type": 2, "owner": 0, "x": 1, "y": 1, "command": 1},
            {"internal_id": 2, "type": 3, "owner": 0, "x": 5, "y": 5, "command": 8},
        ]},
        {"tick": 300, "units": [
            {"internal_id": 1, "type": 2, "owner": 0, "x": 4, "y": 2, "command": 3},
            {"internal_id": 2, "type": 3, "owner": 0, "x": 5, "y": 5, "command": 8},
        ]},
    ]
    report = summarize({"g4_ai_smoke": {"samples": samples}}, mobile)
    assert report["owners"]["0"]["eligible_mobile_tracks"] == 2
    assert report["owners"]["0"]["moved_tracks"] == 1
    assert report["owners"]["0"]["stationary_tracks"] == 1
    assert report["owners"]["0"]["stationary"][0]["commands"] == {"8": 2}
