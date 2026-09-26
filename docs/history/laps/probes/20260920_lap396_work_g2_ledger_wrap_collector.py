#!/usr/bin/env python3
"""lap396 work — G2 work card W2 (ESCALATE_SOL section 9, `G2_SUPPLY_LEDGER_WRAP_PROBE_LAP395.md`).

Measures the two structural unknowns lap395 left open:

  M-a: the maximum per-unit cost `c_max` among unit types actually present in the
       pinned save000 fixture, read live from the runtime cost table `0x9B5238`
       (`&DAT_009b5238 + (short)type * 0x394`, i16 LE, offset 0 -- confirmed by
       reading `FUN_0043eda0` in `Syw2plus_re/analysis/ghidra_output/FUN_0043eda0.c`).
       This table lives in `.data` BSS past the raw section end and cannot be read
       statically (lap395 FO-2); it requires a live process.
  M-b: `min(1200, pool) * c_max` vs the signed16 ceiling 32767 (roster array
       capacity 1200 = `cmp ax,0x4B0` in `roster_add 0x43EE30`, per lap395 A5).

Also opportunistically cross-checks M-e (ledger `+0x200C` vs a roster-cost-sum
recomputed from the same detailed snapshot's live units) -- not requested to be
exact since the two reads (`state(pid)` reads players, then units, sequentially)
are not atomic against the live simulation clock; documented as a caveat.

M-c/M-d (induce one real transfer, then one real reproduction, through in-game
actions such as capture/embark/charm) were **not attempted** -- this is recorded
as BLOCKED per the card's explicit allowance ("M-c/M-d를 유도하지 못하면 억지로
만들지 말고 BLOCKED라고 적는다"); M-a/M-b answer the decisive question on their
own (see verdict below) and GUI-driven unit capture was out of this round's
budget.

Fixture: existing isolated full-game copy `/home/dev_00/syw2plus-run` (original
EXE, verified SHA256 below), dedicated Wine prefix, unused Xvfb display, reused
`save000.dat` (no new save/scenario fixture created). Read-only: `process_vm_readv`
polling and the driver's `click`/`read`/`snapshot` ops only -- no
`process_vm_writev`/`ptrace`/debugger, no binary/memory writes, no baseline edits.

This script performs the live collection itself (so its artifact is a fresh,
directly-observed sample, not a hand transcription -- N16 avoidance) and writes
one JSON artifact with embedded SHA256 of every raw read. Run manually; it starts
Wine/Xvfb/the game and is intentionally excluded from `make check`, matching the
existing convention for `docs/history/laps/probes/*` (lap339 confirmed no
required gate executes this directory).

Usage: python3 docs/history/laps/probes/20260920_lap396_work_g2_ledger_wrap_collector.py
"""
from __future__ import annotations

import hashlib
import json
import struct
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
GAME_ROOT = Path("/home/dev_00/syw2plus-run")
PREFIX = Path("/home/dev_00/.wine_syw2_396b")
DISPLAY = ":396"
OUT_SESSION = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/"
    "20260919_owner_transfer_cap/lap396_work_ledger_wrap_probe/session"
)
ARTIFACT_DIR = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/"
    "20260919_owner_transfer_cap/lap396_work_ledger_wrap_probe"
)

EXPECTED_ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
EXPECTED_SAVE000_SHA256 = "1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da"

# Title menu grid: click (297,506) = row1/col3 "불러오기" (Load) -> PS7 to PS35.
# Then click (316,372) = the load dialog's "불러오기" confirm button on the
# already-selected slot 1 -> PS35 to PS3 (matches STATUS's established S1 chain).
LOAD_MENU_ENTRY_CLICK = (297, 506)
LOAD_DIALOG_CONFIRM_CLICK = (316, 372)
PROGRAM_STATE_TITLE = 7
PROGRAM_STATE_LOAD_DIALOG = 35
PROGRAM_STATE_LOAD_COMPLETE = 3

