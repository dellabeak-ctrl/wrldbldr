#!/usr/bin/env python3
"""
Resize and crop every Deck of Worlds card image to one uniform square size,
saved as lossless PNG so no image quality is lost to compression.

Setup (one time):
    pip install pillow --break-system-packages

Usage:
    python resize_cards.py /path/to/your/project [--force]

Point it at the folder that directly contains index.html and the
six category folders (regions, landmarks, namesakes, origins, attributes,
advents). It processes every image found in those folders, in place:

  1. Corrects orientation (some phone photos store rotation as metadata
     instead of actually rotating the pixels).
  2. Trims TRIM_PERCENT off every edge, then center-crops to a square,
     exactly like the site's on-screen display does.
  3. Resizes every image to the exact same TARGET_SIZE x TARGET_SIZE
     pixels (high-quality Lanczos filter), so all cards match.
  4. Saves it as a .png. If the original was a .jpg/.jpeg, the old file is
     deleted so the folder only ever holds region-7.png.

Every processed file is tagged inside its PNG metadata, and tagged files
are skipped on later runs. That matters because step 2 trims the edges:
without the tag, each run (e.g. in CI on every push) would shave another
TRIM_PERCENT off every card. --force ignores the tag and reprocesses
everything, trimming again — only use it on fresh originals.
"""

import os
import sys

try:
    from PIL import Image, ImageOps
    from PIL.PngImagePlugin import PngInfo
except ImportError:
    print("Pillow isn't installed. Run: pip install pillow --break-system-packages")
    sys.exit(1)

CATEGORIES = ["regions", "landmarks", "namesakes", "origins", "attributes", "advents"]
TARGET_SIZE = 600          # pixels, square — edit this if you want bigger/smaller
VALID_EXT = (".png", ".jpg", ".jpeg")

# Some source exports have a thin bleed/crop-mark border baked in around
# the actual card art; others don't. Trimming a small fixed percentage off
# every edge before cropping removes that border consistently wherever it
# exists, without meaningfully affecting images that never had one.
# Raise this (e.g. 0.05) if marks are still visible after processing;
# lower it (e.g. 0.01) if it looks like it's cutting into real content.
TRIM_PERCENT = 0.03


PROCESSED_TAG = "resize_cards"   # PNG text key marking a finished card


def already_processed(path):
    """Skip PNGs this script already produced, so re-running it never
    re-trims or re-resamples the same image."""
    if not path.lower().endswith(".png"):
        return False
    try:
        with Image.open(path) as img:
            return PROCESSED_TAG in getattr(img, "text", {})
    except Exception:
        return False


def process_image(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # respect phone photo rotation metadata
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGBA")

    # Trim a small fixed margin off every edge first, to strip out any
    # bleed border / crop marks some source images have baked in.
    w, h = img.size
    trim_w = int(w * TRIM_PERCENT)
    trim_h = int(h * TRIM_PERCENT)
    if trim_w > 0 or trim_h > 0:
        img = img.crop((trim_w, trim_h, w - trim_w, h - trim_h))

    # Center-crop to a square (matches the site's object-fit: cover look)
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)

    base, ext = os.path.splitext(path)
    new_path = base + ".png"
    meta = PngInfo()
    meta.add_text(PROCESSED_TAG, f"{TARGET_SIZE}px, trim {TRIM_PERCENT}")
    img.save(new_path, "PNG", optimize=True, pnginfo=meta)

    if new_path != path and os.path.exists(path):
        os.remove(path)

    return new_path


def main():
    if len(sys.argv) < 2:
        print("Usage: python resize_cards.py /path/to/project [--force]")
        sys.exit(1)

    root = sys.argv[1]
    force = "--force" in sys.argv[2:]
    if force:
        print("--force: reprocessing every image, including ones already processed.\n")

    total = 0
    for category in CATEGORIES:
        folder = os.path.join(root, category)
        if not os.path.isdir(folder):
            print(f"Skipping missing folder: {folder}")
            continue
        for filename in sorted(os.listdir(folder)):
            if not filename.lower().endswith(VALID_EXT):
                continue
            full_path = os.path.join(folder, filename)
            if not force and already_processed(full_path):
                continue
            try:
                new_path = process_image(full_path)
                print(f"  {filename} -> {os.path.basename(new_path)} ({TARGET_SIZE}x{TARGET_SIZE})")
                total += 1
            except Exception as e:
                print(f"  FAILED on {filename}: {e}")

    print(f"\nDone. Processed {total} images to {TARGET_SIZE}x{TARGET_SIZE}px PNGs.")


if __name__ == "__main__":
    main()