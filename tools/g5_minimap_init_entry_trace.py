#!/usr/bin/env python3
"""Read-only gdb entry-count trace for the minimap-position-init candidate.

Run under gdb with ``-p <Wine game pid> --batch -x`` (see
``tools/g5_minimap_init_breakpoint_probe.py`` for the driving probe). This
script only installs non-invasive software breakpoints (``stop()`` always
returns ``False`` so execution is never actually halted for the player) at
two previously-identified addresses and counts/logs how many times each is
hit, from process start through a full menu-to-gameplay session. It never
writes game memory and never modifies control flow.

lap759 static disassembly of the protected original found a single direct
caller (``0x451138``, inside a large ~0x1c000-byte struct-zeroing
initializer starting at ``0x451130``) of a tiny leaf function at
``0x451C10``: ``mov DWORD PTR [ecx],0x0`` / ``mov DWORD PTR [ecx+0x4],0x1fd``
/ ``ret``. The cafe-community reference (``0x451C12``/``0x451C19``, read-only
``Syw2plus_re`` doc) labels the two immediates inside that leaf function
"minimap X coordinate" / "minimap Y coordinate" -- but those are *constants
baked into .text* (always 0 and 509 whether or not the function ever runs),
not a live memory address to poll. The only way to learn whether this
constructor path is reached at runtime is to trace whether ``0x451130``
(and, redundantly, the leaf it calls) is ever *called*.

The addresses are code addresses inside ``.text`` and unrelated to any G5
selection-buffer relocation, so they are identical in the protected original
and every G5 candidate; this trace only targets the protected original.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_MINIMAP_INIT_TRACE_CONTROL"]
DEADLINE = time.time() + float(os.environ.get("G5_MINIMAP_INIT_TRACE_DEADLINE", "180"))

CANDIDATES = {
    "widget_ctor_FUN_00451130": 0x00451130,
    "xy_writer_FUN_00451C10": 0x00451C10,
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
        if state[self.name] <= 60:
            log("entry", name=self.name, pc="0x%08x" % self.address,
                registers=frame_registers(), return_address=return_address(),
                backtrace=caller_backtrace())
        return False


summary = {
    "schema": "syw2plus.g5-minimap-init-entry-trace.v1",
    "candidates": {name: hex(address) for name, address in CANDIDATES.items()},
}
try:
    # The game process may not have mapped the PE's .text yet at the moment
    # gdb attaches (the driver attaches immediately after Popen to catch any
    # very-early/startup call, before the main-menu state is reachable).
    # Retry breakpoint creation for a few seconds rather than failing hard.
    breakpoints = []
    retry_deadline = time.time() + 10
    last_exc = None
    while not breakpoints and time.time() < retry_deadline:
        try:
            breakpoints = [EntryBreakpoint(name, address) for name, address in CANDIDATES.items()]
        except gdb.error as exc:
            last_exc = repr(exc)
            for bp in list(gdb.breakpoints() or []):
                bp.delete()
            time.sleep(0.25)
    if not breakpoints:
        raise RuntimeError(f"could not arm breakpoints before deadline: {last_exc}")
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
