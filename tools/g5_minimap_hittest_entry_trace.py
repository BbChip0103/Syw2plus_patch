#!/usr/bin/env python3
"""Read-only gdb entry-count trace for the minimap click hit-test candidate.

lap762 static disassembly of the protected original found the actual mouse
-> minimap-region -> world-coordinate routing chain the operator asked for
(2026-09-29 12:37 direction). The click router at ``0x41e3xx-0x41e60c``
reads the last mouse position (``0x4ed814``/``0x4ed816``) and first tries
the minimap widget's own hit-test method, ``FUN_004516A0`` (``this`` =
``0x00639350``, the same widget lap759 confirmed is constructed exactly once
at new-game start). Only if that test fails does the router fall back to
the main-viewport hit-test (``0x00417db0``, already well-characterised by
``tools/g5_screen_world_calibration.py``).

``FUN_004516A0`` disassembly (args: mouse_x, mouse_y, &out_tile_x,
&out_tile_y; this=widget):

    - Bounds-checks mouse_x in [widget.x, widget.x+0xB4] and mouse_y in
      (widget.y, widget.y+0x5A] -- i.e. screen x in [0,180], y in (509,599]
      for this session's widget (0, 509) -- this matches the "diamond" HUD
      region lap710 already click-tested (x in [0,176], y in [511,598]) and
      found to have zero effect.
    - If in bounds, looks up two per-pixel LUT bytes at ``this+0x13eea`` and
      ``this+0x1bd7a`` (isometric screen-offset -> tile-index tables baked
      by a *separate* minimap-bitmap-generation routine, not the ctor lap759
      traced).
    - Returns 1 (success, tile coords written to the out-pointers) unless
      *either* LUT byte reads the sentinel ``0xFF`` ("outside the diamond
      map render"), in which case it returns 0 (fail) at ``0x00451728``.

This trace counts entries to ``0x004516A0`` (logging the mouse_x/mouse_y
args) and hits to the two return sites (``0x0045171D`` success epilogue,
``0x00451728`` fail epilogue) so a live click on the HUD region can show (a)
whether this hit-test function is ever reached by real input at all, and
(b) whether it is reached but always takes the fail path (LUT sentinel),
narrowing the root cause from "renderer not found" to "hit-test reached but
its LUT was never baked with real tile data".

lap763 follow-up (2026-09-29 12:57 operator direction, "1 lap 연장, no further
extension"): lap762 found that ``FUN_004516A0`` is reached zero times even
though the WM enqueue (24 hits) and per-tick dequeue (19086 hits) both fire,
and narrowed the cause to "one of three filter branches in the click router
body between dequeue and the hit-test call". Static re-disassembly of the
protected original this lap (``objdump -M intel -D`` around
``0x41e260``-``0x41e60c``) resolved exactly what those three branches do and
found they are *not* independent alternative gates -- they are sequential
code on one straight-line path:

  * ``0x41e332`` (``cmp byte [esp+0x13],0x1``) and the ``0x41e365``
    (``cmp si,bx``) region only select between two ways of computing a
    screen-edge scroll-cursor region code that is pushed and passed to
    ``call 0x437510`` (a cursor-icon setter) -- neither one can skip the
    hit-test call; every path through this block falls through to the same
    next instruction.
  * The *only* instruction whose return value gates whether
    ``FUN_004516A0`` is ever called is ``call 0x41c450`` at ``0x41e43d``:
    ``test eax,eax; je 0x41e4c1`` -- if it returns 0, execution jumps
    straight to the *fallback* main-viewport hit-test path (``0x417db0``)
    and ``FUN_004516A0`` is skipped entirely; only a non-zero return falls
    through to set up args and call ``FUN_004516A0`` at ``0x41e464``.
  * ``0x41c450`` itself (disassembled this lap) is a short predicate: it
    returns 1 if a per-"mode" table entry at
    ``[(mode_index*15036)+0x959af6]`` (``mode_index`` = dword at
    ``0xb63fc4``) equals 1, OR the word at ``0xb631ec`` equals 1, OR the
    dword at ``0x97597c`` is non-zero; otherwise it returns 0. These read
    like UI-mode/dialog-active flags, not rendering state.

This lap adds four breakpoints to answer the operator's literal question
empirically instead of by disassembly alone: does a real click in this
environment reach ``0x41c450``, and what does it return (captured at
``0x41e442``, right after the call, before ``test eax,eax`` consumes
``eax``)? The two upstream "filter" addresses the operator named
(``0x41e332``, ``0x41e365``) are also instrumented so their hit counts and
the mode-gate inputs can be cross-checked against the static reading above
rather than assumed.

Non-invasive: every ``stop()`` returns ``False`` so control flow is never
actually halted for the player, and no game memory is written.
"""

import gdb
import json
import os
import struct
import time


CONTROL = os.environ["G5_MINIMAP_HITTEST_TRACE_CONTROL"]
DEADLINE = time.time() + float(os.environ.get("G5_MINIMAP_HITTEST_TRACE_DEADLINE", "180"))

