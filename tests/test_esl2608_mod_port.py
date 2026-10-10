from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path

import pytest

from patches.ai import shop_table_sync_2608 as sync
from tools import esl2608_mod_port as port

TEMP = Path("/home/dev_00/sharedfolder/260320_Syw2plus/260921_temp")
ORIGINAL = TEMP / "[ESL]Syw2plus 2608" / "[ESL]Syw2plus 2608.exe"
STEM = "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000"
TAIL = "_G2_개인500_공용4092_G5_선택50_G6G7_세이브자리수정R5"
R5 = TEMP / "archive" / f"{STEM}{TAIL}.exe"
R5_G1 = TEMP / "archive" / f"{STEM}{TAIL}_G1.exe"
MIRROR_SOURCE = Path(__file__).resolve().parents[1] / "tools/inmm_stub/g1_mirror2x.c"
BASE = 0x400000


def _read(path: Path) -> bytes:
    if not path.exists():
        pytest.skip("local pinned ESL2608 original/R5 executables required")
    return path.read_bytes()


@pytest.fixture(scope="module")
def original() -> bytes:
    return _read(ORIGINAL)


@pytest.fixture(scope="module")
def r5() -> bytes:
    return _read(R5)


@pytest.fixture(scope="module")
def r5_g1() -> bytes:
    return _read(R5_G1)


@pytest.fixture(scope="module")
def r5_sync(r5: bytes) -> bytes:
    return sync.build_candidate(r5)[0]


def _edit(image: bytes, va: int, new: bytes, old: bytes | None = None) -> bytes:
    off = va - BASE
    if old is not None:
        assert image[off : off + len(old)] == old, image[off : off + len(old)].hex()
    out = bytearray(image)
    out[off : off + len(new)] = new
    return bytes(out)


def _psn_edit(image: bytes, va: int, new: bytes) -> bytes:
    off = 0xFC000 + va - 0x01090000
    assert not any(image[off : off + len(new)])
    out = bytearray(image)
    out[off : off + len(new)] = new
    return bytes(out)


def _units(report: dict) -> list[dict]:
    return report["units"]


def _only(report: dict) -> dict:
    units = _units(report)
    assert len(units) == 1, units
    return units[0]


def _diff_positions(a: bytes, b: bytes) -> set[int]:
    assert len(a) == len(b)
    return {i for i in range(len(a)) if a[i] != b[i]}


def test_original_pin(original: bytes) -> None:
    assert hashlib.sha256(original).hexdigest() == port.ORIGINAL_SHA256


def test_identical_mod_is_a_noop(original: bytes, r5: bytes) -> None:
    out, report = port.port_bytes(original, original, r5)
    assert out == r5
    assert report["counts"] == {}


def test_relocation_map_matches_every_r5_operand_rewrite(original: bytes, r5: bytes) -> None:
    evidence = port.target_evidence(original, r5)
    checked = 0
    for value, new_values in evidence.rewrites.items():
        mapped = port.REGION_MAP.inside(value)
        if mapped is None:
            continue
        # The static map must be the dominant R5 rewrite for every in-range
        # operand; a lone unrelated outlier (e.g. a G6/G7 zeroing) is tolerated
        # and is exactly why the port prefers REGION_MAP over learned evidence.
        assert mapped[1] in set(new_values), (hex(value), new_values)
        assert new_values.count(mapped[1]) >= len(new_values) - 1, (hex(value), new_values)
        checked += 1
    assert checked >= 15
    # Selection end and the 1-based active-list base sit just outside their regions;
    # R5 rewrote every occurrence, so the learned evidence resolves them.
    assert port.REGION_MAP.inside(0x00899078) is None
    assert evidence.consistent(0x00899078) == 0x018A60CC
    assert evidence.consistent(0x00974FA6) == 0x018909D6
    # Age-array end is also a separate variable: R5 kept 5 of 6 references.
    assert evidence.consistent(0x0089A388) is None


