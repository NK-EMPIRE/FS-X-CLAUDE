// ae_build.jsx: config-driven After Effects finish for a CGI intro. Fully editable, named layers, no plugins.
// Run:  AfterFX.exe -r D:/aetmp/<proj>/ae_build.jsx      (script path WITHOUT spaces; config next to it: ae_config.json)
// Builds 01_EDIT (brand intro > lens push > flash > shots > blast slow-mo > title)  ->  02_GRADED (named grade layers)
//        -> 03_FINAL (3-channel chromatic aberration, grain, vignette, letterbox), saves .aep, renders master .mov,
//        writes <out_dir>/AE_DONE.txt and <out_dir>/ae_log.txt.
(function () {
var HERE = File($.fileName).parent.fsName.replace(/\\/g, "/") + "/";
var cf = new File(HERE + "ae_config.json"); cf.open("r"); var CFG = eval("(" + cf.read() + ")"); cf.close();
var OUT = CFG.out_dir.replace(/\/?$/, "/"); new Folder(OUT).create();
var LOG = new File(OUT + "ae_log.txt"); LOG.open("w");
function log(s) { LOG.writeln(s); }
try {
app.beginSuppressDialogs();
if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);           // an open project's save dialog blocks -r
var proj = app.newProject();
var W = CFG.width || 1920, H = CFG.height || 1080, FPS = CFG.fps || 24, DUR = CFG.duration;
function dims(p) { var t = p.propertyValueType; if (t == PropertyValueType.TwoD_SPATIAL || t == PropertyValueType.ThreeD_SPATIAL || t == PropertyValueType.OneD) return 1; var v = p.value; return (v instanceof Array) ? v.length : 1; }
function keys(p, list, ease) {
    for (var i = 0; i < list.length; i++) p.setValueAtTime(list[i][0], list[i][1]);
    if (!ease) return; var n = dims(p);
    for (var k = 1; k <= p.numKeys; k++) { var e = []; for (var d = 0; d < n; d++) e.push(new KeyframeEase(0, ease)); p.setTemporalEaseAtKey(k, e, e); }
}
function fx(l, m) { return l.property("ADBE Effect Parade").addProperty(m); }   // NB: moving an effect invalidates refs: re-fetch by index
function tr(l, n) { return l.property("ADBE Transform Group").property(n); }
function folder(name) { return proj.items.addFolder(name); }
var fRend = folder("01_RENDERS (Blender)"), fBrand = folder("02_BRAND INTRO"), fTitle = folder("04_TITLE"), fComps = folder("05_MAIN COMPS"), fSolids = folder("06_SOLIDS");
function solid(c, col, name, blend) { var s = c.layers.addSolid(col, name, W, H, 1, DUR); s.source.parentFolder = fSolids; if (blend) s.blendingMode = blend; return s; }

// ---------- footage
var S = {};
for (var i = 0; i < CFG.shots.length; i++) {
    var sh = CFG.shots[i];
    var io = new ImportOptions(new File(sh.dir.replace(/\/?$/, "/") + sh.name + "_0000.png")); io.sequence = true;
    var it = proj.importFile(io); it.mainSource.conformFrameRate = sh.fps || 24; it.name = sh.name; it.parentFolder = fRend; S[sh.name] = it;
    log("seq " + sh.name + " " + it.duration);
}

// ---------- 01_EDIT
var edit = proj.items.addComp("01_EDIT", W, H, 1, DUR, FPS); edit.parentFolder = fComps; edit.motionBlur = true; edit.bgColor = [0, 0, 0];
function flash(t, col, peak, len, name) {
    var f = solid(edit, col, name || "FLASH", BlendingMode.ADD); f.inPoint = t - 0.2; f.outPoint = t + len + 0.05;
    keys(tr(f, "ADBE Opacity"), [[t - 0.18, 0], [t, peak], [t + len, 0]], 60); return f;
}
function lensFlare(t, x, y, peak, name) {
    var l = solid(edit, [0, 0, 0], name || "FLASH  lens flare", BlendingMode.ADD); l.inPoint = t - 0.4; l.outPoint = t + 0.6;
    var e = fx(l, "ADBE Lens Flare"); e.property("ADBE Lens Flare-0001").setValue([x, y]);
    keys(e.property("ADBE Lens Flare-0002"), [[t - 0.38, 0], [t, peak], [t + 0.5, 0]], 60); return l;
}
var B = 0;
if (CFG.brand && CFG.brand.file) {                       // brand intro, camera pushes INTO a point (e.g. a lens dot) and match-cuts on a flash
    var bi = proj.importFile(new ImportOptions(new File(CFG.brand.file))); bi.parentFolder = fBrand; B = CFG.brand.end;
    var LB = edit.layers.add(bi); LB.name = "BRAND INTRO  (push into " + (CFG.brand.label || "target") + ")"; LB.outPoint = B;
    var px = CFG.brand.target[0], py = CFG.brand.target[1];
    tr(LB, "ADBE Anchor Point").setValue([px, py]);
    var pos = tr(LB, "ADBE Position"); pos.setValueAtTime(B - 0.8, [px, py]); pos.setValueAtTime(B, [W / 2, H / 2]);
    var sc = tr(LB, "ADBE Scale"); sc.setValueAtTime(0, [100, 100]); sc.setValueAtTime(B - 0.8, [100, 100]); sc.setValueAtTime(B, [2800, 2800]);
    var ein = [new KeyframeEase(0, 90), new KeyframeEase(0, 90), new KeyframeEase(0, 90)];
    sc.setTemporalEaseAtKey(2, ein, ein); sc.setTemporalEaseAtKey(3, [new KeyframeEase(0, 10), new KeyframeEase(0, 10), new KeyframeEase(0, 10)], ein);
    keys(fx(LB, "ADBE Gaussian Blur 2").property("ADBE Gaussian Blur 2-0001"), [[B - 0.5, 0], [B, 30]], 70); LB.motionBlur = true;
    flash(B - 0.02, [1, 0.96, 0.9], 85, 0.27, "FLASH  brand > CGI match cut"); lensFlare(B, W / 2, H / 2, 170, "FLASH  brand lens flare");
}
// shots: {name, at (edit time, after brand), out, src_offset, remap [[edit_t, src_t]...], scale_keys, shake: {t0,t1,amp}, label}
var layers = {};
for (var j = 0; j < CFG.shots.length; j++) {
    var s = CFG.shots[j]; if (s.at === undefined) continue;
    var l = edit.layers.add(S[s.name]); l.name = "SHOT " + (s.label || s.name);
    var a = B + s.at, b = B + s.out;
    l.startTime = a - (s.src_offset || 0);
    if (s.remap) {                                                // slow motion: 48 fps source + Time Remap (do NOT remove the default keys)
        l.startTime = a; l.timeRemapEnabled = true; var rk = [];
        for (var r = 0; r < s.remap.length; r++) rk.push([B + s.remap[r][0], s.remap[r][1]]);
        keys(l.property("ADBE Time Remapping"), rk, 0);
    }
    l.inPoint = a; l.outPoint = (s.hold_to_end ? DUR : b);
    if (s.scale_keys) { var sk = []; for (var q = 0; q < s.scale_keys.length; q++) sk.push([B + s.scale_keys[q][0], [s.scale_keys[q][1], s.scale_keys[q][1]]]); keys(tr(l, "ADBE Scale"), sk, 0); }
    if (s.shake) tr(l, "ADBE Position").expression = "wiggle(" + (s.shake.freq || 16) + ", linear(time," + (B + s.shake.t0) + "," + (B + s.shake.t1) + "," + s.shake.amp + ",0))";
    if (s.pops) { var pp = []; for (var z = 0; z < s.pops.length; z++) pp.push(B + s.pops[z]); }   // bijili crackle camera kicks
    if (s.pops) tr(l, "ADBE Position").expression = "var t=[" + pp.join(",") + "];var a=0;for(var i=0;i<t.length;i++){var d=time-t[i];if(d>0&&d<0.2)a=Math.max(a,(1-d/0.2)*10);}wiggle(30,a)";
    layers[s.name] = l;
}
for (var f2 = 0; f2 < (CFG.flashes || []).length; f2++) { var fl = CFG.flashes[f2]; flash(B + fl.t, fl.color || [1, 0.95, 0.85], fl.peak || 60, fl.len || 0.3, fl.name); if (fl.flare) lensFlare(B + fl.t, fl.flare[0], fl.flare[1], fl.flare_peak || 160); }
if (CFG.smoke_overlay) {                                          // living smoke so held frames never freeze
    var so = CFG.smoke_overlay, sm2 = solid(edit, [0, 0, 0], "SMOKE drift (warm overlay)", BlendingMode.SCREEN); sm2.inPoint = B + so.t0; sm2.outPoint = DUR;
    var fn2 = fx(sm2, "ADBE Fractal Noise"); fn2.property("ADBE Fractal Noise-0004").setValue(130); fn2.property("ADBE Fractal Noise-0005").setValue(-45);
    fn2.property("ADBE Fractal Noise-0010").setValue(650); fn2.property("ADBE Fractal Noise-0023").expression = "time*55";
    var tn2 = fx(sm2, "ADBE Tint"); tn2.property("ADBE Tint-0001").setValue([0.12, 0.06, 0.02]); tn2.property("ADBE Tint-0002").setValue(so.color || [1.0, 0.72, 0.42]);
    keys(tr(sm2, "ADBE Opacity"), [[B + so.t0, 0], [B + so.t0 + 1.4, so.opacity || 20]], 40);
}

// ---------- TITLE: live text layers (editable) + PNG lettering fallback (AE only renders fonts installed FOR ALL USERS)
var T = CFG.title, LT = null;
if (T) {
    var TT0 = B + T.start, tc = proj.items.addComp("04_TITLE  (edit text here)", W, H, 1, DUR - TT0, FPS); tc.parentFolder = fTitle;
    var main = null, lines = [];
    for (var k = 0; k < T.lines.length; k++) {
        var ln = T.lines[k], lay;
        if (ln.png && !T.use_live_text) {
            var pi = proj.importFile(new ImportOptions(new File(ln.png))); pi.parentFolder = fTitle; lay = tc.layers.add(pi);
        } else {
            lay = tc.layers.addText(ln.text); var tp = lay.property("ADBE Text Properties").property("ADBE Text Document"); var d = tp.value;
            d.resetCharStyle(); d.resetParagraphStyle(); d.font = ln.font; d.fontSize = ln.size; d.tracking = ln.tracking || 0;
            d.applyFill = true; d.fillColor = [1, 1, 1]; d.applyStroke = false; d.justification = ParagraphJustification.CENTER_JUSTIFY; tp.setValue(d);
            var rr = lay.sourceRectAtTime(0, false); tr(lay, "ADBE Anchor Point").setValue([rr.left + rr.width / 2, rr.top + rr.height / 2]);
        }
        tr(lay, "ADBE Position").setValue([W / 2, ln.y]); lay.name = "TITLE  " + ln.text; lines.push(lay); if (ln.main) main = lay;
        keys(tr(lay, "ADBE Opacity"), [[ln.in || 0, 0], [(ln.in || 0) + 0.45, 100]], 50);
    }
    if (main) {                                                    // brass gradient fill matted to the main word, blur-to-focus reveal
        var g = solid(tc, [1, 1, 1], "GOLD GRADIENT (fill of main word)"); var rp = fx(g, "ADBE Ramp"); var top = T.gold_top || [1, 0.95, 0.84], bot = T.gold_bottom || [0.5, 0.36, 0.2];
        rp.property("ADBE Ramp-0001").setValue([W / 2, T.lines[0].y - 140]); rp.property("ADBE Ramp-0002").setValue(top);
        rp.property("ADBE Ramp-0003").setValue([W / 2, T.lines[0].y + 140]); rp.property("ADBE Ramp-0004").setValue(bot);
        g.moveBefore(main); g.setTrackMatte(main, TrackMatteType.ALPHA);
        keys(fx(main, "ADBE Gaussian Blur 2").property("ADBE Gaussian Blur 2-0001"), [[0, 60], [0.9, 0]], 75);
        keys(tr(main, "ADBE Scale"), [[0, [108, 108]], [1.3, [100, 100]], [tc.duration, [97, 97]]], 70);
    }
    LT = edit.layers.add(tc); LT.name = "TITLE  (precomp)"; LT.startTime = TT0; LT.inPoint = TT0; LT.outPoint = DUR; LT.moveToBeginning();
    var bv = fx(LT, "ADBE Bevel Alpha"); bv.property("ADBE Bevel Alpha-0001").setValue(5); bv.property("ADBE Bevel Alpha-0002").setValue(-50); bv.property("ADBE Bevel Alpha-0004").setValue(0.7);
    var ds = fx(LT, "ADBE Drop Shadow"); ds.property("ADBE Drop Shadow-0002").setValue(170); ds.property("ADBE Drop Shadow-0004").setValue(10); ds.property("ADBE Drop Shadow-0005").setValue(25);
    var tg = fx(LT, "ADBE Glo2"); tg.property("ADBE Glo2-0002").setValue(200); tg.property("ADBE Glo2-0003").setValue(18); tg.property("ADBE Glo2-0004").setValue(0.35);
    var sw = fx(LT, "CC Light Sweep");        // precomp holds ONLY lettering -> the shine stays inside the letters
    keys(sw.property("CC Light Sweep-0001"), [[TT0 + 1.6, [300, T.lines[0].y]], [TT0 + 2.6, [1650, T.lines[0].y]]], 50);
    sw.property("CC Light Sweep-0002").setValue(-22); sw.property("CC Light Sweep-0004").setValue(110); sw.property("CC Light Sweep-0005").setValue(55);
    if (T.darken_behind) { var dk = solid(edit, T.darken_behind, "TITLE  darken backdrop", BlendingMode.MULTIPLY); dk.inPoint = TT0 - 1; dk.outPoint = DUR; keys(tr(dk, "ADBE Opacity"), [[TT0 - 1, 0], [TT0 + 1.2, 85]], 50); dk.moveAfter(LT); }
}
if (CFG.fade_out) { var eb = solid(edit, [0, 0, 0], "FADE OUT end"); eb.inPoint = DUR - CFG.fade_out; keys(tr(eb, "ADBE Opacity"), [[DUR - CFG.fade_out, 0], [DUR, 100]], 40); eb.moveToBeginning(); }
log("edit done");

// ---------- 02_GRADED (preset: brass mids / teal shadows, desat, levels, halation)
var gr = proj.items.addComp("02_GRADED", W, H, 1, DUR, FPS); gr.parentFolder = fComps; gr.layers.add(edit);
var G = CFG.grade || {};
function adj(c, name) { var a = c.layers.addSolid([1, 1, 1], name, W, H, 1, DUR); a.adjustmentLayer = true; a.source.parentFolder = fSolids; return a; }
var tri = fx(adj(gr, "GRADE 1  Tritone (highlights / mids / shadows)"), "ADBE Tritone");
tri.property("ADBE Tritone-0001").setValue(G.high || [1, 0.94, 0.84, 1]); tri.property("ADBE Tritone-0002").setValue(G.mid || [0.6, 0.5, 0.36, 1]);
tri.property("ADBE Tritone-0003").setValue(G.shadow || [0.02, 0.055, 0.07, 1]); tri.property("ADBE Tritone-0004").setValue(G.tritone_mix || 72);
fx(adj(gr, "GRADE 2  Desaturate (Hue/Sat)"), "ADBE HUE SATURATION").property("ADBE HUE SATURATION-0005").setValue(G.saturation || -14);
var lv = fx(adj(gr, "GRADE 3  Contrast (Levels)"), "ADBE Easy Levels2"); lv.property("ADBE Easy Levels2-0003").setValue(0.025); lv.property("ADBE Easy Levels2-0005").setValue(0.96);
var hg = fx(adj(gr, "HALATION  glow on highlights"), "ADBE Glo2");
hg.property("ADBE Glo2-0002").setValue(185); hg.property("ADBE Glo2-0003").setValue(45); hg.property("ADBE Glo2-0004").setValue(G.halation || 0.55);
hg.property("ADBE Glo2-0007").setValue(2); hg.property("ADBE Glo2-0012").setValue([1, 0.5, 0.3, 1]); hg.property("ADBE Glo2-0013").setValue([0.8, 0.15, 0.05, 1]);
log("grade done");

// ---------- 03_FINAL
var fin = proj.items.addComp("03_FINAL  (render this)", W, H, 1, DUR, FPS); fin.parentFolder = fComps; fin.bgColor = [0, 0, 0];
var chan = [["CA  red channel", 2, 100 + (CFG.ca || 0.35)], ["CA  green channel", 3, 100.0], ["CA  blue channel", 4, 100 - (CFG.ca || 0.35)]];
var caOff = CFG.ca_off;   // [t0, t1]: nearly no colour split while bright white shards are on screen (else red/cyan fringes)
for (var c = 0; c < 3; c++) {
    var Lc = fin.layers.add(gr); Lc.name = chan[c][0]; var shc = fx(Lc, "ADBE Shift Channels");
    for (var q2 = 2; q2 <= 4; q2++) if (q2 != chan[c][1]) shc.property("ADBE Shift Channels-000" + q2).setValue(10);
    tr(Lc, "ADBE Scale").setValue([chan[c][2], chan[c][2]]);
    if (caOff) tr(Lc, "ADBE Scale").expression = "var k=Math.max(ease(time," + (B + caOff[0] - 0.3) + "," + (B + caOff[0]) + ",1,0.15),ease(time," + (B + caOff[1]) + "," + (B + caOff[1] + 0.8) + ",0.15,1));var s=100+(value[0]-100)*k;[s,s]";
    if (c > 0) Lc.blendingMode = BlendingMode.ADD;
}
var nz = fx(adj(fin, "GRAIN  (Noise, mono)"), "ADBE Noise"); nz.property("ADBE Noise-0001").setValue(CFG.grain || 5); nz.property("ADBE Noise-0002").setValue(0);
var vg = solid(fin, [0, 0, 0], "VIGNETTE"); var vm = vg.property("ADBE Mask Parade").addProperty("ADBE Mask Atom"); vm.inverted = true; var vs = new Shape(), kx = 0.5523;
vs.vertices = [[W / 2, 70], [W - 60, H / 2], [W / 2, H - 70], [60, H / 2]];
vs.inTangents = [[-(W / 2 - 60) * kx, 0], [0, -(H / 2 - 70) * kx], [(W / 2 - 60) * kx, 0], [0, (H / 2 - 70) * kx]];
vs.outTangents = [[(W / 2 - 60) * kx, 0], [0, (H / 2 - 70) * kx], [-(W / 2 - 60) * kx, 0], [0, -(H / 2 - 70) * kx]]; vs.closed = true;
vm.property("ADBE Mask Shape").setValue(vs); vm.property("ADBE Mask Feather").setValue([420, 420]); tr(vg, "ADBE Opacity").setValue(55);
var lbh = CFG.letterbox === undefined ? 138 : CFG.letterbox;
if (lbh > 0) {
    var lt = fin.layers.addSolid([0, 0, 0], "LETTERBOX top", W, lbh, 1, DUR); tr(lt, "ADBE Position").setValue([W / 2, lbh / 2]); lt.source.parentFolder = fSolids;
    var lb = fin.layers.addSolid([0, 0, 0], "LETTERBOX bottom", W, lbh, 1, DUR); tr(lb, "ADBE Position").setValue([W / 2, H - lbh / 2]); lb.source.parentFolder = fSolids;
}
proj.save(new File(OUT + CFG.aep_name + ".aep")); log("saved project");
if (CFG.render !== false) {
    var rq = proj.renderQueue.items.add(fin); var om = rq.outputModule(1);
    try { om.applyTemplate("High Quality"); } catch (e1) { log("template " + e1); }
    om.file = new File(OUT + CFG.aep_name + "_master"); proj.save(); log("render start"); proj.renderQueue.render(); log("render done");
}
app.endSuppressDialogs(false);
} catch (err) { log("ERR line " + err.line + ": " + err.toString()); try { app.endSuppressDialogs(false); } catch (e2) {} }
LOG.close();
var dn = new File(OUT + "AE_DONE.txt"); dn.open("w"); dn.write("done"); dn.close();
})();
