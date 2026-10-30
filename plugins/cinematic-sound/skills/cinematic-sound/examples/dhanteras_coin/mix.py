"""Sound design + mix for DhanterasCoin v6 (38.708 s). Epidemic Sound sources in ./wav.
Every cue = (file, src_start, src_end, place_at, gain_dB, pan -1..1, fade_in, fade_out, reverb_send, width).
Output: mix_v6.wav (48 kHz stereo, -14 LUFS after loudnorm) + stems for After Effects / Premiere."""
import subprocess, numpy as np, os
SR = 48000; DUR = 38.708; N = int(DUR * SR) + SR
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, "wav")
cache = {}
def load(name):
    if name not in cache:
        f = [x for x in os.listdir(W) if x.startswith(name + ".")][0]
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(W, f), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        cache[name] = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    return cache[name]

BUS = {k: np.zeros((N, 2)) for k in ("music", "amb", "sfx", "impact")}
SEND = np.zeros((N, 2))
def cue(bus, name, s0, s1, at, db=0.0, pan=0.0, fi=0.02, fo=0.05, rev=0.0, width=1.0, pan_to=None, lp=None):
    x = load(name); a = int(s0 * SR); b = int((s1 if s1 else len(x) / SR) * SR); seg = x[a:b].copy()
    if lp:                                                                   # vacuum: no air, only the felt low end
        F_ = np.fft.rfft(seg, axis=0); fr_ = np.fft.rfftfreq(len(seg), 1 / SR); F_ *= (1 / (1 + (fr_ / lp) ** 4))[:, None]; seg = np.fft.irfft(F_, len(seg), axis=0)
    n = len(seg); t = np.arange(n) / SR
    env = np.ones(n)
    if fi > 0: env *= np.clip(t / fi, 0, 1)
    if fo > 0: env *= np.clip((n / SR - t) / fo, 0, 1)
    seg *= (env * 10 ** (db / 20))[:, None]
    mid = seg.mean(1, keepdims=True); side = (seg[:, :1] - seg[:, 1:]) / 2
    seg = np.hstack([mid + side * width, mid - side * width])                # stereo width
    p = np.full(n, pan) if pan_to is None else np.linspace(pan, pan_to, n)  # constant-power pan / auto-pan
    gl = np.cos((p + 1) * np.pi / 4) * np.sqrt(2); gr = np.sin((p + 1) * np.pi / 4) * np.sqrt(2)
    seg[:, 0] *= gl; seg[:, 1] *= gr
    o = int(at * SR); o0 = max(o, 0); seg = seg[o0 - o:]; e = min(N, o0 + len(seg))
    BUS[bus][o0:e] += seg[:e - o0]; SEND[o0:e] += seg[:e - o0] * rev

