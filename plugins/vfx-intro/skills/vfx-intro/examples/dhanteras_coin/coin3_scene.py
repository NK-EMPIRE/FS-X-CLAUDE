"""The Dhanteras Coin v3: 26s, 6 long shots, Bhutan-style rise/melt/stamp morphs, brass, electric energy,
real fracture + Mantaflow fire. Usage:
  blender -b -P coin3_scene.py -- build
  blender -b coin3.blend -P coin3_scene.py -- bake            (fire/smoke sim)
  blender -b coin3.blend -P coin3_scene.py -- sheet <out> [t1,t2,...]
"""
import bpy, bmesh, math, sys, os, random
from mathutils import Vector, Matrix

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["build"]
MODE = argv[0]
HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.join(HERE, "maps")
FPS = 24
def F(sec): return int(round(sec * FPS)) + 1
FIELD = {"diya": 0.522, "kolam": 0.612, "lotus": 0.553, "rupee": 0.545}
MID = 0.55

def gpu():
    pr = bpy.context.preferences.addons["cycles"].preferences
    try:
        pr.compute_device_type = "OPTIX"; pr.get_devices()
        for d in pr.devices: d.use = (d.type == "OPTIX")
    except Exception: pass
    bpy.context.scene.cycles.device = "GPU"

if MODE in ("bake", "sheet", "animatic"):
    sc = bpy.context.scene; gpu()
else:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene; gpu()

# ============================================================== helpers
def node(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items(): setattr(n, k, v)
    return n
def L(nt, a, b): nt.links.new(a, b)
def M(nt, op, a=None, b=None, clamp=False):
    m = node(nt, "ShaderNodeMath", operation=op, use_clamp=clamp)
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)): m.inputs[i].default_value = v
        else: L(nt, v, m.inputs[i])
    return m.outputs[0]
def MR(nt, v, fmin, fmax, tmin=0.0, tmax=1.0, smooth=True):
    m = node(nt, "ShaderNodeMapRange", interpolation_type="SMOOTHSTEP" if smooth else "LINEAR", clamp=True)
    L(nt, v, m.inputs["Value"])
    m.inputs["From Min"].default_value, m.inputs["From Max"].default_value = fmin, fmax
    m.inputs["To Min"].default_value, m.inputs["To Max"].default_value = tmin, tmax
    return m.outputs["Result"]
def MIX(nt, fac, a, b):
    m = node(nt, "ShaderNodeMix", data_type="FLOAT")
    for s, v in ((m.inputs[0], fac), (m.inputs[2], a), (m.inputs[3], b)):
        if isinstance(v, (int, float)): s.default_value = v
        else: L(nt, v, s)
    return m.outputs[0]
def CMIX(nt, fac, a, b):
    m = node(nt, "ShaderNodeMix", data_type="RGBA")
    for s, v in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
        if isinstance(v, (int, float)): s.default_value = v
        elif isinstance(v, tuple): s.default_value = v
        else: L(nt, v, s)
    return m.outputs[2]
def VAL(nt, name, v=0.0):
    n = node(nt, "ShaderNodeValue", label=name, name=name); n.outputs[0].default_value = v; return n.outputs[0]
def KEY(nt, name, pairs):
    o = nt.nodes[name].outputs[0]
    for t, v in pairs:
        o.default_value = v; o.keyframe_insert("default_value", frame=F(t))
def IMG(nt, uv, name):
    i = node(nt, "ShaderNodeTexImage", extension="CLIP", interpolation="Cubic")
    i.image = bpy.data.images.get(name) or bpy.data.images.load(os.path.join(MAPS, name))
    i.image.colorspace_settings.name = "Non-Color"
    L(nt, uv, i.inputs["Vector"]); return i.outputs["Color"]
def COL(nt, rgb, scale):
    n = node(nt, "ShaderNodeRGB"); n.outputs[0].default_value = (*rgb, 1)
    v = node(nt, "ShaderNodeVectorMath", operation="SCALE"); L(nt, n.outputs[0], v.inputs[0])
    if isinstance(scale, (int, float)): v.inputs["Scale"].default_value = scale
    else: L(nt, scale, v.inputs["Scale"])
    return v.outputs[0]
def VADD(nt, a, b):
    v = node(nt, "ShaderNodeVectorMath", operation="ADD"); L(nt, a, v.inputs[0]); L(nt, b, v.inputs[1]); return v.outputs[0]

