#!/usr/bin/env python3
"""G2 layer 4 for ESL 2610-line EXEs: save/load of the relocated unit state.

Port of the accepted stock G2 persistence (``g2_full_capacity_persistence_v1``
+ ``..._compat_v1``) to the 2610 line.  The stock save writes the bulk block
(which still holds the *old* existence/age/category/active arrays) and then
the live UnitStruct records (that walk is raised to 4093 by layer 1).  The
bulk writer/reader calls go through wrappers in ``.g2code`` that, after the
original transfer, stream:

* a 32-byte manifest (``G2MF``, version, layout hash, the five sidecar sizes);
* the five relocated arrays (existence, age, category A/B, active list).

The 2610 modules' own blobs are grown by layer 3 (``KIL1`` kill log, ``PSN2``
portrait blob): an expanded size is rejected by the official EXE, which then
clears/rebuilds that state as for a damaged blob.  ``KIL1`` blobs of the
official size are converted here (old kill_log -> slots 0..1199, slots
1200.. zeroed, the 256x16 table moved to its new place); official ``PSN2``
blobs fail the size check and take the module's own rebuild path.

The save header (+0x38) carries ``S2P2`` and the layout hash:

* no marker (official save): skip the manifest/sidecars and copy the stock
  arrays the bulk block just restored into the relocated ones (zero tail);
* marker with this layout: read the manifest, verify it, read the sidecars;
* marker of another layout: read the manifest and *skip* its sidecars (sizes
  from the manifest, each bounded) so the stream stays in step, then treat
  the save like an official one.  The engine has no failure path once a load
  has started, so this is the safe refusal.
"""

from __future__ import annotations

import hashlib
import struct
from types import SimpleNamespace
from typing import Any

from patches.esl2610 import g2_reloc_2610, g2_state_2610, pe_extend
from patches.population.g2_full_capacity_persistence_compat_v1 import (
    LOAD_HEADER_CALL_VA,
    SAVE_HEADER_CALL_VA,
    _emit_legacy_copy_wrapper,
)
from patches.population.g2_full_capacity_persistence_v1 import (
    LOAD_CALL_VA,
    LOAD_STREAM_FN,
    SAVE_CALL_VA,
    SAVE_STREAM_FN,
    _call,
)

SECTION_NAME = b".g2code"
MARKER_OFFSET = 0x38
MARKER_A = int.from_bytes(b"S2P2", "little")
MANIFEST_MAGIC = int.from_bytes(b"G2MF", "little")
MANIFEST_VERSION = 1
SKIP_MAX = 0x4000  # largest sidecar a foreign manifest may make us skip
SAVE_OFF, LOAD_OFF, SAVE_HDR_OFF, LOAD_HDR_OFF, LEGACY_OFF = 0x000, 0x100, 0x300, 0x380, 0x400
KILL_OFF, MANIFEST_OFF, PSN_OFF, ZERO_OFF = 0x500, 0x600, 0x680, 0x780
CODE_SIZE = 0x800
SCRATCH_BYTES = 0x20 + SKIP_MAX  # manifest buffer + skip buffer (in .g2bss)

# .kills KIL1 loader: "cmp dword [ebp-8],0xA600 ; jne exit" (9 bytes)
KIL1_SIZE_CHECK_VA = 0x0115B485
KIL1_SIZE_CHECK_OLD = bytes.fromhex("817df800a60000" "7540")
KIL1_READ_VA = 0x0115B48E  # push edi ; push 1 ; push size ; push stage ; call read
KIL1_EXIT_VA = 0x0115B4CE
KIL1_HASH_FN = 0x0115B3B7  # FNV-1a(esi=buf, ecx=len) -> eax
KIL1_LEGACY_BYTES = 0xA600
KILL_LOG_OLD_BYTES = 0x9600  # 1200 x 0x20
KILL_TABLE_BYTES = 0x1000

