from capstone import Cs, CS_ARCH_X86, CS_MODE_32

from patches.esl2614 import g5_selection_2614 as g5


def test_added_windows_are_count_bounded_and_skip_empty_tail():
    cases = {
        0: (0, 0), 20: (0, 0), 60: (0, 0), 61: (1, 0),
        79: (19, 0), 80: (20, 0), 81: (20, 1),
        99: (20, 19), 100: (20, 20), 101: (20, 20),
    }
    assert {n: g5.window_counts(n) for n in cases} == cases


def test_wrapper_uses_exact_windows_native_caller_frame_and_original_gate():
    selection_base = 0x2201000
    code = g5._assemble(0x500800, selection_base)
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    insns = list(decoder.disasm(code, 0x500800))
    # Native helper reads its command packet from caller-relative [esp+...]
    # locations, so the dispatcher must not push/save registers or allocate
    # stack locals before either native call.
    assert not any(i.mnemonic in {"push", "pushfd", "pushal", "sub"}
                   and (i.mnemonic != "sub" or "esp" in i.op_str) for i in insns)
    assert any(i.mnemonic == "cmp" and "[esp + 0xac]" in i.op_str and "3" in i.op_str for i in insns)
    calls = [i for i in insns if i.mnemonic == "call"]
    assert [i.operands[0].imm for i in calls] == [g5.CHUNK_HELPER_VA, g5.CHUNK_HELPER_VA]
    assert g5.chunk_vas(selection_base) == (selection_base + 0xF0, selection_base + 0x140)
    assert g5.chunk_vas(selection_base) != (0x16040F4, 0x1604144)
    assert code.endswith(b"\xe9" + (g5.CONTINUATION_VA - (0x500800 + len(code))).to_bytes(4, "little", signed=True))
    assert g5.HOOK_VA != 0x004AE550


def test_sidecar_save_hooks_cover_both_successful_closes_not_short_write_failure():
    save = g5._sidecar_save_asm(0x500900, 0x2201000, 0x500B00,
                                g5.SAVE_CONTINUATION_VA)
    optional = g5._sidecar_save_asm(0x500980, 0x2201000, 0x500B00,
                                    g5.SAVE_OPTIONAL_CONTINUATION_VA)
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    save_insns = list(decoder.disasm(save, 0x500900))
    optional_insns = list(decoder.disasm(optional, 0x500980))
    assert [i.operands[0].imm for i in save_insns
            if i.mnemonic == "call" and i.op_str.startswith("0x")] == [
        g5.STREAM_SAVE_FN, g5.STREAM_SAVE_FN, g5.STREAM_SAVE_FN,
    ]
    assert [i.operands[0].imm for i in optional_insns
            if i.mnemonic == "call" and i.op_str.startswith("0x")] == [
        g5.STREAM_SAVE_FN, g5.STREAM_SAVE_FN, g5.STREAM_SAVE_FN,
    ]
    assert save.endswith(b"\xe9" + (g5.SAVE_CONTINUATION_VA - (0x500900 + len(save))).to_bytes(
        4, "little", signed=True))
    assert optional.endswith(b"\xe9" + (
        g5.SAVE_OPTIONAL_CONTINUATION_VA - (0x500980 + len(optional))).to_bytes(
            4, "little", signed=True))
    assert g5.SAVE_HOOK_OLD == bytes.fromhex("b8 7c a9 4d 00 57 ff d0")
    assert g5.SAVE_OPTIONAL_HOOK_OLD == g5.SAVE_HOOK_OLD
    assert g5.SAVE_HOOK_VA == 0x1210257 and g5.SAVE_OPTIONAL_HOOK_VA == 0x121026F
    # The third close is the native short-write failure path: it must remain
    # untouched and return failure instead of receiving a success footer.
    assert 0x121027C not in (g5.SAVE_HOOK_VA, g5.SAVE_OPTIONAL_HOOK_VA)
    assert len(g5.COUNT_CAP_PATCHES) == 5


