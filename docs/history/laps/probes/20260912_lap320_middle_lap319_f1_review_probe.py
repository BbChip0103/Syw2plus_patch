"""lap320 middle probe — independent review of lap319's F1 folded-byte repair.

Section A re-derives every lap319 number from the pinned original PE and a fresh
objdump listing **without importing any earlier probe**.  It deliberately uses
different methods than lap319 where a second method exists: screen-global writers
are recognised from decoded instruction *bytes* (absolute dword stores `c7 05` and
`89 /r mod=00 rm=101`) instead of disassembly text, and folded instructions are
detected from the
address-delta/column-width disagreement rather than from a byte-count threshold.

Section B deliberately imports the lap319 probe to exercise its collector on
adversarial inputs lap319's own tests do not cover.  That import is review of the
artifact, never a source for the Section A re-derivation.

Section C re-runs the lap319 probe as a subprocess and compares the stdout digest
with the stored report, so the recorded evidence is reproducible rather than
transcribed.

Read-only: no binary, patch, pin, baseline, or runtime evidence is written.
"""
from __future__ import annotations

from collections import deque
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import sys


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
LAP319_PROBE = (
    REPO
    / "docs/history/laps/probes/20260912_lap319_work_v7_reset_store_bytes_probe.py"
)
LAP319_REPORT = REPO / "logs/lap319/lap319_reset_store_bytes.json"

EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
LAP319_INPUT_SHA = {
    "probe": "eeed0913ff2c9d041890315f99775aefef9ea098a24024bfed0244af1671e6d3",
    "test": "4a246d15882d00f046f1fef1dbbe55821c9cd0614dfbf233ac10581e2248522b",
    "report": "09e012dcd536dfd9c81af469e0fd4de16cbede02567e9fdc0aa00bf8f4161def",
}

MAP_ENTRY = 0x431AB0
MAP_END = 0x4324D6
GATE = 0x431AF2
FAILURE_SEED = 0x431AF4
SUCCESS_JOIN = 0x431AFE
SUCCESS_RET = 0x4324D5
SCREEN_GLOBALS = (0xE5BF1C, 0xE5BF20)
CLAIMED_SCREEN_WRITERS = (0x431B79, 0x431B7F, 0x4324B8, 0x4324C2)
CLAIMED_RESET_BYTES = {
    0x4324B8: "c7051cbfe50080020000",
    0x4324C2: "c70520bfe500e0010000",
}
CLAIMED_GATE_BYTES = "750a"
CLAIMED_FAILURE_ARM_BYTES = "5f5e5d33c05b83c434c3"
CLAIMED_COUNTS = {
    "window": 753,
    "entry_reachable": 753,
    "failure_arm": 7,
    "success_arm": 724,
    "folded": 27,
}

BRANCH_PREFIXES = ("j", "loop", "call")
STORE_IMM32_OPCODE = bytes.fromhex("c705")
STORE_REG_OPCODE = 0x89


# --------------------------------------------------------------------------
# Section A helpers — independent derivation
# --------------------------------------------------------------------------
def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def read_pe(image: bytes) -> tuple[int, list[dict[str, int | str]]]:
    """Walk the PE headers with explicit field offsets (no third-party parser)."""
    if image[:2] != b"MZ":
        raise ValueError("missing MZ signature")
    pe_offset = int.from_bytes(image[0x3C:0x40], "little")
    if image[pe_offset : pe_offset + 4] != b"PE\0\0":
        raise ValueError("missing PE signature")
    file_header = pe_offset + 4
    section_count = int.from_bytes(image[file_header + 2 : file_header + 4], "little")
    optional_size = int.from_bytes(image[file_header + 16 : file_header + 18], "little")
    optional = file_header + 20
    image_base = int.from_bytes(image[optional + 28 : optional + 32], "little")
    table = optional + optional_size
    sections: list[dict[str, int | str]] = []
    for index in range(section_count):
        entry = table + index * 40
        name = image[entry : entry + 8].rstrip(b"\0").decode("latin1")
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", image, entry + 8
        )
        sections.append(
            {
                "name": name,
                "virtual_address": virtual_address,
                "virtual_size": virtual_size,
                "raw_pointer": raw_pointer,
                "raw_size": raw_size,
            }
        )
    return image_base, sections


