#!/usr/bin/env python3
"""lap517 middle — W31(lap516 work) 독립 검수: M-0 바이트 재확인 + M-2 원시 비참조 재집계 (읽기 전용).

원본 EXE와 lap516 원시 `samples.jsonl`을 **읽기만** 한다. 바이너리/메모리 쓰기 0, 게임 실행 0.
lap516의 `build_pace_summary.json`·`run_summary.json`은 재집계에 쓰지 않는다(비교 대상 숫자는
lap516 문서 §2.1/§2.2 표를 이 파일에 옮겨 적은 값이다).

사전 고정 단언(데이터 개봉 전에 이 파일에 적은 것):
  A1 원본 SHA256 = b56986e0….
  A2 `0x43E0F3`: `movsx eax,[edi+0xD34]; dec eax; cmp eax,3; ja 0x43E7C9; jmp [eax*4+0x43E7D8]`,
     table = [0x43E113,0x43E174,0x43E2FD,0x43E5A0] (lap516 §1.3 주장).
     [사후 정정, 1차 실행 exit1 원인] 1차 단언은 명령 목록 완전 일치를 요구해 실패했다 — 실제 바이트는
     `dec eax`/`cmp eax,3` 뒤에 무관한 스택 저장 `mov [esp+0x2c],ebp`·`mov [esp+0x28],ebp`가 끼어 있고,
     범위 끝도 0x43E113을 넘었다. 판정 명령의 순서·피연산자는 그대로이므로 단언을 "스택 저장 제외 후
     일치, 범위 [0x43E0F3,0x43E113)"로 고친다(A2). 원래 실패는 lap517 기록에 남긴다.
  A3 `FUN_0043F5A0` = +0xD36/+0xD3A/+0xD3E/+0xD42/+0xD46 dword 0, +0xD32·+0xD34 word 0, ret
     (lap516 §1.4 주장 — 단 +0xD32도 지운다는 점을 함께 확인).
  A4 [검수 쟁점] 외곽 실행 switch `0x43FB62`의 selector는 **+0xD32**이고 `cmp eax,0x1a`(27칸)이다.
     lap516 §1.1/§1.2의 "0x43FD60 = 20칸, +0xD34 = 현재 오더 ID"는 이 단언이 참이면 기각된다.
  A5 table `0x43FD60`[1] = 0x43FBBD, 그 본문이 `call 0x43E0E0`(건설 = 오더 종류 1).
  A6 [재무장 스케줄러] `0x43F5D0`: +0xD32 != 0이면 선택 생략(현 오더 실행), ==0이면 `rand%20`으로
     table `0x43FD10`(20칸) 분기. 건설 case는 정확히 1칸(index 2 → 0x43F871)이며
     `|tick - [+0x33AC]| > 0x64`일 때만 [+0x33AC]=tick, +0xD32=1, +0xD34=1을 쓴다.
  A7 [호출 케이던스] `0x43F5D0`의 호출자는 `0x41CBE5` 1곳뿐이고, 직전에 `tick & 7`로 owner 하나를
     고른다(PlayerStruct base 0x956770 + (tick&7)*0x3ABC) ⇒ owner당 8 tick에 1회.
  A8 `FUN_0043F5A0` 호출자 수 ≥ 20이고 `0x43E7C4`(건설 명령 발부 `call 0x4AF650` 직후)를 포함 ⇒
     "실패 시 리셋"이 아니라 성공·실패 공통 오더 종료.
  A9 `.text` 안 disp32 0x00000D34 원시 바이트 패턴 수 = 41 (lap516 §1.2 주장).
  B1 samples.jsonl SHA256 = 9fa10737…, 1,439줄, 표본 간 tick 간격 최대 ≤ 20(카드 §2 M-1).
  B2 +0xD34 상태 비율(표본 수 기준 또는 tick 가중 중 하나)이 lap516 §2.1 표와 owner별 |Δ| ≤ 0.3pp
     (s0/s2/s3/기타).
  B3 +0xD34 == 1 표본 0건, == 4 표본 0건 (8 owner 전원).
  B4 건물 수 시작→끝이 lap516 §2.2와 일치, `+0x200E` 감소 사건 0건.
  B5 후보 마스크 활성 종 수 평균이 lap516 §2.2와 |Δ| ≤ 0.05, `mask_active_count == len(kinds)` 전 표본.
  B6 owner별 max used = [1708,1035,1583,1536,1513,1070,1406,1376].
  B7 [관찰, 단언 아님] +0xD34 값 집합(0..4 외)과 A6/정적 즉치값 집합의 교집합을 기록.
  B8 [관찰, 단언 아님] 카드 §3 외삽식(조선 건물 보급 2,165 ≈ 160채, FG §4)과 lap516이 실제 쓴 식
     ((5000-used)/13.57 × tick/건물)을 둘 다 계산해 기록한다.

사용법:
    python3 docs/history/laps/probes/20260923_lap517_middle_w31_independent_review.py

exit 0 = 모든 단언 통과. exit 1 = 단언 실패. A4가 실패하면 lap516 §1.2 해석이 옳은 것이다.
프로세스 exit 0 자체는 제품 검증이 아니다.
"""

