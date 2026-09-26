from pathlib import Path


SOURCE = Path(__file__).parents[1] / "tools" / "inmm_stub" / "control_executor.c"


def _probe_body() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    start = text.index("static void g4_idle_attack_execute")
    end = text.index("/* ------------------------------------------------------------------ */", start)
    return text[start:end]


def test_probe_uses_pinned_original_high_level_order_issuer() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    body = _probe_body()
    assert "0x00415480u" in body
    assert "g4_issue_target_signature_ok()" in body
    assert "0x53, 0x56, 0x8B, 0xF1, 0x57, 0x8A" in text
    assert "original_target_order_admitted" in body


def test_probe_is_single_unit_and_does_not_write_active_command_fields() -> None:
    body = _probe_body()
    assert "issued < 1" in body
    assert "UA_OFF_CMD)) =" not in body
    assert "UA_OFF_TGT)) =" not in body


def test_probe_uses_mainthread_one_shot_and_bounded_result_labels() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert "static void WINAPI g4_idle_attack_mainthread" in text
    assert "InterlockedCompareExchange(&s_g4_order_once, 1, 0)" in text
    assert 'chb_call_handler(req->request_id, "g4_order_probe"' in text
    assert 'lstrcpynA(res->bridge_used, "g4_order_probe", sizeof(res->bridge_used))' in text
    assert "lstrcpynA(res->fallback_chain, detail, sizeof(res->fallback_chain))" in text


def test_waypoint_probe_is_mainthread_one_shot_and_uses_pinned_cdecl_issuer() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert '"_g4_idle_waypoint_reinforcement_probe"' in text
    assert "static void WINAPI g4_waypoint_mainthread" in text
    assert "InterlockedCompareExchange(&s_g4_waypoint_once, 1, 0)" in text
    assert 'chb_call_handler(req->request_id, "g4_waypoint_probe"' in text
    assert "FUN_004AEDE0" in text
    assert "0x004AEDE0u" in text
    assert "8B, 0x44, 0x24, 0x10" in text
    assert "0x8B, 0x0D" in text
    assert "0x54, 0x24, 0x0C, 0x6A, 0x00" in text
    assert "typedef void (__attribute__((cdecl)) *g4_waypoint_issue_fn)" in text


def test_waypoint_probe_guards_ai_waypoints_sources_and_membership() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    for token in (
        "0x00956770u", "0x3ABCu", "0x00B3DE34u", "0x00B3DE36u",
        "0x348Au", "0x3490u", "0x2E0u", "0xCBAu", "0x99Au",
        "0x384u", "0x388u", "0x29C", "0x290u",
    ):
        assert token in text
    assert "nation == 0" in text and "nation == 6" in text
    assert "ai != 1" in text
    assert "G4_ROUTE_COUNT           10" in text and "members < 1" in text
    assert "Chebyshev" in text or "dx > dy ? dx : dy" in text
    assert "g4_waypoint_member_contains" in text
    assert "source_full_id" in text
    assert "pending_after == 0x00010003u" in text
    assert "expected_xy = ((DWORD)(USHORT)target_y << 16)" in text
    assert "g4_waypoint_issue_fn" in text


def test_waypoint_probe_does_not_mutate_groups_or_roster_and_writes_bounded_json() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    body_start = text.index("static void g4_waypoint_execute")
    body_end = text.index("/* ------------------------------------------------------------------ */", body_start)
    body = text[body_start:body_end]
    assert "CreateFileA(\"C:\\\\inmm_g4_waypoint_probe.json\"" in body
    assert "g4_waypoint_json" in body
    assert "sizeof(g4_waypoint_json)" in body
    assert "player + 0x99A" not in body or "*=" not in body
    assert "player + 0xCBA" not in body or "*=" not in body
    assert "skip_reason" in text
    assert "admitted" in body
    assert "before_pending" in text and "after_pending" in text


def test_waypoint_result_summary_is_protocol_safe_and_tick_uses_simulation_clock() -> None:
    text = SOURCE.read_text(encoding="utf-8")
    assert '"calls=%d admitted=%d artifact=waypoint_json"' in text
    assert "G4_GLOBAL_TICK_VA       0x008924B8u" in text
    assert "json=C:\\\\inmm_g4_waypoint_probe.json" not in text
