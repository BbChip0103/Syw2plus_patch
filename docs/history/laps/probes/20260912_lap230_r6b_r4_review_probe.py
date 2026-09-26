"""lap230 middle-tier independent probe for G1-R6-B-R4.

Read-only review instrument: it imports tools.runtime_env and exercises
`_g1_selection_responded` / `_wait_state` with synthetic fake-clock observations.
No game, no EXE/DLL, no product code change.

Each case states the reviewer's expectation independently of the lap229 record,
then reports AGREES / DEFECT.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from tools import runtime_env  # noqa: E402

SOUND_A = {"count": 1, "selected_slot": 1199, "selected_type": 70}
SOUND_B = {"count": 2, "selected_slot": 1198, "selected_type": 21}
CORRUPT_TYPE = {
    "count": 1, "selected_slot": 1199, "selected_type": "UNKNOWN",
    "selected_type_provenance": "OSError: transient selected-unit read failure",
}
CORRUPT_NEG = {
    "count": -1, "selected_slot": None, "selected_type": "UNKNOWN",
    "selected_type_provenance": "unsupported selected-unit count",
}
ZERO = {"count": 0, "selected_slot": None, "selected_type": "UNKNOWN",
        "selected_type_provenance": "no selected unit: selection count is zero"}

results: list[tuple[str, str, str]] = []


def report(name: str, expected: Any, actual: Any, note: str = "") -> None:
    verdict = "AGREES" if expected == actual else "DEFECT"
    results.append((name, verdict, f"expected={expected!r} actual={actual!r} {note}".strip()))


def fake_clock(monkey_store: list[float]) -> None:
    runtime_env.time.monotonic = lambda: monkey_store[0]  # type: ignore[assignment]
    runtime_env.time.sleep = (  # type: ignore[assignment]
        lambda seconds: monkey_store.__setitem__(0, monkey_store[0] + seconds)
    )


def run_wait(
    reader: Callable[[bool], dict[str, Any]], before: dict[str, Any],
    *, timeout: float = 10.0, stage_budget: float | None = 1.0,
    stage_started: float = 0.0,
) -> tuple[str | None, dict[str, Any]]:
    """Return (classification, wait_observation) for a timed-out selection wait."""
    real_monotonic = runtime_env.time.monotonic
    real_sleep = runtime_env.time.sleep
    clock = [0.0]
    fake_clock(clock)
    obs: dict[str, Any] = {}
    try:
        runtime_env._wait_state(
            reader,
            lambda item: runtime_env._g1_selection_responded(
                before, item, diagnostics=obs,
            ),
            started=0.0, timeout=timeout, message="probe wait",
            stage="drag_select", stage_budget=stage_budget,
            stage_started=stage_started, wait_observation=obs,
        )
    except runtime_env._G1WaitTimeout as exc:
        return exc.classification, exc.observation
    finally:
        runtime_env.time.monotonic = real_monotonic  # type: ignore[assignment]
        runtime_env.time.sleep = real_sleep  # type: ignore[assignment]
    return None, obs


# --- C1 predicate-level: final status must follow the final poll -------------
diag: dict[str, Any] = {}
runtime_env._g1_selection_responded(SOUND_A, CORRUPT_TYPE, diagnostics=diag)
runtime_env._g1_selection_responded(SOUND_A, SOUND_A, diagnostics=diag)
report("C1a stale CORRUPTED cleared by sound final poll",
       "SOUND", diag["selection_observation"]["status"])
report("C1b corrupted history retained",
       1, diag["selection_observation"]["corrupted_poll_count"])

diag = {}
runtime_env._g1_selection_responded(SOUND_A, SOUND_A, diagnostics=diag)
runtime_env._g1_selection_responded(SOUND_A, CORRUPT_NEG, diagnostics=diag)
report("C1c sound-then-corrupt final poll is CORRUPTED",
       "CORRUPTED", diag["selection_observation"]["status"])

diag = {}
for observation in (CORRUPT_TYPE, SOUND_A, CORRUPT_NEG, SOUND_A, CORRUPT_TYPE):
    runtime_env._g1_selection_responded(SOUND_A, observation, diagnostics=diag)
sel = diag["selection_observation"]
report("C1d alternating polls count only corrupt polls", 3, sel["corrupted_poll_count"])
report("C1e first provenance is the first corrupt poll",
       "OSError: transient selected-unit read failure",
       sel["first_corruption_provenance"]["after"]["selected_type_provenance"])
report("C1f last provenance is the last corrupt poll",
       "OSError: transient selected-unit read failure",
       sel["last_corruption_provenance"]["after"]["selected_type_provenance"])
report("C1g provenance stays bounded to 2 entries", True,
       set(sel) == {
           "status", "before_sound", "after_sound", "before", "after",
           "corrupted_poll_count", "first_corruption_provenance",
           "last_corruption_provenance",
       })

# --- C2 R6-B-R2 / R6-B-R3 semantics must be unchanged ------------------------
report("C2a count 1->0 still counts as a response", True,
       runtime_env._g1_selection_responded(SOUND_A, ZERO))
report("C2b negative count still fails closed", False,
       runtime_env._g1_selection_responded(SOUND_A, CORRUPT_NEG))
report("C2c bool count rejected", False,
       runtime_env._g1_selection_responded(SOUND_A, {"count": True, "selected_slot": 1, "selected_type": 7}))
report("C2d float count rejected", False,
       runtime_env._g1_selection_responded(SOUND_A, {"count": 1.0, "selected_slot": 1, "selected_type": 7}))
report("C2e genuine change still responds", True,
       runtime_env._g1_selection_responded(SOUND_A, SOUND_B))

# --- C3 wait-level W1/W2/W3 --------------------------------------------------
cls, obs = run_wait(lambda _d: CORRUPT_NEG, SOUND_A)
report("C3a W1 persistent corruption -> UNKNOWN",
       "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED", cls)

polls = iter([CORRUPT_TYPE, CORRUPT_NEG])
cls, obs = run_wait(lambda _d: next(polls, SOUND_A), SOUND_A)
report("C3b W3 transient corruption then sound no-effect -> FAIL_NO_EFFECT",
       "FAIL_NO_EFFECT", cls)
report("C3c W3 keeps corruption history", 2,
       obs["selection_observation"]["corrupted_poll_count"])
report("C3d W3 final status SOUND", "SOUND", obs["selection_observation"]["status"])

polls = iter([CORRUPT_TYPE, SOUND_B])
cls, obs = run_wait(lambda _d: next(polls, SOUND_A), SOUND_A)
report("C3e W2 corruption then real response returns (no timeout)", None, cls)
report("C3f W2 returning status is SOUND", "SOUND", obs["selection_observation"]["status"])
report("C3g W2 retains corruption history", 1,
       obs["selection_observation"]["corrupted_poll_count"])

polls = iter([SOUND_A, SOUND_A, CORRUPT_TYPE])
cls, obs = run_wait(lambda _d: next(polls, CORRUPT_TYPE), SOUND_A)
report("C3h corruption on the final polls -> UNKNOWN",
       "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED", cls)

# --- C4 corrupted `before` poisons every poll (must stay fail-closed) --------
cls, obs = run_wait(lambda _d: SOUND_A, CORRUPT_NEG)
report("C4a corrupt before-observation -> UNKNOWN",
       "UNKNOWN_SELECTION_OBSERVATION_CORRUPTED", cls)

# --- C5 reader exceptions: observation never reaches the predicate -----------
def raising_reader(_detailed: bool) -> dict[str, Any]:
    raise OSError("probe: selected-unit read failed")


cls, obs = run_wait(raising_reader, SOUND_A)
report("C5a every poll unreadable -> must not be a hard FAIL_NO_EFFECT",
       True, cls != "FAIL_NO_EFFECT",
       f"classification={cls}; selection_observation="
       f"{'absent' if 'selection_observation' not in obs else obs['selection_observation']['status']}")


def sound_then_raise() -> Callable[[bool], dict[str, Any]]:
    state = {"n": 0}

    def reader(_detailed: bool) -> dict[str, Any]:
        state["n"] += 1
        if state["n"] <= 2:
            return SOUND_A
        raise OSError("probe: selected-unit read failed")

    return reader


cls, obs = run_wait(sound_then_raise(), SOUND_A)
report("C5b sound polls then unreadable tail -> must not be a hard FAIL_NO_EFFECT",
       True, cls != "FAIL_NO_EFFECT",
       f"classification={cls}; final status="
       f"{obs.get('selection_observation', {}).get('status')}; "
       f"poll_count={obs.get('poll_count')}")

# --- C6 tampered previous diagnostics -----------------------------------------
diag = {"selection_observation": {"corrupted_poll_count": -5}}
runtime_env._g1_selection_responded(SOUND_A, CORRUPT_TYPE, diagnostics=diag)
report("C6a negative previous count resets before increment", 1,
       diag["selection_observation"]["corrupted_poll_count"])
diag = {"selection_observation": {"corrupted_poll_count": True}}
runtime_env._g1_selection_responded(SOUND_A, CORRUPT_TYPE, diagnostics=diag)
report("C6b bool previous count resets before increment", 1,
       diag["selection_observation"]["corrupted_poll_count"])

# --- report -------------------------------------------------------------------
defects = [row for row in results if row[1] == "DEFECT"]
for name, verdict, detail in results:
    print(f"{verdict:7s} {name}: {detail}")
print(f"\nTOTAL {len(results)} cases: {len(results) - len(defects)} AGREES, {len(defects)} DEFECT")
