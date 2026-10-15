from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import struct
import subprocess

import numpy as np
import pytest

from tools import g1_hd_convert as hc
from tools import g1_hd_extract as hx


ROOT = Path(__file__).resolve().parents[1]
CC = shutil.which("i686-w64-mingw32-gcc")
WINE = shutil.which("wine")


def _bmp(width: int, height: int, pixels: np.ndarray, palette: bytes) -> bytes:
    stride = (width + 3) & ~3
    rows = pixels[::-1]
    body = b"".join(row.tobytes() + bytes(stride - width) for row in rows)
    offset = 14 + 40 + len(palette)
    dib = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 8, 0, len(body), 2834, 2834, 256, 0)
    return b"BM" + struct.pack("<IHHI", offset + len(body), 0, 0, offset) + dib + palette + body


def _fnv1a(data: bytes) -> int:
    value = 2166136261
    for byte in data:
        value = ((value ^ byte) * 16777619) & 0xFFFFFFFF
    return value


def _build_reader(tmp_path: Path) -> Path:
    compiler = subprocess.run(
        [CC or "", "-m32", "-O2", "-fno-stack-protector", "-mno-stack-arg-probe",
         "-I", str(ROOT / "tools/inmm_stub"),
         str(ROOT / "tools/inmm_stub/g1_hd_native_reader_test.c"),
         "-o", str(tmp_path / "reader.exe"), "-lkernel32", "-luser32"],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert compiler.returncode == 0, compiler.stderr
    return tmp_path / "reader.exe"


def _run_reader(exe: Path, root: Path, name: str, width: int, height: int,
                expected: bytes, *, should_load: bool, prefix: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    private_exe = root / "reader.exe"
    shutil.copy2(exe, private_exe)
    expected_path = root / "expected.bin"
    expected_path.write_bytes(expected)
    environment = os.environ.copy()
    environment.pop("SYW2_G1_HD_PACK", None)
    environment.pop("SYW2_G1_HD_SOURCE", None)
    environment["WINEPREFIX"] = str(prefix)
    environment["WINEDEBUG"] = "-all"
    run = subprocess.run(
        [WINE or "wine", str(private_exe), name, str(width), str(height),
         str(expected_path), "1" if should_load else "0"],
        cwd=root, env=environment, capture_output=True, text=True, timeout=90,
    )
    assert run.returncode == 0, {"exit": run.returncode, "stdout": run.stdout, "stderr": run.stderr}


def _write_source_index(root: Path, source_name: str, hd_name: str) -> None:
    source_sha = hashlib.sha256((root / source_name).read_bytes()).hexdigest()
    (root / "g1_hd_sources.sha256").write_text(
        f"{source_sha}  {hd_name}\n", encoding="ascii"
    )


@pytest.mark.skipif(not CC or not WINE, reason="MinGW i686 and Wine are required for the native reader integration test")
def test_native_bmp_and_sheet_reader_match_python_and_reject_truncation(tmp_path: Path) -> None:
    exe = _build_reader(tmp_path)
    wine_prefix = tmp_path / "wine_prefix"

    bmp_root = tmp_path / "bmp_ok"
    palette = bytes(value for _ in range(256) for value in (1, 2, 3, 0))
    source_pixels = (np.arange(128, dtype=np.uint8).reshape(8, 16) % 200).astype(np.uint8)
    doubled = np.repeat(np.repeat(source_pixels, 2, axis=0), 2, axis=1)
    hd_bmp = _bmp(32, 16, doubled, palette)
    (bmp_root / "portrait.bmp").parent.mkdir(parents=True)
    (bmp_root / "portrait.bmp").write_bytes(_bmp(16, 8, source_pixels, palette))
    (bmp_root / "portrait_hd.bmp").write_bytes(hd_bmp)
    _write_source_index(bmp_root, "portrait.bmp", "portrait_hd.bmp")
    bmp_digest = hc.fnv1a_128(source_pixels.tobytes(), 0)
    assert bmp_digest is not None
    bmp_key = f"h{bmp_digest:08x}_16x8.idx8"
    _run_reader(exe, bmp_root, bmp_key, 16, 8, doubled.tobytes(), should_load=True,
                prefix=wine_prefix)

    bmp_bad = tmp_path / "bmp_truncated"
    (bmp_bad / "portrait.bmp").parent.mkdir(parents=True)
    (bmp_bad / "portrait.bmp").write_bytes(_bmp(16, 8, source_pixels, palette))
    (bmp_bad / "portrait_hd.bmp").write_bytes(hd_bmp[:64])
    _write_source_index(bmp_bad, "portrait.bmp", "portrait_hd.bmp")
    _run_reader(exe, bmp_bad, bmp_key, 16, 8, bytes(128 * 4), should_load=False,
                prefix=wine_prefix)

    sheet_root = tmp_path / "sheet_ok"
    sheet_source = np.array([[1, 2, 3, 4], [5, 6, 7, 8]], dtype=np.uint8)
    # Doubled edge transparencies produce an RLE stream whose byte
    # length collides with the declared raw sheet area without the writer fix.
    sheet_mask = np.array([[False, True, True, True], [False, True, True, True]])
    sheet_stream = hx.rle_encode(sheet_source, sheet_mask)
    source_header = bytearray(hx.SPR_FIXED_HEADER)
    struct.pack_into("<4I", source_header, 0, 9, 2, 1, 1)
    struct.pack_into("<3I", source_header, hx.SPR_SHEET_RECORD, len(sheet_stream), 4, 2)
    source_spr = bytes(source_header) + sheet_stream
    (sheet_root / "SItem001.Spr").parent.mkdir(parents=True)
    (sheet_root / "SItem001.Spr").write_bytes(source_spr)
    doubled_sheet = np.repeat(np.repeat(sheet_source, 2, axis=0), 2, axis=1)
    doubled_mask = np.repeat(np.repeat(sheet_mask, 2, axis=0), 2, axis=1)
    authored_cell = np.array([[21, 22, 23, 24], [31, 32, 33, 34]], dtype=np.uint8)
    doubled_sheet[:2, 4:8] = authored_cell
    hd_spr = hc._encode_spr_sheet_native(source_spr, doubled_sheet, doubled_mask, "rle")
    assert struct.unpack_from("<I", hd_spr, hx.SPR_SHEET_RECORD)[0] != 8 * 4
    (sheet_root / "SItem001_hd.Spr").write_bytes(hd_spr)
    _write_source_index(sheet_root, "SItem001.Spr", "SItem001_hd.Spr")
    cell = sheet_source[0:1, 2:4].tobytes()
    cell_key = f"h{_fnv1a(cell):08x}_2x1.idx8"
    _run_reader(exe, sheet_root, cell_key, 2, 1, authored_cell.tobytes(), should_load=True,
                prefix=wine_prefix)

    sheet_bad = tmp_path / "sheet_truncated"
    (sheet_bad / "SItem001.Spr").parent.mkdir(parents=True)
    (sheet_bad / "SItem001.Spr").write_bytes(source_spr)
    (sheet_bad / "SItem001_hd.Spr").write_bytes(hd_spr[:hx.SPR_FIXED_HEADER + 1])
    _write_source_index(sheet_bad, "SItem001.Spr", "SItem001_hd.Spr")
    _run_reader(exe, sheet_bad, cell_key, 2, 1, bytes(8), should_load=False,
                prefix=wine_prefix)
