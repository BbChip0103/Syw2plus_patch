#!/usr/bin/env python3
"""Read-only gdb hardware-watchpoint trace for the G5 pending-order writer.

``g5_pending_broadcast_snapshot_probe.py`` found that a single click on 50
selected units writes a pending order into exactly the first 20 entries of
the selection array (in drag/selection order) -- an exact, reproducible
count that matches the *original* stock selection capacity, not a
probabilistic pathfinding/consumption effect. This trace pinpoints the
writer itself: it arms one hardware write watchpoint on each of four
selected units' pending-command word (``unit+0x384``) straddling that exact
boundary (selection positions 18/19/20/21, 0-indexed -- i.e. the last two
units that receive the order and the first two that do not), then records
the PC, return address, and backtrace of every write that lands on them.

If the boundary is real, positions 18-19 should show a write hit each (from
the broadcast loop) and positions 20-21 should show none for the whole
click, which directly proves the loop bound is a literal ``20`` rather than
reading the relocated 50-capacity count.

The watchpoints are read-only observation of existing writes -- this script
never itself writes game memory and never modifies control flow.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_PENDING_WRITER_TRACE_CONTROL"]
DEADLINE = time.time() + 60

target_path = os.path.join(CONTROL, "writer-target.json")
with open(target_path, "r", encoding="utf-8") as handle:
    TARGET = json.load(handle)

WATCH_ADDRESSES = {str(item["position"]): int(item["address"], 16) for item in TARGET["watches"]}

armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")
events_path = os.path.join(CONTROL, "writer-events.jsonl")
summary_path = os.path.join(CONTROL, "writer-summary.json")

state = {"hits": {name: 0 for name in WATCH_ADDRESSES}, "events": 0, "fatal": None}


def read_u32(address):
    return struct.unpack("<I", bytes(gdb.selected_inferior().read_memory(address, 4)))[0]


def frame_registers():
    values = {}
    for name in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp"):
        try:
            values[name] = hex(int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF)
        except Exception:
            values[name] = None
    return values


def caller_backtrace():
    try:
        return gdb.execute("bt 8", to_string=True).splitlines()
    except Exception:
        return []


def caller_return_address():
    """The word at [esp] at the moment of the trap.

    The watched writer (``0x412540``) performs no push/pop between its entry
    and the traced write, so ``esp`` here still holds the same value it had
    on entry -- the call site's return address -- regardless of whether the
    ``bt`` command's frame-pointer-based unwind can make sense of this
    ebp-less function (it cannot; see the writer-probe's own findings).
    """
    try:
        esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
        return hex(read_u32(esp))
    except Exception:
        return None


def log(event, **fields):
    state["events"] += 1
    record = {"seq": state["events"], "event": event, "wall_time": time.time()}
    record.update(fields)
    with open(events_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


class PendingWriteWatch(gdb.Breakpoint):
    def __init__(self, position, address):
        super().__init__("*(int*)0x%x" % address, gdb.BP_WATCHPOINT, gdb.WP_WRITE)
        self.position = position
        self.address = address

    def stop(self):
        state["hits"][self.position] += 1
        try:
            pc = hex(int(gdb.selected_frame().pc()) & 0xFFFFFFFF)
        except Exception:
            pc = None
        try:
            new_value = hex(read_u32(self.address))
        except Exception:
            new_value = None
        log(
            "write", position=self.position, address=hex(self.address), pc=pc,
            new_value=new_value, registers=frame_registers(), backtrace=caller_backtrace(),
            caller_return_address=caller_return_address(),
        )
        return False


summary = {
    "schema": "syw2plus.g5-pending-broadcast-writer-trace.v1",
    "watches": {name: hex(address) for name, address in WATCH_ADDRESSES.items()},
}
try:
    watches = [PendingWriteWatch(name, address) for name, address in WATCH_ADDRESSES.items()]
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "watches": summary["watches"]}, handle)
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
