#!/usr/bin/env python3
"""x11_mouse_click.py — X11/XTest 기반 마우스 이동/클릭 주입"""

from __future__ import annotations

import argparse
import ctypes
import time


X11 = ctypes.cdll.LoadLibrary("libX11.so.6")
Xtst = ctypes.cdll.LoadLibrary("libXtst.so.6")

Display_p = ctypes.c_void_p
Bool = ctypes.c_int

X11.XOpenDisplay.argtypes = [ctypes.c_char_p]
X11.XOpenDisplay.restype = Display_p
X11.XCloseDisplay.argtypes = [Display_p]
X11.XCloseDisplay.restype = ctypes.c_int
X11.XFlush.argtypes = [Display_p]
X11.XFlush.restype = ctypes.c_int
Xtst.XTestFakeMotionEvent.argtypes = [Display_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
Xtst.XTestFakeMotionEvent.restype = ctypes.c_int
Xtst.XTestFakeButtonEvent.argtypes = [Display_p, ctypes.c_uint, Bool, ctypes.c_ulong]
Xtst.XTestFakeButtonEvent.restype = ctypes.c_int


def _open_display(display_name: str | None) -> Display_p:
    disp = X11.XOpenDisplay(display_name.encode() if display_name else None)
    if not disp:
        raise RuntimeError(f"XOpenDisplay failed for {display_name!r}")
    return disp


def _move(disp: Display_p, x: int, y: int) -> None:
    Xtst.XTestFakeMotionEvent(disp, -1, x, y, 0)
    X11.XFlush(disp)


def _button(disp: Display_p, button: int, down: bool) -> None:
    Xtst.XTestFakeButtonEvent(disp, button, 1 if down else 0, 0)
    X11.XFlush(disp)


def click(display_name: str | None, x: int, y: int, button: int = 1, hold_ms: int = 30) -> None:
    disp = _open_display(display_name)
    try:
        _move(disp, x, y)
        time.sleep(0.05)
        _button(disp, button, True)
        time.sleep(max(hold_ms, 1) / 1000.0)
        _button(disp, button, False)
    finally:
        X11.XCloseDisplay(disp)


def button_event(display_name: str | None, x: int, y: int, button: int, down: bool) -> None:
    disp = _open_display(display_name)
    try:
        _move(disp, x, y)
        time.sleep(0.02)
        _button(disp, button, down)
    finally:
        X11.XCloseDisplay(disp)


def drag(display_name: str | None, x1: int, y1: int, x2: int, y2: int, button: int = 1, hold_ms: int = 100, steps: int = 12) -> None:
    disp = _open_display(display_name)
    try:
        _move(disp, x1, y1)
        time.sleep(0.05)
        _button(disp, button, True)
        time.sleep(max(hold_ms, 1) / 1000.0)
        steps = max(steps, 1)
        for i in range(1, steps + 1):
            t = i / steps
            _move(disp, round(x1 + (x2 - x1) * t), round(y1 + (y2 - y1) * t))
            time.sleep(0.01)
        _button(disp, button, False)
    finally:
        X11.XCloseDisplay(disp)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Send a mouse click to the active X11 display.")
    ap.add_argument("x", type=int)
    ap.add_argument("y", type=int)
    ap.add_argument("--display", default=None)
    ap.add_argument("--button", type=int, default=1)
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--interval-ms", type=int, default=250)
    ap.add_argument("--hold-ms", type=int, default=30)
    ap.add_argument("--drag-to", nargs=2, type=int, metavar=("X", "Y"))
    ap.add_argument("--steps", type=int, default=12)
    ap.add_argument("--down-only", action="store_true")
    ap.add_argument("--up-only", action="store_true")
    args = ap.parse_args(argv)

    if args.down_only and args.up_only:
        raise SystemExit("--down-only and --up-only are mutually exclusive")
    if args.down_only or args.up_only:
        button_event(args.display, args.x, args.y, args.button, down=args.down_only)
        return 0
    if args.drag_to:
        drag(args.display, args.x, args.y, args.drag_to[0], args.drag_to[1], button=args.button, hold_ms=args.hold_ms, steps=args.steps)
        return 0

    for i in range(max(args.repeat, 1)):
        click(args.display, args.x, args.y, button=args.button, hold_ms=args.hold_ms)
        if i + 1 < args.repeat:
            time.sleep(max(args.interval_ms, 0) / 1000.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
