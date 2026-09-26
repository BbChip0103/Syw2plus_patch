from pathlib import Path
import struct

from tools import g4_difficulty_absence as difficulty


def test_report_accepts_pinned_speed_lobby_and_text_evidence(tmp_path: Path, monkeypatch) -> None:
    exe = tmp_path / "game.exe"
    exe.write_bytes(b"exe")
    texts = tuple(tmp_path / name for name in difficulty.TEXT_NAMES)
    all_labels = " ".join(difficulty.REQUIRED_LABELS).encode("cp949")
    for path in texts:
        path.write_bytes(all_labels)
    speed = b"".join(struct.pack("<I", address) for address in (
        0x00975B2C, 0x00B93960, 0x00B93964, 0x006695A4, 0x004ED80C,
    )) + b"\xB8\x3C\x00\x00\x00\xC3\xFF\x24\x85\x24\x66\x41\x00"
    lobby = b"".join(b"\x66\xA3" + struct.pack("<I", address)
                     for address in difficulty.LOBBY_WORD_TARGETS)
    lobby += b"\x89\x15" + struct.pack("<I", 0x00632D38)
    monkeypatch.setattr(difficulty, "_slice", lambda image, start, end: speed if start == 0x004165C0 else lobby)
    monkeypatch.setattr(
        difficulty, "_sha256",
        lambda path: difficulty.EXPECTED_EXE_SHA256 if path == exe else "1" * 64,
    )
    report = difficulty.build_report(exe, texts)
    assert report["classification"] == "NO_FREE_BATTLE_DIFFICULTY_SELECTOR"
    assert report["activation_allowed"] is False


def test_report_rejects_invented_difficulty_label(tmp_path: Path, monkeypatch) -> None:
    exe = tmp_path / "game.exe"
    exe.write_bytes(b"exe")
    texts = tuple(tmp_path / name for name in difficulty.TEXT_NAMES)
    labels = " ".join((*difficulty.REQUIRED_LABELS, "난이도")).encode("cp949")
    for path in texts:
        path.write_bytes(labels)
    monkeypatch.setattr(difficulty, "_slice", lambda *args: b"")
    monkeypatch.setattr(difficulty, "_sha256", lambda path: difficulty.EXPECTED_EXE_SHA256)
    report = difficulty.build_report(exe, texts)
    assert report["classification"] == "EVIDENCE_INVALID"
    assert report["registries"][0]["forbidden_present"] == ["난이도"]