COST_TABLE_BASE = 0x9B5238
COST_TABLE_STRIDE = 0x394
ROSTER_ARRAY_CAPACITY = 1200
SIGNED16_MAX = 32767


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class DriverClient:
    def __init__(self, out_dir: Path):
        self.out_dir = out_dir

    def send(self, op: str, timeout: float = 30.0, **kwargs) -> dict:
        req_id = str(time.time())
        request = {"id": req_id, "op": op, **kwargs}
        tmp = self.out_dir / "request.json.tmp"
        tmp.write_text(json.dumps(request))
        tmp.replace(self.out_dir / "request.json")
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                response = json.loads((self.out_dir / "response.json").read_text())
                if response.get("id") == req_id:
                    if "error" in response:
                        raise RuntimeError(f"driver op {op} failed: {response['error']}")
                    return response
            except (OSError, ValueError):
                pass
            time.sleep(0.1)
        raise TimeoutError(f"no driver response for op={op}")

    def wait_ps(self, target: int, timeout: float = 30.0) -> int:
        deadline = time.time() + timeout
        last = None
        while time.time() < deadline:
            try:
                latest = json.loads((self.out_dir / "latest.json").read_text())
                last = latest.get("ps")
                if last == target:
                    return last
            except (OSError, ValueError):
                pass
            time.sleep(0.5)
        raise TimeoutError(f"PS did not reach {target} within {timeout}s (last observed {last})")


def collect() -> dict:
    original = GAME_ROOT / "syw2plus_original.exe"
    save000 = GAME_ROOT / "save" / "save000.dat"
    original_sha = sha(original.read_bytes())
    save000_sha = sha(save000.read_bytes())
    if original_sha != EXPECTED_ORIGINAL_SHA256:
        raise SystemExit(f"original EXE SHA mismatch: {original_sha}")
    if save000_sha != EXPECTED_SAVE000_SHA256:
        raise SystemExit(f"save000 SHA mismatch: {save000_sha}")

    OUT_SESSION.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    driver = subprocess.Popen(
        [
            sys.executable, str(REPO / "patches/population/runtime_driver.py"),
            "--game-root", str(GAME_ROOT), "--prefix", str(PREFIX),
            "--out", str(OUT_SESSION), "--display", DISPLAY,
            "--exe", "syw2plus_original.exe", "--screen", "1024x768",
        ]
    )
    client = DriverClient(OUT_SESSION)
    try:
        deadline = time.time() + 30
        while not (OUT_SESSION / "session.json").exists():
            if time.time() > deadline:
                raise TimeoutError("runtime_driver session.json did not appear")
            time.sleep(0.5)
        session = json.loads((OUT_SESSION / "session.json").read_text())
        if session["exe_sha256"] != EXPECTED_ORIGINAL_SHA256:
            raise SystemExit("session exe_sha256 mismatch")

        client.wait_ps(9, timeout=30)
        # PS9 (loading) -> PS7 (title) is automatic once assets finish loading.
        client.wait_ps(PROGRAM_STATE_TITLE, timeout=60)
        client.send("click", x=LOAD_MENU_ENTRY_CLICK[0], y=LOAD_MENU_ENTRY_CLICK[1])
        client.wait_ps(PROGRAM_STATE_LOAD_DIALOG, timeout=15)
        client.send("click", x=LOAD_DIALOG_CONFIRM_CLICK[0], y=LOAD_DIALOG_CONFIRM_CLICK[1])
        client.wait_ps(PROGRAM_STATE_LOAD_COMPLETE, timeout=30)

        snapshot_response = client.send("snapshot", timeout=30)
        state = snapshot_response["state"]
        units = state["units"]
        types_observed = sorted({u["type"] for u in units})
        type_min, type_max = min(types_observed), max(types_observed)
        read_size = (type_max - type_min) * COST_TABLE_STRIDE + 2
        read_va = COST_TABLE_BASE + type_min * COST_TABLE_STRIDE
        cost_read = client.send("read", va=hex(read_va), size=read_size, timeout=30)
        cost_bytes = bytes.fromhex(cost_read["hex"])
        if len(cost_bytes) != read_size:
            raise SystemExit(f"short cost-table read: {len(cost_bytes)}/{read_size}")

        client.send("stop", timeout=10)
    finally:
        driver.wait(timeout=30)

    return {
        "state": state,
        "types_observed": types_observed,
        "cost_table": {
            "base": hex(COST_TABLE_BASE),
            "stride": hex(COST_TABLE_STRIDE),
            "read_va": hex(read_va),
            "read_size": read_size,
            "raw_hex": cost_bytes.hex(),
            "raw_sha256": sha(cost_bytes),
        },
        "fixture": {
            "original_exe_sha256": original_sha,
            "save000_sha256": save000_sha,
            "session": session,
        },
    }


