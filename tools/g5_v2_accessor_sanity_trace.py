#!/usr/bin/env python3
"""Read-only gdb trace: does the v2 (non-chunked) candidate ever feed the
unbounded slot accessor (0x0040FED0) an out-of-range value after a single
UI order dispatch to a full 50/50 selection?

Companion sanity check for ``tools/g5_v3_chunk_dispatch_trace.py``'s finding
that v3's chunked dispatch produces a live, out-of-range (arg > 1200) call
into this accessor after a MOVE click. v2 has no chunking wrapper at all
(FUN_004AE550 runs unmodified, dispatching only to the first 20 of the
50-capacity selection). If the same out-of-range value still appears under
v2, the corruption is not caused by v3's chunk window swap/restore -- it is
a pre-existing property of how the 50-slot selection array gets populated
by drag-select, merely exposed once any order is issued. If it does NOT
appear under v2, v3's chunking is implicated.

Non-invasive: stop() always returns False.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_V2_ACCESSOR_SANITY_CONTROL"]
DEADLINE = time.time() + 60
CRASH_ACCESSOR_ENTRY = 0x0040FED0

armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")
events_path = os.path.join(CONTROL, "events.jsonl")
summary_path = os.path.join(CONTROL, "trace-summary.json")

state = {"hits": 0, "outliers": 0, "fatal": None}


def read_s16(address):
    return struct.unpack("<h", bytes(gdb.selected_inferior().read_memory(address, 2)))[0]


def reg(name):
    try:
        return int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF
    except Exception:
        return None


def return_address():
    try:
        esp = reg("esp")
        raw = bytes(gdb.selected_inferior().read_memory(esp, 4))
        return hex(struct.unpack("<I", raw)[0])
    except Exception:
        return None


def log(event, **fields):
    record = {"event": event, "wall_time": time.time()}
    record.update(fields)
    with open(events_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


class CrashAccessorEntry(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x%x" % CRASH_ACCESSOR_ENTRY, gdb.BP_BREAKPOINT)

    def stop(self):
        state["hits"] += 1
        esp = reg("esp")
        try:
            arg_signed = read_s16(esp + 4)
        except Exception:
            arg_signed = None
        is_outlier = arg_signed is not None and (arg_signed < 0 or arg_signed > 1200)
        if is_outlier:
            state["outliers"] += 1
            if state["outliers"] <= 20:
                log("outlier", hit_seq=state["hits"], arg_signed=arg_signed, return_address=return_address())
        return False


summary = {"schema": "syw2plus.g5-v2-accessor-sanity-trace.v1", "accessor": hex(CRASH_ACCESSOR_ENTRY)}
try:
    _bp = CrashAccessorEntry()
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True}, handle)
    gdb.execute("continue")
    while time.time() < DEADLINE and not os.path.exists(stop_path):
        try:
            gdb.execute("continue")
        except gdb.error as exc:
            summary["continue_error"] = repr(exc)
            break
    summary["stop_reason"] = "stop_flag" if os.path.exists(stop_path) else "deadline"
    summary.update(state)
except Exception as exc:
    state["fatal"] = repr(exc)
    summary.update(state)
finally:
    try:
        gdb.execute("detach")
        summary["detached"] = True
    except Exception as exc:
        summary["detach_error"] = repr(exc)
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
