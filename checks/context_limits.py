#!/usr/bin/env python3
"""Bound fresh-session memory without deleting instructions or promoting evidence."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
CAPS = {
    "docs/STATUS.md": 180,
    "docs/feedback/INBOX.md": 400,
    "docs/feedback/APPROVALS.md": 300,
    "loop/PROMPT.md": 180,
}
HEADINGS = (
    "## 지금 상태",
    "## 다음 한 가지",
    "## 지금 막힌 것 (Blockers)",
    "## 검증 상태",
    "## 바퀴 기록",
)


def check(root: Path) -> list[str]:
    errors = []
    for name, cap in CAPS.items():
        path = root / name
        if not path.is_file():
            errors.append(f"Missing {name}")
            continue
        lines = path.read_text().splitlines()
        if len(lines) > cap:
            errors.append(f"{name}: {len(lines)} lines exceeds {cap}; archive with provenance")
        if name == "docs/STATUS.md":
            for heading in HEADINGS:
                if lines.count(heading) != 1:
                    errors.append(f"{name}: require exactly one {heading}")
    design = root / "docs/DESIGN.md"
    text = design.read_text() if design.is_file() else ""
    for heading in ["### G1", "### G2", "### G3", "### G4"]:
        if heading not in text:
            errors.append(f"DESIGN missing {heading}")
    return errors


if __name__ == "__main__":
    errors = check(ROOT)
    print("\n".join(errors) if errors else "CONTEXT_PASS")
    sys.exit(bool(errors))
