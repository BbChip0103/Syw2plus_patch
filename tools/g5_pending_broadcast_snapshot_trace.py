#!/usr/bin/env python3
"""Read-only gdb snapshot trace for the G5 pending-order broadcast writer.

lap677 established that raw entry counts into ``FUN_0040C640`` (the
per-unit-per-tick pending-order consumer) cannot answer "how many selected
units actually received a pending order" -- that function runs once per
*live* unit every tick regardless of whether it has a pending order, so its
entry count tracks the live unit population, not the broadcast.

The only way to answer that question directly is to read the pending-command
field (``unit+0x384``) for every selected unit at an instant *before* any of
them have had this tick's consumption pass touch it. ``FUN_0040C640``'s own
entry point is that instant: gdb Python breakpoint ``stop()`` callbacks run
while the inferior is already fully paused (this is true regardless of the
callback's return value), so a snapshot taken inside ``stop()`` is atomic
with respect to the *game* -- no consumption can happen while it runs. Firing
on the very first hit after the driving probe's ground click has been sent
(signalled by ``click_marker`` in the control directory) captures the
selected units' fields as written by the click's own input handler, before
this tick's (or any tick's) per-unit consumption loop has processed a single
entry.

The breakpoint's ``stop()`` always returns ``False`` (same non-invasive
pattern as ``g5_order_issuer_entry_trace.py``): the debuggee is never left
halted for the player, only paused for the duration of one memory read.
Several post-marker snapshots (not just the first) are recorded so a slow or
staggered write batch remains visible rather than silently averaged away.
This script never writes game memory and never modifies control flow.
"""

import gdb
import json
import os
import time


CONTROL = os.environ["G5_PENDING_SNAPSHOT_CONTROL"]
DEADLINE = time.time() + 120
CONSUMER_ENTRY = 0x0040C640
MAX_POST_MARKER_SAMPLES = 5

target_path = os.path.join(CONTROL, "target.json")
with open(target_path, "r", encoding="utf-8") as handle:
    TARGET = json.load(handle)

SELECTION_BASE = int(TARGET["selection_base"], 16)
SELECTION_CAPACITY = int(TARGET["selection_capacity"])
UNIT_BASE = int(TARGET["unit_base"], 16)
UNIT_STRIDE = int(TARGET["unit_stride"], 16)
COMMAND_OFFSET = int(TARGET["command_offset"], 16)
PENDING_OFFSET = int(TARGET["pending_offset"], 16)
PENDING_XY_OFFSET = int(TARGET["pending_xy_offset"], 16)
PENDING_TARGET_UID_OFFSET = int(TARGET["pending_target_uid_offset"], 16)

armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")
marker_path = os.path.join(CONTROL, "click_marker.flag")
samples_path = os.path.join(CONTROL, "snapshots.jsonl")

state = {"entries": 0, "post_marker_samples": 0, "fatal": None}


def read_u32(inferior, address):
    return int.from_bytes(bytes(inferior.read_memory(address, 4)), "little")


def read_i16(inferior, address):
    raw = bytes(inferior.read_memory(address, 2))
    value = int.from_bytes(raw, "little")
    return value - 0x10000 if value >= 0x8000 else value


def snapshot(inferior, *, entry_index):
    count = read_u32(inferior, SELECTION_BASE)
    if not 0 <= count <= SELECTION_CAPACITY:
        return {"entry_index": entry_index, "wall_time": time.time(), "error": "count_out_of_range", "count": count}
    slots = []
    for index in range(count):
        raw_entry = read_u32(inferior, SELECTION_BASE + 4 + index * 4)
        slots.append(raw_entry & 0xFFF)
    rows = []
    for slot in slots:
        base = UNIT_BASE + slot * UNIT_STRIDE
        rows.append({
            "slot": slot,
            "command": read_i16(inferior, base + COMMAND_OFFSET),
            "pending_command": read_u32(inferior, base + PENDING_OFFSET),
            "pending_xy": read_u32(inferior, base + PENDING_XY_OFFSET),
            "pending_target_uid": read_u32(inferior, base + PENDING_TARGET_UID_OFFSET),
        })
    pending_written = sum(1 for row in rows if row["pending_command"] != 1)
    return {
        "entry_index": entry_index,
        "wall_time": time.time(),
        "selection_count": count,
        "rows": rows,
        "pending_written_count": pending_written,
    }


class SnapshotBreakpoint(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x%x" % CONSUMER_ENTRY, gdb.BP_BREAKPOINT)

    def stop(self):
        state["entries"] += 1
        if os.path.exists(marker_path) and state["post_marker_samples"] < MAX_POST_MARKER_SAMPLES:
            state["post_marker_samples"] += 1
            record = snapshot(gdb.selected_inferior(), entry_index=state["entries"])
            with open(samples_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
        return False


summary = {"schema": "syw2plus.g5-pending-broadcast-snapshot-trace.v1", "consumer_entry": hex(CONSUMER_ENTRY)}
try:
    breakpoint = SnapshotBreakpoint()
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "consumer_entry": hex(CONSUMER_ENTRY)}, handle)
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
    with open(os.path.join(CONTROL, "trace-summary.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
