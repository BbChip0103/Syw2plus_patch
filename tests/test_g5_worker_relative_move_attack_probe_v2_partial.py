"""Regression contract for the H1/H2/H3-partial variant probe wrapper.

2026-09-26 lap687: three candidates, each v2 (v1 + control-group hooks) minus
exactly one hook, run through the same dense-50 MOVE+ATTACK convergence
probe used to measure V1_FULL/V2_FULL in lap686. These tests pin that the
wrapper computes a fresh candidate SHA per ``--skip-hook`` (no stale hardcoded
pin), swaps the base module's globals only for the call, and restores them
afterward even when the probe itself raises.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from patches.selection import g5_selection_cap50_v2_partial as partial
from tools import g5_worker_relative_move_attack_probe as base
from tools import g5_worker_relative_move_attack_probe_v2_partial as wrapper

SOURCE = Path(__file__).resolve().parents[1] / "Syw2plus/syw2plus_original.exe"


def test_rejects_unknown_hook() -> None:
    with pytest.raises(ValueError):
        wrapper.run_probe(Path("/nonexistent"), Path("/nonexistent"), Path("/nonexistent"), variant="candidate", skip_hook="H4")


def test_original_variant_does_not_build_a_candidate(monkeypatch: pytest.MonkeyPatch) -> None:
    original_g5, original_sha = base.g5, base.TARGET_SHA
    called: dict[str, object] = {}

    def fake_base_run_probe(source, runtime_root, artifact_root, *, variant):
        called["g5_during_call"] = base.g5
        called["sha_during_call"] = base.TARGET_SHA
        return {"status": "FAKE"}

    monkeypatch.setattr(base, "run_probe", fake_base_run_probe)
    result = wrapper.run_probe(Path("/nonexistent"), None, None, variant="original", skip_hook="H2")

    assert result == {"status": "FAKE", "skip_hook": "H2"}
    # "original" never calls build_candidate, so TARGET_SHA is untouched.
    assert called["sha_during_call"] == original_sha
    assert base.g5 is original_g5
    assert base.TARGET_SHA == original_sha


def test_candidate_variant_computes_a_fresh_sha_and_restores_globals(monkeypatch: pytest.MonkeyPatch) -> None:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    original_g5, original_sha = base.g5, base.TARGET_SHA
    called: dict[str, object] = {}

    def fake_base_run_probe(source, runtime_root, artifact_root, *, variant):
        called["g5_during_call"] = base.g5
        called["sha_during_call"] = base.TARGET_SHA
        return {"status": "FAKE"}

    monkeypatch.setattr(base, "run_probe", fake_base_run_probe)
    result = wrapper.run_probe(SOURCE.parent, None, None, variant="candidate", skip_hook="H3")

    expected_sha = partial.build_candidate(SOURCE.read_bytes(), skip="H3")[1]["candidate_sha256"]
    assert result == {"status": "FAKE", "skip_hook": "H3"}
    assert called["sha_during_call"] == expected_sha
    assert called["g5_during_call"] is not original_g5
    assert base.g5 is original_g5
    assert base.TARGET_SHA == original_sha


def test_candidate_variant_restores_globals_even_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    original_g5, original_sha = base.g5, base.TARGET_SHA

    def raising_base_run_probe(source, runtime_root, artifact_root, *, variant):
        raise RuntimeError("boom")

    monkeypatch.setattr(base, "run_probe", raising_base_run_probe)
    with pytest.raises(RuntimeError):
        wrapper.run_probe(SOURCE.parent, None, None, variant="candidate", skip_hook="H1")

    assert base.g5 is original_g5
    assert base.TARGET_SHA == original_sha