from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import statistics
import struct
import sys

import capstone
import pefile

WORKSPACE = pathlib.Path(__file__).resolve().parents[5]
ORIGINAL_EXE = WORKSPACE / "Syw2plus_re" / "Syw2plus" / "syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
IMAGE_BASE = 0x400000

SHARED_TEMP = WORKSPACE / "temp" / "Syw2plus_patch" / "g2_capacity"
LAP516_DIR = SHARED_TEMP / "20260923_lap516_work_w31_build_pace"
SAMPLES_SHA256 = "9fa1073709c4048895dc2b0495a5332f089b5b20c14f72c8904a48a081808355"
OUT_DIR = SHARED_TEMP / "20260923_lap517_middle_w31_review"

# lap516 문서 §2.1 (s0, s2, s3, 기타) %
LAP516_STATE = {
    0: (87.6, 3.3, 1.7, 7.5), 1: (86.9, 3.1, 0.7, 9.3), 2: (87.0, 2.5, 1.1, 9.4),
    3: (87.9, 3.4, 0.7, 8.0), 4: (86.3, 3.4, 0.8, 9.6), 5: (87.3, 3.4, 0.6, 8.7),
    6: (85.6, 2.9, 0.7, 10.9), 7: (87.4, 3.3, 0.5, 8.8),
}
# lap516 문서 §2.2 (시작, 끝, 마스크 평균)
LAP516_BUILD = {
    0: (1, 17, 11.0), 1: (1, 14, 9.6), 2: (1, 16, 11.0), 3: (1, 15, 11.0),
    4: (1, 15, 11.2), 5: (1, 10, 10.9), 6: (1, 15, 10.8), 7: (1, 19, 11.5),
}
LAP516_MAX_USED = [1708, 1035, 1583, 1536, 1513, 1070, 1406, 1376]
JOSEON_BUILDINGS_NEEDED = 160  # 카드 §3 건물 보급 2,165 ≈ 160채 (FG §4)

MD = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)


class Image:
    def __init__(self, raw: bytes):
        self.pe = pefile.PE(data=raw)
        text = next(s for s in self.pe.sections if s.Name.startswith(b".text"))
        self.text = text.get_data()
        self.text_va = IMAGE_BASE + text.VirtualAddress

    def read(self, va: int, n: int) -> bytes:
        return self.pe.get_data(va - IMAGE_BASE, n)

    def dis(self, va: int, end: int) -> list[str]:
        return [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(self.read(va, end - va), va)]

    def dwords(self, va: int, n: int) -> list[int]:
        return list(struct.unpack(f"<{n}I", self.read(va, n * 4)))

    def callers(self, target: int) -> list[int]:
        out, tb = [], self.text
        for i in range(len(tb) - 5):
            if tb[i] == 0xE8:
                rel = struct.unpack_from("<i", tb, i + 1)[0]
                if (self.text_va + i + 5 + rel) & 0xFFFFFFFF == target:
                    out.append(self.text_va + i)
        return out


