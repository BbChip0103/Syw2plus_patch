"""Targeted checks for the read-only FUN_004AE550 xref inventory.

These pin down the static evidence used to escalate lap676: none of the 22
direct-call sites to FUN_004AE550 push a known unit-order opcode (move=3,
attack=4), and none of the known order-issuing functions call it directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.g5_command_packer_xrefs import ORIGINAL_SHA256, PACKER_ADDRESS, inventory


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_CANDIDATES = (
    ROOT.parent / "syw2plus_original.exe",
    ROOT.parent / "Syw2plus_re" / "Syw2plus" / "syw2plus_original.exe",
    ROOT / "Syw2plus" / "syw2plus_original.exe",
)


def _original() -> Path:
    for candidate in ORIGINAL_CANDIDATES:
        if candidate.is_file():
            return candidate
    pytest.skip("local original executable is unavailable")


def test_inventory_is_sha_pinned():
    report = inventory(_original())
    assert report["status"] == "PASS"
    assert report["source"]["sha256"] == ORIGINAL_SHA256
    assert report["packer_address"] == f"0x{PACKER_ADDRESS:08x}"


def test_call_site_count_and_no_order_opcode_present():
    report = inventory(_original())
    assert report["call_site_count"] == 22
    assert len(report["call_sites"]) == 22

    order_opcodes = {"0x00000003", "0x00000004"}
    for site in report["call_sites"]:
        pushed_values = {
            p["value"] for p in site["preceding_pushes_newest_first"] if p["kind"] == "imm"
        }
        assert not (pushed_values & order_opcodes), (
            f"call site {site['call_address']} pushes a move/attack opcode; "
            "this would support the selection-broadcast hypothesis"
        )


def test_known_order_functions_do_not_call_the_packer_directly():
    report = inventory(_original())
    hits = report["known_order_function_direct_calls"]
    assert set(hits) == {
        "op8_issuer_FUN_00415480",
        "op8_issuer_alt_FUN_00415880",
        "group_assign_FUN_00445D30",
        "order_consumer_FUN_0040F7D0",
    }
    for name, calls in hits.items():
        assert calls == [], f"{name} unexpectedly calls the packer directly: {calls}"
