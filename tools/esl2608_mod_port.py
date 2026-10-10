#!/usr/bin/env python3
"""Port an OllyDbg-modded ``[ESL]Syw2plus 2608.exe`` onto a pinned R5 deliverable.

A community modder edits the *pinned original* 2608 EXE (AI table values, AI
code, code caves in ``.psncode``).  Our delivered R5 EXEs stack several binary
layers on top of that same original: the AI shop-table sync layer, the G2 unit
pool 1200->4093 relocation, the G5 20->50 selection relocation, the G6/G7 seat
fixes and (for the ``_G1`` builds) the G1 renderer hooks installed at runtime by
the ``inmm``/``_G1MM`` DLL.

This tool diffs ``modded`` against the *pinned original*, classifies each
contiguous change run, and replays it onto a pinned R5/R5_G1 target:

- ``DATA``    edits in an initialized-data section are copied verbatim.  The AI
  table at ``0x4EC514..+2576`` is fine because the sync layer makes it the
  source of truth again; a target without that layer is flagged.
- ``CONFLICT`` the run overlaps bytes one of our layers already changed (target
  vs original), or a G1 runtime hook/contract site on a ``_G1`` target.  Not
  applied; both byte strings and the owning layer are reported.
- ``RELOC``   a memory displacement, or a ``mov``/``lea`` immediate, that points
  into a relocated old range is rewritten to its new address.
- ``SUSPECT`` an in-range value that is not auto-relocated (e.g. ``push imm``),
  or a known relocated constant (``0x4B0``/``0x4AF``/``0x14`` ...).  Applied as
  written but flagged for manual review.
- ``PLAIN``   everything else is applied verbatim.

Modder-added code in ``.psncode``/``.data`` slack is decoded the same way.

Copy-only: inputs are never written; the output is an exclusive create.
"""

from __future__ import annotations

import argparse
from array import array
import hashlib
import json
import os
import re
import struct
import tempfile
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import capstone
import pefile

from patches.population.full_tail_relocation_storage_layout_v1 import layout
from patches.population.g2_esl2608_pool4092_owner500 import CAPACITY as G2_CAPACITY

IMAGE_BASE = 0x00400000
ORIGINAL_SHA256 = "bf39cb73f395d677a1c27fda01698f849b23973a39fd9be8b22af0010cb60f27"
ORIGINAL_SIZE = 0x104000
ORIGINAL_SECTIONS = (b".text", b".rdata", b".data", b".rsrc", b".psncode", b".psndata")
R5_TAIL_SECTIONS = (b".shopai", b".g2bss", b".g2code", b".g2psn", b".g5bss", b".g5code")
R5_SIZE = 0x109000

DATA_SECTIONS = {b".rdata", b".data", b".rsrc", b".psndata"}
CODE_SECTIONS = {b".text", b".psncode"}

# AI shop table (sync layer keeps it authoritative at the old address).
AI_TABLE_VA = 0x004EC514
AI_TABLE_LEN = 2576
AI_ROW_STRIDE = 18
AI_ROW_COUNT = 143
AI_SENTINEL_VA = AI_TABLE_VA + AI_ROW_COUNT * AI_ROW_STRIDE  # 0x4ECF22, word 0xFFFE
AI_SHAPE_GUARD = 2 + 3 * AI_ROW_STRIDE  # sentinel + room for the 3 appended shop rows
IMAGE_SCN_MEM_EXECUTE = 0x20000000
SYNC_HOOK_FILE_OFFSET = 0x00406C70 - IMAGE_BASE
G1_IMPORT_FILE_OFFSET = 0x004EBB5F - IMAGE_BASE  # "_INMM" vs "_G1MM"

# ESL2608 PSN cache relocation (from patches.population.g2_esl2608_pool4092_owner500).
PSN_CACHE_OLD = 0x0110C000
PSN_CACHE_NEW = 0x01896000
PSN_CACHE_LEN = G2_CAPACITY * 16

# Selection storage relocation (G5): count dword + 20->50 entry array.
SEL_COUNT_OLD = 0x00899024
SEL_COUNT_NEW = 0x018A6000
SEL_ENTRY_OLD = 0x00899028
SEL_ENTRY_NEW = 0x018A6004
SEL_ENTRY_OLD_END = 0x00899078  # old 20-entry array end (a separate bound variable)

# R5-derived relocated-constant dictionary (old immediate -> new immediate).
CONST_SUSPECTS = {
    0x4B0: 0xFFD,  # 1200 owner/pool bound -> 4093-era bound
    0x4AF: 0xFFC,
    0x14: 0x32,  # 20 -> 50 selection cap
    0x80: 0x200,
    0x84: 0x204,
    0x98: 0x270,
}

_MD = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
_MD.detail = True
# A second instance resynchronizes past embedded data for the whole-section
# evidence sweep; the detailed instance above halts at the first bad byte.
_MD_SWEEP = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
_MD_SWEEP.detail = True
_MD_SWEEP.skipdata = True


class LayoutError(ValueError):
    """Raised when the modded EXE is not the pinned original layout."""


# --------------------------------------------------------------------------- #
# Relocation map
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Region:
    name: str
    old_start: int
    old_end: int
    new_start: int
    array_old_span: int
    array_new_span: int

    def inside(self, value: int) -> int | None:
        if not self.old_start <= value < self.old_end:
            return None
        off = value - self.old_start
        if off < self.array_old_span:
            return self.new_start + off  # inside the (grown) array: linear delta
        # Trailing count word(s) sit just past the array, which grew.
        return self.new_start + self.array_new_span + (off - self.array_old_span)


