"""Scene template: copy this AND vfx_lib.py to <project>/blender/ (scene.py + vfx_lib.py) and edit the STORY block. Working 10 s example:
a metal medallion in a dark void -> push in -> electric arcs -> glowing cracks -> centre space-blast -> golden smoke.

  blender -b -P scene.py -- build  [--relief path/to/height.png]      -> scene.blend
  blender -b scene.blend -P scene.py -- bake                           -> fire cache (needs build first)
  blender -b scene.blend -P scene.py -- test  <out_dir>                -> 6 low-res stills (approve before full render)
  blender -b scene.blend -t 6 -P scene.py -- render <out_dir>          -> resumable PNG sequences per shot
Run renders at below-normal priority with 6 threads (see tools/blender_bg.sh): full load can starve Wi-Fi."""
import bpy, sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)                                   # vfx_lib.py is copied next to this file (project stays self-contained)
if os.environ.get("VFX_LIB"): sys.path.insert(0, os.environ["VFX_LIB"])
from vfx_lib import *

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["build"]
MODE = argv[0]
RELIEF = argv[argv.index("--relief") + 1] if "--relief" in argv else None

# ================================================================== STORY (edit this block per project)
END = 10.0
T0 = 7.4                                   # burst moment
CAM_AT_BLAST = (0.25, -3.0, 1.0)
SHOTS = [  # name, t0, t1, lens, fstop, [(t, cam_loc, target)]
    ("S1_push",  0.0, 3.0, 50, 5.6, [(0.0, (0.0, -0.05, 6.5), (0, 0, 0)), (3.0, (1.7, -2.3, 0.62), (0, 0.15, 0.05))]),
    ("S2_macro", 3.0, 5.5, 70, 8.0, [(3.0, (-0.95, -1.2, 0.62), (0, 0.3, 0.08)), (5.5, (0.35, -1.0, 0.52), (0, 0.42, 0.09))]),
    ("S3_crack", 5.5, 7.4, 50, 6.3, [(5.5, (0.4, -3.6, 1.3), (0, 0, 0)), (7.4, CAM_AT_BLAST, (-0.2, 0, 0.1))]),
    ("S4_blast", 7.4, 10.0, 42, 4.0, [(7.4, CAM_AT_BLAST, (-0.2, 0, 0.1)), (8.4, (0.35, -2.1, 0.85), (0, 0.2, 0.35)), (10.0, (0.2, -1.1, 0.6), (-0.05, 0.6, 0.45))]),
]
JOBS = [("S1_push", "S1_push", 0.0, 3.0, 24), ("S2_macro", "S2_macro", 3.0, 5.5, 24), ("S3_crack", "S3_crack", 5.5, 7.4, 24),
        ("S4_burst48", "S4_blast", 7.4, 8.4, 48), ("S4_tail", "S4_blast", 8.4, 10.0, 24)]
TEST = [("S1_push", 1.5), ("S2_macro", 4.5), ("S3_crack", 7.2), ("S4_blast", 7.5), ("S4_blast", 8.0), ("S4_blast", 9.2)]

def build():
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; gpu(sc)
    cinema_setup(sc, end_t=END)
    face = metal_material("Face", height_img=RELIEF); add_energy_arcs(face); add_cracks(face)
    body = metal_material("Body")
    KEY(face.node_tree, "arc_on", [(0, 0), (3.4, 0), (3.8, 1), (5.3, 1), (5.7, 0)])
    KEY(face.node_tree, "crack", [(0, 0), (6.0, 0), (6.8, 1), (T0, 3.5)])
    root = disc("Hero", face_mat=face, body_mat=body, face_res=700 if not RELIEF else 1300)
    for t, rz in ((0, -3), (END, 6)):
        root.rotation_euler = (math.radians(1.5), 0, math.radians(rz)); root.keyframe_insert("rotation_euler", frame=F(t))
    for o in [root] + list(root.children):                       # hero vanishes at the burst, shards take over
        o.hide_render = False; o.keyframe_insert("hide_render", frame=F(T0) - 1)
        o.hide_render = True; o.keyframe_insert("hide_render", frame=F(T0))
    shard_face = face.copy(); shard_face.name = "ShardFace"
    edge = metal_material("ShardEdge", base=(0.13, 0.085, 0.045))
    key_emission(shard_face, [(0, 0), (T0 - 0.01, 0), (T0, 2.2), (T0 + 0.3, 1.0), (T0 + 0.8, 0.25), (T0 + 1.4, 0)])
    key_emission(edge, [(0, 0), (T0 - 0.01, 0), (T0, 4.0), (T0 + 0.4, 2.0), (T0 + 1.0, 0.6), (T0 + 1.6, 0.1)], color=(1.0, 0.62, 0.3))
    shards = fracture_disc(shard_face, edge, n=38, subsurf=4)
    blast(shards, T0, CAM_AT_BLAST, toward_cam=3, end_t=END)
    debris(shards, T0, CAM_AT_BLAST, n=180, end_t=END)
    sparks(T0, end_t=END)
    fire_smoke(T0, END, cache_dir=os.path.join(HERE, "firecache"))
    point_light_keys("PreFlash", (0, 0, 0.15), (1.0, 0.95, 0.85), [(0, 0), (T0 - 0.8, 0), (T0 - 0.02, 2500), (T0 + 0.2, 0)])
    point_light_keys("BlastLight", (0, 0, 0.1), (1.0, 0.62, 0.25), [(0, 0), (T0 - 0.1, 0), (T0, 6000), (T0 + 0.25, 3000), (T0 + 1.2, 1800), (END, 1000)], size=0.5, volume=0.1)
    light_rig(); dark_void()
    shot_cameras(SHOTS)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "scene.blend")); print("SAVED", flush=True)

if MODE == "build":
    build()
elif MODE == "bake":
    gpu(); bake_fire(); bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath); print("BAKED", flush=True)
elif MODE == "test":
    gpu(); render_jobs(argv[1], None, test_times=TEST)
elif MODE == "render":
    gpu(); render_jobs(argv[1], JOBS)
