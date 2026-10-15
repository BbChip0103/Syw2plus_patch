from types import SimpleNamespace

import pytest

from patches.esl2610 import g2_bounds_2610


def _fake_operand(address=0x1000, value=0x4B0):
    insn = SimpleNamespace(address=address, mnemonic="cmp", op_str="eax, 0x4b0")
    return (".profile", insn, "imm", value, 4)


def test_default_capacity_table_behavior_is_unchanged(monkeypatch):
    operand = _fake_operand()
    monkeypatch.setattr(g2_bounds_2610, "_classified", lambda: {})
    monkeypatch.setattr(g2_bounds_2610, "family_operands", lambda _data: iter([operand]))
    with pytest.raises(ValueError, match="1 undecided 1200-family operands"):
        g2_bounds_2610.build_table(b"", set())


@pytest.mark.parametrize(
    "row, message",
    [
        ({"size": 4, "kind": "imm", "decision": "raise", "why": "profile"}, "incomplete"),
        ({"old": 0x4AE, "size": 4, "kind": "imm", "decision": "raise", "why": "profile"}, "preimage"),
        ({"old": 0x4B0, "size": 4, "kind": "imm", "decision": "raise"}, "incomplete"),
    ],
)
def test_explicit_decisions_fail_closed_without_exact_preimage_and_rationale(monkeypatch, row, message):
    monkeypatch.setattr(g2_bounds_2610, "_classified", lambda: {})
    monkeypatch.setattr(g2_bounds_2610, "family_operands", lambda _data: iter([_fake_operand()]))
    with pytest.raises(ValueError, match=message):
        g2_bounds_2610.build_table(b"", set(), {0x1000: row})


def test_explicit_decisions_are_consumed_and_exact(monkeypatch):
    monkeypatch.setattr(g2_bounds_2610, "_classified", lambda: {})
    monkeypatch.setattr(g2_bounds_2610, "family_operands", lambda _data: iter([_fake_operand()]))
    row = {"old": 0x4B0, "size": 4, "kind": "imm", "decision": "raise", "why": "profile slot bound"}
    table = g2_bounds_2610.build_table(b"", set(), {0x1000: row})
    assert table == [{"va": 0x1000, "section": ".profile", "insn": "cmp eax, 0x4b0",
                      "kind": "imm", "old": 0x4B0, "size": 4, "decision": "raise",
                      "why": "profile slot bound", "new": g2_bounds_2610.new_value(0x4B0)}]
    monkeypatch.setattr(g2_bounds_2610, "family_operands", lambda _data: iter([]))
    with pytest.raises(ValueError, match="unused explicit capacity decisions"):
        g2_bounds_2610.build_table(b"", set(), {0x2000: row})
