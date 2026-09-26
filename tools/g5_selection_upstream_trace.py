#!/usr/bin/env python3
"""Read-only gdb trace for the G5 selection writer's upstream count.

The drag probe pauses immediately before input.  This script attaches to the
private Wine process, records the stack/register state at the known upstream
loop and caller, then lets the probe perform exactly one drag.  It never
writes game memory and does not install a product patch.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_SELECTION_TRACE_CONTROL"]
LOOP = 0x0041E1D6
COUNT_BUILD = 0x0041DD74
COUNT_GATE = 0x0041E06A
COUNT_LOAD = 0x0041E154
CALLER = 0x0041E220
WRITER = 0x00412D90
SCAN_ENTRY = 0x0041DD51
SCAN_END = 0x0041DD69
INSERT = 0x0041DE76
INSERT_LOOP = 0x0041DE9E
COUNT_CHECK = 0x0041E1BC
HIT_TEST = 0x004384B0
HIT_TEST_RETURNS = (0x0041DFE3, 0x0041E040, 0x0041E114)
HIT_APPEND_LIMIT = 0x0043877A
COUNT_ASSIGN_SITES = (
    0x0041DC5C, 0x0041DC60, 0x0041DC64, 0x0041DD4D, 0x0041DD74,
    0x0041DE51, 0x0041DF55, 0x0041DF7D, 0x0041DFFE, 0x0041E057,
)
BASE = 0x0108C000
DEADLINE = time.time() + 120
MAX_EVENTS = 400

events_path = os.path.join(CONTROL, "upstream-events.jsonl")
summary_path = os.path.join(CONTROL, "upstream-summary.json")
armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")

state = {
    "events": 0,
    "loop_entries": 0,
    "count_build_entries": 0,
    "count_gate_entries": 0,
    "count_load_entries": 0,
    "caller_entries": 0,
    "writer_entries": 0,
    "scan_entry_entries": 0,
    "scan_end_entries": 0,
    "insert_entries": 0,
    "insert_loop_entries": 0,
    "count_check_entries": 0,
    "hit_test_entries": 0,
    "hit_test_returns": 0,
    "hit_append_limit_entries": 0,
    **{f"count_assign_{address:08x}_entries": 0 for address in COUNT_ASSIGN_SITES},
    "fatal": None,
}


def read_bytes(address, size):
    return bytes(gdb.selected_inferior().read_memory(address, size))


def read_u32(address):
    return struct.unpack("<I", read_bytes(address, 4))[0]


def read_pointer_value(address):
    """Best-effort word read used only for runtime provenance."""
    try:
        return read_u32(address)
    except Exception:
        return None


def read_words(address, count):
    """Best-effort contiguous word snapshot for caller-owned buffers."""
    if not isinstance(address, int) or address < 0x10000:
        return None
    return [read_pointer_value(address + index * 4) for index in range(count)]


def frame_registers():
    values = {}
    for name in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp"):
        try:
            values[name] = int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF
        except Exception:
            values[name] = None
    return values


def stack_snapshot(esp):
    values = {}
    for offset in range(0, 0x31, 4):
        try:
            values[f"esp+0x{offset:x}"] = read_u32(esp + offset)
        except Exception:
            values[f"esp+0x{offset:x}"] = None
    return values


def local_selection_snapshot(esp):
    """Read the temporary selection list used by FUN_0041DC40."""
    try:
        return [read_u32(esp + 0x30 + index * 4) for index in range(50)]
    except Exception:
        return None


def backtrace():
    try:
        return gdb.execute("bt 8", to_string=True).splitlines()
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
        current_count = None
        try:
            current_count = read_u32(BASE)
        except Exception:
            pass
        # 0x0041E220 is a per-tick dispatcher.  Its pre-drag count=0 hits are
        # noise and can exhaust the bounded trace before the drag reaches the
        # selection loop.  Keep the post-selection caller state only.
        if self.name == "caller":
            return False
        if state["events"] >= MAX_EVENTS:
            return False
        registers = frame_registers()
        esp = registers.get("esp")
        stack = stack_snapshot(esp) if esp is not None else {}
        state[f"{self.name}_entries"] += 1
        local = local_selection_snapshot(esp) if esp is not None else None
        log(
            f"{self.name}_entry",
            pc="0x%08x" % self.address,
            registers=registers,
            stack=stack,
            return_address=("0x%08x" % stack.get("esp+0x0")
                            if isinstance(stack.get("esp+0x0"), int) else None),
            count_candidates={
                "esp+0x10": stack.get("esp+0x10"),
                "esp+0x14": stack.get("esp+0x14"),
                "esp+0x18": stack.get("esp+0x18"),
                "esp+0x1c": stack.get("esp+0x1c"),
            },
            selection_count=current_count,
            relocated_entries=(
                [read_u32(BASE + 4 + index * 4) for index in range(50)]
                if self.name in {"count_build", "count_gate", "count_load", "loop", "scan_entry", "scan_end", "insert", "insert_loop"}
                else None
            ),
            local_selection=local,
            backtrace=backtrace() if self.name in {"insert", "insert_loop", "count_build", "count_check"} or self.name.startswith("count_assign_") else None,
        )
        return False


class HitTestEntryBreakpoint(gdb.Breakpoint):
    """Capture the seven-argument hit-test call before its prologue mutates ESP."""

    def __init__(self):
        super().__init__("*0x%x" % HIT_TEST, gdb.BP_BREAKPOINT)

    def stop(self):
        if state["events"] >= MAX_EVENTS:
            return False
        registers = frame_registers()
        esp = registers.get("esp")
        if esp is None:
            return False
        return_address = read_pointer_value(esp)
        args = [read_pointer_value(esp + 4 + index * 4) for index in range(7)]
        state["hit_test_entries"] += 1
        log(
            "hit_test_entry",
            pc="0x%08x" % HIT_TEST,
            return_address=("0x%08x" % return_address
                            if isinstance(return_address, int) else None),
            registers=registers,
            arguments=args,
            argument_words=(
                [read_pointer_value(value) if isinstance(value, int) else None
                 for value in args]
            ),
            caller_stack=stack_snapshot(esp),
            selection_count=read_pointer_value(BASE),
            relocated_entries=[
                read_pointer_value(BASE + 4 + index * 4) for index in range(50)
            ],
            backtrace=backtrace(),
        )
        return False


class HitTestReturnBreakpoint(gdb.Breakpoint):
    """Capture the return value and caller-side count immediately after call."""

    def __init__(self, address):
        super().__init__("*0x%x" % address, gdb.BP_BREAKPOINT)
        self.address = address

    def stop(self):
        if state["events"] >= MAX_EVENTS:
            return False
        registers = frame_registers()
        esp = registers.get("esp")
        if esp is None:
            return False
        state["hit_test_returns"] += 1
        # After RET the caller's first pushed argument is at [ESP]; the entry
        # breakpoint saw the same seven arguments at [ESP+4..+0x1c].
        arguments = [read_pointer_value(esp + index * 4) for index in range(7)]
        log(
            "hit_test_return",
            pc="0x%08x" % self.address,
            registers=registers,
            eax=registers.get("eax"),
            arguments=arguments,
            argument_words=(
                [read_pointer_value(value) if isinstance(value, int) else None
                 for value in arguments]
            ),
            first_argument_buffer=(
                read_words(arguments[0], 50) if arguments else None
            ),
            second_argument_words=(
                read_words(arguments[1], 4) if len(arguments) > 1 else None
            ),
            caller_stack=stack_snapshot(esp),
            caller_count_candidates={
                "esp+0x10": read_pointer_value(esp + 0x10),
                "esp+0x14": read_pointer_value(esp + 0x14),
                "esp+0x18": read_pointer_value(esp + 0x18),
                "esp+0x1c": read_pointer_value(esp + 0x1c),
                "esp+0x2c": read_pointer_value(esp + 0x2c),
            },
            selection_count=read_pointer_value(BASE),
            relocated_entries=[
                read_pointer_value(BASE + 4 + index * 4) for index in range(50)
            ],
            backtrace=backtrace(),
        )
        return False


class HitAppendLimitBreakpoint(gdb.Breakpoint):
    """Capture the helper's exact 20-entry compare before changing any bytes."""

    def __init__(self):
        super().__init__("*0x%x" % HIT_APPEND_LIMIT, gdb.BP_BREAKPOINT)

    def stop(self):
        if state["events"] >= MAX_EVENTS:
            return False
        registers = frame_registers()
        ebp = registers.get("ebp")
        state["hit_append_limit_entries"] += 1
        log(
            "hit_append_limit",
            pc="0x%08x" % HIT_APPEND_LIMIT,
            registers=registers,
            compare_left=registers.get("eax"),
            compare_right=(
                struct.unpack("<H", read_bytes(HIT_APPEND_LIMIT + 2, 2))[0]
            ),
            count_pointer=("0x%08x" % ebp if isinstance(ebp, int) else None),
            count_value=(read_pointer_value(ebp) if isinstance(ebp, int) else None),
            selection_count=read_pointer_value(BASE),
            backtrace=backtrace(),
        )
        return False


