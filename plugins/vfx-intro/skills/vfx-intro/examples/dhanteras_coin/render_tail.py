"""Post-blast continuation (one camera, no cut): from 24.6s the S8 camera keeps going, pushes forward
through the flying shards into the glowing smoke. Frames before 24.6 are the existing S8_blast48 render.
blender -b coin3_baked.blend -P render_tail.py -- <out_dir> [test]"""
import bpy, os, sys, math
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]; TEST = len(argv) > 1
sc = bpy.context.scene
FPS = 24
def F(t): return t * FPS + 1
pr = bpy.context.preferences.addons["cycles"].preferences
pr.compute_device_type = "OPTIX"; pr.get_devices()
for dv in pr.devices: dv.use = (dv.type == "OPTIX")
sc.cycles.device = "GPU"; sc.render.use_persistent_data = True
sc.cycles.samples = 16 if TEST else 48; sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPTIX"
sc.render.resolution_percentage = 50 if TEST else 100; sc.render.use_motion_blur = True
sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"
for mk in sc.timeline_markers: mk.camera = None

J = 24.6
cam = bpy.data.objects["S8_blast"]; foc = bpy.data.objects["S8_blast_focus"]
sc.frame_set(int(F(J)), subframe=F(J) - int(F(J)))
loc0, rot0, f0 = cam.location.copy(), cam.rotation_euler.copy(), foc.location.copy()
from bpy_extras import anim_utils
def FC(idb):
    ad = idb.animation_data
    return list(anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves)
def cut_after(ob, path):
    fc = [c for c in FC(ob) if c.data_path == path]
    for c in fc:
        while True:
            ks = [i for i, k in enumerate(c.keyframe_points) if k.co.x > F(J) - 0.01]
            if not ks: break
            c.keyframe_points.remove(c.keyframe_points[ks[-1]])
for p in ("location", "rotation_euler"): cut_after(cam, p)
cut_after(foc, "location")
def aim(loc, tgt):
    cam.location = loc; q = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y"); cam.rotation_mode = "XYZ"; cam.rotation_euler = q.to_euler()
cam.location = loc0; cam.rotation_euler = rot0; cam.keyframe_insert("location", frame=F(J)); cam.keyframe_insert("rotation_euler", frame=F(J))
foc.location = f0; foc.keyframe_insert("location", frame=F(J))
# push in toward the blast centre (-0.95, 0): shards stream past the lens, then we sit inside the glow
for t, loc, tgt in ((25.6, (0.35, -2.1, 0.85), (0.0, 0.2, 0.35)), (27.0, (0.2, -1.1, 0.6), (-0.05, 0.6, 0.45)), (28.5, (0.12, -0.5, 0.5), (-0.1, 1.2, 0.55))):
    aim(loc, tgt); cam.keyframe_insert("location", frame=F(t)); cam.keyframe_insert("rotation_euler", frame=F(t))
    foc.location = tgt; foc.keyframe_insert("location", frame=F(t))
# ease out of the join smoothly (no jerk), then a steady glide
for c in FC(cam):
    for k in c.keyframe_points:
        if k.co.x >= F(J) - 0.01: k.interpolation = "BEZIER"; k.handle_left_type = k.handle_right_type = "AUTO_CLAMPED"
bpy.data.cameras["S8_blast"].dof.aperture_fstop = 4.0
# keep the blast glowing so the smoke stays warm-lit while we are inside it
bl = bpy.data.lights["BlastLight"]; sc.frame_set(int(F(J))); e0 = bl.energy
cut_after(bl, "energy")
for t, e in ((J, e0), (25.6, 1800), (27.0, 1300), (28.5, 1000)):
    bl.energy = e; bl.keyframe_insert("energy", frame=F(t))

