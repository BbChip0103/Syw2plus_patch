#!/usr/bin/env python3
"""Read-only gdb trace of every call into the v3 order-record builder hook.

lap680 found the crash and fixed it (candidate `e5004764...bac3de6977`), and
confirmed ATTACK-toolbar+ground-click reaches ``+0x384`` pending 50/50 on the
fixed candidate -- but the *same* click mechanics for a plain right-click
MOVE order land at pending 0/50 (five consecutive post-click snapshots, and
``command==3`` also 0 after a 0.3s wait). ``patches/selection/
g5_selection_cap50_v3.py``'s own docstring claims MOVE and ATTACK both reach
the hooked order-record builder (``FUN_004AE550``, now a five-byte near jump
to the cave) with order-type header words 3 and 4 respectively -- this trace
tests that claim directly and cheaply, without touching game bytes.

The hook site itself (``0x004AE550``) is executed exactly once per call
regardless of which branch the wrapper takes afterward (chunked or
fall-through), and the type-header word the wrapper reads
(``movzx eax, word ptr [esp+8]``) is still sitting on the stack unmodified at
that address (the near jump does not touch the stack). Breaking there and
reading ``word ptr [esp+8]`` plus the live selection count at
``SELECTION_BASE`` for every hit answers, without any inference:

- does a MOVE click reach this function *at all* (hit count during the MOVE
  phase's action window);
- if it does, what type header value it carries, and whether the live
  selection count at that instant would send it down the chunking branch
  (count > 20) or the unchunked fall-through (count <= 20, or an
  unrecognised type).

All breakpoints are non-invasive (``stop()`` always returns ``False``): the
game keeps running normally, click input is unaffected, and no game memory
is ever written by this script.
"""

import gdb
import json
import os
import time


CONTROL = os.environ["G5_V3_ORDER_TYPE_HEADER_CONTROL"]
DEADLINE = time.time() + 120

HOOK_SITE = 0x004AE550
SELECTION_BASE = 0x0108C000
CHUNK_UNITS = 20
REAL_ORDER_TYPES = {1, 3, 4, 7, 8, 9}

armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")
marker_path = os.path.join(CONTROL, "click_marker.flag")
events_path = os.path.join(CONTROL, "events.jsonl")
summary_path = os.path.join(CONTROL, "trace-summary.json")

state = {"hits": 0, "post_marker_hits": 0, "fatal": None}
MAX_POST_MARKER_EVENTS = 20


def read_u16(inferior, address):
    return int.from_bytes(bytes(inferior.read_memory(address, 2)), "little")


def read_u32(inferior, address):
    return int.from_bytes(bytes(inferior.read_memory(address, 4)), "little")


def reg(name):
    try:
        return int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF
    except Exception:
        return None


class HookSiteHit(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x%x" % HOOK_SITE, gdb.BP_BREAKPOINT)

    def stop(self):
        state["hits"] += 1
        inferior = gdb.selected_inferior()
        esp = reg("esp")
        try:
            type_header = read_u16(inferior, esp + 8) if esp is not None else None
        except Exception:
            type_header = None
        try:
            selection_count = read_u32(inferior, SELECTION_BASE)
        except Exception:
            selection_count = None
        after_marker = os.path.exists(marker_path)
        if after_marker and state["post_marker_hits"] < MAX_POST_MARKER_EVENTS:
            state["post_marker_hits"] += 1
            record = {
                "hit_seq": state["hits"],
                "post_marker_seq": state["post_marker_hits"],
                "wall_time": time.time(),
                "esp": hex(esp) if esp is not None else None,
                "type_header": type_header,
                "is_real_order_type": type_header in REAL_ORDER_TYPES if type_header is not None else None,
                "selection_count": selection_count,
                "would_chunk": (
                    type_header in REAL_ORDER_TYPES and selection_count is not None
                    and selection_count > CHUNK_UNITS
                ) if type_header is not None else None,
            }
            with open(events_path, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
                handle.flush()
        return False


summary = {"schema": "syw2plus.g5-v3-order-type-header-trace.v1", "hook_site": hex(HOOK_SITE)}
try:
    _bp = HookSiteHit()
    with open(armed_path, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "hook_site": hex(HOOK_SITE)}, handle)
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
