"""Regression contract for the G5 pending-broadcast direct-field-value probe.

lap677 found that raw gdb entry counts into ``FUN_0040C640`` cannot answer
"how many of the 50 selected units actually received a pending order" --
that function runs once per live unit every tick regardless of pending
state. This probe instead snapshots ``unit+0x384`` for every selected unit
the instant that function is entered, right after the click under test. The
gdb trace script itself imports ``gdb`` (only available inside gdb's
embedded interpreter), so its atomic-read/marker-file contract is pinned
here as a regression instead of being imported.
"""

from __future__ import annotations

from tools.g5_pending_broadcast_snapshot_probe import (
    GDB_SCRIPT,
    main,
    run_probe,
    sparse_fixture_requests,
)
from tools.g5_candidate_drag_probe import SEED_COUNT


def test_sparse_fixture_covers_full_seed_count_with_no_adjacent_cells() -> None:
    worker = {"x": 90, "y": 90}
    requests = sparse_fixture_requests(worker)
    assert sum(item["count"] for item in requests) == SEED_COUNT
    coords = {(item["x"], item["y"]) for item in requests}
    assert len(coords) == len(requests)
    # Every pair of distinct cells is at least 2 tiles apart on some axis
    # from its nearest neighbour on the same row/column (step-2 grid), so no
    # two fixture units share or border a tile -- unlike the dense 7x8
    # step-1 grid this probe can also select via --fixture-layout dense.
    xs = sorted({item["x"] for item in requests})
    ys = sorted({item["y"] for item in requests})
    assert all(b - a == 2 for a, b in zip(xs, xs[1:]))
    assert all(b - a == 2 for a, b in zip(ys, ys[1:]))


def test_sparse_fixture_stays_inside_the_map() -> None:
    worker = {"x": 90, "y": 90}
    requests = sparse_fixture_requests(worker)
    assert all(0 <= item["x"] < 180 and 0 <= item["y"] < 180 for item in requests)


def test_gdb_snapshot_script_path_exists_next_to_the_probe() -> None:
    assert GDB_SCRIPT.name == "g5_pending_broadcast_snapshot_trace.py"
    assert GDB_SCRIPT.is_file()


def test_gdb_snapshot_script_reads_pending_field_atomically_at_consumer_entry() -> None:
    # Pin the exact consumer-entry address and the non-invasive stop()->False
    # contract lap677 established: the breakpoint must never actually halt
    # the game, only pause for the duration of one memory read.
    text = GDB_SCRIPT.read_text(encoding="utf-8")
    assert "0x0040C640" in text
    assert "return False" in text
    assert "PENDING_OFFSET" in text
    assert "click_marker" in text


def test_module_exposes_runtime_entry_points() -> None:
    assert callable(run_probe)
    assert callable(main)
