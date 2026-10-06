#!/usr/bin/env python3
"""Read-only live trace for the G1 terrain/pixel-writer attribution.

The script attaches to the private Wine game process, records the pinned
terrain draw/cache entries and renderer primitive call stacks, and arms three
hardware write watchpoints inside the fixed 832x512 terrain buffer.  It never
writes game memory or the protected executable.  Watchpoints are only armed
after the loaded-scene state is observable so menu writes cannot be mistaken
for terrain evidence.
"""

import gdb
import hashlib
import json
import os
import struct
import time


CONTROL = os.environ["G1_TERRAIN_WRITER_TRACE_CONTROL"]
DEADLINE = time.time() + float(os.environ.get("G1_TERRAIN_WRITER_TRACE_DEADLINE", "120"))
EVENTS = os.path.join(CONTROL, "writer-events.jsonl")
SUMMARY = os.path.join(CONTROL, "writer-summary.json")
ARMED = os.path.join(CONTROL, "armed.json")
STOP = os.path.join(CONTROL, "stop.flag")
RENDERER = 0x00E5BF18
PROGRAM_STATE = 0x004ED818
GLOBAL_TICK = 0x009B5210
TERRAIN_BUFFER = 0x00BA3D30
TERRAIN_WIDTH = 832
TERRAIN_HEIGHT = 512

# Three deterministic points span the fixed terrain cache.  They are probe
# coordinates, not a claim that every point is written on every redraw.
TERRAIN_POINTS = ((64, 64), (416, 256), (768, 448))
TERRAIN_ENTRIES = {
    "terrain_draw_0x4324e0": 0x004324E0,
    "terrain_cache_0x433019": 0x00433019,
    "terrain_overlay_0x4332f0": 0x004332F0,
}
MAX_ENTRY_SAMPLES = 16
MAX_ASSET_SAMPLES = 256
ASSET_ENTRY = 0x00435400
ASSET_CALLS = {
    "full_0x435593": (0x00435593, 12),
    "clipped_0x4355d7": (0x004355D7, 16),
    "fog_0x43561e": (0x0043561E, 16),
    "tinted_0x435662": (0x00435662, 16),
    "caller_0x435910": (0x00435910, 12),
    "caller_0x435959": (0x00435959, 16),
}
ASSET_BASE_TABLE = 0x00B65E8C
ASSET_OFFSET_TABLE = 0x00B65758
ASSET_FILE_STRIDE = 0xBF8
ASSET_FRAME_STRIDE = 0x2FE
ASSET_DIGEST_BYTES = 128

TARGETS = {
    "terrain_context_0x403b20": 0x00403B20,
    "object_copy_0x403c10": 0x00403C10,
    "rle_clip_0x466d50": 0x00466D50,
    "rle_plain_0x4664d0": 0x004664D0,
    "rect_fill_0x465e80": 0x00465E80,
    "block_copy_0x466280": 0x00466280,
    "rect_border_0x465b30": 0x00465B30,
    "rle_tinted_clip_0x466540": 0x00466540,
    "rle_tinted_0x466ea0": 0x00466EA0,
    "set_pixel_0x4658e0": 0x004658E0,
}

state = {
    "events": 0,
    "entries": {name: 0 for name in {**TARGETS, **TERRAIN_ENTRIES}},
    "watchpoints_armed": 0,
    "watchpoint_hits": 0,
    "fatal": None,
    "asset_events": 0,
    "asset_entry_events": 0,
    "asset_call_events": 0,
    "asset_equality": {"true": 0, "false": 0, "unknown": 0},
}
watchpoints = []
asset_by_source = {}


def as_int(value):
    try:
        return int(value, 16) if isinstance(value, str) else int(value)
    except (TypeError, ValueError):
        return None


def digest_memory(address, amount=ASSET_DIGEST_BYTES):
    if not isinstance(address, int) or address < 0x10000 or address >= 0x80000000:
        return {"status": "UNKNOWN", "reason": "pointer outside user image", "address": address}
    try:
        raw = read_bytes(address, amount)
    except Exception as exc:
        return {"status": "UNKNOWN", "reason": repr(exc), "address": hex(address)}
    return {"status": "PASS", "address": hex(address), "bytes": len(raw),
            "sha256": hashlib.sha256(raw).hexdigest(), "prefix_hex": raw[:16].hex()}


