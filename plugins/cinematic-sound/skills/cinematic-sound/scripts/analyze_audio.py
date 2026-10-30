"""Score blueprint of a reference film's audio: tempo, frequency layers, onsets vs beat grid vs picture cuts, energy arc.
  python analyze_audio.py <film.mp4> <out_dir> [--sections 0,5.45,20,36.75,45.4,50]
Writes blueprint.png and prints per-section stats. Needs ffmpeg, numpy, librosa, matplotlib (all in the earshot venv)."""
import sys, os, re, argparse, subprocess, numpy as np, librosa, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
ap = argparse.ArgumentParser(); ap.add_argument("film"); ap.add_argument("out"); ap.add_argument("--sections", default="")
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.film, "-ac", "1", "-ar", "22050", "-f", "f32le", "-"], capture_output=True).stdout
y = np.frombuffer(raw, np.float32); sr = 22050; hop = 512; dur = len(y) / sr
S = np.abs(librosa.stft(y, hop_length=hop)) ** 2; fr = librosa.fft_frequencies(sr=sr); t = librosa.times_like(S[0], sr=sr, hop_length=hop)
bands = {"sub <60": (20, 60), "bass 60-250": (60, 250), "mid 250-2k": (250, 2000), "high 2k+": (2000, 11000)}
E = {k: 10 * np.log10(S[(fr >= lo) & (fr < hi)].sum(0) + 1e-9) for k, (lo, hi) in bands.items()}
tempo, beats = librosa.beat.beat_track(y=y, sr=sr, units="time"); on = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
log = subprocess.run(["ffmpeg", "-v", "info", "-i", a.film, "-vf", "select='gt(scene,0.25)',showinfo", "-an", "-f", "null", "-"], capture_output=True, text=True, errors="ignore").stderr
cuts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", log)]
fig, ax = plt.subplots(3, 1, figsize=(20, 10), sharex=True); sm = lambda x: np.convolve(x, np.ones(20) / 20, mode="same")
for k in E: ax[0].plot(t, sm(E[k]), label=k)
ax[0].legend(loc="lower left"); ax[0].set_title("frequency layers"); ax[1].plot(t, on, lw=0.6); ax[1].set_title("onsets, beats (grey), cuts (red)")
for b in beats: ax[1].axvline(b, color="0.85", lw=0.5)
for c in cuts: ax[1].axvline(c, color="r", lw=0.8)
rms = librosa.feature.rms(y=y, hop_length=hop)[0]; ax[2].plot(t, 20 * np.log10(rms + 1e-6)); ax[2].set_title("energy arc"); ax[2].set_xlabel("s")
plt.tight_layout(); plt.savefig(os.path.join(a.out, "blueprint.png"), dpi=70)
bt = np.array(beats); d = [min(abs(bt - c)) * 1000 for c in cuts] if len(bt) else []
print("duration %.1fs  tempo %.1f BPM  cuts %d  median cut-to-beat %s ms" % (dur, float(np.atleast_1d(tempo)[0]), len(cuts), round(float(np.median(d))) if d else "-"))
secs = [float(x) for x in a.sections.split(",")] if a.sections else list(np.linspace(0, dur, 6))
for s0, s1 in zip(secs, secs[1:]):
    msk = (t >= s0) & (t < s1); n_on = librosa.onset.onset_detect(onset_envelope=on[msk], sr=sr, hop_length=hop).size
    print("%5.1f-%5.1f  " % (s0, s1) + "  ".join("%s %.0f" % (k.split()[0], np.median(E[k][msk])) for k in E) + "  onsets/s %.1f" % (n_on / max(s1 - s0, 1e-3)))
print("cuts:", " ".join("%.2f" % c for c in cuts))
