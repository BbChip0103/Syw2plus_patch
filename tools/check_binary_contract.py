"""Read-only static contract for the original event-ring dequeue branch."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import struct
from typing import Literal


@dataclass(frozen=True)
class Branch:
    address: int
    opcode: bytes
    target: int


IMAGE_BASE = 0x00400000
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
DEQUEUE_ADDRESS = 0x004AC420
PRODUCER_ADDRESS = 0x0040FB50
PRODUCER_TARGET = 0x00415880
ENQUEUE_ADDRESS = 0x004AC3E0
ENQUEUE_TARGET = 0x004AA820
DISPATCH_START = 0x0041EC3D
DISPATCH_END = 0x0041ED0C
DISPATCH_ENQUEUE_CALLSITE = 0x0041ED07
GUARD_START = 0x004AC47F
GUARD_END = 0x004AC4DF
CALL_BLOCK = 0x004AC4C4
RETURN_BLOCK = 0x004AC4DF
CALL_TARGET = 0x004AA8D0

PRODUCER_BYTES = bytes.fromhex(
    "0f bf 4c 24 04 8b 44 24 08 50 8d 04 49 c1 e0 04 "
    "2b c1 8d 0c 80 8d 0c cd 90 b7 66 00 e8 0f 5d 00 00 "
    "c2 08 00"
)
ENQUEUE_BYTES = bytes.fromhex(
    "66 8b 15 fe aa 05 01 66 83 fa 05 7c 03 33 c0 c3 "
    "0f bf c2 66 42 8d 04 40 66 89 15 fe aa 05 01 8b "
    "54 24 0c 8d 0c 45 e0 aa 05 01 8b 44 24 08 52 8b "
    "54 24 08 50 52 e8 06 e4 ff ff b8 01 00 00 00 c3"
)
RECORD_WRITER_BYTES = bytes.fromhex(
    "66 8b 44 24 04 66 8b 54 24 08 66 89 01 66 8b 44 24 0c "
    "66 89 51 02 66 89 41 04 c2 0c 00"
)

DISPATCH_BYTES = bytes.fromhex(
    """
    66 83 f9 04 0f 85 dc 00 00 00 66 39 3d b4 8f 89 00 75 0d
    66 39 3d b6 8f 89 00 0f 84 3e 02 00 00 33 ed 33 ff a1 c8 24
    89 00 33 d2 03 c7 b9 14 00 00 00 f7 f1 66 8b 34 95 28 90 89
    00 0f bf d6 52 e8 4e 83 ff ff 83 c4 04 83 f8 01 0f 85 86 00
    00 00 a1 b4 8f 89 00 b9 6c e3 61 00 50 56 e8 b1 0e ff ff 83
    f8 01 75 70 85 ed 75 6c 56 b9 6c e3 61 00 e8 ed 08 ff ff 0f
    bf c0 8d 0c c0 8d 0c 48 8d 14 49 8d 04 90 66 39 2c 85 9a 52
    9b 00 74 48 56 b9 6c e3 61 00 e8 09 09 ff ff 50 56 b9 6c e3
    61 00 e8 dd 08 ff ff 50 56 b9 6c e3 61 00 e8 b1 08 ff ff 0f
    bf c0 8d 0c c0 8d 0c 48 8d 14 49 8d 04 90 66 8b 0c 85 9a 52
    9b 00 51 e8 d4 d6 08 00
    """
)

DISPATCH_BRANCHES = (
    Branch(0x0041EC41, bytes.fromhex("0f 85 dc 00 00 00"), 0x0041ED23),
    Branch(0x0041EC4E, bytes.fromhex("75 0d"), 0x0041EC5D),
    Branch(0x0041EC57, bytes.fromhex("0f 84 3e 02 00 00"), 0x0041EE9B),
    Branch(0x0041EC88, bytes.fromhex("0f 85 86 00 00 00"), 0x0041ED14),
    Branch(0x0041ECA2, bytes.fromhex("75 70"), 0x0041ED14),
    Branch(0x0041ECA6, bytes.fromhex("75 6c"), 0x0041ED14),
    Branch(0x0041ECCA, bytes.fromhex("74 48"), 0x0041ED14),
)

DISPATCH_CALLS = (
    (0x0041EC7D, 0x00416FD0),
    (0x0041EC9A, PRODUCER_ADDRESS),
    (0x0041ECAE, 0x0040F5A0),
    (0x0041ECD2, 0x0040F5E0),
    (0x0041ECDE, 0x0040F5C0),
    (0x0041ECEA, 0x0040F5A0),
    (DISPATCH_ENQUEUE_CALLSITE, ENQUEUE_ADDRESS),
)

DISPATCH_HELPER_BYTES = {
    0x0040F5A0: bytes.fromhex(
        "0f bf 4c 24 04 8d 04 49 c1 e0 04 2b c1 8d 04 80 "
        "66 0f b6 04 c5 1d b8 66 00 c2 04 00"
    ),
    0x0040F5C0: bytes.fromhex(
        "0f bf 4c 24 04 8d 04 49 c1 e0 04 2b c1 8d 04 80 "
        "66 8b 04 c5 32 ba 66 00 c2 04 00"
    ),
    0x0040F5E0: bytes.fromhex(
        "0f bf 4c 24 04 8d 04 49 c1 e0 04 2b c1 8d 04 80 "
        "66 8b 04 c5 34 ba 66 00 c2 04 00"
    ),
}

DISPATCH_ARGUMENT_PROVENANCE = {
    "arg1_[esp+0x4]": (
        "WORD [0x009B529A + 4 * (109 * sign_extend(WORD return "
        "of 0x0040F5A0(ESI) at 0x0041ECEA))]"
    ),
    "arg2_[esp+0x8]": "WORD return of 0x0040F5C0(ESI) at 0x0041ECDE",
    "arg3_[esp+0xc]": "WORD return of 0x0040F5E0(ESI) at 0x0041ECD2",
}

DISPATCH_REACHABILITY = (
    "0x0041ED07 is reachable only on the 0x0041EC3D code-0x04 path: "
    "CX==4, candidate helper 0x00416FD0 returns 1, "
    "0x0040FB50 returns 1, EBP==0, and the first 0x0040F5A0(ESI)-derived "
    "table WORD is nonzero; the three helpers then return normally via ret 0x4."
)

# Upstream provenance for the code-0x04 dispatch inputs.  These are deliberately
# machine-level facts only: the shared state and active-record table are not
# assigned a production/UI meaning by this contract.
UPSTREAM_BYTES = {
    0x0041E635: bytes.fromhex("e8 56 98 01 00"),
    0x0041E64E: bytes.fromhex("e8 8d e8 ff ff"),
    0x0041E6FE: bytes.fromhex("e8 dd e7 ff ff"),
    0x0041CEFC: bytes.fromhex("8b 0d cc 1d 9e 00"),
    0x0041EBF6: bytes.fromhex("66 8b 0d fe 2f 89 00"),
    0x0041EC61: bytes.fromhex("a1 c8 24 89 00"),
    0x0041EC71: bytes.fromhex("66 8b 34 95 28 90 89 00"),
    0x00412E61: bytes.fromhex("89 14 8d 28 90 89 00"),
    0x00412EBC: bytes.fromhex("66 89 3c 8d 28 90 89 00"),
    0x0041CEE0: bytes.fromhex("66 83 3d fe 2f 89 00 00"),
    0x00437EA5: bytes.fromhex("c7 05 cc 1d 9e 00 00 00 00 00"),
}

# The coordinate path is pinned as machine provenance only. It connects the
# Win32 message pump and mouse-message handler to the coordinate words consumed
# by the existing input-state updater; it does not claim gameplay/UI meaning or
# verify the 1600x1200 runtime.
INPUT_PROVENANCE_BYTES = {
    0x00423C34: bytes.fromhex("c7 44 24 14 c0 3d 42 00"),
    0x00423C8B: bytes.fromhex("ff 15 64 52 4e 00"),
    0x004232FC: bytes.fromhex("ff 15 18 52 4e 00"),
    0x00424364: bytes.fromhex("89 0d 58 cb c0 00"),
    0x0042436A: bytes.fromhex("a3 5c cb c0 00"),
    0x0042436F: bytes.fromhex("e8 3c d3 ff ff"),
    0x004216B0: bytes.fromhex(
        "a1 b8 24 89 00 56 83 f8 0a 57 0f 82 e3 00 00 00"
    ),
    0x004217B0: bytes.fromhex(
        "a1 70 e2 61 00 85 c0 0f 84 93 00 00 00 8b 44 24 04"
    ),
    0x00423FE8: bytes.fromhex("e8 53 87 ff ff"),
    0x0041C81E: bytes.fromhex("e8 fd 19 00 00"),
    0x0041E299: bytes.fromhex("e8 12 35 00 00"),
    0x0041E45F: bytes.fromhex("b9 50 93 63 00"),
    0x0041E464: bytes.fromhex("e8 37 32 03 00"),
    0x0041E4AF: bytes.fromhex("66 89 0d 34 77 63 00"),
    0x0041E4B6: bytes.fromhex("66 a3 36 77 63 00"),
    0x0041E626: bytes.fromhex("66 a1 36 77 63 00"),
    0x0041E62C: bytes.fromhex("66 8b 0d 34 77 63 00"),
    0x0041E635: bytes.fromhex("e8 56 98 01 00"),
}

INPUT_PROVENANCE_CALLS = (
    (0x0042436F, 0x004216B0),
    (0x00423FE8, 0x0041C740),
    (0x0041C81E, 0x0041E220),
    (0x0041E299, 0x004217B0),
    (0x0041E464, 0x004516A0),
    (0x0041E635, 0x00437E90),
)

# The branch edges between the updater call and the state load are pinned
# separately from the code-0x04 dispatch block. They describe machine flow
# only; they do not assign a UI or production meaning to the shared globals.
UPSTREAM_BRANCHES = (
    Branch(0x0041E624, bytes.fromhex("75 17"), 0x0041E63D),
    Branch(0x0041E644, bytes.fromhex("75 0d"), 0x0041E653),
    Branch(0x0041E64C, bytes.fromhex("75 05"), 0x0041E653),
    Branch(0x0041E6FC, bytes.fromhex("75 17"), 0x0041E715),
    Branch(0x0041E705, bytes.fromhex("74 67"), 0x0041E76E),
    Branch(0x0041E77B, bytes.fromhex("0f 85 fe 03 00 00"), 0x0041EB7F),
    Branch(0x0041EB8B, bytes.fromhex("75 67"), 0x0041EBF4),
    Branch(0x0041EB9C, bytes.fromhex("7d 58"), 0x0041EBF6),
    Branch(0x0041EBA5, bytes.fromhex("7d 4f"), 0x0041EBF6),
    Branch(0x0041EBAD, bytes.fromhex("75 47"), 0x0041EBF6),
)

# Exact direct stores observed by instruction decoding. The old bytes are
# checked so a future binary cannot silently reuse these addresses with a
# different operation. The lists are intentionally kept separate per global:
# 0x009E1DCC is the updater/mapper mask state and 0x00892FFE is the later state
# code consumed at 0x0041EBF6.
DATA_WRITER_BYTES = {
    0x009E1DCC: {
        0x0041E392: bytes.fromhex("89 1d cc 1d 9e 00"),
        0x00437EA5: bytes.fromhex("c7 05 cc 1d 9e 00 00 00 00 00"),
        0x00437F92: bytes.fromhex("89 15 cc 1d 9e 00"),
        0x00438106: bytes.fromhex("89 15 cc 1d 9e 00"),
        0x00438179: bytes.fromhex("89 15 cc 1d 9e 00"),
        0x004382ED: bytes.fromhex("a3 cc 1d 9e 00"),
        0x00438315: bytes.fromhex("89 0d cc 1d 9e 00"),
        0x0043836A: bytes.fromhex("a3 cc 1d 9e 00"),
        0x0043847B: bytes.fromhex("a3 cc 1d 9e 00"),
        0x00438498: bytes.fromhex("a3 cc 1d 9e 00"),
    },
    0x00892FFE: {
        0x00412EE7: bytes.fromhex("66 89 3d fe 2f 89 00"),
        0x0041CF16: bytes.fromhex("66 89 15 fe 2f 89 00"),
        0x0041CF39: bytes.fromhex("66 c7 05 fe 2f 89 00 03 00"),
        0x0041CF5F: bytes.fromhex("66 c7 05 fe 2f 89 00 04 00"),
        0x0041CF85: bytes.fromhex("66 c7 05 fe 2f 89 00 20 00"),
        0x0041CFAB: bytes.fromhex("66 c7 05 fe 2f 89 00 25 00"),
        0x0041CFD1: bytes.fromhex("66 c7 05 fe 2f 89 00 4a 00"),
        0x0041CFF7: bytes.fromhex("66 c7 05 fe 2f 89 00 09 00"),
        0x0041EA14: bytes.fromhex("66 a3 fe 2f 89 00"),
        0x0041EBC0: bytes.fromhex("66 89 3d fe 2f 89 00"),
        0x0041F0AC: bytes.fromhex("66 89 3d fe 2f 89 00"),
        0x004997D6: bytes.fromhex("66 a3 fe 2f 89 00"),
        0x00499A61: bytes.fromhex("66 89 1d fe 2f 89 00"),
        0x00499B0A: bytes.fromhex("66 a3 fe 2f 89 00"),
        0x00499C22: bytes.fromhex("66 a3 fe 2f 89 00"),
        0x00499CF2: bytes.fromhex("66 a3 fe 2f 89 00"),
        0x00499D82: bytes.fromhex("66 a3 fe 2f 89 00"),
        0x00499E75: bytes.fromhex("66 a3 fe 2f 89 00"),
    },
}

ACTIVE_RECORD_HELPER = 0x00412D90
STATE_MAPPING_HELPER = 0x0041CEE0
INPUT_STATE_UPDATER = 0x00437E90

GUARD_BYTES = bytes.fromhex(
    """
    66 83 3d 18 d8 4e 00 03 66 89 15 fe aa 05 01 75
    34 66 85 f6 74 2f 66 85 c9 74 2a 8b 2d 7c 2d b4
    00 0f bf c6 2b c5 99 33 c2 2b c2 83 f8 11 7f 30
    8b 2d 80 2d b4 00 0f bf c1 2b c5 99 33 c2 2b c2
    83 f8 11 7f 1b 0f bf c9 51 0f bf 4c 24 10 0f bf
    d6 c1 e1 05 52 81 c1 a0 7c 05 01 e8 f1 e3 ff ff
    5e
    """
)


class BinaryContractError(ValueError):
    """Raised when a binary is not the pinned original or its contract drifts."""


BRANCHES = (
    Branch(0x004AC48E, b"\x75\x34", CALL_BLOCK),
    Branch(0x004AC493, b"\x74\x2f", CALL_BLOCK),
    Branch(0x004AC498, b"\x74\x2a", CALL_BLOCK),
    Branch(0x004AC4AD, b"\x7f\x30", RETURN_BLOCK),
    Branch(0x004AC4C2, b"\x7f\x1b", RETURN_BLOCK),
)


Dispatch = Literal["call", "skip"]


def guard_dispatch(
    *,
    count_positive: bool,
    mode: int,
    first_field_nonzero: bool,
    second_field_nonzero: bool,
    first_distance: int,
    second_distance: int,
) -> Dispatch:
    """Return the dispatch path encoded by the original branch graph.

    This is a static truth table for the machine branches, not a claim about the
    production meaning of the ring record or its fields.
    """
    if not count_positive:
        return "skip"
    if mode != 3 or not first_field_nonzero or not second_field_nonzero:
        return "call"
    if first_distance > 0x11 or second_distance > 0x11:
        return "skip"
    return "call"


def _offset(address: int) -> int:
    return address - IMAGE_BASE


def _read(data: bytes, address: int, size: int) -> bytes:
    start = _offset(address)
    end = start + size
    if start < 0 or end > len(data):
        raise BinaryContractError(f"address outside file: {address:#x}+{size}")
    return data[start:end]


def _relative_target(data: bytes, address: int) -> int:
    raw = _offset(address)
    if data[raw] == 0x0F and 0x80 <= data[raw + 1] <= 0x8F:
        displacement = struct.unpack_from("<i", data, raw + 2)[0]
        return address + 6 + displacement
    if data[raw] == 0xE9:
        displacement = struct.unpack_from("<i", data, raw + 1)[0]
        return address + 5 + displacement
    displacement = struct.unpack_from("<b", data, raw + 1)[0]
    return address + 2 + displacement


def _direct_callers(data: bytes, target: int) -> list[int]:
    callers: list[int] = []
    for raw in range(len(data) - 5):
        if data[raw] != 0xE8:
            continue
        address = IMAGE_BASE + raw
        displacement = struct.unpack_from("<i", data, raw + 1)[0]
        if address + 5 + displacement == target:
            callers.append(address)
    return callers


def _direct_calls(data: bytes, start: int, end: int) -> list[tuple[int, int]]:
    """Return direct E8 callsite/target pairs in an address range."""
    calls: list[tuple[int, int]] = []
    for raw in range(_offset(start), _offset(end)):
        if data[raw] != 0xE8 or raw + 5 > len(data):
            continue
        address = IMAGE_BASE + raw
        displacement = struct.unpack_from("<i", data, raw + 1)[0]
        calls.append((address, address + 5 + displacement))
    return calls


def validate(path: Path) -> dict[str, object]:
    """Validate one binary without writing to it or creating derived assets."""
    data = path.read_bytes()
    observed_sha256 = hashlib.sha256(data).hexdigest()
    if observed_sha256 != ORIGINAL_SHA256:
        raise BinaryContractError(
            f"unexpected executable SHA-256 for {path}: {observed_sha256}"
        )

    observed_guard = _read(data, GUARD_START, GUARD_END - GUARD_START + 1)
    if observed_guard != GUARD_BYTES:
        raise BinaryContractError("event-ring guard bytes do not match the pinned contract")

    branches: dict[str, int] = {}
    for branch in BRANCHES:
        if _read(data, branch.address, len(branch.opcode)) != branch.opcode:
            raise BinaryContractError(f"branch opcode drift at {branch.address:#x}")
        target = _relative_target(data, branch.address)
        if target != branch.target:
            raise BinaryContractError(
                f"branch target drift at {branch.address:#x}: {target:#x}"
            )
        branches[f"{branch.address:#x}"] = target

    callers = _direct_callers(data, DEQUEUE_ADDRESS)
    if callers != [0x004233AE]:
        raise BinaryContractError(f"unexpected dequeue callers: {[hex(x) for x in callers]}")
    if _read(data, 0x004AC4DA, 5) != bytes.fromhex("e8 f1 e3 ff ff"):
        raise BinaryContractError("dequeue call site drift")
    call_displacement = struct.unpack_from("<i", data, _offset(0x004AC4DA) + 1)[0]
    if 0x004AC4DA + 5 + call_displacement != CALL_TARGET:
        raise BinaryContractError("dequeue call target drift")
    if _read(data, 0x004AA8D0, 32) != bytes.fromhex(
        "83 ec 08 53 55 8b e9 33 db 8b 0d 74 39 b9 00 3b "
        "cb 75 0a 5d 33 c0 5b 83 c4 08 c2 08 00 66 8b 45"
    ):
        raise BinaryContractError("dequeue callee entry drift")

    if _read(data, PRODUCER_ADDRESS, len(PRODUCER_BYTES)) != PRODUCER_BYTES:
        raise BinaryContractError("producer wrapper bytes do not match the pinned contract")
    producer_callers = _direct_callers(data, PRODUCER_ADDRESS)
    if producer_callers != [0x0041EC9A]:
        raise BinaryContractError(
            f"unexpected producer wrapper callers: {[hex(x) for x in producer_callers]}"
        )
    producer_calls = _direct_calls(data, PRODUCER_ADDRESS, PRODUCER_ADDRESS + len(PRODUCER_BYTES))
    if producer_calls != [(0x0040FB6C, PRODUCER_TARGET)]:
        raise BinaryContractError(f"unexpected producer wrapper calls: {producer_calls}")
    producer_to_enqueue_direct = any(
        target == ENQUEUE_ADDRESS for _, target in producer_calls
    )

    if _read(data, ENQUEUE_ADDRESS, len(ENQUEUE_BYTES)) != ENQUEUE_BYTES:
        raise BinaryContractError("ring enqueue bytes do not match the pinned contract")
    enqueue_calls = _direct_calls(data, ENQUEUE_ADDRESS, ENQUEUE_ADDRESS + len(ENQUEUE_BYTES))
    if enqueue_calls != [(0x004AC415, ENQUEUE_TARGET)]:
        raise BinaryContractError(f"unexpected ring enqueue calls: {enqueue_calls}")
    enqueue_callers = _direct_callers(data, ENQUEUE_ADDRESS)
    if len(enqueue_callers) != 134:
        raise BinaryContractError(f"unexpected ring enqueue caller count: {len(enqueue_callers)}")

    if _read(data, ENQUEUE_TARGET, len(RECORD_WRITER_BYTES)) != RECORD_WRITER_BYTES:
        raise BinaryContractError("ring record writer bytes do not match the pinned contract")
    writer_callers = _direct_callers(data, ENQUEUE_TARGET)
    if writer_callers != [0x004AC415]:
        raise BinaryContractError(
            f"unexpected ring record writer callers: {[hex(x) for x in writer_callers]}"
        )

    if _read(data, DISPATCH_START, len(DISPATCH_BYTES)) != DISPATCH_BYTES:
        raise BinaryContractError("code-0x04 dispatch block bytes do not match the pinned contract")

    dispatch_branches: dict[str, int] = {}
    for branch in DISPATCH_BRANCHES:
        if _read(data, branch.address, len(branch.opcode)) != branch.opcode:
            raise BinaryContractError(f"dispatch branch opcode drift at {branch.address:#x}")
        target = _relative_target(data, branch.address)
        if target != branch.target:
            raise BinaryContractError(
                f"dispatch branch target drift at {branch.address:#x}: {target:#x}"
            )
        dispatch_branches[f"{branch.address:#x}"] = target

    dispatch_calls: dict[str, int] = {}
    for callsite, target in DISPATCH_CALLS:
        calls = _direct_calls(data, callsite, callsite + 5)
        if calls != [(callsite, target)]:
            raise BinaryContractError(
                f"dispatch call drift at {callsite:#x}: {calls}"
            )
        dispatch_calls[f"{callsite:#x}"] = target

    for helper, helper_bytes in DISPATCH_HELPER_BYTES.items():
        if _read(data, helper, len(helper_bytes)) != helper_bytes:
            raise BinaryContractError(f"dispatch helper bytes drift at {helper:#x}")

    for address, expected in UPSTREAM_BYTES.items():
        if _read(data, address, len(expected)) != expected:
            raise BinaryContractError(f"dispatch upstream bytes drift at {address:#x}")

    for address, expected in INPUT_PROVENANCE_BYTES.items():
        if _read(data, address, len(expected)) != expected:
            raise BinaryContractError(f"input provenance bytes drift at {address:#x}")

    input_provenance_calls: dict[str, int] = {}
    for callsite, target in INPUT_PROVENANCE_CALLS:
        calls = _direct_calls(data, callsite, callsite + 5)
        if calls != [(callsite, target)]:
            raise BinaryContractError(
                f"input provenance call drift at {callsite:#x}: {calls}"
            )
        input_provenance_calls[f"{callsite:#x}"] = target

    upstream_branches: dict[str, int] = {}
    for branch in UPSTREAM_BRANCHES:
        if _read(data, branch.address, len(branch.opcode)) != branch.opcode:
            raise BinaryContractError(f"upstream branch opcode drift at {branch.address:#x}")
        target = _relative_target(data, branch.address)
        if target != branch.target:
            raise BinaryContractError(
                f"upstream branch target drift at {branch.address:#x}: {target:#x}"
            )
        upstream_branches[f"{branch.address:#x}"] = target

    data_writer_xrefs: dict[str, list[str]] = {}
    for target, writers in DATA_WRITER_BYTES.items():
        for address, expected in writers.items():
            if _read(data, address, len(expected)) != expected:
                raise BinaryContractError(
                    f"data writer bytes drift for {target:#x} at {address:#x}"
                )
        data_writer_xrefs[f"{target:#x}"] = [hex(address) for address in writers]

    state_mapping_callers = _direct_callers(data, STATE_MAPPING_HELPER)
    if state_mapping_callers != [0x0041DCFA, 0x0041E64E, 0x0041E6FE]:
        raise BinaryContractError(
            "unexpected state-mapping helper callers: "
            f"{[hex(x) for x in state_mapping_callers]}"
        )

    input_state_updater_callers = _direct_callers(data, INPUT_STATE_UPDATER)
    if input_state_updater_callers != [0x0041E635]:
        raise BinaryContractError(
            "unexpected input-state updater callers: "
            f"{[hex(x) for x in input_state_updater_callers]}"
        )

    active_record_helper_callers = _direct_callers(data, ACTIVE_RECORD_HELPER)
    if active_record_helper_callers != [
        0x00407192,
        0x00409C8E,
        0x00409FB9,
        0x0040F7F1,
        0x00412A1E,
        0x004170B5,
        0x0044302D,
        0x00476EDC,
        0x0047B5B9,
        0x0048E209,
        0x0048E7E0,
    ]:
        raise BinaryContractError(
            "unexpected active-record helper callers: "
            f"{[hex(x) for x in active_record_helper_callers]}"
        )

    return {
        "path": str(path),
        "sha256": observed_sha256,
        "guard_range": [hex(GUARD_START), hex(GUARD_END)],
        "branch_targets": branches,
        "dequeue_callers": [hex(address) for address in callers],
        "producer_callers": [hex(address) for address in producer_callers],
        "producer_direct_callees": [hex(target) for _, target in producer_calls],
        "producer_to_enqueue_direct": producer_to_enqueue_direct,
        "enqueue_callers_count": len(enqueue_callers),
        "enqueue_record_writer": "0x4ac415->0x4aa820",
        "record_word_store_order": [
            "arg1 -> [ecx+0x0]",
            "arg2 -> [ecx+0x2]",
            "arg3 -> [ecx+0x4]",
        ],
        "dispatch_range": [hex(DISPATCH_START), hex(DISPATCH_END - 1)],
        "dispatch_branch_targets": dispatch_branches,
        "dispatch_calls": {site: hex(target) for site, target in dispatch_calls.items()},
        "dispatch_enqueue_callsite": hex(DISPATCH_ENQUEUE_CALLSITE),
        "dispatch_enqueue_reachability": DISPATCH_REACHABILITY,
        "dispatch_argument_provenance": DISPATCH_ARGUMENT_PROVENANCE,
        "dispatch_truth_table": "count<=0 skip; mode!=3 or either field==0 call; otherwise any distance>0x11 skip, else call",
        "dispatch_upstream": {
            "upstream_branch_targets": upstream_branches,
            "updater_callsite": "0x0041E635->0x00437E90 (unique direct caller)",
            "mask_to_mapper_read": "0x0041CEFC: DWORD [0x009E1DCC]",
            "mapper_to_state_load": "0x0041CEE0 writes 0x00892FFE; consumed at 0x0041EBF6",
            "data_writer_xrefs": data_writer_xrefs,
            "cx_dominating_load": "0x0041EBF6: WORD [0x00892FFE]",
            "esi_loop_load": "0x0041EC71: WORD [0x00899028 + 4 * EDX]",
            "esi_loop_index_source": "0x0041EC61: DWORD [0x008924C8] + EDI, unsigned remainder / 0x14",
            "state_mapping_helper": hex(STATE_MAPPING_HELPER),
            "state_mapping_callers": [hex(address) for address in state_mapping_callers],
            "input_state_updater": hex(INPUT_STATE_UPDATER),
            "input_state_updater_callers": [hex(address) for address in input_state_updater_callers],
            "active_record_table": "0x00899028, 20 slots * 4 bytes",
            "active_record_writers": ["0x00412E61 add", "0x00412EBC clear"],
            "active_record_helper_callers": [hex(address) for address in active_record_helper_callers],
            "direct_input_to_active_record_writer": False,
            "direct_state_mapper_to_enqueue": False,
        },
        "input_message_provenance": {
            "wndproc_registration": "0x00423C34 -> 0x00423DC0; RegisterClassA at 0x00423C8B",
            "message_dispatch": "DispatchMessageA IAT call at 0x004232FC",
            "mouse_coordinates": "WM_MOUSEMOVE handler 0x0042434B stores lParam low/high at 0x00C0CB58/0x00C0CB5C",
            "event_ring": "0x0042436F -> 0x004216B0; game tick 0x0041E299 -> 0x004217B0",
            "coordinate_words": "0x0041E4AF/0x0041E4B6 write 0x00637734/0x00637736",
            "updater_arguments": "0x0041E626/0x0041E62C load 0x00637736/0x00637734; 0x0041E635 -> 0x00437E90",
            "direct_calls": {site: hex(target) for site, target in input_provenance_calls.items()},
            "semantic_status": "OS input origin statically connected; gameplay meaning, output resolution, and runtime behavior remain unverified",
        },
    }
