# Astronode Final Output (Sophisticated)

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
