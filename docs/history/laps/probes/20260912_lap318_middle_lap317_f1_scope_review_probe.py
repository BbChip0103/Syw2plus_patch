"""lap318 middle probe — independent review of the lap317 Astra F1 scope document.

The lap317 handoff asks middle to accept or reject three things before any work
implementation:

* reading the reset-store bytes **directly from the PE image**;
* treating a *normally* wrapped objdump instruction as a success and only a
  *damaged or incomplete* collection as fail-closed;
* leaving the E2/CFG acceptance numbers unchanged.

This probe re-derives the facts those decisions rest on.  It never imports the
lap315 or lap316 probes and never reads their stored reports as an oracle: the
only inputs are the original PE image and a fresh ``objdump`` listing.

Two byte sources are kept apart on purpose, exactly as lap317 asks:

* **values** come from the raw PE image (``struct`` section walk, VA -> raw);
* **instruction boundaries** come from the address column of the disassembly,
  which is correct even for a wrapped instruction because the wrapped
  continuation line carries no mnemonic and is not an instruction row.

That split is what makes "text line width" independent of "byte source", so a
wrapped byte column cannot silently shorten an instruction without the two
sources disagreeing.

Read-only static audit.  No game, Wine, Xvfb, runtime, Stage B, PNG, or click
path is run.  Nothing is written; JSON is emitted on stdout only.
"""
from __future__ import annotations

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

RESET_WRITERS = (0x4324B8, 0x4324C2)

# The acceptance table of docs/work/active/G1_ASTRA_F1_SCOPE_LAP317.md.
CLAIMED_RESET_BYTES = {
    0x4324B8: "c7051cbfe50080020000",
    0x4324C2: "c70520bfe500e0010000",
}
CLAIMED_GATE_BYTES = "750a"
CLAIMED_FAILURE_ARM_BYTES = "5f5e5d33c05b83c434c3"
CLAIMED_WINDOW_INSTRUCTIONS = 753
CLAIMED_FOLDED_IN_WINDOW = 27

# lap315's parser, reproduced verbatim so its behaviour is measured, not assumed.
LAP315_INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
# A byte-continuation line: address, bytes, and no mnemonic column.
CONTINUATION_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*$", re.MULTILINE)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_sections(image: bytes) -> tuple[int, list[tuple[str, int, int, int, int]]]:
    """Return ``(image_base, sections)`` from the raw PE headers."""
    (e_lfanew,) = struct.unpack_from("<I", image, 0x3C)
    if image[e_lfanew : e_lfanew + 4] != b"PE\0\0":
        raise ValueError("not a PE image")
    coff = e_lfanew + 4
    (section_count,) = struct.unpack_from("<H", image, coff + 2)
    (optional_size,) = struct.unpack_from("<H", image, coff + 16)
    optional = coff + 20
    (image_base,) = struct.unpack_from("<I", image, optional + 28)
    sections = []
    cursor = optional + optional_size
    for _ in range(section_count):
        name = image[cursor : cursor + 8].rstrip(b"\0").decode("latin1")
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", image, cursor + 8)
        sections.append((name, virtual_address, virtual_size, raw_pointer, raw_size))
        cursor += 40
    return image_base, sections


def virtual_to_raw(image_base: int, sections: list[tuple[str, int, int, int, int]], va: int) -> int | None:
    """Map a virtual address to a file offset, or ``None`` when it is not backed."""
    rva = va - image_base
    for _name, virtual_address, virtual_size, raw_pointer, raw_size in sections:
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            offset = rva - virtual_address
            if offset >= raw_size:
                return None
            return raw_pointer + offset
    return None


def pe_bytes(image: bytes, image_base: int, sections: list, va: int, length: int) -> bytes | None:
    """Read ``length`` bytes at ``va`` from the file, refusing partial reads."""
    start = virtual_to_raw(image_base, sections, va)
    end = virtual_to_raw(image_base, sections, va + length - 1) if length else start
    if start is None or end is None or end != start + length - 1:
        return None
    return image[start : start + length]


