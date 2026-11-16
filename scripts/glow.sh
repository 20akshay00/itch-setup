#!/usr/bin/env bash
# glow.sh IN OUT [SCALE% PAD BLUR LEVEL% STRENGTH]
# Scales a sprite up (nearest neighbour), pads it, and lays a soft pink glow around it - outside the
# silhouette only. (A CSS drop-shadow glow also shows through semi-transparent pixels, which turned
# the tank's blue glass pink.)
set -euo pipefail
IN="$1"; OUT="$2"; SCALE="${3:-200}"; PAD="${4:-16}"; BLUR="${5:-6}"; LEVEL="${6:-70}"; STRENGTH="${7:-.8}"
GLOW="#ff6fae"

magick "$IN" -filter point -resize "$SCALE%" -bordercolor none -border "$PAD" \
    \( +clone -alpha extract -threshold 0 -write mpr:m -blur "0x$BLUR" -level "0,$LEVEL%" \
       mpr:m -compose MinusSrc -composite -evaluate multiply "$STRENGTH" \
       -background "$GLOW" -alpha shape \) \
    -compose DstOver -composite "$OUT"
