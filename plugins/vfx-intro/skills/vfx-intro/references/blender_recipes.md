# Blender recipes (values that worked, Blender 5.2 Cycles, RTX 3050 6 GB)

## Render
- Cycles GPU **OptiX** (check: a CPU fallback is ~17x slower), 48 samples + OptiX denoise, persistent data, motion blur 0.5, AgX, exposure -0.3 to -0.6.
- 1920x804 (2.39:1) 16-bit PNG per shot folder; ~20-45 s/frame (volumes and 1300^2 relief grids are the slow parts). Test: 50 % / 16 samples.
- Slow-mo: render that window at 48 fps. Re-render only changed frames: delete those PNGs, run again (jobs skip existing files).

## Look: the premium dark void (`dark_void()` + `light_rig()`)
Teal-black world (0.0012, 0.0018, 0.0022), faint smoke dome, volume haze 0.0007 anisotropy 0.6, ~70 dust motes. One hard warm raking key (AREA 1100 W at (4.6,-2.2,1.0)), cool rim (650 W), weak under-fill. Raking light = relief reads.

## Metal + relief (`metal_material`)
Brass base (0.80,0.57,0.28), cavity dark (0.16,0.10,0.05), highs (0.88,0.68,0.40); Metallic 1; roughness 0.16 raised -> 0.48 cavities. Height map -> Displacement (scale 0.05, method BOTH) + Bump 0.3. Grids 1300x1300 for macro. Maps: 4K, 16-bit, median filter after upscaling (grain = camo blotches). Morph between reliefs: sink old -> soft ridge -> emboss new with 18 % overshoot, driven by a radial wave (coin3_scene.py `transition`).

## Energy
- Arcs: 4D Voronoi distance-to-edge, domain-warped by 4D noise (W = frame/8), core gain 60 white, fringe gain 7 cyan (0.25,0.8,1.0), gated by patch noise (`add_energy_arcs`).
- Cracks: Voronoi edges threshold `crack*0.028`, key 0 -> 1 -> 3.5 over ~1.2 s, emission (1,0.75,0.45) x25 (`add_cracks`).
- Fuse: angular emission head + trail around the rim; bijili pops = point lights 3500 W for 0.15 s + AE flashes + camera kicks.

## Blast (space style, zero-g) (`fracture_disc` + `blast` + `debris` + `sparks` + `fire_smoke`)
- Pre-flash point light builds over ~0.8 s to 2500 W at T0 (white build from inside).
- Origin = **centre** of the object. Hero hides at T0, 38 shards appear.
- Shards: 360 spread, speed 1.4-2.6, keys (T0,0)(+0.06,0.3)(+0.5,0.75)(+1.5,1.2)(end,2.4). Only 3 aim at a **ring around the lens** (offset 0.9-1.4 x, 0.5-0.9 z). Never down the lens axis: they look frozen.
- Debris: 180-260 instanced fragments (shared mesh), sizes 0.1-0.24 near / 0.07-0.2 far.
- Hot shards: emission peak **2-4** (not 30: blows out after the grade), cool to 0 by +1.4 s; edges a bit hotter (1,0.62,0.3).
- Sparks: 150 stretched spheres (scale z 10-35), blackbody 1700-3400 K, speed 5-11.
- Fire: Mantaflow gas res 128, noise x2, dissolve 22, volume density 0.85, golden flame ramp, emission flame^1.5 x11. Blast light 6000 -> 1000 W held warm so the smoke glows.
- Camera: keep the same camera; push forward into the cloud after ~0.5 s so smoke fills the frame (the title emerges from it).

## Cameras (`shot_cameras`)
Each shot = own camera, location keys + **Track-To an animated focus empty** (keyed rotations drift off target between keys), DOF on the empty. Lenses: wide push 42-50 mm f5.6, macro 70 mm f8, hero low 60 mm. Timeline markers bind cameras; render per shot.

## Flip / reveal
Root rotation keys (rx 2 -> 182 deg) with a small z hop (0.55) over ~2 s; back face grid rotated (pi, 0, pi) so its relief reads upright after the flip.

## Hero objects beyond discs
bmesh/geometry nodes for primitives (bells, lamps, bars, chips), Text objects with bevel for 3D type (users often prefer AE type), imported meshes (glTF/FBX) for idols/products. Relief/engraving via height maps on UV'd faces.
