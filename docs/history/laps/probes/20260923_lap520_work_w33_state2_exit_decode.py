#!/usr/bin/env python3
"""lap520 work(Sonnet5) — W33 M-0 정적 해독 + M-1 정적 예측 가능성 판정 (읽기 전용, 게임 실행 0).

카드: docs/work/active/G2_BUILD_STATE2_EXIT_PROBE_LAP519.md (W33, lap519 middle 발행).
대상: 상태2 핸들러 [0x43E174,0x43E2FD) 의 두 F5A0 종료(0x43E252/0x43E2D8)가 무엇을 검사하는지.

사전 고정 단언 (원본 EXE 바이트만 읽는다. 메모리/바이너리 쓰기 0, 게임 실행 0):
  A1 원본 SHA256 = b56986e0....
  A2 [0x43E174,0x43E2FD) 안 `call 0x43f5a0`(F5A0, 오더 리셋) 호출은 정확히 2곳
     (0x43E252, 0x43E2D8)이고, 이 범위 안에 `+0x3A70`(BUILD_ISSUE_OFF, dword 발부 tick) 쓰기는
     0건이다 — 카드 §3 반증 조건("F5A0 종료가 2곳이 아니거나 +0x3A70 쓰기가 있으면 S2L_REFUTED").
  A3 EXIT_A(0x43E252) 직전 게이트: `cmp word [edi+0x2014],bp; jg 0x43e261` — 즉 [edi+0x2014]
     (F4F0/F550이 쓰는 1,000칸 큐 카운트, W30 lap511 N157과 동일 필드)가 0이면 EXIT_A.
  A4 [edi+0x2014] 카운트를 올리는 것은 첫 루프(0x43E192~0x43E23F) 안 두 곳의 `call 0x43f4f0`
     (0x43E1F9, 0x43E22C)뿐이고, 그 진입 조건은 사이트 배열 `word [eax*2+0x974214]`
     (eax = esi*217, esi = 사이트 인덱스 bx) 값과 [edi+1](진영 바이트)·10%~14 확률식뿐이다.
     이 조건에 **종(kind, [edi+0xD36])은 피연산자로 전혀 등장하지 않는다** — 즉 EXIT_A 게이트는
     구조적으로 종-무관이다.
  A5 EXIT_B(0x43E2D8) 직전 루프(0x43E272~0x43E29F)는 `call 0x43f550`(F550, 큐 pop)으로 얻은
     후보를 `call 0x4afdd0`(edi, kind=[edi+0xD36], &out1, &out2)로 평가하고, eax==1인 후보가
     하나도 없으면(베스트 스코어가 초기값 -1 그대로) EXIT_B다. AFDD0 호출은 kind를 명시 인자로
     받는다 — 이 게이트는 구조적으로 종-의존적이다.
  A6 AFDD0(0x4AFDD0) 내부에서 kind(edx, 전달받은 그대로)는 `TYPESPEC_BASE + kind*TYPESPEC_STRIDE`
     (기존 read_type_specs()의 0x9B5228/0x394와 동일 베이스·스트라이드) 레코드의 **+0x16**(word, cx)·
     **+0x18**(word, ax)을 읽고, kind가 0x29(41)/0x38(56)/0x44(68)면 탐색 반경 상수를 10→15로
     올린다. 그 외에는 kind가 AFDD0 안에서 더 쓰이지 않는다(터레인 체크 0x4A4E70/점유 체크
     0x4AF970은 인자에 kind가 없다 — 전역 문맥 0xB3DDA8을 통해서만 간접 참조 가능, 미해독).
  A7 EXIT_B(0x43E2D8) 직전 게이트는 `cmp word [edi+0xD3C],si; jne 0x43e2e7`(베스트 사이트 슬롯이
     초기 sentinel -1 그대로면 통과)이고, 통과 시 `word [edi+0x3A74]=1`을 쓴다(EXIT_A 경로에는
     이 쓰기가 없다).
     +0x3A74는 BUILD_ISSUE_OFF(+0x3A70, dword)와 인접하지만 별도 필드이고, 기존
     read_owners_full()/read_owners_build_ext()/read_owners_build_issue()의 어떤 오프셋
     범위에도 들어있지 않다(신규 읽기 후보, M-2 §6 선언용).
  A8 +0x16/+0x18(및 kind*0x394 스트라이드 전체)은 원본 EXE의 `.data` 섹션 **raw 범위 밖**이다
     (SizeOfRawData < VirtualAddress+오프셋) — 즉 이 파라미터는 **정적 이미지에서 읽을 수 없고
     런타임에만 존재**한다(외부 데이터 파일에서 기동 시 적재). 그래서 M-1은 이 단언까지만
     "정적"이고, 수치 예측(§3 12/14 기준)은 M-0 정적 정보만으로는 불가능하다 — kind별로
     달라지는 유일한 순수 정적(코드 리터럴) 신호는 A6의 반경 상수뿐이며 카드 범위 14종 중
     이 신호로 구분되는 것은 kind 41(반경15) 대 나머지 13종(반경10) 단 1건이다.

사용법:
    python3 docs/history/laps/probes/20260923_lap520_work_w33_state2_exit_decode.py

exit 0 = 모든 단언 통과(S2L §3 미반증, M-0 완료). exit 1 = 단언 실패(S2L_REFUTED 또는 해독 오류).
프로세스 exit 0 자체는 제품 검증이 아니다. M-1 수치 예측·S2L §4 대조는 이 파일이 아니라
analysis/memory_maps/ 결과 문서에 원시로만 기록한다(과대 라벨 금지).
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
IMAGE_BASE = 0x400000

SHARED_TEMP = WORKSPACE / "temp" / "Syw2plus_patch" / "g2_capacity"
OUT_DIR = SHARED_TEMP / "20260923_lap520_work_w33_state2_exit_decode"

STATE2_START = 0x43E174
STATE2_END = 0x43E2FD
EXIT_A = 0x43E252
EXIT_B = 0x43E2D8
FUNNEL_KIND_OFF = 0xD36
QUEUE_COUNT_OFF = 0x2014
BUILD_ISSUE_OFF = 0x3A70  # existing tracked field (dword)
EXIT_B_FLAG_OFF = 0x3A74  # candidate new field (word), this lap's finding
TYPESPEC_BASE = 0x009B5228
TYPESPEC_STRIDE = 0x394
AFDD0_PARAM_A_OFF = 0x16  # word within type_spec record (== 0x9B523E - 0x9B5228)
AFDD0_PARAM_B_OFF = 0x18  # word within type_spec record (== 0x9B5240 - 0x9B5228)
RADIUS_OVERRIDE_KINDS = (0x29, 0x38, 0x44)  # 41, 56, 68
CARD_KINDS = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 105]

MD = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)


class Image:
    def __init__(self, raw: bytes):
        self.pe = pefile.PE(data=raw)
        self.sections = {
            s.Name.rstrip(b"\x00").decode(): s for s in self.pe.sections
        }

    def read(self, va: int, n: int) -> bytes:
        return self.pe.get_data(va - IMAGE_BASE, n)

    def dis(self, va: int, end: int) -> list[str]:
        return [f"{i.mnemonic} {i.op_str}".strip() for i in MD.disasm(self.read(va, end - va), va)]

    def find_calls_to(self, start: int, end: int, target: int) -> list[int]:
        out = []
        for ins in MD.disasm(self.read(start, end - start), start):
            if ins.mnemonic == "call":
                try:
                    dest = int(ins.op_str, 16)
                except ValueError:
                    continue
                if dest == target:
                    out.append(ins.address)
        return out

    def raw_offset_of_va(self, va: int) -> tuple[str, int, bool]:
        for name, s in self.sections.items():
            lo = IMAGE_BASE + s.VirtualAddress
            hi = lo + max(s.Misc_VirtualSize, s.SizeOfRawData)
            if lo <= va < hi:
                raw_extent_hi = lo + s.SizeOfRawData
                return name, va - lo, va < raw_extent_hi
        return "?", -1, False


def main() -> int:
    raw = ORIGINAL_EXE.read_bytes()
    result: dict = {"original_sha256": hashlib.sha256(raw).hexdigest()}
    result["A1"] = result["original_sha256"] == ORIGINAL_SHA256
    img = Image(raw)

    full_text = img.dis(STATE2_START, STATE2_END)
    result["state2_instruction_count"] = len(full_text)

    f5a0_calls = img.find_calls_to(STATE2_START, STATE2_END, 0x43F5A0)
    result["f5a0_calls"] = [hex(a) for a in f5a0_calls]
    # scan for any write to +0x3A70 (dword) inside the range: opcode 89 /r or C7 /0 with disp 0x3A70
    disp_pat_le = struct.pack("<i", BUILD_ISSUE_OFF)
    text_slice = img.read(STATE2_START, STATE2_END - STATE2_START)
    build_issue_write_present = disp_pat_le in text_slice
    result["build_issue_off_bytes_present"] = build_issue_write_present
    result["A2"] = (f5a0_calls == [EXIT_A, EXIT_B]) and not build_issue_write_present

    exit_a_gate = img.dis(0x43E247, 0x43E252)
    result["exit_a_gate"] = exit_a_gate
    result["A3"] = exit_a_gate == [
        f"cmp word ptr [edi + {hex(QUEUE_COUNT_OFF)}], bp",
        f"jg {hex(0x43E261)}",
        "mov ecx, edi",
    ]

    f4f0_calls = img.find_calls_to(STATE2_START, EXIT_A, 0x43F4F0)
    result["f4f0_calls"] = [hex(a) for a in f4f0_calls]
    first_loop = img.dis(0x43E192, 0x43E237)
    result["A4_first_loop_has_kind_operand"] = any(hex(FUNNEL_KIND_OFF)[2:] in s for s in first_loop)
    result["A4"] = f4f0_calls == [0x43E1F9, 0x43E22C] and not result["A4_first_loop_has_kind_operand"]

    f550_calls = img.find_calls_to(EXIT_A, EXIT_B, 0x43F550)
    afdd0_calls = img.find_calls_to(EXIT_A, EXIT_B, 0x4AFDD0)
    result["f550_calls"] = [hex(a) for a in f550_calls]
    result["afdd0_calls"] = [hex(a) for a in afdd0_calls]
    afdd0_call_setup = img.dis(0x43E27C, 0x43E28E)
    result["afdd0_call_setup"] = afdd0_call_setup
    result["A5"] = (
        len(f550_calls) == 1 and len(afdd0_calls) == 1
        and any(f"[edi + {hex(FUNNEL_KIND_OFF)}]" in s for s in afdd0_call_setup)
    )

    afdd0_head = img.dis(0x4AFDD0, 0x4AFE45)
    result["afdd0_head"] = afdd0_head
    result["A6_radius_override_present"] = (
        "cmp dx, 0x29" in afdd0_head and "cmp dx, 0x38" in afdd0_head and "cmp dx, 0x44" in afdd0_head
    )
    # exact literal-address form as disassembled (0x9B523E / 0x9B5240), independently
    # cross-checked against TYPESPEC_BASE + off below.
    result["A6"] = (
        any("0x9b523e" in s for s in afdd0_head)
        and any("0x9b5240" in s for s in afdd0_head)
        and (0x9B523E - TYPESPEC_BASE) == AFDD0_PARAM_A_OFF
        and (0x9B5240 - TYPESPEC_BASE) == AFDD0_PARAM_B_OFF
        and result["A6_radius_override_present"]
    )

    exit_b_gate = img.dis(0x43E2C4, 0x43E2D8)
    result["exit_b_gate"] = exit_b_gate
    result["A7"] = exit_b_gate == [
        "cmp word ptr [edi + 0xd3c], si",
        f"jne {hex(0x43E2E7)}",
        f"mov word ptr [edi + {hex(EXIT_B_FLAG_OFF)}], 1",
        "mov ecx, edi",
    ]

    sec_name, raw_off, in_raw = img.raw_offset_of_va(TYPESPEC_BASE)
    result["typespec_base_section"] = sec_name
    result["typespec_base_in_raw_image"] = in_raw
    result["A8"] = sec_name == ".data" and not in_raw

    verdict_keys = ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8"]
    verdict = {k: result[k] for k in verdict_keys}
    result["verdict"] = verdict
    result["failures"] = [k for k, v in verdict.items() if not v]

    result["s2l_refuted"] = not (result["A2"])
    result["card_kinds"] = CARD_KINDS
    result["radius_override_kinds_in_card_set"] = [k for k in CARD_KINDS if k in RADIUS_OVERRIDE_KINDS]
    result["m1_static_only_verdict"] = (
        "UNRESOLVED_STATIC_ONLY: AFDD0 kind-parameter table (radius/score) is runtime-resident "
        "(.data beyond raw image, A8), so the only purely-static kind-dependent signal in scope "
        "is the radius override for kind in {41,56,68}; only kind 41 of the 14 card kinds is "
        "affected -- 1/14 cannot reach the card's >=12/14 threshold either way. Numeric M-1 "
        "prediction requires one runtime snapshot of TYPESPEC_BASE+kind*TYPESPEC_STRIDE+0x16/+0x18 "
        "(a post-PS3 constant read, NOT a 24k-tick soak) -- declared as the M-2 candidate address "
        "for the next round."
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "w33_state2_exit_decode.json"
    payload = json.dumps(result, indent=1, sort_keys=True, default=str).encode()
    out.write_bytes(payload)
    print(json.dumps({"verdict": verdict, "failures": result["failures"],
                      "m1_static_only_verdict": result["m1_static_only_verdict"],
                      "out": str(out), "out_sha256": hashlib.sha256(payload).hexdigest()}, indent=1))
    return 0 if not result["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
