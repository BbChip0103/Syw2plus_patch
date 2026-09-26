#!/usr/bin/env python3
"""Read-only S1 load evidence over a selected save fixture.

This lane is intentionally separate from the live R1 origin observer.  It
does not start a process or inspect the game.  A future post-PS3 collector
can use :func:`read_post_player_structs`, then pass its raw records to the
same evaluator used by this offline CLI.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import time
from typing import Any, Callable, Mapping, Sequence


PLAYER_BASE = 0x00956770
PLAYER_STRIDE = 0x3ABC
PLAYER_COUNT = 8
PLAYER_RECORD_SIZE = 6
GROUP_WORD_ADDRESS = 0x0066966C
LOAD_DIALOG_OBJECT_ADDRESS = 0x01086278
SELECTED_INDEX_OFFSET = 0xF9E
SELECTED_INDEX_ADDRESS = LOAD_DIALOG_OBJECT_ADDRESS + SELECTED_INDEX_OFFSET
PROGRAM_STATE_ADDRESS = 0x004ED818
LOAD_COMPLETE_PS = 3
PLAYER_FIELDS = (
    "nation",
    "player_num",
    "is_cpu",
    "self_bit_mask",
    "opponent_mask",
    "team_num",
)


@dataclass(frozen=True)
class FixtureSpec:
    name: str
    expected_size: int
    expected_sha256: str
    selected_index: int
    player0_file_offset: int


FIXTURES: dict[str, FixtureSpec] = {
    "save000.dat": FixtureSpec(
        "save000.dat", 3_093_902,
        "1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da",
        1, 2_259_634,
    ),
    "save006.dat": FixtureSpec(
        "save006.dat", 3_437_942,
        "616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064",
        7, 2_259_634,
    ),
}

ReadMemory = Callable[[int, int], bytes]
_COLLECTOR_TOKEN = object()


class S1ReadError(RuntimeError):
    """A post-PS3 raw record could not be read completely."""

    def __init__(self, message: str, *, owner: int, address: int, requested: int, actual: int | None = None) -> None:
        super().__init__(message)
        self.owner = owner
        self.address = address
        self.requested = requested
        self.actual = actual


class S1EventBoundaryError(RuntimeError):
    """A live S1 load did not cross its verified event boundary."""

    def __init__(self, classification: str, message: str, *, boundary: Mapping[str, Any]) -> None:
        super().__init__(message)
        self.classification = classification
        self.boundary = dict(boundary)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _record(owner: int, raw: bytes, *, file_offset: int | None = None,
            memory_address: int | None = None) -> dict[str, Any]:
    if len(raw) != PLAYER_RECORD_SIZE:
        raise ValueError(f"PlayerStruct record returned {len(raw)}/{PLAYER_RECORD_SIZE} bytes")
    result: dict[str, Any] = {
        "owner": owner,
        "raw_hex": raw.hex(" "),
        "nation": raw[0],
        "player_num": raw[1],
        "is_cpu": raw[2],
        "self_bit_mask": raw[3],
        "opponent_mask": raw[4],
        "team_num": raw[5],
    }
    if file_offset is not None:
        result["file_offset"] = file_offset
    if memory_address is not None:
        result["memory_address"] = hex(memory_address)
    return result


def read_post_player_structs(read_memory: ReadMemory) -> list[dict[str, Any]]:
    """Read exactly the six documented leading bytes for all eight players."""

    records: list[dict[str, Any]] = []
    for owner in range(PLAYER_COUNT):
        address = PLAYER_BASE + owner * PLAYER_STRIDE
        try:
            raw = read_memory(address, PLAYER_RECORD_SIZE)
        except OSError as exc:
            raise S1ReadError(
                f"post-PS3 PlayerStruct read failed for owner {owner}: {exc}",
                owner=owner, address=address, requested=PLAYER_RECORD_SIZE,
            ) from exc
        if len(raw) != PLAYER_RECORD_SIZE:
            raise S1ReadError(
                f"post-PS3 PlayerStruct read returned {len(raw)}/{PLAYER_RECORD_SIZE} bytes",
                owner=owner, address=address, requested=PLAYER_RECORD_SIZE, actual=len(raw),
            )
        records.append(_record(owner, raw, memory_address=address))
    return records


def _read_word(read_memory: ReadMemory, address: int, label: str) -> int:
    try:
        raw = read_memory(address, 2)
    except OSError as exc:
        raise S1ReadError(
            f"{label} WORD read failed: {exc}",
            owner=-1, address=address, requested=2,
        ) from exc
    if len(raw) != 2:
        raise S1ReadError(
            f"{label} WORD read returned {len(raw)}/2 bytes",
            owner=-1, address=address, requested=2, actual=len(raw),
        )
    return int.from_bytes(raw, "little", signed=False)


def read_s1_snapshot(
    read_memory: ReadMemory, *, phase: str,
    player_reader: Callable[[ReadMemory], list[dict[str, Any]]] = read_post_player_structs,
    group_address: int = GROUP_WORD_ADDRESS,
    selected_index_address: int = SELECTED_INDEX_ADDRESS,
    program_state_address: int = PROGRAM_STATE_ADDRESS,
) -> dict[str, Any]:
    """Capture one directly-read S1 state sample.

    The private token is deliberately retained in-process.  It prevents a
    JSON payload copied from a fixture or caller from being treated as a live
    memory sample by :func:`evaluate`.
    """

    if phase not in {"pre", "post"}:
        raise ValueError(f"invalid S1 snapshot phase: {phase}")
    group_word = _read_word(read_memory, group_address, "group")
    selected_index = _read_word(read_memory, selected_index_address, "selected-index")
    ps = _read_word(read_memory, program_state_address, "program-state")
    players = player_reader(read_memory)
    read_points = [
        {"name": "group_word", "address": hex(group_address), "width": 2},
        {"name": "selected_index", "address": hex(selected_index_address), "width": 2},
        {"name": "program_state", "address": hex(program_state_address), "width": 2},
    ]
    read_points.extend(
        {
            "name": f"player_struct[{owner}]",
            "address": hex(PLAYER_BASE + owner * PLAYER_STRIDE),
            "width": PLAYER_RECORD_SIZE,
        }
        for owner in range(PLAYER_COUNT)
    )
    return {
        "_collector_token": _COLLECTOR_TOKEN,
        "collector": "runtime_driver.read",
        "phase": phase,
        "group_word": group_word,
        "selected_index": selected_index,
        "ps": ps,
        "players": players,
        "read_points": read_points,
    }


def collected_load_observation(
    pre_snapshot: Mapping[str, Any], post_snapshot: Mapping[str, Any],
) -> dict[str, Any]:
    """Bind two in-process collector samples into an evaluable observation."""

    if pre_snapshot.get("_collector_token") is not _COLLECTOR_TOKEN:
        raise ValueError("pre snapshot was not produced by read_s1_snapshot")
    if post_snapshot.get("_collector_token") is not _COLLECTOR_TOKEN:
        raise ValueError("post snapshot was not produced by read_s1_snapshot")
    return {
        "_collector_token": _COLLECTOR_TOKEN,
        "collector": "runtime_driver.read",
        "pre": pre_snapshot,
        "post": post_snapshot,
    }


def collect_load_event_boundary(
    read_memory: ReadMemory, *, trigger: Callable[[], object], timeout: float,
    player_reader: Callable[[ReadMemory], list[dict[str, Any]]] = read_post_player_structs,
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    precondition: Callable[[Mapping[str, Any]], Mapping[str, Any] | None] | None = None,
    event_deadline: float | None = None,
    pre_snapshot: Mapping[str, Any] | None = None,
    event_started: float | None = None,
    post_timeout: float | None = None,
) -> dict[str, Any]:
    """Collect S1 evidence across one explicit load event.

    The caller supplies the already-approved input helper as ``trigger``.  It
    is invoked once, after a direct PS=35 pre-sample and optional precondition.
    The adapter then polls only the documented PS WORD until PS=3 or one fixed
    deadline expires; the full post sample is not read before that boundary.
    ``event_deadline`` is an absolute monotonic deadline and, when supplied,
    includes the pre-sample and trigger rather than starting after them.  A
    trigger may return an integer invocation count for harnesses that can
    attest to the helper's own count; when omitted, the adapter's single
    invocation is the count.
    """

    if timeout <= 0:
        raise ValueError("S1 load wait timeout must be positive")
    if post_timeout is not None and post_timeout <= 0:
        raise ValueError("S1 post snapshot timeout must be positive")

    event_started = monotonic() if event_started is None else event_started
    if pre_snapshot is None:
        pre = read_s1_snapshot(read_memory, phase="pre", player_reader=player_reader)
    else:
        if pre_snapshot.get("_collector_token") is not _COLLECTOR_TOKEN:
            raise ValueError("pre snapshot was not produced by read_s1_snapshot")
        pre = dict(pre_snapshot)
    boundary: dict[str, Any] = {
        "status": "STARTED",
        "pre_ps": pre["ps"],
        "trigger_invocations": 0,
        "wait_ps": [],
        "timeout_seconds": timeout,
        "event_started": event_started,
    }
    if pre["ps"] != 35:
        boundary.update({"status": "UNKNOWN", "classification": "PRE_LOAD_STATE_MISMATCH"})
        raise S1EventBoundaryError(
            "PRE_LOAD_STATE_MISMATCH",
            "S1 load trigger requires a directly observed PS=35 pre-sample",
            boundary=boundary,
        )

    if precondition is not None:
        try:
            precondition_result = precondition(pre)
        except S1EventBoundaryError:
            raise
        except Exception as exc:
            boundary.update({
                "status": "UNKNOWN", "classification": "PRECONDITION_FAILURE",
                "precondition_error": f"{type(exc).__name__}: {exc}",
            })
            raise S1EventBoundaryError(
                "PRECONDITION_FAILURE", "S1 precondition failed before load trigger",
                boundary=boundary,
            ) from exc
        if precondition_result is not None:
            boundary["precondition"] = dict(precondition_result)

    if event_deadline is not None and monotonic() >= event_deadline:
        boundary.update({"status": "UNKNOWN", "classification": "EVENT_DEADLINE_EXPIRED"})
        raise S1EventBoundaryError(
            "EVENT_DEADLINE_EXPIRED", "S1 event boundary deadline expired before trigger",
            boundary=boundary,
        )

    try:
        trigger_result = trigger()
    except Exception as exc:
        boundary.update({
            "status": "UNKNOWN", "classification": "TRIGGER_FAILURE",
            "trigger_error": f"{type(exc).__name__}: {exc}",
        })
        raise S1EventBoundaryError(
            "TRIGGER_FAILURE", "S1 load trigger failed", boundary=boundary,
        ) from exc

    boundary["trigger_invocations"] = 1
    if isinstance(trigger_result, int) and not isinstance(trigger_result, bool):
        boundary["reported_trigger_invocations"] = trigger_result
        if trigger_result != 1:
            boundary.update({"status": "UNKNOWN", "classification": "TRIGGER_COUNT_MISMATCH"})
            raise S1EventBoundaryError(
                "TRIGGER_COUNT_MISMATCH",
                f"S1 load trigger reported {trigger_result} invocations; exactly one is required",
                boundary=boundary,
            )

    started = monotonic()
    if event_deadline is not None and started >= event_deadline:
        boundary.update({"status": "UNKNOWN", "classification": "EVENT_DEADLINE_EXPIRED"})
        raise S1EventBoundaryError(
            "EVENT_DEADLINE_EXPIRED", "S1 event boundary deadline expired after trigger",
            boundary=boundary,
        )
    deadline = min(started + timeout, event_deadline) if event_deadline is not None else started + timeout
    boundary["event_deadline"] = deadline
    while True:
        now = monotonic()
        if now >= deadline:
            boundary.update({"status": "UNKNOWN", "classification": "PS3_WAIT_TIMEOUT"})
            raise S1EventBoundaryError(
                "PS3_WAIT_TIMEOUT", "S1 load did not reach PS=3 before the fixed deadline",
                boundary=boundary,
            )
        try:
            raw = read_memory(PROGRAM_STATE_ADDRESS, 2)
        except OSError as exc:
            boundary.update({
                "status": "UNKNOWN", "classification": "PS3_WAIT_READ_FAILURE",
                "read_error": f"{type(exc).__name__}: {exc}",
            })
            raise S1EventBoundaryError(
                "PS3_WAIT_READ_FAILURE", "S1 PS=3 wait read failed", boundary=boundary,
            ) from exc
        if len(raw) != 2:
            boundary.update({
                "status": "UNKNOWN", "classification": "PS3_WAIT_READ_FAILURE",
                "read_error": f"program-state WORD read returned {len(raw)}/2 bytes",
            })
            raise S1EventBoundaryError(
                "PS3_WAIT_READ_FAILURE", "S1 PS=3 wait read was partial", boundary=boundary,
            )
        ps = int.from_bytes(raw, "little", signed=False)
        boundary["wait_ps"].append(ps)
        if ps == LOAD_COMPLETE_PS:
            boundary.update({"status": "PS3_REACHED", "post_ps": ps})
            break
        remaining = deadline - monotonic()
        if remaining <= 0:
            boundary.update({"status": "UNKNOWN", "classification": "PS3_WAIT_TIMEOUT"})
            raise S1EventBoundaryError(
                "PS3_WAIT_TIMEOUT", "S1 load did not reach PS=3 before the fixed deadline",
                boundary=boundary,
            )
        sleep(min(0.25, remaining))

    post_started = monotonic()
    post_deadline = (
        min(post_started + post_timeout, event_deadline)
        if post_timeout is not None and event_deadline is not None
        else post_started + post_timeout if post_timeout is not None else event_deadline
    )
    if post_deadline is not None and post_started >= post_deadline:
        boundary.update({"status": "UNKNOWN", "classification": "POST_SNAPSHOT_TIMEOUT"})
        raise S1EventBoundaryError(
            "POST_SNAPSHOT_TIMEOUT", "S1 post snapshot stage deadline expired",
            boundary=boundary,
        )
    try:
        post = read_s1_snapshot(read_memory, phase="post", player_reader=player_reader)
    except S1ReadError as exc:
        boundary.update({
            "status": "UNKNOWN", "classification": "POST_SNAPSHOT_READ_FAILURE",
            "post_read_error": str(exc),
        })
        raise S1EventBoundaryError(
            "POST_SNAPSHOT_READ_FAILURE", "S1 post snapshot read failed", boundary=boundary,
        ) from exc
    post_finished = monotonic()
    boundary.update({
        "post_started": post_started,
        "post_finished": post_finished,
        "post_elapsed_seconds": round(post_finished - post_started, 6),
    })
    if post_deadline is not None and post_finished > post_deadline:
        boundary.update({"status": "UNKNOWN", "classification": "POST_SNAPSHOT_TIMEOUT"})
        raise S1EventBoundaryError(
            "POST_SNAPSHOT_TIMEOUT", "S1 post snapshot exceeded its fixed deadline",
            boundary=boundary,
        )
    boundary["status"] = "COMPLETE"
    observation = collected_load_observation(pre, post)
    observation["event_boundary"] = boundary
    return observation


def _read_fixture(path: Path, spec: FixtureSpec) -> tuple[list[dict[str, Any]] | None, dict[str, Any]]:
    identity: dict[str, Any] = {
        "path": str(path),
        "expected_size": spec.expected_size,
        "expected_sha256": spec.expected_sha256,
    }
    if path.is_symlink() or not path.is_file():
        identity.update({"actual_size": None, "actual_sha256": None, "status": "UNKNOWN"})
        return None, identity
    try:
        actual_size = path.stat().st_size
        actual_sha = _sha256(path)
    except OSError as exc:
        identity.update({"actual_size": None, "actual_sha256": None, "status": "UNKNOWN", "error": str(exc)})
        return None, identity
    identity.update({"actual_size": actual_size, "actual_sha256": actual_sha})
    if actual_size != spec.expected_size or actual_sha != spec.expected_sha256:
        identity["status"] = "UNKNOWN"
        return None, identity
    try:
        with path.open("rb") as stream:
            records = []
            for owner in range(PLAYER_COUNT):
                offset = spec.player0_file_offset + owner * PLAYER_STRIDE
                stream.seek(offset)
                raw = stream.read(PLAYER_RECORD_SIZE)
                if len(raw) != PLAYER_RECORD_SIZE:
                    identity.update({"status": "UNKNOWN", "error": f"partial fixture read at owner {owner}"})
                    return None, identity
                records.append(_record(owner, raw, file_offset=offset))
    except OSError as exc:
        identity.update({"status": "UNKNOWN", "error": str(exc)})
        return None, identity
    identity["status"] = "PASS"
    return records, identity


def _validate_masks(records: Sequence[Mapping[str, Any]]) -> list[str]:
    failures: list[str] = []
    by_player: dict[int, Mapping[str, Any]] = {}
    for record in records:
        owner = record.get("owner")
        player_num = record.get("player_num")
        if not isinstance(owner, int) or not isinstance(player_num, int):
            failures.append("record owner/player_num is missing or not an integer")
            continue
        if player_num in by_player:
            failures.append(f"duplicate player_num {player_num}")
        by_player[player_num] = record
        if record.get("self_bit_mask") != (1 << player_num):
            failures.append(f"owner {owner} self_bit_mask does not equal 1<<player_num")
    if set(by_player) != set(range(PLAYER_COUNT)):
        failures.append("player_num set is not exactly 0..7")
    for record in records:
        player_num = record.get("player_num")
        team_num = record.get("team_num")
        if not isinstance(player_num, int) or not isinstance(team_num, int):
            continue
        expected = 0
        for other_num, other in by_player.items():
            if other_num != player_num and other.get("team_num") != team_num:
                expected |= 1 << other_num
        if record.get("opponent_mask") != expected:
            failures.append(f"player {player_num} opponent_mask does not match different-team players")
    return failures


def _base_evidence(spec: FixtureSpec, fixture_path: Path, group_word: int,
                   selected_index: int) -> dict[str, Any]:
    return {
        "status": "UNKNOWN",
        "classification": "NOT_EVALUATED",
        "scope": {
            "game_started": False,
            "wine_started": False,
            "xvfb_started": False,
            "memory_writes": False,
            "product_g1_pass": False,
        },
        "fixture": {
            "name": spec.name,
            "path": str(fixture_path),
            "group_word": group_word,
            "group_word_address": hex(GROUP_WORD_ADDRESS),
            "selected_index": selected_index,
            "selected_index_base": "1-based UI index; handler uses index-1",
            "expected_sha256": spec.expected_sha256,
            "player0_file_offset": spec.player0_file_offset,
            "player_stride": PLAYER_STRIDE,
            "player_record_size": PLAYER_RECORD_SIZE,
        },
        "addresses": {
            "player_base": hex(PLAYER_BASE),
            "player_stride": hex(PLAYER_STRIDE),
            "program_state_word": hex(PROGRAM_STATE_ADDRESS),
            "group_word": hex(GROUP_WORD_ADDRESS),
            "selected_index_word": hex(SELECTED_INDEX_ADDRESS),
        },
        "player_struct_fields": list(PLAYER_FIELDS),
        "fixture_players": [],
        "post_ps3_players": [],
        "load": {"post_ps": None, "open_succeeded": None},
    }


def evaluate(
    *, fixture_path: Path, fixture_name: str, group_word: int, selected_index: int,
    post: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate fixture identity and optional post-PS3 raw evidence."""

    spec = FIXTURES.get(fixture_name)
    if spec is None:
        spec = FixtureSpec(fixture_name, -1, "", -1, 0)
    evidence = _base_evidence(spec, fixture_path, group_word, selected_index)
    if group_word != 0:
        evidence.update({"classification": "INVALID_GROUP", "reason": "only group WORD 0 maps to save000/save006"})
        return evidence
    if selected_index not in (1, 7):
        evidence.update({"classification": "INVALID_SLOT", "reason": "S1 fixture mapping covers only 1-based slots 1 and 7"})
        return evidence
    if spec.selected_index != selected_index:
        evidence.update({"classification": "FIXTURE_SELECTION_MISMATCH", "reason": "selected index does not identify the supplied fixture"})
        return evidence
    records, identity = _read_fixture(fixture_path, spec)
    evidence["fixture_identity"] = identity
    if records is None:
        evidence.update({"classification": "FIXTURE_IDENTITY_MISMATCH", "reason": "fixture size/SHA or read shape did not match the expected immutable fixture"})
        return evidence
    evidence["fixture_players"] = records
    mask_failures = _validate_masks(records)
    if mask_failures:
        evidence.update({"status": "FAIL", "classification": "FIXTURE_PLAYER_FIELDS_MISMATCH", "failures": mask_failures})
        return evidence
    if post is None:
        evidence.update({"classification": "READER_MISSING", "reason": "post-PS3 load evidence was not supplied"})
        return evidence
    event_boundary = post.get("event_boundary")
    if isinstance(event_boundary, Mapping):
        evidence["event_boundary"] = dict(event_boundary)
    if post.get("collector_error") is not None:
        evidence.update({
            "classification": "READER_READ_FAILURE",
            "reason": "direct runtime reader failed before a complete S1 sample was captured",
            "reader_error": post["collector_error"],
        })
        return evidence
    load = post.get("load")
    load_map = load if isinstance(load, Mapping) else {}
    post_ps = post.get("ps")
    open_succeeded = load_map.get("open_succeeded")
    evidence["load"] = {"post_ps": post_ps, "open_succeeded": open_succeeded}
    if open_succeeded is False:
        evidence.update({"classification": "OPEN_FAILURE_PS3", "reason": "PS3 was observed after fopen/open failure; this is not load completion"})
        return evidence
    if open_succeeded is not True and post.get("_collector_token") is not _COLLECTOR_TOKEN:
        evidence.update({
            "classification": "UNTRUSTED_READER_EVIDENCE",
            "reason": "caller-supplied post PS/open/raw values have no direct runtime-reader provenance",
        })
        return evidence
    if post.get("_collector_token") is not _COLLECTOR_TOKEN:
        evidence.update({
            "classification": "UNTRUSTED_READER_EVIDENCE",
            "reason": "caller-supplied post PS/open/raw values have no direct runtime-reader provenance",
        })
        return evidence
    pre_sample = post.get("pre")
    post_sample = post.get("post")
    if not isinstance(pre_sample, Mapping) or not isinstance(post_sample, Mapping):
        evidence.update({"classification": "READER_MISSING", "reason": "collector pre/post samples are missing"})
        return evidence
    if (pre_sample.get("_collector_token") is not _COLLECTOR_TOKEN or
            post_sample.get("_collector_token") is not _COLLECTOR_TOKEN):
        evidence.update({"classification": "UNTRUSTED_READER_EVIDENCE", "reason": "collector pre/post token is missing"})
        return evidence
    if pre_sample.get("phase") != "pre" or post_sample.get("phase") != "post":
        evidence.update({"classification": "READER_MISSING", "reason": "collector phases are not pre/post"})
        return evidence
    if pre_sample.get("group_word") != group_word or post_sample.get("group_word") != group_word:
        evidence.update({"classification": "LIVE_INPUT_MISMATCH", "reason": "directly-read group WORD differs from requested group"})
        return evidence
    if pre_sample.get("selected_index") != selected_index or post_sample.get("selected_index") != selected_index:
        evidence.update({"classification": "LIVE_INPUT_MISMATCH", "reason": "directly-read selected index differs from requested slot"})
        return evidence
    pre_ps = pre_sample.get("ps")
    post_ps = post_sample.get("ps")
    evidence["load"] = {
        "pre_ps": pre_ps, "post_ps": post_ps, "open_succeeded": None,
        "open_status": "not_directly_observable",
    }
    evidence["reader"] = {
        "kind": post.get("collector"),
        "pre_read_points": pre_sample.get("read_points"),
        "post_read_points": post_sample.get("read_points"),
    }
    if pre_ps != 35:
        evidence.update({"classification": "PRE_LOAD_STATE_MISMATCH", "reason": "direct pre sample was not the documented PS=35 load-entry state"})
        return evidence
    if post_ps != LOAD_COMPLETE_PS:
        evidence.update({"classification": "PS3_NOT_REACHED", "reason": "direct post reader did not observe PS=3"})
        return evidence
    pre_records = pre_sample.get("players")
    post_records = post_sample.get("players")
    if not isinstance(pre_records, list) or len(pre_records) != PLAYER_COUNT:
        evidence.update({"classification": "PARTIAL_READ", "reason": "collector pre sample does not contain eight PlayerStruct records"})
        return evidence
    post_records = post_sample.get("players")
    if not isinstance(post_records, list) or len(post_records) != PLAYER_COUNT:
        evidence.update({"classification": "PARTIAL_READ", "reason": "post-PS3 evidence does not contain eight PlayerStruct records"})
        return evidence
    evidence["pre_ps3_players"] = pre_records
    evidence["post_ps3_players"] = post_records
    all_records = [*pre_records, *post_records]
    if any(
        not isinstance(item, Mapping) or not isinstance(item.get("raw_hex"), str)
        or not isinstance(item.get("memory_address"), str)
        for item in all_records
    ):
        evidence.update({"classification": "PARTIAL_READ", "reason": "post-PS3 PlayerStruct raw bytes are missing"})
        return evidence
    for sample_name, sample_records in (("pre", pre_records), ("post", post_records)):
        for owner, item in enumerate(sample_records):
            if item.get("owner") != owner or item.get("memory_address") != hex(PLAYER_BASE + owner * PLAYER_STRIDE):
                evidence.update({
                    "classification": "READ_PROVENANCE_MISMATCH",
                    "reason": f"{sample_name} PlayerStruct record {owner} has unexpected owner/address provenance",
                })
                return evidence
    expected = [item["raw_hex"] for item in records]
    before = [item["raw_hex"] for item in pre_records]
    observed = [item["raw_hex"] for item in post_records]
    if before == observed or pre_ps == post_ps:
        evidence.update({"classification": "PRE_POST_NO_CHANGE", "reason": "direct pre/post samples did not change"})
        return evidence
    if observed != expected:
        evidence.update({"status": "FAIL", "classification": "PLAYER_STRUCT_MISMATCH", "reason": "post-PS3 raw PlayerStruct bytes differ from the selected fixture"})
        return evidence
    evidence.update({
        "status": "PASS",
        "classification": "LOAD_RESTORED_PLAYER_STRUCTS",
        "reason": "direct pre/post runtime reads changed and post-PS3 raw bytes match all eight selected-fixture PlayerStruct records",
    })
    return evidence


