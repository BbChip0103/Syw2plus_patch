"""Contract pin for the W35 (lap523 card) op8 addition to runtime_bridge.c.

op8 is the G2 S0 diagnostic: issue one original target-order via the
unmodified issuer FUN_00415480 (thiscall, ret 0x0C, signature
`53 56 8B F1 57 8A 86 1C 03 00 00 84`). Card section 0-3/1 requires this
branch to read PlayerStruct+5 (the side byte, N177) but never write it or
use it to gate the call -- admission is decided entirely by the original
engine call, not by this bridge. This file pins that op8:
  1. checks the issuer's 12-byte signature before calling it,
  2. contains zero U16/U32/U8 write-assignments (it only reads and calls
     the original function; only that original call may mutate state),
  3. validates target uid low-16 bits == target slot (N178) before calling,
  4. never writes PlayerStruct+5,
  5. left the pre-existing op4 fixture write and op>7 gate change to op>8
     as the only other source changes (card section 1).
If this fails, op8 changed in a way the W35 card forbids without a new
middle/strategy review.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "patches/population/runtime_bridge.c"

WRITE_ASSIGN_RE = re.compile(r"U(?:8|16|32)\([^)]*\)\s*=[^=]")
SIGNATURE_RE = re.compile(
    r"issuer_sig\[\]\s*=\s*\{0x53,0x56,0x8B,0xF1,0x57,0x8A,\s*"
    r"0x86,0x1C,0x03,0x00,0x00,0x84\}"
)
SAME_BYTES_CALL_RE = re.compile(
    r"same_bytes\(0x415480u,\s*issuer_sig,\s*sizeof\(issuer_sig\)\)"
)
UID_SLOT_CHECK_RE = re.compile(
    r"\(U32\(tgt_unit\+0x29c\)\s*&\s*0xffffu\)\s*!=\s*tgt_slot"
)
PLAYER_STRUCT_5_WRITE_RE = re.compile(r"0x05[^)]*\)\s*=[^=]")
OP_GATE_RE = re.compile(r"owner >= 8 \|\| op > 9")
OLD_OP_GATE_RE = re.compile(r"op > 7\b")


def _source_text() -> str:
    return SOURCE.read_text(encoding="utf-8")


def _op8_branch_text() -> str:
    text = _source_text()
    start = text.index("} else if (op == 8) {")
    end = text.index("\n        ledger(after,owner);", start)
    assert start < end, "op8 branch boundaries not found as expected"
    return text[start:end]


def test_op8_branch_exists():
    text = _source_text()
    assert "} else if (op == 8) {" in text, "op8 branch must exist (W35 card section 1)"


def test_op8_checks_issuer_signature_before_calling():
    branch = _op8_branch_text()
    assert SIGNATURE_RE.search(branch), (
        "op8 must pin the exact 12-byte FUN_00415480 signature "
        "(N177 contract doc, `53 56 8B F1 57 8A 86 1C 03 00 00 84`)"
    )
    assert SAME_BYTES_CALL_RE.search(branch), (
        "op8 must fail-closed on same_bytes(0x415480u, issuer_sig, ...) "
        "before issuing the order"
    )
    sig_pos = SIGNATURE_RE.search(branch).start()
    call_pos = branch.index("(Issue)0x415480u")
    assert sig_pos < call_pos, "signature check must precede the order call"


def test_op8_has_zero_write_assignments():
    branch = _op8_branch_text()
    matches = WRITE_ASSIGN_RE.findall(branch)
    assert not matches, (
        "op8 must not write via U8()=/U16()=/U32()= -- only the original "
        f"engine call may mutate state (card section 1); found: {matches}"
    )


def test_op8_validates_target_uid_low16_equals_slot():
    branch = _op8_branch_text()
    assert UID_SLOT_CHECK_RE.search(branch), (
        "op8 must fail-closed on (target uid & 0xFFFF) == tgt_slot before "
        "calling (N178, contract doc section 4)"
    )
    assert '"target_uid_slot_mismatch"' in branch


def test_op8_never_writes_player_struct_plus5():
    branch = _op8_branch_text()
    assert not PLAYER_STRUCT_5_WRITE_RE.search(branch), (
        "op8 must never write PlayerStruct+5 (side byte); it may only "
        "read it for reporting (card section 0-3)"
    )
    assert "pp+0x05" in branch, "op8 must still report the 8-owner side byte array (N177)"


def test_op8_reads_all_eight_owner_side_bytes():
    branch = _op8_branch_text()
    assert "po < 8" in branch
    assert "pp+0x00" in branch and "pp+0x02" in branch and "pp+0x05" in branch


def test_operation_gate_widened_from_7_to_8():
    text = _source_text()
    assert OP_GATE_RE.search(text), "operation gate must accept op<=8 (card section 1)"
    assert not OLD_OP_GATE_RE.search(text), (
        "the old op>7 gate text must not remain anywhere in the source"
    )


def test_op4_fixture_write_unchanged():
    text = _source_text()
    assert 'U16(p+0x200c)=(USHORT)request[7];' in text, (
        "op4's single ledger write must be unchanged (card section 1, "
        "op8 must not touch op4)"
    )
    op4_start = text.index("} else if (op == 4) {")
    op4_end = text.index("} else if (op == 7) {", op4_start)
    op4_branch = text[op4_start:op4_end]
    writes = WRITE_ASSIGN_RE.findall(op4_branch)
    assert len(writes) == 1, f"op4 write count changed unexpectedly: {writes}"


def test_fixture_type_allowlist_unrelaxed():
    text = _source_text()
    assert (
        "fixture_type != 5u && fixture_type != 7u && fixture_type != 46u "
        "&& fixture_type != 2u"
    ) in text, (
        "op5/op6 allow-list revised to {5,7,46,2} in W36(lap527) "
        "(card §83); must not be further relaxed"
    )
