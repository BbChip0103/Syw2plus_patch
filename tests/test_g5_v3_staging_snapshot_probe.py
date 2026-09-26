"""Regression contract for lap685's v3 staging/dispatch-loop tracers.

lap685 compared MOVE (type 3, stable 50/50 per lap682) against ATTACK
(type 4, reproducible ~0/49 sustained per lap684) through the v3 chunked
order-record builder. ``g5_v3_staging_snapshot_probe.py`` found the staging
record at 0x893130 is byte-identical across all 3 chunk calls for *both*
order types (ruling that path in/out symmetrically), and
``g5_v3_pending_broadcast_loop_probe.py`` found the real per-unit writer
dispatch loop (0x4aec60) is entered exactly 50 times for both MOVE and
ATTACK -- so the divergence is not in the chunked builder-to-writer path at
all. The gdb trace scripts themselves import ``gdb`` (only available inside
gdb's embedded interpreter), so their address/contract pins are regression-
tested here instead of being imported.
"""

from __future__ import annotations

from tools.g5_v3_staging_snapshot_probe import GDB_SCRIPT as STAGING_GDB_SCRIPT
from tools.g5_v3_staging_snapshot_probe import main as staging_main
from tools.g5_v3_staging_snapshot_probe import run_probe as staging_run_probe
from tools.g5_v3_pending_broadcast_loop_probe import TARGET_SHA as LOOP_TARGET_SHA
from tools.g5_v3_pending_broadcast_loop_probe import main as loop_main
from tools.g5_v3_pending_broadcast_loop_probe import run_probe as loop_run_probe


def test_staging_snapshot_trace_pins_the_confirmed_addresses() -> None:
    # The gdb trace script itself imports ``gdb`` (only available inside
    # gdb's embedded interpreter), so its address pins are checked as text
    # rather than by importing the module.
    text = STAGING_GDB_SCRIPT.read_text(encoding="utf-8")
    assert "0x00893130" in text
    assert "0x008931E8" in text
    # Right after `call 0x004A3C10` inside the single relocated body copy
    # the v3 wrapper invokes up to 3 times per chunked order.
    assert "0x004E4F37" in text
    assert "return False" in text


def test_staging_snapshot_probe_targets_the_v3_chunked_candidate() -> None:
    assert STAGING_GDB_SCRIPT.name == "g5_v3_staging_snapshot_trace.py"
    assert STAGING_GDB_SCRIPT.is_file()
    assert callable(staging_run_probe)
    assert callable(staging_main)


def test_loop_probe_targets_the_v3_chunked_candidate_sha() -> None:
    assert LOOP_TARGET_SHA == "e5004764e945350a0391d69035f8c8f0d305fcca7d6aaa54066836bac3de6977"
    assert callable(loop_run_probe)
    assert callable(loop_main)
