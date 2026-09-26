#!/usr/bin/env python3
"""Validate existing ``runtime_driver.py`` state/trace evidence, read only.

The CLI accepts exactly one ``--state`` snapshot JSON or ``--trace`` JSONL,
plus the driver's ``session.json`` and an expected executable SHA-256.  A state
has ``pid``, ``time``, ``ps``, ``tick`` and ``players``; each player has
``owner``, ``nation``, ``ai``, ``count``, ``used``, ``count_cap`` and ``cap``.
A nonzero nation is only a configured-slot candidate.  The report's
``active_proxy`` additionally requires PROGRAM_STATE3 (``ps == 3``) and a
positive player count; neither proxy is proof of real human/AI activity or
successful gameplay.  Empty slots and cap-only observations therefore cannot
satisfy G2/G3.

The checker never starts Wine/game/X11 and never edits inputs.  RSS, when
present, is an observation only and never proves absence of OOM, allocation
failure, or crash.  Existing telemetry is eight player records and a 1200
entry object table; this does not establish G3/16-player support.  G2/G3
remain incomplete until behavioral evidence (production, combat, save/load,
and where applicable synchronization) exists. Exit status is 0 only for a
selected structural ``pass`` gate; these checks do not claim product support.
"""


from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from typing import Any, Iterator

SCHEMA = "runtime-evidence/v1"
TARGET_SUPPLY = 5000
PLAYER_FIELDS = ("owner", "nation", "ai", "count", "used", "count_cap", "cap")
STATE_FIELDS = ("pid", "time", "ps", "tick", "players")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _unwrap_state(value: Any) -> Any:
    if isinstance(value, dict) and isinstance(value.get("state"), dict):
        return value["state"]
    return value


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _state_errors(state: Any, index: int) -> list[str]:
    prefix = f"sample {index}"
    if not isinstance(state, dict):
        return [f"{prefix}: state is not an object"]
    errors = [f"{prefix}: missing field {field}" for field in STATE_FIELDS if field not in state]
    for field in ("pid", "ps", "tick"):
        if field in state and not _integer(state[field]):
            errors.append(f"{prefix}: {field} is not an integer")
    if "time" in state and not _number(state["time"]):
        errors.append(f"{prefix}: time is not numeric")
    players = state.get("players")
    if not isinstance(players, list):
        if "players" in state:
            errors.append(f"{prefix}: players is not a list")
        return errors
    owners: set[int] = set()
    for player_index, player in enumerate(players):
        pp = f"{prefix} player {player_index}"
        if not isinstance(player, dict):
            errors.append(f"{pp}: player is not an object")
            continue
        errors.extend(f"{pp}: missing field {field}" for field in PLAYER_FIELDS if field not in player)
        if "owner" in player:
            if not _integer(player["owner"]):
                errors.append(f"{pp}: owner is not an integer")
            elif player["owner"] in owners:
                errors.append(f"{pp}: duplicate owner {player['owner']}")
            else:
                owners.add(player["owner"])
        for field in PLAYER_FIELDS[1:]:
            if field in player and not _integer(player[field]):
                errors.append(f"{pp}: {field} is not an integer")
    return errors


def load_state(path: Path) -> tuple[Any, list[str]]:
    """Read one state JSON, preserving parse errors in the report."""
    try:
        return _unwrap_state(json.loads(path.read_text(encoding="utf-8"))), []
    except (OSError, UnicodeError) as exc:
        return None, [f"state input: {exc}"]
    except json.JSONDecodeError as exc:
        return None, [f"state input: invalid JSON ({exc})"]


def load_trace(path: Path) -> tuple[list[Any], list[str]]:
    """Read runtime_driver JSON-lines trace; blank lines are ignored."""
    samples: list[Any] = []
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return [], [f"trace input: {exc}"]
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            samples.append(_unwrap_state(json.loads(line)))
        except json.JSONDecodeError as exc:
            errors.append(f"trace line {line_number}: invalid JSON ({exc})")
    return samples, errors


def _iter_rss(state: dict[str, Any]) -> Iterator[float]:
    for key in ("rss", "rss_bytes", "memory_rss", "memory_rss_bytes"):
        value = state.get(key)
        if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
            yield float(value)
    memory = state.get("memory")
    if isinstance(memory, dict):
        for key in ("rss", "rss_bytes"):
            value = memory.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool) and value >= 0:
                yield float(value)


