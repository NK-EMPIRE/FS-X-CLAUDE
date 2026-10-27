# After Effects finishing

## Running scripts
`AfterFX.exe -r <path>` with a path **without spaces** (keep jsx + config in e.g. `D:/aetmp/<project>/`). The script closes any open project first (an unsaved-changes dialog blocks headless runs). ES3 only: no `const/let`, arrow functions, `JSON` (config is read with `eval("(" + text + ")")`). Use matchNames (`ADBE Glo2`, `ADBE Tritone` ...) never display names. Moving an effect (`moveTo`) invalidates references: re-fetch by index. Don't remove the default Time Remap keys ("property hidden" error).

## ae_config.json fields
```json
{ "aep_name": "Name_v1", "out_dir": "D:/aetmp/proj/out", "width": 1920, "height": 1080, "fps": 24, "duration": 38.7,
  "brand": { "file": ".../brand.mp4", "end": 4.8, "target": [921, 320], "label": "selfie lens" },
  "shots": [ { "name": "S1_push", "dir": ".../frames/S1_push", "fps": 24, "at": 0.0, "out": 5.5 },
             { "name": "S8_burst48", "dir": "...", "fps": 48, "at": 24.7, "out": 25.85,
               "remap": [[24.7, 0], [25.3, 0.3], [25.85, 0.999]], "scale_keys": [[24.7, 100], [25.85, 112]],
               "shake": {"t0": 24.7, "t1": 25.7, "amp": 16} },
             { "name": "S8_tail", "dir": "...", "fps": 24, "at": 25.85, "out": 29.2, "hold_to_end": true },
             { "name": "S7_fuse", "...": "...", "pops": [22.6, 22.85, 23.1] } ],
  "flashes": [ { "t": 24.72, "peak": 60, "len": 0.3, "name": "FLASH burst", "flare": [840, 560] } ],
  "smoke_overlay": { "t0": 26.6, "opacity": 20 },
  "title": { "start": 27.5, "darken_behind": [0.16, 0.08, 0.03], "use_live_text": false,
             "gold_top": [1, 0.95, 0.84], "gold_bottom": [0.5, 0.36, 0.2],
             "lines": [ { "text": "EXPENSIVE", "png": ".../T_MAIN.png", "font": "Theblock-Regular", "size": 330, "y": 470, "main": true },
                        { "text": "THE MOST", "png": ".../T_TOP.png", "font": "OpenSauceSans-SemiBold", "size": 30, "tracking": 700, "y": 282, "in": 0.7 } ] },
  "ca": 0.35, "ca_off": [24.4, 27.6], "grain": 5, "letterbox": 138, "fade_out": 0.8,
  "grade": { "high": [1,0.94,0.84,1], "mid": [0.6,0.5,0.36,1], "shadow": [0.02,0.055,0.07,1], "tritone_mix": 72, "saturation": -14, "halation": 0.55 } }
```
All shot/flash/title times are in **CGI time** (seconds after the brand intro); the script adds the brand length.

## <a name="graded-test"></a>Graded test frames
Raw Blender stills are flatter/brighter than the final. Before approval: open the current .aep, import the test stills as a sequence (scale 200 % if rendered at 50 %), disable the SHOT layers under them, render that span of `03_FINAL` (default output module -> mov, then ffmpeg tile). Or run ae_build.jsx with `render:true` on a config whose shots point at test sequences (copy each still N times as name_0000..).

## Title
PNG lettering (`tools/title_png.py`, TheBlock 400 px main word, Open Sauce 46 px tracked 0.6 above/below) gives the exact font even when AE can't. The precomp holds only lettering, so the CC Light Sweep shine stays inside the letters. Gold = Ramp matte (top highlight -> bronze bottom) + Bevel Alpha + Drop Shadow + Glow. Reveal: blur 60 -> 0 in 0.9 s, scale 108 -> 100, small lines fade + tracking in. For an editable title the user must install fonts for all users; `title_build` pattern: live text + per-layer Ramp + Set Matte (self) + controls null with Color/Slider controls linked by expressions.

## Grade presets
See `style_presets.md`. Layers are named and separate so the user can tweak any one in the AE UI.

## Packaging
Copy every footage folder + brand + title PNGs + fonts + preview into `<Name>_PACKAGE/Footage/...`, open the .aep and `replaceWithSequence` / `replace` each item to the package paths (keep `conformFrameRate`), save as `<Name>_PACKAGE/<Name>.aep`, write README (timeline + easy edits), zip.
What the package can change without Blender: cuts, timing, slow-mo, grade, flashes, CA, grain, title text/look, adding SFX/music. Anything in 3D (camera angle, object, materials, blast physics) needs the Blender source kit.
