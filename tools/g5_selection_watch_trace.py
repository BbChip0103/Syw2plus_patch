#!/usr/bin/env python3
"""Read-only gdb trace for the G5 selection writer.

Run under gdb with ``-p <Wine game pid> -x``.  The probe owns all input and
creates ``G5_SELECTION_TRACE_CONTROL``; this script only installs hardware
watchpoints/breakpoints, reads registers/memory, and writes JSON evidence.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_SELECTION_TRACE_CONTROL"]
BASE = 0x0108C000
COUNT = BASE
USER_TARGET = BASE + 20 * 4
CONSUMER = 0x0041DC40
TICK = 0x00  # optional; this trace does not guess a version-specific tick VA
DEADLINE = time.time() + 120

events_path = os.path.join(CONTROL, "trace-events.jsonl")
summary_path = os.path.join(CONTROL, "trace-summary.json")
armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")

state = {
    "events": 0,
    "watch_hits": {"count": 0, "user_target": 0},
    "consumer_entries": 0,
    "writer_entries": 0,
    "fatal": None,
}


def read_bytes(address, size):
    return bytes(gdb.selected_inferior().read_memory(address, size))


def read_u32(address):
    return struct.unpack("<I", read_bytes(address, 4))[0]


def log(event, **fields):
    state["events"] += 1
    record = {"seq": state["events"], "event": event, "wall_time": time.time()}
    record.update(fields)
    with open(events_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def frame_pc():
    try:
        return hex(int(gdb.selected_frame().pc()) & 0xFFFFFFFF)
    except Exception:
        return None


def frame_registers():
    values = {}
    for name in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp"):
        try:
            values[name] = hex(int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF)
        except Exception:
            values[name] = None
    return values


class ConsumerEntryBreakpoint(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x%x" % CONSUMER, gdb.BP_HARDWARE_BREAKPOINT)

    def stop(self):
        state["consumer_entries"] += 1
        registers = frame_registers()
        esp = None
        return_address = None
        try:
            esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
            return_address = read_u32(esp)
        except Exception:
            pass
        log("consumer_entry", pc=frame_pc(), esp=hex(esp) if esp is not None else None,
            return_address=(hex(return_address) if return_address is not None else None),
            registers=registers)
        return False


class WriterEntryBreakpoint(gdb.Breakpoint):
    """Trace the selection writer entry without modifying execution."""

    def __init__(self):
        super().__init__("*0x412d90", gdb.BP_HARDWARE_BREAKPOINT)

    def stop(self):
        state["writer_entries"] += 1
        esp = None
        return_address = None
        try:
            esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
            return_address = read_u32(esp)
        except Exception:
            pass
        log("writer_entry", pc=frame_pc(), esp=hex(esp) if esp is not None else None,
            return_address=(hex(return_address) if return_address is not None else None),
            registers=frame_registers())
        return False


class WriteWatch(gdb.Breakpoint):
    def __init__(self, name, address):
        super().__init__("*(int*)0x%x" % address, gdb.BP_WATCHPOINT, gdb.WP_WRITE)
        self.name = name
        self.address = address
        self.last = None
        try:
            self.last = read_u32(address)
        except Exception:
            pass

    def stop(self):
        try:
            value = read_u32(self.address)
        except Exception:
            value = None
        old = self.last
        if value is not None:
            self.last = value
        state["watch_hits"][self.name] += 1
        log("write_watch", name=self.name, address=hex(self.address),
            old=old, new=value, pc=frame_pc(), registers=frame_registers())
        return False


summary = {"schema": "syw2plus.g5-selection-writer-trace.v1", "base": hex(BASE),
           "count_address": hex(COUNT), "user_target_address": hex(USER_TARGET),
           "consumer_address": hex(CONSUMER)}
try:
    gdb.execute("set can-use-hw-watchpoints 1")
    try:
        gdb.execute("set architecture i386")
    except Exception as exc:
        summary["architecture_error"] = repr(exc)
    watches = [WriteWatch("count", COUNT), WriteWatch("user_target", USER_TARGET)]
    consumer = ConsumerEntryBreakpoint()
    writer = WriterEntryBreakpoint()
    info = gdb.execute("info breakpoints", to_string=True)
    summary["breakpoints_after_arm"] = info
    if info.count("hw watchpoint") != 2 or info.count("hw breakpoint") < 2:
        summary["blocked_reason"] = "hardware_debug_register_arm_failed"
    else:
        with open(armed_path, "w", encoding="utf-8") as handle:
            json.dump({"armed": True, "hardware_watchpoints": 2,
                       "hardware_breakpoint": hex(CONSUMER)}, handle)
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
