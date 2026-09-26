from pathlib import Path


BRIDGE = Path(__file__).parents[1] / "tools" / "inmm_stub" / "control_handler_bridge.c"
HEADER = Path(__file__).parents[1] / "tools" / "inmm_stub" / "control_handler_bridge.h"


def test_handler_slot_publishes_payload_after_claim() -> None:
    text = BRIDGE.read_text(encoding="utf-8")
    assert "CHB_SLOT_CLAIMED" in text
    claim = text.index("CHB_SLOT_CLAIMED")
    payload = text.index("s_handler_va = handler_va", claim)
    publish = text.index("InterlockedExchange(&s_slot_state, CHB_SLOT_PENDING)", payload)
    assert claim < payload < publish


def test_mainthread_drain_only_executes_published_pending_slot() -> None:
    text = BRIDGE.read_text(encoding="utf-8")
    assert "CHB_SLOT_CLAIMED" in HEADER.read_text(encoding="utf-8")
    drain = text.index("void chb_drain_slot_mainthread")
    body = text[drain:]
    assert "CHB_SLOT_PENDING" in body
    assert "if (st != CHB_SLOT_PENDING)" in body
    assert "CHB_SLOT_CLAIMED" not in body