# ---- dense debris (reference look): small coin fragments, many blown toward the lens, the rest drifting round the cloud
import random
random.seed(11)
T0 = 24.1; O = Vector((-0.95, 0.0, 0.0)); CAMP = Vector((0.25, -3.0, 1.0))
src = [o for o in bpy.data.objects if o.name.startswith("Shard") and o.type == "MESH"]
C0 = Vector((0.0, 0.0, 0.0))
# ---- centre the blast (reference): fire, light and the 38 big shards all burst from the coin centre
C0 = Vector((0.0, 0.0, 0.0))
bpy.data.objects["FireFlow"].location = (0, 0, 0)
bpy.data.objects["BlastLight"].location = (0, 0, 0.1)
for o in bpy.data.objects:
    if o.name.startswith("Shard") and o.type == "MESH" and o.name[5:].isdigit():
        sc.frame_set(int(F(T0)) - 2); c = o.location.copy()
        for path in ("location", "rotation_euler"):
            for fc_ in [x for x in FC(o) if x.data_path == path]:
                while len(fc_.keyframe_points): fc_.keyframe_points.remove(fc_.keyframe_points[len(fc_.keyframe_points) - 1])
        out = Vector((c.x, c.y, 0)).normalized() if Vector((c.x, c.y)).length > 0.05 else Vector((1, 0, 0))
        if o.name in ("Shard3", "Shard17", "Shard29"):   # only three big pieces pass the camera
            ring = Vector((random.choice((-1, 1)) * random.uniform(0.9, 1.4), 0, random.choice((-1, 1)) * random.uniform(0.5, 0.9)))
            dd = (out * 0.4 + (CAMP + ring - c).normalized() * 0.9).normalized()
        else:                                             # the rest burst out 360 and leave the frame sideways
            dd = (out * 0.9 + Vector((random.gauss(0, 0.35), random.gauss(0, 0.35), random.uniform(0.0, 0.6)))).normalized()
        spd = random.uniform(1.4, 2.6); spin = Vector((random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5), random.uniform(-1.5, 1.5))); o.scale = (0.8, 0.8, 0.8)
        for t, k in ((0.0, 0.0), (T0, 0.0), (T0 + 0.06, 0.3), (T0 + 0.5, 0.75), (T0 + 1.5, 1.2), (28.5, 2.4)):
            o.location = c + dd * spd * k; o.rotation_euler = (spin.x * k, spin.y * k, spin.z * k)
            o.keyframe_insert("location", frame=F(t)); o.keyframe_insert("rotation_euler", frame=F(t))
# Shard1 / Shard16 flew straight down the lens axis and looked frozen: send them out sideways, fast
for n_, side in (("Shard1", Vector((1.0, 0.15, 0.35))), ("Shard16", Vector((0.9, 0.1, 0.7)))):
    o = bpy.data.objects[n_]; sc.frame_set(int(F(T0)) - 2); c = o.location.copy()
    for path in ("location", "rotation_euler"):
        for fc_ in [x for x in FC(o) if x.data_path == path]:
            while len(fc_.keyframe_points): fc_.keyframe_points.remove(fc_.keyframe_points[len(fc_.keyframe_points) - 1])
    dd = side.normalized(); spin = Vector((1.5, -2.0, 1.0))
    for t, k in ((0.0, 0.0), (T0, 0.0), (T0 + 0.06, 0.3), (T0 + 0.5, 0.75), (T0 + 1.5, 1.2), (28.5, 2.4)):
        o.location = c + dd * 4.5 * k; o.rotation_euler = (spin.x * k, spin.y * k, spin.z * k)
        o.keyframe_insert("location", frame=F(t)); o.keyframe_insert("rotation_euler", frame=F(t))
