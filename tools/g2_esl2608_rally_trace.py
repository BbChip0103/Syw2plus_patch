#!/usr/bin/env python3
"""Read-only gdb trace for the ESL2608 rally command path."""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G2_RALLY_TRACE_CONTROL"]
STOP = os.path.join(CONTROL, "stop.flag")
ARMED = os.path.join(CONTROL, "armed.json")
EVENTS = os.path.join(CONTROL, "events.jsonl")
SUMMARY = os.path.join(CONTROL, "summary.json")
TARGETS = {
    0x004AE550: "queue_builder",
    0x004AEC60: "queue_forwarder",
    0x0040FF90: "command_forwarder",
    0x00412540: "hq_command_writer",
}
state = {"hits": {name: 0 for name in TARGETS.values()}, "events": [], "fatal": None}


def read_u32(address):
    return struct.unpack("<I", bytes(gdb.selected_inferior().read_memory(address, 4)))[0]


def registers():
    values = {}
    for name in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp"):
        try:
            values[name] = hex(int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF)
        except Exception:
            values[name] = None
    return values


def event(name, address):
    regs = registers()
    esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
    stack = []
    for index in range(1, 6):
        try:
            stack.append(hex(read_u32(esp + 4 * index)))
        except Exception:
            stack.append(None)
    record = {
        "event": name,
        "address": hex(address),
        "time": time.time(),
        "registers": regs,
        "stack_args": stack,
        "action_arg": stack[0] if stack else None,
        "packed_xy_arg": stack[1] if len(stack) > 1 else None,
        "hq_this_ecx": regs.get("ecx") if name == "hq_command_writer" else None,
    }
    state["hits"][name] += 1
    state["events"].append(record)
    with open(EVENTS, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


class Entry(gdb.Breakpoint):
    def __init__(self, address, name):
        super().__init__("*0x%X" % address, gdb.BP_BREAKPOINT, internal=True)
        self.address = address
        self.name = name

    def stop(self):
        event(self.name, self.address)
        return False


try:
    for address, name in TARGETS.items():
        Entry(address, name)
    with open(ARMED, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "targets": {name: hex(address) for address, name in TARGETS.items()}}, handle)
    gdb.execute("continue")
    while not os.path.exists(STOP):
        try:
            gdb.execute("continue")
        except gdb.error as exc:
            state["fatal"] = repr(exc)
            break
except Exception as exc:
    state["fatal"] = repr(exc)
finally:
    try:
        gdb.execute("detach")
    except Exception as exc:
        state["detach_error"] = repr(exc)
    with open(SUMMARY, "w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2, sort_keys=True)
