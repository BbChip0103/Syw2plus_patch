#!/usr/bin/env python3
"""Independent contract review for the lap353 S1 load-evidence reader.

The probe does not start Wine or the game.  It checks the production wiring
and demonstrates whether a caller-supplied post payload can be promoted to a
load-restored PASS without any live reader provenance.
"""

from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path

from tools import runtime_env
from tools import s1_load_evidence as s1


REPO = Path(__file__).resolve().parents[4]
FIXTURE = REPO / "local/runtime/20260912_191422_3558862_0/game/save/save000.dat"
EXPECTED_FIXTURE_SHA = "1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_raw_records(path: Path) -> list[dict[str, str]]:
    data = path.read_bytes()
    return [
        {
            "raw_hex": data[
                s1.FIXTURES[path.name].player0_file_offset + owner * s1.PLAYER_STRIDE:
                s1.FIXTURES[path.name].player0_file_offset + owner * s1.PLAYER_STRIDE
                + s1.PLAYER_RECORD_SIZE
            ].hex(" ")
        }
        for owner in range(s1.PLAYER_COUNT)
    ]


def main() -> int:
    failures: list[str] = []
    fixture_sha = sha256(FIXTURE)
    if fixture_sha != EXPECTED_FIXTURE_SHA:
        failures.append("F0: protected fixture SHA differs from the reviewed pin")

    wrapper_source = inspect.getsource(runtime_env.g1_s1_load_evidence)
    module_source = inspect.getsource(s1)
    production_source = "\n".join((wrapper_source, module_source.split("def main(", 1)[1]))
    collector_wired = "read_post_player_structs(" in production_source
    group_reader_wired = "GROUP_WORD_ADDRESS" in production_source
    ps_reader_wired = "PROGRAM_STATE_ADDRESS" in production_source
    if not collector_wired:
        failures.append("F1: the production CLI/evaluator never calls read_post_player_structs")
    if not group_reader_wired:
        failures.append("F2: the production CLI/evaluator accepts group_word instead of reading its address")
    if not ps_reader_wired:
        failures.append("F3: the production CLI/evaluator accepts ps instead of reading its address")

    copied_fixture_payload = {
        "ps": 3,
        "load": {"open_succeeded": True},
        "players": fixture_raw_records(FIXTURE),
    }
    result = s1.evaluate(
        fixture_path=FIXTURE,
        fixture_name=FIXTURE.name,
        group_word=0,
        selected_index=1,
        post=copied_fixture_payload,
    )
    ungrounded_payload_rejected = result.get("status") != "PASS"
    if not ungrounded_payload_rejected:
        failures.append(
            "F4: caller-supplied ps/open/raw strings receive LOAD_RESTORED_PLAYER_STRUCTS PASS "
            "without live reader provenance or a pre/post change"
        )

    report = {
        "scope": "lap353 S1 reader/CLI contract; offline independent review",
        "fixture": str(FIXTURE),
        "fixture_sha256": fixture_sha,
        "checks": {
            "collector_wired": collector_wired,
            "group_reader_wired": group_reader_wired,
            "program_state_reader_wired": ps_reader_wired,
            "ungrounded_payload_rejected": ungrounded_payload_rejected,
            "ungrounded_payload_result": {
                "status": result.get("status"),
                "classification": result.get("classification"),
            },
        },
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
