"""Signals running along the background's circuit traces: a transparent animated PNG (APNG).

    python signals.py OUT.png

It is the background tile's size (640px, shown at 2x like the background) and loops, so the CSS can
tile it over the background with the same anchor, and the pulses stay on the traces at any screen
width. Each pulse is a bright head with a fading tail and a soft pink glow. It runs along a stretch of
one trace, fading in and out at the ends, then waits for its next turn. No two pulses ever come close.
"""
import struct
import sys
import zlib
import numpy as np
from PIL import Image                                          # only to check the result
from background import N, LEVELS, height_field, segments

FRAMES, MS = 240, 50            # a 12-second loop at 20 fps
RUN = 150                       # how far a pulse travels, in pixels (one pixel per frame)
PULSES = 8                      # per tile
APART = 16                      # how close two pulses' runs may come, if they run at the same time
TAIL, FADE = 22, 18             # tail length; fade-in/out at the ends of a run
HEAD, GLOW = (255, 190, 222), (255, 111, 174)
BRIGHT, HALO = .75, .32         # the head's opacity; the glow's cap
rng = np.random.default_rng(5)

# 17 opacities x 5 mixes of head and glow colour: one fixed palette, a byte a pixel
PALETTE = [round(m / 4 * h + (1 - m / 4) * g) for m in range(5) for _ in range(17) for h, g in zip(HEAD, GLOW)]
ALPHAS = [round(a / 16 * 255) for _ in range(5) for a in range(17)]


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


def meets(run1, start1, run2, start2):
    """Whether two pulses are on screen at the same time, with their runs closer than APART somewhere."""
    gap = abs(start1 - start2) % FRAMES
    if min(gap, FRAMES - gap) >= RUN + TAIL:
        return False
    a, b = np.array(run1)[:, None, :] % N, np.array(run2)[None, :, :] % N
    d = np.abs(a - b)
    d = np.minimum(d, N - d).max(-1)                            # distance across the tile's wrap-around
    return d.min() < APART


def blur_kernel(sigma):
    """A Gaussian in Fourier space; multiplying by it blurs with the tile's wrap-around."""
    f = np.fft.fftfreq(N)
    fx, fy = np.meshgrid(f, f)
    return np.exp(-2 * (np.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))


def render():
    """The frames, as arrays of palette indices."""
    long_paths = [p for p in paths() if len(p) >= RUN + 20]
    pulses = []
    while len(pulses) < PULSES:                                 # draw candidates; keep those that never meet another
        p = long_paths[rng.integers(len(long_paths))]
        s = rng.integers(len(p) - RUN)
        run = p[s:s + RUN][:: rng.choice([1, -1])]
        start = rng.integers(FRAMES)
        if all(not meets(run, start, r, t) for r, t in pulses):
            pulses.append((run, start))
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
                    core[y % N, x % N] = max(core[y % N, x % N], BRIGHT * fade * (1 - i / TAIL) ** 1.5)
        glow = np.clip(np.real(np.fft.ifft2(np.fft.fft2(core) * K)) * 9, 0, HALO)
        a = np.round(np.maximum(core, glow) * 16).astype(int)
        mix = np.round(core / np.maximum(a / 16, 1e-6) * 4).clip(0, 4).astype(int)
        frames.append(np.where(a > 0, mix * 17 + a, 0).astype(np.uint8))
    return frames


def write_apng(out, frames):
    """Writes the frames as an APNG by hand. Each frame is cut to the box around what it shows, replaces
    that box, and is cleared again once shown (dispose to background). So every frame starts from a clear
    canvas, and no decoder can leave an earlier frame's glow behind, which browsers did with Pillow's
    frames (those keep everything outside what changed, and rely on replacing exactly)."""
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    def idat(f):
        return zlib.compress(b"".join(b"\x00" + row.tobytes() for row in f), 9)   # filter 0 on each row

    png = [b"\x89PNG\r\n\x1a\n", chunk(b"IHDR", struct.pack(">IIBBBBB", N, N, 8, 3, 0, 0, 0)),
           chunk(b"PLTE", bytes(PALETTE)), chunk(b"tRNS", bytes(ALPHAS)),
           chunk(b"acTL", struct.pack(">II", len(frames), 0))]
    seq = 0
    for t, f in enumerate(frames):
        ys, xs = np.nonzero(f)
        if t == 0:
            x0, y0, x1, y1 = 0, 0, N, N                         # the first frame covers the whole image
        elif len(xs):
            x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        else:
            x0, y0, x1, y1 = 0, 0, 1, 1
        png.append(chunk(b"fcTL", struct.pack(">IIIIIHHBB", seq, x1 - x0, y1 - y0, x0, y0, MS, 1000, 1, 0)))
        seq += 1
        data = idat(f[y0:y1, x0:x1])
        if t == 0:
            png.append(chunk(b"IDAT", data))
        else:
            png.append(chunk(b"fdAT", struct.pack(">I", seq) + data))
            seq += 1
    png.append(chunk(b"IEND", b""))
    open(out, "wb").write(b"".join(png))


def main(out):
    frames = render()
    write_apng(out, frames)
    check = Image.open(out)                                     # play it back and compare, frame by frame
    for t, f in enumerate(frames):
        check.seek(t)
        if not np.array_equal(np.array(check.convert("RGBA"))[..., 3], np.array(ALPHAS)[f]):
            sys.exit(f"{out}: frame {t} plays back wrong")


if __name__ == "__main__":
    main(sys.argv[1])
