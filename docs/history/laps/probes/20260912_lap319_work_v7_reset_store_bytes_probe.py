"""lap319 work probe — make folded-instruction byte collection fail closed.

This is a read-only audit of the pinned original PE32 executable.  Instruction
values come from the PE image; instruction boundaries come from the next
disassembly address.  The objdump byte column is reconstructed from its main
row and continuation rows only to enforce the invariant that the column's
complete length equals that address delta.

The probe deliberately keeps the R2 facts in scope as regression invariants,
but does not change any binary, patch, pin, or runtime evidence.
"""
from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import sys


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

MAP_ENTRY = 0x431AB0
MAP_END = 0x4324D6
GATE = 0x431AF2
FAILURE_SEED = 0x431AF4
SUCCESS_JOIN = 0x431AFE
SUCCESS_RET = 0x4324D5
SCREEN_GLOBALS = (0xE5BF1C, 0xE5BF20)
SCREEN_WRITERS = (0x431B79, 0x431B7F, 0x4324B8, 0x4324C2)
RESET_WRITERS = (0x4324B8, 0x4324C2)
GATE_BYTES = bytes.fromhex("750a")
FAILURE_ARM_BYTES = bytes.fromhex("5f5e5d33c05b83c434c3")
EXPECTED_RESET_BYTES = {
    0x4324B8: bytes.fromhex("c7051cbfe50080020000"),
    0x4324C2: bytes.fromhex("c70520bfe500e0010000"),
}

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
CONTINUATION_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*$", re.MULTILINE)
DIRECT_BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\s+0x([0-9a-f]+)$")
ANY_BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\b")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
SCREEN_WRITER_RE = re.compile(r"^mov\s+DWORD PTR ds:0x(e5bf1c|e5bf20),")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_sections(image: bytes) -> tuple[int, list[tuple[str, int, int, int, int]]]:
    (e_lfanew,) = struct.unpack_from("<I", image, 0x3C)
    if image[e_lfanew : e_lfanew + 4] != b"PE\0\0":
        raise ValueError("not a PE image")
    coff = e_lfanew + 4
    section_count = struct.unpack_from("<H", image, coff + 2)[0]
    optional_size = struct.unpack_from("<H", image, coff + 16)[0]
    optional = coff + 20
    image_base = struct.unpack_from("<I", image, optional + 28)[0]
    cursor = optional + optional_size
    sections = []
    for _ in range(section_count):
        name = image[cursor : cursor + 8].rstrip(b"\0").decode("latin1")
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", image, cursor + 8
        )
        sections.append((name, virtual_address, virtual_size, raw_pointer, raw_size))
        cursor += 40
    return image_base, sections


def virtual_to_raw(
    image_base: int, sections: list[tuple[str, int, int, int, int]], address: int
) -> int | None:
    rva = address - image_base
    for _name, virtual_address, virtual_size, raw_pointer, raw_size in sections:
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            offset = rva - virtual_address
            return raw_pointer + offset if offset < raw_size else None
    return None


def pe_bytes(
    image: bytes,
    image_base: int,
    sections: list[tuple[str, int, int, int, int]],
    address: int,
    length: int,
) -> bytes | None:
    if length <= 0:
        return None
    start = virtual_to_raw(image_base, sections, address)
    end = virtual_to_raw(image_base, sections, address + length - 1)
    if start is None or end is None or end != start + length - 1:
        return None
    return image[start : start + length]


def parse_listing(text: str) -> tuple[list[tuple[int, bytes, str]], list[tuple[int, bytes]]]:
    rows = [
        (int(address, 16), bytes.fromhex(raw), instruction)
        for address, raw, instruction in INSN_RE.findall(text)
    ]
    row_addresses = {address for address, _raw, _instruction in rows}
    continuations = [
        (int(address, 16), bytes.fromhex(raw))
        for address, raw in CONTINUATION_RE.findall(text)
        if int(address, 16) not in row_addresses
    ]
    return rows, continuations


