"""W30 카드 §8 안 B M-b~M-g 기계 회귀. `docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md` 참조.

M-a(구멍 정적+런타임 상수성)는 이 스위트의 범위가 아니다 -- 그건 실제 게임 실행 probe로만
검증 가능하다. 안 A 의 `+0x2100` 구멍은 lap511 middle 이 실제로는 `+0x2018` 용량 1,000칸
dword 리스트의 58번 칸임을 밝혀 REJECT 했다(`analysis/memory_maps/
g2_supply_ledger_hole_rejection_lap511_20260923.md`). 안 B 는 building_count 를
`+0x2016`(그 리스트의 count 워드/원소 배열 사이 2바이트 정렬 패딩)으로 옮기고, `used` 는
제자리(`+0x200c`)에서 4바이트로 확장한다 -- 새 필드가 아니므로 안 A 식 "구멍"이 필요 없다.
이 24k 런타임 재확인은 lap511 §8 이 요구하는 별도 probe 산출물로 남긴다(이 스위트 범위 밖).
"""
import importlib.util
import struct
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "supply_ledger_32bit", Path(__file__).with_name("supply_ledger_32bit.py")
)
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original():
    if not SOURCE.exists():
        pytest.skip("Local original game required")
    return SOURCE.read_bytes()


# --- M-b: 원본 old-bytes 가 §1 표와 바이트 단위 일치 -----------------------------------


def test_all_15_sites_old_bytes_match_before_patching(original):
    # patched_bytes() 는 내부에서 이미 이 검사를 하지만(불일치 시 예외), 여기서는
    # 사이트별로 개별 확인해 어느 사이트가 깨졌는지 바로 드러나게 한다.
    for va, before, _after in patch.EDITS:
        off = va - patch.IMAGE_BASE
        assert original[off : off + len(before)] == before, f"mismatch at 0x{va:08x}"


def test_rejects_wrong_version():
    with pytest.raises(ValueError, match="SHA256"):
        patch.patched_bytes(b"not the original")


# --- M-c: 후보 생성 -> 정확한 원복 -> 원본 SHA 재일치 -----------------------------------


