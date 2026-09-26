#!/usr/bin/env python3
"""Read-only, SHA-pinned xref inventory for the original unit pool.

Only instructions decoded by Capstone are reported.  In particular, this
module does not treat an arbitrary byte sequence containing an address as an
xref: direct calls are resolved from decoded ``call`` immediates and direct
region references are resolved from absolute decoded memory operands.  Other
in-range immediates and base/index displacements are retained as unresolved
relocation candidates.  The result is static machine provenance, not proof
that extending the pool is safe to activate.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import capstone
import pefile


ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
IMAGE_BASE = 0x00400000
UNIT_POOL_BASE = 0x0066B790
UNIT_STRIDE = 0x758
UNIT_SLOT_COUNT = 1200
UNIT_POOL_END = UNIT_POOL_BASE + UNIT_STRIDE * UNIT_SLOT_COUNT
UNIT_EXISTS_BASE = 0x008990C8
UNIT_EXISTS_END = 0x00899A28
# These are the two immediate boundaries used by FUN_00442FA0's auxiliary
# scan.  Their semantic element type is intentionally left unresolved.
ALLOCATOR_SIDECAR_START = 0x00899A2A
ALLOCATOR_SIDECAR_END = 0x0089A388
# The age array begins at the existence-end boundary. The allocator's
# slot-1 scan starts at ALLOCATOR_SIDECAR_START, which remains an endpoint
# below but is not the age-array base.
UNIT_AGE_BASE = 0x00899A28
UNIT_AGE_END = 0x0089A388
# FUN_0048BC00's active-slot list contains 1200 two-byte entries.  It is
# kept as a separate region because it is not the allocator sidecar.
ACTIVE_SLOT_LIST_BASE = 0x00974FA8
ACTIVE_SLOT_LIST_END = 0x00975908
# FUN_0048BC00 maintains two additional dword lists. Their count words live
# immediately at each half-open end address.
CATEGORY_SLOT_LIST_A_BASE = 0x0089B008
CATEGORY_SLOT_LIST_A_END = 0x0089C2C8
CATEGORY_SLOT_LIST_B_BASE = 0x0089C2CA
CATEGORY_SLOT_LIST_B_END = 0x0089D58A

FUNCTIONS = {
    "allocator": 0x00442FA0,
    "destruction": 0x00442FE0,
    "spawn": 0x00443190,
    "save_roster": 0x0040F4B0,
    "load_roster": 0x0040F4F0,
}
ENDPOINTS = {
    "unit_pool_base": UNIT_POOL_BASE,
    "unit_pool_bulk_start": UNIT_POOL_END,
    "unit_existence_base": UNIT_EXISTS_BASE,
    "unit_existence_end": UNIT_EXISTS_END,
    "allocator_sidecar_start": ALLOCATOR_SIDECAR_START,
    "allocator_sidecar_end": ALLOCATOR_SIDECAR_END,
}
# Unlike ENDPOINTS, these are half-open ranges. Candidates are emitted for
# decoded immediate operands and base/index displacements. Direct region
# references require absolute memory operands;
# an address computed from a register cannot be proven to land in one of these
# ranges from the instruction alone.
REGIONS = {
    "unit_pool": (UNIT_POOL_BASE, UNIT_POOL_END),
    "unit_existence": (UNIT_EXISTS_BASE, UNIT_EXISTS_END),
    "unit_age": (UNIT_AGE_BASE, UNIT_AGE_END),
    "active_slot_list": (ACTIVE_SLOT_LIST_BASE, ACTIVE_SLOT_LIST_END),
    "category_slot_list_a": (CATEGORY_SLOT_LIST_A_BASE, CATEGORY_SLOT_LIST_A_END),
    "category_slot_list_b": (CATEGORY_SLOT_LIST_B_BASE, CATEGORY_SLOT_LIST_B_END),
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


def _insn_record(insn: capstone.CsInsn, *, kind: str, name: str, value: int) -> dict[str, Any]:
    return {
        "instruction": f"0x{insn.address:08x}",
        "bytes": insn.bytes.hex(" "),
        "mnemonic": insn.mnemonic,
        "operands": insn.op_str,
        "kind": kind,
        "name": name,
        "value": f"0x{value:08x}",
        "evidence": "decoded_capstone_operand",
    }


def inventory(executable: Path) -> dict[str, Any]:
    """Return a static inventory without modifying the executable or filesystem."""

    executable = executable.expanduser().resolve(strict=True)
    digest = _sha256(executable)
    if digest != ORIGINAL_SHA256:
        raise ValueError(f"original SHA-256 mismatch: {digest}")

    pe = pefile.PE(str(executable), fast_load=True)
    try:
        if int(pe.PE_TYPE) != int(pefile.OPTIONAL_HEADER_MAGIC_PE):
            raise ValueError(f"expected PE32, got PE type {pe.PE_TYPE!r}")
        image_base = int(pe.OPTIONAL_HEADER.ImageBase)
        if image_base != IMAGE_BASE:
            raise ValueError(f"unexpected image base: 0x{image_base:x}")
        text_start, text = _section_bytes(pe)
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        # The PE .text raw range contains alignment/data gaps between code
        # regions.  Continue past undecodable bytes, but never inspect the
        # synthetic ``.byte`` records as instructions.
        decoder.skipdata = True
        function_by_address = {address: name for name, address in FUNCTIONS.items()}
        endpoint_by_address = {address: name for name, address in ENDPOINTS.items()}
        direct_calls: list[dict[str, Any]] = []
        endpoint_refs: list[dict[str, Any]] = []
        region_refs: dict[str, list[dict[str, Any]]] = {
            name: [] for name in REGIONS
        }
        immediate_candidates: dict[str, list[dict[str, Any]]] = {
            name: [] for name in REGIONS
        }
        base_index_candidates: dict[str, list[dict[str, Any]]] = {
            name: [] for name in REGIONS
        }
        decoded = 0
        for insn in decoder.disasm(text, text_start):
            if insn.mnemonic == ".byte":
                continue
            decoded += 1
            for operand_index, operand in enumerate(insn.operands):
                if operand.type == capstone.x86.X86_OP_IMM:
                    value = int(operand.imm) & 0xFFFFFFFF
                    target_name = function_by_address.get(value)
                    if insn.mnemonic == "call" and target_name is not None:
                        direct_calls.append(_insn_record(
                            insn, kind="direct_call_target", name=target_name, value=value,
                        ))
                    endpoint_name = endpoint_by_address.get(value)
                    if endpoint_name is not None:
                        endpoint_refs.append(_insn_record(
                            insn, kind="immediate_operand", name=endpoint_name, value=value,
                        ))
                    for region_name, (start, end) in REGIONS.items():
                        if start <= value < end:
                            record = _insn_record(
                                insn,
                                kind="immediate_operand",
                                name=region_name,
                                value=value,
                            )
                            record["operand_type"] = "immediate"
                            record["operand_index"] = operand_index
                            immediate_candidates[region_name].append(record)
                elif operand.type == capstone.x86.X86_OP_MEM:
                    memory = operand.mem
                    value = int(memory.disp) & 0xFFFFFFFF
                    mode = "absolute" if not memory.base and not memory.index else "base_plus_disp"
                    endpoint_name = endpoint_by_address.get(value)
                    if endpoint_name is not None:
                        record = _insn_record(
                            insn, kind=f"memory_{mode}", name=endpoint_name, value=value,
                        )
                        record["effective_address"] = (
                            f"0x{value:08x}" if mode == "absolute" else "base/index dependent"
                        )
                        endpoint_refs.append(record)
                    # Do not classify [register + displacement] as a region
                    # reference: its effective address depends on runtime
                    # state. Endpoint output above intentionally retains its
                    # historical behavior for compatibility.
                    if mode == "absolute":
                        for region_name, (start, end) in REGIONS.items():
                            if start <= value < end:
                                region_record = _insn_record(
                                    insn,
                                    kind="memory_absolute",
                                    name=region_name,
                                    value=value,
                                )
                                region_record["effective_address"] = f"0x{value:08x}"
                                region_record["operand_type"] = "absolute_memory"
                                region_record["operand_index"] = operand_index
                                region_refs[region_name].append(region_record)
                    else:
                        # The displacement is a useful relocation candidate,
                        # but the effective address depends on runtime
                        # register state and is therefore not a proven region
                        # reference.
                        for region_name, (start, end) in REGIONS.items():
                            if start <= value < end:
                                candidate = _insn_record(
                                    insn,
                                    kind="memory_base_index_displacement_candidate",
                                    name=region_name,
                                    value=value,
                                )
                                candidate["effective_address"] = (
                                    "runtime effective address unresolved"
                                )
                                candidate["addressing"] = "base/index-dependent"
                                candidate["operand_type"] = "base_index_memory"
                                candidate["operand_index"] = operand_index
                                base_index_candidates[region_name].append(candidate)
        calls_by_name: dict[str, list[dict[str, Any]]] = {name: [] for name in FUNCTIONS}
        for call in direct_calls:
            calls_by_name[call["name"]].append(call)
        refs_by_name: dict[str, list[dict[str, Any]]] = {name: [] for name in ENDPOINTS}
        for ref in endpoint_refs:
            refs_by_name[ref["name"]].append(ref)
        return {
            "status": "PASS",
            "coverage": "INCOMPLETE",
            "activation": {
                "status": "NO-GO",
                "reason": "static xrefs do not prove safe slot-1200 activation or save/network compatibility",
            },
            "source": {
                "path": str(executable),
                "sha256": digest,
                "pe32": True,
                "image_base": f"0x{image_base:08x}",
                "text_start": f"0x{text_start:08x}",
                "text_bytes": len(text),
                "decoded_instructions": decoded,
            },
            "pool_geometry": {
                "base": f"0x{UNIT_POOL_BASE:08x}",
                "stride": UNIT_STRIDE,
                "slots": UNIT_SLOT_COUNT,
                "end_bulk_start": f"0x{UNIT_POOL_END:08x}",
                "existence_base": f"0x{UNIT_EXISTS_BASE:08x}",
                "existence_end": f"0x{UNIT_EXISTS_END:08x}",
                "allocator_sidecar_start": f"0x{ALLOCATOR_SIDECAR_START:08x}",
                "allocator_sidecar_end": f"0x{ALLOCATOR_SIDECAR_END:08x}",
                "unit_age_base": f"0x{UNIT_AGE_BASE:08x}",
                "unit_age_end": f"0x{UNIT_AGE_END:08x}",
                "active_slot_list_base": f"0x{ACTIVE_SLOT_LIST_BASE:08x}",
                "active_slot_list_end": f"0x{ACTIVE_SLOT_LIST_END:08x}",
                "category_slot_list_a_base": f"0x{CATEGORY_SLOT_LIST_A_BASE:08x}",
                "category_slot_list_a_end": f"0x{CATEGORY_SLOT_LIST_A_END:08x}",
                "category_slot_list_b_base": f"0x{CATEGORY_SLOT_LIST_B_BASE:08x}",
                "category_slot_list_b_end": f"0x{CATEGORY_SLOT_LIST_B_END:08x}",
                "geometry_check": UNIT_POOL_END == 0x00892410
                and UNIT_EXISTS_END - UNIT_EXISTS_BASE == UNIT_SLOT_COUNT * 2
                and UNIT_AGE_END - UNIT_AGE_BASE == UNIT_SLOT_COUNT * 2
                and ACTIVE_SLOT_LIST_END - ACTIVE_SLOT_LIST_BASE == UNIT_SLOT_COUNT * 2
                and CATEGORY_SLOT_LIST_A_END - CATEGORY_SLOT_LIST_A_BASE == UNIT_SLOT_COUNT * 4
                and CATEGORY_SLOT_LIST_B_END - CATEGORY_SLOT_LIST_B_BASE == UNIT_SLOT_COUNT * 4,
            },
            "functions": {
                name: {
                    "address": f"0x{address:08x}",
                    "direct_call_xrefs": calls_by_name[name],
                }
                for name, address in FUNCTIONS.items()
            },
            "endpoints": {
                name: {
                    "address": f"0x{address:08x}",
                    "decoded_xrefs": refs_by_name[name],
                }
                for name, address in ENDPOINTS.items()
            },
            "regions": {
                name: {
                    "start": f"0x{start:08x}",
                    "end": f"0x{end:08x}",
                    "decoded_xrefs": region_refs[name],
                    "immediate_operand_candidates": immediate_candidates[name],
                    "base_index_displacement_candidates": base_index_candidates[name],
                }
                for name, (start, end) in REGIONS.items()
            },
            "evidence_policy": {
                "raw_pattern_scan": False,
                "accepted_xref_evidence": "decoded instruction operand only",
                "unbounded_byte_patterns": "not counted as xrefs",
                "region_reference_scope": (
                    "decoded absolute memory operands are direct region references; "
                    "immediates and base/index-dependent memory operands are candidates only"
                ),
                "immediate_operand_scope": "in-range relocation candidates; semantic role unresolved",
                "base_index_displacement_scope": (
                    "in-range relocation candidates; runtime effective address unresolved"
                ),
                "overlapping_endpoint_semantics": (
                    "unit_age starts at unit_existence_end (0x00899a28); "
                    "allocator_sidecar_start (0x00899a2a) remains a historical endpoint"
                ),
            },
            "xref_counts": {
                "direct_call_targets": dict(Counter(call["name"] for call in direct_calls)),
                "decoded_endpoint_operands": dict(Counter(ref["name"] for ref in endpoint_refs)),
                "absolute_memory_operands": {
                    name: len(refs) for name, refs in region_refs.items()
                },
                "immediate_operand_candidates": {
                    name: len(refs) for name, refs in immediate_candidates.items()
                },
                "base_index_displacement_candidates": {
                    name: len(refs) for name, refs in base_index_candidates.items()
                },
            },
        }
    finally:
        pe.close()


def _summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": report["status"],
        "coverage": report["coverage"],
        "activation": report["activation"],
        "source": report["source"],
        "pool_geometry": report["pool_geometry"],
        "xref_counts": report["xref_counts"],
        "functions": {
            name: {
                "address": details["address"],
                "direct_call_xref_count": len(details["direct_call_xrefs"]),
            }
            for name, details in report["functions"].items()
        },
        "endpoints": {
            name: {
                "address": details["address"],
                "decoded_xref_count": len(details["decoded_xrefs"]),
            }
            for name, details in report["endpoints"].items()
        },
        "regions": {
            name: {
                "start": details["start"],
                "end": details["end"],
                "decoded_xref_count": len(details["decoded_xrefs"]),
                "immediate_operand_candidate_count": len(
                    details["immediate_operand_candidates"]
                ),
                "base_index_displacement_candidate_count": len(
                    details["base_index_displacement_candidates"]
                ),
            }
            for name, details in report["regions"].items()
        },
        "evidence_policy": report["evidence_policy"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    report = inventory(args.exe)
    payload = _summary(report) if args.summary else report
    encoded = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