def _artifact_report(session_path: Path | None, expected: str | None) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    observed: str | None = None
    if expected is not None:
        expected = expected.lower()
        if not SHA256_RE.fullmatch(expected):
            errors.append("expected artifact hash is not a 64-digit SHA-256")
    if session_path is None:
        errors.append("session input is required for artifact identity")
    else:
        try:
            session = json.loads(session_path.read_text(encoding="utf-8"))
            if not isinstance(session, dict):
                errors.append("session input is not an object")
            else:
                raw = session.get("exe_sha256")
                if isinstance(raw, str) and SHA256_RE.fullmatch(raw.lower()):
                    observed = raw.lower()
                else:
                    errors.append("session missing valid exe_sha256")
        except (OSError, UnicodeError) as exc:
            errors.append(f"session input: {exc}")
        except json.JSONDecodeError as exc:
            errors.append(f"session input: invalid JSON ({exc})")
    if expected is None:
        errors.append("expected artifact hash was not provided")
    if expected is not None and observed is not None and expected != observed:
        errors.append(f"artifact hash mismatch: expected {expected}, observed {observed}")
    status = "pass" if not errors else "fail"
    if expected is None or observed is None:
        status = "incomplete"
    return {"status": status, "expected_sha256": expected, "observed_sha256": observed, "errors": errors}, errors


