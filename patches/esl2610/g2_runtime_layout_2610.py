#!/usr/bin/env python3
"""Runtime address contract for the ESL2610 G2 spike candidate's .g2bss arrays.

Mirrors :mod:`patches.population.g2_esl2608_runtime_layout` but for the 2610
spike: the six unit-capacity arrays live in one appended ``.g2bss`` section at
the image tail (VA ``0x1AB5000`` for the standalone G2 build), packed in the
same order and geometry the accepted full-tail layout uses.  A runtime probe or
the diagnostic bridge reads unit records from ``unit_pool_base`` and existence
words from ``unit_existence_base``.  Fail closed on an unexpected base.
"""

from __future__ import annotations

from dataclasses import dataclass

from patches.esl2610 import g2_reloc_2610

CAPACITY = g2_reloc_2610.CAPACITY
UNIT_STRIDE = g2_reloc_2610.UNIT_STRIDE
# Standalone G2 spike places .g2bss at the pinned 2610 first-free RVA.
ESL2610_SPIKE_POOL_BASE = 0x01AB5000


@dataclass(frozen=True)
class RuntimeLayout:
    capacity: int
    unit_pool_base: int
    unit_existence_base: int
    unit_stride: int


def from_pool_base(pool_base: int, capacity: int = CAPACITY) -> RuntimeLayout:
    if capacity != CAPACITY:
        raise ValueError(f"ESL2610 spike layout requires capacity {CAPACITY}, got {capacity}")
    # existence array starts just past the grown unit pool, per the packed geometry.
    geo = g2_reloc_2610._GEOMETRY
    pool_span = geo.regions[1].new_start - geo.regions[0].new_start
    return RuntimeLayout(
        capacity=CAPACITY,
        unit_pool_base=pool_base,
        unit_existence_base=pool_base + pool_span,
        unit_stride=UNIT_STRIDE,
    )


ESL2610_SPIKE_LAYOUT = from_pool_base(ESL2610_SPIKE_POOL_BASE)
