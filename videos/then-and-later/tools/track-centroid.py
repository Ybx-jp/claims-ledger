#!/usr/bin/env python3
"""Measure the panel's slide from the TrackMatte image sequence and check it
against the film's own position function.

    npx remotion render TrackMatte out/matte --sequence --image-format=png --scale=0.25 \
        --frames=160-200
    python3 tools/track-centroid.py out/matte --scale 0.25

The matte draws the moving panel alone, white on black. The intensity-weighted
centroid of each frame, weighted by pixel centres, is the panel's centre; the
expected centre is PANEL_CENTER_X - SLIDE_PX * siso((f - 165) / 30) + PANEL_W / 2,
reimplemented here from timing.ts so the two can disagree.
"""

from __future__ import annotations

import argparse
import re
import struct
import sys
import zlib
from pathlib import Path

PANEL_W, PANEL_CENTER_X, LEFT_X = 860, 530, 100
SLIDE = (165, 195)


def siso(t: float) -> float:
    return 2 * t * t if t <= 0.5 else 1 - 2 * (1 - t) * (1 - t)


def expected_cx(frame: int) -> float:
    s, e = SLIDE
    t = 0.0 if frame <= s else 1.0 if frame >= e else siso((frame - s) / (e - s))
    return PANEL_CENTER_X - (PANEL_CENTER_X - LEFT_X) * t + PANEL_W / 2


def read_png_gray(path: Path) -> tuple[int, int, list[list[int]]]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    pos, chunks, w = 8, [], 0
    h = bit_depth = color_type = 0
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos : pos + 4])
        ctype = data[pos + 4 : pos + 8]
        body = data[pos + 8 : pos + 8 + length]
        if ctype == b"IHDR":
            w, h, bit_depth, color_type = struct.unpack(">IIBB", body[:10])
        elif ctype == b"IDAT":
            chunks.append(body)
        pos += 12 + length
    assert bit_depth == 8, bit_depth
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    raw = zlib.decompress(b"".join(chunks))
    stride = w * channels
    rows: list[list[int]] = []
    prev = bytearray(stride)
    p = 0
    for _ in range(h):
        f = raw[p]
        line = bytearray(raw[p + 1 : p + 1 + stride])
        p += 1 + stride
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            if f == 1:
                line[i] = (line[i] + a) & 255
            elif f == 2:
                line[i] = (line[i] + b) & 255
            elif f == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pred = a if pa <= pb and pa <= pc else b if pb <= pc else c
                line[i] = (line[i] + pred) & 255
        rows.append([line[i * channels] for i in range(w)])
        prev = line
    return w, h, rows


def centroid(rows: list[list[int]]) -> tuple[float, float]:
    sx = sy = s = 0.0
    for y, row in enumerate(rows):
        for x, v in enumerate(row):
            if v:
                s += v
                sx += v * (x + 0.5)
                sy += v * (y + 0.5)
    return sx / s, sy / s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--scale", type=float, default=0.25)
    ap.add_argument("--tolerance", type=float, default=1.0, help="px at full scale")
    a = ap.parse_args()
    files = sorted(Path(a.directory).glob("*.png"))
    if not files:
        print("no frames", file=sys.stderr)
        return 2
    worst = 0.0
    prev = None
    print("frame  measured  expected  delta  travel")
    for f in files:
        m = re.search(r"(\d+)\.png$", f.name)
        frame = int(m.group(1)) if m else 0
        _, _, rows = read_png_gray(f)
        cx, _ = centroid(rows)
        cx /= a.scale
        exp = expected_cx(frame)
        d = cx - exp
        worst = max(worst, abs(d))
        travel = "" if prev is None else f"{cx - prev:+.2f}"
        print(f"{frame:5d}  {cx:8.2f}  {exp:8.2f}  {d:+6.2f}  {travel}")
        prev = cx
    print(f"worst |delta| = {worst:.2f} px (tolerance {a.tolerance})")
    return 0 if worst <= a.tolerance else 1


if __name__ == "__main__":
    sys.exit(main())
