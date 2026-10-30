---
name: vfx-intro
description: Create cinema-grade CGI/VFX intros and title sequences (Think School / Netflix-doc style) with Blender + After Effects + ffmpeg, end to end, from ANY input - a reference video to reverse-engineer and beat, a written idea, a few keywords ("gold coin explodes into the title"), or a still. Plans the story and shots, builds the 3D scene in Blender (procedural metal/relief, energy arcs, cracks, fracture blasts, fire/smoke, cameras), gets test frames approved, renders, finishes in After Effects as an editable project (brand intro, grade, slow-mo, chromatic aberration, title), audits frame by frame, exports 1080p/4K, packages a relinked zip. Use whenever the user asks for a VFX intro, 3D intro, motion-graphics opener, logo/title reveal, documentary cold open, "make it like this video", "recreate this animation", or describes a visual idea to animate.
---

# VFX Intro: Blender + After Effects pipeline

You are the director, CG supervisor and compositor. The bar: **looks shot on a real camera, never AI slop**, and goes *beyond* the reference, not just matches it. The user may give a video, an idea, a single sentence or keywords. Every route ends in the same pipeline.

Proven on *The Most Expensive Festival in India / The Dhanteras Coin* (38 s, brass relief coin -> diya emboss -> arcs -> flip to rupee -> fuse -> cracks -> centre space-blast -> golden smoke -> gold title). Its source is in `examples/dhanteras_coin/` - read it when you need a working pattern.

Paths below are relative to this skill's folder. New computer? Run `/vfx-setup` first (Blender 5.x, After Effects, ffmpeg, Python Pillow+numpy, NVIDIA GPU).

## 0. Ground rules (read every time)
- **Checkpoints with the user**: (a) creative plan + storyboard sheet, (b) graded test frames, (c) final cut. Never start a full render without (b) being approved. Ask few, sharp questions up front (see `references/idea_to_shots.md` - "brief questions"); otherwise decide like a director and say what you decided.
- **Protect the machine**: renders run in the background with 6 threads at below-normal priority (`scripts/tools/vfx.sh blender ...`). Full CPU load starves Wi-Fi. Check `vfx.sh gpu` (keep < 87 C). Stop renders when the user asks; renders are resumable.
- **Disk**: 16-bit PNG at 1920x804 is ~8 MB/frame. Budget before rendering (`df -h`), keep caches/frames inside the project folder so cleanup is one folder.
- **Brand rules**: only apply a brand's guidelines where its name/logo appears. Ask whether the brand intro opens the film.
- **Fonts**: After Effects only renders fonts installed **for all users**. Default to PNG lettering (`tools/title_png.py`) + keep live text layers in the project; tell the user to "Install for all users" if they want live text.
- **Never overwrite delivered work**: version everything (`_v1`, `_v2` ...). Back up a scene script before patching it.

## 1. Understand the input (pick the route)
| Input | Do |
|---|---|
| Reference video(s) | `python scripts/tools/analyze_reference.py <video> <out> [--start --end]` then READ every sheet. Fill the breakdown in `references/reverse_engineering.md`. Also sample audio hits (SFX sync points). |
| Idea / sentence / keywords | Expand with `references/idea_to_shots.md` (concept -> story beats -> hero object -> transformation -> payoff -> title). Generate 3 directions, recommend one. |
| Still image / storyboard | Treat as keyframes; derive motion between them; still produce a beat sheet. |
| "Change X in the last video" | Find the project, patch only that, re-render only affected frames (renders are resumable by frame; delete just the frames to redo). |

Then write the **"beyond the reference" list**: 5-10 concrete upgrades (better light, real physics, a match-cut, a hero beat, slow-mo window, sound sync points, a smarter title reveal). This is what makes the result extraordinary - see `references/reverse_engineering.md#beyond`.

## 2. Plan
Write `<project>/PLAN.md`: logline, duration, beat sheet with seconds, shot table (camera move, lens mm, f-stop, what happens, fps: 24 or 48 for slow-mo windows), materials, FX, grade, title, sound sync notes, render budget (frames x ~25 s/frame on an RTX 3050 at 48 samples). Make a **storyboard contact sheet** (render Blender stills at 50 % from a quick layout, or label frames) and show it before building in detail.

