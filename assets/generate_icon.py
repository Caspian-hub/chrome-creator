#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ASSETS_DIR = Path(__file__).resolve().parent
PNG_PATH = ASSETS_DIR / "icon.png"
ICO_PATH = ASSETS_DIR / "icon.ico"

BG = "#FFFFFF"
PRIMARY = "#5A94C7"
PRIMARY_LIGHT = "#C5DCF0"
BORDER = "#D6E4F0"


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = max(4, size // 16)
    outer = (margin, margin, size - margin, size - margin)
    draw.rounded_rectangle(outer, radius=size // 5, fill=BG, outline=BORDER, width=max(2, size // 32))

    gap = size // 28
    top = margin + size // 10
    bar_h = size // 7
    draw.rounded_rectangle(
        (margin + size // 10, top, size - margin - size // 10, top + bar_h),
        radius=size // 20,
        fill=PRIMARY,
    )

    left = margin + size // 8
    right = size - margin - size // 8
    bottom = size - margin - size // 10
    mid = size // 2
    draw.rounded_rectangle((left, top + bar_h + gap, mid - gap // 2, bottom), radius=size // 16, fill=PRIMARY_LIGHT, outline=PRIMARY, width=max(1, size // 64))
    draw.rounded_rectangle((mid + gap // 2, top + bar_h + gap, right, bottom), radius=size // 16, fill=PRIMARY_LIGHT, outline=PRIMARY, width=max(1, size // 64))

    dot_r = max(2, size // 36)
    for cx in (left + size // 12, left + size // 7, left + size // 5):
        draw.ellipse((cx - dot_r, top + bar_h // 2 - dot_r, cx + dot_r, top + bar_h // 2 + dot_r), fill=BG)

    return img


def main() -> None:
    base = draw_icon(256)
    base.save(PNG_PATH)
    base.save(ICO_PATH, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print(f"Generated: {PNG_PATH}")
    print(f"Generated: {ICO_PATH}")


if __name__ == "__main__":
    main()
