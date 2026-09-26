#!/usr/bin/env python3
"""Read-only, SHA-pinned feasibility inventory for the 16-player boundary.

This is static decoded-operand evidence only. It does not write a binary or
run the game. Immediate value ``8`` is deliberately reported as common-number
noise, not as proof of a player loop. The result is a quick-feasibility
boundary check, not a declaration that an invasive extension is impossible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from importlib import import_module
from pathlib import Path
from typing import Any

try:
    _xref = import_module("tools.g2_unit_pool_xrefs")
except ModuleNotFoundError:  # Running this file directly from the tools directory.
    _xref = import_module("g2_unit_pool_xrefs")

import capstone
import pefile


ORIGINAL_SHA256 = _xref.ORIGINAL_SHA256
IMAGE_BASE = 0x00400000
PLAYER_STRUCT_BASE = 0x00956770
PLAYER_STRUCT_STRIDE = 0x3ABC
PLAYER_COUNT_ORIGINAL = 8
PLAYER_COUNT_TARGET = 16
PLAYER_STRUCT_ORIGINAL_END = PLAYER_STRUCT_BASE + PLAYER_STRUCT_STRIDE * PLAYER_COUNT_ORIGINAL
PLAYER_STRUCT_TARGET_END = PLAYER_STRUCT_BASE + PLAYER_STRUCT_STRIDE * PLAYER_COUNT_TARGET
BULK_SAVE_BASE = 0x00892410
BULK_SAVE_END = 0x00975D8C
BULK_TARGET_EXCESS = PLAYER_STRUCT_TARGET_END - BULK_SAVE_END

MASK_FUNCTION_START = 0x0043EBC0
MASK_FUNCTION_END = 0x0043EBE1
MASK_INSTRUCTIONS = {
    0x0043EBC9: ("88 48 01", "mov", "byte ptr [eax + 1], cl"),
    0x0043EBCC: ("88 48 05", "mov", "byte ptr [eax + 5], cl"),
    0x0043EBC2: ("b2 01", "mov", "dl, 1"),
    0x0043EBD2: ("d2 e2", "shl", "dl, cl"),
    0x0043EBDB: ("88 50 03", "mov", "byte ptr [eax + 3], dl"),
}

BOUNDARY_CATEGORIES = {
    "player_struct_base": PLAYER_STRUCT_BASE,
    "player_struct_stride": PLAYER_STRUCT_STRIDE,
    "player_struct_original_end": PLAYER_STRUCT_ORIGINAL_END,
    "player_struct_target_end": PLAYER_STRUCT_TARGET_END,
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _section_bytes(pe: pefile.PE) -> tuple[int, bytes]:
    sections = [section for section in pe.sections if section.Name.rstrip(b"\0").startswith(b".text")]
    if len(sections) != 1:
        raise ValueError(f"expected one .text section, found {len(sections)}")
    section = sections[0]
    start = int(pe.OPTIONAL_HEADER.ImageBase) + int(section.VirtualAddress)
    end = int(section.PointerToRawData) + int(section.SizeOfRawData)
    return start, bytes(pe.__data__[section.PointerToRawData:end])


def _record(insn: capstone.CsInsn, *, kind: str, value: int, operand_index: int) -> dict[str, Any]:
    return {
        "instruction": f"0x{insn.address:08x}",
        "bytes": insn.bytes.hex(" "),
        "mnemonic": insn.mnemonic,
        "operands": insn.op_str,
        "kind": kind,
        "value": f"0x{value:08x}",
        "operand_index": operand_index,
        "evidence": "decoded_capstone_operand",
        "semantic_status": "UNRESOLVED",
    }


def _mask_record(insn: capstone.CsInsn) -> dict[str, Any]:
    return {
        "instruction": f"0x{insn.address:08x}",
        "bytes": insn.bytes.hex(" "),
        "mnemonic": insn.mnemonic,
        "operands": insn.op_str,
        "evidence": "decoded_capstone_instruction",
    }


def inventory(executable: Path) -> dict[str, Any]:
    """Return static PlayerStruct boundary evidence without filesystem writes."""

    executable = executable.expanduser().resolve(strict=True)
    digest = _sha256(executable)
    if digest != ORIGINAL_SHA256:
        raise ValueError(f"original SHA-256 mismatch: {digest}")
    pe = pefile.PE(str(executable), fast_load=True)
    try:
        if int(pe.PE_TYPE) != int(pefile.OPTIONAL_HEADER_MAGIC_PE):
            raise ValueError(f"expected PE32, got PE type {pe.PE_TYPE!r}")
        if int(pe.OPTIONAL_HEADER.ImageBase) != IMAGE_BASE:
            raise ValueError("unexpected image base")
        text_start, text = _section_bytes(pe)
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        decoder.skipdata = True
        candidates: dict[str, list[dict[str, Any]]] = {
            name: [] for name in BOUNDARY_CATEGORIES
        }
        loop_bound_8: list[dict[str, Any]] = []
        mask_records: dict[int, dict[str, Any]] = {}
        decoded = 0
        for insn in decoder.disasm(text, text_start):
            if insn.mnemonic == ".byte":
                continue
            decoded += 1
            if MASK_FUNCTION_START <= insn.address < MASK_FUNCTION_END:
                mask_records[insn.address] = _mask_record(insn)
            for operand_index, operand in enumerate(insn.operands):
                if operand.type == capstone.x86.X86_OP_IMM:
                    value = int(operand.imm) & 0xFFFFFFFF
                    if value == PLAYER_COUNT_ORIGINAL:
                        loop_bound_8.append(_record(
                            insn, kind="immediate_loop_bound_8_candidate",
                            value=value, operand_index=operand_index,
                        ))
                elif operand.type == capstone.x86.X86_OP_MEM:
                    value = int(operand.mem.disp) & 0xFFFFFFFF
                    if not operand.mem.base and not operand.mem.index:
                        kind = "absolute_memory_operand_candidate"
                    else:
                        kind = "base_index_displacement_candidate"
                    for category, expected in BOUNDARY_CATEGORIES.items():
                        if value == expected:
                            candidates[category].append(_record(
                                insn, kind=kind, value=value,
                                operand_index=operand_index,
                            ))
            # Immediate boundary values are candidates too, but the same
            # numeric value may have a semantic role only at a specific site.
            for operand_index, operand in enumerate(insn.operands):
                if operand.type != capstone.x86.X86_OP_IMM:
                    continue
                value = int(operand.imm) & 0xFFFFFFFF
                for category, expected in BOUNDARY_CATEGORIES.items():
                    if value == expected:
                        candidates[category].append(_record(
                            insn, kind="immediate_operand_candidate", value=value,
                            operand_index=operand_index,
                        ))
        missing = set(MASK_INSTRUCTIONS) - set(mask_records)
        if missing:
            raise ValueError(f"mask evidence instructions missing: {sorted(missing)!r}")
        mask_evidence = [mask_records[address] for address in sorted(MASK_INSTRUCTIONS)]
        for address, record in zip(sorted(MASK_INSTRUCTIONS), mask_evidence, strict=True):
            expected_bytes, expected_mnemonic, expected_operands = MASK_INSTRUCTIONS[address]
            if (record["bytes"], record["mnemonic"], record["operands"]) != (
                expected_bytes, expected_mnemonic, expected_operands
            ):
                raise ValueError(f"unexpected mask instruction at {record['instruction']}")
        return {
            "status": "PASS",
            "coverage": "INCOMPLETE",
            "activation": {
                "status": "NO-GO",
                "reason": (
                    "constant-only 16-player patch cannot preserve byte masks/save semantics; "
                    "invasive extension remains unresolved, not declared impossible"
                ),
            },
            "source": {
                "path": str(executable),
                "sha256": digest,
                "pe32": True,
                "image_base": f"0x{IMAGE_BASE:08x}",
                "text_start": f"0x{text_start:08x}",
                "text_bytes": len(text),
                "decoded_instructions": decoded,
            },
            "player_struct": {
                "base": f"0x{PLAYER_STRUCT_BASE:08x}",
                "stride": f"0x{PLAYER_STRUCT_STRIDE:08x}",
                "original_count": PLAYER_COUNT_ORIGINAL,
                "original_end": f"0x{PLAYER_STRUCT_ORIGINAL_END:08x}",
                "target_count": PLAYER_COUNT_TARGET,
                "target_end": f"0x{PLAYER_STRUCT_TARGET_END:08x}",
                "target_geometry_check": PLAYER_STRUCT_TARGET_END == 0x00991330,
            },
            "bulk_save": {
                "start": f"0x{BULK_SAVE_BASE:08x}",
                "end": f"0x{BULK_SAVE_END:08x}",
                "target_excess_bytes": BULK_TARGET_EXCESS,
                "target_excess_hex": f"0x{BULK_TARGET_EXCESS:08x}",
                "arithmetic_check": BULK_TARGET_EXCESS == 0x1B5A4,
            },
            "boundary_operand_candidates": candidates,
            "immediate_loop_bound_8_candidates": loop_bound_8,
            "candidate_policy": {
                "boundary_operands": "decoded operands only; semantic use unresolved",
                "immediate_loop_bound_8": (
                    "common-number noise; not proof of an 8-player loop or safe bound"
                ),
                "base_index_memory": "effective address depends on runtime registers",
            },
            "mask_evidence": {
                "function": "0x0043ebc0",
                "instructions": mask_evidence,
                "owner_mask": {
                    "offset": 3,
                    "width": "byte",
                    "basis": "decoded mov [eax+3],dl",
                    "implication": "owner indices 8..15 shift outside an 8-bit self mask and become zero",
                },
                "player_index_storage": {
                    "offsets": [1, 5],
                    "width": "byte",
                    "basis": "decoded mov byte ptr [eax+1],cl and [eax+5],cl",
                },
                "opponent_mask": {
                    "offset": 4,
                    "width": "byte",
                    "semantics": "OR of 1<<other.player_num for different-team players",
                    "basis": "existing static field evidence; no new runtime execution",
                },
            },
            "unresolved": {
                "table_relocation": "UNRESOLVED",
                "mask_widening_all_consumers": "UNRESOLVED",
                "lobby_start_positions_win_ai": "UNRESOLVED",
                "save_version": "UNRESOLVED",
                "lan_protocol": "UNRESOLVED",
            },
        }
    finally:
        pe.close()


def summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        key: report[key] for key in (
            "status", "coverage", "activation", "source", "player_struct",
            "bulk_save", "candidate_policy", "mask_evidence", "unresolved",
        )
    } | {
        "boundary_operand_candidate_counts": {
            name: len(records)
            for name, records in report["boundary_operand_candidates"].items()
        },
        "immediate_loop_bound_8_candidate_count": len(
            report["immediate_loop_bound_8_candidates"]
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    report = inventory(args.exe)
    payload = summary(report) if args.summary else report
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
