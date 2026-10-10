#!/usr/bin/env python3
"""Runtime probe for the ESL2610 G2 spike candidate (own runtime root/prefix/display).

Read/import only from the shared harness (``tools.esl2610_runtime``,
``tools.runtime_env``, ``patches.population.runtime_driver``).  Uses its own
private runtime root, Wine prefix and Xvfb display (``_xvfb`` auto-picks a free
one in :90..:199, so it never collides with another agent's runs).

Two lanes:

* ``boot`` -- launch the candidate, confirm it reaches the title/menu program
  state and stays alive for a window.  This proves the six-array ``.text``
  relocation did not brick startup (a precondition for the >1200 lane).  It does
  NOT prove the pool holds >1200 units.

* ``live`` -- the >1200 lane.  Control = pinned base + G8 supply layer
  (1500 + 500*heroes, clamp 5000); candidate = base + G2 spike + G8.  The game
  enters with eight AI owners via the ``_custom_game_chain_inject_g2_eight_ai``
  control goal, optional synthetic op5 seeding (labeled, ``--accelerate``)
  speeds growth, then the AI plays naturally while live count, per-owner
  count/used/cap and module-activity markers are sampled.  Control must stay at
  or below 1199 live; the candidate must exceed 1200 without crash/corruption.
  The diagnostic bridge is built per variant with the matching pool/existence
  base (``build_runtime_bridge --unit-existence-base``).

Never writes into a deliverable path; the candidate is built in memory and
installed into the private game copy only.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping, cast

from patches.esl2610 import g2_spike_build, pe_extend
from patches.esl2610.g2_runtime_layout_2610 import ESL2610_SPIKE_LAYOUT
from patches.population.runtime_driver import read as read_memory
from patches.population.runtime_driver import state as read_state
from tools import esl2610_runtime, runtime_env

REPO = Path(__file__).resolve().parents[1]
STOCK = REPO / "Syw2plus" / "syw2plus_original.exe"

# Stock (base2610) unit arrays vs the spike candidate's relocated .g2bss arrays.
STOCK_POOL_BASE = 0x0066B790
STOCK_EXIST_BASE = 0x008990C8
STOCK_CAPACITY = 1200
MAP_W_VA = 0x00B3DE34
MAP_H_VA = 0x00B3DE36
SEED_TYPE = 7  # cost-10 unit, same as the 2610 G6 runtime fixture


def _layout_for(variant: str) -> tuple[int, int, int]:
    if variant in CANDIDATE_VARIANTS:
        lay = ESL2610_SPIKE_LAYOUT
        return lay.unit_pool_base, lay.unit_existence_base, lay.capacity
    return STOCK_POOL_BASE, STOCK_EXIST_BASE, STOCK_CAPACITY


def _players(pid: int) -> list[dict[str, int]]:
    """Per-owner count/used/supply cap (shows the G8 cap and natural growth)."""
    return [{"owner": p["owner"], "nation": p["nation"], "count": p["count"],
             "used": p["used"], "count_cap": p["count_cap"], "cap": p["cap"]}
            for p in read_state(pid)["players"] if p["nation"]]


# 2610-line module state the spike leaves on the *old* arrays: if these stay
# empty on the candidate while populated on the control, those modules are
# inactive (not corrupting) for relocated units.
KILLDAT_SLOT_BASE = 0x0115C000  # .kills per-slot 32-byte records x1200
HRSTATE_MAGIC_VA = 0x01193000   # .hrcode session header ('HRT1')
MVSTATE_MAGIC_VA = 0x01182000   # .mvcode session header ('MOV1')


# Hero fixture: the supply loop (0x43FDD0) walks hero-flagged types (type flag
# 0x8 at 0x9B524C + type*0x394) and writes the living-hero count to player
# +0x980; G8 turns that into min(1500 + 500*heroes, 5000).  Seven heroes per
# owner lift the supply cap to 5000 so it cannot be the limiter under G8.
PLAYER_BASE = 0x00956770
PLAYER_STRIDE = 0x3ABC
HERO_COUNT_OFFSET = 0x980
TYPE_FLAGS_VA = 0x009B524C
TYPE_STRIDE = 0x394
HERO_FLAG = 0x8
HEROES_PER_OWNER = 7

# The six stock arrays.  On the candidate the relocated .text no longer uses
# them, so any byte that becomes nonzero there is a write by code that still
# targets stock storage (a 2610 module): a canary for stale-reference writes.
STOCK_ARRAY_CANARIES = {
    "pool": (0x0066B790, 0x00892410), "exist": (0x008990C8, 0x00899A28),
    "age": (0x00899A28, 0x0089A388), "cat_a": (0x0089B008, 0x0089C2CC),
    "cat_b": (0x0089C2CA, 0x0089D58E), "active": (0x00974FA6, 0x0097590C),
}
# 2610 per-unit BSS arrays sized to 1200 (header, stride from the inventory).
PERUNIT_BSS = {
    ".wecache": (0x0114C000, 0x00, 0x10), ".idldata": (0x01158000, 0x10, 0x08),
    ".killdat_sub": (0x0115C000, 0x00, 0x20), ".rsidle": (0x01171000, 0x10, 0x10),
    ".mvstate": (0x01182000, 0x14, 0x28), ".hrstate": (0x01193000, 0x20, 0x44),
    ".skstate": (0x011AB000, 0x10, 0x18), ".healst": (0x011BC000, 0x20, 0x28),
    ".cpstate": (0x01200000, 0x10, 0x30),
}


def _hero_bridge_source(out_dir: Path) -> Path:
    """Private fork of the shared bridge: op5 also accepts hero-flagged types.

    The shared ``runtime_bridge.c`` is read only; the fork is written into the
    artifact dir and passed via ``--bridge-source``.  Hero spawns still go
    through the engine's own Place -> Gate -> Spawn path with the same
    per-entity accounting check (SYNTHETIC fixture, not production).
    """
    text = (REPO / "patches/population/runtime_bridge.c").read_text()
    old = ("fixture_type != 103u) ||\n"
           "                (U32(0x9b524cu+type_offset)&14u) != 0 ||")
    new = ("fixture_type != 103u && (U32(0x9b524cu+type_offset)&8u) == 0) ||\n"
           "                ((U32(0x9b524cu+type_offset)&8u) == 0 &&\n"
           "                 (U32(0x9b524cu+type_offset)&14u) != 0) ||")
    if text.count(old) != 1:
        raise RuntimeError("bridge op5 allow-list anchor mismatch")
    out_dir.mkdir(parents=True, exist_ok=True)
    fork = out_dir / "runtime_bridge_hero_fork.c"
    fork.write_text(text.replace(old, new))
    return fork


def _owner_anchor(pid: int, owner: int, pool_base: int, exist_base: int,
                  capacity: int) -> tuple[int, int] | None:
    """Tile of the owner's first live unit, so its heroes spawn at home."""
    raw = read_memory(pid, exist_base, capacity * 2)
    for slot in range(1, capacity):
        if not (raw[2 * slot] or raw[2 * slot + 1]):
            continue
        unit = pool_base + slot * ESL2610_SPIKE_LAYOUT.unit_stride
        if read_memory(pid, unit + 0x8E, 1)[0] == owner:
            return (int.from_bytes(read_memory(pid, unit + 0x2A2, 2), "little", signed=True),
                    int.from_bytes(read_memory(pid, unit + 0x2A4, 2), "little", signed=True))
    return None


