"""Completes the island's rock. The sprite was cut out of the old banner, whose frame cut the rock off
flat along the bottom; this grows the underside back, tapering to a blunt point.

    py -3.12 make_island_full.py   ->  composites/island.png   (1x, like the sprite; the stickers scale it)

The rock is two colours: a fill and the crack lines, with a band of the crack colour along each
edge. New rows continue the cracks by reflecting the plain-rock rows back and forth (so cracks run
on across each turn with no seam), are cut to a narrowing width, get the edge band back, and end in
a row of the crack colour. make_tankrock.py uses complete() for the tank's rock too.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SPRITES = os.path.join(HERE, "..", "20akshay00.github.io", "images", "sprites")
FILL = np.array([0x8d, 0x6e, 0x63, 255], np.uint8)
CRACK = np.array([0x79, 0x55, 0x48, 255], np.uint8)


def complete(A, extra=60, edge=4, seed=4):
    """A: RGBA array of a rock cut flat along its last row. Returns it with the underside grown back."""
    h, w = A.shape[:2]
    last = np.nonzero(A[h - 1, :, 3])[0]
    L0, R0 = last[0], last[-1]
    rng = np.random.default_rng(seed)
    out = np.zeros((h + extra, w, 4), np.uint8)
    out[:h] = A
    # rows of plain rock (only rock colours, nothing standing on them) to draw the cracks from
    rock_only = [y for y in range(h) if A[y, :, 3].any() and all(
        (p[:3] == FILL[:3]).all() or (p[:3] == CRACK[:3]).all() for p in A[y][A[y, :, 3] > 0])]
    top = rock_only[0]
    period = 2 * (h - 1 - top)
    for k in range(1, extra + 1):
        # reflect back and forth through the plain-rock rows: every crack carries on across the
        # turn, so there's no seam (repeating a band of rows left a horizontal line at each repeat)
        p = k % period
        row = A[h - 1 - p] if p <= h - 1 - top else A[top + (p - (h - 1 - top))]
        t = 1.1 * k + 0.03 * k * k                                # taper: steady, then curling under
        lo = int(L0 + t + rng.integers(0, 2))
        hi = int(R0 - t - rng.integers(0, 2))
        if hi - lo < 6:
            break
        seg = row[lo:hi + 1].copy()
        seg[seg[:, 3] == 0] = FILL           # it may have come from beyond an old edge
        seg[(seg[:, :3] != FILL[:3]).any(1) & (seg[:, :3] != CRACK[:3]).any(1)] = FILL   # rock colours only
        out[h + k - 1, lo:hi + 1] = seg
        out[h + k - 1, lo:lo + edge] = CRACK                      # the edge band
        out[h + k - 1, hi - edge + 1:hi + 1] = CRACK
    bottom = np.nonzero(out[..., 3].any(1))[0][-1]
    out[bottom][out[bottom][:, 3] > 0] = CRACK                    # close the bottom
    return out[:bottom + 1]


def tank_rock(island):
    """A smaller rock for the phi tank, cut from the island so it matches: the island's right edge (no
    characters on it), mirrored to make a left edge, a strip of plain rock from just inside it between."""
    edge = island[:, 184:]
    fill = island[:, 184:212]
    rock = np.concatenate([edge[:, ::-1], fill, edge], axis=1)
    rows = np.nonzero(rock[..., 3].any(1))[0]
    return complete(rock[rows[0]:rows[-1] + 1], seed=9)


if __name__ == "__main__":
    # art/ holds the editable 1x rocks. They're only written when missing, so hand edits survive;
    # pass --force to regenerate them (and lose the edits).
    import sys
    force = "--force" in sys.argv
    island = np.array(Image.open(os.path.join(SPRITES, "island.png")).convert("RGBA"))
    os.makedirs(os.path.join(HERE, "art"), exist_ok=True)
    for name, make in (("island", lambda: complete(island)), ("rock", lambda: tank_rock(island))):
        path = os.path.join(HERE, "art", f"{name}.png")
        if os.path.exists(path) and not force:
            print(f"kept art/{name}.png (exists; --force to regenerate)")
            continue
        out = make()
        Image.fromarray(out).save(path)
        print(f"wrote art/{name}.png ({out.shape[1]}x{out.shape[0]})")
