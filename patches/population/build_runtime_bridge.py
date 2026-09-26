#!/usr/bin/env python3
"""Build diagnostic DLL from PRIVATE copies; never deploy or modify originals."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument(
        "--unit-pool-capacity", type=int, default=1200,
        help="build the stock reader or a tail-relocation reader for N>=1200",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    if not 1200 <= args.unit_pool_capacity <= 5000:
        parser.error("--unit-pool-capacity must be between 1200 and 5000")
    if args.unit_pool_capacity == 1200:
        pool_base = 0x0066B790
        existence_base = 0x008990C8
    else:
        from patches.population.tail_relocation_storage_layout_v1 import layout

        pool_layout = layout(args.unit_pool_capacity)
        pool_base = pool_layout.regions[0].new_start
        existence_base = pool_layout.regions[1].new_start
    source = root / "tools/inmm_stub"
    out = args.out_dir.resolve()
    if out == root or root in out.parents:
        parser.error("--out-dir must be outside the repository")
    out.mkdir(parents=True, exist_ok=False)
    copied = []
    for path in source.iterdir():
        if path.suffix in {".c", ".h", ".def"} or path.name == "Makefile":
            shutil.copy2(path, out / path.name)
            copied.append(path)
    shutil.copy2(Path(__file__).with_name("runtime_bridge.c"), out / "runtime_bridge.c")
    bridge_source = out / "runtime_bridge.c"
    if args.unit_pool_capacity != 1200:
        bridge_text = bridge_source.read_text()
        replacements = {
            "0x66b790u": f"0x{pool_base:08x}u",
            "0x8990c8u": f"0x{existence_base:08x}u",
            "1200": str(args.unit_pool_capacity),
        }
        for old, new in replacements.items():
            if old not in bridge_text:
                raise RuntimeError(f"pool1210 bridge anchor missing: {old}")
            bridge_text = bridge_text.replace(old, new)
        bridge_source.write_text(bridge_text)
    stub = out / "inmm_stub.c"
    text = stub.read_text()
    anchor = "DWORD WINAPI _imeGetTime(void)\n{\n"
    if text.count(anchor) != 1:
        raise RuntimeError("stub _imeGetTime anchor mismatch; no build performed")
    text = text.replace(anchor,
        "extern void supply_probe_poll(void *caller);\n" + anchor +
        "    supply_probe_poll(__builtin_return_address(0));\n")
    # Avoid placing extern between __declspec(dllexport) and the exported function.
    text = text.replace("__declspec(dllexport)\nextern void supply_probe_poll(void *caller);\n",
                        "extern void supply_probe_poll(void *caller);\n__declspec(dllexport)\n")
    stub.write_text(text)
    makefile = out / "Makefile"
    text = makefile.read_text()
    if text.count("SRCS = ") != 1:
        raise RuntimeError("stub Makefile SRCS anchor mismatch")
    makefile.write_text(text.replace("SRCS = ", "SRCS = runtime_bridge.c "))
    subprocess.run(["make", "all"], cwd=out, check=True)
    dll = out / "_inmm.dll"
    manifest = {
        "diagnostic_only": True,
        "dll": str(dll),
        "dll_sha256": hashlib.sha256(dll.read_bytes()).hexdigest(),
        "original_stub_inputs": {
            str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in copied
        },
        "bridge_sha256": hashlib.sha256((out / "runtime_bridge.c").read_bytes()).hexdigest(),
        "activation_environment": "SYW2_SUPPLY_PROBE=1",
        "unit_pool_capacity": args.unit_pool_capacity,
        "unit_pool_base": f"0x{pool_base:08X}",
        "unit_existence_base": f"0x{existence_base:08X}",
        "request": "C:\\supply_probe_request.txt",
        "result": "C:\\supply_probe_result.json",
        "request_fields": "id op owner slot type rice wood used",
    }
    (out / "supply_bridge_build.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
