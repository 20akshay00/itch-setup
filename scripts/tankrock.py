"""Stands the phi tank on its rock, both at 2x.

    python tankrock.py art/tank.png art/rock.png OUT.png

The tank's feet sink SINK pixels below the rock's top edge, so it stands on the surface rather than
on the rim.
"""
import sys
import numpy as np
from PIL import Image

SINK = 22

tank, rock = (Image.open(p).convert("RGBA") for p in sys.argv[1:3])
tank = tank.resize((tank.width * 2, tank.height * 2), Image.NEAREST)
rock = rock.resize((rock.width * 2, rock.height * 2), Image.NEAREST)

# the rock's top edge: the median first opaque row across its middle third
alpha = np.array(rock)[..., 3]
top = int(np.median([np.nonzero(alpha[:, x])[0][0] for x in range(alpha.shape[1] // 3, 2 * alpha.shape[1] // 3)]))
stand = top + SINK

W = max(rock.width, tank.width)
H = tank.height - stand + rock.height
out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
out.alpha_composite(rock, ((W - rock.width) // 2, tank.height - stand))
out.alpha_composite(tank, ((W - tank.width) // 2, 0))
out.save(sys.argv[3])
