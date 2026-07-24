#!/usr/bin/env python3
"""Generate App Store listing images at exactly 1320 x 2868 for Astronode."""

from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
W, H = 1320, 2868
OUT = ROOT / "exports" / "iphone-1320x2868"
SRC = ROOT / "public" / "screenshots" / "apple" / "iphone" / "en"
REF = ROOT / "public" / "screenshots" / "references"
MOCKUP = ROOT / "public" / "mockup.png"

# Phone screen placement inside mockup.png (from template PHONE_SCREEN ratios)
MK_L, MK_T, MK_W, MK_H = 52 / 1022, 46 / 2082, 918 / 1022, 1990 / 2082

SERIF = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF_REG = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SANS = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
SANS_REG = "/System/Library/Fonts/Supplemental/Arial.ttf"

SLIDES = [
    {
        "file": "01-home.png",
        "headline": "Your Daily\nCosmic Guidance",
        "out": "01-daily-guidance.png",
    },
    {
        "file": "02-explore.png",
        "headline": "Explore the\nAstral Feed",
        "out": "02-astral-feed.png",
    },
    {
        "file": "03-sync-year.png",
        "headline": "Know Your\nCosmic Score",
        "out": "03-cosmic-score.png",
    },
    {
        "file": "04-overview.png",
        "headline": "See Your Full\nCosmic Overview",
        "out": "04-cosmic-overview.png",
    },
    {
        "file": "05-relationships.png",
        "headline": "Find Emotional\n& Mental Harmony",
        "out": "05-relationships.png",
    },
    {
        "file": "06-power-moves.png",
        "headline": "Cosmic Timing\nfor Success",
        "out": "06-power-moves.png",
    },
    {
        "file": "07-oracle.png",
        "headline": "Ask the Oracle\nAnything",
        "out": "07-oracle.png",
    },
    {
        "file": "08-quick-actions.png",
        "headline": "Capture Moments\nin Seconds",
        "out": "08-quick-actions.png",
    },
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def nebula_background(seed: int) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGB", (W, H), (8, 4, 18))
    px = img.load()

    # Deep space base gradient
    for y in range(H):
        t = y / H
        r = int(8 + 28 * t + 18 * math.sin(t * 3.1))
        g = int(4 + 10 * t)
        b = int(18 + 55 * (1 - abs(t - 0.45)) + 20 * math.sin(t * 2.4))
        for x in range(0, W, 2):
            px[x, y] = (min(255, r), min(255, g), min(255, b))
            if x + 1 < W:
                px[x + 1, y] = px[x, y]

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Nebula blobs
    for _ in range(18):
        cx = rng.randint(-100, W + 100)
        cy = rng.randint(0, H)
        rad = rng.randint(180, 520)
        color = rng.choice(
            [
                (90, 40, 160, 55),
                (140, 70, 190, 45),
                (180, 120, 60, 40),
                (60, 30, 120, 50),
                (210, 170, 90, 28),
            ]
        )
        draw.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=color)

    overlay = overlay.filter(ImageFilter.GaussianBlur(90))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

    # Stars
    star = ImageDraw.Draw(img)
    for _ in range(420):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        bright = rng.randint(140, 255)
        size = 1 if rng.random() < 0.82 else 2
        star.ellipse((x, y, x + size, y + size), fill=(bright, bright, min(255, bright + 20)))

    # Soft vignette
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(80):
        a = int(i * 1.6)
        vd.rectangle((i, i, W - 1 - i, H - 1 - i), outline=(0, 0, 0, a))
    vig = vig.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img.convert("RGBA"), vig).convert("RGB")
    return img


def draw_headline(canvas: Image.Image, text: str, gold: bool = False) -> None:
    draw = ImageDraw.Draw(canvas)
    f = font(SERIF, 92)
    lines = text.split("\n")
    line_heights = []
    widths = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        widths.append(bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    total_h = sum(line_heights) + (len(lines) - 1) * 18
    y = 168
    color = (232, 196, 110) if gold else (255, 255, 255)
    for i, line in enumerate(lines):
        x = (W - widths[i]) // 2
        # Soft glow
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.text((x, y), line, font=f, fill=(*color, 90))
        glow = glow.filter(ImageFilter.GaussianBlur(12))
        canvas.alpha_composite(glow)
        draw = ImageDraw.Draw(canvas)
        draw.text((x, y), line, font=f, fill=color)
        y += line_heights[i] + 18


def fit_cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    scale = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def compose_phone(screenshot_path: Path, phone_h: int = 1980) -> Image.Image:
    mock = Image.open(MOCKUP).convert("RGBA")
    scale = phone_h / mock.height
    phone_w = int(mock.width * scale)
    mock = mock.resize((phone_w, phone_h), Image.Resampling.LANCZOS)

    shot = Image.open(screenshot_path).convert("RGB")
    sx = int(mock.width * MK_L)
    sy = int(mock.height * MK_T)
    sw = int(mock.width * MK_W)
    sh = int(mock.height * MK_H)
    fitted = fit_cover(shot, sw, sh).convert("RGBA")

    # Mockup screen region is opaque black — paste UI on top with rounded clip.
    radius = int(min(sw, sh) * 0.11)
    mask = Image.new("L", (sw, sh), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, sw - 1, sh - 1), radius=radius, fill=255)

    composed = mock.copy()
    composed.paste(fitted, (sx, sy), mask)
    return composed


