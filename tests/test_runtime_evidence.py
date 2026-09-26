"""Synthetic, labeled fixtures for the fail-closed runtime evidence checker."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("check_runtime_evidence", ROOT / "tools/check_runtime_evidence.py")
assert SPEC and SPEC.loader
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

HASH = "a" * 64


def player(owner: int, *, nation: int = 0, used: int = 0, cap: int = 5000) -> dict[str, int]:
    return {
        "owner": owner,
        "nation": nation,
        "ai": 1,
        "count": 2 if nation else 0,
        "used": used,
        "count_cap": 250,
        "cap": cap,
    }


def state(tick: int = 1, players: list[dict[str, int]] | None = None, **extra: object) -> dict[str, object]:
    return {"pid": 42, "time": 1.0 + tick, "ps": 3, "tick": tick, "players": players or [player(0)], **extra}


def write_inputs(tmp_path: Path, samples: list[dict[str, object]], *, session: bool = True):
    trace = tmp_path / "trace.jsonl"
    trace.write_text("\n".join(json.dumps(item) for item in samples) + "\n")
    session_path = tmp_path / "session.json"
    if session:
        session_path.write_text(json.dumps({"exe_sha256": HASH}))
    return trace, session_path


def test_labeled_fixture_missing_required_fields_fails_closed(tmp_path: Path):
    trace, session = write_inputs(tmp_path, [{"pid": 42, "tick": 1, "players": []}])
    report = checker.evaluate(trace=trace, session=session, expected_sha256=HASH)
    assert report["status"] == "fail"
    assert any("missing field time" in error for error in report["trace"]["schema_errors"])


def test_labeled_fixture_tick_reset_is_reported_as_rollback(tmp_path: Path):
    trace, session = write_inputs(tmp_path, [state(10), state(9)])
    report = checker.evaluate(trace=trace, session=session, expected_sha256=HASH)
    assert report["status"] == "fail"
    assert report["trace"]["rollback_events"] == [
        {"from_sample": 1, "to_sample": 2, "from_tick": 10, "to_tick": 9}
    ]


def test_labeled_fixture_empty_eight_slots_are_not_active_players(tmp_path: Path):
    players = [player(owner) for owner in range(8)]
    trace, session = write_inputs(tmp_path, [state(players=players)])
    report = checker.evaluate(trace=trace, session=session, expected_sha256=HASH, goal="g2")
    assert report["players"]["max_records"] == 8
    assert report["players"]["max_simultaneous_active_proxy"] == 0
    assert report["status"] == "incomplete"
    assert any("active_proxy" in error for error in report["supply"]["g2_errors"])


def test_labeled_fixture_nation_set_but_zero_count_is_not_active_proxy(tmp_path: Path):
    players = [player(owner, nation=owner + 1, used=5000) for owner in range(8)]
    for item in players:
        item["count"] = 0
    trace, session = write_inputs(tmp_path, [state(players=players)])
    report = checker.evaluate(trace=trace, session=session, expected_sha256=HASH, goal="g2")
    assert report["players"]["max_configured_candidates"] == 8
    assert report["players"]["max_simultaneous_active_proxy"] == 0
    assert any("active_proxy" in error for error in report["supply"]["g2_errors"])


def test_labeled_fixture_cap5000_without_used5000_does_not_pass_g2(tmp_path: Path):
    players = [player(owner, nation=owner + 1, used=0, cap=5000) for owner in range(8)]
    trace, session = write_inputs(tmp_path, [state(players=players)])
    report = checker.evaluate(trace=trace, session=session, expected_sha256=HASH, goal="g2")
    assert report["status"] == "incomplete"
    assert all(detail["cap_values"] == [5000] for detail in report["supply"]["per_owner"].values())
    assert all(not detail["reached_target"] for detail in report["supply"]["per_owner"].values())
    assert any("never observed used>=5000" in error for error in report["supply"]["g2_errors"])


def test_labeled_fixture_eight_slot_telemetry_is_unsupported_for_g3(tmp_path: Path):
    players = [player(owner, nation=owner + 1, used=5000) for owner in range(8)]
    trace, session = write_inputs(tmp_path, [state(players=players)])
    report = checker.evaluate(trace=trace, session=session, expected_sha256=HASH, goal="g3")
    assert report["status"] == "unsupported"
    assert report["players"]["max_records"] == 8
    assert "16-player support" in " ".join(report["gates"]["g3"]["errors"])


def test_rss_is_observation_not_oom_proof(tmp_path: Path):
    trace, session = write_inputs(tmp_path, [state(rss_bytes=123456)])
    report = checker.evaluate(trace=trace, session=session, expected_sha256=HASH)
    assert report["memory"]["status"] == "observed_not_oom_proof"
    assert report["memory"]["oom_proof"] is False
