#!/usr/bin/env bash
# Renders banner/banner.html to banner/banner.png: the 960x400 header image for itch (transparent
# apart from the sign), with headless Chrome. Upload it as the profile's banner in the theme editor.
#
#     bash render_banner.sh
set -euo pipefail
cd "$(dirname "$0")"
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
"$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --default-background-color=00000000 --virtual-time-budget=8000 --window-size=960,400 \
    --screenshot="$(cygpath -w "$PWD/banner/banner.png" 2>/dev/null || echo "$PWD/banner/banner.png")" \
    "file:///$(cygpath -m "$PWD/banner/banner.html" 2>/dev/null || echo "$PWD/banner/banner.html")" 2>/dev/null
magick identify -format "banner/banner.png %wx%h, alpha: %[channels]\n" banner/banner.png
