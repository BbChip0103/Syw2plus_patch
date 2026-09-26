#!/usr/bin/env python3
"""Validate one-shot G4 waypoint reinforcement admission and movement evidence.

The probe is deliberately kept separate from the runtime's broad product verdict.  It
answers only whether each *admitted* source subsequently issued command 3 and moved
as the same ``(slot, source_full_id, owner)`` identity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

SCHEMA = "syw2plus.g4.waypoint_probe_outcomes.v1"
PASS_CLASSIFICATION = "WAYPOINT_REINFORCEMENT_MOVEMENT_PASS"
NO_ADMITTED_CLASSIFICATION = "NO_ADMITTED_ORDER"
INCOMPLETE_CLASSIFICATION = "INCOMPLETE_OR_NO_MOVEMENT"
MALFORMED_CLASSIFICATION = "MALFORMED_PROBE"
LIMITATIONS = [
    "one waypoint movement only",
    "no group membership/persistent AI/LAN/quality proof",
    "runtime/probe association is operational provenance from the same private-prefix capture; no cryptographic requestid binding is present",
]

_REQUIRED_FIELDS = (
    "owner", "tick", "source_full_id", "slot", "group", "target",
    "before_pending", "after_pending", "after_pending_xy", "expected_xy",
    "admitted", "skip_reason",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _int(value: Any, name: str, *, hex_string: bool = False) -> int:
    """Read a JSON integer, accepting the probe writer's quoted ``0x`` fields."""
    if isinstance(value, bool):
        raise ValueError(f"{name} is not an integer")
    if isinstance(value, int):
        return value
    if hex_string and isinstance(value, str):
        text = value.strip()
        if text.lower().startswith("0x"):
            try:
                return int(text, 16)
            except ValueError as exc:
                raise ValueError(f"{name} is not an integer") from exc
    raise ValueError(f"{name} is not an integer")


