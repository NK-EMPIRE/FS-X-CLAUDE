// The Most Expensive Festival in India — v4 edit. Fully editable AE project.
// Structure: 01_EDIT (brand intro > lens push > flash > 6 coin shots + slow-mo blast + title)
//            02_GRADED (EDIT + named grade adjustment layers)
//            03_FINAL (radial chromatic aberration from 3 channel copies + grain + vignette + letterbox)
(function () {
var BASE = "D:/FS DOCUMENTARY INTRO/downloads/3d_motion_intros/";
var FR = BASE + "work/coin3/final/"; var FR5 = BASE + "work/coin3/final5/";
var PROJ = BASE + "renders/AE_PROJECT/";
var LOG = new File("D:/aetmp/fsintro/out/v6_log.txt"); LOG.open("w");
function log(s) { LOG.writeln(s); }
try {
app.beginSuppressDialogs();
if (app.project) app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
new Folder(PROJ).create();
var proj = app.newProject();
var W = 1920, H = 1080, FPS = 24, B = 4.8;
var DUR = 38.7;
function dims(p) { var t = p.propertyValueType; if (t == PropertyValueType.TwoD_SPATIAL || t == PropertyValueType.ThreeD_SPATIAL || t == PropertyValueType.OneD) return 1; var v = p.value; return (v instanceof Array) ? v.length : 1; }
function keys(p, list, ease) {
    for (var i = 0; i < list.length; i++) p.setValueAtTime(list[i][0], list[i][1]);
    if (!ease) return; var n = dims(p);
    for (var k = 1; k <= p.numKeys; k++) { var e = []; for (var d = 0; d < n; d++) e.push(new KeyframeEase(0, ease)); p.setTemporalEaseAtKey(k, e, e); }
}
function fx(l, m) { return l.property("ADBE Effect Parade").addProperty(m); }
function tr(l, n) { return l.property("ADBE Transform Group").property(n); }
function folder(name) { return proj.items.addFolder(name); }
var fRend = folder("01_RENDERS (Blender)"), fBrand = folder("02_BRAND INTRO"), fShots = folder("03_SHOTS"), fTitle = folder("04_TITLE"), fComps = folder("05_MAIN COMPS"), fSolids = folder("06_SOLIDS");

// ---------- footage
function seq(name, rate, dir) {
    var io = new ImportOptions(new File((dir || FR) + name + "/" + name + "_0000.png")); io.sequence = true;
    var it = proj.importFile(io); it.mainSource.conformFrameRate = rate; it.name = name; it.parentFolder = fRend; return it;
}
var S = {};
var NAMES = [["S1_push", 24, FR], ["S2_macro", 24, FR], ["S3_diyahero", 24, FR5], ["S4_flip", 24, FR5], ["S5_rupeemacro", 24, FR5], ["S6_rupeehero", 24, FR5], ["S7_fuse", 24, FR5], ["S8_blast48", 48, FR5], ["S8_after", 24, FR5], ["S8_burst48", 48, BASE + "work/coin3/tail/"], ["S8_tail2", 24, BASE + "work/coin3/tail/"]];
for (var i = 0; i < NAMES.length; i++) { S[NAMES[i][0]] = seq(NAMES[i][0], NAMES[i][1], NAMES[i][2]); log("seq " + NAMES[i][0] + " " + S[NAMES[i][0]].duration); }
var brand = proj.importFile(new ImportOptions(new File(BASE + "FS-INTRO/cp its your time.mp4"))); brand.parentFolder = fBrand;

// ---------- 01_EDIT
var edit = proj.items.addComp("01_EDIT", W, H, 1, DUR, FPS); edit.parentFolder = fComps; edit.motionBlur = true; edit.bgColor = [0, 0, 0];
function place(item, inP, outP, srcOffset) { var l = edit.layers.add(item); l.startTime = inP - (srcOffset || 0); l.inPoint = inP; l.outPoint = outP; return l; }
function flash(t, col, peak, len, name) {
    var f = edit.layers.addSolid(col, name || "FLASH", W, H, 1, DUR); f.source.parentFolder = fSolids;
    f.blendingMode = BlendingMode.ADD; f.inPoint = t - 0.2; f.outPoint = t + len + 0.05;
    keys(tr(f, "ADBE Opacity"), [[t - 0.18, 0], [t, peak], [t + len, 0]], 60); return f;
}
// brand intro + push into the selfie-camera lens (lens dot at 921,320)
var LB = place(brand, 0, B); LB.name = "BRAND INTRO  (push into the selfie-camera lens)";
tr(LB, "ADBE Anchor Point").setValue([921, 320]);
var pos = tr(LB, "ADBE Position"); pos.setValueAtTime(4.0, [921, 320]); pos.setValueAtTime(B, [960, 540]);
var sc = tr(LB, "ADBE Scale"); sc.setValueAtTime(0, [100, 100]); sc.setValueAtTime(4.0, [100, 100]); sc.setValueAtTime(B, [2800, 2800]);
var ein = [new KeyframeEase(0, 90), new KeyframeEase(0, 90), new KeyframeEase(0, 90)];
sc.setTemporalEaseAtKey(2, ein, ein); sc.setTemporalEaseAtKey(3, [new KeyframeEase(0, 10), new KeyframeEase(0, 10), new KeyframeEase(0, 10)], ein);
var lbB = fx(LB, "ADBE Gaussian Blur 2"); keys(lbB.property("ADBE Gaussian Blur 2-0001"), [[4.3, 0], [B, 30]], 70);
LB.motionBlur = true;
var fl0 = edit.layers.addSolid([1, 0.96, 0.9], "FLASH  selfie camera pop > coin", W, H, 1, DUR); fl0.source.parentFolder = fSolids;
fl0.inPoint = 4.65; fl0.outPoint = B + 0.3; fl0.blendingMode = BlendingMode.ADD; keys(tr(fl0, "ADBE Opacity"), [[4.68, 0], [B - 0.02, 85], [B + 0.25, 0]], 60);
var lf0 = edit.layers.addSolid([0, 0, 0], "FLASH  lens flare", W, H, 1, DUR); lf0.source.parentFolder = fSolids; lf0.blendingMode = BlendingMode.ADD;
lf0.inPoint = 4.6; lf0.outPoint = B + 0.5; var lfx = fx(lf0, "ADBE Lens Flare"); lfx.property("ADBE Lens Flare-0001").setValue([960, 540]);
keys(lfx.property("ADBE Lens Flare-0002"), [[4.62, 0], [B, 170], [B + 0.45, 0]], 60);

// coin shots
var T = [["S1_push", 0.0, 5.5], ["S2_macro", 5.5, 10.0], ["S3_diyahero", 10.0, 13.0], ["S4_flip", 13.0, 15.5], ["S5_rupeemacro", 15.5, 18.5], ["S6_rupeehero", 18.5, 21.0], ["S7_fuse", 21.0, 23.5]];
for (var j = 0; j < T.length; j++) {
    var l = place(S[T[j][0]], B + T[j][1], B + T[j][2]); l.name = "SHOT " + T[j][0];
}
// blast: slow white build (0.5x), then real-time 360 burst; then debris leaves frame and it fades to black
var b0 = B + 23.5;                                  // 28.3
var LBl = edit.layers.add(S["S8_blast48"]); LBl.name = "SHOT S8_blast (Time Remap: slow build > real-time burst)";
LBl.startTime = b0; LBl.timeRemapEnabled = true;
var trm = LBl.property("ADBE Time Remapping");
keys(trm, [[b0, 0], [b0 + 1.2, 0.6], [b0 + 2.6, 1.999]], 0);
LBl.inPoint = b0; LBl.outPoint = b0 + 1.2;   // hands over at source 24.6s to the continuous tail
tr(LBl, "ADBE Position").expression = "wiggle(20, linear(time," + (b0 + 1.2) + "," + (b0 + 2.2) + ",26,0))";
tr(LBl, "ADBE Scale").setValue([103, 103]);
flash(b0 + 1.22, [1.0, 0.95, 0.85], 60, 0.3, "FLASH  burst (white-gold)");
var lf1 = edit.layers.addSolid([0, 0, 0], "FLASH  burst lens flare", W, H, 1, DUR); lf1.source.parentFolder = fSolids; lf1.blendingMode = BlendingMode.ADD;
lf1.inPoint = b0 + 0.8; lf1.outPoint = b0 + 2.4; var lfx1 = fx(lf1, "ADBE Lens Flare"); lfx1.property("ADBE Lens Flare-0001").setValue([840, 560]);
keys(lfx1.property("ADBE Lens Flare-0002"), [[b0 + 0.8, 0], [b0 + 1.2, 160], [b0 + 2.2, 0]], 50);
// ONE continuous camera: the tail continues the same S8 camera from 24.6s, pushing through the shards into the smoke
var tl0 = b0 + 1.2;
// burst at half speed (48 fps source) so the shards hang in front of the lens, then the smoke tail in real time
var LBu = edit.layers.add(S["S8_burst48"]); LBu.name = "SHOT S8_burst (centre blast, half-speed slow motion)";
LBu.startTime = tl0; LBu.timeRemapEnabled = true; keys(LBu.property("ADBE Time Remapping"), [[tl0, 0], [tl0 + 0.6, 0.3], [tl0 + 1.15, 0.999]], 0);   // slow-mo on the burst only, then real speed
LBu.inPoint = tl0; LBu.outPoint = tl0 + 1.15;
keys(tr(LBu, "ADBE Scale"), [[tl0, [100, 100]], [tl0 + 1.15, [112, 112]]], 0);
var tl1 = tl0 + 1.15;
var LTail = edit.layers.add(S["S8_tail2"]); LTail.name = "SHOT S8_tail (same camera: debris drift, smoke fills the frame)";
LTail.startTime = tl1; LTail.timeRemapEnabled = true; LTail.inPoint = tl1; LTail.outPoint = DUR;
tr(LTail, "ADBE Scale").expression = "var s=linear(time," + (tl1 + 3.35) + "," + DUR + ",100,107);[s,s]";
tr(LBu, "ADBE Position").expression = "wiggle(14, linear(time," + tl0 + "," + (tl0 + 1.0) + ",16,0))";
// living smoke on top so the frame never freezes once the camera is inside the cloud
var sm2 = edit.layers.addSolid([0, 0, 0], "SMOKE drift (warm, over the tail)", W, H, 1, DUR); sm2.source.parentFolder = fSolids; sm2.blendingMode = BlendingMode.SCREEN;
sm2.inPoint = tl1 + 0.8; sm2.outPoint = DUR;
var fn2 = fx(sm2, "ADBE Fractal Noise"); fn2.property("ADBE Fractal Noise-0004").setValue(130); fn2.property("ADBE Fractal Noise-0005").setValue(-45);
fn2.property("ADBE Fractal Noise-0010").setValue(650); fn2.property("ADBE Fractal Noise-0023").expression = "time*55";
var tn2 = fx(sm2, "ADBE Tint"); tn2.property("ADBE Tint-0001").setValue([0.12, 0.06, 0.02]); tn2.property("ADBE Tint-0002").setValue([1.0, 0.72, 0.42]);
keys(tr(sm2, "ADBE Opacity"), [[tl1 + 0.8, 0], [tl1 + 2.2, 20]], 40);
// bijili crackles on the fuse shot
var pops = [22.6, 22.85, 23.1];
var ex = "var t=[" + (B + 22.6) + "," + (B + 22.85) + "," + (B + 23.1) + "];var a=0;for(var i=0;i<t.length;i++){var d=time-t[i];if(d>0&&d<0.2)a=Math.max(a,(1-d/0.2)*10);}wiggle(30,a)";
for (var k2 = 1; k2 <= edit.numLayers; k2++) { if (edit.layer(k2).name == "SHOT S7_fuse") tr(edit.layer(k2), "ADBE Position").expression = ex; }
for (var p2 = 0; p2 < pops.length; p2++) flash(B + pops[p2], [1, 0.72, 0.4], 35, 0.1, "FLASH  bijili crackle");

// ---------- TITLE (live text, editable)
var TT0 = 32.3;                           // title focuses in out of the smoke, held ~6s
var tc = proj.items.addComp("04_TITLE  (edit text here)", W, H, 1, DUR - TT0, FPS); tc.parentFolder = fTitle;
function text(c, txt, font, size, track) {
    var l = c.layers.addText(txt); var p = l.property("ADBE Text Properties").property("ADBE Text Document"); var d = p.value;
    d.resetCharStyle(); d.resetParagraphStyle(); d.font = font; d.fontSize = size; d.tracking = track;
    d.applyFill = true; d.fillColor = [1, 1, 1]; d.applyStroke = false; d.justification = ParagraphJustification.CENTER_JUSTIFY; p.setValue(d);
    log("font " + font + " -> " + p.value.font); return l;
}
function centre(l, y) { var r = l.sourceRectAtTime(0, false); tr(l, "ADBE Anchor Point").setValue([r.left + r.width / 2, r.top + r.height / 2]); tr(l, "ADBE Position").setValue([W / 2, y]); return r; }
var tE = text(tc, "EXPENSIVE", "Theblock-Regular", 330, 15); var rE = centre(tE, 470); tE.name = "TITLE  EXPENSIVE";
var tM = text(tc, "THE MOST", "OpenSauceSans-SemiBold", 30, 700); centre(tM, 470 - rE.height / 2 - 46); tM.name = "TITLE  THE MOST";
var tF = text(tc, "FESTIVAL IN INDIA", "OpenSauceSans-SemiBold", 30, 700); centre(tF, 470 + rE.height / 2 + 52); tF.name = "TITLE  FESTIVAL IN INDIA";
// AE cannot see the user-installed fonts at render time: rendered lettering drives the look; live text kept (disabled) for edits
function png(n) { var it = proj.importFile(new ImportOptions(new File("D:/aetmp/fsintro/" + n + ".png"))); it.parentFolder = fTitle; return tc.layers.add(it); }
tE.enabled = false; tM.enabled = false; tF.enabled = false;
tE.name = "LIVE TEXT (disabled) EXPENSIVE  - edit + re-enable if font is installed for all users"; tM.name = "LIVE TEXT (disabled) THE MOST"; tF.name = "LIVE TEXT (disabled) FESTIVAL IN INDIA";
var pE = png("T_EXPENSIVE"); pE.name = "TITLE  EXPENSIVE (TheBlock)"; var pM = png("T_THEMOST"); pM.name = "TITLE  THE MOST"; var pF = png("T_FESTIVAL"); pF.name = "TITLE  FESTIVAL IN INDIA";
tE = pE; tM = pM; tF = pF;
var rE2 = pE.sourceRectAtTime(0, false);
tr(pE, "ADBE Anchor Point").setValue([960, 470]); tr(pE, "ADBE Position").setValue([960, 470]);
var g = tc.layers.addSolid([1, 1, 1], "BRASS GRADIENT (fill of EXPENSIVE)", W, H, 1, tc.duration); g.source.parentFolder = fSolids;
var rp = fx(g, "ADBE Ramp");
rp.property("ADBE Ramp-0001").setValue([W / 2, 470 - rE.height / 2]); rp.property("ADBE Ramp-0002").setValue([1, 0.95, 0.84]);
rp.property("ADBE Ramp-0003").setValue([W / 2, 470 + rE.height / 2]); rp.property("ADBE Ramp-0004").setValue([0.5, 0.36, 0.2]);
g.moveBefore(tE); g.setTrackMatte(tE, TrackMatteType.ALPHA);
var bl = fx(tE, "ADBE Gaussian Blur 2"); keys(bl.property("ADBE Gaussian Blur 2-0001"), [[0, 60], [0.9, 0]], 75);
keys(tr(tE, "ADBE Opacity"), [[0, 0], [0.45, 100]], 50);
keys(tr(tE, "ADBE Position"), [[0, [W / 2, 540]], [1.1, [W / 2, 470]]], 85);
keys(tr(tE, "ADBE Scale"), [[0, [108, 108]], [1.3, [100, 100]], [tc.duration, [97, 97]]], 70);
keys(tr(tM, "ADBE Opacity"), [[0.7, 0], [1.2, 100]], 50); keys(tr(tF, "ADBE Opacity"), [[0.85, 0], [1.35, 100]], 50);
var LT = edit.layers.add(tc); LT.name = "TITLE  (precomp)"; LT.startTime = TT0; LT.inPoint = TT0; LT.outPoint = DUR; LT.moveToBeginning();
var bv = fx(LT, "ADBE Bevel Alpha"); bv.property("ADBE Bevel Alpha-0001").setValue(5); bv.property("ADBE Bevel Alpha-0002").setValue(-50); bv.property("ADBE Bevel Alpha-0004").setValue(0.7);
var ds = fx(LT, "ADBE Drop Shadow"); ds.property("ADBE Drop Shadow-0002").setValue(170); ds.property("ADBE Drop Shadow-0004").setValue(10); ds.property("ADBE Drop Shadow-0005").setValue(25);
var tg = fx(LT, "ADBE Glo2"); tg.property("ADBE Glo2-0002").setValue(200); tg.property("ADBE Glo2-0003").setValue(18); tg.property("ADBE Glo2-0004").setValue(0.35);
var sw = fx(LT, "CC Light Sweep");
keys(sw.property("CC Light Sweep-0001"), [[TT0 + 1.6, [300, 470]], [TT0 + 2.6, [1650, 470]]], 50);
sw.property("CC Light Sweep-0002").setValue(-22); sw.property("CC Light Sweep-0004").setValue(110); sw.property("CC Light Sweep-0005").setValue(55);
// title backdrop: near-black with very faint drifting smoke + a few embers (title card stands alone)
var bd = tc.layers.addSolid([0.02, 0.022, 0.024], "TITLE BACKDROP (off: title sits on the smoke)", W, H, 1, tc.duration); bd.source.parentFolder = fSolids; bd.moveToEnd(); bd.enabled = false;
var sm = tc.layers.addSolid([0, 0, 0], "TITLE faint smoke", W, H, 1, tc.duration); sm.source.parentFolder = fSolids; sm.blendingMode = BlendingMode.SCREEN;
var fn = fx(sm, "ADBE Fractal Noise"); fn.property("ADBE Fractal Noise-0004").setValue(140); fn.property("ADBE Fractal Noise-0005").setValue(-55);
fn.property("ADBE Fractal Noise-0010").setValue(500); fn.property("ADBE Fractal Noise-0023").expression = "time*40";
tr(sm, "ADBE Opacity").setValue(18); sm.moveBefore(bd); sm.enabled = false;
keys(tr(LT, "ADBE Opacity"), [[DUR - 0.6, 100], [DUR, 0]], 40);
// smoke deepens to dark warm brown behind the title so the gold reads (reference look)
var dk = edit.layers.addSolid([0.16, 0.08, 0.03], "SMOKE darken behind title", W, H, 1, DUR); dk.source.parentFolder = fSolids; dk.blendingMode = BlendingMode.MULTIPLY;
dk.inPoint = TT0 - 1.0; dk.outPoint = DUR; keys(tr(dk, "ADBE Opacity"), [[TT0 - 1.0, 0], [TT0 + 1.2, 85]], 50); dk.moveAfter(LT);
var eb = edit.layers.addSolid([0, 0, 0], "FADE OUT end", W, H, 1, DUR); eb.source.parentFolder = fSolids; eb.inPoint = DUR - 0.8; eb.outPoint = DUR;
keys(tr(eb, "ADBE Opacity"), [[DUR - 0.8, 0], [DUR, 100]], 40); eb.moveToBeginning();
log("title + fg done");

// ---------- 02_GRADED
var gr = proj.items.addComp("02_GRADED", W, H, 1, DUR, FPS); gr.parentFolder = fComps;
gr.layers.add(edit);
function adj(c, name) { var a = c.layers.addSolid([1, 1, 1], name, W, H, 1, DUR); a.adjustmentLayer = true; a.source.parentFolder = fSolids; return a; }
var a1 = adj(gr, "GRADE 1  Brass mids / teal shadows (Tritone)");
var tri = fx(a1, "ADBE Tritone");
tri.property("ADBE Tritone-0001").setValue([1, 0.94, 0.84, 1]); tri.property("ADBE Tritone-0002").setValue([0.6, 0.5, 0.36, 1]);
tri.property("ADBE Tritone-0003").setValue([0.02, 0.055, 0.07, 1]); tri.property("ADBE Tritone-0004").setValue(72);
var a2 = adj(gr, "GRADE 2  Desaturate (Hue/Sat)"); fx(a2, "ADBE HUE SATURATION").property("ADBE HUE SATURATION-0005").setValue(-14);
var a3 = adj(gr, "GRADE 3  Contrast (Levels)"); var lv = fx(a3, "ADBE Easy Levels2");
lv.property("ADBE Easy Levels2-0003").setValue(0.025); lv.property("ADBE Easy Levels2-0005").setValue(0.96);
var a4 = adj(gr, "HALATION  red glow on highlights"); var hg = fx(a4, "ADBE Glo2");
hg.property("ADBE Glo2-0002").setValue(185); hg.property("ADBE Glo2-0003").setValue(45); hg.property("ADBE Glo2-0004").setValue(0.55);
hg.property("ADBE Glo2-0007").setValue(2); hg.property("ADBE Glo2-0012").setValue([1, 0.5, 0.3, 1]); hg.property("ADBE Glo2-0013").setValue([0.8, 0.15, 0.05, 1]);
log("grade done");

// ---------- 03_FINAL: radial chromatic aberration (R scaled out, B scaled in), grain, vignette, letterbox
var fin = proj.items.addComp("03_FINAL  (render this)", W, H, 1, DUR, FPS); fin.parentFolder = fComps; fin.bgColor = [0, 0, 0];
var chan = [["CA  red channel", 2, 100.35], ["CA  green channel", 3, 100.0], ["CA  blue channel", 4, 99.65]];
for (var c = 0; c < 3; c++) {
    var L = fin.layers.add(gr); L.name = chan[c][0];
    var sh = fx(L, "ADBE Shift Channels");
    for (var q = 2; q <= 4; q++) if (q != chan[c][1]) sh.property("ADBE Shift Channels-000" + q).setValue(10);   // 10 = Full Off
    tr(L, "ADBE Scale").setValue([chan[c][2], chan[c][2]]);
    // almost no colour split during the blast (white shards were fringing red/cyan), full again for the title
    tr(L, "ADBE Scale").expression = "var k=Math.max(ease(time," + (B + 24.4) + "," + (B + 24.7) + ",1,0.15),ease(time," + (B + 27.6) + "," + (B + 28.4) + ",0.15,1));var s=100+(value[0]-100)*k;[s,s]";
    if (c > 0) L.blendingMode = BlendingMode.ADD;
}
var gn = adj(fin, "GRAIN  (Noise 5%, mono)"); var nz = fx(gn, "ADBE Noise"); nz.property("ADBE Noise-0001").setValue(5); nz.property("ADBE Noise-0002").setValue(0);
var vg = fin.layers.addSolid([0, 0, 0], "VIGNETTE", W, H, 1, DUR); vg.source.parentFolder = fSolids;
var vm = vg.property("ADBE Mask Parade").addProperty("ADBE Mask Atom"); vm.inverted = true; var vs = new Shape();
var kx = 0.5523;
vs.vertices = [[960, 70], [1860, 540], [960, 1010], [60, 540]];
vs.inTangents = [[-900 * kx, 0], [0, -470 * kx], [900 * kx, 0], [0, 470 * kx]];
vs.outTangents = [[900 * kx, 0], [0, 470 * kx], [-900 * kx, 0], [0, -470 * kx]]; vs.closed = true;
vm.property("ADBE Mask Shape").setValue(vs); vm.property("ADBE Mask Feather").setValue([420, 420]); tr(vg, "ADBE Opacity").setValue(55);
var lt = fin.layers.addSolid([0, 0, 0], "LETTERBOX top", W, 138, 1, DUR); tr(lt, "ADBE Position").setValue([W / 2, 69]); lt.source.parentFolder = fSolids;
var lbm = fin.layers.addSolid([0, 0, 0], "LETTERBOX bottom", W, 138, 1, DUR); tr(lbm, "ADBE Position").setValue([W / 2, H - 69]); lbm.source.parentFolder = fSolids;

proj.save(new File(PROJ + "DhanterasCoin_v6.aep")); log("saved project");
var rq = proj.renderQueue.items.add(fin); var om = rq.outputModule(1);
try { om.applyTemplate("High Quality"); } catch (e1) { log("template " + e1); }
om.file = new File("D:/aetmp/fsintro/out/v6_master");
proj.save(); log("render start"); proj.renderQueue.render(); log("render done");
app.endSuppressDialogs(false);
} catch (err) { log("ERROR line " + err.line + ": " + err.toString()); try { app.endSuppressDialogs(false); } catch (e2) {} }
LOG.close();
var d = new File("D:/aetmp/fsintro/out/V6_DONE.txt"); d.open("w"); d.write("done"); d.close();
})();
