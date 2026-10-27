# Example: The Dhanteras Coin (v6, shipped)
38.7 s: FirstSelfie brand intro -> lens push + flash -> blank brass coin -> diya embosses -> macro with electric arcs ->
diya hero -> end-over-end flip to the rupee side -> rupee macro + slow-mo hero -> fuse -> bijili crackles -> cracks ->
slow white build -> centre space blast (48 fps, slow-mo on impact) -> debris + golden smoke in one continuous camera ->
gold TheBlock title emerges from the smoke, holds 6 s.

- coin3_scene.py   full scene builder (morphing relief rig, arcs, kolam traces, fuse, cracks, fracture, fire, 8 shot cameras). Modes build/bake/sheet.
- render_final5.py resumable per-shot render jobs (24 fps + 48 fps slow-mo window).
- render_tail.py   blast rework applied on top of the baked scene: centre origin, re-aimed shards, debris, hot shards, sparks, fire re-bake, continuous camera.
- v6_build.jsx     the shipped After Effects build (brand push, flashes, remaps, title, grade, CA, letterbox) - ae_build.jsx is its config-driven generalisation.
- title_build.jsx  fully editable live-text title with controls null (needs fonts installed for all users).
- gradetest.jsx    render test stills through the project's grade.
Paths inside are the original project paths (D:/FS DOCUMENTARY INTRO/...); adapt when reusing.
