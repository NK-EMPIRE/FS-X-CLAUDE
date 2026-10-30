---
name: fs-color-grade
description: Professional, natural colour grading that recreates a reference video's look on the user's footage, plus a one-click .cube LUT of the finished grade for editors. It measures the reference and the footage (background hue, skin, brand colours), builds a global creative look the way a colourist does in curves (split tone, hue vs sat skin rescue, density, luma vs sat), finishes it in Premiere Pro Lumetri through the Premiere MCP (or Resolve/ffmpeg), proves it with numbers and review sheets, renders 4K at the right bitrate, and bakes every setting into one LUT. Use whenever the user asks to colour grade or colour correct a video, "match this reference / make it look like <video>", teal-orange / moody / cinematic look, fix skin tones, make a LUT or "colour preset", or share a grade with an editor, or complains a grade looks painted, AI, too saturated, too dark or unnatural.
---

# FS colour grade: reference to natural pro grade to one-click LUT

You are the senior colourist. The bar: a real pro graded it. Skin looks like skin, the background carries the mood, the
brand colours are untouched, and nobody can point at an edge, a band or a "painted" area. Ask before you guess; never
render or deliver without the user's OK.

Proven on the FirstSelfie *Festival Intro* (7:06, 4K 25p, 8-bit H.264): a moody teal look copied from a reference's left
side, a natural face, and the red logo preserved. Settings, numbers and LUTs are in `examples/firstselfie_festival_intro/`.

Scripts (`scripts/`, Python 3 + numpy + Pillow + ffmpeg): `grade_measure.py`, `build_look.py`, `bake_lut.py`,
`make_preset.py`, `sheets.py`, plus `fsgrade.py` (helpers). The Premiere ExtendScript recipes are in
`references/premiere_mcp.md`, the colourist method in `references/pro_method.md`, and the mistakes not to repeat in
`references/lessons.md`. Read lessons.md before you start.

## 0. Brief (one message, then wait)
Get or confirm:
- the footage path, the reference path and the **exact reference range** (e.g. 45–58 s);
- **which part of the reference to copy** (e.g. "only the left-side teal and the face, ignore the red");
- **colours that must not change** (logo, product, brand), as hue plus where they are;
- the tool: Premiere via MCP (default, cheap), DaVinci Resolve free (manual or computer use, which costs more), or ffmpeg-only;
- the deliverable: graded render, LUT for an editor, or both.

Then give a short plan and the cost (in time and credits) before doing anything.

## 1. Measure, don't eyeball
`python grade_measure.py --ref REF.mp4 --ref-range 45-58 --src ROUGH.mp4 --out work/ --bg-zone left --brand-hue 6`
This grabs frames decoded as **Rec.709**. ffmpeg's default 601 matrix shifts hues by about 5°, so never trust a plain `ffmpeg -i x.mp4 f.png`.
It prints the background, skin and brand values per frame, skips fades and frames without a face, and writes `targets.json`.
Look at the reference and source frames yourself too.

Write down the gap: background hue, sat and luma; skin hue, sat and luma; the shadows percentage. Then decide **how far** to go:
- a reference is usually graded harder than a client wants (the FirstSelfie reference had teal sat 0.89 and skin sat 0.50);
- we shipped teal sat 0.46 and skin sat 0.26–0.37, because the user wanted "natural" and the mood came from hue and density, not from saturation.

## 2. Balance first (Lumetri Basic Correction)
Do exposure and white balance first, on scopes:
- highlights under ~90 IRE (practicals like lamps may clip);
- skin on the vectorscope skin line (target hue **8–14°**, a natural warm brown);
- a bit of contrast with soft, slightly lifted (filmic) blacks;
- Shadows up so faces under caps and hair aren't swallowed.

Rule: **the graded face is never darker than the rough cut's face.**

