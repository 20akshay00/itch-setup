"""Minifies the CSS for itch.io's 5120-character custom CSS box.

    python minify.py profile.css upload/profile.min.css
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
css = open(src, encoding="utf8").read()
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)          # comments
css = re.sub(r"\s+", " ", css)                            # whitespace runs
css = re.sub(r"\s*([{};:,>+])\s*", r"\1", css)            # around punctuation
css = css.replace(";}", "}").replace(" !important", "!important").strip()
css = css.replace("and(", "and (")                        # media queries need that space
open(dst, "w", encoding="utf8").write(css)
print(f"{dst}: {len(css)} / 5120 characters")
if len(css) > 5120:
    sys.exit("too long for itch")
