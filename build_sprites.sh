#!/usr/bin/env bash
# Rebuilds the glowing sprites the profile CSS loads, from the editable art in art/.
#
#     bash build_sprites.sh
#
# art/island.png and art/rock.png are 1x pixel art; edit them freely. They're created by
# make_island_full.py only if missing, so this never overwrites your edits.
set -euo pipefail
cd "$(dirname "$0")"
PY="${PY:-py -3.12}"
GLOW="#ff6fae"

$PY make_island_full.py                     # creates art/*.png if missing; keeps them otherwise
$PY make_tankrock.py                        # art/rock.png + the tank -> composites/tankrock.png (2x)
OUT=stickers-glow EDGE=none GLOW="$GLOW" bash make_stickers.sh                                   # flyer, jet, cage
OUT=stickers-glow EDGE=none GLOW="$GLOW" SRC=art NAMES=island bash make_stickers.sh              # the completed island
OUT=stickers-glow EDGE=none GLOW="$GLOW" SRC=composites NAMES=tankrock SCALE=100 bash make_stickers.sh
# the margin jets: three in formation, baked into one image (one URL in the CSS instead of three)
J=stickers-glow/jet1.png
magick -size 150x170 xc:none \
    \( "$J" -filter point -resize 52x50! \) -geometry +14+0 -composite \
    \( "$J" -filter point -resize 44x43! \) -geometry +96+58 -composite \
    \( "$J" -filter point -resize 40x39! \) -geometry +0+124 -composite \
    stickers-glow/jets.png
echo "wrote stickers-glow/jets.png"
# dist/: the files the profile CSS loads, under the names it uses; copy them into the site's
# images/sprites/ (the robot sheet is uploaded into the bio instead)
mkdir -p dist
for n in island tankrock flyer jets cage; do cp "stickers-glow/$n.png" "dist/itch-$n.png"; done
echo "wrote dist/: $(ls dist | tr '\n' ' ')"
# the robot walk sheet for the bio, with the same glow (64px frames; the glow stays inside each frame)
magick robot_walk_sheet.png \( +clone -alpha extract -threshold 0 -write mpr:m -blur 0x3 -level 0,60% \
    mpr:m -compose MinusSrc -composite -evaluate multiply .9 -background "$GLOW" -alpha shape \) \
    -compose DstOver -composite robot_walk_glow.png
echo "wrote robot_walk_glow.png"
