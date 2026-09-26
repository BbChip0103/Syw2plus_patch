#!/usr/bin/env python3
"""Independently recompute lap581 W49 raw and capture evidence.

The work-tier run summary is intentionally not an input.  This probe reads only
the append-only sample stream, capture manifest, capture PNGs, and T0 positions.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image


ARTIFACT = Path(
    "/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/"
    "g2_capacity/20260925_lap581_w49_screen_evidence"
)
EXPECTED_TAGS = ["preseed", "t0", "plus2000", "plus10000", "minimap"]
EXPECTED_SAMPLE_SHA256 = (
    "4466c7c2d26b3ee8dd81c1814270fa9c0f6af0ef1eacdf6000962e2a6ce987cf"
)
EXPECTED_MANIFEST_SHA256 = (
    "87be1fdaaa723f638051edf8fb5bf127447a711309870f36a548991452a3e687"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    sample_path = ARTIFACT / "samples.jsonl"
    manifest_path = ARTIFACT / "capture_manifest.json"
    records = [
        json.loads(line)
        for line in sample_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    t0_positions = json.loads(
        (ARTIFACT / "t0_positions.json").read_text(encoding="utf-8")
    )
    seed_receipts = json.loads(
        (ARTIFACT / "seed_receipts.json").read_text(encoding="utf-8")
    )

    capture_results: list[dict[str, object]] = []
    for capture in manifest:
        path = Path(capture["path"])
        with Image.open(path) as opened:
            image = opened.convert("RGB")
        nonblack = [
            (x, y)
            for y in range(image.height)
            for x in range(image.width)
            if image.getpixel((x, y)) != (0, 0, 0)
        ]
        bbox = None
        if nonblack:
            bbox = [
                min(x for x, _ in nonblack),
                min(y for _, y in nonblack),
                max(x for x, _ in nonblack),
                max(y for _, y in nonblack),
            ]
        exact_raw = next(
            (record for record in records if record["tick"] == capture["tick"]),
            None,
        )
        capture_results.append(
            {
                "tag": capture["tag"],
                "tick": capture["tick"],
                "size": list(image.size),
                "sha256": sha256(path),
                "sha_matches_manifest": sha256(path) == capture["sha256"],
                "nonblack_bbox": bbox,
                "nonblack_outside_800x600": sum(
                    x >= 800 or y >= 600 for x, y in nonblack
                ),
                "exact_sample_present": exact_raw is not None,
                "sample_used_matches": bool(
                    exact_raw
                    and [owner["used"] for owner in exact_raw["owners"]]
                    == capture["owners_used"]
                ),
                "sample_count_matches": bool(
                    exact_raw
                    and [owner["count"] for owner in exact_raw["owners"]]
                    == capture["owners_count"]
                ),
            }
        )

    all_used = [owner["used"] for record in records for owner in record["owners"]]
    plus10000 = next(item for item in manifest if item["tag"] == "plus10000")
    minimap = next(item for item in manifest if item["tag"] == "minimap")
    result = {
        "inputs": {
            "sample_sha256": sha256(sample_path),
            "sample_sha_matches_expected": sha256(sample_path)
            == EXPECTED_SAMPLE_SHA256,
            "manifest_sha256": sha256(manifest_path),
            "manifest_sha_matches_expected": sha256(manifest_path)
            == EXPECTED_MANIFEST_SHA256,
        },
        "raw": {
            "records": len(records),
            "sample_index": [records[0]["sample"], records[-1]["sample"]],
            "tick": [records[0]["tick"], records[-1]["tick"]],
            "tick_regressions": sum(
                later["tick"] < earlier["tick"]
                for earlier, later in zip(records, records[1:])
            ),
            "live_count_mismatches": sum(
                record["live"] != record["sum_count"] for record in records
            ),
            "used_minmax": [min(all_used), max(all_used)],
            "over_cap": sum(value > 5000 for value in all_used),
            "negative_used": sum(value < 0 for value in all_used),
            "owner_shape_failures": sum(
                [owner["owner"] for owner in record["owners"]] != list(range(8))
                for record in records
            ),
            "active_ai_or_cap_failures": sum(
                any(
                    owner["ai"] != 1
                    or owner["nation"] == 0
                    or owner["cap"] != 5000
                    for owner in record["owners"]
                )
                for record in records
            ),
            "ledger_failures": sum(
                any(
                    ledger["used32"] != owner["used"]
                    or ledger["used_hi"] != 0
                    or ledger["bldg"] < 0
                    for owner, ledger in zip(record["owners"], record["ledger_raw"])
                )
                for record in records
            ),
            "vm_size_kb_unique": sorted(
                {record["vm_size_kb"] for record in records}
            ),
            "rss_kb_first_last_max": [
                records[0]["rss_kb"],
                records[-1]["rss_kb"],
                max(record["rss_kb"] for record in records),
            ],
            "t0_position_count": len(t0_positions),
            "preseed_receipts_confirm_20_used_2_count_8of8": all(
                any(
                    item["owner"] == owner
                    and item["op"] == 7
                    and item["receipt"]["before"]["used"] == 20
                    and item["receipt"]["before"]["count"] == 2
                    for item in seed_receipts
                )
                for owner in range(8)
            ),
            "t0_receipts_confirm_4950_used_207_count_8of8": all(
                [item for item in seed_receipts if item["owner"] == owner][-1][
                    "receipt"
                ]["after"]["used"]
                == 4950
                and [item for item in seed_receipts if item["owner"] == owner][-1][
                    "receipt"
                ]["after"]["count"]
                == 207
                for owner in range(8)
            ),
        },
        "captures": capture_results,
        "capture_contract": {
            "tags_exact": [item["tag"] for item in manifest] == EXPECTED_TAGS,
            "all_1600x1200": all(
                item["size"] == [1600, 1200] for item in capture_results
            ),
            "all_nonblack_pixels_within_800x600": all(
                item["nonblack_outside_800x600"] == 0
                for item in capture_results
            ),
            "plus10000_and_minimap_bytes_equal": Path(
                plus10000["path"]
            ).read_bytes()
            == Path(minimap["path"]).read_bytes(),
        },
    }
    encoded = json.dumps(result, ensure_ascii=False, sort_keys=True)
    print(encoded)
    print("canonical_sha256=" + hashlib.sha256(encoded.encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
