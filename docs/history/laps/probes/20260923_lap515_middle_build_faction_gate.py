#!/usr/bin/env python3
"""lap515 middle — AI 건설 후보 진영 블록 / 건물 개수 한도 정적 확인 (읽기 전용).

트랙②(2026-09-23 12:55 사용자 지시 "27종 중 18종을 AI가 왜 안 짓는지")의 첫 판별이다.
원본 EXE를 **읽기만** 한다. 바이너리/메모리 쓰기 0, 게임 실행 0.
런타임 값(type_spec cost/typemax, fixture nation)은 lap507 W29 원시 산출물을 SHA로 고정해 읽는다.

사전 고정 단언(데이터 개봉 전에 이 파일에 적은 것):
  A1 원본 SHA256 = b56986e0….
  A2 `FUN_0043DBB0` 로스터 순회 jump table: kind 7→`+0x314C`, 21→`+0x3154`, 70→`+0x3158`(조건부
     `FUN_004076C0(0x41,0x40)||(0x41,1)`), 75→`+0x3150`, 7..75의 나머지 kind 전부 기본(무동작).
  A3 블록 바이트 쓰기(`+0x33B0 + kind`)가 네 건물 종 집합으로 해독된다(참고 저장소 표와 대조).
  A4 생산표 `0x4EC514`(stride 0x12, sentinel 0xFFFE) 143행 → 생산 건물 27종, 네 블록으로 서로소 분할.
  A5 lap508 N151 합집합 {41,44,45,46,47,49,50,51,105} == 조선 블록 ∩ 생산 건물, 미건설 18종은
     전부 타 진영 블록(18/18 FACTION_BLOCK).
  A6 fixture(lap507 samples.jsonl) 전 표본 8 owner 전원 nation==1.
  A7 진영별 유닛 천장 Σ(typemax_default×cost) — 조선 2,835(N151 수치 재현)·일본·명 전부 < 5,000,
     전 65종 합 8,077(lap507 이론최대 재현).
  A8 `FUN_0043DB00`: override 0·ai==1이면 `+0x200E >= +0x2010/5`에서 전 건물 거부, typemax 비교 없음.
  A9 `FUN_0043DBB0` 건물 종별 한도 = typemax×N/6 (+typemax if N%12) — 고정 typemax 상한이 아니다.

사용법:
    python3 docs/history/laps/probes/20260923_lap515_middle_build_faction_gate.py

exit 0 = 모든 단언 통과. exit 1 = 단언 실패(사실이 바뀐 것이므로 카드를 다시 읽는다).
프로세스 exit 0 자체는 제품 검증이 아니다.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import sys

import capstone

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
ORIGINAL_EXE = REPO_ROOT / "Syw2plus" / "syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
IMAGE_BASE = 0x400000

SHARED_TEMP = REPO_ROOT.parent / "temp" / "Syw2plus_patch" / "g2_capacity"
W29_DIR = SHARED_TEMP / "20260923_lap506_w29_used_ceiling"
W29_INPUTS = {
    "type_specs.json": None,
    "samples.jsonl": None,
}
OUT_DIR = SHARED_TEMP / "20260923_lap515_middle_build_faction_gate"

EXPECTED_BLOCKS = {
    "JOSEON_7@0x314c": set(range(40, 53)) | {105},
    "MING_21@0x3154": {66, 68, 69, 70, 73},
    "MING_70@0x3158": {64, 65, 67, 71, 72, 74, 107},
    "JAPAN_75@0x3150": set(range(53, 64)) | {106},
}
N151_UNION = {41, 44, 45, 46, 47, 49, 50, 51, 105}
N151_UNBUILT = {53, 54, 55, 56, 58, 59, 60, 61, 64, 65, 67, 68, 70, 71, 72, 74, 106, 107}

FAILURES: list[str] = []


def check(cond: bool, label: str) -> None:
    print(("PASS " if cond else "FAIL ") + label)
    if not cond:
        FAILURES.append(label)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def va(addr: int) -> int:
    return addr - IMAGE_BASE


def disasm(exe: bytes, start: int, end: int) -> list:
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    return list(md.disasm(exe[va(start):va(end)], start))


def decode_blocks(exe: bytes) -> dict[str, set[int]]:
    """0x43DCBE..0x43DDDD: 플래그 비교 뒤 `mov byte [esi+0x33B0+kind]` 묶음을 블록별로 모은다."""
    blocks: dict[str, set[int]] = {}
    current = None
    names = {0x314C: "JOSEON_7@0x314c", 0x3154: "MING_21@0x3154",
             0x3158: "MING_70@0x3158", 0x3150: "JAPAN_75@0x3150"}
    for ins in disasm(exe, 0x43DCBE, 0x43DDDD):
        text = f"{ins.mnemonic} {ins.op_str}"
        if ins.address == 0x43DCBE:
            current = names[0x314C]  # mov ecx,[ebx]; ebx = esi+0x314C (0x43DBCD)
        for disp, name in names.items():
            if text.startswith("cmp dword ptr [esi + ") and f"0x{disp:x}]" in text:
                current = name
        if ins.mnemonic == "mov" and text.startswith("mov byte ptr [esi + 0x3"):
            disp = int(ins.op_str.split("+ ")[1].split("]")[0], 16)
            blocks.setdefault(current, set()).add(disp - 0x33B0)
    return blocks


def decode_jump_table(exe: bytes) -> dict[int, int]:
    targets = [struct.unpack_from("<I", exe, va(0x43E084) + 4 * k)[0] for k in range(5)]
    index = exe[va(0x43E098):va(0x43E098) + 0x45]  # cmp ecx,0x44 → 69 entries, kind-7
    return {k + 7: targets[c] for k, c in enumerate(index)}


def parse_production_table(exe: bytes) -> list[tuple[int, int]]:
    rows, off = [], va(0x4EC514)
    while struct.unpack_from("<h", exe, off)[0] != -2:
        words = struct.unpack_from("<9h", exe, off)
        if words[2] != -1:
            rows.append((words[1], words[2]))  # (building, produce_kind)
        off += 0x12
    return rows


def instr_at(exe: bytes, addr: int) -> str:
    ins = disasm(exe, addr, addr + 16)[0]
    return f"{ins.mnemonic} {ins.op_str}"


def main() -> int:
    exe = ORIGINAL_EXE.read_bytes()
    check(sha256_bytes(exe) == ORIGINAL_SHA256, "A1 original SHA256")

    jt = decode_jump_table(exe)
    special = {k: t for k, t in jt.items() if t != 0x43DCB0}
    check(special == {7: 0x43DC62, 21: 0x43DC6A, 70: 0x43DC76, 75: 0x43DCA6},
          f"A2 jump table special kinds {sorted(special)}")
    check(instr_at(exe, 0x43DC62) == "mov dword ptr [ebx], 1"
          and instr_at(exe, 0x43DBCD) == "lea ebx, [esi + 0x314c]", "A2 kind7 -> +0x314C")
    check(instr_at(exe, 0x43DC7C) == "push 0x40" and instr_at(exe, 0x43DC7E) == "push 0x41"
          and instr_at(exe, 0x43DC82) == "call 0x4076c0"
          and instr_at(exe, 0x43DC8B) == "push 1", "A2 kind70 conditional FUN_004076C0(0x41,0x40|1)")

    blocks = decode_blocks(exe)
    check(blocks == EXPECTED_BLOCKS, "A3 block byte writes decode to four faction sets")

    prod = parse_production_table(exe)
    producers = {b for b, _ in prod}
    check(len(prod) == 65 and len(producers) == 27, f"A4 production rows {len(prod)} producers {len(producers)}")
    owner_of = {}
    for name, kinds in blocks.items():
        for b in producers & kinds:
            owner_of.setdefault(b, []).append(name)
    check(all(len(v) == 1 for v in owner_of.values()) and set(owner_of) == producers,
          "A4 27 producers partition disjointly into faction blocks")
    joseon_producers = producers & blocks["JOSEON_7@0x314c"]
    check(joseon_producers == N151_UNION, "A5 N151 union == Joseon producers")
    unbuilt = producers - joseon_producers
    check(unbuilt == N151_UNBUILT, "A5 18 unbuilt == non-Joseon producers")
    unbuilt_class = {b: owner_of[b][0] for b in sorted(unbuilt)}

    inputs = {}
    for fname in W29_INPUTS:
        data = (W29_DIR / fname).read_bytes()
        inputs[fname] = sha256_bytes(data)
    nations = set()
    n_samples = 0
    for line in (W29_DIR / "samples.jsonl").read_text().splitlines():
        rec = json.loads(line)
        n_samples += 1
        nations |= {o["nation"] for o in rec["owners"]}
    check(nations == {1}, f"A6 fixture nations over {n_samples} samples = {sorted(nations)}")

    ts = json.loads((W29_DIR / "type_specs.json").read_text())
    kinds_of: dict[int, set[int]] = {}
    for b, k in prod:
        kinds_of.setdefault(b, set()).add(k)

    def ceiling(builds: set[int]) -> int:
        kinds = set().union(*(kinds_of[b] for b in builds if b in kinds_of))
        return sum(ts[str(k)]["typemax_default"] * ts[str(k)]["cost"] for k in kinds)

    faction_ceiling = {
        "JOSEON(7)": ceiling(blocks["JOSEON_7@0x314c"]),
        "JAPAN(75)": ceiling(blocks["JAPAN_75@0x3150"]),
        "MING(21+70)": ceiling(blocks["MING_21@0x3154"] | blocks["MING_70@0x3158"]),
        "MING(21 only)": ceiling(blocks["MING_21@0x3154"]),
        "ALL_65": ceiling(producers),
    }
    check(faction_ceiling["JOSEON(7)"] == 2835, "A7 Joseon ceiling reproduces N151 2,835")
    check(faction_ceiling["ALL_65"] == 8077, "A7 all-65 ceiling reproduces lap507 8,077")
    check(all(v < 5000 for k, v in faction_ceiling.items() if k != "ALL_65"),
          f"A7 every single-faction unit ceiling < 5000 {faction_ceiling}")

    db00 = [f"{i.mnemonic} {i.op_str}" for i in disasm(exe, 0x43DB00, 0x43DBAD)]
    check("cmp word ptr [0x9e1dd8], 0" in db00 and "cmp byte ptr [esi + 2], 1" in db00
          and "movsx ecx, word ptr [esi + 0x2010]" in db00 and "mov eax, 0x66666667" in db00
          and "movsx ecx, word ptr [esi + 0x200e]" in db00, "A8 DB00 building gate +0x200e >= +0x2010/5")
    check(not any("0x9b525c" in t or "0x89a388" in t for t in db00), "A8 DB00 has no typemax check")

    lim = [f"{i.mnemonic} {i.op_str}" for i in disasm(exe, 0x43DF3E, 0x43DF94)]
    check(lim[:1] == ["mov bx, word ptr [eax + 0x9b525c]"] and "mov eax, 0x2aaaaaab" in lim
          and "mov edi, 0xc" in lim and "add ecx, ebx" in lim
          and "cmp ax, cx" in lim, "A9 building per-kind limit typemax*N/6 (+typemax if N%12)")
    check(instr_at(exe, 0x43DF0E) == "test byte ptr [eax + 0x9b5274], 2",
          "A9 +0x4C bit 0x2 = AI-buildable flag test")
    buildable = {b: bool(ts[str(b)]["crowd_flat_flag"] & 2) for b in sorted(producers)}
    check(all(buildable.values()), "A9 all 27 producers carry +0x4C bit 0x2")

    def building_limit(typemax: int, n: int) -> int:
        return typemax * n // 6 + (typemax if n % 12 else 0)

    joseon_buildings = sorted(blocks["JOSEON_7@0x314c"])
    bcost = {b: ts[str(b)]["cost"] for b in joseon_buildings}
    need = 5000 - faction_ceiling["JOSEON(7)"]
    mean_cost = sum(bcost.values()) / len(bcost)
    result = {
        "schema": "lap515_build_faction_gate/v1",
        "original_sha256": ORIGINAL_SHA256,
        "w29_input_sha256": inputs,
        "fixture_samples": n_samples,
        "fixture_nations": sorted(nations),
        "blocks": {k: sorted(v) for k, v in blocks.items()},
        "producers": sorted(producers),
        "unbuilt_18_classification": unbuilt_class,
        "faction_unit_ceiling": faction_ceiling,
        "joseon_building_cost": bcost,
        "building_gate_max_buildings_at_count_cap_1200": 1200 // 5,
        "building_limit_examples_typemax1": {n: building_limit(1, n) for n in (1, 6, 10, 12, 13, 60)},
        "joseon_building_supply_needed_for_5000": need,
        "joseon_mean_building_cost": round(mean_cost, 3),
        "joseon_buildings_needed_at_mean_cost": -(-need * len(bcost) // sum(bcost.values())),
        "joseon_building_supply_hard_upper": (1200 // 5) * max(bcost.values()),
        "failures": FAILURES,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "build_faction_gate.json"
    payload = json.dumps(result, indent=1, sort_keys=True, default=str).encode()
    out.write_bytes(payload)
    print(f"output {out} sha256 {sha256_bytes(payload)}")
    print(json.dumps({k: result[k] for k in ("faction_unit_ceiling", "joseon_building_supply_needed_for_5000",
                                              "joseon_buildings_needed_at_mean_cost",
                                              "joseon_building_supply_hard_upper")}, default=str))
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