def evaluate(
    *,
    session: Path | None = None,
    state: Path | None = None,
    trace: Path | None = None,
    expected_sha256: str | None = None,
    goal: str = "smoke",
) -> dict[str, Any]:
    """Return a JSON-compatible validation report for state/trace inputs."""
    if goal not in {"smoke", "g2", "g3"}:
        raise ValueError(f"unknown goal: {goal}")
    if state is None and trace is None:
        source_errors = ["one of --state or --trace is required"]
        samples: list[Any] = []
        source = None
    elif state is not None and trace is not None:
        source_errors = ["provide only one of --state or --trace"]
        samples = []
        source = None
    elif state is not None:
        one, source_errors = load_state(state)
        samples = [one] if one is not None else []
        source = str(state)
    else:
        samples, source_errors = load_trace(trace)  # type: ignore[arg-type]
        source = str(trace)

    schema_errors = list(source_errors)
    for index, sample in enumerate(samples, 1):
        schema_errors.extend(_state_errors(sample, index))
    valid_states = [
        sample for index, sample in enumerate(samples, 1) if not _state_errors(sample, index)
    ]

    rollback_events: list[dict[str, int]] = []
    previous_tick: int | None = None
    for index, sample in enumerate(samples, 1):
        if not isinstance(sample, dict) or not _integer(sample.get("tick")):
            continue
        tick = sample["tick"]
        if previous_tick is not None and tick < previous_tick:
            rollback_events.append(
                {
                    "from_sample": index - 1,
                    "to_sample": index,
                    "from_tick": previous_tick,
                    "to_tick": tick,
                }
            )
        previous_tick = tick
    continuity_errors = [
        f"tick rollback at sample {event['to_sample']}: {event['from_tick']} -> {event['to_tick']}"
        for event in rollback_events
    ]
    continuity_status = "pass" if samples and not continuity_errors else (
        "fail" if continuity_errors else "incomplete"
    )

    max_slots = max((len(s.get("players", [])) for s in valid_states), default=0)
    active_proxy_by_sample: list[list[int]] = []
    configured_owners_seen: set[int] = set()
    active_proxy_owners_seen: set[int] = set()
    per_owner: dict[str, dict[str, Any]] = {}
    rss: list[float] = []
    for sample in valid_states:
        players = sample.get("players", [])
        active_proxy: list[int] = []
        for player in players:
            owner = player.get("owner")
            if not _integer(owner):
                continue
            owner_key = str(owner)
            is_configured = _integer(player.get("nation")) and player["nation"] != 0
            if is_configured:
                configured_owners_seen.add(owner)
            is_active_proxy = (
                is_configured
                and sample.get("ps") == 3
                and _integer(player.get("count"))
                and player["count"] > 0
            )
            if is_active_proxy:
                active_proxy.append(owner)
                active_proxy_owners_seen.add(owner)
            detail = per_owner.setdefault(
                owner_key,
                {
                    "samples": 0,
                    "configured_samples": 0,
                    "active_proxy_samples": 0,
                    "cap_values": [],
                    "max_used": None,
                    "reached_target": False,
                },
            )
            detail["samples"] += 1
            if is_configured:
                detail["configured_samples"] += 1
            if is_active_proxy:
                detail["active_proxy_samples"] += 1
                if _integer(player.get("cap")):
                    detail["cap_values"].append(player["cap"])
                if _integer(player.get("used")):
                    detail["max_used"] = max(detail["max_used"] or player["used"], player["used"])
                    detail["reached_target"] = detail["reached_target"] or player["used"] >= TARGET_SUPPLY
        active_proxy_by_sample.append(active_proxy)
        rss.extend(_iter_rss(sample))
    max_active_proxy = max((len(owners) for owners in active_proxy_by_sample), default=0)
    simultaneous_8 = any(len(owners) >= 8 for owners in active_proxy_by_sample)
    g2_errors: list[str] = []
    if not simultaneous_8:
        g2_errors.append(
            f"fewer than 8 simultaneous active_proxy candidates (max {max_active_proxy}); "
            "configured slots are not proof of real player activity"
        )
    qualifying_sample = next((owners for owners in active_proxy_by_sample if len(owners) >= 8), [])
    for owner in qualifying_sample[:8]:
        detail = per_owner[str(owner)]
        if TARGET_SUPPLY not in detail["cap_values"]:
            g2_errors.append(f"owner {owner} has no observed cap=5000")
        if not detail["reached_target"]:
            g2_errors.append(f"owner {owner} has cap=5000 but never observed used>=5000")

    artifact, artifact_errors = _artifact_report(session, expected_sha256)
    memory_status = "observed_not_oom_proof" if rss else "missing"
    memory = {
        "status": memory_status,
        "rss_samples": len(rss),
        "rss_min": min(rss) if rss else None,
        "rss_max": max(rss) if rss else None,
        "oom_proof": False,
        "note": "RSS is an observation and does not prove absence of OOM, allocation failure, or crash.",
    }
    g2_errors.append(
        "behavioral evidence is missing; state telemetry does not prove real player activity"
    )
    g2_errors.append(
        "memory health remains unproven: RSS alone is not OOM proof"
        if rss
        else "memory health evidence missing; RSS alone would not prove no OOM"
    )

    smoke_errors = list(schema_errors) + list(artifact_errors) + continuity_errors
    smoke_status = "pass" if samples and not smoke_errors else (
        "fail" if smoke_errors else "incomplete"
    )
    g2_status = "pass" if not g2_errors and smoke_status == "pass" else (
        "fail" if smoke_status == "fail" else "incomplete"
    )
    g3_errors: list[str] = []
    if max_slots < 16:
        g3_errors.append(
            f"only {max_slots} player records observed; existing runtime telemetry is 8-slot and does not establish 16-player support"
        )
    if max_active_proxy < 16:
        g3_errors.append(
            f"fewer than 16 simultaneous active_proxy candidates (max {max_active_proxy}); "
            "configured slots are not proof of real player activity"
        )
    g3_errors.append("behavioral evidence is missing; state telemetry does not prove real player activity")
    g3_status = "unsupported" if 0 < max_slots < 16 else (
        "pass" if not g3_errors and smoke_status == "pass" else (
            "fail" if smoke_status == "fail" else "incomplete"
        )
    )
    gate = {"smoke": smoke_status, "g2": g2_status, "g3": g3_status}[goal]
    return {
        "schema": SCHEMA,
        "status": gate,
        "goal": goal,
        "source": source,
        "artifact": artifact,
        "trace": {
            "samples": len(samples),
            "valid_samples": len(valid_states),
            "schema_errors": schema_errors,
            "tick_min": min((s["tick"] for s in valid_states), default=None),
            "tick_max": max((s["tick"] for s in valid_states), default=None),
            "rollback_events": rollback_events,
            "continuity_status": continuity_status,
        },
        "players": {
            "max_records": max_slots,
            "max_configured_candidates": max((len(owners) for owners in [
                [p.get("owner") for p in s.get("players", [])
                 if _integer(p.get("nation")) and p["nation"] != 0]
                for s in valid_states
            ]), default=0),
            "max_simultaneous_active_proxy": max_active_proxy,
            "configured_owners_seen": sorted(configured_owners_seen),
            "active_proxy_owners_seen": sorted(active_proxy_owners_seen),
            "empty_or_inactive_records": max_slots - max_active_proxy if max_slots else 0,
            "definition": (
                "configured candidate iff nation != 0; active_proxy additionally requires "
                "ps == 3 and count > 0; neither proves real player activity"
            ),
        },
        "supply": {"target_cap": TARGET_SUPPLY, "per_owner": per_owner, "g2_errors": g2_errors},
        "memory": memory,
        "gates": {
            "smoke": {"status": smoke_status, "errors": smoke_errors},
            "g2": {"status": g2_status, "errors": g2_errors},
            "g3": {"status": g3_status, "errors": g3_errors},
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--state", type=Path, help="runtime_driver latest/snapshot JSON")
    source.add_argument("--trace", type=Path, help="runtime_driver trace JSONL")
    parser.add_argument("--session", type=Path, required=True, help="runtime_driver session.json")
    parser.add_argument(
        "--expected-sha256", "--expected-artifact-sha256", dest="expected_sha256", required=True
    )
    parser.add_argument("--goal", choices=("smoke", "g2", "g3"), default="smoke")
    parser.add_argument("--pretty", action="store_true", help="indent JSON output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = evaluate(
        session=args.session,
        state=args.state,
        trace=args.trace,
        expected_sha256=args.expected_sha256,
        goal=args.goal,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
