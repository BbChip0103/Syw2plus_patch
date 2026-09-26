#!/usr/bin/env python3
"""lap509 middle — `+0x200c`(전비 장부 used) 전수 사이트 인벤토리 / 읽기 전용.

F4(B) 32-bit 확장 카드(W30)의 범위를 바이트로 확정하기 위한 정적 probe다.
원본 EXE를 **읽기만** 한다. 바이너리/메모리 쓰기 0, 게임 실행 0.

검증 대상 (STATUS lap508 시점의 카드 범위 서술을 독립 확인):
  - writer 2곳 `0x43EE9B`(add) / `0x43EF8B`(sub)
  - reader 3곳 `0x43EE03` / `0x43F0F3` / `0x43F43F` 가 정말 `+0x200c` 읽기인가
  - `+0x200c` 를 만지는 명령이 정말 5곳뿐인가 (절대주소 별칭 형태 포함)

사용법:
    python3 docs/history/laps/probes/20260923_lap509_middle_supply_ledger_site_inventory.py

exit 0 = 모든 사전 고정 단언 통과. exit 1 = 단언 실패(사실이 바뀐 것이므로 카드를 다시 읽는다).
프로세스 exit 0 자체는 제품 검증이 아니다.
"""

from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import struct
import sys

import capstone
from capstone.x86 import X86_OP_MEM

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
ORIGINAL_EXE = REPO_ROOT / "Syw2plus" / "syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
ORIGINAL_SIZE = 1_032_192

IMAGE_BASE = 0x400000
PS_BASE = 0x956770          # PlayerStruct[0]
PS_STRIDE = 0x3ABC
PS_COUNT = 8

# PlayerStruct 전비/개수 필드 (analysis/memory_maps/player_offsets.md)
FIELDS = {
    0x200A: "count(+200a)",
    0x200C: "USED(+200c)",
    0x200E: "building(+200e)",
    0x2010: "unitcap(+2010)",
    0x2012: "limit(+2012)",
}


