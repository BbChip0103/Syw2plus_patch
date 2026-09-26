#!/usr/bin/env python3
"""lap322 middle — independent evidence for the §13 runtime-envelope document review.

Read-only. No game/Wine/Xvfb/Stage B/click/PNG production, no writes outside stdout.
Every fact this probe reports is re-derived here rather than imported from an
earlier lap's probe, so a disagreement with a prior lap is a real disagreement.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
GAME = REPO.parent / "Syw2plus"
TEMP = REPO.parent / "temp"
RUNTIME_ENV = REPO / "tools/runtime_env.py"
CONTRACT = REPO / "docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_facts() -> dict:
    out = {}
    for name, path in (
        ("save000", GAME / "save/save000.dat"),
        ("save006", GAME / "save/save006.dat"),
        ("save011", REPO / "local/fixtures/20260910/save011.dat"),
        ("save012", REPO / "local/fixtures/20260910/save012.dat"),
    ):
        out[name] = ({"present": False} if not path.exists()
                     else {"present": True, "bytes": path.stat().st_size, "sha256": sha256(path)})
    return out


def title_capture_facts() -> dict:
    pngs = sorted(TEMP.glob("*title_before_menu*.png")) if TEMP.is_dir() else []
    digests = sorted({sha256(p) for p in pngs})
    sizes = set()
    for p in pngs:
        head = p.read_bytes()[:33]
        # PNG IHDR: 8-byte signature, 4-byte length, "IHDR", width, height (big-endian).
        if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
            sizes.add(struct.unpack(">II", head[16:24]))
    return {"count": len(pngs), "distinct_sha256": digests,
            "distinct_sizes": [list(item) for item in sorted(sizes)]}


def dialog_origin_candidates() -> dict:
    spr = GAME / "yfnt/saveloadtitle.spr"
    if not spr.exists():
        return {"present": False}
    header = struct.unpack("<4I", spr.read_bytes()[:16])
    _, width, height, _ = header
    return {
        "present": True,
        "bytes": spr.stat().st_size,
        "sha256": sha256(spr),
        "header_dwords": list(header),
        "sprite_wh": [width, height],
        # The two lap301 candidates are the SAME centring formula evaluated on the
        # two screen-global pairs that lap312/lap316 left unresolved.  This is the
        # point of the row-2 UNKNOWN, not a promotion of either candidate.
        "origin_if_screen_800x600": [(800 - width) // 2, (600 - height) // 2],
        "origin_if_screen_640x480": [(640 - width) // 2, (480 - height) // 2],
    }


def harness_facts() -> dict:
    src = RUNTIME_ENV.read_text(encoding="utf-8")
    tree = ast.parse(src)

    # (i) lap284's two regex guards, re-run verbatim.
    lap284_ps_states_waited = sorted({int(m) for m in re.findall(r'get\("ps"\)\s*==\s*(\d+)', src)})
    lap284_ps35_references = len(re.findall(r"\b35\b(?=[^\n]*ps)|ps.{0,12}==\s*35", src))
    lap284_save_references = len(re.findall(r"\bsave\d|save\\\\|\.dat\b|load_game", src))

    # (ii) A stronger scan: every integer a ps-bearing expression is compared to,
    # including set membership, which the == regex cannot see.
    ast_ps_compared: set[int] = set()
    membership_sites: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        left = ast.unparse(node.left)
        if not re.search(r"\bps\b", left):
            continue
        for op, comp in zip(node.ops, node.comparators):
            if isinstance(comp, ast.Constant) and isinstance(comp.value, int):
                ast_ps_compared.add(comp.value)
            elif isinstance(comp, (ast.Set, ast.Tuple, ast.List)):
                values = [e.value for e in comp.elts
                          if isinstance(e, ast.Constant) and isinstance(e.value, int)]
                ast_ps_compared.update(values)
                if isinstance(op, ast.In):
                    membership_sites.append({"line": node.lineno, "values": sorted(values),
                                             "source": ast.unparse(node)[:90]})

    # (iii) Does the == regex see the membership form?  Demonstrate on the real
    # line and on the hypothetical PS35 line the guard is supposed to catch.
    real_membership = next((s["source"] for s in membership_sites), "")
    hypothetical = 'state, lambda item: item.get("ps") in {35, 3}, started, timeout,'
    guard_fail_open = {
        "real_membership_line_seen_by_eq_regex":
            bool(re.findall(r'get\("ps"\)\s*==\s*(\d+)', real_membership)),
        "hypothetical_ps35_membership_seen_by_eq_regex":
            bool(re.findall(r'get\("ps"\)\s*==\s*(\d+)', hypothetical)),
        "hypothetical_ps35_membership_seen_by_ps35_regex":
            bool(re.findall(r"\b35\b(?=[^\n]*ps)|ps.{0,12}==\s*35", hypothetical)),
        "hypothetical_ps35_equality_seen_by_ps35_regex":
            bool(re.findall(r"\b35\b(?=[^\n]*ps)|ps.{0,12}==\s*35",
                            'lambda item: item.get("ps") == 35,')),
    }

    # (iv) Independent, form-agnostic check that 35 is absent from the harness at all.
    bare_35_occurrences = len(re.findall(r"(?<![\w.])35(?![\w.])", src))

    # (v) Flush cadence: which functions call the per-stage persistence helper.
    flush_callers = sorted({
        node.lineno for node in ast.walk(tree)
        if isinstance(node, ast.Call) and ast.unparse(node.func).endswith(
            ("flush", "flush_input_stage", "_g1_flush_input_stage"))
    })

    stage_budgets = None
    for node in ast.walk(tree):
        if (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
                and node.target.id == "G1_INPUT_STAGE_BUDGETS" and node.value is not None):
            stage_budgets = ast.literal_eval(node.value)

    return {
        "lap284_ps_states_waited": lap284_ps_states_waited,
        "lap284_ps35_references": lap284_ps35_references,
        "lap284_save_references": lap284_save_references,
        "ast_ps_values_compared": sorted(ast_ps_compared),
        "ps_set_membership_waits": membership_sites,
        "guard_fail_open": guard_fail_open,
        "bare_35_occurrences": bare_35_occurrences,
        "flush_call_sites": flush_callers,
        "stage_budgets": stage_budgets,
        "timeout_cap_90": "timeout > 90" in src,
        "load_click_296_505_present": bool(re.search(r"\b296\b", src) or re.search(r"\b505\b", src)),
        "title_click_184_560_sites": sorted({
            i for i, line in enumerate(src.splitlines(), 1)
            if "184" in line and "560" in line}),
    }


def main() -> int:
    failures: list[str] = []

    fixtures = fixture_facts()
    titles = title_capture_facts()
    origins = dialog_origin_candidates()
    harness = harness_facts()
    exe = GAME / "game.exe"
    exe_sha = sha256(exe) if exe.exists() else None

    # Contract-sourced values this review depends on; a mismatch must be loud.
    if fixtures["save000"].get("bytes") != 3_093_902:
        failures.append("save000 size disagrees with contract §2")
    if fixtures["save006"].get("bytes") != 3_437_942:
        failures.append("save006 size disagrees with contract §2")
    if titles["count"] != 14 or len(titles["distinct_sha256"]) != 1:
        failures.append("title capture determinism (14 captures, 1 sha) not reproduced")
    if titles["distinct_sizes"] != [[800, 600]]:
        failures.append("title captures are not uniformly 800x600")
    if origins.get("origin_if_screen_800x600") != [240, 145]:
        failures.append("candidate A did not re-derive to (240,145)")
    if origins.get("origin_if_screen_640x480") != [160, 85]:
        failures.append("candidate B did not re-derive to (160,85)")
    if harness["lap284_save_references"] != 0:
        failures.append("harness now references save files; contract §3 premise changed")
    if harness["bare_35_occurrences"] != 0:
        failures.append("harness contains a literal 35; PS35 absence must be re-argued")
    if not harness["timeout_cap_90"]:
        failures.append("90s timeout cap no longer enforced")
    if harness["load_click_296_505_present"]:
        failures.append("load candidate (296,505) is wired into the harness; it must stay document-only")
    if exe_sha != "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac":
        failures.append("original game.exe sha changed")

    # The two findings this review reports as measurement defects.  They are
    # asserted as PRESENT so that a future repair of the guards makes this probe
    # fail loudly rather than silently agreeing.
    if set(harness["ast_ps_values_compared"]) <= set(harness["lap284_ps_states_waited"]):
        failures.append("N6 premise gone: eq-regex now covers every compared ps value")
    if not harness["ps_set_membership_waits"]:
        failures.append("N6 premise gone: no ps set-membership wait remains")
    if harness["guard_fail_open"]["hypothetical_ps35_membership_seen_by_ps35_regex"]:
        failures.append("N6 premise gone: ps35 guard now catches the membership form")

    report = {
        "lap": 322,
        "role": "middle (Opus5/high) — document review of runtime contract §13",
        "scope": "read-only static evidence; game/Wine/Xvfb/StageB/click/PNG budget = 0",
        "exe_sha256": exe_sha,
        "fixtures": fixtures,
        "title_captures": titles,
        "dialog_origin_candidates": origins,
        "harness": harness,
        "contract_sha256": sha256(CONTRACT) if CONTRACT.exists() else None,
        "runtime_env_sha256": sha256(RUNTIME_ENV),
        "notes": [
            "Candidate A/B are one formula on two screen-global pairs; neither is promoted.",
            "PS35 absence is established by bare_35_occurrences==0, NOT by the lap284 regex.",
            "Flush call sites are per-record, not per-stage; see flush_call_sites.",
        ],
        "failures": failures,
        "verdict": "PASS" if not failures else "FAIL",
    }
    json.dump(report, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