def _parse_int(value: str) -> int:
    return int(value, 0)


def _write_new_json(path: Path, value: Mapping[str, Any]) -> None:
    _install_new_json_payload(path, prepare_json_payload(value))


def prepare_json_payload(value: Mapping[str, Any]) -> str:
    """Serialize an evidence payload without touching the output filesystem."""

    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _install_new_json_payload(path: Path, payload: str, *, deadline: float | None = None) -> None:
    """Install one fresh JSON file without overwriting or missing its deadline.

    The deadline is checked around every synchronous filesystem operation.  A
    filesystem call cannot be interrupted safely here, so a late hard-link is
    removed again when this invocation created it; an existing final path is
    never removed.
    """

    def check_deadline(phase: str) -> None:
        if deadline is not None and time.monotonic() > deadline:
            raise TimeoutError(f"JSON artifact deadline expired during {phase}")

    check_deadline("artifact preparation")
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"refusing to overwrite existing evidence: {path}")
    if not path.parent.is_dir():
        raise NotADirectoryError(f"output parent is not a directory: {path.parent}")
    temporary = path.with_name(f".{path.name}.tmp")
    if temporary.exists() or temporary.is_symlink():
        raise FileExistsError(f"refusing to overwrite temporary evidence: {temporary}")
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    installed = False
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        check_deadline("payload write and fsync")
        # A hard-link install is atomic and fails if another writer created the
        # final artifact.  os.replace() would silently overwrite that artifact.
        os.link(temporary, path)
        installed = True
        try:
            check_deadline("atomic artifact install")
        except Exception:
            # This path can only be ours: the final path was checked before the
            # exclusive temporary file and the non-overwriting link succeeded.
            path.unlink()
            installed = False
            raise
    except Exception:
        if descriptor != -1:
            os.close(descriptor)
        if installed:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        raise
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only S1 load-evidence fixture evaluator")
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--fixture-name", default=None)
    parser.add_argument("--group-word", type=_parse_int, required=True)
    parser.add_argument("--selected-index", type=_parse_int, required=True)
    parser.add_argument("--post-json", type=Path)
    parser.add_argument("--output", type=Path, default=Path("s1_load_evidence.json"))
    args = parser.parse_args(argv)
    fixture_name = args.fixture_name or args.fixture.name
    post: Mapping[str, Any] | None = None
    if args.post_json is not None:
        try:
            loaded = json.loads(args.post_json.read_text(encoding="utf-8"))
            if not isinstance(loaded, Mapping):
                raise ValueError("post JSON root must be an object")
            post = loaded
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"ok": False, "error": f"post JSON unreadable: {exc}"}, ensure_ascii=False))
            return 2
    try:
        result = evaluate(
            fixture_path=args.fixture, fixture_name=fixture_name,
            group_word=args.group_word, selected_index=args.selected_index, post=post,
        )
        _write_new_json(args.output, result)
    except (OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
