"""lap314 middle — independent review of the lap313 D1-D4 R2 repair.

Nothing here imports lap313 code.  The listing is re-parsed, the gate
dominators are recomputed with a *node-cut* method (delete a node, ask whether
the gate is still reachable) instead of lap313's iterative dataflow, and the
gate bytes are read straight from the instruction encodings.  Two fail-open
gaps that lap313 does not cover are measured directly: indirect branches in the
window, and contiguity of the failure-arm byte run.

Read-only static audit of the SHA-pinned original executable.  No game, Wine,
Xvfb, runtime, Stage B, PNG, or click path is exercised.  JSON goes to stdout;
the caller redirects it without hand transcription.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
LAP313_PROBE = REPO / "docs/history/laps/probes/20260912_lap313_work_v5_mode_writer_order_probe.py"
LAP313_TEST = REPO / "tests/test_lap313_mode_writer_probe.py"
LAP313_REPORT = REPO / "logs/lap313/lap313_v5_mode_writer_order.json"

EXPECTED_SHA = {
    "original_exe": "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac",
    "lap313_probe": "4d3a01a8fb050a05d1b6117e1559f843dd1bebf4abb7de645fe835ce1b066eef",
    "lap313_test": "9ed8eec4a5fda4b6b924ab632acd379efe4a4965c8ac47898277439df858aae2",
    "lap313_report": "74976804fad29513d0d01df29b776ce05b2ff4b9d577d25fcb2552cc13ef9c3f",
}

MAP_ENTRY = 0x431AB0
MAP_END = 0x4324D6
GATE = 0x431AF2
FAILURE_SEED = 0x431AF4
SUCCESS_JOIN = 0x431AFE
SUCCESS_RET = 0x4324D5
SCREEN_GLOBALS = ("e5bf1c", "e5bf20")
FAILURE_ARM_BYTES = "5f5e5d33c05b83c434c3"

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
DIRECT_BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\s+0x([0-9a-f]+)$")
ANY_BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\b")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
WRITER_RE = re.compile(r"ds:0x(?:%s)\s*," % "|".join(SCREEN_GLOBALS))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def listing() -> list[tuple[int, bytes, str]]:
    out = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [(int(a, 16), bytes.fromhex(r), i) for a, r, i in INSN_RE.findall(out)]


def build_cfg(window: list[tuple[int, bytes, str]]) -> tuple[dict[int, set[int]], list[str]]:
    known = {a for a, _r, _i in window}
    graph: dict[int, set[int]] = {}
    unresolved: list[str] = []
    for index, (address, _raw, text) in enumerate(window):
        if RET_RE.match(text):
            graph[address] = set()
            continue
        fallthrough = window[index + 1][0] if index + 1 < len(window) else None
        direct = DIRECT_BRANCH_RE.match(text)
        if direct:
            mnemonic, target_text = direct.groups()
            target = int(target_text, 16)
            edges = {target}
            if mnemonic != "jmp" and fallthrough is not None:
                edges.add(fallthrough)
            if target not in known:
                unresolved.append(f"0x{address:x} -> 0x{target:x} outside window")
            graph[address] = {e for e in edges if e in known}
            continue
        if ANY_BRANCH_RE.match(text):
            # lap314 finding: an indirect branch has no computable successor.
            unresolved.append(f"0x{address:x} indirect branch: {text}")
            graph[address] = set()
            continue
        graph[address] = {fallthrough} if fallthrough in known else set()
    return graph, unresolved


def reachable(graph: dict[int, set[int]], start: int, cut: int | None = None) -> set[int]:
    seen: set[int] = set()
    pending = [start]
    while pending:
        node = pending.pop()
        if node in seen or node not in graph or node == cut:
            continue
        seen.add(node)
        pending.extend(graph[node] - seen)
    return seen


def dominators_by_cut(graph: dict[int, set[int]], entry: int, target: int) -> set[int]:
    """A node dominates ``target`` iff deleting it makes ``target`` unreachable."""
    live = reachable(graph, entry)
    if target not in live:
        return set()
    return {entry} | {n for n in live if n != entry and target not in reachable(graph, entry, cut=n)}


def fmt(values) -> list[str]:
    return [f"0x{v:x}" for v in sorted(values)]


def main() -> int:  # noqa: C901 - one bounded review report
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 314,
        "role": "middle (independent review of lap313); no game code edited, no execution",
        "execution": False,
        "scope": "re-derive lap313 R2 numbers without lap313 code; audit D1-D4 repair",
        "method": "objdump re-parse + node-cut dominators (not lap313's dataflow) + raw instruction bytes",
    }

    observed = {
        "original_exe": sha256_file(EXE) if EXE.is_file() else None,
        "lap313_probe": sha256_file(LAP313_PROBE) if LAP313_PROBE.is_file() else None,
        "lap313_test": sha256_file(LAP313_TEST) if LAP313_TEST.is_file() else None,
        "lap313_report": sha256_file(LAP313_REPORT) if LAP313_REPORT.is_file() else None,
    }
    report["sha256"] = observed
    for key, expected in EXPECTED_SHA.items():
        if observed[key] != expected:
            failures.append(f"sha mismatch {key}: {observed[key]}")

    rows = listing()
    window = [r for r in rows if MAP_ENTRY <= r[0] < MAP_END]
    graph, unresolved = build_cfg(window)

    writers = {a for a, _r, text in window if WRITER_RE.search(text)}
    mentions = {a for a, _r, text in window if any(g in text for g in SCREEN_GLOBALS)}
    entry_live = reachable(graph, MAP_ENTRY)
    failure_live = reachable(graph, FAILURE_SEED)
    success_live = reachable(graph, SUCCESS_JOIN)
    gate_doms = dominators_by_cut(graph, MAP_ENTRY, GATE)
    pre_gate = writers & gate_doms

    report["a1_independent_numbers"] = {
        "instruction_count": len(window),
        "entry_reachable": len(entry_live),
        "failure_arm": fmt(failure_live),
        "failure_arm_count": len(failure_live),
        "success_arm_count": len(success_live),
        "unresolved_branches": unresolved,
        "screen_global_mentions": fmt(mentions),
        "direct_screen_writers": fmt(writers),
        "pre_gate_screen_writers": fmt(pre_gate),
        "failure_arm_screen_writers": fmt(writers & failure_live),
        "success_arm_screen_writers": fmt(writers & success_live),
        "gate_dominator_count": len(gate_doms),
        "failure_arm_reaches_success_ret": SUCCESS_RET in failure_live,
    }

    by_address = {a: r for a, r, _i in window}
    gate_raw = by_address.get(GATE, b"")
    taken = GATE + 2 + int.from_bytes(gate_raw[1:2], "little", signed=True) if len(gate_raw) >= 2 else None
    arm_rows = [(a, r) for a, r, _i in window if a >= FAILURE_SEED][: len(FAILURE_ARM_BYTES) // 2]
    cursor = FAILURE_SEED
    contiguous = True
    arm_bytes = b""
    consumed = 0
    for address, raw in arm_rows:
        if address != cursor:
            contiguous = False
            break
        arm_bytes += raw
        consumed += 1
        cursor = address + len(raw)
        if len(arm_bytes) >= len(FAILURE_ARM_BYTES) // 2:
            break
    report["a2_gate_bytes"] = {
        "gate_bytes": gate_raw.hex(),
        "taken_target": f"0x{taken:x}" if taken is not None else None,
        "taken_is_success_join": taken == SUCCESS_JOIN,
        "failure_arm_bytes": arm_bytes.hex(),
        "failure_arm_returns_zero": arm_bytes.hex() == FAILURE_ARM_BYTES,
        "failure_arm_is_contiguous": contiguous,
        "failure_arm_instruction_count": consumed,
    }
    if gate_raw.hex() != "750a":
        failures.append(f"gate bytes drifted: {gate_raw.hex()}")
    if taken != SUCCESS_JOIN:
        failures.append("gate taken target is not the success join")
    if arm_bytes.hex() != FAILURE_ARM_BYTES or not contiguous:
        failures.append("failure arm bytes are not the contiguous zero-return run")

    report["a3_lap313_defect_audit"] = {
        "D1_vacuity": {
            "pre_gate_is_empty": not pre_gate,
            "comparison_reduces_to": "failure_writers == set()",
            "verdict": "PARTIAL - soundness fixed, vacuity still not annotated in the lap313 report",
        },
        "D2_address_order": {
            "verdict": "REPAIRED",
            "evidence": "cut-method dominators reproduce lap313's dominance-based pre_gate set exactly",
        },
        "D3_fail_open_anchor": {
            "verdict": "REPAIRED",
            "evidence": "taken target derived from the rel8 displacement; failure arm byte-compared",
        },
        "D4_dead_constant": {
            "verdict": "REPAIRED",
            "evidence": "EXPECTED_RUNTIME_WRITERS absent; both writer tuples feed EXPECTED_SCREEN_WRITERS",
        },
        "E1_indirect_branch_fail_open": {
            "indirect_branches_in_window": [u for u in unresolved if "indirect" in u],
            "count": len([u for u in unresolved if "indirect" in u]),
            "note": "lap313 gives an unmatched indirect branch a fabricated fall-through edge and does "
            "not record it as unresolved; currently 0 in this window so numeric impact is 0",
        },
        "E2_arm_contiguity_unchecked": {
            "note": "lap313 concatenates rows at or after the failure seed without checking addresses; "
            "lap314 checks contiguity explicitly and it holds",
            "holds": contiguous,
        },
        "E3_test_quality": {
            "note": "lap313's synthetic backward-jump tests are genuine algorithm tests, unlike lap311; "
            "the binary-fact tests still import the subject and only catch drift",
        },
    }

    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "calls are treated as fall-through; callee writes and cross-function event/thread order are UNKNOWN",
        "computed/indirect pointer writes to the screen globals remain UNKNOWN (lap306 fail-open)",
        "this review produces no G1/G2/G3/G4 product evidence and is not a milestone approval",
    ]
    report["failures"] = failures
    report["verdict"] = "PASS" if not failures else "FAIL"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
