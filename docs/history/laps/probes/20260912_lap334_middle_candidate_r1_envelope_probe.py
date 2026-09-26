#!/usr/bin/env python3
"""lap334 middle probe — document-failure review and candidate R1 envelope basis.

Re-derives every claim of the lap334 middle envelope from primary sources only:
the STATUS file on disk, the lap332 preservation block, the original PE bytes,
the live harness source, the pinned dxwrapper profile, and the preserved lap148 /
lap154 candidate run records.  It imports no previous probe, runs no game, injects
no input or memory write, and asserts no SHA of its own output.
Prints a JSON report and exits non-zero on any failure.
"""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]

STATUS = REPO / "docs/STATUS.md"
# Two immutable archives: STATUS as it stood at the end of lap332 and of lap333.
# The live STATUS is deliberately NOT used here — lap334 and later laps rewrite it,
# and a probe that pinned the live file would become a permanently failing self-check.
PRESERVED_LAP332 = REPO / "docs/history/laps/20260912_status_lap332_compaction.md"
PRESERVED_LAP333 = REPO / "docs/history/laps/20260912_status_lap333_compaction.md"
ORIGINAL = REPO / "Syw2plus/syw2plus_original.exe"
HARNESS = REPO / "tools/runtime_env.py"
DXCONFIG = REPO / "patches/resolution/dxwrapper_config.py"
LAP332_PROBE = REPO / "docs/history/laps/probes/20260912_lap332_middle_lap331_r1_artifact_probe.py"
LAP148 = REPO / "docs/history/laps/20260911_lap148_luna_g1_config_2x_block.md"
LAP154 = REPO / "docs/history/laps/20260911_lap154_luna_g1_dxwrapper_install_finalization_block.md"

ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
# Harness SHA reviewed and accepted at lap330; unchanged through lap331..lap333.
LAP330_HARNESS_SHA = "997ff15b13115ccebd9d8832b3b066add589b755d9cc6e8a77d987696cc46eed"
# STATUS body at the end of lap332 (preserved by lap333 before its aborted 131-line edit)
# and at the end of lap333 (preserved by lap334 before this lap's edit).
STATUS_AFTER_LAP332_SHA = "ec10aaec102e9ea918a8d3cf72e5cfcc1061b6c852dc75a66989f6e78982cbbf"
STATUS_AFTER_LAP333_SHA = "b2d2c230c907d0e34629cdd2e188013ee41d49d680aa2be2b45597f617ee1e5d"
# The only lines lap333 rewrote: four "다음 한 가지" lines, one blocker headline, one lap row.
EXPECTED_CHANGED_LINES = [20, 21, 22, 23, 25, 128]

failures: list[str] = []


def check(condition: bool, message: str) -> bool:
    if not condition:
        failures.append(message)
    return condition


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


class PE:
    """Minimal PE VA->file-offset mapper (raw bytes only, no disassembler)."""

    def __init__(self, data: bytes) -> None:
        self.data = data
        e = struct.unpack_from("<I", data, 0x3C)[0]
        if data[e : e + 4] != b"PE\0\0":
            raise ValueError("not a PE image")
        sections = struct.unpack_from("<H", data, e + 6)[0]
        opt_size = struct.unpack_from("<H", data, e + 20)[0]
        self.image_base = struct.unpack_from("<I", data, e + 24 + 28)[0]
        table = e + 24 + opt_size
        self.sections = [
            struct.unpack_from("<IIII", data, table + 40 * i + 8) for i in range(sections)
        ]

    def offset(self, va: int) -> int:
        rva = va - self.image_base
        for virtual_size, virtual_address, raw_size, raw_pointer in self.sections:
            if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
                return raw_pointer + (rva - virtual_address)
        raise ValueError(f"unmapped VA {va:#x}")

    def read(self, va: int, size: int) -> bytes:
        start = self.offset(va)
        return self.data[start : start + size]


def status_contract() -> dict[str, Any]:
    """A. The STATUS actually on disk honours the loop/PROMPT.md document contract."""
    text = STATUS.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = [line for line in lines if line.startswith("## ")]
    blockers = [line for line in lines if line == "## 지금 막힌 것 (Blockers)"]
    check(len(lines) <= 130, f"STATUS exceeds the 130-line limit: {len(lines)}")
    check(len(blockers) == 1, f"STATUS must hold exactly one blockers section: {len(blockers)}")
    check(text.endswith("\n"), "STATUS must end with a newline")
    # The live STATUS hash is deliberately NOT reported: this probe's stdout would
    # then change with every later lap's STATUS edit, making its recorded SHA useless.
    # The reviewed STATUS hash is recorded in the lap334 documents instead.
    return {
        "line_count": len(lines),
        "headings": headings,
        "blocker_sections": len(blockers),
    }