def analyze(collected: dict) -> dict:
    cost_table = collected["cost_table"]
    data = bytes.fromhex(cost_table["raw_hex"])
    if sha(data) != cost_table["raw_sha256"]:
        raise SystemExit("cost table raw bytes do not match their own recorded SHA256")
    type_min = int(cost_table["read_va"], 16)
    type_min = (type_min - COST_TABLE_BASE) // COST_TABLE_STRIDE
    types_observed = collected["types_observed"]

    costs_by_type: dict[int, int] = {}
    for t in types_observed:
        offset = (t - type_min) * COST_TABLE_STRIDE
        costs_by_type[t] = struct.unpack_from("<h", data, offset)[0]

    c_max = max(costs_by_type.values())
    c_max_type = [t for t, c in costs_by_type.items() if c == c_max]
    structural_bound = ROSTER_ARRAY_CAPACITY * c_max
    m_b_exceeds_ceiling = structural_bound > SIGNED16_MAX

    state = collected["state"]
    units = state["units"]
    players = state["players"]
    roster_cost_sum: dict[int, int] = {}
    roster_unit_count: dict[int, int] = {}
    for u in units:
        owner = u["owner"]
        roster_cost_sum[owner] = roster_cost_sum.get(owner, 0) + costs_by_type.get(u["type"], 0)
        roster_unit_count[owner] = roster_unit_count.get(owner, 0) + 1

    m_e_rows = []
    for p in players:
        owner = p["owner"]
        ledger_used = p["used"]
        computed = roster_cost_sum.get(owner, 0)
        m_e_rows.append({
            "owner": owner,
            "ledger_used": ledger_used,
            "roster_cost_sum": computed,
            "ledger_count": p["count"],
            "roster_unit_count": roster_unit_count.get(owner, 0),
            "delta": ledger_used - computed,
        })

    return {
        "costs_by_type": costs_by_type,
        "c_max": c_max,
        "c_max_types": c_max_type,
        "roster_array_capacity": ROSTER_ARRAY_CAPACITY,
        "structural_bound_min1200_x_cmax": structural_bound,
        "signed16_max": SIGNED16_MAX,
        "m_b_verdict": "EXCEEDS_CEILING" if m_b_exceeds_ceiling else "WITHIN_CEILING",
        "m_e_rows": m_e_rows,
        "m_e_caveat": (
            "state()'s player-struct read and its unit-pool read are two separate "
            "process_vm_readv calls while the simulation keeps ticking; small deltas "
            "here are expected timing noise, not asserted as an alias/bypass writer"
        ),
    }


def main() -> int:
    collected = collect()
    analysis = analyze(collected)
    output = {
        "probe": Path(__file__).name,
        "lap": 396,
        "fixture": collected["fixture"],
        "types_observed": collected["types_observed"],
        "unit_count": len(collected["state"]["units"]),
        "cost_table": {k: v for k, v in collected["cost_table"].items() if k != "raw_hex"},
        "cost_table_raw_hex_sha256": collected["cost_table"]["raw_sha256"],
        "analysis": analysis,
        "m_c_m_d": "BLOCKED_NOT_ATTEMPTED — in-game transfer/reproduction (capture/embark/charm) "
                   "requires GUI navigation beyond this round's budget; M-a/M-b already answer the "
                   "decisive question (see m_b_verdict)",
    }
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = ARTIFACT_DIR / "output.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
    print(json.dumps({
        "c_max": analysis["c_max"],
        "c_max_types": analysis["c_max_types"],
        "structural_bound": analysis["structural_bound_min1200_x_cmax"],
        "m_b_verdict": analysis["m_b_verdict"],
        "output_path": str(out_path),
        "output_sha256": sha(out_path.read_bytes()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