def sha256_of(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_original() -> bytes:
    if not ORIGINAL_EXE.is_file():
        raise SystemExit(f"원본 EXE를 찾을 수 없다: {ORIGINAL_EXE}")
    data = ORIGINAL_EXE.read_bytes()
    actual = sha256_of(ORIGINAL_EXE)
    if actual != ORIGINAL_SHA256 or len(data) != ORIGINAL_SIZE:
        raise SystemExit(
            "원본 fingerprint 불일치 — 다른 바이너리다. "
            f"sha256={actual} size={len(data)}"
        )
    return data


def text_section(data: bytes) -> tuple[int, int, int]:
    """(.text VA, file offset, size) 를 PE 섹션 테이블에서 직접 읽는다."""
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    nsec = struct.unpack_from("<H", data, pe + 6)[0]
    opt_size = struct.unpack_from("<H", data, pe + 20)[0]
    for index in range(nsec):
        off = pe + 24 + opt_size + index * 40
        name = data[off : off + 8].rstrip(b"\0").decode("ascii", "replace")
        vsize, vaddr, _rsize, raw = struct.unpack_from("<IIII", data, off + 8)
        if name == ".text":
            return IMAGE_BASE + vaddr, raw, vsize
    raise SystemExit(".text 섹션을 찾지 못했다")


def sweep(code: bytes, base_va: int) -> dict[int, capstone.CsInsn]:
    """선형 스윕 + 정지 지점 1바이트 전진 재시작으로 .text 전체를 덮는다."""
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    found: dict[int, capstone.CsInsn] = {}
    pos = 0
    size = len(code)
    while pos < size:
        advanced = False
        for insn in md.disasm(code[pos:], base_va + pos):
            found[insn.address] = insn
            advanced = True
            pos = insn.address - base_va + insn.size
        if not advanced:
            pos += 1

    # 스윕이 지나친(디코드 안 된) 바이트에서도 한 번씩 시도한다.
    covered = set()
    for addr, insn in found.items():
        covered.update(range(addr, addr + insn.size))
    for va in range(base_va, base_va + size):
        if va in covered:
            continue
        for insn in md.disasm(code[va - base_va : va - base_va + 16], va):
            found.setdefault(insn.address, insn)
            break
    return found


def collect(insns: dict[int, capstone.CsInsn]) -> dict[str, list[dict]]:
    """필드별로 (a) base+disp 형태와 (b) PlayerStruct[0] 절대주소 형태를 모두 모은다."""
    absolute = {PS_BASE + off: label for off, label in FIELDS.items()}
    hits: dict[str, list[dict]] = collections.defaultdict(list)
    for addr in sorted(insns):
        insn = insns[addr]
        for op in insn.operands:
            if op.type != X86_OP_MEM:
                continue
            disp = op.mem.disp
            entry = {
                "va": f"0x{addr:08x}",
                "text": f"{insn.mnemonic} {insn.op_str}",
                "bytes": insn.bytes.hex(),
            }
            if disp in FIELDS:
                hits[f"disp {FIELDS[disp]}"].append(dict(entry, form="base+disp"))
            unsigned = disp & 0xFFFFFFFF
            if unsigned in absolute:
                hits[f"abs {absolute[unsigned]}"].append(dict(entry, form="absolute"))
    return hits


def bulk_blob(data: bytes) -> dict:
    """bulk save/load 가 쓰는 고정 길이 raw span 을 push 즉시값에서 읽는다."""
    save_len_off = 0x440F02 - IMAGE_BASE
    save_ptr_off = 0x440F07 - IMAGE_BASE
    load_len_off = 0x4412D2 - IMAGE_BASE
    load_ptr_off = 0x4412D7 - IMAGE_BASE
    out = {}
    for label, len_off, ptr_off in (
        ("save@0x440f02", save_len_off, save_ptr_off),
        ("load@0x4412d2", load_len_off, load_ptr_off),
    ):
        if data[len_off] != 0x68 or data[ptr_off] != 0x68:
            raise SystemExit(f"{label}: push 즉시값 형태가 아니다 — 주소 전제가 깨졌다")
        length = struct.unpack_from("<I", data, len_off + 1)[0]
        start = struct.unpack_from("<I", data, ptr_off + 1)[0]
        out[label] = {"start": f"0x{start:08x}", "length": length,
                      "end": f"0x{start + length:08x}"}
    return out


def main() -> int:
    data = read_original()
    text_va, text_off, text_size = text_section(data)
    insns = sweep(data[text_off : text_off + text_size], text_va)
    hits = collect(insns)
    blob = bulk_blob(data)

    ps_end = PS_BASE + PS_STRIDE * PS_COUNT
    blob_start = int(blob["save@0x440f02"]["start"], 16)
    blob_end = int(blob["save@0x440f02"]["end"], 16)

    report = {
        "source": {
            "path": str(ORIGINAL_EXE),
            "sha256": ORIGINAL_SHA256,
            "size": len(data),
            "text_va": f"0x{text_va:08x}",
            "text_size": text_size,
            "decoded_instructions": len(insns),
        },
        "player_struct": {
            "base": f"0x{PS_BASE:08x}",
            "stride": f"0x{PS_STRIDE:04x}",
            "count": PS_COUNT,
            "end": f"0x{ps_end:08x}",
        },
        "bulk_blob": blob,
        "bulk_blob_contains_player_struct": blob_start <= PS_BASE and ps_end <= blob_end,
        "sites": {key: hits[key] for key in sorted(hits)},
        "site_counts": {key: len(hits[key]) for key in sorted(hits)},
    }

    def vas(key: str) -> list[str]:
        return [entry["va"] for entry in hits.get(key, [])]

    used_disp = vas("disp USED(+200c)")
    used_abs = vas("abs USED(+200c)")
    limit_disp = vas("disp limit(+2012)")

    # 사전 고정 단언 — 카드 W30 §1 이 의존하는 사실들
    checks = {
        # (1) `+0x200c` base+disp 사이트는 정확히 5곳이고 그 목록이 이것뿐이다.
        "used_disp_sites_exact": used_disp == [
            "0x0043edfc", "0x0043ee9b", "0x0043ef8b", "0x0043f0e9", "0x0043f3b3",
        ],
        # (2) writer 2곳은 STATUS 서술대로다.
        "writers_confirm_status": ("0x0043ee9b" in used_disp) and ("0x0043ef8b" in used_disp),
        # (3) STATUS 가 `+0x200c` reader 로 적은 3곳은 사실 `+0x2012`(limit) reader 다.
        "status_named_readers_are_limit": all(
            va in limit_disp for va in ("0x0043ee03", "0x0043f0f3", "0x0043f43f")
        ),
        "status_named_readers_not_used": not any(
            va in used_disp for va in ("0x0043ee03", "0x0043f0f3", "0x0043f43f")
        ),
        # (4) 절대주소 별칭 형태의 `+0x200c` reader 가 4곳 더 있다.
        "used_abs_sites_exact": used_abs == [
            "0x0040dd12", "0x0040e03b", "0x00499767", "0x00499a0e",
        ],
        # (5) bulk save/load 는 같은 고정 span 을 raw 로 읽고 쓴다.
        "bulk_save_load_same_span": (
            blob["save@0x440f02"] == blob["load@0x4412d2"]
        ),
        # (6) 그 span 안에 PlayerStruct 배열 전체가 들어 있다.
        "bulk_contains_player_struct": report["bulk_blob_contains_player_struct"],
    }
    report["checks"] = checks
    report["total_used_sites"] = len(used_disp) + len(used_abs)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        print(f"\nFAILED ASSERTIONS: {failed}", file=sys.stderr)
        return 1
    print(
        f"\nALL CHECKS PASS — `+0x200c` 총 사이트 {report['total_used_sites']}곳"
        f"(base+disp {len(used_disp)} + 절대주소 {len(used_abs)})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