# ---- white-hot shards that cool to the engraved coin metal
pb = [n for n in bpy.data.materials["ShardFace"].node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
pb.inputs["Emission Color"].default_value = (1.0, 0.78, 0.5, 1)
for t, e in ((0.0, 0.0), (T0 - 0.01, 0.0), (T0, 2.2), (T0 + 0.3, 1.0), (T0 + 0.8, 0.25), (T0 + 1.4, 0.0), (T0 + 2.4, 0.0)):
    pb.inputs["Emission Strength"].default_value = e; pb.inputs["Emission Strength"].keyframe_insert("default_value", frame=F(t))
en_ = bpy.data.materials["ShardEdge"].node_tree; eb_ = [n for n in en_.nodes if n.type == "BSDF_PRINCIPLED"][0]
for inp in ("Emission Color", "Emission Strength"):
    for l_ in list(eb_.inputs[inp].links): en_.links.remove(l_)
eb_.inputs["Emission Color"].default_value = (1.0, 0.62, 0.3, 1)
for t, e in ((0.0, 0.0), (T0 - 0.01, 0.0), (T0, 4.0), (T0 + 0.4, 2.0), (T0 + 1.0, 0.6), (T0 + 1.6, 0.1), (T0 + 2.4, 0.0)):
    eb_.inputs["Emission Strength"].default_value = e; eb_.inputs["Emission Strength"].keyframe_insert("default_value", frame=F(t))
fpv = [n for n in bpy.data.materials["Fire"].node_tree.nodes if n.type == "PRINCIPLED_VOLUME"][0]
fpv.inputs["Density"].default_value = 0.85   # thinner smoke
# ---- spark spikes: longer, brighter radial streaks from the centre
for o in bpy.data.objects:
    if o.name.startswith("Sphere") and o.data.materials and o.data.materials[0].name == "Spark":
        o.scale = (1.4, 1.4, o.scale.z * 3.5)
        for fc_ in [x for x in FC(o) if x.data_path == "location"]:
            for k in fc_.keyframe_points: k.co.y -= ({0: -0.95, 1: 0.0, 2: 0.0}[fc_.array_index]); k.handle_left.y -= ({0: -0.95, 1: 0.0, 2: 0.0}[fc_.array_index]); k.handle_right.y -= ({0: -0.95, 1: 0.0, 2: 0.0}[fc_.array_index])
# ---- re-simulate the fire at the centre (own cache, old one kept)
dom = bpy.data.objects["FireDomain"]; dsd = dom.modifiers["Fluid"].domain_settings
dsd.cache_directory = os.path.join(os.path.dirname(bpy.data.filepath), "firecache_centre")
if not os.path.exists(os.path.join(dsd.cache_directory, "data")):
    sc.frame_set(1)
    for o_ in sc.objects: o_.select_set(False)
    dom.select_set(True); bpy.context.view_layer.objects.active = dom
    with bpy.context.temp_override(active_object=dom, object=dom):
        bpy.ops.fluid.free_all(); bpy.ops.fluid.bake_all()
    print("FIRE BAKED", flush=True)
for i in range(260):
    b = random.choice(src); ob = bpy.data.objects.new("Frag%d" % i, b.data); sc.collection.objects.link(ob)
    m = ob.modifiers.new("sub", "SUBSURF"); m.subdivision_type = "SIMPLE"; m.levels = m.render_levels = 3
    s_ = random.uniform(0.1, 0.24) if i < 120 else random.uniform(0.07, 0.2); ob.scale = (s_, s_, s_ * 0.9)
    r = 0.92 * math.sqrt(random.random()); a_ = random.uniform(0, 2 * math.pi)
    start = Vector((r * math.cos(a_), r * math.sin(a_), random.uniform(-0.03, 0.05)))   # pieces of the coin face itself
    out = Vector((start.x, start.y, 0)).normalized() if r > 0.05 else Vector((1, 0, 0))
    if i < 120:   # blown at the lens: radial burst biased to camera, fills the frame and flies past
        ring = Vector((random.choice((-1, 1)) * random.uniform(0.9, 2.2), 0, random.choice((-1, 1)) * random.uniform(0.6, 1.3)))
        d = (out * 0.5 + (CAMP + ring - start).normalized() * 0.8 + Vector((random.gauss(0, 0.35), random.gauss(0, 0.2), random.gauss(0, 0.35)))).normalized(); spd = random.uniform(1.6, 3.2)
    else:         # 360 spherical spread from the centre, slower so they hang around the cloud
        d = (out * 0.7 + Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized()).normalized(); spd = random.uniform(1.0, 3.5)
    spin = Vector((random.uniform(-7, 7), random.uniform(-7, 7), random.uniform(-4, 4)))
    ob.rotation_euler = (0, 0, random.uniform(0, 6.3)); base_rz = ob.rotation_euler.z
    ob.hide_render = True; ob.keyframe_insert("hide_render", frame=F(T0) - 1)
    ob.hide_render = False; ob.keyframe_insert("hide_render", frame=F(T0))
    for t, k in ((T0, 0.0), (T0 + 0.06, 0.3), (T0 + 0.5, 0.75), (T0 + 1.5, 1.2), (28.5, 2.4)):
        ob.location = start + d * spd * k; ob.rotation_euler = (spin.x * k, spin.y * k, base_rz + spin.z * k)
        ob.keyframe_insert("location", frame=F(t)); ob.keyframe_insert("rotation_euler", frame=F(t))
sc.camera = cam
d = os.path.join(OUT, "S8_tail2"); os.makedirs(d, exist_ok=True)
JOBS = [("S8_burst48", 24.1, 25.1, 48), ("S8_tail2", 25.1, 28.5, 24)]
if TEST: JOBS = [("S8_tail2", 0, 0, 0)]
for folder, t0, t1, rate in JOBS:
    d = os.path.join(OUT, folder); os.makedirs(d, exist_ok=True)
    times = [24.15, 24.35, 24.6, 24.9, 25.6, 26.6] if TEST else [t0 + k / rate for k in range(int(round((t1 - t0) * rate)))]
    for k, t in enumerate(times):
        path = os.path.join(d, ("test_%02d.png" % k) if TEST else ("%s_%04d.png" % (folder, k)))
        if os.path.exists(path) and not TEST: continue
        f = F(t); sc.frame_set(int(f), subframe=f - int(f)); sc.render.filepath = path
        bpy.ops.render.render(write_still=True); print("FRAME", folder, k + 1, "/", len(times), flush=True)
print("ALLDONE", flush=True)
