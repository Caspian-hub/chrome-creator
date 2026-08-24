from __future__ import annotations

import sys

import customtkinter as ctk

from ui.theme import (
    ASPECT_HEIGHT,
    ASPECT_WIDTH,
    DEFAULT_WINDOW_WIDTH,
    MIN_WINDOW_WIDTH,
    UI_BG,
    UI_BORDER,
    UI_BTN_BG,
    UI_BTN_HOVER,
    UI_BTN_PRIMARY_BG,
    UI_BTN_PRIMARY_HOVER,
    UI_BTN_PRIMARY_TEXT,
    UI_BTN_TEXT,
    UI_CARD,
    UI_FONT,
    UI_TEXT,
)


def _get_work_area(root) -> tuple[int, int, int, int]:
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", wintypes.LONG),
                    ("top", wintypes.LONG),
                    ("right", wintypes.LONG),
                    ("bottom", wintypes.LONG),
                ]

            rect = RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(rect), 0):
                return rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top
        except Exception:
            pass
    return 0, 0, root.winfo_screenwidth(), root.winfo_screenheight()


def center_window(root, default_width=DEFAULT_WINDOW_WIDTH, min_width=MIN_WINDOW_WIDTH) -> None:
    root.update_idletasks()
    ax, ay, aw, ah = _get_work_area(root)
    max_w, max_h = int(aw * 0.85), int(ah * 0.85)
    width = min(default_width, max_w)
    height = width * ASPECT_HEIGHT // ASPECT_WIDTH
    if height > max_h:
        height = max_h
        width = height * ASPECT_WIDTH // ASPECT_HEIGHT
    min_height = min_width * ASPECT_HEIGHT // ASPECT_WIDTH
    width, height = max(width, min_width), max(height, min_height)
    root.minsize(min_width, min_height)
    x = ax + max(0, (aw - width) // 2)
    y = ay + max(0, (ah - height) // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")


def show_centered(root) -> None:
    root.withdraw()
    center_window(root)
    root.after(0, lambda: (root.deiconify(), root.lift()))


def card(parent, **kwargs) -> ctk.CTkFrame:
    defaults = {
        "fg_color": UI_CARD,
        "border_color": UI_BORDER,
        "border_width": 1,
        "corner_radius": 8,
    }
    defaults.update(kwargs)
    return ctk.CTkFrame(parent, **defaults)


def btn(parent, primary: bool = False, **kwargs) -> ctk.CTkButton:
    if primary:
        defaults = {
            "fg_color": UI_BTN_PRIMARY_BG,
            "hover_color": UI_BTN_PRIMARY_HOVER,
            "text_color": UI_BTN_PRIMARY_TEXT,
            "border_width": 0,
        }
    else:
        defaults = {
            "fg_color": UI_BTN_BG,
            "hover_color": UI_BTN_HOVER,
            "text_color": UI_BTN_TEXT,
            "border_width": 1,
            "border_color": UI_BORDER,
        }
    defaults.update(kwargs)
    return ctk.CTkButton(parent, **defaults)


def label(parent, **kwargs) -> ctk.CTkLabel:
    kwargs.setdefault("text_color", UI_TEXT)
    kwargs.setdefault("font", UI_FONT)
    return ctk.CTkLabel(parent, **kwargs)


def entry(parent, **kwargs) -> ctk.CTkEntry:
    kwargs.setdefault("fg_color", UI_BG)
    kwargs.setdefault("border_color", UI_BORDER)
    kwargs.setdefault("text_color", UI_TEXT)
    kwargs.setdefault("font", UI_FONT)
    return ctk.CTkEntry(parent, **kwargs)
