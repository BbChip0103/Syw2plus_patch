#!/usr/bin/env python3
"""lap324 middle — independent evidence for the lap323 execution-path compatibility ruling.

Read-only.  No game/Wine/Xvfb/Stage B/click/PNG, no writes outside stdout.
Every fact is re-derived here (AST for the harness, PE bytes + one objdump listing
for the binary) instead of imported from an earlier lap's probe, so a disagreement
with a prior lap is a real disagreement.

Question this probe serves (lap323 handoff table): can the §14.7 observation
("value of ds:0xE5BF1C/0xE5BF20 at the moment 0x4D6312 reads them") be reached and
measured under the standing prohibitions?  It therefore measures three things:
  (1) what the harness can start, wait for, and read;
  (2) whether any exact-site instrument (breakpoint/ptrace/write) exists at all;
  (3) whether the computed origin is persisted in a global that a poll could read,
      and how many writers that global has.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import struct
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus/syw2plus_original.exe"
RUNTIME_ENV = REPO / "tools/runtime_env.py"
RUNTIME_DRIVER = REPO / "patches/population/runtime_driver.py"
DIRECTION = REPO / "docs/work/active/G1_OBSERVATION_DIRECTION_LAP323.md"
CONTRACT = REPO / "docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md"

ORIGIN_X_GLOBAL = 0x01088B5C
ORIGIN_Y_GLOBAL = 0x01088B5E
SCREEN_W_GLOBAL = 0x00E5BF1C
SCREEN_H_GLOBAL = 0x00E5BF20
DIALOG_FUNC = 0x004D60B0
CENTRE_SITE = 0x004D6312

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)


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


def text_span(image_base, sections):
    for name, va, vsize, raw_ptr, raw_size in sections:
        if name == ".text":
            return image_base + va, raw_ptr, min(vsize, raw_size)
    raise ValueError(".text not found")


def disassemble_text() -> dict[int, tuple[bytes, str]]:
    listing = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True, capture_output=True, text=True,
    ).stdout
    return {
        int(address, 16): (bytes.fromhex(raw), instruction)
        for address, raw, instruction in INSN_RE.findall(listing)
    }


def absolute_operand_sites(image, text_base, text_raw, text_size, value) -> list[int]:
    """Every .text position whose 4 bytes are the little-endian absolute address."""
    needle = struct.pack("<I", value)
    body = image[text_raw : text_raw + text_size]
    sites, start = [], 0
    while True:
        found = body.find(needle, start)
        if found < 0:
            return sites
        sites.append(text_base + found)
        start = found + 1


def classify(rows: dict[int, tuple[bytes, str]], operand_va: int, window: int = 8):
    """Attribute an operand position to the instruction that contains it."""
    for back in range(1, window + 1):
        head = operand_va - back
        if head in rows:
            raw, text = rows[head]
            if back + 4 <= len(raw):
                return {"instruction_address": f"0x{head:X}", "bytes": raw.hex(),
                        "text": text, "operand_offset": back}
    return {"instruction_address": None, "bytes": None, "text": None, "operand_offset": None}


def direct_callers(rows: dict[int, tuple[bytes, str]], target: int) -> list[str]:
    out = []
    for address, (raw, text) in rows.items():
        if raw[:1] == b"\xe8" and len(raw) >= 5:
            (rel,) = struct.unpack_from("<i", raw, 1)
            if (address + 5 + rel) & 0xFFFFFFFF == target:
                out.append(f"0x{address:X}")
        elif text.startswith("call") and f"0x{target:x}" in text:
            out.append(f"0x{address:X}")
    return sorted(set(out))


def harness_facts() -> dict:
    source = RUNTIME_ENV.read_text(encoding="utf-8")
    tree = ast.parse(source)
    subcommands, popen_argv, timeout_caps = [], [], []
    ps_compared: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr == "add_parser" and node.args:
                if isinstance(node.args[0], ast.Constant):
                    subcommands.append(node.args[0].value)
            if node.func.attr == "Popen" and node.args and isinstance(node.args[0], ast.List):
                argv = [e.value for e in node.args[0].elts if isinstance(e, ast.Constant)]
                if argv:
                    popen_argv.append(argv)
        if isinstance(node, ast.Compare):
            left = ast.unparse(node.left)
            # form-agnostic: any comparison whose left side reads a "ps" field
            if re.search(r"""\bget\(["']ps["']\)|\[["']ps["']\]""", left):
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and isinstance(comparator.value, int):
                        ps_compared.add(comparator.value)
                    elif isinstance(comparator, (ast.Set, ast.List, ast.Tuple)):
                        for element in comparator.elts:
                            if isinstance(element, ast.Constant) and isinstance(element.value, int):
                                ps_compared.add(element.value)
            if "timeout" in left:
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and comparator.value == 90:
                        timeout_caps.append(left)
    names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    driver_source = RUNTIME_DRIVER.read_text(encoding="utf-8")
    instruments = {
        token: len(re.findall(re.escape(token), source + driver_source))
        for token in ("process_vm_readv", "process_vm_writev", "ptrace", "PTRACE",
                      "winedbg", "gdb", "int3", "0xcc", "0xCC")
    }
    bare_35 = len(re.findall(r"(?<![\w.])35(?![\w.])", source))
    return {
        "runtime_env_sha256": sha256_file(RUNTIME_ENV),
        "runtime_driver_sha256": sha256_file(RUNTIME_DRIVER),
        "subcommands": sorted(subcommands),
        "arbitrary_address_read_subcommand": False,
        "popen_argv_literals": popen_argv,
        "ps_values_compared": sorted(ps_compared),
        "ps35_compared": 35 in ps_compared,
        "bare_35_occurrences": bare_35,
        "save_token_occurrences": len(re.findall(r"(?<![\w.])save(?![\w.])", source)),
        "timeout_cap_comparisons": sorted(set(timeout_caps)),
        "instrument_tokens": instruments,
        "isolation_helpers_present": sorted(
            name for name in (
                "validate_original_source", "_assert_private_copy", "_new_run", "_xvfb",
                "_display_busy", "_owned_runtime_process_pids", "_request_owned_game_close",
                "_prefix_pids", "_existing_state", "prepare", "check_runtime",
            ) if name in names
        ),
        "origin_globals_referenced": [
            hex(value) for value, token in (
                (ORIGIN_X_GLOBAL, "1088B5C"), (ORIGIN_Y_GLOBAL, "1088B5E"),
                (SCREEN_W_GLOBAL, "E5BF1C"), (SCREEN_H_GLOBAL, "E5BF20"),
            ) if re.search(token, source, re.IGNORECASE)
        ],
    }


def binary_facts() -> dict:
    image = EXE.read_bytes()
    image_base, sections = parse_sections(image)
    text_base, text_raw, text_size = text_span(image_base, sections)
    rows = disassemble_text()
    out: dict[str, object] = {
        "exe_sha256": sha256_file(EXE),
        "image_base": hex(image_base),
        "text_span": [hex(text_base), hex(text_base + text_size)],
        "instruction_rows": len(rows),
    }
    for label, value in (("origin_x_0x1088B5C", ORIGIN_X_GLOBAL),
                         ("origin_y_0x1088B5E", ORIGIN_Y_GLOBAL)):
        sites = absolute_operand_sites(image, text_base, text_raw, text_size, value)
        classified = [classify(rows, site) | {"operand_at": f"0x{site:X}"} for site in sites]
        writers = [item for item in classified
                   if item["text"] and re.match(r"^mov\s+(WORD|DWORD|BYTE) PTR ds:", item["text"])]
        out[label] = {
            "operand_occurrences": len(sites),
            "sites": classified,
            "direct_store_sites": [item["instruction_address"] for item in writers],
        }
    centre = {}
    for address in sorted(a for a in rows if CENTRE_SITE <= a <= CENTRE_SITE + 0x40):
        raw, text = rows[address]
        centre[f"0x{address:X}"] = {"bytes": raw.hex(), "text": text}
    out["centre_site_window"] = centre
    out["dialog_function_direct_callers"] = direct_callers(rows, DIALOG_FUNC)
    out["screen_global_direct_stores"] = sorted(
        f"0x{address:X}" for address, (_raw, text) in rows.items()
        if re.match(r"^mov\s+DWORD PTR ds:0x(e5bf1c|e5bf20),", text)
    )
    return out


def main() -> int:
    harness = harness_facts()
    binary = binary_facts()
    failures: list[str] = []

    if binary["exe_sha256"] != "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac":
        failures.append("original exe sha changed")
    # Premises this ruling rests on.  If a later lap makes any of them false, this
    # probe must fail loudly instead of silently agreeing with a stale document.
    if harness["ps35_compared"] or harness["bare_35_occurrences"]:
        failures.append("harness now references PS35; the 'no load path' premise changed")
    if harness["instrument_tokens"]["process_vm_writev"] or harness["instrument_tokens"]["ptrace"]:
        failures.append("a write/ptrace instrument appeared; exact-site premise changed")
    if "g1-load-observation" in harness["subcommands"]:
        failures.append("an unreviewed load-observation subcommand exists")

    report = {
        "lap": 324,
        "role": "middle (Claude Code claude-opus-5/high) — lap323 execution-path compatibility ruling",
        "scope": "read-only static evidence; game/Wine/Xvfb/StageB/click/PNG/runtime budget = 0",
        "harness": harness,
        "binary": binary,
        "direction_sha256": sha256_file(DIRECTION) if DIRECTION.exists() else None,
        "contract_sha256": sha256_file(CONTRACT) if CONTRACT.exists() else None,
        "notes": [
            "Reads are process_vm_readv polls from outside; no breakpoint/ptrace/write exists.",
            "PS values are what the harness can wait for; there is no save/load state among them.",
            "Origin-global writer count decides whether a poll could substitute for exact-site.",
        ],
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }
    json.dump(report, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
