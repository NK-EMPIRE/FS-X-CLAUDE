"""Contact sheets for review.
  python contact_sheet.py video <file> <out.jpg> [--start S --dur D --fps 3 --cols 6 --w 480]
  python contact_sheet.py frames <glob> <out.jpg> [--every N --cols 3 --w 960]     (e.g. Blender test PNGs)"""
import sys, glob, math, subprocess, argparse
from PIL import Image, ImageDraw
ap = argparse.ArgumentParser(); ap.add_argument("mode"); ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--start", type=float, default=0); ap.add_argument("--dur", type=float); ap.add_argument("--fps", type=float, default=3)
ap.add_argument("--cols", type=int, default=6); ap.add_argument("--w", type=int, default=480); ap.add_argument("--every", type=int, default=1)
a = ap.parse_args()
if a.mode == "video":
    dur = a.dur or float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.src], capture_output=True, text=True).stdout) - a.start
    n = int(math.ceil(dur * a.fps)); rows = max(1, math.ceil(min(n, 300) / a.cols))
    cmd = ["ffmpeg", "-y", "-v", "error", "-ss", str(a.start)] + (["-t", str(a.dur)] if a.dur else []) + ["-i", a.src, "-vf", "fps=%g,scale=%d:-2,tile=%dx%d" % (a.fps, a.w, a.cols, rows), "-frames:v", "1", a.out]
    subprocess.run(cmd, check=True)
else:
    fs = sorted(glob.glob(a.src))[::a.every]; ims = [Image.open(f).convert("RGB") for f in fs]
    ims = [i.resize((a.w, int(i.height * a.w / i.width))) for i in ims]; h = ims[0].height; rows = math.ceil(len(ims) / a.cols)
    S = Image.new("RGB", (a.cols * a.w, rows * h)); d = ImageDraw.Draw(S)
    for k, im in enumerate(ims):
        x, y = (k % a.cols) * a.w, (k // a.cols) * h; S.paste(im, (x, y)); d.text((x + 4, y + 4), fs[k].replace("\\", "/").split("/")[-1], fill=(255, 220, 120))
    S.save(a.out, quality=90)
print(a.out)