def asset_table_lookup(tile_file, frame):
    """Recompute the protected-original table expression independently."""
    if tile_file is None or frame is None or tile_file < 0 or frame < 0:
        return {"status": "UNKNOWN", "reason": "negative-or-missing-key",
                "tile_file": tile_file, "frame": frame}
    if tile_file >= 0x1000 or frame >= ASSET_FRAME_STRIDE:
        return {"status": "UNKNOWN", "reason": "key-out-of-bounds",
                "tile_file": tile_file, "frame": frame}
    try:
        base_slot = ASSET_BASE_TABLE + tile_file * ASSET_FILE_STRIDE
        base = read_u32(base_slot)
        index = tile_file * ASSET_FRAME_STRIDE + frame
        offset_slot = ASSET_OFFSET_TABLE + index * 4
        offset = read_u32(offset_slot)
        source = (base + offset) & 0xFFFFFFFF
        return {"status": "PASS", "tile_file": tile_file, "frame": frame,
                "index": index, "base_slot": hex(base_slot), "base": hex(base),
                "offset_slot": hex(offset_slot), "offset": hex(offset),
                "computed_source": hex(source), "source_digest": digest_memory(source)}
    except Exception as exc:
        return {"status": "UNKNOWN", "reason": repr(exc),
                "tile_file": tile_file, "frame": frame}


def log_asset_event(event, **fields):
    state["asset_events"] += 1
    log(event, **fields)


def record_asset_call(name, source_stack_offset):
    stack = stack_args(8)
    try:
        esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
        pushed_source = read_u32(esp + source_stack_offset)
    except Exception as exc:
        pushed_source = None
        stack["source_read_error"] = repr(exc)
    match = asset_by_source.get(pushed_source)
    equality = "unknown"
    if match is not None:
        equality = "true" if as_int(match["computed_source"]) == pushed_source else "false"
    state["asset_call_events"] += 1
    state["asset_equality"][equality] += 1
    log_asset_event("asset_blitter_call", call_site=name,
                    address=hex(ASSET_CALLS[name][0]),
                    pushed_source=hex(pushed_source) if isinstance(pushed_source, int) else None,
                    pushed_source_digest=digest_memory(pushed_source),
                    matching_entry=match, table_equality=equality,
                    registers=registers(), scene=scene_context(),
                    renderer=renderer_context(), stack=stack,
                    backtrace=backtrace())


def read_bytes(address, size):
    return bytes(gdb.selected_inferior().read_memory(address, size))


def read_u32(address):
    return struct.unpack("<I", read_bytes(address, 4))[0]


def safe_u32(address):
    try:
        return read_u32(address)
    except Exception as exc:
        return {"error": repr(exc)}


def registers():
    result = {}
    for name in ("eax", "ebx", "ecx", "edx", "esi", "edi", "esp", "ebp"):
        try:
            result[name] = hex(int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF)
        except Exception:
            result[name] = None
    return result


