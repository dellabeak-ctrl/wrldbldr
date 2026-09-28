# World Builder

A browser-based workspace for playing **[The Story Engine: Deck of Worlds](https://thestoryengine.co/)** virtually — draw cards, arrange them on an infinite pannable/zoomable canvas, and save as many worlds as you want.


## Features

- **Six decks, numbered draw** — Region, Landmark, Namesake, Origin, Attribute, and Advent. Drawing a card removes it from that deck until you reshuffle.
- **Infinite canvas** — pan by dragging empty space, zoom with the scroll wheel or the +/− controls.
- **Right-click (or two-finger trackpad) drag** to reposition a card — left-click is reserved for canvas panning. Cards snap to a light grid when you release them.
- **Fixed visual hierarchy** — Region cards always render on top, then Landmark, Namesake, Origin, Attribute, with Advent on the bottom, regardless of draw order.
- **Rotate / remove** — hover any card to reveal small rotate (⟳) and remove (✕) buttons.
- **Region auras** — the background picks up color from any Region card(s) on the board, sampled from your own card photos.
- **Named workspaces** — save, load, rename, and delete multiple boards from the Workspaces panel, plus export/import as backup JSON files.
- **ⓘ How to Use** — an in-page modal with editable instructions, no external doc needed.

## Setup

1. Host `world-builder.html` anywhere static files can be served (this repo is set up for GitHub Pages).
2. Add your own card photos in six folders **next to** `world-builder.html` (no wrapping "cards" folder):
3. Name each photo `<singular-category>-<number>.jpg` (or `.png`), zero-padding numbers under 10:

   ```
   regions/region-01.jpg ... region-32.jpg
   landmarks/landmark-01.jpg ... landmark-48.jpg
   etc.
   ```

   A card with no matching photo just displays its number instead — nothing breaks.

## Keeping images a uniform size

`resize_cards.py` (Pillow-based) trims any bleed border, center-crops to a square, and resizes every photo in the six folders to the same dimensions.

It runs automatically via `.github/workflows/resize-cards.yml` whenever you push new images to any of the six folders — no local setup needed. You can also trigger it manually from the **Actions** tab on GitHub ("Resize card images" → "Run workflow"), with an optional **force** checkbox to reprocess every image (useful after changing crop/size settings in the script).

Key settings, near the top of `resize_cards.py`:

| Setting | Purpose |
|---|---|
| `TARGET_SIZE` | Output width/height in pixels (square) |
| `TRIM_PERCENT` | Fixed-margin trim applied before cropping, to strip inconsistent bleed/crop marks |
| `JPEG_QUALITY` | Compression quality for any `.jpg` sources (PNGs are kept lossless and are never converted) |

To run it locally instead:

```
pip install pillow --break-system-packages
python resize_cards.py /path/to/this/project
```

## Saving your progress

Workspaces are stored in the browser's `localStorage`, which is tied to that specific browser. Use **Workspaces → Export all to file** periodically to back up your saved worlds outside the browser, and **Import from file** to restore them (e.g. on a new device or after clearing browser data).

## Credits

Deck of Worlds is a product of The Story Engine. This tool is an unofficial fan project for personal use and reproduces none of the deck's copyrighted card text or artwork.
