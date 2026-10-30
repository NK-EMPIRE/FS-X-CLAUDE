"""Review sheets. Look at every one yourself (Read the jpg) before showing the user: judge the face, under-cap/eye shadows,
blacks, the logo and the background edges, not just the numbers.
  python sheets.py grid --pairs rough_30.png:graded_30.png rough_90.png:graded_90.png ... --labels 0:30 1:30 ... --out grid.jpg
  python sheets.py zoom --before rough.png --after graded.png --box 0.34,0.06,0.62,0.62 --out face_zoom.jpg
  python sheets.py side --a graded.png --b reference.png --labels GRADED REFERENCE --out vs_reference.jpg
--box is fractions of the frame (x0,y0,x1,y1). All inputs are resized to 1920x1080 first, so 4K exports and 1080 grabs mix."""
import argparse
from PIL import Image, ImageDraw

def L(f, size=(1920, 1080)): return Image.open(f).convert("RGB").resize(size, Image.LANCZOS)

def tag(img, x, y, text, gold=False):
    d = ImageDraw.Draw(img); d.rectangle([x, y, x + 8 + 7 * len(text), y + 24], fill=(0, 0, 0)); d.text((x + 5, y + 6), text, fill=(255, 200, 90) if gold else (255, 255, 255))

def grid(a):
    tw, th = 800, 450; n = len(a.pairs); cols = 2; rows = -(-n // cols)
    S = Image.new("RGB", (tw * 2 * cols, th * rows))
    for k, pr in enumerate(a.pairs):
        b, g = pr.split(":"); lab = a.labels[k] if a.labels and k < len(a.labels) else str(k + 1)
        for j, (f, nm) in enumerate([(b, "BEFORE"), (g, "GRADED")]):
            x = ((k % cols) * 2 + j) * tw; y = (k // cols) * th; S.paste(L(f, (tw, th)), (x, y)); tag(S, x, y, nm + " " + lab, j == 1)
    S.save(a.out, quality=92); print("wrote", a.out)

def zoom(a):
    x0, y0, x1, y1 = [float(v) for v in a.box.split(",")]; box = (int(1920 * x0), int(1080 * y0), int(1920 * x1), int(1080 * y1))
    b, g = L(a.before).crop(box), L(a.after).crop(box); w, h = b.size
    Z = Image.new("RGB", (w * 2, h)); Z.paste(b, (0, 0)); Z.paste(g, (w, 0)); Z = Z.resize((w * 4, h * 2), Image.LANCZOS)
    tag(Z, 10, 10, "BEFORE"); tag(Z, w * 2 + 10, 10, "GRADED", True); Z.save(a.out, quality=92); print("wrote", a.out)

def side(a):
    S = Image.new("RGB", (3200, 900)); S.paste(L(a.a, (1600, 900)), (0, 0)); S.paste(L(a.b, (1600, 900)), (1600, 0))
    la = a.labels or ["A", "B"]; tag(S, 10, 10, la[0], True); tag(S, 1610, 10, la[1]); S.save(a.out, quality=92); print("wrote", a.out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("grid"); x.add_argument("--pairs", nargs="+", required=True); x.add_argument("--labels", nargs="*"); x.add_argument("--out", required=True)
    x = sp.add_parser("zoom"); x.add_argument("--before", required=True); x.add_argument("--after", required=True); x.add_argument("--box", default="0.34,0.06,0.62,0.62"); x.add_argument("--out", required=True)
    x = sp.add_parser("side"); x.add_argument("--a", required=True); x.add_argument("--b", required=True); x.add_argument("--labels", nargs="*"); x.add_argument("--out", required=True)
    a = ap.parse_args(); {"grid": grid, "zoom": zoom, "side": side}[a.cmd](a)
