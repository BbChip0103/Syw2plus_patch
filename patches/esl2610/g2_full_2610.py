#!/usr/bin/env python3
"""G2 4093 on ESL 2610-line EXEs: layers 1+2+3 composed (runtime-pending build).

* layer 1 -- :mod:`g2_spike_build`: replay the accepted stock G2 ``.text``
  relocation of the six unit-capacity arrays into ``.g2bss`` (product edits
  such as the owner cap and the supply formula are not replayed);
* layer 2 -- :mod:`g2_newcode_2610`: retarget the 2610 modules' operands at
  the relocated arrays, with pool/exist end sentinels at 4093 slots;
* layer 3 -- :mod:`g2_state_2610`: move the modules' per-unit state into
  ``.g2bss`` grown to 4093 and raise every capacity constant;
* layer 4 -- :mod:`g2_persist_2610`: save/load sidecars in ``.g2code``.

``.g2bss`` holds the six arrays, then (0x1000-aligned) the moved module state.
Not wired into the deliverable builder (:mod:`g2_pool4093_2610`) until the
live lane and a save/load of a >1200-unit game pass.
"""

from __future__ import annotations

import hashlib
from typing import Any

from patches.esl2610 import (
    g2_newcode_2610,
    g2_persist_2610,
    g2_reloc_2610,
    g2_spike_build,
    g2_state_2610,
)


def _state_base(six_base: int, plan_direct_span: int) -> int:
    return (six_base + g2_reloc_2610.SIX_ARRAY_SPAN + plan_direct_span + 0xFFF) & ~0xFFF


def build_candidate(data: bytes, stock: bytes) -> tuple[bytes, dict[str, Any]]:
    plan = g2_reloc_2610.plan_spike(data, require_pinned_base=False)
    direct = sum(int(a["span_4093"], 16) for a in plan.direct_arrays)
    extra = g2_state_2610.block_size() + 0x2000 + g2_persist_2610.SCRATCH_BYTES
    l1, r1 = g2_spike_build.build_spike_candidate(data, stock, extra_bss=extra)
    six_base = int(r1["g2bss_va"], 16)
    l2, r2 = g2_newcode_2610.apply(l1, data, six_base, clamp=g2_reloc_2610.CAPACITY)
    state_base = _state_base(six_base, direct)
    g2bss_end = six_base + int(_g2bss_vsize(l2))
    if state_base + g2_state_2610.block_size() > g2bss_end:
        raise ValueError(".g2bss is too small for the moved module state")
    l3, r3 = g2_state_2610.apply(l2, data, state_base)
    flag_va = (state_base + g2_state_2610.block_size() + 0x13) & ~3
    scratch_va = (flag_va + 0x13) & ~0xF
    if scratch_va + g2_persist_2610.SCRATCH_BYTES > g2bss_end:
        raise ValueError(".g2bss has no room for the save-format flag and scratch")
    if state_base + g2_state_2610.block_size() != g2_state_2610.layout(state_base)["__end__"]:
        raise ValueError("block_size disagrees with the layout end")
    l4, r4 = g2_persist_2610.apply(l3, six_base, state_base, flag_va, scratch_va)
    return l4, {
        "schema": "syw2plus.esl2610.g2-full.v1",
        "status": "STATIC_ONLY_RUNTIME_PENDING",
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "candidate_sha256": hashlib.sha256(l4).hexdigest(),
        "layer1": r1, "layer2": r2, "layer3": r3, "layer4": r4,
    }


def _g2bss_vsize(image: bytes) -> int:
    import pefile

    pe = pefile.PE(data=image, fast_load=True)
    try:
        sec = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".g2bss")
        return int(sec.Misc_VirtualSize)
    finally:
        pe.close()
