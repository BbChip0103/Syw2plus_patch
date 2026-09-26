#!/usr/bin/env python3
"""lap346 middle probe: independently review the preserved lap345 candidate R1 run.

This probe is read-only.  It does not import or invoke the runtime harness, start
Wine/Xvfb, inject input, or update any pin/baseline.  Its inputs are the preserved
artifact, manifest, private run files, and the reviewed live source fingerprints.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
RUN = REPO / "local/runtime/20260912_191422_3558862_0"
ARTIFACT = RUN / "output/r1_load_origin_candidate.json"
LOG = RUN / "output/r1_load_origin_candidate.log"
MANIFEST = RUN / "manifest.json"
LOCK = RUN / ".r1-load-origin-candidate.lock"

ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
HARNESS_SHA = "965e370989fdad63ec09da25a3f5b3f3a3c66e364d668ab1d48965e141ddb547b"
TEST_SHA = "891b60ebb87cb44de38ae64a69d952378b976b82bb99f90498f628a7e15b4265"
MANIFEST_SHA = "d2fc6095909d3a2735ee3b544d9e067ad738cb3290a5446a205e5cf5425308fc"
ARTIFACT_SHA = "dd8cd3502edb66e08a1d2514cd8b4b26622da73531ca503adf2f3a6e71b37634"
LOG_SHA = "0c7455a2f469e157a221f6d35c8c79377cd4d231b84d5d02b9784f5ba3103a71"
DDRAW_SHA = "3bc7230d1a6023a8fc0ea52b18d7edda94fcb4c0ae3d178f6e1577d68a62bd19"
INI_ORIGINAL_SHA = "918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2"
INI_CANDIDATE_SHA = "f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785"

failures: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        failures.append(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


evidence: dict[str, Any] = json.loads(ARTIFACT.read_text(encoding="utf-8"))
manifest: dict[str, Any] = json.loads(MANIFEST.read_text(encoding="utf-8"))

# Artifact integrity, reviewed source identity, and the separately named lane.
observed_sha = {
    "artifact": sha256(ARTIFACT),
    "log": sha256(LOG),
    "manifest": sha256(MANIFEST),
    "harness": sha256(REPO / "tools/runtime_env.py"),
    "test": sha256(REPO / "tests/test_lap326_r1_load_origin.py"),
    "run_exe": sha256(RUN / "game/syw2plus_original.exe"),
    "source_exe": sha256(
        Path(manifest["source"]["root"]) / manifest["source"]["exe"]
    ),
    "ddraw": sha256(RUN / "game/ddraw.dll"),
    "restored_ini": sha256(RUN / "game/dxwrapper.ini"),
}
expected_sha = {
    "artifact": ARTIFACT_SHA,
    "log": LOG_SHA,
    "manifest": MANIFEST_SHA,
    "harness": HARNESS_SHA,
    "test": TEST_SHA,
    "run_exe": ORIGINAL_SHA,
    "source_exe": ORIGINAL_SHA,
    "ddraw": DDRAW_SHA,
    "restored_ini": INI_ORIGINAL_SHA,
}
for name, expected in expected_sha.items():
    check(observed_sha[name] == expected, f"{name} SHA differs from the reviewed/recorded value")

candidate_artifacts = sorted(REPO.glob("local/runtime/*/output/r1_load_origin_candidate.json"))
candidate_locks = sorted(REPO.glob("local/runtime/*/.r1-load-origin-candidate.lock"))
original_artifacts = sorted(REPO.glob("local/runtime/*/output/r1_load_origin.json"))
check(candidate_artifacts == [ARTIFACT], "candidate lane does not contain exactly the lap345 artifact")
check(candidate_locks == [LOCK], "candidate lane does not contain exactly the lap345 lock")
check(len(original_artifacts) == 1, "the separately preserved original R1 lane changed cardinality")
check(not list((RUN / "output").glob("*.png")), "candidate R1 output contains forbidden PNGs")
check(
    MANIFEST.stat().st_mtime_ns <= LOCK.stat().st_mtime_ns <= LOG.stat().st_mtime_ns
    <= ARTIFACT.stat().st_mtime_ns,
    "manifest/lock/log/artifact timestamps are not in run order",
)

# Fresh private-copy manifest and same-run path binding.
run_root = RUN.resolve()
check(manifest["run_id"] == RUN.name, "manifest run_id differs from its directory")
check(manifest["wine"] == {
    "prefix": str(RUN / "prefix"), "arch": "win32", "created_new": True, "private": True,
}, "manifest does not describe a newly created private win32 prefix")
check(Path(manifest["game"]["root"]).resolve() == RUN / "game", "manifest game root escaped the run")
check(Path(manifest["output"]["run_dir"]).resolve() == run_root, "manifest run directory mismatch")
check(
    Path(manifest["output"]["evidence_dir"]).resolve() == RUN / "output",
    "manifest evidence directory mismatch",
)
check(manifest["game"]["diagnostic_bridge_overridden"] is False, "diagnostic bridge was overridden")
check(manifest["game"]["exe_sha256"] == ORIGINAL_SHA, "manifest game EXE is not the pinned original")
check(manifest["source"]["exe_sha256"] == ORIGINAL_SHA, "manifest source EXE is not pinned")
check(
    (RUN / "game/syw2plus_original.exe").stat().st_ino
    != (Path(manifest["source"]["root"]) / manifest["source"]["exe"]).stat().st_ino,
    "private EXE and source EXE share an inode",
)
owner = json.loads((RUN / "prefix/.syw2plus-runtime-owner.json").read_text(encoding="utf-8"))
check(Path(owner["run_dir"]).resolve() == run_root, "prefix owner does not name this run")
check(Path(owner["prefix"]).resolve() == RUN / "prefix", "prefix owner path mismatch")

# Candidate identity, command, module gate, and wrapper restoration.
check(evidence["variant"] == "candidate-dxwrapper-2x", "candidate variant is wrong")
check(evidence["run_id"] == f"{RUN.name}-candidate", "candidate run_id is not same-run bound")
check(evidence["status"] == "OBSERVED", "status is not OBSERVED")
check(evidence["classification"] == "REACHED_CHANGED", "classification is not REACHED_CHANGED")
check("error" not in evidence and "reason" not in evidence, "successful artifact carries a failure")
check(evidence["provenance"]["manifest_sha256"] == MANIFEST_SHA, "provenance manifest SHA mismatch")
check(
    evidence["provenance"]["harness_sha256"] == {"tools/runtime_env.py": HARNESS_SHA},
    "artifact harness SHA differs from the independently reviewed source",
)
check(evidence["provenance"]["observational_only"] is True, "artifact is not observational-only")
check(
    evidence["provenance"]["command"]
    == f"runtime_env.py g1-r1-candidate-load-origin --manifest local/runtime/{RUN.name}/manifest.json --screen 1600x1200x24 --timeout 90.0",
    "provenance command is not the fixed candidate command",
)
check(evidence["provenance"]["environment"]["WINEDLLOVERRIDES"] == "ddraw=n,b", "override is wrong")

config = evidence["dxwrapper_config"]
check(config["enabled"] is True and config["winedlloverrides"] == "ddraw=n,b", "candidate config disabled")
check(config["ini_original_sha256"] == INI_ORIGINAL_SHA, "candidate config old SHA mismatch")
check(config["ini_candidate_sha256"] == INI_CANDIDATE_SHA, "candidate config new SHA mismatch")
check(config["install"]["source_sha256"] == INI_ORIGINAL_SHA, "install source SHA mismatch")
check(config["install"]["patched_sha256"] == INI_CANDIDATE_SHA, "installed SHA mismatch")
check(config["uninstall"]["restored_sha256"] == INI_ORIGINAL_SHA, "uninstall did not restore ini")
check(config["uninstall"]["sidecars_removed"] is True, "uninstall did not remove sidecars")
check(not (RUN / "game/dxwrapper.ini.original-backup").exists(), "wrapper backup survived cleanup")
check(not (RUN / "game/dxwrapper.ini.patch.json").exists(), "wrapper patch manifest survived cleanup")

gate = evidence["module_gate"]
check(gate["status"] == "PASS", "module gate did not pass")
check(Path(gate["private_ddraw"]).resolve() == RUN / "game/ddraw.dll", "loaded ddraw is not private")
check(gate["private_ddraw_sha256"] == DDRAW_SHA, "loaded private ddraw SHA mismatch")
check(gate["syw2x_loaded"] is False, "QHD syw2x.dll was loaded")
mapped = {Path(item["path"]).name: item["sha256"] for item in gate["modules"]}
check(mapped == {"syw2plus_original.exe": ORIGINAL_SHA, "ddraw.dll": DDRAW_SHA}, "module set mismatch")
for item in config["wrapper_logs"]:
    path = Path(item["path"])
    check(within(path, RUN / "output/wrapper_logs"), f"wrapper log escaped output: {path}")
    check(path.is_file(), f"wrapper log is absent: {path}")
    if path.is_file():
        check(sha256(path) == item["sha256"], f"wrapper log SHA mismatch: {path.name}")
        check(path.stat().st_size == item["bytes"], f"wrapper log size mismatch: {path.name}")

# Fixed geometry, one unscaled click, and read-only fixture.
check(evidence["screen"] == "1600x1200x24", "screen differs from the fixed envelope")
check(evidence["timeout_seconds"] == 90.0, "timeout differs from the fixed envelope")
check(evidence["fixture"] == {
    "kind": "new private copy; default two-player random game",
    "synthetic": False, "memory_writes": False, "resource_grant": False,
}, "fixture declaration differs from the envelope")
window = evidence["window"]
check(window["physical_size"] == [1600, 1200], "physical output is not 1600x1200")
check(window["logical_size"] == [800, 600], "logical composition is not 800x600")
check(window["scale"] == [2.0, 2.0], "candidate scale is not 2x")
check([window["root"]["width"], window["root"]["height"]] == [1600, 1200], "root geometry failed")
check(
    [window["content_child"]["width"], window["content_child"]["height"]] == [1600, 1200],
    "content child geometry failed",
)
input_data = evidence["input"]
check(input_data["client"] == [296, 505], "logical click source differs from the accepted coordinate")
check(input_data["scale_applied"] == [1.0, 1.0], "click was scaled")
check(input_data["count"] == 1, "input count is not exactly one")
check(input_data["focus_exit"] == input_data["inject_exit"] == 0, "focus or injection failed")
crop = input_data["content_crop"]
expected_root = [crop["x"] + 296, crop["y"] + 505]
check(input_data["root"] == input_data["x11"] == expected_root, "root click transform is wrong")

# Independent state-series and origin derivation from same-run raw inputs.
series = evidence["pending_state"]
check(len(series) == len(evidence["ps_word"]) == len(evidence["ps_dword"]) == 12, "sample count is not 12")
check(all(a["ps_word"] == a["ps_dword"] for a in series), "WORD/DWORD sample mismatch")
times = [item["elapsed_seconds"] for item in series]
check(times == sorted(times), "sample times are not monotone")
for sample, word, dword in zip(series, evidence["ps_word"], evidence["ps_dword"], strict=True):
    check(sample["elapsed_seconds"] == word["elapsed_seconds"] == dword["elapsed_seconds"], "series timestamps diverge")
    check(sample["ps_word"] == word["value"] and sample["ps_dword"] == dword["value"], "series values diverge")
pending = [item["pending_state"] for item in series]
check(pending == sorted(pending) and set(pending) == {0, 34}, "pending state is mixed or unexpected")
check(evidence["wait_ps_states"] == [9, 35], "wait state declaration is wrong")
check(evidence["pre"] == {
    "state": {"ps": 9, "ps_word": 9, "ps_dword": 9, "pending_state": 0},
    "origin": {"x": 0, "y": 0, "tag": 0},
}, "pre state/origin differs from P1")
check(evidence["post"]["state"] == {
    "ps": 35, "ps_word": 35, "ps_dword": 35, "pending_state": 34,
}, "post state did not reach PS35/pending34")

sprite = RUN / "game/yfnt/saveloadtitle.spr"
sprite_tag, width, height, frames = struct.unpack_from("<4I", sprite.read_bytes(), 0)
predicted_origin = [(800 - width) // 2, (600 - height) // 2, 8]
check((sprite_tag, frames) == (9, 1), "same-run sprite header shape changed")
check(list(evidence["post"]["origin"].values()) == predicted_origin, "post origin does not match same-run sprite")
check(evidence["origin_tag"] == {"pre": 0, "post": 8}, "origin tag did not change 0->8")

# The stage timeline proves the fixed total and per-stage envelopes without rerunning.
timeline = evidence["stage_timeline"]
stage_names = [
    "prepare_and_install", "launch_and_ps9", "geometry_and_module_gate",
    "click_and_ps35", "cleanup",
]
check(list(timeline) == stage_names, "stage timeline is absent, reordered, or incomplete")
for left, right in zip(stage_names, stage_names[1:], strict=True):
    check(timeline[left]["ended_elapsed"] <= timeline[right]["started_elapsed"], f"stages overlap: {left}/{right}")
check(timeline["launch_and_ps9"]["ended_elapsed"] <= 40, "prepare/PS9 exceeded 40 seconds")
check(timeline["click_and_ps35"]["duration_seconds"] <= 20, "click/PS35 exceeded 20 seconds")
check(timeline["geometry_and_module_gate"]["duration_seconds"] <= 15, "observation gate exceeded 15 seconds")
check(timeline["cleanup"]["duration_seconds"] <= 15, "cleanup exceeded 15 seconds")
check(evidence["elapsed_seconds"] <= 90, "total runtime exceeded 90 seconds")

cleanup = evidence["cleanup"]
check(cleanup["owned_launchers_stopped"] is True, "owned launchers survived")
check(cleanup["xvfb_stopped"] is True, "private Xvfb survived")
check(cleanup["global_kill_used"] is False, "cleanup used a global kill")
check(cleanup["prefix_processes_after"] == [], "private prefix processes survived")
check(cleanup["error"] is None, "cleanup recorded an error")
check(cleanup["dxwrapper_config_restored"] is True, "wrapper restore flag is false")
check(cleanup["ok"] is True, "cleanup did not pass")

report = {
    "scope": "read-only independent review of the preserved lap345 candidate R1 artifact",
    "run": str(RUN.relative_to(REPO)),
    "sha256": observed_sha,
    "candidate_artifact_count": len(candidate_artifacts),
    "candidate_lock_count": len(candidate_locks),
    "original_artifact_count": len(original_artifacts),
    "sample_count": len(series),
    "observed_ps_values": sorted({item["ps_word"] for item in series}),
    "pending_transition": [pending[0], pending[-1]],
    "predicted_origin_from_same_run_sprite": predicted_origin,
    "stage_timeline": timeline,
    "lap345_record_note": {
        "kind": "PATH_TYPO",
        "recorded": "output/g1-r1-candidate-load-origin.log",
        "actual": "output/r1_load_origin_candidate.log",
        "recorded_sha_matches_actual": observed_sha["log"] == LOG_SHA,
        "affects_measurement": False,
    },
    "failures": failures,
}
print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
raise SystemExit(1 if failures else 0)