class RegionMap:
    """Static map of relocated old address ranges to their new base.

    The six unit arrays come from the verified G2 full-tail layout (with the
    ESL2608 pool-base delta); the selection arrays and the PSN cache are added
    on top.  Each region keeps its own per-array delta, so the trailing count
    words that follow a grown array are mapped by position inside the region
    rather than by a single global delta.
    """

    def __init__(self) -> None:
        geometry = layout(G2_CAPACITY)
        esl_delta = 0x0112E000 - geometry.regions[0].new_start
        regions = [
            _Region(r.name, r.old_start, r.old_end, r.new_start + esl_delta,
                    r.array_old_span, r.array_new_span)
            for r in geometry.regions
        ]
        regions.append(_Region("selection_count", SEL_COUNT_OLD, SEL_COUNT_OLD + 4,
                               SEL_COUNT_NEW, 4, 4))
        regions.append(_Region("selection_entries", SEL_ENTRY_OLD, SEL_ENTRY_OLD_END,
                               SEL_ENTRY_NEW, SEL_ENTRY_OLD_END - SEL_ENTRY_OLD, 50 * 4))
        regions.append(_Region("psn_cache", PSN_CACHE_OLD, PSN_CACHE_OLD + PSN_CACHE_LEN,
                               PSN_CACHE_NEW, PSN_CACHE_LEN, PSN_CACHE_LEN))
        self.regions = tuple(regions)

    def inside(self, value: int) -> tuple[str, int] | None:
        for region in self.regions:
            mapped = region.inside(value)
            if mapped is not None:
                return region.name, mapped
        return None


REGION_MAP = RegionMap()


# --------------------------------------------------------------------------- #
# PE geometry
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Section:
    name: bytes
    va: int
    vsize: int
    raw_ptr: int
    raw_size: int
    characteristics: int

    @property
    def file_end(self) -> int:
        return self.raw_ptr + self.raw_size


def _sections(data: bytes) -> list[_Section]:
    pe = pefile.PE(data=data, fast_load=True)
    try:
        return [
            _Section(s.Name.rstrip(b"\0"), IMAGE_BASE + s.VirtualAddress,
                     s.Misc_VirtualSize, s.PointerToRawData, s.SizeOfRawData,
                     s.Characteristics)
            for s in pe.sections
        ]
    finally:
        pe.close()


def _file_to_va(sections: list[_Section], file_off: int) -> int | None:
    for s in sections:
        if s.raw_ptr <= file_off < s.file_end:
            return s.va + (file_off - s.raw_ptr)
    return None


def _section_of(sections: list[_Section], file_off: int) -> _Section | None:
    for s in sections:
        if s.raw_ptr <= file_off < s.file_end:
            return s
    return None


def _check_modded_layout(original: bytes, modded: bytes) -> list[_Section]:
    orig_secs = _sections(original)
    try:
        mod_secs = _sections(modded)
    except pefile.PEFormatError as exc:
        raise LayoutError(f"모드 EXE PE 파싱 실패: {exc}") from exc
    if len(mod_secs) != len(orig_secs):
        raise LayoutError(
            f"섹션 개수가 원본과 다름({len(mod_secs)} != {len(orig_secs)}); "
            "모더가 섹션을 추가한 것으로 보임"
        )
    if len(modded) != len(original):
        raise LayoutError(
            f"모드 EXE 크기가 원본과 다름: {len(modded):#x} != {len(original):#x}"
        )
    if mod_secs != orig_secs:
        raise LayoutError("섹션 테이블이 원본과 다름(이름/주소/크기/플래그 변경)")
    return mod_secs


# --------------------------------------------------------------------------- #
# Target evidence (learned from the real original->target rewrites)
# --------------------------------------------------------------------------- #
@dataclass
class TargetEvidence:
    rewrites: dict[int, list[int]] = field(default_factory=dict)
    _kept: set[int] = field(default_factory=set)

    def consistent(self, value: int) -> int | None:
        news = self.rewrites.get(value)
        if not news or value in self._kept:
            return None
        unique = set(news)
        return next(iter(unique)) if len(unique) == 1 else None


def _is_branch(insn: capstone.CsInsn) -> bool:
    return insn.group(capstone.CS_GRP_JUMP) or insn.group(capstone.CS_GRP_CALL)


def _branch_target(insn: capstone.CsInsn) -> int | None:
    """Absolute target of a direct (immediate) call/jmp/jcc, else None."""
    if not _is_branch(insn):
        return None
    for op in insn.operands:
        if op.type == capstone.x86.X86_OP_IMM:
            return op.imm & 0xFFFFFFFF
    return None


def _operand_fields(insn: capstone.CsInsn) -> list[tuple[int, int, str, bool]]:
    """Return ``(field_offset, value, mnemonic, is_imm)`` for 32-bit imm/disp.

    A direct branch's immediate is capstone's *absolute* target while its bytes
    are a rel32, so branch immediates are excluded (code VAs never move).
    """
    out: list[tuple[int, int, str, bool]] = []
    branch = _is_branch(insn)
    for op in insn.operands:
        if op.type == capstone.x86.X86_OP_IMM and insn.imm_size == 4 and not branch:
            out.append((insn.imm_offset, op.imm & 0xFFFFFFFF, insn.mnemonic, True))
        elif op.type == capstone.x86.X86_OP_MEM and insn.disp_size == 4:
            out.append((insn.disp_offset, op.mem.disp & 0xFFFFFFFF, insn.mnemonic, False))
    return out