def test_region_map_per_array_deltas() -> None:
    m = port.REGION_MAP
    assert m.inside(0x0066B790 + 0x758 + 0x10)[1] == 0x0112E000 + 0x758 + 0x10
    assert m.inside(0x008990C8 + 6)[1] == 0x018849F8 + 6
    assert m.inside(0x00899A28)[1] == 0x018869F2
    assert m.inside(0x0089C2C8)[1] == 0x0188C9E0  # list-A trailing count word
    assert m.inside(0x0089D58A)[1] == 0x018909D6  # list-B trailing count word
    assert m.inside(0x00975908)[1] == 0x018929D2  # active-list trailing count word
    assert m.inside(0x00899024)[1] == 0x018A6000
    assert m.inside(0x00899028 + 8)[1] == 0x018A600C
    assert m.inside(0x0110C000 + 16)[1] == 0x01896010


def test_ai_table_edit_is_copied_and_warns_without_sync(original: bytes, r5: bytes) -> None:
    va = sync.OLD_TABLE_VA + 18 * 3 + 2
    mod = _edit(original, va, bytes([original[va - BASE] ^ 0x01]))
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "DATA"
    assert out[va - BASE] == mod[va - BASE]
    assert any(w["code"] == "ai_table_without_sync" for w in report["warnings"])


def test_ai_table_edit_lands_at_old_table_with_sync_layer(original: bytes, r5_sync: bytes) -> None:
    va = sync.OLD_TABLE_VA + 18 * 10 + 4
    mod = _edit(original, va, b"\x07\x00")
    out, report = port.port_bytes(original, mod, r5_sync)
    assert report["target"]["sync_layer"] is True
    assert _only(report)["kind"] == "DATA"
    assert out[va - BASE : va - BASE + 2] == b"\x07\x00"
    assert not report["warnings"]
    assert _diff_positions(out, r5_sync) <= {va - BASE, va - BASE + 1}


def test_new_pool_immediate_is_relocated(original: bytes, r5: bytes) -> None:
    mod = _edit(original, 0x00450981, b"\xb8" + struct.pack("<I", 0x0066B790 + 0x758 * 3 + 0x40),
                old=b"\xb8\x04\x00\x00\x00")
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "RELOC"
    assert struct.unpack_from("<I", out, 0x00450982 - BASE)[0] == 0x0112E000 + 0x758 * 3 + 0x40
    assert unit["relocations"][0]["region"] == "unit_pool"


def test_new_pool_displacement_is_relocated(original: bytes, r5: bytes) -> None:
    mod = _edit(original, 0x00450981, b"\xa1" + struct.pack("<I", 0x0066B790 + 0x10),
                old=b"\xb8\x04\x00\x00\x00")
    out, report = port.port_bytes(original, mod, r5)
    assert _only(report)["kind"] == "RELOC"
    assert out[0x00450981 - BASE] == 0xA1
    assert struct.unpack_from("<I", out, 0x00450982 - BASE)[0] == 0x0112E010


def test_psncode_cave_references_are_relocated(original: bytes, r5: bytes) -> None:
    cave = 0x01091800
    code = (
        b"\xa1" + struct.pack("<I", 0x00899028 + 8)  # mov eax,[selection entry 2]
        + b"\x66\x8b\x0d" + struct.pack("<I", 0x0089C2C8)  # mov cx,[list A count]
        + b"\xc3"
    )
    mod = _psn_edit(original, cave, code)
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "RELOC"
    off = 0xFC000 + cave - 0x01090000
    assert struct.unpack_from("<I", out, off + 1)[0] == 0x018A600C
    assert struct.unpack_from("<I", out, off + 8)[0] == 0x0188C9E0
    assert out[off + len(code) - 1] == 0xC3


def test_edit_of_g2_rewritten_operand_conflicts(original: bytes, r5: bytes) -> None:
    # 0x403484: cmp word [eax*2+0x8990C8],0 ; G2 rewrote the displacement.
    mod = _edit(original, 0x00403488, b"\xca", old=b"\xc8")
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "CONFLICT"
    assert "G2" in unit["conflict"]["owner"]
    assert unit["conflict"]["target_hex"] and unit["conflict"]["modded_hex"]
    assert out == r5


