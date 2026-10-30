"""Original score for 'The Dhanteras Coin' (38.708 s). Real recorded instruments (VSCO2 CE, CC0) played by a small
sampler; every note is placed on the picture's beat grid. 104.45 BPM, D minor. Beat 0 = shutter cut (4.8 s), beat 43 = blast.
  python score.py [--test A B]   -> stems/*.wav + score.wav  (test: render only seconds A..B)"""
import os, re, sys, glob, subprocess, numpy as np
SR = 48000; DUR = 38.708
HERE = os.path.dirname(os.path.abspath(__file__)); LIB = r"D:/aetmp_dl/vsco/lib"
BPM = 104.45; BEAT = 60 / BPM; T0 = 4.8
def bt(n): return T0 + n * BEAT                           # beat -> seconds
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11, "Bb": 10, "Eb": 3, "Ab": 8}
def m(n):                                                  # "D2" -> midi
    mm = re.match(r"([A-G][#b]?)(-?\d)", n); return 12 * (int(mm.group(2)) + 1) + NOTE[mm.group(1)]
# ------------------------------------------------------------------ sampler
_cache = {}
def wav(path):
    if path not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        _cache[path] = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    return _cache[path]
def index(folder, piano=False):
    out = []
    for f in glob.glob(os.path.join(LIB, folder, "**", "*.wav"), recursive=True):
        b = os.path.basename(f)
        if piano:
            k = re.search(r"dyn(\d)_rr\d_(\d{3})", b); note = 21 + int(k.group(2)) * 2 if k else None; v = int(k.group(1)) if k else 1
        else:
            k = re.search(r"_([A-G]#?-?\d)_", b); note = m(k.group(1)) if k else None
            vv = re.search(r"_v(\d)", b); v = int(vv.group(1)) if vv else 1
        if note is not None: out.append((note, v, f))
    return out
INST = {}
def inst(name, folder, piano=False): INST[name] = index(folder, piano)
inst("cello_spic", "Strings/Cello Section/spic"); inst("cello_sus", "Strings/Cello Section/susvib"); inst("cello_trem", "Strings/Cello Section/trem")
inst("vln_spic", "Strings/Violin Section/Spic"); inst("vln_sus", "Strings/Violin Section/susVib"); inst("vln_trem", "Strings/Violin Section/Trem")
inst("cb_spic", "Strings/Solo Contrabass/Spic"); inst("cb_sus", "Strings/Solo Contrabass/SusVib")
inst("horn_sus", "Brass/F Horn/sus"); inst("horn_stac", "Brass/F Horn/stac"); inst("tbn_sus", "Brass/Tenor Trombone/sus")
inst("tbn_stac", "Brass/Tenor Trombone/stac"); inst("tuba_sus", "Brass/Tuba/sus"); inst("piano", "Keys/Upright Piano", piano=True)
ONESHOT = {
    "timp": sorted(glob.glob(os.path.join(LIB, "Percussion/Timpani/Timpani*_Hit_v3*.wav")) + glob.glob(os.path.join(LIB, "Percussion/Timpani/Timpani*_Hit_v4*.wav"))),
    "timp_roll": sorted(glob.glob(os.path.join(LIB, "Percussion/Timpani/Rolls/*v5*.wav"))),
    "kick": sorted(glob.glob(os.path.join(LIB, "VSCO 1 Percussion/drums/bass/*f*.wav"))),
    "taiko": sorted(glob.glob(os.path.join(LIB, "VSCO 1 Percussion/drums/other/ethnic/giant/**/*fff*.wav"), recursive=True)) or sorted(glob.glob(os.path.join(LIB, "VSCO 1 Percussion/drums/other/ethnic/giant/**/*.wav"), recursive=True)),
    "rim": sorted(glob.glob(os.path.join(LIB, "VSCO 1 Percussion/drums/other/ethnic/giant/*rimshot*.wav"))),
    "snare": sorted(glob.glob(os.path.join(LIB, "VSCO 1 Percussion/drums/snare/drum1/*click*.wav"))) or sorted(glob.glob(os.path.join(LIB, "VSCO 1 Percussion/drums/snare/drum1/*.wav"))),
    "glock_up": sorted(glob.glob(os.path.join(LIB, "Miscellania Raw/Misc 2/glock_glisses/*up*.wav"))),
    "bells": sorted(glob.glob(os.path.join(LIB, "Miscellania Raw/Misc 2/NepaleseBells/*.wav"))),
}
STEMS = {k: np.zeros((int((DUR + 4) * SR), 2)) for k in ("strings", "brass", "keys", "perc", "sub", "fx")}
SEND = np.zeros_like(STEMS["strings"]); _rr = {}
def place(stem, x, at, gain=1.0, rev=0.25):
    o = int(at * SR)
    if o < 0: x = x[-o:]; o = 0
    e = min(len(STEMS[stem]), o + len(x)); x = x[:e - o] * gain
    STEMS[stem][o:e] += x; SEND[o:e] += x * rev
