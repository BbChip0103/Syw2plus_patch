#!/usr/bin/env python3
"""lap332 middle probe — independent review of the lap331 R1 artifact.

Re-derives every claim from primary sources only: the preserved run artifact,
the run's own game copy (original PE bytes and the sprite header), and the live
harness file. It imports no previous probe, re-runs nothing, and injects no
memory write or input. Prints a JSON report and exits non-zero on any failure.
"""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
RUN = REPO / "local/runtime/20260912_172722_2210599_0"
ARTIFACT = RUN / "output/r1_load_origin.json"
ORIGINAL_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"

# SHA values as written by lap331 (record) and lap330 (reviewed harness).
LAP331_ARTIFACT_SHA = "76ce7788c9567784a5f82ae52ba77d3a8281e28839b1aa0413689e19bfa442cf"
LAP331_LOG_SHA = "277fe226c55c0241b98adb1791280383986a46f33d8406bc34e9039a072f2453"
LAP331_MANIFEST_SHA = "4109704a9863c818299cab5185b3ac683545e0854d69d183ebc88495d18096a2"
LAP330_HARNESS_SHA = "997ff15b13115ccebd9d8832b3b066add589b755d9cc6e8a77d987696cc46eed"
LAP330_TEST_SHA = "81acc11eab97cc04b797724360a81561a227c8454571290782f611aa936cac72"

failures: list[str] = []


def check(condition: bool, message: str) -> bool:
    if not condition:
        failures.append(message)
    return condition


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        for virtual_size, virtual_addr, raw_size, raw_off in self.sections:
            if virtual_addr <= rva < virtual_addr + max(virtual_size, raw_size):
                if rva - virtual_addr >= raw_size:
                    raise ValueError(f"{va:#x} lies in uninitialised (BSS) space")
                return raw_off + (rva - virtual_addr)
        raise ValueError(f"{va:#x} is outside every section")

    def read(self, va: int, size: int) -> bytes:
        start = self.offset(va)
        return self.data[start : start + size]

    def rel32(self, operand_va: int) -> int:
        return operand_va + 4 + struct.unpack_from("<i", self.data, self.offset(operand_va))[0]


def report_artifact_integrity(evidence: dict[str, Any]) -> dict[str, Any]:
    observed = {
        "artifact": sha256(ARTIFACT),
        "log": sha256(RUN / "output/r1_load_origin.log"),
        "manifest": sha256(RUN / "manifest.json"),
        "harness": sha256(REPO / "tools/runtime_env.py"),
        "test": sha256(REPO / "tests/test_lap326_r1_load_origin.py"),
    }
    check(observed["artifact"] == LAP331_ARTIFACT_SHA, "artifact SHA differs from the lap331 record")
    check(observed["log"] == LAP331_LOG_SHA, "run log SHA differs from the lap331 record")
    check(observed["manifest"] == LAP331_MANIFEST_SHA, "manifest SHA differs from the lap331 record")
    check(observed["harness"] == LAP330_HARNESS_SHA, "live harness SHA differs from the reviewed SHA")
    check(observed["test"] == LAP330_TEST_SHA, "live R1 test SHA differs from the reviewed SHA")

    provenance = evidence["provenance"]
    check(
        provenance["harness_sha256"]["tools/runtime_env.py"] == LAP330_HARNESS_SHA,
        "artifact provenance names a harness SHA other than the reviewed one",
    )
    check(
        provenance["original_exe_sha256"]
        == provenance["expected_original_exe_sha256"]
        == ORIGINAL_SHA,
        "artifact provenance original EXE SHA is not the pinned original",
    )
    check(provenance["observational_only"] is True, "artifact does not declare itself observational")

    runs = sorted(p for p in REPO.glob("local/runtime/*/output/r1_load_origin.json"))
    check(len(runs) == 1, f"exactly-once violated: {len(runs)} r1_load_origin.json artifacts exist")
    pngs = sorted(p.name for p in (RUN / "output").glob("*.png"))
    check(not pngs, f"R1 lane produced forbidden screenshots: {pngs}")
    return {"sha256": observed, "artifact_count": len(runs), "png_count": len(pngs)}


