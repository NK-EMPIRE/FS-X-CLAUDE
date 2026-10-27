# Lessons learned (each one cost a re-render)

## Blender
- OptiX must be selected explicitly; CPU fallback is ~17x slower.
- Blender 5: `action.fcurves` is gone -> `anim_utils.action_get_channelbag_for_slot(action, slot).fcurves` (`vfx_lib.fcurves`). Remove keyframes from the end, re-indexing each time.
- Fluid bake headless: frame 1, deselect all, select + make the domain active, `free_all` then `bake_all` in a temp_override. A bake that finishes in < 1 s baked nothing (check one cache file per frame). Moving the emitter requires a re-bake into a new cache folder.
- `read_factory_settings` wipes the scene: only in `build` mode.
- Saving can leave `file.blend@` on Windows: use `save_as_mainfile`.
- Camera rotation keys between two aims drift off target: use Track-To on an animated focus empty.
- Cap faces above a relief grid cause blotchy "camo": `cap_ends=False`.
- Back face of a flipping object: rotate (pi, 0, pi) or the relief reads upside down.
- Flash/blast lights need explicit 0 keys at t=0 or they leak into earlier shots.
- Blast origin at an edge looks wrong: centre it (fire emitter, light, shards, camera targets).
- Shards flying along the lens axis look frozen. Aim the few camera-bound shards at a ring around the lens.
- Shard emission 30 -> blown white mush after grading. Peak 2-4, cool in ~1.4 s. Too-large debris reads as clutter; many small + 3 big.
- Slow shards + 0.5x slow-mo = frozen frame. Slow-mo only the impact (~0.6 s), then real speed; add a 100 -> 112 scale push.
- Full-load renders can drop Wi-Fi: 6 threads + below-normal priority. GPU ~54-60 C at 100 % is normal on an RTX 3050 laptop.
- The 3D title model got in the camera's way and users preferred AE type: do titles in AE.

## After Effects
- `-r` script paths with spaces fail silently; an open project's save dialog blocks the run.
- Per-user fonts render as a serif fallback: PNG lettering or install for all users.
- Effects referenced after `moveTo` are invalid. Time Remap default keys must stay.
- `applyTemplate("PNG Sequence")` may not exist: use the default output module + ffmpeg.
- Chromatic aberration on bright white shards makes red/cyan fringes: ease CA to 15 % during blasts.
- A title over a black card felt disconnected: let it emerge from the last shot's smoke with a warm darken layer.
- Light sweep on a precomp that contains a backdrop runs across the background: keep the precomp letters-only.

## Workflow / user
- Show graded test frames, not raw renders: colour judgements on raw frames are misleading.
- Users judge from contact sheets: send 6-frame sheets at each checkpoint, preview < 30 MB for phones.
- Check free disk before renders/zips; keep everything for a project in one folder so cleanup is one command.
- Home path may contain spaces ("C:/Users/Naveen Karthick"): always quote paths in bash.
- Keep a Blender source kit (scene.blend + scripts + maps) when deleting frames/caches.
