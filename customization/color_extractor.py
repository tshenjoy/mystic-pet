"""Extract dominant fur colors from a cat photo."""

from PIL import Image
import numpy as np
from sklearn.cluster import KMeans


def extract_fur_colors(image_path, n_colors=4):
    """Extract dominant colors from a cat photo.

    Returns 4 colors sorted light-to-dark: (primary, light, mid, dark).
    Each color is an (R, G, B) tuple.
    """
    img = Image.open(image_path).convert("RGB")

    # Resize for speed
    img = img.resize((200, 200))
    pixels = np.array(img).reshape(-1, 3)

    # Remove near-white and near-black pixels (likely background)
    mask = (pixels.mean(axis=1) > 20) & (pixels.mean(axis=1) < 240)
    pixels = pixels[mask]

    if len(pixels) < n_colors:
        # Not enough non-background pixels, return defaults
        return _default_colors()

    kmeans = KMeans(n_clusters=n_colors, n_init=10, random_state=42)
    kmeans.fit(pixels)
    centers = kmeans.cluster_centers_.astype(int)

    # Sort by brightness (light to dark)
    brightness = [0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2] for c in centers]
    sorted_centers = [c for _, c in sorted(zip(brightness, centers), reverse=True)]

    primary = tuple(int(v) for v in sorted_centers[0])
    light = tuple(int(v) for v in sorted_centers[1]) if len(sorted_centers) > 1 else primary
    mid = tuple(int(v) for v in sorted_centers[2]) if len(sorted_centers) > 2 else light
    dark = tuple(int(v) for v in sorted_centers[3]) if len(sorted_centers) > 3 else mid

    return primary, light, mid, dark


def _default_colors():
    return (
        (200, 200, 200),
        (160, 160, 160),
        (120, 120, 120),
        (60, 60, 60),
    )