def parse_listing(text: str) -> tuple[list[tuple[int, bytes, str]], list[tuple[int, bytes]]]:
    """Split a listing into instruction rows and byte-continuation lines."""
    rows = [
        (int(address, 16), bytes.fromhex(raw), instruction)
        for address, raw, instruction in LAP315_INSN_RE.findall(text)
    ]
    row_addresses = {address for address, _raw, _instruction in rows}
    continuations = [
        (int(address, 16), bytes.fromhex(raw))
        for address, raw in CONTINUATION_RE.findall(text)
        if int(address, 16) not in row_addresses
    ]
    return rows, continuations


def boundary_lengths(rows: list[tuple[int, bytes, str]], end: int) -> dict[int, int]:
    """Instruction lengths taken from the address column, not the byte column."""
    lengths: dict[int, int] = {}
    for index, (address, _raw, _instruction) in enumerate(rows):
        following = rows[index + 1][0] if index + 1 < len(rows) else end
        lengths[address] = following - address
    return lengths


def truncation_audit(
    rows: list[tuple[int, bytes, str]],
    lengths: dict[int, int],
    image: bytes,
    image_base: int,
    sections: list,
) -> dict[str, object]:
    """Measure how the lap315 byte column diverges from the PE image."""
    folded: list[int] = []
    corrupted: list[int] = []
    for address, raw, _instruction in rows:
        length = lengths[address]
        full = pe_bytes(image, image_base, sections, address, length)
        if full is None:
            corrupted.append(address)
            continue
        if len(raw) != length:
            folded.append(address)
        if full[: len(raw)] != raw:
            corrupted.append(address)
    return {
        "folded_instructions": [f"0x{address:x}" for address in folded],
        "folded_instruction_count": len(folded),
        "byte_column_is_prefix_of_image": not corrupted,
        "corrupted_instructions": [f"0x{address:x}" for address in corrupted],
    }


def collect_contiguous_by_column(
    rows: list[tuple[int, bytes, str]], start: int, size: int
) -> tuple[bytes, bool]:
    """lap315's collector: adjacency judged by the *byte column* length."""
    cursor = start
    collected = b""
    for address, raw, _instruction in rows:
        if address < start:
            continue
        if address != cursor:
            return collected[:size], False
        collected += raw
        cursor = address + len(raw)
        if len(collected) >= size:
            return collected[:size], True
    return collected[:size], False