def _runtime_samples(document: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    smoke = document.get("g4_ai_smoke")
    if not isinstance(smoke, Mapping):
        raise ValueError("runtime capture lacks g4_ai_smoke")
    samples = smoke.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError("runtime capture has no G4 samples")
    result: list[Mapping[str, Any]] = []
    previous_tick: int | None = None
    for index, sample in enumerate(samples):
        if not isinstance(sample, Mapping):
            raise ValueError(f"runtime sample {index} is not an object")
        tick = sample.get("tick")
        units = sample.get("units")
        if not isinstance(tick, int) or isinstance(tick, bool) or not isinstance(units, list):
            raise ValueError(f"runtime sample {index} tick/units are malformed")
        if previous_tick is not None and tick < previous_tick:
            raise ValueError("runtime sample ticks are not nondecreasing")
        previous_tick = tick
        result.append(sample)
    return result


def _probe_records(document: Mapping[str, Any]) -> list[dict[str, Any]]:
    if document.get("schema_version") != 1:
        raise ValueError("probe schema_version must be 1")
    owners = document.get("owners")
    if not isinstance(owners, list):
        raise ValueError("probe owners is not a list")
    if len(owners) > 8:
        raise ValueError("probe owners has more than 8 records")
    records: list[dict[str, Any]] = []
    seen_owners: set[int] = set()
    for index, raw in enumerate(owners):
        if not isinstance(raw, Mapping):
            raise ValueError(f"probe owner {index} is not an object")
        missing = [field for field in _REQUIRED_FIELDS if field not in raw]
        if missing:
            raise ValueError(f"probe owner {index} lacks {','.join(missing)}")
        owner = _int(raw["owner"], f"probe owner {index}.owner")
        tick = _int(raw["tick"], f"probe owner {index}.tick")
        if owner not in range(8):
            raise ValueError(f"probe owner {index}.owner is outside 0..7")
        if owner in seen_owners:
            raise ValueError(f"probe owner {index}.owner is duplicated")
        seen_owners.add(owner)
        source_full_id = _int(raw["source_full_id"], f"probe owner {index}.source_full_id")
        slot = _int(raw["slot"], f"probe owner {index}.slot")
        group = _int(raw["group"], f"probe owner {index}.group")
        target = raw["target"]
        if (not isinstance(target, list) or len(target) != 2
                or any(isinstance(value, bool) or not isinstance(value, int) for value in target)):
            raise ValueError(f"probe owner {index}.target is malformed")
        before_pending = _int(raw["before_pending"], f"probe owner {index}.before_pending")
        after_pending = _int(raw["after_pending"], f"probe owner {index}.after_pending")
        after_pending_xy = _int(raw["after_pending_xy"], f"probe owner {index}.after_pending_xy", hex_string=True)
        expected_xy = _int(raw["expected_xy"], f"probe owner {index}.expected_xy", hex_string=True)
        admitted = raw["admitted"]
        if not isinstance(admitted, bool):
            raise ValueError(f"probe owner {index}.admitted is not boolean")
        skip_reason = raw["skip_reason"]
        if not isinstance(skip_reason, str):
            raise ValueError(f"probe owner {index}.skip_reason is not a string")
        record = dict(raw)
        record.update({
            "owner": owner, "tick": tick, "source_full_id": source_full_id,
            "slot": slot, "group": group, "target": list(target),
            "before_pending": before_pending, "after_pending": after_pending,
            "after_pending_xy": after_pending_xy, "expected_xy": expected_xy,
            "admitted": admitted, "skip_reason": skip_reason,
        })
        records.append(record)
    return records


def _player_ai(sample: Mapping[str, Any], owner: int) -> bool | None:
    players = sample.get("players")
    if not isinstance(players, list):
        return None
    for player in players:
        if isinstance(player, Mapping) and player.get("owner") == owner:
            value = player.get("ai")
            return value if isinstance(value, bool) else (value == 1 if isinstance(value, int) else None)
    return None


def _unit_identity(unit: Mapping[str, Any]) -> tuple[int, int, int] | None:
    slot = unit.get("slot")
    full_id = unit.get("internal_id", unit.get("source_full_id"))
    owner = unit.get("owner")
    if (isinstance(slot, bool) or not isinstance(slot, int)
            or isinstance(full_id, bool) or not isinstance(full_id, int)
            or isinstance(owner, bool) or not isinstance(owner, int)):
        return None
    return (slot, full_id, owner)


def _movement(record: Mapping[str, Any], samples: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    owner = int(record["owner"])
    slot = int(record["slot"])
    source_id = int(record["source_full_id"])
    target = (int(record["target"][0]), int(record["target"][1]))
    identity = (slot, source_id, owner)
    post = [sample for sample in samples if isinstance(sample.get("tick"), int)
            and sample["tick"] > int(record["tick"])]
    observations: list[dict[str, Any]] = []
    identity_reused = False
    for sample in post:
        units = sample.get("units")
        if not isinstance(units, list):
            continue
        for raw_unit in units:
            if not isinstance(raw_unit, Mapping):
                continue
            unit_identity = _unit_identity(raw_unit)
            if unit_identity is None or unit_identity[0] != slot or unit_identity[2] != owner:
                continue
            if unit_identity != identity:
                # A replacement in the same slot is not the source unit.  Do not
                # let its later position or command be attributed to this order.
                identity_reused = True
                continue
            x, y, command = raw_unit.get("x"), raw_unit.get("y"), raw_unit.get("command")
            if any(isinstance(value, bool) or not isinstance(value, int) for value in (x, y, command)):
                continue
            observations.append({"tick": sample["tick"], "x": x, "y": y, "command": command})
    positions = [(item["x"], item["y"]) for item in observations]
    first = list(positions[0]) if positions else None
    last = list(positions[-1]) if positions else None
    gaps = [max(abs(x - target[0]), abs(y - target[1])) for x, y in positions]
    distinct = len(set(positions))
    displacement = (max(abs(last[0] - first[0]), abs(last[1] - first[1]))
                    if first is not None and last is not None else None)
    pre = [sample for sample in samples if isinstance(sample.get("tick"), int)
           and sample["tick"] <= int(record["tick"])]
    pre_sample = max(pre, key=lambda sample: sample["tick"]) if pre else None
    first_post = post[0] if post else None
    ai_before = _player_ai(pre_sample, owner) if pre_sample is not None else None
    ai_after = _player_ai(first_post, owner) if first_post is not None else None
    ai_ok = ai_before is True and ai_after is True
    command3_observations = [item for item in observations if item["command"] == 3]
    command3_positions = [(item["x"], item["y"]) for item in command3_observations]
    command3_distinct = len(set(command3_positions))
    command3_displacement = (
        max(abs(command3_positions[-1][0] - command3_positions[0][0]),
            abs(command3_positions[-1][1] - command3_positions[0][1]))
        if command3_positions else None
    )
    command3 = bool(command3_observations)
    moved = distinct > 1
    command3_aligned_movement = len(command3_observations) >= 2 and command3_distinct > 1
    enough_samples = len(observations) >= 2
    row: dict[str, Any] = {
        "owner": owner, "slot": slot, "source_full_id": source_id,
        "tick": int(record["tick"]), "target": list(target),
        "post_sample_count": len(observations), "first_coords": first, "last_coords": last,
        # Keep sibling movement-outcome terminology available to downstream reports.
        "first_position": first, "last_position": last,
        "distinct_count": distinct, "chebyshev_displacement": displacement,
        "target_initial_gap": gaps[0] if gaps else None,
        "target_min_gap": min(gaps) if gaps else None,
        "target_last_gap": gaps[-1] if gaps else None,
        "arrived_within5": bool(gaps and min(gaps) <= 5),
        "command3_observed": command3,
        "command3_sample_count": len(command3_observations),
        "command3_distinct_count": command3_distinct,
        "command3_chebyshev_displacement": command3_displacement,
        "command3_aligned_movement": command3_aligned_movement,
        "identity_reused": identity_reused,
        "ai_before": ai_before, "ai_after": ai_after, "ai_owner_verified": ai_ok,
        "enough_samples": enough_samples, "moved": moved,
    }
    row["movement_pass"] = bool(
        enough_samples and command3_aligned_movement and moved and ai_ok and not identity_reused
    )
    return row


def _runtime_gate(runtime: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    """Require an acknowledged, successful waypoint intervention, not stale movement."""
    gaps: list[str] = []
    intervention = runtime.get("g4_intervention")
    smoke = runtime.get("g4_ai_smoke")
    intervention_mapping = intervention if isinstance(intervention, Mapping) else {}
    result = intervention_mapping.get("result")
    result_mapping = result if isinstance(result, Mapping) else {}
    smoke_mapping = smoke if isinstance(smoke, Mapping) else {}
    checks = {
        "intervention_present": isinstance(intervention, Mapping),
        "intervention_status_completed": intervention_mapping.get("status") == "completed",
        "intervention_goal_waypoint": intervention_mapping.get("goal") == "_g4_idle_waypoint_reinforcement_probe",
        "intervention_result_mapping": isinstance(result, Mapping),
        "intervention_result_ok": result_mapping.get("ok") is True,
        "smoke_present": isinstance(smoke, Mapping),
        "smoke_error_none": "error" in smoke_mapping and smoke_mapping.get("error") is None,
    }
    for name, passed in checks.items():
        if not passed:
            gaps.append("runtime_gate_" + name)
    return {"checks": checks, "status": "VALID" if not gaps else "BLOCKED"}, gaps


def _runtime_context(runtime: Mapping[str, Any]) -> tuple[dict[str, Any], list[str]]:
    gaps: list[str] = []
    cleanup = runtime.get("cleanup")
    if isinstance(cleanup, Mapping) and cleanup.get("ok") is False:
        gaps.append("runtime_cleanup_not_ok")
    error = runtime.get("error")
    if error:
        gaps.append("runtime_top_level_error")
    context: dict[str, Any] = {
        "overall": runtime.get("overall"),
        "error": error,
        "cleanup": cleanup,
    }
    for key in ("input_checks", "ui_tail", "teardown"):
        if key in runtime:
            context[key] = runtime[key]
    return context, gaps


def summarize(runtime: Mapping[str, Any], probe: Mapping[str, Any],
              *, runtime_path: Path | None = None, probe_path: Path | None = None) -> dict[str, Any]:
    """Return a non-passing report for every malformed or incomplete input."""
    provenance: dict[str, Any] = {}
    if runtime_path is not None:
        provenance["runtime"] = {"path": str(runtime_path), "sha256": _sha256(runtime_path)}
    if probe_path is not None:
        provenance["probe"] = {"path": str(probe_path), "sha256": _sha256(probe_path)}
    context, validation_gaps = _runtime_context(runtime)
    runtime_gate, runtime_gate_gaps = _runtime_gate(runtime)
    validation_gaps.extend(runtime_gate_gaps)
    try:
        samples = _runtime_samples(runtime)
        records = _probe_records(probe)
        if records:
            first_tick = samples[0]["tick"]
            last_tick = samples[-1]["tick"]
            assert isinstance(first_tick, int) and isinstance(last_tick, int)
            out_of_range = [record["owner"] for record in records
                            if not first_tick <= record["tick"] <= last_tick]
            if out_of_range:
                raise ValueError(
                    "probe tick is outside runtime sample range for owner(s): "
                    + ",".join(str(owner) for owner in out_of_range)
                )
    except ValueError as exc:
        return {
            "schema": SCHEMA, "pass": False, "classification": MALFORMED_CLASSIFICATION,
            "admitted_count": 0, "owners": [], "skipped_owners": [],
            "provenance": provenance, "runtime_context": context,
            "runtime_gate": runtime_gate,
            "evidence_status": "BLOCKED",
            "validation_gaps": validation_gaps + [str(exc)], "limitations": LIMITATIONS,
        }

    admitted: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    owner_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_owners: set[int] = set()
    for index, record in enumerate(records):
        if not record["admitted"]:
            no_selected_source = record["slot"] < 0 or record["source_full_id"] == 0
            skipped_row = {
                "owner": record["owner"], "tick": record["tick"], "slot": record["slot"],
                "source_full_id": record["source_full_id"], "group": record["group"],
                "target": record["target"], "admitted": False, "order_admitted": False,
                "skip_reason": record["skip_reason"],
                "touch_status": ("no_selected_source" if no_selected_source
                                 else "not_admitted_not_proof_of_no_call"),
            }
            skipped.append(skipped_row)
            owner_rows.append(skipped_row)
            continue
        target_x, target_y = record["target"]
        expected_xy = (target_y << 16) | target_x
        guards = {
            "owner_in_range": record["owner"] in range(8),
            "owner_unique": record["owner"] not in seen_owners,
            "slot_in_range": 1 <= record["slot"] <= 1199,
            "source_slot_match": (record["source_full_id"] & 0xFFFF) == record["slot"],
            "before_pending_low16_is_one": (record["before_pending"] & 0xFFFF) == 1,
            "after_pending_admitted": record["after_pending"] == 0x00010003,
            "after_pending_xy_match": record["after_pending_xy"] == expected_xy,
            "expected_xy_match": record["expected_xy"] == expected_xy,
            "target_in_bounds": 0 <= target_x <= 179 and 0 <= target_y <= 179,
        }
        seen_owners.add(record["owner"])
        if not all(guards.values()):
            errors.append(f"admitted owner {record['owner']} failed admission guards")
            row = {**record, "order_admitted": True, "guards": guards, "movement_pass": False}
            admitted.append(row)
            owner_rows.append(row)
            continue
        movement = _movement(record, samples)
        row = {**record, "order_admitted": True, "guards": guards, **movement}
        admitted.append(row)
        owner_rows.append(row)

    admitted_count = len(admitted)
    movement_pass = bool(
        admitted_count and not errors and runtime_gate["status"] == "VALID"
        and all(row.get("movement_pass") for row in admitted)
    )
    if errors:
        classification = MALFORMED_CLASSIFICATION
    elif not admitted_count:
        classification = NO_ADMITTED_CLASSIFICATION
    elif movement_pass:
        classification = PASS_CLASSIFICATION
    else:
        classification = INCOMPLETE_CLASSIFICATION
    return {
        "schema": SCHEMA,
        "pass": movement_pass,
        "classification": classification,
        "admitted_count": admitted_count,
        "moved_admitted_count": sum(bool(row.get("movement_pass")) for row in admitted),
        "owners": owner_rows,
        "admitted_owners": admitted,
        "skipped_owners": skipped,
        "provenance": provenance,
        "runtime_context": context,
        "runtime_gate": runtime_gate,
        "evidence_status": "VALID" if runtime_gate["status"] == "VALID" else "BLOCKED",
        "validation_gaps": validation_gaps + errors,
        "limitations": LIMITATIONS,
        "movement_verdict": classification,
        "product_verdict": "NOT_EVALUATED",
    }


def validate(runtime: Mapping[str, Any], probe: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    """Alias for callers that use validator terminology."""
    return summarize(runtime, probe, **kwargs)


def build_report(runtime_path: Path, probe_path: Path) -> dict[str, Any]:
    return summarize(
        json.loads(runtime_path.read_text(encoding="utf-8")),
        json.loads(probe_path.read_text(encoding="utf-8")),
        runtime_path=runtime_path, probe_path=probe_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime_json", type=Path)
    parser.add_argument("probe_json", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = build_report(args.runtime_json, args.probe_json)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