def file_slice(
    image: bytes,
    image_base: int,
    sections: list[dict[str, int | str]],
    address: int,
    length: int,
) -> bytes | None:
    """Return `length` file bytes for a virtual address, or None when unmapped."""
    if length <= 0:
        return None
    rva = address - image_base
    for section in sections:
        start_rva = int(section["virtual_address"])
        raw_size = int(section["raw_size"])
        offset = rva - start_rva
        if 0 <= offset and offset + length <= raw_size:
            start = int(section["raw_pointer"]) + offset
            chunk = image[start : start + length]
            return chunk if len(chunk) == length else None
    return None


def split_listing(text: str) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Classify objdump lines by *field count*, not by a hand-written line regex.

    An instruction line is `address:\\tbytes\\tmnemonic`; a folded continuation
    line is `address:\\tbytes` with no mnemonic field at all.
    """
    rows: list[dict[str, object]] = []
    continuations: list[dict[str, object]] = []
    for line in text.splitlines():
        if ":\t" not in line:
            continue
        head, _, rest = line.partition(":\t")
        head = head.strip()
        if not head or any(character not in "0123456789abcdef" for character in head):
            continue
        fields = rest.split("\t")
        byte_text = fields[0].strip()
        if not byte_text or any(
            len(token) != 2 or any(c not in "0123456789abcdef" for c in token)
            for token in byte_text.split()
        ):
            continue
        record = {
            "address": int(head, 16),
            "bytes": bytes.fromhex(byte_text.replace(" ", "")),
        }
        mnemonic = fields[1].strip() if len(fields) > 1 else ""
        if mnemonic:
            record["text"] = mnemonic
            rows.append(record)
        else:
            continuations.append(record)
    return rows, continuations


def disassemble_text() -> str:
    return subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def window_instructions(
    rows: list[dict[str, object]], start: int, end: int
) -> list[dict[str, object]]:
    return [row for row in rows if start <= int(row["address"]) < end]


def attach_boundaries(
    rows: list[dict[str, object]], window: list[dict[str, object]]
) -> list[dict[str, object]]:
    """Length of each window instruction = next listing address - this address."""
    addresses = [int(row["address"]) for row in rows]
    index = {address: position for position, address in enumerate(addresses)}
    resolved: list[dict[str, object]] = []
    for row in window:
        address = int(row["address"])
        position = index[address]
        next_address = addresses[position + 1] if position + 1 < len(addresses) else None
        resolved.append(
            {
                **row,
                "next_address": next_address,
                "length": None if next_address is None else next_address - address,
            }
        )
    return resolved


def reassemble_column(
    row: dict[str, object], continuations: dict[int, bytes]
) -> tuple[bytes, str | None]:
    """Glue folded continuation rows onto the main row; refuse any discontinuity."""
    address = int(row["address"])
    length = row["length"]
    column = bytearray(row["bytes"])  # type: ignore[arg-type]
    if length is None:
        return bytes(column), "missing_next_address_boundary"
    cursor = address + len(column)
    limit = address + int(length)
    while cursor < limit:
        chunk = continuations.get(cursor)
        if chunk is None:
            return bytes(column), "missing_continuation_row"
        column.extend(chunk)
        cursor += len(chunk)
    if cursor != limit:
        return bytes(column), "column_overruns_next_instruction"
    return bytes(column), None


def decode_screen_writer(insn_bytes: bytes) -> int | None:
    """Direct dword store to an absolute address, recognised from bytes not text.

    Two encodings reach the screen globals in this window:
    `c7 05 <abs32> <imm32>` (store immediate, 10 bytes) and
    `89 <modrm mod=00 rm=101> <abs32>` (store register, 6 bytes).
    """
    target: int | None = None
    if len(insn_bytes) == 10 and insn_bytes[:2] == STORE_IMM32_OPCODE:
        target = int.from_bytes(insn_bytes[2:6], "little")
    elif (
        len(insn_bytes) == 6
        and insn_bytes[0] == STORE_REG_OPCODE
        and insn_bytes[1] & 0xC7 == 0x05
    ):
        target = int.from_bytes(insn_bytes[2:6], "little")
    return target if target in SCREEN_GLOBALS else None


def build_graph(
    window: list[dict[str, object]],
) -> tuple[dict[int, set[int]], list[str]]:
    known = {int(row["address"]) for row in window}
    graph: dict[int, set[int]] = {}
    unresolved: list[str] = []
    for position, row in enumerate(window):
        address = int(row["address"])
        text = str(row["text"])
        mnemonic, _, operand = text.partition(" ")
        operand = operand.strip()
        fallthrough = (
            int(window[position + 1]["address"]) if position + 1 < len(window) else None
        )
        if mnemonic == "ret" or mnemonic.startswith("ret"):
            graph[address] = set()
            continue
        if mnemonic.startswith(BRANCH_PREFIXES) and not mnemonic.startswith("call"):
            target: int | None = None
            if operand.startswith("0x"):
                try:
                    target = int(operand, 16)
                except ValueError:
                    target = None
            if target is None:
                unresolved.append(f"0x{address:x}: unresolved branch {text}")
                graph[address] = set()
                continue
            edges = {target}
            if mnemonic != "jmp" and fallthrough is not None:
                edges.add(fallthrough)
            if target not in known:
                unresolved.append(f"0x{address:x}: target 0x{target:x} outside window")
            graph[address] = {edge for edge in edges if edge in known}
            continue
        graph[address] = {fallthrough} if fallthrough in known else set()
    return graph, unresolved


def reachable(graph: dict[int, set[int]], start: int) -> set[int]:
    seen: set[int] = set()
    queue = deque([start])
    while queue:
        node = queue.popleft()
        if node in seen or node not in graph:
            continue
        seen.add(node)
        queue.extend(graph[node] - seen)
    return seen


def hexes(values: set[int]) -> list[str]:
    return [f"0x{value:x}" for value in sorted(values)]


def derive(image: bytes) -> dict[str, object]:
    image_base, sections = read_pe(image)
    rows, continuation_rows = split_listing(disassemble_text())
    continuations = {int(row["address"]): row["bytes"] for row in continuation_rows}  # type: ignore[misc]
    row_addresses = {int(row["address"]) for row in rows}
    window = attach_boundaries(rows, window_instructions(rows, MAP_ENTRY, MAP_END))

    folded: list[dict[str, object]] = []
    writers: set[int] = set()
    prefix_damage: list[str] = []
    reassembly_failures: list[str] = []
    for row in window:
        address = int(row["address"])
        length = row["length"]
        column_width = len(row["bytes"])  # type: ignore[arg-type]
        if length is not None and column_width != int(length):
            folded.append(
                {
                    "address": f"0x{address:x}",
                    "column_width": column_width,
                    "boundary_length": int(length),
                }
            )
        column, reason = reassemble_column(row, continuations)
        if reason is not None:
            reassembly_failures.append(f"0x{address:x}: {reason}")
            continue
        truth = file_slice(image, image_base, sections, address, len(column))
        if truth is None or truth != column:
            prefix_damage.append(f"0x{address:x}")
            continue
        target = decode_screen_writer(column)
        if target is not None:
            writers.add(address)

    phantom = sorted(address for address in continuations if address in row_addresses)
    inside_folded = all(
        any(
            int(entry["address"], 16)
            < address
            < int(entry["address"], 16) + int(entry["boundary_length"])
            for entry in folded
        )
        for address in continuations
        if MAP_ENTRY <= address < MAP_END
    )

    graph, unresolved = build_graph(window)
    from_entry = reachable(graph, MAP_ENTRY)
    failure_arm = reachable(graph, FAILURE_SEED)
    success_arm = reachable(graph, SUCCESS_JOIN)

    resets: dict[str, object] = {}
    for address in CLAIMED_RESET_BYTES:
        row = next(
            (entry for entry in window if int(entry["address"]) == address), None
        )
        if row is None:
            resets[f"0x{address:x}"] = {"ok": False, "reason": "row_missing"}
            continue
        column, reason = reassemble_column(row, continuations)
        truth = file_slice(image, image_base, sections, address, int(row["length"]))
        resets[f"0x{address:x}"] = {
            "ok": reason is None and truth is not None and truth == column,
            "reason": reason,
            "boundary_length": row["length"],
            "boundary_source": "next listing address minus this address",
            "main_row_width": len(row["bytes"]),  # type: ignore[arg-type]
            "reassembled_column": column.hex(),
            "file_bytes": None if truth is None else truth.hex(),
            "value_source": "original PE VA->raw read",
            "decoded_target": (
                None
                if decode_screen_writer(column) is None
                else f"0x{decode_screen_writer(column):x}"
            ),
            "decoded_immediate": (
                None if len(column) != 10 else int.from_bytes(column[6:10], "little")
            ),
        }

    gate_row = next((entry for entry in window if int(entry["address"]) == GATE), None)
    gate_file = file_slice(image, image_base, sections, GATE, 2)
    taken = (
        None
        if gate_file is None
        else GATE + 2 + int.from_bytes(gate_file[1:2], "little", signed=True)
    )
    failure_file = file_slice(image, image_base, sections, FAILURE_SEED, 10)

    return {
        "image_base": f"0x{image_base:x}",
        "sections": [
            {
                "name": section["name"],
                "va": f"0x{image_base + int(section['virtual_address']):x}",
                "raw_pointer": f"0x{int(section['raw_pointer']):x}",
                "raw_size": section["raw_size"],
            }
            for section in sections
        ],
        "listing": {
            "instruction_rows": len(rows),
            "continuation_rows": len(continuations),
            "phantom_rows": [f"0x{address:x}" for address in phantom],
        },
        "counts": {
            "window": len(window),
            "entry_reachable": len(from_entry),
            "failure_arm": len(failure_arm),
            "success_arm": len(success_arm),
            "folded": len(folded),
        },
        "unresolved_branches": unresolved,
        "folded_instructions": folded,
        "folded_all_truncated_not_overrun": all(
            int(entry["column_width"]) < int(entry["boundary_length"])
            for entry in folded
        ),
        "window_continuations_inside_folded": inside_folded,
        "reassembly_failures": reassembly_failures,
        "column_prefix_damage": prefix_damage,
        "screen_writers": hexes(writers),
        "failure_arm_screen_writers": hexes(writers & failure_arm),
        "success_arm_screen_writers": hexes(writers & success_arm),
        "success_return_in_failure_arm": SUCCESS_RET in failure_arm,
        "resets": resets,
        "gate": {
            "text": None if gate_row is None else gate_row["text"],
            "file_bytes": None if gate_file is None else gate_file.hex(),
            "taken_target": None if taken is None else f"0x{taken:x}",
        },
        "failure_arm_bytes": None if failure_file is None else failure_file.hex(),
    }


# --------------------------------------------------------------------------
# Section B helpers — adversarial exercise of the lap319 artifact
# --------------------------------------------------------------------------
def load_lap319():
    spec = importlib.util.spec_from_file_location("lap319_probe", LAP319_PROBE)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {LAP319_PROBE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def synthetic_case(listing: str, payload: bytes, section_size: int | None = None):
    """Return the lap319 collector's verdict for a hand-written listing."""
    module = load_lap319()
    rows, continuations = module.parse_listing(listing)
    size = len(payload) if section_size is None else section_size
    sections = [(".text", 0x1000, size, 0x200, size)]
    image = bytes(0x200) + payload
    return module.collect_folded_instruction(
        rows, continuations, image, 0x400000, sections, 0x401000
    )