# .psncode PSN2 loader: "cmp dword [hdr+8],size ; jne fallback" (10 + 2 bytes).
# On an official save this check fails for the grown size, and the only path
# to the KIL1 load (0x1144880 -> 0x4EBFC0 restore -> 0x115B4D2 -> KIL1) is the
# PSN2 success path, so the official 0x16000 blob is converted here.
PSN2_SIZE_CHECK_VA = 0x01091108
PSN2_GROWN_VA = 0x01091114  # push esi ; push 1 ; push size ; push stage ; call read
PSN2_FALLBACK_VA = 0x01091155  # rebuild loop, then return (no KIL1)
PSN2_SUCCESS_VA = 0x01091198  # jmp 0x1144880
PSN2_LEGACY_BYTES = 0x16000
PSN2_CACHE_OFF = 0xC000  # psn_cache inside the blob
PSN2_CACHE_OLD = 0x4B00  # 1200 x 0x10


def _regions(six_base: int) -> list[SimpleNamespace]:
    """The five relocated arrays (old/new spans) at this build's base."""
    geo = g2_reloc_2610._GEOMETRY  # noqa: SLF001
    pack = g2_reloc_2610._PACK_BASE  # noqa: SLF001
    return [SimpleNamespace(
        name=r.name, old_start=r.old_start, old_end=r.old_end,
        new_start=six_base + (r.new_start - pack), new_end=six_base + (r.new_end - pack))
        for r in geo.regions[1:]]


def layout_hash(sidecars: list[tuple[int, int]], starts: dict[str, int]) -> int:
    """32-bit FNV-1a over everything a save of this layout depends on."""
    text = ";".join(f"{a:x}:{s:x}" for a, s in sidecars)
    text += f";cap={g2_reloc_2610.CAPACITY};kill={g2_state_2610.blob_length(
        (g2_state_2610.KILL_FROM, g2_state_2610.KILL_TO), starts):x}"
    text += f";psn={g2_state_2610.blob_length(
        (g2_state_2610.PSN_FROM, g2_state_2610.PSN_TO), starts):x}"
    h = 0x811C9DC5
    for byte in text.encode():
        h = ((h ^ byte) * 0x01000193) & 0xFFFFFFFF
    return h


class _Asm:
    """Tiny x86 emitter with rel32 labels (all jumps near: no rel8 overflow)."""

    def __init__(self, va: int) -> None:
        self.va = va
        self.code = bytearray()
        self.labels: dict[str, int] = {}
        self.fixups: list[tuple[int, str]] = []

    def raw(self, hexstr: str) -> None:
        self.code.extend(bytes.fromhex(hexstr))

    def imm(self, value: int) -> None:
        self.code.extend(struct.pack("<I", value & 0xFFFFFFFF))

    def call(self, target: int) -> None:
        self.code.extend(_call(self.va + len(self.code), target))

    def jmp_abs(self, target: int) -> None:
        self.code.extend(b"\xe9" + struct.pack("<i", target - (self.va + len(self.code) + 5)))

    def jcc(self, cc: str, label: str) -> None:
        ops = {"jmp": b"\xe9", "jne": b"\x0f\x85", "je": b"\x0f\x84", "ja": b"\x0f\x87"}
        self.code.extend(ops[cc])
        self.fixups.append((len(self.code), label))
        self.code.extend(b"\0\0\0\0")

    def label(self, name: str) -> None:
        self.labels[name] = len(self.code)

    def stream(self, fn: int, buffer: int | None, size: int | None) -> None:
        """fn(buffer, size, 1, stream) -- or the wrapped call's own arguments."""
        if buffer is None:
            self.raw("ff7514ff7510ff750cff7508")
        else:
            if size is None:
                raise ValueError("explicit stream buffer requires a size")
            self.raw("ff75146a0168")
            self.imm(size)
            self.raw("68")
            self.imm(buffer)
        self.call(fn)
        self.raw("83c410")

    def done(self, limit: int) -> bytes:
        for pos, name in self.fixups:
            struct.pack_into("<i", self.code, pos, self.labels[name] - (pos + 4))
        if len(self.code) > limit:
            raise ValueError(f"wrapper is {len(self.code)} bytes, limit {limit}")
        return bytes(self.code)


