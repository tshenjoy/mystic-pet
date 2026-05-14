"""Slice the sit-transition sprite sheet into individual frames."""

from PIL import Image, ImageOps, ImageDraw
import numpy as np
from scipy import ndimage
import os

SHEET = os.path.expanduser("~/Downloads/ChatGPT Image Apr 30, 2026, 10_29_19 PM.png")
ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets", "template")
TARGET_W, TARGET_H = 174, 128

# Reference walk frame for baseline alignment
WALK_REF = os.path.join(ASSETS, "walk", "walk_00.png")


def find_sprite_bounds(img_rgba):
    """Find bounding box of non-background pixels."""
    arr = np.array(img_rgba)
    # Consider pixels that are not near-white and not fully transparent
    alpha = arr[:, :, 3]
    rgb = arr[:, :, :3]
    brightness = rgb.mean(axis=2)
    mask = (alpha > 128) & (brightness < 240)
    if not mask.any():
        mask = alpha > 128
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    if not rows.any():
        return None
    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]
    return cmin, rmin, cmax + 1, rmax + 1


def get_feet_baseline(img_rgba):
    """Find Y position of lowest non-transparent pixel (feet)."""
    arr = np.array(img_rgba)
    alpha = arr[:, :, 3]
    rgb = arr[:, :, :3]
    brightness = rgb.mean(axis=2)
    mask = (alpha > 128) & (brightness < 240)
    if not mask.any():
        return img_rgba.height
    rows = np.any(mask, axis=1)
    return np.where(rows)[0][-1] + 1


def extract_frames(sheet_path):
    """Split 2x3 sheet into 6 individual sprites."""
    sheet = Image.open(sheet_path).convert("RGBA")
    w, h = sheet.size
    cell_w, cell_h = w // 3, h // 2

    frames = []
    for row in range(2):
        for col in range(3):
            x0 = col * cell_w
            y0 = row * cell_h
            cell = sheet.crop((x0, y0, x0 + cell_w, y0 + cell_h))
            frames.append(cell)
    return frames


def normalize_frame(frame, ref_baseline_ratio):
    """Normalize frame: remove background, convert to grayscale, fit to 174x128."""
    arr = np.array(frame)

    # Find transparent pixels and classify as interior vs exterior.
    # Interior transparent pixels (enclosed by opaque outline) get filled white.
    alpha = arr[:, :, 3]
    transparent_mask = alpha < 128

    # Label connected transparent regions
    labeled, num_features = ndimage.label(transparent_mask)

    # Regions touching any edge = exterior background
    h, w = labeled.shape
    edge_labels = set()
    edge_labels.update(labeled[0, :].flat)
    edge_labels.update(labeled[h-1, :].flat)
    edge_labels.update(labeled[:, 0].flat)
    edge_labels.update(labeled[:, w-1].flat)
    edge_labels.discard(0)

    # Interior = transparent regions NOT touching edges → fill with white
    for label_id in range(1, num_features + 1):
        if label_id not in edge_labels:
            region = labeled == label_id
            arr[region] = [255, 255, 255, 255]

    frame = Image.fromarray(arr)

    bounds = find_sprite_bounds(frame)
    if bounds is None:
        return Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))

    # Crop to content
    cropped = frame.crop(bounds)

    # Scale to fit within target, preserving aspect ratio
    cw, ch = cropped.size
    scale = min(TARGET_W / cw, TARGET_H / ch) * 0.85  # leave margin
    new_w = int(cw * scale)
    new_h = int(ch * scale)
    scaled = cropped.resize((new_w, new_h), Image.LANCZOS)

    # Convert to grayscale while preserving alpha
    r, g, b, a = scaled.split()
    gray = ImageOps.grayscale(scaled.convert("RGB"))
    scaled = Image.merge("RGBA", (gray, gray, gray, a))

    # Find feet baseline in scaled sprite
    feet_y = get_feet_baseline(scaled)

    # Place on target canvas, aligning feet to reference baseline
    canvas = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    target_baseline = int(TARGET_H * ref_baseline_ratio)
    paste_x = (TARGET_W - new_w) // 2
    paste_y = target_baseline - feet_y
    canvas.paste(scaled, (paste_x, paste_y), scaled)

    return canvas


def get_ref_baseline_ratio():
    """Get feet baseline ratio from reference walk frame."""
    if os.path.exists(WALK_REF):
        ref = Image.open(WALK_REF).convert("RGBA")
        baseline = get_feet_baseline(ref)
        return baseline / ref.height
    return 0.9  # default


def main():
    frames = extract_frames(SHEET)
    ref_ratio = get_ref_baseline_ratio()
    print(f"Reference baseline ratio: {ref_ratio:.3f}")

    # Top row (0-2): walk_to_idle transition
    walk_to_idle_dir = os.path.join(ASSETS, "walk_to_idle")
    os.makedirs(walk_to_idle_dir, exist_ok=True)
    for i, frame in enumerate(frames[:3]):
        out = normalize_frame(frame, ref_ratio)
        path = os.path.join(walk_to_idle_dir, f"walk_to_idle_{i:02d}.png")
        out.save(path)
        print(f"Saved {path}")

    # Bottom row (3-5): idle sitting
    idle_dir = os.path.join(ASSETS, "idle")
    os.makedirs(idle_dir, exist_ok=True)
    for i, frame in enumerate(frames[3:]):
        out = normalize_frame(frame, ref_ratio)
        path = os.path.join(idle_dir, f"idle_{i:02d}.png")
        out.save(path)
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
