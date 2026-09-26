"""Regression contract for the G5 pending-broadcast loop/staging tracers.

lap678 traced the confirmed 20/50 pending-broadcast boundary
(``g5_pending_broadcast_snapshot_probe.py``) down through the per-unit
writer (``0x412540``), its wrapper (``0x40ff90``), the dispatcher
(``0x4aec60``), and the enqueue function (``0x4ae660``) that reads a
count word from a hardcoded record base (``0x8931ec``) -- all the way to a
60-byte order-staging record at ``0x893130`` whose unit-list sub-array has
room for exactly 20 word-encoded slots. The gdb trace scripts themselves
import ``gdb`` (only available inside gdb's embedded interpreter), so their
address/contract pins are regression-tested here instead of being imported.
"""

from __future__ import annotations

from tools.g5_pending_broadcast_loop_probe import GDB_SCRIPT as LOOP_GDB_SCRIPT
from tools.g5_pending_broadcast_loop_probe import main as loop_main
from tools.g5_pending_broadcast_loop_probe import run_probe as loop_run_probe
from tools.g5_pending_broadcast_staging_probe import GDB_SCRIPT as STAGING_GDB_SCRIPT
from tools.g5_pending_broadcast_staging_probe import STAGING_BASE, WATCHES
from tools.g5_pending_broadcast_staging_probe import main as staging_main
from tools.g5_pending_broadcast_staging_probe import run_probe as staging_run_probe


def test_loop_entry_trace_script_pins_wrapper_and_dispatch_addresses() -> None:
    assert LOOP_GDB_SCRIPT.name == "g5_pending_broadcast_loop_entry_trace.py"
    text = LOOP_GDB_SCRIPT.read_text(encoding="utf-8")
    assert "0x0040FF90" in text
    assert "0x004AEC60" in text
    assert "return False" in text


def test_staging_probe_watches_the_confirmed_60_byte_record_base() -> None:
    assert STAGING_BASE == 0x00893130
    addresses = {item["address"] for item in WATCHES}
    assert hex(STAGING_BASE) in addresses
    assert hex(STAGING_BASE + 0xA) in addresses
    assert hex(STAGING_BASE + 0x14) in addresses


def test_staging_probe_reuses_the_pinned_writer_trace_script() -> None:
    assert STAGING_GDB_SCRIPT.name == "g5_pending_broadcast_writer_trace.py"
    assert STAGING_GDB_SCRIPT.is_file()


def test_modules_expose_runtime_entry_points() -> None:
    assert callable(loop_run_probe)
    assert callable(loop_main)
    assert callable(staging_run_probe)
    assert callable(staging_main)
