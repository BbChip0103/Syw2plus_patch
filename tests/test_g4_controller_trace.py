from tools.g4_controller_trace import compare, episodes


def capture(events):
    return {"g4_ai_smoke": {"samples": [
        {"tick": tick, "players": [
            {"controller_opcode": 0, "controller_argument": 0},
            {"controller_opcode": opcode, "controller_argument": argument},
        ]}
        for tick, opcode, argument in events
    ]}}


def test_episode_extraction_collapses_contiguous_opcode() -> None:
    samples = capture([(10, 0, 0), (11, 18, 101), (12, 18, 102), (13, 0, 0), (14, 1, 2)])["g4_ai_smoke"]["samples"]
    assert episodes(samples, 1) == [
        {"tick": 11, "opcode": 18, "argument": 101},
        {"tick": 14, "opcode": 1, "argument": 2},
    ]


def test_compare_allows_three_tick_capture_jitter() -> None:
    first = capture([(10, 0, 0), (20, 18, 101), (21, 0, 0), (40, 1, 2)])
    second = capture([(10, 0, 0), (23, 18, 101), (24, 0, 0), (38, 1, 2)])
    report = compare(first, second)
    assert report["pass"] is True
    assert report["owners"]["1"]["max_abs_tick_delta"] == 3


def test_compare_rejects_opcode_drift() -> None:
    first = capture([(10, 0, 0), (20, 18, 101)])
    second = capture([(10, 0, 0), (20, 3, 5)])
    assert compare(first, second)["classification"] == "CONTROLLER_TRACE_DRIFT"
