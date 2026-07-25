#!/usr/bin/env python3
"""
Astronode production App Store listing generator (clean backgrounds).

- Pure procedural nebula (no reference-phone ghosting)
- Crisp Didot gold headlines (single layer)
- Exact 1320×2868 (iPhone 6.9") and 2064×2752 (iPad 13")
- Writes ASO metadata alongside exports
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC_UI = ROOT / "public" / "screenshots" / "sources" / "ui"
SRC_REF = ROOT / "public" / "screenshots" / "sources" / "refs"
LEGACY = ROOT / "public" / "screenshots" / "apple" / "iphone" / "en"
MOCKUP = ROOT / "public" / "mockup.png"
OUT = ROOT / "final-output"

IPHONE = (1320, 2868)
IPAD = (2064, 2752)

MK_L, MK_T, MK_W, MK_H = 52 / 1022, 46 / 2082, 918 / 1022, 1990 / 2082

DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
BODONI = "/System/Library/Fonts/Supplemental/Bodoni 72.ttc"
NEWYORK = "/System/Library/Fonts/NewYork.ttf"
GEORGIA = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"

GOLD = (232, 196, 110)

# ASO-optimized slide copy: benefit-first, searchable themes, short thumbnail lines
SLIDES = [
    {
        "id": "01-daily-horoscope-rituals",
        "headline": "Daily Horoscope\n& Rituals",
        "keyword_focus": "daily horoscope, rituals, meditation",
        "ui": "01-home.png",
        "legacy": "01-home.png",
        "palette": 0,
    },
    {
        "id": "02-love-compatibility",
        "headline": "Love &\nCompatibility",
        "keyword_focus": "love compatibility, relationships, astrology match",
        "ui": None,
        "legacy": "05-relationships.png",
        "palette": 1,
    },
    {
        "id": "03-ai-astrology-oracle",
        "headline": "AI Astrology\nOracle",
        "keyword_focus": "AI astrology, oracle, birth chart chat",
        "ui": None,
        "legacy": "07-oracle.png",
        "palette": 2,
    },
    {
        "id": "04-cosmic-journal",
        "headline": "Cosmic Journal\nin Seconds",
        "keyword_focus": "astrology journal, voice notes, reflection",
        "ui": None,
        "legacy": "08-quick-actions.png",
        "palette": 3,
    },
    {
        "id": "05-personal-cosmic-guide",
        "headline": "Your Personal\nCosmic Guide",
        "keyword_focus": "personal astrology, daily guidance, zodiac",
        "ui": "01-home.png",
        "legacy": "01-home.png",
        "palette": 4,
    },
    {
        "id": "06-astrology-insights-feed",
        "headline": "Astrology\nInsights Feed",
        "keyword_focus": "astrology news, vedic, western, tarot",
        "ui": "02-explore.png",
        "legacy": "02-explore.png",
        "palette": 5,
    },
    {
        "id": "07-birth-chart-overview",
        "headline": "Birth Chart\nOverview",
        "keyword_focus": "birth chart, vedic astrology, numerology",
        "ui": "03-overview.png",
        "legacy": "04-overview.png",
        "palette": 6,
    },
    {
        "id": "08-cosmic-profile-karma",
        "headline": "Track Your\nCosmic Karma",
        "keyword_focus": "karma, manifestations, astrology profile",
        "ui": "04-profile.png",
        "legacy": "04-overview.png",
        "palette": 7,
    },
]

PALETTES = [
    # (deep, mid_purple, gold_dust, magenta)
    ((8, 4, 20), (90, 40, 150), (210, 160, 80), (160, 70, 140)),
    ((6, 3, 18), (110, 45, 160), (220, 170, 90), (180, 60, 130)),
    ((10, 5, 24), (70, 30, 130), (200, 150, 70), (140, 50, 150)),
    ((5, 2, 16), (100, 50, 170), (230, 180, 100), (170, 80, 150)),
    ((8, 4, 22), (85, 35, 145), (215, 165, 85), (155, 65, 135)),
    ((7, 3, 19), (95, 42, 155), (205, 155, 75), (165, 75, 145)),
    ((9, 4, 21), (80, 38, 140), (225, 175, 95), (150, 55, 140)),
    ((6, 3, 17), (105, 48, 165), (218, 168, 88), (175, 70, 138)),
]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path, index in [(DIDOT, 0), (DIDOT, 1), (BODONI, 0), (NEWYORK, 0), (GEORGIA, 0)]:
        try:
            return ImageFont.truetype(path, size=size, index=index)
        except Exception:
            continue
    return ImageFont.load_default()


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
    raise FileNotFoundError(f"No UI for slide {slide['id']}")


def clean_nebula(size: tuple[int, int], seed: int, palette_idx: int) -> Image.Image:
    """Pure procedural cosmic background — zero device silhouettes."""
    w, h = size
    rng = random.Random(seed)
    deep, mid, gold, mag = PALETTES[palette_idx % len(PALETTES)]

    img = Image.new("RGB", (w, h), deep)
    px = img.load()
    for y in range(h):
        t = y / h
        wave = 0.5 + 0.5 * math.sin(t * 2.8 + seed * 0.01)
        r = int(deep[0] + (mid[0] - deep[0]) * t * 0.55 + gold[0] * 0.04 * wave)
        g = int(deep[1] + (mid[1] - deep[1]) * t * 0.35)
        b = int(deep[2] + (mid[2] - deep[2]) * (0.45 + 0.4 * wave))
        row = (min(255, r), min(255, g), min(255, b))
        for x in range(w):
            px[x, y] = row

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Organic nebula clouds — ellipses only, never rectangles/device shapes
    for _ in range(22):
        cx = rng.randint(-w // 5, w + w // 5)
        cy = rng.randint(0, h)
        rx = rng.randint(int(w * 0.18), int(w * 0.55))
        ry = rng.randint(int(h * 0.08), int(h * 0.22))
        color = rng.choice(
            [
                (*mid, 50),
                (*mag, 42),
                (*gold, 28),
                (mid[0] // 2, mid[1] // 2, mid[2], 55),
                (40, 20, 80, 60),
            ]
        )
        od.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=color)
    overlay = overlay.filter(ImageFilter.GaussianBlur(max(40, int(min(w, h) * 0.055))))
    canvas = Image.alpha_composite(img.convert("RGBA"), overlay)

    # Extra gold dust ribbon near top (editorial feel, still abstract)
    ribbon = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ribbon)
    for _ in range(6):
        cx = rng.randint(0, w)
        cy = rng.randint(int(h * 0.05), int(h * 0.45))
        r = rng.randint(int(w * 0.1), int(w * 0.35))
        rd.ellipse((cx - r, cy - r // 2, cx + r, cy + r // 2), fill=(*gold, 22))
    canvas = Image.alpha_composite(canvas, ribbon.filter(ImageFilter.GaussianBlur(55)))

    # Stars — points only
    stars = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars)
    n = int(520 * (w * h) / (1320 * 2868))
    for _ in range(n):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        b = rng.randint(180, 255)
        s = 1 if rng.random() < 0.88 else 2
        sd.ellipse((x, y, x + s, y + s), fill=(b, b, min(255, b + 25), 220))
    for _ in range(16):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, int(h * 0.5))
        r = rng.randint(2, 3)
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(255, 236, 190, 140))
    canvas = Image.alpha_composite(canvas, stars)

    # Soft edge vignette (no hard shapes)
    vig = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for i in range(90):
        vd.rectangle((i, i, w - 1 - i, h - 1 - i), outline=(0, 0, 0, int(i * 1.2)))
    canvas = Image.alpha_composite(canvas, vig.filter(ImageFilter.GaussianBlur(45)))
    return canvas.convert("RGBA")


def draw_crisp_headline(canvas: Image.Image, text: str, size: tuple[int, int]) -> None:
    """Single-layer Didot headline — no blur bloom that reads as double text."""
    w, h = size
    font_size = int(86 * (w / 1320))
    font = load_font(font_size)
    lines = text.split("\n")
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))

    widths, heights = [], []
    for line in lines:
        bbox = probe.textbbox((0, 0), line, font=font)
        widths.append(bbox[2] - bbox[0])
        heights.append(bbox[3] - bbox[1])
    gap = int(12 * (w / 1320))
    y = int(h * 0.048)

    draw = ImageDraw.Draw(canvas)
    for i, line in enumerate(lines):
        x = (w - widths[i]) // 2
        # Tiny dark shadow for legibility only (1px, not a second glyph)
        draw.text((x + 1, y + 2), line, font=font, fill=(0, 0, 0, 120))
        draw.text((x, y), line, font=font, fill=GOLD)
        y += heights[i] + gap


def compose_iphone(screenshot_path: Path, phone_h: int) -> Image.Image:
    """Clean iPhone frame — no mockup.png halo/glow ghosting."""
    # Match mockup aspect (~1022/2082)
    phone_w = int(phone_h * (1022 / 2082))
    bezel = max(10, int(phone_w * 0.028))
    radius = int(phone_w * 0.12)

    shot = fit_cover(
        Image.open(screenshot_path).convert("RGB"),
        phone_w - bezel * 2,
        phone_h - bezel * 2,
    )

    frame = Image.new("RGBA", (phone_w, phone_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # Outer titanium (hard edge only — no soft halo)
    fd.rounded_rectangle(
        (0, 0, phone_w - 1, phone_h - 1),
        radius=radius,
        fill=(38, 34, 30, 255),
    )
    # 1px gold rim (drawn as inset fill ring, not thick outline glow)
    fd.rounded_rectangle(
        (2, 2, phone_w - 3, phone_h - 3),
        radius=max(4, radius - 2),
        outline=(210, 180, 110, 255),
        width=2,
    )
    # Inner black inset
    inner_r = max(10, radius - bezel)
    fd.rounded_rectangle(
        (bezel - 1, bezel - 1, phone_w - bezel, phone_h - bezel),
        radius=inner_r,
        fill=(0, 0, 0, 255),
    )

    screen_mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(screen_mask).rounded_rectangle(
        (0, 0, shot.width - 1, shot.height - 1),
        radius=max(8, inner_r - 4),
        fill=255,
    )
    frame.paste(shot.convert("RGBA"), (bezel, bezel), screen_mask)

    # Dynamic Island
    island_w = int(phone_w * 0.28)
    island_h = max(18, int(phone_h * 0.018))
    ix = (phone_w - island_w) // 2
    iy = bezel + max(8, int(phone_h * 0.012))
    fd.rounded_rectangle(
        (ix, iy, ix + island_w, iy + island_h),
        radius=island_h // 2,
        fill=(5, 5, 5, 255),
    )
    return frame


def compose_ipad_frame(screenshot_path: Path, frame_h: int) -> Image.Image:
    frame_w = int(frame_h * 0.75)
    bezel = max(18, int(frame_w * 0.028))
    radius = int(frame_w * 0.045)
    shot = fit_cover(Image.open(screenshot_path).convert("RGB"), frame_w - bezel * 2, frame_h - bezel * 2)

    frame = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle((0, 0, frame_w - 1, frame_h - 1), radius=radius, fill=(28, 28, 30, 255))
    fd.rounded_rectangle(
        (1, 1, frame_w - 2, frame_h - 2),
        radius=radius - 1,
        outline=(160, 140, 90, 220),
        width=2,
    )
    inner_r = max(8, radius - 6)
    fd.rounded_rectangle(
        (bezel - 2, bezel - 2, frame_w - bezel + 1, frame_h - bezel + 1),
        radius=inner_r,
        fill=(0, 0, 0, 255),
    )
    screen_mask = Image.new("L", shot.size, 0)
    ImageDraw.Draw(screen_mask).rounded_rectangle(
        (0, 0, shot.width - 1, shot.height - 1), radius=max(6, inner_r - 4), fill=255
    )
    frame.paste(shot.convert("RGBA"), (bezel, bezel), screen_mask)
    cam_x, cam_y = frame_w // 2, max(6, bezel // 2)
    fd.ellipse((cam_x - 4, cam_y - 4, cam_x + 4, cam_y + 4), fill=(10, 10, 12, 255))
    return frame


def add_soft_glow(canvas: Image.Image, device: Image.Image, x: int, y: int) -> None:
    """Place device with no backdrop glow (avoids any second-frame illusion)."""
    canvas.alpha_composite(device, (x, y))


def make_listing(slide: dict, size: tuple[int, int], device: str) -> Image.Image:
    w, h = size
    seed = sum(ord(c) for c in slide["id"]) + w * 3
    bg = clean_nebula(size, seed=seed, palette_idx=slide["palette"])
    draw_crisp_headline(bg, slide["headline"], size)

    ui_path = resolve_ui(slide)
    if device == "iphone":
        device_img = compose_iphone(ui_path, phone_h=int(h * 0.70))
        x = (w - device_img.width) // 2
        y = h - device_img.height - int(h * 0.018)
    else:
        device_img = compose_ipad_frame(ui_path, frame_h=int(h * 0.72))
        x = (w - device_img.width) // 2
        y = h - device_img.height - int(h * 0.03)

    add_soft_glow(bg, device_img, x, y)
    out = bg.convert("RGB")
    out = ImageEnhance.Contrast(out).enhance(1.03)
    out = ImageEnhance.Color(out).enhance(1.05)
    return out


def upscale_reference(ref_name: str, size: tuple[int, int], dest: Path) -> None:
    img = fit_cover(Image.open(SRC_REF / ref_name).convert("RGB"), *size)
    img = ImageEnhance.Sharpness(img).enhance(1.1)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "PNG", optimize=True)


def save_resized_originals(size: tuple[int, int], dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(SRC_UI.glob("*.png")):
        fit_cover(Image.open(p).convert("RGB"), *size).save(dest_dir / p.name, "PNG", optimize=True)


def write_aso_metadata(out_dir: Path) -> None:
    """App Store Optimization copy ready to paste into App Store Connect."""
    # Apple keyword field max 100 characters, comma-separated, no spaces after commas ideal
    keywords = (
        "astrology,horoscope,birth chart,zodiac,vedic,tarot,numerology,"
        "compatibility,oracle,meditation,rituals,journal"
    )
    # Trim to <= 100 chars
    while len(keywords) > 100:
        keywords = keywords.rsplit(",", 1)[0]

    aso = {
        "app_name": "Astronode",
        "subtitle": "Astrology, Horoscope & Rituals",  # max 30 chars
        "promotional_text": (
            "Your personal cosmic guide — daily horoscopes, birth chart insights, "
            "love compatibility, AI oracle, and sacred rituals in one elegant app."
        ),
        "description": (
            "Astronode is your personal cosmos companion.\n\n"
            "Get daily horoscopes and rituals tailored to you. Explore Vedic and Western "
            "astrology, decode relationship compatibility, ask the AI Oracle about your chart "
            "and timing, and capture reflections in your cosmic journal.\n\n"
            "FEATURES\n"
            "• Daily horoscope & meditation rituals\n"
            "• Birth chart overview across traditions\n"
            "• Love & relationship compatibility scores\n"
            "• AI Astrology Oracle chat\n"
            "• Astral feed — articles on astrology, tarot & crystals\n"
            "• Cosmic journal, voice notes & manifestations\n"
            "• Power Moves — planetary timing for success\n\n"
            "Whether you follow Vedic, Western, Chinese astrology, or numerology, "
            "Astronode brings your chart into focus with a calm, premium experience.\n\n"
            "Symbolic guidance only — not medical, legal, or financial advice."
        ),
        "keywords": keywords,
        "keywords_character_count": len(keywords),
        "keyword_field_limit": 100,
        "primary_category": "Lifestyle",
        "secondary_category": "Health & Fitness",
        "whats_new": (
            "Refined cosmic experience with daily rituals, relationship insights, "
            "AI Oracle guidance, and a clearer birth-chart overview."
        ),
        "screenshot_order_aso": [
            {
                "file": s["id"] + ".png",
                "headline": s["headline"].replace("\n", " "),
                "keyword_focus": s["keyword_focus"],
                "why": "Maps to high-intent astrology search themes visible at thumbnail size.",
            }
            for s in SLIDES
        ],
        "sizes": {
            "iphone_6_9": {"folder": "iphone-1320x2868", "pixels": "1320x2868"},
            "ipad_13": {"folder": "ipad-2064x2752", "pixels": "2064x2752"},
        },
        "upload_notes": [
            "Use numbered 01–08 PNGs as primary App Store screenshots (clean production set).",
            "reference-listings/ are art references only — may contain prior design artifacts.",
            "Paste subtitle + keywords + description into App Store Connect localization.",
            "Keep first screenshot benefit-led (daily horoscope) — it is the search thumbnail.",
        ],
    }

    (out_dir / "ASO-metadata.json").write_text(json.dumps(aso, indent=2) + "\n", encoding="utf-8")
    md = f"""# Astronode — ASO Metadata (paste into App Store Connect)

