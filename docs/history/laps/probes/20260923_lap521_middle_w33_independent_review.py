#!/usr/bin/env python3
"""lap521 middle(Opus5.5) — W33(lap520 work) M-0/M-1 독립 검수 (읽기 전용, 게임 실행 0).

카드: docs/work/active/G2_BUILD_STATE2_EXIT_PROBE_LAP519.md (W33).
검수 대상: analysis/memory_maps/ai_build_state2_exit_decode_lap520_20260923.md,
          docs/history/laps/probes/20260923_lap520_work_w33_state2_exit_decode.py.

lap520 산출을 참조하지 않고 원본 바이트와 원시 파일만 다시 읽는다.
사전 고정 단언(데이터 개봉 전에 적음, 결과로 고치지 않는다):
  B1 원본 SHA256 = b56986e0....
  B2 [0x43E174,0x43E2FD) 안 F5A0 호출 = [0x43E252, 0x43E2D8], 명령 단위로 +0x3A70 쓰기 0건
     (lap520 A2는 바이트 패턴 검색이었다 → 명령 단위로 재확인).
  B3 EXIT_A 종-무관: 첫 루프[0x43E192,0x43E23F)와 callee F4F0 본문[0x43F4F0,0x43F549) 모두
     +0xD36 피연산자 0건(lap520 A4는 callee를 보지 않았다). 첫 루프 F4F0 호출 2곳의 두 번째 경로
     조건(+0x200E<5, 0x974226 표)을 원시로 남긴다.
  B4 (lap520 A6 서술 반증 시험) AFDD0 루프가 4A4E70을 부를 때 kind([esp+0x48]=원 인자 kind)를
     push한다. 그리고 4A4E70 머리에 kind 0x29/0x38/0x44 → 0x4A4F31(별도 술어 0x4A4BF0 호출)
     분기가 있다. 참이면 lap520의 "4A4E70/4AF970은 인자에 kind가 없다"는 틀린 서술이다.
  B5 4A4E70 일반 경로가 0x9B523E/0x9B5240(+0x16/+0x18)으로 이중 루프를 돌며 타일마다 0x42F020을
     부르고, AFDD0은 +0x16/+0x18 사본([esp+0x34]/[esp+0x30])을 4AF970에 넘긴다 ⇒ 두 필드는
     배치 footprint(폭/높이)로 쓰인다.
  B6 .text 전체에서 disp 0x3A74 피연산자 명령을 전수 나열한다(쓰기/읽기, 리셋 유무 판정 입력).
  B7 참고 저장소 정적 캡처 unit_templates_9b5228_394x152.raw(읽기 전용)의 겹치는 6필드
     (cost/flags/nation/ratio_cap/typemax_default/crowd_flat_flag)가 lap518 런타임 type_specs.json
     (a23ba1d7...)과 겹치는 모든 kind에서 불일치 0이다. 참이면 이 캡처는 같은 표다.
  B8 B7이 참일 때만 카드 14종의 +0x16/+0x18을 캡처에서 읽고, 두 규칙으로 S2L §4 방향과 대조한다.
     R1: 면적 1(1x1)만 성공 다수, R2: 면적<=4만 성공 다수. **두 규칙 모두 S2L §4 공개 뒤 정한 사후
     임계다** ⇒ 이 파일은 카드 §3 라벨을 부여하지 않고 일치 수만 원시로 남긴다.

  (B6 sanity: 전수 스윕이 .text 끝까지 가고 이미 본 0x43E2CD 쓰기를 포함해야 한다 — 1차 실행 도구 결함 뒤 추가.)
exit 0 = B1~B7 성립(B4는 lap520 서술 반증이 "성립"한 것). 프로세스 exit 0은 제품 검증이 아니다.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import struct
import sys

import capstone
import pefile

WORKSPACE = pathlib.Path(__file__).resolve().parents[5]
ORIGINAL_EXE = WORKSPACE / "Syw2plus_re" / "Syw2plus" / "syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
REF_CAPTURE = (WORKSPACE / "Syw2plus_re" / "plan_c" / "verification" / "captures" / "original"
               / "ai_static_tables_0703" / "tables" / "unit_templates_9b5228_394x152.raw")
LAP518_TYPESPECS = (WORKSPACE / "temp" / "Syw2plus_patch" / "g2_capacity"
                    / "20260923_lap518_work_w32_build_funnel" / "type_specs.json")
LAP518_TYPESPECS_SHA = "a23ba1d70b19232c77793ab20955660c9ce413304a5116429883b8abbbedc078"
OUT_DIR = WORKSPACE / "temp" / "Syw2plus_patch" / "g2_capacity" / "20260923_lap521_middle_w33_review"
IMAGE_BASE = 0x400000
STRIDE = 0x394

# S2L §4 (lap519) 선택 직후 코호트 발부/전체 — 원문 표 그대로.
S2L_TABLE = {40: (2, 32), 41: (1, 66), 46: (2, 34), 49: (2, 21), 44: (6, 26), 48: (5, 23),
             51: (3, 13), 45: (9, 44), 52: (6, 17), 47: (8, 17), 43: (3, 5), 105: (9, 15),
             50: (21, 25), 42: (12, 14)}

MD = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
MD.detail = True


def disasm(pe, start, end):
    return list(MD.disasm(pe.get_data(start - IMAGE_BASE, end - start), start))


def text_of(ins):
    return f"{ins.mnemonic} {ins.op_str}".strip()


def call_target(ins):
    if ins.mnemonic != "call":
        return None
    try:
        return int(ins.op_str, 16)
    except ValueError:
        return None


def mem_write_disp(ins, disp):
    """True if first operand is a memory operand with the given displacement (i.e. a store)."""
    ops = ins.operands
    return bool(ops) and ops[0].type == capstone.x86.X86_OP_MEM and ops[0].mem.disp == disp \
        and ins.mnemonic not in ("cmp", "test", "push")


def main() -> int:
    raw = ORIGINAL_EXE.read_bytes()
    r: dict = {"original_sha256": hashlib.sha256(raw).hexdigest()}
    r["B1"] = r["original_sha256"] == ORIGINAL_SHA256
    pe = pefile.PE(data=raw)

    s2 = disasm(pe, 0x43E174, 0x43E2FD)
    f5a0 = [i.address for i in s2 if call_target(i) == 0x43F5A0]
    w3a70 = [hex(i.address) for i in s2 if mem_write_disp(i, 0x3A70)]
    r["f5a0_calls"] = [hex(a) for a in f5a0]
    r["state2_writes_3a70"] = w3a70
    r["B2"] = f5a0 == [0x43E252, 0x43E2D8] and not w3a70

    loop1 = disasm(pe, 0x43E192, 0x43E23F)
    f4f0 = disasm(pe, 0x43F4F0, 0x43F549)
    r["loop1_d36_ops"] = [hex(i.address) for i in loop1 if "0xd36" in i.op_str]
    r["f4f0_d36_ops"] = [hex(i.address) for i in f4f0 if "0xd36" in i.op_str]
    r["loop1_f4f0_calls"] = [hex(i.address) for i in loop1 if call_target(i) == 0x43F4F0]
    r["loop1_second_path"] = [text_of(i) for i in loop1 if 0x43E204 <= i.address <= 0x43E22C]
    r["B3"] = (not r["loop1_d36_ops"] and not r["f4f0_d36_ops"]
               and r["loop1_f4f0_calls"] == ["0x43e1f9", "0x43e22c"])

    afdd0_loop = disasm(pe, 0x4AFE80, 0x4AFEC6)
    seq = [text_of(i) for i in afdd0_loop]
    r["afdd0_callsite_4a4e70"] = seq
    kind_reload = "mov edx, dword ptr [esp + 0x48]" in seq
    push_idx = [k for k, s in enumerate(seq) if s == "push edx"]
    call_idx = seq.index("call 0x4a4e70")
    kind_pushed = kind_reload and any(k < call_idx for k in push_idx)
    head = disasm(pe, 0x4A4E70, 0x4A4E9B)
    hs = [text_of(i) for i in head]
    r["4a4e70_head"] = hs
    special = all(f"cmp bx, {k}" in hs for k in ("0x29", "0x38", "0x44")) \
        and hs.count("je 0x4a4f31") == 3
    tail = [text_of(i) for i in disasm(pe, 0x4A4F31, 0x4A4F81)]
    r["4a4e70_special_calls"] = [s for s in tail if s.startswith("call")]
    r["B4"] = kind_pushed and special and r["4a4e70_special_calls"] == ["call 0x4a4bf0"]

    gen = [text_of(i) for i in disasm(pe, 0x4A4E9B, 0x4A4F1A)]
    r["B5_generic_reads"] = [s for s in gen if "0x9b523e" in s or "0x9b5240" in s]
    footprint_loop = any("0x9b523e" in s for s in gen) and any("0x9b5240" in s for s in gen) \
        and "call 0x42f020" in gen
    af970_args = [s for s in seq[call_idx + 1:]]
    r["afdd0_callsite_4af970"] = af970_args
    passes_fp = ("mov edx, dword ptr [esp + 0x30]" in af970_args
                 and "mov eax, dword ptr [esp + 0x34]" in af970_args)
    store_fp = [text_of(i) for i in disasm(pe, 0x4AFE03, 0x4AFE1B)]
    r["afdd0_fp_store"] = store_fp
    r["B5"] = footprint_loop and passes_fp and store_fp == [
        "mov cx, word ptr [eax + 0x9b523e]", "mov ax, word ptr [eax + 0x9b5240]",
        "mov word ptr [esp + 0x24], cx", "mov word ptr [esp + 0x20], ax"]

    text = next(s for s in pe.sections if s.Name.rstrip(b"\x00") == b".text")
    tva = IMAGE_BASE + text.VirtualAddress
    # 1차 실행에서 skipdata 없는 선형 스윕이 첫 무효 바이트에서 멈춰 0건을 냈다(도구 결함).
    # skipdata로 끝까지 훑고, 이미 확인한 0x43E2CD가 잡히는지를 sanity로 건다.
    sweep = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    sweep.detail = True
    sweep.skipdata = True
    hits, last = [], 0
    for ins in sweep.disasm(pe.get_data(text.VirtualAddress, text.Misc_VirtualSize), tva):
        last = ins.address
        if ins.id == 0:
            continue
        for op in ins.operands:
            if op.type == capstone.x86.X86_OP_MEM and op.mem.disp == 0x3A74:
                hits.append({"va": hex(ins.address), "ins": text_of(ins),
                             "write": mem_write_disp(ins, 0x3A74)})
    r["disp_3a74_sites"] = hits
    r["sweep_last_va"] = hex(last)
    r["B6"] = any(h["va"] == "0x43e2cd" for h in hits) and last >= tva + text.Misc_VirtualSize - 16

    cap = REF_CAPTURE.read_bytes()
    r["ref_capture_sha256"] = hashlib.sha256(cap).hexdigest()
    r["ref_capture_len"] = len(cap)
    ts_raw = LAP518_TYPESPECS.read_bytes()
    r["lap518_typespecs_sha_ok"] = hashlib.sha256(ts_raw).hexdigest() == LAP518_TYPESPECS_SHA
    ts = json.loads(ts_raw)
    n_rows = len(cap) // STRIDE
    compared, mism = 0, []
    for k_str, v in ts.items():
        k = int(k_str)
        if k >= n_rows:
            continue
        b = k * STRIDE
        got = dict(cost=struct.unpack_from("<h", cap, b + 0x10)[0],
                   flags_dword=struct.unpack_from("<I", cap, b + 0x24)[0],
                   nation=struct.unpack_from("<h", cap, b + 0x28)[0],
                   ratio_cap=struct.unpack_from("<h", cap, b + 0x32)[0],
                   typemax_default=struct.unpack_from("<h", cap, b + 0x34)[0],
                   crowd_flat_flag=struct.unpack_from("<I", cap, b + 0x4C)[0])
        compared += 1
        if got != v:
            mism.append({"kind": k, "capture": got, "runtime": v})
    r["B7_rows_compared"] = compared
    r["B7_mismatches"] = mism
    r["B7"] = r["lap518_typespecs_sha_ok"] and compared > 0 and not mism

    fp = {}
    if r["B7"]:
        for k in S2L_TABLE:
            b = k * STRIDE
            fp[k] = (struct.unpack_from("<h", cap, b + 0x16)[0], struct.unpack_from("<h", cap, b + 0x18)[0])
    rows, m1, m2 = [], 0, 0
    for k, (ok, n) in S2L_TABLE.items():
        w, h = fp.get(k, (None, None))
        obs_success = ok / n >= 0.5
        area = (w or 0) * (h or 0)
        p1, p2 = area == 1, 0 < area <= 4
        m1 += p1 == obs_success
        m2 += p2 == obs_success
        rows.append({"kind": k, "issued": ok, "total": n, "w": w, "h": h, "special_4a4bf0": k in (41, 56, 68),
                     "obs_success_majority": obs_success, "R1_pred": p1, "R2_pred": p2})
    r["B8_rows"] = rows
    r["B8_R1_match"] = m1
    r["B8_R2_match"] = m2
    r["B8_note"] = "post-hoc thresholds; no card label assigned"

    keys = ["B1", "B2", "B3", "B4", "B5", "B6", "B7"]
    r["failures"] = [k for k in keys if not r[k]]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(r, indent=1, sort_keys=True, default=str).encode()
    out = OUT_DIR / "w33_independent_review.json"
    out.write_bytes(payload)
    print(json.dumps({k: r[k] for k in keys} | {
        "failures": r["failures"], "B7_rows_compared": compared, "B7_mismatches": len(mism),
        "B8_R1_match": m1, "B8_R2_match": m2, "disp_3a74_sites": hits,
        "out": str(out), "out_sha256": hashlib.sha256(payload).hexdigest()}, indent=1))
    return 0 if not r["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