B = 4.8  # brand intro length; CGI timeline starts here
# ---------------- MUSIC: "Last Frontier" (Hampus Naeselius). Body 30.3s -> hit at 55.0 lands on the burst (29.5)
cue("music", "score_full", 0.0, None, 0.0, db=0, fi=0.0, fo=0.0)   # ORIGINAL SCORE composed to picture (score/score.py)
# ---------------- AMBIENCE: dark space drone (the 'room' of the void), swells into the build
cue("amb", "drone", 2.0, 41.0, 0.0, db=-17, fi=1.2, fo=3.0, width=1.4)
# ---------------- BRAND INTRO: logo pieces assemble (0-2.5) -> name lands (2.5) -> push into the selfie lens -> shutter flash
cue("sfx", "whoosh_sub", 0.0, None, 0.6 - 0.3, db=-10, pan=-0.5, pan_to=0.5, lp=320, rev=0.3, width=1.4)
cue("sfx", "sparkle", 0.0, None, 1.4 - 0.64, db=-2, pan=0.4, pan_to=-0.4, rev=0.45)
cue("impact", "sub_thud", 0.0, 2.0, 2.5 - 0.05, db=-14, fo=1.2)
cue("sfx", "arc_impact", 1.6, 3.4, 2.5 - 0.29, db=-14, rev=0.4, width=1.4)
# ---------------- BRAND push + flash
cue("sfx", "whoosh_deep", 0.0, None, 4.7 - 1.04, db=-6, pan=-0.3, pan_to=0.3, lp=320, rev=0.25)
cue("sfx", "shutter", 0.0, None, B - 0.27, db=-2, rev=0.35)
cue("sfx", "swell2", 0.0, 3.99, B - 3.99, db=-9, fo=0.03, rev=0.3, width=1.4)   # pulls into the shutter
cue("impact", "braam2", 0.0, None, B - 0.05, db=-11, fo=2.0, rev=0.4)
cue("impact", "sub_thud", 0.0, 2.5, B - 0.05, db=-12, fo=1.5)
cue("sfx", "whoosh_sub", 0.0, None, 6.0 - 1.54, db=-9, lp=320, rev=0.2, width=1.3)          # camera falls toward the coin
# ---------------- DIYA EMBOSS (6.6-9.4): metal stretching up out of the face
cue("sfx", "metal_groans", 43.6, 47.2, B + 1.7, db=-1, fi=0.6, fo=0.9, rev=0.35, width=0.8)
# ---------------- MACRO: flame spark + electric arcs (10.7-14.6)
cue("sfx", "fuse", 2.27, 2.9, 10.7, db=2, pan=0.15, fo=0.2, rev=0.3)          # real spark ignition (earshot: strong)
cue("sfx", "arc_beam", 2.0, 6.4, 11.1, db=1, fi=0.4, fo=0.8, rev=0.2, width=1.5)
cue("sfx", "arc_beam", 6.8, 9.6, 12.3, db=-4, pan=-0.5, fi=0.3, fo=0.6, rev=0.2)
# ---------------- DIYA HERO (14.8-17.8): slow orbit, warm metal hum
cue("sfx", "whoosh_sub", 0.0, None, 15.2 - 1.54, db=-13, lp=320, rev=0.35, width=1.3)
# ---------------- FLIP (18.0-20.3): air whoosh up, spin, metallic landing ring
cue("sfx", "spin", 0.0, None, 19.15 - 0.95, db=-4, lp=2500, pan=-0.5, pan_to=0.5, rev=0.5, width=1.6)   # zero-g spin (doppler), no air
cue("sfx", "bowl", 3.0, 9.0, 18.0, db=-3, fi=0.4, fo=2.0, rev=0.6, width=1.5)                            # the coin's metal 'sings' as it turns
cue("impact", "subdrop", 0.0, 2.0, 20.3 - 0.06, db=-10, fo=1.0)                                      # felt reveal
cue("sfx", "arc_beam", 9.0, 11.5, 21.0, db=-12, fi=0.6, fo=0.8, pan=0.6, rev=0.3)                # faint residual energy
cue("sfx", "whoosh_sub", 0.0, None, 23.3 - 1.0, db=-12, lp=320, rev=0.3)                  # slow-mo hero move
# ---------------- FUSE (26.1-27.3) -> 3 bijili pops (27.4 / 27.65 / 27.9) -> cracks (27.7-29.3)
cue("sfx", "fuse", 28.0, 29.7, 25.9, db=6, fi=0.2, fo=0.3, pan=0.25, rev=0.15)
for t, g, p in ((27.4, -3, -0.35), (27.65, -1, 0.35), (27.9, 1, 0.0)):       # real firework bangs (earshot: strong)
    cue("sfx", "bang", 0.0, None, t - 0.08, db=g, pan=p, fo=0.4, rev=0.45)
