"""Pin test for the W24 Step D source change (N90), widened by W36 (lap527).

Card docs/work/active/G2_MIXED_COMPOSITION_COMBAT_CYCLE_SOAK_LAP461.md section
6-1 widened patches/population/runtime_bridge.c's op5/op6 fixture_type
allow-list from {5,7} to {5,7,46} (lap463). N90
(docs/history/laps/20260922_lap463_aborted_work_plus_middle_gate_recovery.md)
found that `make check`'s collected-test count did not change for this edit
-- no test in the suite reads runtime_bridge.c, so a further unreviewed
widening or a relaxed guard would pass the gate silently (same class as
N80-3). This file reads the C source text directly and pins the exact
allow-list plus the guards card section 0 and N88 forbid relaxing.

lap526 strategy §83 (K1-K7) + lap527 W36 card section 2-2 widened the
allow-list once more to {5,7,46,2}: N182 found the {5,7,46} seeded units all
lack the bit 0x4 attack-domain flag ("+0x1D8") and so are structurally unable
to engage; type 2 is the lowest-cost bit-0x4-capable type (N184) and is the
only additional entry K6 permits.

lap692 work widened the allow-list again to {5,7,46,2,28,29,104,108,103} for
the G2 전비10000 실측 (2026-09-26 21:54 사용자 판단 다음 우선순위). The pinned
type table (patches/population/verification_0910/type_costs.json) records
type 28/29/104/108 at cost 40 and type 103 at cost 65; live probing
(tools/g2_supply10000_type28_seed_probe.py) found 28/29/108 rejected by the
existing flags guard (unrelaxed) and only 104/103 gate-legal, and separately
found the original Gate (0x43eda0) enforces a real per-owner live-entity
ceiling near 242 (not the +0x2010 field's 250), so a single cost-40 type
cannot reach 10000 (242*40=9680<10000) -- cost-65 type103 plus a cost-35
type5 remainder reaches exactly 10000 within that real ceiling.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "patches/population/runtime_bridge.c"

ALLOWLIST_RE = re.compile(
    r"\(fixture_type != 5u && fixture_type != 7u && fixture_type != 46u && fixture_type != 2u &&\s*"
    r"fixture_type != 28u && fixture_type != 29u && fixture_type != 104u && fixture_type != 108u &&\s*"
    r"fixture_type != 103u\)"
)
FLAGS_GUARD_RE = re.compile(r"U32\(0x9b524cu\+type_offset\)&14u\) != 0")
DIMENSION_GUARD_RE = re.compile(r"width<1 \|\| width>8 \|\| height<1 \|\| height>8")
SUPPLY_GUARD_RE = re.compile(r'"fixture_exceeds_unreserved_supply"')
ACCOUNTING_GUARD_RE = re.compile(r'"spawn_accounting_mismatch"')
LOCK_GUARD_RE = re.compile(r'"fixture_locked_after_accounting_failure"')
PLACE_GATE_SPAWN_RE = re.compile(
    r"0x42ecb0u.*0x43eda0u.*0x443190u", re.DOTALL
)


def _source_text() -> str:
    return SOURCE.read_text(encoding="utf-8")


def test_fixture_type_allowlist_is_exactly_5_7_46_2_28_29_104_108_103():
    text = _source_text()
    assert ALLOWLIST_RE.search(text), (
        "op5/op6 fixture_type allow-list must be exactly "
        "{5,7,46,2,28,29,104,108,103} (card LAP461 section 6-1, widened by "
        "lap526 strategy §83 + W36 LAP527 section 2-2, then lap692 work for "
        "G2 전비10000); if this fails the allow-list changed without "
        "updating this pin"
    )


def test_allowlist_pin_is_not_vacuous():
    # Regression injection (N90): simulate an unauthorized further widening
    # and confirm the exact-match pin above would fail to match it. If this
    # assertion fails, ALLOWLIST_RE is too loose to catch a real widening.
    mutated = _source_text().replace(
        "fixture_type != 103u)", "fixture_type != 103u && fixture_type != 99u)"
    )
    assert mutated != _source_text()
    assert not ALLOWLIST_RE.search(mutated)


def test_flags_and_dimension_guards_unrelaxed():
    # N88: "(flags&14)!=0" reject and width/height 1..8 are original-engine
    # behaviour of unknown meaning; completing a seed by relaxing them is an
    # AGENTS.md violation regardless of build outcome.
    text = _source_text()
    assert FLAGS_GUARD_RE.search(text), "flags&14 guard must remain (N88)"
    assert DIMENSION_GUARD_RE.search(text), "width/height 1..8 guard must remain (N88)"


def test_accounting_and_lock_guards_present():
    text = _source_text()
    assert SUPPLY_GUARD_RE.search(text), "cap/unreserved-supply guard must remain"
    assert ACCOUNTING_GUARD_RE.search(text), "per-entity spawn accounting check must remain"
    assert LOCK_GUARD_RE.search(text), "fixture_failed latch must remain"


def test_place_gate_spawn_order_addresses_unchanged():
    text = _source_text()
    assert PLACE_GATE_SPAWN_RE.search(text), (
        "Place(0x42ecb0)->Gate(0x43eda0)->Spawn(0x443190) order and "
        "addresses must be unchanged (card LAP461 section 0-2 gate-legal path)"
    )
