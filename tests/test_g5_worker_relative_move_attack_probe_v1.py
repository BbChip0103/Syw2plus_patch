"""Regression contract for the v1-targeted variant of
``g5_worker_relative_move_attack_probe.py``.

2026-09-26 lap686: run the same self-calibrated ``ever_command4_count``
measurement against **v1 alone** (relocated selection, no control-group
hooks, no chunking) at full 49/50-selection scale, to localize lap685's
attack-broadcast regression to a specific v1/v2 edit bundle. These tests pin
that this variant targets v1's own candidate SHA and restores the base
module's swapped globals afterward.
"""

from __future__ import annotations

from patches.selection import g5_selection_cap50_v1 as g5_v1
from tools import g5_worker_relative_move_attack_probe as base
from tools import g5_worker_relative_move_attack_probe_v1 as v1_variant


def test_targets_the_v1_candidate_sha() -> None:
    assert v1_variant.TARGET_SHA == "6c8f73ba5626a978abaa09bb56adc46ee5da39bdd16d05c71285ce10d8f20b25"
    # Distinct from the base module's v3 candidate SHA and from v2's -- this
    # variant must not silently fall back to building/verifying a different
    # candidate.
    assert v1_variant.TARGET_SHA != base.TARGET_SHA


def test_run_probe_restores_the_base_modules_g5_and_sha_globals() -> None:
    original_g5, original_sha = base.g5, base.TARGET_SHA
    called = {}

    def fake_base_run_probe(source, runtime_root, artifact_root, *, variant):
        called["g5_during_call"] = base.g5
        called["sha_during_call"] = base.TARGET_SHA
        return {"status": "FAKE"}

    real_run_probe, base.run_probe = base.run_probe, fake_base_run_probe
    try:
        result = v1_variant.run_probe(None, None, None, variant="candidate")
    finally:
        base.run_probe = real_run_probe

    assert result == {"status": "FAKE"}
    assert called["g5_during_call"] is g5_v1
    assert called["sha_during_call"] == v1_variant.TARGET_SHA
    assert base.g5 is original_g5
    assert base.TARGET_SHA == original_sha
