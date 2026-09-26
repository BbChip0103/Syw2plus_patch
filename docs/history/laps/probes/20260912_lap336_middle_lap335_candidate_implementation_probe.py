#!/usr/bin/env python3
"""lap336 middle probe — independent review of the lap335 candidate R1 implementation.

Design note (applies lap334 N12): this probe asserts only *stable structural*
invariants of the source. It never asserts that a live mutable file still has a
previously reviewed SHA, because such an assertion invalidates itself the moment
the reviewed lane is legitimately edited (the lap296 W3 trap, and the reason the
lap332/lap334 probes now exit 1). Live SHAs and open findings are *reported* as
data so a later repair does not have to re-pin anything to make this pass.

No game execution, no memory access, no input, no PNG, no writes outside stdout.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tools import runtime_env  # noqa: E402

failures: list[str] = []
findings: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_of(name: str) -> str:
    text = (REPO / "tools/runtime_env.py").read_text(encoding="utf-8")
    start = text.index(f"def {name}(")
    tail = text[start:]
    end = re.search(r"\n(?=def |class )", tail)
    return tail[: end.start()] if end else tail


# --- 1. artifact / lock / log name separation (protects the lap332 exact-once assertion)
candidate_src = source_of("g1_r1_candidate_load_origin")
original_src = source_of("g1_r1_load_origin")
check('"r1_load_origin_candidate.json"' in candidate_src, "candidate artifact name is not separated")
check('".r1-load-origin-candidate.lock"' in candidate_src, "candidate lock name is not separated")
check('"r1_load_origin_candidate.log"' in candidate_src, "candidate log name is not separated")
check('"r1_load_origin_candidate.json"' not in original_src, "original path gained the candidate artifact name")
check('output / "r1_load_origin.json"' in original_src, "original artifact name changed")
check('".r1-load-origin.lock"' in original_src, "original lock name changed")

# --- 2. repo-wide artifact counts stay as reviewed at lap332
originals = sorted(REPO.glob("local/runtime/*/output/r1_load_origin.json"))
candidates = sorted(REPO.glob("local/runtime/*/output/r1_load_origin_candidate.json"))
check(len(originals) == 1, f"original R1 artifact count is {len(originals)}, expected exactly 1")
check(len(candidates) == 0, f"candidate artifact count is {len(candidates)}, expected 0 before the run")

# --- 3. the click is unscaled (the lap148 x2 FAIL must not come back)
geometry = runtime_env._g1_input_geometry((100, 200, 1600, 1200), (2.0, 2.0), 296, 505)
check(geometry["x11"] == [396, 705], "shared input geometry pre-scaled the logical point")
candidate_geometry = runtime_env._g1_r1_candidate_click_geometry((100, 200, 1600, 1200))
check(candidate_geometry["x11"] == [396, 705], "candidate click is not content_crop + (296,505)")
check(candidate_geometry["content"] == [296, 505], "candidate click lost the logical point")
check(candidate_geometry["scale_applied"] == [1.0, 1.0], "candidate did not declare scale_applied=1 (N11)")
check(runtime_env.G1_R1_CLICK_POINT == (296, 505), "R1 click point drifted")

# --- 4. candidate geometry gate: only physical 1600x1200 content passes
ok_window = runtime_env._g1_r1_candidate_geometry_gate(
    {"x": 0, "y": 0, "width": 1600, "height": 1200},
    {"x": 8, "y": 9, "width": 1600, "height": 1200},
)
check(ok_window["logical_size"] == [800, 600] and ok_window["scale"] == [2.0, 2.0],
      "candidate geometry gate lost the logical/scale contract")
for root, content, label in (
    ({"width": 1600, "height": 1200}, {"width": 800, "height": 600}, "800x600 content"),
    ({"width": 800, "height": 600}, {"width": 1600, "height": 1200}, "800x600 root"),
):
    try:
        runtime_env._g1_r1_candidate_geometry_gate(root, content)
    except runtime_env._G1R1CandidatePreconditionError as exc:
        record = runtime_env._g1_r1_candidate_precondition_record(exc)
        check(record["classification"] == "BLOCKED_PRECONDITION" and record["status"] == "UNKNOWN",
              f"{label} did not classify as BLOCKED_PRECONDITION")
    else:
        failures.append(f"candidate geometry gate accepted {label}")

# --- 5. candidate module gate: private ddraw only, forbidden syw2x, fail-closed on hashes
import tempfile  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    game = Path(tmp) / "game"
    game.mkdir()
    ddraw = game / "ddraw.dll"
    ddraw.write_bytes(b"private-ddraw-bytes")
    good = sha256(ddraw)
    base = {"maps_raw": f"{ddraw}\n", "modules": [{"path": str(ddraw), "sha256": good}]}
    passed = runtime_env._g1_r1_candidate_module_gate(base, game, {"ddraw.dll": good})
    check(passed["status"] == "PASS" and passed["syw2x_loaded"] is False,
          "candidate module gate rejected the private ddraw case")
    other = Path(tmp) / "system32-ddraw.dll"
    other.write_bytes(b"builtin")
    rejects = {
        "syw2x loaded": ({**base, "maps_raw": f"{ddraw}\n/x/SYW2X.dll\n"}, {"ddraw.dll": good}),
        "two ddraw modules": (
            {"maps_raw": f"{ddraw}\n{other}\n",
             "modules": [{"path": str(ddraw), "sha256": good},
                         {"path": str(other), "sha256": sha256(other)}]},
            {"ddraw.dll": good},
        ),
        "hash mismatch": (base, {"ddraw.dll": "0" * 64}),
        "missing expected hash": (base, {}),
        "foreign ddraw path": (
            {"maps_raw": f"{other}\n", "modules": [{"path": str(other), "sha256": sha256(other)}]},
            {"ddraw.dll": good},
        ),
        "no module list": ({"maps_raw": ""}, {"ddraw.dll": good}),
    }
    for label, (evidence, hashes) in rejects.items():
        try:
            runtime_env._g1_r1_candidate_module_gate(evidence, game, hashes)
        except runtime_env._G1R1CandidatePreconditionError:
            pass
        else:
            failures.append(f"candidate module gate accepted: {label}")

# --- 6. the five declared failure modes are reachable and none of them is a PASS
modes = {
    "NOT_REACHED": runtime_env._g1_r1_candidate_wait_failure_record(
        runtime_env._G1WaitTimeout("synthetic", classification="FAIL_NO_EFFECT", last=None,
                                   finished_elapsed=1.0, remaining_budget_after=0.0,
                                   observation={})),
    "TIMEOUT": runtime_env._g1_r1_candidate_wait_failure_record(
        runtime_env._G1WaitTimeout("synthetic", classification="UNKNOWN_BUDGET_EXHAUSTED", last=None,
                                   finished_elapsed=1.0, remaining_budget_after=0.0,
                                   observation={})),
    "COLLECTION_ERROR": runtime_env._g1_r1_candidate_wait_failure_record(
        runtime_env._G1WaitTimeout("synthetic", classification="UNKNOWN_STATE_READ_FAILURE", last=None,
                                   finished_elapsed=1.0, remaining_budget_after=0.0,
                                   observation={})),
    "NO_CHANGE": runtime_env._g1_r1_candidate_compare_origin(
        {"x": 0, "y": 0, "tag": 0}, {"x": 0, "y": 0, "tag": 0}),
    "BLOCKED_PRECONDITION": runtime_env._g1_r1_candidate_precondition_record(
        runtime_env._G1R1CandidatePreconditionError("synthetic gate", details={})),
}
for expected, record in modes.items():
    check(record["classification"] == expected, f"failure mode {expected} did not classify as itself")
    check(record["status"] == "UNKNOWN", f"failure mode {expected} was not held at UNKNOWN")
changed = runtime_env._g1_r1_candidate_compare_origin(
    {"x": 0, "y": 0, "tag": 0}, {"x": 240, "y": 145, "tag": 8})
check(changed["status"] == "OBSERVED" and changed["classification"] == "REACHED_CHANGED",
      "a changed origin no longer classifies as REACHED_CHANGED")

# --- 7. cleanup contract cannot be satisfied while a restore failed
restored = runtime_env._g1_r1_candidate_cleanup_record(
    owned_launchers_stopped=True, xvfb_stopped=True, prefix_target=Path("/p"),
    prefix_processes_after=[], cleanup_error=None, dxwrapper_config_restored=True)
check(restored["ok"] is True, "a fully clean candidate teardown did not report ok")
for label, kwargs in {
    "restore not performed": {"dxwrapper_config_restored": False},
    "restore error": {"dxwrapper_config_restored": True, "dxwrapper_config_error": "boom"},
    "survivor pid": {"dxwrapper_config_restored": True, "prefix_processes_after": [4242]},
    "wineserver error": {"dxwrapper_config_restored": True, "cleanup_error": "wineserver failed"},
}.items():
    args = {"owned_launchers_stopped": True, "xvfb_stopped": True, "prefix_target": Path("/p"),
            "prefix_processes_after": [], "cleanup_error": None, **kwargs}
    check(runtime_env._g1_r1_candidate_cleanup_record(**args)["ok"] is False,
          f"cleanup reported ok despite: {label}")

# --- 8. original lane behaviour is unchanged where the two lanes share code
check(runtime_env._game_window_ids.__defaults__ is None, "unexpected positional defaults")
check(re.search(r"allowed_sizes: tuple\[tuple\[int, int\], \.\.\.\] = \(\(800, 600\),\)",
                source_of("_game_window_ids")) is not None,
      "shared window helper no longer defaults to the original 800x600 contract")
check("_game_window_ids(tree)" in original_src, "original lane no longer uses the default window gate")
check('WINEDLLOVERRIDES="ddraw=b"' in original_src, "original lane DLL override changed")
check('WINEDLLOVERRIDES="ddraw=n,b"' in candidate_src, "candidate lane does not force the native ddraw")
check('"800x600"' in original_src or "800x600" in original_src, "original 800x600 gate text vanished")

# --- 9. candidate preconditions must run before the single click
click_at = candidate_src.index("x11_mouse_click.py")
for marker, label in (
    ("_g1_r1_candidate_module_gate(", "module gate"),
    ("_g1_r1_candidate_geometry_gate(", "geometry gate"),
    ("candidate PS=9 origin was not (0,0,0)", "PS9 origin precondition"),
    ("_g1_r1_candidate_click_geometry(", "unscaled click geometry"),
):
    check(marker in candidate_src and candidate_src.index(marker) < click_at,
          f"{label} does not precede the single permitted click")
check(candidate_src.count("x11_mouse_click.py") == 1, "candidate contains more than one click site")
check('"count": 1' in candidate_src, "candidate does not record exactly one input")
check("uninstall_private" in candidate_src and "finally:" in candidate_src,
      "candidate does not restore the dxwrapper profile in a finally block")
check(runtime_env.G1_R1_WAIT_PS_STATES == (9, 35), "R1 wait states drifted")

# --- reported observations (never asserted, so a later repair need not re-pin anything)
live = {
    "tools/runtime_env.py": sha256(REPO / "tools/runtime_env.py"),
    "tests/test_lap326_r1_load_origin.py": sha256(REPO / "tests/test_lap326_r1_load_origin.py"),
}
test_text = (REPO / "tests/test_lap326_r1_load_origin.py").read_text(encoding="utf-8")
if "r1_load_origin_candidate.json" not in test_text:
    findings.append("lap334 §11.3 required an artifact-name-separation test; no test asserts "
                    "r1_load_origin_candidate.json or .r1-load-origin-candidate.lock")
if "stage_started=launch_started" in candidate_src:
    findings.append("candidate PS9 stage budget starts after the dxwrapper install, so lap334 §8 "
                    "'prepare/PS9 <= 40s' is not enforced over the install stage")
for probe in ("20260912_lap332_middle_lap331_r1_artifact_probe.py",
              "20260912_lap334_middle_candidate_r1_envelope_probe.py"):
    path = REPO / "docs/history/laps/probes" / probe
    rc = subprocess.run([sys.executable, str(path)], capture_output=True, cwd=REPO).returncode
    if rc != 0:
        findings.append(f"{probe} now exits {rc}: it pins the lap330 harness SHA, which the "
                        "lap334-authorised lap335 edit legitimately changed (W3-shaped trap)")

print(json.dumps({
    "lap": 336,
    "role": "middle",
    "scope": "independent review of the lap335 candidate R1 implementation; no execution",
    "live_sha256": live,
    "original_artifacts": [str(p.relative_to(REPO)) for p in originals],
    "candidate_artifacts": [str(p.relative_to(REPO)) for p in candidates],
    "findings": findings,
    "failures": failures,
}, ensure_ascii=False, indent=2))
sys.exit(1 if failures else 0)