def report_envelope_compliance(evidence: dict[str, Any]) -> dict[str, Any]:
    check(evidence["screen"] == "1600x1200x24", "screen is not the fixed 1600x1200x24")
    check(0 < evidence["timeout_seconds"] <= 90, "timeout is outside the 1..90s envelope")
    check(
        evidence["elapsed_seconds"] <= evidence["timeout_seconds"],
        "elapsed exceeds the declared timeout",
    )
    check(evidence["input"]["count"] == 1, "input count is not exactly 1")
    check(evidence["input"]["focus_exit"] == 0, "window focus did not exit 0")
    check(evidence["input"]["inject_exit"] == 0, "click injection did not exit 0")
    check(evidence["fixture"]["synthetic"] is False, "fixture is synthetic")
    check(evidence["fixture"]["memory_writes"] is False, "fixture declares memory writes")
    check(evidence["fixture"]["resource_grant"] is False, "fixture declares a resource grant")
    check(
        evidence["manifest"]["diagnostic_bridge_overridden"] is False,
        "a diagnostic bridge was overridden for this run",
    )

    window = evidence["window"]
    root = (int(window["root"]["width"]), int(window["root"]["height"]))
    content = (int(window["content_child"]["width"]), int(window["content_child"]["height"]))
    check(root == (1600, 1200), f"root window is {root}, not 1600x1200")
    check(content == (800, 600), f"content child is {content}, not 800x600")

    crop = window["content_crop"]
    expected_root = [crop["x"] + evidence["input"]["client"][0], crop["y"] + evidence["input"]["client"][1]]
    check(
        evidence["input"]["root"] == expected_root,
        "root click coordinate is not content_crop + client (lap326 §3 transform)",
    )

    cleanup = evidence["cleanup"]
    for key in ("owned_launchers_stopped", "xvfb_stopped", "ok"):
        check(cleanup[key] is True, f"cleanup.{key} is not true")
    check(cleanup["global_kill_used"] is False, "cleanup used a global kill")
    check(not cleanup["prefix_processes_after"], "prefix processes survived cleanup")
    check(cleanup["error"] is None, "cleanup recorded an error")
    return {
        "root": root,
        "content": content,
        "click_root": evidence["input"]["root"],
        "elapsed_seconds": evidence["elapsed_seconds"],
    }


def report_mode_and_series(evidence: dict[str, Any]) -> dict[str, Any]:
    check(evidence["status"] == "OBSERVED", "status is not OBSERVED")
    check(
        evidence["classification"] == "REACHED_CHANGED",
        "classification is not REACHED_CHANGED",
    )
    check("error" not in evidence, "an OBSERVED artifact must not carry an error field")
    check("reason" not in evidence, "an OBSERVED artifact must not carry a failure reason")
    check(
        evidence["precondition"]["pass"] is True
        and evidence["precondition"]["observed_origin"] == [0, 0, 0],
        "lap326 §5 (P1) precondition (PS9 origin == (0,0,0)) did not hold",
    )

    wait_states = evidence["wait_ps_states"]
    check(wait_states == [9, 35], "declared wait states are not (9, 35) — lap328 N6 closure")
    check(evidence["ps_word"] == {"pre": 9, "post": 35}, "ps_word pre/post are not 9/35")
    check(evidence["ps_dword"] == {"pre": 9, "post": 35}, "ps_dword pre/post are not 9/35")

    series = evidence["pending_state"]
    torn = [s for s in series if s["ps_word"] != s["ps_dword"]]
    check(not torn, f"{len(torn)} samples disagree between the WORD and DWORD reads")
    elapsed = [s["elapsed_seconds"] for s in series]
    check(elapsed == sorted(elapsed), "pending_state series is not monotone in elapsed time")

    pre_click = [s for s in series if s["pending_state"] == 0]
    post_click = [s for s in series if s["pending_state"] != 0]
    check(
        bool(post_click) and all(s["pending_state"] == 34 for s in post_click),
        "post-click pending_state is not the single value 34",
    )
    check(
        series.index(post_click[0]) > series.index(pre_click[-1]) if post_click and pre_click else False,
        "pending_state 0 and 34 samples are interleaved",
    )
    check(
        series[-1]["ps_word"] == 35 and series[-1]["pending_state"] == 34,
        "final sample is not PS=35 with pending_state=34",
    )
    observed_ps = sorted({s["ps_word"] for s in series})
    return {
        "samples": len(series),
        "observed_ps_values": observed_ps,
        "pending_transition": [pre_click[-1]["pending_state"], post_click[0]["pending_state"]],
        "out_of_table_ps": [v for v in observed_ps if v < 1 or v > 35],
    }


