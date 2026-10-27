"""vfx_lib: reusable Blender 5.x building blocks for cinematic CGI intros (Cycles, OptiX).
Import from a scene script:   sys.path.insert(0, LIB_DIR); from vfx_lib import *
Every helper is plain bpy, works headless (blender -b). Times are in SECONDS; F(t) converts to frames.
Proven on: The Dhanteras Coin (brass relief coin, electric arcs, fuse, cracks, centre blast, smoke, 38s)."""
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix

FPS = 24
def F(t): return t * FPS + 1                     # float frame (sub-frame accurate)
def Fi(t): return int(round(t * FPS)) + 1        # integer frame

# ------------------------------------------------------------------ render setup
def gpu(scene=None):
    """OptiX on NVIDIA (CPU fallback is ~17x slower: always check it took)."""
    sc = scene or bpy.context.scene
    pr = bpy.context.preferences.addons["cycles"].preferences
    try:
        pr.compute_device_type = "OPTIX"; pr.get_devices()
        for d in pr.devices: d.use = (d.type == "OPTIX")
    except Exception: pass
    sc.cycles.device = "GPU"

def cinema_setup(sc, w=1920, h=804, samples=48, end_t=10.0, exposure=-0.3):
    """2.39:1 scope, AgX, motion blur, OptiX denoise, persistent data (big speed win for sequences)."""
    sc.render.engine = "CYCLES"; sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, Fi(end_t)
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = exposure
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
    sc.cycles.samples = samples; sc.cycles.use_denoising = True; sc.cycles.denoiser = "OPTIX"
    sc.render.use_persistent_data = True
    sc.render.image_settings.file_format = "PNG"; sc.render.image_settings.color_depth = "16"

# ------------------------------------------------------------------ shader node helpers (compact graph building)
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
def CMIX(nt, fac, a, b):
    m = node(nt, "ShaderNodeMix", data_type="RGBA")
    for s, v in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
        if isinstance(v, (int, float, tuple)): s.default_value = v
        else: L(nt, v, s)
    return m.outputs[2]
def VAL(nt, name, v=0.0):
    """Named Value node = an animatable story control (keyframe it with KEY)."""
    n = node(nt, "ShaderNodeValue", label=name, name=name); n.outputs[0].default_value = v; return n.outputs[0]
def KEY(nt, name, pairs):
    o = nt.nodes[name].outputs[0]
    for t, v in pairs: o.default_value = v; o.keyframe_insert("default_value", frame=F(t))
def keyprop(owner, path, pairs, setter=None):
    for t, v in pairs:
        setattr(owner, path, v); owner.keyframe_insert(path, frame=F(t))

# ------------------------------------------------------------------ animation data (Blender 5 slotted actions!)
def fcurves(idb):
    """Blender 5: action.fcurves is gone. Use the channelbag of the assigned slot."""
    from bpy_extras import anim_utils
    ad = idb.animation_data
    if not ad or not ad.action: return []
    return list(anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves)
def cut_keys_after(idb, path, t):
    """Remove keys after time t (remove from the end: removing invalidates later key refs)."""
    for c in [c for c in fcurves(idb) if c.data_path == path]:
        while True:
            ks = [i for i, k in enumerate(c.keyframe_points) if k.co.x > F(t) - 0.01]
            if not ks: break
            c.keyframe_points.remove(c.keyframe_points[ks[-1]])
def clear_keys(idb, path):
    for c in [c for c in fcurves(idb) if c.data_path == path]:
        while len(c.keyframe_points): c.keyframe_points.remove(c.keyframe_points[len(c.keyframe_points) - 1])

