"""Step 6: bake the WHOLE finished grade (every Lumetri slider + the look) into one .cube that editors apply with one click.
  python bake_lut.py identity --out identity_65.png                 4K lattice image (65^3 points, 4x4-pixel cells)
     -> in Premiere, point the graded clip at this PNG (projectItem.changeMediaPath), export one frame, point it back
  python bake_lut.py extract graded_identity.png --out FS_FINAL.cube [--title "..."]
  python bake_lut.py verify --cube FS_FINAL.cube --before rough_709.png --after premiere_graded.png
     -> mean error must be < 1.5/255 (we got 0.8); the region table must match
  python bake_lut.py resize --cube FS_FINAL.cube --size 33 --out FS_FINAL_33.cube   (65 -> 33 is exact: every other point)
Works for any grade that is global (Lumetri Basic/Creative/Curves/Wheels/HSL curves). Masks, vignette, sharpen and
anything spatial can't live in a LUT; turn them off before baking, or tell the user they aren't included."""
import argparse, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fsgrade as fg

def layout(n, cell, w):
    cols = w // cell; i = np.arange(n ** 3); return i // cols, i % cols

def identity(a):
    rr, cc = layout(a.size, a.cell, a.w); rows = rr.max() + 1
    assert rows * a.cell <= a.h, "lattice doesn't fit; use a smaller --size or --cell"
    img = np.zeros((a.h, a.w, 3)); c = fg.lattice(a.size)
    block = np.zeros((rows * (a.w // a.cell), 3)); block[:len(c)] = c
    block = block.reshape(rows, a.w // a.cell, 3)
    img[:rows * a.cell] = np.repeat(np.repeat(block, a.cell, 0), a.cell, 1)
    fg.save(img, a.out); print("wrote", a.out, "(%dx%d, %d^3 points)" % (a.w, a.h, a.size))

def extract(a):
    g = fg.load(a.graded); h, w = g.shape[:2]; rr, cc = layout(a.size, a.cell, w)
    m = a.cell // 2   # average the inner cells of each block (immune to chroma bleed at block edges)
    s = sum(g[rr * a.cell + dy, cc * a.cell + dx] for dy in (m - 1, m) for dx in (m - 1, m)) / 4
    fg.write_cube(a.out, s, title=a.title or os.path.splitext(os.path.basename(a.out))[0])
    n = a.size; mid = n // 2 + (n // 2) * n + (n // 2) * n * n
    print("wrote", a.out, "| black", (s[0] * 255).round(), "white", (s[-1] * 255).round(), "mid grey", (s[mid] * 255).round())

def verify(a):
    L = fg.read_cube(a.cube); b = fg.load(a.before); p = fg.load(a.after)
    if b.shape != p.shape:
        from PIL import Image
        b = np.asarray(Image.fromarray((b * 255).astype(np.uint8)).resize(p.shape[1::-1], Image.LANCZOS)).astype(float) / 255
    o = fg.apply_cube(b, L); d = np.abs(o - p) * 255
    print("mean err %.2f /255 | 99th pct %.1f /255  (%s)" % (d.mean(), np.percentile(d, 99), "PASS" if d.mean() < 1.5 else "CHECK"))
    print("  LUT     ", fg.fmt(fg.describe(o, brand_hue=a.brand_hue))); print("  reference", fg.fmt(fg.describe(p, brand_hue=a.brand_hue)))
    if a.save: fg.save(o, a.save)

def resize(a):
    L = fg.read_cube(a.cube); n = L.shape[0]; step = (n - 1) // (a.size - 1)
    assert (a.size - 1) * step == n - 1, "size must divide evenly (65->33, 65->17)"
    S = L[::step, ::step, ::step].reshape(-1, 3); fg.write_cube(a.out, S, title=os.path.splitext(os.path.basename(a.out))[0]); print("wrote", a.out)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    x = sp.add_parser("identity"); x.add_argument("--out", required=True); x.add_argument("--size", type=int, default=65)
    x.add_argument("--cell", type=int, default=4); x.add_argument("--w", type=int, default=3840); x.add_argument("--h", type=int, default=2160)
    x = sp.add_parser("extract"); x.add_argument("graded"); x.add_argument("--out", required=True); x.add_argument("--size", type=int, default=65)
    x.add_argument("--cell", type=int, default=4); x.add_argument("--title")
    x = sp.add_parser("verify"); x.add_argument("--cube", required=True); x.add_argument("--before", required=True); x.add_argument("--after", required=True)
    x.add_argument("--brand-hue", type=float); x.add_argument("--save")
    x = sp.add_parser("resize"); x.add_argument("--cube", required=True); x.add_argument("--size", type=int, default=33); x.add_argument("--out", required=True)
    a = ap.parse_args(); {"identity": identity, "extract": extract, "verify": verify, "resize": resize}[a.cmd](a)
