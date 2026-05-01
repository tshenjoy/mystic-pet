"""Recolor grayscale template sprites with user's cat colors.

The template uses grayscale zones to define shading:
  - Outline (dark, <40 avg)     → stays as-is
  - Dark shadow (40-100)        → tinted with user's darkest fur color
  - Mid shade (100-160)         → tinted with user's mid fur color
  - Light shade (160-220)       → tinted with user's light fur color
  - Body white (>220)           → tinted with user's primary fur color

The grayscale value controls brightness within each zone,
so shading detail is preserved after recoloring.
"""

from PIL import Image
import colorsys


class FurColors:
    """Holds the color palette extracted from a user's cat photo."""

    def __init__(self, primary, light, mid, dark, eye_color=None):
        """Each color is an (R, G, B) tuple."""
        self.primary = primary     # main body
        self.light = light         # lighter highlights
        self.mid = mid             # mid-tone shading
        self.dark = dark           # dark shadows / markings
        self.eye_color = eye_color or (120, 180, 60)  # default green


def recolor_frame(frame_img, fur_colors):
    """Recolor a single grayscale template frame.

    Args:
        frame_img: PIL Image (RGBA) — grayscale template
        fur_colors: FurColors instance

    Returns:
        New PIL Image (RGBA) with fur colors applied
    """
    result = frame_img.copy()
    px = result.load()

    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = px[x, y]
            if a < 10:
                continue

            avg = (r + g + b) // 3

            if avg < 40:
                # Outline — keep dark, slight tint
                px[x, y] = _tint(avg, fur_colors.dark, strength=0.2, alpha=a)
            elif avg < 100:
                # Dark shadow zone
                px[x, y] = _tint(avg, fur_colors.dark, strength=0.85, alpha=a)
            elif avg < 160:
                # Mid shade zone
                px[x, y] = _tint(avg, fur_colors.mid, strength=0.85, alpha=a)
            elif avg < 220:
                # Light shade zone
                px[x, y] = _tint(avg, fur_colors.light, strength=0.85, alpha=a)
            else:
                # White body — primary color
                px[x, y] = _tint(avg, fur_colors.primary, strength=0.8, alpha=a)

    return result


def _tint(gray_value, target_color, strength=0.8, alpha=255):
    """Blend a gray value toward a target color, preserving luminance.

    gray_value: 0-255 grayscale of the template pixel
    target_color: (R, G, B) to tint toward
    strength: 0.0 = no tint, 1.0 = full color replacement
    """
    tr, tg, tb = target_color
    luminance_factor = gray_value / 255.0

    # Apply target color scaled by original luminance
    out_r = int(tr * luminance_factor * strength + gray_value * (1 - strength))
    out_g = int(tg * luminance_factor * strength + gray_value * (1 - strength))
    out_b = int(tb * luminance_factor * strength + gray_value * (1 - strength))

    return (min(255, out_r), min(255, out_g), min(255, out_b), alpha)


def recolor_all_frames(frame_paths, fur_colors, output_dir):
    """Recolor a list of template frames and save to output_dir.

    Args:
        frame_paths: list of paths to template PNG frames
        fur_colors: FurColors instance
        output_dir: directory to save recolored frames

    Returns:
        list of output file paths
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    output_paths = []
    for path in frame_paths:
        frame = Image.open(path).convert('RGBA')
        recolored = recolor_frame(frame, fur_colors)
        out_path = os.path.join(output_dir, os.path.basename(path))
        recolored.save(out_path)
        output_paths.append(out_path)

    return output_paths