def test_edit_next_to_g2_operand_keeps_target_operand(original: bytes, r5: bytes) -> None:
    # Same instruction, but only the imm8 changes: merge keeps the relocated displacement.
    mod = _edit(original, 0x0040348C, b"\x01", old=b"\x00")
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] != "CONFLICT"
    assert out[0x0040348C - BASE] == 0x01
    assert out[0x00403488 - BASE : 0x0040348C - BASE] == r5[0x00403488 - BASE : 0x0040348C - BASE]
    assert unit["kept_target_bytes"]


def test_edit_of_g5_hook_conflicts_and_names_trampoline(original: bytes, r5: bytes) -> None:
    mod = _edit(original, 0x00409CBA, b"\xbe", old=b"\xbd")
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "CONFLICT"
    assert ".g5code" in unit["conflict"]["detail"]
    assert out == r5


def test_g1_runtime_hook_conflicts_only_on_g1_target(
    original: bytes, r5: bytes, r5_g1: bytes
) -> None:
    mod = _edit(original, 0x00465B33, b"\x54", old=b"\x53")
    out, report = port.port_bytes(original, mod, r5_g1)
    unit = _only(report)
    assert unit["kind"] == "CONFLICT"
    assert "G1" in unit["conflict"]["owner"]
    assert out == r5_g1
    out_plain, report_plain = port.port_bytes(original, mod, r5)
    assert _only(report_plain)["kind"] != "CONFLICT"
    assert out_plain[0x00465B33 - BASE] == 0x54


def test_plain_code_edit_is_applied(original: bytes, r5: bytes) -> None:
    mod = _edit(original, 0x00450636, b"\xb8\x02\x00\x00\x00", old=b"\xb8\x01\x00\x00\x00")
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "PLAIN"
    assert out[0x00450637 - BASE] == 0x02
    assert _diff_positions(out, r5) == {0x00450637 - BASE}


def test_capacity_constant_is_applied_but_flagged(original: bytes, r5: bytes) -> None:
    mod = _edit(original, 0x00450636, b"\xb8" + struct.pack("<I", 1200), old=b"\xb8\x01\x00\x00\x00")
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "SUSPECT"
    assert struct.unpack_from("<I", out, 0x00450637 - BASE)[0] == 1200
    assert any(s["value"] == "0x4b0" for s in unit["suspects"])


def test_pool_immediate_in_push_is_flagged_not_rewritten(original: bytes, r5: bytes) -> None:
    mod = _edit(original, 0x00450981, b"\x68" + struct.pack("<I", 0x0066B7B0),
                old=b"\xb8\x04\x00\x00\x00")
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "SUSPECT"
    assert struct.unpack_from("<I", out, 0x00450982 - BASE)[0] == 0x0066B7B0
    assert unit["suspects"][0]["suggested"] == "0x112e020"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda b: b + bytes(0x1000),  # appended section raw data
        lambda b: b[:0x3C] + b"\x00" + b[0x3D:],  # header changed
        lambda b: b[: 0x1F0 + 40 + 39] + b"\xe0" + b[0x1F0 + 40 + 40 :],  # .rdata flags changed
    ],
)
def test_non_pinned_layout_is_rejected(original: bytes, r5: bytes, mutate) -> None:
    with pytest.raises(port.LayoutError):
        port.port_bytes(original, mutate(original), r5)


def test_added_section_is_reported(original: bytes, r5: bytes) -> None:
    import pefile

    pe = pefile.PE(data=original, fast_load=True)
    table = pe.sections[0].get_file_offset()
    pe_off = pe.DOS_HEADER.e_lfanew
    pe.close()
    mod = bytearray(original)
    struct.pack_into("<H", mod, pe_off + 6, 7)
    mod[table + 6 * 40 : table + 7 * 40] = b".modsec\0" + struct.pack("<IIII", 0x1000, 0xD2D000,
                                                                     0x1000, 0x104000) + bytes(16)
    mod += bytes(0x1000)
    with pytest.raises(port.LayoutError, match="섹션"):
        port.port_bytes(original, bytes(mod), r5)


