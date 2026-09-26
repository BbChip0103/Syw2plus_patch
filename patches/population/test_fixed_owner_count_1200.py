import importlib.util
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "fixed_owner_count_1200", Path(__file__).with_name("fixed_owner_count_1200.py")
)
assert spec is not None and spec.loader is not None
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
SOURCE = Path(__file__).resolve().parents[2] / "Syw2plus/syw2plus_original.exe"


@pytest.fixture
def original():
    if not SOURCE.exists():
        pytest.skip("Local original game required")
    return SOURCE.read_bytes()


def test_composed_patch_changes_only_existing_five_plus_count_two(original):
    result = patch.patched_bytes(original)
    changed = {i for i, (before, after) in enumerate(zip(original, result)) if before != after}
    assert len(changed) == 7
    assert result[patch.OWNER_COUNT_FILE_OFFSET : patch.OWNER_COUNT_FILE_OFFSET + 4] == (
        patch.OWNER_COUNT_AFTER
    )
    fixed = patch.fixed_supply_bytes(original)
    fixed_changed = {i for i, (before, after) in enumerate(zip(original, fixed)) if before != after}
    assert changed == fixed_changed | {0x1B56E, 0x1B56F}


def test_liveness_and_threshold_policy_are_explicit_metadata():
    assert (patch.NORMAL_MAP_WIDTH, patch.NORMAL_MAP_HEIGHT) == (100, 100)
    assert patch.NORMAL_MAP_LIVENESS_CALL_VA == 0x451130
    assert patch.NORMAL_MAP_LIVENESS_RETURN_VA == 0x4513B0
    assert patch.NORMAL_MAP_LIVENESS_EDX_RESTORED
    assert patch.CPU_BUILD_THRESHOLD_ORIGINAL == 50
    assert patch.CPU_BUILD_THRESHOLD_POLICY == 240


def test_source_guard_and_exact_width_are_preserved():
    assert patch.OWNER_COUNT_BEFORE == bytes.fromhex("fa000000")
    assert patch.OWNER_COUNT_AFTER == bytes.fromhex("b0040000")
    assert len(patch.OWNER_COUNT_BEFORE) == len(patch.OWNER_COUNT_AFTER) == 4
    with pytest.raises(ValueError, match="SHA256"):
        patch.patched_bytes(b"not the original")


def test_copy_restore_and_exclusive_collision(original, tmp_path):
    source = tmp_path / "input.exe"
    target = tmp_path / "syw2plus_supply5000_owner1200_v1.exe"
    source.write_bytes(original)
    patch.create_copy(source, target)
    assert source.read_bytes() == original
    assert target.read_bytes() == patch.patched_bytes(original)
    with pytest.raises(FileExistsError):
        patch.create_copy(source, target)
    assert patch.restore(target) == patch.ORIGINAL_SHA256
    assert target.read_bytes() == original


def test_reapply_and_legacy_name_are_not_accepted(original, tmp_path):
    source = tmp_path / "input.exe"
    source.write_bytes(original)
    legacy = tmp_path / "supply5000.exe"
    with pytest.raises(FileNotFoundError):
        patch.restore(legacy)
    target = tmp_path / "syw2plus_supply5000_owner1200_v1.exe"
    patch.create_copy(source, target)
    with pytest.raises(ValueError, match="SHA256"):
        patch.patched_bytes(target.read_bytes())


@pytest.mark.parametrize("name", [
    "syw2plus_supply5000_owner1200_v1.exe",
    "supply5000.exe",
    "syw2plus_original.exe",
])
def test_candidate_names_are_rejected_before_legacy_launch(original, tmp_path, monkeypatch, name):
    from patches.population import runtime_driver

    root = tmp_path / name.replace(".", "_")
    root.mkdir()
    (root / name).write_bytes(patch.patched_bytes(original))
    with pytest.raises(ValueError, match="SHA256|unsupported"):
        runtime_driver.validate_runtime_executable(root, name)
    calls = []
    monkeypatch.setattr(runtime_driver.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    monkeypatch.setattr(sys, "argv", [
        "runtime_driver.py", "--game-root", str(root), "--prefix", str(tmp_path / "prefix"),
        "--out", str(tmp_path / "out"), "--display", ":99", "--exe", name,
    ])
    with pytest.raises(ValueError, match="SHA256|unsupported"):
        runtime_driver.main()
    assert calls == []
    assert not (tmp_path / "out").exists()


def test_candidate_is_rejected_by_canonical_check_runtime_without_processes(
    original, tmp_path, monkeypatch
):
    from tools import runtime_env

    run = tmp_path / "run"
    game = run / "game"
    game.mkdir(parents=True)
    (game / "syw2plus_original.exe").write_bytes(patch.patched_bytes(original))
    manifest = run / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        runtime_env,
        "_manifest",
        lambda _path: ({"game": {"exe_sha256": runtime_env.ORIGINAL_SHA256}}, game,
                       run / "prefix", run / "output"),
    )
    calls = []
    monkeypatch.setattr(runtime_env.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    monkeypatch.setattr(runtime_env.subprocess, "run", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(runtime_env.RuntimeSafetyError, match="verified original"):
        runtime_env.check_runtime(manifest)
    assert calls == []
    assert not (run / "output").exists()


def test_full_seed_and_guard_bytes_are_unchanged_except_exact_whitelist(original):
    result = patch.patched_bytes(original)
    expected_changed = {
        0x1B56E, 0x1B56F,
        0x1B579, 0x1B57A,
        0x3FFD4, 0x3FFD5, 0x3FFD6,
    }
    assert {i for i, (a, b) in enumerate(zip(original, result)) if a != b} == expected_changed
    assert result[0x1B56D : 0x1B56D + 9] == bytes.fromhex("bab0040000668950fe")
    assert result[0x1B572 : 0x1B576] == original[0x1B572 : 0x1B576]
    assert result[0x1B57B : 0x1B57B + 8] == original[0x1B57B : 0x1B57B + 8]
    assert result[0x1B583 : 0x1B583 + 0x30] == original[0x1B583 : 0x1B583 + 0x30]