def test_load_stages_true_eof_footer_then_commits_after_native_reset():
    entries = 0x2201000
    scratch = 0x3000000
    flag = scratch + g5.SIDE_BYTES
    stage = g5._sidecar_stage_load_asm(0x500A00, scratch, flag)
    begin = g5._sidecar_begin_load_asm(0x500B04, flag)
    commit = g5._sidecar_commit_load_asm(0x500B60, entries, scratch, flag)
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    stage_insns = list(decoder.disasm(stage, 0x500A00))
    begin_insns = list(decoder.disasm(begin, 0x500B04))
    commit_insns = list(decoder.disasm(commit, 0x500B60))
    stage_calls = [i.operands[0].imm for i in stage_insns
                   if i.mnemonic == "call" and i.op_str.startswith("0x")]
    assert stage_calls == [g5.STREAM_SEEK_FN, g5.STREAM_LOAD_FN]
    assert any(i.mnemonic == "call" and i.op_str == "eax" for i in stage_insns)
    assert g5.SIDE_BYTES == 408  # 4-byte magic + 4-byte count + 100 DWORDs
    assert any(i.mnemonic == "push" and i.op_str == "0xfffffe68" for i in stage_insns)
    assert any(i.mnemonic == "cmp" and "0x31533547" in i.op_str for i in stage_insns)
    assert any(i.mnemonic == "cmp" and "0xffc" in i.op_str for i in stage_insns)
    assert not any(i.mnemonic == "mov" and "[0x899024]" in i.op_str for i in stage_insns)
    begin_calls = [i.operands[0].imm for i in begin_insns if i.mnemonic == "call"]
    assert begin_calls == [g5.NATIVE_LOAD_FN, g5.NATIVE_POSTLOAD_CLEAR_FN]
    assert any(i.mnemonic == "mov" and "[0x3000198]" in i.op_str
               for i in begin_insns[:2])  # invalidate before every native load
    commit_calls = [i.operands[0].imm for i in commit_insns if i.mnemonic == "call"]
    assert commit_calls == [g5.NATIVE_FINAL_CLEAR_FN]
    assert any(i.mnemonic == "mov" and "[0x899024]" in i.op_str for i in commit_insns)
    reset_call = next(i.address for i in commit_insns if i.mnemonic == "call"
                      and i.operands[0].imm == g5.NATIVE_FINAL_CLEAR_FN)
    commit_count = next(i.address for i in commit_insns if i.mnemonic == "mov"
                        and "[0x899024]" in i.op_str)
    assert reset_call < commit_count
    assert g5.LOAD_FINAL_CLEAR_HOOK_VA == 0x00441549
    assert g5.LOAD_FINAL_CLEAR_HOOK_OLD == bytes.fromhex("e8 b2 30 cf 00")
    assert g5.LOAD_FINAL_CLEAR_CONTINUATION_VA == 0x0044154E
    assert g5.LOAD_STAGE_HOOK_OLD == bytes.fromhex("b8 7c a9 4d 00")
    assert g5.LOAD_SEQUENCE_HOOK_OLD == bytes.fromhex("56 e8 c0 fd c4 00 e8 eb 2e cf 00")


def test_group_overflow_adaptation_keeps_20_bank_and_expands_unit_tags_to_100():
    pool = 0x1B1C000
    exists = 0x22729F8
    entries = 0x24BD404
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    h1 = list(decoder.disasm(g5._group_h1_asm(0x301CC00, pool_base=pool,
                                              exists_base=exists,
                                              selection_base=entries), 0x301CC00))
    h2 = list(decoder.disasm(g5._group_h2_asm(0x301CD00, pool_base=pool,
                                              selection_base=entries), 0x301CD00))
    h3 = list(decoder.disasm(g5._group_h3_asm(0x301CE00, pool_base=pool,
                                              exists_base=exists), 0x301CE00))
    h4 = list(decoder.disasm(g5._group_h4_asm(0x301CF00), 0x301CF00))

    assert any(i.mnemonic == "cmp" and "0x22729f8" in i.op_str for i in h1)
    assert any(i.mnemonic == "lea" and "0x1b1c000" in i.op_str for i in h1)
    assert any(i.mnemonic == "mov" and i.op_str == "ebx, 0x24bd404" for i in h1)
    assert any(i.mnemonic == "cmp" and "0x24bd454" in i.op_str for i in h2)
    assert any(i.mnemonic == "add" and "0x1b1c344" in i.op_str for i in h2)
    assert any(i.mnemonic == "cmp" and len(i.operands) > 1 and i.operands[1].imm == 100
               for i in h3)
    assert any(i.mnemonic == "cmp" and len(i.operands) > 1 and i.operands[1].imm == 4093
               for i in h3)
    assert [i.operands[0].imm for i in h3 if i.mnemonic == "call"] == [
        0x416F40, 0x40F790, 0x40F7D0,
    ]
    assert next(i for i in h4 if i.mnemonic == "call").operands[0].imm == g5.GROUP_H4_TARGET
    assert any(i.mnemonic == "imul" and "0x50" in i.op_str for i in h4)
    assert any(i.mnemonic == "lea" and "0x9570f4" in i.op_str for i in h4)
    assert g5.GROUP_STRIDE == 0x50  # never widen native PlayerStruct groups
    assert g5.GROUP3_END_OLD_BASE == 0x01604054
