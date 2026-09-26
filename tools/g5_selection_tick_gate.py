#!/usr/bin/env python3
"""Release a G5 drag gate only after the attached game tick advances.

This is a read-only observer for the private Wine process.  It never sends
input, changes game memory, or kills a process; the probe owns lifecycle and
cleanup.  The fixed tick address is documented by the existing runtime driver.
"""

from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
import struct
import time


TICK_ADDRESS = 0x008924B8


class IOV(ctypes.Structure):
    _fields_ = [("base", ctypes.c_void_p), ("size", ctypes.c_size_t)]


LIBC = ctypes.CDLL(None, use_errno=True)
LIBC.process_vm_readv.restype = ctypes.c_ssize_t


def read_word(pid: int, address: int) -> int:
    buf = ctypes.create_string_buffer(4)
    n = LIBC.process_vm_readv(
        pid,
        ctypes.byref(IOV(ctypes.cast(buf, ctypes.c_void_p), 4)),
        1,
        ctypes.byref(IOV(address, 4)),
        1,
        0,
    )
    if n != 4:
        raise OSError(ctypes.get_errno(), f"read {pid}:{address:x}, got {n}/4")
    return struct.unpack("<I", buf.raw)[0]


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def wait_for_tick(pid: int, control: Path, timeout: float) -> int:
    deadline = time.monotonic() + timeout
    first: int | None = None
    while time.monotonic() < deadline:
        try:
            current = read_word(pid, TICK_ADDRESS)
        except OSError:
            time.sleep(0.05)
            continue
        if first is None:
            first = current
            write_json(control / "tick_start.json", {
                "pid": pid, "address": hex(TICK_ADDRESS), "tick": first,
                "observed_at": time.time(),
            })
        elif current != first:
            write_json(control / "tick_ready.json", {
                "pid": pid, "address": hex(TICK_ADDRESS),
                "tick_before": first, "tick_after": current,
                "observed_at": time.time(),
            })
            return 0
        time.sleep(0.05)
    write_json(control / "tick_timeout.json", {
        "pid": pid, "address": hex(TICK_ADDRESS), "tick_before": first,
        "timeout_seconds": timeout, "observed_at": time.time(),
    })
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, required=True)
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    args = parser.parse_args()
    args.control.mkdir(parents=True, exist_ok=True)
    return wait_for_tick(args.pid, args.control, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
