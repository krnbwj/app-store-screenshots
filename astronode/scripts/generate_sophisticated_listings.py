#!/usr/bin/env python3
"""
Astronode sophisticated App Store listing generator.

Outputs:
  final-output/iphone-1320x2868/
  final-output/ipad-2064x2752/

Uses Didot/New York serif headlines and nebula backgrounds sampled from
the reference listing images for a premium celestial look.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC_UI = ROOT / "public" / "screenshots" / "sources" / "ui"
SRC_REF = ROOT / "public" / "screenshots" / "sources" / "refs"
LEGACY = ROOT / "public" / "screenshots" / "apple" / "iphone" / "en"
MOCKUP = ROOT / "public" / "mockup.png"
OUT = ROOT / "final-output"

IPHONE = (1320, 2868)
IPAD = (2064, 2752)

# Template PHONE_SCREEN ratios for mockup.png
MK_L, MK_T, MK_W, MK_H = 52 / 1022, 46 / 2082, 918 / 1022, 1990 / 2082

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
NEWYORK = "/System/Library/Fonts/NewYork.ttf"
BODONI = "/System/Library/Fonts/Supplemental/Bodoni 72.ttc"
SANS_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

GOLD = (232, 196, 110)
GOLD_SOFT = (242, 214, 150)
CREAM = (250, 244, 230)

SLIDES = [
    {
        "id": "01-empower-daily-rituals",
        "headline": "Empower Your\nDaily Rituals",
        "ui": "01-home.png",
        "bg_ref": "01-empower-rituals.png",
        "legacy": "01-home.png",
    },
    {
        "id": "02-decode-relationships",
        "headline": "Decode Your\nRelationships",
        "ui": None,
        "bg_ref": "02-decode-relationships.png",
        "legacy": "05-relationships.png",
    },
    {
        "id": "03-consult-the-oracle",
        "headline": "Consult the\nOracle",
        "ui": None,
        "bg_ref": "03-consult-oracle.png",
        "legacy": "07-oracle.png",
    },
    {
        "id": "04-capture-your-thoughts",
        "headline": "Capture Your\nThoughts",
        "ui": None,
        "bg_ref": "04-capture-thoughts.png",
        "legacy": "08-quick-actions.png",
    },
    {
        "id": "05-cosmic-daily-guide",
        "headline": "Your Cosmic\nDaily Guide",
        "ui": "01-home.png",
        "bg_ref": "05-cosmic-daily-guide.png",
        "legacy": "01-home.png",
    },
    {
        "id": "06-explore-astral-feed",
        "headline": "Explore the\nAstral Feed",
        "ui": "02-explore.png",
        "bg_ref": "01-empower-rituals.png",
        "legacy": "02-explore.png",
    },
    {
        "id": "07-cosmic-overview",
        "headline": "See Your Full\nCosmic Overview",
        "ui": "03-overview.png",
        "bg_ref": "05-cosmic-daily-guide.png",
        "legacy": "04-overview.png",
    },
    {
        "id": "08-cosmic-profile",
        "headline": "Your Ethereal\nCosmic Profile",
        "ui": "04-profile.png",
        "bg_ref": "02-decode-relationships.png",
        "legacy": "04-overview.png",
    },
]


def load_font(size: int, prefer: str = "didot") -> ImageFont.FreeTypeFont:
    paths = {
        "didot": [(DIDOT, 0), (DIDOT, 1), (BODONI, 0), (NEWYORK, 0)],
        "newyork": [(NEWYORK, 0), (DIDOT, 0)],
        "bodoni": [(BODONI, 0), (DIDOT, 0)],
    }
    for path, index in paths.get(prefer, paths["didot"]):
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except Exception:
            continue
    return ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Bold.ttf", size)


def fit_cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    scale = max(tw / img.width, th / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def resolve_ui(slide: dict) -> Path:
    if slide["ui"]:
        p = SRC_UI / slide["ui"]
        if p.exists():
            return p
    legacy = LEGACY / slide["legacy"]
    if legacy.exists():
        return legacy
    # Fallback: crop phone content from reference listing
    return SRC_REF / slide["bg_ref"]


def nebula_from_reference(ref_path: Path, size: tuple[int, int], seed: int) -> Image.Image:
    """Build a sophisticated nebula canvas from a reference listing image."""
    w, h = size
    ref = Image.open(ref_path).convert("RGB")
    base = fit_cover(ref, w, h)
    rng = random.Random(seed)

    # Sample nebula patches from edges (avoid center phone) and rebuild center
    patches = []
    for box in [
        (0, 0, int(w * 0.28), int(h * 0.35)),
        (int(w * 0.72), 0, w, int(h * 0.35)),
        (0, int(h * 0.55), int(w * 0.25), h),
        (int(w * 0.75), int(h * 0.55), w, h),
        (0, int(h * 0.12), w, int(h * 0.22)),
    ]:
        crop = base.crop(box)
        patches.append(fit_cover(crop, w, h))

    rebuilt = patches[0].copy()
    for i, patch in enumerate(patches[1:], start=1):
        alpha = Image.new("L", (w, h), 0)
        ad = ImageDraw.Draw(alpha)
        if i <= 2:
            ad.rectangle((0, 0, w, int(h * 0.4)), fill=180)
        else:
            ad.ellipse((-int(w * 0.2), int(h * 0.2), int(w * 1.2), int(h * 1.2)), fill=140)
        alpha = alpha.filter(ImageFilter.GaussianBlur(80))
        rebuilt = Image.composite(patch, rebuilt, alpha)

    # Keep a whisper of the original edges for authentic nebula texture
    edge_mask = Image.new("L", (w, h), 0)
    ed = ImageDraw.Draw(edge_mask)
    border = int(min(w, h) * 0.16)
    ed.rectangle((0, 0, w, h), fill=255)
    ed.rectangle((border, int(h * 0.18), w - border, h - int(h * 0.02)), fill=0)
    edge_mask = edge_mask.filter(ImageFilter.GaussianBlur(55))
    base = Image.composite(base, rebuilt, edge_mask)
    base = base.filter(ImageFilter.GaussianBlur(1.2))

    # Enrich with layered glow blobs
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for _ in range(12):
        cx = rng.randint(0, w)
        cy = rng.randint(0, h)
        rad = rng.randint(int(min(w, h) * 0.12), int(min(w, h) * 0.4))
        color = rng.choice(
            [
                (120, 50, 170, 42),
                (180, 90, 160, 36),
                (210, 150, 80, 30),
                (70, 30, 110, 48),
                (240, 200, 140, 20),
            ]
        )
        gd.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=color)
    glow = glow.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.085)))
    canvas = Image.alpha_composite(base.convert("RGBA"), glow)

    # Fine starfield
    stars = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars)
    count = int(420 * (w * h) / (1320 * 2868))
    for _ in range(count):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        b = rng.randint(170, 255)
        s = 1 if rng.random() < 0.85 else 2
        sd.ellipse((x, y, x + s, y + s), fill=(b, b, min(255, b + 30), 200))
    for _ in range(22):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, int(h * 0.55))
        r = rng.randint(2, 4)
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 236, 190, 170))
    canvas = Image.alpha_composite(canvas, stars.filter(ImageFilter.GaussianBlur(0.5)))

    # Soft vignette
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(100):
        vd.rectangle((i, i, w - 1 - i, h - 1 - i), outline=(0, 0, 0, int(i * 1.35)))
    canvas = Image.alpha_composite(canvas, vig.filter(ImageFilter.GaussianBlur(50)))
    return canvas.convert("RGBA")


def draw_sophisticated_headline(canvas: Image.Image, text: str, size: tuple[int, int]) -> None:
    w, h = size
    font_size = int(88 * (w / 1320))
    font = load_font(font_size, "didot")
    lines = text.split("\n")
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))

    widths, heights = [], []
    for line in lines:
        bbox = probe.textbbox((0, 0), line, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    gap = int(14 * (w / 1320))
    y = int(h * 0.052)

    for i, line in enumerate(lines):
        x = (w - widths[i]) // 2
        # Soft gold bloom only (no stacked opaque redraws)
        glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.text((x, y), line, font=font, fill=(232, 196, 110, 95))
        glow = glow.filter(ImageFilter.GaussianBlur(14))
        canvas.alpha_composite(glow)

        draw = ImageDraw.Draw(canvas)
        draw.text((x, y), line, font=font, fill=GOLD)
        y += heights[i] + gap


def compose_iphone(screenshot_path: Path, phone_h: int) -> Image.Image:
    mock = Image.open(MOCKUP).convert("RGBA")
    scale = phone_h / mock.height
    phone_w = int(mock.width * scale)
    mock = mock.resize((phone_w, phone_h), Image.Resampling.LANCZOS)

    shot = Image.open(screenshot_path).convert("RGB")
    # If source is a full listing ref, try to use as-is cover into screen
    sx = int(mock.width * MK_L)
    sy = int(mock.height * MK_T)
    sw = int(mock.width * MK_W)
    sh = int(mock.height * MK_H)
    fitted = fit_cover(shot, sw, sh).convert("RGBA")

    radius = int(min(sw, sh) * 0.105)
    mask = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw - 1, sh - 1), radius=radius, fill=255)

    composed = mock.copy()
    composed.paste(fitted, (sx, sy), mask)
    return composed


def compose_ipad_frame(screenshot_path: Path, frame_h: int) -> Image.Image:
    """Slim iPad Pro-style frame around the UI screenshot."""
    # iPad aspect ~ 2064/2752 device, but content is phone UI — use landscape-ish tablet bezel
    # Frame aspect close to 3:4
    frame_w = int(frame_h * 0.75)
    bezel = max(18, int(frame_w * 0.028))
    radius = int(frame_w * 0.045)

    shot = fit_cover(Image.open(screenshot_path).convert("RGB"), frame_w - bezel * 2, frame_h - bezel * 2)

    frame = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    # Outer metal
    fd.rounded_rectangle((0, 0, frame_w - 1, frame_h - 1), radius=radius, fill=(28, 28, 30, 255))
    # Inner black
    inner_r = max(8, radius - 6)
    fd.rounded_rectangle(
        (bezel - 2, bezel - 2, frame_w - bezel + 1, frame_h - bezel + 1),
        radius=inner_r,
        fill=(0, 0, 0, 255),
    )
    # Screen
    screen_mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(screen_mask).rounded_rectangle(
        (0, 0, shot.width - 1, shot.height - 1), radius=max(6, inner_r - 4), fill=255
    )
    frame.paste(shot.convert("RGBA"), (bezel, bezel), screen_mask)

    # Camera dot
    cam_y = bezel // 2
    cam_x = frame_w // 2
    fd.ellipse((cam_x - 4, cam_y - 4, cam_x + 4, cam_y + 4), fill=(10, 10, 12, 255))
    return frame


def add_device_glow(canvas: Image.Image, device: Image.Image, x: int, y: int) -> None:
    glow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    pad = 140
    blob = Image.new("RGBA", (device.width + pad, device.height + pad), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blob)
    bd.rounded_rectangle(
        (pad // 3, pad // 3, device.width + pad * 2 // 3, device.height + pad * 2 // 3),
        radius=100,
        fill=(210, 170, 100, 55),
    )
    blob = blob.filter(ImageFilter.GaussianBlur(60))
    glow.alpha_composite(blob, (x - pad // 3, y - pad // 3))
    # Soft purple ambient under device
    ambient = Image.new("RGBA", (device.width + 200, 180), (0, 0, 0, 0))
    ad = ImageDraw.Draw(ambient)
    ad.ellipse((0, 0, device.width + 200, 180), fill=(120, 60, 160, 50))
    ambient = ambient.filter(ImageFilter.GaussianBlur(40))
    glow.alpha_composite(ambient, (x - 100, y + device.height - 80))
    canvas.alpha_composite(glow)
    canvas.alpha_composite(device, (x, y))


def make_listing(slide: dict, size: tuple[int, int], device: str) -> Image.Image:
    w, h = size
    seed = sum(ord(c) for c in slide["id"]) + w
    bg = nebula_from_reference(SRC_REF / slide["bg_ref"], size, seed=seed)
    draw_sophisticated_headline(bg, slide["headline"], size)

    ui_path = resolve_ui(slide)
    if device == "iphone":
        phone_h = int(h * 0.70)
        device_img = compose_iphone(ui_path, phone_h=phone_h)
        x = (w - device_img.width) // 2
        y = h - device_img.height - int(h * 0.018)
    else:
        # iPad listing: tablet frame, slightly smaller relative height to show nebula
        frame_h = int(h * 0.72)
        device_img = compose_ipad_frame(ui_path, frame_h=frame_h)
        x = (w - device_img.width) // 2
        y = h - device_img.height - int(h * 0.03)

    add_device_glow(bg, device_img, x, y)
    out = bg.convert("RGB")
    out = ImageEnhance.Contrast(out).enhance(1.04)
    out = ImageEnhance.Color(out).enhance(1.06)
    return out


def upscale_reference(ref_name: str, size: tuple[int, int], dest: Path) -> None:
    img = fit_cover(Image.open(SRC_REF / ref_name).convert("RGB"), *size)
    img = ImageEnhance.Sharpness(img).enhance(1.12)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "PNG", optimize=True)


def save_resized_originals(size: tuple[int, int], dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(SRC_UI.glob("*.png")):
        out = fit_cover(Image.open(p).convert("RGB"), *size)
        out.save(dest_dir / p.name, "PNG", optimize=True)


def main() -> None:
    iphone_dir = OUT / "iphone-1320x2868"
    ipad_dir = OUT / "ipad-2064x2752"
    refs_iphone = iphone_dir / "reference-listings"
    refs_ipad = ipad_dir / "reference-listings"
    for d in (iphone_dir, ipad_dir, refs_iphone, refs_ipad):
        d.mkdir(parents=True, exist_ok=True)

    # Exact-size versions of the 5 sophisticated reference listings
    ref_files = [
        ("01-empower-rituals.png", "ref-01-empower-your-daily-rituals.png"),
        ("02-decode-relationships.png", "ref-02-decode-your-relationships.png"),
        ("03-consult-oracle.png", "ref-03-consult-the-oracle.png"),
        ("04-capture-thoughts.png", "ref-04-capture-your-thoughts.png"),
        ("05-cosmic-daily-guide.png", "ref-05-your-cosmic-daily-guide.png"),
    ]
    for src, name in ref_files:
        upscale_reference(src, IPHONE, refs_iphone / name)
        upscale_reference(src, IPAD, refs_ipad / name)
        assert Image.open(refs_iphone / name).size == IPHONE
        assert Image.open(refs_ipad / name).size == IPAD
        print(f"ref ok {name}")

    # Generated sophisticated listings from new screenshots + refs
    for slide in SLIDES:
        iphone = make_listing(slide, IPHONE, "iphone")
        ipad = make_listing(slide, IPAD, "ipad")
        assert iphone.size == IPHONE
        assert ipad.size == IPAD
        iphone.save(iphone_dir / f"{slide['id']}.png", "PNG", optimize=True)
        ipad.save(ipad_dir / f"{slide['id']}.png", "PNG", optimize=True)
        print(f"listing ok {slide['id']}")

    save_resized_originals(IPHONE, iphone_dir / "originals-resized")
    save_resized_originals(IPAD, ipad_dir / "originals-resized")

    manifest = OUT / "README.md"
    manifest.write_text(
        """# Astronode Final Output (Sophisticated)

Store-ready listing images with Didot/New York gold headlines and nebula backgrounds
sampled from your reference listings.

## Sizes

| Device | Folder | Exact size |
|--------|--------|------------|
| iPhone 6.9" | `iphone-1320x2868/` | **1320 × 2868** |
| iPad 13" | `ipad-2064x2752/` | **2064 × 2752** |

## Contents (each size folder)

- `01-…`–`08-….png` — generated marketing listing images
- `reference-listings/` — your 5 sophisticated reference listings resized exactly
- `originals-resized/` — raw UI captures fitted to store size

## Regenerate

```bash
python3 scripts/generate_sophisticated_listings.py
```

## Upload tips

- App Store Connect → iPhone 6.9" display: use `iphone-1320x2868/`
- App Store Connect → 13" iPad: use `ipad-2064x2752/`
- Prefer `reference-listings/` when you want the exact art-directed frames
- Prefer numbered `01-08` when you want the regenerated deck from latest UI captures
""",
        encoding="utf-8",
    )
    print(f"\nDone → {OUT}")


if __name__ == "__main__":
    main()
