from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from patches.g1 import r5_g1mm_import as mod

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT.parent / "260921_temp" / "archive"
TAIL = "_G2_개인500_공용4092_G5_선택50_G6G7_세이브자리수정R5.exe"
PORT = {
    "normal": INPUT / ("[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000" + TAIL),
    "fixed_start": INPUT / ("[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1500-500-5000_시작자리고정" + TAIL),
}


def _synthetic() -> bytes:
    data = bytearray(0xEC000)
    site = mod.IMPORT_NAME_OFFSET
    data[site - len(mod.CONTEXT_BEFORE) : site] = mod.CONTEXT_BEFORE
    data[site : site + len(mod.OLD_NAME)] = mod.OLD_NAME
    after = site + len(mod.OLD_NAME)
    data[after : after + len(mod.CONTEXT_AFTER)] = mod.CONTEXT_AFTER
    return bytes(data)


def test_unpinned_input_is_rejected() -> None:
    with pytest.raises(ValueError, match="pinned"):
        mod.build_candidate(_synthetic())


def test_site_guards_reject_changed_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    base = _synthetic()
    monkeypatch.setitem(mod.BASE_SHA256, "normal", hashlib.sha256(base).hexdigest())
    candidate, report = mod.build_candidate(base)
    assert report["changed_offsets"] == ["0xebb5f", "0xebb60"]
    assert candidate[mod.IMPORT_NAME_OFFSET : mod.IMPORT_NAME_OFFSET + 10] == mod.NEW_NAME
    assert mod.restore_candidate(candidate, base) == base
    with pytest.raises(ValueError, match="refusing"):
        mod.restore_candidate(base, base)
    bad = bytearray(base)
    bad[mod.IMPORT_NAME_OFFSET + 1] ^= 1
    monkeypatch.setitem(mod.BASE_SHA256, "normal", hashlib.sha256(bytes(bad)).hexdigest())
    with pytest.raises(ValueError, match="site bytes"):
        mod.build_candidate(bytes(bad))
    ctx = bytearray(base)
    ctx[mod.IMPORT_NAME_OFFSET - 2] ^= 1
    monkeypatch.setitem(mod.BASE_SHA256, "normal", hashlib.sha256(bytes(ctx)).hexdigest())
    with pytest.raises(ValueError, match="preceding"):
        mod.build_candidate(bytes(ctx))


def test_write_refuses_to_overwrite_input(tmp_path: Path) -> None:
    src = tmp_path / "a.exe"
    src.write_bytes(b"x")
    with pytest.raises(ValueError, match="overwrite"):
        mod.write_candidate(src, src)


@pytest.mark.parametrize("variant", list(PORT))
def test_real_r5_exes(variant: str) -> None:
    if not PORT[variant].is_file():
        pytest.skip("pinned R5 executables are required")
    base = PORT[variant].read_bytes()
    candidate, report = mod.build_candidate(base)
    assert report["base_sha256"] == mod.BASE_SHA256[variant]
    assert len(candidate) == len(base)
    diff = [i for i in range(len(base)) if base[i] != candidate[i]]
    assert diff == [mod.IMPORT_NAME_OFFSET + 1, mod.IMPORT_NAME_OFFSET + 2]
    assert candidate.count(b"_INMM.dll") == 0 and candidate.count(b"_G1MM.dll") == 1
    again, _ = mod.build_candidate(base)
    assert again == candidate
    assert mod.restore_candidate(candidate, base) == base