def adversarial_cases() -> dict[str, object]:
    """Cases lap319's own tests do not cover."""
    full = bytes.fromhex("c7051cbfe50080020000")
    main = "  401000:\tc7 05 1c bf e5 00 80 \tmov    DWORD PTR ds:0xe5bf1c,0x280\n"

    # (1) Column runs past the next instruction address (lap318 §4 wording of
    #     "overlap": next address < start + length).  lap319 tests only the
    #     continuation-vs-cursor overlap, so this branch is untested there.
    overrun = synthetic_case(
        main + "  401007:\t02 00 00 \n" + "  401008:\t90 \tnop\n", full
    )
    # (2) Continuation present but short: column stays under the delta.
    short_continuation = synthetic_case(
        main + "  401007:\t02 \n" + "  40100a:\t90 \tnop\n", full
    )
    # (3) Column is complete but the file bytes disagree (mutated image).
    mutated = synthetic_case(
        main + "  401007:\t02 00 00 \n" + "  40100a:\t90 \tnop\n",
        bytes.fromhex("c7051cbfe500ff020000"),
    )
    # (4) The reset row is absent from the listing entirely.
    missing_row = synthetic_case("  401010:\t90 \tnop\n", full)
    return {
        "column_overruns_next_instruction": {
            "ok": overrun["ok"],
            "reason": overrun.get("reason"),
        },
        "short_continuation": {
            "ok": short_continuation["ok"],
            "reason": short_continuation.get("reason"),
        },
        "column_not_file_prefix": {
            "ok": mutated["ok"],
            "reason": mutated.get("reason"),
        },
        "missing_instruction_row": {
            "ok": missing_row["ok"],
            "reason": missing_row.get("reason"),
            "reports_boundary_length": "boundary_length" in missing_row,
        },
    }