def _hero_counts(pid: int) -> list[int]:
    return [int.from_bytes(read_memory(pid, PLAYER_BASE + o * PLAYER_STRIDE + HERO_COUNT_OFFSET,
                                       4), "little", signed=True) for o in range(8)]


def _nonzero(raw: bytes) -> int:
    return len(raw) - raw.count(0)


def _module_snapshot(pid: int, starts: dict[str, int] | None = None) -> dict[str, Any]:
    """Per-unit module state + stock-array canaries (nonzero bytes/records).

    For each 1200-sized per-unit array: records in use, and nonzero bytes in
    the page slack right past the array (an overflow canary).  For each stock
    array: nonzero bytes (on the candidate these must stay 0 unless some code
    still writes the stock storage).
    """
    out: dict[str, Any] = {"perunit": {}, "stock_arrays_nonzero": {}, "module_arrays": {}}
    from patches.esl2610 import g2_state_2610

    for sec in g2_state_2610.STATE_SECTIONS:
        for arr in sec.arrays:
            if starts is not None:
                va, cap = sec.map(arr.base, starts[sec.name]), arr.capacity
            else:
                va, cap = arr.base, STOCK_CAPACITY
            body = read_memory(pid, va, arr.stride * cap)
            st = arr.stride
            used = [i for i in range(cap) if any(body[st * i: st * (i + 1)])]
            out["module_arrays"][arr.name] = {
                "used": len(used), "used_ge_1200": sum(1 for i in used if i >= STOCK_CAPACITY)}
    if starts is not None:
        # the old storage is PAGE_NOACCESS (guard); a touch is logged as a fault
        return out
    for name, (va, hdr, stride) in PERUNIT_BSS.items():
        body = read_memory(pid, va + hdr, stride * STOCK_CAPACITY)
        used_count = sum(1 for i in range(STOCK_CAPACITY) if any(body[stride * i: stride * (i + 1)]))
        end = va + hdr + stride * STOCK_CAPACITY
        slack_end = (end + 0xFFF) & ~0xFFF
        slack = read_memory(pid, end, slack_end - end) if slack_end > end else b""
        out["perunit"][name] = {"records_used": used_count, "header_nonzero": _nonzero(
            read_memory(pid, va, hdr)) if hdr else 0, "slack_nonzero": _nonzero(slack),
            "slack_bytes": len(slack)}
    for name, (lo, hi) in STOCK_ARRAY_CANARIES.items():
        out["stock_arrays_nonzero"][name] = _nonzero(read_memory(pid, lo, hi - lo))
    return out


def _module_markers(pid: int, starts: dict[str, int] | None = None) -> dict[str, int]:
    from patches.esl2610 import g2_state_2610

    def at(va: int) -> int:
        return va if starts is None else g2_state_2610.map_value(va, starts)

    cap = 1200 if starts is None else 4093
    raw = read_memory(pid, at(KILLDAT_SLOT_BASE), 32 * cap)
    kill_records = sum(1 for i in range(cap) if any(raw[32 * i : 32 * i + 8]))
    return {
        "kills_records": kill_records,
        "hrstate_magic": int.from_bytes(read_memory(pid, at(HRSTATE_MAGIC_VA), 4), "little"),
        "hrstate_session": int.from_bytes(read_memory(pid, at(HRSTATE_MAGIC_VA) + 4, 4), "little"),
        "mvstate_magic": int.from_bytes(read_memory(pid, at(MVSTATE_MAGIC_VA), 4), "little"),
        "mvstate_session": int.from_bytes(read_memory(pid, at(MVSTATE_MAGIC_VA) + 4, 4), "little"),
    }


def _guard_ranges() -> list[tuple[int, int]]:
    """Whole pages of storage the full candidate must never touch again.

    The old module state ranges and the old unit pool: any access there is a
    reference layer 2/3 missed.  Only pages entirely inside a range.
    """
    from patches.esl2610 import g2_state_2610

    # (the PSN portrait cache sits inside the PSN2 save blob, which the 2610
    # module copies whole on save/load: that old read is legitimate)
    spans = [(sec.start, sec.end) for sec in g2_state_2610.STATE_SECTIONS
             if sec.name != ".psndata:psn_cache"]
    spans.append((STOCK_POOL_BASE, STOCK_POOL_BASE + 0x758 * STOCK_CAPACITY))
    out = []
    for lo, hi in spans:
        lo, hi = (lo + 0xFFF) & ~0xFFF, hi & ~0xFFF
        if hi > lo:
            out.append((lo, hi))
    return out


def _guard_fork(fork: Path) -> None:
    """Arm PAGE_NOACCESS on :func:`_guard_ranges` once in game; log faults."""
    text = fork.read_text()
    # decimal: build_runtime_bridge rewrites every "1200" substring in the source
    ranges = ",".join(f"{{{lo}u,{hi}u}}" for lo, hi in _guard_ranges())
    if "1200" in ranges:
        raise RuntimeError("guard range literal contains '1200' (bridge rewrite would corrupt it)")
    helper = f"""
static const DWORD g2_guard_ranges[][2] = {{{ranges}}};
static LONG CALLBACK g2_guard_veh(PEXCEPTION_POINTERS ep)
{{
    static LONG in_veh;
    if (ep->ExceptionRecord->ExceptionCode == EXCEPTION_ACCESS_VIOLATION &&
        InterlockedExchange(&in_veh, 1) == 0) {{  /* IsBadReadPtr probes below fault too */
        char line[1400], mod[160], *p;
        HMODULE hm = NULL;
        DWORD *sp = (DWORD *)(ULONG_PTR)ep->ContextRecord->Esp, k, n = 0, ret[8] = {{0}};
        DWORD *bp = (DWORD *)(ULONG_PTR)ep->ContextRecord->Ebp, chain[8] = {{0}}, m = 0;
        mod[0] = 0;
        if (GetModuleHandleExA(6 /* FROM_ADDRESS|UNCHANGED_REFCOUNT */,
                               (LPCSTR)(ULONG_PTR)ep->ContextRecord->Eip, &hm))
            GetModuleFileNameA(hm, mod, sizeof(mod));
        for (p = mod; *p; ++p) if (*p == 92 || *p == 34) *p = '/';
        for (k = 0; k < 4096 && n < 8; ++k)
            if (!IsBadReadPtr(sp + k, 4) &&
                ((sp[k] >= 4198400u && sp[k] < 5132288u) ||
                 (sp[k] >= 17367040u && sp[k] < 27336704u) ||
                 (sp[k] >= 47046656u && sp[k] < 47063040u)))
                ret[n++] = sp[k];
        while (m < 8 && bp && !IsBadReadPtr(bp, 8)) {{ chain[m++] = bp[1]; bp = (DWORD *)(ULONG_PTR)bp[0]; }}
        wsprintfA(line, "{{\\"eip\\":%lu,\\"write\\":%lu,\\"addr\\":%lu,\\"tick\\":%lu,"
                  "\\"tid\\":%lu,\\"esp\\":%lu,\\"eax\\":%lu,\\"ecx\\":%lu,\\"edx\\":%lu,"
                  "\\"esi\\":%lu,\\"edi\\":%lu,\\"mod\\":\\"%s\\","
                  "\\"stack_exe\\":[%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu],"
                  "\\"ebp_chain\\":[%lu,%lu,%lu,%lu,%lu,%lu,%lu,%lu]}}\\n",
                  (DWORD)ep->ContextRecord->Eip,
                  (DWORD)ep->ExceptionRecord->ExceptionInformation[0],
                  (DWORD)ep->ExceptionRecord->ExceptionInformation[1], U32(0x8924b8),
                  GetCurrentThreadId(), (DWORD)ep->ContextRecord->Esp,
                  (DWORD)ep->ContextRecord->Eax, (DWORD)ep->ContextRecord->Ecx,
                  (DWORD)ep->ContextRecord->Edx, (DWORD)ep->ContextRecord->Esi,
                  (DWORD)ep->ContextRecord->Edi, mod,
                  ret[0], ret[1], ret[2], ret[3], ret[4], ret[5], ret[6], ret[7],
                  chain[0], chain[1], chain[2], chain[3], chain[4], chain[5], chain[6], chain[7]);
        write_file("C:\\\\g2_guard_fault.jsonl", line, TRUE);
        InterlockedExchange(&in_veh, 0);
    }}
    return EXCEPTION_CONTINUE_SEARCH;
}}
static void g2_guard_arm(void)
{{
    static BOOL armed;
    DWORD i, old, ok = 0;
    char line[64];
    if (armed) return;
    armed = TRUE;
    AddVectoredExceptionHandler(1, g2_guard_veh);
    for (i = 0; i < sizeof(g2_guard_ranges) / sizeof(g2_guard_ranges[0]); ++i)
        if (VirtualProtect((LPVOID)(ULONG_PTR)g2_guard_ranges[i][0],
                           g2_guard_ranges[i][1] - g2_guard_ranges[i][0], PAGE_NOACCESS, &old))
            ++ok;
    wsprintfA(line, "{{\\"armed\\":%lu}}\\n", ok);
    write_file("C:\\\\g2_guard_fault.jsonl", line, TRUE);
}}
"""
    anchor = "/* Called only by the copied _imeGetTime export"
    poll = "        enabled[0] != '1') return;\n"
    if text.count(anchor) != 1 or text.count(poll) != 1:
        raise RuntimeError("bridge guard anchors mismatch")
    text = text.replace(anchor, helper + anchor)
    text = text.replace(poll, poll + "    if (U16(0x4ed818) == 3) g2_guard_arm();\n")
    fork.write_text(text)


