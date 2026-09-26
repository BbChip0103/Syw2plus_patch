"""lap302 middle probe — independently review the lap301 save/load layout repair.

Scope: static review only.  The probe reads the SHA-pinned original executable
and the read-only original sprite fixture.  It never runs the game, Wine, Xvfb,
the runtime harness, or any Stage B path, and it never reads a capture as
layout evidence.

What it checks that lap301 did not:

1. ``.text`` / ``.data`` extents are re-derived from the PE headers, so the
   claim "the writer scan covered the whole ``.text``" is checked instead of
   assumed, and the screen globals are shown to live inside ``.data``'s
   virtual (BSS) extension rather than outside the image.
2. The screen globals are also written **indirectly**, as ``[this+4]`` and
   ``[this+8]`` of the graphics object at ``0xE5BF18``.  lap301 enumerated only
   absolute-addressed writes, so its writer set is a lower bound, not the
   exhaustive set its count gate implies.
3. Among the sites that write those two fields, ``800x600`` appears only in
   the mode-table branches, and those branches are an 8-way switch on a
   runtime mode argument, so the reachable static screen set is five
   resolutions, not two.  (The literals ``0x320``/``0x258`` occur widely in
   ``.text`` for unrelated reasons; the probe lists them without claiming
   uniqueness.)
4. The centre formula anchors are pinned **by address**, not by substring
   presence anywhere in a range.

Deliberate non-pin (answer to the W3 failure mode): this probe does not pin the
SHA of any artifact that a later repair lap is expected to change.  Determinism
is checked by running the lap301 probe twice in this session and comparing the
two fresh runs to each other; the archived lap301 log SHA is *reported* for
provenance but never asserted, so repairing the lap301 probe cannot turn this
gate into a permanent exit 1.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus" / "syw2plus_original.exe"
SPRITE = REPO.parent / "Syw2plus" / "yfnt" / "saveloadtitle.spr"
LAP301_PROBE = Path(__file__).with_name("20260912_lap299_work_save_load_layout_probe.py")
LAP301_LOG = REPO / "logs" / "lap301" / "save_load_layout_probe.json"
LAP299_LOG = REPO / "logs" / "lap299" / "save_load_layout_probe.json"

EXPECTED_EXE_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
EXPECTED_SPRITE_SHA = "7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5"
RECORDED_LAP301_LOG_SHA = "c312b42e3593c2af5bb47e9df9e1b624f8a55ea618a1cc70b7e6dc709caaf10a"
RECORDED_LAP299_LOG_SHA = "8e735a9a7f7b4ddbd1ab249039c568b42b16af8b248f47e64681d05476d2bb0b"

GRAPHICS_OBJECT = 0xE5BF18
SCREEN_W_GLOBAL = 0xE5BF1C
SCREEN_H_GLOBAL = 0xE5BF20
ORIGIN_X_GLOBAL = 0x1088B5C
ORIGIN_Y_GLOBAL = 0x1088B5E

# Addresses the review claims, each with the exact instruction expected there.
CENTRE_FORMULA_ANCHORS = {
    0x4D625B: "mov    eax,DWORD PTR [esi+0x10f0]",
    0x4D6310: "mov    edi,eax",
    0x4D6312: "mov    eax,ds:0xe5bf1c",
    0x4D631C: "mov    eax,ds:0xe5bf20",
    0x4D6322: "sar    edi,1",
    0x4D6324: "sar    ecx,1",
    0x4D6326: "sub    ecx,edi",
    0x4D632A: "mov    WORD PTR ds:0x1088b5c,cx",
    0x4D6333: "mov    eax,DWORD PTR [esi+0x10f4]",
    0x4D633C: "sar    edi,1",
    0x4D633E: "sar    eax,1",
    0x4D6340: "sub    edi,eax",
    0x4D6345: "add    eax,0x14",
    0x4D6348: "mov    WORD PTR ds:0x1088b5e,di",
    0x4D6351: "movsx  ecx,WORD PTR ds:0x1088b5e",
    0x4D6358: "sub    ecx,0x1a",
    0x4D635B: "mov    DWORD PTR [esi+0x40c],ecx",
    0x4D6363: "add    edx,0x118",
    0x4D6371: "add    eax,0x18",
}

# The indirect write path: this=0xE5BF18 reaches the mode table.
INDIRECT_CHAIN_ANCHORS = {
    0x423D52: "mov    ecx,0xe5bf18",
    0x423D63: "call   0x464360",
    0x4643BE: "mov    ecx,esi",
    0x4643C0: "call   0x4644a0",
    0x4644AD: "mov    esi,ecx",
    0x4644B5: "mov    DWORD PTR [esi],eax",
    0x4644C1: "jmp    DWORD PTR [eax*4+0x464b68]",
}

# Mode switch branches: address -> (width literal site, resolution).
MODE_BRANCH_WRITES = {
    0x4644C8: ("mov    DWORD PTR [esi+0x4],0x140", (320, 200)),
    0x4644DB: ("mov    DWORD PTR [esi+0x4],0x280", (640, 480)),
    0x4644EB: ("mov    DWORD PTR [esi+0x4],0x280", (640, 480)),
    0x464502: ("mov    DWORD PTR [esi+0x4],0x320", (800, 600)),
    0x464512: ("mov    DWORD PTR [esi+0x4],0x320", (800, 600)),
    0x464529: ("mov    DWORD PTR [esi+0x4],0x400", (1024, 768)),
    0x464539: ("mov    DWORD PTR [esi+0x4],0x400", (1024, 768)),
    0x464550: ("mov    DWORD PTR [esi+0x4],0x500", (1280, 1024)),
}

DIRECT_WRITERS = {
    0x431B79: "mov    DWORD PTR ds:0xe5bf1c,ebp",
    0x431B7F: "mov    DWORD PTR ds:0xe5bf20,edi",
    0x4324B8: "mov    DWORD PTR ds:0xe5bf1c,0x280",
    0x4324C2: "mov    DWORD PTR ds:0xe5bf20,0x1e0",
}

SLOT_Y_OFFSETS = (-0x1A, 0x08, 0x2A, 0x4C, 0x6E, 0x90, 0xB2)
SLOT_X_OFFSET = 0x14
SLOT_W = 0x118
SLOT_H = 0x18

INSN_RE = re.compile(r"^\s+([0-9a-f]{6}):\t(?:[0-9a-f]{2} )+\s*\t(.+?)\s*$", re.MULTILINE)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sections(data: bytes) -> dict[str, dict[str, int]]:
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    opt = pe + 24
    base = struct.unpack_from("<I", data, opt + 28)[0]
    table = opt + opt_size
    out: dict[str, dict[str, int]] = {}
    for index in range(count):
        entry = table + index * 40
        name = data[entry : entry + 8].rstrip(b"\0").decode("ascii")
        vsize, vaddr = struct.unpack_from("<II", data, entry + 8)
        out[name] = {"start": base + vaddr, "end": base + vaddr + vsize, "vsize": vsize}
    return out


def disasm(start: int, stop: int) -> str:
    return subprocess.run(
        [
            "objdump",
            "-d",
            "-Mintel",
            "-j",
            ".text",
            f"--start-address={start:#x}",
            f"--stop-address={stop:#x}",
            str(EXE),
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def instructions(text: str) -> dict[int, str]:
    return {int(addr, 16): insn for addr, insn in INSN_RE.findall(text)}


def check_anchors(
    found: dict[int, str], expected: dict[int, str], label: str, failures: list[str]
) -> dict[str, str]:
    resolved: dict[str, str] = {}
    for address, insn in expected.items():
        actual = found.get(address)
        resolved[f"0x{address:x}"] = actual or ""
        if actual != insn:
            failures.append(f"{label}: 0x{address:x} expected {insn!r}, found {actual!r}")
    return resolved


def halve_toward_zero(value: int) -> int:
    return -((-value) // 2) if value < 0 else value // 2


def origin_from_binary(screen: tuple[int, int], dialog: tuple[int, int]) -> tuple[int, int]:
    """Reproduce cdq/sub/sar/sub exactly as FUN_004D60B0 does."""
    return (
        halve_toward_zero(screen[0]) - halve_toward_zero(dialog[0]),
        halve_toward_zero(screen[1]) - halve_toward_zero(dialog[1]),
    )


def slots_for(origin: tuple[int, int]) -> list[tuple[int, int, int, int]]:
    left = origin[0] + SLOT_X_OFFSET
    return [
        (left, origin[1] + offset, left + SLOT_W, origin[1] + offset + SLOT_H)
        for offset in SLOT_Y_OFFSETS
    ]


def run_lap301_probe() -> tuple[int, str]:
    result = subprocess.run(
        ["python3", str(LAP301_PROBE)], capture_output=True, text=True
    )
    return result.returncode, sha256_bytes(result.stdout.encode())


def main() -> int:
    failures: list[str] = []
    report: dict[str, object] = {
        "probe": Path(__file__).name,
        "lap": 302,
        "role": "middle (diagnose/plan/confirm); no game code, no execution",
        "capture_comparison": False,
        "execution": False,
        "reviews": "lap301 repair of the save/load layout probe (handoff §11 T1~T4)",
    }

    for path in (EXE, SPRITE, LAP301_PROBE, LAP301_LOG, LAP299_LOG):
        if not path.is_file():
            failures.append(f"required read-only input missing: {path}")
    if failures:
        report["failures"] = failures
        print(json.dumps(report, indent=2, sort_keys=True))
        return 1

    exe_bytes = EXE.read_bytes()
    exe_sha = sha256_bytes(exe_bytes)
    sprite_bytes = SPRITE.read_bytes()
    sprite_sha = sha256_bytes(sprite_bytes)
    report["sha256"] = {
        "original_exe": exe_sha,
        "sprite": sprite_sha,
        "lap301_log_now": sha256_bytes(LAP301_LOG.read_bytes()),
        "lap299_log_now": sha256_bytes(LAP299_LOG.read_bytes()),
    }
    if exe_sha != EXPECTED_EXE_SHA:
        failures.append(f"original exe sha mismatch: {exe_sha}")
    if sprite_sha != EXPECTED_SPRITE_SHA:
        failures.append(f"sprite sha mismatch: {sprite_sha}")

    header = struct.unpack_from("<4I", sprite_bytes, 0)
    if header != (9, 320, 310, 1):
        failures.append(f"unexpected saveloadtitle.spr header: {header}")
    dialog = (header[1], header[2])

    # --- 1. image layout -------------------------------------------------
    secs = sections(exe_bytes)
    text = secs[".text"]
    data = secs[".data"]
    scanned = {"start": 0x401000, "end": 0x4E4AE5}
    report["image_layout"] = {
        "text": {"start": hex(text["start"]), "end": hex(text["end"])},
        "data": {"start": hex(data["start"]), "end": hex(data["end"]),
                 "virtual_size": hex(data["vsize"])},
        "lap301_scan_range": {k: hex(v) for k, v in scanned.items()},
        "lap301_scan_covers_whole_text": (
            text["start"] == scanned["start"] and text["end"] == scanned["end"]
        ),
        "globals_inside_data_virtual_extent": {
            hex(addr): data["start"] <= addr < data["end"]
            for addr in (GRAPHICS_OBJECT, SCREEN_W_GLOBAL, SCREEN_H_GLOBAL,
                         ORIGIN_X_GLOBAL, ORIGIN_Y_GLOBAL, 0x519A0C, 0xB3AD74)
        },
    }
    if text["start"] != scanned["start"] or text["end"] != scanned["end"]:
        failures.append(
            f"lap301 scan range {scanned} does not equal .text "
            f"[{text['start']:#x},{text['end']:#x})"
        )
    for addr in (GRAPHICS_OBJECT, SCREEN_W_GLOBAL, SCREEN_H_GLOBAL, ORIGIN_X_GLOBAL):
        if not data["start"] <= addr < data["end"]:
            failures.append(f"{addr:#x} is not inside .data virtual extent")

    whole = disasm(text["start"], text["end"])
    found = instructions(whole)

    # --- 2. direct writers (lap301's set) --------------------------------
    direct_pattern = re.compile(
        r"^\s+([0-9a-f]{6}):\t(?:[0-9a-f]{2} )+\s*\t"
        r"(mov +(?:DWORD|WORD|BYTE) PTR ds:0x(?:e5bf1c|e5bf20),.+?)\s*$",
        re.MULTILINE,
    )
    direct = {int(a, 16): i for a, i in direct_pattern.findall(whole)}
    report["direct_writers"] = {hex(a): i for a, i in sorted(direct.items())}
    if direct != DIRECT_WRITERS:
        failures.append(f"direct absolute writer set changed: {sorted(map(hex, direct))}")

    # --- 3. indirect writers (what lap301 could not see) ------------------
    report["indirect_write_path"] = check_anchors(
        found, INDIRECT_CHAIN_ANCHORS, "indirect chain", failures
    )
    mode_writes: dict[str, object] = {}
    for address, (insn, resolution) in MODE_BRANCH_WRITES.items():
        actual = found.get(address)
        mode_writes[hex(address)] = {"instruction": actual or "", "resolution": list(resolution)}
        if actual != insn:
            failures.append(f"mode branch 0x{address:x} expected {insn!r}, found {actual!r}")
    report["mode_table_writes"] = mode_writes

    # 800x600 must be materialised nowhere else in .text.
    sites_320 = sorted(a for a, i in found.items() if i.endswith(",0x320"))
    sites_258 = sorted(a for a, i in found.items() if i.endswith(",0x258"))
    report["resolution_800x600_sites"] = {
        "width_0x320": [hex(a) for a in sites_320],
        "height_0x258": [hex(a) for a in sites_258],
    }

    reachable = sorted({res for _, res in MODE_BRANCH_WRITES.values()})
    report["screen_global_writer_scope"] = {
        "direct_absolute_write_sites": len(direct),
        "indirect_this_relative_write_sites": 2 * len(MODE_BRANCH_WRITES),
        "lap301_enumeration_is_exhaustive": False,
        "reachable_mode_resolutions": [list(r) for r in reachable],
        "lap301_candidate_count": 2,
        "note": (
            "FUN_004644A0 writes [this+4]/[this+8]; with this=0xE5BF18 those are "
            "ds:0xE5BF1C/ds:0xE5BF20.  lap301 matched only absolute-addressed "
            "writes, so its count gate is fail-open for this path."
        ),
    }

    # --- 4. centre formula, pinned by address ----------------------------
    report["centre_formula_anchors"] = check_anchors(
        found, CENTRE_FORMULA_ANCHORS, "centre formula", failures
    )

    # --- 5. geometry for every reachable mode ----------------------------
    geometry: dict[str, object] = {}
    for screen in reachable:
        binary_origin = origin_from_binary(screen, dialog)
        lap301_origin = ((screen[0] - dialog[0]) // 2, (screen[1] - dialog[1]) // 2)
        rects = slots_for(binary_origin)
        inside = all(
            0 <= r[0] < r[2] <= screen[0] and 0 <= r[1] < r[3] <= screen[1] for r in rects
        )
        geometry[f"{screen[0]}x{screen[1]}"] = {
            "origin_binary_formula": list(binary_origin),
            "origin_lap301_formula": list(lap301_origin),
            "formulas_agree": binary_origin == lap301_origin,
            "slot_rects_inside_screen": inside,
            "slot0_xyxy": list(rects[0]),
            "slot6_xyxy": list(rects[-1]),
        }
        if binary_origin != lap301_origin:
            failures.append(
                f"centre formula mismatch at {screen}: binary {binary_origin} "
                f"vs lap301 {lap301_origin}"
            )
    report["geometry_all_reachable_modes"] = geometry
    report["modes_where_dialog_leaves_screen"] = [
        name for name, entry in geometry.items()
        if not entry["slot_rects_inside_screen"]  # type: ignore[index]
    ]

    # --- 6. determinism without creating a new stale self-pin ------------
    first_code, first_sha = run_lap301_probe()
    second_code, second_sha = run_lap301_probe()
    archived = sha256_bytes(LAP301_LOG.read_bytes())
    report["lap301_determinism"] = {
        "exit_codes": [first_code, second_code],
        "fresh_run_shas": [first_sha, second_sha],
        "two_fresh_runs_identical": first_sha == second_sha,
        "matches_archived_lap301_log": first_sha == archived,
        "archived_lap301_log_sha_recorded_in_lap301": RECORDED_LAP301_LOG_SHA,
        "archived_lap299_log_sha_recorded_in_lap299": RECORDED_LAP299_LOG_SHA,
        "assertion_policy": (
            "only the two-fresh-run comparison is asserted; the archived SHA is "
            "reported so a later repair of the lap301 probe cannot make this "
            "gate a permanent exit 1 (the W3 failure mode)"
        ),
    }
    if first_code != 0 or second_code != 0:
        failures.append(f"lap301 probe exit codes {first_code}/{second_code} are not 0")
    if first_sha != second_sha:
        failures.append("lap301 probe is not deterministic across two fresh runs")

    # --- 7. provenance facts ---------------------------------------------
    lap301_text = LAP301_PROBE.read_text()
    log_payload = json.loads(LAP301_LOG.read_text())
    report["provenance"] = {
        "lap299_log_preserved": sha256_bytes(LAP299_LOG.read_bytes()) == RECORDED_LAP299_LOG_SHA,
        "lap301_report_self_reported_lap": log_payload.get("lap"),
        "lap301_report_self_reported_probe": log_payload.get("probe"),
        "probe_source_lap_field": 'report["lap"] = 299 while the report lives in logs/lap301',
        "pre_repair_source_still_present": "SCREEN = (800, 600)" in lap301_text,
        "note": (
            "the repair edited the lap299 probe in place, so the source that "
            "produced logs/lap299 no longer exists anywhere in the tree"
        ),
    }

    report["limitations"] = [
        "static only: which resolution is live when FUN_004D60B0 builds the "
        "dialog is not decided here and needs an observation this probe does "
        "not authorise",
        "the mode argument reaching FUN_004644A0 is a runtime value threaded "
        "from 0x00423D4x; its stored source is not resolved here",
        "button callsites yield points, not hitbox extents; slot selection and "
        "the post-click load transition remain UNKNOWN",
        "no capture, no game, no Wine/Xvfb, no Stage B, no runtime budget",
    ]
    report["failures"] = failures
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
