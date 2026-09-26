"""Regression contract for the v2-targeted variant of
``g5_worker_relative_move_attack_probe.py``.

2026-09-26 17:55 operator direction: run the same self-calibrated
``ever_command4_count`` measurement against the v2 (relocated selection,
unchunked) candidate to see whether ATTACK's ~0/49 sustain failure already
exists without any chunking involved. This module swaps the base probe's
``g5``/``TARGET_SHA`` module globals to point at v2 and restores them
afterward -- these tests pin that it targets the right SHA and puts the
swapped globals back so a later v3-targeted run in the same process is not
left pointed at v2.
"""

from __future__ import annotations

from patches.selection import g5_selection_cap50_v2 as g5_v2
from tools import g5_worker_relative_move_attack_probe as base
from tools import g5_worker_relative_move_attack_probe_v2 as v2_variant


def test_targets_the_v2_candidate_sha() -> None:
    assert v2_variant.TARGET_SHA == "ae495fa5a1498597c265ad9bcae6444f564ade92adb311a3c413c4fb9996b5b7"
    # Distinct from the base module's v3 candidate SHA -- this variant must
    # not silently fall back to building/verifying the v3 chunked candidate.
    assert v2_variant.TARGET_SHA != base.TARGET_SHA


def test_run_probe_restores_the_base_modules_g5_and_sha_globals() -> None:
    original_g5, original_sha = base.g5, base.TARGET_SHA
    called = {}

    def fake_base_run_probe(source, runtime_root, artifact_root, *, variant):
        called["g5_during_call"] = base.g5
        called["sha_during_call"] = base.TARGET_SHA
        return {"status": "FAKE"}

    real_run_probe, base.run_probe = base.run_probe, fake_base_run_probe
    try:
        result = v2_variant.run_probe(None, None, None, variant="candidate")
    finally:
        base.run_probe = real_run_probe

    assert result == {"status": "FAKE"}
    assert called["g5_during_call"] is g5_v2
    assert called["sha_during_call"] == v2_variant.TARGET_SHA
    assert base.g5 is original_g5
    assert base.TARGET_SHA == original_sha