# --------------------------------------------------------------------------
# Section C — reproducibility of the recorded lap319 evidence
# --------------------------------------------------------------------------
def rerun_lap319() -> dict[str, object]:
    first = subprocess.run(
        [sys.executable, str(LAP319_PROBE)], check=False, capture_output=True
    )
    second = subprocess.run(
        [sys.executable, str(LAP319_PROBE)], check=False, capture_output=True
    )
    digest = hashlib.sha256(first.stdout).hexdigest()
    stored = sha256_file(LAP319_REPORT)
    return {
        "exit_codes": [first.returncode, second.returncode],
        "stdout_sha256": digest,
        "stdout_byte_identical_twice": first.stdout == second.stdout,
        "stored_report_sha256": stored,
        "stdout_matches_stored_report": stored == digest,
    }


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {
        "lap": 320,
        "role": "middle (diagnosis/plan/confirm); reviews lap319 work, writes no game code",
        "execution": False,
        "scope": "independent re-derivation of lap319 F1 bytes, boundaries and invariants",
        "report_contract": "JSON on stdout; redirect stdout instead of transcribing",
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1

    image = EXE.read_bytes()
    exe_sha = hashlib.sha256(image).hexdigest()
    report["exe_sha256"] = exe_sha
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")

    report["lap319_input_sha256"] = {
        "probe": sha256_file(LAP319_PROBE),
        "test": sha256_file(REPO / "tests/test_lap319_reset_store_bytes_probe.py"),
        "report": sha256_file(LAP319_REPORT),
    }
    report["lap319_inputs_match_record"] = (
        report["lap319_input_sha256"] == LAP319_INPUT_SHA
    )

    derived = derive(image)
    report["derived"] = derived
    report["adversarial"] = adversarial_cases()
    report["reproduction"] = rerun_lap319()

    counts = derived["counts"]
    resets = derived["resets"]
    adversarial = report["adversarial"]
    checks = {
        "exe_sha_pinned": exe_sha == EXPECTED_EXE_SHA,
        "lap319_inputs_unchanged": bool(report["lap319_inputs_match_record"]),
        "window_count": counts["window"] == CLAIMED_COUNTS["window"],
        "entry_reachable_count": counts["entry_reachable"]
        == CLAIMED_COUNTS["entry_reachable"],
        "failure_arm_count": counts["failure_arm"] == CLAIMED_COUNTS["failure_arm"],
        "success_arm_count": counts["success_arm"] == CLAIMED_COUNTS["success_arm"],
        "folded_count": counts["folded"] == CLAIMED_COUNTS["folded"],
        "no_unresolved_branches": not derived["unresolved_branches"],
        "folded_are_truncations": bool(derived["folded_all_truncated_not_overrun"]),
        "continuations_inside_folded": bool(
            derived["window_continuations_inside_folded"]
        ),
        "no_phantom_rows": not derived["listing"]["phantom_rows"],
        "no_reassembly_failures": not derived["reassembly_failures"],
        "no_prefix_damage": not derived["column_prefix_damage"],
        "screen_writers_match": derived["screen_writers"]
        == [f"0x{address:x}" for address in sorted(CLAIMED_SCREEN_WRITERS)],
        "failure_arm_has_no_screen_writer": not derived["failure_arm_screen_writers"],
        "success_arm_has_all_screen_writers": derived["success_arm_screen_writers"]
        == [f"0x{address:x}" for address in sorted(CLAIMED_SCREEN_WRITERS)],
        "success_return_outside_failure_arm": not derived[
            "success_return_in_failure_arm"
        ],
        "gate_bytes": derived["gate"]["file_bytes"] == CLAIMED_GATE_BYTES,
        "gate_taken_target": derived["gate"]["taken_target"] == f"0x{SUCCESS_JOIN:x}",
        "failure_arm_bytes": derived["failure_arm_bytes"] == CLAIMED_FAILURE_ARM_BYTES,
        "resets_ok": all(bool(entry["ok"]) for entry in resets.values()),
        "resets_boundary_is_ten": all(
            entry["boundary_length"] == 10 for entry in resets.values()
        ),
        "resets_main_row_is_seven": all(
            entry["main_row_width"] == 7 for entry in resets.values()
        ),
        "resets_bytes_match_claim": all(
            resets[f"0x{address:x}"]["file_bytes"] == expected
            for address, expected in CLAIMED_RESET_BYTES.items()
        ),
        "resets_column_equals_file": all(
            entry["reassembled_column"] == entry["file_bytes"]
            for entry in resets.values()
        ),
        "adversarial_overrun_fails_closed": adversarial[
            "column_overruns_next_instruction"
        ]["ok"]
        is False,
        "adversarial_short_continuation_fails_closed": adversarial[
            "short_continuation"
        ]["ok"]
        is False,
        "adversarial_mutation_fails_closed": adversarial["column_not_file_prefix"]["ok"]
        is False,
        "adversarial_missing_row_fails_closed": adversarial["missing_instruction_row"][
            "ok"
        ]
        is False,
        "lap319_report_reproducible": bool(
            report["reproduction"]["stdout_matches_stored_report"]
        )
        and bool(report["reproduction"]["stdout_byte_identical_twice"]),
    }
    failures.extend(name for name, passed in checks.items() if not passed)

    report["checks"] = checks
    report["check_counts"] = {
        "count": len(checks),
        "passed": sum(1 for passed in checks.values() if passed),
    }
    report["notes"] = [
        "lap319 reports 'missing_instruction_row' without boundary_length, so its main()"
        " check list would raise KeyError instead of emitting a FAIL verdict; that is"
        " fail-closed by crash, not a graceful failure",
        "lap319's direct row lookups (gate row, failure-arm collection) still bypass the"
        " new length invariant; both targets are unfolded today, so numbers are unaffected",
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or click evidence",
        "this probe produces no G1/G2/G3/G4 product evidence and closes no milestone",
    ]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