def note(name, n, at, dur, vel=0.7, gain=1.0, stem="strings", rev=0.3, rel=0.25, atk=0.0):
    """Play midi n on instrument `name`: nearest sampled pitch (resampled, max ~4 st), velocity layer, round robin."""
    if isinstance(n, str): n = m(n)
    S = INST[name]; vmax = max(v for _, v, _ in S); want = 1 + round(vel * (vmax - 1))
    cand = sorted(S, key=lambda s: (abs(s[0] - n), abs(s[1] - want)))
    best = [c for c in cand if c[0] == cand[0][0] and c[1] == cand[0][1]]
    key = (name, n); _rr[key] = _rr.get(key, -1) + 1; pick = best[_rr[key] % len(best)]
    x = wav(pick[2]); semi = n - pick[0]
    if semi:
        r = 2 ** (semi / 12); idx = np.arange(0, len(x) - 1, r)
        x = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in (0, 1)], 1)
    L = int((dur + rel) * SR); x = x[:L].copy()
    if atk > 0: x[:int(atk * SR)] *= np.linspace(0, 1, int(atk * SR))[:, None]
    r0 = int(dur * SR)
    if r0 < len(x): x[r0:] *= np.linspace(1, 0, len(x) - r0)[:, None]
    place(stem, x * (0.35 + 0.65 * vel), at, gain, rev)
def hit(kind, at, gain=1.0, stem="perc", rev=0.35, i=None, pitch=0):
    L = ONESHOT[kind]
    if not L: return
    _rr[kind] = _rr.get(kind, -1) + 1; x = wav(L[(i if i is not None else _rr[kind]) % len(L)])
    if pitch:
        r = 2 ** (pitch / 12); idx = np.arange(0, len(x) - 1, r); x = np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in (0, 1)], 1)
    place(stem, x, at, gain, rev)
def chord(name, notes, at, dur, vel=0.6, gain=1.0, stem="strings", rev=0.35, atk=0.0, rel=0.4):
    for n in notes: note(name, n, at, dur, vel, gain, stem, rev, rel, atk)
def sine_sub(f0, f1, at, dur, gain=0.3, atk=0.05, rel=0.6):
    """Sub-bass layer (the felt 'body' under the orchestra): glide f0->f1 Hz."""
    n = int((dur + rel) * SR); t = np.arange(n) / SR; f = np.where(t < dur, f0 + (f1 - f0) * np.clip(t / max(dur, 1e-3), 0, 1), f1)
    ph = 2 * np.pi * np.cumsum(f) / SR; y = np.sin(ph) + 0.15 * np.sin(2 * ph)
    env = np.clip(t / atk, 0, 1) * np.where(t > dur, np.clip(1 - (t - dur) / rel, 0, 1), 1)
    place("sub", np.stack([y * env, y * env], 1), at, gain, 0.0)

# ================================================================== THE SCORE
D = "D"; HARM = {"Dm": ["D", "F", "A"], "Bb": ["A#", "D", "F"], "F": ["F", "A", "C"], "C": ["C", "E", "G"], "Gm": ["G", "A#", "D"], "A": ["A", "C#", "E"]}
ROOT = {"Dm": "D", "Bb": "A#", "F": "F", "C": "C", "Gm": "G", "A": "A"}
def ostinato(beat0, beat1, chord_name, vel=0.55, inst_lo="cb_spic", inst_hi="cello_spic", gain=1.0):
    """16th-note driving ostinato (root-root-octave-root-fifth-root-third-root), the Think School pulse."""
    r = ROOT[chord_name]; pat = [r + "2", r + "2", r + "3", r + "2", HARM[chord_name][2] + "2", r + "2", HARM[chord_name][1] + "2", r + "2"]
    b = beat0
    while b < beat1 - 1e-6:
        k = int(round((b - beat0) * 4)) % 8; acc = 1.0 if k % 4 == 0 else 0.8
        note(inst_hi, pat[k], bt(b), BEAT / 4 * 0.9, vel * acc, gain * 0.9, "strings", 0.2, 0.08)
        if k % 2 == 0: note(inst_lo, ROOT[chord_name] + "1", bt(b), BEAT / 2 * 0.9, vel * acc, gain * 0.8, "strings", 0.1, 0.08)
        b += 0.25
