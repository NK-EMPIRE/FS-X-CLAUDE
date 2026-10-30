"""Shared helpers for the fs-color-grade scripts: frame grabs, colour maths, region masks, measurement and .cube I/O.
Everything works on float RGB arrays in 0-1. Requires numpy + Pillow + ffmpeg on PATH."""
import os, subprocess, json
import numpy as np
from PIL import Image

# ---------- frames ----------
def grab(video, t, out_png, width=None):
    """One frame at t seconds, decoded as Rec.709 (untagged 4K H.264 is 709; ffmpeg's default 601 matrix skews hues ~5 deg)."""
    vf = "scale=in_color_matrix=bt709:out_color_matrix=bt709" + (":w=%d:h=-2" % width if width else "") + ",format=rgb24"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", "-vf", vf, out_png], check=True)
    return out_png

def duration(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True)
    return float(r.stdout.strip())

def load(path):
    return np.asarray(Image.open(path).convert("RGB")).astype(float) / 255

def save(a, path, quality=92):
    Image.fromarray((np.clip(a, 0, 1) * 255).round().astype(np.uint8)).save(path, quality=quality)

# ---------- colour maths ----------
def rgb2hsv(c):
    r, g, b = c[..., 0], c[..., 1], c[..., 2]; mx = c.max(-1); mn = c.min(-1); d = mx - mn
    h = np.zeros_like(mx); nz = d > 1e-6
    h = np.where(nz & (mx == r), ((g - b) / np.maximum(d, 1e-6)) % 6, h)
    h = np.where(nz & (mx == g), (b - r) / np.maximum(d, 1e-6) + 2, h)
    h = np.where(nz & (mx == b), (r - g) / np.maximum(d, 1e-6) + 4, h)
    return h * 60, np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0), mx

def luma(c): return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
def hdist(a, b): return np.abs((a - b + 180) % 360 - 180)

# ---------- regions ----------
def skin_mask(a, centre_only=True):
    """Skin by YCbCr range (works for South-Asian to fair skin under warm practicals); restricted to the centre/upper frame."""
    r, g, b = a[..., 0], a[..., 1], a[..., 2]; H, W = r.shape
    Y = 0.299 * r + 0.587 * g + 0.114 * b; Cb = -0.169 * r - 0.331 * g + 0.5 * b; Cr = 0.5 * r - 0.419 * g - 0.081 * b
    m = (Cr > 0.04) & (Cr < 0.18) & (Cb > -0.15) & (Cb < 0.0) & (Y > 0.12) & (Y < 0.85)
    if centre_only: m[:, :int(W * 0.25)] = False; m[:, int(W * 0.75):] = False; m[int(H * 0.75):] = False
    return m

def zone_mask(shape, zone):
    H, W = shape[:2]; m = np.zeros((H, W), bool)
    x0, x1 = {"left": (0, 0.42), "right": (0.58, 1), "full": (0, 1), "centre": (0.25, 0.75)}[zone]
    m[:, int(W * x0):int(W * x1)] = True
    return m

def dominant_hue(a, mask):
    h, s, v = rgb2hsv(a); m = mask & (s > 0.12) & (v > 0.10)
    if m.sum() < 200: return None
    hist, edges = np.histogram(h[m], bins=72, range=(0, 360), weights=s[m])
    hist = np.convolve(np.r_[hist[-2:], hist, hist[:2]], np.ones(5) / 5, "valid")
    return float(edges[np.argmax(hist)] + 2.5)

def regions(a, bg_zone="left", bg_hue=None, brand_hue=None):
    """Masks for background (dominant hue in the zone, skin excluded), skin, and an optional saturated brand colour (e.g. a red logo)."""
    h, s, v = rgb2hsv(a); skin = skin_mask(a)
    zone = zone_mask(a.shape, bg_zone) & ~skin_mask(a, centre_only=False)
    bh = bg_hue if bg_hue is not None else dominant_hue(a, zone)
    bg = zone & (hdist(h, bh) < 25) & (s > 0.15) & (v > 0.10) if bh is not None else np.zeros_like(skin)
    out = {"background": bg, "skin": skin}
    if brand_hue is not None:
        out["brand"] = (hdist(h, brand_hue) < 15) & (s > 0.65) & (v > 0.45)
    return out, bh

def stats(a, m):
    if m.sum() < 50: return None
    c = a[m].mean(0); h, s, v = rgb2hsv(c[None])
    return {"hex": "#%02x%02x%02x" % tuple((c * 255).round().astype(int)), "hue": round(float(h[0]), 1),
            "sat": round(float(s[0]), 3), "luma": round(float(luma(c)), 3), "px": int(m.sum())}

def describe(a, **kw):
    rg, bh = regions(a, **kw)
    d = {k: stats(a, m) for k, m in rg.items()}
    d["shadows_pct"] = round(float(100 * (luma(a) < 0.2).mean()), 1); d["bg_hue_detected"] = bh
    return d

def fmt(d):
    parts = []
    for k in ("background", "skin", "brand"):
        if k in d:
            x = d[k]; parts.append("%s %s" % (k, "n/a" if x is None else "%s hue %3.0f sat %.2f luma %.2f" % (x["hex"], x["hue"], x["sat"], x["luma"])))
    return " | ".join(parts) + " | shadows %.0f%%" % d["shadows_pct"]

# ---------- .cube ----------
def write_cube(path, table, title="FS grade"):
    """table: (N^3, 3) in .cube order (red fastest, then green, then blue)."""
    n = round(len(table) ** (1 / 3))
    with open(path, "w") as f:
        f.write('TITLE "%s"\nLUT_3D_SIZE %d\nDOMAIN_MIN 0.0 0.0 0.0\nDOMAIN_MAX 1.0 1.0 1.0\n' % (title, n))
        for r, g, b in np.clip(table, 0, 1): f.write("%.6f %.6f %.6f\n" % (r, g, b))

def read_cube(path):
    n, rows = None, []
    for line in open(path):
        t = line.strip()
        if not t or t.startswith("#") or t.startswith("TITLE") or t.startswith("DOMAIN"): continue
        if t.startswith("LUT_3D_SIZE"): n = int(t.split()[1]); continue
        rows.append([float(x) for x in t.split()[:3]])
    return np.array(rows).reshape(n, n, n, 3)   # [b, g, r]

def lattice(n):
    g = np.linspace(0, 1, n); i = np.arange(n ** 3)
    return np.stack([g[i % n], g[(i // n) % n], g[i // (n * n)]], -1)

def apply_cube(c, L, intensity=1.0):
    """Trilinear lookup; L is read_cube() output. intensity blends with the input like Lumetri's Look Intensity (<=1)."""
    n = L.shape[0]; x = np.clip(c, 0, 1) * (n - 1); i0 = np.minimum(np.floor(x).astype(int), n - 2); f = x - i0; out = 0
    for db in (0, 1):
        for dg in (0, 1):
            for dr in (0, 1):
                w = (f[..., 2] if db else 1 - f[..., 2]) * (f[..., 1] if dg else 1 - f[..., 1]) * (f[..., 0] if dr else 1 - f[..., 0])
                out = out + w[..., None] * L[i0[..., 2] + db, i0[..., 1] + dg, i0[..., 0] + dr]
    return c + (out - c) * intensity

def dump(obj, path):
    with open(path, "w") as f: json.dump(obj, f, indent=2)
