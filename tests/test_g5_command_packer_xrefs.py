"""Targeted checks for the read-only FUN_004AE550 xref inventory.

These pin down the static evidence used to escalate lap676: none of the 22
direct-call sites to FUN_004AE550 push a known unit-order opcode (move=3,
attack=4), and none of the known order-issuing functions call it directly.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools import g5_command_packer_xrefs as xrefs
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


class _FakePE:
    def __init__(self, text: bytes, image_base: int = xrefs.IMAGE_BASE):
        self.OPTIONAL_HEADER = type("OptionalHeader", (), {"ImageBase": image_base})()
        self.sections = [type("Section", (), {
            "Name": b".text\0\0\0",
            "VirtualAddress": 0,
            "PointerToRawData": 0x200,
            "SizeOfRawData": len(text),
        })()]
        self.__data__ = bytes(0x200) + text
        self.closed = False

    def close(self) -> None:
        self.closed = True


def _call(address: int, target: int = PACKER_ADDRESS) -> bytes:
    return b"\xe8" + (target - (address + 5)).to_bytes(4, "little", signed=True)


def _install_fake_pe(monkeypatch, tmp_path, text: bytes, image_base=xrefs.IMAGE_BASE):
    executable = tmp_path / "synthetic.exe"
    executable.write_bytes(b"synthetic")
    pe = _FakePE(text, image_base)
    calls = []

    def open_pe(path, *, fast_load):
        calls.append((path, fast_load))
        return pe

    monkeypatch.setattr(xrefs, "_sha256", lambda _path: ORIGINAL_SHA256)
    monkeypatch.setattr(xrefs.pefile, "PE", open_pe)
    return executable, pe, calls


def test_synthetic_report_decodes_calls_pushes_and_scan_terminators(monkeypatch, tmp_path):
    text = bytearray()
    text.extend(b"".join(b"\x6a" + bytes([value]) for value in range(1, 7)))
    text.extend(b"\x50")  # push eax: newest push instruction
    text.extend(_call(xrefs.IMAGE_BASE + len(text)))
    text.extend(b"\xff\xd0")  # register-indirect call is not an immediate xref
    text.extend(b"\x6a\x07\xc3\x6a\x08")
    text.extend(_call(xrefs.IMAGE_BASE + len(text)))
    text.extend(b"\x6a\x09\xeb\x00\x6a\x0a")
    text.extend(_call(xrefs.IMAGE_BASE + len(text)))
    text.extend(b"\x6a\x0b\xff\xd0\x6a\x0c")
    text.extend(_call(xrefs.IMAGE_BASE + len(text)))
    executable, pe, opened = _install_fake_pe(monkeypatch, tmp_path, bytes(text))

    report = inventory(executable)

    assert report == {
        "status": "PASS",
        "coverage": "text_section_direct_calls_only",
        "source": {
            "path": str(executable.resolve()),
            "sha256": ORIGINAL_SHA256,
            "text_start": "0x00400000",
            "text_bytes": len(text),
            "decoded_instructions": 21,
        },
        "packer_address": "0x004ae550",
        "call_site_count": 4,
        "call_sites": [
            {
                "call_address": "0x0040000d",
                "preceding_pushes_newest_first": [
                    {"address": "0x0040000c", "kind": "reg", "value": "eax"},
                    {"address": "0x0040000a", "kind": "imm", "value": "0x00000006"},
                    {"address": "0x00400008", "kind": "imm", "value": "0x00000005"},
                    {"address": "0x00400006", "kind": "imm", "value": "0x00000004"},
                    {"address": "0x00400004", "kind": "imm", "value": "0x00000003"},
                ],
                "push_count_found": 5,
            },
            {
                "call_address": "0x00400019",
                "preceding_pushes_newest_first": [
                    {"address": "0x00400017", "kind": "imm", "value": "0x00000008"},
                ],
                "push_count_found": 1,
            },
            {
                "call_address": "0x00400024",
                "preceding_pushes_newest_first": [
                    {"address": "0x00400022", "kind": "imm", "value": "0x0000000a"},
                ],
                "push_count_found": 1,
            },
            {
                "call_address": "0x0040002f",
                "preceding_pushes_newest_first": [
                    {"address": "0x0040002d", "kind": "imm", "value": "0x0000000c"},
                ],
                "push_count_found": 1,
            },
        ],
        "known_order_function_direct_calls": {
            "op8_issuer_FUN_00415480": [],
            "op8_issuer_alt_FUN_00415880": [],
            "group_assign_FUN_00445D30": [],
            "order_consumer_FUN_0040F7D0": [],
        },
        "evidence_policy": {
            "raw_pattern_scan": False,
            "accepted_xref_evidence": "decoded call-immediate operand only",
            "indirect_or_register_calls": "not scanned; stated gap, not proven absent",
        },
    }
    assert opened == [(str(executable.resolve()), True)]
    assert pe.closed


@pytest.mark.parametrize(
    ("call_offset", "expected_hits"),
    [(0, ["0x0040f7d0"]), (0x1FFF, ["0x004117cf"]), (0x2000, [])],
)
def test_known_function_windows_are_half_open(
    monkeypatch, tmp_path, call_offset, expected_hits
):
    function_start = xrefs.KNOWN_ORDER_FUNCTIONS["order_consumer_FUN_0040F7D0"]
    text_start = function_start
    text = bytearray(b"\x90" * (call_offset + 5))
    text[call_offset:call_offset + 5] = _call(text_start + call_offset)
    executable, pe, _ = _install_fake_pe(
        monkeypatch, tmp_path, bytes(text), xrefs.IMAGE_BASE
    )
    pe.sections[0].VirtualAddress = text_start - xrefs.IMAGE_BASE

    report = inventory(executable)

    assert report["known_order_function_direct_calls"]["order_consumer_FUN_0040F7D0"] == expected_hits
    assert pe.closed


def test_sha_rejection_happens_before_opening_pe(monkeypatch, tmp_path):
    executable = tmp_path / "wrong.exe"
    executable.write_bytes(b"wrong build")
    opened = []
    monkeypatch.setattr(xrefs, "_sha256", lambda _path: "0" * 64)
    monkeypatch.setattr(xrefs.pefile, "PE", lambda *args, **kwargs: opened.append(args))

    with pytest.raises(ValueError, match="original SHA-256 mismatch"):
        inventory(executable)

    assert opened == []


def test_pe_is_closed_when_validation_fails(monkeypatch, tmp_path):
    executable, pe, _ = _install_fake_pe(
        monkeypatch, tmp_path, b"\x90", image_base=xrefs.IMAGE_BASE + 1
    )

    with pytest.raises(ValueError, match="unexpected image base"):
        inventory(executable)

    assert pe.closed


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
