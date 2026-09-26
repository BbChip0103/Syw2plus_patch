"""Migration boundaries: local diagnostic dependencies and protected originals."""

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_runtime_rejects_both_original_roots():
    spec = importlib.util.spec_from_file_location(
        "runtime_driver", ROOT / "patches/population/runtime_driver.py"
    )
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    for path in [ROOT / "Syw2plus", ROOT.parent / "Syw2plus_re/Syw2plus", ROOT.parent / "Syw2plus"]:
        with pytest.raises(ValueError, match="original"):
            driver.validate_game_root(path)


def test_runtime_accepts_private_copy(tmp_path):
    from patches.population.runtime_driver import build_runtime_env, SCREENSHOTS, validate_game_root

    assert validate_game_root(tmp_path) == tmp_path.resolve()
    env = build_runtime_env(tmp_path / "prefix", ":321")
    assert env["DISPLAY"] == ":321"
    assert env["WINEPREFIX"] == str(tmp_path / "prefix")
    assert env["WINEARCH"] == "win32"
    assert env["LC_ALL"] == "ko_KR.UTF-8"
    assert env["WINEDLLOVERRIDES"] == "ddraw=b"
    assert SCREENSHOTS == Path(
        "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures"
    )


def test_runtime_rejects_original_symlink(tmp_path):
    from patches.population.runtime_driver import validate_game_root

    link = tmp_path / "alias"
    link.symlink_to(ROOT / "Syw2plus", target_is_directory=True)
    with pytest.raises(ValueError, match="original"):
        validate_game_root(link)


def test_diagnostic_support_is_local_and_build_only():
    builder = (ROOT / "patches/population/build_runtime_bridge.py").read_text()
    driver = (ROOT / "patches/population/runtime_driver.py").read_text()
    assert 'root / "tools/inmm_stub"' in builder
    assert "plan_c/tools/" not in builder + driver
    makefile = (ROOT / "tools/inmm_stub/Makefile").read_text()
    assert "deploy:" not in makefile and "restore:" not in makefile
    assert "GAME_DIR" not in makefile
    for name in ["x11_mouse_click.py", "x11_send_keys.py"]:
        assert (ROOT / "tools" / name).is_file()


@pytest.mark.parametrize(
    "name,allowed",
    [
        ("patches/source.py", True),
        ("local/private.txt", False),
        ("oops.DLL", False),
        ("save011.dat", False),
        (".env.secret", False),
    ],
)
def test_commit_hook_blocks_binary_and_private_inputs(tmp_path, name, allowed):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    file = tmp_path / name
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text("test fixture\n")
    subprocess.run(["git", "add", "-f", "--", name], cwd=tmp_path, check=True)
    result = subprocess.run(
        [sys.executable, str(ROOT / ".githooks/pre-commit")], cwd=tmp_path, capture_output=True
    )
    assert (result.returncode == 0) is allowed


def test_import_provenance_distinguishes_uncommitted_experiments():
    manifest = json.loads((ROOT / "docs/history/import_manifest.json").read_text())
    assert manifest["source_head"] == "edd86cafdb83e29d6929bd9d3aba272e795f3f81"
    assert "working tree" in manifest["snapshot_kind"]
    entries = {entry["destination"]: entry for entry in manifest["files"]}
    assert not entries["patches/population/fixed_supply_5000.py"]["source_git_tracked"]
    for name in ["patches/population/fixed_supply_5000.py", "patches/resolution/qhd_probe.py"]:
        assert entries[name]["source_sha256"] == entries[name]["imported_sha256"]


def test_historical_launcher_cannot_start_old_session():
    result = subprocess.run(
        [sys.executable, str(ROOT / "patches/resolution/run_qhd_probe.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=5,
    )
    assert result.returncode != 0
    assert "Historical QHD launcher disabled" in result.stderr
