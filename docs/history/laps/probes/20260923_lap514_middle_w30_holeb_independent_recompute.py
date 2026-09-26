#!/usr/bin/env python3
"""lap514 middle -- W30 안 B(lap512 source + lap513 24k soak) 독립 재계산. 읽기 전용.

work 산출물의 요약 필드(hole_hex/verdict)를 믿지 않고:
  R. samples.jsonl 의 window_hex 원시 바이트에서 +0x2016..+0x2018 를 다시 뽑아 위반을 센다.
  S. 원본 .text 전수 디스어셈블로 [0x200c,0x2010)·[0x2016,0x2018) 과 **겹치는** 모든 메모리
     피연산자를 찾는다(정확 disp 일치가 아니라 [disp, disp+size) 겹침; base+disp 와
     PlayerStruct 배열 절대주소 별칭 양쪽).
  P. 패처를 임시 복사본에 적용 -> diff 범위 -> 패치 사이트 역디스어셈블 -> 원복 SHA.
  C. 9개 used 읽기/쓰기 사이트 뒤 명령이 레지스터를 16-bit 로 소비하지 않는지(뒤따르는 명령 덤프).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

import capstone
from capstone import x86

REPO = Path(__file__).resolve().parents[4]
EXE = REPO / "Syw2plus/syw2plus_original.exe"
RUN = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/"
           "20260923_lap512_work_f4b_ledger_32bit_hole_b")
OUT = Path("/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/"
           "20260923_lap514_middle_w30_holeb_review/w30_holeb_independent_recompute.json")
ORIG_SHA = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
PS_BASE, STRIDE = 0x956770, 0x3ABC
TEXT_VA, TEXT_END = 0x401000, 0x401000 + 0xE3AE5
USED = (0x200C, 0x2010)
HOLE = (0x2016, 0x2018)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def overlaps(a: int, b: int, rng: tuple[int, int]) -> bool:
    return a < rng[1] and rng[0] < b


def runtime_recompute() -> dict:
    summary = json.loads((RUN / "run_summary.json").read_text())
    lines = (RUN / "samples.jsonl").read_text().splitlines()
    ticks, viol, nonzero_hole = [], 0, 0
    base = {}
    max_list_count = [0] * 8
    max_used = [0] * 8
    max_building = [0] * 8
    list_nonzero_words = 0
    for line in lines:
        s = json.loads(line)
        ticks.append(s["tick"])
        for o in s["owners"]:
            w = bytes.fromhex(o["window_hex"])
            assert len(w) == 0x110
            hole = w[0x16:0x18]
            k = o["owner"]
            base.setdefault(k, hole)
            viol += hole != base[k]
            nonzero_hole += hole != b"\0\0"
            lc = int.from_bytes(w[0x14:0x16], "little", signed=True)
            max_list_count[k] = max(max_list_count[k], lc)
            max_used[k] = max(max_used[k], int.from_bytes(w[0x0C:0x0E], "little", signed=True))
            max_building[k] = max(max_building[k], int.from_bytes(w[0x0E:0x10], "little", signed=True))
            list_nonzero_words += any(w[0x18:0x110])
            # 요약 필드와 원시가 일치하는지(work 필드 전사 검사)
            assert o["hole_hex"] == hole.hex()
            assert o["used"] == int.from_bytes(w[0x0C:0x0E], "little", signed=True)
    return dict(
        run_summary_sha=sha((RUN / "run_summary.json").read_bytes()),
        samples_sha=sha((RUN / "samples.jsonl").read_bytes()),
        sample_count=len(lines), owner_samples=len(lines) * 8,
        first_tick=ticks[0], final_tick=ticks[-1],
        ticks_monotonic=all(a <= b for a, b in zip(ticks, ticks[1:])),
        hole_violations_recomputed=viol, hole_nonzero_samples=nonzero_hole,
        baseline=[base[k].hex() for k in range(8)],
        max_list_count_2014=max_list_count, max_used=max_used, max_building=max_building,
        samples_with_nonzero_list_window=list_nonzero_words,
        summary_claims=dict(verdict=summary["verdict"], final_tick=summary["final_tick"],
                            sample_count=summary["sample_count"],
                            hole_violation_count=summary["hole_violation_count"],
                            exe_sha256=summary["exe_sha256"],
                            source_unchanged=summary["source_unchanged"]),
    )


def disasm(data: bytes):
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    md.skipdata = True
    code = data[TEXT_VA - 0x400000:TEXT_END - 0x400000]
    return list(md.disasm(code, TEXT_VA))


def mem_hits(insns) -> dict:
    hits = {"used": [], "hole": [], "abs_other_owner_used_or_hole": []}
    n = 0
    for ins in insns:
        if ins.id == 0:
            continue
        n += 1
        for op in ins.operands:
            if op.type != x86.X86_OP_MEM:
                continue
            disp = op.mem.disp & 0xFFFFFFFF
            size = op.size or 1
            rec = f"0x{ins.address:08x} {ins.mnemonic} {ins.op_str} (size {size})"
            if op.mem.base != 0 or op.mem.index != 0:
                for key, rng in (("used", USED), ("hole", HOLE)):
                    if overlaps(disp, disp + size, rng):
                        hits[key].append(rec)
            if PS_BASE <= disp < PS_BASE + 16 * STRIDE:
                rel = (disp - PS_BASE) % STRIDE
                for key, rng in (("used", USED), ("hole", HOLE)):
                    if overlaps(rel, rel + size, rng):
                        hits[key if disp < PS_BASE + STRIDE else
                             "abs_other_owner_used_or_hole"].append("ABS " + rec)
    return {"instruction_count": n, **hits}


def context_after(insns, vas, k=6) -> dict:
    idx = {ins.address: i for i, ins in enumerate(insns)}
    out = {}
    for va in vas:
        i = idx.get(va)
        out[f"0x{va:08x}"] = None if i is None else [
            f"0x{x.address:08x} {x.mnemonic} {x.op_str}" for x in insns[max(0, i - 3):i + k]]
    return out


def patch_check(orig: bytes) -> dict:
    spec = importlib.util.spec_from_file_location(
        "sl32", REPO / "patches/population/supply_ledger_32bit.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    with tempfile.TemporaryDirectory() as td:
        src, dst = Path(td) / "in.exe", Path(td) / "cand.exe"
        shutil.copyfile(EXE, src)
        cand_sha = m.create_copy(src, dst)
        cand = dst.read_bytes()
        diff = [i for i in range(len(orig)) if orig[i] != cand[i]]
        spans = [(va - 0x400000, va - 0x400000 + len(b)) for va, b, _ in m.EDITS]
        outside = [i for i in diff if not any(a <= i < b for a, b in spans)]
        md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
        redis = {}
        for va, before, after in m.EDITS:
            off = va - 0x400000
            redis[f"0x{va:08x}"] = [f"{x.mnemonic} {x.op_str}" for x in md.disasm(cand[off:off + len(after)], va)]
        restored = m.restore(dst)
        return dict(candidate_sha=cand_sha, diff_bytes=len(diff), diff_outside_sites=len(outside),
                    edits=len(m.EDITS), redisasm=redis, restored_sha=restored,
                    restored_equals_original=dst.read_bytes() == orig, input_untouched=sha(src.read_bytes()) == ORIG_SHA)


def main() -> int:
    orig = EXE.read_bytes()
    assert sha(orig) == ORIG_SHA
    insns = disasm(orig)
    res = {"source_sha_before": sha(orig)}
    res["runtime"] = runtime_recompute()
    res["static"] = mem_hits(insns)
    res["context"] = context_after(insns, [0x43EDFC, 0x43F0E9, 0x43F3B3, 0x43EE9B, 0x43EF8B,
                                           0x40DD12, 0x40E03B, 0x499767, 0x499A0E, 0x43F57F,
                                           0x43DB24, 0x43E204, 0x43EEAD, 0x43EF9D])
    res["patch"] = patch_check(orig)
    res["source_sha_after"] = sha(EXE.read_bytes())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(json.dumps(res, ensure_ascii=False, indent=1))
    print("OUT_SHA256", sha(OUT.read_bytes()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
