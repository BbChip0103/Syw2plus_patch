"""Pure helpers of the ESL2610 G2 spike runtime probe (no Wine)."""

from __future__ import annotations

from tools import g2_esl2610_spike_probe as probe


def test_layout_for_control_is_the_stock_1200_pool() -> None:
    assert probe._layout_for("base") == (0x0066B790, 0x008990C8, 1200)


def test_layout_for_candidate_is_the_relocated_g2bss_pool() -> None:
    pool, exist, cap = probe._layout_for("candidate")
    assert (pool, exist, cap) == (0x01AB5000, 0x0220B9F8, 4093)
    # existence follows the grown 4093-slot pool directly (packed geometry)
    assert exist - pool == 0x758 * 4093


def test_kill_marker_region_is_the_kills_per_slot_array() -> None:
    assert probe.KILLDAT_SLOT_BASE == 0x0115C000


def _good_live_result() -> dict[str, object]:
    owners = list(range(8))
    return {
        "peak_live": 1400, "crashed": False, "active_owners": owners,
        "synthetic_heroes_per_owner": 7,
        "samples": [{"live": 1300, "high_slots_ok": True, "highest_slot": 1300, "ps": 3, "tick": 100},
                    {"live": 1400, "high_slots_ok": True, "highest_slot": 1400, "ps": 3, "tick": 110}],
        "guard_log": ['{"armed": 22}'],
        "after_heroes": {"players": [{"owner": owner, "cap": 5000} for owner in owners]},
        "save_test": {"save_receipt": {"ok": True, "op": 2}, "save_files": ["save005.dat"],
                      "save_size": 123, "slots_ge_1200_before": 20, "slots_ge_1200_after": 20,
                      "load_receipt": {"ok": True, "op": 3}, "restored_exact": True},
        "alive_after_save_test": True,
    }


def test_live_acceptance_requires_complete_eight_owner_guard_cap_and_save_evidence() -> None:
    result = _good_live_result()
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_OK_EXCEEDED_1200"


def test_live_acceptance_rejects_partial_or_bad_samples_and_malformed_owner_caps() -> None:
    result = _good_live_result()
    result["samples"] = []
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"
    result = _good_live_result()
    result["samples"] = [{"live": 1300, "high_slots_ok": False, "highest_slot": 1300, "ps": 3}]
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"
    result = _good_live_result()
    result["active_owners"] = list(range(7))
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"
    result = _good_live_result()
    result["after_heroes"] = {"players": [{"owner": owner, "cap": 6000} for owner in range(8)]}
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"


def test_live_acceptance_does_not_call_guard_arm_record_a_fault() -> None:
    result = _good_live_result()
    result["guard_log"] = ['{"armed": 22}', '{"fault":"PAGE_NOACCESS","eip":"0x401000"}']
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"
    result = _good_live_result()
    result["guard_log"] = ['{"armed": 1}']
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"


def test_live_acceptance_requires_tick_progress_inside_the_live_window() -> None:
    result = _good_live_result()
    result["samples"][1]["tick"] = 100
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"
    result["samples"][1]["tick"] = None
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"


def test_live_acceptance_requires_requested_save_load_and_nonpartial_guard() -> None:
    result = _good_live_result()
    result["save_test"] = {"save_receipt": {"ok": True, "op": 2}, "save_files": [],
                           "load_receipt": {"ok": True, "op": 3}, "restored_exact": True}
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"
    result = _good_live_result()
    result["guard_log"] = []
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_PARTIAL_EXCEEDED_1200"
    result = _good_live_result()
    result["samples"][0]["highest_slot"] = 1200
    assert probe.live_acceptance_status(result, save_requested=True, guard_requested=True) == "LIVE_OK_EXCEEDED_1200"
