"""Step 7: a correct H.264 export preset (.epr) for Premiere / Media Encoder.
Trap we hit: "Match Source - High bitrate" is really 1080p at 10 Mbps, so a 4K export comes out at 10.7 Mbps and looks soft.
This copies Adobe's "High Quality 2160 4K" (or the 1080 one) and sets the frame rate and bitrate.
  python make_preset.py --fps 25 --mbps 50 --out FS_H264_4K25_50Mbps.epr            (4K UHD)
  python make_preset.py --fps 25 --mbps 20 --hd --out FS_H264_1080p25_20Mbps.epr
Then, in Premiere ExtendScript: app.encoder.encodeSequence(seq, outPath, eprPath, 0, 1); app.encoder.startBatch();"""
import argparse, glob, re

TICKS = 254016000000   # Premiere ticks per second; ADBEVideoFPS stores ticks per frame

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=float, required=True); ap.add_argument("--mbps", type=float, default=50)
    ap.add_argument("--max-mbps", type=float); ap.add_argument("--hd", action="store_true"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    name = "High Quality 1080 HD.epr" if a.hd else "High Quality 2160 4K.epr"
    hits = glob.glob(r"C:/Program Files/Adobe/Adobe Media Encoder */MediaIO/systempresets/4E49434B_48323634/" + name) + \
           glob.glob("/Applications/Adobe Media Encoder */*/MediaIO/systempresets/4E49434B_48323634/" + name)
    if not hits: raise SystemExit("Adobe Media Encoder H.264 system presets not found; is Media Encoder installed?")
    t = open(sorted(hits)[-1], encoding="utf-8").read()
    for ident, v in [("ADBEVideoFPS", str(round(TICKS / a.fps))), ("ADBEVideoTargetBitrate", "%g." % a.mbps),
                     ("ADBEVideoMaxBitrate", "%g." % (a.max_mbps or round(a.mbps * 1.2)))]:
        t, n = re.subn(r"(<ParamIdentifier>%s</ParamIdentifier>.*?<ParamValue>)[^<]*(</ParamValue>)" % ident, r"\g<1>%s\g<2>" % v, t, count=1, flags=re.S)
        assert n == 1, ident
    open(a.out, "w", encoding="utf-8").write(t)
    print("wrote", a.out, "from", sorted(hits)[-1], "| fps", a.fps, "| target", a.mbps, "Mbps")

if __name__ == "__main__":
    main()
