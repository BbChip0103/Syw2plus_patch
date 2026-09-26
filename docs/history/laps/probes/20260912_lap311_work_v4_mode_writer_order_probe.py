"""lap311 work — strengthen the lap310 R2 static evidence.

This is a read-only probe of the SHA-pinned original executable.  It uses the
objdump instruction graph already established for this function, but derives
the success-side claim with reverse post-dominators rather than the earlier
forward-dominator calculation.  It also compares the complete screen-global
writer set before and after the gate, instead of checking only the two runtime
writer addresses.  No game, Wine, Xvfb, runtime, Stage B, PNG, or click path
is run here; JSON is emitted on stdout only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

MAP_ENTRY = 0x431AB0
MAP_END = 0x4324D6
MAP_GATE_BRANCH = 0x431AF2
MAP_FAILURE_SEED = 0x431AF4
MAP_FAILURE_RET = 0x431AFD
MAP_SUCCESS_JOIN = 0x431AFE
MAP_SUCCESS_RET = 0x4324D5
SCREEN_GLOBALS = (0xE5BF1C, 0xE5BF20)
EXPECTED_SCREEN_WRITERS = {0x431B79, 0x431B7F, 0x4324B8, 0x4324C2}
EXPECTED_RUNTIME_WRITERS = {0x431B79, 0x431B7F}
EXPECTED_RESET_WRITERS = {0x4324B8, 0x4324C2}

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\s+0x([0-9a-f]+)$")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
SCREEN_WRITER_RE = re.compile(r"^mov\s+DWORD PTR ds:0x(e5bf1c|e5bf20),")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_text() -> list[tuple[int, str]]:
    listing = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [(int(address, 16), instruction) for address, _bytes, instruction in INSN_RE.findall(listing)]


def build_cfg(window: list[tuple[int, str]]) -> tuple[dict[int, set[int]], list[str]]:
    known = {address for address, _instruction in window}
    graph: dict[int, set[int]] = {}
    unresolved: list[str] = []
    for index, (address, instruction) in enumerate(window):
        if RET_RE.match(instruction):
            graph[address] = set()
            continue
        fallthrough = window[index + 1][0] if index + 1 < len(window) else None
        match = BRANCH_RE.match(instruction)
        if match:
            mnemonic, target_text = match.groups()
            target = int(target_text, 16)
            edges = {target}
            if mnemonic != "jmp" and fallthrough is not None:
                edges.add(fallthrough)
            if target not in known:
                unresolved.append(f"0x{address:x}: target 0x{target:x} outside window")
            graph[address] = {edge for edge in edges if edge in known}
            continue
        graph[address] = {fallthrough} if fallthrough in known else set()
    return graph, unresolved


def reachable(graph: dict[int, set[int]], start: int) -> set[int]:
    seen: set[int] = set()
    pending = [start]
    while pending:
        address = pending.pop()
        if address in seen or address not in graph:
            continue
        seen.add(address)
        pending.extend(graph[address] - seen)
    return seen


def reverse_graph(graph: dict[int, set[int]]) -> dict[int, set[int]]:
    reversed_graph = {node: set() for node in graph}
    for source, targets in graph.items():
        for target in targets:
            reversed_graph.setdefault(target, set()).add(source)
    return reversed_graph


def dominators(graph: dict[int, set[int]], start: int) -> dict[int, set[int]]:
    """Dominators on a graph; on the reversed graph these are post-dominators."""
    nodes = reachable(graph, start)
    predecessors = {node: set() for node in nodes}
    for source in nodes:
        for target in graph[source] & nodes:
            predecessors[target].add(source)
    result = {node: set(nodes) for node in nodes}
    result[start] = {start}
    changed = True
    while changed:
        changed = False
        for node in sorted(nodes - {start}):
            incoming = predecessors[node]
            candidate = {node} if not incoming else {node} | set.intersection(*(result[p] for p in incoming))
            if candidate != result[node]:
                result[node] = candidate
                changed = True
    return result


def screen_writers(window: list[tuple[int, str]]) -> set[int]:
    return {address for address, instruction in window if SCREEN_WRITER_RE.match(instruction)}


def fmt(values: set[int] | list[int] | tuple[int, ...]) -> list[str]:
    return [f"0x{value:x}" for value in sorted(values)]


def main() -> int:  # noqa: C901 - one bounded static audit report
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 311,
        "role": "work (static research/probe); no game code edited, no execution",
        "execution": False,
        "scope": "R2 stronger failure-arm writer comparison and reverse post-dominator proof",
        "report_contract": "JSON is emitted on stdout; redirect stdout without hand transcription",
    }
    if not EXE.is_file():
        report["failures"] = [f"missing original executable: {EXE}"]
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    exe_sha = sha256_file(EXE)
    report["sha256"] = {"original_exe": exe_sha}
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")

    instructions = parse_text()
    map_window = [(address, instruction) for address, instruction in instructions if MAP_ENTRY <= address < MAP_END]
    graph, unresolved = build_cfg(map_window)
    if not map_window:
        failures.append("objdump produced no instructions in map window")

    all_writers = screen_writers(map_window)
    from_entry = reachable(graph, MAP_ENTRY)
    before_gate = all_writers & {address for address in from_entry if address < MAP_GATE_BRANCH}
    failure_path = reachable(graph, MAP_FAILURE_SEED)
    success_path = reachable(graph, MAP_SUCCESS_JOIN)
    failure_writers = all_writers & failure_path
    success_writers = all_writers & success_path
    failure_preserves_screen_writer_set = failure_writers == before_gate
    report["r2_failure_arm_writer_set_comparison"] = {
        "gate": f"0x{MAP_GATE_BRANCH:x}",
        "failure_seed": f"0x{MAP_FAILURE_SEED:x}",
        "failure_seed_is_fall_through": MAP_FAILURE_SEED == MAP_GATE_BRANCH + 2,
        "pre_gate_screen_writers": fmt(before_gate),
        "failure_arm_screen_writers": fmt(failure_writers),
        "success_arm_screen_writers": fmt(success_writers),
        "all_screen_writers_in_map_window": fmt(all_writers),
        "failure_preserves_pre_gate_screen_writer_set": failure_preserves_screen_writer_set,
        "failure_has_no_new_screen_global_writer": not (failure_writers - before_gate),
        "expected": {
            "all_screen_writers": fmt(EXPECTED_SCREEN_WRITERS),
            "failure_arm": [],
            "success_arm": fmt(EXPECTED_SCREEN_WRITERS),
        },
        "verdict": "PASS"
        if all_writers == EXPECTED_SCREEN_WRITERS
        and failure_preserves_screen_writer_set
        and success_writers == EXPECTED_SCREEN_WRITERS
        else "FAIL",
    }
    if all_writers != EXPECTED_SCREEN_WRITERS:
        failures.append(f"screen writer set changed: {fmt(all_writers)}")
    if not failure_preserves_screen_writer_set:
        failures.append(f"failure arm adds screen writers: {fmt(failure_writers - before_gate)}")
    if success_writers != EXPECTED_SCREEN_WRITERS:
        failures.append(f"success arm screen writer set changed: {fmt(success_writers)}")
    if MAP_SUCCESS_RET in failure_path:
        failures.append("failure arm reaches the success return")

    # Reverse reachability from the successful return limits the proof to every
    # CFG path that can actually reach that return.  Dominators on this reversed
    # graph are post-dominators in the original graph, so the reset writers in
    # postdom(entry) are mandatory on every entry-to-success-ret path.
    reversed_cfg = reverse_graph(graph)
    success_reaching = reachable(reversed_cfg, MAP_SUCCESS_RET)
    success_postdom = dominators(reversed_cfg, MAP_SUCCESS_RET)
    reset_postdominates_entry = EXPECTED_RESET_WRITERS <= success_postdom.get(MAP_ENTRY, set())
    reset_postdominates_join = EXPECTED_RESET_WRITERS <= success_postdom.get(MAP_SUCCESS_JOIN, set())
    report["r2_success_reverse_postdominator"] = {
        "success_return": f"0x{MAP_SUCCESS_RET:x}",
        "success_reaching_node_count": len(success_reaching),
        "entry_reaches_success_return": MAP_ENTRY in success_reaching,
        "failure_return_reaches_success_return": MAP_FAILURE_RET in success_reaching,
        "reset_writers": fmt(EXPECTED_RESET_WRITERS),
        "entry_postdominators_contain_reset_writers": fmt(EXPECTED_RESET_WRITERS & success_postdom.get(MAP_ENTRY, set())),
        "join_postdominators_contain_reset_writers": fmt(EXPECTED_RESET_WRITERS & success_postdom.get(MAP_SUCCESS_JOIN, set())),
        "reset_writers_postdominate_entry": reset_postdominates_entry,
        "reset_writers_postdominate_success_join": reset_postdominates_join,
        "verdict": "PASS" if reset_postdominates_entry and reset_postdominates_join else "FAIL",
        "method_note": (
            "reverse CFG traversal starts at the success ret; dominators there are "
            "post-dominators of the original success paths, independent of the prior forward-dominator result"
        ),
    }
    if unresolved:
        failures.append(f"map CFG has branch targets outside the inspected window: {unresolved}")
    if MAP_ENTRY not in success_reaching:
        failures.append("map entry cannot reach the success return in the inspected CFG")
    if not reset_postdominates_entry or not reset_postdominates_join:
        failures.append("reset writers do not post-dominate the success paths")

    report["map_cfg"] = {
        "instruction_count": len(map_window),
        "unresolved_branches": unresolved,
        "entry_reachable_instruction_count": len(from_entry),
        "success_reachable_instruction_count": len(success_path),
        "success_return": f"0x{MAP_SUCCESS_RET:x}",
    }
    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "screen writer comparison covers direct instructions in this map function; indirect/computed writers remain UNKNOWN",
        "the CFG treats calls as fall-through and does not prove cross-function event/thread order",
        "this probe produces no G1/G2/G3/G4 product evidence",
    ]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