def disassemble() -> tuple[list[tuple[int, bytes, str]], list[tuple[int, bytes]]]:
    listing = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return parse_listing(listing)


def collect_folded_instruction(
    rows: list[tuple[int, bytes, str]],
    continuations: list[tuple[int, bytes]],
    image: bytes,
    image_base: int,
    sections: list[tuple[str, int, int, int, int]],
    start: int,
) -> dict[str, object]:
    """Validate one instruction using PE values and disassembly boundaries."""
    row_index = next((index for index, row in enumerate(rows) if row[0] == start), None)
    if row_index is None:
        return {"ok": False, "reason": "missing_instruction_row", "address": f"0x{start:x}"}

    address, primary, _instruction = rows[row_index]
    next_address = rows[row_index + 1][0] if row_index + 1 < len(rows) else None
    if next_address is None:
        return {
            "ok": False,
            "reason": "missing_next_address_boundary",
            "address": f"0x{start:x}",
            "primary_bytes": primary.hex(),
        }
    boundary_length = next_address - address
    if boundary_length <= 0:
        return {
            "ok": False,
            "reason": "non_positive_or_overlapping_boundary",
            "address": f"0x{start:x}",
            "next_address": f"0x{next_address:x}",
            "boundary_length": boundary_length,
        }

    column = bytearray(primary)
    continuation_reason: str | None = None
    continuation_rows = sorted(
        (continuation_address, raw)
        for continuation_address, raw in continuations
        if address < continuation_address < next_address
    )
    cursor = address + len(column)
    for continuation_address, raw in continuation_rows:
        if continuation_address < cursor:
            continuation_reason = "continuation_overlap"
            break
        if continuation_address > cursor:
            continuation_reason = "continuation_gap"
            break
        column.extend(raw)
        cursor += len(raw)
    if continuation_reason:
        return {
            "ok": False,
            "reason": continuation_reason,
            "address": f"0x{start:x}",
            "boundary_length": boundary_length,
            "primary_bytes": primary.hex(),
            "column_bytes": bytes(column).hex(),
        }

    column_bytes = bytes(column)
    if len(column_bytes) > boundary_length:
        reason = "column_overlaps_next_instruction"
    elif len(column_bytes) < boundary_length:
        reason = "column_shorter_than_address_delta"
    else:
        reason = None

    image_bytes = pe_bytes(image, image_base, sections, address, boundary_length)
    if image_bytes is None:
        reason = reason or "pe_read_out_of_range"
    elif image_bytes[: len(column_bytes)] != column_bytes:
        reason = reason or "column_not_pe_prefix"

    result: dict[str, object] = {
        "ok": reason is None,
        "reason": reason,
        "address": f"0x{address:x}",
        "next_address": f"0x{next_address:x}",
        "boundary_source": "next disassembly instruction address minus current address",
        "boundary_length": boundary_length,
        "primary_bytes": primary.hex(),
        "column_bytes": column_bytes.hex(),
        "column_length": len(column_bytes),
        "value_source": "original PE VA-to-raw read",
        "image_bytes": image_bytes.hex() if image_bytes is not None else None,
        "image_length": len(image_bytes) if image_bytes is not None else None,
        "column_is_pe_prefix": image_bytes is not None and image_bytes[: len(column_bytes)] == column_bytes,
        "length_invariant": len(column_bytes) == boundary_length,
    }
    return result