def thump(at, gain=0.5):
    """Tight trailer-kick body under the acoustic bass drum: 110->45 Hz pitch drop, 140 ms."""
    n = int(0.22 * SR); t = np.arange(n) / SR; f = 45 + 65 * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.09) * np.minimum(t / 0.002, 1)
    place("perc", np.stack([y, y], 1), at, gain, 0.05)
def kicks(beat0, beat1, gain=0.8, taiko_every=4):
    b = beat0
    while b < beat1 - 1e-6:
        hit("kick", bt(b), gain, rev=0.1); thump(bt(b), 0.55 * gain)
        if taiko_every and int(round(b - beat0)) % taiko_every == 0: hit("taiko", bt(b), gain * 0.9, rev=0.3)
        b += 1
def ticks(beat0, beat1, step=0.5, gain=0.25, accel_to=None):
    b = beat0
    while b < beat1 - 1e-6:
        hit("rim", bt(b), gain, rev=0.15)
        s = step if accel_to is None else step + (accel_to - step) * (b - beat0) / (beat1 - beat0); b += s
FREQ = {"D": 36.71, "A#": 58.27, "F": 43.65, "C": 32.70, "G": 49.00, "A": 55.00}
def pulse_bass(beat0, beat1, chord_name, gain=0.35):
    """Think-School engine: 8th-note sub/bass pulse on the root, pumping (ducked on every kick)."""
    f = FREQ[ROOT[chord_name]]; b = beat0
    while b < beat1 - 1e-6:
        n = int(0.5 * BEAT * SR); t = np.arange(n) / SR
        y = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t))
        env = np.minimum(t / 0.008, 1) * np.exp(-t / 0.16) * (0.75 if (b - beat0) % 1 else 1.0)
        place("sub", np.stack([y * env, y * env], 1), bt(b), gain, 0.0); b += 0.5
def offbeat_clicks(beat0, beat1, gain=0.22):
    b = beat0 + 0.5
    while b < beat1 - 1e-6: hit("snare", bt(b), gain, rev=0.2, i=0); b += 1
MOTIF = [("D5", 0, 1.0), ("A4", 1, 1.0), ("F5", 2, 0.5), ("E5", 2.5, 0.5), ("D5", 3, 1.5)]        # the 'Dhanteras' theme
def motif(beat0, vel=0.45, octave=0):
    for n, b, d in MOTIF:
        nn = m(n) + 12 * octave; note("piano", nn, bt(beat0 + b), d * BEAT, vel, 1.0, "keys", 0.55, 1.2)

