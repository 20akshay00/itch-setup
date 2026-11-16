# itch-setup

Everything behind my itch.io profile, [20akshay00.itch.io](https://20akshay00.itch.io/).

## What's where

|               |                                                                                                                            |
| ------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `profile.css` | The profile's custom CSS. Edit this one.                                                                                   |
| `placeholder.css` | The custom CSS for the link-card placeholder project's own page: just the sign and a way back to the profile.   |
| `art/`        | The pixel art everything is built from: the sprites, the robot's walk and idle sheets, the two rocks, and the banner (an HTML page). |
| `upload/`     | What goes into itch by hand: the banner, the background, the robot, and the minified CSS. Built, don't edit.               |
| `docs/`       | The floating sprites and the trace signals. GitHub Pages serves this folder, and the CSS loads them from it. Built, don't edit. |
| `build.sh`    | Rebuilds `upload/` and `docs/` from `art/` and `profile.css`.                                                              |
| `scripts/`    | Helpers that `build.sh` runs.                                                                                              |
| `original/`   | The profile as it was before the 2026 redesign.                                                                            |

## Updating the profile

1. Edit `profile.css` or anything in `art/`.
2. Run `bash build.sh`. It needs ImageMagick, Python with numpy and Pillow, and Chrome. It prints how
   many characters the CSS is: itch allows 5120.
3. Commit and push.
4. If something in `upload/` changed, put it into itch's theme editor (*Edit theme* on the profile):
   - `banner.png` as the banner
   - `background.png` as the background image
   - `profile.min.css` pasted into the custom CSS box
   - `robot.png` as the very first thing in the bio text (the CSS hides it and draws the walking robot
     from `docs/robot.png` in its place)

## Notes

- **The floating sprites** are placed by `profile.css` on top of the banner to animate motion.
- **The glow** is baked into the images to save CSS space.
- **The signals** running along the background's traces are an animated PNG (`scripts/signals.py`) built from the
  same traces as the background. The CSS tiles it over the background with the same anchor, so the two
  stay lined up at any screen width. Change the background and rebuild both.
- **The CSS uses nesting** to fit in 5120 characters.
- **itch filters the CSS**: it silently drops some properties, like `zoom` and `scale`. `transform` gets through.
- **The banner is shown at 720px wide** (75%), and the sprites around it are placed in percentages of
  it, so they scale together when itch shrinks the banner on phones.
- **Phones** (below 600px) get their own layout: a bigger sign, the sprites pulled in, even card gaps, a
  shorter robot cycle, and on touch screens no hover effects.
- **The link preview** (Discord, Twitter, ...) is `upload/card.png`. itch uses the cover of the first
  project in the profile's grid, so it's the cover of a placeholder project (ID 5384024) that has to stay
  first, and the CSS hides it. Its own page gets `upload/placeholder.min.css`: only the sign and an
  "open profile" button, and a click anywhere on the page goes to the profile (CSS can't redirect).
- **The CSS is almost exactly at the limit** (about 5100 of 5120). Anything new needs something cut.