def test_unpinned_target_is_rejected(original: bytes) -> None:
    with pytest.raises(ValueError, match="target"):
        port.port_bytes(original, original, original)


def test_target_unchanged_outside_applied_runs(original: bytes, r5_g1: bytes) -> None:
    mod = _edit(original, 0x00450636, b"\xb8\x02\x00\x00\x00")
    mod = _edit(mod, 0x00450981, b"\xa1" + struct.pack("<I", 0x0066B790 + 0x10))
    mod = _edit(mod, 0x00403488, b"\xca")  # conflict
    mod = _edit(mod, 0x00465B33, b"\x54")  # G1 conflict
    mod = _edit(mod, sync.OLD_TABLE_VA + 5, b"\x09")
    out, report = port.port_bytes(original, mod, r5_g1)
    allowed: set[int] = set()
    for unit in _units(report):
        if unit["kind"] == "CONFLICT":
            continue
        allowed.update(unit["applied_offsets"])
    changed = _diff_positions(out, r5_g1)
    assert changed <= allowed
    assert 0x00403488 - BASE not in changed and 0x00465B33 - BASE not in changed
    assert report["counts"]["CONFLICT"] == 2


def test_g1_site_table_covers_mirror_prologue_hooks() -> None:
    source = MIRROR_SOURCE.read_text(encoding="utf-8")
    defines = dict(re.findall(r"#define (G1_\w+) (0x[0-9A-Fa-f]+|\d+)u", source))
    installed = set(re.findall(r"install_one\((G1_\w+),", source))
    sites = {(va, length) for va, length, _ in port.G1_RUNTIME_SITES}
    assert installed
    for name in installed:
        length = int(defines.get(f"{name}_LEN", "8"), 0)
        assert (int(defines[name], 0), length) in sites, name


def test_g1_site_bytes_are_untouched_in_g1_target(original: bytes, r5_g1: bytes) -> None:
    for va, length, name in port.G1_RUNTIME_SITES:
        off = va - BASE
        assert r5_g1[off : off + length] == original[off : off + length], name


def test_cli_dry_run_and_exclusive_write(original: bytes, r5: bytes, tmp_path: Path) -> None:
    orig_path = tmp_path / "orig.exe"
    mod_path = tmp_path / "mod.exe"
    target_path = tmp_path / "target.exe"
    orig_path.write_bytes(original)
    mod_path.write_bytes(_edit(original, 0x00450636, b"\xb8\x02\x00\x00\x00"))
    target_path.write_bytes(r5)
    out_path = tmp_path / "out" / "ported.exe"
    report = port.run(orig_path, mod_path, target_path, out_path, dry_run=True)
    assert report["counts"] == {"PLAIN": 1}
    assert not out_path.exists()
    report = port.run(orig_path, mod_path, target_path, out_path)
    assert hashlib.sha256(out_path.read_bytes()).hexdigest() == report["output_sha256"]
    saved = json.loads(out_path.with_suffix(".exe.json").read_text(encoding="utf-8"))
    assert saved["counts"] == {"PLAIN": 1}
    assert "요약" in out_path.with_suffix(".exe.md").read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        port.run(orig_path, mod_path, target_path, out_path)
    with pytest.raises(ValueError, match="input"):
        port.run(orig_path, mod_path, target_path, target_path)
    assert target_path.read_bytes() == r5


# --------------------------------------------------------------------------- #
# Review findings (H1-H3, M1-M2, L1-L3)
# --------------------------------------------------------------------------- #
PSN_CAVE = 0x01091800


def _psn_off(va: int) -> int:
    return 0xFC000 + va - 0x01090000


def _rel_call(src_va: int, dest_va: int, opcode: int = 0xE8) -> bytes:
    return bytes([opcode]) + struct.pack("<i", dest_va - (src_va + 5))


