#!/usr/bin/env python3
"""
Resize and crop every Deck of Worlds card image to one uniform square size,
and re-save them as compressed JPEGs so world-builder.html loads and drags
smoothly.

Setup (one time):
    pip install pillow --break-system-packages

Usage:
    python resize_cards.py /path/to/your/project

Point it at the folder that directly contains world-builder.html and the
six category folders (regions, landmarks, namesakes, origins, attributes,
advents). It processes every image found in those folders, in place:

  1. Corrects orientation (some phone photos store rotation as metadata
     instead of actually rotating the pixels).
  2. Center-crops it to a square, exactly like the site's on-screen
     display does, so what you see while resizing matches what the site
     shows.
  3. Resizes every image to the exact same TARGET_SIZE x TARGET_SIZE
     pixels, guaranteeing all cards are identical dimensions.
  4. Saves it as an optimized .jpg (much smaller than .png for photos).
     If the original was a .png, the old file is deleted so you don't
     end up with duplicate region-7.png AND region-7.jpg confusing the
     site (it looks for .jpg first, then falls back to .png).

Nothing else needs to change in world-builder.html — it already expects
.jpg files first.
"""

import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    print("Pillow isn't installed. Run: pip install pillow --break-system-packages")
    sys.exit(1)

CATEGORIES = ["regions", "landmarks", "namesakes", "origins", "attributes", "advents"]
TARGET_SIZE = 600          # pixels, square — edit this if you want bigger/smaller
JPEG_QUALITY = 82          # 1-95, higher = better quality & bigger file
VALID_EXT = (".png", ".jpg", ".jpeg")


def already_processed(path):
    """Skip files that are already a correctly-sized .jpg, so re-running
    this (e.g. in CI on every push) doesn't keep re-compressing the same
    image over and over and slowly degrading its quality."""
    if not path.lower().endswith(".jpg"):
        return False
    try:
        with Image.open(path) as img:
            return img.size == (TARGET_SIZE, TARGET_SIZE)
    except Exception:
        return False


def process_image(path):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # respect phone photo rotation metadata
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Center-crop to a square (matches the site's object-fit: cover look)
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)

    base, ext = os.path.splitext(path)
    new_path = base + ".jpg"
    img.save(new_path, "JPEG", quality=JPEG_QUALITY, optimize=True)

    if new_path != path and os.path.exists(path):
        os.remove(path)

    return new_path


def main():
    if len(sys.argv) != 2:
        print("Usage: python resize_cards.py /path/to/project")
        sys.exit(1)

    root = sys.argv[1]
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
            if already_processed(full_path):
                continue
            try:
                new_path = process_image(full_path)
                print(f"  {filename} -> {os.path.basename(new_path)} ({TARGET_SIZE}x{TARGET_SIZE})")
                total += 1
            except Exception as e:
                print(f"  FAILED on {filename}: {e}")

    print(f"\nDone. Processed {total} images to {TARGET_SIZE}x{TARGET_SIZE}px JPEGs.")


if __name__ == "__main__":
    main()
