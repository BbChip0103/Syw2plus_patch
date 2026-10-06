#!/usr/bin/env python3
"""Build diagnostic DLL from PRIVATE copies; never deploy or modify originals."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> None:
    from patches.population.g2_esl2608_runtime_layout import from_pool_base as esl2608_layout

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument(
        "--unit-pool-capacity", type=int, default=1200,
        help="build the stock reader or a tail-relocation reader for N>=1200",
    )
    parser.add_argument(
        "--unit-pool-base", type=lambda value: int(value, 0), default=None,
        help="explicit appended ESL2608 pool base (required only for that layout)",
    )
    parser.add_argument(
        "--bridge-source", type=Path, default=None,
        help=(
            "override runtime_bridge.c with a private fork (e.g. a probe-scoped "
            "diagnostic op) without touching the shared file G2's approved bridge "
            "SHA256 pin (tools/runtime_env.py G2_APPROVED_BRIDGE_SHA256) is keyed to"
        ),
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    if not 1200 <= args.unit_pool_capacity <= 5000:
        parser.error("--unit-pool-capacity must be between 1200 and 5000")
    if args.unit_pool_capacity == 1200:
        if args.unit_pool_base is not None:
            parser.error("--unit-pool-base is only valid with the ESL2608 4093-slot layout")
        pool_base = 0x0066B790
        existence_base = 0x008990C8
    elif args.unit_pool_base is not None:
        resolved = esl2608_layout(args.unit_pool_base, args.unit_pool_capacity)
        pool_base = resolved.unit_pool_base
        existence_base = resolved.unit_existence_base
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
    bridge_source_input = args.bridge_source or Path(__file__).with_name("runtime_bridge.c")
    shutil.copy2(bridge_source_input, out / "runtime_bridge.c")
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
        "bridge_source": str(bridge_source_input.resolve()),
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
