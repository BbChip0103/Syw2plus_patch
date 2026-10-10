import hashlib
import importlib.util
import struct
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("shop_table_sync_2608.py")
spec = importlib.util.spec_from_file_location("shop_table_sync_2608", MODULE_PATH)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

TEMP = Path("/home/dev_00/sharedfolder/260320_Syw2plus/260921_temp/archive")
TAIL = "_G2_개인500_공용4092_G5_선택50_G6G7_세이브자리수정R5"
STEM = "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000"
INPUTS = {
    "r5-normal": TEMP / f"{STEM}{TAIL}.exe",
    "r5-fixed": TEMP / f"{STEM}_시작자리고정{TAIL}.exe",
    "g1-normal": TEMP / f"{STEM}{TAIL}_G1.exe",
    "g1-fixed": TEMP / f"{STEM}_시작자리고정{TAIL}_G1.exe",
}
ROW = 18


def _load(name: str) -> bytes:
    path = INPUTS[name]
    if not path.exists():
        pytest.skip("local pinned R5 executables required")
    return path.read_bytes()


@pytest.fixture(scope="module", params=sorted(INPUTS))
def source(request) -> bytes:
    return _load(request.param)


def _changed_ranges(a: bytes, b: bytes) -> list[tuple[int, int]]:
    assert len(a) == len(b)
    ranges: list[tuple[int, int]] = []
    i = 0
    while i < len(a):
        if a[i] != b[i]:
            j = i
            while j < len(a) and a[j] != b[j]:
                j += 1
            ranges.append((i, j))
            i = j
        else:
            i += 1
    return ranges


def test_inputs_are_pinned(source):
    assert hashlib.sha256(source).hexdigest() in mod.INPUT_SHA256.values()


def test_build_only_touches_header_hook_and_cave(source):
    candidate, report = mod.build_candidate(source)
    assert len(candidate) == len(source)
    header = mod._shopai_header(source)
    allowed = [
        (header + 8, header + 12),  # VirtualSize
        (header + 36, header + 40),  # Characteristics
        (mod.HOOK_FILE_OFFSET, mod.HOOK_FILE_OFFSET + len(mod.HOOK_OLD)),
        (mod.CAVE_FILE_OFFSET, mod.CAVE_FILE_OFFSET + report["cave_len"]),
    ]
    for start, end in _changed_ranges(source, candidate):
        assert any(lo <= start and end <= hi for lo, hi in allowed), hex(start)
    assert candidate[mod.HOOK_FILE_OFFSET] == 0xE9
    target = mod.HOOK_VA + 5 + struct.unpack_from("<i", candidate, mod.HOOK_FILE_OFFSET + 1)[0]
    assert target == mod.CAVE_VA


def test_section_becomes_writable_and_covers_cave(source):
    candidate, report = mod.build_candidate(source)
    header = mod._shopai_header(candidate)
    vsize, = struct.unpack_from("<I", candidate, header + 8)
    chars, = struct.unpack_from("<I", candidate, header + 36)
    assert chars == mod.NEW_CHARACTERISTICS
    assert vsize == mod.CAVE_RVA_IN_SECTION + report["cave_len"]
    assert vsize <= 0x1000  # stays in the one already-mapped page


def test_restore_is_exact_inverse(source):
    candidate, _ = mod.build_candidate(source)
    assert mod.restore_candidate(candidate) == source


def test_rejects_unpinned_and_double_apply(source):
    candidate, _ = mod.build_candidate(source)
    with pytest.raises(ValueError):
        mod.build_candidate(candidate)
    with pytest.raises(ValueError):
        mod.build_candidate(source[:-1] + b"\x01")


# --- emulation: the selector must honour edits made at the old 2608 table ---

STACK = 0x00200000
FAKE_UNIT = 0x00300000
RET_SENTINEL = 0x00100000


def _image(data: bytes):
    unicorn = pytest.importorskip("unicorn")
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    count = struct.unpack_from("<H", data, pe + 6)[0]
    opt = pe + 24
    size_of_image = struct.unpack_from("<I", data, opt + 56)[0]
    table = opt + struct.unpack_from("<H", data, pe + 20)[0]
    uc = unicorn.Uc(unicorn.UC_ARCH_X86, unicorn.UC_MODE_32)
    uc.mem_map(0x400000, (size_of_image + 0xFFF) & ~0xFFF)
    uc.mem_write(0x400000, data[:0x1000])
    for i in range(count):
        off = table + i * 40
        vsize, rva, rsize, raw = struct.unpack_from("<IIII", data, off + 8)
        n = min(vsize, rsize)
        uc.mem_write(0x400000 + rva, data[raw : raw + n])
    for base in (STACK, FAKE_UNIT, RET_SENTINEL):
        uc.mem_map(base, 0x10000)
    return uc


def _select(data: bytes, building: int, research: bool) -> int:
    uc = _image(data)
    from unicorn import x86_const as X
    uc.mem_write(FAKE_UNIT + 0x8D, bytes([building, 0]))
    esp = STACK + 0x8000
    uc.mem_write(esp, struct.pack("<II", RET_SENTINEL, int(research)))
    uc.reg_write(X.UC_X86_REG_ESP, esp)
    uc.reg_write(X.UC_X86_REG_ECX, FAKE_UNIT)
    uc.emu_start(mod.HOOK_VA, RET_SENTINEL, count=200000)
    assert uc.reg_read(X.UC_X86_REG_ESP) == esp + 8  # ret 4 balanced
    return uc.reg_read(X.UC_X86_REG_EAX) & 0xFFFF


def _only_row(data: bytes, building: int, field: int, keep: int | None, value: int) -> bytes:
    """Edit the *old* 2608 table: leave one row of ``building`` selectable."""
    out = bytearray(data)
    for i in range(143):
        off = mod.OLD_TABLE_FILE_OFFSET + i * ROW
        if struct.unpack_from("<H", out, off + 2)[0] != building:
            continue
        if i == keep:
            struct.pack_into("<9H", out, off, 0x000F, building, 0xFFFF, 0xFFFF,
                             0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF, 0xFFFF)
            struct.pack_into("<H", out, off + field, value)
        else:
            struct.pack_into("<HH", out, off + 4, 0xFFFF, 0xFFFF)
    return bytes(out)


def _first_row(data: bytes, building: int) -> int:
    for i in range(143):
        if struct.unpack_from("<H", data, mod.OLD_TABLE_FILE_OFFSET + i * ROW + 2)[0] == building:
            return i
    raise AssertionError(building)


@pytest.fixture(scope="module")
def r5() -> bytes:
    return _load("r5-normal")


def test_old_table_edit_is_dead_without_sync(r5):
    building = 0x31
    edited = _only_row(r5, building, 4, _first_row(r5, building), 0x0777)
    assert _select(edited, building, research=False) != 0x0777


def test_old_table_production_edit_reaches_selector(r5):
    candidate, _ = mod.build_candidate(r5)
    building = 0x31
    edited = _only_row(candidate, building, 4, _first_row(r5, building), 0x0777)
    assert _select(edited, building, research=False) == 0x0777


def test_old_table_research_edit_reaches_selector(r5):
    candidate, _ = mod.build_candidate(r5)
    building = 0x31
    edited = _only_row(candidate, building, 6, _first_row(r5, building), 0x0055)
    assert _select(edited, building, research=True) == 0x0055


def test_appended_shop_rows_survive_sync(r5):
    candidate, _ = mod.build_candidate(r5)
    # Remove every old-table research row of the market; only RID 20 remains.
    edited = _only_row(candidate, 0x30, 6, None, 0)
    assert _select(edited, 0x30, research=True) == 20
