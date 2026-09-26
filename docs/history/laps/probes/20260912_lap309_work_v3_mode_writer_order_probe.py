"""lap309 work V3 — repair the lap308 R2, R3, and R5 probe gates.

This is a read-only static probe of the SHA-pinned original executable.  The
report is emitted only on stdout; the caller must redirect stdout to the
lap-specific report file so that the report is exactly the generator output.
No game, Wine, Xvfb, runtime harness, Stage B, PNG, or click execution is
performed here.
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
MAP_FAILURE_FALLTHROUGH = 0x431AF4
MAP_FAILURE_RET = 0x431AFD
MAP_SUCCESS_JOIN = 0x431AFE
MAP_SUCCESS_RET = 0x4324D5
MAP_CALLERS = (0x48F538,)
RUNTIME_WRITERS = (0x431B79, 0x431B7F)
RESET_WRITERS = (0x4324B8, 0x4324C2)
DIALOG_ENTRY = 0x4D60B0
DIALOG_CALLERS = (0x4D69E5, 0x4D6A05)

CALLEE = 0x465250
CALLEE_END = 0x4652AF
CALLEE_LOG_CALL = 0x465268
CALLEE_VCALL = 0x465284
CALLEE_IMPORT_CALL = 0x46529D
CALLEE_JOIN = 0x465287
CALLEE_RET = 0x4652AE
CALLEE_ARG1_READ = 0x46526D

# The three calls in the inspected callee have different cleanup contracts:
# cdecl logging (caller cleanup), a virtual method that pops its one argument,
# and USER32's four-argument stdcall import (callee cleanup).
CALL_CLEANUP_BYTES = {
    CALLEE_LOG_CALL: 0,
    CALLEE_VCALL: 4,
    CALLEE_IMPORT_CALL: 16,
}
CALL_CONVENTIONS = {
    CALLEE_LOG_CALL: "cdecl",
    CALLEE_VCALL: "indirect callee-clean (4)",
    CALLEE_IMPORT_CALL: "stdcall callee-clean (16)",
}

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\s+0x([0-9a-f]+)$")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
ESP_ADJUST_RE = re.compile(r"^(sub|add)\s+esp,0x([0-9a-f]+)$")
ESP_ACCESS_RE = re.compile(r"\[esp(?:\+0x([0-9a-f]+))?\]")


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
            edges = {int(target_text, 16)}
            if mnemonic != "jmp" and fallthrough is not None:
                edges.add(fallthrough)
            graph[address] = {edge for edge in edges if edge in known}
            continue
        if instruction.startswith(("j", "loop")):
            unresolved.append(f"0x{address:x}: {instruction}")
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


def dominators(graph: dict[int, set[int]], start: int) -> dict[int, set[int]]:
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


def stack_adjustment(
    instruction: str, address: int, call_cleanup_bytes: dict[int, int] | None = None
) -> int:
    """Return the entry-relative depth delta for one instruction.

    Calls are modeled by their calling convention at the callsite.  Omitting
    the mapping intentionally gives the old all-calls-cdecl-neutral model for
    the R3 regression comparison; the corrected model supplies every callsite
    in the inspected callee explicitly.
    """
    match = ESP_ADJUST_RE.match(instruction)
    if match:
        amount = int(match.group(2), 16)
        return amount if match.group(1) == "sub" else -amount
    if instruction.startswith("push"):
        return 4
    if instruction.startswith("pop"):
        return -4
    if instruction.startswith("call"):
        if call_cleanup_bytes is None:
            return 0
        if address not in call_cleanup_bytes:
            raise ValueError(f"missing calling-convention cleanup for 0x{address:x}: {instruction}")
        return -call_cleanup_bytes[address]
    return 0


def walk_depths(
    window: list[tuple[int, str]], start: int, call_cleanup_bytes: dict[int, int] | None = None
) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    graph, _unresolved = build_cfg(window)
    body = dict(window)
    depths: dict[int, set[int]] = {start: {0}}
    offsets: dict[int, set[int]] = {}
    pending = [start]
    while pending:
        address = pending.pop()
        current = depths[address]
        instruction = body[address]
        for match in ESP_ACCESS_RE.finditer(instruction):
            raw = int(match.group(1), 16) if match.group(1) else 0
            offsets.setdefault(address, set()).update(raw - depth for depth in current)
        outgoing = {
            depth + stack_adjustment(instruction, address, call_cleanup_bytes)
            for depth in current
        }
        for target in graph.get(address, set()):
            merged = depths.setdefault(target, set()) | outgoing
            if merged != depths[target]:
                depths[target] = merged
                pending.append(target)
    return depths, offsets


def fmt(values: set[int] | list[int] | tuple[int, ...]) -> list[str]:
    return [f"0x{value:x}" for value in sorted(values)]


def main() -> int:  # noqa: C901 - one bounded static audit report
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 309,
        "role": "work (static research/probe); no game code edited, no execution",
        "execution": False,
        "report_contract": "JSON is emitted on stdout; redirect stdout without hand transcription",
        "scope": "V3 repair of lap308 R2 failure seed, R3 call cleanup, and R5 caller assertion",
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
    body = dict(instructions)
    if not instructions:
        failures.append("objdump produced no .text instructions")

    anchors = {
        0x431AE1: "call   0x4da96e",
        0x431AEB: "cmp    eax,ebx",
        MAP_GATE_BRANCH: "jne    0x431afe",
        0x431AF7: "xor    eax,eax",
        MAP_FAILURE_RET: "ret",
        0x431B79: "mov    DWORD PTR ds:0xe5bf1c,ebp",
        0x431B7F: "mov    DWORD PTR ds:0xe5bf20,edi",
        0x4324B8: "mov    DWORD PTR ds:0xe5bf1c,0x280",
        0x4324C2: "mov    DWORD PTR ds:0xe5bf20,0x1e0",
        0x4324CC: "mov    eax,0x1",
        MAP_SUCCESS_RET: "ret",
        0x4D6312: "mov    eax,ds:0xe5bf1c",
        0x4D631C: "mov    eax,ds:0xe5bf20",
        0x4D632A: "mov    WORD PTR ds:0x1088b5c,cx",
        0x4D6348: "mov    WORD PTR ds:0x1088b5e,di",
    }
    anchor_matches = {f"0x{a:x}": body.get(a, "") == expected for a, expected in anchors.items()}
    failures.extend(
        f"anchor 0x{a:x}: expected {expected!r}, found {body.get(a)!r}"
        for a, expected in anchors.items()
        if body.get(a) != expected
    )

    map_callers = [a for a, instruction in instructions if instruction == f"call   0x{MAP_ENTRY:x}"]
    dialog_callers = [a for a, instruction in instructions if instruction == f"call   0x{DIALOG_ENTRY:x}"]
    map_window = [(a, i) for a, i in instructions if MAP_ENTRY <= a < MAP_END]
    map_graph, map_unresolved = build_cfg(map_window)
    map_rets = [a for a, i in map_window if RET_RE.match(i)]
    failure_path = reachable(map_graph, MAP_FAILURE_FALLTHROUGH)
    success_path = reachable(map_graph, MAP_SUCCESS_JOIN)
    success_dom = dominators(map_graph, MAP_SUCCESS_JOIN)
    writers_on_failure = sorted(set(RUNTIME_WRITERS) & failure_path)
    runtime_on_success = {f"0x{w:x}": w in success_path for w in RUNTIME_WRITERS}
    reset_dominates = all(w in success_dom.get(MAP_SUCCESS_RET, set()) for w in RESET_WRITERS)

    # R2: seed from the jne fall-through, not from the ret instruction.
    report["r2_failure_path_gate"] = {
        "seed": f"0x{MAP_FAILURE_FALLTHROUGH:x}",
        "seed_is_fallthrough_of": f"0x{MAP_GATE_BRANCH:x}",
        "failure_path": fmt(failure_path),
        "runtime_writers_on_failure_path": fmt(writers_on_failure),
        "runtime_writers_reachable_on_success": runtime_on_success,
        "reset_writers_dominate_success_ret": reset_dominates,
        "verdict": "PASS" if not writers_on_failure else "FAIL",
    }
    if map_callers != list(MAP_CALLERS):
        failures.append(f"R5 map direct callers changed: {fmt(map_callers)}")
    if dialog_callers != list(DIALOG_CALLERS):
        failures.append(f"dialog direct callers changed: {fmt(dialog_callers)}")
    if map_rets != [MAP_FAILURE_RET, MAP_SUCCESS_RET]:
        failures.append(f"map return sites changed: {fmt(map_rets)}")
    if not all(runtime_on_success.values()) or writers_on_failure:
        failures.append("R2 runtime writer reachability does not match the failure/success paths")
    if not reset_dominates:
        failures.append("R2 reset writers do not dominate the success return")
    if map_unresolved:
        failures.append(f"map CFG has unresolved branch forms: {map_unresolved}")

    # R3: compare the old neutral-call model with the corrected per-call model.
    callee_window = [(a, i) for a, i in instructions if CALLEE <= a < CALLEE_END]
    old_depths, old_offsets = walk_depths(callee_window, CALLEE)
    corrected_depths, corrected_offsets = walk_depths(callee_window, CALLEE, CALL_CLEANUP_BYTES)
    old_ret = old_depths.get(CALLEE_RET, set())
    corrected_ret = corrected_depths.get(CALLEE_RET, set())
    corrected_join = corrected_depths.get(CALLEE_JOIN, set())
    single_ret_invariant = len(corrected_ret) == 1
    corrected_offsets_report = {
        f"0x{CALLEE_ARG1_READ:x}": sorted(corrected_offsets.get(CALLEE_ARG1_READ, set())),
        f"0x{CALLEE_JOIN:x}": sorted(corrected_offsets.get(CALLEE_JOIN, set())),
    }
    report["r3_stack_call_convention_regression"] = {
        "callee": f"0x{CALLEE:x}..0x{CALLEE_END:x}",
        "call_conventions": {
            f"0x{address:x}": {
                "convention": CALL_CONVENTIONS[address],
                "cleanup_bytes": CALL_CLEANUP_BYTES[address],
            }
            for address in sorted(CALL_CLEANUP_BYTES)
        },
        "old_all_calls_neutral_depths_at_join": fmt(old_depths.get(CALLEE_JOIN, set())),
        "old_all_calls_neutral_depths_at_single_ret": fmt(old_ret),
        "corrected_depths_at_join": fmt(corrected_join),
        "corrected_depths_at_single_ret": fmt(corrected_ret),
        "single_ret_depth_is_singleton": single_ret_invariant,
        "corrected_entry_relative_offsets": corrected_offsets_report,
        "expected": {
            "0x465287_join_depths": ["0x100"],
            "0x4652ae_ret_depths": ["0x0"],
            "0x46526d_entry_offset": [4],
            "0x465287_entry_offset": [8],
        },
        "verdict": "PASS" if single_ret_invariant else "FAIL",
    }
    if old_ret == corrected_ret or len(old_ret) <= 1:
        failures.append("R3 old neutral-call model no longer demonstrates the multi-valued ret regression")
    if corrected_join != {0x100} or corrected_ret != {0}:
        failures.append(f"R3 corrected depths changed: join={fmt(corrected_join)}, ret={fmt(corrected_ret)}")
    if corrected_offsets.get(CALLEE_ARG1_READ) != {4} or corrected_offsets.get(CALLEE_JOIN) != {8}:
        failures.append(f"R3 corrected offsets changed: {corrected_offsets_report}")
    if not single_ret_invariant:
        failures.append(f"R3 single-ret invariant failed: {fmt(corrected_ret)}")

    # R5 is a real assertion above, not merely a field copied into the report.
    report["r5_map_entry_caller_assertion"] = {
        "expected": fmt(MAP_CALLERS),
        "observed": fmt(map_callers),
        "asserted": map_callers == list(MAP_CALLERS),
        "verdict": "PASS" if map_callers == list(MAP_CALLERS) else "FAIL",
    }
    report["anchors"] = anchor_matches
    report["map_cfg"] = {
        "unresolved_branches": map_unresolved,
        "reachable_instruction_count": len(reachable(map_graph, MAP_ENTRY)),
        "returns": fmt(map_rets),
    }
    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "indirect/virtual writers outside these inspected sites remain unknown",
        "map-caller and dialog-caller event/thread order remains UNKNOWN",
        "this probe does not produce G1/G2/G3/G4 product evidence",
    ]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
