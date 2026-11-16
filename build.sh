#!/usr/bin/env bash
# Rebuilds everything from art/ and profile.css:
#   docs/    the floating sprites, the robot and the trace signals (served by GitHub Pages, loaded by the CSS)
#   upload/  what goes into itch by hand: banner, background, robot, minified CSS
# Needs ImageMagick, Python with numpy + Pillow, and Chrome (for the banner).
set -euo pipefail
cd "$(dirname "$0")"
PY="${PY:-py -3.12}"
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
mkdir -p docs upload

# floating sprites: 2x with the glow
for s in flyer island; do bash scripts/glow.sh "art/$s.png" "docs/$s.png"; done
$PY scripts/tankrock.py art/tank.png art/rock.png "$TMP/tank.png"
bash scripts/glow.sh "$TMP/tank.png" docs/tank.png 100           # already 2x

# signals running along the background's traces (an animated PNG)
(cd scripts && $PY signals.py ../docs/signals.png)

# for itch
bash scripts/glow.sh art/robot.png upload/robot.png 100 0 3 60 .9  # the sheet is already 2x
# the robot as the CSS draws it: the walk row, and below it the two idle frames at 2x, each held for
# five slots so the same ten-step animation plays them at about 2 fps
magick art/robot_idle.png -filter point -resize 200% -crop 64x64 +repage "$TMP/idle_%d.png"
magick "$TMP"/idle_0.png "$TMP"/idle_0.png "$TMP"/idle_0.png "$TMP"/idle_0.png "$TMP"/idle_0.png     "$TMP"/idle_1.png "$TMP"/idle_1.png "$TMP"/idle_1.png "$TMP"/idle_1.png "$TMP"/idle_1.png +append "$TMP/idle.png"
magick art/robot.png "$TMP/idle.png" -background none -append +repage "$TMP/robot.png"
bash scripts/glow.sh "$TMP/robot.png" docs/robot.png 100 0 3 60 .9
$PY scripts/background.py upload/background.png
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --default-background-color=00000000 --virtual-time-budget=8000 --window-size=960,400 \
    --screenshot="$(cygpath -w "$PWD/upload/banner.png")" "file:///$(cygpath -m "$PWD/art/banner.html")" 2>/dev/null
$PY scripts/minify.py profile.css upload/profile.min.css

echo "built: $(ls docs | tr '\n' ' ')| $(ls upload | tr '\n' ' ')"
