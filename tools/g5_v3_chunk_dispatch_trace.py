#!/usr/bin/env python3
"""Read-only gdb trace for the v3 chunked order-dispatch cave and its crash.

``patches/selection/g5_selection_cap50_v3.py`` splits a >20-unit selection
into up to 3 chunked calls to the original order-record builder body
(``FUN_004AE550``, relocated into a cave). Live testing
(``tools/g5_pending_broadcast_snapshot_probe_v3.py``) crashes with
``Unhandled page fault on read access to 0x02A45AAA at address 0040FEE0``.

Static disassembly of the original EXE (read-only) narrowed the fault: the
instruction at ``0x0040FED0`` is ``movsx ecx, word ptr [esp+4]`` (a *signed*
16-bit slot index) feeding ``word ptr [ecx*0x758*8/... + 0x66bd0a]`` with no
bounds check -- ``0x758`` is the confirmed per-slot unit stride. If the
16-bit value handed to this accessor has its sign bit set (or is otherwise
out of the live slot range), the multiply-by-stride address computation
walks far outside mapped memory, matching the observed fault address.

Static reading of ``FUN_004AE550``'s own body also found that the packed
"slot | (aux << 12)" 16-bit unit-list word it builds (``0x004ae619: mov word
ptr [edi], dx``) derives its high "aux" nibble from an *overlapping,
never-explicitly-initialized* stack read (``0x004ae60f: mov edx, dword ptr
[esp+0x12]``, straddling the just-read handle and the next stack slot up).
In stock (unchunked, single real-caller) execution this is whatever
leftover stack content the true caller left there. The v3 wrapper calls the
*same* relocated body three times in a row via ``call`` at an *identical*
absolute stack depth each time (its own frame is fixed via ``ebp``) -- so
unlike stock, chunk 1 and chunk 2's reads of that same stack address can see
*chunk 0's own leftover local-variable residue* rather than independent
per-session garbage. This trace directly measures, per chunk call:

- the raw packed unit-list word for every valid entry (``dx`` at the store
  site, relocated to ``BODY_ADDR + (0x004ae619 - HOOK_SITE)``);
- the slot argument handed to the suspected crash accessor's entry
  (``0x0040FED0``), across every call site (direct or indirect -- this is a
  function-entry breakpoint, not a call-site one), the instant before the
  unchecked read that would fault;
- the single-target override flag (``word ptr [0x8930a4]``) and its target
  value (``dword ptr [0x8930a0]``) at each of the three cave call sites, to
  rule in/out the override-branch hypothesis in the same run.

All breakpoints are non-invasive (``stop()`` always returns ``False``) so
the game keeps running (and, if the hypothesis is confirmed, still faults)
-- this script only observes.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_V3_CHUNK_TRACE_CONTROL"]
DEADLINE = time.time() + 90

HOOK_SITE = 0x004AE550
CAVE_CALL_SITES = (0x004E4DB2, 0x004E4DE0, 0x004E4E17)  # chunk0, chunk1, chunk2
PACKED_WORD_STORE = 0x004E4E40 + (0x004AE619 - HOOK_SITE)
OVERRIDE_FLAG = 0x008930A4
OVERRIDE_TARGET = 0x008930A0
CRASH_ACCESSOR_ENTRY = 0x0040FED0
SELECTION_COUNT = 0x0108C000

armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")
events_path = os.path.join(CONTROL, "events.jsonl")
summary_path = os.path.join(CONTROL, "trace-summary.json")

state = {
    "call_site_hits": {hex(a): 0 for a in CAVE_CALL_SITES},
    "packed_word_hits": 0,
    "accessor_entry_hits": 0,
    "fatal": None,
}
chunk_counter = {"n": -1}


def read_u16(address):
    return struct.unpack("<H", bytes(gdb.selected_inferior().read_memory(address, 2)))[0]


def read_s16(address):
    return struct.unpack("<h", bytes(gdb.selected_inferior().read_memory(address, 2)))[0]


def read_u32(address):
    return struct.unpack("<I", bytes(gdb.selected_inferior().read_memory(address, 4)))[0]


def reg(name):
    try:
        return int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF
    except Exception:
        return None


def log(event, **fields):
    record = {"event": event, "wall_time": time.time()}
    record.update(fields)
    with open(events_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def return_address():
    try:
        esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
        raw = bytes(gdb.selected_inferior().read_memory(esp, 4))
        return hex(struct.unpack("<I", raw)[0])
    except Exception:
        return None


def caller_backtrace():
    try:
        return gdb.execute("bt 8", to_string=True).splitlines()
    except Exception:
        return []


def region_dump(address, length):
    try:
        raw = bytes(gdb.selected_inferior().read_memory(address, length))
        return raw.hex()
    except Exception as exc:
        return f"error: {exc!r}"


class CaveCallSite(gdb.Breakpoint):
    """Break at each of the three `call original_body` sites in the cave."""

    def __init__(self, address, chunk_index):
        super().__init__("*0x%x" % address, gdb.BP_BREAKPOINT)
        self.address = address
        self.chunk_index = chunk_index

    def stop(self):
        chunk_counter["n"] = self.chunk_index
        state["call_site_hits"][hex(self.address)] += 1
        esp = reg("esp")
        try:
            override_flag = read_u16(OVERRIDE_FLAG)
        except Exception:
            override_flag = None
        try:
            override_target = read_u32(OVERRIDE_TARGET)
        except Exception:
            override_target = None
        # The original body's own frame lands at esp-4 (call's own return
        # push) minus 0xa4 (sub esp,0x94 + 4 pushed registers); the
        # suspected stale-residue dword sits at that frame's +0x10.
        stale_addr = esp - 4 - 0xA4 + 0x10
        try:
            stale_dword = hex(read_u32(stale_addr))
        except Exception:
            stale_dword = None
        log(
            "cave_call_site",
            chunk_index=self.chunk_index,
            call_site=hex(self.address),
            hit_seq=state["call_site_hits"][hex(self.address)],
            esp=hex(esp) if esp is not None else None,
            override_flag=override_flag,
            override_target=hex(override_target) if override_target is not None else None,
            stale_residue_addr=hex(stale_addr),
            stale_residue_dword_before_body=stale_dword,
        )
        return False


class PackedWordStore(gdb.Breakpoint):
    """Break at `mov word ptr [edi], dx` inside the relocated body -- one
    hit per *valid* unit-list entry the body finds this call."""

    def __init__(self):
        super().__init__("*0x%x" % PACKED_WORD_STORE, gdb.BP_BREAKPOINT)

    def stop(self):
        state["packed_word_hits"] += 1
        edx = reg("edx")
        edi = reg("edi")
        ebx = reg("ebx")
        packed = edx & 0xFFFF if edx is not None else None
        log(
            "packed_word_store",
            chunk_index=chunk_counter["n"],
            hit_seq=state["packed_word_hits"],
            packed_word=hex(packed) if packed is not None else None,
            packed_word_low12_slot=(packed & 0xFFF) if packed is not None else None,
            packed_word_high4_aux=((packed >> 12) & 0xF) if packed is not None else None,
            ebx_valid_count_so_far=ebx,
            edi=hex(edi) if edi is not None else None,
        )
        return False


class CrashAccessorEntry(gdb.Breakpoint):
    """Break at the entry of the suspected unchecked slot accessor
    (0x0040FED0) -- catches every caller, direct or indirect, the instant
    before its unbounded `movsx`-then-index read."""

    def __init__(self):
        super().__init__("*0x%x" % CRASH_ACCESSOR_ENTRY, gdb.BP_BREAKPOINT)

    def stop(self):
        state["accessor_entry_hits"] += 1
        esp = reg("esp")
        try:
            arg_raw_u16 = read_u16(esp + 4)
            arg_signed = read_s16(esp + 4)
        except Exception:
            arg_raw_u16 = None
            arg_signed = None
        computed_fault_addr = None
        if arg_signed is not None:
            ecx = arg_signed & 0xFFFFFFFF if arg_signed >= 0 else (arg_signed + (1 << 32))
            # eax = ((ecx*3)<<4 - ecx)*5 ; final = eax*8 + 0x66bd0a, all mod 2**32
            eax = ((ecx * 3) << 4) - ecx
            eax &= 0xFFFFFFFF
            eax = (eax * 5) & 0xFFFFFFFF
            computed_fault_addr = (eax * 8 + 0x66BD0A) & 0xFFFFFFFF
        is_outlier = arg_signed is not None and (arg_signed < 0 or arg_signed > 1200)
        fields = dict(
            chunk_index=chunk_counter["n"],
            hit_seq=state["accessor_entry_hits"],
            arg_raw_u16=hex(arg_raw_u16) if arg_raw_u16 is not None else None,
            arg_signed=arg_signed,
            computed_read_address=hex(computed_fault_addr) if computed_fault_addr is not None else None,
        )
        if is_outlier and state["accessor_entry_hits"] - state.get("_last_outlier_detail_seq", -1000) > 50:
            state["_last_outlier_detail_seq"] = state["accessor_entry_hits"]
            fields["return_address"] = return_address()
            fields["backtrace"] = caller_backtrace()
            fields["region_dumps"] = {
                "queue_0x8931e0_len0x60": region_dump(0x008931E0, 0x60),
                "staging_0x893100_len0x60": region_dump(0x00893100, 0x60),
                "entries_0x108c000_len0x30": region_dump(0x0108C000, 0x30),
            }
        log("crash_accessor_entry", **fields)
        return False


summary = {
    "schema": "syw2plus.g5-v3-chunk-dispatch-trace.v1",
    "cave_call_sites": [hex(a) for a in CAVE_CALL_SITES],
    "packed_word_store": hex(PACKED_WORD_STORE),
    "crash_accessor_entry": hex(CRASH_ACCESSOR_ENTRY),
    "override_flag": hex(OVERRIDE_FLAG),
    "override_target": hex(OVERRIDE_TARGET),
}
try:
    _sites = [CaveCallSite(addr, idx) for idx, addr in enumerate(CAVE_CALL_SITES)]
    _packed = PackedWordStore()
    _accessor = CrashAccessorEntry()
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True}, handle)
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
