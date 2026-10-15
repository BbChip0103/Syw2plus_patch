from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUB = ROOT / "tools" / "inmm_stub"


def _exports() -> list[tuple[int, str, str]]:
    rows: list[tuple[int, str, str]] = []
    for line in (STUB / "g1_winmm_proxy.def").read_text(encoding="ascii").splitlines()[2:]:
        match = re.fullmatch(r"\s*(\w+)=(\w+) @(\d+)", line)
        if match:
            name, target, ordinal = match.groups()
        else:
            match = re.fullmatch(r"\s*(\w+) @(\d+) NONAME", line)
            assert match, f"unparsed WINMM export line: {line!r}"
            target, ordinal = match.groups()
            name = ""
        rows.append((int(ordinal), name, target))
    return rows


def test_g1_winmm_proxy_preserves_full_export_ordinal_map() -> None:
    rows = _exports()
    assert len(rows) == 189
    assert sorted(row[0] for row in rows) == list(range(2, 191))
    assert sum(bool(name) for _, name, _ in rows) == 186
    assert sum(not name for _, name, _ in rows) == 3

    by_name = {name: (ordinal, target) for ordinal, name, target in rows if name}
    assert {name: by_name[name] for name in (
        "mciSendCommandA", "timeBeginPeriod", "timeEndPeriod", "timeGetTime"
    )} == {
        "mciSendCommandA": (52, "g1_proxy_mciSendCommandA"),
        "timeBeginPeriod": (145, "g1_proxy_timeBeginPeriod"),
        "timeEndPeriod": (146, "g1_proxy_timeEndPeriod"),
        "timeGetTime": (149, "g1_proxy_timeGetTime"),
    }
    hooks = {"mciSendCommandA", "timeBeginPeriod", "timeEndPeriod", "timeGetTime"}
    assert all(target.startswith("g1_forward_") for _, name, target in rows if name not in hooks)
    assert all(target.startswith("g1_forward_ordinal_") for _, name, target in rows if not name)


def test_proxy_hooks_reuse_g1_exports_and_system_winmm_resolution() -> None:
    source = (STUB / "g1_winmm_proxy.c").read_text(encoding="utf-8")
    stub = (STUB / "inmm_stub.c").read_text(encoding="utf-8")
    makefile = (STUB / "Makefile").read_text(encoding="utf-8")
    assert "GetSystemDirectoryA" in source and "LoadLibraryA(path)" in source
    assert "return _imeBeginPeriod(period);" in source
    assert "return _imeEndPeriod(period);" in source
    assert "return _ciSendCommandA(device, command, flags, params);" in source
    assert "return _imeGetTime();" in source
    assert "#define INMM_EXPORT" in stub
    assert "SYW2_WINMM_PROXY" in makefile and "default-on-winmm" in makefile


def test_generated_forwarders_cover_each_named_stock_export() -> None:
    rows = _exports()
    asm = (STUB / "g1_winmm_forwarders.S").read_text(encoding="ascii")
    names = [name for _, name, target in rows if name and target.startswith("g1_forward_")]
    assert len(names) == 182
    for name in names:
        assert f'_g1_forward_{name}_name:' in asm
        assert f'.asciz "{name}"' in asm
    for ordinal in range(2, 5):
        assert f"g1_forward_ordinal_{ordinal} @{ordinal} NONAME" in (STUB / "g1_winmm_proxy.def").read_text(encoding="ascii")