def _small_imms(insn: capstone.CsInsn) -> list[tuple[int, int, int]]:
    """``(field_offset, size, value)`` for 8/16-bit non-branch immediates."""
    if _is_branch(insn) or insn.imm_size not in (1, 2):
        return []
    return [
        (insn.imm_offset, insn.imm_size, op.imm & ((1 << (8 * insn.imm_size)) - 1))
        for op in insn.operands
        if op.type == capstone.x86.X86_OP_IMM
    ]


def _code_slice(sec: _Section) -> tuple[int, int]:
    """File range of a code section's raw bytes (never past its raw data)."""
    return sec.raw_ptr, sec.raw_ptr + min(sec.vsize, sec.raw_size)


_EVIDENCE_CACHE: dict[tuple[int, int], TargetEvidence] = {}


def target_evidence(original: bytes, target: bytes) -> TargetEvidence:
    """Decode the original code sections and learn every operand the target moved."""
    key = (hash(original), hash(target))
    cached = _EVIDENCE_CACHE.get(key)
    if cached is not None:
        return cached
    evidence = TargetEvidence()
    sections = _sections(original)
    for s in sections:
        if s.name not in CODE_SECTIONS:
            continue
        lo, hi = _code_slice(s)
        for insn in _MD_SWEEP.disasm(original[lo:hi], s.va):
            if insn.id == 0:  # skipdata .byte stub: no decoded operands
                continue
            base_off = s.raw_ptr + (insn.address - s.va)
            for fld, value, _mn, _imm in _operand_fields(insn):
                w = base_off + fld
                new_value = struct.unpack_from("<I", target, w)[0]
                if new_value != value:
                    evidence.rewrites.setdefault(value, []).append(new_value)
                else:
                    evidence._kept.add(value)
    _EVIDENCE_CACHE[key] = evidence
    return evidence


# --------------------------------------------------------------------------- #
# Instruction boundaries
# --------------------------------------------------------------------------- #
_START_CACHE: dict[int, array] = {}


def _start_map(original: bytes, sections: list[_Section]) -> array:
    """offset -> covering instruction start, from one skipdata sweep (-1 = unknown).

    This is the same sweep :func:`target_evidence` uses, so operand fields line
    up with the ones the R5 layers actually rewrote.
    """
    key = hash(original)
    cached = _START_CACHE.get(key)
    if cached is not None:
        return cached
    starts = array("i", [-1]) * len(original)
    for s in sections:
        if s.name not in CODE_SECTIONS:
            continue
        lo, hi = _code_slice(s)
        for insn in _MD_SWEEP.disasm(original[lo:hi], s.va):
            if insn.id == 0:  # skipdata stub: leave unknown, fall back to voting
                continue
            off = lo + (insn.address - s.va)
            starts[off : off + insn.size] = array("i", [off]) * insn.size
    _START_CACHE[key] = starts
    return starts


def _insn_start(original: bytes, sections: list[_Section], file_off: int) -> int:
    """File offset of the instruction covering ``file_off``.

    Uses the one-time sweep map; only where the sweep emitted a data stub does
    it fall back to a backward vote over the preceding offsets.
    """
    va = _file_to_va(sections, file_off)
    if va is None:
        return file_off
    mapped = _start_map(original, sections)[file_off]
    if mapped >= 0:
        return mapped
    votes: Counter[int] = Counter()
    for k in range(0, 24):
        begin = file_off - k
        if begin < 0:
            break
        for insn in _MD.disasm(original[begin : file_off + 16], va - k):
            if insn.address <= va < insn.address + insn.size:
                votes[insn.address] += 1
                break
            if insn.address > va:
                break
    if not votes:
        return file_off
    best_va = votes.most_common(1)[0][0]
    return file_off - (va - best_va)


def _is_added_code(original: bytes, sections: list[_Section], start_off: int, end_off: int) -> bool:
    """True when the run sits in an all-zero slack region (modder-added code).

    A lone zero immediate byte inside real code is not slack, so the window is
    padded and clipped to the section the run belongs to.
    """
    sec = _section_of(sections, start_off)
    if sec is None:
        return False
    lo = max(sec.raw_ptr, start_off - 8)
    hi = min(sec.file_end, end_off + 8)
    return not any(original[lo:hi])


def _decode_run(image: bytes, original: bytes, sections: list[_Section],
                start_off: int, end_off: int) -> tuple[int, list[capstone.CsInsn]]:
    """Decode ``image`` instructions overlapping ``[start_off, end_off)``.

    Returns ``(begin_off, instructions)``.  For code the modder added into
    slack the decode starts at the run; otherwise it starts at the original
    instruction boundary so operand fields align.
    """
    begin = start_off if _is_added_code(original, sections, start_off, end_off) else \
        _insn_start(original, sections, start_off)
    va = _file_to_va(sections, begin)
    if va is None:
        return begin, []
    insns: list[capstone.CsInsn] = []
    for insn in _MD.disasm(image[begin : end_off + 16], va):
        insns.append(insn)
        if begin + (insn.address - va) + insn.size >= end_off:
            break
    return begin, insns


