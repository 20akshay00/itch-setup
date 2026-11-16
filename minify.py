"""Minify profile.css -> profile.min.css for itch.io's 5120-character custom CSS box.

    python3 tools/itch/minify.py
"""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, "profile.css")).read()
css = re.sub(r"/\*.*?\*/", "", src, flags=re.S)          # comments
css = re.sub(r"\s+", " ", css)                            # whitespace runs
css = re.sub(r"\s*([{};:,>+])\s*", r"\1", css)            # around punctuation
css = css.replace(";}", "}").strip()
# a space is needed in "and (" media queries and calc(); restore those
css = css.replace("and(", "and (")
open(os.path.join(HERE, "profile.min.css"), "w").write(css)
print(f"{len(css)} / 5120 characters")
