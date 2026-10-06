import hashlib
import importlib.util
import sys
from pathlib import Path

import capstone
import pefile
import pytest

MODULE = Path(__file__).with_name("g5_selection_cap50_v10.py")
spec = importlib.util.spec_from_file_location(MODULE.stem, MODULE)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original() -> bytes:
    if not SOURCE.is_file():
        pytest.skip("local original executable is unavailable")
    return SOURCE.read_bytes()


def _offset(pe: pefile.PE, va: int) -> int:
    return mod._va_to_file_offset(pe, va)


def test_build_is_deterministic_and_v9_plus_two_hooks(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    candidate2, report2 = mod.build_candidate(original)
    v9_candidate, v9_report = mod.v9.build_candidate(original)
    assert len(candidate) == len(original)
    assert candidate == candidate2
    assert report["candidate_sha256"] == report2["candidate_sha256"]
    assert report["v9_candidate_sha256"] == hashlib.sha256(v9_candidate).hexdigest()
    assert report["v9_candidate_sha256"] == v9_report["candidate_sha256"]
    assert report["candidate_sha256"] == hashlib.sha256(candidate).hexdigest()
    assert report["candidate_sha256"] != report["v9_candidate_sha256"]


def test_hook_old_bytes_are_the_pinned_stock_call_encoding(original: bytes) -> None:
    v9_candidate, _v9_report = mod.v9.build_candidate(original)
    pe = pefile.PE(data=v9_candidate, fast_load=True)
    try:
        save_off = _offset(pe, mod.SAVE_APPEND_HOOK_VA)
        load_off = _offset(pe, mod.LOAD_APPEND_HOOK_VA)
    finally:
        pe.close()
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)

    actual_save = v9_candidate[save_off : save_off + len(mod.SAVE_APPEND_HOOK_OLD)]
    assert actual_save == mod.SAVE_APPEND_HOOK_OLD
    insn = next(md.disasm(mod.SAVE_APPEND_HOOK_OLD, mod.SAVE_APPEND_HOOK_VA))
    assert insn.mnemonic == "call" and insn.op_str == hex(mod.STREAM_SAVE_FN)

    actual_load = v9_candidate[load_off : load_off + len(mod.LOAD_APPEND_HOOK_OLD)]
    assert actual_load == mod.LOAD_APPEND_HOOK_OLD
    insn = next(md.disasm(mod.LOAD_APPEND_HOOK_OLD, mod.LOAD_APPEND_HOOK_VA))
    assert insn.mnemonic == "call" and insn.op_str == hex(mod.STREAM_LOAD_FN)


def test_hooked_calls_are_the_last_block_transfer_before_the_stream_closes(original: bytes) -> None:
    """Both hooks must sit on the last fread/fwrite-shaped call in their
    routine -- any earlier one would shift the file position of every
    subsequent legacy block for a reader that does not know about the
    sidecar, breaking backward/forward save compatibility."""
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = False
    pe = pefile.PE(data=original, fast_load=True)
    try:
        image_base = pe.OPTIONAL_HEADER.ImageBase
        data = pe.get_memory_mapped_image()
    finally:
        pe.close()

    def calls_to(target: int, lo: int, hi: int) -> list[int]:
        code = data[lo - image_base : hi - image_base]
        out = []
        for insn in md.disasm(code, lo):
            if insn.mnemonic == "call" and insn.op_str.startswith("0x"):
                if int(insn.op_str, 16) == target:
                    out.append(insn.address)
        return out

    save_calls = calls_to(mod.STREAM_SAVE_FN, 0x440800, 0x441200)
    load_calls = calls_to(mod.STREAM_LOAD_FN, 0x440800, 0x441800)
    assert save_calls[-1] == mod.SAVE_APPEND_HOOK_VA
    assert load_calls[-1] == mod.LOAD_APPEND_HOOK_VA


def test_only_the_hook_sites_cave_and_section_header_differ_from_v9(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    v9_candidate, _v9_report = mod.v9.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        save_off = _offset(pe, mod.SAVE_APPEND_HOOK_VA)
        load_off = _offset(pe, mod.LOAD_APPEND_HOOK_VA)
        rsrc = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".rsrc")
        section_header_off = rsrc.get_file_offset()
        cave_off = rsrc.PointerToRawData + mod.V9_CAVE_END
        cave_len = mod.V10_CAVE_END_OFFSET - mod.V9_CAVE_END
    finally:
        pe.close()
    diffs = [i for i in range(len(candidate)) if candidate[i] != v9_candidate[i]]
    assert diffs, "expected at least the hook sites and cave to differ"
    allowed = (
        set(range(save_off, save_off + len(mod.SAVE_APPEND_HOOK_OLD)))
        | set(range(load_off, load_off + len(mod.LOAD_APPEND_HOOK_OLD)))
        | set(range(section_header_off, section_header_off + 40))
        | set(range(cave_off, cave_off + cave_len))
    )
    assert set(diffs) <= allowed, (
        f"unexpected byte differences outside pinned scope: {sorted(set(diffs) - allowed)}"
    )