def test_h1_branch_targets_are_not_learned_as_relocations(original: bytes, r5: bytes) -> None:
    evidence = port.target_evidence(original, r5)
    assert evidence.consistent(0x004010B0) is None
    mod = _edit(original, 0x00450636, b"\xb8" + struct.pack("<I", 0x004010B0))
    out, report = port.port_bytes(original, mod, r5)
    assert _only(report)["kind"] == "PLAIN"
    assert struct.unpack_from("<I", out, 0x00450637 - BASE)[0] == 0x004010B0


def test_h1_added_rel_call_into_code_is_plain(original: bytes, r5: bytes) -> None:
    code = _rel_call(PSN_CAVE, 0x00450636) + b"\xc3"
    out, report = port.port_bytes(original, _psn_edit(original, PSN_CAVE, code), r5)
    assert _only(report)["kind"] == "PLAIN"
    assert out[_psn_off(PSN_CAVE) : _psn_off(PSN_CAVE) + len(code)] == code


def test_h1_added_rel_call_outside_code_is_suspect(original: bytes, r5: bytes) -> None:
    code = _rel_call(PSN_CAVE, 0x0066B790) + b"\xc3"
    _out, report = port.port_bytes(original, _psn_edit(original, PSN_CAVE, code), r5)
    unit = _only(report)
    assert unit["kind"] == "SUSPECT"
    assert "분기" in unit["suspects"][0]["reason"]


def _data_slack(original: bytes) -> int:
    import pefile

    pe = pefile.PE(data=original, fast_load=True)
    sec = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".data")
    raw, size = sec.PointerToRawData, sec.SizeOfRawData
    pe.close()
    zero = original[raw : raw + size].rfind(bytes(64))
    assert zero > 0
    return raw + zero + 16


def test_h2_data_slack_cave_is_relocated(original: bytes, r5: bytes) -> None:
    off = _data_slack(original)
    code = b"\xa1" + struct.pack("<I", 0x00899030) + b"\xc3"
    mod = bytearray(original)
    mod[off : off + len(code)] = code
    out, report = port.port_bytes(original, bytes(mod), r5)
    assert _only(report)["kind"] == "RELOC"
    assert struct.unpack_from("<I", out, off + 1)[0] == 0x018A600C


def test_h2_data_dword_in_region_is_suspect(original: bytes, r5: bytes) -> None:
    off = next(o for o in range(0xED000, 0xF0000, 4) if all(original[o : o + 8]))
    mod = bytearray(original)
    struct.pack_into("<I", mod, off, 0x0066B7A0)
    out, report = port.port_bytes(original, bytes(mod), r5)
    unit = _only(report)
    assert unit["kind"] == "SUSPECT"
    assert any(s["suggested"] == "0x112e010" for s in unit["suspects"])
    assert struct.unpack_from("<I", out, off)[0] == 0x0066B7A0


def test_h3_disp_missed_by_vote_is_relocated(original: bytes, r5: bytes) -> None:
    import capstone

    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    md.detail = True
    va = 0x0042471C
    insn = next(md.disasm(original[va - BASE : va - BASE + 16], va))
    off = va - BASE + insn.disp_offset
    assert r5[off : off + 4] == original[off : off + 4]
    mod = bytearray(original)
    struct.pack_into("<I", mod, off, 0x0066B7A0)
    out, report = port.port_bytes(original, bytes(mod), r5)
    assert _only(report)["kind"] == "RELOC"
    assert struct.unpack_from("<I", out, off)[0] == 0x0112E010


def test_h3_unaligned_region_window_is_suspect(original: bytes, r5: bytes) -> None:
    # 0x66B7A0 written into the immediate bytes of two NOP-padded instructions:
    # no decoded field holds it, but the 4-byte window does.
    mod = _edit(original, 0x00450636, b"\x90\xa0\xb7\x66\x00", old=b"\xb8\x01\x00\x00\x00")
    _out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "SUSPECT"
    assert any(s["value"] == "0x66b7a0" for s in unit["suspects"])


