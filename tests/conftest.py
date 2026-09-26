"""Keep subprocess-based loop tests independent of the caller's loop settings."""

import os

import pytest


@pytest.fixture(autouse=True)
def clear_inherited_loop_environment(monkeypatch: pytest.MonkeyPatch):
    """Remove inherited LOOP_* settings while preserving PATH and test overrides."""
    for name in tuple(os.environ):
        if name.startswith("LOOP_"):
            monkeypatch.delenv(name)
