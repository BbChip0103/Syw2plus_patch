"""Contract pin for the W42 (lap548/lap549 card section 2) op9 addition to
runtime_bridge.c.

op9 is the G2 S1 (라) diagnostic: issue one original move order via the
unmodified issuer FUN_004AEDE0 (cdecl, N203 signature
`8B 44 24 10 8B 0D 78 5C 9E 00 8B 54`). Card section 2 requires this branch
to:
  1. check the issuer's 12-byte signature before calling it,
  2. contain zero U8/U16/U32 write-assignments (it only reads and calls the
     original function; only that original call may mutate state),
  3. never write PlayerStruct+5,
  4. leave op4's fixture write, the op5/op6/op8 allow-lists, and the op8
     contract untouched (card section 1/2 boundary).
2026-09-24 14:31 KST user approval widened the operation gate from
`op > 8` to `op > 9` (tracked by
tests/test_g2_runtime_bridge_op8_order_engagement_contract.py, updated in
the same change) so op9 requests can reach this branch.
If this fails, op9 changed in a way the W42 card forbids without a new
middle/strategy review.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "patches/population/runtime_bridge.c"

WRITE_ASSIGN_RE = re.compile(r"U(?:8|16|32)\([^)]*\)\s*=[^=]")
MOVE_SIGNATURE_RE = re.compile(
    r"move_sig\[\]\s*=\s*\{0x8B,0x44,0x24,0x10,0x8B,0x0D,0x78,0x5C,\s*"
    r"0x9E,0x00,0x8B,0x54\}"
)
SAME_BYTES_CALL_RE = re.compile(
    r"same_bytes\(0x4aede0u,\s*move_sig,\s*sizeof\(move_sig\)\)"
)
PLAYER_STRUCT_5_WRITE_RE = re.compile(r"0x05[^)]*\)\s*=[^=]")
OP_GATE_RE = re.compile(r"owner >= 8 \|\| op > 9")


def _source_text() -> str:
    return SOURCE.read_text(encoding="utf-8")


def _op9_branch_text() -> str:
    text = _source_text()
    start = text.index("} else if (op == 9) {")
    end = text.index("\n        ledger(after,owner);", start)
    assert start < end, "op9 branch boundaries not found as expected"
    return text[start:end]


def test_op9_branch_exists():
    text = _source_text()
    assert "} else if (op == 9) {" in text, "op9 branch must exist (W42 card section 2)"


def test_operation_gate_widened_from_8_to_9():
    assert OP_GATE_RE.search(_source_text()), (
        "operation gate must accept op<=9 (2026-09-24 14:31 user approval, "
        "W42 card section 2)"
    )


def test_op9_checks_move_issuer_signature_before_calling():
    branch = _op9_branch_text()
    assert MOVE_SIGNATURE_RE.search(branch), (
        "op9 must pin the exact 12-byte FUN_004AEDE0 signature "
        "(N203, `8B 44 24 10 8B 0D 78 5C 9E 00 8B 54`)"
    )
    assert SAME_BYTES_CALL_RE.search(branch), (
        "op9 must fail-closed on same_bytes(0x4aede0u, move_sig, ...) "
        "before issuing the order"
    )
    sig_pos = MOVE_SIGNATURE_RE.search(branch).start()
    call_pos = branch.index("(Move)0x4aede0u")
    assert sig_pos < call_pos, "signature check must precede the order call"


def test_op9_has_zero_write_assignments():
    branch = _op9_branch_text()
    matches = WRITE_ASSIGN_RE.findall(branch)
    assert not matches, (
        "op9 must not write via U8()=/U16()=/U32()= -- only the original "
        f"engine call may mutate state (card section 2); found: {matches}"
    )


def test_op9_never_writes_player_struct_plus5():
    branch = _op9_branch_text()
    assert not PLAYER_STRUCT_5_WRITE_RE.search(branch), (
        "op9 must never write PlayerStruct+5 (side byte)"
    )


def test_op9_validates_destination_bounds():
    branch = _op9_branch_text()
    assert '"bad_move_destination"' in branch
    assert "move_map_w" in branch and "move_map_h" in branch


def test_op8_branch_untouched_by_op9():
    text = _source_text()
    assert "} else if (op == 8) {" in text
    op8_start = text.index("} else if (op == 8) {")
    op9_start = text.index("} else if (op == 9) {")
    assert op8_start < op9_start
    op8_branch = text[op8_start:op9_start]
    assert "issuer_sig" in op8_branch
    assert "move_sig" not in op8_branch