cue("sfx", "glass_crack", 6.9, 8.6, 27.6, db=1, fi=0.15, fo=0.2, rev=0.3, width=1.4)
cue("sfx", "swell2", 0.0, 3.99, 29.30 - 3.99, db=-3, fo=0.02, rev=0.3, width=1.5)   # reverse swell, cut dead at 29.30: vacuum before the hit
# ---------------- BLAST (29.5): boom + sub + debris past the lens, then the long space tail
cue("impact", "boom", 0.0, None, 29.5 - 0.16, db=0, fo=3.0, rev=0.45, width=1.6)
cue("impact", "braam", 0.0, None, 29.5 - 0.06, db=-2, fo=2.5, rev=0.4, width=1.4)
cue("impact", "subdrop", 0.0, None, 29.5 - 0.06, db=-3, fo=2.0)
cue("impact", "sub_thud", 0.0, None, 29.5 - 0.05, db=-1, fo=2.5)
cue("impact", "bang", 0.0, None, 29.5 - 0.08, db=3, fo=0.8, rev=0.5, width=1.6)       # sharp crack: gives the blast a hard attack
cue("sfx", "debris_swoosh", 0.0, None, 30.0 - 0.84, db=0, pan=-0.8, pan_to=0.9, lp=4500, rev=0.2)
cue("sfx", "debris_swoosh", 0.0, None, 30.45 - 0.84, db=-3, pan=0.8, pan_to=-0.9, lp=4500, rev=0.2)
cue("sfx", "whoosh_deep", 0.0, None, 31.0 - 1.04, db=-7, lp=320, rev=0.4, width=1.5)        # camera pushes into the smoke
# ---------------- TITLE (32.3 focus-in, 33.9 light sweep)
cue("sfx", "whoosh_sub", 0.0, None, 32.5 - 1.54, db=-8, lp=320, rev=0.35)
cue("sfx", "sparkle", 0.0, None, 33.9 - 0.64, db=4, pan=-0.6, pan_to=0.6, rev=0.4)

# ---------------- MIX: sidechain music + ambience under impacts, reverb 'air', sub weight, master
def env_follow(x, att=0.005, rel=0.35):
    a = np.abs(x).max(1); out = np.zeros_like(a); ka, kr = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR)); v = 0.0
    for i in range(0, len(a), 48):                       # 1 ms steps
        s = a[i:i + 48].max(); v = (ka if s > v else kr) * v + (1 - (ka if s > v else kr)) * s; out[i:i + 48] = v
    return out
key = env_follow(BUS["impact"] + BUS["sfx"] * 0.6)
duck = 1 / (1 + 1.5 * key)
tt_ = np.arange(N) / SR
suck = 1 - 0.5 * np.clip((tt_ - 29.25) / 0.15, 0, 1) * np.clip((29.5 - tt_) / 0.02, 0, 1)   # music dips just before the blast, back on the hit
mus = BUS["music"] * (duck * suck)[:, None]; amb = BUS["amb"] * ((0.5 + 0.5 * duck) * suck)[:, None]
BUS["sfx"] *= suck[:, None]
# reverb: stereo decorrelated exponential-noise IR (2.6 s, dark) = big space around every hit
rng = np.random.default_rng(1); L_ = int(2.6 * SR); tt = np.arange(L_) / SR
ir = rng.standard_normal((L_, 2)) * np.exp(-tt / 0.75)[:, None]; ir[:int(0.012 * SR)] = 0
from numpy.fft import rfft, irfft
nf = 1 << int(np.ceil(np.log2(N + L_)))
wet = np.stack([irfft(rfft(SEND[:, c], nf) * rfft(ir[:, c], nf), nf)[:N] for c in range(2)], 1)
wet = irfft(rfft(wet, nf, axis=0) * (1 / (1 + (np.fft.rfftfreq(nf, 1 / SR) / 6000) ** 2))[:, None], nf, axis=0)[:N]   # darken
wet *= 0.08 / (np.abs(wet).max() + 1e-9) * 4
mix = mus * 1.1 + amb + BUS["sfx"] * 0.75 + BUS["impact"] * 0.9 + wet * 0.7
# end fade with the picture (37.9 -> 38.7)
t = np.arange(N) / SR; mix *= np.clip((DUR - t) / 0.8, 0, 1)[:, None]; mix = mix[:int(DUR * SR)]
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
def write(name, x):   # 32-bit float WAV: no clipping before the master limiter
    p = os.path.join(HERE, "out", name)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_f32le", p], input=x.astype(np.float32).tobytes())
write("mix_v9_pre.wav", mix)
for k, x in (("music", mus), ("ambience", amb), ("sfx", BUS["sfx"] + wet * 0.5), ("impacts", BUS["impact"])): write("stem_" + k + ".wav", x[:int(DUR * SR)])
print("peak", np.abs(mix).max())