# ------------------------------------------------------------------ materials
def metal_material(name, base=(0.80, 0.57, 0.28), dark=(0.16, 0.10, 0.05), hi=(0.88, 0.68, 0.40),
                   height_img=None, disp_scale=0.05, bump=0.3):
    """Brass/gold/silver metal. Optional grayscale height map -> real displacement relief + cavity patina.
    Height maps: 4K, 16-bit, median-filtered (upscale grain shows as camo blotches otherwise)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; m.displacement_method = "BOTH"
    nt = m.node_tree; bs = nt.nodes["Principled BSDF"]; out = nt.nodes["Material Output"]
    tc = node(nt, "ShaderNodeTexCoord")
    bs.inputs["Metallic"].default_value = 1.0
    if height_img:
        im = node(nt, "ShaderNodeTexImage", extension="CLIP", interpolation="Cubic")
        im.image = bpy.data.images.load(height_img); im.image.colorspace_settings.name = "Non-Color"
        L(nt, tc.outputs["UV"], im.inputs["Vector"]); h = im.outputs["Color"]
        d = node(nt, "ShaderNodeDisplacement"); d.inputs["Midlevel"].default_value = 0.5; d.inputs["Scale"].default_value = disp_scale
        L(nt, h, d.inputs["Height"]); L(nt, d.outputs[0], out.inputs["Displacement"])
        b = node(nt, "ShaderNodeBump"); b.inputs["Strength"].default_value = bump; b.inputs["Distance"].default_value = 0.0025
        L(nt, h, b.inputs["Height"]); L(nt, b.outputs[0], bs.inputs["Normal"])
        cav = MR(nt, h, 0.35, 0.75)
        col = CMIX(nt, MR(nt, cav, 0.8, 1.0), CMIX(nt, cav, (*dark, 1), (*base, 1)), (*hi, 1))
        L(nt, col, bs.inputs["Base Color"]); L(nt, MR(nt, cav, 0.0, 1.0, 0.48, 0.16), bs.inputs["Roughness"])
    else:
        bs.inputs["Base Color"].default_value = (*base, 1)
        n = node(nt, "ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 60; L(nt, tc.outputs["Object"], n.inputs["Vector"])
        L(nt, MR(nt, n.outputs["Fac"], 0.3, 0.7, 0.17, 0.26), bs.inputs["Roughness"])
    return m

def add_energy_arcs(m, gate_name="arc_on", scale=3.2, core_gain=60.0, fringe_gain=7.0, fringe=(0.25, 0.8, 1.0)):
    """Electric arcs crawling over a surface: 4D Voronoi distance-to-edge, white core + cyan fringe.
    Animate with KEY(m.node_tree, gate_name, [(t, 0..1), ...])."""
    nt = m.node_tree; bs = nt.nodes["Principled BSDF"]; tc = nt.nodes.get("Texture Coordinate") or node(nt, "ShaderNodeTexCoord")
    obj = tc.outputs["Object"]
    vor = node(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE", voronoi_dimensions="4D"); vor.inputs["Scale"].default_value = scale
    dn = node(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); dn.inputs["Scale"].default_value = 6; L(nt, obj, dn.inputs["Vector"])
    dn.inputs["W"].driver_add("default_value").driver.expression = "frame/8"
    add = node(nt, "ShaderNodeVectorMath", operation="ADD"); L(nt, obj, add.inputs[0])
    s = node(nt, "ShaderNodeVectorMath", operation="SCALE"); s.inputs["Scale"].default_value = 0.35
    L(nt, dn.outputs["Color"], s.inputs[0]); L(nt, s.outputs[0], add.inputs[1]); L(nt, add.outputs[0], vor.inputs["Vector"])
    vor.inputs["W"].driver_add("default_value").driver.expression = "frame/5"
    gate = VAL(nt, gate_name, 0.0)
    patch = node(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); patch.inputs["Scale"].default_value = 1.6; L(nt, obj, patch.inputs["Vector"])
    patch.inputs["W"].driver_add("default_value").driver.expression = "frame/14"
    g = M(nt, "MULTIPLY", gate, MR(nt, patch.outputs["Fac"], 0.56, 0.64))
    core = M(nt, "MULTIPLY", MR(nt, vor.outputs["Distance"], 0.0035, 0.0), g)
    fr = M(nt, "MULTIPLY", MR(nt, vor.outputs["Distance"], 0.018, 0.002), g)
    c1 = node(nt, "ShaderNodeVectorMath", operation="SCALE"); c1.inputs[0].default_value = (1, 1, 1); L(nt, M(nt, "MULTIPLY", core, core_gain), c1.inputs["Scale"])
    c2 = node(nt, "ShaderNodeVectorMath", operation="SCALE"); c2.inputs[0].default_value = fringe; L(nt, M(nt, "MULTIPLY", fr, fringe_gain), c2.inputs["Scale"])
    e = node(nt, "ShaderNodeVectorMath", operation="ADD"); L(nt, c1.outputs[0], e.inputs[0]); L(nt, c2.outputs[0], e.inputs[1])
    L(nt, e.outputs[0], bs.inputs["Emission Color"]); bs.inputs["Emission Strength"].default_value = 1.0
    return m

def add_cracks(m, name="crack", scale=3.0, color=(1.0, 0.75, 0.45), gain=25.0):
    """Glowing crack network (Voronoi edges) that widens as KEY(nt, name, ...) rises 0 -> 3.5."""
    nt = m.node_tree; bs = nt.nodes["Principled BSDF"]; tc = nt.nodes.get("Texture Coordinate") or node(nt, "ShaderNodeTexCoord")
    v = node(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE"); v.inputs["Scale"].default_value = scale; L(nt, tc.outputs["Object"], v.inputs["Vector"])
    k = VAL(nt, name, 0.0)
    c = M(nt, "MULTIPLY", M(nt, "LESS_THAN", v.outputs["Distance"], M(nt, "MULTIPLY", k, 0.028)), k)
    s = node(nt, "ShaderNodeVectorMath", operation="SCALE"); s.inputs[0].default_value = color; L(nt, M(nt, "MULTIPLY", c, gain), s.inputs["Scale"])
    if bs.inputs["Emission Color"].is_linked:
        a = node(nt, "ShaderNodeVectorMath", operation="ADD"); L(nt, bs.inputs["Emission Color"].links[0].from_socket, a.inputs[0])
        L(nt, s.outputs[0], a.inputs[1]); L(nt, a.outputs[0], bs.inputs["Emission Color"])
    else: L(nt, s.outputs[0], bs.inputs["Emission Color"])
    bs.inputs["Emission Strength"].default_value = 1.0
    return m

def key_emission(m, pairs, color=(1.0, 0.78, 0.5)):
    """White-hot -> cool: key the Principled emission (e.g. shards at the burst). Keep peaks LOW (2-4):
    high values blow out after the AE grade and hide the texture."""
    bs = [n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"][0]
    for inp in ("Emission Color", "Emission Strength"):
        for l in list(bs.inputs[inp].links): m.node_tree.links.remove(l)
    bs.inputs["Emission Color"].default_value = (*color, 1)
    for t, e in pairs:
        bs.inputs["Emission Strength"].default_value = e; bs.inputs["Emission Strength"].keyframe_insert("default_value", frame=F(t))

# ------------------------------------------------------------------ world / light (the 'premium dark void' look)
def light_rig(target=(0, 0, 0), key=(4.6, -2.2, 1.0, 1100), rim=(-3.6, 3.4, 1.4, 650), under=(1.2, -1.4, -3.4, 160)):
    """One hard warm raking key (shows relief), cool rim (separates from black), soft under-fill."""
    sc = bpy.context.scene
    tgt = bpy.data.objects.new("LightTarget", None); sc.collection.objects.link(tgt); tgt.location = target
    def light(name, x, y, z, p, col, size):
        ld = bpy.data.lights.new(name, "AREA"); ld.energy = p; ld.color = col; ld.size = size
        ob = bpy.data.objects.new(name, ld); sc.collection.objects.link(ob); ob.location = (x, y, z)
        c = ob.constraints.new("TRACK_TO"); c.target = tgt; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"; return ob
    return (light("Key", *key, (1.0, 0.88, 0.72), 1.6), light("Rim", *rim, (0.62, 0.86, 1.0), 1.6), light("Under", *under, (0.7, 0.85, 1.0), 3))

def dark_void(bg=(0.0012, 0.0018, 0.0022), haze_density=0.0007, dust=70):
    """Teal-black world + faint smoke dome + volumetric haze + sparse dust motes in the key light."""
    sc = bpy.context.scene
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs["Color"].default_value = (*bg, 1)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=48, radius=30); d = bpy.context.active_object; d.name = "Dome"
    d.visible_shadow = d.visible_glossy = d.visible_diffuse = False
    dm = bpy.data.materials.new("Dome"); dm.use_nodes = True; n = dm.node_tree; n.nodes.remove(n.nodes["Principled BSDF"])
    tc = node(n, "ShaderNodeTexCoord"); sm = node(n, "ShaderNodeTexNoise"); sm.inputs["Scale"].default_value = 0.3; sm.inputs["Detail"].default_value = 12
    L(n, tc.outputs["Object"], sm.inputs["Vector"]); r = node(n, "ShaderNodeValToRGB"); L(n, sm.outputs["Fac"], r.inputs[0])
    r.color_ramp.elements[0].position = 0.4; r.color_ramp.elements[0].color = (0.0006, 0.0010, 0.0013, 1)
    r.color_ramp.elements[1].position = 0.8; r.color_ramp.elements[1].color = (0.006, 0.010, 0.012, 1)
    e = node(n, "ShaderNodeEmission"); L(n, r.outputs["Color"], e.inputs["Color"]); L(n, e.outputs[0], n.nodes["Material Output"].inputs["Surface"])
    d.data.materials.append(dm)
    bpy.ops.mesh.primitive_cube_add(size=18); h = bpy.context.active_object; h.name = "Haze"; h.visible_shadow = False
    hm = bpy.data.materials.new("Haze"); hm.use_nodes = True; hn = hm.node_tree; hn.nodes.remove(hn.nodes["Principled BSDF"])
    vs = node(hn, "ShaderNodeVolumeScatter"); vs.inputs["Density"].default_value = haze_density; vs.inputs["Anisotropy"].default_value = 0.6
    L(hn, vs.outputs[0], hn.nodes["Material Output"].inputs["Volume"]); h.data.materials.append(hm)
    if dust:
        random.seed(3); bm = bmesh.new()
        for i in range(dust):
            r_ = 0.9 + random.random() * 2.4; th = random.random() * 6.283; ph = math.acos(2 * random.random() - 1)
            c = Vector((r_ * math.sin(ph) * math.cos(th), r_ * math.sin(ph) * math.sin(th), r_ * math.cos(ph) * 0.5))
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.0015 + random.random() * 0.002, matrix=Matrix.Translation(c))
        me = bpy.data.meshes.new("Dust"); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new("Dust", me); sc.collection.objects.link(o)
        mt = bpy.data.materials.new("Dust"); mt.use_nodes = True; b = mt.node_tree.nodes["Principled BSDF"]
        b.inputs["Emission Color"].default_value = (0.9, 0.85, 0.8, 1); b.inputs["Emission Strength"].default_value = 0.15; me.materials.append(mt); o.visible_shadow = False

# ------------------------------------------------------------------ hero objects
def disc(name="Coin", radius=1.0, depth=0.116, reeding=480, face_mat=None, body_mat=None, back_mat=None, face_res=600):
    """Coin / medallion / plate: reeded edge, bevelled rims, dense relief grids on both faces (res 1300 for macro)."""
    sc = bpy.context.scene
    root = bpy.data.objects.new(name, None); sc.collection.objects.link(root)
    me = bpy.data.meshes.new(name + "Body"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=False, segments=reeding, radius1=radius, radius2=radius, depth=depth)   # cap_ends=False: a cap above the relief causes 'camo' blotches
    for v in bm.verts:
        k = round((math.atan2(v.co.y, v.co.x) % 6.2832) / 6.2832 * reeding); s = 0.994 if k % 2 else 1.0; v.co.x *= s; v.co.y *= s
    bm.to_mesh(me); bm.free(); bo = bpy.data.objects.new(name + "Body", me); sc.collection.objects.link(bo); bo.parent = root
    if body_mat: me.materials.append(body_mat)
    bv = bo.modifiers.new("bev", "BEVEL"); bv.width = 0.006; bv.segments = 3; bv.limit_method = "ANGLE"
    for z in (depth / 2, -depth / 2):
        bpy.ops.mesh.primitive_torus_add(major_radius=radius * 0.985, minor_radius=0.03, major_segments=320, minor_segments=24, location=(0, 0, z))
        r = bpy.context.active_object; r.scale.z = 0.8; r.parent = root
        if body_mat: r.data.materials.append(body_mat)
    for z, flip, mat in ((depth / 2 - 0.0, False, face_mat), (-depth / 2, True, back_mat or face_mat)):
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=face_res, y_subdivisions=face_res, size=2 * radius * 0.96, location=(0, 0, z))
        g = bpy.context.active_object; g.name = name + ("Back" if flip else "Front")
        bm = bmesh.new(); bm.from_mesh(g.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if math.hypot(v.co.x, v.co.y) > radius * 0.96], context="VERTS"); bm.to_mesh(g.data); bm.free()
        if flip: g.rotation_euler = (math.pi, 0, math.pi)       # y=pi AND z=pi: back relief reads upright after a flip
        g.parent = root
        if mat: g.data.materials.append(mat)
    for o in root.children:
        if o.type == "MESH":
            for p in o.data.polygons: p.use_smooth = True
    root.rotation_mode = "XYZ"
    return root

# ------------------------------------------------------------------ destruction
def fracture_disc(face_mat, edge_mat, n=38, radius=0.97, thick=0.058, seed=7, subsurf=5):
    """Voronoi-fracture a disc into n flat shards (top = engraved face material, sides = dark edge)."""
    sc = bpy.context.scene; random.seed(seed)
    circle = [Vector((math.cos(i / 128 * 6.2832), math.sin(i / 128 * 6.2832))) for i in range(128)]
    def clip(poly, a, b):
        mid = (a + b) * 0.5; nn = b - a; out = []
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]; dp, dq = (p - mid).dot(nn), (q - mid).dot(nn)
            if dp <= 0: out.append(p)
            if (dp <= 0) != (dq <= 0): out.append(p + (q - p) * (dp / (dp - dq)))
        return out
    seeds = []
    while len(seeds) < n:
        v = Vector((random.uniform(-1, 1), random.uniform(-1, 1)))
        if v.length < radius: seeds.append(v)
    shards = []
    for i, s in enumerate(seeds):
        poly = circle[:]
        for j, o in enumerate(seeds):
            if i != j: poly = clip(poly, s, o)
            if len(poly) < 3: break
        if len(poly) < 3: continue
        me = bpy.data.meshes.new("Shard%d" % i); bm = bmesh.new()
        top = [bm.verts.new((p.x, p.y, thick)) for p in poly]; bot = [bm.verts.new((p.x, p.y, -thick)) for p in poly]
        bm.faces.new(top); bm.faces.new(bot[::-1])
        for k in range(len(poly)): bm.faces.new((top[k], bot[k], bot[(k + 1) % len(poly)], top[(k + 1) % len(poly)])).material_index = 1
        uvl = bm.loops.layers.uv.new("UVMap")
        for f in bm.faces:
            for lp in f.loops: lp[uvl].uv = (lp.vert.co.x / 1.92 + 0.5, lp.vert.co.y / 1.92 + 0.5)
        bm.to_mesh(me); bm.free(); me.materials.append(face_mat); me.materials.append(edge_mat)
        ob = bpy.data.objects.new("Shard%d" % i, me); sc.collection.objects.link(ob)
        sub = ob.modifiers.new("sub", "SUBSURF"); sub.subdivision_type = "SIMPLE"; sub.levels = sub.render_levels = subsurf
        c = sum(poly, Vector((0, 0))) / len(poly)
        for v in me.vertices: v.co.x -= c.x; v.co.y -= c.y
        ob.location = (c.x, c.y, 0); shards.append(ob)
    return shards

def blast(objects, T0, cam_pos, centre=(0, 0, 0), toward_cam=3, end_t=None, speed=(1.4, 2.6), seed=11, pass_names=None):
    """Zero-gravity space burst from the CENTRE. Most pieces go out 360 and leave the frame sideways;
    only `toward_cam` pieces aim at a ring AROUND the lens (never down the lens axis: those look frozen).
    Hidden before T0. Ease: fast kick (0.06s), long glide."""
    random.seed(seed); C = Vector(centre); CAM = Vector(cam_pos); end_t = end_t or T0 + 4.5
    chosen = set(pass_names or [o.name for o in random.sample(objects, min(toward_cam, len(objects)))])
    for o in objects:
        c = o.location.copy(); out = Vector((c.x - C.x, c.y - C.y, 0))
        out = out.normalized() if out.length > 0.05 else Vector((1, 0, 0))
        if o.name in chosen:
            ring = Vector((random.choice((-1, 1)) * random.uniform(0.9, 1.4), 0, random.choice((-1, 1)) * random.uniform(0.5, 0.9)))
            d = (out * 0.4 + (CAM + ring - c).normalized() * 0.9).normalized()
        else:
            d = (out * 0.9 + Vector((random.gauss(0, 0.35), random.gauss(0, 0.35), random.uniform(0.0, 0.6)))).normalized()
        spd = random.uniform(*speed); spin = Vector((random.uniform(-2.5, 2.5), random.uniform(-2.5, 2.5), random.uniform(-1.5, 1.5)))
        o.hide_render = True; o.keyframe_insert("hide_render", frame=F(T0) - 1)
        o.hide_render = False; o.keyframe_insert("hide_render", frame=F(T0))
        for t, k in ((0.0, 0.0), (T0, 0.0), (T0 + 0.06, 0.3), (T0 + 0.5, 0.75), (T0 + 1.5, 1.2), (end_t, 2.4)):
            o.location = c + d * spd * k; o.rotation_euler = (spin.x * k, spin.y * k, spin.z * k)
            o.keyframe_insert("location", frame=F(t)); o.keyframe_insert("rotation_euler", frame=F(t))

def debris(src_objects, T0, cam_pos, n=260, centre_radius=0.92, near=120, seed=11, end_t=None):
    """Hundreds of small instanced fragments (shared mesh data, cheap): `near` stream past the lens, rest drift 360.
    Sizes 0.1-0.24 near / 0.07-0.2 far: the reference reads as MANY small pieces + only a few big ones."""
    sc = bpy.context.scene; random.seed(seed); CAM = Vector(cam_pos); end_t = end_t or T0 + 4.5; out_objs = []
    for i in range(n):
        b = random.choice(src_objects); ob = bpy.data.objects.new("Frag%d" % i, b.data); sc.collection.objects.link(ob)
        m = ob.modifiers.new("sub", "SUBSURF"); m.subdivision_type = "SIMPLE"; m.levels = m.render_levels = 3
        s = random.uniform(0.1, 0.24) if i < near else random.uniform(0.07, 0.2); ob.scale = (s, s, s * 0.9)
        r = centre_radius * math.sqrt(random.random()); a = random.uniform(0, 6.283)
        start = Vector((r * math.cos(a), r * math.sin(a), random.uniform(-0.03, 0.05)))
        out = Vector((start.x, start.y, 0)).normalized() if r > 0.05 else Vector((1, 0, 0))
        if i < near:
            ring = Vector((random.choice((-1, 1)) * random.uniform(0.9, 2.2), 0, random.choice((-1, 1)) * random.uniform(0.6, 1.3)))
            d = (out * 0.5 + (CAM + ring - start).normalized() * 0.8 + Vector((random.gauss(0, 0.35), random.gauss(0, 0.2), random.gauss(0, 0.35)))).normalized(); spd = random.uniform(1.6, 3.2)
        else:
            d = (out * 0.7 + Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized()).normalized(); spd = random.uniform(1.0, 3.5)
        spin = Vector((random.uniform(-7, 7), random.uniform(-7, 7), random.uniform(-4, 4))); rz = random.uniform(0, 6.3)
        ob.hide_render = True; ob.keyframe_insert("hide_render", frame=F(T0) - 1)
        ob.hide_render = False; ob.keyframe_insert("hide_render", frame=F(T0))
        for t, k in ((T0, 0.0), (T0 + 0.06, 0.3), (T0 + 0.5, 0.75), (T0 + 1.5, 1.2), (end_t, 2.4)):
            ob.location = start + d * spd * k; ob.rotation_euler = (spin.x * k, spin.y * k, rz + spin.z * k)
            ob.keyframe_insert("location", frame=F(t)); ob.keyframe_insert("rotation_euler", frame=F(t))
        out_objs.append(ob)
    return out_objs

def sparks(T0, centre=(0, 0, 0), n=150, seed=5, end_t=None):
    """Radial spark spikes: thin stretched spheres, blackbody 1700-3400K, zero gravity."""
    sc = bpy.context.scene; random.seed(seed); end_t = end_t or T0 + 4.5
    m = bpy.data.materials.new("Spark"); m.use_nodes = True; n_ = m.node_tree; n_.nodes.remove(n_.nodes["Principled BSDF"])
    e = node(n_, "ShaderNodeEmission"); oi = node(n_, "ShaderNodeObjectInfo"); bb = node(n_, "ShaderNodeBlackbody")
    L(n_, M(n_, "ADD", 1700, M(n_, "MULTIPLY", oi.outputs["Random"], 1700)), bb.inputs["Temperature"]); L(n_, bb.outputs[0], e.inputs["Color"])
    glow = VAL(n_, "glow", 0.0); L(n_, M(n_, "MULTIPLY", glow, M(n_, "ADD", 0.4, oi.outputs["Random"])), e.inputs["Strength"])
    L(n_, e.outputs[0], n_.nodes["Material Output"].inputs["Surface"])
    KEY(n_, "glow", [(0.0, 26), (T0, 26), (T0 + 1.2, 10), (T0 + 3.0, 2), (end_t, 0)])
    C = Vector(centre)
    for i in range(n):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=6, ring_count=3, radius=0.0032); s = bpy.context.active_object
        s.data.materials.append(m); s.visible_shadow = False
        d = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1))).normalized(); spd = random.uniform(5.0, 11.0)
        s.rotation_mode = "QUATERNION"; s.rotation_quaternion = d.to_track_quat("Z", "Y"); s.scale = (1.4, 1.4, random.uniform(10, 35))
        s.hide_render = True; s.keyframe_insert("hide_render", frame=F(T0) - 1); s.hide_render = False; s.keyframe_insert("hide_render", frame=F(T0))
        for t, k in ((T0, 0.0), (T0 + 0.25, 0.4), (T0 + 1.5, 0.9), (end_t, 1.8)):
            s.location = C + d * spd * k; s.keyframe_insert("location", frame=F(t))

def fire_smoke(T0, end_t, centre=(0, 0, 0), cache_dir=None, res=128, density=0.85, dissolve=22):
    """Mantaflow fireball + smoke (golden ramp). Bake with bake_fire() (select + active domain, free first)."""
    sc = bpy.context.scene
    bpy.ops.mesh.primitive_cube_add(size=7, location=(centre[0], centre[1], 1.2)); dom = bpy.context.active_object; dom.name = "FireDomain"
    fm = dom.modifiers.new("Fluid", "FLUID"); fm.fluid_type = "DOMAIN"; ds = fm.domain_settings
    ds.domain_type = "GAS"; ds.resolution_max = res; ds.use_noise = True; ds.noise_scale = 2; ds.noise_strength = 1.4; ds.use_adaptive_domain = True; ds.time_scale = 0.35
    ds.cache_directory = cache_dir or os.path.join(os.path.dirname(bpy.data.filepath) or os.getcwd(), "firecache"); ds.cache_type = "ALL"
    ds.cache_frame_start = Fi(T0); ds.cache_frame_end = Fi(end_t); ds.use_dissolve_smoke = True; ds.dissolve_speed = dissolve
    ds.vorticity = 0.55; ds.flame_vorticity = 1.0; ds.burning_rate = 0.65; ds.flame_smoke = 1.2
    fm_ = bpy.data.materials.new("Fire"); fm_.use_nodes = True; fn = fm_.node_tree; fn.nodes.remove(fn.nodes["Principled BSDF"])
    pv = node(fn, "ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (0.16, 0.13, 0.1, 1); pv.inputs["Density"].default_value = density
    fa = node(fn, "ShaderNodeAttribute"); fa.attribute_name = "flame"; fr = node(fn, "ShaderNodeValToRGB"); L(fn, fa.outputs["Fac"], fr.inputs[0])
    el = fr.color_ramp.elements; el[0].color = (0.35, 0.05, 0.0, 1); el[1].color = (1.0, 0.92, 0.7, 1)
    for pos, col in ((0.3, (0.9, 0.16, 0.01, 1)), (0.55, (1.0, 0.42, 0.05, 1)), (0.8, (1.0, 0.7, 0.25, 1))): el.new(pos).color = col
    L(fn, fr.outputs["Color"], pv.inputs["Emission Color"]); L(fn, M(fn, "MULTIPLY", M(fn, "POWER", fa.outputs["Fac"], 1.5), 11.0), pv.inputs["Emission Strength"])
    L(fn, pv.outputs[0], fn.nodes["Material Output"].inputs["Volume"]); dom.data.materials.append(fm_)
    dom.hide_render = True; dom.keyframe_insert("hide_render", frame=1); dom.keyframe_insert("hide_render", frame=F(T0) - 1)
    dom.hide_render = False; dom.keyframe_insert("hide_render", frame=F(T0))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=centre); fl = bpy.context.active_object; fl.name = "FireFlow"
    ff = fl.modifiers.new("Fluid", "FLUID"); ff.fluid_type = "FLOW"; fs = ff.flow_settings
    fs.flow_type = "BOTH"; fs.flow_behavior = "INFLOW"; fs.fuel_amount = 1.6; fs.temperature = 3.2; fs.smoke_color = (0.22, 0.18, 0.14)
    fs.use_initial_velocity = True; fs.velocity_normal = 4.0; fl.hide_render = True
    for t, s in ((0.0, 0.001), (T0 - 0.05, 0.001), (T0, 1.0), (T0 + 0.25, 1.0), (T0 + 0.35, 0.001)):
        fl.scale = (s, s, s); fl.keyframe_insert("scale", frame=F(t))
    return dom

def bake_fire(dom=None):
    """The ONLY reliable headless bake: frame 1, deselect all, select+activate domain, free_all, bake_all.
    A bake that 'completes' in <1 s baked nothing: check the cache data folder has one file per frame."""
    sc = bpy.context.scene; dom = dom or bpy.data.objects["FireDomain"]; sc.frame_set(1)
    for o in sc.objects: o.select_set(False)
    dom.select_set(True); bpy.context.view_layer.objects.active = dom
    with bpy.context.temp_override(active_object=dom, object=dom):
        bpy.ops.fluid.free_all(); bpy.ops.fluid.bake_all()

def point_light_keys(name, loc, color, pairs, size=0.3, volume=1.0):
    """Flash / blast light with EXPLICIT 0 keys at t=0 (otherwise energy leaks into earlier shots)."""
    sc = bpy.context.scene; ld = bpy.data.lights.new(name, "POINT"); ld.color = color; ld.shadow_soft_size = size; ld.volume_factor = volume
    ob = bpy.data.objects.new(name, ld); sc.collection.objects.link(ob); ob.location = loc
    for t, e in pairs: ld.energy = e; ld.keyframe_insert("energy", frame=F(t))
    return ob

# ------------------------------------------------------------------ cameras
def aim(cam, loc, tgt, roll=0):
    cam.location = loc; q = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y"); cam.rotation_mode = "XYZ"
    cam.rotation_euler = q.to_euler(); cam.rotation_euler.rotate_axis("Z", math.radians(roll))

def shot_cameras(shots):
    """shots = [(name, t0, t1, lens_mm, fstop, [(t, loc, target), ...]), ...]  -> one camera per shot,
    DOF on an animated focus empty, timeline markers bind cameras. Render each shot separately (render_jobs)."""
    sc = bpy.context.scene; cams = {}
    for name, t0, t1, lens, fstop, path in shots:
        cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = 0.01
        cam = bpy.data.objects.new(name, cd); sc.collection.objects.link(cam)
        foc = bpy.data.objects.new(name + "_focus", None); sc.collection.objects.link(foc)
        for t, loc, tg in path:            # camera TRACKS the animated focus empty: keyed rotations drift off-target between keys
            cam.location = loc; cam.keyframe_insert("location", frame=F(t))
            foc.location = tg; foc.keyframe_insert("location", frame=F(t))
        tc = cam.constraints.new("TRACK_TO"); tc.target = foc; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"
        cd.dof.use_dof = True; cd.dof.focus_object = foc; cd.dof.aperture_fstop = fstop
        sc.timeline_markers.new(name, frame=Fi(t0)).camera = cam; cams[name] = cam
    return cams

# ------------------------------------------------------------------ rendering
def render_jobs(out_dir, jobs, test_times=None, test_scale=50, test_samples=16):
    """jobs = [(folder, camera_name, t0, t1, fps), ...]. Resumable (skips existing PNGs).
    Slow-mo: render that window at 48 fps and Time-Remap in AE. test_times -> quick low-res stills in out_dir/_test."""
    sc = bpy.context.scene
    for mk in sc.timeline_markers: mk.camera = None
    if test_times:
        sc.render.resolution_percentage = test_scale; sc.cycles.samples = test_samples
        d = os.path.join(out_dir, "_test"); os.makedirs(d, exist_ok=True)
        for i, (cam, t) in enumerate(test_times):
            sc.camera = bpy.data.objects[cam]; f = F(t); sc.frame_set(int(f), subframe=f - int(f))
            sc.render.filepath = os.path.join(d, "test_%02d_%s_%.2f.png" % (i, cam, t)); bpy.ops.render.render(write_still=True)
            print("TEST", i + 1, "/", len(test_times), flush=True)
        return
    for folder, cam, t0, t1, rate in jobs:
        sc.camera = bpy.data.objects[cam]; d = os.path.join(out_dir, folder); os.makedirs(d, exist_ok=True)
        n = int(round((t1 - t0) * rate))
        for k in range(n):
            p = os.path.join(d, "%s_%04d.png" % (folder, k))
            if os.path.exists(p): continue
            f = F(t0 + k / rate); sc.frame_set(int(f), subframe=f - int(f)); sc.render.filepath = p
            bpy.ops.render.render(write_still=True); print("FRAME", folder, k + 1, "/", n, flush=True)
    print("ALLDONE", flush=True)
