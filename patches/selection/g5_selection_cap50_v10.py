#!/usr/bin/env python3
"""v9 plus a trailing save-stream sidecar that preserves entries 21..50.

2026-09-29 00:59 user judgment (``docs/feedback/INBOX.md``) held the v9
milestone: item (1) is that a raw (unassigned) 50-unit drag selection must
survive save/load in full, not just the first 20 (v7/v8/v9's documented
``known_limit``), while staying bidirectionally save-compatible -- a vanilla
original EXE opening a v10 save must still see (and only see) the first 20,
and v10 opening a save written by the original EXE or any pre-v10 candidate
must behave exactly as v9 already does (first ``min(count, 20)`` restored,
the rest cleared).

Static disassembly of the outer save/load routines (``Syw2plus/
syw2plus_original.exe``, both anchored at the same file offsets in every
prior selection-cap50 candidate since this module changes no earlier byte)
found that the legacy 20-slot mirror v7 already hooks
(``SAVE_CALL_VA``/``LOAD_CALL_VA``, ``0x00440F0C``/``0x004412DC``) is *not*
the last block-transfer call in either routine -- one more call to the same
CRT-style stream primitive follows in each (``0x00440F1E`` on save,
``0x004412EE`` on load, both transferring an unrelated fixed 0x170-byte
block at ``0x00632F7C``), and *that* call is immediately followed by the
routine's own ``fclose``-equivalent (``call 0x004DA97C``) and return -- no
other stream read/write happens afterward. ``STREAM_SAVE_FN``/
``STREAM_LOAD_FN`` (``0x004DA39F``/``0x004DA4A9``) are themselves the
program's own C-runtime ``fwrite``/``fread`` (confirmed by disassembly: they
take ``(buffer, size, count, stream)`` and read/advance the standard
``FILE`` struct fields at ``[stream+0]``/``[stream+4]``/``[stream+0xc]``/
``[stream+0x10]``/``[stream+0x18]``), so ``fread``'s ordinary short-read
behavior on end-of-file -- return fewer than the requested element count,
without raising or crashing -- is exactly the primitive needed to detect,
at load time and without any prior knowledge of the file's length, whether
trailing sidecar bytes are present at all.

Fix: hook the *last* block-transfer call in each routine (not the legacy
mirror call v7 already owns) with a wrapper that first reissues the original
call unchanged, then:

- on save, unconditionally appends a 4-byte magic literal followed by the
  entire live relocated selection array (``SELECTION_BASE``, the count dword
  plus all 50 entry dwords -- a superset of what v7's legacy mirror already
  wrote, so no separate encoding of "just entries 21..50" is needed);
- on load, attempts to read that same 4 bytes into a scratch dword. If the
  read comes back short (``fread`` returned 0 elements -- the file ends
  exactly where a pre-v10 writer's last known block ends) or the bytes read
  do not match the magic, the file is treated as legacy/short and nothing
  further happens: the selection array is left exactly as v7/v8/v9's own
  legacy-mirror load wrapper (which runs earlier, at ``LOAD_CALL_VA``,
  strictly before this hook) already set it -- ``count = min(legacy_count,
  20)``, ``entries[20:50]`` zeroed. If the magic matches, the full 204-byte
  array is read back verbatim over ``SELECTION_BASE``, then the count field
  is defensively clamped to ``TARGET_CAPACITY`` (50) -- the same
  cap-then-store idiom v7's own mirrors already use for the legacy count --
  in case a save was ever produced by bytes this module does not control.

Because the sidecar is appended strictly after every block a pre-v10 reader
(original EXE or v1..v9 candidate) ever looks at, and that reader's own
routine closes the file immediately afterward, a pre-v10 reader opening a
v10-written save never attempts to read the extra bytes at all -- it simply
reaches its own end-of-blocks and returns, exactly as it does for its own
saves. A v10 reader opening a pre-v10 save always gets a short/failed read
for the magic (there is nothing after the file's last legacy block) and
falls back to the existing v7..v9 behavior byte-for-byte. No existing call
site's arguments, no file offset, and no block size changes; the only new
bytes on disk are the ones this module's own save wrapper appends after
everything a pre-v10 build already writes.

Both new hooks are 5-byte ``call`` sites (identical shape to v7's own
``SAVE_CALL_VA``/``LOAD_CALL_VA`` hooks) replaced with a same-length ``call``
into a new cave directly after v9's own (``V9_CAVE_END`` ..
``V10_CAVE_END_OFFSET``, confirmed zero-filled in the v9 candidate and thus
untouched by every earlier candidate in this chain).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

import keystone
import pefile

from patches.selection import g5_selection_cap50_v9 as v9

IMAGE_BASE = v9.IMAGE_BASE
ORIGINAL_SHA256 = v9.ORIGINAL_SHA256
SELECTION_BASE = v9.SELECTION_BASE
STOCK_CAPACITY = v9.STOCK_CAPACITY
TARGET_CAPACITY = v9.TARGET_CAPACITY
SELECTION_DWORDS = v9.SELECTION_DWORDS  # 51: count dword + 50 entry dwords
SELECTION_ARRAY_BYTES = SELECTION_DWORDS * 4  # 0xcc

STREAM_SAVE_FN = v9.v8.v7.STREAM_SAVE_FN
STREAM_LOAD_FN = v9.v8.v7.STREAM_LOAD_FN

# The last (not the legacy-mirror) block-transfer call in each outer
# save/load routine -- confirmed by disassembly to be immediately followed
# by the routine's own fclose-equivalent and return, i.e. the true end of
# the save stream.
SAVE_APPEND_HOOK_VA = 0x00440F1E
LOAD_APPEND_HOOK_VA = 0x004412EE
SAVE_APPEND_HOOK_OLD = bytes.fromhex("e8 7c 94 09 00")
LOAD_APPEND_HOOK_OLD = bytes.fromhex("e8 b6 91 09 00")

SIDECAR_MAGIC = b"G5SC"
SIDECAR_MAGIC_DWORD = struct.unpack("<I", SIDECAR_MAGIC)[0]

V9_CAVE_END = v9.NEWGAME_CAVE_END_OFFSET  # 0x2240
MAGIC_LITERAL_OFFSET = V9_CAVE_END
SAVE_APPEND_WRAPPER_OFFSET = 0x2250
LOAD_APPEND_WRAPPER_OFFSET = 0x22C0
V10_CAVE_END_OFFSET = 0x2340

# The .rsrc cave above is read+execute but *not* writable (confirmed by a
# runtime access violation during development: an fread() destination
# placed at a .rsrc-relative address faulted on write). The magic literal
# is only ever a save-side fwrite *source*, so read-only .rsrc is fine for
# it, but the load-side fread destination needs genuinely writable memory.
# v1's relocated-storage block reserves a full 0x1000-byte gap between
# SELECTION_BASE and the (also relocated) .rsrc section, of which only
# ``STORAGE_END - SELECTION_BASE`` bytes are used by the selection array and
# the control-group block; the remainder is unused, zero-filled (beyond
# ``.data``'s raw size, hence loader-BSS, not file-backed) and writable
# because it is still physically part of the R+W ``.data`` section's
# (oversized) virtual range, the same section SELECTION_BASE itself lives
# in.
MAGIC_SCRATCH_VA = v9.v8.v7.v3.v1.STORAGE_END

BuildAbortedError = v9.BuildAbortedError


def _save_wrapper_asm(stream_save_fn: int, magic_literal_va: int) -> str:
    return f"""
        push ebp
        mov ebp, esp
        push dword ptr [ebp+0x14]
        push dword ptr [ebp+0x10]
        push dword ptr [ebp+0xc]
        push dword ptr [ebp+0x8]
        call {hex(stream_save_fn)}
        add esp, 0x10
        push dword ptr [ebp+0x14]
        push 1
        push 4
        push {hex(magic_literal_va)}
        call {hex(stream_save_fn)}
        add esp, 0x10
        push dword ptr [ebp+0x14]
        push 1
        push {SELECTION_ARRAY_BYTES}
        push {hex(SELECTION_BASE)}
        call {hex(stream_save_fn)}
        add esp, 0x10
        pop ebp
        ret
    """


def _load_wrapper_asm(stream_load_fn: int, magic_scratch_va: int) -> str:
    return f"""
        push ebp
        mov ebp, esp
        push dword ptr [ebp+0x14]
        push dword ptr [ebp+0x10]
        push dword ptr [ebp+0xc]
        push dword ptr [ebp+0x8]
        call {hex(stream_load_fn)}
        add esp, 0x10
        push dword ptr [ebp+0x14]
        push 1
        push 4
        push {hex(magic_scratch_va)}
        call {hex(stream_load_fn)}
        add esp, 0x10
        cmp eax, 1
        jne finish
        mov eax, dword ptr [{hex(magic_scratch_va)}]
        cmp eax, {hex(SIDECAR_MAGIC_DWORD)}
        jne finish
        push dword ptr [ebp+0x14]
        push 1
        push {SELECTION_ARRAY_BYTES}
        push {hex(SELECTION_BASE)}
        call {hex(stream_load_fn)}
        add esp, 0x10
        mov eax, dword ptr [{hex(SELECTION_BASE)}]
        cmp eax, {TARGET_CAPACITY}
        jle finish
        mov dword ptr [{hex(SELECTION_BASE)}], {TARGET_CAPACITY}
        finish:
        pop ebp
        ret
    """


def _va_to_file_offset(pe: pefile.PE, va: int) -> int:
    return v9.v8._va_to_file_offset(pe, va)


def _assemble(asm: str, address: int) -> bytes:
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    encoding, _count = ks.asm(asm, address)
    if encoding is None or len(encoding) < 1:
        raise BuildAbortedError("keystone produced no bytes")
    return bytes(encoding)


def _call_rel32(source_va: int, target_va: int) -> bytes:
    return b"\xe8" + struct.pack("<i", target_va - (source_va + 5))


def build_candidate(original: bytes) -> tuple[bytes, dict[str, Any]]:
    candidate_v9, v9_report = v9.build_candidate(original)
    out = bytearray(candidate_v9)
    pe = pefile.PE(data=bytes(out), fast_load=True)
    try:
        rsrc = next((s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc"), None)
        if rsrc is None:
            raise BuildAbortedError(".rsrc section missing")
        rsrc_va = IMAGE_BASE + int(rsrc.VirtualAddress)
        if rsrc_va != SELECTION_BASE + 0x1000:
            raise BuildAbortedError(f"unexpected relocated .rsrc VA 0x{rsrc_va:08x}")
        if int(rsrc.SizeOfRawData) < V10_CAVE_END_OFFSET:
            raise BuildAbortedError(".rsrc raw padding is too small for the v10 sidecar cave")
        raw = int(rsrc.PointerToRawData)
        cave = bytes(out[raw + V9_CAVE_END : raw + V10_CAVE_END_OFFSET])
        if cave != bytes(len(cave)):
            raise BuildAbortedError("v10 sidecar cave region is not zero-filled")

        magic_literal_va = rsrc_va + MAGIC_LITERAL_OFFSET
        magic_scratch_va = MAGIC_SCRATCH_VA
        save_va = rsrc_va + SAVE_APPEND_WRAPPER_OFFSET
        load_va = rsrc_va + LOAD_APPEND_WRAPPER_OFFSET

        out[raw + MAGIC_LITERAL_OFFSET : raw + MAGIC_LITERAL_OFFSET + 4] = SIDECAR_MAGIC

        save_code = _assemble(_save_wrapper_asm(STREAM_SAVE_FN, magic_literal_va), save_va)
        load_code = _assemble(_load_wrapper_asm(STREAM_LOAD_FN, magic_scratch_va), load_va)
        if len(save_code) > LOAD_APPEND_WRAPPER_OFFSET - SAVE_APPEND_WRAPPER_OFFSET:
            raise BuildAbortedError(f"save append wrapper too large: {len(save_code)} bytes")
        if len(load_code) > V10_CAVE_END_OFFSET - LOAD_APPEND_WRAPPER_OFFSET:
            raise BuildAbortedError(f"load append wrapper too large: {len(load_code)} bytes")

        out[raw + SAVE_APPEND_WRAPPER_OFFSET : raw + SAVE_APPEND_WRAPPER_OFFSET + len(save_code)] = save_code
        out[raw + LOAD_APPEND_WRAPPER_OFFSET : raw + LOAD_APPEND_WRAPPER_OFFSET + len(load_code)] = load_code

        section_off = rsrc.get_file_offset()
        struct.pack_into(
            "<I", out, section_off + 8,
            max(int(rsrc.Misc_VirtualSize), V10_CAVE_END_OFFSET),
        )
        if int(rsrc.Characteristics) & v9.v8.v7.RSRC_EXECUTE_CODE_FLAGS != v9.v8.v7.RSRC_EXECUTE_CODE_FLAGS:
            raise BuildAbortedError(".rsrc is not already marked executable by v7/v8/v9")

        for hook_va, old_bytes, wrapper_va in (
            (SAVE_APPEND_HOOK_VA, SAVE_APPEND_HOOK_OLD, save_va),
            (LOAD_APPEND_HOOK_VA, LOAD_APPEND_HOOK_OLD, load_va),
        ):
            hook_off = _va_to_file_offset(pe, hook_va)
            actual_old = bytes(out[hook_off : hook_off + len(old_bytes)])
            if actual_old != old_bytes:
                raise BuildAbortedError(
                    f"0x{hook_va:08x}: pinned old bytes mismatch "
                    f"expected={old_bytes.hex()} actual={actual_old.hex()}"
                )
            hook_new = _call_rel32(hook_va, wrapper_va)
            if len(hook_new) != len(old_bytes):
                raise BuildAbortedError("hook replacement changed instruction length")
            out[hook_off : hook_off + len(hook_new)] = hook_new
    finally:
        pe.close()

    if len(out) != len(original):
        raise BuildAbortedError("candidate changed raw file length")
    candidate = bytes(out)
    report = {
        "schema": "syw2plus.g5-selection-cap50-saveload-full-restore-candidate.v10",
        "status": "SELECTION_CAP50_SAVELOAD_FULL_50_SIDECAR",
        "original_sha256": ORIGINAL_SHA256,
        "v9_candidate_sha256": v9_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "hooks": {
            "save_append": {
                "site": hex(SAVE_APPEND_HOOK_VA),
                "wrapper_va": hex(save_va),
                "bytes": len(save_code),
            },
            "load_append": {
                "site": hex(LOAD_APPEND_HOOK_VA),
                "wrapper_va": hex(load_va),
                "bytes": len(load_code),
            },
        },
        "sidecar": {
            "magic": SIDECAR_MAGIC.decode("ascii"),
            "magic_literal_va": hex(magic_literal_va),
            "magic_scratch_va": hex(magic_scratch_va),
            "array_bytes": SELECTION_ARRAY_BYTES,
        },
        "rsrc_cave": {
            "offset": hex(V9_CAVE_END),
            "end_exclusive": hex(V10_CAVE_END_OFFSET),
        },
        "known_limit": (
            "sidecar detection relies on a 4-byte magic match on a short/absent "
            "trailing read; a save truncated mid-write of the sidecar itself "
            "(e.g. crash between the magic and array writes) is not specially "
            "detected beyond the existing count<=TARGET_CAPACITY clamp"
        ),
        "v9_report": v9_report,
    }
    return candidate, report


def restore_candidate(candidate: bytes, original: bytes) -> bytes:
    v9.v8.v7.v3.v1.verify_original(original)
    expected, _report = build_candidate(original)
    if hashlib.sha256(candidate).digest() != hashlib.sha256(expected).digest():
        raise ValueError("candidate SHA256 mismatch; refusing to restore unknown bytes")
    return bytes(original)


def write_candidate(original_path: Path, destination: Path) -> dict[str, Any]:
    if destination.resolve() == original_path.resolve():
        raise ValueError("refusing to overwrite the original EXE")
    original = original_path.read_bytes()
    patched, report = build_candidate(original)
    destination.write_bytes(patched)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    print(json.dumps(write_candidate(args.original, args.destination), indent=2))


if __name__ == "__main__":
    main()
