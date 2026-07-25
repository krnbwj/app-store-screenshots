# Astronode App Store Screenshots

Store-ready listing images for **Astronode**, built with the [app-store-screenshots](https://github.com/ParthJadhav/app-store-screenshots) editor template plus a sophisticated export script.

## Final output (use these)

```text
final-output/
├── iphone-1320x2868/          ← App Store 6.9" iPhone  (exact 1320 × 2868)
│   ├── 01-…08-….png           generated marketing listings
│   ├── reference-listings/    your art-directed refs, resized exactly
│   └── originals-resized/     raw UI captures fitted to size
└── ipad-2064x2752/            ← App Store 13" iPad     (exact 2064 × 2752)
    ├── 01-…08-….png
    ├── reference-listings/
    └── originals-resized/
```

Local mirror: `/Users/karanbaweja/Documents/Dev/8/Astronode-Final-Output/`

## Directions of use

### 1. Upload to App Store Connect

1. Open your app → **App Store** → **Previews and Screenshots**
2. **iPhone 6.9"** → upload from `final-output/iphone-1320x2868/`
3. **13" iPad** → upload from `final-output/ipad-2064x2752/`
4. Prefer `reference-listings/` when you want the exact sophisticated frames you designed
5. Prefer numbered `01`–`08` for the regenerated deck from latest UI captures

### 2. Edit live in the screenshot editor

```bash
bun install
bun dev
# → http://localhost:3000
```

- Edit headlines / layouts in the inspector
- Click **Export bundle** for a full zip of Apple sizes
- Project state is saved in `app-store-screenshots.json`

### 3. Regenerate sophisticated PNGs

```bash
python3 scripts/generate_sophisticated_listings.py
```

This rebuilds `final-output/` using:

- **Didot / New York** gold serif headlines
- Nebula backgrounds sampled from your reference listings
- Soft device glow + starfield
- Exact **1320×2868** (iPhone) and **2064×2752** (iPad)

### 4. Source assets

```text
public/screenshots/sources/ui/     new UI captures
public/screenshots/sources/refs/   sophisticated reference listings
public/screenshots/apple/iphone/en/ legacy captures (fallback)
```

## Design notes

- Screenshots are **ads**, not documentation — one outcome per slide
- Headlines use premium serif + metallic gold against deep purple/gold nebulae
- iPad exports keep a tablet frame on the same celestial canvas so both sizes feel like one brand system

## License / credit

Editor template from [ParthJadhav/app-store-screenshots](https://github.com/ParthJadhav/app-store-screenshots) (MIT).