def static_checks(img: Image) -> dict:
    r: dict = {}
    dispatch = [s for s in img.dis(0x43E0F3, 0x43E113) if not s.startswith("mov dword ptr [esp + ")]
    r["A2_interleaved_stack_stores"] = len(img.dis(0x43E0F3, 0x43E113)) - len(dispatch)
    r["A2"] = dispatch == [
        "movsx eax, word ptr [edi + 0xd34]", "dec eax", "cmp eax, 3", "ja 0x43e7c9",
        "jmp dword ptr [eax*4 + 0x43e7d8]",
    ] and img.dwords(0x43E7D8, 4) == [0x43E113, 0x43E174, 0x43E2FD, 0x43E5A0]
    r["A3"] = img.dis(0x43F5A0, 0x43F5CF) == [
        "xor eax, eax", "mov dword ptr [ecx + 0xd36], eax", "mov dword ptr [ecx + 0xd3a], eax",
        "mov dword ptr [ecx + 0xd3e], eax", "mov dword ptr [ecx + 0xd42], eax",
        "mov dword ptr [ecx + 0xd46], eax", "mov word ptr [ecx + 0xd32], ax",
        "mov word ptr [ecx + 0xd34], ax", "ret",
    ]
    r["A4"] = img.dis(0x43FB62, 0x43FB79) == [
        "movsx eax, word ptr [esi + 0xd32]", "cmp eax, 0x1a", "ja 0x43fcee",
        "jmp dword ptr [eax*4 + 0x43fd60]",
    ]
    exec_table = img.dwords(0x43FD60, 27)
    r["exec_table_0x43fd60"] = [hex(x) for x in exec_table]
    r["A5"] = exec_table[1] == 0x43FBBD and img.dis(0x43FBBD, 0x43FBC4) == [
        "mov ecx, esi", "call 0x43e0e0"]
    sel_table = img.dwords(0x43FD10, 20)
    r["select_table_0x43fd10"] = [hex(x) for x in sel_table]
    build_cases = [i for i, x in enumerate(sel_table) if x == 0x43F871]
    r["select_build_cases"] = build_cases
    r["A6"] = (
        build_cases == [2]
        and img.dis(0x43F7C8, 0x43F7E8) == [
            "cmp word ptr [esi + 0xd32], di", "jne 0x43fb62", "movsx eax, dx", "cmp eax, 0x13",
            "ja 0x43fb50", "jmp dword ptr [eax*4 + 0x43fd10]"]
        and "mov edi, 0x14" in img.dis(0x43F7A8, 0x43F7BC)
        and img.dis(0x43F871, 0x43F8A7) == [
            "mov ebp, dword ptr [esi + 0x33ac]", "mov eax, ecx", "sub eax, ebp", "cdq",
            "xor eax, edx", "sub eax, edx", "cmp eax, 0x64", "jle 0x43fb62", "mov eax, 1",
            "mov dword ptr [esi + 0x33ac], ecx", "mov word ptr [esi + 0xd32], ax",
            "mov word ptr [esi + 0xd34], ax", "jmp 0x43fb62"]
    )
    sched_callers = img.callers(0x43F5D0)
    r["scheduler_callers"] = [hex(x) for x in sched_callers]
    r["A7"] = sched_callers == [0x41CBE5] and img.dis(0x41CBC6, 0x41CBEA) == [
        "mov eax, dword ptr [0x8924b8]", "and eax, 7", "lea ecx, [eax + eax*2]", "shl ecx, 4",
        "sub ecx, eax", "lea edx, [ecx + ecx*4]", "shl edx, 4", "sub edx, eax",
        "lea ecx, [edx*4 + 0x956770]", "call 0x43f5d0"]
    # (((t*3)<<4)-t)*5<<4)-t)*4 == t*0x3ABC 확인
    r["A7_stride_ok"] = all(((((((t * 3) << 4) - t) * 5) << 4) - t) * 4 == t * 0x3ABC for t in range(8))
    reset_callers = img.callers(0x43F5A0)
    r["reset_callers_count"] = len(reset_callers)
    r["A8"] = (len(reset_callers) >= 20 and 0x43E7C4 in reset_callers
               and img.dis(0x43E7BA, 0x43E7C9) == ["call 0x4af650", "add esp, 0x14",
                                                    "mov ecx, edi", "call 0x43f5a0"])
    pat = struct.pack("<I", 0xD34)
    n, i = 0, img.text.find(pat)
    while i != -1:
        n, i = n + 1, img.text.find(pat, i + 1)
    r["disp_0xd34_raw_count"] = n
    r["A9"] = n == 41
    # 정적 즉치값: 스케줄러가 +0xD34에 쓰는 상수(di=0 경로 제외)
    imms = set()
    for ins in MD.disasm(img.read(0x43F7E8, 0x43FB62 - 0x43F7E8), 0x43F7E8):
        if ins.mnemonic == "mov" and "[esi + 0xd34]" in ins.op_str:
            src = ins.op_str.split(",")[1].strip()
            if src not in ("ax", "di"):
                imms.add(int(src, 0))
    r["scheduler_d34_immediates"] = sorted(imms)
    return r


