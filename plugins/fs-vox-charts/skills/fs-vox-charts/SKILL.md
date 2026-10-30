---
name: fs-vox-charts
description: Build FirstSelfie "Vox-style" editorial data-chart animations in After Effects, scripted and rendered headless at 4K — cream paper background, serif headline with an italic keyword and orange highlighter, hand-rough bars/rings/pies/lines, Bodoni counters, word-by-word reveals, grain + 12 fps posterize, plus SaaS-speed set-pieces (question burst, timeline, per-minute clock, video-progress counter, select-and-cover call-out). Use whenever the FirstSelfie channel (or the user) asks for "Vox charts", "walks charts", "FS VOX charts", a graph/stat/number animation for a script line, a continuation of an existing V-chart, or new chart shots synced to a voiceover.
---

# FS VOX CHARTS

A kit + workflow for making new chart shots in the FirstSelfie Vox style. It reproduces the **style system**, not any previous
output: every job gets its own data, layout and timing from the script and the voiceover.

Files (all under this skill folder):
- `kit/fs_vox_kit.jsx` — the After Effects library (`VOX.*`): paper BG, headline, type reveals, easing, charts, call-outs, set-pieces, 4K scaler.
- `kit/job_template.jsx` — a working job showing every building block. Copy it per job; never edit the kit for one job.
- `tools/word_times.py` — word-level VO timings (faster-whisper).
- `tools/render.sh` — aerender every comp at 4K + contact sheets + 1080 review copies with the VO.
- `tools/package.sh` — package folder (renders, review, fonts, scripts, README) + zip.
- `tools/selftest.jsx` — builds the template at 1080 into %TEMP% to prove the kit runs.
- `reference/STYLE.md` — the look (colours, type, layout grid, motion rules). Read before designing.
- `reference/RECIPES.md` — which chart for which data/line, the set-piece timings, and every gotcha already hit. Read before building.

## Workflow (do not skip steps — the user's rule: "plan, test, then render; don't do anything blindly")

1. **Understand the ask.** Get from the user, per shot: the exact script line(s), the data, which existing shot it continues
   (if any), and any sketch/reference. Find the line in the script file and in the rough-cut transcript. If a number,
   wording or placement is ambiguous, ask before building. Restate your understanding when the user asks for that, and
   build nothing until they say go.
2. **Time it to the VO.** `python -I -X utf8 tools/word_times.py "<roughcut.mp4>" <start> <dur>` around each line
   (windows ≤ 30 s). Comp start = a beat before the first word; comp end = just before the next line. Every key moment
   (number lands, label appears, highlight swipes) sits on the spoken word, 0–2 frames early.
3. **Design on paper first** (pick from RECIPES.md): one idea per shot, one hero element, orange for the point, cocoa/grey
   for context. Continuation shots start on the exact last frame of the shot they continue (`VOX.TOFF = -3` rebuilds it
   already finished) and end on something the next shot can start from (blank page, a dot, …). Check the numbers add up.
4. **Build.** Copy `kit/job_template.jsx` to `<project>/AE/scripts/build_<job>.jsx`, set `JOB` (copy the logo into
   `<package>/Footage/logo/` first and point `JOB.logo` + `JOB.aep` into the package folder), write the comps, run
   `"C:/Program Files/Adobe/Adobe After Effects 2026/Support Files/AfterFX.com" -r "<abs path>"`, read `vox_build_log.txt`.
   Comp names: `V<nn>_<WHAT>_<mmss>-<mmss>` (VO window). Always `VOX.finish(c)` last in each comp.
5. **Test.** Render (`tools/render.sh`), read every contact sheet, compare against the neighbouring existing shots and the
   VO. Look for: clipped/overlapping text, highlighter damage, wrong font, dead air, numbers not landing on the word,
   layout imbalance. Fix and re-render; never send the first pass unchecked.
6. **Deliver.** 4K masters + 1080 VO review copies + editable .aep + fonts + README, zipped (`tools/package.sh`). Send the
   review copies (render) and the zip (attach). In the message: what each shot does with its VO time, decisions you made
   on your own, and anything not verified.

## Hard rules
- Style = `reference/STYLE.md`. Brand orange `#FF6B00` is the only accent. No gradients, no glow, no bounce/overshoot.
- 4K: `res: 4`. Author in 1920×1080 units; the kit parents everything to `SCALE_4K`. **Never multiply effect values by 2
  on parented layers** (AE already scales them); only the unparented paper BG uses K.
- Don't modify the user's original files or earlier deliverables; new work goes in new comps/files.
- Ask before spending paid credits. No real trademarks/logos except FirstSelfie's.
- Sources: footer `Source: X · to verify` until the user confirms the source.
