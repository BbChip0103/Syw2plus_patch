#!/usr/bin/env python3
"""Read-only gdb trace: snapshot the order-record staging/queue memory
immediately after each of the v3 wrapper's 3 chunked calls to the relocated
order-record-builder body actually stages/dispatches its finished record
(the external call to 0x004A3C10 inside the shared body, relocated once
into the cave since the body is a single copy invoked 3 times as a
subroutine).

lap684 found a real, reproducible ATTACK-only (order type 4) chunked
broadcast failure (candidate ~0/49 sustained vs original 100%) while MOVE
(type 3) is stable 50/50 (lap682). lap685's g5_v3_chunk_dispatch_trace
comparison already showed the builder's own internal packed-word / override
state is byte-identical between MOVE and ATTACK across all 3 chunks -- so
this trace looks one level downstream, at the staging record the builder
hands off after each chunk call, to see whether the 3 back-to-back calls
within a single click each produce an independent staged record or
overwrite/clobber each other before the per-tick consumer (FUN_0x4aec60 per
lap678) can process them.
"""

import gdb
import json
import os
import time


CONTROL = os.environ["G5_V3_STAGING_TRACE_CONTROL"]
DEADLINE = time.time() + 90

# Address right after `call 0x004A3C10` inside the single relocated body
# copy (hit once per chunk call -- 3x per click for a >20 selection).
POST_STAGE_CALL = 0x004E4F37
STAGING_RECORD = 0x00893130
LOCAL_QUEUE_HEAD = 0x008931E8

armed_path = os.path.join(CONTROL, "armed.json")
stop_path = os.path.join(CONTROL, "stop.flag")
events_path = os.path.join(CONTROL, "events.jsonl")
summary_path = os.path.join(CONTROL, "trace-summary.json")

state = {"hits": 0, "fatal": None}


def region_hex(address, length):
    try:
        raw = bytes(gdb.selected_inferior().read_memory(address, length))
        return raw.hex()
    except Exception as exc:
        return f"error: {exc!r}"


def log(event, **fields):
    record = {"event": event, "wall_time": time.time()}
    record.update(fields)
    with open(events_path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


class PostStageCall(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x%x" % POST_STAGE_CALL, gdb.BP_BREAKPOINT)

    def stop(self):
        state["hits"] += 1
        log(
            "post_stage_call",
            hit_seq=state["hits"],
            chunk_index=(state["hits"] - 1) % 3,
            staging_record_hex=region_hex(STAGING_RECORD, 0x60),
            local_queue_head_hex=region_hex(LOCAL_QUEUE_HEAD, 0x64),
        )
        return False


summary = {
    "schema": "syw2plus.g5-v3-staging-snapshot-trace.v1",
    "post_stage_call": hex(POST_STAGE_CALL),
    "staging_record": hex(STAGING_RECORD),
    "local_queue_head": hex(LOCAL_QUEUE_HEAD),
}
try:
    _bp = PostStageCall()
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
