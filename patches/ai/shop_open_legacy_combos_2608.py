#!/usr/bin/env python3
"""Build the two 2608 shop-opening/legacy AI combinations.

The two combinations are deliberately kept as a small, byte-addressed layer
on top of :mod:`shop_open_research_2608`:

* ``seven-generals``: the 2606 ``장수7명_전비1600-200-3000`` changes;
* ``seven-generals-fixed-start``: the first combination plus its two
  ``시작자리고정`` changes.

Only a pinned 2608 source is accepted.  The 2606 executable is a read-only
reference: its SHA, every old byte, and a 256-byte context window around each
site are pinned below.  Building returns bytes and never mutates its input or
launches Wine.  File output uses exclusive creation and an explicit inverse
restores a combo candidate to the pinned original 2608 bytes exactly.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


def _load_shop_module() -> Any:
    """Load the neighbouring shop patch without package-import assumptions."""

    path = Path(__file__).with_name("shop_open_research_2608.py")
    spec = importlib.util.spec_from_file_location("shop_open_research_2608", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load shop patch: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


SHOP = _load_shop_module()

SOURCE_SHA256 = SHOP.ORIGINAL_SHA256
SOURCE_FILE_SIZE = SHOP.ORIGINAL_FILE_SIZE
# Conventional aliases make the two input pins obvious to callers.
ORIGINAL_SHA256 = SOURCE_SHA256
SHOP_CANDIDATE_SHA256 = "0f3334668f5ed37d130726725f421515f031be2856efdde04a9c19ea572627f5"
LEGACY_2606_SHA256 = "716dde6a1cd837c74c83c426fba634491143d624c0c284aad4dc4d5d5ea2417f"
LEGACY_SHA256 = LEGACY_2606_SHA256
LEGACY_2606_FILE_SIZE = 0xFC000
LEGACY_VARIANT_SHA256 = {
    "seven-generals": "4a03895d8e6690080714fab7e851c3a0e9d44b7cac47fed78fc21a2f5210c6f8",
    "seven-generals-fixed-start": "daf0b6a07f01d04397018924f9dd0c6ff414148c0547adc2d5c9e0b403a58523",
}
CONTEXT_RADIUS = 0x100


@dataclass(frozen=True)
class DiffChunk:
    """One contiguous byte change in a legacy 2606 variant."""

    offset: int
    old: bytes
    new: bytes

    @property
    def end(self) -> int:
        return self.offset + len(self.old)


def _chunk(offset: int, old_hex: str, new_hex: str) -> DiffChunk:
    old, new = bytes.fromhex(old_hex), bytes.fromhex(new_hex)
    if not old or len(old) != len(new):
        raise ValueError("legacy combo chunks must be non-empty and same-sized")
    return DiffChunk(offset, old, new)


# These are the complete byte diffs against the pinned 2606 base.  Keep this
# inventory explicit: silently discovering and applying an extra diff would
# make a new upstream variant look like a supported one.
SEVEN_GENERALS_CHUNKS: tuple[DiffChunk, ...] = (
    _chunk(0x0D8DA, "05", "07"),
    _chunk(0x121AF, "05", "07"),
    _chunk(0x124D9, "05", "07"),
    _chunk(0x3E8FD, "05", "07"),
    _chunk(0x3FFD5, "DC05", "4006"),
    _chunk(0x9A5CA, "05", "07"),
)
FIXED_START_CHUNKS: tuple[DiffChunk, ...] = (
    *SEVEN_GENERALS_CHUNKS,
    _chunk(0x1F2B0, "8B", "8A"),
    _chunk(0x2FBB1, "0FBFD2", "8BD390"),
)

VARIANT_CHUNKS: dict[str, tuple[DiffChunk, ...]] = {
    "seven-generals": SEVEN_GENERALS_CHUNKS,
    "seven-generals-fixed-start": FIXED_START_CHUNKS,
}
VARIANT_LABELS = {
    "seven-generals": "장수7명_전비1600-200-3000",
    "seven-generals-fixed-start": "장수7명_전비1600-200-3000_시작자리고정",
}


def _all_chunks() -> tuple[DiffChunk, ...]:
    """Return the unique union of the two inventories."""

    result: dict[tuple[int, bytes, bytes], DiffChunk] = {}
    for chunks in VARIANT_CHUNKS.values():
        for chunk in chunks:
            result[(chunk.offset, chunk.old, chunk.new)] = chunk
    return tuple(result.values())


def _context_digest(data: bytes, chunk: DiffChunk) -> str:
    start = max(0, chunk.offset - CONTEXT_RADIUS)
    end = min(len(data), chunk.end + CONTEXT_RADIUS)
    return hashlib.sha256(data[start:end]).hexdigest()


def _assert_inventory(chunks: Iterable[DiffChunk]) -> None:
    """Reject overlapping/duplicate inventory entries before touching bytes."""

    ordered = sorted(chunks, key=lambda item: item.offset)
    for previous, current in zip(ordered, ordered[1:]):
        if previous.end > current.offset:
            raise ValueError(
                f"legacy diff inventory overlaps at {previous.offset:#x} and {current.offset:#x}"
            )


for _variant_chunks in VARIANT_CHUNKS.values():
    _assert_inventory(_variant_chunks)

# The 2608 sites and their +/-256-byte windows were independently compared to
# the 2606 base.  The digest is pinned rather than relying on a reference file
# being present at build time (the original executable remains read-only).
_CONTEXT_SHA256: dict[int, str] = {
    0x0D8DA: "07e4d1b9b91ac97e992a735ebddccd74b884823922fa7a203bdaac47bda0785a",
    0x121AF: "1c19ec3d22943038a6070833b2afc8ad744ca73663c53145aadaf88630528acf",
    0x124D9: "91f7affd322b4b5388d08058e27581d3dad3b72cca9cf73d374d9c76ad94ad1d",
    0x3E8FD: "ec4e3c66545c1040639d94300c44b896f230edf0a24942449cad4191e75d8a36",
    0x3FFD5: "e148c6c5b9f2ccf2be019e8465694ba195989faf3ad1b88cbbf599a6ab9cb37c",
    0x9A5CA: "ea7bef757c70b6571fa50c33e11d8a151c558edcdb8cd0220d0f067297a0cdb3",
    0x1F2B0: "6a05b3a5157afd23e84b3b87edfad9485a9e631ade4d5f0bf5ddcd00ac707fbc",
    0x2FBB1: "a3b1e3feb9b8451be8eb9d601e9dc7d1181b82b9ad2d36e02bcb05a2fb7d5b21",
}


class BuildAbortedError(RuntimeError):
    """Raised when a source or candidate is not a pinned supported layout."""


def verify_legacy_2606(data: bytes) -> None:
    """Verify an optional 2606 reference without ever modifying it."""

    if len(data) != LEGACY_2606_FILE_SIZE:
        raise ValueError(f"2606 reference size mismatch: {len(data):#x}")
    digest = hashlib.sha256(data).hexdigest()
    if digest != LEGACY_2606_SHA256:
        raise ValueError(f"2606 reference SHA256 mismatch: {digest}")
    for chunk in _all_chunks():
        if data[chunk.offset : chunk.end] != chunk.old:
            raise ValueError(f"2606 old bytes mismatch at {chunk.offset:#x}")
        if _context_digest(data, chunk) != _CONTEXT_SHA256[chunk.offset]:
            raise ValueError(f"2606 context mismatch at {chunk.offset:#x}")


def verify_legacy_variant(data: bytes, variant: str) -> None:
    """Verify a supplied 2606 output against its pinned full-file SHA."""

    expected_sha = LEGACY_VARIANT_SHA256.get(variant)
    if expected_sha is None:
        raise ValueError(f"unsupported combo variant: {variant}")
    if len(data) != LEGACY_2606_FILE_SIZE:
        raise ValueError(f"2606 variant size mismatch: {len(data):#x}")
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_sha:
        raise ValueError(f"2606 variant SHA256 mismatch: {digest}")
    for chunk in VARIANT_CHUNKS[variant]:
        if data[chunk.offset : chunk.end] != chunk.new:
            raise ValueError(f"2606 variant new bytes mismatch at {chunk.offset:#x}")


def _check_source_context(data: bytes, chunks: Iterable[DiffChunk]) -> None:
    for chunk in chunks:
        if data[chunk.offset : chunk.end] != chunk.old:
            raise BuildAbortedError(f"2608 old bytes mismatch at {chunk.offset:#x}")
        expected = _CONTEXT_SHA256.get(chunk.offset)
        if not expected:
            raise BuildAbortedError(f"missing pinned 2608 context at {chunk.offset:#x}")
        actual = _context_digest(data, chunk)
        if actual != expected:
            raise BuildAbortedError(
                f"2608 +/-{CONTEXT_RADIUS:#x} context mismatch at {chunk.offset:#x}: {actual}"
            )


def _diff_ranges(before: bytes, after: bytes) -> list[tuple[int, int]]:
    if len(before) > len(after):
        raise ValueError("candidate is shorter than source")
    ranges: list[tuple[int, int]] = []
    index = 0
    while index < len(before):
        if before[index] == after[index]:
            index += 1
            continue
        start = index
        while index < len(before) and before[index] != after[index]:
            index += 1
        ranges.append((start, index))
    if len(after) > len(before):
        ranges.append((len(before), len(after)))
    return ranges


def _assert_nonoverlap_with_shop_changes(source: bytes, shop_candidate: bytes, chunks: Iterable[DiffChunk]) -> None:
    shop_ranges = _diff_ranges(source, shop_candidate)
    for chunk in chunks:
        for start, end in shop_ranges:
            if chunk.offset < end and start < chunk.end:
                raise BuildAbortedError(
                    f"legacy combo site overlaps shop patch at {chunk.offset:#x}"
                )


def _apply_chunks(base: bytes, chunks: tuple[DiffChunk, ...]) -> bytes:
    out = bytearray(base)
    for chunk in chunks:
        if out[chunk.offset : chunk.end] != chunk.old:
            raise BuildAbortedError(f"combo old bytes mismatch at {chunk.offset:#x}")
        out[chunk.offset : chunk.end] = chunk.new
    return bytes(out)


def _assert_exact_combo_diff(base: bytes, candidate: bytes, chunks: tuple[DiffChunk, ...]) -> None:
    expected = sorted((chunk.offset, chunk.end) for chunk in chunks)
    actual = _diff_ranges(base, candidate)
    if actual != expected:
        raise BuildAbortedError(f"combo diff inventory changed: expected={expected!r} actual={actual!r}")


def build_variant(original: bytes, variant: str) -> tuple[bytes, dict[str, Any]]:
    """Build one named combo on top of the pinned 2608 shop candidate."""

    if variant not in VARIANT_CHUNKS:
        raise ValueError(f"unsupported combo variant: {variant}")
    SHOP.verify_original(original)
    chunks = VARIANT_CHUNKS[variant]
    _check_source_context(original, chunks)
    shop_candidate, shop_report = SHOP.build_candidate(original)
    if shop_report.get("candidate_sha256") != SHOP_CANDIDATE_SHA256:
        raise BuildAbortedError("shop candidate SHA256 is not the pinned 2608 candidate")
    _assert_nonoverlap_with_shop_changes(original, shop_candidate, chunks)
    candidate = _apply_chunks(shop_candidate, chunks)
    _assert_exact_combo_diff(shop_candidate, candidate, chunks)
    report: dict[str, Any] = {
        "version": "esl2608-ai-shop-open-legacy-combo-v1",
        "variant": variant,
        "label": VARIANT_LABELS[variant],
        "source_sha256": SOURCE_SHA256,
        "legacy_2606_sha256": LEGACY_2606_SHA256,
        "shop_candidate_sha256": shop_report["candidate_sha256"],
        "candidate_sha256": hashlib.sha256(candidate).hexdigest(),
        "candidate_size": len(candidate),
        "diff_chunks": [
            {
                "offset": f"0x{chunk.offset:06x}",
                "old": chunk.old.hex(),
                "new": chunk.new.hex(),
                "context_radius": CONTEXT_RADIUS,
                "context_sha256": _CONTEXT_SHA256[chunk.offset],
            }
            for chunk in chunks
        ],
        "shop_changes_nonoverlapping": True,
        "runtime_status": "static-only; game/Wine not launched",
    }
    return candidate, report


def build_candidates(original: bytes) -> dict[str, tuple[bytes, dict[str, Any]]]:
    """Build both outputs from one immutable pinned 2608 source."""

    return {variant: build_variant(original, variant) for variant in VARIANT_CHUNKS}


def restore_variant(candidate: bytes, variant: str) -> bytes:
    """Restore a combo candidate exactly to the pinned original 2608 bytes."""

    if variant not in VARIANT_CHUNKS:
        raise ValueError(f"unsupported combo variant: {variant}")
    chunks = VARIANT_CHUNKS[variant]
    if len(candidate) < SOURCE_FILE_SIZE:
        raise ValueError("candidate is shorter than the pinned 2608 source")
    shop_candidate = bytearray(candidate)
    for chunk in chunks:
        if shop_candidate[chunk.offset : chunk.end] != chunk.new:
            raise ValueError(f"candidate combo bytes mismatch at {chunk.offset:#x}")
        shop_candidate[chunk.offset : chunk.end] = chunk.old
    restored_shop = bytes(shop_candidate)
    if hashlib.sha256(restored_shop).hexdigest() != SHOP_CANDIDATE_SHA256:
        raise ValueError("restored bytes are not the canonical shop-only candidate")
    # The shop patch has its own strict inverse, including the original SHA
    # assertion.  Chaining it makes this combo inverse explicit and exact.
    return SHOP.restore_candidate(restored_shop)


def restore_candidate(candidate: bytes, variant: str) -> bytes:
    """Explicit inverse returning the original pinned 2608 bytes."""

    return restore_variant(candidate, variant)


def write_candidates(original_path: Path, destinations: dict[str, Path]) -> dict[str, dict[str, Any]]:
    """Create both combo files and reports with exclusive creation."""

    original_path = original_path.resolve()
    original = original_path.read_bytes()
    built = build_candidates(original)
    if set(destinations) != set(VARIANT_CHUNKS):
        raise ValueError(f"destinations must name exactly {tuple(VARIANT_CHUNKS)}")
    for variant, destination in destinations.items():
        destination = destination.resolve()
        if destination == original_path:
            raise ValueError("refusing to overwrite the 2608 source")
        report_path = destination.with_suffix(destination.suffix + ".json")
        if destination.exists() or report_path.exists():
            raise FileExistsError(f"refusing to overwrite existing output: {destination}")
    resolved_destinations = [path.resolve() for path in destinations.values()]
    resolved_reports = [path.with_suffix(path.suffix + ".json") for path in resolved_destinations]
    if len(set(resolved_destinations + resolved_reports)) != len(resolved_destinations) + len(resolved_reports):
        raise ValueError("combo output paths and report paths must be distinct")
    reports: dict[str, dict[str, Any]] = {}
    for variant, destination in destinations.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        candidate, report = built[variant]
        with destination.open("xb") as handle:
            handle.write(candidate)
        with destination.with_suffix(destination.suffix + ".json").open("x", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        reports[variant] = report
    return reports


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("seven_generals_destination", type=Path)
    parser.add_argument("fixed_start_destination", type=Path)
    args = parser.parse_args()
    reports = write_candidates(
        args.original,
        {
            "seven-generals": args.seven_generals_destination,
            "seven-generals-fixed-start": args.fixed_start_destination,
        },
    )
    print(json.dumps(reports, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
