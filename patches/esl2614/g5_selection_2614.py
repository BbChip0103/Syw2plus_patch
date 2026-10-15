#!/usr/bin/env python3
"""2614-only continuation of OUR 20-entry chunked selection-order algorithm.

The official 2614 helper at 0x112DC10 already turns one <=20-entry window into
one native command packet. We preserve its first three windows and append two
count-bounded windows at 0x112DBD8. Unlike a cap-only switch this retains the
20-unit packet contract and processes selection entries 0..99 in five chunks.
"""
from __future__ import annotations

import hashlib
import struct
from typing import Any

import keystone
import pefile

from patches.esl2610 import g2_reloc_2610, g2_state_2610, pe_extend

OFFICIAL_SHA256 = "ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf"
HOOK_VA = 0x0112DBD8
HOOK_OLD = bytes.fromhex("e9 e3 02 00 00")  # official jump to 0x112DEC0 tail
CONTINUATION_VA = 0x0112DEC0
CHUNK_HELPER_VA = 0x0112DC10
SELECTION_COUNT_VA = 0x00899024
WINDOW_BYTES = 20 * 4
G2CODE = b".g2code"
ORDER_WRAPPER_OFFSET = 0x800
SAVE_WRAPPER_OFFSET = 0x900
SAVE_OPTIONAL_WRAPPER_OFFSET = 0x980
LOAD_STAGE_WRAPPER_OFFSET = 0xA00
MAGIC_OFFSET = 0xB00
LOAD_BEGIN_WRAPPER_OFFSET = 0xB04
LOAD_COMMIT_WRAPPER_OFFSET = 0xB60
SECTION_BYTES = 0x1000
# OUR v2/v6 control-group overflow algorithm, re-hosted in this candidate's
# owned section. Native PlayerStruct storage remains 20 entries/0x50 stride;
# entries 21..100 are represented by persisted unit+0x344 tags.
GROUP_H1_SITE = 0x00445D4E
GROUP_H1_OFFICIAL_OLD = bytes.fromhex("8b542414bb04406001")
GROUP_H2_SITE = 0x00445DCB
GROUP_H2_OLD = bytes.fromhex("8b44241066c7000000")
GROUP3_END_SITE = 0x00445E0B
GROUP3_END_OLD_BASE = 0x01604054
GROUP_H3_SITE = 0x00445ED1
GROUP_H3_OLD = bytes.fromhex("85db0f84de000000")
GROUP_H4_SITE = 0x00409CB8
GROUP_H4_OLD = bytes.fromhex("e8d3bd0300")
GROUP_H4_TARGET = 0x00445A90
GROUP_H4_RETURN = 0x00409CBD
UNIT_GROUP_OFFSET = 0x344
UNIT_HANDLE_OFFSET = 0x29C
UNIT_OWNER_OFFSET = 0x8E
LOCAL_PLAYER_VA = 0x00B63FC4
# This is the native PlayerStruct group table, not one of the moved G2 pool
# state ranges. Its 10 x 0x50 group bank remains the official 20-slot layout.
PLAYER_GROUP_BASE = 0x009570F4
PLAYER_STRIDE = 0x3ABC
GROUP_ENTRIES_OFFSET = 0x16
GROUP_STRIDE = 0x50
GROUP_H1_CODE_OFFSET = 0xC00
GROUP_H2_CODE_OFFSET = 0xD00
GROUP_H3_CODE_OFFSET = 0xE00
GROUP_H4_CODE_OFFSET = 0xF00
# Exact packed six-array base in the pinned 2614 composition. The corresponding
# existence address is derived through the legacy geometry, not guessed.
G2_SIX_BASE_2614 = 0x01B1C000
SAVE_HOOK_VA = 0x01210257
SAVE_HOOK_OLD = bytes.fromhex("b8 7c a9 4d 00 57 ff d0")
SAVE_CONTINUATION_VA = 0x0121025F
SAVE_OPTIONAL_HOOK_VA = 0x0121026F
SAVE_OPTIONAL_HOOK_OLD = bytes.fromhex("b8 7c a9 4d 00 57 ff d0")
SAVE_OPTIONAL_CONTINUATION_VA = 0x01210277
# The optional SMR9 reader reaches this shared close only after all native
# stream reads. Stage a G5S1 trailer there, then commit it only after the last
# outer 2614 clear at 0x00441549 has run.
LOAD_STAGE_HOOK_VA = 0x012104A6
LOAD_STAGE_HOOK_OLD = bytes.fromhex("b8 7c a9 4d 00")
LOAD_STAGE_CONTINUATION_VA = 0x012104AE
LOAD_SEQUENCE_HOOK_VA = 0x0044130A
LOAD_SEQUENCE_HOOK_OLD = bytes.fromhex("56 e8 c0 fd c4 00 e8 eb 2e cf 00")
LOAD_SEQUENCE_CONTINUATION_VA = 0x00441315
LOAD_FINAL_CLEAR_HOOK_VA = 0x00441549
LOAD_FINAL_CLEAR_HOOK_OLD = bytes.fromhex("e8 b2 30 cf 00")
LOAD_FINAL_CLEAR_CONTINUATION_VA = 0x0044154E
NATIVE_LOAD_FN = 0x010910D0
NATIVE_POSTLOAD_CLEAR_FN = 0x01134200
NATIVE_FINAL_CLEAR_FN = 0x01134600
STREAM_SAVE_FN = 0x004DA39F
STREAM_LOAD_FN = 0x004DA4A9
STREAM_SEEK_FN = 0x004DB090
SIDECAR_MAGIC = b"G5S1"
SIDE_BYTES = 8 + 100 * 4
COUNT_CAP_PATCHES = (
    (0x0041DC68, bytes.fromhex("b8 14 00 00 00"), bytes.fromhex("b8 64 00 00 00")),
    (0x0041DDE4, bytes.fromhex("83 ff 14"), bytes.fromhex("83 ff 64")),
    (0x0041DE55, bytes.fromhex("bf 14 00 00 00"), bytes.fromhex("bf 64 00 00 00")),
    (0x0043877A, bytes.fromhex("66 3d 14 00"), bytes.fromhex("66 3d 64 00")),
    (0x016016D9, bytes.fromhex("83 f9 14"), bytes.fromhex("83 f9 64")),
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def window_counts(count: int) -> tuple[int, int]:
    """Counts supplied to the added third/fourth native 20-entry windows."""
    bounded = min(max(int(count), 0), 100)
    return max(0, min(20, bounded - 60)), max(0, min(20, bounded - 80))


def chunk_vas(selection_base: int) -> tuple[int, int]:
    """Resolve the two added windows from the candidate's relocated list."""
    return selection_base + 0xF0, selection_base + 0x140


def _assemble(address: int, selection_base: int) -> bytes:
    """Append count-bounded windows without shifting the native caller frame.

    The official helper reads packet data from caller-relative stack offsets.
    These calls therefore use original ESP; the existing epilogue restores the
    saved nonvolatile registers and defines EAX on the way out.
    """
    chunk3_va, chunk4_va = chunk_vas(selection_base)
    source = f"""
        cmp word ptr [0x008930A4], 1
        jne allowed
        cmp dword ptr [0x008930A0], 0
        jne done
        cmp word ptr [esp+0xAC], 3
        jne done
    allowed:
        mov eax, dword ptr [{hex(SELECTION_COUNT_VA)}]
        cmp eax, 100
        jbe count_ok
        mov eax, 100
    count_ok:
        cmp eax, 60
        jbe second
        sub eax, 60
        cmp eax, 20
        jbe third_count_ok
        mov eax, 20
    third_count_ok:
        test eax, eax
        jz second
        mov ecx, eax
        mov esi, {hex(chunk3_va)}
        call {hex(CHUNK_HELPER_VA)}
    second:
        mov eax, dword ptr [{hex(SELECTION_COUNT_VA)}]
        cmp eax, 100
        jbe count2_ok
        mov eax, 100
    count2_ok:
        cmp eax, 80
        jbe done
        sub eax, 80
        cmp eax, 20
        jbe fourth_count_ok
        mov eax, 20
    fourth_count_ok:
        test eax, eax
        jz done
        mov ecx, eax
        mov esi, {hex(chunk4_va)}
        call {hex(CHUNK_HELPER_VA)}
    done:
        jmp {hex(CONTINUATION_VA)}
    """
    engine = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoded, _ = engine.asm(source, address)
    return bytes(encoded)


def _sidecar_save_asm(address: int, selection_base: int, magic_va: int,
                      continuation_va: int) -> bytes:
    source = f"""
        pushfd
        pushad
        push edi
        push 1
        push 4
        push {hex(magic_va)}
        call {hex(STREAM_SAVE_FN)}
        add esp, 0x10
        push edi
        push 1
        push 4
        push {hex(SELECTION_COUNT_VA)}
        call {hex(STREAM_SAVE_FN)}
        add esp, 0x10
        push edi
        push 100
        push 4
        push {hex(selection_base)}
        call {hex(STREAM_SAVE_FN)}
        add esp, 0x10
        popad
        popfd
        mov eax, 0x004da97c
        push edi
        call eax
        jmp {hex(continuation_va)}
    """
    encoded, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(source, address)
    return bytes(encoded)


def _sidecar_stage_load_asm(address: int, scratch_va: int, stage_flag_va: int) -> bytes:
    """Stage a complete, validated EOF footer before the native stream closes."""
    source = f"""
        pushfd
        pushad
        mov dword ptr [{hex(stage_flag_va)}], 0
        push 2
        push -{SIDE_BYTES}
        push ebx
        call {hex(STREAM_SEEK_FN)}
        add esp, 0x0c
        test eax, eax
        jne stage_done
        push ebx
        push {SIDE_BYTES}
        push 1
        push {hex(scratch_va)}
        call {hex(STREAM_LOAD_FN)}
        add esp, 0x10
        cmp eax, {SIDE_BYTES}
        jne stage_done
        cmp dword ptr [{hex(scratch_va)}], {int.from_bytes(SIDECAR_MAGIC, 'little')}
        jne stage_done
        mov eax, dword ptr [{hex(scratch_va + 4)}]
        cmp eax, 100
        ja stage_done
        xor ecx, ecx
    validate_entries:
        cmp ecx, eax
        jae stage_valid
        mov edx, dword ptr [{hex(scratch_va + 8)}+ecx*4]
        and edx, 0x0fff
        test edx, edx
        jz stage_done
        cmp edx, 4092
        ja stage_done
        inc ecx
        jmp validate_entries
    stage_valid:
        mov dword ptr [{hex(stage_flag_va)}], 1
    stage_done:
        popad
        popfd
        mov eax, 0x004da97c
        push ebx
        call eax
        jmp {hex(LOAD_STAGE_CONTINUATION_VA)}
    """
    encoded, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(source, address)
    return bytes(encoded)


def _sidecar_begin_load_asm(address: int, stage_flag_va: int) -> bytes:
    """Invalidate stale stage state and replay the original load/early-clear calls."""
    source = f"""
        mov dword ptr [{hex(stage_flag_va)}], 0
        push esi
        call {hex(NATIVE_LOAD_FN)}
        call {hex(NATIVE_POSTLOAD_CLEAR_FN)}
        jmp {hex(LOAD_SEQUENCE_CONTINUATION_VA)}
    """
    encoded, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(source, address)
    return bytes(encoded)


def _sidecar_commit_load_asm(address: int, selection_base: int, scratch_va: int,
                             stage_flag_va: int) -> bytes:
    """Replay the last native clear, then restore a validated G5S1 footer."""
    source = f"""
        call {hex(NATIVE_FINAL_CLEAR_FN)}
        pushfd
        pushad
        cmp dword ptr [{hex(stage_flag_va)}], 1
        jne commit_done
        mov eax, dword ptr [{hex(scratch_va + 4)}]
        cmp eax, 100
        ja commit_done
        mov dword ptr [{hex(SELECTION_COUNT_VA)}], eax
        lea esi, [{hex(scratch_va + 8)}]
        mov edi, {hex(selection_base)}
        mov ecx, 100
        cld
        rep movsd dword ptr es:[edi], dword ptr [esi]
        mov dword ptr [{hex(stage_flag_va)}], 0
    commit_done:
        popad
        popfd
        jmp {hex(LOAD_FINAL_CLEAR_CONTINUATION_VA)}
    """
    encoded, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(source, address)
    return bytes(encoded)


def _group_h1_asm(address: int, *, pool_base: int, exists_base: int,
                  selection_base: int) -> bytes:
    """Clear stale +0x344 memberships for the local player before assign."""
    source = f"""
        pushad
        xor esi, esi
    scan:
        cmp word ptr [esi*2+{hex(exists_base)}], 0
        je next_unit
        mov eax, esi
        lea edi, [eax+eax*2]
        shl edi, 4
        sub edi, esi
        lea edi, [edi+edi*4]
        lea edi, [edi*8+{hex(pool_base)}]
        mov eax, dword ptr [edi+{hex(UNIT_GROUP_OFFSET)}]
        cmp eax, ebx
        jne next_unit
        movsx eax, byte ptr [edi+{hex(UNIT_OWNER_OFFSET)}]
        cmp eax, dword ptr [{hex(LOCAL_PLAYER_VA)}]
        jne next_unit
        mov dword ptr [edi+{hex(UNIT_GROUP_OFFSET)}], -1
    next_unit:
        inc esi
        cmp esi, 4093
        jl scan
        popad
        mov edx, dword ptr [esp+0x14]
        mov ebx, {hex(selection_base)}
        jmp 0x00445D57
    """
    encoded, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(source, address)
    return bytes(encoded)


def _group_h2_asm(address: int, *, pool_base: int, selection_base: int) -> bytes:
    """Keep first 20 in PlayerStruct; store overflow directly on unit+0x344."""
    source = f"""
        cmp ebx, {hex(selection_base+WINDOW_BYTES)}
        jb stock_first_twenty
        movzx eax, word ptr [ebx]
        imul eax, eax, 0x758
        add eax, {hex(pool_base+UNIT_GROUP_OFFSET)}
        mov ecx, dword ptr [esp+0x24]
        mov dword ptr [eax], ecx
        mov ebp, dword ptr [esp+0x18]
        jmp 0x00445E01
    stock_first_twenty:
        mov eax, dword ptr [esp+0x10]
        mov word ptr [eax], 0
        jmp 0x00445DD4
    """
    encoded, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(source, address)
    return bytes(encoded)


def _group_h3_asm(address: int, *, pool_base: int, exists_base: int) -> bytes:
    """Recall tagged overflow members using the stock live/owner/selectable gates."""
    source = f"""
        pushad
        xor esi, esi
        cmp dword ptr [esp+0x10], 100
        jae recall_done
    scan:
        cmp word ptr [esi*2+{hex(exists_base)}], 0
        je next_unit
        mov eax, esi
        push eax
        call 0x00416F40
        add esp, 4
        test eax, eax
        je next_unit
        mov eax, esi
        lea edi, [eax+eax*2]
        shl edi, 4
        sub edi, esi
        lea edi, [edi+edi*4]
        lea edi, [edi*8+{hex(pool_base)}]
        mov eax, dword ptr [edi+{hex(UNIT_GROUP_OFFSET)}]
        cmp eax, ebp
        jne next_unit
        movsx eax, byte ptr [edi+{hex(UNIT_OWNER_OFFSET)}]
        cmp eax, dword ptr [{hex(LOCAL_PLAYER_VA)}]
        jne next_unit
        push esi
        call 0x0040F790
        nop
        nop
        nop
        cmp eax, 1
        jne next_unit
        push 0
        push 1
        push esi
        mov ecx, 0x0061E36C
        call 0x0040F7D0
        test eax, eax
        je next_unit
        inc dword ptr [esp+0x10]
    next_unit:
        inc esi
        cmp esi, 4093
        jl scan
    recall_done:
        popad
        test ebx, ebx
        je 0x00445FB7
        jmp 0x00445ED9
    """
    encoded, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(source, address)
    return bytes(encoded)


def _group_h4_asm(address: int) -> bytes:
    """Reissue stock death cleanup, then clear this unit's one overflow group."""
    source = f"""
        call {hex(GROUP_H4_TARGET)}
        pushad
        mov eax, dword ptr [esi+{hex(UNIT_GROUP_OFFSET)}]
        cmp eax, -1
        je cleanup_done
        movzx ecx, word ptr [esi+{hex(UNIT_HANDLE_OFFSET)}]
        movsx edx, byte ptr [esi+{hex(UNIT_OWNER_OFFSET)}]
        lea ebx, [edx+edx*2]
        shl ebx, 4
        sub ebx, edx
        lea ebx, [ebx+ebx*4]
        shl ebx, 4
        sub ebx, edx
        lea ebx, [ebx*4+{hex(PLAYER_GROUP_BASE)}]
        imul eax, eax, {hex(GROUP_STRIDE)}
        add ebx, eax
        lea edi, [ebx+{hex(GROUP_ENTRIES_OFFSET)}]
        mov esi, 20
    scan_group:
        movzx eax, word ptr [edi]
        cmp ax, cx
        jne next_entry
        mov word ptr [edi], 0
        mov word ptr [edi+2], 0
    next_entry:
        add edi, 4
        dec esi
        jnz scan_group
        push -1
        push ecx
        call 0x0040F750
    cleanup_done:
        popad
        jmp {hex(GROUP_H4_RETURN)}
    """
    encoded, _ = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32).asm(source, address)
    return bytes(encoded)