def _unit_stats(pid: int, pool_base: int, exist_base: int, capacity: int) -> dict[str, Any]:
    """Combat evidence: hp sum, command histogram and units with a target."""
    from collections import Counter

    raw = read_memory(pid, exist_base, capacity * 2)
    hp_sum = 0
    commands: Counter[int] = Counter()
    targeted = targeted_high = high = 0
    for slot in range(1, capacity):
        if not (raw[2 * slot] or raw[2 * slot + 1]):
            continue
        unit = read_memory(pid, pool_base + slot * 0x758, 0x758)
        hp_sum += int.from_bytes(unit[0xB4:0xB8], "little", signed=True)
        commands[int.from_bytes(unit[0x290:0x292], "little", signed=True)] += 1
        if int.from_bytes(unit[0x210:0x212], "little"):
            targeted += 1
            if slot >= STOCK_CAPACITY:
                targeted_high += 1
        if slot >= STOCK_CAPACITY:
            high += 1
    vision = read_memory(pid, 0x0089D58E, 0x7E90 * 8)
    vis = [[vision[0x7E90 * o: 0x7E90 * (o + 1)].count(v) for v in (1, 2)] for o in range(8)]
    return {"vision_1_2": vis,
            "hp_sum": hp_sum, "targeted": targeted, "targeted_ge_1200": targeted_high,
            "units_ge_1200": high, "commands": dict(sorted(commands.items()))}


def _attack_test(pid: int, supply: Any, pool_base: int, exist_base: int,
                 capacity: int) -> dict[str, Any]:
    """DIAGNOSTIC: one original target order (op8) owner0 -> nearest owner1 unit."""
    raw = read_memory(pid, exist_base, capacity * 2)
    units: dict[int, list[tuple[int, int, int]]] = {0: [], 1: []}
    for slot in range(1, capacity):
        if not (raw[2 * slot] or raw[2 * slot + 1]):
            continue
        u = read_memory(pid, pool_base + slot * 0x758, 0x2A6)
        owner = u[0x8E]
        if owner in units and u[0x8D] == SEED_TYPE:
            units[owner].append((slot, int.from_bytes(u[0x2A2:0x2A4], "little", signed=True),
                                 int.from_bytes(u[0x2A4:0x2A6], "little", signed=True)))
    if not units[0] or not units[1]:
        return {"error": "no seeded units for owners 0/1"}
    src, tgt = min(((a, b) for a in units[0] for b in units[1]),
                   key=lambda ab: max(abs(ab[0][1] - ab[1][1]), abs(ab[0][2] - ab[1][2])))
    receipt = _op8(supply, src[0], tgt[0])
    trace = []
    for _ in range(10):
        time.sleep(1)
        su = read_memory(pid, pool_base + src[0] * 0x758, 0x758)
        tu = read_memory(pid, pool_base + tgt[0] * 0x758, 0x758)
        trace.append({"src_cmd": int.from_bytes(su[0x290:0x292], "little", signed=True),
                      "src_target": int.from_bytes(su[0x210:0x214], "little"),
                      "tgt_hp": int.from_bytes(tu[0xB4:0xB8], "little", signed=True)})
    return {"src": src, "tgt": tgt, "receipt": receipt, "trace": trace}


def _op8(supply: Any, src_slot: int, tgt_slot: int) -> dict[str, Any]:
    return _bridge(supply, 8, 0, src_slot, tgt_slot)


