"""v5 final render, resumable. blender -b coin3_baked.blend -P render_final5.py -- <out_dir>
Only the new shots (S1/S2 reuse v4 frames). The blast build + burst (23.5-25.5s) renders at 48 fps for AE slow motion."""
import bpy, os, sys
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
sc = bpy.context.scene
pr = bpy.context.preferences.addons["cycles"].preferences
pr.compute_device_type = "OPTIX"; pr.get_devices()
for dv in pr.devices: dv.use = (dv.type == "OPTIX")
sc.cycles.device = "GPU"; sc.render.use_persistent_data = True
sc.cycles.samples = 48; sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPTIX"
sc.render.resolution_percentage = 100; sc.render.use_motion_blur = True
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
for mk in sc.timeline_markers: mk.camera = None
FPS = 24
JOBS = [("S3_diyahero", "S3_diyahero", 10.0, 13.0, 24), ("S4_flip", "S4_flip", 13.0, 15.5, 24),
        ("S5_rupeemacro", "S5_rupeemacro", 15.5, 18.5, 24), ("S6_rupeehero", "S6_rupeehero", 18.5, 21.0, 24),
        ("S7_fuse", "S7_fuse", 21.0, 23.5, 24), ("S8_blast48", "S8_blast", 23.5, 25.5, 48), ("S8_after", "S8_blast", 25.5, 28.5, 24)]
for folder, camname, t0, t1, rate in JOBS:
    sc.camera = bpy.data.objects[camname]
    d = os.path.join(OUT, folder); os.makedirs(d, exist_ok=True)
    n = int(round((t1 - t0) * rate))
    for k in range(n):
        path = os.path.join(d, "%s_%04d.png" % (folder, k))
        if os.path.exists(path): continue
        f = (t0 + k / rate) * FPS + 1
        sc.frame_set(int(f), subframe=f - int(f))
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("FRAME", folder, k + 1, "/", n, flush=True)
print("ALLDONE", flush=True)
