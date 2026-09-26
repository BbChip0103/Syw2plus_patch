"""lap280 middle probe — independent cross-verification of the lap279 S1 review.

Read-only. Re-derives the facts lap279 asserted from raw objdump output using a
different extraction path, then checks the two things lap279 did NOT enumerate:
the 28 map-layer serializer pairs, and the unit-record x/y field offsets that
`docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.2.5 still lists as open.

No game, no Wine, no Xvfb, no Stage B, no writes to the original tree.

Usage: .venv/bin/python docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py
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
DRIVER = REPO / "patches" / "population" / "runtime_driver.py"
EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

SAVE_ENTRY, SAVE_END = 0x440C20, 0x440FF0
LOAD_ENTRY, LOAD_TAIL = 0x440FF0, 0x441310  # load tail = just past the roster call
FWRITE, FREAD = "0x4da39f", "0x4da4a9"
LAYER_LO, LAYER_HI = 0x42A900, 0x42BD00
UNIT_BASE, UNIT_STRIDE = 0x0066B790, 0x758
PLAYER_BASE, PLAYER_STRIDE = 0x00956770, 0x3ABC
BULK_PTR, BULK_LEN = 0x00892410, 0xE397C

CALL_RE = re.compile(r"call\s+0x([0-9a-f]+)")
LINE_RE = re.compile(r"\s*([0-9a-f]+):\t[0-9a-f ]+\t(\S+)\s*(.*)")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disasm(start: int, stop: int) -> str:
    return subprocess.run(
        ["objdump", "-d", "-Mintel", "-j", ".text",
         f"--start-address={start:#x}", f"--stop-address={stop:#x}", str(EXE)],
        check=True, capture_output=True, text=True,
    ).stdout


def calls_in(text: str, lo: int, hi: int) -> list[int]:
    """Ordered call targets inside [lo, hi)."""
    return [t for t in (int(m, 16) for m in CALL_RE.findall(text)) if lo <= t < hi]


def crt_blocks(text: str, callee: str) -> tuple[int, list[tuple[int, int]]]:
    """Return (total call count, literal (ptr, bytes) blocks) for a CRT io callee."""
    pushes: list[int | None] = []
    total, out = 0, []
    for line in text.splitlines():
        m = LINE_RE.match(line)
        if not m:
            continue
        op, args = m.group(2), m.group(3).strip()
        if op == "push":
            pushes.append(int(args, 16) if re.fullmatch(r"0x[0-9a-f]+", args) else None)
        elif op == "call":
            if callee in args and len(pushes) >= 4:
                total += 1
                _file, count, size, ptr = pushes[-4:]
                if ptr is not None and size is not None and count is not None:
                    out.append((ptr, size * count))
            pushes = []
    return total, out


def main() -> int:
    failures: list[str] = []
    actual = sha256(EXE)
    if actual != EXPECTED_EXE_SHA:
        print(f"FAIL original exe sha mismatch: {actual}", file=sys.stderr)
        return 2

    save_txt = disasm(SAVE_ENTRY, SAVE_END)
    load_txt = disasm(LOAD_ENTRY, LOAD_TAIL)

    # (1) Re-derive the literal block tables independently of the lap279 probe.
    save_n, save_lit = crt_blocks(save_txt, FWRITE)
    load_n, load_lit = crt_blocks(load_txt, FREAD)
    if (save_n, load_n) != (22, 22):
        failures.append(f"expected 22/22 crt io calls, got {save_n}/{load_n}")
    if len(save_lit) != 21 or save_lit != load_lit:
        failures.append(f"literal block tables differ or are not 21 "
                        f"({len(save_lit)} vs {len(load_lit)})")
    # The one non-literal block is a 0x40-byte stack buffer written first (save header).
    if (BULK_PTR, BULK_LEN) not in load_lit:
        failures.append("bulk block fread(0x892410, 0xE397C, 1) not found")

    # (2) lap279 did not enumerate these: the map-layer serializers called after the
    #     literal table.  Save and load must call the same number, pairwise adjacent,
    #     and each save-side helper must write while each load-side helper reads.
    save_layers = calls_in(save_txt, LAYER_LO, LAYER_HI)
    load_layers = calls_in(load_txt, LAYER_LO, LAYER_HI)
    if len(save_layers) != len(load_layers) or not save_layers:
        failures.append(f"layer serializer counts differ: "
                        f"{len(save_layers)} save vs {len(load_layers)} load")
    deltas = [ld - sv for sv, ld in zip(save_layers, load_layers)]
    if any(d <= 0 or d > 0x100 for d in deltas):
        failures.append(f"layer pairs are not adjacent functions: deltas={deltas}")
    bounds = sorted(set(save_layers) | set(load_layers)) + [LAYER_HI]
    body = {}
    for lo, hi in zip(bounds, bounds[1:]):
        body[lo] = disasm(lo, hi)
    for fn in save_layers:
        if FWRITE not in body[fn]:
            failures.append(f"save layer {fn:#x} does not call fwrite")
    for fn in load_layers:
        if FREAD not in body[fn]:
            failures.append(f"load layer {fn:#x} does not call fread")
    # Bounds really are the element-count argument of the first layer serializer.
    if not all(n in body[save_layers[0]] for n in ("ecx+0x8c", "ecx+0x8e", "imul")):
        failures.append("first layer serializer does not imul the map bounds")

    # (3) §4.2.5 item 1 — the unit-record x/y offsets.  They are already pinned in
    #     patches/population/runtime_driver.py; corroborate them against absolute
    #     base-relative references in the original binary.
    src = DRIVER.read_text(encoding="utf-8")
    env_src = (REPO / "tools" / "runtime_env.py").read_text(encoding="utf-8")
    pinned = {}
    for field in ("type", "owner"):
        literal = re.search(rf"{field}=u\[0x([0-9A-Fa-f]+)\]", src)
        if literal is None:
            failures.append(f"{field} literal missing from runtime_driver.py")
            continue
        pinned[field] = int(literal.group(1), 16)
    offset_names = {
        "internal_id": "G1_UNIT_INTERNAL_ID_OFFSET",
        "x": "G1_UNIT_X_OFFSET",
        "y": "G1_UNIT_Y_OFFSET",
    }
    for field, name in offset_names.items():
        definition = re.search(
            rf"^{re.escape(name)} = 0x([0-9A-Fa-f]+)$", env_src, re.MULTILINE
        )
        if definition is None:
            failures.append(f"{name} definition missing from tools/runtime_env.py")
            continue
        pinned[field] = int(definition.group(1), 16)
        if re.search(
            rf"\b{field}\s*=\s*[A-Za-z_][A-Za-z0-9_]*\({re.escape(name)}\)", src
        ) is None:
            failures.append(f"runtime_driver does not bind {field} to {name}")
    offsets = tuple(pinned.get(field) for field in ("x", "y", "internal_id"))
    if all(value is not None for value in offsets) and offsets != (0x2A2, 0x2A4, 0x29C):
        failures.append(f"runtime_driver unit offsets drifted: {pinned}")
    whole = disasm(0x401000, 0x4E0000)
    width = {"x": "WORD", "y": "WORD", "internal_id": "DWORD"}
    refs = {}
    for name in ("x", "y", "internal_id"):
        if name not in pinned:
            continue
        abs_addr = UNIT_BASE + pinned[name]
        hits = re.findall(rf"(WORD|DWORD) PTR \[e[a-z]{{2}}(?:\*8)?\+0x{abs_addr:x}\]", whole)
        refs[name] = {"address": f"{abs_addr:#010x}", "hits": len(hits),
                      "widths": sorted(set(hits))}
        if not hits:
            failures.append(f"no base-relative reference to {name} at {abs_addr:#x}")
        elif sorted(set(hits)) != [width[name]]:
            failures.append(f"{name} at {abs_addr:#x} accessed as {sorted(set(hits))}, "
                            f"expected {width[name]}")
    # The 0x40F540 accessor indexes the same array by slot and returns +0x29C.
    accessor = disasm(0x40F540, 0x40F560)
    if "internal_id" in pinned and f"0x{UNIT_BASE + pinned['internal_id']:x}" not in accessor:
        failures.append("accessor 0x40F540 does not read the internal_id field")

    # (4) G3 boundary arithmetic, recomputed from this probe's own constants.
    bulk_end = BULK_PTR + BULK_LEN
    need16 = PLAYER_BASE + 16 * PLAYER_STRIDE
    overflow = need16 - bulk_end
    if PLAYER_BASE + 8 * PLAYER_STRIDE > bulk_end or overflow != 0x1B5A4:
        failures.append(f"G3 overflow arithmetic unexpected: overflow={overflow:#x}")

    report = {
        "exe_sha256": actual,
        "literal_blocks": len(load_lit),
        "crt_io_calls": {"save_fwrite": save_n, "load_fread": load_n},
        "non_literal_blocks": save_n - len(save_lit),
        "block_table_identical": save_lit == load_lit,
        "layer_serializers": {
            "count": len(save_layers),
            "save_first_last": [f"{save_layers[0]:#010x}", f"{save_layers[-1]:#010x}"],
            "load_first_last": [f"{load_layers[0]:#010x}", f"{load_layers[-1]:#010x}"],
            "pair_deltas": sorted(set(deltas)),
        },
        "unit_record_offsets": {k: f"0x{v:X}" for k, v in pinned.items()},
        "unit_record_refs": refs,
        "g3": {"bulk_end": f"{bulk_end:#010x}",
               "need_16_players": f"{need16:#010x}",
               "overflow_bytes": f"{overflow:#x}"},
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
