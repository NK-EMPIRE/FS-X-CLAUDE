"""Step 3: the global CREATIVE LOOK as a .cube (no masks, no colour keys), built the way a colourist builds it in curves:
  1. RGB-curve split tone: cool shadows, warm mids/highs (Danny Gan / Enam Alamin)
  2. Hue vs Sat: background hue up, skin rescue (orange x1.16, red at half of that, x1.08)
  3. Luma vs Sat: the deepest blacks lose colour (black stays black)
  4. Hue vs Luma density: the background hue a little darker = richer without more saturation (Gaku Lange)
  5. optional skin luma lift (Hue vs Luma on skin), more on dark faces, none on highlights
Every function is smooth and wide, so there's no banding or "painted" edges on 8-bit footage.
  python build_look.py --out FS_Look.cube                              (FirstSelfie Moody Teal v1 defaults)
  python build_look.py --targets work/targets.json --out Look.cube    (reference-driven params from grade_measure.py)
  python build_look.py --set split=0.7 bg_hue=185 --out Look.cube --preview work/src_*.png --intensity 1.25
--preview writes <frame>_look.jpg (before | after) so you can judge it before Premiere. Load the cube in Lumetri >
Creative > Look > Browse; Look Intensity 100-150."""
import argparse, glob, json, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fsgrade as fg

DEFAULTS = dict(            # = FirstSelfie Moody Teal v1 (the shipped Festival Intro grade)
    split=1.0,              # split-tone strength (1 = R -0.035 / B +0.01 in the shadows, R +0.02 / B -0.03 in the highs)
    bg_hue=178.0, bg_width=40.0, bg_sat_gain=0.18, bg_density=0.08,
    skin_hue=28.0, skin_width=30.0, skin_sat_gain=0.16, red_sat_gain=0.08,
    skin_density=0.04,      # Hue vs Luma: the orange band 4 % darker (warm mids feel richer, not brighter)
    black_desat=0.45,       # luma vs sat: colour removed at pure black
    skin_lift=0.0,          # 0 in v1; 0.22 = v2 (too bright/coloured on FirstSelfie footage, reached via Lumetri sliders instead)
)

def smooth_curve(x, pts, n=1024):
    g = np.linspace(0, 1, n); y = np.interp(g, [p[0] for p in pts], [p[1] for p in pts])
    k = np.hanning(61); k /= k.sum(); y = np.convolve(np.pad(y, 30, mode="edge"), k, mode="valid")
    return np.interp(x, g, y)

def bump(h, centre, width):
    d = fg.hdist(h, centre); return np.where(d < width, 0.5 + 0.5 * np.cos(np.pi * d / width), 0.0)

def look(c, p):
    c = np.clip(c, 0, 1); k = p["split"]
    R = smooth_curve(c[..., 0], [(0, 0), (0.12, 0.12 - 0.035 * k), (0.5, 0.5 + 0.015 * k), (0.85, 0.85 + 0.02 * k), (1, 1)])
    G = smooth_curve(c[..., 1], [(0, 0), (0.12, 0.12 - 0.008 * k), (0.5, 0.5), (0.85, 0.85 + 0.005 * k), (1, 1)])
    B = smooth_curve(c[..., 2], [(0, 0), (0.12, 0.12 + 0.01 * k), (0.5, 0.5 - 0.015 * k), (0.85, 0.85 - 0.03 * k), (1, 1 - 0.02 * k)])
    o = np.stack([R, G, B], -1)
    h, s, v = fg.rgb2hsv(o); y = fg.luma(o)[..., None]
    sat = 1 + p["bg_sat_gain"] * bump(h, p["bg_hue"], p["bg_width"]) + p["skin_sat_gain"] * bump(h, p["skin_hue"], p["skin_width"]) + p["red_sat_gain"] * bump(h, 8, 22)
    sat = sat * ((1 - p["black_desat"]) + p["black_desat"] * np.clip(y[..., 0] / 0.12, 0, 1))
    o = y + (o - y) * sat[..., None]
    skin = bump(h, 22, 34) * np.clip((s - 0.08) / 0.25, 0, 1)
    lift = 1 + p["skin_lift"] * skin * np.clip(1 - y[..., 0] / 0.75, 0, 1)
    dens = 1 - p["bg_density"] * bump(h, p["bg_hue"], p["bg_width"]) - p["skin_density"] * bump(h, p["skin_hue"], p["skin_width"])
    o = o * (dens * lift)[..., None]
    return np.clip(o, 0, 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True); ap.add_argument("--size", type=int, default=33)
    ap.add_argument("--targets"); ap.add_argument("--set", nargs="*", default=[])
    ap.add_argument("--preview", nargs="*"); ap.add_argument("--intensity", type=float, default=1.0)
    a = ap.parse_args(); p = dict(DEFAULTS)
    if a.targets: p.update({k: v for k, v in json.load(open(a.targets)).get("suggest", {}).items() if k in p and k != "skin_lift"})
    for kv in a.set: k, v = kv.split("="); p[k] = float(v)
    fg.write_cube(a.out, look(fg.lattice(a.size), p), title=os.path.splitext(os.path.basename(a.out))[0])
    json.dump(p, open(os.path.splitext(a.out)[0] + "_params.json", "w"), indent=2)
    print("wrote", a.out, p)
    if a.preview:
        L = fg.read_cube(a.out)
        for f in [x for pat in a.preview for x in glob.glob(pat)]:
            src = fg.load(f); out = fg.apply_cube(src, L, a.intensity)
            print(os.path.basename(f), "\n  before", fg.fmt(fg.describe(src)), "\n  after ", fg.fmt(fg.describe(out)))
            fg.save(np.concatenate([src, out], 1), os.path.splitext(f)[0] + "_look.jpg")

if __name__ == "__main__":
    main()
