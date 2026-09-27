"""Regression contract for lap685's exhaustive stock-selection-array xref scan.

2026-09-26 17:55 operator direction asked whether any code still reads the
*old* stock selection array (count 0x899024 / entries 0x899028 / end
0x899078) after v1's relocation, specifically in attack-related code. This
scan re-derives the reference inventory independently (Capstone IMM + MEM
operand scan across the whole ``.text`` section, not just v1's hand-picked
byte patterns) and found the same 52 raw byte occurrences the whole EXE
file has, all already covered by v1's ``DIRECT_SITES``/``END_SITES`` tables
-- zero residual. These tests pin the watched-address set and the "no
residual" result so a future v1 table edit that reintroduces a gap fails
loudly here instead of silently.
"""

from __future__ import annotations

from tools import g5_stock_selection_array_xrefs as xrefs
from tools import runtime_env


def test_watched_addresses_match_the_v1_relocation_triple() -> None:
    assert xrefs.STOCK_COUNT == 0x00899024
    assert xrefs.STOCK_ENTRIES == 0x00899028
    assert xrefs.STOCK_ENTRIES_ALT == 0x0089902A
    assert xrefs.STOCK_ENTRIES_END == 0x00899078
    assert xrefs.WATCHED_ADDRESSES == {
        0x00899024, 0x00899028, 0x0089902A, 0x00899078,
    }


def test_inventory_finds_no_residual_reference_in_the_original_exe() -> None:
    _, executable = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    result = xrefs.inventory(executable)
    assert result["residual_count"] == 0
    assert result["residual_hits"] == []
    assert result["total_hits"] > 0
    assert all(hit["already_handled"] for hit in result["hits"])