def add_phone_glow(canvas: Image.Image, phone: Image.Image, x: int, y: int) -> None:
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    blob = Image.new("RGBA", (phone.width + 120, phone.height + 120), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob)
    bd.rounded_rectangle(
        (40, 40, phone.width + 80, phone.height + 80),
        radius=90,
        fill=(210, 170, 90, 70),
    )
    blob = blob.filter(ImageFilter.GaussianBlur(55))
    glow.alpha_composite(blob, (x - 60, y - 60))
    canvas.alpha_composite(glow)
    canvas.alpha_composite(phone, (x, y))


def make_listing(screenshot: Path, headline: str, seed: int, gold_headline: bool = False) -> Image.Image:
    bg = nebula_background(seed).convert("RGBA")
    draw_headline(bg, headline, gold=gold_headline)
    phone = compose_phone(screenshot, phone_h=1980)
    x = (W - phone.width) // 2
    y = H - phone.height - 70
    add_phone_glow(bg, phone, x, y)
    return bg.convert("RGB")


def upscale_exact(src: Path, dest: Path) -> None:
    img = Image.open(src).convert("RGB")
    # Cover-fit into 1320x2868
    out = fit_cover(img, W, H)
    # Mild sharpen after upscale
    out = ImageEnhance.Sharpness(out).enhance(1.15)
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.save(dest, "PNG", optimize=True)


def make_app_icon() -> None:
    size = 1024
    img = Image.new("RGB", (size, size), (12, 8, 24))
    draw = ImageDraw.Draw(img)
    for i in range(40):
        a = 255 - i * 4
        c = (int(30 + i), int(12 + i * 0.4), int(50 + i * 1.5))
        draw.ellipse((i * 4, i * 4, size - i * 4, size - i * 4), outline=c)
    # Gold star
    cx, cy, r = size // 2, size // 2, 220
    pts = []
    for i in range(8):
        ang = math.radians(-90 + i * 45)
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=(232, 196, 110))
    path = ROOT / "public" / "app-icon.png"
    img.save(path, "PNG")
    print(f"Wrote {path}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_app_icon()

    # Upscale the two reference listing images to exact store size
    refs = [
        (REF / "01-explore-astral-feed.png", OUT / "ref-01-explore-the-astral-feed.png"),
        (REF / "02-know-cosmic-score.png", OUT / "ref-02-know-your-cosmic-score.png"),
    ]
    for src, dest in refs:
        upscale_exact(src, dest)
        assert Image.open(dest).size == (W, H)
        print(f"Reference {dest.name}: {Image.open(dest).size}")

    # Generate listing images from all original screenshots
    for i, slide in enumerate(SLIDES):
        src = SRC / slide["file"]
        dest = OUT / slide["out"]
        gold = i in (1, 2)  # match reference gold headlines for feed + score
        img = make_listing(src, slide["headline"], seed=1000 + i * 17, gold_headline=gold)
        assert img.size == (W, H)
        img.save(dest, "PNG", optimize=True)
        print(f"Listing {dest.name}: {img.size}")

    # Also save clean resized originals for App Store raw UI uploads if needed
    raw_dir = OUT / "originals-resized"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for slide in SLIDES:
        src = SRC / slide["file"]
        dest = raw_dir / slide["file"]
        upscale_exact(src, dest)
        assert Image.open(dest).size == (W, H)
        print(f"Original {dest.name}: {Image.open(dest).size}")

    manifest = OUT / "MANIFEST.txt"
    lines = [
        "Astronode App Store assets — exact 1320 x 2868 px",
        "",
        "Reference listing images (from your style references):",
        "  ref-01-explore-the-astral-feed.png",
        "  ref-02-know-your-cosmic-score.png",
        "",
        "Generated listing images (marketing frames from originals):",
    ]
    for slide in SLIDES:
        lines.append(f"  {slide['out']}  ← {slide['headline'].replace(chr(10), ' / ')}")
    lines += [
        "",
        "Resized originals (UI-only, no marketing frame):",
        "  originals-resized/*.png",
    ]
    manifest.write_text("\n".join(lines) + "\n")
    print(f"\nAll exports in {OUT}")


if __name__ == "__main__":
    main()
