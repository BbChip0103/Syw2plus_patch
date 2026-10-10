"""H-DEF1: G1 default-on build flag lives in the repo and keeps SFX probing opt-in."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools/inmm_stub"
SRC = (STUB / "inmm_stub.c").read_text(encoding="utf-8")
MAKEFILE = (STUB / "Makefile").read_text(encoding="utf-8")


def _attach_block() -> str:
    start = SRC.index("if (reason == DLL_PROCESS_ATTACH) {")
    return SRC[start : SRC.index("DisableThreadLibraryCalls(hInst);", start)]


def test_default_on_block_sets_four_env_only_when_unset() -> None:
    block = _attach_block()
    assert "#ifdef SYW2_G1_DEFAULT_ON" in block
    assert "#endif" in block
    names = re.findall(r'"((?:SYW2_G1_[A-Z0-9_]+)|INMM_STUB_NO_UNIT_TICKS)"', block)
    assert names == ["SYW2_G1_NATIVE_2X_BLIT", "SYW2_G1_MIRROR2X", "SYW2_G1_HD_SOURCE", "INMM_STUB_NO_UNIT_TICKS"]
    assert '{"1", "1", "scale2x", "1"}' in block
    # An explicit caller value, even an empty-but-defined one, must survive.
    assert "GetEnvironmentVariableA(names[i], probe, sizeof(probe)) == 0" in block
    assert "GetLastError() == ERROR_ENVVAR_NOT_FOUND" in block
    assert "SetEnvironmentVariableA(names[i], values[i])" in block


def test_default_on_block_precedes_every_install() -> None:
    attach = SRC.index("if (reason == DLL_PROCESS_ATTACH) {")
    block = SRC.index("#ifdef SYW2_G1_DEFAULT_ON", attach)
    assert block < SRC.index("DisableThreadLibraryCalls(hInst);", attach)
    assert block < SRC.index("asset_hook_install();", attach)
    assert block < SRC.index("sfx_hook_install();", attach)


def test_sfx_probe_is_opt_in_only_in_default_on_build() -> None:
    call = SRC.index("sfx_probe_live_units();")
    guard = SRC.rindex("#ifdef SYW2_G1_DEFAULT_ON", 0, call)
    window = SRC[guard : call + 120]
    assert "if (sfx_probe_opted_in())" in window[: window.index("sfx_probe_live_units();")]
    # The `if` is the only conditionally compiled line; the call itself stays plain.
    assert window.index("sfx_probe_opted_in())") < window.index("#endif") < window.index("sfx_probe_live_units();")
    # Flag-less build: the guard preprocesses away, the call stays unconditional.
    assert SRC.count("sfx_probe_live_units();") == 1


def test_opt_in_helper_reads_env_value() -> None:
    helper = SRC[SRC.index("static BOOL sfx_probe_opted_in(void)") :]
    helper = helper[: helper.index("\n}\n") + 3]
    assert 'GetEnvironmentVariableA("INMM_STUB_SFX_PROBE"' in helper
    assert "'0'" in helper                      # "0" means off
    assert helper.count("#ifdef SYW2_G1_DEFAULT_ON") == 0   # wrapped by the caller-side guard


def test_makefile_default_on_target_builds_separate_artifact() -> None:
    assert re.search(r"^default-on:", MAKEFILE, flags=re.M)
    assert "-DSYW2_G1_DEFAULT_ON" in MAKEFILE
    assert "_inmm.dll" in MAKEFILE and "_G1MM.dll" in MAKEFILE
    # The plain target must not carry the flag.
    plain = MAKEFILE[: MAKEFILE.index("default-on:")]
    assert "-DSYW2_G1_DEFAULT_ON" not in plain.replace("# ", "#")


@pytest.mark.skipif(shutil.which("i686-w64-mingw32-gcc") is None, reason="mingw32 not installed")
def test_default_on_object_compiles_and_gates_probe(tmp_path: Path) -> None:
    blobs = {}
    for label, extra in (("plain", []), ("on", ["-DSYW2_G1_DEFAULT_ON"])):
        obj = tmp_path / f"{label}.o"
        subprocess.run(
            ["i686-w64-mingw32-gcc", "-m32", "-Wall", "-Wextra", "-O2", "-fno-stack-protector", "-mno-stack-arg-probe",
             *extra, "-c", str(STUB / "inmm_stub.c"), "-o", str(obj), f"-I{STUB}"],
            check=True, capture_output=True, text=True,
        )
        blobs[label] = obj.read_bytes()
    assert b"INMM_STUB_SFX_PROBE" not in blobs["plain"]
    assert b"SYW2_G1_HD_SOURCE" not in blobs["plain"]
    assert b"INMM_STUB_SFX_PROBE" in blobs["on"]
    assert b"SYW2_G1_HD_SOURCE" in blobs["on"]