def build_cfg(window: list[tuple[int, str]]) -> tuple[dict[int, set[int]], list[str]]:
    known = {address for address, _instruction in window}
    graph: dict[int, set[int]] = {}
    unresolved: list[str] = []
    for index, (address, instruction) in enumerate(window):
        if RET_RE.match(instruction):
            graph[address] = set()
            continue
        fallthrough = window[index + 1][0] if index + 1 < len(window) else None
        direct = DIRECT_BRANCH_RE.match(instruction)
        if direct:
            mnemonic, target_text = direct.groups()
            target = int(target_text, 16)
            edges = {target}
            if mnemonic != "jmp" and fallthrough is not None:
                edges.add(fallthrough)
            if target not in known:
                unresolved.append(f"0x{address:x}: target 0x{target:x} outside window")
            graph[address] = {edge for edge in edges if edge in known}
            continue
        if ANY_BRANCH_RE.match(instruction):
            unresolved.append(f"0x{address:x}: indirect/unparsed branch: {instruction}")
            graph[address] = set()
            continue
        graph[address] = {fallthrough} if fallthrough in known else set()
    return graph, unresolved


def reachable(graph: dict[int, set[int]], start: int) -> set[int]:
    seen: set[int] = set()
    queue = deque([start])
    while queue:
        address = queue.popleft()
        if address in seen or address not in graph:
            continue
        seen.add(address)
        queue.extend(graph[address] - seen)
    return seen


def screen_writers(window: list[tuple[int, str]]) -> set[int]:
    return {address for address, instruction in window if SCREEN_WRITER_RE.match(instruction)}


def dominators(graph: dict[int, set[int]], start: int) -> dict[int, set[int]]:
    nodes = reachable(graph, start)
    predecessors = {node: set() for node in nodes}
    for source in nodes:
        for target in graph[source] & nodes:
            predecessors[target].add(source)
    result = {node: set(nodes) for node in nodes}
    result[start] = {start}
    changed = True
    while changed:
        changed = False
        for node in sorted(nodes - {start}):
            incoming = predecessors[node]
            candidate = {node} if not incoming else {node} | set.intersection(*(result[p] for p in incoming))
            if candidate != result[node]:
                result[node] = candidate
                changed = True
    return result


def collect_contiguous_rows(
    rows: list[tuple[int, bytes, str]], start: int, size: int
) -> tuple[bytes, bool, int]:
    cursor = start
    collected = b""
    consumed = 0
    for address, raw, _instruction in rows:
        if address < start:
            continue
        if address != cursor:
            return collected[:size], False, consumed
        collected += raw
        consumed += 1
        cursor = address + len(raw)
        if len(collected) >= size:
            return collected[:size], True, consumed
    return collected[:size], False, consumed


def fmt(values: set[int] | tuple[int, ...]) -> list[str]:
    return [f"0x{value:x}" for value in sorted(values)]


