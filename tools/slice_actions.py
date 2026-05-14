"""Slice the action sprite sheet into individual frames.

Uses the image's own alpha channel to find sprites — no background
removal heuristics needed. Each connected opaque region = one sprite.
"""

from PIL import Image, ImageOps
import numpy as np
from scipy import ndimage
import os

SHEET = os.path.expanduser("~/Downloads/ChatGPT Image Apr 30, 2026, 10_57_40 PM.png")
ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets", "template")
TARGET_W, TARGET_H = 174, 128

# Row boundaries (from density analysis)
ROWS = [
    ("walk",      30, 220),
    ("stalk",    235, 430),
    ("chase",    440, 640),
    ("trash_can", 700, 840),
]

MIN_SPRITE_PIXELS = 5000


def get_feet_baseline(img_rgba):
    arr = np.array(img_rgba)
    mask = arr[:, :, 3] > 128
    if not mask.any():
        return img_rgba.height
    rows = np.any(mask, axis=1)
    return np.where(rows)[0][-1] + 1


def fill_interior(arr):
    """Fill interior transparent regions enclosed by opaque pixels."""
    alpha = arr[:, :, 3]
    transparent_mask = alpha < 128

    labeled, num_features = ndimage.label(transparent_mask)

    h, w = labeled.shape
    edge_labels = set()
    edge_labels.update(labeled[0, :].flat)
    edge_labels.update(labeled[h-1, :].flat)
    edge_labels.update(labeled[:, 0].flat)
    edge_labels.update(labeled[:, w-1].flat)
    edge_labels.discard(0)

    for label_id in range(1, num_features + 1):
        if label_id not in edge_labels:
            region = labeled == label_id
            if region.sum() > 3:
                arr[region] = [230, 230, 230, 255]
    return arr


def normalize_frame(sprite_region):
    """Convert a cropped sprite region into a standardized frame."""
    arr = np.array(sprite_region).copy()

    # Fill interior transparent holes (e.g., inside body outline)
    arr = fill_interior(arr)

    frame = Image.fromarray(arr)

    # Find content bounds
    alpha = arr[:, :, 3]
    mask = alpha > 128
    if not mask.any():
        return Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))

    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    cropped = frame.crop((cmin, rmin, cmax + 1, rmax + 1))

    cw, ch = cropped.size
    scale = min(TARGET_W / cw, TARGET_H / ch) * 0.85
    new_w = max(1, int(cw * scale))
    new_h = max(1, int(ch * scale))
    scaled = cropped.resize((new_w, new_h), Image.LANCZOS)

    # Convert to grayscale preserving alpha
    r, g, b, a = scaled.split()
    gray = ImageOps.grayscale(scaled.convert("RGB"))
    scaled = Image.merge("RGBA", (gray, gray, gray, a))

    feet_y = get_feet_baseline(scaled)

    canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    target_baseline = int(TARGET_H * 0.95)
    paste_x = (TARGET_W - new_w) // 2
    paste_y = target_baseline - feet_y
    canvas.paste(scaled, (paste_x, paste_y), scaled)

    return canvas


def find_sprites_in_row(sheet, y0, y1):
    """Find individual sprites in a row using alpha-based blob detection."""
    arr = np.array(sheet)
    row_alpha = arr[y0:y1, :, 3]
    opaque = row_alpha > 128

    labeled, num = ndimage.label(opaque)

    sprites = []
    for lid in range(1, num + 1):
        region = labeled == lid
        count = region.sum()
        if count < MIN_SPRITE_PIXELS:
            continue
        cols = np.where(region.any(axis=0))[0]
        x0, x1 = cols[0], cols[-1] + 1
        sprites.append((x0, x1))

    sprites.sort(key=lambda s: s[0])

    # Extract each sprite as a crop from the original sheet
    frames = []
    for x0, x1 in sprites:
        cell = sheet.crop((x0, y0, x1, y1))
        frames.append(cell)

    return frames


def main():
    sheet = Image.open(SHEET).convert("RGBA")

    for anim_name, y0, y1 in ROWS:
        out_dir = os.path.join(ASSETS, anim_name)
        os.makedirs(out_dir, exist_ok=True)

        for f in os.listdir(out_dir):
            if f.endswith(".png"):
                os.remove(os.path.join(out_dir, f))

        frames = find_sprites_in_row(sheet, y0, y1)
        print(f"{anim_name}: {len(frames)} frames")

        for i, frame in enumerate(frames):
            out = normalize_frame(frame)
            path = os.path.join(out_dir, f"{anim_name}_{i:02d}.png")
            out.save(path)
            print(f"  {path}")


if __name__ == "__main__":
    main()
