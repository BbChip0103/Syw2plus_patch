from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def x11_module(monkeypatch: pytest.MonkeyPatch) -> tuple[ModuleType, MagicMock, MagicMock]:
    x11 = MagicMock()
    xtst = MagicMock()
    x11.XOpenDisplay.return_value = 101
    x11.XStringToKeysym.return_value = 0xFF0D
    x11.XKeysymToKeycode.return_value = 36
    libraries = {"libX11.so.6": x11, "libXtst.so.6": xtst}
    loads: list[str] = []

    def load_library(name: str) -> MagicMock:
        loads.append(name)
        return libraries[name]

    monkeypatch.setattr("ctypes.cdll.LoadLibrary", load_library)
    spec = importlib.util.spec_from_file_location(
        "isolated_x11_send_keys", ROOT / "tools/x11_send_keys.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert loads == ["libX11.so.6", "libXtst.so.6"]
    return module, x11, xtst


def test_enter_alias_sends_press_flush_sleep_release_flush_then_closes(
    x11_module: tuple[ModuleType, MagicMock, MagicMock], monkeypatch: pytest.MonkeyPatch
):
    module, x11, xtst = x11_module
    events: list[tuple[object, ...]] = []
    x11.XOpenDisplay.side_effect = lambda display: events.append(("open", display)) or 101
    x11.XStringToKeysym.side_effect = lambda name: events.append(("keysym", name)) or 0xFF0D
    x11.XKeysymToKeycode.side_effect = (
        lambda display, keysym: events.append(("keycode", display, keysym)) or 36
    )
    xtst.XTestFakeKeyEvent.side_effect = (
        lambda display, keycode, pressed, delay: events.append(
            ("key", display, keycode, pressed, delay)
        )
    )
    x11.XFlush.side_effect = lambda display: events.append(("flush", display))
    monkeypatch.setattr(module.time, "sleep", lambda duration: events.append(("sleep", duration)))
    x11.XCloseDisplay.side_effect = lambda display: events.append(("close", display))

    module.send_key(":7", "ENTER", hold_ms=5)

    assert events == [
        ("open", b":7"),
        ("keysym", b"Return"),
        ("keycode", 101, 0xFF0D),
        ("key", 101, 36, 1, 0),
        ("flush", 101),
        ("sleep", 0.005),
        ("key", 101, 36, 0, 0),
        ("flush", 101),
        ("close", 101),
    ]


@pytest.mark.parametrize(
    ("failure", "message"),
    [("unknown", "Unknown keysym"), ("keycode", "No keycode"), ("error", "flush failed")],
)
def test_display_closes_on_lookup_and_injection_errors(
    x11_module: tuple[ModuleType, MagicMock, MagicMock],
    failure: str,
    message: str,
):
    module, x11, _xtst = x11_module
    x11.XOpenDisplay.return_value = 101
    if failure == "unknown":
        x11.XStringToKeysym.return_value = 0
    elif failure == "keycode":
        x11.XKeysymToKeycode.return_value = 0
    else:
        x11.XFlush.side_effect = OSError("flush failed")

    with pytest.raises(RuntimeError if failure != "error" else OSError, match=message):
        module.send_key(None, "ENTER")

    x11.XCloseDisplay.assert_called_once_with(101)