def compose():
    # ---- BRAND (0-4.8): ticking clock + low tremolo swell + timpani roll into the shutter
    ticks(-4, 0, 0.5, 0.18)
    note("cello_trem", "D2", 0.6, 4.1, 0.5, 0.7, "strings", 0.4, 0.2, atk=2.5)
    hit("timp_roll", bt(-3.0), 0.6, rev=0.4)
    # ---- BEAT 0 (4.8 shutter cut): the first BOOM
    hit("taiko", bt(0), 1.0); hit("kick", bt(0), 0.9); hit("timp", bt(0), 0.9)
    note("tuba_sus", "D1", bt(0), 3.0, 0.8, 0.9, "brass", 0.4, 1.5); note("cb_sus", "D1", bt(0), 9.0, 0.6, 0.8, "strings", 0.3, 1.0)
    sine_sub(36.7, 36.7, bt(0), 9.5 * BEAT * 1.0, 0.22)
    # ---- A (beats 0-9.5): coin in the void, diya rises. Piano theme, soft ostinato fades in, ticking
    motif(0.5, 0.45); motif(4.5, 0.5)
    chord("vln_sus", ["A4", "D5"], bt(0), 9 * BEAT, 0.35, 0.6, "strings", 0.5, atk=1.5, rel=1.0)
    ticks(0, 9.5, 0.5, 0.15)
    ostinato(4, 8, "Dm", 0.35, gain=0.7); ostinato(8, 9.5, "Bb", 0.45, gain=0.8)
    kicks(4, 9.5, 0.6, taiko_every=0); pulse_bass(4, 9.5, "Dm", 0.2)
    # ---- B (beats 9.5-23): macro + electric arcs + diya hero. Full drive.
    hit("taiko", bt(9.5), 0.9); hit("timp", bt(9.5), 0.7)
    ostinato(9.5, 12, "Bb", 0.6); ostinato(12, 16, "Bb", 0.62); ostinato(16, 20, "F", 0.66); ostinato(20, 23, "C", 0.7)
    kicks(10, 23, 1.0)
    for c, a_, b_ in (("Bb", 9.5, 16), ("F", 16, 20), ("C", 20, 23)): pulse_bass(a_, b_, c, 0.32)
    offbeat_clicks(10, 23, 0.25)
    for b in np.arange(11, 23, 2): hit("snare", bt(b), 0.25, rev=0.3)
    chord("vln_trem", ["D5", "F5"], bt(11), 5 * BEAT, 0.45, 0.55, "strings", 0.45, atk=0.4)          # arcs shimmer
    chord("horn_sus", ["F3", "A3", "C4"], bt(16), 4 * BEAT, 0.6, 0.8, "brass", 0.45, atk=0.8)       # diya hero swell
    chord("tbn_sus", ["F2", "C3"], bt(16), 4 * BEAT, 0.55, 0.7, "brass", 0.4, atk=0.8)
    chord("horn_sus", ["E3", "G3", "C4"], bt(20), 3 * BEAT, 0.65, 0.8, "brass", 0.45, atk=0.5)
    sine_sub(43.65, 43.65, bt(16), 4 * BEAT, 0.2); sine_sub(32.7, 32.7, bt(20), 3 * BEAT, 0.2)
    # ---- FLIP (beats 23-27): zero gravity. Everything drops away; high harmonics + glock spin, sub only.
    chord("vln_sus", ["D6", "A6"], bt(23), 4 * BEAT, 0.3, 0.45, "strings", 0.7, atk=0.6, rel=0.8)
    hit("glock_up", bt(23.2), 0.35, stem="fx", rev=0.7); sine_sub(36.7, 36.7, bt(23), 4 * BEAT, 0.25)
    # ---- REVEAL (beat 27): rupee face. Hit, then C section builds to the blast.
    hit("taiko", bt(27), 1.0); hit("timp", bt(27), 0.9); note("tbn_stac", "D2", bt(27), 0.4, 0.9, 0.8, "brass")
    ostinato(27, 31, "Dm", 0.68); ostinato(31, 35, "Bb", 0.7); ostinato(35, 39, "Gm", 0.75); ostinato(39, 42.6, "A", 0.82)
    kicks(27, 42.6, 1.05, taiko_every=2)
    for c, a_, b_ in (("Dm", 27, 31), ("Bb", 31, 35), ("Gm", 35, 39), ("A", 39, 42.6)): pulse_bass(a_, b_, c, 0.36)
    offbeat_clicks(27, 42.6, 0.28)
    for b in np.arange(35, 42.5, 0.5): hit("taiko", bt(b), 0.45, rev=0.25)                      # taiko 8ths drive
    chord("horn_sus", ["D3", "F3", "A3"], bt(27), 4 * BEAT, 0.7, 0.85, "brass", 0.45, atk=0.3)
    chord("horn_sus", ["D3", "F3", "A#3"], bt(31), 4 * BEAT, 0.72, 0.85, "brass", 0.45, atk=0.3)
    chord("tbn_sus", ["G2", "D3"], bt(35), 4 * BEAT, 0.75, 0.85, "brass", 0.4, atk=0.3)
    chord("horn_sus", ["E3", "A3", "C#4"], bt(39), 3.6 * BEAT, 0.8, 0.9, "brass", 0.45, atk=0.2)
    for i, n in enumerate(["D5", "E5", "F5", "G5", "A5", "A#5", "C6", "C#6"]):                   # rising violin line
        note("vln_spic", n, bt(27 + i * 2), 1.8 * BEAT, 0.6, 0.6, "strings", 0.3, 0.1)
    sine_sub(36.7, 36.7, bt(27), 8 * BEAT, 0.22); sine_sub(49.0, 49.0, bt(35), 4 * BEAT, 0.22); sine_sub(55.0, 55.0, bt(39), 3.6 * BEAT, 0.24)
    # fuse (beat 37): the clock accelerates; bijili crackles = brass stabs; strings tremolo crescendo
    ticks(37, 42.6, 0.25, 0.3, accel_to=0.0625)
    for t in (27.4, 27.65, 27.9):
        chord("tbn_stac", ["A2", "E3"], t, 0.25, 0.95, 0.9, "brass", 0.3); hit("taiko", t, 0.8)
    chord("vln_trem", ["A4", "C#5", "E5"], bt(39), 3.6 * BEAT, 0.8, 0.8, "strings", 0.4, atk=1.5, rel=0.05)
    chord("cello_trem", ["A2", "E3"], bt(39), 3.6 * BEAT, 0.8, 0.8, "strings", 0.4, atk=1.5, rel=0.05)
    hit("timp_roll", bt(40.4), 0.9, rev=0.4)
    # silence 29.30-29.50 is carved in the mix (vacuum before the hit)
    # ---- BLAST (beat 43 = 29.5): the BWAAM
    for k in range(3): hit("taiko", bt(43) + k * 0.012, 1.0, i=k)
    hit("kick", bt(43), 1.0); hit("timp", bt(43), 1.0)
    for n in ("D1", "D2"): note("tuba_sus", n, bt(43), 4.0, 1.0, 1.0, "brass", 0.5, 2.0)
    for n in ("D2", "A2", "D3"): note("tbn_sus", n, bt(43), 3.5, 1.0, 0.9, "brass", 0.5, 2.0)
    note("cb_sus", "D1", bt(43), 5.0, 0.9, 0.9, "strings", 0.4, 2.0)
    chord("vln_trem", ["D6", "D#6"], bt(43), 2.5, 0.6, 0.4, "strings", 0.6, rel=1.5)              # the dissonant shimmer
    sine_sub(60, 28, bt(43), 2.6, 0.55, atk=0.005, rel=2.0)                                        # sub drop
    # ---- SMOKE + TITLE (beat 48 = 32.37): theme returns, resolution
    chord("vln_sus", ["D4", "F4", "A4", "E5"], bt(46), 11 * BEAT, 0.4, 0.55, "strings", 0.6, atk=2.0, rel=2.0)
    chord("cello_sus", ["D2", "A2"], bt(46), 11 * BEAT, 0.45, 0.55, "strings", 0.5, atk=2.0, rel=2.0)
    hit("taiko", bt(48), 0.75); hit("timp", bt(48), 0.7); note("tuba_sus", "D1", bt(48), 3.0, 0.7, 0.7, "brass", 0.5, 2.0)
    sine_sub(36.7, 36.7, bt(48), 10 * BEAT, 0.22, atk=0.02, rel=2.0)
    motif(48.5, 0.5); hit("glock_up", 33.9 - 0.2, 0.3, stem="fx", rev=0.8)
    note("piano", "D4", bt(53), 4 * BEAT, 0.45, 1.0, "keys", 0.6, 2.5); note("piano", "A4", bt(53.5), 3 * BEAT, 0.35, 1.0, "keys", 0.6, 2.5)

