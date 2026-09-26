"""Lap351 read-only check of the lap286 fixture-offset ambiguity.

This probe does not reinterpret the save format.  It takes the independently
extracted lap286 serializer order as the reviewed model, then evaluates every
combination left open by lap286/lap322:

* file offsets 210/212 assigned as width/height in either order; and
* quarter layers evaluated as ((w // 2) * h) // 2 or (w * h) // 4.

For the four current square, even fixtures, the question is whether those
ambiguities can change the reported bulk, PlayerStruct, or roster file offset.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
from pathlib import Path
from types import ModuleType


REPO = Path(__file__).resolve().parents[4]
LAP286_PROBE = (
    REPO
    / "docs/history/laps/probes/20260912_lap286_middle_save_layout_review_probe.py"
)
LAP322_CONTRACT = REPO / "docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md"
LAP350_REVIEW = REPO / "docs/work/active/G1_S1_LOAD_ENTRY_MIDDLE_REVIEW_LAP350.md"

EXPECTED_INPUT_SHA = {
    LAP286_PROBE: "604e7f8ca8201c54685cd6b57af7286e3da6eafe1169b895be6dd6605080c9fd",
    LAP322_CONTRACT: "b5b54f56a2fc4a944a4a6d93f454c428c8754e3a09320f6c40cb355d83df1e95",
    LAP350_REVIEW: "c8576fdc4066541d67de2db9be1111ac2c501e7a07d7079b6ebb77421eeafed8",
}

EXPECTED_OFFSETS = {
    "save000.dat": (1_455_954, 2_259_634, 2_388_902),
    "save006.dat": (1_455_954, 2_259_634, 2_388_902),
    "save011.dat": (772_754, 1_576_434, 1_705_702),
    "save012.dat": (772_754, 1_576_434, 1_705_702),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_lap286() -> ModuleType:
    spec = importlib.util.spec_from_file_location("lap286_save_layout", LAP286_PROBE)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load lap286 probe")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ordered_components(module: ModuleType) -> list[tuple[str, dict[str, object]]]:
    save_code = module.body(
        module.SAVE_ENTRY, limit=module.SAVE_END - module.SAVE_ENTRY
    )
    layers: list[int] = []
    helpers: list[int] = []
    direct = module.fwrite_sites(save_code)
    for _address, op, args in save_code:
        if op != "call":
            continue
        target = module.call_target(args)
        if target is not None and 0x42A000 <= target < 0x42C000:
            layers.append(target)
        elif target in (0x403950, 0x4441E0, 0x4464B0):
            helpers.append(target)

    layer_by_target = {
        model["target"]: model for model in map(module.classify_layer, layers)
    }
    helper_by_target: dict[str, dict[str, object]] = {}
    for target in helpers:
        sites = module.fwrite_sites(module.body(target))
        if len(sites) != 1:
            raise RuntimeError(f"helper {target:#x} has {len(sites)} fwrite sites")
        site = sites[0]
        helper_by_target[f"{target:#010x}"] = {
            "bytes": int(site["count"]) * int(site["size"])
        }

    ordered: list[tuple[str, dict[str, object]]] = []
    pushes: list[str] = []
    direct_index = 0
    for _address, op, args in save_code:
        if op == "push":
            pushes.append(args)
            continue
        if op != "call":
            continue
        target = module.call_target(args)
        if target == module.FWRITE:
            site = direct[direct_index]
            direct_index += 1
            ordered.append(
                (
                    "literal",
                    {
                        "bytes": int(site["count"]) * int(site["size"]),
                        "ptr": site["ptr"],
                    },
                )
            )
        elif target is not None and f"{target:#010x}" in layer_by_target:
            ordered.append(("layer", layer_by_target[f"{target:#010x}"]))
        elif target is not None and f"{target:#010x}" in helper_by_target:
            ordered.append(("helper", helper_by_target[f"{target:#010x}"]))
        elif target == module.SAVE_ROSTER:
            ordered.append(("roster", {}))
        pushes = []
    return ordered


def layer_bytes(
    item: dict[str, object], width: int, height: int, half_formula: str
) -> int:
    mode = item["mode"]
    if mode == "fixed_count":
        return int(item["fixed_bytes"])
    repeat = int(item["repeat"])
    element = int(item["element_bytes"])
    if mode == "full_area":
        cells = width * height
    elif half_formula == "sequential_signed_positive":
        cells = ((width // 2) * height) // 2
    elif half_formula == "product_quarter":
        cells = (width * height) // 4
    else:
        raise RuntimeError(f"unknown half formula: {half_formula}")
    return cells * repeat * element


def offsets_for(
    module: ModuleType,
    ordered: list[tuple[str, dict[str, object]]],
    width: int,
    height: int,
    half_formula: str,
) -> tuple[int, int, int]:
    cursor = 0
    bulk_offset: int | None = None
    for kind, item in ordered:
        if kind == "literal":
            if item["ptr"] == module.BULK_PTR:
                bulk_offset = cursor
            cursor += int(item["bytes"])
        elif kind == "helper":
            cursor += int(item["bytes"])
        elif kind == "layer":
            cursor += layer_bytes(item, width, height, half_formula)
        elif kind == "roster":
            break
    if bulk_offset is None:
        raise RuntimeError("bulk block not found in serializer order")
    player0_offset = bulk_offset + (module.PLAYER_BASE - module.BULK_PTR)
    return bulk_offset, player0_offset, cursor


def main() -> int:
    failures: list[str] = []
    for path, expected in EXPECTED_INPUT_SHA.items():
        actual = sha256(path)
        if actual != expected:
            failures.append(f"input SHA changed: {path}: {actual}")

    module = load_lap286()
    if sha256(module.EXE) != module.EXPECTED_EXE_SHA:
        failures.append("original executable SHA differs from lap286")
    ordered = ordered_components(module)

    fixtures: dict[str, object] = {}
    for name, (path, expected_size, expected_sha) in module.FIXTURES.items():
        data = path.read_bytes()
        if len(data) != expected_size or sha256(path) != expected_sha:
            failures.append(f"fixture identity changed: {name}")
        first, second = struct.unpack_from("<HH", data, 210)
        variants: dict[str, dict[str, object]] = {}
        values: set[tuple[int, int, int]] = set()
        for assignment, (width, height) in {
            "210_width_212_height": (first, second),
            "212_width_210_height": (second, first),
        }.items():
            for half_formula in (
                "sequential_signed_positive",
                "product_quarter",
            ):
                offsets = offsets_for(
                    module, ordered, width, height, half_formula
                )
                values.add(offsets)
                variants[f"{assignment}+{half_formula}"] = {
                    "dimensions": [width, height],
                    "bulk_file_offset": offsets[0],
                    "player0_file_offset": offsets[1],
                    "roster_file_offset": offsets[2],
                }
        invariant = len(values) == 1
        sole = next(iter(values)) if invariant else None
        if not invariant:
            failures.append(f"{name} offsets vary across allowed ambiguities")
        if sole != EXPECTED_OFFSETS[name]:
            failures.append(
                f"{name} invariant offsets {sole} != lap286 {EXPECTED_OFFSETS[name]}"
            )
        fixtures[name] = {
            "stored_u16_at_210_212": [first, second],
            "square": first == second,
            "even": first % 2 == 0 and second % 2 == 0,
            "variant_count": len(variants),
            "distinct_offset_tuples": [list(v) for v in sorted(values)],
            "offsets_invariant": invariant,
            "variants": variants,
        }

    report = {
        "lap": 351,
        "scope": {
            "game_started": False,
            "wine_started": False,
            "xvfb_started": False,
            "fixture_written": False,
            "product_code_changed": False,
        },
        "ambiguities_enumerated": {
            "dimension_assignments": 2,
            "halving_formulas": 2,
            "combinations_per_fixture": 4,
        },
        "fixtures": fixtures,
        "conclusion": (
            "current four fixture offsets are invariant; width/height semantics "
            "and odd/non-square extrapolation remain unknown"
        ),
        "failures": failures,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