def build():
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, F(28.5)
    sc.render.resolution_x, sc.render.resolution_y = 1920, 804
    sc.render.engine = "CYCLES"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = -0.3
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
    sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPTIX"
    sc.render.use_persistent_data = True

    # ========================================================== FACE MATERIAL: morph rig + brass + energy
    face = bpy.data.materials.new("CoinFace"); face.use_nodes = True; face.displacement_method = "BOTH"
    nt = face.node_tree; out = nt.nodes["Material Output"]; bsdf = nt.nodes["Principled BSDF"]
    tc = node(nt, "ShaderNodeTexCoord"); uv = tc.outputs["UV"]; obj = tc.outputs["Object"]
    sep = node(nt, "ShaderNodeSeparateXYZ"); L(nt, obj, sep.inputs[0]); ox, oy = sep.outputs["X"], sep.outputs["Y"]
    def dist_from(px, py):
        dx = M(nt, "SUBTRACT", ox, px); dy = M(nt, "SUBTRACT", oy, py)
        return M(nt, "SQRT", M(nt, "ADD", M(nt, "MULTIPLY", dx, dx), M(nt, "MULTIPLY", dy, dy)))
    wn = node(nt, "ShaderNodeTexNoise"); wn.inputs["Scale"].default_value = 4.5; wn.inputs["Detail"].default_value = 6; L(nt, obj, wn.inputs["Vector"])
    flow = node(nt, "ShaderNodeTexNoise"); flow.inputs["Scale"].default_value = 9; flow.inputs["Detail"].default_value = 4
    flow.noise_dimensions = "4D"; L(nt, obj, flow.inputs["Vector"])
    flow.inputs["W"].driver_add("default_value").driver.expression = "frame/30"

    H, Mo, D = {}, {}, {}
    for k in ("diya", "kolam", "lotus", "rupee"):
        off = MID - FIELD[k]
        H[k] = M(nt, "ADD", IMG(nt, uv, k + "_height.png"), off)
        Mo[k] = M(nt, "ADD", IMG(nt, uv, k + "_molten.png"), off)
        D[k] = M(nt, "ADD", IMG(nt, uv, k + "_detail.png"), off)

    # Bhutan mechanic: a wave crosses the face; behind it the old relief presses back INTO the flat metal,
    # a soft ridge rolls past, then the new relief embosses UP with a small overshoot. Always crisp, never molten.
    def transition(curH, curD, k, pname, origin):
        P = VAL(nt, pname)
        field = M(nt, "ADD", M(nt, "MULTIPLY", dist_from(*origin), 0.8), M(nt, "MULTIPLY", wn.outputs["Fac"], 0.12))
        p = M(nt, "SUBTRACT", M(nt, "MULTIPLY", P, 2.0), field)
        sink = MR(nt, p, 0.0, 0.35, 1.0, 0.0)
        grow = MR(nt, p, 0.45, 0.9)
        over = M(nt, "MULTIPLY", M(nt, "SINE", M(nt, "MULTIPLY", MR(nt, p, 0.55, 1.05, smooth=False), math.pi)), 0.18)
        ridge = M(nt, "MULTIPLY", M(nt, "SINE", M(nt, "MULTIPLY", MR(nt, p, 0.25, 0.6, smooth=False), math.pi)), 0.02)
        gain = M(nt, "ADD", grow, over)
        hA = M(nt, "MULTIPLY", M(nt, "SUBTRACT", curH, MID), sink)
        hB = M(nt, "MULTIPLY", M(nt, "SUBTRACT", H[k], MID), gain)
        dA = M(nt, "MULTIPLY", M(nt, "SUBTRACT", curD, MID), sink)
        dB = M(nt, "MULTIPLY", M(nt, "SUBTRACT", D[k], MID), gain)
        return (M(nt, "ADD", MID, M(nt, "ADD", M(nt, "ADD", hA, hB), ridge)), M(nt, "ADD", MID, M(nt, "ADD", dA, dB)))

    sharp, det = MID, MID
    for k, pname, origin in (("diya", "P_diya", (0.0, 0.0)), ("lotus", "P_lotus", (-0.5, 0.2)), ("rupee", "P_rupee", (-0.2, 0.45))):
        sharp, det = transition(sharp, det, k, pname, origin)
    hgt = sharp
    disp = node(nt, "ShaderNodeDisplacement"); disp.inputs["Midlevel"].default_value = MID; disp.inputs["Scale"].default_value = 0.05
    L(nt, hgt, disp.inputs["Height"]); L(nt, disp.outputs[0], out.inputs["Displacement"])
    detm = det

    # micro surface: scratches (anisotropic streak noise), fingerprints, cavity patina, polished highs
    mp = node(nt, "ShaderNodeMapping"); mp.inputs["Scale"].default_value = (900, 6, 6); mp.inputs["Rotation"].default_value = (0, 0, 0.6)
    L(nt, obj, mp.inputs["Vector"])
    scr = node(nt, "ShaderNodeTexNoise"); scr.inputs["Scale"].default_value = 1; scr.inputs["Detail"].default_value = 2; L(nt, mp.outputs[0], scr.inputs["Vector"])
    scratch = MR(nt, scr.outputs["Fac"], 0.62, 0.72)
    fp = node(nt, "ShaderNodeTexNoise"); fp.inputs["Scale"].default_value = 3.5; fp.inputs["Detail"].default_value = 12; L(nt, obj, fp.inputs["Vector"])
    cav = MR(nt, M(nt, "SUBTRACT", detm, hgt), -0.06, 0.03)          # 0 = crevice, 1 = raised edge
    bump = node(nt, "ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.3; bump.inputs["Distance"].default_value = 0.0025
    L(nt, detm, bump.inputs["Height"]); L(nt, bump.outputs[0], bsdf.inputs["Normal"])
    base = CMIX(nt, cav, (0.16, 0.10, 0.05, 1), (0.80, 0.57, 0.28, 1))
    base = CMIX(nt, MR(nt, cav, 0.8, 1.0), base, (0.88, 0.68, 0.40, 1))
    L(nt, base, bsdf.inputs["Base Color"]); bsdf.inputs["Metallic"].default_value = 1.0
    rough = M(nt, "ADD", MR(nt, cav, 0.0, 1.0, 0.48, 0.16), M(nt, "ADD", M(nt, "MULTIPLY", scratch, 0.006), MR(nt, fp.outputs["Fac"], 0.5, 0.7, 0.0, 0.008)))
    L(nt, rough, bsdf.inputs["Roughness"])

    # energy: electric arcs hugging relief edges (white core, cyan fringe), kolam light-traces, flame spark, cracks
    vor = node(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE", voronoi_dimensions="4D"); vor.inputs["Scale"].default_value = 3.2
    dvec = node(nt, "ShaderNodeVectorMath", operation="ADD"); L(nt, obj, dvec.inputs[0])
    dn = node(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); dn.inputs["Scale"].default_value = 6; dn.inputs["Detail"].default_value = 3
    L(nt, obj, dn.inputs["Vector"]); dn.inputs["W"].driver_add("default_value").driver.expression = "frame/8"
    dsc = node(nt, "ShaderNodeVectorMath", operation="SCALE"); dsc.inputs["Scale"].default_value = 0.35
    L(nt, dn.outputs["Color"], dsc.inputs[0]); L(nt, dsc.outputs[0], dvec.inputs[1]); L(nt, dvec.outputs[0], vor.inputs["Vector"])
    vor.inputs["W"].driver_add("default_value").driver.expression = "frame/5"
    edge = MR(nt, M(nt, "ABSOLUTE", M(nt, "SUBTRACT", det, sharp)), 0.02, 0.08)
    arc_on = VAL(nt, "arc_on")
    patch = node(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); patch.inputs["Scale"].default_value = 1.6; L(nt, obj, patch.inputs["Vector"])
    patch.inputs["W"].driver_add("default_value").driver.expression = "frame/14"
    gate = M(nt, "MULTIPLY", M(nt, "ADD", M(nt, "MULTIPLY", edge, 0.5), 0.5), M(nt, "MULTIPLY", arc_on, MR(nt, patch.outputs["Fac"], 0.56, 0.64)))
    core = M(nt, "MULTIPLY", MR(nt, vor.outputs["Distance"], 0.0035, 0.0), gate)
    fringe = M(nt, "MULTIPLY", MR(nt, vor.outputs["Distance"], 0.018, 0.002), gate)
    # kolam traces glow in the flat field around the diya, revealed outward from the flame
    kgroove = MR(nt, M(nt, "SUBTRACT", H["kolam"], D["kolam"]), 0.04, 0.12)
    flat = MR(nt, M(nt, "SUBTRACT", H["diya"], MID), 0.09, 0.03)
    trace_t = VAL(nt, "trace")
    reveal = MR(nt, M(nt, "SUBTRACT", M(nt, "MULTIPLY", trace_t, 1.3), dist_from(0.0, 0.42)), -0.03, 0.02)
    traces = M(nt, "MULTIPLY", M(nt, "MULTIPLY", kgroove, flat), reveal)
    spark_t = VAL(nt, "spark")
    spark = M(nt, "MULTIPLY", MR(nt, dist_from(0.0, 0.52), 0.035, 0.0), spark_t)
    cvor = node(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE"); cvor.inputs["Scale"].default_value = 3.0; L(nt, obj, cvor.inputs["Vector"])
    crack_t = VAL(nt, "crack")
    cracks = M(nt, "MULTIPLY", MR(nt, cvor.outputs["Distance"], M(nt, "MULTIPLY", crack_t, 0.03), 0.0, smooth=False) if False else M(nt, "LESS_THAN", cvor.outputs["Distance"], M(nt, "MULTIPLY", crack_t, 0.028)), crack_t)
    emis = VADD(nt, COL(nt, (1, 1, 1), M(nt, "MULTIPLY", core, 60.0)), COL(nt, (0.25, 0.8, 1.0), M(nt, "MULTIPLY", fringe, 7.0)))
    emis = VADD(nt, emis, COL(nt, (1.0, 0.9, 0.78), M(nt, "MULTIPLY", traces, 5.0)))
    emis = VADD(nt, emis, COL(nt, (1.0, 0.95, 0.85), M(nt, "MULTIPLY", spark, 80.0)))
    emis = VADD(nt, emis, COL(nt, (1.0, 0.75, 0.45), M(nt, "MULTIPLY", cracks, 25.0)))
    L(nt, emis, bsdf.inputs["Emission Color"]); bsdf.inputs["Emission Strength"].default_value = 1.0

    # ========================================================== BODY / RIM MATERIAL (fuse spark)
    body = bpy.data.materials.new("CoinBody"); body.use_nodes = True; bn = body.node_tree; bb = bn.nodes["Principled BSDF"]
    btc = node(bn, "ShaderNodeTexCoord"); bsep = node(bn, "ShaderNodeSeparateXYZ"); L(bn, btc.outputs["Object"], bsep.inputs[0])
    bmp = node(bn, "ShaderNodeMapping"); bmp.inputs["Scale"].default_value = (5, 5, 400); L(bn, btc.outputs["Object"], bmp.inputs["Vector"])
    bsn = node(bn, "ShaderNodeTexNoise"); L(bn, bmp.outputs[0], bsn.inputs["Vector"])
    bb.inputs["Base Color"].default_value = (0.80, 0.57, 0.28, 1); bb.inputs["Metallic"].default_value = 1.0
    L(bn, MR(bn, bsn.outputs["Fac"], 0.3, 0.7, 0.16, 0.34), bb.inputs["Roughness"])
    ang = M(bn, "DIVIDE", M(bn, "ADD", M(bn, "ARCTAN2", bsep.outputs["Y"], bsep.outputs["X"]), math.pi), 2 * math.pi)
    fuse = VAL(bn, "fuse")
    lag = M(bn, "SUBTRACT", fuse, ang)
    head = MR(bn, M(bn, "ABSOLUTE", lag), 0.008, 0.0)
    trail = M(bn, "MULTIPLY", M(bn, "GREATER_THAN", lag, 0.0), MR(bn, lag, 0.0, 0.25, 1.0, 0.0))
    L(bn, M(bn, "ADD", M(bn, "MULTIPLY", head, 25.0), M(bn, "MULTIPLY", trail, 0.25)), bb.inputs["Emission Strength"])
    bb.inputs["Emission Color"].default_value = (1.0, 0.9, 0.75, 1)

    # back face: rupee relief only (revealed by the flip), cracks keyed like the front
    back_face = face.copy(); back_face.name = "CoinBack"; bnt = back_face.node_tree
    if bnt.animation_data: bnt.animation_data_clear()
    for n_, v in (("P_diya", 0), ("P_lotus", 0), ("P_rupee", 1), ("arc_on", 0), ("trace", 0), ("spark", 0), ("crack", 0)):
        bnt.nodes[n_].outputs[0].default_value = v

    # ========================================================== GEOMETRY
    root = bpy.data.objects.new("Coin", None); sc.collection.objects.link(root)
    me = bpy.data.meshes.new("Body"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=480, radius1=1.0, radius2=1.0, depth=0.116)
    for v in bm.verts:
        if math.hypot(v.co.x, v.co.y) > 0.5:
            k = round((math.atan2(v.co.y, v.co.x) % (2 * math.pi)) / (2 * math.pi) * 480)
            s = 0.994 if k % 2 else 1.0; v.co.x *= s; v.co.y *= s
    bm.to_mesh(me); bm.free()
    bo = bpy.data.objects.new("Body", me); sc.collection.objects.link(bo); bo.parent = root; me.materials.append(body)
    bv = bo.modifiers.new("bev", "BEVEL"); bv.width = 0.006; bv.segments = 3; bv.limit_method = "ANGLE"
    for z in (0.06, -0.06):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.985, minor_radius=0.03, major_segments=320, minor_segments=24, location=(0, 0, z))
        r = bpy.context.active_object; r.scale.z = 0.8; r.parent = root; r.data.materials.append(body)
    for z, flip, res in ((0.058, False, 1300), (-0.058, True, 1300)):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=res, y_subdivisions=res, size=2 * 0.96, location=(0, 0, z))
        g = bpy.context.active_object; g.name = "FaceFront" if not flip else "FaceBack"
        bm = bmesh.new(); bm.from_mesh(g.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if math.hypot(v.co.x, v.co.y) > 0.96], context="VERTS")
        bm.to_mesh(g.data); bm.free()
        if flip: g.rotation_euler.y = math.pi; g.rotation_euler.z = math.pi
        g.parent = root; g.data.materials.append(face if not flip else back_face)
    for o in root.children:
        if o.type == "MESH":
            for p in o.data.polygons: p.use_smooth = True
    root.rotation_mode = "XYZ"
    for t, rz, rx in ((0, -3, 1.5), (13.3, 0.6, 2.0), (15.4, 1.5, 182.0), (28.5, 4.0, 182.5)):
        root.rotation_euler = (math.radians(rx), 0, math.radians(rz)); root.keyframe_insert("rotation_euler", frame=F(t))
    for t, z in ((0, 0.0), (13.2, 0.0), (14.3, 0.55), (15.5, 0.0), (28.5, 0.0)):
        root.location = (0, 0, z); root.keyframe_insert("location", frame=F(t))

    # ========================================================== STORY KEYS
    KEY(nt, "P_diya", [(1.8, 0), (4.6, 1)])
    KEY(nt, "spark", [(5.9, 0), (6.2, 1), (9.6, 1), (10.2, 0)])
    KEY(nt, "trace", [(6.3, 0), (9.6, 1), (10.0, 1), (10.8, 0)])
    KEY(nt, "arc_on", [(6.6, 0), (7.0, 1), (9.8, 1), (10.4, 0.35), (12.6, 0.35), (13.1, 0)])
    KEY(nt, "P_lotus", [(0.0, 0)])
    KEY(nt, "P_rupee", [(0.0, 0)])
    KEY(bnt, "crack", [(0.0, 0), (22.9, 0), (23.4, 1), (24.1, 3.5)])
    KEY(bn, "fuse", [(0, -0.2), (21.3, -0.2), (22.5, 1.0)])

    # ========================================================== LIGHT + WORLD (Bhutan: one hard raking key, cool rim, teal-black void)
    tgt = bpy.data.objects.new("LightTarget", None); sc.collection.objects.link(tgt)
    def light(name, kind, loc, power, color, size=1.0, vol=0.0):
        ld = bpy.data.lights.new(name, kind); ld.energy = power; ld.color = color; ld.volume_factor = vol
        if kind == "AREA": ld.size = size
        ob = bpy.data.objects.new(name, ld); sc.collection.objects.link(ob); ob.location = loc
        c = ob.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
        return ob
    light("Key", "AREA", (4.6, -2.2, 1.0), 1100, (1.0, 0.88, 0.72), 1.6, vol=1.0)
    light("Rim", "AREA", (-3.6, 3.4, 1.4), 650, (0.62, 0.86, 1.0), 1.6)
    light("Under", "AREA", (1.2, -1.4, -3.4), 160, (0.7, 0.85, 1.0), 3)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 9)); refl = bpy.context.active_object; refl.name = "Reflector"
    refl.scale = (14, 14, 1); refl.visible_camera = False; refl.visible_volume_scatter = False
    rm = bpy.data.materials.new("Reflector"); rm.use_nodes = True; rn = rm.node_tree; rn.nodes.remove(rn.nodes["Principled BSDF"])
    em = node(rn, "ShaderNodeEmission"); gt = node(rn, "ShaderNodeTexGradient"); rtc = node(rn, "ShaderNodeTexCoord")
    L(rn, rtc.outputs["Generated"], gt.inputs[0]); cr = node(rn, "ShaderNodeValToRGB"); L(rn, gt.outputs["Fac"], cr.inputs[0])
    cr.color_ramp.elements[0].color = (0, 0, 0, 1); cr.color_ramp.elements[1].color = (0.8, 0.85, 0.9, 1); cr.color_ramp.elements[1].position = 0.9
    L(rn, cr.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = 0.1
    L(rn, em.outputs[0], rn.nodes["Material Output"].inputs["Surface"]); refl.data.materials.append(rm)
    world = bpy.data.worlds.new("W"); sc.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.0012, 0.0018, 0.0022, 1)
    # textured dome: dark teal smoke, very few soft specks
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=30); dome = bpy.context.active_object; dome.name = "Dome"
    dome.visible_shadow = False; dome.visible_glossy = False; dome.visible_diffuse = False
    dm = bpy.data.materials.new("Dome"); dm.use_nodes = True; dn2 = dm.node_tree; dn2.nodes.remove(dn2.nodes["Principled BSDF"])
    dtc = node(dn2, "ShaderNodeTexCoord"); sm = node(dn2, "ShaderNodeTexNoise"); sm.inputs["Scale"].default_value = 0.3; sm.inputs["Detail"].default_value = 12
    L(dn2, dtc.outputs["Object"], sm.inputs["Vector"])
    sr = node(dn2, "ShaderNodeValToRGB"); L(dn2, sm.outputs["Fac"], sr.inputs[0])
    sr.color_ramp.elements[0].position = 0.4; sr.color_ramp.elements[0].color = (0.0006, 0.0010, 0.0013, 1)
    sr.color_ramp.elements[1].position = 0.8; sr.color_ramp.elements[1].color = (0.006, 0.010, 0.012, 1)
    sp = node(dn2, "ShaderNodeTexVoronoi"); sp.inputs["Scale"].default_value = 3.0; L(dn2, dtc.outputs["Object"], sp.inputs["Vector"])
    tw = node(dn2, "ShaderNodeTexNoise"); tw.inputs["Scale"].default_value = 1.2; L(dn2, dtc.outputs["Object"], tw.inputs["Vector"])
    speck = M(dn2, "MULTIPLY", MR(dn2, sp.outputs["Distance"], 0.035, 0.0), MR(dn2, tw.outputs["Fac"], 0.66, 0.72))
    de = node(dn2, "ShaderNodeEmission"); L(dn2, CMIX(dn2, speck, sr.outputs["Color"], (0.9, 0.75, 0.55, 1)), de.inputs["Color"])
    de.inputs["Strength"].default_value = 1.0; L(dn2, de.outputs[0], dn2.nodes["Material Output"].inputs["Surface"]); dome.data.materials.append(dm)
    bpy.ops.mesh.primitive_cube_add(size=18); haze = bpy.context.active_object; haze.name = "Haze"; haze.visible_shadow = False
    hm = bpy.data.materials.new("Haze"); hm.use_nodes = True; hn = hm.node_tree; hn.nodes.remove(hn.nodes["Principled BSDF"])
    vs = node(hn, "ShaderNodeVolumeScatter"); vs.inputs["Density"].default_value = 0.0007; vs.inputs["Anisotropy"].default_value = 0.6
    L(hn, vs.outputs[0], hn.nodes["Material Output"].inputs["Volume"]); haze.data.materials.append(hm)
    # sparse dust in the key light
    random.seed(3); bm = bmesh.new()
    for i in range(70):
        r = 0.9 + random.random() * 2.4; th = random.random() * 2 * math.pi; ph = math.acos(2 * random.random() - 1)
        c = Vector((r * math.sin(ph) * math.cos(th), r * math.sin(ph) * math.sin(th), r * math.cos(ph) * 0.5))
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.0015 + random.random() * 0.002, matrix=Matrix.Translation(c))
    dme = bpy.data.meshes.new("Dust"); bm.to_mesh(dme); bm.free(); dust = bpy.data.objects.new("Dust", dme); sc.collection.objects.link(dust)
    dmat = bpy.data.materials.new("Dust"); dmat.use_nodes = True; dbb = dmat.node_tree.nodes["Principled BSDF"]
    dbb.inputs["Emission Color"].default_value = (0.9, 0.85, 0.8, 1); dbb.inputs["Emission Strength"].default_value = 0.15; dme.materials.append(dmat)
    dust.visible_shadow = False

    # bijili pops: real light flashes at the rim (explicit 0 at t=0 so nothing leaks)
    for i, (t, a) in enumerate(((22.6, 40), (22.85, 170), (23.1, 290))):
        ld = bpy.data.lights.new("Pop%d" % i, "POINT"); ld.color = (1.0, 0.85, 0.65); ld.shadow_soft_size = 0.05
        ob = bpy.data.objects.new("Pop%d" % i, ld); sc.collection.objects.link(ob)
        ob.location = (1.05 * math.cos(math.radians(a)), 1.05 * math.sin(math.radians(a)), 0.05)
        for tt, e in ((0.0, 0), (t - 0.08, 0), (t, 3500), (t + 0.15, 0)):
            ld.energy = e; ld.keyframe_insert("energy", frame=F(tt))

    # ========================================================== EXPLOSION
    T0 = 24.1
    O = Vector((-0.95, 0.0))
    random.seed(7)
    def clip(poly, a, b):
        mid = (a + b) * 0.5; n = b - a; out = []
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            dp, dq = (p - mid).dot(n), (q - mid).dot(n)
            if dp <= 0: out.append(p)
            if (dp <= 0) != (dq <= 0): out.append(p + (q - p) * (dp / (dp - dq)))
        return out
    circle = [Vector((math.cos(i / 128 * 2 * math.pi), math.sin(i / 128 * 2 * math.pi))) for i in range(128)]
    HERO = 5
    seeds = []
    while len(seeds) < 38:
        v = Vector((random.uniform(-1, 1), random.uniform(-1, 1)))
        if v.length < 0.97: seeds.append(v)
    shard_face = face.copy(); shard_face.name = "ShardFace"
    snt = shard_face.node_tree
    if snt.animation_data: snt.animation_data_clear()
    for n_, v in (("P_diya", 1), ("P_lotus", 1), ("P_rupee", 1), ("arc_on", 0), ("trace", 0), ("spark", 0), ("crack", 0)):
        snt.nodes[n_].outputs[0].default_value = v
    edge_m = bpy.data.materials.new("ShardEdge"); edge_m.use_nodes = True; edge_m.displacement_method = "BOTH"
    en = edge_m.node_tree; eb = en.nodes["Principled BSDF"]
    etc = node(en, "ShaderNodeTexCoord"); enz = node(en, "ShaderNodeTexNoise"); enz.inputs["Scale"].default_value = 40; enz.inputs["Detail"].default_value = 8
    L(en, etc.outputs["Object"], enz.inputs["Vector"])
    ed = node(en, "ShaderNodeDisplacement"); ed.inputs["Scale"].default_value = 0.012; L(en, enz.outputs["Fac"], ed.inputs["Height"])
    L(en, ed.outputs[0], en.nodes["Material Output"].inputs["Displacement"])
    eb.inputs["Base Color"].default_value = (0.13, 0.085, 0.045, 1); eb.inputs["Metallic"].default_value = 1.0; eb.inputs["Roughness"].default_value = 0.45
    heat = VAL(en, "heat", 0.0)
    ecol = node(en, "ShaderNodeValToRGB"); L(en, M(en, "MULTIPLY", enz.outputs["Fac"], heat), ecol.inputs[0])
    ecol.color_ramp.elements[0].color = (0, 0, 0, 1); ecol.color_ramp.elements[1].color = (1.0, 0.45, 0.1, 1)
    L(en, ecol.outputs[0], eb.inputs["Emission Color"]); L(en, M(en, "MULTIPLY", heat, 1.6), eb.inputs["Emission Strength"])
    KEY(en, "heat", [(0.0, 1.0), (T0, 1.0), (T0 + 1.5, 0.35), (28.5, 0.04)])
    for i, s in enumerate(seeds):
        poly = circle[:]
        for j, o in enumerate(seeds):
            if i != j: poly = clip(poly, s, o)
            if len(poly) < 3: break
        if len(poly) < 3: continue
        me = bpy.data.meshes.new("Shard%d" % i); bm = bmesh.new()
        top = [bm.verts.new((p.x, p.y, 0.058)) for p in poly]; bot = [bm.verts.new((p.x, p.y, -0.058)) for p in poly]
        ft = bm.faces.new(top); fb = bm.faces.new(bot[::-1]); ft.material_index = 0; fb.material_index = 0
        for k in range(len(poly)):
            f = bm.faces.new((top[k], bot[k], bot[(k + 1) % len(poly)], top[(k + 1) % len(poly)])); f.material_index = 1
        bmesh.ops.triangulate(bm, faces=[ft])
        uvl = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x / 1.92 + 0.5, lp.vert.co.y / 1.92 + 0.5)
        bm.to_mesh(me); bm.free(); me.materials.append(shard_face); me.materials.append(edge_m)
        ob = bpy.data.objects.new("Shard%d" % i, me); sc.collection.objects.link(ob)
        sub = ob.modifiers.new("sub", "SUBSURF"); sub.subdivision_type = "SIMPLE"; sub.levels = sub.render_levels = 5
        c = sum(poly, Vector((0, 0))) / len(poly)
        for v in me.vertices: v.co.x -= c.x; v.co.y -= c.y
        ob.location = (c.x, c.y, 0)
        rel = c - O; dist = rel.length
        d = (Vector((rel.x, rel.y, 0)).normalized() * 0.6 + Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized()).normalized()
        spd = random.uniform(3.5, 7.0)
        if i == HERO: d = (Vector((0.22, -3.0, 1.0)) - Vector((c.x, c.y, 0))).normalized(); spd = 5.2
        spin = Vector((random.uniform(-4, 4), random.uniform(-4, 4), random.uniform(-2, 2)))
        rel_t = T0 + dist * 0.05
        ob.hide_render = True; ob.keyframe_insert("hide_render", frame=F(T0) - 1)
        ob.hide_render = False; ob.keyframe_insert("hide_render", frame=F(T0))
        for t, s_ in ((T0, 0.0), (rel_t, 0.0), (rel_t + 0.15, 0.22), (rel_t + 0.8, 0.75), (28.5, 2.6)):
            ob.location = Vector((c.x, c.y, 0)) + d * spd * s_
            ob.rotation_euler = (spin.x * s_, spin.y * s_, spin.z * s_)
            ob.keyframe_insert("location", frame=F(t)); ob.keyframe_insert("rotation_euler", frame=F(t))
    for o in [root] + list(root.children):
        o.hide_render = False; o.keyframe_insert("hide_render", frame=F(T0) - 1)
        o.hide_render = True; o.keyframe_insert("hide_render", frame=F(T0))
    # sparks: thin blackbody streaks, varied heat, gravity arcs
    spm = bpy.data.materials.new("Spark"); spm.use_nodes = True; spn = spm.node_tree; spn.nodes.remove(spn.nodes["Principled BSDF"])
    spe = node(spn, "ShaderNodeEmission"); oi = node(spn, "ShaderNodeObjectInfo")
    bb_ = node(spn, "ShaderNodeBlackbody"); L(spn, M(spn, "ADD", 1700, M(spn, "MULTIPLY", oi.outputs["Random"], 1700)), bb_.inputs["Temperature"])
    L(spn, bb_.outputs[0], spe.inputs["Color"]); glow = VAL(spn, "glow", 0.0)
    L(spn, M(spn, "MULTIPLY", glow, M(spn, "ADD", 0.4, oi.outputs["Random"])), spe.inputs["Strength"])
    L(spn, spe.outputs[0], spn.nodes["Material Output"].inputs["Surface"])
    KEY(spn, "glow", [(0.0, 26), (T0, 26), (T0 + 1.2, 10), (T0 + 3.0, 2), (28.5, 0)])
    for i in range(150):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=3, radius=0.0032)
        s_o = bpy.context.active_object; s_o.data.materials.append(spm); s_o.visible_shadow = False
        d = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized(); spd = random.uniform(5.0, 11.0)
        s_o.rotation_mode = "QUATERNION"; s_o.rotation_quaternion = d.to_track_quat("Z", "Y"); s_o.scale = (1, 1, random.uniform(3, 10))
        s_o.hide_render = True; s_o.keyframe_insert("hide_render", frame=F(T0) - 1)
        s_o.hide_render = False; s_o.keyframe_insert("hide_render", frame=F(T0))
        for t, s_ in ((T0, 0.0), (T0 + 0.25, 0.4), (T0 + 1.5, 0.9), (28.5, 1.8)):
            s_o.location = Vector((O.x, O.y, 0)) + d * spd * s_; s_o.keyframe_insert("location", frame=F(t))
    # Mantaflow fire + smoke
    bpy.ops.mesh.primitive_cube_add(size=7, location=(0, 0, 1.2)); dom = bpy.context.active_object; dom.name = "FireDomain"
    fm = dom.modifiers.new("Fluid", "FLUID"); fm.fluid_type = "DOMAIN"; ds = fm.domain_settings
    ds.domain_type = "GAS"; ds.resolution_max = 128; ds.use_noise = True; ds.noise_scale = 2; ds.noise_strength = 1.4; ds.use_adaptive_domain = True; ds.time_scale = 0.35
    ds.cache_directory = os.path.join(HERE, "firecache"); ds.cache_type = "ALL"
    ds.cache_frame_start = F(T0); ds.cache_frame_end = F(28.5); ds.use_dissolve_smoke = True; ds.dissolve_speed = 22
    ds.vorticity = 0.55; ds.flame_vorticity = 1.0; ds.burning_rate = 0.65; ds.flame_smoke = 1.2
    fmat = bpy.data.materials.new("Fire"); fmat.use_nodes = True; fn = fmat.node_tree; fn.nodes.remove(fn.nodes["Principled BSDF"])
    pv = node(fn, "ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (0.16, 0.13, 0.1, 1); pv.inputs["Density"].default_value = 1.6
    fa = node(fn, "ShaderNodeAttribute"); fa.attribute_name = "flame"
    fr = node(fn, "ShaderNodeValToRGB"); L(fn, fa.outputs["Fac"], fr.inputs[0]); el = fr.color_ramp.elements
    el[0].position = 0.0; el[0].color = (0.35, 0.05, 0.0, 1); el[1].position = 1.0; el[1].color = (1.0, 0.92, 0.7, 1)
    for pos, col in ((0.3, (0.9, 0.16, 0.01, 1)), (0.55, (1.0, 0.42, 0.05, 1)), (0.8, (1.0, 0.7, 0.25, 1))):
        e = el.new(pos); e.color = col
    L(fn, fr.outputs["Color"], pv.inputs["Emission Color"]); L(fn, M(fn, "MULTIPLY", M(fn, "POWER", fa.outputs["Fac"], 1.5), 11.0), pv.inputs["Emission Strength"])
    L(fn, pv.outputs[0], fn.nodes["Material Output"].inputs["Volume"]); dom.data.materials.append(fmat)
    dom.hide_render = True; dom.keyframe_insert("hide_render", frame=1); dom.keyframe_insert("hide_render", frame=F(T0) - 1)
    dom.hide_render = False; dom.keyframe_insert("hide_render", frame=F(T0))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(O.x, O.y, 0)); fl = bpy.context.active_object; fl.name = "FireFlow"
    ff = fl.modifiers.new("Fluid", "FLUID"); ff.fluid_type = "FLOW"; fs = ff.flow_settings
    fs.flow_type = "BOTH"; fs.flow_behavior = "INFLOW"; fs.fuel_amount = 1.6; fs.temperature = 3.2; fs.smoke_color = (0.22, 0.18, 0.14); fs.density = 1.0; fs.use_initial_velocity = True; fs.velocity_normal = 4.0
    fl.hide_render = True
    for t, s_ in ((0.0, 0.001), (T0 - 0.05, 0.001), (T0, 1.0), (T0 + 0.25, 1.0), (T0 + 0.35, 0.001)):
        fl.scale = (s_, s_, s_); fl.keyframe_insert("scale", frame=F(t))
    pf = bpy.data.lights.new("PreFlash", "POINT"); pf.color = (1.0, 0.95, 0.85); pf.shadow_soft_size = 0.3
    pfo = bpy.data.objects.new("PreFlash", pf); sc.collection.objects.link(pfo); pfo.location = (0, 0, 0.15)
    for t, e in ((0.0, 0), (23.3, 0), (24.08, 2500), (24.3, 0)):
        pf.energy = e; pf.keyframe_insert("energy", frame=F(t))
    bl = bpy.data.lights.new("BlastLight", "POINT"); bl.color = (1.0, 0.62, 0.25); bl.shadow_soft_size = 0.5; bl.volume_factor = 0.1
    blo = bpy.data.objects.new("BlastLight", bl); sc.collection.objects.link(blo); blo.location = (O.x, O.y, 0.1)
    for t, e in ((0.0, 0), (T0 - 0.1, 0), (T0, 6000), (T0 + 0.25, 3000), (T0 + 1.0, 600), (T0 + 2.0, 60), (28.5, 0)):
        bl.energy = e; bl.keyframe_insert("energy", frame=F(t))

    # ========================================================== 3D TITLE (bevelled brass, behind the debris)
    FT = os.path.normpath(os.path.join(HERE, "..", "..", "fonts"))
    tall = bpy.data.fonts.load(os.path.join(FT, "Tall", "TheBlock-font", "theblock-regular.ttf"))
    sans = bpy.data.fonts.load(os.path.join(FT, "Normal", "Opensauce one", "OpenSauceSans-SemiBold.ttf"))
    tmat = bpy.data.materials.new("TitleBrass"); tmat.use_nodes = True; tn = tmat.node_tree; tb = tn.nodes["Principled BSDF"]
    tb.inputs["Base Color"].default_value = (0.86, 0.67, 0.42, 1); tb.inputs["Metallic"].default_value = 1.0
    ttc = node(tn, "ShaderNodeTexCoord"); tnz = node(tn, "ShaderNodeTexNoise"); tnz.inputs["Scale"].default_value = 60
    L(tn, ttc.outputs["Object"], tnz.inputs["Vector"]); L(tn, MR(tn, tnz.outputs["Fac"], 0.3, 0.7, 0.17, 0.22), tb.inputs["Roughness"])
    smat = bpy.data.materials.new("TitleSmall"); smat.use_nodes = True; sb = smat.node_tree.nodes["Principled BSDF"]
    sb.inputs["Base Color"].default_value = (0.9, 0.86, 0.8, 1); sb.inputs["Emission Color"].default_value = (0.92, 0.88, 0.82, 1); sb.inputs["Emission Strength"].default_value = 1.4
    def text(body, font, size, ext, bev, mat, spacing=1.0):
        cu = bpy.data.curves.new(body, "FONT"); cu.body = body; cu.font = font; cu.size = size; cu.extrude = ext
        cu.bevel_depth = bev; cu.bevel_resolution = 4; cu.align_x = "CENTER"; cu.align_y = "CENTER"; cu.space_character = spacing
        ob = bpy.data.objects.new(body, cu); sc.collection.objects.link(ob); cu.materials.append(mat)
        ob.rotation_euler = (math.radians(90), 0, math.radians(180))
        return ob
    TT = 23.0
    big = text("EXPENSIVE", tall, 1.9, 0.11, 0.022, tmat)
    top = text("THE MOST", sans, 0.17, 0.0, 0.0, smat, 1.9)
    low = text("FESTIVAL IN INDIA", sans, 0.17, 0.0, 0.0, smat, 1.9)
    for ob in (big, top, low):
        ob.hide_render = True; ob.keyframe_insert("hide_render", frame=1); ob.keyframe_insert("hide_render", frame=F(TT) - 1)
        ob.hide_render = False; ob.keyframe_insert("hide_render", frame=F(TT))
    for t, z, sx in ((TT, -0.3, 1.06), (24.6, 0.62, 1.0), (27.0, 0.66, 0.985)):
        big.location = (0, -2.6, z); big.scale = (sx, sx, sx); big.keyframe_insert("location", frame=F(t)); big.keyframe_insert("scale", frame=F(t))
    top.location = (0, -2.6, 1.52); low.location = (0, -2.6, -0.18)
    for ob in (top, low):
        for t, sx in ((0.0, 0.001), (24.4, 0.001), (25.0, 1.0)):
            ob.scale = (sx, sx, sx); ob.keyframe_insert("scale", frame=F(t))
    for nm_, loc_, col_, sz_, peak in (("TitleKey", (2.8, 1.2, 3.0), (1.0, 0.9, 0.78), 3, 900), ("TitleRim", (-3.0, -4.5, 2.2), (0.6, 0.85, 1.0), 2, 600)):
        ld = bpy.data.lights.new(nm_, "AREA"); ld.size = sz_; ld.color = col_
        lo = bpy.data.objects.new(nm_, ld); sc.collection.objects.link(lo); lo.location = loc_
        c_ = lo.constraints.new("TRACK_TO"); c_.target = big; c_.track_axis = "TRACK_NEGATIVE_Z"; c_.up_axis = "UP_Y"
        for t, e in ((0.0, 0), (TT - 0.05, 0), (24.4, peak), (27.0, peak)):
            ld.energy = e; ld.keyframe_insert("energy", frame=F(t))

    # title is built in After Effects: remove the 3D title and its lights
    for n_ in ("TitleKey", "TitleRim", "EXPENSIVE", "THE MOST", "FESTIVAL IN INDIA"):
        o_ = bpy.data.objects.get(n_)
        if o_: bpy.data.objects.remove(o_, do_unlink=True)

    # ========================================================== CAMERAS: 6 long shots + locked morph cam
    def aim(cam, loc, tgt_, roll=0):
        cam.location = loc; q = (Vector(tgt_) - Vector(loc)).to_track_quat("-Z", "Y"); cam.rotation_mode = "XYZ"
        cam.rotation_euler = q.to_euler(); cam.rotation_euler.rotate_axis("Z", math.radians(roll))
    SHOTS = [
        ("S1_push", 0.0, 5.5, 50, 5.6, [(0.0, (0.0, -0.05, 8.2), (0, 0, 0)), (2.6, (2.4, -3.3, 2.6), (0, 0, 0)), (5.5, (1.7, -2.3, 0.62), (0, 0.15, 0.05))]),
        ("S2_macro", 5.5, 10.0, 70, 8.0, [(5.5, (-0.95, -1.2, 0.62), (0, 0.3, 0.08)), (10.0, (0.35, -1.0, 0.52), (0, 0.42, 0.09))]),
        ("S3_diyahero", 10.0, 13.0, 50, 6.3, [(10.0, (0.35, -1.1, 1.1), (0, 0.1, 0)), (13.0, (-1.4, -2.3, 1.35), (0, 0, 0))]),
        ("S4_flip", 13.0, 15.5, 50, 6.3, [(13.0, (0.5, -3.7, 0.75), (0, 0, 0.25)), (15.5, (0.2, -3.2, 1.0), (0, 0, 0.1))]),
        ("S5_rupeemacro", 15.5, 18.5, 70, 8.0, [(15.5, (-0.75, -1.0, 0.6), (0, 0.05, 0.07)), (18.5, (0.55, -0.95, 0.55), (0, 0.0, 0.07))]),
        ("S6_rupeehero", 18.5, 21.0, 60, 6.3, [(18.5, (1.7, -2.3, 0.35), (0, 0, 0.05)), (21.0, (0.9, -2.5, 1.05), (0, 0, 0))]),
        ("S7_fuse", 21.0, 23.5, 50, 6.3, [(21.0, (0.4, -3.6, 1.3), (0, 0, 0)), (23.5, (0.25, -3.0, 1.0), (-0.2, 0, 0.1))]),
        ("S8_blast", 23.5, 28.5, 42, 6.3, [(23.5, (0.25, -3.0, 1.0), (-0.2, 0, 0.1)), (28.5, (0.22, -3.2, 1.05), (-0.2, 0, 0.1))]),
    ]
    cams = []
    for name, t0, t1, lens, fstop, path in SHOTS:
        cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.01
        cam = bpy.data.objects.new(name, cd); sc.collection.objects.link(cam)
        foc = bpy.data.objects.new(name + "_focus", None); sc.collection.objects.link(foc)
        for t, loc, tg in path:
            aim(cam, loc, tg); cam.keyframe_insert("location", frame=F(t)); cam.keyframe_insert("rotation_euler", frame=F(t))
            foc.location = tg; foc.keyframe_insert("location", frame=F(t))
        cd.dof.use_dof = True; cd.dof.focus_object = foc; cd.dof.aperture_fstop = fstop
        m = sc.timeline_markers.new(name, frame=F(t0)); m.camera = cam
        cams.append(name)
    for name, t0, ev in (("S1_push", 0.0, -0.3), ("S2_macro", 5.5, 0.3), ("S3_diyahero", 10.0, -0.1), ("S4_flip", 13.0, -0.2), ("S5_rupeemacro", 15.5, 0.2), ("S6_rupeehero", 18.5, -0.1), ("S7_fuse", 21.0, -0.4), ("S8_blast", 23.5, -0.6)):
        sc.view_settings.exposure = ev; sc.view_settings.keyframe_insert("exposure", frame=F(t0))
    cdm = bpy.data.cameras.new("morph_top"); cdm.lens = 50
    cm = bpy.data.objects.new("morph_top", cdm); sc.collection.objects.link(cm); aim(cm, (0, -0.5, 5.0), (0, 0, 0))
    sc.camera = bpy.data.objects[cams[0]]
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "coin3.blend"))
    print("SAVED", flush=True)

