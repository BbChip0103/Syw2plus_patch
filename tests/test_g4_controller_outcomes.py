from tools.g4_controller_outcomes import summarize, windows


def sample(tick: int, op0: int, arg0: int, units0: int, rice0: int = 100) -> dict:
    units = [{"owner": 0} for _ in range(units0)] + [{"owner": 1}]
    return {
        "tick": tick,
        "players": [
            {"owner": 0, "controller_opcode": op0, "controller_argument": arg0,
             "rice": rice0, "wood": 100, "reserved": 0, "count": units0, "used": units0 * 10},
            {"owner": 1, "controller_opcode": 0, "controller_argument": 0,
             "rice": 100, "wood": 100, "reserved": 0, "count": 1, "used": 10},
        ],
        "units": units,
    }


def test_windows_track_release_and_state_delta():
    rows = [sample(10, 0, 0, 1), sample(13, 3, 6, 1), sample(16, 3, 6, 2, 80), sample(19, 0, 0, 2, 80)]
    assert windows(rows, 0) == [{
        "opcode": 3,
        "argument": 6,
        "end": {"tick": 16, "units": 2, "rice": 80, "wood": 100,
                "reserved": 0, "count": 2, "used": 20},
        "duration_ticks": 3,
        "sample_count": 2,
        "released_to_zero": True,
        "delta": {"units": 1, "rice": -20, "wood": 0, "reserved": 0, "count": 1, "used": 10},
        "truncated": False,
    }]


def test_summary_marks_window_open_at_capture_end():
    report = summarize({"g4_ai_smoke": {"samples": [sample(10, 1, 1, 1), sample(13, 1, 1, 1)]}})
    assert report["owners"]["0"]["by_opcode"]["1"] == {
        "count": 1,
        "released_to_zero": 0,
        "truncated": 1,
        "max_duration_ticks": 3,
        "total_duration_ticks": 3,
    }
