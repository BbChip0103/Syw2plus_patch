from __future__ import annotations

from tools.g4_waypoint_probe_outcomes import (
    INCOMPLETE_CLASSIFICATION,
    MALFORMED_CLASSIFICATION,
    NO_ADMITTED_CLASSIFICATION,
    PASS_CLASSIFICATION,
    summarize,
)


def _probe(*, admitted: bool = True, **overrides: object) -> dict:
    record = {
        "owner": 0,
        "tick": 100,
        "source_full_id": 0x0200,
        "slot": 512,
        "group": 0,
        "target": [20, 20],
        "before_pending": 1,
        "after_pending": 0x00010003,
        "after_pending_xy": "0x00140014",
        "expected_xy": "0x00140014",
        "admitted": admitted,
        "skip_reason": "" if admitted else "human_owner",
    }
    record.update(overrides)
    return {"schema_version": 1, "owners": [record]}


def _runtime(*units: dict, ticks: tuple[int, ...] = (90, 110, 120)) -> dict:
    snapshots = []
    for tick in ticks:
        snapshot_units = []
        for unit in units:
            copy = dict(unit)
            if copy.get("slot") == 512:
                copy["x"] = {90: 2, 110: 8, 120: 15}.get(tick, copy["x"])
                copy["y"] = {90: 2, 110: 8, 120: 15}.get(tick, copy["y"])
                copy["command"] = 3 if tick >= 110 else 1
            snapshot_units.append(copy)
        snapshots.append({
            "tick": tick,
            "players": [{"owner": 0, "ai": 1}],
            "units": snapshot_units,
        })
    return {
        "g4_intervention": {
            "goal": "_g4_idle_waypoint_reinforcement_probe",
            "status": "completed",
            "result": {"ok": True},
        },
        "g4_ai_smoke": {"error": None, "samples": snapshots},
    }


def _source() -> dict:
    return {"slot": 512, "internal_id": 0x0200, "owner": 0, "x": 2, "y": 2, "command": 1}


def test_admission_movement_and_command3_pass():
    report = summarize(_runtime(_source()), _probe())
    assert report["classification"] == PASS_CLASSIFICATION
    assert report["pass"] is True
    row = report["admitted_owners"][0]
    assert row["first_coords"] == [8, 8]
    assert row["last_coords"] == [15, 15]
    assert row["distinct_count"] == 2
    assert row["chebyshev_displacement"] == 7
    assert row["command3_observed"] is True
    assert row["arrived_within5"] is True


def test_command3_without_displacement_fails():
    source = _source()
    runtime = _runtime(source)
    for sample in runtime["g4_ai_smoke"]["samples"]:
        for unit in sample["units"]:
            unit["x"] = 2
            unit["y"] = 2
            if sample["tick"] > 100:
                unit["command"] = 3
    report = summarize(runtime, _probe())
    assert report["classification"] == INCOMPLETE_CLASSIFICATION
    assert report["pass"] is False


def test_zero_admitted_is_not_pass():
    report = summarize(_runtime(_source()), _probe(admitted=False))
    assert report["classification"] == NO_ADMITTED_CLASSIFICATION
    assert report["pass"] is False
    assert report["skipped_owners"][0]["touch_status"] == "not_admitted_not_proof_of_no_call"


def test_identity_reuse_is_not_followed_as_same_unit():
    runtime = _runtime(_source())
    for sample in runtime["g4_ai_smoke"]["samples"]:
        if sample["tick"] == 120:
            sample["units"][0]["internal_id"] = 0x2200
            sample["units"][0]["x"] = 20
            sample["units"][0]["y"] = 20
            sample["units"][0]["command"] = 3
    report = summarize(runtime, _probe())
    assert report["classification"] == INCOMPLETE_CLASSIFICATION
    row = report["admitted_owners"][0]
    assert row["identity_reused"] is True
    assert row["post_sample_count"] == 1
    assert row["last_coords"] == [8, 8]


def test_malformed_pending_or_xy_rejects():
    bad_pending = summarize(_runtime(_source()), _probe(after_pending="broken"))
    assert bad_pending["classification"] == MALFORMED_CLASSIFICATION
    assert bad_pending["pass"] is False

    bad_xy = summarize(_runtime(_source()), _probe(expected_xy="0xnot-hex"))
    assert bad_xy["classification"] == MALFORMED_CLASSIFICATION
    assert bad_xy["pass"] is False


def test_pending_admission_failure_does_not_prove_no_call():
    report = summarize(
        _runtime(_source()),
        _probe(admitted=False, slot=512, source_full_id=0x0200,
               skip_reason="pending_admission_failed"),
    )
    row = report["skipped_owners"][0]
    assert row["order_admitted"] is False
    assert row["touch_status"] == "not_admitted_not_proof_of_no_call"


def test_unadmitted_owner_records_must_be_unique_and_in_range():
    first = _probe(admitted=False)["owners"][0]
    duplicate = dict(first)
    duplicate["skip_reason"] = "inactive_or_observer_nation"
    duplicate_report = summarize(
        _runtime(_source()), {"schema_version": 1, "owners": [first, duplicate]},
    )
    assert duplicate_report["classification"] == MALFORMED_CLASSIFICATION

    out_of_range = dict(first)
    out_of_range["owner"] = 8
    range_report = summarize(_runtime(_source()), {"schema_version": 1, "owners": [out_of_range]})
    assert range_report["classification"] == MALFORMED_CLASSIFICATION


def test_tick_rollback_and_probe_tick_outside_runtime_range_reject():
    rollback = _runtime(_source())
    rollback["g4_ai_smoke"]["samples"][2]["tick"] = 80
    rollback_report = summarize(rollback, _probe())
    assert rollback_report["classification"] == MALFORMED_CLASSIFICATION

    outside_report = summarize(_runtime(_source()), _probe(tick=1_000))
    assert outside_report["classification"] == MALFORMED_CLASSIFICATION


def test_failed_or_missing_intervention_ack_blocks_even_valid_movement():
    runtime = _runtime(_source())
    runtime["g4_intervention"] = {
        "goal": "_g4_idle_waypoint_reinforcement_probe",
        "status": "error",
        "result": None,
    }
    runtime["g4_ai_smoke"]["error"] = "ack timeout"
    report = summarize(runtime, _probe())
    assert report["pass"] is False
    assert report["evidence_status"] == "BLOCKED"
    assert report["classification"] == INCOMPLETE_CLASSIFICATION


def test_missing_or_wrong_ack_cannot_become_pass():
    for intervention in (
        None,
        {"goal": "_g4_issue_idle_attack_probe", "status": "completed", "result": {"ok": True}},
        {"goal": "_g4_idle_waypoint_reinforcement_probe", "status": "completed", "result": {"ok": 1}},
    ):
        runtime = _runtime(_source())
        if intervention is None:
            del runtime["g4_intervention"]
        else:
            runtime["g4_intervention"] = intervention
        report = summarize(runtime, _probe())
        assert report["pass"] is False
        assert report["evidence_status"] == "BLOCKED"


def test_command3_only_once_then_command4_movement_cannot_pass():
    runtime = _runtime(_source())
    for sample in runtime["g4_ai_smoke"]["samples"]:
        if sample["tick"] == 120:
            sample["units"][0]["command"] = 4
    report = summarize(runtime, _probe())
    assert report["pass"] is False
    row = report["admitted_owners"][0]
    assert row["command3_sample_count"] == 1
    assert row["command3_aligned_movement"] is False