def _save_wrapper(va: int, manifest_va: int, sidecars: list[tuple[int, int]]) -> bytes:
    a = _Asm(va)
    a.raw("5589e553")  # push ebp ; mov ebp,esp ; push ebx
    a.stream(SAVE_STREAM_FN, None, None)
    a.raw("89c3")  # mov ebx,eax (the original transfer's result)
    a.stream(SAVE_STREAM_FN, manifest_va, 0x20)
    for address, size in sidecars:
        a.stream(SAVE_STREAM_FN, address, size)
    a.raw("89d85bc9c3")  # mov eax,ebx ; pop ebx ; leave ; ret
    return a.done(0x100)


def _load_wrapper(va: int, flag_va: int, scratch: int, manifest_va: int, fallback_va: int,
                  sidecars: list[tuple[int, int]], zero_va: int) -> bytes:
    a = _Asm(va)
    a.raw("5589e5535657")  # push ebp ; mov ebp,esp ; push ebx ; push esi ; push edi
    a.stream(LOAD_STREAM_FN, None, None)
    a.raw("89c3")
    a.raw("833d")
    a.imm(flag_va)
    a.raw("00")  # cmp dword [flag],0
    a.jcc("je", "legacy")
    a.stream(LOAD_STREAM_FN, scratch, 0x20)  # the manifest
    a.raw("833d")
    a.imm(flag_va)
    a.raw("01")  # this layout?
    a.jcc("jne", "skip")
    a.raw("fcbe")
    a.imm(scratch)
    a.raw("bf")
    a.imm(manifest_va)
    a.raw("b908000000f3a7")  # mov ecx,8 ; repe cmpsd
    a.jcc("jne", "skip")
    for address, size in sidecars:
        a.stream(LOAD_STREAM_FN, address, size)
    a.jcc("jmp", "done")
    a.label("skip")  # another layout: skip its sidecars by the manifest's sizes
    a.raw("813d")
    a.imm(scratch)
    a.imm(MANIFEST_MAGIC)
    a.jcc("jne", "legacy")
    a.raw("31f6")  # xor esi,esi
    a.label("skip_next")
    a.raw("8b04b5")
    a.imm(scratch + 12)  # mov eax,[esi*4+scratch+12]
    a.raw("3d")
    a.imm(SKIP_MAX)  # cmp eax,SKIP_MAX
    a.jcc("ja", "legacy")
    a.raw("ff75146a0150")  # push stream ; push 1 ; push eax
    a.raw("68")
    a.imm(scratch + 0x20)
    a.call(LOAD_STREAM_FN)
    a.raw("83c41046")  # add esp,16 ; inc esi
    a.raw("83fe05")  # cmp esi,5
    a.jcc("jne", "skip_next")
    a.label("legacy")
    a.call(fallback_va)
    a.label("done")
    a.call(zero_va)
    a.raw("89d85f5e5bc9c3")  # mov eax,ebx ; pop edi ; pop esi ; pop ebx ; leave ; ret
    return a.done(0x200)


def _save_header(va: int, layout: int) -> bytes:
    a = _Asm(va)
    a.raw("8b442404")  # mov eax,[esp+4]
    a.raw("c740" + f"{MARKER_OFFSET:02x}")
    a.imm(MARKER_A)
    a.raw("c740" + f"{MARKER_OFFSET + 4:02x}")
    a.imm(layout)
    a.jmp_abs(SAVE_STREAM_FN)
    return a.done(0x80)


def _load_header(va: int, flag_va: int, layout: int) -> bytes:
    """flag: 0 official save, 1 this layout, 2 an expanded save of another layout."""
    a = _Asm(va)
    a.raw("5589e553")
    a.stream(LOAD_STREAM_FN, None, None)
    a.raw("89c38b4d08")  # mov ebx,eax ; mov ecx,[ebp+8]
    a.raw("c705")
    a.imm(flag_va)
    a.imm(0)
    a.raw("8179" + f"{MARKER_OFFSET:02x}")
    a.imm(MARKER_A)
    a.jcc("jne", "out")
    a.raw("c705")
    a.imm(flag_va)
    a.imm(2)
    a.raw("8179" + f"{MARKER_OFFSET + 4:02x}")
    a.imm(layout)
    a.jcc("jne", "out")
    a.raw("c705")
    a.imm(flag_va)
    a.imm(1)
    a.label("out")
    a.raw("89d85bc9c3")
    return a.done(0x80)


