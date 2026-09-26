"""SHA-pinned patch safety tests; no Wine sessions launched."""

import importlib.util
import pathlib
import struct
import pytest
import pefile

spec = importlib.util.spec_from_file_location(
    "qhd_probe", pathlib.Path(__file__).with_name("qhd_probe.py")
)
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
SOURCE = pathlib.Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def source():
    if not SOURCE.exists():
        pytest.skip("Private original game asset unavailable")
    return SOURCE


def test_identity_rejected():
    with pytest.raises(ValueError, match="SHA256"):
        q.build(b"not an original game")


def test_roundtrip_and_layout(source, tmp_path):
    before = source.read_bytes()
    target = tmp_path / "probe.exe"
    m = q.apply(source, target)
    p = pefile.PE(data=target.read_bytes())
    assert p.FILE_HEADER.Machine == 0x14C
    assert p.OPTIONAL_HEADER.Magic == 0x10B
    assert p.sections[-1].Name.rstrip(b"\0") == b".qhd"
    start = int(m["terrain_va"], 16)
    dirty = int(m["dirty_va"], 16)
    assert dirty - start > 2560 * 1440
    assert p.get_data(dirty - q.BASE, 4096) == b"\x01" * 4096
    assert struct.unpack("<I", p.get_data(0x464505 - q.BASE, 4))[0] == 2560
    assert struct.unpack("<I", p.get_data(0x46450C - q.BASE, 4))[0] == 1440
    assert len([c for c in m["changes"] if c["reason"].startswith("private all-dirty")]) == 5
    assert (
        int(m["row_table_va"], 16) + 1441 * 4
        <= q.BASE + p.sections[-1].VirtualAddress + p.sections[-1].Misc_VirtualSize
    )
    clear = int(m["clear_trampoline_va"], 16)
    assert p.get_data(clear - q.BASE, 6) == b"\x9c\x60\xfc\x31\xc0\xbf"
    assert p.sections[0].Misc_VirtualSize <= p.sections[0].SizeOfRawData
    assert (
        p.sections[0].VirtualAddress + p.sections[0].Misc_VirtualSize
        <= p.sections[1].VirtualAddress
    )
    q.restore(target)
    assert target.read_bytes() == before == source.read_bytes()


def test_refuse_in_place_and_overwrite(source, tmp_path):
    with pytest.raises(ValueError):
        q.apply(source, source)
    target = tmp_path / "existing.exe"
    target.write_bytes(b"user file")
    with pytest.raises(ValueError):
        q.apply(source, target)
    assert target.read_bytes() == b"user file"


def test_restore_refuses_tampering(source, tmp_path):
    target = tmp_path / "probe.exe"
    q.apply(source, target)
    target.write_bytes(target.read_bytes() + b"changed")
    with pytest.raises(ValueError):
        q.restore(target)
