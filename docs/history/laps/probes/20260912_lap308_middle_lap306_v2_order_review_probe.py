"""lap308 middle — independent review of the lap306 work V2 static probe.

Read-only static review of the SHA-pinned original executable.  It re-derives the
V2 claims from its own disassembly instead of importing or trusting the work
probe, and it separately audits two V2 gates that are structurally fail-open or
internally inconsistent.  No game, Wine, Xvfb, runtime harness, Stage B, PNG, or
click execution.
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

V2_PROBE = Path(__file__).resolve().parent / "20260912_lap306_work_v2_mode_writer_order_probe.py"
EXPECTED_V2_PROBE_SHA = "c8ada3f90eb254a56a6193f243017de4dcc63c4a56fefc57d685dccda5ca0c44"
V2_REPORT = REPO / "logs" / "lap306" / "lap306_v2_mode_writer_order.json"
EXPECTED_V2_REPORT_SHA = "9eb6913ef8e0416d582bb1b2038b6d1f4658a7762e40f2f88aa1cf86ba02014d"

MAP_ENTRY = 0x431AB0
MAP_END = 0x4324D6
MAP_GATE_BRANCH = 0x431AF2
MAP_FAILURE_FALLTHROUGH = 0x431AF4
MAP_FAILURE_RET = 0x431AFD
MAP_SUCCESS_JOIN = 0x431AFE
MAP_SUCCESS_RET = 0x4324D5
RUNTIME_WRITERS = (0x431B79, 0x431B7F)
RESET_WRITERS = (0x4324B8, 0x4324C2)
DIALOG_ENTRY = 0x4D60B0
CALLEE = 0x465250
CALLEE_END = 0x4652AF
CALLEE_VCALL = 0x465284
CALLEE_JOIN = 0x465287
CALLEE_RET = 0x4652AE
CALLEE_ARG1_READ = 0x46526D

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t([0-9a-f ]+?)\s*\t(.+?)\s*$", re.MULTILINE)
BRANCH_RE = re.compile(r"^(j[a-z]+|loop[a-z]*)\s+0x([0-9a-f]+)$")
RET_RE = re.compile(r"^ret(?:\s+0x[0-9a-f]+)?$")
ESP_ADJUST_RE = re.compile(r"^(sub|add)\s+esp,0x([0-9a-f]+)$")
ESP_PLAIN_RE = re.compile(r"\[esp(?:\+0x([0-9a-f]+))?\]")
ESP_ANY_RE = re.compile(r"\[esp[^\]]*\]")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_text() -> list[tuple[int, str]]:
    out = subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text", str(EXE)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return [(int(a, 16), i) for a, _b, i in INSN_RE.findall(out)]


def build_cfg(window: list[tuple[int, str]]) -> tuple[dict[int, set[int]], list[str]]:
    """Intraprocedural successors.  Any branch form we cannot resolve is recorded."""
    known = {address for address, _ in window}
    graph: dict[int, set[int]] = {}
    unresolved: list[str] = []
    for index, (address, instruction) in enumerate(window):
        if RET_RE.match(instruction):
            graph[address] = set()
            continue
        nxt = window[index + 1][0] if index + 1 < len(window) else None
        match = BRANCH_RE.match(instruction)
        if match:
            mnemonic, target_text = match.groups()
            edges = {int(target_text, 16)}
            if mnemonic != "jmp" and nxt is not None:
                edges.add(nxt)
            graph[address] = {e for e in edges if e in known}
            continue
        if instruction.startswith(("j", "loop")):
            unresolved.append(f"0x{address:x}: {instruction}")
        graph[address] = {nxt} if nxt in known else set()
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
    preds: dict[int, set[int]] = {n: set() for n in nodes}
    for source in nodes:
        for target in graph[source] & nodes:
            preds[target].add(source)
    dom = {n: set(nodes) for n in nodes}
    dom[start] = {start}
    changed = True
    while changed:
        changed = False
        for node in sorted(nodes - {start}):
            incoming = preds[node]
            if not incoming:
                candidate = {node}
            else:
                candidate = {node} | set.intersection(*(dom[p] for p in incoming))
            if candidate != dom[node]:
                dom[node] = candidate
                changed = True
    return dom


def esp_delta(instruction: str, vcall_cleanup: int, address: int) -> int:
    match = ESP_ADJUST_RE.match(instruction)
    if match:
        amount = int(match.group(2), 16)
        return amount if match.group(1) == "sub" else -amount
    if instruction.startswith("push"):
        return 4
    if instruction.startswith("pop"):
        return -4
    if address == CALLEE_VCALL:
        return -vcall_cleanup
    return 0


def walk_depths(
    window: list[tuple[int, str]], start: int, vcall_cleanup: int
) -> tuple[dict[int, set[int]], dict[int, set[int]]]:
    """Entry-relative depths and raw->entry offsets under one call-cleanup model."""
    graph, _ = build_cfg(window)
    body = dict(window)
    depths: dict[int, set[int]] = {start: {0}}
    offsets: dict[int, set[int]] = {}
    pending = [start]
    while pending:
        address = pending.pop()
        current = set(depths.get(address, set()))
        instruction = body[address]
        for match in ESP_PLAIN_RE.finditer(instruction):
            raw = int(match.group(1), 16) if match.group(1) else 0
            offsets.setdefault(address, set()).update(raw - depth for depth in current)
        out = {depth + esp_delta(instruction, vcall_cleanup, address) for depth in current}
        for target in graph.get(address, set()):
            merged = depths.setdefault(target, set()) | out
            if merged != depths[target]:
                depths[target] = merged
                pending.append(target)
    return depths, offsets


def fmt(values: set[int] | list[int] | tuple[int, ...]) -> list[str]:
    return [f"0x{v:x}" for v in sorted(values)]


def main() -> int:  # noqa: C901 - single audit report, kept linear on purpose
    failures: list[str] = []
    notes: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 308,
        "role": "middle (independent review/confirm); no game code edited, no execution",
        "execution": False,
        "reviews": "lap306 work V2 (20260912_lap306_work_v2_mode_writer_order_probe.py)",
    }

    for label, path, expected in (
        ("original_exe", EXE, EXPECTED_EXE_SHA),
        ("v2_probe", V2_PROBE, EXPECTED_V2_PROBE_SHA),
        ("v2_report", V2_REPORT, EXPECTED_V2_REPORT_SHA),
    ):
        if not path.is_file():
            failures.append(f"missing reviewed input: {label} {path}")
    if failures:
        report["failures"] = failures
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1
    shas = {
        "original_exe": sha256_file(EXE),
        "v2_probe": sha256_file(V2_PROBE),
        "v2_report": sha256_file(V2_REPORT),
    }
    report["sha256"] = shas
    for label, expected in (
        ("original_exe", EXPECTED_EXE_SHA),
        ("v2_probe", EXPECTED_V2_PROBE_SHA),
        ("v2_report", EXPECTED_V2_REPORT_SHA),
    ):
        if shas[label] != expected:
            failures.append(f"{label} sha mismatch: {shas[label]} != {expected}")

    instructions = parse_text()
    body = dict(instructions)
    if not instructions:
        failures.append("objdump produced no .text instructions")

    # ── R1: re-derive the V2 anchors from our own listing ───────────────────
    anchors = {
        0x431AE1: "call   0x4da96e",
        0x431AEB: "cmp    eax,ebx",
        0x431AF2: "jne    0x431afe",
        0x431AF7: "xor    eax,eax",
        0x431AFD: "ret",
        0x431B79: "mov    DWORD PTR ds:0xe5bf1c,ebp",
        0x431B7F: "mov    DWORD PTR ds:0xe5bf20,edi",
        0x4324B8: "mov    DWORD PTR ds:0xe5bf1c,0x280",
        0x4324C2: "mov    DWORD PTR ds:0xe5bf20,0x1e0",
        0x4324CC: "mov    eax,0x1",
        0x4324D5: "ret",
        0x4D6312: "mov    eax,ds:0xe5bf1c",
        0x4D631C: "mov    eax,ds:0xe5bf20",
        0x4D632A: "mov    WORD PTR ds:0x1088b5c,cx",
        0x4D6348: "mov    WORD PTR ds:0x1088b5e,di",
    }
    anchor_ok = {f"0x{a:x}": body.get(a, "") == t for a, t in anchors.items()}
    failures.extend(
        f"R1 anchor 0x{a:x}: expected {t!r}, found {body.get(a)!r}"
        for a, t in anchors.items()
        if body.get(a) != t
    )
    map_callers = [a for a, i in instructions if i == f"call   0x{MAP_ENTRY:x}"]
    dialog_callers = [a for a, i in instructions if i == f"call   0x{DIALOG_ENTRY:x}"]
    map_window = [(a, i) for a, i in instructions if MAP_ENTRY <= a < MAP_END]
    map_rets = [a for a, i in map_window if RET_RE.match(i)]
    report["r1_anchor_rederivation"] = {
        "anchors_match": anchor_ok,
        "map_direct_callers": fmt(map_callers),
        "dialog_direct_callers": fmt(dialog_callers),
        "map_returns": fmt(map_rets),
        "verdict": "CONFIRMED" if not failures else "FAIL",
    }
    if map_callers != [0x48F538]:
        failures.append(f"R1 map direct callers changed: {fmt(map_callers)}")
    if dialog_callers != [0x4D69E5, 0x4D6A05]:
        failures.append(f"R1 dialog direct callers changed: {fmt(dialog_callers)}")
    if map_rets != [MAP_FAILURE_RET, MAP_SUCCESS_RET]:
        failures.append(f"R1 map return sites changed: {fmt(map_rets)}")

    # ── R2: the V2 failure-path gate is vacuous; re-seed it correctly ───────
    map_graph, map_unresolved = build_cfg(map_window)
    v2_failure_seed = reachable(map_graph, MAP_FAILURE_RET)
    correct_failure_path = reachable(map_graph, MAP_FAILURE_FALLTHROUGH)
    v2_gate_is_vacuous = v2_failure_seed == {MAP_FAILURE_RET}
    writers_on_failure = [w for w in RUNTIME_WRITERS if w in correct_failure_path]
    success_reach = reachable(map_graph, MAP_SUCCESS_JOIN)
    success_dom = dominators(map_graph, MAP_SUCCESS_JOIN)
    reset_dominates = all(w in success_dom.get(MAP_SUCCESS_RET, set()) for w in RESET_WRITERS)
    report["r2_failure_path_gate"] = {
        "v2_check": "runtime_on_failure = any(writer in reachable(map_graph, 0x431afd))",
        "v2_seed_is_a_ret_instruction": body.get(MAP_FAILURE_RET) == "ret",
        "v2_seed_reachable_set": fmt(v2_failure_seed),
        "v2_gate_is_vacuous": v2_gate_is_vacuous,
        "correct_seed": f"0x{MAP_FAILURE_FALLTHROUGH:x} (fall-through of 0x{MAP_GATE_BRANCH:x} jne)",
        "correct_failure_path": fmt(correct_failure_path),
        "runtime_writers_on_correct_failure_path": fmt(writers_on_failure),
        "runtime_writers_reachable_from_success_join": {
            f"0x{w:x}": w in success_reach for w in RUNTIME_WRITERS
        },
        "reset_writers_dominate_success_ret": reset_dominates,
        "cfg_unresolved_branches": map_unresolved,
        "verdict": "V2 conclusion UPHELD, V2 gate FAIL-OPEN",
        "numeric_impact": 0,
    }
    if not v2_gate_is_vacuous:
        failures.append("R2 could not reproduce the vacuity of the V2 failure-path seed")
    if writers_on_failure:
        failures.append(f"R2 runtime writers do appear on the failure path: {fmt(writers_on_failure)}")
    if not all(w in success_reach for w in RUNTIME_WRITERS):
        failures.append("R2 runtime writers are not reachable from the success join")
    if not reset_dominates:
        failures.append("R2 640x480 reset does not dominate the success return")
    if map_unresolved:
        failures.append(f"R2 map CFG has unresolved branch forms: {map_unresolved}")

    # ── R3: the V2 stack-depth model is internally inconsistent ────────────
    callee_window = [(a, i) for a, i in instructions if CALLEE <= a < CALLEE_END]
    v2_depths, v2_offsets = walk_depths(callee_window, CALLEE, vcall_cleanup=0)
    fixed_depths, fixed_offsets = walk_depths(callee_window, CALLEE, vcall_cleanup=4)
    v2_join = v2_depths.get(CALLEE_JOIN, set())
    fixed_join = fixed_depths.get(CALLEE_JOIN, set())
    v2_ret_depths = v2_depths.get(CALLEE_RET, set())
    fixed_ret_depths = fixed_depths.get(CALLEE_RET, set())
    # The suffix from the join to the single `ret` is straight-line, so distinct
    # join depths must survive to the ret.  A cdecl `ret` cannot pop two esp values.
    inconsistent = len(v2_ret_depths) > 1
    single_valued = len(fixed_ret_depths) == 1
    indexed_esp = [
        f"0x{a:x}: {i}"
        for a, i in callee_window
        if ESP_ANY_RE.search(i) and not ESP_PLAIN_RE.search(i)
    ]
    report["r3_stack_model_audit"] = {
        "callee": f"0x{CALLEE:x}",
        "v2_model": "every call is stack-neutral (esp_delta=0)",
        "v2_depths_at_join": fmt(v2_join),
        "v2_depths_at_single_ret": fmt(v2_ret_depths),
        "v2_model_is_internally_inconsistent": inconsistent,
        "argument": (
            f"0x{CALLEE_RET:x} is the only ret in 0x{CALLEE:x}..0x{CALLEE_END:x} and the path from "
            f"0x{CALLEE_JOIN:x} to it is straight-line, so two distinct join depths imply two distinct "
            "esp values at one cdecl ret, which is impossible"
        ),
        "corrected_model": f"0x{CALLEE_VCALL:x} call DWORD PTR [ecx+0x28] is callee-clean (4 bytes)",
        "corrected_depths_at_join": fmt(fixed_join),
        "corrected_depths_at_single_ret": fmt(fixed_ret_depths),
        "corrected_model_single_valued_at_ret": single_valued,
        "residue_at_ret_is_the_unmodelled_import_cleanup": (
            f"0x{CALLEE_RET:x} residue {fmt(fixed_ret_depths)} is the stdcall cleanup of the import "
            f"call at 0x46529d, which this probe does not model; the claim here is only that the "
            f"depth at the single ret is single-valued, not that it is absolutely zero"
        ),
        "entry_offsets_v2": {
            f"0x{CALLEE_ARG1_READ:x}": sorted(v2_offsets.get(CALLEE_ARG1_READ, set())),
            f"0x{CALLEE_JOIN:x}": sorted(v2_offsets.get(CALLEE_JOIN, set())),
        },
        "entry_offsets_corrected": {
            f"0x{CALLEE_ARG1_READ:x}": sorted(fixed_offsets.get(CALLEE_ARG1_READ, set())),
            f"0x{CALLEE_JOIN:x}": sorted(fixed_offsets.get(CALLEE_JOIN, set())),
        },
        "spurious_arg1_attribution_at_join": 4 in v2_offsets.get(CALLEE_JOIN, set())
        and 4 not in fixed_offsets.get(CALLEE_JOIN, set()),
        "lap306_conclusion_arg1_and_arg2_still_read": (
            fixed_offsets.get(CALLEE_ARG1_READ) == {4} and fixed_offsets.get(CALLEE_JOIN) == {8}
        ),
        "esp_forms_missed_by_the_plain_regex": indexed_esp,
        "verdict": "V2 pinned PASS values ARTIFACT; lap306 arg1/arg2 conclusion UPHELD",
        "numeric_impact": 0,
    }
    if not inconsistent:
        failures.append("R3 could not reproduce the V2 depth inconsistency")
    if fixed_offsets.get(CALLEE_ARG1_READ) != {4} or fixed_offsets.get(CALLEE_JOIN) != {8}:
        failures.append(
            "R3 corrected model did not yield arg1=4 at 0x46526d and arg2=8 at 0x465287: "
            f"{sorted(fixed_offsets.get(CALLEE_ARG1_READ, set()))} / "
            f"{sorted(fixed_offsets.get(CALLEE_JOIN, set()))}"
        )
    if not single_valued:
        failures.append(f"R3 corrected model is still multi-valued at the ret: {fmt(fixed_ret_depths)}")

    # ── R4: the pinned V2 report artifact is a transcription, not probe output ──
    v2_source = V2_PROBE.read_text(encoding="utf-8")
    report_text = V2_REPORT.read_text(encoding="utf-8")
    transcription_only_keys = [k for k in ("fresh_runs", "byte_compare", "output_bytes")
                               if k in report_text and k not in v2_source]
    report["r4_report_artifact_provenance"] = {
        "probe_emits_only_stdout": "print(json.dumps(" in v2_source and "write_text" not in v2_source,
        "report_bytes": len(V2_REPORT.read_bytes()),
        "keys_present_in_report_but_absent_from_the_probe": transcription_only_keys,
        "conclusion": (
            "logs/lap306/lap306_v2_mode_writer_order.json is a hand-written summary, so its SHA pins a "
            "transcription rather than a reproducible generator output"
        ),
        "verdict": "PROVENANCE GAP (values independently re-derived and matching)",
        "numeric_impact": 0,
    }
    if not transcription_only_keys:
        failures.append("R4 could not confirm the report artifact is hand-transcribed")

    # ── R5: which V2 claims are recorded but not gated ──────────────────────
    ungated = []
    if "dialog entry direct callsite set changed" not in v2_source:
        ungated.append("dialog callers (expected a gate, not found)")
    if "map direct call" not in v2_source and "direct_calls_to_entry" in v2_source:
        ungated.append("map entry direct-caller set is reported but never asserted")
    report["r5_ungated_v2_claims"] = {
        "ungated": ungated,
        "note": "drift in the map caller set would not fail the V2 probe",
        "verdict": "FAIL-OPEN (audit only)",
        "numeric_impact": 0,
    }

    notes.append(
        "cross-function order between 0x48f538 (map caller) and 0x4d69e5/0x4d6a05 (dialog callers) "
        "remains UNKNOWN; this review does not narrow it"
    )
    report["notes"] = notes
    report["limitations"] = [
        "static only: no game, Wine, Xvfb, runtime, Stage B, PNG, or clicks",
        "indirect/virtual callers and writers stay outside this review",
        "the corrected call-cleanup model is derived from single-ret balance, not from executing the callee",
        "no G1/G2/G3/G4 product evidence is produced or promoted here",
    ]
    report["middle_verdict"] = (
        "ACCEPT-WITH-CORRECTION: V2 substantive static claims reproduced; R2 gate vacuous and "
        "R3 pinned depth values are an artifact; both need work-tier repair in a NEW file"
    )
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
