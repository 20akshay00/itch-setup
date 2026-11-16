"""Signals running along the background's circuit traces: a transparent animated PNG (APNG).

    python signals.py OUT.png

It is the background tile's size (640px, shown at 2x like the background) and loops, so the CSS can
tile it over the background with the same anchor, and the pulses stay on the traces at any screen
width. Each pulse is a bright head with a fading tail and a soft pink glow. It runs along a stretch of
one trace, fading in and out at the ends, then waits for its next turn.
"""
import sys
import numpy as np
from PIL import Image
from background import N, LEVELS, height_field, segments

FRAMES, MS = 240, 50            # a 12-second loop at 20 fps
RUN = 150                       # how far a pulse travels, in pixels (one pixel per frame)
PULSES = 14                     # per tile
TAIL, FADE = 22, 18             # tail length; fade-in/out at the ends of a run
HEAD, GLOW = (255, 226, 240), (255, 111, 174)
rng = np.random.default_rng(5)


def paths():
    """Chain the unbroken runs of each contour level into paths, each a list of pixels in order."""
    found = []
    for lv in range(1, LEVELS):
        nbrs = {}
        for l, p, q, broken in segments(height_field()):
            if l != lv or broken:
                continue
            p, q = (p[0] % N, p[1] % N), (q[0] % N, q[1] % N)
            nbrs.setdefault(p, []).append(q)
            nbrs.setdefault(q, []).append(p)
        seen = set()
        ends = [n for n, v in nbrs.items() if len(v) == 1]
        for start in ends + list(nbrs):                         # open paths from their ends first, then loops
            if start in seen:
                continue
            path, prev, cur = [start], None, start
            seen.add(start)
            while True:
                nxt = [n for n in nbrs[cur] if n != prev and n not in seen]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                seen.add(cur)
                path.append(cur)
            found.append(path)
    return [pixels(p) for p in found]


def pixels(nodes):
    """The 1px octilinear line through the nodes, unwrapped across the tile edge."""
    out = [nodes[0]]
    for q in nodes[1:]:
        x0, y0 = out[-1]
        dx = (q[0] - x0 + N // 2) % N - N // 2                 # the short way round, across the edge
        dy = (q[1] - y0 + N // 2) % N - N // 2
        steps = max(abs(dx), abs(dy))
        out += [(x0 + dx * s // steps, y0 + dy * s // steps) for s in range(1, steps + 1)]
    return out


def blur_kernel(sigma):
    """A Gaussian in Fourier space; multiplying by it blurs with the tile's wrap-around."""
    f = np.fft.fftfreq(N)
    fx, fy = np.meshgrid(f, f)
    return np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))


def main(out):
    long_paths = [p for p in paths() if len(p) >= RUN + 20]
    pulses = []
    for _ in range(PULSES):
        p = long_paths[rng.integers(len(long_paths))]
        s = rng.integers(len(p) - RUN)
        run = p[s:s + RUN][:: rng.choice([1, -1])]
        pulses.append((run, rng.integers(FRAMES)))
    K = blur_kernel(2.5)
    frames = []
    for t in range(FRAMES):
        core = np.zeros((N, N))
        for run, start in pulses:
            k = (t - start) % FRAMES                            # where this pulse's head is
            if k >= RUN + TAIL:
                continue
            for i in range(TAIL):
                j = k - i
                if 0 <= j < RUN:
                    fade = min(1, (j + 1) / FADE, (RUN - j) / FADE)
                    x, y = run[j]
                    core[y % N, x % N] = max(core[y % N, x % N], fade * (1 - i / TAIL) ** 1.5)
        glow = np.clip(np.real(np.fft.ifft2(np.fft.fft2(core) * K)) * 9, 0, .55)
        # 17 opacities x 5 mixes of head and glow colour: one fixed palette, a byte a pixel
        a = np.round(np.maximum(core, glow) * 16).astype(int)
        mix = np.round(core / np.maximum(a / 16, 1e-6) * 4).clip(0, 4).astype(int)
        frame = Image.fromarray((mix * 17 + a).astype(np.uint8), "P")
        frame.putpalette(PALETTE)
        frames.append(frame)
    frames[0].save(out, save_all=True, append_images=frames[1:], duration=MS, loop=0, disposal=0, blend=0,
                   transparency=ALPHAS, optimize=True)


PALETTE = [round(m / 4 * h + (1 - m / 4) * g) for m in range(5) for _ in range(17) for h, g in zip(HEAD, GLOW)]
ALPHAS = bytes(round(a / 16 * 255) for _ in range(5) for a in range(17))


if __name__ == "__main__":
    main(sys.argv[1])
