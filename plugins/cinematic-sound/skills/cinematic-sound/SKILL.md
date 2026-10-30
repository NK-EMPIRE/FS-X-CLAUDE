---
name: cinematic-sound
description: Hollywood / Think School-level sound for a finished picture (CGI intros, documentary cold opens, trailers, motion graphics). It analyses a reference film's audio, composes an ORIGINAL score to the picture's beat grid with real recorded instruments (orchestra, piano, taiko, timpani, a pumping sub-bass), designs the SFX for the scene's physics (a vacuum in space, a room, the outdoors), mixes and masters to -14 LUFS, verifies with earshot, and muxes the 1080p/4K/preview. Use whenever the user asks for BGM, a score, music or sound design, SFX, "make the audio like <reference>", "Think School / Bhutan / Hollywood level sound", immersive or Atmos-style audio, or complains that the music doesn't fit, is too quiet, or sounds generic.
---

# Cinematic sound: score + sound design + mix

You are composer, sound designer and re-recording mixer on a $1M film. The bar: the audience *feels* the picture. Music and
SFX are written to the frame, not laid under it.

Proven on *The Dhanteras Coin* (38.7 s). Its full working code is in `examples/dhanteras_coin/`: `score.py` (an original
104.45 BPM D-minor hybrid trailer score), `mix.py` (space SFX + score mix) and `reference_blueprint.png` (the Bhutan
Bitcoin analysis it was matched against).

## 0. Ground rules
- **You cannot hear.** Judge with numbers and earshot (`earshot match / rank / find / timeline / realness`); say what was measured and what the user should listen to. Install earshot globally if it's missing (github.com/Leonxlnx/earshot: venv + torch CPU from `--extra-index-url https://download.pytorch.org/whl/cpu`).
- **Physics first.** Space = no air: low-pass every whoosh (~320 Hz, "felt pressure"), no landing/foley clicks, tonal metal resonance, sub-bass impacts, and silence used as a weapon (cut everything for 0.2 s before the big hit). Rooms and outdoors get matching ambience and reverb.
- **Credits:** search and preview for free (LQ preview URLs plus earshot rank). Download only the finalists. Signed Epidemic URLs expire in ~1 min: fetch immediately, in parallel. Prefer MP3 for SFX on slow lines.
- Version every mix (`mix_vN.py`); never overwrite a delivered file.

## 1. Analyse the reference (`scripts/analyze_audio.py ref.mp4 out/`)
It returns the tempo, frequency layers over time (sub/bass/mid/high), the onset density per section, the cuts against the beat grid, and the loudness range, plus a blueprint PNG. Then run `earshot timeline ref.mp4` for genre/mood words per section.
Think School pattern (Bhutan Bitcoin): 103 BPM driving techno/drum-and-bass + orchestral percussion, a constant sub/bass floor of ~40 dB, LRA ~3 LU, two "breath" dips (3 s, 34 s) before surges, the densest section last, then a sub-bass outro.

## 2. Map the picture
List every story beat with its time (cuts, transformations, flips, hits, title). Choose the tempo so the 2-3 biggest moments fall on beats (e.g. 43 beats between the brand cut and the blast gives 104.45 BPM). Write the cue table in PLAN.md: time, picture, music, SFX.

## 3. Compose (`examples/dhanteras_coin/score.py` = the engine + a full score)
- **Sampler:** real CC0 instruments from VSCO-2-CE (github.com/sgossner/VSCO-2-CE). Download only the needed folders file by file from raw.githubusercontent (a partial git clone breaks on slow lines). Strings spic/sus/trem, horn/trombone/tuba sus+stac, upright piano, timpani, giant ethnic drum (taiko), bass drum, snare clicks, glock glisses.
- **Engine pieces:** `ostinato()` (16th-note string drive), `kicks()` + `thump()` (acoustic bass drum + a 110→45 Hz trailer-kick body, needed for a clear pulse), `pulse_bass()` (8th-note pumping sub on the chord root), `offbeat_clicks()`, `ticks()` (an accelerating clock for a fuse/countdown), `motif()` (a 4-5 note theme on piano, stated early and returned under the title), `chord()` swells, `sine_sub()` drops, and a hall reverb send.
- **Arc:** a quiet theme, then the drive, then a drop to near-silence for the magic moment (flip/reveal), then a hit and a bigger drive, then accelerating tension, then **0.2 s of silence**, then the tutti BWAAM (taiko ×3, low brass, braam, a 60→28 Hz sub drop), then the theme as the resolution.
- Stems: strings, brass, keys, perc, sub, fx, reverb (for the Premiere / Resolve hand-off).

## 4. Design and place the SFX (`examples/dhanteras_coin/mix.py`)
`cue(bus, name, src0, src1, at, db, pan, fi, fo, rev, width, pan_to, lp)` places a slice on the frame: transient or peak on the event (measure each file's onset and peak first), constant-power auto-pan, stereo width, reverb send, and `lp` for the vacuum. Buses: music, amb, sfx, impact. Sidechain the music under impacts (gentle, max ~-3 dB, so the music never steps back) and carve a pre-hit suck-out.
Verify every pick with `earshot match file "what it should be"`. Anything under "plausible" gets replaced (we caught firecracker "pops" that were really "glitch / hi-hat", and metal hums that were "a saw / a printer").

## 5. Master and deliver
`acompressor (2.2:1) → alimiter → loudnorm I=-14 TP=-1.5 LRA=5`, then `-af volume=-1dB` at the AAC mux (the AAC encoder overshoots). Mux with `-c:v copy` onto the 1080p, 4K and preview (keep the preview under 30 MB for phones).
QA: `earshot timeline film.mp4` must show the intended genre per section, a beat grid (pulse clarity ≥ 0.15) and hits on the key cuts (±60 ms). Compare against the reference blueprint.

## References
- `references/lessons.md`: every mistake already paid for.
