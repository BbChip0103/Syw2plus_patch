import importlib.util
from pathlib import Path
import pytest

from tools import runtime_env

spec = importlib.util.spec_from_file_location(
    "g4_search_margin_budget_v2", Path(__file__).with_name("g4_search_margin_budget_v2.py")
)
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)


@pytest.fixture
def original():
    try:
        _source, exe = runtime_env.validate_original_source(runtime_env.DEFAULT_SOURCE)
    except runtime_env.RuntimeSafetyError:
        pytest.skip("Local original game required")
    return exe.read_bytes()


def test_only_documented_instruction_bytes_change(original):
    result = patch.patched_bytes(original)
    allowed = {i for off, before, _ in patch.EDITS for i in range(off, off + len(before))}
    assert len(result) == len(original)
    assert {i for i, (a, b) in enumerate(zip(original, result)) if a != b} <= allowed
    for off, _, after in patch.EDITS:
        assert result[off : off + len(after)] == after


def test_edits_raise_bounding_box_margin_from_30_to_60_tiles(original):
    assert len(patch.EDITS) == 4
    for offset, before, after in patch.EDITS:
        assert original[offset : offset + len(before)] == before
    result = patch.patched_bytes(original)
    # Two `lea esi,[eax-0x1e]` disp8 sites: -30 (0xe2) -> -60 (0xc4).
    for offset in (0x1AFC1, 0x1AFED):
        assert original[offset : offset + 3] == bytes.fromhex("8d70e2")
        assert result[offset : offset + 3] == bytes.fromhex("8d70c4")
    # Two `add eax,0x1e` imm8 sites: +30 (0x1e) -> +60 (0x3c).
    for offset in (0x1AFCB, 0x1AFF6):
        assert original[offset : offset + 3] == bytes.fromhex("83c01e")
        assert result[offset : offset + 3] == bytes.fromhex("83c03c")


def test_rejects_wrong_version():
    with pytest.raises(ValueError, match="SHA256"):
        patch.patched_bytes(b"not the original")


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