def test_m1_sync_target_keeps_ai_table_reference(
    original: bytes, r5: bytes, r5_sync: bytes
) -> None:
    code = b"\xa1" + struct.pack("<I", 0x004EC518) + b"\xc3"
    mod = _psn_edit(original, PSN_CAVE, code)
    out, report = port.port_bytes(original, mod, r5_sync)
    assert _only(report)["kind"] == "PLAIN"
    assert struct.unpack_from("<I", out, _psn_off(PSN_CAVE) + 1)[0] == 0x004EC518
    out, report = port.port_bytes(original, mod, r5)
    assert struct.unpack_from("<I", out, _psn_off(PSN_CAVE) + 1)[0] == 0x0112D004
    assert any(w["code"] == "ai_table_ref_without_sync" for w in report["warnings"])


@pytest.mark.parametrize(
    "va,new",
    [
        (0x004ECF22, b"\x0f\x00"),  # sentinel overwritten (table extension)
        (0x004ECF24, b"\x0f\x00"),  # row written past the sentinel
        (sync.OLD_TABLE_VA + 18 * 50, b"\xfe\xff"),  # early sentinel hides the shop rows
    ],
)
def test_m2_ai_table_shape_edits_conflict(original: bytes, r5_sync: bytes, va: int, new: bytes) -> None:
    out, report = port.port_bytes(original, _edit(original, va, new), r5_sync)
    unit = _only(report)
    assert unit["kind"] == "CONFLICT"
    assert "143" in unit["conflict"]["detail"]
    assert out == r5_sync


def test_l1_imm8_constant_is_suspect(original: bytes, r5: bytes) -> None:
    mod = _edit(original, 0x00450636, b"\x83\xf9\x14\x90\x90", old=b"\xb8\x01\x00\x00\x00")
    _out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "SUSPECT"
    assert any(s["value"] == "0x14" for s in unit["suspects"])


def test_l2_code_slice_stops_at_raw_data(original: bytes) -> None:
    psn = next(s for s in port._sections(original) if s.name == b".psncode")
    lo, hi = port._code_slice(psn)
    assert (lo, hi) == (0xFC000, 0xFE000)


def _write_inputs(tmp_path: Path, original: bytes, mod: bytes, target: bytes) -> tuple[Path, ...]:
    paths = (tmp_path / "orig.exe", tmp_path / "mod.exe", tmp_path / "target.exe")
    for path, data in zip(paths, (original, mod, target)):
        path.write_bytes(data)
    return paths


def test_l3_conflict_refuses_write_without_force(
    original: bytes, r5: bytes, tmp_path: Path
) -> None:
    mod = _edit(original, 0x00403488, b"\xca")
    orig_path, mod_path, target_path = _write_inputs(tmp_path, original, mod, r5)
    out_path = tmp_path / "out.exe"
    with pytest.raises(port.PortRefusedError):
        port.run(orig_path, mod_path, target_path, out_path)
    assert not list(tmp_path.glob("out.exe*"))
    report = port.run(orig_path, mod_path, target_path, out_path, force=True)
    assert out_path.read_bytes() == r5
    assert report["counts"] == {"CONFLICT": 1}


def test_l3_existing_report_blocks_exe_write(original: bytes, r5: bytes, tmp_path: Path) -> None:
    mod = _edit(original, 0x00450636, b"\xb8\x02\x00\x00\x00")
    orig_path, mod_path, target_path = _write_inputs(tmp_path, original, mod, r5)
    out_path = tmp_path / "out.exe"
    (tmp_path / "out.exe.md").write_text("stale", encoding="utf-8")
    with pytest.raises(FileExistsError):
        port.run(orig_path, mod_path, target_path, out_path)
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "mod.exe", "orig.exe", "out.exe.md", "target.exe"
    ]


def test_l3_branch_into_conflict_run_is_flagged(original: bytes, r5: bytes) -> None:
    mod = _edit(original, 0x00403488, b"\xca")
    code = _rel_call(PSN_CAVE, 0x00403488, 0xE9)
    mod = _psn_edit(mod, PSN_CAVE, code)
    _out, report = port.port_bytes(original, mod, r5)
    branch = next(u for u in report["units"] if u["section"] == ".psncode")
    assert branch["kind"] == "SUSPECT"
    assert any(w["code"] == "branch_into_conflict" for w in report["warnings"])