# --------------------------------------------------------------------------- #
# G1 runtime hook / contract site inventory
# --------------------------------------------------------------------------- #
def _g1_runtime_sites() -> tuple[tuple[int, int, str], ...]:
    """Parse ``g1_mirror2x.c`` for the renderer prologues the DLL overwrites."""
    source = (Path(__file__).resolve().parent / "inmm_stub" / "g1_mirror2x.c").read_text(
        encoding="utf-8"
    )
    defines = dict(re.findall(r"#define (G1_\w+)\s+(0x[0-9A-Fa-f]+|\d+)u", source))
    installed = sorted(set(re.findall(r"install_one\((G1_\w+),", source)))
    sites: list[tuple[int, int, str]] = []
    for name in installed:
        if name not in defines:
            continue
        length = int(defines.get(f"{name}_LEN", "8"), 0)
        sites.append((int(defines[name], 0), length, name))
    # Call-site and contract bytes verified by the DLL at install time.
    sites.extend(
        [
            (0x004C7EE6, 5, "G1_PRIMARY_READBACK_SITE"),
            (0x004B5493, 5, "G1_BAR_COPY_SITE"),
            (0x004B23B5, 5, "G1_BRIEFING_COMPOSE_SITE"),
            (0x00445930, 6, "G1_SFX"),
            (0x004D7938, 6, "G1_IMPORT_THUNK"),
            (0x00464374, 5, "G1_CONTRACT_CALLER"),
            (0x00464502, 7, "G1_CONTRACT_MODE_WIDTH"),
            (0x00464509, 7, "G1_CONTRACT_MODE_HEIGHT"),
            (0x0046457A, 3, "G1_CONTRACT_MODE_CALL"),
        ]
    )
    for va in (0x00432A2D, 0x00432AB5, 0x00432B38, 0x00432BD4,
               0x00432C7C, 0x00432D4E, 0x00432E1D, 0x00432ED2):
        sites.append((va, 5, "G1_MOVE_SITE"))
    return tuple(sites)


G1_RUNTIME_SITES = _g1_runtime_sites()


# --------------------------------------------------------------------------- #
# Target classification
# --------------------------------------------------------------------------- #
def _validate_target(target: bytes) -> dict[str, Any]:
    if len(target) != R5_SIZE:
        raise ValueError("target EXE 크기가 핀된 R5 레이아웃이 아님")
    try:
        secs = _sections(target)
    except pefile.PEFormatError as exc:
        raise ValueError(f"target PE 파싱 실패: {exc}") from exc
    names = tuple(s.name for s in secs)
    if names != ORIGINAL_SECTIONS + R5_TAIL_SECTIONS:
        raise ValueError(f"target EXE 섹션 레이아웃이 핀된 R5가 아님: {names}")
    is_g1 = target[G1_IMPORT_FILE_OFFSET : G1_IMPORT_FILE_OFFSET + 2] != b"IN"
    sync_layer = target[SYNC_HOOK_FILE_OFFSET] == 0xE9
    return {
        "sha256": hashlib.sha256(target).hexdigest(),
        "is_g1": is_g1,
        "sync_layer": sync_layer,
        "variant": "R5_G1" if is_g1 else "R5",
    }


def _diff_runs(original: bytes, modded: bytes) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    i = 0
    n = len(original)
    while i < n:
        if original[i] != modded[i]:
            j = i
            while j < n and original[j] != modded[j]:
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    # Modder-added code often contains 0x00 bytes that match the zero slack and
    # split one logical block into several runs; rejoin runs separated only by a
    # short all-zero slack gap so an instruction is never cut in two.
    merged: list[tuple[int, int]] = []
    for start, end in runs:
        if merged:
            prev_start, prev_end = merged[-1]
            gap = start - prev_end
            if 0 <= gap <= 15 and not any(original[prev_end:start]):
                merged[-1] = (prev_start, end)
                continue
        merged.append((start, end))
    return merged


def _g1_site_at(file_off: int, end_off: int, sections: list[_Section]) -> tuple[int, int, str] | None:
    va_start = _file_to_va(sections, file_off)
    if va_start is None:
        return None
    va_end = va_start + (end_off - file_off)
    for va, length, name in G1_RUNTIME_SITES:
        if va < va_end and va_start < va + length:
            return va, length, name
    return None


def _conflict_owner(original: bytes, target: bytes, sections: list[_Section],
                    target_sections: list[_Section],
                    start_off: int, end_off: int) -> dict[str, Any]:
    """Describe which layer owns the target bytes a conflicting run overlaps."""
    owner = "레이어(원본 대비 변경된 바이트)"
    detail = ""
    sec = _section_of(sections, start_off)
    if sec is None or sec.name not in CODE_SECTIONS:
        return {"owner": owner, "detail": detail}
    # A hook rewrites the original prologue into a jump into a trampoline
    # section; the jump can start a byte before the original boundary, so scan
    # the target bytes directly for an E9/E8 whose 5-byte span overlaps the run.
    for off in range(max(sec.raw_ptr, start_off - 4), end_off):
        if target[off] not in (0xE8, 0xE9) or off + 5 > sec.file_end:
            continue
        va = _file_to_va(sections, off)
        if va is None or not (off < end_off and off + 5 > start_off):
            continue
        dest = (va + 5 + struct.unpack_from("<i", target, off + 1)[0]) & 0xFFFFFFFF
        dest_sec = _section_for_va(target_sections, dest)
        if dest_sec is not None and dest_sec.name in {b".g2code", b".g5code", b".g2psn"}:
            label = dest_sec.name.decode()
            return {
                "owner": "G5" if label == ".g5code" else "G2",
                "detail": f"원본 명령이 {label} 트램폴린으로 이동했음",
            }
    # Otherwise the target relocated an operand: classify by the ORIGINAL value.
    _b, orig_insns = _decode_run(original, original, sections, start_off, end_off)
    for insn in orig_insns:
        for _fld, value, _mn, _imm in _operand_fields(insn):
            mapped = REGION_MAP.inside(value)
            if mapped is not None:
                return {"owner": _owner_for_region(mapped[0]), "detail": f"{mapped[0]} 재배치 operand"}
    return {"owner": owner, "detail": detail}


