"""Pre-launch fail-closed gates for the legacy private runtime driver."""

import sys
from pathlib import Path

import pytest

from patches.population import fixed_supply_5000, runtime_driver


ORIGINAL = Path(__file__).resolve().parents[1] / "Syw2plus" / "syw2plus_original.exe"


def _private_root(tmp_path: Path, name: str, payload: bytes) -> Path:
    root = tmp_path / "private"
    root.mkdir(parents=True)
    (root / name).write_bytes(payload)
    return root


def test_exact_original_and_fixed_profiles_are_accepted(tmp_path: Path) -> None:
    original = ORIGINAL.read_bytes()
    root = _private_root(tmp_path, "syw2plus_original.exe", original)
    accepted = runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")
    assert accepted["profile"] == "original"

    fixed_root = _private_root(
        tmp_path / "fixed", "supply5000.exe", fixed_supply_5000.patched_bytes(original)
    )
    accepted = runtime_driver.validate_runtime_executable(fixed_root, "supply5000.exe")
    assert accepted["profile"] == "fixed_supply_5000"


def test_exact_tail_relocated_n1210_profile_is_accepted_under_original_name(
    tmp_path: Path,
) -> None:
    from patches.population import g2_unit_pool_expansion_v1

    candidate, _report = g2_unit_pool_expansion_v1.build_candidate(ORIGINAL.read_bytes(), 1210)
    root = _private_root(tmp_path, "syw2plus_original.exe", candidate)
    accepted = runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")
    assert accepted["profile"] == "g2_unit_pool_expansion_v1_n1210_tail_relocated"


def test_exact_tail_relocated_supply5000_profile_is_accepted_under_original_name(
    tmp_path: Path,
) -> None:
    from patches.population import g2_unit_pool_supply5000_v1

    candidate, _report = g2_unit_pool_supply5000_v1.build_candidate(ORIGINAL.read_bytes(), 1210)
    root = _private_root(tmp_path, "syw2plus_original.exe", candidate)
    accepted = runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")
    assert accepted["profile"] == "g2_unit_pool_expansion_v1_n1210_supply5000"


def test_exact_full_capacity_supply5000_profile_is_accepted_under_original_name(
    tmp_path: Path,
) -> None:
    from patches.population import g2_full_unit_capacity_supply5000_v1

    candidate, _report = g2_full_unit_capacity_supply5000_v1.build_candidate(
        ORIGINAL.read_bytes(), 1250
    )
    root = _private_root(tmp_path, "syw2plus_original.exe", candidate)
    accepted = runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")
    assert accepted["profile"] == "g2_full_unit_capacity_v1_n1250_supply5000"


def test_exact_n4001_product_capacity_profile_is_accepted_under_original_name(
    tmp_path: Path,
) -> None:
    from patches.population import g2_full_capacity_supply5000_owner1200_v1

    candidate, _report = g2_full_capacity_supply5000_owner1200_v1.build_candidate(
        ORIGINAL.read_bytes(), 4001
    )
    root = _private_root(tmp_path, "syw2plus_original.exe", candidate)
    accepted = runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")
    assert accepted["profile"] == "g2_full_capacity_v1_n4001_supply5000_owner1200"


def test_exact_n4001_persistence_profile_is_accepted_under_original_name(
    tmp_path: Path,
) -> None:
    from patches.population import g2_full_capacity_persistence_v1

    candidate, _report = g2_full_capacity_persistence_v1.build_candidate(
        ORIGINAL.read_bytes(), 4001
    )
    root = _private_root(tmp_path, "syw2plus_original.exe", candidate)
    accepted = runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")
    assert (
        accepted["profile"]
        == "g2_full_capacity_v1_n4001_supply5000_owner1200_persistence"
    )


def test_exact_n4001_persistence_compat_profile_is_accepted_under_original_name(
    tmp_path: Path,
) -> None:
    from patches.population import g2_full_capacity_persistence_compat_v1

    candidate, _report = g2_full_capacity_persistence_compat_v1.build_candidate(
        ORIGINAL.read_bytes(), 4001
    )
    root = _private_root(tmp_path, "syw2plus_original.exe", candidate)
    accepted = runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")
    assert accepted["profile"] == "g2_full_capacity_v1_n4001_persistence_compat"


def test_actual_combined_qhd_transform_is_the_allowlisted_profile(tmp_path: Path) -> None:
    from patches.resolution.qhd_probe import build as qhd_build

    original = ORIGINAL.read_bytes()
    qhd, _ = qhd_build(original)
    combined = bytearray(qhd)
    for offset, before, after in fixed_supply_5000.EDITS:
        assert combined[offset : offset + len(before)] == before
        combined[offset : offset + len(before)] = after
    root = _private_root(tmp_path, "supply5000_qhd.exe", bytes(combined))
    accepted = runtime_driver.validate_runtime_executable(root, "supply5000_qhd.exe")
    assert accepted["profile"] == "combined_qhd_fixed_supply_5000"


def test_actual_original_and_fixed_bytes_reject_renamed_profiles(tmp_path: Path) -> None:
    original = ORIGINAL.read_bytes()
    fixed = fixed_supply_5000.patched_bytes(original)
    original_root = _private_root(tmp_path / "orig", "renamed.exe", original)
    fixed_root = _private_root(tmp_path / "fixed", "renamed.exe", fixed)
    for root in (original_root, fixed_root):
        with pytest.raises(ValueError, match="unsupported"):
            runtime_driver.validate_runtime_executable(root, "renamed.exe")