def main() -> int:
    image = EXE.read_bytes()
    exe_sha = hashlib.sha256(image).hexdigest()
    image_base, sections = parse_sections(image)

    listing = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    rows, continuations = parse_listing(listing)
    window = [row for row in rows if MAP_ENTRY <= row[0] < MAP_END]
    lengths = boundary_lengths(window, MAP_END)
    audit = truncation_audit(window, lengths, image, image_base, sections)

    window_continuations = [address for address, _raw in continuations if MAP_ENTRY <= address < MAP_END]
    row_addresses = {address for address, _raw, _instruction in window}
    # A continuation line must never be mistaken for an instruction: it carries an
    # address that lies *inside* a folded instruction, so a parser that accepted it
    # would invent a row.  Derive that, do not assert it.
    interior_of_folded = {
        address + offset
        for address, _raw, _instruction in window
        for offset in range(1, lengths[address])
    }
    phantom_rows = sorted(address for address in window_continuations if address in row_addresses)
    continuations_are_interior = all(address in interior_of_folded for address in window_continuations)

    reset_rows = {}
    for address in RESET_WRITERS:
        length = lengths.get(address)
        column = dict((row[0], row[1]) for row in window).get(address, b"")
        full = pe_bytes(image, image_base, sections, address, length) if length else None
        reset_rows[f"0x{address:x}"] = {
            "boundary_length": length,
            "byte_column_length": len(column),
            "image_bytes": full.hex() if full else None,
            "matches_claim": bool(full) and full.hex() == CLAIMED_RESET_BYTES[address],
            "column_is_truncated_without_signal": bool(full) and len(column) < length,
        }

    gate_column = dict((row[0], row[1]) for row in window).get(GATE, b"")
    gate_image = pe_bytes(image, image_base, sections, GATE, lengths.get(GATE, 0))
    taken_target = GATE + 2 + int.from_bytes(gate_column[1:2], "little", signed=True) if len(gate_column) >= 2 else None
    failure_image = pe_bytes(image, image_base, sections, FAILURE_SEED, len(CLAIMED_FAILURE_ARM_BYTES) // 2)
    failure_column, failure_contiguous = collect_contiguous_by_column(
        window, FAILURE_SEED, len(CLAIMED_FAILURE_ARM_BYTES) // 2
    )
    failure_arm_touches_folded = any(
        FAILURE_SEED <= int(address, 16) < SUCCESS_JOIN for address in audit["folded_instructions"]
    )

    report = {
        "lap": 318,
        "role": "middle review of the lap317 Astra F1 scope document",
        "scope": "F1 premise, reset-store bytes, boundary source, residual fail-open",
        "execution": False,
        "exe_sha256": exe_sha,
        "exe_sha_matches": exe_sha == EXPECTED_EXE_SHA,
        "image_base": f"0x{image_base:x}",
        "sections": [
            {"name": name, "va": f"0x{image_base + va:x}", "raw": f"0x{raw:x}", "raw_size": rsz}
            for name, va, _vsz, raw, rsz in sections
        ],
        "window": {
            "entry": f"0x{MAP_ENTRY:x}",
            "end": f"0x{MAP_END:x}",
            "instruction_count": len(window),
            "instruction_count_matches_claim": len(window) == CLAIMED_WINDOW_INSTRUCTIONS,
            "byte_continuation_lines_in_window": len(window_continuations),
            "phantom_instruction_rows": [f"0x{address:x}" for address in phantom_rows],
            "continuation_lines_are_interior_to_a_folded_instruction": continuations_are_interior,
        },
        "f1_premise": {
            **audit,
            "folded_count_matches_claim": audit["folded_instruction_count"] == CLAIMED_FOLDED_IN_WINDOW,
            "reset_writers_are_folded": all(
                f"0x{address:x}" in audit["folded_instructions"] for address in RESET_WRITERS
            ),
        },
        "reset_writers": reset_rows,
        "gate": {
            "bytes": gate_column.hex(),
            "matches_claim": gate_column.hex() == CLAIMED_GATE_BYTES,
            "image_bytes": gate_image.hex() if gate_image else None,
            "taken_target": f"0x{taken_target:x}" if taken_target else None,
            "taken_target_is_success_join": taken_target == SUCCESS_JOIN,
        },
        "failure_arm": {
            "image_bytes": failure_image.hex() if failure_image else None,
            "column_bytes": failure_column.hex(),
            "column_is_contiguous": failure_contiguous,
            "matches_claim": failure_image is not None and failure_image.hex() == CLAIMED_FAILURE_ARM_BYTES,
            "sources_agree": failure_image is not None and failure_image.hex() == failure_column.hex(),
            "touches_a_folded_instruction": failure_arm_touches_folded,
        },
        "success_ret_byte": (pe_bytes(image, image_base, sections, SUCCESS_RET, 1) or b"").hex(),
        "residual_fail_open": {
            "direct_byte_column_lookup_is_silently_truncated": any(
                row["column_is_truncated_without_signal"] for row in reset_rows.values()
            ),
            "note": "a per-instruction length invariant (byte column length == address delta) "
            "catches every folded row; contiguity alone only catches a multi-instruction walk",
        },
    }

    checks = [
        report["exe_sha_matches"],
        report["window"]["instruction_count_matches_claim"],
        report["f1_premise"]["folded_count_matches_claim"],
        report["f1_premise"]["byte_column_is_prefix_of_image"],
        report["f1_premise"]["reset_writers_are_folded"],
        not report["window"]["phantom_instruction_rows"],
        report["window"]["continuation_lines_are_interior_to_a_folded_instruction"],
        all(row["matches_claim"] for row in reset_rows.values()),
        report["gate"]["matches_claim"],
        report["gate"]["taken_target_is_success_join"],
        report["failure_arm"]["matches_claim"],
        report["failure_arm"]["sources_agree"],
        report["failure_arm"]["column_is_contiguous"],
        not report["failure_arm"]["touches_a_folded_instruction"],
    ]
    report["all_checks_pass"] = all(checks)
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
