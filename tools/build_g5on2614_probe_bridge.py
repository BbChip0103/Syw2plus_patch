#!/usr/bin/env python3
"""Build the private 2614 WinMM fixture probe after exact PE guard checks."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import pefile


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_SHA256 = "ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf"
PROFILE = (
    (0x004AF5E0, "53 66 8b 5c 24 0c 56 57"),
    (0x00440C20, "8b 4c 24 04 81 ec 00 01"),
    (0x00440FF0, "8b 4c 24 04 81 ec 04 01"),
    (0x0043ED60, "8b 44 24 04 89 41 14 50"),
    (0x0043ED80, "8b 44 24 04 89 41 18 50"),
    (0x00443190, "55 8b 6c 24 08 0f bf c5"),
    (0x0042ECB0, "83 ec 18 53 55 56 8b 74"),
    (0x0043EDA0, "66 83 7c 24 08 01"),
    (0x0042334A, "ff d6"),
)
CALLER_IAT = 0x004E5294


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_target(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    digest = sha256(data)
    if digest != ORIGINAL_SHA256:
        raise ValueError(f"2614 target SHA mismatch: {digest}")
    pe = pefile.PE(data=data, fast_load=False)
    base = pe.OPTIONAL_HEADER.ImageBase
    checked: list[dict[str, str]] = []
    for va, expected_hex in PROFILE:
        expected = bytes.fromhex(expected_hex)
        actual = pe.get_data(va - base, len(expected))
        if actual != expected:
            raise ValueError(
                f"profile mismatch at 0x{va:08x}: expected={expected.hex()} actual={actual.hex()}"
            )
        checked.append({"va": f"0x{va:08x}", "bytes": actual.hex()})
    imports = []
    for descriptor in pe.DIRECTORY_ENTRY_IMPORT:
        for item in descriptor.imports:
            if item.address == CALLER_IAT:
                imports.append((descriptor.dll.decode("ascii", errors="replace").lower(), item.name))
    if imports != [("winmm.dll", b"timeGetTime")]:
        raise ValueError(f"tick IAT mismatch at 0x{CALLER_IAT:08x}: {imports!r}")
    return {"target_sha256": digest, "profile": checked,
            "tick_iat": {"va": f"0x{CALLER_IAT:08x}", "dll": "WINMM.dll", "name": "timeGetTime"}}


def build(target: Path, out_dir: Path) -> dict[str, object]:
    verification = verify_target(target)
    out_dir = out_dir.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    source_dir = ROOT / "tools" / "inmm_stub"
    dll = out_dir / "winmm.dll"
    command = [
        "i686-w64-mingw32-gcc", "-m32", "-shared", "-Wall", "-Wextra", "-O2",
        "-fno-stack-protector", "-mno-stack-arg-probe", "-o", str(dll),
        str(source_dir / "g5on2614_winmm_probe.c"),
        str(ROOT / "patches" / "population" / "runtime_bridge.c"),
        str(source_dir / "g5on2614_winmm_probe.def"),
        "-I", str(source_dir),
        "-nostartfiles", "-nodefaultlibs", "-Wl,-e,_DllMain@12",
        "-lkernel32", "-luser32",
    ]
    subprocess.run(command, cwd=out_dir, check=True)
    result = {
        "diagnostic_only": True,
        "target": str(target.resolve()),
        "target_sha256": verification["target_sha256"],
        "profile": verification["profile"],
        "tick_iat": verification["tick_iat"],
        "dll": str(dll),
        "dll_sha256": sha256(dll.read_bytes()),
        "source_sha256": {
            str(source_dir / name): sha256((source_dir / name).read_bytes())
            for name in ("g5on2614_winmm_probe.c", "g5on2614_winmm_probe.def")
        },
        "bridge_source_sha256": sha256((ROOT / "patches" / "population" / "runtime_bridge.c").read_bytes()),
        "tick_callback": "timeGetTime proxy calls supply_probe_poll with pinned caller VA 0x42334C, then forwards to system WINMM",
    }
    (out_dir / "g5on2614_winmm_probe.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-exe", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.target_exe, args.out_dir), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
