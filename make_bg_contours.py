"""Pixel-art contour-map background tiles for the itch.io profile.

    python3 tools/itch/make_bg_contours.py   ->  tools/itch/bg/contours_terraces.png

The height field is a sum of sines with whole-number frequencies across the tile, so the tile repeats
seamlessly in both directions. It is drawn at low resolution with hard one-pixel contour lines (no
anti-aliasing) and scaled up by SCALE with nearest neighbour: the smooth map of the "contours" background,
drawn in the same pixels as the sprites floating over it.
"""
import os
import numpy as np
from PIL import Image

SCALE = 2                                 # the sprites' scale (robot, jets)
N = 640                                   # logical tile -> 1280 px
LEVELS = 8                                # contour spacing: lines per unit of height
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bg")

u, v = np.meshgrid(np.arange(N) / N, np.arange(N) / N)
TAU = 2 * np.pi
# whole-number frequencies only: periodic in u and v
# frequencies 2-5 across the tile: smaller hills than one wave per tile, and mixed so the tile has
# no shorter period of its own
field = (np.sin(TAU * 2 * u + 0.7) * np.cos(TAU * 3 * v + 0.2)
         + 0.7 * np.sin(TAU * (2 * u + 3 * v) + 1.9)
         + 0.5 * np.cos(TAU * (5 * u - 2 * v) - 0.4)
         + 0.35 * np.sin(TAU * (3 * u - 4 * v) + 2.6)
         + 0.25 * np.cos(TAU * (u + 5 * v) + 1.1))
field = (field - field.min()) / (field.max() - field.min())          # 0..1
level = np.floor(field * LEVELS).astype(int)


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.uint8)


def contour_mask():
    """A pixel is on a line where its level differs from the pixel to its right or below (wrapping)."""
    return (level != np.roll(level, -1, 1)) | (level != np.roll(level, -1, 0))


def save(name, rgb):
    img = Image.fromarray(rgb).resize((N * SCALE, N * SCALE), Image.NEAREST)
    os.makedirs(OUT, exist_ok=True)
    img.save(os.path.join(OUT, f"contours_{name}.png"), optimize=True)


def terraces():
    """Each height band a step lighter, like a pixel-art elevation map, with the lines on top."""
    # a narrow range: neighbouring bands differ by a step you sense more than see
    tones = ["#260a4b", "#280b4f", "#2a0b52", "#2c0c56", "#2e0d59",
             "#300e5c", "#320f60", "#300e5c", "#2e0d59", "#2c0c56", "#2a0b52"]
    rgb = np.array([hexrgb(tones[min(l, len(tones) - 1)]) for l in level.ravel()]).reshape(N, N, 3)
    m = contour_mask()
    rgb[m] = hexrgb("#3a1470")
    rgb[m & (level % 4 == 0)] = hexrgb("#47198a")
    return rgb


if __name__ == "__main__":
    save("terraces", terraces())
    print("wrote", os.path.join(OUT, "contours_terraces.png"))
