"""Regression contract for the G5 order-issuer dynamic entry-count probe.

lap677 stopped guessing statically which function broadcasts an order to a
50-unit selection and instead traced live gdb breakpoint entry counts during
one known move click and one known attack-toolbar click. These are the
pure-logic pieces that do not require Wine/X11/gdb.
"""

from __future__ import annotations

from tools.g5_move_order_issuer_probe import GDB_SCRIPT, main, run_probe

# tools/g5_order_issuer_entry_trace.py imports ``gdb``, which only exists
# inside gdb's embedded interpreter, so it cannot be imported here; this
# mirrors its CANDIDATES dict as a regression pin instead (same pattern as
# the other gdb-only *.gdb/*_trace.py scripts in this repo, none of which
# have a pytest-importable counterpart).
CANDIDATE_ADDRESSES = {
    "op8_issuer_FUN_00415480": 0x00415480,
    "alt_issuer_FUN_00415880": 0x00415880,
    "group_assign_FUN_00445D30": 0x00445D30,
    "order_consumer_FUN_0040F7D0": 0x0040F7D0,
    "per_tick_dispatch_FUN_0048DDD0": 0x0048DDD0,
    "attack_tick_gate_FUN_00471AF0": 0x00471AF0,
    "selection_toggle_FUN_00412D90": 0x00412D90,
    "deselect_all_FUN_00417080": 0x00417080,
    "pending_order_consumer_FUN_0040C640": 0x0040C640,
}


def test_candidate_addresses_cover_every_previously_hypothesized_issuer() -> None:
    # Every function G5 laps 664-676 named as a possible broadcast issuer or
    # dispatch point must be in the traced set, or a live run cannot falsify
    # (or confirm) the standing hypotheses about it. Keep this pinned dict's
    # source-of-truth text (tools/g5_order_issuer_entry_trace.py CANDIDATES)
    # in sync by hand since it cannot be imported outside gdb.
    trace_script = GDB_SCRIPT.read_text(encoding="utf-8")
    for name, address in CANDIDATE_ADDRESSES.items():
        assert f'"{name}": 0x{address:08X}' in trace_script


def test_gdb_script_path_exists_next_to_the_probe() -> None:
    assert GDB_SCRIPT.name == "g5_order_issuer_entry_trace.py"
    assert GDB_SCRIPT.is_file()


def test_module_exposes_runtime_entry_points() -> None:
    assert callable(run_probe)
    assert callable(main)
