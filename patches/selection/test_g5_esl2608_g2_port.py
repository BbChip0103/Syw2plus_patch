from __future__ import annotations

from pathlib import Path
import struct

import pefile
import pytest

from patches.selection import g5_esl2608_g2_port as mod

ROOT = Path(__file__).resolve().parents[2]
STOCK = ROOT / "Syw2plus" / "syw2plus_original.exe"
INPUT = ROOT.parent / "260921_temp" / "archive"
G2 = {
    "normal": INPUT / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_G2_개인500_공용4092.exe",
    "fixed_start": INPUT
    / "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정_G2_개인500_공용4092.exe",
}
EXPECTED = {
    "normal": "0e28ef57f8eb1f674df544ef84889bd2c51224720a09d0a18122e55f8399d257",
    "fixed_start": "703deaf4c07b44975417f6835c569d65fa03adc2272ff6c75866da4723cd6ea0",
}


@pytest.fixture(scope="module")
def stock() -> bytes:
    if not STOCK.is_file() or not all(p.is_file() for p in G2.values()):
        pytest.skip("pinned stock and ESL2608 G2 executables are required")
    return STOCK.read_bytes()


@pytest.fixture(scope="module")
def built(stock: bytes) -> dict[str, tuple[bytes, bytes, dict]]:
    out = {}
    for variant, path in G2.items():
        g2 = path.read_bytes()
        candidate, report = mod.build_candidate(stock, g2)
        out[variant] = (g2, candidate, report)
    return out


@pytest.mark.parametrize("variant", list(G2))
def test_port_is_deterministic_and_pinned(variant: str, built: dict) -> None:
    _g2, candidate, report = built[variant]
    assert report["variant"] == variant
    assert report["candidate_sha256"] == EXPECTED[variant]
    assert report["caves"] == {"rel32": 25, "abs": 21, "unit_scan_bounds": 2, "chained": 2}
    assert report["inplace"]["ranges"] == 84


@pytest.mark.parametrize("variant", list(G2))
def test_port_appends_sections_and_keeps_g2_bytes(variant: str, built: dict) -> None:
    g2, candidate, _report = built[variant]
    pe = pefile.PE(data=candidate)
    names = [s.Name.rstrip(b"\0") for s in pe.sections]
    assert names == [*mod.G2_SECTION_NAMES, b".g5bss", b".g5code"]
    assert pe.OPTIONAL_HEADER.SizeOfImage == mod.G5CODE_VA - mod.IMAGE_BASE + mod.SECTION_SIZE
    assert len(candidate) == len(g2) + mod.SECTION_SIZE
    # Every G2 section body except .text is untouched, apart from the two
    # ESL fclose call operands in .psncode that now route through the sidecar tail.
    hooked = {site - mod.PSN_CODE_VA + mod.PSN_CODE_RAW + i
              for site in (mod.SAVE_CLOSE_SITE, mod.LOAD_CLOSE_SITE) for i in range(1, 5)}
    for section in pe.sections[1:10]:
        start, size = section.PointerToRawData, section.SizeOfRawData
        changed = {i for i in range(start, start + size) if candidate[i] != g2[i]}
        assert changed <= hooked


@pytest.mark.parametrize("variant", list(G2))
def test_save_load_hooks_chain_g5_then_g2(variant: str, built: dict) -> None:
    _g2, candidate, _report = built[variant]
    code = candidate[-mod.SECTION_SIZE :]
    for site, g2_wrapper in mod.CHAINED_HOOK_SITES.items():
        off = site - mod.IMAGE_BASE
        assert candidate[off] == 0xE8
        target = site + 5 + struct.unpack_from("<i", candidate, off + 1)[0]
        assert mod.G5CODE_VA <= target < mod.G5CODE_VA + mod.SECTION_SIZE
    save_jmp = mod.relocate_code_va(mod.V7_SAVE_TAILJMP)
    load_call = mod.relocate_code_va(mod.V8_LOAD_CALL)
    assert save_jmp is not None and load_call is not None
    for va, wrapper in ((save_jmp, mod.G2_SAVE_WRAPPER), (load_call, mod.G2_LOAD_WRAPPER)):
        rel = struct.unpack_from("<i", code, va - mod.G5CODE_VA + 1)[0]
        assert va + 5 + rel == wrapper


@pytest.mark.parametrize("variant", list(G2))
def test_unit_scans_cover_g2_capacity_and_relocated_pool(variant: str, built: dict) -> None:
    _g2, candidate, _report = built[variant]
    code = candidate[-mod.SECTION_SIZE :]
    for bound_va in mod.UNIT_SCAN_BOUNDS:
        new_va = mod.relocate_code_va(bound_va)
        assert new_va is not None
        assert struct.unpack_from("<I", code, new_va - mod.G5CODE_VA + 2)[0] == 4093
    assert struct.pack("<I", 0x0066B790) not in code
    assert struct.pack("<I", 0x008990C8) not in code
    assert struct.pack("<I", 0x0108C000) not in code


def test_rejects_unpinned_g2_and_original(stock: bytes) -> None:
    g2 = G2["normal"].read_bytes()
    with pytest.raises(ValueError):
        mod.build_candidate(stock, g2[:-1] + b"\x01")
    with pytest.raises(ValueError):
        mod.build_candidate(stock[:-1] + b"\x01", g2)


def test_write_refuses_existing_destination(tmp_path: Path, stock: bytes) -> None:
    destination = tmp_path / "out.exe"
    destination.write_bytes(b"keep")
    with pytest.raises(FileExistsError):
        mod.write_candidate(STOCK, G2["normal"], destination)
    assert destination.read_bytes() == b"keep"


@pytest.mark.parametrize("variant", list(G2))
def test_sidecar_is_written_at_true_stream_end(variant: str, built: dict) -> None:
    """v10's mid-stream sidecar would shift every later block for saves without it."""
    g2, candidate, _report = built[variant]
    for site, stream_fn in zip(mod.V10_APPEND_SITES, (mod.SAVE_STREAM_FN, mod.LOAD_STREAM_FN)):
        off = site - mod.IMAGE_BASE
        assert candidate[off : off + 5] == g2[off : off + 5] == mod._call(site, stream_fn)
    for site, tail in ((mod.SAVE_CLOSE_SITE, mod.SAVE_TAIL_VA), (mod.LOAD_CLOSE_SITE, mod.LOAD_TAIL_VA)):
        off = site - mod.PSN_CODE_VA + mod.PSN_CODE_RAW
        assert g2[off : off + 5] == mod._call(site, mod.FCLOSE_FN)
        assert candidate[off : off + 5] == mod._call(site, tail)
    code = candidate[-mod.SECTION_SIZE :]
    for tail in (mod.SAVE_TAIL_VA, mod.LOAD_TAIL_VA):
        body = code[tail - mod.G5CODE_VA : tail - mod.G5CODE_VA + 0x80].rstrip(b"\0")
        jmp_at = tail + len(body) - 5
        assert body[-5] == 0xE9
        assert jmp_at + 5 + struct.unpack_from("<i", body, len(body) - 4)[0] == mod.FCLOSE_FN
