#!/usr/bin/env bash
# Bakes a look into the sprites: scaled up 2x (nearest neighbour), then optionally tinted, edged,
# rimmed and/or glowing. Everything is drawn OUTSIDE the silhouette, so semi-transparent pixels (MechPhi's
# glass, the whole cage) stay as they are; a CSS drop-shadow edge or glow would show through them.
#
# Options are environment variables:
#   OUT=stickers      output folder
#   TINT=0            percent to pull colours toward TINTCOL first
#   TINTCOL=#2a0b52   (the page purple; #ff6fae gives the sign's pink cast)
#   EDGE=white        2px edge colour, or none
#   RIM=              optional 2px rim outside the edge
#   GLOW=             optional soft glow colour outside everything
#   SRC=, NAMES=, SCALE=200   source folder, which sprites, and the upscale percentage
#
#   bash make_stickers.sh                                        white edge (the original stickers)
#   OUT=stickers-dark EDGE="#0d0616" bash make_stickers.sh       dark edge
#   OUT=stickers-glow EDGE=none GLOW="#ff6fae" bash make_stickers.sh
#   OUT=stickers-glow EDGE=none GLOW="#ff6fae" SRC=composites NAMES=tankrock SCALE=100 bash make_stickers.sh
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="${SRC:-$HERE/../20akshay00.github.io/images/sprites}"
NAMES="${NAMES:-flyer jet1 cage}"
SCALE="${SCALE:-200}"
OUT="$HERE/${OUT:-stickers}"
TINT="${TINT:-0}"; TINTCOL="${TINTCOL:-#2a0b52}"; EDGE="${EDGE:-white}"; RIM="${RIM:-}"; GLOW="${GLOW:-}"
mkdir -p "$OUT"

# add_ring FILE COLOUR: a 2px ring of COLOUR just outside FILE's current silhouette
add_ring() {
    magick "$1" \( +clone -alpha extract -threshold 0 -write mpr:m \
        -morphology Dilate Diamond:2 mpr:m -compose MinusSrc -composite \
        -background "$2" -alpha shape \) -compose DstOver -composite "$1"
}

for name in $NAMES; do
    f="$OUT/$name.png"
    magick "$SRC/$name.png" -fill "$TINTCOL" -colorize "$TINT%" \
        -filter point -resize "$SCALE%" -bordercolor none -border 16 "$f"
    [ "$EDGE" != none ] && add_ring "$f" "$EDGE"
    [ -n "$RIM" ] && add_ring "$f" "$RIM"
    if [ -n "$GLOW" ]; then
        # blurred silhouette in GLOW, with the silhouette itself cut out of it, laid underneath
        magick "$f" \( +clone -alpha extract -threshold 0 -write mpr:m -blur 0x6 -level 0,70% \
            mpr:m -compose MinusSrc -composite -evaluate multiply .8 \
            -background "$GLOW" -alpha shape \) -compose DstOver -composite "$f"
    fi
done
echo "wrote $OUT/"