def _fenced_status(path: Path) -> tuple[str, list[str]] | None:
    """Return the STATUS body preserved inside a compaction archive."""
    match = re.search(r"```markdown\n(.*)\n```\n*$", path.read_text(encoding="utf-8"), re.S)
    if not check(match is not None, f"preserved STATUS fenced block is missing: {path.name}"):
        return None
    body = match.group(1) + "\n"  # type: ignore[union-attr]
    return body, body.splitlines()


def preservation_contract() -> dict[str, Any]:
    """B. lap333 preserved the pre-edit original and rewrote only the handoff lines.

    Both sides are immutable archives, so this verdict stays reproducible after
    later laps rewrite the live STATUS.
    """
    before = _fenced_status(PRESERVED_LAP332)
    after = _fenced_status(PRESERVED_LAP333)
    if before is None or after is None:
        return {"available": False}
    before_body, before_lines = before
    after_body, after_lines = after
    check(sha256_bytes(before_body.encode("utf-8")) == STATUS_AFTER_LAP332_SHA,
          "end-of-lap332 STATUS body does not match the SHA recorded by lap333")
    check(sha256_bytes(after_body.encode("utf-8")) == STATUS_AFTER_LAP333_SHA,
          "end-of-lap333 STATUS body does not match the SHA recorded by lap334")
    check(len(before_lines) == 130, f"end-of-lap332 STATUS is not 130 lines: {len(before_lines)}")
    check(len(after_lines) == 130, f"end-of-lap333 STATUS is not 130 lines: {len(after_lines)}")
    check(sum(1 for line in after_lines if line == "## 지금 막힌 것 (Blockers)") == 1,
          "end-of-lap333 STATUS does not hold exactly one blockers section")
    changed = (
        [i for i, (a, b) in enumerate(zip(before_lines, after_lines)) if a != b]
        if len(before_lines) == len(after_lines)
        else None
    )
    check(changed == EXPECTED_CHANGED_LINES,
          f"lap333 changed unexpected STATUS lines: {changed}")
    return {
        "status_after_lap332_sha256": sha256_bytes(before_body.encode("utf-8")),
        "status_after_lap333_sha256": sha256_bytes(after_body.encode("utf-8")),
        "line_counts": [len(before_lines), len(after_lines)],
        "changed_line_indices": changed,
        "archive_sha256": [sha256(PRESERVED_LAP332), sha256(PRESERVED_LAP333)],
    }


def c1_dispatcher() -> dict[str, Any]:
    """C. Correction C1 re-derived from the original bytes without a disassembler."""
    data = ORIGINAL.read_bytes()
    check(sha256_bytes(data) == ORIGINAL_SHA, "original executable SHA256 drifted")
    pe = PE(data)
    head = pe.read(0x004233B8, 39)
    expected = bytes.fromhex(
        "0fbf0518d84e00"      # movsx eax, word ptr [0x4ED818]
        "83f828"              # cmp  eax, 0x28
        "0f8f57010000"        # jg   0x42351F
        "0f8447010000"        # je   0x423515
        "48"                  # dec  eax
        "83f822"              # cmp  eax, 0x22
        "0f87f0feffff"        # ja   0x4232C8
        "ff248538374200"      # jmp  dword ptr [eax*4 + 0x423738]
    )
    check(head == expected, "dispatcher prologue bytes do not match the C1 claim")
    jg_target = 0x004233C8 + struct.unpack_from("<i", head, 12)[0]
    je_target = 0x004233CE + struct.unpack_from("<i", head, 18)[0]
    ja_target = 0x004233D8 + struct.unpack_from("<i", head, 28)[0]
    table = struct.unpack_from("<I", head, 35)[0]
    check(jg_target == 0x0042351F, f"jg target is not 0x42351F: {jg_target:#x}")
    check(je_target == 0x00423515, f"je target is not 0x423515: {je_target:#x}")
    check(ja_target == 0x004232C8, f"ja target is not 0x4232C8: {ja_target:#x}")
    check(table == 0x00423738, f"jump table base is not 0x423738: {table:#x}")
    # PS==35 still lands on table entry 34 (index PS-1), so C1 changes no verdict.
    entry35 = struct.unpack_from("<I", pe.read(0x00423738 + 4 * 34, 4), 0)[0]
    check(entry35 == 0x0042341B, f"PS35 table entry is not 0x42341B: {entry35:#x}")
    return {
        "bytes": head.hex(),
        "jg_target": hex(jg_target),
        "je_target": hex(je_target),
        "ja_target": hex(ja_target),
        "table": hex(table),
        "ps35_entry": hex(entry35),
    }


