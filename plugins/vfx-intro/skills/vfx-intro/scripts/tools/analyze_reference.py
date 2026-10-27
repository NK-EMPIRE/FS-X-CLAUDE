"""Reverse-engineer a reference intro video: shots, timing, motion energy, brightness/colour, audio hits.
  python analyze_reference.py <video> <out_dir> [--start S --end E] [--fps 4]
Writes to out_dir:
  report.md          shot list (cut times, durations), per-second motion/brightness/colour table, audio peaks
  sheet_full.jpg     1 fps contact sheet of the whole video (timecodes burned in)
  sheet_shotNN.jpg   dense contact sheet per shot (fps per --fps) -> read these to study camera, light, material, FX
  dense_<a>_<b>.jpg  with --start/--end: a high-fps sheet of that window (e.g. the blast)
Needs ffmpeg/ffprobe on PATH and Pillow + numpy."""
import subprocess, sys, os, json, math, re, argparse
import numpy as np
from PIL import Image, ImageDraw

def run(cmd): return subprocess.run(cmd, capture_output=True, text=True, encoding="utf8", errors="ignore")

def probe(v):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate", "-of", "json", v])
    j = json.loads(r.stdout); dur = float(j["format"]["duration"]); vs = [s for s in j["streams"] if s["codec_type"] == "video"][0]
    num, den = vs["r_frame_rate"].split("/"); return dur, vs["width"], vs["height"], float(num) / float(den), any(s["codec_type"] == "audio" for s in j["streams"])

def frames(v, fps, w=320, start=None, end=None):
    """Decode at fps to small RGB arrays."""
    cmd = ["ffmpeg", "-v", "error"] + (["-ss", str(start)] if start else []) + ["-i", v] + (["-t", str(end - (start or 0))] if end else [])
    cmd += ["-vf", "fps=%s,scale=%d:-2" % (fps, w), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    dur, W, H, _, _ = probe(v); h = int(round(H * w / W / 2) * 2); n = len(raw) // (w * h * 3)
    return np.frombuffer(raw[:n * w * h * 3], np.uint8).reshape(n, h, w, 3), h

def sheet(imgs, times, path, cols=6, w=480):
    if not imgs: return
    ims = [Image.fromarray(i).resize((w, int(i.shape[0] * w / i.shape[1]))) for i in imgs]; h = ims[0].height
    rows = math.ceil(len(ims) / cols); S = Image.new("RGB", (cols * w, rows * h), (0, 0, 0)); d = ImageDraw.Draw(S)
    for k, (im, t) in enumerate(zip(ims, times)):
        x, y = (k % cols) * w, (k // cols) * h; S.paste(im, (x, y)); d.rectangle([x, y, x + 64, y + 16], fill=(0, 0, 0)); d.text((x + 3, y + 2), "%.2fs" % t, fill=(255, 220, 120))
    S.save(path, quality=88)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video"); ap.add_argument("out"); ap.add_argument("--start", type=float); ap.add_argument("--end", type=float); ap.add_argument("--fps", type=float, default=4)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    dur, W, H, vfps, has_audio = probe(a.video)
    # --- cuts: frame-difference at 12 fps (robust, no scdet dependency)
    F, h = frames(a.video, 12, 160)
    diff = np.array([0] + [np.abs(F[i].astype(np.int16) - F[i - 1].astype(np.int16)).mean() for i in range(1, len(F))])
    thr = max(18.0, np.percentile(diff, 97))
    cuts = [0.0] + [i / 12 for i in range(1, len(diff)) if diff[i] > thr and diff[i] > 2.2 * np.median(diff[max(0, i - 6):i + 6])]
    merged = []
    for c in cuts:
        if not merged or c - merged[-1] > 0.35: merged.append(c)
    shots = [(merged[i], merged[i + 1] if i + 1 < len(merged) else dur) for i in range(len(merged))]
    # --- per-second stats
    rows = []
    for s in range(int(math.ceil(dur))):
        seg = F[s * 12:(s + 1) * 12]
        if not len(seg): continue
        lum = seg.mean(); mot = diff[s * 12:(s + 1) * 12].mean(); rgb = seg.reshape(-1, 3).mean(0)
        sat = (seg.max(-1).astype(float) - seg.min(-1)).mean()
        rows.append((s, lum, mot, rgb, sat))
    # --- audio peaks (loudness per 0.1 s)
    peaks = []
    if has_audio:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.int16).astype(float)
        if len(x):
            win = 800; env = np.array([np.sqrt((x[i:i + win] ** 2).mean()) for i in range(0, len(x) - win, win)]) + 1e-6
            db = 20 * np.log10(env / 32768); base = np.median(db)
            for i in range(1, len(db) - 1):
                if db[i] > base + 12 and db[i] >= db[i - 1] and db[i] >= db[i + 1] and (not peaks or i * 0.1 - peaks[-1][0] > 0.25): peaks.append((i * 0.1, db[i]))
    # --- sheets
    G, _ = frames(a.video, 1, 320); sheet(list(G), [float(i) for i in range(len(G))], os.path.join(a.out, "sheet_full.jpg"), cols=8, w=320)
    for k, (s0, s1) in enumerate(shots):
        Fs, _ = frames(a.video, a.fps, 480, s0, s1)
        sheet(list(Fs)[:36], [s0 + i / a.fps for i in range(min(36, len(Fs)))], os.path.join(a.out, "sheet_shot%02d.jpg" % (k + 1)))
    if a.start is not None and a.end is not None:
        Fd, _ = frames(a.video, 10, 480, a.start, a.end)
        sheet(list(Fd), [a.start + i / 10 for i in range(len(Fd))], os.path.join(a.out, "dense_%g_%g.jpg" % (a.start, a.end)))
    # --- report
    L = ["# Reference analysis: %s" % os.path.basename(a.video), "", "%.2f s, %dx%d, %.2f fps, audio: %s" % (dur, W, H, vfps, has_audio), "",
         "## Shots (%d cuts -> avg %.2f s/shot)" % (len(shots), dur / max(1, len(shots))), "", "| # | in | out | dur | sheet |", "|---|---|---|---|---|"]
    for k, (s0, s1) in enumerate(shots): L.append("| %d | %.2f | %.2f | %.2f | sheet_shot%02d.jpg |" % (k + 1, s0, s1, s1 - s0, k + 1))
    L += ["", "## Per second (lum 0-255, motion = mean frame diff, rgb, sat)", "", "| s | lum | motion | r,g,b | sat |", "|---|---|---|---|---|"]
    for s, lum, mot, rgb, sat in rows: L.append("| %d | %.0f | %.1f | %d,%d,%d | %.0f |" % (s, lum, mot, rgb[0], rgb[1], rgb[2], sat))
    if peaks: L += ["", "## Audio hits (dB above median)", "", ", ".join("%.1fs" % t for t, _ in peaks)]
    L += ["", "## Read next", "Open sheet_full.jpg, then every sheet_shotNN.jpg. Fill the breakdown template in references/reverse_engineering.md."]
    open(os.path.join(a.out, "report.md"), "w", encoding="utf8").write("\n".join(L)); print("\n".join(L[:12 + len(shots)]))

if __name__ == "__main__": main()
