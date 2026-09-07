"""Derive the dark variant of every figure from its light source, and optionally
rasterize both for review.

    python3 docs/figures/build.py            # writes <name>-dark.svg beside each <name>.svg
    python3 docs/figures/build.py --png DIR  # also renders PNGs into DIR with headless Chrome

The light file is the source of truth. Its first <style> block carries the palette as
CSS custom properties on the root element; this swaps that block for the dark palette
and changes nothing else, so the two variants never drift in geometry or copy.
"""

import re
import shutil
import subprocess
import sys
import xml.dom.minidom
from pathlib import Path
from xml.parsers.expat import ExpatError

HERE = Path(__file__).parent

LIGHT = {
    "paper": "#FAF8F3",
    "ink": "#1C1B18",
    "muted": "#77726A",
    "rule": "#D9D4C7",
    "panel": "#F0ECE2",
    "mark": "#E6E0D2",
    "accent": "#B8451F",
    "accent-soft": "#F7DED2",
}
DARK = {
    "paper": "#161513",
    "ink": "#ECE8DF",
    "muted": "#9C968B",
    "rule": "#3A3732",
    "panel": "#201E1B",
    "mark": "#2E2B26",
    "accent": "#F0855A",
    "accent-soft": "#41251A",
}

PALETTE_RE = re.compile(r"svg\s*\{\s*(--[a-z-]+:\s*#[0-9A-Fa-f]{6};\s*)+\}")


def palette_block(p):
    return "svg { " + " ".join(f"--{k}: {v};" for k, v in p.items()) + " }"


def sources():
    return sorted(p for p in HERE.glob("*.svg") if not p.name.endswith("-dark.svg"))


def build():
    out = []
    for src in sources():
        text = src.read_text(encoding="utf-8")
        try:
            xml.dom.minidom.parseString(text)
        except ExpatError as exc:  # a malformed figure renders as an error box, not a figure
            sys.exit(f"{src.name}: not well-formed XML: {exc}")
        if not PALETTE_RE.search(text):
            sys.exit(f"{src.name}: no palette block found")
        light = PALETTE_RE.sub(palette_block(LIGHT), text, count=1)
        dark = PALETTE_RE.sub(palette_block(DARK), text, count=1)
        src.write_text(light, encoding="utf-8")
        dst = src.with_name(src.stem + "-dark.svg")
        dst.write_text(dark, encoding="utf-8")
        out += [src, dst]
    return out


def render(files, png_dir):
    chrome = next(
        (c for c in map(shutil.which, ("google-chrome", "chromium", "chromium-browser")) if c), None
    )
    if not chrome:
        sys.exit("no chrome/chromium on PATH to rasterize with")
    png_dir = Path(png_dir)
    png_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        m = re.search(r'viewBox="0 0 (\d+) (\d+)"', f.read_text(encoding="utf-8"))
        w, h = (int(m.group(1)), int(m.group(2))) if m else (960, 600)
        png = png_dir / (f.stem + ".png")
        subprocess.run(
            [
                chrome,
                "--headless=new",
                "--hide-scrollbars",
                "--force-device-scale-factor=2",
                f"--window-size={w},{h}",
                f"--screenshot={png}",
                f.resolve().as_uri(),
            ],
            check=True,
            capture_output=True,
        )
        print(png)


if __name__ == "__main__":
    built = build()
    for b in built:
        print(b.relative_to(HERE.parent.parent))
    if "--png" in sys.argv:
        render(built, sys.argv[sys.argv.index("--png") + 1])
