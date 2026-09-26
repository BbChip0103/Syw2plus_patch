#!/usr/bin/env python3
"""lap572 strategy 읽기 전용 probe: F4(B) 15곳 편집이 G2 후보 a10024de 위에 그대로 얹히는가.

파일을 쓰지 않는다. 원본을 읽어 메모리에서만 a10024de 후보를 재생성하고,
F4 EDITS 의 old bytes 가 후보에서도 같은지, 후보 diff 범위와 겹치는지 본다.
사전 고정 단언: A1 원본 SHA 일치, A2 후보 재생성 SHA == a10024de, A3 F4 15곳 old bytes 전부 후보에 존재,
A4 후보 diff 와 F4 편집 범위 겹침 0, A5 원본 적용 F4 SHA == 1893ff50 재현.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from patches.population import supply_ledger_32bit as f4  # noqa: E402
from patches.population.g2_full_capacity_persistence_compat_v1 import build_candidate  # noqa: E402

ORIGINAL = ROOT.parent / "Syw2plus" / "syw2plus_original.exe"
EXPECTED_CANDIDATE = "a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68"
EXPECTED_F4_ONLY = "1893ff508f5ef662e91e9500531108aaab680bab62866e324fe6fb517f353ae1"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def diff_offsets(a: bytes, b: bytes) -> set[int]:
    return {i for i in range(min(len(a), len(b))) if a[i] != b[i]} | set(range(min(len(a), len(b)), max(len(a), len(b))))


def main() -> int:
    original = ORIGINAL.read_bytes()
    candidate, _ = build_candidate(original, 4001)
    cand_diff = diff_offsets(original, candidate)
    sites = []
    combined = bytearray(candidate)
    for va, before, after in f4.EDITS:
        off = va - f4.IMAGE_BASE
        span = set(range(off, off + len(before)))
        present = candidate[off : off + len(before)] == before
        overlap = sorted(span & cand_diff)
        sites.append({"va": f"0x{va:08x}", "old_present": present, "overlap": len(overlap)})
        if present:
            combined[off : off + len(after)] = after
    f4_only = f4.patched_bytes(original)
    asserts = {
        "A1_original_sha": sha(original) == f4.ORIGINAL_SHA256,
        "A2_candidate_sha": sha(candidate) == EXPECTED_CANDIDATE,
        "A3_all_old_present": all(s["old_present"] for s in sites),
        "A4_no_overlap": all(s["overlap"] == 0 for s in sites),
        "A5_f4_only_sha": sha(f4_only) == EXPECTED_F4_ONLY,
    }
    report = {
        "original_sha": sha(original),
        "candidate_sha": sha(candidate),
        "candidate_diff_bytes": len(cand_diff),
        "f4_sites": len(sites),
        "sites": sites,
        "combined_in_memory_sha": sha(bytes(combined)) if asserts["A3_all_old_present"] else None,
        "asserts": asserts,
    }
    print(json.dumps(report, indent=1))
    return 0 if all(asserts.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
