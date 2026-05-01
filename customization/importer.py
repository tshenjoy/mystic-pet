"""Upload flow: user photo → extract colors → recolor templates → reload."""

import os
import glob
from customization.color_extractor import extract_fur_colors
from customization.recolor import FurColors, recolor_all_frames


def process_cat_photo(photo_path, assets_dir):
    """Full pipeline: extract colors from photo, recolor all template animations.

    Args:
        photo_path: path to user's cat photo
        assets_dir: path to assets/ directory

    Returns:
        path to cache directory with recolored sprites
    """
    template_dir = os.path.join(assets_dir, "template")
    cache_dir = os.path.join(assets_dir, "cache", "custom")

    # Step 1: Extract fur colors
    primary, light, mid, dark = extract_fur_colors(photo_path)
    fur = FurColors(primary=primary, light=light, mid=mid, dark=dark)

    print(f"Extracted colors: primary={primary}, light={light}, mid={mid}, dark={dark}")

    # Step 2: Recolor each animation that has template frames
    for anim_name in os.listdir(template_dir):
        anim_dir = os.path.join(template_dir, anim_name)
        if not os.path.isdir(anim_dir):
            continue

        frame_paths = sorted(glob.glob(os.path.join(anim_dir, "*.png")))
        if not frame_paths:
            continue

        out_dir = os.path.join(cache_dir, anim_name)
        recolor_all_frames(frame_paths, fur, out_dir)
        print(f"Recolored {anim_name}: {len(frame_paths)} frames → {out_dir}")

    return cache_dir