def pc():
    try:
        return hex(int(gdb.selected_frame().pc()) & 0xFFFFFFFF)
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
    with open(EVENTS, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
        handle.flush()


def stack_args(count):
    try:
        esp = int(gdb.selected_frame().read_register("esp")) & 0xFFFFFFFF
        raw = read_bytes(esp, 4 * (count + 1))
        values = struct.unpack("<%dI" % (count + 1), raw)
        return {"return_address": hex(values[0]),
                "args": [hex(value) for value in values[1:]]}
    except Exception as exc:
        return {"error": repr(exc)}


def scene_context():
    state_value = safe_u32(PROGRAM_STATE)
    tick = safe_u32(GLOBAL_TICK)
    return {"program_state": state_value, "game_tick": tick}


def renderer_context():
    try:
        buffer = read_u32(RENDERER + 0x1514)
        stride = read_u32(RENDERER + 0x10)
        height = read_u32(RENDERER + 0x08)
        return {"buffer": hex(buffer), "stride": stride, "height": height}
    except Exception as exc:
        return {"error": repr(exc)}


def remove_watchpoint(watch):
    try:
        watch.delete()
    except Exception:
        pass
    if watch in watchpoints:
        watchpoints.remove(watch)


class TerrainWatch(gdb.Breakpoint):
    def __init__(self, address, point, origin):
        super().__init__("*(unsigned char*)0x%x" % address,
                         gdb.BP_WATCHPOINT, gdb.WP_WRITE)
        self.address = address
        self.point = point
        self.origin = origin

    def stop(self):
        state["watchpoint_hits"] += 1
        log("terrain_buffer_write", address=hex(self.address), point=self.point,
            origin=self.origin, writer_eip=pc(), registers=registers(),
            scene=scene_context(), renderer=renderer_context(),
            buffer_range={"base": hex(TERRAIN_BUFFER),
                          "end": hex(TERRAIN_BUFFER + TERRAIN_WIDTH * TERRAIN_HEIGHT)},
            source_candidates={name: safe_u32(int(value, 16))
                               for name, value in registers().items()
                               if name in {"eax", "ecx", "edx", "esi", "edi"}},
            backtrace=backtrace())
        # Do not delete the currently-dispatched watchpoint from its own
        # callback: GDB can crash internally while resuming a Wine inferior.
        # Disabling is equivalent for this bounded trace and cleanup removes
        # the object after the inferior is detached.
        self.enabled = False
        return False


def maybe_arm_terrain_watchpoints(origin):
    if watchpoints:
        return
    if len(TERRAIN_POINTS) != 3:
        log("terrain_watch_arm_failed", error="expected exactly three fixed points")
        return
    scene = scene_context()
    if scene.get("program_state") != 3 or not isinstance(scene.get("game_tick"), int):
        return
    try:
        for x, y in TERRAIN_POINTS:
            address = TERRAIN_BUFFER + y * TERRAIN_WIDTH + x
            watch = TerrainWatch(address, {"x": x, "y": y}, origin)
            watchpoints.append(watch)
        state["watchpoints_armed"] += len(TERRAIN_POINTS)
        log("terrain_watchpoints_armed", addresses=[hex(item.address) for item in watchpoints],
            points=[item.point for item in watchpoints], origin=origin, scene=scene,
            buffer={"base": hex(TERRAIN_BUFFER), "width": TERRAIN_WIDTH,
                    "height": TERRAIN_HEIGHT,
                    "end_exclusive": hex(TERRAIN_BUFFER + TERRAIN_WIDTH * TERRAIN_HEIGHT)})
    except (ValueError, gdb.error) as exc:
        log("terrain_watch_arm_failed", error=repr(exc))


class Entry(gdb.Breakpoint):
    def __init__(self, name, address):
        super().__init__("*0x%x" % address, gdb.BP_BREAKPOINT)
        self.name = name
        self.address = address

    def stop(self):
        state["entries"][self.name] += 1
        if os.path.exists(STOP):
            return False
        if state["entries"][self.name] > MAX_ENTRY_SAMPLES:
            # Keep the draw entry as a cheap continue sentinel so the outer
            # loop observes STOP; disable every other repetitive breakpoint.
            if self.name != "terrain_draw_0x4324e0":
                self.enabled = False
            return False
        fields = {"target": self.name, "address": hex(self.address),
                  "pc": pc(), "registers": registers(),
                  "scene": scene_context(), "renderer": renderer_context(),
                  "backtrace": backtrace()}
        if self.name in TERRAIN_ENTRIES:
            fields["stack"] = stack_args(8)
            maybe_arm_terrain_watchpoints(self.name)
        elif self.name == "terrain_context_0x403b20":
            fields["stack"] = stack_args(7)
        elif self.name == "object_copy_0x403c10":
            fields["stack"] = stack_args(1)
        elif self.address >= 0x004658E0 and self.address <= 0x00466EA0:
            fields["stack"] = stack_args(6)
        if state["entries"][self.name] <= 120:
            log("entry", **fields)
        return False


class AssetEntry(gdb.Breakpoint):
    def __init__(self):
        super().__init__("*0x%x" % ASSET_ENTRY, gdb.BP_BREAKPOINT)
        self.address = ASSET_ENTRY

    def stop(self):
        if os.path.exists(STOP):
            return False
        stack = stack_args(6)
        args = stack.get("args", [])
        tile_file = as_int(args[0]) if len(args) > 0 else None
        frame = as_int(args[1]) if len(args) > 1 else None
        lookup = asset_table_lookup(tile_file, frame)
        if lookup.get("status") == "PASS":
            asset_by_source[as_int(lookup["computed_source"])] = lookup
        state["asset_entry_events"] += 1
        if state["asset_entry_events"] <= MAX_ASSET_SAMPLES:
            log_asset_event("asset_key_entry", address=hex(self.address),
                            tile_file=tile_file, frame=frame,
                            table_lookup=lookup, registers=registers(),
                            scene=scene_context(), renderer=renderer_context(),
                            stack=stack, backtrace=backtrace())
        return False


class AssetCall(gdb.Breakpoint):
    def __init__(self, name, address, source_stack_offset):
        super().__init__("*0x%x" % address, gdb.BP_BREAKPOINT)
        self.name = name
        self.address = address
        self.source_stack_offset = source_stack_offset

    def stop(self):
        if not os.path.exists(STOP):
            record_asset_call(self.name, self.source_stack_offset)
        return False


summary = {"schema": "syw2plus.g1-terrain-writer-trace.v2",
           "targets": {name: hex(address) for name, address in TARGETS.items()},
           "terrain_entries": {name: hex(address) for name, address in TERRAIN_ENTRIES.items()},
           "terrain_buffer": {"base": hex(TERRAIN_BUFFER), "width": TERRAIN_WIDTH,
                              "height": TERRAIN_HEIGHT,
                              "points": [{"x": x, "y": y} for x, y in TERRAIN_POINTS]},
           "asset_trace": {"entry": hex(ASSET_ENTRY),
                           "calls": {name: {"address": hex(address),
                                             "source_stack_offset": offset}
                                     for name, (address, offset) in ASSET_CALLS.items()},
                           "base_table": hex(ASSET_BASE_TABLE),
                           "offset_table": hex(ASSET_OFFSET_TABLE),
                           "file_stride": ASSET_FILE_STRIDE,
                           "frame_stride": ASSET_FRAME_STRIDE,
                           "digest_bytes": ASSET_DIGEST_BYTES},
           "protected_read_only": True}


def write_summary():
    summary["entries"] = dict(state["entries"])
    summary["events"] = state["events"]
    summary["watchpoints_armed"] = state["watchpoints_armed"]
    summary["watchpoint_hits"] = state["watchpoint_hits"]
    summary["fatal"] = state["fatal"]
    with open(SUMMARY, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)


try:
    breakpoints = [Entry(name, address) for name, address in TARGETS.items()]
    breakpoints.extend(Entry(name, address) for name, address in TERRAIN_ENTRIES.items())
    breakpoints.append(AssetEntry())
    breakpoints.extend(AssetCall(name, address, offset)
                       for name, (address, offset) in ASSET_CALLS.items())
    summary["breakpoints"] = gdb.execute("info breakpoints", to_string=True)
    with open(ARMED, "w", encoding="utf-8") as handle:
        json.dump({"armed": True, "target_count": len(breakpoints)}, handle)
    gdb.execute("continue")
    while time.time() < DEADLINE and not os.path.exists(STOP):
        try:
            gdb.execute("continue")
        except gdb.error as exc:
            summary["continue_error"] = repr(exc)
            break
    summary["stop_reason"] = "stop_flag" if os.path.exists(STOP) else "deadline"
    summary.update(state)
except Exception as exc:
    state["fatal"] = repr(exc)
    summary.update(state)
finally:
    for watch in list(watchpoints):
        remove_watchpoint(watch)
    # Persist before detach as well as after it.  Some batch GDB/Wine
    # combinations terminate the embedded Python command stream immediately
    # after detach even though the inferior was detached successfully.
    try:
        write_summary()
    except Exception:
        pass
    try:
        gdb.execute("detach")
        summary["detached"] = True
    except Exception as exc:
        summary["detach_error"] = repr(exc)
    try:
        write_summary()
    except Exception:
        pass