summary = {
    "schema": "syw2plus.g5-selection-upstream-trace.v1",
    "loop_address": "0x%08x" % LOOP,
    "count_build_address": "0x%08x" % COUNT_BUILD,
    "count_gate_address": "0x%08x" % COUNT_GATE,
    "count_load_address": "0x%08x" % COUNT_LOAD,
    "caller_address": "0x%08x" % CALLER,
    "writer_address": "0x%08x" % WRITER,
    "scan_entry_address": "0x%08x" % SCAN_ENTRY,
    "scan_end_address": "0x%08x" % SCAN_END,
    "insert_address": "0x%08x" % INSERT,
    "insert_loop_address": "0x%08x" % INSERT_LOOP,
    "count_check_address": "0x%08x" % COUNT_CHECK,
    "count_assign_addresses": ["0x%08x" % address for address in COUNT_ASSIGN_SITES],
    "selection_base": "0x%08x" % BASE,
}
try:
    gdb.execute("set can-use-hw-watchpoints 1")
    loop = EntryBreakpoint("loop", LOOP)
    count_build = EntryBreakpoint("count_build", COUNT_BUILD)
    count_gate = EntryBreakpoint("count_gate", COUNT_GATE)
    count_load = EntryBreakpoint("count_load", COUNT_LOAD)
    caller = EntryBreakpoint("caller", CALLER)
    writer = EntryBreakpoint("writer", WRITER)
    scan_entry = EntryBreakpoint("scan_entry", SCAN_ENTRY)
    scan_end = EntryBreakpoint("scan_end", SCAN_END)
    insert = EntryBreakpoint("insert", INSERT)
    insert_loop = EntryBreakpoint("insert_loop", INSERT_LOOP)
    count_check = EntryBreakpoint("count_check", COUNT_CHECK)
    count_assign = [
        EntryBreakpoint("count_assign_%08x" % address, address)
        for address in COUNT_ASSIGN_SITES
    ]
    hit_test = HitTestEntryBreakpoint()
    hit_test_returns = [HitTestReturnBreakpoint(address) for address in HIT_TEST_RETURNS]
    hit_append_limit = HitAppendLimitBreakpoint()
    info = gdb.execute("info breakpoints", to_string=True)
    summary["breakpoints_after_arm"] = info
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "breakpoints": [hex(LOOP), hex(COUNT_BUILD),
                       hex(COUNT_GATE), hex(COUNT_LOAD), hex(CALLER), hex(WRITER),
                       hex(SCAN_ENTRY), hex(SCAN_END), hex(INSERT), hex(INSERT_LOOP),
                       hex(COUNT_CHECK), hex(HIT_TEST), *[hex(address) for address in COUNT_ASSIGN_SITES],
                       *[hex(address) for address in HIT_TEST_RETURNS], hex(HIT_APPEND_LIMIT)]}, handle)
    gdb.execute("continue")
    while time.time() < DEADLINE and not os.path.exists(stop_path):
        if state["events"] >= MAX_EVENTS:
            summary["stop_reason"] = "event_limit"
            break
        try:
            gdb.execute("continue")
        except gdb.error as exc:
            summary["continue_error"] = repr(exc)
            break
    summary.setdefault("stop_reason", "stop_flag" if os.path.exists(stop_path) else "deadline")
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