def _bridge(supply: Any, op: int, owner: int, slot: int, kind: int = 0,
            timeout: float = 20) -> dict[str, Any]:
    request_id = supply.next_id
    supply.next_id += 1
    supply.request.write_text(f"{request_id} {op} {owner} {slot} {kind} 0 0 0\n", encoding="ascii")
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            result = json.loads(supply.result.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            time.sleep(0.05)
            continue
        if result.get("id") == request_id:
            return result
        time.sleep(0.05)
    return {"error": "op8 timeout"}


def _signature(pid: int, pool_base: int, exist_base: int, capacity: int
               ) -> list[tuple[int, int, int, int]]:
    """(slot, type, owner, uid) of every live unit."""
    raw = read_memory(pid, exist_base, capacity * 2)
    out: list[tuple[int, int, int, int]] = []
    for slot in range(1, capacity):
        if raw[2 * slot] or raw[2 * slot + 1]:
            u = read_memory(pid, pool_base + slot * 0x758, 0x2A0)
            out.append((slot, u[0x8D], u[0x8E], int.from_bytes(u[0x29C:0x2A0], "little")))
    return out


SAVE_MARKER = b"S2P2"  # + 4-byte layout hash (g2_persist_2610)


def _legacy_state(pid: int, starts: dict[str, int] | None) -> dict[str, Any]:
    """Hashes of the state an official save's KIL1/PSN2 blobs restore, laid out
    as the official EXE sees it (kill_log 1200 entries, 256x16 table, the
    8-dword 0x4EBFC0 block, the 1200 PSN2 portrait-cache entries), so a base
    run and a candidate run loading the same official save can be compared."""
    import hashlib

    from patches.esl2610 import g2_state_2610

    def at(va: int) -> int:
        return va if starts is None else g2_state_2610.map_value(va, starts)

    def h(raw: bytes) -> str:
        return hashlib.sha256(raw).hexdigest()[:16]

    out = {"kill_log_1200": h(read_memory(pid, at(0x0115C000), 0x9600)),
           "kill_table": h(read_memory(pid, at(0x01165600), 0x1000)),
           "enc16_4ebfc0": h(read_memory(pid, 0x004EBFC0, 0x20)),
           "psn_cache_1200": h(read_memory(pid, at(0x0110C000), 0x4B00))}
    if starts is not None:
        rest = read_memory(pid, at(0x0115C000) + 0x9600, 0x20 * (4093 - 1200))
        out["kill_log_ge_1200_nonzero"] = len(rest) - rest.count(0)
    return out


def _save_roundtrip(pid: int, supply: Any, game: Path, pool_base: int, exist_base: int,
                    capacity: int, artifact_root: Path, slot: int = 5,
                    legacy_save: Path | None = None,
                    starts: dict[str, int] | None = None) -> dict[str, Any]:
    """Save a running >1200 game, play on, load it back, compare unit signatures.

    Optionally (``legacy_save``) load a save written by the official EXE.
    """
    out: dict[str, Any] = {}
    before = _signature(pid, pool_base, exist_base, capacity)
    out["tick_before_save"] = read_state(pid).get("tick")
    out["save_receipt"] = _bridge(supply, 2, 0, slot, timeout=60)
    save_files = sorted((game / "save").glob(f"*{slot:03d}*")) if (game / "save").exists() else []
    out["save_files"] = [str(p.name) for p in save_files]
    if save_files:
        blob = save_files[0].read_bytes()
        out["save_size"] = len(blob)
        out["save_marker_at"] = blob.find(SAVE_MARKER)
        shutil.copy2(save_files[0], artifact_root / f"saved_{save_files[0].name}")
    time.sleep(15)  # play on: units move/fight/die
    drift = _signature(pid, pool_base, exist_base, capacity)
    out["tick_before_load"] = read_state(pid).get("tick")
    out["load_receipt"] = _bridge(supply, 3, 0, slot, timeout=60)
    after = _signature(pid, pool_base, exist_base, capacity)  # at once: the game keeps ticking
    key = lambda rows: sorted((r[0], r[1], r[2], r[3]) for r in rows)  # noqa: E731
    out["live_before"], out["live_drift"], out["live_after"] = len(before), len(drift), len(after)
    out["slots_ge_1200_before"] = sum(1 for r in before if r[0] >= STOCK_CAPACITY)
    out["slots_ge_1200_after"] = sum(1 for r in after if r[0] >= STOCK_CAPACITY)
    out["drift_differs"] = key(before) != key(drift)
    out["restored_exact"] = key(before) == key(after)
    if not out["restored_exact"]:
        b, a = set(key(before)), set(key(after))
        out["missing_after"] = sorted(b - a)[:20]
        out["extra_after"] = sorted(a - b)[:20]
    if legacy_save is not None:
        dest = game / "save" / f"save{slot + 1:03d}.dat"
        shutil.copy2(legacy_save, dest)
        out["tick_before_legacy_load"] = read_state(pid).get("tick")
        out["legacy_load_receipt"] = _bridge(supply, 3, 0, slot + 1, timeout=60)
        out["legacy_module_state"] = _legacy_state(pid, starts)
        time.sleep(2)
        rows = _signature(pid, pool_base, exist_base, capacity)
        out["legacy_live_after"] = len(rows)
        out["legacy_ps"] = read_state(pid).get("ps")
        ticks = []
        for _ in range(5):  # does the game keep running after the official-save load?
            ticks.append(read_state(pid).get("tick"))
            time.sleep(2)
        out["legacy_tick_progress"] = ticks
    return out


PAUSE_RESTART_POINT = (400, 307)  # pause menu row 6 "다시하기" (35px pitch from row 1)
CONFIRM_OK_POINT = (419, 329)  # confirm dialog OK (measured, lap746)


def _restart_game(pid: int, display: str, env: Mapping[str, str], log: Any, click: Any,
                  artifact_root: Path, pool_base: int, exist_base: int, capacity: int,
                  starts: dict[str, int] | None) -> dict[str, Any]:
    """Second game in the same process: pause -> restart -> confirm.

    Records the tick reset, the live count and the module state right after
    the new game starts (stale >1200 state would show as records in slots the
    new game has not used), then lets the AI run 60 s.
    """
    from tools.g5_candidate_drag_probe import capture, send_key

    out: dict[str, Any] = {"before": {"tick": read_state(pid).get("tick"),
                                      "live": _live_count(pid, exist_base, capacity)}}
    send_key(display, "Escape", env=env, log=log)
    time.sleep(1.0)
    out["ps_after_escape"] = read_state(pid).get("ps")
    click(*PAUSE_RESTART_POINT)
    time.sleep(1.0)
    out["ps_after_restart_click"] = read_state(pid).get("ps")
    click(*CONFIRM_OK_POINT)
    trace = []
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        st = read_state(pid)
        trace.append((st.get("ps"), st.get("tick")))
        if st.get("ps") == 3 and st.get("tick", 1 << 30) < out["before"]["tick"]:
            break
        time.sleep(0.5)
    out["ps_tick_trace"] = trace[-12:]
    capture(display, artifact_root / "after-restart.png", log)
    st = read_state(pid)
    out["restarted"] = st.get("ps") == 3 and st.get("tick", 1 << 30) < out["before"]["tick"]
    time.sleep(2)
    out["after"] = {"tick": read_state(pid).get("tick"),
                    "live": _live_count(pid, exist_base, capacity),
                    "unit_stats": _unit_stats(pid, pool_base, exist_base, capacity),
                    "module_state": _module_snapshot(pid, starts)}
    time.sleep(60)
    out["after_60s"] = {"alive": Path(f"/proc/{pid}").exists()}
    if out["after_60s"]["alive"]:
        out["after_60s"].update(tick=read_state(pid).get("tick"),
                                live=_live_count(pid, exist_base, capacity),
                                unit_stats=_unit_stats(pid, pool_base, exist_base, capacity))
    return out


def _guard_log_ok(lines: list[str]) -> bool:
    """Require a successfully armed old-pool guard and no recorded fault."""
    if not lines:
        return False
    arm_counts: list[int] = []
    try:
        for line in lines:
            row = json.loads(line)
            if not isinstance(row, dict):
                return False
            if "armed" in row:
                arm_counts.append(int(row["armed"]))
            if "eip" in row or "fault" in row or str(row.get("type", "")).upper() == "FAULT":
                return False
    except (json.JSONDecodeError, TypeError, ValueError):
        return False
    return len(arm_counts) == 1 and arm_counts[0] == len(_guard_ranges())


def _save_roundtrip_ok(result: Mapping[str, Any]) -> bool:
    save = result.get("save_test")
    if not isinstance(save, Mapping):
        return False
    save_receipt, load_receipt = save.get("save_receipt"), save.get("load_receipt")
    high_before, high_after = save.get("slots_ge_1200_before"), save.get("slots_ge_1200_after")
    return (isinstance(save_receipt, Mapping) and save_receipt.get("ok") is True
            and save_receipt.get("op") == 2
            and isinstance(save.get("save_files"), list) and bool(save["save_files"])
            and isinstance(save.get("save_size"), int) and save["save_size"] > 0
            and isinstance(high_before, int) and high_before > 0
            and isinstance(high_after, int) and high_after > 0
            and isinstance(load_receipt, Mapping) and load_receipt.get("ok") is True
            and load_receipt.get("op") == 3 and save.get("restored_exact") is True
            and result.get("alive_after_save_test") is True)


def live_acceptance_status(result: Mapping[str, Any], *, save_requested: bool,
                           guard_requested: bool, legacy_requested: bool = False,
                           restart_requested: bool = False) -> str:
    """Return a strict status; a >1200 peak alone is only partial live evidence."""
    peak = result.get("peak_live", 0)
    if result.get("crashed") is True or not isinstance(peak, int) or peak <= STOCK_CAPACITY:
        return "LIVE_FAILED"
    samples = result.get("samples")
    complete_samples = (isinstance(samples, list) and bool(samples)
                        and len(samples) >= 2
                        and all(isinstance(row, Mapping) and isinstance(row.get("live"), int)
                                and isinstance(row.get("tick"), int)
                                and row.get("ps") == 3 and row.get("high_slots_ok") is True
                                and isinstance(row.get("highest_slot"), int)
                                and row["highest_slot"] >= STOCK_CAPACITY
                                and "error" not in row for row in samples))
    sample_exceeded = (isinstance(samples, list) and bool(samples) and complete_samples
                       and any(isinstance(row, Mapping) and row.get("live", 0) > STOCK_CAPACITY
                               for row in samples))
    ticks = ([row["tick"] for row in samples if isinstance(row, Mapping)
              and isinstance(row.get("tick"), int)] if isinstance(samples, list) else [])
    live_tick_progress = len(ticks) >= 2 and any(after > before for before, after in zip(ticks, ticks[1:]))
    owners = result.get("active_owners")
    eight_owners = (isinstance(owners, list) and len(owners) == 8
                    and len(set(owners)) == 8)
    checks = [complete_samples, sample_exceeded, live_tick_progress, eight_owners]
    if guard_requested:
        checks.append(_guard_log_ok(result.get("guard_log", [])))
    else:
        checks.append(False)
    heroes = result.get("synthetic_heroes_per_owner", 0)
    if isinstance(heroes, int) and heroes > 0:
        after_heroes = result.get("after_heroes")
        players = after_heroes.get("players") if isinstance(after_heroes, Mapping) else None
        caps_ok = (isinstance(players, list) and len(players) == 8
                   and {p.get("owner") for p in players if isinstance(p, Mapping)} == set(owners or [])
                   and all(isinstance(p, Mapping) and p.get("cap") == 5000 for p in players))
        checks.append(caps_ok)
    if save_requested:
        checks.append(_save_roundtrip_ok(result))
    if legacy_requested:
        save = result.get("save_test")
        legacy_ticks = save.get("legacy_tick_progress") if isinstance(save, Mapping) else None
        checks.append(isinstance(save, Mapping)
                      and isinstance(save.get("legacy_load_receipt"), Mapping)
                      and save["legacy_load_receipt"].get("ok") is True
                      and save.get("legacy_ps") == 3
                      and isinstance(save.get("legacy_live_after"), int) and save["legacy_live_after"] > 0
                      and isinstance(legacy_ticks, list) and len(legacy_ticks) >= 2
                      and all(isinstance(t, int) for t in legacy_ticks)
                      and legacy_ticks[-1] > legacy_ticks[0])
    if restart_requested:
        restart = result.get("restart_test")
        checks.append(isinstance(restart, Mapping) and restart.get("restarted") is True
                      and isinstance(restart.get("after_60s"), Mapping)
                      and restart["after_60s"].get("alive") is True
                      and isinstance(restart.get("after"), Mapping)
                      and isinstance(restart.get("after", {}).get("tick"), int)
                      and isinstance(restart["after_60s"].get("tick"), int)
                      and restart["after_60s"]["tick"] > restart["after"]["tick"]
                      and isinstance(restart["after_60s"].get("live"), int)
                      and restart["after_60s"]["live"] > 0)
    return "LIVE_OK_EXCEEDED_1200" if all(checks) else "LIVE_PARTIAL_EXCEEDED_1200"


def _live_count(pid: int, exist_base: int, capacity: int) -> int:
    raw = read_memory(pid, exist_base, capacity * 2)
    return sum(1 for i in range(capacity) if raw[2 * i] or raw[2 * i + 1])


def _sha256(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def base_bytes() -> bytes:
    """The pinned official 2610-line EXE (follows pe_extend's pin, e.g. 2611)."""
    data = pe_extend.BASE_PATH.read_bytes()
    pe_extend.verify_base(data)
    return data


# Candidate variants: "candidate" = layer 1 (six-array .text spike);
# "cand_l2" = layer 1 + layer 2 (2610 modules retargeted, clamp 1200).
CANDIDATE_VARIANTS = ("candidate", "cand_l2", "cand_full", "v8", "v89")
COMBO_VARIANTS = ("v8", "v89")  # deliverable combos (G2+G6+G8[+G9]) built whole


def build_candidate(variant: str = "candidate") -> tuple[bytes, dict[str, Any]]:
    data = base_bytes()
    if variant == "cand_full":
        from patches.esl2610 import g2_full_2610

        return g2_full_2610.build_candidate(data, STOCK.read_bytes())
    spike, report = g2_spike_build.build_spike_candidate(data, STOCK.read_bytes())
    if variant == "candidate":
        return spike, report
    from patches.esl2610 import g2_newcode_2610

    out, l2 = g2_newcode_2610.apply(spike, data, int(report["g2bss_va"], 16))
    return out, {"layer1": report, "layer2": l2}


def boot_probe(runtime_root: Path, artifact_root: Path, *, variant: str = "candidate",
               alive_seconds: float = 30.0) -> dict[str, Any]:
    if artifact_root.exists():
        raise RuntimeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    if variant == "base":
        exe_bytes = base_bytes()
        report: dict[str, Any] = {"build": {"sha256": pe_extend.BASE_SHA256}}
    else:
        exe_bytes, report = build_candidate(variant)
        report = {"build": report}
    manifest, overlay = esl2610_runtime.prepare(exe_bytes, runtime_root, timeout=120)
    game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
    prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
    private_exe = game / runtime_env.ORIGINAL_EXE
    result: dict[str, Any] = {
        "schema": "syw2plus.g2-esl2610-spike-boot.v1", "status": "UNKNOWN", "variant": variant,
        "layout": {"pool": hex(ESL2610_SPIKE_LAYOUT.unit_pool_base),
                   "existence": hex(ESL2610_SPIKE_LAYOUT.unit_existence_base),
                   "capacity": ESL2610_SPIKE_LAYOUT.capacity},
        "provenance": {"private_exe_sha256": _sha256(private_exe.read_bytes()),
                       "private_game": str(game), "private_prefix": str(prefix),
                       "overlay_files": len(overlay)},
        "ps_seen": [], "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb = None
    try:
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        result["display"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env,
                                     stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid
        deadline = time.monotonic() + 45
        reached = False
        while time.monotonic() < deadline:
            if not Path(f"/proc/{pid}").exists():
                break
            try:
                st = read_state(pid)
                ps = st.get("ps")
                if ps is not None and ps not in result["ps_seen"]:
                    result["ps_seen"].append(ps)
                if ps in (7, 9):  # title / menu reached
                    reached = True
                    break
            except (OSError, ValueError):
                pass
            time.sleep(0.5)
        result["reached_menu"] = reached
        # liveness window
        t0 = time.monotonic()
        alive = True
        while time.monotonic() - t0 < alive_seconds:
            if not Path(f"/proc/{pid}").exists():
                alive = False
                break
            time.sleep(1)
        result["alive_after_window"] = alive and Path(f"/proc/{pid}").exists()
        ok = reached and result["alive_after_window"]
        result["status"] = "BOOT_OK" if ok else "BOOT_FAILED"
    finally:
        import shutil

        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
        kill_env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
        subprocess.run(["wineserver", "-k"], env=kill_env, stdout=log, stderr=log,
                       timeout=15, check=False)
        subprocess.run(["wineserver", "-w"], env=kill_env, stdout=log, stderr=log,
                       timeout=15, check=False)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
        result["cleanup"]["prefix_processes_after"] = runtime_env._prefix_pids(prefix)
        if game.exists():
            shutil.rmtree(game, ignore_errors=True)
        result["cleanup"]["game_removed"] = not game.exists()
        log.close()
    (artifact_root / "boot_result.json").write_text(json.dumps(result, indent=2))
    return result


def _build_bridge(variant: str, bridge_dir: Path, log: Any,
                  bridge_source: Path | None = None) -> Path:
    args = [sys.executable, str(REPO / "patches/population/build_runtime_bridge.py"),
            "--out-dir", str(bridge_dir)]
    if bridge_source is not None:
        args += ["--bridge-source", str(bridge_source)]
    if variant in CANDIDATE_VARIANTS:
        lay = ESL2610_SPIKE_LAYOUT
        args += ["--unit-pool-capacity", str(lay.capacity),
                 "--unit-pool-base", hex(lay.unit_pool_base),
                 "--unit-existence-base", hex(lay.unit_existence_base)]
    else:
        args += ["--unit-pool-capacity", "1200"]
    subprocess.run(args, cwd=REPO, check=True, env=dict(os.environ, PYTHONPATH=str(REPO)),
                   stdout=log, stderr=log)
    return bridge_dir / "_inmm.dll"


def live_probe(runtime_root: Path, artifact_root: Path, *, variant: str,
               target_units: int = 2000, tick_seconds: float = 180.0,
               entry: str = "eight_ai", accelerate: int = 150,
               ledger_reset: bool = False, sample_every: float = 15.0,
               g9: bool = False, heroes: int = HEROES_PER_OWNER,
               low_slots: bool = False, attack_test: bool = False,
               save_test: bool = False, legacy_save: Path | None = None,
               restart_test: bool = False, guard: bool = True) -> dict[str, Any]:
    """Live lane: control = pinned base + G8 supply, candidate = base + G2 spike + G8.

    ``accelerate`` seeds up to that many synthetic units per active owner (op5,
    labeled synthetic) before natural AI play; ``ledger_reset`` (default off)
    re-enables the per-batch used-ledger reset hack and is reported if used.
    """
    from patches.esl2610 import g8_supply_1500_500_5000 as g8
    from tools.g5_candidate_drag_probe import ProbeError, SupplyProbe

    if artifact_root.exists():
        raise RuntimeError(f"artifact root must be new: {artifact_root}")
    artifact_root.mkdir(parents=True)
    pool_base, exist_base, capacity = _layout_for(variant)
    if variant in COMBO_VARIANTS:
        from patches.esl2610 import g2_combo_2610

        exe_bytes, combo = g2_combo_2610.build(base_bytes(), variant, stock=STOCK.read_bytes())
        spike_report = combo["detail"]["g2"]
        build = {"combo": {k: v for k, v in combo.items() if k != "detail"},
                 "spike": spike_report}
        g9 = False  # V89 already contains G9
    elif variant in CANDIDATE_VARIANTS:
        spike_bytes, spike_report = build_candidate(variant)
        exe_bytes, g8_report = g8.build_candidate(spike_bytes, require_pinned_base=False)
        build = {"spike": spike_report, "g8": g8_report}
    else:
        exe_bytes, g8_report = g8.build_candidate(base_bytes())
        build = {"base_sha256": pe_extend.BASE_SHA256, "g8": g8_report}
    if g9:
        from patches.esl2610 import g9_fixed_start

        exe_bytes, build["g9"] = g9_fixed_start.build_candidate(
            exe_bytes, require_pinned_base=False)
    build["exe_sha256"] = _sha256(exe_bytes)
    starts = None
    if variant in ("cand_full", *COMBO_VARIANTS):
        starts = {k: int(v, 16) for k, v in spike_report["layer3"]["starts"].items()}
    result: dict[str, Any] = {
        "schema": "syw2plus.g2-esl2610-spike-live.v2", "status": "UNKNOWN", "variant": variant,
        "supply_layer": "G8 1500+500*heroes clamp 5000", "g9_fixed_start": g9,
        "entry": entry, "accelerate_per_owner": accelerate, "ledger_reset": ledger_reset,
        "synthetic_acceleration": accelerate > 0,
        "synthetic_heroes_per_owner": heroes,
        "layout": {"pool": hex(pool_base), "existence": hex(exist_base), "capacity": capacity},
        "target_units": target_units, "build": build, "samples": [], "owners": [],
        "peak_live": 0, "ps_seen": [], "cleanup": {},
    }
    log = (artifact_root / "probe.log").open("a", encoding="utf-8")
    children: list[Any] = []
    xvfb = None
    manifest = None
    game = prefix = None
    try:
        fork = _hero_bridge_source(artifact_root / "bridge_src") if heroes > 0 else None
        if variant in ("cand_full", *COMBO_VARIANTS) and guard:
            if fork is None:
                raise RuntimeError("cand_full guard needs the bridge fork (heroes > 0)")
            _guard_fork(fork)
        bridge = _build_bridge(variant, artifact_root / "bridge", log, fork)
        manifest, overlay = esl2610_runtime.prepare(
            exe_bytes, runtime_root, bridge=bridge, timeout=120)
        game = Path(cast(str, cast(Mapping[str, Any], manifest["game"])["root"]))
        prefix = Path(cast(str, cast(Mapping[str, Any], manifest["wine"])["prefix"]))
        private_exe = game / runtime_env.ORIGINAL_EXE
        result["provenance"] = {
            "private_exe_sha256": _sha256(private_exe.read_bytes()),
            "private_game": str(game), "bridge_sha256": _sha256(bridge.read_bytes()),
            "overlay_files": len(overlay)}
        env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32", WINEDEBUG="-all",
                   LANG="ko_KR.UTF-8", LC_ALL="ko_KR.UTF-8", WINEDLLOVERRIDES="ddraw=b",
                   SYW2_SUPPLY_PROBE="1")
        xvfb, display = runtime_env._xvfb(log, "1600x1200x24")
        env["DISPLAY"] = display
        result["display"] = display
        children.append(subprocess.Popen(["wine", "explorer", "/desktop=Default,1600x1200"],
                                         cwd=game, env=env, stdout=log, stderr=log))
        time.sleep(1)
        game_proc = subprocess.Popen(["wine", str(private_exe)], cwd=game, env=env,
                                     stdout=log, stderr=log)
        children.append(game_proc)
        pid = game_proc.pid

        def wait_ps(target: int, timeout: float = 60) -> None:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if not Path(f"/proc/{pid}").exists():
                    raise ProbeError(f"process died before ps={target}")
                try:
                    ps = read_state(pid).get("ps")
                    if ps is not None and ps not in result["ps_seen"]:
                        result["ps_seen"].append(ps)
                    if ps == target:
                        return
                except (OSError, ValueError):
                    pass
                time.sleep(0.4)
            raise ProbeError(f"ps {target} timeout; seen={result['ps_seen']}")

        tree = None
        wait_ps(9, 60)
        tree = runtime_env._window_tree(display, 10)
        outer, content = runtime_env._game_window_ids(tree)
        info = runtime_env._xwininfo_details(display, content or outer, 10)
        ox, oy = int(info["x"]), int(info["y"])

        def click(x: int, y: int) -> None:
            subprocess.run([sys.executable, str(REPO / "tools/x11_mouse_click.py"), "--display",
                            display, str(ox + x), str(oy + y), "--button", "1"],
                           env=env, stdout=log, stderr=log, timeout=10, check=True)

        subprocess.run(["xdotool", "windowfocus", outer], env=env, stdout=log, stderr=log,
                       timeout=10, check=False)
        click(184, 560)
        wait_ps(7, 45)
        if entry == "eight_ai":
            goal = "_custom_game_chain_inject_g2_eight_ai_seed42"
            chain = runtime_env._g4_send_control_goal(prefix, goal, 30.0)
            result["chain_inject"] = {"goal": goal, "ok": chain.get("ok"),
                                      "reason": chain.get("reason")}
            if chain.get("ok") is not True:
                raise ProbeError(f"eight-AI chain inject failed: {chain.get('reason')}")
        else:
            click(462, 169)
            time.sleep(0.5)
            click(608, 564)
            wait_ps(5, 45)
            deadline = time.monotonic() + 8
            while read_state(pid).get("ps") not in (2, 3) and time.monotonic() < deadline:
                time.sleep(0.3)
            if read_state(pid).get("ps") not in (2, 3):
                click(608, 564)
        wait_ps(3, 60)
        time.sleep(6)  # let the scene settle

        st = read_state(pid)
        active = [p["owner"] for p in st["players"] if p["nation"] > 0]
        result["active_owners"] = active
        if not active:
            active = [0]
        result["players_at_start"] = _players(pid)
        result["player_side_bytes"] = [list(read_memory(pid, PLAYER_BASE + o * PLAYER_STRIDE, 8))
                                       for o in range(8)]
        supply = SupplyProbe(prefix)
        if accelerate > 0:
            # SYNTHETIC: resource-only top-up (op7 never touches used/count/units).
            for owner in active:
                supply.call(op=7, owner=owner, unit_type=0, x=1_000_000, y=1_000_000, count=0)

        map_w = int.from_bytes(read_memory(pid, MAP_W_VA, 2), "little", signed=True)
        map_h = int.from_bytes(read_memory(pid, MAP_H_VA, 2), "little", signed=True)
        result["map"] = [map_w, map_h]
        result["modules_at_start"] = _module_snapshot(pid, starts)

        # SYNTHETIC hero fixture: spawn `heroes` distinct hero-flagged types per
        # owner via the engine Spawn path so G8's cap reaches 5000 (7 heroes).
        if heroes > 0:
            hero_types = [t for t in range(200) if int.from_bytes(
                read_memory(pid, TYPE_FLAGS_VA + t * TYPE_STRIDE, 4), "little") & HERO_FLAG]
            result["hero_types"] = hero_types
            spawned: dict[int, list[int]] = {owner: [] for owner in active}
            receipts = result.setdefault("hero_receipts", [])
            for owner in active:
                anchor = _owner_anchor(pid, owner, pool_base, exist_base, capacity)
                hx, hy = anchor if anchor else (max(1, map_w // 2), max(1, map_h // 2))
                hx = min(max(hx, 1), map_w - 2)
                hy = min(max(hy, 1), map_h - 2)
                for kind in hero_types:
                    if len(spawned[owner]) >= heroes:
                        break
                    r = supply.call(op=5, owner=owner, unit_type=kind, x=hx, y=hy, count=1)
                    receipts.append({"owner": owner, "type": kind, "ok": r.get("ok"),
                                     "reason": r.get("reason"),
                                     "added": r.get("fixture_added")})
                    if r.get("ok") and r.get("fixture_added") == 1:
                        spawned[owner].append(kind)
            result["heroes_spawned"] = {str(o): v for o, v in spawned.items()}
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                caps = [p["cap"] for p in _players(pid)]
                if all(c >= 5000 for c in caps):
                    break
                time.sleep(1)
            result["after_heroes"] = {"players": _players(pid), "hero_count_0x980":
                                      _hero_counts(pid)}

        if low_slots and variant in CANDIDATE_VARIANTS:
            # SYNTHETIC (diagnostic): age the free slots 1..1199 so the engine's
            # own allocator (oldest free slot first) fills them before 1200+.
            from patches.population.runtime_driver import write as write_memory
            age_base = exist_base + 2 * ESL2610_SPIKE_LAYOUT.capacity
            write_memory(pid, age_base + 2, (0x7000).to_bytes(2, "little") * (STOCK_CAPACITY - 1))
            result["synthetic_low_slot_ages"] = True
        # SYNTHETIC acceleration: round-robin op5 up to `accelerate` per owner.
        last_live = _live_count(pid, exist_base, capacity)
        stalls = 0
        first_fail = None
        seeded = {owner: 0 for owner in active}
        while accelerate > 0:
            if not Path(f"/proc/{pid}").exists():
                first_fail = {"when": "spawn", "live": last_live}
                break
            progressed = False
            for owner in active:
                want = min(200, accelerate - seeded[owner])
                if want <= 0:
                    continue
                if ledger_reset:
                    # SYNTHETIC hack (off by default, reported): reset used ledger.
                    supply.call(op=4, owner=owner, unit_type=0, x=1_000_000, y=1_000_000,
                                count=0)
                receipt = supply.call(op=5, owner=owner, unit_type=SEED_TYPE,
                                      x=1, y=1, count=want)
                added = int(receipt.get("fixture_added") or 0)
                seeded[owner] += added
                result.setdefault("spawn_receipts", []).append(
                    {"owner": owner, "added": added, "ok": receipt.get("ok"),
                     "reason": receipt.get("reason")})
                if added > 0:
                    progressed = True
            live = _live_count(pid, exist_base, capacity)
            result["peak_live"] = max(result["peak_live"], live)
            if live >= target_units:
                break
            if not progressed or live <= last_live:
                stalls += 1
            else:
                stalls = 0
            last_live = live
            if stalls >= 2 or all(v >= accelerate for v in seeded.values()):
                break
        result["live_after_fill"] = last_live
        if attack_test:
            result["attack_test"] = _attack_test(pid, supply, pool_base, exist_base, capacity)
        result["seeded_per_owner"] = seeded

        # Tick the AI and sample live count + a light pool/existence consistency check.
        t0 = time.monotonic()
        crashed = False
        while time.monotonic() - t0 < tick_seconds:
            if not Path(f"/proc/{pid}").exists():
                crashed = True
                first_fail = first_fail or {"when": "tick", "live": result["peak_live"]}
                break
            try:
                st = read_state(pid)
                live = _live_count(pid, exist_base, capacity)
                result["peak_live"] = max(result["peak_live"], live)
                # consistency: a few existing high slots must have nonzero type/hp
                sample_ok = True
                raw = read_memory(pid, exist_base, capacity * 2)
                highs = [i for i in range(capacity - 1, 0, -1)
                         if raw[2 * i] or raw[2 * i + 1]][:8]
                for slot in highs:
                    base = pool_base + slot * ESL2610_SPIKE_LAYOUT.unit_stride
                    hp = int.from_bytes(read_memory(pid, base + 0xB4, 4), "little", signed=True)
                    if hp <= 0:
                        sample_ok = False
                result["samples"].append({
                    "t": round(time.monotonic() - t0, 1), "ps": st.get("ps"),
                    "tick": st.get("tick"), "live": live, "high_slots_ok": sample_ok,
                    "highest_slot": highs[0] if highs else 0,
                    "unit_stats": _unit_stats(pid, pool_base, exist_base, capacity),
                    "players": _players(pid), "heroes": _hero_counts(pid),
                    "modules": _module_markers(pid, starts),
                    "module_state": _module_snapshot(pid, starts)})
                if st.get("ps") != 3:
                    crashed = True
                    first_fail = first_fail or {"when": "left_ps3", "ps": st.get("ps")}
                    break
            except (OSError, ValueError) as exc:
                result["samples"].append({"t": round(time.monotonic() - t0, 1), "error": str(exc)})
            time.sleep(sample_every)
        if save_test and not crashed and Path(f"/proc/{pid}").exists():
            result["save_test"] = _save_roundtrip(
                pid, supply, game, pool_base, exist_base, capacity, artifact_root,
                legacy_save=legacy_save, starts=starts)
            result["alive_after_save_test"] = Path(f"/proc/{pid}").exists()
        # after the save test: the second game starts from a fresh map
        if restart_test and not crashed and Path(f"/proc/{pid}").exists():
            result["restart_test"] = _restart_game(
                pid, display, env, log, click, artifact_root, pool_base, exist_base, capacity,
                starts)
        result["first_failure"] = first_fail
        result["crashed"] = crashed
        guard_log = prefix / "drive_c" / "g2_guard_fault.jsonl"
        if guard_log.exists():
            result["guard_log"] = guard_log.read_text(errors="replace").splitlines()[:50]
        exceeded = result["peak_live"] > 1200
        if heroes > 0:
            caps = [p["cap"] for p in result.get("after_heroes", {}).get("players", [])]
            result["supply_cap_5000_all_owners"] = (len(caps) == 8 and all(c == 5000 for c in caps))
        if variant == "base":
            ok = not exceeded and not crashed
            result["status"] = "CONTROL_CAPPED" if ok else "CONTROL_UNEXPECTED"
        else:
            result["status"] = live_acceptance_status(
                result, save_requested=save_test, guard_requested=guard,
                legacy_requested=legacy_save is not None, restart_requested=restart_test)
    except Exception as exc:  # noqa: BLE001
        result["status"] = "ERROR"
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        import shutil

        for child in children:
            if child.poll() is None:
                child.terminate()
        for child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
        if prefix is not None and "guard_log" not in result:
            guard_log = prefix / "drive_c" / "g2_guard_fault.jsonl"
            if guard_log.exists():
                result["guard_log"] = guard_log.read_text(errors="replace").splitlines()[:50]
        if prefix is not None:
            kenv = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win32")
            subprocess.run(["wineserver", "-k"], env=kenv, stdout=log, stderr=log,
                           timeout=15, check=False)
            subprocess.run(["wineserver", "-w"], env=kenv, stdout=log, stderr=log,
                           timeout=15, check=False)
            result["cleanup"]["prefix_processes_after"] = runtime_env._prefix_pids(prefix)
        if xvfb is not None and xvfb.poll() is None:
            xvfb.terminate()
        if game is not None and game.exists():
            shutil.rmtree(game, ignore_errors=True)
            result["cleanup"]["game_removed"] = not game.exists()
        log.close()
    (artifact_root / "live_result.json").write_text(json.dumps(result, indent=2))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("boot")
    b.add_argument("--variant", choices=["base", *CANDIDATE_VARIANTS], default="candidate")
    b.add_argument("--runtime-root", type=Path, required=True)
    b.add_argument("--artifact-root", type=Path, required=True)
    b.add_argument("--alive-seconds", type=float, default=30.0)
    live = sub.add_parser("live")
    live.add_argument("--variant", choices=["base", *CANDIDATE_VARIANTS], required=True)
    live.add_argument("--runtime-root", type=Path, required=True)
    live.add_argument("--artifact-root", type=Path, required=True)
    live.add_argument("--target-units", type=int, default=2000)
    live.add_argument("--tick-seconds", type=float, default=180.0)
    live.add_argument("--entry", choices=["eight_ai", "solo"], default="eight_ai")
    live.add_argument("--accelerate", type=int, default=150)
    live.add_argument("--ledger-reset", action="store_true")
    live.add_argument("--sample-every", type=float, default=15.0)
    live.add_argument("--g9", action="store_true", help="also stack G9 fixed start")
    live.add_argument("--no-guard", action="store_true",
                      help="do not arm PAGE_NOACCESS on the old storage")
    live.add_argument("--restart-test", action="store_true",
                      help="second game in the same process (pause -> restart)")
    live.add_argument("--save-test", action="store_true",
                      help="save the running game, play on, load it back, compare")
    live.add_argument("--legacy-save", type=Path, default=None,
                      help="also load this save (made by the official EXE); read-only input")
    live.add_argument("--attack-test", action="store_true",
                      help="DIAGNOSTIC: issue one original target order and trace it")
    live.add_argument("--low-slots", action="store_true",
                      help="SYNTHETIC diagnostic: make the allocator fill slots <1200 first")
    live.add_argument("--heroes", type=int, default=HEROES_PER_OWNER,
                      help="SYNTHETIC hero spawns per owner (0 disables)")
    args = parser.parse_args()
    if args.command == "boot":
        out = boot_probe(args.runtime_root, args.artifact_root,
                         variant=args.variant, alive_seconds=args.alive_seconds)
        print(json.dumps(out, indent=2))
    elif args.command == "live":
        out = live_probe(args.runtime_root, args.artifact_root, variant=args.variant,
                         target_units=args.target_units, tick_seconds=args.tick_seconds,
                         entry=args.entry, accelerate=args.accelerate,
                         ledger_reset=args.ledger_reset, sample_every=args.sample_every,
                         g9=args.g9, heroes=args.heroes, low_slots=args.low_slots,
                         attack_test=args.attack_test, save_test=args.save_test,
                         legacy_save=args.legacy_save, restart_test=args.restart_test,
                         guard=not args.no_guard)
        print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