SHOT_TABLE = [("S1_push", 0.0, 5.5), ("S2_macro", 5.5, 10.0), ("S3_diyahero", 10.0, 13.0), ("S4_flip", 13.0, 15.5), ("S5_rupeemacro", 15.5, 18.5), ("S6_rupeehero", 18.5, 21.0), ("S7_fuse", 21.0, 23.5), ("S8_blast", 23.5, 28.51)]

if MODE == "build":
    build()
elif MODE == "bake":
    dom = bpy.data.objects["FireDomain"]
    for o in sc.objects: o.select_set(False)
    dom.select_set(True); bpy.context.view_layer.objects.active = dom
    with bpy.context.temp_override(active_object=dom, object=dom):
        bpy.ops.fluid.bake_all()
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "coin3_baked.blend"))
    print("BAKED", flush=True)
elif MODE == "sheet":
    OUT = argv[1]; os.makedirs(OUT, exist_ok=True)
    sc.cycles.samples = 64; sc.render.resolution_percentage = 67
    sc.render.image_settings.file_format = "PNG"
    for mk in sc.timeline_markers: mk.camera = None
    times = [float(x) for x in argv[2].split(",")] if len(argv) > 2 else [i + 0.5 for i in range(27)]
    for t in times:
        name = [n for n, a, b in SHOT_TABLE if a <= t < b][0]
        sc.frame_set(F(t)); sc.camera = bpy.data.objects[name]
        sc.render.filepath = os.path.join(OUT, "t%05.2f_%s.png" % (t, name))
        bpy.ops.render.render(write_still=True); print("SHEET", t, name, flush=True)
    if len(argv) <= 2:
        sc.camera = bpy.data.objects["morph_top"]
        for t in (1.5, 2.6, 3.4, 4.6, 11.2, 12.0, 12.8, 14.0, 15.6, 16.4, 17.2, 18.4):
            sc.frame_set(F(t)); sc.render.filepath = os.path.join(OUT, "morph_t%05.2f.png" % t)
            bpy.ops.render.render(write_still=True); print("MORPH", t, flush=True)
    print("DONE", flush=True)
elif MODE == "animatic":
    OUT = argv[1]; os.makedirs(OUT, exist_ok=True)
    sc.cycles.samples = 10; sc.render.resolution_percentage = 34; sc.render.use_motion_blur = False
    sc.cycles.max_bounces = 4; sc.render.image_settings.file_format = "JPEG"
    for mk in sc.timeline_markers: mk.camera = None
    for f in range(sc.frame_start, sc.frame_end + 1):
        path = os.path.join(OUT, "a_%04d.jpg" % f)
        if os.path.exists(path): continue
        t = (f - 1) / FPS
        sc.frame_set(f); sc.camera = bpy.data.objects[[n for n, a, b in SHOT_TABLE if a <= t < b][0]]
        sc.render.filepath = path; bpy.ops.render.render(write_still=True); print("ANIM", f, flush=True)
    print("ADONE", flush=True)