compose()
# ------------------------------------------------------------------ mix the score (hall reverb, bus balance, vacuum gap)
N = int(DUR * SR); rng = np.random.default_rng(3); L_ = int(3.2 * SR); tt = np.arange(L_) / SR
ir = rng.standard_normal((L_, 2)) * np.exp(-tt / 0.95)[:, None]; ir[:int(0.02 * SR)] = 0
from numpy.fft import rfft, irfft
nf = 1 << int(np.ceil(np.log2(len(SEND) + L_)))
wet = np.stack([irfft(rfft(SEND[:, c], nf) * rfft(ir[:, c], nf), nf)[:len(SEND)] for c in (0, 1)], 1)
wet = irfft(rfft(wet, nf, axis=0) * (1 / (1 + (np.fft.rfftfreq(nf, 1 / SR) / 5000) ** 2))[:, None], nf, axis=0)[:len(SEND)]
wet *= 0.25 * np.abs(SEND).max() / (np.abs(wet).max() + 1e-9)
BAL = {"strings": 0.8, "brass": 0.8, "keys": 0.8, "perc": 1.6, "sub": 1.1, "fx": 0.8}
t = np.arange(len(SEND)) / SR
gap = 1 - np.clip((t - 29.30) / 0.03, 0, 1) * np.clip((29.497 - t) / 0.003, 0, 1)     # vacuum: true silence 29.30-29.50
os.makedirs(os.path.join(HERE, "stems"), exist_ok=True)
def write(p, x):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a", "pcm_f32le", p], input=x[:N].astype(np.float32).tobytes())
total = wet * 0.9 * gap[:, None]
for k, x in STEMS.items():
    y = x * BAL[k] * gap[:, None]; total += y; write(os.path.join(HERE, "stems", "score_" + k + ".wav"), y)
write(os.path.join(HERE, "stems", "score_reverb.wav"), wet * 0.9 * gap[:, None])
write(os.path.join(HERE, "score.wav"), total)
print("score peak", np.abs(total[:N]).max())
