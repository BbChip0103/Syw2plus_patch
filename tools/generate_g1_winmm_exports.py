#!/usr/bin/env python3
"""Generate the app-local G1 WINMM export table and x86 forwarding stubs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pefile


OVERRIDES = {"mciSendCommandA", "timeBeginPeriod", "timeEndPeriod", "timeGetTime"}


def generate(source: Path, out_dir: Path) -> tuple[int, int]:
    pe = pefile.PE(str(source), fast_load=False)
    export = pe.DIRECTORY_ENTRY_EXPORT
    symbols = list(export.symbols)
    by_ordinal = {int(symbol.ordinal): symbol for symbol in symbols}
    names = [(int(symbol.ordinal), symbol.name.decode("ascii"))
             for symbol in symbols if symbol.name]
    names.sort()
    if not OVERRIDES.issubset({name for _, name in names}):
        raise ValueError("source WINMM is missing one or more G1 hook exports")

    definition = ["LIBRARY winmm", "EXPORTS"]
    assembly = [".text", ".extern _g1_winmm_resolve", ".extern _g1_winmm_resolve_ordinal"]
    emitted_ordinals = set()
    for ordinal, name in names:
        symbol = f"_g1_forward_{name}"
        target = f"g1_proxy_{name}" if name in OVERRIDES else f"g1_forward_{name}"
        definition.append(f"    {name}={target} @{ordinal}")
        emitted_ordinals.add(ordinal)
        if name in OVERRIDES:
            continue
        assembly.extend([
            f".globl {symbol}", f"{symbol}:", f"    pushl ${symbol}_name",
            "    call _g1_winmm_resolve", "    addl $4, %esp", "    testl %eax, %eax",
            f"    jz {symbol}_missing", "    jmp *%eax", f"{symbol}_missing:",
            "    xorl %eax, %eax", "    ret", '.section .rdata,"dr"',
            f"{symbol}_name:", f'    .asciz "{name}"', ".text",
        ])

    unnamed = 0
    for ordinal, symbol in sorted(by_ordinal.items()):
        if symbol.name or ordinal in emitted_ordinals:
            continue
        target = f"g1_forward_ordinal_{ordinal}"
        definition.append(f"    {target} @{ordinal} NONAME")
        assembly.extend([
            f".globl _{target}", f"_{target}:", f"    pushl ${ordinal}",
            "    call _g1_winmm_resolve_ordinal", "    addl $4, %esp", "    testl %eax, %eax",
            f"    jz {target}_missing", "    jmp *%eax", f"{target}_missing:",
            "    xorl %eax, %eax", "    ret",
        ])
        unnamed += 1

    if len(by_ordinal) != int(export.struct.NumberOfFunctions):
        raise ValueError("source WINMM has sparse ordinal slots; generator needs explicit holes")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "g1_winmm_proxy.def").write_text("\n".join(definition) + "\n", encoding="ascii")
    (out_dir / "g1_winmm_forwarders.S").write_text("\n".join(assembly) + "\n", encoding="ascii")
    return len(names), unnamed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--system-winmm", required=True, type=Path)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parent / "inmm_stub")
    args = parser.parse_args()
    names, unnamed = generate(args.system_winmm, args.out_dir)
    print(f"generated {names} named exports and {unnamed} ordinal-only exports")


if __name__ == "__main__":
    main()