def _section_for_va(sections: list[_Section], va: int) -> _Section | None:
    for s in sections:
        if s.va <= va < s.va + max(s.vsize, s.raw_size):
            return s
    return None


def _owner_for_region(region: str) -> str:
    if region.startswith("selection"):
        return "G5 (선택 배열 재배치)"
    return "G2 (유닛 배열 재배치)"


def _in_ai_table(value: int) -> bool:
    return AI_TABLE_VA <= value < AI_TABLE_VA + AI_TABLE_LEN


def _auto_target(value: int, evidence: TargetEvidence, sync_layer: bool) -> tuple[str, int] | None:
    """Return ``(region, new_value)`` for an address-like value, else None.

    With the sync layer the old AI table is the source of truth again, so a
    reference to it must stay at the old address.
    """
    mapped = REGION_MAP.inside(value)
    if mapped is not None:
        return mapped
    if sync_layer and _in_ai_table(value):
        return None
    if value >= IMAGE_BASE:
        learned = evidence.consistent(value)
        if learned is not None:
            return ("ai_table" if _in_ai_table(value) else "evidence"), learned
    return None


@dataclass
class _Ctx:
    original: bytes
    modded: bytes
    target: bytes
    out: bytearray
    sections: list[_Section]
    target_sections: list[_Section]
    evidence: TargetEvidence
    target_info: dict[str, Any]
    warnings: list[dict[str, Any]]
    incoming: set[int] = field(default_factory=set)  # branch targets of modded code runs


# --------------------------------------------------------------------------- #
# Core
# --------------------------------------------------------------------------- #
def port_bytes(original: bytes, modded: bytes, target: bytes) -> tuple[bytes, dict[str, Any]]:
    if hashlib.sha256(original).hexdigest() != ORIGINAL_SHA256:
        raise LayoutError("원본 EXE SHA256 불일치; 핀된 2608 원본이 아님")
    sections = _check_modded_layout(original, modded)
    ctx = _Ctx(
        original, modded, target, bytearray(target), sections, _sections(target),
        target_evidence(original, target), _validate_target(target), [],
    )
    runs = _diff_runs(original, modded)
    ctx.incoming = _modded_branch_targets(ctx, runs)
    units = [_classify_run(ctx, start, end) for start, end in runs]
    _flag_branches_into_conflicts(ctx, units)
    counts = Counter(unit["kind"] for unit in units)
    out = bytes(ctx.out)
    report = {
        "schema": "syw2plus.esl2608-mod-port.v2",
        "original_sha256": ORIGINAL_SHA256,
        "target": ctx.target_info,
        "counts": dict(counts),
        "units": units,
        "warnings": ctx.warnings,
        "output_sha256": hashlib.sha256(out).hexdigest(),
        "limits": [
            "레지스터 상대 접근/계산된 포인터/루프 상한은 자동 재배치 불가(SUSPECT로만 표기)",
            "명령 길이를 바꾸는 모드 편집은 원본 명령 경계 기준으로만 디코드함",
            ".data 슬랙은 끝까지 명령으로 디코드되고 ret/jmp로 끝나거나 다른 모드 코드가 분기해 "
            "들어올 때만 코드 동굴로 취급(아니면 DATA+범위 검사, 미변환 주소는 출력 차단)",
            "런타임 미검증: Wine/게임 실행 없이 정적 변환만 수행",
        ],
    }
    return out, report


def _modded_branch_targets(ctx: _Ctx, runs: list[tuple[int, int]]) -> set[int]:
    """Direct branch targets of every modded run in a code section."""
    targets: set[int] = set()
    for start, end in runs:
        sec = _section_of(ctx.sections, start)
        if sec is None or sec.name not in CODE_SECTIONS:
            continue
        _begin, insns = _decode_run(ctx.modded, ctx.original, ctx.sections, start, end)
        for insn in insns:
            dest = _branch_target(insn)
            if dest is not None:
                targets.add(dest)
    return targets


def _flag_branches_into_conflicts(ctx: _Ctx, units: list[dict[str, Any]]) -> None:
    """A jump/call into a skipped CONFLICT run would land on our layer's bytes."""
    skipped = [
        (int(u["va"], 16), int(u["va"], 16) + u["length"])
        for u in units
        if u["kind"] == "CONFLICT" and u["va"].startswith("0x")
    ]
    for unit in units:
        if unit["kind"] == "CONFLICT":
            continue
        for src, dest in unit.pop("_branches", []):
            if not any(lo <= dest < hi for lo, hi in skipped):
                continue
            unit.setdefault("suspects", []).append(
                {"va": f"0x{src:08x}", "reason": "분기 대상이 적용되지 않은 CONFLICT 런 안",
                 "value": f"0x{dest:x}", "suggested": "수동 확인", "blocking": True}
            )
            if unit["kind"] == "PLAIN":
                unit["kind"] = "SUSPECT"
            ctx.warnings.append(
                {"code": "branch_into_conflict", "va": f"0x{src:08x}",
                 "message": f"0x{dest:08x}로 분기하지만 그 바이트는 CONFLICT로 적용되지 않음"}
            )
    for unit in units:
        unit.pop("_branches", None)


def _va_hex(sections: list[_Section], file_off: int) -> str:
    va = _file_to_va(sections, file_off)
    return f"0x{va:08x}" if va is not None else f"file+0x{file_off:x}"