def test_same_fixed_filename_with_original_bytes_is_rejected(tmp_path: Path) -> None:
    root = _private_root(tmp_path, "supply5000.exe", ORIGINAL.read_bytes())
    with pytest.raises(ValueError, match="SHA256"):
        runtime_driver.validate_runtime_executable(root, "supply5000.exe")


def test_stock_supply5000_bytes_are_allowlisted_under_original_filename_for_control(
    tmp_path: Path,
) -> None:
    root = _private_root(
        tmp_path, "syw2plus_original.exe",
        fixed_supply_5000.patched_bytes(ORIGINAL.read_bytes()),
    )
    accepted = runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")
    assert accepted["profile"] == "fixed_supply_5000_original_filename"


def test_official_g2_supply5000_filename_is_allowlisted_for_stock_control(
    tmp_path: Path,
) -> None:
    root = _private_root(
        tmp_path, "g2_supply_5000.exe",
        fixed_supply_5000.patched_bytes(ORIGINAL.read_bytes()),
    )
    accepted = runtime_driver.validate_runtime_executable(root, "g2_supply_5000.exe")
    assert accepted["profile"] == "fixed_supply_5000"


def test_actual_offline_storage_candidate_is_rejected_before_legacy_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from patches.population import offline_storage_v1

    candidate = offline_storage_v1.build_candidate(ORIGINAL.read_bytes())
    root = _private_root(tmp_path, "supply5000.exe", candidate)
    with pytest.raises(ValueError, match="SHA256"):
        runtime_driver.validate_runtime_executable(root, "supply5000.exe")
    original_named_root = _private_root(tmp_path / "original_named", "syw2plus_original.exe", candidate)
    with pytest.raises(ValueError, match="SHA256"):
        runtime_driver.validate_runtime_executable(original_named_root, "syw2plus_original.exe")

    calls: list[object] = []
    monkeypatch.setattr(runtime_driver.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    monkeypatch.setattr(sys, "argv", [
        "runtime_driver.py", "--game-root", str(root), "--prefix", str(tmp_path / "prefix"),
        "--out", str(tmp_path / "out"), "--display", ":98", "--exe", "supply5000.exe",
    ])
    with pytest.raises(ValueError, match="SHA256"):
        runtime_driver.main()
    assert calls == []
    assert not (tmp_path / "out").exists()


def test_canonical_check_runtime_rejects_actual_candidate_named_original(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from tools import runtime_env
    from patches.population import offline_storage_v1

    run = tmp_path / "run"
    game = run / "game"
    game.mkdir(parents=True)
    (game / "syw2plus_original.exe").write_bytes(
        offline_storage_v1.build_candidate(ORIGINAL.read_bytes())
    )
    prefix = run / "prefix"
    output = run / "output"
    data = {"game": {"exe_sha256": runtime_env.ORIGINAL_SHA256}}
    manifest = run / "manifest.json"
    manifest.write_text("{}", encoding="utf-8")
    monkeypatch.setattr(runtime_env, "_manifest", lambda _path: (data, game, prefix, output))
    calls: list[object] = []
    monkeypatch.setattr(runtime_env.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    monkeypatch.setattr(runtime_env.subprocess, "run", lambda *args, **kwargs: calls.append(args))
    with pytest.raises(runtime_env.RuntimeSafetyError, match="verified original"):
        runtime_env.check_runtime(manifest)
    assert calls == []


@pytest.mark.parametrize("name", ["renamed.exe", "syw2plus_original.exe", "supply5000.exe"])
def test_wrong_or_renamed_candidate_is_rejected_before_launch(tmp_path: Path, name: str) -> None:
    root = _private_root(tmp_path / name.replace(".", "_"), name, b"original-but-not-approved")
    with pytest.raises(ValueError, match="SHA256|unsupported"):
        runtime_driver.validate_runtime_executable(root, name)


def test_main_rejects_candidate_before_xvfb_or_wine(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = _private_root(tmp_path, "supply5000.exe", b"stripped-or-new-unapproved-candidate")
    calls: list[object] = []
    monkeypatch.setattr(runtime_driver.subprocess, "Popen", lambda *args, **kwargs: calls.append(args))
    monkeypatch.setattr(sys, "argv", [
        "runtime_driver.py", "--game-root", str(root), "--prefix", str(tmp_path / "prefix"),
        "--out", str(tmp_path / "out"), "--display", ":99", "--exe", "supply5000.exe",
    ])
    with pytest.raises(ValueError, match="SHA256"):
        runtime_driver.main()
    assert calls == []
    assert not (tmp_path / "out").exists()


def test_symlink_candidate_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "source.exe"
    source.write_bytes(ORIGINAL.read_bytes())
    root = tmp_path / "private"
    root.mkdir()
    (root / "syw2plus_original.exe").symlink_to(source)
    with pytest.raises(ValueError, match="missing or linked"):
        runtime_driver.validate_runtime_executable(root, "syw2plus_original.exe")


def test_runtime_driver_enables_private_probe_for_stock_supply5000_control() -> None:
    source = Path(runtime_driver.__file__).read_text(encoding="utf-8")
    activation = source.split('if executable["profile"] in {', 1)[1].split("}:", 1)[0]
    assert '"original"' in activation
    assert '"fixed_supply_5000"' in activation
    assert '"fixed_supply_5000_original_filename"' in activation