CANDIDATES = {
    "hittest_entry_FUN_004516A0": 0x004516A0,
    "hittest_success_ret_0x45171D": 0x0045171D,
    "hittest_fail_ret_0x451728": 0x00451728,
    # lap762 follow-up: 0x4216b0 is the low-level WM_LBUTTONDOWN/UP,
    # WM_RBUTTONDOWN/UP handler's mouse-event-ring-buffer enqueue call (see
    # tools/g5_minimap_click_hittest_probe.py docstring). 0x41e299 is the
    # click-router's dequeue call (same ring buffer, via FUN_004217B0) that
    # gates whether the router ever reaches the minimap hit-test at all.
    "input_enqueue_FUN_004216B0": 0x004216B0,
    "click_router_dequeue_call_0x41e299": 0x0041E299,
    # lap763 follow-up (2026-09-29 12:57 direction): the three filter points
    # named by the operator, plus the gate call's own entry so its inputs
    # can be read directly instead of inferred from the static table-lookup
    # formula alone.
    "router_button_type_filter_0x41e332": 0x0041E332,
    "router_coord_sentinel_filter_0x41e365": 0x0041E365,
    "router_gate_entry_0x41c450": 0x0041C450,
    "router_gate_return_check_0x41e442": 0x0041E442,
}

MODE_INDEX_VA = 0x00B63FC4
MODE_TABLE_BASE = 0x00959AF6
MODE_TABLE_STRIDE = 15036  # ecx*3759*4, derived from the shl/sub sequence at 0x41c450-0x41c469
FLAG_B631EC_VA = 0x00B631EC
FLAG_97597C_VA = 0x0097597C


def read_u32(addr):
    try:
        raw = bytes(gdb.selected_inferior().read_memory(addr, 4))
        return struct.unpack("<I", raw)[0]
    except Exception as exc:
        return f"<error: {exc!r}>"


def read_u16(addr):
    try:
        raw = bytes(gdb.selected_inferior().read_memory(addr, 2))
        return struct.unpack("<H", raw)[0]
    except Exception as exc:
        return f"<error: {exc!r}>"


def read_u8(addr):
    try:
        raw = bytes(gdb.selected_inferior().read_memory(addr, 1))
        return raw[0]
    except Exception as exc:
        return f"<error: {exc!r}>"


def gate_inputs():
    """Read the three operands 0x41c450 branches on, matching the disassembly:
    mode-indexed table word == 1, OR word@0xb631ec == 1, OR dword@0x97597c != 0."""
    mode_index = read_u32(MODE_INDEX_VA)
    table_word = None
    if isinstance(mode_index, int):
        table_word = read_u16(MODE_TABLE_BASE + mode_index * MODE_TABLE_STRIDE)
    return {
        "mode_index_0xb63fc4": mode_index,
        "mode_table_word": table_word,
        "flag_0xb631ec": read_u16(FLAG_B631EC_VA),
        "flag_0x97597c": read_u32(FLAG_97597C_VA),
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


def entry_args():
    """At entry to FUN_004516A0 (before its own prologue pushes), the stack
    is [esp+0]=return_addr, [esp+4]=mouse_x (word, sign-extended into a
    pushed dword), [esp+8]=mouse_y, [esp+0xc]=out_x_ptr, [esp+0x10]=out_y_ptr."""
    try:
        esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
        raw = bytes(gdb.selected_inferior().read_memory(esp, 0x14))
        _ret, mouse_x, mouse_y, out_x_ptr, out_y_ptr = struct.unpack("<IiiII", raw)
        return {"mouse_x": mouse_x, "mouse_y": mouse_y,
                "out_x_ptr": hex(out_x_ptr), "out_y_ptr": hex(out_y_ptr)}
    except Exception as exc:
        return {"error": repr(exc)}


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
        if state[self.name] <= 80:
            fields = {"name": self.name, "pc": "0x%08x" % self.address,
                       "registers": frame_registers(), "return_address": return_address()}
            if self.address == 0x004516A0:
                fields["args"] = entry_args()
            elif self.address == 0x0041E332:
                # cmp byte [esp+0x13],0x1 -- the operator's "button type" filter.
                try:
                    esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
                    fields["button_type_byte_esp_0x13"] = read_u8(esp + 0x13)
                except Exception as exc:
                    fields["button_type_byte_esp_0x13"] = f"<error: {exc!r}>"
            elif self.address == 0x0041E365:
                # cmp si,bx -- the operator's "coord sentinel" filter. si/bx are
                # the low 16 bits of esi/ebx at this point in the disassembly.
                regs = frame_registers()
                fields["si_low16_of_esi"] = regs.get("esi")
                fields["bx_low16_of_ebx"] = regs.get("ebx")
            elif self.address == 0x0041C450:
                fields["gate_inputs"] = gate_inputs()
            elif self.address == 0x0041E442:
                # right after `call 0x41c450`, before `test eax,eax` consumes it:
                # eax IS the gate's return value (1=continue to hit-test, 0=skip it).
                fields["gate_return_eax"] = frame_registers().get("eax")
            else:
                fields["backtrace"] = caller_backtrace()
            log("entry", **fields)
        return False


summary = {
    "schema": "syw2plus.g5-minimap-hittest-entry-trace.v1",
    "candidates": {name: hex(address) for name, address in CANDIDATES.items()},
}
try:
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