def report_dispatcher(pe: PE, observed_ps: list[int]) -> dict[str, Any]:
    """Re-derive the PS dispatcher, including the >35 ladder lap326 §1 omitted."""

    check(
        pe.read(0x4233B8, 7) == bytes.fromhex("0fbf0518d84e00"),
        "0x4233B8 is not `movsx eax, WORD ds:0x4ED818`",
    )
    check(pe.read(0x4233BF, 3) == bytes.fromhex("83f828"), "0x4233BF is not `cmp eax, 0x28`")
    check(pe.read(0x4233C2, 2) == bytes.fromhex("0f8f"), "0x4233C2 is not a `jg` rel32")
    check(pe.read(0x4233C8, 2) == bytes.fromhex("0f84"), "0x4233C8 is not a `je` rel32")
    check(pe.read(0x4233CE, 4) == bytes.fromhex("4883f822"), "0x4233CE is not `dec eax; cmp eax,0x22`")
    check(pe.read(0x4233D2, 2) == bytes.fromhex("0f87"), "0x4233D2 is not a `ja` rel32")
    check(
        pe.read(0x4233D8, 7) == bytes.fromhex("ff248538374200"),
        "0x4233D8 is not `jmp DWORD PTR [eax*4+0x423738]`",
    )
    ladder = {
        "gt_40_arm": pe.rel32(0x4233C4),
        "eq_40_arm": pe.rel32(0x4233CA),
        "default_arm": pe.rel32(0x4233D4),
    }
    check(
        pe.read(ladder["gt_40_arm"], 5) == bytes.fromhex("3d31010000"),
        "the PS>40 arm does not continue with `cmp eax, 0x131`",
    )

    table = [struct.unpack_from("<I", pe.data, pe.offset(0x423738) + 4 * i)[0] for i in range(35)]
    check(table[8] == 0x423407, "jump table PS=9 entry is not 0x423407")
    check(table[33] == 0x423411, "jump table PS=34 entry is not 0x423411")
    check(table[34] == 0x42341B, "jump table PS=35 entry is not 0x42341B")

    # PS=35 is inside the table domain: not >40, not ==40, and (35-1) <= 0x22.
    check(35 <= 0x28 and 35 != 0x28 and (35 - 1) <= 0x22, "PS=35 does not reach the jump table")

    # The observed out-of-table values are legitimate dispatcher inputs, not torn reads.
    unexplained = [v for v in observed_ps if not (1 <= v <= 35 or v == 0x28 or v > 0x28)]
    check(not unexplained, f"observed PS values with no dispatcher arm: {unexplained}")

    chain = {
        0x423411: "e8ca140000",  # PS=34 arm: call 0x4248E0
        0x4A2FF5: "e9460cffff",  # tail jmp 0x493C40 (the edge lap324 missed)
        0x493C40: "6a08",  # push 8  -> origin tag
        0x4D632A: "66890d5c8b0801",  # mov WORD ds:0x1088B5C, cx   (x)
        0x4D6348: "66893d5e8b0801",  # mov WORD ds:0x1088B5E, di   (y)
        0x4D6A23: "66a3608b0801",  # mov WORD ds:0x1088B60, ax   (tag)
        0x4248E5: "66c70518d84e002300",  # mov WORD ds:0x4ED818, 35 (PS := 35, last)
    }
    for va, expected in chain.items():
        check(
            pe.read(va, len(expected) // 2).hex() == expected,
            f"chain byte mismatch at {va:#x}",
        )
    check(pe.rel32(0x423412) == 0x4248E0, "the PS=34 arm does not call 0x4248E0")
    check(pe.rel32(0x4A2FF6) == 0x493C40, "0x4A2FF5 does not tail-jump to 0x493C40")
    check(pe.rel32(0x493C43) == 0x4D6A00, "0x493C42 does not call 0x4D6A00")
    return {"ladder": {k: hex(v) for k, v in ladder.items()}, "table_entries": len(table)}


def report_origin(pe: PE, evidence: dict[str, Any]) -> dict[str, Any]:
    """Confirm candidate A from the run's own sprite, not from a past record."""

    sprite = RUN / "game/yfnt/saveloadtitle.spr"
    tag, width, height, frames = struct.unpack_from("<4I", sprite.read_bytes(), 0)
    check((tag, frames) == (9, 1), f"sprite header shape is {(tag, frames)}, not (9, 1)")
    predicted = [(800 - width) // 2, (600 - height) // 2]
    observed = [evidence["post"]["origin"]["x"], evidence["post"]["origin"]["y"]]
    check(
        observed == predicted,
        f"post origin {observed} does not equal candidate A {predicted}",
    )
    check(
        predicted != [(640 - width) // 2, (640 - height) // 2],
        "candidates A and B are indistinguishable for this sprite",
    )
    check(evidence["origin_tag"] == {"pre": 0, "post": 8}, "origin tag did not go 0 -> 8")
    check(
        evidence["post"]["origin"]["tag"] == struct.unpack_from("<b", pe.read(0x493C41, 1))[0],
        "observed tag does not equal the `push 8` immediate on the PS=34 entry path",
    )
    check(
        evidence["observation"] == {"pre": [0, 0, 0], "post": observed + [8]},
        "the comparator observation does not match the pre/post samples",
    )
    return {
        "sprite_sha256": sha256(sprite),
        "sprite_header": [tag, width, height, frames],
        "candidate_a": predicted,
        "candidate_b": [(640 - width) // 2, (480 - height) // 2],
        "observed": observed + [evidence["post"]["origin"]["tag"]],
    }


def main() -> int:
    evidence = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    pe = PE((RUN / "game/syw2plus_original.exe").read_bytes())
    check(
        hashlib.sha256(pe.data).hexdigest() == ORIGINAL_SHA,
        "the run's game EXE is not the pinned original",
    )
    integrity = report_artifact_integrity(evidence)
    envelope = report_envelope_compliance(evidence)
    series = report_mode_and_series(evidence)
    dispatcher = report_dispatcher(pe, series["observed_ps_values"])
    origin = report_origin(pe, evidence)
    report = {
        "lap": 332,
        "role": "middle",
        "reviews": "lap331 R1 artifact (no re-run, no input, no memory write)",
        "integrity": integrity,
        "envelope": envelope,
        "series": series,
        "dispatcher": dispatcher,
        "origin": origin,
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
