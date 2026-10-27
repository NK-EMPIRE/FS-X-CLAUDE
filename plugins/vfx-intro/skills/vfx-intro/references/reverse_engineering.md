# Reverse-engineering a reference intro

Goal: understand *exactly* how it was made and why it works, then plan a version that beats it.

## 1. Extract
```bash
python scripts/tools/analyze_reference.py ref.mp4 work/ref            # shots, per-second stats, audio hits, sheets
python scripts/tools/analyze_reference.py ref.mp4 work/ref --start 23.6 --end 26   # dense 10 fps sheet of a key moment
```
Cut detection is a guide: confirm on the sheets (fast whip-pans and flashes can fake cuts; dissolves/match-cuts can hide them). For several references, analyse each and compare side by side.

## 2. Breakdown template (fill for every shot)
| Field | Look for |
|---|---|
| Time / duration | in-out seconds; pace (avg shot length; Think School style ~1.5-4 s, hero moments longer) |
| Camera | move (push, pull, orbit, crane, whip, dolly-zoom, locked), speed curve (ease, snap), lens feel (wide 18-28 / normal 35-50 / macro 70-100), DOF depth, height (top-down, eye, low/hero), handheld shake? |
| Subject | hero object, scale cues, material (metal type, roughness, patina, relief depth), surface detail at macro |
| Light | key direction + hardness (raking = relief), rim colour, fill level, practical glows, volumetrics, background (void, gradient, environment) |
| Motion / FX | what transforms (emboss, morph, crack, shatter, melt, dissolve), physics (gravity or zero-g), particle count/size, speed ramps (slow-mo windows), energy (arcs, sparks, embers) |
| Transition | hard cut, match-cut (shape/position match), flash frame, whip, light-wipe, push-through (camera flies into an object), morph |
| Colour | palette (sample rgb from report.md), contrast, saturation, shadow tint (teal?), highlight tint (warm?), halation/bloom, grain, CA, vignette, aspect ratio (2.39 letterbox?) |
| Title | font class (tall condensed / serif / mono), size, tracking, materials (gold gradient, bevel, glow), reveal (blur-to-focus, scale settle, light sweep), hold duration, background |
| Sound | hits at (s), whooshes, risers, sub drops; which visual beats they sync to |

## 3. Infer the build
For each shot write: *Blender*: objects, materials, sim/FX, camera path, fps; *AE*: remaps, flashes, overlays, grade, title. Note what is CGI vs 2D comp. Estimate render frames.

## <a name="beyond"></a>4. Go beyond (mandatory list, pick 5-10)
- **Physical truth**: real displacement relief (not bump-only), raking key to reveal it, correct metal (Metallic 1, roughness variation, cavity patina).
- **One continuous camera** through a transformation (no cut) where the reference cuts.
- **Centre-origin events**: blasts/reveals from the true centre of the subject, debris streaming *past* the lens (ring around the lens, never down the axis).
- **Speed ramp**: 48 fps source for the hero moment, slow on the impact only, then real speed (no frozen-looking holds).
- **Match-cuts**: brand intro -> push into a logo detail (e.g. a lens dot) -> flash -> CGI.
- **Energy layer**: arcs/sparks/embers timed to sound hits; crackle camera kicks.
- **Title integrated into the world**: emerges from the smoke/light of the last shot, shine *inside* the letters, warm backdrop not a black card.
- **Grade discipline**: one look across all shots; chromatic aberration eased off during bright white events (else red/cyan fringe).
- **Micro detail for macro shots**: dust motes in the key light, faint haze, fingerprints/scratches at very low strength.
- **Sound design map**: list exact sync points even if audio comes later.

## 5. Output to the user
A short report: what the reference does (shot table), why it works (3-5 principles), the build plan, the beyond-list, and the 2-3 risks. Then the storyboard sheet.