def runtime_checks() -> dict:
    path = LAP516_DIR / "samples.jsonl"
    raw = path.read_bytes()
    r: dict = {"samples_sha256": hashlib.sha256(raw).hexdigest()}
    rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    ticks = [row["tick"] for row in rows]
    gaps = [b - a for a, b in zip(ticks, ticks[1:])]
    r.update(n=len(rows), tick_first=ticks[0], tick_last=ticks[-1], gap_max=max(gaps),
             gap_mean=round(statistics.mean(gaps), 3))
    r["B1"] = r["samples_sha256"] == SAMPLES_SHA256 and len(rows) == 1439 and max(gaps) <= 20

    per = {}
    b2 = b3 = b4 = b5 = True
    other_values: collections.Counter = collections.Counter()
    for o in range(8):
        st = [row["owners"][o]["build_state"] for row in rows]
        bc = [row["owners"][o]["building_count"] for row in rows]
        used = [row["owners"][o]["used"] for row in rows]
        ext = [row["build_ext"][o] for row in rows]
        n = len(st)
        cnt = collections.Counter(st)
        tw = collections.Counter()
        for s, g in zip(st, gaps):  # 표본 i의 상태가 다음 표본까지 유지된다고 가중
            tw[s] += g
        ttot = sum(gaps)

        def pct(c, tot, keyset):
            return round(100.0 * sum(v for k, v in c.items() if k in keyset) / tot, 2)

        others = {k for k in cnt if k not in (0, 1, 2, 3, 4)}
        other_values.update({k: v for k, v in cnt.items() if k in others})
        by_count = [pct(cnt, n, {0}), pct(cnt, n, {2}), pct(cnt, n, {3}), pct(cnt, n, others)]
        by_tick = [pct(tw, ttot, {0}), pct(tw, ttot, {2}), pct(tw, ttot, {3}), pct(tw, ttot, others)]
        ok_c = all(abs(a - b) <= 0.3 for a, b in zip(by_count, LAP516_STATE[o]))
        ok_t = all(abs(a - b) <= 0.3 for a, b in zip(by_tick, LAP516_STATE[o]))
        b2 &= ok_c or ok_t
        b3 &= cnt.get(1, 0) == 0 and cnt.get(4, 0) == 0
        decreases = sum(1 for a, b in zip(bc, bc[1:]) if b < a)
        increases = sum(b - a for a, b in zip(bc, bc[1:]) if b > a)
        b4 &= (bc[0], bc[-1]) == LAP516_BUILD[o][:2] and decreases == 0
        mask_counts = [e["mask_active_count"] for e in ext]
        b5 &= all(e["mask_active_count"] == len(e["mask_active_kinds"]) for e in ext)
        mmean = statistics.mean(mask_counts)
        b5 &= abs(mmean - LAP516_BUILD[o][2]) <= 0.05
        # 상태 2 진입(직전 표본 != 2) 횟수 — +0xD32 미기록이라 건설 오더 여부는 확정 불가(프록시)
        s2_entries = sum(1 for a, b in zip(st, st[1:]) if b == 2 and a != 2)
        s23_entries = sum(1 for a, b in zip(st, st[1:]) if b in (2, 3) and a not in (2, 3))
        net = bc[-1] - bc[0]
        span = ticks[-1] - ticks[0]
        per[o] = dict(
            state_pct_by_count=by_count, state_pct_by_tick=by_tick, match_count=ok_c, match_tick=ok_t,
            state_counts={str(k): v for k, v in sorted(cnt.items())},
            building_first=bc[0], building_last=bc[-1], net=net, increases=increases,
            decreases=decreases, ticks_per_building=round(span / net, 1) if net else None,
            mask_mean=round(mmean, 3), mask_min=min(mask_counts),
            mask_zero_frac=round(sum(1 for m in mask_counts if m == 0) / n, 4),
            max_used=max(used), used_last=used[-1],
            s2_entries_proxy=s2_entries, s23_entries_proxy=s23_entries,
            # 외삽(외삽일 뿐): 카드식 = 건물 보급 2,165 도달, lap516식 = (5000-used)/13.57 × tick/건물
            extrap_card_160_buildings_ticks=(round(ticks[-1] + (JOSEON_BUILDINGS_NEEDED - bc[-1]) * span / net)
                                             if net else None),
            extrap_lap516_formula_ticks=(round(ticks[-1] + (5000 - used[-1]) / 13.57 * span / net)
                                         if net else None),
        )
    r["per_owner"] = per
    r["max_used_by_owner"] = [per[o]["max_used"] for o in range(8)]
    r["B2"], r["B3"], r["B4"], r["B5"] = b2, b3, b4, b5
    r["B6"] = r["max_used_by_owner"] == LAP516_MAX_USED
    r["B7_other_d34_values"] = {str(k): v for k, v in sorted(other_values.items())}
    return r


def main() -> int:
    raw = ORIGINAL_EXE.read_bytes()
    result: dict = {"original_sha256": hashlib.sha256(raw).hexdigest()}
    result["A1"] = result["original_sha256"] == ORIGINAL_SHA256
    img = Image(raw)
    result["static"] = static_checks(img)
    result["runtime"] = runtime_checks()
    keys_s = ["A2", "A3", "A4", "A5", "A6", "A7", "A7_stride_ok", "A8", "A9"]
    keys_r = ["B1", "B2", "B3", "B4", "B5", "B6"]
    verdict = {"A1": result["A1"]}
    verdict.update({k: result["static"][k] for k in keys_s})
    verdict.update({k: result["runtime"][k] for k in keys_r})
    result["verdict"] = verdict
    result["failures"] = [k for k, v in verdict.items() if not v]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "w31_independent_review.json"
    payload = json.dumps(result, indent=1, sort_keys=True, default=str).encode()
    out.write_bytes(payload)
    print(json.dumps({"verdict": verdict, "failures": result["failures"],
                      "out": str(out), "out_sha256": hashlib.sha256(payload).hexdigest()}, indent=1))
    return 0 if not result["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
