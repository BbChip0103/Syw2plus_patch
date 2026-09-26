from copy import deepcopy

from tools.g4_ai_repeatability import compare


def fixture():
    return {
        "fixture": {"kind": "seed42", "control_bridge": True, "memory_writes": True},
        "scene": {"map": "fixed", "owners": {"0": {"nation": 1}}, "world_bounds": {"width": 100}},
        "g4_ai_smoke": {
            "samples": [{
                "tick": 10,
                "players": [{"owner": 0, "nation": 1, "ai": 1, "rice": 10, "wood": 10,
                             "reserved": 0, "count": 1, "used": 10, "count_cap": 250, "cap": 1500,
                             "controller_opcode": 0, "controller_argument": 0}],
                "units": [{"slot": 1199, "type": 49, "owner": 0, "internal_id": 999, "hp": 4800,
                           "command": 1, "production_type": 0, "progress": 0, "x": 10, "y": 55}],
            }],
            "summary": {"sample_count": 5, "first_tick": 12, "last_tick": 279},
        },
    }


def test_repeatability_ignores_volatile_and_internal_identity():
    first = fixture()
    second = deepcopy(first)
    first["pid"] = 1
    second["pid"] = 2
    second["g4_ai_smoke"]["samples"][0]["units"][0]["internal_id"] = 12345
    report = compare(first, second)
    assert report["equal"] is True
    assert report["exact_equal"] is True
    assert report["first_signature"] == report["second_signature"]


def test_repeatability_rejects_gameplay_drift():
    first = fixture()
    second = deepcopy(first)
    second["g4_ai_smoke"]["samples"][0]["units"][0]["x"] = 11
    report = compare(first, second)
    assert report["equal"] is False
    assert report["classification"] == "FIXED_FIXTURE_DRIFT"


def test_repeatability_allows_one_tick_production_progress_drift():
    first = fixture()
    second = deepcopy(first)
    second["g4_ai_smoke"]["samples"][0]["units"][0]["progress"] = 1
    report = compare(first, second)
    assert report["equal"] is True
    assert report["exact_equal"] is False
    assert report["max_progress_delta"] == 1
    assert report["classification"] == "FIXED_FIXTURE_REPEATABLE_TOLERANCE"
