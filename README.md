# itch-setup

Everything behind my itch.io profile, [20akshay00.itch.io](https://20akshay00.itch.io/). It lives here
because itch.io keeps no history of profile edits.

The look is "screens in the sky": a neon sign for the banner, slim screens for the bio and the game
covers, and my pixel-art sprites floating around them with a soft pink glow, over a contour map drawn
as circuit traces.

## What's where

| | |
|---|---|
| `profile.css` | The profile's custom CSS. Edit this one. |
| `art/` | The pixel art everything is built from: the sprites, the robot's walk sheet, the two rocks, and the banner (an HTML page). |
| `upload/` | What goes into itch by hand: the banner, the background, the robot, and the minified CSS. Built, don't edit. |
| `docs/` | The floating sprites. GitHub Pages serves this folder, and the CSS loads the sprites from it. Built, don't edit. |
| `build.sh` | Rebuilds `upload/` and `docs/` from `art/` and `profile.css`. |
| `scripts/` | Helpers that `build.sh` runs. |
| `original/` | The profile as it was before the 2026 redesign. |

## Updating the profile

1. Edit `profile.css` or anything in `art/`.
2. Run `bash build.sh`. It needs ImageMagick, Python with numpy and Pillow, and Chrome. It prints how
   many characters the CSS is: itch allows 5120.
3. Commit and push. The sprites in `docs/` are live a minute later.
4. If something in `upload/` changed, put it into itch's theme editor (*Edit theme* on the profile):
   - `banner.png` as the banner
   - `background.png` as the background image
   - `profile.min.css` pasted into the custom CSS box
   - `robot.png` as the very first thing in the bio text (the CSS turns it into the walking robot)

## Notes

- **The rocks** in `art/` started as the island sprite cut out of the old banner, which had its bottom
  cut off. Its underside was grown back, and the tank's rock was cut from its edge. Both have since
  been edited by hand.
- **The floating sprites** are placed by `profile.css` on top of the banner, so they can bob. The
  island and the tank's rock are positioned so their ground is level. If you change the height of
  either rock's top edge, nudge their `top` values in the CSS to match.
- **The glow** is baked into the images instead of done in CSS. A CSS glow shows through
  semi-transparent pixels, which turned the tank's blue glass pink.
- **The CSS uses nesting** (rules written inside other rules) to fit in 5120 characters. Every current
  browser supports it.
- **On narrow screens** (below 1380px) the margin sprites hide and the banner's pull in.
