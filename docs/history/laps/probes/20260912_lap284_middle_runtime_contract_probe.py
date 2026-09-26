"""lap284 middle probe — evidence for the six required inputs of the lap283 Astra contract.

Read-only.  Answers, with machine evidence only, the questions
`docs/work/active/G1_RUNTIME_G3_ASTRA_DECISION_LAP283.md` asks the confirming tier
to ACCEPT/REJECT: fixture choice, harness connection, measurement formula, tick,
execution envelope, failure preservation.

No game, no Wine, no Xvfb, no Stage B, no writes to the original tree, no save parsing
(only the serializer call order in the original binary and file sizes are read).

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap284_middle_runtime_contract_probe.py
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
RUNTIME_ENV = REPO / "tools" / "runtime_env.py"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

SAVE_ENTRY, SAVE_END = 0x440C20, 0x440FF0
FWRITE = "0x4da39f"
LAYER_LO, LAYER_HI = 0x42A900, 0x42BD00
UNIT_STRIDE = 0x758
BULK_PTR, BULK_LEN = 0x00892410, 0xE397C
MAP_BLOCK_PTR, MAP_BLOCK_LEN = 0x00B3DDA8, 0xB0
PLAYER_BASE, PLAYER_STRIDE = 0x00956770, 0x3ABC
TICK_ADDRESS = 0x008924B8

# The two fixtures the lap283 contract allows, plus the two this project's own
# 2026-09-10 runs produced (docs/history/20260910_EXPERIMENTS.md).
FIXTURES = {
    "save000.dat": "1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da",
    "save006.dat": "616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064",
}
FIXTURE_DIR = REPO.parent / "Syw2plus" / "save"
LOCAL_FIXTURE_DIR = REPO / "local" / "fixtures" / "20260910"

LINE_RE = re.compile(r"\s*([0-9a-f]+):\t[0-9a-f ]+\t(\S+)\s*(.*)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disasm(start: int, stop: int) -> str:
    return subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text",
         f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(EXE)],
        check=True, capture_output=True, text=True,
    ).stdout


def payload_order(text: str) -> list[dict[str, object]]:
    """Ordered save-side payload sequence: literal fwrite blocks and layer calls."""
    pushes: list[int | None] = []
    out: list[dict[str, object]] = []
    for line in text.splitlines():
        m = LINE_RE.match(line)
        if not m:
            continue
        site, op, args = int(m.group(1), 16), m.group(2), m.group(3).strip()
        if op == "push":
            pushes.append(int(args, 16) if re.fullmatch(r"0x[0-9a-f]+", args) else None)
            continue
        if op == "call":
            target = args.split()[0]
            if FWRITE in args and len(pushes) >= 4:
                _file, count, size, ptr = pushes[-4:]
                out.append({"site": f"{site:#010x}", "kind": "literal" if ptr is not None else "stack",
                            "ptr": None if ptr is None else f"{ptr:#010x}",
                            "bytes": None if (size is None or count is None) else size * count})
            elif re.fullmatch(r"0x[0-9a-f]+", target) and LAYER_LO <= int(target, 16) < LAYER_HI:
                out.append({"site": f"{site:#010x}", "kind": "layer", "ptr": target, "bytes": None})
            pushes = []
    return out


def fixture_facts() -> dict[str, object]:
    """Sizes/hashes of the candidate saves in both the fixture dir and the copy source."""
    source_dir = _default_source() / "save"
    files: dict[str, object] = {}
    for directory, label in ((FIXTURE_DIR, "fixture_dir"), (source_dir, "prepare_copy_source"),
                             (LOCAL_FIXTURE_DIR, "local_fixtures")):
        entry: dict[str, object] = {"path": str(directory), "exists": directory.is_dir()}
        if directory.is_dir():
            entry["files"] = {p.name: {"size": p.stat().st_size, "sha256": sha256(p)}
                              for p in sorted(directory.glob("save*.dat"))}
        files[label] = entry
    return files


def _default_source() -> Path:
    src = RUNTIME_ENV.read_text(encoding="utf-8")
    m = re.search(r'DEFAULT_SOURCE = \(REPO_ROOT\.parent / "([^"]+)" / "([^"]+)"\)', src)
    if not m:
        raise SystemExit("DEFAULT_SOURCE shape changed; probe must be updated")
    return REPO.parent / m.group(1) / m.group(2)


def observed_ps3_ticks() -> list[dict[str, object]]:
    """scene.tick recorded by every past g1 run that actually reached PS3."""
    out = []
    for path in sorted((REPO / "local" / "runtime").glob("*/output/g1_baseline.json")):
        try:
            data = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        scene = data.get("scene")
        if isinstance(scene, dict) and isinstance(scene.get("tick"), int):
            out.append({"run": path.parts[-3], "tick": scene["tick"],
                        "elapsed_seconds": data.get("elapsed_seconds"),
                        "fixture": (data.get("fixture") or {}).get("kind")})
    return out


def main() -> int:
    failures: list[str] = []
    actual = sha256(EXE)
    if actual != EXPECTED_EXE_SHA:
        print(f"FAIL original exe sha mismatch: {actual}", file=sys.stderr)
        return 2

    # (1) Save-file layout order.  The question that decides whether a save file can be
    #     read offline at all: is the bulk block (players/selection/tick) at a file offset
    #     derivable from fixed-size blocks, or does variable map payload precede it?
    order = payload_order(disasm(SAVE_ENTRY, SAVE_END))
    layer_sites = [int(str(i["site"]), 16) for i in order if i["kind"] == "layer"]
    bulk = [i for i in order if i["ptr"] == f"{BULK_PTR:#010x}"]
    mapblk = [i for i in order if i["ptr"] == f"{MAP_BLOCK_PTR:#010x}"]
    if len(layer_sites) != 28:
        failures.append(f"expected 28 map-layer calls in the save entry, got {len(layer_sites)}")
    if len(bulk) != 1 or bulk[0]["bytes"] != BULK_LEN:
        failures.append(f"bulk block not found exactly once with {BULK_LEN:#x} bytes: {bulk}")
    if len(mapblk) != 1 or mapblk[0]["bytes"] != MAP_BLOCK_LEN:
        failures.append(f"map block not found exactly once with {MAP_BLOCK_LEN:#x} bytes: {mapblk}")
    bulk_site = int(str(bulk[0]["site"]), 16) if bulk else 0
    map_site = int(str(mapblk[0]["site"]), 16) if mapblk else 0
    bulk_after_layers = bool(layer_sites) and bulk_site > max(layer_sites)
    map_before_layers = bool(layer_sites) and map_site < min(layer_sites)
    fixed_prefix = sum(int(i["bytes"] or 0) for i in order
                       if int(str(i["site"]), 16) < (min(layer_sites) if layer_sites else 0))
    if not bulk_after_layers:
        failures.append("bulk block no longer follows the variable map layers")
    if not map_before_layers:
        failures.append("map bounds block no longer precedes the variable map layers")

    # (2) Fixture facts.  Same-map pairs must differ by whole unit records.
    fixtures = fixture_facts()
    source_files = fixtures["prepare_copy_source"]  # type: ignore[index]
    if not source_files.get("exists"):  # type: ignore[union-attr]
        failures.append("prepare() copy source has no save/ directory")
    for name, expected in FIXTURES.items():
        got = (fixtures["fixture_dir"].get("files") or {}).get(name)  # type: ignore[union-attr]
        src = (source_files.get("files") or {}).get(name)  # type: ignore[union-attr]
        if not got or got["sha256"] != expected:
            failures.append(f"{name} sha differs from the lap279 record: {got}")
        if not src or src["sha256"] != expected:
            failures.append(f"{name} missing or different inside the prepare copy source: {src}")
    sizes = {name: info["size"]
             for label in ("fixture_dir", "local_fixtures")
             for name, info in (fixtures[label].get("files") or {}).items()}  # type: ignore[union-attr]
    deltas = {}
    for a, b in (("save000.dat", "save006.dat"), ("save011.dat", "save012.dat")):
        if a in sizes and b in sizes:
            d = sizes[b] - sizes[a]
            deltas[f"{b}-{a}"] = {"bytes": d, "unit_records": d / UNIT_STRIDE,
                                  "whole_records": d % UNIT_STRIDE == 0}
            if d % UNIT_STRIDE != 0:
                failures.append(f"{b}-{a} is not a whole number of {UNIT_STRIDE:#x} records")

    # (3) Harness connection facts.
    env_src = RUNTIME_ENV.read_text(encoding="utf-8")
    harness = {
        "save_load_references": len(re.findall(r"\bsave\d|save\\\\|\.dat\b|load_game", env_src)),
        "ps35_references": len(re.findall(r"\b35\b(?=[^\n]*ps)|ps.{0,12}==\s*35", env_src)),
        "ps_states_waited": sorted({int(m) for m in re.findall(r'get\("ps"\)\s*==\s*(\d+)', env_src)}),
        "g1_baseline_timeout_cap": 90 if 'timeout > 90' in env_src else None,
        "fixture_kind": (re.search(r'"kind": "([^"]*random game)"', env_src) or [None, None])[1],
        "setup_points": sorted(re.findall(r'"(\w+)": \((\d+), (\d+)\)', env_src)[:4]),
        "start_endpoint_rule": "before_ps == 5" in env_src and 'after_state.get("ps") == 3' in env_src,
    }
    if harness["save_load_references"] != 0:
        failures.append("runtime_env.py unexpectedly references save files already")
    if harness["g1_baseline_timeout_cap"] != 90:
        failures.append("g1_baseline no longer caps the timeout at 90 seconds")

    # (4) tick: what has actually been observed, and where tick lives in the save.
    ticks = observed_ps3_ticks()
    tick_in_bulk = BULK_PTR <= TICK_ADDRESS < BULK_PTR + BULK_LEN

    # (5) G3 arithmetic, recomputed from this probe's own constants.
    bulk_end = BULK_PTR + BULK_LEN
    need16 = PLAYER_BASE + 16 * PLAYER_STRIDE
    overflow = need16 - bulk_end
    if overflow != 0x1B5A4:
        failures.append(f"G3 overflow arithmetic unexpected: {overflow:#x}")

    report = {
        "exe_sha256": actual,
        "save_layout": {
            "payload_calls": len(order),
            "layer_calls": len(layer_sites),
            "map_block_site": f"{map_site:#010x}",
            "bulk_site": f"{bulk_site:#010x}",
            "map_bounds_precede_layers": map_before_layers,
            "bulk_follows_layers": bulk_after_layers,
            "fixed_bytes_before_first_layer": fixed_prefix,
            "order": order,
        },
        "fixtures": fixtures,
        "fixture_size_deltas": deltas,
        "harness": harness,
        "tick": {"address": f"{TICK_ADDRESS:#010x}", "inside_bulk_block": tick_in_bulk,
                 "observed_ps3_ticks": ticks,
                 "distinct_values": sorted({int(t["tick"]) for t in ticks})},
        "g3": {"bulk_end": f"{bulk_end:#010x}", "need_16_players": f"{need16:#010x}",
               "overflow_bytes": f"{overflow:#x}"},
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
