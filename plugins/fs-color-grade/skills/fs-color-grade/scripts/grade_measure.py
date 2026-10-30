"""Step 1: measure the reference and the footage -> targets.json + the frames used.
  python grade_measure.py --ref REF.mp4 --ref-range 45-58 --src ROUGH.mp4 --out work/ [--bg-zone left] [--brand-hue 6]
  python grade_measure.py --frames a.png b.png ...                     (just describe stills, e.g. graded exports)
--ref-range: the part of the reference whose look you want (seconds). --bg-zone: where the background colour to copy lives
(left/right/full/centre). --brand-hue: hue of a logo colour that must NOT change (FirstSelfie red ~6). Output: one line per
frame plus targets.json {ref, src, suggest} that build_look.py --targets reads."""
import argparse, os, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fsgrade as fg

def avg(ds, key):
    xs = [d[key] for d in ds if d.get(key)]
    if not xs: return None
    h = np.degrees(np.angle(np.mean([np.exp(1j * np.radians(x["hue"])) for x in xs]))) % 360
    return {"hue": round(float(h), 1), "sat": round(float(np.mean([x["sat"] for x in xs])), 3), "luma": round(float(np.mean([x["luma"] for x in xs])), 3)}

def sample(video, rng, n, out, tag):
    if rng: a, b = [float(x) for x in rng.split("-")]
    else: d = fg.duration(video); a, b = d * 0.05, d * 0.95
    ts = np.linspace(a, b, n); paths = []
    for t in ts: paths.append(fg.grab(video, round(float(t), 2), os.path.join(out, "%s_%05.1f.png" % (tag, t)), width=1920))
    return paths

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref"); ap.add_argument("--ref-range"); ap.add_argument("--src"); ap.add_argument("--src-range")
    ap.add_argument("--n", type=int, default=6); ap.add_argument("--out", default="grade_work")
    ap.add_argument("--bg-zone", default="left"); ap.add_argument("--brand-hue", type=float)
    ap.add_argument("--frames", nargs="*")
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    if a.frames:
        for f in a.frames: print(os.path.basename(f), fg.fmt(fg.describe(fg.load(f), bg_zone=a.bg_zone, brand_hue=a.brand_hue)))
        return
    res = {}
    for tag, video, rng in (("ref", a.ref, a.ref_range), ("src", a.src, a.src_range)):
        if not video: continue
        ds = []
        for p in sample(video, rng, a.n, a.out, tag):
            d = fg.describe(fg.load(p), bg_zone=a.bg_zone, brand_hue=a.brand_hue if tag == "src" else None)
            skip = d["shadows_pct"] > 90 or d["skin"] is None          # fades, black frames, cutaways without a face
            if not skip: ds.append(d)
            print(tag, os.path.basename(p), fg.fmt(d), "(skipped)" if skip else "")
        res[tag] = {"background": avg(ds, "background"), "skin": avg(ds, "skin"), "brand": avg(ds, "brand"),
                    "shadows_pct": round(float(np.mean([d["shadows_pct"] for d in ds])), 1)}
    if "ref" in res and "src" in res:
        r, s = res["ref"], res["src"]; sug = {}
        if r["background"] and s["background"]:
            sug["bg_hue"] = r["background"]["hue"]
            sug["bg_sat_gain"] = round(float(np.clip((r["background"]["sat"] / max(s["background"]["sat"], 0.05) - 1) * 0.5, 0, 0.35)), 3)
            sug["bg_density"] = round(float(np.clip((s["background"]["luma"] - r["background"]["luma"]) * 0.6, 0, 0.15)), 3)
        if r["skin"] and s["skin"]:
            sug["skin_sat_gain"] = round(float(np.clip((r["skin"]["sat"] / max(s["skin"]["sat"], 0.05) - 1) * 0.4, 0, 0.2)), 3)
            sug["skin_lift"] = round(float(np.clip((r["skin"]["luma"] - s["skin"]["luma"]) * 0.8, 0, 0.25)), 3)
        res["suggest"] = sug
        print("\nREF  ", r); print("SRC  ", s); print("SUGGESTED LOOK PARAMS", sug)
    fg.dump(res, os.path.join(a.out, "targets.json")); print("wrote", os.path.join(a.out, "targets.json"))

if __name__ == "__main__":
    main()
