"""Minifies the CSS for itch.io's 5120-character custom CSS box.

    python minify.py profile.css upload/profile.min.css
"""
import re
import sys


def squeeze(css):
    """Minifies CSS that has no quoted strings in it."""
    css = re.sub(r"\s+", " ", css)                            # whitespace runs
    css = re.sub(r"\s*([{};:,>+])\s*", r"\1", css)            # around punctuation
    css = css.replace(";}", "}").replace(" !important", "!important")
    return css.replace("and(", "and (")                       # media queries need that space


src, dst = sys.argv[1], sys.argv[2]
css = open(src, encoding="utf8").read()
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)          # comments
# quoted strings (content: "> OPEN", font names, urls) are kept exactly; only what's between is squeezed
parts = re.split(r'("[^"]*")', css)
css = "".join(p if i % 2 else squeeze(p) for i, p in enumerate(parts)).strip()
open(dst, "w", encoding="utf8").write(css)
print(f"{dst}: {len(css)} / 5120 characters")
if len(css) > 5120:
    sys.exit("too long for itch")
