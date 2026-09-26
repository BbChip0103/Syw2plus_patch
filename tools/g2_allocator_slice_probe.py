"""SHA-pinned driver for the isolated FUN_00442FA0 Win32 fixture.

The C fixture executes bytes copied from the original image; this module does
not reimplement the allocator and never writes an executable.  Wine execution
is opt-in because it is an isolated feasibility probe, not a game run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
ALLOCATOR_FILE_OFFSET = 0x42FA0
ALLOCATOR_VA = 0x00442FA0
ALLOCATOR_BYTES = bytes.fromhex(
    "53 56 57 33 db 33 c0 bf 01 00 00 00 "
    "b9 2a 9a 89 00 66 83 b9 a0 f6 ff ff 00 "
    "75 12 66 8b 31 0f bf d6 3b d3 7c 04 "
    "8b da 8b c7 46 66 89 31 83 c1 02 47 "
    "81 f9 88 a3 89 00 7c d8 5f 5e 5b c3"
)
CAPACITIES = (1200, 1201, 4001)
RESULT_POLICY = {
    "activation": "NO-GO",
    "scope": "transplanted original allocator selector only; no spawn/save/LAN/ID proof",
    "execution": "dynamic transplanted original machine code in standalone Win32 process; never the game",
    "bulk_sentinel": "standalone only; not original-game bulk safety proof",
}
OWNER_MARKER = ".g2_allocator_slice_owner"


def verify_original(path: Path) -> dict[str, object]:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != ORIGINAL_SHA256:
        raise ValueError(f"original SHA mismatch: {digest}")
    actual = data[ALLOCATOR_FILE_OFFSET : ALLOCATOR_FILE_OFFSET + len(ALLOCATOR_BYTES)]
    if actual != ALLOCATOR_BYTES:
        raise ValueError("FUN_00442FA0 bytes mismatch")
    return {
        "path": str(path),
        "sha256": digest,
        "allocator_va": f"0x{ALLOCATOR_VA:08x}",
        "allocator_file_offset": f"0x{ALLOCATOR_FILE_OFFSET:x}",
        "allocator_bytes": actual.hex(" "),
    }


def compile_fixture(output: Path, compiler: str | None = None) -> Path:
    compiler = compiler or shutil.which("i686-w64-mingw32-gcc")
    if not compiler:
        raise RuntimeError("i686-w64-mingw32-gcc is unavailable")
    source = Path(__file__).with_name("g2_allocator_slice_fixture.c")
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            compiler,
            "-std=c99",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Wl,--image-base,0x10000000",
            str(source),
            "-o",
            str(output),
        ],
        check=True,
    )
    return output


def run_fixture(original: Path, executable: Path, *, allow_execution: bool) -> dict[str, object]:
    source = verify_original(original)
    if not allow_execution:
        raise RuntimeError("execution requires explicit --allow-execution")
    if os.environ.get("G2_ALLOCATOR_SLICE_ALLOW_WINE") != "1":
        raise RuntimeError("Wine execution requires G2_ALLOCATOR_SLICE_ALLOW_WINE=1")
    prefix_value = os.environ.get("WINEPREFIX", "")
    prefix = Path(prefix_value)
    if not prefix_value or not prefix.is_absolute():
        raise RuntimeError("Wine execution requires an explicit absolute WINEPREFIX")
    marker = prefix / OWNER_MARKER
    if not marker.is_file() or marker.read_text(encoding="utf-8").strip() != "g2_allocator_slice":
        raise RuntimeError("WINEPREFIX is not an owned fresh allocator-slice prefix")
    if not os.environ.get("DISPLAY"):
        raise RuntimeError("Wine execution requires an explicit private DISPLAY")
    fixture_sha = hashlib.sha256(executable.read_bytes()).hexdigest()
    if os.environ.get("G2_ALLOCATOR_SLICE_FIXTURE_SHA256") != fixture_sha:
        raise RuntimeError("fixture SHA pin is missing or mismatched")
    wine = shutil.which("wine")
    if not wine:
        raise RuntimeError("wine is unavailable")
    result = subprocess.run(
        [wine, str(executable), str(original)],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"fixture failed rc={result.returncode}: {result.stderr.strip()}")
    try:
        report = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as exc:
        raise RuntimeError(f"fixture did not emit JSON: {result.stdout!r}") from exc
    if report.get("status") != "PASS" or report.get("bulk_sentinel") != (
        "standalone_only_not_game_bulk_proof"
    ):
        raise RuntimeError(f"fixture returned non-pass report: {report}")
    expected_cases = [
        "empty", "single_free", "multiple_equal_tie", "signed_wrap",
        "all_negative_no_eligible", "common1200", "common1201", "common4001",
        "boundary1201", "exhaustion1201", "boundary4001", "exhaustion4001",
    ]
    if report.get("cases") != 12 or report.get("case_names") != expected_cases:
        raise RuntimeError(f"fixture case coverage is incomplete: {report}")
    if report.get("capacities") != [1200, 1201, 4001]:
        raise RuntimeError(f"fixture capacity coverage is incomplete: {report}")
    if report.get("full_state_model") is not True or report.get("caller_occupancy_only") is not True:
        raise RuntimeError(f"fixture state policy is incomplete: {report}")
    if report.get("execution") != "transplanted_original_machine_code":
        raise RuntimeError(f"fixture execution policy is incomplete: {report}")
    if report.get("activation") != "NO-GO":
        raise RuntimeError(f"fixture activation policy is unsafe: {report}")
    return {"source": source, "fixture": report, "policy": RESULT_POLICY}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--compile", dest="compile_to", type=Path)
    parser.add_argument("--run", dest="executable", type=Path)
    parser.add_argument("--allow-execution", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = verify_original(args.source)
    result: dict[str, object] = {"source": source, "policy": RESULT_POLICY}
    if args.compile_to:
        result["executable"] = str(compile_fixture(args.compile_to))
    if args.executable:
        result = run_fixture(args.source, args.executable, allow_execution=args.allow_execution)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
