#!/usr/bin/env python3
"""Read-only, SHA-pinned xref inventory for FUN_004AE550 ("command packer").

Purpose: verify or falsify the standing G5 hypothesis that FUN_004AE550 is
called by a UI/right-click order-issuing handler to broadcast a command to
the whole unit selection. This module only reports direct ``call`` sites
resolved from decoded Capstone immediates (same evidence policy as
``tools/g2_unit_pool_xrefs.py``) plus the five preceding push immediates at
each site, since every observed call site pushes exactly 5 dwords
(``add esp, 0x14`` after the call) in cdecl style.

It does not prove indirect/register calls do not exist; those are out of
scope for a decoded-immediate xref scan and are reported as a stated gap.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

import capstone
import pefile


ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
IMAGE_BASE = 0x00400000
PACKER_ADDRESS = 0x004AE550

# Known order-issuing / dispatch functions from prior G5/G2 laps. If any of
# these ever gains a direct-call xref to PACKER_ADDRESS, that would support
# (not falsify) the "selection broadcast" hypothesis.
KNOWN_ORDER_FUNCTIONS = {
    "op8_issuer_FUN_00415480": 0x00415480,
    "op8_issuer_alt_FUN_00415880": 0x00415880,
    "group_assign_FUN_00445D30": 0x00445D30,
    "order_consumer_FUN_0040F7D0": 0x0040F7D0,
}


@dataclass
class CallSite:
    address: int
    pushes: list[int] = field(default_factory=list)
    containing_window_start: int = 0


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


def inventory(executable: Path) -> dict[str, Any]:
    executable = executable.expanduser().resolve(strict=True)
    digest = _sha256(executable)
    if digest != ORIGINAL_SHA256:
        raise ValueError(f"original SHA-256 mismatch: {digest}")

    pe = pefile.PE(str(executable), fast_load=True)
    try:
        image_base = int(pe.OPTIONAL_HEADER.ImageBase)
        if image_base != IMAGE_BASE:
            raise ValueError(f"unexpected image base: 0x{image_base:x}")
        text_start, text = _section_bytes(pe)
        decoder = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        decoder.detail = True
        decoder.skipdata = True
        insns = list(decoder.disasm(text, text_start))
        by_index = {insn.address: idx for idx, insn in enumerate(insns)}

        direct_calls: list[int] = []
        for insn in insns:
            if insn.mnemonic != "call":
                continue
            for operand in insn.operands:
                if operand.type == capstone.x86.X86_OP_IMM and (int(operand.imm) & 0xFFFFFFFF) == PACKER_ADDRESS:
                    direct_calls.append(insn.address)

        call_sites: list[dict[str, Any]] = []
        for call_addr in direct_calls:
            idx = by_index[call_addr]
            pushes: list[dict[str, str]] = []
            scan_idx = idx - 1
            count = 0
            while scan_idx >= 0 and count < 5:
                prior = insns[scan_idx]
                if prior.mnemonic == "push":
                    for op in prior.operands:
                        if op.type == capstone.x86.X86_OP_IMM:
                            pushes.append({"address": f"0x{prior.address:08x}", "kind": "imm", "value": f"0x{int(op.imm) & 0xFFFFFFFF:08x}"})
                        elif op.type == capstone.x86.X86_OP_REG:
                            pushes.append({"address": f"0x{prior.address:08x}", "kind": "reg", "value": prior.op_str})
                    count += 1
                elif prior.mnemonic in ("call", "ret", "jmp"):
                    break
                scan_idx -= 1
            call_sites.append({
                "call_address": f"0x{call_addr:08x}",
                "preceding_pushes_newest_first": pushes,
                "push_count_found": len(pushes),
            })

        known_function_hits = {
            name: [f"0x{a:08x}" for a in direct_calls if addr <= a < addr + 0x2000]
            for name, addr in KNOWN_ORDER_FUNCTIONS.items()
            for addr in [addr]
        }

        return {
            "status": "PASS",
            "coverage": "text_section_direct_calls_only",
            "source": {
                "path": str(executable),
                "sha256": digest,
                "text_start": f"0x{text_start:08x}",
                "text_bytes": len(text),
                "decoded_instructions": len(insns),
            },
            "packer_address": f"0x{PACKER_ADDRESS:08x}",
            "call_site_count": len(direct_calls),
            "call_sites": call_sites,
            "known_order_function_direct_calls": known_function_hits,
            "evidence_policy": {
                "raw_pattern_scan": False,
                "accepted_xref_evidence": "decoded call-immediate operand only",
                "indirect_or_register_calls": "not scanned; stated gap, not proven absent",
            },
        }
    finally:
        pe.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = inventory(args.exe)
    encoded = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
