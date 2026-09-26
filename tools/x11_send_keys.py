#!/usr/bin/env python3
"""x11_send_keys.py — X11/XTest 기반 최소 키 입력 주입 도구

의존:
- libX11
- libXtst

용도:
- Xvfb + Wine 환경에서 활성 창에 Enter/Escape/Arrow 키 등을 주입
- 원본 EXE 자동 진행의 기초 입력 계층
"""

from __future__ import annotations

import argparse
import ctypes
import time


X11 = ctypes.cdll.LoadLibrary("libX11.so.6")
Xtst = ctypes.cdll.LoadLibrary("libXtst.so.6")

Display_p = ctypes.c_void_p
Window = ctypes.c_ulong
KeySym = ctypes.c_ulong
Bool = ctypes.c_int

X11.XOpenDisplay.argtypes = [ctypes.c_char_p]
X11.XOpenDisplay.restype = Display_p
X11.XCloseDisplay.argtypes = [Display_p]
X11.XCloseDisplay.restype = ctypes.c_int
X11.XFlush.argtypes = [Display_p]
X11.XFlush.restype = ctypes.c_int
X11.XStringToKeysym.argtypes = [ctypes.c_char_p]
X11.XStringToKeysym.restype = KeySym
X11.XKeysymToKeycode.argtypes = [Display_p, KeySym]
X11.XKeysymToKeycode.restype = ctypes.c_uint
Xtst.XTestFakeKeyEvent.argtypes = [Display_p, ctypes.c_uint, Bool, ctypes.c_ulong]
Xtst.XTestFakeKeyEvent.restype = ctypes.c_int


KEY_ALIASES = {
    "ENTER": "Return",
    "ESC": "Escape",
    "UP": "Up",
    "DOWN": "Down",
    "LEFT": "Left",
    "RIGHT": "Right",
    "SPACE": "space",
}


def send_key(display_name: str | None, key_name: str, hold_ms: int = 30) -> None:
    disp = X11.XOpenDisplay(display_name.encode() if display_name else None)
    if not disp:
        raise RuntimeError(f"XOpenDisplay failed for {display_name!r}")
    try:
        lookup = KEY_ALIASES.get(key_name.upper(), key_name)
        keysym = X11.XStringToKeysym(lookup.encode())
        if not keysym:
            raise RuntimeError(f"Unknown keysym: {key_name}")
        keycode = X11.XKeysymToKeycode(disp, keysym)
        if not keycode:
            raise RuntimeError(f"No keycode for keysym: {lookup}")
        Xtst.XTestFakeKeyEvent(disp, keycode, 1, 0)
        X11.XFlush(disp)
        time.sleep(max(hold_ms, 1) / 1000.0)
        Xtst.XTestFakeKeyEvent(disp, keycode, 0, 0)
        X11.XFlush(disp)
    finally:
        X11.XCloseDisplay(disp)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Send key(s) to the active X11 window using XTest.")
    ap.add_argument("keys", nargs="+", help="Key names (ENTER, ESC, UP, DOWN, LEFT, RIGHT, SPACE, Return, etc.)")
    ap.add_argument("--display", default=None, help="DISPLAY value (default: current env)")
    ap.add_argument("--repeat", type=int, default=1, help="Repeat count")
    ap.add_argument("--interval-ms", type=int, default=120, help="Interval between repeats")
    ap.add_argument("--hold-ms", type=int, default=30, help="Key press hold duration")
    args = ap.parse_args(argv)

    keys = args.keys
    for r in range(max(args.repeat, 1)):
        for i, key in enumerate(keys):
            send_key(args.display, key, hold_ms=args.hold_ms)
            if i + 1 < len(keys):
                time.sleep(max(args.interval_ms, 0) / 1000.0)
        if r + 1 < args.repeat:
            time.sleep(max(args.interval_ms, 0) / 1000.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