# --------------------------------------------------------------------------- #
# Re-review: data caves whose tail bytes equal the zero slack, blocking SUSPECTs
# --------------------------------------------------------------------------- #
def _data_cave_va(original: bytes) -> tuple[int, int]:
    off = _data_slack(original)
    return off, port._file_to_va(port._sections(original), off)


def _put(image: bytes, off: int, code: bytes) -> bytes:
    out = bytearray(image)
    out[off : off + len(code)] = code
    return bytes(out)


def test_data_cave_ending_in_jmp_with_zero_tail_is_relocated(original: bytes, r5: bytes) -> None:
    off, va = _data_cave_va(original)
    code = b"\xa1" + struct.pack("<I", 0x00899030)
    code += _rel_call(va + len(code), PSN_CAVE, 0xE9)
    assert code[-1] == 0  # the tail byte equals the zero slack, so the diff run drops it
    out, report = port.port_bytes(original, _put(original, off, code), r5)
    unit = _only(report)
    assert unit["kind"] == "RELOC" and unit["data_cave"]
    assert struct.unpack_from("<I", out, off + 1)[0] == 0x018A600C
    assert out[off + 5 : off + len(code)] == code[5:]


def _store_cave() -> bytes:
    # mov eax,[sel+8]; mov [sel+12],eax  -- the last byte is 00 (zero slack)
    return b"\xa1" + struct.pack("<I", 0x00899030) + b"\xa3" + struct.pack("<I", 0x00899034)


def test_data_cave_ending_in_00_reached_by_branch_is_relocated(
    original: bytes, r5: bytes
) -> None:
    off, va = _data_cave_va(original)
    mod = _put(original, off, _store_cave())
    mod = _psn_edit(mod, PSN_CAVE, _rel_call(PSN_CAVE, va, 0xE9))
    out, report = port.port_bytes(original, mod, r5)
    cave = next(u for u in report["units"] if u["section"] == ".data")
    assert cave["kind"] == "RELOC" and cave["data_cave"]
    assert struct.unpack_from("<I", out, off + 1)[0] == 0x018A600C
    assert struct.unpack_from("<I", out, off + 6)[0] == 0x018A6010


def test_unreached_unterminated_data_cave_is_blocking_suspect(
    original: bytes, r5: bytes, tmp_path: Path
) -> None:
    off, _va = _data_cave_va(original)
    mod = _put(original, off, _store_cave())
    out, report = port.port_bytes(original, mod, r5)
    unit = _only(report)
    assert unit["kind"] == "SUSPECT" and not unit.get("data_cave")
    assert struct.unpack_from("<I", out, off + 1)[0] == 0x00899030
    assert all(s["blocking"] for s in unit["suspects"])
    paths = _write_inputs(tmp_path, original, mod, r5)
    with pytest.raises(port.PortRefusedError):
        port.run(*paths, tmp_path / "out.exe")


def test_data_slack_pointer_table_is_not_rewritten(original: bytes, r5: bytes) -> None:
    off, _va = _data_cave_va(original)
    out, report = port.port_bytes(original, _put(original, off, struct.pack("<II", 0x0066B7A0,
                                                                          0x12345678)), r5)
    unit = _only(report)
    assert unit["kind"] == "SUSPECT" and not unit.get("data_cave")
    assert struct.unpack_from("<I", out, off)[0] == 0x0066B7A0


def test_region_suspect_blocks_but_constant_suspect_does_not(
    original: bytes, r5: bytes, tmp_path: Path
) -> None:
    push = _edit(original, 0x00450981, b"\x68" + struct.pack("<I", 0x0066B7B0))
    paths = _write_inputs(tmp_path, original, push, r5)
    with pytest.raises(port.PortRefusedError):
        port.run(*paths, tmp_path / "push.exe")
    const = _edit(original, 0x00450636, b"\xb8" + struct.pack("<I", 1200))
    paths = _write_inputs(tmp_path, original, const, r5)
    report = port.run(*paths, tmp_path / "const.exe")
    assert report["counts"] == {"SUSPECT": 1}
    assert not report["forced"]
