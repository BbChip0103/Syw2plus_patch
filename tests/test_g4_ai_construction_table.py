"""Regression contract for the AI building-construction prerequisite table
decode (``tools/g4_ai_construction_table.py``), which extends
``analysis/memory_maps/ai_build_faction_gate_0043dbb0_lap515_20260923.md``
(lap515) with the ``FUN_00422EB0`` record layout that document's
``FUN_0043DB00`` prerequisite reads left undecoded.
"""

from __future__ import annotations

import struct
import subprocess
import sys
from types import SimpleNamespace
from pathlib import Path

import pytest

from tools import g4_ai_construction_table as ct
from tools import runtime_env


def test_decodes_the_real_table() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    records = ct.load_construction_table(executable)
    assert len(records) == 39
    assert all(r["building_type"] != 0 for r in records)
    # Most records' nation_kind is one of the four faction-detection kinds
    # FUN_0043DBB0's jump table recognizes (see the histogram probe module).
    # One outlier (building_type 23, index 13) decodes to nation_kind=49 --
    # not one of the four; left unexplained here (not needed for the G4
    # owner0/owner1 HQ/production-building hypothesis this lap tests).
    known = {7, 21, 70, 75}
    unexplained = {r["nation_kind"] for r in records} - known
    assert unexplained == {49}, unexplained


def test_hq_records_match_this_laps_fresh_disassembly() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    records = ct.load_construction_table(executable)
    hq58 = ct.record_for_building_type(records, 58)
    assert hq58 == {
        "index": 25, "building_type": 58, "prereq_building_type": 0,
        "nation_kind": 75, "prereq_own_kind": 0, "cost": 20,
    }
    type60 = ct.record_for_building_type(records, 60)
    assert type60 == {
        "index": 27, "building_type": 60, "prereq_building_type": 58,
        "nation_kind": 75, "prereq_own_kind": 0, "cost": 30,
    }


def test_record_for_building_type_returns_none_when_absent() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    records = ct.load_construction_table(executable)
    assert ct.record_for_building_type(records, 999) is None


def test_nation_kind_to_flag_off_matches_lap515_faction_flags() -> None:
    assert ct.NATION_KIND_TO_FLAG_OFF == {7: 0x314C, 21: 0x3154, 70: 0x3158, 75: 0x3150}


def _make_record(building_type: int, prereq_building_type: int, nation_kind: int,
                  prereq_own_kind: int, cost: int) -> bytes:
    return struct.pack("<iiiii", building_type, prereq_building_type, nation_kind, prereq_own_kind, cost)


def test_decode_record_reads_every_field_in_declared_order() -> None:
    blob = _make_record(60, 58, 75, 0, 30)
    record = ct._decode_record(blob, 0, index=0)
    assert record == {
        "index": 0, "building_type": 60, "prereq_building_type": 58,
        "nation_kind": 75, "prereq_own_kind": 0, "cost": 30,
    }


def test_decode_record_returns_none_at_zero_terminator() -> None:
    blob = _make_record(0, 0, 0, 0, 0)
    assert ct._decode_record(blob, 0, index=0) is None


def _pe(*sections, image_base=0x12340000):
    return SimpleNamespace(
        sections=list(sections), OPTIONAL_HEADER=SimpleNamespace(ImageBase=image_base)
    )


def _section(virtual_address, raw_size, raw_offset, virtual_size=None):
    return SimpleNamespace(
        VirtualAddress=virtual_address,
        SizeOfRawData=raw_size,
        PointerToRawData=raw_offset,
        Misc=SimpleNamespace(VirtualSize=raw_size if virtual_size is None else virtual_size),
    )


def test_va_translation_uses_fixed_image_base_and_first_raw_section_match() -> None:
    first = _section(0x1000, 0x20, 0x300)
    overlapping = _section(0x1000, 0x20, 0x900)
    assert ct._va_to_file_offset(_pe(first, overlapping), 0x00401000) == 0x300
    assert ct._va_to_file_offset(_pe(first, overlapping), 0x0040101F) == 0x31F


def test_va_translation_uses_raw_end_exclusive_and_rejects_virtual_tail() -> None:
    section = _section(0x2000, 0x10, 0x400, virtual_size=0x80)
    assert ct._va_to_file_offset(_pe(section), 0x0040200F) == 0x40F
    with pytest.raises(ValueError, match=r"^VA 0x00402010 is not in a raw section$"):
        ct._va_to_file_offset(_pe(section), 0x00402010)
    with pytest.raises(ValueError, match=r"^VA 0x00402080 is not in a raw section$"):
        ct._va_to_file_offset(_pe(section), 0x00402080)


def test_cli_help_does_not_import_pefile_in_direct_or_module_entry() -> None:
    script = Path(ct.__file__).resolve()
    for command in ([sys.executable, "-S", str(script), "--help"],
                    [sys.executable, "-S", "-m", "tools.g4_ai_construction_table", "--help"]):
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        assert result.returncode == 0, result.stderr
        assert "--source" in result.stdout
        assert "pefile" not in result.stderr
