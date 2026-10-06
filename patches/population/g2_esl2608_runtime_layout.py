"""Address contract for the appended ESL2608 4093-slot runtime sections.

The generic full-tail layout is still used by the older 4093-slot candidate
profile. ESL2608 appends its storage after the versioned source sections, so
its pool is shifted by the build-reported relocation delta. Keep that
distinction explicit and fail closed on the generic address.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from patches.population.full_tail_relocation_storage_layout_v1 import layout as full_layout

CAPACITY = 4093
ESL2608_POOL_BASE = 0x0112E000
REFERENCE_LAYOUT = full_layout(CAPACITY)
REFERENCE_POOL_BASE = REFERENCE_LAYOUT.regions[0].new_start
ESL2608_RELOCATION_DELTA = ESL2608_POOL_BASE - REFERENCE_POOL_BASE


@dataclass(frozen=True)
class RuntimeLayout:
    capacity: int
    unit_pool_base: int
    unit_existence_base: int
    unit_stride: int


def from_pool_base(pool_base: int, capacity: int = CAPACITY) -> RuntimeLayout:
    """Resolve the ESL2608 layout from its build-reported pool base."""

    if capacity != CAPACITY:
        raise ValueError(f"ESL2608 layout requires capacity {CAPACITY}, got {capacity}")
    if pool_base != ESL2608_POOL_BASE:
        raise ValueError(
            f"unexpected ESL2608 pool base 0x{pool_base:08X}; "
            f"expected 0x{ESL2608_POOL_BASE:08X}"
        )
    existence = REFERENCE_LAYOUT.regions[1]
    return RuntimeLayout(
        capacity=CAPACITY,
        unit_pool_base=pool_base,
        unit_existence_base=existence.new_start + ESL2608_RELOCATION_DELTA,
        unit_stride=REFERENCE_LAYOUT.regions[0].elem_size,
    )


def from_build_report(report: Mapping[str, object]) -> RuntimeLayout:
    """Validate and resolve the address fields emitted by the ESL2608 builder."""

    try:
        pool_base = int(str(report["pool_base_va"]), 0)
        relocation_delta = int(str(report["relocation_delta"]), 0)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("ESL2608 build report lacks valid pool/relocation fields") from exc
    if relocation_delta != ESL2608_RELOCATION_DELTA:
        raise ValueError(
            f"unexpected ESL2608 relocation delta 0x{relocation_delta:X}; "
            f"expected 0x{ESL2608_RELOCATION_DELTA:X}"
        )
    return from_pool_base(pool_base)


ESL2608_LAYOUT = from_pool_base(ESL2608_POOL_BASE)