def test_copy_restore_preserves_input(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    target = tmp_path / "experiment.exe"
    patch.create_copy(source, target)
    assert source.read_bytes() == original
    assert target.read_bytes() == patch.patched_bytes(original)
    assert patch.restore(target) == patch.ORIGINAL_SHA256
    assert target.read_bytes() == original


def test_rejects_input_as_target(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    with pytest.raises(ValueError, match="input"):
        patch.create_copy(source, source)
    assert source.read_bytes() == original


def test_existing_destination_not_overwritten(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    target = tmp_path / "experiment.exe"
    target.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        patch.create_copy(source, target)
    assert target.read_bytes() == b"keep"
    assert not Path(str(target) + ".original").exists()


def test_restore_refuses_unknown_modification(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    target = tmp_path / "experiment.exe"
    patch.create_copy(source, target)
    target.write_bytes(b"changed externally")
    with pytest.raises(ValueError, match="exact experimental"):
        patch.restore(target)
    assert target.read_bytes() == b"changed externally"


# --- M-d: diff 가 building 4곳 + used 9곳 + cost-load 2곳(총 15곳)으로 한정 -------------


def test_diff_confined_to_documented_sites(original):
    result = patch.patched_bytes(original)
    assert len(result) == len(original)
    allowed = {i for va, before, _after in patch.EDITS
               for i in range(va - patch.IMAGE_BASE, va - patch.IMAGE_BASE + len(before))}
    changed = {i for i, (a, b) in enumerate(zip(original, result)) if a != b}
    assert changed <= allowed
    assert changed  # 적어도 하나는 실제로 바뀌어야 한다(무동작 패치 방지)


def test_patched_bytes_match_new_encoding_exactly(original):
    result = patch.patched_bytes(original)
    for va, _before, after in patch.EDITS:
        off = va - patch.IMAGE_BASE
        assert result[off : off + len(after)] == after


def test_all_edits_preserve_instruction_length():
    # 길이 보존이 이 패치의 핵심 전제다 -- 다른 코드의 주소/점프 타깃이 전혀 안 바뀐다.
    for va, before, after in patch.EDITS:
        assert len(before) == len(after), f"0x{va:08x} changes length"


def test_used_dword_exactly_covers_old_used_and_building_slots():
    # 제자리 확장이므로 새 4바이트는 옛 used(2B)+옛 building(2B) 자리와 정확히 같아야 한다
    # (그래야 unitcap +0x2010 을 침범하지 않는다).
    assert patch.USED_OFFSET == 0x200C
    assert patch.OLD_BUILDING_OFFSET == patch.USED_OFFSET + 2
    used_span = range(patch.USED_OFFSET, patch.USED_OFFSET + 4)
    assert set(used_span) == set(range(0x200C, 0x2010))


def test_new_building_offset_does_not_collide_with_list_or_known_block(original):
    # +0x2016 은 count 워드(+0x2014)와 dword 원소 배열(+0x2018, 용량 1,000) 사이 패딩이다
    # (lap511 N157). 카드 §8 근거 바이트를 원본에서 직접 재확인한다: 0x43F4C7 `cmp ax,0x3e8`.
    off = 0x0043F4C7 - patch.IMAGE_BASE
    assert original[off : off + 4] == bytes.fromhex("663de803")  # 66 3d e8 03
    element_region = range(patch.LIST_ELEMENTS_OFFSET,
                            patch.LIST_ELEMENTS_OFFSET + patch.LIST_CAPACITY * 4)
    new_field = range(patch.NEW_BUILDING_OFFSET, patch.NEW_BUILDING_OFFSET + 2)
    known_block = range(0x200A, 0x2014)  # count/used(확장 전)/building(구 자리)/unitcap/limit
    assert not (set(element_region) & set(new_field))
    assert not (set(known_block) & set(new_field))
    assert patch.NEW_BUILDING_OFFSET == patch.LIST_COUNT_OFFSET + 2  # 정렬 패딩 위치


def test_relocated_fields_stay_inside_player_struct():
    for owner in range(patch.PS_COUNT):
        struct_start = patch.PS_BASE + owner * patch.PS_STRIDE
        struct_end = struct_start + patch.PS_STRIDE
        used = patch.used_va(owner)
        building = patch.building_va(owner)
        assert struct_start <= used < used + 4 <= struct_end
        assert struct_start <= building < building + 2 <= struct_end


def test_building_relocation_sites_match_known_inventory():
    expected = {0x0043DB24, 0x0043E204, 0x0043EEAD, 0x0043EF9D}
    edits_by_va = {va: (before, after) for va, before, after in patch.EDITS}
    assert expected <= edits_by_va.keys()
    for va in expected:
        before, after = edits_by_va[va]
        # disp32 `0x200e`(`0e 20 00 00`) 만 `0x2016`(`16 20 00 00`)으로 바뀌고 나머지는 불변.
        assert bytes.fromhex("0e200000") in before
        assert before.replace(bytes.fromhex("0e200000"), bytes.fromhex("16200000")) == after


# --- M-e/M-f: 장부 산술 등가성 + 랩 부재 (인코딩 의미 모델) -----------------------------
#
# 실제 CPU 실행 없이, 이 패치가 바꾸는 두 인코딩의 로드/스토어 의미만 모델링한다:
#   원본: 16-bit 폭 저장 + movsx 부호확장 로드 (word, sign-extend to dword)
#   패치: 32-bit 폭 저장 + 그대로 로드 (dword, no extension)
# 두 모델이 같은 정수 v 에 대해 같은 값을 내는지(M-e, v<=32767)와 원본만 랩하는지(M-f,
# v=78000, roster_add 의 구조적 최대 -- lap509 §3/lap510 재확인)를 확인한다.


def _old_word_signextend_roundtrip(v: int) -> int:
    stored = v & 0xFFFF
    return struct.unpack("<h", struct.pack("<H", stored))[0]


def _new_dword_roundtrip(v: int) -> int:
    stored = v & 0xFFFFFFFF
    return struct.unpack("<I", struct.pack("<I", stored))[0]


@pytest.mark.parametrize("v", [0, 1, 20, 1500, 5000, 20000, 32767])
def test_M_e_arithmetic_equivalence_within_int16_range(v):
    assert _old_word_signextend_roundtrip(v) == v
    assert _new_dword_roundtrip(v) == v


def test_M_f_no_wrap_at_structural_max_used():
    # roster_add(`0x43EE30`)가 보는 유일한 상한은 로스터 1,200칸(`cmp ax,0x4b0`), used 자체는
    # cap을 보지 않는다. c_max=65(kind103, lap507 W29) ⇒ 구조적 최대 = 1200*65 = 78,000.
    c_max = 65
    roster_cap = 1200
    structural_max_used = roster_cap * c_max
    assert structural_max_used == 78000

    old_wrapped = _old_word_signextend_roundtrip(structural_max_used)
    new_value = _new_dword_roundtrip(structural_max_used)

    # 78000 & 0xFFFF = 12464 (< 0x8000 이라 양수로 랩 -- lap395 실측 32,785 대 소진과 같은
    # 부류의 현상. 부호가 항상 음수가 되는 건 아니고, "다른 값으로 랩된다"는 것만 보장된다).
    assert old_wrapped != structural_max_used  # 원본 16-bit 장부는 이 값에서 랩
    assert old_wrapped == 12464
    assert new_value == structural_max_used  # 32-bit 장부는 랩 없음


# --- M-g: 구 세이브 blob 길이 불변 ------------------------------------------------------


def test_M_g_stride_and_struct_bounds_unchanged():
    # 이 패치는 stride/span 을 절대 건드리지 않는다(§2-C 금지, 이 패치는 §2-A 만 구현).
    assert patch.PS_STRIDE == 0x3ABC
    assert patch.PS_BASE == 0x956770
    assert patch.PS_COUNT == 8


def test_M_g_bulk_blob_span_matches_lap509_inventory(original):
    # bulk save/load 가 쓰는 고정 길이 span (lap509 §4 근거) -- 이 패치가 즉시값을 하나도
    # 건드리지 않았음을 원본에서 직접 재확인한다.
    save_len_off = 0x440F02 - patch.IMAGE_BASE
    save_ptr_off = 0x440F07 - patch.IMAGE_BASE
    assert original[save_len_off] == 0x68
    assert original[save_ptr_off] == 0x68
    length = struct.unpack_from("<I", original, save_len_off + 1)[0]
    start = struct.unpack_from("<I", original, save_ptr_off + 1)[0]
    assert length == 0xE397C
    assert start == 0x892410
    ps_end = patch.PS_BASE + patch.PS_STRIDE * patch.PS_COUNT
    assert start <= patch.PS_BASE and ps_end <= start + length
