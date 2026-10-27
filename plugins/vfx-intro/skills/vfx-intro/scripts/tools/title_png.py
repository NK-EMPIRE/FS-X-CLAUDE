"""Render title lettering to transparent 1920x1080 PNGs (white, AE adds the gold/bevel/glow).
Needed because After Effects only renders fonts installed FOR ALL USERS; per-user fonts silently fall back to a serif.
  python title_png.py <out.png> "<TEXT>" <font.ttf> <size> <center_y> [--tracking 0.0] [--w 1920 --h 1080]
Prints the rendered text height (use it to space the lines above/below the main word)."""
import argparse
from PIL import Image, ImageDraw, ImageFont
ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("text"); ap.add_argument("font"); ap.add_argument("size", type=int); ap.add_argument("y", type=int)
ap.add_argument("--tracking", type=float, default=0.0, help="extra spacing as a fraction of size (0.6 = wide caps)"); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
a = ap.parse_args()
f = ImageFont.truetype(a.font, a.size); im = Image.new("RGBA", (a.w, a.h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
sp = a.size * a.tracking; widths = [d.textlength(c, font=f) for c in a.text]; total = sum(widths) + sp * (len(a.text) - 1)
bb = d.textbbox((0, 0), a.text, font=f); th = bb[3] - bb[1]; x = (a.w - total) / 2; y = a.y - th / 2 - bb[1]
for c, cw in zip(a.text, widths): d.text((x, y), c, font=f, fill=(255, 255, 255, 255)); x += cw + sp
im.save(a.out); print("height", th)
