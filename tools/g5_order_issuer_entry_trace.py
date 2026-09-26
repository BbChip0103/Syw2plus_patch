#!/usr/bin/env python3
"""Read-only gdb entry-count trace for G5 order-issuing function candidates.

Run under gdb with ``-p <Wine game pid> --batch -x`` (see
``tools/g5_move_order_issuer_probe.py`` for the driving probe). This script
only installs non-invasive software breakpoints (``stop()`` always returns
``False`` so execution is never actually halted for the player) at a small
set of previously-identified order-issuing/dispatch function entry points,
counts how many times each is hit between "armed" and "stop.flag", and writes
a summary. It never writes game memory and never modifies control flow.

The addresses are code addresses inside ``.text``; G5's candidate patch only
relocates *data* (the unit pool base ``0x66b790`` -> ``0x108c000`` and the
selection buffer), so these function entry addresses are identical in the
protected original and the G5 candidate.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_ORDER_ISSUER_TRACE_CONTROL"]
DEADLINE = time.time() + 120

CANDIDATES = {
    "op8_issuer_FUN_00415480": 0x00415480,
    "alt_issuer_FUN_00415880": 0x00415880,
    "group_assign_FUN_00445D30": 0x00445D30,
    "order_consumer_FUN_0040F7D0": 0x0040F7D0,
    "per_tick_dispatch_FUN_0048DDD0": 0x0048DDD0,
    "attack_tick_gate_FUN_00471AF0": 0x00471AF0,
    "selection_toggle_FUN_00412D90": 0x00412D90,
    "deselect_all_FUN_00417080": 0x00417080,
    # lap677 run8: alt_issuer_FUN_00415880's return address on every one of
    # its 18/19 hits was 0x40c882, which decodes to *inside* this function --
    # a per-unit "does this unit have a pending order (word [esi+0x384] !=
    # 1)? if so, dispatch via a jump table at 0x40e720 keyed by the pending
    # command value" consumer. It was not in the original 8-function
    # hypothesis list; add it to see its own total entry count (is it called
    # for every live unit each tick, or only ones with a pending order?).
    "pending_order_consumer_FUN_0040C640": 0x0040C640,
}

events_path = os.path.join(CONTROL, "entry-events.jsonl")
summary_path = os.path.join(CONTROL, "entry-summary.json")
armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")

state = {name: 0 for name in CANDIDATES}
state["fatal"] = None
state["events"] = 0


def frame_registers():
    values = {}
    for name in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp"):
        try:
            values[name] = hex(int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF)
        except Exception:
            values[name] = None
    return values


def return_address():
    """The word at [esp] at function entry: the call site's return address."""
    try:
        esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
        raw = bytes(gdb.selected_inferior().read_memory(esp, 4))
        return hex(struct.unpack("<I", raw)[0])
    except Exception:
        return None


def caller_backtrace():
    try:
        return gdb.execute("bt 6", to_string=True).splitlines()
    except Exception:
        return []


def log(event, **fields):
    state["events"] += 1
    record = {"seq": state["events"], "event": event, "wall_time": time.time()}
    record.update(fields)
    with open(events_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


class EntryBreakpoint(gdb.Breakpoint):
    def __init__(self, name, address):
        super().__init__("*0x%x" % address, gdb.BP_BREAKPOINT)
        self.name = name
        self.address = address

    def stop(self):
        state[self.name] += 1
        # Cap per-name detailed logging so a hot loop (e.g. the per-tick
        # dispatcher, called once per live unit per tick) cannot blow up the
        # event log; the running count in ``state`` remains exact regardless.
        if state[self.name] <= 60:
            log("entry", name=self.name, pc="0x%08x" % self.address,
                registers=frame_registers(), return_address=return_address(),
                backtrace=caller_backtrace())
        return False


summary = {
    "schema": "syw2plus.g5-order-issuer-entry-trace.v1",
    "candidates": {name: hex(address) for name, address in CANDIDATES.items()},
}
try:
    breakpoints = [EntryBreakpoint(name, address) for name, address in CANDIDATES.items()]
    info = gdb.execute("info breakpoints", to_string=True)
    summary["breakpoints_after_arm"] = info
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "candidates": summary["candidates"]}, handle)
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