## 3. The creative look: global only, no keys or masks
`python build_look.py --targets work/targets.json --out Look.cube --preview "work/src_*.png" --intensity 1.25`
Defaults are FirstSelfie Moody Teal v1, which is bit-exact with what we shipped. The building blocks, all smooth and wide (see pro_method.md):
- RGB-curve split tone;
- hue vs sat (background up; skin rescue orange ×1.16, red ×1.08);
- luma vs sat (clean blacks);
- hue vs luma density (background −8 %, orange −4 %).

Tune with `--set split=0.8 bg_sat_gain=0.25 ...`. Never write a selective HSV "paint" LUT. It bands, haloes and looks AI (the first FirstSelfie grade was rejected for exactly that).
Load the cube in **Lumetri > Creative > Look > Browse** (the user clicks this; scripts can't set the Look). Look Intensity 100–150.

## 4. Finish in Premiere (via the MCP) and judge like a human
Set the sliders by script (`references/premiere_mcp.md` has the property indices), export 6 frames across the timeline, then:
- `grade_measure.py --frames ...` to get the numbers;
- `sheets.py grid / zoom / side` for the before/after grid, the face zoom (2×) and graded vs reference.

**Read every sheet yourself.** Check:
- the face: too orange or saturated? too dark? is the under-cap forehead going navy?
- the blacks: crushed or coloured?
- the logo hue;
- the background edges and gradients: banding?

Fix with small slider moves, one at a time:
- skin too orange → Temperature −2 to −4, Tint +3, Saturation 105;
- dark or cool eye sockets → Shadows +6, Blacks +3, or less Look Intensity.

Don't use Vibrance: −14 dulled the red logo (sat 0.79 → 0.71). Re-measure after every move.
Show the user the sheets plus a short table of the changes and the numbers, and ask before rendering.

## 5. Render (after approval)
`python make_preset.py --fps 25 --mbps 50 --out FS_H264_4K25_50Mbps.epr`, then encode via `app.encoder.encodeSequence` (premiere_mcp.md).
Premiere's "Match Source – High bitrate" preset is a **10 Mbps 1080p** preset, and gave a soft 4K render. Always check with ffprobe: resolution, fps, bitrate ≥ 40 Mbps for 4K, full duration, audio present.

QA:
- 200 % crops of fabric and hair against the rough cut;
- re-measure the render frames (decoded as 709); they must match the Premiere frames within about 1/255.

## 6. One-click LUT for editors (`bake_lut.py`)
The editor usually has the 50 GB final timeline and you only have the rough cut, so ship the grade as a file:
1. Back up the .prproj. Then `bake_lut.py identity --out identity_65.png`.
2. Point the graded clip at the PNG with `projectItem.changeMediaPath(png, true)`, export one frame, and **restore the original path immediately**. Check the sequence duration afterwards.
3. `bake_lut.py extract graded_identity.png --out <Name>_FINAL.cube`.
4. `bake_lut.py verify --cube ... --before rough709.png --after premiere_graded.png`: the mean error must be < 1.5/255 (we got 0.8). Also test the file with `ffmpeg -vf lut3d=...` to prove that other apps parse it.
5. Optionally `bake_lut.py resize --size 33` for a small copy; it's exact.

A LUT can't carry masks, vignette, sharpen or noise, so say so if the grade uses them.

## 7. Deliver
Make a FINAL DELIVERY folder containing:
- the graded 4K render;
- `<Name>_FINAL.cube`;
- 2 before/after JPGs and 2 graded 4K stills;
- `HOW TO APPLY THE GRADE.txt` (from `templates/HOW_TO_APPLY.txt`).

The guide tells the editor:
- **Input LUT** slot, other sliders at default, or save it as a Lumetri preset for one click;
- footage only, not graphics;
- apply once;
- same camera, Rec.709.

Send the small files with SendUserFile. Then offer cleanup: test renders, work frames, the AE/Premiere cache. Top-level cache folders may be blocked by safety rules, so tell the user how to empty them.
