#!/usr/bin/env python3
"""Read-only gdb trace for the code that fills the G5 order-record on the stack.

Prior traces (``g5_pending_broadcast_stack_builder_probe.py``) tried to
*learn* the stack source address from a first order's copy-out, then watch
that address during a *second* order in the same process. That failed
(``g5_pending_broadcast_staging_rotation_probe.py`` explains why, with a
plain before/after memory diff and no gdb involved at all): a second order
issued while an earlier one is still in flight patches a few header fields
of the existing 0x893130 record *in place* (small single-field stores) --
it never re-runs the "build full 60-byte record on the stack, then ``rep
movsd`` copy it out" path that a *first* order takes, so there is no second
copy-out to correlate against.

That same diff probe also found the record's real field layout (the count
field is at offset ``+0xe``, not ``+0xa`` as first assumed from the
*destination* queue-slot struct -- the two structs share a layout but this
offset was misread across them) and confirmed the source stack address is
identical (``0x31f958``) across every independent fresh process launch
observed so far (Wine/this build apparently doesn't randomize it at this
call depth). So this trace hardcodes that address and watches it plus the
copy-out marker in a *single* session, for a *single, first* order of a
freshly started process -- no dynamic breakpoint creation from inside
another breakpoint's callback (the earlier cause of a gdb-internal SIGSEGV),
and no second-order in-place-update ambiguity.

Because the watched stack slot is heavily reused by unrelated per-tick code
(confirmed: hundreds to thousands of unrelated hits/sec), only the *last*
write to each field before the copy-out marker fires is kept (a write
immediately followed by that field being copied into the broadcast record
must be the genuine value, whatever wrote it) -- see
``g5_pending_broadcast_stack_builder_trace.py``'s ``run_fields`` docstring
for why this correlation is safe here.

Read-only: this script never writes game memory or alters control flow
beyond the temporary breaks needed to take one memory/register snapshot per
hit.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_ORDER_BUILDER_TRACE_CONTROL"]
DEADLINE = time.time() + 60
STAGING_DEST = 0x00893130
STACK_BASE = 0x0031F958

armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")
events_path = os.path.join(CONTROL, "builder-events.jsonl")
summary_path = os.path.join(CONTROL, "trace-summary.json")

TARGETS = {
    "count_field_0xe": STACK_BASE + 0xE,
    "list_entry_0": STACK_BASE + 0x14,
    "list_entry_19": STACK_BASE + 0x14 + 19 * 2,
}

state = {"hits": {name: 0 for name in TARGETS}, "marker_hits": 0, "fatal": None}
last_seen: dict[str, dict] = {name: None for name in TARGETS}


def read_u16(address):
    return struct.unpack("<H", bytes(gdb.selected_inferior().read_memory(address, 2)))[0]


def frame_registers():
    values = {}
    for name in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp"):
        try:
            values[name] = hex(int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF)
        except Exception:
            values[name] = None
    return values


def esp_word():
    try:
        esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
        return hex(struct.unpack("<I", bytes(gdb.selected_inferior().read_memory(esp, 4)))[0])
    except Exception:
        return None


def log(event, **fields):
    record = {"event": event, "wall_time": time.time()}
    record.update(fields)
    with open(events_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


class FieldWatch(gdb.Breakpoint):
    def __init__(self, position, address):
        super().__init__("*(short*)0x%x" % address, gdb.BP_WATCHPOINT, gdb.WP_WRITE)
        self.position = position
        self.address = address

    def stop(self):
        state["hits"][self.position] += 1
        try:
            pc = hex(int(gdb.selected_frame().pc()) & 0xFFFFFFFF)
        except Exception:
            pc = None
        try:
            new_value = read_u16(self.address)
        except Exception:
            new_value = None
        last_seen[self.position] = {
            "pc": pc, "new_value": new_value, "esp_word": esp_word(),
            "registers": frame_registers(), "hit_seq": state["hits"][self.position],
        }
        return False


class MarkerWatch(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*(int*)0x%x" % STAGING_DEST, gdb.BP_WATCHPOINT, gdb.WP_WRITE)

    def stop(self):
        state["marker_hits"] += 1
        try:
            marker_new_value = hex(
                struct.unpack("<I", bytes(gdb.selected_inferior().read_memory(STAGING_DEST, 4)))[0]
            )
        except Exception:
            marker_new_value = None
        log("correlated_order_issue", marker_hit_seq=state["marker_hits"],
            marker_new_value=marker_new_value,
            last_seen={k: v for k, v in last_seen.items()})
        return False


summary = {
    "schema": "syw2plus.g5-order-record-builder-trace.v1",
    "staging_dest": hex(STAGING_DEST), "stack_base": hex(STACK_BASE),
    "targets": {k: hex(v) for k, v in TARGETS.items()},
}
try:
    _field_watches = [FieldWatch(name, address) for name, address in TARGETS.items()]
    _marker = MarkerWatch()
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "targets": summary["targets"]}, handle)
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