def main() -> int:  # noqa: C901 - one bounded evidence probe
    failures: list[str] = []
    report: dict[str, object] = {
        "lap": 319,
        "role": "work (static research/probe); no game code edited, no execution",
        "execution": False,
        "scope": "F1 reset-store full bytes and command-boundary invariant",
        "report_contract": "JSON is emitted on stdout; redirect stdout without hand transcription",
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    image = EXE.read_bytes()
    exe_sha = hashlib.sha256(image).hexdigest()
    report["exe_sha256"] = exe_sha
    report["exe_sha_matches"] = exe_sha == EXPECTED_EXE_SHA
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")

    image_base, sections = parse_sections(image)
    rows, continuations = disassemble()
    window_rows = [row for row in rows if MAP_ENTRY <= row[0] < MAP_END]
    window = [(address, instruction) for address, _raw, instruction in window_rows]
    graph, unresolved = build_cfg(window)
    from_entry = reachable(graph, MAP_ENTRY)
    failure_path = reachable(graph, FAILURE_SEED)
    success_path = reachable(graph, SUCCESS_JOIN)
    writers = screen_writers(window)
    before_gate = writers & dominators(graph, MAP_ENTRY).get(GATE, set())
    failure_writers = writers & failure_path
    success_writers = writers & success_path
    failure_bytes, failure_contiguous, failure_consumed = collect_contiguous_rows(
        window_rows, FAILURE_SEED, len(FAILURE_ARM_BYTES)
    )

    reset_reports = {
        f"0x{address:x}": collect_folded_instruction(
            rows, continuations, image, image_base, sections, address
        )
        for address in RESET_WRITERS
    }
    gate_row = next((raw for address, raw, _instruction in window_rows if address == GATE), b"")
    gate_image = pe_bytes(image, image_base, sections, GATE, len(GATE_BYTES))
    taken_target = GATE + 2 + int.from_bytes(gate_row[1:2], "little", signed=True) if len(gate_row) >= 2 else None

    report["image_base"] = f"0x{image_base:x}"
    report["sections"] = [
        {"name": name, "va": f"0x{image_base + va:x}", "raw": f"0x{raw:x}", "raw_size": raw_size}
        for name, va, _virtual_size, raw, raw_size in sections
    ]
    report["window"] = {
        "entry": f"0x{MAP_ENTRY:x}",
        "end": f"0x{MAP_END:x}",
        "instruction_count": len(window_rows),
        "entry_reachable_instruction_count": len(from_entry),
        "failure_arm_instruction_count": len(failure_path),
        "success_arm_instruction_count": len(success_path),
        "unresolved_branches": unresolved,
    }
    report["reset_writers"] = reset_reports
    report["r2"] = {
        "screen_writers": fmt(writers),
        "expected_screen_writers": fmt(set(SCREEN_WRITERS)),
        "pre_gate_screen_writers": fmt(before_gate),
        "failure_arm_screen_writers": fmt(failure_writers),
        "success_arm_screen_writers": fmt(success_writers),
        "failure_preserves_pre_gate_screen_writer_set": failure_writers == before_gate,
        "failure_has_no_new_screen_global_writer": not (failure_writers - before_gate),
    }
    report["gate"] = {
        "column_bytes": gate_row.hex(),
        "image_bytes": gate_image.hex() if gate_image else None,
        "is_conditional_branch": gate_row[:2] == GATE_BYTES,
        "taken_target": f"0x{taken_target:x}" if taken_target is not None else None,
        "taken_target_is_success_join": taken_target == SUCCESS_JOIN,
    }
    report["failure_arm"] = {
        "bytes": failure_bytes.hex(),
        "expected_bytes": FAILURE_ARM_BYTES.hex(),
        "is_contiguous": failure_contiguous,
        "instruction_count": failure_consumed,
        "returns_zero": failure_contiguous and failure_bytes == FAILURE_ARM_BYTES,
        "reaches_success_return": SUCCESS_RET in failure_path,
    }

    checks = [
        report["exe_sha_matches"],
        len(window_rows) == 753,
        len(from_entry) == 753,
        len(failure_path) == 7,
        len(success_path) == 724,
        not unresolved,
        writers == set(SCREEN_WRITERS),
        failure_writers == before_gate,
        success_writers == set(SCREEN_WRITERS),
        not failure_writers,
        GATE in from_entry,
        gate_row[:2] == GATE_BYTES,
        gate_image == GATE_BYTES,
        taken_target == SUCCESS_JOIN,
        failure_contiguous,
        failure_bytes == FAILURE_ARM_BYTES,
        SUCCESS_RET not in failure_path,
        all(row["ok"] for row in reset_reports.values()),
        all(row["boundary_length"] == 10 for row in reset_reports.values()),
        all(row["column_length"] == 10 for row in reset_reports.values()),
        all(row["image_bytes"] == EXPECTED_RESET_BYTES[int(address, 16)].hex() for address, row in reset_reports.items()),
    ]
    report["checks"] = {"count": len(checks), "passed": sum(bool(check) for check in checks)}
    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "direct/computed writers outside this map function and call bodies remain UNKNOWN",
        "this probe produces no G1/G2/G3/G4 product evidence",
    ]
    report["failures"] = failures
    report["verdict"] = "PASS" if all(checks) and not failures else "FAIL"
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