def _group_hook_payloads(image: bytes, original: bytes, out: bytearray,
                         *, code_va: int, raw: int, raw_size: int,
                         pool_base: int, exists_base: int,
                         selection_base: int) -> dict[str, Any]:
    """Install the version-checked 100-member H1/H2/H3/H4 algorithm seam."""
    if bytes(original[pe_extend.va_to_offset(original, GROUP_H1_SITE):
                      pe_extend.va_to_offset(original, GROUP_H1_SITE)+len(GROUP_H1_OFFICIAL_OLD)]) != GROUP_H1_OFFICIAL_OLD:
        raise ValueError("2614 G5 H1 official preimage changed")
    h1_old = b"\x8b\x54\x24\x14\xbb" + struct.pack("<I", selection_base)
    rows = (
        (GROUP_H1_SITE, h1_old, GROUP_H1_CODE_OFFSET,
         _group_h1_asm(code_va+GROUP_H1_CODE_OFFSET, pool_base=pool_base,
                       exists_base=exists_base, selection_base=selection_base)),
        (GROUP_H2_SITE, GROUP_H2_OLD, GROUP_H2_CODE_OFFSET,
         _group_h2_asm(code_va+GROUP_H2_CODE_OFFSET, pool_base=pool_base,
                       selection_base=selection_base)),
        (GROUP_H3_SITE, GROUP_H3_OLD, GROUP_H3_CODE_OFFSET,
         _group_h3_asm(code_va+GROUP_H3_CODE_OFFSET, pool_base=pool_base,
                       exists_base=exists_base)),
        (GROUP_H4_SITE, GROUP_H4_OLD, GROUP_H4_CODE_OFFSET,
         _group_h4_asm(code_va+GROUP_H4_CODE_OFFSET)),
    )
    installed: dict[str, Any] = {}
    for site, expected, offset, payload in rows:
        site_off = pe_extend.va_to_offset(image, site)
        if bytes(image[site_off:site_off+len(expected)]) != expected:
            raise ValueError(f"2614 G5 group hook preimage mismatch at 0x{site:08x}")
        if offset + len(payload) > raw_size:
            raise ValueError(f"2614 G5 group code exceeds .g2code at +0x{offset:x}")
        target = raw + offset
        if any(out[target:target+len(payload)]):
            raise ValueError(f"2614 G5 group code range is not zero at +0x{offset:x}")
        out[target:target+len(payload)] = payload
        replacement = b"\xe9" + struct.pack("<i", code_va+offset-(site+5))
        if len(expected) > 5:
            replacement += b"\x90" * (len(expected)-5)
        patch_off = pe_extend.va_to_offset(image, site)
        out[patch_off:patch_off+len(expected)] = replacement
        installed[hex(site)] = {"old": expected.hex(), "wrapper_va": hex(code_va+offset),
                                "wrapper_bytes": payload.hex(),
                                "wrapper_size": len(payload)}

    # The stock assign loop still ended at 20 entries even after H2 overflow
    # handling; extend its *selection-list pointer end*, not the 0x50 group bank.
    end_old = b"\x81\xfb" + struct.pack("<I", selection_base+WINDOW_BYTES)
    end_new = b"\x81\xfb" + struct.pack("<I", selection_base+100*4)
    _patch_bytes(out, image, GROUP3_END_SITE, end_old, end_new)
    installed[hex(GROUP3_END_SITE)] = {"old": end_old.hex(), "new": end_new.hex(),
                                       "reason": "iterate all 100 selected entries; preserve 20-entry native bank"}
    return installed