def _kil1_loader(va: int, new_size: int, stage: int, kill_log: int, table: int) -> bytes:
    """Replaces the KIL1 size check: grown size loads as before; the official
    0xA600 blob is read, hash-checked and converted to the grown layout."""
    a = _Asm(va)
    a.raw("817df8")
    a.imm(new_size)  # cmp dword [ebp-8],new_size
    a.jcc("je", "grown")
    a.raw("817df8")
    a.imm(KIL1_LEGACY_BYTES)
    a.jcc("jne", "exit")
    a.raw("576a0168")
    a.imm(KIL1_LEGACY_BYTES)  # push edi ; push 1 ; push 0xA600
    a.raw("68")
    a.imm(stage)
    a.call(LOAD_STREAM_FN)
    a.raw("83c41083f801")  # add esp,16 ; cmp eax,1
    a.jcc("jne", "exit")
    a.raw("be")
    a.imm(stage)
    a.raw("b9")
    a.imm(KIL1_LEGACY_BYTES)
    a.call(KIL1_HASH_FN)
    a.raw("3b45fc")  # cmp eax,[ebp-4]
    a.jcc("jne", "exit")
    a.raw("fcbe")
    a.imm(stage)
    a.raw("bf")
    a.imm(kill_log)
    a.raw("b9")
    a.imm(KILL_LOG_OLD_BYTES // 4)
    a.raw("f3a5")  # old kill_log 0..1199
    a.raw("31c0bf")
    a.imm(kill_log + KILL_LOG_OLD_BYTES)
    a.raw("b9")
    a.imm((table - kill_log - KILL_LOG_OLD_BYTES) // 4)
    a.raw("f3ab")  # 1200..
    a.raw("be")
    a.imm(stage + KILL_LOG_OLD_BYTES)
    a.raw("bf")
    a.imm(table)
    a.raw("b9")
    a.imm(KILL_TABLE_BYTES // 4)
    a.raw("f3a5")  # the 256x16 table
    a.label("exit")
    a.jmp_abs(KIL1_EXIT_VA)
    a.label("grown")
    a.jmp_abs(KIL1_READ_VA)
    return a.done(0x100)


def _psn2_loader(va: int, hdr: int, new_size: int, stage: int, blob: int) -> bytes:
    """Grown PSN2 loads as before; the official 0x16000 blob is read, FNV-1a
    checked and re-laid out (prefix, 1200 cache entries, zero to 4093, tail)."""
    a = _Asm(va)
    a.raw("813d")
    a.imm(hdr + 8)
    a.imm(new_size)
    a.jcc("je", "grown")
    a.raw("813d")
    a.imm(hdr + 8)
    a.imm(PSN2_LEGACY_BYTES)
    a.jcc("jne", "fallback")
    a.raw("566a0168")
    a.imm(PSN2_LEGACY_BYTES)
    a.raw("68")
    a.imm(stage)  # push esi ; 1 ; size ; stage
    a.call(LOAD_STREAM_FN)
    a.raw("83c41083f801")  # add esp,16 ; cmp eax,1
    a.jcc("jne", "fallback")
    # FNV-1a over the official length (0x1091040 hashes the grown length)
    a.raw("56be")
    a.imm(stage)
    a.raw("b9")
    a.imm(PSN2_LEGACY_BYTES)
    a.raw("b8c59d1c81")  # mov eax,0x811C9DC5
    a.label("fnv")
    a.raw("0fb61631d069c09301000146" "49")  # movzx edx,[esi]; xor eax,edx; imul eax,eax,0x1000193; inc esi; dec ecx
    a.jcc("jne", "fnv")
    a.raw("5e3b05")
    a.imm(hdr + 0xC)  # pop esi ; cmp eax,[hdr+0xC]
    a.jcc("jne", "fallback")
    tail = PSN2_LEGACY_BYTES - PSN2_CACHE_OFF - PSN2_CACHE_OLD
    grown = new_size - PSN2_LEGACY_BYTES
    a.raw("5657fcbe")
    a.imm(stage)
    a.raw("bf")
    a.imm(blob)
    a.raw("b9")
    a.imm((PSN2_CACHE_OFF + PSN2_CACHE_OLD) // 4)
    a.raw("f3a5")
    a.raw("31c0b9")
    a.imm(grown // 4)
    a.raw("f3ab")
    a.raw("b9")
    a.imm(tail // 4)
    a.raw("f3a5")  # esi already at the official tail
    a.raw("5f5e")
    a.jmp_abs(PSN2_SUCCESS_VA)
    a.label("fallback")
    a.jmp_abs(PSN2_FALLBACK_VA)
    a.label("grown")
    a.jmp_abs(PSN2_GROWN_VA)
    return a.done(0x100)


def _zero_old(va: int, regions: list[SimpleNamespace]) -> bytes:
    """Clear the stock arrays the bulk block restores (nothing uses them any
    more; left filled they hand stale units to anything reading 0x8990C8)."""
    a = _Asm(va)
    a.raw("575150fc31c0")  # push edi ; push ecx ; push eax ; cld ; xor eax,eax
    for r in regions:
        size = r.old_end - r.old_start
        a.raw("bf")
        a.imm(r.old_start)
        a.raw("b9")
        a.imm(size // 4)
        a.raw("f3ab")
        if size % 4:
            a.raw("66ab")
    a.raw("58595fc3")
    return a.done(0x80)


def apply(image: bytes, six_base: int, state_base: int, flag_va: int,
          scratch_va: int, *,
          state_profile: tuple[g2_state_2610.StateSection, ...] | None = None,
          code_reserved_size: int | None = None) -> tuple[bytes, dict[str, Any]]:
    """Add ``.g2code`` with the wrappers and redirect the stream calls."""
    if SECTION_NAME in pe_extend.section_names(image):
        raise ValueError("G2 persistence is already applied")
    starts = g2_state_2610.layout(state_base, state_profile)
    regions = _regions(six_base)
    sidecars = [(r.new_start, r.new_end - r.new_start) for r in regions]
    layout = layout_hash(sidecars, starts)
    manifest = struct.pack("<8I", MANIFEST_MAGIC, MANIFEST_VERSION, layout,
                           *[size for _, size in sidecars])
    code_va = pe_extend.IMAGE_BASE + struct.unpack_from(
        "<I", image, struct.unpack_from("<I", image, 0x3C)[0] + 24 + 56)[0]
    kill_new = g2_state_2610.map_value(g2_state_2610.KILL_FROM, starts, state_profile=state_profile)
    stage_new = g2_state_2610.map_value(g2_state_2610.KILL_TO, starts, state_profile=state_profile)
    table_new = g2_state_2610.map_value(0x01165600, starts, state_profile=state_profile)
    new_kill = stage_new - kill_new
    psn_blob = g2_state_2610.map_value(g2_state_2610.PSN_FROM, starts, state_profile=state_profile)
    psn_stage = g2_state_2610.map_value(g2_state_2610.PSN_TO, starts, state_profile=state_profile)
    psn_hdr = g2_state_2610.map_value(0x0112C000, starts, state_profile=state_profile)
    psn_new = psn_stage - psn_blob
    if code_reserved_size is not None and code_reserved_size < 0x1000:
        raise ValueError("profile-owned .g2code reservation must be at least 0x1000 bytes")
    blob = bytearray(CODE_SIZE)
    for off, code in (
        (SAVE_OFF, _save_wrapper(code_va + SAVE_OFF, code_va + MANIFEST_OFF, sidecars)),
        (LOAD_OFF, _load_wrapper(code_va + LOAD_OFF, flag_va, scratch_va, code_va + MANIFEST_OFF,
                                 code_va + LEGACY_OFF, sidecars, code_va + ZERO_OFF)),
        (PSN_OFF, _psn2_loader(code_va + PSN_OFF, psn_hdr, psn_new, psn_stage, psn_blob)),
        (ZERO_OFF, _zero_old(code_va + ZERO_OFF, regions)),
        (SAVE_HDR_OFF, _save_header(code_va + SAVE_HDR_OFF, layout)),
        (LOAD_HDR_OFF, _load_header(code_va + LOAD_HDR_OFF, flag_va, layout)),
        (LEGACY_OFF, _emit_legacy_copy_wrapper(regions)),
        (KILL_OFF, _kil1_loader(code_va + KILL_OFF, new_kill, stage_new, kill_new, table_new)),
        (MANIFEST_OFF, manifest),
    ):
        blob[off : off + len(code)] = code
    if code_reserved_size is not None:
        if code_reserved_size & 0xFFF:
            raise ValueError("profile-owned .g2code reservation must be file/section aligned")
        blob.extend(b"\0" * (code_reserved_size - len(blob)))
    out = bytearray(pe_extend.add_section(image, SECTION_NAME, bytes(blob),
                                          max(0x1000, code_reserved_size or 0x1000),
                                          pe_extend.CODE_RX))
    if pe_extend.section_va(out, SECTION_NAME) != code_va:
        raise ValueError(".g2code was not placed at the first free RVA")
    for call_va, old_target, new_off in (
        (SAVE_CALL_VA, SAVE_STREAM_FN, SAVE_OFF),
        (LOAD_CALL_VA, LOAD_STREAM_FN, LOAD_OFF),
        (SAVE_HEADER_CALL_VA, SAVE_STREAM_FN, SAVE_HDR_OFF),
        (LOAD_HEADER_CALL_VA, LOAD_STREAM_FN, LOAD_HDR_OFF),
    ):
        off = pe_extend.va_to_offset(bytes(out), call_va)
        if bytes(out[off : off + 5]) != _call(call_va, old_target):
            raise ValueError(f"stream callsite 0x{call_va:08x} old bytes mismatch")
        out[off : off + 5] = _call(call_va, code_va + new_off)
    off = pe_extend.va_to_offset(bytes(out), KIL1_SIZE_CHECK_VA)
    if bytes(out[off : off + 9]) != KIL1_SIZE_CHECK_OLD:
        raise ValueError("KIL1 size check old bytes mismatch")
    out[off : off + 9] = (b"\xe9" + struct.pack("<i", code_va + KILL_OFF - (KIL1_SIZE_CHECK_VA + 5))
                          + b"\x90" * 4)
    off = pe_extend.va_to_offset(bytes(out), PSN2_SIZE_CHECK_VA)
    expected = (b"\x81\x3d" + struct.pack("<I", psn_hdr + 8) + struct.pack("<I", psn_new)
                + b"\x75\x41")
    if bytes(out[off : off + 12]) != expected:
        raise ValueError("PSN2 size check bytes (after layer 3) mismatch")
    out[off : off + 12] = (b"\xe9" + struct.pack("<i", code_va + PSN_OFF - (PSN2_SIZE_CHECK_VA + 5))
                           + b"\x90" * 7)
    result = pe_extend._with_checksum(bytes(out))  # noqa: SLF001
    return result, {
        "schema": "syw2plus.esl2610.g2-persist.v2",
        "g2code_va": hex(code_va),
        "g2code_reserved_size": hex(code_reserved_size or 0x1000),
        "flag_va": hex(flag_va),
        "scratch_va": hex(scratch_va),
        "marker": "S2P2",
        "layout_hash": hex(layout),
        "sidecars": [{"address": hex(a), "size": hex(s)} for a, s in sidecars],
        "psn2": {"grown_size": hex(psn_new), "legacy_size": hex(PSN2_LEGACY_BYTES),
                 "blob": hex(psn_blob), "stage": hex(psn_stage), "header": hex(psn_hdr)},
        "kil1": {"grown_size": hex(new_kill), "legacy_size": hex(KIL1_LEGACY_BYTES),
                 "kill_log": hex(kill_new), "table": hex(table_new), "stage": hex(stage_new)},
        "candidate_sha256": hashlib.sha256(result).hexdigest(),
    }
