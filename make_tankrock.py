"""The phi tank standing on its own floating rock, so it can float like the island instead of hanging
in the air.

    py -3.12 make_tankrock.py   ->  composites/tankrock.png   (at 2x; the stickers don't scale it again)

The rock is art/rock.png (made by make_island_full.py, editable by hand); the tank is the site's
MechPhi sprite. Both are drawn at 2x, the pixel size of every other sprite, the tank's feet sunk SINK
pixels into the rock's top surface so it stands on it rather than on its rim.
"""
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SPRITES = os.path.join(HERE, "..", "20akshay00.github.io", "images", "sprites")
SINK = 22                               # screen px (2x) below the rock's top edge

rock = Image.open(os.path.join(HERE, "art", "rock.png")).convert("RGBA")
tank = Image.open(os.path.join(SPRITES, "MechPhi.png")).convert("RGBA")
rock = rock.resize((rock.width * 2, rock.height * 2), Image.NEAREST)
tank = tank.resize((tank.width * 2, tank.height * 2), Image.NEAREST)

# the rock's top surface: the median first opaque row across its middle third
alpha = np.array(rock)[..., 3]
top = int(np.median([np.nonzero(alpha[:, x])[0][0] for x in range(alpha.shape[1] // 3, 2 * alpha.shape[1] // 3)]))
stand = top + SINK

W = max(rock.width, tank.width)
H = tank.height - stand + rock.height
out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
out.alpha_composite(rock, ((W - rock.width) // 2, tank.height - stand))
out.alpha_composite(tank, ((W - tank.width) // 2, 0))
os.makedirs(os.path.join(HERE, "composites"), exist_ok=True)
out.save(os.path.join(HERE, "composites", "tankrock.png"))
print(f"wrote composites/tankrock.png ({W}x{H})")