def _patch_bytes(out: bytearray, image: bytes, va: int, old: bytes, new: bytes) -> None:
    if len(old) != len(new):
        raise ValueError("G5 exact patch changes instruction width")
    off = pe_extend.va_to_offset(image, va)
    if bytes(out[off:off + len(old)]) != old:
        raise ValueError(f"G5 2614 old bytes differ at 0x{va:08x}")
    out[off:off + len(old)] = new


def apply(image: bytes, original: bytes, *, state_base: int, scratch_va: int,
          state_profile: tuple[g2_state_2610.StateSection, ...] | None = None
          ) -> tuple[bytes, dict[str, Any]]:
    """Apply after G2: native cap100 plus 20-window dispatch and EOF sidecar."""
    if _sha(original) != OFFICIAL_SHA256:
        raise ValueError("G5 2614 adapter requires the pinned official ESL2614 input")
    if G2CODE not in pe_extend.section_names(image):
        raise ValueError("G5 adapter requires the G2-owned .g2code reservation")
    if state_profile is None:
        from patches.esl2614.g2_port_2614 import _state_profile_2614
        state_profile = _state_profile_2614()
    starts = g2_state_2610.layout(state_base, state_profile)
    selection_base = g2_state_2610.map_value(0x01604004, starts,
                                             state_profile=state_profile)
    # The one hook is verified against official input, but the candidate may
    # already contain other nonoverlapping patches.
    off = pe_extend.va_to_offset(original, HOOK_VA)
    old = bytes(original[off:off + len(HOOK_OLD)])
    if old != HOOK_OLD:
        raise ValueError("2614 selection continuation hook preimage changed")
    out = bytearray(image)
    hook_off = pe_extend.va_to_offset(bytes(out), HOOK_VA)
    if bytes(out[hook_off:hook_off + 5]) != old:
        raise ValueError("G5 hook overlaps a prior patch or has unexpected bytes")
    # G2 layer 3 must have moved the three official window operands together
    # with the list. Reject a partial/stale composition instead of embedding
    # the official absolute VA in the new wrapper.
    pe = pefile.PE(data=image, fast_load=True)
    try:
        section = next(s for s in pe.sections if s.Name.rstrip(b"\0") == G2CODE)
    finally:
        pe.close()
    for va, expected in ((0x0112DBBF, selection_base + 0x50),
                         (0x0112DBCE, selection_base + 0xA0)):
        operand_off = pe_extend.va_to_offset(image, va)
        if bytes(image[operand_off:operand_off + 1]) != b"\xbe":
            raise ValueError(f"G5 native first windows changed at 0x{va:08x}")
        actual = int.from_bytes(image[operand_off + 1:operand_off + 5], "little")
        if actual != expected:
            raise ValueError(f"G5 native first window does not use relocated selection base: "
                             f"0x{actual:08x} != 0x{expected:08x}")
    raw = int(section.PointerToRawData)
    raw_size = int(section.SizeOfRawData)
    virtual_size = int(section.Misc_VirtualSize)
    va = pe_extend.section_va(image, G2CODE)
    if raw_size < SECTION_BYTES or virtual_size < SECTION_BYTES:
        raise ValueError(".g2code is too small for the reserved 2614 G5 wrapper")
    stage_flag_va = scratch_va + SIDE_BYTES
    code_map = {
        ORDER_WRAPPER_OFFSET: _assemble(va + ORDER_WRAPPER_OFFSET, selection_base),
        SAVE_WRAPPER_OFFSET: _sidecar_save_asm(
            va + SAVE_WRAPPER_OFFSET, selection_base, va + MAGIC_OFFSET,
            SAVE_CONTINUATION_VA),
        SAVE_OPTIONAL_WRAPPER_OFFSET: _sidecar_save_asm(
            va + SAVE_OPTIONAL_WRAPPER_OFFSET, selection_base, va + MAGIC_OFFSET,
            SAVE_OPTIONAL_CONTINUATION_VA),
        LOAD_STAGE_WRAPPER_OFFSET: _sidecar_stage_load_asm(
            va + LOAD_STAGE_WRAPPER_OFFSET, scratch_va, stage_flag_va),
        LOAD_BEGIN_WRAPPER_OFFSET: _sidecar_begin_load_asm(
            va + LOAD_BEGIN_WRAPPER_OFFSET, stage_flag_va),
        LOAD_COMMIT_WRAPPER_OFFSET: _sidecar_commit_load_asm(
            va + LOAD_COMMIT_WRAPPER_OFFSET, selection_base, scratch_va, stage_flag_va),
        MAGIC_OFFSET: SIDECAR_MAGIC,
    }
    for offset, code in code_map.items():
        if len(code) > raw_size - offset:
            raise ValueError("2614 G5 code exceeds reserved .g2code tail")
        target = raw + offset
        if any(out[target:target + len(code)]):
            raise ValueError(f"reserved .g2code G5 range is not zero-filled at +0x{offset:x}")
        out[target:target + len(code)] = code

    pool_base = g2_reloc_2610.relocate_value(0x0066B790, G2_SIX_BASE_2614)
    exists_base = g2_reloc_2610.relocate_value(0x008990C8, G2_SIX_BASE_2614)
    if pool_base != G2_SIX_BASE_2614 or exists_base != 0x022729F8:
        raise ValueError("2614 G2 pool/existence profile geometry changed")
    group_hooks = _group_hook_payloads(
        image, original, out, code_va=va, raw=raw, raw_size=raw_size,
        pool_base=pool_base, exists_base=exists_base, selection_base=selection_base,
    )

    # All five official active-cap sites are part of OUR custom dispatch path;
    # this is not a cap-only patch, since the order-record windows remain <=20.
    for va_site, old_bytes, new_bytes in COUNT_CAP_PATCHES:
        _patch_bytes(out, image, va_site, old_bytes, new_bytes)

    order_va = va + ORDER_WRAPPER_OFFSET
    _patch_bytes(out, image, HOOK_VA, old,
                 b"\xe9" + struct.pack("<i", order_va - (HOOK_VA + 5)))
    for hook_va, old_bytes, target_va in (
        (SAVE_HOOK_VA, SAVE_HOOK_OLD, va + SAVE_WRAPPER_OFFSET),
        (SAVE_OPTIONAL_HOOK_VA, SAVE_OPTIONAL_HOOK_OLD,
         va + SAVE_OPTIONAL_WRAPPER_OFFSET),
        (LOAD_STAGE_HOOK_VA, LOAD_STAGE_HOOK_OLD,
         va + LOAD_STAGE_WRAPPER_OFFSET),
        (LOAD_SEQUENCE_HOOK_VA, LOAD_SEQUENCE_HOOK_OLD,
         va + LOAD_BEGIN_WRAPPER_OFFSET),
        (LOAD_FINAL_CLEAR_HOOK_VA, LOAD_FINAL_CLEAR_HOOK_OLD,
         va + LOAD_COMMIT_WRAPPER_OFFSET),
    ):
        replacement = b"\xe9" + struct.pack("<i", target_va - (hook_va + 5))
        if len(old_bytes) > 5:
            replacement += b"\x90" * (len(old_bytes) - 5)
        _patch_bytes(out, image, hook_va, old_bytes, replacement)
    result = pe_extend._with_checksum(bytes(out))
    return result, {
        "schema": "syw2plus.esl2614.g5-100-chunked.v1",
        "input_sha256": _sha(original),
        "candidate_sha256": _sha(result),
        "hook_va": hex(HOOK_VA), "old": old.hex(), "wrapper_va": hex(order_va),
        "wrapper_size": len(code_map[ORDER_WRAPPER_OFFSET]), "helper_va": hex(CHUNK_HELPER_VA),
        "selection_count_va": hex(SELECTION_COUNT_VA),
        "relocated_selection_base": hex(selection_base),
        "windows": [
            {"first_entry": 60, "va": hex(chunk_vas(selection_base)[0]), "max_count": 20},
            {"first_entry": 80, "va": hex(chunk_vas(selection_base)[1]), "max_count": 20},
        ],
        "count_behavior": "clamp to 100; pass min(20, count-start); skip zero windows",
        "capacity_sites": [hex(site[0]) for site in COUNT_CAP_PATCHES],
        "control_group_overflow": {
            "algorithm": "OUR H1/H2/H3 + H4 death cleanup; stock 20-slot bank plus unit+0x344 overflow",
            "pool_base": hex(pool_base), "existence_base": hex(exists_base),
            "scan_capacity": 4093, "selection_capacity": 100,
            "group_stride": hex(GROUP_STRIDE), "unit_group_offset": hex(UNIT_GROUP_OFFSET),
            "hooks": group_hooks,
        },
        "sidecar": {"save_hook_va": hex(SAVE_HOOK_VA),
                    "save_optional_hook_va": hex(SAVE_OPTIONAL_HOOK_VA),
                    "load_stage_hook_va": hex(LOAD_STAGE_HOOK_VA),
                    "load_sequence_hook_va": hex(LOAD_SEQUENCE_HOOK_VA),
                    "load_final_clear_hook_va": hex(LOAD_FINAL_CLEAR_HOOK_VA),
                    "magic": SIDECAR_MAGIC.decode(), "selection_bytes": 400,
                    "footer_bytes": SIDE_BYTES, "scratch_va": hex(scratch_va),
                    "stage_flag_va": hex(stage_flag_va),
                    "stage_read": "seek EOF-408; require complete magic/count/active slot IDs",
                    "late_commit": "after final native clear at 0x00441549; legacy/missing/invalid footer leaves native clear"},
        "preserved": ["official three 20-entry chunks", "native 20-entry helper/packet",
                      "4AE550->.d15code official detour", "caller registers and flags"],
    }
