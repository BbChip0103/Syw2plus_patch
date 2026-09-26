#!/usr/bin/env python3
"""Read-only gdb entry trace for the G5 pending-order broadcast loop.

``g5_pending_broadcast_writer_probe.py`` found the exact per-unit order
writer (``0x412540``) and its immediate thin wrapper (``0x40ff90``, "slot ->
unit address, call 0x412540"). Neither has a decoded-call-immediate static
xref, so the actual 20-iteration broadcast loop that calls ``0x40ff90`` once
per selected unit is still unknown. This script breaks at ``0x40ff90``'s
entry point and, for every hit after the driving probe's click marker
appears, reads the return address directly from ``[esp]`` (reliable here
because this function -- like ``0x412540`` -- has no ``push ebp`` prologue,
so ``esp`` at entry still points at the call site's return address; the
frame-pointer-based ``bt`` command was already shown to misread this in
``g5_pending_broadcast_writer_trace.py``'s first run).

A second breakpoint at ``0x4aec60`` (the dispatcher that the outer loop
calls, which itself calls ``0x40ff90``) captures ebx/ebp *before* that
function's own prologue clobbers ebx with a local order-code temporary --
the first attempt at reading the outer loop's ebx/ebp from inside
``0x40ff90`` found only the already-clobbered value, since ``0x40ff90`` is
two call-frames below the real loop.

Both breakpoints' ``stop()`` always return ``False`` (same non-invasive
pattern as the other *_trace.py scripts here): the debuggee is never left
halted for the player, only paused for the duration of one memory read.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_BROADCAST_LOOP_TRACE_CONTROL"]
DEADLINE = time.time() + 60
WRAPPER_ENTRY = 0x0040FF90
DISPATCH_ENTRY = 0x004AEC60
MAX_POST_MARKER_SAMPLES = 10

armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")
marker_path = os.path.join(CONTROL, "click_marker.flag")
events_path = os.path.join(CONTROL, "entry-events.jsonl")
dispatch_events_path = os.path.join(CONTROL, "dispatch-events.jsonl")
summary_path = os.path.join(CONTROL, "trace-summary.json")

state = {"entries": 0, "post_marker_samples": 0, "dispatch_entries": 0,
         "dispatch_post_marker_samples": 0, "fatal": None}


def read_u32(address):
    return struct.unpack("<I", bytes(gdb.selected_inferior().read_memory(address, 4)))[0]


def read_u16(address):
    return struct.unpack("<H", bytes(gdb.selected_inferior().read_memory(address, 2)))[0]


def read_u8(address):
    return bytes(gdb.selected_inferior().read_memory(address, 1))[0]


class WrapperEntryBreakpoint(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x%x" % WRAPPER_ENTRY, gdb.BP_BREAKPOINT)

    def stop(self):
        state["entries"] += 1
        if os.path.exists(marker_path) and state["post_marker_samples"] < MAX_POST_MARKER_SAMPLES:
            state["post_marker_samples"] += 1
            try:
                esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
                return_address = hex(read_u32(esp))
                # The wrapper's own first argument -- the selection-array
                # slot index, read the same way every sibling function in
                # this block (0x40fe30..0x40ffe0) reads its own first arg
                # (``movsx ecx, word ptr [esp+4]``) -- sits at [esp+4] at
                # entry, before any of this function's own pushes.
                arg_slot = read_u32(esp + 4) & 0xFFFF
            except Exception as exc:
                return_address = None
                arg_slot = None
                state["fatal"] = repr(exc)
            record = {
                "seq": state["entries"], "wall_time": time.time(),
                "return_address": return_address, "arg_slot": arg_slot,
            }
            with open(events_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
        return False


class DispatchEntryBreakpoint(gdb.Breakpoint):
    """Capture the outer loop's ebx/ebp before 0x4aec60's own prologue clobbers ebx."""

    def __init__(self):
        super().__init__("*0x%x" % DISPATCH_ENTRY, gdb.BP_BREAKPOINT)

    def stop(self):
        state["dispatch_entries"] += 1
        if os.path.exists(marker_path) and state["dispatch_post_marker_samples"] < MAX_POST_MARKER_SAMPLES:
            state["dispatch_post_marker_samples"] += 1
            try:
                ebx = int(gdb.selected_frame().read_register("ebx")) & 0xFFFFFFFF
                ebp = int(gdb.selected_frame().read_register("ebp")) & 0xFFFFFFFF
                record = {
                    "seq": state["dispatch_entries"], "wall_time": time.time(),
                    "ebx": hex(ebx), "ebp": hex(ebp),
                    "word_at_ebx_plus_0xa": read_u16(ebx + 0xA),
                    "dword_at_ebx": hex(read_u32(ebx)),
                    "byte_at_ebx_minus_1": read_u8(ebx - 1),
                    "byte_at_ebx_minus_2": read_u8(ebx - 2),
                    "word_at_ebp": read_u16(ebp),
                    "words_at_ebp_plus_0x14": [read_u16(ebp + 0x14 + 2 * i) for i in range(25)],
                }
            except Exception as exc:
                record = {"seq": state["dispatch_entries"], "wall_time": time.time(), "error": repr(exc)}
            with open(dispatch_events_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
        return False


summary = {
    "schema": "syw2plus.g5-pending-broadcast-loop-entry-trace.v2",
    "wrapper_entry": hex(WRAPPER_ENTRY), "dispatch_entry": hex(DISPATCH_ENTRY),
}
try:
    wrapper_bp = WrapperEntryBreakpoint()
    dispatch_bp = DispatchEntryBreakpoint()
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "wrapper_entry": hex(WRAPPER_ENTRY), "dispatch_entry": hex(DISPATCH_ENTRY)}, handle)
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
