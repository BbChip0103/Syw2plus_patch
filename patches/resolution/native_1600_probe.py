#!/usr/bin/env python3
"""Static 1600x1200 research build from the unchanged SHA-pinned QHD builder.

The imported QHD experiment remains immutable for its historical provenance.
This single-threaded wrapper scopes its dimensions only around one build/apply.
It does not claim UI parity, high-resolution asset support, or runtime safety.
"""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import json
from pathlib import Path
from typing import Iterator

from patches.resolution import qhd_probe


WIDTH = 1600
HEIGHT = 1200
RADIUS = 64


@contextmanager
def _native_dimensions() -> Iterator[None]:
    previous = (qhd_probe.WIDTH, qhd_probe.HEIGHT, qhd_probe.RADIUS)
    try:
        qhd_probe.WIDTH, qhd_probe.HEIGHT, qhd_probe.RADIUS = WIDTH, HEIGHT, RADIUS
        yield
    finally:
        qhd_probe.WIDTH, qhd_probe.HEIGHT, qhd_probe.RADIUS = previous


def build(source_bytes: bytes) -> tuple[bytes, dict[str, object]]:
    with _native_dimensions():
        return qhd_probe.build(source_bytes)


def apply(source: Path, target: Path) -> dict[str, object]:
    with _native_dimensions():
        return qhd_probe.apply(source, target)


def restore(target: Path) -> None:
    qhd_probe.restore(target)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("apply")
    command.add_argument("source", type=Path)
    command.add_argument("target", type=Path)
    command = commands.add_parser("restore")
    command.add_argument("target", type=Path)
    args = parser.parse_args()
    if args.command == "apply":
        print(json.dumps(apply(args.source, args.target), indent=2))
    else:
        restore(args.target)


if __name__ == "__main__":
    main()