## Subtitle (30 characters max)
```
{aso['subtitle']}
```
({len(aso['subtitle'])} chars)

## Keywords (100 characters max)
```
{aso['keywords']}
```
({aso['keywords_character_count']} chars)

## Promotional Text
{aso['promotional_text']}

## Description
{aso['description']}

## What's New
{aso['whats_new']}

## Categories
- Primary: {aso['primary_category']}
- Secondary: {aso['secondary_category']}

## Screenshot order (ASO)

| # | File | On-image headline | Keyword focus |
|---|------|-------------------|---------------|
"""
    for i, row in enumerate(aso["screenshot_order_aso"], 1):
        md += f"| {i} | `{row['file']}` | {row['headline']} | {row['keyword_focus']} |\n"

    md += """
## Upload

1. **iPhone 6.9"** → `iphone-1320x2868/01-…08-….png`
2. **13" iPad** → `ipad-2064x2752/01-…08-….png`
3. Do **not** use `reference-listings/` for production unless you intentionally want those frames
"""
    (out_dir / "ASO-metadata.md").write_text(md, encoding="utf-8")


def main() -> None:
    iphone_dir = OUT / "iphone-1320x2868"
    ipad_dir = OUT / "ipad-2064x2752"
    refs_iphone = iphone_dir / "reference-listings"
    refs_ipad = ipad_dir / "reference-listings"
    for d in (iphone_dir, ipad_dir, refs_iphone, refs_ipad):
        d.mkdir(parents=True, exist_ok=True)

    # Keep refs as separate non-production copies
    ref_files = [
        ("01-empower-rituals.png", "ref-01-empower-your-daily-rituals.png"),
        ("02-decode-relationships.png", "ref-02-decode-your-relationships.png"),
        ("03-consult-oracle.png", "ref-03-consult-the-oracle.png"),
        ("04-capture-thoughts.png", "ref-04-capture-your-thoughts.png"),
        ("05-cosmic-daily-guide.png", "ref-05-your-cosmic-daily-guide.png"),
    ]
    for src, name in ref_files:
        if (SRC_REF / src).exists():
            upscale_reference(src, IPHONE, refs_iphone / name)
            upscale_reference(src, IPAD, refs_ipad / name)
            print(f"ref archived {name}")

    # Remove old ghosted production filenames if present
    for folder in (iphone_dir, ipad_dir):
        for old in folder.glob("0*.png"):
            old.unlink()

    for slide in SLIDES:
        iphone = make_listing(slide, IPHONE, "iphone")
        ipad = make_listing(slide, IPAD, "ipad")
        assert iphone.size == IPHONE and ipad.size == IPAD
        iphone.save(iphone_dir / f"{slide['id']}.png", "PNG", optimize=True)
        ipad.save(ipad_dir / f"{slide['id']}.png", "PNG", optimize=True)
        print(f"clean listing ok {slide['id']}")

    save_resized_originals(IPHONE, iphone_dir / "originals-resized")
    save_resized_originals(IPAD, ipad_dir / "originals-resized")
    write_aso_metadata(OUT)

    (OUT / "README.md").write_text(
        """# Astronode Final Output — Production

Clean listing images: **no ghost devices**, crisp Didot headlines, ASO-ready copy.

| Device | Folder | Size |
|--------|--------|------|
| iPhone 6.9" | `iphone-1320x2868/` | 1320 × 2868 |
| iPad 13" | `ipad-2064x2752/` | 2064 × 2752 |

**Production uploads:** numbered `01-…08-….png` only.  
**ASO:** see `ASO-metadata.md` / `ASO-metadata.json`.  
**References only:** `reference-listings/` (not for production if they show prior art).

```bash
python3 scripts/generate_sophisticated_listings.py
```
""",
        encoding="utf-8",
    )
    print(f"\nDone → {OUT}")


if __name__ == "__main__":
    main()