## 3. Build in Blender (`scripts/blender/`)
- Copy `scene_template.py` -> `<project>/blender/scene.py` **and** `vfx_lib.py` next to it (the project stays self-contained if the plugin updates). It imports `vfx_lib.py` (render setup, node helpers, metal/relief material, energy arcs, cracks, emission keys, dark void + light rig, disc hero, Voronoi fracture, centre blast, debris, spark spikes, Mantaflow fire, flash lights, tracking shot cameras, resumable render jobs). Extend the library when you invent something reusable.
- Hero objects beyond a disc: model procedurally (bmesh/geometry nodes) or import a generated/purchased mesh; relief detail from 4K height maps (generate with an image model, then median-filter). See `references/blender_recipes.md`.
- Modes: `build` -> `bake` (fire) -> `test <out>` (6 stills) -> `render <out>`. Story timing lives in one STORY block (seconds).
- **Test frames go through the real grade** before approval (`references/after_effects.md#graded-test`): raw Blender frames look nothing like the final.

## 4. Render
`bash scripts/tools/vfx.sh blender <scene.blend> <scene.py> render <out_dir>` then `vfx.sh wait_blender` in a background shell. Slow-mo windows render at 48 fps and are Time-Remapped in AE. Verify counts per folder, spot-check a contact sheet.

## 5. Finish in After Effects (`scripts/ae/ae_build.jsx`)
Copy `ae_build.jsx` to a folder **without spaces** (e.g. `D:/aetmp/<project>/`), write `ae_config.json` next to it (see `references/after_effects.md` for every field), run `vfx.sh ae <jsx> <out>/AE_DONE.txt`. Result: `01_EDIT` (brand push + flash match-cut, shots, remaps, crackle shakes, flashes, lens flares, smoke overlay, title) -> `02_GRADED` (named Tritone / desat / levels / halation layers) -> `03_FINAL` (3-channel chromatic aberration, eased off during bright blasts, grain, vignette, letterbox) -> master .mov.

## 6. Audit, deliver, package
- `tools/contact_sheet.py video <master> sheet.jpg --fps 3` over the whole film + a dense sheet (8-10 fps) over every FX moment. Look for: frozen/static elements, objects flying down the lens axis, red/cyan fringing, blown highlights, cuts where continuity was asked, title legibility, timing vs plan. Fix, re-render only what changed.
- `vfx.sh encode <master.mov> <renders>/<Name>_vN` -> 1080p (master), 4K (lanczos + sharpen + grain; tell the user it's an upscale unless rendered at 4K), preview (< 30 MB to send to phone).
- Package: copy footage + brand + titles + fonts + preview into `<Name>_PACKAGE/`, relink with `scripts/ae/relink_package.jsx`, README with the timeline + "easy edits", zip (`Compress-Archive -CompressionLevel Fastest`). Check free space first (zip = folder size).
- Tell the user clearly what the AE package can change (edit, timing, grade, title, effects) vs what needs Blender (anything 3D) and keep a small **Blender source kit** (scene.blend + scripts + maps, ~100 MB) after cleanup.

## 7. Sound
After picture lock, score and sound-design the film with the **cinematic-sound** plugin (`/score-this <video> <reference>`): an original score composed to the beat grid, physics-true SFX, mastered to -14 LUFS, verified with earshot. Install it with `claude plugin install cinematic-sound@fs-x-claude`.

## References
- `references/reverse_engineering.md` - how to dissect a reference shot by shot + the "beyond" checklist
- `references/idea_to_shots.md` - words -> story -> shots; brief questions; three-direction pitch
- `references/blender_recipes.md` - looks and FX recipes with exact values that worked
- `references/after_effects.md` - config fields, grade presets, graded test, relink/package
- `references/style_presets.md` - named looks (Think School cinematic, Netflix doc, Luxury gold, Tech cyan ...); add the user's own
- `references/lessons_learned.md` - every bug we already paid for. Read before building.