def harness_facts() -> dict[str, Any]:
    """D/E. What the live harness does today for the original and candidate paths."""
    source = HARNESS.read_text(encoding="utf-8")
    harness_sha = sha256_bytes(source.encode("utf-8"))
    check(harness_sha == LAP330_HARNESS_SHA,
          "runtime_env.py drifted from the lap330-reviewed harness SHA")
    facts = {
        "r1_forces_builtin_ddraw": 'WINEDLLOVERRIDES="ddraw=b"' in source,
        "r1_requires_800x600_content": (
            '"R1 game content crop is not exactly 800x600"' in source
        ),
        "r1_click_is_unscaled": (
            "root_x, root_y = content_crop[0] + G1_R1_CLICK_POINT[0], "
            "content_crop[1] + G1_R1_CLICK_POINT[1]" in source
        ),
        "r1_click_point_is_296_505": "G1_R1_CLICK_POINT: tuple[int, int] = (296, 505)" in source,
        "r1_artifact_name": '"r1_load_origin.json"' in source,
        "trace_allows_1600x1200_content": "allowed_sizes=((800, 600), (1600, 1200))" in source,
        "trace_click_is_unscaled": (
            'str(content_crop[0] + x), str(content_crop[1] + y)]' in source
        ),
        "trace_asserts_private_ddraw_loaded": (
            '"dxwrapper 2x run did not load private game/ddraw.dll"' in source
        ),
        "trace_override_is_native_then_builtin": (
            'override = "ddraw=n,b" if dxwrapper_2x else "ddraw=b"' in source
        ),
        "prepare_hashes_wrapper_dlls": (
            '"dxwrapper.dll", "ddraw.dll", "syw2x.dll"' in source
        ),
        "r1_cleanup_is_terminate_kill_not_wm_close": (
            "child.terminate()" in source and "child.kill()" in source
        ),
    }
    for name, value in sorted(facts.items()):
        check(value, f"harness fact not found in runtime_env.py: {name}")
    dx = DXCONFIG.read_text(encoding="utf-8")
    pins = {
        "source_pin": 'SOURCE_SHA256 = "918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2"'
        in dx,
        "candidate_pin": 'CANDIDATE_SHA256 = "f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785"'
        in dx,
        "install_private": "def install_private(" in dx,
        "uninstall_private": "def uninstall_private(" in dx,
    }
    for name, value in sorted(pins.items()):
        check(value, f"dxwrapper profile fact not found: {name}")
    return {
        "runtime_env_sha256": harness_sha,
        "dxwrapper_config_sha256": sha256(DXCONFIG),
        "facts": facts,
        "pins": pins,
    }


def exactly_once_scope() -> dict[str, Any]:
    """F. The original exact-once assertion and the artifact name it owns."""
    probe = LAP332_PROBE.read_text(encoding="utf-8")
    check('REPO.glob("local/runtime/*/output/r1_load_origin.json")' in probe,
          "lap332 probe no longer globs the original R1 artifact name")
    runs = sorted(str(p.relative_to(REPO)) for p in
                  REPO.glob("local/runtime/*/output/r1_load_origin.json"))
    check(len(runs) == 1, f"original R1 exactly-once no longer holds: {len(runs)} artifacts")
    candidates = sorted(str(p.relative_to(REPO)) for p in
                        REPO.glob("local/runtime/*/output/r1_load_origin_candidate.json"))
    check(not candidates, f"candidate R1 artifacts already exist before approval: {candidates}")
    return {
        "lap332_probe_sha256": sha256(LAP332_PROBE),
        "original_artifacts": runs,
        "candidate_artifacts": candidates,
    }


def candidate_transform_evidence() -> dict[str, Any]:
    """G. Two preserved candidate runs already discriminate the input transform."""
    lap148 = LAP148.read_text(encoding="utf-8")
    lap154 = LAP154.read_text(encoding="utf-8")
    scaled_fail = (
        "client 1600×1200 (2.0×2.0) PASS, but one scaled menu click left state PS9/tick0"
        in lap148
    )
    unscaled_pass = (
        "client `[1600,1200]`, scale `[2,2]`, unscaled `(184,560)`, PS9→PS7→PS3" in lap154
    )
    check(scaled_fail, "lap148 record no longer shows the scaled-click failure")
    check(unscaled_pass, "lap154 record no longer shows the unscaled-click PS3 pass")
    check("f0ce9e64" in lap154 and "918e7043" in lap154,
          "lap154 record no longer pins the candidate and restore ini SHAs")
    return {
        "lap148_sha256": sha256(LAP148),
        "lap154_sha256": sha256(LAP154),
        "scaled_click_failed": scaled_fail,
        "unscaled_click_reached_ps3": unscaled_pass,
    }


def main() -> int:
    report: dict[str, Any] = {
        "probe": "lap334 middle — document failure review and candidate R1 envelope basis",
        "status_contract": status_contract(),
        "preservation_contract": preservation_contract(),
        "c1_dispatcher": c1_dispatcher(),
        "harness_facts": harness_facts(),
        "exactly_once_scope": exactly_once_scope(),
        "candidate_transform_evidence": candidate_transform_evidence(),
        "not_claimed": [
            "no candidate run was executed; this probe proves no runtime behaviour",
            "no product G1 evidence, no Stage B permission, no milestone movement",
            "PS register-store fail-open (33 sites) and indirect writers stay open",
            "the live STATUS is only checked against its generic contract, not pinned",
        ],
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
