itch.io profile (https://20akshay00.itch.io/) - kept here because itch.io has no history.

Draft 5, "screens in the sky": a neon sign for a banner, slim screens for the bio and the game covers,
pixel-art sprites with a pink glow floating over it all, on a contour map drawn as circuit traces.

WHAT GOES WHERE ON ITCH (theme editor)
  banner/banner.png      the banner image (960x400, transparent apart from the sign)
  bg/art_traces.png      the page background image (seamless 1280px tile)
  profile.min.css        the custom CSS (itch allows 5120 characters; the count is printed by minify.py)
  robot_walk_glow.png    uploaded as the very first thing in the bio text (the CSS makes it walk)
WHAT GOES ON THE SITE
  dist/itch-*.png        copy into the site's images/sprites/; the CSS loads them from
                         //20akshay00.github.io/images/sprites/itch-*.png (the site's _quarto.yml already
                         publishes images/sprites/*), so renaming them breaks the profile

FILES
  profile.css            the custom CSS, readable; edit this one (written with CSS nesting to fit)
  profile.min.css        profile.css minified: paste this
  minify.py              profile.css -> profile.min.css, prints the character count
  banner/banner.html     the sign, as HTML; render_banner.sh renders it to banner/banner.png
  art/island.png         the island with its rock completed (the old banner's frame had cut it off)
  art/rock.png           the phi tank's rock, cut from the island; both art/ files are 1x pixel art,
                         safe to edit by hand: nothing overwrites them
  build_sprites.sh       rebuilds every sprite from the site's sprites + art/: the tank on its rock,
                         the glow, the three-jet formation, the glowing robot sheet, then dist/
                         (stickers-glow/, composites/ and dist/ are build outputs, not committed)
  make_island_full.py    creates art/*.png when missing (--force regenerates, losing edits)
  make_tankrock.py       stands the tank on art/rock.png -> composites/tankrock.png
  make_stickers.sh       scales sprites 2x and bakes an edge/rim/glow OUTSIDE the silhouette (a CSS
                         drop-shadow shows through semi-transparent pixels, e.g. the tank's glass)
  make_bg_traces.py      writes bg/art_traces.png
  robot_walk_sheet.png   the robot walk sheet without the glow: the source for robot_walk_glow.png
  original/              what was live before the 2026-11 redesign: custom CSS + bio text
  (draft 4's contour background and its script are in git history)

LAYOUT NOTES
  The banner sprites are CSS (#profile_header::before/::after, .image_header::after) laid over the
  header image, so they can bob. The island and the tank's rock have their ground lines level at 300px
  from the top of the banner: island top 230 (ground 70px into its sticker), tank top 190 (ground 110px
  into its sticker at 80%). Change a rock's top edge in art/ and these two numbers need re-measuring.
  Below 1380px wide the margin stickers hide and the banner sprites pull inside the column.