def test_save_wrapper_reissues_original_write_then_appends_magic_and_full_array(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        save_va = int(report["hooks"]["save_append"]["wrapper_va"], 16)
        off = _offset(pe, save_va)
    finally:
        pe.close()
    code = candidate[off : off + report["hooks"]["save_append"]["bytes"]]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insns = list(md.disasm(code, save_va))

    calls = [i for i in insns if i.mnemonic == "call"]
    assert len(calls) == 3
    assert all(i.op_str == hex(mod.STREAM_SAVE_FN) for i in calls)
    assert insns[0].mnemonic == "push" and insns[0].op_str == "ebp"
    assert insns[-1].mnemonic == "ret"

    pushes_before_third_call = [
        i.op_str for i in insns[insns.index(calls[1]) + 1 : insns.index(calls[2])]
    ]
    assert hex(mod.SELECTION_BASE) in pushes_before_third_call
    assert hex(mod.SELECTION_ARRAY_BYTES) in pushes_before_third_call


def test_load_wrapper_gates_full_restore_on_magic_and_clamps_count(original: bytes) -> None:
    candidate, report = mod.build_candidate(original)
    pe = pefile.PE(data=candidate, fast_load=True)
    try:
        load_va = int(report["hooks"]["load_append"]["wrapper_va"], 16)
        off = _offset(pe, load_va)
    finally:
        pe.close()
    code = candidate[off : off + report["hooks"]["load_append"]["bytes"]]
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    insns = list(md.disasm(code, load_va))

    calls = [i for i in insns if i.mnemonic == "call"]
    assert len(calls) == 3
    assert all(i.op_str == hex(mod.STREAM_LOAD_FN) for i in calls)

    jne = [i for i in insns if i.mnemonic == "jne"]
    assert len(jne) == 2
    finish_targets = {i.op_str for i in jne}
    assert len(finish_targets) == 1, "both magic-format guards must jump to the same finish label"

    jle = [i for i in insns if i.mnemonic == "jle"]
    assert len(jle) == 1
    assert jle[0].op_str in finish_targets, "the count clamp must also fall through to finish"

    cmp_magic = next(i for i in insns if i.mnemonic == "cmp" and i.op_str.startswith("eax, 0x"))
    assert int(cmp_magic.op_str.split(",")[1].strip(), 16) == mod.SIDECAR_MAGIC_DWORD

    clamp_store = next(
        i for i in insns if i.mnemonic == "mov" and i.op_str.startswith(f"dword ptr [{hex(mod.SELECTION_BASE)}]")
    )
    assert clamp_store.op_str.endswith(f"0x{mod.TARGET_CAPACITY:x}")


def test_sidecar_magic_is_four_ascii_bytes_and_matches_dword() -> None:
    assert mod.SIDECAR_MAGIC == b"G5SC"
    assert len(mod.SIDECAR_MAGIC) == 4
    assert mod.SIDECAR_MAGIC_DWORD.to_bytes(4, "little") == mod.SIDECAR_MAGIC


def test_v10_cave_starts_after_v9_own_cave() -> None:
    assert mod.V9_CAVE_END == mod.v9.NEWGAME_CAVE_END_OFFSET
    assert mod.MAGIC_LITERAL_OFFSET == mod.V9_CAVE_END
    assert mod.SAVE_APPEND_WRAPPER_OFFSET > mod.MAGIC_LITERAL_OFFSET + 4
    assert mod.LOAD_APPEND_WRAPPER_OFFSET > mod.SAVE_APPEND_WRAPPER_OFFSET
    assert mod.V10_CAVE_END_OFFSET > mod.LOAD_APPEND_WRAPPER_OFFSET
    # The magic scratch buffer (fread destination) must NOT live in .rsrc --
    # that section is read+execute but not writable (confirmed by a runtime
    # access violation during development) -- so it must sit in the
    # writable relocated-storage gap instead, strictly before the also
    # relocated (read+execute-only) .rsrc section begins.
    assert mod.MAGIC_SCRATCH_VA == mod.v9.v8.v7.v3.v1.STORAGE_END
    assert mod.MAGIC_SCRATCH_VA + 4 <= mod.SELECTION_BASE + 0x1000


def test_restore_candidate_rejects_unknown_bytes(original: bytes) -> None:
    candidate, _report = mod.build_candidate(original)
    with pytest.raises(ValueError):
        mod.restore_candidate(candidate[:-1] + bytes([candidate[-1] ^ 1]), original)
    assert mod.restore_candidate(candidate, original) == original
