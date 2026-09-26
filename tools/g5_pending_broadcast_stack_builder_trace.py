#!/usr/bin/env python3
"""Read-only gdb traces for the G5 order-record stack builder.

``g5_pending_broadcast_staging_probe.py`` found that a 60-byte "pending
order" record is assembled on the stack and then copied wholesale (``rep
movsd``, PC ``0x4a3c39``) into a global staging buffer at ``0x893130``. That
copy is the destination side; the *source* stack address changes every
process run, so no static address can be watched directly, and it must be
learned live before the code that fills it can be watched.

This module holds two gdb ``--batch -x`` entry points, run as two separate
gdb attach sessions against the same live pid (never as breakpoints created
from inside another breakpoint's own ``stop()`` callback -- an earlier,
single-session version of this trace that created new hardware watchpoints
and self-deleted from within a watchpoint's ``stop()`` crashed gdb itself
with a SIGSEGV internal to the debugger, not the debuggee):

``learn`` -- arms one watchpoint on ``0x893130`` (the copy-out
destination), and on the first hit computes ``stack_base = esi_at_trap - 4``
(``rep movsd`` auto-increments ``esi`` past the dword it just wrote). Its
``stop()`` returns ``True`` so ``gdb.execute("continue")`` returns control
to the top level immediately after one hit; the script then detaches
(leaving the debuggee running) and exits cleanly.

``fields`` -- reads the learned ``stack_base`` from the control directory
(written by ``learn``), arms three watchpoints on that address (the
record's unit-count field at ``+0xa`` and its first/last unit-list words at
``+0x14``/``+0x3a``) *before* ever calling ``continue`` (the same safe,
proven pattern as ``g5_pending_broadcast_writer_trace.py``), then loops
non-invasively (every ``stop()`` returns ``False``) until a stop-flag file
appears, recording PC/backtrace/registers for each hit.

Both scripts are read-only observation: they never write game memory or
alter control flow beyond the temporary breaks needed to take one memory
snapshot per hit.
"""

import gdb
import json
import os
import struct
import sys
import time


MODE = os.environ["G5_STACK_BUILDER_TRACE_MODE"]
CONTROL = os.environ["G5_STACK_BUILDER_TRACE_CONTROL"]
DEADLINE = time.time() + 60
STAGING_DEST = 0x00893130
MAX_SAMPLES = 30

armed_path = os.path.join(CONTROL, "armed-%s.json" % MODE)
stop_path = os.path.join(CONTROL, "stop.flag")
base_found_path = os.path.join(CONTROL, "base-found.json")
events_path = os.path.join(CONTROL, "builder-events.jsonl")
summary_path = os.path.join(CONTROL, "trace-summary-%s.json" % MODE)


def read_u32(address):
    return struct.unpack("<I", bytes(gdb.selected_inferior().read_memory(address, 4)))[0]


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


def caller_backtrace():
    try:
        return gdb.execute("bt 10", to_string=True).splitlines()
    except Exception:
        return []


def esp_word():
    try:
        esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
        return hex(read_u32(esp))
    except Exception:
        return None


def log(event, **fields):
    record = {"event": event, "wall_time": time.time()}
    record.update(fields)
    with open(events_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def run_learn():
    state = {"hits": 0, "stack_base": None, "fatal": None}

    class StagingDestWatch(gdb.Breakpoint):
        def __init__(self):
            super().__init__("*(int*)0x%x" % STAGING_DEST, gdb.BP_WATCHPOINT, gdb.WP_WRITE)

        def stop(self):
            state["hits"] += 1
            try:
                esi = int(gdb.selected_frame().read_register("esi")) & 0xFFFFFFFF
                base = (esi - 4) & 0xFFFFFFFF
            except Exception as exc:
                state["fatal"] = repr(exc)
                return True
            state["stack_base"] = hex(base)
            log("phase1_learned_base", stack_base=hex(base), esi_at_trap=hex(esi),
                registers=frame_registers())
            with open(base_found_path, "w", encoding="utf-8") as handle:
                json.dump({"stack_base": hex(base)}, handle)
            return True

    summary = {"schema": "syw2plus.g5-pending-broadcast-stack-builder-learn.v1",
               "staging_dest": hex(STAGING_DEST)}
    try:
        StagingDestWatch()
        with open(armed_path, "w", encoding="utf-8") as handle:
            json.dump({"armed": True}, handle)
        gdb.execute("continue")
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


def run_fields():
    """Watch the learned stack address, correlated against the 0x893130 copy-out.

    The stack slot at ``stack_base`` turned out to be an extremely hot,
    generically-reused scratch location (thousands of unrelated writes per
    second from unrelated per-tick code, not just the order builder), so a
    plain "first N hits" capture is pure noise. The genuine order-builder
    write to each field is, by construction, the *last* write to that address
    before the record gets copied out via ``rep movsd`` to ``0x893130`` (the
    already-confirmed, low-frequency, order-specific marker from the
    ``learn`` pass) -- anything written after that and before the copy would
    corrupt the very record the game is about to broadcast. So this only
    keeps a cheap rolling "most recent write" per field (no backtrace, no
    per-hit file I/O) and snapshots those into one log entry each time the
    marker fires.
    """
    with open(base_found_path, "r", encoding="utf-8") as handle:
        base = int(json.load(handle)["stack_base"], 16)

    state = {"hits": {}, "marker_hits": 0, "fatal": None}
    targets = {
        "count_field_0xa": base + 0xA,
        "list_entry_0": base + 0x14,
        "list_entry_19": base + 0x14 + 19 * 2,
    }
    last_seen: dict[str, dict] = {name: None for name in targets}
    for name in targets:
        state["hits"][name] = 0

    class BuilderFieldWatch(gdb.Breakpoint):
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

    class StagingMarkerWatch(gdb.Breakpoint):
        def __init__(self):
            super().__init__("*(int*)0x%x" % STAGING_DEST, gdb.BP_WATCHPOINT, gdb.WP_WRITE)

        def stop(self):
            state["marker_hits"] += 1
            log("correlated_order_issue", marker_hit_seq=state["marker_hits"],
                last_seen={k: v for k, v in last_seen.items()})
            return False

    summary = {"schema": "syw2plus.g5-pending-broadcast-stack-builder-fields.v2",
               "stack_base": hex(base), "targets": {k: hex(v) for k, v in targets.items()}}
    try:
        _watches = [BuilderFieldWatch(name, address) for name, address in targets.items()]
        _marker = StagingMarkerWatch()
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


if MODE == "learn":
    run_learn()
elif MODE == "fields":
    run_fields()
else:
    sys.stderr.write("unknown G5_STACK_BUILDER_TRACE_MODE=%r\n" % MODE)