def _conflict(base: dict[str, Any], ctx: _Ctx, start: int, end: int, owner: str,
              detail: str) -> dict[str, Any]:
    base.update(
        kind="CONFLICT",
        conflict={
            "owner": owner,
            "detail": detail,
            "target_hex": ctx.target[start:end].hex(),
            "modded_hex": ctx.modded[start:end].hex(),
        },
    )
    return base


def _ai_table_shape_problem(ctx: _Ctx, va: int, start: int, end: int) -> str | None:
    """The sync layer copies exactly 143 rows; the sentinel and what follows are fixed."""
    end_va = va + (end - start)
    if va < AI_SENTINEL_VA + AI_SHAPE_GUARD and end_va > AI_SENTINEL_VA:
        return "AI 표 센티널(0x4ECF22) 또는 그 뒤를 편집함: 동기화는 정확히 143행만 복사하므로 확장 불가"
    if _in_ai_table(va) or _in_ai_table(end_va - 1):
        first = max(0, (va - AI_TABLE_VA) // AI_ROW_STRIDE)
        last = min(AI_ROW_COUNT - 1, (end_va - 1 - AI_TABLE_VA) // AI_ROW_STRIDE)
        for row in range(first, last + 1):
            off = AI_TABLE_VA - IMAGE_BASE + row * AI_ROW_STRIDE
            if ctx.modded[off : off + 2] == b"\xfe\xff" and ctx.original[off : off + 2] != b"\xfe\xff":
                return f"{row}행에 0xFFFE를 써서 표가 일찍 끝남: 143행 뒤 상점 3행이 가려짐"
    return None


def _classify_run(ctx: _Ctx, start_off: int, end_off: int) -> dict[str, Any]:
    original, modded, target = ctx.original, ctx.modded, ctx.target
    va = _file_to_va(ctx.sections, start_off)
    sec = _section_of(ctx.sections, start_off)
    base: dict[str, Any] = {
        "va": _va_hex(ctx.sections, start_off),
        "section": sec.name.decode() if sec else "?",
        "length": end_off - start_off,
        "modded_hex": modded[start_off:end_off].hex(),
        "applied_offsets": [],
    }

    # CONFLICT: overlaps bytes our layers already changed.
    if any(target[i] != original[i] for i in range(start_off, end_off)):
        owner = _conflict_owner(original, target, ctx.sections, ctx.target_sections,
                                start_off, end_off)
        return _conflict(base, ctx, start_off, end_off, owner["owner"], owner["detail"])

    # CONFLICT: G1 runtime hook / contract site on a _G1 target.
    if ctx.target_info["is_g1"]:
        site = _g1_site_at(start_off, end_off, ctx.sections)
        if site is not None:
            return _conflict(base, ctx, start_off, end_off, f"G1 ({site[2]} 런타임 훅)",
                             f"원본 프롤로그 0x{site[0]:08x}는 DLL이 런타임에 후킹함")

    # CONFLICT: AI table shape edits the sync layer cannot carry.
    if va is not None:
        problem = _ai_table_shape_problem(ctx, va, start_off, end_off)
        if problem is not None:
            return _conflict(base, ctx, start_off, end_off, "AI 상점표 동기화(shop_table_sync_2608)",
                             problem)

    if sec is not None and sec.name in DATA_SECTIONS:
        if _is_added_code(original, ctx.sections, start_off, end_off):
            insns = _slack_cave_insns(ctx, start_off, end_off)
            if insns and _is_code_like(ctx, insns, start_off, end_off):
                base["data_cave"] = True
                return _classify_code(ctx, start_off, end_off, base)
        return _classify_data(ctx, va, start_off, end_off, base)

    return _classify_code(ctx, start_off, end_off, base)


def _slack_cave_insns(ctx: _Ctx, start_off: int, end_off: int) -> list[capstone.CsInsn] | None:
    """Decode a slack run as code, or None if it is not cleanly code.

    A diff run drops trailing bytes that happen to equal the zero slack (e.g. the
    high byte of a ``jmp`` rel32 or of a ``[0x00899034]`` operand), so the last
    instruction may extend past ``end_off`` -- but only over bytes that are zero
    in the original.
    """
    va = _file_to_va(ctx.sections, start_off)
    sec = _section_of(ctx.sections, start_off)
    if va is None or sec is None:
        return None
    limit = min(sec.file_end, end_off + 15)
    insns: list[capstone.CsInsn] = []
    cursor = start_off
    for insn in _MD.disasm(ctx.modded[start_off:limit], va):
        insns.append(insn)
        cursor += insn.size
        if cursor >= end_off:
            break
    if cursor < end_off or any(ctx.original[end_off:cursor]):
        return None
    return insns


def _is_code_like(ctx: _Ctx, insns: list[capstone.CsInsn], start_off: int, end_off: int) -> bool:
    """Ends in ret/jmp, or another modded run branches into it."""
    last = insns[-1]
    if last.group(capstone.CS_GRP_RET) or last.mnemonic == "jmp":
        return True
    lo = _file_to_va(ctx.sections, start_off)
    assert lo is not None
    hi = lo + (end_off - start_off)
    return any(lo <= dest < hi for dest in ctx.incoming)


def _region_windows(ctx: _Ctx, start_off: int, end_off: int, handled: set[int],
                    reason: str) -> list[dict[str, Any]]:
    """Every modder-created 4-byte window that lands in a relocated range."""
    found = []
    for w in range(max(0, start_off - 3), end_off):
        if w in handled or w + 4 > len(ctx.modded):
            continue
        value = struct.unpack_from("<I", ctx.modded, w)[0]
        if value == struct.unpack_from("<I", ctx.original, w)[0]:
            continue
        mapped = REGION_MAP.inside(value)
        if mapped is not None:
            found.append({"va": _va_hex(ctx.sections, w), "reason": reason,
                          "value": f"0x{value:x}", "suggested": f"0x{mapped[1]:x}",
                          "blocking": True})
    return found


def _classify_data(ctx: _Ctx, va: int | None, start_off: int, end_off: int,
                   base: dict[str, Any]) -> dict[str, Any]:
    ctx.out[start_off:end_off] = ctx.modded[start_off:end_off]
    base.update(kind="DATA", applied_offsets=list(range(start_off, end_off)))
    suspects = _region_windows(ctx, start_off, end_off, set(),
                               "데이터 안의 4바이트 값이 재배치 범위(포인터일 수 있음)")
    if suspects:
        base.update(kind="SUSPECT", suspects=suspects)
    if va is not None and (_in_ai_table(va) or _in_ai_table(va + base["length"] - 1)):
        base["ai_table"] = True
        if not ctx.target_info["sync_layer"]:
            ctx.warnings.append(
                {"code": "ai_table_without_sync", "va": base["va"],
                 "message": "AI 테이블(0x4EC514)을 편집했으나 target에 동기화 레이어가 없음; "
                 "AI는 .shopai 사본을 읽으므로 반영되지 않을 수 있음"}
            )
    return base


def _is_exec_va(ctx: _Ctx, va: int) -> bool:
    sec = _section_for_va(ctx.target_sections, va)
    return sec is not None and bool(sec.characteristics & IMAGE_SCN_MEM_EXECUTE)


def _classify_code(ctx: _Ctx, start_off: int, end_off: int,
                   base: dict[str, Any]) -> dict[str, Any]:
    sections, evidence = ctx.sections, ctx.evidence
    sync_layer = ctx.target_info["sync_layer"]
    begin, insns = _decode_run(ctx.modded, ctx.original, sections, start_off, end_off)
    begin_va = _file_to_va(sections, begin)
    relocations: list[dict[str, Any]] = []
    suspects: list[dict[str, Any]] = []
    reloc_writes: list[tuple[int, int]] = []  # (field_off, new_value)
    handled: set[int] = set()
    branches: list[tuple[int, int]] = []
    span_end = begin

    def touched(field_off: int, size: int) -> bool:
        return field_off < end_off and field_off + size > start_off

    for insn in insns:
        insn_off = begin + (insn.address - begin_va)
        span_end = max(span_end, insn_off + insn.size)
        if not touched(insn_off, insn.size):
            continue
        dest = _branch_target(insn)
        if dest is not None:
            branches.append((insn.address, dest))
            if not _is_exec_va(ctx, dest):
                suspects.append({"va": f"0x{insn.address:08x}", "value": f"0x{dest:x}",
                                 "reason": "분기 대상이 실행 섹션 밖", "suggested": "수동 확인",
                                 "blocking": True})
        for fld, value, mnemonic, is_imm in _operand_fields(insn):
            field_off = insn_off + fld
            if not touched(field_off, 4):
                continue
            handled.add(field_off)
            auto = _auto_target(value, evidence, sync_layer)
            qualifies = (not is_imm) or mnemonic in ("mov", "lea")
            if auto is not None and qualifies:
                region, new_value = auto
                reloc_writes.append((field_off, new_value))
                relocations.append(
                    {"va": f"0x{insn.address:08x}", "region": region,
                     "old": f"0x{value:08x}", "new": f"0x{new_value:08x}"}
                )
                if region == "ai_table":
                    ctx.warnings.append(
                        {"code": "ai_table_ref_without_sync", "va": f"0x{insn.address:08x}",
                         "message": "동기화 레이어 없는 target이라 AI 표 참조를 .shopai 사본으로 옮김; "
                         "동기화 레이어를 먼저 적용하는 것을 권장"}
                    )
            elif auto is not None:
                suspects.append(
                    {"va": f"0x{insn.address:08x}", "reason": "주소형 operand이나 자동 재배치 비대상",
                     "value": f"0x{value:x}", "suggested": f"0x{auto[1]:x}", "blocking": True}
                )
            elif value in CONST_SUSPECTS:
                suspects.append(
                    {"va": f"0x{insn.address:08x}", "reason": "재배치 상수 사전 일치",
                     "value": f"0x{value:x}", "suggested": f"0x{CONST_SUSPECTS[value]:x}",
                     "blocking": False}
                )
        for fld, size, value in _small_imms(insn):
            if touched(insn_off + fld, size) and value in CONST_SUSPECTS:
                suspects.append(
                    {"va": f"0x{insn.address:08x}", "reason": "재배치 상수 사전 일치(imm8/16)",
                     "value": f"0x{value:x}", "suggested": f"0x{CONST_SUSPECTS[value]:x}",
                     "blocking": False}
                )

    # Safety net for decode misalignment: any modder-made 4-byte window in a
    # relocated range that no decoded field accounted for.
    suspects.extend(_region_windows(ctx, start_off, end_off, handled,
                                    "디코드 필드 밖 4바이트 창이 재배치 범위(명령 경계 확인 필요)"))

    applied = set(range(start_off, end_off))
    ctx.out[start_off:end_off] = ctx.modded[start_off:end_off]
    for field_off, new_value in reloc_writes:
        struct.pack_into("<I", ctx.out, field_off, new_value)
        applied.update(range(field_off, field_off + 4))

    if relocations:
        base["kind"] = "RELOC"
        base["relocations"] = relocations
    elif suspects:
        base["kind"] = "SUSPECT"
    else:
        base["kind"] = "PLAIN"
    if suspects:
        base["suspects"] = suspects
    base["applied_offsets"] = sorted(applied)
    base["_branches"] = branches
    # The covering instruction may hold target-relocated bytes we deliberately kept.
    base["kept_target_bytes"] = any(
        off not in applied and ctx.out[off] != ctx.original[off] for off in range(begin, span_end)
    )
    return base


# --------------------------------------------------------------------------- #
# Report rendering + IO
# --------------------------------------------------------------------------- #
class PortRefusedError(RuntimeError):
    """Raised when the port has CONFLICTs/warnings and ``force`` was not given."""


def render_markdown(report: dict[str, Any]) -> str:
    counts = report["counts"]
    lines = [
        "# ESL2608 모드 포팅 요약",
        "",
        f"- 원본 SHA256: `{report['original_sha256']}`",
        f"- target: {report['target']['variant']} "
        f"(G1={report['target']['is_g1']}, 동기화레이어={report['target']['sync_layer']})",
        f"- 출력 SHA256: `{report['output_sha256']}`",
        f"- 변경 런 분류: {counts or '없음'}",
        "",
        "## 분류별 상세",
    ]
    for unit in report["units"]:
        lines.append(f"- [{unit['kind']}] {unit['va']} ({unit['section']}, {unit['length']}B)")
        if unit["kind"] == "CONFLICT":
            c = unit["conflict"]
            lines.append(f"    - 소유 레이어: {c['owner']} {c['detail']}")
            lines.append(f"    - target=`{c['target_hex']}` modded=`{c['modded_hex']}`")
        for rel in unit.get("relocations", []):
            lines.append(f"    - RELOC {rel['region']} {rel['old']} -> {rel['new']}")
        for sus in unit.get("suspects", []):
            mark = " [출력 차단]" if sus.get("blocking") else ""
            lines.append(f"    - SUSPECT{mark} {sus['value']} (권장 {sus['suggested']}) {sus['reason']}")
    if report["warnings"]:
        lines.append("")
        lines.append("## 경고")
        for w in report["warnings"]:
            lines.append(f"- {w['code']} @ {w['va']}: {w['message']}")
    if report["limits"]:
        lines.append("")
        lines.append("## 알려진 한계")
        for limit in report["limits"]:
            lines.append(f"- {limit}")
    return "\n".join(lines) + "\n"


def _write_all_or_nothing(payloads: list[tuple[Path, bytes]]) -> None:
    """Exclusive-create every file or none: temp files first, then hard links.

    Reports are listed before the EXE, so a failure never leaves an EXE
    without its report.
    """
    for final, _data in payloads:
        if final.exists():
            raise FileExistsError(f"refusing to overwrite existing file: {final}")
    temps: list[Path] = []
    linked: list[Path] = []
    try:
        for final, data in payloads:
            fd, name = tempfile.mkstemp(dir=final.parent, prefix=f"{final.name}.", suffix=".tmp")
            temps.append(Path(name))
            with os.fdopen(fd, "wb") as handle:
                handle.write(data)
            os.chmod(name, 0o644)
        for (final, _data), temp in zip(payloads, temps):
            os.link(temp, final)  # fails if final appeared meanwhile
            linked.append(final)
    except BaseException:
        for path in linked:
            path.unlink(missing_ok=True)
        raise
    finally:
        for temp in temps:
            temp.unlink(missing_ok=True)


def run(original_path: Path, modded_path: Path, target_path: Path, output_path: Path,
        *, dry_run: bool = False, force: bool = False) -> dict[str, Any]:
    inputs = {p.resolve() for p in (original_path, modded_path, target_path)}
    if output_path.resolve() in inputs:
        raise ValueError("output path가 입력(input) 파일과 같음; 덮어쓰기 거부")
    out_bytes, report = port_bytes(
        original_path.read_bytes(), modded_path.read_bytes(), target_path.read_bytes()
    )
    if dry_run:
        report["dry_run"] = True
        return report
    left_as_is = sum(
        1 for unit in report["units"] for sus in unit.get("suspects", []) if sus["blocking"]
    )
    blocking = report["counts"].get("CONFLICT", 0) + len(report["warnings"]) + left_as_is
    if blocking and not force:
        raise PortRefusedError(
            f"CONFLICT {report['counts'].get('CONFLICT', 0)}건/경고 {len(report['warnings'])}건/"
            f"재배치 범위 주소 미변환 {left_as_is}건: "
            "--dry-run으로 보고서를 확인한 뒤 --force로만 출력 가능"
        )
    report["forced"] = bool(blocking)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    json_bytes = (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    _write_all_or_nothing(
        [
            (output_path.with_suffix(output_path.suffix + ".json"), json_bytes),
            (output_path.with_suffix(output_path.suffix + ".md"),
             render_markdown(report).encode("utf-8")),
            (output_path, out_bytes),
        ]
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="pinned original 2608 EXE")
    parser.add_argument("modded", type=Path, help="OllyDbg-modded 2608 EXE")
    parser.add_argument("target", type=Path, help="pinned R5 / R5_G1 deliverable")
    parser.add_argument("output", type=Path, help="output path (exclusive create)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true",
                        help="write even when CONFLICTs/warnings exist (conflicts stay unapplied)")
    args = parser.parse_args()
    report = run(args.original, args.modded, args.target, args.output,
                 dry_run=args.dry_run, force=args.force)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
