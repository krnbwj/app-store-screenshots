# Astronode App Store Screenshots

Editable Next.js screenshot deck for **Astronode**, scaffolded from [app-store-screenshots](https://github.com/ParthJadhav/app-store-screenshots).

## Quick start

```bash
cd astronode
bun install
bun dev
```

Open http://localhost:3000 — edit headlines/layouts in the inspector, then click **Export bundle**.

Primary export size for iPhone 6.9": **1320 × 2868**.

## Generated assets

Ready-to-upload PNGs live in:

```text
exports/iphone-1320x2868/
```

- `ref-01-*.png` / `ref-02-*.png` — your two reference listing images, resized exactly to 1320×2868
- `01-*.png` … `08-*.png` — marketing listing images built from every original simulator screenshot
- `originals-resized/` — UI-only originals stretched to the same App Store size

Regenerate with:

```bash
python3 scripts/generate_listing_images.py
```

## Source screenshots

```text
public/screenshots/apple/iphone/en/   # 8 original captures
public/screenshots/references/        # 2 listing style references
```
