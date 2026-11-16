"""The page background: the contour map drawn as circuit traces.

    python background.py OUT.png   (a seamless 1280px tile; upload it as the
                                    page background in itch's theme editor)

A periodic height field (whole-number frequencies across the tile, so it repeats seamlessly) is drawn
as quiet terraces, one tone per height band. Its contours are then traced with marching squares on a
coarse grid. Marching squares only ever joins the midpoints of a cell's edges, so every contour comes
out in 45- and 90-degree runs, like routed traces. Now and then a run is left out and its two ends get
pads, the way a trace stops at a via. Drawn at 640px and scaled up 2x with nearest neighbour, the
sprites' pixel size.
"""
import numpy as np
from PIL import Image

SCALE, N = 2, 640
TAU = 2 * np.pi
TONES = ["#260a4b", "#280b4f", "#2a0b52", "#2c0c56", "#2e0d59", "#300e5c", "#320f60",
         "#300e5c", "#2e0d59", "#2c0c56", "#2a0b52"]          # one per height band
LINE, LINE2 = "#3a1470", "#47198a"                             # traces; every fourth level brighter
LEVELS, GRID = 8, 8                                            # contour levels; routing pitch (16px on screen)


def rgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.uint8)


def height_field():
    u, v = np.meshgrid(np.arange(N) / N, np.arange(N) / N)
    f = (np.sin(TAU * 2 * u + .7) * np.cos(TAU * 3 * v + .2) + .7 * np.sin(TAU * (2 * u + 3 * v) + 1.9)
         + .5 * np.cos(TAU * (5 * u - 2 * v) - .4) + .35 * np.sin(TAU * (3 * u - 4 * v) + 2.6)
         + .25 * np.cos(TAU * (u + 5 * v) + 1.1))
    return (f - f.min()) / (f.max() - f.min())


def draw_line(img, p, q, c):
    """1px octilinear line, wrapping at the tile edge."""
    (x0, y0), (x1, y1) = p, q
    steps = max(abs(x1 - x0), abs(y1 - y0), 1)
    for s in range(steps + 1):
        img[(y0 + (y1 - y0) * s // steps) % N, (x0 + (x1 - x0) * s // steps) % N] = c


def draw_pad(img, x, y, c):
    """3x3 pad with its drill hole left in the colour that was under it."""
    hole = img[y % N, x % N].copy()
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            img[(y + dy) % N, (x + dx) % N] = c
    img[y % N, x % N] = hole


def segments(field):
    """The traces as (level, from, to, broken) runs between cell-edge midpoints, by marching squares."""
    rng = np.random.default_rng(11)
    m = N // GRID
    corners = field[::GRID, ::GRID]                            # samples at the grid corners
    out = []
    for lv in range(1, LEVELS):
        th = lv / LEVELS
        above = corners > th
        for y in range(m):
            for x in range(m):
                a, b = above[y, x], above[y, (x + 1) % m]
                c, d = above[(y + 1) % m, (x + 1) % m], above[(y + 1) % m, x]
                X, Y, h = x * GRID, y * GRID, GRID // 2
                mids = {"t": (X + h, Y), "r": (X + GRID, Y + h), "b": (X + h, Y + GRID), "l": (X, Y + h)}
                crossed = [e for e, (p, q) in zip("trbl", ((a, b), (b, c), (c, d), (d, a))) if p != q]
                if len(crossed) == 2:
                    segs = [crossed]
                elif len(crossed) == 4:                        # saddle: pair them by the cell's centre value
                    segs = [["t", "l"], ["b", "r"]] if a == (field[Y + h, X + h] > th) else [["t", "r"], ["b", "l"]]
                else:
                    continue
                for e1, e2 in segs:
                    out.append((lv, mids[e1], mids[e2], rng.random() < .04))   # a break in the trace, padded
    return out


def traces():
    field = height_field()
    level = np.floor(field * LEVELS).astype(int)
    img = np.stack([rgb(c) for c in TONES])[np.minimum(level, len(TONES) - 1)]
    for lv, p, q, broken in segments(field):
        col = rgb(LINE2 if lv % 4 == 0 else LINE)
        if broken:
            draw_pad(img, *p, col)
            draw_pad(img, *q, col)
        else:
            draw_line(img, p, q, col)
    return img


if __name__ == "__main__":
    import sys
    Image.fromarray(traces()).resize((N * SCALE, N * SCALE), Image.NEAREST).save(sys.argv[1], optimize=True)
