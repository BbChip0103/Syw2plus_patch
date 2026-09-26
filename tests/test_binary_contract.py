"""Read-only regression tests for the pinned event-ring binary contract."""

from __future__ import annotations

import hashlib
from pathlib import Path
import shutil

import pytest

from tools.check_binary_contract import (
    CALL_BLOCK,
    ORIGINAL_SHA256,
    RETURN_BLOCK,
    BinaryContractError,
    guard_dispatch,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "Syw2plus/syw2plus_original.exe"


def test_pinned_original_contract_and_branch_targets():
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")

    report = validate(ORIGINAL)

    assert report["sha256"] == ORIGINAL_SHA256
    assert report["guard_range"] == ["0x4ac47f", "0x4ac4df"]
    assert report["branch_targets"] == {
        "0x4ac48e": CALL_BLOCK,
        "0x4ac493": CALL_BLOCK,
        "0x4ac498": CALL_BLOCK,
        "0x4ac4ad": RETURN_BLOCK,
        "0x4ac4c2": RETURN_BLOCK,
    }
    assert report["dequeue_callers"] == ["0x4233ae"]


def test_generic_ring_producer_boundary_and_word_order():
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")

    report = validate(ORIGINAL)

    assert report["producer_callers"] == ["0x41ec9a"]
    assert report["producer_direct_callees"] == ["0x415880"]
    assert report["producer_to_enqueue_direct"] is False
    assert report["enqueue_callers_count"] == 134
    assert report["enqueue_record_writer"] == "0x4ac415->0x4aa820"
    assert report["record_word_store_order"] == [
        "arg1 -> [ecx+0x0]",
        "arg2 -> [ecx+0x2]",
        "arg3 -> [ecx+0x4]",
    ]


def test_code_04_dispatch_reachability_and_stack_provenance():
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")

    report = validate(ORIGINAL)

    assert report["dispatch_range"] == ["0x41ec3d", "0x41ed0b"]
    assert report["dispatch_branch_targets"] == {
        "0x41ec41": 0x0041ED23,
        "0x41ec4e": 0x0041EC5D,
        "0x41ec57": 0x0041EE9B,
        "0x41ec88": 0x0041ED14,
        "0x41eca2": 0x0041ED14,
        "0x41eca6": 0x0041ED14,
        "0x41ecca": 0x0041ED14,
    }
    assert report["dispatch_calls"] == {
        "0x41ec7d": "0x416fd0",
        "0x41ec9a": "0x40fb50",
        "0x41ecae": "0x40f5a0",
        "0x41ecd2": "0x40f5e0",
        "0x41ecde": "0x40f5c0",
        "0x41ecea": "0x40f5a0",
        "0x41ed07": "0x4ac3e0",
    }
    assert report["dispatch_enqueue_callsite"] == "0x41ed07"
    assert report["dispatch_argument_provenance"] == {
        "arg1_[esp+0x4]": (
            "WORD [0x009B529A + 4 * (109 * sign_extend(WORD return "
            "of 0x0040F5A0(ESI) at 0x0041ECEA))]"
        ),
        "arg2_[esp+0x8]": "WORD return of 0x0040F5C0(ESI) at 0x0041ECDE",
        "arg3_[esp+0xc]": "WORD return of 0x0040F5E0(ESI) at 0x0041ECD2",
    }
    assert "0x0040FB50 returns 1" in report["dispatch_enqueue_reachability"]
    assert "EBP==0" in report["dispatch_enqueue_reachability"]


def test_code_04_upstream_inputs_are_pinned_without_semantic_promotion():
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")

    report = validate(ORIGINAL)

    assert report["dispatch_upstream"] == {
        "upstream_branch_targets": {
            "0x41e624": 0x0041E63D,
            "0x41e644": 0x0041E653,
            "0x41e64c": 0x0041E653,
            "0x41e6fc": 0x0041E715,
            "0x41e705": 0x0041E76E,
            "0x41e77b": 0x0041EB7F,
            "0x41eb8b": 0x0041EBF4,
            "0x41eb9c": 0x0041EBF6,
            "0x41eba5": 0x0041EBF6,
            "0x41ebad": 0x0041EBF6,
        },
        "updater_callsite": "0x0041E635->0x00437E90 (unique direct caller)",
        "mask_to_mapper_read": "0x0041CEFC: DWORD [0x009E1DCC]",
        "mapper_to_state_load": "0x0041CEE0 writes 0x00892FFE; consumed at 0x0041EBF6",
        "data_writer_xrefs": {
            "0x9e1dcc": [
                "0x41e392", "0x437ea5", "0x437f92", "0x438106", "0x438179",
                "0x4382ed", "0x438315", "0x43836a", "0x43847b", "0x438498",
            ],
            "0x892ffe": [
                "0x412ee7", "0x41cf16", "0x41cf39", "0x41cf5f", "0x41cf85",
                "0x41cfab", "0x41cfd1", "0x41cff7", "0x41ea14", "0x41ebc0",
                "0x41f0ac", "0x4997d6", "0x499a61", "0x499b0a", "0x499c22",
                "0x499cf2", "0x499d82", "0x499e75",
            ],
        },
        "cx_dominating_load": "0x0041EBF6: WORD [0x00892FFE]",
        "esi_loop_load": "0x0041EC71: WORD [0x00899028 + 4 * EDX]",
        "esi_loop_index_source": "0x0041EC61: DWORD [0x008924C8] + EDI, unsigned remainder / 0x14",
        "state_mapping_helper": "0x41cee0",
        "state_mapping_callers": ["0x41dcfa", "0x41e64e", "0x41e6fe"],
        "input_state_updater": "0x437e90",
        "input_state_updater_callers": ["0x41e635"],
        "active_record_table": "0x00899028, 20 slots * 4 bytes",
        "active_record_writers": ["0x00412E61 add", "0x00412EBC clear"],
        "active_record_helper_callers": [
            "0x407192",
            "0x409c8e",
            "0x409fb9",
            "0x40f7f1",
            "0x412a1e",
            "0x4170b5",
            "0x44302d",
            "0x476edc",
            "0x47b5b9",
            "0x48e209",
            "0x48e7e0",
        ],
        "direct_input_to_active_record_writer": False,
        "direct_state_mapper_to_enqueue": False,
    }


def test_coordinate_input_provenance_reaches_existing_updater_without_g1_promotion():
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")

    report = validate(ORIGINAL)

    assert report["input_message_provenance"] == {
        "wndproc_registration": "0x00423C34 -> 0x00423DC0; RegisterClassA at 0x00423C8B",
        "message_dispatch": "DispatchMessageA IAT call at 0x004232FC",
        "mouse_coordinates": "WM_MOUSEMOVE handler 0x0042434B stores lParam low/high at 0x00C0CB58/0x00C0CB5C",
        "event_ring": "0x0042436F -> 0x004216B0; game tick 0x0041E299 -> 0x004217B0",
        "coordinate_words": "0x0041E4AF/0x0041E4B6 write 0x00637734/0x00637736",
        "updater_arguments": "0x0041E626/0x0041E62C load 0x00637736/0x00637734; 0x0041E635 -> 0x00437E90",
        "direct_calls": {
            "0x42436f": "0x4216b0",
            "0x423fe8": "0x41c740",
            "0x41c81e": "0x41e220",
            "0x41e299": "0x4217b0",
            "0x41e464": "0x4516a0",
            "0x41e635": "0x437e90",
        },
        "semantic_status": "OS input origin statically connected; gameplay meaning, output resolution, and runtime behavior remain unverified",
    }


def test_code_04_dispatch_contract_rejects_drift_without_mutating_original(tmp_path: Path):
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")

    candidate = tmp_path / ORIGINAL.name
    shutil.copy2(ORIGINAL, candidate)
    data = bytearray(candidate.read_bytes())
    data[0x0041ED07 - 0x00400000] ^= 0x01
    candidate.write_bytes(data)

    with pytest.raises(BinaryContractError, match="unexpected executable SHA-256"):
        validate(candidate)
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == ORIGINAL_SHA256


def test_contract_rejects_one_byte_drift_without_mutating_original(tmp_path: Path):
    if not ORIGINAL.is_file():
        pytest.skip("local original executable is unavailable")

    candidate = tmp_path / ORIGINAL.name
    shutil.copy2(ORIGINAL, candidate)
    data = bytearray(candidate.read_bytes())
    data[0x4AC48E - 0x400000] ^= 0x01
    candidate.write_bytes(data)

    with pytest.raises(BinaryContractError, match="unexpected executable SHA-256"):
        validate(candidate)
    assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest() == ORIGINAL_SHA256


@pytest.mark.parametrize(
    ("case", "expected"),
    [
        ({"count_positive": False, "mode": 3, "first_field_nonzero": True, "second_field_nonzero": True, "first_distance": 0, "second_distance": 0}, "skip"),
        ({"count_positive": True, "mode": 2, "first_field_nonzero": False, "second_field_nonzero": False, "first_distance": 99, "second_distance": 99}, "call"),
        ({"count_positive": True, "mode": 3, "first_field_nonzero": False, "second_field_nonzero": True, "first_distance": 99, "second_distance": 99}, "call"),
        ({"count_positive": True, "mode": 3, "first_field_nonzero": True, "second_field_nonzero": True, "first_distance": 0x12, "second_distance": 0}, "skip"),
        ({"count_positive": True, "mode": 3, "first_field_nonzero": True, "second_field_nonzero": True, "first_distance": 0, "second_distance": 0x12}, "skip"),
        ({"count_positive": True, "mode": 3, "first_field_nonzero": True, "second_field_nonzero": True, "first_distance": 0x11, "second_distance": 0x11}, "call"),
    ],
)
def test_guard_truth_table(case: dict[str, object], expected: str):
    assert guard_dispatch(**case) == expected
